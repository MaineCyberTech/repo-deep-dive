# 09 Testing, Quality & Release Confidence

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Test inventory, what CI actually gates, coverage enforcement, browser/device coverage, and the confidence that can be derived from the repository alone. Read-only.

## Evidence Reviewed

- `package.json` scripts, `vitest.config.ts`, `playwright.config.ts`
- `.github/workflows/ci-foundation.yml`
- `scripts/verify-all.sh`
- Test file inventory (138 files: `apps/realtime/src/__tests__`, `apps/web/**/__tests__`, `packages/*/src/__tests__`, `apps/web/e2e`)
- `AGENTS.md` tooling caveat; `evidence/audit-20260927/REMEDIATION.md` (verification claims)

## Verification Performed

- Enumerated test files (138) and e2e specs (3).
- Read CI: `npm run typecheck`, `lint`, `format:check`, `npm test`, explicit integration run, `npm run build`, compose config, bundle secret gate; separate `migrations` and `e2e` jobs.
- Attempted to run tests — `node_modules` absent, so **not reproducible in this audit environment**; relied on repository evidence.
- Confirmed coverage config exists but is not invoked in CI; no threshold set.

## Executive Summary

Test volume is high (138 test files) and CI gates a meaningful chain: typecheck, lint, format, unit tests, the realtime integration suite, a production build, compose validation and the bundle secret gate, plus Playwright e2e and a fresh-DB migration apply. The weaknesses are enforcement gaps rather than absent tests: no coverage thresholds or coverage artifacts, a Chromium-only e2e project despite a multi-browser support matrix, and the 16 SQL negative RLS suites excluded from CI. Local `verify-all.sh` also omits `format:check`, e2e, compose and any dependency audit, so "local green" is weaker than CI green.

## Inventory

| Suite | Location | Runs in CI | Runs locally |
|---|---|---|---|
| Unit/component (vitest) | `apps/**`, `packages/**` | yes (`npm test`) | yes |
| Realtime integration | `apps/realtime/src/__tests__/server.integration.test.ts` | yes (explicit) | yes |
| E2E (Playwright) | `apps/web/e2e` (3 specs) | yes (chromium only) | `npm run test:e2e` |
| SQL negative/RLS | `supabase/tests` (16) | no | manual |
| Coverage | configured, unused | no | no |

## Findings

### Finding ID: TEST-P2-001 - No coverage thresholds and coverage never runs in CI

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `vitest.config.ts` lines 18–20 — `coverage.reporter` set, no `thresholds`
  - `.github/workflows/ci-foundation.yml` — no `--coverage`
- What is happening: Coverage is collectable but not measured or enforced.
- Why it matters: There is no signal on untested critical paths (e.g. scoring, authz branches).
- User / business impact: Untested regressions reach release.
- Security / privacy / reliability impact: Unknown coverage of security-critical code.
- Recommended fix: Run coverage in CI, publish an artifact, and set ratcheting thresholds on critical packages (`game-core`, `realtime`).
- Suggested validation: CI fails when coverage drops below threshold.
- Owner suggestion: QA engineer
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: TEST-P2-002 - E2E matrix is Chromium-only despite a multi-browser product claim

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `playwright.config.ts` lines 51–56 — single `chromium` project
  - `README.md` line 46–52 — browser/touch validation claim (emulated viewports)
  - `docs/content/DEVICES_TARGET_MATRIX.md` referenced as the support matrix
- What is happening: Only Chromium is exercised; no Firefox/WebKit project.
- Why it matters: Layout/accessibility regressions specific to other engines are invisible.
- User / business impact: Player-facing breakage on non-Chromium browsers.
- Security / privacy / reliability impact: Reliability.
- Recommended fix: Add Firefox and WebKit projects at least for the mobile/a11y journeys, or explicitly bound the supported-browser claim.
- Suggested validation: CI runs the journeys in three engines.
- Owner suggestion: Web/QA engineer
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: TEST-P2-003 - SQL negative/RLS suites are not gated by any pipeline

- Severity: P2
- Confidence: High
- Area: TEST (see also DATA-P2-001)
- Evidence:
  - `AGENTS.md` line 16 — suites "not run in CI"
  - `.github/workflows/ci-foundation.yml` `migrations` job runs only the dry-run
- What is happening: The RLS correctness suites are manual.
- Why it matters: The most security-relevant tests do not protect releases.
- User / business impact: Silent tenant-isolation regressions.
- Security / privacy / reliability impact: Tenant data exposure risk.
- Recommended fix: Execute the suites in the CI migrations job.
- Suggested validation: Weakened policy causes CI failure.
- Owner suggestion: DB/CI engineer
- Effort estimate: M
- Dependencies: DATA-P2-001
- Status: open

### Finding ID: TEST-P3-001 - `test:unit` script resolves to a non-existent path

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `package.json` line 22 — `"test:unit": "npm run build:packages && vitest run packages/*/src/apps"`
  - No `packages/*/src/apps` directory exists (listing shows `packages/contracts/src/__tests__`, `game-core/src/__tests__`)
- What is happening: The glob matches nothing, so the script is a no-op/broken entry point.
- Why it matters: Contributors using it believe tests ran.
- User / business impact: False confidence during development.
- Security / privacy / reliability impact: None direct.
- Recommended fix: Point it at real paths (e.g. `vitest run packages apps/realtime`), or remove in favour of `npm test`.
- Suggested validation: `npm run test:unit` executes >0 tests.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: TEST-P3-002 - Local `verify-all.sh` is a weaker gate than CI, and audit could not reproduce tests

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `scripts/verify-all.sh` — build/typecheck/lint/test/test:integration/secret-scan only (no `format:check`, e2e, compose, audit)
  - `.github/workflows/ci-foundation.yml` adds `format:check`, e2e, compose config
  - Audit environment: `node_modules` absent → tests not executed
- What is happening: "verify-all is green" is commonly cited as the local bar but is a subset of CI; no captured test artifact is bound to this commit in the run folder.
- Why it matters: Reviewers may over-trust a partial local gate.
- User / business impact: Low.
- Security / privacy / reliability impact: None.
- Recommended fix: Align `verify-all.sh` with CI or document the delta; capture CI artifacts per commit.
- Suggested validation: Script and CI step lists match (or documented).
- Owner suggestion: CI engineer
- Effort estimate: S
- Dependencies: CI-P3-001
- Status: open

## Risks

- R-TEST-1: Un-gated RLS suites (P2).
- R-TEST-2: Single-engine browser coverage (P2).
- R-TEST-3: No coverage signal (P2).

## Recommendations

1. Gate SQL suites + coverage in CI.
2. Broaden e2e engines or bound the claim.
3. Fix `test:unit` and align local/CI gates.

## Quick Wins

- Fix `test:unit` (S). Add coverage artifact (S).

## Hardening Backlog

- Flake budget and deterministic e2e harness (existing `e2e-determinism-harness.mjs` can be extended).

## Suggested Tests

- CI coverage ratchet; Firefox/WebKit journeys; SQL suite job.

## Suggested Documentation Updates

- `README.md`/`CONTRIBUTING.md`: correct the local-vs-CI gate description.

## Open Questions

- What is the current pass count at this commit? (`Unknown` — not reproducible without deps; `evidence/audit-20260927` claims 870 unit / 135 integration at an earlier commit.)

## Appendix

- 3 e2e specs: `menu.mobile.spec.ts`, `shopPanel.a11y.spec.ts`, `spriteTextures.spec.ts`.
