# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P2-001 | P2 | Secret scanner echoes the matched secret value into CI logs |
| SEC-P2-002 | P2 | Webhook SSRF guard has a DNS-rebinding TOCTOU window |
| SEC-P3-001 | P3 | gitleaks generic-api-key/jwt hits are false positives (no tracked secret) |
| SEC-P2-003 | P2 | Client-onboarding mutations run without `requirePermission` (authorization outlier) |
| SEC-P2-004 | P2 | MSP platform roles are cross-tenant for org access but not for permissions (inconsistent trust model) |
| SEC-P2-005 | P2 | Forgot-password email redirect still uses attacker-controlled `Origin` header |
| SEC-P2-006 | P2 | `GET /analytics/summary` calls a `get_analytics_summary` RPC that no migration defines |
| SEC-P2-007 | P2 | RLS is bypassed on API requests by default (service-role is the default client) |
| SEC-P3-002 | P3 | `5302116` grants anon/authenticated full DML on every public table (RLS is the only gate) |
| SEC-P3-003 | P3 | CORS reflects any origin with credentials when `CORS_ORIGIN="*"` |
| SEC-P3-004 | P3 | `notification-preferences` PUT accepts a body `organizationId` without `assertOrgScopeMatches` |
| SEC-P3-005 | P3 | `resolveEffectivePermissions` is uncached and fans out 4–6 queries per gated request |
| SEC-P1-001 | P1 | PII field encryption silently degrades to reversible plaintext |
| SEC-P2-008 | P2 | CAPTCHA/Turnstile is bypassed when the secret is unset |
| SEC-P2-009 | P2 | `/health` publicly discloses provider configuration and Redis errors |
| SEC-P3-006 | P3 | Deprecated header and broad API CSP style directive |
| SEC-P3-007 | P3 | M365 webhook `clientState` is compared non-constant-time |
