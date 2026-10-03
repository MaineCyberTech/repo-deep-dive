# Feature Implementation and Gap Map

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: FEAT
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/03_feature_implementation_map.md
- Scope limitations: no live device exercise; feature status verified against code, contract, and ledgers only.

## Scope

Reviewed implemented/partial features: enrollment, certificate renewal, heartbeat, inventory, desired-state/ETag, state reports, events, Vector ingest, update manifests, recovery directives, quarantine/release/revoke, and the CLI. Cross-checked the OpenAPI contract against `service.ROUTES`.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `src/falcon_control/service.py` | Source | 19 route handlers | feature surface |
| `api/openapi/falcon-edge-v1.yaml` | Contract | Documented operations | 19 paths |
| `src/falcon_agent/runner.py` | Source | Device-side features | desired/update/directive |
| `src/falcon_cli/__main__.py` | Source | Operator commands | 17 subcommands |
| `ledgers/gate_ledger.csv` | Ledger | Claimed gate status | 86/88 PASS |
| `tests/**` (49 files) | Tests | Feature coverage | phase0–10 |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Route↔contract diff | Static | Contract conformance | 19/19 paths present |
| `_summary` field check | Static | Response completeness | `queueDepth` missing |
| Handler review | Static | `destroyKeys` handling | audit only, no key action |
| Enrollment re-entry review | Static | Revocation | no REVOKED guard |

## Executive Summary

Feature coverage is broad and matches the contract's 19 operations. Enrollment, identity, signed state, quarantine/revoke, updates, and recovery are implemented with tests and ledgers. Gaps: the contract advertises cursor pagination the handler does not implement; `SensorSummary.queueDepth` is never populated; the `destroyKeys` revoke flag is only recorded; and re-enrollment can move a REVOKED sensor back to CONFIGURING (tracked as SEC-P1-001).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Enroll | `h_enroll` | Bootstrap + CSR | Implemented | High | revocation bypass (SEC) |
| Renewal | `h_renewal` | Cert rotation | Implemented | Low | device UUID checked |
| Heartbeat | `h_heartbeat` | Telemetry + skew/replay | Implemented | Low | — |
| Inventory | `h_inventory` | Snapshot replace | Implemented | Low | — |
| Desired state | `h_desired_state` | ETag/304 | Implemented | Low | signed |
| State report | `h_state_report` | Apply outcome | Implemented | Low | moves to ACTIVE |
| Events | `h_events` | Batch | Implemented | Low | — |
| Vector ingest | `h_ingest_vector` | Aggregator | Implemented | Low | at-least-once |
| Update manifests | `h_issue_update_manifest` | Signed offer | Implemented | Low | — |
| Recovery directives | `h_issue_recovery_directive` | Signed recovery | Implemented | Low | — |
| Quarantine/release/revoke | handlers | Security states | Implemented | Med | destroyKeys no-op |
| List sensors | `h_list_sensors` | Paginate | Partial | Med | no cursor |
| CLI | `falcon_cli` | Operator UX | Implemented | Low | token to stdout |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Pages/routes | 4 | `ROUTES` | no cursor page | API-P2-001 |
| Components | 4 | modules | no packaging | minor |
| API endpoints | 4 | 19 operations | `queueDepth` missing | FEAT-P2-001 |
| Server actions | 4 | handlers | — | — |
| Workers/jobs | 4 | agent cycle | — | — |
| Database entities | 3 | `store.SCHEMA` | no migrations | DATA |
| Permissions | 4 | cert-role authz | revocation bypass | SEC-P1-001 |
| Audit logs | 4 | `audit_log` | — | — |
| Tests | 4 | 49 files | no revoked-enroll test | TEST-P2-002 |
| Docs | 3 | `docs/**` | stale counts | HYG |
| Workflow states | 5 | `state.py` map | — | — |
| Failure states | 4 | runner recovery | — | — |

## Detailed Review

### Item: Enrollment

- Evidence: `service.h_enroll`; `pki.issue_cert(subject=pki.sensor_subject(...))`
- What it does: redeem single-use token, sign CSR with server-pinned subject, issue cert, seed desired state.
- Current controls: atomic redemption, server-side subject (CSR subject ignored), device-uuid binding.
- Missing controls: no rejection when the bound sensor is REVOKED/RETIRED.
- Risks: SEC-P1-001.

### Item: Sensor summary

- Evidence: `service._summary`, `openapi components.schemas.SensorSummary` (`queueDepth`)
- What it does: returns lifecycle/profile/config/cert fields.
- Missing controls: `queueDepth` documented but never populated from `heartbeat_samples.queue`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FEAT-001 | Routes | `ROUTES` | complete | — | — | — |
| FEAT-002 | Components | `src/**` | modular | — | — | — |
| FEAT-003 | API endpoints | contract | 19 ops | cursor | P2 | API-P2-001 |
| FEAT-004 | Server actions | handlers | — | — | — | — |
| FEAT-005 | Workers | agent | — | — | — | — |
| FEAT-006 | DB entities | `SCHEMA` | — | migrations | P2 | DATA |
| FEAT-007 | Permissions | cert role | strong | revoke reset | P1 | SEC-P1-001 |
| FEAT-008 | Audit logs | `audit` | — | — | — | — |
| FEAT-009 | Tests | `tests/**` | broad | gap | P2 | TEST-P2-002 |
| FEAT-010 | Docs | docs | extensive | drift | P2 | HYG |
| FEAT-011 | Workflow states | `state.py` | complete | — | — | — |
| FEAT-012 | Failure states | runner | good | — | — | — |

## Findings

### Finding ID: FEAT-P2-001 - `SensorSummary.queueDepth` is documented but never populated

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `api/openapi/falcon-edge-v1.yaml` — `SensorSummary.properties.queueDepth`
  - `src/falcon_control/service.py` — `_summary()` omits `queueDepth`
  - `src/falcon_control/store.py` — `heartbeat_samples` table holds queue data
- What is happening: the contract advertises a queue-depth field that the operator API never returns.
- Why it matters: operators/automation reading the contract expect the field; monitoring must scrape a separate path.
- User / business impact: broken client assumptions; extra plumbing.
- Security / privacy / reliability impact: low.
- Recommended fix: populate `queueDepth` from the latest heartbeat sample, or remove it from the contract.
- Suggested validation: contract test asserting `queueDepth` present/absent per decision.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: FEAT-P3-001 - `destroyKeys` is recorded in the audit log but performs no key destruction server-side

- Severity: P3
- Confidence: High
- Area: FEAT
- Evidence:
  - `src/falcon_control/service.py` — `h_revoke` computes `destroyKeys` only for the audit detail
  - `src/falcon_cli/__main__.py` — `retire` sets `destroy_keys=True`
  - `docs/runbooks/retirement-key-destruction.md` — "key-destruction intent recorded in the audit log"
- What is happening: the control plane retains the issued sensor cert (`secrets/sensors/<id>.crt.pem`) and the fingerprint row after retirement; physical destruction is delegated to on-device wiping.
- Why it matters: a reader of the audit log may believe server-side key material was destroyed when it was not.
- User / business impact: misleading retirement evidence.
- Security / privacy / reliability impact: retained cert material for retired identities.
- Recommended fix: on `destroyKeys`, delete the sensor cert file and (optionally) null the fingerprint mapping, or rename the flag to `recordDestructionIntent` and document it.
- Suggested validation: retire a test sensor and assert the cert file is removed / the field semantics are explicit.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: FEAT-P3-002 - `create-token` prints the plaintext bootstrap token to stdout when `--out` is omitted

- Severity: P3
- Confidence: High
- Area: FEAT
- Evidence:
  - `src/falcon_cli/__main__.py` — `cmd_create_token` returns `{"token": token["token"]}` when no `--out`
  - `AGENTS.md` — "never pass secrets on a command line"
- What is happening: without `--out`, the single-use token (a credential) is emitted in command output, which may be captured to logs/terminal scrollback.
- Why it matters: contradicts the repo's own no-secret-printing doctrine; captured tokens are single-use but grant enrollment.
- User / business impact: accidental credential exposure in shell history/logs.
- Security / privacy / reliability impact: low-to-medium credential exposure.
- Recommended fix: require `--out` (or `--stdout` with an explicit warning) and never include the token in the structured result by default.
- Suggested validation: CLI test asserting the token is absent from non-`--out` output.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Revocation reset via re-enroll | P1 | Medium | Security control bypass | `h_enroll` | SEC-P1-001 |
| Contract/response drift | P2 | High | Client breakage | `_summary` | FEAT-P2-001 |
| Token to stdout | P3 | Medium | Credential exposure | CLI | FEAT-P3-002 |

## Recommendations

### Immediate / Release Blocking
Fix SEC-P1-001 before broad/production rollout.

### This Week
Resolve `queueDepth`; harden `create-token` output.

### This Month
Clarify `destroyKeys` semantics.

### Later / Platform Evolution
Cursor pagination across list APIs.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Populate/remove `queueDepth` | contract truth | `service.py` | contract test |
| Require `--out` for tokens | secret hygiene | `falcon_cli` | CLI test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Cursor pagination | P2 | build-agent | M | store query |
| destroyKeys semantics | P3 | build-agent | S | none |

## Suggested Tests

- Contract: assert every documented `SensorSummary` field is produced.
- Security: assert re-enrollment of a REVOKED sensor is refused (TEST-P2-002).
- CLI: assert token absent from default output.

## Suggested Documentation Updates

- `docs/phase2/DESIGN.md`: document pagination/`queueDepth` status.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is re-enrollment of a revoked sensor intended? | determines SEC-P1-001 fix | owner decision |
| Is `destroyKeys` meant to be intent-only? | determines FEAT-P3-001 fix | owner decision |

## Appendix

Route classes: public 1 (`healthz`), bootstrap 1 (`enrollments`), sensor 9, operator 8. Gate ledger 86/88 PASS.
