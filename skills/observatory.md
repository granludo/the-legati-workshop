# /observatory — see who's working and don't step on them

**When to invoke:** whenever more than one agent session may be running against this repo at once — before you regenerate a shared file (a dashboard, an index, a backlog), when you want to know who else is live, or when you switch persona and want your activity attributed correctly. Also the skill to read when you want to *render* the dashboard.

**Who runs it:** any agent (any legatus). The capture is automatic via hooks; this skill is the **self-report + coordination** layer that only the agent can drive.

The full design is in [`../engineering-projects/legati-observatory/README.md`](../engineering-projects/legati-observatory/README.md) and [`DESIGN.md`](../engineering-projects/legati-observatory/DESIGN.md). This skill is the operational how-to.

---

## The one environment variable

```bash
OBS=engineering-projects/legati-observatory/obs.py
```

## On every persona switch — attribute your events

The hooks capture every tool call automatically, but they need to know *which* legatus is acting. The moment you switch persona, run:

```bash
python3 $OBS agent <your-legatus-name>     # e.g. orchestrator, writer, reviewer
```

This writes a per-session marker that wins over the session default, so all subsequent captured events attribute to the active legatus until the next switch. Idempotent and cheap — run it on every switch.

## Set what you're doing (optional but useful)

```bash
python3 $OBS task "drafting the methodology paper §5"
```

`current_task` is the human-readable "what am I doing" that only you know — it shows up in the presence table.

## Before a risky shared write — check, then lock

This is the point of the whole thing. If you are about to regenerate a file another session might also be writing (a dashboard, an `INDEX.md`, a `BACKLOG.md`):

```bash
python3 $OBS who                                          # 1. who else is live, doing what?
python3 $OBS lock acquire <slug> --task "..." --ttl 15    # 2. claim it (atomic; fails if already held)
#   ... do the write ...
python3 $OBS lock release <slug>                          # 3. release when done
```

`lock acquire` uses atomic exclusive-create, so **two cooperating agents cannot both win the same lock**. If the acquire **fails**, it returns the current owner — **surface that to the user and stand down**, do not race. A lock auto-frees after its TTL if the owner crashed (no deadlock).

The lock is *advisory* — it works because cooperating agents honor it. Encode the discipline in your agent guide: *before regenerating any shared file, acquire its lock; if the acquire is denied, stand down.*

## Render the dashboard

```bash
python3 $OBS render            # markdown -> render/dashboard-<host>.md  (read it in your editor)
python3 $OBS render --html     # interactive single-file HTML -> render/dashboard-<host>.html (open in a browser)
```

Both surfaces are static, gitignored, and per-host. The markdown is the at-a-glance view; the HTML is interactive (filter by agent/project/time, drill into a session, cost bars).

## What you do NOT need to do

- **You don't start a server or a daemon.** Everything is static files rendered on demand.
- **You don't commit any of it.** `.observatory/` and `render/` are gitignored — they're machine- and host-dependent.
- **You don't configure capture per session.** The hooks in `.claude/settings.json` already wire it up; a fresh clone captures on the next session.
