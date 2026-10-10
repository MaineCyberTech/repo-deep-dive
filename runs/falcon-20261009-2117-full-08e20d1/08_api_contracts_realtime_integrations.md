# 08_api_contracts_realtime_integrations — Prompt 08 - API Contracts, Realtime, and Integrations Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `08_api_contracts_realtime_integrations.md` (area API, prompt)

## Verification Performed

# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-08e20d1`
- Branch: main (worktree detached at the audited commit)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:50:50Z
- Auditor: subagent (read-only; live checks read-only)
- Area code: API
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/08_api_contracts_realtime_integrations.md
- Scope limitations: no REST framework/OpenAPI in this repository (infrastructure repo); the API surface is Traefik routes, the Vector ingest/aggregator contract, the alert relay, and the cross-repo edge pairing contract. Live host runs post-audit main (`6e4fccd`) for deploy state; API files audited at `08e20d1`.

## Scope

Reviewed: Traefik routers/middlewares, the Vector edge->aggregator ingest contract and aggregator->OpenSearch delivery, the alert relay HTTP contract, the Cloudflare public routes and external smoke check, the cross-repo pairing contract (EDGE_RELEASE_PIN + verifier), pagination/error/retry behavior, and request validation. Not reviewed: the falcon-edge control-plane API implementation (separate repository; only its healthz contract was checked), ntfy server internals, and IRIS/Greenbone app APIs (vendored).

## Evidence Reviewed

- `config/traefik/{traefik.yml,dynamic.yml}`, `compose/central/docker-compose.yml` (ports)
- `config/vector/{edge.yaml,aggregator.yaml}` (ingest contract, retries, buffers, DLQ)
- `automation/alerting/ntfy_relay.py`, `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`
- `docs/architecture/PORT_PROTOCOL_MATRIX.md`, `automation/validation/port_matrix_check.sh`
- `docs/edge/{EDGE_RELEASE_PIN.md,EDGE_PIN_OFFLINE_VERIFICATION.md,JOINT_RELEASE_PROCEDURE.md}`, `automation/validation/{verify_edge_pin.py,selfcheck_edge_pin.py,joint_release_check.sh}`
- `.github/workflows/external-smoke.yml`, `bootstrap/97-cloudflare-api-config.sh`
- Live (read-only): `port_matrix_check.sh` (documented=22 undocumented=0), `verify_edge_pin.py` (PASS), `joint_release_check.sh` (both pairs OK), edge healthz, relay/service metrics.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py` clean clone @08e20d1 | reproduction | contract/gates | 0 failures incl. edge-pin self-check |
| `bash automation/validation/tests/edge_pin_offline_test.sh` + `selfcheck_edge_pin.py` | reproduction | API-P1-001 fix | PASS; mutated manifest fails closed |
| `verify_edge_pin.py` on the live delivery | live read-only | Real pairing contract | PASS (manifest sha, signature VALID, SBOM, image) |
| `joint_release_check.sh` | live read-only | pin<->delivery + pin<->live CP | OK both pairs; live source=17a09a9 dirty=0 |
| `curl -sk https://127.0.0.1:9443/api/v1/healthz` | live read-only | Live contract | `{"status":"ok","version":"0.1.0","source_commit":"17a09a9","source_dirty":false}` |
| `port_matrix_check.sh` | live read-only | Contract vs implementation | documented=22 undocumented=0 |
| `falcon_service_up` metrics | live read-only | External clients | grafana/dash/ntfy/relay/do-ntfy-public/do-host/iris/edge-cp all 1 |
| `git show e267ce1:.github/workflows/external-smoke.yml` | reproduction | Regression check | prior version required `302 && cloudflareaccess.com` on `ubuntu-latest` |

### Prior-run reconciliation (run falcon-20261005-full-main-e267ce1)

- **API-P1-001 (cross-repo pairing contract not verifiable in a clean clone)** — prior post-audit status `verified-fixed` (PR #47, `f7522d0`, present in `08e20d1`). Re-verified here: the offline self-check passes on a clean clone, the mutation test fails closed, and the live pairing check passes both pairs. **Closed; no current finding.**
- **API-P2-001 (ingest contract relies on a shared secret header)** — prior status `partially-fixed`. Current: unchanged; HTTP basic auth only, no request signing/idempotency keys. Kept as a current finding with the prior ID.
- New at this commit: the `external-smoke` weakening (owner-IP bypass accepted on lab runners) — introduced by `70292a0`/`08e20d1`, i.e. after the prior run. It is a real current issue but it is already reported by the CI, ADMIN and ACM domain audits of this run; it is recorded here as a cross-domain observation only (not re-raised as an API finding).

## Executive Summary

The cross-repo contract is now genuinely verifiable: the edge-pin verifier passes offline in a clean clone (self-check + mutation fail-closed), against the live delivery, and against the live control plane. The port/protocol matrix matches the live listeners (22 documented, 0 undocumented), and all user-facing service probes are up. The ingest contract remains authenticated only by a shared basic-auth secret with no signing or idempotency keys (accepted, partially fixed), and the daily external smoke check has been weakened: it now runs on lab runners and accepts the owner-IP Access bypass, so it no longer asserts the Cloudflare Access posture its own header claims.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Traefik routers | `config/traefik/dynamic.yml:51-134` | Public/private entry | 12 routers; rate limit + sec headers | Medium | Access posture external |
| Ingest (edge->aggregator) | `config/vector/edge.yaml:234-256` | Telemetry contract | basic auth, 10 retries/300 s, 2 GiB disk buffer | Medium | no signing/idempotency |
| Ingest (aggregator->OpenSearch) | `config/vector/aggregator.yaml:116-138` | Storage delivery | basic auth, no sink DLQ | High | see WH-P1-001 |
| Alert relay | `automation/alerting/ntfy_relay.py` | Grafana webhook -> ntfy | token path, rate limit, honest 502, spool | Low | replay residual (WH-P3-001) |
| Edge pairing contract | `docs/edge/EDGE_RELEASE_PIN.md` + verifier | Cross-repo | PASS offline+live | Low | API-P1-001 closed |
| External smoke | `.github/workflows/external-smoke.yml` | Public surface gate | accepts bypass on lab runners | Medium | API-P2-002 |
| Public routes | `bootstrap/97-cloudflare-api-config.sh` | Access/DNS as code | falcon/iris/soc apps + policies | Medium | no in-repo posture assertion |
| Realtime/WebSocket | none | - | n/a | - | ntfy client SSE/WS only |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| REST/RPC routes | 3 | Traefik + port matrix | public routes rely on Cloudflare Access | keep Access checks real |
| Server actions | 0 | n/a (infra) | - | - |
| WebSocket/realtime | 2 | ntfy client streaming only | no repo-managed realtime contract | - |
| Subscriptions/events | 3 | ntfy topics, per-path metrics | - | - |
| Webhooks | 3 | relay contract (see WH) | replay residual | see WH-P3-001 |
| External clients | 3 | probes all up | Access posture check weakened | API-P2-002 |
| Retries/timeouts/circuit breakers | 3 | vector retries; relay 2 attempts | sink non-retriable drops | see WH-P1-001 |
| Pagination/filter/sort | 2 | OpenSearch queries bounded (`size<=2000`) | no API-level pagination | n/a infra |
| Error response format | 3 | relay 400/404/429/502; vector DLQ | - | - |
| OpenAPI/versioning | 1 | no OpenAPI; pin docs instead | no machine-readable contract | optional |
| Request/response validation | 3 | vector validators + DLQ; relay JSON parse | - | - |
| Auth/rate limit | 3 | token/secret/basic auth; rate limits | shared secret only | API-P2-001 |

## Detailed Review

### Item: Ingest contract (edge -> aggregator -> OpenSearch)

- Evidence: `config/vector/edge.yaml:234-256`, `config/vector/aggregator.yaml:12-35,116-138`, `docs/architecture/PORT_PROTOCOL_MATRIX.md:27`.
- Current controls: HTTP basic auth (`falcon-vector-edge`), newline-delimited JSON framing, field validation to DLQ, retries 10 with backoff to 300 s, 2 GiB disk buffer `block`.
- Missing controls: no request signing/HMAC, no idempotency key; duplicates are measured (`pipeline_duplicate_check.py`, DQ-P2-002) but not prevented; sink write failures are dropped and not dead-lettered (WH-P1-001).
- Risks: a compromised network position with the shared secret can inject/replay; retries are at-least-once with no dedup.

### Item: External smoke / Access posture

- Evidence: `.github/workflows/external-smoke.yml:3-6,23-26,33-46` vs `git show e267ce1:...`.
- What changed: `70292a0` moved the job to `[self-hosted, lab]`; `08e20d1` made `check_gated` accept any 302 as OK ("owner-IP Access bypass; origin reachable"). The header still claims a GitHub-network vantage asserting `302 -> cloudflareaccess.com`.
- Missing controls: no in-repo check that iris/soc are still Access-gated (bootstrap/97 configures but does not assert; grep shows no other verifier).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| API-001 | REST/RPC routes | `dynamic.yml` | Traefik + Cloudflare | posture check weakened | P2 | cross-ref CI/ADMIN/ACM (external-smoke) |
| API-002 | Server actions | n/a | - | - | - | - |
| API-003 | WebSocket/realtime | ntfy | native auth | - | - | - |
| API-004 | Subscriptions/events | ntfy topics | per-path metrics | - | - | - |
| API-005 | Webhooks | relay | token + rate limit | replay residual | P3 | WH-P3-001 |
| API-006 | External clients | probes | all up | Access assertion weakened | P2 | cross-ref CI/ADMIN/ACM (external-smoke) |
| API-007 | Retries/timeouts | vector/relay | bounded retries | sink drops | P1 | WH-P1-001 |
| API-008 | Pagination/filter/sort | scripts | bounded sizes | - | - | - |
| API-009 | Error response format | relay | 400/404/429/502 | - | - | - |
| API-010 | OpenAPI/versioning | none | pins/docs | no machine contract | P3 | optional |
| API-011 | Request validation | vector | DLQ | sink not DLQ'd | P1 | WH-P1-001 |
| API-012 | Auth/rate limit | relay/vector | token/basic/limits | shared secret only | P2 | API-P2-001 |

## Findings

### API-P2-001 - Ingest contract relies on a shared secret header, not request signing or idempotency keys

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `config/vector/aggregator.yaml:18-28` (`edge_ingest` http_server, basic auth `falcon-vector-edge`/`${VECTOR_INGEST_PW}`).
  - `config/vector/edge.yaml:245-248` (same shared secret on the sink side).
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` (N-08: "shared secret header", "lab substitution for VPN").
  - `automation/validation/pipeline_duplicate_check.py:1-8` (DQ-P2-002: no dedup/idempotency; duplicates measured, not prevented).
  - No changes to `config/vector/*` between `e267ce1` and `08e20d1`.
- What is happening: any party that obtains the shared secret can post arbitrary telemetry with no per-request signature and no idempotency key; retries/replays create duplicate documents.
- Why it matters: the ingest path is the platform's trust boundary; compromise/replay is not attributable and duplicates distort analytics.
- User / business impact: data integrity risk; duplicate-driven alert noise.
- Security / privacy / reliability impact: medium — network-scoped (docker bridge/VPN) and secret-rotatable, but no request-level authentication.
- Recommended fix: add an HMAC (or mTLS) request signature with a timestamp/nonce, and an idempotency key mapped to a deterministic document `_id`; keep the basic auth as a second factor.
- Suggested validation: a replayed request is rejected or deduplicated; duplicate ratio stays ~0 under forced retry.
- Owner suggestion: platform owner
- Effort estimate: M
- Dependencies: edge release coordination
- Status: partially-fixed (prior ID API-P2-001)
- Endpoint / data path: POST `http://vector-aggregator:6000/` -> normalize/enrich -> `falcon-eve-%Y.%m.%d`
- Attack path: network-adjacent secret compromise -> arbitrary ingest/replay (single-tenant lab; no cross-tenant path)

### Cross-domain observation (not re-raised as an API finding): external-smoke Access posture

- Evidence: `.github/workflows/external-smoke.yml:3-6` (header: "from GitHub's network ... asserts ... still gated by Cloudflare Access (302 -> cloudflareaccess.com)"); `:23-26` (runs-on `[self-hosted, lab]` while the comment says "it stays on hosted"); `:33-46` (`check_gated` now accepts any 302, including "owner-IP Access bypass; origin reachable"); `git show e267ce1:.github/workflows/external-smoke.yml` (prior version required `302 && location cloudflareaccess.com` on `ubuntu-latest`; changed by `70292a0` + `08e20d1`).
- Assessment: the daily gate no longer proves the Cloudflare Access posture it claims and its header is stale; no other in-repo mechanism asserts the posture (bootstrap/97 configures but does not verify).
- Disposition: this is the same issue reported by the CI, ADMIN and ACM domain audits of this run; it is intentionally **not duplicated here**. Fix: restore the `cloudflareaccess.com` location assertion (keep the bypass as a separate labelled check) or add a non-owner-IP vantage, and update the stale header.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Ingest replay/injection with shared secret | P2 | Medium | Data integrity | API-P2-001 | signing + idempotency |
| Access posture regression undetected | P2 | Medium | Public console exposure | API-P2-002 | restore assertion |
| Sink delivery drops | P1 | High | Telemetry loss | WH-P1-001 | DLQ |

## Recommendations

### Immediate / Release Blocking
1. Restore the Access-posture assertion (API-P2-002) or add a real external vantage.

### This Week
2. Add request signing + idempotency to the ingest contract (API-P2-001) and a sink-failure DLQ (WH-P1-001).

### This Month
3. Optional: machine-readable contract (OpenAPI-style) for the ingest/relay endpoints.

### Later / Platform Evolution
4. mTLS for the edge ingest path once the edge release supports it.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the stale workflow comment + separate bypass check | Honest gate | `.github/workflows/external-smoke.yml` | simulate bypass -> FAIL |
| Record the Access-posture external verification | Evidence | `docs/security/` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Ingest signing + idempotency | P2 | platform | M | edge release |
| Sink DLQ | P1 | ops | M | vector config |
| Contract doc for ingest | P3 | platform | S | - |

## Suggested Tests

- Replay test: identical ingest request twice -> one document.
- External smoke mutation test: bypass response must fail the gate.
- Contract test: port matrix check stays 0 undocumented.

## Suggested Documentation Updates

- `.github/workflows/external-smoke.yml` header (remove the stale vantage claim).
- `docs/architecture/PORT_PROTOCOL_MATRIX.md` N-08 note on the accepted signing residual.
- `docs/edge/EDGE_PIN_OFFLINE_VERIFICATION.md` is accurate; no change.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there an owner-side Access posture check? | Determines residual risk | ops notes |
| Edge release timeline for signing/mTLS? | Unblocks API-P2-001 | edge repo roadmap |

## Appendix

- Live joint check output: pin<->delivery OK; pin<->live CP OK (source=17a09a9 dirty=0).
- Port matrix: documented=22 undocumented=0.

## Findings

| ID | Severity | Title |
|---|---|---|
| API-P2-001 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys |
