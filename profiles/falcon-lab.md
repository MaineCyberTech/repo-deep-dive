# Profile — Falcon Lab

Adapts the Repo Deep-Dive Full Hardening pack to the falcon monitoring lab.

Read `prompts/00_SHARED_AUDIT_RULES.md` first — it applies unchanged. This profile adds scope, doctrine, boundaries, an applicability matrix, lenses, waves, output wiring, and cadence. The machine-readable twin is `profiles/falcon-lab.manifest.json`.

## 1. Scope

| Element | Path / description |
|---|---|
| Central program | `/home/user/falcon-build` — monitoring stack (Wazuh/OpenSearch, ntfy, WireGuard, feeds, backups, R2 snapshots), doctrine, ledgers, gates |
| Edge program | `/home/user/falcon-edge-build` — edge sensor (image, agent, enrollment, control-plane client), own doctrine/gates/releases |
| Shared live host | Proxmox host + central VM + live containers and network fabric. Read-only during audits unless a step is explicitly sanctioned by the owner |
| Delivery artifacts | `/home/user/falcon-edge-delivery` — edge release manifest, SBOM, secrets backups |
| Audit name | `repo-deep-dive` (unchanged) |
| Run naming | `YYYYMMDD-HHMM-falcon-<sha7>_edge-<sha7>`; fallback `YYYYMMDD-HHMM-manual` |
| Finding areas | Base codes 00–40 plus `CHAIN` (45), plus `EVID` (41), `XREPO` (42), `FLEET` (43), `DQ` (44), and lens codes `ND`, `REV`, `INTG`, `LIVE`, `ADV` |

## 2. Read first (doctrine)

### falcon-build

- `AGENTS.md`, `REPOSITORY.md`, `README.md`
- `ledgers/decision_log.md`, `ledgers/gate_ledger.csv`, `ledgers/phase9_gate_ledger.csv`
- `ledgers/evidence_index.csv`, `ledgers/risk_register.md`
- `ledgers/contradiction_ledger.md`, `ledgers/exception_register.md`
- `ledgers/redactions.md`, `ledgers/progress_ledger.md`, `ledgers/test_execution.csv`
- `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `PACK_VERIFICATION_NOTES.txt`
- `pins/`, `docs/edge/EDGE_RELEASE_PIN.md`, `docs/phase9/review/` (review / adoption / verdict records)
- `docs/architecture/`, `docs/runbooks/`, `docs/security/`, `docs/threat-model/`
- `closeout/`, `review-package/`, `sbom/`, `evidence/`

### falcon-edge-build

- `AGENTS.md`, `REPOSITORY.md`, `README.md`
- `ledgers/`, `docs/` (gates/releases), `closeout/`
- `deploy/`, `image/`, `bin/`, `profiles/`, `config/`
- `api/`, `src/`, `tests/`, `ci/`, `evidence/`

Read the doctrine documents **before** forming any finding: they define what counts as evidence, how gates are earned, and which records are append-only.

## 3. Boundaries

1. **Audit-only.** Never modify application code, ledgers, gates, configs, or live systems. Write only under the run folders (canonical + edge mirror).
2. **Live host.** Read-only inspection is allowed for evidence (service state, versions, configs, logs, disk, tunnels, container state). Do not restart, reconfigure, deploy, or fail over. Destructive or disruptive checks (backup drills, failover tests, load tests) require explicit owner sanction and must be recorded in the report.
3. **Secrets.** Never print values. Reference path + secret type only (`/home/user/.env`, `secrets/`, tokens, keys, certificates). Redact in reports and transcripts.
4. **Append-only records.** The audit does not rewrite history. Findings and follow-ups live in the run folder. The decision-log entry is *proposed* (wave 4), not silently inserted; the operator applies it per doctrine.
5. **Independence.** An audit is not the independent review and not the owner adoption. It feeds them. Never mark a gate, review, or adoption as passed, and never revoke one.
6. **Parallel sessions.** Other sessions may be actively working in the repos. Record branch/HEAD/dirty state for both repos at start; re-check before writing reports; note movement in the manifest.

## 4. Applicability matrix (46 prompts)

Legend: **RUN** = run as-is · **ADAPTED** = run with the notes below · **N/A** = short not-applicable/future-readiness report with evidence (per shared rules).

| ID | Prompt | Status | Falcon-lab notes |
|---|---|---|---|
| 00 | audit_orchestrator | RUN | Establishes run folder, manifest, waves, output map |
| 01 | repository_inventory | RUN | Both repos + shared host services |
| 02 | architecture_runtime_topology | RUN | Host + VM + containers + VPN + zones + edge path |
| 03 | feature_implementation_map | ADAPTED | Capability map: feeds, alerts, backups, VPN, enrollment, snapshots — no product features |
| 04 | usability_workflow_audit | N/A | No end-user app; operator usability covered by 16 + `LIVE` lens |
| 05 | ui_ux_accessibility_audit | N/A | UIs are upstream (Wazuh / OpenSearch Dashboards); note future readiness only |
| 06 | security_authz_tenancy_audit | RUN | Host, containers, services, keys, ACLs, tunnels, enrollment |
| 07 | data_schema_migration_runtime_validation | ADAPTED | OpenSearch indices/ISM/retention, Wazuh data, config schemas; no app DB/migrations |
| 08 | api_contracts_realtime_integrations | ADAPTED | Edge control plane (mTLS), enrollment, ntfy, Prometheus, Wazuh API |
| 09 | testing_quality_release_confidence | RUN | Validation scripts and regression checks are the test estate |
| 10 | github_actions_cicd_governance | ADAPTED | In-repo `ci/` + GitHub protections; deployment is scripted/manual, not pipeline |
| 11 | supply_chain_dependency_secrets | RUN | Pins, digests, vendored deps, key material |
| 12 | infra_deployment_environment_drift | RUN | Repo ↔ live host drift; config, zone, and network drift |
| 13 | resilience_recovery_failure_modes | RUN | Power loss, disk full, tunnel loss, feed loss, boot order |
| 14 | observability_monitoring_incident_readiness | RUN | The lab's own telemetry, alerting, and incident readiness |
| 15 | performance_scalability_cost | RUN | Disk burn, retention, resource sizing, balloon/swap |
| 16 | documentation_devex_operator_readiness | RUN | Runbooks, READMEs, doctrine docs, operator handoff |
| 17 | mobile_pwa_responsive_access | N/A | No mobile surface |
| 18 | privacy_compliance_data_governance | ADAPTED | Monitoring data: redaction, retention, personal data in logs |
| 19 | platform_evolution_extensibility | RUN | Phase model, roadmap, extensibility rules |
| 20 | ai_automation_agent_readiness | ADAPTED | AGENTS.md, agent-safe automation, permission boundaries |
| 21 | repo_hygiene_maintainability | RUN | Repo layout, artifacts, generated files, dead weight |
| 22 | final_risk_register_roadmap | RUN | Aggregate; reconcile with the repos' own risk registers |
| 23 | executive_summary_release_gate | RUN | Audit opinion; reconcile with program verdicts (see §9) |
| 24 | access_control_matrix_audit | RUN | Users, keys, tokens, sockets, service accounts |
| 25 | multi_tenant_isolation_attack_simulation | N/A | Single owner/tenant; zone isolation covered by 06/12 |
| 26 | admin_console_abuse_case_audit | N/A | No first-party admin console; privileged UIs covered by 06/24 |
| 27 | webhook_delivery_replay_idempotency_audit | N/A | No webhooks; alert delivery covered by 30 |
| 28 | file_upload_download_security_audit | N/A | No app uploads; packages/SBOM covered by 11/35 |
| 29 | billing_payments_reconciliation_audit | N/A | Self-hosted, license-free |
| 30 | notification_email_push_delivery_audit | ADAPTED | ntfy alert delivery reliability — the alert channel is part of monitoring |
| 31 | search_indexing_privacy_audit | ADAPTED | OpenSearch indices, ISM/retention, exposure of indexed data |
| 32 | backup_restore_drill | RUN | Offsite, R2 snapshots, cold tier, restore drill |
| 33 | incident_tabletop_exercise | RUN | Power loss, disk full, feed corruption, key compromise |
| 34 | branch_protection_required_checks | RUN | GitHub protections + required checks |
| 35 | sbom_license_policy | RUN | License-free constraint; SBOM completeness |
| 36 | container_runtime_security | RUN | Docker runtime, images, privileges, mounts, networks |
| 37 | supabase_rls_policy_deep_dive | N/A | Not used |
| 38 | env_secret_rotation | RUN | `.env`, keys, tokens, certificates; rotation and backup |
| 39 | analytics_tracking_privacy | N/A | No analytics |
| 40 | release_notes_changelog_generator | RUN | Release manifests, pins, changelogs, digests |
| 41 | evidence_doctrine_gate_integrity_audit | RUN | Area `EVID` — ledgers vs evidence vs claims |
| 42 | cross_repo_integration_pairing_audit | RUN | Area `XREPO` — falcon↔edge pin and shared host |
| 43 | edge_fleet_hardware_audit | RUN | Area `FLEET` — edge image, updates, hardware, per-unit lifecycle |
| 44 | data_quality_pipeline_fidelity_audit | RUN | Area `DQ` — data completeness, freshness, drift, canaries |
| 45 | exploit_chain_attack_path_audit | RUN | Area `CHAIN` — end-to-end attack paths composed from domain findings |

Status counts: 28 RUN · 8 ADAPTED · 10 N/A.

## 5. Lenses

Lenses are cross-cutting overlays applied on top of the domain reports. Each lens reads the wave-1 reports plus primary evidence and writes its own `lens_<id>.md` with findings under its own area code. Lenses do not duplicate domain findings; they add what the domain view misses and cross-reference domain IDs.

| Lens | File | Area code | Apply to |
|---|---|---|---|
| New developer | `lenses/new_developer.md` | `ND` | 01, 09, 10, 12, 16, 19, 21, 32, 41, 42 |
| Independent reviewer | `lenses/independent_reviewer.md` | `REV` | 22, 23, 32, 33, 34, 35, 41 |
| Integration | `lenses/integration.md` | `INTG` | 02, 08, 12, 13, 14, 30, 32, 42 |
| Live operations | `lenses/live_operations.md` | `LIVE` | 06, 13, 14, 15, 30, 32, 33, 43 |
| Security adversary | `lenses/security_adversary.md` | `ADV` | 06, 24, 36, 38, 41, 42, 43, 45 |

## 6. Waves (orchestration)

- **Wave 0 — Recon (shared, sequential).** `00`, `01`, `02` + doctrine read. Output: run folders, `INDEX.md` skeleton, `audit_manifest.json`, repo/host snapshot, prompt statuses.
- **Wave 1 — Domain fan-out (parallel subagents, read-only).** The RUN/ADAPTED prompts in dependency order (see the falcon-lab master runner).
- **Wave 2 — Lenses (parallel).** Each lens per the matrix above.
- **Wave 3 — Synthesis.** `22` (risk register + roadmap), `23` (executive summary + release gate), `40` (release notes/changelog).
- **Wave 4 — Doctrine wiring.** Propose the decision-log entry; populate `follow_up_register.md`; define the verification plan. No gate or ledger mutation.

## 7. Output wiring

- **Canonical run folder:** `<falcon>/docs/audits/repo-deep-dive/{run}/` — all reports, lens reports, finals, `audit_manifest.json`.
- **Edge mirror:** `<edge>/docs/audits/repo-deep-dive/{run}/` — the edge-scoped reports and finals plus a pointer to the canonical folder. Both paths are recorded in the manifest.
- Findings feed the repos' risk registers and follow-up tracking **only through the operator's normal flow** (proposed decision-log entry + register updates). The audit never edits ledgers directly.
- Vendoring the pack into the repos (`docs/audits/repo-deep-dive/`) is an operator decision; by default the pack runs from its own location and only run folders are written into the repos.

## 8. Cadence

- **Full run:** before each release, verdict, or major change.
- **Focused re-run:** the affected prompts after remediation.
- **Synthesis refresh:** always re-run `22`, `23`, `40` after fixes.
- **Verification-only pass:** for already-fixed findings, re-check evidence at the current SHA and mark `verified-fixed` / `partially-fixed` / `still-open` / `regressed` without re-auditing everything.

## 9. Reconciliation rule (release gate)

The audit's release gate (`GO` / `GO WITH CONDITIONS` / `NO-GO`) is an **audit opinion**. It must reconcile with — not silently contradict — existing program verdicts and gates. When they differ, state the delta, the evidence, and the recommended reconciliation. The audit never grants or revokes a program verdict; that remains with the program's review/adoption flow.
