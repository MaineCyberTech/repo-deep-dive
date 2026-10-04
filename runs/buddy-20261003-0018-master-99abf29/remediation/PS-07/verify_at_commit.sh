set -u
cd /srv/work/buddy
echo "### git state"
echo "HEAD: $(git rev-parse HEAD)"
echo "status lines: $(git status --porcelain --untracked-files=all | wc -l)"
echo
echo "### primary gate: npm ci ; npm run lint ; npm run typecheck ; npm run test"
npm ci
echo "NPMCI_EXIT=$?"
npm run lint
echo "LINT_EXIT=$?"
npm run typecheck
echo "TYPECHECK_EXIT=$?"
npm run test
echo "TEST_EXIT=$?"
echo
echo "### patch-set verification: npm run build ; npm run test -- error"
npm run build
echo "BUILD_EXIT=$?"
npm run test -- error
echo "ERRORTEST_EXIT=$?"
echo
echo "### secret gate: gitleaks on git archive HEAD"
rm -rf /tmp/glscan-ps07c
mkdir -p /tmp/glscan-ps07c
git archive HEAD | tar -x -C /tmp/glscan-ps07c
gitleaks detect --no-git --redact --source /tmp/glscan-ps07c -v
echo "GITLEAKS_EXIT=$?"
echo "__VERIFY_AT_COMMIT_DONE"
