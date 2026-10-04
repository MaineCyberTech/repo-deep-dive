# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| CI-P1-001 | P1 | The audit CI example is not under `.github/workflows/` and never runs |  |  | verified-fixed | merged repo-deep-dive#3 @ c97e73e; re-audit 2026-10-04: closed |
| CI-P1-002 | P1 | ci/audit.yml assumes a vendored PACK_DIR that does not match this repo |  |  | verified-fixed | merged repo-deep-dive#3 @ c97e73e; re-audit 2026-10-04: closed |
| DATA-P1-001 | P1 | findings.json violates its own schema (`sourceReports` array vs integer) |  |  | verified-fixed | merged repo-deep-dive#1 @ 85eff06; re-audit 2026-10-04: closed |
| DATA-P1-002 | P1 | Base-profile scaffold produces a manifest the pack's own gate rejects |  |  | verified-fixed | merged repo-deep-dive#1 @ 85eff06; re-audit 2026-10-04: closed |
| INV-P1-001 | P1 | Run is bound to 7bac320 but the worktree is at 6cada03 |  |  | verified-fixed | merged repo-deep-dive#4 @ 6c89296; re-audit 2026-10-04: closed |
| SEC-P1-001 | P1 | CI executes remotely downloaded scripts and archives as root without pinning |  |  | verified-fixed | merged repo-deep-dive#2 @ 2d5b4f5; re-audit 2026-10-04: closed |
| SEC-P1-002 | P1 | PAT is embedded in the git clone URL, risking token exposure in logs |  |  | verified-fixed | merged repo-deep-dive#2 @ 2d5b4f5; re-audit 2026-10-04: closed |
| SUPPLY-P1-001 | P1 | GitHub Actions and downloaded tools are unpinned (mutable tags/branches) |  |  | verified-fixed | re-audit 2026-10-04: regression fixed by repo-deep-dive#39 @ 7893e39 |
| TEST-P1-001 | P1 | No CI job runs the pack's own lint/self-test or authorizes PRs |  |  | verified-fixed | merged repo-deep-dive#3 @ c97e73e; re-audit 2026-10-04: closed |
| API-P2-001 | P2 | Deterministic lens reuses domain area codes, risking duplicate finding IDs |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-002 | P2 | Deterministic findings never reach the run findings flow |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-001 | P2 | Orchestration truth is duplicated across four artifacts with no drift check |  |  | partially-fixed | re-audit 2026-10-04: partially-fixed |
| ARCH-P2-002 | P2 | The primary run gate is silently skipped when bash is unavailable |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-003 | P2 | The wired workflow installs mutable "latest" tools and fails silently |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-004 | P2 | Org-wide PAT workflow lacks concurrency, timeouts, and environment protection |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-005 | P2 | No branch protection, required-check, or CODEOWNERS evidence |  |  | partially-fixed | re-audit 2026-10-04: partially-fixed |
| CI-P2-006 | P2 | pull_request runs pass an empty run_dir to the P0 gate |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P2-001 | P2 | No accountable owner mapping for the pack |  |  | partially-fixed | remediation PS-011 open fd9cf670164dba78f5a9fee8635da9c7d95f5725 https://github.com/MaineCyberTech/repo-deep-dive/pull/10 |
| FEAT-P2-001 | P2 | New tools and the org workflow shipped without changelog, version bump, or docs |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P2-001 | P2 | No evidence the toolchain/self-test ran at the audited commit |  |  | partially-fixed | remediation PS-010 open bfbb0e005880f28e77892650a548e9817dd78924 https://github.com/MaineCyberTech/repo-deep-dive/pull/9 |
| HYG-P2-001 | P2 | Missing `.gitignore` and `.gitattributes` create cross-platform and config-sprawl risk |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-002 | P2 | inventory.json reports no CI/workflows while a workflow exists at HEAD |  |  | partially-fixed | remediation PS-009 open c7f59f8c375b9bf649ce6b452352ede37fd8a10b https://github.com/MaineCyberTech/repo-deep-dive/pull/4 |
| OBS-P2-001 | P2 | No structured output or freshness signal for the audit pipeline |  |  | partially-fixed | remediation PS-008 open 50c3d2407193923cc9acfbfb8c015f6f226e9e98 https://github.com/MaineCyberTech/repo-deep-dive/pull/8 |
| OBS-P2-002 | P2 | Scheduled checks mask failures and never alert on regression |  |  | partially-fixed | re-audit 2026-10-04: partially-fixed |
| SEC-P2-003 | P2 | CI security checks are non-gating and there is no secret-scan allowlist |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-002 | P2 | No dependency-update automation |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-003 | P2 | No SBOM or license policy is enforced despite prompt 35 |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | The smoke harness is bash-only and not exercised on the maintainer's platform |  |  | partially-fixed | re-audit 2026-10-04: partially-fixed |
| TEST-P2-003 | P2 | Self-test schema check omits type/contract validation |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P3-003 | P3 | Deterministic findings use line 1 for every row and an en-dash separator |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P3-002 | P3 | The gate cannot cite a machine-validated run until the scaffold defect is fixed |  |  | partially-fixed | remediation PS-011 open fd9cf670164dba78f5a9fee8635da9c7d95f5725 https://github.com/MaineCyberTech/repo-deep-dive/pull/10 |
| FEAT-P3-002 | P3 | README tool inventory is stale |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P3-002 | P3 | Archived run verdicts and register statuses were not re-verified after two tooling commits |  |  | partially-fixed | remediation PS-010 open bfbb0e005880f28e77892650a548e9817dd78924 https://github.com/MaineCyberTech/repo-deep-dive/pull/9 |
| HYG-P3-002 | P3 | The integrity digest omits a tracked file and disagrees with the inventory count |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P3-003 | P3 | Archived runs commit sensitive environment snapshots |  |  | partially-fixed | remediation PS-008 open 50c3d2407193923cc9acfbfb8c015f6f226e9e98 https://github.com/MaineCyberTech/repo-deep-dive/pull/8 |
| INV-P3-003 | P3 | A tracked, environment-local pin is excluded from the integrity digest |  |  | partially-fixed | remediation PS-009 open c7f59f8c375b9bf649ce6b452352ede37fd8a10b https://github.com/MaineCyberTech/repo-deep-dive/pull/4 |
| OBS-P3-003 | P3 | Dashboards and diffs are generated but not bound to archived runs |  |  | partially-fixed | remediation PS-008 open 50c3d2407193923cc9acfbfb8c015f6f226e9e98 https://github.com/MaineCyberTech/repo-deep-dive/pull/8 |
| SEC-P3-004 | P3 | No vulnerability-disclosure policy or code ownership file |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P3-005 | P3 | Internal org and repository identifiers are hardcoded as workflow defaults |  |  | partially-fixed | remediation PS-008 open 50c3d2407193923cc9acfbfb8c015f6f226e9e98 https://github.com/MaineCyberTech/repo-deep-dive/pull/8 |
| SUPPLY-P3-004 | P3 | No LICENSE file |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-004 | P3 | No unit tests for parsing, inventory, or deterministic logic |  |  | verified-fixed | re-audit 2026-10-04: closed |
