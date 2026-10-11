# 19_platform_evolution_extensibility — Prompt 19 - Platform Evolution and Extensibility Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `19_platform_evolution_extensibility.md` (area EVOL, prompt)

## Verification Performed

# Platform Evolution and Extensibility Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `github.com/MaineCyberTech/mainecybertech` (read-only worktree `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8d` (merge PR #168, 2026-10-11)
- Generated at: 2026-10-11
- Auditor: domain subagent (area EVOL), full-hardening rerun
- Area code: EVOL
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/19_platform_evolution_extensibility.md`
- Scope limitations: static read-only review. Node.js is not installed on the audit host, so repository scripts (openapi-audit, guards) could not be executed; findings rest on source/config reading plus Python extraction of literals. No application or database was run; no production systems were touched.

## Scope

Reviewed for evolution/extensibility: module boundaries, domain model, shared packages, extension points, feature flags, permission extensibility, tenant/org model, API versioning, migration strategy, eventing/webhooks, integration framework, UI reuse, admin tooling, background jobs, config model, observability extensibility, docs for adding modules, AI-agent compatibility, package extraction.

Not reviewed in depth (owned by other domains in this run): RBAC correctness itself (ACM), webhook delivery/idempotency semantics (WH), RLS policy content (RLS/DATA), release/changelog process (REL), CI/supply chain (CI/SC). Cross-domain rows re-verified here are marked as such.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/app.ts:174-233` | Source | Module boundary / mounting | 60 `/api/v1/*` prefixes mounted by hand |
| `packages/sdk/src/index.ts:347-421` | Source | Extension point | `MCTClient` declares 55 sub-APIs, hand-wired |
| `apps/web/lib/navigation/portal-nav.ts`, `admin-nav.ts` | Source | Module catalog | 63 portal / 57 admin module keys |
| `apps/web/lib/module-config.ts:25-748` | Source | UI reuse / module config | Per-module CRUD UI descriptors |
| `apps/web/lib/permissions.ts:45-133` | Source | Permission labels | 41 labels vs 94 catalog module keys |
| `apps/api/src/lib/entitlements.ts:21-41` | Source | Plan/module model | Default vs subscription sets; `support` key drift |
| `apps/api/src/middleware/entitlement.ts` | Source | Extension point | `requireEntitlement` on 6 gated routers |
| `apps/api/src/lib/permissions.ts`, `middleware/permissions.ts` | Source | Permission extensibility | Data-driven resolution + overrides |
| `supabase/migrations/5302118_permission_matrix_full_catalog.sql` | Migration | Permission catalog | 94 module keys, role assignments |
| `supabase/migrations/5302128_role_catalog_expansion.sql:30` | Migration | Role catalog | Hardcoded role keys |
| `apps/api/src/lib/feature-flags.ts:1-15` | Source | Feature flags | Static map + env overrides; no consumers |
| `apps/api/src/routes/webhook-management.ts:43-49`, `lib/webhook-dispatcher.ts:159-162` | Source | Eventing | Free-form events, `.contains` filter |
| `apps/api/src/routes/projects.ts:522`, `tickets.ts:183`, `store/quotes.ts:536` | Source | Eventing | Only `project.created` / `ticket.created` emitted |
| `apps/web/components/admin/NewWebhookForm.tsx:6-18`, `WebhookDetailClient.tsx:8-20` | Source | Eventing UI | Duplicated 11-event lists |
| `apps/worker/src/task-registry.ts`, `tasks/index.ts`, `schedule-config.ts` | Source | Extension point / jobs | `registerTask` + scheduled scan table |
| `apps/api/src/routes/final/crud.ts:25-183`, `governance.ts:38-80`, `field-services.ts:26-44`, `vendors.ts`, `security-suite.ts`, `security-ops.ts`, `batch.ts` | Source | Extension points | Route factories (`registerCrud`, `crudRoute`, `crudEndpoints`) |
| `apps/api/src/routes/store.ts` | Source | Module boundaries | `register*Routes` split pattern |
| `docs/API_VERSIONING.md`, `apps/api/src/openapi/spec.ts:4797` | Docs/Code | API versioning | Policy vs implementation |
| `docs/SUPABASE_MIGRATION_WORKFLOW.md`, `docs/migrations/naming-guide.md`, `docs/SUPABASE_MIGRATION_CHEATSHEET.md` | Docs | Migration strategy | Contradictory conventions |
| `supabase/migrations/` (134 files) | Migrations | Schema evolution | All `5302xxx` sequential |
| `apps/api/src/config/env.ts`, `apps/worker/src/env.ts`, `apps/web/lib/env.ts`, `packages/config/package.json` | Source | Config model | Three separate env schemas |
| `packages/sdk/package.json`, `packages/ui/package.json`, `apps/api/src/services/supabase.ts`, `apps/worker/src/services/supabase.ts`, `docs/arch/evaluation/db-package-evaluation.md` | Source/Docs | Package extraction | Source-only packages; DB duplication |
| `docs/adr/README.md` (008–011), `docs/module-matrix-mapping.md`, `docs/modules/*` (75 files) | Docs | ADRs / module docs | Decision records + module docs |
| `docs/ui-kit.md`, `packages/ui/src/components/*` | Docs/Source | UI reuse | Shared kit + app-local generics |
| `AGENTS.md`, `review.md`, `prompts/PROVENANCE.md`, `scripts/verify-prompts.js` | Docs/Tooling | AI-agent compatibility | Pinned prompts, guarded mirror |
| `.github/actions/unit-tests/action.yml:30-63` | CI | Guard inventory | Every repo guard; no permission lint |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log -1` on target | Command | Commit binding | `8d299b8d` confirmed; `9c0b88c` is an ancestor |
| `git diff --stat 9c0b88c..HEAD -- apps/api/src/lib/feature-flags.ts` | Command | EVOL–P3-001 re-check | empty — file unchanged since previous run |
| `grep -rn "isFeatureEnabled\|getFeatureFlags" apps packages scripts` | Command | Flag consumers | only `feature-flags.ts` self-references — zero call sites |
| `grep -rn "FEATURE_" .` (examples/workflows) | Command | Flag deployment | no `FEATURE_*` variable anywhere |
| Python extraction: `requirePermission("m","a")` literals + factory `permissionModule` values vs catalog pairs parsed from `supabase/migrations/*.sql` | Command | ACM-P3-002 re-check | 43 distinct literal module keys, 0 missing pairs; all 10 `registerCrud` modules present |
| `grep -n "EVENT_OPTIONS" apps/web` + `grep -rn "dispatchWebhook(" apps/api/src` | Command | WH-P3-002 re-check | 2 UI lists of 11 events; 4 dispatch call sites, 2 distinct event names |
| `ls supabase/migrations \| wc -l`; `ls supabase/migrations \| cut -d_ -f1 \| sort \| uniq -d` | Command | Migration hygiene | 134 files, latest `5302436`, no duplicate prefixes |
| `grep -rn "Sunset\|deprecat" apps/` | Command | API versioning | only `docs/API_VERSIONING.md:14` mentions Sunset; no implementation |
| `grep -c "  \"/" docs/openapi.yaml` | Command | Spec inventory | 418 paths (matches `docs/INDEX.md:210`) |
| `timeout 60 node scripts/openapi-audit.js --report` | Command | Guard execution | **not reproducible on host** — `node: command not found`; guard reviewed statically only |
| `grep -rn "M365_CLIENT_STATE\|M365_WEBHOOK_SECRET" apps/api/src/config/env.ts apps/api/.env.example` | Command | Docs drift | env schema confirms `M365_CLIENT_STATE` is the auth value; no `M365_WEBHOOK_SECRET` |

## Executive Summary

The platform is a Turborepo monorepo (3 apps + 3 packages) with real, working extension seams: a worker task registry with metrics and a central scheduled-scan table, server-side module entitlement enforcement sharing one derivation, a data-driven permission catalog with per-user overrides, route factories (`registerCrud`, `crudRoute`, `crudEndpoints`, `register*Routes`) that collapse repetitive CRUD wiring, a documented migration workflow with a dry-run plan artifact and post-push drift check, a coverage-gated OpenAPI spec, guarded agent documentation, and 75 module docs with feature/runbook pairs. These are genuine strengths and are why this domain scores 3–4 in most categories.

The recurring weakness is that module metadata has no single source of truth. A module's identity is spread across the API mount table, the SDK class, two nav catalogs, module-config, the permission catalog migration, the entitlement lists, and the OpenAPI spec. Today's data is mostly consistent (all 43 referenced permission keys resolve), but drift is silent — the entitlement key `support` already disagrees with the permission key `tickets`, and the webhook UI advertises nine event types the platform never emits. Adding a module or an event is therefore an unchecked, multi-file change with no scaffold or CI guard.

Prioritized next actions: (1) introduce a module manifest + `check-module-registry` CI guard and promote the pack templates into live tooling; (2) define a webhook event catalog and assert emitters in CI; (3) close the permission-catalog lint; (4) resolve the migration-docs contradictions and add a naming lint. Feature flags are dead code and should be deleted or rebuilt.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| API mounts | `app.ts:174-233` | Module boundary | 60 hand mounts | Medium | no registry drives mounts |
| SDK client | `packages/sdk/src/index.ts:347` | Client contract | 55 sub-APIs hand-wired | Medium | no build/publish |
| Nav catalogs | `portal-nav.ts` / `admin-nav.ts` | UI module catalog | 63 / 57 keys | Medium | all resolve in permission catalog |
| Module UI config | `module-config.ts` | Generic CRUD UI | 748 lines | Medium | not linked to other catalogs |
| Permission catalog | `5302118` + `permissions`/`role_permissions`/`user_permission_overrides` | RBAC | Data-driven, enforced | Low | no catalog lint |
| Entitlements | `lib/entitlements.ts`, `middleware/entitlement.ts` | Plan gating | Enforced on 6 gated modules | Low | `support` key drift; fail-open on lookup error |
| Feature flags | `lib/feature-flags.ts` | Rollout control | Dead code | Low | zero consumers |
| Worker task registry | `task-registry.ts`, `tasks/index.ts` | Job extension | 28 registered tasks | Low | overwrite logs a warning |
| Scheduled scans | `schedule-config.ts` | Job scheduling | 17 entries, distinct offsets | Low | env-gated integrations |
| Route factories | `final/crud.ts`, `governance.ts`, `field-services.ts`, `security-suite.ts`, `security-ops.ts`, `vendors.ts`, `batch.ts` | CRUD extension | 5 patterns | Medium | inconsistent guards/tenant clients |
| Eventing | `webhook-dispatcher.ts`, `webhook-management.ts` | Outbound events | 2 events emitted | High | 11 advertised |
| API versioning | `/api/v1`, `docs/API_VERSIONING.md` | Contract evolution | Prefix only | Medium | policy unenforced |
| Migrations | `supabase/migrations/` | Schema evolution | 134 files, guarded push | Low | doc contradictions |
| Config | three env schemas | Config model | Duplicated | Medium | no shared env package |
| Shared packages | `@mct/config`, `@mct/sdk`, `@mct/ui` | Reuse | Source-only | Medium | extraction deferred |
| ADRs / module docs | `docs/adr`, `docs/modules`, `docs/module-matrix-mapping.md` | Docs | 11 ADR entries, 75 module docs | Low | stale in places (webhooks M365) |
| AI-agent docs | `AGENTS.md` + `review.md` + pinned prompts | Agent compatibility | Guarded mirror, SHA-pinned packs | Low | strong |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Module boundaries | 3 | `app.ts:174-233`; `routes/store.ts`; route factories | No manifest/registry; boundaries are file conventions only | Module manifest + drift guard |
| Domain model | 3 | `packages/sdk/src/database.types.ts` (generated, guarded); validators | Status/plan/role vocabularies hardcoded; `change_requests.status` free-form | Shared enums; catalog parity tests |
| Shared packages | 3 | 3 workspace packages used by all apps | Source-only, no build; DB client duplication | Decide extraction (ADR); @mct/db |
| Extension points | 4 | `registerTask`, `registerCrud`, `crudRoute`, `register*Routes`, entitlement middleware | Factories differ in guards/tenant client; no module template live | Unify factory; live templates |
| Feature flags | 1 | `feature-flags.ts:1-15` | Dead, global, no audit/targeting | Delete or rebuild |
| Permission extensibility | 4 | Data-driven catalog + overrides; `requirePermission` enforced on 225 call sites | No catalog lint; keys only checked by hand | `check-permission-catalog.mjs` |
| Tenant/org model | 4 | `organizations` + memberships + per-org entitlements/overrides; `assertResourceOrg` | Org `settings` jsonb untyped (one consumer); no hierarchy | Type org settings schema |
| API versioning | 2 | `/api/v1` prefix; `docs/API_VERSIONING.md` | No Sunset/deprecation code; spec version hardcoded | Deprecation middleware; version binding |
| Migration strategy | 4 | Workflow doc; dry-run artifact; post-push drift check; `db-types --check` | Conflicting naming docs; no down migrations (documented); no naming lint | Fix docs; add naming guard |
| Eventing/webhooks | 2 | Atomic dispatcher, DLQ, retries | No catalog; 9/11 advertised events never emitted | Event catalog + emitter test |
| Integration framework | 3 | Per-integration tasks (Jira/JSM/M365/Stripe) + signature verification | Each integration hand-written; no registry; M365 docs stale | Integration descriptor pattern |
| UI reuse | 4 | `@mct/ui` (7 components + stories), `docs/ui-kit.md`, app generics | Shared kit adoption narrow (39 files, mostly Skeleton) | Expand kit incrementally |

## Detailed Review

### Item: Module boundaries and registry

- Evidence: `app.ts:174-233`; `packages/sdk/src/index.ts:347-421`; nav catalogs; `module-config.ts`; `5302118`; `entitlements.ts:21-41`.
- What it does: routes are mounted manually under `/api/v1`; the SDK mirrors each route group as a class; the web app describes modules in three more lists.
- Current controls: OpenAPI coverage audit (`scripts/openapi-audit.js`) ensures routes appear in the spec; docs counts/links guards keep numbers honest; route-mount and tenant-scoping static tests guard new routers.
- Missing controls: nothing binds module keys across catalogs; no scaffold; templates live only in the pinned historical prompt pack.
- Risks: silent drift, incomplete module additions, agent/human confusion.
- Recommended improvement: single manifest + generator + CI guard (finding below).

### Item: Extension points (inventory)

- Worker tasks: `registerTask(type, handler)` (`task-registry.ts:19-25`) with success/failure/duration metrics and a no-handler counter; 28 registered types (`tasks/index.ts`); scheduled scans centralized with env gates and distinct offsets (`schedule-config.ts:27-55`).
- API CRUD factories: `registerCrud` (final), `crudRoute` (governance/field-services/security-suite/security-ops/batch/vendors), `register*Routes` (store). They differ: `final/crud.ts` uses `getSupabaseAdmin()` + `organization_id` query param, while governance/field-services use `getScopedClient(req, module, kind)`. A new module copied from the wrong factory inherits a weaker tenant pattern.
- Entitlements: `requireEntitlement(moduleKey)` + `GATED_MODULES` derived from one list.
- Permissions: `requirePermission(moduleKey, action)` resolved per request with admin bypass.
- Webhooks: event-name string filter.
- Metrics: prom-client registry with per-module counters (`lib/metrics.ts`).
- UI: `module-config.ts` + `module-record-actions.ts` generic update/delete; `AdminListPage`, `ModuleDetailPage`, `CrudForm`.
- Missing: an integration descriptor (each integration is hand-written), an event catalog, a module manifest.

### Item: Feature flags

- Evidence: `feature-flags.ts:1-15`; zero consumers; no `FEATURE_*` deploy vars.
- Assessment: not just unmanaged — currently dead. Verify/delete decision needed (EVOL–P3-001, still-open).

### Item: Permission extensibility

- Evidence: catalog migration `5302118` (94 module keys, role assignments for super_admin/admin/client_admin/technician/client_user), `lib/permissions.ts` (union of role_permissions across approved memberships + per-org overrides; super_admin bypass), `middleware/permissions.ts` (enforced on 225 call sites), `apps/web/lib/permissions.ts` (UI `can()`).
- Verification: Python extraction found all 43 literal module keys + 10 factory modules present in the catalog. No lint enforces this (ACM-P3-002 still-open).
- Risk: a typo'd key silently denies (or, combined with the admin bypass, hides the mistake).

### Item: API versioning

- Evidence: `docs/API_VERSIONING.md:11-16` (Sunset header, 6-month window, migration docs); no implementation; `spec.ts:4797` version `1.0.0` vs `VERSION` `0.1.0`; SDK private/source-only.
- Assessment: policy exists on paper only (finding below). Acceptable while the only consumer is the in-repo web app; a blocker for external/mobile/AI clients.

### Item: Migration strategy

- Strengths: workflow doc (`SUPABASE_MIGRATION_WORKFLOW.md`), pre-push dry-run plan uploaded as an artifact, fail-closed post-push drift check, `generate-db-types.js --check` in CI, RLS-predicate lint.
- Gaps: naming guide says ISO timestamps while the tree and workflow doc use 7-digit sequential; cheatsheet references a nonexistent `supabase/seed.sql`; no reverse migrations (documented decision); no duplicate-prefix lint (none exist today).

### Item: Eventing/webhooks

- Strengths: atomic idempotency claim, retry with backoff, DLQ, SSRF guard + pinned fetch, metrics, per-endpoint event subscription filter.
- Gaps: no event catalog; the UI advertises 11 events, only 2 are emitted; the API accepts arbitrary event strings; consumer docs missing/stale (M365).

### Item: Tenant/org model

- Strengths: `organizations` + memberships + roles + per-org `client_portal_entitlements` and `user_permission_overrides`; `assertResourceOrg` fail-safe 404; org-scoped admin resolution (`admin-scope.ts`); branding.
- Gaps: `organizations.settings` jsonb is an untyped extension point (single consumer: `status-page.ts:59` reads `status_page_enabled`); no org hierarchy (unknown if needed — no evidence of requirement).

### Item: Shared packages, config model, package extraction

- `@mct/config` is eslint/tsconfig/date only; each app owns its env schema (143/107/127 lines) with overlapping keys.
- `@mct/sdk`/`@mct/ui` are source-only private packages (no build/publish); `docs/arch/evaluation/db-package-evaluation.md` recommends `@mct/db` but it was never created; Supabase client setup is duplicated API↔worker.

### Item: UI reuse, admin tooling, background jobs, observability, AI compatibility

- UI: `docs/ui-kit.md` inventories shared primitives and app-local generics; `@mct/ui` has 7 components, 7 stories; adoption is real but narrow.
- Admin tooling: `AdminListPage` + `module-config` generic CRUD; admin nav guarded by `ADMIN_ROUTE_PERMISSIONS`; permission matrix UI.
- Jobs: registry + schedule config + scan lock; `WORKER_TIMEOUT` is not a real task timeout (RES-P2-002, owned by resilience domain).
- Observability: prom-client registry extensible per module; alert rules in `infra/digitalocean/alertmanager.tmpl.yml` (reviewed by OBS domain).
- AI compatibility: `AGENTS.md` is the single contract, mirrored to `review.md` and CI-checked (`sync-review-md.mjs --check`); prompt packs SHA-pinned with manifest verification; repomix config includes AGENTS.md as instructions. Strength.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EVOL-001 | Add a new module end-to-end | `app.ts:174-233`, `sdk/index.ts:347`, navs, `5302118` | conventions + OpenAPI audit | no registry/scaffold/guard | P2 | module manifest + CI drift guard |
| EVOL-002 | Rename a module key | `entitlements.ts` (`support` vs `tickets`) | none | silent drift | P2 | manifest as single source |
| EVOL-003 | Add a new outbound event | `NewWebhookForm.tsx:6-18`; 2 emitters | none | 9/11 events never fire | P2 | event catalog + emitter test |
| EVOL-004 | Reference a permission key | `requirePermission` (225 sites) | runtime resolution | no catalog lint | P3 | `check-permission-catalog.mjs` |
| EVOL-005 | Roll out a feature gradually | `feature-flags.ts` | env override only | dead, global, no audit | P3 | delete or managed flags |
| EVOL-006 | Deprecate an endpoint | `docs/API_VERSIONING.md` | none | no Sunset/Deprecation code | P3 | deprecation middleware |
| EVOL-007 | Add an env variable | 3 env schemas + deploy-do | boot-time zod | manual deploy parity | P3 | shared env package + parity test |
| EVOL-008 | New plan tier | `entitlements.ts:21-41` | binary active check | hardcoded sets | P3 | plan→module mapping table |
| EVOL-009 | New MSP role | `roles.ts` ×2 + `5302128` | comments | no parity test | P3 | generated constants |
| EVOL-010 | New migration | naming guide vs workflow doc | dry-run + drift check | contradictory docs; no naming lint | P3 | fix docs; naming guard |
| EVOL-011 | New integration | `tasks/jira-sync.ts` etc. | per-integration code | no descriptor/registry | P3 | integration descriptor pattern |
| EVOL-012 | External/mobile client | private source-only SDK | none | no versioned contract | P3 | decide extraction (ADR) |

## Findings

IDs below are provisional; the aggregator assigns final IDs. Severity, status and evidence are authoritative.

### Finding ID: EVOL–P2-001 - No module registry: module metadata is duplicated across six disconnected catalogs with no drift guard

- Severity: P2
- Confidence: High
- Area: EVOL
- Evidence:
  - `apps/api/src/app.ts:174-233` — 60 route prefixes mounted by hand
  - `packages/sdk/src/index.ts:347-421` — 55 sub-APIs hand-wired in `MCTClient`
  - `apps/web/lib/navigation/portal-nav.ts`, `admin-nav.ts` — 63/57 module keys
  - `apps/web/lib/module-config.ts:25-748`; `apps/web/lib/permissions.ts:45-133` (41 labels vs 94 catalog keys)
  - `apps/api/src/lib/entitlements.ts:21-41` — `support` vs permission key `tickets`
  - `prompts/.../templates/api-route-template.ts` — templates only in the pinned historical pack
- What is happening: no artifact describes a module once; every catalog is edited by hand and only routes↔spec is machine-checked.
- Why it matters: adding/renaming a module is an unchecked multi-file change; drift is silent; agents cannot verify wiring.
- User/business impact: slower, riskier module rollout; features can appear in nav but be missing from SDK/permissions/entitlements.
- Security/privacy/reliability impact: a module missing from the permission catalog relies on the admin bypass or denies everyone; an entitlement key typo silently gates or ungates a surface.
- Recommended fix: module manifest consumed by mounts/SDK/nav/entitlements/permission migration generation; CI guard; live templates.
- Suggested validation: `scripts/check-module-registry.mjs` test fixture with a deliberately missing key must fail.
- Owner suggestion: API principal engineer + web platform lead
- Effort estimate: M
- Dependencies: permission-catalog lint (below)
- Status: open
- Endpoint/data path: n/a (platform-wide)

### Finding ID: EVOL–P2-002 - Webhook UI advertises 11 event types but only 2 are ever dispatched; no event catalog exists

- Severity: P2
- Confidence: High
- Area: EVOL
- Evidence:
  - `apps/web/components/admin/NewWebhookForm.tsx:6-18` and `.../WebhookDetailClient.tsx:8-20` — duplicated 11-event lists
  - `apps/api/src/routes/webhook-management.ts:43-49` — events accepted as arbitrary strings
  - `apps/api/src/lib/webhook-dispatcher.ts:159-162` — `.contains("events", [event])`
  - `apps/api/src/routes/projects.ts:522`, `tickets.ts:183`, `store/quotes.ts:536` — only `project.created` and `ticket.created`
- What is happening: subscribers can select events that no code path emits; the filter silently matches nothing.
- Why it matters: silent non-delivery; unmanaged event contract.
- User/business impact: tenants build integrations on events that never arrive.
- Security/privacy/reliability impact: none directly; trust and support burden.
- Recommended fix: shared typed event catalog + payload schemas; validate on write; CI test catalog↔emitters; publish consumer docs.
- Suggested validation: unit test asserting every catalog event has an emitter and every `dispatchWebhook` literal is catalogued.
- Owner suggestion: API + integrations lead
- Effort estimate: S–M
- Dependencies: none
- Status: open

### Finding ID: EVOL–P3-001 - Feature flags are a hardcoded static map with no managed service, change log, or targeting

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence: `apps/api/src/lib/feature-flags.ts:1-15`; zero consumers (`grep`); no `FEATURE_*` deploy vars; file unchanged since `7a56f8dd`.
- What is happening: flags are a code literal resolved from env; nothing calls them.
- Why it matters: flag-driven evolution is impossible; the abstraction is dead weight.
- Recommended fix: delete, or move to a managed store with audit log and tenant/percentage targeting.
- Suggested validation: if kept, a test that every referenced flag exists in the catalog.
- Owner suggestion: `@api`
- Effort estimate: S
- Dependencies: none
- Status: still-open
- Note: re-verified at `8d299b8d`; previous row EVOL–P3-001.

### Finding ID: EVOL–P3-002 - No catalog-lint: referenced permission keys are not checked against the permissions table

- Severity: P3
- Confidence: High
- Area: EVOL (previous row area ACM — see note)
- Evidence: `.github/actions/unit-tests/action.yml:30-63` guard list has no permission check; no lint script; manual extraction at `8d299b8d` shows 43 literal module keys + 10 factory modules all resolve; `field-services.ts:257-264` `camera-calc` intentionally unguarded with no catalog row.
- What is happening: key correctness depends on reviewer diligence.
- Why it matters: typos deny (or with the admin bypass, mask) access; catalog renames have no reference search.
- Recommended fix: `scripts/check-permission-catalog.mjs` over route sources + web `permKey` usages, with a documented allowlist.
- Suggested validation: fixture with a bogus key must fail the guard.
- Owner suggestion: API platform
- Effort estimate: S
- Dependencies: none
- Status: still-open
- Note: re-verified at `8d299b8d`; previous row ACM-P3-002 (area ACM). Verified under the EVOL permission-catalog scope; the owning ACM domain may re-report — dedupe if duplicated.

### Finding ID: EVOL–P3-003 - No committed event catalog or webhook documentation for consumers

- Severity: P3
- Confidence: High
- Area: EVOL (previous row area WH — see note)
- Evidence: no catalog file (grep for "event catalog" only matches audit artifacts); `docs/modules/webhooks.md` inbound-only and documents M365 HMAC while the code authenticates via `M365_CLIENT_STATE` (`webhooks.ts:574-601`, `env.ts:58-59`); event list only in UI components.
- What is happening: consumers have no authoritative event/payload documentation.
- Why it matters: integrations cannot be built safely; docs misdescribe auth.
- Recommended fix: generate `docs/EVENTS.md` from the catalog; correct the M365 section.
- Suggested validation: docs-links guard covers the new file; review against catalog test.
- Owner suggestion: integrations/backend
- Effort estimate: S
- Dependencies: EVOL–P2-002
- Status: still-open
- Note: re-verified at `8d299b8d`; previous row WH-P3-002 (area WH). Verified under the EVOL eventing scope; the owning WH domain may re-report — dedupe if duplicated.

### Finding ID: EVOL–P3-004 - API versioning policy is documented but not enforced

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence: `docs/API_VERSIONING.md:11-16`; no Sunset/Deprecation code (grep); `spec.ts:4797` version `1.0.0` vs `VERSION` `0.1.0`; `packages/sdk/package.json` private/source-only.
- What is happening: single `/api/v1` prefix, no deprecation mechanism, no versioned client.
- Why it matters: breaking changes cannot follow the documented policy; future external clients lack a contract.
- Recommended fix: deprecation middleware driven by route metadata; bind OpenAPI version to releases; ADR on external SDK.
- Suggested validation: contract test that a deprecated route returns `Sunset`/`Deprecation` headers.
- Owner suggestion: API principal engineer
- Effort estimate: M
- Dependencies: release/versioning decisions
- Status: open

### Finding ID: EVOL–P3-005 - Config model is duplicated per app; no shared env-schema package

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence: `apps/api/src/config/env.ts:19-143`; `apps/worker/src/env.ts:5-107`; `apps/web/lib/env.ts:3-16`; `packages/config/package.json:5-9` exports eslint/typescript/date only; INFRA-P2-006 history shows deploy parity was manual.
- What is happening: each app re-declares overlapping env keys; deploy pipeline mirrors them by hand.
- Why it matters: one variable means up to four edits; drift surfaces at boot or never.
- Recommended fix: `@mct/config/env` fragments + deploy-parity test; generate `docs/ENVIRONMENT_VARIABLES.md`.
- Suggested validation: parity test fails when a schema key is absent from `deploy-do.yml`.
- Owner suggestion: platform engineering
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: EVOL–P3-006 - Shared-package extraction is deferred: source-only SDK/UI and duplicated DB client setup

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence: `packages/sdk/package.json:3-8,12-16`; `packages/ui/package.json`; `apps/api/src/services/supabase.ts:58-93` vs `apps/worker/src/services/supabase.ts`; `docs/arch/evaluation/db-package-evaluation.md`.
- What is happening: packages are consumed as TS source inside the workspace; DB bootstrap duplicated; no publish path.
- Why it matters: no versioned client for external/mobile consumers; duplication persists.
- Recommended fix: ADR deciding scope; extract `@mct/db`; add a build step to the SDK.
- Suggested validation: typecheck/test pass with the shared client; no direct `createClient` in app services.
- Owner suggestion: platform engineering (package owner)
- Effort estimate: M–L
- Dependencies: module registry (optional generator)
- Status: open

### Finding ID: EVOL–P3-007 - Migration-strategy docs contradict each other and the tree

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence: `docs/migrations/naming-guide.md:95` (ISO format) vs `docs/SUPABASE_MIGRATION_WORKFLOW.md:9` (7-digit prefix) vs 134 files using `5302xxx`; `docs/SUPABASE_MIGRATION_CHEATSHEET.md:41,68,141` references nonexistent `supabase/seed.sql` (contradicted by workflow doc lines 12-14); no duplicate prefixes today.
- What is happening: three docs describe different conventions; the cheatsheet references a removed file.
- Why it matters: contributors and agents create non-conforming migrations; ordering is load-bearing for hosted pushes.
- Recommended fix: standardize on the sequential convention, fix docs, add `check-migration-naming.mjs`.
- Suggested validation: guard fails on an out-of-sequence or duplicate prefix fixture.
- Owner suggestion: backend/data governance
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: EVOL–P3-008 - Roles, plan-to-module mapping, and status vocabularies are hardcoded with no parity guard

- Severity: P3
- Confidence: High
- Area: EVOL
- Evidence: `apps/api/src/lib/roles.ts:29-49` + `apps/web/lib/roles.ts:20-31` + `5302128:30` (three role lists synced by comments); `entitlements.ts:21-41` + free-text `subscriptions.plan_name` (`5302026...:525`); `validators/governance.ts:78` `z.string()` status with no DB check (`5302071_governance.sql:14`) while the UI offers 7 values (`module-config.ts:40-54`); 76 `z.enum` literals in the API.
- What is happening: vocabularies live in multiple hand-maintained lists with no parity test.
- Why it matters: role/plan/status changes are error-prone; unknown statuses pass the API silently.
- Recommended fix: generate role constants from the catalog migration; plan→module mapping table/config; shared status enums in `@mct/sdk` + zod + DB check constraints.
- Suggested validation: parity test between generated constants and migrations; validator rejects an unknown status.
- Owner suggestion: API platform + web
- Effort estimate: M
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Module drift makes a feature half-wired (nav without SDK/permission) | P2 | Medium | Broken UX, support load | EVOL–P2-001 | Manifest + CI guard |
| Tenants integrate against events that never fire | P2 | High (already true) | Silent non-delivery, churn | EVOL–P2-002 | Event catalog + emitter test |
| Permission key typo denies or masks access | P3 | Medium | Authz incidents | EVOL–P3-002 | Catalog lint |
| External client built on unversioned API breaks silently | P3 | Low today / High later | Rework, incidents | EVOL–P3-004 | Deprecation policy in code |
| Deploy drift on env vars | P3 | Medium | Boot failures | EVOL–P3-005 | Shared env + parity test |
| Non-conforming migration breaks ordering/drift check | P3 | Medium | Failed deploy, schema drift | EVOL–P3-007 | Naming guard |
| Role/status vocabulary drift | P3 | Medium | Inconsistent authz/UI | EVOL–P3-008 | Catalogs + parity tests |

## Recommendations

### Immediate / Release Blocking

None. No P0/P1 extensibility finding was identified at `8d299b8d`.

### This Week

1. Correct `docs/modules/webhooks.md` M365 authentication text and the migration naming/cheatsheet contradictions (S, docs-only).
2. Land `scripts/check-permission-catalog.mjs` (S) — it protects the 225 existing `requirePermission` sites at near-zero cost.

### This Month

3. Author the module manifest + `check-module-registry.mjs`; promote pack templates to a live `templates/` directory with an "adding a module" checklist (M).
4. Define the webhook event catalog, validate on write, add the emitter-coverage test, publish `docs/EVENTS.md` (S–M).
5. Delete `feature-flags.ts` or replace it with a managed implementation (S).
6. Add `check-migration-naming.mjs` and fix the naming guide (S).

### Later / Platform Evolution

7. Deprecation middleware + OpenAPI version binding; ADR on external SDK/mobile clients (M).
8. `@mct/config/env` shared schemas + deploy-parity test; generate env docs (M).
9. Extract `@mct/db`; add SDK build step; optionally generate SDK wiring from the manifest (M–L).
10. Unify the CRUD factories (one factory with explicit tenant-client + permission parameters) so new modules inherit the hardened pattern (M).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Delete or quarantine `feature-flags.ts` | Removes dead abstraction and confusion | `apps/api/src/lib/feature-flags.ts` | grep shows no consumers; tests green |
| Fix M365 text in `docs/modules/webhooks.md` | Docs currently contradict code | `docs/modules/webhooks.md:15-39` | manual read vs `routes/webhooks.ts:574-601` |
| Permission-catalog lint | Catches key typos at CI time | new `scripts/check-permission-catalog.mjs`, `.github/actions/unit-tests/action.yml` | fixture with bogus key fails |
| Single-source the webhook event list | Removes a duplicated 11-entry list | `NewWebhookForm.tsx`, `WebhookDetailClient.tsx` | one shared constant import |
| Fix migration naming guide/cheatsheet | Stops new non-conforming migrations | `docs/migrations/naming-guide.md`, `docs/SUPABASE_MIGRATION_CHEATSHEET.md` | `check-docs-links` + manual read |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Module manifest + registry guard | P2 | API + web platform | M | permission lint |
| Event catalog + emitter test + EVENTS docs | P2 | API/integrations | S–M | none |
| Deprecation/Sunset middleware | P3 | API principal | M | release versioning |
| Shared env package + deploy parity test | P3 | platform engineering | M | none |
| `@mct/db` extraction + SDK build | P3 | platform engineering | M–L | ADR |
| Role/status/plan catalogs + parity tests | P3 | API + web | M | none |
| Migration naming lint | P3 | data governance | S | docs fix |
| Integration descriptor registry | P3 | integrations | M | event catalog |

## Suggested Tests

- Unit: `check-module-registry` fixture (missing nav key, missing SDK entry, orphan route) fails.
- Unit: event catalog — every catalog event has ≥1 emitter; every `dispatchWebhook` literal is catalogued; API rejects uncatalogued events on webhook creation.
- Unit: permission-catalog lint fixture with an unknown `module:action` fails.
- Integration: deprecation middleware emits `Sunset`/`Deprecation` headers for a flagged route.
- Integration: deploy-parity test — every key in API/worker env schemas appears in `deploy-do.yml` envs/printf.
- CI: migration-naming guard (unique, monotonic prefixes).
- Manual: walk the "adding a module" checklist in a scratch branch and confirm the guard catches each omitted wiring point.

## Suggested Documentation Updates

- `docs/modules/webhooks.md` — correct M365 auth; link the new event catalog.
- `docs/EVENTS.md` (new) — generated event catalog with payloads and delivery semantics.
- `docs/migrations/naming-guide.md` + `docs/SUPABASE_MIGRATION_CHEATSHEET.md` — align with the workflow doc and the tree.
- `docs/adr/README.md` — add ADRs: module registry, event catalog, package extraction (`@mct/db`), feature-flag decision.
- `docs/module-matrix-mapping.md` — add a "wiring checklist" column or link the manifest.
- `AGENTS.md` — after the manifest lands, replace the manual wiring instructions with the manifest/guard commands.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is an external/mobile SDK or API consumer planned? | Decides whether versioning/extraction work is required now | product roadmap (not in repo) |
| Are feature flags intended to be used at all? | Delete vs rebuild | product/engineering decision |
| Should `organizations.settings` be a typed, validated extension point? | Currently one untyped consumer | roadmap for per-org configuration |
| Which catalog convention wins for migrations (sequential vs ISO)? | Docs contradict; the tree and workflow say sequential | owner decision |
| Are the 9 unemitted webhook events planned features or UI overreach? | Determines delete vs implement | integrations roadmap |

## Appendix

### Extension point inventory (verified at 8d299b8d)

| Extension point | Registration API | Count / evidence |
|---|---|---|
| Worker tasks | `registerTask(type, handler)` | 28 registered (`apps/worker/src/tasks/index.ts`) |
| Scheduled scans | `scheduledScans` table | 17 entries, distinct offsets (`schedule-config.ts:27-55`) |
| API CRUD (final) | `registerCrud(router, path, table, schema, permissionModule)` | 10 modules (`final/crud.ts:167-178`) |
| API CRUD (governance/field-services/security-suite/security-ops/batch/vendors) | local `crudRoute`/`crudEndpoints` | 5 factories |
| Store routes | `register*Routes(router)` | 5 registrations (`routes/store.ts`) |
| Module gating | `requireEntitlement(moduleKey)` | 6 gated modules; `GATED_MODULES` single source |
| Permission gating | `requirePermission(moduleKey, action)` | 225 call sites, 43 distinct module keys |
| Metrics | prom-client `register` | `apps/api/src/lib/metrics.ts`, worker `metrics.ts` |
| UI CRUD | `module-config.ts` + `module-record-actions.ts` | generic update/delete/audit actions |
| Scoped DB client | `getScopedClient(req, module, kind)` | RLS allow-lists from env secrets (ADR-008) |
| Shared UI | `@mct/ui` subpath exports | 7 components + tokens + ThemeProvider |

### Command log (observed results)

- `git log -1 --format='%H %s'` → `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd Merge PR #168…`
- `git merge-base --is-ancestor 9c0b88c HEAD` → ancestor (previous-run comparison valid)
- `git diff --stat 9c0b88c..HEAD -- apps/api/src/lib/{feature-flags,entitlements,permissions,roles}.ts` → empty (unchanged)
- `grep -rn "isFeatureEnabled\|getFeatureFlags" apps packages scripts` → 4 self-references only
- `grep -rn "FEATURE_" .` → 1 self-reference only
- `ls supabase/migrations | wc -l` → 134; `uniq -d` on prefixes → empty
- `grep -rn "Sunset" apps docs` → `docs/API_VERSIONING.md:14` only
- Python catalog extraction → 43 referenced module keys, 94 catalog keys, 0 missing pairs
- `grep -rn "dispatchWebhook(" apps/api/src` → 4 sites, 2 distinct event names
- `node scripts/openapi-audit.js --report` → **not run** (`node: command not found` on host)

## Findings

| ID | Severity | Title |
|---|---|---|
| EVOL-P2-001 | P2 | No module registry: module metadata is duplicated across six disconnected catalogs with no drift guard |
| EVOL-P2-002 | P2 | Webhook UI advertises 11 event types but only 2 are ever dispatched; no event catalog exists |
| EVOL-P3-001 | P3 | Feature flags are a hardcoded static map with no managed service, change log, or targeting |
| EVOL-P3-002 | P3 | No catalog-lint: referenced permission keys are not checked against the permissions table |
| EVOL-P3-003 | P3 | No committed event catalog or webhook documentation for consumers |
| EVOL-P3-004 | P3 | API versioning policy is documented but not enforced (no Sunset/Deprecation mechanism; spec version unrelated to the app version) |
| EVOL-P3-005 | P3 | Config model is duplicated per app; there is no shared env-schema package |
| EVOL-P3-006 | P3 | Shared-package extraction is deferred: @mct/sdk and @mct/ui are source-only, and DB client setup is duplicated |
| EVOL-P3-007 | P3 | Migration-strategy docs contradict each other and the tree (ISO vs sequential naming; seed.sql references) |
| EVOL-P3-008 | P3 | Roles, plan-to-module mapping, and status vocabularies are hardcoded with no parity guard |
