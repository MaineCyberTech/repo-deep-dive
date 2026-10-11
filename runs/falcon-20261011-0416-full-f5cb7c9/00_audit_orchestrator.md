# 00_audit_orchestrator — Prompt 00 - Audit Orchestrator

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `00_audit_orchestrator.md` (area ORCH, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive (falcon)
- Run: `falcon-20261011-0416-full-f5cb7c9` (mode full, profile base per manifest)
- Repository: `MaineCyberTech/falcon` @ `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (branch `main`)
- Generated at: 2026-10-11T04:45Z
- Auditor: repo-deep-dive full-pass subagent (ORCH)
- Area code: ORCH
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/00_audit_orchestrator.md` (intended; emitted here under the pack run dir)
- Scope limitations: orchestration domain only; no application code was modified; the live host was inspected read-only. Final synthesis artifacts did not exist at capture time (the run is mid-flight).

## Scope

Reviewed: this run's scaffold (`runs/falcon-20261011-0416-full-f5cb7c9/{audit_manifest.json, INDEX.md, coverage.md, deterministic-findings.json, _domains/deterministic.json, live_snapshot.txt}`), the pack orchestration tooling (`tools/full_domain.py`, `tools/check_run.sh`, `tools/lib_findings.py`, `tools/publish_audit.py`, `VERSION`, `profiles/falcon-lab.md`, `profiles/falcon-lab.manifest.json`), and the falcon repository's durable audit-run records and tooling (`docs/audits/repo-deep-dive/` — 6 committed runs, `automation/validation/audit_run_lifecycle.sh`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md`, `docs/RELEASE_GATE.md`, `docs/CURRENT_STATE.md`, `docs/audits/AUDIT_REMEDIATION_HANDOFF.md`). Not reviewed: per-domain report content outside this assignment; final synthesis artifacts (not yet emitted); the pack's other profiles beyond the falcon-lab comparison.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `runs/falcon-20261011-0416-full-f5cb7c9/audit_manifest.json` | artifact | run manifest | profile `base`; promptCount 42; 43 domains; `lenses` = 43 area codes; findings 0 at scaffold |
| `runs/falcon-20261011-0416-full-f5cb7c9/INDEX.md`, `coverage.md` | artifact | report inventory / output map | 43 rows, consistent; release gate `pending` |
| `runs/falcon-20261011-0416-full-f5cb7c9/_domains/deterministic.json` | artifact | seed findings + ID scheme | DET-P3-001..003 pre-assigned |
| `tools/full_domain.py` | tooling | writes manifest/INDEX/coverage, assigns IDs, aggregates | `default_run()` prefixes the repo name (185-191); profile hardcoded `base` (203, 219); `lenses` = area codes (224) |
| `tools/check_run.sh` | tooling | run validation | falcon-lab extras required only when `profile == "falcon-lab"` (47-52) |
| `tools/lib_findings.py:149-165` | tooling | shared gate rule | `compute_gate`: P0 -> NO-GO, P1 -> GO WITH CONDITIONS |
| `tools/publish_audit.py` | tooling | publication into the consumer repo | default run id is timestamp-first (`20261004-0700-<branch>-<sha>`); gate computed by the shared rule |
| `profiles/falcon-lab.md`, `profiles/falcon-lab.manifest.json`, `prompts/MASTER_RUNNER_FALCON_LAB.md` | doctrine | documented falcon adaptation | 46 prompts + 5 lens overlays; manifest uses `lenses` for ND/REV/INTG/LIVE/ADV |
| `docs/audits/repo-deep-dive/` (6 committed runs) | artifact | durable run records | newest = `20261005-0354-full-main-e267ce1`; the 20261009 full run and the 20261011 verification run are **not** committed |
| `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md` | artifact | committed gate | `Verdict: **GO WITH CONDITIONS**` with `P0 x1, P1 x7` |
| `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/audit_manifest.json` | artifact | committed run scope | profile `focused-security-supply-chain-ci`, promptCount 4 |
| `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/follow_up_register.md` | artifact | committed register | 34 rows `open` |
| `automation/validation/audit_run_lifecycle.sh:120-122` | source | consumer run-id rule | run id must match `^[0-9]{8}-[0-9]{4}-` |
| `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` | doc | run lifecycle rules | rule 1: never rewrite a committed run folder; corrections are new dated files/appended sections |
| `docs/RELEASE_GATE.md` | doc | canonical repo gate page | still references the 20261002/20260930 audit opinions; the newest full run is not referenced |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Manifest/INDEX/coverage cross-count (current run) | artifact | aggregate self-consistency | 43 domains = 1 deterministic + 42 prompts; rows consistent; 0 findings at scaffold — consistent |
| Run-id regex test against `audit_run_lifecycle.sh:120-122` | command | naming conformance | `falcon-20261011-0416-full-f5cb7c9` -> FAIL; `20261011-0416-full-main-f5cb7c9` -> PASS |
| `git log`/`git ls-files` on `docs/audits/repo-deep-dive/` | command | durable-record inventory | 6 runs; newest `20261005-0354-full-main-e267ce1`; no 20261009/20261011 run folders |
| Re-read committed 20261005 gate, manifest, register | artifact | prior-finding reconciliation | gate `GO WITH CONDITIONS` with `P0 x1`; profile focused/promptCount 4; `grep -c "| open |"` = 34 |
| `grep -n` on `tools/full_domain.py` profile/lenses/default_run | command | prior-finding reconciliation | unchanged: `"profile": "base"` at 203/219; `lenses` = area codes at 224 |
| Report-vs-JSON status comparison for the 20261009 ARCH domain | artifact | self-consistency | report body says ARCH-P2-001 `verified fixed` / `Status: verified-fixed`; the same JSON's findings array and both registers say `open` |
| GitHub API `GET /repos/MaineCyberTech/falcon/commits/main` | command | live-vs-remote binding | remote `main` = `f5cb7c9` (pushed 2026-10-11T04:04:15Z) = the audited commit |

## Executive Summary

The current run's scaffold is internally consistent (43 domains, 42 prompts, matching INDEX/coverage rows, deterministic seed findings with `AREA-Px-NNN` IDs). Four orchestration issues stand out:

1. **The repository's durable audit record still ends at the 2026-10-05 focused run** (`20261005-0354-full-main-e267ce1`), which carries `P0 x1` but publishes `GO WITH CONDITIONS` — contradicting the pack's shared gate rule (P0 -> NO-GO) and its canonical run — and presents full-domain findings under a 4-prompt "focused" profile with no per-domain reports. The 2026-10-09 full run and the 2026-10-11 verification run have never been committed to `docs/audits/repo-deep-dive/`, so the newest durable record in the repo is a P0-bearing run whose gate is wrong (ORCH-P2-001).
2. **The pack's full-domain driver still cannot represent the documented falcon-lab profile**: `profile` is hardcoded `base` and `lenses` is filled with area codes, so "full" falcon runs silently cover only the base 42 prompts and the manifest cannot validate against the falcon-lab schema (ORCH-P2-002).
3. **The run id again violates the consumer repo's lifecycle rule** (`falcon-...` prefix), which will fail `audit_run_lifecycle.sh check` if published unchanged (ORCH-P3-001).
4. **New: a status contradiction inside the 20261009 run's own artifacts** — the ARCH domain report marks ARCH-P2-001 `verified-fixed` while its findings array and both follow-up registers say `open`; live evidence supports fixed (ORCH-P3-002).

Strengths: the scaffold, ID scheme, gate rule, and publication gate are consistent; `publish_audit.py` already defaults to a conforming timestamp-first run id; the lifecycle runbook defines append-only correction semantics that make reconciliation cheap.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Run manifest (current) | `runs/falcon-20261011-0416-full-f5cb7c9/audit_manifest.json` | scope + aggregates | consistent; profile base; lenses=areas | medium | ORCH-P2-002 |
| INDEX / coverage (current) | same folder | output map | 43 rows, consistent | low | finals pending (mid-run) |
| Deterministic seed | `_domains/deterministic.json` | DET findings | DET-P3-001..003 | low | DET-P3-001 no LICENSE; DET-P3-002 gitleaks missing; DET-P3-003 unpinned images |
| Driver | `tools/full_domain.py` | scaffold/aggregate | base-only; repo-prefixed run id | medium | ORCH-P2-002, ORCH-P3-001 |
| Run checker | `tools/check_run.sh` | validate run folder | profile-gated falcon-lab extras | low | never fires for base runs |
| Gate rule | `tools/lib_findings.py:149-165` | single gate decision | P0 -> NO-GO | low | source of the ORCH-P2-001 contradiction |
| Publisher | `tools/publish_audit.py` | publish into consumer repo | timestamp-first default id; secret scan fail-closed | low | uses the shared gate |
| Committed run (newest) | `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/` | durable record | gate GO WITH CONDITIONS with P0; 4-prompt profile; 34 open | high | ORCH-P2-001 |
| Unpublished runs | `runs/falcon-20261009-2117-full-08e20d1/`, `runs/falcon-20261011-0400-verify-main-584e1a3/` | canonical records | not committed to the repo | medium | durable record lags |
| Lifecycle tooling | `automation/validation/audit_run_lifecycle.sh` | run inventory/check | 6 runs, `check_failures=0` | low | regex at 120-122 |
| Repo gate page | `docs/RELEASE_GATE.md` | canonical reconciliation | references 20261002/20260930 opinions only | medium | newest full run's P0 not referenced (HYGIENE-P2-002) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Repository type and monorepo boundaries | 4 | ops repository, single tree; `README.md`, `REPOSITORY.md` | no monorepo/package map needed | keep |
| App/service/package map | 4 | compose/central, compose/probe, automation/wazuh, compose/mct | staged MCT tree policy gap (FEAT-P2-001) | keep |
| Audit prompts to run and dependencies | 3 | `full_domain.py` domain list (43); `profiles/falcon-lab.md` documents 46 | falcon-lab not representable | ORCH-P2-002 |
| Current branch/SHA/run naming | 2 | run id `falcon-...` vs `audit_run_lifecycle.sh:120-122` | id fails the consumer regex | ORCH-P3-001 |
| Report inventory and expected files | 4 | INDEX/coverage/manifest consistent; finals pending | finals not yet emitted at capture | re-check at closeout |
| Risk aggregation strategy | 3 | shared `compute_gate`; register mirror 1:1 | report/JSON/register status contradiction (ARCH-P2-001) | ORCH-P3-002 |
| Finding ID scheme | 4 | `AREA-Px-NNN`; deterministic seeds pre-assigned | none found | keep |
| Do-not-touch safety zones | 4 | runbook rule 1 (never rewrite committed runs); AGENTS hard rules | not enforced mechanically | optional check |
| Final index requirements | 3 | INDEX skeleton exists; finals pending | release gate pending mid-run | closeout |
| Operator handoff requirements | 3 | `patch_plan.md`/`roadmap.md` expected; handoff doc exists (`docs/audits/AUDIT_REMEDIATION_HANDOFF.md`) | handoff for this run pending | closeout |

## Detailed Review

### Item: Run scaffold and manifest (current run)

- Evidence: `runs/falcon-20261011-0416-full-f5cb7c9/audit_manifest.json`; `INDEX.md`; `coverage.md`; `_domains/deterministic.json`.
- What it does: records the run scope (43 domains, 42 prompts), the target commit, and the aggregate counters; seeds DET findings.
- How it appears to work: `tools/full_domain.py` writes manifest/INDEX/coverage from the prompt list and the deterministic lens; `_domains/*.json` carry per-domain findings; the aggregator merges them.
- Dependencies: prompt pack, target clone, deterministic checks.
- Current controls: consistent counts; IDs pre-assigned; secret scan at publish.
- Missing controls: no claim-sample set artifact (extended verification check), no profile field fidelity (below), no mechanical cross-check that a domain report's finding statuses match the JSON findings array.
- Risks: a stale status propagates into the final register (ORCH-P3-002).
- Recommended improvement: add a status-consistency check to `tools/check_run.sh` (report body vs findings array) and emit a `claims.json` sample set at scaffold time.
- Suggested tests: `check_run.sh` fails a run whose domain report says verified-fixed while the findings array says open.
- Suggested docs: note in the runbook that domain reports and `_domains/*.json` must agree on status.

### Item: Committed run record vs canonical pack run (20261005)

- Evidence: `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md:3`; same folder `audit_manifest.json`, `follow_up_register.md`; pack `runs/falcon-20261005-full-main-e267ce1/RELEASE_GATE.md`; `tools/lib_findings.py:149-165`.
- What it does: the durable record a reviewer/operator sees in the repository.
- How it appears to work: published by the then-current `publish_audit.py`, which treated P0 as a condition; the pack unified the gate later, and the falcon artifact was only renamed, never reconciled (prior-run evidence, unchanged).
- Dependencies: publication flow; lifecycle rules.
- Current controls: `audit_run_lifecycle.sh` structural check only (run id + folder shape).
- Missing controls: no content binding or canonical-gate cross-check.
- Risks: release decisions read a weaker gate than the audit produced.
- Recommended improvement: append a dated reconciliation note (rule 1 forbids rewriting) or publish the 20261009/20261011 runs to supersede it.
- Suggested tests: a publish-time assertion that a P0-bearing run cannot emit GO/GO WITH CONDITIONS while unresolved.
- Suggested docs: `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` reconciliation procedure reference.

### Item: Profile and lens recording (`full_domain.py`)

- Evidence: `tools/full_domain.py:203,219,224`; current manifest `profile: base`, `lenses` = 43 area codes; `profiles/falcon-lab.manifest.json:29-31`; `tools/check_run.sh:47-52`.
- What it does: describes the audited scope in the machine-readable manifest.
- How it appears to work: base profile only; falcon-lab extras are required only when the profile string is `falcon-lab`, which the driver never emits.
- Dependencies: falcon-lab profile wiring.
- Current controls: none.
- Missing controls: profile option; lens records; manifest schema validation.
- Risks: "full" falcon runs overstate coverage; falcon-only domains and lenses are never audited.
- Recommended improvement: add `--profile`, emit the falcon-lab manifest shape, record lens IDs/results.
- Suggested tests: generated manifest validates against `examples/audit_manifest.falcon-lab.example.json`.
- Suggested docs: state explicitly that base-profile runs are a reduced scope for falcon.

### Item: Run id and lifecycle conformance

- Evidence: `tools/full_domain.py:185-191`; `automation/validation/audit_run_lifecycle.sh:120-122`; current run id; falcon PR #45 (rename of already-published runs).
- What it does: names the run folder that will be published into the consumer repo.
- How it appears to work: `default_run()` prefixes the repo name, contradicting its own comment.
- Dependencies: publication rename.
- Current controls: none.
- Missing controls: publish-time regex assertion; auto-rename.
- Risks: publishing this run unchanged fails the repo's lifecycle check (mechanical rework, broken record).
- Recommended improvement: emit `<timestamp>-<mode>-<branch>-<sha7>` or auto-rename at publish.
- Suggested tests: `audit_run_lifecycle.sh check` passes on the published folder without a rename.
- Suggested docs: runbook note that publish normalizes ids.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ORCH-001 | Repository type and monorepo boundaries | `README.md`, `REPOSITORY.md` | documented single ops repo | none | — | keep |
| ORCH-002 | App/service/package map | compose trees; `automation/wazuh` | drift check + compose pins | staged MCT policy (FEAT-P2-001) | P2 | see FEAT report |
| ORCH-003 | Audit prompts to run and dependencies | `full_domain.py`; falcon-lab profile docs | base 42 prompts | falcon-lab not representable | P2 | ORCH-P2-002 |
| ORCH-004 | Current branch/SHA/run naming | run id; lifecycle regex | none | id fails `^[0-9]{8}-[0-9]{4}-` | P3 | ORCH-P3-001 |
| ORCH-005 | Report inventory and expected files | INDEX/coverage/manifest | consistent at scaffold | finals pending | — | closeout re-check |
| ORCH-006 | Risk aggregation strategy | `compute_gate`; registers | shared gate rule | report/JSON/register status contradiction | P3 | ORCH-P3-002 |
| ORCH-007 | Finding ID scheme | DET seeds; `_domains/*.json` | `AREA-Px-NNN` | none found | — | keep |
| ORCH-008 | Do-not-touch safety zones | runbook rule 1; AGENTS rules | documented | not mechanical | — | optional check |
| ORCH-009 | Final index requirements | INDEX skeleton | skeleton present | gate pending | — | closeout |
| ORCH-010 | Operator handoff requirements | handoff doc; patch_plan expected | handoff doc exists for 20261002 | current run's handoff pending | — | closeout |

## Findings

### ORCH-P2-001 - Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence

- Severity: P2
- Confidence: High (both artifacts read directly at the audited commit)
- Area: ORCH
- Evidence:
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md:3` — `Verdict: **GO WITH CONDITIONS**`; `P0 x1, P1 x7`
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/audit_manifest.json` — `profile: focused-security-supply-chain-ci`, `promptCount: 4`; no per-domain reports in the folder
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/follow_up_register.md` — 34 rows, all `open` (`grep -c "| open |"` = 34)
  - `tools/lib_findings.py:149-165` — shared gate: any P0 -> NO-GO
  - `runs/falcon-20261005-full-main-e267ce1/RELEASE_GATE.md` — canonical pack run says NO-GO for the same audit
  - `docs/audits/repo-deep-dive/` — still ends at the 20261005 run; the 20261009 full run and the 20261011 verification run are not committed
- What is happening: the durable record of the newest published full-domain audit says GO WITH CONDITIONS while carrying a P0, presents the findings under a 4-prompt focused profile with no domain evidence, and keeps pre-reconciliation statuses. Two newer canonical runs exist only in the pack.
- Why it matters: the repo copy is what a reviewer/operator sees; it understates the gate and cannot be traced to domain evidence.
- User / business impact: release/review decisions may rely on a weaker gate than the audit produced.
- Security / privacy / reliability impact: no runtime effect; integrity/consistency defect in the audit record.
- Recommended fix: per `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` rule 1 (never rewrite), append a dated reconciliation note and/or publish the 20261009/20261011 runs to supersede it; add a publish-time check that a P0-bearing run cannot emit GO/GO WITH CONDITIONS while unresolved.
- Suggested validation: regenerate/append and re-run `automation/validation/audit_run_lifecycle.sh check`; assert gate consistency in the pack's `tools/check_run.sh`.
- Owner suggestion: audit-tooling owner.
- Effort estimate: S.
- Dependencies: access to the pack run folders.
- Status: still-open (unchanged from the 20261009 run).
- Endpoint / data path: `docs/audits/repo-deep-dive/<run>/RELEASE_GATE.md` -> reviewer/operator.
- Attack path: none identified.

### ORCH-P2-002 - full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable

- Severity: P2
- Confidence: High
- Area: ORCH
- Evidence:
  - `tools/full_domain.py:203,219` — `"profile": "base"` written unconditionally
  - `tools/full_domain.py:224` — `"lenses": [d["area"] for d in domains]`
  - `runs/falcon-20261011-0416-full-f5cb7c9/audit_manifest.json` — `profile: base`; `lenses` = DET, ORCH, INV, ..., REL (43 area codes)
  - `profiles/falcon-lab.manifest.json:29-31` and `profiles/falcon-lab.md` — the documented falcon adaptation uses 46 prompts (incl. 41 EVID, 42 XREPO, 43 FLEET, 44 DQ) + 5 lens overlays (ND/REV/INTG/LIVE/ADV)
  - `tools/check_run.sh:47-52` — falcon-lab extras are required only when `profile == "falcon-lab"`, which this driver never emits
  - current run `scope.domains` — no `41_*`..`44_*` entries
- What is happening: the base full-domain driver cannot express the falcon-lab profile; both the prior and the current "full" falcon runs are the base 42-prompt set, and the manifest's `lenses` key is filled with area codes instead of lens records.
- Why it matters: coverage claims ("full run") overstate what was audited for this target; evidence-doctrine, cross-repo pairing, edge-fleet and data-quality fidelity are not assessed; the manifest cannot be validated against the falcon-lab schema.
- User / business impact: gaps in the audit program for exactly the falcon-specific risks the profile was written for.
- Security / privacy / reliability impact: indirect (missing audits).
- Recommended fix: add a `--profile` option; emit the falcon-lab manifest shape (lens IDs/targets/status, waves) when auditing falcon; or record an explicit, documented scope reduction in the manifest.
- Suggested validation: `full_domain.py domains --profile falcon-lab` lists 46 prompts; a generated manifest validates against `examples/audit_manifest.falcon-lab.example.json`.
- Owner suggestion: audit-tooling owner.
- Effort estimate: M.
- Dependencies: falcon-lab profile wiring.
- Status: still-open.
- Endpoint / data path: pack tooling -> run manifest -> coverage claims.
- Attack path: none identified.

### ORCH-P3-001 - Run id does not start with the timestamp required by the consumer repo's lifecycle check

- Severity: P3
- Confidence: High
- Area: ORCH
- Evidence:
  - `tools/full_domain.py:185-191` — `default_run()` prefixes the repo name although its own comment says ids must start `YYYYMMDD-HHMM-`
  - `automation/validation/audit_run_lifecycle.sh:120-122` — a run id must match `^[0-9]{8}-[0-9]{4}-`
  - current run id `falcon-20261011-0416-full-f5cb7c9` -> regex FAIL (tested); `20261011-0416-full-main-f5cb7c9` -> PASS
  - falcon PR #45 renamed already-published runs for exactly this reason
  - `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:24-33` — run folders must pass the structural check
- What is happening: the run id produced for this run again starts with the repo name, so publishing it unchanged into `docs/audits/repo-deep-dive/` fails the target repo's lifecycle check and requires a rename commit.
- Why it matters: mechanical rework and a broken run record if published as-is.
- User / business impact: minor process friction.
- Security / privacy / reliability impact: none directly.
- Recommended fix: make `default_run()` emit `<timestamp>-<mode>-<branch>-<sha7>` (repo recorded in `scope.name` only) or auto-rename at publish; add a publish-time regex assertion. Note `tools/publish_audit.py` already defaults to a conforming id.
- Suggested validation: `audit_run_lifecycle.sh check` passes on the published folder without a rename.
- Owner suggestion: audit-tooling owner.
- Effort estimate: S.
- Dependencies: none.
- Status: still-open.
- Endpoint / data path: run id -> published folder -> lifecycle check.
- Attack path: none identified.

### ORCH-P3-002 - Domain report and findings array disagree on a finding status inside the same 20261009 run artifact

- Severity: P3
- Confidence: High (the same JSON file contains both values; reproduced by parsing it)
- Area: ORCH
- Evidence:
  - `runs/falcon-20261009-2117-full-08e20d1/_domains/02_architecture_runtime_topology.json` — the embedded `report` says `ARCH-P2-001 - Declared container hardening lags the running containers (verified fixed)` and `Status: verified-fixed`; the file's `findings` array records the same finding as `"status": "open"`
  - `runs/falcon-20261009-2117-full-08e20d1/follow_up_register.md:34` and `runs/falcon-20261011-0400-verify-main-584e1a3/follow_up_register.md:34` — `ARCH-P2-001 ... open`
  - live evidence at `f5cb7c9` supports fixed: `falcon_container_drift{kind="security"} 0` (fresh run 04:18Z) and live `no-new-privileges` on all inspected central/probe containers
- What is happening: the run's report body and its machine-readable findings disagree; the registers carried the machine value forward, so an already-fixed finding remains open in the register while the report claims closure.
- Why it matters: the aggregator and the release register cannot be trusted to reflect the audit's own conclusions without a manual re-check; the same class of contradiction (report vs register) is how ORCH-P2-001 arose.
- User / business impact: wrong open-work counts; reviewer confusion.
- Security / privacy / reliability impact: none directly; audit-record integrity.
- Recommended fix: reconcile ARCH-P2-001 in the register (append a note per lifecycle rule 1) and add a `check_run.sh` cross-check that every domain report's finding statuses match the findings array.
- Suggested validation: `check_run.sh` fails a synthetic run with a report/JSON status mismatch.
- Owner suggestion: audit-tooling owner.
- Effort estimate: S.
- Dependencies: none.
- Status: open.
- Endpoint / data path: `_domains/*.json` -> aggregate -> `follow_up_register.md`.
- Attack path: none identified.

## Prior-Run Comparison

| Prior finding | Status now | Evidence |
|---|---|---|
| ORCH-P2-001 | still-open | committed 20261005 gate/manifest/register unchanged; no newer run committed |
| ORCH-P2-002 | still-open | `full_domain.py:203,219,224` unchanged; current manifest profile base, lenses=areas |
| ORCH-P3-001 | still-open | current run id fails the lifecycle regex |
| — (new) | ORCH-P3-002 | report-vs-JSON status contradiction in the 20261009 ARCH domain |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Weaker committed gate misleads release decisions | P2 | Medium | High | committed 20261005 gate vs shared rule | reconcile the record; publish newer runs |
| Falcon-lab-only domains/lenses never audited under base runs | P2 | High | Medium | manifest domains list; profile docs | profile support in the driver |
| Published run-id rejected by repo lifecycle check | P3 | High | Low | regex test; PR #45 | fix `default_run`/publish rename |
| Register statuses diverge from report conclusions | P3 | Medium | Medium | ARCH-P2-001 contradiction | status cross-check in `check_run.sh` |

## Recommendations

### Immediate / Release Blocking
- None (audit-record integrity only; no P0).

### This Week
- Reconcile the committed 20261005 record and publish the 20261009/20261011 runs so the durable record matches the canonical runs (ORCH-P2-001).
- Reconcile ARCH-P2-001 in the register with a dated note (ORCH-P3-002).

### This Month
- Add profile support + lens recording to `full_domain.py`; fix run-id generation (ORCH-P2-002, ORCH-P3-001).
- Add report-vs-JSON status consistency to `tools/check_run.sh`.

### Later / Platform Evolution
- Add a machine check binding committed run records to the canonical pack run for the same audit.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Append a dated reconciliation note to the committed run | removes the gate contradiction without rewriting history | repo run folder | readers see one gate |
| Fix `default_run()` id shape (or rely on publish's default) | removes publish-time rename | `tools/full_domain.py` | lifecycle check passes |
| Register note for ARCH-P2-001 | removes a false open item | `follow_up_register.md` | counts match evidence |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Profile-aware manifest emission (falcon-lab) | P2 | tooling | M | profile schema |
| Publish-time gate/ID assertions | P2 | tooling | S | check_run.sh |
| Report/JSON/register status cross-check | P3 | tooling | S | check_run.sh |
| Committed-run vs canonical-run binding check | P3 | tooling | M | run registry |

## Suggested Tests

- Unit: `full_domain.py` manifest emission for both profiles validates against the example schemas.
- CI: `check_run.sh` fails a run whose gate contradicts its P0/P1 counts.
- CI: `check_run.sh` fails a run whose domain report and findings array disagree on a status.
- CI: publish step rejects a run id not matching `^[0-9]{8}-[0-9]{4}-`.
- Manual: re-read a committed run record against the canonical run and confirm gate/report/register equality.

## Suggested Documentation Updates

- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md`: state the reconciliation procedure for a committed record that contradicts its canonical run (append-only).
- `profiles/falcon-lab.md` / `wiring/REPO_WIRING.md`: state explicitly that base-profile runs are a reduced scope for falcon.
- Pack README: document the claim-sample-set expectation for full runs.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was the base profile a deliberate scope decision for this run? | determines whether ORCH-P2-002 is a defect or a documented reduction | operator statement / manifest note |
| Should the committed 20261005 record be corrected or superseded? | lifecycle says never rewrite committed runs | owner decision |
| Why does the ARCH domain JSON disagree with its own report? | root cause for the status check design | aggregator source inspection |

## Limitations

- The current run was mid-flight at capture (no finals, no aggregate); final-file completeness could not be assessed.
- Live checks were read-only and timestamped in the ARCH report.
- The 20261005 pack-run comparison relies on the pack artifacts already read by the prior run; the falcon artifact itself was re-read at `f5cb7c9`.

## Appendix

- Run-id regex reproduction: `printf '%s' falcon-20261011-0416-full-f5cb7c9 | grep -Eq '^[0-9]{8}-[0-9]{4}-'` -> exit 1.
- Scaffold consistency: 43 domains = 1 deterministic + 42 prompts; INDEX rows = coverage rows = manifest domains.
- Canonical gate rule: `tools/lib_findings.py:149-165` (P0 -> NO-GO, P1 -> GO WITH CONDITIONS, else GO).

## Findings

| ID | Severity | Title |
|---|---|---|
| ORCH-P2-001 | P2 | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence |
| ORCH-P2-002 | P2 | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable |
| ORCH-P3-001 | P3 | Run id does not start with the timestamp required by the consumer repo's lifecycle check |
| ORCH-P3-002 | P3 | Domain report and findings array disagree on a finding status inside the same 20261009 run artifact |
