# Release Gate

- Target: `falcon-edge` @ `ba4becb` (`main`)
- Run: `20261004-full-main-ba4becb`
- Decision: **GO WITH CONDITIONS**

## Basis

- P0 x0, P1 x3, P2 x35, P3 x38.

## Blocking findings

| ID | Sev | Title |
|---|---|---|
| EXEC-P1-001 | P1 | Release-gate condition (terminal revocation) is closed |
| FINAL-P1-001 | P1 | Release blocker (non-terminal revocation) is closed |
| SEC-P1-001 | P1 | Re-enrollment no longer resets a REVOKED/RETIRED sensor |

## Verification required to change the verdict

Re-run the owning domains at the remediated commit and capture artifacts; confirm zero P0/P1 remains. This run records a delta only.

