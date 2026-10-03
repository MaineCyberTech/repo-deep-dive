# Release Gate — Snowride @ 59e12b9

## Verdict

GO WITH CONDITIONS

## Basis

- Findings: 0 × P0, 6 × P1, 25 × P2, 15 × P3 (46 total).
- No critical or exploitable high-severity runtime defect was identified; the security core (JWKS auth, admin/ops split, RLS default-deny, server authority) is sound.
- The conditions are release-integrity, supply-chain and operational-control gaps.

## Blocking conditions (must close before an *attested* release claim)

| # | Condition | Finding |
|---|---|---|
| 1 | Re-attest the exact HEAD (`59e12b9`) and migration head (`0056`); enforce cryptographic owner signature verification | SEC-P1-001, DATA-P1-001, FINAL-P1-001 |
| 2 | Prove branch protection / required status checks on `main` | CI-P1-001 |
| 3 | Generate and bind an SBOM to the release; add per-PR dependency audit + repository secret scan | SUPPLY-P1-001, CI-P2-001, SEC-P2-002 |
| 4 | Version-control and self-test the alerting/scheduling; define RPO/RTO | OBS-P1-001 |

## Strongly recommended (non-blocking for a bounded runtime use)

- Run the SQL negative/RLS suites in CI (DATA-P2-001, TEST-P2-003).
- Coverage thresholds and multi-engine e2e (TEST-P2-001/002).
- Resource limits and dependency-aware readiness (ARCH-P2-001/002).
- Lint all workspaces and reconcile stale docs (HYG-P2-001/003).

## Explicit caveats

- The audit is static: no `node_modules`, no database, no production access. Test-count and runtime claims are `Unknown`/prior-evidence only.
- "Configured" ≠ "exercised": backup/restore, alert firing and RLS behaviour were not re-executed in this run.
- This verdict does not grant or revoke any published gate; it records a delta only.

## Delta vs prior verdicts

Prior closeout state (`evidence/closeout/CLOSEOUT_REPORT.md`) is `INSUFFICIENT_EVIDENCE` / production acceptance NOT established. This run is consistent with that: it strengthens the runtime-security picture and adds specific, closeable release-governance conditions. No prior verdict is changed.
