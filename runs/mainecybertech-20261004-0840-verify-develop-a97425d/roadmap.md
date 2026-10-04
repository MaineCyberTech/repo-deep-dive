# Roadmap — post-merge follow-ups

**Repo:** `MaineCyberTech/mainecybertech` · **Commit:** `a97425db` · **Date:** 2026-10-04

No new code patches are required for the verified findings. The remaining work is
operational or an explicit owner decision.

## Operator actions

| Item | Finding | Action |
|---|---|---|
| Provision the `prod` environment | `CI-P1-001` | Add `SUPABASE_*`, `JWT_SECRET`, `FIELD_ENCRYPTION_KEY`, `TURNSTILE_SECRET_KEY`, `REDIS_PASSWORD`, alerting URLs; apply migrations `5302430`–`5302436`; run a prod deploy drill |
| Verify backup/restore end to end | `OBS-P2-003` | Provide `SUPABASE_DB_URL`, `BACKUP_ENCRYPTION_KEY`, bucket + webhook secrets; confirm the `0 4 * * *` schedule fires |
| Continue the RLS rollout | `ARCH-P2-002` | Flip remaining modules in `RLS_READS_ENABLED` / `RLS_WRITES_ENABLED` and watch the bypass metric |
| Replace the dev Turnstile test pair | `SEC-P2-002` | Set the real Cloudflare site/secret pair for non-dev environments |

## Owner decisions

| Item | Finding | Decision needed |
|---|---|---|
| Externalize the committed prompt/audit corpus | `HYG-P2-001` | Keep in-repo, move to a separate repo, or artifact store |
| Reconcile the duplicate product catalogs | `HYG-P2-002` | Pick the canonical catalog generation |
| Topology / SPOF | `ARCH-P2-001` | Accept single-droplet risk or fund redundancy (API replica, managed Redis) |
| `main` promotion + scheduled jobs | `CI-P3-001` | Promote `develop` to `main` or re-point scheduled workflows |
| Tabletop evidence | `OBS-P3-001` | Schedule the exercise and record the evidence |

## Optional machine hardening

| Item | Finding | Action |
|---|---|---|
| Exec bits on tracked shell scripts | `DET-P2-002` | `git update-index --chmod=+x` for the 17 scripts |
| Digest-pinned images | `DET-P3-004` | Pin the 4 container images by digest |
