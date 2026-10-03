# 11 Supply Chain, Dependencies & Secrets

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Dependency pinning, lockfile integrity, SBOM provenance, license assurance, install-script risk, and secret handling. Read-only; no install performed.

## Evidence Reviewed

- `package.json`, `package-lock.json` (lockfileVersion 3), workspace `package.json` files
- `.github/dependabot.yml`
- `scripts/license-assurance.mjs`, `scripts/bundle-secret-gate.mjs`, `scripts/check-web-bundle.mjs`
- `scripts/assurance/assurance.sh` (daily OSV/audit/license lanes)
- `apps/realtime/Dockerfile` (dev-toolchain leak gate), `.dockerignore`
- `.env.example`, `evidence/closeout/CREDENTIAL_ROTATION_PLAN.md`, `evidence/phase3/04-credential-lifecycle/*`

## Verification Performed

- Confirmed lockfile present and all direct deps use exact versions where listed (e.g. `@supabase/supabase-js 2.116.0`, `socket.io 4.8.3`), with `^` on a few (`next`, `vitest`, `eslint`).
- Read the realtime Dockerfile prod-deps stage: `npm ci --omit=dev` plus a blocking gate that fails if `vitest`/`puppeteer`/`cyclonedx`/`libxmljs2` survive — good runtime hygiene.
- Confirmed no committed SBOM or license report for the current commit (CycloneDX is a devDependency but no generated artifact found).
- `npm audit` could not be executed (no `node_modules`).
- Ran a tracked-tree secret pattern sweep; only fixtures/placeholders found (see SEC report).

## Executive Summary

Dependency hygiene is above average for the ecosystem: a committed lockfile, exact pins for most runtime deps, a runtime-image dev-toolchain leak gate, digest-pinned container images, and a daily host lane that runs `npm audit --omit=dev`, OSV, and license assurance. The gaps are that these checks are not per-PR, no SBOM is produced/committed for the release, and license enforcement is host-only. Install scripts are allowed for several packages, which is normal for esbuild/puppeteer but is a supply-chain surface worth tracking.

## Inventory

| Item | State |
|---|---|
| Lockfile | `package-lock.json`, lockfileVersion 3 |
| Runtime dep pinning | mostly exact; `next`/`vitest`/`eslint` caret |
| SBOM (CycloneDX) | tool devDep present; no artifact for HEAD |
| npm audit | daily host lane only; not CI |
| OSV scan | daily host lane only |
| License gate | `license-assurance.mjs`, daily lane only |
| Container images | digest-pinned (nginx, otel, certbot) |
| Install scripts | `allowScripts` for esbuild/protobufjs/puppeteer/unrs-resolver |

## Findings

### Finding ID: SUPPLY-P1-001 - No SBOM artifact generated or bound to the release commit

- Severity: P1
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `package.json` devDependencies include `@cyclonedx/cyclonedx-npm` (SBOM tool)
  - No `sbom*.json`/CycloneDX artifact tracked under the repo; no SBOM step in `.github/workflows/ci-foundation.yml`
- What is happening: The tooling exists but is never invoked for a release, so there is no component inventory for 59e12b9.
- Why it matters: Vulnerability response ("are we affected by CVE-X?") requires a per-release component list.
- User / business impact: Slow incident response.
- Security / privacy / reliability impact: Supply-chain traceability gap.
- Recommended fix: Generate CycloneDX SBOM in CI/release, bind it to the commit, and retain it as an artifact.
- Suggested validation: SBOM artifact exists for the tagged commit and validates.
- Owner suggestion: Release engineer
- Effort estimate: S
- Dependencies: CI-P3-001
- Status: open

### Finding ID: SUPPLY-P2-001 - License and vulnerability enforcement is host-only, not merge-gating

- Severity: P2
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `scripts/assurance/assurance.sh` lines 95–112, 117 — OSV scan, `npm audit --omit=dev`, license assurance
  - `.github/workflows/ci-foundation.yml` — none of these steps
- What is happening: License violations/failed audits are discovered after merge, on a schedule.
- Why it matters: A disallowed license or high-severity CVE can enter `main` and ship before the daily lane flags it.
- User / business impact: Legal/security exposure.
- Security / privacy / reliability impact: Supply-chain.
- Recommended fix: Run a pinned OSV/audit + license check in CI on PRs touching the lockfile.
- Suggested validation: A planted disallowed-license dep fails PR CI.
- Owner suggestion: CI/legal
- Effort estimate: M
- Dependencies: CI-P2-001
- Status: open

### Finding ID: SUPPLY-P2-002 - Install scripts are allowlisted for several dependencies without provenance checks

- Severity: P2
- Confidence: Medium
- Area: SUPPLY
- Evidence:
  - `package.json` `allowScripts` — esbuild, protobufjs, puppeteer, unrs-resolver enabled
  - No `--ignore-scripts` alternative or provenance/attestation verification documented
- What is happening: Postinstall scripts run for these packages during `npm ci`.
- Why it matters: Install scripts are a common supply-chain execution vector.
- User / business impact: Low likelihood, high impact.
- Security / privacy / reliability impact: Build-time code execution.
- Recommended fix: Document why each script is required; verify provenance (`npm audit signatures`) or replace where possible.
- Suggested validation: `npm audit signatures` passes; allowlist reviewed per release.
- Owner suggestion: Build engineer
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: SUPPLY-P3-001 - Dependabot is configured but ungrouped for security updates

- Severity: P3
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `.github/dependabot.yml` — weekly, `open-pull-requests-limit: 5`, groups by dependency-type only; no `security` update grouping/priority
- What is happening: Security and routine updates share the same cadence/limit.
- Why it matters: A security update can be delayed behind routine dependency PRs.
- User / business impact: Minor.
- Security / privacy / reliability impact: Patch latency.
- Recommended fix: Add a security-updates grouping and prioritize/auto-merge low-risk security PRs after CI.
- Suggested validation: A security advisory opens a prioritized PR.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: CI-P1-001
- Status: open

## Risks

- R-SUPPLY-1: No per-release SBOM (P1).
- R-SUPPLY-2: Host-only vuln/license enforcement (P2).
- R-SUPPLY-3: Install-script execution (P2).

## Recommendations

1. Generate+bind SBOM.
2. Move vuln/license checks into CI.
3. Document/verify install-script allowlist.

## Quick Wins

- Add CycloneDX to a release workflow (S).
- Add OSV step to CI (S).

## Hardening Backlog

- Sigstore/npm provenance attestation for build outputs.

## Suggested Tests

- CI SBOM validation; license-gate negative test.

## Suggested Documentation Updates

- `SECURITY.md`: reference the SBOM and advisory process.

## Open Questions

- Are the `evidence/phase2/.../osv-*.json` scans current enough to substitute for a per-PR scan? (`Unknown` — they are historical.)

## Appendix

- Secret sweep: no live secrets found in tracked files; fixtures only (`bundle-secret-gate.mjs`, `check-web-bundle.mjs`, `repomix-output*.xml`).
