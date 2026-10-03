# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: OBS
- Output path: docs/audits/{name}/{run}/14_observability_monitoring_incident_readiness.md
- Scope limitations: no live Prometheus/Grafana; rule evaluation is static.

## Scope

Reviewed Prometheus scrape config, Grafana alert provisioning (`bootstrap/90-alerting.sh`), the metrics exporter, the ntfy relay and canaries, and incident-readiness docs.

## Evidence Reviewed

- `config/prometheus/prometheus.yml` (3 targets).
- `bootstrap/90-alerting.sh` (rule generation), `automation/validation/export_monitor_metrics.sh` (textfile exporter).
- `automation/validation/alert_canary.sh`, `heartbeat.sh`, `tests/alert_expression_bool_test.sh`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/prometheus/prometheus.yml` | Config | Scrape coverage | only 3 targets |
| `export_monitor_metrics.sh` | Source | Textfile SPOF | single export path |
| `alert_expression_bool_test.sh` | Test | bool-vs-raw guard | present (partial fix) |
| `docs/CURRENT_STATE.md` C4 | Doc | live canary status | 3-path canary live |

## Executive Summary

Alerting is extensive (70+ rules, live three-path canary, freeze-drill firing proofs) but structurally fragile: Prometheus scrapes only three targets and nearly all `falcon_*` signals are manufactured by the node-exporter textfile collector, so one exporter failure blinds alerting. Two prior rule-quality findings are partially remediated (an expression test exists); relay failure accounting remains all-or-nothing, so partial path loss is caught only by the weekly canary.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Prometheus | `config/prometheus/prometheus.yml` | scrape | Functional | High | 3 targets |
| Exporter | `export_monitor_metrics.sh` | textfile metrics | Functional | High | SPOF |
| Alert rules | `bootstrap/90-alerting.sh` | rules | Functional | Medium | ~70 |
| Relay | `falcon-alert-relay` | ntfy delivery | Functional | Medium | counter granularity |
| Canary | `alert_canary.sh` | e2e proof | Functional | Low | weekly |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Metrics coverage | 2 | 3 scrape targets | SPOF | OBS-P0-001 |
| Alert rules | 3 | 70+ rules | duplicates | OBS-P1-002 |
| Alert quality | 3 | expression test | lint coverage | OBS-P1-001 |
| Delivery | 3 | canary + relay | partial-path math | OBS-P1-003 |
| Dashboards | 4 | Grafana JSON | — | — |
| Runbooks | 3 | catalogue | runbook_url | IR |

## Findings

### Finding ID: OBS-P0-001 - Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector

- Severity: P0
- Confidence: High
- Area: OBS
- Evidence:
  - `config/prometheus/prometheus.yml` — targets: `localhost:9090`, `node-exporter:9100`, `traefik:8082`
  - `automation/validation/export_monitor_metrics.sh` (49 KB) — writes the metric textfile
  - `heartbeat.sh` — dead-man depends on the same path
- What is happening: The monitoring system's own health is largely self-reported by one exporter file.
- Why it matters: If the exporter or its timer stalls, stale values can look healthy; alerting on monitoring death is weak.
- User / business impact: Total-loss detection latency.
- Security / privacy / reliability impact: Observability SPOF.
- Recommended fix: Scrape exporters directly (OpenSearch/Vector/ntfy) where possible, add a freshness/`up` rule per exporter, and make the dead-man independent of the textfile.
- Suggested validation: Stop the exporter timer; a `falcon_*_last_run` staleness rule fires within minutes.
- Owner suggestion: observability
- Effort estimate: M
- Dependencies: exporter targets
- Status: open

### Finding ID: OBS-P1-001 - Alert expressions mix `bool` and raw comparison forms with no linter

- Severity: P1
- Confidence: Medium
- Area: OBS
- Evidence:
  - `bootstrap/90-alerting.sh` — rules use both `... >= bool 0` and raw comparisons
  - `automation/validation/tests/alert_expression_bool_test.sh` — guards a subset
- What is happening: `bool` changes firing semantics (always returns 0/1), so mixing forms can mis-fire.
- Why it matters: Silent alert failures.
- User / business impact: Missed incidents.
- Security / privacy / reliability impact: Reliability of alerting.
- Recommended fix: Add a rule linter enforcing one comparison style and validating expressions parse.
- Suggested validation: Linter test over every generated rule.
- Owner suggestion: observability
- Effort estimate: M
- Dependencies: rule generator
- Status: partially-fixed

### Finding ID: OBS-P1-002 - Duplicate/overlapping rules and a self-contradictory firing-proof coverage total

- Severity: P1
- Confidence: Medium
- Area: OBS
- Evidence:
  - `bootstrap/90-alerting.sh` — multiple rules with overlapping conditions
  - firing-proof coverage totals previously inconsistent (prior run); a reconciliation section exists
- What is happening: Some rules overlap and coverage accounting was internally inconsistent.
- Why it matters: Duplicate pages and false confidence in coverage.
- User / business impact: Alert fatigue; gaps hidden.
- Security / privacy / reliability impact: Alerting quality.
- Recommended fix: De-duplicate rules and derive the coverage total from the rule set rather than hand-maintaining it.
- Suggested validation: Generator emits a count; a test asserts it matches the rule list.
- Owner suggestion: observability
- Effort estimate: M
- Dependencies: None
- Status: partially-fixed

### Finding ID: OBS-P1-003 - Relay failure counter is all-or-nothing; partial-path degradation is caught only by the weekly canary

- Severity: P1
- Confidence: High
- Area: OBS
- Evidence:
  - `falcon-alert-relay` service + `export_monitor_metrics.sh` — relay failure metric
  - `automation/validation/alert_canary.sh` — weekly three-path proof
- What is happening: There is no per-path/per-topic success metric, so one failed destination among several is invisible until the canary runs.
- Why it matters: Degraded delivery can go unnoticed for up to a week.
- User / business impact: Missed alerts.
- Security / privacy / reliability impact: Notification reliability.
- Recommended fix: Emit per-path delivery counters (success/failure/latency) and alert on any path failing.
- Suggested validation: Fault-inject one path; per-path rule fires within one interval.
- Owner suggestion: observability
- Effort estimate: M
- Dependencies: relay code
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Textfile SPOF blinds alerting | P0 | Medium | High | prometheus.yml | OBS-P0-001 |
| Mis-fired expression | P1 | Medium | High | 90-alerting.sh | OBS-P1-001 |
| Silent partial delivery loss | P1 | Medium | High | relay | OBS-P1-003 |

## Recommendations

### Immediate / Release Blocking
- Make monitoring-death detection independent of the textfile (OBS-P0-001).

### This Week
- Per-path relay metrics (OBS-P1-003).

### This Month
- Rule linter + dedup (OBS-P1-001/002).

### Later / Platform Evolution
- Direct service scrapes.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Staleness rule on exporter | Early detection | 90-alerting.sh | rule fires |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Per-path relay metrics | P1 | observability | M | relay |
| Rule linter | P1 | observability | M | generator |

## Suggested Tests

- Exporter-stall fires a staleness alert.
- Every generated expression parses and uses one comparison style.

## Suggested Documentation Updates

- Document the metric provenance (which signals come from the textfile).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are direct scrapes feasible for OpenSearch/ntfy? | OBS-P0-001 fix | service metrics endpoints |

## Appendix
Not applicable.
