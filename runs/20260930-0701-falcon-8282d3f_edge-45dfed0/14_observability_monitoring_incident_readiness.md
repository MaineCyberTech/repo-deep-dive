# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab, prompt 14) · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: `/home/user/falcon-build` + `/home/user/falcon-edge-build`, branch `main`
- Commit SHA: central `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (dirty: audit run folder + offsite evidence in flight); edge `f1c5defe6b66887ae49bc44c2cd79b37ad249663`
- Generated at: 2026-09-30T15:05Z · Auditor: audit subagent (read-only; no synthetic alerts fired, no mutations) · Area code: OBS
- Output path: docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/14_observability_monitoring_incident_readiness.md
- Scope limitations: Grafana admin API is root-only, so rule state was reconstructed from webhook deliveries (journald) and by re-evaluating provisioned expressions against the live Prometheus API (`172.30.1.6:9090`, GET only); no docker/wg/root; container logs unread; the DO watcher is out of repo and was not inspected.

## Scope

Reviewed the alert pipeline end to end (31 Grafana rules in `bootstrap/90-alerting.sh` → contact point → `falcon-alert-relay` → lab ntfy + independent DO ntfy), 7-day signal quality, monitoring-of-the-monitoring freshness, dead-man paths, edge-fleet alert coverage, dashboards, runbooks and firing-proof evidence. Not reviewed: Grafana UI state, upstream Grafana/OSD internals, phone subscriptions, DO host, Wazuh/IRIS logs beyond metrics.

## Evidence Reviewed

- `bootstrap/90-alerting.sh` (contact point 57-105, policy 115-129, helper 160-195, 31 rules 202-323); `docs/phase9/ALERT_CATALOGUE.yaml` (31 rules, runbooks + review_date 2026-09-30)
- `config/prometheus/prometheus.yml` (3 jobs, no `rule_files`); `config/grafana/dashboards/central-overview.json`; `compose/central/docker-compose.yml:283-299`
- `automation/validation/{export_monitor_metrics,service_probe,disk_guard,heartbeat,backup_new_services}.sh`; `bootstrap/{80-offsite-backup,85-backup-job}.sh`; `config/systemd/falcon-*.{service,timer}`
- Live read-only: `/srv/falcon/textfile/*.prom`, Prometheus API (15:00Z), `journalctl -u falcon-alert-relay` 7 d, `/proc`, `df`, `free`
- `docs/runbooks/*.md`, `docs/phase7/runbooks/*.md`; edge `config/prometheus/edge-alerts.yaml`, `deploy_edge_alert_rules.sh`, D-007
- Evidence: P4-G09, P5-G08, P7-G08, `REVIEW-FIX` alert drills + `20260930T035539Z_offsite-backup-env-fix.out`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Relay journal 7 d / since 04:12:30Z | live read-only | counts, flapping, delivery | 79 primary FIRING (156 incl. alt), 68 resolved, 2 alt failures; 1 post-tune fire |
| PromQL re-evaluation of rule expressions | live read-only | bool-modifier correctness | all comparison rules evaluate false today; `count(up==0)=0` |
| `node_textfile_mtime_seconds` | live metric | exporter freshness | ages 8/62/64/219 s; `node_textfile_scrape_error 0`; no rule uses them |
| Suricata uptime vs RestartCount | live query | rotation visibility | `min_over_time(uptime[25h])=0`, `increase(restarts[25h])=0` |
| Offsite archive log + backup metric | evidence/live | backup observability | 03:55→07:43Z upload, 1 723 files, sample of 3 verified; no metric emitted |
| Firing-proof inventory | evidence | "does it fire" | disk drill raw artifact contradicts `PERFORMANCE_ENVELOPE.md` |

### Prior-run findings (20260930-0320) checked at this commit

| Prior ID | Status | Evidence |
|---|---|---|
| LIVE-P0-004 TLS flap | `partially-fixed` | `d83f421` 30 m→6 h (`90-alerting.sh:234-236`); fires 00:08–04:09Z, zero since 04:12:28Z (~10.8 h); 7-day re-measure pending |
| LIVE-P1-002 MoM gaps | `partially-fixed` | mtime + `falcon_suricata_uptime_seconds` exist live; no alert uses them; swap/guard/watcher/eval-health still unalerted |
| LIVE-P1-004 alert hygiene | `partially-fixed` | catalogue 31=31 (a614af8); benign UniFi filters absent; new `Disk space low` flap 08:03→08:38Z |
| LIVE-P2-001 broken panel | `still-open` | panel unchanged; node-exporter still not `network_mode: host` |
| LIVE-P2-004 Suricata restart | `still-open` | rule reads RestartCount (0); uptime reset proves the restart |
| INTG-P1-001 edge alerts | `still-open` | no `rule_files`; edge rules undeployed (D-007 dry-run) |

## Executive Summary

The alert path is rules-as-code, dual-delivered and demonstrably working (79/79 primary deliveries HTTP 200 in 7 days; noise dropped sharply after today's TLS-window tune). The weaknesses are blind spots: total-host loss is announced only via a 26 h dead-man whose watcher staleness is unalerted; the Sep 30 silent offsite-backup failure can recur with no alert; several critical rules have no firing proof (one raw artifact contradicts its summary doc); Suricata's daily rotation is invisible to its rule; and the edge fleet has metrics/dashboards but zero alerts. Priority: monitoring-of-the-monitoring alerts, offsite outcome metrics, scoped edge rules, and proof drills.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Alert rules | `90-alerting.sh:202-323` | detection | 31 live; catalogue 31/31 | Low | folder monitoring-lab |
| Routing / contact point | `90-alerting.sh:57-129` | delivery | group by alertname, 4 h repeat, dual ntfy | Medium | failures journal-only |
| Metrics exporter | `export_monitor_metrics.sh` | telemetry | fresh (8 s) | Medium | no self last-run metric |
| Disk guard | `disk_guard.sh` | data-LV reclaim | free 45.1 GiB; reclaims 0 | High | threshold 10 GiB, alert text says 5 GiB |
| Heartbeat | `heartbeat.sh`, daily | dead-man | last 00:00:20Z | High | lab ntfy only, inside stack |
| DO watcher | out of repo | off-host dead-man | last metric 14:45Z | High | 15 min / 26 h; unalerted |
| Edge fleet metrics | `falcon_edge_metrics.prom` | fleet visibility | 9 sensors (1 ACTIVE) | Medium | no alerts consume them |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Structured logs | 3 | JSON events in OpenSearch; journald; Traefik JSON | no correlation IDs | document field contract |
| Request IDs/correlation | 2 | pipeline only | no request-id concept | mark N/A (edge CP has ids) |
| Error tracking | 2 | relay journal, Wazuh | no error aggregation | export relay/pipeline failures |
| Metrics | 4 | Prometheus + textfile + probe | freshness/resource gaps | add staleness+swap+guard alerts |
| Tracing | 0 | none found | absent | document N/A |
| Health/readiness | 4 | probes/health 200 | Grafana eval unobserved | external eval dead-man |
| Client/API/worker errors | 2 | journals | no aggregated signal | edge rules |
| Job metrics | 3 | local backup freshness | offsite/new-services unmonitored | add outcome metrics |
| DB/queue/webhook/notification | 3 | DLQ, OS health, buffer | relay failures silent | NOTIF-P1-002 |
| Uptime checks | 4 | service+site probes | alert path not probed e2e | synthetic publish probe |
| Alerts | 3 | 31 rules; dual delivery | proofs + noise history | budgets + drills |

## Detailed Review

- **Alert pipeline:** works end to end; `noDataState: OK` + `execErrState: Error` (`90-alerting.sh:169`); no noise budgets, no delivery-failure metric, error-state notification behaviour undocumented.
- **Monitoring of the monitoring:** freshness data now exists (`node_textfile_mtime_seconds`, watcher metric) but no alert consumes it; swap, guard-free-space and eval health unalerted; single evaluation plane (Grafana).
- **Incident readiness:** `INCIDENT_RESPONSE.md` has a severity model, first-15-min and containment steps; `SENSOR_SILENCE.md:27-28` still says "no VPN / no physical SPAN"; `OPERATOR_START_HERE.md:60-65` gives false assurance on buffer/rotation.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| OBS-001 | Structured logs | OpenSearch JSON; journald | implicit schema | no contract | P3 | document |
| OBS-002 | Request IDs/correlation | none | N/A | unclear status | P3 | state N/A |
| OBS-003 | Error tracking | relay/Wazuh | journal only | no aggregation | P2 | metrics + alert |
| OBS-004 | Metrics | Prometheus, textfile | 4 exporters | staleness unalerted | P1 | mtime rules |
| OBS-005 | Tracing | none | none | absent | P3 | mark N/A |
| OBS-006 | Health/readiness | `service_probe.sh` | 9 services | eval plane unobserved | P1 | external check |
| OBS-007 | Client/API/worker errors | journals | none | gap | P2 | edge rules |
| OBS-008 | Job metrics | backup freshness | local only | offsite unmonitored | P1 | outcome metrics |
| OBS-009 | DB/queue/webhook/notif | DLQ, OS health | partial | relay failures silent | P2 | NOTIF-P1-002 |
| OBS-010 | Uptime checks | probes + DO | good | relay not probed e2e | P2 | publish probe |
| OBS-011 | Alerts | 31 rules | good with gaps | proofs/noise | P2 | budgets + drills |
| OBS-012 | Dashboards | 3 boards | functional | broken panel | P2 | repair |

## Findings

### Finding ID: OBS-P1-001 - Total-host failure has no real-time external notification
- Severity: P1 · Confidence: High · Area: dead-man / alerting
- Evidence: `automation/validation/heartbeat.sh` (daily, lab ntfy only); `export_monitor_metrics.sh:377-379` exports `falcon_site_watcher_last_run_timestamp_seconds` (live 14:45Z) with no rule using it; journal Sep 28 — last publish 10:58:26Z, host down until reboot 15:30Z, no external alert.
- What is happening: the only off-host detector is a 15-min/26-h watcher whose own staleness is silent.
- Why it matters: the monitoring system cannot announce its own death promptly.
- User / business impact: outage MTTD hours-to-a-day (Sep 28: ~4.5 h, human-detected). · Security / privacy / reliability impact: alert-path reliability.
- Recommended fix: alert on watcher age >1 h; shorten the threshold with the owner; consider a mutual check with a publisher on the independent host. · Suggested validation: stop the watcher → alert; documented heartbeat-expiry drill.
- Owner suggestion: owner + falcon maintainer · Effort: M · Dependencies: DO access, owner threshold decision
- Status: still-open (prior LIVE-P1-007)

### Finding ID: OBS-P1-002 - Offsite and new-services backup outcomes are unmonitored
- Severity: P1 · Confidence: High · Area: job metrics / backup
- Evidence: `bootstrap/80-offsite-backup.sh:115-137` uploads/verifies but emits no metric; `bootstrap/85-backup-job.sh:9,36` updates only `.last_backup_epoch`; `export_monitor_metrics.sh:80-85` exports only that local state; `falcon-backup-stale` (`90-alerting.sh:222-224`) tracks the local snapshot; no offsite rule anywhere.
- What is happening: the Sep 30 silent offsite failure (manual fix 03:55→07:43Z, `REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out`) can recur unseen while the local metric stays green.
- Why it matters: offsite is the last protection against host loss; silent failure destroys the recovery window invisibly.
- User / business impact: data-protection gap found only by audit/manual check. · Security / privacy / reliability impact: recoverability.
- Recommended fix: export offsite + new-services success timestamps; 36 h staleness rules; alert on verification failure. · Suggested validation: break the Spaces probe → alert; restore → resolved.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open (prior LIVE-P0-001/002 fixed mechanically, not observably)

### Finding ID: OBS-P1-003 - Monitoring-of-the-monitoring freshness, resources and alert-evaluation health unalerted
- Severity: P1 · Confidence: High · Area: metrics / alerting
- Evidence: live mtime ages 8/62/64/219 s but no rule in `90-alerting.sh:202-323` uses them; exporter has no self timestamp; live swap 4.7/8 GiB used with no swap alert; no `falcon_disk_guard_free_bytes` rule; rules live only in Grafana (`prometheus.yml` has no `rule_files`), so Grafana/relay death is externally invisible; `noDataState: OK` (`90-alerting.sh:169`) treats vanished series and stale textfiles as healthy; relay publish failures are journal-only (2 alt failures Sep 28).
- What is happening: every monitor can die silently while dashboards look healthy.
- Why it matters: silent monitor death equals silent blindness across all feeds.
- User / business impact: undetected monitoring loss; false confidence. · Security / privacy / reliability impact: observability assurance.
- Recommended fix: mtime-staleness alert, swap >75 % for 30 m, guard free <15 GiB, `node_textfile_scrape_error`, watcher-age, relay publish-failure metric, external eval-plane dead-man. · Suggested validation: stop each timer → statement alert fires; stop Grafana → external path fires.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none
- Status: partially-fixed (prior LIVE-P1-002; metrics exist, controls do not)

### Finding ID: OBS-P1-004 - Edge fleet has live metrics and dashboards but zero alerts
- Severity: P1 · Confidence: High · Area: alerts / edge
- Evidence: live `falcon_edge_metrics.prom`: 9 sensors (1 ACTIVE, heartbeat 51 s; 5 RETIRED + 3 REVOKED at ~34 h); no rule consumes `falcon_edge_*`; `config/prometheus/prometheus.yml` has no `rule_files`; rules prepared in `falcon-edge-build/config/prometheus/edge-alerts.yaml`, `deploy_edge_alert_rules.sh` dry-run by default, D-007 defers deployment; the prepared `EdgeSensorRevoked` rule would fire immediately on the 3 revoked test sensors.
- What is happening: the fleet is observable but not alertable; a lost sensor/queue loss/cert expiry pages no one.
- Why it matters: fleet blind spot and delayed recovery.
- User / business impact: unseen device loss. · Security / privacy / reliability impact: edge security posture.
- Recommended fix: scope rules (exclude retired/revoked residue, as `EdgeSensorSilence` already does), complete D-007 deployment into the central catalogue. · Suggested validation: dry-run plan executed; simulated ACTIVE-sensor silence fires; no fire for residue.
- Owner suggestion: edge maintainer + falcon maintainer · Effort: M · Dependencies: D-007 owner decision
- Status: still-open (prior INTG-P1-001)

### Finding ID: OBS-P1-005 - Peers that never handshaked are invisible to the WireGuard stale rule
- Severity: P1 · Confidence: High · Area: VPN metrics
- Evidence: live `falcon_wg_peers_total 6` vs 4 exported per-peer ages (10.99.0.10/.21/.22/.30); `export_monitor_metrics.sh:147-156` skips peers whose endpoint is `(none)`; `90-alerting.sh:297-299` needs a per-peer series.
- What is happening: configured-but-idle peers (10.99.0.2 test, 10.99.0.20 samsung) can never alert.
- Why it matters: a device lost before its first handshake is unmonitored.
- User / business impact: silent connectivity gaps; lost-device blind spot. · Security / privacy / reliability impact: fleet integrity.
- Recommended fix: export every configured peer (`-1`/large age when never handshaked); retire or label the test peer. · Suggested validation: add a never-connected peer → alert condition true.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: still-open (prior LIVE-P1-003)

### Finding ID: OBS-P2-001 - TLS-silence tuning works so far; benign-message noise and the 7-day re-measure remain
- Severity: P2 · Confidence: High (counts) / Medium (post-tune) · Area: signal quality
- Evidence: 7 d counts — TLS-silence 46/79 primary FIRING (58.2 %), device-syslog-errors 4, rest ≤3; `d83f421` set `for: 6h` (`90-alerting.sh:234-236`); fires at 00:08/01:08/02:09/03:09/04:09Z stopped at 04:12:28Z, zero since (~10.8 h); device-syslog-errors fired 02:04–02:09Z with no benign UniFi-family exclusion; `Disk space low` flapped 08:03→08:38Z.
- What is happening: the largest noise source is curbed; second-tier noise is unchanged and the sample is short.
- Why it matters: noise erodes alert trust; only a 7-day measurement proves the tune.
- User / business impact: operator fatigue if noise returns. · Security / privacy / reliability impact: missed real events; TLS outage detection now up to 6 h late.
- Recommended fix: benign-family suppression/per-host dedupe; expected-rate budgets per rule; re-measure 2026-10-07. · Suggested validation: 7-day counts inside budget; a real UniFi error still pages.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: 7-day data
- Status: partially-fixed (prior LIVE-P0-004 + LIVE-P1-004)

### Finding ID: OBS-P2-002 - Daily Suricata rotation remains invisible to its restart rule
- Severity: P2 · Confidence: High · Area: monitoring-of-the-monitoring
- Evidence: `export_monitor_metrics.sh:106` reads Docker `.RestartCount`; `90-alerting.sh:273-275` alerts on `increase(falcon_suricata_restarts_total[1h]) > 3`; live proof `min_over_time(falcon_suricata_uptime_seconds[25h])=0` while `increase(falcon_suricata_restarts_total[25h])=0`; `OPERATOR_START_HERE.md:60-65` says restarts should read 0.
- What is happening: in-container rotation restarts reset uptime but not RestartCount; rule and doc both miss them.
- Why it matters: a crash-loop class remains invisible to the rule added for it.
- User / business impact: capture gaps unnoticed; false assurance. · Security / privacy / reliability impact: feed integrity.
- Recommended fix: alert on uptime resets (`delta(...) < 0`/`resets`), keep RestartCount secondary; correct the runbook. · Suggested validation: simulate restart → alert; normal rotation documented.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: still-open (prior LIVE-P2-004)

### Finding ID: OBS-P2-003 - Firing-proof coverage incomplete; one raw artifact contradicts its summary
- Severity: P2 · Confidence: High · Area: alert validation
- Evidence: delivered live in 7 d — TLS-silence, syslog-514, device-syslog-errors, disk-warning, capture-fidelity, SPAN/NetFlow/15140 silence, service-down, site-down, VPN-stale, sensor-silence, probe-buffer, container-unhealthy; drilled earlier — target-down (P4-G09), DLQ + backup-stale (P7-G08), disk-critical (P5-G08 delivery proofs); no artifact found for memory-low, OpenSearch red/unknown, device-link-flap, kernel-drops, site disk/memory, wazuh rules, restart-loop; `P5-G08/...disk-pressure-drill.out:8,14` says disk rules "NOT active after 600s" while `PERFORMANCE_ENVELOPE.md` claims both fired.
- What is happening: "provisioned and evaluated" is treated as proof for roughly a third of rules, and one doc contradicts its raw evidence.
- Why it matters: release confidence rests on unexercised detections.
- User / business impact: surprises when it matters. · Security / privacy / reliability impact: incident readiness.
- Recommended fix: per-rule proof requirement, safe drills for the unproven set, reconcile envelope vs raw artifact, regenerate catalogue `tests` from artifacts. · Suggested validation: proof table where every critical-path rule has raw delivery output.
- Owner suggestion: falcon maintainer + owner (drill windows) · Effort: M · Dependencies: quiet window
- Status: open (prior run noted gaps; new contradiction)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Host loss announced up to 26 h late | P1 | Medium | Long outages | heartbeat/watch docs; Sep 28 | watcher alert + shorter threshold |
| Silent offsite failure recurs | P1 | Medium | Data-protection gap | offsite evidence; no rule | outcome metrics + alerts |
| Monitor/exporter/Grafana dies silently | P1 | Medium | Blindness | mtime unalerted; journal-only failures | staleness + external checks |

## Recommendations

### Immediate / Release Blocking
- Offsite/new-services freshness metrics + 36 h alerts (OBS-P1-002).
- Watcher-age and textfile-staleness alerts (OBS-P1-001/003).

### This Week
- Scoped edge deployment (D-007), revoked/retired exclusion (OBS-P1-004).
- Uptime-reset Suricata rule (OBS-P2-002); swap/guard/scrape-error alerts; relay failure metric.

### This Month
- Safe firing drills for unproven rules (OBS-P2-003); per-rule noise budgets + 7-day TLS re-measure; repair throughput panel; update drift runbooks.

### Later / Platform Evolution
- External end-to-end alert-path probe, mutual dead-man, continuous DQ metrics, N/A tracing statement.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Watcher-age rule | watcher death visible | `bootstrap/90-alerting.sh` | drill |
| mtime staleness rules | dead exporters caught | `bootstrap/90-alerting.sh` | stop timer → fire |
| Offsite success metric | closes silent-backup lesson | `80-offsite-backup.sh`, exporter | break probe → fire |
| Uptime-reset rule | rotation/crash visible | `90-alerting.sh` | simulate restart |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| External alert-eval dead-man | P1 | falcon maintainer | M | DO access |
| Edge rules scoped + deployed | P1 | edge maintainer | M | D-007 |
| Firing-proof drill program | P2 | owner + maintainer | M | quiet windows |
| Noise budgets in catalogue tool | P2 | falcon maintainer | S | 7-day data |

## Suggested Tests

- Unit: relay auth/failure branches; expression lint (bool modifier) in CI.
- Integration: stop each timer → freshness alert; stop Grafana → external dead-man; break Spaces probe → offsite alert.
- E2E: one safe drill per unproven rule with raw delivery capture on both ntfy paths.
- CI: catalogue == live rules; every rule has runbook + proof status.

## Suggested Documentation Updates

- `ALERT_CATALOGUE.yaml`: regenerate `tests` from raw artifacts.
- `OPERATOR_START_HERE.md`: correct buffer/rotation claims; alert-path health checklist.
- `SENSOR_SILENCE.md`: remove "no VPN / no physical SPAN".

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Owner-accepted host-loss detection target? | sets watcher threshold | owner decision record |
| Does Grafana notify on `execErrState: Error`? | blind-failure path | config/test |
| Does the DO watcher observe lab ntfy via tunnel or a copy? | dead-man correctness | out-of-repo watcher source |

## Appendix

Live accounting (relay journal 2026-09-23→30, primary): Syslog-TLS 46; device-syslog-errors 4; syslog-514, post-reboot (manual), disk-low, capture-fidelity 3 each; service-down, SPAN/NetFlow/15140 silence, site-down 2 each; VPN-stale, cert drill, sensor-silence, relay-verification, probe-buffer high/critical, container-unhealthy 1 each. Post-tune: only `Disk space low` (08:03→08:38Z). Alt failures: 2 (Sep 28 DNS). Rule-expression checks (15:00Z): `count(up==0)=0`; event age 2 s; DLQ 0; TLS 5 m empty but `max_over_time(tls[6h])=1`; bool-fix expressions all false; 931/1 962 five-minute samples empty over 7 d (47.4 %) — the 6 h window trades noise for up to 6 h detection latency.
