# Access Control Matrix — Snowride @ 59e12b9

Derived from `apps/realtime/src/server.ts` (`authorizedForOps`, `authorizedForAdmin`, route handlers), `apps/realtime/src/auth.ts`, `docs/API.md`, and `supabase/migrations/0002`/`0017`.

| Surface | anon | authenticated player | moderator | admin | metrics token | service_role |
|---|---|---|---|---|---|---|
| `POST /perf`, `POST /client-error` | ✅ | ✅ | ✅ | ✅ | n/a | n/a |
| `GET /healthz`,`/readyz`,`/config`,`/equipment`,`/content/*`,`/challenges`,`/launch-readiness`,`/perf-budget`,`/economy/simulation` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /metrics` | ❌ (loopback unless token) | ❌ | ❌ | ✅ (JWT) | ✅ | ✅ |
| `GET /beta`, `/admin/live`, `/admin/ops`, `/admin/version`, `/admin/signals`, `/admin/metrics/history`, `/admin/liveops` (GET) | ❌ | ❌ | ❌ | ✅ | ✅ (ops token) | ✅ |
| `GET /admin/{player,audit,suspensions,errors,submissions,run}`, `/perf-recent` | ❌ | ❌ | ❌ | ✅ (admin JWT only) | ❌ | ✅ |
| `POST /admin/*` mutations (`moderate`, `run-state`, `run/recover`, `run/reconcile-effects`, `economy/*`, `room/teardown`, `season/rollover`, `liveops`) | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| `POST /runs`, `/creator/courses` | ❌ | ✅ (own identity) | ✅ | ✅ | ❌ | ✅ |
| `GET /pass`, `/progression`, `POST /challenges/claim` | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Socket events (`lobby:*`, `player:*`, `party:*`) | ❌ (JWT required on first event) | ✅ | ✅ | ✅ | n/a | n/a |
| Socket `admin:metrics`, `admin:reopen-signal`, `admin:global-avalanche`, `admin:catalog-check` | ❌ | ❌ | ❌ | ✅ (`role==="admin"`) | ❌ | n/a |
| DB tables via RLS | deny-by-default SELECT on public views only | own-row SELECT | via RPC guards | service path | n/a | ALL (bypass RLS) |

## Notes

- Admin role is sourced from `app_metadata.role` (server-controlled JWT claim), never a request parameter.
- Ops endpoints accept the shared `METRICS_TOKEN`; PII/mutation endpoints deliberately do not.
- Moderator-gated SQL RPCs derive the acting identity from JWT claims (`social_guard_moderator`, migration 0017).
- Residual: HTTP endpoints have no Origin check (SEC-P2-001); claim-less SQL callers are trusted (SEC-P3-001) but `anon` has no EXECUTE.
