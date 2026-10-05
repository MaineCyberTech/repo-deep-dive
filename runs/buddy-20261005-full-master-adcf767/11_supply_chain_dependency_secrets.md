# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

Lockfile committed (`package-lock.json`), Dependabot config present, Actions pinned to SHAs, release SBOM + provenance configured, and the lab test suite is green. Residual supply-chain risk is the accepted nested postcss vulnerability and disabled repository security features. The vendored prompt pack has unconfirmed authorship/licensing.

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-001 | P2 | High-severity postcss advisory remains in the production dependency tree (accepted) |
| SC-P2-002 | P2 | Repository secret-scanning and Dependabot security updates are disabled |
| SC-P2-003 | P2 | Vendored prompt pack authorship and licensing are unconfirmed |
| SC-P3-001 | P3 | gitleaks runs with the default ruleset; no reviewed allowlist file in-repo |
