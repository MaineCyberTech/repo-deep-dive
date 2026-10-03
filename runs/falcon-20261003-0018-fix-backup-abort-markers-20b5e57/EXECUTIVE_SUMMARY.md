# Executive Summary

- **Repository:** `falcon` (`C:\temp\falcon`)
- **Branch / commit:** fix/backup-abort-markers @ `20b5e57`
- **Run:** 20261003-0018-fix-backup-abort-markers-20b5e57
- **Profile:** base
- **Findings:** 46 (P0 ×4, P1 ×20, P2 ×18, P3 ×4)
- **Gate:** NO-GO for a production-readiness claim; GO WITH CONDITIONS for continued lab operation (`RELEASE_GATE.md`).

## What changed in this commit

`20b5e57` adds an abort trap to `bootstrap/lib.sh` that writes a durable marker on SIGTERM/SIGINT and exits 130, installs it in `bootstrap/85-backup-job.sh`, and adds `automation/validation/tests/abort_marker_test.sh` (auto-discovered by `ci/validate.py`). It is a real improvement, but:
- the marker is cleared at the *start* of the next run, contradicting the comment that it is cleared only on clean completion, and normal failure exits (`exit 1`) leave no marker at all;
- only the backup job installs the trap; offsite, cold-copy, indexer-backup and restore do not.

## Top risks

1. **P0 — Release integrity.** `PACKAGE_DIGEST.txt` names commit `b595354f` and `closeout/FINAL_RESPONSE.json` names `605fc100`; neither is the audited HEAD `20b5e57`. The delivered bytes are not provably the reviewed bytes, so no production-readiness claim can be substantiated. (FINAL-P0-001, HYG-P0-001/002)
2. **P0 — Observability SPOF.** Prometheus scrapes only 3 targets; nearly all `falcon_*` signals come from the node-exporter textfile collector, so one exporter failure can blind alerting. (OBS-P0-001)
3. **P1 — Resilience.** Graceful-stop/abort markers incomplete, no retry/backoff for offsite. (ARCH-P1-002, ARCH-P2-005, FEAT-P2-002)
4. **P1 — Exposure.** Blanket WireGuard accept, OpenCanary decoy ports on all interfaces, contradictory inbound state. (SEC-P1-001/002/003)
5. **P1 — Data lifecycle.** Wazuh/IRIS have no retention on the shared data LV. (DATA-P1-001)
6. **P1 — Supply chain.** The digest gate only scans `compose/`; vulnerabilities are not gated. (SUPPLY-P1-001/002)
7. **P1 — Pairing.** The edge pairing contract cannot be verified from a clone. (API-P1-001)
8. **P1 — Governance.** Branch protection is plan-blocked; governance relies on the owner label gate. (CI-P1-002)

## Strengths

- Evidence-first doctrine with append-only ledgers and raw captures.
- Pinned images (`tag@digest`), SHA-pinned Actions, hash-pinned CI tools.
- Strong static CI gate (13 checks) with a fail-closed secret history scan and drift gates.
- Extensive runbooks and a current-state page.
- The new abort-marker regression test is wired into CI.

## Immediate actions

1. Rebuild/rebind the delivery chain and add the digest↔closeout↔manifest↔HEAD equality test.
2. Fix the abort-marker contract and extend the trap to all long-running jobs.
3. Make monitoring-death detection independent of the textfile.

## Reconciliation

This opinion neither grants nor revokes the repository's program production verdict (APPROVED 2026-09-29). It records deltas at `20b5e57` under a separate authority.
