# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

Supply chain: actions pinned to commit SHAs, node/postgres bases digest-pinned, @grpc/grpc-js overridden to 1.14.5 (package-lock.json:1003), Dependabot with grouped security updates, and a merge-gating supply-chain workflow. gitleaks reported no leaks. Residual: docs/SUPPLY_CHAIN.md still describes the pre-fix advisory posture, and registry signature verification is continue-on-error.

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-001 | P2 | docs/SUPPLY_CHAIN.md is stale against the shipped supply-chain gates |
| SC-P3-001 | P3 | Registry signature verification is continue-on-error (provenance not blocking) |
