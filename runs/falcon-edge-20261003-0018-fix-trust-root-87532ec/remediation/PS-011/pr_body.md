# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-011** closes the release-integrity / derived-artifact findings from run
`20261003-0018-fix-trust-root-87532ec` (audit reports `02_architecture_runtime_topology.md`,
`21_repo_hygiene_maintainability.md`, `01_repository_inventory.md`).

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-011`
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)
- Findings: `ARCH-P2-001`, `HYG-P2-002`, `INV-P3-001`

The findings were re-verified against current `origin/main` and **still reproduce**: the
`edge-control-plane.service` unit has no start-time guard against a dirty working tree, and
`ci/validate.sh` has no regeneration guard for `closeout/FINAL_RESPONSE.json`, the Grafana
dashboard, or the frozen audit mirror (`closeout/check_derived.py` does not exist).

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P2-001` | P2 | open -> fixed (draft PR) | The unit now refuses to start from a dirty `/home/user/falcon-edge-build` tree (`ExecStartPre` fail-closed guard); `/api/v1/healthz` continues to report `source_commit`/`source_dirty`. |
| `HYG-P2-002` | P2 | open -> fixed (draft PR) | `closeout/generate_final_response.py --check` binds `FINAL_RESPONSE.json` to `ledgers/gate_ledger.csv`; the dashboard and frozen audit mirror are pinned by SHA-256 in `closeout/derived_artifacts.json` via `closeout/check_derived.py`. Both are wired into `ci/validate.sh`. |
| `INV-P3-001` | P3 | open -> fixed (draft PR) | Same guard covers the generated/derived artifacts that previously had no `--check`: dashboard JSON and the committed audit mirror (frozen snapshot), in addition to the already-guarded models/schemas. |

## Changes

| File | What changed |
|---|---|
| `deploy/edge-control-plane.service` | New `ExecStartPre` that fails closed if `git status --porcelain` is non-empty in `/home/user/falcon-edge-build`; `--no-optional-locks` keeps the check read-only under `ProtectHome=read-only`. |
| `closeout/generate_final_response.py` | Refactored to a `compute()` helper and a `--check` mode that compares the committed `gate_counts` / `phase_gate_counts` with the gate ledger (exit 1 on drift). |
| `closeout/check_derived.py` (new) | Pins the artifacts that have no generator by content SHA-256 (CRLF-normalised) using `closeout/derived_artifacts.json`; a file or directory drift is a failure. |
| `closeout/derived_artifacts.json` (new) | The frozen manifest: Grafana dashboard digest and the recursive digest of the `20261002-0630-edge-f6f1610` audit mirror, `frozen_at_commit` = base. |
| `ci/validate.sh` | Adds `== closeout response sync ==` and `== derived artifact guards ==` to the fail-closed gate. |
| `tests/phase10/test_derived_artifact_guards.py` (new) | Locks the two guards (they pass on the committed tree) and the tree-digest helper's mutation detection. |

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04.5, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive --format=tar.gz` of the committed branch
(the archive is git-initialised so `ci/validate.sh` exercises its `git ls-files` parse loop);
raw output and exit codes are in `remediation/PS-011/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 closeout/generate_final_response.py --check` | edge-builder VM | 0 (`in sync`) | `remediation/PS-011/verify.log` |
| `python3 closeout/check_derived.py` | edge-builder VM | 0 (`all pinned artifacts match`) | `remediation/PS-011/verify.log` |
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM | 0 (129 passed) | `remediation/PS-011/verify.log` |
| `python3 -m pytest -q tests/phase8 tests/phase10` | edge-builder VM | 0 (38 passed, 2 skipped) | `remediation/PS-011/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-011/verify.log` |
| dirty-tree guard (clean / dirty checkout) | edge-builder VM | 0 / 1 | `remediation/PS-011/verify.log` |
| `systemd-analyze verify deploy/edge-control-plane.service` | edge-builder VM (systemd 255) | 0 | `remediation/PS-011/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-011/verify.log` |

Base reproduction on the same VM (archive of `origin/main` `f5811d1`): no `ExecStartPre`
guard, no `closeout/check_derived.py`, and no final-response `--check` wiring, so a dashboard
edit is undetected. Patch checks on the same VM: clean tree passes and a dirty tree is refused;
mutating the dashboard, the gate ledger, or the audit mirror makes the corresponding guard exit
1, and the restored tree passes again. All recorded in `verify.log`.

- Secret scan: **pass** — "no leaks found" (6.73 MB scanned).
- Scope check: **pass** — patch-set files (`deploy/edge-control-plane.service`, `ci/validate.sh`,
  `closeout/`) plus a Phase-10 regression test. No product code, API, schema or dependency changed.

## Evidence bundle

- `remediation/PS-011/diff.patch` — SHA-256 `7dd18c6e28047b0bf2ceb03fe1b554a253b0eb33c64856858df443efe777c421`
- `remediation/PS-011/manifest.json`
- `remediation/PS-011/verify.log`

## Risk and rollback

- Risk: **low**. The only runtime behaviour change is that the control-plane unit refuses to
  start from a dirty checkout — deliberate, and the intent of `ARCH-P2-001`. The CI additions
  are additive checks; the pinned digests are CRLF-normalised so they hold on a normal checkout
  and on a `git archive` export. No API/schema/dependency changes.
- Rollback: `git revert <sha>` restores the previous unit, CI gate and closeout checks.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- **Pinned release vs. dirty-tree guard.** `ARCH-P2-001`'s preferred fix is to deploy a pinned
  release directory / `git worktree` at a recorded commit. This PR takes the finding's
  fail-closed alternative (refuse a dirty working tree) because the release pipeline is outside
  this patch set; moving the unit to a pinned release path remains the stronger follow-up and is
  an owner/release decision.
- **Dashboard generator.** `config/grafana/edge-fleet-dashboard.json` has no generator in the
  repo, so it is pinned as a point-in-time snapshot (digest + `frozen_at_commit`) rather than
  regenerated. If a generator is added later, replace the digest pin with a `--check` against it.
- **Audit-mirror immutability.** The mirror is guarded by a recursive digest; adding an explicit
  "frozen at <sha>" header inside the mirror is a docs follow-up if readers want the marker
  in-file.

## Definition of done (for this set)

From `patch_plan.md`: "dirty-tree alarm; regen guard fails on mutation". The functional check
shows the dirty-tree guard exits 1 on a dirty checkout, and the mutation check shows the regen /
frozen-artifact guards exit 1 when the dashboard, ledger, or mirror is mutated.
