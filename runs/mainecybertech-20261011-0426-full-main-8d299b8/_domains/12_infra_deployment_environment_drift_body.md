# Infrastructure, Deployment, and Environment Drift Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (read-only worktree at `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8d` (merge of PR #168)
- Generated at: 2026-10-11
- Auditor: domain subagent (area INFRA, prompt `12_infra_deployment_environment_drift.md`)
- Area code: INFRA
- Output path: `docs/audits/{name}/{run}/12_infra_deployment_environment_drift.md` (pack run folder: `_domains/`)
- Scope limitations:
  - No access to the live droplets, DO API, Terraform state, GHCR, Cloudflare, or GitHub environment settings. Everything below is repository evidence; live drift is explicitly marked `unverifiable`.
  - No `terraform`/`docker`/`promtool` execution was attempted (resource discipline; long-running commands prohibited). The promtool test file was read, not run.
  - Secrets are referenced by name and `path:line` only; no values were read or printed.

## Scope

Reviewed: `infra/digitalocean/**` (droplet compose stack, Caddyfile variants, Prometheus rules/config, Alertmanager template, redis entrypoint, `.env.example`), `infra/terraform/digitalocean/**` (providers, variables, droplet, firewall, DNS, outputs, cloud-init, tfvars examples, backend configs, lock file), `.github/workflows/deploy-do.yml`, `terraform-do.yml`, `supabase-migrations.yml`, `backup-dispatch.yml`, `db-backup.yml`, `db-restore-test.yml`, `storage-backup.yml`, the app Dockerfiles and `.dockerignore`, `apps/*/src` env schemas and web env validation, `scripts/rollback.sh`, `scripts/backup-database.sh`, `scripts/validate-terraform-env.sh`, and the ops docs (`FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md`, `ROLLBACK_PROCEDURES.md`, `RELEASING.md`, `CI.md`, `MONITORING_AND_ALERTING.md`, `ENVIRONMENT_VARIABLES.md`, `GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `RTO_RPO.md`, `infra/digitalocean/README.md`, `infra/terraform/README.md`).

Not reviewed (owned by other domains): container runtime hardening deep dive (CTR prompt 36), backup/restore drill execution (DR 32), incident response (IR 33), observability design (OBS 14), CI governance/branch protection (CI 10, BP 34), supply chain/SBOM (SC 11, SBOM 35).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `infra/digitalocean/docker-compose.yml` | Droplet compose | Source of truth for all 7 services, users, healthchecks, limits, volumes | 344 lines, read in full |
| `infra/digitalocean/{Caddyfile,Caddyfile.dev,Caddyfile.prod}` | Reverse proxy | TLS, headers, /metrics exposure per env | diffed dev vs prod |
| `infra/digitalocean/prometheus.{yml,rules.yml,rules.test.yml}`, `alertmanager.tmpl.yml` | Observability config | Alert path, scrape auth, dead-man's switch | read in full |
| `infra/digitalocean/redis-entrypoint.sh`, `.env.example`, `README.md` | Runtime config | Password off argv, env template, service inventory | read in full |
| `infra/terraform/digitalocean/*.tf`, `cloud-init.yml`, `env/*` | Terraform | Firewall/SSH, droplet, DNS, state backend, tfvars | read in full |
| `.github/workflows/deploy-do.yml` (935 lines) | Deploy pipeline | Env delivery, health gate, rollback, attestation gate | read in full |
| `.github/workflows/terraform-do.yml` | Infra pipeline | Manual-only, drift plan, prod-approval | read in full |
| `.github/workflows/{db-backup,db-restore-test,storage-backup,backup-dispatch,supabase-migrations}.yml` | Ops workflows | Backup hooks, restore verification, migration coupling | read in full / key sections |
| `apps/api/Dockerfile`, `apps/worker/Dockerfile`, `apps/web/Dockerfile`, `.dockerignore` | Images | Non-root users, healthchecks, build args, no secrets | read in full |
| `apps/api/src/config/env.ts`, `apps/worker/src/env.ts`, `apps/web/lib/env.ts` | Runtime validators | Env schema (source of truth for delivery comparison) | read in full |
| `scripts/rollback.sh`, `scripts/backup-database.sh`, `scripts/validate-terraform-env.sh` | Deploy/ops scripts | Rollback path, dump version, tfvars guard | read in full |
| Ops docs listed in Scope | Documentation | Consistency vs current pipeline/config | line-level comparison |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline -3` | command | Bind the audit to the exact commit | `8d299b8d Merge PR #168` |
| `git ls-files infra/terraform/digitalocean/env/` + `git ls-files \| grep -i tfvars` | command | INFRA–P3-008 re-verify | only `*.example` tracked |
| `git check-ignore -v infra/terraform/digitalocean/{dev,prod}.tfvars` | command | tfvars ignore coverage | module-root paths NOT ignored |
| `git ls-files -s scripts/rollback.sh infra/digitalocean/redis-entrypoint.sh` | command | exec-bit regression (PORT-001) | `100755` on both |
| Python diff: deploy envs list (50) vs printf writes (46) vs compose `${VAR}` refs | command | env name drift (INFRA–P2-006) | zero mismatches (control vars only) |
| `grep -rn "TASK_QUEUE_ENABLED\|appendonly\|promtool" ...` | command | schema defaults, Redis AOF claim, rules tests | see findings |
| `bash -c 'set -euo pipefail; echo "$UNSET" \| cat \|\| true'` | command | Confirm rollback script login failure mode | pipeline failure swallowed by `\|\| true`; shell continues |
| `grep -rn "cancel-in-progress\|terraform-do" docs/*.md` | command | docs consistency (INFRA–P2-005) | 8 contradictions captured |
| Read of previous run registers (`follow_up_register.md`, `risk_register.md`, `12_infra_*.md` at 9c0b88c) | evidence | verification duty | 12 INFRA rows re-checked |

Live checks deliberately not performed: SSH/UFW/DO firewall state, droplet `.env` contents, Terraform state, GHCR tags, GitHub environment settings. All such rows are marked `unverifiable` below.

## Executive Summary

The infrastructure domain is in materially better shape than at the 20261004 baseline. The 12 INFRA rows from the previous register were re-verified at `8d299b8d`: **8 are verified-fixed**, 1 is partially-fixed, and 3 remain open (all documentation/configuration drift). The strongest work is in the deploy pipeline: the droplet `.env` is now written from 46 secrets with no shell re-expansion, the env-delivery gap (INFRA–P2-006) is closed for every non-defaulted schema variable, `METRICS_TOKEN` is delivered to both the API and the Prometheus scrape via a 0600/400 file owned by the container user (commits `8f8dbe42`, `ddbc389c`, `00cb3da6`), and the Alertmanager/ntfy dead-man's switch is fully wired with a prod fail-closed guard.

Remaining risks cluster in three places. **(1) Operator-facing truth drift:** the deployment handbook, rollback runbook §4, the infra README and the secrets matrix still describe the pre-remediation pipeline (concurrency, Terraform triggers, firewall port 2376, migration gating, health semantics, state bucket names, Slack-only alerting, optional METRICS_TOKEN). **(2) The manual rollback tool is broken:** `scripts/rollback.sh` defaults to a stale GHCR prefix and never forwards registry credentials, and its health checks are weaker than the pipeline's. **(3) Deploy confidence stops at api/web/worker:** a deploy can finish green while Alertmanager/Prometheus (the alert delivery path) is down, and an empty `METRICS_TOKEN` produces a permanently-failing API scrape with no deploy-time guard. Live Terraform-vs-droplet drift remains unverifiable from the repository; the weekly plan-only drift check is present but dormant (`TF_DRIFT_PLAN_ENABLED` unset) and the DO token is reportedly 401 (CI-domain rows own that).

Recommended next actions: fix `scripts/rollback.sh` (P2), extend the deploy health gate to the monitoring containers (P2), and do a single documentation-sync PR (P2/P3) covering every contradiction listed in the findings.

## Inventory

### Environment inventory (droplet `.env`, written by `deploy-do.yml:669-716`)

| Group | Variables | Delivery |
|---|---|---|
| Supabase / auth | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET` | required by compose (`${VAR:?}`) and by both app schemas |
| Domains / CORS | `APP_DOMAIN`, `API_DOMAIN`, `CORS_ORIGIN` | computed in `setup` from branch/target |
| Queue | `REDIS_PASSWORD` (required), `REDIS_URL` (compose-built) | password in `.env`; URL built in compose |
| Payments / PII | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `FIELD_ENCRYPTION_KEY` (prod fail-closed at API boot) | optional in schema, fail-closed for PII key |
| Integrations | `JIRA_*`, `JSM_*`, `M365_*`, `PUBLIC_*_WEBHOOK_URL`, `SMTP_*`, `EMAIL_FROM`, `TURNSTILE_SECRET_KEY`, `SENTRY_DSN` | all forwarded |
| Security toggles | `MFA_ENFORCEMENT_ENABLED`, `RLS_READS_ENABLED`, `RLS_WRITES_ENABLED` | forwarded (empty = service-role default) |
| Metrics | `METRICS_TOKEN` | `.env` + `/opt/mct-portal/metrics-token` (65534:65534, 0400) |
| Alerting | `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` (prod fail-closed), `ALERTMANAGER_CRITICAL_WEBHOOK_URL`, `ALERTMANAGER_DEFAULT_WEBHOOK_URL`, `ALERTMANAGER_SLACK_API_URL`, `ALERTMANAGER_SLACK_CHANNEL` (var), `ALERTMANAGER_WEBHOOK_USER/PASS` | forwarded; compose substitutes no-op loopback when unset |
| Build/deploy | `IMAGE_TAG`, `GHCR_IMAGE_PREFIX` | passed at `docker compose up`, not written to `.env` |
| CI-only notifiers | `NTFY_ALERTS_URL/USER/PASS`, `SLACK_WEBHOOK_URL` | GitHub secrets used by backup/restore workflows only, correctly not in `.env` |

### Runtime config inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Droplet compose | `infra/digitalocean/docker-compose.yml` | 7 services, all with `cap_drop: ALL`, `no-new-privileges`, `mem_limit`, `pids_limit`, bounded json-file logs | functional | low | redis/api/worker/prometheus/alertmanager read-only rootfs + tmpfs |
| Reverse proxy | `Caddyfile.dev` / `Caddyfile.prod` / `Caddyfile` fallback | TLS + headers, SSE flush, `/metrics` 404 on prod | functional | low | dev Caddyfile omits the `/metrics` 404 block; the API 404s unauthenticated requests anyway |
| Scrape auth | `prometheus.yml:26-28`, `docker-compose.yml:216` | Bearer token from `./metrics-token` | functional | low | token required for a successful scrape (see METRICS_TOKEN guard finding) |
| Alert routing | `alertmanager.tmpl.yml`, compose `:278-293` | awk-render at start, fail on surviving placeholder, Watchdog → external URL | functional | low | state volume `alertmanager-data` |
| Redis | compose `:27-61`, `redis-entrypoint.sh` | password-file entrypoint, `user: redis`, `REDISCLI_AUTH` healthcheck | functional | low | no AOF (see RTO_RPO finding) |
| App images | `apps/*/Dockerfile` | non-root (`appuser`/`nextjs`), healthchecks, digest-pinned node:20-alpine, npm/corepack removed | functional | low | web build args are all `NEXT_PUBLIC_*` (public by design) |

### Deployment inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| App deploy | `.github/workflows/deploy-do.yml` | push main/develop + dispatch (`deploy_target`, `rollback_sha`); build/scan/attest/verify; SSH deploy; health gate; auto-revert | functional | medium | health gate covers api/web/worker only |
| Infra deploy | `.github/workflows/terraform-do.yml` | manual dispatch + dormant weekly plan-only drift check; prod-approval on apply | manual-only by design | medium | operator-gated on DO token |
| Migrations | `.github/workflows/supabase-migrations.yml` | `db push --include-all`, dry-run artifact, fail-closed post-push drift check | functional | medium | prod gate runs before app deploy (reverse path is manual; IR/DR rows own this) |
| Backups | `backup-dispatch.yml` → `db-backup.yml`, `storage-backup.yml`, `db-restore-test.yml` | daily/weekly, encrypted, offsite option, ntfy+Slack failure notify | functional | low | dispatched onto `develop` from `main` |
| Manual rollback | `scripts/rollback.sh` | operator rollback by SHA | broken (prefix + credentials) | medium | see finding |
| CI rollback | `deploy-do.yml:11-15,38,435-515,807-858` | `rollback_sha` dispatch, attestation allow-list, auto-revert to previous tag | functional | low | fail-closed provenance verification |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 4 | digest-pinned base images, non-root users, healthchecks, npm/corepack removed (`apps/*/Dockerfile`) | no image-level secret scan differences (trivy image scan exists in deploy path) | keep |
| Compose | 4 | 7 services hardened, bounded logs, resource/PID limits, named volumes, explicit required env | health gate ignores alertmanager/prometheus/caddy | extend health gate |
| Terraform/OpenTofu | 4 | fail-closed SSH, required_version/use_lockfile consistent, provider lock file, env-isolated backends | live drift unverifiable; drift plan dormant; module-root tfvars unignored | widen ignore + doc sync |
| Cloud/hosting config | 3 | DNS records per env, droplet monitoring tag, cloud-init UFW | UFW create-time only; live state unverified | document/automate UFW refresh |
| Deploy scripts | 3 | `.env` via printf, chmod 600, token file ownership, retries, auto-revert | rollback.sh broken; health gate narrow | fix rollback.sh + gate |
| Reverse proxy | 4 | per-env Caddyfiles, SSE flush, security headers, TLS certs | dev Caddyfile lacks the prod `/metrics` 404 (app-level gate covers) | optional consistency |
| Environment examples | 3 | app-level `.env.example` files current; droplet `.env.example` missing alerting/metrics keys | drift in `infra/digitalocean/.env.example` | add missing keys |
| Runtime validators | 4 | Zod boot validation; prod fail-closed for PII key + Turnstile; web prod fail-fast for API URL | METRICS_TOKEN not guarded | add prod guard |
| Secret references | 4 | env-only delivery, no argv secrets, no client-exposed secrets found | NTFY/ALERTMANAGER rows missing from the secrets matrix | update matrix |
| Build args | 4 | web build args all `NEXT_PUBLIC_*`; no secret in build args | none found | keep |
| Container users | 4 | redis, appuser (1001), nextjs (1001); metrics-token chowned to 65534 | none found | keep |
| Health/readiness/liveness | 3 | per-container healthchecks; deploy gate + SSH worker probe + HTTPS checks | monitoring stack unchecked; caddy healthcheck is config-validation only | extend gate |

## Detailed Review

### Item: Droplet compose stack

- Evidence: `infra/digitalocean/docker-compose.yml:1-344`.
- What it does: defines redis, api, worker, web, prometheus, alertmanager, caddy with shared `x-security` (cap_drop ALL, no-new-privileges) and bounded json-file logging.
- How it appears to work: deploy copies the file to `/opt/mct-portal/` and runs `docker compose -p mct-portal up -d` with `IMAGE_TAG`/`GHCR_IMAGE_PREFIX`.
- Dependencies: `.env`, `redis-entrypoint.sh`, `prometheus.yml`, `prometheus.rules.yml`, `alertmanager.tmpl.yml`, `Caddyfile*`, `certs/`, `metrics-token` — all copied by `deploy-do.yml:789-805` (metrics-token written at `:722-727`).
- Current controls: `${VAR:?}` for SUPABASE_*/JWT_SECRET/REDIS_PASSWORD/IMAGE_TAG; read-only rootfs for api/worker/web/prometheus/alertmanager; tmpfs `/tmp`; healthchecks on redis/api/worker/alertmanager/caddy.
- Missing controls: no healthcheck on prometheus; the deploy gate does not assert alertmanager/prometheus/caddy.
- Risks: a broken alerting path can ship green (see finding).
- Recommended improvement: assert every healthchecked service in the deploy gate.
- Suggested tests: CI `docker compose config` render check with a fixture `.env`; a compose-level healthcheck assertion script.
- Suggested docs: add alertmanager/metrics-token to `infra/digitalocean/README.md`.

### Item: Terraform droplet/firewall/DNS

- Evidence: `variables.tf:76-92`, `firewall.tf:20-48`, `cloud-init.yml:19-30`, `droplet.tf:1-21`, `dns.tf:1-73`, `providers.tf:1-31`, `env/backend.*.hcl`, `.terraform.lock.hcl`.
- What it does: one droplet per env (dev/prod state isolated), DO firewall (SSH allowlist + Cloudflare IPs on 80/443), UFW mirror at first boot, proxied A records for app/api/www per domain, S3 backend with native locking.
- Current controls: SSH fail-closed in code + CI guard; `prevent_destroy` on droplet/firewall/DNS; provider lock file with hashes.
- Missing controls: live-state drift detection is dormant; UFW is create-time only; module-root tfvars unignored.
- Risks: documented-vs-live drift is unverifiable without operator access; narrowed SSH allowlists leave stale host rules (edge still blocks).
- Recommended improvement: enable the drift plan after token rotation; widen the tfvars ignore; document the UFW behavior.
- Suggested tests: `terraform fmt -check` (already in CI), `terraform validate` with a dummy tfvars fixture in CI, `tflint` optionally.
- Suggested docs: `infra/terraform/README.md` is now accurate; add the UFW note.

### Item: Deploy pipeline (env delivery, health, rollback)

- Evidence: `deploy-do.yml:578-637` (envs), `:669-716` (`.env`), `:718-727` (token file), `:739-752` (guards), `:764-862` (deploy + health + prune), `:869-934` (HTTPS/SSH checks).
- What it does: writes `.env` from secrets without interpolation, copies config, pulls with retries, compose up with auto-revert on failure, health-gates api/web/worker, prunes only after health.
- Current controls: fail-closed gates (`deploy` `if:` block `:550-562`), attestation verification, prod-approval environment, watchdog fail-closed guard.
- Missing controls: monitoring containers not gated; METRICS_TOKEN not gated.
- Risks: alerting path loss ships green; empty token yields permanent scrape failure.
- Recommended improvement: extend gate; add token guard.
- Suggested tests: a workflow-lint that asserts the health-gate service list covers all healthchecked services.
- Suggested docs: sync `FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` §Deploy Workflow.

### Item: Manual rollback script

- Evidence: `scripts/rollback.sh:25,42-51,63-72`.
- What it does: resolves the droplet IP, SSHes in, pulls `mct-{api,worker,web}:<sha>`, compose up, health checks.
- Current controls: SHA/arg validation is minimal (no hex check like the workflow), `set -euo pipefail`.
- Missing controls: correct GHCR prefix, credential forwarding, strict host-key checking, meaningful health assertions, fatal worker check.
- Risks: documented operator tool fails during an incident (see finding).
- Recommended improvement: see finding recommendation.
- Suggested tests: shellcheck in CI; a dry-run mode that prints the resolved image refs without SSH.
- Suggested docs: mark the workflow-dispatch path as primary in `scripts/README.md`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INFRA-001 | Dockerfiles | `apps/*/Dockerfile` | digest pins, non-root, healthcheck | none found | — | keep |
| INFRA-002 | Compose | `infra/digitalocean/docker-compose.yml` | hardened 7-service stack | health gate coverage | P2 | extend gate |
| INFRA-003 | Terraform/OpenTofu | `infra/terraform/digitalocean/**` | fail-closed SSH, locking, isolated backends | live drift unverifiable | P2 | enable drift plan (CI-owned) |
| INFRA-004 | Cloud/hosting config | `dns.tf`, `cloud-init.yml`, `firewall.tf` | terraform-managed DNS/firewall | UFW create-time only | P3 | document/automate |
| INFRA-005 | Deploy scripts | `deploy-do.yml`, `scripts/rollback.sh` | fail-closed app deploy | rollback.sh broken | P2 | fix script |
| INFRA-006 | Reverse proxy | `Caddyfile*` | TLS + headers + SSE | dev lacks /metrics 404 (app-level gate) | P3 | optional parity |
| INFRA-007 | Environment examples | `infra/digitalocean/.env.example` | app examples current | droplet example missing keys | P3 | add keys |
| INFRA-008 | Runtime validators | `apps/*/src` env schemas | Zod + prod fail-closed | METRICS_TOKEN unguarded | P3 | add guard |
| INFRA-009 | Secret references | deploy envs vs schemas | 46 vars delivered, no argv secrets | matrix doc missing rows | P3 | update matrix |
| INFRA-010 | Build args | `deploy-do.yml:332-338`, web Dockerfile | public-only args | none found | — | keep |
| INFRA-011 | Container users | compose users, Dockerfile users | redis/appuser/nextjs | none found | — | keep |
| INFRA-012 | Health/readiness/liveness | compose healthchecks, deploy gate | api/web/worker gated | monitoring unchecked | P2 | extend gate |

## Findings

Verification rows keep the previous register titles and IDs (INFRA-*); new findings are marked `new`.

| Ref | Severity | Status | Title |
|---|---|---|---|
| INFRA–P1-001 | P1 | verified-fixed | SSH is open to the internet on both droplets (admin_ip_ranges default 0.0.0.0/0 and CI never overrides it) |
| INFRA–P1-002 | P1 | verified-fixed | Terraform state-locking fix is incompatible with the pinned Terraform version (use_lockfile requires >= 1.10, workflows pin 1.9) |
| INFRA–P2-003 | P2 | verified-fixed | Prometheus alert rules have no delivery path (no Alertmanager) |
| INFRA–P2-004 | P2 | verified-fixed | Dev droplet capacity is under-provisioned and the CI value drifts from dev.tfvars.example |
| INFRA–P2-005 | P2 | still-open | Operations documentation contradicts the current pipeline and configuration |
| INFRA–P2-006 | P2 | verified-fixed | Integration/security env vars referenced by the app schema are not delivered by the deploy pipeline |
| INFRA–P2-007 | P2 | verified-fixed | Redis container hardening was weakened and its password remains in process arguments |
| INFRA–P3-008 | P3 | verified-fixed | `env/prod.tfvars` is tracked despite an ignore rule that names it |
| INFRA–P3-009 | P3 | partially-fixed | Restore test uses a different Postgres major than the backup script and verifies only table counts |
| INFRA–P3-010 | P3 | still-open | `docs/RTO_RPO.md` claims Redis AOF persistence that compose does not enable |
| INFRA–P3-011 | P3 | verified-fixed | `infra/terraform/README.md` references an `aws/` directory that does not exist |
| INFRA–P3-012 | P3 | still-open | Terraform is manual-dispatch only, so the "push to trigger apply" rollback runbook step is a no-op |
| new | P2 | open | Manual rollback script cannot authenticate to GHCR and defaults to the wrong image prefix |
| new | P2 | open | Deploy health gate ignores the monitoring and reverse-proxy containers |
| new | P3 | open | infra/digitalocean/.env.example omits the alerting and internal-metrics variables the compose stack reads |
| new | P3 | open | Terraform tfvars generated/referenced at the module root are not covered by the .gitignore rule |
| new | P3 | open | Cloud-init UFW SSH allowlist is applied only at droplet creation, so narrowed allowlists leave stale host rules |
| new | P3 | open | METRICS_TOKEN has no fail-closed deploy guard; an empty token leaves the API scrape permanently down |
| new | P3 | open | Prometheus alert-rule unit tests exist but are not run in CI |

Full evidence, impact, recommendation, owner, target, confidence and verification notes are in the companion JSON (`_domains/12_infra_deployment_environment_drift.json`, 19 findings).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Operator follows stale handbook/runbook during an incident | P2 | High | Wrong concurrency/firewall/rollback action | `FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:54,137,144`; `ROLLBACK_PROCEDURES.md:199-203,219-220` | docs-sync PR |
| Manual rollback fails (wrong prefix / no registry auth) | P2 | Medium | Extended outage during rollback | `scripts/rollback.sh:25,42-51` | fix script; prefer workflow dispatch |
| Deploy green while alert delivery is down | P2 | Medium | Undetected monitoring loss (prod paged by watchdog after grace) | `deploy-do.yml:835-858`; compose `:244-307` | extend health gate |
| Empty METRICS_TOKEN → permanent MCTServiceDown noise | P3 | Medium | Alert fatigue, masked real outages | `deploy-do.yml:722-727`; `app.ts:154-171`; `prometheus.yml:20-32` | fail-closed guard |
| Live Terraform drift undetected | P2 | Medium | Infra divergence from code | `terraform-do.yml:14-15,38`; `docs/CI.md:106-110` | rotate DO token, set `TF_DRIFT_PLAN_ENABLED=true` (CI-owned) |
| Unignored module-root tfvars with live tokens | P3 | Low | Credential commit | `.gitignore:57`; `git check-ignore`; `deploy-do.yml:95` | widen ignore rule |
| Stale UFW allow rules after narrowing SSH allowlist | P3 | Low | Defense-in-depth drift (edge still blocks) | `droplet.tf:17-20`; `cloud-init.yml:24-26` | document/manage UFW |

## Recommendations

### Immediate / Release Blocking

None found in this domain at `8d299b8d`. The previous P1s (SSH fail-closed, state locking) are verified fixed; the remaining items are P2/P3.

### This Week

1. Fix `scripts/rollback.sh`: correct the GHCR prefix default, forward `GHCR_TOKEN`/`GHCR_USER` (or document a droplet-side login), make worker health fatal, require 200/301/302/307 for API/web, and verify the droplet host key. (P2)
2. Extend the deploy health gate to assert `alertmanager` (and optionally `prometheus`/`caddy`) health before pruning/returning success. (P2)

### This Month

3. Single documentation-sync PR covering every contradiction in INFRA–P2-005 and INFRA–P3-012 (handbook, rollback §4, infra README, secrets matrix, CI/RELEASING ntfy wording). (P2/P3)
4. Add `METRICS_TOKEN` to the prod fail-closed guards alongside the watchdog URL. (P3)
5. Add the missing keys to `infra/digitalocean/.env.example`. (P3)

### Later / Platform Evolution

6. Widen the tfvars ignore to the module root (or move all tfvars to `env/`) and extend `validate-terraform-env.sh`. (P3)
7. Wire `promtool check rules` + `promtool test rules` into the deploy gate. (P3)
8. Decide Redis persistence (enable AOF or correct `RTO_RPO.md`) and document the UFW create-time behavior. (P3)
9. Re-enable `terraform-do` push/PR triggers once the DO token is rotated and `prod-approval` reviewers are set (CI-owned); enable the weekly drift plan.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| One-line GHCR prefix fix in rollback.sh | Restores the documented rollback path | `scripts/rollback.sh:25` | shellcheck + dry-run |
| Add `alertmanager` to the health loop | Closes a silent monitoring-loss path | `.github/workflows/deploy-do.yml:840` | next deploy shows alertmanager asserted |
| Add METRICS_TOKEN to the prod guard | Removes a permanent-alert footgun | `.github/workflows/deploy-do.yml:739-747` | deploy fails when secret empty |
| Add missing `.env.example` keys | Manual deploys stop silently losing alerting | `infra/digitalocean/.env.example` | compose config render |
| Fix handbook concurrency/firewall lines | Cheap, high-trust doc repair | `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:54,137,144` | doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rollback script parity with the pipeline (auth, health, host key) | P2 | platform/infrastructure | S | none |
| Deploy health gate covers all healthchecked services | P2 | platform/infrastructure | S | none |
| Docs-sync PR (handbook + rollback + README + matrix) | P2 | platform/infrastructure | M | none |
| METRICS_TOKEN prod guard + scrape-up assertion | P3 | platform/infrastructure | S | secret availability |
| Droplet `.env.example` completeness + CI parity check | P3 | platform/infrastructure | S | none |
| tfvars ignore coverage + validator scope | P3 | platform/infrastructure | S | none |
| promtool rules tests in CI | P3 | platform/infrastructure | S | pinned image |
| Redis AOF decision (enable or document RDB-only) | P3 | platform/infrastructure | S | dev droplet memory check |
| UFW refresh strategy (runbook or automation) | P3 | platform/infrastructure | M | operator access |
| Live drift verification (rotate DO token, enable TF_DRIFT_PLAN_ENABLED) | P2 | platform/CI owner | S | DO token + reviewers |

## Suggested Tests

- **CI**: `docker compose -f infra/digitalocean/docker-compose.yml config` with a fixture env file (catches missing/renamed variables).
- **CI**: env-parity check that diffs `apps/api/src/config/env.ts` + `apps/worker/src/env.ts` (non-defaulted keys) against the `deploy-do.yml` envs list and printf block.
- **CI**: `promtool check rules` + `promtool test rules` (existing `prometheus.rules.test.yml`) using the pinned prom/prometheus image.
- **CI**: shellcheck (or `bash -n`) on `scripts/*.sh`, plus a rollback dry-run mode that resolves and prints image refs without SSH.
- **CI**: a health-gate coverage check that every compose service with a `healthcheck:` is asserted in the deploy gate (static parse).
- **Manual (operator)**: after the next prod deploy, confirm Alertmanager `/api/v2/alerts` shows Watchdog and that stopping alertmanager triggers the external dead-man's switch within its grace period (documented in `MONITORING_AND_ALERTING.md:343-352`).
- **Manual**: after enabling drift detection, run `terraform plan` from CI and confirm "No changes." on a clean tree.
- **Security**: extend gitleaks/pre-commit patterns for `*.tfvars` contents (do_token, cloudflare_api_token) to catch the unignored path.

## Suggested Documentation Updates

1. `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` — concurrency (`cancel-in-progress: false`), Terraform manual-dispatch, firewall ports (no 2376), prod-only migration gate, health-check semantics (200/301/302/307 + fatal worker), prune commands, Redis health via `REDISCLI_AUTH`, secret count.
2. `docs/ROLLBACK_PROCEDURES.md` — §4 state bucket/key names (`portal-terraform-state-<env>`, `digitalocean/<env>/terraform.tfstate`), remove "push to trigger", tfvars path (`env/`), Redis `-a` example.
3. `infra/digitalocean/README.md` — add alertmanager to the service table; add `alertmanager.tmpl.yml` and `metrics-token` to supporting files.
4. `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` — add `ALERTMANAGER_*` and `NTFY_ALERTS_*` rows; mark `METRICS_TOKEN` required for the scrape path; note ntfy as the primary backup notifier.
5. `docs/CI.md` and `docs/RELEASING.md` — ntfy-primary wording for backup/restore failure notification.
6. `docs/RTO_RPO.md` — Redis persistence truth (AOF vs RDB) and queue-loss semantics.
7. `infra/digitalocean/.env.example` — add METRICS_TOKEN, ALERTMANAGER_*, MFA_ENFORCEMENT_ENABLED, JIRA/JSM webhook secrets, M365_CLIENT_STATE.
8. `infra/terraform/README.md` — add a note that UFW rules are create-time only and the DO firewall is authoritative.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the live dev/prod droplet match the committed Terraform (size, firewall, UFW, DNS)? | Core drift question; unverifiable from the repo | `terraform plan` output at `8d299b8d` after token rotation |
| Is `ADMIN_IP_RANGES` actually set in dev/prod environments? | SSH remains fail-closed only if the secret exists | GitHub environment settings (operator) |
| Are `METRICS_TOKEN` and `ALERTMANAGER_*` secrets present in dev and prod? | Determines whether the alerting path and scrape are live | GitHub environment secrets (operator) |
| Are the GHCR app images public or private? | Determines the blast radius of the rollback script's missing login | GHCR package visibility (operator) |
| Does the prod `prod-approval` environment have required reviewers? | Gate effectiveness (CI-owned row CI-P1-001) | GitHub settings (operator) |
| Is `TF_DRIFT_PLAN_ENABLED` set and is `DO_API_TOKEN` valid? | Whether drift detection actually runs | GitHub variables + a dispatch run |
| What Postgres major does the Supabase project run? | Needed to choose the dump/restore client major deliberately | Supabase dashboard |
| Was the dead-man's switch ever exercised end-to-end? | "Configured" vs "exercised" (shared rules §Verification) | A recorded alertmanager-stop drill |

## Appendix

### Environment matrix (dev vs prod, repository view)

| Aspect | dev | prod |
|---|---|---|
| Branch | `develop` (or dispatch target dev) | `main` (or dispatch target prod) |
| Domains | `app/api/www.mainecybertech.us` | `app/api/www.mainecybertech.com` |
| Droplet name / size | `mct-portal-dev` / `s-1vcpu-2gb` | `mct-portal-prod` / `s-2vcpu-2gb` |
| Terraform backend | `portal-terraform-state-development` / `digitalocean/dev/terraform.tfstate` | `portal-terraform-state-production` / `digitalocean/prod/terraform.tfstate` |
| GitHub environment | `dev` (no approval) | `prod` (migrations/read-only) + `prod-approval` (deploy/apply) |
| TLS | `tls internal` (Caddyfile.dev) | Cloudflare Origin CA certs (Caddyfile.prod) |
| Test accounts page | enabled (`NEXT_PUBLIC_TEST_ACCOUNTS_ENABLED=true`) | disabled |
| Watchdog fail-closed | warns | deploy fails when empty |
| Migrations gate | skipped | required before deploy |
| E2E gate | skipped | required before deploy |

### Hardening checklist

- [x] Non-root container users (redis/appuser/nextjs)
- [x] Digest-pinned third-party images; app images SHA-tagged + attestation-verified
- [x] Capability drop + no-new-privileges on every service
- [x] Read-only rootfs where feasible + tmpfs for writable paths
- [x] Memory + PID limits on every service; bounded container logs
- [x] Healthchecks on redis/api/worker/alertmanager/caddy
- [ ] Healthcheck coverage enforced by the deploy gate (api/web/worker only today)
- [x] Secrets delivered via env/printf, never argv or build args
- [x] METRICS_TOKEN bearer gate on `/metrics`, token file 0400 owned by container user
- [ ] Fail-closed guard for an empty METRICS_TOKEN
- [x] Alertmanager delivery + external dead-man's switch with prod fail-closed guard
- [ ] Alert rules unit tests run in CI
- [x] SSH fail-closed in Terraform + CI guard
- [ ] UFW refresh strategy for narrowed allowlists
- [ ] tfvars ignore coverage at the module root
- [ ] Documented + tested manual rollback path (script currently broken)

### Unverifiable items (marked, not asserted)

- Live droplet state, UFW contents, DO firewall state, Terraform state contents.
- GitHub environment secrets/variables and `prod-approval` reviewer configuration.
- GHCR package visibility and whether the referenced image tags still exist for old SHAs.
- Whether the dead-man's switch has been exercised (no dated drill artifact found in the repository).

### Commands run (exact, read-only)

```
git log --oneline -3
git status --short
git ls-files infra/terraform/digitalocean/env/
git ls-files | grep -i tfvars
git ls-files -s scripts/rollback.sh infra/digitalocean/redis-entrypoint.sh
git check-ignore -v infra/terraform/digitalocean/dev.tfvars infra/terraform/digitalocean/env/dev.tfvars
grep -rn "NTFY" --include="*.yml" --include="*.md" --include="*.ts" .
grep -rn "TF_DRIFT_PLAN_ENABLED" .
grep -rn "promtool|rules.test" .github/ package.json
python3 (envs-list vs printf vs compose ${VAR} comparison)
bash -c 'set -euo pipefail; echo "$UNSET" | cat || true; echo REACHED'
```
