#!/usr/bin/env bash
set -u
cd /srv/work/snowride
echo "main tar worktree HEAD: $(git rev-parse HEAD)"
rm -rf /srv/work/snowride-p1-3
git worktree prune
git worktree add --detach /srv/work/snowride-p1-3 HEAD
echo "clean worktree HEAD: $(git -C /srv/work/snowride-p1-3 rev-parse HEAD)"
echo "clean worktree dirty count: $(git -C /srv/work/snowride-p1-3 status --porcelain | wc -l)"
echo "clean workflow sha256: $(sha256sum /srv/work/snowride-p1-3/.github/workflows/ci-foundation.yml | cut -d' ' -f1)"
