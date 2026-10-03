## repo-deep-dive results - 20261003-0018-fix-backup-abort-markers-20b5e57

Score: 0/100 (advisory) | Advisory: NO-GO

| Severity | Count |
|---|---|
| P0 | 4 |
| P1 | 20 |
| P2 | 18 |
| P3 | 4 |

Full gate: RELEASE_GATE.md in the run folder.

### Top findings

- **[P0]** FINAL-P0-001: Production-readiness claim is unsupportable at this commit (release integrity)
- **[P0]** HYG-P0-001: Publication digest and closeout declare commits that do not match the audited tree
- **[P0]** HYG-P0-002: The mandated publication-chain verifier could not be reproduced and the chain is not bound to HEAD
- **[P0]** OBS-P0-001: Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector
- **[P1]** API-P1-001: Cross-repo pairing contract cannot be verified in this environment
- **[P1]** ARCH-P1-001: Single-host concentration: host loss is total pipeline loss
- **[P1]** ARCH-P1-002: Abort-marker contract is self-contradictory and normal failure exits leave no marker
- **[P1]** CI-P1-001: CI tool downloads did not fail fast
- **[P1]** CI-P1-002: Branch protection and required checks are not enforced server-side
- **[P1]** DATA-P1-001: Wazuh and IRIS data have no retention (unbounded index growth)
- **[P1]** EXEC-P1-001: Lab "GO" can be misread as a production approval
- **[P1]** FINAL-P1-001: Operational resilience remains incomplete across the backup lifecycle
- **[P1]** HYG-P1-001: Committed `review-package/` is a stale snapshot duplicate of the source tree
- **[P1]** HYG-P1-002: Secret-scanner path allowlist was not separator-portable
- **[P1]** OBS-P1-001: Alert expressions mix `bool` and raw comparison forms with no linter
