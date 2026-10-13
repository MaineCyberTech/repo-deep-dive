# Usability and Workflow Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (target `/tmp/opencode/mct-audit-target`, read-only)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent (`04_usability_workflow_audit`, area `USE`)
- Area code: USE
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/04_usability_workflow_audit.md`
- Scope limitations: static review of the code only; the app was **not** run (no server, no browser, no
  database). Claims about runtime behavior are derived from code paths and are marked with confidence.
  Supabase dashboard configuration (redirect allow-lists, SMTP) is external and unknown.

## Scope

Reviewed end-to-end web workflows in `apps/web` (Next.js App Router) against `apps/api`, `packages/sdk`,
and `infra/digitalocean` where the workflow depends on them:

- Onboarding: signup, email confirmation, pending approval, admin approval queue, organization
  onboarding wizard, client-onboarding command center.
- Login/signup/reset: password login, MFA challenge/recovery/step-up, forgot/reset password.
- Navigation: portal/admin sidebars, subnav, breadcrumbs, org switcher, global search.
- Dashboards: portal dashboard (admin dashboard inspected for structure).
- Forms: auth forms, profile, support ticket, admin module CRUD, bulk invite, onboarding wizard.
- Search/filter/sort: admin tickets, admin users, portal global search, notifications filters.
- Bulk workflows: bulk invite, bulk ticket update, bulk document folder/metadata/delete/visibility.
- Admin/support workflows: ticket lifecycle (create/triage/comment/edit/delete/restore), approvals,
  user/membership management, API keys, documents, onboarding.
- Notifications and preferences: bell, notifications page, notification preferences, profile.
- Error recovery, empty/loading states, destructive actions, session expiry, offline, help paths.

Not reviewed in depth: store/marketing funnels (public store checkout, quiz, quote), billing payment
flows (covered by domain 29), accessibility conformance (domain 05), mobile layout specifics (domain 17).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/web/middleware.ts` | code | Session/expiry gate, domain routing, CSP | Non-authoritative UX gate (ARCH-P3-001) |
| `apps/web/lib/auth/auth-actions.ts` | code | Login/MFA/signup/logout actions | Signup redirect + MFA cookie handling |
| `apps/web/app/(public)/{login,signup,forgot-password,password-reset,pending}/page.tsx` | code | Auth UX | Reset page has no token handling |
| `apps/api/src/routes/auth.ts` | code | Sign-up/reset/MFA endpoints | `emailRedirectTo`, `requireAuth` on reset |
| `apps/web/app/(portal)/layout.tsx`, `app/(admin)/admin/layout.tsx` | code | Portal/admin shells, route-permission maps, MFA redirect | `?mfa=required` produced but unused |
| `apps/web/components/portal/SupportCenterClient.tsx`, `app/(portal)/portal/support/*` | code | Ticket create/reply | Field-name drift vs `actions.ts` |
| `apps/web/app/(admin)/admin/tickets/**` | code | Ticket lifecycle, inline status, delete/restore | Delete only closes |
| `apps/web/components/admin/AdminTicketCenterClient.tsx` | code | Search/filter/sort/bulk tickets | 25-row cap; no success toast |
| `apps/web/app/(admin)/admin/approvals/*` | code | Membership/org approval | `roleId:""` breaks PATCH |
| `apps/web/app/(admin)/admin/users/**`, `components/admin/{AdminUsersClient,InviteUserForm,BulkInviteForm}.tsx` | code | User/membership admin, bulk invite | No confirm/feedback on status changes |
| `apps/web/components/admin/OrganizationOnboardingWizard.tsx`, `app/(admin)/admin/onboarding/**`, `app/(portal)/portal/client-onboarding-command-center/**` | code | Onboarding workflows | Redirect swallowed; checklist read-only |
| `apps/web/app/(portal)/portal/documents/**`, `components/portal/{PortalDocumentsCenterClient,DocumentVersionsClient,DocumentShareClient}.tsx`, `app/(admin)/admin/documents/**` | code | Document flows, bulk actions, shares | Bulk false success |
| `apps/web/components/NotificationBell.tsx`, `NotificationsPageClient.tsx`, `notifications/preferences/*` | code | Notifications + preferences | Wrong ticket links, silent failures, interval leak |
| `apps/web/app/(portal)/portal/profile/ProfileClient.tsx` | code | Preferences/profile/password | Unused current-password field |
| `apps/web/app/(portal)/portal/profile/security/*` | code | MFA management/step-up | Step-up only via recovery codes |
| `packages/sdk/src/client.ts`, `documents.ts`, `tickets.ts`, `memberships.ts` | code | Web↔API contract | `res.json()` on 204; no If-Match |
| `apps/api/src/routes/{tickets,documents,memberships,client-onboarding-command-center}.ts` | code | Behavior behind UI | Per-item bulk results; PATCH checklist |
| `apps/api/src/middleware/optimistic-locking.ts`, `validators/membership.ts`, `middleware/not-found.ts` | code | Conflict handling, validation | `If-Match` optional; roleId UUID |
| `infra/digitalocean/Caddyfile.prod`, `.github/workflows/deploy-do.yml` | config | Host topology for email links | API host ≠ app host |
| `apps/web/public/sw.js` | code | Offline asset | Never registered |
| `apps/web/e2e/a11y.spec.ts`, `.github/workflows/e2e.yml` | test | Existing workflow coverage | No auth-recovery E2E |
| Previous run `mainecybertech-20261004-full-main-9c0b88c` register + `_domains/04_usability_workflow_audit.json` | artifact | Verification duty | No `USE` rows exist |

## Verification Performed

Previous-run verification duty (per instructions):

| Check | Command | Observed result |
|---|---|---|
| `USE` rows in previous follow-up register | `grep -c "| USE-" .../mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md` | `0` — there are no USE rows to re-verify |
| Previous domain JSON | `cat .../_domains/04_usability_workflow_audit.json` | `"findings": []` (reconciliation pass had no USE findings) |
| Only UX-area row | `grep -n "^| UX" follow_up_register.md` | `UX-P3-001` (accessibility breadth scan) — subject matter belongs to domain `05_ui_ux_accessibility_audit`; **not duplicated here** per instructions |
| Earliest full run (20261002) | `grep -rn "USE-P" docs/audits/repo-deep-dive/20261002-0344-develop-6286137/` | no USE findings in the committed corpus either |

Fresh-audit verification commands (all read-only):

| Check | Command | Observed result |
|---|---|---|
| Empty-body DELETE exposure | `grep -rho "res.status(204)" apps/api/src/routes/*.ts | wc -l` | `46` 204-only delete/removal handlers |
| SDK parses every body | `sed -n '80,105p' packages/sdk/src/client.ts` | `await res.json()` before any status check |
| 204 masked in tests | `sed -n '14,40p' packages/sdk/src/__tests__/sdk-expanded.test.ts` | mock returns `{success:true,data:null}` even for status 204 |
| Approval payload | `grep -n "roleId" apps/web/app/(admin)/admin/approvals/actions.ts` | `33: roleId: ""`, `46: roleId: ""` |
| API roleId rule | `cat apps/api/src/validators/membership.ts` | `roleId: z.string().uuid()` |
| Password-reset token handling | `grep -c "searchParams|useSearchParams|location.hash" apps/web/app/(public)/password-reset/page.tsx` | `0` |
| Reset endpoint guard | `grep -n "reset-password|requireAuth," apps/api/src/routes/auth.ts` | `349:/reset-password`, `350: requireAuth` |
| Signup redirect host | `grep -n "emailRedirectTo" apps/api/src/routes/auth.ts` | `182: .../auth/callback` built from the API request host |
| Prod topology | `sed -n '1,31p' infra/digitalocean/Caddyfile.prod` | `api.<domain>` → `api:4000` only; `/auth/callback` exists only on the web host |
| Ticket list cap | `sed -n '95,105p' apps/api/src/routes/tickets.ts` | default `limit = 25`; portal/admin call `list({})` |
| Notification ticket links | `grep -n "tickets/" components/NotificationBell.tsx components/NotificationsPageClient.tsx` | `${basePath}/tickets/<id>`; `ls app/(portal)/portal/tickets` → not found |
| MFA redirect consumers | `grep -rn "mfa=required" apps/web --include=*.tsx` | only producers (3 layouts/guards); no consumer |
| Service worker registration | `grep -rn "serviceWorker" apps/web/app apps/web/components apps/web/lib apps/web/instrumentation-client.ts | wc -l` | `0` |
| Offline handling | `grep -rn "navigator.onLine" apps/web/app apps/web/components apps/web/lib | wc -l` | `0` |
| If-Match usage | `grep -rn "If-Match" packages/sdk/src | wc -l` | `0` |
| Checklist UI | `grep -rn "updateChecklistItem|hecklist" apps/web/app apps/web/components apps/web/lib` | no onboarding-checklist caller; SDK+API methods exist |
| Dead support action | `grep -rn "createPortalTicket" apps/web` | only `actions.ts` + its test; live action is inline in `support/page.tsx` |

## Executive Summary

The web app is a large, mostly coherent portal (319 routes) with several genuinely good UX foundations:
grouped permission-aware navigation, route-level error boundaries, skeleton loading states, an accessible
confirmation dialog, optimistic updates with rollback and toasts in the admin document center, per-item
results in the bulk-invite UI, and `DataErrorNote` to distinguish "load failed" from "no data".

The audit nevertheless found four P1 workflow breaks that a real user hits early:

1. **Account recovery is broken.** The emailed password-reset link lands on a page that cannot complete
   the reset, because the reset endpoint requires an authenticated session and the page never consumes
   the Supabase `code`/token.
2. **Signup cannot be completed.** The confirmation email redirect is built from the API host, which
   serves no `/auth/callback` route, so the link 404s.
3. **Admins cannot approve pending users.** The approval queue sends `roleId: ""`, which the API schema
   rejects (UUID required); the action throws instead of approving.
4. **Every delete looks like a failure.** The SDK calls `res.json()` on empty 204 bodies, so 46 API
   delete endpoints surface as errors even when the delete succeeded — and some bulk deletes then
   swallow the same error and claim success.

Beyond those, the recurring theme is **missing or misleading feedback**: bulk document operations
report the requested count rather than per-item results; ticket lists silently stop at 25 rows and
their stats are computed from that page; ticket "delete" is only a close while the UI promises a
restorable soft-delete; notification preferences can fail silently; notification deep links for
tickets 404; and the MFA step-up redirect is produced but never explained.

Recommended next actions: fix the four P1s this week (they are small, localized changes), then make
feedback truthful in the bulk/notification/ticket surfaces, and add E2E coverage that walks the
actual emailed-link shapes (signup confirm, password reset) — the current unit tests mock those paths
and therefore hide the breaks.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Login (+MFA/recovery) | `app/(public)/login/page.tsx`, `lib/auth/auth-actions.ts` | Sign-in | Functional; good error handling | Low | Recovery/step-up covered below |
| Signup | `app/(public)/signup/page.tsx` | Create account | Functional UI; no try/catch; no password guidance | Medium | Confirmation link broken (API) |
| Email confirmation | `app/auth/callback/route.ts`, `api routes/auth.ts:182` | Verify email | Web route works; email points at API host | High | P1 |
| Forgot/reset password | `forgot-password/page.tsx`, `password-reset/page.tsx` | Self-service recovery | Forgot works; reset cannot complete | High | P1 |
| Pending approval page | `app/(public)/pending/page.tsx` | Explain blocked access | Clear copy + sign-out | Low | No "check status" affordance |
| Admin approval queue | `app/(admin)/admin/approvals/**` | Approve orgs/users | Org approve works; membership approve broken | High | P1 |
| Org onboarding wizard | `components/admin/OrganizationOnboardingWizard.tsx` | Create org + first admin | 3-step wizard with review | Medium | Generic error text |
| Client onboarding center | `app/(portal)/.../client-onboarding-command-center/**` | Track client onboarding | Create + read-only; redirect swallowed | Medium | Checklist not completable |
| Portal navigation | `components/portal/PortalSidebarContent.tsx`, `lib/navigation/portal-nav.ts` | Grouped nav + subnav | Permission-filtered, keyboard-aware | Low | 69 modules, grouped |
| Portal dashboard | `app/(portal)/portal/dashboard/page.tsx` | Landing + quick actions | Empty states + error note | Low | CTA does not open ticket modal |
| Support center | `components/portal/SupportCenterClient.tsx` | Client tickets | Create/reply/list | Medium | 25-row cap; no success toast |
| Admin ticket center | `components/admin/AdminTicketCenterClient.tsx` | Triage + bulk | Search/filter/sort/bulk with partial-failure messaging | Medium | Success silent; skipped ignored |
| Ticket detail (admin) | `app/(admin)/admin/tickets/[ticketId]/**` | Lifecycle | Edit/comments/activity/delete | Medium | Delete=close mismatch |
| Documents (portal/admin) | `app/(portal)/portal/documents/**`, `app/(admin)/admin/documents/**` | Upload/download/share/version/bulk | Rich admin client; optimistic updates | Medium | Bulk false success; single delete errors |
| Notifications | `components/NotificationBell.tsx`, `NotificationsPageClient.tsx` | Bell + list | SSE + polling fallback, filters | Medium | Wrong ticket links; interval leak |
| Notification preferences | `notifications/preferences/*` | Channel toggles | Table + Save | Medium | Silent save failure; copy mismatch |
| Profile/security | `app/(portal)/portal/profile/**` | Profile, password, MFA | Functional | Medium | Unused current-password; step-up hidden |
| Error boundaries | `app/(portal|admin|public)/error.tsx`, `global-error.tsx` | Recovery | Try again / log out / login | Low | No support link |
| Empty/loading states | `components/EmptyState.tsx`, 26 `loading.tsx` | Feedback | Skeletons at portal/admin roots; EmptyState widely used | Low | Some pages render false empties |
| Offline | `public/sw.js` | Caching | File exists, never registered | Medium | PWA caching inactive |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Onboarding | 2 | Signup/pending pages; approval queue; wizard | Confirmation link 404s; approval action fails; checklist not completable | Fix redirect host + roleId; wire checklist |
| Login/signup/reset | 2 | `auth-actions.ts`, login MFA handling | Reset dead-ends; no password guidance; silent session expiry | Route reset via callback; add policy copy + expired banner |
| Navigation | 4 | Grouped sidebar, subnav, breadcrumbs, permissions | Deep-link CTA gaps; no help entry | Deep-link CTAs; add support/help link |
| Dashboards | 3 | Portal dashboard with error note + empty states | Counts derived from capped lists | Use API totals; add trend/context |
| Forms | 3 | Consistent `cyber-*` styles, SubmitButton pending state | Lossy/generic errors; signup can hang; unused fields | try/finally + field-level errors |
| Search/filter/sort | 3 | Admin tickets/users filters + chips; portal search with error state | Ticket search client-side over 25 rows | Server-side search + pagination |
| Bulk workflows | 2 | Bulk invite per-item results; ticket partial failures | Document bulk false success; skipped ignored; no success toast | Plumb per-item results everywhere |
| Admin/support workflows | 2 | Rich ticket/document admins; ConfirmDialog | Approval break; delete=close; no confirm on access revocation | Fix P1s; confirm destructive transitions |
| Notifications | 2 | Bell + page + preferences + SSE | Wrong links; silent failures; interval leak | Fix links, surface errors, clear interval |
| Preferences | 3 | Notification prefs + profile | Silent save failure; inconsistent save models | Error feedback; single save model |
| Error recovery | 3 | Error boundaries, `withRetry`, `DataErrorNote` | Swallowed errors; raw messages; no support link | Centralize error mapping + support link |
| Empty/loading states | 3 | 26 loading files; EmptyState component | False empties on failed loads; 204 false failures | Distinguish error vs empty consistently |

## Detailed Review

### Personas

| Persona | Goals | Current experience | Top friction |
|---|---|---|---|
| New client user | Sign up, get approved, see dashboard | Signup succeeds but confirmation link 404s; approval may fail | Onboarding P1s |
| Existing client user | Track tickets, download docs, manage notifications | Ticket create works but is silent; ticket notification links 404; prefs can fail silently | Feedback + links |
| MSP admin / technician | Triage tickets, manage users/orgs, bulk operations | Ticket workflow good; approvals broken; deletes report false failures; 25-row cap | P1s + truthfulness |
| MSP super-admin / operator | Cross-tenant admin, approvals, break-glass | Cross-tenant scoping fixed in prior runs; onboarding wizard functional | Error clarity |
| Support staff (read-only) | Find a ticket fast | Search works client-side over first 25 rows | Pagination |
| Mobile user on flaky network | Work on the go | No offline banner or caching; silent empties | Offline support |

### Workflow friction table

| Workflow | Entry point | Friction observed | Severity |
|---|---|---|---|
| Signup → confirm → pending | `/signup` → email link | Email link points at API host → 404 (P1) | P1 |
| Forgot → reset → login | `/forgot-password` → email link → `/password-reset` | Reset page cannot consume the token; endpoint needs a session (P1) | P1 |
| Approve pending user | `/admin/approvals` | Approve/Reject throw (roleId `""`); no result feedback | P1 |
| Delete any record | admin module detail / API keys / documents | SDK cannot parse 204; UI reports failure after success | P1 |
| Create support ticket | `/portal/support` | Silent close; dashboard CTA doesn't open the modal; dead duplicate action | P3 |
| Client ticket triage | `/admin/tickets` | 25-row cap; bulk success silent; skipped ignored | P2 |
| Delete ticket | ticket detail | Only closes; copy promises soft-delete/restore | P2 |
| Bulk documents | `/admin/documents`, `/portal/documents` | Success claims even when items fail | P2 |
| Client onboarding | command center | Create error after success; checklist not completable | P2 |
| Notification click | bell / notifications page | Ticket links 404 | P2 |
| Notification preferences | preferences page | Silent save failure; copy contradicts Save button | P2 |
| MFA step-up | any portal page | Redirect without explanation; no visible step-up control | P2 |
| Password change | profile | Current password unused; requirements mismatch | P2 |
| Offline | any page | No banner/caching; silent stale UI | P3 |

### High-friction areas

1. **Account lifecycle (signup/confirm/reset/approve)** — three of the four P1s live here; the paths are
   individually small fixes but currently block the entire client onboarding funnel.
2. **Truthful feedback on destructive/bulk actions** — deletes report failure after success; bulk
   deletes report success on swallowed failure; bulk visibility/metadata report requested counts.
3. **Notification surfaces** — wrong deep links plus swallowed errors make the notification system
   look unreliable precisely when it matters.
4. **Large-list workflows** — ticket lists stop at 25 rows with no pagination or indication.

### Item: Password reset

- Evidence: `apps/web/app/(public)/password-reset/page.tsx:17-37`; `apps/api/src/routes/auth.ts:327-330,349-378`; `apps/web/app/auth/callback/route.ts:8-15`.
- What it does: sends email + new password to an authenticated endpoint; ignores the link token.
- Missing controls: no code exchange, no session bootstrap, no expired-link state.
- Recommended improvement: exchange `code` in `/password-reset` (or redirect through `/auth/callback`) before showing the form.
- Suggested tests: E2E that visits the URL shape GoTrue produces (`?code=...`), completes reset, and signs in.

### Item: Ticket lifecycle

- Evidence: `support/page.tsx:56`; `AdminTicketCenterClient.tsx:297-322,376-382`; `tickets/[ticketId]/actions.ts:79-101`.
- What it works well: admin triage, inline status/priority, comment edit window, activity timeline, typed delete confirmation.
- Gaps: list cap/pagination; delete=close semantics; silent bulk success; skipped ids hidden.
- Suggested tests: pagination beyond 25; delete → visible state change; bulk with one failing row.

### Item: Documents

- Evidence: `PortalDocumentsCenterClient.tsx:130-170`; `app/(admin)/admin/documents/page.tsx:438-470`; `DocumentVersionsClient.tsx:36-37`.
- Works well: signed-URL download with fallback message, share revoke confirmation, optimistic admin updates with rollback, toasts.
- Gaps: false success on bulk; version history read-only; single delete reports failure (204 bug).

### Item: Notifications and preferences

- Evidence: `NotificationBell.tsx:108-119,187-192`; `NotificationsPageClient.tsx:60-74,94-100`; `NotificationPreferencesClient.tsx:89-96`.
- Gaps: wrong ticket route, silent failures, interval leak, contradictory copy.

### Item: Admin access changes

- Evidence: `approvals/actions.ts:28-52`; `users/[userId]/page.tsx:167-233`; `users/[userId]/actions.ts:22-50`.
- Gaps: broken approve/reject; no confirmations; no success/error feedback.

### UX copy suggestions

| Current copy | Suggested copy | Where |
|---|---|---|
| "This performs a safer soft-delete so the ticket can be restored later." | "This will close the ticket and keep it in history." (or implement real delete) | ticket delete confirm |
| "Preferences are saved immediately and control whether new notifications are sent to each channel." | "Changes apply after you click Save Preferences." | notification preferences |
| "Onboarding failed. The slug may already be in use or the admin email is invalid." | Show the API message, e.g. "Slug 'acme' is already taken." | onboarding wizard |
| "Request failed" | "Could not reach the server. Your CSV was not imported — try again." | bulk invite |
| "Something went wrong" (boundaries) | Add "Contact support at /portal/support" link | error boundaries |
| "Password must be at least 6 characters." | State the real rule (e.g. "Use 12+ characters or a passphrase; common passwords are rejected.") | reset/profile |
| "Check your email to confirm your account, then return to continue." | Add "Didn't get it? Resend confirmation" once the link is fixed | signup |

### Manual QA scenarios

1. Sign up with a fresh email, open the confirmation email, complete confirmation, land on `/pending`, get approved, sign in.
2. Forgot password for a signed-out account, follow the emailed link, set a new password, sign in with it.
3. As admin, approve a pending membership from `/admin/approvals` and verify status/role.
4. Delete an API key and a document; verify the row disappears without an error toast.
5. Select 3 documents in admin bulk delete, force one to fail (already deleted), verify per-item outcome.
6. Create a ticket from the portal dashboard CTA and confirm visible success + the ticket in the list.
7. Click a "ticket created" notification in the portal bell; expect the ticket page, not 404.
8. Toggle an email preference with the API offline; expect an error, not a false success.
9. Let a session expire on a portal page; expect an explanation on `/login`.
10. With MFA enforced, use an aal1 session and confirm the security page offers a step-up.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| USE-001 | Onboarding | `auth.ts:182`, `Caddyfile.prod:19-30` | Signup form + pending page | Confirmation link 404s | P1 | Build redirect from APP_BASE_URL |
| USE-002 | Login/signup/reset | `password-reset/page.tsx`, `auth.ts:349` | Forgot-password works | Reset cannot complete | P1 | Exchange code before reset |
| USE-003 | Navigation | `PortalSidebarContent.tsx`, `PortalSubnav.tsx` | Grouped, permission-filtered nav | Help/support entry missing; CTAs shallow | P3 | Add help link; deep-link CTAs |
| USE-004 | Dashboards | `portal/dashboard/page.tsx` | Empty states + error note | Counts from capped lists | P2 | Use API totals |
| USE-005 | Forms | `ProfileClient.tsx`, `signup/page.tsx` | Required fields, pending buttons | Lossy errors; unused field; signup can hang | P2 | try/finally + field errors |
| USE-006 | Search/filter/sort | `AdminTicketCenterClient.tsx:333-425` | Search/org/status/sort + chips | Client-side over 25 rows | P2 | Server-side pagination/search |
| USE-007 | Bulk workflows | `admin/documents/page.tsx:438-470`; `portal/documents/bulk-actions.ts` | Confirm dialogs; bulk invite per-item results | False success; skipped hidden | P2 | Per-item results in UI |
| USE-008 | Admin/support workflows | `approvals/actions.ts:28-52`; `tickets/[ticketId]/actions.ts:79` | Admin consoles + confirm dialogs | Approval broken; delete=close | P1/P2 | Fix payload; real delete or relabel |
| USE-009 | Notifications | `NotificationBell.tsx:187-192` | Bell + SSE + polling fallback | Wrong links; interval leak | P2 | Fix routes; clear interval |
| USE-010 | Preferences | `NotificationPreferencesClient.tsx:89-96` | Save button + success banner | Failure silent; copy mismatch | P2 | Error feedback + copy fix |
| USE-011 | Error recovery | error boundaries; `retry.ts` | Try again; DataErrorNote; withRetry | Swallowed errors; raw messages | P2 | Central error mapping |
| USE-012 | Empty/loading states | 26 `loading.tsx`; `EmptyState.tsx` | Skeletons + empty components | False empties on failed loads | P2 | Gate empty on success flag |

## Findings

The full machine-readable list is in `04_usability_workflow_audit.json`. Summary by severity and status:

| # | Severity | Title | Confidence | Status |
|---|---|---|---|---|
| 1 | P1 | Self-service password reset dead-ends | high | open |
| 2 | P1 | Signup email-confirmation link 404s (API host) | high | open |
| 3 | P1 | Approval queue cannot approve/reject memberships (`roleId:""`) | high | open |
| 4 | P1 | Deletes report failure after succeeding (SDK 204 parsing) | high | open |
| 5 | P2 | Bulk document operations report false success | high | open |
| 6 | P2 | Ticket lists/counts capped at 25 rows | high | open |
| 7 | P2 | "Delete Ticket" only closes; copy promises soft-delete/restore | high | open |
| 8 | P2 | Ticket notification deep links 404 in the portal | high | open |
| 9 | P2 | Notification surfaces swallow failures / false empty state | high | open |
| 10 | P2 | NotificationBell SSE fallback leaks polling interval | high | open |
| 11 | P2 | Client-onboarding create swallows redirect ("NEXT_REDIRECT" shown) | high | open |
| 12 | P2 | Onboarding checklist cannot be completed in the web app | high | open |
| 13 | P2 | Session/MFA expiry has no explanation; `?mfa=required` ignored | high | open |
| 14 | P2 | Membership/approval actions lack confirmation + feedback | high | open |
| 15 | P2 | Change Password: unused current password + wrong rule | high | open |
| 16 | P3 | Portal ticket creation silent; tested action is dead code | high | open |
| 17 | P3 | Offline support absent (sw.js never registered) | high | open |
| 18 | P3 | Version history display-only / hidden for one version | high | open |
| 19 | P3 | No If-Match in web edit flows (silent overwrite) | medium | open |
| 20 | P3 | Lossy/missing form error handling | high | open |

Finding-format detail for each item (abbreviated from the JSON; IDs assigned by the aggregator):

### Finding: Self-service password reset dead-ends (P1)

- Severity: P1 · Confidence: High · Area: USE
- Evidence: `apps/api/src/routes/auth.ts:327-330` (redirectTo `/password-reset`), `apps/api/src/routes/auth.ts:349-378` (`requireAuth` reset), `apps/web/app/(public)/password-reset/page.tsx:17-37` (no token handling), `apps/web/app/auth/callback/route.ts:8-15` (the only code exchange).
- What is happening: the reset email points at a page that ignores the token and calls an endpoint that only works for a signed-in user.
- Why it matters / impact: account recovery fails; every reset escalates to an admin.
- Recommended fix: exchange the code (directly or via `/auth/callback`) before showing the reset form. Validation: E2E from the real email URL shape.
- Owner: Web + API auth owner · Effort: S · Status: open

### Finding: Signup email-confirmation link points at the API host (P1)

- Severity: P1 · Confidence: High · Area: USE
- Evidence: `apps/api/src/routes/auth.ts:182`; `infra/digitalocean/Caddyfile.prod:19-30`; `apps/api/src/middleware/not-found.ts:3-5`; `deploy-do.yml:333`.
- What is happening: `emailRedirectTo` is built from the API request host; only the web host serves `/auth/callback`.
- Impact: new signups cannot confirm their email → onboarding funnel stops.
- Fix: build the redirect from `APP_BASE_URL` (as forgot-password does). Validation: send a real confirmation email in a non-prod environment and follow it.
- Owner: API auth owner · Effort: S · Status: open

### Finding: Approval queue cannot approve/reject memberships (P1)

- Severity: P1 · Confidence: High · Area: USE
- Evidence: `apps/web/app/(admin)/admin/approvals/actions.ts:28-52`; `apps/api/src/validators/membership.ts:3-8`; `apps/api/src/routes/memberships.ts:123-127`.
- Impact: pending users stay locked out; admins see an error instead of approval.
- Fix: send the current/explicit roleId (or relax the schema), handle errors, add a test. Owner: API + web admin · Effort: S · Status: open

### Finding: Deletes report failure after succeeding (P1)

- Severity: P1 · Confidence: High · Area: USE (cross-cutting with API contracts)
- Evidence: `packages/sdk/src/client.ts:96`; 46 `res.status(204)` handlers (e.g. `documents.ts:597`, `api-keys.ts:173`); masked test at `sdk-expanded.test.ts:14-40`; UI effects at `AdminApiKeysClient.tsx:74-84` and `RecordDetail.tsx:56-68`.
- Impact: users believe deletes failed; stale rows/rollbacks; retries.
- Fix: treat 204/empty as `null` in `executeFetch`; add empty-body tests. Owner: SDK/API contracts · Effort: S · Status: open

### Findings 5–20

Details (evidence, impact, recommendation, owner, target, confidence) are recorded in
`04_usability_workflow_audit.json`; titles and severities are listed in the summary table above.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Clients cannot recover accounts (reset) | P1 | High | Access loss, support load | Reset page + requireAuth endpoint | Fix reset code exchange |
| New signups cannot activate | P1 | High | Onboarding funnel broken | emailRedirectTo host | Use APP_BASE_URL |
| Admins cannot approve users | P1 | High | Clients locked out | roleId "" vs UUID schema | Fix payload + test |
| Delete operations appear broken | P1 | High | Confusion, duplicate work, trust loss | SDK `res.json()` on 204 | Empty-body handling |
| Silent partial failures on bulk docs | P2 | Medium | Data-governance mistakes | Bulk loops/actions | Per-item results |
| Users miss tickets beyond row 25 | P2 | High for large tenants | Missed SLAs | Default limit 25 | Pagination |
| Notification links 404 | P2 | High | Missed updates | Wrong route mapping | Fix mapping + test |
| Preferences silently fail | P2 | Medium | Missed/extra email | Swallowed catch | Error feedback |
| MFA-enforced sessions dead-end | P2 | Medium (only when MFA enabled) | Lockout until support | `?mfa=required` unused | Step-up banner |
| SSE fallback interval leak | P2 | Medium | API load, rate limits | Discarded cleanup | Ref + clear |

## Recommendations

### Immediate / Release Blocking

1. Fix the four P1s (reset token exchange, signup redirect host, approval roleId, SDK 204 handling).
2. Add regression tests for each: E2E reset-from-email, E2E confirm-from-email, API+web approval test, SDK empty-body test.

### This Week

3. Correct notification ticket deep links and add a link-resolution test per module.
4. Make bulk document/ticket actions report per-item results (surface `successful`/`failed`/`skipped`).
5. Add success/error feedback and ConfirmDialog to membership status transitions and approvals.
6. Clear the SSE polling interval on unmount.

### This Month

7. Paginate ticket lists (portal + admin) and derive counts from API totals.
8. Fix the ticket delete semantics (real delete + tombstone/restore, or relabel to Close).
9. Fix notification preferences error handling and copy; distinguish "load failed" from "empty".
10. Rethrow redirects in the client-onboarding action; wire checklist completion (portal or admin).
11. Add session-expired copy and an explicit MFA step-up banner on the security page.
12. Remove or implement the Current Password check and publish the real password policy.

### Later / Platform Evolution

13. Register the service worker (or remove it) and add online/offline messaging.
14. Thread If-Match/version through edit forms and render 409 conflicts.
15. Add per-version document download and always-visible version info.
16. Standardize form error mapping (API message → field/inline/toast) across all modules.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix notification ticket href | One-line mapping | `NotificationBell.tsx:188`, `NotificationsPageClient.tsx:96` | Unit test href |
| Clear polling interval | Stops API leak | `NotificationBell.tsx:108-118` | Jest fake timers |
| Rethrow NEXT_REDIRECT | Create works as expected | `client-onboarding-command-center/actions.ts:38-40` | Unit test |
| Add signup try/finally | No stuck button | `signup/page.tsx:15-31` | Unit test rejection |
| Empty-body handling in SDK | 46 deletes stop lying | `packages/sdk/src/client.ts:96` | SDK test with empty body |
| Fix preferences copy | Removes contradiction | `NotificationPreferencesClient.tsx:172-176` | Copy review |
| Deep-link dashboard CTA | One click saved | `portal/dashboard/page.tsx:121` | Manual QA |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Password reset via code exchange | P1 | Auth owner | S | None |
| Signup redirect from APP_BASE_URL | P1 | API auth | S | Supabase allow-list |
| Approval roleId fix | P1 | API + web | S | None |
| SDK 204/empty-body support | P1 | SDK owner | S | None |
| Bulk per-item results (docs/tickets) | P2 | Web + API | M | SDK types |
| Ticket pagination | P2 | Web platform | M | API totals |
| Ticket delete semantics | P2 | Web admin + API | M | Product decision |
| Notification links + feedback | P2 | Web platform | S–M | None |
| MFA step-up surface | P2 | Web auth | M | None |
| Checklist completion UI | P2 | Web portal | M | None |
| Offline/PWA activation | P3 | Web platform | M | Product scope |
| If-Match editing | P3 | Web + SDK | M | None |

## Suggested Tests

- **Unit (web):** notification href mapping; SSE interval cleanup with fake timers; signup action rejection keeps button usable; client-onboarding action rethrows redirect.
- **Unit (SDK):** `executeFetch` with a 204/empty body resolves to null; delete methods do not retry on parse errors.
- **API:** PATCH membership with the approval-queue payload returns 400 today (regression), and returns 200 with a resolved role after the fix.
- **E2E (Playwright):** signup → follow confirmation URL shape → `/pending`; forgot password → follow reset URL shape (`?code=`) → new password → login; admin approve pending user; delete API key/document shows success; bulk document delete with one failing id shows partial result; ticket notification opens `/portal/support/<id>`; session expiry shows an explanation on `/login`.
- **Manual:** the 10 scenarios in Detailed Review.
- **CI:** add an integration job that runs the SDK against the real API container for one DELETE route (catches empty-body regressions).

## Suggested Documentation Updates

- `docs/TROUBLESHOOTING.md`: add "Deletes report failure but the row is gone" (SDK 204) and "Confirmation/reset emails" troubleshooting.
- `docs/ENVIRONMENT_VARIABLES.md`: clarify that `APP_BASE_URL` must be the web origin used in emails and that `NEXT_PUBLIC_API_URL` is the API origin (never a link target).
- New `docs/runbooks/PASSWORD_RESET_AND_EMAIL_LINKS.md`: how reset/confirm links are generated, allowed redirects, and how to test them.
- `docs/WEB_UI_CONVENTIONS.md`: feedback rules (every mutation reports success/error; bulk reports per-item; destructive transitions confirm; no swallowed catches).
- `docs/audits/.../04_usability_workflow_audit.md` (this report): link from the run INDEX.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `MFA_ENFORCEMENT_ENABLED` on in production? | Determines whether the MFA dead-end is live | Droplet env (not in repo) |
| Is `https://api.<domain>/auth/callback` allow-listed in Supabase? | If not, GoTrue may fall back to the dashboard Site URL and confirmation might work by accident | Supabase project settings |
| Is the ticket delete-by-close intentional? | Changes whether we relabel or implement tombstones | Product owner decision |
| What is the intended maximum ticket list size? | Drives pagination design | Product owner |
| Should the client onboarding command center be client-editable? | Drives checklist UI placement | Product owner |
| Is SMTP configured in production? | Preference emails may no-op regardless of UI | NOTIF-P2-002 residual (domain 30) |

## Appendix

- Target commit: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (`Merge PR #168: promote develop to main`).
- Route inventory: 319 `page.tsx`, 26 `loading.tsx`, 4 `error.tsx`, 3 `not-found.tsx`.
- 204-only API handlers: 46 (`grep -rho "res.status(204)" apps/api/src/routes/*.ts | wc -l`).
- Previous register: no `USE` rows; `UX-P3-001` (a11y breadth scan) belongs to domain 05 and was not duplicated.
- Machine-readable findings: `_domains/04_usability_workflow_audit.json` (20 findings: 4×P1, 11×P2, 5×P3; all `open`).
