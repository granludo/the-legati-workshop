#!/usr/bin/env bash
# tools/refs-check/setup.sh
#
# Idempotent setup of the refs-check toolchain on a new host. Run this when
# moving to a fresh Mac (the roving MacBook, a new Studio, anywhere bibsleuth
# is not yet installed). Re-runs safely — checks for existing install before
# acting.
#
# Marc 2026-05-28: "make sure this tool is pre approved" — see also the
# project .claude/settings.json allowlist, which is the per-repo permission
# layer. This script handles the system-level install; the allowlist handles
# the harness-level permission.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "→ host: $(hostname)"
echo "→ python: $(python3 --version 2>&1)"

# 1. uv — required to install bibsleuth with the right Python pin.
if ! command -v uv >/dev/null 2>&1; then
  echo -e "${RED}✗ uv not found.${NC} Install uv first: https://docs.astral.sh/uv/getting-started/installation/"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
echo -e "${GREEN}✓ uv${NC} $(uv --version)"

# 2. Python 3.12+ — bibsleuth's requirement. uv will fetch + manage it for us.
if ! uv python find 3.12 >/dev/null 2>&1; then
  echo -e "${YELLOW}→ installing managed CPython 3.12 via uv${NC}"
  uv python install 3.12
fi
echo -e "${GREEN}✓ python3.12${NC} available to uv"

# 3. bibsleuth — install (or upgrade) as a uv tool, pinned to Python 3.12.
if command -v bibsleuth >/dev/null 2>&1; then
  INSTALLED_VERSION=$(bibsleuth --version 2>&1 || echo "unknown")
  echo -e "${GREEN}✓ bibsleuth already installed${NC} ($INSTALLED_VERSION)"
  echo "  to upgrade: uv tool upgrade bibsleuth"
else
  echo -e "${YELLOW}→ installing bibsleuth via uv tool${NC}"
  uv tool install bibsleuth --python 3.12
  echo -e "${GREEN}✓ bibsleuth installed${NC} ($(bibsleuth --version))"
fi

# 4. Quick smoke test against a known-real reference (the LAMB 2025 paper),
#    confirming network + provider APIs are reachable from this host.
echo "→ smoke test (bibsleuth + provider reachability)"
SMOKE_DIR=$(mktemp -d -t refs-check-smoke)
trap "rm -rf $SMOKE_DIR" EXIT
TMP_BIB="$SMOKE_DIR/smoke.bib"
SMOKE_OUT="$SMOKE_DIR/report"
cat > "$TMP_BIB" <<'EOF'
@article{alier2025lamb,
  title={LAMB: An open-source software framework to create artificial intelligence assistants deployed and integrated into learning management systems},
  author={Alier, Marc and Pereira, Juanan and Garc{\'\i}a-Pe{\~n}alvo, Francisco and Casa{\~n}, Maria Jos{\'e} and Cabr{\'e}, Jose},
  journal={Computer Standards \& Interfaces},
  volume={92},
  year={2025},
  doi={10.1016/j.csi.2024.103940}
}
EOF
bibsleuth check "$TMP_BIB" --no-llm --format json -o "$SMOKE_OUT" >/dev/null 2>&1 || true
if [ -f "${SMOKE_OUT}.json" ]; then
  VERDICT=$(python3 -c "import json; d = json.load(open('${SMOKE_OUT}.json')); print(d['results'][0]['verdict'])" 2>/dev/null || echo "?")
  if [ "$VERDICT" = "verified" ] || [ "$VERDICT" = "likely" ]; then
    echo -e "${GREEN}✓ smoke test passed${NC} (LAMB 2025 → $VERDICT)"
  else
    echo -e "${YELLOW}⚠ smoke test ran but LAMB 2025 came back as '$VERDICT'${NC}"
    echo "  This may indicate provider rate-limiting or a transient API issue."
    echo "  Re-run in a few minutes if you need a clean baseline."
  fi
else
  echo -e "${RED}✗ smoke test failed${NC} — bibsleuth produced no JSON output."
  echo "  Possible causes: no network, provider APIs down, bibsleuth install broken."
  exit 2
fi

# 5. Workshop wrapper script — verify the workshop wrapper is callable.
WORKSHOP_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TOOL_DIR="$WORKSHOP_ROOT/tools/refs-check"
if [ -f "$TOOL_DIR/check_refs.py" ]; then
  echo -e "${GREEN}✓ workshop wrapper${NC} at tools/refs-check/check_refs.py"
else
  echo -e "${RED}✗ workshop wrapper not found${NC}"
  echo "  Expected: $TOOL_DIR/check_refs.py"
  exit 3
fi

# 6. Playwright URL re-check layer (verify-urls.mjs) — the browser-backed
#    escalation for refs whose URL the Python pass got 403'd on (publishers that
#    bot-block non-browser clients: Macmillan, BJET, RIED, theconversation, ...).
#    Needs Node + the playwright npm package + a Chromium binary. All idempotent.
if command -v node >/dev/null 2>&1; then
  echo -e "${GREEN}✓ node${NC} $(node --version)"
  if [ -d "$TOOL_DIR/node_modules/playwright" ]; then
    echo -e "${GREEN}✓ playwright npm package${NC} already installed in tools/refs-check/"
  else
    echo -e "${YELLOW}→ installing playwright npm package in tools/refs-check/${NC}"
    ( cd "$TOOL_DIR" && npm install playwright >/dev/null 2>&1 )
    echo -e "${GREEN}✓ playwright npm package installed${NC}"
  fi
  # Chromium browser binary (~150 MB first time; reused after). Idempotent.
  if ls "$HOME/Library/Caches/ms-playwright/" 2>/dev/null | grep -q '^chromium-'; then
    echo -e "${GREEN}✓ chromium binary${NC} already provisioned"
  else
    echo -e "${YELLOW}→ provisioning Chromium (~150 MB, one-time)${NC}"
    ( cd "$TOOL_DIR" && npx playwright install chromium )
    echo -e "${GREEN}✓ chromium provisioned${NC}"
  fi
  echo -e "${GREEN}✓ URL re-check layer ready${NC} — node tools/refs-check/verify-urls.mjs <file>-refs-checks.md"
else
  echo -e "${YELLOW}⚠ node not found${NC} — the Playwright URL re-check layer (verify-urls.mjs) will be unavailable."
  echo "  Install Node (nvm recommended) then re-run this script to provision it."
  echo "  bibsleuth + check_refs.py still work without it; you lose only the bot-block-busting URL re-check."
fi

echo
echo -e "${GREEN}→ refs-check toolchain ready on $(hostname)${NC}"
echo
echo "Next step: invoke against a real .bib —"
echo "  python3 tools/refs-check/check_refs.py PATH/TO/refs.bib"
echo
echo "Per-host install state should be recorded in memory/reference_hosts.md."
