<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Fixes `DATA-P2-005` in the `chat` API/repo. The GDPR account-erasure RPC `public.gdpr_delete_user` was
**non-functional**: its `SET search_path = 'public, auth'` used the quoted form, which PostgreSQL
interprets as a *single schema literally named* `public, auth`. `current_schemas()` was therefore empty,
every unqualified `DELETE FROM dm_members …` failed with `relation "dm_members" does not exist`, the
function always returned `{"success": false}`, and the API returned 500 — so the right to erasure was
never actually honoured.

The fix uses the unquoted list form (`SET search_path = public, auth`), and makes the erasure a **single
atomic transaction** by deleting `auth.users` inside the same function instead of relying on a separate
`supabase.auth.admin.deleteUser` call after the RPC succeeded. The API route is simplified to the one RPC
call, and covered by tests. Because every statement is a plain `DELETE`, the operation is idempotent and
retryable: a failure rolls the whole transaction back and reports `success=false`.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U04` — Unassigned DATA findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (`develop`)
- Branch: `remediation/ps-u04-20261003-0018-develop-a72b8cc`
- Commit: `937b43983fd3efc836f19af8407e4f06e8fcfbc2`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P2-005` | P2 | open -> partially-fixed | Erasure now works, covers every user-referencing table, and runs as one idempotent transaction. Status becomes `verified-fixed` after merge / green CI. |

The audit's stated failure mode ("`admin.deleteUser` fails after the SQL succeeds, leaving a partial
deletion") is closed by removing the second step entirely: `auth.users` is now deleted in the same
transaction as the public rows. Idempotency and retained-vs-deleted semantics are documented in the
migration header.

## Changes

| File | What changed |
|---|---|
| `supabase/migrations/20260725000001_make_gdpr_delete_atomic.sql` | New migration. `CREATE OR REPLACE FUNCTION public.gdpr_delete_user` with the corrected `search_path`, full public-table coverage, auth token/identity cleanup and `DELETE FROM auth.users` in one transaction; header documents deleted vs retained/anonymised rows. |
| `supabase/rollback/20260725000001_make_gdpr_delete_atomic_down.sql` | Matching down script restoring the previous function (required by the migration-rollback CI check). |
| `supabase/migrations/migrations.list` | Register the new migration in the manifest. |
| `apps/api/src/modules/auth/routes.ts` | `DELETE /account` now performs the erasure with the single atomic RPC and drops the separate `auth.admin.deleteUser` step. |
| `apps/api/src/modules/auth/__tests__/gdpr-delete.test.ts` | New tests: one RPC, 204 on success, `auth.admin.deleteUser` never called; `success=false` surfaces an error (retryable). |

Scope: the migration + its rollback/manifest and the single API route it guards, plus tests. No other
application code, dependency or config changes.

## Verification Performed

Runner: `ci-runner` (LXC 200, `172.23.128.51`), clean sync of `/srv/work/chat` at commit `937b439`.
Full raw log: `remediation/PS-U04/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | ci-runner (node 20.20.2, pnpm 9.15.4) | 0 | install ok — `verify.log` §2 |
| `corepack pnpm --filter @chat/api test` | ci-runner | 0 | **63 files / 487 tests passed**, incl. `gdpr-delete.test.ts (2 tests)` — `verify.log` §2 |
| `supabase db reset` (applies all migrations on real Postgres) | ci-runner (supabase 2.119.0) | 0 | `Applying migration 20260725000001_make_gdpr_delete_atomic.sql…` / `Finished supabase db reset` — `verify.log` §3 |
| Functional erasure on the seeded DB (`gdpr_delete_user(seeded user)`, assert zero rows in every user-referencing table incl. `auth.*`) | ci-runner (psql in `supabase_db_chat`) | 0 | call 1 `{"success": true}`; **no remaining rows** across 32 public tables + `dm_channels`/`public.users` + `auth.users/identities/sessions/mfa_factors/refresh_tokens`; call 2 `{"success": true}` (idempotent) → `GDPR_DELETE_OK` — `verify.log` §4 |
| `gitleaks stdin --redact --exit-code 1 < diff.patch` | ci-runner (gitleaks 8.30.1) | 0 | `no leaks found` (16.40 KB scanned) — `verify.log` §5 |

- **Before/after proof for the root cause**: at base the function returned
  `{"error": "relation \"dm_members\" does not exist", "success": false}` and deleted nothing; at this
  commit it returns `{"success": true}` and leaves zero rows.
- **Secret scan (gitleaks)**: pass on the diff.
- **Scope check**: 5 changed files, all within the patch set (migration, rollback, manifest, the route
  it guards, and tests). Pass.

## Evidence bundle

- `remediation/PS-U04/diff.patch` — SHA-256 `389EBA5657209B1FD3B949AB7ABDF95B0FFDDFD76C72C3CB4C4A37880F28AC90`
- `remediation/PS-U04/verify.log` — SHA-256 `BFAF6442A9046DB3D9EC838B0B885286BE4885E624A8624F75D94B03F6501332`
- `remediation/PS-U04/manifest.json`

## Risk and rollback

- Risk: **medium**. The change repairs a privacy-critical path that previously did nothing. Two design
  notes for the reviewer: (1) `auth.users` is now deleted by the SQL function rather than through
  GoTrue's admin API — this repo already deletes `auth.users` directly in `supabase/seeds` and already
  deleted `auth.sessions`/`identities`/`mfa_factors`/`refresh_tokens` from SQL, so it is consistent;
  (2) the API no longer calls `admin.deleteUser`, so any GoTrue-side hooks on that endpoint would not
  run. The in-repo trigger `handle_user_deletion` still fires on the `auth.users` delete.
- Rollback: `git revert 937b43983fd3efc836f19af8407e4f06e8fcfbc2`. The migration's down script restores
  the previous function verbatim (and therefore the prior behaviour, including the `search_path` defect).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/rollback/manifest)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Tests added for the fix
- [ ] Reviewer accepts deleting `auth.users` from SQL instead of `auth.admin.deleteUser`
- [ ] Rollback is practical

## Definition of done (for this set)

- `gdpr_delete_user` actually erases the account (public rows + auth user) and returns `success: true`.
- The erasure is a single atomic transaction: on error nothing is deleted and the request is retryable.
- What is deleted vs retained/anonymised is documented in the migration.
- API route tests cover the single-RPC behaviour.

## Open questions

1. **Deleting `auth.users` from SQL vs GoTrue admin API.** The fix makes the erasure atomic by removing
   the second call. If the project relies on GoTrue admin delete hooks/callbacks (none are visible in this
   repo), a reviewer may prefer keeping `admin.deleteUser` and instead accepting the two-step risk. The
   SQL path is consistent with existing repo practice (`seeds/00_comprehensive_users.sql` deletes
   `auth.users`; migration 20260724000006 already deleted auth token/identity rows directly).
2. **Content anonymisation vs hard delete.** The finding also mentions "nor anonymizes content". This PR
   completes and documents hard erasure; whether shared-thread content should instead be anonymised is a
   privacy/product decision left to the owner.
