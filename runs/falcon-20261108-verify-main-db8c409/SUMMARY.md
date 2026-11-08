# Falcon verify summary — main@db8c409 (2026-11-08)

Three-lens re-verification of the Oct 14 verify plus new issues in touched areas.

## Counts

| Status | Count |
|---|---:|
| verified-fixed | 52 |
| partially-fixed | 40 |
| open | 43 |
| regressed | 5 |
| owner-accepted | 4 |
| **total** | **144** |

## P1

- **DATA-P1-001** (owner-accepted) — Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts class not ISM-managed)
- **PRIV-P1-001** (verified-fixed) — Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated)
- **WH-P1-001** (partially-fixed) — OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified)
- **ACM-P2-004** (open) — Endpoint-script sync embeds the entire enrollment token file (all per-device tokens) into every device script
- **RES-P1-002** (verified-fixed) — Root LV is above the disk-guard threshold; guard/alert state is healthy
- **RES-P2-002** (verified-fixed) — Wazuh VPN proxy socket boot race is fixed and has survived a boot
- **DR-P1-002** (partially-fixed) — Offsite upload-state truncation class is still not fail-closed; live RPO is currently met
- **PERF-P1-002** (verified-fixed) — Root LV incident condition is cleared; guard and projection rules are healthy
- **ARCH-P1-001** (owner-accepted) — Single-host concentration: host loss is total pipeline loss
- **EVOL-P1-001** (partially-fixed) — Cross-repo shared tooling has drifted and still has no pin/hash enforcement
- **EVOL-P1-002** (verified-fixed) — MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose

## New findings

