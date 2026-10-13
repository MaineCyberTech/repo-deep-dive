# Performance, Scalability, and Cost Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening rerun)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (monorepo: apps/api, apps/web, apps/worker, packages/*, supabase/)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent `15_performance_scalability_cost` (area PERF)
- Output path: `docs/audits/repo-deep-dive/{run}/15_performance_scalability_cost.md` (this run folder)
- Scope limitations: static, read-only analysis. No builds, no load tests, no live Supabase/Prometheus/droplet access. Bundle sizes, CI wall-clock times, and external service quotas are `Unknown` and marked as such.

## Scope

Reviewed: web bundle/perf configuration, SSR/client rendering modes, heavy dependencies, images/caching, pagination, N+1/query patterns, indexes/migrations, worker throughput and queue concurrency, realtime (SSE) scaling, webhook volume, rate limiting, CDN/proxy, container resources, droplet sizing, CI caching/build timeouts, storage/log growth, and third-party API cost.

Not reviewed (out of scope or not verifiable statically): live metrics/TSDB cardinality, Supabase plan tier and Realtime/REST quotas, DigitalOcean Monitoring configuration, actual CI run durations, production traffic volumes.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/middleware/request-id.ts` | source | HTTP metrics labels | `route: req.path` (lines 41-49) |
| `apps/api/src/lib/metrics.ts` | source | metric label sets | 15s-scraped counters/histograms |
| `apps/api/src/lib/pagination.ts` | source | shared pagination | `LIST_HARD_CAP=1000` (line 19) |
| `apps/api/src/lib/permissions.ts`, `middleware/permissions.ts`, `middleware/entitlement.ts` | source | permission fan-out/caching | no cache for permissions |
| `apps/api/src/routes/store/catalog.ts`, `apps/api/src/lib/store-catalog.ts` | source | public catalog reads | uncached, limit(1000) |
| `apps/web/app/(public)/store/*`, `apps/web/lib/catalog/catalog-source.ts` | source | public SSR + fetch mode | force-dynamic, no fetch cache |
| `apps/api/src/routes/bulk.ts`, `apps/api/src/app.ts` | source | bulk invite vs 30s timeout | sequential N+1 |
| `apps/api/src/routes/billing.ts` | source | Stripe pagination | fixed limits, no cursor |
| `apps/api/src/routes/notifications.ts`, `apps/web/components/NotificationBell.tsx` | source | SSE/realtime scaling | per-connection channel |
| `apps/api/src/routes/compliance.ts`, `apps/api/src/routes/final/time-entries.ts` | source | unbounded lists | no range/limit |
| `supabase/migrations/*.sql` (134 files) | schema | indexes/query patterns | 316 `create index` statements |
| `apps/worker/src/{main,env,producer,consumer-bullmq,consumer-sqs,schedule-config}.ts`, `tasks/*` | source | worker/queue throughput | concurrency, retries, batching |
| `infra/digitalocean/docker-compose.yml`, `prometheus.yml`, `Caddyfile.prod`, `infra/terraform/digitalocean/*` | config | container/droplet/CDN sizing | 7 services, ~1.5GB limits |
| `.github/workflows/*`, `.github/actions/*` | CI | caching, build/test budgets | pnpm/docker/playwright caches |
| `docs/PERFORMANCE.md`, `docs/CLOUDFLARE_CACHE_AND_PROXY_RECOMMENDATIONS.md`, `docs/API_RATE_LIMITING.md` | docs | claimed controls | mostly accurate; one overstatement |

## Verification Performed

All commands run read-only in `/tmp/opencode/mct-audit-target` at `8d299b8d`.

| Command (abridged) | Observed result |
|---|---|
| `git rev-parse HEAD` | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (main) |
| `grep -rn 'select("\*")' apps/api/src --include='*.ts' \| grep -v __tests__ \| wc -l` | 154 (plus 1 single-quoted variant) |
| `grep -rln 'lib/pagination' apps/api/src/routes` | 4 files (store/campaigns, promotions, quotes, visual-assets) |
| `grep -rln 'queryInt(req.query.page' apps/api/src/routes` | 37 files parse page/limit inline |
| `grep -rn 'count: "exact"' apps/api/src --include='*.ts' \| grep -v __tests__ \| wc -l` | 77 occurrences in 46 files (67 with `select("*")`) |
| `grep -rn 'limit(10000)' apps/api/src --include='*.ts' \| grep -v __tests__` | 12 call sites, all export paths |
| `grep -rn 'ANALYZE\|bundle-analyzer\|size-limit\|bundlewatch' .github/ apps/web/package.json` | no CI bundle step/budget (only CodeQL "Analyze") |
| `grep -rn 'resolveEffectivePermissions' apps/api/src \| grep -v __tests__` | 3 middleware/routes + resolver; `grep` for cache in permissions files → none |
| `grep -rn 'requirePermission(' apps/api/src --include='*.ts' \| grep -v __tests__ \| wc -l` | 211 call sites in 44 route files |
| `grep -rn 'responseCache' apps/api/src/routes/store/*.ts apps/api/src/lib/store-catalog.ts` | no output (public catalog uncached) |
| `grep -rn 'route: req.path' apps/api/src --include='*.ts'` | `request-id.ts:43,47` only |
| Python loop+await scan over `apps/api/src` | 32 loop-with-DB-await sites; notable `bulk.ts:83`, `billing.ts:273/304/338`, `edu-automation.ts:1043` |
| `grep -rn 'force-dynamic' apps/web/app --include='*.tsx' \| wc -l` | 290 files (287 pages, including `(public)/store/*`) |
| `grep -rin 'create index' supabase/migrations \| wc -l` | 316 statements |
| `grep -n 'mem_limit' infra/digitalocean/docker-compose.yml` | 7 services totalling 1,520 MB of limits |
| `grep -rn 'turbo' .github/workflows/*.yml` | no turbo cache step (pnpm/docker/playwright caches present) |
| `git log -- apps/api/src/lib/pagination.ts` | added in `8f9d06c7` ("P2-21"), extended in `ccb8d1a6` (store catalog N+1 fix) |

## Executive Summary

The stack has real performance discipline: a shared pagination helper, a Redis-backed response cache with tenant-scoped keys, an index-dense schema (including a dedicated FK-index migration), bounded retention batches, BullMQ retries/backoff, scan locks, log rotation, container memory/PID limits, and CI dependency caches. Most previous remediation intent (P2-21 pagination, store-catalog N+1) is present in code.

The remaining risks are concentrated in four areas. (1) **Per-request fan-out to hosted Supabase**: permission resolution is uncached and duplicated across middleware, every paginated list also runs an exact count, and the public storefront re-reads the full catalog on every dynamic render. (2) **Unbounded metric cardinality**: HTTP metrics label by raw URL path, which grows with every resource ID and feeds a 256MB/30d Prometheus. (3) **Sync-over-async request patterns**: bulk invite (500 × 4 sequential calls under a 30s timeout) and billing sync (unpaginated Stripe + row-by-row upserts). (4) **Realtime fan-out**: one Supabase channel per SSE connection with no cap and a leaked polling fallback on the client.

No P0/P1 performance defects were found (no evidence of data loss, outage-causing unbounded loops, or release-blocking regressions). Four previous PERF/adjacent rows were re-verified: two still open, one partially fixed, one still open (cross-domain BILL), plus one cross-domain SEC caching row still open.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| HTTP metrics | `middleware/request-id.ts:41-49` | request count/latency | label = raw path | High cardinality | unbounded series |
| Response cache | `middleware/cache.ts` | Redis+memory GET cache | used by 11 route files | none material | keys scoped org/user; SCAN invalidation |
| Pagination helper | `lib/pagination.ts` | shared page/limit + cap | 4 route files adopt it | inconsistent | 37 files inline parsing |
| Permission resolver | `lib/permissions.ts:49-138` | effective permissions | uncached, 3-5 queries | per-request fan-out | 211 call sites |
| Entitlement resolver | `middleware/entitlement.ts:48` | module entitlements | 30s in-memory cache | OK | permissions resolved again per call |
| Store catalog | `lib/store-catalog.ts:130-154` | public product/category reads | `select("*").limit(1000)`, uncached | DB cost per view | public routes |
| Public storefront | `apps/web/app/(public)/store/*` | marketing pages | `force-dynamic`, 2 API calls/render | SSR + DB cost | no ISR |
| Bulk invite | `routes/bulk.ts:71-170` | ≤500 invites | 4 sequential calls per entry | timeout/partial | 30s request timeout |
| Billing sync | `routes/billing.ts:256-358` | Stripe reconciliation | fixed limits, row-by-row upserts | stale data + API cost | no cursor pagination |
| SSE notifications | `routes/notifications.ts:47-144` | realtime bell | channel per connection | fan-out | no cap; shared admin socket today |
| Retention | `worker/src/tasks/retention.ts` | purge old rows | 1000/batch, 200 batch cap | OK | reports truncation |
| Webhook retry/DLQ | `worker/src/tasks/webhook-retry.ts` | failed delivery retry | batch 20, ≤5 retries | OK | per-row endpoint lookup |
| Queue | `worker/src/{producer,consumer-bullmq}.ts` | BullMQ tasks | concurrency 10, 3 attempts, backoff | OK | single queue, no per-task rate limits |
| Scheduler | `worker/src/schedule-config.ts` | hourly/daily scans | staggered offsets + Redis lock | OK | scans share the task queue |
| Containers | `infra/digitalocean/docker-compose.yml` | 7 services | 48-512MB limits, pids caps, 10m×3 logs | tight on 2GB | no CPU caps (deliberate) |
| Prometheus | `infra/digitalocean/prometheus.yml` | metrics | 15s scrape, 30d retention, 256MB | OOM risk | cardinality driver above |
| Proxy/CDN | `Caddyfile.prod`, `dns.tf` | TLS/proxy | Caddy + Cloudflare proxied | OK | no HTML cache policy |
| CI | `.github/actions/setup-pnpm`, workflows | build/test | pnpm/docker/playwright caches | OK | no turbo cache |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Bundle size indicators | 2 | `next.config.mjs:57` analyzer opt-in; no budget in CI | no baseline, no gate | size-limit budget + PR report |
| SSR/client hot spots | 2 | 290 `force-dynamic` files incl. public storefront | no ISR/HTML cache for public pages | revalidate or cache public routes |
| Heavy dependencies | 3 | web deps lean (`next`, `react`, `sentry`, `lucide-react`); server-only heavy deps | no measured bundle output | measure once, then budget |
| Images/caching | 3 | Cloudflare proxied; response cache on 11 route files; 2 raw `<img>` avatars | no `next/image`, no HTML cache | catalog/response caching; image policy |
| Pagination | 3 | `lib/pagination.ts` + 4 adopters; 12 export caps | 37 inline parsers; 3 unbounded lists | finish adoption; cap compliance/time-entries |
| N+1 risks | 2 | store-catalog N+1 fixed (`ccb8d1a6`); bulk/billing/worker fan-outs remain | sequential per-row DB calls | batch + queue bulk/billing |
| Indexes/query patterns | 4 | 316 indexes; FK-index migration `5302419`; trgm/partial indexes | exact counts; `select("*")` | opt-in counts; projections |
| Worker throughput | 3 | concurrency 10, attempts/backoff, bounded retention | per-recipient sequential writes | batch notification inserts |
| Queue concurrency | 3 | single BullMQ queue, retry/DLQ, scan lock | no per-task rate limit/priority | per-task lanes if scans grow |
| Realtime scaling | 2 | channel per SSE stream, no cap | connection/channel fan-out | shared subscription + caps |
| Webhook volume | 3 | idempotent claim, retry/DLQ, SSRF guard, 10s timeout | 10MB global ingress, no per-provider caps | per-provider size/rate limits |
| Rate limiting | 3 | 5 tiers, hashed user key, trust proxy | in-memory per process; webhook skip | Redis store before scaling out |
| Cost drivers | 2 | Supabase fan-out, Prometheus series, dynamic storefront | no cost budgets/alerts | cache + cardinality + ISR fixes |

## Detailed Review

### Item: Request metrics and Prometheus cardinality

- Evidence: `request-id.ts:41-49` labels by `req.path`; `lib/metrics.ts:7-19`; `prometheus.yml:5-6` (15s); `docker-compose.yml:224,232` (30d, 256MB).
- What it does: records every request under a label equal to the concrete URL, e.g. `/api/v1/tickets/4f2c…`.
- Current controls: retention window and memory cap only; no relabeling/recording rules; no alert on series count.
- Missing controls: route-template normalization, cardinality alert, series budget.
- Risks: unbounded TSDB growth → Prometheus OOM (monitoring blind spot) and disk growth on a 2GB droplet.

### Item: Public storefront rendering and catalog reads

- Evidence: `(public)/store/layout.tsx:5`, `(public)/store/page.tsx:20`, `catalog-source.ts:51-70`, `store/catalog.ts:24-33,86-102`, `store-catalog.ts:130-152`, SDK `client.ts:88-92`, `dns.tf:2-42`.
- What it does: every storefront view server-renders and fetches products+categories from the API; the API reads both tables from Supabase uncached.
- Current controls: Cloudflare proxy (static assets only), global IP rate limit 300/15min.
- Missing controls: response cache/ISR, ETag, per-route limits.
- Risks: bot/public traffic amplification on a 1-2 vCPU origin.

### Item: Permission resolution

- Evidence: `lib/permissions.ts:49-138`; `middleware/permissions.ts:66`; `middleware/entitlement.ts:121`; 211 call sites / 44 files.
- What it does: per gated request, resolves roles/overrides/permissions from hosted Supabase with no cache; some routes resolve twice.
- Current controls: none for permissions (entitlements have a 30s cache).
- Risks: latency and Supabase request-count cost on most writes; no invalidation point.

### Item: Bulk invite and billing sync

- Evidence: `bulk.ts:71-170` vs `app.ts:151`; `billing.ts:256-358`.
- What it does: both perform sequential, per-row network operations inside one request/task.
- Risks: 30s timeout mid-loop (partial state), stale billing data, third-party API cost.

### Item: Realtime SSE

- Evidence: `notifications.ts:47-144`; `NotificationBell.tsx:81-119`; `Caddyfile.prod:26-29`; `supabase.ts:198-226`.
- What it does: one Supabase channel + 2 change subscriptions per stream, initial unread query per connect; client polls every 30s after a stream error (cleanup leak).
- Risks: linear fan-out, reconnect storm on deploy, leaked pollers; worsens if `RLS_READS_ENABLED` gives each stream its own socket.

### Item: Worker/queue and retention

- Evidence: `env.ts:9-10`; `producer.ts:43-48`; `consumer-bullmq.ts:15-36`; `retention.ts:26,34`; `schedule-config.ts`; `main.ts:54-149`.
- What it does: concurrency 10 (configurable), 3 attempts with exponential backoff, bounded retention batches, staggered scans behind a Redis lock.
- Missing controls: per-task rate limits/priority; sequential per-recipient notification loops (`module-tasks.ts:1242-1262,1531-1553`).

### Item: Capacity and thresholds (extended check)

| Critical resource | Distance to first signal | Warning band | Failure threshold | Evidence |
|---|---|---|---|---|
| Prometheus memory/series | unknown (no series alert); first in-repo signal would be OOM/container restart | none | `mem_limit: 256m` OOM | compose:232; request-id.ts:41-49 |
| Droplet memory | ~1.5GB limits on a 2GB droplet (prod default `s-2vcpu-2gb`; dev `s-1vcpu-2gb`) | DO Monitoring (external, `unverified`) | OOM kill / swap-less stall | variables.tf:24-28; dev.tfvars.example; compose |
| Droplet disk | Docker images per deploy + 30d TSDB + capped logs (10m×3) | none in repo | disk full → deploy/pull failure | compose:19-23,224 |
| Supabase REST requests | scales with permission fan-out + exact counts + uncached catalog | none | plan quota (external, `Unknown`) | permissions.ts; catalog.ts |
| Supabase Realtime channels | one per SSE stream, no cap | none | project quota (external, `Unknown`) | notifications.ts:108-144 |
| Redis | 48MB limit; queue capped by removeOnComplete 100 / removeOnFail 500 | none | eviction/OOM under backlog | compose:51; producer.ts:43-48 |
| API memory | 256MB; unbounded lists + 10k-row exports | none | OOM kill | compose:114; tickets.ts:76 etc. |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| PERF-001 | Bundle size indicators | `next.config.mjs:57` | analyzer opt-in | no budget/gate | P3 | size-limit in CI |
| PERF-002 | SSR/client hot spots | 290 `force-dynamic` | dynamic SSR | public pages uncached | P2 | ISR/response cache |
| PERF-003 | Heavy dependencies | web package.json | lean client deps | unmeasured | P3 | measure + budget |
| PERF-004 | Images/caching | 2 raw `<img>`; Cloudflare proxied | CDN for statics | no HTML/image policy | P3 | next/image; cache headers |
| PERF-005 | Pagination | `lib/pagination.ts`; 37 inline parsers | helper + caps | unbounded compliance/time-entries | P3 | adopt helper |
| PERF-006 | N+1 risks | `bulk.ts:82-170`; `billing.ts` | batching in some paths | sequential loops remain | P2 | batch + queue |
| PERF-007 | Indexes/query patterns | 316 indexes; `5302419` | dense indexing | exact counts, `select("*")` | P3 | opt-in counts, projections |
| PERF-008 | Worker throughput | `consumer-bullmq.ts`; `retention.ts` | concurrency + batches | per-recipient loops | P3 | batch inserts |
| PERF-009 | Queue concurrency | `producer.ts:43-48` | retries/backoff/caps | no per-task lanes | P3 | priority/rate limits |
| PERF-010 | Realtime scaling | `notifications.ts:108-144` | keepalive/auth revalidation | channel per stream, no cap | P2 | shared fan-out + caps |
| PERF-011 | Webhook volume | `webhook-dispatcher.ts`; `webhook-retry.ts` | idempotency, DLQ, timeout | 10MB global ingress | P3 | per-provider limits |
| PERF-012 | Rate limiting | `app.ts:125-146`; `rate-limit.ts` | 5 tiers | in-memory; webhook skip | P3 | Redis store |
| PERF-013 | Metric cardinality | `request-id.ts:41-49` | none | unbounded series | P2 | route normalization |
| PERF-014 | Public catalog cost | `store/catalog.ts`; `catalog-source.ts` | global IP limit | no cache | P2 | cache/ISR |
| PERF-015 | Permission fan-out | `lib/permissions.ts` | none | uncached, duplicated | P2 | TTL + request memo |

## Findings

Full machine-readable detail is in `15_performance_scalability_cost.json`. Summary:

1. **Request metrics label uses the raw URL path, so Prometheus cardinality grows with every resource ID** — P2, open. `request-id.ts:41-49` + 256MB/30d Prometheus.
2. **Public storefront pages are force-dynamic and uncached; each page view costs two Supabase reads** — P2, open. Public SSR + uncached catalog.
3. **resolveEffectivePermissions is uncached and fans out 4–6 queries per gated request** — P2, still-open (verification of SEC-P3-005). 211 call sites; double resolution via entitlement middleware.
4. **Bulk invite performs 4 sequential Supabase calls per invite and cannot finish 500 invites inside the 30s request timeout** — P2, open.
5. **Each SSE notification stream opens its own Supabase Realtime channel with no connection cap** — P2, open.
6. **POST /billing/sync does not paginate Stripe results** — P2, still-open (verification of BILL-P2-002).
7. **Unbounded list reads remain on compliance and time-entry endpoints; exports load up to 10k rows with `select("*")`** — P3, open.
8. **Every paginated list request also runs an exact row count** — P3, open.
9. **No bundle-size or performance budget gate; the analyzer is opt-in only** — P3, still-open (verification of PERF-P3-001).
10. **API routes broadly select all columns and pagination is ad hoc** — P3, partially-fixed (verification of PERF-P3-002).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Prometheus OOM from series explosion | P2 | Medium | Monitoring loss during an incident | `request-id.ts:41-49`; compose:232 | route normalization + series alert |
| Public traffic amplifies DB load | P2 | Medium | Latency/cost, origin saturation | catalog routes uncached | response cache/ISR |
| Supabase latency on every gated write | P2 | High | Slow writes, request-count cost | permissions resolver | TTL cache + memoization |
| Bulk invite partial state/timeouts | P2 | Medium | Admin confusion, orphaned users | `bulk.ts`; 30s timeout | queue the batch |
| Realtime fan-out hits plan limits | P2 | Medium | Notifications degrade silently | per-stream channel | shared fan-out + cap |
| Billing data silently stale | P2 | Medium | Reconciliation/billing errors | fixed Stripe limits | cursor pagination |
| 10k-row exports spike API memory | P3 | Low | 256MB OOM under concurrency | 12 export call sites | stream/batch exports |

## Recommendations

### Immediate / Release Blocking

- None (no P0/P1 findings).

### This Week

- Normalize the HTTP metric route label and add a `prometheus_tsdb_head_series` alert (P2 #1).
- Add `responseCache` to public catalog routes as a stopgap before the ISR change (P2 #2).
- Add a TTL + request-scoped memo to permission resolution (P2 #3).

### This Month

- Move bulk invite to a worker job with a bounded synchronous batch (P2 #4).
- Fix the SSE polling-fallback cleanup and add a per-process stream cap with jittered reconnect (P2 #5).
- Paginate Stripe with `starting_after` and batch upserts (P2 #6).
- Add a web bundle budget gate in CI (P3 #9).

### Later / Platform Evolution

- ISR/on-demand revalidation for public store pages; streaming exports.
- Shared realtime fan-out (single subscription → local SSE broadcast) before enabling RLS reads for notifications.
- Redis-backed rate-limit store when a second API replica is added.
- Per-task queue lanes/rate limits as scheduled scans grow.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Route-label normalization | bounds Prometheus series | `middleware/request-id.ts`, `lib/metrics.ts` | unit test asserting bounded labels |
| Catalog response cache | removes 2 Supabase reads/view | `routes/store/catalog.ts` | test asserting `X-Cache: HIT` |
| Permission request memo | halves gated-request fan-out | `middleware/permissions.ts`, `middleware/entitlement.ts` | request test with query counter |
| Opt-in exact counts | removes a count scan per list | list routes | API test on `?withTotal` |
| SSE fallback cleanup fix | stops leaked pollers | `components/NotificationBell.tsx` | component test with fake EventSource |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Metric cardinality budget + alert | P2 | observability owner | S | none |
| Public catalog cache/ISR | P2 | @web + API | M | cache invalidation on catalog writes |
| Permission cache with invalidation | P2 | API principal | M | membership/role write hooks |
| Bulk invite jobification | P2 | API principal | M | worker task + progress API |
| Realtime fan-out redesign | P2 | API principal | L | load test harness |
| Stripe pagination + batching | P2 | billing/backend | S-M | none |
| Pagination adoption sweep | P3 | @api | M | lint rule |
| Export streaming | P3 | API principal | M | download-artifact flow |
| Redis rate-limit store | P3 | platform | S | Redis already present |

## Suggested Tests

- Unit: metric label normalizer maps `/api/v1/tickets/<uuid>` → `/api/v1/tickets/:id` and unknown paths to a bounded bucket.
- Integration: second GET of `/api/v1/store/products` returns `X-Cache: HIT`; catalog admin write invalidates it.
- Integration: a permission-gated route issues at most 1 permission-resolution query set per request (query counter/spy).
- Integration: `POST /bulk/invite` with the max batch returns within budget (or returns a job id).
- Regression: SSE error path clears its polling interval on unmount (fake EventSource).
- CI: size-limit budget job for `apps/web`; Prometheus rule test for a series-count alert.
- Manual: run the bundle analyzer once and commit the baseline to `docs/PERFORMANCE.md`.

## Suggested Documentation Updates

- `docs/PERFORMANCE.md`: update the "Admin list endpoints … no page pulls whole tables" claim (only 4 route files use the helper; 3 endpoints remain unbounded); add the metric-cardinality rule; document the permission-cache design once added; refresh the index count (doc says 313, current grep: 316).
- Add a "performance budgets" section (bundle size, p95 API latency, Prometheus series count) to `docs/PERFORMANCE.md` or `docs/CI.md`.
- Document the realtime scaling model and caps (SSE connections, Supabase channels) in `docs/MONITORING_AND_ALERTING.md` or `docs/PERFORMANCE.md`.
- Document droplet scale-up triggers (memory/disk/series thresholds) in `infra/digitalocean/README.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What are the Supabase plan quotas (REST requests, Realtime connections/channels)? | Determines how close the fan-out is to failure | Supabase dashboard/plan export |
| What is the current Prometheus series count and TSDB size? | Distance to the 256MB OOM | `docker exec prometheus` query (not run; read-only audit) |
| Are DigitalOcean Monitoring alerts configured for memory/disk on the droplet? | First signal for the capacity table | DO account settings |
| What are actual CI build/test durations? | Build-cost budget | Actions run logs |
| How many concurrent SSE clients exist in practice? | Realtime design urgency | API metrics (none currently for open streams) |
| Is `RLS_READS_ENABLED` planned for notifications? | Changes SSE from shared socket to per-stream socket | deploy env + rollout plan |

## Appendix

- Previous PERF rows re-checked: `PERF-P3-001` (still-open), `PERF-P3-002` (partially-fixed); cross-domain subject-matter rows `SEC-P3-005` (still-open, re-rated P2 for PERF) and `BILL-P2-002` (still-open). No previous PERF row regressed.
- Strong patterns worth preserving: `retention.ts` bounded batches with truncation reporting; `webhook-dispatcher.ts` atomic per-endpoint idempotency claim; `orphan-cleanup.ts` recursive listing with caps; `cache.ts` SCAN-based invalidation and memory-entry cap; `schedule-config.ts` distinct staggered offsets + `offsetsAreDistinct()` guard; CI shared composite actions preventing workflow drift.
- No secrets observed in reviewed performance-relevant files.
