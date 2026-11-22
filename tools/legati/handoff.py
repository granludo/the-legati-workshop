#!/usr/bin/env python3
"""Legati handoffs: one file per message under legati/handoffs/, carried by git between machines and harnesses.

  handoff.py send --to writer --subject "…" [--body "…" | --body-file f | stdin] [--re FILE] [--no-push]
  handoff.py inbox [--for NAME] [--all] [--quiet]     unread messages addressed to me (or to all)
  handoff.py show FILE                                print one message
  handoff.py ack FILE|--all                            archive messages addressed to me; bump marker for broadcasts
  handoff.py whoami

Why one file per message: two senders never touch the same line, so pulls never conflict on the bus.
Identity: Observatory per-session marker, else LEGATUS_AGENT env, else 'unknown'.
Read markers live per legatus+harness in <repo>/.legati-state/ (never committed). Python 3.9, no deps.
"""
import argparse, datetime, os, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BOX = REPO / "legati" / "handoffs"
ARCHIVE = BOX / "archive"
SYNC = REPO / "tools" / "git" / "sync.sh"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from state import marker_path as state_marker, atomic_write

def sh(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)

def harness():
    e = os.environ
    if e.get("LEGATUS_HARNESS"): return e["LEGATUS_HARNESS"]
    if e.get("CLAUDE_CODE_SESSION_ID") or e.get("CLAUDE_SESSION_ID") or e.get("CLAUDECODE"): return "claude-code"
    if any(k.startswith("CODEX_") for k in e): return "codex"
    return "unknown"

def legatus():
    # A marker under ANY id this session is known by wins (launcher id, then harness ids), so the
    # name survives when the launcher env is gone but the Codex thread id / Claude session id remains.
    for k in ("LEGATUS_SESSION", "CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID", "CODEX_THREAD_ID"):
        sid = os.environ.get(k)
        if not sid: continue
        p = REPO / ".observatory" / "sessions" / f"{sid.replace('/', '_')}.agent"
        if p.exists():
            name = p.read_text().strip()
            if name: return name
    return os.environ.get("LEGATUS_AGENT") or "unknown"

def host():
    return subprocess.run(["hostname", "-s"], capture_output=True, text=True).stdout.strip()

def now():
    return datetime.datetime.now().astimezone()

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "msg"

def parse(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            for line in parts[0].splitlines()[1:]:
                if ":" in line:
                    k, v = line.split(":", 1); meta[k.strip()] = v.strip()
            body = parts[1].lstrip("\n")
    return meta, body

def marker_path(me):
    return state_marker(REPO, f"inbox.{me}.{harness()}.last")

def marker(me):
    p = marker_path(me)
    return p.read_text().strip() if p.exists() else ""

def messages():
    return sorted(p for p in BOX.glob("*.md") if p.name != "README.md")

def cmd_send(a):
    me = a.frm or legatus()
    body = a.body if a.body is not None else (Path(a.body_file).read_text() if a.body_file else (sys.stdin.read() if not sys.stdin.isatty() else ""))
    ts = now()
    name = f"{ts.strftime('%Y-%m-%dT%H-%M-%S')}_{me}_to_{a.to}_{slug(a.subject)}.md"
    BOX.mkdir(parents=True, exist_ok=True)
    path = BOX / name
    lines = ["---", f"from: {me}", f"to: {a.to}", f"ts: {ts.isoformat(timespec='seconds')}", f"host: {host()}", f"harness: {harness()}", f"subject: {a.subject}"]
    if a.re: lines.append(f"re: {a.re}")
    head = sh(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    if head: lines.append(f"at-commit: {head}")
    lines += ["---", "", body.rstrip() + "\n"]
    path.write_text("\n".join(lines), encoding="utf-8")
    rel = path.relative_to(REPO)
    print(f"[handoff] wrote {rel}")
    if a.no_push:
        print("[handoff] not committed (--no-push). Deliver with: bash tools/git/sync.sh commit -m 'Handoff …' -- " + str(rel))
        return 0
    r = subprocess.run(["bash", str(SYNC), "commit", "-m", f"Handoff: {me} → {a.to}: {a.subject}", "--", str(rel)], cwd=REPO)
    return r.returncode

def unread(me, include_all=True):
    mk = marker(me)
    out = []
    for p in messages():
        meta, _ = parse(p)
        to = meta.get("to", "")
        if to == me or (include_all and to == "all") or me == "*":
            if to == "all" and mk and p.name <= mk:      # broadcasts: marker by filename (time-sorted)
                continue
            out.append((p, meta))
    return out

def cmd_inbox(a):
    me = a.for_ or ("*" if a.all else legatus())
    items = unread(me)
    if not items:
        if not a.quiet: print(f"[handoff] inbox empty for {me}")
        return 0
    print(f"[handoff] {len(items)} unread for {me}:")
    for p, m in items:
        print(f"  {m.get('ts','?')[:16]}  {m.get('from','?'):8} → {m.get('to','?'):8}  {m.get('subject','')}   ({p.name})")
    print("  read with: python3 tools/legati/handoff.py show <file>   · done with: … ack <file>")
    return 0

def cmd_show(a):
    p = BOX / a.file if not os.path.isabs(a.file) else Path(a.file)
    if not p.exists(): p = REPO / a.file
    if not p.exists(): print(f"no such message: {a.file}"); return 1
    print(p.read_text(encoding="utf-8")); return 0

def cmd_ack(a):
    me = legatus()
    targets = unread(me) if a.all else [(BOX / a.file, parse(BOX / a.file)[0])]
    moved = []
    for p, m in targets:
        if not p.exists(): continue
        if m.get("to") == "all":
            atomic_write(marker_path(me), p.name); continue         # broadcasts are not archived by readers
        dest = ARCHIVE / now().strftime("%Y-%m"); dest.mkdir(parents=True, exist_ok=True)
        sh(["git", "mv", str(p.relative_to(REPO)), str((dest / p.name).relative_to(REPO))])
        moved.append(str((dest / p.name).relative_to(REPO))); moved.append(str(p.relative_to(REPO)))
    if not moved:
        print("[handoff] nothing to archive (marker bumped for broadcasts)"); return 0
    subj = "all" if a.all else a.file
    r = subprocess.run(["bash", str(SYNC), "commit", "-m", f"Handoff ack: {me} archived {subj}", "--"] + moved, cwd=REPO)
    return r.returncode

def main():
    ap = argparse.ArgumentParser(prog="handoff.py")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("send"); s.add_argument("--to", required=True); s.add_argument("--subject", required=True)
    s.add_argument("--body"); s.add_argument("--body-file"); s.add_argument("--re"); s.add_argument("--from", dest="frm"); s.add_argument("--no-push", action="store_true")
    i = sub.add_parser("inbox"); i.add_argument("--for", dest="for_"); i.add_argument("--all", action="store_true"); i.add_argument("--quiet", action="store_true")
    w = sub.add_parser("show"); w.add_argument("file")
    k = sub.add_parser("ack"); k.add_argument("file", nargs="?"); k.add_argument("--all", action="store_true")
    sub.add_parser("whoami")
    a = ap.parse_args()
    if a.cmd == "send": return cmd_send(a)
    if a.cmd == "inbox": return cmd_inbox(a)
    if a.cmd == "show": return cmd_show(a)
    if a.cmd == "ack":
        if not a.file and not a.all: ap.error("ack needs FILE or --all")
        return cmd_ack(a)
    if a.cmd == "whoami": print(f"legatus={legatus()} harness={harness()} host={host()}"); return 0
    ap.print_help(); return 4

if __name__ == "__main__":
    sys.exit(main())
