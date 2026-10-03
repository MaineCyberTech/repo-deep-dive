# 22 Final Risk Register, Roadmap & Patch Plan

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent
- Inputs: domain reports 01,02,03,06,07,08,09,10,11,14,21

## Scope

Consolidation of all findings into a prioritized risk register, phased roadmap and patch plan. No P0 findings were identified.

## Evidence Reviewed

- All domain reports in this run folder; `audit_manifest.json`; `inventory.json`.
- Cross-referenced `docs/runbooks/*`, `evidence/closeout/*`, `ext_review.md`.

## Verification Performed

- Aggregated finding counts from the 11 domain reports (scripts not used; hand-verified ID uniqueness against `[A-Z]+-P[0-3]-[0-9]{3}`).
- Confirmed no finding was assigned P0 and that every finding cites a path/symbol.

## Executive Summary

46 findings, 0 critical (P0), 6 high (P1), 25 medium (P2), 15 low (P3). The product's security core (JWT/JWKS verification, admin/ops split, RLS default-deny, server authority) is strong and no exploitable defect was reproduced. The P1 set is dominated by **release and supply-chain governance** (unverified launch signature, migration-head drift, absent SBOM, host-only alerting, unproven branch protection), not runtime exploitation. Remediation is mostly small-to-medium process changes; the system is a candidate for a **GO WITH CONDITIONS** gate.

## Inventory

| Severity | Count | Areas |
|---|---|---|
| P0 | 0 | — |
| P1 | 6 | SEC, DATA, CI, SUPPLY, OBS, FINAL |
| P2 | 25 | all areas including EXEC |
| P3 | 15 | INV, FEAT, SEC, DATA, API, TEST, CI, SUPPLY, OBS, HYG |
| **Total** | **46** | |

## Findings

### Finding ID: FINAL-P1-001 - Release trust is assembled from self-asserted and stale identities

- Severity: P1
- Confidence: Medium
- Area: FINAL
- Evidence:
  - `infra/compose/docker-compose.yml` 103–121 — hardcoded `LAUNCH_OWNER_SIGNATURE`, `LAUNCH_ATTESTED_COMMIT: e5fea775…`, `LAUNCH_MIGRATION_HEAD: 0055`
  - Repo HEAD `59e12b9`; newest migration `0056` (DATA-P1-001, SEC-P1-001)
- What is happening: The launch gate binds to an older commit and migration head and accepts a free-text approval.
- Why it matters: A release can be represented as verified without a verifiable, current owner artifact.
- User / business impact: Governance risk; potential release of an un-attested schema/code combination.
- Security / privacy / reliability impact: Release integrity.
- Recommended fix: Re-attest at 59e12b9/0056, enforce cryptographic signature verification, and add a head-equality CI check.
- Suggested validation: Gate returns not-ready on tamper/stale identity.
- Owner suggestion: Owner + release engineer
- Effort estimate: M
- Dependencies: SEC-P1-001, DATA-P1-001
- Status: open

### Finding ID: FINAL-P2-001 - Operational reliability controls are not version-controlled or exercised per release

- Severity: P2
- Confidence: High
- Area: FINAL
- Evidence:
  - ARCH-P2-001/002/003 (resource limits, readiness, state loss)
  - OBS-P1-001/002 (host-only alerting, debug-only traces)
  - `docs/runbooks/BACKUP_RESTORE.md` (no RPO/RTO; stale freshness note)
- What is happening: Recovery and monitoring machinery lives largely outside the repo and is not re-tested each release.
- Why it matters: Clone-to-production reproducibility and incident response depend on undocumented host state.
- User / business impact: Longer outages; unclear recovery point.
- Security / privacy / reliability impact: Reliability governance.
- Recommended fix: Version the schedule/alert rules, define RPO/RTO, and execute backup/restore + alert drills per release with captured evidence.
- Suggested validation: Documented drill artifacts per release.
- Owner suggestion: Operator
- Effort estimate: M
- Dependencies: OBS-P1-001
- Status: open

## Risks

See `risk_register.md` (top 12). Summary:

1. Release identity not cryptographically enforced (P1).
2. Migration head drift (P1).
3. No SBOM for the release (P1).
4. Host-only alerting/scheduling (P1).
5. Branch protection unproven (P1).
6. Un-gated RLS regression (P2).
7. No coverage enforcement (P2).
8. Chromium-only e2e (P2).
9. Compose lacks resource limits (P2).
10. Readiness false-positive (P2).
11. Unlinted core services (P2).
12. Contract/doc drift (P2).

## Recommendations

1. **Release integrity (this week):** re-attest at current head, verify signature, add head-equality check.
2. **CI hardening (this week):** branch protection, dependency audit, repo secret scan, SHA-pinned actions, SBOM.
3. **Data/Rls (this month):** run SQL negative suites in CI, add migration checksum manifest.
4. **Reliability (this month):** resource limits, dependency-aware readiness, persisted LiveOps overrides, committed alert rules/SLOs.
5. **Quality (this month):** coverage thresholds, multi-engine e2e, lint all workspaces, doc reconciliation.

## Quick Wins

- Remove committed approval string; SHA-pin actions; add origin check; add `gitleaks`; fix `test:unit`; update `BACKUP_RESTORE.md`; add `.gitattributes`; delete duplicate repomix copies.

## Hardening Backlog

- HA/shared-adapter spike (only if measured load justifies); trace backend; OpenAPI generation.

## Suggested Tests

- Migration-head equality check; RLS suites in CI; signature-tamper gate test; origin rejection; coverage ratchet.

## Suggested Documentation Updates

- `AGENTS.md`, `docs/runbooks/{KILL_SWITCHES,MIGRATIONS,BACKUP_RESTORE,INCIDENT}.md`, `README.md`, `SECURITY.md`.

## Open Questions

- Is there independent external review/acceptance at this commit? (`Unknown` — prior reviews are automated subagents.)
- Is branch protection enabled in GitHub settings? (`Unknown`.)

## Appendix

- Per-area detail: see `01`–`21` reports; consolidated list in `risk_register.md`, sequenced work in `roadmap.md` and `patch_plan.md`.
