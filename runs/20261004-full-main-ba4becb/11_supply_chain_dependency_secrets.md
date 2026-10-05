# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `20261004-full-main-ba4becb`
- Target: `falcon-edge` @ `ba4becb` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

- Read-only analysis of `MaineCyberTech/falcon-edge` at `ba4becb` (git `ba4becb6ecd8fdc0c4e0363a67d7a62f60985788`, branch `main`).
- Deterministic lens (LLM-free) run on the lab (`ci-runner`, HTTP job API) and locally: LICENSE absent; no non-executable tracked `*.sh`; no CRLF tracked text; no tracked secret-like filenames; `.gitattributes` present.
- Wave-0 inventory via `tools/repo_inventory.py` (1,410 files; 5 workflows; 3 routes; 17 schema tables; 56 test files).
- Target repository is not applicable to this domain; the finding records the evidence and the future-readiness trigger.
- No secrets printed; all evidence is file:line references.

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-001 | P2 | CI installs Python dependencies with exact versions and hashes |
| SC-P2-002 | P2 | Secret scanning covers git history, not only the working tree |
| SC-P2-003 | P2 | CI downloads lint/scan binaries with embedded SHA-256 verification |
| SC-P2-004 | P2 | Credential-bearing image artifacts/releases rely solely on private-repo access |
| SC-P3-001 | P3 | Dependabot now watches the pip toolchain as well as GitHub Actions |
| SUPPLY-P2-001 | P2 | Shipped sensor image auto-applies signed updates with no per-update human gate |
