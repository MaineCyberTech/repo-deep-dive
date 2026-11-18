# Audit Run Index

## Metadata

- Name: bench-test
- Run: `bench-test-20261013-0819-full-main-b916709`
- Mode: full
- Profile: base
- Target repo: `C:/temp/bench-test`
- Branch: `main`
- Commit: `b916709`
- Release gate: **NO-GO**
- Findings: 274 total — P0 6, P1 47, P2 138, P3 83

## Domains

| Domain | Area | Findings | Status |
|---|---|---:|---|
| deterministic | DET | 5 | done |
| 00_audit_orchestrator | ORCH | 5 | done |
| 01_repository_inventory | INV | 8 | done |
| 02_architecture_runtime_topology | ARCH | 6 | done |
| 03_feature_implementation_map | FEAT | 7 | done |
| 06_security_authz_tenancy_audit | SEC | 8 | done |
| 24_access_control_matrix_audit | ACM | 7 | done |
| 25_multi_tenant_isolation_attack_simulation | MT | 0 | done |
| 26_admin_console_abuse_case_audit | ADMIN | 8 | done |
| 07_data_schema_migration_runtime_validation | DATA | 8 | done |
| 37_supabase_rls_policy_deep_dive | RLS | 0 | done |
| 08_api_contracts_realtime_integrations | API | 8 | done |
| 27_webhook_delivery_replay_idempotency_audit | WH | 0 | done |
| 28_file_upload_download_security_audit | FILE | 6 | done |
| 29_billing_payments_reconciliation_audit | BILL | 0 | done |
| 30_notification_email_push_delivery_audit | NOTIF | 2 | done |
| 31_search_indexing_privacy_audit | SEARCH | 6 | done |
| 10_github_actions_cicd_governance | CI | 7 | done |
| 34_branch_protection_required_checks | BP | 7 | done |
| 11_supply_chain_dependency_secrets | SC | 7 | done |
| 35_sbom_license_policy | SBOM | 7 | done |
| 36_container_runtime_security | CTR | 5 | done |
| 38_env_secret_rotation | SECRET | 7 | done |
| 12_infra_deployment_environment_drift | INFRA | 8 | done |
| 09_testing_quality_release_confidence | TEST | 7 | done |
| 13_resilience_recovery_failure_modes | RES | 8 | done |
| 32_backup_restore_drill | DR | 7 | done |
| 33_incident_tabletop_exercise | IR | 6 | done |
| 14_observability_monitoring_incident_readiness | OBS | 8 | done |
| 15_performance_scalability_cost | PERF | 8 | done |
| 04_usability_workflow_audit | USE | 8 | done |
| 05_ui_ux_accessibility_audit | UX | 8 | done |
| 17_mobile_pwa_responsive_access | MOB | 7 | done |
| 18_privacy_compliance_data_governance | PRIV | 8 | done |
| 39_analytics_tracking_privacy | AN | 4 | done |
| 16_documentation_devex_operator_readiness | DOC | 7 | done |
| 19_platform_evolution_extensibility | EVOL | 8 | done |
| 20_ai_automation_agent_readiness | AI | 6 | done |
| 21_repo_hygiene_maintainability | HYGIENE | 8 | done |
| 45_exploit_chain_attack_path_audit | CHAIN | 5 | done |
| 22_final_risk_register_roadmap | FINAL | 8 | done |
| 23_executive_summary_release_gate | EXEC | 7 | done |
| 40_release_notes_changelog_generator | REL | 8 | done |

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md`
- Risk register: `risk_register.md`
- Follow-up register: `follow_up_register.md`
- Coverage: `coverage.md`
- Roadmap: `roadmap.md`
- Patch plan: `patch_plan.md`
- Release gate: `RELEASE_GATE.md` — **NO-GO**

## Next Actions

1. Validate: `tools/check_run.sh bench-test-20261013-0819-full-main-b916709`.
2. Publish: `tools/publish_audit.py --repo bench-test ...` (see runbook).
3. Remediate unresolved P0/P1/P2 per `patch_plan.md`.

