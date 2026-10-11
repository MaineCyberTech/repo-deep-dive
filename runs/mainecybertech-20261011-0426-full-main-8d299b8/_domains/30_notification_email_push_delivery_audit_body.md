# Notification, Email, and Push Delivery Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening rerun)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (read-only worktree `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` ("Merge PR #168: promote develop to main (metrics scrape fixes + register sync)")
- Generated at: 2026-10-11
- Auditor: domain subagent 30 (area NOTIF), fresh audit + verification of the `mainecybertech-20261004-full-main-9c0b88c` register
- Area code: NOTIF
- Scope limitations:
  - AUDIT-ONLY. No application code, config, migration, or infra file was modified; only the two run-folder outputs were written.
  - No email, push, or ntfy message was sent, and no provider (SMTP, Supabase Realtime, ntfy) was contacted. Delivery claims are code/config analysis at the audited commit, not reproduced against a live provider.
  - The repository has no `node_modules` in the worktree; the supabase-js serialization behaviour behind one new finding is inferred from documented PostgREST semantics (confidence `medium`, flagged in the finding).
  - Secret values were never read or printed; only secret/key names and paths are cited.
  - Cross-domain rows whose subject is notification delivery (SEC-P3-004, MT-P2-004, DR-P2-001) were re-verified here because they are in this domain's subject matter; they remain owned by their areas.

## Scope

Reviewed at `8d299b8d` (branch `main`):

- **Notification model / schema:** `supabase/migrations/5302029_create_notifications_table.sql`, `5302107_notification_dedup_and_indexes.sql`, `5302057_fix_bootstrap_rls_fk_indexes.sql`, `5302026_...corrected.v3.sql` (`notification_preferences` + RLS).
- **In-app delivery:** `apps/api/src/routes/notifications.ts` (SSE, list, unread, read, mark-all-read, admin create, delete), `apps/web/components/NotificationBell.tsx`, `apps/web/app/(portal)/portal/notifications/**`.
- **Send helpers:** `apps/api/src/lib/notify.ts`, `apps/api/src/lib/notification-channels.ts`, `apps/api/src/lib/email.ts`, `apps/worker/src/notification-store.ts`, `apps/worker/src/email.ts`, `apps/worker/src/tasks/notification-email.ts`, `apps/worker/src/tasks/scheduled-notifications.ts`, `apps/worker/src/tasks/module-tasks.ts` (notification inserts).
- **Preferences:** `apps/api/src/routes/notification-preferences.ts`, `packages/sdk/src/notifications.ts`, preferences UI, `apps/api/src/middleware/org-access.ts`.
- **Config / queue / lifecycle:** `apps/api/src/config/env.ts`, `apps/api/src/main.ts`, `apps/worker/src/env.ts`, `apps/worker/src/main.ts`, `apps/api/src/lib/task-producer.ts`, `apps/worker/src/consumer-bullmq.ts`, `apps/worker/src/task-registry.ts`, `apps/worker/src/lib/idempotency.ts`, `apps/worker/src/lib/scan-lock.ts` (via callers), `apps/worker/src/tasks/retention.ts`.
- **Observability:** `apps/api/src/lib/metrics.ts`, `apps/worker/src/metrics.ts`, `infra/digitalocean/prometheus.yml`, `infra/digitalocean/prometheus.rules.yml`, `infra/digitalocean/dashboards/mct-overview.json`, `docs/SLO.md`, `docs/MONITORING_AND_ALERTING.md`.
- **ntfy alerting (separate from user notifications):** `infra/digitalocean/alertmanager.tmpl.yml`, `infra/digitalocean/docker-compose.yml`, `.github/workflows/deploy-do.yml`, `db-backup.yml`, `storage-backup.yml`, `db-restore-test.yml`, `CHANGELOG.md`.
- **Tests/docs:** API `notify-enforcement`, `email`, `notifications*`, `notification-preferences` suites; worker `notification-store`, `main`, `schedule-config`, `task-handlers`; web E2E `notification*` specs; `docs/modules/notifications.md`, `docs/modules/notification-preferences.md`, `docs/GAP_ANALYSIS.md`.

Not reviewed in depth (owned by sibling domains, cross-referenced only): general resilience/queue/DLQ semantics (RES-*), webhook delivery (WH-*), RLS policy correctness (RLS-*), billing/DR alerting internals beyond the ntfy path, password-reset email content (SEC-P2-005).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `supabase/migrations/5302029_create_notifications_table.sql` | Schema | Base notifications table + RLS | `title`/`body` plaintext; insert policy hardened by `5302057` |
| `supabase/migrations/5302107_notification_dedup_and_indexes.sql:2-3` | Schema | Dedup | `notification_key` + partial unique index `idx_notifications_key` |
| `supabase/migrations/5302026_...v3.sql:231-240,1063-1088` | Schema | Preferences model + RLS | `organization_id` **NOT NULL, no default**; self-or-admin policies |
| `apps/api/src/lib/notify.ts` | Source | API fan-out | Key derivation, upsert dedup, preference gates, enqueue→inline fallback |
| `apps/api/src/lib/notification-channels.ts` | Source | Preference resolver | Default-on, fail-safe, `sms` excluded from deliverable channels |
| `apps/api/src/routes/notifications.ts` | Source | In-app API | SSE scope assertion, 5-min JWT revalidation, admin create via `createNotification` |
| `apps/api/src/routes/notification-preferences.ts` | Source | Preferences API | PUT upsert without `organization_id` fallback (new finding) |
| `apps/api/src/lib/email.ts`, `apps/worker/src/email.ts` | Source | SMTP senders | Bounded retries (3, backoff), SMTP skip + metric, recipient redacted |
| `apps/worker/src/notification-store.ts` | Source | Worker fan-out | Mirrors API resolver/key; `claimNotificationEmail` atomic email claim |
| `apps/worker/src/tasks/scheduled-notifications.ts` | Source | Reminders | task-due/membership/ticket/custom; atomic claim; inline HTML; org omitted in `resolveChannels` |
| `apps/worker/src/tasks/module-tasks.ts:390,915,1262,1545,1613` | Source | Scan notifications | All inserts via `insertNotification` (gated + keyed) |
| `apps/api/src/middleware/org-access.ts:73-79,158-173,231,252` | Source | Org resolution | `req.orgId` resolved from X-Active-Org; `assertBodyOrgMatches` on every request |
| `apps/api/src/lib/task-producer.ts`, `apps/worker/src/consumer-bullmq.ts`, `task-registry.ts` | Source | Queue/retry | attempts 3 + exp backoff; `ok:false` retries; PII-safe Sentry |
| `apps/worker/src/lib/idempotency.ts` | Source | Idempotency store | Redis SET NX EX, 24h TTL, in-memory fallback |
| `apps/api/src/lib/metrics.ts`, `apps/worker/src/metrics.ts` | Source | Observability | delivery/suppressed/dedup counters on both sides |
| `infra/digitalocean/prometheus.rules.yml`, `dashboards/mct-overview.json`, `docs/SLO.md` | Infra/docs | Alerting | No notification rule; SLO computed from API-side counter |
| `infra/digitalocean/alertmanager.tmpl.yml`, `docker-compose.yml:240-305`, `.github/workflows/{deploy-do,db-backup,storage-backup,db-restore-test}.yml` | Infra/CI | ntfy alerting | ntfy receivers, noop defaults, deploy warnings, backup notifiers |
| API/worker tests, web E2E specs, `docs/modules/*.md`, `CHANGELOG.md` | Tests/docs | Coverage & claims | Enforcement/dedup/retry tested; no persistence/alerting tests; docs partially stale |

## Verification Performed

| Evidence / claim | Type | Why relevant | Outcome | Notes |
|---|---|---|---|---|
| NOTIF-P1-001 preferences enforced | Re-verify | Previous register row | **supported** | `notify.ts:116-128,167-202`; `notification-channels.ts:53-105`; worker `notification-store.ts:31-79,122-141`; `scheduled-notifications.ts:167,275,349`; tests exist |
| NOTIF-P1-002 dedup key on all producers | Re-verify | Previous register row | **supported** | `grep 'from("notifications")'` → all writes via `insertNotification` upsert (`onConflict notification_key`) |
| NOTIF-P1-003 failures "surfaced for alerting" | Re-verify | Previous register row | **partially supported** | Counters emitted; `prometheus.rules.yml` has no notification rule; SLO alert is "dashboard" |
| NOTIF-P2-001 web push absent | Re-verify | Previous register row | **supported (still absent)** | `grep -i 'vapid\|web-push\|pushManager\|serviceWorker'` over `apps/ packages/` → no matches |
| NOTIF-P2-002 SMTP loud but optional | Re-verify | Previous register row | **supported** | `api/main.ts:18-33` logger.error; `worker/env.ts:96-99` warn; skips metered; fail-closed reverted `3f2a772c` |
| NOTIF-P2-003 worker `unhandledRejection` | Re-verify | Previous register row | **supported** | `worker/main.ts:42-45` log + Sentry, continue |
| NOTIF-P2-004 atomic reminder email | Re-verify | Previous register row | **supported** | `notification-store.ts:200-217` claim; used in all 3 email branches; worker tests |
| NOTIF-P2-005 sensitive content | Re-verify | Previous register row | **supported (still open)** | `tickets.ts:386-395` excerpt; `notify.ts:204-211` verbatim; no redaction code |
| NOTIF-P2-006 inline retry | Re-verify | Previous register row | **supported** | `api/lib/email.ts:17-18,30-60`; `email.test.ts:38-90` |
| NOTIF-P3-001 template system | Re-verify | Previous register row | **supported (still open)** | Inline HTML at `notify.ts:208-210`, `scheduled-notifications.ts:214,321,394`, `admin.ts:61-70` |
| NOTIF-P3-002 sms / UI copy | Re-verify | Previous register row | **partially supported** | UI only email/in_app; API still accepts/returns `sms` (`notification-preferences.ts:14,35,52`) |
| NOTIF-P3-003 SSE fallback interval | Re-verify | Previous register row | **supported (still open)** | `NotificationBell.tsx:108-118` — interval never cleared on unmount |
| SEC-P3-004 prefs PUT org scope | Cross-verify | Subject in domain | **supported (fixed)** | `org-access.ts:158-173` + calls at `:231,252` |
| MT-P2-004 SSE org assertion | Cross-verify | Subject in domain | **supported** | `notifications.ts:36-44,154-156`; `notifications-sse-scope.test.ts:17-35` |
| DR-P2-001 backup ntfy delivery | Cross-verify | ntfy alerting in domain | **configuration supported; delivery not exercised in-repo** | All 3 workflows post to ntfy with Slack fallback; exercise evidence is external (PR #157) |
| Preference toggle persistence from web | Fresh | New finding | **unsupported (bug)** | PUT body omits `organization_id`; column NOT NULL; UI sends no org |
| API email deduped-but-sent | Fresh | New finding | **unsupported (bug)** | `notify.ts:173-221` never consults `inApp.deduped` before enqueue |
| Notification SLO semantics | Fresh | New finding | **unsupported (misleading)** | `notify.ts:215-220` records success on enqueue; dashboard/SLO use that counter only |
| Commands run | — | Reproducibility | `git log/show`, `grep -rn`, `sed -n`, `ls` only; no installs/builds/tests, no network | See Appendix |

## Executive Summary

The notification subsystem at `8d299b8d` is materially healthier than the audited baseline. Preference enforcement (NOTIF-P1-001), deterministic dedup on every producer (NOTIF-P1-002), worker atomic email claims (NOTIF-P2-004), worker `unhandledRejection` (NOTIF-P2-003), inline email retries (NOTIF-P2-006) and delivery counters (half of NOTIF-P1-003) are all present and test-covered at this commit. The loud-but-non-fatal SMTP boot signal (NOTIF-P2-002) is exactly as the register describes, with the fail-closed revert documented in `3f2a772c`.

The verification duty also surfaced two important caveats:

1. **Consent is still not exercisable end-to-end.** The preferences PUT accepts an optional `organizationId`, but both web clients omit it and the route never falls back to `req.orgId`; `notification_preferences.organization_id` is `NOT NULL` with no default. The upsert therefore cannot succeed from the UI (new P1), so the now-enforced preference gates read default-enabled forever.
2. **The delivery observability fix is half-complete.** Counters exist and are scraped, but no Prometheus rule consumes them; the published "Notification delivery success ≥ 99%" SLO is computed from the API-side counter that records a successful **enqueue** as a delivery success, and the worker counter that records the real SMTP outcome is used nowhere (new P2).

Also still open from the register: web push is entirely absent (NOTIF-P2-001); sensitive ticket/comment content is stored and emailed verbatim (NOTIF-P2-005); there is no email template system or unsubscribe/global opt-out (NOTIF-P3-001, new P3); the SSE polling fallback still leaks its interval (NOTIF-P3-003); and the dead `sms` option persists in the API surface (NOTIF-P3-002 residual).

ntfy alerting (out-of-band from user notifications) is wired for backup failures and Alertmanager critical/default receivers, but production only *warns* when the critical receiver URL is missing, and no in-repo artifact proves a critical alert ever reached ntfy (new P2).

**Recommended next actions:** fix the preferences write path (one-line org fallback + test); gate the API email on `inApp.deduped`; add a Prometheus alert on notification/email failure and recompute the SLO from worker outcomes; configure SMTP on the droplet; and add a preferences persistence E2E.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Notification model | `notifications` (`5302029`, `5302107`) | In-app rows | Implemented | Low | Plaintext body; keyed dedup; RLS insert hardened in `5302057` |
| Dedup key | `notification_key` partial unique index | Prevent duplicates | Implemented everywhere | Low | All producers upsert on conflict |
| In-app SSE | `notifications.ts:47-173` | Real-time push | Implemented | Low | Sanitized payload, org assertion, 5-min JWT recheck, keepalive |
| In-app polling | `NotificationBell.tsx:108-118` | Fallback | Implemented | Low | Interval leak (NOTIF-P3-003) |
| API fan-out | `lib/notify.ts` | Insert + email | Implemented | Medium | Preference gates present; email not gated on dedup |
| Worker fan-out | `notification-store.ts`, `scheduled-notifications.ts` | Reminders | Implemented | Low-Medium | Atomic claim; org omitted in resolver (new P3) |
| API email | `api/lib/email.ts` | Inline SMTP fallback | Implemented | Low | 3 attempts + backoff + metrics |
| Worker email | `worker/email.ts` | SMTP send | Implemented | Low | 3 attempts + exp backoff + timeouts |
| Email task | `tasks/notification-email.ts` | Queued send | Implemented | Low | `ok:false` → BullMQ retry |
| Preferences table | `notification_preferences` | Consent store | Implemented | Medium | Enforced on reads; writes from UI broken (new P1) |
| Preferences API/UI | `routes/notification-preferences.ts`, `NotificationPreferencesClient.tsx`, bell | Toggles | Implemented | High | `sms` accepted; org omitted |
| Test email | `routes/admin.ts:53-86` | SMTP verification | Implemented | Low | `rateLimitEmail` 5/h; audited |
| Reminder jobs | `scheduled-notifications.ts` + `schedule-config.ts` | task-due daily | Implemented + scheduled | Low | Idempotent claim; tested |
| Scan notifications | `module-tasks.ts` | License/vendor/renewal/approval | Implemented | Low | Gated + keyed; no email |
| Push / VAPID | — | Browser push | **Absent** | Medium | No code/env/table (NOTIF-P2-001) |
| Email templates | inline HTML ×4 | Branding | Partial | Low | No shared template (NOTIF-P3-001) |
| Unsubscribe/opt-out | — | Global opt-out | **Absent** | Medium | No link/header; per-module toggles only |
| Delivery metrics | `api/lib/metrics.ts`, `worker/metrics.ts` | Observability | Implemented | Medium | No alert rule; SLO semantics wrong |
| ntfy alerting | alertmanager tmpl + workflows | Ops alerts | Implemented | Medium | Critical receiver optional; delivery unexercised |
| Rate limiting | `middleware/rate-limit.ts` | Abuse control | Partial | Low-Medium | Global 600/15min; no per-recipient send throttle |
| Tests | API/worker unit + web E2E | Verification | Partial | Medium | No persistence, alerting, or multi-org tests |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Notification models | 4 | `5302029`/`5302107`/`5302057`; sanitized SSE; RLS | Plaintext body; no sensitivity field | Sensitivity/redaction policy |
| Email templates | 2 | Inline HTML ×4; `escapeHtml` | No shared template/footer | One template helper with preferences link |
| Push subscriptions | 0 | grep — none | Channel absent | Implement or record out-of-scope |
| VAPID/config | 0 | no VAPID env keys | No push config | Add keys if push pursued |
| Reminder jobs | 4 | `scheduled-notifications.ts`, `schedule-config.ts`, claim + tests | Org-less preference resolution | Pass org; multi-org test |
| Preferences | 3 | Table+API+UI; enforced on sends | Writes cannot persist (org NOT NULL) | Org fallback in PUT; persistence test |
| Tenant scoping | 4 | user_id filters; SSE org assertion; prefs RLS | mark-all-read org via query only | Keep guard tests green |
| Unsubscribe/opt-out | 2 | Per-module toggles (enforced) | No link/header/global pause | Footer link + global pause |
| Retries | 4 | worker 3× exp; API 3× linear; BullMQ 3× | No email-side idempotency on API path | Gate email on dedup |
| Failure handling | 3 | bool results, metrics, Sentry, skip metering | No alert rule; SLO counts enqueue as success | Alert rule + terminal-outcome SLO |
| Duplicate prevention | 4 | Key upsert everywhere; worker email claim | API email still sent when deduped | Mirror claim in `notifyAndEmail` |
| Rate limiting | 3 | Global per-user; `rateLimitEmail` test-email | No per-recipient send throttle | Per-recipient email bucket |

## Detailed Review

### Item: Preference enforcement and its write path

- Evidence: `notification-channels.ts:53-105`, `notify.ts:116-128,167-202`, `notification-store.ts:31-79`, `notification-preferences.ts:45-74`, `NotificationPreferencesClient.tsx:81-90`, `NotificationBell.tsx:175-185`, `5302026…v3.sql:231-240`.
- What it does: Send paths resolve `notification_preferences` (default-on, fail-safe) and suppress channels; the API/UI store preferences per `(organization_id, user_id, module_key, channel)`.
- How it appears to work: Enforcement is real and tested. The write path is broken from the web: the PUT body has no `organizationId`, the route does not fall back to `req.orgId` (which `requireOrgAccess` resolves and injects into `req.query`), and `organization_id` is NOT NULL with no default, so the upsert cannot satisfy the constraint. Both clients swallow the failure.
- Dependencies: Supabase service/scoped client; `requireOrgAccess`.
- Current controls: RLS self-or-admin, audit event, upsert conflict target, fail-safe defaults.
- Missing controls: org fallback/default in the PUT, error surfacing in the UI, persistence test.
- Risks: Consent boundary is non-functional; silent failure erodes trust.
- Recommended improvement: default `organization_id` to `req.orgId ?? req.query.organization_id` (or make it required and send it), surface errors, add API + E2E persistence tests.
- Suggested tests: PUT without `organizationId` → row written for the active org; toggle → save → reload → still off; bell toggle failure shows an error.
- Suggested docs: preference semantics (per-org) + a note that the toggle gates enforced channels only.

### Item: Dedup and idempotency across the two send paths

- Evidence: `notify.ts:68-110,173-221`; `notification-store.ts:86-99,144-171,200-217`; `notifications.ts:297-320`; worker tests `notification-store.test.ts:115-180`.
- What it does: Both sides derive `notification_key` (user/module/moduleId/action + 16-hex content fingerprint) and upsert with `ignoreDuplicates`. The worker additionally treats the insert as the email claim; the API does not.
- How it appears to work: Row dedup is uniform. Email dedup is worker-only; a replayed API call suppresses the row but re-enqueues the email.
- Dependencies: partial unique index `idx_notifications_key`; Redis idempotency store for the suppressed fallback.
- Current controls: atomic row upsert; worker email claim; scan lock; `recentlyNotified` windows.
- Missing controls: API email claim; job-id dedup on `notification-email`.
- Risks: Duplicate emails on retries/replays of ticket/comment/assignment flows.
- Recommended improvement: in `notifyAndEmail`, skip the email when `inApp.deduped` (or claim `notif-email-${key}` before enqueue).
- Suggested tests: two identical `notifyAndEmail` calls → one row, one email job.
- Suggested docs: dedup/idempotency contract for both send paths.

### Item: Reminder jobs and scheduling

- Evidence: `scheduled-notifications.ts:86-411`; `schedule-config.ts:47-54`; `main.ts:48-159`; `scan-lock.ts` via `runScheduledTask`.
- What it does: Daily `task-due` scan (24h window, limit 100), plus membership/ticket/custom typed notifications; per-run scan lock; 7-day `alerted` set and 10-minute `recentlyNotified` guards; atomic key claim before email.
- How it appears to work: Verified; the 7-day/10-minute guards are belt-and-braces on top of the atomic claim. Preference lookups omit the organization (new P3). `task-due` skips users whose profile has no email entirely (no in-app row either) — acceptable today because portal users always have an email.
- Dependencies: Supabase, Redis scan lock, SMTP.
- Current controls: scan lock, stagger offsets, dedup windows, atomic claim, metrics.
- Missing controls: org-scoped preference lookup; email failure does not fail the task (inline retries only).
- Risks: Low-Medium (inconsistent multi-org suppression; no retry beyond 3 attempts).
- Recommended improvement: pass `organizationId` in `resolveChannels`; consider failing the task (or re-queueing) when a transient send exhausts attempts.
- Suggested tests: multi-org opt-out only suppresses that org; SMTP-down run records email/failed.
- Suggested docs: scheduled reminder catalogue incl. dedup windows.

### Item: Email senders, retries, and SMTP configuration

- Evidence: `api/lib/email.ts:17-63`; `worker/email.ts:12-64`; `tasks/notification-email.ts:11-20`; `api/main.ts:18-33`; `worker/env.ts:96-99`; `deploy-do.yml:585-588,677-680`; `3f2a772c`.
- What it does: Both senders retry 3× (API linear 250 ms; worker exp 1000 ms with 10s timeouts), skip + meter when SMTP is unset, redact recipients in logs; production logs a boot error naming missing SMTP_* keys (non-fatal).
- How it appears to work: Verified. Fail-closed was deliberately reverted because the deployment has SMTP_HOST empty and the crash failed every deploy health gate.
- Dependencies: nodemailer, SMTP secrets.
- Current controls: bounded retries, timeouts, skip metering, boot signal, deploy forwards SMTP_*.
- Missing controls: SMTP still optional; no deploy gate; no alert on the skip counter.
- Risks: All email remains a no-op until the operator configures SMTP.
- Recommended improvement: re-introduce fail-closed (or a deploy gate) once SMTP exists; alert on email/skipped.
- Suggested tests: production-without-SMTP env test (the removed `env-smtp.test.ts`); skip counter assertion.
- Suggested docs: SMTP operations runbook + the fail-closed decision record.

### Item: In-app delivery (SSE, polling, read state)

- Evidence: `notifications.ts:36-173,194-290`; `NotificationBell.tsx`; `notifications-sse-scope.test.ts`; E2E `notifications*.spec.ts`.
- What it does: SSE stream with sanitized payloads, org assertion, keepalive, 5-minute JWT revalidation, initial unread backfill; list/unread/read/delete are user-scoped and audited; polling fallback every 30 s.
- How it appears to work: Verified. The fallback interval is not cleared on unmount and the `onerror` cleanup return is dead code.
- Dependencies: Supabase Realtime, cookie session.
- Current controls: whitelist, org assertion, auth revalidation, audit events.
- Missing controls: interval cleanup; reconnect backfill/ack.
- Risks: Low (leaked timer/background requests).
- Recommended improvement: store the interval id in a ref, clear on cleanup/re-create.
- Suggested tests: unmount clears the timer; SSE payload contains no body.
- Suggested docs: realtime notification behaviour and scope rules.

### Item: Observability, SLO, and alerting

- Evidence: `api/lib/metrics.ts:99-118,235-250`; `worker/metrics.ts:44-56,80-89`; `prometheus.yml:34-39`; `prometheus.rules.yml`; `dashboards/mct-overview.json:76`; `docs/SLO.md:17`; `docs/MONITORING_AND_ALERTING.md:126-151`.
- What it does: Both processes expose delivery/suppressed/dedup counters; Prometheus scrapes both; a dashboard stat and SLO expression use the API counter.
- How it appears to work: A successful enqueue is recorded as `email/success`; the worker's real outcome counter is not referenced by any rule/panel; there is no notification alert rule. The monitoring doc's metric table is stale (omits the notification counters and says worker metrics are not exported).
- Dependencies: Prometheus/Alertmanager (deployed).
- Current controls: counters, SLO doc, dashboard JSON, Alertmanager routing.
- Missing controls: alert rule; enqueue-vs-delivery separation; per-channel SLO.
- Risks: Silent email outage can look like 100% success.
- Recommended improvement: label the enqueue hand-off distinctly, compute the SLO from worker terminal outcomes per channel, add a failure/skip alert.
- Suggested tests: unit assertion that an enqueue records `queued`, not `success`; rule lint via `prometheus.rules.test.yml` pattern.
- Suggested docs: update the metric table and SLO section.

### Item: ntfy-based alerting (non-user notifications)

- Evidence: `alertmanager.tmpl.yml:12-15,105-152`; `docker-compose.yml:246-305`; `deploy-do.yml:617-632,740-752,801-805`; `db-backup.yml:48-67`; `storage-backup.yml:58-76`; `db-restore-test.yml:241-264`; `CHANGELOG.md:287-293`.
- What it does: Prometheus → Alertmanager → ntfy (critical/default) with basic auth via a write-only relay user; the Watchdog routes to an external dead-man's switch; backup/restore/storage failures POST to the ntfy topic with a Slack fallback.
- How it appears to work: The compose awk renderer substitutes all placeholders and unset URLs default to a loopback no-op; prod fails the deploy only for the watchdog URL, while a missing critical URL or missing relay credentials is a warning (ntfy would 403). Backup notifiers swallow POST failures with `|| true`.
- Dependencies: ntfy.mainecybertech.us, GitHub secrets, Alertmanager.
- Current controls: fail-closed watchdog, credential wiring, Slack fallback, Watchdog heartbeat.
- Missing controls: fail-closed critical receiver, delivery exercise artifact, notify-failure visibility.
- Risks: Critical alerts silently undeliverable in production.
- Recommended improvement: fail prod deploys when the critical URL is unset (or document acceptance); record one real alert exercise in the runbook; consider alerting on notify failure.
- Suggested tests: a synthetic critical alert exercise (manual) + a config-render test that no placeholder survives.
- Suggested docs: monitoring runbook exercise log; fix the compose/template renderer comment mismatch (awk vs envsubst/sed).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| NOTIF-001 | Notification models | `5302029`, `5302107`, `5302057` | Row store + unique key + RLS | Plaintext body; no sensitivity field | P2 | Sensitivity/redaction policy |
| NOTIF-002 | Email templates | inline HTML ×4 | Escaped inline HTML | No engine/footer/unsubscribe | P3 | Shared template helper |
| NOTIF-003 | Push subscriptions | grep — none | None | Channel absent | P2 | Implement or document out-of-scope |
| NOTIF-004 | VAPID/config | env schemas | None | No push config | P2 | Add keys if pursued |
| NOTIF-005 | Reminder jobs | `scheduled-notifications.ts`, `schedule-config.ts` | Daily + claim + windows | Org-less preference lookup | P3 | Pass org; multi-org test |
| NOTIF-006 | Preferences | `notification-channels.ts`, UI | Enforced on sends | UI writes cannot persist (NOT NULL) | P1 | Org fallback in PUT + tests |
| NOTIF-007 | Tenant scoping | `notifications.ts:36-44,154-156` | User + org assertions | — | P3 | Keep guard tests green |
| NOTIF-008 | Unsubscribe/opt-out | prefs toggles only | Per-module toggles | No link/header/global pause | P3 | Footer link + global pause |
| NOTIF-009 | Retries | `api/lib/email.ts`, `worker/email.ts` | 3× both, BullMQ 3× | API email not deduped on replay | P2 | Mirror worker claim |
| NOTIF-010 | Failure handling | metrics, logs, Sentry | Metered + logged | No alert rule; SLO semantics | P2 | Alert + terminal-outcome SLO |
| NOTIF-011 | Duplicate prevention | key upsert + worker claim | Two-path dedup | API email re-sent when deduped | P2 | Gate email on `deduped` |
| NOTIF-012 | Rate limiting | `rate-limit.ts` | Global per-user 600/15min | No per-recipient send throttle | P3 | Per-recipient email bucket |

## Findings

Full evidence, impact, recommendations, owners, targets, confidence and statuses are in `30_notification_email_push_delivery_audit.json`. Summary:

| Title | Severity | Status |
|---|---|---|
| Notification preferences are stored and displayed but never enforced on any send path | P1 | verified-fixed |
| API-originated notifications bypass the dedup unique index | P1 | verified-fixed |
| No delivery observability: email/notification failures are silent and unalerted | P1 | partially-fixed |
| Notification preference writes from the web UI omit organization_id (NOT NULL) so toggles cannot persist | P1 | open (new) |
| Web Push channel is entirely absent (no subscriptions, no VAPID, no service worker) | P2 | still-open |
| SMTP remains optional; email silently degrades to no-op in production | P2 | partially-fixed |
| Worker lacks an `unhandledRejection` handler (independently verified) | P2 | verified-fixed |
| Scheduled reminder inserts and email sends are not atomic; retries can double-send | P2 | verified-fixed |
| Sensitive ticket content is stored and emailed verbatim with no sensitivity filter | P2 | still-open |
| API inline email fallback has no retry and ignores the send result | P2 | verified-fixed |
| `sms` channel is a dead preference option; UI copy misstates enforcement | P3 | partially-fixed |
| No email template system; repetitive inline HTML diverges between senders | P3 | still-open |
| SSE polling fallback interval is not cleared on unmount | P3 | still-open |
| `notification-preferences` PUT accepts a body `organizationId` without `assertOrgScopeMatches` (SEC-P3-004) | P3 | verified-fixed |
| Realtime/SSE notification channel is scoped by user only, with no org assertion (MT-P2-004) | P2 | verified-fixed |
| Backup-failure alerting is present but cannot be trusted to deliver (DR-P2-001, ntfy) | P2 | verified-fixed |
| notifyAndEmail enqueues email even when the in-app notification was deduped | P2 | open (new) |
| Notification delivery SLO counts a queued email hand-off as success and excludes worker send outcomes | P2 | open (new) |
| Alertmanager→ntfy critical alert delivery is optional in production and has no in-repo exercise evidence | P2 | open (new) |
| No unsubscribe link or global opt-out in notification emails | P3 | open (new) |
| Worker reminder preference lookups omit the organization (cross-org suppression) | P3 | open (new) |
| No per-recipient send throttle on notification producers | P3 | open (new) |
| Worker ticket-responded email builds the deep link from unescaped payload metadata | P3 | open (new, latent) |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Users cannot opt out (preferences never persist) | High | High | Consent/trust, support load, possible regulatory exposure | `notification-preferences.ts:63-74`; `5302026…v3.sql:233` | Org fallback in PUT + persistence test |
| Email outage invisible in SLO/dashboard | High | Medium | Silent loss of all notification email | `notify.ts:215-220`; `mct-overview.json:76` | Terminal-outcome SLO + alert rule |
| Duplicate emails on API replay | Medium | Medium | Noise, eroded trust | `notify.ts:173-221` | Gate email on `inApp.deduped` |
| Sensitive comment content emailed/persisted verbatim | Medium | Medium | PII/credential disclosure | `tickets.ts:386-395` | Abstract + deep link; redaction |
| Critical alerts undeliverable (ntfy receiver unset/403) | Medium | Medium | Missed outages | `deploy-do.yml:749-752`; `docker-compose.yml:257` | Fail prod deploy or document acceptance |
| Missed alerts with no browser tab open (no push) | Medium | High | Slow response to assignments/overdues | grep — no push code | Implement push or record out-of-scope |
| Cross-org reminder suppression for multi-org users | Low | Medium | Dropped reminders | `scheduled-notifications.ts:167` | Pass org; multi-org test |

## Recommendations

### Immediate / Release Blocking

- Fix the preferences write path: default `organization_id` to `req.orgId ?? req.query.organization_id` (or require it and send it from the web), surface the error in both UIs, and add a save/reload E2E. Until this is fixed, no user can actually opt out.

### This Week

- Gate `notifyAndEmail` email on `inApp.deduped` (mirror `claimNotificationEmail`).
- Add a Prometheus alert on notification/email failure and skipped rates; route it through the existing Alertmanager receivers.
- Configure SMTP_HOST/PORT/USER/PASS on the droplet (or set the deploy gate) to close NOTIF-P2-002.

### This Month

- Recompute the delivery SLO from worker terminal outcomes per channel; label the API enqueue as a hand-off, not a success; update `docs/SLO.md` and the dashboard.
- Make the prod deploy fail when `ALERTMANAGER_CRITICAL_WEBHOOK_URL` is empty (or document the accepted risk) and record one real alert exercise.
- Add the sensitivity/redaction policy for notification bodies and emails (NOTIF-P2-005).
- Remove `sms` from the preferences API surface (or implement it).

### Later / Platform Evolution

- Implement Web Push + VAPID (or record the out-of-scope decision).
- Introduce the shared email template with a preferences/unsubscribe footer and a global pause-all toggle.
- Add per-recipient email throttling; fix the SSE fallback timer; harden the worker email links.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Org fallback in preferences PUT | Restores all consent toggles | `apps/api/src/routes/notification-preferences.ts` | PUT without org writes a row; E2E save/reload |
| Skip email when deduped | Stops duplicate emails on replay | `apps/api/src/lib/notify.ts` | Unit: second identical call sends no email |
| Email failure alert rule | Turns a silent outage into a page | `infra/digitalocean/prometheus.rules.yml` | `promtool`/rules test; synthetic failure |
| Clear SSE fallback interval | Stops leaked polling | `apps/web/components/NotificationBell.tsx` | Unit test with fake timers |
| Remove `sms` from API enums | Removes a dead option | `apps/api/src/routes/notification-preferences.ts` | PUT with sms → 400 |
| Preferences persistence E2E | Catches the class of bug | `apps/web/e2e/portal/notifications-page.spec.ts` | Toggle → save → reload assertion |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Preference write-path fix + tests | P1 | notifications/backend | S | none |
| API email idempotency claim | P2 | notifications/backend | S | existing key scheme |
| Notification alert rule + SLO rework | P2 | platform + notifications/backend | M | Prometheus/Alertmanager |
| Sensitive-content policy for notifications/email | P2 | notifications/backend + privacy | M | product decision |
| SMTP configuration + fail-closed decision | P2 | platform | S | droplet secrets |
| Web Push channel (or scope decision) | P2 | platform | L | VAPID keys, migration, SW |
| Shared email template + unsubscribe/global pause | P3 | notifications/backend/frontend | M | template helper |
| Per-recipient send throttle | P3 | notifications/backend | M | rate-limit middleware |
| Org-scoped worker preference resolution | P3 | notifications/backend | S | payload org ids |
| Worker email link escaping | P3 | notifications/backend | S | none |
| SSE fallback timer cleanup | P3 | notifications/frontend | S | none |

## Suggested Tests

- **Unit (API):** PUT preferences without `organizationId` persists for the active org; `notifyAndEmail` does not enqueue when `inApp.deduped`; enqueue records a distinct hand-off outcome; `sendEmail` skip increments the skip counter.
- **Unit (worker):** multi-org preference resolution (org A opt-out does not suppress org B); claim semantics for inserted/deduped/suppressed; ticket-responded link encoding.
- **Integration:** admin create → recipient with in_app disabled → suppressed result and no row; ticket comment → preference-disabled email → no job; retried scheduled task → one email.
- **E2E:** preferences toggle → save → reload → still off; bell toggle error is surfaced; SSE reconnect with polling fallback.
- **CI / security:** malicious ticket id in a notification email does not break out of the href (API and worker); `promtool`-style rule test for the new notification alert.
- **Manual validation:** send the admin test email with SMTP configured; dispatch a synthetic critical alert to ntfy and record the run URL; exercise a backup-failure notification and record it in the runbook.

## Suggested Documentation Updates

- `docs/modules/notification-preferences.md` — remove/flag the `sms` channel; document per-org semantics and the org field requirement.
- `docs/modules/notifications.md` — add the dedup key semantics, preference gating, and the enqueue-vs-delivery metric distinction.
- `docs/SLO.md` — recompute objective 4 from worker terminal outcomes per channel; add the alert rule.
- `docs/MONITORING_AND_ALERTING.md` — add the notification counters to the metric table; document the notification alert; record the ntfy alert exercise and the critical-receiver gate.
- New runbook: email/SMTP operations (SMTP-unset boot error, skip counter, test-email, fail-closed decision).
- `CHANGELOG.md` / ADR: the fail-closed revert rationale and the conditions to re-enable it.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the preferences PUT actually 500 from the web, or does some path inject organization_id? | Confirms the P1 severity | One API call or DB row after a UI save |
| Is `ALERTMANAGER_CRITICAL_WEBHOOK_URL` set in the prod environment today? | Whether critical alerts are deliverable | Environment secret inventory (operator) |
| Was the DR-P2-001 ntfy delivery exercised (run URL)? | Delivery vs configuration | PR #157 / workflow run artifact |
| Is SMTP configured on the droplet now? | Whether email is a no-op in production | Droplet `.env` presence check (operator) |
| Is Web Push in or out of scope for the product? | NOTIF-P2-001 disposition | Product decision record |

## Appendix

Commands used (read-only; no installs/builds/tests/network):

```
git -C /tmp/opencode/mct-audit-target rev-parse HEAD                 # 8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd
git log --oneline 9c0b88c..8d299b8d -- <notification files>          # fix commits 3f2a772c, 1c066787, 68379c76, 69efe096, c59f133e, 109bde14, 8548cade
grep -rn 'from("notifications")' apps --include='*.ts'               # all writes route through the two helpers
grep -rin 'vapid|web-push|pushManager|serviceWorker|PushSubscription' apps packages   # no matches
grep -rn 'unhandledRejection|uncaughtException' apps/*/src            # API main.ts:85-92, worker main.ts:30-45
grep -rn 'recordNotificationDelivery|recordNotificationSuppressed'    # emission sites on both sides
grep -n 'alert:|expr:' infra/digitalocean/prometheus.rules.yml        # no notification rule
grep -rn 'ntfy' .github/workflows/*.yml infra/digitalocean/*.yml      # backup notifiers + Alertmanager relay
sed -n '231,240p' supabase/migrations/5302026_...corrected.v3.sql     # organization_id NOT NULL, no default
```

Observations: no application file was modified; the target worktree was not written to; secret values were not read or printed. The `.github`/infra ntfy paths were inspected as text only; no alert or email was sent.
