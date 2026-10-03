# Final Risk Register, Roadmap, and Patch Plan

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: FINAL
- Output path: docs/audits/{name}/{run}/22_final_risk_register_roadmap.md
- Scope limitations: static/read-only; no live host, no bash.

## Scope

Aggregates the 44 domain findings from reports 01–21 into cross-cutting risks, a roadmap and a patch plan. The run-wide machine register is `risk_register.md`; this report adds the synthesized view and two `FINAL` findings.

## Evidence Reviewed

- Reports `01_*` … `21_*` in this run folder.
- `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json`.
- `docs/CURRENT_STATE.md`, `ledgers/risk_register.md`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| This run's domain reports | Findings | Aggregation | 44 domain findings |
| `PACKAGE_DIGEST.txt` vs HEAD | Artifact | Release integrity | mismatch |
| `git show 20b5e57` | Diff | Abort fix scope | script-level only |

## Executive Summary

The commit under audit makes a genuine but narrow improvement to backup interrupt safety. The repository does not, at this commit, support a production-readiness claim: the delivery digest/closeout are not bound to HEAD (release integrity), and the operational-resilience front (graceful stop across all jobs, retry/backoff, retention) remains open. Lab operation is reasonable under conditions. The two headline findings are `FINAL-P0-001` and `FINAL-P1-001`.

## Inventory

Not applicable (aggregate report).

## Findings

### Finding ID: FINAL-P0-001 - Production-readiness claim is unsupportable at this commit (release integrity)

- Severity: P0
- Confidence: High
- Area: FINAL
- Evidence:
  - `PACKAGE_DIGEST.txt` — commits `b595354f...`
  - `closeout/FINAL_RESPONSE.json` — commit `605fc100...`
  - `git rev-parse HEAD` → `20b5e57`
  - HYG-P0-001, HYG-P0-002 in this run
- What is happening: The delivered package, closeout and digest are not provably the audited bytes.
- Why it matters: No production-readiness claim can be substantiated until the chain is rebuilt and re-verified.
- User / business impact: Approval cannot be relied upon.
- Security / privacy / reliability impact: Release integrity failure.
- Recommended fix: Rebuild/rebind at a frozen commit and add the CI equality test (see HYG-P0-001).
- Suggested validation: `verify_publication_chain.sh` exits 0 from a full clone.
- Owner suggestion: owner
- Effort estimate: M
- Dependencies: review flow
- Status: open

### Finding ID: FINAL-P1-001 - Operational resilience remains incomplete across the backup lifecycle

- Severity: P1
- Confidence: High
- Area: FINAL
- Evidence:
  - ARCH-P1-002, ARCH-P2-005 — marker semantics gap; only one job has the trap
  - FEAT-P2-002 — no retry/backoff/dead-letter
  - DATA-P1-001 — Wazuh/IRIS have no retention
  - `docs/CURRENT_STATE.md` C7 — capacity partial
- What is happening: Graceful-stop, retry and retention are each partially addressed, and the gaps compose.
- Why it matters: A transient failure can silently miss a recovery point.
- User / business impact: Recovery assurance.
- Security / privacy / reliability impact: Reliability.
- Recommended fix: Sequence the C1-style resilience work: fix the marker contract, extend the trap, add retry/backoff, then retention.
- Suggested validation: Fault-injection drills.
- Owner suggestion: ops/resilience
- Effort estimate: L
- Dependencies: —
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unbound delivered bytes | P0 | High | High | digest vs HEAD | HYG-P0-001 |
| Observability SPOF | P0 | Medium | High | prometheus.yml | OBS-P0-001 |
| Incomplete abort/retry | P1 | Medium | High | lib.sh, 85-backup | ARCH-P1-002, FEAT-P2-002 |
| VPN host-wide trust | P1 | Medium | High | falcon.nft | SEC-P1-002 |
| No Wazuh/IRIS retention | P1 | High | High | CURRENT_STATE C7 | DATA-P1-001 |
| Unverifiable pairing | P1 | Medium | High | edge pin | API-P1-001 |
| Ungated supply chain | P1 | Medium | High | checker scope | SUPPLY-P1-001 |
| Unenforced branch protection | P1 | Medium | Medium | BRANCH_PROTECTION.md | CI-P1-002 |

## Recommendations

### Immediate / Release Blocking
1. FINAL-P0-001 release integrity (rebuild/rebind + CI equality test).
2. ARCH-P1-002 abort-marker contract.
3. OBS-P0-001 monitoring-death detection.

### This Week
4. ARCH-P2-005 extend trap; FEAT-P2-002 retry/backoff.
5. SEC-P1-002 wg0 narrowing; SEC-P1-001 fence decoys.
6. DATA-P1-001 Wazuh/IRIS retention.
7. SUPPLY-P1-001/002 supply-chain gates.

### This Month
8. SEC-P2-001 origin auth; API-P1-001 pairing verification.
9. OBS-P1-003 per-path relay metrics; ARCH-P2-001 redeploy hardening.
10. HYG-P1-001 package drift check.

### Later / Platform Evolution
11. ARCH-P1-001 warm standby; SEC-P2-003 rate-limit hardening; API-P2-002 mTLS.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix early marker clear | Restores crash-safety | `bootstrap/85-backup-job.sh` | extend abort test |
| Add `--require-vuln` | Gates CVEs | `.github/workflows/validate.yml` | CI |
| Bind digest to HEAD | Prevents release drift | `ci/validate.py` | equality test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Release rebind | P0 | owner | M | review flow |
| Marker contract fix | P1 | ops | S | — |
| Retry/DLQ | P1 | ops | M | — |
| Wazuh/IRIS lifecycle | P1 | data owner | M | decision |
| Supply-chain gates | P1 | supply-chain | M | — |
| Origin auth | P2 | ops | M | Access export |

## Suggested Tests

- Release-chain equality test (digest↔closeout↔manifest↔HEAD).
- Abort failure-exit marker test.
- Offsite retry fault-injection.
- `--require-vuln` planted-CVE fixture.

## Suggested Documentation Updates

- Refresh `docs/CURRENT_STATE.md` from the ledgers after rebind.
- Document the marker lifecycle accurately.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which commit is the true delivered tree? | Approval binding | release review artifact |
| Current inbound mode? | Live exposure | host state file |
| Plan upgrade for branch protection? | Governance | owner decision |

## Appendix

Run-wide severity/area rollup:

| Severity | Count |
|---|---:|
| P0 | 4 |
| P1 | 20 |
| P2 | 18 |
| P3 | 4 |
| **Total** | **46** |

| Area | Count |
|---|---:|
| INV | 2 |
| ARCH | 6 |
| FEAT | 2 |
| SEC | 6 |
| DATA | 2 |
| API | 3 |
| TEST | 3 |
| CI | 5 |
| SUPPLY | 5 |
| OBS | 4 |
| HYG | 5 |
| FINAL | 2 |
| EXEC | 1 |
