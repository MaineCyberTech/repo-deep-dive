# Release Gate

- Target: `falcon` @ `08e20d1` (`main`)
- Run: `falcon-20261009-2117-full-08e20d1`
- Decision: **NO-GO**

## Basis

- P0 x1, P1 x19, P2 x52, P3 x42.

## Blocking findings

| ID | Sev | Title |
|---|---|---|
| DATA-P0-001 | P0 | 41-hour EVE ingestion outage with confirmed data loss (empty 10.08 index, ~1.74 GB spool purge, non-retriable sink drops); durable capacity fix absent from the audited tree |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |
| ARCH-P1-002 | P1 | Live host source tree has diverged from the audited commit and is dirty; merged remediation is not deployed |
| ARCH-P1-003 | P1 | Central Vector aggregator is in a cgroup OOM restart loop; no container memory/restart alert covers it |
| CHAIN-P1-001 | P1 | WireGuard peers still have host-wide reach: the committed SEC-P1-002 narrowing is not applied to the live host |
| CI-P1-001 | P1 | Same-repo PR workflows execute on a passwordless-sudo self-hosted runner |
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate |
| DR-P1-001 | P1 | Nightly backup job failed 3 times in 7 days; Oct 8-9 snapshot hole; RPO gap ~37 h; no retry and no immediate alert |
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| EVOL-P1-002 | P1 | MCT vendoring policy proposed but not enforced; the pin gate remains blind to mct/compose |
| INFRA-P1-001 | P1 | Declared wg0 firewall narrowing (SEC-P1-002) is not applied; every VPN peer still has blanket access |
| NOTIF-P1-001 | P1 | Public lab ntfy endpoint is dead: tunnel ingress and repo docs disagree on the hostname; watcher heartbeat read and owner public subscriptions cannot work |
| OBS-P0-001 | P1 | OBS-P0-001 remediation not provisioned live: 6 rules missing from Grafana; runtime tree 22 commits behind |
| OBS-P1-001 | P1 | Aggregator source-side event drops neither exported nor alerted; 0.7-1.5M events dropped unseen |
| PERF-P1-001 | P1 | Vector aggregator OOM-kill loop under catch-up load discards events at the ingest source |
| PERF-P1-002 | P1 | Root LV carries the relocated 56 GiB snapshot repository with no root-side retention or reclaim |
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| RES-P1-001 | P1 | Vector aggregator OOM crash-loop drops security telemetry (512 MiB cap; 23 kills; 0.7-1.5M source-side drops per window) |
| SEC-P1-001 | P1 | SEC-P1-002 remediation committed but not applied live - WireGuard blanket accept still in effect |
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter path and the failure counters stayed 0 through a 40-hour outage |

## Verification required to change the verdict

Re-run the owning domains at the remediated commit and capture artifacts; confirm zero P0/P1 remains. This run records a delta only.

