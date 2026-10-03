#!/usr/bin/env bash
set -u
cd /srv/work/snowride
echo "git-dir: $(git rev-parse --git-dir)"
echo "cat-file -t HEAD: $(git cat-file -t HEAD 2>&1)"
echo "cat-file -t d61c968: $(git cat-file -t d61c968a1a5166b65204abbe6bf62559bcd9cd1c 2>&1)"
echo "loose object dir d6:"; ls -la .git/objects/d6 2>&1 | head
echo "count objects:"; find .git/objects -type f | wc -l
echo "fsck:"; git fsck --no-progress 2>&1 | head -20
