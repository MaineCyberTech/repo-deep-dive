# Admin Console Abuse Case Audit — re-audit verification (main @ 7dd0402)

## Audit Metadata

- Audit name: mainecybertech
- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Repository: `github.com/MaineCyberTech/mainecybertech`
- Branch: `main` (audited ref `origin/main`)
- Commit SHA: `7dd040234e8dfa40dd2d2b6fe1ca7379f2fba097`
- Generated at: 2026-10-14
- Auditor: subagent (full-domain verification re-audit, group 1)
- Area code: ADMIN
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261014-0033-full-main-7dd0402/26_admin_console_abuse_case_audit.md`
- Scope limitations: static review; no live console session, no Stripe dashboard. Recovery claims are
  documentation-level (PITR runbook) and were not exercised.

## Scope

Re-verification of the 16 ADMIN findings from the previous full run, plus a sweep of the admin surfaces
touched since (203 admin pages, exports, bulk operations, approvals, billing portal, deletes). Reviewed:
`apps/api/src/routes/{admin,organizations,memberships,users,roles,bulk,documents,tickets,approvals,audit,
api-keys,webhook-management,billing,dashboard,search,store/*}`, `apps/api/src/services/{approvals,audit,
client-onboarding-command-center,dynamic-client-forms-builder}`, `apps/api/src/lib/delete-confirm.ts`, and
the web admin gate.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/middleware/admin.ts`, `lib/admin-scope.ts` | Source | Admin gate + org pinning | Pinned semantics |
| `apps/api/src/lib/role-assignment.ts` | Source | Role-assignment guard | All four paths |
| `apps/api/src/lib/delete-confirm.ts`, `routes/organizations.ts:427-460` | Source | Destructive-action confirmation | Typed slug for org delete |
| `apps/api/src/services/approvals.ts:80-84,139-142,195-202` | Source | Approval SoD + state machine | Self-approval blocked; pending-only cancel |
| `apps/api/src/routes/billing.ts:685-740` | Source | Stripe portal gate | Billing contact or `billing:manage` |
| Export handlers across `apps/api/src/routes/*.ts` (12 routes, scripted scan) | Source | Export audit coverage | 9 audited / 3 not |
| `apps/web/lib/auth/admin.ts` + 203 `page.tsx` guard scan | Source | Web admin gate parity | 165 direct + shared `ModuleDetailPage`/redirect stubs cover all 203 |
| `apps/api/src/__tests__/destructive-delete-guard.test.ts` | Test | Delete confirm/audit gate | Table-driven exemptions |

## Verification Performed

- Re-checked every prior ADMIN evidence path at the current commit.
- Scripted scan of all export routes for an `*.export` audit event inside the handler block.
- Scripted scan of the seven previously un-audited DELETE handlers for confirm + audit (now routed through
  audited services) and confirmation of the delete guard test.
- Scanned all 203 admin pages for `requireAdminAccess` or a shared guarded wrapper/redirect stub.
- Re-checked the impersonation review/alert path and the store-catalog org pinning.

## Executive Summary

Fifteen of the 16 findings are verified fixed and one remains partially fixed; no regressions. The admin
console now has org-pinned admin semantics, a central role-assignment guard, typed confirmation for the
highest-blast-radius delete (organization), dry-run previews + explicit confirm for bulk document changes,
approval separation of duties, per-route rate limits on expensive admin operations, billing-contact gating
for the Stripe portal, and audited deletes.

The single residual is export auditing: 9 of 12 export handlers write an audit event, but
`/audit/impersonation/export` (the most sensitive export) and two smaller exports remain unaudited. The web
admin gate now shares the API's cross-tenant role set.

## Findings

| ID | Sev | Status | Title | Re-verification evidence |
|---|---|---|---|---|
| ADMIN-P1-001 | P1 | verified-fixed | Org-agnostic `requireAdmin` cross-tenant reads | `middleware/admin.ts:22-64`; `admin-scope.ts` |
| ADMIN-P1-002 | P1 | verified-fixed | Impersonation logged but not reviewable/alerted | `audit.ts:126-158,172-191`; metric + Prometheus rules |
| ADMIN-P1-003 | P1 | verified-fixed | Delegated user-manager cross-tenant role grants | `role-assignment.ts:20-43`; four call sites |
| ADMIN-P2-001 | P2 | partially-fixed | Sensitive admin exports not audit-logged | 9/12 audited (approval/asset/audit/domain_monitor/finding/project/proposal/ticket/user). Residual: `audit.ts:172-191` (impersonation export), `satisfaction-pulse-widget.ts:87`, `dynamic-client-forms-builder.ts:71` |
| ADMIN-P2-002 | P2 | verified-fixed | Destructive deletes inconsistently gated / org delete unrecoverable | `delete-confirm.ts` + typed slug `organizations.ts:427-460`; recovery documented |
| ADMIN-P2-003 | P2 | verified-fixed | Bulk document ops without preview/elevation guard | `documents.ts:707-775,821-858` dry-run + confirm |
| ADMIN-P2-004 | P2 | verified-fixed | Bulk invite pre-confirmed accounts | `bulk.ts:163`; `organizations.ts:127-138` pending |
| ADMIN-P2-005 | P2 | verified-fixed | No admin-op rate limits | `rate-limit.ts:87-104` applied to exports/bulk/org/tickets |
| ADMIN-P2-006 | P2 | verified-fixed | No undo/soft-delete exercised | `5302432` drops columns; `ADMIN_FEATURES.md:451-452` documents hard delete |
| ADMIN-P2-007 | P2 | verified-fixed | Approval self-approval / cancel-any-state | `services/approvals.ts:80-84,139-142,195-202` |
| ADMIN-P2-008 | P2 | verified-fixed | Destructive deletes not consistently audited | All 7 handlers route through audited services/inline log; `destructive-delete-guard.test.ts` |
| ADMIN-P2-009 | P2 | verified-fixed | Any member can open Stripe portal | `billing.ts:685-740` billing-contact or `billing:manage` |
| ADMIN-P3-001 | P3 | verified-fixed | Web admin gate accepts broader role set | `apps/web/lib/auth/admin.ts` uses shared `isCrossTenantKey` |
| ADMIN-P3-002 | P3 | verified-fixed | Active-org cookie setter unauthorized | `apps/web/lib/org-actions.ts:21-50` |
| ADMIN-P3-003 | P3 | verified-fixed | Admin search/dashboard global names/counts | `search.ts:107-252`; `dashboard.ts:16-50` |
| ADMIN-P3-004 | P3 | verified-fixed | Global store catalog mutable by any tenant admin | `store/catalog.ts:180-195` org pinning |

New findings: none. The three un-audited exports are the residual of ADMIN-P2-001 (the previous run's
recommendation explicitly targeted the impersonation export first).

## Abuse case matrix (abridged)

| Abuse case | Control today | Gap |
|---|---|---|
| Self-escalate to cross-tenant admin | Central `assertCanAssignRole` (all four paths) | — |
| Wipe a tenant | Typed-slug confirm + audit + PITR runbook | Recovery untested |
| Mass-flip documents public | Dry-run preview + explicit confirm | — |
| Create confirmed accounts en masse | `inviteUserByEmail` + pending membership | — |
| Approve own request | SoD guard | — |
| Exfiltrate impersonation trail | allTenants gate | Export un-audited (ADMIN-P2-001) |
| Cancel org subscription | Billing-contact gate | — |
| Hammer exports/bulk | `rateLimitAdminOps` | — |

## Recommendations

### This Week

1. Add the export audit event to `routes/audit.ts` `/impersonation/export` (row count only), then to
   `satisfaction-pulse-widget.ts` and `dynamic-client-forms-builder.ts`; add a table-driven test that every
   export handler emits its `*.export` event (ADMIN-P2-001).
2. Consider a shared `sendAuditedExport` helper so new exports cannot miss the audit step.

### This Month

3. Exercise the org-delete PITR recovery path once and record the result in `docs/ROLLBACK_PROCEDURES.md`
   (ADMIN-P2-002 residual risk, not a code gap).

## Suggested Tests

- Integration: each export route writes its audit event (extend the existing per-route suites).
- Regression: impersonation export remains 403 for single-org admins and 200 for `allTenants` admins.
- Manual: org delete without/with a wrong slug → 400; correct slug → 204 + cascade summary audit event.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the impersonation export intentionally un-audited? | Closes or re-scopes ADMIN-P2-001 | Product/security decision |
| Is PITR restore of a deleted org rehearsed? | Recovery confidence | Operator drill record |
