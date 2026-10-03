## repo-deep-dive results - 20261003-0018-fix-trust-root-87532ec

Score: 0/100 (advisory) | Advisory: GO WITH CONDITIONS

| Severity | Count |
|---|---|
| P0 | 0 |
| P1 | 3 |
| P2 | 27 |
| P3 | 12 |

Full gate: RELEASE_GATE.md in the run folder.

### Top findings

- **[P1]** EXEC-P1-001: Release gate condition: revocation must be terminal before broad/production rollout
- **[P1]** FINAL-P1-001: Consolidated release blocker: revocation is not terminal on the enrollment path
- **[P1]** SEC-P1-001: Re-enrollment silently resets a REVOKED or RETIRED sensor to CONFIGURING
