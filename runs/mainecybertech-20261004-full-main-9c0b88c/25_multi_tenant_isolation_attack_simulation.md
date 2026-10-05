# 25_multi_tenant_isolation_attack_simulation — Prompt 25 - Multi-Tenant Isolation Attack Simulation

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `25_multi_tenant_isolation_attack_simulation.md` (area MT, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| MT-P1-001 | P1 | Audit log list and export are not org-scoped by default |
| MT-P1-002 | P1 | Platform dashboards expose all-tenant aggregates to any single-org admin |
| MT-P1-003 | P1 | Public file-request upload authorizes with a permission unioned across all orgs |
| MT-P2-001 | P2 | Admin global search lists all organizations and can fall through unscoped |
| MT-P2-002 | P2 | By-id org filters are conditional, so they fail open if the org gate is not reached |
| MT-P2-003 | P2 | Storage writer path and RLS org-derivation disagree (`orgs/<uuid>/` vs `<uuid>/`) |
| MT-P2-004 | P2 | Realtime/SSE notification channel is scoped by user only, with no org assertion |
| MT-P2-005 | P2 | Platform-admin cross-tenant access is role-key based, broad, and unalerted |
| MT-P2-006 | P2 | Platform-wide report generators run as service role with no tenant guard on scope inputs |
| MT-P3-001 | P3 | No automated cross-tenant isolation regression suite for application-layer scoping |
