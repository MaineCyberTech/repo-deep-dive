# Security, Authorization, and Tenancy — re-audit verification (main @ 7dd0402)

## Audit Metadata

- Audit name: mainecybertech
- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Repository: `github.com/MaineCyberTech/mainecybertech`
- Branch: `main` (audited ref `origin/main`)
- Commit SHA: `7dd040234e8dfa40dd2d2b6fe1ca7379f2fba097`
- Generated at: 2026-10-14
- Auditor: subagent (full-domain verification re-audit, group 1)
- Area code: SEC
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261014-0033-full-main-7dd0402/06_security_authz_tenancy_audit.md`
- Scope limitations: read-only static review; no runtime probing, no database access. Deployed secret values
  (`RLS_READS_ENABLED`, `RLS_WRITES_ENABLED`, environment allow-lists) remain operator-side and unverified.

## Scope

Re-verification of all 40 SEC findings from the previous full run at the current `origin/main`, plus a
security scan of code added since that run (220 non-merge commits, 115 files changed under `apps/api/src`).
Reviewed surfaces: authn (JWT/API-key/MFA), authz middleware (`admin`, `permissions`, `org-access`),
rate limiting, CORS/CSRF/security headers, SSRF guards and pinned fetch, webhook verification, file upload
validation and storage policy, PII field encryption, RLS posture, secret scanning, and the new
`final/*`/`registerCrud` routes.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/lib/role-assignment.ts`, `routes/{memberships,bulk,organizations,users}.ts` | Source | Role-assignment escalation paths | Shared guard on all four paths |
| `apps/api/src/config/env.ts`, `lib/field-encryption.ts` | Source | Fail-closed production validation | Turnstile, PII key, CORS |
| `apps/api/src/middleware/{admin,permissions,api-key,auth,rate-limit,org-access}.ts` | Source | Authz gates + key scoping | Key scope cap before admin bypass |
| `apps/api/src/lib/{pinned-fetch,ssrf-guard}.ts` + worker webhook tasks | Source | SSRF/DNS-rebinding | Redirects not followed, 64 KiB cap |
| `supabase/migrations/5302434, 5302437, 5302440, 5302459` | Migration | anon grants, super-admin trigger, RPC, dead predicates | All present and consistent |
| `scripts/scan-secrets.sh`, `.gitleaks.toml`, `scripts/ci/verify-gitleaks-config.sh` | Script/Config | Secret handling in CI | File names only |
| `apps/api/src/routes/final/crud.ts`, `final/*.ts`, `sla.ts` | Source | New routes since the last run | No permission gates on reads (new finding) |

## Verification Performed

- Grep/line inspection of every evidence file cited in the 40 previous findings; no runtime tests were run
  (no Node toolchain in the sandbox), so statuses rely on source evidence and the checked-in test files.
- Scanned all mutating-verb route blocks for missing auth/permission gates; scanned all `requirePermission`
  literals for `view` on mutating verbs.
- Verified the M365 clientState comparison is timing-safe and fails closed.
- Verified the anon-grant migration and the super-admin trigger are the last writers of their policies.

## Executive Summary

The security posture holds up well. Of the 40 previously raised findings, 37 are verified fixed at
`7dd04023`, three remain partially fixed (additive PII encryption, RLS rollout, and the by-design web
middleware exp gate), and none regressed. The strongest improvements since the last run are the central
role-assignment guard, the `is_super_admin` database trigger, API-key scope enforcement with a pruner,
fail-closed production env validation, and pinned-fetch SSRF protection across API and worker webhooks.

One new issue was raised: the `final/*` and `registerCrud` module reads/compute endpoints have no
`requirePermission` gate (SEC-P3-013, security lens of ACM-P3-008) — any approved org member can read
module data for their own tenant without the corresponding `view` grant. No cross-tenant path was found.

## Findings

| ID | Sev | Status | Title | Re-verification evidence |
|---|---|---|---|---|
| SEC-P1-001 | P1 | verified-fixed | super_admin role can be granted without the users/:id/role guard | `lib/role-assignment.ts:20-43,76`; call sites memberships.ts:90-91,151-161, bulk.ts:65-66, organizations.ts:93, users.ts:491-492 |
| SEC-P1-002 | P1 | verified-fixed | PII field encryption silently degrades to plaintext | `env.ts:172-181,195-196`; `field-encryption.ts:38-52` throws in prod |
| SEC-P1-003 | P1 | verified-fixed | Org-agnostic `requireAdmin` cross-tenant reads | `middleware/admin.ts:22-64`; `lib/admin-scope.ts:29-71` |
| SEC-P1-004 | P1 | verified-fixed | Impersonation logged but not reviewable | `routes/audit.ts:126-158,172-191` allTenants gate |
| SEC-P1-005 | P1 | verified-fixed | Low-trust MSP role cross-tenant pivot | `@mct/sdk/role-keys` split; `lib/roles.ts` re-export |
| SEC-P1-006 | P1 | verified-fixed | Caller-controlled reset redirect | `routes/auth.ts:34-61,347` |
| SEC-P1-007 | P1 | verified-fixed | Client-onboarding mutations ungated | `client-onboarding-command-center.ts:32-33,50-247` |
| SEC-P1-008 | P1 | verified-fixed | M365 webhook secret dead config | `env.ts:102-105`; `deploy-do.yml:688,787` |
| SEC-P1-009 | P1 | verified-fixed | Deploy pipeline misses secret env vars | `scripts/check-env-parity.mjs`; `unit-tests/action.yml:83-84` |
| SEC-P1-010 | P1 | verified-fixed | Public file-request upload permission union | `routes/file-requests.ts:114-160,197-275` token/org bound |
| SEC-P2-001 | P2 | verified-fixed | Worker monitor DNS-rebinding TOCTOU | `module-tasks.ts:606-624,656-681`; `fetchSslExpiry` pins (:34-80) |
| SEC-P2-002 | P2 | partially-fixed | PII encryption is additive | Reads decrypt (`profile-pii.ts:39-58`); plaintext columns still written (`profiles.ts:165-187`); no drop migration |
| SEC-P2-003 | P2 | verified-fixed | Global role catalog mutable by tenant managers | `role-assignment.ts:47-72`; `roles.ts:103,149,197,273` |
| SEC-P2-004 | P2 | verified-fixed | API-key scopes never enforced | `middleware/permissions.ts:73-79` |
| SEC-P2-005 | P2 | verified-fixed | MFA enforcement opt-in / default false | `lib/mfa.ts:48-74,140-152` privileged aal2 unconditional |
| SEC-P2-006 | P2 | verified-fixed | Secret scanner echoes matched value | `scripts/scan-secrets.sh:27-32` file names only |
| SEC-P2-007 | P2 | verified-fixed | Webhook SSRF DNS-rebinding TOCTOU | `pinned-fetch` in API+worker dispatch/retry/test |
| SEC-P2-008 | P2 | verified-fixed | Client-onboarding ungated (duplicate lens) | Same gate as SEC-P1-007 |
| SEC-P2-009 | P2 | verified-fixed | MSP roles inconsistent trust model | Role-key tiers + catalog parity test |
| SEC-P2-010 | P2 | verified-fixed | Forgot-password redirect uses Origin | `auth.ts:347` |
| SEC-P2-011 | P2 | verified-fixed | `get_analytics_summary` RPC undefined | `5302440:19-36`; `analytics.ts:106` |
| SEC-P2-012 | P2 | partially-fixed | RLS bypassed by default (service role) | `rls-startup-check.ts:29-64` + `main.ts:19` fail closed on empty reads; deployed allow-list unverifiable; writes warn only |
| SEC-P2-013 | P2 | verified-fixed | Turnstile bypass when unset | `env.ts:141-147`; `public.ts:71,185-188` |
| SEC-P2-014 | P2 | verified-fixed | `/health` discloses provider config | `health.ts:150-161` METRICS_TOKEN gate |
| SEC-P2-015 | P2 | verified-fixed | Bulk invite pre-confirmed accounts | `bulk.ts:163`; `organizations.ts:127-138` pending |
| SEC-P2-016 | P2 | verified-fixed | PLATFORM_ADMIN_KEYS vs ADMIN_BYPASS_KEYS | Split in `@mct/sdk/role-keys`; `permissions.ts:71` |
| SEC-P2-017 | P2 | verified-fixed | API-key expiry unenforced/unpruned | `api-key.ts:83-88`; prune task `index.ts:51`, `schedule-config.ts:50` |
| SEC-P2-018 | P2 | verified-fixed | API keys cannot authenticate | `middleware/auth.ts:68-88`; `middleware/api-key.ts` |
| SEC-P3-001 | P3 | verified-fixed | Signup redirect from Host header | `auth.ts:193` |
| SEC-P3-002 | P3 | verified-fixed | Analytics admin reads not tenant-scoped | `analytics.ts:78-110`; `5302446` drops PII columns |
| SEC-P3-003 | P3 | verified-fixed | Auth rate-limit key unnormalized | `rate-limit.ts:51-58` normalize+hash |
| SEC-P3-004 | P3 | verified-fixed | gitleaks false positives | `.gitleaks.toml` + negative-fixture verifier |
| SEC-P3-005 | P3 | verified-fixed | `5302116` blanket anon DML | `5302434` revokes + narrow allowlist; `5302458` narrows more |
| SEC-P3-006 | P3 | verified-fixed | CORS reflects any origin with `*` | `env.ts:49-54`; `app.ts:94-106` fails closed |
| SEC-P3-007 | P3 | verified-fixed | notification-preferences body org | `org-access.ts:162-173,228,249`; `notification-preferences.ts:64-70` |
| SEC-P3-008 | P3 | verified-fixed | `resolveEffectivePermissions` uncached | `lib/permissions.ts:34-45` 15s cache + invalidation |
| SEC-P3-009 | P3 | verified-fixed | Deprecated header / broad CSP | `security-headers.ts:7-8,29-36`. Residual (cosmetic): `infra/digitalocean/Caddyfile.prod:12,35` still emits X-XSS-Protection |
| SEC-P3-010 | P3 | verified-fixed | M365 clientState non-constant-time | `webhooks.ts:887` timingSafeCompare; missing state fails closed |
| SEC-P3-011 | P3 | verified-fixed | Active-org cookie setter unauthorized | `apps/web/lib/org-actions.ts:21-50` |
| SEC-P3-012 | P3 | partially-fixed | Web middleware gates on unverified exp | `apps/web/middleware.ts:1-16` documented non-authoritative UX gate; behavior unchanged by design |
| SEC-P3-013 | P3 | **open (new)** | `final/*` + `registerCrud` reads have no `requirePermission` gate | `final/crud.ts:33-59,88-103`; `final/procurement.ts:8`; `final/sharepoint.ts:7`; `final/backups.ts:7,22`; `final/budgets.ts:7`; `final/time-entries.ts:11`; `sla.ts:13`; catalog view actions exist (`5302118:182-185`) |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| In-tenant module reads without a view grant (new) | P3 | Medium | Low-Med (info disclosure within tenant) | SEC-P3-013 | Add `requirePermission(module,'view')` to the factory reads and final/* routes |
| Plaintext PII duplicates remain in `profiles` | P2 | Low (needs DB read) | Medium | SEC-P2-002 | Run the backfill, then drop/blank plaintext columns |
| RLS not the enforcement layer for unlisted modules | P2 | Medium | Medium-High | SEC-P2-012 | Continue the allow-list rollout; publish deployed values |
| Impersonation log write can be dropped | P3 | Low | Medium (audit gap) | `services/impersonation.ts` fire-and-forget | Queue/await the write (tracked under MT-P2-005) |

## Recommendations

### This Week

1. Gate the `registerCrud` list/get handlers and the `final/*` module reads with
   `requirePermission(module, "view")`; add a denial test for a client role (SEC-P3-013 / ACM-P3-008).
2. Complete the PII cutover: run `scripts/backfill-profile-pii.mjs`, then ship a migration that drops or
   blanks the plaintext `full_name/email/phone/title` columns (SEC-P2-002).

### This Month

3. Record the deployed `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` values in a checked-in template and keep
   extending write coverage (SEC-P2-012 / ACM-P2-002).
4. Drop the legacy `X-XSS-Protection` header from `infra/digitalocean/Caddyfile.prod` to finish SEC-P3-009.

## Suggested Tests

- Integration: a `client_user` calling `/api/v1/final/time-entries` (and each `final/*` list) gets 403 once
  gated; a `technician` with `time-entries:view` gets 200.
- DB: after the cutover, a profile write leaves no plaintext PII in `full_name/email/phone/title`.
- CI: assert the permission-catalog guard covers `registerCrud` module keys (it does) and add a per-route
  `requirePermission` coverage check for read handlers.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are the deployed RLS allow-lists populated? | Determines real RLS coverage | Droplet environment (operator) |
| Is the `ai:view` triage gate on POST /triage/analyze permanent? | Action-vocabulary contract | Product decision |
| Are `final/*` reads intentionally member-visible? | Decides gate vs document | Product decision |
