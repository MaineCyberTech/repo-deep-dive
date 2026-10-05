# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

Reviewed `.github/dependabot.yml`, workflow action pinning, `.gitleaks.toml`, and the lab dependency pins. GitHub Actions are SHA-pinned and the org scan downloads tools by version with sha256 verification.

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-001 | P2 | Infrastructure toolchain is pinned only to lower bounds |
| SC-P3-001 | P3 | gitleaks allowlist can mask real 40-hex OSQUERY keys and a token-shaped string |
