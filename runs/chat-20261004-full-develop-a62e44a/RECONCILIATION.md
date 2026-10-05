# Reconciliation — chat-20261004-full-develop-a62e44a (2026-10-05)

Post-audit reconciliation of the `chat` full-domain run
(`chat` @ `a62e44a`, branch `develop`), per
`runbooks/POST_AUDIT_PIPELINE.md`.

## Corrections

| Finding | Was | Now | Basis |
|---|---|---|---|
| `TEST-P2-002` | open | verified-fixed | `validate.yml` `migration-test` runs every `supabase/tests/*.sql` (incl. `rls_tenant_isolation.sql`) inside the local Supabase Postgres via `docker exec … psql` at `a62e44a`. The "not run by CI" claim was incorrect. |
| `RLS-P2-001` | open | verified-fixed | Same root cause as `TEST-P2-002`; the RLS isolation SQL test is executed by CI. |

Both were recorded as open against a stale reading of `package.json`
(`test:rls`) and missed the inline CI step. No code change was required.

## Draft remediation PRs opened against `chat` (`develop`)

| Finding(s) | PR | Scope |
|---|---|---|
| `SEC-P2-001` | chat#104 | Deliver `WEBHOOK_ENCRYPTION_KEY` via prod compose + env example. |
| `SEC-P2-002`, `WH-P2-002` | chat#105 | `redirect: "manual"` webhook dispatch; reject credential URLs; tests. |
| `INV-P2-001`, `DOC-P2-002` | chat#106 | Delete the six stale root reconciliation artifacts. |
| `CI-P2-001` | chat#107 | Make `infra-development` manual/plan-only + `development` environment. |
| `BP-P2-001`, `CI-P2-003` | chat#108 | Gate the default branch (`develop`), not a non-existent `main`. |

These PRs are **draft and unmerged**, so the findings above stay `open`
until the changes land and are re-verified at the merged commit.

## Owner-gated / policy-gated (no code change)

| Finding | Status | Residual / required owner action |
|---|---|---|
| `BP-P2-001`, `CI-P2-003` | open | Live state: repo default is `develop`, there is no `main`, and there are **no rulesets/branch protection** (`GET /rules/branches/develop` → `[]`, `/branches/develop/protection` → 404). Enable a ruleset on `develop` (PR review, required status checks, no force pushes). The in-repo gate now fails closed until then. |
| `DATA-P2-001` | open | `supabase/migrations/README.md` documents the two `add_user_groups` migrations as **intentional** and forbids editing/deleting applied migrations. The audit's "squash/drop" recommendation conflicts with that documented decision — needs a DB-owner call (rename vs keep). Not changed here. |
| `ARCH-P2-001`, `INFRA-P2-001`, `RES-P2-001` | open | Single-node topology / no environment isolation: infrastructure decision, out of scope for code remediation. |
| `EXEC-P1-001`, `FINAL-P1-001` | open | Release gate stays conditional until the P2 items above are remediated and re-verified. |
