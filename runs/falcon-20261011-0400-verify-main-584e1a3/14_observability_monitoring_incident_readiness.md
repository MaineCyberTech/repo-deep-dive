# 14_observability_monitoring_incident_readiness — Prompt 14 - Observability, Monitoring, and Incident Readiness Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `14_observability_monitoring_incident_readiness.md` (area OBS, prompt)

## Verification Performed

# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` @ `08e20d1` (branch `main`)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-09T21:55Z
- Auditor: subagent (OBS)
- Area code: OBS
- Scope limitation: read-only; Grafana/Prometheus APIs queried with read-only GETs; alert history is sampled (annotation API cap 500; relay journal since Oct 6); no alert was injected by this audit.

## Scope

Reviewed structured logs, correlation, error tracking, metrics, tracing, health/readiness, job metrics, queue/webhook/notification metrics, uptime checks, alerts, dashboards, incident runbooks, audit/security logs, release markers, and user-impact/data-quality signals at `08e20d1`, and verified the live alerting deployment: Prometheus targets, Grafana-managed rules, active alerts, delivery paths, rule provisioning vs code, and alert-quality signals over Oct 6–9.

## Evidence Reviewed

- `config/prometheus/prometheus.yml`, `config/prometheus/edge-alerts.yaml`
- `bootstrap/90-alerting.sh` (83 rules), `automation/validation/export_monitor_metrics.sh`, `alert_canary.sh`, `heartbeat.sh`, `service_probe.sh`
- `config/systemd/falcon-metrics.timer`, `falcon-service-probe.timer`, `falcon-alert-canary.timer`, `falcon-heartbeat.timer`, `falcon-alert-relay.service`
- `automation/alerting/ntfy_relay.py`, `automation/alerting/do_watcher/watch.sh`
- `docs/runbooks/MONITORING_SCRAPE_AND_FRESHNESS.md`, `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`, `docs/phase9/ALERT_CATALOGUE.yaml`, `docs/phase9/ALERT_FIRING_PROOFS.md`
- Live: Prometheus `/api/v1/targets`, `/api/v1/alerts`, `/api/v1/query`; Grafana `/api/v1/provisioning/alert-rules`, `/api/prometheus/grafana/api/v1/rules`, alertmanager API, annotations; `journalctl -u falcon-alert-relay.service`; container logs/metrics

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Prometheus `/api/v1/targets` | Live | Scrape coverage | 5 jobs, all `health=up` (prometheus, node, traefik, vector-aggregator, grafana) |
| Grafana rule list vs `90-alerting.sh` | Live/Repo | Deployment completeness | 77 live vs 83 in code; 6 rules missing (comm diff) |
| Grafana rules API | Live | Rule health | 77/77 `health=ok`; 12 pending/firing at 21:47Z |
| Alertmanager active alerts | Live | Current signal | 9 feed/projection alerts during the pipeline incident |
| `journalctl -u falcon-alert-relay` | Live | Delivery + noise | Both paths HTTP 200; 334 FIRING lines Oct 6–9 (50/62/262/294 per day) |
| Grafana annotations (8 d) | Live | Signal quality | 500 state changes in the last 2.5 h; top offenders counted |
| `vector_component_discarded_events_total` | Live | Blind spot | 677,475 source drops not exported by the exporter |
| `falcon_site_watcher_last_run_timestamp_seconds` | Live | External check | Age 515 s (fresh); relay publish failures 0 |
| `ALERT_CATALOGUE.yaml` vs live | Repo/Live | Artifact consistency | 79 vs 77; 3 listed-not-live, 1 live-not-listed |

## Executive Summary

The monitoring stack is broad and mostly healthy: five Prometheus scrape jobs are up (including the direct Vector and Grafana scrapes added for OBS-P0-001), the monitoring-of-monitoring rules are live and healthy, the external DO watcher is fresh, the hourly heartbeat is running, the three-path alert canary reports all paths up, and alert delivery to both the lab and independent ntfy paths returned HTTP 200 throughout the Oct 7–9 incidents. The textfile freshness layer, however, is not deployed: the live Grafana rule set has 77 rules and is missing six rules present in the repository — the three per-file `node_textfile_mtime_seconds` freshness rules, `falcon-monitoring-scrape-absent`, `falcon-backup-offsite-dlq` and `falcon-relay-path-failures`. The lab's own runbook records that provisioning is still pending, and the runtime tree is 22 commits behind origin/main, so the prior run's "verified-fixed" claim for OBS-P0-001 holds for the code only, not for the live deployment.

Two further gaps matter operationally. First, the source side of the pipeline is invisible: the exporter reads only sink metrics, so the 677K–1.5M events the aggregator dropped during the Oct 9 OOM episode produced no alert for the loss itself (only buffer-cap and feed-silence alerts fired). Second, signal quality is noisy under stress: 334 FIRING notifications in four days, 500 state changes in 2.5 hours during the incident, and a root-disk projection alert triggered by the one-off 60 GB snapshot-repo relocation rather than a real trend. The committed alert catalogue also contradicts the live rule set while claiming it cannot drift.

## Findings Summary

| # | Prior ID | Severity | Title | Status |
|---|---|---|---|---|
| 1 | OBS-P0-001 | P1 | OBS-P0-001 remediation not provisioned live; 6 rules missing; runtime tree 22 commits behind | partially-fixed (runtime) |
| 2 | — | P1 | Aggregator source-side drops neither exported nor alerted | open |
| 3 | — | P2 | ALERT_CATALOGUE.yaml contradicts live Grafana | open |
| 4 | — | P2 | Alert noise/flapping high; projection false-positive from the relocation step | open |
| 5 | — | P3 | Live alerting config is uncommitted drift ahead of the audited commit | open |

## Detailed Findings

### 1. OBS-P0-001 remediation not provisioned live (P1, prior OBS-P0-001)

The direct-scrape half of the prior P0 is live and healthy (5 targets up). The monitoring-death rules added by PR #46/#49 are not: the live Grafana set (77 rules, all healthy) lacks `falcon-textfile-collector-stale`, `-stale-daily`, `-absent` (`bootstrap/90-alerting.sh:632-642`), `falcon-monitoring-scrape-absent` (`:620-622`), `falcon-backup-offsite-dlq` (`:467-469`) and `falcon-relay-path-failures` (`:543-545`). The repository documents this residual itself: "Provisioning the new rules live requires running `bootstrap/90-alerting.sh` on the lab" (`docs/runbooks/MONITORING_SCRAPE_AND_FRESHNESS.md:77-82`). Root cause: the live runtime tree `/home/user/falcon-build` is 22 commits behind origin/main (`git rev-list --count HEAD..origin/main` = 22) and its provisioning script (81 lines, 80 rules) predates the Oct 5 additions; the tree also lacks `automation/validation/restore_assertion.sh`. The prior follow-up register's `verified-fixed` note (PR #46 merge) is therefore only a code claim.

**Fix:** deploy current main (or run the provisioning script from the audited tree), verify the six rules evaluate, and add a drift check comparing provisioned rule IDs to the script/catalogue. **Validation:** Grafana rule count reaches 83 and each new rule reports `health=ok`; a deliberate collector-stall test fires `falcon-textfile-collector-stale`.

### 2. Aggregator source-side drops neither exported nor alerted (P1)

`automation/validation/export_monitor_metrics.sh` exports only sink-side Vector metrics (`falcon_pipeline_sink_http_errors/errors/discarded/buffer`, lines 66-77). The source-side counter `vector_component_discarded_events_total{component_id="edge_ingest",component_kind="source",intentional="false"}` is not read and no rule covers it: it reached 677,475 in the current instance and 1.5M+ in the prior one while the container logged "Source send interrupted mid-flight" thousands of times per event. During the Oct 9 incident the only pipeline alerts were buffer-cap and feed-silence; nothing alerted on the loss itself, and the loss class is the one the OOM loop produces. **Fix:** export source dropped/received counters and add a rule (increase > 0 or a drop-ratio threshold) plus a Vector restart/OOM counter; prove with a bounded drill.

### 3. ALERT_CATALOGUE.yaml contradicts live Grafana (P2)

The committed catalogue has 79 alerts and lists the three textfile-collector rules that are not provisioned live, while omitting `falcon-feed-stale-wazuh`, which is live. The file header says "Generated from the live Grafana rules" and the generator docstring claims "regenerated from the live rules so it cannot drift from what is deployed" (`build_alert_catalogue.py:1-9`) — both are false against the current lab. **Fix:** regenerate the catalogue after closing finding 1 and add a catalogue-vs-live comparison to the drift gate.

### 4. Alert noise/flapping high; projection false-positive (P2)

The relay published 334 FIRING notifications in four days (Oct 6–9: 50/62/262/294 lines including both paths; ≈167 firing episodes), and 500 alert state-change annotations accumulated in the 2.5-hour 19:16–21:42Z window during the incident. Top offenders since Oct 6: "Live source tree not reviewable" 44, "Wazuh alert feed stale" 40, "Syslog-TLS feed stale" 40, "Host memory pressure (early warning)" 38, feed-silence families ~26–36 each, "Probe buffer" 52 combined, "Container unhealthy" 24. The "Root disk projected full within 7 days" alert fired at 20:49Z because `predict_linear` over 6 h saw the one-off 60 GB snapshot-repo copy (`predict_linear(...) = -757,706,754,084`; root 83%) — a step change, not a trend. **Fix:** add step-change suppression or a trend floor to projection rules, review repeat/for tuning for the noisiest rules, and run the documented 7-day noise accounting after each incident.

### 5. Live alerting config is uncommitted drift (P3)

The live `/etc/prometheus/edge-alerts.yaml` is 340 lines vs 235 in the audited commit, and the live tree has `config/prometheus/edge-alerts.yaml` modified-uncommitted with 2026-10-09 additions (sensor hardware-health, capture-service, inventory collector-gating; e.g. `EdgeSensorCaptureInterfaceMissing`, firing since 19:24Z). Alerting changes are not bound to any reviewed commit, so the audited commit cannot reproduce the live rule set. **Fix:** commit or revert the live changes, regenerate the catalogue, and add config-vs-commit binding to the drift gate.

## Strengths (verified)

- 5/5 Prometheus targets up; monitoring-of-monitoring rules (`falcon-mom-series-absent`, `falcon-metrics-exporter-stale`, `falcon-service-probe-stale`, `falcon-textfile-scrape-error`) live and healthy.
- External dead-man path alive: DO watcher age 515 s (threshold 7,200 s), hourly heartbeat, dead-man contract asserted offline; relay publish failures 0; canary paths (lab/independent/relay) all up.
- Delivery worked end to end during real incidents: cluster-red, backup-stale and feed-silence alerts published HTTP 200 to both paths.
- Job/queue metrics are rich (backup/offsite/cold-copy/Wazuh freshness, feed age, sink health, container drift, retention, spool) with documented alert rules.

## Prior-Run Comparison

| Prior finding | Prior claim | Current evidence | Current disposition |
|---|---|---|---|
| OBS-P0-001 (textfile-collector dependence) | verified-fixed (PR #46 merged) | Direct scrapes live; freshness rules not provisioned; tree 22 behind; runbook says pending | partially-fixed at runtime (finding 1) |
| NOTIF-P2-001 etc. (other domains) | — | Not re-audited here | see respective domain reports |

## Scorecard

| Category | Score | Evidence | Gap |
|---|---:|---|---|
| Structured logs | 3 | Vector/OpenSearch pipelines; redaction transforms | — |
| Request IDs/correlation | 2 | site/sensor identity, ingested_at; no request-id propagation | No correlation IDs across services |
| Error tracking | 2 | No Sentry-class tracker; logs + counters only | Error aggregation manual |
| Metrics | 3 | Textfile + direct scrapes; 5 jobs | Source-side drops not exported |
| Tracing | 1 | None found | No tracing |
| Health/readiness | 4 | Healthchecks everywhere; service probe; edge healthz | — |
| Client/API/worker errors | 3 | Sink/worker counters + rules | Source worker drops blind |
| Job metrics | 4 | Backup/cold-copy/Wazuh/drift/E2E freshness + rules | Some rules not provisioned |
| DB/queue/webhook/notification metrics | 3 | Sink, buffer, relay, spool | Offsite-DLQ + relay-path rules not provisioned |
| Uptime checks | 4 | Service probe + site watcher + canary | — |
| Alerts | 3 | 77 live, healthy; delivered | 6 missing; noise |
| Dashboards | 3 | 3 dashboards provisioned | — |

## Limitations

- Alert-history counts come from the relay journal (since Oct 6) and a 500-entry annotation sample; they are lower bounds for the 8-day window.
- The live Grafana rule set was compared by ID; rule bodies for live-only changes were compared only for `edge-alerts.yaml` (Prometheus).
- Concurrent remediation work on the host during the window (relocation, rule edits) means some drift may be mid-flight rather than settled.

## Findings

| ID | Severity | Title |
|---|---|---|
| OBS-P0-001 | P1 | OBS-P0-001 remediation not provisioned live: 6 rules missing from Grafana; runtime tree 22 commits behind |
| OBS-P1-001 | P1 | Aggregator source-side event drops neither exported nor alerted; 0.7-1.5M events dropped unseen |
| OBS-P2-001 | P2 | ALERT_CATALOGUE.yaml contradicts live Grafana while claiming it cannot drift |
| OBS-P2-002 | P2 | Alert noise/flapping high during incidents; root-disk projection false-positive from the relocation step |
| OBS-P3-001 | P3 | Live alerting config is uncommitted drift ahead of the audited commit (edge-alerts.yaml) |
