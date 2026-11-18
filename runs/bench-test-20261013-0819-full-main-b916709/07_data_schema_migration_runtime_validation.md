# 07_data_schema_migration_runtime_validation — Prompt 07 - Data, Schema, Migration, and Runtime Validation Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `07_data_schema_migration_runtime_validation.md` (area DATA, prompt)

## Verification Performed

# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: bench-test full-domain audit (repo-deep-dive harness)
- Run: 20261013-bench-test
- Repository: `C:\temp\bench-test` (MaineCyberTech/bench-test)
- Branch: main
- Commit SHA: `72c18734aea2e5b3381254b74205d0b2944bafab` (VERSION 1.11.4)
- Generated at: 2026-10-13
- Auditor: domain subagent, domain 07 (DATA)
- Area code: DATA
- Output path (framework convention): `docs/audits/{name}/{run}/07_data_schema_migration_runtime_validation.md`
- Scope limitations: read-only audit; no review of external upstream data (GitHub), no restoration/backup exercise, no load test. The lab/CI were not exercised. Note: the brief named commit `b9167095…`, but the working tree is at `72c18734` (one commit newer, "fix(security)…"). All line numbers below are at the checked-out HEAD `72c18734`; the discrepancy is itself evidence of a moving target.

## Scope

Reviewed the only persistent data store in the repository — the stdlib SQLite database opened by the control plane `server/benchd.py` — plus the runtime validators that feed it and the import path that backfills it. Specifically:

- **Schema / tables / indexes / constraints / foreign keys:** `server/benchd.py:94-143` (SCHEMA), `:151-157` (Store).
- **Migrations:** `server/benchd.py:159-176` (`_migrate`).
- **Runtime validators:** `server/benchd.py:57-76` (`sanitise_sample`), `:382-401` (`safe_id`, `int_arg`), `:545-559` (`_body`), and each POST handler.
- **Data lifecycle / retention / deletes:** `server/benchd.py:653-681` (DELETE), `:1277-1398` (scheduler/reaper loop).
- **Config/env validation:** `server/benchd.py:1401-1429`, `server/benchd.conf.example`.
- **Import / backfill client usage:** `server/import_results.py` and the shared merge helpers in `bench/benchreport.py`.
- **Docs:** `docs/DATA.md`, `docs/CONTROL_PLANE.md`.

Not reviewed (not applicable to this repository, with evidence): ORM/entity mapping, generated DB types, RLS policies, tenant columns, JSON-Schema contracts, and a migration CI job. `server/benchd.py:36` imports `sqlite3` directly and there is no ORM dependency anywhere in the tree; there is no `policy`/`rls`/`tenant` code (grep returns nothing), and no workflow runs migrations (`.github/workflows/` only build the app, ISO and release). These categories are scored 0/N-A in the scorecard rather than treated as missing features.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `server/benchd.py:94-143` | Source (SCHEMA) | Defines all 9 tables and 8 indexes | No FK, no UNIQUE beyond PK, no audit/retention columns |
| `server/benchd.py:151-176` | Source (Store/_migrate) | Connection setup + migrations | Pragma/WAL only; additive ALTERs, no version |
| `server/benchd.py:545-559, 683-693` | Source | Body parsing + error handling | No object-type validation; 500 leak |
| `server/benchd.py:653-681` | Source | DELETE routes | Run delete omits `logs` |
| `server/benchd.py:1053-1108` | Source | Phase + telemetry writes | Check-then-insert phase upsert |
| `server/benchd.py:1143-1160, 1315-1335` | Source | Finish + reaper | No version precondition |
| `server/benchd.py:1277-1398` | Source | Lifecycle jobs | No retention/prune |
| `server/benchd.py:1401-1429` | Source | Config | Only BENCHD_TOKEN honoured |
| `server/benchd.conf.example:8-9` | Config | Documents BENCHD_DB | Not read by any code |
| `server/import_results.py` | Source | Backfill client | Reuses `benchreport` aliases/merge |
| `bench/benchreport.py:54` (`CSV_ALIASES`), `:190` (`DASH_FIELDS`) | Source | Field naming contract | Every sampler column must map (docs/DATA.md §4) |
| `tests/test_control_plane.py` | Test | Control-plane coverage | Asserts malformed query, not malformed body |
| `docs/CONTROL_PLANE.md:132, 189-254` | Docs | Documents delete/data/growth | "delete a run (+data)"; DB growth |
| `docs/DATA.md` | Docs | Data inventory | Describes metrics, not DB lifecycle |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse HEAD` → `72c18734…`, branch `main`, `VERSION` = `1.11.4` | Command | Bind report to a commit | Brief's `b9167095` is one commit behind |
| Repro `repro_delete_logs.py` (in-process server via `tests/harness.py`) | Executed | Headline claim | After DELETE 200 and run detail 404, `logs` rows = 2 (orphaned) |
| Repro `repro_logs_after_delete.py` | Executed | Reachability of deleted data | `GET /runs/<id>/logs` returned 200 with the line after the run was deleted |
| Repro `repro_validation.py` | Executed | Body validation + phase race + pragmas | Non-object bodies → 500; phases count = 2 for one seq; `PRAGMA foreign_keys` = 0 |
| `grep -rn "BENCHD_DB"`, `"foreign_keys"`, `"_migrate"`, `user_version` | Command | Config/FK/migration evidence | BENCHD_DB only in the example; FK pragma never set; no user_version |
| `grep -rn -i "retention|prune|purge|vacuum|DELETE FROM" server/ bench/ live/` | Command | Retention evidence | Only manual deletes in benchd; no aging job |
| Manual read of `docs/CONTROL_PLANE.md` and `docs/DATA.md` | Read | Doc-vs-code consistency | "delete a run (+data)" vs orphaned logs |

### Reproduction detail (headline claim)

Using the repository's own harness (`tests/harness.py`) against HEAD:

```
register 200
create run 200 c69c64d2-…
post log 200 {'ok': True, 'n': 2}
before delete: {'logs': 2, 'telemetry': 1}
delete run 200
after delete: {'logs': 2, 'telemetry': 0, 'runs': 0}
ORPHANED LOGS: 2
```

and the follow-up showing the data is still served after deletion:

```
delete: 200
run detail after delete: 404
logs AFTER delete: 200 {'run_id': '9f2e9459-…', 'lines': [{'line': 'SECRET-LINE-abc'}]}
```

Second repro:

```
list body -> (500, '{"error": "AttributeError: \'list\' object has no attribute \'get\'"}')
phase rows for seq=1: 2
PRAGMA foreign_keys: {'foreign_keys': 0}
unique indexes on phases: [CREATE INDEX idx_phases_run ON phases(run_id, seq)]
```

**Supported / partially supported / unsupported claims:** the delete gap is **supported** (reproduced). The `finish`-vs-reaper overwrite is **not reproduced** (code-path reasoning only; confidence Medium). Everything else is directly captured.

## Executive Summary

The repository's data layer is a single stdlib SQLite database (`server/benchd.py`) that stores runners, runs, phases, telemetry, logs, events, artifacts, commands and schedules. It is deliberately dependency-free and works well for its stated purpose — a lab-scale fleet control plane — and several data-safety controls are already good:

- Runtime telemetry validation exists and is tested: impossible percentages (`fan_pct`/`gpu_util`/`cpu_util` outside 0–100) are dropped rather than clamped (`server/benchd.py:57-76`), and `tests/test_control_plane.py:125-141` proves it including the 0/100 boundaries.
- Legacy positional telemetry and named telemetry are both supported and tested (`tests/test_control_plane.py:107-123`), so old CSVs still import.
- A single shared alias table (`bench/benchreport.py:54`) and `import_results.py` reuse it, so live and backfilled runs agree (`docs/DATA.md:90-97`).
- WAL journaling is enabled (`server/benchd.py:154`).
- The import client parses timestamps defensively (`import_results.py:66-88`) and caps telemetry (`:112-150`).

The significant risks are all about **data lifecycle and schema discipline**, and the single most concrete one is a deletion bug: `DELETE /api/v1/runs/<id>` is documented as "delete a run (+data)" but it does not delete the run's `logs`, which therefore stay orphaned and remain downloadable. This is compounded by there being **no foreign keys** (so nothing prevents the class), **no retention policy anywhere** (telemetry/logs/artifacts grow forever), **no schema versioning** (migrations are best-effort ALTERs), and a **non-atomic phase upsert** with no unique constraint. Request-body validation has a gap (non-object JSON → HTTP 500 with an internal exception) even though the test suite already asserts the same property for query strings.

Recommended next actions: (1) delete (or cascade) run logs and add a test; (2) add FKs + `PRAGMA foreign_keys=ON`; (3) define and implement a retention window; (4) add a schema_migrations table; (5) make the phase upsert atomic with `UNIQUE(run_id, seq)`; (6) reject non-object bodies with 400.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| SQLite schema | `server/benchd.py:94-143` `SCHEMA` | 9 tables, 8 indexes | Present, functional | Medium | No FK/UNIQUE/audit/retention columns |
| Migration | `server/benchd.py:159-176` `Store._migrate` | Add columns to old DBs | Partial (3 tables, 7 cols) | Medium | No version/rollback/drift |
| FK/cascade | `server/benchd.py:151-157` | Referential integrity | Absent | Medium | `PRAGMA foreign_keys` = 0 |
| Runtime validators | `sanitise_sample`, `safe_id`, `int_arg`, `_body` | Reject bad input | Partial | Medium | Query OK; body not type-checked |
| Telemetry extra | `server/benchd.py:1081-1094, 111-115` | Arbitrary metric columns | Present | Low | Stored as JSON blob per row |
| Logs | `server/benchd.py:116-118, 1117-1130` | Console/exec output | Present | High | Not deleted with the run |
| Retention | (none) | Age out data | Absent | Medium | No owner/policy for any table |
| Soft delete / audit | (none) | Track deletion/edits | Absent | Low | Hard deletes only |
| Deletes | `server/benchd.py:653-681` | Remove run/runner/schedule | Partial | High | Run delete omits logs |
| Reapers | `server/benchd.py:1315-1398` | Status hygiene | Present | Low | No data pruning |
| Config parsing | `server/benchd.py:1401-1429` | Token/DB selection | Partial | Low | BENCHD_DB documented, unused |
| Backfill import | `server/import_results.py` | Load historical results | Present | Low | Reuses shared merge logic |
| Generated DB types | (none) | Typed DB layer | N/A | N/A | stdlib `sqlite3`, no ORM |
| RLS / tenant columns | (none) | Multi-tenant isolation | N/A | N/A | Single-operator lab tool |
| JSON schema | (none) | Request/response contract | N/A | Low | Handlers validate ad hoc |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database schema | 3 | `server/benchd.py:94-143` | No FK/UNIQUE/audit/retention columns | Add constraints + metadata columns |
| Migrations | 1 | `server/benchd.py:159-176` | No versioning, rollback, or drift check | Add schema_migrations + drift check |
| Constraints | 1 | No UNIQUE beyond PK (`:107-110`) | Phase/seq not unique; no CHECK | `UNIQUE(run_id, seq)`, CHECKs |
| Indexes | 4 | `server/benchd.py:135-142` | Reasonable set; no index on `runs(status)` | Add for reaper/trends scans |
| Foreign keys/cascades | 0 | `PRAGMA foreign_keys` = 0 | None declared or enforced | FKs + `PRAGMA foreign_keys=ON` |
| RLS | 0 (N/A) | No RLS/tenant code | Not applicable (no multi-tenant) | None |
| Tenant columns | 0 (N/A) | No tenant column | Not applicable | None |
| Soft deletes | 0 | `:653-681`, `:94-143` | Hard delete only | `deleted_at` + filtering |
| Audit fields | 1 | `:94-143` | No created/updated/by | Add audit columns |
| Retention | 0 | No prune anywhere | No policy/owner | Implement + document |
| Seeds/fixtures | 2 | `examples/`, test fixtures | No DB seed path | Document fixture loading |
| Generated DB types | 0 (N/A) | No ORM | Not applicable | None |

## Detailed Review

### Item: SQLite schema (`server/benchd.py:94-143`)

- Evidence: `SCHEMA` creates `runners, runs, phases, telemetry, logs, commands, events, artifacts, schedules` plus 8 indexes.
- What it does: one row per entity; child tables keyed by `run_id`.
- How it works: `executescript(SCHEMA)` (idempotent via `IF NOT EXISTS`) then `_migrate()`.
- Dependencies: stdlib `sqlite3`, file at `server/data/benchd.sqlite` (`:50`).
- Current controls: primary keys; WAL; `MAX_BODY` cap (`:55`).
- Missing controls: foreign keys, unique constraints on natural keys, CHECK constraints, audit/retention columns.
- Risks: orphan rows, schema drift (see findings).
- Recommended improvement: add FKs + `ON DELETE CASCADE`, `UNIQUE(run_id, seq)`, timestamps.
- Suggested tests: constraint tests (duplicate seq, orphan insert).
- Suggested docs: a `docs/SCHEMA.md` or a section in `docs/CONTROL_PLANE.md`.

### Item: Migrations (`server/benchd.py:159-176`)

- Evidence: guarded `ALTER TABLE ADD COLUMN` for `runners` (api_key, machine_id, ephemeral, instance), `telemetry` (extra), `runs` (system, preset).
- What it does: makes new columns exist on upgraded DBs.
- How it works: `PRAGMA table_info` check per column; no transaction/version record.
- Current controls: idempotent column adds; `Store.commit()` after.
- Missing controls: version tracking, down migrations, drift detection, index migration.
- Risks: silent un-applied schema changes on old DBs; no audit of which version a DB is.
- Recommended improvement: `schema_migrations`/`PRAGMA user_version`.
- Suggested tests: open a fixture DB at v(N-1) and migrate.
- Suggested docs: migration/rollback runbook.

### Item: Runtime validation (`sanitise_sample`, `safe_id`, `int_arg`, `_body`)

- Evidence: `sanitise_sample` drops out-of-range percentages (`:57-76`); `safe_id` restricts ids (`:382-387`); `int_arg` clamps query ints (`:395-401`); `_body`/`do_POST` lack object-type validation (`:545-559`, `:683-693`).
- What it does: prevents implausible telemetry and path/HTML-bearing ids entering storage.
- Current controls: strong on query strings and telemetry; tested (`tests/test_control_plane.py:125-215`).
- Missing controls: object-type check for JSON bodies; field-level schema.
- Risks: 500 + internal exception text on malformed body.
- Recommended improvement: reject non-dict bodies with 400; add per-route required fields.
- Suggested tests: extend the malformed-input block to bodies.
- Suggested docs: document the accepted body shapes (already partly in `docs/CONTROL_PLANE.md:147-166`).

### Item: Data lifecycle (deletes, retention, reapers)

- Evidence: DELETE (`:653-681`); reapers (`:1315-1398`); no pruning.
- What it does: removes runs/runners/schedules and fixes stale statuses.
- Current controls: commands/schedules cleaned for deleted/reaped runners; ephemeral runners reaped.
- Missing controls: logs omitted on run delete; no retention for telemetry/logs/events/artifacts.
- Risks: data a user believes deleted persists (finding 1); unbounded growth (finding 2).
- Recommended improvement: cascade deletes + retention job.
- Suggested tests: post-delete zero-row assertions per table; retention boundary test with mixed ages.
- Suggested docs: document "what DELETE removes" precisely and the retention window.

### Item: Import/backfill client (`server/import_results.py`)

- Evidence: reuses `CSV_ALIASES`/`_merge_into`/`_hardware_verdicts` from `benchreport` (`:30-37`); `read_telemetry` caps and reconstructs timestamps (`:112-150`); `epoch()` tolerates 7-digit fractions (`:66-88`).
- What it does: creates one run per historical session over the API.
- Current controls: defensive parsing, shared alias logic, cap 1500 rows, windowing by mtime.
- Missing controls: none material for this domain (it is a client; the server validates).
- Risks: mtime-based window heuristics could mis-attribute sessions (out of domain scope).
- Recommended improvement: none required for DATA.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DATA-001 | Delete a run removes all its data | `server/benchd.py:665-672`; reproduced | Deletes phases/telemetry/events/artifacts | Logs (and commands by run_id) retained & still served | High | Add logs to the delete/cascade |
| DATA-002 | Data ages out / retention | no prune in `:1277-1398` | None | No retention for any table | Medium | Retention job + config |
| DATA-003 | Referential integrity enforced by DB | `PRAGMA foreign_keys`=0; `:94-143` | Hand-written deletes | No FK/cascade | Medium | FKs + pragma ON |
| DATA-004 | Schema version known/applied | `server/benchd.py:159-176` | Additive ALTERs | No version/rollback/drift | Medium | schema_migrations |
| DATA-005 | Phase write is idempotent | `server/benchd.py:1053-1069` | SELECT-then-INSERT | No UNIQUE(run_id,seq) | Medium | Atomic upsert + UNIQUE |
| DATA-006 | Malformed body rejected, not 500 | `server/benchd.py:545-559`; reproduced | None | Non-dict body → 500 + leak | Low | Type-check body → 400 |
| DATA-007 | Concurrent/late writes do not clobber | `server/benchd.py:1146-1152` | None | No version/ETag; reaper race | Low | Status/version precondition |
| DATA-008 | Deletions are auditable/recoverable | `server/benchd.py:653-681` | None | Hard delete, no audit | Low | Soft delete + audit fields |
| DATA-009 | Config keys are honoured | `benchd.conf.example:8-9` | Only BENCHD_TOKEN | BENCHD_DB ignored | Low | Implement or remove |
| DATA-010 | Telemetry domain validation | `server/benchd.py:57-76`; tests | Drops 0–100 violations | (control present) | N/A | Maintain |
| DATA-011 | RLS / tenant isolation | none | Not applicable | — | N/A | — |
| DATA-012 | Generated DB types | none (stdlib sqlite3) | Not applicable | — | N/A | — |

## Findings

Full machine-readable copy: `07_data_schema_migration_runtime_validation.json`.

### Finding: DATA-P1 — DELETE /api/v1/runs/<id> does not delete the run's logs (they stay orphaned and remain readable)

- Severity: P1 · Confidence: High · Area: DATA
- Evidence: `server/benchd.py:665-672` (delete loop omits `logs`), `:116-118` (logs table), `:802-807` (`_run_logs` has no run-existence check), `docs/CONTROL_PLANE.md:132` ("delete a run (+data)"); reproduced (DELETE 200 then run detail 404 but `GET /runs/<id>/logs` 200 with the line).
- What is happening: the run row and four child tables are deleted; `logs` rows are not; the logs endpoint keeps serving them.
- Why it matters / impact: operator-initiated erasure silently fails for console and remote-terminal output, which may contain sensitive data; rows persist forever.
- Recommended fix: add `logs` (and run-scoped commands) to the delete, or add `ON DELETE CASCADE` + `PRAGMA foreign_keys=ON`; test it.
- Suggested validation: delete a run, assert zero rows in every run-scoped table and 404 on `/logs`.
- Status: open.

### Finding: DATA-P2 — No retention/aging for telemetry, logs, events, artifacts

- Severity: P2 · Confidence: High
- Evidence: `server/benchd.py:94-143`, `:1376-1398`, `:1070-1108`; `docs/CONTROL_PLANE.md:254`.
- Impact: unbounded DB/backup growth and degrading history scans; no table has an owner or retention window.
- Recommended fix: configurable retention job (N days or rows/run), documented and tested.
- Status: open.

### Finding: DATA-P3 — No foreign keys / no FK enforcement

- Severity: P2 · Confidence: High
- Evidence: `server/benchd.py:94-143` (no `REFERENCES`), `:151-157` (no `PRAGMA foreign_keys=ON`; observed 0), `:665-680` (hand-maintained deletes).
- Impact: integrity depends on hand-written SQL; orphan rows are unguardable and already occur.
- Recommended fix: FKs with `ON DELETE CASCADE` + pragma ON; tests.
- Status: open.

### Finding: DATA-P4 — No schema versioning / rollback / drift detection

- Severity: P2 · Confidence: High
- Evidence: `server/benchd.py:159-176`, `:94-143`; no `user_version`/migration table anywhere.
- Impact: no record of DB schema version; SCHEMA/`_migrate` drift is silent; no down path.
- Recommended fix: `schema_migrations` table (or `PRAGMA user_version`) + startup drift check.
- Status: open.

### Finding: DATA-P5 — Non-atomic phase upsert with no UNIQUE(run_id, seq)

- Severity: P2 · Confidence: Medium
- Evidence: `server/benchd.py:1053-1069`, `:107-110`, `:137`; reproduced duplicate seq rows.
- Impact: duplicate phase rows from concurrent/replayed posts; idempotency not guaranteed.
- Recommended fix: `UNIQUE(run_id, seq)` + `INSERT … ON CONFLICT DO UPDATE`.
- Status: open.

### Finding: DATA-P6 — Request bodies not validated as objects; BENCHD_DB documented but ignored

- Severity: P3 · Confidence: High
- Evidence: `server/benchd.py:545-559`, `:683-693` (reproduced 500 for list/string/null/number bodies), `tests/test_control_plane.py:206-215`, `server/benchd.conf.example:8-9` vs `:1413-1429`.
- Impact: malformed body → 500 + internal exception text; documented DB path silently ignored.
- Recommended fix: type-check bodies (400), implement or remove BENCHD_DB, extend tests.
- Status: open.

### Finding: DATA-P7 — No optimistic locking / version preconditions

- Severity: P3 · Confidence: Medium
- Evidence: `server/benchd.py:1146-1152`, `:1315-1335`, `:1059-1060`; no ETag/version anywhere.
- Impact: a late `/finish` can flip a reaped `failed` run back to `done`; blind overwrites.
- Recommended fix: status/version precondition on `/finish`; test reaper-then-finish ordering.
- Status: open.

### Finding: DATA-P8 — Hard deletes, no soft delete/audit fields

- Severity: P3 · Confidence: High
- Evidence: `server/benchd.py:665-680`, `:94-143`; `docs/CONTROL_PLANE.md:223`.
- Impact: deletions/edits are unauditable; accidental delete is unrecoverable without an (undocumented) backup.
- Recommended fix: `deleted_at` + soft-delete filtering or a deletion journal; audit columns; backup/restore docs.
- Status: open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Deleted-run logs persist and stay readable | High | High once a run is deleted | Privacy/retention failure | `server/benchd.py:665-672`, `:802-807` | Fix delete/cascade |
| Unbounded DB growth | Medium | High over time | Storage/backup/scan cost | `:1277-1398` | Retention job |
| Orphan rows from future delete paths | Medium | Medium | Integrity/consistency | No FK | FKs + pragma |
| Schema drift on upgraded DBs | Medium | Medium | Silent wrong schema | `:159-176` | Versioning + drift check |
| Duplicate phase rows | Low | Low | UI/count skew | `:1053-1069` | UNIQUE + upsert |
| 500 + exception leak on bad body | Low | Medium | Info leak / bad UX | `:545-559` | Body type check |

## Recommendations

### Immediate / Release Blocking
- Delete (or cascade) a run's `logs` on `DELETE /api/v1/runs/<id>`; add the regression test (DATA-P1).

### This Week
- Add `FOREIGN KEY … ON DELETE CASCADE` and `PRAGMA foreign_keys=ON` (DATA-P3).
- Make the phase upsert atomic with `UNIQUE(run_id, seq)` (DATA-P5).

### This Month
- Add a `schema_migrations` table / `user_version` and a startup drift check (DATA-P4).
- Implement a configurable retention job and document the policy (DATA-P2).
- Reject non-object JSON bodies with 400; implement or remove `BENCHD_DB` (DATA-P6).

### Later / Platform Evolution
- Soft delete + audit columns, and a documented/tested backup-restore procedure (DATA-P8).
- Version preconditions on `/finish` and phase updates (DATA-P7).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `"logs"` to the delete loop | Removes the P1 deletion gap | `server/benchd.py:668` | Repro script asserts 0 rows |
| Add `?` run-existence check to `_run_logs` | Stops serving data of deleted runs | `server/benchd.py:802-807` | 404 after delete |
| `if not isinstance(b, dict): return 400` after `_body()` | Rejects malformed bodies cleanly | `server/benchd.py:545-559` | POST list → 400 |
| Remove/adjust the `BENCHD_DB` line in the example | Removes config drift | `server/benchd.conf.example:9` | grep |
| Document "what DELETE removes" | Matches docs to code | `docs/CONTROL_PLANE.md:132` | Review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Retention job + config + docs | P2 | Control-plane owner | M | None |
| FK/cascade migration | P2 | Control-plane owner | M | schema_migrations |
| schema_migrations framework | P2 | Control-plane owner | M | None |
| Atomic phase upsert | P2 | Control-plane owner | S | None |
| Body schema validation | P3 | Control-plane owner | S | None |
| Soft delete + audit fields | P3 | Control-plane owner | M | Retention design |
| Backup/restore runbook | P3 | Ops owner | S | None |

## Suggested Tests

- **Unit / API:** delete a run, then assert zero rows in `phases, telemetry, logs, events, artifacts` and 404 on `/runs/<id>/logs`; `PRAGMA foreign_keys` is ON; inserting a child for a missing parent fails.
- **Regression:** POST the same `/phase` seq twice (concurrently) → exactly one row; malformed bodies (list/string/null/number) → 400 not 500.
- **Integration:** backfill via `import_results.py` into a fresh DB, then delete a run, verifying the same invariants.
- **CI:** a migration test that opens a fixture DB at v(N-1) and asserts the migrated schema matches a v(N) reference (`table_info` + `index_list`).
- **Manual:** retention dry-run over a copy of a real DB with mixed-age rows; confirm only expired rows are removed.

## Suggested Documentation Updates

- `docs/CONTROL_PLANE.md`: state exactly which tables `DELETE /runs/<id>` and `DELETE /runners/<id>` remove; document the retention window and owner; document the schema-migration/rollback procedure.
- New `docs/SCHEMA.md` (or a section): table list, keys, indexes, FKs, and the `schema_migrations` policy.
- `server/benchd.conf.example`: implement or drop `BENCHD_DB`, and list the retention config key once added.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there an out-of-band cleanup job that purges the SQLite DB (cron/systemd timer)? | Would mitigate DATA-P2 | Host crontab / systemd timer inventory (not in repo) |
| Is there a backup/restore procedure for `benchd.sqlite`? | Determines recoverability of hard deletes | Ops runbook (not in repo) |
| Is the deployed DB grown large already (row counts)? | Confirms retention urgency | Access to the live `server/data/benchd.sqlite` |
| Does any client depend on logs surviving run deletion? | Avoids breaking a consumer if we cascade | Web/CLI history views |
| Why does the brief name commit `b9167095` while HEAD is `72c18734`? | Binds findings to a commit | Orchestrator manifest |

## Appendix

Tables and index inventory (from `SCHEMA`, `server/benchd.py:94-143`):

```
runners(id PK, name, os, kind, version, capabilities, first_seen, last_seen,
        status, current_run, addr, git, api_key, machine_id, ephemeral, instance)
runs(id PK, runner_id, host, label, profile, started, ended, status, exit_code,
     platform, gpu, driver, torch, summary, system, preset)
phases(id PK AUTOINCREMENT, run_id, seq, grp, label, status, t0, t1, detail)
telemetry(run_id, ts, elapsed, temp_c, fan_pct, power_w, gpu_util, gpu_fan_rpm,
          cpu_util, ram_used, sm_mhz, mem_used, extra)
logs(id PK AUTOINCREMENT, run_id, ts, stream, line)
commands(id PK, runner_id, run_id, kind, payload, status, created, sent, acked, result)
events(id PK AUTOINCREMENT, run_id, ts, level, message)
artifacts(id PK AUTOINCREMENT, run_id, name, kind, size, sha256, content)
schedules(id PK, runner_id, label, profile, kind, every_s, at_time, next_run,
          enabled, last_run, created, last_status)
indexes: runs(started), runs(runner_id), phases(run_id,seq), telemetry(run_id,ts),
         commands(runner_id,status), events(run_id,ts), logs(run_id,id),
         schedules(enabled,next_run)
```

`PRAGMA foreign_keys` = 0; no `REFERENCES`; `idx_phases_run` is non-unique. The repro scripts are kept outside the target at `C:\Users\Admin\AppData\Local\Temp\opencode\bench-dive\repro\` (`repro_delete_logs.py`, `repro_logs_after_delete.py`, `repro_validation.py`).

## Findings

| ID | Severity | Title |
|---|---|---|
| DATA-P1-001 | P1 | DELETE /api/v1/runs/<id> does not delete the run's logs; they stay orphaned in the DB and remain readable |
| DATA-P2-001 | P2 | No retention or aging policy for telemetry, logs, events or artifacts - the SQLite database grows without bound |
| DATA-P2-002 | P2 | Schema declares no foreign keys and never enables FK enforcement (PRAGMA foreign_keys = 0) |
| DATA-P2-003 | P2 | Migrations are best-effort additive ALTERs with no schema version tracking, rollback, or drift detection |
| DATA-P2-004 | P2 | Phase writes use a non-atomic check-then-insert with no UNIQUE(run_id, seq), so concurrent or replayed posts can create duplicate phase rows |
| DATA-P3-001 | P3 | Request bodies are not validated as JSON objects (non-object body returns 500 + internal exception), and the documented BENCHD_DB setting is ignored |
| DATA-P3-002 | P3 | No optimistic locking or version preconditions on mutations; a late /finish can overwrite a reaped run's terminal status |
| DATA-P3-003 | P3 | Hard deletes with no soft-delete/tombstone and no audit fields on any table |
