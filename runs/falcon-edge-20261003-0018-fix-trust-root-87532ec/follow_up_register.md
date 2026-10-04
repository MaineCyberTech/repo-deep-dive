# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| EXEC-P1-001 | P1 | Release gate condition: revocation must be terminal before broad/production rollout |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P1-001 | P1 | Consolidated release blocker: revocation is not terminal on the enrollment path |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-001 | P1 | Re-enrollment silently resets a REVOKED or RETIRED sensor to CONFIGURING |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-001 | P2 | Contract documents cursor pagination that the implementation ignores |  |  | verified-fixed | origin/main already contains merged keyset-pagination fix (71cffcd); PS-013 no-op avoided; >500 sensor fixture returns nextCursor at f5811d1; re-audit 2026-10-04: closed |
| API-P2-002 | P2 | `SensorSummary.queueDepth` is documented but never returned |  |  | verified-fixed | No new PR: origin/main already contains merged fix a4b388b (SensorSummary.queueDepth populated from latest heartbeat sample + schema test). PS-012 no-op avoided.; re-audit 2026-10-04: closed |
| ARCH-P2-001 | P2 | The control plane executes a mutable working tree, not a pinned release |  |  | still-open | re-audit 2026-10-04: still-open |
| ARCH-P2-002 | P2 | Edge control plane is a co-tenant single point of failure on the shared lab host |  |  | still-open | re-audit 2026-10-04: still-open |
| CI-P2-001 | P2 | Branch protection and required checks cannot be enforced; pushes to main are only advisory-gated |  |  | still-open | re-audit 2026-10-04: still-open |
| CI-P2-002 | P2 | Dependabot auto-merge does not bind the merge to the exact checked commit |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-001 | P2 | The idempotency table is unbounded and stores full response bodies |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-002 | P2 | No foreign keys and no retention for events, state_reports, heartbeat history |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-003 | P2 | No schema migration mechanism; only CREATE TABLE IF NOT EXISTS |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P2-001 | P2 | Production readiness remains insufficient-evidence |  |  | still-open | re-audit 2026-10-04: still-open |
| FEAT-P2-001 | P2 | `SensorSummary.queueDepth` is documented but never populated |  |  | verified-fixed | No new PR: origin/main already contains merged fix a4b388b (SensorSummary.queueDepth populated from latest heartbeat sample + schema test). PS-012 no-op avoided.; re-audit 2026-10-04: closed |
| FINAL-P2-001 | P2 | Cross-cutting theme: automation artifacts and claims are not continuously bound to their sources |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P2-001 | P2 | Summary documentation drifts from the code (test counts, Dependabot cadence) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P2-002 | P2 | Committed derived artifacts (audit mirrors, closeout response, evidence) can go stale |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-001 | P2 | 900 raw evidence files committed with no retention or size policy |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-002 | P2 | Wave-0 inventory tooling is blind to the route table, schema, and entry points |  |  | still-open | re-audit 2026-10-04: still-open |
| OBS-P2-001 | P2 | No alert delivery path (no Alertmanager/pager); rules are visible only in Prometheus/Grafana |  |  | still-open | re-audit 2026-10-04: still-open |
| OBS-P2-002 | P2 | Inventory alert metrics depend on host-side SSH to each sensor (single point of failure) |  |  | still-open | re-audit 2026-10-04: still-open |
| SC-P2-001 | P2 | CI installs Python dependencies and tools without version pinning or hashes |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SC-P2-002 | P2 | Secret scanning covers only the working tree, never git history |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SC-P2-003 | P2 | CI downloads lint/scan binaries via curl without checksum verification |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SC-P2-004 | P2 | Credential-bearing image artifacts and releases rely solely on private-repo access (owner-accepted) |  |  | still-open | re-audit 2026-10-04: still-open |
| SEC-P2-001 | P2 | HTTP transport has no rate limiting, security headers, or slow-client protection |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-002 | P2 | Inventory metrics collector disables SSH host-key verification |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-003 | P2 | Raw host inventory (MAC/IP/hostnames) is world-readable on sensors and read over the network |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-001 | P2 | Test-count claims are stale and mutually inconsistent (163 vs 197 vs 253) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | No regression test that re-enrollment of a REVOKED/RETIRED sensor is refused |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P3-001 | P3 | Problem `instance` is a static string rather than the request path |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P3-002 | P3 | Vector ingest is at-least-once with no idempotency key or dedupe |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P3-001 | P3 | Bare stdlib HTTP transport has no connection or rate limits |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P3-001 | P3 | CI documentation states a 20-minute Dependabot sweep; the workflow runs daily |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P3-001 | P3 | Queue age-expiry is evaluable only on enqueue; `purge_expired` is unwired |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P3-001 | P3 | `destroyKeys` is recorded in the audit log but performs no key destruction server-side |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P3-002 | P3 | `create-token` prints the plaintext bootstrap token to stdout when `--out` is omitted |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P3-001 | P3 | Hardcoded, drifted sensor endpoint/key list in the inventory metrics collector |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P3-001 | P3 | Generated models, schemas, dashboard JSON, and audit mirrors are committed and can go stale |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P3-001 | P3 | Stale `pending_directives` metric is documented but unfixed |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-001 | P3 | Coverage is reported informationally with no threshold gate |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-002 | P3 | HEAD explicitly lands a known-flaky time-relative test fixture |  |  | verified-fixed | re-audit 2026-10-04: closed |
