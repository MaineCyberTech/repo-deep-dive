## repo-deep-dive results - 20261003-0018-main-7bac320

Score: 0/100 (advisory) | Advisory: GO WITH CONDITIONS

| Severity | Count |
|---|---|
| P0 | 0 |
| P1 | 9 |
| P2 | 20 |
| P3 | 12 |

Full gate: RELEASE_GATE.md in the run folder.

### Top findings

- **[P1]** CI-P1-001: The audit CI example is not under `.github/workflows/` and never runs
- **[P1]** CI-P1-002: ci/audit.yml assumes a vendored PACK_DIR that does not match this repo
- **[P1]** DATA-P1-001: findings.json violates its own schema (`sourceReports` array vs integer)
- **[P1]** DATA-P1-002: Base-profile scaffold produces a manifest the pack's own gate rejects
- **[P1]** INV-P1-001: Run is bound to 7bac320 but the worktree is at 6cada03
- **[P1]** SEC-P1-001: CI executes remotely downloaded scripts and archives as root without pinning
- **[P1]** SEC-P1-002: PAT is embedded in the git clone URL, risking token exposure in logs
- **[P1]** SUPPLY-P1-001: GitHub Actions and downloaded tools are unpinned (mutable tags/branches)
- **[P1]** TEST-P1-001: No CI job runs the pack's own lint/self-test or authorizes PRs
