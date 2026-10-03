# Final Risk Register, Roadmap, and Patch Plan

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: FINAL
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/22_final_risk_register_roadmap.md
- Scope limitations: Aggregates the 13 domain reports in this run. No live system; dependency advisories unverified offline.

## Scope

Aggregated all findings from reports 01, 02, 03, 06, 07, 08, 09, 10, 11, 14, 21, plus the executive report. Produced consolidated risk register, roadmap, patch plan, validation plan, and definition of done. Companion files: `risk_register.md`, `roadmap.md`, `patch_plan.md`.

## Evidence Reviewed

All run reports in this folder; source evidence cited within them.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| finding IDs across reports | aggregate | counts | 40 findings, 0 P0 |
| phase reports | docs | claim consistency | claim "None" P0/P1 vs this run |
| test count grep | command | claim sampling | 109 supported |

## Executive Summary

Across the domain reports, `buddy` has **0 P0, 11 P1, 24 P2, and 5 P3** findings. There is **no critical security or data-exposure issue** because the app is a guest-only, offline, client-side game with no server, accounts, or remote tenant data. The P1s cluster into five themes: (1) **release governance** (no CI, no license, branch protection unverified), (2) **core feature integration** (achievements, evolution, and skills are unwired; item economy inert), (3) **data integrity** (save version downgrade, no runtime validation), (4) **client-authoritative/dependency risk** (no server authority for future account mode; aged deps), and (5) **state correctness** (adventure/device desync). Several P1s are small (add CI, add LICENSE, align save version, restore guestId).

This is a healthy **0.1.0-rc hobby/indie codebase** that is close to a clean "GO WITH CONDITIONS" once governance and the P1 integration/data bugs are addressed. The repo's own phase reports asserting "None" P0/P1 are **self-inconsistent** with this audit: they under-report the unwired features and save bugs.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Risk register | `risk_register.md` | consolidated risks | new | — | this run |
| Roadmap | `roadmap.md` | 7/30/60/90 | new | — | this run |
| Patch plan | `patch_plan.md` | PS-00N mapping | new | — | this run |
| Gate | `RELEASE_GATE.md` | decision | new | — | GO WITH CONDITIONS |
| Exec summary | `EXECUTIVE_SUMMARY.md` | leadership view | new | — | this run |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| All previous reports | 4 | 13 reports | — | keep |
| P0/P1 risks | 2 | 0 P0, 11 P1 | unaddressed P1 | patch plan |
| Duplicate findings | 3 | cross-referenced | some overlap | merged |
| Cross-cutting themes | 4 | 5 themes | — | roadmap |
| Quick wins | 4 | several S-effort | — | do first |
| 7/30/60/90-day plans | 3 | defined | not executed | track |
| Patch sets | 3 | PS-01..PS-08 | not executed | assign owners |
| Validation commands | 3 | defined | no CI | CI-P1-001 |
| Owners/effort/dependencies | 4 | per finding | — | — |
| Accepted/deferred risks | 2 | none recorded | needs owner sign-off | FINAL-P2-002 |

## Detailed Review

### Item: Cross-cutting themes
1. **No automation/governance** — CI, branch protection, license, SBOM.
2. **Half-wired product** — achievements/evolution/skills/items.
3. **Save integrity** — version, validation, identity.
4. **Client authority & aging deps** — future account/premium risk.
5. **Missing operational signals & docs** — error tracking, README.

### Item: Duplicate/merged findings
- Identity issues appear as ARCH-P2-002 and SEC-P3-001 → merged into PS-03.
- `importSave` validation appears as SEC-P2-001 and DATA-P1-002 → merged into PS-04.
- Autosave dead code appears as ARCH-P2-003 and HYG-P2-001 → merged into PS-05.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FINAL-001 | Release process | `git tag`, no CI | manual tag | no bound artifacts | P1 | PS-01 |
| FINAL-002 | Report accuracy | phase reports | manual claims | under-report P1 | P2 | reconcile |
| FINAL-003 | Risk ownership | no register before | none | no acceptance | P2 | record sign-off |

## Findings

### Finding ID: FINAL-P1-001 - No release/versioning process binds artifacts to a commit

- Severity: P1
- Confidence: High
- Area: FINAL
- Evidence:
  - `git tag` → `v0.1.0-rc1` (single tag, created manually)
  - no `.github/workflows` (no release job, no SBOM, no provenance)
  - `package.json` version `0.1.0`; runtime string hardcoded `BUDDY v0.1`
- What is happening: Releases are manual tags with no automated build/test/artifact/attestation and no runtime build id.
- Why it matters: Cannot prove what commit a shipped artifact came from; rollback/triage is guesswork.
- User / business impact: Release integrity and support cost.
- Security / privacy / reliability impact: Supply-chain/release integrity.
- Recommended fix: Add a tag-driven release workflow (build + test + SBOM + changelog + build id) per SUPPLY-P2-002 and OBS-P3-001.
- Suggested validation: Dry-run a release tag and verify artifacts/attestation/business.
- Owner suggestion: maintainer/DevOps
- Effort estimate: M
- Dependencies: CI-P1-001
- Status: open

### Finding ID: FINAL-P2-001 - Phase completion reports claim "None" P0/P1 while this audit finds unresolved P1s

- Severity: P2
- Confidence: High
- Area: FINAL
- Evidence:
  - `docs/buddy/reports/phases/phase-05-completion-report.md` line 43 — "P0/P1/P2/P3 Issues: None"
  - `phase-06-completion-report.md` line 37 — lists achievement integration as remaining work, yet reports no P1
  - This run — FEAT-P1-001/002, DATA-P1-001/002, ARCH-P1-002, CI-P1-001
- What is happening: Phase reports self-report no P0/P1 issues while the code has unwired features, save-version bugs, and no CI.
- Why it matters: Status artifacts contradict their sources; downstream readers over-trust them.
- User / business impact: Misinformed release decisions.
- Security / privacy / reliability impact: Governance/verification integrity.
- Recommended fix: Update phase reports (or add an addendum) to reflect integration/save/CI gaps and reference this audit's findings; add a status matrix.
- Suggested validation: Cross-check each report claim against code; reconcile counts.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: FINAL-P2-002 - No accepted/deferred-risk record or owner sign-off

- Severity: P2
- Confidence: High
- Area: FINAL
- Evidence:
  - No risk register existed before this run (`risk_register.md` is new)
  - No SECURITY/ADR/decision records in repo
- What is happening: There is no place to record risks that are knowingly accepted or deferred, or who owns them.
- Why it matters: Unresolved P1s could be silently ignored; accountability is unclear.
- User / business impact: Risk of shipping known gaps.
- Security / privacy / reliability impact: Governance.
- Recommended fix: Adopt the generated `risk_register.md`, mark accepted/deferred rows with owner + date, and review per release.
- Suggested validation: Risk register updated with owner/status for each open P1/P2.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unbound releases | P1 | High | High | FINAL-P1-001 | release workflow |
| Misleading status docs | P2 | High | Medium | FINAL-P2-001 | reconcile |
| No risk ownership | P2 | Medium | Medium | FINAL-P2-002 | adopt register |

## Recommendations

### Immediate / Release Blocking
- PS-01 (CI) and PS-02 (LICENSE) before a non-RC release.
- PS-03/PS-04 (state + save integrity) before advertising progression.

### This Week
- PS-05 dead-code decisions; PS-06 observability basics.

### This Month
- PS-07 dependency/SBOM upgrade program.

### Later / Platform Evolution
- PS-08 server authority before account/cloud mode.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| CI workflow | gate | `.github/workflows/ci.yml` | failing PR |
| LICENSE | legal | `LICENSE` | detection |
| Save version constant | integrity | `indexeddb.ts` | unit test |
| Restore guestId | identity | `app/page.tsx` | reload test |
| Error boundary | crash recovery | `app/error.tsx` | test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| CI + branch protection | P1 | maintainer | S | none |
| LICENSE | P1 | legal | S | none |
| Feature integration | P1 | gameplay | M | none |
| Save integrity | P1 | frontend | M | none |
| Server authority | P1 (future) | backend | L | product decision |
| Dependency program | P2 | DevSecOps | M | CI |

## Suggested Tests

See each domain report. Cross-cutting: CI gate; save migration/validation; component state sync; E2E smoke hatch→care→adventure→reload.

## Suggested Documentation Updates

`README.md`, `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, `docs/data-model.md`, `docs/testing.md`, `docs/observability.md`, reconciled phase reports.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is this a public OSS release or private product? | license/CI urgency | product decision |
| Account/Supabase still planned? | P1 future scope | roadmap |
| Is autosave intended? | dead vs missing | design |

## Appendix

### Consolidated risk table (P1)

| ID | Title | Theme | Effort |
|---|---|---|---|
| ARCH-P1-001 | Client-authoritative, no server boundary | authority | L |
| ARCH-P1-002 | Adventure/device state desync | correctness | M |
| FEAT-P1-001 | Achievements unwired | integration | M |
| FEAT-P1-002 | Evolution/skills unwired | integration | M |
| DATA-P1-001 | Save version downgrade | integrity | S |
| DATA-P1-002 | No runtime save validation | integrity | M |
| CI-P1-001 | No CI | governance | S |
| CI-P1-002 | Branch protection unverified | governance | S |
| SUPPLY-P1-001 | No LICENSE | legal | S |
| FINAL-P1-001 | No bound release process | governance | M |
| EXEC-P1-001 | P1 blockers preclude plain GO | summary | — |

### Patch-set mapping

| Set | Findings | Files | Deps | Effort | Verify |
|---|---|---|---|---|---|
| PS-01 CI | CI-P1-001, CI-P1-002, TEST-P3-001, HYG-P3-001 | `.github/workflows/ci.yml`, `.github/dependabot.yml`, configs | none | S | failing PR blocked |
| PS-02 Legal | SUPPLY-P1-001, SUPPLY-P2-003 | `LICENSE`, `NOTICE`, `docs/README.md` | none | S | license detected |
| PS-03 Identity/state | ARCH-P1-002, ARCH-P2-002, SEC-P3-001 | `MainDevice.tsx`, `AdventureScreen.tsx`, `app/page.tsx`, `store.ts` | none | M | component/reload tests |
| PS-04 Save integrity | DATA-P1-001, DATA-P1-002, DATA-P2-001, SEC-P2-001 | `indexeddb.ts`, new `lib/storage/schema.ts` | none | M | fuzz/migration tests |
| PS-05 Hygiene | ARCH-P2-003, HYG-P2-001, HYG-P2-002, HYG-P3-001 | `autosave.ts`, `rng.ts`, `hash.ts`, `items.ts`, `MainDevice.tsx` | PS-03 | S | lint/unused checks |
| PS-06 Feature wiring | FEAT-P1-001, FEAT-P1-002, FEAT-P2-001 | `care.ts`, `adventure.ts`, `MainDevice.tsx`, `InventoryScreen.tsx` | PS-04 | M | integration tests |
| PS-07 Ops/privacy | OBS-P2-001, OBS-P2-002, OBS-P3-001, API-P2-002, SEC-P2-002 | `app/error.tsx`, `next.config.js`, fonts | PS-01 | M | error/header tests |
| PS-08 Supply/upgrades | SUPPLY-P2-001, SUPPLY-P2-002, INV-P2-002 | `package.json`, deps, inventory | PS-01 | M | audit/SBOM |
| PS-09 Docs | INV-P2-001, INV-P3-001, FINAL-P2-001, FINAL-P2-002 | `README.md`, phase reports, register | none | S | link/claim checks |
