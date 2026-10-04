# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| DATA-P0-001 | P0 | Orphan cleanup can recursively delete a bucket’s contents |  |  | verified-fixed | remediation PATCH-001 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/43; re-audit 2026-10-04: closed |
| CI-P1-001 | P1 | Production deploy path cannot run; prod environment lacks secrets and protection rules |  |  | verified-fixed | re-audit 2026-10-04: closed by mainecybertech#83-#86; required reviewers configured on prod/prod-approval (GitHub Environments API) |
| FINAL-P1-001 | P1 | P0 data-loss path and unverified "fixed" claim block a clean release |  |  | still-open | re-audit 2026-10-04: still-open |
| SEC-P1-001 | P1 | PII field encryption silently degrades to reversible plaintext |  |  | verified-fixed | re-audit 2026-10-04: closed by mainecybertech#83 @ 3e764c5 + #86 @ 27f1847 (prod boot requires FIELD_ENCRYPTION_KEY) |
| API-P2-001 | P2 | Search falls through to an unscoped cross-tenant query |  |  | verified-fixed | remediation PATCH-005 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/57; re-audit 2026-10-04: closed |
| API-P2-002 | P2 | OpenAPI schema is public and the Swagger UI is blocked by CSP |  |  | still-open | re-audit 2026-10-04: still-open |
| ARCH-P2-001 | P2 | Single-droplet, single-instance runtime is a hard SPOF |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| ARCH-P2-002 | P2 | API defaults to the service-role DB client (RLS bypass) |  |  | still-open | re-audit 2026-10-04: still-open |
| ARCH-P2-003 | P2 | Prometheus loads rules but has no alert routing |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| CI-P2-001 | P2 | Branch protection permits admin bypass and ignores CODEOWNERS |  |  | partially-fixed | re-audit 2026-10-04: partially-fixed |
| CI-P2-002 | P2 | Terraform apply is manual and drift detection is not automated |  |  | still-open | re-audit 2026-10-04: still-open |
| DATA-P2-001 | P2 | Generated DB types / schema can drift from migration intent |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| DATA-P2-002 | P2 | Orphan cleanup reference query is unbounded in the object list |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| FEAT-P2-001 | P2 | API keys cannot authenticate; the feature is dead |  |  | verified-fixed | remediation PATCH-009 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/59 |
| FEAT-P2-002 | P2 | Demo/test data can be seeded into a fresh production database |  |  | still-open | re-audit 2026-10-04: still-open |
| FINAL-P2-001 | P2 | Governance and observability gaps mean the platform cannot yet detect or control production failure |  |  | verified-fixed | remediation PS-U02 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/55 |
| FINAL-P2-002 | P2 | Residual authorization/secret defaults need explicit decisions |  |  | verified-fixed | remediation PS-U02 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/55 |
| HYG-P2-001 | P2 | Committed prompt/audit corpus bloats the repo and review surface |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| HYG-P2-002 | P2 | Duplicate product catalogs have diverged |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| INV-P2-001 | P2 | Committed generated artifacts drift without a gate |  |  | verified-fixed | remediation PATCH-012 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/61 |
| INV-P2-002 | P2 | Duplicate schema bootstrap SQL can be mistaken for the source of truth |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| OBS-P2-001 | P2 | Prometheus alert rules are not routed anywhere |  |  | verified-fixed | Already fixed at PR base 11746adc by prior remediation IR-P0-003 (e59d875d, 5e97b660, e84c8ee9); audit ran on stale clone 2295958d. No duplicate PR opened. Verified in lab: docker compose config, promtool check/test rules, amtool check-config all exit 0. |
| OBS-P2-002 | P2 | No committed dashboards or SLO/error-budget definitions |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| OBS-P2-003 | P2 | Backup/restore is scheduled but not verified on the deployed branch |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| SEC-P2-002 | P2 | CAPTCHA/Turnstile is bypassed when the secret is unset |  |  | verified-fixed | re-audit 2026-10-04: closed by mainecybertech#84 @ 49646db (worker pinnedFetch closes DNS-rebinding TOCTOU) |
| SEC-P2-003 | P2 | `/health` publicly discloses provider configuration and Redis errors |  |  | still-open | re-audit 2026-10-04: still-open |
| SUPPLY-P2-001 | P2 | `licenses.json` is committed but unenforced and unverified |  |  | verified-fixed | remediation PATCH-012 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/61 |
| SUPPLY-P2-002 | P2 | Swagger UI loads an unpinned third-party script without SRI |  |  | still-open | re-audit 2026-10-04: still-open |
| TEST-P2-001 | P2 | Orphan-cleanup tests model `storage.list` incorrectly, masking the data-loss bug |  |  | verified-fixed | remediation PATCH-001 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/43; re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | Route suites stub authorization middleware, so new routes can regress silently |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| API-P3-001 | P3 | `/metrics` is fully public when `METRICS_TOKEN` is unset |  |  | still-open | re-audit 2026-10-04: still-open |
| ARCH-P3-001 | P3 | Web middleware gates routes on an unverified JWT `exp` |  |  | partially-fixed | remediation PS-U01 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/64 |
| CI-P3-001 | P3 | `main` is far behind `develop`; scheduled jobs fire only from the default branch |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| FEAT-P3-001 | P3 | OpenAPI/Swagger surface is public and its UI is blocked by the API CSP |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P3-001 | P3 | Stale and machine-specific generated documentation |  |  | verified-fixed | remediation PS-U03 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/65 |
| HYG-P3-002 | P3 | Generated artifacts are inconsistently tracked |  |  | verified-fixed | remediation PATCH-012 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/61 |
| INV-P3-001 | P3 | Large committed prompt/audit corpus inflates the application repository |  |  | verified-fixed | remediation PS-U04 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/66 |
| INV-P3-002 | P3 | Stale, machine-specific repo path in the agent reference |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| OBS-P3-001 | P3 | Incident runbooks/tabletop evidence is partial |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| SEC-P3-001 | P3 | Deprecated header and broad API CSP style directive |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| SEC-P3-002 | P3 | M365 webhook `clientState` is compared non-constant-time |  |  | still-open | re-audit 2026-10-04: still-open |
| SUPPLY-P3-001 | P3 | SBOM is produced as a transient artifact, not bound to a release |  |  | verified-fixed | remediation PS-U05 merged a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/67 |
| SUPPLY-P3-002 | P3 | A secrets file exists on disk outside git (should never be committed) |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
| TEST-P3-001 | P3 | Coverage thresholds are low and E2E stability is unproven on `main` |  |  | partially-fixed | remediation PATCH-013 open a97425dbefc54b7db2a4e3ebe42470364dac0fab https://github.com/MaineCyberTech/mainecybertech/pull/63 |
