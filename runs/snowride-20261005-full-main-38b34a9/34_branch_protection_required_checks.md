# 34_branch_protection_required_checks — Prompt 34 - Branch Protection and Required Checks Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `34_branch_protection_required_checks.md` (area BP, prompt)

## Verification Performed

Declared policy (.github/branch-protection.json) requires foundation, migrations, e2e and license-and-vulnerability, strict, code-owner review, conversation resolution, and no force-push/delete. The self-test passed on the lab: 'PASS policy is complete and matches workflow jobs'. Residual: the operator runbook still lists only three checks, and live protection cannot be verified without an admin token.

## Findings

| ID | Severity | Title |
|---|---|---|
| BP-P3-001 | P3 | BRANCH_PROTECTION.md runbook lists a stale required-check set |
| BP-P3-002 | P3 | Live branch protection not verified in this read-only pass |
