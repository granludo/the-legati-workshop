#!/usr/bin/env python3
"""Lane claims: a legatus says "I am working on this project" in the project's own BACKLOG.md,
so every other session (any machine, any harness) sees it on its next pull.

  lane.py claim  <project-dir> "<task>" [--force] [--no-push]   insert a lane callout at the top of <dir>/BACKLOG.md, commit, push
  lane.py release <project-dir> [--no-push]                      remove my callout(s) there, commit, push
  lane.py list                                                    every active lane callout in the repo

The callout (Obsidian-renderable, greppable):
  > [!lane] LANE — orchestrator@my-laptop/claude-code — rebuild the bibliography checker — since 2026-09-06 10:12
A claim younger than --ttl hours (default 24) by another legatus blocks a new claim unless --force.
Python 3.9, no deps. Identity as in handoff.py.
"""
import argparse, datetime, os, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SYNC = REPO / "tools" / "git" / "sync.sh"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from handoff import legatus, harness, host  # noqa: E402

PAT = re.compile(r"^> \[!lane\] LANE — (?P<who>\S+)@(?P<where>\S+) — (?P<task>.*) — since (?P<since>\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*$")

def backlog(project):
    d = (REPO / project).resolve()
    if d.is_file(): d = d.parent
    b = d / "BACKLOG.md"
    return b

def claims_in(path):
    out = []
    try:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            m = PAT.match(line)
            if m: out.append((n, m.groupdict()))
    except Exception:
        pass
    return out

def age_hours(since):
    try:
        t = datetime.datetime.strptime(since, "%Y-%m-%d %H:%M")
        return (datetime.datetime.now() - t).total_seconds() / 3600
    except Exception:
        return 1e9

def cmd_claim(a):
    b = backlog(a.project)
    if not b.exists():
        print(f"[lane] no BACKLOG.md at {b.relative_to(REPO)} — create one first (every project has a backlog)"); return 4
    me = legatus(); where = f"{host()}/{harness()}"
    for _, c in claims_in(b):
        if c["who"] != me and age_hours(c["since"]) < a.ttl and not a.force:
            print(f"[lane] HELD by {c['who']}@{c['where']} since {c['since']}: {c['task']}\n       stand down, or coordinate via handoff, or --force if you know it is stale."); return 1
    lines = b.read_text(encoding="utf-8").splitlines()
    call = f"> [!lane] LANE — {me}@{where} — {a.task} — since {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    # insert after the H1 (and any blank line right after it), else at top
    idx = 0
    for i, l in enumerate(lines[:5]):
        if l.startswith("# "): idx = i + 1; break
    lines[idx:idx] = ["", call, ""]
    b.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rel = str(b.relative_to(REPO)); print(f"[lane] claimed {a.project}: {call}")
    if a.no_push: return 0
    return subprocess.run(["bash", str(SYNC), "commit", "-m", f"Lane: {me} claims {a.project}: {a.task}", "--", rel], cwd=REPO).returncode

def cmd_release(a):
    b = backlog(a.project); me = legatus()
    if not b.exists(): print("[lane] no BACKLOG.md there"); return 4
    lines = b.read_text(encoding="utf-8").splitlines(); keep = []; removed = 0
    for l in lines:
        m = PAT.match(l)
        if m and (m.group("who") == me or a.force): removed += 1; continue
        keep.append(l)
    if not removed: print(f"[lane] no lane held by {me} in {b.relative_to(REPO)}"); return 0
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(keep)) + "\n"
    b.write_text(text, encoding="utf-8"); rel = str(b.relative_to(REPO))
    print(f"[lane] released {a.project} ({removed} callout(s))")
    if a.no_push: return 0
    return subprocess.run(["bash", str(SYNC), "commit", "-m", f"Lane: {me} releases {a.project}", "--", rel], cwd=REPO).returncode

def cmd_list(a):
    found = 0
    for b in sorted(REPO.rglob("BACKLOG.md")):
        if "/archive/" in str(b) or "/node_modules/" in str(b): continue
        for _, c in claims_in(b):
            found += 1; stale = " (stale)" if age_hours(c["since"]) > a.ttl else ""
            print(f"  {c['who']:8}@{c['where']:22} {b.parent.relative_to(REPO)}  — {c['task']}  since {c['since']}{stale}")
    if not found: print("[lane] no active lanes")
    return 0

def main():
    ap = argparse.ArgumentParser(prog="lane.py"); ap.add_argument("--ttl", type=float, default=24.0, help="hours before a foreign claim counts as stale")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("claim"); c.add_argument("project"); c.add_argument("task"); c.add_argument("--force", action="store_true"); c.add_argument("--no-push", action="store_true")
    r = sub.add_parser("release"); r.add_argument("project"); r.add_argument("--force", action="store_true"); r.add_argument("--no-push", action="store_true")
    sub.add_parser("list")
    a = ap.parse_args()
    return {"claim": cmd_claim, "release": cmd_release, "list": cmd_list}.get(a.cmd, lambda _: (ap.print_help(), 4)[1])(a)

if __name__ == "__main__":
    sys.exit(main())
