# Feature Implementation and Gap Map

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: FEAT
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/03_feature_implementation_map.md
- Scope limitations: Static review only; no runtime exercising. `node_modules` absent.

## Scope

Mapped every user-facing feature to its code path: hatch, care loop, offline decay, adventures/loot, inventory/economy, lifecycle/evolution, skills, achievements, and memories. Checked each against UI wiring, tests, and docs. Not reviewed: mini-games, seasonal events, home customization beyond confirming absence.

## Evidence Reviewed

- `app/page.tsx`, `components/hatch/HatchFlow.tsx`, `components/device/MainDevice.tsx`, `components/device/AdventureScreen.tsx`, `components/device/InventoryScreen.tsx`
- `lib/actions/care.ts`, `lib/locations/adventure.ts`, `lib/progression/lifecycle.ts`
- `data/items.ts`, `data/loot-tables.ts`, `data/locations.ts`, `data/achievements.ts`
- `docs/buddy/reports/phases/phase-01..08-completion-report.md`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `grep checkAchievements\|createMemory` | command | wiring check | only definitions/tests, no app call |
| `grep checkEvolution\|updateSkills` | command | wiring check | only in `lifecycle.test.ts` |
| `grep getStageProgress` | command | unused import | imported in `MainDevice.tsx`, never used |
| `grep DECOR_ITEMS\|HAT_MAP` | command | unused exports | no call sites |
| `Select-String 'it('` | command | test count | 109 matches |
| phase reports | docs | claimed status | claim "None" P0/P1 |

## Executive Summary

The **core loop is real and playable**: hatch a deterministic pet, feed/play/wash/rest/talk/train/heal, take adventures against 9 locations with loot tables, and view stats, needs, profile, and inventory. Unit tests cover generation, care, adventure, lifecycle, items, and loot (109 cases).

However, three of the eight advertised phases are only half-wired. **Achievements (15), memories, lifecycle evolution, and skill progression are implemented as pure functions but never invoked from the game loop**; the phase-06 report itself lists "Integrate achievement checking into main game loop" as remaining work. Items are display-only: there is **no use/sell/equip**, so `sellValue`, `effect`, food/medicine/toy categories, and `skill_book` effects are inert. The economy has income (adventure coins/items) but no sink. This makes progression (level/stage/bond) mostly cosmetic and the item catalogue non-functional.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Hatch | `components/hatch/HatchFlow.tsx` | onboarding | Implemented | Low | saves on confirm |
| Care loop | `lib/actions/care.ts`, `MainDevice.tsx` | core actions | Implemented | Low | 7 actions |
| Offline decay | `care.ts::applyOfflineDecay`, `MainDevice.tsx` | time decay | Implemented | Low | 60s threshold |
| Adventures | `lib/locations/adventure.ts`, `AdventureScreen.tsx` | exploration | Implemented | Medium | state desync (ARCH) |
| Loot | `data/loot-tables.ts` | drops | Implemented | Low | deterministic with seed |
| Inventory UI | `components/device/InventoryScreen.tsx` | browse items | Implemented | Low | read-only |
| Item usage/economy | (none) | use/sell/equip | Absent | High | item effects unused |
| Lifecycle | `lib/progression/lifecycle.ts` | stages | Partial | High | evolution not called |
| Skills | `lifecycle.ts::updateSkills` | skill growth | Absent(wired) | High | never called |
| Achievements | `data/achievements.ts` | rewards | Absent(wired) | High | `checkAchievements` unused |
| Memories | `data/achievements.ts::createMemory` | journal | Absent(wired) | Medium | unused |
| Home/seasonal/mini-games | (none) | future | Absent | Low | declared future |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Pages/routes | 3 | `app/page.tsx` single route | no deep links | acceptable for SPA |
| Components | 3 | 8 components | desync | fix ARCH-P1-002 |
| API endpoints | 0 | none | N/A | document |
| Server actions | 0 | none | N/A | document |
| Workers/jobs | 0 | none | N/A | N/A |
| Database entities | 1 | IndexedDB store | no migration | DATA findings |
| Permissions | 0 | guest-only | no accounts | document |
| Audit logs | 0 | none | no history | add memory/event log |
| Tests | 3 | 109 unit | no UI/E2E | TEST findings |
| Docs | 2 | phase reports overclaim | stale status | reconcile |
| Workflow states | 2 | screens enum | limited | expand if needed |
| Failure states | 2 | `save failed`, `Too tired` | partial | add error boundary |

## Detailed Review

### Item: Achievements
- Evidence: `data/achievements.ts` defines 15 achievements with `condition`s; `checkAchievements` (line 136) has no caller in `app/`/`components/`/`lib/`; phase-06 report line 37 lists integration as remaining.
- Risks: rewards never granted; "15 unlockable achievements" is not player-reachable.

### Item: Lifecycle / evolution / skills
- Evidence: `lib/progression/lifecycle.ts::checkEvolution` and `updateSkills` called only from `lifecycle.test.ts`; `MainDevice.tsx` only displays `getStageName`.
- Risks: XP accumulates but the pet never evolves or grows skills, contradicting phase-06 summary.

### Item: Item economy
- Evidence: `data/items.ts` has `sellValue` and `effect`; `InventoryScreen.tsx` only lists items; no shop/use code.
- Risks: loot has no purpose beyond collection; economy balance (game-balance-matrix) unenforceable.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FEAT-001 | Achievements granted | `data/achievements.ts` | none | not wired | P1 | call from action/adventure |
| FEAT-002 | Evolution/skills | `lifecycle.ts` | none | not wired | P1 | invoke on XP change |
| FEAT-003 | Item use/economy | `data/items.ts`, `InventoryScreen.tsx` | display only | no use/sell/equip | P2 | implement item actions |

## Findings

### Finding ID: FEAT-P1-001 - Achievement system is implemented but never invoked during gameplay

- Severity: P1
- Confidence: High
- Area: FEAT
- Evidence:
  - `data/achievements.ts` — `ACHIEVEMENTS` (15 entries), `checkAchievements` line 136
  - grep — no call site outside `data/achievements.ts`
  - `docs/buddy/reports/phases/phase-06-completion-report.md` line 37 — "Integrate achievement checking into main game loop"
- What is happening: Conditions/rewards exist but nothing evaluates them after care actions, level-ups, evolutions, or adventures.
- Why it matters: A headline feature (achievements with coin/item rewards) never fires; player retention and reward economy are absent.
- User / business impact: Players never receive achievement feedback or rewards.
- Security / privacy / reliability impact: Low; functional/reliability gap.
- Recommended fix: Evaluate `checkAchievements` after each state transition in `MainDevice.handleAction`, `AdventureScreen.handleAdventure`, and lifecycle updates; persist unlocked ids in `progression.achievements`; grant `rewardCoins`/`rewardItemId`.
- Suggested validation: Integration test: meet `bond_10` condition, assert achievement added and coins granted exactly once.
- Owner suggestion: gameplay
- Effort estimate: M
- Dependencies: DATA (persist unlocked achievements)
- Status: open

### Finding ID: FEAT-P1-002 - Lifecycle evolution and skill progression are not wired into the game loop

- Severity: P1
- Confidence: High
- Area: FEAT
- Evidence:
  - `lib/progression/lifecycle.ts` — `checkEvolution` line 55, `updateSkills` line 64
  - `lib/progression/lifecycle.test.ts` — only call sites
  - `components/device/MainDevice.tsx` line 12 imports `getStageName, getStageProgress`; `getStageProgress` unused
- What is happening: XP is gained and level rises, but `progression.lifecycle` stays `'baby'` and `skills` stay zero because evolution/skill functions are never called from care or adventure flows.
- Why it matters: The 6-stage lifecycle and 5 skills are core progression advertised in phase-06; they are non-functional.
- User / business impact: Progression feels broken; the pet never grows up.
- Security / privacy / reliability impact: Reliability/correctness.
- Recommended fix: After XP changes, call `checkEvolution` and update `progression.lifecycle`; call `updateSkills` on relevant actions (`train`, `talk`, exploring); persist results.
- Suggested validation: Test that XP ≥ 100 moves lifecycle `baby → child` in the live action path (not just the pure function).
- Owner suggestion: gameplay
- Effort estimate: M
- Dependencies: FEAT-P1-001 (shared state transition)
- Status: open

### Finding ID: FEAT-P2-001 - Item catalogue and economy are non-functional (no use, sell, or equip)

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `data/items.ts` — `sellValue`, `effect`, categories `food`/`medicine`/`toy`/`hat`/`skill_book`
  - `components/device/InventoryScreen.tsx` — renders items only; no actions
  - `data/achievements.ts::bond_100` — grants `rewardItemId: 'friendship_bracelet'` but no use path
- What is happening: Items accumulate from loot but cannot be consumed, sold, equipped, or used to train skills; `effect`/`sellValue` are dead data.
- Why it matters: The economy has no sink and loot has no purpose; balance data is inert.
- User / business impact: Shallow gameplay loop; no reason to collect.
- Security / privacy / reliability impact: Low; design/UX gap. (If server authority is added, item mutations become an anti-cheat surface.)
- Recommended fix: Add item actions (use food/medicine/toy, equip hats, consume skill books, sell for coins) with validation; update inventory on use.
- Suggested validation: Tests for each item category action and inventory decrement; sell updates coins by `sellValue`.
- Owner suggestion: gameplay
- Effort estimate: L
- Dependencies: FEAT-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Features appear complete but are inert | P1 | High | High | FEAT-P1-001/002 | wire or relabel |
| No economy sink | P2 | High | Medium | FEAT-P2-001 | item actions |
| Docs overclaim | P2 | High | Medium | FINAL-P2-001 | reconcile reports |

## Recommendations

### Immediate / Release Blocking
- Wire achievements + evolution, or explicitly mark them "planned" in docs/UI.

### This Week
- Decide and implement item use/sell/equip for at least hats/food.

### This Month
- Add memories/journal UI.

### Later / Platform Evolution
- Home customization, mini-games, seasonal events.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Call `checkAchievements` on action | activates rewards | `MainDevice.tsx`, `adventure.ts` | unit test |
| Apply `checkEvolution` on XP gain | activates growth | `care.ts`, `adventure.ts` | unit test |
| Remove unused `getStageProgress` import | hygiene | `MainDevice.tsx` | lint |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Achievement integration | P1 | gameplay | M | DATA |
| Evolution/skill integration | P1 | gameplay | M | DATA |
| Item economy | P2 | gameplay | L | FEAT-P1-001 |

## Suggested Tests

- Integration: achievement unlocked once, reward granted once.
- Integration: lifecycle transition through care/adventure path.
- Unit: item use decrements inventory and applies effect.

## Suggested Documentation Updates

- Reconcile phase-06/phase-07 reports with actual wiring status.
- Add a feature-status matrix to `README.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are achievements intended for v0.1? | scope of P1 fix | product decision |
| Is item use planned before release? | economy relevance | roadmap |

## Appendix

| Phase | Advertised | Actually wired |
|---|---|---|
| 01 Foundation | yes | yes |
| 02 Generation | yes | yes |
| 03 Hatch/Device | yes | yes |
| 04 Care loop | yes | yes |
| 05 Adventures/loot | yes | yes |
| 06 Lifecycle/skills/achievements | yes | **no** |
| 07 Inventory/economy | yes | **partial (display only)** |
| 08 PWA offline | yes | yes |
