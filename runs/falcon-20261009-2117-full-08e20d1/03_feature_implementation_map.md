# 03_feature_implementation_map — Prompt 03 - Feature Implementation and Gap Map

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `03_feature_implementation_map.md` (area FEAT, prompt)

## Verification Performed

## Metadata

- Domain: `03_feature_implementation_map` (area FEAT)
- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`); live checks read-only 2026-10-09 21:29-21:50 UTC
- Emitted: 2026-10-09T21:52:25Z by the repo-deep-dive full-pass subagent
- Scope limitation: capability map (ops platform, not an end-user product); UI surfaces are upstream (Grafana/OSD/Wazuh/ntfy/ntopng).

## Scope

Mapped every first-party capability to its UI, interface/API, data, worker/timer, permissions, tests and docs: capture, transport, storage/search, metrics, alerting, notifications, access, flow UI, Wazuh integration, IRIS/OpenCanary, staged MCT services, edge fleet, backups, VPN, and platform-health jobs. Checked for UI-without-backend and backend-without-UI, orphaned modules, stale feature claims, and missing tests/docs. Mobile behavior is N/A (no mobile surface; falcon-lab profile marks prompt 17 N/A).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md:23-36` | doc | feature inventory and data path | claims 3 dashboards / 73 panels / 79 alert rules |
| `compose/central`, `compose/probe`, `compose/mct` | source | deployed features | 27 live containers |
| `bootstrap/*.sh` (30) | source | feature provisioning | deploy stages, timers, alert rules, dashboards |
| `automation/validation/*` (104 scripts), `automation/validation/tests/*` (51 suites) | source | test estate | run in `ci/validate.py` |
| `automation/alerting/`, `config/ntfy/`, `config/prometheus/`, `config/grafana/` | source | alerting/notification features | 83 scripted rules |
| `automation/wazuh/*`, `docs/runbooks/WAZUH_INTEGRATION.md`, `WAZUH_INDEXER_BACKUP.md` | source/docs | Wazuh feature | live multi-node + forwarder |
| `docs/runbooks/MCT_CONSOLIDATION.md`, `mct/VENDORING.md` | docs | IRIS/OpenCanary live; staged services | live-vs-staged map |
| `automation/vpn/`, `config/wireguard/`, `docs/runbooks/VPN.md` | source/docs | VPN + enrollment | live wg0 + enroll service |
| `docs/phase9/ALERT_CATALOGUE.yaml`, `automation/validation/build_alert_catalogue.py` | generated/doc | alert feature state | 79 alerts committed |
| live textfile metrics, Grafana API, `docker ps`, `systemctl` | live | feature state | see tables |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Feature/health metrics (`/srv/falcon/textfile/*.prom`) | live | current state | services all up; e2e recovered; cold-copy/Wazuh backup fresh |
| Grafana API rule set vs `bootstrap/90-alerting.sh` | live vs source | stale feature claim | 77 live vs 83 scripted UIDs; 6 missing |
| `docker ps` / `systemctl list-timers` | live | feature inventory | timers active for backup, disk-guard, probe, canary, drift |
| `bash automation/validation/tests/remediation_guards_test.sh` | command | archive-only boundary guard | PASS |
| `bash automation/validation/tests/alert_rule_lint_test.sh` | command | alert rule set lint | PASS (derived_rule_count=83) |
| `falcon_service_up{...}` | live | UI/API availability | grafana/dash/ntfy/traefik/ntop/relay/iris/edge-cp = 1 |
| `falcon_edge_inventory_*` | live | edge feature | 66 hosts / 103 services, scan fresh (17.5 h) |

## Executive Summary

The capability set is broad and mostly complete: capture (Suricata+pmacct), buffered transport with DLQ, OpenSearch storage with ISM retention and R2 searchable snapshots, metrics/alerting, self-hosted notifications with an independent path and dead-man, TLS ingress with Cloudflare Access, Wazuh multi-node integration, IRIS/OpenCanary, edge-fleet tooling, backups and VPN. The feature-state defect is alerting: the repository claims 79 rules and the catalogue lists them, but the live Grafana instance has 77 rules and has not been re-provisioned since 2026-10-03T03:50Z, so six merged rules (including the OBS-P0-001 per-file textfile freshness rules) are not live. The MCT archive-only boundary is documented and guarded, with one residual: the container drift check still treats `mct/compose` as a declared source. Mobile is N/A; UI surfaces are upstream products.

## Inventory (feature map)

| Feature | UI | Interface / API | Data | Worker / timer | Permissions | Tests | Docs | State |
|---|---|---|---|---|---|---|---|---|
| Capture (IDS) | OSD triage | SPAN ens19; Suricata EVE | `falcon-eve-*` | `falcon-probe-suricata-1` | passive, no listener | alert/e2e suites; live span checks | `SURICATA_RULESET.md` | running |
| Flow capture | ntopng | pmacct/nfacctd -> flows | flow indices | `falcon-pmacct`, `falcon-nfacctd` | NET_ADMIN/RAW | live checks | `CAPACITY_AND_TELEMETRY.md` | running (ntopng captures eth0, documented caveat) |
| Transport | vector metrics | HTTP 6000 (basic auth), syslog 5141 | DLQ files | `vector-edge` (2 GiB disk buffer), `vector-aggregator` | shared credential | `write_rejection_test`, `event_time_consistency_test` | `DATA_FLOW_AND_CLASSIFICATION.md` | running; aggregator OOM loop (ARCH-P1-003) |
| Storage/search | OSD dashboards | OpenSearch 9200 (internal) | `falcon-eve-*`, audit log | ISM policies | internal users | `ism_retention_metrics_test`, `mapping_drift_check_test` | `SCHEMA_AND_RETENTION.md` | running; yellow normal |
| Searchable snapshots | — | repository-s3 plugin -> R2 | snapshots | cold-copy timer | root-only secrets | `r2_cold_tier_setup_test` | `R2_COLD_TIER.md` | running |
| Metrics | Grafana | Prometheus 9090 (internal), exporters | TSDB | textfile timers | none (internal) | exporter suites | `MONITORING_SCRAPE_AND_FRESHNESS.md` | running |
| Alerting | Grafana | 77 live rules -> relay -> ntfy | rule store | API provisioning | Grafana admin | `alert_rule_lint_test`, `alert_expression_bool_test` | `ALERT_CATALOGUE.yaml` | running; 6 repo rules not live (FEAT-P2-002) |
| Notifications | ntfy | ntfy HTTP (loopback 2586) | ntfy cache | relay service | ntfy ACLs + Traefik basic auth | `ntfy_sh_alert_test`, `silence_alert_test`, `deadman_contract_test` | `NOTIFICATION_AND_DEADMAN.md` | running (lab + independent + heartbeat) |
| Access | Traefik/Cloudflare | 80/443; public hosts | — | — | basic auth + Cloudflare Access | `exposure_edges_test` | `ACCESS_AND_ACCOUNTS.md` | running |
| Flow UI | ntopng | /ntop behind basic auth | ntopng data dir | — | dedicated htpasswd | live probe | README caveat | running; nProbe license blocked (documented) |
| Wazuh | Wazuh dashboard | manager/indexer/dashboard; agent proxies 15140/15141 | wazuh-* indices | backup timer, forwarder | RBAC | `wazuh_indexer_backup_test` | `WAZUH_INTEGRATION.md` | running |
| IRIS | IRIS web | https://iris... via tunnel | iris_db | app+worker | Cloudflare Access | `retired_iris_literal_test`, guards | `MCT_CONSOLIDATION.md` | running |
| OpenCanary | — | decoy ports 21/23/... | Wazuh alerts | container | mgmt-interface bind | canary live checks | `MCT_CONSOLIDATION.md` | running |
| Staged MCT (Shuffle/MISP/Velociraptor/OTel/Greenbone) | — | compose files only | archive | — | — | boundary guard | `mct/VENDORING.md` | archive-only |
| Edge fleet | — | control plane; enrollment; metrics/inventory/diagnostics | textfile metrics | timers | certs/tokens | `edge_pin_offline_test`, `pair_state_check_test` | `docs/edge/*` | running |
| Backups | — | snapshots, offsite, R2 | backups | backup/offsite/cold-copy timers | root-only | `backup_e2e_test`, `restore_assertion_test` | `RESTORE.md`, `R2_COLD_TIER.md` | running; daily snapshot failure recovered manually (DR domain) |
| VPN | — | wg0 5182; enroll service | peers | enroll service | keys/tokens | `wg_peer_preservation_check` (live) | `VPN.md` | running (8 peers) |
| Platform health | — | disk guard, service probe, canary, drift | textfile metrics | timers | root | `textfile_freshness_test`, `audit_run_lifecycle_test` | `OPERATOR_START_HERE.md` | running |

### Completeness scorecard

| Area | Score | Evidence | Gap |
|---|---:|---|---|
| Capture | 4 | live suricata + rules + checks | nProbe license block for flow enrichment |
| Transport | 3 | buffer/DLQ/validation live | OOM loop; shared-secret auth |
| Storage/search | 4 | ISM + R2 + tests | Wazuh/IRIS retention owner-gated |
| Metrics | 4 | textfile + direct scrapes | OpenSearch unscrapable (documented) |
| Alerting | 3 | 77 live rules, proofs | 6 merged rules not provisioned; no live-vs-source drift gate |
| Notifications | 4 | three paths + canary | DO-side watcher residual (owner) |
| Access | 3 | TLS, auth, Access | public routes lack origin auth for some consoles (SEC domain) |
| Wazuh | 4 | cluster + backup + forwarder | retention open |
| IRIS/OpenCanary | 4 | live + pinned | no functional test for IRIS |
| Staged MCT | 2 | archived, policy | archive-only enforcement incomplete |
| Edge fleet | 4 | timers + tests + pin | fleet hardware domain not in this run |
| Backups | 4 | restore assertion + timers | daily snapshot failure history |
| VPN | 4 | live peers + preservation check | no offline unit test |
| Platform health | 4 | timers + metrics + tests | container memory/restart alert gap |

## Findings

### FEAT-P2-001 - Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only (partially fixed)

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `mct/VENDORING.md:62-78` — `mct/compose/` is archive-only; P4 (CI enforcement / vendor-drift check) is proposed and not implemented
  - `docs/runbooks/MCT_CONSOLIDATION.md:22-39` — live-vs-staged map; "no first-party deployment artifact may reference it"
  - `bash automation/validation/tests/remediation_guards_test.sh` -> `PASS remediation_guards` (asserts no `-f`/`file:` reference to `mct/compose`)
  - `automation/validation/container_drift_check.sh:150` — `DECLARED_ROOTS` still includes `mct/compose`, so a container started from the archive tree would be classified as declared
- What is happening: the classification and a static guard now exist, but one validation tool still treats the archive-only tree as a declared deployment source, and P4's enforcement/vendor-drift checks are unimplemented.
- Why it matters: a staged service could be revived from the archive tree and look "declared" to the drift check; silent edits to vendored files are invisible.
- Recommended fix: drop `mct/compose` from `DECLARED_ROOTS` (classify as undeclared/other), implement P4 (per-ref pin exceptions + import manifest), or explicitly scope the drift check's archive tree handling.
- Suggested validation: start a container from a staged compose file in a test and assert it reports as undeclared; add an import-manifest check.
- Status: partially-fixed.

### FEAT-P2-002 - Alerting feature state is stale: 79 rules claimed/catalogued, 77 live; six merged rules are not provisioned

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `README.md:30` — "79 alert rules"; `docs/phase9/ALERT_CATALOGUE.yaml` — 79 alerts including `falcon-textfile-collector-{absent,stale,stale-daily}`
  - live Grafana API (2026-10-09) — 77 rules; missing: `falcon-textfile-collector-{absent,stale,stale-daily}`, `falcon-backup-offsite-dlq`, `falcon-monitoring-scrape-absent`, `falcon-relay-path-failures`
  - all 77 live rules' `updated` timestamps are 2026-10-03T03:49:54-03:50:04Z — the last provisioning run
  - `bootstrap/90-alerting.sh:467,543,620,632-644` — the six rules exist in the script; `alert_rule_lint_test` derives 83 UIDs
  - `automation/validation/build_alert_catalogue.py:1-8` — catalogue "generated from the live Grafana rules so it cannot drift" (manual regeneration; drift present)
  - `automation/validation/tests/alert_rule_lint_test.sh` — static lint only; no live comparison
  - `docs/CURRENT_STATE.md:112` — "77 rules live (new falcon-feed-stale-wazuh)" (2026-10-03)
- What is happening: alert rules merged since 2026-10-03 (including the OBS-P0-001 per-file textfile freshness rules and the scrape-absent dead-man rule) are not in the live Grafana; the committed catalogue and README overstate live coverage; nothing compares live rules to the source.
- Why it matters: the alerting feature does not deliver the documented coverage; monitoring-death detection is weaker than the repo claims; the catalogue's "cannot drift" statement is false in practice.
- User / business impact: missed or late alerts; false confidence during incidents.
- Security / privacy / reliability impact: monitoring reliability.
- Recommended fix: re-run `bootstrap/90-alerting.sh` from the converged tree, regenerate the catalogue from live, and add a live-vs-source rule drift check (REPO_WIRING §5 check #8).
- Suggested validation: live rule UID set equals the script's UID set; catalogue regeneration produces a no-diff commit.
- Status: open.

## Prior-Run Comparison

| Prior finding | Status now | Evidence |
|---|---|---|
| FEAT-P2-001 | partially-fixed | policy + guard landed; drift-check root listing and P4 enforcement remain |

New this run: FEAT-P2-002 (alert feature state vs live).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Documented alert coverage absent live | P2 | Certain | High | 77 vs 79/83 | provision + drift gate |
| Staged service revived from archive tree | P2 | Low | Medium | drift roots include `mct/compose` | remove/classify |
| Vendored files silently edited | P2 | Low | Medium | no import manifest | P4 |

## Recommendations

### Immediate / Release Blocking
- None (monitoring coverage gap is P2).

### This Week
- Re-provision the alert rules from the converged tree and regenerate the catalogue (FEAT-P2-002).

### This Month
- Implement the live-vs-source rule drift check; remove `mct/compose` from declared roots (FEAT-P2-001).

### Later / Platform Evolution
- Implement the MCT import manifest and staged-service revival checklist.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Provision the six missing rules | restores documented coverage | `bootstrap/90-alerting.sh` run | live UID set matches |
| Correct README/catalogue count wording | removes stale claim | `README.md`, catalogue | regenerated catalogue |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Live-vs-source alert drift check | P2 | ops | S | Grafana API |
| MCT P4 enforcement + import manifest | P2 | maintainer | M | owner decision |
| Functional IRIS/OpenCanary smoke in CI | P3 | maintainer | M | live access |

## Suggested Tests

- Integration: compare live Grafana rule UIDs to `bootstrap/90-alerting.sh` and fail on drift.
- Static: extend the remediation guard to assert the drift check's declared roots exclude `mct/compose`.
- Manual: after provisioning, confirm the six rules fire in a fixture drill.

## Suggested Documentation Updates

- `README.md` and `docs/phase9/ALERT_CATALOGUE.yaml`: regenerate/refresh counts.
- `docs/runbooks/MCT_CONSOLIDATION.md`: state how the drift check classifies archive-tree containers.
- `docs/runbooks/MONITORING_SCRAPE_AND_FRESHNESS.md`: add a provisioning-drift note.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why was provisioning not re-run after Oct 3? | determines process fix | ops statement |
| Should the drift check classify `mct/compose` as undeclared? | boundary enforcement | maintainer decision |

## Limitations

- Panel counts ("73 panels") were not verified (would require parsing live dashboards); only dashboard count/uid provisioning is evidenced.
- Mobile behavior is N/A; operator UIs are upstream products.
- Feature health is point-in-time; see ARCH for live command details.

## Findings

| ID | Severity | Title |
|---|---|---|
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |
| FEAT-P2-002 | P2 | Alerting feature state is stale: 79 rules claimed/catalogued, 77 live; six merged rules are not provisioned |
