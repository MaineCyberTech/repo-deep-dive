# 14 Observability, Monitoring & Incident Readiness

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Metrics, tracing, logging, alerting, dashboards, SLOs and incident readiness. Read-only.

## Evidence Reviewed

- `apps/realtime/src/server.ts` (`/metrics` exposition, `renderPrometheusMetrics`, `captureMetricsSnapshot`)
- `apps/realtime/src/instrumentation.ts`, `infra/otel/collector-config.yaml`
- `docs/runbooks/INCIDENT.md`, `docs/runbooks/KILL_SWITCHES.md`, `docs/runbooks/BACKUP_RESTORE.md`
- `scripts/assurance/assurance.sh`, `scripts/assurance/ledger-format.mjs`
- `evidence/closeout/ALERT_TIMELINE.csv`, `evidence/closeout/G17_*`
- `apps/web/app/admin/page.tsx` / `apps/web/components/admin/AdminPage.tsx`

## Verification Performed

- Read the Prometheus exposition: fixed-cardinality series, `service` label only (cardinality policy enforced in code comments and `push` helper).
- Confirmed `/metrics` auth: bearer/`X-Metrics-Token` when configured; else loopback-only (server.ts 1170–1202).
- Read OTel collector config: OTLP/HTTP receiver → batch → **debug** exporter only.
- Read assurance script: detection/alerting runs from host crontab, writes JSONL ledger, alerts via ntfy.
- Confirmed no alert-rule or dashboard definition files exist in the repository.

## Executive Summary

Instrumentation is solid at the application layer: a well-defined Prometheus endpoint with fixed cardinality, per-response status-class counters, RUM/performance aggregates, durable metrics snapshots (migration 0053), structured pino logging with trace IDs, and OTLP tracing wired into the realtime service. The gaps are operational: traces terminate in the collector's `debug` exporter (no storage/query/retention), alert rules and dashboards live only outside the repo (host crontab + ntfy), and there are no committed SLO/error-budget definitions. Incident runbooks are clear and actionable, but their ability to fire automatically cannot be reproduced from the repository alone.

## Inventory

| Capability | State | Evidence |
|---|---|---|
| Prometheus metrics | Present, fixed cardinality | `server.ts` `push`/`renderPrometheusMetrics` |
| Metrics durability | Snapshot timer + migration 0053 | `captureMetricsSnapshot`, `METRICS_SNAPSHOT_INTERVAL_MS` |
| Tracing | OTLP/HTTP → collector | `instrumentation.ts`, collector config |
| Trace storage/query | Absent (`debug` exporter) | `infra/otel/collector-config.yaml` |
| Alerting | Host crontab + ntfy | `assurance.sh` `notify()` |
| Alert rules in repo | Absent | — |
| Dashboards in repo | Absent (admin UI is in-app) | — |
| SLO/error budget | Not formalized | `/launch-readiness` sloBurn only |

## Findings

### Finding ID: OBS-P1-001 - Alerting and scheduled detection are defined only on the host, not in the repository

- Severity: P1
- Confidence: High
- Area: OBS
- Evidence:
  - `scripts/assurance/assurance.sh` — designed to run "from crontab"; `notify()` reads `NTFY_TOPIC` from `/home/user/.env`
  - No crontab file, alert-rule file, or ntfy config is tracked in the repository
  - `.env.example` line 108 lists `NTFY_TOPIC` as host-only
- What is happening: The detection/alert topology is external and cannot be reproduced or version-controlled from the repo.
- Why it matters: A host rebuild loses alerting silently; thresholds are not reviewable.
- User / business impact: Outages may go undetected after migration/rehost.
- Security / privacy / reliability impact: Reliability/incident readiness.
- Recommended fix: Commit the crontab schedule (or a systemd timer), alert thresholds, and an ntfy/alerting config template; add an alert-path self-test to CI or the daily lane.
- Suggested validation: Rebuild host from repo + documented secrets; a forced failure alerts.
- Owner suggestion: Operator
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: OBS-P2-001 - OTel traces are exported only to the collector `debug` exporter

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - `infra/otel/collector-config.yaml` lines 12–20 — `exporters: debug` only
  - `infra/compose/docker-compose.yml` — `OTEL_ENABLED: "1"`, `OTEL_TRACES_SAMPLER_ARG: "0.1"`
- What is happening: Spans are logged, not stored or queryable.
- Why it matters: Distributed tracing provides no investigation capability (correlating session → room → run/purchase).
- User / business impact: Longer mean-time-to-diagnose.
- Security / privacy / reliability impact: Observability gap.
- Recommended fix: Add a real trace backend (or at least a retained file/OTLP sink) and a documented retention policy; keep sampling/redaction explicit.
- Suggested validation: A trace for a known request is retrievable after the fact.
- Owner suggestion: Operator
- Effort estimate: M
- Dependencies: OBS-P1-001
- Status: open

### Finding ID: OBS-P2-002 - No committed SLO/error-budget definitions

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - No SLO file in the tree; `server.ts` exposes only `sloBurn` derived from `classificationFailures` in `/launch-readiness`
  - `ext_review.md` recommends defining SLIs before targets
- What is happening: Service objectives exist informally (perf budgets, capacity lane) but are not declared as SLOs with burn policies.
- Why it matters: No agreed basis for paging vs. non-paging or for release gating.
- User / business impact: Inconsistent reliability decisions.
- Security / privacy / reliability impact: Reliability governance.
- Recommended fix: Define SLIs/SLOs (boot, join, run validation, purchase, reconnect) and wire alerts to error budgets.
- Suggested validation: SLO definition committed and referenced by alert rules.
- Owner suggestion: Operator/owner
- Effort estimate: M
- Dependencies: OBS-P1-001
- Status: open

### Finding ID: OBS-P3-001 - Metrics are process-local counters with durable history only when the snapshot timer is enabled

- Severity: P3
- Confidence: High
- Area: OBS
- Evidence:
  - `server.ts` — `_bootTotal`, `_authFailures`, etc. are in-memory; `startMetricsTimer` returns early when `metricsSnapshotIntervalMs <= 0`
  - compose sets `METRICS_SNAPSHOT_INTERVAL_MS: "300000"`
- What is happening: A restart resets counters; history depends on the snapshot timer and DB.
- Why it matters: Rate/trend analysis around a restart is incomplete.
- User / business impact: Low.
- Security / privacy / reliability impact: Observability quality.
- Recommended fix: Ensure the snapshot timer is explicit in prod configs (already done) and document restart semantics for dashboards.
- Suggested validation: Snapshot rows exist across a restart.
- Owner suggestion: Operator
- Effort estimate: S
- Dependencies: None
- Status: open

## Risks

- R-OBS-1: Non-reproducible alerting (P1).
- R-OBS-2: No trace retention (P2).
- R-OBS-3: No formal SLOs (P2).

## Recommendations

1. Version the alerting/schedule in-repo and self-test it.
2. Add trace storage/retention.
3. Define SLOs and burn alerts.

## Quick Wins

- Commit the crontab + thresholds (S).
- Document restart semantics for metrics (S).

## Hardening Backlog

- Dashboard-as-code for the admin metrics.

## Suggested Tests

- Forced-failure alert drill in the daily lane (exists as `ASSURANCE_DRILL=1`); capture evidence per release.

## Suggested Documentation Updates

- `docs/runbooks/INCIDENT.md`: link the alert rules once committed.

## Open Questions

- Is there an existing external dashboard/alert stack not captured in the repo? (`Unknown`.)

## Appendix

- `evidence/closeout/ALERT_TIMELINE.csv` and `G17_*` record an ntfy delivery exercise at an earlier commit.
