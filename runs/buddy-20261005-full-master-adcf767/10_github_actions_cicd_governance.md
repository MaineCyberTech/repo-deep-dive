# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

Two workflows: `ci.yml` (install/lint/typecheck/test/coverage/build + security scan + dependency-review) and `release.yml` (tag-driven build/SBOM/changelog/provenance/release). Actions are pinned to full SHAs, jobs set least-privilege `permissions`, and production dependency installs are isolated in the read-only build job. Lab reproduction: install, lint, typecheck, test (185 passed), and build all succeed. CI is nevertheless red on master.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P1-001 | P1 | CI is failing on master at the audited commit |
| CI-P2-001 | P2 | dependency-review job is skipped because the dependency graph / Dependabot is disabled |
| CI-P3-001 | P3 | `next lint` is deprecated and will be removed in Next.js 16 |
