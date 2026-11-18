# 14_observability_monitoring_incident_readiness — Prompt 14 - Observability, Monitoring, and Incident Readiness Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `14_observability_monitoring_incident_readiness.md` (area OBS, prompt)

## Verification Performed

# 14_observability_monitoring_incident_readiness - 14_observability_monitoring_incident_readiness.md

Domain subagent `14_observability_monitoring_incident_readiness` (area OBS), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - No alerting or uptime monitoring for the control plane or for failed runs** (confidence: High)
  - `docs/CONTROL_PLANE.md:278 - the only mention of alerting is a Roadmap bullet: 'Prometheus//metrics export and alerting (throttle, TDR, over-temp).'`
  - `server/benchd.py:629-634 - /health exists and is public, but nothing in the repo consumes it (no cron, timer, probe config or CI check found by grep).`
  - `server/benchd.service:12 - the only self-healing is systemd 'Restart=on-failure'; there is no OnFailure= unit, no watchdog, and no notification of a restart.`
  - `server/benchd.py:1315-1335 - runs are moved to status='failed' by reap_stale_runs when a runner stops heartbeating, but that transition is only broadcast on the in-process SSE bus and stored; no operator is alerted.`
  - Impact: The control plane can be down (probe 8722 unreachable) or a run can end failed/unknown and the operator learns only by manually opening the dashboard. Long soak/stress runs that die silently waste the machine and the test window.
  - Recommendation: Add an external uptime probe for GET /health (e.g. a systemd timer or an off-box check) plus a minimal alert path: on run status -> failed (or control-plane restart) emit to a webhook/email and record a row in an 'alerts' table; add OnFailure= to server/benchd.service. Document the alert contract.
- **P2 - No structured logging and no request IDs / correlation IDs** (confidence: High)
  - `server/benchd.py:515-525 - the only server log is BaseHTTPRequestHandler.log_message writing a plain-text '[benchd] HH:MM:SS <msg>' line via print(); no level, no JSON, no logger.`
  - `server/benchd.py:1397 - the scheduler loop logs plain text 'scheduler error: %s'; server/benchd.py:1438-1441 - startup lines are plain print().`
  - `grep for request.?id|correlation|x-request|traceid|logger|getLogger across server/ and bench/ returned no matches - no request id is generated or propagated, and the per-runner API key / per-run context is not stamped on any log line.`
  - `bench/agent.py:127-128,370-371 - the runner-log path is also unstructured '[agent] %s' text.`
  - Impact: With concurrent runners and 4 Hz telemetry, a text stream with no correlation id cannot be tied to a specific run/runner/request. Triaging an incident requires guessing which activity belongs to which run.
  - Recommendation: Emit JSON log lines with at least ts, level, event, request_id (server-generated X-Request-Id echoed in the response) and run_id/runner_id where known; add a small log helper and use it in log_message and the exception paths. Keep the text mode behind a flag if needed.
- **P2 - Server-side errors are swallowed; no error tracking or stack traces** (confidence: High)
  - `server/benchd.py:647-650 - do_GET wraps _api_get in 'except Exception as exc: return self._err(500, "%s: %s" % (type(exc).__name__, exc))' and stores/prints nothing beyond that short body.`
  - `server/benchd.py:690-693 - do_POST does the same; the /api/v1/runs/<id>/telemetry path also has bare 'except Exception: pass' handlers (e.g. server/benchd.py:957-966 in _stream, 316-317, 478 in helpers).`
  - `server/benchd.py:629-634 vs 649-650 - a 500 is not recorded in the events table or any log with its traceback; log_message only records the request line and status code.`
  - Impact: A recurring 500 (bad input, DB lock, decode failure) is invisible server-side: the exception type/message is only in the client response, so there is no way to count, trend, or root-cause errors that operators did not happen to see.
  - Recommendation: Add an error-logging path (traceback + request id + route) for the 500 branches and for unexpected exceptions in the scheduler loop; persist error events so they can be listed. Reserve the events table or add a 'server_errors' table.
- **P2 - /health conflates liveness and readiness and performs a DB query plus a network call** (confidence: High)
  - `server/benchd.py:629-634 - the single /health handler returns {ok, time, git, version, protocol, latest, runners} and calls latest_git(), which is an outbound GitHub API request with timeout=8 (server/benchd.py:359-379), plus a SQLite query len(self.store.q(...)).`
  - `grep for readiness|/readyz returned no matches - there is no separate readiness endpoint and no dependency check (e.g. SQLite writability, web dir present).`
  - `docs/CONTROL_PLANE.md:129 - documents this only as 'public liveness'.`
  - Impact: A liveness probe can block up to the 8 s network timeout (GitHub unreachable/offline is a normal lab condition), so a probe configured with a short timeout will mark a healthy process dead. There is no signal that distinguishes 'process up' from 'able to serve' (DB/web dir healthy).
  - Recommendation: Split into /livez (process only, no I/O) and /readyz (checks SQLite read+write, web dir, and optionally cached latest_git without a live network call); keep /health as a public informational endpoint but make the probe path cheap and side-effect free.
- **P2 - No runtime/service metrics and no monitoring-of-the-monitoring** (confidence: High)
  - `server/benchd.py:718-719 - GET /api/v1/metrics returns {metrics: METRICS}, and server/benchd.py:78-90 shows METRICS is the benchmark result catalog (gpu_matmul_tflops.fp16, disk_seqwrite_mbps, ...), not service metrics.`
  - `No request counters, latency histograms, error-rate, queue-depth, DB-size or exporter/probe-freshness metrics exist anywhere (grep for prometheus returned only the Roadmap line docs/CONTROL_PLANE.md:278).`
  - `docs/CONTROL_PLANE.md:254 - 'the DB grows ~1 row/second per active run' is stated but never measured or exposed.`
  - Impact: There is no way to see control-plane load/saturation, SSE subscriber counts, API latency, error rate, command queue depth, or DB growth; and nothing monitors whether the monitoring path (the /health endpoint itself, the scheduler thread) is alive and current.
  - Recommendation: Expose a real metrics endpoint (Prometheus text format is fine, stdlib-only) with request count/latency by route+status, SSE subscribers, commands queued/sent/failed, runs running/failed, DB size/WAL size and last scheduler tick age; add freshness gauges for the runner population and an external check that the alerting path end-to-end works.
- **P3 - No audit log of operator / destructive command issuance** (confidence: High)
  - `server/benchd.py:1220-1232 - _issue_command inserts (id, runner_id, kind, payload, status, created) only; there is no actor identity, source address, or reason, and the kinds include destructive ones: iso_write, iso_write_slot, shutdown, reboot, exec, shell (server/benchd.py:1223-1225).`
  - `server/benchd.py:673-681 - DELETE /api/v1/runners/<id> removes that runner's commands, so even the command rows are not a durable record.`
  - `docs/CONTROL_PLANE.md:204-212 - the auth model is a single shared operator token, so no per-actor attribution is possible today.`
  - Impact: Destructive actions (raw-disk ISO write, reboot/shutdown, arbitrary exec/shell) leave no attributable, tamper-evident trail. After the fact it is impossible to reconstruct who issued a destructive command or when.
  - Recommendation: Append-only audit log (table or file) recording ts, source addr, command kind, target runner, payload digest and operator/session identifier for every issued command and every delete; never cascade-delete audit rows with the runner.
- **P3 - No incident runbook, escalation path, or on-call checklist** (confidence: High)
  - `docs/CONTROL_PLANE.md:214-254 - 'Operating notes' explain behaviour (offline after 15 s, fails soft, reapers, staleness) but there is no incident runbook, no 'what to do when X fails', no escalation or recovery checklist anywhere in docs/.`
  - `No file matching runbook/incident/on-call exists in the tree (git ls-files).`
  - Impact: Recovery relies on tribal knowledge: an operator facing a stuck run, a failed ISO write, or a down control plane has no documented steps, and a future AI agent has no checklist to follow.
  - Recommendation: Add docs/INCIDENT_RUNBOOK.md with detection (which dashboard/endpoint shows it), triage, immediate actions and recovery for: control plane down, runner offline mid-run, failed/unknown run, stuck/reaped command, disk/WAL full, over-temp/throttle/TDR; link it from CONTROL_PLANE.md.
- **P3 - Release marker not bound in the documented copy-deploy; /health can report 0.0.0+unknown** (confidence: Medium)
  - `server/benchd.py:267-282 - server_version() opens <repo>/VERSION (repo = parent of server/), and server/benchd.py:233-264 - server_git() falls back to .deployed-commit/.bench-version only when git is absent.`
  - `docs/CONTROL_PLANE.md:172-185 - the documented Proxmox deploy is 'pct push 108 benchd.py /opt/bench-test/server/benchd.py' plus the web dir and unit; it pushes neither VERSION nor a .deployed-commit stamp.`
  - `AGENTS.md:204 states the control plane is 'deployed as a copy, so VERSION ships with it' - contradicted by the deploy command above.`
  - Impact: /health would report version '0.0.0+unknown' and git '' for a copy-deployed control plane, so the fleet 'behind the deployed code' comparison loses its reference and an operator cannot tell which build is running.
  - Recommendation: Either push VERSION in the deploy, or write a .deployed-commit/.bench-version stamp (containing version+commit) as part of the deploy, and document it; assert it in a test that /health reports a non-unknown version for a copy deploy. Reconcile AGENTS.md:204.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| OBS-P2-001 | P2 | No alerting or uptime monitoring for the control plane or for failed runs |
| OBS-P2-002 | P2 | No structured logging and no request IDs / correlation IDs |
| OBS-P2-003 | P2 | Server-side errors are swallowed; no error tracking or stack traces |
| OBS-P2-004 | P2 | /health conflates liveness and readiness and performs a DB query plus a network call |
| OBS-P2-005 | P2 | No runtime/service metrics and no monitoring-of-the-monitoring |
| OBS-P3-001 | P3 | No audit log of operator / destructive command issuance |
| OBS-P3-002 | P3 | No incident runbook, escalation path, or on-call checklist |
| OBS-P3-003 | P3 | Release marker not bound in the documented copy-deploy; /health can report 0.0.0+unknown |
