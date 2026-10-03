# Follow-Up Register — run `20260930-0701-falcon-8282d3f_edge-45dfed0`

Tracker for all **264 findings** from the full-domain run (P0 ×13, P1 ×80, P2 ×131, P3 ×40). **Status is audit-time** (`open`); nothing here closes a finding — only an artifact-backed verification pass or a recorded owner acceptance can.

**2026-09-30 verification pass:** statuses updated for the findings remediated this session (28 `verified-fixed`, 17 `partially-fixed`; see `verification_log.md`); all others remain `open` as filed.

Prior run `20260930-0320-falcon-794ba31_edge-2b5bc8b` (90 findings) statuses **as recorded by this run's domain agents at `8282d3f` / `45dfed0`**: **verified-fixed 1** (ND-P1-001) · **partially-fixed 31** · **still-open 53** · **regressed 2** (ND-P2-001, REV-P3-007) · **not re-assessed 3** (INTG-P3-002, INTG-P3-003, REV-P3-006). No prior LIVE finding is `verified-fixed`; "fixed" fuses were partial (cause fixed, detector/evidence open).

Legend — **Owner**: `falcon` (central repo/lab), `edge` (falcon-edge-build), `both` (cross-repo/shared host), `falcon/ops` (live operations/backups), `owner` (human decision/verdict/independence). **Target**: immediate (P0) / this week (P1) / this month (P2) / this quarter (P3). Redaction: no secret values are recorded; paths/types only.

| ID | Sev | Owner | Owning prompt/lens | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| API-P0-001 | P0 | falcon | 08_api_contracts_realtime_integrations | immediate | partially-fixed | new — Wazuh config credential literals in repo/package/delivery; scanner blind to the XML-tag form (EVID-P1-004, SC-P1-001). Cluster key rotated + Shuffle key retired 2026-09-30 (live-verified); repo/package scrubbed; rebuild/rebind at C1. |
| EVID-P0-001 | P0 | owner | 41_evidence_doctrine_gate_integrity_audit | immediate | partially-fixed | new — approval chain binds superseded package; prior REV-P1-001: still-open, prior REV-P1-002: still-open (worse). |
| EVID-P0-002 | P0 | owner | 41_evidence_doctrine_gate_integrity_audit | immediate | partially-fixed | new — reviewer disposition is a transcription; prior REV-P1-002: still-open (worse), system installer named as reviewer. |
| INV-P0-001 | P0 | edge | 01_repository_inventory | immediate | verified-fixed | prior INTG-P0-001: still-open — pin `dffcbbb7…` + sidecar `18681751…` vs actual `3fa4a49c…`. |
| INV-P0-002 | P0 | owner | 01_repository_inventory | immediate | partially-fixed | new — verdict artifacts bind a superseded package and contradict the digest (prior REV-P1-001: still-open; prior REV-P1-003: partially-fixed). |
| LIVE-P0-001 | P0 | falcon/ops | lens_live_operations | immediate | verified-fixed | prior LIVE-P0-001/002: partially-fixed; prior LIVE-P1-007: still-open — total loss waits up to ~26 h, 09-28 outage produced no notification. Alert path proven end-to-end 2026-09-30: relay/watcher/offsite metrics + rules + the three-path canary (all 2xx); DO-side watcher threshold remains (OBS-P1-001). |
| LIVE-P0-002 | P0 | falcon/ops | lens_live_operations | immediate | verified-fixed | prior LIVE-P0-001: partially-fixed — offsite succeeded 09-30 07:43Z (uncommitted), still unalerted; prior LIVE-P0-002: partially-fixed/unverified — new-services completeness unproven. |
| RES-P0-001 | P0 | falcon/ops | 13_resilience_recovery_failure_modes | immediate | verified-fixed | prior LIVE-P0-001: partially-fixed — offsite succeeded 09-30, still unalerted (no metric/alert on offsite outcome). |
| RES-P0-002 | P0 | falcon/ops | 13_resilience_recovery_failure_modes | immediate | verified-fixed | prior LIVE-P1-007: still-open — relay-only alert-path failure invisible to the dead-man (in-stack path only). |
| REV-P0-001 | P0 | owner | lens_independent_reviewer | immediate | partially-fixed | new — reviewed archive itself carries a denying digest; prior REV-P1-001: still-open, prior REV-P1-002: still-open. |
| XREPO-P0-001 | P0 | both | 42_cross_repo_integration_pairing_audit | immediate | verified-fixed | prior INTG-P0-001: still-open — pairing pin does not verify against the edge release manifest. |
| ACM-P1-001 | P1 | edge | 24_access_control_matrix_audit | this week | verified-fixed | prior REV-P1-004: still-open — CN string → operator; audited code unchanged 2b5bc8b→45dfed0. |
| ACM-P1-002 | P1 | edge | 24_access_control_matrix_audit | this week | verified-fixed | new — lifecycle state not enforced (revoked ingest, inert `destroyKeys`, retired renewal); related prior REV-P1-004/005: still-open. |
| ADV-P1-001 | P1 | edge | lens_security_adversary | this week | verified-fixed | new reproduction of the prior REV-P1-004 class (still-open): token → `CN=operator` cert → fleet-wide operator. |
| ADV-P1-002 | P1 | edge | lens_security_adversary | this week | partially-fixed | new chain framing; prior REV-P3-010: still-open — one directory/lost device exposes CA, operator and update-signing keys. |
| AI-P1-001 | P1 | falcon | 20_ai_automation_agent_readiness | this week | verified-fixed | prior ND-P1-002: still-open — agent instruction files direct work at closed gates. |
| AI-P1-002 | P1 | edge | 20_ai_automation_agent_readiness | this week | open | new this run — see report `20_ai_automation_agent_readiness`. |
| API-P1-001 | P1 | edge | 08_api_contracts_realtime_integrations | this week | verified-fixed | prior REV-P1-004: still-open — enrollment signs unconstrained CSR subject. |
| ARCH-P1-001 | P1 | both | 02_architecture_runtime_topology | this week | partially-fixed | new — single-host pressure; prior INTG-P2-005: still-open (root 82–83 %, swap 4.8–5.5 GiB). |
| ARCH-P1-002 | P1 | both | 02_architecture_runtime_topology | this week | open | prior INTG-P1-002: still-open; prior INTG-P1-004: still-open — live services run from dirty working trees. |
| ARCH-P1-003 | P1 | falcon | 02_architecture_runtime_topology | this week | open | new — trust-boundary matrix vs live port binds (prior INTG-P1-004/INTG-P3-004: still-open). |
| BP-P1-001 | P1 | both | 34_branch_protection_required_checks | this week | partially-fixed | new this run — see report `34_branch_protection_required_checks`. |
| CTR-P1-001 | P1 | falcon | 36_container_runtime_security | this week | verified-fixed | new — root systemd services execute from user-writable repo trees. |
| CTR-P1-002 | P1 | edge | 36_container_runtime_security | this week | verified-fixed | prior REV-P1-005: still-open — apply script byte-identical; agent-writable request trusted. |
| DATA-P1-001 | P1 | falcon | 07_data_schema_migration_runtime_validation | this week | verified-fixed | new — schema/retention controls exist only in validation scripts, not in deployment. |
| DATA-P1-002 | P1 | falcon | 07_data_schema_migration_runtime_validation | this week | verified-fixed | new — Wazuh indexer has no scheduled backup; repository stale since 2026-09-21. |
| DATA-P1-003 | P1 | edge | 07_data_schema_migration_runtime_validation | this week | verified-fixed | prior ND-P2-014: fixed 2026-10-01 — `purge_expired()` now cuts at now - max_age (was iso_now(), i.e. delete-all; latent while unwired); mixed-age regression test fails on the pre-fix code and passes after; edge suite 199 tests OK; ci/validate.sh PASS. |
| DOC-P1-001 | P1 | falcon | 16_documentation_devex_operator_readiness | this week | verified-fixed | prior ND-P1-002: still-open — falcon entry docs contradict ledgers. |
| DOC-P1-002 | P1 | edge | 16_documentation_devex_operator_readiness | this week | verified-fixed | prior ND-P1-005: partially-fixed — README fixed; AGENTS/REPOSITORY still say hardware absent. |
| DOC-P1-003 | P1 | falcon | 16_documentation_devex_operator_readiness | this week | verified-fixed | prior ND-P1-004: still-open — README quick start cannot deploy; first step fails in-tree. |
| DQ-P1-001 | P1 | falcon | 44_data_quality_pipeline_fidelity_audit | this week | open | new — DLQ counts pre-sink validation errors only; write failures invisible (prior LIVE-P2-002/003: still-open). |
| DR-P1-001 | P1 | falcon/ops | 32_backup_restore_drill | this week | verified-fixed | prior LIVE-P0-001: partially-fixed — offsite succeeded 09-30 (uncommitted evidence), no metric/alert. |
| DR-P1-002 | P1 | falcon/ops | 32_backup_restore_drill | this week | partially-fixed | prior LIVE-P0-002: partially-fixed — new-services/IRIS completeness unproven; offsite pruner retained-union + fail-closed implemented 2026-09-30 (live read-back confirmed; first engagement at the next offsite run). 2026-09-30 evening: a full size verification found and restored 195 objects (1.4 GB) lost to the pre-union prune; the full verification now gates every offsite run (live PASS 23:22Z, both repositories). The union prune path itself still awaits the 8th inventory. |
| DR-P1-003 | P1 | falcon/ops | 32_backup_restore_drill | this week | partially-fixed | prior LIVE-P1-005: still-open — duplicate snapshots, undocumented window, rehearsal narrower than claim. |
| DR-P1-004 | P1 | falcon/ops | 32_backup_restore_drill | this week | partially-fixed | new — backup-key custody unverified; offsite archives depend on a host-only key. |
| DR-P1-005 | P1 | both | 32_backup_restore_drill | this week | partially-fixed | prior INTG-P1-003: still-open — edge PKI/DB backup local-only; archives sit in the release surface. |
| EVID-P1-001 | P1 | falcon | 41_evidence_doctrine_gate_integrity_audit | this week | open | new — delivered package ships closeout records that do not match the delivery commit. |
| EVID-P1-002 | P1 | falcon | 41_evidence_doctrine_gate_integrity_audit | this week | partially-fixed | prior ND-P2-002: still-open — `FINAL_RESPONSE.json` contradicts `PACKAGE_DIGEST.txt` at HEAD; verdict fields hardcoded. |
| EVID-P1-003 | P1 | falcon | 41_evidence_doctrine_gate_integrity_audit | this week | open | prior ND-P1-001: verified-fixed (context) — doctrine docs/progress ledger still describe pre-closure state. |
| EVID-P1-004 | P1 | falcon | 41_evidence_doctrine_gate_integrity_audit | this week | partially-fixed | new — secret literals ship in repo/package/delivery; scanner blind to XML-tag credentials; no redaction entry (API-P0-001). |
| FEAT-P1-001 | P1 | falcon | 03_feature_implementation_map | this week | partially-fixed | prior ND-P1-002: still-open; prior ND-P2-013: partially-fixed — status claims contradict ledgers/digest. |
| FEAT-P1-002 | P1 | owner | 03_feature_implementation_map | this week | partially-fixed | prior REV-P1-001: still-open; prior REV-P1-003: partially-fixed — verdict vs digest bind different artifact sets. |
| FLEET-P1-001 | P1 | edge | 43_edge_fleet_hardware_audit | this week | verified-fixed | prior XREPO-P1-001/ND-P2-017: partially-fixed — manifest sidecar no longer matches the signed manifest. |
| FLEET-P1-002 | P1 | edge | 43_edge_fleet_hardware_audit | this week | partially-fixed | new — update apply not power-loss safe; OS/rootfs rollback path does not exist. |
| INFRA-P1-001 | P1 | falcon | 12_infra_deployment_environment_drift | this week | verified-fixed | prior LIVE-P1-006: still-open — runbooks describe a no-VPN/no-SPAN/no-backup lab. |
| INTG-P1-001 | P1 | both | lens_integration | this week | verified-fixed | prior INTG-P1-001: still-open — prepared edge rules target a plane the central alert path cannot deliver. |
| INTG-P1-002 | P1 | both | lens_integration | this week | open | prior INTG-P1-002/-P1-004: still-open — no joint release gate, upgrade order or atomic rollback. |
| INV-P1-001 | P1 | falcon | 01_repository_inventory | this week | verified-fixed | prior ND-P1-002: still-open — README/AGENTS describe pre-closure open-gate state. |
| INV-P1-002 | P1 | falcon | 01_repository_inventory | this week | open | new — live images/vendored stacks outside the pin check. |
| IR-P1-001 | P1 | falcon | 33_incident_tabletop_exercise | this week | open | new — no tabletop for total loss of the monitoring/alerting path. |
| IR-P1-002 | P1 | falcon | 33_incident_tabletop_exercise | this week | open | new — exercise coverage/artefacts short of the required catalogue. |
| LIVE-P1-001 | P1 | falcon | lens_live_operations | this week | open | prior LIVE-P0-003: partially-fixed; prior LIVE-P1-001: still-open. |
| LIVE-P1-002 | P1 | falcon | lens_live_operations | this week | verified-fixed | prior LIVE-P1-006: still-open — runbooks not executable as written by the paged operator. |
| LIVE-P1-003 | P1 | both | lens_live_operations | this week | verified-fixed | prior LIVE-P1-003/INTG-P1-001: still-open — edge fleet visible but not alertable. |
| ND-P1-001 | P1 | both | lens_new_developer | this week | verified-fixed | new — no current-state orientation layer (prior ND-P1-001: verified-fixed; prior ND-P1-002: still-open). |
| NOTIF-P1-001 | P1 | falcon/ops | 30_notification_email_push_delivery_audit | this week | partially-fixed | prior LIVE-P1-007: still-open — up to ~26 h dead-man detection; no real-time external notice. |
| NOTIF-P1-002 | P1 | falcon/ops | 30_notification_email_push_delivery_audit | this week | verified-fixed | new — relay acknowledges Grafana before delivery and keeps nothing on failure. |
| OBS-P1-001 | P1 | falcon/ops | 14_observability_monitoring_incident_readiness | this week | partially-fixed | prior LIVE-P1-007: still-open — no real-time external notification on total-host failure. Three-path canary live 2026-09-30; DO-side watcher threshold remains. |
| OBS-P1-002 | P1 | falcon/ops | 14_observability_monitoring_incident_readiness | this week | verified-fixed | prior LIVE-P0-001/002: partially-fixed — offsite/new-services backup outcomes unmonitored. |
| OBS-P1-003 | P1 | falcon | 14_observability_monitoring_incident_readiness | this week | partially-fixed | new — MoM freshness/resources/alert-eval health unalerted (prior LIVE-P1-002: partially-fixed). |
| OBS-P1-004 | P1 | both | 14_observability_monitoring_incident_readiness | this week | verified-fixed | prior INTG-P1-001/LIVE-P1-003: still-open — edge fleet has metrics but zero alerts. |
| OBS-P1-005 | P1 | falcon | 14_observability_monitoring_incident_readiness | this week | verified-fixed | prior LIVE-P1-003: still-open — never-handshaked peers invisible to the WireGuard stale rule. |
| PERF-P1-001 | P1 | falcon | 15_performance_scalability_cost | this week | partially-fixed | prior LIVE-P1-001: still-open — root LV 83 %, ~-3.8 GB/day, no reclaim path. |
| PERF-P1-002 | P1 | falcon | 15_performance_scalability_cost | this week | verified-fixed | prior LIVE-P0-003: partially-fixed — 10 GiB guard unexercised (reclaims_total 0). |
| PRIV-P1-001 | P1 | owner | 18_privacy_compliance_data_governance | this week | partially-fixed | new — synthetic-traffic claim contradicted by live owner-device telemetry; privacy authority pending (owner decision). |
| PRIV-P1-002 | P1 | both | 18_privacy_compliance_data_governance | this week | verified-fixed | prior REV-P3-011: still-open — capture wrappers export the whole credential file. |
| RES-P1-001 | P1 | falcon/ops | 13_resilience_recovery_failure_modes | this week | partially-fixed | prior LIVE-P1-007: still-open — 09-28 outage produced no notification; up to ~26 h detection. |
| RES-P1-002 | P1 | falcon | 13_resilience_recovery_failure_modes | this week | partially-fixed | prior LIVE-P1-002: partially-fixed — metrics exist (mtime, uptime), no alert uses them. |
| RES-P1-003 | P1 | both | 13_resilience_recovery_failure_modes | this week | partially-fixed | prior INTG-P1-001/INTG-P1-003: still-open — no deployed edge alert; PKI/DB local-only. |
| RES-P1-004 | P1 | falcon/ops | 13_resilience_recovery_failure_modes | this week | partially-fixed | prior LIVE-P0-002: partially-fixed; prior LIVE-P1-005: still-open — new-services verification unproven; duplicate snapshots. |
| RES-P1-005 | P1 | falcon | 13_resilience_recovery_failure_modes | this week | partially-fixed | prior LIVE-P0-003: partially-fixed; prior LIVE-P1-001: still-open — root LV unguarded; guard reclaim never exercised. |
| RES-P1-006 | P1 | falcon | 13_resilience_recovery_failure_modes | this week | verified-fixed | prior LIVE-P1-003: still-open — 6 configured peers / 4 exported. |
| REV-P1-001 | P1 | owner | lens_independent_reviewer | this week | partially-fixed | prior REV-P1-002: still-open (worse) — independence claim self-referential; P9-G11 wording requires a human reviewer. |
| REV-P1-002 | P1 | owner | lens_independent_reviewer | this week | partially-fixed | new — machine-readable verdict artifacts disagree and are not derived from one source (prior REV-P1-001/003: still-open/partially-fixed). |
| SBOM-P1-001 | P1 | both | 35_sbom_license_policy | this week | verified-fixed | new — no license data or license gate exists in either program. |
| SC-P1-001 | P1 | falcon | 11_supply_chain_dependency_secrets | this week | partially-fixed | new — scanner false-negative blind spots let the API-P0-001 credential set ship; prior ND-P2-003/REV-P3-004: still-open. |
| SEC-P1-001 | P1 | edge | 06_security_authz_tenancy_audit | this week | verified-fixed | prior REV-P1-004: still-open — CSR subject + CN trust unchanged. |
| SEC-P1-002 | P1 | edge | 06_security_authz_tenancy_audit | this week | verified-fixed | prior REV-P1-005: still-open — root update-apply trusts agent-writable request. |
| SECRET-P1-001 | P1 | edge | 38_env_secret_rotation | this week | open | new — host/Wi-Fi credentials baked into sensor images and shared across environments. |
| SECRET-P1-002 | P1 | falcon/ops | 38_env_secret_rotation | this week | open | prior LIVE-P2-005: still-open — cleartext multi-class `.env` drives root tooling. |
| SECRET-P1-003 | P1 | edge | 38_env_secret_rotation | this week | verified-fixed | prior REV-P3-010/INTG-P2-003/INTG-P1-003: still-open — unencrypted edge secret backups in the delivery surface. |
| XREPO-P1-001 | P1 | both | 42_cross_repo_integration_pairing_audit | this week | verified-fixed | prior INTG-P0-001: still-open; prior ND-P2-017: partially-fixed — signed manifest rewritten in place; sidecar binds superseded contents. |
| XREPO-P1-002 | P1 | both | 42_cross_repo_integration_pairing_audit | this week | verified-fixed | prior INTG-P1-001: still-open — no central alerting for the edge path. |
| XREPO-P1-003 | P1 | both | 42_cross_repo_integration_pairing_audit | this week | verified-fixed | prior INTG-P2-003/REV-P3-010: still-open — secret material in the shared delivery directory. |
| XREPO-P1-004 | P1 | both | 42_cross_repo_integration_pairing_audit | this week | partially-fixed | prior INTG-P1-004: still-open — no automated pin verification or skew detection. |
| ACM-P2-001 | P2 | edge | 24_access_control_matrix_audit | this month | open | new — expired tokens/directives never pruned (extends prior ND-P3-010/REV-P3-008: still-open). |
| ACM-P2-002 | P2 | falcon | 24_access_control_matrix_audit | this month | open | new — client-VPN enrollment shared credential, peer replacement, unthrottled. |
| ACM-P2-003 | P2 | edge | 24_access_control_matrix_audit | this month | open | new — fleet-privilege key material in unencrypted delivery backups (prior REV-P3-010: still-open). |
| ACM-P2-004 | P2 | falcon | 24_access_control_matrix_audit | this month | open | new — public routes depend on per-app logins/out-of-repo Cloudflare Access; no in-repo rate limits. |
| ADV-P2-001 | P2 | both | lens_security_adversary | this month | open | new this run — see report `lens_security_adversary`. |
| ADV-P2-002 | P2 | edge | lens_security_adversary | this month | open | new reproduction — sensor telemetry self-attested; one sensor can spoof another's health. |
| ADV-P2-003 | P2 | both | lens_security_adversary | this month | open | new this run — see report `lens_security_adversary`. |
| AI-P2-003 | P2 | falcon | 20_ai_automation_agent_readiness | this month | open | new — falcon summary artifacts hardcode a verdict opposite to the ledgers (prior ND-P2-013: partially-fixed). |
| AI-P2-004 | P2 | falcon | 20_ai_automation_agent_readiness | this month | open | new — audit outputs conflict with repo validation; no untrusted-content handling rule. |
| AI-P2-005 | P2 | falcon | 20_ai_automation_agent_readiness | this month | open | new — human-approval/drift enforcement documented, not enforced (prior ND-P3-006/ND-P3-011 context). |
| AI-P2-006 | P2 | edge | 20_ai_automation_agent_readiness | this month | open | new — edge CI docs/cadence drift; no PR/AI provenance policy (prior ND-P3-006/ND-P3-011). |
| API-P2-001 | P2 | edge | 08_api_contracts_realtime_integrations | this month | open | prior ND-P2-012: still-open — three implemented endpoints absent from the contract. |
| API-P2-002 | P2 | edge | 08_api_contracts_realtime_integrations | this month | open | new — documented pagination not implemented; `limit=-1` bypasses the cap. |
| API-P2-003 | P2 | edge | 08_api_contracts_realtime_integrations | this month | open | new — Idempotency-Key not enforced on quarantine/revoke. |
| API-P2-004 | P2 | edge | 08_api_contracts_realtime_integrations | this month | open | new — malformed CSR burns a single-use token; no problem response. |
| API-P2-005 | P2 | falcon | 08_api_contracts_realtime_integrations | this month | open | new this run — see report `08_api_contracts_realtime_integrations`. |
| ARCH-P2-001 | P2 | falcon | 02_architecture_runtime_topology | this month | open | prior INTG-P3-004: still-open — edge CP binds all interfaces. |
| ARCH-P2-002 | P2 | falcon | 02_architecture_runtime_topology | this month | open | prior INTG-P0-002/INTG-P1-003: partially-fixed/still-open — edge trust state single-host, not fully config-managed. |
| BP-P2-001 | P2 | both | 34_branch_protection_required_checks | this month | open | new — credential-bearing bake/release paths have no approval gate. |
| BP-P2-002 | P2 | both | 34_branch_protection_required_checks | this month | partially-fixed | new — no CODEOWNERS/PR template/required review; Dependabot merges bypass human review. |
| BP-P2-003 | P2 | both | 34_branch_protection_required_checks | this month | verified-fixed | new — falcon-build protection/plan state undocumented/unverifiable from repo. |
| CI-P2-001 | P2 | falcon | 10_github_actions_cicd_governance | this month | verified-fixed | prior ND-P2-001: regressed; prior ND-P2-003: still-open — mandated validation fails on committed audit run folders. |
| CI-P2-002 | P2 | falcon | 10_github_actions_cicd_governance | this month | partially-fixed | prior ND-P3-006: partially-fixed (one doc agent recorded verified-fixed; no run evidence, tests excluded). |
| CI-P2-004 | P2 | edge | 10_github_actions_cicd_governance | this month | open | prior ND-P2-012/ND-P3-011: still-open/partially-fixed — edge CI lacks route parity. |
| CTR-P2-003 | P2 | falcon | 36_container_runtime_security | this month | open | new — running stacks outside image pin/SBOM enforcement. |
| CTR-P2-004 | P2 | falcon | 36_container_runtime_security | this month | open | new — live privilege/exposure profile outgrew the container hardening certification. |
| CTR-P2-005 | P2 | falcon | 36_container_runtime_security | this month | open | new — no routine running-vs-declared drift check; digest evidence stale. |
| DATA-P2-004 | P2 | edge | 07_data_schema_migration_runtime_validation | this month | open | prior ND-P2-015: still-open — directives never consumed/purged; control DB lacks migrations/FKs/retention. |
| DATA-P2-005 | P2 | falcon | 07_data_schema_migration_runtime_validation | this month | open | prior LIVE-P2-002: still-open — retention covers one class; DLQ/fixtures unmanaged. |
| DATA-P2-006 | P2 | falcon | 07_data_schema_migration_runtime_validation | this month | open | prior LIVE-P2-003: still-open — mapping drift; dynamic mapping open to writers. |
| DOC-P2-001 | P2 | falcon | 16_documentation_devex_operator_readiness | this month | open | prior ND-P2-007: still-open + prior ND-P1-003: partially-fixed — runbooks/VPN checklist stale/mutating. |
| DOC-P2-002 | P2 | both | 16_documentation_devex_operator_readiness | this month | open | prior ND-P2-004/008/011, ND-P3-001/002/003: still-open — records and references contradict current state. |
| DOC-P2-003 | P2 | edge | 16_documentation_devex_operator_readiness | this month | open | prior ND-P2-008/011/013, ND-P3-007/009: partially-fixed/still-open — edge onboarding gaps. |
| DOC-P2-004 | P2 | owner | 16_documentation_devex_operator_readiness | this month | partially-fixed | prior REV-P1-001/003: still-open/partially-fixed — published verdict binds superseded package, still NOT_SUPPORTED. |
| DQ-P2-002 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — no dedup/idempotency on the main ingest path. |
| DQ-P2-003 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — no scheduled canary or end-to-end assertion. |
| DQ-P2-004 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — freshness detection is zero-rate silence only; partial gaps/alert feed uncovered. |
| DQ-P2-005 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — event time discarded for ingest time; hardcoded timezone label. |
| DQ-P2-006 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — completeness checks fields whose values are pipeline literals. |
| DQ-P2-007 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — retention boundaries delete silently (indices and edge spool). |
| DQ-P2-008 | P2 | falcon | 44_data_quality_pipeline_fidelity_audit | this month | open | new — consumer queries depend on unpinned dynamic mappings. |
| DR-P2-001 | P2 | falcon/ops | 32_backup_restore_drill | this month | open | new — datasets with no backup only partially accepted. |
| DR-P2-002 | P2 | falcon/ops | 32_backup_restore_drill | this month | open | new — no bad-migration/rollback drill for the index-rename path. |
| EVID-P2-001 | P2 | falcon | 41_evidence_doctrine_gate_integrity_audit | this month | open | prior REV-P3-003: partially-fixed — phase-9 aggregate omits the NOT_APPLICABLE gate. |
| EVID-P2-002 | P2 | falcon | 41_evidence_doctrine_gate_integrity_audit | this month | open | prior REV-P2-001: partially-fixed — `PACKAGE_MANIFEST.sha256` cannot verify the tree it describes. |
| EVID-P2-003 | P2 | falcon | 41_evidence_doctrine_gate_integrity_audit | this month | open | prior ND-P2-008/ND-P3-005: still-open — exception/contradiction registers not reconciled with closure. |
| EVOL-P2-001 | P2 | falcon | 19_platform_evolution_extensibility | this month | open | new — no in-repo roadmap/evolution guide/module template. |
| EVOL-P2-002 | P2 | falcon | 19_platform_evolution_extensibility | this month | open | new — shared tooling duplicated across repos instead of a versioned package. |
| EVOL-P2-003 | P2 | edge | 19_platform_evolution_extensibility | this month | open | new — edge SQLite store has no schema migration mechanism. |
| EVOL-P2-004 | P2 | falcon | 19_platform_evolution_extensibility | this month | open | new — MCT subtree vendored without pin/upstream policy; outside CI image pinning. |
| FEAT-P2-001 | P2 | falcon | 03_feature_implementation_map | this month | open | prior LIVE-P0-001: partially-fixed — offsite backup outcomes not exported to monitoring/alerting. |
| FEAT-P2-002 | P2 | falcon | 03_feature_implementation_map | this month | open | new — imported MCT docs claim a fully deployed SOC stack the lab only partially runs. |
| FLEET-P2-003 | P2 | edge | 43_edge_fleet_hardware_audit | this month | open | prior ND-P2-017: partially-fixed — live unit runs an image/SBOM combination no release reproduces. |
| FLEET-P2-004 | P2 | edge | 43_edge_fleet_hardware_audit | this month | open | new — fleet inventory cannot verify hardware matrix or site identity. |
| FLEET-P2-005 | P2 | edge | 43_edge_fleet_hardware_audit | this month | open | new — revocation/decommissioning are DB states, not enforced key lifecycle. |
| FLEET-P2-006 | P2 | edge | 43_edge_fleet_hardware_audit | this month | open | new — support bundles land on an unauthenticated partition; no redaction verification. |
| FLEET-P2-007 | P2 | edge | 43_edge_fleet_hardware_audit | this month | open | new — SD endurance half of P9-G04 has no evidence; no wear monitoring. |
| HYGIENE-P2-001 | P2 | falcon | 21_repo_hygiene_maintainability | this month | open | prior ND-P2-001: regressed — run-folder lifecycle undefined; `ci/validate.py` fails on audit folders. |
| HYGIENE-P2-002 | P2 | falcon | 21_repo_hygiene_maintainability | this month | open | prior ND-P2-001: regressed; prior ND-P2-003/ND-P3-004: still-open — stale pack and false/historical claims. |
| HYGIENE-P2-003 | P2 | falcon | 21_repo_hygiene_maintainability | this month | open | prior ND-P2-002/ND-P2-013: still-open/partially-fixed — closeout/status artifacts stale/hardcoded. |
| HYGIENE-P2-004 | P2 | edge | 21_repo_hygiene_maintainability | this month | open | prior ND-P2-013/ND-P2-017: partially-fixed — edge summary artifacts lag ledger/image. |
| INFRA-P2-001 | P2 | falcon | 12_infra_deployment_environment_drift | this month | open | prior ND-P2-004: still-open — `PORT_PROTOCOL_MATRIX.md` stale (51820 vs live 5182). |
| INFRA-P2-002 | P2 | falcon | 12_infra_deployment_environment_drift | this month | open | prior ND-P2-005: partially-fixed; prior ND-P2-006: still-open — VPN tests dial 51820; bootstrap/70 uses retired `veth-span-b`. |
| INFRA-P2-003 | P2 | edge | 12_infra_deployment_environment_drift | this month | open | new — three edge maintenance timers host-only; tunnel config/units outside backup coverage. |
| INTG-P2-001 | P2 | both | lens_integration | this month | open | prior INTG-P2-001: partially-fixed — dashboard adopted `cf7f5c4`; rules script still writes into falcon repo; unvalidated metric contract. |
| INTG-P2-002 | P2 | both | lens_integration | this month | open | prior INTG-P2-002: partially-fixed — no joint recovery/rebind procedure; central clean-host path does not reconstruct the edge side. |
| INTG-P2-003 | P2 | both | lens_integration | this month | open | prior INTG-P2-003: still-open — central→edge control unmonitored; command state not authoritative. |
| INV-P2-001 | P2 | edge | 01_repository_inventory | this month | open | new this run — see report `01_repository_inventory`. |
| IR-P2-001 | P2 | falcon | 33_incident_tabletop_exercise | this month | open | new — data-breach notification process is a paragraph, not a procedure. |
| IR-P2-002 | P2 | falcon | 33_incident_tabletop_exercise | this month | open | prior LIVE-P2-002 class: still-open (not re-verified) — reboot/boot-order incidents recur; fixes await re-exercise. |
| IR-P2-003 | P2 | falcon | 33_incident_tabletop_exercise | this month | open | new — incident-support artefacts contradict live state. |
| IR-P2-004 | P2 | both | 33_incident_tabletop_exercise | this month | open | new — edge incident readiness partial; not joined to the lab. |
| IR-P2-005 | P2 | falcon | 33_incident_tabletop_exercise | this month | open | new — R-29 postmortem follow-through incomplete; escalation contacts placeholder (prior LIVE-P2-002 class). |
| LIVE-P2-001 | P2 | falcon | lens_live_operations | this month | open | prior LIVE-P2-001: still-open — firing-proof coverage incomplete; one raw artifact contradicts its summary. Note: current-run LIVE-P2-001 is the firing-proof finding (not the prior panel finding). |
| LIVE-P2-002 | P2 | falcon/ops | lens_live_operations | this month | open | prior LIVE-P2-002 class: still-open (index hygiene not re-verified this wave). |
| LIVE-P2-003 | P2 | falcon | lens_live_operations | this month | open | prior LIVE-P0-004: partially-fixed — 6 h TLS window; 7-day re-measure pending; trade-off undocumented. |
| LIVE-P2-004 | P2 | falcon | lens_live_operations | this month | open | prior LIVE-P2-001/004: still-open — operator screens can silently lie (panel netns, mapping drift, uptime reset). |
| ND-P2-001 | P2 | falcon | lens_new_developer | this month | open | prior ND-P2-001: regressed — first documented command still red (verify_pack 37 mismatched/957 missing). |
| ND-P2-002 | P2 | falcon | lens_new_developer | this month | open | prior ND-P2-002: still-open — quick start lists a disruptive root script as health step. |
| ND-P2-003 | P2 | falcon | lens_new_developer | this month | open | prior ND-P2-003: still-open — fresh checkout cannot reach a running dev/test environment. |
| ND-P2-004 | P2 | both | lens_new_developer | this month | open | prior ND-P2-004/ND-P2-011: still-open — onboarding/verification artifacts bound to the lab host. |
| ND-P2-005 | P2 | edge | lens_new_developer | this month | open | prior ND-P2-005: partially-fixed — edge quick start example still mutates the append-only record. |
| NOTIF-P2-001 | P2 | falcon | 30_notification_email_push_delivery_audit | this month | open | new — webhook auth static path token with a fail-open branch bound to Docker bridge gateways. |
| NOTIF-P2-002 | P2 | falcon | 30_notification_email_push_delivery_audit | this month | open | prior LIVE-P0-004: partially-fixed — noise concentrated in one rule; tuning only hours old. |
| NOTIF-P2-003 | P2 | falcon | 30_notification_email_push_delivery_audit | this month | open | prior LIVE-P1-007 class: still-open — notification config not reproducible; watcher can fail invisibly. |
| OBS-P2-001 | P2 | falcon | 14_observability_monitoring_incident_readiness | this month | open | prior LIVE-P0-004 + LIVE-P1-004: partially-fixed — TLS tuning works so far; 7-day re-measure and benign filters remain. |
| OBS-P2-002 | P2 | falcon | 14_observability_monitoring_incident_readiness | this month | open | prior LIVE-P2-004: still-open — daily Suricata rotation invisible to its restart rule. |
| OBS-P2-003 | P2 | falcon | 14_observability_monitoring_incident_readiness | this month | open | prior LIVE-P2-001: still-open — firing-proof coverage incomplete; artifact/summary contradiction. |
| PERF-P2-001 | P2 | falcon | 15_performance_scalability_cost | this month | open | new — memory/swap pressure unalerted; host-side memory outside monitoring. |
| PERF-P2-002 | P2 | falcon | 15_performance_scalability_cost | this month | open | prior LIVE-P1-005: still-open — offsite copies whole snapshot repository nightly; load spikes. |
| PERF-P2-003 | P2 | falcon | 15_performance_scalability_cost | this month | open | new — throughput ~77 % of approved budget with no runtime tracking. |
| PERF-P2-004 | P2 | falcon | 15_performance_scalability_cost | this month | open | prior LIVE-P2-003: still-open (live mappings unverified this run) — mapping drift degrades aggregations. |
| PRIV-P2-001 | P2 | edge | 18_privacy_compliance_data_governance | this month | open | prior REV-P3-010: still-open — delivery dir mixes keys/credentials/unencrypted backups with publishable artifacts. |
| PRIV-P2-002 | P2 | falcon | 18_privacy_compliance_data_governance | this month | open | prior LIVE-P2-002: still-open — retention for one index class only; audit logs/DLQ lack policies. |
| PRIV-P2-003 | P2 | owner | 18_privacy_compliance_data_governance | this month | open | prior ND-P1-001: verified-fixed (context); prior REV-P1-003: partially-fixed — governance artifacts bind different sets. |
| RES-P2-001 | P2 | falcon | 13_resilience_recovery_failure_modes | this month | open | prior LIVE-P2-002 class: still-open — reboot/boot-order failures recurred; controls host-only. |
| RES-P2-002 | P2 | edge | 13_resilience_recovery_failure_modes | this month | open | prior ND-P2-014/015, REV-P3-008: still-open — edge queue latent purge + directives never decrement. |
| RES-P2-003 | P2 | falcon | 13_resilience_recovery_failure_modes | this month | open | prior LIVE-P1-006: still-open — incident-critical runbooks stale. |
| REV-P2-001 | P2 | owner | lens_independent_reviewer | this month | open | prior REV-P2-002: partially-fixed — reviewer reproduction commands not reproducible as written. |
| REV-P2-002 | P2 | falcon | lens_independent_reviewer | this month | open | new this run — see report `lens_independent_reviewer`. |
| REV-P2-003 | P2 | owner | lens_independent_reviewer | this month | open | prior REV-P1-004/005: still-open — prior-run edge P1 security fixes absent; phase-10 fix real. |
| SBOM-P2-001 | P2 | edge | 35_sbom_license_policy | this month | open | prior ND-P2-017/XREPO-P1-001: partially-fixed — sidecar stale; verification fails on the shipped set. |
| SBOM-P2-002 | P2 | both | 35_sbom_license_policy | this month | open | new — SBOM coverage over shipped artifacts incomplete in both programs. |
| SBOM-P2-003 | P2 | both | 35_sbom_license_policy | this month | open | new — SBOM/vuln/license checks not enforced in CI; dispositions stale. |
| SBOM-P2-004 | P2 | both | 35_sbom_license_policy | this month | open | prior REV-P3-009: still-open — provenance not independently verifiable (no public key in delivery). |
| SC-P2-001 | P2 | edge | 11_supply_chain_dependency_secrets | this month | open | prior REV-P3-010/INTG-P2-003: still-open — keys/credentials/unencrypted backups in the edge release surface. |
| SC-P2-002 | P2 | falcon | 11_supply_chain_dependency_secrets | this month | open | prior ND-P2-001: regressed — delivered repomix pack stale; packed-only verification INCOMPLETE. |
| SC-P2-003 | P2 | falcon | 11_supply_chain_dependency_secrets | this month | open | prior ND-P2-003: still-open — history-scan drift undetected; gate ledger still records clean history scan. |
| SC-P2-004 | P2 | both | 11_supply_chain_dependency_secrets | this month | open | new this run — see report `11_supply_chain_dependency_secrets`. |
| SEARCH-P2-001 | P2 | falcon | 31_search_indexing_privacy_audit | this month | partially-fixed | R2 cold-copy automation live 2026-09-30 (drill: falcon-eve-2026.09.22 -> cold-...; daily timer); mount + deletion procedures documented in the script header. |
| SEARCH-P2-002 | P2 | falcon | 31_search_indexing_privacy_audit | this month | open | prior LIVE-P2-003: still-open — mapping drift silently breaks keyword search/aggregations. |
| SEARCH-P2-003 | P2 | falcon | 31_search_indexing_privacy_audit | this month | open | new — search/audit logs have no retention and store query text (prior LIVE-P2-002). |
| SEARCH-P2-004 | P2 | falcon | 31_search_indexing_privacy_audit | this month | open | new this run — see report `31_search_indexing_privacy_audit`. |
| SEC-P2-001 | P2 | edge | 06_security_authz_tenancy_audit | this month | open | prior REV-P2-007: still-open — no hostname verification; one CA issues all identities. |
| SEC-P2-002 | P2 | falcon/ops | 06_security_authz_tenancy_audit | this month | open | prior LIVE-P2-005 + REV-P3-011: still-open — cleartext `.env` sourced into capture environments. |
| SEC-P2-003 | P2 | edge | 06_security_authz_tenancy_audit | this month | open | new — revocation is state-only (revoked ingest, inert `destroyKeys`, retired renewal). |
| SEC-P2-004 | P2 | edge | 06_security_authz_tenancy_audit | this month | open | prior REV-P3-010: still-open — fleet key material unencrypted in delivery, incompletely manifest-covered. |
| SEC-P2-005 | P2 | falcon | 06_security_authz_tenancy_audit | this month | open | new — public enrollment surfaces open (Wazuh 1516/1517; token-shared client-VPN). |
| SECRET-P2-004 | P2 | both | 38_env_secret_rotation | this month | open | new — rotation evidence partial; signing seed unrotatable; governance records contradict execution. |
| SECRET-P2-005 | P2 | both | 38_env_secret_rotation | this month | open | prior REV-P3-011: still-open — whole-file env export in capture/deploy/backup wrappers. |
| SECRET-P2-006 | P2 | falcon/ops | 38_env_secret_rotation | this month | open | new — no owner-env inventory/validator; duplicate keys; undocumented agent token file. |
| SECRET-P2-007 | P2 | falcon | 38_env_secret_rotation | this month | open | new — inherited Wazuh/MCT stores have no rotation execution; single-account blast radius. |
| TEST-P2-001 | P2 | falcon | 09_testing_quality_release_confidence | this month | open | new — 'validation: ALL PASS' excludes the suite; commit gate does not run tests (prior ND-P3-011: partially-fixed). |
| TEST-P2-002 | P2 | falcon | 09_testing_quality_release_confidence | this month | open | prior ND-P2-003/REV-P3-004: still-open — secret scan fails at HEAD (working-tree exit 1; history REVIEW_REQUIRED). |
| TEST-P2-003 | P2 | edge | 09_testing_quality_release_confidence | this month | verified-fixed | prior ND-P2-014: mixed-input boundary test added 2026-10-01 (`test_purge_expired_mixed_age_keeps_fresh_items`; fresh item 10 s old inside the 1 h window) — fails pre-fix, passes post-fix. |
| TEST-P2-004 | P2 | falcon | 09_testing_quality_release_confidence | this month | open | new — most evidence-backed test executions are ephemeral `/tmp/opencode` procedures. |
| TEST-P2-005 | P2 | falcon | 09_testing_quality_release_confidence | this month | open | prior ND-P2-011: still-open — 264/462 captures bind to a legacy symlink; CI skips them. |
| XREPO-P2-001 | P2 | both | 42_cross_repo_integration_pairing_audit | this month | open | prior INTG-P2-002/INTG-P3-001/ND-P2-004: partially-fixed/still-open — cross-repo documents contradict the live shared interface. |
| XREPO-P2-002 | P2 | owner | 42_cross_repo_integration_pairing_audit | this month | open | prior REV-P2-005: partially-fixed — edge P4-G02 owner-flash claim has no owner-attributable artifact (owner decision). |
| XREPO-P2-003 | P2 | both | 42_cross_repo_integration_pairing_audit | this month | open | prior INTG-P1-002/INTG-P1-004: still-open — upgrade/rollback skew only partially covered. |
| XREPO-P2-004 | P2 | both | 42_cross_repo_integration_pairing_audit | this month | open | prior INTG-P1-002: still-open — live edge control plane runs from the repository working tree. |
| ACM-P3-001 | P3 | edge | 24_access_control_matrix_audit | this quarter | open | new this run — see report `24_access_control_matrix_audit`. |
| ACM-P3-002 | P3 | edge | 24_access_control_matrix_audit | this quarter | open | new this run — see report `24_access_control_matrix_audit`. |
| ADV-P3-001 | P3 | edge | lens_security_adversary | this quarter | open | new this run — see report `lens_security_adversary`. |
| API-P3-001 | P3 | edge | 08_api_contracts_realtime_integrations | this quarter | open | new this run — see report `08_api_contracts_realtime_integrations`. |
| API-P3-002 | P3 | edge | 08_api_contracts_realtime_integrations | this quarter | open | new this run — see report `08_api_contracts_realtime_integrations`. |
| BP-P3-001 | P3 | both | 34_branch_protection_required_checks | this quarter | open | new this run — see report `34_branch_protection_required_checks`. |
| BP-P3-002 | P3 | both | 34_branch_protection_required_checks | this quarter | open | new this run — see report `34_branch_protection_required_checks`. |
| CI-P3-001 | P3 | both | 10_github_actions_cicd_governance | this quarter | open | new this run — see report `10_github_actions_cicd_governance`. |
| CI-P3-002 | P3 | both | 10_github_actions_cicd_governance | this quarter | open | new this run — see report `10_github_actions_cicd_governance`. |
| CTR-P3-006 | P3 | falcon | 36_container_runtime_security | this quarter | open | new this run — see report `36_container_runtime_security`. |
| CTR-P3-007 | P3 | falcon | 36_container_runtime_security | this quarter | open | new this run — see report `36_container_runtime_security`. |
| DATA-P3-007 | P3 | falcon | 07_data_schema_migration_runtime_validation | this quarter | open | new this run — see report `07_data_schema_migration_runtime_validation`. |
| DQ-P3-009 | P3 | falcon | 44_data_quality_pipeline_fidelity_audit | this quarter | open | new this run — see report `44_data_quality_pipeline_fidelity_audit`. |
| EVID-P3-001 | P3 | falcon | 41_evidence_doctrine_gate_integrity_audit | this quarter | open | new this run — see report `41_evidence_doctrine_gate_integrity_audit`. |
| EVOL-P3-001 | P3 | falcon | 19_platform_evolution_extensibility | this quarter | open | new this run — see report `19_platform_evolution_extensibility`. |
| EVOL-P3-002 | P3 | falcon | 19_platform_evolution_extensibility | this quarter | open | new this run — see report `19_platform_evolution_extensibility`. |
| FEAT-P3-001 | P3 | falcon | 03_feature_implementation_map | this quarter | open | new this run — see report `03_feature_implementation_map`. |
| FLEET-P3-008 | P3 | edge | 43_edge_fleet_hardware_audit | this quarter | verified-fixed | prior ND-P1-005: partially-fixed — AGENTS.md still contradicts the proven hardware matrix. |
| HYGIENE-P3-001 | P3 | falcon | 21_repo_hygiene_maintainability | this quarter | open | new this run — see report `21_repo_hygiene_maintainability`. |
| HYGIENE-P3-002 | P3 | falcon | 21_repo_hygiene_maintainability | this quarter | open | prior ND-P3-005/008/010: still-open — dead/duplicate files, rows, misleading surfaces. |
| INFRA-P3-001 | P3 | falcon | 12_infra_deployment_environment_drift | this quarter | open | new this run — see report `12_infra_deployment_environment_drift`. |
| INFRA-P3-002 | P3 | falcon | 12_infra_deployment_environment_drift | this quarter | open | new this run — see report `12_infra_deployment_environment_drift`. |
| IR-P3-001 | P3 | both | 33_incident_tabletop_exercise | this quarter | open | new/related BP-P2-001/IR-P1-002 — no CI/CD incident playbook; bake approval gap open. |
| ND-P3-001 | P3 | both | lens_new_developer | this quarter | open | new this run — see report `lens_new_developer`. |
| NOTIF-P3-001 | P3 | falcon | 30_notification_email_push_delivery_audit | this quarter | open | new this run — see report `30_notification_email_push_delivery_audit`. |
| NOTIF-P3-002 | P3 | falcon | 30_notification_email_push_delivery_audit | this quarter | open | new this run — see report `30_notification_email_push_delivery_audit`. |
| PERF-P3-001 | P3 | falcon | 15_performance_scalability_cost | this quarter | open | new — no cost model/budgets/spend visibility. |
| PERF-P3-002 | P3 | falcon | 15_performance_scalability_cost | this quarter | open | new — CI captures no performance/build-time data. |
| PRIV-P3-001 | P3 | falcon | 18_privacy_compliance_data_governance | this quarter | open | new — governance documentation gaps: identifier inventory, processor/notice artifacts. |
| PRIV-P3-002 | P3 | edge | 18_privacy_compliance_data_governance | this quarter | open | prior REV-P3-009: still-open — signed edge manifest not verifiable from delivery alone; signs hashes of secret files. |
| RES-P3-001 | P3 | falcon | 13_resilience_recovery_failure_modes | this quarter | open | new this run — see report `13_resilience_recovery_failure_modes`. |
| SBOM-P3-001 | P3 | both | 35_sbom_license_policy | this quarter | open | new this run — see report `35_sbom_license_policy`. |
| SC-P3-001 | P3 | falcon | 11_supply_chain_dependency_secrets | this quarter | open | new this run — see report `11_supply_chain_dependency_secrets`. |
| SEARCH-P3-005 | P3 | falcon | 31_search_indexing_privacy_audit | this quarter | open | new this run — see report `31_search_indexing_privacy_audit`. |
| SEARCH-P3-006 | P3 | falcon | 31_search_indexing_privacy_audit | this quarter | open | new this run — see report `31_search_indexing_privacy_audit`. |
| SEC-P3-001 | P3 | falcon | 06_security_authz_tenancy_audit | this quarter | open | new — CI secret-gate integrity (scanner invocation/allowlists, un-evidenced gitleaks run). |
| SECRET-P3-008 | P3 | falcon/ops | 38_env_secret_rotation | this quarter | open | new — break-glass custody open (OD-04); MCT runbook stale post-migration. |
| SECRET-P3-010 | P3 | falcon | 38_env_secret_rotation | this quarter | open | prior ND-P2-003: still-open — secret-scan allowlist gaps; history scan not re-recorded. |
| TEST-P3-001 | P3 | falcon | 09_testing_quality_release_confidence | this quarter | open | prior REV-P3-007: regressed — '161 tests' vs 163 at HEAD; unannotated failing capture. |
| XREPO-P3-001 | P3 | edge | 42_cross_repo_integration_pairing_audit | this quarter | open | prior INTG-P3-004: still-open — edge CP binds 0.0.0.0:9443 with firewall-only gate. |

| FINAL-P0-001 | P0 | owner | 22_final_risk_register_roadmap | immediate | partially-fixed | filed by synthesis (22) — release cannot be approved/delivered on current evidence. |
| FINAL-P0-002 | P0 | falcon/ops | 22_final_risk_register_roadmap | immediate | partially-fixed | filed by synthesis (22) — live protection cannot detect its own failure. |
| FINAL-P1-001 | P1 | falcon | 22_final_risk_register_roadmap | this week | verified-fixed | filed by synthesis (22) — findings.json classification fields. |
| FINAL-P1-002 | P1 | both | 22_final_risk_register_roadmap | this week | verified-fixed | filed by synthesis (22) — stale-but-open statuses. |
| FINAL-P1-003 | P1 | falcon | 22_final_risk_register_roadmap | this week | verified-fixed | filed by synthesis (22) — run artifacts fail ci/validate.py (CI-P2-001). |
| FINAL-P1-004 | P1 | falcon | 22_final_risk_register_roadmap | this week | verified-fixed | filed by synthesis (22) — verification pass pending. |
| EXEC-P1-001 | P1 | owner | 23_executive_summary_release_gate | this week | partially-fixed | filed by synthesis (23) — prior-run P0s not verified-fixed. |
| EXEC-P1-002 | P1 | owner | 23_executive_summary_release_gate | this week | verified-fixed | filed by synthesis (23) — owner decisions D1–D8 pending. |

## Verification plan

1. Each fix lands with an evidence capture at the current commit; findings move to `verified-fixed` only with an artifact at the post-fix SHA.
2. Re-run the owning prompt/lens checks for every P0/P1 first; then the verification-only pass produces `verification_log.md` with per-finding `verified-fixed` / `partially-fixed` / `still-open` / `regressed` verdicts.
3. Rebuild `findings.json` aggregates from the reports after every verification wave (counts must stay reconciled: 11/74/131/40).
4. Refresh risk register, release gate, release notes and changelog (prompts 22, 23, 40) after each verification wave.
5. Never close on assertion. Regressions are new entries, not edits (append-only doctrine).

## Human decisions required (owner)

| # | Decision | Related findings |
|---|---|---|
| D1 | Reviewer artifact production + reviewer/installer disambiguation + owner authorization recording | EVID-P0-002, REV-P1-001, REV-P0-001 |
| D2 | Re-approve or return the P9-G04 reset approximation; align edge verdict with ledgers | REV-P2-006, DOC-P2-004, FEAT-P1-002 |
| D3 | Authorize/route the edge alert-rules deployment (central plane vs Alertmanager) | INTG-P1-001, XREPO-P1-002, OBS-P1-004 |
| D4 | Retention vs cold-offload decision; offsite alerting target | RES-P0-001, DR-P1-001, SEARCH-P2-001 |
| D5 | Secrets-backup encryption (or explicit risk acceptance) and credential rotation — includes the committed Wazuh credential set | XREPO-P1-003, SECRET-P1-003, API-P0-001, SC-P2-001 |
| D6 | Edge offsite PKI/DB custody (or explicit acceptance) and backup-key custody | DR-P1-005, DR-P1-004, SECRET-P1-001 |
| D7 | Privacy authority for live owner-device telemetry ("synthetic traffic" claim) | PRIV-P1-001 |
| D8 | Human independence for P9-G11 / production-verdict wording | REV-P1-001, REV-P0-001 |

## Counts by owner (this run)

| Owner | Count |
|---|---:|
| falcon | 125 |
| edge | 53 |
| both | 44 |
| falcon/ops | 21 |
| owner | 13 |