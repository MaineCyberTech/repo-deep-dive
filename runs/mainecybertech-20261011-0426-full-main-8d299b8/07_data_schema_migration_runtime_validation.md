# 07_data_schema_migration_runtime_validation — Prompt 07 - Data, Schema, Migration, and Runtime Validation Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `07_data_schema_migration_runtime_validation.md` (area DATA, prompt)

## Verification Performed

# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech`
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11
- Auditor: repo-deep-dive subagent (base profile), domain 07
- Area code: DATA
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/07_data_schema_migration_runtime_validation.md`
- Scope limitations: static review only; no database connection, no Supabase CLI and no `node` in the audit environment, so repo guards were reimplemented/read rather than executed. Live row counts, lock timings and hosted-project state are unknown.

## Scope

Reviewed: `supabase/migrations/` (134 files), `supabase/seeds/`, `supabase/config.toml`, migration CI (`.github/workflows/supabase-migrations.yml`, `db-backup.yml`, `db-restore-test.yml`), migration tooling (`scripts/verify-rls.mjs`, `scripts/check-rls-predicate.mjs`, `scripts/generate-db-types.js`, `tools/migration_chain_check.sh`), DB-facing worker tasks (`retention.ts`, `orphan-cleanup.ts`, `public-interaction-retention.ts`), generated DB types, DB-facing API routes (org delete, generic crudRoute factories, optimistic locking, validators) and the rollback/backup docs.

Not reviewed in depth: live RLS behaviour against a running Postgres, migration lock timings on production-sized tables, the OpenAPI contract surface (domain 08), infra/DR runbooks in full (domains 12/13), and operator-side configuration that is not in the repository.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `supabase/migrations/` (134 files) | SQL | Schema + migration safety | Version gaps: `5302026→5302028`, `5302038→5302041`, `5302043→5302050`, `5302083→5302085`, `5302135→5302402`, `5302428→5302430` |
| `supabase/migrations/5302055/5302406/5302407` | SQL | Destructive replacements | `drop table ... cascade` with no begin/commit |
| `supabase/migrations/5302108` | SQL | Audit cascade | `audit_logs.organization_id` `on delete cascade` |
| `supabase/migrations/5302432`, `5302434`, `5302435`, `5302436` | SQL | Latest fixes | Soft-delete removal, anon least privilege, RPC caller identity, admin-gate restore |
| `scripts/verify-rls.mjs`, `scripts/check-rls-predicate.mjs` | JS | RLS + predicate gates | Baselines `5302427` / `5302430`; wired via `.github/actions/unit-tests/action.yml:51,59` |
| `.github/workflows/supabase-migrations.yml` | CI | Apply + drift | Dry-run artifact; post-push `db diff` fails on DDL |
| `.github/workflows/db-backup.yml`, `db-restore-test.yml`, `storage-backup.yml` | CI | Backup/restore | All `environment: dev`; restore test asserts floors + freshness |
| `apps/worker/src/tasks/retention.ts`, `orphan-cleanup.ts`, `public-interaction-retention.ts` | TS | Destructive helpers | Batching, recursion, PII purge |
| `apps/api/src/routes/{organizations,assets,security-ops,governance,field-services,batch,security-suite,device-profiles,network-diagrams}.ts` | TS | DB-facing writes | Org delete, crudRoute PATCH, version preconditions, updated_at |
| `packages/sdk/src/database.types.ts`, `scripts/generate-db-types.js` | Generated TS / JS | Type drift gate | Types current; no commit binding |
| `docs/migrations/naming-guide.md`, `docs/ROLLBACK_PROCEDURES.md`, `docs/RTO_RPO.md` | Docs | Standards + recovery claims | BEGIN/COMMIT + rollback-comment standard; prod/dev backup mismatch |

## Verification Performed

Commands run (read-only) and observed results:

| Command | Observed result |
|---|---|
| `git log --oneline -3` / `git rev-parse 8d299b8d` | Target confirmed at `8d299b8d`; `9c0b88c` is its ancestor; `supabase/` unchanged between the two commits |
| `grep -c "begin;"` + per-file loop over `supabase/migrations/*.sql` | 47 files contain `begin;`; destructive files `5302055`, `5302406`, `5302407` do not |
| Python scan: `drop table` / `drop column` / `delete from` per file | `5302055` (9 drops), `5302406` (1), `5302407` (1), `5302432` (6 drop-column, wrapped) |
| Python scan: unpaired `create policy` per file | 61 pre-baseline files unpaired; 0 files newer than `5302427` unpaired |
| Python scan: `alter table ... enable row level security` vs created tables | 134/134 live tables enable RLS; only `mfa_recovery_codes` has no policy and it is marked `-- rls: deny-all` |
| Python reimplementation of `check-rls-predicate.mjs` over migrations > `5302430` | 0 violations; live raw predicate remains only in `notifications_insert_system_or_admin` (5302057) |
| Python scan: `create trigger` across migrations | 17 triggers total (bootstrap core + `webhook_endpoints`); 69 tables have `updated_at` with no trigger |
| Python scan: `organization_id uuid ... references organizations(id) on delete ...` | 95 cascade, 2 set-null (`audit_logs`, `impersonation_log`), 1 no-action (`profiles.default_organization_id`, seeds-only writes) |
| Python scan: `.update(` / `.delete()` chains without filters in `apps/api|worker/src` | none on the DB (matches were crypto `.update()` calls) |
| `grep -rn "deleted_at|deleted_by"` across apps/packages/supabase | no live references; `5302432` drop is effective |
| `grep -rn "archive" apps/api/src apps/worker/src` | no audit archive sink |
| `grep -rn "publicInteractionRetention" apps/worker/src/__tests__` | no hits — PII purge untested |
| `grep "environment:" .github/workflows/*.yml` | backup/restore/storage-backup all `environment: dev` |
| `node scripts/*.mjs` | not run — `node` is not installed in the audit environment (recorded as `not reproducible` here) |

## Executive Summary

The data domain has improved materially since the 20261004 run. All four headline fixes are present and effective at `8d299b8d`: orphan cleanup is folder-aware, paginated, chunked and fail-closed (`orphan-cleanup.ts`, tests at `orphan-cleanup.test.ts:369-445`); the retention task is batched, bounded and honest about failures (`retention.ts:23,31,58-84,156-165`); the dead soft-delete columns were dropped in `5302432` with the product decision documented; and the blanket `anon` DML grant was replaced by an explicit allowlist in `5302434`. RLS coverage is 134/134 live tables, the only policy-less table is explicitly deny-all, and the membership-predicate guard is wired into CI and clean for every migration after `5302430`.

The remaining risks are quieter. Destructive table replacements (`5302406`, `5302407`) and the nine-table cleanup (`5302055`) are still not transaction-wrapped — and `5302110` documents the real collateral damage a cascade drop already caused. `audit_logs` still cascades on org delete and is purged after 365 days with no archive. Only three of 118 timestamped tables have a retention purge. A newly found schema/runtime gap makes `updated_at` unreliable on 69 module tables: no trigger exists, and the generic PATCH factories explicitly strip `updated_at` without setting it. The scheduled database dump (and its restore test) run against the **dev** environment while `RTO_RPO.md` advertises 30-day S3 recovery, and production long-term dump coverage cannot be evidenced from the repo. Finally, the retention tests never exercise the age boundary — the mock ignores the cutoff — so a too-greedy purge would pass CI.

Recommended next actions: (1) wrap every `drop table`/`drop column` migration in `begin;…commit;` and archive before dropping; (2) install the existing `set_updated_at()` trigger on all 69 tables (or set it in the shared crudRoute factories); (3) settle the audit retention/archive decision (cascade vs set-null + cold storage); (4) extend the retention inventory to the listed PII/audit-adjacent stores; (5) fix the retention test mock to honour `.lt(col, cutoff)` and add mixed fresh/expired fixtures; (6) prove or document production backup coverage.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Migrations | `supabase/migrations/` (134) | Schema evolution | Ordered, applied by CI | Medium | Destructive files unwrapped; gaps undocumented |
| RLS | all migrations | Tenant isolation | 134/134 enable RLS; CI-gated | Low | One residual raw predicate (`notifications` insert) |
| Predicate guard | `scripts/check-rls-predicate.mjs` | Block raw membership predicates | Baseline `5302430`; wired in CI | Low | 0 post-baseline violations |
| Soft delete | `5302109` → `5302432` | Tombstones | Removed; hard delete documented | Low | Verified fixed |
| Optimistic locking | `5302051`/`5302053`/`5302409` + middleware | Concurrent-edit safety | 11 route files; DB `.eq("version")` | Low | `notification_preferences`/`billing_customers` version columns unused |
| Audit logs | `audit_logs` + `5302108` + `retention.ts` | Compliance trail | Org cascade; 365-day purge | Medium | No archive sink |
| Retention | `retention.ts`, `public-interaction-retention.ts`, `5302117` | Purge jobs | 3 stores purged | Medium | 118 timestamped tables total; `retention_policies` not consulted |
| Orphan cleanup | `orphan-cleanup.ts` | Storage GC | Recursive/paginated/chunked | Low | Verified fixed |
| Seeds | `supabase/seeds/` (9) | Local/E2E data | All registered; demo gated by `app.seed_demo` | Low | Exercised by `supabase db reset` in e2e.yml:94 |
| Generated types | `packages/sdk/src/database.types.ts` | SDK types | Generated + CI `--check` | Low | No commit binding |
| Migration CI | `supabase-migrations.yml` | Apply + drift | Post-push diff fails on DDL | Low | Pinned CLI 2.107.0; serialized |
| Backup/restore | `db-backup.yml`, `db-restore-test.yml` | Recovery | Assertive restore test | Medium | Targets `environment: dev` only |
| updated_at | 69 module tables | Audit field | Frozen at insert | Medium | New finding this run |
## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database schema | 4 | 134 migrations, generated types, deny-all marker | Free-text status columns unconstrained | Add CHECK/enum constraints |
| Migrations | 3 | CI apply + post-push drift gate | Destructive files unwrapped; no rollback notes | Wrap + document rollback |
| Constraints | 3 | 6 bounded numerics + 9 version checks | 88 status-like columns unconstrained | Constrain status vocabularies |
| Indexes | 4 | FK-index backfills `5302056/5302419` | Duplicate index names silently no-op (e.g. `idx_audit_logs_entity`) | De-duplicate names |
| Foreign keys/cascades | 3 | 96 org cascades (incl. audit_logs); 1 set-null | Org delete destroys audit history | SET NULL or archive |
| RLS | 4 | 134/134 enabled; two CI gates | Residual `notifications` insert predicate | Rewrite with `user_has_role` |
| Tenant columns | 4 | `organization_id` on tenant tables; platform-only tables documented | Child tables scoped via parent (by design) | Keep inventory |
| Soft deletes | 4 | Hard delete decided + documented | — | Keep docs aligned |
| Audit fields | 2 | `set_updated_at()` exists | 69 tables never update `updated_at` | Install trigger |
| Retention | 2 | 3 purges; `retention_policies` table | Most stores unpurged; thresholds hardcoded | Inventory + wire policies |
| Seeds/fixtures | 4 | 9/9 registered; demo opt-in | Schema drift only caught at reset | Keep E2E reset gate |
| Generated DB types | 4 | `--check` gate; drop-column aware | No commit/version binding | Embed digest |

## Detailed Review

### Item: Migration safety (destructive DDL)

- Evidence: `5302406:3-7`, `5302407:8-15`, `5302055:4-12`, `docs/migrations/naming-guide.md:168`, `tools/migration_chain_check.sh:102`, `5302110:1-10`.
- What it does: replaces `device_profiles`/`network_diagrams` with `drop table ... cascade; create table` and drops nine "dead" tables; each file is a sequence of autocommitted statements when applied by `psql -f`.
- Missing controls: no `begin;/commit;`, no data archive, no static check that fails destructive DDL outside a transaction; the comments claim the files are "safe to re-run" although re-running drops live rows.
- Risks: partial-apply data loss; cascade collateral (already materialised once in `5302110`).
- Recommended improvement: wrap + archive + add a lint rule; correct the comments.

### Item: Audit-log lifecycle

- Evidence: `5302108:2-7` (cascade), `retention.ts:9-12,129-132` (365-day purge), `organizations.ts:397-419` (hard org delete), no archive code.
- What it does: destroys audit rows on org teardown and after one year.
- Missing controls: cold-storage archive or `on delete set null`; no operator-facing archive runbook.
- Risks: compliance evidence loss during offboarding and for aged incidents.

### Item: Retention framework

- Evidence: `retention.ts`, `public-interaction-retention.ts`, `5302117`, `5302071:54-75`.
- What it does: purges `audit_logs` (365d), `notifications` (90d) and `public_interactions` (90d, scheduled in `main.ts:71-79`).
- Missing controls: no purge for `impersonation_log`, `satisfaction_pulses`, `webhook_deliveries`, `webhook_dead_letters`, `document_shares`, `business_os_snapshots`; thresholds hardcoded rather than read from `retention_policies`.
- Risks: unbounded PII/audit-adjacent growth with no disposal owner.

### Item: updated_at audit field

- Evidence: 17 `create trigger` statements; 69 tables with `updated_at` and no trigger; `security-ops.ts:29-37,106-122`; `assets.ts:231,281-288`.
- What it does: new tables default `updated_at` to `now()` at insert; generic PATCH factories block client-supplied `updated_at` and never set it.
- Risks: stale modification timestamps for sorting, sync, cache invalidation and audit queries.

### Item: DB-facing runtime writes

- Evidence: 11 route files with `requireIfMatch`; 16 `.eq("version")` preconditions; no unfiltered `.update()`/`.delete()`; `parsePartialUpdate` mass-assignment guard (`lib/validators.ts:14-21`).
- Strengths: optimistic locking is enforced at the DB with version preconditions; mass assignment is closed for generic factories.
- Gaps: `notification_preferences`/`billing_customers` version columns are never used; status vocabularies not enforced at the DB.

### Item: Backup / rollback / drift

- Evidence: `supabase-migrations.yml:90-125` (drift fails), `db-restore-test.yml:135-210` (floors + freshness + RLS canary), `db-backup.yml:12-14` (dev), `RTO_RPO.md:10,18,24`.
- Strengths: drift gate, dry-run artifact, assertive restore test, encrypted/offsite-capable dump script.
- Gap: the scheduled dump and freshness assertion exercise the dev database; production long-term dump coverage is unproven in-repo.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DATA-001 | Database schema | migrations + types | Generated types + CI check | Unconstrained status strings | P3 | Add CHECK/enums |
| DATA-002 | Migrations | 134 files | CI apply, drift gate | Unwrapped destructive DDL | P2 | begin/commit + archive |
| DATA-003 | Constraints | 15 named CHECKs | version>=1, bounded numerics | 88 status-like free text | P3 | Constrain vocabularies |
| DATA-004 | Indexes | `5302056/5302419` | FK index backfill | Duplicate names no-op | P3 | Rename/dedupe |
| DATA-005 | Foreign keys/cascades | 95 org cascades | Cascade deletes | audit_logs history loss | P2 | SET NULL/archive |
| DATA-006 | RLS | 134/134 enabled | verify-rls + predicate guard | notifications insert residual | P1/P3 | Rewrite with helper |
| DATA-007 | Tenant columns | org FKs | org-scoped policies | child tables via parent | — | Keep inventory |
| DATA-008 | Soft deletes | 5302432 | Hard delete documented | — | — | Keep docs |
| DATA-009 | Audit fields | triggers | Core tables only | 69 frozen updated_at | P2 | Install trigger |
| DATA-010 | Retention | 3 purges | Bounded batch purge | Most stores unpurged | P2 | Inventory + framework |
| DATA-011 | Seeds/fixtures | 9/9 registered | demo opt-in gate | reset-only validation | — | Keep |
| DATA-012 | Generated DB types | `--check` gate | Byte-exact check | No commit binding | P3 | Embed digest |
| DATA-013 | Migration CI | supabase-migrations.yml | Post-push drift fails | — | — | Keep |
| DATA-014 | Rollback/drift/backup | docs + workflows | Restore test asserts | prod dump unproven | P2 | Prod-scoped backup |
| DATA-015 | Destructive helpers boundary | retention tests | Batch/count tests | cutoff ignored by mock | P3 | Mixed fixtures |

## Findings

Full finding blocks (severity, evidence, impact, fix, status) are in the companion JSON (`07_data_schema_migration_runtime_validation.json`). Titles and verification outcomes:

1. **DATA-P0-001 — Orphan cleanup can recursively delete a bucket's contents** — `verified-fixed` (folder-aware recursion + unsafe-path abort + tests).
2. **DATA-P1-001 — Approved-membership RLS predicate reintroduced six times** — `partially-fixed` (guard present, 0 post-baseline violations; residual raw `notifications_insert_system_or_admin`).
3. **DATA-P1-002 — `retention` task unbounded deletes / false success** — `verified-fixed` (batched, bounded, honest errors, tests).
4. **DATA-P1-003 — Soft-delete columns dead schema** — `verified-fixed` (columns dropped in `5302432`, no refs, hard delete documented).
5. **DATA-P2-001 — Blanket `anon` DML grant** — `verified-fixed` (`5302434` revokes defaults + allowlist).
6. **DATA-P2-002 — Destructive table replacements not transaction-wrapped** — `still-open` (`5302055`, `5302406`, `5302407`; psql autocommit; prior cascade incident).
7. **DATA-P2-003 — orphan-cleanup truncated listing** — `verified-fixed` (pagination + MAX_LISTED abort).
8. **DATA-P2-004 — Migration CI dry-run non-blocking** — `verified-fixed` (post-push drift gate fails on DDL).
9. **DATA-P2-005 — `audit_logs` cascade + purge with no archive** — `still-open`.
10. **DATA-P2-006 — Several stores lack a retention policy and owner** — `still-open` (118 timestamped tables, 3 purges; `retention_policies` unused by worker).
11. **DATA-P2-007 — Generated DB types can drift** — `verified-fixed` (`--check` gate; drop-column aware; types current).
12. **DATA-P2-008 — Orphan cleanup reference query unbounded** — `verified-fixed` (200-key chunks, fail-closed).
13. **DATA-P3-001 — Pre-baseline policies without `drop policy if exists`** — `still-open` (informational; 61 files, baseline `5302427`).
14. **DATA-P3-002 — Migration version gaps undocumented** — `partially-fixed` (count 134 = tree and CI-guarded; gaps still undocumented).
15. **`updated_at` frozen on 69 module tables** — `open` (new; no trigger + generic PATCH strips it).
16. **Scheduled DB dump/restore test target dev only; prod long-term backup unproven** — `open` (new; docs claim 30-day S3 recovery).
17. **Retention purge boundary untested; PII purge untested** — `open` (new; mock ignores cutoff).
18. **Status-like text columns unconstrained by CHECK/enum** — `open` (new).
19. **No down-migrations / destructive migrations lack rollback notes** — `open` (new).
20. **Generated DB types carry no commit binding** — `open` (new).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Partial-apply data loss on destructive migration failure | P2 | Low | Lost module data + broken schema | `5302406:5`, `5302407:13`, `5302055:4-12`, chain-check psql | begin/commit + archive |
| Audit evidence erased on org delete / after 365 days | P2 | Medium | Compliance exposure | `5302108`, `retention.ts:131`, `organizations.ts:397-419` | SET NULL/archive |
| PII/audit-adjacent stores grow forever | P2 | Medium | Cost + privacy | no purge for 6 listed stores; 118 timestamped tables | Retention inventory |
| Stale `updated_at` breaks sorting/sync/audit | P2 | High | Silent data-quality errors | 69 tables, `security-ops.ts:29-37`, `assets.ts:231,281-288` | Trigger or factory |
| Prod recovery beyond PITR depends on out-of-repo backups | P2 | Medium | Data loss beyond 7 days | `db-backup.yml:12-14`, `RTO_RPO.md:18` | Prod-scoped dump |
| Residual raw predicate on notifications insert | P3 | Low | Notification injection by pending admin | `5302057:39-55` | `user_has_role` rewrite |
| Too-greedy purge undetected by tests | P3 | Low | Fresh-data deletion | `retention.test.ts:37-43` | Mixed fixtures |
| Unconstrained status values written directly | P3 | Medium | Filter/report corruption | 88 status columns, 15 checks | CHECK/enums |

## Recommendations

### Immediate / Release Blocking

None. All P0/P1 items from the previous register are fixed or have a documented residual.

### This Week

1. Wrap `5302055`, `5302406`, `5302407` (or a follow-up migration policy) in `begin;…commit;`, archive before drop, and correct the "safe to re-run" comments (DATA-P2-002).
2. Rewrite `notifications_insert_system_or_admin` with `public.user_has_role(organization_id, array['super_admin','admin'])` (DATA-P1-001 residual).
3. Decide audit retention: `on delete set null` or archive-before-delete for org teardown and the 365-day purge (DATA-P2-005).

### This Month

4. Install the existing `set_updated_at()` trigger on the 69 tables lacking one (new finding).
5. Fix the retention test mock to honour `.lt(col, cutoff)`; add mixed fresh/expired fixtures for `retention` and `public-interaction-retention` (new finding).
6. Publish a retention inventory and extend purges to the listed PII/audit-adjacent stores; wire or explicitly waive `retention_policies` (DATA-P2-006).
7. Run the dump + restore test against a prod-scoped environment or correct the RTO/RPO docs (new finding).

### Later / Platform Evolution

8. Add CHECK/enum constraints for status vocabularies (new finding).
9. Backfill drop-pairing in pre-baseline migrations or document the exemption (DATA-P3-001).
10. Add rollback blocks to destructive migrations and document the no-down-migration policy (new finding).
11. Embed a migrations digest in `database.types.ts` and assert it in `--check` (new finding).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Wrap the three destructive files | Atomic schema change | `5302055`, `5302406`, `5302407` | inject failure → rollback |
| `user_has_role` rewrite of the notifications policy | Closes the last raw predicate | new migration | predicate guard + RLS test |
| `set_updated_at` trigger loop | Fixes 69 tables at once | new migration | update row → timestamp changes |
| Mock honours the cutoff | Catches too-greedy purges | `retention.test.ts:37-43` | fresh row survives |
| Correct RTO/RPO wording (if dev-only is intentional) | Removes false assurance | `docs/RTO_RPO.md`, `docs/ROLLBACK_PROCEDURES.md` | doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Transactional + archived destructive migrations | P2 | backend/data | S–M | archive target |
| Audit archive / SET NULL decision | P2 | platform lead | M | governance decision |
| Retention inventory + framework extension | P2 | platform lead | M | product decision |
| updated_at trigger migration | P2 | backend/data | S | none |
| Prod-scoped backup/restore-test | P2 | platform/ops | S–M | prod secrets |
| Retention boundary tests | P3 | backend/data | S | none |
| Status CHECK/enums | P3 | backend/data | M | vocabulary freeze |
| Rollback notes + docs | P3 | backend/data | S | none |
| Types digest binding | P3 | backend/data | S | none |

## Suggested Tests

- Storage integration fixture: nested objects + folder entries + one true orphan; assert `remove()` receives only concrete keys and referenced files survive.
- Retention boundary: seed rows just before/after the cutoff for `audit_logs`, `notifications` and `public_interactions`; assert fresh rows are never deleted and expired rows are.
- `updated_at`: PATCH a module row (e.g. `assets`, `offboarding_checklists`) and assert `updated_at` advances.
- RLS matrix: authenticated approved member vs pending/suspended member on `notifications` insert; assert the pending member is rejected after the fix.
- Migration lint: static check failing `drop table`/`drop column` outside `begin;…commit;`.
- Restore test extension: run the same assertions against a prod-scoped backup once provisioned.

## Suggested Documentation Updates

- `docs/migrations/naming-guide.md` — add the destructive-migration policy (transaction + archive + rollback block) and record the version gaps.
- `docs/RTO_RPO.md` / `docs/ROLLBACK_PROCEDURES.md` — state exactly which environment the S3 dumps cover.
- A retention inventory doc (table → policy → owner → last exercised) covering the 118 timestamped tables.
- `docs/migrations/` — note the pre-`5302427` policy drop-pairing exemption.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does any operator-side schedule dump the production database? | Determines whether prod has long-term recovery | Hosted/prod cron or external scheduler config |
| Is `retention_policies` intended to drive the worker purge, or is it a customer-facing register only? | Data-governance design decision | Product/governance decision record |
| Are the pre-baseline unpaired `create policy` statements ever re-applied outside the ledger? | Determines DATA-P3-001 real risk | Incident/partial-apply runbook |
| Do module tables need `updated_at` semantics at all? | Some may never display it | Product/UI usage check |
| Does Supabase CLI 2.107.0 wrap each migration file in a transaction? | Reduces (not removes) DATA-P2-002 risk for `db push` | CLI docs/source; chain check uses plain psql |

## Appendix

- Table parse (static): 145 `create table` statements, 12 dropped, 134 live; 134/134 enable RLS; 1 policy-less table (`mfa_recovery_codes`, `-- rls: deny-all`).
- FK actions to `organizations` (current state): 96 cascade (95 as created + `audit_logs` after `5302108`), 1 set-null (`impersonation_log`), 1 no-action (`profiles.default_organization_id`, seeds-only writes).
- Timestamps: 118 tables with a created/captured timestamp; 3 purge targets.
- Triggers: 17 `create trigger` statements; 69 tables with `updated_at` and no trigger.
- Duplicate index names (later `IF NOT EXISTS` silently no-ops): `idx_audit_logs_entity`, `idx_notifications_user`, `idx_ticket_comments_ticket_id`, `idx_document_shares_document`, `idx_sop_library_org` (low impact; definitions are equal or superseded).
- Unused version columns: `notification_preferences`, `billing_customers` (no route reads/increments `version`).
- Command outputs are summarised in "Verification Performed"; no secret values were printed during this audit.

## Findings

| ID | Severity | Title |
|---|---|---|
| DATA-P0-001 | P0 | Orphan cleanup can recursively delete a bucket's contents |
| DATA-P1-001 | P1 | Approved-membership RLS predicate reintroduced six times; pending/suspended members could access tenant data |
| DATA-P1-002 | P1 | `retention` worker task performs unbounded deletes and reports success on partial failure |
| DATA-P1-003 | P1 | Soft-delete columns remain dead schema; DELETE endpoints hard-delete |
| DATA-P2-001 | P2 | Blanket `anon` DML grant + default privileges make every future table anon-writable unless RLS happens to stop it |
| DATA-P2-002 | P2 | Destructive table-replacement migrations are not transaction-wrapped |
| DATA-P2-003 | P2 | `orphan-cleanup` deletes storage objects based on a truncated listing |
| DATA-P2-004 | P2 | Migration CI dry-run diff is non-blocking; drift is never gated |
| DATA-P2-005 | P2 | `audit_logs` org-delete cascade destroys compliance history; 365-day purge has no archive |
| DATA-P2-006 | P2 | Several stores lack a retention policy and owner |
| DATA-P2-007 | P2 | Generated DB types / schema can drift from migration intent |
| DATA-P2-008 | P2 | Orphan cleanup reference query is unbounded in the object list |
| DATA-P3-001 | P3 | Pre-baseline policies created without a preceding `drop policy if exists` |
| DATA-P3-002 | P3 | Migration version gaps undocumented; brief states 141 migrations, tree has 127 |
| DATA-P2-009 | P2 | `updated_at` is frozen on 69 module tables (no trigger; generic PATCH drops it) |
| DATA-P2-010 | P2 | Scheduled database dump and restore test target the dev environment only; production long-term backup is unproven |
| DATA-P3-003 | P3 | Retention purge boundary behaviour is untested; the mock ignores the age cutoff and the PII purge has no tests |
| DATA-P3-004 | P3 | Status-like text columns are not constrained by CHECK/enum, so app vocabulary is not enforced by the DB |
| DATA-P3-005 | P3 | No down-migrations and destructive migrations lack rollback notes despite the repo's own naming guide |
| DATA-P3-006 | P3 | Generated DB types carry no commit/version binding |
