# Release Gate

- Target: `falcon` @ `f5cb7c9` (`main`)
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Decision: **GO WITH CONDITIONS**

## Basis

- P0 x0, P1 x10, P2 x57, P3 x59.

## Blocking findings

| ID | Sev | Title |
|---|---|---|
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts class not ISM-managed) |
| DR-P1-002 | P1 | Offsite upload state truncated to empty by the 2026-10-10 run; the 2026-10-11 run is re-uploading the full 68.3 GiB repository and the offsite success stamp is 33.6 h stale (24 h RPO target breached) |
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| EVOL-P1-002 | P1 | MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose |
| PERF-P1-002 | P1 | Root LV sits below the guard's 20 GiB threshold: 48 failed reclaims in ~19 h, alerting every 15 min, and no effective reclaim path for the root-resident snapshot repo |
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| RES-P1-002 | P1 | Root LV below the 20 GiB disk-guard threshold; guard failing every 15 min while the snapshot repository grows ~4.3-5.5 GiB/night |
| RES-P2-002 | P1 | Wazuh VPN proxy socket boot race is not fixed: systemd still deletes the socket jobs on boot (listeners dead 45 min after the Oct 11 reboot) |
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified) |

## Verification required to change the verdict

Re-run the owning domains at the remediated commit and capture artifacts; confirm zero P0/P1 remains. This run records a delta only.

