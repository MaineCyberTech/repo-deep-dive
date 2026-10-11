# Audit Orchestrator

## Audit Metadata

- Audit name: `repo-deep-dive` (profile `base`)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` — read-only worktree `/tmp/opencode/mct-audit-target`
- Branch: `main`
- Commit SHA: `8d299b8d` (merge of PR #168, "promote develop to main (metrics scrape fixes + register sync)")
- Generated at: 2026-10-11 (UTC)
- Auditor: `00_audit_orchestrator` subagent (area ORCH); read-only, no installs/builds/tests, no lab/network
- Area code: `ORCH`
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/00_audit_orchestrator.md`
- Scope limitations: this domain audits the **audit process and its artifacts**, not application behavior
  (other domains own that). Live GitHub settings (branch protection, environment reviewers) are
  `unverified` — not reachable read-only. This run's own finals (`INDEX.md`, registers, `EXECUTIVE_SUMMARY.md`,
  `RELEASE_GATE.md`) are rendered by `tools/full_domain.py aggregate` after the domain fan-out; the copies
  on disk at audit time are the scaffold state.

## Scope

Reviewed (all at `8d299b8d`):

- The repository's committed audit corpus under `docs/audits/` (3 `repo-deep-dive` runs, the
  comprehensive/ui-ux runs, `docs/audits/README.md`, `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md`).
- The vendored audit prompt pack `prompts/repo-deep-dive/` (prompts, `RUN_ORDER.md`, `README.md`,
  `MASTER_RUNNER_FULL_HARDENING.md`, templates, examples) and its provenance/pinning machinery
  (`prompts/PROVENANCE.md`, `prompts/manifest.json`, `scripts/verify-prompts.js`).
- Do-not-touch / agent guardrails: `AGENTS.md` (mirrored as `review.md`), `prompts/PROVENANCE.md`,
  CI guards in `.github/workflows/validate.yml`.
- The audit framework side of this rerun: `tools/full_domain.py` (init/emit/aggregate), `tools/lib_findings.py`,
  `tools/check_run.sh`, `tools/publish_audit.py`, `REFERENCE_CARD.md`, `runbooks/POST_AUDIT_PIPELINE.md`,
  `runbooks/OPERATOR_QUICKSTART.md`, and this run's scaffold (`audit_manifest.json`, `INDEX.md`, `coverage.md`,
  `_domains/deterministic.json`).

Not reviewed: application/runtime code (other domains); live repository settings; secrets; any network
service. The previous run's rows were re-checked only where the subject matter is in ORCH scope.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/audits/README.md:13-16,19-28,30-37,39-40` | docs (contract + index) | Declares the audit run layout and lists runs | Contradicts the pack contract and omits the repo-deep-dive runs |
| `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/` (10 files) | published run | Latest `main` audit corpus | INDEX/manifest/findings/register disagree (findings below) |
| `docs/audits/repo-deep-dive/20261004-0700-main-178b91c/`, `.../20261002-0344-develop-6286137/` | published runs | Comparison baselines | Both are internally consistent (14/14 and 269/269 IDs) |
| `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md:9-11` | docs (re-audit) | Operator-facing evidence links | Points at machine-local `C:\temp\...` paths |
| `prompts/repo-deep-dive/README.md:14,16-25`; `RUN_ORDER.md:1-43`; `prompts/MASTER_RUNNER_FULL_HARDENING.md` | vendored pack | Run naming, expected outputs, execution order (41 domains, 00–40) | Snapshot ends at prompt 40 |
| `prompts/PROVENANCE.md:3-4,31-33,63`; `prompts/manifest.json`; `scripts/verify-prompts.js`; `.github/workflows/validate.yml:107,109-110` | supply-chain guard | Pins prompt files by SHA-256 and fails CI on drift | `repo-deep-dive` row marked "Stale vs its runs" |
| `AGENTS.md:11,13-20,37-76,90,470,100-109` | agent contract | Monorepo map, do-not-touch rules, running audit ledger | Guardrails are specific and CI-backed |
| `tools/check_run.sh:20-23,54-95` | tool | Required finals + ID consistency checks | Compares registers↔manifest only; not reports↔findings |
| `tools/full_domain.py:190-228,348-377,485-571` | tool | Run naming, manifest, ID assignment, single-writer aggregate | Deterministic per-run ID assignment |
| `tools/lib_findings.py:52-83,101-119,149-165` | tool | Register merge, duplicate/orphan detection, gate logic | Reproduced the ID divergence with it |
| `tools/publish_audit.py:213-252` | tool | Canonical publish metadata for a focused run | Shows the committed 9c0b88c metadata did not come from this flow |
| `runs/mainecybertech-20261011-0426-full-main-8d299b8/{audit_manifest.json,INDEX.md,coverage.md,_domains/deterministic.json}` | this run (scaffold) | Scope, prompt inventory, deterministic seed findings | 43 domains (42 prompts + deterministic), gate pending |
| `runs/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md:18,28,124,153,183,226,277,294` | previous run | Verification duty + cross-run ID continuity | No ORCH rows; adjacent rows noted below |

## Verification Performed

| # | Command (all read-only) | Observed result |
|---|---|---|
| 1 | `git -C /tmp/opencode/mct-audit-target log -3 --format='%h %ci %s'`; `git status --porcelain` | HEAD `8d299b8d` (2026-10-11), branch `main`, worktree clean |
| 2 | `python3 tools/full_domain.py domains --full` (pack) | 43 domains: `deterministic` + 42 prompt domains; every referenced prompt file exists in the pack; `promptCount` 42 in the run manifest matches |
| 3 | `bash tools/check_run.sh <target 9c0b88c run>` | `RESULT: PASS` — the guard compares the two registers to the manifest; it does **not** compare report files to `findings.json` |
| 4 | `python3` with `lib_findings.collect_with_dupes` on the published 9c0b88c folder | 336 findings from 1 report; **11 findings have no register row**; **11 register rows exist in no report** (orphans) |
| 5 | Title-level comparison (lens vs `findings.json`) | 0 titles unique to either artifact, but **25 titles carry different IDs** and **14 IDs present in both artifacts denote different findings** |
| 6 | Same collectors on the pack's canonical run `runs/mainecybertech-20261004-full-main-9c0b88c` | 43 reports, 336 findings, 0 missing register rows, 0 orphans → the divergence was introduced in the published copy, not in the audit itself |
| 7 | `git log -1 -- <published paths>` | lens last touched `24857899` (2026-10-04, PR #97); `findings.json` last touched `7a8eb1ce` (2026-10-11, register sync); `audit_manifest.json` last touched `43604416` (2026-10-09) |
| 8 | Read of published `audit_manifest.json` / `findings.json` | `profile: base`, `promptCount: 42`, `mode: full`, 43 domains, `sourceReports: 43` — but the folder holds exactly 1 report and the INDEX calls the run "Focused" |
| 9 | Read of the 178b91c published run metadata | `profile: focused-security-supply-chain-ci`, `promptCount: 4`, `scaffolded_by: tools/publish_audit.py`, `sourceReports: 1` — consistent with its one-report inventory |
| 10 | `grep -n` of `prompts/PROVENANCE.md`, `prompts/repo-deep-dive/README.md`, vendored/pack master runners | Vendored master lists 41 domains (00–40); committed run manifests list `45_exploit_chain_attack_path_audit` (line 63 of the 9c0b88c manifest) which the vendored pack does not contain (AI-P1-001 residual) |
| 11 | `grep -n` of the previous register (`follow_up_register.md`, `risk_register.md`, `findings.json`) for `ORCH` | 0 rows — the previous run emitted no ORCH findings (its `_domains/00_audit_orchestrator.json` has `findings: []`) |
| 12 | Cross-run ID comparison (previous register vs this run's `_domains/deterministic.json`) | `DET-P3-001` changed meaning (digest-pin check → gitleaks check); the digest-pin check re-enters as `DET-P3-002` with status `open` although the previous register reconciled it `verified-fixed` |

### Verification duty (previous run)

The previous run's register (`runs/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md`) contains
**no ORCH-area rows**, so there is nothing to carry with a `verified-fixed`/`still-open` verdict for this area.
Adjacent rows whose subject matter touches this domain, and their owning areas:

- `AI-P1-001` "Vendored audit prompt packs are stale and the run manifest references a prompt the pack does
  not contain" (register line 18, `partially-fixed`). Re-checked at `8d299b8d`: still true —
  `prompts/repo-deep-dive/` ends at prompt 40 (41 domains in its master runner; `PROVENANCE.md:63` marks it
  "Stale vs its runs"), while committed run manifests reference prompt 45. **Left to the AI domain**
  (`20_ai_automation_agent_readiness`) — not duplicated here.
- `HYG-P2-001` "Committed prompt/audit corpus bloats the repo and review surface" (line 153) — HYGIENE domain.
- `FINAL-P1-001` (line 47) and `INV-P3-001` (line 294) — FINAL / INV domains.
- `DET-P3-001` "3 container image(s) without a digest pin" (line 277, `verified-fixed` with the note that
  static pinning is not applicable) — re-enters this run's deterministic lens under a changed ID; see
  Finding "Finding identity is not stable across runs".

## Executive Summary

The audit **process** around this repository is unusually mature: the run contract, do-not-touch rules, prompt
pinning, and operator handoff are all documented and partially CI-enforced. The ORCH domain has no P0.

Strengths:

- **Scope and guardrails are explicit.** The run manifest binds repo, branch, commit, read-only and
  secret-redaction flags (`audit_manifest.json:12-22`); `AGENTS.md:37-76` lists generated files, human-approval
  gates, and "Never" rules; `prompts/PROVENANCE.md:3-4` declares the prompt tree untrusted data, and
  `AGENTS.md:74-76` makes that binding.
- **Prompt inventory is pinned and guarded.** Every vendored prompt file is SHA-256-pinned in
  `prompts/manifest.json` and checked in CI (`validate.yml:107` runs `node scripts/verify-prompts.js verify`).
- **Aggregation is single-writer by construction.** `tools/full_domain.py aggregate` (lines 485-571) writes
  `findings.json`, both registers, the finals, the manifest and the INDEX from one assigned-ID set;
  `tools/check_run.sh` then enforces ID parity between registers and manifest, uniqueness, and status
  vocabulary.
- **Do-not-touch zones are real, not aspirational.** Prompt edits must be regenerated through
  `verify-prompts.js generate`; `review.md` must be regenerated from `AGENTS.md` (`validate.yml:109-110`);
  docs links are guarded (`scripts/check-docs-links.mjs`).
- **Operator handoff is written down** at both layers: pack runbooks (`OPERATOR_QUICKSTART.md`,
  `POST_AUDIT_PIPELINE.md`) and repo docs (`docs/audits/README.md`, `AGENTS.md` Known Debt / Completed Work,
  operator-action list at `AGENTS.md:100-109`).

Major risks:

1. **The published `main` audit run is internally inconsistent (P1).** The report file a reviewer opens and
   the register an operator remediates from disagree on finding IDs for 25 rows, and 14 IDs denote different
   findings in each artifact. `tools/check_run.sh` passes it anyway. Any ID-based verification, remediation
   PR, or cross-run diff targets the wrong rows.
2. **The audit index contradicts itself and omits the current runs (P2).** `docs/audits/README.md` documents
   a run shape (`YYYY-MM-DD`, `report.md`, `evidence/`) that no repo-deep-dive run follows, while the vendored
   pack documents a different one; the Runs table lists only the comprehensive/ui-ux runs.
3. **Finding identity is not stable across runs (P3).** Deterministic IDs are reused for different checks,
   legacy area codes (`SUPPLY`, `HYG`, `CONF`, `PORT`) persist beside the current lens codes, and a
   previously reconciled `verified-fixed` item re-enters as an open finding.

Recommended next actions: republish the 9c0b88c run from the pack's canonical copy (or re-key the lens) and
add a report↔register ID parity guard to the publish flow; then repair `docs/audits/README.md` and add an
index guard. Neither action blocks the product release, but both protect every future remediation wave.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Run manifest (this run) | `_domains/../audit_manifest.json` | Scope, prompt inventory, gate | Scaffold state; `promptCount` 42, 43 domains, gate `pending` | Low | Aggregator refreshes totals/gate |
| Prompt inventory | `prompts/MASTER_RUNNER_FULL_HARDENING.md` (pack) | Ordered domain list | 42 prompt domains; all files exist | Low | Verified via `full_domain.py domains --full` |
| Vendored pack | `prompts/repo-deep-dive/` | Target-repo copy of the audit pack | Pinned; ends at prompt 40 | Medium | `PROVENANCE.md:63` marks it stale vs its runs (AI-P1-001) |
| Prompt pinning | `prompts/manifest.json`, `scripts/verify-prompts.js` | Tamper detection for 630 files | Enforced in `validate.yml:107` | Low | Tree hashes per pack |
| Published runs | `docs/audits/repo-deep-dive/{20261002-0344,20261004-0700,mainecybertech-20261004-full}` | Audit corpus | 2 consistent, 1 inconsistent | High | See Finding 1 |
| Audit index | `docs/audits/README.md` | Layout contract + Runs table | Contradictory + stale | Medium | See Finding 2 |
| Re-audit report | `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md` | Cross-repo re-audit summary | Committed; machine-local evidence links | Low | Lines 9-11 use `C:\temp\...` |
| Aggregation tooling | `tools/full_domain.py`, `tools/lib_findings.py` | Normalize/assign/aggregate | Single-writer, deterministic | Low | `assign_ids` at lines 348-377 |
| Run validator | `tools/check_run.sh` | Required finals + ID parity | PASSes the inconsistent run | Medium | Checks registers↔manifest only (lines 54-95) |
| Publish flow | `tools/publish_audit.py` | Canonical publish metadata | Not used for the 9c0b88c copy | Medium | Focused manifest at lines 213-227 |
| Guardrails | `AGENTS.md:37-76`, `prompts/PROVENANCE.md` | Do-not-touch zones | Documented + partly CI-enforced | Low | Strong |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Repository type and monorepo boundaries | 5 | `AGENTS.md:11` "Turborepo monorepo: 3 apps + 3 packages"; `pnpm-workspace.yaml:2-3`; `turbo.json` | None material | Keep |
| App/service/package map | 5 | `AGENTS.md:13-20` (API/Web/Worker/SDK/UI/Config with entries + ports); `apps/*`, `packages/*` | None material | Keep |
| Audit prompts to run and dependencies | 3 | Pack master runner lists 42 domains; vendored copy lists 41 (00–40); committed manifests reference prompt 45 | Vendored pack cannot resolve prompt 45; README says "reports from 00 through 40" | Refresh vendored pack or add pinned-version guard (owner: AI domain, AI-P1-001) |
| Current branch/SHA/run naming | 3 | Manifests bind branch/commit (`audit_manifest.json:16-18`); run ids dated | Two documented conventions (`docs/audits/README.md:13` vs `prompts/repo-deep-dive/README.md:14`) and three actual variants | Declare one canonical naming rule; validate it in the publish flow |
| Report inventory and expected files | 2 | `tools/check_run.sh:20-23` (7 finals); pack README expected outputs | Two conflicting inventories; published 9c0b88c inventory contradicts its own metadata | Republish; add inventory↔metadata guard |
| Risk aggregation strategy | 3 | `full_domain.py:485-571` single writer; registers mirrored; `lib_findings.compute_gate:149-165` | Published corpus diverged (25 ID mismatches); mixed area vocabularies; `Target` column mixes windows and areas | Reconcile published copy; normalize carried rows |
| Finding ID scheme | 3 | `REFERENCE_CARD.md:38-40` `AREA-Px-NNN`; `full_domain.py:348-377` assigns deterministically | 25 titles with two IDs in one published run; 14 ID/title collisions; legacy codes | Parity guard + stable carry-forward IDs |
| Do-not-touch safety zones | 4 | `AGENTS.md:42-76`; `PROVENANCE.md:3-4`; CI guards `validate.yml:107,110` | Audit-run read-only rule not restated in `docs/audits/README.md` (only "never overwrite a run", line 21) | Add a short read-only/do-not-touch section to the audit README |
| Final index requirements | 2 | `check_run.sh:20-23` enforced when validating a run | Repo-side index omits all repo-deep-dive runs; published INDEX cites an ID absent from its register | Fix Runs table; add index guard |
| Operator handoff requirements | 4 | Pack runbooks; `docs/audits/README.md:39-40` → `AGENTS.md:90,470`; operator actions `AGENTS.md:100-109` | Stale index; machine-local evidence paths in the re-audit report | Repoint evidence to repo-relative paths |

## Detailed Review

### Item: Run scaffold and manifest (this run)

- Evidence: `runs/mainecybertech-20261011-0426-full-main-8d299b8/audit_manifest.json` (pack: `tools/full_domain.py:200-228`).
- What it does: records name/repo/branch/commit/read-only flags, the 43-domain fan-out, and the pending gate.
- How it appears to work: `full_domain.py init` wrote the manifest/INDEX/coverage; the deterministic lens was
  emitted next (`_domains/deterministic.json`); `aggregate` will re-render finals.
- Current controls: commit binding, secret-redaction flag, `check_run.sh` after aggregate.
- Missing controls: no binding of the deterministic lens artifact to the commit (`deterministic-findings.json`
  records `run: mct-audit-target`, the worktree basename, and no SHA).
- Risks: low (pack-side artifact), but it shows run-level metadata can drift from the audited commit.
- Recommended improvement: pass `--run <run-id>` and record the commit in deterministic artifacts.
- Suggested tests: unit assert that emitted `deterministic-findings.json.run` equals the manifest `run` and
  that both record `shortCommit`.
- Suggested docs: note in the master runner that lens artifacts must bind the commit.

### Item: Audit prompt inventory and dependencies

- Evidence: pack master runner (42 domains) vs vendored `prompts/repo-deep-dive/prompts/MASTER_RUNNER_FULL_HARDENING.md`
  (41 domains, 00–40) vs committed manifests listing `45_exploit_chain_attack_path_audit`.
- What it does: defines the ordered domain list and dependencies (foundation → security → data/API → CI/CD →
  operations → UX → governance → final aggregation).
- How it appears to work: `full_domain.py master_order()` parses the numbered list; the aggregator walks it.
- Current controls: vendored pack pinned by `prompts/manifest.json` + CI.
- Missing controls: no check that run manifests resolve every listed prompt against the vendored pack.
- Risks: medium — the committed corpus references a prompt no reader can open (tracked as AI-P1-001).
- Recommended improvement: add the resolve-check the previous register proposed (manifest prompts ⊆ vendored files).
- Suggested tests: script test that each `domains[]` entry maps to a vendored file or is explicitly marked external.
- Suggested docs: `prompts/repo-deep-dive/README.md` should state the snapshot boundary next to the run list.

### Item: Finding-ID scheme and aggregation strategy

- Evidence: `REFERENCE_CARD.md:38-40`; `full_domain.py:348-377`; `lib_findings.py:101-119`; published 9c0b88c
  folder; previous register lines 28/80/114/115/158/159/289-293 vs lens lines 26/72/107-108/153-154/287-291.
- What it does: assigns `AREA-Px-NNN` per area per run; registers mirror; gate derives from severities.
- How it appears to work: deterministic and collision-free **within a run**; carry-forward rows keep their
  previous IDs only if the subagent re-emits them.
- Current controls: uniqueness check + register↔manifest parity in `check_run.sh`.
- Missing controls: report↔findings parity; cross-run ID stability for tool-generated findings.
- Risks: high where the published copy diverges (Finding 1); medium across runs (Finding 3).
- Recommended improvement: add the parity check to `check_run.sh` and to the publish flow; document carry-forward rules.
- Suggested tests: run `lib_findings.collect_with_dupes` on every published run in CI and fail on orphans.
- Suggested docs: a short "finding identity across runs" section in the shared rules.

### Item: Report inventory, published corpus, and final index

- Evidence: `docs/audits/README.md:13-16,30-37`; pack README `:16-25`; the three run folders; `check_run.sh:20-23`.
- What it does: tells operators what a run contains and where to find it.
- How it appears to work: pack runs are self-describing (INDEX + manifest + registers); the repo index does not
  list them.
- Current controls: `check_run.sh` (pack-side); docs link guard scans `docs/audits/README.md` for broken links only.
- Missing controls: no check that run directories are indexed, or that published metadata matches the files.
- Risks: medium — operators cannot discover the current corpus from the documented index.
- Recommended improvement: reconcile the contract, list all runs, add an index-completeness check.
- Suggested tests: CI script asserting `docs/audits/<pack>/<run>/` ⊆ README table.
- Suggested docs: `docs/audits/README.md` (single canonical contract).

### Item: Do-not-touch safety zones

- Evidence: `AGENTS.md:42-76` (generated files; human approval for merges/prod/Terraform/migrations/RLS/branch
  protection/secrets; "Never" list); `prompts/PROVENANCE.md:3-4`; `AGENTS.md:74-76`; CI guards
  `validate.yml:107,109-110`; pack shared rules (read-only target, redact secrets, no destructive commands).
- What it does: prevents agents from editing generated artifacts or bypassing review.
- How it appears to work: CI enforces what it can (prompt manifest, review mirror, docs links); the rest are
  review gates, explicitly labeled.
- Current controls: strong and specific.
- Missing controls: the audit-run read-only rule is only in the pack, not restated in the repo's audit README.
- Risks: low.
- Recommended improvement: add three bullets to `docs/audits/README.md` (read-only target; write only under the run dir; never overwrite a run — already at line 21).
- Suggested tests: none needed beyond existing CI.
- Suggested docs: `docs/audits/README.md`.

### Item: Operator handoff requirements

- Evidence: `runbooks/OPERATOR_QUICKSTART.md`, `runbooks/POST_AUDIT_PIPELINE.md`, `docs/audits/README.md:39-40`,
  `AGENTS.md:90,100-109,470`, `REAUDIT_REPORT_20261004.md:9-11`.
- What it does: sequences publish → remediate → verify, and records operator-gated items.
- How it appears to work: the pack defines the pipeline; the repo keeps a running ledger; operator actions
  (e.g., `prod-approval` reviewers, backup keys) are listed explicitly.
- Current controls: draft-PR-only rules, fail-closed verification, ledger pointers.
- Missing controls: evidence links that only exist on the generating machine.
- Risks: medium-low — handoff works, but some evidence is unreachable for the next operator.
- Recommended improvement: commit evidence excerpts under the run's `evidence/` (or repo-relative paths) instead of `C:\temp\...`.
- Suggested tests: docs link guard already fails broken relative links; extend it to flag absolute local paths.
- Suggested docs: `REAUDIT_REPORT_20261004.md` path cleanup.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ORCH-001 | Repository type and monorepo boundaries | `AGENTS.md:11`; `pnpm-workspace.yaml:2-3` | Documented | None | — | Keep |
| ORCH-002 | App/service/package map | `AGENTS.md:13-20` | Documented with entries/ports | None | — | Keep |
| ORCH-003 | Audit prompts to run and dependencies | Pack master (42) vs vendored (41) vs manifests (prompt 45) | Vendored pack pinned in CI | Dangling prompt 45 | P1 (AI-owned) | Resolve-check in CI (AI-P1-001) |
| ORCH-004 | Current branch/SHA/run naming | Manifests `:16-18`; `docs/audits/README.md:13`; pack README `:14` | Commit binding in manifests | Two contradictory conventions | P3 | Declare one canonical rule |
| ORCH-005 | Report inventory and expected files | `check_run.sh:20-23`; published 9c0b88c folder | Pack-side validator | Published inventory ≠ metadata | P1/P3 | Republish + inventory guard (Findings 1/3) |
| ORCH-006 | Risk aggregation strategy | `full_domain.py:485-571` | Single-writer aggregate | Published copy diverged | P1 | Republish; add report↔register parity |
| ORCH-007 | Finding ID scheme | `REFERENCE_CARD.md:38-40`; `full_domain.py:348-377` | Deterministic per-run IDs | 25 dual IDs; 14 collisions; legacy areas | P1/P3 | Parity guard; carry-forward rules (Findings 1/3) |
| ORCH-008 | Do-not-touch safety zones | `AGENTS.md:42-76`; `PROVENANCE.md:3-4`; CI guards | Documented + CI-enforced | Audit README silent on read-only | P3 | Add read-only section |
| ORCH-009 | Final index requirements | `check_run.sh:20-23`; `docs/audits/README.md:30-37` | Pack-side | Repo index omits all repo-deep-dive runs | P2 | Fix table; add index guard (Finding 2) |
| ORCH-010 | Operator handoff requirements | Pack runbooks; `AGENTS.md:100-109`; `REAUDIT_REPORT_20261004.md:9-11` | Pipeline + ledger documented | Machine-local evidence paths | P3 | Repo-relative evidence links |

## Findings

### Finding: Published `main` audit run is internally inconsistent (report/register ID divergence; full-domain metadata over a one-report inventory)

- Severity: P1
- Confidence: High (reproduced with the pack's own collector at `8d299b8d`)
- Area: ORCH
- Evidence:
  - `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/lens_focused_security_supply_chain_ci.md:26` — `CHAIN-P1-003` "Branch-protection bypass + missing prod gate compose into unattended production change"; `follow_up_register.md:28` carries the **same title as `CHAIN-P1-008`** (`verified-fixed`), and the register contains no `CHAIN-P1-003` row (grep count 0).
  - Same pattern at `lens:72` (`ACM-P2-001` "PLATFORM_ADMIN_KEYS…") vs `register:80` (`ACM-P2-008` "Profiles are enumerable…"); `lens:153-154` (`INFRA-P2-001/002`) vs `register:158-159` (`INFRA-P2-006/007`); `lens:287-291` (`INFRA-P3-001–005`) vs `register:289-293` (`INFRA-P3-008–012`); `lens:107-108` (`CHAIN-P2-001/002`) vs `register:114-115` (`CHAIN-P2-009/010`).
  - Reproduced with `tools/lib_findings.py` (`collect_with_dupes`, lines 101-119) on the published folder: 336 findings collected from the single report; **11 have no register row** (`ACM-P2-001`, `CHAIN-P1-003`, `CHAIN-P2-001/002`, `INFRA-P2-001/002`, `INFRA-P3-001–005`); **11 register rows appear in no report** (`ACM-P2-008`, `CHAIN-P1-008`, `CHAIN-P2-009/010`, `INFRA-P2-006/007`, `INFRA-P3-008–012`).
  - Title-level comparison: **25 titles carry different IDs** between the lens and `findings.json`/register, and **14 IDs present in both artifacts denote different findings** (e.g. `ACM-P2-002` = "RLS is not a database backstop…" in the lens, = "PLATFORM_ADMIN_KEYS…" in the register).
  - `INDEX.md:37` lists `CHAIN-P1-003` as a P1, an ID that does not exist in the register.
  - The pack's canonical copy (`runs/mainecybertech-20261004-full-main-9c0b88c`) is consistent (43 reports, 336 findings, 0 orphans), so the divergence entered through the published copy: the lens was last touched `24857899` (2026-10-04, PR #97), while `findings.json` was last touched `7a8eb1ce` (2026-10-11, register sync) and the manifest `43604416` (2026-10-09).
  - `tools/check_run.sh` (lines 54-95) `RESULT: PASS` on the published folder — its consistency checks compare the two registers to the manifest, never the report files to `findings.json`.
  - Metadata over a one-report inventory: `audit_manifest.json:11` `"mode": "full"`, `:5` `promptCount: 42`, `:23-67` 43 domains, `:10` `scaffolded_by: tools/full_domain.py aggregate`, `:14` `targetRepo: /mnt/c/temp/fdtarget`; `findings.json:4` `sourceReports: 43`; but the folder holds exactly one report and `INDEX.md:3` describes it as a "Focused security / supply-chain / CI deep-dive". `tools/publish_audit.py:213-227` shows the standard publish flow would record `profile: focused-security-supply-chain-ci`, `promptCount: 4`, `sourceReports: 1` for this inventory (as the 178b91c run does).
- What is happening: two generations of the same audit were merged into one published folder — the focused lens from 2026-10-04 (old ID numbering) and the reconciled registers/findings/manifest from 2026-10-09/11 (renumbered IDs, full-domain metadata). Nothing in the publish path re-checks the two against each other.
- Why it matters: the published run is the release-gating evidence base; ID-based verification (the pack's own protocol), remediation PRs citing IDs, `tools/diff_runs.py`, and CSV exports all target the wrong rows for 25 findings, and 14 IDs are ambiguous depending on which file is read.
- User / business impact: remediation work can be done under the wrong ID (or duplicated); the INDEX cannot lead a reader to the register row for `CHAIN-P1-003`; the next rerun inherits the ambiguity when it re-verifies by ID.
- Security / privacy / reliability impact: indirect — the audit ledger is the control that tracks security/reliability fixes; its integrity is load-bearing for every other domain's findings.
- Recommended fix: republish the run from the pack's canonical copy (either ship the 43 domain reports, or regenerate the lens with the register's IDs and re-sync INDEX/EXECUTIVE_SUMMARY/RELEASE_GATE), and add a publish/CI guard that scans report files and fails when their IDs do not match `findings.json`/register (`lib_findings.collect_with_dupes` already computes exactly this).
- Suggested validation: re-run the collector on the republished folder → 0 missing register rows, 0 orphan register rows; `tools/check_run.sh` still PASSes; spot-check `CHAIN-P1-003/008` and `ACM-P2-001/002` resolve to one ID.
- Owner suggestion: platform engineering / audit owner
- Effort estimate: S
- Dependencies: the pack's canonical run (`/root/repo-deep-dive/runs/mainecybertech-20261004-full-main-9c0b88c`)
- Status: open
- Endpoint / data path: n/a (repository artifacts)
- Attack path: none identified

### Finding: `docs/audits/README.md` documents a run contract that contradicts the pack and the actual runs, and its Runs table omits all three repo-deep-dive runs

- Severity: P2
- Confidence: High (files inspected at `8d299b8d`)
- Area: ORCH
- Evidence:
  - `docs/audits/README.md:13` — `<run> = YYYY-MM-DD (or YYYY-MM-DD-<n>)`; `:14-16` — every run must contain `report.md`, `findings.json` (optional), `evidence/`. The actual repo-deep-dive runs are `mainecybertech-20261004-full-main-9c0b88c`, `20261004-0700-main-178b91c`, `20261002-0344-develop-6286137`, none of which has `report.md` or `evidence/`.
  - `prompts/repo-deep-dive/README.md:14` — the vendored pack documents `{run} = YYYYMMDD-HHMM-{branch}-{shortsha}` and `:16-25` expects `INDEX.md`, `risk_register.md`, `roadmap.md`, `patch_plan.md`, `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md` plus domain reports `00`–`40` — a second, conflicting contract shipped in the same repository.
  - `docs/audits/README.md:30-37` — the Runs table lists only `comprehensive-audit/2026-08-26` and the three `ui-ux-docs-completeness/2026-09-27*` runs; the three `repo-deep-dive` runs and `REAUDIT_REPORT_20261004.md` are absent.
  - `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md:9-11` — evidence links are machine-local (`C:\temp\reaudit\...`, `file:///C:/temp/...`), unreachable for any other operator.
  - `docs/audits/README.md:21` does carry the useful rule "Never overwrite a previous run"; `:39-40` correctly points at `AGENTS.md` Known Debt/Completed Work (present at `AGENTS.md:90,470`).
- What is happening: the audit index was written for the two manual packs and was never updated when the repo-deep-dive pack became the primary audit path; it now documents a shape no current run follows.
- Why it matters: operators and agents cannot discover the current audit corpus from the documented index, and an agent following the documented contract would create runs that do not match the pack's required finals or the pack's own INDEX expectations.
- User / business impact: slower onboarding to the audit corpus; risk of divergent run shapes; the re-audit report's evidence cannot be opened by the reader it was written for.
- Security / privacy / reliability impact: low directly; indirectly it weakens the audit trail (the control that tracks everything else).
- Recommended fix: make `docs/audits/README.md` state one canonical contract (the pack's naming + finals, with the manual packs' shape called out as legacy), add all three repo-deep-dive runs plus `REAUDIT_REPORT_20261004.md` to the table, and replace machine-local evidence paths with repo-relative ones.
- Suggested validation: `scripts/check-docs-links.mjs` stays green; a new check fails when a `docs/audits/<pack>/<run>/` directory is not listed.
- Owner suggestion: platform engineering / docs owner
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

### Finding: Finding identity is not stable across runs (deterministic IDs reused; legacy area codes persist), so verification status does not carry

- Severity: P3
- Confidence: High (register/artifacts compared directly)
- Area: ORCH
- Evidence:
  - Previous run register `runs/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md:277` — `DET-P3-001` = "[SUPPLY] 3 container image(s) without a digest pin", `verified-fixed` ("Static pinning is not applicable").
  - This run's `_domains/deterministic.json` (emitted at `8d299b8d`) — `DET-P3-001` now means "[SEC] gitleaks not installed (secret scan skipped)"; the digest-pin check re-enters as `DET-P3-002` with status `open`, losing the previous reconciliation.
  - Legacy area codes persist in the carried corpus beside the current lens codes: `SUPPLY-*` (e.g. `follow_up_register.md:226,334`) vs the `SC` lens; `HYG-*` (`:153`) vs the `HYGIENE` lens; one-off `CONF-P2-001` (`:124`) and `PORT-P2-001` (`:183`) with no current lens.
  - `tools/lib_findings.py` and `tools/diff_runs.py` key entirely on `AREA-Px-NNN`; `tools/full_domain.py:348-377` assigns fresh sequential IDs per area per run unless a payload re-emits a pack-schema ID.
- What is happening: tool-generated findings and carried rows are not guaranteed the same ID between runs, and old area vocabularies remain in the ledger.
- Why it matters: cross-run diffs report false "added"/"missing" churn; verification by ID can compare different findings; a reconciled item silently re-opens.
- User / business impact: noisy delta reports; reviewer time lost re-adjudicating closed items.
- Security / privacy / reliability impact: low — ledger hygiene.
- Recommended fix: document and enforce carry-forward rules (re-emit the previous ID for a carried finding; keep deterministic check IDs stable per check/subcode or include the check name in the ID), publish a legacy→current area mapping (`SUPPLY→SC`, `HYG→HYGIENE`, `PORT→DET/CI`, `CONF→SECRET`), and have the aggregator warn when a finding's area is not in the run's lens list.
- Suggested validation: run `tools/diff_runs.py` between consecutive runs and confirm no false churn for reconciled items; unit test that the deterministic lens reuses its IDs when the check set is unchanged.
- Owner suggestion: audit tooling owner (repo-deep-dive pack)
- Effort estimate: S–M
- Dependencies: agreement on the carry-forward rule; Finding 1's republish
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Remediation work driven by mismatched IDs | High | Medium | Wrong/duplicated fixes; broken verification | Finding 1 | Republish + parity guard |
| Audit corpus undiscoverable from the documented index | Medium | High | Operator/agent confusion; divergent run shapes | Finding 2 | Fix README + index guard |
| Cross-run delta reports mislead | Medium | Medium | Wasted review; re-opened closed items | Finding 3 | Carry-forward rules + area map |
| Vendored pack cannot resolve a referenced prompt | Medium | High (already true) | Agent cannot follow the manifest to prompt 45 | AI-P1-001; `PROVENANCE.md:63` | Refresh pack or pinned-version guard (AI domain) |
| Published metadata misstates coverage | Low | High (already true) | Aggregations overstate scope | Finding 1 (metadata evidence) | Align metadata with published set |

## Recommendations

### Immediate / Release Blocking

None — no P0 in this domain.

### This Week

1. Republish the 9c0b88c run as one consistent artifact set (Finding 1): either publish the 43 domain reports
   from the canonical pack run, or re-key the lens to the register IDs and re-render INDEX/EXECUTIVE_SUMMARY/
   RELEASE_GATE from the same generation.
2. Add the report↔register ID parity check to `tools/check_run.sh` and/or the publish flow so the same class of
   drift cannot ship again.

### This Month

3. Rewrite `docs/audits/README.md` against one canonical contract, list every run (including the three
   repo-deep-dive runs and the re-audit report), and replace machine-local evidence paths (Finding 2).
4. Align the published manifest/`findings.json` metadata (`mode`, `promptCount`, `sourceReports`) with the files
   actually published, and drop machine-local `targetRepo` values (Finding 1 metadata evidence).
5. Add an index-completeness guard for `docs/audits/` (script or CI step).

### Later / Platform Evolution

6. Document and enforce cross-run carry-forward ID rules; normalize legacy area codes (Finding 3).
7. Extend the deterministic lens to bind artifacts to the audited commit and to reuse check-stable IDs.
8. Add a "do-not-touch / read-only during audit" section to `docs/audits/README.md` so the repo's audit contract
   matches the pack's shared rules.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Run `lib_findings.collect_with_dupes` on every published run in CI | Catches orphan/missing register rows immediately | `.github/workflows/*`, `scripts/` (new small script), `tools/lib_findings.py` | Fails on the current 9c0b88c copy; passes after republish |
| Add the missing runs to `docs/audits/README.md` Runs table | Operators find the current corpus | `docs/audits/README.md` | `scripts/check-docs-links.mjs` green |
| Publish the legacy→current area map (`SUPPLY→SC`, `HYG→HYGIENE`, …) | Makes carried IDs explainable | `docs/audits/README.md` or the run's README | Reviewer can map every legacy row |
| Flag environment-scoped deterministic findings (`gitleaks not installed`) in the register note | Prevents the target repo being blamed for audit-host tooling | `_domains/deterministic.json`, register note | Register row states "audit-host tooling" |
| Replace `C:\temp\...` links with repo-relative evidence | Next operator can open the evidence | `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md` | No absolute local paths in docs |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Republish 9c0b88c consistently | P1 | platform engineering | S | canonical pack run |
| Report↔register parity guard in `check_run.sh` | P1 | audit tooling | S | none |
| `docs/audits/README.md` contract + Runs table rewrite | P2 | docs owner | S | none |
| Published metadata ↔ inventory alignment | P2 | audit tooling | S | republish |
| Index-completeness guard | P2 | CI owner | S | none |
| Carry-forward ID rules + area map | P3 | audit tooling | S–M | agreement |
| Commit binding in deterministic artifacts | P3 | audit tooling | S | none |

## Suggested Tests

- **Unit (pack):** `lib_findings.collect_with_dupes` returns 0 missing / 0 orphan for a synthetic run whose
  report IDs match its register; fails when one row is renumbered.
- **CI (target repo):** script scanning `docs/audits/<pack>/<run>/` — report-file IDs ⊆ `findings.json` IDs and
  register rows ⊆ report-file IDs; fails on the current 9c0b88c copy.
- **CI (target repo):** index-completeness — every run directory appears in `docs/audits/README.md`.
- **CI (target repo):** docs guard extension — reject absolute local paths (`C:\`, `file:///C:/`) in docs.
- **Regression:** after republishing, `tools/diff_runs.py <previous> <republished>` shows no ID churn beyond the
  intended republish; `check_run.sh` PASS.
- **Manual:** open `INDEX.md` and walk each P0/P1 ID to its register row — every ID must resolve.

## Suggested Documentation Updates

- `docs/audits/README.md` — canonical layout contract, full Runs table, read-only/do-not-touch section,
  legacy area-code mapping.
- `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md` — repo-relative evidence paths.
- `prompts/repo-deep-dive/README.md` — note the snapshot boundary (ends at prompt 40) beside the run list.
- A short "finding identity across runs" note in the pack's shared rules / `REFERENCE_CARD.md`.
- `runs/<run>/README` convention note (pack) — what `mode`/`sourceReports` mean for a published subset.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which contract is canonical for `docs/audits/` — the pack's `INDEX`/registers shape or the manual `report.md` shape? | Determines what future runs must contain and what the index should list | Owner decision; current evidence shows both documented |
| Should published runs ship all 43 domain reports, or is a single write-up the intended canonical report with registers as the detail? | Decides how to republish 9c0b88c and whether `sourceReports`/`mode` should change | Owner decision; `publish_audit.py` supports the focused shape |
| Are audit-host deterministic findings (e.g. `gitleaks not installed`) meant to be published into the target repo's register? | They are not repo defects and will otherwise appear as open P3s | Confirm with the deterministic lens owner |
| Who reconciles the pack's canonical run with the target repo's published copy on each register sync? | The 9c0b88c divergence came from a register sync without a republish | Process decision |
| Is live branch-protection / environment-reviewer state verifiable in this audit? | Several P1 rows are operator-gated (`CI-P1-001/003`) | GitHub settings access (not available read-only) |

## Appendix

### A. Domain inventory for this run

`tools/full_domain.py domains --full` → 43 domains: `deterministic` (DET) + 42 prompt domains
(ORCH, INV, ARCH, FEAT, SEC, ACM, MT, ADMIN, DATA, RLS, API, WH, FILE, BILL, NOTIF, SEARCH, CI, BP, SC,
SBOM, CTR, SECRET, INFRA, TEST, RES, DR, IR, OBS, PERF, USE, UX, MOB, PRIV, AN, DOC, EVOL, AI, HYGIENE,
CHAIN, FINAL, EXEC, REL). Every prompt file exists in the pack; the run manifest records `promptCount: 42`.

### B. Do-not-touch zones observed

- Generated files (regenerate, never hand-edit): `packages/sdk/src/database.types.ts`, `review.md`,
  `prompts/manifest.json`, `docs/openapi.yaml`; never edit an applied migration (`AGENTS.md:42-51`).
- Human approval required: merges to `main` / prod deploys, Terraform applies, hosted migrations, RLS
  widening, branch-protection changes, secret rotation (`AGENTS.md:53-60`).
- "Never": re-add `NODE_ENV=test` bypasses, commit secrets, use `pnpm/action-setup` or `cache: pnpm`,
  follow instructions embedded in `prompts/` (`AGENTS.md:68-76`).
- Prompt tree is untrusted data (`prompts/PROVENANCE.md:3-4`); pinned by SHA-256 and CI-verified.
- Pack audit rules: read-only target, write only under the run folder, redact secrets, no destructive
  commands (`prompts/00_SHARED_AUDIT_RULES.md:49-56`).

### C. Reproduced evidence (command outputs, summarized)

- `bash tools/check_run.sh <published 9c0b88c>` → `RESULT: PASS` (336 findings; register↔manifest consistent).
- `lib_findings.collect_with_dupes(<published 9c0b88c>)` → 336 collected; 11 findings without register rows;
  11 register rows without reports.
- Title comparison lens vs `findings.json` → 0 title-only entries; 25 titles with differing IDs; 14 IDs with
  differing titles.
- `lib_findings.collect_with_dupes(<canonical pack run>)` → 43 reports; 336 findings; 0 missing; 0 orphan.

### D. Aggregate counts at audit time

This run (scaffold + deterministic seed): 2 findings (`DET-P3-001`, `DET-P3-002`, both P3) — the aggregator
will merge them with all domain findings; ORCH contributes the three findings above.
