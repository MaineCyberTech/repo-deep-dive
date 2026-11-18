# G1 — Security / auth / tenancy — delta re-audit

- **Target:** `main@3fa9f636c887fd28698852d37daa5dcef9593f60` (promoted 2026-11-07; worktree `origin/main`, read-only)
- **Delta window:** `6b7aa1a5..3fa9f636` — 132 commits (`git log --oneline 6b7aa1a..HEAD`), including SSO (#350/#351/#355/#359), the Nov-3 security batch (#335, commit `206365f1`), service-account docs (#369, `4169459e`), and the CSRF doc (`00a3a086`).
- **Previous full run:** `mainecybertech-20261103-0748-full-main-6b7aa1a`
- **Method:** static read of the changed surface + execution of the dependency-free repo checks (`node scripts/verify-rls.mjs`, `node scripts/check-rls-predicate.mjs`). `node_modules` is absent, so Jest suites were **not executed**; every "verified-fixed" below rests on code + committed tests at this commit, not a green run.
- **Scope honesty:** this is a lens re-audit, not a full sweep. It covers only the G1 surface listed in the brief plus the files those findings touch.

## Counts

### Re-verified prior findings (10)

| Domain | IDs | verified-fixed | partially-fixed | open | regressed |
|---|---|---|---|---|---|
| SEC | SEC-P1-011, SEC-P2-019, SEC-P2-020, SEC-P3-014, SEC-P3-015 | 4 | 1 | 0 | 0 |
| MT | MT-P1-005 | 1 | 0 | 0 | 0 |
| ACM | ACM-P2-009 | 1 | 0 | 0 | 0 |
| RLS | RLS-P3-009 | 1 | 0 | 0 | 0 |
| PRIV | PRIV-P2-010 | 1 | 0 | 0 | 0 |
| ADMIN | ADMIN-P2-010 | 1 | 0 | 0 | 0 |
| **Total** | **10** | **9** | **1** | **0** | **0** |

### New findings (4)

| ID | Severity | Status | Title |
|---|---|---|---|
| SEC-P1-012 | P1 | open | Client roles can still read internal comments on tickets and project tasks |
| SEC-P3-016 | P3 | open | `GET /ai/triage` returns every org triage draft to client roles holding `ai:view` |
| SEC-P3-017 | P3 | open | SSO callback forwards the whole cookie jar (incl. `mct_session`) to the API |
| SEC-P3-018 | P3 | open | SSO PKCE start and verifier-negative paths have no regression tests |

**Regression check:** none. No re-verified ID regressed, and no gate was removed in the delta (`git diff … | grep '^-.*requirePermission|requireAdmin|requireOrgAccess|isClientVisible'` yields only test mocks and multi-line reformatting).

## Re-verification detail

### SEC-P1-011 — verified-fixed (comments/timeline side channels)
The nested routes now load the parent's `visibility` and 404 before touching comments/timeline, then force `is_internal=false` for client members:
- `apps/api/src/routes/approvals.ts:465` / `:539` (parent visibility), `:475` (`is_internal`)
- `apps/api/src/routes/assets.ts:361` / `:430`, `:371`
- `apps/api/src/routes/findings.ts:464` / `:536`, `:473`
- `apps/api/src/routes/proposals.ts:1015` / `:1089`, `:1025`

Detail endpoints keep the same predicate (`approvals.ts:189`, `assets.ts:162`, `findings.ts:164`, `proposals.ts:145`). Regression tests: `apps/api/src/__tests__/client-visibility-sidechannels.test.ts:145-200`. Residual note: `module_timeline_events` is still returned for a client-visible parent because it has no per-event internal flag; only workflow events are written there today, so this is not a re-open.

### SEC-P2-019 — verified-fixed (file-request nested uploads)
`apps/api/src/routes/file-requests.ts:407` (uploads list) and `:444` (signed URL) both apply `isClientVisible` to the parent request; the signed URL also keeps the upload row bound to `request.id` + org (`:452-458`). Both routes now carry `requirePermission('file-requests','view')` (`:394`, `:421`). Tests: `apps/api/src/__tests__/file-requests.test.ts:477-524`.

### SEC-P2-020 — verified-fixed (AI draft outputs)
`apps/api/src/routes/ai.ts:31-35` adds `assertInternalDraftReader` (client member → 403) and awaits it at `:555` and `:581`. Tests: `apps/api/src/__tests__/ai.test.ts:236-253`. The client grant of `ai:view` is intentional (`supabase/migrations/5302463_client_portal_ai_and_visibility.sql:22-33`); its remaining data-scope consequence for triage drafts is filed separately as SEC-P3-016 (the triage surface was already the intended one in the migration header).

### SEC-P3-014 — partially-fixed (client-visibility fail-open / API keys)
Fail-open is fixed: `apps/api/src/lib/client-visibility.ts:100` now throws on the membership query error and `:107-110` returns `true` (client-scoped, visibility filter applied) instead of the staff view. The second half of the finding is unchanged: `:85-92` still returns `false` (staff view) for any `req.apiKey` request. That exemption is now documented (`:81-88`) and bounded today because `api-keys:manage` is an admin-scope permission (`supabase/migrations/5302118:306-307`), the client-role grant loop only grants `scope in ('portal','both')` (`:407-413`), and the route is permission-gated (`apps/api/src/routes/api-keys.ts:65`). It stays latent, not closed.

### SEC-P3-015 — verified-fixed (`GET /ai/triage` gate)
`apps/api/src/routes/ai.ts:336` mounts `requirePermission('ai','view')`, matching `:364`, `:553`, `:579`.

### MT-P1-005 — verified-fixed (cross-org admin widening)
- `apps/api/src/lib/admin-scope.ts:66-95`: `adminOrgIds` comes only from cross-tenant role rows; a non-super-admin admin is confined to the request-pinned org or `adminOrgIds`; `allTenants` still requires `profiles.is_super_admin` **and** a cross-tenant role (`:76-82`).
- `apps/api/src/middleware/org-access.ts:143-162`: an unpinned tenant admin is pinned to `adminMemberships[0]`; only a genuine super admin (profile flag + admin membership) stays org-agnostic.
- `apps/api/src/middleware/admin.ts:49-58`: an explicit org is rejected unless the caller is super_admin or admin in that org.
- `apps/api/src/routes/search.ts:78-97` uses the same `adminOrgIds` set.
- Tests: `apps/api/src/__tests__/admin-scope-cross-org.test.ts:38-117`, `middleware-org-access.test.ts:353`, `search-tenant-scope.test.ts:191`.

The non-admin branch (`admin-scope.ts:97-99`) still returns all approved orgs; that path only feeds non-admin exports and is not reachable behind `requireAdmin` for the admin surfaces that were over-wide.

### ACM-P2-009 — verified-fixed (module reads permission-gated)
`requirePermission(module,'view')` is now on every listed primary read: `assets.ts:44/75/108/143`, `approvals.ts:52/95/122/165`, `findings.ts:51/84/118/143`, `proposals.ts:48/81/111`, `qbr.ts:22/47`, `service-catalog.ts:20/43`, `file-requests.ts:343/370` (+ `:394/:421` nested), `domain-monitors.ts:41/70/100/157`, `vendors.ts:29/62/183`. Vendors also stopped serving client contracts under the admin-only `vendors` module: the routes use the client-scope `vendor-contracts`/`vendor-contacts` permissions (`supabase/migrations/5302118:260-267`) and still apply client visibility (`vendors.ts:47`, `:74`).

### RLS-P3-009 — verified-fixed (notification org scoping)
`supabase/migrations/5302466_notifications_insert_membership_scope.sql:19-36` requires `user_id = auth.uid() AND (organization_id is null OR public.is_org_member(organization_id))` on the self branch. `is_org_member` filters `status='approved'` (`5302100:14-19`) and has a pinned `search_path` (`5302112:20`). `node scripts/verify-rls.mjs` → 140/140 tables, 1,036 policies, **0 failures / 0 warnings**; `node scripts/check-rls-predicate.mjs` → PASS over 36 migrations newer than 5302430. Covered by `rls-policy-fix-migrations.test.ts:164-178`.

### PRIV-P2-010 — verified-fixed (anon store_quotes insert)
`supabase/migrations/5302465_revoke_anon_store_quotes_insert.sql:16-17` drops `anon_insert_quotes` and revokes `INSERT` from `anon`. The only anon grant was `5302434:74`; no later migration re-grants it (`5302465` is the last file touching `store_quotes`). Authenticated writes keep the approved-membership predicate (`5302448:19-23`) and `POST /store/quotes` remains the consent-enforcing path. Covered by `rls-policy-fix-migrations.test.ts:140-162`.

### ADMIN-P2-010 — verified-fixed (client decisions)
`apps/api/src/routes/proposals.ts:813-823` requires approved + published/client-visible; `:825-830` rejects non-client callers; `:832-835` refuses to overwrite an existing decision (409). The reset path is staff-only and org-scoped via router-level `requireOrgAccess` + `loadOwned` (`:886-912`). Tests: `apps/api/src/__tests__/proposals.test.ts:368-401`.

## New findings

### SEC-P1-012 — P1 — Client roles can read internal ticket/project comments
`is_internal` is a real, used flag (admin ticket form, `apps/web/app/(admin)/admin/tickets/[ticketId]/page.tsx:562`; admin project tasks, `apps/web/components/admin/ProjectTaskListV5.tsx:988`) and the portal UI filters it client-side (`apps/web/app/(portal)/portal/support/[ticketId]/page.tsx:172`). The API does not:
- `apps/api/src/routes/tickets.ts:143` — `GET /tickets/:id` embeds `ticket_comments(*)` with no predicate.
- `apps/api/src/routes/tickets.ts:356-378` — `GET /tickets/:id/comments` returns every row; no permission/client gate.
- `apps/api/src/routes/projects.ts:845-847` — `GET /projects/:id/tasks/comments` filters `is_internal=false` **only if the caller asks**; omitting the parameter returns internal notes (`:830-851`, no gate).

Client roles have `tickets:view`/`projects:view` (`supabase/migrations/5302118:30,38`; client grant loop `:407-430`), and the `mct_session` cookie is scoped to the parent domain, so a client can call the API directly. RLS is no backstop: `ticket_comments` SELECT is org-membership only (`supabase/migrations/5302026…v3.sql:1188-1195`). Secondary: the comment POST accepts caller-supplied `isInternal` (`tickets.ts:398-405`), so a `client_admin` can also forge an internal-only note.

**Remediation:** require `tickets:view`/`projects:view`; add `.eq('is_internal', false)` when `isClientMember(req)`; replace the embedded `ticket_comments(*)` with a filtered sub-select (or drop it); force `is_internal=false` for client callers on POST; add an `is_internal=false OR is_staff(...)` predicate to the RLS SELECT policies; add a client-token regression test for all three paths.

### SEC-P3-016 — P3 — All org triage drafts visible to clients with `ai:view`
`supabase/migrations/5302463:22-33` grants `ai:view` to client roles by design. `apps/api/src/routes/ai.ts:336-357` lists `ticket_triage_drafts` for the org with no `created_by`/visibility filter, and the table has no visibility column (`5302065:4-21`). The portal renders the rows (`apps/web/app/(portal)/portal/ai-triage/page.tsx:27-60`), contradicting the documented "on own tickets" contract (`docs/modules/ai-tools.md:44`). Bounded to the client's own tenant, so P3. **Fix:** filter to `created_by = req.authUser.userId` for client members (or add a visibility column), and test it.

### SEC-P3-017 — P3 — SSO callback forwards the whole cookie jar
`apps/web/app/auth/callback/route.ts:24-27` posts `request.headers.get("cookie")` to `/api/v1/auth/callback`; the API only extracts the `sb-<ref>-auth-token-code-verifier` cookie (`apps/api/src/routes/auth.ts:223-229`, `:249-253`). The session JWT and CSRF token therefore cross the web→API boundary in a JSON body. No body-logging sink was found (`middleware/request-id.ts`; `middleware/error.ts:46-52`; Sentry scrubs with `sendDefaultPii:false`, `lib/sentry.ts:16-17`), so this is least-privilege hygiene. **Fix:** forward only the verifier (or use the existing `code_verifier` field).

### SEC-P3-018 — P3 — SSO start / verifier-negative paths untested
`apps/api/src/routes/auth.ts:796-824` (`/auth/sso`) has no test; no test covers `ssoLoginAction` (`apps/web/lib/auth/auth-actions.ts:45-64`). The new callback suite (`apps/api/src/__tests__/auth.test.ts:603-655`) covers only the happy path, a generic 401 and the missing-`auth_code` 400 — it never asserts that a missing/mismatched verifier fails, so dropping PKCE binding would not fail CI. **Fix:** add the negative tests listed in the JSON. Assurance gap, not an exploit.

## SSO / callback / CSRF review (new surface)

**What checks out at `3fa9f636`:**
- `/auth/sso` builds a fresh 48-byte base64url verifier + SHA-256 S256 challenge per call, hardcodes `provider=custom:authelia`, and builds `redirect_to` from `APP_BASE_URL`, never from the request (`apps/api/src/routes/auth.ts:796-824`).
- The callback exchanges with `grant_type=pkce` (previously `authorization_code` — the #355 fix) and forwards only the verifier it finds in the cookie blob (`auth.ts:249-267`). There is no `code_verifier`/code logging and the upstream error is reduced to a generic 401 (test `auth.test.ts:634-655`).
- The web callback derives the redirect origin from `APP_BASE_URL` (compose sets it for the web service: `infra/digitalocean/docker-compose.yml:241`), so `Host`/`request.url` no longer influences the redirect target (`apps/web/lib/auth/callback-redirect.ts:36-46`). `next` is same-origin-only with `//`, `\`, whitespace and absolute URLs rejected (`callback-redirect.ts:15-25`; tests `apps/web/__tests__/lib/auth/callback-redirect.test.ts:20-46`). No percent-encoding bypass found (`%2F%2F`/`%5C`/`..` all stay same-origin).
- PKCE blocks login CSRF on the callback: an attacker's code is bound to the attacker's challenge, and the victim's browser does not hold the matching verifier cookie (the verifier is generated by the API, returned only to the web server action, and stored `httpOnly`). No session fixation primitive found.
- `/auth/sso` was added to the CSRF skip list (`apps/api/src/middleware/csrf.ts:46`), which is safe: the route has no side effect beyond minting a verifier and is rate-limited.
- MFA: the SSO-issued `aal1` token is still subject to `requiresSecondFactor` on every non-`/auth/*` route, and privileged (admin/super_admin) sessions are enforced unconditionally (`apps/api/src/lib/mfa.ts:136-152`, wired in `middleware/auth.ts:119-125,173-175`), so SSO does not downgrade an enrolled admin.

**Residual risk noted, not filed as a finding:** if the hosted Supabase project ever accepts the callback code without a verifier (PKCE disabled / implicit flow), the GET `/auth/callback?code=…` route becomes login-CSRF-able. The code always sends a challenge for the SSO path, so this is a project-configuration dependency, not a repo defect.

## What changed since Nov 3

- **#335 (commit `206365f1`)** closed 9 of the 10 re-verified items in one batch: parent-visibility + `is_internal` filters on the four comment/timeline modules, file-request nested visibility, an internal-only guard on `ai_draft_outputs`, `requirePermission(...,'view')` on the module reads, the `admin-scope`/`org-access` admin-org pinning, the two corrective migrations (`5302465`, `5302466`), and the client-decision state/identity/immutability checks.
- **SSO (#350, #355, #359, #351)** is new surface. The grant-type and callback-origin fixes are correct; the two P3 hygiene/assurance gaps above are the only issues found in it.
- **Service-account docs (#369)** add no credentials; it names custody locations (`/etc/kestrel-access-import/portal.env`, Vaultwarden) and CI identity model. No secret value is committed (`grep` for `eyJ…`/`sk_live`/`mct_…` in `AGENTS.md`/`review.md`/`docs/*.md` finds none).
- **Delta-added seeds** (`supabase/seeds/09_super_admin_memberships.sql`, `00_local_auth_users` Julian entry) are local-only (`supabase/config.toml` `sql_paths`; deploy uses `supabase db push` over `supabase/migrations`), so they do not reach prod. The `/test-accounts` helper remains a documented dev-only affordance (default password `1`, gate `host.endsWith('.us')` — `apps/web/lib/auth/auth-actions.ts:185-193`, `apps/web/lib/test-accounts.ts:19-24`); worth keeping in mind for the dev droplet but not a delta finding.
- **No regression** in the re-verified set; the one status change versus the Nov 3 verdict is SEC-P3-014 → partially-fixed because the API-key exemption was intentionally retained rather than closed.
