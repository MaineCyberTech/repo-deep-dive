# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-016** closes the repository-inventory finding from run
`20261003-0018-fix-trust-root-87532ec` (report `01_repository_inventory.md`).

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-016` — evidence retention / size policy
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)

Finding `INV-P2-001` ("900 raw evidence files committed with no retention or size policy")
was re-verified against current `origin/main`. A previous change had added an evidence size
*budget* (`ci/check_evidence_size.py`, wired into `ci/validate.sh`) and an archival policy in
`REPOSITORY.md`, but the checker is explicitly **advisory** ("always exit 0"). The finding's
required control — *"add a CI step that fails when `evidence/` exceeds the budget"* — was still
missing, so an over-budget tree printed `WARN` and the gate still reported `validation: ALL PASS`.
The finding therefore **still reproduces**.

This PR makes the budget gate **fail-closed** so over-budget evidence blocks CI until
completed-phase captures are archived (the policy already documented in `REPOSITORY.md`).

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `INV-P2-001` | P2 | open -> fixed (draft PR) | The evidence size budget now exits non-zero over budget and `ci/validate.sh` fails the gate; an over-budget tree yields `validation: FAILURES PRESENT` (exit 1). Retention/archive policy remains `REPOSITORY.md` + external archive path; raw evidence is never deleted. |

## Changes

| File | What changed |
|---|---|
| `ci/check_evidence_size.py` | Now **fail-closed**: returns `1` when `evidence/` exceeds 2,500 files / 50 MiB (was "advisory only, always exit 0"); over-budget line prints `FAIL` instead of `WARN`. Added a `--root DIR` option so the gate can be exercised against a fixture, and factored the walk into `measure()`. |
| `ci/validate.sh` | `== evidence size budget ==` now runs `python3 ci/check_evidence_size.py || rc=1`, so the budget failure propagates to the validator's exit code. |
| `REPOSITORY.md` | One-line policy fix: the budget now *fails the gate* past 2,500 files / 50 MiB (was "warns"), attributed to `INV-P2-001 / HYG-P2-003`. |
| `tests/phase10/test_evidence_budget_gate.py` (new) | Locks the fail-closed behaviour: under-budget passes, over-budget exits 1, and `ci/validate.sh` wires the check with `|| rc=1`. |

Scope note: the patch plan listed `evidence/`, `ci/validate.sh`. `ci/check_evidence_size.py`
is the size check the finding names; making it fail is the minimal change that closes the
finding (a shell re-implementation in `validate.sh` would duplicate it). No evidence data files
were changed.

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04.5, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive --format=tar.gz` of the committed branch
(the archive is git-initialised so `ci/validate.sh` exercises its `git ls-files` parse loop);
raw output and exit codes are in `remediation/PS-016/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| base check: over-budget tree on `origin/main` | edge-builder VM | `check_evidence_size`=0 / `validate.sh`=0 (`ALL PASS`) | `remediation/PS-016/verify.log` |
| `python3 ci/check_evidence_size.py` (under budget) | edge-builder VM | 0 (`PASS 950 files, 2.5 MiB`) | `remediation/PS-016/verify.log` |
| `shellcheck -S warning ci/validate.sh` | edge-builder VM | 0 | `remediation/PS-016/verify.log` |
| `python3 -m pytest -q tests/phase10/test_evidence_budget_gate.py` | edge-builder VM (pytest 7.4.4) | 0 (3 passed) | `remediation/PS-016/verify.log` |
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM (pytest 7.4.4) | 0 (129 passed) | `remediation/PS-016/verify.log` |
| `bash ci/validate.sh` (under budget) | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-016/verify.log` |
| functional check: inject 2,600 raw files, re-run gate | edge-builder VM | `check_evidence_size`=1 / `validate.sh`=1 (`FAILURES PRESENT`) | `remediation/PS-016/verify.log` |
| functional check: remove injected files, re-run gate | edge-builder VM | 0 (`PASS`) | `remediation/PS-016/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (`no leaks found`, ~6.65 MB) | `remediation/PS-016/verify.log` |

Base reproduction on the same VM (archive of `origin/main` `f5811d1`): with 3,550 evidence files
(over the 2,500 budget) the checker exited 0 and `ci/validate.sh` exited 0 with
`validation: ALL PASS`. On the patched tree the same injected over-budget tree makes the checker
exit 1 and `ci/validate.sh` exit 1 with `validation: FAILURES PRESENT`, and the restored
under-budget tree passes again. The new phase-10 test asserts the same behaviour directly.

- Secret scan: **pass** — "no leaks found" (6.65 MB scanned).
- Scope check: **pass** — `ci/validate.sh` (patch-set file), `ci/check_evidence_size.py` (the
  check named by the finding), `REPOSITORY.md` (one-line policy) and a Phase-10 regression test.
  No product code, API, schema, evidence payload or dependency changed.

## Evidence bundle

- `remediation/PS-016/diff.patch` — SHA-256 `829f29dc651fbfab799f40c0c97901010a5e1e13700111387ad211fece8139f6`
- `remediation/PS-016/manifest.json`
- `remediation/PS-016/verify.log`

## Risk and rollback

- Risk: **low**. The only behaviour change is that an evidence tree over 2,500 files / 50 MiB
  now fails `ci/validate.sh`. The current tree is ~950 files / 2.5 MiB, well under budget, so no
  gate changes state today. When the budget trips, the documented remedy is to archive
  completed-phase captures to `/srv/falcon/edge-evidence-archive/` (keeping the index + manifest);
  raw evidence is never deleted.
- Rollback: `git revert 52b825b` restores the advisory checker and validator invocation.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- **Budget values.** The 2,500 file / 50 MiB budget is unchanged from the prior change; if the
  owner wants a different threshold (per-gate retention, byte budget only), adjust the constants
  in `ci/check_evidence_size.py`.
- **External archive automation.** This PR only makes the in-repo gate fail. Automating the
  archive move to `/srv/falcon/edge-evidence-archive/` (with a sidecar manifest) is a separate
  ops/tooling follow-up, as the archive lives outside the repository.

## Definition of done (for this set)

From `patch_plan.md`: "evidence byte-budget gate". The functional check shows the gate now exits
1 when `evidence/` exceeds the budget and 0 when it is under budget; `ci/validate.sh` propagates
the failure. `bash ci/validate.sh` and `python3 -m pytest -q tests/phase2 tests/phase3` pass on
the committed branch.
