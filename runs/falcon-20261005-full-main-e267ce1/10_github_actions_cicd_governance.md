# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `falcon-20261005-full-main-e267ce1`
- Target: `falcon` @ `e267ce1` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

Domain subagent produced 2 finding(s) at the bound commit; machine IDs assigned by tools/full_domain.py.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P1-001 | P1 | Branch protection and required checks are not enforced server-side |
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection |
