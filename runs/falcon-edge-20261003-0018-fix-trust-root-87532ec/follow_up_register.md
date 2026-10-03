# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| EXEC-P1-001 | P1 | Release gate condition: revocation must be terminal before broad/production rollout |  |  | partially-fixed | terminal revocation guard + regression test; draft PR awaiting human review |
| FINAL-P1-001 | P1 | Consolidated release blocker: revocation is not terminal on the enrollment path |  |  | partially-fixed | terminal revocation guard + regression test; draft PR awaiting human review |
| SEC-P1-001 | P1 | Re-enrollment silently resets a REVOKED or RETIRED sensor to CONFIGURING |  |  | partially-fixed | terminal revocation guard + regression test; draft PR awaiting human review |
| API-P2-001 | P2 | Contract documents cursor pagination that the implementation ignores |  |  | open |  |
| API-P2-002 | P2 | `SensorSummary.queueDepth` is documented but never returned |  |  | open |  |
| ARCH-P2-001 | P2 | The control plane executes a mutable working tree, not a pinned release |  |  | open |  |
| ARCH-P2-002 | P2 | Edge control plane is a co-tenant single point of failure on the shared lab host |  |  | open |  |
| CI-P2-001 | P2 | Branch protection and required checks cannot be enforced; pushes to main are only advisory-gated |  |  | open |  |
| CI-P2-002 | P2 | Dependabot auto-merge does not bind the merge to the exact checked commit |  |  | partially-fixed | draft PR #18; actionlint+pytest+gitleaks+run-block test green |
| DATA-P2-001 | P2 | The idempotency table is unbounded and stores full response bodies |  |  | open |  |
| DATA-P2-002 | P2 | No foreign keys and no retention for events, state_reports, heartbeat history |  |  | open |  |
| DATA-P2-003 | P2 | No schema migration mechanism; only CREATE TABLE IF NOT EXISTS |  |  | open |  |
| EXEC-P2-001 | P2 | Production readiness remains insufficient-evidence |  |  | open |  |
| FEAT-P2-001 | P2 | `SensorSummary.queueDepth` is documented but never populated |  |  | open |  |
| FINAL-P2-001 | P2 | Cross-cutting theme: automation artifacts and claims are not continuously bound to their sources |  |  | open |  |
| HYG-P2-001 | P2 | Summary documentation drifts from the code (test counts, Dependabot cadence) |  |  | open |  |
| HYG-P2-002 | P2 | Committed derived artifacts (audit mirrors, closeout response, evidence) can go stale |  |  | open |  |
| INV-P2-001 | P2 | 900 raw evidence files committed with no retention or size policy |  |  | open |  |
| INV-P2-002 | P2 | Wave-0 inventory tooling is blind to the route table, schema, and entry points |  |  | open |  |
| OBS-P2-001 | P2 | No alert delivery path (no Alertmanager/pager); rules are visible only in Prometheus/Grafana |  |  | open |  |
| OBS-P2-002 | P2 | Inventory alert metrics depend on host-side SSH to each sensor (single point of failure) |  |  | open |  |
| SC-P2-001 | P2 | CI installs Python dependencies and tools without version pinning or hashes |  |  | open |  |
| SC-P2-002 | P2 | Secret scanning covers only the working tree, never git history |  |  | open |  |
| SC-P2-003 | P2 | CI downloads lint/scan binaries via curl without checksum verification |  |  | open |  |
| SC-P2-004 | P2 | Credential-bearing image artifacts and releases rely solely on private-repo access (owner-accepted) |  |  | open |  |
| SEC-P2-001 | P2 | HTTP transport has no rate limiting, security headers, or slow-client protection |  |  | open |  |
| SEC-P2-002 | P2 | Inventory metrics collector disables SSH host-key verification |  |  | open |  |
| SEC-P2-003 | P2 | Raw host inventory (MAC/IP/hostnames) is world-readable on sensors and read over the network |  |  | open |  |
| TEST-P2-001 | P2 | Test-count claims are stale and mutually inconsistent (163 vs 197 vs 253) |  |  | open |  |
| TEST-P2-002 | P2 | No regression test that re-enrollment of a REVOKED/RETIRED sensor is refused |  |  | partially-fixed | terminal revocation guard + regression test; draft PR awaiting human review |
| API-P3-001 | P3 | Problem `instance` is a static string rather than the request path |  |  | open |  |
| API-P3-002 | P3 | Vector ingest is at-least-once with no idempotency key or dedupe |  |  | open |  |
| ARCH-P3-001 | P3 | Bare stdlib HTTP transport has no connection or rate limits |  |  | open |  |
| CI-P3-001 | P3 | CI documentation states a 20-minute Dependabot sweep; the workflow runs daily |  |  | open |  |
| DATA-P3-001 | P3 | Queue age-expiry is evaluable only on enqueue; `purge_expired` is unwired |  |  | open |  |
| FEAT-P3-001 | P3 | `destroyKeys` is recorded in the audit log but performs no key destruction server-side |  |  | open |  |
| FEAT-P3-002 | P3 | `create-token` prints the plaintext bootstrap token to stdout when `--out` is omitted |  |  | open |  |
| HYG-P3-001 | P3 | Hardcoded, drifted sensor endpoint/key list in the inventory metrics collector |  |  | open |  |
| INV-P3-001 | P3 | Generated models, schemas, dashboard JSON, and audit mirrors are committed and can go stale |  |  | open |  |
| OBS-P3-001 | P3 | Stale `pending_directives` metric is documented but unfixed |  |  | open |  |
| TEST-P3-001 | P3 | Coverage is reported informationally with no threshold gate |  |  | open |  |
| TEST-P3-002 | P3 | HEAD explicitly lands a known-flaky time-relative test fixture |  |  | open |  |
