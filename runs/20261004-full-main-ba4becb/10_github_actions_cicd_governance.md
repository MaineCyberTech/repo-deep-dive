# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `20261004-full-main-ba4becb`
- Target: `falcon-edge` @ `ba4becb` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

- Read-only analysis of `MaineCyberTech/falcon-edge` at `ba4becb` (git `ba4becb6ecd8fdc0c4e0363a67d7a62f60985788`, branch `main`).
- Deterministic lens (LLM-free) run on the lab (`ci-runner`, HTTP job API) and locally: LICENSE absent; no non-executable tracked `*.sh`; no CRLF tracked text; no tracked secret-like filenames; `.gitattributes` present.
- Wave-0 inventory via `tools/repo_inventory.py` (1,410 files; 5 workflows; 3 routes; 17 schema tables; 56 test files).
- Target repository is not applicable to this domain; the finding records the evidence and the future-readiness trigger.
- No secrets printed; all evidence is file:line references.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P2-002 | P2 | bake-image no longer interpolates secrets into script text |
| CI-P2-001 | P2 | CI toolchain is downloaded and hash-verified (pinning enforced) |
| CI-P3-001 | P3 | Branch-protection documentation matches implemented Dependabot-merge behavior |
