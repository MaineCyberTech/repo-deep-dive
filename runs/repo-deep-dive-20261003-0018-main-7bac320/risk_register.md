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
