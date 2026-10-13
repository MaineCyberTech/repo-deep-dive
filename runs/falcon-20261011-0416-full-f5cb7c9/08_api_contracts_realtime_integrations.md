# 08_api_contracts_realtime_integrations — Prompt 08 - API Contracts, Realtime, and Integrations Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `08_api_contracts_realtime_integrations.md` (area API, prompt)

## Verification Performed

# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-f5cb7c9`
- Branch: main (detached worktree at the audited commit; live tree `/home/user/falcon-build` HEAD == f5cb7c9, clean)
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:33:09Z
- Auditor: subagent (read-only; live checks read-only)
- Area code: API
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/08_api_contracts_realtime_integrations.md
- Scope limitations: no REST framework/OpenAPI in this infrastructure repository; the API surface is Traefik routes, the Vector ingest/aggregator contract, the alert relay, and the cross-repo edge pairing contract. The falcon-edge control-plane API implementation is a separate repository (its healthz contract is checked). ntfy server internals and IRIS/Greenbone app APIs are vendored.

## Scope

Reviewed: Traefik routers/middlewares, the Vector edge->aggregator ingest contract and aggregator->OpenSearch delivery, the alert relay HTTP contract, the Cloudflare public routes/tunnel ingress and the external smoke check, the cross-repo pairing contract (EDGE_RELEASE_PIN + verifier), pagination/error/retry behavior, and request validation. Not reviewed: the falcon-edge control-plane implementation, ntfy internals, and vendored app APIs.

## Evidence Reviewed

- `config/traefik/{traefik.yml,dynamic.yml}`, `compose/central/docker-compose.yml` (ports)
- `config/vector/{edge.yaml,aggregator.yaml}` (ingest contract, retries, buffers, DLQ)
- `automation/alerting/ntfy_relay.py`, `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`
- `docs/architecture/PORT_PROTOCOL_MATRIX.md`, `automation/validation/port_matrix_check.sh`
- `docs/edge/{EDGE_RELEASE_PIN.md,EDGE_PIN_OFFLINE_VERIFICATION.md,JOINT_RELEASE_PROCEDURE.md}`, `automation/validation/{verify_edge_pin.py,selfcheck_edge_pin.py,joint_release_check.sh}`
- `.github/workflows/external-smoke.yml`, `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh`
- Live (read-only): `port_matrix_check.sh` (documented=22 undocumented=0), `verify_edge_pin.py` (PASS), `joint_release_check.sh` (both pairs OK), relay metrics, service metrics.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `bash automation/validation/port_matrix_check.sh` on a clean clone | reproduction | Contract vs implementation | documented=22 undocumented=0 |
| `python3 automation/validation/verify_edge_pin.py` | reproduction | Cross-repo contract | PASS (manifest sha256, signature VALID, SBOM, image) |
| `bash automation/validation/joint_release_check.sh` | reproduction | pin<->delivery + pin<->live CP | OK both pairs; live source=17a09a9 dirty=0 |
| `python3 ci/validate.py` clean clone | reproduction | Contract/gates | 0 failures; includes the edge-pin self-check |
| Live relay/service metrics (`falcon_relay.prom`, `falcon_services.prom`) | live read-only | External clients | relay 9/9 success, 0 failures, last success fresh |
| `.github/workflows/external-smoke.yml` read | static | Access-posture contract | still lab-runner + owner-IP bypass accepted (cross-domain, CI-P2-002) |

### Prior-run reconciliation (run falcon-20261009-2117-full-08e20d1; verification run falcon-20261011-0400-verify-main-584e1a3)

- **API-P1-001 (cross-repo pairing contract not verifiable in a clean clone)** — prior post-audit status `verified-fixed` (present since `08e20d1`). Re-verified at f5cb7c9: the offline self-check passes on a clean clone, the mutation test fails closed (flake fixed 2026-10-10), and the live pairing check passes both pairs. **Closed; no current finding.**
- **API-P2-001 (ingest contract relies on a shared secret header)** — prior status `partially-fixed`. Current: unchanged at this commit (HTTP basic auth only; no request signing/idempotency keys; duplicates measured, not prevented). Kept as a current finding with the prior ID.
- The `external-smoke` weakening (owner-IP bypass accepted on lab runners; header still claims a GitHub-network vantage) remains a current issue but is reported by the CI/ADMIN/ACM domains (CI-P2-002 open); recorded here as a cross-domain observation only, not re-raised.

## Executive Summary

The cross-repo contract is genuinely verifiable: the edge-pin verifier passes offline in a clean clone and against the live delivery and live control plane (source=17a09a9, dirty=0), and the port/protocol matrix matches the live listeners (22 documented, 0 undocumented). The relay answers honestly (2xx only after a path accepted; 502 + bounded spool otherwise) and its live counters are clean (9/9 per path, 0 failures).

The ingest contract remains authenticated only by a shared basic-auth secret with no per-request signature and no idempotency key (API-P2-001, unchanged), and the public-access deploy script's operator guidance still names the retired `dash.falcon`/`ntfy.falcon` hostnames while the actual tunnel ingress set is `falcon`/`iris`/`enroll` (API-P3-002, new). The external smoke gate no longer asserts the Cloudflare Access posture it claims (cross-domain, CI-P2-002).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Traefik routers | `config/traefik/dynamic.yml:51-134` | Public/private entry | routers incl. falcon/iris/enroll/soc + lab hosts | Medium | Access posture external |
| Ingest (edge->aggregator) | `config/vector/edge.yaml:236-256` | Telemetry contract | basic auth, 10 retries/300 s, 2 GiB disk buffer | Medium | no signing/idempotency |
| Ingest (aggregator->OpenSearch) | `config/vector/aggregator.yaml:117-138` | Storage delivery | basic auth, no sink DLQ | High | see WH-P1-001 |
| Alert relay | `automation/alerting/ntfy_relay.py` | Grafana webhook -> ntfy | token path, rate limit, honest 502, spool | Low | replay residual (WH-P3-001) |
| Edge pairing contract | `docs/edge/EDGE_RELEASE_PIN.md` + verifier | Cross-repo | PASS offline+live | Low | API-P1-001 closed |
| Public ingress | `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh` | Tunnel/DNS/Access as code | falcon/iris/enroll (live v13) | Medium | 97 log text stale (API-P3-002) |
| External smoke | `.github/workflows/external-smoke.yml` | Public surface gate | accepts bypass on lab runners | Medium | CI-P2-002 (cross-domain) |
| Realtime/WebSocket | none | - | n/a | - | ntfy client SSE/WS only |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| REST/RPC routes | 3 | Traefik + port matrix 22/0 | public routes rely on Cloudflare Access | keep Access checks real |
| Server actions | 0 | n/a (infra) | - | - |
| WebSocket/realtime | 2 | ntfy client streaming only | no repo-managed realtime contract | - |
| Subscriptions/events | 3 | ntfy topics, per-path metrics | - | - |
| Webhooks | 3 | relay contract (see WH) | replay residual | see WH-P3-001 |
| External clients | 3 | probes all up | Access posture check weakened | CI-P2-002 |
| Retries/timeouts/circuit breakers | 3 | vector 10/300 s; relay 2 attempts | sink non-retriable drops | see WH-P1-001 |
| Pagination/filter/sort | 2 | OpenSearch queries bounded (size<=2000) | no API-level pagination | n/a infra |
| Error response format | 3 | relay 400/404/429/502; vector DLQ | - | - |
| OpenAPI/versioning | 1 | no OpenAPI; pin docs instead | no machine-readable contract | optional |
| Request/response validation | 3 | vector validators + DLQ; relay JSON parse | sink failures not DLQ'd | WH-P1-001 |
| Auth/rate limit | 3 | token/secret/basic auth; rate limits | shared secret only | API-P2-001 |

## Detailed Review

### Item: Ingest contract (edge -> aggregator -> OpenSearch)

- Evidence: `config/vector/edge.yaml:236-256`, `config/vector/aggregator.yaml:18-28,117-138`, `docs/architecture/PORT_PROTOCOL_MATRIX.md:27`.
- Current controls: HTTP basic auth (`falcon-vector-edge`), newline-delimited JSON framing, field validation to DLQ, retries 10 with backoff to 300 s, 2 GiB disk buffer `block`.
- Missing controls: no request signing/HMAC, no idempotency key; duplicates are measured (`falcon_pipeline_duplicate_ratio` live 0.0000 over a 2000-event sample) but not prevented; sink write failures are dropped and not dead-lettered (WH-P1-001).
- Risks: a compromised network position with the shared secret can inject/replay; retries are at-least-once with no dedup.

### Item: Public routes / tunnel ingress

- Evidence: `bootstrap/96-public-access.sh:46-72`, `bootstrap/97-cloudflare-api-config.sh:35,59-61,71,90`, live v13 ingress (per the verification run).
- What changed at this commit (584e1a3): the ingress/DNS/Access set is `falcon`/`iris`/`enroll`; the prior `dash.falcon`/`ntfy.falcon` hostnames are retired (lab ntfy is internal-only).
- Missing controls: the operator-guidance log lines in 97 still name the retired hostnames; no automated remote-vs-repo drift check (INFRA-P2-004 residual).

### Item: Cross-repo pairing contract

- Evidence: `automation/validation/verify_edge_pin.py`, `selfcheck_edge_pin.py`, `joint_release_check.sh`; live runs.
- Current controls: manifest sha256 + signature + SBOM + image verified offline and live; mutation self-check fails closed; joint gate compares pin/delivery/live source commit.
- Risks: low; remaining "NOT CHECKED" items are edge-owned (sensor image digests, edge gate ledger) and declared.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| API-001 | REST/RPC routes | `dynamic.yml` | Traefik + Cloudflare | posture check weakened | P2 | CI-P2-002 (cross-domain) |
| API-002 | Server actions | n/a | - | - | - | - |
| API-003 | WebSocket/realtime | ntfy | native auth | - | - | - |
| API-004 | Subscriptions/events | ntfy topics | per-path metrics | - | - | - |
| API-005 | Webhooks | relay | token + rate limit | replay residual | P3 | WH-P3-001 |
| API-006 | External clients | probes | all up | Access assertion weakened | P2 | CI-P2-002 (cross-domain) |
| API-007 | Retries/timeouts | vector/relay | bounded retries | sink drops | P1 | WH-P1-001 |
| API-008 | Pagination/filter/sort | scripts | bounded sizes | - | - | - |
| API-009 | Error response format | relay | 400/404/429/502 | - | - | - |
| API-010 | OpenAPI/versioning | none | pins/docs | no machine contract | P3 | optional |
| API-011 | Request validation | vector | DLQ | sink not DLQ'd | P1 | WH-P1-001 |
| API-012 | Auth/rate limit | relay/vector | token/basic/limits | shared secret only | P2 | API-P2-001 |
| API-013 | Public ingress docs | `97:59-61` | ingress set correct | stale log hostnames | P3 | API-P3-002 |

## Findings

### API-P2-001 - Ingest contract relies on a shared secret header, not request signing or idempotency keys

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `config/vector/aggregator.yaml:18-28` (`edge_ingest` http_server, basic auth `falcon-vector-edge`/`${VECTOR_INGEST_PW}`).
  - `config/vector/edge.yaml:238-247` (same shared secret on the sink side; `uri: "http://vector-aggregator:6000/"`).
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` (N-08: "shared secret header"; note: the mechanism is actually HTTP basic auth — see ARCH-P3-001).
  - `automation/validation/pipeline_duplicate_check.py` (DQ-P2-002: duplicates measured, not prevented); live `falcon_pipeline_duplicate_ratio 0.0000` over a 2000-event sample.
  - No changes to `config/vector/*` between `08e20d1` and `f5cb7c9`.
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

### API-P3-002 - Public-access deploy script still names the retired dash.falcon/ntfy.falcon hostnames in its operator guidance

- Severity: P3
- Confidence: High
- Area: API
- Evidence:
  - `bootstrap/97-cloudflare-api-config.sh:35` `HOSTS=("falcon.mainecybertech.us" "iris.mainecybertech.us" "enroll.mainecybertech.us")`; `:71`/`:90` ingress hosts the same set.
  - `bootstrap/97-cloudflare-api-config.sh:59-61`: the fallback operator-guidance log still lists `dash.falcon.mainecybertech.us` and `ntfy.falcon.mainecybertech.us` (both retired; lab ntfy is internal-only per NOTIF-P1-001).
  - `bootstrap/96-public-access.sh:46-72` ingress updated to falcon/iris/enroll; the local config is explicitly non-authoritative (remote v13 is effective).
- What is happening: an operator following the printed fallback instructions would configure public hostnames that no longer exist in the intended set.
- Why it matters: wrong manual configuration during an incident; confusing audit evidence.
- User / business impact: operator error risk; docs/UX debt.
- Security / privacy / reliability impact: low — could re-expose a retired hostname if followed blindly.
- Recommended fix: update the three log lines to falcon/iris/enroll and note the remote-managed source of truth.
- Suggested validation: a grep test asserting the retired hostnames appear only in historical records.
- Owner suggestion: platform/ops
- Effort estimate: S
- Dependencies: none
- Status: open (new)
- Endpoint / data path: n/a (deploy script guidance)
- Attack path: none identified

### Cross-domain observation (not re-raised as an API finding): external-smoke Access posture

- Evidence: `.github/workflows/external-smoke.yml:3-6` (header claims a GitHub-network vantage asserting `302 -> cloudflareaccess.com`); `:23-26` runs on `[self-hosted, lab]`; `:33-46` `check_gated` accepts any 302 including "owner-IP Access bypass; origin reachable".
- Assessment: the daily gate no longer proves the Cloudflare Access posture it claims; no other in-repo mechanism asserts it.
- Disposition: same issue as CI-P2-002 (open) and the ADMIN/ACM domains; intentionally not duplicated here. Fix: restore the `cloudflareaccess.com` location assertion (keep the bypass as a separate labelled check) or add a non-owner-IP vantage, and update the stale header.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Ingest replay/injection with shared secret | P2 | Medium | Data integrity | API-P2-001 | signing + idempotency |
| Access posture regression undetected | P2 | Medium | Public console exposure | CI-P2-002 | restore assertion |
| Sink delivery drops | P1 | High | Telemetry loss | WH-P1-001 | DLQ |
| Operator misconfigures retired hostname | P3 | Low | Confusion / re-exposure | API-P3-002 | fix log text |

## Recommendations

### Immediate / Release Blocking
1. Restore the Access-posture assertion (CI-P2-002) or add a real external vantage.

### This Week
2. Add request signing + idempotency to the ingest contract (API-P2-001) and a sink-failure DLQ (WH-P1-001).
3. Fix the stale hostnames in `bootstrap/97` (API-P3-002).

### This Month
4. Optional: machine-readable contract (OpenAPI-style) for the ingest/relay endpoints.

### Later / Platform Evolution
5. mTLS for the edge ingest path once the edge release supports it.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the stale 97 log hostnames | Honest operator guidance | `bootstrap/97-cloudflare-api-config.sh` | grep for retired names |
| Fix the stale external-smoke header + separate bypass check | Honest gate | `.github/workflows/external-smoke.yml` | simulate bypass -> FAIL |
| Record the Access-posture external verification | Evidence | `docs/security/` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Ingest signing + idempotency | P2 | platform | M | edge release |
| Sink DLQ | P1 | ops | M | vector config |
| Contract doc for ingest | P3 | platform | S | - |
| Remote-vs-repo tunnel drift check | P2 | ops | S | INFRA-P2-004 residual |

## Suggested Tests

- Replay test: identical ingest request twice -> one document.
- External smoke mutation test: bypass response must fail the gate.
- Contract test: port matrix check stays 0 undocumented.
- Doc test: retired public hostnames absent from bootstrap scripts.

## Suggested Documentation Updates

- `.github/workflows/external-smoke.yml` header (remove the stale vantage claim).
- `bootstrap/97-cloudflare-api-config.sh` operator log lines (falcon/iris/enroll).
- `docs/architecture/PORT_PROTOCOL_MATRIX.md` N-08: record that the mechanism is HTTP basic auth (ARCH-P3-001) and the accepted signing residual.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there an owner-side Access posture check? | Determines residual risk | ops notes |
| Edge release timeline for signing/mTLS? | Unblocks API-P2-001 | edge repo roadmap |

## Appendix

- Live joint check output: pin<->delivery OK; pin<->live CP OK (source=17a09a9 dirty=0).
- Port matrix: documented=22 undocumented=0.
- Live relay: 9/9 success per path in ~2 h, 0 failures.

## Findings

| ID | Severity | Title |
|---|---|---|
| API-P2-001 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys |
| API-P3-002 | P3 | Public-access deploy script still names the retired dash.falcon/ntfy.falcon hostnames in its operator guidance |
