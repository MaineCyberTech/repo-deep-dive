# 27_webhook_delivery_replay_idempotency_audit — Prompt 27 - Webhook Delivery, Replay, and Idempotency Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `27_webhook_delivery_replay_idempotency_audit.md` (area WH, prompt)

## Verification Performed

# Webhook Delivery, Replay, and Idempotency Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (target worktree `/tmp/opencode/mct-audit-target`, read-only)
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11
- Auditor: domain subagent (area WH, prompt `27_webhook_delivery_replay_idempotency_audit.md`)
- Area code: WH
- Output paths: `_domains/27_webhook_delivery_replay_idempotency_audit.json`, `_domains/27_webhook_delivery_replay_idempotency_audit_body.md`
- Scope limitations: repository-only review (no running API/worker/Redis/Supabase, no provider traffic). Every claim is from source/config/migrations/tests at `8d299b8d`. No lab access used (not required for this domain).

## Scope

Reviewed at `8d299b8d`:

- Inbound receivers: `apps/api/src/routes/webhooks.ts` (Stripe, Jira, JSM, M365), raw-body capture in `apps/api/src/app.ts`, signature/timestamp helpers in `apps/api/src/lib/webhook-signature.ts`, dedup/claim library in `apps/api/src/lib/idempotency.ts`.
- Outbound delivery: `apps/api/src/lib/webhook-dispatcher.ts` (inline fallback), `apps/worker/src/tasks/webhook-dispatcher.ts`, `apps/worker/src/tasks/webhook-retry.ts`, queue producers/consumers, scheduler (`apps/worker/src/main.ts`, `scan-lock.ts`).
- Admin management + DLQ: `apps/api/src/routes/webhook-management.ts`, SDK `packages/sdk/src/webhooks.ts`, web UI `apps/web/app/(admin)/admin/webhooks/**`, tests, docs.
- Data model/RLS: migrations `5302032`, `5302050`, `5302053`, `5302101`, `5302129`, `5302410`.
- Observability: `apps/api/src/lib/metrics.ts`, `infra/digitalocean/prometheus.rules.yml`.
- Secrets: `apps/api/src/config/env.ts`, `.env.example`, `infra/digitalocean/docker-compose.yml`, `.github/workflows/deploy-do.yml`, `docs/SECRETS_ROTATION.md`.

Not reviewed here (owned by other domains): payment reconciliation logic (BILL), Alertmanager plumbing (IR), RLS policy catalog breadth (RLS), overall tenant-isolation model (MT).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/routes/webhooks.ts` (655 lines) | Source | All four inbound receivers | Signature, timestamp, dedup, logging |
| `apps/api/src/lib/webhook-signature.ts` | Source | HMAC + timestamp + raw-body helper | 5-min tolerance; fail-closed helper |
| `apps/api/src/lib/idempotency.ts` | Source | Atomic claims / store / delete | Redis SET NX EX; 24h default TTL |
| `apps/api/src/lib/webhook-dispatcher.ts` | Source | Outbound inline dispatcher | Claims, HMAC, retries, DLQ, metrics |
| `apps/worker/src/tasks/webhook-dispatcher.ts` | Source | Queued outbound dispatcher | Per-endpoint claim, SSRF pinning |
| `apps/worker/src/tasks/webhook-retry.ts` | Source | Retry/DLQ worker task | 5 retries, 1m×2^n backoff, batch 20 |
| `apps/api/src/routes/webhook-management.ts` | Source | Admin CRUD, DLQ, test ping | Authz, masking, optimistic locking |
| `apps/api/src/app.ts:110-151` | Source | JSON parser, rate limit, timeout | 10mb global; webhook rate-limit skip |
| `apps/api/src/lib/pinned-fetch.ts`, `ssrf-guard.ts` (+ worker copies) | Source | SSRF defense | DNS pinning closes rebinding |
| `supabase/migrations/5302032/5302050/5302053/5302101/5302129/5302410` | Migrations | Tables, RLS, unique key | DLQ has no DELETE policy |
| `apps/api/src/__tests__/webhook-*.test.ts`, `apps/worker/src/__tests__/webhook-*.test.ts` | Tests | Coverage of claims/DLQ/signature | Gaps in retry semantics |
| `docs/modules/webhooks.md`, `docs/modules/webhook-management.md` | Docs | Consumer/admin docs | Stale M365 claims; no catalog |
| `docs/SECRETS_ROTATION.md` | Docs | Rotation inventory | Env secrets covered; endpoint secrets not |
| `infra/digitalocean/prometheus.rules.yml` | Config | Alert rules | No webhook/DLQ rule |

## Verification Performed

Fresh commands at `8d299b8d` (all read-only; target worktree):

| Command | Observed result |
|---|---|
| `git log --oneline -3` | `8d299b8d Merge PR #168…`; worktree clean |
| `grep -n "claimIdempotencyKey\|Idempotency-Key\|idempotency_key:" apps/api/src/lib/webhook-dispatcher.ts apps/worker/src/tasks/webhook-dispatcher.ts` | Claims at API:179 and worker:84; header API:185/worker:99; persisted key API:219/worker:124,179 |
| `grep -rn "M365_CLIENT_STATE" deploy-do.yml docker-compose.yml env.ts` | `deploy-do.yml:597,647,689`, `docker-compose.yml:90`, `env.ts:59` — wired |
| `grep -rn "M365_WEBHOOK_SECRET" apps infra .github` | Only explanatory comments (`env.ts:58`, `.env.example:33`) — declaration removed |
| `grep -n "M365_REPLAY_WINDOW_SECONDS\|storeIdempotencyKey\|IDEMPOTENCY_TTL_SECONDS" webhooks.ts idempotency.ts` | Claim TTL 7d at `webhooks.ts:27,629`; `storeIdempotencyKey` at `:47` resets to `idempotency.ts:50` 24h |
| `grep -n "retry_count: result.attempts\|dead_letter: failed\|recordWebhook.*" dispatchers/retry` | API:217-218 truthful attempts; counters at API:124,224, worker:127-128,183, retry:149,175,208 |
| `grep -n "rawBodyBuffer\|raw body unavailable" webhooks.ts` | Jira:377-379, JSM:479-481 fail closed |
| `grep -n "create policy" 5302050_webhook_retry_dlq.sql` | select/insert/update only — no DELETE policy |
| `grep -n 'limit: "10mb"\|webhooks/' app.ts` | `:112` 10mb global; `:142` webhook rate-limit skip |
| `grep -rn "dead_letters" supabase/migrations` | No DELETE policy in any migration (5302050, 5302055, 5302120 only) |
| `grep -rn "webhook_deliveries" migrations | policy` | insert/update/delete exist (5302101:85-115, 5302129:1975-1987) |
| `grep -n "webhook" prometheus.rules.yml` | 0 matches — no DLQ/delivery alert |
| `grep -rn "pinnedFetch(" apps --include=*.ts` | API dispatcher:58, test:469, worker dispatcher:150, retry:122 |
| `sed -n '185,193p' webhook-management.ts; '69,77p' webhook-retry.ts; '210,213p' webhook-dispatcher.ts` | DLQ retry recreates `{event,receivedAt}` row, worker skips no-data rows, DLQ row deleted → no-op path confirmed |
| `grep -n "claim\|lock" webhook-retry.ts` | No claim/lock in retry task |
| `git merge-base --is-ancestor` checks | `8d299b8d` descends from `9c0b88c`; fix commits `adea562c` (raw body + M365 window) and `68fd8d12` (retry accounting + metering) are between them |

### Verification duty (previous register rows, area WH + clearly in-domain)

| Previous row | Status at 8d299b8d | Basis |
|---|---|---|
| WH-P1-001 — non-atomic/absent outbound idempotency | `verified-fixed` | Atomic claims in both dispatchers + tests |
| WH-P1-002 — M365 auth/secret/deploy gap | `verified-fixed` | `M365_CLIENT_STATE` deploy-wired; dead `M365_WEBHOOK_SECRET` removed |
| WH-P2-001 — M365 no replay window | `partially-fixed` | 7-day claim present, but post-processing store resets TTL to 24h |
| WH-P2-002 — fixed retry_count / duplicated retry logic | `verified-fixed` | Actual attempts + dead-lettered inline rows |
| WH-P2-003 — outbound/DLQ unmetered | `verified-fixed` | Counters on API + worker + retry paths |
| WH-P2-004 — Jira/JSM signature fallback | `verified-fixed` | `rawBodyBuffer` fail-closed + tests |
| WH-P2-005 — DLQ no DELETE policy | `still-open` | No DELETE policy in any migration; masked today by service-role default |
| WH-P2-006 — no per-provider schema/size cap | `still-open` | Global 10mb, no Zod, rate-limit exempt |
| WH-P3-001 — random test idempotency key | `still-open` | `webhook-management.ts:485` unchanged |
| WH-P3-002 — no event catalog/docs | `partially-fixed` | Module docs exist; no catalog; stale M365 signature claims |
| RES-P3-002 — worker inserts deliveries without key | `verified-fixed` | Worker derives/persists `idempotency_key` |
| BILL-P3-001 — raw body string vs Buffer | `still-open` | `app.ts:117` string; `webhooks.ts:153` cast |
| SEC-P2-002 — SSRF DNS-rebinding TOCTOU | `verified-fixed` | `pinnedFetch` on all four outbound paths |
| ACM-P2-005 — webhook reads not manage-gated | `still-open` | GET routes lack `requirePermission('webhooks','view')` |
| ACM-P2-007 — signing secrets plaintext, no rotation | `still-open` | `secret text`; no expiry/rotation metadata; not in rotation doc |
| IR-P2-003 — no alerting on DLQ accumulation | `still-open` (webhook half) | No rule consumes `portal_webhook_dead_letters_total` |
| RLS-P2-002 — sibling of WH-P2-005 | covered by WH-P2-005 row | Same gap; one fix closes both |
| SECRET-P1-001 — dead M365 secret | residual resolved (out of area) | Dead key removed; owning secrets domain should close it |

## Executive Summary

The webhook surface is materially stronger than the previous full run. Both outbound dispatchers now claim a per-endpoint idempotency key atomically (Redis `SET NX EX`), send it as `Idempotency-Key`, and persist it on the delivery row; inbound Jira/JSM signatures fail closed unless the captured raw body exists; M365 uses a constant-time `clientState` gate with a 7-day replay claim; outbound delivery is SSRF-pinned on all four paths; DLQ/delivery counters exist; and the admin UI/API exposes dead letters with retry/dismiss and audit logging. The previous WH-P1 findings and four of the WH-P2 findings are verified fixed on main.

Remaining risks are concentrated in the retry/DLQ lifecycle and hardening edges:

1. The M365 "7-day" replay window is effectively 24 hours because the post-processing `storeIdempotencyKey` resets the TTL (WH-P2-001 residual).
2. The admin dead-letter Retry action silently discards inline-dispatched dead letters without attempting delivery (new P2).
3. `webhook-retry` has no row claim, so overlapping runs can double-send (new P2).
4. Inbound webhook routes still share the global 10mb JSON parser, have no per-provider schema, and are exempt from rate limiting (WH-P2-006).
5. `webhook_dead_letters` still has no DELETE policy, and reads are not gated by the existing `webhooks:view` permission; per-endpoint signing secrets remain plaintext with no rotation.

Recommended next actions: fix the TTL reset, make DLQ retry truthful, claim retry rows, add per-route body limits + schemas, add the DLQ DELETE policy and read permission, and add a DLQ alert rule.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Stripe receiver | `webhooks.ts:131-349` | Billing events | Implemented | Low | `constructEvent` + `stripe-<event.id>` claim |
| Jira receiver | `webhooks.ts:351-451` | Issue status sync | Implemented | Low | raw-body HMAC + 5-min timestamp + body-hash dedup |
| JSM receiver | `webhooks.ts:453-558` | Ticket status sync | Implemented | Low | same controls |
| M365 receiver | `webhooks.ts:560-653` | Change-notification logging | Implemented | Med | clientState only; 7d claim resets to 24h; value[0] only |
| Signature helper | `lib/webhook-signature.ts` | HMAC/timestamp/raw body | Implemented | Low | timing-safe; fail-closed helper |
| Claim library | `lib/idempotency.ts` | Atomic dedup claims | Implemented | Low-Med | 24h default; in-memory fallback per process |
| API inline dispatcher | `lib/webhook-dispatcher.ts` | Queue fallback delivery | Implemented | Med | 3 attempts; summary-only payloads |
| Worker dispatcher | `worker/tasks/webhook-dispatcher.ts` | Queued delivery | Implemented | Med | claim + HMAC + pinned fetch; full payload stored |
| Worker retry | `worker/tasks/webhook-retry.ts` | Retry + DLQ | Implemented | High | no row claim; skips no-data rows silently |
| DLQ admin | `routes/webhook-management.ts:75-258` | List/retry/dismiss | Implemented | Med | retry no-op for inline rows; no DELETE policy |
| Test ping | `routes/webhook-management.ts:430-542` | Admin test | Implemented | Low | random key; not through dispatcher |
| Web UI | `apps/web/app/(admin)/admin/webhooks/**` | Admin console | Implemented | Low | dead-letters page + actions |
| SDK | `packages/sdk/src/webhooks.ts` | Client | Implemented | Low | endpoints + DLQ methods |
| Metrics | `lib/metrics.ts:30-145` | Counters | Implemented | Low | no alert rules |
| Docs | `docs/modules/webhooks.md`, `webhook-management.md` | Module docs | Partial | Low | stale M365 claims; no event catalog |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Inbound endpoints | 3 | 4 receivers, fail-closed secrets, dedup | No schema/size cap; rate-limit exempt; M365 value[0] | WH-P2-006, M365 batch finding |
| Outbound delivery | 3 | Atomic claim + HMAC + pinned SSRF on both paths | Retry fidelity/concurrency | Claim retry rows; persist full body |
| Event models | 2 | Inline `{event,timestamp,data}`; 2 event names | No catalog/versioning; retry body drifts | Publish `docs/WEBHOOKS.md` |
| Signature verification | 4 | HMAC-SHA256 timing-safe over raw bytes; fail closed; Stripe SDK | M365 has no signature by provider design | Keep; document M365 clientState |
| Timestamp tolerance | 3 | 5-min window; Jira/JSM require timestamp; Stripe SDK default | M365 window effectively 24h | Fix TTL reset |
| Replay nonce | 3 | Atomic digest claim (M365 7d intent); body-hash keys | TTL overwrite; in-memory fallback | Fix TTL; make Redis required |
| Idempotency keys | 4 | Atomic claims both dispatchers; header; DB unique key | Retry task doesn't claim; insert conflicts ignored | Retry claim; handle conflicts |
| Retry backoff | 3 | Worker 1m×2^n ×5; inline 200ms×2 ×3; DLQ | Concurrent double-send; payload drift | Row claim + verbatim replay |
| Dead-letter queues | 3 | Table, admin list/retry/dismiss, worker dead-lettering | Retry no-op; no DELETE policy; no retention/alert | Truthful retry; policy; retention; alert |
| Secrets | 2 | Masking; env secrets in rotation doc | Endpoint secrets plaintext, no rotation/expiry | Rotation policy + optional encryption |
| Tenant scoping | 3 | Dispatch scoped by org; DLQ scoped via endpoint join | Reads not permission-gated | `webhooks:view` on GET routes |
| Payload schema/size | 2 | Global JSON parser only | 10mb unauthenticated parse; no schemas | Per-route limit + Zod |
| Delivery logs | 3 | `webhook_deliveries` + admin views | Unchecked inserts; no retention | Conflict handling; retention |
| Admin management | 3 | CRUD, optimistic locking, audit, UI, SDK | Read authz gap | Permission gate |
| Secret rotation | 2 | Provider secrets inventoried | Outbound endpoint secrets absent | Add rotation row/runbook |
| Timeouts | 4 | 10s outbound abort; 30s request timeout | Response read unbounded | Cap response size |
| Tests/docs | 3 | Strong signature/idempotency/DLQ tests; module docs | Retry semantics untested; no catalog | Add tests below; publish catalog |

## Detailed Review

### Item: Inbound receivers and signature verification

- Evidence: `webhooks.ts:131-653`; `webhook-signature.ts:3-73`; `app.ts:110-120`.
- What it does: Stripe uses `stripe.webhooks.constructEvent` over `req.rawBody`; Jira/JSM require `x-hub-signature` and the captured raw body and reject 401 when it is missing, then enforce a 5-minute timestamp window with `requireTimestamp: true`; M365 authenticates every notification by constant-time `clientState` and fails closed (501 unset / 401 mismatch).
- Current controls: HMAC-SHA256 timing-safe compare; per-event dedup keys (`stripe-<id>`, body-hash Jira/JSM keys, M365 notification digest); audit + delivery logging; claim released on handler failure so provider retries reprocess.
- Missing controls: per-provider schemas, per-route body cap, inbound rate limiting; M365 processes only `value[0]`; the M365 replay claim TTL is reset to 24h after processing.
- Risks: WH-P2-001 residual, WH-P2-006, M365 batch handling.
- Suggested tests: oversized body → 413; malformed provider payload → 400; multi-notification M365 batch; final TTL assertion after processing.

### Item: Outbound dispatchers (API inline + worker queue)

- Evidence: `lib/webhook-dispatcher.ts:134-262`; `worker/tasks/webhook-dispatcher.ts:36-219`; `lib/task-producer.ts:76-105`.
- What it does: The API prefers the queue; the inline fallback fans out per endpoint with an atomic per-endpoint claim, HMAC signing, 3 attempts (200ms/400ms backoff), truthful `retry_count`, dead-letter on failure and release of the claim; the worker does the same with a 10s timeout, pinned fetch, blocked-URL dead-lettering and `next_retry_at` scheduling.
- Current controls: Idempotency-Key header + persisted key; DB unique constraint; org-scoped endpoint lookup; PII-safe summaries on the inline path (full payload on the worker path).
- Missing controls: retry-task row claim; conflict handling on delivery inserts; bounded response reads.
- Risks: new findings on retry concurrency, payload drift, silent insert conflicts, unbounded response bodies.

### Item: Worker retry + dead-letter lifecycle

- Evidence: `worker/tasks/webhook-retry.ts:12-230`; `worker/main.ts:81-89`; `lib/scan-lock.ts:26-73`; `routes/webhook-management.ts:75-258`.
- What it does: Every 5 minutes (one replica via scan lock) the task selects up to 20 due failed rows, retries with the preserved Idempotency-Key and re-signed HMAC, updates `retry_count`/`next_retry_at` with 1m×2^n backoff, and dead-letters after 5 attempts. Admins can list/retry/dismiss DLQ rows; retry recreates a due-now delivery and deletes the DLQ row.
- Current controls: SSRF guard + pinned fetch; attempt counting; audit events; UI confirm dialog for dismiss.
- Missing controls: row claim/lock; truthful retry for non-replayable rows; DLQ DELETE policy; retention; alerting.
- Risks: the retry no-op (P2), concurrent double-send (P2), WH-P2-005, IR-P2-003.

### Item: Secrets and admin management

- Evidence: `5302032:8`; `webhook-management.ts:20-51,168-397,430-542`; `env.ts:54-59`; `SECRETS_ROTATION.md:52-54`.
- What it does: Endpoint secrets are masked on GET, audit metadata keys containing "secret" are redacted (`services/audit.ts:34-45`), provider secrets are deploy-wired and in the rotation inventory, and CRUD mutations require `webhooks:manage` with optimistic locking and audit logs.
- Missing controls: GET routes are not permission-gated; endpoint secrets have no expiry/rotation metadata and are absent from the rotation doc; POST/PATCH responses return the secret unmasked to the caller.
- Risks: ACM-P2-005, ACM-P2-007.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| WH-001 | Inbound endpoints | `webhooks.ts:131-653` | Signature/clientState + dedup | No schema/size cap, rate-limit exempt | P2 | Per-route limit + Zod |
| WH-002 | Outbound delivery | both dispatchers | Atomic claim, HMAC, pinned SSRF | Retry concurrency/fidelity | P2 | Claim retry rows; verbatim body |
| WH-003 | Event models | `lib/webhook-dispatcher.ts:166` | Inline envelope | No catalog/versioning | P3 | Publish catalog |
| WH-004 | Signature verification | `webhook-signature.ts:3-21` | Timing-safe HMAC over raw bytes | — | — | Keep; M365 unsigned by design |
| WH-005 | Timestamp tolerance | `webhook-signature.ts:23,62-73` | 5-min window; require for Jira/JSM | M365 effective window 24h | P2 | Fix TTL reset |
| WH-006 | Replay nonce | `webhooks.ts:622-632`; `idempotency.ts:99-136` | Atomic claim TTL | TTL overwrite; per-process fallback | P2 | Preserve TTL; require Redis |
| WH-007 | Idempotency keys | API:178-186,219; worker:80-100,179 | Atomic per-endpoint claim + header + DB unique | Retry task unclaimed; conflicts ignored | P2/P3 | Claim in retry; handle conflicts |
| WH-008 | Retry backoff | `webhook-retry.ts:8-10,130-186` | 5× exponential (1m base); inline 3× | No claim; no jitter | P2 | Row claim; consider jitter |
| WH-009 | Dead-letter queues | `5302050`; `webhook-management.ts:75-258` | Table + admin retry/dismiss | Retry no-op; no DELETE policy/retention/alert | P2 | Truthful retry; policy; alert |
| WH-010 | Secrets | `5302032:8`; `env.ts:56-59` | Masking + deploy wiring | Endpoint secrets plaintext/no rotation | P2 | Rotation policy; optional encryption |
| WH-011 | Tenant scoping | `webhook-management.ts:84-104,162-163`; dispatcher org filter | Org-scoped queries + explicit DLQ org check | GET authz not permission-gated | P2 | `webhooks:view` gate |
| WH-012 | Payload schema/size | `app.ts:110-120,138-143` | Global parser | 10mb unauth parse; no schemas | P2 | Per-route limit + Zod |
| WH-013 | Timeouts | dispatcher:53-54; `app.ts:151` | 10s outbound; 30s request | Response bytes unbounded | P3 | Cap response read |
| WH-014 | Delivery logs | `webhook_deliveries` + admin views | Full audit of attempts | Insert conflicts ignored; no retention | P3 | Conflict handling; retention |
| WH-015 | Admin management | `webhook-management.ts`; web UI | CRUD + locking + audit + DLQ UI | Read authz | P2 | Permission gate |

## Findings

23 findings (2 P1, 12 P2, 9 P3; statuses: 7 verified-fixed, 2 partially-fixed, 7 still-open, 7 open). Titles below; full evidence/impact/recommendation in the JSON.

**Verified fixed (this run):** Outbound webhook idempotency is non-atomic in the API and absent in the worker dispatcher; M365 webhook auth depends on `M365_CLIENT_STATE`…; Inline dispatcher records a fixed `retry_count`…; Outbound and DLQ delivery outcomes are not metered…; Inbound Jira/JSM signature falls back to re-serialized JSON…; Worker queued webhook dispatcher inserts deliveries without an idempotency key; Webhook SSRF guard has a DNS-rebinding TOCTOU window.

**Partially fixed:** M365 inbound notifications have no enforced timestamp/replay window (7-day claim reset to 24h); No committed event catalog or webhook documentation for consumers (module docs exist; no catalog; stale M365 claims).

**Still open:** `webhook_dead_letters` has no DELETE policy…; No per-provider payload schema or size cap…; Test endpoint generates a random idempotency key…; Webhook raw body typed as `string` but consumed as `Buffer`; Webhook endpoint and delivery reads are available to any org member…; Webhook signing secrets are stored plaintext with no rotation or expiry; No alerting when webhook dead-letters accumulate… (webhook half).

**New:** Admin dead-letter retry of inline-dispatched failures no-ops and deletes the DLQ row (P2); `webhook-retry` has no row claim: concurrent retry runs can double-send deliveries (P2); Retried deliveries replay a body without the envelope `timestamp` (P3); Delivery inserts ignore unique-key conflicts… (P3); Outbound webhook response bodies are read without a size cap (P3); M365 handler processes only the first notification in a batch (P3); No retention/cleanup for `webhook_deliveries` and `webhook_dead_letters` (P3).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Inline dead letters lost on admin retry (false success) | P2 | Med (Redis/queue outage) | Med | `webhook-management.ts:185-205`; `webhook-retry.ts:69-77`; dispatcher:210-213 | Truthful retry / non-replayable flag |
| Duplicate retries under concurrency | P2 | Med | Med-High | `webhook-retry.ts:16-30`; `consumer-bullmq.ts:15,31` | Row claim/SKIP LOCKED |
| M365 replay window 24h not 7d | P2 | Low | Low-Med | `webhooks.ts:47,629`; `idempotency.ts:50,144` | Preserve TTL on store |
| Unauthenticated 10mb parse / no schemas | P2 | Low | Med | `app.ts:112,142` | Per-route limit + Zod |
| DLQ dismiss fails under RLS allow-list | P2 | Low today | Med | `5302050:27-62`; `services/supabase.ts:198-226` | DELETE policy |
| Endpoint secret disclosure/retention | P2 | Low | Med | `5302032:8` | Rotation/encryption |
| Silent delivery-log gaps on re-dispatch | P3 | Low | Low | `5302053:19-21`; dispatcher:208 | Conflict handling |
| Memory pressure from hostile endpoint | P3 | Low | Med | `pinned-fetch.ts:91-99` | Response cap |

## Recommendations

### Immediate / Release Blocking

1. Fix the M365 replay TTL reset (`storeIdempotencyKey` must not shorten the 7-day claim) and add a test asserting the post-processing TTL.
2. Make DLQ retry truthful: do not delete the DLQ row until a delivery attempt happens; re-insert a DLQ row when the retry task skips a non-replayable row, or disable Retry for those rows in the UI.

### This Week

3. Add a row claim/lease to `webhook-retry` (or `FOR UPDATE SKIP LOCKED`) and a concurrency test.
4. Add a tighter per-route JSON limit for `/api/v1/webhooks/*` plus per-provider Zod schemas.
5. Add the `webhook_dead_letters` DELETE policy and gate webhook read routes with `requirePermission('webhooks','view')`.
6. Add a Prometheus rule on `portal_webhook_dead_letters_total` growth and the outbound failure ratio.

### This Month

7. Persist/replay the full outbound body (including `timestamp`) on retries.
8. Handle unique-key conflicts on delivery inserts (update/upsert or log).
9. Document outbound endpoint secret rotation and add `last_rotated_at`/expiry guidance.
10. Publish the event catalog and correct the M365 statements in `docs/modules/webhooks.md`.

### Later / Platform Evolution

11. Cap outbound response reads and truncate stored `response_body`.
12. Process all M365 notifications in a batch (or explicitly document value[0]).
13. Add retention/cleanup for `webhook_deliveries`/`webhook_dead_letters`.
14. Consider making Redis mandatory for webhook dedup (fail closed vs per-process fallback) and adding jitter to retry backoff.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Pass the M365 TTL into `storeIdempotencyKey` | Restores the documented replay window | `webhooks.ts`, `idempotency.ts` | Unit test on final TTL |
| Keep DLQ row until retry attempt | Removes false success | `webhook-management.ts`, `webhook-retry.ts` | Route + task test |
| `requirePermission('webhooks','view')` on GET routes | Closes ACM-P2-005 | `webhook-management.ts` | 403 test for view-less member |
| DLQ DELETE policy migration | Closes WH-P2-005/RLS-P2-002 | new migration | RLS-client delete test |
| Webhook/DLQ alert rule | Operator visibility | `prometheus.rules.yml` | `promtool test rules` |
| Correct M365 lines in module docs | Prevents broken integrations | `docs/modules/webhooks.md` | doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Row-claim/lease in webhook-retry | P2 | platform/backend | S | none |
| Truthful DLQ retry semantics | P2 | integrations/backend | S | none |
| Per-route body limit + provider schemas | P2 | integrations/backend | M | none |
| DLQ DELETE policy + RLS test | P2 | DB/platform | S | RLS rollout |
| Read-permission gate for webhook routes | P2 | API platform | S | none |
| DLQ/delivery alert rules | P2 | platform ops | S | metrics (done) |
| Full-body retry replay | P3 | platform/backend | S | none |
| Delivery-insert conflict handling | P3 | integrations/backend | S | none |
| Response size cap | P3 | integrations/backend | S | none |
| M365 multi-notification handling | P3 | integrations/backend | S | provider behavior check |
| Retention for webhook tables | P3 | platform/backend | S | none |
| Event catalog + doc-lint | P3 | docs/API | S | none |

## Suggested Tests

- Unit: `storeIdempotencyKey` preserves a caller-provided TTL (M365 7d) and does not shorten it.
- Unit/route: DLQ retry on a no-`data` dead letter leaves the DLQ row intact and returns a non-success or "non-replayable" state.
- Worker: `webhookRetry` concurrency — two overlapping invocations against the same due row must produce one HTTP attempt (row claim).
- Worker: retry body fidelity — the retried body equals the first-attempt body (including `timestamp`) and the HMAC verifies.
- API: re-dispatch after a failed delivery records the successful attempt despite the unique idempotency key.
- API: inbound >limit body → 413; malformed Jira/JSM/Stripe/M365 payload → 400 before side effects.
- API: GET webhook routes → 403 for an org member without `webhooks:view`; 200 for a member with it.
- RLS: non-super-admin org admin deletes a DLQ row under the user-scoped client and one row is removed.
- Security: hostname re-resolving to a private IP between guard and connect is still blocked (pinned fetch).
- E2E: admin retry/dismiss flows show accurate success/failure states (extend `apps/web/e2e/admin/webhooks.spec.ts`).
- CI/ops: `promtool test rules` for the new DLQ alert thresholds.

## Suggested Documentation Updates

- `docs/WEBHOOKS.md` (new): event catalog (`project.created`, `ticket.created`), envelope `{event,timestamp,data}`, `X-Webhook-Signature: sha256=<hmac>`, `Idempotency-Key`, retry schedule (5× exponential, 1m base), DLQ semantics and admin replay, inbound signature/timestamp expectations per provider, explicit "M365 is clientState-authenticated and unsigned".
- `docs/modules/webhooks.md`: fix lines 8/16/39 (M365 HMAC/x-hub-signature claims are wrong), add replay-window and rate-limit notes.
- `docs/modules/webhook-management.md`: document DLQ list/retry/dismiss, non-replayable inline rows, and the read permission.
- `docs/SECRETS_ROTATION.md`: add per-endpoint outbound webhook signing secrets (90-day cadence, rotation via PATCH).
- `docs/RLS-rollout.md` (or equivalent): note the required `webhook_dead_letters` DELETE policy before allow-listing `webhook-management`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `webhook-management` (or any webhook module) currently in `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` in prod? | Determines whether WH-P2-005 is latent or already breaking dismiss/retry | Redacted prod env inspection |
| Is `TASK_QUEUE_ENABLED=true` in prod (is the inline fallback ever used)? | Scope of the DLQ retry no-op finding | Redacted prod env inspection |
| Does the M365 subscription actually deliver batched `value` arrays? | Confirms impact of the value[0] finding | Graph notification samples/logs |
| Which consumers implement `Idempotency-Key` dedup? | Bounds the duplicate-retry impact | Consumer inventory/interviews |
| Is Redis HA/single-instance, and what happens on failover? | Dedup durability | Infra review |

## Appendix

- Commit lineage: `8d299b8d` descends from `9c0b88c`; the webhook fixes between them are `adea562c` (fail-closed raw-body signatures + M365 replay window, WH-P2-001/004) and `68fd8d12` (retry accounting + outcome metering, WH-P2-002/003); `49646db7`/`ae07bd22` (SEC-P2-002) predate `9c0b88c`.
- Data path (outbound): `dispatchWebhook` → `enqueueTask('webhook-dispatcher')` → worker claim `idempotency:<base>:<endpoint>` → HMAC → `pinnedFetch` → `webhook_deliveries` row → (failure) `webhook-retry` → DLQ `webhook_dead_letters` → admin retry/dismiss.
- Data path (inbound): provider → `express.json` rawBody capture → signature/timestamp → `claimIdempotencyKey` → handler side effects → `logWebhookDelivery` (summary) → `storeIdempotencyKey('done')` (TTL reset — see WH-P2-001 residual).
- No secrets were printed during this audit; secret values were not accessed.

## Findings

| ID | Severity | Title |
|---|---|---|
| WH-P1-001 | P1 | Outbound webhook idempotency is non-atomic in the API and absent in the worker dispatcher |
| WH-P1-002 | P1 | M365 webhook auth depends on `M365_CLIENT_STATE` which the deploy pipeline does not write, while `M365_WEBHOOK_SECRET` is dead config |
| WH-P2-001 | P2 | M365 inbound notifications have no enforced timestamp/replay window |
| WH-P2-002 | P2 | Inline dispatcher records a fixed `retry_count` and duplicates the worker's retry logic |
| WH-P2-003 | P2 | Outbound and DLQ delivery outcomes are not metered; only inbound success increments the counter |
| WH-P2-004 | P2 | Inbound Jira/JSM signature falls back to re-serialized JSON when `req.rawBody` is absent |
| WH-P2-005 | P2 | `webhook_dead_letters` has no DELETE policy while the API deletes via the RLS client |
| WH-P2-006 | P2 | No per-provider payload schema or size cap on webhook ingress (global 10mb JSON limit) |
| WH-P3-001 | P3 | Test endpoint generates a random idempotency key and never dedups |
| WH-P3-002 | P3 | No committed event catalog or webhook documentation for consumers |
| WH-P3-003 | P3 | Worker queued webhook dispatcher inserts deliveries without an idempotency key |
| WH-P3-004 | P3 | Webhook raw body typed as `string` but consumed as `Buffer` |
| WH-P2-007 | P2 | Webhook endpoint and delivery reads are available to any org member (not manage-gated) |
| WH-P2-008 | P2 | Webhook signing secrets are stored plaintext with no rotation or expiry |
| WH-P2-009 | P2 | Webhook SSRF guard has a DNS-rebinding TOCTOU window |
| WH-P2-010 | P2 | No alerting when webhook dead-letters accumulate or payment reconciliation drifts |
| WH-P2-011 | P2 | Admin dead-letter retry of inline-dispatched failures no-ops and deletes the DLQ row |
| WH-P2-012 | P2 | `webhook-retry` has no row claim: concurrent retry runs can double-send deliveries |
| WH-P3-005 | P3 | Retried deliveries replay a body without the envelope `timestamp` (payload drift) |
| WH-P3-006 | P3 | Delivery inserts ignore unique-key conflicts, losing the successful-attempt record |
| WH-P3-007 | P3 | Outbound webhook response bodies are read without a size cap |
| WH-P3-008 | P3 | M365 handler processes only the first notification in a batch (value[0]) |
| WH-P3-009 | P3 | No retention/cleanup for webhook_deliveries and webhook_dead_letters |
