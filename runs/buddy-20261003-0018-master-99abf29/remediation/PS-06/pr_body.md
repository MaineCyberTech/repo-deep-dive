# Remediation PR — PS-06 Feature wiring

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Wires the three half-implemented gameplay systems identified by the audit into the live
game loop. Achievements are now evaluated and persisted after every care action and
adventure, and pay out their configured coin/item rewards exactly once (FEAT-P1-001).
Lifecycle evolution and skill growth run in the care and adventure paths instead of only
as pure functions (FEAT-P1-002). The item catalogue is functional: food, medicine, toys
and skill books can be used, hats equipped, and items sold for coins (FEAT-P2-001).

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-06` — Feature wiring
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `25149bb33e65634820179eac3ca4f9c2ce956e5a`
- Branch: `remediation/ps-06-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P1-001` | P1 | open -> fixed | `grantAchievements` (data/achievements.ts) evaluates `checkAchievements`, persists unlocked ids in `progression.achievements`, records a memory, and grants `rewardCoins`/`rewardItemId`. Called from `applyAction` (care) and `applyAdventureResult` (adventure); rewards are granted once via the unlocked-id dedupe. |
| `FEAT-P1-002` | P1 | open -> fixed | `advanceProgression` (lib/actions/care.ts) invokes `checkEvolution` (against lifetime XP) and `updateSkills`, and is called from both care actions and adventures. `train`/`talk` grow `training`/`social`; adventures grow `exploring`. |
| `FEAT-P2-001` | P2 | open -> fixed | New pure `applyItemAction` (use/sell/equip) in `lib/actions/care.ts`; `InventoryScreen` exposes USE / EQUIP / SELL buttons per item and writes results back to the store. Food/medicine/toy/skill_book are consumed, hats equipped, sellable items convert to coins. |

## Changes

| File | What changed |
|---|---|
| `data/achievements.ts` | Added `grantAchievements(buddy, inventory, totalAdventures)` — dedupes against `progression.achievements`, adds reward coins/items, and appends memory entries. |
| `lib/actions/care.ts` | `applyAction` now takes/returns `inventory`, runs `advanceProgression` + `grantAchievements`. Added `advanceProgression` (evolution/skills) and `applyItemAction` (use/sell/equip). |
| `lib/locations/adventure.ts` | `applyAdventureResult` now keeps `xp` as a post-level remainder, runs `advanceProgression('exploring')`, and grants achievements against the post-adventure count. |
| `components/device/MainDevice.tsx` | `handleAction` passes the store inventory through `applyAction`, writes back the returned inventory, and saves it. |
| `components/device/InventoryScreen.tsx` | Adds USE/EQUIP/SELL actions per item, wired to `applyItemAction` and the store. |
| `data/achievements.test.ts` (new) | Once-only grant, reward-item grant, and live adventure-path integration. |
| `lib/actions/items.test.ts` (new) | Use/sell/equip per category, decrement, and rejection paths. |
| `lib/progression/lifecycle.test.ts` | Live-path baby->child and skill-growth tests; `[...new Set]` -> `Array.from(new Set)` to unblock the pre-existing `TS2802` typecheck error (same minimal unblock as PS-01/PS-03). |
| `lib/locations/adventure.test.ts` | Coin assertions now account for achievement rewards introduced by FEAT-P1-001. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `25149bb`) | 0 | `remediation/PS-06/verify.log` — lint clean; typecheck clean; 7 files / 124 tests passed (`__VERIFY_EXIT=0`) |
| `npm run test -- achievements lifecycle items` | lab: `ci-runner` | 0 | 4 files / 47 tests passed |
| `git archive HEAD \| tar -x -C /tmp/glscan-ps06 && gitleaks detect --no-git --redact --source /tmp/glscan-ps06 -v` | lab: `ci-runner` | 0 | `no leaks found` (≈271.6 KB, tracked content at the commit) |
| `npm run lint` / `npm run typecheck` / `npm run test` | local (node v24.19.0) | 0 | 7 files / 124 tests passed |

- Scope check: pass. Runtime files touched are exactly the patch-set files
  (`lib/actions/care.ts`, `lib/locations/adventure.ts`, `components/device/MainDevice.tsx`,
  `components/device/InventoryScreen.tsx`, `data/achievements.ts`); the remaining changes are
  the required new/updated tests plus the pre-existing `TS2802` one-line typecheck unblock in
  `lib/progression/lifecycle.test.ts`.

## Evidence bundle

- `remediation/PS-06/diff.patch` — SHA-256 `8de1352a47ed4a77c1c1c2df9c764c19cfee84cc94aa14d43bd0148e7226175a`
- `remediation/PS-06/verify.log` — SHA-256 `b7303bad426aabb75ef524a1898ed49abe87b7e095a9447ff555c7d206c382a1`
- `remediation/PS-06/manifest.json`

## Risk and rollback

- Risk: **low–moderate**. Behavior changes are additive to the existing pure functions.
  Achievement rewards now flow into the inventory on the first qualifying care/adventure,
  and item actions mutate inventory/needs as designed. No schema or storage changes.
- Rollback: `git revert 25149bb`.

## Open questions / reviewer actions

1. **PS-04 dependency not merged.** The plan lists PS-04 (save integrity) as a dependency.
   This branch is based on `origin/master` and does not depend on `lib/storage/schema.ts`;
   rebase/re-run if PS-04 lands first.
2. **`first_hatch` timing.** `first_hatch` has `condition: () => true` and is granted on the
   first care action/adventure rather than at hatch time, because `HatchFlow.tsx` is outside
   this patch set. Confirm whether to move it to the hatch flow.
3. **`AdventureScreen.tsx` untouched.** Achievement/evolution wiring for adventures lives in
   `applyAdventureResult` so the flow stays within the patch-set files; `AdventureScreen`
   continues to increment `progression.totalAdventures` after the call. `applyAdventureResult`
   evaluates achievements against `totalAdventures + 1` to match.
4. **PS-03 overlap on `MainDevice.tsx`.** PS-03 removes the private `currentBuddy` state; this
   branch changes `handleAction` to thread the inventory through `applyAction`. Both are
   additive; rebase whichever lands second.
5. **Economy balance.** Item effect magnitudes (food +25 hunger, medicine +30 HP, skill book
   +5 stat) are first-pass values; the balance matrix may want tuning.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests listed above)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical
