# Executive Summary

- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Run: `mainecybertech-20261004-full-main-9c0b88c` (full mode, full-domain)
- Verdict: **NO-GO**

## Findings

- 336 total: P0 6, P1 59, P2 166, P3 105.
- Domains covered: deterministic, 00_audit_orchestrator, 01_repository_inventory, 02_architecture_runtime_topology, 03_feature_implementation_map, 06_security_authz_tenancy_audit, 24_access_control_matrix_audit, 25_multi_tenant_isolation_attack_simulation, 26_admin_console_abuse_case_audit, 07_data_schema_migration_runtime_validation, 37_supabase_rls_policy_deep_dive, 08_api_contracts_realtime_integrations, 27_webhook_delivery_replay_idempotency_audit, 28_file_upload_download_security_audit, 29_billing_payments_reconciliation_audit, 30_notification_email_push_delivery_audit, 31_search_indexing_privacy_audit, 10_github_actions_cicd_governance, 34_branch_protection_required_checks, 11_supply_chain_dependency_secrets, 35_sbom_license_policy, 36_container_runtime_security, 38_env_secret_rotation, 12_infra_deployment_environment_drift, 09_testing_quality_release_confidence, 13_resilience_recovery_failure_modes, 32_backup_restore_drill, 33_incident_tabletop_exercise, 14_observability_monitoring_incident_readiness, 15_performance_scalability_cost, 04_usability_workflow_audit, 05_ui_ux_accessibility_audit, 17_mobile_pwa_responsive_access, 18_privacy_compliance_data_governance, 39_analytics_tracking_privacy, 16_documentation_devex_operator_readiness, 19_platform_evolution_extensibility, 20_ai_automation_agent_readiness, 21_repo_hygiene_maintainability, 45_exploit_chain_attack_path_audit, 22_final_risk_register_roadmap, 23_executive_summary_release_gate, 40_release_notes_changelog_generator.

Top risks:

- `DATA-P0-001` — Orphan cleanup can recursively delete a bucket’s contents
- `DR-P0-001` — Scheduled backup and restore-test workflows never run because they are absent from the default branch
- `DR-P0-002` — The restore test never asserts integrity and therefore cannot fail on a bad backup
- `IR-P0-001` — No platform-level incident response plan, roles, or postmortem process
- `IR-P0-002` — No data breach response / notification process
- `IR-P0-003` — Total loss of the monitoring/alerting path has no independent dead-man's-switch receiver
- `ACM-P1-001` — Client-onboarding mutations run without any `requirePermission` gate
- `ADMIN-P1-001` — Org-agnostic `requireAdmin` lets a tenant admin read other tenants' admin data
- `ADMIN-P1-002` — Impersonation/cross-tenant access is logged but not reviewable or alerted
- `AI-P1-001` — Vendored audit prompt packs are stale and the run manifest references a prompt the pack does not contain
- `AI-P1-002` — `AGENTS.md` names a stale repository path and three developer docs state a stale accessibility gate size that no guard covers
- `BILL-P1-001` — Module entitlements are derived but not enforced server-side
- `BILL-P1-002` — `payments` table is never populated; payment history is silently empty
- `BILL-P1-003` — Missing Stripe webhook events leave refunds, void, and payment lifecycle unrecorded
- `BP-P1-001` — `main` requires a context (`Dependency Review`) that no job emits
- `BP-P1-002` — `enforce_admins:false` lets administrators bypass all required checks and reviews
- `BP-P1-003` — Production deploy path uses the unguarded `prod` environment, not `prod-approval`
- `CHAIN-P1-001` — Low-trust MSP role key composes into a cross-tenant read pivot
- `CHAIN-P1-002` — Caller-controlled reset redirect composes into an account-takeover assist
- `CHAIN-P1-008` — Branch-protection bypass + missing prod gate compose into unattended production change
- `CI-P1-001` — Production application deploys have no working manual-approval gate
- `CI-P1-002` — Branch-protection-as-code has a likely-mismatched required check and permits admin bypass
- `CI-P1-003` — Production deploy path cannot run; prod environment lacks secrets and protection rules
- `CTR-P1-001` — No Container Image Vulnerability Scan in CI
- `CTR-P1-002` — SBOM Is Lockfile-Only, Not an Image SBOM or Attestation
- `CTR-P1-003` — Unsigned Images With No Provenance/Attestation
- `DATA-P1-001` — Approved-membership RLS predicate reintroduced six times; pending/suspended members could access tenant data
- `DATA-P1-002` — `retention` worker task performs unbounded deletes and reports success on partial failure
- `DATA-P1-003` — Soft-delete columns remain dead schema; DELETE endpoints hard-delete
- `DR-P1-001` — No backup or restore path exists for uploaded files in Supabase Storage
- `DR-P1-002` — Restore-test backup location contract (`S3_BACKUP_BUCKET`) is undocumented and can silently mismatch the backup script
- `DR-P1-003` — Database backups are unencrypted and stored in a single location with no offsite copy
- `DR-P1-004` — The restore test has no failure alert
- `DR-P1-005` — No automated migration reverse/rollback and no bad-migration drill
- `DR-P1-006` — RPO/RTO targets are documented but unvalidated, and the Postgres RPO conflates PITR with the daily dump
- `FILE-P1-001` — Public file-request upload is permission-gated and unreachable for anonymous uploaders
- `FILE-P1-002` — File-request uploads have no tenant-scoped path and no download path; orphan cleanup will delete them
- `FILE-P1-003` — Document version history objects are deleted at replace and by orphan cleanup
- `FINAL-P1-001` — P0 data-loss path and unverified "fixed" claim block a clean release
- `INFRA-P1-001` — SSH is open to the internet on both droplets (admin_ip_ranges default 0.0.0.0/0 and CI never overrides it)
- `INFRA-P1-002` — Terraform state-locking fix is incompatible with the pinned Terraform version (use_lockfile requires >= 1.10, workflows pin 1.9)
- `IR-P1-001` — Rollback documentation contradicts itself on SHA-targeted rollback
- `IR-P1-002` — Bad-migration recovery is manual-only with no automated reverse or staging proof
- `IR-P1-003` — Worker health failure during deploy is non-fatal
- `IR-P1-004` — Backups are not verified deeply enough to prove the documented RPO/RTO
- `IR-P1-005` — Backup bucket configuration is inconsistent between the script, the backup workflow, and the restore test
- `IR-P1-006` — No runtime detection or alerting for tenant-isolation (RLS) regressions
- `MT-P1-001` — Audit log list and export are not org-scoped by default
- `MT-P1-002` — Platform dashboards expose all-tenant aggregates to any single-org admin
- `MT-P1-003` — Public file-request upload authorizes with a permission unioned across all orgs
- `NOTIF-P1-001` — Notification preferences are stored and displayed but never enforced on any send path
- `NOTIF-P1-002` — API-originated notifications bypass the dedup unique index
- `NOTIF-P1-003` — No delivery observability: email/notification failures are silent and unalerted
- `REL-P1-001` — No version identity: no tags, no product version, no commit binding in generated artifacts
- `REL-P1-002` — Documented production deploy path is stated as non-functional and the approval gate claim is false
- `SBOM-P1-001` — No license allow/deny policy in dependency review or any CI gate
- `SBOM-P1-002` — SBOM carries no license data and no dependency graph, limiting triage and license review
- `SC-P1-001` — Critical/high advisories persist in the dev dependency tree; `next` override is mis-scoped
- `SEARCH-P1-001` — `sanitizeSearchTerm` does not strip PostgREST `.` operator separators
- `SEARCH-P1-002` — Admin global search exposes profile PII and never tenant-scopes the organizations query
- `SEC-P1-001` — PII field encryption silently degrades to reversible plaintext
- `SECRET-P1-001` — M365 webhook secret is dead config while the real M365 auth value is undocumented and undeployed
- `SECRET-P1-002` — Deploy pipeline does not write several secret-class env vars the API schema and compose reference
- `WH-P1-001` — Outbound webhook idempotency is non-atomic in the API and absent in the worker dispatcher
- `WH-P1-002` — M365 webhook auth depends on `M365_CLIENT_STATE` which the deploy pipeline does not write, while `M365_WEBHOOK_SECRET` is dead config

## Reconciliation note

All six P0 entries above are `verified-fixed` at `9c0b88c` (evidence in `verification_log.md`).
The automated **NO-GO** is fail-closed: `tools/full_domain.py` counts register severities
regardless of status, and the verdict mirrors the repository's own pre-go-live
`docs/RELEASE_GATE.md` (production is not provisioned; operator exit criteria remain open).
The only open P1 in the latest authoritative verification ledger (`a97425d`, an ancestor of
main) is `CI-P1-001` — provisioning the `prod` environment, an operator action.

Rows from the `20261002-0344` full run are carried **unverified at this commit** and are
marked as such in their notes; fail-closed discipline treats them as open until re-checked.
Fresh findings at `9c0b88c`: `PERF-P3-001`, `PERF-P3-002`, `UX-P3-001`, `PRIV-P2-001`,
`AN-P3-001`, `MOB-P3-001`, `EVOL-P3-001`, `DOC-P3-001`, and the lab deterministic
`DET-P3-001` (3 container images without a digest pin). `CI-P3-003` was re-verified open on
main: the fix merged to `develop` (#94) is not on the default branch.

