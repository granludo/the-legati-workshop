#!/usr/bin/env bash
# Print this host's section of memory/reference_hosts.md: from the "## <hostname>" heading (case-insensitive)
# to the next "## " heading. A legatus reads this at boot instead of the whole host profile.
#   bash tools/legati/host-section.sh            # section for `hostname`
#   bash tools/legati/host-section.sh my-desktop # section for another host
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
H="${1:-$(hostname -s)}"; H="$(printf '%s' "$H" | tr '[:upper:]' '[:lower:]')"
OUT="$(awk -v h="$H" 'BEGIN{p=0} /^## /{p=(index(tolower($0),h)>0)} p' "$REPO/memory/reference_hosts.md" 2>/dev/null)"
if [ -n "$OUT" ]; then printf '%s\n' "$OUT"; exit 0; fi
echo "[host-section] no section for '$H' in memory/reference_hosts.md: tell the principal, do not assume a toolchain (skills/start-here.md, step 6, writes one)"; exit 1
