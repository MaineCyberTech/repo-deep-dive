## Summary

Closes the testing / final-release gaps for patch set **PS-010** of audit run
`20261003-0018-main-7bac320` (repo-deep-dive @ `7bac320`; worktree `6cada03`).

- **TEST-P3-004** — add a stdlib `unittest` suite under `tests/` covering the
  parsing (`lib_findings`), inventory (`repo_inventory`), and deterministic-check
  (`deterministic_checks`) logic that the smoke harness only exercised indirectly.
- **FINAL-P2-001** — add `.github/workflows/pack-tests.yml`, which runs the unit
  tests plus `tools/self_test.sh` and **archives the self-test log as a build
  artifact per commit** (`self-test-log-<sha>`). The log is real CI output, not an
  assertion.
- **FINAL-P3-002** — bind archived-run verdicts/statuses to the commits they were
  generated at in `runs/INDEX.md`, and state that later tooling commits do not
  inherit those statuses.
- Supporting fix: `tools/*.py` invoked as `./tools/*.py` by `self_test.sh` were
  tracked as `100644`, so the harness failed on a clean Linux checkout
  (`Permission denied`) — including at the audited SHA `6cada03`. The exec bit is
  now set on those eight files, which is required for FINAL-P2-001 to produce a
  real PASS.

## Findings covered

| Finding | Severity | Change |
|---|---|---|
| TEST-P3-004 | P3 | `tests/` unit suite (31 tests) |
| FINAL-P2-001 | P2 | `pack-tests.yml` runs + archives the self-test log; exec bits fixed |
| FINAL-P3-002 | P3 | `runs/INDEX.md` archive-to-commit binding |

Patch set: `PS-010 — Verification and tests` (files: `tests/`, `.github/workflows/`, `runs/INDEX.md`). Disjoint from PS-003 (`deep-dive-deterministic.yml`) and PS-004 (`audit.yml`); this PR adds a new workflow file only.

## Verification Performed

All commands were run on a **native Linux checkout** (WSL2 Ubuntu 24.04, Python 3.12.3) of commit `bfbb0e0`. Raw output and exit codes: `runs/20261003-0018-main-7bac320/remediation/PS-010/verify.log` (audit run copy).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m unittest discover -s tests -v` | WSL Ubuntu 24.04 | 0 | 31 tests, `OK` |
| `bash tools/lint_pack.sh` | WSL Ubuntu 24.04 | 0 | `RESULT: PASS` (digest current, runs index consistent) |
| `bash tools/self_test.sh` | WSL Ubuntu 24.04 | 0 | `RESULT: PASS` |
| `actionlint -no-color .github/workflows/pack-tests.yml` | actionlint 1.7.12 | 0 | no diagnostics |

Honest note: at the audited SHA `6cada03`, `bash tools/self_test.sh` fails with
`./tools/collect_findings.py: Permission denied` because the Python tools carry no
exec bit on a clean Linux checkout. The audit could not run the harness; this PR
fixes that so a genuine PASS is now reproducible and archived by CI.

## Risk / rollback

- **Risk:** low. Mode-only changes to existing tools; new tests; a new CI workflow.
  No production code, no secrets.
- **Rollback:** revert the PR (or delete the branch). No data or config migration.

## Review checklist

- [ ] `tests/` covers the parsing/inventory/deterministic paths claimed by TEST-P3-004.
- [ ] `pack-tests.yml` uses `set -o pipefail` and uploads the log even on failure.
- [ ] Exec-bit fix is mode-only (`git diff --summary` shows no content change).
- [ ] `runs/INDEX.md` binding wording matches the audit finding FINAL-P3-002.
- [ ] No secrets in the diff; scope stays within PS-010 files plus the required tools/ mode fix.
