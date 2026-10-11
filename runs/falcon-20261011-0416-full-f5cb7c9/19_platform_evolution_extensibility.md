# 19_platform_evolution_extensibility — Prompt 19 - Platform Evolution and Extensibility Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `19_platform_evolution_extensibility.md` (area EVOL, prompt)

## Verification Performed

# Platform Evolution and Extensibility Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (short `f5cb7c9`)
- Branch: `main` · Generated at: 2026-10-11T04:33Z · Auditor: repo-deep-dive subagent (prompt 19) · Area code: EVOL
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/19_platform_evolution_extensibility.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo value read from the owner file in a subshell, never printed); no state mutated. Edge-repository extension surfaces are referenced but not assessed (single-repo scope).

## Scope

Reviewed at `f5cb7c9`: module/file conventions, domain/data contract (event schema), shared packages, extension points, feature staging (flags), permission/identity extensibility, tenant/org model (single-tenant lab; site model), API versioning, migration strategy, eventing/webhooks, integration framework, UI reuse, admin tooling, background jobs, config model, observability extensibility, docs for adding modules, AI-agent compatibility, package extraction.

Not reviewed: the edge repository's implementation (its SQLite migrations and OpenAPI are edge-owned; referenced).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/EVOLUTION_GUIDE.md` | doc | Extension model, conventions, checklists, module template, roadmap | `:270-279` state block stale (DOC-P2-002); `:311-320` identity hazard; `:342-360` feature staging |
| `docs/architecture/SHARED_TOOLING_POLICY.md` | doc | Cross-repo tooling duplication + options | Status "proposed"; option B sketch at `:85-101`; no enforcement |
| `mct/VENDORING.md` | doc | Vendored subtree policy | Status "proposed"; `:38-48` 37 refs / 8 pinned / 29 unpinned / 11 floating; P4 CI coverage unimplemented |
| `ci/validate.py` | code | Pin check scope; digest cross-check | `:112-119` `check_compose_pins()` globs `compose/**`; `:142-158` `check_compose_digests()` covers `compose`, `mct/compose`, `automation/wazuh` |
| `pins/images.lock`, `pins/supply-chain-waivers.json` | config | Pins + explicit waivers | mct/compose waived (`review_by 2026-12-31`) |
| `bootstrap/60-central-deploy.sh` | code | Identity apply semantics | `:142-151` comment: apply REPLACES the internal-user set (R-28); `:207` securityadmin apply |
| `ledgers/risk_register.md` | ledger | Observed identity hazard | R-28 CLOSED (declared identities + verify); R-39 open (retired IRIS literal, rotation owner-side) |
| `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` | doc | Owner decisions pending | E-1 (shared tooling), E-2a/b (MCT), E-4a (identity apply), E-4b (feature staging) unsigned |
| `docs/phase9/OWNER_ACTIONS.md:78-79` | doc | Owner actions C7/C8 | Shared-tooling choice; MCT pin enforcement + import status |
| `docs/edge/EDGE_RELEASE_PIN.md`, `JOINT_RELEASE_PROCEDURE.md`; `automation/validation/verify_edge_pin.py` | docs/code | API/pair versioning | Pin machine-checked; PASS in the gate |
| `config/opensearch/falcon-eve-template.json`; `config/vector/*.yaml` | config | Data contract + ingest extension points | Template pinned, `dynamic:false`, 75 properties |

## Verification Performed

| Check | Type | Why relevant | Notes |
|---|---|---|---|
| `ls automation/shared-tooling.lock automation/validation/shared_tooling_check.sh` | reproduce | Enforcement existence | Both absent — option B not implemented |
| Read `SHARED_TOOLING_POLICY.md` §1-§5 | inspect | Drift map + decision status | Still "proposed 2026-10-01"; capture wrapper drift documented (falcon hardened, edge copy not) |
| Recount image refs under `mct/compose/` (read-only script) | reproduce | VENDORING claim | 37 refs; 8 digest-pinned; 29 unpinned; 11 floating — matches the policy doc |
| `python3 automation/validation/check_compose_digests.py --compose-dir mct/compose --waivers pins/supply-chain-waivers.json` | reproduce | CI blind-spot mitigation | `compose_digest_findings=0; compose_digest_waived=35` (explicit, expiring waiver) |
| `python3 ci/validate.py --only compose-pins` scope read | inspect | Pin gate coverage | Still globs `compose/**` only; `mct/compose` covered only by the waived digest cross-check |
| Read `bootstrap/60-central-deploy.sh:142-151,207`; `ledgers/risk_register.md` R-28 | inspect | Identity merge-safety | Replace-on-apply documented; identities declared; verify control; merge-safe apply not implemented |
| `grep` for feature-flag mechanisms in first-party code | inspect | EVOL-P3-002 | None found; §9 additive-deploy substitute documented, E-4b unsigned |
| Read `EVOLUTION_GUIDE.md` §6 (module template), §7 (roadmap), §8 (identity/version), §9 (staging) | inspect | Extension points + templates + policies | Present |
| `python3 ci/validate.py` | reproduce | Gate | `validation_failures=0` (edge-pin offline self-check PASS) |

## Executive Summary

The extension model remains genuinely strong for a lab of this size: `EVOLUTION_GUIDE.md` gives file conventions, per-extension checklists (service, feed, alert rule, backup class, site host, automation module), a copy-paste module template, a worked wave example, an identity/version registry with the R-28 hazard, and an explicit "no flags — additive deploy + canary + rollback" staging policy. All four prior-run EVOL findings persist at `f5cb7c9` and remain owner-gated or hardening-pending: (1) cross-repo shared tooling has drifted once already (an asymmetric security fix) and still has no pin/hash enforcement — owner decision E-1/C7; (2) the vendored MCT subtree carries 29/37 unpinned image refs and no recorded upstream commit, and the pin gate is still blind to `mct/compose` — partially mitigated by an explicit expiring waiver in the digest cross-check (E-2/C8); (3) the OpenSearch identity apply is not merge-safe (R-28 closed via declaration + verify; E-4a unsigned); (4) feature flags remain intentionally absent, with the documented substitute awaiting owner acceptance (E-4b). Post-08e20d1 changes (PRs #49–#54) do not alter these surfaces. Recommended: record the E-1/E-2/E-4 decisions, implement option B for shared tooling, extend pin enforcement (or archive-only enforcement) for `mct/compose`, and decide the identity-apply hardening.

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
| Observability extension | `automation/validation/export_monitor_metrics.sh`; `bootstrap/90-alerting.sh` | Metric/rule extension points | Implemented | Low | 86 rules provisioned |
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

## Findings

### EVOL-P1-001 — Cross-repo shared tooling has drifted and still has no pin/hash enforcement

- Severity: P1 · Confidence: High · Status: owner-accepted
- Evidence: `docs/architecture/SHARED_TOOLING_POLICY.md:1-7` ("Status: proposed 2026-10-01 … Nothing was implemented cross-repo"), `:27-38` (7 same-path tools; 2 identical / 5 differ; parallel secret scanners), `:40-50` (falcon capture wrapper hardened 2026-10-01; edge copy still exports the owner credential file, records the password feed's exit code, misses `falcon-` topic redaction), `:85-101` (option B sketch — **not implemented**: `automation/shared-tooling.lock` and `automation/validation/shared_tooling_check.sh` do not exist); `docs/phase9/OWNER_ACTIONS.md:78` (C7); `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-1 unsigned.
- What is happening: safety-critical tools are duplicated across the paired repositories without a pin or hash check; drift has already produced an asymmetric security fix, and the enforcement design is proposed but unimplemented and undecided.
- Recommended fix: record the owner choice (E-1; recommended option B) and implement it: shared-file manifest per repo + a read-only cross-repo check wired into both CIs, with a small intentional-fork allowlist (owner + expiry); unify the capture wrapper and scanner pattern sets first.
- Status: owner-accepted (register 2026-10-11: owner-accepted, unchanged).

### EVOL-P1-002 — MCT vendoring policy is proposed but not enforced; the pin gate remains blind to `mct/compose`

- Severity: P1 · Confidence: High · Status: owner-accepted
- Evidence: `mct/VENDORING.md:3-7` (policy proposed; owner decision pending), `:38-48` (37 refs: 8 pinned / 29 unpinned / 11 floating; "Blind spot demonstrated"), `:62-73` (P3 no unpinned image may run; P4 CI coverage proposed), `:115-126` (open; coordinator follow-up); recount at `f5cb7c9` = 37/8/29/11 (unchanged); `ci/validate.py:112-119` (`check_compose_pins()` globs `compose/**` only); `ci/validate.py:142-158` (`check_compose_digests()` covers `mct/compose`; PASS with 35 waived findings; `pins/supply-chain-waivers.json` waiver `review_by 2026-12-31`); `docs/phase9/OWNER_ACTIONS.md:79` (C8).
- What is happening: the vendored subtree carries unpinned/floating images and no recorded upstream commit; the pin check still does not cover it, and the digest cross-check only passes because of an explicit, expiring waiver.
- Recommended fix: implement VENDORING P4 (extend the pin check to `mct/compose/**` with an explicit exceptions table, or enforce archive-only), record the upstream pin at the next import, and keep the waiver expiry visible; decide E-2a/E-2b.
- Status: owner-accepted (register 2026-10-11: owner-accepted, unchanged).

### EVOL-P2-001 — The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending)

- Severity: P2 · Confidence: High · Status: open
- Evidence: `bootstrap/60-central-deploy.sh:142-151` (comment: the config-driven apply "REPLACES the whole internal-user set, so ad-hoc users are deleted on every bootstrap re-run (finding R-28)"), `:207` (`securityadmin.sh -f /tmp/internal_users.yml -t internalusers -icl -nhnv`); `ledgers/risk_register.md` R-28 (CLOSED: identities declared + verify-after-rerun control; originally broke the exporter and snapshot job); `docs/architecture/EVOLUTION_GUIDE.md:311-320` ("make the apply merge-safe or fail loud" — not done); `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-4a unsigned.
- What is happening: adding an identity out-of-band is silently undone on the next bootstrap re-run; the control is "declare everything and verify after", not merge-safety.
- Recommended fix: make the apply merge-safe or fail loud on undeclared users; keep the declared registry as the source of truth.
- Status: open (hazard closed; hardening pending).

### EVOL-P3-002 — No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance

- Severity: P3 · Confidence: High · Status: open
- Evidence: `docs/architecture/EVOLUTION_GUIDE.md:342-360` ("There is no feature-flag mechanism in either repository … The official substitute is additive deploy + staged rollout + idempotent rollback"; introduce real flags only at fleet scale); read-only grep for flag mechanisms in first-party code: none; `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-4b unsigned.
- What is happening: there is no per-feature kill switch; the substitute is documented but not owner-accepted as official policy.
- Recommended fix: record the owner acceptance of §9 (or fund the flag registry before the next multi-site expansion).
- Status: open (documented substitute).

## Prior-Run Comparison

- Prior full run `falcon-20261009-2117-full-08e20d1` emitted EVOL-P1-001, EVOL-P1-002, EVOL-P2-001 and EVOL-P3-002. All four persist at `f5cb7c9`; the 2026-10-11 verification register dispositions (owner-accepted / owner-accepted / open / open) are confirmed.
- Post-08e20d1 changes reviewed (PRs #49–#54): alerting/capacity/tunnel/backup ops changes; none touches the shared-tooling, MCT-vendoring, identity-apply or feature-flag surfaces. The mct/compose recount matches the 2026-10-01 measurement exactly (37/8/29/11); the digest cross-check still passes via the expiring waiver (35 waived).
- No new EVOL issues were identified at this commit.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Shared-tooling drift recurs | P1 | High | Asymmetric security/scanning | `SHARED_TOOLING_POLICY.md:40-50` | Option B enforcement |
| Vendored unpinned images revived | P1 | Medium | Supply chain | `mct/VENDORING.md:38-48` | P4 enforcement + upstream pin |
| Identity apply breaks services | P2 | Medium | Monitoring/backup outage | R-28; `60-central-deploy.sh:142-151` | Merge-safe apply |
| No flags at fleet scale | P3 | Low | Rollout risk | `EVOLUTION_GUIDE.md:342-360` | Accept or fund |

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
- `docs/architecture/EVOLUTION_GUIDE.md` — refresh the state block (DOC-P2-002); mark E-4a/E-4b outcomes.
- `docs/runbooks/MCT_CONSOLIDATION.md` — keep live-vs-staged current.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Option A vs B for shared tooling? | Enforcement design | Owner decision E-1 |
| Keep vs extract the MCT subtree? | Determines pin/upstream investment | Owner decision E-2a |
| Will a multi-site fleet arrive soon? | Determines flag/tenant-model urgency | Owner roadmap |
| Who owns the template/`event_time` field contract? | Split-ownership risk | Cross-ref DATA-P2-001 |

## Limitations / Appendix

- Single-repo scope: edge-owned extension surfaces (SQLite migrations, OpenAPI, agent bundles, roles) were not assessed; the falcon side of the pair contract is machine-checked (`verify_edge_pin.py` PASS in `ci/validate.py`).
- The shared-tooling drift claims were not re-measured against the live edge repository (read-only pack); the policy document's 2026-10-01 measurements and the falcon-side fix are cited.
- The mct/compose image counts were reproduced read-only at `f5cb7c9` and match the policy doc (37 refs / 8 pinned / 29 unpinned / 11 floating); the digest cross-check was re-run read-only (0 findings, 35 waived).

## Findings

| ID | Severity | Title |
|---|---|---|
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| EVOL-P1-002 | P1 | MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose |
| EVOL-P2-001 | P2 | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) |
| EVOL-P3-002 | P3 | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance |
