#!/usr/bin/env python3
"""obs — Legati Observatory CLI.

Portable, static, stigmergic observability + advisory locks for the workshop's
parallel AI sessions (the legati). No server, no database, no cloud — just an
append-only event log plus two tiny state dirs, all under <repo>/.observatory/
(gitignored; machine-dependent). See DESIGN.md.

The core (this file) knows NOTHING about any specific harness. Harness-specific
capture lives in adapters/<harness>/ and only ever calls `obs emit`.

Identity resolution (env, best-effort):
  LEGATUS_AGENT    -> agent name (your legatus/persona name); default "unknown"
  LEGATUS_SESSION  -> stable session id; falls back to CLAUDE_SESSION_ID, then host-ppid
  OBS_STALE_MINUTES-> presence staleness threshold (default 10)
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


def repo_root() -> Path:
    p = Path(__file__).resolve()
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return d
    return Path.cwd()


ROOT = repo_root()
OBS = ROOT / ".observatory"
EVENTS = OBS / "events"
SESSIONS = OBS / "sessions"
LOCKS = OBS / "locks"
# Rendered dashboards live in a VISIBLE dir (not a dot-dir) so Obsidian can show
# them; still gitignored (machine-dependent). history/ keeps timestamped snapshots.
RENDER = Path(__file__).resolve().parent / "render"
HISTORY = RENDER / "history"
STALE_MIN = int(os.environ.get("OBS_STALE_MINUTES", "10"))


def now() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def iso(dt: datetime | None = None) -> str:
    return (dt or now()).isoformat(timespec="seconds")


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def host() -> str:
    return socket.gethostname().split(".")[0]


def session_id() -> str:
    return (
        os.environ.get("LEGATUS_SESSION")
        or os.environ.get("CLAUDE_CODE_SESSION_ID")  # Claude Code exposes this to Bash + hooks
        or os.environ.get("CLAUDE_SESSION_ID")
        or f"{host()}-{os.getppid()}"
    )


def agent_marker_path(sid: str | None = None) -> Path:
    safe = (sid or session_id()).replace("/", "_")
    return SESSIONS / f"{safe}.agent"


def agent() -> str:
    # Per-session marker (set by `obs agent <name>` on persona switch) wins over
    # the env default, so attribution follows the active legatus within a session.
    mp = agent_marker_path()
    try:
        if mp.exists():
            v = mp.read_text().strip()
            if v:
                return v
    except Exception:
        pass
    return os.environ.get("LEGATUS_AGENT", "unknown")


def ensure_dirs() -> None:
    for d in (EVENTS, SESSIONS, LOCKS, RENDER, HISTORY):
        d.mkdir(parents=True, exist_ok=True)
    gi = OBS / ".gitignore"
    if not gi.exists():
        gi.write_text(
            "# Legati Observatory runtime state — machine-dependent, never committed.\n"
            "# Per-host dashboards live in render/ and are also ignored; force-add one\n"
            "# deliberately if you want a teaching snapshot in git.\n"
            "*\n!.gitignore\n"
        )


def project_of(cwd: str) -> str:
    try:
        rel = Path(cwd).resolve().relative_to(ROOT)
        return rel.parts[-1] if rel.parts else ROOT.name
    except Exception:
        return ROOT.name


# ---------------------------------------------------------------- presence
def presence_path(sid: str) -> Path:
    safe = sid.replace("/", "_")
    return SESSIONS / f"{safe}.json"


def touch_presence(cwd: str | None = None, current_task: str | None = None) -> None:
    sid = session_id()
    p = presence_path(sid)
    data = {}
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except Exception:
            data = {}
    data.setdefault("session_id", sid)
    data.setdefault("started", iso())
    data["agent"] = agent()
    data["host"] = host()
    if cwd:
        data["cwd"] = cwd
        data["project"] = project_of(cwd)
    if current_task is not None:
        data["current_task"] = current_task
    data["last_seen"] = iso()
    p.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------- events
def append_event(ev: dict) -> None:
    day = now().strftime("%Y-%m-%d")
    with (EVENTS / f"{day}.jsonl").open("a") as f:
        f.write(json.dumps(ev) + "\n")


def cmd_emit(a) -> int:
    ensure_dirs()
    cwd = a.cwd or os.getcwd()
    ev = {
        "ts": iso(),
        "session_id": session_id(),
        "agent": agent(),
        "host": host(),
        "cwd": cwd,
        "project": project_of(cwd),
        "type": a.type,
    }
    for k in ("tool", "target", "model", "parent"):
        v = getattr(a, k)
        if v:
            ev[k if k != "parent" else "parent_session_id"] = v
    if a.tokens_in:
        ev["tokens_in"] = a.tokens_in
    if a.tokens_out:
        ev["tokens_out"] = a.tokens_out
    if a.cost:
        ev["cost_usd"] = a.cost
    append_event(ev)
    touch_presence(cwd=cwd)
    return 0


def cmd_agent(a) -> int:
    ensure_dirs()
    agent_marker_path().write_text(a.name.strip())
    touch_presence(cwd=os.getcwd())
    print(f"session {session_id()} → agent {a.name.strip()}")
    return 0


def cmd_task(a) -> int:
    ensure_dirs()
    touch_presence(cwd=os.getcwd(), current_task=a.text)
    append_event({"ts": iso(), "session_id": session_id(), "agent": agent(),
                  "host": host(), "cwd": os.getcwd(), "project": project_of(os.getcwd()),
                  "type": "task", "target": a.text})
    return 0


def cmd_heartbeat(a) -> int:
    ensure_dirs()
    touch_presence(cwd=os.getcwd())
    return 0


def load_sessions() -> list[dict]:
    out = []
    for p in sorted(SESSIONS.glob("*.json")):
        try:
            out.append(json.loads(p.read_text()))
        except Exception:
            continue
    return out


def age_min(ts: str) -> float:
    return (now() - parse_iso(ts)).total_seconds() / 60.0


def cmd_who(a) -> int:
    ensure_dirs()
    rows = load_sessions()
    live = [s for s in rows if age_min(s.get("last_seen", iso())) <= STALE_MIN]
    if not live:
        print("No live legati sessions.")
        return 0
    for s in sorted(live, key=lambda r: r.get("last_seen", "")):
        am = age_min(s.get("last_seen", iso()))
        print(f"● {s.get('agent','?'):8} {s.get('host','?'):18} "
              f"{s.get('project','?'):22} {s.get('current_task','—')}  "
              f"(seen {am:.0f}m ago)")
    return 0


# ---------------------------------------------------------------- locks
def lock_path(slug: str) -> Path:
    return LOCKS / f"{slug}.lock"


def read_lock(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def lock_expired(data: dict) -> bool:
    try:
        return age_min(data["ts"]) > float(data.get("ttl_minutes", 15))
    except Exception:
        return True


def cmd_lock(a) -> int:
    ensure_dirs()
    p = lock_path(a.slug)
    if a.action == "check":
        d = read_lock(p)
        if d and not lock_expired(d):
            print(f"LOCKED by {d['agent']} ({d['owner_session']}): {d.get('task','')} "
                  f"(ttl {d.get('ttl_minutes')}m, {age_min(d['ts']):.0f}m old)")
            return 1
        print("free")
        return 0

    if a.action == "release":
        d = read_lock(p)
        if not d:
            print("not locked")
            return 0
        if d.get("owner_session") != session_id() and not a.force:
            print(f"refusing: lock owned by {d['agent']} ({d['owner_session']}); use --force")
            return 1
        p.unlink(missing_ok=True)
        print("released")
        return 0

    # acquire — atomic exclusive create IS the mutex
    payload = json.dumps({
        "slug": a.slug, "owner_session": session_id(), "agent": agent(),
        "host": host(), "ts": iso(), "ttl_minutes": a.ttl, "task": a.task or "",
    }, indent=2)
    for attempt in (1, 2):
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            with os.fdopen(fd, "w") as f:
                f.write(payload)
            print(f"acquired {a.slug} (ttl {a.ttl}m)")
            return 0
        except FileExistsError:
            d = read_lock(p)
            if d and lock_expired(d) and attempt == 1:
                p.unlink(missing_ok=True)  # steal expired lock, retry once
                continue
            who = f"{d['agent']} ({d['owner_session']})" if d else "unknown"
            print(f"DENIED: {a.slug} held by {who}: {d.get('task','') if d else ''}")
            return 1
    return 1


# ---------------------------------------------------------------- render
def _node_id(sid: str) -> str:
    return "s_" + "".join(c if c.isalnum() else "_" for c in sid)[:24]


def orchestration_graph_text(sessions: list[dict], events: list[dict]) -> str | None:
    """The Mermaid flowchart body (no code fences) for sessions + parent→child links,
    or None if there's nothing to graph. Shared by the markdown and HTML renderers."""
    info: dict = {}
    for s in sessions:
        sid = s.get("session_id")
        if not sid:
            continue
        info.setdefault(sid, {})
        info[sid]["agent"] = s.get("agent", "?")
        info[sid]["task"] = s.get("current_task", "")
        info[sid]["live"] = age_min(s.get("last_seen", iso())) <= STALE_MIN
    edges = set()
    for e in events:
        sid = e.get("session_id")
        if sid and sid not in info:
            info[sid] = {"agent": e.get("agent", "?"), "task": "", "live": False}
        p = e.get("parent_session_id")
        if p and sid:
            edges.add((p, sid))
            info.setdefault(p, {"agent": "?", "task": "", "live": False})
    if not info:
        return None
    out = ["flowchart TD"]
    for sid, m in info.items():
        label = f"{m.get('agent', '?')} · {sid[:8]}"
        task = (m.get("task") or "").replace('"', "'").replace("[", "(").replace("]", ")")
        if task:
            label += f"<br/>{task[:40]}"
        out.append(f'  {_node_id(sid)}["{label}"]')
    for p, c in sorted(edges):
        out.append(f"  {_node_id(p)} --> {_node_id(c)}")
    out.append("  classDef live fill:#d6f5d6,stroke:#2e7d32;")
    out.append("  classDef stale fill:#eeeeee,stroke:#999999,color:#777777;")
    for sid, m in info.items():
        out.append(f"  class {_node_id(sid)} {'live' if m.get('live') else 'stale'};")
    return "\n".join(out)


def mermaid_orchestration(sessions: list[dict], events: list[dict]) -> list[str]:
    """Markdown-fenced Mermaid block (renders in Obsidian)."""
    body = orchestration_graph_text(sessions, events)
    if body is None:
        return ["_No sessions to graph._"]
    return ["```mermaid", body, "```"]


def parse_window(s: str | None) -> int | None:
    """'today'/'now'→0 · 'NNd'→NN days · 'all'/None→None (everything)."""
    if not s or s == "all":
        return None
    if s in ("today", "now"):
        return 0
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    if s.isdigit():
        return int(s)
    return None


def load_events_window(days: int | None) -> list[dict]:
    """Events across day-files within the window (days=0 → today only, None → all)."""
    out: list[dict] = []
    cutoff = None
    if days is not None:
        cutoff = (now() - timedelta(days=days)).date()
    for f in sorted(EVENTS.glob("*.jsonl")):
        try:
            fday = datetime.strptime(f.stem, "%Y-%m-%d").date()
        except ValueError:
            continue
        if cutoff and fday < cutoff:
            continue
        for line in f.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Legati Observatory — __HOST__</title>
<style>
:root{color-scheme:dark}
body{margin:0;background:#0f1115;color:#d7dae0;font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}
header{padding:14px 18px;border-bottom:1px solid #232733;display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header h1{font-size:16px;margin:0;color:#fff}
header .meta{color:#7d8694;font-size:12px}
#controls{padding:10px 18px;border-bottom:1px solid #232733;display:flex;gap:10px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:#0f1115;z-index:5}
#controls button{background:#1b1f29;color:#cbd1da;border:1px solid #2c313d;border-radius:6px;padding:4px 10px;cursor:pointer}
#controls button.on{background:#2e7d32;color:#fff;border-color:#2e7d32}
#controls select,#controls input{background:#1b1f29;color:#cbd1da;border:1px solid #2c313d;border-radius:6px;padding:4px 8px}
section{padding:14px 18px;border-bottom:1px solid #1c2027}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:#8a93a2;margin:0 0 10px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid #1c2027;vertical-align:top}
th{color:#7d8694;font-weight:600}
tr.clk{cursor:pointer}tr.clk:hover{background:#161a22}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.live{background:#39d353}.stale{background:#555}
.agent{font-weight:700;color:#fff}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:#9fb6d6}
.cards{display:flex;gap:12px;flex-wrap:wrap}
.card{background:#161a22;border:1px solid #232733;border-radius:8px;padding:10px 14px;min-width:90px}
.card .n{font-size:22px;color:#fff}.card .l{font-size:11px;color:#7d8694}
.bar{height:14px;background:#2e7d32;border-radius:3px}
#drill{position:fixed;right:0;top:0;bottom:0;width:min(560px,92vw);background:#11151c;border-left:1px solid #2c313d;overflow:auto;transform:translateX(100%);transition:.18s;padding:16px;z-index:20}
#drill.open{transform:none}
#drill .x{float:right;cursor:pointer;color:#7d8694;font-size:18px}
pre.mermaid{background:#11151c;border:1px solid #232733;border-radius:8px;padding:10px;overflow:auto}
.muted{color:#7d8694}
</style>
__MERMAID_HEAD__
</head><body>
<header>
  <h1>🛰 Legati Observatory</h1>
  <span class="meta">host <b>__HOST__</b> · generated __GENERATED__ · static · machine-local</span>
</header>
<div id="controls">
  <span class="muted">zoom:</span>
  <button data-w="now">● now</button>
  <button data-w="today">today</button>
  <button data-w="7d">7d</button>
  <button data-w="30d">30d</button>
  <button data-w="all">all</button>
  <select id="fa"><option value="">all agents</option></select>
  <select id="fp"><option value="">all projects</option></select>
  <input id="fq" placeholder="search…" size="16">
  <span class="muted" id="summary"></span>
</div>
<section><h2>Live sessions (L0)</h2><div id="live"></div></section>
<section><h2>Totals (in window)</h2><div class="cards" id="counts"></div></section>
<section><h2>Cost by project</h2><div id="cost"></div></section>
<section><h2>Orchestration</h2><pre class="mermaid">__GRAPH__</pre></section>
<section><h2>Sessions — click to drill (L3)</h2><div id="sessions"></div></section>
<section><h2>Activity feed</h2><div id="feed"></div></section>
<div id="drill"></div>
<script>
const DATA=__DATA__;
const NOW=Date.now(), STALE=(DATA.stale_min||10)*60000, DAY=86400000;
let F={win:"7d",agent:"",project:"",q:""};
const $=s=>document.querySelector(s), el=(t,p={})=>Object.assign(document.createElement(t),p);
const esc=s=>(s==null?"":(""+s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function inWin(ts){const t=Date.parse(ts); if(isNaN(t))return false;
  if(F.win==="all")return true;
  if(F.win==="now")return (NOW-t)<=STALE;
  if(F.win==="today"){const d=new Date();d.setHours(0,0,0,0);return t>=d.getTime();}
  const ms=(F.win==="7d"?7:30)*DAY; return (NOW-t)<=ms;}
function fev(){const q=F.q.toLowerCase();
  return DATA.events.filter(e=>inWin(e.ts)&&(!F.agent||e.agent===F.agent)&&(!F.project||e.project===F.project)
    &&(!q||JSON.stringify(e).toLowerCase().includes(q)));}
function ageStr(ts){const m=(NOW-Date.parse(ts))/60000; if(m<60)return Math.round(m)+"m";
  if(m<1440)return Math.round(m/60)+"h"; return Math.round(m/1440)+"d";}
function renderLive(){const live=(DATA.sessions||[]).filter(s=>(NOW-Date.parse(s.last_seen))<=STALE)
    .sort((a,b)=>b.last_seen.localeCompare(a.last_seen));
  if(!live.length){$("#live").innerHTML='<span class="muted">none live</span>';return;}
  let h="<table><tr><th></th><th>agent</th><th>project</th><th>task</th><th>seen</th></tr>";
  live.forEach(s=>h+=`<tr><td><span class="dot live"></span></td><td class="agent">${esc(s.agent)}</td>
    <td class="mono">${esc(s.project||"")}</td><td>${esc(s.current_task||"—")}</td><td>${ageStr(s.last_seen)}</td></tr>`);
  $("#live").innerHTML=h+"</table>";}
function renderCounts(){const ev=fev(); const sess=new Set(ev.map(e=>e.session_id)).size;
  const tools=ev.filter(e=>e.type==="tool_use").length;
  const cost=ev.reduce((a,e)=>a+(e.cost_usd||0),0);
  const c=[["events",ev.length],["sessions",sess],["tool calls",tools],["cost $",cost.toFixed(2)]];
  $("#counts").innerHTML=c.map(([l,n])=>`<div class="card"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");
  $("#summary").textContent=`${ev.length} events · ${sess} sessions · window ${F.win}`;}
function renderCost(){const ev=fev(),by={};ev.forEach(e=>{if(e.cost_usd)by[e.project||"?"]=(by[e.project||"?"]||0)+e.cost_usd;});
  const rows=Object.entries(by).sort((a,b)=>b[1]-a[1]); if(!rows.length){$("#cost").innerHTML='<span class="muted">no cost data in window</span>';return;}
  const max=rows[0][1]; let h="<table>";
  rows.forEach(([p,v])=>h+=`<tr><td class="mono" style="width:240px">${esc(p)}</td>
    <td style="width:60px">$${v.toFixed(2)}</td><td><div class="bar" style="width:${Math.max(2,100*v/max)}%"></div></td></tr>`);
  $("#cost").innerHTML=h+"</table>";}
function renderSessions(){const ev=fev(),by={};
  ev.forEach(e=>{const s=by[e.session_id]||(by[e.session_id]={n:0,last:"",agent:e.agent,project:e.project});
    s.n++; if(e.ts>s.last)s.last=e.ts; if(e.agent)s.agent=e.agent;});
  const rows=Object.entries(by).sort((a,b)=>b[1].last.localeCompare(a[1].last)).slice(0,80);
  if(!rows.length){$("#sessions").innerHTML='<span class="muted">no sessions in window</span>';return;}
  let h="<table><tr><th>agent</th><th>session</th><th>project</th><th>events</th><th>last</th></tr>";
  rows.forEach(([sid,s])=>h+=`<tr class="clk" data-sid="${esc(sid)}"><td class="agent">${esc(s.agent)}</td>
    <td class="mono">${esc(sid.slice(0,12))}</td><td class="mono">${esc(s.project||"")}</td><td>${s.n}</td><td>${ageStr(s.last)}</td></tr>`);
  $("#sessions").innerHTML=h+"</table>";
  document.querySelectorAll("#sessions tr.clk").forEach(r=>r.onclick=()=>drill(r.dataset.sid));}
function renderFeed(){const ev=fev().slice(-250).reverse();
  let h="<table><tr><th>time</th><th>agent</th><th>type</th><th>tool</th><th>target</th></tr>";
  ev.forEach(e=>h+=`<tr><td class="mono">${esc((e.ts||"").slice(5,19).replace("T"," "))}</td>
    <td class="agent">${esc(e.agent)}</td><td>${esc(e.type)}</td><td>${esc(e.tool||"")}</td>
    <td class="mono">${esc(e.target||"")}</td></tr>`);
  $("#feed").innerHTML=h+"</table>";}
function drill(sid){const ev=DATA.events.filter(e=>e.session_id===sid).reverse();
  let h=`<span class="x" onclick="document.getElementById('drill').classList.remove('open')">✕</span>
    <h2>session ${esc(sid.slice(0,16))}</h2><div class="muted">${ev.length} events</div><table>`;
  ev.forEach(e=>h+=`<tr><td class="mono">${esc((e.ts||"").slice(5,19).replace("T"," "))}</td>
    <td class="agent">${esc(e.agent)}</td><td>${esc(e.tool||e.type)}</td><td class="mono">${esc(e.target||"")}</td></tr>`);
  const d=$("#drill"); d.innerHTML=h+"</table>"; d.classList.add("open");}
function renderAll(){renderLive();renderCounts();renderCost();renderSessions();renderFeed();}
function fillSelect(id,key){const vals=[...new Set(DATA.events.map(e=>e[key]).filter(Boolean))].sort();
  const s=$(id); vals.forEach(v=>s.appendChild(el("option",{value:v,textContent:v})));}
fillSelect("#fa","agent"); fillSelect("#fp","project");
document.querySelectorAll("#controls button").forEach(b=>b.onclick=()=>{
  F.win=b.dataset.w; document.querySelectorAll("#controls button").forEach(x=>x.classList.toggle("on",x===b)); renderAll();});
$("#fa").onchange=e=>{F.agent=e.target.value;renderAll();};
$("#fp").onchange=e=>{F.project=e.target.value;renderAll();};
$("#fq").oninput=e=>{F.q=e.target.value;renderAll();};
document.querySelector('#controls button[data-w="7d"]').classList.add("on");
renderAll();
</script>
__MERMAID_INIT__
</body></html>
"""


def build_html(data: dict, graph: str, mermaid_src: str) -> str:
    data_json = json.dumps(data).replace("</", "<\\/")
    graph_esc = (graph or "_no sessions_").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if mermaid_src:
        head = f'<script src="{mermaid_src}"></script>'
        init = ('<script>window.addEventListener("load",function(){'
                'try{mermaid.initialize({startOnLoad:false,theme:"dark"});mermaid.run();}'
                'catch(e){console.error("mermaid:",e);}});</script>')
    else:
        head = ""
        init = ""
    return (HTML_TEMPLATE
            .replace("__HOST__", data.get("host", "?"))
            .replace("__GENERATED__", data.get("generated", ""))
            .replace("__DATA__", data_json)
            .replace("__GRAPH__", graph_esc)
            .replace("__MERMAID_HEAD__", head)
            .replace("__MERMAID_INIT__", init))


def render_html(a) -> int:
    ensure_dirs()
    sessions = load_sessions()
    since = getattr(a, "since", None)
    days = parse_window(since) if since else 30      # default embed window: 30 days
    events = load_events_window(days)
    CAP = 8000
    if len(events) > CAP:
        events = events[-CAP:]
    locks = []
    for p in sorted(LOCKS.glob("*.lock")):
        d = read_lock(p)
        if d and not lock_expired(d):
            locks.append(d)
    graph = orchestration_graph_text(sessions, events) or ""
    vendor = Path(__file__).resolve().parent / "vendor" / "mermaid.min.js"
    data = {"host": host(), "generated": iso(), "stale_min": STALE_MIN,
            "sessions": sessions, "locks": locks, "events": events}
    out = RENDER / f"dashboard-{host()}.html"
    out.write_text(build_html(data, graph, "../vendor/mermaid.min.js" if vendor.exists() else ""))
    snap = HISTORY / f"dashboard-{host()}-{now().strftime('%Y%m%d-%H%M%S')}.html"
    snap.write_text(build_html(data, graph, "../../vendor/mermaid.min.js" if vendor.exists() else ""))
    win = "all" if days is None else (f"{days}d" if days else "today")
    print(f"wrote {out.relative_to(ROOT)}  ({len(events)} events embedded, default window {win})")
    print(f"  + history snapshot {snap.relative_to(ROOT)}")
    if not vendor.exists():
        print("  note: vendor/mermaid.min.js missing — graph shows as text. Fetch once:")
        print("    curl -sL https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js \\")
        print("      -o engineering-projects/legati-observatory/vendor/mermaid.min.js")
    return 0


def cmd_render(a) -> int:
    if getattr(a, "html", False):
        return render_html(a)
    return render_markdown(a)


def render_markdown(a) -> int:
    ensure_dirs()
    sessions = load_sessions()
    live = sorted([s for s in sessions if age_min(s.get("last_seen", iso())) <= STALE_MIN],
                  key=lambda r: r.get("last_seen", ""), reverse=True)
    stale = [s for s in sessions if age_min(s.get("last_seen", iso())) > STALE_MIN]

    locks = []
    for p in sorted(LOCKS.glob("*.lock")):
        d = read_lock(p)
        if d and not lock_expired(d):
            locks.append(d)

    # today's events: recent activity + per-project cost
    day = now().strftime("%Y-%m-%d")
    events = []
    ef = EVENTS / f"{day}.jsonl"
    if ef.exists():
        for line in ef.read_text().splitlines():
            try:
                events.append(json.loads(line))
            except Exception:
                pass
    cost = {}
    for e in events:
        if e.get("cost_usd"):
            cost[e.get("project", "?")] = cost.get(e.get("project", "?"), 0.0) + e["cost_usd"]

    L = []
    L.append(f"# Legati Observatory — {host()}")
    L.append("")
    L.append(f"_Rendered {iso()} · stale threshold {STALE_MIN}m · machine-local, gitignored._")
    L.append("")
    L.append("## Live sessions")
    L.append("")
    if live:
        L.append("| Agent | Host | Project | Task | Seen |")
        L.append("|---|---|---|---|---|")
        for s in live:
            L.append(f"| **{s.get('agent','?')}** | {s.get('host','?')} | "
                     f"`{s.get('project','?')}` | {s.get('current_task','—')} | "
                     f"{age_min(s.get('last_seen', iso())):.0f}m |")
    else:
        L.append("_None live._")
    L.append("")
    L.append("## Active locks (pheromone trails)")
    L.append("")
    if locks:
        L.append("| Slug | Owner | Task | Age | TTL |")
        L.append("|---|---|---|---|---|")
        for d in locks:
            L.append(f"| `{d['slug']}` | {d['agent']} | {d.get('task','')} | "
                     f"{age_min(d['ts']):.0f}m | {d.get('ttl_minutes')}m |")
    else:
        L.append("_No active locks._")
    L.append("")
    L.append("## Orchestration")
    L.append("")
    L += mermaid_orchestration(sessions, events)
    L.append("")
    if cost:
        L.append("## Cost today (best-effort)")
        L.append("")
        L.append("| Project | USD |")
        L.append("|---|---:|")
        for proj, c in sorted(cost.items(), key=lambda kv: -kv[1]):
            L.append(f"| `{proj}` | {c:.2f} |")
        L.append("")
    L.append("## Recent activity")
    L.append("")
    recent = events[-15:]
    if recent:
        for e in reversed(recent):
            t = e.get("ts", "")[11:19]
            detail = e.get("tool", e.get("type", ""))
            tgt = e.get("target", "")
            L.append(f"- `{t}` **{e.get('agent','?')}** {detail} {tgt}".rstrip())
    else:
        L.append("_No events today._")
    if stale:
        L.append("")
        L.append(f"_{len(stale)} stale session record(s) (no heartbeat > {STALE_MIN}m)._")
    L.append("")

    content = "\n".join(L)
    out = RENDER / f"dashboard-{host()}.md"
    out.write_text(content)
    snap = HISTORY / f"dashboard-{host()}-{now().strftime('%Y%m%d-%H%M%S')}.md"
    snap.write_text(content)
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"  + history snapshot {snap.relative_to(ROOT)}")
    return 0


# ---------------------------------------------------------------- argparse
def main() -> int:
    ap = argparse.ArgumentParser(prog="obs", description="Legati Observatory CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("emit", help="append an event (used by capture adapters)")
    e.add_argument("--type", required=True)
    e.add_argument("--tool")
    e.add_argument("--target")
    e.add_argument("--model")
    e.add_argument("--parent")
    e.add_argument("--cwd")
    e.add_argument("--tokens-in", type=int, dest="tokens_in")
    e.add_argument("--tokens-out", type=int, dest="tokens_out")
    e.add_argument("--cost", type=float)
    e.set_defaults(fn=cmd_emit)

    ag = sub.add_parser("agent", help="set the active legatus for this session (call on persona switch)")
    ag.add_argument("name")
    ag.set_defaults(fn=cmd_agent)

    t = sub.add_parser("task", help="set this session's current task")
    t.add_argument("text")
    t.set_defaults(fn=cmd_task)

    h = sub.add_parser("heartbeat", help="bump this session's last-seen")
    h.set_defaults(fn=cmd_heartbeat)

    w = sub.add_parser("who", help="list live legati sessions")
    w.set_defaults(fn=cmd_who)

    lk = sub.add_parser("lock", help="advisory locks (atomic exclusive create)")
    lk.add_argument("action", choices=["acquire", "check", "release"])
    lk.add_argument("slug")
    lk.add_argument("--task")
    lk.add_argument("--ttl", type=int, default=15)
    lk.add_argument("--force", action="store_true")
    lk.set_defaults(fn=cmd_lock)

    r = sub.add_parser("render", help="render the per-host static dashboard")
    r.add_argument("--html", action="store_true", help="emit the interactive single-file HTML (zoom L0–L3) instead of markdown")
    r.add_argument("--since", help="embed window for --html: today|7d|30d|all (default 30d)")
    r.set_defaults(fn=cmd_render)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
