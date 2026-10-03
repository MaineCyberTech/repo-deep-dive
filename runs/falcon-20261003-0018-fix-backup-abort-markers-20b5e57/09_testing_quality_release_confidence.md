# Testing, Quality, and Release Confidence Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: TEST
- Output path: docs/audits/{name}/{run}/09_testing_quality_release_confidence.md
- Scope limitations: no bash host execution of the full gate in this audit; live suites skipped.

## Scope

Reviewed the offline shell suite (`automation/validation/tests/*.sh`), the static gate (`ci/validate.py`), the test/gate ledgers, and whether the new abort-marker test is wired. Did not run the gate (per run instructions).

## Evidence Reviewed

- `automation/validation/tests/*.sh` (32 suites, incl. `abort_marker_test.sh`).
- `ci/validate.py` `check_shell_tests` (auto-discovers `tests/*.sh`) and `CHECKS`.
- `ledgers/test_execution.csv`, `ledgers/gate_ledger.csv`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `ci/validate.py` check_shell_tests | Source | Suite runner | globs `tests/*.sh`; skips `test-requires` |
| `abort_marker_test.sh` | Test | New regression guard | no `test-requires` → runs in gate |
| `test_execution.csv` | Ledger | Test provenance | contains `/home/user/falcon-build` command paths |

## Executive Summary

The test strategy is strong for a lab: 32 offline, stubbed shell suites run in CI and the new abort-marker test is auto-discovered, so the fix is guarded. Two confidence gaps remain: the test ledger is a historical lab-host record that references out-of-repo trees, and there is no end-to-end backup/offsite/restore test in the standard gate. The gate is long and Linux/bash-dependent, so a short bounded off-host run is not achievable.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Offline suites | `automation/validation/tests/*.sh` | regression | Functional | Low | 32 |
| Abort test | `abort_marker_test.sh` | marker regression | Functional | Low | wired |
| Gate | `ci/validate.py` | static | Functional | Medium | 13 checks |
| Test ledger | `ledgers/test_execution.csv` | provenance | Historical | Medium | host paths |
| Gate ledger | `ledgers/gate_ledger.csv` | gates | Maintained | Low | 102 rows |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Unit | 3 | shell suites | — | — |
| Integration | 3 | offline stubs | no live | — |
| E2E | 2 | none for backup | add | TEST-P2-001 |
| CI tests | 4 | validate.py | — | — |
| Test data | 3 | fixtures | — | — |
| Traceability | 2 | ledgers | host paths | TEST-P1-001 |

## Findings

### Finding ID: TEST-P1-001 - Repo-local test ledger points at an out-of-repo, pre-rename lab tree

- Severity: P1
- Confidence: High
- Area: TEST
- Evidence:
  - `ledgers/test_execution.csv` — command cells reference `/home/user/falcon-build` and `/home/user/falcon-edge-build`, plus `/tmp/opencode/`
  - `ledgers/test_execution.csv` — historical rows from the lab host (`2026-09-22`)
- What is happening: The ledger records commands whose paths no longer resolve in a clone and reference a different repository layout.
- Why it matters: Test provenance cannot be reproduced or verified off-host.
- User / business impact: Weakened release confidence.
- Security / privacy / reliability impact: Provenance integrity.
- Recommended fix: Add a repo-relative command/procedure column (or a resolver) and mark historical rows explicitly; do not rewrite history.
- Suggested validation: A checker that flags absolute `/home/`/`/tmp/` paths in new ledger rows.
- Owner suggestion: build/QA
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: TEST-P1-002 - The full gate does not complete within a short bounded run and shell suites are not executable off a bash host

- Severity: P1
- Confidence: High
- Area: TEST
- Evidence:
  - `ci/validate.py` — full check set (13 checks incl. shell tests)
  - `automation/validation/tests/*.sh` — require bash/coreutils
  - Run instructions: `python3 ci/validate.py --only shell-tests` for subsets
- What is happening: There is no quick, portable smoke invocation; the full gate is long and bash-bound.
- Why it matters: Fast feedback and off-host validation suffer.
- User / business impact: Slower iteration; reviewers cannot cheaply reproduce.
- Security / privacy / reliability impact: Confidence gap.
- Recommended fix: Define a documented `--fast` subset and a container image for the gate.
- Suggested validation: `ci/validate.py --fast` completes in <60s on Linux.
- Owner suggestion: build/QA
- Effort estimate: M
- Dependencies: CI
- Status: open

### Finding ID: TEST-P2-001 - No backup/offsite/restore end-to-end test runs in the standard gate

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `automation/validation/tests/offsite_backup_reuse_test.sh`, `offsite_upload_delta_test.sh` — unit-level delta/reuse
  - `automation/validation/restore_rehearsal.sh` — live drill, not in the offline gate
  - `bootstrap/85-backup-job.sh` — no test drives the full snapshot→offsite→freshness path
- What is happening: The backup lifecycle is only tested in parts; the full chain requires the lab.
- Why it matters: The most consequential recovery path has the weakest automated coverage.
- User / business impact: Recovery regressions caught late.
- Security / privacy / reliability impact: Reliability.
- Recommended fix: Add a stubbed end-to-end test (fake OpenSearch snapshot API + fake object store) asserting freshness state and marker lifecycle.
- Suggested validation: New `tests/backup_e2e_test.sh` passes in the offline gate.
- Owner suggestion: build/QA
- Effort estimate: M
- Dependencies: ARCH-P1-002
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unreproducible provenance | P1 | High | Medium | test_execution.csv | TEST-P1-001 |
| Slow/opaque gate | P1 | Medium | Medium | validate.py | TEST-P1-002 |
| Recovery regression late | P2 | Medium | High | no e2e | TEST-P2-001 |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
- Add a `--fast` gate subset (TEST-P1-002).

### This Month
- Stubbed backup e2e test (TEST-P2-001).
- Repo-relative ledger provenance (TEST-P1-001).

### Later / Platform Evolution
- Gate container image.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Flag absolute paths in new ledger rows | Provenance hygiene | checker | runs clean |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Backup e2e | P2 | build/QA | M | — |

## Suggested Tests

- Backup lifecycle e2e (stubbed).
- Marker-failure regression (see ARCH-P1-002).

## Suggested Documentation Updates

- `docs/` — document the fast gate invocation.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the full gate currently pass? | Release confidence | CI log |

## Appendix
Not applicable.
