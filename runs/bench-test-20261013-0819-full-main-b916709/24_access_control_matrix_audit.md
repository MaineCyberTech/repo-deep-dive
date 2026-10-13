# 24_access_control_matrix_audit — Prompt 24 - Access Control Matrix Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `24_access_control_matrix_audit.md` (area ACM, prompt)

## Verification Performed

# Access Control Matrix Audit

## Audit Metadata

- Audit name: bench-test full-domain audit
- Run: 20261013-bench-test DOMAIN 24
- Repository: `C:\temp\bench-test` (read-only)
- Branch: `main`
- Commit SHA: brief states `b9167095b08c2f45a814e88e09d88decbd0ea885`; **observed HEAD is `72c18734aea2e5b3381254b74205d0b2944bafab`** (2 commits ahead) with an additional dirty working tree (see Scope limitations)
- Generated at: Tue Oct 13 2026
- Auditor: domain subagent (ACM)
- Area code: ACM
- Output path: `docs/audits/{name}/{run}/24_access_control_matrix_audit.md`
- Scope limitations: see below

## Scope

Reviewed the **control-plane authorization surface** of bench-test, which is the only
component in the repo with a role/permission model:

- `server/benchd.py` — HTTP REST + SSE + SQLite control plane: auth helpers, route
  dispatch, every write path, background scheduler/reapers.
- `server/web/app.js` — dashboard client: token handling, which controls it exposes.
- `bench/benchreport.py`, `bench/agent.py` — runner client, key storage, command
  dispatch (incl. `exec`/`shell`).
- `server/benchd.service`, `server/benchd.conf.example`, `benchd.conf` search order.
- `.github/workflows/build-app.yml`, `live/Build-LiveUSB.sh`, `live/airootfs/**` —
  how the operator token reaches public artifacts and the privilege it runs with.
- `tests/test_control_plane.py`, `tests/harness.py` — existing authz test coverage.
- `docs/CONTROL_PLANE.md`, `README.md` — documented model.

Not reviewed / not applicable: bench-test is a workstation benchmark + lab control
plane. There is **no org/tenant/workspace, no multi-tenant data, no billing, no
Supabase/RLS, no webhook delivery, no mobile/PWA, no per-object ACL store**. Those
rows of the matrix are `N/A — not present` (evidence: the SQLite schema in
`server/benchd.py:94-143` has only runners/runs/phases/telemetry/logs/commands/
events/artifacts/schedules; there is no tenant/org/account table anywhere).

### Scope limitations (important)

The brief pins commit `b9167095`, but the checkout is at `72c18734`. The two extra
commits are:

- `a3dc49b8 fix(security): the audit's high findings - key leak, root code exec, ...`
  (adds the runner_id ownership guard, body cap, log redaction, static-path
  containment, live-USB key parsing, constant-time bearer compare).
- `72c18734 chore(release): VERSION 1.11.4`

All evidence below is captured from the **on-disk files** (i.e. `72c18734` + an
uncommitted diff to `README.md`, `docs/PHASE_TIMINGS.md`, `server/web/app.js`,
`tests/test_dashboards.py`; the uncommitted hunks are unrelated to access control).
Findings already fixed by `a3dc49b8` are deliberately **excluded** (body size cap,
static-file traversal, runner_id takeover, token-in-journald). Because the target is
2 commits ahead of the stated SHA, results may not match an audit of `b9167095`.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `server/benchd.py:572-615` | code | `_is_operator` / `_runner_ok` / `_caller` / `_may_act_as` / `_may_write_run` | the whole authorization decision surface |
| `server/benchd.py:626-693` | code | route dispatch (GET/DELETE/POST) and the top-level gate | shows which routes are operator-only |
| `server/benchd.py:975-1251` | code | run/phase/telemetry/log/artifact/finish writes, command issue, schedules, register | per-object checks |
| `server/benchd.py:94-143` | schema | SQLite tables | no tenant/org/ACL/audit tables |
| `server/benchd.py:1163-1218` | code | `_register` identity adoption | the machine_id flaw |
| `server/benchd.py:1277-1398` | code | scheduler + reapers (background jobs) | run with full store access, no actor |
| `server/benchd.py:1401-1451` | code | config/token resolution, startup warning, bind host | open-mode |
| `server/web/app.js:98-205,1577-1583,1787-1833` | code | client token handling / hidden controls | client-side hiding |
| `bench/benchreport.py:338-374,447-527,811-843` | code | key persistence (0600), register, `run_exec` shell | runner side |
| `bench/agent.py:242-325` | code | command dispatch incl. `exec`/`shell` | RCE surface |
| `server/benchd.service:1-21`, `docs/CONTROL_PLANE.md:39-52,99-166,202-213` | config/doc | deployment hardening + documented model | 0.0.0.0 bind |
| `.github/workflows/build-app.yml:61-63`, `README.md:158-163,357-363` | CI/doc | operator token baked into public releases | world-readable |
| `live/Build-LiveUSB.sh:136-139`, `live/airootfs/usr/local/bin/bench-agent-env:26-54`, live units | code | token in public ISO, root context | RCE as root |
| `tests/test_control_plane.py:18-68,190-204`, `tests/harness.py:26-66` | test | existing authz coverage | gaps noted |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Read `server/benchd.py` in full (1452 lines) | read | confirm auth helpers + every route | cited line numbers |
| Read `tests/test_control_plane.py`, `tests/harness.py` | read | establish what authz is actually asserted | runner_id/own-run scoping covered; machine_id, DELETE, open-mode not |
| `git -C C:\temp\bench-test rev-parse HEAD` | command | confirm audited commit | `72c18734…` (brief said `b9167095…`) |
| `git -C C:\temp\bench-test log --oneline -8` | command | identify intervening fix commit | `a3dc49b8 fix(security)…` sits between brief SHA and HEAD |
| `git -C C:\temp\bench-test diff b9167095..HEAD -- server/benchd.py bench/benchreport.py bench/agent.py` | command | separate fixed vs still-open issues | machine_id adoption explicitly left unguarded |
| `git -C C:\temp\bench-test status --porcelain` | command | note dirty tree | 4 modified files, none access-control |
| Read `server/web/app.js` token/SSE/download regions | read | client-side hiding + token exposure | token in URL + localStorage |
| Read `live/airootfs/usr/local/bin/bench-agent-env` | read | privilege of the agent | runs as root at boot |

The findings were derived by tracing each route to its authorization check and asking
"who can call this, and is the object/identity bound to the caller?" No exploit was
executed against a live server (read-only audit; the in-process harness would mutate
state).

## Executive Summary

bench-test's access-control model is a **small two-tier scheme**: a shared join token
(= operator) and per-runner API keys issued at registration. Within that model the
implementation is careful — per-runner keys are scoped to their own runner and their
own run (`_may_write_run`, `_may_act_as`, `server/benchd.py:602-615`), operator-only
routes are gated consistently, run/artifact IDs are validated (`safe_id`,
`server/benchd.py:382-387`), and the test suite asserts the scoping
(`tests/test_control_plane.py:190-204`). A recent commit even fixed a genuine
runner_id takeover. Those are real strengths.

The weaknesses are structural, not scattered:

1. **There is no least-privilege credential.** The join token is literally the
   operator token (`server/benchd.py:572-580`), and it is *baked into public app
   bundles and the public ISO* (`README.md:158-163`, `build-app.yml:61-63`). Anyone
   who downloads a release can queue `exec`/`shell` (arbitrary command, root on the
   live USB), `reboot`/`shutdown`, raw device writes, and destructive deletes. The
   README's mitigation ("use a limited, rotatable one") is not implementable — no
   limited token exists.
2. **Runner identity is caller-asserted.** Adoption by `machine_id` has no ownership
   proof (`server/benchd.py:1190-1200`), so any authenticated runner that knows
   another's machine_id receives that runner's API key (`:1217`). The recent fix
   explicitly left this path open.
3. **No credential lifecycle and no audit trail.** Keys never expire and cannot be
   rotated/revoked individually (only by deleting the runner); privileged actions
   record no actor.
4. **Fail-open by default** when the token is unset, on a unit that binds `0.0.0.0`.

Recommended next actions, in order: introduce scoped/named credentials (registration
vs operator) and stop baking the operator secret into public artifacts; bind
machine_id adoption (or make it unforgeable); add key expiry/rotation/revocation and
an audit log; refuse to serve unauthenticated unless explicitly allowed.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Roles | `benchd.py` (operator/runner only) | principal model | implemented, 2 roles | High | no read-only role, no per-user |
| Permissions | `_is_operator`/`_runner_ok`/`_may_act_as`/`_may_write_run` `benchd.py:572-615` | authz checks | implemented, object-scoped for runners | Medium | operator unrestricted by design |
| Join/registration token | `BENCHD_TOKEN`, `benchd.py:572-580,1413-1415` | register + operator bearer | same secret for both | High | world-readable in releases |
| Runner API keys | `benchd.py:1201-1217`, `benchreport.py:355-374` | per-runner auth | issued once, plaintext, no expiry/rotation | Medium | `0600` on client |
| Org/tenant/workspace membership | — | — | N/A | — | no such tables (`benchd.py:94-143`) |
| Project/ticket/billing/webhook perms | — | — | N/A | — | not present |
| Admin console | `server/web/app.js` | operator dashboard | single-token, no role UI | Medium | all controls shown to any token |
| Public/authenticated/internal routes | `benchd.py:626-693` | `/health` public; all else token | consistent | Low | `/health` leaks count/git only |
| Server actions | n/a (no SSR) | — | N/A | — | dashboard is static JS |
| API endpoints | `benchd.py:696-1251` | REST + SSE | implemented, per-object scoping | Medium | see findings |
| Background jobs | `benchd.py:1277-1398` | scheduler + reapers | implemented, no actor | Medium | run as server process |
| DB helpers | `Store` `benchd.py:147-190` | SQLite access | parameterised SQL throughout | Low | no tenant scoping needed |
| Middleware | `do_GET/POST/DELETE`, `_send` `benchd.py:626-693,527-540` | gate + headers | per-method, no audit | Medium | wildcard CORS |
| Client-side hiding | `app.js:1822-1833`, `:153` | token prompt / auth header | server also enforces | Low | hiding is not the only control |
| Server enforcement | `benchd.py:975-1005` | write scoping | implemented | Low | good |
| Audit logs | `events`/`logs` tables | run events/console only | no authz audit | High | no actor on any action |
| Authz tests | `tests/test_control_plane.py` | regression | covers runner_id/own-run; misses machine_id, DELETE, open-mode | Medium | |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Roles | 2 | two principal kinds, `benchd.py:572-615`, docs `CONTROL_PLANE.md:204-207` | no read-only/operator split, no per-user | add named/scoped tokens |
| Permissions | 3 | `_may_act_as`/`_may_write_run`, `benchd.py:602-615` | operator unrestricted; join==operator | least-privilege tokens |
| Org/tenant/workspace membership | 0 | schema `benchd.py:94-143` | N/A | none needed |
| Project/ticket/document/billing/API key/webhook permission | 2 | runner key issuance only, `benchd.py:1201-1217` | key lifecycle absent | expiry/rotation/revocation |
| Admin console | 2 | `web/app.js` | single token, all controls, no audit | viewer role + audit view |
| Public/authenticated/internal routes | 3 | `benchd.py:626-693` | consistent gate; fail-open when token unset | refuse to start without token |
| Server actions | 0 | no SSR | N/A | — |
| API endpoints | 3 | `benchd.py:696-1251` | machine_id adoption; CORS/URL token | see findings |
| Background jobs | 3 | `benchd.py:1277-1398` | no actor, unlimited store access | log actor/schedule changes |
| DB helpers | 4 | `Store` `benchd.py:147-190` | parameterised, WAL; keys plaintext | hash keys |
| Middleware | 2 | `do_*` + `_send` | wildcard CORS, no audit hook | scoped CORS + audit |
| Client-side hiding | 3 | `app.js:153,179,1822-1833` | server-enforced (good); token in URL | ticket-based downloads |

## Detailed Review

### Item: Authorization helpers

- Evidence: `server/benchd.py:562-615`.
- What it does: resolves (is_operator, runner_row) from the bearer / `?token=`, then
  offers `_may_act_as(rid)` and `_may_write_run(run_id)` which bind runner keys to
  their own runner and their own runs.
- How it appears to work: correct and object-scoped for runners; operator bypasses.
- Current controls: `secrets.compare_digest` on the operator bearer; parameterised
  SQL; `safe_id` on run ids.
- Missing controls: no actor identity is ever retained; comparisons are inconsistent
  (`==` on three paths); operator is a single shared secret with no scopes.
- Risks: attribution and least privilege (findings 1, 3, 5, 7).
- Recommended improvement: single credential-verification helper + actor context.
- Suggested tests: unit tests asserting every route denies cross-runner access and
  that `== self.token` does not appear.
- Suggested docs: a role→route matrix in `docs/CONTROL_PLANE.md`.

### Item: Registration / identity adoption

- Evidence: `server/benchd.py:1163-1218`; `bench/benchreport.py:341-374,509-527`.
- What it does: issues a per-runner key; re-registration reuses a row by
  `runner_id` (now proof-gated) or by `machine_id`+`kind`+`instance` (not gated).
- Current controls: ownership proof for explicit `runner_id`; stable machine identity.
- Missing controls: proof for machine_id adoption; the response echoes the key.
- Risks: cross-runner key theft (finding 2).
- Suggested tests: register A and B; as B, POST `/register` with A's machine_id; assert
  the response does not contain A's key.
- Suggested docs: state that machine_id is a *hint*, not an authenticator.

### Item: Command issuance & runner terminal (RCE)

- Evidence: `server/benchd.py:1220-1232`, `bench/agent.py:266-325`,
  `bench/benchreport.py:811-843` (`subprocess.Popen(cmd, shell=True)`).
- What it does: operator-only endpoint queues `exec`/`shell`/`reboot`/`shutdown`/raw
  ISO writes; the agent runs the command as its own user (root on the live USB).
- Current controls: `_is_operator` gate; `confirm=true` for raw device writes;
  ACK timeouts.
- Missing controls: no scopes, no audit, and the operator secret is public.
- Risks: findings 1, 5, 6.

### Item: Background jobs

- Evidence: `server/benchd.py:1277-1398` (`scheduler_tick`, `reap_stale_runs`,
  `reap_ephemeral_runners`, `reap_stale_commands`).
- What it does: queues scheduled starts, fails stale runs/commands, drops one-shot
  runners — all with direct store access and no actor.
- Current controls: per-schedule online/busy guards; long-op ACK budgets.
- Missing controls: no audit of who created/edited a schedule; no scheduling ACLs.
- Risks: finding 5.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ACM-001 | Roles | `benchd.py:572-615` | operator vs runner (2 tiers) | no read-only/registration scope, no per-user | P1 | scoped/named tokens, viewer role |
| ACM-002 | Permissions | `benchd.py:602-615` | runner object-scoped | operator unrestricted; join==operator | P1 | least-privilege per action |
| ACM-003 | Org/tenant/workspace membership | `benchd.py:94-143` | none | N/A | — | none |
| ACM-004 | API key / webhook / billing permission | `benchd.py:1201-1217` | runner key issued once | no lifecycle; webhook/billing N/A | P2 | expiry/rotation/revocation, hash |
| ACM-005 | Admin console | `web/app.js` | token gate, server-enforced | no roles, no audit view | P2 | viewer role + audit page |
| ACM-006 | Public/authenticated/internal routes | `benchd.py:626-693` | `/health` public, rest token | fail-open when token unset | P2 | refuse open mode by default |
| ACM-007 | Server actions | n/a | none (static JS) | N/A | — | — |
| ACM-008 | API endpoints | `benchd.py:696-1251` | per-object scoping | machine_id adoption; CORS/URL token | P1/P2 | ownership proof; scoped CORS |
| ACM-009 | Background jobs | `benchd.py:1277-1398` | guards + reapers | no actor | P2 | audit schedule/actor |
| ACM-010 | DB helpers | `benchd.py:147-190` | parameterised SQL | keys plaintext | P2 | store hashes |
| ACM-011 | Middleware | `benchd.py:527-540,626-693` | per-method gate | wildcard CORS, no audit hook | P2 | scoped CORS + audit middleware |
| ACM-012 | Client-side hiding | `app.js:153,179,1577-1583` | token prompt; server also enforces | token in URL/localStorage | P2 | ticket-based downloads |

## Findings

### Finding ID: `ACM-P1-001` - Shared join token is the full operator credential and is baked into public releases

- Severity: P1
- Confidence: High
- Area: ACM
- Evidence:
  - `server/benchd.py:572-580` (`_is_operator` accepts `BENCHD_TOKEN` as operator bearer)
  - `server/benchd.py:582-591,688-689` (registration gate also accepts that same token)
  - `server/benchd.py:1223-1225` (operator-only endpoint can queue `exec`,`shell`,`reboot`,`shutdown`,`iso_write`)
  - `README.md:158-163`, `.github/workflows/build-app.yml:61-63`, `live/Build-LiveUSB.sh:136-139`
  - `docs/CONTROL_PLANE.md:135-137,204-207`
- What is happening: one shared secret is both the runner join token and the
  all-powerful operator bearer, and CI bakes it into public bundles/ISOs.
- Why it matters / impact: anyone who downloads a release can control the fleet,
  including arbitrary command execution (root on the live USB), reboots, raw writes,
  and destructive deletes. There is no way to issue a limited registration token.
- Recommended fix: separate registration and operator credentials; per-user/scoped
  operator tokens; bake only the registration token into public artifacts.
- Suggested validation: attempt an operator action (`exec`) with a token limited to
  registration → expect 403. Assert the public bundle contains no operator token.
- Owner suggestion: control-plane maintainer. Effort: M. Dependencies: none.
- Status: open. Endpoint/data path: `POST /api/v1/runners/<id>/commands` with
  `kind=exec` → `_issue_command` → agent `_exec_and_ack` → `run_exec` (shell=True).
- Attack path: download public ISO/app bundle → read baked `BENCHD_TOKEN` → call the
  LAN-bound control plane → `exec` on any runner (root) → full compromise.

### Finding ID: `ACM-P1-002` - machine_id adoption hands out another runner's API key

- Severity: P1
- Confidence: High
- Area: ACM
- Evidence: `server/benchd.py:1190-1200,1217`, `server/benchd.py:688-689`,
  `bench/benchreport.py:380-444`, `docs/CONTROL_PLANE.md:231-238`,
  `tests/test_control_plane.py:46-68`.
- What is happening: any authenticated runner that sends someone else's
  `machine_id` (+ kind + instance) has that row adopted and receives its `api_key`.
- Why it matters / impact: cross-runner impersonation; the attacker can drain/ack the
  victim's commands and write to the victim's runs. Identity relies on a
  client-supplied, forgeable string.
- Recommended fix: require ownership proof for machine_id adoption (row key as
  body/bearer or operator), or make the id server-issued/unforgeable.
- Suggested validation: as runner B, POST `/register` with runner A's machine_id;
  assert the returned key is not A's.
- Owner suggestion: control-plane maintainer. Effort: S. Dependencies: none.
- Status: open.
- Attack path: register legitimately to get a key → know victim's machine_id → claim
  it at `/register` → receive victim's key → poll/ack victim's command queue.

### Finding ID: `ACM-P2-003` - No credential lifecycle (expiry/rotation/revocation); keys plaintext

- Severity: P2 · Confidence: High · Area: ACM
- Evidence: `server/benchd.py:1203,98,653-681,1413-1415`;
  `bench/benchreport.py:355-374`; `docs/CONTROL_PLANE.md:275-276`.
- What is happening: keys are issued once, stored plaintext, never expire, and the
  only "revoke" is deleting the whole runner.
- Why it matters: a leaked key is valid forever; no rotation or revocation evidence.
- Recommended fix: key metadata + rotate/revoke endpoints; store hashes.
- Suggested validation: rotate → old key returns 401, new key works; revoke keeps the
  runner row but invalidates the key. Effort: M. Status: open.

### Finding ID: `ACM-P2-004` - Fail-open when no token is set, on a 0.0.0.0 unit

- Severity: P2 · Confidence: High · Area: ACM
- Evidence: `server/benchd.py:572-573,583,1438-1441`; `server/benchd.service:11`;
  `docs/CONTROL_PLANE.md:48,208-210`; `server/web/app.js:1823-1826`.
- What is happening: with `BENCHD_TOKEN` unset, every request is a full operator, and
  the shipped service binds all interfaces.
- Why it matters: one config slip exposes an unauthenticated RCE/reboot/delete plane.
- Recommended fix: refuse to start (or bind loopback + refuse registration) without a
  token unless `--allow-open`; add `ConditionPathExists`/`EnvironmentFile` to the unit.
- Suggested validation: start with no token → requests are rejected. Effort: S.
- Status: open.

### Finding ID: ACM-P2-005 - No audit trail / actor attribution for privileged actions

- Severity: P2 · Confidence: High · Area: ACM
- Evidence: `server/benchd.py:119-134,515-525,653-681,1220-1232,1234-1251`.
- What is happening: commands/events have no actor column; deletes and schedule
  creation are unattributed; the access log redacts the token and records no identity.
- Why it matters: no way to reconstruct who ran/rebooted/deleted what.
- Recommended fix: append-only audit table (actor, route, resource, action, outcome),
  surfaced read-only. Effort: M. Status: open.

### Finding ID: ACM-P2-006 - Operator token in URLs + wildcard CORS

- Severity: P2 · Confidence: High · Area: ACM
- Evidence: `server/benchd.py:533,618-624,578`; `server/web/app.js:179,1582-1583`;
  `docs/CONTROL_PLANE.md:206-207`.
- What is happening: the operator token travels in `?token=` for SSE/downloads and
  every response carries `Access-Control-Allow-Origin: *`.
- Why it matters: URL-borne secrets leak via history/sync/Referer/proxy logs; wildcard
  CORS lets any origin read API responses given the token.
- Recommended fix: short-lived download/stream tickets; restrict/remove wildcard CORS.
  Effort: S–M. Status: open.

### Finding ID: ACM-P3-007 - Inconsistent constant-time token comparison

- Severity: P3 · Confidence: High · Area: ACM
- Evidence: `server/benchd.py:576` (compare_digest) vs `:578,:586,:598` (`==`).
- What is happening: only the bearer path in `_is_operator` is constant-time.
- Why it matters: inconsistency/possible timing signal on the query path.
- Recommended fix: single constant-time comparator everywhere. Effort: S. Status: open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Public operator token → fleet RCE (root on live USB) | High | High | High | `README.md:158-163`, `build-app.yml:63`, `benchd.py:1223-1225` | split/stop baking tokens |
| Cross-runner key theft via machine_id | High | Medium | High | `benchd.py:1190-1200,1217` | ownership proof |
| No revocation of leaked keys | Medium | Medium | Medium | `benchd.py:653-681` | rotate/revoke endpoints |
| Unauthenticated open mode on 0.0.0.0 | High | Low | High | `benchd.py:572-573`, `benchd.service:11` | refuse open mode |
| No forensic attribution | Medium | High | Medium | `benchd.py:119-134` | audit log |

## Recommendations

### Immediate / Release Blocking
- Stop baking the operator token into public app bundles/ISOs (ACM-P1-001).
- Add ownership proof to machine_id adoption (ACM-P1-002).

### This Week
- Refuse to serve without a token unless `--allow-open` (ACM-P2-004).
- Add an audit table and record actor + action (ACM-P2-005).
- Replace `?token=` in URLs with short-lived tickets; scope CORS (ACM-P2-006).

### This Month
- Key metadata + rotate/revoke; store hashes (ACM-P2-003).
- Named/scoped operator tokens and a read-only viewer role (ACM-P1-001).
- Unify constant-time comparisons (ACM-P3-007).

### Later / Platform Evolution
- Per-user operator logins (already on the roadmap, `docs/CONTROL_PLANE.md:275-276`),
  with roles → routes → actions as a maintained matrix; optional mTLS for runners.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `--allow-open` gate | kills fail-open | `server/benchd.py`, `server/benchd.service` | start without token → 401 |
| machine_id ownership proof | closes key theft | `server/benchd.py:1190-1200` | new regression test |
| constant-time helper | removes P3 | `server/benchd.py:572-600` | grep for `== self.token` |
| audit table on writes | attribution | `server/benchd.py` | row per delete/command |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Scoped/named credentials + least privilege | P1 | control-plane | M | token model |
| Ownership proof for identity adoption | P1 | control-plane | S | none |
| Credential lifecycle (expiry/rotate/revoke, hashing) | P2 | control-plane | M | key metadata |
| Audit log + dashboard view | P2 | control-plane | M | schema migration |
| Ticket-based downloads, scoped CORS | P2 | control-plane/web | S–M | none |
| Refuse open mode by default | P2 | control-plane/packaging | S | none |

## Suggested Tests

- Unit/security: as runner B, claim runner A's `machine_id` at `/register` and assert
  A's key is not returned (ACM-P1-002).
- Unit/security: with the token unset, assert `/api/v1/*` rejects writes unless
  `--allow-open` (ACM-P2-004).
- Integration: rotate a runner key → old key 401, new key 200; revoke keeps the row
  (ACM-P2-003).
- Integration/E2E: every state-changing route writes exactly one audit row with an
  actor (ACM-P2-005).
- CI/lint: forbid `== self.token` and `Access-Control-Allow-Origin: *` (ACM-P3-007,
  ACM-P2-006).
- Regression: a registration-only token cannot issue commands or DELETE (ACM-P1-001).
- Manual: extract a public app bundle and confirm it carries no operator token.

## Suggested Documentation Updates

- `docs/CONTROL_PLANE.md`: add a role → route → action matrix; state that the join
  token must not be an operator credential; document key lifecycle and audit log.
- `README.md` Security section: remove the "use a limited, rotatable token" advice
  until a limited token exists; state the current blast radius honestly.
- Add `docs/audits/.../access_control_matrix.md` as a maintained living matrix.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are the lab deployments using a token that equals a baked public token? | determines live exposure | lab `/etc/benchd.conf` (not accessible read-only here) |
| Is the control plane ever reachable beyond the LAN/WireGuard? | determines severity of findings 1/4 | reverse-proxy / firewall config (not in repo) |
| Was b9167095 the intended audit SHA, or is HEAD the target? | results differ by 2 commits | operator confirmation |

## Appendix

### Evidence highlights (verbatim)

```python
# server/benchd.py:572-580
def _is_operator(self, q=None):
    if self.token is None:
        return True                       # <-- fail open
    b = self._bearer()
    if b and secrets.compare_digest(b, self.token):
        return True                       # <-- BENCHD_TOKEN == operator
    if q and q.get("token", [None])[0] == self.token:   # <-- non-constant-time
        return True
    return False

# server/benchd.py:1190-1200  (machine_id adoption, no ownership proof)
if not existing and mid:
    existing = S.one("SELECT * FROM runners WHERE machine_id=? AND kind=? "
                     "AND COALESCE(instance,'')=?", (mid, kind, inst))
if existing:
    rid = existing["id"]
    key = existing["api_key"]             # <-- returned to caller at :1217
```

### Commit context

```
72c18734 chore(release): VERSION 1.11.4          <- observed HEAD
a3dc49b8 fix(security): the audit's high findings - key leak, root code exec, ...
b9167095 chore(release): VERSION 1.11.3          <- brief's stated target
```

The `a3dc49b8` fix closed: runner_id takeover, import positional indexing, static-path
containment, live-USB root config parsing, body size cap, and token redaction in
journald. It explicitly left the machine_id adoption path open (ACM-P1-002) and did
not add scopes (ACM-P1-001), key lifecycle (ACM-P2-003), audit (ACM-P2-005), or
scoped CORS (ACM-P2-006).

## Findings

| ID | Severity | Title |
|---|---|---|
| ACM-P1-001 | P1 | Shared join token IS the full operator credential - no least-privilege registration/read-only role - and it is baked into world-readable public releases |
| ACM-P1-002 | P1 | Runner identity adoption by unverified, client-supplied machine_id lets any authenticated runner obtain another runner's API key |
| ACM-P2-001 | P2 | No lifecycle for runner API keys or the operator token: no expiry, rotation, or per-key revocation; keys stored in plaintext |
| ACM-P2-002 | P2 | Control plane fails open: with no BENCHD_TOKEN every request is a full operator (RCE/reboot/delete), and the shipped unit binds 0.0.0.0 |
| ACM-P2-003 | P2 | No audit trail: privileged actions (exec/shell, reboot/shutdown, deletes, schedules) are not attributed to any actor |
| ACM-P2-004 | P2 | Operator token is placed in URL query strings and the API returns a wildcard CORS header on every response |
| ACM-P3-001 | P3 | Inconsistent constant-time credential comparison (bearer uses compare_digest; ?token=, _runner_ok and _caller use ==) |
