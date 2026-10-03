# Patch Plan (20261003-0018-fix-trust-root-87532ec)

Each finding lands in exactly one patch set. The P0-only set (none) would carry no
dependencies. Sets spanning 3+ files or >0.5 day get their own set. Duplicate root
causes are merged; references show every finding covered.

| Set | Findings | Files | Depends on | Effort | Verification command / check |
|---|---|---|---|---|---|
| PS-001 | SEC-P1-001, FINAL-P1-001, EXEC-P1-001, TEST-P2-002 | `src/falcon_control/service.py`, `tests/phase2/test_service_integration.py` | — | S | `python -m unittest tests.phase2.test_service_integration`; re-enroll REVOKED returns 403/409 |
| PS-002 | CI-P2-002 | `.github/workflows/dependabot-merge.yml` | — | S | workflow test where PR head changes mid-check |
| PS-003 | SC-P2-002 | `.github/workflows/validate.yml` | — | S | `gitleaks detect --source .` (git mode) finds an injected dummy secret |
| PS-004 | SC-P2-001, SC-P2-003 | `.github/workflows/validate.yml`, new `requirements-dev.txt` | — | S | corrupted tool download fails; unpinned install rejected |
| PS-005 | TEST-P2-001, HYG-P2-001, CI-P3-001 | `docs/GITHUB_CI.md`, `docs/CURRENT_STATE.md`, `docs/security/BRANCH_PROTECTION.md` | — | S | counts match CI job summary; cadence matches cron |
| PS-006 | DATA-P2-001, DATA-P3-001 | `src/falcon_control/store.py`, `src/falcon_agent/runner.py` | — | S | TTL prune test; queue purge-on-cycle test |
| PS-007 | DATA-P2-002, DATA-P2-003 | `src/falcon_control/store.py`, new `migrations/` | — | M | migration round-trip test; FK violation test |
| PS-008 | OBS-P2-001, OBS-P2-002 | `config/prometheus/edge-alerts.yaml`, monitoring stack, `automation/validation/inventory_metrics.py` | central stack | M | synthetic critical alert delivered end-to-end |
| PS-009 | SEC-P2-002, HYG-P3-001 | `automation/validation/inventory_metrics.py` | known_hosts | S | wrong host key fails closed; sensors loaded from config |
| PS-010 | SEC-P2-003 | `automation/validation/fleet_inventory.py`, systemd unit | owner auth | S | DB mode/ownership test |
| PS-011 | ARCH-P2-001, HYG-P2-002, INV-P3-001 | `deploy/edge-control-plane.service`, `ci/validate.sh`, `closeout/` | release | M | dirty-tree alarm; regen guard fails on mutation |
| PS-012 | FEAT-P2-001, API-P2-002 | `src/falcon_control/service.py`, `api/openapi/falcon-edge-v1.yaml` | — | S | response schema test asserts `queueDepth` |
| PS-013 | API-P2-001 | `src/falcon_control/service.py`, `store.py`, `api/openapi/falcon-edge-v1.yaml` | — | M | >500 sensor fixture returns `nextCursor` |
| PS-014 | API-P3-001, API-P3-002, FEAT-P3-001, FEAT-P3-002 | `src/falcon_control/service.py`, `src/falcon_cli/__main__.py` | — | S | error `instance` = path; ingest replay; token absent without `--out` |
| PS-015 | SEC-P2-001, ARCH-P3-001 | `src/falcon_control/http_server.py` | — | M | N-connection bound; security-header assertion |
| PS-016 | INV-P2-001 | `evidence/`, `ci/validate.sh` | external archive | M | evidence byte-budget gate |
| PS-017 | INV-P2-002 | `repo-deep-dive/tools/repo_inventory.py` | tooling release | M | routes/tables/entry points non-empty |
| PS-018 | OBS-P3-001, TEST-P3-001, TEST-P3-002, CI-P2-001, SC-P2-004, ARCH-P2-002, HYG-P3-002, EXEC-P2-001, FINAL-P2-001 | mixed (see owners in `risk_register.md`) | various | M | per-item validation in the owning domain report |

## Rollback notes

- PS-001 changes authorization: rollback is `git revert` of the guard; keep the added
  test (it documents intended behavior).
- PS-004/PS-005/PS-009 are CI/docs/config only; rollback by revert, no runtime state.
- PS-006/PS-007 change persistence: take a DB copy before applying; migrations must be
  idempotent and forward-compatible so a revert of the code does not break the DB.
- PS-008 touches the central monitoring stack: deploy additively; record backups and a
  rollback note per `AGENTS.md` rule 6.

## Coverage check

Every finding ID from 01/02/03/06/07/08/09/10/11/14/21/22/23 appears in exactly one
set above (deduplicated root causes are listed together).
