# Access control matrix — snowride @ `38b34a9`

Companion artifact for `24_access_control_matrix_audit.md`. Read-only derivation
from `apps/realtime/src/server.ts`, `apps/realtime/src/config.ts` and
`supabase/migrations/0002_rls_and_grants.sql`. No credential or token value is
reproduced.

## Principal roles

| Principal | Credential | Source |
|---|---|---|
| Anonymous guest | ephemeral guest identity | client session |
| Registered user | Supabase JWT (audience `authenticated`) | JWKS verification |
| Admin / moderator | Supabase JWT `role=admin` | JWKS verification |
| Ops scraper | `METRICS_TOKEN` (optional) | env, host-only |
| Service | service-role key | env, server-only |

## Surface × principal

| Surface | Guest | User | Admin | Ops token | Service |
|---|---|---|---|---|---|
| `/healthz`, `/readyz` | allow | allow | allow | allow | allow |
| `/config`, `/equipment`, `/content/*`, `/challenges`, `/beta`, `/launch-readiness`, `/perf-budget` | allow (public read) | allow | allow | allow | allow |
| `/pass`, `/progression`, `/perf-summary*` | deny | allow (owner-scoped) | allow | allow | allow |
| `POST /perf`, `POST /client-error` | allow (bounded) | allow | allow | allow | allow |
| `POST /runs`, `POST /creator/courses` | deny (auth) | allow | allow | allow | allow |
| `/metrics` | loopback only (404 proxied) | deny | allow | allow | allow |
| `/admin/*` (reads + mutations) | deny | deny | allow | deny | allow |
| Supabase tables (RLS) | owner-scoped SELECT where public read | owner-scoped | moderator views | n/a | full |

## Notes

- Admin mutations record an `admin_audit_events` row
  (`0003_economy_and_submission.sql:252`, `record_admin_audit()`).
- `ADMIN-P3-001`: admin routes have no dedicated rate limit or step-up check.
- `SEC-P3-001`: `METRICS_TOKEN` is compared with `===` (not constant-time) and
  has no rotation procedure.
- Multi-tenancy isolation is not applicable (`25_multi_tenant_isolation_attack_simulation.md`).
