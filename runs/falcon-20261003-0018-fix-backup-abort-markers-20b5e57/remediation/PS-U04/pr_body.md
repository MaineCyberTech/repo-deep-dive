# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the one repo-local finding in catch-all patch set `PS-U04` — the split
ownership of the `event_time` field between the OpenSearch index template and the
Vector transforms, with no check at HEAD that they agree — by adding an offline,
static consistency check and wiring it into `ci/validate.py`. The finding's stated
fix is either single-source template generation **or** a CI check that validates
the Vector-derived document against the template; this PR takes the check path
(the lower-risk, no-deployment alternative) and records single-source generation
as the deferred residual.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U04` — Unassigned DATA findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u04-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `eee84c8ec4a69f5614a7b0b267231a14a1ff65f5`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P2-001` | P2 | open -> partially-fixed (verified at this commit, draft PR) | The template and the Vector transforms now have a gate that fails closed when they disagree. `check_event_time_consistency.py` asserts the template pins `event_time` as `date` and every Vector remap transform that assigns `.event_time` derives a timestamp (`parse_timestamp`/`now`, directly or transitively through a local variable); a string/number assignment, a template type drift, or an orphaned field fails. Wired as `ci/validate.py --only event-time-consistency`; the 31-suite gate is green at this commit (the new offline suite runs inside it). |

Statuses map to `partially-fixed` while the PR is a draft; the finding moves to
`verified-fixed` only after a human merges with green CI. The fixture negative
controls (below) show the check fails closed, not just that it passes on HEAD.

## Changes

| File | What changed |
|---|---|
| `automation/validation/check_event_time_consistency.py` | New offline static check. Reads `config/opensearch/falcon-eve-template.json` (`event_time` must be `date`) and every remap transform under `config/vector/`; resolves `.event_time` values transitively to a timestamp producer and fails on a non-timestamp assignment or a missing emitter. Exit 0/1/2. |
| `automation/validation/tests/event_time_consistency_test.sh` | New offline regression suite: positive fixture, plus negative controls (template type -> `keyword`; transform emits a string with `parse_timestamp` used elsewhere; field orphaned) and a wiring assertion against `ci/validate.py`. |
| `ci/validate.py` | Adds the `event-time-consistency` check (and its docstring entry) over `check_event_time_consistency.py`. |
| `docs/phase9/OPENSEARCH_TEMPLATE_EVENT_TIME_NOTE.md` | Replaces the stale "recorded here, not applied / event_time is the missing field" wording with the applied state (decision log 2026-10-01T19:37Z) and the new enforcement; the note is the field-ownership record. |

Scope: only the `event_time` contract check, its test, the gate wiring and the
note that documents it. No template mapping value, no Vector transform, no
consumer query, no dependency, and no deployed config was changed. The
`review-package/` snapshot was deliberately not touched (separate hygiene set).

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against the synced
worktree, driven by the job API (`tools/lab_runner.py`). Raw log:
`remediation/PS-U04/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 31/31 shell suites including `event_time_consistency_test.sh`; `PASS event_time template/Vector consistency` |
| `git ls-files -z \| xargs -0 chmod +x` | lab `ci-runner` | 0 | setup note: the tar-based lab sync drops the exec bit; tracked `*.sh` are restored +x before the gate (same as the other remediation runs) |
| `gitleaks stdin --redact --exit-code 1 < /tmp/psu04.diff` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `scanned ~17342 bytes (17.34 KB)`, `no leaks found` (the exact `base..HEAD` patch, generated on the audit host because the lab clone cannot read the packed base object) |

Negative controls (in `event_time_consistency_test.sh`, run by the gate above):
a template `event_time` type of `keyword` fails with `expected 'date'`; a
transform that assigns `.event_time = "2026-10-01T00:00:00Z"` fails with
`not a timestamp`; a transform that drops the `.event_time` assignment fails with
`no remap transform emits`. Each is asserted and the suite exits non-zero.

- Secret scan (gitleaks): **pass** — no leaks on the full diff.
- Scope check: **pass** — only the four patch-set files above.
- No fabricated evidence: every exit code above is from the recorded run; the
  one `chmod` setup step is disclosed rather than hidden.

## Evidence bundle

- `remediation/PS-U04/diff.patch` — SHA-256 `9BC40C3F05F6C586E8730FFE445768266FEF92736FF533DE5F04EA5BD413C467`
- `remediation/PS-U04/verify.log`
- `remediation/PS-U04/manifest.json`
- `remediation/PS-U04/pr_body.md`

## Risk and rollback

- Risk: **low**. The change is additive: a new read-only check, its offline
  suite, a gate registration and a doc correction. The check only reads the
  committed template/Vector YAML; it has no network, docker, credential or
  cluster dependency, so it cannot flake on lab state. If the check itself is
  wrong it fails closed and blocks CI, which is the intended direction for a
  mapping-drift guard.
- Residual risk: the check is a static approximation of VRL types (it follows
  local variables to a timestamp producer, not a full type inferencer). A
  contrived transform could still evade it; the live `mapping_drift_check.py`
  remains the runtime authority.
- Rollback: `git revert eee84c8ec4a69f5614a7b0b267231a14a1ff65f5`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ test/doc)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] The new check fails closed on all three negative controls
- [ ] Rollback is practical

## Open questions / deferred

1. **Single-source schema generation (deferred).** The finding's first option was
   to generate `falcon-eve-template.json` from one schema source so the two
   owners cannot diverge by construction. That is a template-pipeline change
   (who generates it, how it is reviewed and deployed) and is out of scope for
   this minimal fix; the static check is the finding's explicitly offered
   alternative. Recommend a follow-up design decision if the drift keeps
   recurring.
2. **Runtime authority unchanged.** `mapping_drift_check.py` still owns the
   live-index comparison; this PR does not run it in CI (it needs docker and
   credentials). Nothing here deletes, reindexes or re-maps data.
