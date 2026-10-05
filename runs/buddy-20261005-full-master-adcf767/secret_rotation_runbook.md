# Secret Rotation Runbook

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Finding reference: `38_env_secret_rotation` (area SECRET)

## Inventory

No application secrets exist. `repo_inventory` reports no tracked `.env`/key material; the one
"secret-adjacent" filename is a prior audit markdown. The app needs no runtime credentials and
makes no outbound calls (`connect-src 'self'` in `next.config.js`).

| Secret | Where used | Rotation trigger | Procedure |
|---|---|---|---|
| (none in product) | — | — | — |
| GitHub Actions `GITHUB_TOKEN` | CI / release workflows | ephemeral per run | managed by GitHub; least-privilege `permissions:` blocks |
| Release OIDC identity | `attest-build-provenance` | ephemeral per run | no long-lived credential stored |
| Maintainer PATs / deploy keys | repo administration | on suspicion/leaver | revoke + reissue; see incident tabletop |

## Procedure if a token is ever added

1. Store only in GitHub Actions secrets / environment secrets, never in the repo.
2. Reference only through `env:`, never inline in `run:` commands.
3. Rotate on a schedule and immediately on suspected exposure.
4. Re-run gitleaks (CI) and deterministic secret scan after rotation; allowlist only reviewed
   false positives via a versioned `.gitleaks.toml`.

## Verdict

**Not applicable** for credential rotation today; documented so a future server/agent mode has
a starting point. No secret was printed or read during this audit.
