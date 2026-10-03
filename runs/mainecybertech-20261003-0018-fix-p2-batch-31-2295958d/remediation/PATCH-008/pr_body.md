# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PATCH-008` — demo data seed-only, covering `FEAT-P2-002` (P2).

The audit ran against a stale local clone (`2295958d`). The finding **still
reproduces** at the current base, `origin/fix/p2-batch-31 @ 11746adc`: the demo
dataset is shipped inside the versioned migration path (`supabase db push`) and
was guarded only by a domain heuristic:

```sql
if exists (select 1 from public.organizations
           where primary_domain is not null
             and primary_domain not like '%.example'
             and primary_domain not like '%.local') then
  ... skip demo data ...
end if;
```

On a brand-new database no organization exists, so the condition is **false**
and the block runs: a fresh production project receives demo tenants and
`password: 1` accounts before any real tenant exists.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d` (finding at `fix/p2-batch-31 @ 2295958d`)
- Patch set: `PATCH-008` — Demo data seed-only
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)
- Commit: `624c02e1b2cebdf890f3d69a2bfdd580ced4f111`

> Base note: the audit was taken on a stale clone (`2295958d`); `origin/fix/p2-batch-31`
> is now `11746adc`. The demo migrations and their heuristic guard are unchanged
> between the audited commit and the base (reproduced in `verify.log`).

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P2-002` | P2 | open -> addressed (pending review) | All demo-seeding blocks are now opt-in and default OFF. A fresh production database gets **zero** demo orgs/users/rows. |

## Changes

Every demo-seeding block now uses an explicit opt-in setting that defaults off:

```sql
if coalesce(current_setting('app.seed_demo', true), '') <> 'true' then
  raise notice '<migration>: app.seed_demo is not ''true'' - skipping ...';
  return;
end if;
```

| File | What changed |
|---|---|
| `supabase/migrations/5302119_demo_test_data.sql` | Domain heuristic -> `app.seed_demo` opt-in (defaults off); header updated. |
| `supabase/migrations/5302120_demo_module_data.sql` | Same. |
| `supabase/migrations/5302121_demo_permission_edge_cases.sql` | Same. |
| `supabase/migrations/5302123_demo_expanded_test_data.sql` | Same. |
| `supabase/migrations/5302126_demo_worker_admin_coverage.sql` | Same. |
| `supabase/migrations/5302128_role_catalog_expansion.sql` | Same for its guarded demo-user block (the roles/permission assignments stay unguarded — they are real config). Kept consistent so the chain does not try to insert demo users into orgs that were skipped. |
| `supabase/migrations/5302406_device_profiles.sql` | Its Device-Profile-Library demo insert was **unguarded** and referenced the five demo org ids; wrapped it in the same opt-in guard so an empty database does not fail the migration on a missing FK. |

Local/E2E demo data is unaffected: `supabase db reset` runs
`supabase/seeds/00..08` after migrations (`supabase/config.toml [db.seed]`),
which remain the local source of demo data. To populate a disposable hosted dev
database deliberately:

```sql
alter database postgres set app.seed_demo = 'true';
```

### Scope note (why two files outside `5302119…5302126_demo*.sql`)

`5302128` and `5302406` move demo data through the same migration path and
depend on the demo orgs created by `5302119`. Gating only the demo files would
make a fresh-database migration run fail (FK violation) instead of cleanly
skipping. They are included to keep the fix correct on an empty database, not as
drive-by refactors.

## Verification Performed

All commands ran on the Proxmox `ci-runner` (172.23.128.51) against the fix;
raw output and exit codes are in `remediation/PATCH-008/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | Proxmox ci-runner | 0 | lockfile up to date; `Done in 4.7s` |
| `node scripts/generate-db-types.js --check` | Proxmox ci-runner | 0 | `Processing 134 migration files... database types up to date` |
| `corepack pnpm --filter api test` | Proxmox ci-runner | 0 | `Test Suites: 122 passed, 122 total`; `Tests: 1406 passed, 1406 total` |
| Guard expression on real PostgreSQL 17 (`guard-db-check.sh`) | Proxmox ci-runner (docker) | 0 | unset -> `t` (skip), `'true'` -> `f` (run), `'false'` -> `t` (skip) |
| Static guard coverage (`git grep`) | host | 0 | all 7 demo-seeding files gate on `app.seed_demo`; no `production-like organization domains` guard remains |
| `gitleaks detect --no-git --redact` (diff additions only) | Proxmox ci-runner (gitleaks 8.30.1) | 0 | `no leaks found` |

- Secret gate: the addition-only diff is gitleaks-clean. Scanning whole changed
  files also reports two **pre-existing** `generic-api-key` false positives in
  `5302128` (module-key string literals `m365-hardening` / `patch-compliance`, in
  unchanged hunks); they are not introduced by this diff.
- `scripts/scan-secrets.sh` (the repo's pre-commit gate) was run on the working
  tree: exit 0.
- Not run: full `supabase db reset` / migrate-an-empty-DB assertion (standing up
  the full Supabase local stack is outside the set's mandated verification and
  would re-run the seeds, which are the intended local demo source). The guard
  was verified against a real PostgreSQL engine instead (row above).

## Evidence bundle

- `remediation/PATCH-008/diff.patch` — SHA-256 `f3bb76d2bd7083020e7ef5f12b46d41dd6795a1a83732e01446c33b168d516ac`
- `remediation/PATCH-008/manifest.json`
- `remediation/PATCH-008/verify.log`
- `remediation/PATCH-008/api-test.raw.log`
- `remediation/PATCH-008/guard-db-check.sh` (the guard logic exercised in the lab)

## Risk and rollback

- Risk: **low.** No application/runtime code changes; migration SQL only.
- Behaviour change: hosted dev databases no longer receive demo data via
  migrations unless `app.seed_demo = 'true'` is set. Production is now safe by
  default. Local/E2E still get demo data from seeds.
- Rollback: `git revert 624c02e1` (release the demo blocks back to the previous
  heuristic), or drop the branch.

## Open questions / follow-ups (out of scope)

- Setting `app.seed_demo` on a Supabase-hosted dev project is an operator action
  (`alter database postgres set app.seed_demo = 'true';`). If maintainers prefer
  a dashboard/env-driven flag, that is a follow-up.
- The finding also suggested a CI assertion that a fresh migration run yields
  zero demo orgs. That needs a Postgres service in CI and is deferred (noted in
  `verify.log`).
- `5302406`'s demo insert would already have failed on any database that has a
  real org but not the demo orgs; the guard now makes it consistent.

## Review checklist

- [x] Diff touches only migration SQL required for the fix (7 files; two are the
      demo-dependent migrations the fix must keep consistent — rationale above)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran in the lab; results pasted, not asserted
- [x] No secrets added; gitleaks clean on the diff
- [x] Fail-closed by default demonstrated (unset flag -> skip)
- [x] Rollback is practical

## Definition of done (for this set)

A fresh (empty) production database applies all migrations with **zero demo
orgs, users, or rows**, because every demo-seeding block is skipped unless
`app.seed_demo = 'true'` is explicitly set.
