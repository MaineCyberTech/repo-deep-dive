# Audit Run Index

## Metadata

- Name: buddy
- Run: 20261003-0018-master-99abf29
- Profile: base
- Target repo: C:\temp\buddy
- Branch: master
- Commit: 99abf29
- Generated: 2026-10-03T04:18:30.313357+00:00
- Audit completed: 2026-10-03T04:18Z
- Findings: P0 0 · P1 11 · P2 24 · P3 5 · total 40

## Reports

This run executed the `base` profile subset defined in the subagent brief (13 domain reports).
The remaining full-hardening prompts were not run.

| Order | Report | Status |
|---:|---|---|
| 1 | 00_audit_orchestrator.md | not run (base profile) |
| 2 | 01_repository_inventory.md | done |
| 3 | 02_architecture_runtime_topology.md | done |
| 4 | 03_feature_implementation_map.md | done |
| 5 | 06_security_authz_tenancy_audit.md | done |
| 6 | 24_access_control_matrix_audit.md | not run (base profile) |
| 7 | 25_multi_tenant_isolation_attack_simulation.md | not run (base profile) |
| 8 | 26_admin_console_abuse_case_audit.md | not run (base profile) |
| 9 | 07_data_schema_migration_runtime_validation.md | done |
| 10 | 37_supabase_rls_policy_deep_dive.md | not run (base profile) |
| 11 | 08_api_contracts_realtime_integrations.md | done |
| 12 | 27_webhook_delivery_replay_idempotency_audit.md | not run (base profile) |
| 13 | 28_file_upload_download_security_audit.md | not run (base profile) |
| 14 | 29_billing_payments_reconciliation_audit.md | not run (base profile) |
| 15 | 30_notification_email_push_delivery_audit.md | not run (base profile) |
| 16 | 31_search_indexing_privacy_audit.md | not run (base profile) |
| 17 | 10_github_actions_cicd_governance.md | done |
| 18 | 34_branch_protection_required_checks.md | not run (base profile) |
| 19 | 11_supply_chain_dependency_secrets.md | done |
| 20 | 35_sbom_license_policy.md | not run (base profile) |
| 21 | 36_container_runtime_security.md | not run (base profile) |
| 22 | 38_env_secret_rotation.md | not run (base profile) |
| 23 | 12_infra_deployment_environment_drift.md | not run (base profile) |
| 24 | 09_testing_quality_release_confidence.md | done |
| 25 | 13_resilience_recovery_failure_modes.md | not run (base profile) |
| 26 | 32_backup_restore_drill.md | not run (base profile) |
| 27 | 33_incident_tabletop_exercise.md | not run (base profile) |
| 28 | 14_observability_monitoring_incident_readiness.md | done |
| 29 | 15_performance_scalability_cost.md | not run (base profile) |
| 30 | 04_usability_workflow_audit.md | not run (base profile) |
| 31 | 05_ui_ux_accessibility_audit.md | not run (base profile) |
| 32 | 17_mobile_pwa_responsive_access.md | not run (base profile) |
| 33 | 18_privacy_compliance_data_governance.md | not run (base profile) |
| 34 | 39_analytics_tracking_privacy.md | not run (base profile) |
| 35 | 16_documentation_devex_operator_readiness.md | not run (base profile) |
| 36 | 19_platform_evolution_extensibility.md | not run (base profile) |
| 37 | 20_ai_automation_agent_readiness.md | not run (base profile) |
| 38 | 21_repo_hygiene_maintainability.md | done |
| 39 | 45_exploit_chain_attack_path_audit.md | not run (base profile) |
| 40 | 22_final_risk_register_roadmap.md | done |
| 41 | 23_executive_summary_release_gate.md | done |
| 42 | 40_release_notes_changelog_generator.md | not run (base profile) |

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md` — done
- Risk register: `risk_register.md` — done
- Roadmap: `roadmap.md` — done
- Patch plan: `patch_plan.md` — done
- Release gate: `RELEASE_GATE.md` — **GO WITH CONDITIONS** (0 P0, 11 P1)

## Top Risks

| # | ID | Severity | Risk |
|---:|---|---|---|
| 1 | ARCH-P1-001 | P1 | Entire game is client-authoritative; no server trust boundary (becomes security-relevant for account mode) |
| 2 | CI-P1-001 | P1 | No CI; lint/typecheck/test/build never run automatically |
| 3 | SUPPLY-P1-001 | P1 | No LICENSE; distribution/derivative rights undefined |
| 4 | DATA-P1-001 | P1 | `loadGame` silently downgrades every save to version 1 |
| 5 | DATA-P1-002 | P1 | No runtime schema validation for loaded/imported saves |
| 6 | ARCH-P1-002 | P1 | Adventure updates store but not device local state (stale UI) |
| 7 | FEAT-P1-001 | P1 | Achievements implemented but never invoked |
| 8 | FEAT-P1-002 | P1 | Lifecycle evolution/skills not wired into gameplay |
| 9 | CI-P1-002 | P1 | Branch protection / required checks unverified |
| 10 | FINAL-P1-001 | P1 | No release process binding artifacts to a commit |

## Next Actions

1. Close conditions C1–C5 in `RELEASE_GATE.md` (patch sets PS-01–PS-04, plus PS-06 partial).
2. Reconcile phase reports that claim "None" P0/P1 (`FINAL-P2-001`).
3. Validate when done: `python3 tools/run_toolchain.py C:\temp\proxmox-vm\audits\runs\buddy\20261003-0018-master-99abf29 --write --dashboard`
