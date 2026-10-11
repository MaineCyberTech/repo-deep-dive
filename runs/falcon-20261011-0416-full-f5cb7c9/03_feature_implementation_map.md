# 03_feature_implementation_map — Prompt 03 - Feature Implementation and Gap Map

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `03_feature_implementation_map.md` (area FEAT, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive (falcon)
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` @ `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (branch `main`)
- Generated at: 2026-10-11T04:45Z
- Auditor: repo-deep-dive full-pass subagent (FEAT)
- Area code: FEAT
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/03_feature_implementation_map.md` (intended)
- Scope limitations: capability map of an ops platform (not an end-user product); operator UIs are upstream products (Grafana/OSD/Wazuh/ntfy/ntopng/IRIS). Live checks were read-only, 2026-10-11 04:19-04:35 UTC. Mobile behavior is N/A (no mobile surface).

## Scope

Mapped every first-party capability to its UI, interface/API, data, worker/timer, permissions, tests and docs: capture, transport, storage/search, metrics, alerting, notifications, access, flow UI, Wazuh integration, IRIS/OpenCanary, staged MCT services, edge fleet, backups, VPN, and platform-health jobs. Checked for UI-without-backend and backend-without-UI, orphaned modules, stale feature claims, and missing tests/docs. The MCT archive-only boundary was checked against the drift-check classification.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md:29-36` | doc | feature inventory and data path | claims 3 dashboards / 73 panels / 85 alert rules |
| `compose/central`, `compose/probe`, `compose/mct`, `automation/wazuh/multi-node` | source | deployed features | 27 live containers |
| `bootstrap/*.sh` (30) | source | feature provisioning | deploy stages, timers, alert rules, dashboards |
| `automation/validation/*` (206 files incl. 322 shell scripts) | source | test estate | offline suites in `ci/validate.py` |
| `automation/alerting/`, `config/ntfy/`, `config/prometheus/`, `config/grafana/` | source | alerting/notification features | 86 scripted rules |
| `automation/wazuh/*`, `docs/runbooks/WAZUH_*.md` | source/docs | Wazuh feature | live multi-node + forwarder |
| `docs/runbooks/MCT_CONSOLIDATION.md`, `mct/VENDORING.md` | docs | IRIS/OpenCanary live; staged services | archive-only policy |
| `automation/vpn/`, `config/wireguard/`, `docs/runbooks/VPN.md` | source/docs | VPN + enrollment | live wg0 + enroll service |
| `docs/phase9/ALERT_CATALOGUE.yaml`, `automation/validation/build_alert_catalogue.py` | generated/doc | alert feature state | 85 catalogue entries |
| `automation/validation/container_drift_check.sh:150` | source | declared-vs-running classification | `DECLARED_ROOTS` includes `mct/compose` |
| live textfile metrics, Grafana API, `docker ps`, `systemctl list-timers` | live | feature state | see tables |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `bash automation/validation/tests/alert_rule_lint_test.sh` | command | rule set lint | `PASS (derived_rule_count=86; unique_uids=86; unique_expressions=86)` |
| Grafana API rule set vs `bootstrap/90-alerting.sh` UIDs | live vs source | stale feature claim | live 86 == script 86 (sorted diff empty); catalogue 85 (missing `falcon-wazuh-proxy-listeners`) |
| Grafana API dashboards | live | UI claim | 3 dashboards (matches README) |
| `bash automation/validation/tests/remediation_guards_test.sh` | command | archive-only boundary guard | `PASS remediation_guards` |
| live `docker ps` | live | staged MCT not deployed | no `mct/compose` containers running |
| `falcon_service_up` textfile | live | feature availability | grafana/dash/ntfy/traefik/ntop/relay/do-ntfy-public/do-host/iris/edge-cp = 1 (10/10) |
| `falcon_pipeline_e2e` textfile | live | transport feature | last success 04:15Z; last failure 2026-10-09T20:40Z |
| `falcon_edge_inventory` textfile | live | edge fleet feature | 72 hosts / 109 services; daily scan (age ~23.7 h) |
| `falcon_wazuh_backup` / `falcon_cold_copy` textfiles | live | backup features | Wazuh backup 2026-10-11T03:06Z; cold copy 2026-10-10T04:52Z (next 04:40 daily) |
| `falcon_alert_canary` textfile + `systemctl list-timers` | live | notification proof | weekly (Mondays 06:00 UTC); last success 2026-10-05; next 2026-10-12 |
| `falcon_container_drift` / `falcon_live_image_drift` | live | feature consistency | all kinds 0; live image drift 0 |
| `git status` / GitHub API | command | feature-state binding | live tree clean at `f5cb7c9` = remote main |

## Executive Summary

The capability set is broad and mostly complete: capture (Suricata + pmacct/nfacctd), buffered transport with DLQ, OpenSearch storage with ISM retention and R2 searchable snapshots, metrics/alerting, self-hosted notifications with an independent path and dead-man, TLS ingress with Cloudflare Access, Wazuh multi-node, IRIS/OpenCanary, edge-fleet tooling, backups and VPN. The prior feature-state defect is fixed: the live Grafana rule set is now identical to the provisioning script (86 == 86; the six previously missing rules are live, and the new `falcon-wazuh-proxy-listeners` rule was added and provisioned). The remaining gaps are: the alert catalogue and README/CURRENT_STATE counts lag the provisioned set by one rule (85 vs 86) — a new instance of the catalogue-drift class; the archive-only MCT boundary is documented and statically guarded, but the container drift check still treats `mct/compose` as a declared source (latent); and the staged MCT tree remains unpinned under a blanket waiver. Mobile is N/A; operator UIs are upstream products.

## Inventory (feature map)

| Feature | UI | Interface / API | Data | Worker / timer | Permissions | Tests | Docs | State |
|---|---|---|---|---|---|---|---|---|
| Capture (IDS) | OSD triage | SPAN ens19; Suricata EVE | `falcon-eve-*` | `falcon-probe-suricata-1` | passive, no listener | alert/e2e suites; live span checks | `SURICATA_RULESET.md` | running |
| Flow capture | ntopng | pmacct/nfacctd -> flows | flow indices | `falcon-pmacct`, `falcon-nfacctd` | NET_ADMIN/RAW | live checks | `CAPACITY_AND_TELEMETRY.md` | running |
| Transport | vector metrics | HTTP 6000 (basic auth), syslog 5141 | DLQ files | `vector-edge` (disk buffer), `vector-aggregator` (1 GiB) | shared credential | `write_rejection_test`, `event_time_consistency_test` | `DATA_FLOW_AND_CLASSIFICATION.md` | running; OOM closed |
| Storage/search | OSD dashboards | OpenSearch 9200 (internal) | `falcon-eve-*`, audit log | ISM policies | internal users | `ism_retention_metrics_test`, `mapping_drift_check_test` | `SCHEMA_AND_RETENTION.md` | running; yellow normal |
| Searchable snapshots | — | repository-s3 plugin -> R2 | snapshots | cold-copy timer | root-only secrets | `r2_cold_tier_setup_test` | `R2_COLD_TIER.md` | running (Oct 10) |
| Metrics | Grafana | Prometheus 9090 (internal), exporters | TSDB | textfile timers | none (internal) | exporter suites | `MONITORING_SCRAPE_AND_FRESHNESS.md` | running |
| Alerting | Grafana | 86 live rules -> relay -> ntfy | rule store | API provisioning | Grafana admin | `alert_rule_lint_test` (86), `alert_expression_bool_test` | `ALERT_CATALOGUE.yaml` | running; catalogue 85 (FEAT-P3-001) |
| Notifications | ntfy | ntfy HTTP (loopback) | ntfy cache | relay service | ntfy ACLs + Traefik basic auth | `ntfy_sh_alert_test`, `silence_alert_test`, `deadman_contract_test` | `NOTIFICATION_AND_DEADMAN.md` | running (lab + independent + weekly canary) |
| Access | Traefik/Cloudflare | 80/443; public hosts | — | — | basic auth + Cloudflare Access | `exposure_edges_test` | `ACCESS_AND_ACCOUNTS.md` | running |
| Flow UI | ntopng | /ntop behind basic auth | ntopng data dir | — | dedicated htpasswd | live probe | README caveat | running; nProbe license blocked (documented) |
| Wazuh | Wazuh dashboard | manager/indexer/dashboard; agent proxies 15140/15141 | wazuh-* indices | backup timer, forwarder | RBAC | `wazuh_indexer_backup_test` | `WAZUH_INTEGRATION.md` | running; proxy rule added |
| IRIS | IRIS web | via tunnel | iris_db | app+worker | Cloudflare Access | `retired_iris_literal_test`, guards | `MCT_CONSOLIDATION.md` | running |
| OpenCanary | — | decoy ports | Wazuh alerts | container | mgmt-interface bind | canary live checks | `MCT_CONSOLIDATION.md` | running |
| Staged MCT (Shuffle/MISP/Velociraptor/OTel/Greenbone) | — | compose files only | archive | — | — | boundary guard (PASS) | `mct/VENDORING.md` | archive-only; 29 unpinned refs |
| Edge fleet | — | control plane; enrollment; metrics/inventory/diagnostics | textfile metrics | timers | certs/tokens | `edge_pin_offline_test`, `pair_state_check_test` | `docs/edge/*` | running (72 hosts / 109 services) |
| Backups | — | snapshots, offsite, R2 | backups | backup/offsite/cold-copy timers | root-only | `backup_e2e_test`, `restore_assertion_test` | `RESTORE.md`, `R2_COLD_TIER.md` | running; DR domain owns details |
| VPN | — | wg0 5182; enroll service | peers | enroll service | keys/tokens | `wg_peer_preservation_check` | `VPN.md` | running (8 peers) |
| Platform health | — | disk guard, service probe, canary, drift | textfile metrics | timers | root | `textfile_freshness_test`, `audit_run_lifecycle_test` | `OPERATOR_START_HERE.md` | running; container memory alert gap (ARCH report) |

### Completeness scorecard

| Area | Score | Evidence | Gap |
|---|---:|---|---|
| Capture | 4 | live suricata + rules + checks | nProbe license block for flow enrichment |
| Transport | 4 | buffer/DLQ/validation live; OOM closed; e2e success | shared-credential auth (ARCH-P2-003) |
| Storage/search | 4 | ISM + R2 + tests | Wazuh/IRIS retention owner-gated |
| Metrics | 4 | textfile + direct scrapes | OpenSearch unscrapable (documented) |
| Alerting | 4 | 86 live == 86 script; proofs | catalogue/README count lag (FEAT-P3-001) |
| Notifications | 4 | three paths + canary + dead-man | owner-side watcher residual |
| Access | 3 | TLS, auth, Access | public routes lack origin auth for some consoles (SEC domain) |
| Wazuh | 4 | cluster + backup + forwarder + proxy alert | retention open |
| IRIS/OpenCanary | 4 | live + pinned | no functional CI smoke for IRIS |
| Staged MCT | 2 | archived, policy + static guard | drift-check declared root + P4 enforcement (FEAT-P2-001) |
| Edge fleet | 4 | timers + tests + pin | fleet hardware domain not in this run |
| Backups | 4 | restore assertion + timers | daily failure history (DR fixed) |
| VPN | 4 | live peers + preservation check | no offline unit test |
| Platform health | 4 | timers + metrics + tests | container memory/restart alert (ARCH report) |

## Detailed Review

### Item: Alerting feature state

- Evidence: `bootstrap/90-alerting.sh` (86 `write_rule` calls); `alert_rule_lint_test` PASS 86/86/86; live Grafana 86 (all updated 2026-10-11T03:16-03:18Z); `docs/phase9/ALERT_CATALOGUE.yaml` 85 entries; `README.md:30` "85 alert rules"; `docs/CURRENT_STATE.md:112` "85 rules live".
- What it does: provisions alert rules to Grafana; routes via relay to ntfy.
- How it appears to work: `write_rule` definitions -> Grafana API; catalogue generated manually from live by `build_alert_catalogue.py`.
- Dependencies: Grafana API credentials; relay; ntfy ACLs.
- Current controls: static lint (UID uniqueness, expression uniqueness/balance); live-vs-script comparison done by this audit.
- Missing controls: no automated live-vs-source drift check; catalogue/README regeneration is manual.
- Risks: a merged rule can go unprovisioned/unlisted unnoticed (the class fixed on 2026-10-09).
- Recommended improvement: wire a live-vs-source UID comparison into a scheduled check; regenerate the catalogue after each provisioning run.
- Suggested tests: integration check comparing live UIDs to script UIDs; catalogue regeneration produces no diff.
- Suggested docs: note the regeneration step in the monitoring runbook.

### Item: MCT archive-only boundary

- Evidence: `mct/VENDORING.md` (archive-only; 29 unpinned refs; P4 proposed); `docs/runbooks/MCT_CONSOLIDATION.md`; `remediation_guards_test` PASS; `container_drift_check.sh:150` `DECLARED_ROOTS` includes `mct/compose`; live `docker ps` shows no `mct/compose` containers.
- What it does: keeps the vendored SOC stack as a non-deployable archive while IRIS/OpenCanary are the consolidated live services.
- How it appears to work: policy + static guard forbidding `-f`/`file:` references from first-party deploy artifacts; drift check classifies containers by compose root.
- Dependencies: maintainer discipline.
- Current controls: static guard; documented policy.
- Missing controls: drift check treats `mct/compose` as declared; no import manifest / vendor-drift check (P4).
- Risks: a staged service revived from the archive tree would look "declared"; silent edits to vendored files are invisible.
- Recommended improvement: drop `mct/compose` from `DECLARED_ROOTS` (classify as undeclared/other) and implement P4.
- Suggested tests: start a container from a staged compose file in a test and assert it reports undeclared; import-manifest check.
- Suggested docs: state how the drift check classifies archive-tree containers.

### Item: Feature availability and failure states

- Evidence: `falcon_service_up` 10/10; `falcon_pipeline_e2e` last success 04:15Z, last failure 2026-10-09T20:40Z; `falcon_container_drift` all-zero; relay path successes lab 9 / alt 9, failures 0; `falcon_alert_canary` weekly success 2026-10-05.
- What it does: proves the user-facing services and the end-to-end pipeline are up, and that alerts actually deliver.
- How it appears to work: service probe timer; e2e marker injection; weekly canary across all three notification paths.
- Dependencies: timers; ntfy; DO watcher.
- Current controls: per-path metrics, dead-man contract, drift check.
- Missing controls: none identified for the feature map (container-level memory alert is the ARCH residual).
- Risks: low.
- Recommended improvement: none.
- Suggested tests: keep the canary and e2e; add the container memory fixture (ARCH report).
- Suggested docs: none.

### Item: UI-without-backend / backend-without-UI / orphaned modules

- Evidence: operator UIs are upstream products (Grafana, OSD, ntopng, ntfy, Wazuh dashboard, IRIS) — no first-party frontend code in the tree (`git ls-files` shows no app/package trees). Every provisioned service has a compose definition and a probe; every script family has a caller or a timer (spot-checked: bootstrap stages, automation validation, edge tooling).
- What it does: confirms there are no orphaned first-party routes/modules in the sense of the prompt.
- How it appears to work: n/a (ops repository).
- Dependencies: n/a.
- Current controls: `ci/validate.py` shell syntax + parsers over the whole tree.
- Missing controls: none found.
- Risks: none identified.
- Recommended improvement: none.
- Suggested tests: none.
- Suggested docs: none.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FEAT-001 | Pages/routes | no first-party web app | upstream UIs | none | — | keep |
| FEAT-002 | Components | compose services + scripts | drift check + gate | staged MCT classification | P2 | FEAT-P2-001 |
| FEAT-003 | API endpoints | Grafana API, ingest :6000, control plane :9443 | provisioning + drift | live-vs-source drift check absent | P3 | wire a check |
| FEAT-004 | Server actions | n/a (ops repo) | — | — | — | — |
| FEAT-005 | Workers/jobs | 13 timers | systemd + metrics | container memory alert (ARCH) | P3 | ARCH report |
| FEAT-006 | Database entities | OpenSearch indices, ntfy cache, Wazuh indices | ISM + tests | Wazuh/IRIS retention owner-gated | P1 | owner |
| FEAT-007 | Permissions | Cloudflare Access + per-service logins | auth middleware | origin auth gaps (SEC) | P2 | SEC owner |
| FEAT-008 | Audit logs | evidence tree; ledgers | append-only + manifests | run records unbound | P2 | INV report |
| FEAT-009 | Tests | 322 scripts; offline suites in gate | CI gate | IRIS functional smoke absent | P3 | backlog |
| FEAT-010 | Docs | runbooks + current state | docs gate (drift test) | alert-count lag | P3 | FEAT-P3-001 |
| FEAT-011 | Workflow states | deploy stages; alert FIRING/RESOLVED | provisioning + proofs | catalogue lag | P3 | FEAT-P3-001 |
| FEAT-012 | Failure states | DLQ, e2e, canary, drift | alerts + timers | container OOM/restart alert gap | P3 | ARCH report |

## Findings

### FEAT-P2-001 - Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only (partially fixed)

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `mct/VENDORING.md` — `mct/compose/` is archive-only; P4 (CI enforcement / vendor-drift check) proposed, not implemented; 37 refs, 29 unpinned
  - `docs/runbooks/MCT_CONSOLIDATION.md` — live-vs-staged map; "no first-party deployment artifact may reference it"
  - `bash automation/validation/tests/remediation_guards_test.sh` -> `PASS remediation_guards` (asserts no `-f`/`file:` reference to `mct/compose`)
  - `automation/validation/container_drift_check.sh:150` — `DECLARED_ROOTS = ["compose/central", "compose/probe", "compose/mct", "mct/compose", "automation/wazuh/multi-node"]`
  - live `docker ps` — no `mct/compose` containers running (latent)
- What is happening: the classification and a static guard exist, but one validation tool still treats the archive-only tree as a declared deployment source, and P4's enforcement/vendor-drift checks are unimplemented.
- Why it matters: a staged service could be revived from the archive tree and look "declared" to the drift check; silent edits to vendored files are invisible.
- User / business impact: low today (nothing staged is running); policy erosion risk.
- Security / privacy / reliability impact: a revived unmaintained service would run outside the pin/SBOM gates.
- Recommended fix: drop `mct/compose` from `DECLARED_ROOTS` (classify as undeclared/other), implement P4 (per-ref pin exceptions + import manifest), or explicitly scope the drift check's archive tree handling.
- Suggested validation: start a container from a staged compose file in a test and assert it reports as undeclared; add an import-manifest check.
- Owner suggestion: maintainer.
- Effort estimate: M.
- Dependencies: owner decision (waiver review_by 2026-12-31).
- Status: partially-fixed.
- Endpoint / data path: compose -> drift classification.
- Attack path: none identified (latent).

### FEAT-P3-001 - Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-listener addition

- Severity: P3
- Confidence: High
- Area: FEAT
- Evidence:
  - `bootstrap/90-alerting.sh:252` — `write_rule "falcon-wazuh-proxy-listeners"` (added by PR #53 for the N1 remediation)
  - `bash automation/validation/tests/alert_rule_lint_test.sh` -> `PASS (derived_rule_count=86; unique_uids=86; unique_expressions=86)`
  - live Grafana API -> 86 rules (sorted UID diff vs the script is empty); all updated 2026-10-11T03:16-03:18Z
  - `docs/phase9/ALERT_CATALOGUE.yaml` -> 85 entries (no `falcon-wazuh-proxy-listeners`); header: "Generated from the live Grafana rules by automation/validation/build_alert_catalogue.py"
  - `README.md:30` — "85 alert rules"; `docs/CURRENT_STATE.md:112` — "85 rules live (2026-10-10)"
  - prior FEAT-P2-002/OBS-P2-001 were verified-fixed at 77->85; the drift re-appeared with the 86th rule
- What is happening: the provisioning gap is fixed (live == script), but the catalogue, README and current-state page still say 85 and omit the new rule, so the catalogue's "cannot drift" property is false again by one entry.
- Why it matters: the documented alert coverage understates the live set and the catalogue cannot be used as the source of truth; reviewers re-derive counts manually (this audit did).
- User / business impact: minor; review/ops friction.
- Security / privacy / reliability impact: documentation/feature-state accuracy.
- Recommended fix: regenerate `docs/phase9/ALERT_CATALOGUE.yaml` from live (or from the script) after each provisioning run and update the README/CURRENT_STATE counts; consider a gate check deriving the count from `write_rule` and comparing docs.
- Suggested validation: catalogue regeneration produces a no-diff commit; `alert_rule_lint_test` count == catalogue count == README count.
- Owner suggestion: ops.
- Effort estimate: S.
- Dependencies: live Grafana access for regeneration.
- Status: open.
- Endpoint / data path: `bootstrap/90-alerting.sh` -> Grafana -> catalogue/README.
- Attack path: none identified.

## Prior-Run Comparison

| Prior finding | Status now | Evidence |
|---|---|---|
| FEAT-P2-001 | partially-fixed | policy + guard landed and PASS; drift-check root listing and P4 enforcement remain |
| FEAT-P2-002 | verified-fixed | live 86 == script 86; all previously missing rules present; the six-rule provisioning gap is closed |
| — (new) | FEAT-P3-001 | catalogue/README/CURRENT_STATE lag live by one rule (`falcon-wazuh-proxy-listeners`) |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Documented alert coverage lags live | P3 | Medium | Medium | 85 vs 86; catalogue missing the new rule | regenerate + count check |
| Staged service revived from archive tree | P2 | Low | Medium | drift roots include `mct/compose` | FEAT-P2-001 |
| Vendored files silently edited | P2 | Low | Medium | no import manifest | P4 |
| IRIS/OpenCanary regression without functional smoke | P3 | Low | Medium | no CI functional test | backlog |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Regenerate the alert catalogue and update README/CURRENT_STATE counts (FEAT-P3-001).

### This Month
- Implement the live-vs-source rule drift check; remove `mct/compose` from declared roots (FEAT-P2-001).

### Later / Platform Evolution
- Implement the MCT import manifest and staged-service revival checklist (P4).
- Add a functional IRIS/OpenCanary smoke where feasible.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Regenerate the catalogue | restores the single source of truth | `docs/phase9/ALERT_CATALOGUE.yaml` | regeneration no-diff |
| Update the README/CURRENT_STATE count | removes a stale claim | `README.md`, `docs/CURRENT_STATE.md` | review |
| Drop `mct/compose` from `DECLARED_ROOTS` | aligns the drift check with policy | `container_drift_check.sh:150` | staged-container test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Live-vs-source alert drift check | P2 | ops | S | Grafana API |
| MCT P4 enforcement + import manifest | P2 | maintainer | M | owner decision |
| Functional IRIS/OpenCanary smoke in CI | P3 | maintainer | M | live access |
| Doc count derived from the script | P3 | ops | S | lint test |

## Suggested Tests

- Integration: compare live Grafana rule UIDs to `bootstrap/90-alerting.sh` and fail on drift.
- Static: extend the remediation guard to assert the drift check's declared roots exclude `mct/compose`.
- CI: assert `alert_rule_lint_test` derived count == catalogue count == README count.
- Manual: after provisioning, confirm the new proxy-listener rule fires in a fixture drill.

## Suggested Documentation Updates

- `README.md` and `docs/phase9/ALERT_CATALOGUE.yaml`: regenerate/refresh counts and the new rule entry.
- `docs/CURRENT_STATE.md`: refresh the 85-rule line.
- `docs/runbooks/MCT_CONSOLIDATION.md`: state how the drift check classifies archive-tree containers.
- `docs/runbooks/MONITORING_SCRAPE_AND_FRESHNESS.md`: add a provisioning-drift/catalogue regeneration note.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Should the catalogue be generated from the script instead of live? | removes the manual live step and drift | owner decision |
| Is the IRIS functional gap acceptable given Cloudflare Access? | test investment | owner statement |
| Why was the catalogue not regenerated with the #53 provisioning? | process fix | ops statement |

## Limitations

- Panel counts ("73 panels") were not verified (would require parsing live dashboards); only dashboard count/uid provisioning is evidenced (3 dashboards confirmed).
- Mobile behavior is N/A; operator UIs are upstream products.
- Feature health is point-in-time (2026-10-11 04:19-04:35 UTC); see the ARCH report for live command details.
- The `mct/` upstream was not consulted.

## Appendix

- Live rule comparison: script `write_rule` UIDs (86) == live Grafana UIDs (86); catalogue `id` values (85) missing `falcon-wazuh-proxy-listeners`.
- Feature metrics at capture: services 10/10 up; e2e last success 04:15Z; drift all-zero; live image drift 0; edge inventory 72 hosts / 109 services; cold copy 2026-10-10T04:52Z; Wazuh backup 2026-10-11T03:06Z; canary weekly (next 2026-10-12T06:00Z).

## Findings

| ID | Severity | Title |
|---|---|---|
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |
| FEAT-P3-001 | P3 | Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-listener addition |
