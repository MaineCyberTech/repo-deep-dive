# Architecture and Runtime Topology Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: ARCH
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/02_architecture_runtime_topology.md
- Scope limitations: no live host/Pi access; topology reconstructed from repo artifacts and documented environment facts (`AGENTS.md`).

## Scope

Reviewed the runtime topology: control-plane service, agent, CLI, image/update path, PKI/trust, queue, deploy units, and the documented lab-host co-tenancy. Not reviewed live: the running monitoring stack, Prometheus scrape path, or actual device state.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `src/falcon_control/http_server.py` | Source | HTTP(S) transport | stdlib `ThreadingHTTPServer` + TLS 1.2+ |
| `src/falcon_control/service.py` | Source | Request lifecycle, authz | `ROUTES`, `handle`, `_resolve_identity` |
| `src/falcon_agent/runner.py` | Source | Agent cycle, updates | retry→recover→degrade ordering |
| `deploy/*.service` | Units | Runtime isolation | hardened systemd |
| `AGENTS.md` | Doc | Live topology facts | shared KVM host `falcon`; monitoring stack |
| `docs/CURRENT_STATE.md` | Doc | As-built state | tree-exec, 3 ACTIVE sensors |
| `image/overlay/.../falcon-update-verify.py` | Source | Root update path | signed manifest + rollback copy |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Route-table read | Static | Count routes | 19 routes; 4 auth classes |
| Service-unit read | Static | Isolation | `ProtectSystem=strict`, `NoNewPrivileges` |
| Health contract read | Static | Deploy identity | `source_commit`/`source_dirty` reported |
| Mermaid diagrams | Synthesis | Topology clarity | see Appendix |

## Executive Summary

The architecture is a two-tier edge system: a lab control plane (mTLS, SQLite, Ed25519-signed desired state/updates/recovery directives) manages Raspberry Pi sensors running `falcon-agent` (bounded SQLite queue, signed-directive verification, root-side update verify/swap/rollback). Deployment is systemd with solid hardening on the agent and control-plane units. The main architectural weaknesses are that the control plane executes a mutable working tree on the shared lab host (`deploy/edge-control-plane.service`), making it a co-tenant single point of failure, and that the HTTP transport is a bare stdlib server with no connection/rate limits.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Control plane | `src/falcon_control/service.py` | Request handling | Implemented | Med | 19 routes |
| Transport | `http_server.py` | mTLS HTTP/1.1 | Implemented | Med | no rate limits |
| Data | `store.py` | SQLite store | Implemented | Med | no migrations |
| PKI | `pki.py` | CA + cert issuance | Implemented | Low | server-pinned subjects |
| Trust root | `service._operator_fingerprint` | Operator identity | Implemented (pinned) | Low | fail-closed |
| Agent | `runner.py`, `queue.py`, `state.py` | Device runtime | Implemented | Low | bounded queue |
| Update path | `falcon-update-verify.py` | Root verify/swap | Implemented | Low | marker + rollback |
| Deploy | `deploy/*.service` | systemd | Implemented | Low | hardened |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Monorepo structure | 4 | `src/{agent,common,control,cli}` | no packaging | add `pyproject.toml` |
| Frontend/backend/worker boundaries | 4 | no frontend; clear separation | — | — |
| Auth/session flow | 5 | mTLS + pinned operator fp | — | — |
| Authorization and tenant boundaries | 4 | role by cert | single-tenant lab | document multi-site path |
| Request lifecycle | 4 | `handle()` route table | no rate limit | SEC-P2-001 |
| Data flow | 4 | agent→CP→SQLite | — | — |
| Background jobs | 4 | agent cycle, timers | — | — |
| Queues | 4 | `BoundedQueue` | expired-only-evict-on-enqueue | DATA-P3-001 |
| Webhooks | 3 | Vector HTTP ingest | at-least-once | API-P2-002 |
| Realtime | 2 | none (polling) | N/A lab | document |
| Notifications | 2 | Prometheus/Grafana only | no pager | OBS-P2-001 |
| External integrations | 3 | Vector, Prometheus, Kuma? | — | — |

## Detailed Review

### Item: Control-plane runtime

- Evidence: `deploy/edge-control-plane.service` (`ExecStart ... /home/user/falcon-edge-build`, `WorkingDirectory=/home/user/falcon-edge-build`), `service.py source_state()`
- What it does: serves the mTLS API from a git working tree on the shared lab host.
- How it appears to work: systemd starts `python3 -m falcon_control`; `healthz` reports `source_commit`/`source_dirty`.
- Dependencies: `openssl`, `sqlite3`, secrets dir.
- Current controls: hardened unit (`ProtectSystem=strict`, `ProtectHome=read-only`, `ReadWritePaths`).
- Missing controls: pinned release checkout/digest; process supervision beyond bounded restarts.
- Risks: uncommitted edits execute in production-equivalent path; a host fault takes down both edge and monitoring (ARCH-P2-001/002).

### Item: Agent update path

- Evidence: `runner.py apply_update`, `image/overlay/.../falcon-update-verify.py`
- What it does: downloads artifact over the tunnel, verifies SHA-256/size, stages the signed manifest, root helper re-verifies signature, extracts safely, swaps with rollback copy.
- Current controls: TOCTOU-closed copy, archive member validation, root-owned key, marker-based recovery.
- Missing controls: full A/B tryboot out of scope (documented).
- Risks: low; well engineered.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ARCH-001 | Monorepo structure | `src/**` | clear packages | no packaging | P3 | add metadata |
| ARCH-002 | Boundaries | dirs | clear | — | — | — |
| ARCH-003 | Auth flow | `_resolve_identity` | fingerprint-pinned | — | — | — |
| ARCH-004 | Tenant boundaries | single-site lab | none | multi-site absent | P3 | document |
| ARCH-005 | Request lifecycle | `handle()` | route table | no rate limit | P2 | SEC |
| ARCH-006 | Data flow | agent→CP→SQLite | atomic writes | — | — | — |
| ARCH-007 | Background jobs | agent cycle | ordered recovery | — | — | — |
| ARCH-008 | Queues | `queue.py` | bounded + accounting | expiry lazy | P3 | DATA |
| ARCH-009 | Webhooks | `ingest/vector` | cert attributed | no dedupe | P2 | API |
| ARCH-010 | Realtime | none | N/A | — | — | — |
| ARCH-011 | Notifications | alerts yaml | rules only | no pager | P2 | OBS |
| ARCH-012 | External integrations | Vector/Prometheus | additive | — | — | — |

## Findings

### Finding ID: ARCH-P2-001 - The control plane executes a mutable working tree, not a pinned release

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `deploy/edge-control-plane.service` — `WorkingDirectory=/home/user/falcon-edge-build`, `ExecStart=... -m falcon_control --config .../edge-control-plane.lab.json`
  - `src/falcon_control/service.py` — `source_state()` reports `source_commit`/`source_dirty`
  - `docs/CURRENT_STATE.md` — "the live control plane runs from the working tree" (R-015)
- What is happening: the running service imports code from a checkout that can be edited in place; nothing binds the running bytes to a commit/digest.
- Why it matters: an uncommitted or partially-applied edit can serve traffic; `healthz` only observes dirtiness, it does not prevent it.
- User / business impact: incidents are hard to reproduce; "what is deployed" is not provable.
- Security / privacy / reliability impact: supply-chain/deploy integrity gap.
- Recommended fix: deploy from a pinned release directory or `git worktree` at a recorded commit; fail `healthz` (or alarm) when `source_dirty` is true in the deployed unit.
- Suggested validation: start the unit with a dirty tree and assert readiness degrades / an alert fires.
- Owner suggestion: build-agent + owner
- Effort estimate: M
- Dependencies: release pipeline
- Status: open

### Finding ID: ARCH-P2-002 - Edge control plane is a co-tenant single point of failure on the shared lab host

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `AGENTS.md` — "the monitoring stack on the same host is the control-plane platform"; interfaces `ens18/ens19/wg0`
  - `ledgers/risk_register.md` — R-003 "Edge services share a host with the live monitoring stack"
  - `deploy/edge-control-plane.service` — additive lab service
- What is happening: edge and monitoring share one KVM host, kernel, `wg0`, and disk; there is no resource/failure isolation beyond systemd sandboxing.
- Why it matters: a host-level fault (OOM, disk, wg0 misconfig) affects both programs; edge owns no dedicated host.
- User / business impact: correlated outage across monitoring and edge management.
- Security / privacy / reliability impact: shared-fate; no independent recovery domain.
- Recommended fix: record an explicit availability dependency and a break-glass procedure; move the edge control plane to its own host/VM before production.
- Suggested validation: failover tabletop; verify monitoring still functions with the edge unit stopped and vice versa.
- Owner suggestion: owner
- Effort estimate: L
- Dependencies: hardware
- Status: open

### Finding ID: ARCH-P3-001 - Bare stdlib HTTP transport has no connection or rate limits

- Severity: P3
- Confidence: High
- Area: ARCH
- Evidence:
  - `src/falcon_control/http_server.py` — `ThreadingHTTPServer`, unbounded threads
  - `src/falcon_control/service.py` — `MAX_BODY_BYTES = 2 * 1024 * 1024`
- What is happening: each connection spawns a thread; the only bound is body size. There is no request rate limit, concurrency cap, or slow-loris timeout at the transport.
- Why it matters: a misbehaving or hostile client on the lab network can exhaust threads/memory.
- Security / privacy / reliability impact: DoS exposure on a lab service.
- Recommended fix: use a bounded thread pool / request timeout, or front with a reverse proxy that enforces limits.
- Suggested validation: load test with concurrent connections; assert bounded memory.
- Owner suggestion: build-agent
- Effort estimate: M
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unpinned runtime tree | P2 | Medium | Integrity incident | `edge-control-plane.service` | pinned deploy |
| Shared-host failure | P2 | Medium | Correlated outage | `AGENTS.md`, R-003 | separate host |
| Transport DoS | P3 | Low | Availability | `http_server.py` | bounded pool |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Surface `source_dirty` as an alert; document the shared-host dependency.

### This Month
Pin the deployed control-plane tree; add transport limits.

### Later / Platform Evolution
Dedicated edge control-plane host; multi-site tenancy model.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Alert on `source_dirty` | catches unpinned runtime | `config/prometheus/edge-alerts.yaml` | rule fires |
| Document co-tenancy | operator awareness | `AGENTS.md` | reviewed |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Pinned deploy dir | P2 | build-agent | M | release |
| Transport limits | P3 | build-agent | M | none |
| Multi-site tenant model | P3 | owner | L | roadmap |

## Suggested Tests

- Integration: dirty-tree startup readiness.
- Load: N concurrent requests bounded memory.
- Tabletop: monitoring survives edge stop and vice versa.

## Suggested Documentation Updates

- `docs/CURRENT_STATE.md`: state the shared-host availability dependency.
- `deploy/README` (new): explain the working-tree deploy and its risk.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is a dedicated host planned? | resolves ARCH-P2-002 | owner plan |
| Was a pinned deploy ever attempted? | effort estimate | git history |

## Appendix

```mermaid
flowchart LR
  subgraph LabHost["Lab host (KVM)"]
    CP[edge-control-plane] --> DB[(control-plane.db)]
    CP --> SEC[/falcon-edge-secrets/]
    MON[monitoring stack]
  end
  subgraph Pi["Raspberry Pi sensor"]
    AG[falcon-agent] --> Q[(queue.db)]
    AG --> ST[state.json]
    UA[f update verify/swap] --> SRC[/opt/falcon-edge/src]
  end
  AG -- mTLS heartbeat/desired/events --> CP
  CP -- signed manifest/directive --> AG
  AG -- artifact download --> CP
```
