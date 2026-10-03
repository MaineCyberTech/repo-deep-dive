# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-005** closes the CI/test/hygiene documentation drift reported against run
`20261003-0018-fix-trust-root-87532ec`.

On the base commit several parts of this finding were already fixed by earlier reconciliation work
(the `163 tests` claims were removed from `docs/GITHUB_CI.md` and
`docs/security/BRANCH_PROTECTION.md`, and the Dependabot cadence was corrected to the real cron,
with `tests/phase10/test_ci_doc_drift.py` guarding workflow inventory + cadence). This PR closes
the **residual** drift:

- `docs/CURRENT_STATE.md` still hardcoded `197 tests OK` in the C6 live-verification bullet — a
  number that is stale as the suite grows.
- `docs/GITHUB_CI.md` and `docs/security/BRANCH_PROTECTION.md` did not state where the
  authoritative per-run suite size comes from, inviting a future editor to re-hardcode it.
- The existing drift guard did not prevent a test count from being frozen back into the
  summary/governance docs.

The docs now point at the per-run CI job log/job summary instead of a frozen number, and the drift
guard fails if a hardcoded count is reintroduced.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-005` — close CI/test hygiene documentation gaps
- Repo / base: `falcon-edge` @ `origin/main` (`af6f83a`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `TEST-P2-001` | P2 | open -> fixed | Removed the last hardcoded suite count (`CURRENT_STATE.md`); docs now cite the authoritative per-run CI log/summary. |
| `HYG-P2-001` | P2 | open -> fixed | Summary-doc drift closed: no hardcoded test count in the three authoritative docs; `test_ci_doc_drift.py` guards against reintroduction. |
| `CI-P3-001` | P3 | open -> fixed | Documented cadence (daily `23 5 * * *`) matches `dependabot-merge.yml`; the drift guard asserts the cron string appears in `GITHUB_CI.md`. |

## Changes

| File | What changed |
|---|---|
| `docs/CURRENT_STATE.md` | Replace `197 tests OK` with "the full test suite passed", pointing at the CI run/job log for the size (TEST-P2-001). |
| `docs/GITHUB_CI.md` | State explicitly that the suite size is **not hardcoded**: each run prints `Ran N tests` in the job log and the 3.12 coverage table is in the job summary (TEST-P2-001/HYG-P2-001). |
| `docs/security/BRANCH_PROTECTION.md` | Note that the suite size is reported per run, not hardcoded, and point at the documented required-check contexts under **Target settings**. |
| `tests/phase10/test_ci_doc_drift.py` | New `test_docs_do_not_hardcode_test_count`: fail if `GITHUB_CI.md`, `BRANCH_PROTECTION.md` or `CURRENT_STATE.md` contains a `\d+ tests` claim. |

No workflows, application code, dependencies, or secrets changed.

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive` of the committed branch; raw output and
exit codes in `remediation/PS-005/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2` | edge-builder VM (pytest 7.4.4) | 0 (73 passed) | `remediation/PS-005/verify.log` |
| `python3 -m pytest -q tests/phase10/test_ci_doc_drift.py` | edge-builder VM (pytest 7.4.4) | 0 (3 passed) | `remediation/PS-005/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-005/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-005/verify.log` |

- Secret scan (gitleaks 8.30.1): **pass** — "no leaks found".
- Scope check: **pass** — only the three patch-set docs plus the docs-drift guard test changed.

The patch-plan verification is "counts match CI job summary; cadence matches cron". Counts are no
longer hardcoded anywhere in the authoritative docs and are taken from the per-run CI output;
`tests/phase10/test_ci_doc_drift.py` asserts the documented cadence equals the workflow cron.

## Evidence bundle

- `remediation/PS-005/diff.patch` — SHA-256 `e0f1408b444fe3d396baa7ff4be2cf8dad0929ffa7a33aa736af1d74a4c7decd`
- `remediation/PS-005/manifest.json`
- `remediation/PS-005/verify.log`

## Risk and rollback

- Risk: **low**. Documentation plus one additive drift-guard test; no runtime, workflow, or
  dependency behavior changes.
- Rollback: `git revert f2dbd1d` restores the prior wording and removes the guard test.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md`: "counts match CI job summary; cadence matches cron" — met by removing the
hardcoded counts (docs defer to the CI run) and by the `test_ci_doc_drift.py` cadence/count guards,
all green in `verify.log`.
