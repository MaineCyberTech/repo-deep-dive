# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `20261004-full-main-ba4becb`
- Target: `falcon-edge` @ `ba4becb` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

- Read-only analysis of `MaineCyberTech/falcon-edge` at `ba4becb` (git `ba4becb6ecd8fdc0c4e0363a67d7a62f60985788`, branch `main`).
- Deterministic lens (LLM-free) run on the lab (`ci-runner`, HTTP job API) and locally: LICENSE absent; no non-executable tracked `*.sh`; no CRLF tracked text; no tracked secret-like filenames; `.gitattributes` present.
- Wave-0 inventory via `tools/repo_inventory.py` (1,410 files; 5 workflows; 3 routes; 17 schema tables; 56 test files).
- Target repository is not applicable to this domain; the finding records the evidence and the future-readiness trigger.
- No secrets printed; all evidence is file:line references.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P1-001 | P1 | Re-enrollment no longer resets a REVOKED/RETIRED sensor |
| SEC-P2-001 | P2 | HTTP transport hardening (rate limit, headers, slow-client guard) present |
| SEC-P2-002 | P2 | Inventory metrics collector no longer disables SSH host-key verification |
| SEC-P2-003 | P2 | Raw host inventory file no longer world-readable on sensors |
| AUTH-P2-001 | P2 | Device mTLS private key is group-readable (0640), contradicting its documented 0600 |
| SEC-P3-002 | P3 | Lab drill tooling disables SSH host-key and TLS verification |
