# Final Risk Register, Roadmap, and Patch Plan

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: FINAL
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/22_final_risk_register_roadmap.md
- Scope limitations: aggregate of this run's 12 domain reports plus repo ledgers. 42 findings total (0 P0 / 3 P1 / 27 P2 / 12 P3).

## Scope

Aggregated all domain reports into one risk register, roadmap, patch plan, and definition of done. Duplicates (e.g. `queueDepth` = FEAT-P2-001 ≈ API-P2-002; doc drift = HYG-P2-001 ≈ TEST-P2-001 ≈ CI-P3-001) are merged into single patch sets rather than counted twice in the plan. Counts below are the raw finding counts; the plan maps each distinct fix once.

## Evidence Reviewed

All 12 domain reports in this run folder, `ledgers/risk_register.md`, `ledgers/gate_ledger.csv`, `docs/CURRENT_STATE.md`, `closeout/REVIEW-2026-09-30.md`.

## Verification Performed

- Count reconciliation: per-area findings re-summed to 3 / 27 / 12 (P1 / P2 / P3) = 42 domain findings; the `FINAL`/`EXEC` reports add 4 aggregate findings that mirror the same root causes, so the consolidated patch plan lists 18 patch sets.
- Existing-register reconciliation: R-003, R-012, R-013, R-015, R-016 checked against this run; R-014 security items are `verified-fixed` per `CURRENT_STATE.md` except the revocation-reset gap found here.

## Executive Summary

The program is a mature lab implementation with an excellent trust-root and update-verification design. There are no P0s. The single release-gating issue is **SEC-P1-001**: re-enrollment can reset a REVOKED/RETIRED sensor to CONFIGURING, silently undoing the very revocation control this branch hardened. Everything else is P2/P3 hardening: observability delivery (no pager), CI tool integrity, secret-scan history coverage, data retention/migrations, and docs/artifact staleness. The correct posture is GO WITH CONDITIONS for continued **lab** operation; the production claim remains NO-GO/insufficient-evidence as the repo itself states.

## Inventory

| Severity | Count | Theme |
|---|---:|---|
| P0 | 0 | — |
| P1 | 3 | revocation reset; release gate condition; aggregate blocker |
| P2 | 27 | retention, transport, CI integrity, observability delivery, drift |
| P3 | 12 | cleanup, docs, minor contract drift |

## Findings

### Finding ID: FINAL-P1-001 - Consolidated release blocker: revocation is not terminal on the enrollment path

- Severity: P1
- Confidence: High
- Area: FINAL
- Evidence:
  - `src/falcon_control/service.py` — `h_enroll` sets `lifecycle_state="CONFIGURING"` for an existing sensor with no REVOKED/RETIRED guard
  - `06_security_authz_tenancy_audit.md` — SEC-P1-001
  - `23_executive_summary_release_gate.md` — RELEASE_GATE condition C1
- What is happening: the strongest control in this branch (revocation) can be undone through re-enrollment.
- Why it matters: it undermines the security claim the branch exists to deliver.
- User / business impact: decommissioned/compromised devices can be returned to service without a deliberate re-provisioning control.
- Security / privacy / reliability impact: revocation bypass.
- Recommended fix: refuse enrollment of a REVOKED/RETIRED sensor; add an explicit, audited operator re-provision path if required.
- Suggested validation: negative test + manual re-enroll attempt returns 403/409.
- Owner suggestion: security owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: FINAL-P2-001 - Cross-cutting theme: automation artifacts and claims are not continuously bound to their sources

- Severity: P2
- Confidence: High
- Area: FINAL
- Evidence:
  - `TEST-P2-001` / `HYG-P2-001` / `CI-P3-001` — counts and cadence drift
  - `INV-P2-002` — inventory blind to routes/schema
  - `HYG-P2-002` — unguarded derived artifacts
  - `the control plane runs from a working tree` (ARCH-P2-001)
- What is happening: several self-describing artifacts (docs, generated files, inventory) are hand-maintained or unguarded and drift from code.
- Why it matters: the doctrine is evidence-first; drift reduces trust in every claim.
- User / business impact: reviewers cannot rely on summaries.
- Security / privacy / reliability impact: low-to-medium (false status).
- Recommended fix: derive counts/status from machine artifacts, add regeneration checks, and report `source_dirty` operationally.
- Suggested validation: a docs/derived-artifact drift check in `ci/validate.sh`.
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Revocation reset | P1 | Medium | Control bypass | SEC-P1-001 | enrollment guard |
| Production readiness unproven | P2 | High | Overclaim | CURRENT_STATE | keep lab-scoped |
| No alert delivery | P2 | High | Slow response | OBS-P2-001 | Alertmanager |
| CI tool/dep integrity | P2 | Medium | CI RCE | SC-P2-001/002/003 | pin+hash+history |
| Data growth | P2 | High | Disk | DATA-P2-001/002 | retention |
| Claim/artifact drift | P2 | High | Misinformation | HYG-P2-001 | derive in CI |

## Recommendations

### Immediate / Release Blocking
Fix SEC-P1-001 + add its regression test.

### This Week
CI Dependabot `--match-head-commit`; checksum-verify CI tools; gitleaks git-mode; correct docs.

### This Month
Alert delivery; data retention + migrations; inventory DB permissions.

### Later / Platform Evolution
Dedicated edge host; multi-site isolation; artifact attestation.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| REVOKED/RETIRED enroll guard | closes P1 | `service.py` | new test |
| `--match-head-commit` | merge integrity | `dependabot-merge.yml` | workflow test |
| Fix doc counts/cadence | accuracy | `docs/GITHUB_CI.md` | review |
| Idempotency TTL | bounds growth | `store.py` | prune test |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Enrollment revocation guard | P1 | security | S | none |
| Alert delivery path | P2 | owner | M | central stack |
| CI tool/dep pinning+checksums | P2 | build-agent | S | none |
| History secret scan | P2 | security | S | none |
| Data retention + migrations | P2 | build-agent | M | none |
| Inventory DB permissions | P2 | build-agent | S | owner |
| Derived-artifact guards | P2 | build-agent | S | none |
| Transport limits/headers | P2 | build-agent | M | none |
| Pinned deploy tree | P2 | build-agent | M | release |

## Patch-Set Mapping

| ID | Findings | Files | Dependencies | Effort | Verification |
|---|---|---|---|---|---|
| PS-001 | SEC-P1-001, FINAL-P1-001, EXEC-P1-001, TEST-P2-002 | `src/falcon_control/service.py`, `tests/phase2/test_service_integration.py` | none | S | `python -m unittest tests.phase2.test_service_integration` + manual re-enroll 403 |
| PS-002 | CI-P2-002 | `.github/workflows/dependabot-merge.yml` | none | S | workflow test with head change |
| PS-003 | SC-P2-002 | `.github/workflows/validate.yml` | none | S | gitleaks git-mode finds injected secret |
| PS-004 | SC-P2-001, SC-P2-003 | `.github/workflows/validate.yml`, new `requirements-dev.txt` | none | S | corrupted download fails; unpinned install rejected |
| PS-005 | TEST-P2-001, HYG-P2-001, CI-P3-001 | `docs/GITHUB_CI.md`, `docs/CURRENT_STATE.md`, `docs/security/BRANCH_PROTECTION.md` | none | S | counts match CI summary |
| PS-006 | DATA-P2-001, DATA-P3-001 | `src/falcon_control/store.py`, `src/falcon_agent/runner.py` | none | S | TTL prune + purge-on-cycle tests |
| PS-007 | DATA-P2-002, DATA-P2-003 | `src/falcon_control/store.py`, new `migrations/` | none | M | migration round-trip + FK test |
| PS-008 | OBS-P2-001, OBS-P2-002 | `config/prometheus/edge-alerts.yaml`, monitoring stack, `automation/validation/inventory_metrics.py` | central stack | M | synthetic critical alert delivered |
| PS-009 | SEC-P2-002, HYG-P3-001 | `automation/validation/inventory_metrics.py` | known_hosts | S | wrong-key fail-closed; config-driven sensors |
| PS-010 | SEC-P2-003 | `automation/validation/fleet_inventory.py`, unit files | owner | S | DB mode test |
| PS-011 | ARCH-P2-001, HYG-P2-002 | `deploy/edge-control-plane.service`, `ci/validate.sh`, `closeout/` | release | M | dirty-tree alarm + regen guard |
| PS-012 | FEAT-P2-001, API-P2-002 | `src/falcon_control/service.py`, contract | none | S | response schema test |
| PS-013 | API-P2-001 | `service.py`, `store.py`, contract | none | M | >500 sensor pagination test |
| PS-014 | API-P3-002, API-P3-001, FEAT-P3-001, FEAT-P3-002 | `service.py`, `falcon_cli/__main__.py` | none | S | ingest replay; error instance; token output |
| PS-015 | SEC-P2-001, ARCH-P3-001 | `src/falcon_control/http_server.py` | none | M | concurrency bound + header test |
| PS-016 | INV-P2-001 | `evidence/`, `ci/validate.sh` | archive | M | evidence size gate |
| PS-017 | INV-P2-002 | `repo-deep-dive/tools/repo_inventory.py` | tooling | M | routes/tables non-empty |
| PS-018 | OBS-P3-001, TEST-P3-001, TEST-P3-002, CI-P2-001, SC-P2-004, ARCH-P2-002, HYG-P3-002, EXEC-P2-001, FINAL-P2-001 | mixed (see domain reports) | various | M | per-item validation |

## Definition of Done

- 0 P0; the P1 (PS-001) merged with a failing-before/passing-after test.
- `ci/validate.sh` ALL PASS on the fix commit, captured as evidence.
- Docs counts/status derived from CI artifacts, not hardcoded.
- No new secret-scan, contract-drift, or ledger failures introduced.
- Production claim remains explicitly unasserted until clean-host replication + owner acceptance.

## Suggested Tests

See each domain report; the release-critical ones are PS-001 (revocation), PS-013 (pagination), PS-006/007 (retention/migration), PS-008 (alert delivery).

## Suggested Documentation Updates

- `RELEASE_GATE.md`, `EXECUTIVE_SUMMARY.md` (produced this run).
- `docs/CURRENT_STATE.md`: add the revocation-reset finding and alert-delivery gap.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is re-enrollment of revoked sensors intended? | PS-001 design | owner decision |
| Is the GitHub plan upgradeable? | CI-P2-001 | owner decision |
| Is an Alertmanager available centrally? | PS-008 | monitoring plan |

## Appendix

Per-area counts: INV 3, ARCH 3, FEAT 3, SEC 4, DATA 4, API 4, TEST 4, CI 3, SC 4, OBS 3, HYG 3, FINAL 2, EXEC 2 = 42 findings total (includes the FINAL/EXEC aggregate rows). Severity: 0 P0 / 3 P1 / 27 P2 / 12 P3. Reconciliation with the existing ledger: R-014's revocation enforcement is `verified-fixed` for sensor routes but this run finds the enrollment-path bypass (regressed surface), recorded as open.
