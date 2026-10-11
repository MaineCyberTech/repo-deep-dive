# Supabase RLS Policy Deep-Dive Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (MaineCyberTech portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent `37_supabase_rls_policy_deep_dive` (area `RLS`)
- Area code: RLS
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/37_supabase_rls_policy_deep_dive.md`
- Scope limitations: read-only audit; no Supabase instance or network access. Node.js is not installed in the audit environment, so `scripts/verify-rls.mjs` and `scripts/check-rls-predicate.mjs` were **replicated in Python** from their source (deterministic regex logic) rather than executed; all replication outcomes are labelled. `RLS_READS_ENABLED` / `RLS_WRITES_ENABLED` values are GitHub secrets and are **not verifiable from the repo**. Prometheus `promtool` tests were read, not executed (no docker/promtool).

## Scope

Reviewed at `8d299b8d`:

- `supabase/migrations/*.sql` (134 files, 17,105 lines) — RLS enablement, policies, grants/roles, storage policies, functions/triggers, SECURITY DEFINER.
- App-side scoped-client rollout: `apps/api/src/services/supabase.ts` (`getScopedClient`), `apps/api/src/lib/rls-startup-check.ts`, `apps/api/src/main.ts`, `apps/api/src/lib/metrics.ts`, `apps/api/src/lib/service-role.ts`, route/service call sites.
- Guards/CI: `scripts/verify-rls.mjs`, `scripts/check-rls-predicate.mjs`, `scripts/check-docs-counts.mjs`, `.github/actions/unit-tests/action.yml`, `.github/workflows/{test,validate,supabase-migrations,e2e,db-restore-test}.yml`.
- Observability: `infra/digitalocean/prometheus.rules.yml`, `prometheus.rules.test.yml`, `alertmanager.tmpl.yml`, `docker-compose.yml`.
- Docs: `docs/RLS-rollout.md`, `docs/RLS-coverage-matrix.md`, `docs/MT-P0-001-RLS-remediation-design.md`, `docs/adr/README.md` (ADR-008), `AGENTS.md`, `review.md`, `CHANGELOG.md`.
- Generated types: `packages/sdk/src/database.types.ts` + `scripts/generate-db-types.js`.

Not reviewed: live database state, hosted Supabase project settings (auth MFA, storage bucket config in the dashboard), GitHub secret values, runtime behavior of the deployed API.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `supabase/migrations/` (134 files) | SQL | Full policy/grant/function history; effective state is the append-only fold | 137 live tables, all RLS-enabled (replicated scan) |
| `scripts/verify-rls.mjs` | Guard | CI gate: RLS enablement, policy-less tables, drop/create pairing | 3 rules; wired in test.yml + validate.yml |
| `scripts/check-rls-predicate.mjs` | Guard | Blocks the raw status-unfiltered memberships predicate in new migrations | Baseline `5302430` |
| `apps/api/src/services/supabase.ts:198-226` | Code | `getScopedClient` allow-list switch (read/write), platform-admin fallback, metrics | The rollout's core |
| `apps/api/src/lib/rls-startup-check.ts` | Code | Fail-closed production boot when the read allow-list is empty | Writes log only |
| `apps/api/src/routes/*` (43 files) | Code | 383 scoped call sites, 43 module keys; 238 direct admin call sites remain | Mixed adoption (see finding) |
| `infra/digitalocean/prometheus.rules.yml:94-142` | Config | Runtime RLS-regression detection (IR-P1-006) | Two rules + promtool unit tests |
| `docs/RLS-rollout.md`, `docs/RLS-coverage-matrix.md` | Docs | Rollout procedure, preconditions, coverage snapshot | Matrix self-declared stale snapshot |
| `packages/sdk/src/database.types.ts` | Generated | Types generated from migrations; CI `--check` | `Functions: Record<string, never>` |

## Verification Performed

| Evidence / command | Type | Why relevant | Observed result |
|---|---|---|---|
| `git log -1 --format='%H %ci %s'` | Command | Bind the audit to the commit | `8d299b8d… Merge PR #168` |
| `git diff --name-only 9c0b88c..8d299b8d -- supabase/` | Command | Are migrations changed since the previous run? | **Empty** — migrations byte-identical; previous migration verifications carry, re-checked below |
| Python replication of `scripts/verify-rls.mjs` (node unavailable) | Re-implementation | Reproduce the CI hygiene scan | tables 137, rls-enabled 137, create-policy statements 1021, failures 0, warnings 0 (mfa_recovery_codes carries `-- rls: deny-all`) |
| Python replication of `scripts/check-rls-predicate.mjs` | Re-implementation | Reproduce the DATA-P1-001 guard | 6 migrations newer than baseline 5302430 checked, **0 violations** |
| Python SECURITY DEFINER scan (effective definitions, `set search_path` + `alter function … set search_path`) | Re-implementation | Prompt special check | 18 definer functions, **all** pinned (`is_org_member` pinned by `alter function` in 5302112:19) |
| Python effective-policy replay (apply every `create policy`/`drop policy` in order, scan live bodies) | Re-implementation | Find leftovers a baseline-exempt static guard misses | 516 live policies; 1 live raw-predicate policy (`dv_update`); 7 live policies with dead permission pairs; 1 short admin role gate (`notifications_insert_system_or_admin`, by design) |
| `grep -rn "getScopedClient(req" apps/api/src` | Command | Rollout surface | 43 module keys, 383 call sites, 43 route files |
| `grep -rn "getSupabaseAdmin" apps/api/src --include='*.ts' \| grep -v __tests__ \| wc -l` | Command | Remaining RLS-bypass surface | 238 direct admin call sites |
| `grep -rn "webhook_dead_letters" supabase/migrations/` | Command | RLS-P2-002 verification | Only SELECT/INSERT/UPDATE policies exist; no DELETE |
| `grep -n "auth.admin" apps/api/src/routes/auth.ts` | Command | New finding check | `signOut`/`updateUserById` called on a `getScopedClient(...,'write')` client |
| `grep -rn "RLS_READS_ENABLED\|RLS_WRITES_ENABLED"` | Command | Wiring | deploy-do.yml:615-616,647,707-708 → droplet `.env` (0600); compose:108-109; e2e.yml:120 sets `auth` |
| `promtool test rules` | Not run | IR-P1-006 verification | No docker/promtool in audit env; tests read only — **not reproducible** here |

## Executive Summary

RLS is in unusually good shape for a repo of this size: **every one of the 137 live public tables enables RLS** (replicated scan matches the AGENTS.md/review.md count of 137/1021 exactly), policies overwhelmingly route through the approved-aware `is_org_member`/`user_has_permission` helpers (268/41 live-policy usages), all 18 SECURITY DEFINER functions pin `search_path`, the anon blanket DML grant was removed in `5302434`, the avatars bucket is declared with owner-scoped policies (`5302433`), and three CI guards (`verify-rls.mjs`, `check-rls-predicate.mjs`, `check-docs-counts.mjs`) plus a fail-closed production boot check (`rls-startup-check.ts`) protect the posture. Runtime telemetry for tenant-isolation regressions now exists (counters + two Prometheus rules with promtool unit tests).

The remaining risks are concentrated in three places:

1. **Effective-state leftovers** that the baseline-exempt static guards miss: `document_versions.dv_update` still uses the raw unfiltered membership predicate (pending/suspended members can UPDATE version rows via PostgREST), and seven live policies reference permissions that do not exist in the catalog (dead write predicates).
2. **The scoped-client rollout is partial and secret-defined**: 43 module keys / 383 scoped call sites vs 238 direct service-role call sites; several tenant modules (satisfaction-pulse, dynamic-client-forms, the final/ generic CRUD tables) never consult the allow-list, service helpers bypass it, and two `auth.admin.*` calls sit on the scoped client (breakage if `auth` is write-enabled). Whether "RLS is already enforced for most read paths" (docs) is true cannot be verified from the repository.
3. **One policy-level injection gap**: `store_quotes` keeps a public `INSERT WITH CHECK (true)` policy from before tenant scoping, so any authenticated/anon writer can insert rows tagged with an arbitrary `organization_id`.

Recommended next actions, in order: fix `dv_update` and `store_quotes` (new migrations), add the `webhook_dead_letters` DELETE policy, move the `auth.admin` calls off the scoped client, and extend `verify-rls.mjs` with an effective-state pass (raw predicate, role-gate drift, policy↔catalog drift).

## Inventory

### Table policy inventory (summary; effective state, replicated)

| Metric | Count | Notes |
|---|---:|---|
| Live public tables | 137 | Every one has `enable row level security` (CI-enforced) |
| `create policy` statements (all history) | 1021 | The number AGENTS.md/review.md/check-docs-counts guard |
| Effective live policies (drop/create replayed) | 516 | select 144, insert 128, update 116, delete 104, all 24 |
| Live policies using `is_org_member` | 268 | approved-aware helper (5302100 + 5302112 pin) |
| Live policies using `user_has_permission` | 41 | 7 reference pairs absent from the permission catalog |
| Live policies using `is_super_admin()` | 101 | Explicit platform bypass |
| Live policies using `auth.uid()` | 147 | Owner-scoped predicates |
| Tables with a deny-all marker | 1 | `mfa_recovery_codes` (5302427, service-role only) |
| Live raw unfiltered membership predicates | 1 | `document_versions.dv_update` (5302081) — new finding |

### Storage policy inventory

| Bucket | Declared | Policies | State |
|---|---|---|---|
| `documents` | 5302026:2297 (private) | `documents_bucket_select_aligned` (via `can_read_document`), `insert/update/delete_aligned` (org from `storage_path_org_id(name)` + approved member + documents permission) | Good; residual name-derived org (P3) |
| `logos` | 5302031:10 (public) | `logos_select_public` (authenticated), `logos_insert_admin_only` (super admin, 5302057:56-65) | Good; no user update/delete (service-role only) |
| `avatars` | 5302433:30 (public) | `select` (authenticated), `insert/update/delete_own` (first folder segment = `auth.uid()`) | FILE-P2-001 fix verified present |

### Function review (effective definitions)

| Function | Definer | search_path | Grants/notes |
|---|---|---|---|
| `is_org_member`, `is_org_approved_member`, `is_super_admin`, `user_has_role`, `user_has_permission`, `can_read_document`, `storage_path_org_id` | Yes | Pinned (`is_org_member` pinned via `alter function` 5302112:19) | Helpers; `can_read_document` maps manage→edit + 8 admin keys (5302129:658) |
| `approve_project_task`, `add_project_task_comment` | Yes | Pinned (5302435) | `auth.uid()` identity guard; execute revoked from public/anon |
| `mark_task_read`, `bulk_update_with_version`, `increment_article_count`, `claim/release_file_request_slot`, `release_slot_token`, `bootstrap_portal_access`, `handle_new_user` | Yes | Pinned | RPC hardening from 5302129/5302431 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Supabase migrations | 4 | Append-only, forward-fix, idempotent; post-push drift check | Research doc/design stale | Refresh design doc references |
| SQL schema | 4 | Tenant/version/soft-delete columns, constraints | Pre-baseline leftovers possible | Effective-state scan in CI |
| RLS enablement | 5 | 137/137 + CI rule 1 + deny-all marker | None material | Keep |
| Policies | 3 | Approved-aware helpers dominant | `dv_update` raw predicate; 7 dead-permission policies; `store_quotes` insert | Fix three migrations + lint |
| Grants/roles | 4 | 5302434 removed anon blanket DML | authenticated blanket DML remains (by design) | Document; keep RLS as the gate |
| Storage bucket policies | 4 | 3 buckets declared, org/owner-scoped | Name-derived org helper | Bind to documents row where feasible |
| Functions/triggers | 4 | All definers pinned; RPC identity fixed | No DB_FUNCTIONS.md inventory | Generate + CI-check function inventory |
| Security definer | 5 | 18/18 pinned; execute revoked on RPCs | None found | Keep |
| Generated types | 4 | Generated from migrations; CI `--check` | `Functions` map empty (RPCs untyped) | Extend generator to RPCs |
| App queries | 3 | 43 modules scoped; boundary metrics | Partial/mixed adoption; `auth.admin` misuse | Complete rollout + manifest |
| Tenant/user matching | 4 | Approved helpers everywhere new | `dv_update` exception | Fix + effective-state lint |
| Admin bypass | 4 | Platform-admin fallback + audited impersonation | Secret-defined rollout not auditable | Publish enabled-module manifest |

## Detailed Review

### Item: Scoped-client rollout (`getScopedClient` + allow-lists)

- Evidence: `apps/api/src/services/supabase.ts:198-226`; `docs/RLS-rollout.md:13-28`; `apps/api/src/__tests__/get-scoped-client.test.ts`; `.github/workflows/e2e.yml:120`.
- What it does: returns the user-scoped client (RLS enforced) when the module key is in `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` and `req.userJwt` exists; platform admins keep service-role; every selection is metered.
- Current controls: fail-closed production read gate; platform-admin fallback audited via `requireOrgAccess`/impersonation log; unit tests cover selection, independence of read/write, platform admin, metrics.
- Missing controls: no repo-visible record of which modules are enabled; modules with no scoped call sites cannot be enabled; `auth.admin.*` calls on the scoped client (new finding).

### Item: Static guards + CI

- Evidence: `scripts/verify-rls.mjs:6-19,50,128-318`; `scripts/check-rls-predicate.mjs:38,52-57`; `.github/actions/unit-tests/action.yml:35-59`; `scripts/check-docs-counts.mjs:403-410`.
- What works: RLS enablement gate, policy-less warning, drop/create pairing for migrations ≥5302427, raw-predicate gate for migrations >5302430, doc-count guard for the policy count, DB-types `--check`.
- Gap: all guards are file-scoped/baseline-exempt; the effective state is not scanned (new P3 lint finding).

### Item: Runtime detection (IR-P1-006)

- Evidence: `apps/api/src/lib/metrics.ts:163-196`; `infra/digitalocean/prometheus.rules.yml:94-142`; `prometheus.rules.test.yml:20-95`.
- State: counters + `MCTTenantScopeRegression` + `MCTRlsEnforcedShareCollapsed` rules with promtool unit tests. Promtool not wired into CI; delivery depends on Alertmanager receiver config (unverifiable from repo).

### Item: `webhook_dead_letters` write path

- Evidence: `5302050:25-57` (no DELETE policy); `webhook-management.ts:173-241` (scoped-write deletes).
- State: RLS-P2-002 still open; docs (`AGENTS.md:97`, `review.md:103`) misdescribe the delete client.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| RLS-001 | Supabase migrations | 134 files; supabase-migrations.yml | Append-only forward fixes + drift check | Effective state unscanned | P3 | Effective-state CI pass |
| RLS-002 | SQL schema | Bootstrap + module migrations | Tenant/version columns | — | P3 | — |
| RLS-003 | RLS enablement | replicated scan 137/137 | verify-rls rule 1 in CI | — | — | Keep |
| RLS-004 | Policies | 516 effective; helper-dominated | Approved-aware helpers | dv_update; dead predicates; store_quotes insert | P2 | Fix migrations + lints |
| RLS-005 | Grants/roles | 5302434 | Anon narrowed to explicit allowlist | Authenticated blanket DML (by design) | P3 | Document |
| RLS-006 | Storage bucket policies | documents/logos/avatars | Org/owner-scoped | Name-derived org helper | P3 | Bind to documents row |
| RLS-007 | Functions/triggers | 18 definers pinned | search_path pinned; RPC grants narrowed | No inventory doc | P3 | DB_FUNCTIONS.md |
| RLS-008 | Security definer | SECURITY DEFINER scan | 18/18 pinned | — | — | Keep |
| RLS-009 | Generated types | database.types.ts + `--check` | CI freshness gate | RPCs untyped | P3 | Extend generator |
| RLS-010 | App queries | 383 scoped / 238 admin | Per-module switch + metrics | Partial/mixed adoption | P3 | Manifest + conversion |
| RLS-011 | Tenant/user matching | is_org_member/user_has_permission | Approved-aware | dv_update exception | P2 | Fix |
| RLS-012 | Admin bypass | platform-admin fallback; impersonation log | Audited cross-tenant path | Secret-defined allow-list | P3 | Publish manifest |

## Findings

Findings below reference titles; IDs are assigned by the aggregator. Full structured data is in `37_supabase_rls_policy_deep_dive.json`.

### MSP platform-admin role keys missing from post-5302129 admin-gate RLS policies (P2, verified-fixed)

- Evidence: `5302436:31-78` restores all five regressed DELETE gates via `user_has_role(...,8 keys)`; `5302436:83-103` asserts it; effective-policy scan found no other short admin gate.
- Status: **verified-fixed** at 8d299b8d (migrations unchanged since 9c0b88c). Residual: the drift lint was never added (see lint finding).

### webhook_dead_letters has no user-scoped DELETE policy while the API deletes via the RLS client (P2, still-open)

- Evidence: `5302050:25-57` (no DELETE policy, none later); `webhook-management.ts:173-205,228-241` (scoped-write delete → 404 on zero rows); `AGENTS.md:97`/`review.md:103` claim service-role.
- Impact: retry/dismiss silently fail if `webhook-management` enters `RLS_WRITES_ENABLED`. Fix: add the DELETE policy or pin those deletes to the admin client; correct the docs.

### approve_project_task / add_project_task_comment trust a caller-supplied user id (P2, verified-fixed)

- Evidence: `5302435:44-46,100-102` (`p_user_id` must equal `auth.uid()` for end users); `48-56,108-116` approved-membership; `152-155` grants narrowed.

### 5302116 grants anon UPDATE/DELETE on every table (P3, partially-fixed)

- Evidence: `5302434:33-36,41-67,72-86` removes default + existing anon DML and re-grants a 3-insert/4-select allowlist. The title's second half — the RLS-off × anon-write lint — does not exist (`verify-rls.mjs:6-19`).

### No behavioral RLS allow/deny matrix test (P3, still-open)

- Evidence: CI runs only static scripts (`.github/actions/unit-tests/action.yml:49-59`); `get-scoped-client.test.ts` mocks Supabase; no RLS assertions in `apps/web/e2e/` even though `e2e.yml:94` runs `supabase db reset`.

### storage_path_org_id trusts a client-controlled object name (P3, partially-fixed)

- Evidence: `5302026:799-825` (name-derived); `5302129:718-769` (membership+permission on the derived org); `documents.ts:265-272` (API path↔org equality). Residual bounded to intra-tenant path control.

### Duplicate scoped-client tests and stale coverage-matrix snapshot (P3, partially-fixed)

- Evidence: `supabase-scoped-client.test.ts` + `get-scoped-client.test.ts` both test selection; matrix self-declares stale (`RLS-coverage-matrix.md:6-9`); guarded counts match (137/1021) but the matrix table itself is unguarded.

### API defaults to the service-role DB client (RLS bypass) (P2, partially-fixed)

- Evidence: `supabase.ts:198-226`; `rls-startup-check.ts:26-54`; `main.ts:12-14`; `metrics.ts:163-196`. Residual: writes non-fatal; allow-list secret-defined; 238 admin call sites.

### No runtime detection or alerting for tenant-isolation (RLS) regressions (P1, partially-fixed)

- Evidence: `metrics.ts:163-196`; `supabase.ts:221-224`; `prometheus.rules.yml:94-142`; `prometheus.rules.test.yml:20-95`. Residuals: promtool not in CI; no DB_ERROR/empty-result signal; no E2E isolation assertion.

### Approved-membership RLS predicate reintroduced six times (P1, verified-fixed)

- Evidence: `check-rls-predicate.mjs:38,52-57` wired at `.github/actions/unit-tests/action.yml:53-59`; `5302412`, `5302418`, `5302420` rewrites; replication: 0 violations in 6 migrations > baseline. Residual: baseline exemption (see dv_update).

### RLS policies reference `manage` permissions that no role holds (P3, still-open)

- Evidence: live policies `contracts_insert/update`, `contract_signers_manage`, `appointments_insert/update`, `project_members_manage`, `onboarding_update_same_org` reference pairs absent from `5302118`/`5302028`/`5302131`. Fix: add catalog rows or rewrite to create/edit/delete; add the catalog lint.

### document_versions UPDATE policy still uses the raw unfiltered membership predicate (P2, open — new)

- Evidence: `5302081:25-30` creates `dv_update` with `organization_id IN (SELECT organization_id FROM memberships WHERE user_id = auth.uid())`; no later drop; 5302112 missed it; baseline-exempt. Impact: pending/suspended members can UPDATE version metadata via PostgREST. Fix: recreate with `is_org_member` + documents permission; add effective-state scan.

### store_quotes public INSERT policy allows arbitrary organization_id after tenant scoping (P2, open — new)

- Evidence: `5302105:15-16` (`WITH CHECK (true)`, no TO clause) survives `5302132:8-21`; `5302408:41-52` adds `organization_id` + member read; `5302434:74` grants anon INSERT; authenticated keeps the blanket grant. Impact: cross-tenant row injection into a tenant's quote pipeline. Fix: `WITH CHECK (organization_id IS NULL)` for the public policy (or membership check for org-tagged inserts).

### Auth write endpoints call GoTrue admin APIs through the RLS-scoped client (P2, open — new)

- Evidence: `auth.ts:305-308` (`signOut`), `380-381` (`updateUserById`) on `getScopedClient(...,'auth','write')`; scoped client uses the anon key (`supabase.ts:121-143`). Impact: adding `auth` to `RLS_WRITES_ENABLED` breaks sign-out/password reset. Fix: use the admin client for `auth.admin.*`.

### No static lint for RLS role-gate drift or policy↔permission-catalog drift (P3, open — new)

- Evidence: `verify-rls.mjs:6-19` (three rules only); `5302436:83-103` (scoped assertion); the 20261002 report's suggested lints (b)/(d) do not exist. Recommendation: effective-state pass covering raw predicates, role gates, catalog pairs.

### Scoped-client adoption is partial: several tenant modules have no RLS call sites and service helpers bypass the scoped client (P3, open — new)

- Evidence: `services/satisfaction-pulse-widget.ts` (17 admin calls), `services/dynamic-client-forms-builder.ts` (10), `services/approvals.ts:211-220` (`addTimelineEvent`, used by 4 routes), `routes/final/crud.ts:25-183` (10 tenant tables, admin only), `business-os.ts`/`dashboard.ts`/`search.ts`/`bulk.ts`. Docs claim ~44 read/17 write modules (secret); code defines 43 module keys. Fix: publish a non-secret manifest + convert or document each module.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Pending/suspended member updates document version rows | P2 | Medium | Metadata tampering under the API's back | `5302081:25-30` | Recreate `dv_update` with approved-aware predicate |
| Cross-tenant quote injection | P2 | Medium | Tenant pipeline pollution/phishing | `5302105:15-16` + `5302408` | Constrain INSERT `organization_id` |
| Dead-letter deletes silently 404 under RLS writes | P2 | Medium (secret-dependent) | Ops/retention failure | `5302050` + `webhook-management.ts:173/228` | Add DELETE policy |
| `auth` write enablement breaks sign-out/password reset | P2 | Low (secret-dependent) | Auth outage | `auth.ts:305/380` | Admin client for `auth.admin.*` |
| Dead permission predicates break non-super-admin writes when enabled | P3 | Medium | 0-row/403 module writes | 7 live policies vs catalog | Catalog rows or policy rewrite + lint |
| Rollout coverage unverifiable from repo | P3 | Certain | False confidence in isolation | secret allow-list; 43 keys/238 admin sites | Publish manifest; complete conversion |
| Semantic policy regression undetected | P3 | Medium | Silent isolation weakening | static-only gates | Behavioral matrix in CI |

## Recommendations

### Immediate / Release Blocking

None — no P0/P1-with-exploit-path was found. The P1 rows are partial-fix residuals (monitoring, predicate guard coverage).

### This Week

1. Recreate `document_versions.dv_update` with `is_org_member` + documents permission (new migration).
2. Constrain `store_quotes` public INSERT (`organization_id IS NULL`) or add membership gating.
3. Add the `webhook_dead_letters` DELETE policy (or pin those deletes to the admin client) and correct `AGENTS.md`/`review.md`.
4. Move `auth.admin.*` calls in `auth.ts` to `getSupabaseAdmin()`.
5. Wire promtool `check rules`/`test rules` into CI for the RLS alert rules.

### This Month

6. Extend `verify-rls.mjs` with the effective-state pass (raw predicate, role-gate drift, policy↔catalog pairs).
7. Add the behavioral RLS allow/deny matrix (local Supabase harness already used by e2e).
8. Publish the non-secret enabled-module manifest and reconcile the docs' "~44/17" claim.

### Later / Platform Evolution

9. Bind storage path derivation to server-side records where feasible.
10. Generate `docs/DB_FUNCTIONS.md` (definer inventory + authz contract) with a CI check.
11. Extend the DB-types generator to RPC signatures; guard the coverage-matrix table counts.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| New migration fixing `dv_update` | Removes a live DATA-P1-001-class predicate | `supabase/migrations/` | Pending member UPDATE denied; member UPDATE allowed |
| New migration fixing `store_quotes` INSERT | Blocks cross-tenant row injection | `supabase/migrations/` | Authenticated insert with foreign org → denied |
| webhook dead-letter DELETE policy | Removes silent 404 under RLS writes | `supabase/migrations/` | Org admin delete succeeds |
| `auth.admin` calls → admin client | Prevents auth breakage if `auth` is write-enabled | `apps/api/src/routes/auth.ts` | Sign-out/reset still pass tests |
| Add promtool to CI | Alerts can't silently become unfireable | `.github/workflows/` | `promtool test rules` green |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Effective-state RLS lint | P2 | Backend/Platform | M | verify-rls.mjs |
| Behavioral RLS matrix in CI | P2 | Backend/Platform | M | local Supabase |
| Enabled-module manifest + scoped-call-site check | P3 | API platform | S | RLS secrets access |
| Convert remaining tenant services/CRUD to scoped client | P3 | API platform | M | policy coverage per module |
| Storage path binding to documents row | P3 | Backend | S–M | upload flow |
| DB_FUNCTIONS.md + CI check | P3 | Platform | S | — |
| RPC signatures in generated types | P3 | Platform | M | generate-db-types.js |

## Suggested Tests

- **Behavioral RLS matrix (highest value):** after `supabase db reset`, assert allow/deny for {anon, approved member org A, pending member org A, approved member org B, platform admin, service_role} × {SELECT, INSERT, UPDATE, DELETE} on `document_versions`, `store_quotes`, `webhook_dead_letters`, `public_interactions`, `client_portal_entitlements`, `phishing_targets`, `mfa_recovery_codes`.
- **Regression for the new findings:** pending-member `UPDATE document_versions` → denied; authenticated `INSERT store_quotes(organization_id = foreign)` → denied; `DELETE webhook_dead_letters` as org admin with `webhook-management` write-enabled → succeeds.
- **RPC abuse:** `approve_project_task`/`add_project_task_comment` with a foreign `p_user_id` → exception (already fixed; pin it).
- **Static lints:** effective-state raw predicate scan; role-gate superset check; policy↔catalog pair check; DISABLE-RLS count == 0.
- **CI:** `promtool check rules` + `promtool test rules`; `node scripts/verify-rls.mjs` (already wired).
- **Manual:** platform-admin org-switcher access still works and is written to `impersonation_log`; RLS counters visible on `/metrics` (token-gated).

## Suggested Documentation Updates

- `AGENTS.md:97` / `review.md:103`: correct the webhook dead-letter delete-client claim (it is the scoped client, conditional on `RLS_WRITES_ENABLED`).
- `docs/RLS-rollout.md`: add the enabled-module manifest (module keys actually set), the auth-module caveat, and the service-helper bypass list.
- `docs/RLS-coverage-matrix.md`: refresh counts from `verify-rls.mjs` and record the snapshot commit; note the `dv_update` fix.
- `docs/MT-P0-001-RLS-remediation-design.md`: mark as historical (call sites changed from 833 to 238 admin / 383 scoped).
- New `docs/DB_FUNCTIONS.md`: SECURITY DEFINER inventory + authz contract.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which modules are actually in `RLS_READS_ENABLED` / `RLS_WRITES_ENABLED` today? | Determines whether findings 2/14/15 are live or latent | GitHub repo/env secret values (operator read) |
| Is `webhook-management` in `RLS_WRITES_ENABLED`? | Turns RLS-P2-002 from latent to active breakage | Secret value |
| Is the docs' "~44 read / ~17 write modules" accurate? | Code has 43 module keys; claim not reproducible | Secret value |
| Are the Prometheus RLS rules loaded and delivered in prod? | IR-P1-006 residual | Prometheus/Alertmanager runtime config + last firing |
| Do any other pre-baseline live policies carry raw predicates missed by replay heuristics (dynamic SQL)? | dv_update may not be the only one | A real effective-state scanner over a reset DB (`pg_policies`) |

## Appendix

### A. Replicated scan outputs (verbatim, node unavailable)

```
RLS/migration hygiene: tables=137, rls-enabled=137, policies=1021, failures=0, warnings=1
  WARN [no-policy] mfa_recovery_codes has RLS enabled (5302427:28) but no create policy targets it
```
The single warning is a false positive of the Python replication: `5302427:28` carries the `-- rls: deny-all` marker that `verify-rls.mjs` honours.

```
check-rls-predicate replication: checked 6 migration(s) newer than 5302430; violations: 0
```

```
effective live policies: 516 (select 144, insert 128, update 116, delete 104, all 24)
live raw org-in-memberships predicates: 9 -> 8 cab_* (dropped dynamically by 5302412) + document_versions.dv_update (real)
live policies with catalog-absent permission pairs: 12 occurrences / 7 distinct policies
live policies with admin/super_admin-only r.key gate: 1 (notifications_insert_system_or_admin, by design)
```

```
SECURITY DEFINER effective definitions: 18; without pinned search_path: 0
```

### B. Migration patch suggestions

1. `5302437_fix_document_versions_update_predicate.sql`: `drop policy if exists dv_update on public.document_versions; create policy dv_update ... for update using (public.is_org_member((select organization_id from public.documents d where d.id = document_id)) and public.user_has_permission(...,'documents','edit'))`.
2. `5302438_store_quotes_public_insert_scope.sql`: drop/recreate the public insert policy with `with check (organization_id is null)`; keep `service_role_all_quotes`.
3. `5302439_webhook_dead_letters_delete_policy.sql`: add `for delete using (exists (select 1 from webhook_endpoints we where we.id = webhook_id and (is_super_admin() or user_has_permission(we.organization_id,'webhooks','manage'))))`.
4. (Optional) catalog completion migration for contracts/appointments/projects manage + documents upload, or rewrite those policies to create/edit/delete.
