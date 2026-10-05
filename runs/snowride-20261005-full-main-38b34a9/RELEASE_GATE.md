# Release Gate

- Target: `snowride` @ `38b34a9` (`main`)
- Run: `snowride-20261005-full-main-38b34a9`
- Decision: **GO WITH CONDITIONS**

## Basis

- P0 x0, P1 x1, P2 x7, P3 x34.

## Blocking findings

| ID | Sev | Title |
|---|---|---|
| FINAL-P1-001 | P1 | Release identity is stale: attestation commit 9125913 != HEAD 38b34a9 |

## Verification required to change the verdict

Re-run the owning domains at the remediated commit and capture artifacts; confirm zero P0/P1 remains. This run records a delta only.

