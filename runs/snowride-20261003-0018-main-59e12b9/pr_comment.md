## repo-deep-dive results - 20261003-0018-main-59e12b9

Score: 0/100 (advisory) | Advisory: GO WITH CONDITIONS

| Severity | Count |
|---|---|
| P0 | 0 |
| P1 | 6 |
| P2 | 25 |
| P3 | 15 |

Full gate: RELEASE_GATE.md in the run folder.

### Top findings

- **[P1]** CI-P1-001: No evidence of branch protection or required status checks on `main`
- **[P1]** DATA-P1-001: Attested migration head (0055) is one behind the repository head (0056)
- **[P1]** FINAL-P1-001: Release trust is assembled from self-asserted and stale identities
- **[P1]** OBS-P1-001: Alerting and scheduled detection are defined only on the host, not in the repository
- **[P1]** SEC-P1-001: Launch owner approval is unverified free text, so release identity binding is not enforced
- **[P1]** SUPPLY-P1-001: No SBOM artifact generated or bound to the release commit
