# Audit Run Index

## Metadata

- Name: mainecybertech
- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Mode: full
- Profile: base
- Target repo: ``
- Branch: `main`
- Commit: `7dd0402`
- Release gate: **pending**
- Findings: 0 total — P0 0, P1 0, P2 0, P3 0

## Domains

| Domain | Area | Findings | Status |
|---|---|---:|---|
| deterministic | DET | 0 | not run |
| 00_audit_orchestrator | ORCH | 0 | not run |
| 01_repository_inventory | INV | 0 | not run |
| 02_architecture_runtime_topology | ARCH | 0 | not run |
| 03_feature_implementation_map | FEAT | 0 | not run |
| 06_security_authz_tenancy_audit | SEC | 0 | not run |
| 24_access_control_matrix_audit | ACM | 0 | not run |
| 25_multi_tenant_isolation_attack_simulation | MT | 0 | not run |
| 26_admin_console_abuse_case_audit | ADMIN | 0 | not run |
| 07_data_schema_migration_runtime_validation | DATA | 0 | not run |
| 37_supabase_rls_policy_deep_dive | RLS | 0 | not run |
| 08_api_contracts_realtime_integrations | API | 0 | not run |
| 27_webhook_delivery_replay_idempotency_audit | WH | 0 | not run |
| 28_file_upload_download_security_audit | FILE | 0 | not run |
| 29_billing_payments_reconciliation_audit | BILL | 0 | not run |
| 30_notification_email_push_delivery_audit | NOTIF | 0 | not run |
| 31_search_indexing_privacy_audit | SEARCH | 0 | not run |
| 10_github_actions_cicd_governance | CI | 0 | not run |
| 34_branch_protection_required_checks | BP | 0 | not run |
| 11_supply_chain_dependency_secrets | SC | 0 | not run |
| 35_sbom_license_policy | SBOM | 0 | not run |
| 36_container_runtime_security | CTR | 0 | not run |
| 38_env_secret_rotation | SECRET | 0 | not run |
| 12_infra_deployment_environment_drift | INFRA | 0 | not run |
| 09_testing_quality_release_confidence | TEST | 0 | not run |
| 13_resilience_recovery_failure_modes | RES | 0 | not run |
| 32_backup_restore_drill | DR | 0 | not run |
| 33_incident_tabletop_exercise | IR | 0 | not run |
| 14_observability_monitoring_incident_readiness | OBS | 0 | not run |
| 15_performance_scalability_cost | PERF | 0 | not run |
| 04_usability_workflow_audit | USE | 0 | not run |
| 05_ui_ux_accessibility_audit | UX | 0 | not run |
| 17_mobile_pwa_responsive_access | MOB | 0 | not run |
| 18_privacy_compliance_data_governance | PRIV | 0 | not run |
| 39_analytics_tracking_privacy | AN | 0 | not run |
| 16_documentation_devex_operator_readiness | DOC | 0 | not run |
| 19_platform_evolution_extensibility | EVOL | 0 | not run |
| 20_ai_automation_agent_readiness | AI | 0 | not run |
| 21_repo_hygiene_maintainability | HYGIENE | 0 | not run |
| 45_exploit_chain_attack_path_audit | CHAIN | 0 | not run |
| 22_final_risk_register_roadmap | FINAL | 0 | not run |
| 23_executive_summary_release_gate | EXEC | 0 | not run |
| 40_release_notes_changelog_generator | REL | 0 | not run |

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md`
- Risk register: `risk_register.md`
- Follow-up register: `follow_up_register.md`
- Coverage: `coverage.md`
- Roadmap: `roadmap.md`
- Patch plan: `patch_plan.md`
- Release gate: `RELEASE_GATE.md` — **pending**

## Next Actions

1. Validate: `tools/check_run.sh mainecybertech-20261014-0033-full-main-7dd0402`.
2. Publish: `tools/publish_audit.py --repo mainecybertech ...` (see runbook).
3. Remediate unresolved P0/P1/P2 per `patch_plan.md`.

