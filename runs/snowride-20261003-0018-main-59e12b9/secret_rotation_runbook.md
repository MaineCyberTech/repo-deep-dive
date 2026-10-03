# Secret Rotation Runbook — Snowride

Complements `evidence/closeout/CREDENTIAL_ROTATION_PLAN.md`, `evidence/phase3/04-credential-lifecycle/SECRET_HANDLING_GUIDE.md`, `ROTATION_LEDGER.csv`.

## Secret inventory (types only — never values)

| Secret | Where | Scope | Rotation trigger |
|---|---|---|---|
| `RM_SUPABASE_SERVICE_ROLE_KEY` | realtime env / `/home/user/.env` | server-only, bypasses RLS | suspected exposure |
| Supabase admin/db password (`db_pw`) | host `/home/user/.env` | `scripts/db.sh` / migrations | suspected exposure |
| `NTFY_TOPIC` | host `/home/user/.env` | alert channel | suspected exposure |
| `s3_kid`/`s3_key`/`do_s3`/`cf_tkey` | host `/home/user/.env` | offsite backup/tunnel | suspected exposure |
| TLS private keys | host acme.sh store | HTTPS | renewal/cert compromise |

## Procedure (service-role example)

1. Rotate in the Supabase dashboard.
2. Update `/home/user/.env` (never commit); recreate realtime/nginx.
3. Verify: `/runs` with a real token classifies; `/admin/version` healthy.
4. Append a `ROTATION_LEDGER.csv` row (append-only) and update the exception register if applicable.
5. Re-run the tracked-tree secret scan.

## Controls

- Secrets never committed; `.env` gitignored.
- Service-role key is server-only; publishable key is public by design.
- Residual: key delivered via container env not a Docker secret (SEC-P3-002).

## Audit notes

- No live secret values were printed during this audit; only type/path recorded.
- The tracked-tree sweep found only test fixtures/placeholders.
