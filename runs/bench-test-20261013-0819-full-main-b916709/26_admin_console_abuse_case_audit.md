# 26_admin_console_abuse_case_audit — Prompt 26 - Admin Console Abuse Case Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `26_admin_console_abuse_case_audit.md` (area ADMIN, prompt)

## Verification Performed

# Admin Console Abuse Case Audit

## Audit Metadata

- Audit name: bench-test full-domain audit
- Run: 20261013-1200-main-72c1873
- Repository: `C:\temp\bench-test` (read-only)
- Branch: `main`
- Commit SHA: `72c18734aea2e5b3381254b74205d0b2944bafab` (working tree has uncommitted edits to README.md, docs/PHASE_TIMINGS.md, server/web/app.js, tests/test_dashboards.py). The domain brief named `b9167095…`; the checkout is two commits later (b9167095 → a3dc49b8 "fix(security)" → 72c18734). Findings below cite the on-disk tree.
- Generated at: 2026-10-13
- Auditor: domain subagent (26_admin_console_abuse_case_audit)
- Area code: ADMIN
- Output path: docs/audits/repo-deep-dive/20261013-1200-main-72c1873/26_admin_console_abuse_case_audit.md
- Scope limitations: read-only; no live lab/control-plane instance was touched beyond a local copy of `server/benchd.py` started on loopback for one reproduction.

## Scope

Reviewed the only admin/operator surface in the repository: the `benchd` control plane
(`server/benchd.py`), its web console (`server/web/app.js`, `index.html`, `style.css`), the
runner client that executes operator commands (`bench/agent.py`, `bench/benchreport.py`), the
live-USB runner config (`live/airootfs/…`), the control-plane docs, and the stdlib tests.

The target is a workstation benchmark/stress toolkit. There is **no** multi-tenant SaaS,
billing, user/org/role store, document/ticket system, webhook administration, approval workflow,
or impersonation feature. Those areas are not applicable and are called out as such below.

## Evidence Reviewed

- `server/benchd.py` (full read) — auth, routing, GET/POST/DELETE API, register, scheduler, reapers, static serving.
- `server/web/app.js` (targeted), `server/web/index.html` (full) — operator console actions, confirmations, token handling, downloads.
- `bench/agent.py` (command dispatch), `bench/benchreport.py` (`Reporter`, `run_exec`, `power_action`, `identity`/`machine_id`, `iso_write*`).
- `live/airootfs/etc/bench-agent.conf.example`, `live/airootfs/usr/local/bin/bench-agent-env` — where the runner credential lives.
- `server/benchd.conf.example`, `docs/CONTROL_PLANE.md`, `README.md`, `AGENTS.md` — documented auth/admin model.
- `tests/test_control_plane.py`, `tests/test_dashboards.py` — existing coverage.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline -3` / `git status --porcelain` | command | Establish exact audited revision | HEAD `72c1873`; 4 dirty files |
| `git show --stat a3dc49b8` | command | Understand the recent security fixes | Fixed runner_id takeover, static traversal, body cap, token log redaction; left machine_id adoption |
| Full read of `server/benchd.py` | read | Enumerate admin endpoints/auth | Single shared token; no audit table |
| `Select-String` over `app.js` for confirm/DELETE/exec/token | command | Locate destructive UI paths | Client-side confirmations only |
| Local copy of `server/` started on `127.0.0.1:8791` + `repro.py` | execution | Reproduce the self-privilege-escalation | Attacker bearer + `machine_id` of victim → 200 with victim `runner_id` + `api_key` (`TOOK OVER VICTIM ROW: True`, `RECEIVED VICTIM KEY: True`) |
| Read `live/…/bench-agent-env`, `bench-agent.conf.example` | read | Verify where BENCHD_TOKEN is stored | Writable FAT partition / image, root at boot |
| `Select-String docs/*.md README.md AGENTS.md` for audit/role/rate/confirm | command | Find any audit or role controls | None found; per-user accounts listed as roadmap |

## Executive Summary

The admin surface is the `benchd` control plane plus its single-page console. It is small,
dependency-free, and well commented. The strong points: per-runner API keys are issued at
registration and the API returns runners with `api_key` stripped (`benchd.py:419-453`), run
writes are scoped to the owning runner (`_may_write_run`, `benchd.py:607-615`), negative-number
and unknown-command inputs are rejected, request bodies are capped (`benchd.py:545-559`), and the
recent security commit fixed a runner-id takeover, a static-path traversal, and token-in-log
leakage.

The core abuse risk is **all-or-nothing privilege**: one shared `BENCHD_TOKEN` is simultaneously
the runner registration secret and the full operator bearer, and it is deployed onto every runner
machine (including a writable FAT USB partition). A holder of that secret can run arbitrary
shell commands (`exec`/`shell`), power off/reboot, raw-write disks (`iso_write`), and delete
runs/runners — with no roles, no server-side confirmation, no undo, and no audit trail. On top of
that, one enrolled runner can hijack another runner's identity by claiming its `machine_id` in
`/register` and is handed the victim's API key (reproduced). Recommended first actions:
separate the join secret from the operator credential and stop shipping the operator secret to
runners; close the `machine_id` adoption hole; and add an append-only audit log.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Admin API server | `server/benchd.py` | REST+SSE control plane | Implemented | P1/P2 | Single-tier operator token |
| Operator console | `server/web/app.js` | Start/stop/exec/power/ISO/delete | Implemented | P2 | Confirmations client-side only |
| Runner registry / identity | `server/benchd.py:1163-1218` `_register` | Issue per-runner keys; adopt by machine_id | Implemented | P1 | Identity takeover hole |
| Command issuance | `server/benchd.py:1220-1232` `_issue_command` | exec/shell/shutdown/reboot/iso_* | Implemented | P1/P2 | No approval, no actor |
| Run/runner/schedule delete | `server/benchd.py:653-681` | Remove data | Implemented | P2 | Irreversible, unaudited, no confirm |
| Scheduler | `server/benchd.py:1234-1251`, `1277-1312` | Recurring runs | Implemented | P3 | Delete has no confirm in UI |
| Audit log | — | Attribute privileged actions | **Absent** | P2 | No table, no actor |
| Roles / users / orgs | — | RBAC | **Absent** | P1 | Roadmap item `CONTROL_PLANE.md:275` |
| Settings / approval / impersonation | — | — | **Not applicable** | — | No such features |
| Exports | `benchd.py:885-913` CSV/artifact | Download data | Implemented | P2 | Token in URL; no access log |
| Webhook admin | — | — | **Not applicable** | — | No webhooks |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Admin pages/APIs | 3 | Console + full REST/SSE (`app.js`, `benchd.py`) | Single shared token, fail-open | Split secrets, fail closed |
| User/org/role management | 0 | No user/role tables (`SCHEMA benchd.py:94-143`) | Absent | Add per-user accounts + roles |
| Billing panels | 0 | Not applicable | — | None |
| Document/ticket admin | 0 | Not applicable | — | None |
| Webhook/API key admin | 2 | Per-runner keys (`_register`), no rotation/revocation UI | No key lifecycle | Add rotation/revocation |
| Bulk ops | 2 | Per-runner commands only; no bulk UI | None exists/no preview needed | Keep single-target, or add preview if bulk added |
| Approval flows | 0 | Absent | No approval for destructive ops | Add confirm/approval for P1 actions |
| Impersonation | 0 | Absent | — | None (runners cannot impersonate operators) |
| Settings | 1 | Config via flags/env only (`benchd.py:1401-1433`) | No UI, fail-open default | Fail-closed config |
| Exports | 2 | CSV/artifact download (`benchd.py:885-913`) | Token in URL, no audit | Scoped download tokens + audit |
| Destructive actions | 2 | DELETE endpoints, power/ISO commands | Ungated, irreversible | Server-side confirm + undo |
| Confirmations | 2 | UI-only (`app.js:1353,1363,1404-1437`) | Inconsistent, bypassable | Shared confirm component |

## Detailed Review

### Item: Operator authentication and privilege model

- Evidence: `server/benchd.py:14-25`, `:562-615`, `:1428-1441`; `server/benchd.conf.example:4-6`; `live/airootfs/etc/bench-agent.conf.example:11`.
- What it does: one token (`BENCHD_TOKEN`) doubles as the runner join token and the operator bearer; runners receive per-runner `api_key`s after registration.
- Current controls: bearer/`?token=` checks; per-runner run-write scoping; constant-time compare on the bearer path.
- Missing controls: role separation; distinct join vs operator secrets; token lifetime/rotation; rate limiting.
- Risks: any holder of the shared secret has full fleet power.
- Recommended improvement: separate secrets + per-user scopes; never deploy the operator token to runners.
- Suggested tests: assert a runner key cannot reach operator routes and that an operator token is not required to register with a distinct join token.

### Item: Runner identity adoption (`POST /register`)

- Evidence: `server/benchd.py:1190-1217`; `tests/test_control_plane.py:46-71`.
- What it does: a re-registering runner (or ephemeral live-USB boot with no persisted config) reclaims its row by `machine_id`+`kind`+`instance`, and the response returns that row's `api_key`.
- Current controls: the `runner_id` path requires the row's own key/operator (tested); the `machine_id` path requires nothing.
- Missing controls: proof that the caller owns the claimed `machine_id`.
- Risks: identity takeover + key disclosure (reproduced, see Findings).
- Recommended improvement: bind `machine_id` to the issuing key; require operator/per-machine proof to adopt.
- Suggested tests: mirror `test_control_plane.py:46-71` but claim `machine_id`.

### Item: Audit logging

- Evidence: `server/benchd.py:94-143` (no audit table), `:653-681` (deletes), `:1220-1232` (commands), `:885-913` (exports).
- What it does: records every command (kind/payload/status) in `commands`, but no actor and no immutable trail.
- Missing controls: an append-only log of privileged/delete/export actions.
- Recommended improvement: add an `audit` table and write to it from every mutating handler.
- Suggested tests: issue a delete/exec and assert an audit row with actor+target exists and survives target deletion.

### Item: Destructive actions and confirmation

- Evidence: `server/benchd.py:1220-1232`, `:665-680`; `server/web/app.js:1353,1363,1404-1437,1702-1704`.
- What it does: the API accepts power/ISO/exec/DELETE; the browser adds `confirm()`/checkbox prompts.
- Missing controls: server-side confirmation, undo/soft-delete, consistent prompts.
- Recommended improvement: server-enforced confirmation + undo window.

### Item: Remote terminal (`exec`/`shell`)

- Evidence: `server/benchd.py:1223-1225`; `bench/agent.py:273-276`; `bench/benchreport.py:811-820`, `:573-575`.
- What it does: runs arbitrary shell as the runner's OS user (root on the live USB) and streams output only while a run is active.
- Missing controls: approval, allowlist, rate limit, output retention when idle.
- Recommended improvement: privileged-role gating, persistent output, optional allowlist.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ADMIN-001 | Admin pages/APIs | `benchd.py`, `app.js` | Token gate | Shared token, fail-open | P1/P2 | Split secrets, fail closed |
| ADMIN-002 | User/org/role management | no tables | None | Absent | P1 | Add RBAC |
| ADMIN-003 | Billing panels | n/a | n/a | Not applicable | — | None |
| ADMIN-004 | Document/ticket admin | n/a | n/a | Not applicable | — | None |
| ADMIN-005 | Webhook/API key admin | `_register` | Per-runner keys | No rotation/revocation | P2 | Add key lifecycle |
| ADMIN-006 | Bulk ops | `_issue_command` (single target) | Per-runner only | No bulk surface to preview | P3 | Keep single-target |
| ADMIN-007 | Approval flows | none | None | Absent | P2 | Confirm/approve destructive ops |
| ADMIN-008 | Impersonation | `_register` adoption | None | Runner identity takeover | P1 | Prove ownership |
| ADMIN-009 | Settings | flags/env | None | Fail-open default | P2 | Fail closed |
| ADMIN-010 | Exports | `benchd.py:885-913` | Token in URL | No scoped token, no audit | P2 | Scoped tokens + audit |
| ADMIN-011 | Destructive actions | `benchd.py:1220-1232,665-680` | Operator token | Ungated, irreversible | P2 | Server-side confirm + undo |
| ADMIN-012 | Confirmations | `app.js` | Client-side only | Inconsistent, bypassable | P2/P3 | Shared confirm component |

## Findings

### Finding ID: `ADMIN-P1-001` - Shared all-powerful operator token is distributed to every runner

- Severity: P1
- Confidence: High
- Area: ADMIN
- Evidence:
  - `server/benchd.conf.example:4-6` (`BENCHD_TOKEN` is "Shared bearer token for runners + the web UI")
  - `server/benchd.py:14-25`, `:572-580` (join token == operator bearer; full operator surface)
  - `server/benchd.py:1223-1225` (operator may issue exec/shell/shutdown/reboot/iso_write)
  - `live/airootfs/etc/bench-agent.conf.example:11`, `live/airootfs/usr/local/bin/bench-agent-env:26-50` (token shipped to / read from the stick, including a writable FAT partition)
  - `docs/CONTROL_PLANE.md:204-207`, `:275`
- What is happening: one secret is both the registration token handed to every runner and the highest-privilege credential.
- Why it matters: trust-boundary collapse — a low-trust runner host (or its removable config) holds fleet-admin power.
- User / business impact: compromise of any single runner yields fleet-wide control; no accountability.
- Security / privacy / reliability impact: remote code execution, power control, raw-disk writes, data deletion fleet-wide.
- Recommended fix: split join vs operator secrets; keep the operator secret off runners; per-user accounts/roles; rotation.
- Suggested validation: test that the join token cannot call operator routes and that runners never persist the operator token.
- Owner suggestion: control-plane maintainer
- Effort estimate: M
- Dependencies: per-user accounts (roadmap `CONTROL_PLANE.md:275`)
- Status: open
- Endpoint / data path: `POST /api/v1/runners/<id>/commands` (operator token) → queued `commands` row → runner poll → `exec`/`power_action`/`iso_write`.

### Finding ID: `ADMIN-P1-002` - Runner identity takeover via machine_id

- Severity: P1
- Confidence: High
- Area: ADMIN
- Evidence:
  - `server/benchd.py:1190-1203` (adoption on caller-supplied `machine_id`, no proof), `:1215-1217` (returns that row's `api_key`)
  - `tests/test_control_plane.py:46-71` (runner_id path tested, machine_id path not)
  - Reproduced at the audited commit: attacker bearer + `{"machine_id":"dmi-VICTIM"}` → HTTP 200 with victim `runner_id` + `api_key`.
- What is happening: any enrolled runner can claim another runner's row by `machine_id`.
- Why it matters: cross-runner identity seizure and API-key disclosure; the attacker then receives operator commands (incl. exec) meant for the victim.
- Security impact: identity spoofing of an enrolled runner; lateral command interception.
- Recommended fix: require proof of ownership for adoption; never echo an existing key without proof; add regression test.
- Suggested validation: the mirrored test above.
- Owner suggestion: control-plane maintainer
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: `POST /api/v1/register` → `runners` row adoption → leaked `api_key`.

### Finding ID: `ADMIN-P2-003` - No audit trail for privileged/delete/export actions

- Severity: P2
- Confidence: High
- Area: ADMIN
- Evidence: `server/benchd.py:94-143`, `:653-681`, `:1220-1232`, `:885-913`.
- What is happening: no immutable record of who did what; the shared token means no actor exists.
- Why it matters: the "audit logs for role/delete/export" check fails.
- Recommended fix: append-only audit table + UI; write on every mutating/export action.
- Suggested validation: delete/exec then assert an audit row survives.
- Owner suggestion: control-plane maintainer
- Effort estimate: M
- Dependencies: per-user identity for meaningful attribution
- Status: open

### Finding ID: `ADMIN-P2-004` - Destructive actions gated only in the browser; deletes irreversible

- Severity: P2
- Confidence: High
- Area: ADMIN
- Evidence: `benchd.py:1220-1232`, `:665-680`; `app.js:1353,1363,1404-1437,1702-1704`.
- What is happening: the API accepts destructive commands and DELETEs unconditionally; prompts live only in JS.
- Why it matters: any API/script access performs irreversible fleet actions in one request; no undo.
- Recommended fix: server-side confirmation token/typed confirm; soft-delete/undo; explicit confirm param on DELETE.
- Suggested validation: assert the API rejects a destructive command without confirmation.
- Owner suggestion: control-plane maintainer
- Effort estimate: M
- Dependencies: ADMIN-P2-003
- Status: open

### Finding ID: `ADMIN-P2-005` - Fail-open when no token; docs bind 0.0.0.0

- Severity: P2
- Confidence: High
- Area: ADMIN
- Evidence: `benchd.py:573-574`, `:595-600`, `:1440-1441`, `:1420`; `docs/CONTROL_PLANE.md:48`.
- What is happening: a token-less server is fully open (only a warning).
- Why it matters: a config miss exposes command/exec/delete to the LAN/overlay.
- Recommended fix: refuse non-loopback bind without a token; require `--insecure`.
- Suggested validation: start without a token on `0.0.0.0` and assert it refuses (or requires the flag).
- Owner suggestion: control-plane maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: ADMIN-P2-006 - exec/shell is fleet-wide RCE with no approval and idle output is dropped

- Severity: P2
- Confidence: High (mechanism); Medium (that the live runner is root — inferred)
- Area: ADMIN
- Evidence: `benchd.py:1223-1225`; `bench/agent.py:273-276`; `bench/benchreport.py:811-820`, `:573-575`; `live/.../bench-agent-env:32-37`.
- What is happening: arbitrary shell runs as the runner's user; output is only stored during an active run.
- Why it matters: privileged remote execution plus a weak forensic trail.
- Recommended fix: privileged-role + audit; persist output regardless of run; optional allowlist/rate limit.
- Suggested validation: issue idle exec and assert its output is retrievable.
- Owner suggestion: control-plane maintainer
- Effort estimate: M
- Dependencies: ADMIN-P2-003
- Status: open

### Finding ID: ADMIN-P2-007 - Operator token in URL/localStorage; no expiry, rotation, or lockout

- Severity: P2
- Confidence: High
- Area: ADMIN
- Evidence: `app.js:101,171,179,1577-1578`; `benchd.py:578` (query token compared with `==`), `:626-693` (no rate limit); `docs/CONTROL_PLANE.md:206-207`.
- What is happening: the master token is carried in query strings and browser storage and can be guessed without limit.
- Why it matters: credential leakage and unlimited online guessing; global-only revocation.
- Recommended fix: header auth + short-lived scoped download/stream tokens; constant-time query compare; rate limiting; per-user tokens.
- Suggested validation: rate-limit test; assert downloads use a scoped token.
- Owner suggestion: control-plane maintainer
- Effort estimate: M
- Dependencies: ADMIN-P1-001
- Status: open

### Finding ID: ADMIN-P3-008 - Inconsistent confirmation (schedule delete has none)

- Severity: P3
- Confidence: High
- Area: ADMIN
- Evidence: `app.js:1353,1363` (confirm exists) vs `app.js:1702-1704,1663,1779` (no confirm).
- What is happening: destructive actions prompt inconsistently.
- Why it matters: a stray click deletes a recurring schedule; operators learn to click through prompts.
- Recommended fix: one shared confirmation component; typed confirm for fleet-scale actions.
- Suggested validation: UI test asserting a confirm is shown before schedule delete.
- Owner suggestion: front-end maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Runner host compromise → fleet RCE | P1 | Medium | Critical | ADMIN-P1-001 | Split secrets; RBAC |
| Runner identity takeover | P1 | Low–Medium | High | ADMIN-P1-002 | Prove machine ownership |
| Destructive action unattributable | P2 | Medium | High | ADMIN-P2-003 | Audit log |
| Accidental fleet wipe via API | P2 | Medium | High | ADMIN-P2-004 | Server-side confirm + undo |
| Open control plane on LAN | P2 | Medium | High | ADMIN-P2-005 | Fail closed |
| Operator token leak | P2 | Medium | High | ADMIN-P2-007 | Scoped short-lived tokens |

## Recommendations

### Immediate / Release Blocking
- Stop shipping the operator token to runners: separate join and operator secrets (ADMIN-P1-001).
- Close the `machine_id` adoption hole (ADMIN-P1-002).

### This Week
- Add the append-only audit log (ADMIN-P2-003).
- Fail closed without a token (ADMIN-P2-005).
- Server-side confirmation for destructive actions and DELETEs (ADMIN-P2-004).

### This Month
- Per-user accounts/roles; scoped download/stream tokens; rate limiting (ADMIN-P1-001, ADMIN-P2-007).
- Persist exec output regardless of run; optional allowlist (ADMIN-P2-006).

### Later / Platform Evolution
- Approval workflow for ISO write / bulk operations; key rotation/revocation; UI audit viewer.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Refuse to start without a token on non-loopback | Removes accidental-open deployments | `server/benchd.py:1418-1441` | Start test |
| Bind `machine_id` adoption to the issuing key | Closes takeover | `server/benchd.py:1190-1217` | Regression test |
| Add confirm to schedule delete | Consistent destructive UX | `server/web/app.js:1702-1704` | UI test |
| Constant-time query-token compare | Removes a token-timing gap | `server/benchd.py:578` | Unit test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Separate join vs operator secret | P1 | server | S | none |
| Prove machine ownership on adopt | P1 | server | S | none |
| Audit log + viewer | P2 | server | M | per-user identity |
| Server-side destructive confirmation + undo | P2 | server | M | audit log |
| Per-user accounts/roles | P1 | server | L | roadmap |
| Scoped download/stream tokens + rate limit | P2 | server | M | accounts |
| Exec output retention + allowlist | P2 | agent/server | M | audit log |

## Suggested Tests

- Unit: `_register` rejects adoption of a row whose `machine_id` was not issued to the caller (mirror `tests/test_control_plane.py:46-71`).
- Unit: destructive command kinds require a confirmation field; DELETE without confirm is rejected.
- Unit: query-token comparison is constant-time (or uses `compare_digest`).
- Unit: an audit row is written for command/delete/schedule/export and survives target deletion.
- Integration: a token-less server refuses a non-loopback bind; a join token cannot call operator routes.
- Security: rate limit + lockout on repeated bad tokens.
- Regression: exec output issued while idle is retrievable.
- Manual: walk the console and confirm every destructive control prompts consistently.

## Suggested Documentation Updates

- `docs/CONTROL_PLANE.md` §Security: split join vs operator credentials, document the audit log, and state the fail-closed default.
- `docs/CONTROL_PLANE.md` §API reference: note required confirmation for destructive kinds and DELETEs.
- `README.md` §Auth: correct "shared join token for operators" once secrets are split.
- Add an `## Audit` section describing what is logged and how to read it.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are live-USB runners actually root (so exec=root RCE)? | Severity of ADMIN-P2-006 | The systemd units that launch the TUI/agent and their `User=` |
| Is `machine_id` ever exposed to non-operators? | Exploitability of ADMIN-P1-002 | Any response including `machine_id` reachable by a runner key |
| Was a token ever deployed with the operator secret on runner machines in the lab? | Real-world exposure | Lab configs/`/etc/bench-agent.conf` (not in repo) |

## Appendix

Reproduction (executed against a **copy** of `server/` in the scratch dir, loopback only; the
target repo was not modified):

```
victim  : {'runner_id': '12ccedcb-…', 'api_key': 'Ip_HTvo…'}
attacker: {'runner_id': '085cff25-…', 'api_key': 'hPrqmfm…'}
POST /api/v1/register (bearer = attacker key, body.machine_id = 'dmi-VICTIM')
status: 200
body  : {'runner_id': '12ccedcb-…', 'api_key': 'Ip_HTvo…'}   # victim's row + key
TOOK OVER VICTIM ROW : True
RECEIVED VICTIM KEY  : True
```

Evidence discipline: every path/line above was read from the audited tree; the single dynamic
result is the reproduction above. No secret values from the target repo are reproduced (the keys
shown are throwaway values minted by the local copy).

## Findings

| ID | Severity | Title |
|---|---|---|
| ADMIN-P1-001 | P1 | Single shared BENCHD_TOKEN is both the runner join secret and the all-powerful operator bearer, deployed to every runner host |
| ADMIN-P1-002 | P1 | One enrolled runner can hijack another runner's identity and receive its API key via machine_id adoption in POST /register |
| ADMIN-P2-001 | P2 | No audit log for privileged, destructive, or export actions; actions are unattributable because the token is shared |
| ADMIN-P2-002 | P2 | Destructive actions are gated only in the browser; the API enforces nothing and deletes are irreversible with no undo |
| ADMIN-P2-003 | P2 | Control plane fails open when no token is configured, while the docs run it on 0.0.0.0 |
| ADMIN-P2-004 | P2 | exec/shell provides fleet-wide arbitrary code execution (often as root) with no approval path and output dropped when no run is active |
| ADMIN-P2-005 | P2 | Operator credential is exposed via URL query string and localStorage, with no expiry, rotation, or brute-force lockout |
| ADMIN-P3-001 | P3 | Inconsistent confirmation for destructive console actions (schedule delete has none) |
