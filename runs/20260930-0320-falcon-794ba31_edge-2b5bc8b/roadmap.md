# Audit Remediation Roadmap — falcon-lab run `20260930-0320-falcon-794ba31_edge-2b5bc8b`

Items are the finding IDs from the lens reports. Post-audit notes reflect remediation known at conversion time (details in `follow_up_register.md`); they do not close a finding — only a verification pass does.

## Immediate / Release Blocking (P0)

| ID | Action | Post-audit note |
|---|---|---|
| INTG-P0-001 | Version manifest names; re-pin to a stable edge release; add cross-repo drift check | Rebind work landed (`095c3e0`, `24a57eb`, `5b9f232`); pin corrections still tracked |
| INTG-P0-002 | Make WG peer persistence real; non-destructive re-render; regression check | Peer preservation + `wg syncconf` + regression check landed; verify |
| LIVE-P0-001 | Fix `.env` quoting; re-run offsite; add success/freshness alert | `.env` quoted; offsite re-run performed; alert presence to verify |
| LIVE-P0-002 | Confirm new-services archive contents; fix verification; alert | Script fix landed (`1f76aca`); verification pending |
| LIVE-P0-003 | EVE housekeeping; retention/offload decision; <15 GiB warning | Rotation + guard prune landed (`c5755f5`, `f1db6d8`); warning alert pending |
| LIVE-P0-004 | Widen/re-anchor TLS-silence rule; rename | Tuned to 6 h (`d83f421`); verify noise drop |

## This Week (P1)

**Security (edge):** `REV-P1-004` (enrollment→operator), `REV-P1-005` (update-apply root trust), `REV-P2-007` (hostname/CA separation) — plus `ND-P1-003` (dangerous tooling) on the falcon side.

**Verdict/records:** `REV-P1-001`, `REV-P1-002`, `REV-P1-003`, `REV-P1-006` — reconcile artifacts with the verdict; produce/obtain the reviewer artifact; disambiguate JPB; regenerate the edge response.

**Integration:** `INTG-P1-001` (edge alert coverage), `INTG-P1-002` (worktree execution), `INTG-P1-003` (offsite edge PKI), `INTG-P1-004` (skew freeze/re-pin/push).

**Onboarding:** `ND-P1-001`, `ND-P1-002`, `ND-P1-004`, `ND-P1-005`.

**Live ops:** `LIVE-P1-001` (root LV), `LIVE-P1-002` (monitor freshness), `LIVE-P1-003` (peer visibility), `LIVE-P1-004` (alert hygiene), `LIVE-P1-005` (snapshot/rehearsal), `LIVE-P1-006` (runbooks), `LIVE-P1-007` (external dead-man).

## This Month (P2)

- **Onboarding/docs (falcon):** `ND-P2-001`–`ND-P2-011`
- **Edge program:** `ND-P2-012`–`ND-P2-018`, `REV-P2-004`, `REV-P2-005`, `REV-P2-006`
- **Reviewer/records:** `REV-P2-001`, `REV-P2-002`, `REV-P2-003`
- **Integration:** `INTG-P2-001`–`INTG-P2-005`
- **Live ops:** `LIVE-P2-001`–`LIVE-P2-005`

## This Quarter (P3)

- **Falcon hygiene:** `ND-P3-001`–`ND-P3-007`, `REV-P3-001`–`REV-P3-003`
- **Edge hygiene:** `ND-P3-008`–`ND-P3-011`, `REV-P3-004`–`REV-P3-012`
- **Integration hygiene:** `INTG-P3-001`–`INTG-P3-004`
- **Structural:** CI drift checks (doc↔ledger, pin↔delivery), generated current-state block, exception-register status summary, catalogue generation.

## Later

- First **full domain run** (all applicable prompts 00–43) once P0/P1 are closed — this lens-focused run covers the lenses; domains are still un-audited as domains.
- CI drift checks to prevent recurrence of the ND-P1-001/002 class.
- Re-run synthesis (`22`, `23`, `40`) after remediation; then a verification-only pass for every fixed finding.

## Deferred / Accepted Risks (owner decisions)

- SSH password auth remains enabled (`EX-01`) — owner-accepted; fail2ban active.
- ntfy relay runs on the monitored host (`EX-22` residual) — accepted with independent ntfy domain.
- Unencrypted secrets backups in the delivery dir (`REV-P3-010`, `INTG-P2-003`) — accept with explicit risk entry, or encrypt.
- Exceptions expiring 2026-12-31 (`EX-01/02/03/11–16/18/20–23`): schedule the pre-expiry review; clean up PENDING/ACCEPTED duplicate rows (`ND-P3-005`).
- Third-party outside-in scan never performed (`P7-G02` limitation) — schedule or formally accept.
