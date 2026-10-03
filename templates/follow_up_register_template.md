# Follow-Up Register — {run}

Tracker for all findings. Status is audit-time; post-audit notes never close a finding — only artifact-backed verification does.

Legend — Owner: `{repo}` / `owner` / `ops`. Target: `immediate` / `this week` / `this month` / `this quarter`. Status: shared vocabulary (`open`, `partially-fixed`, `verified-fixed`, `still-open`, `regressed`, `owner-accepted`).

| ID | Sev | Owner | Owning prompt/lens | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| | | | | | `open` | |

## Verification plan

1. After each patch set: re-run the owning prompt/lens checks for the fixed findings.
2. Verification-only pass at the settled tree: evidence at the current commit per finding; statuses into `verification_log.md`.
3. Refresh the risk register, release gate, and changelog (`22`, `23`, `40`) after verification.
4. Findings never close by assertion: only by artifact-backed verification or recorded owner acceptance.

## Human decisions required

| # | Decision | Related findings |
|---|---|---|
| D1 | | |
