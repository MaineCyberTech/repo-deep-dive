# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PATCH-001` â€” make `orphanCleanup` folder-aware and non-destructive, covering
`DATA-P0-001` (P0) and `TEST-P2-001` (P2).

> **Important base-drift note.** The audit was taken at `fix/p2-batch-31 @ 2295958d`. Since then
> the remote branch was force-updated and now points at `11746adc`; `2295958d` is no longer an
> ancestor of the branch. The audited base already contained commit `08ad3d4d`
> ("fix(security): P2 batch - isolation, credentials and data-loss hardening"), which introduced
> the recursive/folder-aware listing for `orphanCleanup`. This PR is therefore based on the
> current `origin/fix/p2-batch-31` (`11746adc`) and adds the pieces of the patch plan that were
> still missing: a pre-`remove()` object-key assertion, `.emptyFolderPlaceholder` handling, and
> defence against folder entries whose `id` field is **absent** rather than `null`. It is a
> hardening/regression-coverage change, not a re-implementation of the already-present recursion.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d`
- Patch set: `PATCH-001` â€” Make orphan cleanup folder-aware and non-destructive
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P0-001` | P0 | open -> fixed | Folders are recursed (never passed to `remove`), folder placeholders are skipped, and a pre-`remove` guard aborts on any non-object path. |
| `TEST-P2-001` | P2 | open -> fixed | The test mock now models the real `list(path)` contract (folders `id:null`/absent, files with ids, pagination per prefix) and new regression tests fail on the unpatched source. |

## Changes

| File | What changed |
|---|---|
| `apps/worker/src/tasks/orphan-cleanup.ts` | `isFolderEntry` now treats a null **or absent** `id` as a folder (an absent-id folder previously became a `remove()` input = recursive prefix delete). Skip `.emptyFolderPlaceholder`. Bound recursion depth. Add a pre-`remove()` assertion that every orphan path is a concrete nested object key (`/`, no trailing slash, non-empty); abort the bucket and report failure otherwise. |
| `apps/worker/src/__tests__/orphan-cleanup.test.ts` | Mock `list` now models real shapes (folders `id:null`/absent; root files get ids; nested listings pass through). Updated flat fixtures to real nested storage paths. Added three regression tests: absent-`id` folder, `.emptyFolderPlaceholder` skip, and non-object-path abort. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm --filter worker test -- orphan` | Windows host / jest 29 | 0 | `remediation/PATCH-001/verify.log` â€” 14 passed, 14 total |
| Same tests against **unpatched** source (`git stash` of the task file) | jest 29 | 1 | 3 new tests fail: absent-id folder, placeholder, non-object path |
| `corepack pnpm --filter worker typecheck` | tsc 5.7 | 0 | `remediation/PATCH-001/verify.log` |
| `corepack pnpm --filter worker lint` | eslint 9 | 0 | 0 errors (1 pre-existing warning in `src/tasks/retention.ts`, unrelated) |

- Secret scan (gitleaks): **pass** â€” `zricethezav/gitleaks:latest detect --no-git --redact` on the two changed files: `no leaks found`, exit 0.
- Scope check (files within patch set): **pass** â€” only the two files listed in `patch_plan.md` were touched.
- Integration against containerised Supabase Storage: **not run** (out of scope for this runner; the unit suite exercises the `list`/`remove` contract directly).

## Evidence bundle

- `remediation/PATCH-001/diff.patch` â€” SHA-256 `ff9111184d63b41405ce918c30a3e083b40180dd94ee51f673020224c945770e`
- `remediation/PATCH-001/manifest.json`
- `remediation/PATCH-001/verify.log`

## Risk and rollback

- Risk: low. The change is fail-closed: it only ever *removes* paths from the delete set (skips placeholder/folder/unsafe entries and aborts the bucket when an unsafe path is seen). It cannot delete more than the pre-change code did.
- Rollback: `git revert 0538e1ce` (or drop the branch).

## Review checklist

- [x] Diff touches only the patch-set files (+ tests/docs)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran; results pasted, not asserted
- [x] No secrets added; gitleaks clean
- [x] Tests added/updated for the fix where applicable
- [x] Rollback is practical

## Definition of done (for this set)

- No `remove` input equals a folder/prefix; regression test fails on the old code.
- Real `list(path)` semantics modelled (folders, nested files, pagination per path).
- Fixture `orgs/<org>/ref.pdf` + `orgs/<org>/orphan.pdf`: `ref.pdf` survives, only `orphan.pdf` is removed, and no `remove` call includes a folder.

