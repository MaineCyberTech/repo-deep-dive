# Remediation PR - PS-009 (Run binding and inventory)

Draft remediation PR for audit run **20261003-0018-main-7bac320** of the `repo-deep-dive`
pack (pack self-audit). Opened as **draft**; requires human review - the implementer does not
self-approve.

## Summary

Makes the run's own artifacts self-consistent about *which revision was audited* and fixes the
digest/tracked-tree mismatch:

- **INV-P1-001** - the run id/`inventory.json` claimed `7bac320`, while the audited worktree was
  `6cada03`. The run is now explicitly bound to the audited revision `6cada03` in `INDEX.md` and
  `audit_manifest.json` (`recordedSha` keeps the legacy `7bac320` used by the run id).
- **INV-P2-002** - `inventory.json` reported no CI/workflows because it was generated at
  `7bac320`. It is regenerated at `6cada03`, so the org workflow and the two newer Python tools
  are visible (`.py` 9 -> 11; `workflows` `[]` -> `.github/workflows/deep-dive-deterministic.yml`;
  `ci`/`stacks` -> `github-actions`).
- **INV-P3-003** - `opencode.json` (environment-local model pin) was git-tracked yet deliberately
  excluded from the integrity digest. It is now **untracked** (`git rm --cached`), matching the
  documented digest design; the `.gitignore` ignore for local pins lands with PS-008/HYG-P2-001.

`PACK_DIGEST.txt` was regenerated **last**, after all tracked-content changes.

## Patch set

- Patch set: `PS-009` - Run binding and inventory
- Findings: `INV-P1-001`, `INV-P2-002`, `INV-P3-003`
- Base: `origin/main` @ `b3d0382`
- Branch: `remediation/ps-009-20261003-0018-main-7bac320`
- Commit: `c7f59f8c375b9bf649ce6b452352ede37fd8a10b`

## Findings covered

| Finding | Status after this PR | Change |
|---|---|---|
| INV-P1-001 | partially-fixed (draft PR) | run bound to audited `6cada03` in `INDEX.md` + `audit_manifest.json`; `inventory.json` regenerated at `6cada03` |
| INV-P2-002 | partially-fixed (draft PR) | regenerated `inventory.json` now lists the org GitHub Actions workflow |
| INV-P3-003 | partially-fixed (draft PR) | `opencode.json` untracked so the digest covers the tracked tree |

> Per `profiles/remediation.md`, findings move to `verified-fixed` only on merge with the commit as
> evidence; an open/draft PR maps to `partially-fixed`.

## Verification performed

All commands run on the pushed commit `c7f59f8c375b9bf649ce6b452352ede37fd8a10b` (WSL Ubuntu 24.04,
Python 3.12.3, git 2.43.0). Raw transcripts + exit codes: `remediation/PS-009/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash tools/self_test.sh` | local WSL | 0 (`RESULT: PASS`) | `remediation/PS-009/verify.log` |
| `bash tools/lint_pack.sh` | local WSL | 0 (`RESULT: PASS`, `PACK_DIGEST.txt is current`) | `remediation/PS-009/verify.log` |
| `bash tools/check_run.sh runs/repo-deep-dive-20261003-0018-main-7bac320` | local WSL | 0 (`RESULT: PASS`) | `remediation/PS-009/verify.log` |
| INV-P1-001 binding assertion (`inventory.git.sha == 6cada03`, manifest `sha/recordedSha`) | local WSL | 0 | `remediation/PS-009/verify.log` |
| INV-P2-002 workflows assertion (`workflows`, `ci`, `.py == 11`) | local WSL | 0 | `remediation/PS-009/verify.log` |
| INV-P3-003 assertion (`opencode.json` not in `git ls-files`) | local WSL | 0 | `remediation/PS-009/verify.log` |
| Digest vs tracked tree (`comm` equivalent: no missing/extra entries) | local WSL | 0 | `remediation/PS-009/verify.log` |
| `gitleaks detect --no-git --redact` | - | **not run** | binary not installed on the remediation host; the diff is JSON/Markdown/digest only and contains no secret material |

## Diff summary

5 files changed, 30 insertions(+), 24 deletions(-):

- `runs/repo-deep-dive-20261003-0018-main-7bac320/inventory.json` - regenerated at `6cada03`
- `runs/repo-deep-dive-20261003-0018-main-7bac320/INDEX.md` - audited commit `6cada03`
- `runs/repo-deep-dive-20261003-0018-main-7bac320/audit_manifest.json` - scope binding note
- `opencode.json` - untracked (environment-local pin)
- `PACK_DIGEST.txt` - regenerated last

Scoped to PS-009; PS-002/PS-003/PS-004 touch disjoint files (no overlap).

## Evidence bundle

- `remediation/PS-009/verify.log` - raw verification transcripts + exit codes
- `remediation/PS-009/diff.patch` - SHA-256 `dcfa652385ae33d6237d26bdd6a4444d07bc242b29003b863e7a26ce1eab4a8a`
- `remediation/PS-009/manifest.json` - commit/PR + command list + exit codes + diff digest

## Risk

Low. Changes are audit-run metadata and a digest/evidence file; no application code, no runtime,
no dependencies. `opencode.json` is an environment-local pin and removal does not affect the pack's
tooling (nothing references it; `repo_inventory`/`lint_pack`/`self_test` all pass).

## Rollback

Revert the single commit `c7f59f8c375b9bf649ce6b452352ede37fd8a10b` (or close the PR; no state is
mutated). `opencode.json` remains present in local working trees; restore tracking with
`git add opencode.json` if desired (the follow-up `.gitignore` in PS-008 supersedes this).

## Review checklist

- [ ] Run binding is correct: the audited revision is `6cada03`, and `recordedSha`/run id retain `7bac320` intentionally.
- [ ] Regenerated `inventory.json` matches `6cada03` content (`.py == 11`, workflow present).
- [ ] Untracking `opencode.json` is the intended resolution of INV-P3-003 (vs including it in the digest); confirm the PS-008 `.gitignore` follow-up covers local pins.
- [ ] `PACK_DIGEST.txt` is current at the commit and remains complete for the tracked tree.
- [ ] No files outside the PS-009 scope are touched; no conflicts with PS-002/003/004.
- [ ] gitleaks gate: re-run where the binary is available before merge (recorded not-run here).

## Open questions

None. The only choice point - untrack vs include-in-digest for `opencode.json` - is resolved by the
pack's own documented design (environment-local pins are excluded from the digest) and the
PS-008/HYG-P2-001 `.gitignore` dependency.
