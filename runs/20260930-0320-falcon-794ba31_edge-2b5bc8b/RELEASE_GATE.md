# Release Gate — audit opinion for run `20260930-0320-falcon-794ba31_edge-2b5bc8b`

## Decision

**GO WITH CONDITIONS**

This is the **audit opinion** on the state of the falcon lab (central + edge + shared host) as of the 2026-09-30 lens audits. It is not a program verdict: it does not revoke, replace, or grant one (see Reconciliation).

## Why

The lab's engineering substance is sound and the core pipeline is live and healthy; nothing found requires stopping operations. But six P0 conditions are open at audit time (silent backup regressions, disk trajectory, alert noise, pin integrity, tunnel persistence), the delivery's machine artifacts contradict the published verdict, the independence/adoption evidence is attestation-based, and the edge program carries two significant security weaknesses. These are all fixable within the existing processes — hence GO **with conditions**, not NO-GO.

## Conditions

| # | Condition | Findings | Done when |
|---|---|---|---|
| C1 | Offsite backup restored and alerted; new-services backup contents confirmed | LIVE-P0-001, LIVE-P0-002 | Fresh offsite inventory + passing new-services verification + failure alert fires |
| C2 | Disk trajectory controlled | LIVE-P0-003, LIVE-P1-001 | Free space stable over 7 days; warning band active before the 5 GiB guard |
| C3 | Alert path de-noised | LIVE-P0-004, LIVE-P1-004 | TLS-silence flap gone; catalogue matches live rules; real outages still alert |
| C4 | Edge release integrity restored | INTG-P0-001, INTG-P1-004, ND-P2-017, REV-P1-006 | Pinned digest resolves to a present artifact; deployed digest recorded; phase-10 test green; artifacts coherent |
| C5 | WG peer persistence made real | INTG-P0-002 | Bootstrap re-run preserves the edge peer; regression check green |
| C6 | Verdict artifacts reconciled | REV-P1-001, REV-P1-003 | Digest/response derive from ledgers; verdict document internally consistent |
| C7 | Independence/adoption resolved | REV-P1-002, REV-P2-005, REV-P2-006 | Reviewer artifact produced and digested; JPB disambiguated; owner authorization recorded; gate dispositions corrected — **or** explicit owner acceptance recorded |
| C8 | Edge security weaknesses fixed | REV-P1-004, REV-P1-005, REV-P2-007 | Negative tests fail the exploit paths; gates reopened and re-closed with evidence |
| C9 | Edge path monitored and backed up | INTG-P1-001, INTG-P1-002, INTG-P1-003 | Edge alert rules or probes live; deployed code pinned; PKI/DB offsite or owner-accepted |
| C10 | Verification pass complete | all fixed findings | `verification_log.md` marks each `verified-fixed`; register/gate/changelog refreshed |

## Reconciliation With Existing Program Verdicts

- **Central:** the program's own published verdict is **APPROVED** (2026-09-29), with a reviewer disposition and owner adoption. The audit does not revoke it. The audit's delta: the delivery's machine artifacts (`PACKAGE_DIGEST.txt`, `FINAL_RESPONSE.json`, `AGENTS.md`) still deny the verdict (hard-coded), and the independence/adoption chain is a transcription rather than a separate artifact. Recommended reconciliation: regenerate the artifacts from the ledgers, produce the reviewer artifact (or record an explicit owner acceptance of the attestation basis), and correct the verdict document's self-contradictions. The lab implementation itself is substantially supported.
- **Edge:** the program's own review disposition is **CONDITIONAL_PASS for lab review gates; production readiness INSUFFICIENT_EVIDENCE**. The audit concurs and adds specific conditions (C4, C8, C9).
- Where audit conditions and program records differ, the difference is stated above with evidence pointers in the lens reports; the resolution path is the program's normal review/adoption flow, not this document.

## What this gate is not

- Not a revocation or grant of any program gate, verdict, review, or adoption.
- Not a substitute for the independent review or owner adoption.
- Not a full-domain audit: this run covered lenses; domains (including `41` EVID, `42` XREPO, `43` FLEET) are scheduled for the first full run after P0/P1 closure.

## Path to GO

1. Complete C1–C9 with evidence (patch plan sets 1–2 first).
2. Run the verification-only pass (C10) at the settled tree.
3. Refresh this gate at the next synthesis; it becomes **GO** when all conditions verify.

## Path to NO-GO (triggers to revisit)

- Any P0 condition regresses or a new silent data-loss path is found.
- Disk exhaustion occurs before C2 lands.
- A confirmed exploit of REV-P1-004/005 in the live environment.
- The independence/adoption question remains unresolved *and* unaccepted beyond the next review cycle.
