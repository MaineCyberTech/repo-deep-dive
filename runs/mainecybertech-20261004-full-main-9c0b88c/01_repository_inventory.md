# 01_repository_inventory — Prompt 01 - Comprehensive Repository Inventory

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `01_repository_inventory.md` (area INV, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| INV-P2-001 | P2 | Committed generated artifacts drift without a gate |
| INV-P2-002 | P2 | Duplicate schema bootstrap SQL can be mistaken for the source of truth |
| INV-P3-001 | P3 | Large committed prompt/audit corpus inflates the application repository |
| INV-P3-002 | P3 | Stale, machine-specific repo path in the agent reference |
