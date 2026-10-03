# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Removes the deploy-time "Management SQL" steps from the production and development
deploy workflows. Previously, every push to `main`/`develop` executed raw SQL against
the hosted Supabase project that (a) dropped the least-privilege
`users_select_own` policy and replaced it with `users_select ... USING (true)`,
(b) rewrote `workspace_members` RLS, (c) patched `auth.users` tokens/identities and
set a shared hardcoded bcrypt password on `%@seed.test` accounts, and (d) ran the
`supabase/seeds/01..05` files. This makes CI a second, unversioned schema/data channel
and an automatic RLS bypass. After this change, schema and policies are managed only by
the migration path, and production is no longer seeded by deploy.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-01`  -  Remove production RLS weakening
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P0-001` | P0 | open -> partially-fixed | `users_select USING (true)` + `workspace_members` DDL removed from both workflows; least-privilege `users_select_own` remains migration-defined. |
| `CI-P1-002` | P1 | open -> partially-fixed | Both `database/query` Management API steps removed; deploy pipeline now performs no DDL/DML. |
| `DATA-P1-001` | P1 | open -> partially-fixed | Seed-user insert/password UPDATE and seed-file execution removed from both workflows. Existing production seed rows still require a separate cleanup/rotation. |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/deploy-production.yml` | Deleted the `Seed auth users via Management SQL` and `Seed data tables via Management API` steps (RLS DDL, auth token/identity/password UPDATEs, seed execution). |
| `.github/workflows/deploy-development.yml` | Deleted the same two Management SQL steps (equivalent dev mutation). |

Deletion-only diff: 273 deletions, 0 insertions.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `rg "USING \(true\)\|database/query" .github/workflows/deploy-production.yml` | local (rg.exe) | 1 (no matches) | `remediation/PATCH-01/verify.log` |
| `rg -n "Seed auth users\|USING \(true\)\|database/query\|users_select\|workspace_members_select\|encrypted_password\|seed\.test\|auth\.identities\|auth\.users" deploy-production.yml deploy-development.yml` | local (rg.exe) | 1 (no matches) | `remediation/PATCH-01/verify.log` |
| `git diff --name-only` | local | 0 | only 2 in-scope files |
| `rg -n users_select_own supabase/migrations/20260626000022_apply_rls_policies.sql` | local (rg.exe) | 0 | least-privilege policy still defined |
| YAML parse of both workflows (`python` + PyYAML) | local | 0 | OK for both files |
| `git diff --numstat` | local | 0 | `0 138`, `0 135`  -  deletion only |

- Secret scan (gitleaks): **not run**  -  gitleaks is not installed / on PATH in this environment. Manual gate: diff is deletion-only (`git diff --unified=0` added-lines = 0), so no secret can be introduced by this change.
- Scope check (files within patch set): **pass**  -  only `deploy-production.yml` and `deploy-development.yml`.
- `supabase db reset` / RLS assertion: **not run**  -  `supabase` CLI is not installed/on PATH in this environment.

## Evidence bundle

- `remediation/PATCH-01/diff.patch`  -  SHA-256 `A5A79B200636E50A944BD6553D5545C46265D3958FEF5A8958330E2B79467EFF`
- `remediation/PATCH-01/manifest.json`
- `remediation/PATCH-01/verify.log`

## Risk and rollback

- Risk: low. Deploy no longer seeds demo/test data, so a fresh production/dev database
  will not contain sample workspaces/messages until an explicit, guarded seed workflow
  is used. RLS is strictly tightened (no `USING (true)`).
- Rollback: `git revert 1b9b0ca096b9493936e7d7c74600e330082542f8`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- `rg "USING \(true\)|database/query" .github/workflows/deploy-production.yml` returns nothing.
- `supabase db reset` yields `users_select_own` (not run here  -  no local Supabase).
- Deploy pipeline performs no DDL/DML to auth or schema.

## Follow-ups (not in this patch set)

- Delete existing production `%@seed.test` accounts and rotate/remove the shared password.
- Add a guarded, opt-in seed workflow that cannot target production.
- Apply a migration if `workspace_members` policy changes are still desired.
