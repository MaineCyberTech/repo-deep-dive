# Verification log — post-merge re-audit

- Repo: `MaineCyberTech/mainecybertech` @ `a97425dbefc54b7db2a4e3ebe42470364dac0fab` (develop)
- Original run: `20261003-0018-fix-p2-batch-31-2295958d`
- Procedure: `runbooks/POST_MERGE_REAUDIT.md`
- Date: 2026-10-04

## Method

1. Reconciled the 16 remediation PRs to the integration merge commit via `tools/remediation_status.py` (42 findings updated; PATCH-006/007 already verified-fixed at base).
2. Machine re-audit: `tools/deterministic_checks.py /root/mainecybertech -o /tmp/det --run mainecybertech --deep` at `a97425db` — 5 DET findings, no P0/P1; gitleaks/trivy/hadolint not installed on the host (recorded as skipped, not as passes).
3. LLM verification of every original finding against the merged tree and, where runtime-observable, the dev deployment (deploy run 37188587849; droplet at `a97425db`).

## Finding-by-finding result

| ID | Severity | Status | Evidence at `a97425db` |
|---|---|---|---|
| DATA-P0-001 | P0 | verified-fixed | apps/worker/src/tasks/orphan-cleanup.ts: folder entries never reach remove(); unsafe paths abort the bucket; regression tests in orphan-cleanup.test.ts; CI test green. |
| CI-P1-001 | P1 | still-open | Fail-closed deploy gate merged via PR #72; prod environment still lacks secrets and protection rules (operator action). |
| FINAL-P1-001 | P1 | verified-fixed | docs/RELEASE_GATE.md at the commit records the P0 closure and gate state. |
| SEC-P1-001 | P1 | verified-fixed | apps/api/src/config/env.ts assertProductionSecrets + lib/field-encryption.ts throws instead of writing plaintext; env/field-encryption tests green; dev droplet boots with the key. |
| API-P2-001 | P2 | verified-fixed | routes/search.ts scopes to req.orgScope and fails closed on empty scope; search tests green. |
| API-P2-002 | P2 | verified-fixed | routes/docs.ts 404s in production; verified on the dev droplet: /api/v1/openapi.json -> 404. |
| ARCH-P2-001 | P2 | partially-fixed | Platform failure/recovery runbooks added; single-droplet topology unchanged (owner/budget decision). |
| ARCH-P2-002 | P2 | partially-fixed | Production refuses to boot with an empty RLS read allow-list (rls-startup-check.ts; dev boots with the full list); per-module rollout remains operational. |
| ARCH-P2-003 | P2 | verified-fixed | already fixed at base (Prometheus alerting block + Alertmanager service). |
| CI-P2-001 | P2 | verified-fixed | already fixed at base 8b02f91a (PR #30): enforce_admins, code-owner reviews, real contexts. |
| CI-P2-002 | P2 | verified-fixed | terraform-do.yml weekly plan-only drift run alerts on a non-empty plan. |
| DATA-P2-001 | P2 | verified-fixed | already fixed at base 11746adc (encrypted_pii + generate-db-types --check); verified green. |
| DATA-P2-002 | P2 | verified-fixed | orphan-cleanup.ts chunks the PostgREST .in() reference lookup (200 keys/request), fail-closed preserved. |
| FEAT-P2-001 | P2 | verified-fixed | middleware/api-key.ts resolves mct_ keys (hash + timing-safe compare) and is wired into middleware/auth.ts; api_keys table exists (5302042). |
| FEAT-P2-002 | P2 | verified-fixed | demo-seeding migrations gated on app.seed_demo (default off). |
| FINAL-P2-001 | P2 | verified-fixed | docs/RELEASE_GATE.md + docs/RELEASE.md governance/observability state. |
| FINAL-P2-002 | P2 | verified-fixed | docs/RELEASE_GATE.md records the residual authorization/secret decisions. |
| HYG-P2-001 | P2 | partially-fixed | Prior-run snapshots removed (PS-U04); externalizing the remaining corpus is an owner decision. |
| HYG-P2-002 | P2 | partially-fixed | Duplicate product catalogs remain diverged (content-owner decision). |
| INV-P2-001 | P2 | verified-fixed | generated license/SBOM artifacts stay untracked; CI guard added (dependency-audit composite). |
| INV-P2-002 | P2 | verified-fixed | bootstrap SQL header marks it historical / do-not-edit. |
| OBS-P2-001 | P2 | verified-fixed | already fixed at base (IR-P0-003); promtool/amtool checks green. |
| OBS-P2-002 | P2 | verified-fixed | infra/digitalocean/dashboards/mct-overview.json + docs/SLO.md committed. |
| OBS-P2-003 | P2 | partially-fixed | Backup/restore still not verified end-to-end on the deployed branch (operator secrets/schedule). |
| SEC-P2-002 | P2 | verified-fixed | env.ts assertProductionTurnstile; routes/public.ts requires a verified token; E2E boots with the test secret; dev droplet boots and the web contact page renders the Turnstile widget. |
| SEC-P2-003 | P2 | verified-fixed | routes/health.ts exposes only status/uptime on /; /detail requires METRICS_TOKEN (404 without; verified on dev). |
| SUPPLY-P2-001 | P2 | verified-fixed | licenses.json untracked + gitignored; license gate + untracked-artifact guard run in CI. |
| SUPPLY-P2-002 | P2 | verified-fixed | docs route self-hosts Swagger UI; no unpinned third-party script. |
| TEST-P2-001 | P2 | verified-fixed | orphan-cleanup.test.ts models list() folder ids/absence and pagination; merged suite passes (worker 129 tests). |
| TEST-P2-002 | P2 | verified-fixed | apps/api/src/__tests__/route-authorization-guard.test.ts guards new router mounts. |
| API-P3-001 | P3 | verified-fixed | metrics endpoint token-gated; /api/v1/metrics -> 404 on dev without token. |
| ARCH-P3-001 | P3 | partially-fixed | Web middleware documented as a non-authoritative UX gate; behavior intentionally unchanged (API verifies tokens). |
| CI-P3-001 | P3 | partially-fixed | develop is ahead of main and scheduled jobs still fire only from the default branch (owner decision). |
| FEAT-P3-001 | P3 | verified-fixed | same docs gating; OpenAPI coverage gate restored (openapi-audit 0 missing; 418 paths). |
| HYG-P3-001 | P3 | verified-fixed | stale generated-docs path corrected (PS-U03). |
| HYG-P3-002 | P3 | verified-fixed | same guard: licenses.json/sbom.* fail the build if tracked. |
| INV-P3-001 | P3 | verified-fixed | 157 prior-run prompt snapshots removed; manifest regenerated (630 pinned); deploy validate prompt-provenance green. |
| INV-P3-002 | P3 | verified-fixed | AGENTS.md and generated review.md carry the canonical repo slug. |
| OBS-P3-001 | P3 | partially-fixed | Platform failure runbooks added; tabletop evidence still partial. |
| SEC-P3-001 | P3 | verified-fixed | security-headers.ts drops the deprecated X-XSS-Protection and tightens the API style-src. |
| SEC-P3-002 | P3 | verified-fixed | lib/timing-safe.ts + constant-time M365 clientState comparison in routes/webhooks.ts. |
| SUPPLY-P3-001 | P3 | verified-fixed | deploy-do generates digest-bound image SBOMs and attests them; verify-attestations green in deploy run 37188587849. |
| SUPPLY-P3-002 | P3 | verified-fixed | secret-scan composite rejects tracked supabase/.temp/** and non-example .env files. |
| TEST-P3-001 | P3 | partially-fixed | Coverage thresholds ratcheted; E2E stability on main remains unproven (main behind develop). |

## Runtime verification (dev droplet)

| Check | Result |
|---|---|
| `deploy-do` run 37188587849 (validate → builds → attestations → deploy) | success |
| Droplet checkout | `a97425db` |
| Containers | api/web/worker/redis/caddy healthy (restarted by the deploy) |
| `GET /health` (public) | 200, `{service, status, uptime}` only |
| `GET /health/detail` without token | 404 |
| `GET /api/v1/openapi.json`, `/api/v1/docs`, `/api/v1/metrics` without token | 404 |
| Boot gates | `FIELD_ENCRYPTION_KEY` (64-hex), `TURNSTILE_SECRET_KEY` (test pair), non-empty `RLS_READS_ENABLED` |
| Web contact page | Turnstile widget site key present |

## Machine re-audit output

| ID | Severity | Title |
|---|---|---|
| DET-P2-002 | P2 | 17 tracked shell scripts without the exec bit (pre-existing) |
| DET-P3-001 | P3 | trivy not installed (dependency vuln scan skipped) |
| DET-P3-003 | P3 | gitleaks not installed (secret scan skipped) |
| DET-P3-004 | P3 | 4 container images without a digest pin (pre-existing) |
| DET-P3-005 | P3 | hadolint not installed (Dockerfile lint skipped) |

## Regressions

None. No new P0/P1 findings at the merged commit.
