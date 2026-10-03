# Platform Evolution and Extensibility Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab profile v1.0.0, pack v1.2.1)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: central `/home/user/falcon-build`; edge `/home/user/falcon-edge-build`
- Branch: `main` (both)
- Commit SHA: central `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c`; edge `f1c5defe6b66887ae49bc44c2cd79b37ad249663` (run started at edge `45dfed0`, which moved 9 commits during the run — re-checked before writing)
- Generated at: 2026-09-30T14:24Z
- Auditor: subagent, read-only
- Area code: EVOL
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/19_platform_evolution_extensibility.md`
- Scope limitations: no live-host mutation, no root/docker, no GitHub settings query (plan limits taken from `docs/GITHUB_CI.md`). The MCT upstream repo (`MaineCyberTech/soc`) is not accessible; only the imported subtree was reviewed.

## Scope

Reviewed: phase model and gates in both repos; additive/evolution doctrine; roadmap state; module boundaries and layout; shared packages and duplication; extension points (falcon compose/config/bootstrap/mct, edge profiles/deploy/API); feature flags; permission extensibility; tenant/org model; API versioning; migration strategy; eventing; integration framework; UI reuse; admin tooling; background jobs; config model; observability extensibility; docs for adding modules; AI-agent compatibility; package extraction. Not in depth: prompts 01/02/08/10/11/16/21/34/41/42 (cross-referenced only).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/phase0/IMPLEMENTATION_PLAN.md`, `docs/phase9/PHASE9_CHARTER.md`, `ledgers/gate_ledger.csv` (102), `ledgers/phase9_gate_ledger.csv` (14) | Phase/gate model | Evolution is gate-gated | Central 101 PASS / 1 N/A; phase 9 13 PASS / 1 N/A |
| Edge `AGENTS.md` rules 6–7; `docs/phase0/SCOPE_AND_BOUNDARIES.md`; `REPOSITORY.md`; edge `ledgers/gate_ledger.csv` (88) | Additive doctrine | Defines extension safety | Edge 77 PASS / 8 BLOCKED / 3 INSUFFICIENT_EVIDENCE |
| `compose/{central,probe}`, `mct/compose/`, `config/`, `bootstrap/` (21 steps) | Falcon extension surfaces | Where modules plug in | Per-zone compose projects |
| `mct/integrations/integration-matrix.md`, `payload-contracts/`, `failure-modes.md` | Integration framework | Add-a-route pattern | 11 routes each with contract + runbook |
| Edge `profiles/sensor/*`, `deploy/` units, `api/openapi/falcon-edge-v1.yaml`, `api/generate_models.py`, `src/falcon_common/`, `src/falcon_control/{service,store,http_server}.py` | Edge extension surfaces | Profiles/units/contract/runtime | Generated models with `--check`; roles hardcoded; SQLite store |
| `automation/evidence/capture.sh` (both), `automation/validation/`, `ci/validate.py`, `docs/phase9/ALERT_CATALOGUE.yaml` (31 alerts), `config/grafana/dashboards/*` | Shared tooling/observability | Duplication + extension patterns | capture.sh byte-identical; 3 dashboards-as-code |
| `closeout/OWNER_ACTIONS.md` (edge), `ledgers/{risk_register,decision_log}.md` (both) | Open evolution items | Roadmap state | No roadmap doc in either repo |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `bash automation/validation/verify_publication_chain.sh` (falcon) | Reproduction | State binding | `publication_chain_failures=0`; signed archives intact |
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` (falcon) | Reproduction | Static gate | 4 PASS + secret-scan FAIL (2 `long_hex` hits in this run's reports — report 20) |
| Gate-ledger recount (both) | Aggregate | Phase/gate claims | Counts reproduced with `csv.DictReader` |
| `diff` of `automation/evidence/capture.sh` across repos | Sample | Shared-package claim | rc=0; 126 lines each |
| Compose pinning coverage walk | Reproduction | mct extension safety | validate PASSes while `mct/compose/` has 29 unpinned refs incl. `:latest` |

## Executive Summary

Both programs evolve through gate-gated phases (central 0–9, edge 0–10) under an evidence-first, append-only, additive doctrine. Central flexes well inside its boundaries: numbered bootstrap steps, per-zone Compose projects, a documented integration matrix with payload contracts, generated alert catalogue and dashboards-as-code. Edge has the strongest formal extension design: typed profiles, systemd units, OpenAPI v1 with generated models, signed desired-state/update manifests, recovery directives. The gap is the playbook: no roadmap, no module template, duplicated shared tooling, an imported MCT subtree outside CI pinning, and no schema-migration mechanism for the edge control-plane store. No P0/P1 findings; four P2 and two P3.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Phase model (central) | `docs/phase0/IMPLEMENTATION_PLAN.md`; 2 ledgers | Gate-gated phases 0–9 | Closed; 101 PASS/1 N/A; phase 9 13/1 | Low | No in-repo phase-10 definition |
| Phase model (edge) | `docs/phase0..9/`, `tests/phase10/` | Gate-gated phases 0–10 | 77 PASS / 8 BLOCKED / 3 IE | Medium | No `docs/phase10/CLOSEOUT.md` (review F10) |
| Additive rule | Edge `AGENTS.md` rule 6; `SCOPE_AND_BOUNDARIES.md`; `mct/runbooks/phase12-change-control.md` | New capability must be additive/rollback-able | Documented, mostly followed | Low | Falcon lacks an equivalent shared-host rule |
| Module boundaries | `compose/{central,probe}`; edge `src/falcon_{agent,common,control,cli}`; `profiles/` | Separation of concerns | Clear, small modules | Low | Cross-repo tooling duplicated |
| Shared packages | Edge `src/falcon_common`; falcon `automation/` | Reuse | Edge has one; falcon none | Medium | Extraction candidate |
| Extension points | bootstrap steps; vector transforms; Wazuh rules; catalogue; integration matrix; profiles/units/API | Add capability | Rich but recipe-free | Medium | No module template |
| Permission extensibility | `bootstrap/60-central-deploy.sh` users; Traefik auth; edge roles | Add identities/roles | Config-list based | Medium | Bootstrap apply replaces user set (R-28) |
| API versioning | `api/openapi/falcon-edge-v1.yaml` (v1, schemaVersion 1.0) | Contract evolution | Versioned + drift-checked | Medium | Component/service versions differ |
| Migration strategy | Wazuh migration record; edge `store.py` | Change data/layout | Rehearsed with snapshots; no store migrations | Medium | EVOL-P2-003 |
| Docs for adding modules / package extraction | per-case runbooks; `mct/` (856 files) | Onboarding/consolidation | No guide/template; vendored subtree | Medium | EVOL-P2-001 / EVOL-P2-004 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Module boundaries | 4 | per-zone compose, small edge modules, profiles | No formal boundary contract | Add a boundary register |
| Domain model | 3 | gate statuses, `LifecycleState` enum, schemas | Entities spread across ledgers/configs | Document domain model |
| Shared packages | 3 | edge `falcon_common`; duplicated capture.sh | No cross-repo shared package | Extract shared tooling |
| Extension points | 3 | bootstrap steps, profiles, integration matrix | No template/recipe | Publish module template |
| Feature flags | 1 | absent | No staged activation | Document additive substitute |
| Permission extensibility | 3 | bootstrap user set, roles, mTLS | Hardcoded roles; replace-on-apply | Role registry + idempotent apply |
| Tenant/org model | 3 | single owner; site label; client templates | No multi-tenant abstraction | Accept for lab; document |
| API versioning | 4 | OpenAPI v1 + schemaVersion; CI lint/drift | Version policy undefined | Define version policy |
| Migration strategy | 2 | Wazuh migration record; SQLite store | No store migrations | Add `user_version` + migrations |
| Eventing/webhooks | 3 | ntfy, forwarder, edge events | Retry semantics undocumented | Document delivery semantics |
| Integration framework | 4 | matrix, contracts, failure modes | Routes MCT-only | Extend matrix to falcon/edge |
| UI reuse | 4 | 3 dashboards-as-code, generated catalogue | Edge rules not deployed | Ship rules with rollback |

## Detailed Review

### Item: Phase model and gates

- Evidence: `docs/phase0/IMPLEMENTATION_PLAN.md` safety rules 1–7; `docs/phase9/PHASE9_CHARTER.md`; edge `docs/phase0/SCOPE_AND_BOUNDARIES.md`; both gate ledgers.
- Current controls: evidence-first statuses (`NOT_RUN`…`NOT_APPLICABLE`), append-only registers, owner/reviewer boundaries.
- Missing controls: no definition of "phase 10+", how new modules/sites are numbered, or how capabilities are retired.
- Risk: evolution direction lives in decision logs and audit reports rather than a roadmap (EVOL-P2-001).

### Item: Extension points (central and edge)

- Evidence: `compose/{central,probe}`, `bootstrap/*.sh`, `config/vector/edge.yaml`, `docs/phase9/ALERT_CATALOGUE.yaml` (regenerated from live rules), `mct/integrations/integration-matrix.md`, edge `profiles/sensor/*` + `validate_configs.py`, `deploy/*.service`, OpenAPI + `api/generate_models.py --check`.
- Current controls: profile validator; compose pinning (central only); CI contract/model drift checks; integration contracts.
- Missing control: no single "add a module" template (code + config + evidence + gate + dashboard/alert + rollback) — EVOL-P2-001.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EVOL-001 | Module boundaries | compose/src layout | per-zone/per-package | No boundary contract | P3 | boundary register |
| EVOL-002 | Domain model | gate statuses, enums | enums in OpenAPI | Entities not modeled centrally | P3 | domain doc |
| EVOL-003 | Shared packages | capture.sh diff=0 | duplication | no shared package | P2 | extract + version |
| EVOL-004 | Extension points | matrix/profiles/units | documented patterns | no template | P2 | module template |
| EVOL-005 | Feature flags | grep: none | additive deploy + update channels | no flags | P3 | document substitute |
| EVOL-006 | Permission extensibility | bootstrap users/roles | config lists, mTLS | replace-on-apply; hardcoded roles | P3 | registry + merge |
| EVOL-007 | Tenant/org model | single owner; site label | single tenant by design | none for lab | P3 | accept/document |
| EVOL-008 | API versioning | v1 + schemaVersion | URL major + payload schema | components drift | P3 | version policy |
| EVOL-009 | Migration strategy | migration record; store | rehearsed, snapshots | no DB migrations | P2 | schema_version + runner |
| EVOL-010 | Eventing | ntfy/forwarder/events | alerts delivered | retry contract undocumented | P3 | document semantics |
| EVOL-011 | Integration framework | matrix + contracts | 11 documented routes | MCT-only | P3 | extend matrix |
| EVOL-012 | UI reuse | dashboards-as-code | 3 dashboards | edge rules not deployed | P2 | ship with rollback |

## Findings

### Finding ID: EVOL-P2-001 - No in-repo roadmap, evolution guide, or module template

- Severity: P2 · Confidence: High · Area: EVOL · Repo: both
- Evidence: `grep -rniE "roadmap|phase 10|module template"` over `docs/`, `ledgers/`, root `*.md` (excluding audit outputs) returns no roadmap/evolution document; falcon `README.md` lines 8–13 still describe the 2026-09-24 open-gate state; extension knowledge is scattered across `docs/runbooks/{SITE_HOST_ONBOARDING,WAZUH_INTEGRATION}.md` and `mct/integrations/integration-matrix.md`.
- What is happening: the platform evolved through 9–10 gated phases but has no forward plan or reusable recipe for the next module/site/integration.
- Why it matters: owners and agents cannot answer "what next and how" from the repository; work restarts from audit reports.
- User / business impact: slower onboarding of the next capability; duplicated discovery effort.
- Security / privacy / reliability impact: low direct; indirect via inconsistent rollout rigor.
- Recommended fix: add `docs/architecture/EVOLUTION.md` (roadmap + add-a-module template + gate checklist); link from both READMEs and AGENTS.md.
- Suggested validation: doc-drift check that the roadmap current-state block matches the gate ledger; walk the template once.
- Owner suggestion: falcon + edge maintainers · Effort: S · Dependencies: none · Status: open

### Finding ID: EVOL-P2-002 - Shared tooling duplicated across repos instead of a versioned package

- Severity: P2 · Confidence: High · Area: EVOL · Repo: both
- Evidence: `diff falcon-build/automation/evidence/capture.sh falcon-edge-build/automation/evidence/capture.sh` → rc=0, both 126 lines; parallel `automation/evidence/{index.sh,manifest.sh}` and validation trees; edge has `src/falcon_common/`, falcon has no shared package.
- What is happening: safety-critical capture/evidence tooling is copied, so fixes (e.g., redaction patterns) must be applied twice.
- Why it matters: divergence breaks evidence comparability across the pairing; one repo can silently lag.
- User / business impact: reviewer effort increases; cross-repo checks must special-case each copy.
- Security / privacy / reliability impact: a redaction fix applied to one copy only leaves the other leaking patterns.
- Recommended fix: extract shared tooling to a small versioned package, or vendor with a digest pin plus a mirror-check in both CIs.
- Suggested validation: cross-repo hash-compare CI job that fails when copies differ.
- Owner suggestion: both maintainers · Effort: M · Dependencies: release-freeze rules · Status: open

### Finding ID: EVOL-P2-003 - Edge control-plane SQLite store has no schema migration mechanism

- Severity: P2 · Confidence: High · Area: EVOL · Repo: edge
- Evidence: `src/falcon_control/store.py` lines 13–113: `SCHEMA = "CREATE TABLE IF NOT EXISTS ..."` for 7 tables; no `PRAGMA user_version`, `ALTER TABLE`, or migration module (`grep -rn "ALTER|migrat|schema_version" src/` → none); the update bundle (`automation/validation/build_agent_bundle.sh`) ships only `falcon_agent`.
- What is happening: existing DBs can never be altered by a release; a future column/table change simply does not apply.
- Why it matters: upgrades fail or silently run old schemas, breaking enrollment/heartbeats/audit writes.
- User / business impact: control-plane upgrade path undefined; rollback/data-repair burden.
- Security / privacy / reliability impact: code/DB divergence; audit rows lost if operators recreate DBs.
- Recommended fix: schema-version table + ordered migrations applied at startup with a pre-migration backup.
- Suggested validation: migration tests from a frozen old-schema DB fixture; CI check that schema changes have migrations.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: EVOL-P2-004 - MCT subtree vendored without pin/upstream policy and outside CI image pinning

- Severity: P2 · Confidence: High · Area: EVOL · Repo: falcon
- Evidence: `mct/` = 856 tracked files with its own README/CI badge (`mct/README.md` line 3), no submodule/upstream commit marker; `grep image: mct/compose/*.yml | grep -v @sha256` → 29 unpinned refs including `:latest`/`:stable`; `ci/validate.py` `check_compose_pins()` globs only `compose/**` (lines 77–103) and `pins/images.lock` (18 images) has no mct entries, yet validate reports "PASS compose image pinning".
- What is happening: imported MCT compose files are staged for revival (`docs/runbooks/MCT_CONSOLIDATION.md` lines 86–88) but are exempt from the repo's pinning policy.
- Why it matters: reviving a staged service bypasses the supply-chain control every first-party compose file must satisfy.
- User / business impact: unreviewed images could run on the shared host; policy confidence overstated by CI.
- Security / privacy / reliability impact: floating tags on a shared monitoring host; supply-chain risk.
- Recommended fix: include `mct/compose/**` in the pin check (or an explicit exceptions file with owner/expiry), pin/classify every mct image, record the upstream commit.
- Suggested validation: CI fails on unpinned mct compose refs; lock coverage report.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: MCT revival decision · Status: open

### Finding ID: EVOL-P3-001 - Hardcoded roles/versions with no registry or version policy; bootstrap apply replaces the identity set

- Severity: P3 · Confidence: High · Area: EVOL · Repo: both
- Evidence: edge `src/falcon_control/service.py` lines 216–220 hardcode `operator`/`sensor`; OpenAPI line 4 says `1.0.0` while `http_server.py` line 15 announces `FalconEdgeControl/0.1.0`, `runner.py` line 26 `AGENT_VERSION = "0.1.0"` and the delivered bundle is `falcon-agent-0.1.1-lab` (review line 57); falcon R-28 (`risk_register.md` line 35): a `bootstrap/60-central-deploy.sh` rerun deleted ad-hoc users `falcon-healthcheck`/`falcon-backup`.
- What is happening: adding a role, profile, user or version requires code/config edits and can remove undeclared identities; component/API/schema/bundle versions move independently.
- Why it matters: extension cost and regression risk; operators cannot tell which agent pairs with which control plane.
- User / business impact: new roles/users need maintainer work and careful reruns; upgrade/rollback confusion.
- Security / privacy / reliability impact: identity loss from reruns can break monitoring/backup accounts (observed once).
- Recommended fix: make the bootstrap identity apply merge-safe or fail loud; document a role registry; define one version policy incl. `minAgentVersion`.
- Suggested validation: rerun test asserting undeclared users are preserved or reported; CI check heartbeat versions against the contract.
- Owner suggestion: both maintainers · Effort: S · Dependencies: none · Status: open

### Finding ID: EVOL-P3-002 - No feature-flag mechanism; additive deploy is the only staging control

- Severity: P3 · Confidence: High · Area: EVOL · Repo: both
- Evidence: `grep -rniE "feature[_ -]?flag|FEATURE_[A-Z]|ENABLE_[A-Z]"` over falcon docs/compose/config/automation and edge src/config/deploy/api returns only unrelated OpenSearch settings (`enable_for_single_data_node`) and Suricata rule text; edge update channels `canary|lab|stable` exist in `UpdateManifest`.
- What is happening: new monitors/rules/endpoints become active as soon as deployed; staging relies on additive deploy + rollback.
- Why it matters: gradual rollout of risky extensions is manual; no per-feature kill switch.
- User / business impact: low for a single-owner lab; higher as fleets grow.
- Security / privacy / reliability impact: rollback is per-deploy, not per-feature.
- Recommended fix: document the additive-deploy + update-channel substitute as official; add flags only for fleet-scale features.
- Suggested validation: canary-channel rollout exercise; document outcome.
- Owner suggestion: both maintainers · Effort: S · Dependencies: none · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Staged MCT services revived with floating tags | P2 | Medium | Medium | `mct/compose/*.yml`; CI glob | EVOL-P2-004 |
| Control-plane DB cannot be migrated in place | P2 | Medium | High | `store.py` SCHEMA | EVOL-P2-003 |
| Cross-repo tooling drifts | P2 | Medium | Medium | identical capture.sh | EVOL-P2-002 |
| Evolution work restarts from audit reports | P2 | High | Medium | no roadmap | EVOL-P2-001 |

## Recommendations

### Immediate / Release Blocking
- None in this domain (no P0/P1).

### This Week
- EVOL-P2-004: extend pinning checks to `mct/compose/**` or record an explicit exception table; EVOL-P2-003: add SQLite `user_version` + ordered migrations.

### This Month
- EVOL-P2-001: publish `docs/architecture/EVOLUTION.md` (roadmap + module template + gate checklist); EVOL-P2-002: extract/pin shared evidence tooling with a cross-repo hash check.

### Later / Platform Evolution
- EVOL-P3-001/002: role registry and version policy; capability flags only if the fleet grows.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Extend pin check to mct | Applies the policy where CI is blind | `ci/validate.py` | validate green with mct check |
| 1-page "add a module" checklist | Reusable recipe | new `docs/architecture/` doc | walkthrough with one real change |
| Record upstream commit for mct import | Provenance | `mct/README.md` | commit exists upstream |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Module template + roadmap | P2 | falcon maintainer | S | none |
| Shared tooling package/pin | P2 | both maintainers | M | release freeze |
| SQLite migrations | P2 | edge maintainer | M | none |
| mct pin enforcement | P2 | falcon maintainer | M | MCT revival decision |
| Identity/version policy | P3 | both maintainers | S | none |

## Suggested Tests

- Unit: migration runner v1→v2 on a frozen DB fixture; profile validator rejects unbounded buffers.
- Integration: cross-repo capture.sh hash equality job; mct compose pin check fails on a doctored `:latest`.
- E2E: add a synthetic site via `SITE_HOST_ONBOARDING.md`; confirm `falcon_site_*` series + alert evaluation.
- Regression: bootstrap rerun preserves undeclared OpenSearch users (R-28 class).

## Suggested Documentation Updates

- New: `docs/architecture/EVOLUTION.md` (falcon) — roadmap, module template, gate checklist.
- New: `docs/architecture/MODULE_TEMPLATE.md` (edge) — profile + unit + contract + rollback recipe.
- Update: `mct/README.md` — upstream commit, ownership, CI coverage inside falcon.
- Update: falcon `README.md` current-state block after closure.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `mct/` intended to stay in falcon-build or be extracted? | Determines pin/CI policy | owner decision / `mct/PORTABILITY.md` |
| Are staged MCT services going live? | Pins become enforcement-critical | `closeout/OWNER_ACTIONS.md` §6 follow-up |

## Appendix

- Edge open gates at `f1c5def`: P0-G03/G05/G06 (IE); P6-G04/G06, P7-G05, P9-G05/G06, P10-G02/G04/G06 (BLOCKED).
- Central open items: none in gates; open risks include R-15, R-24 residual, R-27 residual (risk register).
- Edge update channels `canary|lab|stable`; recovery directives `RESET_CONFIG`, `SWITCH_SLOT`, `ENTER_RECOVERY`, `EXIT_QUARANTINE`, `UPLOAD_DIAGNOSTICS`; alert catalogue 31 alerts; dashboards central-overview (34 panels), feeds-overview (31), edge-fleet-overview (7).
