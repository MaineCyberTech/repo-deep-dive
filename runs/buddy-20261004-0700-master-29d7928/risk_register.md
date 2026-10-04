# Follow-up register

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| DEP-P1-001 | P1 | Next.js 14.2.35 is EOL and ships unpatched known CVEs | @owner | DEP | open | Upgrade to a supported line (15.5.26+ or 16.3.6+); if deferred, record a dated risk acceptance and re-check advisories m |
| DEP-P2-001 | P2 | Vulnerable transitive copies: nanoid 3.3.15 and nested postcss 8.4.31 | @owner | DEP | open | Bump the direct postcss dev dep to >=8.5.19 and nanoid to a fixed 3.3.x; defer the Next.js-pinned nested postcss to the  |
| SUPPLY-P1-001 | P1 | Release workflow runs install scripts and unpinned actions with a write token | @owner | SUPPLY | open | Pin every uses: to a full commit SHA; scope permissions to the job/step that needs writes and keep npm ci under contents |
| CI-P2-001 | P2 | No dependency-vulnerability, license, or secret-scanning gate in CI | @owner | CI | open | Add CI jobs: npm audit --audit-level=high --omit=dev, actions/dependency-review-action on PRs, a gitleaks/secret scan, a |
| CI-P2-002 | P2 | Release is not gated by environment protection or protected tags | @owner | CI | open | Create a release GitHub Environment with required reviewers, apply a v* tag protection rule, and enable branch protectio |
| CI-P3-001 | P3 | Release SBOM includes dev dependencies, inconsistent with the npm script | @owner | CI | open | Use one SBOM definition; if the release ships production code, generate npm sbom --omit=dev and state excluded items exp |
| PORT-P3-001 | P3 | .gitattributes missing (no line-ending policy) | @owner | PORT | open | Add .gitattributes with '* text=auto eol=lf' and mark binary asset types as binary. |
| CONF-P3-001 | P3 | Product docs still claim saves are not runtime-validated | @owner | CONF | open | Update README.md:19-22 and the docs/README.md status matrix to verified-fixed with commit evidence. |
| SUPPLY-P3-001 | P3 | License is explicitly pending and vendored prompt-pack provenance is unconfirmed | @owner | SUPPLY | open | Choose a license (or keep proprietary + internal-only) and record the prompt-pack provenance/ownership decision in NOTIC |
