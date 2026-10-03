# Roadmap — Snowride hardening @ 59e12b9

Sequenced to move the release gate from **GO WITH CONDITIONS** to **GO** with minimal risk. Windows follow the severity policy: P1 this week, P2 this month, P3 this quarter.

## Now (Day 0–1) — stop the bleeding on release identity

| Action | Findings | Owner | Effort |
|---|---|---|---|
| Re-attest at `59e12b9`; set `LAUNCH_MIGRATION_HEAD=0056`; remove committed approval string | SEC-P1-001, DATA-P1-001, FINAL-P1-001 | Owner/Release | S |
| Enable branch protection with required `foundation`/`migrations` checks; capture evidence | CI-P1-001 | Owner | S |
| SHA-pin `actions/checkout` and `actions/setup-node` | CI-P2-002 | CI | S |
| Add `Origin` validation to browser-facing HTTP endpoints | SEC-P2-001 | Realtime | S |

## 7 days — CI and supply-chain hardening

| Action | Findings | Owner | Effort |
|---|---|---|---|
| Add `npm audit`/OSV + repository secret scan to CI | CI-P2-001, SEC-P2-002, SUPPLY-P2-001 | CI/Sec | S/M |
| Generate and bind a CycloneDX SBOM; upload CI artifacts | SUPPLY-P1-001, CI-P3-001 | Release | S |
| Run `supabase/tests/*` in the CI migrations job | DATA-P2-001, TEST-P2-003 | DB/CI | M |
| Add migration-head equality + checksum manifest | DATA-P1-001, DATA-P2-002 | DB/CI | S |
| Commit and self-test the alert schedule; define RPO/RTO | OBS-P1-001, FINAL-P2-001 | Operator | M |

## 30 days — reliability, observability, quality

| Action | Findings | Owner | Effort |
|---|---|---|---|
| Resource limits on compose services | ARCH-P2-001 | Operator | S |
| Dependency-aware `/readyz`; persist LiveOps overrides | ARCH-P2-002/003 | Realtime | M |
| Trace backend/retention; define SLOs/error budgets | OBS-P2-001/002 | Operator | M |
| Coverage thresholds + multi-engine e2e | TEST-P2-001/002 | QA/Web | M |
| Lint all workspaces; reconcile runbook/doc drift | HYG-P2-001/003 | Maintainer | M |
| API contract generation/parity test | API-P2-001 | Realtime | M |

## This quarter — hygiene and consolidation

| Action | Findings | Owner | Effort |
|---|---|---|---|
| De-duplicate repomix/PDF artifacts; set tree-size budget | INV-P2-001/002, HYG-P2-002 | Maintainer | M |
| Re-home root review artifacts; reconcile `.gitignore` | INV-P3-001/002 | Maintainer | S |
| Release versioning + changelog; `.gitattributes` | HYG-P3-001/002 | Release | S |
| Fix `test:unit`; align local and CI gates | TEST-P3-001/002 | Maintainer | S |
| Confirm ≥1 intended repomix archive policy | INV-P2-001 | Maintainer | S |

## Dependencies / sequencing

`FINAL-P1-001` is the umbrella for the identity items and closes only when SEC/DATA/CI/SUPPLY/OBS P1s are `verified-fixed` and a fresh attestation exists. Re-run this audit in **verification mode** at the new attested commit.

## Not in scope (defer unless measured need)

HA/multi-region/shared adapter, trace sampling backend expansion, public chat, UGC ranked admission — per `ext_review.md`.
