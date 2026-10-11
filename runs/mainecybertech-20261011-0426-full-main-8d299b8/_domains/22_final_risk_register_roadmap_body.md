# Final Risk Register, Roadmap, and Patch Plan

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent `22_final_risk_register_roadmap` (area FINAL)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/22_final_risk_register_roadmap.md`
- Scope limitations: read-only static review. The **new** run's registers/roadmap are written by
  `tools/full_domain.py aggregate` from the per-domain payloads, so this domain audits the
  repository's **existing** register/roadmap/gate artifacts and records run-level aggregation
  observations; it does not re-aggregate the run. Live GitHub settings and production state are
  `unverified`.

## Scope

Reviewed at `8d299b8d`, read-only:

- `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/` — the published
  full-domain run copy: `INDEX.md`, `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`,
  `audit_manifest.json`, `findings.json`, `follow_up_register.md`, `risk_register.md`,
  `roadmap.md`, `patch_plan.md`, `lens_focused_security_supply_chain_ci.md`.
- `docs/audits/repo-deep-dive/20261004-0700-main-178b91c/` and
  `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/` — the other two committed run
  copies, used as contrast for what a complete roadmap/patch plan looks like.
- `docs/RELEASE_GATE.md` (the repository's operative pre-go-live gate), `docs/RELEASING.md`,
  `docs/RELEASE.md`.
- The previous run's `follow_up_register.md` FINAL rows (`FINAL-P1-001`, `FINAL-P2-001`,
  `FINAL-P2-002`) for the verification duty, re-checked against code at `8d299b8d`.

Not reviewed: re-auditing all 336 register findings (each owning domain re-verified its own rows
in this run); live branch protection, GitHub Environments, droplet state; the pack-side run copy
was consulted only as supporting evidence for staleness.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/audit_manifest.json` | Generated metadata | Machine-readable run state; carries the reconciled `releaseGate` | `:11` mode `full`; `:113` `"releaseGate": "NO-GO"`; `:115-167` 336 findings |
| `.../follow_up_register.md` / `risk_register.md` | Register (1:1 mirrored) | Authoritative per-finding status/owner/target/note | 336 rows; P0 6, P1 59, P2 166, P3 105 |
| `.../findings.json` | Generated findings | Machine copy of the register | 336 findings; counts match the register and manifest exactly |
| `.../INDEX.md`, `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md` | Generated companions | Reader-facing entry points | Not updated by any register-sync commit (stale) |
| `.../roadmap.md`, `.../patch_plan.md` | Generated plan artifacts | Required prompt-22 outputs | Flat list / 314 `TBD` placeholders |
| `docs/RELEASE_GATE.md` | In-repo gate | The repository's own consolidated go-live gate | Bound to a commit not reachable from any ref; decision table stale |
| `docs/RELEASING.md`, `docs/RELEASE.md` | Docs | Point at `RELEASE_GATE.md`; document the deploy gate | `RELEASING.md:137` names `RELEASE_GATE.md` the consolidated gate |
| `apps/worker/src/tasks/orphan-cleanup.ts`, `apps/worker/src/__tests__/orphan-cleanup.test.ts` | Source/tests | FINAL-P1-001 underlying P0 fix | Folder guard + regression tests present |
| `apps/api/src/lib/field-encryption.ts`, `apps/api/src/config/env.ts`, `apps/api/src/middleware/api-key.ts`, `apps/api/src/routes/search.ts` | Source | FINAL-P2-002 underlying controls | All now fail closed / implemented |
| `infra/terraform/digitalocean/providers.tf`, `.github/workflows/terraform-do.yml` | Config | CHAIN-P2-009 subject matter | TF 1.15.9 + `required_version >= 1.15` |

## Verification Performed

All commands were read-only against `/tmp/opencode/mct-audit-target` at `8d299b8d`.

| Command | Observed result |
|---|---|
| `git rev-parse HEAD` | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (Merge PR #168) |
| `git log --oneline -- docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/` | Publish `24857899` (2026-10-04) + sync `43604416` (2026-10-09) + 10+ register-only reconciliations through `7a8eb1ce` (2026-10-11) |
| `git show --stat 43604416` | Only `audit_manifest.json`, `findings.json`, `follow_up_register.md`, `risk_register.md` were synced |
| `git log -S "CHAIN-P1-008" -- .../follow_up_register.md` | First appears in `43604416`; the register has no `CHAIN-P1-003` row (`grep -c` = 0) |
| `grep -c '^TBD$' .../patch_plan.md` | 314 (every finding section is `TBD`); `grep -c 'PS-0'` = 0 |
| `grep -c '7-day\|30-day\|60-day\|90-day' .../roadmap.md` | 0; the file is a flat 338-line finding list |
| `grep -n 'CHAIN-P1-003' INDEX.md roadmap.md patch_plan.md` | `INDEX.md:37`, `roadmap.md:22`, `patch_plan.md:79` (stale ID) |
| `grep -n '"releaseGate"\|"mode"' .../audit_manifest.json` | `:113` `NO-GO`, `:11` `full`; `RELEASE_GATE.md:3` says `GO WITH CONDITIONS`, `INDEX.md:3` says "Focused security…" |
| `python3` register/json counters | 336 register rows = 336 findings.json = manifest total; byArea sums to 336; statuses: verified-fixed 159, partially-fixed 22, still-open 4, open 150, regressed 1 |
| `git merge-base --is-ancestor 2295958d HEAD`; `git rev-list --all \| grep -c 2295958d` | `false`; `0` — the commit `docs/RELEASE_GATE.md:4-5` is bound to is not in any local ref |
| `git log -1 --format='%h %ad %s' -- docs/RELEASE_GATE.md` | `c11f40ad` 2026-10-03 — untouched through the October reconciliation waves |
| `grep -n 'assertProductionSecrets\|assertProductionTurnstile' apps/api/src/config/env.ts` | Guards present (`:100-105`, `:85-90`) |
| `grep -n 'plain:\|throw' apps/api/src/lib/field-encryption.ts` | `:42-51` throws in production instead of writing `plain:` |
| `grep -n 'timingSafeEqual\|expires_at' apps/api/src/middleware/api-key.ts` | `:82-83` enforces `is_active`/`expires_at` + timing-safe compare |
| `grep -rn 'seed_demo' supabase/migrations/5302120_demo_module_data.sql` | `:27-28` demo seeding gated on `app.seed_demo` (default off) |
| `grep -n 'required_version\|use_lockfile' infra/terraform/digitalocean/providers.tf`; `grep -n 'terraform_version' .github/workflows/terraform-do.yml` | `>= 1.15` + `use_lockfile = true`; workflow pins `1.15.9` (`:52,215,255`) |
| `grep -n 'DATA-P0-001\|null.*id\|non-object' apps/worker/src/__tests__/orphan-cleanup.test.ts` | Regression tests at `:369-435` cover folder/null-id and non-object abort |
| `diff` published copy vs framework run copy (`runs/mainecybertech-20261004-full-main-9c0b88c`) | Same: findings.json, registers, manifest. Differ: INDEX, EXECUTIVE_SUMMARY, RELEASE_GATE, roadmap, patch_plan, lens |
| `grep -c '^TBD$'` on the other two committed run copies | `0` (20261004-0700 and 20261002-0344 both have real plans; the 20261002 copy has `PS-001…PS-015` and 7/30/60/90 windows) |

Headline-claim reproductions:

- "All P0s are `verified-fixed`" — **supported**: register P0 rows all `verified-fixed`; DATA-P0-001
  guard and its regression tests are present at `8d299b8d`.
- "The published run gate is NO-GO" — **unsupported for the published copy**: the manifest says
  `NO-GO`, but the committed `RELEASE_GATE.md` still says `GO WITH CONDITIONS`.
- "The patch plan is actionable" — **unsupported**: 314 `TBD` bodies, no `PS-` sets, no mapping table.
- "`docs/RELEASE_GATE.md` records the residual decisions" — **partially supported**: the decisions
  table exists (`:43-49`) but every row still reads `open` while the register/code say fixed.

## Executive Summary

The repository's register data is in good shape: the 336-row register, `findings.json`, and
`audit_manifest.json` were reconciled through 2026-10-11 and agree on every count and status. All
six P0 rows are `verified-fixed`; 48 of 59 P1 rows are `verified-fixed`; the 11 remaining P1 rows
are explicitly documented as partially fixed, operator-gated, or owner decisions.

The **plan and gate artifacts around that register did not follow**. The published run copy's
`RELEASE_GATE.md` says `GO WITH CONDITIONS` while its own manifest says `NO-GO`; `INDEX.md` still
describes a "Focused security / supply-chain / CI deep-dive" while the manifest says `full`; and
`INDEX.md`/`roadmap.md`/`patch_plan.md` still cite the pre-reconciliation ID `CHAIN-P1-003`, which
no longer exists in the register (renamed `CHAIN-P1-008`). `patch_plan.md` is a placeholder — all
314 finding bodies are `TBD` — and `roadmap.md` is a flat list with no 7/30/60/90-day sequencing.
The repository's own operative gate, `docs/RELEASE_GATE.md`, is bound to a commit that is not in
`main`'s history and still marks five controls `open` that are implemented and fail-closed in code.

Recommended next actions: (1) regenerate every companion artifact of the full run from the
reconciled register in one pass and add a consistency guard; (2) produce the missing patch sets
(`PS-00N` → findings → files → dependencies → effort → verification) from the register's
recommendations; (3) rebind and reconcile `docs/RELEASE_GATE.md`; (4) de-duplicate the register
rows that describe the same defect.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Register | `.../mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md` | Per-finding status ledger | Reconciled 2026-10-11; 336 rows | Low | Mirrored 1:1 with `risk_register.md` |
| Machine findings | `.../findings.json` | Machine-readable findings | Current; counts match register | Low | 336 findings, no duplicate IDs |
| Manifest | `.../audit_manifest.json` | Run metadata + gate | `releaseGate: NO-GO`, mode `full` | Medium | Contradicts `RELEASE_GATE.md`/`INDEX.md` in the same folder |
| Release gate (run) | `.../RELEASE_GATE.md` | Gate verdict | `GO WITH CONDITIONS` (stale) | Medium | Never updated after publish |
| Index / summary | `.../INDEX.md`, `.../EXECUTIVE_SUMMARY.md` | Entry points | Focused-run description; 5-line stub | Medium | Stale IDs; no verdict in summary |
| Roadmap | `.../roadmap.md` | Remediation sequencing | Flat list, no windows | Medium | No quick wins/themes/owners |
| Patch plan | `.../patch_plan.md` | Patch sets + mapping | 314 `TBD` bodies; no `PS-` sets | Medium | Required prompt-22 output missing |
| In-repo gate | `docs/RELEASE_GATE.md` | Pre-go-live gate | Bound to unreachable `2295958d`; decisions `open` | Medium | `RELEASING.md:137` points at it |
| Contrast plans | `.../20261002-0344-develop-6286137/{roadmap,patch_plan}.md` | Earlier run's plan | Real `PS-001…PS-015`, windows, mapping table | — | Shows the expected shape |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| All previous reports | 4 | 336 findings reconciled with provenance notes (`follow_up_register.md`); P0/P1 re-verified | Published folder ships one report; companions stale | Republish companions from the register |
| P0/P1 risks | 4 | 6/6 P0 verified-fixed; 48/59 P1 verified-fixed; 11 residuals documented | Operator-gated rows (CI-P1-001/003) have no dated artifact | Record operator artifacts when provisioned |
| Duplicate findings | 2 | DR-P1-002 ≡ IR-P1-005 (identical evidence); WH-P1-001 ≈ API-P2-005; SECRET-P1-001 ≈ WH-P1-002; AI-P1-002 ≈ TEST-P2-001 | Duplicates inflate P1/P2 counts; no merge pass | Merge into one row each, keep provenance in the note |
| Cross-cutting themes | 3 | 10 CHAIN rows carry composed paths | No consolidated theme/cluster section in the final artifacts | Add a themes section to the roadmap |
| Quick wins | 1 | No quick-win list anywhere in the published plan | Missing deliverable | Derive from P3 verified-fixed rows |
| 7/30/60/90-day plans | 1 | `roadmap.md` is a flat list (grep for windows = 0) | Missing deliverable | Sequence by severity/owner; 20261002 copy shows the shape |
| Patch sets | 1 | `patch_plan.md` all `TBD`; 0 `PS-` IDs | Missing deliverable | Generate `PS-00N` sets + mapping table |
| Validation commands | 2 | Register notes carry evidence but no runnable commands; no patch-set verification commands | Missing per-set commands | Add the command per patch set (as the 20261002 copy does) |
| Owners/effort/dependencies | 3 | Owner + target columns per row | No effort estimates or dependencies | Add effort (`S/M/L`) and dependency notes |
| Accepted/deferred risks | 3 | Operator-gated and owner-decision rows documented; `docs/RELEASE_GATE.md` decisions table exists | Decisions table stale (`open` for fixed controls); no `owner-accepted` status used | Reconcile the decisions table |

## Detailed Review

### Item: Published full-run companion set

- Evidence: `RELEASE_GATE.md:3`; `audit_manifest.json:11,113`; `INDEX.md:3,37`; `EXECUTIVE_SUMMARY.md:1-5`;
  commit history (`24857899`, `43604416`, `d15c9d40`, `7a8eb1ce`).
- What it does: entry-point artifacts for the published full run.
- How it appears to work: they were generated at publish time (2026-10-04) and never regenerated;
  later sync commits touched only the register trio + manifest.
- Dependencies: the register/findings data.
- Current controls: none; `tools/check_run.sh` validates registers against the manifest but not the
  companions' verdicts/IDs.
- Missing controls: a consistency guard (`manifest.releaseGate` == gate verdict; every companion ID
  ∈ findings.json; mode description matches manifest).
- Risks: a reader (or agent) opening `RELEASE_GATE.md` gets a different verdict than the manifest;
  roadmap/patch-plan IDs cannot be mapped to register rows.
- Recommended improvement: regenerate all companions from the reconciled register in one pass.
- Suggested tests: a CI/script check comparing gate verdicts and ID sets.
- Suggested docs: a "generated artifacts" note in `docs/audits/README.md` (owned by ORCH domain).

### Item: patch_plan.md

- Evidence: `patch_plan.md:1` (`# Patch plan`), `:5` first `TBD`; 314 `^TBD$` lines; 0 `PS-` IDs;
  contrast `20261002-0344-develop-6286137/patch_plan.md:155-159` (mapping table with files,
  dependencies, effort, verification commands).
- What it does: should carry patch sets, grouping rules, dependency graph, and a mapping table.
- How it appears to work: `tools/full_domain.py` falls back to `TBD` when a finding has no
  `recommendation`; the imported rows carried none, and no FINAL pass filled them.
- Dependencies: per-finding `recommendation` fields.
- Current controls: none.
- Missing controls: patch-set grouping (every finding in exactly one set; P0-only set with no
  dependencies; 3+ file fixes get their own set) and per-set verification commands.
- Risks: implementation agents cannot start scoped PRs from the run; the run's promised remediation
  deliverable is absent.
- Recommended improvement: generate the patch sets from the register (see Recommendations).
- Suggested tests: a plan-lint that every finding appears in exactly one patch set and each set has
  a verification command.
- Suggested docs: none.

### Item: roadmap.md

- Evidence: `roadmap.md:1-338` — one bullet per finding, no phases, owners, effort, quick wins, or
  themes; `20261002-0344-develop-6286137/roadmap.md:3` states the 7/30/60/90-day contract.
- What it does: should sequence remediation into 7/30/60/90-day windows mapped to patch sets.
- Current state: flat list (aggregator default), never enriched.
- Risks: no owner-facing sequencing; P0/P1/P2 work is not prioritized for delivery.
- Recommended improvement: sequence by severity/owner with quick wins and cross-cutting themes.

### Item: docs/RELEASE_GATE.md (in-repo gate)

- Evidence: `:3-5` bound to run `20261003-0018-fix-p2-batch-31` at `2295958d` (not an ancestor;
  unreachable from any ref); last modified `c11f40ad` (2026-10-03); `:43-49` all five fail-closed
  decisions `open`; `docs/RELEASING.md:137` names it the consolidated gate.
- What it does: consolidates exit criteria, fail-closed decisions, and the operator checklist.
- How it appears to work: it was correct for its own run at 2026-10-03, then drifted; the code
  moved on (field encryption, Turnstile, search scoping, API keys, demo seeding all fixed) without
  the doc being rebound.
- Current controls: none; nothing checks the gate against the register.
- Missing controls: commit binding validation; a stale-gate guard.
- Risks: release decisions read a gate whose blockers no longer exist while its binding commit is
  absent from `main`'s history; the full-run register's FINAL-P2-002 note points at this stale doc
  as the residual-decision record.
- Recommended improvement: rebind to the current run/commit and reconcile the five decision rows
  against code + register (or mark the file historical and point at the current register).
- Suggested tests: a docs check that the gate's commit resolves from `main`.
- Suggested docs: update `docs/RELEASE_GATE.md`; keep `RELEASING.md:136-137` in sync.

### Item: follow_up_register.md / risk_register.md

- Evidence: 336 rows; statuses verified-fixed 159 / partially-fixed 22 / still-open 4 / open 150 /
  regressed 1; ~140 rows say "Carried from full run 20261002 …; not re-verified at main 9c0b88c".
- What it does: authoritative per-finding ledger with provenance notes.
- Strengths: counts reconcile across register, `findings.json`, manifest, INDEX and summary; no
  duplicate IDs; reconciliation history is auditable in git.
- Gaps: duplicate rows not merged; `CHAIN-P2-009` stays `regressed` while its underlying cause
  (INFRA-P1-002) is `verified-fixed` — the CHAIN domain re-verified it as `partially-fixed` in this
  run, so the new register supersedes it; ~140 rows carried unverified from a different branch/commit.
- Recommended improvement: merge duplicates, and re-verify or explicitly date-box carried rows.

### Item: other committed run copies (contrast)

- Evidence: `20261002-0344-develop-6286137/patch_plan.md` (`PS-001…PS-015`, grouping rules,
  dependency graph, mapping table) and `roadmap.md:3` (7/30/60/90 windows); `20261004-0700-main-178b91c`
  gate verdict `GO` consistent with P0 x0/P1 x0.
- Conclusion: the full run's plan artifacts are the outlier, not the norm.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FINAL-001 | All previous reports | 336-row register + findings.json + manifest agree | Reconciliation + provenance notes | Companions stale | P2 | Regenerate companions from the register |
| FINAL-002 | P0/P1 risks | 6/6 P0 and 48/59 P1 verified-fixed; 11 residuals documented | Register statuses + notes | Operator-gated rows lack dated artifacts | P2 | Record operator artifacts on closure |
| FINAL-003 | Duplicate findings | DR-P1-002 ≡ IR-P1-005 etc. | Cross-references in notes only | No merge | P3 | Merge rows; keep provenance |
| FINAL-004 | Cross-cutting themes | 10 CHAIN rows | Chain findings exist | No themes section | P3 | Add themes to the roadmap |
| FINAL-005 | Quick wins | none in published plan | — | Missing | P3 | Derive from P3 verified-fixed rows |
| FINAL-006 | 7/30/60/90-day plans | roadmap is flat | — | Missing | P2 | Sequence work into windows |
| FINAL-007 | Patch sets | patch_plan all `TBD` | — | Missing | P2 | Generate `PS-00N` + mapping table |
| FINAL-008 | Validation commands | none in plan | Register notes carry evidence | No runnable commands | P2 | Add per-set verification commands |
| FINAL-009 | Owners/effort/dependencies | owner+target columns | Per-row owners | No effort/dependencies | P3 | Add `S/M/L` + dependencies |
| FINAL-010 | Accepted/deferred risks | `docs/RELEASE_GATE.md:43-49` | Decisions table | Stale rows; no `owner-accepted` | P2 | Reconcile the decisions table |

## Findings

| Severity | Status | Title |
|---|---|---|
| P1 | verified-fixed | P0 data-loss path and unverified "fixed" claim block a clean release *(previous FINAL row, re-verified)* |
| P2 | partially-fixed | Governance and observability gaps mean the platform cannot yet detect or control production failure *(previous FINAL row, re-verified)* |
| P2 | partially-fixed | Residual authorization/secret defaults need explicit decisions *(previous FINAL row, re-verified)* |
| P2 | open | The full run's patch plan is a placeholder and the roadmap has no 7/30/60/90-day sequencing |
| P2 | open | Release-gate artifacts contradict the reconciled register (published gate says GO WITH CONDITIONS vs manifest NO-GO; in-repo gate doc is stale and mis-bound) |
| P3 | open | Register retains duplicate findings and carried-unverified rows without a merge/refresh pass |

Detail (IDs are assigned by `tools/full_domain.py`; see the findings table rendered above this body):

1. **P0 data-loss path and unverified "fixed" claim block a clean release** — verified-fixed at
   `8d299b8d`: `apps/worker/src/tasks/orphan-cleanup.ts:221-231` refuses to remove non-object paths;
   regression tests `apps/worker/src/__tests__/orphan-cleanup.test.ts:369-435`; all six P0 register
   rows remain verified-fixed. Caveat recorded in the gate finding below.
2. **Governance and observability gaps …** — partially-fixed: alert delivery improved (ntfy routing,
   PRs #154/#157; register DR-P2-001 "delivery verified end-to-end"), but the exit conditions in
   `docs/RELEASE_GATE.md:33-36` remain unmet/unverified — CI-P1-001/CI-P1-003 are `still-open`
   (operator provisioning) and OBS-P2-003 is `partially-fixed` (no dated green restore drill).
3. **Residual authorization/secret defaults need explicit decisions** — partially-fixed: every
   fail-open control now fails closed in code (`field-encryption.ts:42-51`, `env.ts:85-90,100-105`,
   `search.ts:97-150`, `api-key.ts:82-83`, demo seeding gated), but the decision record
   (`docs/RELEASE_GATE.md:43-49`) still marks all five `open` and API-P2-001 remains open.
4. **Patch plan placeholder** — `patch_plan.md` (314 `TBD`), no `PS-` sets/mapping table;
   `roadmap.md` has no windows/quick wins/themes.
5. **Gate artifacts contradict the register** — `RELEASE_GATE.md:3` vs `audit_manifest.json:113`;
   `docs/RELEASE_GATE.md` bound to unreachable `2295958d` and stale decisions.
6. **Register hygiene** — duplicate pairs and ~140 carried-unverified rows; `CHAIN-P2-009` stale
   `regressed` (superseded by this run's CHAIN row).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Release decision made from a contradictory gate artifact | P2 | Medium | Wrong go/no-go framing | `RELEASE_GATE.md:3` vs `audit_manifest.json:113` | Regenerate companions; add guard |
| Remediation cannot start from the run's plan | P2 | High | Lost implementation time | `patch_plan.md` 314 `TBD` | Generate patch sets |
| Stale in-repo gate misdirects the go-live checklist | P2 | Medium | Re-litigating closed items / missing open ones | `docs/RELEASE_GATE.md:43-49` | Rebind + reconcile |
| Count inflation from duplicate rows | P3 | High | Slightly overstated P1/P2 totals | `follow_up_register.md:39,54,72,94` | Merge duplicates |

## Recommendations

### Immediate / Release Blocking

None from this domain — no P0 is open. The contradictions below are release-*governance* blockers,
not code blockers.

### This Week

1. Regenerate `RELEASE_GATE.md`, `EXECUTIVE_SUMMARY.md`, `INDEX.md`, `roadmap.md`, `patch_plan.md`
   for the published full run from the reconciled register + manifest (single generation pass), and
   add a guard that `manifest.releaseGate` equals the gate verdict and every companion ID resolves
   in `findings.json`.
2. Rebind `docs/RELEASE_GATE.md` to a reachable commit and reconcile its five decision rows against
   the register/code (mark fixed rows fixed; keep operator items open).

### This Month

3. Generate the patch sets: `PS-00N` → findings → files → dependencies → effort → verification
   command; P0-only immediate set with no dependencies; 3+ file fixes get their own set; every
   finding in exactly one set.
4. Add the 7/30/60/90-day sequencing, quick wins, and cross-cutting themes to the roadmap.
5. Merge duplicate register rows and re-verify (or date-box) the ~140 carried-unverified rows.

### Later / Platform Evolution

6. Make the run-consistency guard part of `tools/check_run.sh`/CI so future reconciliations cannot
   leave companions stale (register-sync commits should regenerate companions atomically).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Re-run `tools/full_domain.py aggregate` for the published run | Regenerates gate/summary/index/roadmap/patch plan from the reconciled register | `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/` | `diff` companions; gate verdict matches manifest |
| Fix `RELEASE_GATE.md` verdict string | Removes the most visible contradiction | `.../RELEASE_GATE.md` | `grep Verdict` == manifest `releaseGate` |
| Merge the two identical duplicate rows | Removes count inflation with zero code risk | `follow_up_register.md`, `risk_register.md`, `findings.json` | Register row count drops by 1; `check_run.sh` PASS |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Companion-artifact regeneration + guard | P2 | audit owner | M | none |
| Patch-set generation (`PS-00N` + mapping) | P2 | audit owner / implementation lead | M | register recommendations |
| `docs/RELEASE_GATE.md` rebind + reconcile | P2 | release owner + security/API | S | none |
| Duplicate merge + carried-row refresh | P3 | audit owner | M | owning domains |

## Suggested Tests

- Run-level consistency script: `manifest.releaseGate == RELEASE_GATE verdict`; every ID in
  `INDEX.md`/`roadmap.md`/`patch_plan.md` exists in `findings.json`; every finding appears in exactly
  one patch set.
- Docs binding check: `git merge-base --is-ancestor <commit in docs/RELEASE_GATE.md> HEAD`.
- Register integrity: duplicate-title/duplicate-evidence detector (e.g., exact-note equality already
  catches DR-P1-002 ≡ IR-P1-005).

## Suggested Documentation Updates

- `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/{RELEASE_GATE,EXECUTIVE_SUMMARY,INDEX,roadmap,patch_plan}.md` — regenerate.
- `docs/RELEASE_GATE.md` — rebind and reconcile; add a "superseded by" pointer when replaced.
- `docs/audits/README.md` — note that companions are generated artifacts and must be regenerated
  when the register is reconciled (also flagged by the ORCH domain).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which gate is authoritative for the next release decision — the published run copy or `docs/RELEASE_GATE.md`? | They disagree (GO WITH CONDITIONS vs NO-GO; open vs fixed) | Owner decision recorded in a doc/issue |
| Were the ~140 carried-unverified rows ever re-checked at `main`? | Their statuses drive P2/P3 counts | Re-verification notes at 8d299b8d |
| Are duplicate rows intentional (per-domain provenance) or should they be merged? | Counts and gate framing | Owner/audit-owner decision |

## Appendix

### Run-level aggregation observations (for `tools/full_domain.py aggregate`)

- **Counts reconcile.** 336 findings = register rows = `findings.json` = manifest `bySeverity` =
  INDEX/summary counts; `byArea` sums to 336. No duplicate IDs in `findings.json`.
- **Status distribution** (previous run): verified-fixed 159, partially-fixed 22, still-open 4,
  open 150, regressed 1. P0 6/6 verified-fixed. P1: 48 verified-fixed, 7 partially-fixed,
  2 still-open (CI-P1-001, CI-P1-003), 2 open (DATA-P1-003, IR-P1-006).
- **Do not repeat the pack-side note verbatim.** The framework copy's `RELEASE_GATE.md` states "the
  only open P1 in the authoritative ledger is CI-P1-001"; the register actually has 11 P1 rows not
  `verified-fixed` (2 `open`, 2 `still-open`, 7 `partially-fixed`). If the new run's gate text
  repeats this phrasing, it will be wrong.
- **Duplicate pairs to consider merging in the new register:** webhook idempotency
  (WH-P1-001 ≈ API-P2-005), M365 auth/secret (SECRET-P1-001 ≈ WH-P1-002), backup-bucket contract
  (DR-P1-002 ≡ IR-P1-005), a11y gate-size docs (AI-P1-002 ≈ TEST-P2-001). The new run's payloads
  contain the same overlaps across domains (e.g., "No runtime detection … RLS regressions" appears
  in domains 14 and 37; SBOM/image-attestation findings repeat across 11, 35, 36).
- **Patch plan needs `recommendation` fields.** `tools/full_domain.py` writes `TBD` for findings
  without a `recommendation`; every payload in this run carries one, so the new patch plan should be
  non-empty — verify after aggregation.
- **Carried rows.** ~140 rows were imported from the `20261002-0344` develop run and marked "not
  re-verified"; the new run re-verifies them per domain, so the new register should supersede them
  with current statuses rather than carrying them forward.
- **Superseded rows.** `CHAIN-P2-009` (`regressed`) is re-verified `partially-fixed` by this run's
  CHAIN domain; the new aggregation should use the new status.
