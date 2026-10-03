# Release Gate — repo-deep-dive

**Verdict:** `GO WITH CONDITIONS`

- Run: 20261003-0018-main-7bac320
- Commit: worktree `6cada03` (recorded `7bac320`)
- Findings: P0 0 · P1 9 · P2 20 · P3 12 (41 total)
- Advisory score: 0/100 (`tools/risk_score.py`; advisory only)

## Rationale

No P0 exists: the pack holds no production data, no tenant boundary, and no running service, so there is no data-loss, tenant-exposure, or outage condition. However, nine P1 issues affect the trustworthiness and safety of the tools themselves (CI supply-chain execution, PAT exposure, a broken findings/manifest contract, and an unwired audit CI). The shared severity model reserves GO for "no P0/P1 blockers and validation evidence"; both are absent, so the gate is **GO WITH CONDITIONS**.

## Conditions (all required)

| # | Condition | Findings | Validation |
|---|---|---|---|
| 1 | Align `findings.json` and `audit_manifest.json` with their schemas/consumers | DATA-P1-001, DATA-P1-002, TEST-P2-003 | `new_run.py` scaffold passes `check_run.sh`; schema type validation green |
| 2 | Remove root remote-script execution; pin/checksum CI tools | SEC-P1-001, SUPPLY-P1-001, CI-P2-003 | pinned refs; corrupted download fails |
| 3 | Eliminate PAT-in-URL; mask token; gate secret scanning | SEC-P1-002, SEC-P2-003 | clone-failure log has no token; fixture secret fails |
| 4 | Wire the audit CI at `.github/workflows/` with correct path + PR trigger | CI-P1-001, CI-P1-002, CI-P2-005/006, TEST-P1-001 | lint/self-test run on PR; P0 fixture fails |
| 5 | Make the run gate strict by default / not bash-skippable | ARCH-P2-002 | no-bash run fails without `--no-check` |
| 6 | Provide evidence the toolchain/self-test ran at the audited SHA | FINAL-P2-001 | archived CI log with `RESULT: PASS` |

## Explicitly not blocking

- P2 architecture, docs-drift, observability, and determinism-integration items.
- P3 hygiene items (LICENSE, `.gitignore`, `.gitattributes`, digest completeness, sensitive archives).

## Reconciliation

Existing falcon-lab program verdicts are **not** modified. This gate is a pack-level audit opinion at the audited commit and does not grant or revoke any product gate.

## Sign-off

- Gate owner: `Unknown` (no CODEOWNERS; see EXEC-P2-001)
- Next review: after conditions 1–4 land, re-run the owning prompts and refresh this gate.
