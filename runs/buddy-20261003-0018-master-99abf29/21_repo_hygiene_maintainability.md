# Repository Hygiene and Maintainability Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: HYG
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/21_repo_hygiene_maintainability.md
- Scope limitations: Static review; no `node_modules`.

## Scope

Reviewed structural hygiene: dead/unused code, duplication, naming/consistency, docs/root files, formatting/lint enforcement, and generated-artifact management. Not reviewed: per-line style beyond ESLint config.

## Evidence Reviewed

- grep for unused exports: `startAutosave`, `exportSave`, `importSave`, `getSaveMetadata`, `checkAchievements`, `createMemory`, `checkEvolution`, `updateSkills`, `getStageProgress`, `DECOR_ITEMS`, `HAT_MAP`
- `lib/generation/hash.ts` vs `lib/generation/rng.ts` (`hashString` duplicated)
- `data/items.ts` line 8 (label typo)
- root files (no README/LICENSE/CHANGELOG)
- `package.json` scripts, `.eslintrc.json`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| unused-export grep | command | dead code | see findings |
| `hashString` grep | command | duplication | defined in 2 files |
| `data/items.ts` line 8 | code | consistency | `' celebration Cake'` |
| root file listing | command | docs | empty |
| `.prettierrc` check | command | formatting | only script, no config file? |

## Executive Summary

The codebase is **small and readable**, with strong naming and strict TypeScript, but it carries meaningful **dead/unwired code** and **missing project scaffolding**. At least nine exported functions/constants have no production call site (`startAutosave`, `exportSave`, `importSave`, `getSaveMetadata`, `checkAchievements`, `createMemory`, `checkEvolution`, `updateSkills`, `getStageProgress` import, `DECOR_ITEMS`, `HAT_MAP`), several of which correspond to the feature-integration gaps identified in FEAT. `hashString` is implemented twice with slightly different callers. There is no README, CHANGELOG, or CONTRIBUTING, and formatting/lint runs only manually. Content has a minor label typo (`' celebration Cake'` leading space). None of this is release-blocking on its own, but together it slows contributors and hides real gaps behind apparently finished modules.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Dead: autosave | `startAutosave`/`stopAutosave` | periodic save | Unused | Medium | also ARCH-P2-003 |
| Dead: storage | `exportSave`/`importSave`/`getSaveMetadata` | portability | Unused (no UI) | Medium | SEC/DATA |
| Dead: features | `checkAchievements`/`createMemory` | rewards | Unused | High | FEAT-P1-001 |
| Dead: progression | `checkEvolution`/`updateSkills` | growth | Unused | High | FEAT-P1-002 |
| Unused import | `getStageProgress` | display | Unused | Low | `MainDevice.tsx` |
| Unused const | `DECOR_ITEMS`, `HAT_MAP` | catalogues | Unused | Low | `data/` |
| Duplication | `hashString` | hashing | 2 copies | Medium | `hash.ts`, `rng.ts` |
| Content typo | `data/items.ts` line 8 | label | `' celebration Cake'` | Low | leading space |
| Root docs | README/CHANGELOG/CONTRIBUTING | onboarding | Absent | Medium | INV |
| Formatting | Prettier script | style | Manual | Low | no `.prettierrc`? |
| Docs weight | `docs/` 99 files | docs | Large | Low | INV-P3-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Naming/structure | 4 | clean `lib`/`app`/`components` | — | keep |
| Dead code | 1 | 9+ unused exports | accumulation | wire/remove |
| Duplication | 2 | duplicated `hashString` | small | consolidate |
| Root docs | 1 | none | onboarding | add |
| Formatting/lint gate | 2 | scripts only | not enforced | CI |
| Generated artifacts | 2 | `inventory.json` stale | drift | regenerate |
| Consistency | 3 | minor typo | — | fix |
| Dependency hygiene | 3 | lock committed | aged | SUPPLY |

## Detailed Review

### Item: Dead code
- Evidence: grep results above; `data/achievements.ts::checkAchievements`/`createMemory`, `lib/progression/lifecycle.ts::checkEvolution`/`updateSkills`, `lib/storage/*` helpers, `MainDevice.tsx` `getStageProgress` import, `data/items.ts::DECOR_ITEMS`, `data/hats.ts::HAT_MAP`.
- Risk: readers assume features work; reviewers miss the integration gap.

### Item: Duplicate hashing
- Evidence: `lib/generation/hash.ts::hashString` (lines 1–9) and `lib/generation/rng.ts::hashString` (lines 54–62) are near-identical.
- Risk: divergent behavior over time.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| HYG-001 | Dead/unwired code | grep | none | 9+ symbols | P2 | wire or delete |
| HYG-002 | Hash duplication | 2 files | none | duplicate | P2 | consolidate |
| HYG-003 | Root docs/consistency | listing; items.ts | none | missing/typo | P3 | add/fix |

## Findings

### Finding ID: HYG-P2-001 - Multiple exported functions and constants are defined but never used in production

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `lib/storage/autosave.ts` — `startAutosave`/`stopAutosave` (no caller)
  - `lib/storage/indexeddb.ts` — `exportSave` (line 79), `importSave` (86), `getSaveMetadata` (101) (no callers)
  - `data/achievements.ts` — `checkAchievements` (136), `createMemory` (127) (no callers)
  - `lib/progression/lifecycle.ts` — `checkEvolution` (55), `updateSkills` (64) (tests only)
  - `components/device/MainDevice.tsx` line 12 — `getStageProgress` imported, never used
  - `data/items.ts` — `DECOR_ITEMS`; `data/hats.ts` — `HAT_MAP` (no callers)
- What is happening: A large share of the API surface is unreferenced by the app.
- Why it matters: It obscures which features actually ship (FEAT-P1-001/002) and increases maintenance/security surface.
- User / business impact: Reviewers and users overestimate completeness.
- Security / privacy / reliability impact: Unmaintained code paths (e.g., unvalidated `importSave`) remain reachable only if someone adds UI later.
- Recommended fix: For each symbol: wire it (achievements/evolution) or delete it (autosave if unused, unused constants); remove unused imports. Track each decision in the patch plan.
- Suggested validation: ESLint `no-unused-vars` (including exports via `ts-prune`/`knip`) passes; features behave.
- Owner suggestion: maintainer
- Effort estimate: M
- Dependencies: FEAT-P1-001/002
- Status: open

### Finding ID: HYG-P2-002 - `hashString` is implemented twice with divergent callers

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `lib/generation/hash.ts` lines 1–9 — `hashString`
  - `lib/generation/rng.ts` lines 54–62 — an identical `hashString`
  - `lib/generation/engine.ts` imports `generateSeed`/`deriveSeeds` from `hash.ts`; `rng.ts` uses its private copy in `createRNG`
- What is happening: Two copies of the same hashing routine exist; only one is exported/shared.
- Why it matters: A future change to one copy can break determinism/seed consistency between generation and RNG.
- User / business impact: Potential non-deterministic pet generation regressions.
- Security / privacy / reliability impact: Reliability/determinism (a core design guarantee).
- Recommended fix: Delete the private copy in `rng.ts` and import `hashString` from `hash.ts`.
- Suggested validation: Existing determinism tests still pass; add a cross-module hash equality test.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: HYG-P3-001 - Content label typo and no enforced formatting/lint gate

- Severity: P3
- Confidence: High
- Area: HYG
- Evidence:
  - `data/items.ts` line 8 — `name: ' celebration Cake'` (leading space)
  - `package.json` — `format:check`/`lint` scripts exist but no CI runs them
- What is happening: A label ships with a stray leading space; formatting/lint is manual.
- Why it matters: Minor polish and consistency; style drift over time.
- User / business impact: Cosmetic.
- Security / privacy / reliability impact: None.
- Recommended fix: Fix the label; add a Prettier config and run lint/format:check in CI.
- Suggested validation: `npm run lint` and `npm run format:check` pass in CI.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: CI-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Hidden incompleteness | P2 | High | High | HYG-P2-001 | wire/delete |
| Determinism drift | P2 | Low | Medium | HYG-P2-002 | consolidate hash |
| Style drift | P3 | Medium | Low | HYG-P3-001 | CI lint/format |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Remove unused import/constants; consolidate `hashString`; fix typo.

### This Month
- Decide wire-vs-delete for each unused export and execute.

### Later / Platform Evolution
- Adopt `knip`/`ts-prune` to prevent dead-code accumulation.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Consolidate `hashString` | determinism | `rng.ts`, `hash.ts` | tests |
| Remove unused import/consts | clarity | `MainDevice.tsx`, `data/*` | lint |
| Fix item label | polish | `data/items.ts` | snapshot |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Wire/delete unused exports | P2 | maintainer | M | FEAT |
| Deduplicate hashing | P2 | maintainer | S | none |
| Lint/format in CI | P3 | maintainer | S | CI |

## Suggested Tests

- Determinism equality between `hash.ts` and former `rng.ts` copy (regression).
- `knip`/unused-export check in CI.

## Suggested Documentation Updates

- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which unused exports are intentional API? | wire vs delete | design decision |
| Is autosave planned? | dead vs missing wiring | ARCH-P2-003 |

## Appendix

Unused-export evidence (grep): `checkAchievements`, `createMemory`, `checkEvolution`, `updateSkills`, `startAutosave`, `exportSave`, `importSave`, `getSaveMetadata`, `DECOR_ITEMS`, `HAT_MAP`, and the `getStageProgress` import. All defined at HEAD; none referenced by `app/`/`components/` runtime code.
