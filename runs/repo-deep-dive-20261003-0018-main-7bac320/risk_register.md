# Risk Register — repo-deep-dive (20261003-0018-main-7bac320)

Commit: worktree `6cada03` (recorded `7bac320`) · Total findings: 41 (P0 0 · P1 9 · P2 20 · P3 12)

| ID | Severity | Area | Title | Owner suggestion | Target | Status |
|---|---|---|---|---|---|---|
| INV-P1-001 | P1 | INV | Run bound to 7bac320 but worktree at 6cada03 | pack maintainer | this week | open |
| INV-P2-002 | P2 | INV | inventory.json reports no CI/workflows while one exists at HEAD | pack maintainer | this month | open |
| INV-P3-003 | P3 | INV | Tracked environment-local pin excluded from digest | pack maintainer | this quarter | open |
| ARCH-P2-001 | P2 | ARCH | Orchestration truth duplicated across four artifacts | pack maintainer | this month | open |
| ARCH-P2-002 | P2 | ARCH | Primary run gate silently skipped without bash | pack maintainer | this month | open |
| FEAT-P2-001 | P2 | FEAT | New tools/workflow shipped without changelog/version/docs | pack maintainer | this month | open |
| FEAT-P3-002 | P3 | FEAT | README tool inventory stale | pack maintainer | this quarter | open |
| SEC-P1-001 | P1 | SEC | CI executes remote scripts/archives as root unpinned | CI owner | this week | open |
| SEC-P1-002 | P1 | SEC | PAT embedded in git clone URL | CI owner | this week | open |
| SEC-P2-003 | P2 | SEC | CI security checks non-gating; no gitleaks allowlist | CI owner | this month | open |
| SEC-P3-004 | P3 | SEC | No SECURITY.md or CODEOWNERS | pack maintainer | this quarter | open |
| SEC-P3-005 | P3 | SEC | Internal org/repo identifiers hardcoded | CI owner | this quarter | open |
| DATA-P1-001 | P1 | DATA | findings.json violates its own schema (sourceReports) | pack maintainer | this week | open |
| DATA-P1-002 | P1 | DATA | Base scaffold manifest rejected by check_run | pack maintainer | this week | open |
| DATA-P3-003 | P3 | DATA | Deterministic findings line=1 and en-dash separator | pack maintainer | this quarter | open |
| API-P2-001 | P2 | API | Deterministic lens reuses domain area codes | pack maintainer | this month | open |
| API-P2-002 | P2 | API | Deterministic findings never reach run findings flow | pack maintainer | this month | open |
| TEST-P1-001 | P1 | TEST | No CI runs lint/self-test or authorizes PRs | CI owner | this week | open |
| TEST-P2-002 | P2 | TEST | Smoke harness bash-only, not exercised on Windows | pack maintainer | this month | open |
| TEST-P2-003 | P2 | TEST | Self-test schema check omits type validation | pack maintainer | this month | open |
| TEST-P3-004 | P3 | TEST | No unit tests for parsing/inventory/deterministic logic | pack maintainer | this quarter | open |
| CI-P1-001 | P1 | CI | Audit CI example not under .github/workflows, never runs | CI owner | this week | open |
| CI-P1-002 | P1 | CI | ci/audit.yml PACK_DIR assumes vendored layout | CI owner | this week | open |
| CI-P2-003 | P2 | CI | Wired workflow installs mutable latest tools, fails silently | CI owner | this month | open |
| CI-P2-004 | P2 | CI | Org-wide PAT workflow lacks concurrency/timeouts/protection | CI owner | this month | open |
| CI-P2-005 | P2 | CI | No branch protection/required checks/CODEOWNERS | repo admin | this month | open |
| CI-P2-006 | P2 | CI | pull_request passes empty run_dir to P0 gate | CI owner | this month | open |
| SUPPLY-P1-001 | P1 | SUPPLY | Actions and downloaded tools unpinned | CI owner | this week | open |
| SUPPLY-P2-002 | P2 | SUPPLY | No dependency-update automation | CI owner | this month | open |
| SUPPLY-P2-003 | P2 | SUPPLY | No SBOM or license policy enforcement | pack maintainer | this month | open |
| SUPPLY-P3-004 | P3 | SUPPLY | No LICENSE file | pack maintainer | this quarter | open |
| OBS-P2-001 | P2 | OBS | No structured output or pipeline freshness signal | pack maintainer | this month | open |
| OBS-P2-002 | P2 | OBS | Scheduled checks mask failures, never alert on regression | CI owner | this month | open |
| OBS-P3-003 | P3 | OBS | Dashboards/diffs generated but not bound to archived runs | pack maintainer | this quarter | open |
| HYG-P2-001 | P2 | HYG | Missing .gitignore/.gitattributes | pack maintainer | this month | open |
| HYG-P3-002 | P3 | HYG | Digest omits tree file and disagrees with inventory count | pack maintainer | this quarter | open |
| HYG-P3-003 | P3 | HYG | Archived runs commit sensitive environment snapshots | pack maintainer | this quarter | open |
| FINAL-P2-001 | P2 | FINAL | No evidence toolchain/self-test ran at audited commit | pack maintainer | this month | open |
| FINAL-P3-002 | P3 | FINAL | Archived verdicts not re-verified after two tooling commits | pack maintainer | this quarter | open |
| EXEC-P2-001 | P2 | EXEC | No accountable owner mapping | repo admin | this month | open |
| EXEC-P3-002 | P3 | EXEC | Gate cannot cite machine-validated run until scaffold fixed | pack maintainer | this quarter | open |

## Finding index

| ID | Severity | Title |
|---|---|---|
| CI-P1-001 | P1 | The audit CI example is not under `.github/workflows/` and never runs |
| CI-P1-002 | P1 | ci/audit.yml assumes a vendored PACK_DIR that does not match this repo |
| DATA-P1-001 | P1 | findings.json violates its own schema (`sourceReports` array vs integer) |
| DATA-P1-002 | P1 | Base-profile scaffold produces a manifest the pack's own gate rejects |
| INV-P1-001 | P1 | Run is bound to 7bac320 but the worktree is at 6cada03 |
| SEC-P1-001 | P1 | CI executes remotely downloaded scripts and archives as root without pinning |
| SEC-P1-002 | P1 | PAT is embedded in the git clone URL, risking token exposure in logs |
| SUPPLY-P1-001 | P1 | GitHub Actions and downloaded tools are unpinned (mutable tags/branches) |
| TEST-P1-001 | P1 | No CI job runs the pack's own lint/self-test or authorizes PRs |
| API-P2-001 | P2 | Deterministic lens reuses domain area codes, risking duplicate finding IDs |
| API-P2-002 | P2 | Deterministic findings never reach the run findings flow |
| ARCH-P2-001 | P2 | Orchestration truth is duplicated across four artifacts with no drift check |
| ARCH-P2-002 | P2 | The primary run gate is silently skipped when bash is unavailable |
| CI-P2-003 | P2 | The wired workflow installs mutable "latest" tools and fails silently |
| CI-P2-004 | P2 | Org-wide PAT workflow lacks concurrency, timeouts, and environment protection |
| CI-P2-005 | P2 | No branch protection, required-check, or CODEOWNERS evidence |
| CI-P2-006 | P2 | pull_request runs pass an empty run_dir to the P0 gate |
| EXEC-P2-001 | P2 | No accountable owner mapping for the pack |
| FEAT-P2-001 | P2 | New tools and the org workflow shipped without changelog, version bump, or docs |
| FINAL-P2-001 | P2 | No evidence the toolchain/self-test ran at the audited commit |
| HYG-P2-001 | P2 | Missing `.gitignore` and `.gitattributes` create cross-platform and config-sprawl risk |
| INV-P2-002 | P2 | inventory.json reports no CI/workflows while a workflow exists at HEAD |
| OBS-P2-001 | P2 | No structured output or freshness signal for the audit pipeline |
| OBS-P2-002 | P2 | Scheduled checks mask failures and never alert on regression |
| SEC-P2-003 | P2 | CI security checks are non-gating and there is no secret-scan allowlist |
| SUPPLY-P2-002 | P2 | No dependency-update automation |
| SUPPLY-P2-003 | P2 | No SBOM or license policy is enforced despite prompt 35 |
| TEST-P2-002 | P2 | The smoke harness is bash-only and not exercised on the maintainer's platform |
| TEST-P2-003 | P2 | Self-test schema check omits type/contract validation |
| DATA-P3-003 | P3 | Deterministic findings use line 1 for every row and an en-dash separator |
| EXEC-P3-002 | P3 | The gate cannot cite a machine-validated run until the scaffold defect is fixed |
| FEAT-P3-002 | P3 | README tool inventory is stale |
| FINAL-P3-002 | P3 | Archived run verdicts and register statuses were not re-verified after two tooling commits |
| HYG-P3-002 | P3 | The integrity digest omits a tracked file and disagrees with the inventory count |
| HYG-P3-003 | P3 | Archived runs commit sensitive environment snapshots |
| INV-P3-003 | P3 | A tracked, environment-local pin is excluded from the integrity digest |
| OBS-P3-003 | P3 | Dashboards and diffs are generated but not bound to archived runs |
| SEC-P3-004 | P3 | No vulnerability-disclosure policy or code ownership file |
| SEC-P3-005 | P3 | Internal org and repository identifiers are hardcoded as workflow defaults |
| SUPPLY-P3-004 | P3 | No LICENSE file |
| TEST-P3-004 | P3 | No unit tests for parsing, inventory, or deterministic logic |
