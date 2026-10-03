# Follow-up register

Auto-created by tools/remediation_status.py. Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| SEC-P0-001 | P0 | Production deploy creates `users_select USING (true)`, exposing all users' PII to any authenticated user |  |  | partially-fixed | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| API-P1-001 | P1 | `/metrics` is readable by any authenticated user |  |  | open |  |
| ARCH-P1-001 | P1 | Webhook service uses the anonymous Supabase client, so RLS denies all operations |  |  | open |  |
| ARCH-P1-002 | P1 | Socket.io authorization and presence use the anonymous client; membership checks fail/bypass |  |  | open |  |
| CI-P1-001 | P1 | Production auto-deploys on push to `main` without a required review gate in-repo |  |  | open |  |
| CI-P1-002 | P1 | Deploy workflow mutates production schema and data from CI |  |  | partially-fixed | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| CI-P1-003 | P1 | Security scans are non-blocking |  |  | open |  |
| CI-P1-004 | P1 | Deploy prunes all Docker volumes (data loss) |  |  | open |  |
| DATA-P1-001 | P1 | Deploy workflows seed production with test users and a hardcoded password |  |  | partially-fixed | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| DATA-P1-002 | P1 | Deploy runs `docker system prune -af --volumes`, destroying the Redis named volume |  |  | open |  |
| EXEC-P1-001 | P1 | Release gate must be conditional on P0/P1 remediation |  |  | open |  |
| FEAT-P1-001 | P1 | `/v1/auth/magic-link` does not send a magic link |  |  | open |  |
| FEAT-P1-002 | P1 | Webhook retries are in-process `setTimeout`, not durable |  |  | open |  |
| FINAL-P1-001 | P1 | Systemic Supabase client/role mismatch |  |  | open |  |
| FINAL-P1-002 | P1 | Deploy pipeline mutates schema/policies/data outside migrations |  |  | open |  |
| OBS-P1-001 | P1 | No alerting is wired despite metrics and a TODO |  |  | open |  |
| SEC-P1-002 | P1 | Tracked credential file `test-signin.json` |  |  | open |  |
| SEC-P1-003 | P1 | Admin `/v1/admin/users` returns all platform users (including email) to any workspace admin |  |  | open |  |
| SEC-P1-004 | P1 | Admin `/v1/admin/audit-logs` leaks other tenants' logs when `workspaceId` omitted |  |  | open |  |
| SEC-P1-005 | P1 | Admin compliance exports are not tenant-scoped on list/download |  |  | open |  |
| SEC-P1-006 | P1 | Bulk import endpoints operate globally with only "admin of anything" authorization |  |  | open |  |
| SEC-P1-007 | P1 | SSH is open to the internet by default |  |  | open |  |
| SEC-P1-008 | P1 | Webhook secrets are optional and signature can be omitted |  |  | open |  |
| SUPPLY-P1-001 | P1 | Credential committed to the repository |  |  | open |  |
| TEST-P1-001 | P1 | E2E tests skip without `test-signin.json` and are non-blocking |  |  | open |  |
| API-P2-002 | P2 | Inconsistent error response shapes in parts of the API |  |  | open |  |
| API-P2-003 | P2 | User input interpolated into PostgREST filters (`.or(...)`) |  |  | open |  |
| API-P2-004 | P2 | `PATCH /v1/auth/status` accepts unvalidated `customStatus` |  |  | open |  |
| ARCH-P2-003 | P2 | Single-node, no-high-availability topology |  |  | open |  |
| ARCH-P2-004 | P2 | Worker `/metrics` and health endpoints are unauthenticated |  |  | open |  |
| CI-P2-005 | P2 | Migration validation and order checks are non-blocking |  |  | open |  |
| CI-P2-006 | P2 | `build-push` pushes images on pull requests |  |  | open |  |
| CI-P2-007 | P2 | Branch-protection check cannot fail the build and uses an outdated API shape |  |  | open |  |
| DATA-P2-003 | P2 | Duplicate `add_user_groups` migrations |  |  | open |  |
| DATA-P2-004 | P2 | Rollback scripts are only proven to exist, never executed |  |  | open |  |
| DATA-P2-005 | P2 | `gdpr_delete_user` is a hard multi-table delete with partial coverage and coupled auth deletion |  |  | open |  |
| EXEC-P2-002 | P2 | Documentation materially overstates readiness |  |  | open |  |
| FEAT-P2-003 | P2 | Webhook idempotency key is regenerated per attempt |  |  | open |  |
| FEAT-P2-004 | P2 | Naive input sanitizer blocks legitimate content |  |  | open |  |
| FINAL-P2-003 | P2 | Release confidence limited by advisory gates |  |  | open |  |
| HYG-P2-001 | P2 | Generated outputs and audit artifacts committed |  |  | open |  |
| HYG-P2-002 | P2 | One-off remediation scripts and duplicated logic/schema remain |  |  | open |  |
| INV-P2-001 | P2 | Committed audit/generated artifacts bloat the repository |  |  | open |  |
| INV-P2-002 | P2 | Credential file `test-signin.json` is tracked |  |  | open |  |
| INV-P2-003 | P2 | Documentation self-contradicts repository state |  |  | open |  |
| OBS-P2-002 | P2 | `/metrics` authorization is weak and label cardinality is risky |  |  | open |  |
| OBS-P2-003 | P2 | Error tracking is optional and admin log buffer is in-memory only |  |  | open |  |
| OBS-P2-004 | P2 | No distributed tracing / correlation to a collector |  |  | open |  |
| SEC-P2-009 | P2 | `timingSafeEqual` can throw on length mismatch (unhandled 500) in CSRF middleware |  |  | open |  |
| SEC-P2-010 | P2 | Socket typing/leave events can be sent to arbitrary channel rooms |  |  | open |  |
| SUPPLY-P2-002 | P2 | GitHub Actions are not pinned to commit SHAs |  |  | open |  |
| SUPPLY-P2-003 | P2 | Dependency vulnerability scanning is advisory-only |  |  | open |  |
| SUPPLY-P2-004 | P2 | SBOM is generated only for develop and not for production artifacts |  |  | open |  |
| TEST-P2-002 | P2 | Low coverage thresholds and non-blocking diff coverage |  |  | open |  |
| TEST-P2-003 | P2 | No real-database/RLS integration test tier |  |  | open |  |
| TEST-P2-004 | P2 | Migration rollback is validated by file existence only |  |  | open |  |
| API-P3-005 | P3 | OpenAPI spec coverage/consistency needs verification |  |  | open |  |
| ARCH-P3-005 | P3 | Duplicated `requireAdmin` implementations |  |  | open |  |
| HYG-P3-003 | P3 | Unresolved TODO in operational metrics |  |  | open |  |
| HYG-P3-004 | P3 | Encoding artifacts and inconsistent comments |  |  | open |  |
| INV-P3-001 | P3 | Character-encoding (mojibake) artifacts in docs and config |  |  | open |  |
| INV-P3-002 | P3 | Overlapping and inconsistent environment example files |  |  | open |  |
| SUPPLY-P3-005 | P3 | Large binary archives committed to the repo |  |  | open |  |
