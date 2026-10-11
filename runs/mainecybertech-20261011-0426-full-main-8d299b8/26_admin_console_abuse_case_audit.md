# 26_admin_console_abuse_case_audit — Prompt 26 - Admin Console Abuse Case Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `26_admin_console_abuse_case_audit.md` (area ADMIN, prompt)

## Verification Performed

# Admin Console Abuse Case Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening rerun)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (read-only worktree at `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (`8d299b8d`)
- Generated at: 2026-10-11
- Auditor: domain subagent (26_admin_console_abuse_case_audit)
- Area code: ADMIN
- Output path (pack convention): `docs/audits/repo-deep-dive/{run}/26_admin_console_abuse_case_audit.md`
- Scope limitations: read-only static review; no runtime/API execution, no production access, no lab. Rate-limit and Stripe behavior assessed from code/config only.

## Scope

Reviewed: admin/organization/user/role APIs and web admin UI; destructive deletes; confirmations; bulk invite; bulk document/ticket operations; approval flows; impersonation logging and review; billing panel entry points; webhook/API-key admin; admin settings; exports; audit logging of role/delete/export actions; tests covering these.

Not reviewed in depth (owned by other domains): RLS policy design (37), multi-tenant attack simulation (25), billing reconciliation (29), file upload/download (28), webhook delivery/replay (27), secrets/CI/infra.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/routes/admin.ts` (90 lines) | API | Super-admin tenant list + test-email | GET /organizations gated on `profiles.is_super_admin`; test-email rate-limited + audited |
| `apps/api/src/middleware/admin.ts` | API | `requireAdmin` org-pinning | Lines 49-58: pinned org requires admin in that org unless super_admin |
| `apps/api/src/lib/admin-scope.ts` | API | Single cross-tenant decision point | `resolveAdminTenantScope` / `applyOrgScope` / `applyRequestedOrg` |
| `apps/api/src/middleware/org-access.ts` | API | Cross-tenant reach + impersonation logging | admin/super_admin role keys cross tenants (audited) |
| `apps/api/src/routes/organizations.ts` | API | Org CRUD, onboard, domains, logo, delete | Delete cascades, no confirm; onboard auto-approves admin |
| `apps/api/src/routes/memberships.ts`, `users.ts`, `roles.ts` | API | User/org/role management | Role assignment guard gap |
| `apps/api/src/routes/bulk.ts` | API | Bulk invite | `email_confirm: true` accounts; arbitrary `roleId` |
| `apps/api/src/routes/documents.ts`, `tickets.ts` | API | Document/ticket admin + bulk ops | 4 confirm-gated deletes; bulk ops no preview |
| `apps/api/src/routes/approvals.ts`, `services/approvals.ts` | API | Approval flows | No self-approval guard; cancel any state |
| `apps/api/src/routes/audit.ts`, `services/impersonation.ts`, `lib/metrics.ts` | API | Audit + impersonation review | Export audit gaps |
| `apps/api/src/routes/api-keys.ts`, `webhook-management.ts` | API | Webhook/API-key admin | SSRF guard, masked secrets, confirm + audit |
| `apps/api/src/routes/billing.ts` | API | Billing panel entry points | Portal session open to any member |
| `apps/api/src/routes/roles.ts`, `lib/permissions.ts`, `middleware/permissions.ts` | API | Role/permission model | Delegable `users:manage`/`roles:manage`; admin bypass |
| `apps/api/src/lib/delete-confirm.ts`, `middleware/rate-limit.ts`, `app.ts` | API | Confirmations, rate limits | 4/59 deletes confirmed; two global limiters only |
| `apps/api/src/services/audit.ts` | API | Audit write path | 3 retries, PII key redaction, no delete policy on `audit_logs` |
| `apps/web/lib/auth/admin.ts`, `lib/roles.ts`, `lib/org-actions.ts`, `lib/auth/membership.ts` | Web | Admin gate, role keys, active-org cookie | 8-key UI gate vs 2-key API gate; unguarded cookie setter |
| `apps/web/components/admin/*` (`AdminDocumentsBulkControls`, `BulkInviteForm`, `AdminOrganizationsClient`, `RolePermissionsEditor`, `AdminApiKeysClient`, `SuperAdminOrgSwitcher`) | Web | Admin UI abuse surfaces | Bulk UI count-only; role editor can delegate manage permissions |
| `apps/web/app/(admin)/admin/**` (203 `page.tsx`) | Web | Admin page gating | 165 call `requireAdminAccess`; the rest use `ModuleDetailPage` (which calls it) or redirect — no ungated page found |
| `supabase/migrations/5302432_drop_unused_soft_delete_columns.sql`, `5302424_manage_actions.sql`, `5302408_store_tenant_scoping.sql`, `5302026...v3.sql` | SQL | Deletion semantics, delegable manage perms, store scoping, FK cascades | See findings |
| `docs/ADMIN_FEATURES.md`, `docs/API_RATE_LIMITING.md`, `docs/ROLLBACK_PROCEDURES.md`, `CHANGELOG.md` | Docs | Claimed behavior | Export-audit claim over-broad; hard-delete documented |
| `apps/api/src/__tests__/{admin,organizations,bulk,memberships,audit,documents,tickets,api-keys,webhook-management}.test.ts` | Tests | Control coverage | Good scoping/confirm/impersonation coverage; no escalation/self-approval tests |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse HEAD` → `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` | command | Bind findings to commit | Target worktree clean, read-only |
| `git log --oneline 9c0b88c..8d299b8d` → 113 commits | command | What changed since previous run | Admin-relevant: `24aa512a` (ADMIN-P2-001 export audit), `0dd81973` (FILE-P2-006 CSV safety), `a499e03a` (SEARCH-P2-004), `36e5f723` (IR-P2-001 metrics) |
| `grep -rn "assertDeleteConfirmed" apps/api/src` → lib + 4 call sites | command | Confirmation coverage | api-keys.ts:148, documents.ts:567, tickets.ts:494, webhook-management.ts:374 |
| `grep -rn "router.delete(" apps/api/src/routes | wc -l` → 59 | command | Destructive-action inventory | Only 4/59 confirmation-gated |
| Python scan of each DELETE handler for `logAuditEvent` / `assertDeleteConfirmed` | command | Audit + confirm matrix | 7 handlers hard-delete without audit; 55 without confirm |
| `grep -n "email_confirm" apps/api/src/routes/bulk.ts` → line 114 `email_confirm: true` | command | ADMIN-P2-004 verification | Pre-confirmed auth accounts |
| `grep -n "status: \"approved\"" apps/api/src/routes/organizations.ts` → line 124 | command | ADMIN-P2-004 verification | Onboard auto-approves admin membership |
| `grep -rn "resolveAdminTenantScope|applyOrgScope" apps/api/src/routes` → audit/dashboard/search/business-os/approvals/assets/proposals/findings/domain-monitors/tickets/projects/store/billing | command | ADMIN-P1-001/P3-003 verification | Shared scope applied broadly |
| `grep -rn "impersonation" apps/api/src infra/digitalocean` → audit endpoints, service, metric, Prometheus rule `infra/digitalocean/prometheus.rules.yml:45-56` | command | ADMIN-P1-002 verification | Review + alert present |
| `git merge-base --is-ancestor 925ec007 9c0b88c` → true | command | ADMIN-P2-006 verification | Soft-delete drop predates the previous run; previous "columns exist" note was stale |
| `grep -rn "rateLimit" apps/api/src/app.ts apps/api/src/routes` → global IP + per-user + auth/test-email only | command | ADMIN-P2-005 verification | No destructive-op-specific limiter |
| `grep -rn "requireAdminAccess" apps/web/app/(admin)` + scan of the remaining 38 pages | command | Admin UI gating | All 203 admin pages gated (165 direct, 38 via ModuleDetailPage/redirect) |
| `grep -rn "\.export" apps/api/src/routes` vs `logAuditEvent` | command | Export audit matrix | 8 audited; impersonation/satisfaction/onboarding/dynamic-forms not |
| `git log --oneline 9c0b88c..8d299b8d -- <admin files>` | command | Confirm no unseen admin changes | Only export-audit + search-pagination touched admin code |

## Executive Summary

The admin surface is materially safer than at the previous run. The ADMIN-P1-001 org-scoping fix is intact and broadly applied (audit, dashboard, search, business-os, organizations, approvals/assets/projects/tickets exports), impersonation is now reviewable and alerted, exports were mostly brought under audit logging, and the store catalog is org-pinned. The web admin gate is consistently applied to all 203 admin pages.

Remaining risk concentrates in four places. (1) **Role assignment has no cross-tenant-role guard** on the memberships/onboard paths: a delegated `users:manage`/`roles:manage` holder can assign themselves the `admin`/`super_admin` role key and gain cross-tenant reach plus permission bypass — the users.ts guard proves the policy exists but is not enforced everywhere. (2) **Destructive actions are unevenly protected**: only 4 of 59 DELETE handlers require a confirmation body, organization delete cascades to all tenant data with no confirmation and no in-app recovery, and 7 deletes leave no audit event. (3) **Approvals can be self-approved** and approved requests can be cancelled afterwards. (4) **Bulk operations (documents, store import, bulk invite) apply without preview/dry-run**, and bulk invite still creates pre-confirmed accounts with a never-delivered password while onboarding auto-approves admin memberships. A minor billing-panel gap (any org member can open the Stripe portal) rounds out the abuse-case set.

Recommended next actions: fix the role-assignment policy first (P1), then add confirmation + audit to destructive endpoints, a self-approval guard, and export audit coverage for the four remaining exports.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Admin gate (API) | `apps/api/src/middleware/admin.ts:22-63` | `requireAdmin` role + org-pin | Implemented | Medium | Pinned-org branch denies plain `admin` outside pinned org |
| Tenant scope helper | `apps/api/src/lib/admin-scope.ts:28-99` | allTenants/orgIds decision | Implemented | Low | Single decision point, fails closed |
| Admin tenant list | `apps/api/src/routes/admin.ts:18-51` | Super-admin org list | Implemented | Low | `is_super_admin` only, paginated |
| Test email | `apps/api/src/routes/admin.ts:54-88` | SMTP check | Implemented | Low | `rateLimitEmail`, audited |
| Org CRUD | `apps/api/src/routes/organizations.ts` | Org create/update/onboard/domains/logo/delete | Implemented | High | Delete cascades, no confirm; onboard auto-approve |
| Membership admin | `apps/api/src/routes/memberships.ts` | Invite/patch/delete memberships | Implemented | High | `roleId` unguarded (self-escalation) |
| User admin | `apps/api/src/routes/users.ts` | List/detail/role/permissions | Implemented | High | Guards `super_admin` only on `/role`; no self block |
| Role admin | `apps/api/src/routes/roles.ts` | Role CRUD + permission matrix | Implemented | Medium | `roles:manage` can delegate any catalog permission |
| Bulk invite | `apps/api/src/routes/bulk.ts` | CSV/array invite up to 500 | Implemented | High | Confirmed accounts; arbitrary role; no preview |
| Document admin | `apps/api/src/routes/documents.ts` | CRUD, bulk folder/metadata, delete | Implemented | Medium | Delete confirm; bulk no preview; org pre-filter |
| Ticket admin | `apps/api/src/routes/tickets.ts` | CRUD, bulk update, delete, export | Implemented | Medium | Delete confirm; bulk update org-filtered |
| Approvals | `apps/api/src/routes/approvals.ts`, `services/approvals.ts` | Request/approve/reject/cancel | Implemented | Medium | Self-approval; cancel any state |
| Audit/impersonation | `apps/api/src/routes/audit.ts` | Audit list/export, impersonation review | Implemented | Medium | Impersonation export un-audited |
| API keys | `apps/api/src/routes/api-keys.ts` | Key create/list/revoke/delete | Implemented | Low | Hash-only storage, confirm + audit |
| Webhooks | `apps/api/src/routes/webhook-management.ts` | Endpoint CRUD, DLQ retry, test | Implemented | Low | SSRF guard, masked secrets, confirm + audit |
| Billing panel | `apps/api/src/routes/billing.ts` | Summary/invoices/sync/portal session | Implemented | Medium | Portal session open to any member |
| Admin settings | `apps/web/app/(admin)/admin/settings/page.tsx` | Email test only | Skeleton | Low | No platform-settings CRUD exists |
| Exports | tickets/projects/audit/approvals/assets/proposals/findings/domain-monitors + 4 un-audited | CSV/JSON download | Implemented | Medium | Formula guard; tenant-scoped |
| Admin UI pages | `apps/web/app/(admin)/admin/**` (203 pages) | Operator console | Implemented | Low | All gated; org delete has no UI |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Admin pages/APIs | 4 | admin.ts, admin gating, 203/203 pages gated | No admin-op rate limits; no impersonation UI | Add dangerous-op limiter + impersonation page |
| User/org/role management | 2 | memberships.ts, users.ts, roles.ts, 5302424 | Cross-tenant role assignment unguarded; self-assign | Central `assertCanAssignRole`; block self-role change |
| Billing panels | 3 | billing.ts scoped + audited | Portal session open to any member | Require billing-contact/permission |
| Document/ticket admin | 4 | documents.ts/tickets.ts, delete confirm, org filters | Bulk ops no preview | Dry-run + second apply step |
| Webhook/API key admin | 4 | webhook-management.ts, api-keys.ts | — | Keep SSRF/masking tests |
| Bulk ops | 2 | bulk.ts, documents bulk, store import | No preview/dry-run; pre-confirmed accounts | Preview endpoints + approval for visibility changes |
| Approval flows | 3 | approvals.ts/services | Self-approval; cancel any state | SoD guard + pending-only cancel |
| Impersonation | 4 | audit.ts, metrics, Prometheus rule | No UI; export un-audited | Add UI + audit the export |
| Settings | 3 | settings page, admin test-email | No platform settings surface | Document that settings are env-driven |
| Exports | 3 | 8 audited + scoped, formula guard | 4 exports un-audited | Shared audited-export helper |
| Destructive actions | 2 | 59 DELETE handlers | 4 confirmed; org delete cascades, no undo | Confirm + audit everywhere; org delete guard |
| Confirmations | 3 | delete-confirm.ts, UI ConfirmDialog/typed DELETE | Only API-side on 4 routes | CI check for new DELETE routes |

## Detailed Review

### Item: Organization lifecycle and destructive delete

- Evidence: `apps/api/src/routes/organizations.ts:59-151` (onboard), `:403-429` (delete), `:513-540` (domain delete); FK cascades in `supabase/migrations/5302026_supabase_consolidated_fresh_bootstrap_20260529.corrected.v3.sql:138,203,223,233,284,...`.
- What it does: Creates/updates orgs, onboards with an auto-approved admin membership, hard-deletes the org and every cascaded row.
- Current controls: `requireOrgAccessByParam` + `requirePermission("organizations","manage")` + audit events; org list scoped by `admin-scope`.
- Missing controls: confirmation body on delete, typed name confirmation, soft-delete/undo, UI delete control (none exists — API only).
- Risks: total tenant data loss from one unconfirmed DELETE; accidental deletion unrecoverable except PITR.
- Recommended improvement: require `{ confirm: true }` plus a typed slug for org delete; log a summary count of cascaded rows before delete; document PITR recovery in the admin UI.
- Suggested tests: DELETE without/with confirm; cascade count; audit event content.
- Suggested docs: `docs/ADMIN_FEATURES.md` destructive-action section.

### Item: Membership/role assignment (self-privilege escalation)

- Evidence: `apps/api/src/routes/memberships.ts:123-156`; `apps/api/src/routes/users.ts:390-442`; `apps/api/src/routes/organizations.ts:77-127`; `apps/api/src/routes/bulk.ts:35-48`; `apps/api/src/lib/roles.ts:22-29`; `apps/api/src/middleware/org-access.ts:44-60`; `apps/api/src/middleware/permissions.ts:70-86`; `supabase/migrations/5302424_manage_actions.sql:14-29`.
- What it does: Changes a membership's role/status; role keys `admin`/`super_admin` are cross-tenant by design.
- Current controls: audit events (`membership.update`, `user.role.update`); `super_admin` assignment guard on `users.ts` only; org scoping via `loadOwned`/`assertOrgScopeMatches`.
- Missing controls: guard against assigning CROSS_TENANT_KEYS without a super-admin profile; self-role-change block; role allowlist validation; consistency across all four assignment paths.
- Risks: delegated user/role managers escalate to cross-tenant access + permission bypass.
- Recommended improvement: one `assertCanAssignRole` helper used by memberships POST/PATCH, users PATCH /role, bulk invite and onboard.
- Suggested tests: negative tests for each path assigning `admin`/`super_admin` by a non-super-admin; self-assign test.
- Suggested docs: `docs/portal_admin_permissions_guide.md` role-assignment policy.

### Item: Bulk operations (documents, invite, store import)

- Evidence: `apps/api/src/routes/documents.ts:651-751`; `apps/web/components/admin/AdminDocumentsBulkControls.tsx:141-335`; `apps/api/src/routes/bulk.ts:33-189`; `apps/web/components/admin/BulkInviteForm.tsx:24-45`; `apps/web/app/(admin)/admin/store/import-export/actions.ts:46-80`.
- What it does: Applies folder/metadata changes, invites up to 500 users, imports catalog JSON.
- Current controls: org pre-filtering (`resolveOwnedDocumentIds`), 500-entry cap, audit events with counts, `documents:create` permission.
- Missing controls: per-row preview/dry-run, before/after diff, dedicated bulk permission or second confirmation, invite preview.
- Risks: mass visibility flips to `public`, wrong folder/import applied at scale, pre-confirmed account creation.
- Recommended improvement: preview endpoint returning resolved rows + diffs; explicit apply; treat visibility changes as elevated.
- Suggested tests: preview returns only owned rows; apply requires confirmation for visibility.
- Suggested docs: admin bulk-operations runbook.

### Item: Approval flows

- Evidence: `apps/api/src/routes/approvals.ts:193-435`; `apps/api/src/services/approvals.ts:68-209`.
- What it does: Request → approve/reject/cancel with optimistic locking and timeline events.
- Current controls: `approvals:edit` permission, org scoping via `loadOwned`, version checks, audit + timeline.
- Missing controls: requester≠approver check; cancel restricted to pending.
- Risks: rubber-stamp approvals; reversal of approved decisions.
- Recommended improvement: SoD guard and pending-only cancel with a reversal event.
- Suggested tests: self-approval 403; cancel approved 400.
- Suggested docs: approval workflow policy.

### Item: Impersonation + audit

- Evidence: `apps/api/src/routes/audit.ts:122-191`; `apps/api/src/services/impersonation.ts`; `apps/api/src/lib/metrics.ts:125-127,252-255`; `infra/digitalocean/prometheus.rules.yml:45-56`.
- What it does: Records every cross-tenant entry; exposes list/export to genuine cross-tenant admins; alerts on volume.
- Current controls: `allTenants` gate, metric, alert rule, tests.
- Missing controls: web UI page; audit event on the impersonation export.
- Risks: low; review requires API/SDK use.
- Recommended improvement: admin UI page + shared audited-export helper.
- Suggested tests: export writes `impersonation.export`.
- Suggested docs: incident runbook link.

### Item: Exports

- Evidence: audited at `tickets.ts:84`, `projects.ts:81`, `audit.ts:96`, `approvals.ts:78`, `assets.ts:59`, `domain-monitors.ts:56`, `findings.ts:63`, `proposals.ts:63`; un-audited at `audit.ts:168-191`, `satisfaction-pulse-widget.ts:81-110`, `client-onboarding-command-center.ts:71-110`, `dynamic-client-forms-builder.ts:65-78`; formula guard `apps/api/src/lib/csv.ts:8-30`; tenant scope via `admin-scope`.
- Current controls: mandatory tenant predicate, row-count audit events (8 routes), CSV formula-injection guard.
- Missing controls: audit events for 4 exports (including the impersonation trail).
- Risks: unattributable exfiltration of those datasets.
- Recommended improvement: shared `sendAuditedExport` helper.
- Suggested tests: each export route asserts its audit event.
- Suggested docs: update `docs/ADMIN_FEATURES.md` export section.

### Item: Webhook/API-key admin and settings

- Evidence: `apps/api/src/routes/webhook-management.ts:275-440`, `:168-258`; `apps/api/src/routes/api-keys.ts:17-177`; `apps/api/src/routes/admin.ts:54-88`; `apps/web/app/(admin)/admin/settings/page.tsx`.
- What it does: Manage endpoints/keys with secret masking and SSRF protection; SMTP test.
- Current controls: `webhooks:manage`/`api-keys:manage`, confirm+audit deletes, hashed keys, `assertSafeWebhookUrl`, rate-limited test email.
- Missing controls: none material found.
- Risks: low.
- Recommended improvement: keep regression tests for SSRF/masking.
- Suggested tests: existing suites cover; add DLQ retry audit assertions if touched.
- Suggested docs: unchanged.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ADMIN-001 | Admin pages/APIs | `apps/api/src/routes/admin.ts`; 203/203 web pages gated | requireAdmin + org pin | No dangerous-op limiter | P2 | Add admin-op rate limits |
| ADMIN-002 | User/org/role management | `memberships.ts:123`, `users.ts:390` | Audit + org scope | Cross-tenant role assignment unguarded | P1 | `assertCanAssignRole` |
| ADMIN-003 | Billing panels | `billing.ts:383-447` | Org access + audit | Any member can open Stripe portal | P2 | Require billing contact/permission |
| ADMIN-004 | Document/ticket admin | `documents.ts:565`, `tickets.ts:492` | Confirm + audit + org filter | Bulk ops no preview | P2 | Dry-run + apply step |
| ADMIN-005 | Webhook/API key admin | `webhook-management.ts`, `api-keys.ts` | SSRF guard, masking, confirm, audit | — | — | Keep tests |
| ADMIN-006 | Bulk ops | `documents.ts:651-751`, `bulk.ts` | Org filter, counts, cap | No preview/dry-run | P2 | Preview endpoints |
| ADMIN-007 | Approval flows | `services/approvals.ts:68-193` | Permission + version + audit | Self-approval; cancel any state | P2 | SoD + pending-only cancel |
| ADMIN-008 | Impersonation | `audit.ts:122-191`, Prometheus rule | Logged + review API + alert | No UI; export un-audited | P3/P2 | UI + export audit |
| ADMIN-009 | Settings | `admin/settings/page.tsx`, `admin.ts:54` | Rate-limited + audited | No platform settings surface | P3 | Document env-driven settings |
| ADMIN-010 | Exports | 8 audited; 4 not | Scoped + formula guard | 4 un-audited | P2 | Shared audited-export |
| ADMIN-011 | Destructive actions | 59 DELETE handlers | 4 confirmed | Org delete cascades, no undo | P2 | Confirm + audit everywhere |
| ADMIN-012 | Confirmations | `delete-confirm.ts`, UI dialogs | Typed DELETE in UI, 4 API routes | API confirmation coverage | P2 | CI check for DELETE routes |

## Findings

1. **Org-agnostic `requireAdmin` lets a tenant admin read other tenants' admin data** — P1, `verified-fixed`. Org-pinning + shared scope helper present with tests.
2. **Impersonation/cross-tenant access is logged but not reviewable or alerted** — P1, `verified-fixed`. Review endpoints + metric + Prometheus alert present; residual UI/export gaps tracked below.
3. **Sensitive admin exports are not audit-logged** — P2, `partially-fixed`. Tickets/projects/audit now audited (PR #127); impersonation/export + satisfaction-pulse + onboarding + dynamic-forms still not.
4. **Destructive deletes are inconsistently confirmation-gated and org delete is unrecoverable** — P2, `still-open`. 4/59 confirmed; org delete cascades with no confirm or undo.
5. **Bulk document operations apply without a per-row preview or elevation guardrail** — P2, `still-open`.
6. **Bulk invite creates pre-confirmed auth accounts (and org onboarding auto-approves admin)** — P2, `still-open`.
7. **No rate limiting specific to expensive/destructive admin operations** — P2, `still-open`.
8. **No undo/soft-delete is exercised despite the schema supporting it** — P2, `verified-fixed`. Columns dropped (5302432), hard delete documented; previous register note was stale.
9. **Web admin gate accepts a broader role set than the API `requireAdmin` (guard/API divergence)** — P3, `still-open` (documented, API-enforced).
10. **Active-org cookie setter performs no server-side authorization** — P3, `still-open` (API-side enforcement bounds impact).
11. **Admin global search and dashboard expose global resource names/counts to any admin** — P3, `verified-fixed`.
12. **Global store catalog is mutable by any tenant admin** — P3, `verified-fixed`.
13. **Role assignment paths let a delegated user-manager grant cross-tenant admin roles (self-escalation)** — P1, `open` (new).
14. **Approval flows allow self-approval and cancellation of already-approved requests** — P2, `open` (new).
15. **Destructive deletes are not consistently audit-logged** — P2, `open` (new).
16. **Any org member can open the Stripe billing portal for their org (no billing-contact check)** — P2, `open` (new).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Delegated user-manager escalates to cross-tenant admin | P1 | Medium | High | `memberships.ts:123-156`, `users.ts:390-442`, `org-access.ts:44-60` | Central role-assignment guard |
| Org delete destroys all tenant data unconfirmed | P2 | Low | Critical | `organizations.ts:403-429`, FK cascades | Confirm + typed slug; PITR runbook |
| Bulk visibility flip / mass metadata change | P2 | Medium | Medium | `documents.ts:697-751`, bulk UI | Preview + second apply |
| Pre-confirmed accounts from bulk invite | P2 | Medium | Medium | `bulk.ts:108-116` | Invite emails, approval step |
| Self-approved privileged requests | P2 | Medium | Medium | `services/approvals.ts:68-118` | SoD guard |
| Un-audited deletes/exports | P2 | Medium | Medium | 7 DELETE handlers; 4 exports | Shared audited helpers |
| Billing portal misuse by any member | P2 | Low | High | `billing.ts:383-447` | Billing-contact gate |
| Admin-op hammering (exports/bulk) | P2 | Medium | Medium | global limiters only | Per-route limiters |

## Recommendations

### Immediate / Release Blocking

- Enforce role-assignment policy server-side (cross-tenant role keys require a super-admin profile; no self-role-change) across memberships, users, bulk invite and onboard (P1).

### This Week

- Add a confirmation body + typed org slug requirement to organization delete; record a pre-delete cascade summary in the audit event.
- Add the four missing export audit events, starting with `/audit/impersonation/export`.
- Add `logAuditEvent` to the 7 un-audited DELETE handlers.

### This Month

- Add preview/dry-run + explicit apply for bulk document metadata/visibility, store import and bulk invite.
- Add the self-approval guard and pending-only cancel to approvals.
- Gate the Stripe billing portal session on `is_billing_contact` or a client billing permission.
- Add per-route rate limits for destructive/expensive admin operations.
- Add a CI check that every `router.delete` handler calls `assertDeleteConfirmed` and `logAuditEvent` (or is explicitly exempted).

### Later / Platform Evolution

- Admin UI page for the impersonation trail; align the web admin gate with the API role tiers; undo/restore design if soft delete is revisited (documented as hard delete today).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Guard `admin` role assignment like `super_admin` | Closes the escalation path | `apps/api/src/routes/users.ts`, `memberships.ts` | Negative test assigning `admin` as non-super-admin |
| Audit the impersonation export | Most sensitive export currently invisible | `apps/api/src/routes/audit.ts` | Test asserts `impersonation.export` event |
| Add `assertDeleteConfirmed` to org delete | Prevents one-call tenant wipe | `apps/api/src/routes/organizations.ts` | DELETE without body → 400 |
| Add `logAuditEvent` to 7 DELETE handlers | Restores delete accountability | client-onboarding, dynamic-forms, edu-automation, license-optimizer, projects, status-page, uptime-monitor | Audit event per route |
| Self-approval guard | Restores four-eyes | `apps/api/src/services/approvals.ts` | approve own request → 403 |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Central `assertCanAssignRole` helper + tests | P1 | API security | M | None |
| Org-delete confirmation + cascade summary | P2 | API platform | S | None |
| Bulk preview endpoints (documents/store/invite) | P2 | API + web | M | None |
| Approval SoD + state machine | P2 | API platform | S | None |
| Audited-export helper for all exports | P2 | API platform | S | None |
| Audited-delete helper + CI guard | P2 | API platform | M | CI workflow |
| Admin-op rate limiter | P2 | API platform | S | None |
| Billing portal permission gate | P2 | Billing | S | Permission catalog |
| Impersonation admin UI page | P3 | Web + API | M | None |

## Suggested Tests

- Unit: `assertCanAssignRole` matrix (super-admin vs admin vs delegated role; self vs other; each of the four assignment paths).
- Integration: DELETE org without confirm → 400; with confirm → 204 + audit; cascade summary metadata.
- Integration: bulk document metadata preview returns only owned ids and field diffs; apply requires confirmation for visibility.
- Integration: approve own request → 403; cancel approved request → 400; cancel pending → 200.
- Integration: each export route writes its `*.export` audit event (extend existing suites).
- Integration: every DELETE handler emits an audit event (table-driven test or CI grep guard).
- Security: member (non-billing-contact) POST /billing/create-portal-session → 403.
- Regression: impersonation export still 403 for single-org admin and 200 for allTenants admin (already covered).
- Manual: rate-limit bulk invite/export with 20 rapid calls → 429; verify admin UI 429 messaging.

## Suggested Documentation Updates

- `docs/ADMIN_FEATURES.md`: correct the "Every sensitive export is audit-logged" claim; add destructive-action confirmation matrix and role-assignment policy.
- `docs/API_RATE_LIMITING.md`: document admin-op limiters once added.
- `docs/ROLLBACK_PROCEDURES.md`: link the org-delete PITR recovery steps from the admin console docs.
- `docs/portal_admin_permissions_guide.md`: state which roles may assign `admin`/`super_admin` and that `users:manage`/`roles:manage` are delegable but not escalation-safe today.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are `admin` role holders MSP staff only, or can client orgs hold it? | Determines the real precondition of the escalation finding | Role-assignment records / product policy |
| Is `RLS_WRITES_ENABLED` populated in prod for memberships/documents? | If enabled, RLS narrows some paths (but memberships RLS still allows org admins to update) | Droplet `.env` (operator) |
| Who approves onboarding admin memberships operationally? | Auto-approve may be acceptable with a compensating review | Onboarding runbook |
| Is the Stripe portal configured to restrict cancellations? | Bounds the billing-panel abuse case | Stripe dashboard (operator) |
| Are the 4 un-audited exports actually exercised by operators? | Prioritizes the export-audit fix | Usage/observability data |

## Appendix

### A. Admin surface inventory (API routers)

`admin.ts` (tenant list, test email) · `organizations.ts` (CRUD/onboard/domains/logo/delete) · `memberships.ts` · `users.ts` · `roles.ts` · `profiles.ts` · `bulk.ts` · `documents.ts` · `tickets.ts` · `approvals.ts` · `audit.ts` · `api-keys.ts` · `webhook-management.ts` · `billing.ts` · `dashboard.ts` · `search.ts` · `store/*` · `batch.ts` · `settings` (web-only page).

### B. Abuse case matrix (abridged)

| Abuse case | Actor | Path | Control today | Gap |
|---|---|---|---|---|
| Self-escalate to cross-tenant admin | Delegated user-manager | PATCH memberships/users role | Audit only | No guard (P1) |
| Wipe a tenant | Admin with organizations:manage | DELETE /organizations/:id | Audit only | No confirm/undo (P2) |
| Mass-flip documents public | Admin with documents:create | POST /documents/bulk/metadata | Org filter + audit | No preview (P2) |
| Create confirmed accounts en masse | Admin | POST /bulk/invite | 500 cap + audit | Pre-confirmed, no consent (P2) |
| Approve own privileged request | Approver/requester | POST /approvals/:id/approve | Audit | No SoD (P2) |
| Exfiltrate impersonation trail | Cross-tenant admin | GET /audit/impersonation/export | allTenants gate | Export un-audited (P2) |
| Cancel org subscription | Any member | POST /billing/create-portal-session | Org access + audit | No billing-contact check (P2) |
| Hammer exports/bulk | Any admin | GET exports, POST bulk | Global limiters | No per-route limiter (P2) |

### C. Destructive action review (DELETE handlers)

- Confirmed + audited (4): `api-keys.ts:146`, `documents.ts:565`, `tickets.ts:492`, `webhook-management.ts:372`.
- Audited, not confirmed (48): e.g. `organizations.ts:403`, `memberships.ts:158`, `roles.ts:185`, `approvals.ts:302`, `batch.ts:143`, `projects.ts:596`.
- Neither confirmed nor audited (7): `client-onboarding-command-center.ts:174`, `dynamic-client-forms-builder.ts:139`, `edu-automation.ts:598`, `license-optimizer.ts:195`, `projects.ts:333`, `status-page.ts:249`, `uptime-monitor.ts:220`.
- Highest-blast-radius delete: `organizations.ts:403` (FK `on delete cascade` across the tenant schema).

### D. Guardrail recommendations (operator-facing)

1. Treat `admin`/`super_admin` assignment as a platform action: require a profile-flagged super admin and log the change with actor/target/role.
2. Make every destructive API require a confirmation body; org delete additionally a typed slug.
3. Require preview → apply for bulk operations; treat visibility/ownership changes as elevated.
4. Surface the impersonation trail and destructive-action audit events in the admin console.
5. Add per-route rate limits and 429 messaging for exports/bulk/destructive endpoints.
6. Keep the hard-delete decision visible in operator docs; link PITR recovery steps from the admin console.

## Findings

| ID | Severity | Title |
|---|---|---|
| ADMIN-P1-001 | P1 | Org-agnostic `requireAdmin` lets a tenant admin read other tenants' admin data |
| ADMIN-P1-002 | P1 | Impersonation/cross-tenant access is logged but not reviewable or alerted |
| ADMIN-P2-001 | P2 | Sensitive admin exports are not audit-logged |
| ADMIN-P2-002 | P2 | Destructive deletes are inconsistently confirmation-gated and org delete is unrecoverable |
| ADMIN-P2-003 | P2 | Bulk document operations apply without a per-row preview or elevation guardrail |
| ADMIN-P2-004 | P2 | Bulk invite creates pre-confirmed auth accounts (and org onboarding auto-approves admin) |
| ADMIN-P2-005 | P2 | No rate limiting specific to expensive/destructive admin operations |
| ADMIN-P2-006 | P2 | No undo/soft-delete is exercised despite the schema supporting it |
| ADMIN-P3-001 | P3 | Web admin gate accepts a broader role set than the API `requireAdmin` (guard/API divergence) |
| ADMIN-P3-002 | P3 | Active-org cookie setter performs no server-side authorization |
| ADMIN-P3-003 | P3 | Admin global search and dashboard expose global resource names/counts to any admin |
| ADMIN-P3-004 | P3 | Global store catalog is mutable by any tenant admin |
| ADMIN-P1-003 | P1 | Role assignment paths let a delegated user-manager grant cross-tenant admin roles (self-escalation) |
| ADMIN-P2-007 | P2 | Approval flows allow self-approval and cancellation of already-approved requests |
| ADMIN-P2-008 | P2 | Destructive deletes are not consistently audit-logged |
| ADMIN-P2-009 | P2 | Any org member can open the Stripe billing portal for their org (no billing-contact check) |
