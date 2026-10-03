#!/usr/bin/env bash
# Diagnostic: why does tests/ledger-format.test.ts fail in the tar-extracted
# worktree? Compare native ESM load of the .mjs module and run the single suite.
set -u
echo "== file types =="
file scripts/assurance/ledger-format.mjs tests/ledger-format.test.ts 2>/dev/null || true
echo
echo "== node --check .mjs (dirty worktree, CRLF) =="
cd /srv/work/snowride
node --check scripts/assurance/ledger-format.mjs; echo "mjs_check_exit=$?"
echo
echo "== native import of .mjs (dirty worktree) =="
node --input-type=module -e 'const u=new URL("file:///srv/work/snowride/scripts/assurance/ledger-format.mjs"); import(u).then(()=>console.log("import ok")).catch(e=>{console.error("IMPORT_FAIL:",e.message);process.exit(3)});'; echo "import_exit=$?"
echo
echo "== vitest single suite (dirty worktree) =="
npx --no-install vitest run tests/ledger-format.test.ts 2>&1 | tail -40; echo "vitest_exit=${PIPESTATUS[0]}"
