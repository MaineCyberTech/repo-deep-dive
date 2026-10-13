# 27_webhook_delivery_replay_idempotency_audit — Prompt 27 - Webhook Delivery, Replay, and Idempotency Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `27_webhook_delivery_replay_idempotency_audit.md` (area WH, prompt)

## Verification Performed

# Webhook Delivery, Replay, and Idempotency Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-f5cb7c9`
- Branch: main (detached worktree at the audited commit; live tree `/home/user/falcon-build` HEAD == f5cb7c9, clean)
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:33:09Z
- Auditor: subagent (read-only; live checks read-only)
- Area code: WH
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/27_webhook_delivery_replay_idempotency_audit.md
- Scope limitations: Shuffle is retired live (no containers); only its vendored scripts were reviewed. The DO-side watcher is owner-side (repo-versioned config verified; live run state from the verification run's evidence). The edge control-plane spool is an ingest buffer, not a webhook; its ongoing purge is reported under DATA-P2-003.

## Scope

Reviewed inbound webhook endpoints (Grafana -> relay), outbound notification delivery (relay -> lab/alt ntfy, heartbeat, dead-man watcher), the Vector delivery path to OpenSearch (retries, buffering, DLQ), event models, signature/timestamp/replay controls, idempotency keys, retry/backoff, dead-letter handling, secrets, tenant scoping, payload handling, timeouts, delivery logs, admin management/rotation, and the webhook test inventory. Live read-only checks: relay metrics, sink metrics, aggregator drop counters, container state.

## Evidence Reviewed

- `automation/alerting/ntfy_relay.py` (auth, rate limit, publish, spool, metrics), `automation/alerting/do_watcher/{watch.sh,install.sh}`, `automation/validation/heartbeat.sh`
- `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`, `docs/architecture/PORT_PROTOCOL_MATRIX.md:38` (N-21)
- `config/vector/{edge.yaml,aggregator.yaml}`, `automation/validation/export_monitor_metrics.sh` (new drop metrics), `bootstrap/90-alerting.sh:243-248,611-613`
- `automation/validation/pipeline_duplicate_check.py`, `automation/validation/tests/` inventory (51 suites), `automation/validation/write_rejection_test.sh`
- `mct/scripts/shuffle-webhook-smoke-test.sh` (retired path)
- Live (read-only): `/srv/falcon/textfile/falcon_relay.prom`, `falcon_metrics.prom` (sink + drop metrics), `falcon_pipeline_e2e.prom`, live Grafana rules API, `docker ps`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `falcon_relay.prom` | live read-only | Delivery accounting | lab 9 success/0 fail; alt 9/0; last success 2026-10-11T04:21Z; publish_failures 0 |
| `falcon_metrics.prom` sink counters | live read-only | Outbound delivery health | received == sent (1,643,152); errors 0; discarded 0; buffer 0 |
| `falcon_pipeline_aggregator_drop_logs_15m` | live read-only | New drop detection | 0 (healthy) |
| `falcon_pipeline_all_discarded_events_total` / `all_errors_total` | live read-only | New component-wide counters | 0 / 0 |
| Live Grafana rules API | live read-only | Alert provisioning | 86 rules incl. "Pipeline drops detected (Vector log)" (critical), "Pipeline discarded/error events (counters)", "Edge spool purge burst", "Wazuh VPN proxy listener down", "Wazuh indexer backup stale" |
| `falcon_pipeline_e2e.prom` | live read-only | End-to-end delivery proof | last success 2026-10-11T04:30Z; last failure 2026-10-09T18:00Z; inject/landed steps 1 |
| Tests inventory (51 suites) | static | Replay/idempotency evidence | `ntfy_relay_auth_test.py` covers auth; no duplicate/replay test for the relay/ntfy path |
| `write_rejection_test.sh` (read-only review; not run) | static | Sink failure drill | counts DLQ lines but the DLQ only consumes validation rejects; sink failures are not captured |

### Prior-run reconciliation (run falcon-20261009-2117-full-08e20d1; verification run falcon-20261011-0400-verify-main-584e1a3)

- **WH-P1-001 (OpenSearch sink drops failed batches with no dead-letter path; counters stayed 0 through the outage)** — prior status `partially-fixed` (detection closed; DLQ residual). Current: **detection half verified live** (log-derived counter exported and two rules provisioned; live values 0 = healthy; a forced-rejection drill exists). **Residual open**: the sink still has no dead-letter/replay path (`aggregator.yaml:133-135` consumes only `route_valid.invalid`), and the new counters only observe — they do not capture the dropped batch for replay. Kept with the prior ID.
- **WH-P3-001 (no replay/idempotency protection or tests on the notification path; Shuffle retired)** — prior status `still-open`. Current: unchanged for the ntfy/relay path (no signature/timestamp/nonce, documented residual; no duplicate-delivery test); the Shuffle path remains retired. Kept with the prior ID.
- New in this run: the edge control-plane spool continues to purge ~134 MiB per 10-14 h (four events since the prior audit) and the `falcon-edge-spool-purge-burst` threshold (256 MiB/6 h) cannot fire at that rate — reported as DATA-P2-003 (data lifecycle), cross-referenced here because it is the telemetry-delivery boundary.

## Executive Summary

The notification path is well controlled for an accepted-residual design: fail-closed token auth with constant-time compare, per-source rate limit, honest 2xx/502 answers so Grafana retries, a bounded replay spool (100 entries, manual replay), dual delivery domains, per-path metrics, and a matched dead-man contract (hourly heartbeat vs 7200 s threshold; the watcher now reads the independent topic locally on the DO, removing the dependency on the lab being reachable). Live counters are clean (9/9 per path, 0 failures).

The serious gap remains on the telemetry delivery path: the OpenSearch sink has no dead-letter/replay path — a non-retriable write rejection still destroys the batch. The detection half of the prior finding is now genuinely fixed and live-verified: the exporter publishes `falcon_pipeline_aggregator_drop_logs_15m` (log-derived) plus all-component discard/error sums, and two Grafana rules are provisioned; a `write_rejection_test.sh` drill exists. Replay/idempotency on the ntfy path is still untested (documented residual).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Inbound webhook | `ntfy_relay.py:380-436` | Grafana -> readable ntfy | token path + rate limit + spool | Low | replay residual |
| Inbound ingest | `aggregator.yaml:18-28` | Edge telemetry | basic auth | Medium | API-P2-001 |
| Outbound ntfy lab | `ntfy_relay.py:250-289` | Primary notify | 2 attempts, no backoff | Low | - |
| Outbound ntfy alt | `ntfy_relay.py:233-247` | Independent domain | 1 attempt, best effort | Low | - |
| Dead-man | `heartbeat.sh`, `do_watcher/watch.sh` | Liveness | hourly vs 7200 s; watcher reads the alt topic locally | Low | repo-versioned; owner-side deploy |
| Outbound OpenSearch | `aggregator.yaml:117-131` | Telemetry delivery | no DLQ; non-retriable drops | High | WH-P1-001 residual |
| DLQ | `aggregator.yaml:133-135` | Validation rejects | file, 30 d/64 MiB via disk guard | Low | sink failures not included |
| Drop visibility | `export_monitor_metrics.sh:78-88,505-515` | Failure detection | log counter + all-component sums live | Low | WH-P1-001 detection closed |
| Duplicate measurement | `pipeline_duplicate_check.py` | At-least-once replay | measured (live 0.0000) | Low | no dedup |
| Shuffle | `mct/scripts/shuffle-webhook-smoke-test.sh` | Retired webhook | dry-run default | Low | not live |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Inbound endpoints | 3 | relay auth + rate limit | no signature | accepted residual |
| Outbound delivery | 2 | ntfy good; sink drops | no DLQ/replay | WH-P1-001 |
| Event models | 3 | Grafana payload rendered | - | - |
| Signature verification | 1 | token path only | no HMAC (not implementable with Grafana) | accepted |
| Timestamp tolerance | 0 | none | replay window unbounded | accepted residual |
| Replay nonce | 0 | none | replay within rate budget | accepted residual |
| Idempotency keys | 1 | none on webhooks; duplicate measured on ingest | no dedup | optional |
| Retry backoff | 2 | vector 10/300 s; relay no backoff | relay retries immediate | low |
| Dead-letter queues | 2 | validation DLQ + relay spool + working drop detection | sink failures dropped, no replay | WH-P1-001 |
| Secrets | 3 | root-owned, rotation docs | - | - |
| Tenant scoping | 2 | single tenant | n/a | - |
| Payload schema/size | 3 | JSON parse, rendered subsets | no explicit size cap | low |

## Detailed Review

### Item: Relay (Grafana -> ntfy)

- Evidence: `ntfy_relay.py:22-34,250-289,351-436`; `NOTIFICATION_AND_DEADMAN.md`.
- Current controls: secret path token (constant-time, fail-closed), per-source rate limit before auth, JSON parse errors -> 400, total failure -> 502 + bounded spool (100, manual replay), per-path metrics.
- Missing controls: no timestamp/nonce/signature (documented, not implementable with Grafana); no automated spool replay; no replay/duplicate test.
- Risks: a captured valid POST can re-publish within the rate budget (documented residual).

### Item: Telemetry sink delivery (aggregator -> OpenSearch)

- Evidence: `aggregator.yaml:117-138`; `export_monitor_metrics.sh:78-88,505-515`; `bootstrap/90-alerting.sh:243-248`; live metrics.
- Current controls: bulk API with TLS + least-privilege writer; Vector default retries; validation DLQ upstream; log-derived drop counter + all-component discard/error sums; two provisioned rules; end-to-end assertion every 15 min (last success fresh).
- Missing controls: non-retriable responses still drop batches with no dead-letter capture/replay (Vector's elasticsearch sink has no failure DLQ); the drill counts DLQ lines but sink failures never reach it.
- Risks: silent telemetry loss on write rejection (materialized 2026-10-07/09 — DATA-P0-001, now closed with detection live).

### Item: Dead-man / watcher

- Evidence: `automation/alerting/do_watcher/watch.sh` (2026-10-09 change: reads the independent topic locally on the DO; no dependency on the lab being reachable), `heartbeat.sh`, `NOTIFICATION_AND_DEADMAN.md`.
- Current controls: hourly heartbeat; watcher threshold 7200 s (1x < t <= 2x); dual-domain publish; watcher staleness rule live (`falcon-watcher-stale`, 1 h, critical).
- Risks: low; owner-side deployment.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| WH-001 | Inbound endpoints | relay | token + rate limit | no signature | P3 | accepted residual |
| WH-002 | Outbound delivery | sink | retries + detection | no DLQ/replay | P1 | WH-P1-001 |
| WH-003 | Event models | relay render | bounded subsets | - | - | - |
| WH-004 | Signature verification | relay | token only | no HMAC | P3 | accepted |
| WH-005 | Timestamp tolerance | none | - | replay window | P3 | accepted |
| WH-006 | Replay nonce | none | - | replay | P3 | accepted |
| WH-007 | Idempotency keys | none/measured | duplicate ratio metric | no dedup | P3 | optional |
| WH-008 | Retry backoff | vector/relay | 10/300 s; 2 immediate | relay no backoff | P3 | minor |
| WH-009 | Dead-letter queues | DLQ/spool | validation + relay + detection | sink failures | P1 | WH-P1-001 |
| WH-010 | Secrets | files | root-owned + rotation | - | - | - |
| WH-011 | Tenant scoping | single tenant | n/a | - | - | - |
| WH-012 | Payload schema/size | relay/vector | JSON parse | no size cap | P3 | minor |
| WH-013 | Drop detection | exporter + rules | live, values 0 | - | - | keep firing proofs |

## Findings

### WH-P1-001 - OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified)

- Severity: P1
- Confidence: High (live metrics + rules + code)
- Area: WH
- Evidence:
  - `config/vector/aggregator.yaml:117-131` (sink; no buffer/DLQ), `:133-135` (DLQ sink consumes only `route_valid.invalid`).
  - `automation/validation/export_monitor_metrics.sh:78-88` (new all-component discard/error sums + `falcon_pipeline_aggregator_drop_logs_15m` from the aggregator's "dropping the request"/"Not retriable" lines), `:505-515` (export).
  - `bootstrap/90-alerting.sh:243-248` ("Pipeline drops detected (Vector log)" critical; "Pipeline discarded/error events (counters)" warning) — both live in Grafana (86-rule set).
  - Live `falcon_metrics.prom`: `falcon_pipeline_aggregator_drop_logs_15m 0`, `falcon_pipeline_all_discarded_events_total 0`, `falcon_pipeline_all_errors_total 0`, sink received == sent (1,643,152), errors 0, discarded 0.
  - `automation/validation/write_rejection_test.sh` (drill lowers the flood watermark, observes rejection/recovery and counts DLQ lines) — reviewed, not run (mutating).
- What is happening: a write rejection (e.g. `unavailable_shards_exception`) is still classified non-retriable and the batch is discarded with no DLQ/replay; the new counters/rules make the drop visible within 5 minutes but do not preserve the data.
- Why it matters: retries require idempotency and failures must be recoverable; here a delivery failure is still permanent loss, now at least observable.
- User / business impact: lost telemetry during outages (the 2026-10-07/09 instance is recorded as DATA-P0-001, closed).
- Security / privacy / reliability impact: reliability/forensics; no direct security exposure.
- Recommended fix: route sink failures to a durable failure journal (proxy/sidecar or a scheduled replay of a failure journal; Vector's elasticsearch sink cannot DLQ natively) and prove with a forced-rejection drill that every batch is captured and replayable; keep the new counters/rules as the detection layer.
- Suggested validation: forced-rejection test: assert the journal captures every batch and the alert fires; replay restores the events with no duplicates.
- Owner suggestion: ops/platform
- Effort estimate: M
- Dependencies: Vector behavior; capacity fixes
- Status: partially-fixed (prior ID WH-P1-001; detection verified-fixed live, replay/DLQ residual open)
- Endpoint / data path: aggregator sink -> `https://opensearch:9200` bulk `falcon-eve-%Y.%m.%d`
- Attack path: none identified

### WH-P3-001 - No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired

- Severity: P3
- Confidence: High
- Area: WH
- Evidence:
  - `automation/alerting/ntfy_relay.py:22-34` (HMAC/timestamp replay assessed not implementable with Grafana; replay residual documented).
  - `docs/runbooks/NOTIFICATION_AND_DEADMAN.md` section 4 (accepted controls: token, rate limit, rotation; replay residual).
  - `automation/validation/tests/` inventory (51 suites): `ntfy_relay_auth_test.py` covers auth; no replay/duplicate/idempotency test for the relay/ntfy path.
  - `ledgers/decision_log.md` 2026-09-27 (Wazuh->Shuffle integration disabled; shuffle-backend retired); live `docker ps` has no Shuffle containers; `mct/scripts/shuffle-webhook-smoke-test.sh` is dry-run default.
- What is happening: the ntfy/relay path has no signature, timestamp tolerance, nonce or idempotency key; a captured valid POST can re-publish an alert within the rate budget (120 POSTs/60 s per source).
- Why it matters: the residual is documented and bounded (bridge-only listener, token rotation), but there is no regression test proving duplicate-delivery behavior, and the prior finding covered a path (Shuffle) that is now retired.
- Recommended fix: add a duplicate-delivery test for the relay (same payload twice within/over the rate window; assert the documented behavior) and either add an optional `X-Message` idempotency id for ntfy or explicitly re-record the accepted residual; archive the Shuffle smoke script as retired.
- Suggested validation: test asserts 2xx + two publishes (documented) or dedup if implemented.
- Owner suggestion: notifications owner
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior ID WH-P3-001; Shuffle half N/A)
- Endpoint / data path: POST `http://<bridge-gw>:9099/grafana/<token>` -> lab/alt ntfy
- Attack path: none identified (bridge-scoped)

### Cross-domain observation (not re-raised as a WH finding): edge spool purges continue

- Evidence: `falcon_edge_spool_purged_bytes_total` 1,743,575,365 (2026-10-09T13:30Z) -> 2,146,154,182 now (+402 MB / 4 overwrites); `removed_files_total=0`; `falcon-edge-spool-purge-burst` threshold 256 MiB/6 h cannot fire at the observed rate.
- Disposition: reported as DATA-P2-003 (data lifecycle) because the spool is the edge control plane's ingest buffer rather than a webhook; the notification path itself is healthy.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent sink delivery loss (no replay) | P1 | Medium (detection now live) | Telemetry gaps | WH-P1-001 | failure journal + replay |
| Webhook replay within rate budget | P3 | Low | Duplicate alerts | WH-P3-001 | accepted residual + test |
| Continuous edge spool destruction | P2 | Certain | Telemetry loss | DATA-P2-003 | see DATA domain |

## Recommendations

### Immediate / Release Blocking
1. WH-P1-001: add the sink-failure journal + replay path (detection is done; recovery is not).

### This Week
2. Add the relay duplicate-delivery test; re-record the replay residual (WH-P3-001).

### This Month
3. Optional `X-Message` idempotency id on ntfy publishes.

### Later / Platform Evolution
4. If Grafana ever supports signed webhooks, implement HMAC + timestamp.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Relay duplicate test | Proves documented behavior | `automation/validation/tests/` | test passes |
| Archive the Shuffle smoke script | Avoids false coverage | `mct/scripts/` | review |
| Keep the new firing proofs updated | Evidence discipline | `docs/phase9/ALERT_FIRING_PROOFS.md` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Sink failure journal + replay | P1 | ops | M | Vector |
| Relay duplicate test | P3 | notifications | S | - |
| ntfy X-Message idempotency | P3 | notifications | S | ntfy version |

## Suggested Tests

- Forced OpenSearch 503: assert the sink failure is captured (journal) and the alert fires; replay restores events.
- Relay duplicate POST: assert documented behavior and rate-limit interaction.
- Dead-man contract (already present, keep green).

## Suggested Documentation Updates

- `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`: note Shuffle retirement in the delivery inventory (already partially updated 2026-10-09); record the drop-detection closure.
- `docs/runbooks/SCHEMA_AND_RETENTION.md`: state explicitly that the Vector DLQ does not capture sink failures (already stated) and add the failure-journal plan when implemented.
- `docs/phase9/ALERT_FIRING_PROOFS.md`: add the two new drop rules if not yet recorded.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Where should the sink failure journal live (proxy vs sidecar)? | Fix design | ops decision |
| Should the relay spool be replayed automatically? | Recovery gap | owner decision |

## Appendix

- Relay metrics at audit time: lab 9/0, alt 9/0 (success/failures), publish_failures 0, last success 2026-10-11T04:21:26Z.
- Sink counters at audit time: received 1,643,152; sent 1,643,152; errors 0; discarded 0; buffer 0.
- New drop metrics: `falcon_pipeline_aggregator_drop_logs_15m 0`; `all_discarded 0`; `all_errors 0`.
- Dead-man contract: heartbeat hourly; watcher MAX_AGE 7200 s; watcher reads the independent topic locally (2026-10-09 change).
- Live Grafana: 86 rules including the drop/discard/spool/wazuh-listener/indexer-backup rules.

## Findings

| ID | Severity | Title |
|---|---|---|
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified) |
| WH-P3-001 | P3 | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired |
