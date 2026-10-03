# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the unassigned DATA findings from the 2026-10-03 snowride audit:
the RLS/grants SQL negative suites now run in CI, and the migration set gains a
machine-verifiable checksum manifest. Wiring the suites up surfaced one real
schema drift (a retired item category was silently re-permitted), fixed forward.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U04` — Unassigned DATA findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P2-001` | P2 | open -> partially-fixed | All 16 `supabase/tests/*.sql` suites run in the `migrations` CI job after the fresh-DB dry run. The dry-run stub is now faithful to Supabase (auth schema grants, `auth.uid()` legacy+JSON claims, complete `auth.users` columns, pgcrypto in `extensions`) and a deterministic fixture account is seeded. 0008 also exposed a real schema drift. |
| `DATA-P2-002` | P2 | open -> partially-fixed | `supabase/migrations/MANIFEST.sha256` + `scripts/migrations-manifest.sh --check/--write`, verified in CI. `.gitattributes` pins the migrations/manifest to LF so the digest is reproducible. The `0032` tombstone question is deferred (open question 2). |
| `DATA-P3-001` | P3 | open -> still-open | No production database was authorized for the audit; this is an owner-run read-only reconciliation, now documented in `docs/runbooks/MIGRATIONS.md`. Not fixable in-repo. |

Status is `partially-fixed` while the PR is an unmerged draft; the runner marks
`verified-fixed` only when the commit is merged (`tools/remediation_status.py`).

## Changes

| File | What changed |
|---|---|
| `scripts/ci-db-tests.sh` | New: runs `supabase/tests/*.sql` fail-closed after the dry run; seeds `scripts/ci-db-fixtures.sql` first. |
| `scripts/ci-db-fixtures.sql` | New: CI-only deterministic seed for the account the suites reference by fixed id. |
| `scripts/ci-migrations-dryrun.sh` | Faithful Supabase stub: full `auth.users` columns, `GRANT USAGE ON SCHEMA auth` + `auth.uid()` EXECUTE, `auth.uid()` reads legacy and JSON claims, pgcrypto installed in `extensions` (0056 uses `extensions.digest`). |
| `scripts/migrations-manifest.sh` | New: `--write`/`--check` for the migration digest manifest. |
| `supabase/migrations/MANIFEST.sha256` | New: 56 SHA-256 digests, lexical order, LF. |
| `supabase/migrations/0057_retire_consumable_category.sql` | New: re-asserts the 0019 `consumable` retirement that 0029 accidentally re-permitted. |
| `.github/workflows/ci-foundation.yml` | `migrations` job: verify the manifest, then run the negative suites. |
| `AGENTS.md`, `docs/runbooks/MIGRATIONS.md`, `supabase/tests/README.md` | Document the CI gate, manifest workflow, and owner-run live-head reconciliation. |
| `.gitattributes` | New: pin `supabase/migrations/*.sql` + `MANIFEST.sha256` to LF. |

## Verification Performed

Run in a clean LF bundle clone on the ci-runner lab (`/srv/work/snowride-ps-u04`)
at commit `dcdceca`. SQL scripts ran in a `postgres:17-alpine` client container
against a detached `postgres:17-alpine` server because the lab host has no `psql`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash scripts/migrations-manifest.sh --check` | ci-runner | 0 | manifest OK (56 files) |
| manifest tamper probe (append to `0001`; check must fail) | ci-runner | 1 | expected non-zero; restored check exits 0 |
| `bash scripts/ci-migrations-dryrun.sh` | ci-runner / postgres:17 | 0 | migrations applied clean: 56 files |
| `bash scripts/ci-db-tests.sh` | ci-runner / postgres:17 | 0 | db negative suites passed: 16 files |
| `npm ci` | ci-runner | 0 | 628 packages installed |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed |
| `actionlint .github/workflows/ci-foundation.yml` | ci-runner | 0 | no findings |
| `gitleaks detect --no-git --redact --source <changed file>` (x11) | ci-runner | 0 | no leaks in any changed file |
| `gitleaks detect --no-git --redact --source .` (full worktree) | ci-runner | 1 | 19 pre-existing fixture hits in `evidence/**` + `scripts/bundle-secret-gate.mjs`; none in this diff (same finding as PS-U01/PS-U02; this branch does not add the `.gitleaks.toml` allowlist that PS-U03 introduces) |

- Secret scan (gitleaks): **pass** — all 11 changed files clean; full-tree hits are pre-existing and untouched.
- Scope check (files within patch set): **pass** — PS-U04 declared no file list; the diff is limited to the CI workflow, the migration-integrity scripts/manifest/migration, and the related docs.

Raw output: `remediation/PS-U04/verify.log`, `remediation/PS-U04/gitleaks.log`.

## Evidence bundle

- `remediation/PS-U04/diff.patch` — SHA-256 `98965abcccd2b77993b2274f27174cc5b4b52e2d02e51d7dc1639182377b54d3`
- `remediation/PS-U04/verify.log`
- `remediation/PS-U04/gitleaks.log`
- `remediation/PS-U04/manifest.json`

## Risk and rollback

- Risk: low-to-medium. CI-only plus one forward migration. `0057` tightens
  `items_category_chk`; no migration after `0019` seeds a `consumable`, and no
  application code references `consumable`, so the constraint applies cleanly.
  The new suites and manifest gate only add checks.
- Rollback: `git revert dcdceca659acd8ecfce6eed5a80d6ea58fbf8d13` (the forward
  migration is additive; reverting the commit restores the previous workflow).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **DATA-P3-001 / live schema reconciliation.** A read-only
   `supabase_migrations.schema_migrations` dump is still required to confirm
   repo head == live head. Recorded as owner-run in `docs/runbooks/MIGRATIONS.md`.
2. **Migration `0032` tombstone.** `0032` never existed; whether a tombstone
   file is required remains open (the audit's own open question). Not fabricated.
3. **Migration-head re-attestation overlap with `P1-1` (`DATA-P1-001`).** This PR
   adds `0057`, moving the repo head past `0056`. `LAUNCH_MIGRATION_HEAD` must be
   re-attested to the lexical last migration; whichever of `P1-1` / `PS-U04`
   merges second owns that update.
4. **`consumable` retirement.** `0057` restores the `0019` retirement because
   `0029` re-listed the category when adding `equipment`. If consumables are
   actually intended to return, `0057` should be dropped and test `0008` updated
   instead — flagged for the owner rather than guessed.

## Definition of done (for this set)

- The `migrations` CI job verifies the manifest and runs all 16 negative suites
  on a fresh database.
- A migration added/edited without updating `MANIFEST.sha256` fails CI.
- The suites themselves pass on a fresh database (verified on the lab).
