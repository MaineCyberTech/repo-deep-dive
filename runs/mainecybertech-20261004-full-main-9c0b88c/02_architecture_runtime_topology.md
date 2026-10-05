# 02_architecture_runtime_topology — Prompt 02 - Architecture and Runtime Topology Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `02_architecture_runtime_topology.md` (area ARCH, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| ARCH-P2-001 | P2 | Single-droplet, single-instance runtime is a hard SPOF |
| ARCH-P2-002 | P2 | API defaults to the service-role DB client (RLS bypass) |
| ARCH-P2-003 | P2 | Prometheus loads rules but has no alert routing |
| ARCH-P3-001 | P3 | Web middleware gates routes on an unverified JWT `exp` |
