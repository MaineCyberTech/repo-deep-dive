# Testing, Quality, and Release Confidence Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: TEST
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/09_testing_quality_release_confidence.md
- Scope limitations: `node_modules` absent, so the suite was **not executed**; test inventory/counts are static. No CI to observe results.

## Scope

Reviewed Vitest configuration, all five test files, package test scripts, and the testing dependencies. Assessed coverage of the game loop, persistence, UI, and E2E. Not reviewed: actual coverage output (not runnable here).

## Evidence Reviewed

- `vitest.config.ts`, `package.json` (scripts/deps)
- `lib/generation/generation.test.ts` (344 lines), `lib/actions/care.test.ts` (209), `lib/locations/adventure.test.ts` (128), `lib/progression/lifecycle.test.ts` (116), `data/items.test.ts` (99)
- `@testing-library/react`, `jsdom`, `@playwright/test` in `package.json`
- `docs/buddy/reports/phases/*` (claims "109/109 tests pass")

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `Select-String '\bit\('` | command | test count | 109 matches — supports the "109 tests" claim |
| test file listing | static | coverage map | 5 files, all `lib/`/`data/` |
| grep `testing-library` imports | command | UI test presence | 0 imports |
| grep `playwright` config | command | E2E presence | no `playwright.config.*`, no e2e dir |
| `vitest.config.ts` | config | setup | `setupFiles: []`, no coverage |
| `npm test` | command | execution | **not run** (no `node_modules`) |

## Executive Summary

The unit-test layer is genuinely good for a project this size: **109 test cases across 5 files** covering deterministic generation, RNG/hash determinism, rarity weights, care actions, offline decay, adventure/loot with fixed seeds, lifecycle math, and catalogue integrity. The claim "109/109 tests pass" is **supported by count** but **not reproducible in this audit environment** (no dependencies installed). The significant gaps are systemic rather than unit-level: **no test runs in CI**, **no component/UI tests** despite `@testing-library/react` being installed, **no E2E tests** despite `@playwright/test`, **zero tests for the persistence layer** (IndexedDB, save migration, import/export), and **no coverage thresholds**. Because the persistence and UI-integration layers are exactly where the P1 bugs live (ARCH-P1-002, DATA-P1-001/002), the current suite gives a false sense of release confidence.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Runner | `vitest.config.ts` | unit tests | Implemented | Low | jsdom, globals |
| Generation tests | `generation.test.ts` | determinism | Strong | Low | 38-ish cases |
| Care tests | `care.test.ts` | care loop | Strong | Low | 30-ish cases |
| Adventure tests | `adventure.test.ts` | loot/adventure | Strong | Low | fixed seeds |
| Lifecycle tests | `lifecycle.test.ts` | progression | Strong | Low | pure functions |
| Items tests | `items.test.ts` | catalogue | Good | Low | referential checks |
| Storage tests | (none) | persistence | Absent | High | P1 bugs here |
| Component tests | (none) | UI | Absent | High | RTL installed |
| E2E tests | (none) | flows | Absent | Medium | Playwright installed |
| Coverage | (none) | thresholds | Absent | Medium | no config |
| CI execution | (none) | automation | Absent | High | see CI |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Unit tests (engines) | 4 | 109 cases | — | keep |
| Unit tests (persistence) | 0 | none | critical | add |
| Component tests | 0 | RTL unused | none | add |
| E2E tests | 0 | Playwright unused | none | add |
| Coverage thresholds | 0 | none | none | add |
| Test data/fixtures | 2 | inline helpers | duplicated | extract |
| CI test execution | 0 | no workflows | none | add CI |
| Flake/performance | 1 | fast pure tests | no timing | — |

## Detailed Review

### Item: Persistence untested
- Evidence: no test imports `lib/storage/indexeddb.ts` or `autosave.ts`; `jsdom` lacks a default IndexedDB (needs `fake-indexeddb`).
- Risks: the save version bug (DATA-P1-001) and import validation gap (SEC-P2-001) are untested and would regress silently.

### Item: UI untested
- Evidence: no `*.test.tsx`; `@testing-library/react` installed.
- Risks: the store/component desync (ARCH-P1-002) is invisible to the current suite.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| TEST-001 | UI/component testing | `package.json` | none | RTL unused | P2 | add RTL tests |
| TEST-002 | Persistence testing | storage files | none | no coverage | P2 | add fake-indexeddb tests |
| TEST-003 | Coverage/quality gate | config | none | no thresholds | P3 | add coverage |
| TEST-004 | Test execution in CI | no workflows | manual | no gate | P1 | see CI-P1-001 |

## Findings

### Finding ID: TEST-P2-001 - No component/UI tests despite React Testing Library being installed

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `package.json` — `@testing-library/react`, `jsdom` devDependencies
  - grep `@testing-library` in `*.test.*` — 0 matches; no `*.test.tsx`
  - `components/device/MainDevice.tsx`, `AdventureScreen.tsx` — untested UI logic
- What is happening: All 109 tests are pure-function tests; no component renders.
- Why it matters: The known store/component state divergence (ARCH-P1-002) and hatch/adventure flows have no regression protection.
- User / business impact: UI regressions ship undetected.
- Security / privacy / reliability impact: Reliability.
- Recommended fix: Add RTL tests for `MainDevice` (care action updates display), `AdventureScreen` (result applies to store), `HatchFlow` (nickname length), and `StatBars` (ARIA values).
- Suggested validation: `npm test` includes new `*.test.tsx` and passes.
- Owner suggestion: frontend
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: TEST-P2-002 - Persistence layer (IndexedDB, save migration, import/export) is untested

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - No test file imports `lib/storage/indexeddb.ts` or `lib/storage/autosave.ts`
  - `vitest.config.ts` — `setupFiles: []`; `jsdom` provides no IndexedDB by default
  - `docs` — no storage test report
- What is happening: The save/load/version/import code paths lack tests.
- Why it matters: DATA-P1-001 (version downgrade), DATA-P1-002 (no validation), and SEC-P2-001 (unvalidated import) can regress unnoticed.
- User / business impact: Silent data loss/corruption risk.
- Security / privacy / reliability impact: Reliability/integrity.
- Recommended fix: Add `fake-indexeddb` and tests for save→load round-trip, version migration, malformed import rejection, and guestId persistence.
- Suggested validation: New storage tests pass; cover both v1 and v2 fixtures.
- Owner suggestion: frontend
- Effort estimate: M
- Dependencies: DATA-P1-001/002
- Status: open

### Finding ID: TEST-P3-001 - No coverage configuration or thresholds, and test setup is empty

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `vitest.config.ts` — `setupFiles: []`, no `coverage` block
  - `package.json` — no `test:coverage` script
  - `@testing-library/react` installed but no setup file registers matchers
- What is happening: There is no measured coverage and no minimum bar.
- Why it matters: Test scope can silently shrink; the installed RTL cannot be used without a setup file.
- User / business impact: Lower confidence over time.
- Security / privacy / reliability impact: Process quality.
- Recommended fix: Add `@vitest/coverage-v8`, a `test:coverage` script, thresholds (e.g., 80% lines for `lib/`), and a `vitest.setup.ts` importing `@testing-library/jest-dom`.
- Suggested validation: `npm run test:coverage` enforces thresholds.
- Owner suggestion: frontend
- Effort estimate: S
- Dependencies: TEST-P2-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| P1 bugs not covered | P2 | High | High | TEST-P2-001/002 | add UI+storage tests |
| No automated test gate | P1 | High | High | no CI | CI-P1-001 |
| No coverage visibility | P3 | Medium | Low | config | coverage thresholds |

## Recommendations

### Immediate / Release Blocking
- Run the existing suite in CI (CI-P1-001).

### This Week
- Add storage tests (fake-indexeddb) and the first RTL component tests.

### This Month
- Add coverage thresholds and a Playwright smoke test for hatch→care→adventure.

### Later / Platform Evolution
- Add visual regression and accessibility (axe) tests.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `vitest.setup.ts` + jest-dom | enables RTL | new setup, `vitest.config.ts` | RTL test |
| fake-indexeddb storage tests | covers P1 save bugs | new test | pass |
| coverage script | visibility | `package.json`, config | report |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Storage tests | P2 | frontend | M | DATA fixes |
| RTL component tests | P2 | frontend | M | setup |
| Coverage thresholds | P3 | frontend | S | none |
| Playwright smoke E2E | P3 | frontend | M | CI |

## Suggested Tests

- Unit: save version + migration fixtures; import rejection.
- Component: care action updates LCD; adventure updates device; nickname cap.
- E2E: hatch → care → adventure → reload persists.
- Accessibility: axe on main screens.

## Suggested Documentation Updates

- `docs/testing.md` with how to run tests and add coverage.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Were tests passing at HEAD? | confidence | CI log or local run |
| Is Playwright intended? | E2E plan | decision |

## Appendix

- Claim sample: "109/109 tests pass" (phase-05/06/07 reports) → **supported by count, not reproduced** (no `node_modules`).
- Claim sample: "Build succeeded / TypeScript clean" (phase-01) → **not reproducible** at audit time.
