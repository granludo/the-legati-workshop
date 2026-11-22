#!/usr/bin/env python3
"""Offline identity regression checks. No harnesses, models, Git writes or network.

Run: python3 tools/legati/test_identity.py
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, REPO / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


obs = module("obs_identity_test", "engineering-projects/legati-observatory/obs.py")
handoff = module("handoff_identity_test", "tools/legati/handoff.py")
# Exercise the actual shell resolver without running sync's Git/marker operations.
sync_source = (REPO / "tools/git/sync.sh").read_text()
shell_resolver = sync_source.split("legatus() {", 1)[1].split("\nhost()", 1)[0]
shell_resolver = "legatus() {" + shell_resolver + "\nlegatus\n"


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.sessions = self.root / ".observatory" / "sessions"
        self.sessions.mkdir(parents=True)
        for sid, name in (("codex-a", "writer"), ("codex-d", "reviewer"),
                          ("claude-a", "writer"), ("claude-d", "reviewer"),
                          ("explicit", "comms"), ("slash_id", "reviewer"), ("empty", "")):
            (self.sessions / (sid + ".agent")).write_text(name)
        for target, key, value in ((obs, "SESSIONS", self.sessions), (handoff, "REPO", self.root)):
            replacement = patch.object(target, key, value)
            replacement.start()
            self.addCleanup(replacement.stop)

    def check_identity(self, env, expected, sid=None):
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(obs.agent(), expected)
            self.assertEqual(handoff.legatus(), expected)
            if sid:
                self.assertEqual(obs.session_id(), sid)
        result = subprocess.run(["/bin/bash", "-c", shell_resolver],
                                cwd=self.root, env={"PATH": os.defpath, **env},
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), expected)

    def test_independent_codex_terminals(self):
        for sid, name in (("codex-a", "writer"), ("codex-d", "reviewer"), ("codex-a", "writer")):
            self.check_identity({"CODEX_THREAD_ID": sid}, name, sid)

    def test_independent_claude_terminals(self):
        for key in ("CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID"):
            for sid, name in (("claude-a", "writer"), ("claude-d", "reviewer")):
                self.check_identity({key: sid}, name, sid)

    def test_launcher_override(self):
        self.check_identity({"LEGATUS_SESSION": "explicit", "CODEX_THREAD_ID": "codex-d"},
                            "comms", "explicit")

    def test_active_persona_overrides_launcher_default(self):
        self.check_identity({"CODEX_THREAD_ID": "codex-d", "LEGATUS_AGENT": "orchestrator"}, "reviewer")

    def test_unregistered_session_does_not_inherit_other_terminal(self):
        self.check_identity({"CODEX_THREAD_ID": "new-terminal"}, "unknown")
        self.check_identity({"CODEX_THREAD_ID": "new-terminal", "LEGATUS_AGENT": "historian"}, "historian")

    def test_empty_marker_falls_back_to_default(self):
        self.check_identity({"CODEX_THREAD_ID": "empty", "LEGATUS_AGENT": "historian"}, "historian")

    def test_marker_path_normalization(self):
        self.check_identity({"LEGATUS_SESSION": "slash/id"}, "reviewer", "slash/id")

    def test_marker_under_harness_id_survives_lost_launcher_env(self):
        # Launcher id set but unregistered; the harness id carries the marker (e.g. a session moved to a desktop app).
        self.check_identity({"LEGATUS_SESSION": "no-marker", "CODEX_THREAD_ID": "codex-d"}, "reviewer", "no-marker")
        self.check_identity({"LEGATUS_SESSION": "no-marker", "CLAUDE_CODE_SESSION_ID": "claude-a"}, "writer")

    def test_set_agent_writes_every_known_id(self):
        with patch.dict(os.environ, {"LEGATUS_SESSION": "launch-x", "CODEX_THREAD_ID": "thread-x"}, clear=True):
            obs.set_agent("comms")
        for sid in ("launch-x", "thread-x"):
            self.assertEqual((self.sessions / (sid + ".agent")).read_text(), "comms")
        # launcher env gone, only the thread id remains: still comms in all three resolvers
        self.check_identity({"CODEX_THREAD_ID": "thread-x"}, "comms", "thread-x")

    def test_remember_agent_pins_resolved_name_without_clobbering(self):
        obs.remember_agent("hook-sid", "historian")
        self.assertEqual((self.sessions / "hook-sid.agent").read_text(), "historian")
        obs.remember_agent("hook-sid", "reviewer")           # existing non-empty marker wins
        self.assertEqual((self.sessions / "hook-sid.agent").read_text(), "historian")
        obs.remember_agent("empty", "historian")               # empty marker gets filled
        self.assertEqual((self.sessions / "empty.agent").read_text(), "historian")
        obs.remember_agent("never", "unknown")           # unknown is never pinned
        self.assertFalse((self.sessions / "never.agent").exists())


if __name__ == "__main__":
    unittest.main()
