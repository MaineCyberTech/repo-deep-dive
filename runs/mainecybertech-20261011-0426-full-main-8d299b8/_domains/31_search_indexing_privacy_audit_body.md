# Search, Indexing, and Privacy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (portal monorepo, target worktree `/tmp/opencode/mct-audit-target`)
- Branch: `main` (detached at `HEAD`)
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (`8d299b8d`)
- Generated at: 2026-10-11
- Auditor: subagent, prompt 31
- Area code: SEARCH
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/31_search_indexing_privacy_audit.md`
- Scope limitations:
  - Static, read-only review of the working tree at 8d299b8d. No database, hosted Supabase, or production access; RLS/PostgREST behavior is inferred from SQL/TypeScript.
  - `RLS_READS_ENABLED` / `RLS_WRITES_ENABLED` runtime values are not committed; allow-lists are assumed empty unless stated (services/supabase.ts:203-209).
  - No external search provider, indexing job, or reindexing scheduler exists, so those scope rows are `not applicable` rather than unknown.
  - Frontend behavior (React components) was read, not executed; no browser session was used.

## Scope

Reviewed:

- Search API: `apps/api/src/routes/search.ts` (admin global), `apps/api/src/routes/search-portal.ts` (portal), `apps/api/src/lib/search.ts` (`sanitizeSearchTerm`), `apps/api/src/lib/query.ts`.
- Authorization chain: `apps/api/src/middleware/auth.ts`, `admin.ts`, `org-access.ts`, `permissions.ts`, `apps/api/src/lib/roles.ts`, `apps/api/src/services/supabase.ts` (`getScopedClient`), `apps/api/src/services/audit.ts`.
- Search surfaces/UI: `apps/web/components/admin/AdminGlobalSearch.tsx`, `apps/web/components/portal/PortalGlobalSearch.tsx`, `apps/web/components/admin/AdminListPageSearch.tsx`, `apps/web/e2e/admin/search.spec.ts`.
- SDK/contracts: `packages/sdk/src/search.ts`, `apps/api/src/openapi/spec.ts` (Search tag), `docs/API_ENDPOINT_INVENTORY.md`.
- Indexes/data: `supabase/migrations/5302102_add_performance_indexes.sql`, `5302432_drop_unused_soft_delete_columns.sql`, `5302110_restore_document_permissions.sql`, `5302118_permission_matrix_full_catalog.sql`.
- Logs/analytics/retention: `apps/api/src/lib/metrics.ts`, `apps/api/src/routes/analytics.ts`, `apps/worker/src/tasks/retention.ts`, `docs/MONITORING_AND_ALERTING.md`.
- Tests: `apps/api/src/__tests__/search.test.ts`, `search-tenant-scope.test.ts`, `search-portal.test.ts`, `sanitize-search.test.ts`, `packages/sdk/src/__tests__/sdk-expanded.test.ts`.
- Adjacent `ilike` list filters that do NOT use the shared sanitizer: `assets.ts`, `proposals.ts`, `findings.ts`, `staging.ts`, `device-profiles.ts`, `domain-monitors.ts`, `network-diagrams.ts`, `vendors.ts`, `approvals.ts`.

Not reviewed / not applicable:

- Live EXPLAIN plans, index selectivity, and PostgREST parser behavior (no DB).
- External index providers (none exist), indexing/reindex jobs (none exist), vector/RAG retrieval (none).
- The full audit-log reader UI and retention of non-search stores (owned by prompts 06/18/37).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/routes/search.ts:16` | Source | Admin search auth chain | `requireAuth, requireAdmin, requireOrgAccess` |
| `apps/api/src/routes/search.ts:28` | Source | Pagination | `?limit` default 5, hard cap 25 |
| `apps/api/src/routes/search.ts:38-70` | Source | Tenant/PII scoping | memberships + `is_super_admin`; all-tenants requires both |
| `apps/api/src/routes/search.ts:84-99` | Source | PII projection + user scope | email/phone only for all-tenants; `__none__` fail-closed |
| `apps/api/src/routes/search.ts:137-147` | Source | Document search | org filter only; no visibility filter |
| `apps/api/src/routes/search.ts:153-163` | Source | Organizations scope | `.in("id", scopedOrgIds)` unless all-tenants |
| `apps/api/src/routes/search.ts:191-213` | Source | Search audit + metric | SHA-256 fingerprint; `recordSearchQuery()` |
| `apps/api/src/routes/search.ts:215-231` | Source | Response shape | arrays + `counts` + `limit` |
| `apps/api/src/routes/search-portal.ts:9-59` | Source | Portal search | `requireAuth` only; tickets/projects; `.limit(5)` |
| `apps/api/src/lib/search.ts:22-33` | Source | Sanitizer | strips `,()."\%*`; 100-char cap |
| `apps/api/src/middleware/admin.ts:46-58` | Source | Org-pinned admin check | needs `req.orgScope` set by upstream middleware |
| `apps/api/src/middleware/org-access.ts:43-60` | Source | Cross-tenant grant | `admin` key grants any org, logs impersonation |
| `supabase/migrations/5302110_restore_document_permissions.sql:39-107` | Migration | Document visibility | `can_read_document` + select policy |
| `supabase/migrations/5302432_drop_unused_soft_delete_columns.sql:17-31` | Migration | Deleted-data removal | drops `deleted_at`/`deleted_by` |
| `supabase/migrations/5302102_add_performance_indexes.sql:10-16` | Migration | Search indexes | 7 GIN trigram indexes; slug/documents.name unindexed |
| `apps/api/src/lib/metrics.ts:68-72,218-220` | Source | Search metric | `portal_search_queries_total` + recorder |
| `apps/api/src/routes/analytics.ts:84` | Source | Analytics RPC | `get_analytics_summary` (undefined in SQL) |
| `apps/web/components/admin/AdminGlobalSearch.tsx:7-70` | Source | Admin UI | no `documents`, no counts |
| `packages/sdk/src/search.ts:4-26` | SDK | Client contract | admin type lacks documents/counts/limit |
| `apps/api/src/openapi/spec.ts:976-987` | Contract | OpenAPI | only `q` documented |

## Verification Performed

| Command (at `/tmp/opencode/mct-audit-target`) | Observed result |
|---|---|
| `git rev-parse HEAD` | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (matches run manifest) |
| `grep -rn "recordSearchQuery" apps/api/src` | Definition at `metrics.ts:218`; only call site `search.ts:213` (plus a test mock) — portal route unwired |
| `grep -rn "get_analytics_summary" supabase/` | `NO MATCHES` — the RPC called by `analytics.ts:84` is still undefined |
| `grep -rn "deleted_at" apps/api/src` | `NO MATCHES` — no runtime reads/writes of soft-delete columns |
| `grep -n "limit" apps/api/src/routes/search.ts apps/api/src/routes/search-portal.ts` | Admin: `:28` clamp + `.limit(limit)` at 5 sites; portal: `.limit(5)` at `:42,48` |
| `grep -rn "tsvector" supabase/ apps/api/src` | `NO MATCHES` — no full-text search |
| `grep -rin "meilisearch\|algolia\|elasticsearch\|typesense" apps packages supabase` | `NO MATCHES` — no external search provider |
| `grep -rn "organizations.*slug\|idx_organizations" supabase/migrations/*.sql` (filtered to index lines) | Only `idx_organizations_name_trgm`; no index on `organizations.slug` |
| `grep -n "documents" apps/web/components/admin/AdminGlobalSearch.tsx` | `NO documents IN ADMIN UI` — API array discarded |
| `sed -n '16p' apps/api/src/routes/search.ts` vs `sed -n '22p' apps/api/src/routes/audit.ts` | `requireAuth, requireAdmin, requireOrgAccess` vs `requireAuth, requireOrgAccess, requireAdmin` — ordering differs |
| `grep -n "replace(/\|MAX_SEARCH_TERM" apps/api/src/lib/search.ts` | Strip set `/[,()."\\%*]/g`; cap 100 |
| `grep -rn "get_analytics_summary\|search" docs/MONITORING_AND_ALERTING.md` | `:132` still marks `portal_search_queries_total` 'defined, not wired' |

Reproduction notes: all headline claims above were reproduced from source at 8d299b8d; no claim relies on the previous run. Live PostgREST/RLS behavior remains `not reproducible` in this read-only environment.

## Executive Summary

Search is a Postgres-native, real-time implementation: two authenticated REST endpoints (`GET /api/v1/search`, `GET /api/v1/search/portal`) issue `ilike`/`.or()` filters against Supabase, accelerated by GIN trigram indexes. There is no external index, indexing job, reindexing scheduler, `tsvector` column, or dedicated autocomplete endpoint, so stale-index and index-deletion problems do not exist by construction; the privacy questions are what is queried, returned, logged, and retained.

Strengths verified at this commit:

1. The sanitizer now strips every PostgREST grammar token (`.`, `,`, `()`, quotes, `\`, `%`, `*`) and caps length at 100 with regression tests (`lib/search.ts:22-33`, `sanitize-search.test.ts:32-64`).
2. Admin search scopes organizations to the caller's orgs, gates `email`/`phone` to a true platform admin, fails closed on an empty scope, and audits the all-tenants path (`search.ts:38-99,153-163`; tests `search.test.ts:173-203`, `search-tenant-scope.test.ts:136-225`).
3. Search terms are no longer persisted in plaintext: only a truncated SHA-256 fingerprint and length reach `audit_logs` (`search.ts:191-211`).
4. Admin search gained `?limit` (default 5, cap 25) and per-entity exact counts (`search.ts:28,103-155,222-231`), and the search counter is now incremented (`search.ts:213`).
5. Soft-delete columns were dropped, so deleted rows cannot silently become searchable later (`5302432`).

Material gaps at this commit:

1. **Private documents remain searchable** — the admin documents query filters only by organization and runs on the service-role client, so any tenant `admin` can discover `private`/`internal` document names that `can_read_document` would hide elsewhere. New finding.
2. **Cross-tenant search via explicit org** — because `requireAdmin` runs before `requireOrgAccess`, the org-pin never applies; a tenant admin can request another tenant's `organization_id` and read its search results (impersonation-audited), while `audit`/`bulk` deny the same pattern. New finding.
3. **Pagination fix is API-only** — portal search, both UIs, the SDK, and OpenAPI still assume 5 results with no counts; the `count: 'exact'` cost was not measured.
4. **Portal search remains the weakest surface** — no documents (SDK/doc contract still promises them), no metric, no audit, hard `.limit(5)`.
5. **Docs and contracts are stale** — module docs still say "across all organizations", attribute the portal route to the wrong file, and mark the search metric dead.

Recommended next actions: (a) filter admin-search documents by the visibility model; (b) align the search router's middleware order with `audit.ts` or document `admin` as cross-tenant; (c) finish the pagination rollout (portal + UI + SDK/OpenAPI); (d) add indexes for `organizations.slug` and `documents.name`; (e) refresh the search docs. None of the new items is a P0.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Admin global search route | `apps/api/src/routes/search.ts` `GET /api/v1/search` | Cross-entity admin search | Implemented | High | users/orgs/tickets/projects/documents; `?limit`+counts |
| Portal search route | `apps/api/src/routes/search-portal.ts` `GET /api/v1/search/portal` | Org-scoped search | Implemented | Medium | tickets/projects only; no counts |
| Search sanitizer | `apps/api/src/lib/search.ts` `sanitizeSearchTerm` | PostgREST filter safety | Implemented | Low | strips `.`/`*`; 100-char cap |
| Admin search UI | `apps/web/components/admin/AdminGlobalSearch.tsx` | Typeahead UI | Implemented | Medium | drops `documents`, ignores counts |
| Portal search UI | `apps/web/components/portal/PortalGlobalSearch.tsx` | Typeahead UI | Implemented | Low | 300 ms debounce |
| SDK search API | `packages/sdk/src/search.ts` | Client contract | Stale | Medium | no documents/counts/limit on admin type |
| GIN trigram indexes | `supabase/migrations/5302102_add_performance_indexes.sql:10-16` | Fuzzy text search perf | Implemented | Medium | slug, documents.name/mime_type missing |
| Soft-delete columns | `5302109` (add) / `5302432` (drop) | Tombstoning | Removed | Low | product decision = hard delete |
| Encrypted PII mirror | `supabase/migrations/5302135_profiles_encrypted_pii.sql` | PII at rest | Implemented | Medium | plaintext columns remain the search source |
| Search metric | `apps/api/src/lib/metrics.ts:68-72` | Search volume | Partially wired | Low | only admin route increments it |
| Analytics summary RPC | `apps/api/src/routes/analytics.ts:84` | Admin analytics | Missing RPC | Medium | `get_analytics_summary` undefined in SQL |
| Audit retention | `apps/worker/src/tasks/retention.ts:13,131` | Purge audit/notifications | Implemented | Low | 365 d / 90 d; search audit rows included |
| External index / indexing job / reindex | — | — | Absent | — | Not applicable (document the decision) |
| Autocomplete endpoint | — | — | Absent | Medium | debounced full search used instead |
| `search.view` permission | `supabase/migrations/5302118:339` | Catalog entry | Unused | Low | route relies on `requireAdmin` only |

### Indexed data inventory (owner / retention / cleanup)

| Table / index | Owner | Retention / cleanup | Notes |
|---|---|---|---|
| `profiles` (`idx_profiles_full_name_trgm`, `idx_profiles_email_trgm`) | platform/data | No table retention; PII mirror `5302135` | Searchable columns are plaintext |
| `organizations` (`idx_organizations_name_trgm`) | platform/data | No retention | `slug` searched, unindexed |
| `tickets` (`idx_tickets_title_trgm`, `idx_tickets_description_trgm`) | platform/data | Hard delete on DELETE | No tombstone after `5302432` |
| `projects` (`idx_projects_name_trgm`, `idx_projects_description_trgm`) | platform/data | Hard delete | — |
| `documents` (no trigram on `name`) | platform/data | Hard delete + storage object removal | `name`/`mime_type` searched, unindexed |
| `audit_logs` (`idx_audit_logs_org_created`, `idx_audit_logs_entity`) | platform/security | 365-day purge (`retention.ts:13,131`) | Search audit rows land here (hash only) |
| `document_permissions` (`idx_document_permissions_user_id/_role_id`) | platform/security | Cascade with document | Backs `can_read_document` |

Leftovers without a documented retention policy (tickets/projects/documents/profiles) are tracked by DATA-P2-006 and not duplicated here.

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Search routes/UI | 3 | `search.ts`, `search-portal.ts`, both `*GlobalSearch.tsx` | Admin UI drops documents/counts; portal unchanged | Render documents; surface counts |
| Indexes | 2 | `5302102:10-16` | `organizations.slug`, `documents.name` unindexed; no btree/tsvector | Add indexes; measure |
| Indexing jobs | N/A | No worker/external index found | None | Document the real-time decision |
| Indexed fields | 2 | route `.select()` lists | Private docs searchable; email predicate for non-super callers | Visibility-aware filtering |
| Tenant filters | 3 | `search.ts:77-99,153-163`; `search-portal.ts:23-40` | Explicit-org path bypasses the admin pin | Fix middleware order or document model |
| Permission filters | 2 | `requireAdmin` only; `search.view` unused | No field-level or per-role projection beyond PII | Consider `requirePermission` |
| Document/ticket/project/message search | 2 | `search.ts:113-147`; `search-portal.ts:36-49` | Portal misses documents; no message search | Add docs to portal; state message scope |
| Admin/global search | 3 | `search.ts` | Private-doc exposure; cross-tenant explicit-org path | See new findings |
| Autocomplete | 2 | debounced full endpoints | No dedicated endpoint; no search-specific limit/cache | Add lightweight endpoint or limiter |
| Search logs | 3 | `search.ts:191-211` | Portal search unlogged; audit rows lack org id | Log portal (hashed); set org |
| Query analytics | 2 | `metrics.ts`, `search.ts:213`, `analytics.ts:84` | Portal unwired; RPC missing; docs stale | Wire + implement RPC |
| Deleted data removal | 4 | `5302432`; hard deletes | Dead UI fallbacks | Clean up fallbacks |

## Detailed Review

### Item: Admin global search (`GET /api/v1/search`)

- Evidence: `search.ts:16-231`; tests `search.test.ts`, `search-tenant-scope.test.ts`.
- What it does: authenticated admin search over profiles, organizations, tickets, projects, documents; min 2 chars; `?limit` (default 5, cap 25) + per-entity exact counts.
- Current controls: role gate; membership-derived org scope with `__no_match__` fail-closed; PII gated to super admins; hashed audit; metric.
- Missing controls: document-visibility filtering; consistent org-pin semantics; SDK/OpenAPI/UI alignment.
- Risks: private-document discovery (new finding), cross-tenant explicit-org reads (new finding), dead-end pagination payload.

### Item: Portal search (`GET /api/v1/search/portal`)

- Evidence: `search-portal.ts:9-59`; tests `search-portal.test.ts:51-115`.
- What it does: membership-derived org filter over tickets/projects; hard `.limit(5)`; no counts; no audit/metric.
- Current controls: `requireAuth`; app-level `.in("organization_id", orgIds)`; empty membership short-circuits.
- Missing controls: documents, pagination, audit/metric, RLS by default (`getScopedClient` falls back to service role unless `search-portal` is allow-listed; bypass is now recorded via `recordRlsBypass`).
- Risks: contract drift; weakest observability of the two endpoints.

### Item: Query sanitizer

- Evidence: `lib/search.ts:22-33`; tests `sanitize-search.test.ts:3-69`.
- What it does: replaces `,()."\%*` with spaces, collapses whitespace, caps 100 chars; dots are intentionally unsearchable.
- Controls: unit-tested injection strings; used by search, search-portal, knowledge-base, edu-automation.
- Residual: other list routes (`assets`, `proposals`, `findings`, …) use raw `.ilike()` values without the sanitizer; those values are passed as method arguments (not interpolated into `.or()`), so no grammar injection, but `%`/`_` wildcards pass through and results are still org-scoped.

### Item: Indexes and query performance

- Evidence: `5302102:10-16`; `search.ts:29-30,140,156`.
- Gap: no index for `organizations.slug` or `documents.name`/`mime_type`; prefix columns use trigram; no `tsvector`; `count: 'exact'` on five parallel queries adds cost.

### Item: Deleted data and retention

- Evidence: `5302432:17-31`; `retention.ts:13,131`.
- State: hard deletes; soft-delete columns removed; search audit rows (hash only) purge after 365 days.
- Residual: dead `deleted_at` probes in web components.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEARCH-001 | Search routes/UI | `search.ts`, `search-portal.ts`, UIs | Auth(+admin) gates | UI drops documents/counts | P2 | Finish UI rollout |
| SEARCH-002 | Indexes | `5302102` | GIN trigram | slug/documents.name unindexed; no tsvector | P2 | Add indexes |
| SEARCH-003 | Indexing jobs | none found | N/A (real-time) | Decision undocumented | P3 | Document |
| SEARCH-004 | Indexed fields | route selects | PII gated to super admin | Private docs searchable; email predicate | P2 | Visibility-aware filter |
| SEARCH-005 | Tenant filters | `search.ts:77-163` | Membership-derived, fail closed | Explicit-org path bypasses admin pin | P2 | Middleware order/pin |
| SEARCH-006 | Permission filters | `search.ts:16`; `5302118:339` | `requireAdmin` | `search.view` unused | P3 | Optional `requirePermission` |
| SEARCH-007 | Document/ticket/project/message search | `search.ts`, `search-portal.ts` | Docs in admin only | Portal docs; no message search | P2 | Add docs or fix contract |
| SEARCH-008 | Admin/global search | `search.ts` | Scoped + audited | New P2 findings | P2 | See findings |
| SEARCH-009 | Autocomplete | UI components | Global limiters | No dedicated endpoint/cache | P2 | Lightweight endpoint |
| SEARCH-010 | Search logs | `search.ts:191-211` | Hashed admin audit | Portal unlogged; no org id | P2 | Log portal |
| SEARCH-011 | Query analytics | `metrics.ts`, `analytics.ts:84` | Admin counter wired | Portal unwired; RPC missing | P2 | Wire + RPC |
| SEARCH-012 | Deleted data removal | `5302432` | Hard delete | Dead UI fallbacks | P3 | Cleanup |

## Findings

Titles only; IDs/areas are assigned by the aggregator. Full evidence and status live in `_domains/31_search_indexing_privacy_audit.json`.

Verification rows (re-checked at 8d299b8d):

- `sanitizeSearchTerm` does not strip PostgREST `.` operator separators — **verified-fixed**.
- Admin global search exposes profile PII and never tenant-scopes the organizations query — **verified-fixed** (residual: email predicate remains for non-super callers).
- Raw search terms persisted in plaintext `audit_logs.metadata` — **verified-fixed**.
- Portal search omits documents despite SDK and documentation contract — **still-open**.
- Admin search UI silently discards the documents result set — **still-open**.
- No search pagination or result counts; hard 5-result ceiling — **partially-fixed** (admin API only).
- Search query analytics metric is dead and the analytics summary RPC is missing — **partially-fixed** (admin metric wired; RPC and portal still missing).
- Prefix/wildcard mismatch: no btree on prefix columns and no full-text (`tsvector`) search — **still-open**.
- Typeahead calls full search endpoints without rate limiting or a dedicated autocomplete surface — **partially-fixed** (global limiters only).
- Soft-delete columns are defined but never used by queries or deletes — **verified-fixed** (columns dropped).
- Search module documentation is stale relative to the code — **still-open**.

New findings (open at 8d299b8d):

- Admin global search returns private/internal documents without applying the `can_read_document` visibility filter — **P2**.
- Search router bypasses the org-pinned admin check, so a tenant admin can read another tenant's search results — **P2**.
- Search SDK and OpenAPI contracts do not cover the implemented response (documents, counts, limit) — **P3**.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Private/internal document names discoverable via admin search | P2 | Medium | Within-tenant metadata disclosure; breaks visibility model | `search.ts:26,137-147`; `5302110:39-107` | Visibility-aware filter |
| Tenant admin reads another tenant's search results via `?organization_id` | P2 | Medium | Cross-tenant read (audited) inconsistent with audit/bulk | `search.ts:16`; `admin.ts:46-58`; `org-access.ts:43-60` | Fix ordering/pin or document model |
| Search latency grows with unindexed slug/name scans and exact counts | P2 | Medium | Slower search as data grows | `5302102`; `search.ts:140,156` | Add indexes; measure |
| Contract drift misleads SDK consumers/agents | P3 | High | Wasted integration effort; false assumptions | `sdk/search.ts`; `openapi/spec.ts:976-987`; docs | Sync contracts |
| Typeahead amplification under abuse | P3 | Low | DB load spikes (bounded by global limiters) | `app.ts:125-146`; UI debounce | Search-specific limit/cache |

## Recommendations

### Immediate / Release Blocking

None. No P0 and no P1-remains-open in this domain.

### This Week

1. Fix the admin-search documents query to respect the visibility model (or require `documents:manage` plus a `private` filter); add a regression test.
2. Align the search router's middleware order with `audit.ts`/`bulk.ts` (or explicitly document `admin` as cross-tenant); add a tenant-admin/foreign-org test.

### This Month

3. Extend `?limit`/counts to `search-portal.ts`; document `limit` in OpenAPI; add an optional limit to the SDK.
4. Wire the portal search metric and a hashed audit event; implement or replace `get_analytics_summary` (SEC-P2-004).
5. Add indexes for `organizations.slug` and `documents.name`; measure `count: 'exact'` cost at volume.

### Later / Platform Evolution

6. Decide the documents contract (portal + UI + SDK + docs) once, then add a contract test.
7. Evaluate a dedicated autocomplete endpoint and a `tsvector`-based ranked search; document the "no external index" decision.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Render `documents` + counts in admin UI | Delivers existing API work end-to-end | `AdminGlobalSearch.tsx` | Unit/E2E assertion |
| Fix module docs | Removes agent/operator misinformation | `docs/modules/search.md`, `search-portal.md`, `API_ENDPOINT_INVENTORY.md` | Doc review |
| Mark search metric 'live (admin)' | Stops stale monitoring guidance | `docs/MONITORING_AND_ALERTING.md:132` | Doc review |
| Add `queryParam("limit")` to OpenAPI | Cheap contract fix | `openapi/spec.ts:976-987` | Spec build |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Visibility-aware document search | P2 | search/backend + security | S | Product visibility decision |
| Org-pin/middleware-order alignment | P2 | API platform | S | CHAIN-P1-001 model decision |
| Portal pagination + counts | P2 | search/backend | S | none |
| Portal search audit + metric | P2 | search/backend + SRE | S | none |
| Index `organizations.slug`, `documents.name` | P2 | data/platform | S | migration review |
| SDK/OpenAPI contract sync + tests | P3 | SDK + API platform | S–M | SEARCH-P2-002 decision |
| Dedicated autocomplete endpoint | P3 | search/backend + web | M | none |

## Suggested Tests

- Unit: keep the sanitizer injection suite; add a case asserting the term never contains `.`/`,`/`*` before interpolation.
- Integration: tenant-admin search with a foreign `organization_id` returns 403 or empty (new finding); private document not returned to a non-granted admin (new finding).
- Integration: `?limit` bounded (0/negative/999) and counts match seeded totals; portal `?limit` once implemented.
- Contract: SDK/OpenAPI response-shape test against the route payload (documents/counts/limit).
- Security/regression: search audit metadata contains no raw term (exists); portal search emits a metric/audit once wired.
- Manual: with `RLS_READS_ENABLED=search-portal`, confirm a member of Org A cannot match Org B tickets.

## Suggested Documentation Updates

- `docs/modules/search.md` — documents, org scoping, PII gating, `?limit`/counts, hashed audit.
- `docs/modules/search-portal.md` — correct route file, documents contract decision, metric/audit status.
- `docs/API_ENDPOINT_INVENTORY.md:163-164` — correct auth gates and entity lists.
- `docs/MONITORING_AND_ALERTING.md:132` — mark the search metric wired (admin) and note the RPC status.
- New: a short "search data map" (searchable columns, visibility model, retention) for operators/agents.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Should `admin` be cross-tenant for search reads? | Determines whether the explicit-org path is a bug or the model | Owner decision (CHAIN-P1-001/ADMIN-P1-001) |
| Should admin search return private documents to any tenant admin? | Visibility model consistency | Product/security decision |
| Are exact per-entity counts acceptable at production volume? | Query cost on 5 parallel queries | EXPLAIN/load measurement |
| Is portal documents search in scope for the product? | Drives SDK/doc vs implementation alignment | Product decision |
| Is `RLS_READS_ENABLED` configured for `search-portal` in prod? | Defense-in-depth for tenant isolation | Droplet `.env` (operator) |

## Appendix

Search surface inventory:

| Surface | Method/route | Gate | Tenant filter | Notes |
|---|---|---|---|---|
| Admin global | `GET /api/v1/search` | `requireAuth, requireAdmin, requireOrgAccess` | memberships/orgScope; `__no_match__` fail-closed | documents unscoped by visibility |
| Portal | `GET /api/v1/search/portal` | `requireAuth` | membership org ids; empty → empty result | no audit/metric |
| KB list | `GET /api/v1/knowledge-base` | router auth | org query param | uses sanitizer |
| EDU KB search | `GET /api/v1/edu-automation/kb/search` | router auth | scoped client | uses sanitizer |
| List filters (9 routes) | e.g. `GET /api/v1/assets?search=` | router auth | route-specific org filter | raw `.ilike` values, no sanitizer |

Authorization review summary: all search filters are constructed server-side; no client-supplied scope is trusted (portal derives orgs from memberships; admin derives from `req.orgScope`/memberships). The two open scoping gaps are the document-visibility filter and the explicit-org admin pin.

Privacy tests (existing): sanitizer injection suite; admin scoping/PII projection tests; audit-metadata test asserting no raw term. Missing: document-visibility search test; cross-tenant explicit-org test; portal metric/audit test.
