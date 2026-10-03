# Release Gate

- Repository: MaineCyberTech/falcon-edge
- Branch: fix/trust-root
- Commit: 87532ec
- Run: 20261003-0018-fix-trust-root-87532ec
- Scope: lab operation (production readiness is not claimed by this repository or this audit)

## Decision

**GO WITH CONDITIONS** (for continued lab operation)

Production readiness remains not claimed and requires the outstanding owner gates
(P10-G02 clean-host replication, P10-G04 owner acceptance, P10-G06 production
change/rollback approval) per `docs/CURRENT_STATE.md` and `ledgers/gate_ledger.csv`.

## Rationale

- Findings: 0 P0 / 3 P1 / 27 P2 / 12 P3 (42 total).
- No critical (P0) issue exists.
- One unmitigated P1 defect prevents an unconditional approval: revocation is not terminal on
  the enrollment path (SEC-P1-001 / FINAL-P1-001 / EXEC-P1-001).

## Conditions

| ID | Condition | Owning finding | Verification |
|---|---|---|---|
| C1 | Refuse enrollment of a REVOKED/RETIRED sensor, with a regression test | SEC-P1-001 | `python -m unittest tests.phase2.test_service_integration`; manual re-enroll returns 403/409 |
| C2 | Bind the Dependabot merge to the checked commit | CI-P2-002 | workflow test with a changed head |
| C3 | Pin/hash CI dependencies and tool downloads; scan git history for secrets | SC-P2-001, SC-P2-002, SC-P2-003 | corrupted download fails; injected secret detected |
| C4 | Provide an alert delivery path for `severity=critical` | OBS-P2-001 | synthetic critical alert delivered |

## Gate Evidence

- `ledgers/gate_ledger.csv` — 88 gates: 86 PASS / 2 BLOCKED (P6-G06, P9-G05 MT7612U).
- `closeout/REVIEW-2026-09-30.md` — lab review `CONDITIONAL_PASS`; this run does not revoke it.
- `ci/validate.sh` — static validation suite (not re-executed here on Linux; see 09).

## Reconciliation With Existing Verdicts

- Prior lab verdict `CONDITIONAL_PASS` (2026-09-30) is preserved.
- Prior production status `INSUFFICIENT_EVIDENCE` is preserved (not granted, not revoked).
- Delta introduced by this run: one new lab-scope P1 (enrollment revocation reset).
