# Verification log — bench-test full-domain run

- Run: `bench-test-20261013-0819-full-main-b916709`
- Pinned target: `bench-test` @ `b9167095` (VERSION 1.11.3), branch `main`
- Scaffolded: 2026-10-13T08:19Z · mode: full (43 domains)

## Target drift observed during the audit

The target checkout **moved while the 43 domain subagents were running**:

- `2026-10-13 04:28 local (08:28Z)` — rebase finished: HEAD `72c18734` (VERSION 1.11.4),
  including `a3dc49b8 fix(security): the audit's high findings - key leak, root code exec, ...`
- `2026-10-13 04:37 local (08:37Z)` — `git pull --ff-only` → HEAD `60ab90eb` (VERSION 1.11.5)
- At close-out: HEAD `60ab90eb`, VERSION 1.11.5, with 3 uncommitted files
  (`bench/benchreport.py`, `bench/run_win.py`, `tests/test_update.py`).

Early domains (e.g. `24_access_control_matrix_audit`) explicitly recorded the mismatch and
excluded findings already closed by `a3dc49b8`; later domains read the newer tree. The pinned
commit `b9167095` was rewritten by the rebase and is no longer an ancestor of HEAD.

## Consequence / status

- The run is **bound to `b9167095`** but its evidence spans `b9167095` → `60ab90eb`.
- Findings may be **stale** relative to `60ab90eb`; the release gate (NO-GO, P0 x6) must be
  re-checked at one fixed commit before remediation.
- **No finding here is `verified-fixed`.** Recommendation: re-run the owning domains against a
  pinned `60ab90eb` worktree (or re-init the run at that commit) before acting on the register.

## Verification performed

- `tools/deterministic_checks.py C:\temp\bench-test --deep` → 5 DET findings (emitted as domain `deterministic`).
- 43/43 domains emitted; `tools/collect_findings.py <run> --write` → **274 findings**
  (P0 x6, P1 x47, P2 x138, P3 x83).
- `tools/check_run.sh runs/bench-test-20261013-0819-full-main-b916709` → **PASS**.
- Read-only against the target; no writes to `C:\temp\bench-test`.
