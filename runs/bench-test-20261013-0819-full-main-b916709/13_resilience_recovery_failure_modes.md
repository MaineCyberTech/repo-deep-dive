# 13_resilience_recovery_failure_modes — Prompt 13 - Resilience, Recovery, and Failure Modes Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `13_resilience_recovery_failure_modes.md` (area RES, prompt)

## Verification Performed

# 13_resilience_recovery_failure_modes - 13_resilience_recovery_failure_modes.md

Domain subagent `13_resilience_recovery_failure_modes` (area RES), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - iso_fetch returns ok=True even when SHA256SUMS verification fails, so a bad ISO is accepted for a destructive write** (confidence: High)
  - `bench/benchreport.py:1750-1765 - iso_fetch() computes sha256_file(iso), sets `ok = (want is None) or (want == got)` and then returns `{"ok": True, "iso": iso, ..., "verified": ok}`; the mismatch verdict is never turned into a failure`
  - `bench/benchreport.py:1751-1764 - only the release's SHA256SUMS asset is consulted; when that asset is missing the check is skipped (`ok = None`) yet the result is still ok:True (unverified)`
  - `bench/agent.py:295-315 - _update_and_ack() runs iso_fetch and then `self.rep.ack(cid, "done" if res.get("ok") else "failed", res)`, so a mismatched ISO is acked 'done' and staged for iso_write / iso_write_slot`
  - `tests/test_update.py:200-202 - the test only asserts `r3.get("verified") is False`; it never asserts `ok` is False, so the fail-open path is enshrined rather than caught`
  - Impact: A corrupted, truncated or tampered ISO is treated as a verified download and can be written to a single-slot stick (iso_write) or the inactive A/B slot (iso_write_slot). The integrity check that exists to catch a bad recovery artifact is effectively advisory, defeating the fail-closed guarantee on the toolkit's most destructive operation and potentially bricking a runner.
  - Recommendation: Make the verdict binding: on `verified is False` return `{"ok": False, "error": "sha256 mismatch (expected %s, got %s)"}`, and fail closed when SHA256SUMS is absent (require an expected hash). Have agent/_update_and_ack treat `verified is False` as failed, and update tests/test_update.py to assert `ok` is False on mismatch.
- **P2 - A completed run is recorded as 'failed' and its summary lost when the final finish post fails (no retry/idempotency)** (confidence: High)
  - `bench/benchreport.py:590-598 - Reporter.finish() performs one _req() and then unconditionally sets `self.run_id = None`; the HTTP status/return value is ignored`
  - `bench/benchreport.py:487-507 - _req() returns `(0, {})` on any transport error (connection refused, timeout) and never retries or backs off`
  - `bench/agent.py:219-224, bench/gui.py:938-942, bench/tui.py:676-680 - each runner uploads telemetry/files and then calls finish exactly once; there is no retry, no local spool, and no operator-visible error`
  - `server/benchd.py:1315-1335 - reap_stale_runs() marks any still-'running' run 'failed' once its runner stops heartbeating, converting the lost finish into a 'failed' history row with an empty summary`
  - Impact: A transient control-plane outage at the end of an otherwise successful battery produces a 'failed', summary-less run: the run's metrics never reach trends/compare/Fleet, and the record cannot be corrected without a manual re-import. The reaper converts a success into a failure, so history is actively wrong rather than merely incomplete.
  - Recommendation: Retry finish with bounded backoff and persist the pending summary locally (replay at next start, or a spool the agent/pump drains); use a stable run id so finish is idempotent; add a distinct status (e.g. 'interrupted' + reason) for reaped runs so a lost finish is not reported as a runner failure.
- **P2 - Backfill importer is not idempotent (re-running duplicates every run) and --reset deletes all history** (confidence: High)
  - `server/import_results.py:404-409 and 429-435 - each Windows/Linux unit POSTs /api/v1/runs with no id / dedup key, so the server mints a new uuid run on every invocation`
  - `server/import_results.py:194-217 - upload_run() then posts phases/telemetry/artifacts/finish; a second run creates a complete duplicate rather than updating the existing run`
  - `server/import_results.py:385-390 - --reset GETs /api/v1/runs?limit=1000 and DELETEs each, wiping every run in the DB (not just imported rows)`
  - `tests/test_import.py:1-85 - tests cover parsing/merge only; there is no re-run/dedup or reset-scope test`
  - Impact: Re-running the documented backfill - a primary recovery path when a runner's results were never uploaded - silently duplicates history, double-counting runs and skewing trends/compare/Fleet medians. --reset is an unbounded destructive operation whose only guard is a CLI flag.
  - Recommendation: Derive a stable run id from source path + host + start timestamp (the server already honours a supplied id) and make the import an upsert; scope --reset to imported runs or require an explicit confirm/target instead of deleting all runs.
- **P2 - agent 'start' has a TOCTOU race that can run two benchmark batteries concurrently on one machine** (confidence: Medium)
  - `bench/agent.py:249-256 - handle('start') reads self.running and, if False, spawns the run thread and returns immediately`
  - `bench/agent.py:139-157 - self.running is only set True inside run_battery() after the blocking start_run() HTTP call, so the guard is still False when handle() returns`
  - `bench/agent.py:357-361 - the poll loop passes every fetched command to handle() in one iteration, so two queued 'start' commands both observe running=False`
  - `server/benchd.py:1291-1299 - the scheduler's busy guard checks runners.status='busy' or a queued start command; both can be false in the window between the fetch (status flipped to 'sent') and start_run setting the runner busy`
  - Impact: Two full-system soaks (GPU+CPU+RAM+disk) can run at once on the same host: the measurements are invalid and the machine can OOM or overheat - exactly the instability the toolkit is meant to detect, now caused by the toolkit itself.
  - Recommendation: Set a 'starting' flag synchronously under a lock before spawning (clear it on failure), reject a second start while one is pending, and have the server mark the runner busy when a start command is issued (not only when /runs is created).
- **P2 - Documented rollback paths (A/B slot auto-revert, live toolkit self-update) are never exercised, and a bad toolkit update has no rollback** (confidence: High)
  - `tests/test_update.py:296 - c.check("iso_write_slot not exercised on a real A/B stick (destructive)", True, "") - the A/B write + boot-flag flip is explicitly asserted unexercised; only confirm/missing-iso guards are tested (tests/test_update.py:290-299)`
  - `bench/benchreport.py:1994-2002 and live/ab-layout.sh:101-105 - grub auto-reverts only when attempts >= 3; nothing in tests/ drives the bench-slot attempt/confirm path (live/airootfs/usr/local/bin/bench-slot)`
  - `bench/benchreport.py:1333-1403 - update_toolkit() swaps the 'current' symlink / current.txt to the freshly fetched copy`
  - `bench/benchreport.py:1685-1711 - toolkit_boot_link()/_newest_toolkit_copy() fall forward to the newest/fresh copy, with no known-good previous pointer`
  - Impact: Two headline recovery mechanisms - unattended A/B flash with auto-revert and in-place live self-update - are unproven end to end. If a fetched toolkit copy is broken (import error), the runner re-execs into non-working code and can only be recovered by reflashing from another device; the auto-revert covers the ISO/boot path but not the toolkit copy.
  - Recommendation: Add a lab test (or at least a grubenv/bench-slot unit test) that flips a slot and confirms the revert after 3 attempts; keep the previous toolkit copy and add a startup health check with automatic revert (or `live_update.py toolkit --rollback`). Record the last exercise in the runbook.
- **P3 - Command queue is at-most-once with no DLQ/expiry; a fetched-but-unacked command is dropped, and a queued command never expires** (confidence: High)
  - `server/benchd.py:773-786 - GET /runners/<id>/commands flips every queued command to 'sent' as it is returned, before the runner executes it`
  - `server/benchd.py:1376-1385 - reap_stale_commands() marks a 'sent' command 'failed' (result 'no ack from the runner (dropped?)') after its timeout; there is no re-queue, no dead-letter table and no alert`
  - `server/benchd.py:1220-1232 - commands are inserted 'queued' with no expiry, so a command issued while a runner is briefly away (e.g. start/reboot) can fire much later, whenever the runner next polls`
  - `server/benchd.py:1019-1024 - ack() writes status/result but never re-drives or replays a failed command`
  - Impact: A scheduled or operator 'start' can be silently lost (marked failed with nothing retrying) or execute long after it was intended; there is no dead-letter view or replay, so dropped commands are invisible outside a transient SSE event. Scheduled runs can therefore be missed without an operator noticing.
  - Recommendation: Add command expiry/TTL for time-sensitive kinds, surface a dead-letter view and allow replay, and only mark a command 'sent' with an in-flight lease that is re-queued once if it expires (ack remains the durable completion signal).
- **P3 - Control-plane client has no retry/backoff/circuit-breaker; registration retries forever and telemetry is dropped on failure** (confidence: High)
  - `bench/benchreport.py:487-507 - Reporter._req() is a single attempt with timeout=self.timeout (default 6 s); there is no retry, backoff or circuit breaker anywhere in the client`
  - `bench/benchreport.py:711-743 - ReporterPump._drain() pops a batch and posts it once; on failure the batch is discarded (never re-queued), and heartbeat/command polling share the same loop`
  - `bench/agent.py:353-354, bench/gui.py:606-610, bench/tui.py:266-269 - `while not rep.register(caps): time.sleep(5)` retries forever at a fixed interval with no backoff/jitter/cap, even on a 401 (wrong token)`
  - Impact: During an outage, telemetry and log events are silently lost (only the end-of-run CSV can recover them, and that upload can also be lost - see the finish finding); a mis-configured fleet hammers a server every 5 s per host forever; every blocked call holds a thread up to 6 s, so a slow/black-holed server stalls the pump.
  - Recommendation: Add bounded retries with exponential backoff + jitter for control-plane writes, a small bounded local spool so telemetry/logs survive a short outage, and a registration backoff cap with an operator-visible 'cannot authenticate / server unreachable' state instead of an infinite fixed-interval loop.
- **P3 - HTTP server sets no read/connection timeout; a declared-but-unsent body pins a handler thread indefinitely** (confidence: High)
  - `server/benchd.py:506-512 - the Handler class never sets self.timeout; ThreadingHTTPServer is created without a socket timeout (server/benchd.py:1431-1433) and applications run on daemon threads with no connection cap`
  - `server/benchd.py:545-559 - _body() validates Content-Length <= MAX_BODY (server/benchd.py:52-55) and then blocks in self.rfile.read(n); the inline comment claims a declared-but-never-sent body 'cannot pin a handler thread', which only holds for an oversized declaration`
  - `server/benchd.py:626-651 - do_GET reads the request line through the base handler with the same missing deadline; the SSE handler (server/benchd.py:948-968) is long-lived by design with no idle cap`
  - Impact: An authenticated client (or any client when the server runs without a token) can open connections and declare bodies they never send, each pinning a handler thread indefinitely; enough of them exhaust the control plane and its memory, and there is no timeout to reclaim the threads.
  - Recommendation: Set Handler.timeout (e.g. 30 s) and/or SO_RCVTIMEO, read the body with a deadline, bound concurrent connections, and return 408 on timeout; correct the MAX_BODY comment to reflect that it only guards oversized declarations.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| RES-P1-001 | P1 | iso_fetch returns ok=True even when SHA256SUMS verification fails, so a bad ISO is accepted for a destructive write |
| RES-P2-001 | P2 | A completed run is recorded as 'failed' and its summary lost when the final finish post fails (no retry/idempotency) |
| RES-P2-002 | P2 | Backfill importer is not idempotent (re-running duplicates every run) and --reset deletes all history |
| RES-P2-003 | P2 | agent 'start' has a TOCTOU race that can run two benchmark batteries concurrently on one machine |
| RES-P2-004 | P2 | Documented rollback paths (A/B slot auto-revert, live toolkit self-update) are never exercised, and a bad toolkit update has no rollback |
| RES-P3-001 | P3 | Command queue is at-most-once with no DLQ/expiry; a fetched-but-unacked command is dropped, and a queued command never expires |
| RES-P3-002 | P3 | Control-plane client has no retry/backoff/circuit-breaker; registration retries forever and telemetry is dropped on failure |
| RES-P3-003 | P3 | HTTP server sets no read/connection timeout; a declared-but-unsent body pins a handler thread indefinitely |
