# Remediation PR - PS-005 (Change control and docs)

Draft remediation PR for audit run **20261003-0018-main-7bac320** of the `repo-deep-dive`
pack (pack self-audit). Opened as **draft**; requires human review - the implementer does not
self-approve.

## Summary

Closes the change-control gap from FEAT-P2-001 by giving the deterministic-checks / org-runner /
remediation release its own version instead of re-using the previous one, and confirms FEAT-P3-002
(README tools inventory) against the current tree.

- **FEAT-P2-001** - `CHANGELOG.md` documented the new capabilities under a top entry labelled
  **v1.4.1**, the same version as the preceding 2026-10-02 entry, and `VERSION` was never bumped.
  This PR bumps the base pack `1.4.1 -> 1.5.0`, relabels the 2026-10-03 entry `(v1.5.0)`, adds a
  `Versions` bullet, and brings `README.md`, both example manifests, and
  `profiles/falcon-lab.manifest.json` version fields into sync (enforced by `lint_pack.sh`).
- **FEAT-P3-002** - the stale `tools/` inventory was already refreshed on `main`
  (`README.md` now lists all 21 `tools/*` basenames). No additional README edit is needed; this PR
  adds an explicit assertion so the row cannot silently drift again (the reviewer can decide whether
  to promote it into `lint_pack.sh`, which is `ARCH`/PS-006 scope).

`PACK_DIGEST.txt` was regenerated **last**, after all tracked-content changes.

## Patch set

- Patch set: `PS-005` - Change control and docs
- Findings: `FEAT-P2-001`, `FEAT-P3-002`
- Base: `origin/main` @ `b3d0382`
- Branch: `remediation/ps-005-20261003-0018-main-7bac320`
- Commit: `c07a49a4b1a0001b5d6f38b4b2504d9a1a2c5289`

## Findings covered

| Finding | Status after this PR | Change |
|---|---|---|
| FEAT-P2-001 | partially-fixed (draft PR) | base pack bumped `1.4.1 -> 1.5.0`; CHANGELOG top entry relabelled `(v1.5.0)` + `Versions` bullet; `VERSION`/README/2 example manifests/`falcon-lab.manifest.json` synced |
| FEAT-P3-002 | partially-fixed (draft PR) | already resolved on `main` (all 21 tools listed); regression assertion added to the PS-005 binding checks |

> Per `profiles/remediation.md`, findings move to `verified-fixed` only on merge with the commit as
> evidence; an open/draft PR maps to `partially-fixed`.

## Verification performed

All commands run on the pushed commit `c07a49a4b1a0001b5d6f38b4b2504d9a1a2c5289` (WSL Ubuntu 24.04,
Python 3.12.3, git 2.43.0). Raw transcripts + exit codes: `remediation/PS-005/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash tools/self_test.sh` | local WSL | 0 (`RESULT: PASS`) | `remediation/PS-005/verify.log` |
| `bash tools/lint_pack.sh` | local WSL | 0 (`RESULT: PASS`, `VERSION = 1.5.0`, `README references v1.5.0`, `JSON version fields match VERSION`, `PACK_DIGEST.txt is current`) | `remediation/PS-005/verify.log` |
| `bash tools/check_run.sh runs/repo-deep-dive-20261003-0018-main-7bac320` | local WSL | 0 (`RESULT: PASS`) | `remediation/PS-005/verify.log` |
| FEAT-P2-001 assertion (`VERSION`/README/3 JSON version fields == 1.5.0) | local WSL | 0 | `remediation/PS-005/verify.log` |
| FEAT-P2-001 assertion (CHANGELOG top entry `(v1.5.0)`; names `deterministic_checks.py`, `aggregate_findings.py`, `deep-dive-deterministic.yml`, `remediation_plan.py`) | local WSL | 0 | `remediation/PS-005/verify.log` |
| FEAT-P3-002 assertion (all 21 `tools/*` basenames appear in `README.md`) | local WSL | 0 | `remediation/PS-005/verify.log` |
| `gitleaks detect --no-git --redact` | - | **not run** | binary not installed on the remediation host; the diff is version strings + changelog/README prose + digest only and contains no secret material |

## Diff summary

7 files changed, 16 insertions(+), 13 deletions(-):

- `VERSION` - `1.4.1` -> `1.5.0`
- `CHANGELOG.md` - top entry `(v1.4.1)` -> `(v1.5.0)`; add `Versions` bullet (`1.4.1 -> 1.5.0`)
- `README.md` - header `base edition v1.4.1` -> `v1.5.0`
- `examples/audit_manifest.example.json` - `version` -> `1.5.0`
- `examples/audit_manifest.falcon-lab.example.json` - `packVersion` -> `1.5.0`
- `profiles/falcon-lab.manifest.json` - `basePackVersion` -> `1.5.0` (`profileVersion` stays `1.1.0`)
- `PACK_DIGEST.txt` - regenerated last

Scoped to PS-005; PS-002/PS-003/PS-004/PS-009 touch disjoint files (no overlap). No file outside
the patch set is modified.

## Evidence bundle

- `remediation/PS-005/verify.log` - raw verification transcripts + exit codes
- `remediation/PS-005/diff.patch` - SHA-256 recorded in `manifest.json`
- `remediation/PS-005/manifest.json` - commit/PR + command list + exit codes + diff digest

## Risk

Low. Documentation and manifest-version metadata only; no application code, runtime, dependencies,
workflows, or archived run artifacts are touched. `lint_pack.sh`/`self_test.sh` pass and the digest
is current.

## Rollback

Revert the single commit `c07a49a4b1a0001b5d6f38b4b2504d9a1a2c5289` (or close the PR; no state is
mutated). The pack returns to `1.4.1` with the previous digest.

## Review checklist

- [ ] `1.5.0` is the correct next version (minor bump for the new deterministic/org/remediation capabilities) versus a patch bump.
- [ ] The 2026-10-03 CHANGELOG top entry is correctly relabelled `(v1.5.0)` (it previously duplicated the v1.4.1 label).
- [ ] `profileVersion` `1.1.0` intentionally unchanged (only `basePackVersion` follows the base pack).
- [ ] FEAT-P3-002 is accepted as already-satisfied on `main` (all 21 tools listed); decide whether the README drift assertion should be promoted into `lint_pack.sh` under PS-006/ARCH.
- [ ] `PACK_DIGEST.txt` is current at the commit and no archived `runs/**/audit_manifest.json` was altered.
- [ ] No files outside the PS-005 scope are touched; no conflicts with PS-002/003/004/009.
- [ ] gitleaks gate: re-run where the binary is available before merge (recorded not-run here).

## Open questions

- FEAT-P2-001's original scope also mentioned listing new tools/workflow in `REFERENCE_CARD.md`; the
  card already covers deterministic checks + remediation at the capability level (no version string).
  No edit is included - flag if a more explicit tool list is desired.
- Whether FEAT-P3-002 should be closed `verified-fixed` on the basis of the prior `main` commit, or
  held `partially-fixed` until this PR (which adds the regression assertion) is merged.
