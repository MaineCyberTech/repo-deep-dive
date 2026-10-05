# Verification Log

Run: `mainecybertech-20261004-full-main-9c0b88c` (full-domain reconciliation at main `9c0b88c`).

## Method

The repository already carries committed audit ledgers. This pass re-binds them to the
current default-branch commit instead of re-deriving every finding from scratch:

- `a97425d` verification ledger (ancestor of main) — authoritative statuses.
- `178b91c` main-tip focused security/supply-chain/CI run — main-tip statuses.
- `20261002-0344` full run — historical depth for domains the later ledgers did not cover;
  those rows are carried fail-closed and marked *not re-verified at 9c0b88c*.
- Fresh analysis at main for domains with no prior coverage (performance, usability,
  privacy, analytics, mobile/PWA, docs, extensibility).
- Machine deterministic sweep executed on the lab (ci-runner) against a synced
  `mainecybertech` workspace pinned to `9c0b88c`.

## Re-verified at `9c0b88c`

| Finding | Previous | Now | Evidence |
|---|---|---|---|
| DATA-P0-001 | open | verified-fixed | orphan-cleanup lists per prefix, treats null-id as folder; regression tests |
| DR-P0-001 | P0 open | verified-fixed | backup/restore workflows present on default branch (PR #93) |
| DR-P0-002 | P0 open | verified-fixed | db-restore-test.yml:135-201 asserts integrity |
| IR-P0-001 | P0 open | verified-fixed | docs/INCIDENT_RESPONSE.md |
| IR-P0-002 | P0 open | verified-fixed | docs/DATA_BREACH_RESPONSE.md |
| IR-P0-003 | P0 open | verified-fixed | alertmanager Watchdog + deploy-do IR-P0-003 fail-closed guard |
| CI-P1-001 | still-open | still-open | prod env provisioning is an operator action (RELEASE_GATE.md) |
| CI-P3-003 | open | open (main) | deploy-do.yml:862 StrictHostKeyChecking=no; fix #94 exists only on develop |

## Main vs develop

`main` is 6 commits behind `develop`. The develop-only fixes `#94` (deploy SSH host-key
verification, CI-P3-003) and `#95` (known_hosts awk robustness) are **not** on the deployed
default branch; `git merge-base --is-ancestor e4a8338b HEAD` is false.

No secrets were printed; all reads were read-only against the checkout.
