# 31_search_indexing_privacy_audit — Prompt 31 - Search, Indexing, and Privacy Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `31_search_indexing_privacy_audit.md` (area SEARCH, prompt)

## Verification Performed

# 31_search_indexing_privacy_audit - 31_search_indexing_privacy_audit.md

Domain subagent `31_search_indexing_privacy_audit` (area SEARCH), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - Deleting a run does not delete its console logs; they stay retrievable by run id** (confidence: High)
  - `server/benchd.py:665-672 - DELETE /api/v1/runs/<id> loops over ('phases','telemetry','events','artifacts') and then deletes the run row, but never 'logs' (the logs table is not in the list and there are no FOREIGN KEY/cascade constraints in SCHEMA at server/benchd.py:94-143)`
  - `server/benchd.py:744-746 and 802-807 - GET /api/v1/runs/<id>/logs queries logs WHERE run_id=? without checking that the run still exists, so a deleted run's logs are still served`
  - `server/benchd.py:1117-1130 - the /log endpoint stores raw runner stdout lines (up to 4000 chars each) verbatim`
  - `Reproduced at HEAD (72c18734): after DELETE /api/v1/runs/<id> -> 200, GET /api/v1/runs/<id> -> 404, but GET /api/v1/runs/<id>/logs -> 200 returning the two stored lines (incl. a planted 'secret-token=ABC123' line); direct row counts: runs=0, phases=0, telemetry=0, events=0, artifacts=0, logs=2`
  - `docs/CONTROL_PLANE.md:132 - documents the endpoint as 'delete a run (+data)', which the implementation does not honor for logs`
  - Impact: A run's console log can contain operator tokens, credentials or other secrets echoed by benchmark/exec output. After an operator deletes the run to remove it, the log rows persist indefinitely in SQLite and remain reachable via a known run id. This breaks the documented delete contract and the required 'deleted/private sensitive data must not remain searchable' control.
  - Recommendation: Add 'logs' to the delete table list in server/benchd.py (and make it a single explicit list of every run-scoped table so future tables cannot be missed); optionally delete orphaned logs defensively. Update docs/CONTROL_PLANE.md:132 to state exactly which tables are removed. Add a regression test asserting GET /api/v1/runs/<id>/logs returns 404 (or empty) after the run is deleted.
- **P2 - No retention policy or cleanup job for logs, telemetry, artifacts or events - run data is kept forever** (confidence: High)
  - `server/benchd.py:94-143 - SCHEMA defines runners/runs/phases/telemetry/logs/commands/events/artifacts/schedules with no created-at TTL, no retention column, and no cleanup`
  - `server/benchd.py:1276-1398 - the scheduler loop only fires schedules and reaps stale runs/commands/ephemeral runners; none of the reapers prune run data (logs/telemetry/artifacts/events)`
  - `server/benchd.py:1140-1142 - artifacts store the full base64 file content inline in the DB, so attached reports/inventory/log bundles are retained as-is`
  - `docs/CONTROL_PLANE.md:254 - 'SQLite uses WAL; the DB grows ~1 row/second per active run (fine for a lab)' - growth is acknowledged but no retention/cleanup exists`
  - `No occurrence of retention/prune/purge/VACUUM in server/ or docs/ (grep over *.py and *.md)`
  - Impact: Benchmark runs collect full hardware inventory, console output and report artifacts. With no owner, retention window or cleanup, sensitive operational data accumulates permanently and the SQLite DB grows without bound; there is no way to prove data is removed after a retention period. This fails the extended check requiring owner/retention/cleanup per table.
  - Recommendation: Define per-table retention (e.g. logs/telemetry 30-90 days, artifacts 90 days) in config, add a periodic prune task to the scheduler loop, document owner + retention per table in docs/DATA.md or docs/CONTROL_PLANE.md, and expose a manual purge endpoint. Add a test that a row past its retention window is removed by the prune pass.
- **P2 - Deleting a runner orphans its runs, telemetry, logs and artifacts** (confidence: High)
  - `server/benchd.py:673-680 - DELETE /api/v1/runners/<id> removes only commands, schedules and the runner row; runs/telemetry/logs/events/artifacts that reference the runner are left behind`
  - `Reproduced at HEAD (72c18734): after DELETE /api/v1/runners/<id> the runner's run row still exists (runs for runner = 1) and its log row still exists (logs for that run = 1)`
  - `server/benchd.py:726-737 - GET /api/v1/runs lists all runs regardless of whether the owning runner still exists, so orphaned runs still appear in history`
  - `docs/CONTROL_PLANE.md:132 - documents runner delete as 'a runner (+its commands & schedules)', so the orphaned runs are undocumented behavior rather than an intended cascade`
  - Impact: When an operator decommissions a machine, its run history, telemetry and console logs remain in the store and are still listed/served. Combined with the missing retention policy this means 'removed' machines keep leaking data, and history shows runs with no live owner.
  - Recommendation: On runner delete, cascade to the runner's runs via the same run-delete path (which must also delete logs, per the P1 fix), or explicitly document and provide a separate purge command. Add a test that deleting a runner removes its runs and their run-scoped rows.
- **P2 - Shared operator token is accepted in the URL query string and compared non-constant-time** (confidence: Medium)
  - `server/benchd.py:572-580 - _is_operator accepts q.get('token') and compares it with plain == (the bearer path at :576 correctly uses secrets.compare_digest)`
  - `docs/CONTROL_PLANE.md:206 - instructs operators to use '?token=' for the SSE stream and file downloads`
  - `server/web/app.js:101 - the dashboard reads the token from location.search and also persists it in localStorage`
  - `server/benchd.py:518-525 - log_message redacts 'token=' from the server's own log line, but the token is still in the request URL (browser history, Referer, any reverse proxy/access log)`
  - Impact: The token is a single shared credential that grants full operator control. Putting it in a URL exposes it to browser history, the Referer header on any outbound link, and any proxy access log in front of the LAN service, and it bypasses the compare_digest hardening used for the bearer path.
  - Recommendation: Prefer a short-lived signed URL or an httpOnly cookie for SSE/downloads instead of ?token=; if query auth must stay, compare with secrets.compare_digest and document the leak surface. Consider rotating the token and adding per-user operator logins (already on the roadmap at docs/CONTROL_PLANE.md:275).
- **P3 - History 'search' is client-side only, over a capped 300-row page - not server-side** (confidence: High)
  - `server/web/app.js:842 - renderHistory fetches '/runs?limit=300' (+ optional host), so only the newest 300 runs are ever searched`
  - `server/web/app.js:843-846 - the text filter does JSON.stringify(r).toLowerCase().includes(q) in the browser; there is no server-side text/field query`
  - `server/benchd.py:726-737 - GET /api/v1/runs supports only limit/offset/host; no q/text/field filter, and no LIKE/MATCH/FTS query exists anywhere in server/`
  - `server/benchd.py:135-142 - indexes are all key/range B-trees (run_id, started, runner_id); there is no search index`
  - Impact: The required control 'search filters must be server-side' is unmet: a run older than the newest 300 (or outside the current host filter) cannot be found, results depend on a client-side substring match over serialized JSON, and there is no index to make a real search scale.
  - Recommendation: Add server-side filtering (e.g. q= across label/host/status/preset, plus explicit field filters and stable pagination) with an index, or, if the client-side cap is intentional, document it in the UI and docs so operators know older runs are not searchable. Add a test that a run outside the first page is still findable by the server filter.
- **P3 - Missing indexes on hot filter paths and no documented index ownership** (confidence: Medium)
  - `server/benchd.py:135-142 - indexes cover runs(started), runs(runner_id), phases(run_id,seq), telemetry(run_id,ts), commands(runner_id,status), events(run_id,ts), logs(run_id,id), schedules(enabled,next_run)`
  - `server/benchd.py:700-712 - /state scans runs WHERE status='running' and SELECT DISTINCT host FROM runs (no index on runs(status) or runs(host))`
  - `server/benchd.py:726-737 - /runs filters WHERE host=? (no index on runs(host))`
  - `server/benchd.py:901-902 - artifact download queries artifacts WHERE run_id=? AND name=? (artifacts has no index)`
  - Impact: As the store grows these queries degrade to full table scans, and there is no place recording which index belongs to which query/owner or a retention policy for each. This is a maintainability/scaling gap rather than an active exposure.
  - Recommendation: Add indexes on runs(status), runs(host) and artifacts(run_id,name); document each index's owning query and retention alongside the table inventory (see the retention finding).

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| SEARCH-P1-001 | P1 | Deleting a run does not delete its console logs; they stay retrievable by run id |
| SEARCH-P2-001 | P2 | No retention policy or cleanup job for logs, telemetry, artifacts or events - run data is kept forever |
| SEARCH-P2-002 | P2 | Deleting a runner orphans its runs, telemetry, logs and artifacts |
| SEARCH-P2-003 | P2 | Shared operator token is accepted in the URL query string and compared non-constant-time |
| SEARCH-P3-001 | P3 | History 'search' is client-side only, over a capped 300-row page - not server-side |
| SEARCH-P3-002 | P3 | Missing indexes on hot filter paths and no documented index ownership |
