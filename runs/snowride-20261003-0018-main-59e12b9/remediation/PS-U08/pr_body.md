# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all hygiene remediation for the unassigned `HYG` findings from the
2026-10-03 audit run. It corrects a stale backup runbook, adds the missing
`.gitattributes` text/binary policy, seeds the in-repo changelog/release lineage,
and stops new generated `repomix-output*.xml` snapshots from being committed.
Two findings need a larger decision and are explicitly deferred with a concrete
path rather than guessed (see Open questions).

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U08` — Unassigned HYG findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `HYG-P2-001` | P2 | open -> **still-open** (deferred) | Making `npm run lint` cover `apps/realtime`, `packages/game-core`, `packages/contracts` needs a shared ESLint config plus a declared `typescript-eslint` devDependency, and will surface an unknown batch of errors (the finding rates it effort **M**). Deferred as an open question instead of shipping a config that guesses rules or leaves the gate red. |
| `HYG-P2-002` | P2 | open -> **partially-fixed** | The recurrence root cause is fixed: `.gitignore` now ignores `repomix-output*.xml` (not just the exact `repomix-output.xml`). Removal/dedup of the already-tracked snapshots and the 6.9 MB PDF is the explicit dependency `INV-P2-001` (patch set `PS-U09`) and is not duplicated here. |
| `HYG-P2-003` | P2 | open -> **verified-fixed** | `docs/runbooks/BACKUP_RESTORE.md` no longer calls the freshness check "known-broken"; it documents the current `*.dump` glob, the `>26 h` alert, and links the 2026-09-27 remediation. The runbook text now matches `scripts/assurance/assurance.sh:123,139`. |
| `HYG-P3-001` | P3 | open -> **partially-fixed** | Added `CHANGELOG.md` as the in-repo release lineage (cross-linked to `docs/product/VERSION_ANALYTICS_POLICY.md`). The remaining half — actually bumping/tagging workspace versions per release — is a release-process change (`DATA-P1-001` dependency) and stays open. |
| `HYG-P3-002` | P3 | open -> **verified-fixed** | Added `.gitattributes`: `* text=auto eol=lf`, binary globs (`*.png/jpg/jpeg/gif/ico/pdf/zip/dump`), and `linguist-generated` for `evidence/**` + `repomix-output*.xml`. `git check-attr` confirms the policy applies. |

## Changes

| File | What changed |
|---|---|
| `docs/runbooks/BACKUP_RESTORE.md` | Replaced the stale "globs `*.sql` / known-broken" note with the current `*.dump` freshness check (`>26 h` -> exit `5`), linking `scripts/assurance/assurance.sh` and `evidence/audit-20260927/REMEDIATION.md`. |
| `.gitattributes` (new) | Repository text/binary normalization (`text=auto eol=lf`), binary globs, and `linguist-generated` markers for generated evidence. |
| `.gitignore` | `repomix-output.xml` -> `repomix-output*.xml` so numbered snapshots are not re-committed. |
| `CHANGELOG.md` (new) | In-repo release lineage: baseline `0.1.0`, link to the per-axis version policy, Keep-a-Changelog/SemVer format. |

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab
(`/srv/work/snowride-ps-u08`, `core.autocrlf` unset) at commit `dcea60b`.
Snowride profile gate (`npm ci && npm run lint && npm test`) plus link,
`.gitattributes` and gitleaks checks.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| relative-link existence check for changed docs | ci-runner | 0 | `linkcheck_broken=0` (`remediation/PS-U08/verify.log`) |
| `git check-attr text binary linguist-generated` on sample paths | ci-runner | 0 | PDF `binary: set`; repomix XML `linguist-generated: true` (`verify.log`) |
| `npm ci` | ci-runner | 0 | 628 packages installed (`verify.log`) |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` (`verify.log`) |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed (`verify.log`) |
| `git status --short` after gates | ci-runner | 0 | clean (generated `dist/` not committed) |
| `gitleaks detect --no-git --redact --source <changed file>` ×4 | ci-runner | 0 | no leaks (`remediation/PS-U08/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing audited fixture hits under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff (`gitleaks.log`) |

- Secret scan (gitleaks): **pass** — all four changed files clean; the 19
  full-tree hits are the same audited, pre-existing fixtures recorded by the
  sibling PS-U03/PS-U04/PS-U05/PS-U07 runs.
- Scope check (files within patch set): **pass** — `PS-U08` declared no file
  list; the diff is limited to the backup runbook, `.gitattributes`,
  `.gitignore` and the new `CHANGELOG.md`.

## Evidence bundle

- `remediation/PS-U08/diff.patch` — SHA-256 `75ee7a34a45458e4c07780262381fec12d6d63440b360bc92a7820ac204a0be5`
- `remediation/PS-U08/verify.log` — SHA-256 `df271d64f672dac482b66c3f624860c3e2b804ce9a357e4c986e259ec5bab918`
- `remediation/PS-U08/gitleaks.log` — SHA-256 `fe80bfd83c2a3cd011155f93d8e94381c681428d45690964043a1f0260bcc180`
- `remediation/PS-U08/manifest.json`

## Risk and rollback

- Risk: **very low**. Docs/config only; no runtime code, CI workflow,
  dependency or lockfile change. `.gitattributes` normalization is applied on
  future checkouts (no `--renormalize` run, so no mass line-ending diff).
- Rollback: `git revert dcea60b19dac6a3f98c145a68ba74e13361a3526`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **`HYG-P2-001` needs an ESLint design decision (deferred).** Covering the
   un-linted workspaces means adding a root/per-workspace ESLint config and a
   declared `typescript-eslint` dependency, then fixing whatever errors appear
   in `apps/realtime` / `packages/game-core` / `packages/contracts`. This is a
   real change (effort **M**), not a hygiene one-liner; a maintainer should pick
   the ruleset and own the error cleanup. Recommended follow-up patch set.
2. **`HYG-P2-002` deletion/dedup is `INV-P2-001` (PS-U09).** This PR stops new
   snapshots but deliberately does not delete the tracked copies or the PDF;
   that overlaps the inventory catch-all. Merge ordering: `PS-U09` first, then
   this.
3. **`HYG-P3-001` release cadence.** The changelog now exists, but version bumps
   and tags per release (`DATA-P1-001` dependency) remain a process change. The
   baseline section is the current `0.1.0` state, dated from the `c4ec021`
   scaffold commit.
4. **Potential `BACKUP_RESTORE.md` overlap with PS-U07.** PS-U07 edits the
   "Notes" (RPO/RTO) section of the same file; this PR edits the assurance-lane
   paragraph earlier in the file. If both merge, resolve any conflict by keeping
   both changes (they are additive).

## Definition of done (for this set)

- Backup runbook matches the current `*.dump` assurance check (`HYG-P2-003`).
- `.gitattributes` present and confirmed via `git check-attr` (`HYG-P3-002`).
- `CHANGELOG.md` committed and cross-linked to the version policy (`HYG-P3-001`).
- New `repomix-output*.xml` snapshots are ignored (`HYG-P2-002` root cause).
- `HYG-P2-001` and the deletion half of `HYG-P2-002` recorded as open with a
  concrete path.
- The snowride profile gate remains green (`npm ci`, `npm run lint`,
  `npm test`) and the changed files scan clean under gitleaks.
