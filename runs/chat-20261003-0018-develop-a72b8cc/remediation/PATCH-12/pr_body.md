# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Wire the missing alerting pipeline and give API errors a durable record:

- Check in Prometheus alert rules plus Alertmanager routing (the metrics pipeline existed
  but no rules or notification channels were checked in), and document the required env.
- Persist the API admin error buffer to an optional newline-delimited file (`ERROR_LOG_FILE`)
  so `/admin/logs` survives restarts, and make `initSentry()` warn (instead of silently
  returning) when `SENTRY_DSN` is unset.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-12` — Alerting + durable log aggregation (OBS-P1-001, OBS-P2-003)
- Repo / base: `chat` @ `a72b8cc` (`origin/develop`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P1-001` | P1 | open -> partially-fixed | Rules (`ChatApiDown/HighErrorRate/HighLatency/CircuitBreakerOpen/HealthcheckFailing/WorkerQueueBacklog/WorkerQueueFailures`) and Alertmanager routing are now checked in with required env documented; actual notification delivery depends on deploying the stack and provisioning `ALERT_EMAIL` / `ALERT_WEBHOOK_URL` (open question). |
| `OBS-P2-003` | P2 | open -> partially-fixed | Errors persist to `ERROR_LOG_FILE` (opt-in, redacted, rehydrated on startup); `initSentry()` now logs a warning when `SENTRY_DSN` is unset. Full durable aggregation still depends on mounting the file on a persistent volume and setting `SENTRY_DSN` in all envs (open question). |

## Changes

| File | What changed |
|---|---|
| `infra/prometheus/rules/chat.rules.yml` | New Prometheus alert rules for API availability, 5xx rate, p95 latency, circuit breaker, health-check failures, and worker queue backlog/failures |
| `infra/prometheus/alertmanager.yml` | New Alertmanager route: email default receiver + webhook receiver for critical alerts (env-expanded) |
| `infra/prometheus/README.md` | Deploy steps, required env (`METRICS_TOKEN`, `ALERT_EMAIL`, `ALERT_WEBHOOK_URL`), and validation commands |
| `docs/runbooks/alerting.md` | Points the "Prometheus / Alertmanager" section at the checked-in rules/routing instead of a "future" snippet |
| `infra/terraform/README.md`, `infra/terraform/terraform.tfvars.example` | Document/add `alert_email`, which gates the DO CPU/memory/disk alerts |
| `apps/api/src/modules/admin/error-buffer.ts` | Optional durable JSONL backing store (`ERROR_LOG_FILE`), startup rehydration, email-PII redaction, best-effort writes |
| `apps/api/src/modules/admin/__tests__/error-buffer.test.ts` | Persistence, rehydration, redaction, corrupt-file, and unwritable-path tests |
| `apps/api/src/lib/sentry.ts` | Warn when `SENTRY_DSN` is unset instead of silently disabling error tracking |
| `apps/api/src/lib/__tests__/sentry.test.ts` | Assert the warning is emitted |
| `apps/api/src/config/env.ts`, `apps/api/src/server.ts` | Add `ERROR_LOG_FILE` and call `initErrorLog()` at startup; replace the stale alerting TODO |
| `.env.example`, `apps/api/.env.example` | Document `ERROR_LOG_FILE` and `ALERT_WEBHOOK_URL` |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter api test` | ci-runner (Proxmox, `lab-run.ps1`) | 0 | `remediation/PATCH-12/verify.log` — `Test Files 64 passed (64)`, `Tests 492 passed (492)`; new tests ran (`error-buffer`=6, `sentry`=1) |
| `corepack pnpm --filter @chat/config build && corepack pnpm --filter @chat/db build && corepack pnpm --filter @chat/sdk build && corepack pnpm --filter api typecheck && corepack pnpm --filter api lint` | ci-runner (Proxmox, `lab-run.ps1`) | 0 | `remediation/PATCH-12/verify.log` — `tsc --noEmit` clean, `eslint` clean |
| `yq e '.' infra/prometheus/rules/chat.rules.yml && yq e '.' infra/prometheus/alertmanager.yml && yq e '.groups[].rules[].alert' ...` | ci-runner (Proxmox, `lab-run.ps1`) | 0 | `remediation/PATCH-12/raw-checks.txt` — YAML OK, all 7 required alert rules present |
| `promtool check rules` / `amtool check-config` | ci-runner (Proxmox, `lab-run.ps1`) | not run | tools are not installed in the lab image; recorded as unavailable rather than passed |

- Secret scan (gitleaks): **pass** — `gitleaks dir <changed-file-set> --redact --exit-code 1` -> `no leaks found` (`remediation/PATCH-12/gitleaks.log`).
- Scope check (files within patch set): **pass** — observability/incident-readiness files only (rules/routing + docs, terraform example/README, API error buffer/Sentry/env, tests, env examples).
- Note: worker `/metrics` returns JSON, so the worker queue rules require a JSON exporter; they are inert until it exists (documented in the rules header and README).

## Evidence bundle

- `remediation/PATCH-12/diff.patch` — SHA-256 `96de1f1cc65e1f8cfdba5d9b26b2de57a13100bb50b6945c484880668f05a2bf`
- `remediation/PATCH-12/manifest.json`
- `remediation/PATCH-12/verify.log` (+ raw `raw-api.txt`, `raw-checks.txt`, `raw-checks2.txt`, `gitleaks.log`)

## Risk and rollback

- Risk: **low**. Inert-config additions (no runtime reads of the new rules), an opt-in log file that defaults off, and a warning log line. The only behavior change when unset is the extra warning; nothing fails closed differently.
- Rollback: `git revert d458b82e1a6ba11dd87b91b07d60aa7c53396f28` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs/env)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical
- [ ] `ALERT_EMAIL` / `ALERT_WEBHOOK_URL` / `METRICS_TOKEN` provisioned and the Prometheus + Alertmanager stack deployed (see open questions)

## Definition of done (for this set)

- Alert rules and notification routing are checked in, versioned, and validated.
- `alert_email` gating of DO alerts is documented.
- API errors have an opt-in durable record that survives restarts, with PII redaction.
- Missing Sentry configuration is observable, not silent.

## Notes / open questions

- **Deploy the alert pipeline:** provision `ALERT_EMAIL` and `ALERT_WEBHOOK_URL`, mount the
  rules file via `rule_files:`, and run Alertmanager with `--config.expand-env`. The PR ships
  config only; no notification channel is active until that deployment.
- **Worker JSON exporter:** `apps/worker/src/main.ts` returns JSON, so Prometheus cannot scrape
  it directly. Add a JSON exporter (or change the worker to expose Prometheus text) to activate
  `ChatWorkerQueueBacklog` / `ChatWorkerQueueFailures`.
- **Persistent volume:** `ERROR_LOG_FILE` is only durable if the path is mounted on a persistent
  volume; otherwise it survives restarts on the same host but not container replacement.
- `promtool` / `amtool` are absent from the lab image; run `promtool check rules` and
  `amtool check-config` in CI/deploy where they are available.
