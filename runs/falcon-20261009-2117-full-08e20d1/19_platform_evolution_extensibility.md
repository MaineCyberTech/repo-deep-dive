# 19_platform_evolution_extensibility — Prompt 19 - Platform Evolution and Extensibility Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `19_platform_evolution_extensibility.md` (area EVOL, prompt)

## Verification Performed

# Platform Evolution and Extensibility Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d` (short `08e20d1`)
- Branch: `main` (target pinned at 08e20d1; the clone's `main` ref now points at `6e4fccd` and `ops/20261009-snapshot-repo-relocate-clean` at `c13a416` — both used only as post-audit context, never as the audited tree)
- Generated at: 2026-10-09T21:50:40Z · Auditor: repo-deep-dive subagent (prompt 19) · Area code: EVOL
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/19_platform_evolution_extensibility.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo password read from the owner file in a subshell, never printed); no state mutated; no formal compliance claimed — SOC2/ISO27001/NIST/CIS/OWASP/GDPR/CCPA/HIPAA/PCI/CMMC are used as readiness lenses only. Edge-repository surfaces (sensor images, edge delivery directory, edge SQLite store) are outside this repository and are referenced through owner-action C13. Edge-repository extension surfaces are referenced but not assessed (single-repo scope).


## Scope

Reviewed at `08e20d1`: module/file conventions, domain/data contract (event schema), shared packages, extension points, feature staging (flags), permission/identity extensibility, tenant/org model (single-tenant lab; site model), API versioning, migration strategy, eventing/webhooks, integration framework, UI reuse, admin tooling, background jobs, config model, observability extensibility, docs for adding modules, AI-agent compatibility, package extraction. Not reviewed: the edge repository's implementation (its SQLite migrations and OpenAPI are edge-owned; referenced).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/EVOLUTION_GUIDE.md` | doc | Extension model, conventions, checklists, module template, roadmap | Written 2026-10-01 for EVOL-P2-001 |
| `docs/architecture/SHARED_TOOLING_POLICY.md` | doc | Cross-repo tooling duplication + options | Status "proposed"; no enforcement |
| `mct/VENDORING.md` | doc | Vendored subtree policy | Status "proposed"; 29/37 unpinned refs |
| `ci/validate.py:106-137,142-158` | code | Pin check scope; digest cross-check | Pin check globs `compose/**` only; digest check covers `mct/compose` + `automation/wazuh` with waivers |
| `pins/images.lock`, `pins/supply-chain-waivers.json` | config | Pins + explicit waivers | mct/compose waived to 2026-12-31 |
| `bootstrap/60-central-deploy.sh:143-151,207` | code | Identity apply semantics | Config-driven securityadmin apply replaces the internal-user set |
| `ledgers/risk_register.md` (R-28) | ledger | Observed identity-apply hazard | CLOSED via declaration + verify-after-rerun |
| `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-1/E-2/E-4 | doc | Owner decisions pending | Shared tooling, MCT, identity apply, flags |
| `docs/runbooks/{RUNTIME_AND_SCHEDULE,MCT_CONSOLIDATION,SITE_HOST_ONBOARDING}.md` | docs | Background jobs, MCT live/staged, site extension | Present |
| `config/opensearch/falcon-eve-template.json`, `config/vector/*.yaml` | config | Data contract + ingest extension points | Template pinned, `dynamic:false` |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Read `EVOLUTION_GUIDE.md` §2,§4,§6,§7,§8,§9 | inspect | Extension points + templates + policies | Module template at §6 (`:237-266`); roadmap §7; identity §8; staging §9 |
| Read `SHARED_TOOLING_POLICY.md`; `ls automation/shared-tooling.lock automation/validation/shared_tooling_check.sh` | inspect | Enforcement existence | Both absent — option B not implemented |
| Count image refs under `mct/compose/` (read-only script) | reproduce | VENDORING claim | 37 refs; 8 digest-pinned; 29 unpinned; 11 floating |
| `python3 automation/validation/check_compose_digests.py --compose-dir mct/compose --waivers pins/supply-chain-waivers.json` | reproduce | Is the CI blind spot mitigated? | `compose_digest_findings=0; compose_digest_waived=35` (explicit, expiring waiver) |
| `grep` for feature-flag mechanisms | inspect | EVOL-P3-002 | None found (only vendored MCT narrative "kill switch" references) |
| `grep -rn sqlite` in falcon tree | inspect | EVOL-P2-003 | No references — edge-side |
| Read R-28 + `bootstrap/60-central-deploy.sh` comment | inspect | Identity merge-safety | Replace-on-apply documented; identities declared; verify control |
| Read `docs/edge/EDGE_RELEASE_PIN.md`, `JOINT_RELEASE_PROCEDURE.md` | inspect | API/pair versioning | Pin machine-checked; `verify_edge_pin.py` PASS in gate |

## Executive Summary

The extension model is genuinely strong for a lab of this size: `EVOLUTION_GUIDE.md` gives file conventions, per-extension checklists (service, feed, alert rule, backup class, site host, automation module), a copy-paste module template, a worked wave example, an identity/version registry with the R-28 hazard, and an explicit "no flags — additive deploy + canary + rollback" staging policy. The open evolution risks are the two cross-cutting policies that are documented but not enforced: (1) shared tooling between the paired repositories has drifted once already (a security fix landed in falcon only) and still has no pin/hash check — owner decision E-1/C7 pending; (2) the vendored MCT subtree has 29/37 unpinned image refs, no recorded upstream commit, and the pin gate still globs `compose/**` only — partially mitigated by explicit expiring waivers in the digest cross-check, owner decision E-2/C8 pending. A third residual: the OpenSearch identity apply is not merge-safe (R-28 closed through declaration + verify, owner decision E-4a pending), and feature flags remain intentionally absent (documented substitute; owner acceptance E-4b pending). Recommended: implement option B for shared tooling (or record the decision), extend pin enforcement/archive-only enforcement for `mct/compose`, and decide the identity-apply hardening.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Extension guide | `docs/architecture/EVOLUTION_GUIDE.md` | Conventions + checklists + template | Implemented | Low | State block stale (DOC finding) |
| Module template | `EVOLUTION_GUIDE.md` §6 | Copy-paste automation module | Implemented | Low | — |
| Shared tooling | `SHARED_TOOLING_POLICY.md`; capture.sh, secret_scan.py etc. | Evidence/scanning tools | Proposed; drift observed | High | No lock/check |
| MCT subtree | `mct/` (856 files) | Vendored MCT stack | Archive-only by policy; unenforced | High | 29 unpinned refs |
| Identity registry | `EVOLUTION_GUIDE.md` §8.1; `bootstrap/60-central-deploy.sh:160-215` | OpenSearch users/roles | Implemented; replace-on-apply | Medium | R-28 closed via control |
| Version policy | `EVOLUTION_GUIDE.md` §8.2 | Interface/component versions | Proposed policy | Low | Edge-owned parts |
| Feature staging | `EVOLUTION_GUIDE.md` §9 | Additive deploy substitute | Documented; no flags | Low | Owner acceptance pending |
| Data contract | `config/opensearch/falcon-eve-template.json` | Pinned 75-property template | Implemented | Low | `dynamic:false` |
| Background jobs | `config/systemd/falcon-*.{service,timer}`; `RUNTIME_AND_SCHEDULE.md` | Scheduled work | Implemented | Low | Documented cadence |
| Observability extension | `automation/validation/export_monitor_metrics.sh`; `service_probe.sh`; `bootstrap/90-alerting.sh` | Metric/rule extension points | Implemented | Low | `SITE_HOSTS` env-overridable default |
| Edge contract | `docs/edge/EDGE_RELEASE_PIN.md`; `verify_edge_pin.py` | Pair version pin | Machine-checked | Low | Offline self-check in gate |
| UI reuse | `config/grafana/dashboards/*.json`; `config/dashboards/*.json` | Dashboards/saved objects as code | Implemented | Low | 3 dashboards |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Module boundaries | 4 | compose projects; config/; bootstrap numbering; EVOLUTION_GUIDE §2 | — | Keep |
| Domain model | 3 | Event template; site/sensor identity | No formal domain model (ops platform) | Keep template pin |
| Shared packages | 1 | SHARED_TOOLING_POLICY (proposed) | No lock/hash check; drift observed | Implement option B (EVOL-P1-001) |
| Extension points | 4 | §4 checklists; write_rule; exporter | — | Keep |
| Feature flags | 2 | §9 substitute; no mechanism | No per-feature off switch | Accept or fund (E-4b) |
| Permission extensibility | 3 | §8.1 registry; declared identities | Apply not merge-safe | E-4a decision |
| Tenant/org model | 3 | Single-tenant lab; site model; SITE_HOST_ONBOARDING | Multi-site is label-based only | Extend at fleet scale |
| API versioning | 3 | Edge API v1 (edge repo); version policy proposed | Central has no HTTP API | Record policy acceptance |
| Migration strategy | 3 | Index rename + rollback drill; ISM; docker volume migration | Edge SQLite migrations out of repo | Edge-side |
| Eventing/webhooks | 2 | Grafana→relay→ntfy; relay hardening | No replay/idempotency evidence (WH-P3-001, other domain) | Harden (other domain) |
| Integration framework | 2 | MCT staged/vendored; Vector sources/sinks | No first-party integration SDK | Keep checklists |
| UI reuse | 4 | Dashboards-as-code; saved objects | — | Keep |

## Detailed Review

### Item: Module boundaries and extension flow

- Evidence: `EVOLUTION_GUIDE.md:52-75` (artifact→location table), `:96-195` (per-extension checklists), `:237-266` (module template), `:196-235` (worked DQ/CTR wave).
- Assessment: clear, additive, evidence-producing extension model; the canonical flow includes validate + evidence + ledger row + publication rebind.

### Item: Shared tooling (EVOL-P1-001)

- Evidence: `SHARED_TOOLING_POLICY.md:1-7` (status proposed; no implementation), `:27-38` (duplication map: 7 same-path tools; 2 identical/5 differ; parallel scanners), `:40-50` (capture wrapper drift — falcon hardened; edge copy still exports credentials), `:85-116` (option B sketch: per-repo `automation/shared-tooling.lock` + `shared_tooling_check.sh` in both CIs — **not present**: `ls` fails), `docs/phase9/OWNER_ACTIONS.md:78` (C7), `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-1.
- Assessment: the predicted failure (asymmetric security fix) already happened; the enforcement design is recommended but undecided/undone. Keep open.

### Item: MCT vendoring (EVOL-P1-002)

- Evidence: `mct/VENDORING.md:3-7` (policy proposed), `:38-48` (37 refs: 8 pinned / 29 unpinned / 11 floating; "Blind spot demonstrated" for `--only compose-pins`), `:50-78` (P1 record upstream commit; P3 archive-only; P4 CI coverage — proposed), `:115-127` (open; coordinator follow-up); `ci/validate.py:106-137` (`check_compose_pins()` globs `compose/**`); `ci/validate.py:142-158` (`check_compose_digests()` covers `mct/compose` + `automation/wazuh`; PASS with 35 waived findings, waiver `review_by 2026-12-31`); read-only recount confirms 37/8/29/11.
- Assessment: partially mitigated by explicit expiring waivers, but the policy's enforcement (pin coverage or archive-only enforcement) and the upstream pin are still missing. Keep open.

### Item: Identity/permission extensibility (EVOL-P2-001)

- Evidence: `bootstrap/60-central-deploy.sh:143-151` (comment: the securityadmin apply "REPLACES the whole internal-user set"; all identities must be declared), `:207` (`securityadmin.sh -f /tmp/internal_users.yml -t internalusers -icl`); `ledgers/risk_register.md` R-28 (CLOSED; declared identities + verify-after-rerun); `EVOLUTION_GUIDE.md:311-320` (hazard + "Recommended follow-up (runtime, not done here): make the apply merge-safe or fail loud"); `OWNER_DECISION_PACKAGE` E-4a.
- Assessment: the observed break is controlled, but adding an identity out-of-band is still a foot-gun; the merge-safe/fail-loud apply is not implemented.

### Item: Feature staging (EVOL-P3-002)

- Evidence: `EVOLUTION_GUIDE.md:340-360`; grep for flag mechanisms returns none in first-party code; owner decision E-4b pending.
- Assessment: documented substitute is reasonable at this scale; record the owner acceptance to close it.

### Item: API/pair versioning and migration

- Evidence: `docs/edge/EDGE_RELEASE_PIN.md` (pin + machine check; rebind procedure), `JOINT_RELEASE_PROCEDURE.md`; `automation/validation/verify_edge_pin.py` + offline self-check PASS in the gate; `EVOLUTION_GUIDE.md:322-338` (version policy proposed); index rename migration + rollback drill (`automation/validation/index_rename_migration.sh`, `index_rename_rollback_drill.sh`); Docker volume migration runbook + helper.
- Assessment: strong for central; edge SQLite migration mechanism remains edge-owned (EVOL-P2-003 out of repo).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EVOL-001 | Module boundaries | `EVOLUTION_GUIDE.md:52-75` | Conventions documented | — | — | Keep |
| EVOL-002 | Domain model | `falcon-eve-template.json` | Pinned template | No formal model (ops) | P3 | Keep pin checks |
| EVOL-003 | Shared packages | `SHARED_TOOLING_POLICY.md` | Policy proposed | No enforcement; drift observed | P1 | EVOL-P1-001 |
| EVOL-004 | Extension points | Guide §4 | Checklists + template | — | — | Keep |
| EVOL-005 | Feature flags | Guide §9 | Additive substitute | No off switch | P3 | EVOL-P3-002 |
| EVOL-006 | Permission extensibility | `bootstrap/60:143-151` | Registry + verify | Apply not merge-safe | P2 | EVOL-P2-001 |
| EVOL-007 | Tenant/org model | Site model; onboarding runbook | Single-tenant lab | Fleet-scale gap | P3 | Revisit at scale |
| EVOL-008 | API versioning | Edge pin; §8.2 | Pin machine-checked | Central has no API | P3 | Record policy |
| EVOL-009 | Migration strategy | Rename + rollback drill; volume migration | Tested | Edge SQLite out of repo | P3 | Edge-side |
| EVOL-010 | Eventing/webhooks | Relay + ntfy; WH-P3-001 | Hardened relay | Replay/idempotency (other domain) | P2 | Other domain |
| EVOL-011 | Integration framework | MCT staged; Vector | Checklists | No first-party SDK | P3 | Keep staged policy |
| EVOL-012 | UI reuse | Dashboards-as-code | Implemented | — | — | Keep |

## Findings

### EVOL-P1-001 - Cross-repo shared tooling has drifted and still has no pin/hash enforcement

- Severity: P1
- Confidence: High
- Area: EVOL
- Evidence:
  - `docs/architecture/SHARED_TOOLING_POLICY.md:1-7` ("Status: **proposed** 2026-10-01; … Nothing was implemented cross-repo")
  - `docs/architecture/SHARED_TOOLING_POLICY.md:27-38` (7 same-path tools; 2 identical / 5 differ; two parallel secret scanners with non-overlapping pattern coverage)
  - `docs/architecture/SHARED_TOOLING_POLICY.md:40-50` (§2.1: falcon's capture wrapper hardened 2026-10-01; the edge copy still `set -a; . "$ENV_FILE"`, uses `PIPESTATUS[0]`, misses the `falcon-` topic redaction)
  - `docs/architecture/SHARED_TOOLING_POLICY.md:85-116` (option B sketch: `automation/shared-tooling.lock` + `shared_tooling_check.sh` — **not implemented**; `ls` finds neither file)
  - `docs/phase9/OWNER_ACTIONS.md:78` (C7 choice owner); `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-1 (decision unsigned)
  - Falcon side verified hardened: `automation/evidence/capture.sh:1-13,82-98` (single-key sudo read; `PIPESTATUS[1]`); `ci/validate.py` credential-sourcing PASS
  - Prior findings: 20261002 run EVOL-P1-001 (P1); 20260930 run EVOL-P2-002
- What is happening: safety-critical tools are duplicated across the paired repositories without a pin or hash check; drift has already produced an asymmetric security fix, and the enforcement design (option B) is proposed but unimplemented and undecided.
- Why it matters: "the same tool" behaves differently in each repository; a security fix can silently miss one side, and evidence/scanning comparability is not guaranteed.
- User / business impact: asymmetric credential handling/scanning across the program; audit findings can differ per side.
- Security / privacy / reliability impact: a known credential-handling fix is absent on the edge side until the edge session mirrors it.
- Recommended fix: record the owner choice (E-1; recommended option B) and implement it: shared-file manifest per repo + a read-only cross-repo check wired into both CIs, with a small intentional-fork allowlist (owner + expiry); unify the capture wrapper and scanner pattern sets first.
- Suggested validation: `shared_tooling_check.sh` fails when a shared file differs and passes when mirrored; mutation test for the manifest.
- Owner suggestion: both maintainers + independent reviewer (E-1) · Effort: M · Dependencies: owner choice + edge session
- Status: open (owner-gated)
- Attack path: none identified (process/assurance risk)

### EVOL-P1-002 - MCT vendoring policy is proposed but not enforced; the pin gate is still blind to `mct/compose`

- Severity: P1
- Confidence: High
- Area: EVOL
- Evidence:
  - `mct/VENDORING.md:3-7` ("Status: **policy proposed** 2026-10-01; owner decision pending")
  - `mct/VENDORING.md:38-48` (37 image refs: 8 digest-pinned / 29 unpinned, 11 floating; `check_compose_pins()` globs `compose/**` only; "Blind spot demonstrated")
  - `mct/VENDORING.md:50-78` (P1 record upstream commit — current upstream commit unknown; P4 CI coverage proposed, not implemented)
  - Read-only recount at `08e20d1`: 37 refs / 8 pinned / 29 unpinned / 11 floating (same as the policy doc)
  - `ci/validate.py:106-137` (`check_compose_pins()` scope); `ci/validate.py:142-158` (`check_compose_digests()` now covers `mct/compose` + `automation/wazuh`); `pins/supply-chain-waivers.json` (mct/compose waived, reason TB-8, `review_by 2026-12-31`)
  - `docs/phase9/OWNER_ACTIONS.md:79` (C8); `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-2
  - Prior findings: 20261002 run EVOL-P1-002 (P1); 20260930 run EVOL-P2-004
- What is happening: the vendored subtree carries unpinned/floating images and no recorded upstream commit; the pin check still does not cover it, and the digest cross-check only passes because of an explicit, expiring waiver.
- Why it matters: reviving a staged MCT service would bypass the supply-chain control unless the waiver is re-examined; there is no vendor-drift check against an import manifest.
- User / business impact: supply-chain exposure if staged services go live.
- Security / privacy / reliability impact: an unpinned image can change under a deployment.
- Recommended fix: implement VENDORING P4 (extend the pin check to `mct/compose/**` with an explicit exceptions table, or enforce archive-only), record the upstream pin at the next import, and keep the waiver expiry visible; decide E-2a/E-2b.
- Suggested validation: `ci/validate.py --only compose-pins` fails on a floating ref under `mct/compose/` unless waived; import-manifest drift test.
- Owner suggestion: coordinator + maintainer (C8/E-2) · Effort: M
- Status: open (partially mitigated by explicit waivers)
- Attack path: none identified

### EVOL-P2-001 - The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending)

- Severity: P2
- Confidence: High
- Area: EVOL
- Evidence:
  - `bootstrap/60-central-deploy.sh:143-151` (comment: the config-driven securityadmin apply "REPLACES the whole internal-user set, so ad-hoc users are deleted on every bootstrap re-run (finding R-28 …)")
  - `bootstrap/60-central-deploy.sh:207` (`securityadmin.sh -f /tmp/internal_users.yml -t internalusers -icl -nhnv`)
  - `ledgers/risk_register.md` R-28 (CLOSED: identities now declared + verify-after-rerun control; originally broke the exporter and snapshot job)
  - `docs/architecture/EVOLUTION_GUIDE.md:311-320` ("Recommended follow-up (runtime, not done here): make the apply merge-safe or fail loud when an undeclared user exists (audit EVOL-P3-001)")
  - `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-4a (decision unsigned)
  - Prior findings: 20261002 run EVOL-P2-001; 20260930 run EVOL-P3-001 (same issue)
- What is happening: adding an identity out-of-band is silently undone on the next bootstrap re-run; the control is "declare everything and verify after", not merge-safety.
- Why it matters: a future extension (new dashboard reader, new exporter) can break services silently until the verify step catches it.
- Recommended fix: make the apply merge-safe or fail loud on undeclared users; keep the declared registry as the source of truth.
- Suggested validation: fixture with an undeclared user blocks/fails the apply; post-rerun user-set check.
- Owner suggestion: maintainer (E-4a) · Effort: M
- Status: open (hazard closed; hardening pending)

### EVOL-P3-002 - No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence:
  - `docs/architecture/EVOLUTION_GUIDE.md:340-360` ("There is no feature-flag mechanism in either repository … The official substitute is **additive deploy + staged rollout + idempotent rollback**"; introduce real flags only at fleet scale)
  - Read-only grep for flag mechanisms in first-party code: none (only vendored MCT narrative "kill switch" references)
  - `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-4b (decision unsigned)
  - Prior finding: 20260930 run EVOL-P3-002
- What is happening: there is no per-feature kill switch; the substitute (additive deploy, canary/lab/stable channels for edge, rollback per change) is documented but not owner-accepted as official policy.
- Why it matters: at multi-site/fleet scale the absence of flags becomes a rollout risk; at lab scale it is acceptable.
- Recommended fix: record the owner acceptance of §9 (or fund the flag registry before the next multi-site expansion).
- Suggested validation: decision-log row; §9 referenced by the release procedure.
- Owner suggestion: both maintainers (E-4b) · Effort: S
- Status: open (documented substitute)

## Prior-Run Comparison

- Prior full run `falcon-20261005-full-main-e267ce1` emitted **no EVOL findings**; its same-domain report said "Evolution/extensibility policy exists (docs/architecture/EVOLUTION_GUIDE.md, mct/VENDORING.md). No active finding." This run agrees the policy exists and reports the enforcement/decision residuals.
- Lineage checks at `08e20d1`:
  - `EVOL-P2-001` (20260930: no in-repo roadmap/evolution guide/module template) — **verified-fixed**: `EVOLUTION_GUIDE.md` exists with the module template (`:237-266`) and the roadmap/state block (`:268-295`).
  - `EVOL-P1-001` (20261002: shared tooling drift) / `EVOL-P2-002` (20260930) — **still-open** (re-emitted as EVOL-P1-001).
  - `EVOL-P1-002` (20261002: MCT policy unenforced) / `EVOL-P2-004` (20260930) — **partially-fixed** (digest cross-check covers `mct/compose` with waivers; pin policy still unenforced; re-emitted).
  - `EVOL-P2-001` (20261002: identity apply) / `EVOL-P3-001` (20260930) — **partially-fixed** (R-28 closed via declaration + verify; merge-safety pending; re-emitted).
  - `EVOL-P3-002` (20260930: no feature flags) — **documented, owner acceptance pending** (re-emitted).
  - `EVOL-P2-003` (edge SQLite migrations) — **out of repo** (edge-owned; no sqlite references in the falcon tree).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Shared-tooling drift recurs | P1 | High | Asymmetric security/scanning | `SHARED_TOOLING_POLICY.md:40-50` | Option B enforcement |
| Vendored unpinned images revived | P1 | Medium | Supply chain | `mct/VENDORING.md:38-48` | P4 enforcement + upstream pin |
| Identity apply breaks services | P2 | Medium | Monitoring/backup outage | R-28; `60-central-deploy.sh:143-151` | Merge-safe apply |
| No flags at fleet scale | P3 | Low | Rollout risk | `EVOLUTION_GUIDE.md:340-360` | Accept or fund |

## Recommendations

### Immediate / Release Blocking

None.

### This Week

1. Record E-1 (shared tooling) and start option B — EVOL-P1-001.
2. Record E-2/C8 and extend the pin check (or enforce archive-only) for `mct/compose` — EVOL-P1-002.

### This Month

3. Decide E-4a (merge-safe identity apply) — EVOL-P2-001.
4. Decide E-4b (feature staging policy) — EVOL-P3-002.

### Later / Platform Evolution

5. Define the multi-site/tenant model and flag registry before fleet expansion.
6. Consider extracting shared tooling to a versioned package if the surface grows (option A).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Record the E-1/E-2 decisions | Unblocks enforcement work | `ledgers/decision_log.md`; owner package | Decision row exists |
| Extend `check_compose_pins` to `mct/compose` with an exceptions file | Closes the demonstrated blind spot | `ci/validate.py`; `mct/VENDORING.md` §4 | Floating ref fails without a waiver |
| Add an undeclared-user test | Proves the apply behavior | `bootstrap/60-central-deploy.sh` test fixture | Test fails closed |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Shared-tooling lock + cross-repo check | P1 | both maintainers | M | E-1 |
| MCT pin enforcement + upstream pin | P1 | coordinator + maintainer | M | E-2/C8 |
| Merge-safe identity apply | P2 | maintainer | M | E-4a |
| Vendor-drift import manifest | P2 | maintainer | M | Next import |
| Feature-staging acceptance | P3 | owner | S | E-4b |

## Suggested Tests

- `shared_tooling_check.sh` mutation test (a changed shared file fails; an allowlisted fork passes).
- `ci/validate.py --only compose-pins` fixture with a floating ref under `mct/compose/`.
- Undeclared-user apply fixture (must fail or preserve).
- Import-manifest drift test (sha256 per vendored file).
- Edge-pin offline verification (exists; keep).

## Suggested Documentation Updates

- `docs/architecture/SHARED_TOOLING_POLICY.md` — record the decision and the implemented enforcement.
- `mct/VENDORING.md` — record the upstream commit at the next import; update the exception table; state the CI coverage once implemented.
- `docs/architecture/EVOLUTION_GUIDE.md` — refresh the state block; mark E-4a/E-4b outcomes.
- `docs/runbooks/MCT_CONSOLIDATION.md` — keep live-vs-staged current.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Option A vs B for shared tooling? | Enforcement design | Owner decision E-1 |
| Keep vs extract the MCT subtree? | Determines pin/upstream investment | Owner decision E-2a |
| Will a multi-site fleet arrive soon? | Determines flag/tenant-model urgency | Owner roadmap |
| Who owns the template/`event_time` field contract? | Split-ownership risk (20261002 EVOL-P2-001 note) | Cross-ref DATA-P2-001 |

## Limitations / Appendix

- Single-repo scope: edge-owned extension surfaces (SQLite migrations, OpenAPI, agent bundles, roles) were not assessed; the falcon side of the pair contract is machine-checked (`verify_edge_pin.py` PASS in `ci/validate.py`).
- The shared-tooling drift claims were not re-measured against the live edge repository (read-only pack); the policy document's measurements (2026-10-01) and the falcon-side fix are cited.
- The mct/compose image counts were reproduced read-only at `08e20d1` and match the policy doc.

## Findings

| ID | Severity | Title |
|---|---|---|
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| EVOL-P1-002 | P1 | MCT vendoring policy proposed but not enforced; the pin gate remains blind to mct/compose |
| EVOL-P2-001 | P2 | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) |
| EVOL-P3-002 | P3 | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance |
