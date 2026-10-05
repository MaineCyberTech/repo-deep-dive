# 33_incident_tabletop_exercise — Prompt 33 - Incident Tabletop Exercise

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `33_incident_tabletop_exercise.md` (area IR, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| IR-P0-001 | P0 | No platform-level incident response plan, roles, or postmortem process |
| IR-P0-002 | P0 | No data breach response / notification process |
| IR-P0-003 | P0 | Total loss of the monitoring/alerting path has no independent dead-man's-switch receiver |
| IR-P1-001 | P1 | Rollback documentation contradicts itself on SHA-targeted rollback |
| IR-P1-002 | P1 | Bad-migration recovery is manual-only with no automated reverse or staging proof |
| IR-P1-003 | P1 | Worker health failure during deploy is non-fatal |
| IR-P1-004 | P1 | Backups are not verified deeply enough to prove the documented RPO/RTO |
| IR-P1-005 | P1 | Backup bucket configuration is inconsistent between the script, the backup workflow, and the restore test |
| IR-P1-006 | P1 | No runtime detection or alerting for tenant-isolation (RLS) regressions |
| IR-P2-001 | P2 | Several Prometheus metrics are declared but not wired, limiting incident diagnosis |
| IR-P2-002 | P2 | No alerting on audit-trail gaps or privileged (impersonation/admin) abuse |
| IR-P2-003 | P2 | No alerting when webhook dead-letters accumulate or payment reconciliation drifts |
| IR-P2-004 | P2 | Secrets rotation is documented but has no exercised evidence |
| IR-P2-005 | P2 | No platform status/communication surface for MCT's own outages |
| IR-P2-006 | P2 | Migration dry-run result is discarded in CI |
| IR-P3-001 | P3 | Terraform state restore guidance lacks a tested procedure |
| IR-P3-002 | P3 | Monitoring doc and health endpoint disagree on check semantics; Redis severity undocumented in alerts |
