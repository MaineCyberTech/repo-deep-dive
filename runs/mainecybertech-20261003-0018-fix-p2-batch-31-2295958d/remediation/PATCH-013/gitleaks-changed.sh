#!/usr/bin/env bash
# Run gitleaks over only the files changed by this patch (working tree vs HEAD),
# so the secret gate covers the diff without scanning the whole repo corpus.
set -u
STAGE=/tmp/p013-changed
rm -rf "$STAGE"
mkdir -p "$STAGE"
FILES="$(git status --porcelain | awk '{print $2}' | grep -v '^$' || true)"
if [ -z "$FILES" ]; then
  echo "No changed files to scan"
  exit 0
fi
for f in $FILES; do
  mkdir -p "$STAGE/$(dirname "$f")"
  cp -r "$f" "$STAGE/$f"
done
echo "Scanning changed files:"
printf '%s\n' "$FILES"
gitleaks detect --no-git --redact --source "$STAGE"
echo "gitleaks_exit:$?"
