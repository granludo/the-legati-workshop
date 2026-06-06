#!/bin/bash
# tools/wiki/batch_ingest.sh — drive tools/wiki/ingest.py --apply over a file list.
#
# Each line of the list file is a repo-relative path to a markdown source.
# Runs ingest.py --apply per file (idempotent: re-ingesting a file already
# referenced by a wiki entry is a no-op on that entry). Commits a checkpoint
# every COMMIT_EVERY files so a long run leaves a durable trail and a crash
# doesn't lose work. At the end, rebuilds co-occurrence backlinks + facet
# indexes and makes a final commit.
#
# Only ever `git add wiki/` — never -A — so parallel-session work in other
# folders is never swept into these commits.
#
# Usage:
#   tools/wiki/batch_ingest.sh /tmp/wiki-ingest-list.txt "cabalga + new docs"
#
set -uo pipefail

LIST="${1:?usage: batch_ingest.sh <file-list> [label]}"
LABEL="${2:-new docs}"
COMMIT_EVERY=15
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO" || exit 1

TOTAL=$(grep -c . "$LIST")
N=0
FAILED=0

echo "[batch_ingest] $TOTAL files from $LIST — label: $LABEL"
echo "[batch_ingest] repo: $REPO"

while IFS= read -r f; do
  [ -z "$f" ] && continue
  N=$((N + 1))
  echo ""
  echo "=== [$N/$TOTAL] ingest --apply: $f ==="
  if [ ! -f "$f" ]; then
    echo "  [SKIP] not found on disk"
    continue
  fi
  if ! python3 tools/wiki/ingest.py --apply "$f" 2>&1 | tail -6; then
    echo "  [FAIL] ingest returned non-zero for $f"
    FAILED=$((FAILED + 1))
  fi
  if [ $((N % COMMIT_EVERY)) -eq 0 ]; then
    git add wiki/
    if ! git diff --cached --quiet; then
      git commit -q -m "wiki: batch ingest checkpoint ${N}/${TOTAL} (${LABEL})

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
      echo "  [checkpoint] committed at $N/$TOTAL"
    fi
  fi
done < "$LIST"

echo ""
echo "[batch_ingest] ingest pass done ($N processed, $FAILED failed). Rebuilding co-occurrence + indexes…"
python3 tools/wiki/build_cooccurrence.py 2>&1 | tail -3
python3 tools/wiki/render_indexes.py 2>&1 | tail -3

git add wiki/
if ! git diff --cached --quiet; then
  git commit -q -m "wiki: batch ingest of ${TOTAL} new docs + co-occurrence + indexes (${LABEL})

Final commit of the batch ingest run. ${N} files processed, ${FAILED} failed.
Co-occurrence backlinks and facet INDEXes rebuilt over the full wiki tree.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
  echo "[batch_ingest] final commit done."
else
  echo "[batch_ingest] nothing new to commit at finalize."
fi

echo "[batch_ingest] DONE — $N processed, $FAILED failed."
