# Risk Register (consolidated, 20261003-0018-fix-trust-root-87532ec)

Status vocabulary: `open`, `partially-fixed`, `verified-fixed`, `still-open`, `regressed`, `owner-accepted`.
Counts: 0 P0 / 3 P1 / 27 P2 / 12 P3 = 42.

| Risk ID | Finding | Severity | Status | Area | Evidence | Owner | Effort | Mitigation |
|---|---|---|---|---|---|---|---|---|
| R-A01 | Enrollment resets REVOKED/RETIRED sensor to CONFIGURING | P1 | open | SEC | `src/falcon_control/service.py` `h_enroll` | security | S | enrollment lifecycle guard + test |
| R-A02 | Release gate condition on revocation | P1 | open | EXEC | `23_...md` | security | S | same as R-A01 |
| R-A03 | Aggregated release blocker (revocation) | P1 | open | FINAL | `22_...md` | security | S | same as R-A01 |
| R-B01 | 900 evidence files, no retention | P2 | open | INV | `evidence/raw` | build-agent | M | evidence size gate/archive |
| R-B02 | Inventory tool blind to routes/schema | P2 | open | INV | `inventory.json` | tooling | M | parser fix |
| R-B03 | Control plane runs mutable working tree | P2 | open | ARCH | `deploy/edge-control-plane.service` | build-agent | M | pinned deploy |
| R-B04 | Shared-host single point of failure | P2 | open | ARCH | `AGENTS.md`, R-003 | owner | L | dedicated host |
| R-B05 | `queueDepth` documented, not returned | P2 | open | FEAT/API | `_summary`, contract | build-agent | S | populate/remove |
| R-B06 | No transport rate limits/headers | P2 | open | SEC | `http_server.py` | build-agent | M | limiter/headers |
| R-B07 | Inventory SSH host-key checking disabled | P2 | open | SEC | `inventory_metrics.py` | build-agent | S | known_hosts |
| R-B08 | Raw inventory world-readable | P2 | open | SEC | `fleet_inventory.py` | build-agent/owner | S | tighten perms |
| R-B09 | Idempotency table unbounded | P2 | open | DATA | `store.py` | build-agent | S | TTL prune |
| R-B10 | No FKs / retention for events/reports | P2 | open | DATA | `store.py` | build-agent | M | FK + retention |
| R-B11 | No schema migration mechanism | P2 | open | DATA | `store.py` | build-agent | M | migrations |
| R-B12 | Cursor pagination unimplemented | P2 | open | API | contract vs `h_list_sensors` | build-agent | M | keyset pagination |
| R-B13 | Stale/inconsistent test counts | P2 | open | TEST/HYG | docs vs 253 tests | build-agent | S | derive in CI |
| R-B14 | No revoked-enroll regression test | P2 | open | TEST | `test_service_integration.py` | build-agent | S | add test |
| R-B15 | Branch protection unenforceable | P2 | owner-accepted | CI | `BRANCH_PROTECTION.md`, R-012 | owner | S | plan upgrade |
| R-B16 | Dependabot merge not head-bound | P2 | open | CI | `dependabot-merge.yml` | build-agent | S | `--match-head-commit` |
| R-B17 | Unpinned CI deps | P2 | open | SC | `validate.yml` | build-agent | S | pin+hash |
| R-B18 | No git-history secret scan | P2 | open | SC | `gitleaks --no-git` | security | S | git-mode scan |
| R-B19 | Unverified CI tool downloads | P2 | open | SC | `validate.yml` | build-agent | S | checksums |
| R-B20 | Credential-bearing release assets | P2 | owner-accepted | SC | `bake-image.yml`, R-007 | owner | M | encryption/scoping |
| R-B21 | No alert delivery (no pager) | P2 | open | OBS | `CURRENT_STATE.md` | owner | M | Alertmanager |
| R-B22 | Inventory metrics SSH collector SPOF | P2 | open | OBS | `inventory_metrics.py` | build-agent | M | per-sensor export |
| R-B23 | Docs drift (counts/cadence) | P2 | open | HYG | `GITHUB_CI.md` | build-agent | S | fix docs |
| R-B24 | Unguarded derived artifacts | P2 | open | HYG | `closeout/`, `docs/audits/` | build-agent | S | regen guards |
| R-B25 | Automation claims not source-bound | P2 | open | FINAL | multiple | build-agent | M | drift checks |
| R-B26 | Production readiness insufficient-evidence | P2 | open | EXEC | `CURRENT_STATE.md` | owner | L | complete P10 gates |
| R-C01 | Generated models/schemas stale risk | P3 | open | INV | `models_generated.py` | build-agent | S | regen guards |
| R-C02 | Bare HTTP transport no limits | P3 | open | ARCH | `http_server.py` | build-agent | M | bounded pool |
| R-C03 | `destroyKeys` only audited | P3 | open | FEAT | `h_revoke`, runbook | build-agent | S | clarify/implement |
| R-C04 | Token printed to stdout | P3 | open | FEAT | `falcon_cli` | build-agent | S | require `--out` |
| R-C05 | Queue expiry lazy / `purge_expired` unwired | P3 | open | DATA | `queue.py`, `runner.py` | build-agent | S | wire purge |
| R-C06 | Ingest at-least-once, no dedupe | P3 | open | API | `h_ingest_vector` | build-agent | M | dedupe/rotation |
| R-C07 | Problem `instance` static | P3 | open | API | `problem()` | build-agent | S | use path |
| R-C08 | Coverage not gated | P3 | open | TEST | `validate.yml` | build-agent | S | `--fail-under` |
| R-C09 | Flaky time-relative fixture | P3 | open | TEST | HEAD message | build-agent | S | injectable clock |
| R-C10 | Dependabot cadence doc drift | P3 | open | CI | `GITHUB_CI.md` | build-agent | S | fix doc |
| R-C11 | Stale pending-directives metric | P3 | open | OBS | `AGENTS.md` | build-agent | S | fix/remove |
| R-C12 | Hardcoded drifted sensor endpoints | P3 | open | HYG | `inventory_metrics.py` | build-agent | S | config file |

Reconciliation with the pre-existing `ledgers/risk_register.md`: R-014 (security trust
boundaries) is `verified-fixed` for sensor routes and ingest but the enrollment-path
revocation bypass found here is a related open surface (R-A01). R-003, R-012, R-015,
R-016 remain open/owner-accepted and are represented above.

## Finding index

| ID | Severity | Title |
|---|---|---|
| EXEC-P1-001 | P1 | Release gate condition: revocation must be terminal before broad/production rollout |
| FINAL-P1-001 | P1 | Consolidated release blocker: revocation is not terminal on the enrollment path |
| SEC-P1-001 | P1 | Re-enrollment silently resets a REVOKED or RETIRED sensor to CONFIGURING |
| API-P2-001 | P2 | Contract documents cursor pagination that the implementation ignores |
| API-P2-002 | P2 | `SensorSummary.queueDepth` is documented but never returned |
| ARCH-P2-001 | P2 | The control plane executes a mutable working tree, not a pinned release |
| ARCH-P2-002 | P2 | Edge control plane is a co-tenant single point of failure on the shared lab host |
| CI-P2-001 | P2 | Branch protection and required checks cannot be enforced; pushes to main are only advisory-gated |
| CI-P2-002 | P2 | Dependabot auto-merge does not bind the merge to the exact checked commit |
| DATA-P2-001 | P2 | The idempotency table is unbounded and stores full response bodies |
| DATA-P2-002 | P2 | No foreign keys and no retention for events, state_reports, heartbeat history |
| DATA-P2-003 | P2 | No schema migration mechanism; only CREATE TABLE IF NOT EXISTS |
| EXEC-P2-001 | P2 | Production readiness remains insufficient-evidence |
| FEAT-P2-001 | P2 | `SensorSummary.queueDepth` is documented but never populated |
| FINAL-P2-001 | P2 | Cross-cutting theme: automation artifacts and claims are not continuously bound to their sources |
| HYG-P2-001 | P2 | Summary documentation drifts from the code (test counts, Dependabot cadence) |
| HYG-P2-002 | P2 | Committed derived artifacts (audit mirrors, closeout response, evidence) can go stale |
| INV-P2-001 | P2 | 900 raw evidence files committed with no retention or size policy |
| INV-P2-002 | P2 | Wave-0 inventory tooling is blind to the route table, schema, and entry points |
| OBS-P2-001 | P2 | No alert delivery path (no Alertmanager/pager); rules are visible only in Prometheus/Grafana |
| OBS-P2-002 | P2 | Inventory alert metrics depend on host-side SSH to each sensor (single point of failure) |
| SC-P2-001 | P2 | CI installs Python dependencies and tools without version pinning or hashes |
| SC-P2-002 | P2 | Secret scanning covers only the working tree, never git history |
| SC-P2-003 | P2 | CI downloads lint/scan binaries via curl without checksum verification |
| SC-P2-004 | P2 | Credential-bearing image artifacts and releases rely solely on private-repo access (owner-accepted) |
| SEC-P2-001 | P2 | HTTP transport has no rate limiting, security headers, or slow-client protection |
| SEC-P2-002 | P2 | Inventory metrics collector disables SSH host-key verification |
| SEC-P2-003 | P2 | Raw host inventory (MAC/IP/hostnames) is world-readable on sensors and read over the network |
| TEST-P2-001 | P2 | Test-count claims are stale and mutually inconsistent (163 vs 197 vs 253) |
| TEST-P2-002 | P2 | No regression test that re-enrollment of a REVOKED/RETIRED sensor is refused |
| API-P3-001 | P3 | Problem `instance` is a static string rather than the request path |
| API-P3-002 | P3 | Vector ingest is at-least-once with no idempotency key or dedupe |
| ARCH-P3-001 | P3 | Bare stdlib HTTP transport has no connection or rate limits |
| CI-P3-001 | P3 | CI documentation states a 20-minute Dependabot sweep; the workflow runs daily |
| DATA-P3-001 | P3 | Queue age-expiry is evaluable only on enqueue; `purge_expired` is unwired |
| FEAT-P3-001 | P3 | `destroyKeys` is recorded in the audit log but performs no key destruction server-side |
| FEAT-P3-002 | P3 | `create-token` prints the plaintext bootstrap token to stdout when `--out` is omitted |
| HYG-P3-001 | P3 | Hardcoded, drifted sensor endpoint/key list in the inventory metrics collector |
| INV-P3-001 | P3 | Generated models, schemas, dashboard JSON, and audit mirrors are committed and can go stale |
| OBS-P3-001 | P3 | Stale `pending_directives` metric is documented but unfixed |
| TEST-P3-001 | P3 | Coverage is reported informationally with no threshold gate |
| TEST-P3-002 | P3 | HEAD explicitly lands a known-flaky time-relative test fixture |
