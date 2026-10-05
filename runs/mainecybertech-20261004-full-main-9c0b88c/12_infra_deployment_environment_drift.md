# 12_infra_deployment_environment_drift — Prompt 12 - Infrastructure, Deployment, and Environment Drift Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `12_infra_deployment_environment_drift.md` (area INFRA, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| INFRA-P1-001 | P1 | SSH is open to the internet on both droplets (admin_ip_ranges default 0.0.0.0/0 and CI never overrides it) |
| INFRA-P1-002 | P1 | Terraform state-locking fix is incompatible with the pinned Terraform version (use_lockfile requires >= 1.10, workflows pin 1.9) |
| INFRA-P2-003 | P2 | Prometheus alert rules have no delivery path (no Alertmanager) |
| INFRA-P2-004 | P2 | Dev droplet capacity is under-provisioned and the CI value drifts from dev.tfvars.example |
| INFRA-P2-005 | P2 | Operations documentation contradicts the current pipeline and configuration |
| INFRA-P2-006 | P2 | Integration/security env vars referenced by the app schema are not delivered by the deploy pipeline |
| INFRA-P2-007 | P2 | Redis container hardening was weakened and its password remains in process arguments |
| INFRA-P3-008 | P3 | `env/prod.tfvars` is tracked despite an ignore rule that names it |
| INFRA-P3-009 | P3 | Restore test uses a different Postgres major than the backup script and verifies only table counts |
| INFRA-P3-010 | P3 | `docs/RTO_RPO.md` claims Redis AOF persistence that compose does not enable |
| INFRA-P3-011 | P3 | `infra/terraform/README.md` references an `aws/` directory that does not exist |
| INFRA-P3-012 | P3 | Terraform is manual-dispatch only, so the "push to trigger apply" rollback runbook step is a no-op |
