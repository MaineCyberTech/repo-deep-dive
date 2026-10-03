# 02 Architecture & Runtime Topology

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Runtime topology: web client, realtime service, data plane, reverse proxy, containers, and how they compose on the certified single host. Read-only.

## Evidence Reviewed

- `infra/compose/docker-compose.yml` (web, realtime, otel, nginx, certbot; networks/volumes)
- `apps/web/Dockerfile`, `apps/realtime/Dockerfile`
- `infra/nginx/nginx.conf.template` (routing, TLS, socket upgrade)
- `apps/realtime/src/server.ts` — `http.createServer`, Socket.IO CORS, `/healthz`, `/readyz`
- `apps/web/app/healthz/route.ts`
- `README.md` (deploy topology), `docs/runbooks/INCIDENT.md`

## Verification Performed

- Traced all published ports: only nginx `80/443`; web/realtime `expose` only.
- Confirmed `read_only: true`, `cap_drop: ALL`, `no-new-privileges` on app services.
- Confirmed nginx proxies `/runs`, `/socket.io/`, `/metrics`, `/admin/*`, `/content/*` to `realtime:3001`; `/` to `web:3000`.
- Read `/readyz` handler (line 842) and web `/healthz` route.

## Executive Summary

Topology is a clean single-host reverse-proxy stack: nginx terminates TLS, web (Next standalone) and realtime (Socket.IO/HTTP) are internal-only, Supabase is hosted, OTel collector is internal. App containers are hardened (non-root UID 1001, read-only rootfs, dropped caps). The dominant architectural risks are the deliberate single-node, in-process state model (no HA, no shared adapter) and the absence of container resource limits, which together create noisy-neighbour/OOM and restart-induced state loss. A notable correctness gap: `/readyz` reports "accepting" purely from a shutdown flag and does not probe the Supabase/JWKS dependency, so a dependency outage is reported ready.

## Inventory

| Component | Image / build | Ports | Hardening |
|---|---|---|---|
| nginx | `nginx:1.27.4-alpine@sha256:4ff1…` | 80,443 published | `cap_drop: ALL` + NET_BIND_SERVICE/CHOWN/SETUID/SETGID |
| web | `snowride-web:certified` (apps/web/Dockerfile) | expose 3000 | non-root 1001, read_only, cap_drop ALL |
| realtime | `snowride-realtime:certified` | expose 3001 | non-root 1001, read_only, cap_drop ALL |
| otel | pinned digest | internal only | user 1001, read_only, cap_drop ALL |
| certbot | pinned digest | tls profile | volumes only |

## Findings

### Finding ID: ARCH-P2-001 - Compose services define no CPU, memory or PID limits

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `infra/compose/docker-compose.yml` — `web`, `realtime`, `nginx`, `otel` have `restart`, `read_only`, healthchecks but no `mem_limit`, `cpus`, `pids_limit`, or `deploy.resources`
  - `apps/realtime/src/server.ts` — in-process room sims, replay cache, `runSessions` map
- What is happening: A memory/CPU spike in one service can starve the host (single certified host runs everything).
- Why it matters: The host previously suffered a disk-full incident (referenced in `scripts/assurance/assurance.sh`); resource exhaustion is a demonstrated failure mode.
- User / business impact: Full outage rather than a degraded single service.
- Security / privacy / reliability impact: Reduced blast-radius containment.
- Recommended fix: Add `mem_limit`/`cpus`/`pids_limit` (or compose `deploy.resources`) with values validated against `/perf-budget` and the capacity lane.
- Suggested validation: `docker compose config` shows limits; an induced memory hog cannot take down nginx.
- Owner suggestion: Operator
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: ARCH-P2-002 - Readiness endpoint cannot fail when a dependency is unavailable

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `apps/realtime/src/server.ts` line ~842: `/readyz` returns `{ ok: true, accepting: !this.shutdownStarted }`
  - `apps/web/app/healthz/route.ts`: returns `{ ok: true }` unconditionally
- What is happening: Readiness is true whenever the process started, regardless of Supabase/JWKS reachability.
- Why it matters: Orchestrators and load balancers route traffic to an instance that cannot serve `/runs` or verify tokens.
- User / business impact: Elevated 4xx/5xx during dependency outages; no automatic removal from rotation.
- Security / privacy / reliability impact: Reliability only.
- Recommended fix: Make `/readyz` perform a bounded, cached dependency probe (JWKS fetch or `select 1`) and return 503 when unhealthy.
- Suggested validation: Integration test simulates an unreachable `SUPABASE_URL` and asserts `/readyz` 503.
- Owner suggestion: Realtime engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: ARCH-P2-003 - Authoritative lobby/LiveOps state is process-local and lost on restart

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `apps/realtime/src/server.ts` — `roomSims`, `runSessions`, `submitRate`, `liveOpsOverrides` are in-process maps
  - `docs/runbooks/INCIDENT.md` line 46: "restart resets counters and process-local LiveOps overrides"
  - `docs/runbooks/KILL_SWITCHES.md` line 55: "LIVEOPS_* can also be toggled at runtime from /admin (process-local; a restart reverts)"
- What is happening: Rooms, sessions, rate windows and admin kill-switch overrides live only in the single realtime process.
- Why it matters: A restart/deploy drops active rooms and silently reverts an operator's emergency kill switch.
- User / business impact: Disconnects mid-race; emergency freeze may lapse without notice.
- Security / privacy / reliability impact: Loss of an active moderation/anti-cheat control until re-applied.
- Recommended fix: Persist LiveOps override state (durable store) and re-apply at boot; document room loss as an accepted limitation or add graceful drain.
- Suggested validation: Recreate realtime after toggling `LIVEOPS_KILL_PUBLISH` and confirm the override survives.
- Owner suggestion: Realtime engineer / operator
- Effort estimate: M
- Dependencies: None
- Status: open

## Risks

- R-ARCH-1: Noisy-neighbour outage from absent quotas.
- R-ARCH-2: False readiness during dependency failure.
- R-ARCH-3: Emergency control reversion on restart (safety/anti-cheat).

## Recommendations

1. Add resource limits and validate against used capacity.
2. Make readiness dependency-aware.
3. Persist LiveOps overrides or loudly surface their process-local nature at boot.

## Quick Wins

- Resource limits (S).
- `/readyz` probe (S).

## Hardening Backlog

- Optional HA/shared-adapter design spike (only if measured load requires it, per `ext_review.md`).

## Suggested Tests

- Dependency-down readiness test; restart-override persistence test; resource soak.

## Suggested Documentation Updates

- `docs/runbooks/INCIDENT.md`: state that readiness does not currently reflect dependency health.

## Open Questions

- Is there an external orchestrator consuming `/readyz`? (`Unknown` — single-host compose only.)

## Appendix

- Mermaid: `client → nginx(443) → {web:3000, realtime:3001} → Supabase + otel`.
