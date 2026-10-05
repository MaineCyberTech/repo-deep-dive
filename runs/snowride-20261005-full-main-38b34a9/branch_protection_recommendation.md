# Branch protection recommendation — snowride @ `38b34a9`

Companion artifact for `34_branch_protection_required_checks.md`.

## Declared policy (in-repo)

`.github/branch-protection.json` requires, for `main`:

- strict required checks: `foundation`, `migrations`, `e2e`,
  `license-and-vulnerability`;
- >= 1 approving review, code-owner review, dismiss stale reviews;
- conversation resolution; enforce admins; no force-push; no deletions.

`node scripts/verify-branch-protection.mjs --self-test` passed on the lab and
printed the four checks matching the workflow job names across
`.github/workflows/`.

## Recommendations

1. **Live evidence.** Run the non-self-test audit with an admin token and store
   the raw PASS output under `evidence/` (`BP-P3-002`).
2. **Fix the runbook drift.** `docs/runbooks/BRANCH_PROTECTION.md` still lists
   only three checks; update it to include `license-and-vulnerability`
   (`BP-P3-001`).
3. **Reviewer bus factor.** Replace the personal `@MaineCyberTech` CODEOWNERS
   entry with an organisation team handle (`CI-P3-001`).
4. **Branch coverage.** The declared policy covers only `main`; add release/
   hotfix rulesets if those branches are introduced.

No branch-protection setting can be applied from the repository itself; live
changes require an admin token and remain an operator action.
