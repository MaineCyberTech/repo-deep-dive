# Testing, Quality, and Release Confidence

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: TEST
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/09_testing_quality_release_confidence.md
- Scope limitations: read-only; `self_test.sh` not executed (bash availability on Windows unknown); `inventory.json.tests.files = 0`.

## Scope

The pack's validation strategy: `tools/self_test.sh` (end-to-end), `tools/lint_pack.sh` (pack lint), `tools/check_run.sh` (run gate), archived-run fixtures, and CI. No unit test framework exists.

## Evidence Reviewed

- `tools/self_test.sh`, `tools/lint_pack.sh`, `tools/check_run.sh`
- `.github/workflows/deep-dive-deterministic.yml`, `ci/audit.yml`
- `inventory.json` — `tests.files: 0`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `inventory.json` tests | artifact | test presence | 0 test files |
| `.github` tree listing | command | CI coverage | only deterministic workflow; no lint/test job |
| `self_test.sh` read | code | coverage | exercises tools, not unit logic |

## Executive Summary

A reasonable smoke harness exists (`self_test.sh`) and pack lint is thorough, but nothing runs them automatically: the only wired workflow is a scheduled org scan, and `ci/audit.yml` (which does lint/validate/score) is unwired. Schema checks in the self-test are shallow (types unchecked). There are no unit tests for the parsing/inventory logic. Release confidence therefore rests on manual execution.

## Inventory

| Test capability | Path | Runs in CI | Coverage |
|---|---|---|---|
| End-to-end smoke | `tools/self_test.sh` | No | toolchain happy path |
| Pack lint | `tools/lint_pack.sh` | No (only in `ci/audit.yml`, unwired) | versions, structure, digest |
| Run gate | `tools/check_run.sh` | No | finals, IDs, statuses |
| Unit tests | none | No | — |
| Archived fixtures | `runs/*/` | via self_test | 2 runs |

## Findings

### Finding ID: TEST-P1-001 - No CI job runs the pack's own lint/self-test or authorizes PRs

- Severity: P1
- Confidence: High
- Area: TEST
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` — only scheduled/org scan; no `lint_pack.sh`/`self_test.sh` step
  - `ci/audit.yml` — contains lint/validate/P0 gate but is at `ci/` not `.github/workflows/` (see CI-P1-001)
  - `tools/lint_pack.sh`, `tools/self_test.sh` — runnable but not invoked by any wired workflow
- What is happening: Commits and PRs are not validated by the pack's own checks.
- Why it matters: `README.md` says a run is complete only when `check_run.sh` prints PASS and `CONTRIBUTING.md` requires lint/self-test — none are enforced.
- User / business impact: Regressions (e.g. DATA-P1-001/002) can merge unnoticed.
- Security / privacy / reliability impact: No automated quality gate.
- Recommended fix: Add a `.github/workflows/pack-ci.yml` running `lint_pack.sh` + `self_test.sh` on `pull_request` and `push`.
- Suggested validation: A PR that breaks the schema fails the new workflow.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: TEST-P2-002 - The smoke harness is bash-only and not exercised on the maintainer's platform

- Severity: P2
- Confidence: Medium
- Area: TEST
- Evidence:
  - `tools/self_test.sh`, `tools/lint_pack.sh`, `tools/check_run.sh` — `#!/usr/bin/env bash`
  - `tools/run_toolchain.py` lines 65-76 — soft-skips the check when no `bash`
  - environment: Windows maintainer host; no evidence of a Linux run at 6cada03
- What is happening: The only automated tests require bash; on Windows they may not run.
- Why it matters: The new Python tools and workflow are not demonstrably tested.
- User / business impact: "PASS" claims are unverified on the authoring platform.
- Security / privacy / reliability impact: Test gaps.
- Recommended fix: Port core assertions to Python or run the suite in CI (Linux) on every push.
- Suggested validation: CI log shows `self_test.sh` PASS at the audited SHA.
- Owner suggestion: maintainer
- Effort estimate: M
- Dependencies: TEST-P1-001
- Status: open

### Finding ID: TEST-P2-003 - Self-test schema check omits type/contract validation

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `tools/self_test.sh` lines 75-83 — asserts required keys present and ID pattern only
  - `schemas/findings.schema.json` line 11 — `sourceReports` integer
  - `tools/collect_findings.py` line 53 — emits an array (DATA-P1-001)
- What is happening: The self-test claims "findings.schema.json conformance" without validating types, so the schema mismatch passes.
- Why it matters: A false-green quality signal.
- User / business impact: Contract drift persists.
- Security / privacy / reliability impact: Low-medium.
- Recommended fix: Use `jsonschema` validation (or a stdlib type check) in the self-test.
- Suggested validation: The current archived findings.json fails the new check until DATA-P1-001 is fixed.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: DATA-P1-001
- Status: open

### Finding ID: TEST-P3-004 - No unit tests for parsing, inventory, or deterministic logic

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `inventory.json` — `tests.files: 0`
  - `tools/lib_findings.py`, `tools/repo_inventory.py`, `tools/deterministic_checks.py` — no corresponding test files
- What is happening: Logic is covered only indirectly by the smoke harness.
- Why it matters: Edge cases (ID regex, en-dash, CRLF detection) are untested.
- User / business impact: Regressions in parsing silently change counts.
- Security / privacy / reliability impact: Low.
- Recommended fix: Add `tests/` with fixtures for `scan_report`, `counts`, and CRLF detection.
- Suggested validation: `pytest` (or stdlib `unittest`) green.
- Owner suggestion: maintainer
- Effort estimate: M
- Dependencies: TEST-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unvalidated changes merge | P1 | High | Medium | TEST-P1-001 | add PR CI |
| False schema conformance | P2 | High | Medium | TEST-P2-003 | type validation |

## Recommendations

### This Week
- Wire a PR workflow running lint + self-test.
- Add schema type validation.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `pack-ci.yml` | enforcement | `.github/workflows/` | failing PR blocks |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Unit test suite | P3 | maintainer | M | TEST-P1-001 |

## Suggested Tests

- `test_lib_findings.py`: full-format + table rows + en-dash.
- `test_repo_inventory.py`: stack/route detection fixtures.
- Schema round-trip.

## Suggested Documentation Updates

- Add a Testing section to CONTRIBUTING.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Has `self_test.sh` ever run at 6cada03? | validates new tools | CI/local log — `Unknown` |

## Appendix

No coverage tooling or reported coverage percentage exists.
