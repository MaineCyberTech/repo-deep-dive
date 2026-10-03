# Feature Implementation and Gap Map

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: FEAT
- Output path: docs/audits/{name}/{run}/03_feature_implementation_map.md
- Scope limitations: static review; no live exercise of backup/offsite.

## Scope

Mapped the lab's user-facing/operational capabilities: capture → transport → storage → search → metrics/alerting → notifications → access, plus backup/restore and edge pairing. Did not run stacks or drills.

## Evidence Reviewed

- `README.md` (capability table, data path).
- `bootstrap/85-backup-job.sh`, `bootstrap/80-offsite-backup.sh`, `automation/validation/restore_rehearsal.sh`.
- `compose/mct/*`, `config/alerting/`, `config/grafana/`, `config/opensearch/`.
- `docs/CURRENT_STATE.md`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| README capability table | Doc | Feature inventory | matches config presence |
| `git show 20b5e57` | Diff | New abort feature | script-level only |
| `compose/mct` vs `mct/` | Tree | Vendoring policy check | both present |

## Executive Summary

Core monitoring features are implemented and documented. The main feature-level gaps are: backup delivery has no retry/backoff/dead-letter (single attempt per day), and the newly added abort-marker behavior is not a complete recovery feature (see ARCH-P1-002). Vendored MCT services are still runnable from `compose/mct` while the subtree policy calls the vendored tree archive-only.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Capture | probe `ens19` Suricata/pmacct | IDS/flows | Implemented | Low | — |
| Transport | Vector aggregator | normalize/enrich/route | Implemented | Medium | shared secret |
| Storage/search | OpenSearch + Dashboards | indexed events | Implemented | Medium | single node |
| Metrics/alerting | Prometheus/Grafana | health + alerts | Implemented | Medium | 3 scrape targets |
| Notifications | ntfy + relay + canary | deliver alerts | Implemented | Medium | relay metrics gap |
| Access | Traefik + Cloudflare | HTTPS entry | Implemented | High | origin auth gap |
| Backup | `85-backup-job.sh` | snapshot/config/offsite | Implemented | High | no retry |
| Offsite | `80-offsite-backup.sh` | copy to object store | Implemented | High | no trap |
| Edge pairing | `docs/edge/EDGE_RELEASE_PIN.md` | frozen contract | Partial | High | unverifiable here |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Pages/routes | 3 | Traefik routers | origin auth | SEC |
| Components | 4 | compose services | single host | ARCH |
| API endpoints | 3 | enroll/ingest | shared secret | API |
| Server actions | 3 | bootstrap stages | — | — |
| Workers/jobs | 2 | systemd timers | retry/graceful-stop | FEAT-P2-002 |
| Database entities | 3 | OpenSearch indices | retention | DATA |
| Permissions | 3 | basic auth + Access | origin auth | SEC |
| Audit logs | 4 | ledgers/evidence | — | — |
| Tests | 3 | 32 suites | no backup e2e | TEST |
| Docs | 4 | extensive | minor stale | HYG |
| Workflow states | 3 | backup freshness gauges | marker semantics | ARCH |
| Failure states | 2 | abort markers partial | incomplete | ARCH-P1-002 |

## Findings

### Finding ID: FEAT-P2-001 - Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `compose/mct/docker-compose.opencanary.yml` — runnable stack referencing `mct`-derived config
  - `compose/mct/iris-web/`, `mct/` (857 files) — vendored tree
  - `docs/` subtree policy (MCT vendoring) — archive-only intent
- What is happening: Vendored MCT services are deployable from this repo, not merely archived.
- Why it matters: Two sources of truth; security fixes can land in one and not the other.
- User / business impact: Inconsistent behaviour between the vendored and native copies.
- Security / privacy / reliability impact: Unpatched copy may remain runnable.
- Recommended fix: Either freeze the vendored tree read-only with a CI guard that forbids compose files under `compose/mct`, or formally adopt those services and bring them into the pin/SBOM scope.
- Suggested validation: CI check that fails if `compose/mct/**` changes without an owner-approved marker.
- Owner suggestion: maintainer
- Effort estimate: M
- Dependencies: EVOL policy
- Status: open

### Finding ID: FEAT-P2-002 - Backup/offsite delivery is single-attempt with no retry, backoff, or dead-letter

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `bootstrap/85-backup-job.sh` lines 51-56 — offsite "attempt" once per run; failure only logged
  - `automation/validation/r2_cold_copy.sh` — one pass
  - `automation/validation/tests/offsite_upload_delta_test.sh` — delta/reuse tested, not retry
- What is happening: A transient offsite failure drops the day's copy with no retry queue.
- Why it matters: Recovery point objective silently missed.
- User / business impact: Data-loss window on repeated transient failures.
- Security / privacy / reliability impact: Reliability gap.
- Recommended fix: Add bounded retry with exponential backoff and a persistent dead-letter record, plus an alert on exhausted retries.
- Suggested validation: Fault-injection test: object store 5xx for N attempts → retry then alert.
- Owner suggestion: ops/resilience
- Effort estimate: M
- Dependencies: None
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Missed offsite copy | P2 | Medium | High | 85-backup-job.sh | FEAT-P2-002 |
| Vendored service drift | P2 | Medium | Medium | compose/mct | FEAT-P2-001 |

## Recommendations

### Immediate / Release Blocking
- None beyond ARCH-P1-002.

### This Week
- Add offsite retry/backoff + alert.

### This Month
- Enforce the vendoring policy in CI.

### Later / Platform Evolution
- Adopt-or-archive decision for MCT.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Alert on offsite failure count | Surfaces misses | 85-backup-job.sh, metrics | export_monitor_metrics.sh |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Offsite retry/DLQ | P2 | ops | M | — |
| Vendoring CI guard | P2 | maintainer | M | policy |

## Suggested Tests

- Offsite transient-failure retry test.
- Compose-mct guard test.

## Suggested Documentation Updates

- `docs/` — state whether MCT is archived or supported.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `compose/mct` actually deployed? | Scope of risk | host `docker ps` |

## Appendix
Not applicable.
