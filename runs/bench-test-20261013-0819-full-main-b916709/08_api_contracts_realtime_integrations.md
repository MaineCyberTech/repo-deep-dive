# 08_api_contracts_realtime_integrations — Prompt 08 - API Contracts, Realtime, and Integrations Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `08_api_contracts_realtime_integrations.md` (area API, prompt)

## Verification Performed

# 08_api_contracts_realtime_integrations - 08_api_contracts_realtime_integrations.md

Domain subagent `08_api_contracts_realtime_integrations` (area API), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - POST /api/v1/register gives away another runner's api_key via unproven machine_id adoption** (confidence: High)
  - `server/benchd.py:1190-1197 - when no runner_id is supplied, the server adopts any existing row matching (machine_id, kind, instance) with no ownership proof: existing = S.one("SELECT * FROM runners WHERE machine_id=? AND kind=? AND COALESCE(instance,'')=?")`
  - `server/benchd.py:1198-1200 - on adoption it sets key = existing['api_key'] and returns it`
  - `server/benchd.py:1217 - the response body hands the caller that api_key: {"runner_id": rid, "api_key": key, ...}`
  - `server/benchd.py:688 - the POST gate only requires *any* valid runner bearer (_runner_ok()), so one enrolled runner can reach /register`
  - `server/benchd.py:1178-1189 - the explicit runner_id path *is* ownership-checked, and the inline comment claims takeover is now blocked; the machine_id path bypasses that check entirely`
  - `reproduced: attacker (holding its own valid api_key) POSTs /register with the victim's machine_id and receives the victim's runner_id AND api_key; the stolen key then drains the victim's command queue, including an operator-issued exec {cmd: whoami}`
  - Impact: Any enrolled runner can impersonate another runner, steal its API key, forge heartbeats/runs, and intercept operator commands targeted at the victim - including exec/shell remote-terminal payloads. The in-code claim that this takeover class is closed is false, so a reviewer/operator would treat the fleet as safe when it is not.
  - Recommendation: Require proof of ownership for machine_id-based adoption too: only adopt a row when the request already presents that row's api_key (or the operator token); otherwise mint a new row. Add the missing test (mirror tests/test_control_plane.py:49-61 but steal via machine_id instead of runner_id).
- **P2 - Write endpoints perform no body validation: malformed JSON is treated as success** (confidence: High)
  - `server/benchd.py:545-559 - _body() swallows every parse failure and returns {} instead of raising/400`
  - `server/benchd.py:691 - do_POST passes that {} straight into _api_post`
  - `server/benchd.py:1029-1052 - POST /api/v1/runs with an empty body returns 200 and creates a phantom run (runner_id NULL, status 'running')`
  - `server/benchd.py:1070-1108 - POST /runs/<id>/telemetry with a malformed body returns 200 {"ok":true,"accepted":0}, so a writer believes the samples landed`
  - `server/benchd.py:1109-1116 - POST /runs/<id>/event passes message/level through unvalidated`
  - `reproduced: body b'{not json' -> 200; body {} on POST /runs -> 200 + run_id; body [1,2,3] -> 500 AttributeError; event message={...} -> 500 ProgrammingError (Error binding parameter 4: type 'dict' is not supported)`
  - Impact: Silent data loss (telemetry/logs accepted-and-dropped) and phantom runs polluting history; malformed input surfaces as 500s that leak internals rather than a 4xx contract. No caller can tell a rejected write from an accepted one.
  - Recommendation: Raise a 400 from _body() on parse failure and on a non-object top level; validate required types per route (str for level/message/stream, list of dicts/floats for samples, numeric seq/ts) and return 400 with a structured error instead of catching the exception into a 500.
- **P2 - Run creation is not idempotent: a repeated client-supplied run id returns 500 and leaks the DB schema** (confidence: High)
  - `server/benchd.py:1038 - the client may supply the run id: run_id = b.get("id") or str(uuid.uuid4())`
  - `server/benchd.py:1041-1046 - it is inserted with a plain INSERT; runs.id is the PRIMARY KEY (server/benchd.py:102)`
  - `server/benchd.py:692-693 - any exception becomes 500 with the exception type/message`
  - `reproduced: POST /runs {id: 'dup-run'} -> 200; the same request again -> 500 {"error": "IntegrityError: UNIQUE constraint failed: runs.id"}`
  - `bench/benchreport.py:545-553 - the reporter never sends its own id, so a timed-out start_run that is retried silently creates a duplicate run instead of converging`
  - Impact: A retried 'start a run' either errors (explicit id) or duplicates history (generated id); neither is a safe retry. The 500 also discloses the SQLite schema, and the run id in the URL is meant to be a stable idempotency key (PROTOCOL/POST /register documents client ids).
  - Recommendation: Make POST /api/v1/runs upsert/return-existing on a repeated id (INSERT ... ON CONFLICT(id) DO NOTHING then read back, returning 200 with the existing run_id), and have the reporter send a client-generated id so retries are idempotent.
- **P2 - DELETE /api/v1/runs/<id> leaves the run's log rows orphaned; the doc contract says '+data'** (confidence: High)
  - `server/benchd.py:665-672 - the delete loop covers phases, telemetry, events, artifacts but NOT logs: for t in ("phases", "telemetry", "events", "artifacts")`
  - `server/benchd.py:116-118 - logs is a separate table (id, run_id, ts, stream, line) with no foreign key`
  - `docs/CONTROL_PLANE.md:132 - documents DELETE /runs/<id> as 'delete a run (+data)'`
  - `reproduced: 3 log lines for run X -> DELETE run X -> runs row gone, telemetry gone, logs still 3`
  - Impact: Deleting a run does not delete its console output: rows accumulate forever, the documented '+data' guarantee is false, and sensitive captured logs (the remote terminal streams into the same table, bench/benchreport.py:817-843) survive a delete an operator believes wiped the run.
  - Recommendation: Add 'logs' to the delete loop (server/benchd.py:668); optionally add a foreign-key/ON DELETE CASCADE or a periodic orphan sweep, and reconcile the run detail/logs queries. Update docs/CONTROL_PLANE.md:132 or make it true.
- **P2 - Realtime SSE fan-out silently drops events once a subscriber's queue fills (no backpressure, no metric)** (confidence: High)
  - `server/benchd.py:199-204 - each SSE subscriber gets queue.Queue(maxsize=1000)`
  - `server/benchd.py:210-217 - Bus.publish uses q.put_nowait(ev) inside a bare except: pass, so a full queue drops the event with no counter, log, or error`
  - `server/benchd.py:948-968 - the SSE handler blocks on q.get(timeout=15) and, on any exception, only emits a keepalive`
  - `server/benchd.py:1105-1107 - one telemetry event can carry up to 1000 samples (named[-1000:]), and the 4 Hz publish rate means a stalled client fills the 1000-slot queue and then loses phase/run/command events`
  - `reproduced in-process: 1500 Bus.publish calls with one subscriber left the queue at exactly 1000 and dropped 500 events, with no signal to the publisher`
  - Impact: A slow/backgrounded dashboard tab silently misses live phases, run status changes and commands; nothing tells the client it is behind, so the live view can be wrong without any error (partial mitigation: the UI re-polls /state, which masks but does not detect the loss).
  - Recommendation: Count drops (per-subscriber) and expose them (e.g. a 'lagged' SSE event or /metrics counter); either coalesce telemetry into the latest-only value for slow subscribers, or close/resync a lagging stream with an explicit 'resync' event so the client refetches /state.
- **P3 - Error responses leak internal exception type and message; invalid client input returns 500 instead of 4xx** (confidence: High)
  - `server/benchd.py:649-650 - do_GET: self._err(500, "%s: %s" % (type(exc).__name__, exc))`
  - `server/benchd.py:692-693 - do_POST: same pattern`
  - `reproduced 500 bodies: 'IntegrityError: UNIQUE constraint failed: runs.id'; "AttributeError: 'list' object has no attribute 'get'"; "ProgrammingError: Error binding parameter 4: type 'dict' is not supported"`
  - Impact: Client-caused errors are reported as server faults (500) and the body exposes SQLite/ORM internals (table/column names, parameter indices) to any authenticated runner; callers cannot reliably branch on status codes.
  - Recommendation: Keep {"error": <generic message>} for 5xx and log the exception server-side; map validation failures to 400/422 explicitly (see the body-validation finding) so the error contract is stable and non-leaky.
- **P3 - No rate limiting or request throttling on any endpoint; /health is unauthenticated** (confidence: High)
  - `server/benchd.py:683-693 - do_POST has no per-caller counter; server/benchd.py:626-651 - do_GET likewise`
  - `server/benchd.py:629-634 - GET /health (no auth) returns ok, time, git, version, protocol, latest, runners count`
  - `server/benchd.py:55 - the only guard is MAX_BODY=24 MiB; there is no per-window request/size cap`
  - `reproduced: 200 unauthenticated /health requests completed in ~0.38s with no throttling`
  - Impact: A single authenticated runner (or anyone when BENCHD_TOKEN is unset: server/benchd.py:1440-1441) can flood telemetry/log writes and grow the SQLite store without bound; /health leaks the exact deployed version/commit/protocol and fleet size to unauthenticated callers.
  - Recommendation: Add a simple per-client token-bucket (or at least a max rows/s and max queued-write cap) for write routes, and reduce /health to a bare liveness/version or gate the git/latest/runners fields behind auth.
- **P3 - No machine-readable API contract (OpenAPI/schema); the prose contract already drifts from the handlers** (confidence: High)
  - `No OpenAPI/Swagger/JSON-schema artifact exists in the repo (only docs/CONTROL_PLANE.md:99-133 documents the routes in prose)`
  - `server/benchd.py:1117-1130 implements POST /api/v1/runs/<id>/log (used by bench/benchreport.py:573-580 for the live console) but it is absent from the API table in docs/CONTROL_PLANE.md:103-133`
  - `server/benchd.py:673-680 - DELETE /runners/<id> removes commands and schedules but leaves the runner's runs and their logs orphaned, which the table (docs/CONTROL_PLANE.md:132) does not state`
  - `server/benchd.py:1239-1244 - schedule 'kind' is unvalidated; an unknown kind is silently treated as 'every' (reproduced: kind='bogus' -> 200 with a next_run)`
  - `server/benchd.py:48 + 632 + 716 - PROTOCOL=1 is advertised but the server never rejects a mismatched runner (mismatch is only highlighted in the web UI, server/web/app.js:383-384)`
  - Impact: There is no contract to test against, so implemented-but-undocumented routes, undocumented deletes and unvalidated enums drift silently; a protocol mismatch is a UI warning rather than an enforced server-side check.
  - Recommendation: Add a checked-in OpenAPI (or a route table generated from the handler) plus a contract test that asserts every implemented route appears in it; validate schedule kind against the allowed set; document POST /runs/<id>/log and the actual delete semantics.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| API-P1-001 | P1 | POST /api/v1/register gives away another runner's api_key via unproven machine_id adoption |
| API-P2-001 | P2 | Write endpoints perform no body validation: malformed JSON is treated as success |
| API-P2-002 | P2 | Run creation is not idempotent: a repeated client-supplied run id returns 500 and leaks the DB schema |
| API-P2-003 | P2 | DELETE /api/v1/runs/<id> leaves the run's log rows orphaned; the doc contract says '+data' |
| API-P2-004 | P2 | Realtime SSE fan-out silently drops events once a subscriber's queue fills (no backpressure, no metric) |
| API-P3-001 | P3 | Error responses leak internal exception type and message; invalid client input returns 500 instead of 4xx |
| API-P3-002 | P3 | No rate limiting or request throttling on any endpoint; /health is unauthenticated |
| API-P3-003 | P3 | No machine-readable API contract (OpenAPI/schema); the prose contract already drifts from the handlers |
