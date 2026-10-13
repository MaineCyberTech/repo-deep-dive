# 30_notification_email_push_delivery_audit — Prompt 30 - Notification, Email, and Push Delivery Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `30_notification_email_push_delivery_audit.md` (area NOTIF, prompt)

## Verification Performed

# 30_notification_email_push_delivery_audit - 30_notification_email_push_delivery_audit.md

Domain subagent `30_notification_email_push_delivery_audit` (area NOTIF), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - No out-of-band alert/notification delivery for critical health verdicts** (confidence: High)
  - `docs/CONTROL_PLANE.md:278 - alerting is only a roadmap bullet: '- Prometheus/`/metrics` export and alerting (throttle, TDR, over-temp).'`
  - `bench/benchreport.py:2524-2535 - WHEA/TDR/Kernel-Power/bugcheck/thermal are classified into summary.verdicts as 'warn'/'bad' but only ever returned to the caller (dashboard/report), never dispatched as a notification.`
  - `server/benchd.py:1315-1335 - reap_stale_runs marks an orphaned run 'failed' and publishes it on the in-process SSE bus only; no email/push/webhook/desktop alert is emitted.`
  - `server/benchd.py:818-849 - throttle/over-temp is computed server-side (throttled_pct) for the web UI and likewise never leaves the dashboard.`
  - `Repository-wide search for notif|email|smtp|webpush|vapid|webhook|slack|discord|ntfy|push_subscription|reminder returns no delivery code (only git user.email, the Bus.unsubscribe method, and the ephemeral web toast in server/web/app.js:143-148).`
  - Impact: An unattended multi-hour soak (fullsoak/Invoke-FullSystemSoak.ps1, Run-LinuxBench.sh, or a scheduled run on the live USB) can overheat, throttle, or hit WHEA/TDR/predictive disk failure and nobody is notified. The signal exists in summary.verdicts and the dashboard, but there is no channel that reaches an operator who is not watching the web UI at that moment - i.e. there is no alerting/notification delivery at all.
  - Recommendation: Add a small, opt-in notification sink to the control plane (stdlib only): a configurable webhook/ntfy/SMTP sink invoked by benchd when a finished run's summary.verdicts contains level 'bad' (or 'warn' above a threshold) and by reap_stale_runs when a run is marked failed. Keep it disabled by default, document the config key, redact the endpoint secret, and record a delivery-attempt row for audit. If out-of-band delivery is deliberately out of scope, state that explicitly in CONTROL_PLANE.md rather than listing alerting only as roadmap.
- **P3 - In-app SSE notification bus silently drops events when a subscriber queue fills** (confidence: High)
  - `server/benchd.py:199-204 - each subscriber gets queue.Queue(maxsize=1000) with no overflow policy.`
  - `server/benchd.py:210-217 - Bus.publish uses q.put_nowait(ev) inside `except Exception: pass`, so once a slow/stalled dashboard client's queue is full every subsequent event (runner/run/phase/telemetry/command/log/schedule/event) is dropped with no counter, log line, or resync signal.`
  - `server/benchd.py:948-968 - _stream consumes the queue and reconnects with a fresh 'snapshot'; a client that fell behind can miss events between its old position and the new snapshot without ever knowing.`
  - `tests/test_control_plane.py:327-334 - the only SSE test asserts the opening 'event: snapshot'; there is no test for a saturated subscriber or dropped-event accounting.`
  - Impact: The live dashboard is the toolkit's only real-time notification surface. A transient slowdown (large telemetry burst, GC) can silently desynchronise a browser from the fleet state, so an operator may not see a run go 'failed', a phase warning, or a queued command - the notification is dropped rather than delayed.
  - Recommendation: Track drops per subscriber (increment a counter on put_nowait failure) and either (a) send a 'resync' SSE event telling the client to refetch /state, or (b) disconnect the lagging subscriber so the browser's reconnect+snapshot path restores consistency. Add a unit test that fills a subscriber queue and asserts the drop is surfaced, not swallowed.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| NOTIF-P2-001 | P2 | No out-of-band alert/notification delivery for critical health verdicts |
| NOTIF-P3-001 | P3 | In-app SSE notification bus silently drops events when a subscriber queue fills |
