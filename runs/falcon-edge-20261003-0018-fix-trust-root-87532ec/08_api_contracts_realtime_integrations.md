# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: API
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/08_api_contracts_realtime_integrations.md
- Scope limitations: static contract-vs-implementation comparison; no live API calls.

## Scope

Reviewed the OpenAPI 3.1 contract (`api/openapi/falcon-edge-v1.yaml`), the route table and handlers in `src/falcon_control/service.py`, error format, idempotency, the Vector ingest integration, and the agent client (`src/falcon_agent/client.py`). No WebSocket/realtime channel exists.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `api/openapi/falcon-edge-v1.yaml` | Contract | 19 paths, schemas | authoritative |
| `src/falcon_control/service.py` | Source | handlers + `ROUTES` | 19 routes |
| `src/falcon_control/client`? `src/falcon_agent/client.py` | Source | retries/errors | transient vs definitive |
| `ci/lint_openapi.py` | CI | contract lint | in `validate.sh` |
| `tests/phase1/test_contract_routes.py` | Test | route conformance | present |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Path-by-path diff | Static | Missing/extra endpoints | all 19 present |
| Parameter check | Static | `cursor`/`nextCursor` | not implemented |
| Schema field check | Static | `queueDepth` | not produced |
| Error-shape check | Static | RFC 9457 | present |

## Executive Summary

The contract and implementation align on all 19 documented operations, with RFC 9457 problem bodies, per-endpoint idempotency, ETag/304 for desired state, and a signed manifest/directive model. Drift exists in pagination (contract documents `cursor`/`nextCursor`; `h_list_sensors` ignores it and only supports a `limit` up to 500), in `SensorSummary.queueDepth` (never populated), and in documented status responses (no 413/429 documented though enforced/possible). The Vector ingest path is deliberately at-least-once with no idempotency key, documented as a consumer concern.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Contract | `api/openapi/falcon-edge-v1.yaml` | API spec | 3.1, 19 paths | Low | drift below |
| Routes | `service.ROUTES` | Dispatch | 19 routes | Low | regex + auth class |
| List sensors | `h_list_sensors` | Pagination | No cursor | Med | API-P2-001 |
| Sensor summary | `_summary` | Detail | no `queueDepth` | Med | API-P2-002 |
| Ingest | `h_ingest_vector` | Vector batch | At-least-once | Low | API-P3-002 (P3) |
| Problems | `problem()` | Errors | RFC 9457 | Low | static instance |
| Client | `falcon_agent/client.py` | Retry semantics | transient/definitive | Low | good |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| REST/RPC routes | 4 | `ROUTES` | — | — |
| Server actions | 4 | handlers | — | — |
| WebSocket/realtime | N/A | none | polling | document |
| Subscriptions/events | 4 | `h_events` | — | — |
| Webhooks | 3 | `ingest/vector` | no dedupe | API-P3-002 |
| External clients | 4 | agent client | — | — |
| Retries/timeouts/circuit breakers | 4 | full jitter + timeouts | no circuit breaker | minor |
| Pagination/filter/sort | 2 | limit only | no cursor | API-P2-001 |
| Error response format | 4 | RFC 9457 | static instance | API-P3-001 |
| OpenAPI/versioning | 4 | v1 + schemaVersion | drift | API-P2-001/002 |
| Request/response validation | 5 | `validate_payload` | — | — |
| Auth/rate limit | 3 | mTLS authz | no rate limit | SEC-P2-001 |
| Background delivery | 4 | queue flush | — | — |
| Dead-letter handling | 4 | `dlq` | — | — |
| Duplicate event behavior | 3 | idempotency (except ingest) | — | API-P3-002 |

## Detailed Review

### Item: Pagination

- Evidence: contract `/sensors` `cursor` param + `SensorPage.nextCursor`; `h_list_sensors` reads only `state`/`limit`.
- Gap: a client cannot page past the 500-row cap.
- Risk: API-P2-001.

### Item: Problem responses

- Evidence: `problem()` sets `"instance": "/api/v1"` for every error.
- Gap: RFC 9457 `instance` should identify the occurrence/path.
- Risk: API-P3-001.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| API-001 | Routes | contract/`ROUTES` | 19/19 | — | — | — |
| API-002 | Server actions | handlers | — | — | — | — |
| API-003 | Realtime | none | N/A | — | — | — |
| API-004 | Events | `h_events` | idempotent | — | — | — |
| API-005 | Webhooks | `ingest/vector` | cert attribution | no dedupe | P3 | API-P3-002 |
| API-006 | External clients | agent client | jitter/timeout | no breaker | P3 | minor |
| API-007 | Pagination | contract | limit only | cursor | P2 | API-P2-001 |
| API-008 | Errors | `problem()` | RFC 9457 | static instance | P3 | API-P3-001 |
| API-009 | Versioning | v1/schemaVersion | good | drift | P2 | API-P2-002 |
| API-010 | Validation | `validate_payload` | strong | — | — | — |

## Findings

### Finding ID: API-P2-001 - Contract documents cursor pagination that the implementation ignores

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `api/openapi/falcon-edge-v1.yaml` — `/sensors` `cursor` parameter; `SensorPage.nextCursor`
  - `src/falcon_control/service.py` — `h_list_sensors` reads `state`/`limit` only, returns `{"items": items}`
- What is happening: there is no cursor support; >500 sensors cannot be enumerated and `nextCursor` is never returned.
- Why it matters: contract-vs-implementation drift; clients written to the spec silently get truncated lists.
- User / business impact: operator tooling under-reports fleets >500.
- Security / privacy / reliability impact: low (completeness).
- Recommended fix: implement keyset pagination (`sensor_id > cursor`) and return `nextCursor`, or remove cursor fields from the contract and document the cap.
- Suggested validation: contract test that `nextCursor` is honored/absent per decision.
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: `store.list_sensors`
- Status: open

### Finding ID: API-P2-002 - `SensorSummary.queueDepth` is documented but never returned

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `api/openapi/falcon-edge-v1.yaml` — `SensorSummary.properties.queueDepth`
  - `src/falcon_control/service.py` — `_summary()` returns no `queueDepth`
- What is happening: same as FEAT-P2-001 (single root cause, referenced here for contract conformance).
- Why it matters: schema-validating clients may require or display the field.
- User / business impact: broken client expectations.
- Security / privacy / reliability impact: low.
- Recommended fix: populate from latest heartbeat sample or drop from the contract.
- Suggested validation: schema-based response test.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: API-P3-002 - Vector ingest is at-least-once with no idempotency key or dedupe

- Severity: P3
- Confidence: High
- Area: API
- Evidence:
  - `src/falcon_control/service.py` — `h_ingest_vector` docstring: "no Idempotency-Key ... dedupe is the consumer's concern"
  - `src/falcon_control/service.py` — `_append_ingest` writes a single daily NDJSON file capped at 128 MiB, rotating to `.1` (overwriting)
- What is happening: retried batches are appended again; rotation keeps only one `.1` predecessor.
- Why it matters: duplicate events and bounded retention (only two files) with no downstream consumer in-repo.
- User / business impact: duplicate/failed ingest unnoticed.
- Security / privacy / reliability impact: data-quality/reliability.
- Recommended fix: accept an optional idempotency/batch id and dedupe, or document the consumer contract and retention explicitly; use timestamped rotated files rather than overwriting `.1`.
- Suggested validation: integration test that a replayed batch is deduped or counted.
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: consumer design
- Status: open

### Finding ID: API-P3-001 - Problem `instance` is a static string rather than the request path

- Severity: P3
- Confidence: High
- Area: API
- Evidence:
  - `src/falcon_control/service.py` — `problem()` sets `"instance": "/api/v1"`
  - `api/openapi/falcon-edge-v1.yaml` — `Problem.instance` format uri
- What is happening: every error reports the same instance URI.
- Why it matters: RFC 9457 instance is meant to identify the specific occurrence for support/triage.
- User / business impact: harder error correlation.
- Security / privacy / reliability impact: low.
- Recommended fix: set `instance` from `req.path` (plus correlation id).
- Suggested validation: error-response test asserting the path appears.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Pagination drift | P2 | Medium | Tooling undercounts | contract vs handler | API-P2-001 |
| Missing field | P2 | High | Client breakage | `_summary` | API-P2-002 |
| Ingest duplicates | P3 | Medium | Data quality | ingest docstring | API-P3-002 |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Resolve `queueDepth`; fix `instance`.

### This Month
Implement or remove cursor pagination; define ingest consumer contract.

### Later / Platform Evolution
Webhook/realtime channel for operators.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix `instance` | triage | `service.py` | error test |
| Document ingest retention | clarity | contract/docs | reviewed |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Cursor pagination | P2 | build-agent | M | store |
| Ingest dedupe | P3 | build-agent | M | consumer |

## Suggested Tests

- Contract conformance: enumerate every documented response field.
- Pagination: >500 sensor fixture.
- Ingest: replay batch.

## Suggested Documentation Updates

- `api/openapi/falcon-edge-v1.yaml` descriptions for pagination status and ingest delivery semantics.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is cursor pagination required at scale? | fix choice | owner/fleet plan |
| Who consumes the ingest NDJSON? | dedupe design | integration doc |

## Appendix

All 19 contract paths were matched to a handler in `ROUTES`; `ingest/vector` carries no sensor path segment and is authorized by certificate only (`_authorize` "sensor" branch). No WebSocket/realtime endpoints exist.
