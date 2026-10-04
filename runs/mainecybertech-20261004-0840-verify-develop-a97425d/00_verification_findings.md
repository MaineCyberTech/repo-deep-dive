# Verification findings — post-merge re-audit

- Repo: `MaineCyberTech/mainecybertech` @ `a97425dbefc54b7db2a4e3ebe42470364dac0fab` (develop)
- Original run: `20261003-0018-fix-p2-batch-31-2295958d`
- This report carries the 44 original findings re-checked at the merged commit;
  per-finding evidence is in `verification_log.md` and `risk_register.md`.

| ID | Severity | Title |
|---|---|---|
| DATA-P0-001 | P0 | Orphan cleanup can recursively delete a bucket’s contents |
| CI-P1-001 | P1 | Production deploy path cannot run; prod environment lacks secrets and protection rules |
| FINAL-P1-001 | P1 | P0 data-loss path and unverified "fixed" claim block a clean release |
| SEC-P1-001 | P1 | PII field encryption silently degrades to reversible plaintext |
| API-P2-001 | P2 | Search falls through to an unscoped cross-tenant query |
| API-P2-002 | P2 | OpenAPI schema is public and the Swagger UI is blocked by CSP |
| ARCH-P2-001 | P2 | Single-droplet, single-instance runtime is a hard SPOF |
| ARCH-P2-002 | P2 | API defaults to the service-role DB client (RLS bypass) |
| ARCH-P2-003 | P2 | Prometheus loads rules but has no alert routing |
| CI-P2-001 | P2 | Branch protection permits admin bypass and ignores CODEOWNERS |
| CI-P2-002 | P2 | Terraform apply is manual and drift detection is not automated |
| DATA-P2-001 | P2 | Generated DB types / schema can drift from migration intent |
| DATA-P2-002 | P2 | Orphan cleanup reference query is unbounded in the object list |
| FEAT-P2-001 | P2 | API keys cannot authenticate; the feature is dead |
| FEAT-P2-002 | P2 | Demo/test data can be seeded into a fresh production database |
| FINAL-P2-001 | P2 | Governance and observability gaps mean the platform cannot yet detect or control production failure |
| FINAL-P2-002 | P2 | Residual authorization/secret defaults need explicit decisions |
| HYG-P2-001 | P2 | Committed prompt/audit corpus bloats the repo and review surface |
| HYG-P2-002 | P2 | Duplicate product catalogs have diverged |
| INV-P2-001 | P2 | Committed generated artifacts drift without a gate |
| INV-P2-002 | P2 | Duplicate schema bootstrap SQL can be mistaken for the source of truth |
| OBS-P2-001 | P2 | Prometheus alert rules are not routed anywhere |
| OBS-P2-002 | P2 | No committed dashboards or SLO/error-budget definitions |
| OBS-P2-003 | P2 | Backup/restore is scheduled but not verified on the deployed branch |
| SEC-P2-002 | P2 | CAPTCHA/Turnstile is bypassed when the secret is unset |
| SEC-P2-003 | P2 | `/health` publicly discloses provider configuration and Redis errors |
| SUPPLY-P2-001 | P2 | `licenses.json` is committed but unenforced and unverified |
| SUPPLY-P2-002 | P2 | Swagger UI loads an unpinned third-party script without SRI |
| TEST-P2-001 | P2 | Orphan-cleanup tests model `storage.list` incorrectly, masking the data-loss bug |
| TEST-P2-002 | P2 | Route suites stub authorization middleware, so new routes can regress silently |
| API-P3-001 | P3 | `/metrics` is fully public when `METRICS_TOKEN` is unset |
| ARCH-P3-001 | P3 | Web middleware gates routes on an unverified JWT `exp` |
| CI-P3-001 | P3 | `main` is far behind `develop`; scheduled jobs fire only from the default branch |
| FEAT-P3-001 | P3 | OpenAPI/Swagger surface is public and its UI is blocked by the API CSP |
| HYG-P3-001 | P3 | Stale and machine-specific generated documentation |
| HYG-P3-002 | P3 | Generated artifacts are inconsistently tracked |
| INV-P3-001 | P3 | Large committed prompt/audit corpus inflates the application repository |
| INV-P3-002 | P3 | Stale, machine-specific repo path in the agent reference |
| OBS-P3-001 | P3 | Incident runbooks/tabletop evidence is partial |
| SEC-P3-001 | P3 | Deprecated header and broad API CSP style directive |
| SEC-P3-002 | P3 | M365 webhook `clientState` is compared non-constant-time |
| SUPPLY-P3-001 | P3 | SBOM is produced as a transient artifact, not bound to a release |
| SUPPLY-P3-002 | P3 | A secrets file exists on disk outside git (should never be committed) |
| TEST-P3-001 | P3 | Coverage thresholds are low and E2E stability is unproven on `main` |

## Verification Performed

- Reconciled the 16 remediation PRs to the integration merge commit (`tools/remediation_status.py`).
- Machine re-audit at the merged commit (`tools/deterministic_checks.py --deep`): no new P0/P1.
- Runtime verification on the dev deployment (`deploy-do` run 37188587849).

## Scope and limits

- Verification mode only: no new domain audit was performed; the original reports remain authoritative for descriptions.
- The machine checks skipped gitleaks/trivy/hadolint because the tools are not installed on the verification host; this is recorded as not-run, not as a pass.
