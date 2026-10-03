# Lens — Independent Reviewer

## Purpose

Evaluate the program the way an independent reviewer (the one who signs the review or adoption) would: are the **claims** actually supported by the **evidence**, is the evidence reproducible, and is the independence real?

This lens is adversarial in method, not in tone: challenge the strongest claims first. It is an overlay; cross-reference domain IDs instead of re-filing domain findings.

## Area code

Findings from this lens use `REV`:

- `REV-P0-001`
- `REV-P1-001`
- `REV-P2-001`
- `REV-P3-001`

## When to apply

Targets per the falcon-lab profile: `22`, `23`, `32`, `33`, `34`, `35`, `41` (and the review/adoption records in both repos).

## Question set

1. For each headline claim (verdicts, `PASS`, `APPROVED`, "verified", "working", "closed"), what exact artifact backs it, and can the claim be reproduced from the repo alone?
2. Are there claims with **no artifact** — statuses that were asserted rather than earned?
3. Do any two artifacts contradict each other (doc vs ledger, README vs code, pin vs release), and is there a contradiction-ledger entry for each?
4. Are digests/checksums recomputable, and do they match the artifacts they describe?
5. Was the reviewer different from the author? Did the reviewer have access to the artifacts? Is that recorded (names, dates, scope)?
6. Are dates and sequence consistent (evidence predates verdict; fixes predate re-verification; review predates adoption)?
7. Are test/validation results traceable to a specific commit SHA?
8. Are findings marked "fixed" actually fixed **at the recorded commit** — or only claimed fixed?
9. Which claims are strongest, and which are weakest? What would a hostile reviewer attack first?
10. Are exceptions justified, owned, and time-bounded? Do they expire?
11. Is the evidence sample sufficient for the claim (e.g., spot-check N of M)? What was sampled vs asserted?
12. Are redactions consistent — nothing sensitive leaked into reports while still preserving reviewability?
13. Does any record reference external state (live host, remote, delivery dir) that cannot be verified later? Is that noted?

## Evidence expectations

- For each sampled claim: quote the claim, cite the artifact, and state `supported` / `partially supported` / `unsupported` / `not reproducible`.
- Capture reproduction commands where safe and read-only; otherwise state the exact gap.
- Name names only as recorded in the repo (reviewer/approver roles), never invent identities.

## Output shape

Write `lens_independent_reviewer.md` in the run folder using the shared report structure, with:

- A **claim sample table**: claim · artifact · reproduction result · verdict.
- Findings in the shared finding format with area `REV`.
- A cross-reference table: `REV-ID ↔ related domain ID`.

## Traps to avoid

- Do not equate "documented as passed" with "independently verified".
- Do not accept self-attestation as evidence.
- Do not re-file domain findings; cross-reference them.
- Do not print secret values while checking digests/redactions.
