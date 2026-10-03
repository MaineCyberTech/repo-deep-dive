# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all inventory remediation for the unassigned `INV` findings from the
2026-10-03 audit run. It removes the two superseded full-source `repomix`
exports (keeping the latest package), removes the superseded 6.9 MB roadmap
PDF, documents an archive/size policy, reconciles the `*.log` ignore rule with
the tracked evidence transcripts, and re-homes the one-off root review
artifacts under `docs/archive/` with a pointer. No runtime, CI, dependency or
lockfile change.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U09` — Unassigned INV findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `INV-P2-001` | P2 | open -> **partially-fixed** | Deleted the two superseded duplicate packages (`repomix-split` r70, `repomix-r71`) and kept only the latest `repomix-r71-repair`. Recurrence is already excluded by `.repomixignore`; the retained-snapshot policy is documented in `docs/EVIDENCE.md`. Draft PR is not merged, so reconciliation records `partially-fixed`. |
| `INV-P2-002` | P2 | open -> **partially-fixed** | Added an explicit archive & size policy (budget, generated-artifact rule, current-state pointer). This change drops the tracked worktree from ~95 MB to ~53 MB, but the evidence tree still dominates by file count; the full archive/index restructure is deliberately left to a dedicated follow-up. |
| `INV-P3-001` | P3 | open -> **verified-fixed** | `.gitignore` now documents the intentional allowlist: `!evidence/**/*.log`. All 94 tracked logs are under `evidence/` (`non_evidence_logs=0`), so the ignore rule now describes the tree. No files were renamed/deleted. |
| `INV-P3-002` | P3 | open -> **verified-fixed** | Moved `ext_review.md`, `reviewer.md`, `agent_final_response.json`, `GATE_LEDGER.csv`, `REVIEW_PLAN_20260911.md` to `docs/archive/` with a pointer README; removed the superseded roadmap PDF. `root_review_artifacts_remaining=0`. |

## Changes

| File | What changed |
|---|---|
| `evidence/production-acceptance/repomix-split/**` (deleted) | Superseded r70 full-source snapshot, removed as a duplicate (`git rm`). |
| `evidence/production-acceptance/repomix-r71/**` (deleted) | Superseded r71 full-source snapshot, removed as a duplicate (`git rm`). |
| `evidence/production-acceptance/repomix-r71-repair/**` (kept) | Latest package retained as the single archived snapshot. |
| `snowride_production_grade_major_phase_roadmap_20260911_050010.pdf` (deleted) | Superseded 6.9 MB generated roadmap; recoverable from git history. |
| `.gitignore` | Added a documented evidence-transcript exemption (`!evidence/**/*.log`) for `INV-P3-001`. |
| `docs/EVIDENCE.md` | New "Archive & size policy" section (generated snapshots, large reports, log allowlist, budget, current-state pointer). |
| `docs/archive/README.md` (new) | Pointer for the re-homed one-off review artifacts. |
| `ext_review.md`, `reviewer.md`, `agent_final_response.json`, `GATE_LEDGER.csv`, `REVIEW_PLAN_20260911.md` | Moved to `docs/archive/` (100% renames, content unchanged). |

Coordination with `PS-U08`: that set adds `.gitattributes` and edits the
`repomix-output.xml` line in `.gitignore`; this set appends the `*.log`
exemption at the end of `.gitignore` and does not touch `.gitattributes`.
The hunks are disjoint, so both PRs should merge cleanly.

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab
(`/srv/work/snowride-ps-u09`, `core.autocrlf` unset) at commit `8f369a6`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| relative-link existence check for changed docs | ci-runner | 0 | `linkcheck_broken=0` (`remediation/PS-U09/verify.log`) |
| tracked repomix packages | ci-runner | 0 | one package remains (`repomix-r71-repair`); `repomix_file_count=16` |
| tracked `.log` + `.gitignore` exemption | ci-runner | 0 | `tracked_log_count=94`, `non_evidence_logs=0`, new evidence logs match `!evidence/**/*.log` |
| root review artifacts remaining | ci-runner | 0 | `root_review_artifacts_remaining=0` |
| largest tracked files / worktree size | ci-runner | 0 | worktree `53 MB` (was ~95 MB) |
| `npm ci` | ci-runner | 0 | 628 packages installed |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed |
| `git status --short` after gates | ci-runner | 0 | clean |
| `gitleaks detect --no-git --redact --no-banner --source <changed file>` ×3 | ci-runner | 0 | no leaks (`remediation/PS-U09/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 16 pre-existing `generic-api-key` fixture hits under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff |

- Secret scan (gitleaks): **pass** — all three changed text files clean; the 16
  full-tree hits are the pre-existing audited fixtures also recorded by the
  sibling PS-U03/PS-U04/PS-U05/PS-U07/PS-U08 runs (down from 19 because the two
  deleted snapshot packages carried some of them).
- Scope check (files within patch set): **pass** — `PS-U09` declared no file
  list; the diff is limited to `INV` inventory artifacts (`repomix-*`, the
  roadmap PDF, `.gitignore`, `docs/EVIDENCE.md`, `docs/archive/**`).

## Evidence bundle

- `remediation/PS-U09/diff.patch` — SHA-256 `e7b483434c0a6fe5e79fa8a2b8ee1f5a944a2f1d2eb46edbe8039428495f6e6f`
- `remediation/PS-U09/verify.log` — SHA-256 `a4eb5c29725e19438e4a0ab3d690e0345522f629006d0d67fec6abc33db785f0`
- `remediation/PS-U09/gitleaks.log` — SHA-256 `ecfcf6f6a62e004e88067e52336670d7b838cf80e6f6ac5dac6c828c55622d6c`
- `remediation/PS-U09/manifest.json`

## Risk and rollback

- Risk: **low**. Docs/config plus removal of generated, reproducible artifacts;
  no runtime code, CI workflow, dependency or lockfile change. The deleted files
  remain in git history (`git rm`, no history rewrite).
- Rollback: `git revert 8f369a62f019bf8a0527908e9e61307f931fa6e9`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- Duplicate `repomix` packages de-duplicated and recurrence excluded (`INV-P2-001`).
- Archive & size budget documented; worktree shrunk (`INV-P2-002`).
- `.gitignore` reconciles with the tracked evidence logs (`INV-P3-001`).
- Root one-off review artifacts re-homed with a pointer (`INV-P3-002`).

## Open questions

1. **`INV-P2-002` full restructure.** The evidence tree still dominates by file
   count (853 evidence files). A real fix is an explicit archive/index policy
   with CI enforcement (tree-size budget) plus moving older closeouts to
   `docs/archive/` or release storage. That is an M-effort change and is left
   open; this PR only documents the policy and cuts the duplicated weight.
2. **`evidence/MANIFEST.sha256` was not regenerated.** It is a historical
   integrity binding (already stale at the base: 877 entries vs 853 tracked
   evidence files). Removing/renaming files intentionally supersedes it at the
   tip; regenerating it is a separate evidence-maintenance change and the
   doctrine forbids hand-editing old manifest lines.
3. **Retained repomix snapshot.** `repomix-r71-repair` is kept as the single
   archived package. It still contains eight pre-existing `generic-api-key`
   gitleaks fixture matches; if the owner prefers zero retained snapshots, a
   follow-up can delete it (nothing has referenced it since the r71 closure).
4. **Roadmap PDF is removed, not archived.** The audit's open question marked
   its active/historical status `Unknown` (superseded by `ext_review.md`); it
   was removed per the size budget and remains recoverable from history.
