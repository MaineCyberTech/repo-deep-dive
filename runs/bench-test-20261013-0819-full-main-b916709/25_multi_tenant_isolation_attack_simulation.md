# 25_multi_tenant_isolation_attack_simulation — Prompt 25 - Multi-Tenant Isolation Attack Simulation

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `25_multi_tenant_isolation_attack_simulation.md` (area MT, prompt)

## Verification Performed

# Multi-Tenant Isolation Attack Simulation

## Audit Metadata

- Audit name: repo-deep-dive (bench-dive full-domain)
- Run: 20261013-manual (full-domain subagent pass)
- Repository: `C:\temp\bench-test`
- Branch: `main`
- Commit SHA: `72c18734aea2e5b3381254b74205d0b2944bafab` (observed via `git log -1`; the brief
  supplied `b9167095b08c2f45a814e88e09d88decbd0ea885`, which is **not** the working-tree HEAD —
  see Open Questions)
- Generated at: 2026-10-13
- Auditor: domain subagent (`25_multi_tenant_isolation_attack_simulation`)
- Area code: MT
- Output path (pack convention): `docs/audits/{name}/{run}/25_multi_tenant_isolation_attack_simulation.md`
  (this file was written to the driver's bench-dive output dir, not the target repo — target is read-only)
- Scope limitations: read-only static review; no server was launched against a live fleet; no network
  calls were made to the control plane; `.venv/` third-party packages were excluded as not application code.

## Scope

This domain simulates safe, code-level **cross-tenant** abuse through IDs, routes, APIs, realtime,
files, jobs, cache and search. A cross-tenant test requires a **tenant / org / workspace boundary**
that data, memberships, queries and responses are supposed to be scoped to.

Reviewed:
- `server/benchd.py` (control plane: schema, auth, dispatch, all `/api/v1` routes)
- `server/web/app.js`, `server/web/index.html` (client fetchers, token handling)
- `bench/benchreport.py`, `bench/agent.py` (client-side reporter/agent)
- `tests/test_control_plane.py` (auth/isolation tests that exist)
- `README.md`, `AGENTS.md`, `docs/CONTROL_PLANE.md` (documented model)

Not reviewed / not present:
- No SaaS application surface exists in the repo (no web app with accounts, no Supabase/Postgres
  RLS, no webhook receivers, no invitations, no notifications subsystem).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `server/benchd.py:94-143` | SQLite `SCHEMA` | Would hold `tenant`/`org`/`workspace` columns if multi-tenant | Tables: `runners, runs, phases, telemetry, logs, commands, events, artifacts, schedules` — **no tenant/org/workspace/account column anywhere** |
| `server/benchd.py:14-17` | Auth-model docstring | Defines the only principal types | Two principals only: `operators` (shared join token) and `runners` (per-runner API key). No tenant principal |
| `server/benchd.py:562-615` | Auth helpers | Where an isolation boundary would be enforced | `_is_operator`, `_runner_ok`, `_caller`, `_may_act_as`, `_may_write_run` — scope is **operator vs. its own runner/run**, not tenant vs. tenant |
| `server/benchd.py:626-694` | `do_GET`/`do_DELETE`/`do_POST` dispatch | Route-level gate | All `/api/v1` GET except `stream` and `runners/<id>/commands` require `_is_operator`; no per-tenant route segment exists |
| `server/benchd.py:696-771` | `_api_get` | Data access for runs/telemetry/logs/artifacts/trends | Queries key off `runner_id`/`run_id`/`host`, never a tenant id |
| `server/benchd.py:636-639, 178-179`, `server/web/app.js:153-179` | Realtime | SSE channel = the only "realtime" surface | `/api/v1/stream` is operator-gated; a single global `Bus`. No channel/room per tenant |
| `server/web/app.js:98-179, 1577-1578` | Client fetchers | Client-side scoping/auth | Bearer token via `localStorage`/`?token=`; downloads append the operator token. No tenant id in any fetch |
| `README.md:197-202`, `AGENTS.md:94-120` | Docs | Documented auth/identity model | "shared join token for operators; per-runner API keys for runners" — a single fleet, not tenants |
| `docs/CONTROL_PLANE.md:1-22` | Docs | Deployment intent | "turns a set of bench-test machines into **one** live, controllable fleet" |
| `tests/test_control_plane.py:19-93` | Tests | Existing isolation tests | Cover operator-vs-runner and **runner-vs-runner key theft** only; no tenant tests |
| Repo-wide grep | Command | Prove absence | Case-insensitive search for `tenant|org_id|workspace|organization|membership|supabase|row level|RLS|webhook` in application files returns **no matches** (only vendored `.venv` third-party hits) |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `grep -i 'tenant\|org_id\|workspace\|organization\|membership\|orgId\|account_id'` over `C:\temp\bench-test` | command | Prove no tenancy concept | `No matches found` (first run, default excludes) |
| PowerShell `Select-String` over `*.py,*.js,*.html,*.css,*.md,*.json,*.sh,*.ps1` (excluding `.git`, `__pycache__`) | command | Confirm absence in app code | Only matches under `.venv\Lib\site-packages\cryptography|filelock|networkx` (third-party) |
| `grep -i 'RLS\|row level security\|supabase\|realtime\|webhook'` | command | Prove no RLS/realtime/webhooks | Only `realtime` = Windows Defender "Real-Time Protection" in `bench/Get-EnvInfo.ps1:41,60` and `bench/Sample-Sensors.ps1`; no webhook/RLS matches |
| `git log -1 --format='%H %ci %s'` / `git rev-parse --abbrev-ref HEAD` | command | Bind report to a commit | `72c18734… 2026-10-13 chore(release): VERSION 1.11.4`, branch `main` |
| Read `server/benchd.py` lines 14-43, 60-239, 540-879 | read | Auth + schema + routes | Confirmed single-namespace model |
| Read `README.md`, `AGENTS.md`, `docs/CONTROL_PLANE.md` | read | Documented model | Confirmed "one fleet" single-tenant intent |
| Read `tests/test_control_plane.py` | read | Existing isolation coverage | Confirmed no tenant tests |

## Executive Summary

**Not applicable.** `bench-test` is a workstation benchmark/stress toolkit plus a **single-operator,
single-fleet control plane** (`benchd`). It has no tenant, organization, workspace, account, or
membership concept in code, schema, docs, or tests. The only authorization boundary is
**operator (shared join token) vs. a runner's own row/run (per-runner API key)**, and that boundary is
enforced and tested (`server/benchd.py:602-615`; `tests/test_control_plane.py:46-67`). Because there is
no tenant boundary, the class of attack this domain simulates — one tenant reaching another tenant's
data through IDs, routes, APIs, realtime, files, jobs, cache, or search — **cannot be constructed
against this repository**. An empty finding set is the accurate result.

The real access-control surface here (a shared operator token granting full fleet control, including a
remote `exec`/`shell` on runners) is a genuine consideration, but it is a **single-tenant privileged
operator** risk, not a multi-tenant isolation failure, so it is out of scope for this domain and is
expected to be covered by the authz/secrets domains. Per the brief, no findings are fabricated to fill
the domain.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Tenant/org/workspace IDs | `server/benchd.py:94-143` (`SCHEMA`) | Tenant scoping key | Absent | N/A | No such column; only `runner_id`, `run_id`, `host` |
| Membership checks | `server/benchd.py:562-615` | Who may act on a resource | Present, but operator/runner only | N/A (not tenancy) | `_is_operator`, `_may_act_as`, `_may_write_run` |
| DB queries | `server/benchd.py:696-879` | Reads/writes | Scoped by runner/run/host | N/A | SQLite, single namespace |
| API routes | `server/benchd.py:626-771` | `/api/v1/*` | Operator-gated (except runner self-commands) | N/A | No per-tenant path |
| Server actions | n/a | Server actions framework | Absent | N/A | Plain `http.server` handlers, no Next.js/actions |
| Client fetchers | `server/web/app.js:153-179`; `bench/benchreport.py` | HTTP client | Bearer token; no tenant id | N/A | Single token namespace |
| RLS | repo-wide | Row-level security | Absent | N/A | SQLite (not Postgres/Supabase); grep: no matches |
| Storage/file access | `server/benchd.py:750-752, 126-129` (`artifacts`) | Artifact download/store | Operator-gated download; path containment test exists | N/A | `tests/test_control_plane.py:150` checks containment |
| Realtime channels | `server/benchd.py:636-639, 194-217` (`Bus`) | SSE live stream | Single operator-gated stream | N/A | Global bus, no channel/room |
| Search/export | `server/benchd.py:726-737` (`?host=`), `740` (`telemetry.csv`) | Filter/export | Operator-gated | N/A | No tenant filter |
| Admin overrides | `server/benchd.py:14-17, 113-116` docs | Operator powers | Present | N/A (not tenancy) | Operator token = full fleet control |
| Invitations | repo-wide | Invite flow | Absent | N/A | Grep: no matches |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Tenant/org/workspace IDs | 0 | `benchd.py:94-143` — no tenant column | Domain not implemented (no multi-tenancy) | None; N/A — re-score if the product ever becomes multi-tenant |
| Membership checks | 0 | `benchd.py:562-615` — operator/runner only | No tenant membership model | None; N/A |
| DB queries | 0 | `benchd.py:696-879` | Not tenant-scoped (no tenants) | None; N/A |
| API routes | 0 | `benchd.py:626-771` | No tenant segment | None; N/A |
| Server actions | 0 | none | n/a (no action framework) | None; N/A |
| Client fetchers | 0 | `server/web/app.js:153-179` | Single token namespace | None; N/A |
| RLS | 0 | repo grep — absent; SQLite backend | No RLS engine | None; N/A |
| Storage/file access | 0 | `benchd.py:750-752` | Not tenant-scoped | None; N/A |
| Realtime channels | 0 | `benchd.py:194-217, 636-639` | Single global channel | None; N/A |
| Search/export | 0 | `benchd.py:726-740` | Not tenant-scoped | None; N/A |
| Admin overrides | 0 | `benchd.py:14-17` | Operator override is whole-fleet | None; N/A (see authz domain) |
| Invitations | 0 | repo grep — absent | No invite flow | None; N/A |

`0` here means "absent or not assessable" precisely because **multi-tenancy does not exist** — it is not
a quality judgment on the (correct, tested) single-tenant control plane.

## Detailed Review

### Item: Control-plane data model

- Evidence: `server/benchd.py:94-143`
- What it does: Defines all persisted entities (`runners, runs, phases, telemetry, logs, commands, events, artifacts, schedules`).
- How it appears to work: Every row is keyed by `id` and related via `runner_id`/`run_id`; there is no `tenant_id`/`org_id`.
- Dependencies: `sqlite3` (stdlib).
- Current controls: Primary keys, `run_id`/`runner_id` foreign keys, indexes.
- Missing controls: No tenant partitioning (not required by the product).
- Risks: None within this domain.
- Recommended improvement: None (N/A).
- Suggested tests: N/A.
- Suggested docs: N/A.

### Item: Authorization boundary

- Evidence: `server/benchd.py:562-615` (`_is_operator`, `_runner_ok`, `_caller`, `_may_act_as`, `_may_write_run`), `:626-694` (dispatch gates).
- What it does: Grants the shared join token full operator access; a per-runner key may only read its own queued commands and write its own runs.
- How it appears to work: `_may_write_run()` checks `runs.runner_id == runner.id`; `_runner_ok()` restricts `/commands` to the caller's runner id.
- Dependencies: `secrets.compare_digest` for the operator token compare.
- Current controls: Operator gate + per-runner run ownership; tested.
- Missing controls: n/a for tenancy. (Note: `_runner_ok`/`_caller` use `==` rather than `compare_digest` for the runner key; that is a timing-hygiene concern belonging to the authz domain, not multi-tenancy.)
- Risks: None within this domain.
- Recommended improvement: None (N/A).
- Suggested tests: Already covered — `tests/test_control_plane.py:19-33` (token required; bogus key rejected), `:46-67` (a runner cannot claim another runner's id and receive its key).
- Suggested docs: N/A.

### Item: Realtime / files / jobs / cache / search-export

- Evidence: `server/benchd.py:194-217` (`Bus`), `:636-639` (`/api/v1/stream`), `:750-752` (`_artifact_download`), `:726-740` (`/runs` filter, `telemetry.csv`), `:360` (`latest_git` cache).
- What it does: One global SSE bus; artifact download; host-filtered run listing; cached GitHub tip.
- How it appears to work: All are behind the operator gate; none carry a tenant dimension.
- Missing controls: Tenant scoping (N/A).
- Risks: None within this domain.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| MT-001 | Tenant/org/workspace IDs | `benchd.py:94-143` | None (no tenant column) | Domain not implemented | N/A | Not applicable — no tenancy model exists |
| MT-002 | Membership checks | `benchd.py:562-615` | Operator/runner scoping | No tenant membership | N/A | Not applicable |
| MT-003 | DB queries | `benchd.py:696-879` | Scoped by runner/run/host | No tenant scope | N/A | Not applicable |
| MT-004 | API routes | `benchd.py:626-771` | Operator-gated | No per-tenant route | N/A | Not applicable |
| MT-005 | Server actions | none | n/a | No action framework | N/A | Not applicable |
| MT-006 | Client fetchers | `server/web/app.js:153-179` | Bearer token | No tenant id | N/A | Not applicable |
| MT-007 | RLS | repo grep; SQLite | No RLS | Backend is SQLite | N/A | Not applicable |
| MT-008 | Storage/file access | `benchd.py:750-752`; test `:150` | Operator-gated + containment check | No tenant scope | N/A | Not applicable |
| MT-009 | Realtime channels | `benchd.py:194-217, 636-639` | Operator-gated SSE | Single global bus | N/A | Not applicable |
| MT-010 | Search/export | `benchd.py:726-740` | Operator-gated | No tenant filter | N/A | Not applicable |
| MT-011 | Admin overrides | `benchd.py:14-17` | Operator token = full fleet | Whole-fleet by design | N/A | Not applicable (authz domain covers this) |
| MT-012 | Invitations | repo grep — absent | None | No invite flow | N/A | Not applicable |

## Findings

**None.** No multi-tenant boundary exists to attack; simulating cross-tenant access would require
inventing functionality that the repository does not have, which the shared rules forbid.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| (This domain) | N/A | N/A | N/A | No tenant boundary exists | N/A — re-evaluate only if the product becomes multi-tenant |
| Whole-fleet operator token is unpartitioned | (see authz domain) | — | — | `benchd.py:14-17, 113-116`; `README.md:197-202` | Out of scope here; track in the authorization/secrets domain |

## Recommendations

### Immediate / Release Blocking

None for this domain.

### This Week

None for this domain.

### This Month

None for this domain.

### Later / Platform Evolution

- If `benchd` is ever offered as a shared multi-tenant service, add an explicit tenant/org key to
  `SCHEMA` (`benchd.py:94-143`), thread it through every query in `_api_get`/`_api_post`, and add
  per-tenant authorization in `_caller`/`_may_write_run` before any such change ships.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| (none for this domain) | — | — | — |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Adopt a tenant dimension only if multi-tenancy is a product goal | Later | Control-plane owner | L | Product decision |

## Suggested Tests

- None required for this domain. If multi-tenancy is ever added, add cross-tenant access-denial tests
  mirroring the existing runner-isolation test at `tests/test_control_plane.py:46-67`.

## Suggested Documentation Updates

- Optional: add one line to `docs/CONTROL_PLANE.md` stating the control plane is **single-tenant
  (one operator, one fleet)** so future audits/agents do not re-open this domain. No other doc changes.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the audit brief's commit `b9167095…` differ from working-tree HEAD `72c18734…`? | Binds findings to the right revision | A `git log`/`git rev-parse` at the audited commit; here HEAD is `72c18734` |
| Will `benchd` ever be exposed as a shared multi-tenant service? | Determines whether this domain becomes applicable | Product roadmap / control-plane design doc |
| `.venv/` is present in the working tree | Vendored third-party code is not application code | Not evidence of tenancy (all `tenant`-like hits are third-party libs) |

## Appendix

Commands actually run (read-only; nothing under the target was modified):

```
cd C:\temp\bench-test
git log -1 --format="%H %ci %s"            # -> 72c18734… 2026-10-13 chore(release): VERSION 1.11.4
git rev-parse --abbrev-ref HEAD            # -> main
# case-insensitive greps for tenant/org_id/workspace/organization/membership/supabase/RLS/webhook
#   -> no application-code matches (only .venv third-party and Defender "Real-Time Protection")
```

Key source anchors:
- `server/benchd.py:14-27` — auth-model docstring (operators + runners only)
- `server/benchd.py:94-143` — `SCHEMA` (no tenant column)
- `server/benchd.py:562-615` — auth/boundary helpers
- `server/benchd.py:626-771` — routes
- `tests/test_control_plane.py:46-67` — runner-vs-runner key-theft test (the closest existing "isolation" control)
- `README.md:197-202`, `AGENTS.md:94-120`, `docs/CONTROL_PLANE.md:1-22` — documented single-fleet model

## Findings

_No findings in this domain._
