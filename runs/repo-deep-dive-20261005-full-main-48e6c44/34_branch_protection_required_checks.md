# 34_branch_protection_required_checks — Prompt 34 - Branch Protection and Required Checks Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `34_branch_protection_required_checks.md` (area BP, prompt)

## Verification Performed

Live state read via `gh api repos/MaineCyberTech/repo-deep-dive/rulesets/24481135` and `/branches/main/protection`. `main` is governed by an active ruleset `main-protection` (deletion + non-fast-forward + required status checks); the legacy branch-protection API returns 404 'Branch not protected'.

## Findings

| ID | Severity | Title |
|---|---|---|
| BP-P2-001 | P2 | Required checks and PR/review rules do not match the documented gates |
| BP-P2-002 | P2 | Required check 'Lab preflight / lab' is unobtainable for fork PRs |
| BP-P3-001 | P3 | Ruleset bypass actors permanently include the repository role and a deploy key |
