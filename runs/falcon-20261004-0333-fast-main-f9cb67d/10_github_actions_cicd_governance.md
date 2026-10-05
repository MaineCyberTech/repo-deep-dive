# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `falcon-20261004-0333-fast-main-f9cb67d`
- Target: `falcon` @ `f9cb67d` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

Read-only review of the CI/CD governance surface at `f9cb67d`: `.github/workflows/validate.yml`, `.github/workflows/dependabot-merge.yml`, `.github/CODEOWNERS`, and `docs/security/BRANCH_PROTECTION.md`.

- `validate.yml` is a single `validate` job (actionlint, shellcheck, ruff, gitleaks, zizmor, `ci/validate.py`, SBOM/provenance) on every push/PR; the workflow pins tool downloads by sha256 and actions by commit SHA.
- `BRANCH_PROTECTION.md:3-8` records that protection is plan-gated: apply returned `403 Upgrade to GitHub Pro`.
- `dependabot-merge.yml:17-19` declares `contents: write` + `pull-requests: write` and `:46-48` merges after `gh pr checks` without `--match-head-commit`.

No secrets were printed.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P2-001 | P2 | Branch protection and required checks are plan-gated, so `validate` is advisory |
| CI-P2-002 | P2 | Auto-merge workflow holds broad write scope and merges without pinning the checked commit |
