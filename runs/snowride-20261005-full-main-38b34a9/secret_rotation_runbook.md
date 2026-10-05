# Secret rotation runbook — snowride @ `38b34a9`

Companion artifact for `38_env_secret_rotation.md`. Values are never printed or
committed; this records the rotation targets and the current gaps.

## Secret inventory

| Secret | Where | Rotation status |
|---|---|---|
| `RM_SUPABASE_SERVICE_ROLE_KEY` | host env / compose interpolation | owner action; empty value silently disables persistence (`SECRET-P2-001`) |
| `SUPABASE_*` URL/issuer/JWKS | compose env (public) | n/a |
| `METRICS_TOKEN` | host env | no documented rotation (`SECRET-P3-001`) |
| `NTFY_TOPIC`, `s3_*`, `cf_tkey`, `db_pw` | `/home/user/.env` (untracked) | owner action |
| `LAUNCH_OWNER_SIGNATURE` / `LAUNCH_OWNER_PUBLIC_KEY` | inject at deploy | re-attest per release (`FINAL-P1-001`) |

## Procedure

1. Generate the new value out-of-band; never echo it.
2. Update `/home/user/.env` (or the approved secret channel).
3. Restart the affected service (`docker compose up -d --force-recreate`).
4. Verify: `/readyz` healthy, `/metrics` authorized (or 401 wrong token),
   `scripts/attested-migration-head-check.mjs` unaffected.
5. Append a name-only rotation record under `evidence/` (no values).

## Blocking gaps

- `SECRET-P2-001`: fail boot/readiness when `NODE_ENV=production` and the
  service-role key is empty.
- `SECRET-P3-001`: constant-time compare + a `METRICS_TOKEN` rotation entry.
