# 00_audit_orchestrator — Prompt 00 - Audit Orchestrator

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `00_audit_orchestrator.md` (area ORCH, prompt)

## Verification Performed

## Metadata

- Domain: `00_audit_orchestrator` (area ORCH)
- Run: `falcon-20261009-2117-full-08e20d1` (mode full, profile base per manifest)
- Target: `falcon` @ `08e20d1` (branch `main`); audited clone `/tmp/opencode/falcon-audit-08e20d1`
- Emitted: 2026-10-09T21:52:25Z by the repo-deep-dive full-pass subagent
- Scope limitation: orchestration domain only; no application code was modified; live host read-only.

## Scope

Reviewed: this run's scaffold (`runs/falcon-20261009-2117-full-08e20d1/{audit_manifest.json, INDEX.md, coverage.md, deterministic-findings.json, lens_deterministic.md, live_snapshot.txt}`), the pack orchestration tooling (`prompts/MASTER_RUNNER_FULL_HARDENING.md`, `prompts/MASTER_RUNNER_FALCON_LAB.md`, `profiles/falcon-lab.md`, `tools/full_domain.py`, `tools/check_run.sh`, `tools/lib_findings.py`, `tools/publish_audit.py`, `schemas/findings.schema.json`, `examples/audit_manifest*.json`), and the falcon repo's audit-run records/tooling (`docs/audits/repo-deep-dive/` 6 committed runs, `automation/validation/audit_run_lifecycle.sh`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md`, `docs/RELEASE_GATE.md`, `docs/CURRENT_STATE.md`). Not reviewed: the content of domains outside this assignment; final synthesis artifacts (not yet emitted at capture time).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `runs/falcon-20261009-2117-full-08e20d1/audit_manifest.json` | artifact | run manifest | 43 domains = 1 deterministic + 42 prompts; promptCount 42; profile base |
| `runs/falcon-20261009-2117-full-08e20d1/INDEX.md`, `coverage.md` | artifact | report inventory / output map | consistent 43 rows; finals listed but not yet present |
| `runs/falcon-20261009-2117-full-08e20d1/_domains/deterministic.json`, `deterministic-findings.json` | artifact | seed findings + ID scheme | DET-P3-001..003 pre-assigned IDs |
| `tools/full_domain.py` | tooling | writes manifest/INDEX/coverage, assigns IDs, aggregates | profile hardcoded; `lenses` = area codes; default_run shape |
| `tools/check_run.sh`, `tools/lib_findings.py` | tooling | run validation + gate rule | P0 -> NO-GO; falcon-lab extras gated on profile |
| `profiles/falcon-lab.md`, `prompts/MASTER_RUNNER_FALCON_LAB.md` | doctrine | the pack's documented falcon adaptation | 46 prompts, 5 lenses, wave plan, repo-canonical output |
| `docs/audits/repo-deep-dive/*/` (6 committed runs) | artifact | durable run records | lifecycle check passes (`check_failures=0`) |
| `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/` vs `runs/falcon-20261005-full-main-e267ce1/` | artifact | prior-run reconciliation | gate, profile, report inventory, register statuses diverge |
| `automation/validation/audit_run_lifecycle.sh`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` | repo tooling | run-id rule, states, archive | run id must start `YYYYMMDD-HHMM-` |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `bash automation/validation/audit_run_lifecycle.sh status` / `check` (falcon repo) | command | run inventory + structural validity | 6 runs, all tracked; `check_failures=0` |
| Manifest/INDEX/coverage cross-count | artifact | aggregate self-consistency | 43 domains, 42 prompts, 0 findings at scaffold; consistent |
| Pack `git show 729b9f1:tools/publish_audit.py` vs `1e2a086`/`HEAD` | command | date the gate inconsistency | old gate `P0/P1 -> GO WITH CONDITIONS`; current `P0 -> NO-GO` |
| Repo run vs pack run field-by-field | artifact | durable-record fidelity | profile `focused-*` vs `base`; 12 files vs 59; gate GO WITH CONDITIONS vs NO-GO |
| `git log --follow` on the repo run's `RELEASE_GATE.md` | command | confirm no reconciliation after publish | only add (`dba374d`) + rename (`427298b`) |
| Current run id vs `audit_run_lifecycle.sh:120-122` regex | command | naming conformance | id starts `falcon-`, rule requires leading timestamp |

## Executive Summary

The orchestration scaffolding for this run is internally consistent (43 domains, promptCount 42, coverage/INDEX rows match, deterministic seed findings present, IDs follow `AREA-Px-NNN`). The two structural risks are (1) the durable record of the previous full run in the target repository does not match the canonical pack run: it publishes a weaker gate for a P0-bearing run, omits all per-domain reports, and keeps pre-reconciliation statuses; and (2) the pack's full-domain driver cannot express the falcon-lab profile (46 prompts, 5 lenses, edge mirror), so "full" falcon runs silently cover only the base 42 prompts and record area codes under a `lenses` field. A smaller mechanical gap remains in run-id naming, which conflicts with the target repo's lifecycle rule and previously required a dedicated rename commit (falcon PR #45).

## Findings

### ORCH-P2-001 - Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence

- Severity: P2
- Confidence: High (both artifacts read directly; tool history reproduced from pack git)
- Area: ORCH
- Evidence:
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md:3` — `Verdict: **GO WITH CONDITIONS**` with `P0 x1, P1 x7`
  - `runs/falcon-20261005-full-main-e267ce1/RELEASE_GATE.md:5` — `Decision: **NO-GO**` for the same 34 findings; `INDEX.md:12` gate NO-GO
  - `tools/lib_findings.py:149-165` — shared rule: any P0 -> NO-GO
  - `git show 729b9f1:tools/publish_audit.py:198` — publisher gate at publication time treated P0 as GO WITH CONDITIONS; the pack unified the gate 30 min later (`1e2a086`, 2026-10-04 21:29) but the falcon artifact was only renamed (`427298b`), never reconciled
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/audit_manifest.json` — `profile: focused-security-supply-chain-ci`, `promptCount: 4`, `reports: [lens_focused_security_supply_chain_ci.md]`; the pack run of the same audit carries 42 domain reports
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/follow_up_register.md` — all 34 findings `open`; the pack register carries post-audit statuses (e.g. OBS-P0-001 `verified-fixed`)
- What is happening: two durable artifacts describe the same 2026-10-05 full-domain audit at `e267ce1`; the copy committed in the target repository says GO WITH CONDITIONS while carrying a P0, contradicts the pack's shared gate rule and the pack's canonical NO-GO, presents the full-domain findings under a 4-prompt "focused" profile with no domain reports, and keeps pre-reconciliation statuses.
- Why it matters: the repo copy is the record a reviewer/operator sees; it understates the release gate, cannot be traced to domain evidence, and disagrees with the canonical run.
- User / business impact: release/review decisions may rely on a weaker gate than the audit actually produced.
- Security / privacy / reliability impact: no runtime effect; it is an integrity/consistency defect in the audit record.
- Recommended fix: republish/reconcile the committed run from the canonical pack run (all domain reports + gate computed by the shared rule), or append an explicit reconciliation note; add a publish-time check that a P0-bearing run cannot emit GO/GO WITH CONDITIONS while unresolved.
- Suggested validation: regenerate the run folder from the pack run and re-run `automation/validation/audit_run_lifecycle.sh check`; assert gate consistency in the pack's `tools/check_run.sh`.
- Owner suggestion: audit-tooling owner.
- Effort estimate: S.
- Dependencies: access to the pack run folder.
- Status: open.

### ORCH-P2-002 - full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable

- Severity: P2
- Confidence: High
- Area: ORCH
- Evidence:
  - `tools/full_domain.py:203,219` — `"profile": "base"` written unconditionally
  - `tools/full_domain.py:224` — `"lenses": [d["area"] for d in domains]` (43 area codes)
  - `runs/falcon-20261009-2117-full-08e20d1/audit_manifest.json:68-112` — `lenses` = DET, ORCH, INV, ..., REL
  - `examples/audit_manifest.falcon-lab.example.json:101` and `profiles/falcon-lab.manifest.json:29-31` — `lenses` are the five lens records (ND/REV/INTG/LIVE/ADV)
  - `profiles/falcon-lab.md:51-104,118-131` — the falcon adaptation runs 46 prompts (incl. 41 EVID, 42 XREPO, 43 FLEET, 44 DQ) + 5 lenses + edge mirror; `prompts/MASTER_RUNNER_FALCON_LAB.md:37-69` wave plan
  - `tools/check_run.sh:47-52` — falcon-lab extras are required only when `profile == "falcon-lab"`, which this driver never emits
  - current run `scope.domains` — no `41_*`, `42_*`, `43_*`, `44_*` entries
- What is happening: the base full-domain driver cannot represent the pack's documented falcon profile. Both the prior and current "full" falcon runs are the base 42-prompt set; the falcon-only domains and the lens wave are skipped and the manifest's `lenses` key is filled with area codes instead of lens IDs.
- Why it matters: coverage claims ("full run") overstate what was audited for this target; evidence-doctrine, cross-repo pairing, edge-fleet and data-quality fidelity are not assessed; the manifest cannot be validated against the falcon-lab schema.
- User / business impact: gaps in the audit program for exactly the falcon-specific risks the profile was written for.
- Security / privacy / reliability impact: indirect (missing audits).
- Recommended fix: add a `--profile` option to `full_domain.py`; emit the falcon-lab manifest shape (lenses with IDs/targets/status, waves, repos/hosts) when auditing falcon; or record an explicit, documented scope reduction in the manifest.
- Suggested validation: `full_domain.py domains --profile falcon-lab` lists 46 prompts; a generated manifest validates against `examples/audit_manifest.falcon-lab.example.json`.
- Owner suggestion: audit-tooling owner.
- Effort estimate: M.
- Dependencies: falcon-lab profile wiring (`wiring/REPO_WIRING.md`).
- Status: open.

### ORCH-P3-001 - Run id does not start with the timestamp required by the consumer repo's lifecycle check

- Severity: P3
- Confidence: High
- Area: ORCH
- Evidence:
  - `tools/full_domain.py:185-191` — `default_run()` prefixes the repo name (`<repo>-<ts>-<mode>-<branch>-<sha>`) although its own comment (lines 186-189) says ids must start `YYYYMMDD-HHMM-` to satisfy consumer CI
  - `automation/validation/audit_run_lifecycle.sh:120-122` — a run id must match `^[0-9]{8}-[0-9]{4}-`
  - falcon commit `427298b` (PR #45) — renamed already-published runs for exactly this reason
  - `runs/falcon-20261009-2117-full-08e20d1/audit_manifest.json` — run `falcon-20261009-2117-full-08e20d1`
  - `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:24-33` — run folders must pass the structural check (valid id, not ignored)
- What is happening: the run id produced/selected for this run again starts with the repo name, so publishing it unchanged into `docs/audits/repo-deep-dive/` fails the target repo's lifecycle check and requires a rename commit.
- Why it matters: mechanical rework and a broken run record if published as-is; the same defect produced PR #45 on the previous run.
- User / business impact: minor process friction.
- Security / privacy / reliability impact: none directly.
- Recommended fix: make `default_run()` emit `<timestamp>-<mode>-<branch>-<sha7>` (repo recorded in `scope.name` only) or auto-rename at publish; add a publish-time regex assertion.
- Suggested validation: `audit_run_lifecycle.sh check` passes on the published folder without a rename.
- Owner suggestion: audit-tooling owner.
- Effort estimate: S.
- Dependencies: none.
- Status: open.

## Prior-Run Comparison

Prior ORCH report (`runs/falcon-20261005-full-main-e267ce1/00_audit_orchestrator.md`) recorded no findings ("orchestration-only domain"). This run adds three orchestration findings because the committed-record and manifest-fidelity defects are directly evidenced now. No prior ORCH finding exists to carry forward.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Weaker committed gate misleads release decisions | P2 | Medium | High | repo run RELEASE_GATE.md vs pack NO-GO | reconcile the record; publish-time gate check |
| Falcon-lab-only domains/lenses never audited under base runs | P2 | High | Medium | manifest domains list; profile docs | profile support in the driver |
| Published run-id rejected by repo lifecycle check | P3 | High | Low | audit_run_lifecycle.sh:120-122; PR #45 | fix default_run/publish rename |

## Recommendations

### Immediate / Release Blocking
- None (audit-record integrity only).

### This Week
- Reconcile the repo's `20261005-0354-full-main-e267ce1` record with the canonical pack run (ORCH-P2-001).
- Decide whether falcon runs are base or falcon-lab scope and record it in the manifest (ORCH-P2-002).

### This Month
- Add profile support + lens recording to `full_domain.py`; fix run-id generation (ORCH-P3-001).

### Later / Platform Evolution
- Add a machine check binding committed run records to the canonical run for the same audit.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Append a reconciliation note to the committed run | removes the gate contradiction without rewriting history | repo run folder | readers see one gate |
| Fix `default_run()` id shape | removes publish-time rename | `tools/full_domain.py` | lifecycle check passes |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Profile-aware manifest emission (falcon-lab) | P2 | tooling | M | profile schema |
| Publish-time gate/ID assertions | P2 | tooling | S | check_run.sh |
| Committed-run vs canonical-run binding check | P3 | tooling | M | run registry |

## Suggested Tests

- Unit: `full_domain.py` manifest emission for both profiles validates against the example schemas.
- CI: `check_run.sh` fails a run whose gate contradicts its P0/P1 counts.
- CI: publish step rejects a run id not matching `^[0-9]{8}-[0-9]{4}-`.
- Manual: re-read a committed run record against the canonical run and confirm gate/report/register equality.

## Suggested Documentation Updates

- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md`: note that pack run ids must be renamed to the repo convention at publish time (or that publish handles it).
- `profiles/falcon-lab.md` / `wiring/REPO_WIRING.md`: state explicitly that base-profile runs are a reduced scope for falcon.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was the base profile a deliberate scope decision for this run? | determines whether ORCH-P2-002 is a defect or a documented reduction | operator statement / manifest note |
| Should the committed 20261005 record be corrected or superseded? | lifecycle says never rewrite committed runs | owner decision |

## Limitations

- The current run was mid-flight at capture (no finals, no aggregate); final-file completeness could not be assessed.
- The repo's 20260930 falcon-lab run was used only for schema comparison, not re-audited.
- Live-host checks were read-only and timestamped in the ARCH report.

## Findings

| ID | Severity | Title |
|---|---|---|
| ORCH-P2-001 | P2 | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence |
| ORCH-P2-002 | P2 | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable |
| ORCH-P3-001 | P3 | Run id does not start with the timestamp required by the consumer repo's lifecycle check |
