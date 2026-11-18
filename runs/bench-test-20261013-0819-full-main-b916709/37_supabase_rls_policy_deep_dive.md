# 37_supabase_rls_policy_deep_dive — Prompt 37 - Supabase RLS Policy Deep-Dive Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `37_supabase_rls_policy_deep_dive.md` (area RLS, prompt)

## Verification Performed

# Supabase RLS Policy Deep-Dive Audit

## Audit Metadata

- Audit name: repo-deep-dive (bench-test full-domain audit)
- Run: bench-dive (domain subagent)
- Repository: `C:\temp\bench-test`
- Branch: `main`
- Commit SHA: working tree at `72c18734aea2e5b3381254b74205d0b2944bafab` (brief nominal target `b9167095b08c2f45a814e88e09d88decbd0ea885`, an ancestor of HEAD — see Scope limitations)
- Generated at: 2026-10-13
- Auditor: domain subagent (37_supabase_rls_policy_deep_dive)
- Area code: RLS
- Output path (prompt convention): `docs/audits/{name}/{run}/37_supabase_rls_policy_deep_dive.md`
- Scope limitations: Read-only audit of the checkout on disk; the brief's nominal commit `b9167095` differs from the checked-out HEAD `72c18734` (two commits ahead). All evidence below was captured at `72c18734`; the domain conclusion is unchanged at either commit (no Supabase/Postgres/SQL files exist in either tree up to HEAD).

## Scope

Reviewed everything in the target repo that could carry a Supabase/Postgres RLS surface and the
mandatory equivalent-control readiness check:

- Supabase migrations — **absent**
- SQL schema — **absent** (no `*.sql` anywhere, tracked or untracked)
- RLS enablement / policies / grants / roles — **absent**
- Storage bucket policies — **absent**
- Functions / triggers / `SECURITY DEFINER` — **absent**
- Generated DB types — **absent**
- App queries / tenant-user matching / admin bypass / service-role usage — the repo's actual
  data-access path (an HTTP control plane over SQLite) was reviewed as the RLS equivalent
- RLS tests / migration CI / docs — reviewed for any of the above

Not reviewed: runtime behavior of the workstation benchmark harnesses (out of domain), live
benchd instance, and any data not present in the repository.

## Evidence Reviewed

- `server/benchd.py` — the only datastore in the repo; uses `sqlite3`, not Postgres.
  - `36: import sqlite3`
  - `95–142: CREATE TABLE IF NOT EXISTS ...` / `CREATE INDEX IF NOT EXISTS ...` schema block
  - `151: self.conn = sqlite3.connect(path, check_same_thread=False)`
  - `154: PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL`
  - `160–176: PRAGMA table_info(...)` + `ALTER TABLE ... ADD COLUMN` migrations
- `server/benchd.py:561–615` — authorization model (`_is_operator`, `_runner_ok`,
  `_caller`, `_may_act_as`, `_may_write_run`), enforced in the HTTP handler, not the DB.
- `server/web/app.js:101,153–155,163–179` — client sends `Authorization: Bearer <TOKEN>` or
  `?token=`; single shared token.
- `docs/CONTROL_PLANE.md:43` — token generation via `secrets.token_urlsafe(32)`.
- `server/benchd.conf.example:5` — token configured via env/conf.
- Repository-wide searches for `supabase|Supabase|postgres|PostgreSQL|RLS|CREATE POLICY|
  row-level security|service_role` and for any `*.sql` / `migration` / `storage` / `seed` path.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse HEAD` → `72c18734...` | command output | Establish audited commit | Brief nominal `b9167095` is an ancestor; tree at HEAD audited |
| `grep -ri "supabase"` repo-wide | command output | Prove no Supabase project/config | 0 matches |
| `grep -riE "postgres\|PostgreSQL\|RLS\|CREATE POLICY\|row level security\|service_role"` | command output | Prove no Postgres/RLS surface | Only SQLite `ALTER TABLE` lines in `benchd.py` matched `ALTER TABLE`; no Postgres/RLS matches |
| `git ls-files` filter `\.sql$\|migrat\|schema\|supabase\|rls\|storage\|seed` | command output | Find schema/migration/storage artifacts | No matches |
| Recursive file scan for `*.sql` / `supabase*` (incl. untracked) | command output | Catch ignored/untracked SQL | No matches |
| `grep -n "sqlite3\|CREATE TABLE\|PRAGMA"` `server/benchd.py` | command output | Identify actual datastore | SQLite confirmed (lines 36, 95–142, 151–176) |
| Read `server/benchd.py:555–704` | file read | Inspect auth/authz (RLS equivalent) | Token + runner api_key; handler-enforced |
| `grep -n "Authorization\|token"` `server/web/app.js` | command output | Client-to-server data path | Bearer/`?token=` shared token |

## Executive Summary

This domain is **NOT APPLICABLE**. The repository is a Windows/Linux workstation
benchmark-and-stress toolkit with a stdlib Python control plane. There is **no Supabase project,
no Postgres, no SQL schema, no migrations, and therefore no row-level security, policies, grants,
roles, storage bucket policies, database functions/triggers, `SECURITY DEFINER`, or generated DB
types** anywhere in the tree.

The prompt's fallback applies: an **equivalent-control readiness report** for the actual
data-access path. The control plane (`server/benchd.py`) stores all state in **SQLite** and enforces
authorization in the **HTTP handler** (a two-role model: shared *operator* token versus per-runner
`api_key`), not in the database. This is a deliberate, App-layer analogue of RLS: `_is_operator`,
`_runner_ok`, `_may_act_as`, and `_may_write_run` scope runner access to its own rows, while the
operator token can read/write everything. Because SQLite has no RLS engine, the guarantee holds only
as long as every query path is correctly gated in Python — there is no second, database-level
enforcement line as Postgres RLS would provide.

Strengths: opaque random tokens (`secrets.token_urlsafe(32)`), constant-time comparison for the
operator token (`secrets.compare_digest`), per-runner keyed writes, token redaction in logs
(`benchd.py:524`), and an explicit open-mode warning when no token is set
(`benchd.py:1440–1441`). No RLS-specific remediation is possible or warranted; the RLS-equivalent
observations are recorded here for completeness and are expected to be owned by the auth/authz and
control-plane domains, which is why this report returns **no RLS findings**.

No findings are reported. An accurate empty result is the correct outcome for a non-applicable
domain where no Supabase/Postgres artifacts exist.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Supabase migrations | — | Postgres schema versioning | Absent | N/A | No `supabase/`, no `*.sql` |
| SQL schema | — | Table definitions | Absent (as SQL) | N/A | Schema defined in Python: `benchd.py:95–142` (SQLite DDL) |
| RLS enablement | — | Row-level security | Absent | N/A | SQLite has no RLS feature |
| Policies | — | Access predicates | Absent | N/A | Equivalent: handler checks `benchd.py:572–615` |
| Grants/roles | — | DB roles/privileges | Absent | N/A | Equivalent: operator vs runner, `benchd.py:593–615` |
| Storage bucket policies | — | Object storage ACLs | Absent | N/A | Artifacts served by handler, gated by token |
| Functions/triggers | — | DB-side logic | Absent | N/A | None defined |
| `SECURITY DEFINER` / `search_path` | — | Privilege-escalation surface | Absent (N/A) | N/A | No SQL functions exist |
| Generated types | — | DB type generation | Absent | N/A | Stdlib only; no codegen |
| App queries | `server/web/app.js:153–155`; `server/benchd.py:696+` | Client/server data path | Present (SQLite) | Low | Bearer-token gated HTTP API |
| Tenant/user matching | — | Per-tenant isolation | Absent (N/A) | N/A | No multi-tenant model; single operator + runners |
| Admin bypass | `benchd.py:610–611` | Operator full access | Present by design | Low | Documented single shared operator token |
| Service role usage | — | Elevated DB role | Absent (N/A) | N/A | No service-role concept |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Supabase migrations | 0 | No `supabase/` or `*.sql`; `grep -ri supabase` = 0 | N/A domain | None (document non-applicability) |
| SQL schema | 1 | SQLite DDL in `benchd.py:95–142` | Schema not a standalone SQL artifact | Optional: not required for scope |
| RLS enablement | 0 | No Postgres; SQLite has no RLS | N/A | None |
| Policies | 1 | Handler checks `benchd.py:572–615` (RLS analogue) | No DB-level policy layer | Owned by auth/authz domain |
| Grants/roles | 1 | Two-role token model `benchd.py:593–615` | No per-user/DB grants | Owned by auth/authz domain |
| Storage bucket policies | 0 | No object storage; artifacts token-gated | N/A | None |
| Functions/triggers | 0 | None defined | N/A | None |
| Security definer | 0 | No SQL functions | N/A | None |
| Generated types | 0 | None; stdlib-only | N/A | None |
| App queries | 3 | `app.js:153–155` + `benchd.py` API | Client/server covered by shared token | Owned by control-plane domain |
| Tenant/user matching | 0 | No tenant model | N/A | None |
| Admin bypass | 2 | Operator token bypasses scoping (`benchd.py:610–611`) | Shared, non-attributable | Owned by auth/authz domain |

Scores of `0` denote "not applicable / absent", not "unimplemented requirement", per the shared
scoring rule (`0`: absent or not assessable).

## Detailed Review

### Item: Datastore (SQLite, not Supabase/Postgres)

- Evidence: `server/benchd.py:36` (`import sqlite3`), `:151` (`sqlite3.connect`), `:95–142`
  (`CREATE TABLE`/`CREATE INDEX`), `:160–176` (`PRAGMA table_info` + `ALTER TABLE ADD COLUMN`).
- What it does: Stores runners, runs, phases, telemetry, logs, commands, events, artifacts, and
  schedules in a local SQLite file.
- How it appears to work: DDL is created idempotently on startup; lightweight in-code migrations add
  columns when `PRAGMA table_info` shows them missing.
- Dependencies: `sqlite3` stdlib; WAL journal mode.
- Current controls: none at DB layer (SQLite has no RLS/roles).
- Missing controls: N/A for RLS.
- Risks: Authorization depends entirely on correct handler gating.
- Recommended improvement: none within this domain.
- Suggested tests: none (out of domain).
- Suggested docs: note in docs that the control plane is SQLite, not Supabase.

### Item: RLS-equivalent authorization (handler-enforced)

- Evidence: `server/benchd.py:562–615` — `_bearer`, `_runner_from_bearer`, `_is_operator`,
  `_runner_ok`, `_caller`, `_may_act_as`, `_may_write_run`; enforced at `do_GET` (:637, :642, :645),
  `do_DELETE` (:658), `do_POST` (:688).
- What it does: Distinguishes *operator* (shared token) from *runner* (per-runner `api_key`); runners
  may only act on their own runner id and write their own runs; operator may act on any row.
- How it appears to work: Every API entry point calls an auth predicate before dispatching to the
  query layer.
- Current controls: constant-time operator comparison (`secrets.compare_digest`, :576); opaque keys
  (`secrets.token_urlsafe(32)`, :1203); `api_key` stripped from public payloads (`:423`); token
  redaction in logs (`:524`); explicit open-mode warning (`:1440–1441`).
- Missing controls (RLS-specific): no database-level policy as a second enforcement layer.
- Risks: If a query path were ever reached without the handler predicate, there is no DB-level
  backstop (contrast with Postgres RLS).
- Recommended improvement: keep the "all queries go through the gated dispatcher" invariant; consider
  asserting it in tests (owned by auth/authz).
- Suggested tests: request-level tests that a runner bearer is rejected on another runner's rows.
- Suggested docs: describe the operator/runner model as the repo's tenant-matching equivalent.

### Item: Open mode when no token is configured

- Evidence: `server/benchd.py:573–574` and `:595–596` — `_is_operator`/`_caller` return `True` when
  `self.token is None`; `:1440–1441` prints `WARNING: no BENCHD_TOKEN set`.
- What it does: With no token, every request is treated as operator and runner.
- How it appears to work: Intentional for local/lab convenience, explicitly warned.
- Current controls: startup warning; docs reference `BENCHD_TOKEN`.
- Risks: An unauthenticated deployment has no access control at all.
- Recommended improvement: bind to loopback by default when token is unset (owned by auth/authz/control-plane domains).
- Suggested tests: assert a warning/refusal when unbound with no token.
- Suggested docs: document this as a non-production mode.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| RLS-001 | Supabase migrations | no `supabase/`, no `*.sql` | N/A — not Supabase | Not applicable | N/A | None |
| RLS-002 | SQL schema | `benchd.py:95–142` | SQLite DDL in Python | Not a standalone SQL artifact | N/A | None |
| RLS-003 | RLS enablement | `sqlite3` only (`benchd.py:36,151`) | DB has no RLS | Not applicable | N/A | None |
| RLS-004 | Policies | `benchd.py:572–615` | Handler-level predicates | No DB policy layer | N/A | Owned by auth/authz |
| RLS-005 | Grants/roles | `benchd.py:593–615` | operator vs runner token | No per-user grants | N/A | Owned by auth/authz |
| RLS-006 | Storage bucket policies | artifacts served by gated handler | Token-gated download | No bucket concept | N/A | None |
| RLS-007 | Functions/triggers | none found | N/A | Not applicable | N/A | None |
| RLS-008 | Security definer | no SQL functions | N/A | Not applicable | N/A | None |
| RLS-009 | Generated types | none found | N/A | Not applicable | N/A | None |
| RLS-010 | App queries | `app.js:153–155` | Bearer/`?token=` API | Shared token | N/A | Owned by control-plane |
| RLS-011 | Tenant/user matching | single operator + runners | Runner→own rows only | No tenant model | N/A | None |
| RLS-012 | Admin bypass | `benchd.py:610–611` | Operator may write any run | Shared, non-attributable | N/A | Owned by auth/authz |

## Findings

None. The domain is not applicable: no Supabase, Postgres, SQL schema, migrations, RLS policies,
grants/roles, storage bucket policies, functions/triggers, `SECURITY DEFINER`, or generated DB types
exist in the repository. Fabricating findings here would violate the shared evidence discipline.

The RLS-equivalent observations (handler-enforced authorization over SQLite; open mode when no token
is set; shared operator token) are recorded above for traceability and are expected to be owned and
scored by the authentication/authorization, control-plane, and secrets domains, not by this one.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| None in the Supabase/RLS domain (no such surface) | N/A | N/A | N/A | Repo-wide searches: 0 Supabase/Postgres/RLS matches | N/A |

## Recommendations

### Immediate / Release Blocking

None from this domain.

### This Week

None from this domain.

### This Month

- Optionally note in `docs/` that the control plane intentionally uses SQLite (not Supabase/Postgres),
  so future audits do not re-open this non-applicable domain.

### Later / Platform Evolution

- If the project ever adopts Postgres/Supabase, re-run this prompt against real migrations and
  enforce RLS + `WITH CHECK` + `SECURITY DEFINER search_path` from day one.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add a one-line "datastore: SQLite (no Postgres/Supabase/RLS)" note | Prevents repeat non-applicable audits | `docs/CONTROL_PLANE.md` | Grep the doc for the note |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| None (domain not applicable) | — | — | — | — |

## Suggested Tests

- No RLS tests are possible or required (no Postgres). The RLS-equivalent request-authorization tests
  (runner cannot touch another runner's rows; operator can) belong to the auth/authz domain.

## Suggested Documentation Updates

- `docs/CONTROL_PLANE.md`: state explicitly that persistence is SQLite via `server/benchd.py`, and
  that there is no Supabase/Postgres/RLS surface.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is a Postgres/Supabase backend planned? | Would activate this entire domain | Roadmap / `docs/FUTURE_WORK.md` or an operator decision |
| Should the datastore choice be documented as intentional? | Avoids repeat non-applicable findings | `docs/CONTROL_PLANE.md` edit |

## Appendix

### Domain classification

`NOT APPLICABLE`. Evidence: the repository is a workstation benchmark/stress toolkit; the only
datastore is SQLite inside `server/benchd.py`; repo-wide searches for
`supabase|Supabase|postgres|PostgreSQL|RLS|CREATE POLICY|row-level security|service_role` and for any
`*.sql`/migration/storage artifact returned zero relevant matches.

### Commands actually run

```text
git -C C:\temp\bench-test rev-parse HEAD                       -> 72c18734aea2e5b3381254b74205d0b2944bafab
git -C C:\temp\bench-test branch --show-current                -> main
git -C C:\temp\bench-test merge-base --is-ancestor b9167095... HEAD -> exit 0 (ancestor)
grep -ri "supabase" C:\temp\bench-test                         -> 0 matches
grep -riE "postgres|PostgreSQL|RLS|CREATE POLICY|row level security|service_role" -> no Postgres/RLS matches
git ls-files | filter '\.sql$|migrat|schema|supabase|rls|storage|seed' -> no matches
recursive scan for *.sql / supabase* (incl. untracked)         -> no matches
grep -n "sqlite3|CREATE TABLE|PRAGMA" server/benchd.py          -> sqlite3 at :36, DDL :95-142, :151-176
read server/benchd.py:555-704                                   -> handler auth model
grep -n "Authorization|token" server/web/app.js                -> Bearer/`?token=` client path
```

## Findings

_No findings in this domain._
