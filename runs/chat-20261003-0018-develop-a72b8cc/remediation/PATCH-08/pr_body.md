# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Restrict the Prometheus `/metrics` endpoints to a dedicated scraper service token instead of
any authenticated user session, and remove the per-tenant `channel_id` label from the message
counter.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-08` — Restrict `/metrics` and drop tenant labels (API-P1-001, OBS-P2-002)
- Repo / base: `chat` @ `a72b8cc` (`origin/develop`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `API-P1-001` | P1 | open -> fixed | `GET /metrics` no longer accepts an ordinary authenticated session; it requires a dedicated `METRICS_TOKEN` and fails closed (404 when unset, 401 on missing/incorrect token) |
| `OBS-P2-002` | P2 | open -> fixed | Scrape access restricted on both API and worker; `chat_messages_created_total` no longer carries the tenant-scoped `channel_id` label |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/middleware/metrics-auth.ts` | New `requireMetricsAccess` middleware: constant-time `METRICS_TOKEN` check (`x-metrics-token` header or `Authorization: Bearer`), fail closed |
| `apps/api/src/app.ts` | `GET /metrics` now uses `requireMetricsAccess` instead of the generic `authenticate`; removes the "any valid token passes" path |
| `apps/api/src/lib/metrics.ts` | Drops `labelNames: ["channel_id"]` from `chat_messages_created_total`; `recordMessageCreated()` no longer takes a channel id |
| `apps/worker/src/lib/metrics-auth.ts` | New `checkMetricsAccess` helper (same token policy) for the worker's raw Node HTTP metrics server |
| `apps/worker/src/main.ts` | Worker `/metrics` now requires the token |
| `apps/api/src/config/env.ts` | Adds optional `METRICS_TOKEN` (min 16 chars) to the API env schema |
| `.env.example`, `apps/api/.env.example`, `apps/worker/.env.example`, `infra/docker/.env.prod.example` | Document `METRICS_TOKEN` |
| `infra/docker/docker-compose.prod.yml` | Propagates `METRICS_TOKEN` to the `api` and `worker` containers |
| `apps/api/src/lib/__tests__/metrics.test.ts` | Regression test: message counter exposes no `channel_id` label |
| `apps/api/src/middleware/__tests__/metrics-auth.test.ts` | Unit tests: unset -> 404, missing/wrong/length-mismatch -> 401, matching header/Bearer -> next |
| `apps/worker/src/__tests__/metrics-auth.test.ts` | Unit tests for the worker token check |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter api test` | ci-runner (Proxmox, `lab-run.ps1`) | 0 | `remediation/PATCH-08/verify.log` — `Test Files 65 passed (65)`, `Tests 497 passed (497)`; 12 new tests ran (`metrics-auth` api=6, worker=5, `metrics.test`=1) |
| `corepack pnpm --filter @chat/config build && corepack pnpm --filter @chat/db build && corepack pnpm --filter @chat/sdk build && corepack pnpm --filter api typecheck && corepack pnpm --filter worker typecheck && corepack pnpm --filter api lint && corepack pnpm --filter worker lint` | ci-runner (Proxmox, `lab-run.ps1`) | 0 | `remediation/PATCH-08/verify.log` — `tsc --noEmit` clean (api + worker), `eslint` clean (api + worker) |
| `gitleaks protect --staged --redact --exit-code 1` | ci-runner (Proxmox, `lab-run.ps1`) | 0 | `remediation/PATCH-08/gitleaks.log` — `no leaks found` |

- Note: the workspace packages' `dist/` is excluded from the lab sync, so `typecheck` requires building `@chat/config`, `@chat/db`, and `@chat/sdk` first (included in command 2). A bare `--filter api typecheck` against an unbuilt lab tree fails on pre-existing workspace imports, unrelated to this patch.
- Scope check (files within patch set): **pass** — the diff touches only the metrics/API files, their tests, and env/compose wiring.

## Evidence bundle

- `remediation/PATCH-08/diff.patch` — SHA-256 `48f222eca3e7cac202f11df17e2baf17d7be27c9579dc41993c4cf2dea26352b`
- `remediation/PATCH-08/manifest.json`
- `remediation/PATCH-08/verify.log` (+ raw `raw-api.txt`, `raw-checks.txt`)
- `remediation/PATCH-08/gitleaks.log`

## Risk and rollback

- Risk: **low**. Authorization on a monitoring endpoint plus a metric-label reduction. Behaviour change:
  `/metrics` now returns 404 until `METRICS_TOKEN` is provisioned and the scraper sends it (intentional fail-closed).
- Rollback: `git revert 9feae529cc04e0f53e87abb1539b7307dbf62dbf` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs/env)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical
- [ ] `METRICS_TOKEN` provisioned in the deployment environment and scrape config updated (see open questions)

## Definition of done (for this set)

- `GET /metrics` (API and worker) rejects ordinary user sessions and requires the scraper token; disabled by default.
- No tenant-scoped (`channel_id`) label is emitted by the message counter.
- Token and label tests pass.

## Notes / open questions

- **Provisioning required:** set `METRICS_TOKEN` (>= 16 chars) in the production env file and configure the
  Prometheus scrape job to send it (e.g. `authorization: Bearer <token>` or `x-metrics-token`). Until then the
  endpoint intentionally returns 404. This secret must live in the deployment secret store, never in the repo.
- `chat_notifications_created_total` keeps its `type` label: it is a bounded internal category (e.g. `mention`),
  not a tenant identifier. If notification types ever become user-controlled, add an allowlist or hash them.
- `recordNotificationCreated`/`recordMessageCreated` currently have no in-tree callers; the functions remain
  exported for the message/notification paths. The label change is source-compatible with those call sites.
