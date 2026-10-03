# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab profile, prompt 08 ADAPTED)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: `/home/user/falcon-build` (central) + `/home/user/falcon-edge-build` (edge); branch `main`
- Commit SHA: central `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c`; edge `45dfed050fba9c25d7f8f8b5c64526887379ce84` (dirty: 4 modified + 2 untracked CI files)
- Generated at: 2026-09-30T07:25Z · Auditor: audit subagent (read-only; no live POSTs/test sends) · Area code: API
- Output path: docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/08_api_contracts_realtime_integrations.md
- Scope limitations: upstream ntfy/Wazuh/Grafana API schemas not reviewed; live Grafana only via repo artifacts; secrets directories unreadable to the audit account.

## Scope

Reviewed: edge control-plane OpenAPI contract vs `service.py`/`http_server.py`; mTLS, enrollment, renewal, RBAC, idempotency, pagination, error format; agent/CLI/Vector/Wazuh-forwarder clients (timeouts, retries, DLQ); integration surface on the central side: ntfy relay, Prometheus/exporters, Wazuh API/forwarder, VPN enrollment, edge alert deployment. Not reviewed: live VPN/WG internals; Grafana live admin API; upstream contracts.

## Evidence Reviewed

- `falcon-edge-build/api/openapi/falcon-edge-v1.yaml`; `src/falcon_control/{service,http_server,pki,store,tokens}.py`
- `falcon-edge-build/src/falcon_agent/{client,runner,queue}.py`; `src/falcon_common/{x509tools,models_generated}.py`
- `falcon-edge-build/tests/{phase2,phase6,phase7}`; `ci/lint_openapi.py`; `ci/validate.sh`; `profiles/sensor/vector/edge.toml`
- `falcon-edge-build/automation/validation/deploy_edge_alert_rules.sh`; `config/prometheus/edge-alerts.yaml`; `automation/observability/fleet_metrics.py`
- `falcon-build/automation/alerting/ntfy_relay.py`; `bootstrap/90-alerting.sh`; `config/prometheus/prometheus.yml`; `config/ntfy/server.yml`
- `falcon-build/automation/wazuh/falcon-alert-forwarder/forward.py`; `automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf`; `mct/scripts/endpoint-count-report.sh`
- `falcon-build/automation/vpn/enroll-service.py`; `docs/phase9/ALERT_CATALOGUE.yaml`; `automation/validation/secret_scan.py`
- `/home/user/falcon-review-delivery-2026-09-30.tar.gz` (archive listing only); run dir `live_snapshot.txt`; read-only journal excerpts

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Local repro `/tmp/opencode/audit08_repro.py` | reproduction | contract vs implementation | 19 implemented ops vs 16 documented; `cursor` ignored (`{items}` only); `limit=-1` accepted; CN=operator CSR → operator role; invalid CSR burns token, raises `X509Error`, 0 sensor rows |
| `git rev-parse` both repos | binding | report bound to commits | SHAs above; edge dirty at write time |
| `live_snapshot.txt` | live read-only | ports/units | 9443 `0.0.0.0`; relay on 172.17.0.1/172.30.x.1:9099; ntfy 127.0.0.1:2586; Wazuh API 127.0.0.1:55000 |
| review package + delivery tar + `secret_scan.py` | artifact/reproduction | secret exposure + scanner gap | secret present in both; whole-tree scan returns `NO_FINDINGS` |
| `ci/lint_openapi.py` + `ci/validate.sh` | source | contract checks | syntax/generated-model checks only; no route parity |

## Executive Summary

The edge control plane is contract-first and well tested (RFC 9457 problems, per-route RBAC, heartbeat replay protection, atomic token redemption, linted OpenAPI with generated models in CI). The gaps are parity and boundary gaps: three live endpoints are undocumented, the documented pagination cursor was never implemented, `Idempotency-Key` is unenforced on two routes that promise it, and a malformed CSR burns a single-use token while raising an unhandled exception. A reproduced authz gap remains: enrollment signs an unconstrained CSR subject, so a token holder can mint an operator certificate (still-open REV-P1-004). The release-blocking item is on the central side: the newly committed Wazuh config contains integration credential material the secret scan cannot see, already inside the published delivery archive. Next: rotate/redact and fix the scanner (same day); add route-parity/pagination tests; enforce idempotency; deploy the prepared edge alert rules when the owner unblocks D-007.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Edge CP API v1 | `api/openapi/falcon-edge-v1.yaml`; `service.py:ROUTES` | sensor+operator control | 16 documented / 19 implemented | Medium | renewals, release, ingest/vector undocumented |
| Enrollment | `service.py:h_enroll`; `tokens.py` | token + CSR → cert | single-use, atomic redeem | High | unconstrained CSR subject; redeem-before-sign |
| Sensor mTLS APIs | `service.py:434-660` | heartbeat/inventory/state/events | idempotent, replay-guarded | Low | clock skew 300 s; schema-validated |
| Operator APIs | `service.py:693-771` | tokens/quarantine/release/revoke | RBAC | Medium | quarantine/revoke ignore Idempotency-Key |
| Vector ingest | `service.py:h_ingest_vector`; `profiles/sensor/vector/edge.toml` | NDJSON metadata batches | at-least-once, 1000 cap, 128 MiB | Medium | hardcoded sensor id; shallow item checks; `.1` rotation overwrites |
| Agent client + offline queue | `client.py`; `queue.py` | error classification, DLQ | 10 s timeout; checksum/eviction/DLQ | Medium | no circuit breaker; `purge_expired()` deletes non-expired rows |
| ntfy publish | `ntfy_relay.py`; `config/ntfy/server.yml` | alert fan-out | basic auth, deny-all server | Medium | relay webhook auth covered in prompt 30 |
| Prometheus | `config/prometheus/prometheus.yml` | scrape config | 3 jobs; no `rule_files` | Low | edge rules not loaded (INTG-P1-001) |
| Wazuh API | `automation/wazuh/migration/docker-compose.lab.yml:18`; `mct/scripts/*` | loopback admin API | 127.0.0.1:55000; 10 s timeouts | Low | upstream contract; no retry |
| Wazuh forwarder | `automation/wazuh/falcon-alert-forwarder/forward.py` | alerts.json → syslog TLS | reconnect loop | Medium | at-most-once, no spool, CERT_NONE client |
| VPN enrollment API | `automation/vpn/enroll-service.py` | WG peer self-enroll | shared static token | Medium | no contract/versioning/rate limit |

Realtime inventory: **no first-party WebSocket/SSE/subscriptions**; realtime is agent polling (60 s), ntfy mobile long-poll, Prometheus pull, timers (documented in `docs/architecture/PORT_PROTOCOL_MATRIX.md`).

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| REST/RPC routes | 3 | `service.py:ROUTES`; phase2/6/7 tests | 3 undocumented ops; no rate limit | parity test + docs |
| Server actions | n/a | no framework server-action layer | none | none |
| WebSocket/realtime | 3 | polling only, documented | no push channel (by design) | none |
| Subscriptions/events | 3 | event batches idempotent; agent queue | no consumer subscription API | defer |
| Webhooks | 2 | relay webhook (prompt 30) | static path token, no HMAC/replay | see NOTIF-P2-001 |
| External clients | 3 | agent/CLI/Vector/Wazuh | forwarder at-most-once; no rate limits | document loss model |
| Retries/timeouts | 3 | `runner.full_jitter`; Vector 30 s; client 10 s | relay 2 immediate attempts; no breaker | backoff + spool |
| Pagination/filter/sort | 1 | contract 96-103, 751-757; `h_list_sensors` | cursor ignored; no nextCursor; negative limit unlimited | implement or remove |
| Error response format | 4 | `problem()` RFC 9457 | X509Error unhandled | map exceptions to problems |
| OpenAPI/versioning | 3 | `lint_openapi.py`; generated models | 3 missing paths; no deprecation policy | add paths + policy |
| Request/response validation | 4 | `validate_payload` on documented routes | ingest items shallow | define ingest schema |
| Auth/rate limit | 2 | mTLS + RBAC + single-use tokens | CSR→operator escalation; no rate limit | constrain CSR; add limits |

## Detailed Review

### Item: Contract vs implementation
- Evidence: contract 28-354; `service.py:137-158`; local repro.
- Controls: operationId lint, generated models/schemas in `ci/validate.sh`, 400 on schema failure. Gaps: no test asserts ROUTES ⊆ contract; `cursor`/`nextCursor`/`queueDepth` drift; `limit=-1` bypasses the 500 cap. Fix: parity test; implement keyset pagination or remove cursor fields; document the 3 operations.

### Item: Idempotency and enrollment failure handling
- Evidence: `_idempotent` 254-273; `h_quarantine` 693-703; `h_revoke` 760-771; `h_enroll` redeem 329 → `pki.issue_cert` 333; repro.
- Controls: request-SHA replay with `Idempotency-Replayed`, 409 on body mismatch, heartbeat sequence/replay checks. Gaps: quarantine/revoke skip the contract-required key (CLI sends one anyway); idempotency rows never expire; invalid CSR raises `X509Error` after redemption. Fix: wrap quarantine/revoke; validate CSR before redeem; `problem(400,"CSR_INVALID",retryable=false)`; 7-day retention.

### Item: External clients and central integrations
- Evidence: `client.py:32-76` (10 s timeout), `runner.py:552-627` (flush/degrade/full jitter), `queue.py` (DLQ/checksum; `purge_expired` bug), `profiles/sensor/vector/edge.toml` (2 GiB disk buffer, `when_full=block`, healthcheck off), `forward.py` (reconnect loop, no spool); `ntfy_relay.py`, `90-alerting.sh`, `prometheus.yml` (no `rule_files`), `enroll-service.py:9-16,87-111,171-174` (decision log 2026-09-28 02:35Z exposes it), `edge-alerts.yaml` + `deploy_edge_alert_rules.sh`, `fleet_metrics.py`.
- Gaps: Wazuh forwarder loses alerts while disconnected; agent retry is cycle-bounded; ingest items not schema-validated; `purge_expired()` latent data-loss bug; edge rules undeployed (D-007; no `falcon-edge` rules in the live catalogue); VPN enrollment API internet-reachable with static token, no rate limit; Wazuh API loopback-only (good). Fix: spool or document; fix `purge_expired`; define ingest schema; deploy edge rules when unblocked; version/limit enrollment.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| API-001 | REST/RPC contract parity | OpenAPI; ROUTES | CI contract lint | 3 undocumented ops | P2 | parity test + docs |
| API-002 | Server actions | n/a | n/a | n/a | n/a | none |
| API-003 | WebSocket/realtime | none in repo | polling documented | none | P3 | none |
| API-004 | Subscriptions/events | events idempotent | replay + idempotency | no consumer API | P3 | defer |
| API-005 | Webhooks | relay path token | token check | no HMAC/replay | P2 | see NOTIF-P2-001 |
| API-006 | External clients | agent/CLI/Vector/Wazuh | timeouts, buffers, idempotency | forwarder at-most-once | P2 | spool or document |
| API-007 | Retries/timeouts | `full_jitter`; Vector 30 s | bounded retry | relay immediate x2 | P2 | backoff/queue |
| API-008 | Pagination/filter/sort | contract 96-103; handler | none | cursor ignored; neg. limit | P2 | implement/remove |
| API-009 | Error format | `problem()` | RFC 9457 | unhandled X509Error | P2 | map exceptions |
| API-010 | OpenAPI/versioning | lint + generated | URL/schema versions | 3 paths missing | P2 | add paths |
| API-011 | Request/response validation | `validate_payload` | schema enforcement | ingest shallow | P2 | define ingest schema |
| API-012 | Auth/rate limit | mTLS+RBAC; `pki.py` | cert roles | CSR→operator; no limits | P1 | constrain CSR; rate limit |

## Findings

### Finding ID: API-P0-001 - Integration credentials committed into the published Wazuh config and invisible to the secret scan
- Severity: P0 · Confidence: High · Area: API (integration secrets)
- Evidence: `automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf` — VirusTotal `<api_key>` (64-hex literal) in the active block; a 32-char cluster `<key>` literal; a 36-char Shuffle `<api_key>` + hook URL in a disabled comment; `automation/validation/secret_scan.py:19,30` — `api_key_assignment` misses XML tags and `ALLOW_VALUE = ^[0-9a-f]{64}$` allowlists every 64-hex value; scanner run returns `NO_FINDINGS`; the file is inside `/home/user/falcon-review-delivery-2026-09-30.tar.gz` (matching declared SHA-256); no entry in `ledgers/redactions.md`.
- What is happening: commit `6bf001a` (06:52Z) published live-looking credentials, and the delivery archive was built at 06:59Z with them.
- Why it matters: credentials are disclosed to everyone with the repo or the delivery package, and the scanner cannot catch a repeat.
- User/business impact: VirusTotal account abuse; Wazuh cluster-auth exposure; doctrine breach in a "no secrets" package · Security/privacy/reliability impact: confirmed credential-shaped secret in a delivered artifact; systemic scanner blind spot (any 64-hex secret).
- Recommended fix: rotate the keys; redact in place and record SHA-256 in `ledgers/redactions.md`; rebuild review package + delivery; make `secret_scan.py` context-aware (XML tags; 64-hex allowed only on known digest lines).
- Suggested validation: injected 64-hex `<api_key>` fixture is caught; repo clean after rotation.
- Owner suggestion: falcon maintainer (security) · Effort: S · Dependencies: key rotation · Status: open

### Finding ID: API-P1-001 - Enrollment signs an unconstrained CSR subject; a token holder can mint an operator certificate
- Severity: P1 · Confidence: High (reproduced) · Area: API auth
- Evidence: `pki.py:30-59` signs the submitted CSR unmodified; `service.py:196-203` grants operator role solely from `peer_cn == "operator"`; `h_enroll` 291-376 accepts any CSR from a valid token; repro: a `/CN=operator` CSR issued via `pki.issue_cert` resolves to `operator` when its fingerprint is not in `sensors`.
- What is happening: the contract (`falcon-edge-v1.yaml:359`) says role is carried by the certificate subject, but nothing constrains that subject at issuance.
- Why it matters: any bootstrap token escalates into full operator API control.
- User/business impact: full fleet control (quarantine/revoke/update) by a token holder · Security/privacy/reliability impact: authorization bypass.
- Recommended fix: reject/rewrite CSR subjects at enrollment and renewal (allow only `CN=device-<uuid8>`), or issue certs from a server-built subject.
- Suggested validation: enrollment CSR with CN=operator is rejected (or issued cert resolves as sensor).
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: still-open (prior REV-P1-004)

### Finding ID: API-P2-001 - Three implemented endpoints are absent from the authoritative contract
- Severity: P2 · Confidence: High (reproduced) · Area: API contract
- Evidence: `service.py:141` (`/renewals`), `:150` (`/ingest/vector`), `:156` (`/release`); repro: 19 implemented vs 16 documented, 0 documented-but-missing.
- What is happening: undocumented paths have no published validation/auth/idempotency statement; `ingest/vector` deliberately omits `Idempotency-Key`, an unrecorded contract deviation.
- Why it matters / impact: consumers cannot rely on the contract; the surface cannot be enumerated from it.
- Security / privacy / reliability impact: low directly; auditability gap.
- Recommended fix: document the 3 paths (add ingest/release schemas; reuse `EnrollmentRequest` for renewal).
- Suggested validation: CI parity check fails on divergence.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: still-open (prior ND-P2-012)

### Finding ID: API-P2-002 - Documented pagination is not implemented; a negative limit bypasses the page cap
- Severity: P2 · Confidence: High (reproduced) · Area: API contract
- Evidence: contract `limit`/`cursor` 96-103 and `nextCursor` 751-757; `h_list_sensors` 418-426 ignores `cursor` and returns only `{items}`; `store.list_sensors` 159-168 takes any integer; repro: `limit=-1` → 200 and unlimited page.
- Why it matters / impact: contract consumers cannot page correctly; silent truncation or oversized responses.
- Recommended fix: keyset pagination on `sensor_id`, or remove the cursor fields and clamp `limit ≥ 1`.
- Suggested validation: two-page walk returns all sensors once; `limit=-1` → 400/clamped.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: API-P2-003 - Contract-required Idempotency-Key is not enforced on quarantine and revoke
- Severity: P2 · Confidence: High · Area: API idempotency
- Evidence: contract 322-324, 341-343; handlers 693-703, 760-771 bypass `_idempotent`; the CLI sends keys anyway (`falcon_cli/__main__.py:328-368`).
- Why it matters / impact: retries duplicate audit rows and give no replay response; conservative clients cannot tell replay from re-execution.
- Recommended fix: wrap both handlers in `_idempotent`.
- Suggested validation: same key twice → one audit row + `Idempotency-Replayed: true`.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: open

### Finding ID: API-P2-004 - A malformed CSR burns a single-use bootstrap token and returns no problem response
- Severity: P2 · Confidence: High (reproduced) · Area: API reliability
- Evidence: `h_enroll` redeem at `service.py:329` precedes `pki.issue_cert` at 333; schema accepts any `csrPem` ≥ 64 chars (contract 474); repro: bogus CSR → `X509Error`, `redeemed_at` set, 0 sensor rows.
- Why it matters / impact: a bad body destroys a one-shot provisioning token and yields a transport error instead of RFC 9457.
- Recommended fix: parse/validate CSR before redemption; catch `X509Error` → `problem(400,"CSR_INVALID",retryable=false)`.
- Suggested validation: negative test asserts 400 problem and token remains redeemable.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: open

### Finding ID: API-P2-005 - Client-VPN enrollment API is internet-reachable, unversioned, and unthrottled
- Severity: P2 · Confidence: Medium-High · Area: API / external integration
- Evidence: `automation/vpn/enroll-service.py:9-16,87-111,171-174` (shared static token in JSON body; allocates `10.99.0.20-99`; can return a generated private key); decision log 2026-09-28 02:35Z exposes it at `enroll.mainecybertech.us` without Cloudflare Access; no schema/version/rate limit.
- Why it matters / impact: a leaked static token admits a tunnel peer; no lockout or burst detection.
- Recommended fix: version and document the small contract; add rate limiting, token expiry, and rotation metadata.
- Suggested validation: brute-force simulation returns 429; rotation invalidates the old token.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: API-P3-001 - Response schema drift: `SensorSummary.queueDepth` is never returned
- Severity: P3 · Confidence: High · Area: API contract
- Evidence: contract 747; `_summary` (`service.py:779-789`) omits the field.
- Recommended fix / impact: populate from the latest heartbeat or remove it; low impact.
- Suggested validation: contract test asserts handler output fields.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: open

### Finding ID: API-P3-002 - No automated route-vs-contract parity test
- Severity: P3 · Confidence: High · Area: API tests/CI
- Evidence: `ci/validate.sh` runs `lint_openapi.py` (syntax only) and generated-model checks; no test enumerates `ROUTES` (prior ND-P3-011).
- Recommended fix / impact: add a parity unit test wired into CI; prevents recurrence of API-P2-001.
- Suggested validation: removing a documented path fails CI.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: still-open (prior ND-P3-011)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Credential material in delivered package | P0 | Certain | Credential abuse, doctrine breach | ossec.conf; delivery tar; scanner bypass | rotate, redact, fix scanner, rebuild |
| Token → operator escalation | P1 | Medium | Fleet control by token holder | `pki.py`; `_resolve_identity`; repro | constrain CSR subject |
| Contract drift misleads consumers | P2 | High | Wrong client assumptions | 3 missing paths; pagination | parity test; implement/remove |
| At-most-once Wazuh forwarding | P2 | Medium | Alert gaps during outages | `forward.py` | spool or document |

## Recommendations

### Immediate / Release Blocking
- Rotate/redact the committed credentials; fix `secret_scan.py`; rebuild the review package and delivery archive.

### This Week
- Constrain CSR subjects; add the route-parity test; enforce idempotency on quarantine/revoke; validate CSR before redemption and map `X509Error` to a problem.

### This Month
- Implement/remove pagination; document the 3 endpoints; define the ingest item schema; rate-limit the VPN enrollment API; fix `purge_expired()`.

### Later / Platform Evolution
- Deprecation/versioning policy; idempotency-row retention; circuit-breaker policy for external clients.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add the 3 paths to OpenAPI | removes contract drift | `api/openapi/falcon-edge-v1.yaml` | lint + parity test |
| CSR pre-validation | stops token burn | `service.py`, `pki.py` | negative test |
| Fix `purge_expired()` cutoff | removes latent data loss | `src/falcon_agent/queue.py` | unit test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Scanner context rules (XML + digest context) | P0 | falcon maintainer | S | rotation |
| CSR subject policy | P1 | edge maintainer | S | none |
| Route/pagination contract tests | P2 | edge maintainer | M | none |
| Ingest schema + `.1` rotation fix | P2 | edge maintainer | M | none |
| VPN enrollment contract + limits | P2 | falcon maintainer | M | none |

## Suggested Tests

- Unit: ROUTES vs OpenAPI parity; pagination walk incl. `limit=-1`; idempotent quarantine/revoke; invalid CSR does not redeem; CSR CN=operator rejected.
- Integration: enrollment→heartbeat→state-report→events over real mTLS (extend `tests/phase2`); Vector ingest schema negatives; VPN enroll rate-limit/brute-force.
- CI/manual: scanner fixture with a 64-hex `<api_key>`; route drift fails `ci/validate.sh`; owner-approved rotate VT key and confirm redaction entries.

## Suggested Documentation Updates

- `docs/architecture/PORT_PROTOCOL_MATRIX.md`: add `renewals`, `release`, `ingest/vector`, VPN enroll; edge pin/runbooks: CSR subject policy and enrollment failure modes.
- `build_alert_catalogue.py`: map `falcon-wg-peer-stale` to `docs/runbooks/VPN.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the committed VirusTotal/cluster key live or a placeholder? | rotation urgency | owner/API check (not performed; key not used) |
| Should ingest/vector ever require idempotency (Vector limitation)? | contract vs replicability | owner decision |

## Appendix

Implemented-vs-documented (normalized): 19 implemented, 16 documented; undocumented `POST /ingest/vector`, `POST /sensors/{sensorId}/release`, `POST /sensors/{sensorId}/renewals`; documented-but-missing 0. Repro script: `/tmp/opencode/audit08_repro.py` (local temp only). Prior-run verification: LIVE-P0-004 partially-fixed (6 h TLS window live per regenerated catalogue; commit `d83f421`; no relay fires in the ~3 h since); LIVE-P1-004 partially-fixed (catalogue 31=31 incl. `falcon-wg-peer-stale`; benign-UniFi/Zen filters absent); LIVE-P1-007 partially-fixed (independent DO ntfy live, 147 alt deliveries/7 d; watcher 15-min/26 h documented; heartbeat still inside the stack; see 30); INTG-P1-001 still-open (edge rules prepared, deploy gated by D-007, no `rule_files`, no `falcon-edge` rules in the live catalogue); INTG-P2-004 verified-fixed; ND-P2-012 still-open; ND-P2-014 still-open (`queue.py:126-138` deletes everything; test-only caller); ND-P2-015 partially-fixed (`pending_directive` excludes expired; `consume_directive` still uncalled and `fleet_metrics.py:61-62` counts unconsumed incl. expired); REV-P1-004 still-open (reproduced); INTG-P3-004 still-open (`edge-control-plane.lab.json` binds `0.0.0.0`).
