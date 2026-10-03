# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: SEC
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/06_security_authz_tenancy_audit.md
- Scope limitations: static review only; no exploit execution against a live service. Secrets inspected as file paths/types only (redacted).

## Scope

Reviewed authentication (mTLS, bootstrap token), authorization (certificate-fingerprint role resolution, path sensor-id binding, lifecycle gates), input validation, secret handling, scanning, and the ingest/update trust boundaries. No live penetration testing performed.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `src/falcon_control/service.py` | Source | Authn/authz, lifecycle | `_resolve_identity`, `_authorize`, `_lifecycle_error` |
| `src/falcon_control/pki.py` | Source | Trust root, cert issuance | pinned operator fingerprint |
| `src/falcon_control/tokens.py` | Source | Bootstrap tokens | single-use, hashed |
| `src/falcon_control/http_server.py` | Source | Transport identity | SHA-256 of DER cert |
| `src/falcon_control/store.py` | Source | Persistence | revocation mapping |
| `ci/secret_scan.py`, `.gitleaks.toml` | Scanners | Secret detection | working tree only |
| `automation/validation/inventory_metrics.py` | Source | SSH handling | `StrictHostKeyChecking=no` |
| `auto.../fleet_inventory.py` | Source | Active discovery | raw identifiers retained |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `h_enroll` trace | Static | Revocation | no REVOKED guard → SEC-P1-001 |
| `server_ssl_context` read | Static | mTLS posture | `CERT_OPTIONAL`, TLS 1.2+ |
| Operator fingerprint flow | Static | Privilege escalation | CN ignored; fingerprint pinned (good) |
| Ingest attribution | Static | Spoofing | `sensor_id` overwritten + audited (good) |
| Scanner scope read | Static | Secret history | `--no-git` → SUPPLY-P2-002 |

## Executive Summary

The trust-root work in this branch is strong: operator authority requires an immutable fingerprint pin (CN alone never grants it), sensor certificates get server-pinned subjects (CSR subject ignored), ingest events are attributed to the certificate identity with mismatches audited, and revoked/retired sensors are denied on all sensor routes. The one material gap is that **re-enrollment can move a REVOKED (or a RETIRED) sensor back to CONFIGURING**, silently undoing revocation. Secondary gaps: no transport rate limiting/security headers, SSH host-key verification disabled in the inventory metrics collector, and raw host inventory data readable broadly.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Operator identity | `_operator_fingerprint` | Role grant | Pinned, fail-closed | Low | SEC-P1-003 fix |
| Sensor identity | `get_sensor_by_fingerprint` | Role grant | DB mapping | Low | unmap on renewal |
| Revocation | `_lifecycle_error` | Deny revoked | Implemented | High | bypassed by enroll |
| Bootstrap token | `tokens.create_token` | Scoped enrollment | Single-use, hashed | Low | TTL 60–604800s |
| Idempotency | `_idempotent` | Replay safety | Implemented | Low | unbounded (DATA) |
| Ingest | `h_ingest_vector` | Vector batch | Cert attributed | Low | at-least-once |
| Transport | `http_server.py` | mTLS | TLS 1.2+, optional client cert | Med | no limits |
| Secret scan | `ci/secret_scan.py` | Leak detection | Tree only | Med | no history |
| Inventory SSH | `inventory_metrics.py` | Host-key check | Disabled | Med | MITM |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 5 | `_resolve_identity` | — | — |
| Session tokens/cookies | 4 | bootstrap token | TTL up to 7d | keep lab-bound |
| JWT validation | N/A | none | — | — |
| CSRF/CORS | 3 | no browser surface | N/A | document |
| Rate limits | 2 | none | transport | SEC-P2-001 |
| Security headers | 2 | none | transport | SEC-P2-001 |
| Input/output validation | 5 | `validate_payload` | — | — |
| File handling | 4 | update verify | — | — |
| API permissions | 4 | cert role + path bind | revocation reset | SEC-P1-001 |
| Admin permissions | 4 | operator pin | — | — |
| Tenant/org/workspace isolation | 3 | single-site | multi-site absent | document |
| RLS policies | N/A | SQLite lab | — | — |

## Detailed Review

### Item: Revocation

- Evidence: `service._lifecycle_error`, `h_enroll`, `store.set_state`, `tests/phase2/test_service_integration.py`
- What it does: REVOKED sensors get 403 on sensor routes; RETIRED is terminal for renewal/ingest.
- Missing controls: `h_enroll` never inspects the existing sensor's lifecycle; it issues a new cert and sets CONFIGURING.
- Risks: SEC-P1-001.

### Item: Ingest trust boundary

- Evidence: `h_ingest_vector` — cert sensor id overwrites client `sensor_id`, mismatches audited; `INGEST_MAX_EVENTS=1000`, `INGEST_FILE_CAP_BYTES=128MiB`.
- Current controls: strong attribution; bounds on batch size.
- Missing controls: no idempotency/dedupe (documented as consumer concern).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEC-001 | Auth provider | mTLS + pin | strong | — | — | — |
| SEC-002 | Session tokens | bootstrap token | hashed/single-use | — | — | — |
| SEC-003 | JWT validation | N/A | — | — | — | — |
| SEC-004 | CSRF/CORS | no browser | N/A | — | — | — |
| SEC-005 | Rate limits | none | none | brute/DoS | P2 | SEC-P2-001 |
| SEC-006 | Security headers | none | none | — | P2 | SEC-P2-001 |
| SEC-007 | Input validation | `validate_payload` | strong | — | — | — |
| SEC-008 | File handling | update verify | strong | — | — | — |
| SEC-009 | API permissions | `_authorize` | strong | revoke reset | P1 | SEC-P1-001 |
| SEC-010 | Admin permissions | operator pin | strong | — | — | — |
| SEC-011 | Tenant isolation | single-site | — | — | P3 | document |
| SEC-012 | RLS | N/A | — | — | — | — |

## Findings

### Finding ID: SEC-P1-001 - Re-enrollment silently resets a REVOKED or RETIRED sensor to CONFIGURING

- Severity: P1
- Confidence: High
- Area: SEC
- Evidence:
  - `src/falcon_control/service.py` — `h_enroll` (existing-device branch): `self.store.update_sensor(sensor_id, ..., lifecycle_state="CONFIGURING", ...)` with no check on `existing["lifecycle_state"]`
  - `src/falcon_control/service.py` — `_authorize` returns early for `auth == "bootstrap"` before any lifecycle check
  - `src/falcon_control/store.py` — `update_sensor` simply writes the new state
  - `api/openapi/falcon-edge-v1.yaml` — `EnrollmentRequest`/`createEnrollment`
- What is happening: a bootstrap token bound to a sensor's `sensorId` (or redeemed by the device's `deviceUuid`) causes enrollment to issue a fresh certificate and set the sensor to CONFIGURING, regardless of prior REVOKED/RETIRED state. The prior certificate's fingerprint is replaced, so the revoked identity is effectively reinstated.
- Why it matters: revocation/retirement is meant to be a terminal security control (the C6 hardening theme of this branch). This path lets an operator holding a token undo it, and the enrollment leaves no explicit "revocation override" audit marker.
- User / business impact: a compromised/decommissioned device can be returned to service without a deliberate re-provisioning step.
- Security / privacy / reliability impact: revocation bypass; violates the documented "RETIRED is terminal" intent.
- Recommended fix: in `h_enroll`, if `existing is not None` and `existing["lifecycle_state"] in ("REVOKED", "RETIRED")`, return 403/409 (`SENSOR_REVOKED`/`SENSOR_RETIRED`) unless an explicit, audited `reprovision` flag is supplied by an operator with elevated intent.
- Suggested validation: test that enrolling a REVOKED sensor with a correctly bound token returns 403 and leaves the state REVOKED (add to `tests/phase2/test_service_integration.py`).
- Owner suggestion: security owner
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: `POST /api/v1/enrollments` (bootstrap bearer) → `ControlPlaneService.h_enroll` → `store.update_sensor(lifecycle_state="CONFIGURING")`
- Attack path: holder of a bound bootstrap token (or a re-imaged/revoked device) → enroll endpoint → revocation cleared → new certificate valid for all sensor routes.

### Finding ID: SEC-P2-001 - HTTP transport has no rate limiting, security headers, or slow-client protection

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `src/falcon_control/http_server.py` — `ThreadingHTTPServer`, `_dispatch` writes only `Content-Type`/`Content-Length`
  - `src/falcon_control/service.py` — `problem()` responses include no security headers
- What is happening: the only queued mitigation is a 2 MiB body cap. There are no `X-Content-Type-Options`/`Cache-Control` headers, no per-peer rate limit on `/enrollments` or operator routes, and no connection timeout.
- Why it matters: defense-in-depth is absent; a lab-network peer can exhaust threads or brute-force operator actions.
- User / business impact: availability risk; noisy-neighbor susceptibility.
- Security / privacy / reliability impact: DoS and brute-force exposure (token entropy still makes enrollment brute force impractical).
- Recommended fix: add a bounded request rate limiter keyed by peer fingerprint/IP, request timeouts, and security response headers; or front the service with a reverse proxy.
- Suggested validation: concurrency/rate test; header assertion in the phase2 integration test.
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: SEC-P2-002 - Inventory metrics collector disables SSH host-key verification

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `automation/validation/inventory_metrics.py` — `ssh -i <key> -o StrictHostKeyChecking=no -o ConnectTimeout=6 falcon@<ip> ...`
  - `AGENTS.md` — SSH host key change for the reflashed Zero W is tracked manually
- What is happening: the hourly inventory metrics job accepts any host key, so a MITM on the management path can answer as a sensor.
- Why it matters: the collector reads the inventory DB and emits alert metrics; spoofed data can hide failure or inject false health.
- User / business impact: unreliable alerting.
- Security / privacy / reliability impact: MITM/spoofing of an internal read.
- Recommended fix: pin sensor host keys in `known_hosts` (or `StrictHostKeyChecking=yes` with a managed known_hosts), consistent with the SSH host-key tracking already done.
- Suggested validation: run collector with a wrong host key and assert it fails closed.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: known_hosts management
- Status: open

### Finding ID: SEC-P2-003 - Raw host inventory (MAC/IP/hostnames) is world-readable on sensors and read over the network

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `automation/validation/inventory_metrics.py` — docstring: "the database is world-readable"
  - `automation/validation/fleet_inventory.py` — `hosts` table stores raw `mac`, `ip`, `hostname`
  - `fleet_inventory.py export` — hashes identifiers only when `export` is invoked (ED-10)
- What is happening: the on-sensor SQLite DB stores raw identifiers and is readable beyond the owning account; `associate` prints raw MACs/ips; only the explicit `export` path hashes.
- Why it matters: the inventory is a map of the owner's network (hosts, open services, versions) — sensitive reconnaissance material.
- User / business impact: privacy/recon exposure if a sensor is compromised.
- Security / privacy / reliability impact: sensitive data at rest with broad read permission.
- Recommended fix: restrict the DB and its directory to the `falcon-agent`/root account; default `show`/`associate` output to hashed identifiers and require an explicit flag for raw.
- Suggested validation: assert file mode/ownership in unit tests; verify unprivileged read fails.
- Owner suggestion: build-agent + owner
- Effort estimate: S
- Dependencies: owner authorization (ED-20)
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Revocation reset | P1 | Medium | Security control bypass | `h_enroll` | SEC-P1-001 |
| Transport DoS/noise | P2 | Medium | Availability | `http_server.py` | SEC-P2-001 |
| SSH MITM | P2 | Low | False health data | `inventory_metrics.py` | SEC-P2-002 |
| Recon data exposure | P2 | Medium | Privacy | `fleet_inventory.py` | SEC-P2-003 |

## Recommendations

### Immediate / Release Blocking
SEC-P1-001 (revocation reset) — fix before broad or production rollout.

### This Week
Pin SSH host keys; restrict inventory DB permissions.

### This Month
Transport rate limits + security headers.

### Later / Platform Evolution
Multi-site tenancy/isolation model.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| REVOKED/TIRED enroll guard | closes revocation bypass | `service.py` | new test |
| `StrictHostKeyChecking=yes` | stops MITM | `inventory_metrics.py` | failure test |
| Require `--out` for create-token | secret hygiene | `falcon_cli` | CLI test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Transport limits/headers | P2 | build-agent | M | none |
| History secret scan | P2 | build-agent | S | see 11 |
| Inventory data minimization | P2 | build-agent | S | owner |

## Suggested Tests

- Security: revoked/retired re-enrollment refusal; role escalation attempts (CSR CN=operator already covered).
- Transport: concurrent-connection bound; security-header presence.
- Collector: wrong-host-key fail-closed.

## Suggested Documentation Updates

- `docs/security/SECURITY_BOUNDARY.md`: state the revocation-is-terminal rule and the re-provisioning exception (or absence).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is re-enrollment of a revoked sensor a required recovery path? | fixes scope of SEC-P1-001 | owner decision |
| Is a reverse proxy planned in front of the control plane? | transport fix choice | architecture plan |

## Appendix

Strengths confirmed: operator fingerprint pinning (`_resolve_identity` + `pki.OPERATOR_FINGERPRINT_PIN_FILE`), server-pinned cert subjects, ingest `sensor_id` overwrite + audit, secrets never printed by scanners (path/line only), Ed25519-signed directives with expiry/replay checks. Secret-adjacent files were inventoried by `inventory.json`; no secret values were read or printed in this report.
