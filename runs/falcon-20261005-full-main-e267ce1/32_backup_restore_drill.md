# 32_backup_restore_drill — Prompt 32 - Backup and Restore Drill Audit

- Run: `falcon-20261005-full-main-e267ce1`
- Target: `falcon` @ `e267ce1` (branch `main`)
- Domain: `32_backup_restore_drill.md` (area DR, prompt)

## Verification Performed

Domain subagent produced 1 finding(s) at the bound commit; machine IDs assigned by tools/full_domain.py.

## Findings

| ID | Severity | Title |
|---|---|---|
| DR-P3-001 | P3 | Offsite/dead-man residuals remain owner-side; no scheduled restore assertion in CI |
