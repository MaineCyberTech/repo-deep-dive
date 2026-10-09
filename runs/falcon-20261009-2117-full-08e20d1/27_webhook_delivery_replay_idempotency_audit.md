# 27_webhook_delivery_replay_idempotency_audit — Prompt 27 - Webhook Delivery, Replay, and Idempotency Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `27_webhook_delivery_replay_idempotency_audit.md` (area WH, prompt)

## Verification Performed

# Webhook Delivery, Replay, and Idempotency Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-08e20d1`
- Branch: main (worktree detached at the audited commit)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:50:50Z
- Auditor: subagent (read-only; live checks read-only)
- Area code: WH
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/27_webhook_delivery_replay_idempotency_audit.md
- Scope limitations: Shuffle is retired live (no containers; manager integration disabled 2026-09-27), so only its vendored scripts were reviewed; the DO-side watcher and alt ntfy are owner-side (config verified from docs + metrics only).

## Scope

Reviewed inbound webhook endpoints (Grafana->relay), outbound notification delivery (relay->lab/alt ntfy, heartbeat, dead-man watcher), the Vector delivery path to OpenSearch (retries, buffering, DLQ), event models, signature/timestamp/replay controls, idempotency keys, retry/backoff, dead-letter handling, secrets, tenant scoping, payload handling, timeouts, delivery logs, admin management and rotation, and the webhook test inventory. Live read-only checks: relay metrics, spool presence, container state.

## Evidence Reviewed

- `automation/alerting/ntfy_relay.py` (auth, rate limit, publish, spool, metrics), `automation/alerting/do_watcher/{watch.sh,install.sh}`, `automation/validation/heartbeat.sh`
- `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`, `docs/architecture/PORT_PROTOCOL_MATRIX.md:40` (N-19)
- `config/vector/{edge.yaml,aggregator.yaml}`, `automation/validation/export_monitor_metrics.sh`, `bootstrap/90-alerting.sh:233`
- `automation/validation/pipeline_duplicate_check.py`, `automation/validation/tests/` inventory, `automation/validation/{alert_canary.sh,alert_delivery_test.sh,alert_storm_test.sh}`
- `mct/scripts/shuffle-webhook-smoke-test.sh`, `mct/integrations/opensearch-alerting/shuffle-webhook-wiring.md`
- Live (read-only): `/srv/falcon/textfile/falcon_relay.prom`, `/srv/falcon/textfile/falcon_metrics.prom`, docker ps, Prometheus `query_range` (sink counters), aggregator logs.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `falcon_relay.prom` | live read-only | Delivery accounting | lab 468 success/0 fail; alt 467 success/1 fail; last success fresh |
| Relay spool dir | live read-only | Failed-delivery capture | absent -> no failed deliveries since last cleanup (spool is created on failure) |
| `docker ps` | live read-only | Shuffle path status | no Shuffle containers (retired); decision log 2026-09-27 |
| Prometheus `query_range` sink counters | live read-only | Outbound delivery health | `sink_sent` flat ~38 h during the outage; `sink_errors`/`sink_discarded` stayed 0 |
| Aggregator logs | live read-only | Failure mode | `Not retriable; dropping the request`; `component_events_dropped` counts |
| Vector metrics endpoint | live read-only | Counter lifecycle | only `vector_component_discarded_events_total{component_id="edge_ingest",component_kind="source"}` materialized |
| Tests inventory (51 suites) | static | Replay/idempotency evidence | no replay/duplicate/idempotency test for the relay/ntfy path |

### Prior-run reconciliation (run falcon-20261005-full-main-e267ce1)

- **WH-P3-001 (no replay/idempotency evidence for Shuffle and ntfy paths)** — prior status `open`. Current: the Shuffle path is retired (no live containers; Wazuh->Shuffle integration disabled 2026-09-27; the vendored smoke script remains dry-run default), while the ntfy/relay path still has no signature/timestamp/nonce and no replay/duplicate tests; the replay residual is documented in `ntfy_relay.py:22-34` and `NOTIFICATION_AND_DEADMAN.md` section 4. **Still open for the ntfy path; kept with the prior ID.**
- New at this commit: the sink-failure DLQ/visibility gap below (WH-P1-001) is reported here because it is the outbound-delivery contract; the data-loss incident itself is DATA-P0-001.

## Executive Summary

The notification path is well controlled for an accepted-residual design: fail-closed token auth with constant-time compare, per-source rate limit, honest 2xx/502 answers so Grafana retries, a bounded replay spool, dual delivery domains, per-path metrics and a matched dead-man contract (heartbeat hourly vs watcher 7200 s threshold, asserted offline by `deadman_contract_test.sh`). Replay protection is absent by design (Grafana cannot sign), documented, and no replay/duplicate test exists for it (WH-P3-001).

The serious gap is on the telemetry delivery path: the OpenSearch sink has no dead-letter path and its failure counters did not register during the 40-hour outage — `falcon_pipeline_sink_errors_total` and `falcon_pipeline_sink_discarded_events_total` stayed 0 in Prometheus while the sink sent nothing and the aggregator logged dropped batches. The alert that depends on those counters (`bootstrap/90-alerting.sh:233`) could not fire; detection depended on freshness.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Inbound webhook | `ntfy_relay.py:380-436` | Grafana -> readable ntfy | token path + rate limit + spool | Low | replay residual |
| Inbound ingest | `aggregator.yaml:18-28` | Edge telemetry | basic auth | Medium | API-P2-001 |
| Outbound ntfy lab | `ntfy_relay.py:250-289` | Primary notify | 2 attempts, no backoff | Low | - |
| Outbound ntfy alt | `ntfy_relay.py:233-247` | Independent domain | 1 attempt, best effort | Low | - |
| Dead-man | `heartbeat.sh`, `do_watcher/watch.sh` | Liveness | hourly vs 7200 s, contract-tested | Low | owner-side deploy |
| Outbound OpenSearch | `aggregator.yaml:116-131` | Telemetry delivery | no DLQ; non-retriable drops | High | WH-P1-001 |
| DLQ | `aggregator.yaml:133-138` | Validation rejects | file, 30 d/64 MiB via disk guard | Low | sink failures not included |
| Duplicate measurement | `pipeline_duplicate_check.py` | At-least-once replay | measured (DQ-P2-002) | Low | no dedup |
| Shuffle | `mct/scripts/shuffle-webhook-smoke-test.sh` | Retired webhook | dry-run default | Low | not live |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Inbound endpoints | 3 | relay auth + rate limit | no signature | accepted residual |
| Outbound delivery | 2 | ntfy good; sink drops | no DLQ, counters blind | WH-P1-001 |
| Event models | 3 | Grafana payload rendered | - | - |
| Signature verification | 1 | token path only | no HMAC (not implementable with Grafana) | accepted |
| Timestamp tolerance | 0 | none | replay window unbounded | accepted residual |
| Replay nonce | 0 | none | replay within rate budget | accepted residual |
| Idempotency keys | 1 | none on webhooks; duplicate measured on ingest | no dedup | optional |
| Retry backoff | 2 | vector 10/300 s; relay no backoff | relay retries immediate | low |
| Dead-letter queues | 2 | vector validation DLQ + relay spool | sink failures dropped | WH-P1-001 |
| Secrets | 3 | root-owned, rotation docs | - | - |
| Tenant scoping | 2 | single tenant | n/a | - |
| Payload schema/size | 3 | JSON parse, rendered subsets | no explicit size cap | low |

## Detailed Review

### Item: Relay (Grafana -> ntfy)

- Evidence: `ntfy_relay.py:22-34,250-289,351-436`; `NOTIFICATION_AND_DEADMAN.md`.
- Current controls: secret path token (constant-time, fail-closed), per-source rate limit before auth, JSON parse errors -> 400, total failure -> 502 + bounded spool (100, manual replay), per-path metrics.
- Missing controls: no timestamp/nonce/signature (documented, not implementable with Grafana); no automated spool replay; no replay test.
- Risks: a captured valid POST can re-publish within the rate budget (documented residual).

### Item: Telemetry sink delivery (aggregator -> OpenSearch)

- Evidence: `aggregator.yaml:116-138`; `export_monitor_metrics.sh:60-77,487-489`; `bootstrap/90-alerting.sh:233`; live logs/metrics.
- Current controls: bulk API with TLS + least-privilege writer; Vector default retries; validation DLQ upstream.
- Missing controls: non-retriable responses drop batches with no dead-letter capture; the sink error/discard counters did not materialize during the outage (only the source counter exists), so the write-failure alert could not fire; recovery depends on the bounded edge buffer.
- Risks: silent telemetry loss (materialized 2026-10-07/09 — DATA-P0-001).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| WH-001 | Inbound endpoints | relay | token + rate limit | no signature | P3 | accepted residual |
| WH-002 | Outbound delivery | sink | retries | no DLQ | P1 | WH-P1-001 |
| WH-003 | Event models | relay render | bounded subsets | - | - | - |
| WH-004 | Signature verification | relay | token only | no HMAC | P3 | accepted |
| WH-005 | Timestamp tolerance | none | - | replay window | P3 | accepted |
| WH-006 | Replay nonce | none | - | replay | P3 | accepted |
| WH-007 | Idempotency keys | none/measured | duplicate ratio metric | no dedup | P3 | optional |
| WH-008 | Retry backoff | vector/relay | 10/300 s; 2 immediate | relay no backoff | P3 | minor |
| WH-009 | Dead-letter queues | DLQ/spool | validation + relay | sink failures | P1 | WH-P1-001 |
| WH-010 | Secrets | files | root-owned + rotation | - | - | - |
| WH-011 | Tenant scoping | single tenant | n/a | - | - | - |
| WH-012 | Payload schema/size | relay/vector | JSON parse | no size cap | P3 | minor |

## Findings

### WH-P3-001 - No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired

- Severity: P3
- Confidence: High
- Area: WH
- Evidence:
  - `automation/alerting/ntfy_relay.py:22-34` (HMAC/timestamp replay assessed not implementable with Grafana; replay residual documented).
  - `docs/runbooks/NOTIFICATION_AND_DEADMAN.md` section 4 (accepted controls: token, rate limit, rotation; replay residual).
  - `automation/validation/tests/` inventory (51 suites): `ntfy_relay_auth_test.py` covers auth; no replay/duplicate/idempotency test for the relay/ntfy path.
  - Live `docker ps`: no Shuffle containers; `ledgers/decision_log.md:136` (2026-09-27: Wazuh->Shuffle integration disabled, shuffle-backend retired).
  - `mct/scripts/shuffle-webhook-smoke-test.sh` (dry-run default; smoke only).
- What is happening: the ntfy/relay path has no signature, timestamp tolerance, nonce or idempotency key; a captured valid POST can re-publish an alert within the rate budget. Shuffle is no longer a live webhook path.
- Why it matters: the residual is documented and bounded (bridge-only listener, token rotation), but there is no regression test proving duplicate delivery behavior, and the prior finding covered two paths of which one is now retired.
- Recommended fix: add a duplicate-delivery test for the relay (same payload twice within/over the rate window; assert documented behavior) and either add an optional `X-Message` idempotency id for ntfy or explicitly re-record the accepted residual; drop/archive the Shuffle webhook test from the live inventory.
- Suggested validation: test asserts 2xx + two publishes (documented) or dedup if implemented.
- Owner suggestion: notifications owner
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior ID WH-P3-001; Shuffle half N/A)
- Endpoint / data path: POST `http://<bridge-gw>:9099/grafana/<token>` -> lab/alt ntfy
- Attack path: none identified (bridge-scoped)

### WH-P1-001 - OpenSearch sink drops failed batches with no dead-letter path and the failure counters stayed 0 through a 40-hour outage

- Severity: P1
- Confidence: High (live metrics + logs at audit time)
- Area: WH
- Evidence:
  - `config/vector/aggregator.yaml:116-131` (sink, no buffer/DLQ), `:133-138` (DLQ sink consumes only `route_valid.invalid`).
  - `automation/validation/export_monitor_metrics.sh:60-77` (sink_errors/sink_discarded from `vector_component_*{component_id="opensearch",component_kind="sink"}`), `:487-489` (export).
  - `bootstrap/90-alerting.sh:233` (falcon-pipeline-sink-write-failures rule uses `increase(...errors/discarded) > bool 0`).
  - Live Prometheus: `falcon_pipeline_sink_errors_total` = 0 and `falcon_pipeline_sink_discarded_events_total` = 0 across 2026-10-07..10-09 while `falcon_pipeline_sink_sent_events_total` was flat for ~38 h.
  - Live aggregator logs 2026-10-08: `Not retriable; dropping the request` and `component_events_dropped ... count=62/1227/13310`.
  - Live vector metrics endpoint: only `vector_component_discarded_events_total{component_id="edge_ingest",component_kind="source"}` materialized (379,476 at audit time); no sink series.
- What is happening: a write rejection (e.g., `unavailable_shards_exception`) is classified non-retriable and the batch is discarded with no DLQ/replay; the counters the alert depends on did not increment (the sink series did not materialize), so the failure was invisible to the write-failure rule and was only visible via freshness/e2e.
- Why it matters: retries require idempotency and failures must be visible and recoverable; here a delivery failure becomes permanent, silent data loss.
- User / business impact: lost telemetry during outages (materialized as DATA-P0-001).
- Security / privacy / reliability impact: reliability/forensics; no direct security exposure.
- Recommended fix: route sink failures to a DLQ (Vector cannot do this natively for the elasticsearch sink — add a proxy/sidecar or a scheduled replay of a failure journal), and fix or replace the sink failure counters with a source that provably increments (e.g., scrape `vector_component_discarded_events_total` without the component filter and export the sink series, or count via the failure journal); add a firing proof that a forced 503 drops zero events unaccounted.
- Suggested validation: forced-rejection test: assert the DLQ/journal captures every batch and the alert fires.
- Owner suggestion: ops/platform
- Effort estimate: M
- Dependencies: Vector behavior; capacity fixes (DATA-P0-001)
- Status: open (new)
- Endpoint / data path: aggregator sink -> `https://opensearch:9200` bulk `falcon-eve-%Y.%m.%d`
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent sink delivery loss | P1 | High (occurred) | Telemetry gaps | WH-P1-001 | DLQ + counters |
| Alert cannot fire on sink drops | P1 | High | Blind failure | WH-P1-001 | fix metric source + firing proof |
| Webhook replay within rate budget | P3 | Low | Duplicate alerts | WH-P3-001 | accepted residual + test |

## Recommendations

### Immediate / Release Blocking
1. WH-P1-001: make sink failures visible and recoverable (DLQ/journal + working counters + firing proof).

### This Week
2. Add the relay duplicate-delivery test; re-record the replay residual (WH-P3-001).

### This Month
3. Optional `X-Message` idempotency id on ntfy publishes.

### Later / Platform Evolution
4. If Grafana ever supports signed webhooks, implement HMAC + timestamp.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Remove the component filter from the discard metric | Makes the real counter visible | `export_monitor_metrics.sh` | forced 503 -> metric > 0 |
| Archive the Shuffle smoke script as retired | Avoids false coverage | `mct/scripts/` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Sink failure journal + replay | P1 | ops | M | Vector |
| Relay duplicate test | P3 | notifications | S | - |
| ntfy X-Message idempotency | P3 | notifications | S | ntfy version |

## Suggested Tests

- Forced OpenSearch 503: assert the sink failure is captured (DLQ/journal) and the alert fires.
- Relay duplicate POST: assert documented behavior and rate-limit interaction.
- Dead-man contract (already present, keep green).

## Suggested Documentation Updates

- `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`: note Shuffle retirement in the delivery inventory.
- `docs/runbooks/SCHEMA_AND_RETENTION.md`: state explicitly that the Vector DLQ does not capture sink failures.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why did the sink discarded/errors counters not materialize? | Fix target | Vector 0.58 behavior / metric scrape |
| Should the relay spool be replayed automatically? | Recovery gap | owner decision |

## Appendix

- Relay metrics at audit time: lab 468/0, alt 467/1 (success/failures), publish_failures 0, last success fresh.
- Sink counters at audit time: received 385,704; sent 360,312; errors 0; discarded 0; buffer 1000.
- Dead-man contract: heartbeat hourly; watcher MAX_AGE 7200 s (1x < t <= 2x); dual-domain publish asserted by `deadman_contract_test.sh`.

## Findings

| ID | Severity | Title |
|---|---|---|
| WH-P3-001 | P3 | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired |
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter path and the failure counters stayed 0 through a 40-hour outage |
