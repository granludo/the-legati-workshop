"""Offline read-marker, fetch-diagnostics and startup checks, without Git writes or model calls.

Run: python3 -B tools/legati/test_state.py
"""
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from state import marker_path, atomic_write

ROOT = Path(__file__).resolve().parents[2]


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / "workshop"
        self.repo.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.env = {**os.environ, "HOME": str(self.home), "LEGATUS_REPO": str(self.repo),
                    "LEGATUS_HARNESS": "codex", "LEGATUS_SESSION": "",
                    "CODEX_THREAD_ID": "", "CLAUDE_CODE_SESSION_ID": "",
                    "CLAUDE_SESSION_ID": ""}

    def fake_git(self, body):
        bindir = self.base / "bin"
        bindir.mkdir(exist_ok=True)
        git = bindir / "git"
        git.write_text("#!/bin/bash\n" + body)
        git.chmod(0o755)
        self.env["PATH"] = str(bindir) + os.pathsep + os.environ["PATH"]

    def sync(self, command, **env):
        return subprocess.run(["bash", str(ROOT / "tools/git/sync.sh"), command],
                              env={**self.env, **env}, capture_output=True, text=True)

    def test_git_markers_are_per_agent(self):
        self.fake_git('case "$1" in rev-parse) echo "$TEST_HEAD";; esac\n')
        for agent, head in (("writer", "aaa"), ("orchestrator", "bbb")):
            result = self.sync("log", LEGATUS_AGENT=agent, TEST_HEAD=head)
            self.assertEqual(result.returncode, 0, result.stderr)
        directory = self.repo / ".legati-state"
        self.assertEqual((directory / "codex.writer.last-seen").read_text().strip(), "aaa")
        self.assertEqual((directory / "codex.orchestrator.last-seen").read_text().strip(), "bbb")

    def test_fetch_classification_and_exit_status(self):
        self.fake_git('echo "$TEST_ERROR" >&2\nexit "$TEST_STATUS"\n')
        for error, expected in (("cannot open FETCH_HEAD: Operation not permitted", "permission"),
                                ("Permission denied (publickey)", "authentication"),
                                ("Authentication failed", "authentication"),
                                ("Could not resolve host", "connectivity"),
                                ("unexpected server response", "fetch")):
            result = self.sync("fetch", TEST_ERROR=error, TEST_STATUS="128")
            self.assertEqual(result.returncode, 128)
            self.assertIn(expected + " failure", result.stderr)
            self.assertIn(error, result.stderr)
        self.assertEqual(self.sync("fetch", TEST_ERROR="", TEST_STATUS="0").returncode, 0)

    def test_startup_defers_sandbox_writes_and_refresh_preserves_dirty_work(self):
        scripts = self.repo / "tools/legati"
        scripts.mkdir(parents=True)
        startup = scripts / "session-start.sh"
        shutil.copyfile(ROOT / "tools/legati/session-start.sh", startup)
        sync = self.repo / "tools/git/sync.sh"
        sync.parent.mkdir()
        sync.write_text('echo "$1" >> "$TEST_CALLS"\n'
                        'case "$1" in whoami) echo "legatus=orchestrator";; esac\n')
        self.fake_git('case "$1" in symbolic-ref) echo main;; '
                      'remote) echo https://example.org/workshop.git;; '
                      'rev-list) echo "0 1";; '
                      'status) [ "$TEST_DIRTY" = 1 ] && echo " M draft.md";; esac\nexit 0\n')
        calls = self.base / "calls"

        def run(args, sandbox, dirty="0"):
            calls.write_text("")
            result = subprocess.run(["bash", str(startup), *args],
                                    env={**self.env, "CODEX_SANDBOX": sandbox,
                                         "TEST_CALLS": str(calls), "TEST_DIRTY": dirty},
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout, calls.read_text().splitlines()

        for args, sandbox in (([], "seatbelt"), (["--local"], "")):
            out, invoked = run(args, sandbox)
            self.assertNotIn("fetch", invoked)
            self.assertNotIn("pull", invoked)
            self.assertIn("log", invoked)
            self.assertIn("Git refresh deferred", out)

        for args, sandbox in ((["--refresh"], "seatbelt"), ([], "")):
            _, invoked = run(args, sandbox)
            self.assertIn("fetch", invoked)
            self.assertIn("pull", invoked)
            out, invoked = run(args, sandbox, dirty="1")
            self.assertIn("fetch", invoked)
            self.assertNotIn("pull", invoked)
            self.assertIn("uncommitted", out)

    def test_startup_never_rebases_local_commits_or_pulls_the_scaffold(self):
        scripts = self.repo / "tools/legati"
        scripts.mkdir(parents=True)
        startup = scripts / "session-start.sh"
        shutil.copyfile(ROOT / "tools/legati/session-start.sh", startup)
        sync = self.repo / "tools/git/sync.sh"
        sync.parent.mkdir()
        sync.write_text('echo "$1" >> "$TEST_CALLS"\n')
        calls = self.base / "calls"
        for origin, ahead, fetch_expected in (("https://example.org/w.git", "2", True),
                                              ("https://github.com/granludo/the-legati-workshop.git", "0", False)):
            self.fake_git('case "$1" in symbolic-ref) echo main;; '
                          f'remote) echo {origin};; '
                          f'rev-list) echo "{ahead} 3";; esac\nexit 0\n')
            calls.write_text("")
            result = subprocess.run(["bash", str(startup)], env={**self.env, "CODEX_SANDBOX": "", "TEST_CALLS": str(calls)},
                                    capture_output=True, text=True)
            invoked = calls.read_text().splitlines()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("pull", invoked)
            self.assertEqual("fetch" in invoked, fetch_expected)


if __name__ == "__main__":
    unittest.main()
