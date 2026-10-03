# Lens — Live Operations

## Purpose

Evaluate the running system the way the **operator experiences it**, especially at 3am: what do they see, what alerts them, what do they do, and what happens in degraded modes. Configuration proves intent; this lens looks for what is actually true on the live host.

This lens is an overlay; cross-reference domain IDs instead of re-filing domain findings.

## Area code

Findings from this lens use `LIVE`:

- `LIVE-P0-001`
- `LIVE-P1-001`
- `LIVE-P2-001`
- `LIVE-P3-001`

## When to apply

Targets per the falcon-lab profile: `06`, `13`, `14`, `15`, `30`, `32`, `33`, `43` (and the live stack where read-only).

## Question set

1. Walk the operator's real journey: what do they see on a normal day, what wakes them up, and what do they actually do first?
2. Do alerts fire on real problems — and **only** on real problems? Quantify noise if evidence exists (alert counts, repeats, silences).
3. Do dashboards show the truth, or do they show stale/empty panels nobody noticed? Which panels are broken?
4. Are the runbooks executable **as written**? Do the commands exist, with the right paths and permissions, and do they work today?
5. What happens in each degraded mode: disk full, feed down/stale, tunnel down, backup failing, certificate near expiry, DNS down, host reboot?
6. Is the backup/restore path actually exercised (restore verified), not just configured? When was the last real restore?
7. What is the recovery time for each failure class, and is it documented with evidence?
8. What would the operator **not notice until it is too late** (silent failures, no alert, no dashboard, no log)?
9. Where are the gaps between "monitored" and "actually working"? Is the monitoring of the monitoring covered?
10. What is the weekly maintenance burden (manual steps, pruning, checks) and is it sustainable without the original author?
11. Are there recurring incidents/patterns, and did fixes actually stick?
12. What does the operator need that the system does not yet give them (top three)?

## Evidence expectations

- Prefer live, read-only observations: service status, versions, alert history, dashboard state, logs, disk, tunnel state. Timestamp everything.
- For "runbook works" claims, run the read-only commands (or state precisely why not).
- For degraded-mode claims, use evidence from config/code when a live drill is not sanctioned; label the difference clearly.

## Output shape

Write `lens_live_operations.md` in the run folder using the shared report structure, with:

- A **degraded-mode matrix**: failure class · detection · alert? · runbook? · recovery time · silent gap.
- Findings in the shared finding format with area `LIVE`.
- A cross-reference table: `LIVE-ID ↔ related domain ID`.

## Traps to avoid

- Do not restart, reconfigure, or "quickly test" anything on the live host — read-only means read-only.
- Do not confuse "configured" with "exercised".
- Do not re-file domain findings; cross-reference them.
