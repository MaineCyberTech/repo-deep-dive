# 21_repo_hygiene_maintainability — Prompt 21 - Repository Hygiene, Maintainability, and Code Health Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `21_repo_hygiene_maintainability.md` (area HYGIENE, prompt)

## Verification Performed

Hygiene: monorepo with workspaces, prettier, eslint, .gitattributes LF policy, .gitleaks.toml, LICENSE and CONTRIBUTING. Residual: only apps/web has a lint script; the other four workspaces are unlinted. Multi-MB generated evidence exports remain tracked (see INV-P2-001).

## Findings

| ID | Severity | Title |
|---|---|---|
| HYGIENE-P2-001 | P2 | Only apps/web is linted; four workspaces have no lint script |
| HYGIENE-P2-002 | P2 | Large generated evidence artifacts inflate the repository |
