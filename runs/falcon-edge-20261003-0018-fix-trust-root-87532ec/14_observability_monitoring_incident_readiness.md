# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: OBS
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/14_observability_monitoring_incident_readiness.md
- Scope limitations: no live Prometheus/Grafana; alert rules and runbooks reviewed statically. Delivery/alerting path not exercised.

## Scope

Reviewed the 21 Prometheus alert rules (`config/prometheus/edge-alerts.yaml`), the Grafana dashboard, the metrics exporters (`automation/observability/fleet_metrics.py`, `automation/validation/inventory_metrics.py`), runbooks, and the documented monitoring topology.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/prometheus/edge-alerts.yaml` | Config | 21 rules | golden-signal coverage |
| `automation/observability/fleet_metrics.py` | Source | Exporter | writes textfile |
| `automation/validation/inventory_metrics.py` | Source | Inventory metrics | SSH collector |
| `config/grafana/edge-fleet-dashboard.json` | Config | Dashboard | committed JSON |
| `docs/runbooks/*` | Docs | Incident response | 17 runbooks |
| `docs/CURRENT_STATE.md`, `AGENTS.md` | Docs | Live state | no Alertmanager |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Rule count/severity | Static | Coverage | 21 rules |
| Runbook link check | Static | Triage path | each rule names a runbook |
| Delivery path read | Static | Paging | no Alertmanager |
| Freshness rule check | Static | Monitoring-of-monitoring | `EdgeMetricsStale`, `EdgeInventoryExporterDown` |

## Executive Summary

Observability is strong on paper for a lab: 21 alert rules covering silence, queue backlog/loss/age, certificate expiry, quarantine/revocation, thermal/disk/memory/cpu, capture drops, and exporter staleness; every rule links a runbook; there is monitoring-of-the-monitoring for the exporter. The critical caveat is delivery: **there is no Alertmanager**, so alerts are only visible via the Prometheus API/Grafana and nobody is paged. The inventory metric path also depends on host-side SSH to the sensors, so a single host/SSH failure blinds several rules.

## Inventory

| Item | Path | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Alert rules | `edge-alerts.yaml` | 21 rules | Deployed (ED-21) | Med | delivery gap |
| Exporter | `fleet_metrics.py` | Edge metrics | textfile | Low | — |
| Inventory metrics | `inventory_metrics.py` | Inventory health | SSH collector | Med | host SPOF |
| Dashboard | `edge-fleet-dashboard.json` | Visual | committed | Low | — |
| Runbooks | `docs/runbooks/*` | Triage | 17 files | Low | good |
| Paging | none | Delivery | absent | High | OBS-P2-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Structured logs | 3 | runner JSON prints | no levels | minor |
| Request ids/correlation | 4 | `x-correlation-id` | — | — |
| Error tracking | 3 | problem bodies | no aggregator | minor |
| Metrics | 4 | 21 rules | in-repo exporter only | — |
| Tracing | 1 | none | N/A lab | document |
| Health/readiness | 4 | `/healthz` + source state | no readiness depth | minor |
| Client/API/worker errors | 3 | events/audit | no error-rate alert | P3 |
| Job metrics | 4 | inventory/export metrics | — | — |
| DB/queue/webhook metrics | 4 | queue rules | — | — |
| Uptime checks | 3 | `EdgeMetricsStale` | external probe absent | P2 |
| Alerts | 4 | 21 rules | no Alertmanager | P2 |
| Dashboards | 3 | one dashboard | — | — |
| Incident runbooks | 4 | 17 runbooks | — | — |
| Release markers | 3 | `source_commit` | not a metric | P3 |

## Detailed Review

### Item: Alert delivery

- Evidence: `docs/CURRENT_STATE.md` — "No Alertmanager exists, so alerts surface via the Prometheus API/Grafana rather than paging"; `AGENTS.md` similar.
- Gap: no notification channel, no escalation, no alert-fatigue measurement.
- Risk: OBS-P2-001.

### Item: Inventory metrics delivery

- Evidence: `inventory_metrics.py` SSHes to sensors; `EdgeInventoryStale/Unreadable/ExporterDown` depend on it.
- Gap: host SSH is a single point; `StrictHostKeyChecking=no` (SEC-P2-002).
- Risk: OBS-P2-002.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| OBS-001 | Structured logs | agent JSON | present | framing | P3 | minor |
| OBS-002 | Correlation | headers | present | — | — | — |
| OBS-003 | Error tracking | problem/audit | present | aggregator | P3 | optional |
| OBS-004 | Metrics | rules/exporters | strong | — | — | — |
| OBS-005 | Tracing | none | N/A | — | — | — |
| OBS-006 | Health | `/healthz` | present | depth | P3 | minor |
| OBS-007 | Job metrics | inventory | present | SPOF | P2 | OBS-P2-002 |
| OBS-008 | Uptime | stale rules | present | external probe | P2 | add |
| OBS-009 | Alerts | 21 rules | present | no delivery | P2 | OBS-P2-001 |
| OBS-010 | Release markers | source state | partial | no metric | P3 | add metric |

## Findings

### Finding ID: OBS-P2-001 - No alert delivery path (no Alertmanager/pager); rules are visible only in Prometheus/Grafana

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - `docs/CURRENT_STATE.md` — "No Alertmanager exists, so alerts surface via the Prometheus API/Grafana rather than paging"
  - `config/prometheus/edge-alerts.yaml` — rules carry `severity` labels but no receiver
  - `AGENTS.md` — edge rules deployed without paging
- What is happening: critical rules (`EdgeSensorQuarantined`, `EdgeSensorRevoked`, `EdgeControlPlaneNoSensors`) never reach a human unless someone looks.
- Why it matters: detection without delivery is not incident readiness; the failed-SDR alert is the only active one and is noticed manually.
- User / business impact: slow response to sensor/security incidents.
- Security / privacy / reliability impact: security events can go unseen.
- Recommended fix: add Alertmanager (or a Grafana alerting contact point) with at least one paging/email receiver for `severity=critical`, and a periodic "alert path alive" heartbeat.
- Suggested validation: fire a synthetic critical alert and confirm delivery end-to-end.
- Owner suggestion: owner + monitoring program
- Effort estimate: M
- Dependencies: central monitoring stack
- Status: open

### Finding ID: OBS-P2-002 - Inventory alert metrics depend on host-side SSH to each sensor (single point of failure)

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - `automation/validation/inventory_metrics.py` — SSH loop over `SENSORS` from the lab host
  - `config/prometheus/edge-alerts.yaml` — `EdgeInventoryStale`, `EdgeInventoryUnreadable`, `EdgeInventoryExporterDown`
  - `docs/CURRENT_STATE.md` — hourly timer on the lab host
- What is happening: all inventory health signals are produced by one host process reaching each sensor over SSH.
- Why it matters: if the host or SSH key path fails, the "exporter down" rules fire but the underlying sensors are unobserved; conversely the collector is a natural attack/target.
- User / business impact: blind spots and alert noise.
- Security / privacy / reliability impact: reliability of monitoring.
- Recommended fix: have each sensor self-export its inventory metrics (like the agent does), or add a second collection vantage.
- Suggested validation: stop the host collector and confirm alert semantics distinguish "sensor down" from "collector down".
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: agent metrics plumbing
- Status: open

### Finding ID: OBS-P3-001 - Stale `pending_directives` metric is documented but unfixed

- Severity: P3
- Confidence: High
- Area: OBS
- Evidence:
  - `AGENTS.md` — "Known metric artifact: `falcon_edge_sensor_pending_directives` counts expired-but-unmarked directives from the September drills ... do not alert on it"
  - `src/falcon_control/store.py` — `consume_directive` is never called; `pending_directive` filters by expiry but the counter can still over-report
- What is happening: a misleading metric is knowingly left in place with a "do not alert" note.
- Why it matters: operators must remember a special case; a future rule could alert on it.
- Security / privacy / reliability impact: low.
- Recommended fix: fix the counter (exclude expired) or remove it.
- Suggested validation: unit test that expired directives are excluded from the count.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No paging | P2 | High | Slow response | CURRENT_STATE | Alertmanager |
| SSH collector SPOF | P2 | Medium | Blind spots | inventory_metrics | per-sensor export |
| Stale metric | P3 | Low | Confusion | AGENTS.md | fix/remove |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Fix or remove the stale pending-directives metric.

### This Month
Add an alert delivery path with a critical receiver and a self-test.

### Later / Platform Evolution
Per-sensor metric export; tracing if the platform grows.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix pending metric | removes special case | exporter/store | test |
| Grafana critical contact | first delivery path | monitoring stack | synthetic alert |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Alert delivery | P2 | owner | M | central stack |
| Per-sensor inventory metrics | P2 | build-agent | M | agent |
| External uptime probe | P2 | owner | S | endpoint |

## Suggested Tests

- Synthetic critical alert end-to-end delivery.
- Collector failure vs sensor failure distinction.
- Rule/runbook link integrity.

## Suggested Documentation Updates

- `docs/CURRENT_STATE.md`: mark the alert-delivery gap as the top ops risk.
- `AGENTS.md`: move the stale metric from "known artifact" to a tracked fix.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is a central Alertmanager planned? | OBS-P2-001 fix | owner/monitoring plan |
| Can sensors export without host SSH? | OBS-P2-002 fix | agent design |

## Appendix

21 rules: 3 critical, 14 warning, 4 info. Every rule names a `runbook:` annotation. `EdgeMetricsStale` uses 600s (two missed 5-min exporter cycles). `EdgeInventoryExporterDown` uses `absent()` for 3h.
