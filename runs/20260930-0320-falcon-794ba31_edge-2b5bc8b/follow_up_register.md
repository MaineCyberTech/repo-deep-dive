# Follow-Up Register — run `20260930-0320-falcon-794ba31_edge-2b5bc8b`

Tracker for all 90 findings. **Status is audit-time** (`open` = open at the audit); the post-audit note records remediation known at conversion time (2026-09-30) and never closes a finding — only a verification pass can do that.

Legend — Owner: `falcon`, `edge`, `both`, `owner` (human decision), `falcon/ops`. Target: immediate / this week / this month / this quarter.

| ID | Sev | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|
| INTG-P0-001 | P0 | both | immediate | open | Rebind work landed (`095c3e0`, `24a57eb`, `5b9f232`); pin corrections still tracked |
| INTG-P0-002 | P0 | falcon | immediate | open | Peer preservation + `wg syncconf` + regression check landed; verify |
| LIVE-P0-001 | P0 | falcon/ops | immediate | open | `.env` quoted; offsite re-run performed; alert presence to verify |
| LIVE-P0-002 | P0 | falcon | immediate | open | Script fix landed (`1f76aca`); root-log verification pending |
| LIVE-P0-003 | P0 | falcon | immediate | open | EVE rotation + disk-guard prune landed (`c5755f5`, `f1db6d8`); warning alert pending |
| LIVE-P0-004 | P0 | falcon | immediate | open | Rule tuned to 6 h (`d83f421`); verify noise drop |
| ND-P1-001 | P1 | falcon | this week | open | Digest derivation from ledgers landed (`93ea9c6`); verify |
| ND-P1-002 | P1 | falcon | this week | open | Partly addressed via digest derivation; AGENTS/README regeneration pending |
| ND-P1-003 | P1 | falcon | this week | open | Tooling fixes landed (mode restore; disruptive test flagged); verify |
| ND-P1-004 | P1 | falcon | this week | open | — |
| ND-P1-005 | P1 | edge | this week | open | — |
| REV-P1-001 | P1 | falcon | this week | open | Partly addressed via digest derivation (`93ea9c6`); generator/AGENTS updates pending |
| REV-P1-002 | P1 | owner | this week | open | Human actions: reviewer artifact + JPB disambiguation + owner authorization |
| REV-P1-003 | P1 | falcon | this week | open | — |
| REV-P1-004 | P1 | edge | this week | open | — |
| REV-P1-005 | P1 | edge | this week | open | — |
| REV-P1-006 | P1 | edge | this week | open | — |
| INTG-P1-001 | P1 | both | this week | open | — |
| INTG-P1-002 | P1 | edge | this week | open | — |
| INTG-P1-003 | P1 | both | this week | open | — |
| INTG-P1-004 | P1 | both | this week | open | Rebind partially addressed; edge repo ahead of remote (push pending) |
| LIVE-P1-001 | P1 | falcon | this week | open | — |
| LIVE-P1-002 | P1 | falcon | this week | open | — |
| LIVE-P1-003 | P1 | falcon | this week | open | — |
| LIVE-P1-004 | P1 | falcon | this week | open | — |
| LIVE-P1-005 | P1 | falcon | this week | open | — |
| LIVE-P1-006 | P1 | falcon | this week | open | — |
| LIVE-P1-007 | P1 | falcon/owner | this week | open | — |
| ND-P2-001 | P2 | falcon | this month | open | — |
| ND-P2-002 | P2 | falcon | this month | open | — |
| ND-P2-003 | P2 | falcon | this month | open | — |
| ND-P2-004 | P2 | falcon | this month | open | — |
| ND-P2-005 | P2 | falcon | this month | open | Companion mode-restore fix landed; port parameterization open |
| ND-P2-006 | P2 | falcon | this month | open | — |
| ND-P2-007 | P2 | falcon | this month | open | — |
| ND-P2-008 | P2 | falcon | this month | open | — |
| ND-P2-009 | P2 | falcon | this month | open | — |
| ND-P2-010 | P2 | falcon | this month | open | — |
| ND-P2-011 | P2 | falcon | this month | open | — |
| ND-P2-012 | P2 | edge | this month | open | — |
| ND-P2-013 | P2 | edge | this month | open | — |
| ND-P2-014 | P2 | edge | this month | open | — |
| ND-P2-015 | P2 | edge | this month | open | — |
| ND-P2-016 | P2 | edge | this month | open | — |
| ND-P2-017 | P2 | edge | this month | open | — |
| ND-P2-018 | P2 | edge | this month | open | — |
| REV-P2-001 | P2 | falcon | this month | open | Archive-verifier guard added (`789846b`); canonical-path rebind pending |
| REV-P2-002 | P2 | falcon | this month | open | — |
| REV-P2-003 | P2 | falcon | this month | open | — |
| REV-P2-004 | P2 | edge | this month | open | — |
| REV-P2-005 | P2 | edge | this month | open | — |
| REV-P2-006 | P2 | edge/owner | this month | open | Owner decision needed (P9-G04 disposition) |
| REV-P2-007 | P2 | edge | this month | open | — |
| INTG-P2-001 | P2 | both | this month | open | — |
| INTG-P2-002 | P2 | both | this month | open | — |
| INTG-P2-003 | P2 | edge | this month | open | — |
| INTG-P2-004 | P2 | falcon | this month | open | — |
| INTG-P2-005 | P2 | both | this month | open | — |
| LIVE-P2-001 | P2 | falcon | this month | open | — |
| LIVE-P2-002 | P2 | falcon | this month | open | — |
| LIVE-P2-003 | P2 | falcon | this month | open | — |
| LIVE-P2-004 | P2 | falcon | this month | open | — |
| LIVE-P2-005 | P2 | falcon/owner | this month | open | — |
| ND-P3-001 | P3 | falcon | this quarter | open | — |
| ND-P3-002 | P3 | falcon | this quarter | open | — |
| ND-P3-003 | P3 | falcon | this quarter | open | — |
| ND-P3-004 | P3 | falcon | this quarter | open | — |
| ND-P3-005 | P3 | falcon | this quarter | open | — |
| ND-P3-006 | P3 | falcon | this quarter | open | — |
| ND-P3-007 | P3 | falcon | this quarter | open | — |
| ND-P3-008 | P3 | edge | this quarter | open | — |
| ND-P3-009 | P3 | edge | this quarter | open | — |
| ND-P3-010 | P3 | edge | this quarter | open | — |
| ND-P3-011 | P3 | edge | this quarter | open | — |
| REV-P3-001 | P3 | falcon | this quarter | open | — |
| REV-P3-002 | P3 | falcon | this quarter | open | — |
| REV-P3-003 | P3 | falcon | this quarter | open | — |
| REV-P3-004 | P3 | edge | this quarter | open | — |
| REV-P3-005 | P3 | edge | this quarter | open | — |
| REV-P3-006 | P3 | edge | this quarter | open | — |
| REV-P3-007 | P3 | edge | this quarter | open | — |
| REV-P3-008 | P3 | edge | this quarter | open | — |
| REV-P3-009 | P3 | edge | this quarter | open | — |
| REV-P3-010 | P3 | edge | this quarter | open | — |
| REV-P3-011 | P3 | edge | this quarter | open | — |
| REV-P3-012 | P3 | edge | this quarter | open | — |
| INTG-P3-001 | P3 | falcon | this quarter | open | — |
| INTG-P3-002 | P3 | edge | this quarter | open | — |
| INTG-P3-003 | P3 | both | this quarter | open | — |
| INTG-P3-004 | P3 | edge | this quarter | open | — |

## Verification plan

1. After each patch set: re-run the owning prompt/lens checks for the fixed findings.
2. Verification-only pass at the settled tree: evidence at the current SHA per finding; verdicts `verified-fixed` / `partially-fixed` / `still-open` / `regressed` into `verification_log.md`.
3. Refresh risk register, release gate, and changelog (pack prompts `22`, `23`, `40`) after verification.
4. Findings never close by assertion: only by artifact-backed verification or recorded owner acceptance.

## Human decisions required (owner)

| # | Decision | Related findings |
|---|---|---|
| D1 | Reviewer artifact production + JPB disambiguation + owner authorization recording | REV-P1-002, REV-P1-003 |
| D2 | P9-G04 disposition (approve hard-reset approximation or return gate) | REV-P2-006 |
| D3 | Edge alert-rules deployment authorization | INTG-P1-001 |
| D4 | Retention vs R2 cold-offload decision | LIVE-P0-003 |
| D5 | Secrets-backup encryption or explicit risk acceptance | REV-P3-010, INTG-P2-003 |
| D6 | Edge PKI offsite or explicit acceptance | INTG-P1-003 |
