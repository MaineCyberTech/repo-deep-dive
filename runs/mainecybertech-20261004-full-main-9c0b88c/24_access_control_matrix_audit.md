# 24_access_control_matrix_audit — Prompt 24 - Access Control Matrix Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `24_access_control_matrix_audit.md` (area ACM, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| ACM-P1-001 | P1 | Client-onboarding mutations run without any `requirePermission` gate |
| ACM-P2-002 | P2 | `PLATFORM_ADMIN_KEYS` (org traversal) and `ADMIN_BYPASS_KEYS` (permission bypass) are inconsistent trust sets |
| ACM-P2-003 | P2 | RLS is not a database backstop on API requests (service-role is the default client) |
| ACM-P2-004 | P2 | Write and state-transition actions gated by `view` permissions (action mismatch) |
| ACM-P2-005 | P2 | Webhook endpoint and delivery reads are available to any org member (not manage-gated) |
| ACM-P2-006 | P2 | API keys store `expires_at` but nothing enforces or prunes expiry |
| ACM-P2-007 | P2 | Webhook signing secrets are stored plaintext with no rotation or expiry |
| ACM-P2-008 | P2 | Profiles are enumerable by email/id for any authenticated user |
| ACM-P3-001 | P3 | Client-side permission hiding is UI-only for several module actions |
| ACM-P3-002 | P3 | No catalog-lint: referenced permission keys are not checked against the `permissions` table |
| ACM-P3-003 | P3 | Public route surface is broad and has no single documented inventory |
| ACM-P3-004 | P3 | `GET /roles/:id` and `GET /me/permissions` are readable without an admin gate |
| ACM-P3-005 | P3 | RLS policies reference `manage` permissions that no role holds (dead predicates) |
