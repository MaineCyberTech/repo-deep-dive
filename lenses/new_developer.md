# Lens — New Developer

## Purpose

Evaluate the program the way a competent stranger joining the team would experience it: can they understand it, set it up, operate it, and extend it **without tribal knowledge**?

This lens is an overlay. It does not repeat domain findings; it adds the onboarding-experience view and cross-references domain IDs.

## Area code

Findings from this lens use `ND`:

- `ND-P0-001`
- `ND-P1-001`
- `ND-P2-001`
- `ND-P3-001`

## When to apply

Targets per the falcon-lab profile: `01`, `09`, `10`, `12`, `16`, `19`, `21`, `32`, `41`, `42` (and both repos).

## Question set

1. Can a new developer get from a fresh checkout to a running development/test environment using **only in-repo documentation**? Which steps rely on undocumented host state, personal credentials, or session history?
2. What is the intended reading order (README → AGENTS.md → REPOSITORY.md → runbooks)? Is it stated anywhere, and is it correct?
3. Which terms are used without definition (feeds, gates, rebind, pairing, R2, EVE, ISM, doctrine, ledger)? Where is the glossary?
4. What implicit knowledge exists only in chat/transcripts rather than the repo?
5. Walk the documented quickstart **literally, step by step**: where does a newcomer get stuck, and what do the errors look like?
6. Are failure messages actionable (what failed, why, what to do next)?
7. How does a newcomer run tests and validation locally? Which commands are safe, and which are destructive or disruptive?
8. Are dangerous scripts clearly labeled (in filename, header comment, and docs) with their blast radius?
9. What is the contribution flow (branch, commit, review, gates, evidence)? Is it documented end-to-end?
10. What would a newcomer's first-week tasks be, and does the repo actually support them?
11. Where do they find credentials/secrets needed to work, and is that handled safely?
12. If the original author disappeared tomorrow, what breaks first — and what would the newcomer do about it?
13. Are there "works on my machine" elements (absolute paths, user-specific configs, shell assumptions)?
14. Does the onboarding path differ between the central and edge programs, and is that difference explained?

## Evidence expectations

- Cite the exact doc, script, or config a newcomer would hit, with path (and line where possible).
- For "gets stuck" claims, quote the actual command/output shape or the missing step.
- Distinguish *documented but wrong* from *undocumented but discoverable* from *undocumented and blocking*.

## Output shape

Write `lens_new_developer.md` in the run folder using the shared report structure, with:

- A short "onboarding walkthrough" section (the literal journey, step by step, with friction points).
- Findings in the shared finding format with area `ND`.
- A cross-reference table: `ND-ID ↔ related domain ID`.

## Traps to avoid

- Do not confuse "I know how this works" with "a newcomer could learn this from the repo".
- Do not file style nits as findings; onboarding blockers and hidden knowledge only.
- Do not re-file a domain finding; cross-reference it.
