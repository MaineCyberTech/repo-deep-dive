#!/usr/bin/env bash
# pack_digest.sh — regenerate PACK_DIGEST.txt (file inventory + sha256) for this pack.
# Run after any change to the pack tree. Usage: tools/pack_digest.sh
set -euo pipefail

cd "$(dirname "$0")/.."

tmp="$(mktemp)"
# Environment-local files are untracked by the digest (opencode.json pins a
# local default model; the rest is OS/editor junk). Keep this list in sync
# with the skip list in lint_pack.sh.
find . -type f \
  ! -path './.git/*' \
  ! -path '*/__pycache__/*' \
  ! -name 'PACK_DIGEST.txt' \
  ! -name 'opencode.json' \
  ! -name '.DS_Store' \
  ! -name 'Thumbs.db' \
  ! -name '*~' \
  -print0 | sort -z > "$tmp"
count=$(tr -cd '\0' < "$tmp" | wc -c)

{
  echo "# repo-deep-dive pack digest"
  echo "# generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# files: $count"
  echo "# format: sha256  path"
  while IFS= read -r -d '' f; do sha256sum "$f"; done < "$tmp" | sed 's/ \*/  /'
} > PACK_DIGEST.txt

rm -f "$tmp"
echo "wrote PACK_DIGEST.txt ($count files)"
