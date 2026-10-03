# Testing, Quality, and Release Confidence Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: TEST
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/09_testing_quality_release_confidence.md
- Scope limitations: tests executed on Windows (auditor platform), not the Linux CI/host. POSIX-only failures are recorded as platform-limited, not product defects.

## Scope

Reviewed the test suite (49 files under `tests/phase0..10`), the CI test execution, coverage reporting, negative tests, and the ledger claims. Executed the suite locally where safe.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `tests/**` (49 files) | Tests | Coverage of features | unittest discover |
| `.github/workflows/validate.yml` | CI | Matrix 3.12/3.13 | coverage informational |
| `ledgers/test_execution.csv`, `gate_ledger.csv` | Ledgers | Claimed results | 86/88 PASS |
| `docs/GITHUB_CI.md`, `CURRENT_STATE.md`, `BRANCH_PROTECTION.md` | Docs | Test-count claims | 163 vs 197 (stale) |
| HEAD commit message | Git | Flake admission | time-relative fixture |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python -m unittest discover` | Command | Reproduce suite | **253 tests**, 8 skipped; on Windows 80 fail/error (POSIX-only) |
| Failure classification | Command | Separate platform from real | 23× `os.uname`, openssl/`resource`, mode `0o666` |
| `download-failed != staged` | Command | Real-looking assertion | 3× update tests (Windows path) |
| Doc count compare | Static | Self-consistency | documented 163/197 ≠ 253 |

## Executive Summary

The suite is broad (253 tests, 49 files) and includes negative tests and state-machine boundaries, and CI runs it on Python 3.12 and 3.13 with lint/secret/contract gates. Weaknesses: documented test counts are stale and inconsistent (163/197 vs 253); coverage is informational only (no threshold); and the suite is not cross-platform, so a Windows auditor cannot reproduce the "all pass" claim (23 failures alone are `os.uname`, plus openssl/`resource`/mode-bit assumptions). The repo itself admits a flaky fixture at HEAD.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Unit/integration | `tests/phase0..10` | Feature tests | 253 tests | Low | POSIX-leaning |
| Negative tests | `tests/phase0/negative_tests.sh`, `phase1/negative_tests.sh` | Adversarial | Present | Low | not in unittest count |
| Contract routes | `tests/phase1/test_contract_routes.py` | Route conformance | Present | Low | good |
| Coverage | `validate.yml` | Informational | No threshold | Med | TEST-P3-001 |
| CI execution | `validate.yml` | 3.12 + 3.13 | Green claimed | Med | not reproducible on Windows |
| Flaky fixture | HEAD message | `tests/phase9` fleet-inventory | Self-admitted | Low | TEST-P3-002 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Unit tests | 4 | 253 tests | platform coupling | mark POSIX-only |
| Integration tests | 4 | phase2/3 | — | — |
| API tests | 4 | `test_contract_routes` | pagination | API-P2-001 |
| E2E | 3 | lab walkthroughs (not CI) | manual | keep |
| Component tests | N/A | no frontend | — | — |
| Visual regression | N/A | no UI | — | — |
| Accessibility | N/A | no UI | — | — |
| Contract tests | 4 | route tests | field drift | API-P2-002 |
| Migration tests | 1 | none | no migrations | DATA-P2-003 |
| Security tests | 4 | escalation/revocation tests | revoked-enroll gap | TEST-P2-002 |
| Load/failure tests | 3 | soak/queue | not in CI nightly | minor |
| Smoke tests | 4 | boot-smoke workflow | — | — |
| CI execution | 4 | 3.12/3.13 | Windows not covered | document |
| Flaky risks | 3 | HEAD admission | fixture | TEST-P3-002 |
| Coverage | 2 | informational report | no threshold | TEST-P3-001 |

## Detailed Review

### Item: Test execution reproduction

- Evidence: `python -m unittest discover -s tests -p "test_*.py"` → `Ran 253 tests ... failures=40, errors=40, skipped=8` on Windows 3.12.
- Interpretation: the claim "197 tests OK" (`CURRENT_STATE.md`) and "163 tests" (`GITHUB_CI.md`, `BRANCH_PROTECTION.md`) both understate the current suite; `253` is the count at this commit. The Windows failures are dominated by POSIX assumptions (`resource`, `os.uname`, mode bits, openssl), so the Linux CI result cannot be independently reproduced here.
- Risk: TEST-P2-001.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| TEST-001 | Unit | 253 tests | broad | — | — | — |
| TEST-002 | Integration | phase2/3 | present | — | — | — |
| TEST-003 | API | route tests | present | — | — | — |
| TEST-004 | E2E | walkthroughs | manual | not automated | P3 | optional |
| TEST-005 | Contract | route tests | present | response fields | P2 | add |
| TEST-006 | Migration | none | none | none | P2 | DATA |
| TEST-007 | Security | escalation/revocation | present | revoked-enroll | P2 | TEST-P2-002 |
| TEST-008 | CI execution | matrix | 2 versions | Windows | P3 | document |
| TEST-009 | Coverage | informational | no gate | threshold | P3 | TEST-P3-001 |
| TEST-010 | Flaky | HEAD message | fixture | time-relative | P3 | stabilize |

## Findings

### Finding ID: TEST-P2-001 - Test-count claims are stale and mutually inconsistent (163 vs 197 vs 253)

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `docs/GITHUB_CI.md` — "the full test suite (163 tests)"
  - `docs/security/BRANCH_PROTECTION.md` — "validate (163 tests on 3.12/3.13 ...)"
  - `docs/CURRENT_STATE.md` — "197 tests OK"
  - Executed at HEAD — `Ran 253 tests`
- What is happening: documented counts differ from each other and from the current suite.
- Why it matters: the shared verification rules require aggregates to reconcile with their source; stale counts undermine trust in the release claims.
- User / business impact: reviewers cannot tell how much coverage "all pass" represents.
- Security / privacy / reliability impact: low (credibility).
- Recommended fix: derive the count in CI (already prints it) and reference the artifact instead of hardcoding numbers; update the docs.
- Suggested validation: CI job summary already emits the count; link it from the docs.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: TEST-P2-002 - No regression test that re-enrollment of a REVOKED/RETIRED sensor is refused

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `tests/phase2/test_service_integration.py` — revocation tests cover sensor routes and ingest, not enrollment
  - `src/falcon_control/service.py` — `h_enroll` has no lifecycle guard (SEC-P1-001)
- What is happening: the revocation control has no enrollment-path regression test, so SEC-P1-001 passed the suite.
- Why it matters: the exact gap that matters most lacks a guard.
- User / business impact: regression risk after fix.
- Security / privacy / reliability impact: security control not test-protected.
- Recommended fix: add tests that enrolling a REVOKED and a RETIRED sensor returns 403/409 and leaves the state unchanged.
- Suggested validation: the new test fails on the current code.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: SEC-P1-001 fix
- Status: open

### Finding ID: TEST-P3-001 - Coverage is reported informationally with no threshold gate

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `.github/workflows/validate.yml` — `coverage run ...` then `coverage report` into `$GITHUB_STEP_SUMMARY`; no `--fail-under`
- What is happening: coverage never blocks a PR.
- Why it matters: coverage can silently regress; critical modules (`service.py`, `runner.py`) have no enforced floor.
- User / business impact: gradual loss of release confidence.
- Security / privacy / reliability impact: low.
- Recommended fix: add `coverage report --fail-under=<N>` (start at the current value) scoped to `src/`.
- Suggested validation: lower coverage in a test branch and assert CI fails.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: TEST-P3-002 - HEAD explicitly lands a known-flaky time-relative test fixture

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - git log `87532ec` — "test: make the fleet-inventory 'changes' fixture time-relative (unrelated pre-existing flake)"
  - `tests/phase9/test_fleet_inventory.py`
- What is happening: a test was changed to be time-relative to deflake it rather than made deterministic.
- Why it matters: time-relative fixtures can still flake around boundaries; the admission signals known instability.
- User / business impact: intermittent CI red.
- Security / privacy / reliability impact: low.
- Recommended fix: use an injectable clock / frozen time in `changes`.
- Suggested validation: run the test with a mocked clock at boundaries.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale test counts | P2 | High | Credibility | docs vs run | derive in CI |
| Untested revocation-reset | P2 | High | Security regression | `test_service_integration` | TEST-P2-002 |
| Ungated coverage | P3 | Medium | Slow decay | `validate.yml` | threshold |
| Flaky fixture | P3 | Medium | CI noise | HEAD | injectable clock |

## Recommendations

### Immediate / Release Blocking
Add the revoked-enroll regression test alongside SEC-P1-001.

### This Week
Fix documented counts; add coverage floor.

### This Month
Stabilize time-relative fixtures.

### Later / Platform Evolution
Nightly soak/load job.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Reference CI count | removes stale numbers | `docs/GITHUB_CI.md` | reviewed |
| Add fail-under | prevents decay | `validate.yml` | CI fail |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Revoked-enroll test | P2 | build-agent | S | SEC-P1-001 |
| Coverage gate | P3 | build-agent | S | none |
| Cross-platform guards | P3 | build-agent | S | none |

## Suggested Tests

- Enroll-after-revoke/retire (negative).
- Pagination >500 sensors.
- Idempotency TTL prune boundary.
- Queue expiry without new enqueue.

## Suggested Documentation Updates

- `docs/GITHUB_CI.md`: replace hardcoded test counts with a link to the job summary; note the suite is POSIX-targeted.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why does CURRENT_STATE say 197? | provenance | commit history |
| Is Windows a supported dev platform? | platform fixes | owner decision |

## Appendix

Executed command and result:
```
python -m unittest discover -s tests -p "test_*.py"
Ran 253 tests in 91.655s
FAILED (failures=40, errors=40, skipped=8)
```
Failure classes: 23× `AttributeError: module 'os' has no attribute 'uname'`; `ModuleNotFoundError: No module named 'resource'`; `PermissionError [WinError 32]`; mode assertion `'0o666' != '0o600'`; 3× update-path assertions (Windows path/TLS). All are platform-coupled, not product defects. Not reproduced on Linux in this run.
