# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: DATA
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/07_data_schema_migration_runtime_validation.md
- Scope limitations: static review of SQLite schemas and JSON-schema validators; no production DB instance available.

## Scope

Reviewed the control-plane SQLite schema (`src/falcon_control/store.py`), the agent queue schema (`src/falcon_agent/queue.py`), the fleet-inventory schema (`automation/validation/fleet_inventory.py`), runtime validation (`api/generate_models.py` → `models_generated.validate_payload`), and retention/migration handling.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `src/falcon_control/store.py` | Source | CP schema (10 tables) | `CREATE TABLE IF NOT EXISTS` |
| `src/falcon_agent/queue.py` | Source | Queue/DLQ/meta | bounded, checksummed |
| `automation/validation/fleet_inventory.py` | Source | Inventory schema | raw identifiers |
| `src/falcon_common/models_generated.py` | Generated | Payload validation | from OpenAPI |
| `api/generate_models.py --check` | CI | Drift guard | in `ci/validate.sh` |
| `automation/validation/backup_edge_secrets.py` | Source | DB backup/retention | 7 backups |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Schema grep | Static | FK/index/retention | no FK, no retention |
| Idempotency growth trace | Static | Unbounded table | `idem_put` INSERT OR REPLACE keyed |
| `purge_expired` call-site grep | Static | Dead/lazy path | only tests call it |
| Migration grep | Static | Evolution | none found |

## Executive Summary

Data handling is solid for a lab: atomic file writes, a bounded checksummed queue with loss accounting, consistent SQLite backups, and strict JSON-schema validation of every payload. The gaps are lifecycle-oriented: no schema migration mechanism (only `CREATE TABLE IF NOT EXISTS`), no foreign keys, no retention/cleanup for the `idempotency`, `events`, `state_reports`, and `heartbeat_samples` tables, and the queue's age-expiry only runs opportunistically on enqueue.

## Inventory

| Table / store | Path | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| `sensors` | `store.py` | Identity/lifecycle | Good | Low | UNIQUE fingerprints |
| `bootstrap_tokens` | `store.py` | Enrollment | Good | Low | hashed, single-use |
| `desired_state` | `store.py` | Signed config | Good | Low | PK (sensor,rev) |
| `idempotency` | `store.py` | Replay store | Unbounded | Med | full bodies stored |
| `heartbeat_samples` | `store.py` | Latest heartbeat | 1 row/sensor | Low | — |
| `inventory` | `store.py` | Snapshot | 1 row/sensor | Low | — |
| `state_reports` | `store.py` | Append-only | Unbounded | Med | no retention |
| `events` | `store.py` | Append-only | Unbounded | Med | no retention |
| `update_manifests` | `store.py` | Signed offers | PK (sensor,version) | Low | — |
| `directives` | `store.py` | Recovery | consumed_at | Low | — |
| `audit_log` | `store.py` | Audit | Append-only | Med | no retention |
| `queue`/`dlq` | `queue.py` | Agent spool | Bounded | Low | — |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database schema | 4 | `store.SCHEMA` | no FK | DATA-P2-002 |
| Migrations | 1 | none | no evolution path | DATA-P2-003 |
| Constraints | 4 | PK/UNIQUE | no FK | DATA-P2-002 |
| Indexes | 3 | PK indexes only | no query indexes | DATA-P3-001 |
| Foreign keys/cascades | 1 | none | — | DATA-P2-002 |
| RLS | N/A | SQLite lab | — | — |
| Tenant columns | N/A | single-site | — | — |
| Soft deletes | 3 | states, not deletes | — | — |
| Audit fields | 4 | `audit_log` | no retention | DATA-P2-001 |
| Retention | 2 | none in CP | unbounded tables | DATA-P2-001 |
| Seeds/fixtures | 3 | tests build fixtures | — | — |
| Generated DB types | 3 | none (SQLite) | — | — |
| Request/response validators | 5 | `validate_payload` | — | — |
| Env/config validation | 3 | CLI preflight | partial | minor |

## Detailed Review

### Item: Idempotency store

- Evidence: `store.idem_get`/`idem_put`; `service._idempotent`
- What it does: caches successful (<500) responses keyed by (sensor, endpoint, key) to replay duplicates.
- Missing controls: no TTL, no prune, stores the full response body.
- Risks: unbounded DB growth (DATA-P2-001).

### Item: Queue expiry

- Evidence: `queue._evict`, `queue.purge_expired`; grep shows `purge_expired` called only from `tests/phase3/test_queue*.py`
- What it does: `_evict` drops priority-oldest and age-expired items on enqueue; `purge_expired` is not wired into the runner.
- Risks: if the agent stops enqueuing, expired items are never purged (DATA-P3-001).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DATA-001 | Schema | `store.SCHEMA` | typed columns | — | — | — |
| DATA-002 | Migrations | none | none | no evolution | P2 | DATA-P2-003 |
| DATA-003 | Constraints | PK/UNIQUE | partial | no FK | P2 | DATA-P2-002 |
| DATA-004 | Indexes | PK only | partial | no query idx | P3 | DATA-P3-001 |
| DATA-005 | FKs/cascades | none | none | orphan rows | P2 | DATA-P2-002 |
| DATA-006 | RLS | N/A | — | — | — | — |
| DATA-007 | Tenant columns | N/A | — | — | — | — |
| DATA-008 | Soft deletes | states | — | — | — | — |
| DATA-009 | Audit fields | `audit_log` | present | retention | P2 | DATA-P2-001 |
| DATA-010 | Retention | none | none | growth | P2 | DATA-P2-001/002 |

## Findings

### Finding ID: DATA-P2-001 - The idempotency table is unbounded and stores full response bodies

- Severity: P2
- Confidence: High
- Area: DATA
- Evidence:
  - `src/falcon_control/store.py` — `idempotency` table (`response_body TEXT NOT NULL`), `idem_put` `INSERT OR REPLACE`
  - `src/falcon_control/service.py` — `_idempotent` writes every successful response
- What is happening: no TTL or prune; idempotency keys accumulate forever with their response payloads.
- Why it matters: the lab DB grows without bound; a busy operator/agent loop can inflate storage and slow lookups.
- User / business impact: disk pressure on the shared host; slower queries.
- Security / privacy / reliability impact: unnecessary retention of response data.
- Recommended fix: add a `created_at` TTL prune (e.g. 24–72 h) run on write or by a timer, and cap stored body size.
- Suggested validation: test that expired idempotency rows are removed and replays after TTL are re-executed.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: DATA-P2-002 - No foreign keys and no retention for events, state_reports, heartbeat history

- Severity: P2
- Confidence: High
- Area: DATA
- Evidence:
  - `src/falcon_control/store.py` — `events`, `state_reports`, `audit_log` have `sensor_id` with no FK and no cleanup
  - `store.py` — connection does not set `PRAGMA foreign_keys=ON`
- What is happening: append-only tables grow with sensor activity forever; orphan rows are possible if a sensor row were removed.
- Why it matters: unbounded growth and weak referential integrity; test-sensor cleanup (documented 2026-10-02) had to delete dependent rows manually.
- User / business impact: storage exhaustion; manual cleanup errors.
- Security / privacy / reliability impact: stale data retained.
- Recommended fix: add FKs with `ON DELETE CASCADE` (and enable `foreign_keys`), plus a retention policy for events/state_reports/audit_log.
- Suggested validation: FK violation test; retention pruner boundary test (fresh vs expired).
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: migration mechanism (DATA-P2-003)
- Status: open

### Finding ID: DATA-P2-003 - No schema migration mechanism; only CREATE TABLE IF NOT EXISTS

- Severity: P2
- Confidence: High
- Area: DATA
- Evidence:
  - `src/falcon_control/store.py` — `SCHEMA` executed via `executescript` at every open
  - `--check`/migration tooling absent (no `migrations/` directory)
- What is happening: schema changes only take effect on fresh databases; an existing DB never receives new columns/tables.
- Why it matters: upgrades/rollbacks cannot evolve the DB safely; drift between code expectation and stored schema is undetected.
- User / business impact: upgrade breakage; data-format divergence across hosts.
- Security / privacy / reliability impact: reliability risk on upgrades.
- Recommended fix: introduce a `schema_version` meta row and ordered idempotent migrations applied at startup; assert version in tests.
- Suggested validation: open an old-schema DB and assert migrations bring it current.
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: DATA-P3-001 - Queue age-expiry is evaluable only on enqueue; `purge_expired` is unwired

- Severity: P3
- Confidence: High
- Area: DATA
- Evidence:
  - `src/falcon_agent/queue.py` — `purge_expired` exists; `_evict` enforces age only when `enqueue` runs
  - grep: `purge_expired` called only from `tests/phase3/test_queue*.py`
  - `src/falcon_agent/runner.py` — cycle never calls `purge_expired`
- What is happening: a queue that stops receiving new items can retain items past `max_age_seconds` indefinitely (read by `read_batch`).
- Why it matters: the loss-accounting contract ("whichever bound is hit first") is only applied opportunistically.
- User / business impact: stale data shipped late; expiry semantics inconsistent.
- Security / privacy / reliability impact: low.
- Recommended fix: call `purge_expired()` at the start of each agent cycle (and on open), or filter expired rows in `read_batch`.
- Suggested validation: unit test that a cycle purges expired items without a new enqueue.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unbounded idempotency/events | P2 | High | Disk exhaustion | `store.py` | retention |
| No migrations | P2 | Medium | Upgrade breakage | `store.py` | migration framework |
| Lazy queue expiry | P3 | Low | Stale delivery | `queue.py` | wire purge |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Add idempotency TTL prune.

### This Month
Migration framework + FK enforcement + retention.

### Later / Platform Evolution
Schema versioning in health output; data-inventory documentation.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Idempotency TTL | bounds growth | `store.py` | prune test |
| `PRAGMA foreign_keys=ON` | integrity | `store.py` | FK test |
| Wire `purge_expired` | expiry correctness | `runner.py` | queue test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Migrations | P2 | build-agent | M | none |
| Retention for events/reports/audit | P2 | build-agent | M | migrations |
| Query indexes | P3 | build-agent | S | none |

## Suggested Tests

- Destructive/retention boundary tests with mixed fresh/expired rows.
- Migration round-trip from an old-schema fixture.
- FK cascade test.

## Suggested Documentation Updates

- New `docs/phase2/DATA_RETENTION.md` naming owner and window per table.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Required retention windows? | fixes DATA-P2-001/002 | owner decision |
| Any external consumer reads events table? | migration risk | integration doc |

## Appendix

Validators: `validate_payload` is called on every sensor/operator body (`h_enroll`, `h_heartbeat`, `h_inventory`, `h_state_report`, `h_events`, `h_issue_*`, `h_quarantine`, `h_revoke`), and the agent re-validates signed payloads in `directives.py`. This is a strength (score 5).
