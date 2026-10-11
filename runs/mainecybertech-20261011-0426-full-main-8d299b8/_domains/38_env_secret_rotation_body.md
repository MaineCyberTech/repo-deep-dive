# Environment and Secret Rotation Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` — read-only worktree `/tmp/opencode/mct-audit-target`
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11 (UTC)
- Auditor: domain subagent `38_env_secret_rotation` (area SECRET); read-only, no installs/builds/tests, no network
- Area code: SECRET
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/38_env_secret_rotation.md`
- Scope limitations: live GitHub environment/secret scoping, `gh secret list` timestamps, and droplet `.env`
  contents are not inspectable from the repository (marked `Unknown`); `gitleaks` is not installed on the
  audit host (deterministic lens DET-P3-001), so the committed scanner configuration was reviewed statically
  and with `grep` pattern checks instead of executed. Secret values were never printed; only names and
  `path:line` references appear.

## Scope

Reviewed at `8d299b8d`: the four `.env.example` templates; `docs/ENVIRONMENT_VARIABLES.md`,
`docs/SECRETS_ROTATION.md`, `docs/JWT_ROTATION.md`, `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`,
`docs/INCIDENT_RESPONSE.md`, `docs/DATA_BREACH_RESPONSE.md`; runtime validators (`apps/api/src/config/env.ts`,
`apps/worker/src/env.ts`, `apps/web/lib/env.ts`, `apps/api/src/lib/rls-startup-check.ts`); deploy/CI secret
handling (`deploy-do.yml`, `terraform-do.yml`, `build-push.yml`, `secret-scan` composite,
`secret-history-scan.yml`, `secret-rotation-reminder.yml`, backup workflows, `e2e.yml`); both compose files;
Terraform variables/artifacts; local dev scripts; `.gitignore`/`.dockerignore` exclusion rules; the previous
run's SECRET rows and the cross-domain rows whose subject matter is secret rotation/evidence.

Not reviewed: live GitHub environments and reviewers; the droplet and hosted Supabase; runtime logs; actual
secret values (never printed); the `_domains` outputs of sibling domains beyond cross-referencing.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/.env.example`, `apps/worker/.env.example`, `apps/web/.env.example`, `infra/digitalocean/.env.example` | templates | Documented config surface | Placeholders only; no real values |
| `apps/api/src/config/env.ts:19-108` | runtime validator | Zod schema + production fail-closed assertions | 38 keys; `assertProductionSecrets`/`assertProductionTurnstile` |
| `apps/worker/src/env.ts:5-107` | runtime validator | Worker schema + superRefine guards | 33 keys; prod forbids `QUEUE_BACKEND=inline` |
| `apps/web/lib/env.ts:3-127` | client validator | `NEXT_PUBLIC_*` handling | Prod throw at :87-92 |
| `apps/api/src/middleware/auth.ts:46-134`; `apps/api/src/routes/auth.ts:113,143` | JWT handling | Multi-secret verify; token issuance | API verifies only; Supabase signs |
| `docs/SECRETS_ROTATION.md` | policy | 48-entry inventory, procedures, emergency, log | Log has one row (:222-228) |
| `docs/JWT_ROTATION.md` | policy | Zero-downtime JWT procedure | References `JWT_EXPIRY` (:50) |
| `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` | inventory | Per-workflow secret matrix | Env-scope notes at :16-20, :150-151 |
| `.github/workflows/deploy-do.yml:571-727` | CI/CD | Prod deploy secret path | Job environment `prod-approval`; `.env` 0600 |
| `.github/workflows/terraform-do.yml:66-159` | CI/CD | tfvars + plan artifact | `tfplan` uploaded as artifact |
| `.github/actions/secret-scan/action.yml`; `secret-history-scan.yml` | CI/CD | Diff + full-history scans | Redacted output; checksum-pinned gitleaks |
| `infra/digitalocean/docker-compose.yml` | deploy config | Runtime secret wiring | REDIS/ALERTMANAGER/M365/RLS keys |
| `.gitignore:19-23,57`; `.dockerignore:20-22`; `scripts/ci/verify-gitleaks-config.sh` | exclusions | Secret-file exclusion rules | `.env*` ignored; examples kept |

## Verification Performed

| # | Command (read-only) | Observed result |
|---|---|---|
| 1 | `git -C /tmp/opencode/mct-audit-target rev-parse HEAD; git status --porcelain` | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`; worktree clean |
| 2 | `grep -rn "M365_WEBHOOK_SECRET" .` (excl. `docs/audits`) | Only comments/doc notes: `env.ts:58`, `.env.example:33`, `ENVIRONMENT_VARIABLES.md:78`, `SECRETS_ROTATION.md:54`, matrix `:80` — no declaration, no consumer |
| 3 | `grep -n "M365_CLIENT_STATE" deploy-do.yml docker-compose.yml webhooks.ts env.ts` | Forwarded (`:597`), written (`:689`), wired (`compose:90`), consumed (`webhooks.ts:576`); timing-safe compare at `:592` |
| 4 | Programmatic diff: `secrets.X` in workflows vs backticked names in `docs/SECRETS_ROTATION.md` / matrix | 68 workflow secret names; **20 absent from the rotation inventory**; 13 absent from the matrix |
| 5 | `grep -c "REDIS_PASSWORD" docs/SECRETS_ROTATION.md` | `0` — required prod secret (`compose:44,76-77,139-140`) has no rotation row |
| 6 | `grep -n "ALERTMANAGER\|NTFY_ALERTS" deploy-do.yml db-backup.yml` + `git log` | 6 alertmanager secrets + 3 ntfy secrets used; added 2026-10-11 (`ed53f041`, `2af00893`); absent from both docs |
| 7 | `sed -n '222,228p' docs/SECRETS_ROTATION.md` | Rotation Log contains only `(Initial deployment) \| All \| — \| No \| dev, prod`; no dated rotation |
| 8 | `grep -rn "JWT_EXPIRY" .` (excl. node_modules) | 3 hits, all documentation; no code/config key exists |
| 9 | `grep -rn "jwt.sign" apps packages` | No matches — the API does not sign JWTs; tokens come from Supabase (`routes/auth.ts:113,143`) |
| 10 | `grep -n "environment:" .github/workflows/*.yml` | deploy prod job `prod-approval` (`deploy-do.yml:571`); migrations/plan `prod`; backups `dev` |
| 11 | `find . -name "secret_rotation_runbook*"` | Only `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/secret_rotation_runbook.md`; nothing at `docs/` |
| 12 | `grep -rn "escrow" docs/*.md` | Only `SECRETS_ROTATION.md:82,99` referencing an "agreed escrow location" that is never defined |
| 13 | `git ls-files \| grep tfvars; git check-ignore -v infra/terraform/digitalocean/env/prod.tfvars` | Only `*.tfvars.example` tracked; `.gitignore:57` matches the produced file (exit 0) |
| 14 | `grep -n "chmod 600\|chmod 400\|chown 65534" deploy-do.yml` | `.env` 0600 (`:717`), metrics token 0400/65534 (`:726-727`), TLS key 0600 (`:770`), temp SSH key 0600 (`:882`) |
| 15 | Python parity check: Zod schema keys vs `.env.example` keys (api/worker/web) | 0 missing in all three (API 38/38, worker 33/33, web 13/13); API example additionally documents `APP_DOMAIN`/`API_DOMAIN` |
| 16 | `grep -rlnE "AKIA[0-9A-Z]{16}\|ghp_[0-9a-zA-Z]{36}\|sk_live_"` (excl. node_modules/.git) | No tracked matches; no real secret found in the tree |
| 17 | `git log --oneline -- docs/SECRETS_ROTATION.md docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` | Both last updated 2026-10-04 (`3090f768`, `6674b3e8`); newer secrets never inventoried |
| 18 | `scripts/ci/verify-gitleaks-config.sh` | Not run — `gitleaks` not installed (DET-P3-001); config reviewed statically |

### Verification duty (previous run, `mainecybertech-20261004-full-main-9c0b88c`)

All 9 SECRET rows were re-checked at `8d299b8d`; 4 adjacent rows (CONF/IR) whose subject matter is secret
inventory/rotation evidence were also re-checked and are emitted here. Status changes vs the previous
register: `SECRET-P1-001` partially-fixed→**verified-fixed**, `SECRET-P3-002` verified-fixed→**partially-fixed**;
the rest keep their prior status. `ACM-P2-007` (webhook signing secrets plaintext) is in this domain's scope
but was already re-verified with current evidence by the ACM (24) and WH (27) domains — left to them to
avoid duplicate rows. `SEC-P2-001`/`SECRET-P2-003/004` were also re-verified by the SEC/SC domains; this
domain re-verifies independently.

| Previous row | Title | Status at 8d299b8d | One-line outcome |
|---|---|---|---|
| SECRET-P1-001 | M365 webhook secret is dead config… | verified-fixed | Dead key gone; `M365_CLIENT_STATE` deployed, consumed, constant-time |
| SECRET-P1-002 | Deploy pipeline does not write several secret-class env vars… | verified-fixed | All previously missing keys written by `envs:`+`printf`, incl. Turnstile |
| SECRET-P2-001 | Secret rotation inventory and GitHub matrix lag… | partially-fixed | SCHEDULE_DISPATCH_TOKEN added; 20 other names still uncovered |
| SECRET-P2-002 | Rotation reminder workflow referenced in docs does not exist… | partially-fixed | Workflow exists; Rotation Log still has no exercised entry |
| SECRET-P2-003 | Secret scanning is diff-scoped only… | verified-fixed | Weekly/manual full-history gitleaks 8.30.1 + verifier + artifact |
| SECRET-P2-004 | Produced Terraform `prod.tfvars` is tracked… | verified-fixed | Untracked; ignore rule matches; only `.example` committed |
| SECRET-P3-001 | Worker `.env.example` omits `APP_BASE_URL` | verified-fixed | Documented at `apps/worker/.env.example:41` |
| SECRET-P3-002 | Web runtime validator can silently fall back to a localhost API URL | partially-fixed | Prod throw exists, but the Dockerfile ENV default pre-populates the var |
| SECRET-P3-003 | No IT-level break-glass / emergency credential revocation runbook… | still-open | No runbook, no drill evidence, escrow undefined |
| CONF-P2-001 | Workflow-scope PAT SCHEDULE_DISPATCH_TOKEN omitted… | verified-fixed | Rotation row #48 + matrix row + workflow consumer |
| CONF-P3-001 | Secret rotation policy has no evidence any secret was ever rotated | still-open | Rotation Log single row; no dated artifact |
| IR-P2-004 | Secrets rotation is documented but has no exercised evidence | still-open | Same evidence as CONF-P3-001 |

## Executive Summary

Secret handling at `8d299b8d` is materially stronger than at the previous full run. The API fails closed at
boot in production for PII encryption and CAPTCHA keys; the deploy pipeline forwards ~50 secrets as
environment variables (never interpolated into the remote script) and writes the droplet `.env` with mode
0600; the metrics token is written 0400 to the Prometheus container user; M365/Jira/JSM webhooks verify
credentials in constant time over raw bytes and fail closed with 501 when unconfigured; `JWT_SECRET` supports
comma-separated zero-downtime verification; diff secret scanning runs on PRs/pushes and a checksum-pinned
gitleaks job now scans full history weekly with a negative-fixture guard; and `.env.example` files match all
three runtime schemas.

The remaining risk is concentrated in the **documented rotation/revocation path**, not the runtime wiring:

1. **The rotation and emergency procedures target the wrong GitHub environment (P1).** `SECRETS_ROTATION.md`
   and `JWT_ROTATION.md` say `--env prod`, but the prod deploy job runs under `prod-approval` and the backup
   workflows run under `dev`; an operator following the runbook can rotate a value the consuming job never
   reads — silently, during an incident.
2. **The rotation inventory still lags the workflows (P2).** 20 secret names (including required
   `REDIS_PASSWORD`, today's `ALERTMANAGER_*`/`NTFY_ALERTS_*`, and the SSH host-key pins) are absent from the
   inventory; 13 are absent from the matrix.
3. **No exercised rotation evidence (P2/P3).** The Rotation Log has one undated "Initial deployment" row;
   the reminder workflow exists but no rotation or revocation drill artifact does.
4. **JWT rotation does not rotate the signer (P2).** The API only verifies; Supabase signs. The procedure
   rotates the API-side copy and references a `JWT_EXPIRY` key that does not exist.
5. **Delivery artifacts (P2).** The Terraform `tfplan` artifact embeds the DO/Cloudflare token values and is
   downloadable by any repo reader for its retention window.
6. **Break-glass is still undefined (P3).** No IT runbook, no escrow location, and `INCIDENT_RESPONSE.md`
   points at a `secret_rotation_runbook.md` that exists only inside an old audit-run folder (P2 doc defect).

Recommended next actions: fix the environment mapping in the rotation docs and add a post-rotation
verification step; reconcile the inventory/matrix with a CI parity check; run one real (dev) rotation drill
and record it; rewrite the JWT procedure around the Supabase signing secret; and either encrypt the tfplan
artifact or stop uploading it.

## Inventory

### Environment variable inventory (by consumer, non-secret config included)

| Consumer | Where set | Secret-class keys | Notes |
|---|---|---|---|
| API (`apps/api`) | droplet `.env` (from GitHub env secrets) | `SUPABASE_*`, `JWT_SECRET`, `STRIPE_*`, `SMTP_*`, `JIRA_WEBHOOK_SECRET`, `JSM_*`, `M365_CLIENT_STATE`, `METRICS_TOKEN`, `TURNSTILE_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `REDIS_PASSWORD`, `PUBLIC_*_WEBHOOK_URL`, `RLS_*`, `MFA_ENFORCEMENT_ENABLED` | 38 schema keys; production assertions at `env.ts:85-108` |
| Worker (`apps/worker`) | droplet `.env` | `SUPABASE_*`, `STRIPE_SECRET_KEY`, `JIRA_API_TOKEN`, `JSM_API_TOKEN`, `M365_CLIENT_SECRET`, `SMTP_PASS`, `REDIS_PASSWORD` | 33 schema keys; `QUEUE_BACKEND=inline` refused in prod |
| Web (`apps/web`) | Docker build args + runtime env | none (all `NEXT_PUBLIC_*` are public by design) | `NEXT_PUBLIC_TEST_ACCOUNT_PASSWORD` is dev-only and never passed by `deploy-do` |
| Deploy job (`deploy-do`) | GitHub env `prod-approval`/`dev` | ~50 forwarded secrets | `.env` rewritten every deploy, 0600 |
| Terraform (`terraform-do`) | GitHub env `prod`/`dev` + tfvars on runner | `DO_API_TOKEN`, `CLOUDFLARE_API_TOKEN`, Spaces keys, `ADMIN_IP_RANGES` | plan artifact uploaded |
| Backups (`db-backup`, `storage-backup`, `db-restore-test`) | GitHub env `dev` | `SUPABASE_DB_URL`, `AWS_*`/Spaces, `BACKUP_ENCRYPTION_KEY`, `NTFY_ALERTS_*`, `SLACK_WEBHOOK_URL` | encryption enforced (`REQUIRE_BACKUP_ENCRYPTION=1`) |
| Observability | droplet `.env` | `ALERTMANAGER_WATCHDOG/CRITICAL/DEFAULT_WEBHOOK_URL`, `ALERTMANAGER_SLACK_API_URL`, `ALERTMANAGER_WEBHOOK_USER/PASS` | dead-man's switch; fail-closed in prod deploy |

### Secret classification (required companion artifact)

| Class | Examples | Storage | Rotation source of truth |
|---|---|---|---|
| Application auth | `JWT_SECRET` | GitHub env secret → droplet `.env` | `docs/JWT_ROTATION.md` (incomplete, see finding) |
| Data keys (no-schedule) | `FIELD_ENCRYPTION_KEY`, `BACKUP_ENCRYPTION_KEY` | GitHub env secret | `SECRETS_ROTATION.md:62-99` re-encryption procedures |
| Supabase | `SUPABASE_URL/ANON_KEY/SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`, `SUPABASE_ACCESS_TOKEN` | GitHub env secrets | Supabase dashboard |
| Payments | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | GitHub env secrets | Stripe dashboard |
| Integrations | `JIRA_*`, `JSM_*`, `M365_*`, `SMTP_*` | GitHub env secrets | provider consoles |
| Inbound webhooks | `JIRA_WEBHOOK_SECRET`, `JSM_WEBHOOK_SECRET`, `M365_CLIENT_STATE` | GitHub env secrets | 90-day entries present |
| Observability | `METRICS_TOKEN`, `ALERTMANAGER_*`, `NTFY_ALERTS_*` | GitHub env secrets | `METRICS_TOKEN` only; others missing |
| Infrastructure | `DO_*`, `CLOUDFLARE_*`, `CI_SSH_PRIVATE_KEY`, `DO_SSH_HOST_FINGERPRINT`, `DO_SSH_HOST_KEY`, `CF_ORIGIN_*`, `ADMIN_IP_RANGES` | GitHub env secrets | partially inventoried |
| Non-secret config forwarded as secrets | `RLS_READS/WRITES_ENABLED`, `MFA_ENFORCEMENT_ENABLED`, `SMTP_HOST/PORT`, `EMAIL_FROM`, `*_SERVICEDESK_ID`, `*_REQUEST_TYPE_ID` | GitHub env secrets | classification gap (see SECRET-P2-001) |
| Client-exposed | `NEXT_PUBLIC_*` | build args, inlined in bundle | public by design |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| `.env.example` | 5 | `apps/*/.env.example`; programmatic parity vs all three schemas (0 missing) | None material | Keep; add parity guard |
| Env docs | 4 | `docs/ENVIRONMENT_VARIABLES.md` covers app vars incl. M365/RLS/MFA | Observability/deploy keys not in it; ALERTMANAGER lives only in `MONITORING_AND_ALERTING.md` | Add a deploy/observability section or cross-link |
| Runtime validators | 4 | `env.ts:19-108`, worker `env.ts:5-66`, web `lib/env.ts:87-92` | Web guard bypassed by Dockerfile default; no placeholder/default-value check for prod keys | Fix Dockerfile default; add tests |
| CI/deploy/local secrets | 4 | `deploy-do.yml:578-727`; secret-scan composite; history scan | Env-scope docs defect (new finding); history scan has no failure notifier (SC-owned) | Correct docs; add notifier |
| API/JWT/DB/Supabase/webhook/OAuth/email/push/Sentry/payment/cloud/GitHub keys | 3 | Rotation inventory rows 1-48; compose wiring | 20 names uncovered incl. `REDIS_PASSWORD`; webhook endpoint secrets plaintext (ACM/WH-owned) | Reconcile inventory; encrypt/rotate webhook secrets |
| Naming consistency | 3 | `DO_SSH_FINGERPRINT` vs `DO_SSH_HOST_FINGERPRINT`/`DO_SSH_HOST_KEY`; `S3_BUCKET` vs `S3_BACKUP_BUCKET` | Two undocumented deploy-critical secrets; legacy name kept for compatibility | Rename/document with an explicit mapping |
| Client-exposed vars | 4 | `apps/web/lib/env.ts:3-17`; `deploy-do.yml:332-338` | Test password default "1" if the dev flag ever reaches prod | Keep prod flag forced false; add a test |
| Rotation/revocation docs | 3 | `SECRETS_ROTATION.md`; `JWT_ROTATION.md`; emergency section | Wrong env scope; JWT signer gap; `JWT_EXPIRY` nonexistent; broken runbook ref | Rewrite per findings |
| Break-glass | 2 | `INCIDENT_RESPONSE.md:67,115`; escrow references | No IT runbook, no escrow location, no drill | Create + drill |

## Detailed Review

### Item: `.env.example` and runtime validators

- Evidence: `apps/api/.env.example:1-55`; `apps/worker/.env.example:1-44`; `apps/web/.env.example:1-22`;
  `apps/api/src/config/env.ts:19-74`; `apps/worker/src/env.ts:5-43`; `apps/web/lib/env.ts:3-17`.
- What it does: templates document every schema key with placeholders; validators enforce types and
  production fail-closed checks.
- Current controls: API requires `JWT_SECRET` ≥32 chars and `SUPABASE_*`; production throws without a valid
  32-byte `FIELD_ENCRYPTION_KEY` (`env.ts:100-108`) or `TURNSTILE_SECRET_KEY` (`env.ts:85-93`); worker
  refuses `QUEUE_BACKEND=inline` in production; `rls-startup-check.ts` refuses an empty RLS read allow-list
  in production.
- Missing controls: automated parity between schemas, examples, and docs; web production guard is defeated by
  the Dockerfile default (see SECRET-P3-002); no check that a production secret is not a placeholder value
  (e.g. `infra/digitalocean/.env.example`'s `JWT_SECRET=your-jwt-secret` would fail the ≥32 check, so the
  risk is low).
- Suggested tests: schema↔example parity test; build a web image without the build arg and assert the build
  fails.

### Item: CI/deploy/local secret flow

- Evidence: `deploy-do.yml:578-637` (envs), `:669-716` (printf writer), `:717` (chmod 600),
  `:722-727` (metrics token 0400), `:881-891` (temp SSH key 0600, pinned host key); `e2e.yml:96-118`
  (throwaway local secrets); `db-backup.yml:44-46` (`REQUIRE_BACKUP_ENCRYPTION=1`).
- What it does: forwards secrets as env vars (values never interpolated into remote shell), rewrites the
  droplet `.env` each deploy, writes the Prometheus credential file for the container user.
- Current controls: strong; diff secret scan on PR/push (`secret-scan/action.yml:15-55`) with redacted
  output and tracked-`.env` rejection; weekly full-history gitleaks; pre-commit hook.
- Missing controls: the rotation docs' environment mapping (new finding); history scan not wired to the
  deploy gate and has no failure notification (SC-owned finding).

### Item: JWT handling

- Evidence: `apps/api/src/middleware/auth.ts:46-52,100-134`; `apps/api/src/routes/notifications.ts:83-101`;
  `apps/api/src/routes/auth.ts:113,143`; `docs/JWT_ROTATION.md:4,50`; `docs/SECRETS_ROTATION.md:101-128`.
- What it does: verifies HS256 tokens against a comma-separated list (first = preferred), falls back to
  Supabase `getUser` with a 5s timeout; SSE re-validates every 5 minutes.
- Current controls: algorithm pinned to HS256; constant-time webhook compares; sessions issued by Supabase.
- Missing controls: the procedure does not rotate the Supabase project JWT secret (the actual signer) and
  references a nonexistent `JWT_EXPIRY` (see new finding).
- Suggested tests: token signed with a removed secret must be rejected; after rotation a token signed with
  the old Supabase secret must fail.

### Item: Rotation inventory and matrix

- Evidence: `docs/SECRETS_ROTATION.md:9-58`; `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:24-123`.
- What it does: lists 48 secrets with frequency and source; matrix maps secrets to workflows/environments.
- Current controls: SCHEDULE_DISPATCH_TOKEN, webhook keys, M365_CLIENT_STATE, Turnstile, metrics, PII key
  added since the previous run; quarterly reminder workflow.
- Missing controls: 20 workflow-referenced names absent from the inventory; 13 absent from the matrix;
  several non-secrets classified as secrets (see SECRET-P2-001).
- Suggested tests: CI parity check that every `secrets.X` used in `.github/` has an inventory row.

### Item: Client-exposed variables

- Evidence: `apps/web/lib/env.ts:3-17,66-125`; `deploy-do.yml:332-338`; `test-accounts.ts:8-18`;
  `app/(public)/test-accounts/page.tsx:454,481,506`.
- What it does: only public values are `NEXT_PUBLIC_*`; the dev test-accounts page is gated client- and
  server-side and never enabled by the prod build (`TEST_ACCOUNTS_ENABLED=false` for prod).
- Current controls: no server secret is prefixed `NEXT_PUBLIC_`; production API URL guard exists.
- Missing controls: the test password defaults to `"1"` when the page is enabled; acceptable only because
  the prod flag is forced false and the server gate also requires localhost/.us.

### Item: Break-glass and revocation

- Evidence: `docs/INCIDENT_RESPONSE.md:67,107,115`; `docs/DATA_BREACH_RESPONSE.md:171-227`;
  `docs/SECRETS_ROTATION.md:82-83,99,183-209`.
- What it does: incident doc mandates "revoke first, investigate after"; breach doc has per-secret
  containment playbooks; rotation policy has an emergency procedure.
- Missing controls: no IT-level break-glass runbook at the referenced path; escrow location undefined; no
  drill/tabletop evidence; emergency JWT step depends on the environment-scope defect above.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SECRET-001 | `.env.example` | `apps/*/.env.example`; parity check | Complete, placeholders only | No CI parity guard | P3 | Add parity script to validate.yml |
| SECRET-002 | Env docs | `docs/ENVIRONMENT_VARIABLES.md` | App vars documented | Observability/deploy keys absent | P3 | Add section/cross-link |
| SECRET-003 | Runtime validators | `env.ts:19-108`; worker `env.ts`; web `lib/env.ts` | Zod + prod fail-closed | Web guard bypassed by Dockerfile default | P2 | Remove default; test |
| SECRET-004 | CI/deploy/local secrets | `deploy-do.yml:578-727`; scans | Env-var forwarding, 0600 files, scans | Env-scope doc defect | P1 | Fix docs + verify step |
| SECRET-005 | Key inventory coverage | `SECRETS_ROTATION.md:9-58` | 48 entries | 20 names uncovered | P2 | Reconcile + CI check |
| SECRET-006 | Naming consistency | `DO_SSH_*`, `S3_*` | Legacy aliases tolerated | Confusing/undocumented | P3 | Rename + mapping doc |
| SECRET-007 | Client-exposed vars | `apps/web/lib/env.ts`; deploy build args | Public-only `NEXT_PUBLIC_*` | Dev password default "1" | P3 | Keep prod flag forced; test |
| SECRET-008 | Rotation/revocation docs | `SECRETS_ROTATION.md`; `JWT_ROTATION.md` | Detailed procedures | Wrong env; JWT signer; no evidence | P1/P2 | Rewrite; drill |
| SECRET-009 | Break-glass | `INCIDENT_RESPONSE.md` | Emergency section exists | No runbook/escrow/drill | P3 | Create + drill |

## Findings

The authoritative rows (severity, evidence, impact, recommendation, owner, target, confidence, status, note)
are in `_domains/38_env_secret_rotation.json`. Summary of all 17:

| # | Finding | Sev | Status |
|---|---|---|---|
| 1 | M365 webhook secret is dead config while the real M365 auth value is undocumented and undeployed | P1 | verified-fixed |
| 2 | Deploy pipeline does not write several secret-class env vars the API schema and compose reference | P1 | verified-fixed |
| 3 | Secret rotation inventory and GitHub matrix lag the schema/compose; seven keys uncovered | P2 | partially-fixed |
| 4 | Rotation reminder workflow referenced in docs does not exist; rotation log shows no real rotation | P2 | partially-fixed |
| 5 | Secret scanning is diff-scoped only; no full-history scan artifact | P2 | verified-fixed |
| 6 | Produced Terraform `prod.tfvars` is tracked despite `.gitignore` intending to exclude it | P2 | verified-fixed |
| 7 | Worker `.env.example` omits `APP_BASE_URL` | P3 | verified-fixed |
| 8 | Web runtime validator can silently fall back to a localhost API URL | P3 | partially-fixed |
| 9 | No IT-level break-glass / emergency credential revocation runbook, and no revocation drill evidence | P3 | still-open |
| 10 | Workflow-scope PAT SCHEDULE_DISPATCH_TOKEN omitted from secret inventory and rotation policy | P2 | verified-fixed |
| 11 | Secret rotation policy has no evidence any secret was ever rotated | P3 | still-open |
| 12 | Secrets rotation is documented but has no exercised evidence | P2 | still-open |
| 13 | **NEW** Rotation and emergency procedures target the wrong GitHub environment for the prod deploy and backup workflows | P1 | open |
| 14 | **NEW** Incident response points at a secret-rotation runbook that is not in `docs/` | P2 | open |
| 15 | **NEW** Terraform plan artifacts carry sensitive variable values off the runner | P2 | open |
| 16 | **NEW** JWT rotation runbook rotates the API verification copy, not the Supabase signing secret, and references a nonexistent `JWT_EXPIRY` | P2 | open |
| 17 | **NEW** No automated `.env.example` ↔ runtime schema ↔ docs parity check | P3 | open |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Emergency rotation silently does not reach prod | P1 | Medium | Compromised credential stays live | Finding 13; `deploy-do.yml:571` vs `SECRETS_ROTATION.md:191` | Correct env mapping; verify after rotation |
| Uncovered secrets never rotate | P2 | High | Long-lived credentials (REDIS, ntfy relay, alerting) | Finding 3; 20 names uncovered | Inventory reconciliation + CI parity |
| No rotation/drill evidence | P2 | High | Untested revocation path in a real incident | Findings 4, 11, 12 | Run a dev drill; record it |
| JWT compromise not truly revoked | P2 | Medium | Attacker tokens remain valid | Finding 16; `routes/auth.ts:113,143` | Rotate Supabase JWT secret; force logout |
| Infra tokens exposed via plan artifact | P2 | Low-Medium | DO/Cloudflare account compromise | Finding 15; `terraform-do.yml:154-159` | OIDC or encrypted plan |
| On-call cannot find the revocation runbook | P2 | Medium | Slower containment | Finding 14; `INCIDENT_RESPONSE.md:115` | Publish runbook to `docs/` |
| Web prod build silently points at localhost | P3 | Low | Broken deployment | Finding 8; `apps/web/Dockerfile:17-23` | Remove Dockerfile default |
| Env drift recurs | P3 | Medium | Missing config in prod | Finding 17 | Add parity check |

## Recommendations

### Immediate / Release Blocking

1. Correct the GitHub-environment mapping in `docs/SECRETS_ROTATION.md` (and `docs/JWT_ROTATION.md`) to name
   the environment each consuming job actually uses: `prod-approval` for the prod deploy job and prod
   Terraform apply, `prod` for migrations/plan, `dev` for the backup workflows. Add a post-rotation
   verification step (`gh secret list --env <env>` and a deploy that proves the value landed) (Finding 13).

### This Week

2. Reconcile `docs/SECRETS_ROTATION.md` and `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` with the workflow
   secret set (add `REDIS_PASSWORD`, `ALERTMANAGER_*`, `NTFY_ALERTS_*`, `DO_SSH_HOST_FINGERPRINT`,
   `DO_SSH_HOST_KEY`, `ADMIN_IP_RANGES`, `SLACK_WEBHOOK_URL`, `CHROMATIC_PROJECT_TOKEN`, `E2E_JWT_SECRET`,
   `S3_BACKUP_BUCKET`; reclassify non-secret config) (Finding 3).
3. Publish the secret-rotation/revocation runbook into `docs/` and link it from `docs/INDEX.md`; add
   `docs/INCIDENT_RESPONSE.md` to the docs-link guard (Finding 14).
4. Rewrite the JWT procedure around the Supabase project JWT secret, replace `JWT_EXPIRY` with the real token
   lifetime, and add a negative test (old-secret token rejected after removal) (Finding 16).

### This Month

5. Run one real rotation drill in `dev` (a non-critical secret), record date/operator/run URL in the Rotation
   Log, and add a drill row to the quarterly reminder checklist (Findings 4, 11, 12).
6. Stop uploading the plaintext `tfplan` artifact: apply from the same protected job, encrypt the artifact, or
   move to OIDC/short-lived infra credentials (Finding 15).
7. Fix the web production guard so a Docker build without `NEXT_PUBLIC_API_URL` fails (remove the Dockerfile
   ENV defaults or make the guard check the build arg) (Finding 8).
8. Add the env-parity CI check and a test that the dev test-accounts page cannot be enabled in prod
   (Findings 1, 17).

### Later / Platform Evolution

9. Encrypt/rotate tenant webhook signing secrets (`webhook_endpoints.secret`) with an expiry/rotation
   endpoint (owned by ACM/WH domains; cross-referenced here).
10. Add a scheduled-scan failure notifier (owned by SC domain) and wire the full-history scan result into the
    release evidence bundle.
11. Consider GitHub OIDC for DigitalOcean/Cloudflare to retire long-lived infra tokens entirely.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix `--env prod` → `--env prod-approval` in rotation/emergency steps | Rotation actually reaches prod | `docs/SECRETS_ROTATION.md`, `docs/JWT_ROTATION.md` | Dry-run `gh secret list --env prod-approval` |
| Add the 10 missing inventory rows | Operators can find every secret | `docs/SECRETS_ROTATION.md`, matrix | `grep` each name returns a row |
| Link the runbook from `docs/INDEX.md` | On-call finds it during an incident | `docs/INDEX.md`, runbook file | Docs link guard green |
| Replace `JWT_EXPIRY` with the Supabase session lifetime | Removes a false knob | `docs/JWT_ROTATION.md`, `docs/SECRETS_ROTATION.md` | Review |
| Delete the web Dockerfile `ENV NEXT_PUBLIC_API_URL` default | Makes the prod guard real | `apps/web/Dockerfile` | Build without the arg fails |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Correct environment mapping + verify step | P1 | platform/security | S | none |
| Inventory/matrix reconciliation + CI parity | P2 | platform/security | S/M | none |
| Publish revocation runbook + escrow definition | P2 | platform/security | S | owner decision on escrow |
| JWT procedure rewrite (Supabase signer) | P2 | API platform | S | Supabase admin access |
| tfplan artifact handling | P2 | platform/infra | S/M | OIDC or artifact encryption decision |
| Rotation drill in dev + log entry | P2 | platform/security | S | operator |
| Web guard/Dockerfile fix | P3 | web platform | S | none |
| Env parity check | P3 | platform/CI | S | none |
| Tenant webhook secret encryption/rotation | P2 | API platform | M | schema migration |

## Suggested Tests

- **Unit:** `assertProductionSecrets`/`assertProductionTurnstile` (exist, `apps/api/src/__tests__/env*.test.ts`);
  add a web test that `getClientEnv()` throws when `NODE_ENV=production` and the URL is absent, and an image
  build test that the Dockerfile cannot supply a default.
- **Integration:** rotate a dev secret end-to-end (set → deploy → health check → feature check) and record
  the run; assert the old value is no longer accepted.
- **Security/regression:** a scratch PR adding a platform-format token (`dop_v1_…`, `sbp_…`, `npm_…`) must
  fail the diff scan (SC-owned gap); a synthetic key must still be detected by `verify-gitleaks-config.sh`.
- **CI:** parity check — every `secrets.X` in `.github/` has a row in `SECRETS_ROTATION.md`; every schema key
  appears in the matching `.env.example`.
- **Manual:** walk `docs/INCIDENT_RESPONSE.md` §4.2 as written and confirm every referenced document resolves.

## Suggested Documentation Updates

- `docs/SECRETS_ROTATION.md` — environment mapping, missing inventory rows, classification fixes, escrow
  location, drill cadence.
- `docs/JWT_ROTATION.md` — Supabase signing secret, real token lifetime, verification and force-logout steps.
- `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` — add the 13 missing names and a "consuming job → environment"
  column.
- `docs/INCIDENT_RESPONSE.md` — repoint the runbook references and remove the stale monitoring gap.
- `docs/ENVIRONMENT_VARIABLES.md` — add the observability/alertmanager env vars (or cross-link
  `MONITORING_AND_ALERTING.md`).
- New: `docs/SECRET_ROTATION_RUNBOOK.md` (IT-level break-glass/revocation, including escrow and drill steps).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| On which GitHub environment are the prod deploy secrets actually scoped (repo-wide, `prod`, or `prod-approval`)? | Decides whether the documented `--env prod` command is effective or a silent no-op | `gh secret list --env prod` / `--env prod-approval` output (no access here) |
| Has any secret ever been rotated since the initial deployment? | Rotation policy effectiveness | `gh secret list` updated-at timestamps; Rotation Log entries |
| Has the weekly `secret-history-scan` run and passed since 2026-10-10? | Proves the new control is exercised | Actions run history / artifact |
| Where is the "agreed escrow location" for `BACKUP_ENCRYPTION_KEY` / `FIELD_ENCRYPTION_KEY`? | Recovery if the key is lost | Owner decision; no repo evidence |
| Are dev and prod using separate credentials for every secret (no shared cross-environment values)? | Blast radius of a dev leak | Live environment scoping (not inspectable) |
| Is the Supabase project JWT secret the same value as the app `JWT_SECRET`? | Whether the current rotation procedure is effective at all | Supabase dashboard + secret store comparison |
| Has the quarterly reminder workflow ever created an issue? | Confirms the automation is exercised | GitHub issues search (`label:secret-rotation`) |

## Appendix

### A. Companion artifact — secret rotation runbook (summary; full text in Findings 13/16 and Recommendations)

1. **Scope:** every name in the inventory (once reconciled); values never pasted anywhere.
2. **Standard rotation:** generate at source → `gh secret set <NAME> --env <consuming-environment>` →
   deploy/verify → revoke old → record in the Rotation Log.
   - Consuming environments: deploy/app secrets → `prod-approval` (prod) / `dev`; migrations & Terraform
     plan → `prod` / `dev`; Terraform apply → `prod-approval`; backups → `dev`.
3. **JWT:** rotate the Supabase project JWT secret first; keep the comma-list only for the overlap window;
   after the window remove the old value and confirm an old-secret token is rejected.
4. **No-schedule keys:** `FIELD_ENCRYPTION_KEY` and `BACKUP_ENCRYPTION_KEY` follow the re-encryption
   procedures in `SECRETS_ROTATION.md:62-99`; never rotate without a re-encrypt plan.
5. **Record:** date, secret names, operator, environment, incident flag, run URL.

### B. Companion artifact — emergency revocation plan (summary)

1. Revoke/disable the credential at the source first (provider console), preserving the audit trail.
2. Set the replacement with `gh secret set` into the **consuming** environment; redeploy the affected job.
3. If JWT/session material is involved: rotate the Supabase project JWT secret and invalidate sessions
   (concrete mechanism still to be documented — Open Question).
4. Rotate adjacent consumers (worker + API for Supabase keys; all consumers for shared integrations).
5. Run the full-history secret scan; record the incident and the rotation in the Rotation Log.
6. Break-glass rules: incident ticket + named approver, time-boxed, post-incident review.

### C. Command log (read-only, excerpted)

```
git rev-parse HEAD                                  # 8d299b8d...
grep -rn "M365_WEBHOOK_SECRET" . --exclude-dir=docs/audits   # comments only
python3 diff(secrets.X, SECRETS_ROTATION.md backticks)       # 20 missing names
grep -c REDIS_PASSWORD docs/SECRETS_ROTATION.md              # 0
grep -n environment: .github/workflows/*.yml                 # prod-approval vs prod vs dev
grep -rn JWT_EXPIRY .                                # docs only, 0 code hits
find . -name "secret_rotation_runbook*"              # only the 20261002 audit folder
git check-ignore -v .../prod.tfvars                  # .gitignore:57 (exit 0)
grep -n "chmod 600\|chmod 400" .github/workflows/deploy-do.yml
```

### D. Cross-domain rows not duplicated here

- `ACM-P2-007` / WH row "Webhook signing secrets are stored plaintext with no rotation or expiry" —
  re-verified at `8d299b8d` by the ACM (24) and WH (27) domains (still-open).
- `SC` row "Scheduled full-history secret scan has no failure notification" — owned by the SC domain.
- `CI-P1-003` "prod environment lacks secrets/protection rules" — owned by the CI domain; related to but
  distinct from Finding 13 (this domain reports the rotation-procedure mapping defect).
