# Lens — Security Adversary

## Purpose

Evaluate the system the way an attacker with a foothold — or an authorized-but-curious insider — would: turn lower-trust positions into higher-privilege outcomes, chain weaknesses, and break the strongest security claims. Safe, lab-confined reproduction only.

This lens is an overlay. It does not repeat domain findings; it adds the adversarial view and cross-references domain IDs.

## Area code

Findings from this lens use `ADV`:

- `ADV-P0-001`
- `ADV-P1-001`
- `ADV-P2-001`
- `ADV-P3-001`

## When to apply

Targets per the falcon-lab profile: `06`, `24`, `36`, `38`, `41`, `42`, `43` — and anywhere the security prompts produced PASS-like statements that were not independently challenged.

## Question set

1. Enumerate the **trust ladder**: what positions exist (anonymous, device/enrollment token holder, agent process, service account, operator, root/host) and what each can reach.
2. For each step up the ladder, find a path: what does the lower position control that a higher position trusts (files, requests, certificates, configs, queues, identifiers)?
3. Challenge the strongest claims first: "mTLS prevents", "signed manifest prevents", "read-only", "isolated". What would falsify each, and can it be tested safely?
4. Where are identity/role decisions made from attacker-supplied strings (names, subjects, headers, paths) rather than unforgeable attributes?
5. Which privileged components consume unprivileged input (agent-written files → root service; webhook payload → worker; uploaded archive → extractor)?
6. What does a leaked token/key actually unlock, and for how long? Are there short-lived, revocable credentials?
7. What chains two medium weaknesses into one high-impact outcome?
8. What is the blast radius of a single compromised component (sensor, agent, operator laptop, CI runner)?
9. Are negative tests present for each claimed control (forged input, wrong role, replay, symlink, path traversal)?
10. What does the system log or alert on for the attacks above — would any of them be noticed?

## Evidence expectations

- Reproduce in an isolated sandbox where possible (temporary directories, local fixtures, test databases); never against live systems.
- For each attempted path: state the exact input, the observed result, and whether the control held or failed.
- If reproduction is unsafe or impossible, mark `unverified` with the precise missing piece.

## Output shape

Write `lens_security_adversary.md` in the run folder using the shared report structure, with:

- A **trust-ladder table**: position · can reach · step-up paths found · controls that held.
- Findings in the shared finding format with area `ADV`.
- A cross-reference table: `ADV-ID ↔ related domain ID`.

## Traps to avoid

- Do not run exploits against live systems — sandbox or don't run.
- Do not equate "no CVE-style bug" with "no path"; logic and trust errors are the target.
- Do not re-file domain findings; cross-reference them.
- Do not print secret values while testing boundaries.
