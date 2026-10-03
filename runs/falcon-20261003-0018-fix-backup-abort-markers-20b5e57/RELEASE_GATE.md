# Release Gate

## Audit Metadata

- Audit name: repo-deep-dive — Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` @ `20b5e57` (branch fix/backup-abort-markers)
- Generated at: 2026-10-03 — Gate authority: advisory audit opinion only; never overrides a program verdict.

## Decision

**NO-GO** for any production-readiness claim. **GO WITH CONDITIONS** for continued lab operation.

Rationale: the release-integrity defect (FINAL-P0-001, HYG-P0-001/002) means the delivered package is not bound to the audited commit, so no production-readiness claim can be substantiated. Lab operation may continue under the conditions below. The commit's abort-marker fix is a genuine but partial improvement.

## Conditions

### Must close before a production-readiness claim

- **C0 — Release integrity.** Rebuild the review package at a frozen commit; regenerate `closeout/FINAL_RESPONSE.json` and `PACKAGE_DIGEST.txt`; commit in the documented order; add a CI equality test binding digest ↔ closeout ↔ package manifest ↔ HEAD; confirm `verify_publication_chain.sh` returns 0 in a full clone. (FINAL-P0-001, HYG-P0-001/002, HYG-P1-001)

### Conditions for continued lab operation (this week)

- **C1 — Abort/retry.** Fix the abort-marker contract (clear only on clean completion; write on failure exits); extend the trap to offsite/cold-copy/indexer/restore; add retry/backoff with a dead-letter and alert. (ARCH-P1-002, ARCH-P2-005, FEAT-P2-002)
- **C2 — Observability.** Make monitoring-death detection independent of the node-exporter textfile; add per-path relay delivery metrics. (OBS-P0-001, OBS-P1-003)
- **C3 — Capacity/data.** Set Wazuh/IRIS retention and alarm on growth. (DATA-P1-001)
- **C4 — Exposure edges.** Narrow the blanket `wg0` accept; fence the OpenCanary decoy ports; reconcile the inbound-mode state and record it. (SEC-P1-001/002/003)
- **C5 — Supply chain.** Close the digest-gate scope hole (`mct/compose`, `automation/wazuh`); gate vulnerabilities (`--require-vuln`). (SUPPLY-P1-001/002)
- **C6 — Evidence/CI.** Make the pairing contract verifiable from a clone; enable required checks where the plan allows. (API-P1-001, CI-P1-002)

## Reconciliation With Existing Verdicts

- The repository records a program production verdict **APPROVED (2026-09-29)** (`docs/phase9/review/PRODUCTION_VERDICT.md`) and prior audit opinions.
- This run **does not revoke** that verdict. It reports deltas at `20b5e57`: the abort-marker fix is a genuine improvement, while the release-integrity and resilience gaps persist.
- Honest delta: the operational bytes are improving (abort markers, CI gates); the delivered bytes are still not provably bound to the reviewed commit.

## Advisory Risk Score

`100 - (P0×40 + P1×10 + P2×3)` = `100 - (4×40 + 20×10 + 18×3)` = `100 - 314` → clamp `0`. Advisory only.

## Validation Commands

- `python C:\temp\repo-deep-dive\tools\collect_findings.py <run> --write --update-manifest`
- `python C:\temp\repo-deep-dive\tools\risk_score.py <run>`
- `bash C:\temp\repo-deep-dive\tools\check_run.sh <run>` — must print PASS
- In-repo: `python ci/validate.py`; `bash automation/validation/verify_publication_chain.sh`

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which commit is the true delivered tree? | Approval binding | reviewer-produced artifact |
| Current `/srv/falcon/compose-state/inbound-mode`? | Live exposure | host read |
| Will GitHub plan allow required checks? | Governance | owner decision |
