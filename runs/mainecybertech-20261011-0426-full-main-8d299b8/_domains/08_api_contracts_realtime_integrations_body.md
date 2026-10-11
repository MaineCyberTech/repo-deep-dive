# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: mainecybertech-20261011-0426-full-main-8d299b8
- Repository: /tmp/opencode/mct-audit-target (MaineCyberTech/mainecybertech)
- Branch: main
- Commit SHA: 8d299b8d (merge PR #168; verified with `git log -1`)
- Generated at: 2026-10-11
- Auditor: subagent (prompt 08 pass, fresh read-only review + previous-register verification)
- Area code: API
- Output path: docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/08_api_contracts_realtime_integrations.md
- Scope limitations:
  - Read-only static review at 8d299b8d. No runtime, database, Redis, Stripe/Jira/JSM/M365 or production access.
  - `node` is not installed in this audit shell, so `scripts/openapi-audit.js`, Jest suites and `tsx` scripts were **not executed**; the OpenAPI audit was reproduced by a faithful Python port (recorded below) and the rest is static analysis.
  - Worker handlers `module-tasks`, `scheduled-notifications`, `retention`, `orphan-cleanup` were skimmed, not exhaustively read; Next.js server actions were reviewed at surface level (they proxy the SDK).
  - This report covers the API lens; webhook replay/idempotency depth lives in domain 27, authz/tenancy in 06/24/25.

## Scope

Reviewed at HEAD `8d299b8d`:

- Routing/middleware: `apps/api/src/app.ts`, all 62 top-level + 13 subdirectory route files under `apps/api/src/routes/**` (61 mounted routers), middleware `auth.ts`, `permissions.ts`, `org-access.ts`, `admin.ts`, `idempotency.ts`, `optimistic-locking.ts`, `rate-limit.ts`, `csrf.ts`, `error.ts`, `not-found.ts`, `request-id.ts`, `request-timeout.ts`, `cache.ts`, `security.ts`, `security-headers.ts`.
- Contracts: `apps/api/src/openapi/spec.ts|builder.ts|generate.ts|extract.ts`, `docs/openapi.yaml`, `scripts/openapi-audit.js`, `.github/actions/unit-tests/action.yml`, `scripts/check-docs-counts.mjs`, `docs/API_ERROR_HANDLING.md`, `docs/API_RATE_LIMITING.md`, `docs/API_VERSIONING.md`, `docs/API_ENDPOINT_INVENTORY.md`.
- SDK: `packages/sdk/src/client.ts` and the retry/idempotency tests.
- Realtime: `apps/api/src/routes/notifications.ts` (SSE), `apps/web/components/NotificationBell.tsx`, `apps/api/src/__tests__/notifications-sse-scope.test.ts`.
- Webhooks/integrations: `apps/api/src/routes/webhooks.ts` (Stripe/Jira/JSM/M365 inbound), `routes/webhook-management.ts`, `lib/webhook-dispatcher.ts`, `lib/webhook-signature.ts`, `lib/ssrf-guard.ts`, `lib/pinned-fetch.ts`, worker `tasks/{webhook-dispatcher,webhook-retry,jira-sync,jsm-sync,m365-calendar-sync,stripe-reconcile}.ts`, `consumer-bullmq.ts`, `task-registry.ts`, `schedule-config.ts`, `apps/api/src/lib/task-producer.ts`.
- Pagination/validation/idempotency: `lib/pagination.ts`, `lib/query.ts`, `lib/idempotency.ts`, `middleware/idempotency.ts`, `validators/*` (32 files), `lib/http-client.ts`, `lib/circuit-breaker.ts`.

Not reviewed in depth: RLS SQL, Terraform/infra, notification-email rendering, M365 hardening scan, server action bodies.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/app.ts` | source | Mount order + global middleware | 61 routers under `/api/v1`; global IP limiter skips `/api/v1/webhooks/`; idempotency/CSRF/timeout chain |
| `apps/api/src/types/index.ts` | source | Envelope contract | `{success,data}` / `{success,error:{code,message,status,details?}}`; no body request_id |
| `apps/api/src/middleware/error.ts`, `request-id.ts`, `not-found.ts` | source | Error normalization | AppError/ZodError mapped centrally; generic 5xx message; `X-Request-ID` header |
| `apps/api/src/middleware/permissions.ts`, `lib/permissions.ts` | source | `requirePermission(module,action)` | 209 call sites; per-org resolution with admin bypass |
| `apps/api/src/__tests__/route-authorization-guard.test.ts` | test | Static route-mount guard | Asserts requireAuth/requireOrgAccess only (not permission keys) |
| `apps/api/src/middleware/{rate-limit,csrf,idempotency,request-timeout}.ts` | source | Non-handler error shapes | Plain-string 429, non-enveloped 403/400/409/408 |
| `apps/api/src/lib/pagination.ts` | source | List pagination helper | `parsePagination`/`paginationMeta`/`applyPagination` have zero call sites; `LIST_HARD_CAP` arrays remain |
| `apps/api/src/openapi/*`, `docs/openapi.yaml` | source | Contract source + artifact | 418 path keys; no commit binding; `info.version` 1.0.0 |
| `scripts/openapi-audit.js`, `.github/actions/unit-tests/action.yml` | source/CI | Contract drift gate | Fails on MISSING, warns on EXTRA; wired into test.yml + validate.yml |
| `docs/API_ERROR_HANDLING.md` (rewritten `a61aadc0`) | docs | Published error contract | Now matches error.ts/types/request-id |
| `docs/API_RATE_LIMITING.md` | docs | Published limiter contract | Claims an enveloped `RATE_LIMITED` 429 that is not emitted |
| `packages/sdk/src/client.ts` + `__tests__/client-fetch.test.ts` | source/test | SDK retry + idempotency | One `Idempotency-Key` per logical unsafe call, reused across retries |
| `apps/api/src/routes/notifications.ts`, `apps/web/components/NotificationBell.tsx` | source | Realtime SSE server + client | Org/user scope + JWT revalidation on server; no client reconnect |
| `apps/api/src/routes/webhooks.ts`, `webhook-management.ts` | source | Inbound + outbound webhook API | Raw-body signature verification, timestamp window, atomic dedup, DLQ routes |
| `apps/api/src/lib/webhook-dispatcher.ts`, worker `tasks/webhook-dispatcher.ts` | source | Outbound delivery | Atomic per-endpoint claim, `Idempotency-Key`, release on failure |
| Worker `tasks/{jira-sync,jsm-sync,stripe-reconcile,m365-calendar-sync}.ts` | source | External integration syncs | jsm fixed+tested; jira/stripe still `ok:true` on errors; M365 duplicates events |
| `apps/worker/src/schedule-config.ts`, `tasks/index.ts` | source | Background delivery | stripe-reconcile daily; jira/jsm/m365 registered but not scheduled or enqueued |

## Verification Performed

Commands were run read-only against `/tmp/opencode/mct-audit-target` at `8d299b8d` (node absent; one ported script).

| # | Command / method | Observed result | Verdict |
|---|---|---|---|
| 1 | `git log -1 --format=%h` ; `git merge-base --is-ancestor <fix> HEAD` for 1a6a5712, a61aadc0, d5e0d5b7, 08ad3d4d, 14a2b301 | All five remediation commits are ancestors of HEAD | supported |
| 2 | `grep -r "requirePermission(" apps/api/src/routes \| wc -l` | 209 call sites; governance.ts:184 and client-onboarding-command-center.ts:136/153/176/197/244 guarded | API-P2-001 fix present |
| 3 | Python route-guard scan of mutating registrations | 34 mutating routes lack a route-level guard token; residual candidates manually reviewed (projects/ai/assets/findings/field-services/public) | residual confirmed |
| 4 | Read `apps/worker/src/tasks/jsm-sync.ts` + `__tests__/tasks/task-handlers.test.ts` | startAt pagination, 3-attempt retry on network/429/5xx, truncation/errors -> `ok:false`; two-page and retry tests | API-P2-002 jsm fix verified |
| 5 | Read `jira-sync.ts:206`, `stripe-reconcile.ts:146` | Both still `return { ok: true }` after `errors++` | residual confirmed |
| 6 | `grep -rn "422" apps/api/src --include=*.ts` (non-test) | Only a migration-number comment (`routes/store/campaigns.ts:132`); no 422 responses | API-P2-003 verified |
| 7 | Read `docs/API_ERROR_HANDLING.md` vs `error.ts`/`types`/`request-id.ts`; grep documented codes | Envelope, 400 VALIDATION, generic 5xx, X-Request-ID and code vocabulary all match the code | API-P2-003 verified |
| 8 | `grep -rn "Idempotency-Key" packages/sdk apps/api` + read `client-fetch.test.ts:120-180` | SDK mints one key outside the retry loop; test asserts same key across 3 attempts; GET sends none | API-P2-004 verified |
| 9 | Read both dispatchers + `webhook-dispatcher-idempotency.test.ts:117-160` | Atomic `claimIdempotencyKey` per endpoint, header sent, claim released on failure; 3 concurrent dispatches -> 1 POST | API-P2-005 verified |
| 10 | Read `rate-limit.ts`, `csrf.ts`, `idempotency.ts`, `request-timeout.ts`, `docs/API_RATE_LIMITING.md:44-55` | Limiter/CSRF/idempotency/timeout bodies are not the envelope; doc claims an enveloped 429 | API-P3-001 residual confirmed |
| 11 | Python port of `scripts/openapi-audit.js` (regexes preserved) | 440 statically parsed live routes; 0 MISSING; 257 dynamic/unresolved EXTRA; RESULT: PASS | API-P3-002 gate works; binding still absent |
| 12 | `grep -c '^  "/' docs/openapi.yaml` vs `docs/INDEX.md:210` vs `AGENTS.md:589` | 418 vs 418 vs 412 — AGENTS.md stale (unchecked by check-docs-counts.mjs) | residual confirmed |
| 13 | `grep -rn "auth_expired" apps/web` | No client listener; server emits it (`notifications.ts:74-105`) | API-P3-003 still-open |
| 14 | `grep -rn "enqueueTask(" apps/api apps/web` and `"jsm-sync"` | Only webhook-dispatcher, notification-email, webhook-retry enqueue; no jira/jsm/m365 dispatch path | new finding confirmed |
| 15 | Read `routes/search.ts:74-97/153-173` + `search-tenant-scope.test.ts:136/214` | Queries scope to `req.orgScope` and substitute `["__none__"]` on empty scope; tests assert fail-closed | API-P2-006 verified-fixed |
| 16 | Read `routes/docs.ts:25-39` + `docs.test.ts:67-68` | Both `/openapi.json` and `/docs` 404 in production (SRI + CSP nonce wired) | API-P2-007 verified-fixed |
| 17 | Read `app.ts:154-171` + `config/env.ts:63` | `/metrics` gated by `authorizeInternalRequest(req, METRICS_TOKEN)`; 404 without token | API-P3-004 verified-fixed |

## Executive Summary

The API contract surface remains the strongest part of the platform, and the four reconciled P2 fixes are real at this commit: the SDK now sends a stable `Idempotency-Key` on unsafe requests (API-P2-004), both outbound webhook dispatchers claim deliveries atomically (API-P2-005), the published error contract matches the implementation (API-P2-003), and `jsm-sync` paginates, retries transient HTTP failures and fails the run on dropped records with tests (API-P2-002, jsm half). The OpenAPI coverage gate now fails CI on implemented-but-undocumented routes and passes with 0 missing.

What remains is boundary completeness and operational truthfulness, not headline architecture:

1. **Permission coverage is still uneven** (API-P2-001, partially-fixed): governance and client-onboarding are now guarded, but project comments/updates/task-approve, AI reply drafts, asset/finding comments and field-services calculations still run with auth + org access only, and the static route guard tests mounts, not permissions.
2. **Two of four integration syncs still lie about failure** (API-P2-002 residual): `jira-sync` and the daily `stripe-reconcile` return `ok:true` after counting per-item errors.
3. **Middleware error shapes bypass the envelope** (API-P3-001, partially-fixed): the per-user 429 is plain text, CSRF 403 / idempotency 400-409 / timeout 408 are hand-rolled, and `docs/API_RATE_LIMITING.md` documents a JSON 429 that is never emitted.
4. **The generated contract is unbound** (API-P3-002, partially-fixed): `docs/openapi.yaml` records no commit, EXTRA spec entries only warn, and AGENTS.md still says 412 paths (actual 418).
5. **Realtime client resilience is unchanged** (API-P3-003, still-open): no reconnect, no `auth_expired` handling, polling interval leaks on unmount.
6. **New operational gaps**: the Jira/JSM/M365 batch syncs are registered but never dispatched despite docs calling them periodic; the M365 calendar sync duplicates events on every run; and the M365 inbound webhook drops every batched notification after the first.

Overall domain score: **4/5** — production-ready with tests/docs/observability, but not "continuously validated" because permission coverage, integration failure reporting and contract binding remain incomplete.

## Inventory

### API inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Routers mounted | `apps/api/src/app.ts` | 61 routers under `/api/v1` | Implemented | Low | Global IP limiter skips `/health`, loopback and `/api/v1/webhooks/` |
| Route files | `apps/api/src/routes/**` (75 non-test) | Endpoints | Implemented | Medium | 274 mutating registrations; 209 `requirePermission` sites |
| Validators | `apps/api/src/validators/*.ts` (32) | Zod request schemas | Implemented | Low | Handlers call `.parse`; ZodError normalized centrally |
| Envelope | `types/index.ts` `success()`/`failure()` | Response contract | Implemented | Low | 204 deletes carry no body |
| Central error handler | `middleware/error.ts` | AppError/ZodError mapping | Implemented | Low | Generic 5xx client message; logs real message |
| Idempotency | `middleware/idempotency.ts` + `lib/idempotency.ts` | Atomic claim + replay | Implemented | Low | Owner+method+route scoped; `X-Idempotent-Replay` |
| Permissions | `middleware/permissions.ts` | `requirePermission` | Implemented | Medium | Residual unguarded mutations (API-P2-001) |
| Rate limiting | `middleware/rate-limit.ts`, `app.ts` | IP/user/auth/email/metrics | Implemented | Low | Per-user 429 non-enveloped; auth keyed on unverified email |
| Request timeout | `middleware/request-timeout.ts` | 30s guard | Implemented | Low | Non-enveloped 408; SSE unaffected (headers already sent) |
| Pagination | `lib/pagination.ts`, `lib/query.ts` | page/limit helpers | Partially adopted | Low | `parsePagination` unused; `LIST_HARD_CAP` raw arrays remain |
| OpenAPI runtime | `routes/docs.ts` | `/openapi.json` + Swagger UI | Implemented | Low | 404 in production; SRI-pinned UI assets |
| OpenAPI artifact | `docs/openapi.yaml` | Offline contract | Implemented, unbound | Low | 418 paths; no commit/date |
| OpenAPI gate | `scripts/openapi-audit.js` + unit-tests action | Drift gate | Implemented | Low | MISSING fails; EXTRA warns only |

### Realtime inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| SSE stream | `routes/notifications.ts` `GET /stream` | Live notifications | Implemented | Low | Cookie JWT revalidation every 5 min; 30s keepalives |
| SSE scope assertion | `notificationInScope()` | Org/user row filtering | Implemented + tested | Low | Rows without matching user/org are dropped |
| Supabase channel | per-user `postgres_changes` | INSERT/UPDATE fan-out | Implemented | Low | Cleanup on `req.on("close")` |
| Realtime client | `apps/web/components/NotificationBell.tsx` | EventSource consumer | Implemented | Medium | One-shot polling fallback; no reconnect/auth_expired |
| Realtime tests | `__tests__/notifications-sse-scope.test.ts` | Scope assertions | Implemented | Low | No reconnect test exists |

### Integration inventory

| Item | Path / symbol | Direction | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Stripe inbound | `routes/webhooks.ts:131` | Inbound | Implemented | Low | Signature + `event.id` atomic dedup; claim released on failure |
| Jira inbound | `routes/webhooks.ts:351` | Inbound | Implemented | Low | Raw-body HMAC + timestamp window + body-digest dedup |
| JSM inbound | `routes/webhooks.ts:453` | Inbound | Implemented | Low | Same pattern as Jira |
| M365 inbound | `routes/webhooks.ts:560/570` | Inbound | Implemented | Medium | clientState timing-safe; only `value[0]` processed |
| Outbound dispatcher | `lib/webhook-dispatcher.ts` + worker twin | Outbound | Implemented | Low | Queue-first, atomic claim, HMAC, SSRF-pinned fetch, DLQ |
| Retry task | worker `tasks/webhook-retry.ts` | Outbound retry | Implemented | Low | 5 attempts, exponential backoff, DLQ rows, Idempotency-Key preserved |
| JSM batch sync | worker `tasks/jsm-sync.ts` | Pull | Fixed + tested | Low | Pagination, retry, fail on errors/truncation; no dispatcher |
| Jira batch sync | worker `tasks/jira-sync.ts` | Pull | Partial reporting | Medium | `ok:true` on errors; no dispatcher |
| Stripe reconcile | worker `tasks/stripe-reconcile.ts` | Pull | Partial reporting | Medium | Scheduled daily; `ok:true` on errors |
| M365 calendar sync | worker `tasks/m365-calendar-sync.ts` | Push | Duplicates on rerun | Medium | No event dedup/idempotency; no dispatcher |
| Task queue | `lib/task-producer.ts`, worker `consumer-bullmq.ts` | Background | Implemented | Low | BullMQ attempts=3, failed set only (no queue DLQ/alert) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| REST/RPC routes | 4 | 61 routers, consistent envelope, 209 permission sites, mount-guard test | Residual unguarded mutations (projects/ai/assets/findings/field-services) | Extend guards + permission-level guard test |
| Server actions | 3 | 60 `"use server"` files proxy the SDK; ~10 action test files | No action↔route contract coverage; no server-action validation | Add thin contract tests for high-value actions |
| WebSocket/realtime | 4 | SSE + org/user scope assertion + 5-min JWT revalidation + tests | Client never reconnects; auth_expired undocumented | Client reconnect/backoff + docs |
| Subscriptions/events | 4 | Per-user `postgres_changes`, sanitized payloads, MT-P2-004 scope test | No documented disconnect/reconnect contract | Document + test reconnect semantics |
| Webhooks | 4 | 4 providers verified, atomic outbound claim, DLQ + retry, SSRF-pinned fetch | M365 batch drops; queue-level failures have no DLQ/alert | Process all M365 notifications; alert on failed jobs |
| External clients | 3 | `http-client` retry/breaker; jsm-sync fixed; m365 reporting fixed | jira/stripe report success on errors; no dispatcher for batch syncs | Fix result contracts; add dispatch path |
| Retries/timeouts/circuit breakers | 4 | SDK key+retry, `HttpClient` 429/5xx retry + breaker, 30s timeout, AbortSignal in workers | SDK retries non-JSON 429 as an opaque parse error | Envelope limiter 429 |
| Pagination/filter/sort | 3 | `{items,total,page,limit}` on most lists; `LIST_HARD_CAP` | Helper unused; raw capped arrays; no sort-param validation | Adopt helper or delete; validate sort |
| Error response format | 4 | Central handler, generic 5xx, doc now accurate, X-Request-ID | Middleware-level 429/403/400/409/408 non-enveloped | Envelope middleware errors |
| OpenAPI/versioning | 4 | Generated spec + fail-closed runtime docs + CI coverage gate | No commit binding; EXTRA warn-only; stale AGENTS.md count | Bind artifact; tighten audit |
| Request/response validation | 4 | Zod across mutations; 14 routes with responseSchema + contract tests | No SDK runtime response validation; legacy thin routes | Extend responseSchema/tests |
| Auth/rate limit | 4 | Multi-layer limiters, CSRF, JWT fast path, API keys, permissions | Guard gaps; limiter output shape; email-keyed auth limiter | Close gaps; envelope output |

## Detailed Review

### Item: REST/RPC routes and validation

- Evidence: `app.ts:82-238`; 274 mutating registrations; `validators/*` (32 files); 209 `requirePermission` sites.
- What it does: All routers mount under `/api/v1`, mutate through Zod-validated handlers, and most module mutations pass through `requirePermission`. A static test (`route-authorization-guard.test.ts`) enforces auth/org mounts.
- Missing controls: Permission keys are not enforced by that test, and a residual set of mutations only has auth + org access (see API-P2-001). Public surfaces (`/analytics/track`, `/store/quotes`, `/public/submit`) are on the global IP limiter only.
- Risks: A view-only role can still write on the residual modules.

### Item: Error envelope and middleware errors

- Evidence: `types/index.ts:1-38`, `middleware/error.ts:20-51`, `middleware/not-found.ts`, `middleware/rate-limit.ts:27-40`, `middleware/csrf.ts:84-88`, `middleware/idempotency.ts:30/69-72`, `middleware/request-timeout.ts:7-12`.
- What it does: Thrown AppErrors and ZodErrors are normalized centrally; 5xx messages are genericized; 404s use the envelope; every response carries `X-Request-ID`.
- Missing controls: Errors produced by middleware (not the central handler) are not enveloped: per-user 429 is a plain string, CSRF 403, idempotency 400/409 and timeout 408 are ad-hoc `{error: ...}` shapes. `docs/API_RATE_LIMITING.md:44-55` documents an enveloped `RATE_LIMITED` 429 that no limiter emits.
- Risks: The SDK's `res.json()` parse of a text 429 throws and is retried as an opaque error; clients cannot switch on a stable limiter code.

### Item: OpenAPI contract and CI gate

- Evidence: `openapi/spec.ts` (697 method entries), `generate.ts:1-60`, `docs/openapi.yaml` (418 paths, 16,588 lines), `scripts/openapi-audit.js:121-126`, `.github/actions/unit-tests/action.yml:29-34`.
- What it does: `buildSpec()` is served at runtime (404 in production) and materialized to `docs/openapi.yaml`; CI validates the spec and fails when a statically-resolvable route is missing. The ported audit at HEAD reports 440 live routes, 0 missing, 257 dynamic/unresolved entries — PASS.
- Missing controls: No commit/date binding in the generated artifact; EXTRA entries only warn; `AGENTS.md:589` still claims 412 paths; response schemas cover 14 routes and the error schema is not modeled.
- Risks: The artifact cannot be traced to a revision; phantom spec entries can persist; doc counts drift unchecked.

### Item: Idempotency (requests, webhooks, SDK)

- Evidence: `middleware/idempotency.ts:24-105`, `lib/idempotency.ts:99-185`, `routes/webhooks.ts:53-63/167-172`, `lib/webhook-dispatcher.ts:140/178-180/230`, worker `tasks/webhook-dispatcher.ts:80-100`, `packages/sdk/src/client.ts:176-178/296`.
- What it does: Request keys are atomically claimed, owner+route scoped, replayed on success, released on failure; inbound webhooks dedupe on provider keys; outbound dispatchers claim per endpoint; the SDK now mints one key per logical unsafe call.
- Missing controls: The in-memory fallback is per-process (single instance today); `lib/idempotency.ts:9-18` mutex chain releases the next waiter before the critical section finishes, which is acceptable for tiny map operations but not a general mutex.
- Risks: Low in the current single-instance topology; the fallback weakens if scaled out.

### Item: Realtime SSE

- Evidence: `routes/notifications.ts:30-173`, `apps/web/components/NotificationBell.tsx:81-119`, `__tests__/notifications-sse-scope.test.ts:16-38`.
- What it does: The stream authenticates via cookie/Bearer, re-validates the JWT every 5 minutes against all configured secrets, asserts user+org scope per row, sanitizes payloads, and sends keepalives; tests cover the scope assertion.
- Missing controls: The client closes the EventSource on any error and degrades to a one-shot 30s poll of the unread count only (no reconnect, no recent-list refresh), ignores the server's `auth_expired` event, and never clears the fallback interval on unmount; no disconnect/reconnect contract is documented.
- Risks: Up to 30s notification latency after any drop; interval leak; no user signal to re-authenticate.

### Item: External integrations and background delivery

- Evidence: worker `tasks/{jsm-sync,jira-sync,stripe-reconcile,m365-calendar-sync}.ts`, `schedule-config.ts:27-60`, `tasks/index.ts:35-37`, `lib/task-producer.ts`, `consumer-bullmq.ts`, `tasks/webhook-retry.ts`.
- What it does: Outbound HTTP has timeouts/retries/breaker; webhook delivery has a queue-first path with inline fallback, atomic dedup, retry task and DLQ; stripe-reconcile is scheduled daily; jsm-sync now paginates, retries and fails honestly.
- Missing controls: `jira-sync` and `stripe-reconcile` still return `ok:true` after per-item errors; `jira-sync` retries only 429 (not 5xx); jira/jsm/m365 syncs have no scheduler or enqueue path although docs describe them as periodic; M365 calendar sync duplicates events on re-run; the M365 webhook processes only the first batched notification; BullMQ failures land in the failed set with only logs (no queue DLQ/alert).
- Risks: Silent staleness in billing/Jira reconciliation; duplicate reminders; lost M365 events; dormant batch import.

### Item: SDK client

- Evidence: `packages/sdk/src/client.ts:20-140/149-303`, `__tests__/client-fetch.test.ts`.
- What it does: 30s timeout, 3 retries with exponential backoff on 429/502/503/504 and network/abort errors, stable `Idempotency-Key` on unsafe methods, CSRF and `X-Active-Org` headers, structured `ApiError`.
- Missing controls: `executeFetch` parses JSON before checking status, so a non-JSON 429 body throws a SyntaxError that is retried as a generic error; no runtime response validation.
- Risks: Opaque rate-limit errors; duplicate retries of a non-JSON 429.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| API-001 | REST/RPC routes | `app.ts`, route files | Envelope + Zod + 209 permission sites | Residual unguarded mutations | P2 | Close guards; permission-level guard test |
| API-002 | Server actions | 60 `"use server"` files | Proxy SDK calls | No action↔route contract tests | P3 | Thin contract tests |
| API-003 | WebSocket/realtime | `notifications.ts` | SSE + scope assertion + JWT revalidation | Client no reconnect/auth_expired | P3 | Reconnect + backoff + docs |
| API-004 | Subscriptions/events | Supabase channel | Per-user filter + org assertion | No disconnect contract | P3 | Document + test |
| API-005 | Webhooks | `webhooks.ts`, dispatchers | Sig verify + atomic dedup + DLQ + SSRF | M365 batch drop; queue DLQ absent | P3 | Process all notifications; alert failed jobs |
| API-006 | External clients | `http-client.ts`, worker tasks | Timeout/retry/breaker | jira/stripe `ok:true`; no dispatcher | P2 | Fix result contracts; add dispatch path |
| API-007 | Retries/timeouts/breakers | SDK + `http-client.ts` | Retry 429/5xx + breaker + 30s | Non-JSON 429 retried opaquely | P3 | Envelope limiter output |
| API-008 | Pagination/filter/sort | `pagination.ts`, list routes | `{items,total,page,limit}` mostly | Helper unused; raw arrays; sort unvalidated | P3 | Adopt/delete helper; validate sort |
| API-009 | Error response format | `error.ts`, middleware | Normalized envelope | Middleware errors non-enveloped | P3 | Envelope 429/403/400/409/408 |
| API-010 | OpenAPI/versioning | spec + audit + yaml | Generated spec + failing coverage gate | No commit binding; EXTRA warn-only | P3 | Bind artifact; allowlist EXTRA |
| API-011 | Request/response validation | Zod validators | Broad on mutations | 14 response schemas; no SDK validation | P3 | Extend schemas/tests |
| API-012 | Auth/rate limit | auth/rate-limit/permissions | Multi-layer | Guard gaps; limiter output shape | P2 | Close gaps; envelope output |

## Findings

Full detail is in the companion `08_api_contracts_realtime_integrations.json`. Titles and status at 8d299b8d:

| # | Title | Severity | Status | Confidence |
|---|---|---|---|---|
| 1 | Mutations remain unguarded by `requirePermission` in several routers (including a governance state transition) | P2 | partially-fixed | high |
| 2 | External integration syncs report success while dropping items, and `jsm-sync` has no HTTP retry | P2 | partially-fixed | high |
| 3 | Published error-handling contract contradicts the implementation (codes, 422, and `request_id`) | P2 | verified-fixed | high |
| 4 | SDK retries unsafe requests without an `Idempotency-Key` (duplicate creates on transient failure) | P2 | verified-fixed | high |
| 5 | Outbound webhook dispatcher uses a non-atomic idempotency check (duplicate deliveries under concurrency) | P2 | verified-fixed | high |
| 6 | Minor contract inconsistencies (`rateLimitByUser` non-enveloped 429, capped raw-array lists, no `request_id`) | P3 | partially-fixed | high |
| 7 | OpenAPI artifact is not bound to a commit and the CI audit warns (not fails) on documented-but-missing routes | P3 | partially-fixed | high |
| 8 | Realtime client has no reconnect path; server emits `auth_expired` with no documented client handling | P3 | still-open | high |
| 9 | Batch Jira/JSM/M365 sync tasks are registered but never dispatched (no scheduler or enqueue path) | P3 | open (new) | high |
| 10 | M365 calendar sync recreates a calendar event for every task on each run (duplicate events, no idempotency) | P3 | open (new) | high |
| 11 | M365 inbound webhook acknowledges but only processes the first notification of a batch | P3 | open (new) | high |
| 12 | Search falls through to an unscoped cross-tenant query | P2 | verified-fixed | high |
| 13 | OpenAPI schema is public and the Swagger UI is blocked by CSP | P2 | verified-fixed | high |
| 14 | `/metrics` is fully public when `METRICS_TOKEN` is unset | P3 | verified-fixed | high |

The last three rows are the `@owner | API` ledger findings from the previous register (`API-P2-006`, `API-P2-007`, `API-P3-004`); all three were re-verified directly at 8d299b8d (search scope fail-closed, production docs 404, token-gated metrics).

### Finding detail: API-P2-001 (partially-fixed)

- What changed: `governance.ts:184` now guards `POST /change-requests/:id/submit` with `requirePermission("governance","edit")`; all five client-onboarding mutations are guarded (`client-onboarding-command-center.ts:136/153/176/197/244`); commit `14a2b301`.
- Residual: `projects.ts:845/910/947/1196/1228` (task comments, updates, task approve, portal comment), `ai.ts:357`, `assets.ts:359`, `findings.ts:456`, `field-services.ts:266` have auth+org only; `route-authorization-guard.test.ts` checks mounts, not permission keys; public surfaces have no dedicated limiter.
- Recommended fix: extend guards or add documented exceptions; extend the guard test to assert permission keys; add a limiter for `/analytics/track`.
- Validation: per-router tests asserting a role without `module:action` receives 403 on each residual mutation.

### Finding detail: API-P2-002 (partially-fixed)

- What changed: `jsm-sync.ts:29-62/114-134/227-234` paginates (`startAt`, `MAX_PAGES=20`), retries network/429/5xx 3 times, and fails the run on truncation or any per-item error; tests at `task-handlers.test.ts:106-160`; commit `1a6a5712` / PR #150.
- Residual: `jira-sync.ts:206` and `stripe-reconcile.ts:146` return `{ok:true}` after `errors++`; `fetchJiraIssue` retries only 429; `stripe-reconcile` runs daily (`schedule-config.ts:29-33`).
- Recommended fix: return `{ok:false}` (or a partial result) when `errors > 0`; retry 5xx in `fetchJiraIssue`; add failure-injection tests.
- Validation: mock one failing per-item write and assert the task result is not `ok`.

### Finding detail: API-P3-001 (partially-fixed)

- Fixed: `X-Request-ID` header on every response (`request-id.ts:22`).
- Residual: plain-string 429 (`rate-limit.ts:30`), ad-hoc 403/400/409/408 bodies, doc claiming an enveloped `RATE_LIMITED` 429 (`docs/API_RATE_LIMITING.md:44-55`), unused pagination helper (`lib/pagination.ts:28/42/52`) and capped raw arrays (`store/quotes.ts:192`).
- Recommended fix: envelope every middleware error via `failure(...)`; align the rate-limiting doc; adopt or delete `lib/pagination.ts` and convert raw arrays.

### Finding detail: API-P3-002 (partially-fixed)

- Fixed: the coverage gate fails on missing routes and is wired into `test.yml`/`validate.yml` via the shared unit-tests action; ported audit at HEAD = 0 missing.
- Residual: no commit/date in `docs/openapi.yaml:1-4`; EXTRA warn-only (`openapi-audit.js:117-119`); `AGENTS.md:589` says 412 paths vs 418 actual.
- Recommended fix: embed `GIT_SHA` + date in the generated header; allowlist-and-fail on EXTRA; update AGENTS.md and the docs-count guard.

### Finding detail: API-P3-003 (still-open)

- Server: `notifications.ts:74-105` emits `auth_expired` and ends the stream.
- Client: `NotificationBell.tsx:108-113` closes and starts a one-shot poll; `:115-118` cleanup closes only the EventSource; no `auth_expired` listener anywhere in `apps/web`.
- Recommended fix: reconnect with bounded backoff, handle `auth_expired` (redirect to login), clear the fallback interval in the effect cleanup, document the contract.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Residual unguarded mutations bypass RBAC | P2 | Medium | Medium | `projects.ts:845-1228`, `ai.ts:357`, `assets.ts:359` | Extend guards + tests |
| Silent partial sync (Jira/Stripe) | P2 | Medium | High | `jira-sync.ts:206`, `stripe-reconcile.ts:146` | Fail on errors |
| Batch integrations never run | P2 | Medium | Medium | `schedule-config.ts:57-60`, no enqueue site | Add dispatch path + docs |
| Limiter/middleware errors unparseable by SDK | P3 | Certain | Low | `rate-limit.ts:30`, SDK `client.ts:96` | Envelope middleware errors |
| Duplicate M365 calendar events | P3 | Medium | Medium | `m365-calendar-sync.ts:79-112` | Event id persistence / transactionId |
| M365 batched notifications dropped | P3 | Medium | Low | `webhooks.ts:612-644` | Iterate `value[]` |
| Realtime degrades to polling silently | P3 | Medium | Low | `NotificationBell.tsx:108-113` | Reconnect + docs |
| Contract artifact untraceable | P3 | Medium | Low | `docs/openapi.yaml:1-4` | Commit binding |

## Recommendations

### Immediate / Release Blocking

None. No P0/P1 findings remain open at this commit.

### This Week

1. API-P2-001: guard or explicitly allowlist the residual mutating routes; extend `route-authorization-guard.test.ts` to permission keys.
2. API-P2-002: make `jira-sync` and `stripe-reconcile` return failure on per-item errors; retry 5xx in `fetchJiraIssue`.
3. API-P3-003: add `auth_expired` handling and bounded SSE reconnect; fix the polling-interval cleanup.

### This Month

4. API-P3-001: envelope the per-user 429, CSRF 403, idempotency 400/409 and timeout 408; align `docs/API_RATE_LIMITING.md`.
5. API-P3-002: bind `docs/openapi.yaml` to the generating commit; fail or allowlist EXTRA entries; fix `AGENTS.md:589`.
6. New findings: add a dispatch path (schedule or admin trigger) for the batch syncs; dedupe M365 calendar events; iterate M365 webhook batches.
7. Add alerting on BullMQ `failed` jobs (queue-level DLQ visibility).

### Later / Platform Evolution

8. Adopt or delete `lib/pagination.ts`; add sort-parameter validation and cursor pagination where lists are large.
9. Extend response schemas and contract tests to the highest-traffic routes; consider SDK runtime response validation for critical modules.
10. Document the realtime disconnect/reconnect and rate-limit contracts for operators and agents.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `failure("RATE_LIMIT", ..., 429)` from all limiters | SDK parses 429 as `ApiError` | `middleware/rate-limit.ts` | Limiter test asserting envelope |
| `errors > 0 -> ok:false` in jira/stripe | Removes silent partial success | `tasks/jira-sync.ts`, `tasks/stripe-reconcile.ts` | Failure-injection unit tests |
| Iterate M365 `value[]` | Stops dropping batched events | `routes/webhooks.ts` | Multi-notification test |
| Clear polling interval in effect cleanup | Stops interval leak | `NotificationBell.tsx` | Component unmount test |
| Embed commit in openapi header | Traceable artifact | `openapi/generate.ts`, `docs/openapi.yaml` | CI header assertion |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Permission-level route guard test + residual guards | P2 | API principal engineer | S | permission catalog keys |
| Integration result contract (`ok:false` on partial) | P2 | Worker engineer | S | none |
| Batch sync dispatch (schedule or admin trigger) | P2 | Worker/API engineer | M | per-tenant payloads |
| Envelope all middleware errors | P3 | Implementation agent | S | none |
| OpenAPI commit binding + EXTRA allowlist | P3 | Implementation agent | M | GIT_SHA in CI |
| SSE reconnect/backoff + docs | P3 | Web + API engineers | S | none |
| M365 calendar event dedup | P3 | Worker engineer | M | Graph event id storage |
| BullMQ failed-job alerting | P3 | Platform engineer | S | metrics/alert rules |
| Pagination helper adoption or removal | P3 | API engineer | M | route-by-route conversion |

## Suggested Tests

- Unit: limiter 429 body parses as the standard envelope; CSRF/idempotency/timeout bodies match `failure()`.
- Unit: `jira-sync`/`stripe-reconcile` return `ok:false` when one per-item write fails; `fetchJiraIssue` retries 5xx.
- Unit: M365 webhook with two `value` entries audits/dedupes both.
- Integration: M365 calendar sync run twice produces no duplicate events.
- Integration/regression: SSE component test simulating `onerror` and `auth_expired` asserts reconnect and login redirect; interval cleared on unmount.
- Contract: permission-level guard test enumerating mutating routes and asserting `requirePermission` or a documented allowlist entry.
- CI: generated `docs/openapi.yaml` header contains the current commit; EXTRA entries must be in the allowlist.
- Security: authenticated 429 through the SDK surfaces `ApiError` with `RATE_LIMIT`, not a parse error.

## Suggested Documentation Updates

- `docs/API_RATE_LIMITING.md` — correct the 429 body claim; document auth/email/metrics limiters and their shapes.
- `docs/JIRA_JSM_INTEGRATION.md` — state the actual dispatch model for batch syncs (and update once a scheduler/trigger exists).
- `docs/openapi.yaml` header — commit + date binding (generator change).
- `AGENTS.md:589` — 412 → 418 paths (and extend `check-docs-counts.mjs` to guard it).
- New `docs/REALTIME.md` (or a section in `docs/API_ENDPOINT_INVENTORY.md`) — SSE events (`connected`, `initial`, `notification`, `notification_update`, `auth_expired`), reconnect semantics and polling fallback.
- `docs/API_ERROR_HANDLING.md` — add the middleware-level error shapes once enveloped.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Who is expected to enqueue jira-sync/jsm-sync/m365-calendar-sync? | Determines whether batch reconciliation is dormant or operator-run | Ops runbook or queue-dispatch evidence |
| Should the residual project comment/update routes be permission-gated or are they intentionally member-writable? | Determines API-P2-001 closure | Product/role intent for `projects:edit` |
| Is BullMQ's failed set monitored/alerts configured? | Determines queue-level DLQ risk | Alert rules referencing worker failure metrics |
| Is M365 webhook batching expected in this tenant? | Sets the urgency of the batch-drop fix | Graph subscription/batch evidence |
| Is `docs/openapi.yaml` expected to be regenerated per commit or per release? | Determines the binding mechanism | Release/CI policy |

## Appendix

- Companion JSON: `_domains/08_api_contracts_realtime_integrations.json` (14 findings: P2 x7, P3 x7; verified-fixed 6, partially-fixed 4, still-open 1, open 3).
- OpenAPI audit reproduction: `node` is absent in this shell, so the regex logic of `scripts/openapi-audit.js` was ported to Python (same import/mount/route/spec regexes) and run read-only. Result at `8d299b8d`: `Live routes parsed: 440`, `Spec route entries: 697`, `MISSING from spec (0)`, `Dynamic/unresolved spec entries (257)`, `RESULT: PASS`.
- Route-guard scan reproduction: a Python scan of mutating registrations found 34 routes without a route-level guard token; each was manually classified (self-scoped, public-by-design, signature-verified, or residual — see API-P2-001).
- Counts: 61 mounted routers; 75 non-test route files; 274 mutating registrations; 32 validator files; 133 API test files; 209 `requirePermission` call sites; 418 OpenAPI path keys.
- Provenance: previous-run rows re-verified: API-P2-001 (open→partially-fixed), API-P2-002 (verified-fixed→partially-fixed residual), API-P2-003/004/005 (verified-fixed→verified-fixed), API-P2-006/007 and API-P3-004 (verified-fixed→verified-fixed, ledger a97425d carried), API-P3-001 (open→partially-fixed), API-P3-002 (open→partially-fixed), API-P3-003 (open→still-open).
