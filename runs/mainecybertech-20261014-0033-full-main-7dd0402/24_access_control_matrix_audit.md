# Access Control Matrix — re-audit verification (main @ 7dd0402)

## Audit Metadata

- Audit name: mainecybertech
- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Repository: `github.com/MaineCyberTech/mainecybertech`
- Branch: `main` (audited ref `origin/main`)
- Commit SHA: `7dd040234e8dfa40dd2d2b6fe1ca7379f2fba097`
- Generated at: 2026-10-14
- Auditor: subagent (full-domain verification re-audit, group 1)
- Area code: ACM
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261014-0033-full-main-7dd0402/24_access_control_matrix_audit.md`
- Scope limitations: static route/middleware inspection; no live database, so RLS conclusions are drawn from
  the migration chain (latest writers win) and the checked-in guards. Deployed allow-list values unverified.

## Scope

Re-verification of the 17 ACM findings from the previous full run, plus a route-level scan for missing
permission gates. Reviewed: role/trust tiers, the permission catalog and its lint, tenant/org membership
resolution, module CRUD gates, API keys/webhooks, admin console surfaces, server actions, background jobs,
DB helpers/RLS predicates, and the middleware chain.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/lib/roles.ts`, `packages/sdk/src/role-keys.ts` | Source | Trust tiers | CROSS_TENANT vs ELEVATED split |
| `apps/api/src/middleware/permissions.ts`, `lib/permissions.ts` | Source | `requirePermission` + resolver/cache | Key-scope cap before bypass |
| `supabase/migrations/5302437, 5302459, 5302434` | Migration | super-admin trigger, dead predicates, anon grants | Latest writers verified |
| `scripts/ci/check-permission-catalog.sh`, `scripts/check-permission-catalog.mjs` | Script/CI | Catalog lint + negative fixture | Wired in unit-tests action |
| `docs/PUBLIC_ROUTES.md`, `scripts/public-route-inventory.mjs` | Doc/CI | Public surface inventory | Generated + `--check` in CI |
| `apps/api/src/routes/final/crud.ts`, `final/*.ts`, `sla.ts` | Source | Ungated reads (new) | Router mounts only requireAuth+requireOrgAccess |
| `supabase/migrations/5302118_permission_matrix_full_catalog.sql:182-185` | Migration | Module `view` actions exist | Proves the gate gap is a real inconsistency |

## Verification Performed

- Re-checked every prior ACM evidence path at the current commit (roles, permissions middleware, api-keys,
  webhooks, profiles, RLS migrations, AI routes, store catalog, client-portal ordering).
- Ran a mutating-verb scan for `requirePermission(...,'view')` (one residual: `ai.ts:217`).
- Scanned `registerCrud`/`final/*`/`sla` for any permission gate (none) and confirmed the catalog defines
  `view` actions for those modules.
- Confirmed the catalog-lint script and its negative fixture, and the public-route inventory check, are in CI.

## Executive Summary

The access-control model is much stronger than at the previous audit: 13 of 17 findings are verified fixed,
four are partially fixed, and none regressed. Role assignment is centrally guarded, the global role catalog
is super-admin-only, API-key scopes are enforced with expiry/pruning, webhook reads are `webhooks:view`
gated, dead RLS predicates are now catalogued, and the public route inventory is generated and gated.

One new issue was raised (ACM-P3-008): the `registerCrud` factory and the `final/*` module routers expose
read/compute endpoints with no `requirePermission` gate, even though the catalog defines `view` actions for
those modules — any approved org member can read them for their own org. The residual partials are the RLS
rollout (ACM-P2-002), the single `ai:view` triage exception (ACM-P2-003), same-org profile enumeration
(ACM-P2-007), and the absence of a per-route permission coverage gate (ACM-P3-001, which ACM-P3-008 now
exemplifies).

## Findings

| ID | Sev | Status | Title | Re-verification evidence |
|---|---|---|---|---|
| ACM-P1-001 | P1 | verified-fixed | Client-onboarding mutations ungated | `client-onboarding-command-center.ts:32-33,137-247` |
| ACM-P1-002 | P1 | verified-fixed | `profiles.is_super_admin` forgeable | `5302437_protect_is_super_admin.sql` BEFORE UPDATE trigger |
| ACM-P2-001 | P2 | verified-fixed | PLATFORM/ADMIN_BYPASS key sets inconsistent | `@mct/sdk/role-keys` split + parity test |
| ACM-P2-002 | P2 | partially-fixed | RLS not a DB backstop (service role default) | `rls-startup-check.ts:40-46`; `getScopedClient` still service-role for unlisted modules |
| ACM-P2-003 | P2 | partially-fixed | Write/state transitions gated by `view` | Only `ai.ts:217` (POST /triage/analyze, `ai:view`) remains |
| ACM-P2-004 | P2 | verified-fixed | Webhook reads open to any member | `webhook-management.ts:103,125,348,508` `webhooks:view` |
| ACM-P2-005 | P2 | verified-fixed | API-key expiry unenforced/unpruned | `api-key.ts:84-88`; prune task scheduled daily |
| ACM-P2-006 | P2 | verified-fixed | Webhook signing secrets plaintext | `webhook-management.ts:35-52,77-78,369` encrypted at rest + rotation metadata |
| ACM-P2-007 | P2 | partially-fixed | Profiles enumerable by email/id | `profiles.ts:62-92`; RLS same-org (`5302026:1006-1016`); ciphertext stripped. No permission gate on the directory query |
| ACM-P2-008 | P2 | verified-fixed | API-key permissions decorative | `middleware/permissions.ts:73-79`; `api-keys.ts:43` |
| ACM-P3-001 | P3 | partially-fixed | Client-side hiding UI-only for several actions | Server enforcement broad + catalog-linted; no per-route permission coverage gate; ACM-P3-008 is the concrete instance |
| ACM-P3-002 | P3 | verified-fixed | No catalog-lint | `scripts/ci/check-permission-catalog.sh` + negative fixture in CI |
| ACM-P3-003 | P3 | verified-fixed | No public route inventory | `docs/PUBLIC_ROUTES.md` + `public-route-inventory.mjs --check` |
| ACM-P3-004 | P3 | verified-fixed | `GET /roles/:id` and `/me/permissions` ungated | `roles.ts:67` requireAdmin; `me.ts:18` self-scoped |
| ACM-P3-005 | P3 | verified-fixed | Dead RLS `manage` predicates | `5302459_dead_rls_permission_predicates.sql`; guard clean |
| ACM-P3-006 | P3 | verified-fixed | `GET /api-keys` ungated | `api-keys.ts:43` `api-keys:view` + test |
| ACM-P3-007 | P3 | verified-fixed | AI copilot endpoints ungated | `ai.ts:346-348,418-420,515,537,562,578` |
| ACM-P3-008 | P3 | **open (new)** | `registerCrud`/`final/*` reads have no `requirePermission` gate | `final/crud.ts:33-59,88-103`; `final.ts:20-21`; `final/procurement.ts:8`; `final/sharepoint.ts:7`; `final/backups.ts:7,22`; `final/budgets.ts:7`; `final/time-entries.ts:11`; `sla.ts:13`; catalog views `5302118:182-185` |

## Route access matrix (updated observations)

| Guard shape | Current state |
|---|---|
| Router-level `requireAuth` + `requireOrgAccess` | Majority of routers (unchanged) |
| Router-level `requireAdmin` | admin, bulk, business-os, dashboard, search, audit, sla (read-only metrics), final/* (only auth+org) |
| Per-route `requirePermission` | Broad; catalog-linted. Reads ungated in `final/*` + `registerCrud` (new) |
| Mutating route with a `view` gate | 1 residual: `ai.ts:217` |
| Public (no router auth) | auth, public, docs (404 in prod), health, webhooks, store/*, analytics `/track` (global limiter) |

## Recommendations

### This Week

1. Add `requirePermission(module, "view")` to the `registerCrud` list/get handlers and to the `final/*`
   module reads; decide whether `POST /procurement/compare` needs a gate (ACM-P3-008).
2. Add a per-route permission coverage check (static, with an explicit allow-list) so a new ungated read
   fails CI (ACM-P3-001).

### This Month

3. Resolve `ai.ts:217` (either a documented permanent exception or an `ai:create`-style gate) (ACM-P2-003).
4. Continue the RLS rollout for writes and publish the deployed allow-lists (ACM-P2-002).
5. Decide the profile-directory contract: gate `GET /profiles?email=` or document it (ACM-P2-007).

## Suggested Tests

- Integration: client roles get 403 on `final/time-entries`, `final/budgets`, `final/backups`,
  `final/sharepoint`, `sla/metrics`; members with the view grant get 200.
- Unit: permission coverage guard enumerates every read handler and requires a gate or an allow-list entry.
- DB/RLS: user-scoped client cannot update `profiles.is_super_admin` (covered by 5302437); catalog guard
  green.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are `final/*` modules client-visible by design? | Decides gate vs document | Product decision |
| Should `/sla/metrics` be permission-gated? | Same | Product decision |
| Deployed RLS allow-lists | Real RLS coverage | Operator environment |
