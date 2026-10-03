# Audit Run Index

## Metadata

- Name: falcon
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Profile: base
- Target repo: C:\temp\falcon
- Branch: fix/backup-abort-markers
- Commit: 20b5e57
- Generated: 2026-10-03
- Scope: static/read-only base-profile audit of 13 domain reports; no live host access.

## Reports

### Produced in this run

| Order | Report | Status |
|---:|---|---|
| 2 | 01_repository_inventory.md | done |
| 3 | 02_architecture_runtime_topology.md | done |
| 4 | 03_feature_implementation_map.md | done |
| 5 | 06_security_authz_tenancy_audit.md | done |
| 9 | 07_data_schema_migration_runtime_validation.md | done |
| 11 | 08_api_contracts_realtime_integrations.md | done |
| 24 | 09_testing_quality_release_confidence.md | done |
| 17 | 10_github_actions_cicd_governance.md | done |
| 19 | 11_supply_chain_dependency_secrets.md | done |
| 28 | 14_observability_monitoring_incident_readiness.md | done |
| 38 | 21_repo_hygiene_maintainability.md | done |
| 40 | 22_final_risk_register_roadmap.md | done |
| 41 | 23_executive_summary_release_gate.md | done |

### Not in scope for this base-profile run

The Full Hardening pack's other prompts (00, 04, 05, 12, 13, 15–20, 24–40, 45) were not run; this run is the brief's 13-report base profile. Prior-run records for those areas remain under `docs/audits/repo-deep-dive/` in the target repo.

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md` — done
- Risk register: `risk_register.md` — done (46 findings)
- Follow-up register: `follow_up_register.md` — done
- Roadmap: `roadmap.md` — done
- Patch plan: `patch_plan.md` — done
- Release gate: `RELEASE_GATE.md` — done (NO-GO for production claim; GO WITH CONDITIONS for lab)

## Top Risks

1. **FINAL-P0-001 / HYG-P0-001/002 (P0)** — delivered digest/closeout name commits `b595354f` / `605fc100`, not HEAD `20b5e57`; production-readiness claim unsupportable.
2. **OBS-P0-001 (P0)** — Prometheus scrapes only 3 targets; monitoring death hinges on the node-exporter textfile.
3. **ARCH-P1-002 (P1)** — abort-marker contract self-contradictory; failure exits leave no marker.
4. **SEC-P1-001/002/003 (P1)** — OpenCanary ports on all interfaces; blanket wg0 accept; contradictory inbound state.
5. **DATA-P1-001 (P1)** — Wazuh/IRIS have no retention on the shared data LV.
6. **SUPPLY-P1-001/002 (P1)** — digest gate scope hole; vulnerabilities not gated.
7. **API-P1-001 (P1)** — edge pairing contract unverifiable from a clone.
8. **ARCH-P1-001 (P1)** — single-host concentration: host loss is total pipeline loss.

## Findings Summary

| Severity | Count |
|---|---:|
| P0 | 4 |
| P1 | 20 |
| P2 | 18 |
| P3 | 4 |
| **Total** | **46** |

## Next Actions

1. Orchestrator: run `tools/run_toolchain.py <run> --write --dashboard`.
2. Owner: start with release rebind (FINAL-P0-001) and the abort-marker patch (ARCH-P1-002).
