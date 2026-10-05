# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

Reviewed all 12 workflows under `.github/workflows/`. Actions are SHA-pinned and jobs declare `permissions:`; the reusable lab-preflight gate and the required-check drift are covered under branch protection.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P2-001 | P2 | Required lab-preflight check cannot pass on fork pull requests |
| CI-P2-002 | P2 | CI does not run shellcheck/actionlint on the pack's own shell/yaml despite shipping the scanners |
