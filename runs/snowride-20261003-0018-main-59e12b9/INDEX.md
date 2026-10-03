# Audit Run Index

## Metadata

- Name: snowride
- Run: 20261003-0018-main-59e12b9
- Profile: base (Full Hardening — 13 domain reports)
- Target repo: C:\temp\snowride
- Branch: main
- Commit: 59e12b9
- Generated: 2026-10-03
- Verdict: **GO WITH CONDITIONS**
- Totals: 46 findings — P0 0 / P1 6 / P2 25 / P3 15

## Reports

| Order | Report | Area | Status |
|---:|---|---|---|
| 1 | 01_repository_inventory.md | INV | done |
| 2 | 02_architecture_runtime_topology.md | ARCH | done |
| 3 | 03_feature_implementation_map.md | FEAT | done |
| 4 | 06_security_authz_tenancy_audit.md | SEC | done |
| 5 | 07_data_schema_migration_runtime_validation.md | DATA | done |
| 6 | 08_api_contracts_realtime_integrations.md | API | done |
| 7 | 09_testing_quality_release_confidence.md | TEST | done |
| 8 | 10_github_actions_cicd_governance.md | CI | done |
| 9 | 11_supply_chain_dependency_secrets.md | SUPPLY | done |
| 10 | 14_observability_monitoring_incident_readiness.md | OBS | done |
| 11 | 21_repo_hygiene_maintainability.md | HYG | done |
| 12 | 22_final_risk_register_roadmap.md | FINAL | done |
| 13 | 23_executive_summary_release_gate.md | EXEC | done |

Other pack prompts (24–45) are not part of the base profile for this run.

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md` — done
- Release gate: `RELEASE_GATE.md` — **GO WITH CONDITIONS**
- Risk register: `risk_register.md` — done (46 findings)
- Roadmap: `roadmap.md` — done
- Patch plan: `patch_plan.md` — done
- Supporting: `access_control_matrix.md`, `backup_restore_drill_plan.md`, `incident_tabletop_scenarios.md`, `branch_protection_recommendation.md`, `sbom_license_policy_recommendation.md`, `secret_rotation_runbook.md`, `release_notes_draft.md`, `changelog_draft.md`

## Top Risks

1. **SEC-P1-001** — Launch owner approval is unverified free text (`LAUNCH_OWNER_SIGNATURE`), so release identity is self-asserted.
2. **DATA-P1-001** — Attested migration head `0055` is behind the repo head `0056`.
3. **FINAL-P1-001** — Release trust assembled from self-asserted + stale identities.
4. **SUPPLY-P1-001** — No SBOM bound to the release.
5. **OBS-P1-001** — Alerting/scheduling is host-only, not version-controlled.
6. **CI-P1-001** — Branch protection / required checks unproven.
7. **DATA-P2-001 / TEST-P2-003** — RLS negative suites are manual and un-gated.
8. **TEST-P2-001/002** — No coverage thresholds; e2e Chromium-only.
9. **ARCH-P2-001/002/003** — No resource limits; readiness false-positive; LiveOps overrides lost on restart.
10. **HYG-P2-001** — Only `apps/web` is linted.

## Next Actions

1. Close the six P1 conditions, capture a fresh attestation at `59e12b9`/`0056`.
2. Execute `patch_plan.md` (7-day then 30-day items).
3. Re-run this audit in verification mode.
4. Validate the run: `python3 tools/run_toolchain.py C:\temp\proxmox-vm\audits\runs\snowride\20261003-0018-main-59e12b9 --write --dashboard`
