# Remediation PR — PS-03 State & identity correctness

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Fixes the stale-device defect in the primary gameplay loop and the guest-identity defects. The
game store is now the single source of truth for the device, so an adventure result written by
`AdventureScreen` is reflected immediately in the LCD/mood/HP/energy (previously `MainDevice`
rendered from a private `useState` copy and only updated on remount). Guest identity is now
restored from the save across reloads and generated with `crypto.randomUUID()` instead of
`Math.random()`. Two focused regression tests cover both behaviors.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-03` — State & identity correctness
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `96c3e6650dc345dd699c6e5825fa9505810c0cb3`
- Branch: `remediation/ps-03-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P1-002` | P1 | open -> fixed | `MainDevice` subscribes to `useGameStore(s => s.buddy)` instead of holding a local copy; adventure/care/decay writes to the store now render immediately. New regression test `components/device/MainDevice.test.tsx`. |
| `ARCH-P2-002` | P2 | open -> fixed | `app/page.tsx` restores `save.guestId` into the store on load; `HatchFlow` generates ids with `crypto.randomUUID()`. New regression test `app/page.test.tsx`. |
| `SEC-P3-001` | P3 | open -> fixed (live path) | Guest ids are generated with `crypto.randomUUID()`. The duplicate weak pattern in `lib/storage/autosave.ts` is dead code (`ARCH-P2-003`, scheduled for PS-05) and is out of this patch set's file scope; flagged in Open questions. |

## Changes

| File | What changed |
|---|---|
| `components/device/MainDevice.tsx` | Derives `currentBuddy` from the store (`storedBuddy ?? initialBuddy`) and seeds the store from the prop only when empty. Care actions and offline decay write to the store, removing the private `useState` copy that caused the stale LCD (ARCH-P1-002). |
| `components/device/AdventureScreen.tsx` | Subscribes to individual store fields instead of the whole store (decouples the adventure flow from unrelated state). |
| `app/page.tsx` | Restores the persisted `guestId` from the save via `setGuestId` (ARCH-P2-002). |
| `components/hatch/HatchFlow.tsx` | Generates the guest id with `crypto.randomUUID()`, with a `Math.random` fallback only for non-secure contexts (SEC-P3-001). |
| `components/device/MainDevice.test.tsx` (new) | Asserts the device seeds the store from its prop and re-renders when the store buddy changes (ARCH-P1-002). |
| `app/page.test.tsx` (new) | Asserts `guestId`/buddy/inventory are restored from the loaded save (ARCH-P2-002). |
| `vitest.config.ts` | Sets esbuild `jsx: 'automatic'` so `.tsx` tests use the same JSX runtime as Next (supporting change for the new tests). |
| `lib/progression/lifecycle.test.ts` | `[...new Set(x)]` -> `Array.from(new Set(x))`: unblocks `npm run typecheck` on the base commit (pre-existing `TS2802`; identical minimal unblock already made in PS-01). |

`lib/buddy/store.ts` is listed in the patch plan but needed no change: it already exposes
`buddy`, `setBuddy`, `updateBuddy`, and `setGuestId`; the fix is to consume them.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `96c3e66`) | 0 | `remediation/PS-03/verify.log` — 7 files / 111 tests passed; lint/typecheck clean (`__VERIFY_EXIT=0`) |
| `git archive HEAD \| tar -x -C /tmp/glscan-ps03 && gitleaks detect --no-git --redact --source /tmp/glscan-ps03 -v` | lab: `ci-runner` | 0 | `remediation/PS-03/verify.log` — `no leaks found` tracked content at the commit |
| `npm run lint` | local (node v24.19.0) | 0 | No ESLint warnings or errors |
| `npm run typecheck` | local (node v24.19.0) | 0 | clean |
| `npm run test` | local (node v24.19.0) | 0 | 7 files / 111 tests passed (109 pre-existing + 2 new) |

- Secret scan (gitleaks): pass on tracked repository content, exit 0, no leaks found.
- Scope check (files within patch set): pass with documented supporting files — patch-set files
  `MainDevice.tsx`, `AdventureScreen.tsx`, `app/page.tsx`, `HatchFlow.tsx`; plus the two required
  regression tests, `vitest.config.ts` (JSX runtime for `.tsx` tests), and
  `lib/progression/lifecycle.test.ts` (the pre-existing `TS2802` typecheck unblock, matching PS-01).
  No runtime/application logic outside the patch set changed.

## Evidence bundle

- `remediation/PS-03/diff.patch` — SHA-256 `b8d71ed74fb8f589e052ec800ac8af468a525f761c8329e722b57983adc0e6c9`
- `remediation/PS-03/manifest.json`
- `remediation/PS-03/verify.log` — SHA-256 `6beead71a2c2d2b8556279c3aa72e04c1e0899caf46d3f5fa937e6707e10cf56`

## Risk and rollback

- Risk: **low**. The device now reads from the existing store instead of a duplicate local copy;
  care actions, offline decay, hatch, and load continue to write the same `BuddyState`. Guest id
  format changes from `guest-<ts><rand>` to a UUID, which is compatible with the save schema
  (`guestId: string`) and improves the import check. The added tests are additive.
- Rollback: `git revert 96c3e66`.

## Open questions / reviewer actions

1. **Dead-code duplicate of the weak RNG** — `lib/storage/autosave.ts` line 12 still builds a
   `guest-...Math.random()` id, but `startAutosave`/`stopAutosave` have no call site
   (`ARCH-P2-003`). It is outside PS-03's file scope; PS-05 should delete or fix it. Confirm.
2. **Own IndexedDB key for `guestId`** — the audit suggested storing the id under its own key.
   This patch restores it from the existing save envelope, which satisfies save->reload->save
   stability without a schema change. A dedicated key is deferred to PS-04 (save integrity).
3. **`vitest.config.ts` JSX setting** — overlaps with PS-01's edit to the same file (coverage
   config). Both changes are additive; rebase whichever lands second.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs listed above)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

A component test proves an adventure updates the rendered device state, and a reload test proves
the same `guestId` is preserved; lint/typecheck/test pass in the lab.
