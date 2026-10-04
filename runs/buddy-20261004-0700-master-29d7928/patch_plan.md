# Patch plan

## DEP-P1-001 - Next.js 14.2.35 is EOL and ships unpatched known CVEs

Upgrade to a supported line (15.5.26+ or 16.3.6+); if deferred, record a dated risk acceptance and re-check advisories monthly.

## DEP-P2-001 - Vulnerable transitive copies: nanoid 3.3.15 and nested postcss 8.4.31

Bump the direct postcss dev dep to >=8.5.19 and nanoid to a fixed 3.3.x; defer the Next.js-pinned nested postcss to the framework upgrade in buddy-DEP-001.

## SUPPLY-P1-001 - Release workflow runs install scripts and unpinned actions with a write token

Pin every uses: to a full commit SHA; scope permissions to the job/step that needs writes and keep npm ci under contents: read; prefer npm ci --ignore-scripts or isolate install in a read-only job; bump stale majors (checkout/setup-node v4->v7, attest-build-provenance v1->v4, action-gh-release v2->v3).

## CI-P2-001 - No dependency-vulnerability, license, or secret-scanning gate in CI

Add CI jobs: npm audit --audit-level=high --omit=dev, actions/dependency-review-action on PRs, a gitleaks/secret scan, and a license allow/deny check once a policy exists.

## CI-P2-002 - Release is not gated by environment protection or protected tags

Create a release GitHub Environment with required reviewers, apply a v* tag protection rule, and enable branch protection on master requiring the CI check and CODEOWNERS review; document in docs/release-process.md.

## CI-P3-001 - Release SBOM includes dev dependencies, inconsistent with the npm script

Use one SBOM definition; if the release ships production code, generate npm sbom --omit=dev and state excluded items explicitly.

## PORT-P3-001 - .gitattributes missing (no line-ending policy)

Add .gitattributes with '* text=auto eol=lf' and mark binary asset types as binary.

## CONF-P3-001 - Product docs still claim saves are not runtime-validated

Update README.md:19-22 and the docs/README.md status matrix to verified-fixed with commit evidence.

## SUPPLY-P3-001 - License is explicitly pending and vendored prompt-pack provenance is unconfirmed

Choose a license (or keep proprietary + internal-only) and record the prompt-pack provenance/ownership decision in NOTICE; add a license-policy gate if the project opens up.

