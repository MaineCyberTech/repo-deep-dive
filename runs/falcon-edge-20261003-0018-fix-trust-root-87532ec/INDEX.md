# Audit Run Index

## Metadata

- Name: falcon-edge
- Run: 20261003-0018-fix-trust-root-87532ec
- Profile: base
- Target repo: C:\temp\falcon-edge (MaineCyberTech/falcon-edge)
- Branch: fix/trust-root
- Commit: 87532ec
- Generated: 2026-10-03T04:18:35.753257+00:00
- Release gate: **GO WITH CONDITIONS** (lab); production readiness not claimed
- Findings: 42 total — 0 P0 / 3 P1 / 27 P2 / 12 P3

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
| 9 | 11_supply_chain_dependency_secrets.md | SC | done |
| 10 | 14_observability_monitoring_incident_readiness.md | OBS | done |
| 11 | 21_repo_hygiene_maintainability.md | HYG | done |
| 12 | 22_final_risk_register_roadmap.md | FINAL | done |
| 13 | 23_executive_summary_release_gate.md | EXEC | done |

Not produced by this profile/run (no evidence requested in the brief): the remaining
Full Hardening prompts (04, 05, 12, 13, 15–20, 24–45) and their companion artifacts.

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md` — done
- Risk register: `risk_register.md` — done
- Roadmap: `roadmap.md` — done
- Patch plan: `patch_plan.md` — done
- Release gate: `RELEASE_GATE.md` — done (GO WITH CONDITIONS)

## Top Risks

1. **SEC-P1-001 / FINAL-P1-001 / EXEC-P1-001 (P1)** — re-enrollment resets a
   REVOKED/RETIRED sensor to CONFIGURING; revocation is not terminal.
2. **OBS-P2-001 (P2)** — no alert delivery (no Alertmanager/pager); rules visible only
   in Prometheus/Grafana.
3. **SC-P2-001/002/003 (P2)** — unpinned CI deps, unverified tool downloads, no
   git-history secret scan.
4. **DATA-P2-001/002/003 (P2)** — unbounded idempotency/events tables, no FK/retention,
   no schema migrations.
5. **HYG-P2-001 / TEST-P2-001 / CI-P3-001 / ARCH-P2-001 (P2)** — documentation/claim
   drift and a mutable working-tree deploy.

## Next Actions

1. Fix SEC-P1-001 with a regression test (release condition C1).
2. Bind the Dependabot merge to the checked commit; pin/hash CI deps; scan history (C2/C3).
3. Add an alert delivery path for critical rules (C4).
4. Correct documented counts/cadence; add idempotency retention.

## Validation

The orchestrator runs the pack toolchain against this folder (not run by this agent):
`python3 tools/run_toolchain.py C:\temp\proxmox-vm\audits\runs\falcon-edge\20261003-0018-fix-trust-root-87532ec --write --dashboard`.
