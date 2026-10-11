# 13_resilience_recovery_failure_modes — Prompt 13 - Resilience, Recovery, and Failure Modes Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `13_resilience_recovery_failure_modes.md` (area RES, prompt)

## Verification Performed

# Resilience, Recovery, and Failure Modes Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (target worktree `/tmp/opencode/mct-audit-target`, read-only)
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11
- Auditor: domain subagent (area RES, prompt `13_resilience_recovery_failure_modes.md`)
- Area code: RES
- Output paths: `_domains/13_resilience_recovery_failure_modes.json`, `_domains/13_resilience_recovery_failure_modes_body.md`
- Scope limitations: repository-only review. No running API/worker/Redis/Supabase/SMTP, no provider traffic, no lab, no docker commands against the target. Every claim is source/config/migration/test evidence at `8d299b8d`. Timeouts and retry behavior were read from code, not exercised (except unit tests already in the repo).

## Scope

Reviewed at `8d299b8d`:

- Worker runtime: `apps/worker/src/main.ts`, `consumer-bullmq.ts`, `consumer-sqs.ts`, `shutdown.ts`, `env.ts`, `task-registry.ts`, `producer.ts`, `health-server.ts`, `metrics.ts`, `schedule-config.ts`, `lib/{idempotency,scan-lock,ssrf-guard,pinned-fetch}.ts`, `tasks/{webhook-dispatcher,webhook-retry,notification-email,orphan-cleanup,retention,module-tasks,m365-calendar-sync,jira-sync,jsm-sync,stripe-reconcile}.ts`.
- API runtime: `main.ts`, `app.ts`, `middleware/{request-timeout,idempotency,cache,rate-limit}.ts`, `lib/{circuit-breaker,http-client,idempotency,webhook-dispatcher,task-producer,email,notify}.ts`, `services/{supabase,audit}.ts`, `routes/{health,webhooks,notifications,public,auth}.ts`.
- Deploy/runtime config: `infra/digitalocean/{docker-compose.yml,prometheus.yml,prometheus.rules.yml,alertmanager.tmpl.yml}`, `.github/workflows/{deploy-do,db-backup,db-restore-test,storage-backup,backup-dispatch,supabase-migrations}.yml`, `scripts/{rollback.sh,backup-database.sh}`, `apps/{api,worker}/Dockerfile`.
- Docs: `docs/{PLATFORM_FAILURE_RUNBOOKS,RTO_RPO,ROLLBACK_PROCEDURES,INCIDENT_RESPONSE,MONITORING_AND_ALERTING,ENVIRONMENT_VARIABLES}.md`, `AGENTS.md`, `scripts/load-testing/README.md`.
- Tests: `apps/worker/src/__tests__/{main,shutdown,health,webhook-dispatcher,webhook-retry,orphan-cleanup,retention}.test.ts`, `apps/api/src/__tests__/{circuit-breaker,idempotency,lib-idempotency,webhook-dispatcher-idempotency}.test.ts`.
- Not reviewed here (owned elsewhere): RLS policy breadth (RLS), webhook signature/replay internals (WH), backup encryption/offsite provisioning details (DR), Terraform/CI governance (INFRA/CI), container hardening (CTR).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/worker/src/main.ts` (166 lines) | Source | Process handlers, scheduler, scan locks | unhandledRejection, staggered scans, queue fallback |
| `apps/worker/src/consumer-bullmq.ts`, `consumer-sqs.ts` | Source | Queue consumption + shutdown | lockDuration=WORKER_TIMEOUT; failed handler logs only |
| `apps/worker/src/shutdown.ts` | Source | Graceful shutdown | Watchdog (default 30s), in-flight replace-set |
| `apps/worker/src/env.ts` | Source | Queue backend guards | inline rejected in production; REDIS_URL required for bullmq |
| `apps/api/src/lib/circuit-breaker.ts`, `services/supabase.ts` | Source | Supabase breaker | Global breaker on all REST calls; uncleared timer |
| `apps/api/src/lib/webhook-dispatcher.ts`, `apps/worker/src/tasks/{webhook-dispatcher,webhook-retry}.ts` | Source | Outbound retry + DLQ | Atomic claims, Idempotency-Key, 5-attempt backoff, DLQ |
| `apps/api/src/routes/webhooks.ts` (655 lines) | Source | Inbound Stripe/Jira/JSM/M365 | Unchecked persistence errors, ACK 200 |
| `apps/api/src/middleware/{request-timeout,idempotency,cache}.ts` | Source | Request deadline, idempotency, Redis fallback | 408 advisory; atomic claim; in-memory fallback |
| `infra/digitalocean/docker-compose.yml` | Config | Prod runtime | No stop_grace_period; healthchecks; QUEUE_BACKEND=bullmq |
| `infra/digitalocean/prometheus.rules.yml`, `alertmanager.tmpl.yml` | Config | Alerting + dead-man's switch | Watchdog → external; no queue/DLQ rule |
| `.github/workflows/{deploy-do,db-restore-test}.yml` | CI | Deploy gate, restore verification | Fatal worker gate; integrity assertions |
| `docs/{PLATFORM_FAILURE_RUNBOOKS,RTO_RPO}.md` | Docs | Recovery readiness | Drill table all `_pending`; PITR RPO unproven |
| `apps/web/public/sw.js` + web grep | Source | Offline client | SW present, never registered |
| `scripts/load-testing/*.js` | Tests | Load/failure testing | k6 scripts, not wired to CI |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline -3` in target | Command | Bind the audit to a commit | `8d299b8d Merge PR #168: promote develop to main` |
| `git log --oneline 9c0b88c..8d299b8d \| wc -l` | Command | Window since the previous run | 113 commits; remediation PRs #121–#168 visible |
| `git show --stat 8548cade` | Command | RES–P2-001/004, RES–P3-001 fix | unhandledRejection + shutdown watchdog + bounded fetches; on main |
| `git show --stat 1c066787` | Command | RES–P2-003 fix | inline rejected in production; tests; PR #142 |
| `grep -rn "WORKER_TIMEOUT" apps/ docs/ .github/` | Command | RES–P2-002 | Only env default, BullMQ lockDuration, tests, docs |
| `grep -rn "task_dead" supabase/ apps/ docs/` | Command | RES–P2-002 | No task dead-letter table or code anywhere |
| `grep -rn "closeScanLock\|closeIdempotency" apps/worker/src` | Command | Shutdown completeness | Definitions only; never called outside tests |
| `grep -rn "stop_grace_period" infra/ .github/ docker-compose.yml` | Command | Shutdown budget | No hits (Docker default 10s applies) |
| Python sweep of every `fetch(` site in `apps/`, `packages/sdk` | Command | RES–P2-004 | 17/17 sites carry a signal or setTimeout-abort |
| `grep -n "alert:\|expr:" infra/digitalocean/prometheus.rules.yml` | Command | Queue/alert detection | 2 rule groups; no queue/DLQ rule |
| `grep -rn "serviceWorker" apps/web` | Command | Offline client | No registration anywhere |
| `grep -rn "load-testing\|k6" .github/workflows` | Command | Failure/load tests | No CI wiring |
| `grep -n "RES-" .../follow_up_register.md` | Command | Verification duty | 11 RES rows located and re-checked |
| `python3 -c` JSON validation of the findings file | Command | Output contract | 20 findings; P2×10, P3×10; statuses valid |

## Executive Summary

The asynchronous and recovery paths are materially stronger than in the previous run. Outbound `fetch` calls are all bounded; the worker can no longer start in production with the idle `inline` backend; the worker has an unhandled-rejection handler and a shutdown watchdog; both webhook dispatchers claim idempotency keys atomically and the retry task owns a real dead-letter set; the deploy gate now fails when the worker is unhealthy; and the weekly restore test asserts integrity and freshness instead of printing counts.

The gaps that remain are about **detection and completion**, not about the happy path:

1. **No task-level timeout and no generic task DLQ.** `WORKER_TIMEOUT` is only a BullMQ lock, `executeTask` never cancels a handler, and a permanently failing task is logged and dropped after 3 attempts (webhooks excepted). Operators cannot see or replay stuck work. (RES–P2-002, still-open.)
2. **Queue degradation is invisible.** The worker reports HTTP 200 and Docker/Prometheus stay green when its queue connection is dead, and no alert rule consumes queue depth or connectivity. Redis loss therefore stalls email, webhook retries/DLQ, scans and retention silently. (New P2.)
3. **Graceful shutdown is not effective in production.** No `stop_grace_period` is set, so Docker SIGKILLs the worker at 10s while its drain budget is 30s; the scan-lock/idempotency/producer Redis handles are never closed, so even a clean drain cannot exit naturally. In-flight jobs can be killed mid-run and redelivered. (New P2.)
4. **Inbound webhook handlers ACK 200 on unobserved write failures.** Stripe/Jira/JSM handlers ignore Supabase `{error}` returns and release the idempotency claim only on thrown errors; during a DB degradation the provider never retries and the claim blocks replay for 24h. (New P2.)
5. **Recovery is written, not exercised.** The runbook drill table is entirely `_pending`; the PITR RPO is explicitly unproven; and `docs/INCIDENT_RESPONSE.md` still tells responders the dead-man's switch does not exist. (RES–P2-005/006, partially-fixed.)
6. **Deploys are stop-the-world** (`docker compose down` before `up`), so every release and rollback is a planned full outage. (New P2.)

Recommended next actions: add a task timeout + `task_dead_letters` and a queue-connectivity gauge/alert; set `stop_grace_period` and close Redis handles on shutdown; make inbound webhook handlers fail on persistence errors; record one restore drill and one dead-man's-switch exercise; and fix the stale incident doc.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| BullMQ consumer | `apps/worker/src/consumer-bullmq.ts` | Execute jobs | Implemented (prod) | Medium | lockDuration only; failed handler logs |
| SQS consumer | `apps/worker/src/consumer-sqs.ts` | Fallback backend | Implemented, unused in prod | Low | no redrive/DLQ config in code |
| Inline backend | `apps/worker/src/env.ts:58-65` | Local/dev | Blocked in production | Low | fail-fast guard + tests |
| Task registry | `apps/worker/src/task-registry.ts` | Dispatch | Implemented | Medium | no timeout, no DLQ |
| Shutdown watchdog | `apps/worker/src/shutdown.ts` | Force exit on hung drain | Implemented + tested | Medium | 30s budget vs Docker 10s |
| Scan lock | `apps/worker/src/lib/scan-lock.ts` | One replica per scan | Implemented | Low | runs unlocked if Redis down |
| Task producers | `apps/api/src/lib/task-producer.ts`, `apps/worker/src/producer.ts` | Enqueue | Implemented | Low | never throw; 3 attempts, exp 5s |
| Webhook retry/DLQ | `apps/worker/src/tasks/webhook-retry.ts` | Retry + dead letters | Implemented | Low | 5 attempts, 1m×2^n, batch 20 |
| Outbound dispatchers | API + worker `webhook-dispatcher` | Deliver events | Implemented | Low | atomic per-endpoint claims |
| Inbound receivers | `apps/api/src/routes/webhooks.ts` | Stripe/Jira/JSM/M365 | Implemented | High | unchecked write errors + ACK 200 |
| Request deadline | `apps/api/src/middleware/request-timeout.ts` | 408 at 30s | Implemented | Medium | advisory only; no abort |
| Idempotency middleware | `apps/api/src/middleware/idempotency.ts` | Replay-safe mutations | Implemented | Low | atomic claim, stored replay |
| Supabase breaker | `apps/api/src/lib/circuit-breaker.ts` | Fail fast on DB failure | Implemented + tested | Medium | global scope; timer leak |
| Redis cache | `apps/api/src/middleware/cache.ts` | Response cache | Implemented | Low | in-memory fallback |
| Worker health | `apps/worker/src/health-server.ts` | Liveness | Implemented | High | 200 even when queue dead |
| Worker metrics | `apps/worker/src/metrics.ts` | Queue depth, deliveries | Implemented | Medium | queue depth not alerted |
| Backups | `scripts/backup-database.sh`, `db-backup.yml` | Daily dump | Implemented | Low | upload not verified post-hoc |
| Restore test | `.github/workflows/db-restore-test.yml` | Weekly verify | Implemented, strong | Low | structural + freshness + RLS |
| Storage backup/restore | `storage-backup.yml`, `scripts/restore-storage.sh` | File durability | Implemented | Low | see DR domain |
| Rollback (workflow) | `deploy-do.yml` `rollback_sha` | Deploy rollback | Implemented | Low | builds skipped, tag must exist |
| Rollback (manual) | `scripts/rollback.sh` | SSH fallback | Stale | Medium | wrong GHCR prefix; weak checks |
| Deploy path | `deploy-do.yml:809-858` | Release | Stop-the-world | Medium | down→up→health |
| Alert path | `prometheus*.yml`, `alertmanager.tmpl.yml` | Detect + deliver | Implemented | Medium | watchdog external; no queue/DLQ rules |
| Runbooks | `docs/PLATFORM_FAILURE_RUNBOOKS.md` | Recovery procedures | Written | Medium | drills all `_pending` |
| Offline client | `apps/web/public/sw.js` | Offline cache | Dead code | Low | never registered |
| Load/chaos tests | `scripts/load-testing/*.js` | Capacity/failure | Present | Medium | not wired to CI |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Timeouts | 3 | All 17 outbound fetch sites bounded; `http-client.ts:14-18`; `requestTimeout(30000)` `app.ts:151` | `WORKER_TIMEOUT` is lock-only; 408 does not abort work | Implement handler cancellation; document lock-only semantics |
| Retries/backoff | 4 | BullMQ 3× exp 5s; webhook 5× 1m×2^n; email 3× 1s×2; 429-aware Jira/JSM/Stripe; SDK retries with Idempotency-Key | No jitter; generic tasks have no DLQ | Add jitter + task DLQ; document retry owners |
| Idempotency | 4 | Atomic claim middleware; per-endpoint webhook claims; notification dedup key; 24h TTL | Inbound ACK-on-error; in-memory fallback is single-instance | Fail webhook handlers on persistence errors |
| Circuit breakers | 3 | Supabase breaker with tests; no-breaker health client | No breaker for Stripe/JSM/M365/SMTP; timer leak; global scope | Fix timer/cancel; consider per-integration breakers |
| Queue DLQ | 2 | Webhook DLQ + admin re-drive works | No task DLQ; queue outage invisible | Add `task_dead_letters` + metrics/alerts |
| Webhook recovery | 3 | Retry/DLQ/replay window/admin re-drive; outbound idempotent | Inbound handlers ACK 200 on write failure | Return 5xx + release claim on write error |
| Worker recovery | 2 | Watchdog; unhandledRejection; health endpoint | No task timeout; health ignores queue; restart loses queued visibility | Add timeout + queue health surfacing |
| Graceful shutdown | 3 | Drain + watchdog + tests; API force exit 10s | No `stop_grace_period`; Redis handles open; no clean exit(0) | Set grace period; close handles; exit 0 |
| DB/Redis/API/email/file/realtime failure | 3 | Supabase breaker; cache fallback; email retries; SSE polling fallback; storage restore | Queue silent stall; no alert for queue/DB drift | Add queue alert; alert on 5xx and DLQ |
| Offline client | 1 | Manifest linked; bundled catalog fallback | `sw.js` unregistered; no offline UX | Register or delete the SW; document stance |
| Transactions | 2 | Upserts keyed by unique id; audit retries | No cross-statement transaction in app code; migration wrap open (DATA-P2-002) | Prefer RPC for multi-write handlers |
| Partial writes | 2 | Webhook delivery row + endpoint update are separate writes | Inbound handlers ignore partial failure and ACK | Check every write; fail closed |

## Detailed Review

### Item: Worker task execution (timeouts, DLQ)

- Evidence: `consumer-bullmq.ts:17-41`, `task-registry.ts:35-71`, `env.ts:10`, `producer.ts:43-49`, `api/src/lib/task-producer.ts:50-55`, migrations (no `task_dead_letters`).
- What it does: BullMQ worker with concurrency `WORKER_CONCURRENCY`; job options attempts 3, exponential 5s, removeOnComplete 100, removeOnFail 500; `lockDuration = WORKER_TIMEOUT`.
- How it appears to work: BullMQ renews locks for active jobs, so a long handler is not cancelled; after 3 failures the job stays in the failed set (last 500) and only a log line is emitted.
- Missing controls: handler cancellation, task DLQ table, failed-job admin view, DLQ metric/alert.
- Risks: permanently stuck/expensive jobs are invisible; a CPU-bound handler can block lock renewal and cause redelivery (duplicate work).
- Recommended improvement / tests / docs: see Finding RES–P2-002 (still-open).

### Item: Queue backend selection

- Evidence: `env.ts:44-66`, `consumer-sqs.ts:80-108`, `docker-compose.yml:130-160`, `main.test.ts:65-83`.
- What it does: `bullmq` (prod), `sqs`, `inline` (idle). Production refuses `inline` and requires `REDIS_URL` for `bullmq`.
- Missing controls: SQS path has no visibility-timeout/DLQ configuration in code (unused in prod); unknown backend values log a warning and fall through to SQS (`consumer-sqs.ts:95-97`).
- Risks: low (guard fixed); the SQS fallback is untested against a real queue.

### Item: Graceful shutdown

- Evidence: `shutdown.ts:13-39`, `consumer-bullmq.ts:56-67`, `consumer-sqs.ts:110-145`, `api/src/main.ts:62-79`, `docker-compose.yml` (no `stop_grace_period`), Dockerfiles (`CMD ["node", ...]`, PID 1).
- What it does: SIGTERM/SIGINT → mark shutting down (health 503), close BullMQ worker, drain tracked promises, watchdog exits 1 after 30s. API closes the server and force-exits after 10s.
- Missing controls: container stop budget ≥ drain budget; closing scan-lock/idempotency/producer connections; explicit `exit(0)` after a clean drain; idempotent signal handling in the API (`shutdown()` has no guard).
- Risks: see Finding "Graceful shutdown is not effective in production".

### Item: Webhook delivery and recovery

- Evidence: `api/src/lib/webhook-dispatcher.ts:40-99,134-261`, `worker/src/tasks/webhook-dispatcher.ts:23-219`, `worker/src/tasks/webhook-retry.ts:8-229`, `api/src/routes/webhook-management.ts:84-248`, `api/src/__tests__/webhook-dispatcher-idempotency.test.ts`.
- What it does: queued-first delivery with inline fallback; atomic per-endpoint idempotency claims; HMAC signatures; SSRF guard + pinned fetch; 3 in-process attempts then DLQ; worker retry 5 attempts with 1m×2^n backoff and DLQ rows; admin list/re-drive/dismiss.
- Missing controls: inbound handlers' write-error handling (Finding below); DLQ accumulation has metrics but no alert (IR-P2-003).
- Strengths: single retry owner (inline path marks rows dead-lettered), stable Idempotency-Key across layers, DLQ rows carry the original payload.

### Item: Supabase / DB failure behavior

- Evidence: `api/src/services/supabase.ts:50-61,131-134,228-230`, `api/src/lib/circuit-breaker.ts:21-138`, `api/src/routes/health.ts:91-126`, `api/src/middleware/cache.ts:62-97`, `api/src/lib/idempotency.ts:63-136`.
- What it does: every REST call goes through a shared circuit breaker (5 failures / 30s open / 2 successes to close); `db.timeout` 30s; health probes use a breaker-free client; Redis-backed cache/idempotency fall back to memory.
- Missing controls: breaker timer cleanup and cancellation; breaker is global (one failing table trips every table); no breaker on Stripe/JSM/M365/SMTP.
- Risks: acceptable fail-fast trade-off, but the timer leak and global blast radius are hardening gaps (Finding).

### Item: Email / notification failure

- Evidence: `worker/src/email.ts:12-64` (3 attempts, 1s×2, SMTP timeouts 10s each), `api/src/lib/email.ts` (bounded inline retry), `notification-email.ts`, `main.ts:96-100` (loud non-fatal SMTP warning).
- What it does: queued email retries 3× then returns `ok:false`; queued task retries via BullMQ attempts; delivery outcomes are metered.
- Missing controls: no SMTP circuit breaker; failed notification emails have no DLQ (they ride the generic task failure path).
- Risks: with the task-DLQ gap, a permanently failing email is only visible in logs/metrics.

### Item: Realtime (SSE)

- Evidence: `api/src/routes/notifications.ts:46-173` (keepalive 30s, auth revalidation 5m, scoped rows), `apps/web/components/NotificationBell.tsx:84-117` (EventSource with a 30s polling fallback on error).
- What it does: SSE stream over Supabase realtime; on failure the client falls back to polling the unread count.
- Missing controls: server-side subscribe errors are not surfaced (only the SUBSCRIBED status is written); no metric for stream failures.
- Risks: low; degradation is handled client-side.

### Item: Backups / restore / rollback

- Evidence: `db-backup.yml` (daily 04:00 UTC, failure notify), `db-restore-test.yml` (weekly, integrity assertions), `storage-backup.yml`, `scripts/backup-database.sh:95-138`, `docs/ROLLBACK_PROCEDURES.md` §1-3b, `scripts/rollback.sh`.
- What it does: encrypted optional dump + offsite copy; weekly structural/freshness/RLS restore verification; documented workflow rollback and manual paths.
- Missing controls: no recorded drill (Finding RES–P2-006); manual script stale (Finding); no post-upload object verification.

### Item: Alerting / availability detection

- Evidence: `prometheus.rules.yml:5-143` (service down, 5xx rate, impersonation, tenant scope, watchdog), `alertmanager.tmpl.yml` (watchdog/critical/default routes), `deploy-do.yml:728-748` (fail-closed watchdog URL in prod), `MONITORING_AND_ALERTING.md` §9.
- What it does: off-box dead-man's switch for total loss; critical delivery via ntfy/Slack; 5xx-rate and RLS-regression rules.
- Missing controls: no rule for worker queue connectivity/backlog, DLQ accumulation, or task failures; `INCIDENT_RESPONSE.md:124-128` contradicts the deployed switch.
- Risks: silent async-plane degradation (Finding).

### Item: Offline client

- Evidence: `apps/web/public/sw.js`, `apps/web/public/manifest.webmanifest`, `apps/web/app/layout.tsx:26`, grep for registration (none), `docs/GAP_ANALYSIS.md:67`.
- What it does: manifest is linked; the service worker is never registered; the storefront's bundled catalog fallback is server-side.
- Missing controls: registration, versioned cache strategy, offline page, `navigator.onLine` UX.
- Risks: low; dead asset + false confidence.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| RES-001 | Timeouts | `http-client.ts:14-18`; 17/17 fetch sites; `app.ts:151` | Bounded outbound calls; 408 middleware | No handler cancellation; `WORKER_TIMEOUT` lock-only | P2/P3 | AbortSignal into handlers; document semantics |
| RES-002 | Retries/backoff | BullMQ attempts/backoff; webhook-retry; email; JSM/Jira/Stripe 429 handling | Multi-layer retries with caps | No jitter; no generic DLQ | P2 | Add jitter; task DLQ |
| RES-003 | Idempotency | `middleware/idempotency.ts`; per-endpoint claims; SDK keys | Atomic claims + stored replay | Inbound ACK-on-error; memory fallback | P2 | Fail inbound handlers on write error |
| RES-004 | Circuit breakers | `circuit-breaker.ts`; `services/supabase.ts:50-61` | Supabase breaker + tests | Timer leak; global scope; no integration breakers | P3 | Clear timer; per-integration breakers |
| RES-005 | Queue DLQ | `webhook-retry.ts`; `webhook_dead_letters` | Real DLQ for webhooks + admin re-drive | No task DLQ; queue outage invisible | P2 | `task_dead_letters` + queue alert |
| RES-006 | Webhook recovery | Both dispatchers + retry + management UI | Retry/backoff/DLQ/replay window | Inbound handlers ACK on DB failure | P2 | Check writes; 5xx; release claim |
| RES-007 | Worker recovery | `shutdown.ts`; `main.ts:42-45`; `health-server.ts` | Watchdog + unhandledRejection | No task timeout; health ignores queue | P2 | Timeout + queue health |
| RES-008 | Graceful shutdown | `shutdown.ts`; compose (no `stop_grace_period`) | Drain + watchdog + tests | SIGKILL at 10s; open Redis handles | P2 | `stop_grace_period` ≥ 60s; close handles |
| RES-009 | DB/Redis/API/email/file/realtime failure | breaker; cache fallback; email retries; SSE polling | Partial isolation + fallbacks | Queue stall silent; no queue/DB-drift alert | P2 | Alert queue + 5xx; chaos tests |
| RES-010 | Offline client | `sw.js`; manifest; no registration | None effective | SW dead; no offline UX | P3 | Register or delete; document |
| RES-011 | Transactions | Upserts by unique key; `logAuditEvent` retries | Per-statement atomicity | No multi-write transaction/RPC | P2 | Use RPC for multi-step handlers |
| RES-012 | Partial writes | `webhooks.ts` writes; delivery+endpoint updates | Idempotent upserts in places | Unchecked errors; split writes | P2 | Check + fail closed; single RPC |
| RES-013 | Backups/restore | `db-backup.yml`; `db-restore-test.yml:135-232` | Daily dump; weekly integrity test | No drill record; PITR RPO unproven | P2 | Record drills; add PITR exercise |
| RES-014 | Rollback | `ROLLBACK_PROCEDURES.md`; `deploy-do.yml` rollback_sha; `rollback.sh` | Workflow rollback works | Manual script stale; deploy is down→up | P2/P3 | Fix script; per-service recreate |
| RES-015 | Incident runbooks | `PLATFORM_FAILURE_RUNBOOKS.md`; `INCIDENT_RESPONSE.md` | Written per failure mode | Drills pending; stale dead-man's-switch paragraph | P3 | Exercise + fix doc |
| RES-016 | Failure injection/load | `scripts/load-testing/*` | k6 scripts exist | Not run in CI; no chaos suite | P3 | Scheduled k6 + failure-injection job |

## Findings

### Finding ID: RES–P2-001 - Worker process has no `unhandledRejection` handler

- Severity: P2 · Confidence: high · Area: RES · Status: verified-fixed
- Evidence: `apps/worker/src/main.ts:42-45`; `apps/api/src/main.ts:85-87`; `git show --stat 8548cade`
- What is happening: background promise rejections are logged to Sentry and do not exit the worker.
- Why it matters / impact: no restart-loop on non-fatal async failures; fatal states remain on the uncaughtException path.
- Recommended fix / validation: none; keep the semantics documented.
- Owner: platform/backend · Target: this month · Note: re-verified at 8d299b8d — fix on main (mainecybertech#121 lineage).

### Finding ID: RES–P2-002 - `WORKER_TIMEOUT` is not a real task timeout; generic task failures have no DLQ

- Severity: P2 · Confidence: high · Area: RES · Status: still-open
- Evidence: `apps/worker/src/consumer-bullmq.ts:32` (lockDuration only); `apps/worker/src/task-registry.ts:35-71` (no timeout wrapper); `apps/worker/src/consumer-bullmq.ts:36-41` (failed handler logs); no `task_dead_letters` anywhere; `producer.ts:43-49` removeOnFail 500.
- What is happening: a hung handler is never cancelled; after 3 attempts the failure is logged and the job eventually falls out of Redis. Only webhooks have a DLQ.
- Why it matters: stuck/expensive work is invisible and unreplayable; operators cannot answer "what failed last night?" for any non-webhook task.
- Recommended fix: AbortSignal-based handler timeout (or document lock-only) + `task_dead_letters` written from the failed handler with a metric and alert.
- Suggested validation: test that a >timeout handler is aborted; test that a permanently failing task lands in the DLQ.
- Owner: platform/backend · Target: this month · Note: re-verified at 8d299b8d — unchanged; no code, table or surface added.

### Finding ID: RES–P2-003 - `QUEUE_BACKEND` default `inline` diverges from production and can silently stall all queued work

- Severity: P2 · Confidence: high · Area: RES · Status: verified-fixed
- Evidence: `apps/worker/src/env.ts:54-65`; `main.test.ts:65-83`; `docker-compose.yml:138`; `git show --stat 1c066787`.
- What is happening: production boot with `inline` or `bullmq` without `REDIS_URL` fails validation.
- Impact: the silent-stall misconfiguration cannot ship.
- Owner: platform/backend · Target: this month · Note: re-verified at 8d299b8d — mainecybertech#142.

### Finding ID: RES–P2-004 - External `fetch` calls without `AbortController` in `public.ts` and `auth.ts`

- Severity: P2 · Confidence: high · Area: RES · Status: verified-fixed
- Evidence: `public.ts:33-39`; `auth.ts:243-253,273-281`; 17/17 call sites swept carry signals; `http-client.ts:36-42`.
- Impact: no unbounded outbound call remains.
- Owner: platform/backend · Target: this month · Note: re-verified at 8d299b8d — mainecybertech#121 (8548cade).

### Finding ID: RES–P2-005 - Availability detection lives inside the failed domain; no external dead-man's switch or alert delivery

- Severity: P2 · Confidence: high · Area: RES · Status: partially-fixed
- Evidence: `alertmanager.tmpl.yml:86-100,144-152`; `prometheus.rules.yml:33-40`; `deploy-do.yml:728-748`; `PLATFORM_FAILURE_RUNBOOKS.md:112-118` (drills pending); `INCIDENT_RESPONSE.md:124-128` (stale claim); `RTO_RPO.md:45-47`.
- What is happening: the off-box watchdog + fail-closed prod deploy now exist, but there is no evidence the heartbeat path has ever been exercised and the incident doc still says it does not exist.
- Why it matters: during a real total-monitoring loss, the operator cannot trust the runbook to verify the off-box path.
- Recommended fix: record the documented stop-alertmanager drill with date/result; fix `INCIDENT_RESPONSE.md`; confirm the watchdog URL is provisioned.
- Owner: platform lead / security reviewer · Target: this month · Note: re-verified at 8d299b8d — mechanism present, exercise + doc consistency missing.

### Finding ID: RES–P2-006 - Backup/restore recovery is configured but not evidenced as exercised, and the restore test verifies only table counts

- Severity: P2 · Confidence: high · Area: RES · Status: partially-fixed
- Evidence: `db-restore-test.yml:135-232` (assertions); `:84-108` (fail on encrypted-without-key); `RTO_RPO.md:40-47`; `PLATFORM_FAILURE_RUNBOOKS.md:112-118`; `backup-database.sh:103-111`.
- What is happening: the "table counts only" half is fixed (structural + freshness + RLS assertions); no restore/PITR/single-host drill is recorded.
- Recommended fix: run and record a restore drill; add a PITR exercise before claiming the 5-minute RPO.
- Owner: platform/backend + platform/ops · Target: this month · Note: re-verified at 8d299b8d — DR-P0-002 lineage fixed the verification; exercise evidence absent.

### Finding ID: RES–P3-001 - Worker graceful shutdown has no force-exit fallback

- Severity: P3 · Confidence: high · Area: RES · Status: verified-fixed
- Evidence: `shutdown.ts:13-39`; `shutdown.test.ts:52-78`; `consumer-bullmq.ts:56-67`.
- Note: re-verified at 8d299b8d — watchdog + env override + tests; residual captured in the new shutdown-effectiveness finding.

### Finding ID: RES–P3-002 - Worker queued webhook dispatcher inserts deliveries without an idempotency key

- Severity: P3 · Confidence: high · Area: RES · Status: verified-fixed
- Evidence: `worker/src/tasks/webhook-dispatcher.ts:23-34,80-92,98-100,179`.
- Note: re-verified at 8d299b8d — builds, claims, sends and persists the key; dedupes against the API layer.

### Finding ID: RES–P3-003 - `AGENTS.md` documents the worker consumer incorrectly and omits the queue backend divergence

- Severity: P3 · Confidence: high · Area: RES · Status: partially-fixed
- Evidence: `AGENTS.md:17` (updated) vs `AGENTS.md:328` (still "SQS-based"); `consumer-sqs.ts:80-97`.
- Recommended fix: update AGENTS.md:328 to BullMQ-first with SQS/inline fallbacks.
- Owner: platform/backend · Target: this quarter · Note: re-verified at 8d299b8d — partially updated.

### Finding ID: RES–P3-004 - Deploy health gate treats worker unhealthiness as non-fatal

- Severity: P3 · Confidence: high · Area: RES · Status: verified-fixed
- Evidence: `deploy-do.yml:915-922` (exit 1); `:835-858` (container gate includes worker); `docker-compose.yml:174-184`.
- Note: re-verified at 8d299b8d — worker health is fatal (IR-P1-003/CTR-P2-004 lineage).

### Finding ID: RES–P3-005 - Orphan cleanup lists at most 1000 objects per bucket and cannot verify the purge shrank anything

- Severity: P3 · Confidence: high · Area: RES · Status: partially-fixed
- Evidence: `orphan-cleanup.ts:10-17,97-127,204-235,237-255`.
- What is happening: pagination + a 10k fail-closed ceiling replaced the 1000-object truncation; removal is still not verified against the bucket afterwards.
- Recommended fix: post-remove re-list/compare; metric when the 10k ceiling aborts cleanup.
- Owner: platform/backend · Target: this quarter · Note: re-verified at 8d299b8d — DATA-P2-003/008 lineage; verification half remains.

### Finding ID: pending - Inbound webhook handlers ACK 200 while ignoring persistence errors, dropping events during DB degradation

- Severity: P2 · Confidence: high · Area: RES · Status: open
- Evidence: `webhooks.ts:190-210,230-246,254-261,281-294` (unread `{error}`); `:308-314` (only warning); `:413-423,515-525`; `services/audit.ts:29-67` (never throws); `:34-50` (delivery log swallows errors); `:169,340,403,441,505,548,629,644` (200); `:341-348,442-447,549-554,645-652` (claim released only on throw).
- What is happening: supabase-js returns errors instead of throwing; the handlers ACK success anyway and keep the 24h idempotency claim.
- Why it matters: during a DB degradation Stripe/Jira/JSM/M365 events are accepted and never retried or replayable; billing/ticket state drifts silently.
- Recommended fix: check each write's `{error}` and return 5xx (releasing the claim) on failure, or use one RPC per event.
- Suggested validation: regression test stubbing a failing write, asserting non-2xx and a released claim.
- Owner: integrations/backend · Target: this month · Note: new at 8d299b8d.

### Finding ID: pending - Worker queue degradation is invisible to health checks and alerting

- Severity: P2 · Confidence: high · Area: RES · Status: open
- Evidence: `health-server.ts:12-30` (200 unless shutting down); `docker-compose.yml:174-184`; `deploy-do.yml:835-858`; `prometheus.rules.yml` (no queue rule); `metrics.ts:103-118`; `producer.ts:114-118`; `webhook-retry.ts` runs in the worker.
- What is happening: a dead queue connection changes only the JSON status string; Docker, the deploy gate and Prometheus all stay green.
- Why it matters: Redis loss silently stalls email, webhook retries/DLQ, scans and retention; the first symptom is missing side effects.
- Recommended fix: queue-connectivity gauge + alert (and/or 503 from a readiness endpoint); chaos test stopping Redis.
- Owner: platform/backend · Target: this month · Note: new at 8d299b8d; cross-ref IR-P2-003.

### Finding ID: pending - Graceful shutdown is not effective in production: Redis handles are never closed and Docker's 10s stop timeout kills the worker before its 30s drain budget

- Severity: P2 · Confidence: high · Area: RES · Status: open
- Evidence: `shutdown.ts:13-18`; `consumer-bullmq.ts:56-67`; `scan-lock.ts:76-81` and `lib/idempotency.ts:119-124` (never called); `producer.ts:28-60` (never closed); no `process.exit(0)`; no `stop_grace_period` in any compose file.
- What is happening: Docker SIGKILLs at 10s; lingering Redis sockets would prevent a natural exit even after a completed drain.
- Why it matters: in-flight jobs are killed and redelivered (at-least-once) to non-idempotent handlers; a clean drain would be recorded as exit 1.
- Recommended fix: `stop_grace_period: 60s`; close scan-lock/idempotency/producer connections; `exit(0)` on clean drain.
- Suggested validation: SIGTERM mid-task integration test asserting clean exit and no duplicate side effect.
- Owner: platform/backend · Target: this month · Note: new at 8d299b8d; complements RES–P3-001.

### Finding ID: pending - Deploys are stop-the-world: `docker compose down` before `up` takes the whole stack offline with no rolling replace

- Severity: P2 · Confidence: high · Area: RES · Status: open
- Evidence: `deploy-do.yml:809-824,825-858`; `FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:82`.
- What is happening: every deploy/rollback stops all services before starting the new ones.
- Why it matters: a planned full outage on every release; a bad revision extends it until rollback completes.
- Recommended fix: pre-pull then per-service `up -d --no-deps` recreation, or document a maintenance window.
- Owner: platform/infrastructure · Target: this month · Note: new at 8d299b8d; cross-domain INFRA.

### Finding ID: pending - Manual rollback script points at the wrong GHCR namespace and accepts non-2xx health codes

- Severity: P3 · Confidence: high · Area: RES · Status: open
- Evidence: `rollback.sh:25` vs `deploy-do.yml:97`; `rollback.sh:48-51,63-67,70-72,42`.
- Why it matters: the incident-time fallback can pull from a nonexistent namespace and call a 500 a success.
- Recommended fix: share the prefix with the workflow; require 200; fatal worker check; pin host key.
- Owner: platform/backend · Target: this quarter · Note: new at 8d299b8d.

### Finding ID: pending - Circuit breaker leaks an uncleared timer per call and does not abort the timed-out operation

- Severity: P3 · Confidence: high · Area: RES · Status: open
- Evidence: `circuit-breaker.ts:73-80`; `services/supabase.ts:50-61,131-134`; breaker config at `circuit-breaker.ts:131-137`.
- Why it matters: every Supabase call leaves a 30s pending timer; timed-out work continues in the background.
- Recommended fix: clear the timer in `finally`; pass an AbortSignal so the timeout cancels.
- Owner: API platform · Target: this quarter · Note: new at 8d299b8d.

### Finding ID: pending - Service worker is shipped but never registered — offline capability is dead code

- Severity: P3 · Confidence: high · Area: RES · Status: open
- Evidence: `apps/web/public/sw.js`; no `serviceWorker.register` (grep); `app/layout.tsx:26`; `GAP_ANALYSIS.md:67`; `PLATFORM_FAILURE_RUNBOOKS.md:74`.
- Why it matters: dead asset creates false confidence; no offline UX exists.
- Recommended fix: register with a versioned strategy or delete and document.
- Owner: web platform · Target: next quarter · Note: new at 8d299b8d; may overlap domain 17.

### Finding ID: pending - Failure-injection and load tests exist but are never executed by CI

- Severity: P3 · Confidence: high · Area: RES · Status: open
- Evidence: `scripts/load-testing/*.js`; `scripts/load-testing/README.md:9-36`; no k6 reference in `.github/workflows`; no chaos suite.
- Why it matters: retry/breaker/DLQ/shutdown paths are only mock-tested; no exercised partial-outage evidence.
- Recommended fix: scheduled/manual k6 job + a small failure-injection suite; see Suggested Tests.
- Owner: platform/backend · Target: this quarter · Note: new at 8d299b8d.

### Finding ID: pending - `requestTimeout` responds 408 but does not abort the handler or close the connection

- Severity: P3 · Confidence: high · Area: RES · Status: open
- Evidence: `middleware/request-timeout.ts:3-19`; `app.ts:151`.
- Why it matters: a client can get 408 while the mutation commits, inviting duplicate retries (mitigated only when an Idempotency-Key is sent).
- Recommended fix: thread the deadline into handlers or destroy the socket; document that 408 is advisory.
- Owner: API platform · Target: next quarter · Note: new at 8d299b8d.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent async-plane stall (queue dead, health green) | P2 | Medium | Delayed/failed notifications, webhook DLQ, scans | Finding "queue degradation is invisible" | Queue gauge + alert; readiness 503 |
| Task stuck/never cancelled; no task DLQ | P2 | Medium | Unreplayable failed work; duplicate redelivery | RES–P2-002 | Handler timeout; task_dead_letters |
| In-flight jobs killed at deploy (10s SIGKILL) | P2 | High (every deploy) | Duplicate/lost side effects on non-idempotent tasks | Finding "graceful shutdown not effective" | stop_grace_period; close handles |
| Inbound provider events dropped during DB outage | P2 | Low-Medium | Billing/ticket drift; manual reconciliation | Finding "inbound webhooks ACK 200" | Fail on write error; release claim |
| Planned full outage per release | P2 | High | User-visible downtime each deploy/rollback | Finding "stop-the-world deploys" | Rolling recreate; maintenance window |
| Recovery never exercised (restore/PITR/watchdog) | P2 | Medium | RTO/RPO claims unproven at the worst moment | RES–P2-005/006; RTO_RPO.md:45-47 | Record drills; fix incident doc |
| Manual rollback path fails under pressure | P3 | Medium | Longer outage during incident | Finding "rollback script" | Fix prefix/health checks |
| Breaker timer leak / global scope | P3 | Medium | Event-loop churn; wide blast radius | Finding "circuit breaker timer" | Timer cleanup; per-integration breakers |

## Recommendations

### Immediate / Release Blocking

None. No P0/P1 findings in this domain at `8d299b8d`.

### This Week

1. Fix the inbound webhook write-error handling (return 5xx + release the claim) — smallest change with the highest correctness payoff.
2. Add the queue-connectivity gauge/alert and surface queue state in the worker health response (or a `/ready` endpoint).
3. Set `stop_grace_period: 60s` on worker/api and close the scan-lock/idempotency/producer connections during drain.
4. Correct `docs/INCIDENT_RESPONSE.md:124-128` so responders see the deployed dead-man's switch.

### This Month

5. Add the handler timeout (AbortSignal) + `task_dead_letters` + failed-task metric/alert (RES–P2-002).
6. Record one restore drill and one dead-man's-switch exercise in `docs/PLATFORM_FAILURE_RUNBOOKS.md` §5.
7. Replace the deploy `down`→`up` sequence with pre-pull + per-service recreate.
8. Fix `scripts/rollback.sh` (prefix, 200-only, fatal worker check) or retire it in favor of the workflow.
9. Update `AGENTS.md:328` and document `WORKER_SHUTDOWN_TIMEOUT_MS`.

### Later / Platform Evolution

10. Per-integration circuit breakers (Stripe/JSM/M365/SMTP) and breaker timer/cancellation hygiene.
11. Chaos/failure-injection suite + scheduled k6 load runs in CI.
12. Decide the offline/PWA stance (register a versioned service worker or delete `sw.js`).
13. Multi-replica-aware scan locking and rate limiting if the topology grows beyond one droplet.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `stop_grace_period: 60s` on worker/api | Aligns container stop budget with the 30s drain | `infra/digitalocean/docker-compose.yml` | `docker compose config`; SIGTERM test |
| Queue-connected gauge + alert rule | Makes silent stalls alertable | `apps/worker/src/metrics.ts`, `infra/digitalocean/prometheus.rules.yml` | `promtool check rules`; stop-Redis test |
| Fix `INCIDENT_RESPONSE.md` dead-man's-switch paragraph | Removes responder confusion | `docs/INCIDENT_RESPONSE.md` | `scripts/check-docs-links.mjs` |
| `AGENTS.md:328` wording | Stops misleading future agents | `AGENTS.md` | review |
| Check `{error}` on Stripe upserts | Prevents silent billing drift | `apps/api/src/routes/webhooks.ts` | unit test with failing write |
| Document `WORKER_SHUTDOWN_TIMEOUT_MS` | Operator visibility | `docs/ENVIRONMENT_VARIABLES.md` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Handler timeout + `task_dead_letters` + failed-job surface | P2 | platform/backend | M | None |
| Queue connectivity/backlog detection end-to-end | P2 | platform/backend | S-M | Metrics + rules |
| Shutdown completeness (handles closed, exit 0, grace period) | P2 | platform/backend | S-M | Compose change |
| Inbound webhook write-error handling | P2 | integrations/backend | S-M | None |
| Rolling deploy (pre-pull + per-service recreate) | P2 | platform/infrastructure | M | Deploy workflow |
| Drill program (restore, PITR, dead-man's switch, host restore) | P2 | platform lead + ops | M | Operator access |
| Manual rollback script repair/retire | P3 | platform/backend | S | None |
| Breaker timer/cancellation + per-integration breakers | P3 | API platform | S-M | None |
| Chaos + load test CI job | P3 | platform/backend | M | Dev environment |
| Offline stance (register vs delete SW) | P3 | web platform | M | Product decision |

## Suggested Tests

- **Unit**: handler exceeding `WORKER_TIMEOUT` is aborted; permanently failing task writes a `task_dead_letters` row; queue-connected gauge is 0 when the BullMQ connection errors; `CircuitBreaker.execute` clears its timer and aborts on timeout; `requestTimeout` marks the request aborted.
- **Integration**: stop Redis → worker `/ready` (or health) goes unhealthy and the queue alert fires; SIGTERM mid-task → clean exit 0, no duplicate side effect; inbound Stripe/Jira/JSM handler with a stubbed failing write → 5xx and released idempotency claim.
- **E2E/manual**: deploy with an intentionally unhealthy worker → gate fails and auto-revert runs; dead-man's-switch drill (stop alertmanager → external page within grace); restore drill per `PLATFORM_FAILURE_RUNBOOKS.md` §0/§5.
- **CI**: scheduled k6 smoke+spike run against dev; a `promtool test rules` job for the new queue rules.
- **Regression**: keep the RES–P2-003 inline-rejection tests; add a test that `docker compose config` contains a `stop_grace_period` ≥ `WORKER_SHUTDOWN_TIMEOUT_MS` default.

## Suggested Documentation Updates

- `docs/INCIDENT_RESPONSE.md:124-128` — replace the stale "no dead-man's switch" paragraph with the deployed mechanism and the drill procedure.
- `docs/PLATFORM_FAILURE_RUNBOOKS.md` §5 — record drills with date/operator/variant/result/evidence; add the PITR exercise.
- `docs/ENVIRONMENT_VARIABLES.md` — document `WORKER_SHUTDOWN_TIMEOUT_MS` and clarify `WORKER_TIMEOUT` as lock-only.
- `AGENTS.md:328` — worker consumer is BullMQ-first in production.
- `docs/RTO_RPO.md` — keep the "not yet proven" caveat until the PITR drill is recorded, then update with the artifact.
- `scripts/load-testing/README.md` — link the CI job once it exists.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` provisioned in prod and has it ever pinged? | The dead-man's switch is only real when the external endpoint exists | GitHub env secret presence + external service history |
| Has any restore/rollback been run in production since 9c0b88c? | RTO/RPO claims depend on exercised evidence | Dated drill record or workflow run artifact |
| Are any non-webhook handlers idempotent under at-least-once redelivery? | SIGKILL/redelivery can duplicate side effects | Per-handler review of `tasks/` |
| Is the queue depth metric ever scraped successfully (queue label present)? | The proposed alert depends on it | `worker_task_queue_depth` series in Prometheus |
| Does the operator accept stop-the-world deploys as policy? | Determines whether rolling deploy is required | Owner decision (INFRA/ops) |

## Appendix

### Failure mode inventory (summary)

| Failure | Detector today | Detector gap | Recovery path |
|---|---|---|---|
| Worker process crash | `MCTServiceDown` (up==0) | — | Docker restart `unless-stopped`; BullMQ redelivery |
| Redis/BullMQ loss on worker | none (health stays 200) | queue gauge/alert | Redis restart; BullMQ retries |
| Hung task | logs only | task timeout + DLQ | manual restart (job redelivered) |
| Generic task permanent failure | logs only | task DLQ | none (not replayable) |
| Webhook endpoint failure | metrics + DLQ rows | DLQ alert (IR-P2-003) | webhook-retry + admin re-drive |
| Supabase/DB outage | breaker metrics + `/health` 503 | no alert on `/health` from off-box | fail-fast + provider retries |
| SMTP outage | delivery metrics | no alert | task retries; skipped email metered |
| Inbound provider event during DB outage | none | write-error handling | none (ACK 200) |
| Total droplet/monitoring loss | external watchdog | exercise evidence | PLATFORM_FAILURE_RUNBOOKS §0 |
| Bad deploy | deploy health gate + rollback | downtime window | workflow rollback / manual |

### Critical path resilience matrix

| Critical path | Failure behavior | Verified control | Residual |
|---|---|---|---|
| Sign-in / API reads | 503 when Supabase unhealthy; breaker fail-fast | `health.ts:131-141`; breaker | breaker timer leak |
| Mutations (retry safety) | Idempotency-Key claim + replay; 408 advisory | `middleware/idempotency.ts` | no handler abort |
| Outbound webhooks | queued-first; retries + DLQ; idempotent | both dispatchers + retry task | DLQ alert absent |
| Queued email | 3 retries then `ok:false`; task retries | `email.ts` | no task DLQ |
| Scheduled scans | scan lock; staggered; queue fallback | `main.ts:47-159` | lock skipped when Redis down |
| Deploy/rollback | down→up→health; rollback on failure | `deploy-do.yml:809-858` | planned outage |
| Backup/restore | daily dump; weekly integrity test | `db-restore-test.yml` | no drill record |

### Recovery readiness

- Backup path: implemented and verified weekly by `db-restore-test.yml` (integrity, freshness, RLS) — **exercised by CI schedule** (last run not observable offline; workflow exists on the default branch).
- Restore/rollback by humans: documented (`ROLLBACK_PROCEDURES.md`), **not exercised** (drill table `_pending`).
- Dead-man's switch: implemented and deploy-enforced, **not exercised**.
- Single-host loss: documented (`PLATFORM_FAILURE_RUNBOOKS.md` §0), **not exercised**; droplet `prevent_destroy` per ROLLBACK §4.

### Chaos test plan (proposed)

1. **Queue outage**: `docker compose stop redis` → assert worker health/readiness reflects it, the queue alert fires within 5m, and no task is lost after restart (BullMQ waiting set intact).
2. **Worker kill mid-task**: SIGKILL the worker during a slow task → assert BullMQ redelivery, no duplicate side effect for idempotent handlers, and a visible DLQ/attempt record.
3. **DB degradation**: point the API at an unreachable Supabase URL → assert breaker opens, `/health` degrades, inbound webhook handlers return 5xx (after the fix) and providers retry.
4. **SMTP outage**: stop the SMTP host → assert email task retries, metric increments, and the failure is visible after the task DLQ exists.
5. **Deploy failure**: deploy an image that fails its healthcheck → assert auto-revert and bounded outage.
6. **Monitoring loss**: stop alertmanager → assert the external dead-man's switch pages within its grace period (record as the §5 drill).

## Findings

| ID | Severity | Title |
|---|---|---|
| RES-P2-001 | P2 | Worker process has no `unhandledRejection` handler |
| RES-P2-002 | P2 | `WORKER_TIMEOUT` is not a real task timeout; generic task failures have no DLQ |
| RES-P2-003 | P2 | `QUEUE_BACKEND` default `inline` diverges from production and can silently stall all queued work |
| RES-P2-004 | P2 | External `fetch` calls without `AbortController` in `public.ts` and `auth.ts` |
| RES-P2-005 | P2 | Availability detection lives inside the failed domain; no external dead-man's switch or alert delivery |
| RES-P2-006 | P2 | Backup/restore recovery is configured but not evidenced as exercised, and the restore test verifies only table counts |
| RES-P3-001 | P3 | Worker graceful shutdown has no force-exit fallback |
| RES-P3-002 | P3 | Worker queued webhook dispatcher inserts deliveries without an idempotency key |
| RES-P3-003 | P3 | `AGENTS.md` documents the worker consumer incorrectly and omits the queue backend divergence |
| RES-P3-004 | P3 | Deploy health gate treats worker unhealthiness as non-fatal |
| RES-P3-005 | P3 | Orphan cleanup lists at most 1000 objects per bucket and cannot verify the purge shrank anything |
| RES-P2-007 | P2 | Inbound webhook handlers ACK 200 while ignoring persistence errors, dropping events during DB degradation |
| RES-P2-008 | P2 | Worker queue degradation is invisible to health checks and alerting |
| RES-P2-009 | P2 | Graceful shutdown is not effective in production: Redis handles are never closed and Docker's 10s stop timeout kills the worker before its 30s drain budget |
| RES-P2-010 | P2 | Deploys are stop-the-world: `docker compose down` before `up` takes the whole stack offline with no rolling replace |
| RES-P3-006 | P3 | Manual rollback script points at the wrong GHCR namespace and accepts non-2xx health codes |
| RES-P3-007 | P3 | Circuit breaker leaks an uncleared timer per call and does not abort the timed-out operation |
| RES-P3-008 | P3 | Service worker is shipped but never registered — offline capability is dead code |
| RES-P3-009 | P3 | Failure-injection and load tests exist but are never executed by CI |
| RES-P3-010 | P3 | `requestTimeout` responds 408 but does not abort the handler or close the connection |
