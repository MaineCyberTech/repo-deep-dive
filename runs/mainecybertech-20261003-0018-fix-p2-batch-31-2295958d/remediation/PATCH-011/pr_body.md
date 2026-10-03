# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PATCH-011` — health/metrics minimisation, covering `SEC-P2-003` (P2) and
`API-P3-001` (P3). The unauthenticated `GET /health` previously returned the full dependency
check map, disclosing provider configuration (`stripe`/`jsm` `not_configured`) and raw Redis
error strings. `GET /metrics` was only gated when the optional `METRICS_TOKEN` was set, so an
unconfigured deployment exposed Prometheus metric labels (route names, tenant IDs, error
counts) to anyone who could reach the port.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d` (findings at `fix/p2-batch-31 @ 2295958d`)
- Patch set: `PATCH-011` — Health/metrics minimisation
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)

> Base note: the audit ran against a stale local clone (`2295958d`); `origin/fix/p2-batch-31` is
> now `11746adc`. Both patch-set source files (`routes/health.ts`, `app.ts`) are byte-identical
> between `2295958d` and `11746adc`, so both findings were verified to still reproduce on the
> current base and the fix is applied there.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-003` | P2 | open -> fixed (pending review) | `GET /health` now returns only `{service,status,uptime}`. Provider names, `not_configured` markers and raw dependency errors moved to a new `METRICS_TOKEN`-gated `GET /health/detail`. |
| `API-P3-001` | P3 | open -> fixed (pending review) | `GET /metrics` now fails closed: metrics are served only when `METRICS_TOKEN` is configured and presented, otherwise `404`. |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/routes/health.ts` | Added exported `authorizeInternalRequest()` (constant-time, fail-closed token gate for internal endpoints). Extracted the DB/Stripe/JSM/Redis probes into `runHealthChecks()`. Public `GET /health` now returns only `{service,status,uptime}` (200/503). New `GET /health/detail` returns the full `checks` map, gated by `METRICS_TOKEN` and 404 otherwise. |
| `apps/api/src/app.ts` | `GET /metrics` now calls the shared `authorizeInternalRequest()`; when `METRICS_TOKEN` is unset or does not match, it returns `404` instead of serving metrics. |
| `apps/api/src/__tests__/health.test.ts` | Updated for the trimmed public payload; added tests for non-disclosure, `/health/detail` 404 without/with-wrong token, full detail with the correct bearer token, and unit coverage of the shared gate. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | Proxmox ci-runner | 0 | `remediation/PATCH-011/verify.log` |
| `corepack pnpm --filter api typecheck` | Proxmox ci-runner (tsc --noEmit) | 0 | `remediation/PATCH-011/verify.log` |
| `corepack pnpm --filter api test` | Proxmox ci-runner (jest 29) | 0 | `remediation/PATCH-011/verify.log` — 122 suites passed, 1412 tests passed |
| `gitleaks detect --no-git --redact` (changed files) | `zricethezav/gitleaks:latest` (docker) | 0 | `remediation/PATCH-011/verify.log` — `no leaks found` |

- Secret scan (gitleaks): **pass** — no leaks found on the three changed files.
- Scope check: **pass** — only the two patch-set files plus `health.test.ts` were touched.
- Fail-closed behaviour is covered by the new tests: the public payload no longer contains
  `stripe`/`jsm`/`redis`/`database`, and `/health/detail` 404s without a valid token.

## Evidence bundle

- `remediation/PATCH-011/diff.patch` — SHA-256 `fa6f48244329b4e2ad51742bf99e77ec8af13efa3fa14305e18cf65b844fc75c`
- `remediation/PATCH-011/manifest.json`
- `remediation/PATCH-011/verify.log`

## Risk and rollback

- Risk: **low security risk change, operationally visible.** `/metrics` and `/health/detail` now
  require `METRICS_TOKEN` to be set *and* presented. In the DigitalOcean compose stack Prometheus
  scrapes `api:4000/metrics` without a bearer token today, so an operator must set
  `METRICS_TOKEN` and add the matching `authorization`/`authorization` credentials to the
  Prometheus scrape config (or the scrape will receive 404). This is the intended fail-closed
  posture; provisioning the token is a deploy-time prerequisite, tracked as an open follow-up.
- Public `GET /health` still returns `200`/`503` so the Docker healthcheck, deploy gate and
  e2e readiness checks keep working.
- Rollback: `git revert a7776f3` (or drop the branch).

## Open questions / follow-ups (out of scope)

- `infra/digitalocean/prometheus.yml` does not send a bearer token. After merge the deployment
  must set `METRICS_TOKEN` and configure the `mct-api` scrape job to send `Authorization: Bearer
  <token>`. `infra/` is outside this patch set, so it was intentionally not modified here.
- Should `/health/detail` also be reachable over loopback without a token (for local debugging)?
  This PR chooses strict fail-closed (404) so an unconfigured deployment exposes nothing.
- The web admin health dashboard (`HealthDashboardClient.tsx`) reads `json.database`/`json.worker`
  from the flat response, which does not match the wrapped API response shape and was already not
  reflecting real check values; it is unaffected by this change and should be fixed separately.

## Review checklist

- [x] Diff touches only the patch-set files (+ tests)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran in the lab; results pasted, not asserted
- [x] No secrets added; gitleaks clean
- [x] Tests added/updated for the fix
- [x] Rollback is practical

## Definition of done (for this set)

Public responses contain no provider names/errors; external `/metrics` 404.
