#!/usr/bin/env bash
set -u
rm -rf /srv/work/snowride-p1-3
git clone -b remediation/p1-3-20261003-0018-main-59e12b9 /srv/work/p1-3.bundle /srv/work/snowride-p1-3
echo "clone_exit=$?"
cd /srv/work/snowride-p1-3
echo "HEAD: $(git rev-parse HEAD)"
echo "dirty count: $(git status --porcelain | wc -l)"
echo "workflow sha256: $(sha256sum .github/workflows/ci-foundation.yml | cut -d' ' -f1)"
