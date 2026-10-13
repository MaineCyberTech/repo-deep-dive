# 00_audit_orchestrator — Prompt 00 - Audit Orchestrator

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `00_audit_orchestrator.md` (area ORCH, prompt)

## Verification Performed

# Audit Orchestrator

## Audit Metadata

- Audit name: repo-deep-dive (bench-test full-domain audit)
- Run: 20261013-b916709 (ad-hoc, read-only domain subagent)
- Repository: `C:\temp\bench-test`
- Branch: `main`
- Commit SHA: `b9167095b08c2f45a814e88e09d88decbd0ea885`
- Generated at: 2026-10-13
- Auditor: audit-orchestrator domain subagent
- Area code: ORCH
- Output path: `docs/audits/repo-deep-dive/20261013-b916709/00_audit_orchestrator.md`
- Scope limitations: read-only; no lab access used; this is a workstation-benchmark toolkit, not the audit framework, so the orchestrator's own tooling (`tools/new_run.py`, `tools/publish_audit.py`) lives in the *repo-deep-dive* pack and is out of scope here. The only orchestration artifact set inside the target is the one published run under `docs/audits/`.

## Scope

Reviewed the repository's audit-orchestration surface: repository type / monorepo boundaries, the app/service/package map, the published audit run under `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/`, run naming, report inventory, risk aggregation, finding-ID scheme, do-not-touch rules, and operator handoff. Not reviewed: the benchmark phases, the control plane, the live-USB build, and CI workflow internals (owned by other domains). The target working tree had two pre-existing uncommitted modifications (`server/benchd.py`, `server/import_results.py`) that were not touched.

## Evidence Reviewed

- `README.md`, `AGENTS.md`, `VERSION`, `.gitattributes`
- `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/` — all 12 tracked files
- git history for the audit run, `.github/`, and `.gitattributes`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log -1 --format=%H` | command | Bind the audit to a commit | `b916709…`, branch `main` |
| `git ls-files` / `git ls-tree -r HEAD -- docs/audits/` | command | Enumerate orchestrator artifacts | 12 files in the single run folder |
| `git diff --no-index risk_register.md follow_up_register.md` | command | Test whether the risk register is distinct | Exit 0 — files are identical |
| `git log --diff-filter=A -- .github/workflows/build-app.yml` / `-- .gitattributes` | command | Check reconciliation of CI/port findings | Added after the run (14b0b0e3, 71772649) |
| Read `INDEX.md`, `audit_manifest.json`, `findings.json`, `deterministic-findings.json`, `risk_register.md`, `follow_up_register.md`, registers, `lens_*.md` | read | Report inventory + self-consistency | ID and inventory mismatches reproduced directly |

## Executive Summary

`bench-test` is a **single-package workstation toolkit** (not a SaaS, not a monorepo): a flat layout of `bench/`, `server/`, `live/`, `packaging/`, `tests/`, `docs/`, `examples/`, `results/`, documented in `README.md:326-336` and `AGENTS.md:48-60`. Nothing here implements the audit-orchestration pipeline itself — that pipeline (scaffolding, publishing, digests) is the *repo-deep-dive* pack's job. What the target *does* contain is one published audit run serving as the worked example of the run contract, and that run is internally inconsistent.

Strengths: run folder naming follows the pack convention (`YYYYMMDD-HHMM-{branch}-{shortsha}` → `20261007-1731-main-4ecee97`); a machine-readable `audit_manifest.json` with `outputRoot`, prompt list, and commit binding exists; the report has a `Verification Performed` section that distinguishes lab-unavailable (`MODE=local`) and records it honestly; the repo declares do-not-touch rules (`AGENTS.md:279-285`).

Risks: the published run uses **two conflicting finding-ID schemes**, its `risk_register.md` is a **verbatim duplicate** of the follow-up register, the manifest/INDEX **omit two produced reports**, one deterministic finding is **silently dropped** from the aggregate, and the register is **never reconciled** after later commits fixed two findings. Findings: 5 (0 P0, 0 P1, 3 P2, 2 P3).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Run folder | `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/` | One published audit run | Present, 12 files | Low | Bound to `4ecee97` |
| Run INDEX | `…/INDEX.md` | Operator handoff map | Partial | Medium | Omits 2 reports; no execution plan |
| Run manifest | `…/audit_manifest.json` | Machine-readable manifest | Partial | Medium | `scope.reports` lists 1 of 2 lenses |
| Findings aggregate | `…/findings.json` | Consolidated findings | 7 findings | Medium | No DET area / no exclusion note |
| Risk register | `…/risk_register.md` | Risk aggregation | Duplicate of follow-up register | Medium | Identical file |
| Follow-up register | `…/follow_up_register.md` | Owner/status tracker | 7 rows, all `open` | Medium | Not reconciled |
| Deterministic lens | `…/lens_deterministic.md`, `…/deterministic-findings.json` | Machine checks | Present, unlisted | Low | DET-P3-002 dropped from aggregate |
| Do-not-touch rules | `AGENTS.md:279-285` | Repo safety zones | Present | Low | `## Do not` section |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Repository type and monorepo boundaries | 4 | `README.md:326-336`, `AGENTS.md:48-60` | No explicit "not a monorepo" statement | Add one line to AGENTS.md |
| App/service/package map | 4 | `README.md:338-355` script table, `AGENTS.md:50-60` | Map exists in two docs, could drift | Cross-link / single source |
| Audit prompts to run and dependencies | 3 | `audit_manifest.json:9-15` (`promptCount`, `prompts`) | No dependency/order info | Record prompt dependencies |
| Current branch/SHA/run naming | 4 | run dir name; `audit_manifest.json:16-25` | Working tree dirty at audit time (uncommitted) | Record tree state in manifest |
| Report inventory and expected files | 2 | `INDEX.md:7-15`, `audit_manifest.json:23-25` | 2 reports omitted | Complete both artifacts |
| Risk aggregation strategy | 1 | `risk_register.md` == `follow_up_register.md` | No risk fields / categories | Build a real risk register |
| Finding ID scheme | 2 | `lens_…md:7-13` vs `:71-115` | Two schemes collide | Unify to per-area IDs |
| Do-not-touch safety zones | 3 | `AGENTS.md:279-285`; `lens_…md:20` ("Read-only audit") | Not stated per-run | Add to manifest/INDEX |
| Final index requirements | 3 | `INDEX.md` present but incomplete | No cross-run/aggregate index | Add run index + exclusions |
| Operator handoff requirements | 3 | `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`, `roadmap.md`, `patch_plan.md` | Status staleness | Reconcile statuses |

## Detailed Review

### Item: Repository type and monorepo boundaries

- Evidence: `README.md:1-10`, `README.md:326-336`; `AGENTS.md:6-17`, `AGENTS.md:48-60`; flat top-level dirs (`git ls-files`).
- What it does: declares a single host-agnostic toolkit with `bench/`, `server/`, `live/`, `packaging/`, `tests/`, `docs/`.
- How it appears to work: no workspace manifests (`package.json`, `pyproject.toml`, `go.mod`); Python is stdlib-only (`AGENTS.md:21-24`).
- Dependencies: none cross-package.
- Current controls: layout documented in two places.
- Missing controls: no explicit "single package, no monorepo" note.
- Risks: low.
- Recommended improvement: state the boundary explicitly in `AGENTS.md`.
- Suggested tests: n/a.
- Suggested docs: `AGENTS.md` one-liner.

### Item: App/service/package map

- Evidence: `README.md:338-355` (script table), `AGENTS.md:50-60`, `docs/CONTROL_PLANE.md`, `docs/DATA.md`.
- What it does: maps runners, phases, dashboards, agent, and `server/benchd.py` control plane.
- Missing controls: the same map is maintained in two docs, so it can drift.
- Recommended improvement: keep the map in `README.md` and have `AGENTS.md` link to it.

### Item: Audit prompts to run and dependencies

- Evidence: `audit_manifest.json:9-15` (`promptCount: 4`, four `prompts`), `profile: focused-security-supply-chain-ci`.
- What it does: records which pack prompts ran.
- Missing controls: no dependency/ordering metadata, and the deterministic lens (`tools/deterministic_checks.py`) is not named in the manifest even though it ran (`lens_…md:38-42`).
- Recommended improvement: add a `lenses`/`dependencies` block.

### Item: Current branch/SHA/run naming

- Evidence: `audit_manifest.json:16-25`; run folder name `20261007-1731-main-4ecee97`.
- What it does: binds scope to `branch`, `commit`, `shortCommit`, `generatedAt`.
- Missing controls: no record of the working-tree state; at this audit's commit the tree is dirty (`git status` shows `M server/benchd.py`, `M server/import_results.py`).
- Risks: a SHA-only binding cannot reproduce a run over uncommitted changes.
- Recommended improvement: record `dirty: true/false` + a tree hash in the manifest.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ORCH-001 | Repository type and boundaries | `README.md:326-336` | Documented layout | Not stated as single-package | P3 | Add note |
| ORCH-002 | App/service/package map | `README.md:338-355` | Script table | Duplicated in 2 docs | P3 | Single source |
| ORCH-003 | Audit prompts + dependencies | `audit_manifest.json:9-15` | Prompt list | No dependencies/lens | P2 | Extend manifest |
| ORCH-004 | Branch/SHA/run naming | `audit_manifest.json:16-25` | Commit binding | Working tree unrecorded | P2 | Record tree state |
| ORCH-005 | Report inventory | `INDEX.md:7-15` | File table | Omits 2 reports | P2 | Complete inventory |
| ORCH-006 | Risk aggregation | `risk_register.md` | None (duplicate) | No risk fields | P2 | Real risk register |
| ORCH-007 | Finding ID scheme | `lens_…md:7-13,71-115` | Two schemes | Collision | P2 | Unify IDs |
| ORCH-008 | Do-not-touch zones | `AGENTS.md:279-285` | `## Do not` | Not per-run | P3 | Add to manifest |
| ORCH-009 | Final index | `INDEX.md` | Run INDEX | Incomplete, no exclusions | P2 | Rebuild |
| ORCH-010 | Operator handoff | registers | Register present | Stale statuses | P3 | Reconcile |

## Findings

### Finding ID: `ORCH-P2-001` - Published audit run uses two conflicting finding-ID schemes

- Severity: P2
- Confidence: High
- Area: ORCH (finding ID scheme)
- Evidence:
  - `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/lens_focused_security_supply_chain_ci.md:7-13` — summary table IDs `SUPPLY-P2-001`, `SUPPLY-P2-002`, `DATA-P2-001`, `SAFE-P2-001`, `CI-P3-001`, `GOV-P3-001`.
  - `…/lens_focused_security_supply_chain_ci.md:71,79,87,97,108,115` — body headings use an ordinal scheme `SUPPLY-P2-002`, `SUPPLY-P2-003`, `DATA-P2-004`, `SAFE-P2-005`, `CI-P3-006`, `GOV-P3-007`.
  - `…/findings.json:22,41,59,77,95,113,130` and `…/follow_up_register.md:5-11` use the per-area scheme.
- What is happening: the narrative and the machine-readable aggregate disagree on the ID of every finding after the first.
- Why it matters: cross-referencing a body heading to `findings.json`/the register resolves to a different finding.
- Recommended fix: regenerate all headings from `findings.json` and add a consistency check.
- Suggested validation: a test that every `### Finding ID:` heading equals a `findings[].id`.
- Owner suggestion: audit tooling owner.
- Effort estimate: S
- Dependencies: none
- Status: open
- Attack path: none identified

### Finding ID: `ORCH-P2-002` - risk_register.md is a verbatim copy of follow_up_register.md

- Severity: P2
- Confidence: High
- Area: ORCH (risk aggregation strategy)
- Evidence:
  - `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/risk_register.md:1` — title `# Follow-up register`.
  - `git diff --no-index risk_register.md follow_up_register.md` → exit 0 (no differences).
  - `…/INDEX.md:12` — lists `risk_register.md / follow_up_register.md` as distinct registers.
- What is happening: the "risk register" is a byte-identical copy of the follow-up register and carries no risk fields.
- Why it matters: the orchestrator scope requires aggregation categories for the final risk register; none exist.
- Recommended fix: author a real risk register (category, likelihood, impact, mitigation) derived from `findings.json`.
- Suggested validation: assert the two files differ and that the risk register has required columns.
- Owner suggestion: audit tooling owner.
- Effort estimate: S
- Dependencies: ORCH-P2-001
- Status: open
- Attack path: none identified

### Finding ID: `ORCH-P2-003` - Run INDEX and audit_manifest.json omit the deterministic lens artifacts

- Severity: P2
- Confidence: High
- Area: ORCH (report inventory / final index)
- Evidence:
  - `…/audit_manifest.json:23-25` — `scope.reports` = `["lens_focused_security_supply_chain_ci.md"]`.
  - `…/INDEX.md:7-15` — no row for `lens_deterministic.md` or `deterministic-findings.json`.
  - `git ls-tree -r HEAD -- docs/audits/` — both files are tracked.
  - `…/deterministic-findings.json:20` — findings reference `lens_deterministic.md`.
- What is happening: two produced artifacts are absent from the run's handoff map and manifest, with no stated exclusion.
- Why it matters: a reader reproducing the run cannot see that the deterministic lens ran or find its output.
- Recommended fix: list both artifacts in `INDEX.md` and `audit_manifest.json`; state any intentional exclusions.
- Suggested validation: a check that every file in the run folder appears in `INDEX.md`.
- Owner suggestion: audit tooling owner.
- Effort estimate: S
- Dependencies: none
- Status: open
- Attack path: none identified

### Finding ID: `ORCH-P3-001` - Deterministic finding DET-P3-002 is dropped from the aggregate

- Severity: P3
- Confidence: High
- Area: ORCH (aggregation)
- Evidence:
  - `…/deterministic-findings.json:14-34` — emits `DET-P3-001` and `DET-P3-002`.
  - `…/findings.json:5-18` — aggregate `total: 7`, `byArea` has no `DET`; `DET-P3-002` appears nowhere.
  - `…/findings.json:125` — only `DET-P3-001` is carried over.
- What is happening: one machine-generated finding is silently lost from the aggregate.
- Why it matters: aggregates must account for excluded items; the count no longer reconciles with the lens.
- Recommended fix: merge it or list it as explicitly excluded.
- Suggested validation: aggregate total = sum of lens findings ± an explicit exclusion list.
- Owner suggestion: audit tooling owner.
- Effort estimate: S
- Dependencies: ORCH-P2-003
- Status: open
- Attack path: none identified

### Finding ID: `ORCH-P3-002` - Published run was never reconciled after later commits fixed two findings

- Severity: P3
- Confidence: Medium
- Area: ORCH (operator handoff / reconciliation)
- Evidence:
  - `…/findings.json:113-128` — `CI-P3-001` status `open`.
  - `git log --diff-filter=A -- .github/workflows/build-app.yml` → `14b0b0e3` added CI.
  - `git log --diff-filter=A -- .gitattributes` → `71772649` added the line-ending policy (resolves `DET-P3-002`).
  - `…/follow_up_register.md:10-11` — `CI-P3-001`, `GOV-P3-001` still `open`.
- What is happening: findings the repo has since addressed still read `open`, with no reconciliation note.
- Why it matters: operators cannot tell resolved from outstanding work.
- Recommended fix: run a reconciliation pass and update statuses with the fixing commit as artifact.
- Suggested validation: each `verified-fixed` status cites a commit at/after the finding's scope commit.
- Owner suggestion: audit operator.
- Effort estimate: S
- Dependencies: none
- Status: open
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Remediation mapped to wrong finding ID | P2 | High | Rework / missed fix | `lens_…md:7-13` vs `:71-115` | Unify IDs |
| No usable risk view / categories | P2 | High | Can't prioritize a remediation wave | `risk_register.md` duplicate | Real risk register |
| Reports lost from handoff map | P2 | Medium | Reproduction gap | `INDEX.md:7-15`, manifest `:23-25` | Complete inventory |
| Stale statuses mislead operators | P3 | High | Confusion, double work | registers all `open` | Reconcile |
| Aggregate count unreconciled | P3 | Medium | Score/reproduction mismatch | `findings.json:5-18` | Record exclusions |

## Recommendations

### Immediate / Release Blocking
None (no P0/P1 in this domain).

### This Week
- Unify the finding-ID scheme across the report, JSON, and registers (ORCH-P2-001).
- Complete `INDEX.md` and `audit_manifest.json` with both deterministic artifacts (ORCH-P2-003).

### This Month
- Replace the duplicated `risk_register.md` with a real risk aggregation (ORCH-P2-002).
- Add an exclusion/merge record for deterministic findings (ORCH-P3-001).

### Later / Platform Evolution
- Add a reconciliation step to the run lifecycle so statuses track later commits (ORCH-P3-002).
- Record working-tree state in the manifest for SHA binding.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix 6 body headings to match JSON IDs | Restores traceability | `lens_focused_security_supply_chain_ci.md` | Heading/JSON equality check |
| Add 2 rows to `INDEX.md` | Complete handoff map | `INDEX.md` | Every run file listed |
| Add 1 report to manifest | Manifest matches disk | `audit_manifest.json` | `scope.reports` == tracked lenses |
| Rename/rewrite `risk_register.md` | Real risk view | `risk_register.md` | Files differ |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| ID-scheme consistency check | P2 | audit tooling | S | ORCH-P2-001 |
| Complete run inventory + exclusion record | P2 | audit tooling | S | ORCH-P2-003 |
| Risk aggregation generator | P2 | audit tooling | M | ORCH-P2-002 |
| Reconciliation pass in run lifecycle | P3 | audit operator | M | ORCH-P3-002 |
| Record working-tree state in manifest | P3 | audit tooling | S | — |

## Suggested Tests

- **Unit:** parse `lens_*.md` headings and assert each matches a `findings[].id`.
- **Unit:** assert `risk_register.md != follow_up_register.md` and that the risk register has required columns.
- **Integration:** assert every file under a run folder is referenced by `INDEX.md` and that machine lenses appear in `audit_manifest.json`.
- **CI:** aggregate-count check — `findings.json.counts.total` equals the sum over lens files minus an explicit exclusion list.

## Suggested Documentation Updates

- `docs/audits/repo-deep-dive/<run>/INDEX.md` — add the deterministic-lens rows and an "excluded" note.
- `docs/audits/repo-deep-dive/<run>/audit_manifest.json` — add `scope.reports` entries and a `lenses` block.
- `docs/audits/repo-deep-dive/<run>/risk_register.md` — replace with a genuine risk register.
- `AGENTS.md` — add a single-package statement and the audit-artifact consistency rules.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the dirty working tree (`M server/benchd.py`, `M server/import_results.py`) intended? | A SHA-only run binding cannot capture uncommitted changes | Operator confirmation / a manifest `dirty` field |
| Which report(s) is the canonical aggregate source for this run — `lens_focused…` or `findings.json`? | Determines which IDs win | Runbook statement |
| Was `DET-P3-002` intentionally excluded or an aggregation bug? | Affects whether the count is trustworthy | Aggregator source |
| Is `docs/audits/` intended to hold a cross-run index? | Operator navigation | Any top-level audits index (none found) |

## Appendix

- The target is not the audit framework; `tools/` does not exist in `bench-test` (`git ls-files tools/` is empty). The deterministic lens was run with the repo-deep-dive pack's `tools/deterministic_checks.py` (`lens_focused_security_supply_chain_ci.md:38-42`).
- Run folder contents (12 tracked files): `INDEX.md`, `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`, `audit_manifest.json`, `findings.json`, `follow_up_register.md`, `risk_register.md`, `roadmap.md`, `patch_plan.md`, `lens_deterministic.md`, `deterministic-findings.json`, `lens_focused_security_supply_chain_ci.md`.
- Run naming matches the shared convention: `YYYYMMDD-HHMM-{branch}-{shortsha}` → `20261007-1731-main-4ecee97` (`00_SHARED_AUDIT_RULES.md:14`).

## Findings

| ID | Severity | Title |
|---|---|---|
| ORCH-P2-001 | P2 | Published audit run uses two conflicting finding-ID schemes in the same report |
| ORCH-P2-002 | P2 | risk_register.md is a byte-for-byte copy of follow_up_register.md, so the run has no risk aggregation |
| ORCH-P2-003 | P2 | Run INDEX and audit_manifest.json omit the deterministic lens artifacts |
| ORCH-P3-001 | P3 | Deterministic finding DET-P3-002 is dropped from the aggregate with no exclusion record |
| ORCH-P3-002 | P3 | Published run was never reconciled after later commits fixed two of its findings |
