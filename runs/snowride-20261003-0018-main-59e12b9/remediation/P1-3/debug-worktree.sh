#!/usr/bin/env bash
set -u
cd /srv/work/snowride
echo "inside-work-tree: $(git rev-parse --is-inside-work-tree)"
echo "rev-parse HEAD: $(git rev-parse HEAD)"
echo "symbolic-ref HEAD: $(git symbolic-ref HEAD 2>&1)"
echo "worktree list:"; git worktree list
echo "try add with explicit sha:"
rm -rf /srv/work/snowride-p1-3
git worktree add --detach /srv/work/snowride-p1-3 "$(git rev-parse HEAD)"
echo "add_exit=$?"
ls -la /srv/work/snowride-p1-3/.github/workflows/ 2>&1 | head
