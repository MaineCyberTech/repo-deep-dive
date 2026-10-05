# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P2-001 | P2 | World-open DigitalOcean firewall mutation with no approval and unvalidated udp_port |
| CI-P2-002 | P2 | Deploy-gate secret scan is a no-op on pushes to main |
| CI-P2-003 | P2 | Production approval environment documented as having no required reviewers |
| CI-P3-001 | P3 | actionlint/shellcheck workflow lint issues (SC2086/SC2129/SC2002/SC2015) |
| CI-P3-002 | P3 | Over-broad workflow token permissions (unused write scopes) |
| CI-P3-003 | P3 | StrictHostKeyChecking=no in the deploy health check |
| CI-P1-001 | P1 | Production application deploys have no working manual-approval gate |
| CI-P1-002 | P1 | Branch-protection-as-code has a likely-mismatched required check and permits admin bypass |
| CI-P2-004 | P2 | DB restore test reports success without asserting restore integrity |
| CI-P2-005 | P2 | Infrastructure changes are no longer gated in CI (terraform-do is manual-dispatch only) |
| CI-P2-006 | P2 | Chromatic visual-regression job is permanently non-blocking |
| CI-P3-005 | P3 | Secret scanner misses the platform's own token formats and scans diffs only |
| CI-P3-006 | P3 | Unused permission grants across deploy/test workflows |
| CI-P3-007 | P3 | DB restore test uses an unpinned `postgres:16-alpine` image |
| CI-P3-008 | P3 | No release/tagging workflow and no post-merge release artifact |
| CI-P3-009 | P3 | e2e is required on `main` but the documented flakiness makes it an unstable hard gate |
| CI-P3-010 | P3 | Missing per-job timeouts and minor workflow hygiene gaps |
| CI-P1-003 | P1 | Production deploy path cannot run; prod environment lacks secrets and protection rules |
| CI-P2-007 | P2 | Branch protection permits admin bypass and ignores CODEOWNERS |
| CI-P2-008 | P2 | Terraform apply is manual and drift detection is not automated |
| CI-P3-004 | P3 | `main` is far behind `develop`; scheduled jobs fire only from the default branch |
