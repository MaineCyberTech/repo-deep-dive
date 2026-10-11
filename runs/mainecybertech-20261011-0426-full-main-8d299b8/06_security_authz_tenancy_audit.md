# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (monorepo: `apps/api`, `apps/web`, `apps/worker`, `supabase/`, `infra/`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent `06_security_authz_tenancy_audit` (area SEC)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/06_security_authz_tenancy_audit.md`
- Scope limitations: read-only static review at the audited commit. No runtime probing, no dependency installation, no database access. External state (GitHub secrets, Supabase project settings, live branch protection) is `unverified` and marked as such.

## Scope

Reviewed at `8d299b8d`: auth middleware (`middleware/auth.ts`, `admin.ts`, `org-access.ts`, `permissions.ts`, `api-key.ts`, `csrf.ts`, `rate-limit.ts`, `security-headers.ts`, `entitlement.ts`), auth lifecycle (`routes/auth.ts`, `lib/mfa.ts`, `lib/mfa-recovery.ts`), tenant scoping (`lib/tenant.ts`, `lib/admin-scope.ts`, `lib/roles.ts`, `lib/permissions.ts`), PII handling (`lib/field-encryption.ts`, `lib/profile-pii.ts`), SSRF/file handling (`lib/ssrf-guard.ts`, `lib/pinned-fetch.ts`, `lib/upload-validation.ts`, `routes/documents.ts`, `routes/file-requests.ts`), webhooks (`routes/webhooks.ts`, `lib/webhook-signature.ts`), API keys (`middleware/api-key.ts`, `routes/api-keys.ts`), public/auth routes, RLS migrations and guards, deploy env wiring, and worker SSRF/monitoring paths.

Not reviewed: UI rendering details (domain 05), payment reconciliation (domain 29), notification delivery (domain 30), and live infrastructure. Dependency-CVE review is domain 11 (supply chain).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/middleware/auth.ts` | Source | JWT pinning, API-key resolution, Supabase fallback, MFA step-up | Signature pinned to HS256; MFA checked after verification |
| `apps/api/src/middleware/{admin,org-access,permissions}.ts` | Source | Authz gates, tenant pinning, permission enforcement | Org pinning + `assertBodyOrgMatches` present |
| `apps/api/src/middleware/api-key.ts`, `routes/api-keys.ts` | Source | Machine credentials | Hash + timing-safe compare; scopes not enforced (new finding) |
| `apps/api/src/lib/{mfa,mfa-recovery,field-encryption,profile-pii}.ts` | Source | MFA, recovery codes, PII crypto | Fail-closed crypto; enforcement opt-in |
| `apps/api/src/middleware/{csrf,rate-limit,security-headers}.ts` | Source | CSRF, throttling, headers | Double-submit; per-email buckets; CSP tightened |
| `apps/api/src/routes/{auth,public,webhooks,health,audit,analytics,roles,memberships,users,bulk,organizations}.ts` | Source | Reachable authorization surfaces | Several verification rows and new findings |
| `apps/api/src/lib/{ssrf-guard,pinned-fetch,upload-validation}.ts`, `apps/worker/src/{lib,tasks}` | Source | SSRF, upload sniffing, monitoring fetches | Webhooks pinned; monitoring TOCTOU remains |
| `supabase/migrations/5302100, 5302112, 5302129, 5302135, 5302434, 5302436` + `scripts/check-rls-predicate.mjs` | Migration/guard | RLS approved predicate, anon grants, PII column | Guards wired into CI |
| `.github/workflows/deploy-do.yml`, `infra/digitalocean/docker-compose.yml`, `Caddyfile.prod` | Config | Secret/env wiring, topology, headers | Caddy fronts API; no published API port |
| `.gitleaks.toml`, `scripts/scan-secrets.sh`, `scripts/ci/verify-gitleaks-config.sh` | Config/guard | Secret scanning | Allowlists scoped; scanner no longer echoes values |
| `apps/api/src/__tests__/{api-key-auth,auth-redirect-origin,route-authorization-guard}.test.ts` | Tests | Regression coverage for authz | Present and meaningful |

## Verification Performed

All commands were read-only, run against `/tmp/opencode/mct-audit-target` at `8d299b8d`.

| Command | Observed result |
|---|---|
| `git log -1 --format='%H %s'` | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd Merge PR #168: promote develop to main` |
| `grep -n "assertProductionSecrets\|assertProductionTurnstile" apps/api/src/config/env.ts` | Both guards present (`env.ts:100-108`, `85-93`); `getEnv()` calls both |
| `grep -rn "get_analytics_summary" --include=*.sql --include=*.ts .` | Only `apps/api/src/routes/analytics.ts:84`; no migration/seed definition |
| `grep -rn "to anon" supabase/migrations/` (files > 5302434) | No blanket anon DML re-grant; `5302434` revokes and narrows |
| `grep -n "RLS_READS_ENABLED\|RLS_WRITES_ENABLED" apps/api/src/lib/rls-startup-check.ts` | Production refuses boot with empty read list; empty write list only logs |
| `grep -rn "req.apiKey" apps/api/src` | Only `middleware/auth.ts:70-82`; `permissions.ts` never reads key scopes |
| `grep -rn "pinnedFetch" apps/worker/src apps/api/src` | Webhook dispatch/retry/test use it; `module-tasks.ts` uses plain `fetch` after `assertSafeUrl` |
| `grep -rn "PLATFORM_ADMIN_KEYS\|isPlatformAdminKey" apps/api/src` | Remaining uses are in-org (`tickets.ts:190-195,443-451`); cross-tenant uses `isCrossTenantKey` |
| `grep -rn "M365_WEBHOOK_SECRET" apps .github docker-compose.yml` | Only explanatory comments in `env.ts:58` and `.env.example:33` — dead key removed |
| `grep -rn "email_confirm" apps/api/src/routes/bulk.ts` | `email_confirm: true` still present (line 114) |
| `grep -rn "auth/callback" apps/api/src apps/web/app` | API serves POST `/api/v1/auth/callback`; web route is `/auth/callback`; sign-up redirect uses request Host |
| `grep -n "permissions" supabase/migrations/5302042_api_keys.sql` | Column defaults to `'[]'::jsonb`; no writer |
| `grep -rn "assertBodyOrgMatches" apps/api/src/middleware/org-access.ts` | Called on both `requireOrgAccess` branches (lines 228, 249) |
| `python3 -c "json.load(...)"` on the emitted findings JSON | Parses; 40 findings, all required keys, valid severity/status values |

Headline-claim reproductions: `SEC-P1-001`, `SEC-P2-008`, `SEC-P2-009`, `SEC-P3-002`, `SEC-P3-007`, `ADMIN-P1-001`, `CHAIN-P1-001/002`, `FEAT-P2-001` — all `supported` from source at `8d299b8d`. `SEC-P2-007` — `partially supported` (plumbing and boot gate exist; deployed secret values external, `unverified`). `SEC-P2-006` — `supported` (still broken). `ACM-P2-006` — `partially supported` (enforced at auth, not pruned).

## Executive Summary

The security posture is materially stronger than the previous full run's baseline: field encryption fails closed, the reset redirect is no longer caller-controlled, webhook dispatch and webhook test calls use a DNS-pinned fetch, the anon DML blanket grant is gone, `/health` no longer leaks provider state, RLS predicate hygiene has a CI guard, and API keys actually authenticate. The org-pinned `requireAdmin` + `resolveAdminTenantScope` combination closes the tenant-admin cross-tenant read path, and the audit/impersonation trail is reviewable by genuine platform admins only.

The most important **new** risk is a privilege-escalation gap in role assignment: `PATCH /memberships/:id`, `POST /memberships/invite`, `POST /bulk/invite` and `POST /organizations/onboard` all accept a caller-chosen role (id/key) without the `super_admin` guard that `/users/:id/role` enforces. A user with the delegable `users:manage` permission (or any tenant admin) can mint a `super_admin` membership and move into the cross-tenant trust tier that `ADMIN-P1-001` pinning relies on.

Secondary themes: the PII encryption control is additive (plaintext stays authoritative), the worker's monitoring fetches retain the DNS-rebinding TOCTOU fixed for webhooks, API-key scopes are stored but ignored, the global RBAC catalog is mutable by an org-scoped `roles:manage`, and MFA remains opt-in with a `false` deployed default.

Recommended next actions: fix the role-assignment guard this week (one shared helper + tests); route monitoring through `pinnedFetch`; decide the PII cutover; enforce or drop API-key scopes; and make admin accounts require aal2.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Auth provider | `middleware/auth.ts`, Supabase GoTrue | Session/JWT + API keys | Implemented | Low | HS256 pinned; Supabase fallback bounded by timeout |
| Session cookies | `apps/web/lib/cookie-domain.ts`, `mct_session` | Web session | Implemented | Low | httpOnly, secure, lax, parent domain |
| JWT validation | `middleware/auth.ts:100-134`, `lib/mfa.ts` | Verify + MFA step-up | Implemented | Medium | MFA opt-in; SSE revalidation does not pin algorithms |
| CSRF/CORS | `middleware/csrf.ts`, `app.ts:93-109` | Browser write protection | Implemented | Low/Medium | `CORS_ORIGIN="*"` still reflects any origin |
| Rate limits | `middleware/rate-limit.ts`, `app.ts:125-146` | Abuse throttling | Implemented | Medium | Email key not normalized; auth bucket per-email |
| Security headers | `middleware/security-headers.ts` | API headers/CSP | Implemented | Low | Caddyfile still sets deprecated X-XSS-Protection |
| Input/output validation | Zod schemas across routes; `middleware/security.ts` | Validation | Implemented | Low | Zod strips unknown keys; blocklist is defense in depth |
| File handling | `lib/upload-validation.ts`, `documents.ts`, `file-requests.ts` | Uploads/downloads | Implemented | Low | MIME sniffing, org paths, signed URLs |
| API permissions | `middleware/permissions.ts`, `lib/permissions.ts` | RBAC enforcement | Implemented | Medium | Uncached; API-key scopes ignored |
| Admin permissions | `middleware/admin.ts`, `lib/admin-scope.ts` | Admin gate + scope | Implemented | Low | Org pinning + allTenants rule |
| Tenant isolation | `middleware/org-access.ts`, `lib/tenant.ts` | Org scoping | Implemented | Medium | App-layer primary; RLS opt-in |
| RLS policies | `supabase/migrations/5302100/5302112/5302434`, `scripts/check-rls-predicate.mjs` | DB backstop | Partial (opt-in) | Medium | Prod boot gate for reads; writes warn only |
| API keys | `middleware/api-key.ts`, `routes/api-keys.ts` | Machine credentials | Implemented | Medium | Auth works; scopes dead; always service-role |
| Webhooks | `routes/webhooks.ts`, `lib/webhook-signature.ts` | Inbound verification | Implemented | Low | HMAC over raw body, replay claims, constant-time M365 |
| Secrets/env | `config/env.ts`, `deploy-do.yml`, compose | Config validation | Implemented | Low | Fail-closed prod asserts; dead M365 key removed |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 4 | `auth.ts` HS256 pin, Supabase fallback timeout, MFA support | MFA not enforced by default | Role-aware aal2 enforcement |
| Session tokens/cookies | 4 | `cookie-domain.ts`, CSRF double-submit | No server-side revocation list (Supabase-managed) | Document revocation expectations |
| JWT validation | 4 | `auth.ts:107`, `auth.ts:150-163` | SSE revalidation omits `algorithms` | Pin algorithms in `notifications.ts:89` |
| CSRF/CORS | 3 | `csrf.ts`, `app.ts:101-106` | `*` reflects any origin with credentials | Reject `*` when credentialed/prod |
| Rate limits | 3 | `rate-limit.ts` per-email buckets | Email key not normalized; no per-token limits | Normalize keys; review auth ceilings |
| Security headers | 4 | `security-headers.ts` | Caddyfile deprecated header | Align Caddy header set |
| Input/output validation | 4 | Zod route schemas, `security.ts` | Blocklist heuristics only | Keep Zod as the contract |
| File handling | 4 | sniffing, org-bound paths, signed URLs | Monitoring fetch TOCTOU (worker) | Use pinned fetch everywhere |
| API permissions | 3 | `permissions.ts` enforcement | Uncached; key scopes ignored | Cache; enforce key scopes |
| Admin permissions | 4 | `admin.ts`, `admin-scope.ts` | Role-assignment escalation path | Shared super_admin guard |
| Tenant/org isolation | 4 | `org-access.ts`, `tenant.ts`, search/admin scoping | App-layer primary; RLS opt-in | Finish RLS rollout |
| RLS policies | 3 | approved-aware helper, guards, anon least privilege | Writes default service-role; values external | Verify deployed allowlists |

## Detailed Review

### Item: Authentication and MFA

- Evidence: `middleware/auth.ts:46-181`, `lib/mfa.ts`, `routes/auth.ts:404-730`, `apps/web/lib/auth/auth-actions.ts`.
- What it does: verifies HS256 JWTs against a comma-separated secret list, falls back to Supabase `getUser` (5 s timeout), then applies MFA step-up when `MFA_ENFORCEMENT_ENABLED` is true and the user has a verified TOTP factor.
- Missing controls: MFA default off; SSE revalidation (`routes/notifications.ts:89`) verifies without `algorithms` pinning; sign-up `emailRedirectTo` uses the request Host.
- Risks: admin sessions password-only by default (new finding); Host echo in confirmation email (new finding).

### Item: Authorization middleware and tenant scoping

- Evidence: `middleware/admin.ts:22-64`, `middleware/org-access.ts:20-325`, `middleware/permissions.ts:54-93`, `lib/admin-scope.ts`, `lib/tenant.ts`, `lib/roles.ts`.
- What it does: pins admin checks to the resolved org unless the caller holds `super_admin`; only `admin`/`super_admin` cross tenants; `assertBodyOrgMatches` rejects body/query org mismatches; `loadOwned`/`assertResourceOrg` enforce row ownership.
- Missing controls: role-assignment paths do not validate `super_admin`; `roles` catalog mutations are not platform-gated.
- Risks: privilege escalation to the cross-tenant tier (new P1); cross-tenant RBAC catalog mutation (new P2).

### Item: API keys

- Evidence: `middleware/api-key.ts`, `middleware/auth.ts:67-88`, `routes/api-keys.ts`, `supabase/migrations/5302042_api_keys.sql`.
- What it does: prefix lookup + SHA-256 timing-safe compare, active/expiry checks, org pinning, best-effort `last_used_at`.
- Missing controls: stored `permissions` are never enforced; create API cannot set them; GET list has no permission gate; RLS never applies (no `req.userJwt`).
- Risks: scoped keys silently over-privileged; RLS rollout blind spot (new finding).

### Item: Webhooks and SSRF

- Evidence: `routes/webhooks.ts`, `lib/webhook-signature.ts`, `lib/pinned-fetch.ts`, `apps/worker/src/tasks/{webhook-dispatcher,webhook-retry,module-tasks}.ts`.
- What it does: raw-body HMAC verification, timestamp tolerance, atomic idempotency claims, constant-time M365 `clientState`, DNS-pinned outbound dispatch with no redirects.
- Missing controls: monitoring checks (uptime/website) guard-then-fetch; `fetchSslExpiry` raw `tls.connect`.
- Risks: SSRF from worker into droplet internals via DNS rebinding (new finding).

### Item: PII encryption

- Evidence: `lib/field-encryption.ts`, `lib/profile-pii.ts`, `routes/profiles.ts`, `supabase/migrations/5302135`.
- What it does: AES-256-GCM with fail-closed production key validation; writes a mirrored `encrypted_pii` column.
- Missing controls: reads never decrypt through the helper; plaintext columns remain authoritative.
- Risks: control does not protect at-rest data (new finding).

### Item: RLS and database posture

- Evidence: `services/supabase.ts:198-226`, `lib/rls-startup-check.ts`, `supabase/migrations/5302100/5302112/5302434/5302436`, `scripts/check-rls-predicate.mjs`, `docs/RLS-rollout.md`.
- What it does: per-module opt-in user-scoped client; approved-aware `is_org_member`; anon least-privilege; CI guards for predicate regressions.
- Missing controls: writes default to service-role; API keys always service-role; deployed allowlist values external.
- Risks: tenant isolation remains application-layer by default (SEC-P2-007 partially fixed).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEC-001 | Auth provider | `middleware/auth.ts:100-177` | HS256 + Supabase fallback | MFA opt-in | P2 | Role-aware aal2 |
| SEC-002 | Session tokens/cookies | `cookie-domain.ts:14-26` | httpOnly/secure/lax, CSRF | No local revocation list | P3 | Document revocation |
| SEC-003 | JWT validation | `auth.ts:107`, `notifications.ts:89` | Signature verified | SSE omits algorithms pin | P3 | Pin algorithms |
| SEC-004 | CSRF/CORS | `csrf.ts`, `app.ts:101-106` | Double-submit | `*` reflects any origin | P3 | Reject `*` in prod |
| SEC-005 | Rate limits | `rate-limit.ts:42-66` | Per-email + per-IP | Email key case-split | P3 | Normalize email key |
| SEC-006 | Security headers | `security-headers.ts` | CSP/HSTS/CORP | Caddy legacy header | P3 | Align Caddy |
| SEC-007 | Input validation | Zod schemas; `security.ts` | Typed allowlists | Blocklist heuristics | P3 | Keep Zod contract |
| SEC-008 | File handling | `upload-validation.ts`; `documents.ts` | Sniff + org paths | Worker fetch TOCTOU | P2 | pinnedFetch everywhere |
| SEC-009 | API permissions | `permissions.ts` | requirePermission | Uncached; key scopes dead | P2 | Cache + enforce scopes |
| SEC-010 | Admin permissions | `admin.ts`, `admin-scope.ts` | Org pinning + allTenants | Role-assignment escalation | P1 | Shared super_admin guard |
| SEC-011 | Tenant isolation | `org-access.ts`, `tenant.ts` | Org-scoped reads/writes | RLS opt-in | P2 | Finish RLS rollout |
| SEC-012 | RLS policies | 5302100/5302112/5302434 | Approved-aware, least privilege | Write default service-role | P2 | Verify allowlists |

## Findings

Nine new findings were raised; thirty-one previous-register rows were re-verified (table below). New findings use the shared format without IDs (assigned by the aggregator).

### Finding: super_admin role can be granted through membership/onboarding/bulk-invite APIs without the /users/:id/role guard

- Severity: P1
- Confidence: High
- Area: SEC
- Evidence:
  - `apps/api/src/routes/users.ts:406-420` — the only path with the explicit `super_admin` assignment guard
  - `apps/api/src/validators/membership.ts:3-8`; `apps/api/src/routes/memberships.ts:95-104,123-139` — invite/PATCH accept any `roleId`
  - `apps/api/src/routes/bulk.ts:145-151`; `apps/api/src/validators/organization.ts:42`; `apps/api/src/routes/organizations.ts:77-125` — bulk invite and onboarding accept any role id/key
  - `apps/api/src/lib/roles.ts:27`; `apps/api/src/middleware/org-access.ts:37-60`; `apps/api/src/middleware/admin.ts:49-58` — `super_admin` is the cross-tenant, unpinned tier
- What is happening: role assignment is validated on one route only; the other three accept the caller's role choice, including `super_admin`.
- Why it matters: a delegable `users:manage` holder or tenant admin can promote any account (or themselves) into the trust tier that `ADMIN-P1-001` org pinning depends on.
- Security impact: cross-tenant read/write on every `requireOrgAccess`/`requireAdmin` surface, audited only as impersonation.
- Recommended fix: one shared `assertRoleAssignable(req, roleKey/roleId)` helper used by all four paths; DB trigger as backstop.
- Suggested validation: integration tests per path asserting a non-super-admin caller receives 403 when assigning `super_admin`.
- Owner suggestion: API principal engineer / security. Effort: M. Status: open.

### Finding: Worker monitoring checks are guard-then-fetch (DNS-rebinding TOCTOU)

- Severity: P2
- Confidence: High
- Evidence: `apps/worker/src/tasks/module-tasks.ts:540,548-551,590,602-605`; `fetchSslExpiry` at `:27-42`; contrast `apps/worker/src/tasks/webhook-dispatcher.ts:150` and `apps/worker/src/tasks/webhook-retry.ts:122` (pinnedFetch)
- What is happening: uptime/website monitor URLs are DNS-validated once and then fetched again; the SSL probe does a raw `tls.connect`.
- Why it matters: a tenant admin (monitor creation is a normal feature) can point a rebinding hostname at loopback/private addresses on the worker host.
- Security impact: SSRF into Redis/Prometheus/metadata from the production droplet.
- Recommended fix: use `pinnedFetch` for checks and pin the TLS socket; share the guard module between api/worker.
- Suggested validation: unit test with a resolver that returns a public address then a loopback address; assert the fetch is blocked.
- Owner suggestion: API/worker platform engineer. Effort: S–M. Status: open.

### Finding: PII field encryption is additive: plaintext profile columns remain the source of truth

- Severity: P2
- Confidence: High
- Evidence: `supabase/migrations/5302135_profiles_encrypted_pii.sql:3-6,25-26`; `apps/api/src/routes/profiles.ts:159-175` (writes both), `:61,108` (selects `*`); `lib/profile-pii.ts` decrypt helper unused on reads
- What is happening: every profile write stores an encrypted mirror next to unchanged plaintext columns.
- Why it matters: a DB read still yields plaintext; the control does not protect against the threat it targets.
- Recommended fix: decrypt on read, run the backfill, drop/blank plaintext; or document a dated cutover and stop advertising at-rest encryption.
- Suggested validation: test that a profile write leaves no plaintext in `full_name/email/phone/title` after cutover.
- Owner suggestion: API/backend + data governance. Effort: M–L. Status: open.

### Finding: Global role catalog is mutable by any org's roles:manage holder

- Severity: P2
- Confidence: Medium
- Evidence: `supabase/migrations/5302026_…v3.sql:161-168` (no org column); `apps/api/src/routes/roles.ts:96,139,185,252` (no org/platform gate), `:269-271` (only super_admin role protected); `apps/api/src/middleware/permissions.ts:63-88` (permission union with no org)
- What is happening: `roles`/`role_permissions` are global but writable with a tenant-scoped permission.
- Why it matters: delegated role managers can alter authorization for other tenants.
- Recommended fix: platform-admin gate for catalog mutations, or org-scope custom roles.
- Owner suggestion: API platform / security. Effort: M. Status: open.

### Finding: API-key scopes are stored but never enforced; keys always bypass RLS

- Severity: P2
- Confidence: High
- Evidence: `apps/api/src/middleware/api-key.ts:75,99`; `apps/api/src/middleware/auth.ts:70-82`; `middleware/permissions.ts` never reads `req.apiKey`; `apps/api/src/routes/api-keys.ts:17-21` (no permissions field), `:34-53` (GET ungated); `apps/api/src/services/supabase.ts:210` (`req.userJwt` required for RLS client)
- What is happening: keys act as the creating user; stored scopes are dead config; RLS never applies to keys.
- Recommended fix: intersect key permissions in `requirePermission` or drop the column; gate the list route; document the RLS bypass.
- Owner suggestion: API platform / security. Effort: S–M. Status: open.

### Finding: MFA enforcement is opt-in and the deployed default is false

- Severity: P2
- Confidence: High
- Evidence: `apps/api/src/lib/mfa.ts:28-30,84-95`; `apps/api/src/config/env.ts:64-67`; `.github/workflows/deploy-do.yml:693`; `infra/digitalocean/docker-compose.yml:89`; `docs/MFA.md:48,63`
- What is happening: enforcement requires an operator secret; deploy/compose default to `false`.
- Why it matters: admin/super_admin accounts can operate with password-only sessions.
- Recommended fix: enforce aal2 for admin roles or flip the prod default and document the rollout.
- Owner suggestion: API platform / security. Effort: S–M. Status: open.

### Finding: Sign-up confirmation redirect is built from the caller-controlled Host header

- Severity: P3
- Confidence: Medium
- Evidence: `apps/api/src/routes/auth.ts:182`; contrast `:33-57`; `apps/api/src/app.ts:174`; `apps/web/app/auth/callback/route.ts:8`; `supabase/config.toml.production.example:29-34`
- What is happening: `emailRedirectTo` echoes `req.get('host')` and points at a non-existent API route; only Supabase's redirect allowlist bounds the risk.
- Recommended fix: use `resolveTrustedRedirectOrigin` + the web callback path; add a spoofed-Host regression test.
- Owner suggestion: API team / security. Effort: S. Status: open.

### Finding: Analytics admin reads are not tenant-scoped and expose platform-wide event data including visitor IPs

- Severity: P3
- Confidence: High
- Evidence: `apps/api/src/routes/analytics.ts:64-91` (requireAdmin only); `supabase/migrations/5302106_store_analytics.sql:1-15` (no org column, IP/user-agent)
- What is happening: any tenant admin can read the platform-wide store analytics table.
- Recommended fix: restrict to super_admin / `resolveAdminTenantScope`, or org-scope the events.
- Owner suggestion: API platform / security. Effort: S. Status: open.

### Finding: Auth rate-limit key uses the raw email string without normalization

- Severity: P3
- Confidence: High
- Evidence: `apps/api/src/middleware/rate-limit.ts:48-53` vs `:61-64`
- What is happening: per-account throttling splits across case variants.
- Recommended fix: `email.trim().toLowerCase()` in both generators; unit test.
- Owner suggestion: API platform engineer. Effort: S. Status: open.

### Previous-register verification outcomes

| Title (same as previous register) | Status at 8d299b8d | Evidence / note |
|---|---|---|
| PII field encryption silently degrades to reversible plaintext | verified-fixed | `env.ts:100-108`, `field-encryption.ts:39-58`, `profiles.ts:159-175`; residual coverage gap is a new finding |
| Secret scanner echoes the matched secret value into CI logs | verified-fixed | `scripts/scan-secrets.sh:27-32` prints filenames only |
| Webhook SSRF guard has a DNS-rebinding TOCTOU window | verified-fixed | `pinnedFetch` in worker dispatch/retry + API test endpoint; monitoring residual is a new finding |
| Client-onboarding mutations run without `requirePermission` (authorization outlier) | verified-fixed | `client-onboarding-command-center.ts:20-21,41…` |
| MSP platform roles are cross-tenant for org access but not for permissions | verified-fixed | `roles.ts:26-37`; `org-access.ts:43-60`; `permissions.ts:26` |
| Forgot-password email redirect still uses attacker-controlled `Origin` header | verified-fixed | `auth.ts:33-57,327-330` + regression test |
| `GET /analytics/summary` calls a `get_analytics_summary` RPC that no migration defines | still-open | `analytics.ts:84`; repo-wide grep finds no definition |
| RLS is bypassed on API requests by default | partially-fixed | `supabase.ts:198-226`; `rls-startup-check.ts:40-46`; deployed secret values external (`unverified`) |
| CAPTCHA/Turnstile is bypassed when the secret is unset | verified-fixed | `env.ts:85-93`; `public.ts:132-144` |
| `/health` publicly discloses provider configuration and Redis errors | verified-fixed | `health.ts:131-161` |
| gitleaks generic-api-key/jwt hits are false positives | verified-fixed | `.gitleaks.toml`; `scripts/ci/verify-gitleaks-config.sh`; `secret-history-scan.yml` |
| `5302116` grants anon/authenticated full DML on every public table | verified-fixed | `5302434` revokes; no later re-grant |
| CORS reflects any origin with credentials when `CORS_ORIGIN="*"` | still-open | `app.ts:101-106`; deploy pins an allowlist (`deploy-do.yml:96`) |
| `notification-preferences` PUT accepts a body `organizationId` without `assertOrgScopeMatches` | verified-fixed | `org-access.ts:162-175,228,249` |
| `resolveEffectivePermissions` is uncached | still-open | `lib/permissions.ts` has no cache |
| Deprecated header and broad API CSP style directive | verified-fixed | `security-headers.ts:7-8,31-37` (Caddy leftover noted) |
| M365 webhook `clientState` is compared non-constant-time | verified-fixed | `timing-safe.ts`; `webhooks.ts:596` |
| Org-agnostic `requireAdmin` lets a tenant admin read other tenants' admin data | verified-fixed | `admin.ts:49-58`; `admin-scope.ts:55-57`; audit/search consumers |
| Impersonation/cross-tenant access is logged but not reviewable or alerted | verified-fixed | `audit.ts:122-191` (allTenants gate) |
| Bulk invite creates pre-confirmed auth accounts (and onboarding auto-approves admin) | still-open | `bulk.ts:108-116`; `organizations.ts:118-125` |
| Active-org cookie setter performs no server-side authorization | still-open | `org-actions.ts:8-18`; API validates memberships |
| Low-trust MSP role key composes into a cross-tenant read pivot | verified-fixed | `roles.ts` split + consumers |
| Caller-controlled reset redirect composes into an account-takeover assist | verified-fixed | `auth.ts:327-330` + tests |
| Client-onboarding mutations run without any `requirePermission` gate | verified-fixed | same evidence as SEC-P2-003 |
| `PLATFORM_ADMIN_KEYS` and `ADMIN_BYPASS_KEYS` are inconsistent trust sets | verified-fixed | remaining `isPlatformAdminKey` uses are in-org (`tickets.ts:190-195,443-451`) |
| API keys store `expires_at` but nothing enforces or prunes expiry | partially-fixed | enforced at `api-key.ts:82`; no prune task in worker |
| API keys cannot authenticate; the feature is dead | verified-fixed | `middleware/api-key.ts` + `auth.ts:67-88` + tests |
| M365 webhook secret is dead config while the real auth value is undeployed | verified-fixed | `env.ts:56-59`; `.env.example:32-34`; `deploy-do.yml:597,689` |
| Deploy pipeline does not write several secret-class env vars | verified-fixed | `deploy-do.yml:647,689-708` |
| Public file-request upload authorizes with a permission unioned across all orgs | verified-fixed | `file-requests.ts:109-159,184-237` |
| Web middleware gates routes on an unverified JWT `exp` | partially-fixed | documented non-authoritative UX gate (`middleware.ts:5-16`); API is the control |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Tenant admin/user-manager escalates to super_admin membership | P1 | Medium | Cross-tenant access | `memberships.ts:95-139`; `bulk.ts:145-151`; `organizations.ts:77-125` | Shared role-assignment guard |
| Worker SSRF via monitoring DNS rebinding | P2 | Medium | Internal service/metadata access | `module-tasks.ts:540-605` | pinnedFetch + pinned TLS |
| API-key scope confusion | P2 | Low | Over-privileged machine access | `api-key.ts`; `permissions.ts` | Enforce or drop scopes |
| PII encryption gives false assurance | P2 | High | Data exposure at rest | `5302135`; `profiles.ts` | Complete cutover |
| Admin accounts without MFA | P2 | Medium | Account takeover | `mfa.ts`; `deploy-do.yml:693` | Role-aware aal2 |
| Global RBAC catalog mutated per-tenant | P2 | Low | Cross-tenant authz drift | `roles.ts`; `5302026:161` | Platform gate / org-scoped roles |

## Recommendations

### Immediate / Release Blocking
1. Fix the role-assignment guard (P1) on all four paths; add regression tests.

### This Week
2. Decide and schedule the PII cutover (P2) or document the scaffold explicitly.
3. Enforce or remove API-key scopes; gate `GET /api-keys` (P2).
4. Move monitoring fetches to `pinnedFetch` (P2).

### This Month
5. Platform-gate global role/permission mutations (P2).
6. Enforce aal2 for admin roles or flip the prod default (P2).
7. Restrict platform analytics reads; fix or remove the undefined RPC (P3).
8. Add expiry pruning for API keys (P2, residual of ACM-P2-006).

### Later / Platform Evolution
9. Finish the RLS rollout (writes) and verify deployed allowlists (P2).
10. Normalize rate-limit keys; pin algorithms in SSE revalidation; align Caddy headers (P3).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Normalize auth rate-limit email key | Closes a per-account throttle split | `middleware/rate-limit.ts` | Unit test with case variants |
| Use `resolveTrustedRedirectOrigin` for sign-up | Removes Host echo | `routes/auth.ts` | Spoofed-Host test |
| Add `algorithms: ["HS256"]` to SSE revalidation | Consistency with `auth.ts` | `routes/notifications.ts` | Unit test |
| Require permission on `GET /api-keys` | Matches docs/intent | `routes/api-keys.ts` | Route-auth test |
| Drop `X-XSS-Protection` from Caddyfile | Header consistency | `infra/digitalocean/Caddyfile.prod` | Header check |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Shared `assertRoleAssignable` + DB trigger backstop | P1 | API security | M | None |
| PII plaintext cutover + backfill verification | P2 | Backend/data | M–L | `FIELD_ENCRYPTION_KEY` deployed |
| API-key scope enforcement + UI | P2 | API platform | M | Product decision |
| Monitoring SSRF pinned fetch | P2 | Worker platform | S | None |
| Global RBAC mutation platform gate | P2 | API platform | M | None |
| Admin aal2 policy | P2 | API security | S–M | Supabase MFA enabled |
| Permission resolution cache | P3 | API platform | M | Invalidation hooks |
| SSE/`jwt.verify` algorithm pinning sweep | P3 | API platform | S | None |
| API-key expiry prune task | P2 | Worker platform | S | None |

## Suggested Tests

- Unit: role-assignment guard matrix (4 routes × caller roles × target roles, including `super_admin` denial).
- Unit: `pinnedFetch` used by module-tasks (mock resolver returns public then loopback).
- Unit: profile write/read with encryption cutover; assert no plaintext columns after migration.
- Unit: rate-limit key normalization (case/whitespace variants share a bucket).
- Integration: API-key with restricted DB `permissions` receives 403 on an unlisted module.
- Integration: `PATCH /memberships/:id` by a `users:manage` non-admin cannot set `super_admin`.
- Security/regression: spoofed `Host` on sign-up does not change `emailRedirectTo`.
- CI: extend `scripts/check-rls-predicate.mjs`-style static guard to assert every `supabase.rpc()` called in `apps/api` exists in migrations.

## Suggested Documentation Updates

- `docs/MFA.md` — role-aware enforcement and the deployed default.
- `docs/RLS-rollout.md` — document the API-key and platform-admin service-role bypasses; state how to verify deployed allowlist values.
- `docs/modules/api-keys.md` — either document scope enforcement or remove `permissions` from the data model.
- `docs/ENVIRONMENT_VARIABLES.md` — add the CORS `*` credential caveat.
- `SECURITY.md` / threat model — record the role-assignment trust boundary and the monitoring SSRF surface.
- `docs/RLS-coverage-matrix.md` — refresh after the write-side rollout.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are the deployed `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` secrets actually populated as docs claim (~44/17 modules)? | Determines real RLS coverage | GitHub secret listing / droplet `.env` (operator) |
| Is the Supabase redirect allowlist pinned to the web origin only? | Bounds the sign-up Host echo | Supabase project auth settings (operator) |
| Are API-key scopes intended to be enforced, or is the column vestigial? | Determines fix direction | Product/API decision |
| Is `super_admin` membership intended to be assignable by tenant admins? | The P1 fix depends on the intended model | Security owner decision |
| Has the PII backfill script ever run in production? | Determines cutover effort | `scripts/backfill-profile-pii.mjs` run log (operator) |

## Appendix

- Reproduce the P1: as a caller with `users:manage` in org A, `PATCH /api/v1/memberships/:ownMembershipId` with `{"roleId": "<super_admin role uuid>", "status": "approved"}`; the handler (`memberships.ts:123-139`) updates without the `users.ts:411-419` guard.
- Reproduce the SSRF residual: configure an uptime check whose hostname answers `A 93.184.216.34` for the guard lookup and `A 127.0.0.1` for the worker fetch (`module-tasks.ts:540-551`); observe the fetch executes against loopback.
- RLS helper lineage: `is_org_member` approved filter added in `5302100:8-20`, `search_path` pinned in `5302112:19`, predicate regressions guarded by `scripts/check-rls-predicate.mjs` (baseline 5302430).
- Topology: Caddy (`infra/digitalocean/Caddyfile.prod`) terminates 80/443 and proxies to `api:4000`/`web:3000`; the API container publishes no host port, so `trust proxy: 1` + the localhost rate-limit skip cannot be reached by spoofed `X-Forwarded-For` from the public internet.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P1-001 | P1 | super_admin role can be granted through membership/onboarding/bulk-invite APIs without the /users/:id/role guard |
| SEC-P2-001 | P2 | Worker monitoring checks are guard-then-fetch (DNS-rebinding TOCTOU); webhook path is pinned but uptime/website checks and SSL probe are not |
| SEC-P2-002 | P2 | PII field encryption is additive: plaintext profile columns remain the source of truth and are still returned |
| SEC-P2-003 | P2 | Global role catalog is mutable by any org's roles:manage holder (roles are not org-scoped) |
| SEC-P2-004 | P2 | API-key scopes are stored but never enforced; keys act with the creating user's full permissions and always bypass RLS |
| SEC-P2-005 | P2 | MFA enforcement is opt-in and the deployed default is false |
| SEC-P3-001 | P3 | Sign-up confirmation redirect is built from the caller-controlled Host header and targets a non-existent API route |
| SEC-P3-002 | P3 | Analytics admin reads are not tenant-scoped and expose platform-wide event data including visitor IPs |
| SEC-P3-003 | P3 | Auth rate-limit key uses the raw email string without normalization |
| SEC-P1-002 | P1 | PII field encryption silently degrades to reversible plaintext |
| SEC-P2-006 | P2 | Secret scanner echoes the matched secret value into CI logs |
| SEC-P2-007 | P2 | Webhook SSRF guard has a DNS-rebinding TOCTOU window |
| SEC-P2-008 | P2 | Client-onboarding mutations run without `requirePermission` (authorization outlier) |
| SEC-P2-009 | P2 | MSP platform roles are cross-tenant for org access but not for permissions (inconsistent trust model) |
| SEC-P2-010 | P2 | Forgot-password email redirect still uses attacker-controlled `Origin` header |
| SEC-P2-011 | P2 | `GET /analytics/summary` calls a `get_analytics_summary` RPC that no migration defines |
| SEC-P2-012 | P2 | RLS is bypassed on API requests by default (service-role is the default client) |
| SEC-P2-013 | P2 | CAPTCHA/Turnstile is bypassed when the secret is unset |
| SEC-P2-014 | P2 | `/health` publicly discloses provider configuration and Redis errors |
| SEC-P3-004 | P3 | gitleaks generic-api-key/jwt hits are false positives (no tracked secret) |
| SEC-P3-005 | P3 | `5302116` grants anon/authenticated full DML on every public table (RLS is the only gate) |
| SEC-P3-006 | P3 | CORS reflects any origin with credentials when `CORS_ORIGIN="*"` |
| SEC-P3-007 | P3 | `notification-preferences` PUT accepts a body `organizationId` without `assertOrgScopeMatches` |
| SEC-P3-008 | P3 | `resolveEffectivePermissions` is uncached and fans out 4–6 queries per gated request |
| SEC-P3-009 | P3 | Deprecated header and broad API CSP style directive |
| SEC-P3-010 | P3 | M365 webhook `clientState` is compared non-constant-time |
| SEC-P1-003 | P1 | Org-agnostic `requireAdmin` lets a tenant admin read other tenants' admin data |
| SEC-P1-004 | P1 | Impersonation/cross-tenant access is logged but not reviewable or alerted |
| SEC-P2-015 | P2 | Bulk invite creates pre-confirmed auth accounts (and org onboarding auto-approves admin) |
| SEC-P3-011 | P3 | Active-org cookie setter performs no server-side authorization |
| SEC-P1-005 | P1 | Low-trust MSP role key composes into a cross-tenant read pivot |
| SEC-P1-006 | P1 | Caller-controlled reset redirect composes into an account-takeover assist |
| SEC-P1-007 | P1 | Client-onboarding mutations run without any `requirePermission` gate |
| SEC-P2-016 | P2 | `PLATFORM_ADMIN_KEYS` (org traversal) and `ADMIN_BYPASS_KEYS` (permission bypass) are inconsistent trust sets |
| SEC-P2-017 | P2 | API keys store `expires_at` but nothing enforces or prunes expiry |
| SEC-P2-018 | P2 | API keys cannot authenticate; the feature is dead |
| SEC-P1-008 | P1 | M365 webhook secret is dead config while the real M365 auth value is undocumented and undeployed |
| SEC-P1-009 | P1 | Deploy pipeline does not write several secret-class env vars the API schema and compose reference |
| SEC-P1-010 | P1 | Public file-request upload authorizes with a permission unioned across all orgs |
| SEC-P3-012 | P3 | Web middleware gates routes on an unverified JWT `exp` |
