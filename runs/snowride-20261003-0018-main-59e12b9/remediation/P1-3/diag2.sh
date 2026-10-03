#!/usr/bin/env bash
set -u
cd /srv/work/snowride
echo "== git blob vs worktree hash (tests/ledger-format.test.ts) =="
git show HEAD:tests/ledger-format.test.ts | md5sum
md5sum tests/ledger-format.test.ts
echo "== non-ASCII bytes in worktree copy =="
grep -naP "[^\x00-\x7F]" tests/ledger-format.test.ts | head || echo "(none)"
echo "== CR count =="
echo -n "worktree CR lines: "; grep -c $'\r' tests/ledger-format.test.ts || true
echo -n "git blob CR lines: "; git show HEAD:tests/ledger-format.test.ts | grep -c $'\r' || true
echo
echo "== vitest single suite in CLEAN worktree (shared node_modules) =="
cd /srv/work/snowride-p1-3
ln -sfn /srv/work/snowride/node_modules node_modules
npx --no-install vitest run tests/ledger-format.test.ts 2>&1 | tail -15
echo "clean_vitest_exit=${PIPESTATUS[0]}"
