# Follow-Up Register

Findings for run `20261003-0018-fix-backup-abort-markers-20b5e57`, generated from the run reports. Append-only.
Columns: Finding ID | Severity | Title | Report | Owner | Target | Status | Post-audit note.

| Finding ID | Severity | Title | Report | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|---|
| INV-P2-001 | P2 | Repository is majority generated content with no regeneration/drift check | 01_repository_inventory.md | release owner | this month | open | |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require rewrite in a clone | 01_repository_inventory.md | release owner | this quarter | open | |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss | 02_architecture_runtime_topology.md | owner/ops | this week | open | |
| ARCH-P1-002 | P1 | Abort-marker contract contradictory; normal failure exits leave no marker | 02_architecture_runtime_topology.md | ops/resilience | immediate | open | new in this run (audit of 20b5e57) |
| ARCH-P2-001 | P2 | Declared container hardening lags running containers | 02_architecture_runtime_topology.md | container/ops | this month | open | |
| ARCH-P2-002 | P2 | Wazuh/MCT tag-only images outside pin/SBOM scope | 02_architecture_runtime_topology.md | supply-chain | this month | open | |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS | 02_architecture_runtime_topology.md | owner/ops | this month | open | |
| ARCH-P2-005 | P2 | Only the backup job installs the abort trap | 02_architecture_runtime_topology.md | ops/resilience | this week | open | new in this run |
| FEAT-P2-001 | P2 | Vendored MCT services present in Compose vs archive-only policy | 03_feature_implementation_map.md | maintainer | this month | open | |
| FEAT-P2-002 | P2 | Backup/offsite single-attempt with no retry/backoff/dead-letter | 03_feature_implementation_map.md | ops/resilience | this week | open | |
| SEC-P1-001 | P1 | OpenCanary publishes six services on all interfaces | 06_security_authz_tenancy_audit.md | ops+owner | this week | open | |
| SEC-P1-002 | P1 | Blanket `iifname "wg0" accept` grants peers host-wide access | 06_security_authz_tenancy_audit.md | ops+owner | this week | open | |
| SEC-P1-003 | P1 | Open-inbound override state contradictory across records | 06_security_authz_tenancy_audit.md | ops+owner | this week | partially-fixed | EX-13 reconciled; runtime state still host-only |
| SEC-P2-001 | P2 | Public routers lack origin auth; `ntfy-auth` is dead config | 06_security_authz_tenancy_audit.md | ops+owner | this month | open | |
| SEC-P2-002 | P2 | Cloudflare API token passed in `curl` argv | 06_security_authz_tenancy_audit.md | ops+owner | this month | open | |
| SEC-P3-001 | P3 | Default-deny `forward`/`output` policies inert at managed-table level | 06_security_authz_tenancy_audit.md | ops+owner | this quarter | open | |
| DATA-P1-001 | P1 | Wazuh and IRIS data have no retention (unbounded growth) | 07_data_schema_migration_runtime_validation.md | data owner | this week | open | |
| DATA-P2-001 | P2 | Index template and `event_time` ownership split, no consistency check | 07_data_schema_migration_runtime_validation.md | data owner | this month | open | |
| API-P1-001 | P1 | Cross-repo pairing contract cannot be verified in this environment | 08_api_contracts_realtime_integrations.md | release owner | this week | open | |
| API-P2-001 | P2 | Enrollment API tokens have no expiry field | 08_api_contracts_realtime_integrations.md | release owner | this month | open | |
| API-P2-002 | P2 | Ingest relies on shared-secret header, not signing/idempotency | 08_api_contracts_realtime_integrations.md | release owner | this month | open | |
| TEST-P1-001 | P1 | Repo-local test ledger points at out-of-repo, pre-rename lab tree | 09_testing_quality_release_confidence.md | build/QA | this week | open | |
| TEST-P1-002 | P1 | Full gate not bounded; shell suites not portable off a bash host | 09_testing_quality_release_confidence.md | build/QA | this week | open | |
| TEST-P2-001 | P2 | No backup/offsite/restore end-to-end test in the standard gate | 09_testing_quality_release_confidence.md | build/QA | this month | open | |
| CI-P1-001 | P1 | CI tool downloads did not fail fast (`curl` without `--fail`) | 10_github_actions_cicd_governance.md | CI/coordinator | this week | verified-fixed | all downloads use `--fail` + sha256 at 20b5e57 |
| CI-P1-002 | P1 | Branch protection and required checks not enforced server-side | 10_github_actions_cicd_governance.md | owner | this week | owner-accepted | plan-blocked; label gate is compensating control |
| CI-P2-001 | P2 | `ci/validate.py` did not implement the promised evidence-index check | 10_github_actions_cicd_governance.md | CI/coordinator | this month | verified-fixed | check_evidence_index wired + tested |
| CI-P2-002 | P2 | Auto-merge workflow holds `contents: write` with no environment protection | 10_github_actions_cicd_governance.md | owner | this month | open | |
| CI-P3-001 | P3 | Local and CI shellcheck semantics diverged | 10_github_actions_cicd_governance.md | CI/coordinator | this quarter | verified-fixed | both use `--severity=warning --format=gcc` |
| SUPPLY-P1-001 | P1 | Digest gate scope hole: `mct/compose` and `automation/wazuh` ungated | 11_supply_chain_dependency_secrets.md | supply-chain | this week | open | |
| SUPPLY-P1-002 | P1 | Vulnerability scanning not gated and coverage partial | 11_supply_chain_dependency_secrets.md | security/owner | this week | open | |
| SUPPLY-P2-001 | P2 | `.gitleaks.toml` allowlists broader than the classified set | 11_supply_chain_dependency_secrets.md | supply-chain | this month | open | |
| SUPPLY-P2-002 | P2 | Image lock freshness is not gated | 11_supply_chain_dependency_secrets.md | supply-chain | this month | open | |
| SUPPLY-P3-001 | P3 | `pins/verify-digests.sh` compares only the first RepoDigest | 11_supply_chain_dependency_secrets.md | supply-chain | this quarter | open | |
| OBS-P0-001 | P0 | Prometheus scrapes only 3 targets; metrics hinge on the textfile collector | 14_observability_monitoring_incident_readiness.md | observability | immediate | open | |
| OBS-P1-001 | P1 | Alert expressions mix `bool` and raw comparison with no linter | 14_observability_monitoring_incident_readiness.md | observability | this week | partially-fixed | expression test present |
| OBS-P1-002 | P1 | Duplicate/overlapping rules and self-contradictory coverage total | 14_observability_monitoring_incident_readiness.md | observability | this week | partially-fixed | reconciliation section added |
| OBS-P1-003 | P1 | Relay failure counter all-or-nothing; partial path loss caught only weekly | 14_observability_monitoring_incident_readiness.md | observability | this week | open | |
| HYG-P0-001 | P0 | Publication digest and closeout declare commits that do not match HEAD | 21_repo_hygiene_maintainability.md | owner | immediate | partially-fixed | digest `b595354f`, closeout `605fc100`, HEAD `20b5e57` |
| HYG-P0-002 | P0 | Publication-chain verifier not bound to HEAD (not reproducible here) | 21_repo_hygiene_maintainability.md | owner | immediate | open | no bash on audit host |
| HYG-P1-001 | P1 | Committed `review-package/` is a stale snapshot of the source tree | 21_repo_hygiene_maintainability.md | owner | this week | open | |
| HYG-P1-002 | P1 | Secret scanner path allowlist was not separator-portable | 21_repo_hygiene_maintainability.md | owner | this week | verified-fixed | `secret_scan.py` normalizes `\` → `/` |
| HYG-P2-001 | P2 | Large generated SBOM/vulnerability JSON committed (39 files) | 21_repo_hygiene_maintainability.md | owner | this month | open | |
| FINAL-P0-001 | P0 | Production-readiness claim unsupportable at this commit | 22_final_risk_register_roadmap.md | owner | immediate | open | |
| FINAL-P1-001 | P1 | Operational resilience incomplete across the backup lifecycle | 22_final_risk_register_roadmap.md | ops/resilience | this week | open | |
| EXEC-P1-001 | P1 | Lab "GO" can be misread as a production approval | 23_executive_summary_release_gate.md | owner | this week | open | |

## Notes

- Status vocabulary: open / partially-fixed / verified-fixed / still-open / regressed / owner-accepted.
- Only artifact-backed verification at the current commit moves a finding to `verified-fixed`.
- This register is the machine-readable status source for `tools/collect_findings.py`.
