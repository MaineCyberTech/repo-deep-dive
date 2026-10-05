# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

Read-only security review of the lab job API (`tools/lab_api_server.py`), the lab-vpn toolkit, and `.github/workflows/*.yml`. No secret values printed. `grep -rn 'secrets\.' .github/workflows/` and manual line reads were used.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P2-001 | P2 | Workflows interpolate SSH secrets directly into run scripts |
| SEC-P2-002 | P2 | Lab API /sync ignores the supplied token when the workspace already exists |
| SEC-P3-001 | P3 | Lab API token passed via process argv and server bound to all interfaces as root |
