# Risk Register

Run `20261003-0018-fix-backup-abort-markers-20b5e57` — `falcon` @ `20b5e57`. One row per finding; status mirrors `follow_up_register.md`. Risks are advisory; the gate is `RELEASE_GATE.md`.

| Finding ID | Severity | Risk | Likelihood | Impact | Evidence (report) | Mitigation | Status |
|---|---|---|---|---|---|---|---|
| INV-P2-001 | P2 | Repository is majority generated content with no regeneration/drift check | Medium | Medium | 01_repository_inventory.md | See domain report | open |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require rewrite in a clone | High | Low | 01_repository_inventory.md | See domain report | open |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss | Medium | High | 02_architecture_runtime_topology.md | See domain report | open |
| ARCH-P1-002 | P1 | Abort-marker contract contradictory; normal failure exits leave no marker | Medium | High | 02_architecture_runtime_topology.md | See domain report | open |
| ARCH-P2-001 | P2 | Declared container hardening lags running containers | Medium | Medium | 02_architecture_runtime_topology.md | See domain report | open |
| ARCH-P2-002 | P2 | Wazuh/MCT tag-only images outside pin/SBOM scope | Medium | Medium | 02_architecture_runtime_topology.md | See domain report | open |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS | Medium | Medium | 02_architecture_runtime_topology.md | See domain report | open |
| ARCH-P2-005 | P2 | Only the backup job installs the abort trap | Medium | Medium | 02_architecture_runtime_topology.md | See domain report | open |
| FEAT-P2-001 | P2 | Vendored MCT services present in Compose vs archive-only policy | Medium | Medium | 03_feature_implementation_map.md | See domain report | open |
| FEAT-P2-002 | P2 | Backup/offsite single-attempt with no retry/backoff/dead-letter | Medium | High | 03_feature_implementation_map.md | See domain report | open |
| SEC-P1-001 | P1 | OpenCanary publishes six services on all interfaces | Medium | High | 06_security_authz_tenancy_audit.md | See domain report | open |
| SEC-P1-002 | P1 | Blanket `iifname "wg0" accept` grants peers host-wide access | Medium | High | 06_security_authz_tenancy_audit.md | See domain report | open |
| SEC-P1-003 | P1 | Open-inbound override state contradictory across records | Medium | High | 06_security_authz_tenancy_audit.md | See domain report | partially-fixed |
| SEC-P2-001 | P2 | Public routers lack origin auth; `ntfy-auth` is dead config | Medium | High | 06_security_authz_tenancy_audit.md | See domain report | open |
| SEC-P2-002 | P2 | Cloudflare API token passed in `curl` argv | Medium | Medium | 06_security_authz_tenancy_audit.md | See domain report | open |
| SEC-P3-001 | P3 | Default-deny `forward`/`output` policies inert at managed-table level | Low | Low | 06_security_authz_tenancy_audit.md | See domain report | open |
| DATA-P1-001 | P1 | Wazuh and IRIS data have no retention (unbounded growth) | High | High | 07_data_schema_migration_runtime_validation.md | See domain report | open |
| DATA-P2-001 | P2 | Index template and `event_time` ownership split, no consistency check | Medium | Medium | 07_data_schema_migration_runtime_validation.md | See domain report | open |
| API-P1-001 | P1 | Cross-repo pairing contract cannot be verified in this environment | Medium | High | 08_api_contracts_realtime_integrations.md | See domain report | open |
| API-P2-001 | P2 | Enrollment API tokens have no expiry field | Medium | Medium | 08_api_contracts_realtime_integrations.md | See domain report | open |
| API-P2-002 | P2 | Ingest relies on shared-secret header, not signing/idempotency | Medium | Medium | 08_api_contracts_realtime_integrations.md | See domain report | open |
| TEST-P1-001 | P1 | Repo-local test ledger points at out-of-repo, pre-rename lab tree | High | Medium | 09_testing_quality_release_confidence.md | See domain report | open |
| TEST-P1-002 | P1 | Full gate not bounded; shell suites not portable off a bash host | Medium | Medium | 09_testing_quality_release_confidence.md | See domain report | open |
| TEST-P2-001 | P2 | No backup/offsite/restore end-to-end test in the standard gate | Medium | High | 09_testing_quality_release_confidence.md | See domain report | open |
| CI-P1-001 | P1 | CI tool downloads did not fail fast (`curl` without `--fail`) | Medium | High | 10_github_actions_cicd_governance.md | See domain report | verified-fixed |
| CI-P1-002 | P1 | Branch protection and required checks not enforced server-side | Medium | High | 10_github_actions_cicd_governance.md | See domain report | owner-accepted |
| CI-P2-001 | P2 | `ci/validate.py` did not implement the promised evidence-index check | Medium | Medium | 10_github_actions_cicd_governance.md | See domain report | verified-fixed |
| CI-P2-002 | P2 | Auto-merge workflow holds `contents: write` with no environment protection | Medium | Medium | 10_github_actions_cicd_governance.md | See domain report | open |
| CI-P3-001 | P3 | Local and CI shellcheck semantics diverged | Low | Low | 10_github_actions_cicd_governance.md | See domain report | verified-fixed |
| SUPPLY-P1-001 | P1 | Digest gate scope hole: `mct/compose` and `automation/wazuh` ungated | Medium | High | 11_supply_chain_dependency_secrets.md | See domain report | open |
| SUPPLY-P1-002 | P1 | Vulnerability scanning not gated and coverage partial | Medium | High | 11_supply_chain_dependency_secrets.md | See domain report | open |
| SUPPLY-P2-001 | P2 | `.gitleaks.toml` allowlists broader than the classified set | Medium | High | 11_supply_chain_dependency_secrets.md | See domain report | open |
| SUPPLY-P2-002 | P2 | Image lock freshness is not gated | High | Medium | 11_supply_chain_dependency_secrets.md | See domain report | open |
| SUPPLY-P3-001 | P3 | `pins/verify-digests.sh` compares only the first RepoDigest | Low | Low | 11_supply_chain_dependency_secrets.md | See domain report | open |
| OBS-P0-001 | P0 | Prometheus scrapes only 3 targets; metrics hinge on the textfile collector | Medium | High | 14_observability_monitoring_incident_readiness.md | See domain report | open |
| OBS-P1-001 | P1 | Alert expressions mix `bool` and raw comparison with no linter | Medium | High | 14_observability_monitoring_incident_readiness.md | See domain report | partially-fixed |
| OBS-P1-002 | P1 | Duplicate/overlapping rules and self-contradictory coverage total | Medium | High | 14_observability_monitoring_incident_readiness.md | See domain report | partially-fixed |
| OBS-P1-003 | P1 | Relay failure counter all-or-nothing; partial path loss caught only weekly | Medium | High | 14_observability_monitoring_incident_readiness.md | See domain report | open |
| HYG-P0-001 | P0 | Publication digest and closeout declare commits that do not match HEAD | High | High | 21_repo_hygiene_maintainability.md | See domain report | partially-fixed |
| HYG-P0-002 | P0 | Publication-chain verifier not bound to HEAD (not reproducible here) | Medium | High | 21_repo_hygiene_maintainability.md | See domain report | open |
| HYG-P1-001 | P1 | Committed `review-package/` is a stale snapshot of the source tree | Medium | High | 21_repo_hygiene_maintainability.md | See domain report | open |
| HYG-P1-002 | P1 | Secret scanner path allowlist was not separator-portable | Medium | High | 21_repo_hygiene_maintainability.md | See domain report | verified-fixed |
| HYG-P2-001 | P2 | Large generated SBOM/vulnerability JSON committed (39 files) | Medium | Low | 21_repo_hygiene_maintainability.md | See domain report | open |
| FINAL-P0-001 | P0 | Production-readiness claim unsupportable at this commit | High | High | 22_final_risk_register_roadmap.md | See domain report | open |
| FINAL-P1-001 | P1 | Operational resilience incomplete across the backup lifecycle | Medium | High | 22_final_risk_register_roadmap.md | See domain report | open |
| EXEC-P1-001 | P1 | Lab "GO" can be misread as a production approval | Medium | High | 23_executive_summary_release_gate.md | See domain report | open |

## Notes

- P3 risk rows are informational; P3 findings are unpenalized in the advisory score.
- IDs and statuses are the machine-readable source for `tools/collect_findings.py`.
