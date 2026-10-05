# Owner-gated findings — proposals and residuals

Run: `mainecybertech-20261004-full-main-9c0b88c` · Target: `mainecybertech` @ `9c0b88c`

The P1 rows below are **owner/operator decisions or residuals**. No infrastructure was
changed for them. Each entry records a concrete proposed option and the residual that
remains until the owner decides. The remaining P1 rows (48 of 59) were re-verified as
`verified-fixed` in code at `9c0b88c` — see `P1_RECONCILIATION.md` and `findings.json`.

## CI-P1-001 / CI-P1-003 — production deploy has no active approval gate / prod env not provisioned

- **Evidence**: `.github/workflows/deploy-do.yml:571` already targets `prod-approval` for
  prod; `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` / `docs/RELEASING.md` state the
  `prod`/`prod-approval` environments still lack secrets and required reviewers.
- **Proposed option (operator action)**: in GitHub → Settings → Environments, add ≥1 required
  reviewer to `prod-approval` and populate the prod secret set; then dispatch `deploy-do`
  with `deploy_target: prod` and confirm it pauses at "Waiting for approval".
- **Residual until provisioned**: a `main` push can still deploy to production without a
  human approval step; the pinned host-key port (PR #98) fails closed without the
  `DO_SSH_HOST_FINGERPRINT` / `DO_SSH_HOST_KEY` secrets.

## DATA-P1-003 — soft-delete columns are dead schema; DELETE endpoints hard-delete

- **Evidence**: `supabase/migrations/5302109_soft_delete.sql` adds `deleted_at` / `deleted_by`
  to tickets/projects/documents; no app code reads or writes them and DELETE routes hard-delete.
- **Proposed option A (implement tombstones)**: DELETE sets `deleted_at = now(), deleted_by =
  <actor>`; list/get add `.is("deleted_at", null)`; add an admin restore endpoint; keep the
  existing indexes. **Option B (document hard delete)**: drop the columns and state hard
  delete in the data-retention docs. Record the choice in the data-governance policy.
- **Residual until decided**: the schema advertises recoverability it does not provide;
  accidental deletes are permanent.

## IR-P1-006 — no runtime detection/alerting for tenant-isolation (RLS) regressions

- **Evidence**: `scripts/verify-rls.mjs` / `check-rls-predicate.mjs` gate migrations statically,
  but `infra/digitalocean/alertmanager.tmpl.yml` has no RLS/tenant rule.
- **Proposed option**: add an alert on RLS `DB_ERROR` / empty-result spikes per enabled module
  and a per-module multi-tenant isolation E2E assertion using seeded org-A/org-B data.
- **Residual until implemented**: a regression is only caught by the slower static gates or a
  human reading logs.

## DR-P1-003 — backup encryption/offsite require operator-provisioned secrets

- **Evidence**: `scripts/backup-database.sh` supports AES-256-CBC (`BACKUP_ENCRYPTION_KEY`)
  and an offsite copy (`S3_OFFSITE_BUCKET`); the backup workflows set
  `REQUIRE_BACKUP_ENCRYPTION=1` (fail closed).
- **Proposed option (operator action)**: create `BACKUP_ENCRYPTION_KEY`, create the second
  bucket, set `S3_OFFSITE_BUCKET`/`S3_OFFSITE_PREFIX`, then run `db-backup` once and
  `db-restore-test` to confirm the encrypted object decrypts.
- **Residual until provisioned**: backups are not yet encrypted/offsite in the deployed flow;
  the code affordance is in place.

## DR-P1-005 / IR-P1-002 — bad-migration recovery is manual; no recorded drill

- **Evidence**: `supabase-migrations.yml` now fails closed on post-push drift (the swallowed
  `db diff || true` is gone); `docs/ROLLBACK_PROCEDURES.md` documents reverse-migration, PITR
  and S3-restore options.
- **Proposed option**: rehearse a bad-migration drill on a throwaway project/branch, record
  the measured recovery time, and (where feasible) generate reverse DDL for common operations.
- **Residual until drilled**: recovery time against the documented RTO is unproven.

## DR-P1-006 — RPO/RTO targets documented but unvalidated

- **Evidence**: `docs/RTO_RPO.md` now separates PITR (≤5 min) from the daily `pg_dump` (≤24 h)
  and covers storage; no drill measurement is recorded.
- **Proposed option**: run D1/D2 drills and record measured durations / data-loss windows in
  `docs/RTO_RPO.md`.
- **Residual until measured**: targets are not evidence-backed.

## REL-P1-001 — no version identity (tags / release workflow)

- **Evidence**: `git tag` is empty; `scripts/generate-sbom.mjs` already emits `serialNumber`,
  `metadata.component.version` and git-commit metadata; no release workflow exists.
- **Proposed option**: cut annotated git tags on prod promotion and attach the SBOM to the
  GitHub Release; optionally derive a root `version` from the tag.
- **Residual until decided**: releases are identified only by GHCR SHA tags.

## AI-P1-001 — vendored audit prompt pack is pinned/stale

- **Evidence**: `prompts/repo-deep-dive/` vendors prompts 00–40 + `MASTER_RUNNER_FULL_HARDENING`;
  prompt 45 is not vendored; `prompts/PROVENANCE.md` now marks the tree pinned/historical.
- **Proposed option**: refresh the vendored pack from upstream, or add an explicit
  pinned-version header plus a guard that run-manifest prompt references resolve to vendored files.
- **Residual until decided**: a run manifest that references a non-vendored prompt would fail
  to resolve (mitigated by treating `prompts/` as historical data, AI-P2-002).

## SECRET-P1-001 — dead `M365_WEBHOOK_SECRET` config

- **Evidence**: `M365_CLIENT_STATE` is now written by `deploy-do.yml`; `M365_WEBHOOK_SECRET`
  remains declared in `apps/api/src/config/env.ts:58` and `apps/api/.env.example:33` with no
  first-party consumer (removed from compose).
- **Proposed option**: remove the dead key, or implement real M365 signature verification if
  Graph supports it; add `M365_CLIENT_STATE` to the rotation inventory.
- **Residual until decided**: security-by-misleading-config (fail-closed today).
