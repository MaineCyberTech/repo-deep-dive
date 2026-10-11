# 13_resilience_recovery_failure_modes — Prompt 13 - Resilience, Recovery, and Failure Modes Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `13_resilience_recovery_failure_modes.md` (area RES, prompt)

## Verification Performed

# Resilience, Recovery, and Failure Modes Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` @ `08e20d1` (branch `main`)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-09T21:55Z
- Auditor: subagent (RES)
- Area code: RES
- Scope limitation: read-only; no restarts, no failure injection performed during this audit; live counters were sampled while the host was under active incident pressure.

## Scope

Reviewed timeout/retry/idempotency/queue-DLQ/webhook/worker/graceful-shutdown behavior in the repository at `08e20d1`, and verified runtime behavior read-only on the live lab host: systemd units/timers, container restart policies and memory limits, kernel OOM records, Vector internal metrics, the probe disk buffer, backup/offsite state, and the alert relay journal. Not reviewed: application-level client code (this repo is infrastructure-only), Kubernetes-style circuit breakers (not present by design), and mutating recovery actions (never run).

## Evidence Reviewed

- `compose/central/docker-compose.yml`, `compose/probe/docker-compose.yml` (restart policies, memory limits, healthchecks)
- `config/vector/aggregator.yaml`, `config/vector/edge.yaml` (buffers, retries, DLQ, timeouts)
- `bootstrap/80-offsite-backup.sh` (retry/backoff, dead-letter marker, fail-closed prune, upload-state delta)
- `bootstrap/85-backup-job.sh`, `config/systemd/falcon-backup.{service,timer}` (snapshot job, abort markers)
- `automation/validation/lib/abort.sh`, `restore_rehearsal.sh`, `central_recovery_test.sh`, `boot_order_check.sh`, `upgrade_rollback_rehearsal.sh`, `index_rename_rollback_drill.sh`
- Live: `journalctl -k` (OOM), `journalctl -u falcon-backup.service`, `journalctl -u falcon-alert-relay.service`, `docker inspect`, Prometheus queries, `free -m`, `uptime`, `systemctl list-timers`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `journalctl -k --since 2026-10-02 \| grep 'Killed process'` | Live | Memory-failure mode | 23 kills, all `vector` (5 on Oct 8, 18 on Oct 9) |
| `docker inspect falcon-central-vector-aggregator-1` | Live | Limit/restarts | `Memory=536870912`, `RestartCount=23`, started 21:19:13Z |
| `vector_component_discarded_events_total{component_id="edge_ingest"}` | Live | Actual event loss | 677,475 in the current instance; 1.5M+ in the prior instance |
| `falcon_probe_buffer_bytes` range 8 h | Live | Backpressure depth | 1,940–2,042 MiB (cap 2,048 MiB) from 13:47–20:47Z |
| `journalctl -u falcon-backup.service` | Live | Worker recovery | Snapshot failures Oct 3/8/9 with no retry; success Oct 7 + manual Oct 9 |
| `journalctl -u falcon-alert-relay.service` | Live | Detection/delivery | All incidents delivered on both paths; noise counts recorded |
| `free -m`, `uptime` | Live | Headroom | 2.3 GiB available, 4.5/8 GiB swap, load 24.6 |
| `automation/validation/tests/*.sh` + evidence index | Repo | Drill coverage | Sink-drop, disk, silence, storm drills exist; no OOM drill |

## Executive Summary

The repository contains genuinely strong failure-mode engineering for the pipeline and backup path: abort markers on signals, bounded retry with exponential backoff and a persistent dead-letter marker for offsite backups, fail-closed remote pruning, upload-state deltas, an idempotent snapshot reuse contract, a 2 GiB disk buffer at the edge, `restart: unless-stopped` on all containers, and a dead-man contract test tying the hourly heartbeat to the off-host watcher threshold. The offsite verification (all 1,684 OpenSearch + 8,450 Wazuh objects size-checked nightly) is a real, exercised control.

However, the live host is currently operating past its memory envelope, and the failure mode that matters is happening: the central Vector aggregator runs under a 512 MiB cgroup limit and was OOM-killed 23 times on Oct 8–9, dropping hundreds of thousands to ~1.5 million in-flight events per window while the probe disk buffer sat pinned at its 2 GiB cap for ~7 hours. No alert fires on the source-side drop metric, so the loss is invisible to the alerting that is supposed to cover the pipeline. The nightly backup worker failed 3 times in 7 days (Oct 3/8/9) with a single snapshot attempt, no unit-level retry and no immediate failure signal; recovery depended on an operator noticing a 36-hour-late "Backup stale" alert. The host itself has ~18.5% memory available with 4.5 GiB swap in use.

Recommended next actions: (1) right-size the aggregator memory limit and add a memory/restart + source-drop alert; (2) give the backup worker bounded retry and an immediate failure alert, and log the OpenSearch response; (3) restore host memory headroom before the next ingest spike.

## Findings Summary

| # | Severity | Title | Status |
|---|---|---|---|
| 1 | P1 | Vector aggregator OOM crash-loop drops security telemetry | open |
| 2 | P2 | Host memory headroom exhausted | open |
| 3 | P3 | No failure-injection coverage for aggregator OOM/memory exhaustion | open |

## Detailed Findings

### 1. Vector aggregator OOM crash-loop drops security telemetry (P1)

The aggregator is capped at 512 MiB (`compose/central/docker-compose.yml:149-152`). Kernel OOM records show 23 kills of `vector` since Oct 2 (5 on Oct 8, 18 on Oct 9; `RestartCount=23` at 21:19:13Z). Each restart interrupts in-flight ingest; the container logs report `component_events_dropped ... count=1,240–11,574 reason="Source send interrupted mid-flight; pipeline may be overloaded or shutting down"`, and the source-side counter reached 677,475 dropped events in the current instance and 1.5M+ in the previous one. The probe disk buffer (`when_full: block`, 2 GiB) absorbed the backpressure but was pinned at 2,042 MiB at 19:02Z for ~7 hours, so UDP syslog on the edge was at risk of kernel-buffer loss. This is an active data-loss/telemetry-integrity condition, not a theoretical gap.

**Fix:** raise/right-size the aggregator memory limit for the observed rate (or reduce batch/memory use), add an alert on container restarts/OOM for the aggregator, export and alert the source-side discarded counter, and re-run the sink-drop drill against the source path. **Validation:** bounded drill forcing an OOM with a synthetic burst; assert the drop metric, the new alert firing, and buffer drain after recovery.

### 2. Host memory headroom exhausted (P2)

At 21:23Z the host had 2.3 GiB of 12.8 GiB available (18.5%), 4.5 of 8 GiB swap in use, and load 24.6. The early-warning rule `falcon-host-memory-low` (available < 20%) is pending, and "Host memory pressure (early warning)" has fired 38 times since Oct 6 on the relay. Vector is the current victim, but any workload spike can evict another container (OpenSearch, three Wazuh indexers, Grafana, IRIS). **Fix:** capacity plan (move or resize the Wazuh indexer tier), explicit memory requests/limits per service, and a swap-usage review.

### 3. No failure-injection coverage for aggregator OOM / memory exhaustion (P3)

Existing drills cover the sink write-rejection path, disk pressure, sensor silence, alert storms and VPN, but nothing exercises aggregator memory exhaustion, the OOM restart path, or the buffer-at-cap behavior that actually occurred. **Fix:** add a bounded chaos test to `automation/validation/tests/` and the TEST_PROCEDURES catalogue.

## Strengths (verified)

- Offsite upload: bounded retry with backoff (3 attempts, ×3), persistent dead-letter marker + critical alert rule, fail-closed retained-union prune (`bootstrap/80-offsite-backup.sh:75-102, 117-197, 648-654`).
- Abort-marker contract on SIGTERM/SIGINT for backup, offsite, cold-copy, Wazuh snapshot and restore rehearsal (`automation/validation/lib/abort.sh`; unit `TimeoutStopSec=900`).
- Nightly full offsite verification passed on 2026-10-09 (OpenSearch total=1684 mismatched=0; Wazuh total=8450 mismatched=0).
- Dead-man independence: hourly heartbeat + off-host DO watcher (`MAX_AGE=7200`), contract asserted offline (`tests/deadman_contract_test.sh`); live watcher age 515 s.
- All containers `restart: unless-stopped`; relay/pmacct/nfacctd systemd units `Restart=on-failure`.

## Prior-Run Comparison

The prior run (`falcon-20261005-full-main-e267ce1`) recorded no RES findings; it referenced only ARCH-P1-001 (single-host concentration, owner-accepted). That residual is unchanged. This run's findings are new runtime evidence gathered on the live host; the single-host risk remains as previously accepted.

## Scorecard

| Category | Score | Evidence | Gap |
|---|---:|---|---|
| Timeouts | 3 | Sink request timeouts observed; curl `-m` bounds in scripts | No systematic timeout budget per dependency |
| Retries/backoff | 4 | Offsite retry/backoff; Vector sink retries; unit Restart on relay | Backup snapshot has no retry |
| Idempotency | 4 | Snapshot reuse contract; upload-state delta; abort markers | — |
| Circuit breakers | 2 | Backpressure via disk buffers | No breaker semantics |
| Queue DLQ | 4 | Pipeline DLQ + offsite DLQ marker | Offsite DLQ alert rule not provisioned live |
| Webhook recovery | 3 | Relay spool + canary | End-to-end webhook replay not exercised |
| Worker recovery | 2 | Restart policies work, but 23 OOM restarts with drops | Memory limit/alerting |
| Graceful shutdown | 3 | Abort traps; bounded stop | Vector drops in-flight on OOM/kill |
| DB/Redis/API/email/file/realtime failure | 3 | Feed-silence + sink rules; drill coverage | Aggregator source loss invisible |
| Offline client | 3 | Edge disk buffer; queue metrics | Buffer pinned at cap for ~7 h |
| Transactions | 3 | Snapshot atomicity; fail-closed prune | — |
| Partial writes | 3 | DLQ for invalid records; sink discard counter | Source-side partial reads dropped |

## Limitations

- Read-only audit; the OOM/drop condition was observed, not reproduced, and no drill was run.
- Vector counters reset on each container restart, so the reported drop totals are lower bounds.
- OpenSearch container logs for Oct 8–9 were lost when the container was recreated during the Oct 9 relocation, so the exact snapshot API error is not recoverable.
- Concurrent lab activity (relocation/retirement commits) was in progress during the observation window; timings are UTC-stamped.

## Findings

| ID | Severity | Title |
|---|---|---|
| RES-P1-001 | P1 | Vector aggregator OOM crash-loop drops security telemetry (512 MiB cap; 23 kills; 0.7-1.5M source-side drops per window) |
| RES-P2-001 | P2 | Host memory headroom exhausted: ~18.5% available, 4.5/8 GiB swap used, recurring OOM kills |
| RES-P3-001 | P3 | No failure-injection coverage for aggregator OOM / host memory exhaustion (the failure mode that actually occurred) |
