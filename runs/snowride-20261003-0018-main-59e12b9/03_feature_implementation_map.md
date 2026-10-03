# 03 Feature Implementation Map

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Map declared product features to implementation and runtime activation: gameplay/scoring, social/party, economy, progression, creator courses, live events, and feature-flag state. Read-only.

## Evidence Reviewed

- `packages/game-core/src/*` (scoring, tricks, rating, progression, creatorCourse, launchReadiness, perfBudgets)
- `apps/realtime/src/{server.ts,social.ts,submissions.ts,raceLifecycle.ts,liveops.ts}`
- `apps/web/components/**` and `apps/web/lib/**`
- `apps/realtime/src/config.ts`, `.env.example`, `infra/compose/docker-compose.yml`
- `docs/product/*`, `docs/product/ADR_INDEX.md`

## Verification Performed

- Enumerated `EVENT_SCHEMAS` and server routes vs `docs/API.md`.
- Compared kill-switch defaults in `config.ts`/`.env.example` against the production compose environment.
- Confirmed `CourseEditor.tsx` and `LocalRide.tsx` exist (creator editor surface present).
- Confirmed `/launch-readiness` derives flag state from config only.

## Executive Summary

Feature coverage is broad and server-authoritative: deterministic scoring, ghost/replay handling, rating, progression, social/party, economy, creator courses, and live events all have code, tests and migrations. The main implementation-level concerns are configuration drift between the documented safe defaults and the production compose override (several features are forced live in production while the repo's default/`ground` documentation still says off), and an artifact-honesty issue in `/launch-readiness` where flags are reported `deployed: true` unconditionally. No major feature is missing from the code surface at this commit.

## Inventory

| Feature | Implementation evidence | Activation |
|---|---|---|
| Core gameplay/scoring | `packages/game-core/src/scoring.ts`, `mechanics.ts`, `SnowboardScene.ts` | always |
| Ghost/replay | `ghostCodec.ts`, `apps/realtime/src/replayStore.ts`, migration `0021` | always |
| Rating/seasons | `rating.ts`, migration `0015` | `RATING_MODE` |
| Progression/XP | `progression.ts`, migration `0016` | `PROGRESSION_MODE` |
| Social/party | `social.ts`, `social-guards.ts`, migration `0017` | always |
| Economy/shop | migrations `0003/0019/0030/0031`, `ShopPanel.tsx` | RPC-gated |
| Creator courses | `creatorCourse.ts`, `creatorEditor.ts`, migration `0020` | service-only submitter |
| Live events | `liveops.ts`, migration `0018` | `LIVEOPS_*` |
| Challenges | migration `0027`, `challengeService.ts` | always |
| Season pass | migration `0033`, `passService.ts` | always |

## Findings

### Finding ID: FEAT-P2-001 - Kill-switch defaults drift between repo documentation and production compose

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `apps/realtime/src/config.ts` — defaults: `TRICK_SCORING_MODE=off`, `AVALANCHE_MODE=off`, `MOVING_HAZARD_MODE=off`, `GEAR_MODE=off`
  - `.env.example` lines 50–55 — same "off" defaults
  - `infra/compose/docker-compose.yml` lines 93–94, 125, 128 — production forces `TRICK_SCORING_MODE=enforce`, `AVALANCHE_MODE=live`, `MOVING_HAZARD_MODE=live`, `GEAR_MODE=live`
- What is happening: Production runs scoring/hazard/gear features at their most impactful settings while the documented default is off.
- Why it matters: A reader/agent using config.ts or .env.example cannot predict production behaviour; rollback defaults are unclear.
- User / business impact: Mis-scoped testing and release decisions; unexpected gameplay-affecting changes.
- Security / privacy / reliability impact: Anti-cheat-affecting modes change verdicts.
- Recommended fix: Make compose the single documented source of production flag values (or a `compose.production.env`), and update `.env.example`/runbooks to state the production overrides explicitly.
- Suggested validation: A doc/CI check compares `config.ts` defaults + compose overrides and lists them.
- Owner suggestion: Realtime engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: FEAT-P3-001 - `/launch-readiness` reports flags as `deployed: true` unconditionally

- Severity: P3
- Confidence: High
- Area: FEAT
- Evidence:
  - `apps/realtime/src/server.ts` lines ~903–926 — each flag hardcodes `deployed: true`; only `activated` reads config
- What is happening: "deployed" is a static boolean, not derived from the image/migration/artifact set.
- Why it matters: The endpoint is used as a readiness view; a constant cannot detect an actually missing module.
- User / business impact: Low — operators may over-trust the view.
- Security / privacy / reliability impact: None identified.
- Recommended fix: Derive `deployed` from a build/version constant or remove the field and document `activated` only.
- Suggested validation: Unit test asserts `deployed` changes when a feature module is unbuilt/unwired.
- Owner suggestion: Realtime engineer
- Effort estimate: S
- Dependencies: None
- Status: open

## Risks

- R-FEAT-1: Production behavior diverges from documented defaults (P2).

## Recommendations

1. Consolidate production feature-flag values and document overrides (FEAT-P2-001).
2. Make readiness claims derived, not constant (FEAT-P3-001).

## Quick Wins

- Add a "production overrides" table to `docs/runbooks/KILL_SWITCHES.md`.

## Hardening Backlog

- Feature-flag inventory generated from config + compose with drift check.

## Suggested Tests

- Snapshot test of the effective boot config against a committed expected matrix.

## Suggested Documentation Updates

- `docs/runbooks/KILL_SWITCHES.md`, `AGENTS.md` environment section.

## Open Questions

- Which live modes are actually certified for ranked play vs stage-2 shadow? (`Unknown` — see `evidence/phase9/`.)

## Appendix

- Feature-to-migration crosswalk in `docs/source-pack/08-tests/GATE_MATRIX.md` (historical).
