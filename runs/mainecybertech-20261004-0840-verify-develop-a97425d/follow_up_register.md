# Follow-up register (post-merge verification)

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| DATA-P0-001 | P0 | Orphan cleanup can recursively delete a bucket’s contents |  |  | verified-fixed | apps/worker/src/tasks/orphan-cleanup.ts: folder entries never reach remove(); unsafe paths abort the bucket; regression tests in orphan-cleanup.test.ts; CI test green. |
| CI-P1-001 | P1 | Production deploy path cannot run; prod environment lacks secrets and protection rules |  |  | still-open | Fail-closed deploy gate merged via PR #72; prod environment still lacks secrets and protection rules (operator action). |
| FINAL-P1-001 | P1 | P0 data-loss path and unverified "fixed" claim block a clean release |  |  | verified-fixed | docs/RELEASE_GATE.md at the commit records the P0 closure and gate state. |
| SEC-P1-001 | P1 | PII field encryption silently degrades to reversible plaintext |  |  | verified-fixed | apps/api/src/config/env.ts assertProductionSecrets + lib/field-encryption.ts throws instead of writing plaintext; env/field-encryption tests green; dev droplet boots with the key. |
| API-P2-001 | P2 | Search falls through to an unscoped cross-tenant query |  |  | verified-fixed | routes/search.ts scopes to req.orgScope and fails closed on empty scope; search tests green. |
| API-P2-002 | P2 | OpenAPI schema is public and the Swagger UI is blocked by CSP |  |  | verified-fixed | routes/docs.ts 404s in production; verified on the dev droplet: /api/v1/openapi.json -> 404. |
| ARCH-P2-001 | P2 | Single-droplet, single-instance runtime is a hard SPOF |  |  | partially-fixed | Platform failure/recovery runbooks added; single-droplet topology unchanged (owner/budget decision). |
| ARCH-P2-002 | P2 | API defaults to the service-role DB client (RLS bypass) |  |  | partially-fixed | Production refuses to boot with an empty RLS read allow-list (rls-startup-check.ts; dev boots with the full list); per-module rollout remains operational. |
| ARCH-P2-003 | P2 | Prometheus loads rules but has no alert routing |  |  | verified-fixed | already fixed at base (Prometheus alerting block + Alertmanager service). |
| CI-P2-001 | P2 | Branch protection permits admin bypass and ignores CODEOWNERS |  |  | verified-fixed | already fixed at base 8b02f91a (PR #30): enforce_admins, code-owner reviews, real contexts. |
| CI-P2-002 | P2 | Terraform apply is manual and drift detection is not automated |  |  | verified-fixed | terraform-do.yml weekly plan-only drift run alerts on a non-empty plan. |
| DATA-P2-001 | P2 | Generated DB types / schema can drift from migration intent |  |  | verified-fixed | already fixed at base 11746adc (encrypted_pii + generate-db-types --check); verified green. |
| DATA-P2-002 | P2 | Orphan cleanup reference query is unbounded in the object list |  |  | verified-fixed | orphan-cleanup.ts chunks the PostgREST .in() reference lookup (200 keys/request), fail-closed preserved. |
| FEAT-P2-001 | P2 | API keys cannot authenticate; the feature is dead |  |  | verified-fixed | middleware/api-key.ts resolves mct_ keys (hash + timing-safe compare) and is wired into middleware/auth.ts; api_keys table exists (5302042). |
| FEAT-P2-002 | P2 | Demo/test data can be seeded into a fresh production database |  |  | verified-fixed | demo-seeding migrations gated on app.seed_demo (default off). |
| FINAL-P2-001 | P2 | Governance and observability gaps mean the platform cannot yet detect or control production failure |  |  | verified-fixed | docs/RELEASE_GATE.md + docs/RELEASE.md governance/observability state. |
| FINAL-P2-002 | P2 | Residual authorization/secret defaults need explicit decisions |  |  | verified-fixed | docs/RELEASE_GATE.md records the residual authorization/secret decisions. |
| HYG-P2-001 | P2 | Committed prompt/audit corpus bloats the repo and review surface |  |  | partially-fixed | Prior-run snapshots removed (PS-U04); externalizing the remaining corpus is an owner decision. |
| HYG-P2-002 | P2 | Duplicate product catalogs have diverged |  |  | partially-fixed | Duplicate product catalogs remain diverged (content-owner decision). |
| INV-P2-001 | P2 | Committed generated artifacts drift without a gate |  |  | verified-fixed | generated license/SBOM artifacts stay untracked; CI guard added (dependency-audit composite). |
| INV-P2-002 | P2 | Duplicate schema bootstrap SQL can be mistaken for the source of truth |  |  | verified-fixed | bootstrap SQL header marks it historical / do-not-edit. |
| OBS-P2-001 | P2 | Prometheus alert rules are not routed anywhere |  |  | verified-fixed | already fixed at base (IR-P0-003); promtool/amtool checks green. |
| OBS-P2-002 | P2 | No committed dashboards or SLO/error-budget definitions |  |  | verified-fixed | infra/digitalocean/dashboards/mct-overview.json + docs/SLO.md committed. |
| OBS-P2-003 | P2 | Backup/restore is scheduled but not verified on the deployed branch |  |  | partially-fixed | Backup/restore still not verified end-to-end on the deployed branch (operator secrets/schedule). |
| SEC-P2-002 | P2 | CAPTCHA/Turnstile is bypassed when the secret is unset |  |  | verified-fixed | env.ts assertProductionTurnstile; routes/public.ts requires a verified token; E2E boots with the test secret; dev droplet boots and the web contact page renders the Turnstile widget. |
| SEC-P2-003 | P2 | `/health` publicly discloses provider configuration and Redis errors |  |  | verified-fixed | routes/health.ts exposes only status/uptime on /; /detail requires METRICS_TOKEN (404 without; verified on dev). |
| SUPPLY-P2-001 | P2 | `licenses.json` is committed but unenforced and unverified |  |  | verified-fixed | licenses.json untracked + gitignored; license gate + untracked-artifact guard run in CI. |
| SUPPLY-P2-002 | P2 | Swagger UI loads an unpinned third-party script without SRI |  |  | verified-fixed | docs route self-hosts Swagger UI; no unpinned third-party script. |
| TEST-P2-001 | P2 | Orphan-cleanup tests model `storage.list` incorrectly, masking the data-loss bug |  |  | verified-fixed | orphan-cleanup.test.ts models list() folder ids/absence and pagination; merged suite passes (worker 129 tests). |
| TEST-P2-002 | P2 | Route suites stub authorization middleware, so new routes can regress silently |  |  | verified-fixed | apps/api/src/__tests__/route-authorization-guard.test.ts guards new router mounts. |
| API-P3-001 | P3 | `/metrics` is fully public when `METRICS_TOKEN` is unset |  |  | verified-fixed | metrics endpoint token-gated; /api/v1/metrics -> 404 on dev without token. |
| ARCH-P3-001 | P3 | Web middleware gates routes on an unverified JWT `exp` |  |  | partially-fixed | Web middleware documented as a non-authoritative UX gate; behavior intentionally unchanged (API verifies tokens). |
| CI-P3-001 | P3 | `main` is far behind `develop`; scheduled jobs fire only from the default branch |  |  | partially-fixed | develop is ahead of main and scheduled jobs still fire only from the default branch (owner decision). |
| FEAT-P3-001 | P3 | OpenAPI/Swagger surface is public and its UI is blocked by the API CSP |  |  | verified-fixed | same docs gating; OpenAPI coverage gate restored (openapi-audit 0 missing; 418 paths). |
| HYG-P3-001 | P3 | Stale and machine-specific generated documentation |  |  | verified-fixed | stale generated-docs path corrected (PS-U03). |
| HYG-P3-002 | P3 | Generated artifacts are inconsistently tracked |  |  | verified-fixed | same guard: licenses.json/sbom.* fail the build if tracked. |
| INV-P3-001 | P3 | Large committed prompt/audit corpus inflates the application repository |  |  | verified-fixed | 157 prior-run prompt snapshots removed; manifest regenerated (630 pinned); deploy validate prompt-provenance green. |
| INV-P3-002 | P3 | Stale, machine-specific repo path in the agent reference |  |  | verified-fixed | AGENTS.md and generated review.md carry the canonical repo slug. |
| OBS-P3-001 | P3 | Incident runbooks/tabletop evidence is partial |  |  | partially-fixed | Platform failure runbooks added; tabletop evidence still partial. |
| SEC-P3-001 | P3 | Deprecated header and broad API CSP style directive |  |  | verified-fixed | security-headers.ts drops the deprecated X-XSS-Protection and tightens the API style-src. |
| SEC-P3-002 | P3 | M365 webhook `clientState` is compared non-constant-time |  |  | verified-fixed | lib/timing-safe.ts + constant-time M365 clientState comparison in routes/webhooks.ts. |
| SUPPLY-P3-001 | P3 | SBOM is produced as a transient artifact, not bound to a release |  |  | verified-fixed | deploy-do generates digest-bound image SBOMs and attests them; verify-attestations green in deploy run 37188587849. |
| SUPPLY-P3-002 | P3 | A secrets file exists on disk outside git (should never be committed) |  |  | verified-fixed | secret-scan composite rejects tracked supabase/.temp/** and non-example .env files. |
| TEST-P3-001 | P3 | Coverage thresholds are low and E2E stability is unproven on `main` |  |  | partially-fixed | Coverage thresholds ratcheted; E2E stability on main remains unproven (main behind develop). |
