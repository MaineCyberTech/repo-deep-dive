# Risk Register

Run: `20261003-0018-develop-a72b8cc` · Target: `C:\temp\chat` @ `a72b8cc` · Profile: base

Scoring: Likelihood (L) and Impact (I) low/med/high. Severity per shared model.

| Rank | Risk ID | Title | Severity | L | I | Source findings | Owner | Window |
|---:|---|---|---|---|---|---|---|---|
| 1 | R-01 | Prod RLS weakened to `USING (true)` → all users' PII readable | P0 | High | High | SEC-P0-001, CI-P1-002 | Security/Release | Immediate |
| 2 | R-02 | Deploy seeds prod with known-password test accounts | P1 | High | High | DATA-P1-001 | Release | Immediate |
| 3 | R-03 | Admin endpoints leak cross-tenant users/audit/exports | P1 | High | High | SEC-P1-003/004/005/006 | API | 7 days |
| 4 | R-04 | Webhook/socket/push broken or unauthorized due to anon client | P1 | High | High | ARCH-P1-001/002, FINAL-P1-001 | API | 7 days |
| 5 | R-05 | Deploy deletes Redis volume → queued work lost | P1 | High | Med | DATA-P1-002, CI-P1-004 | Infra | Immediate |
| 6 | R-06 | SSH open to `0.0.0.0/0` | P1 | High | High | SEC-P1-007 | Infra | Immediate |
| 7 | R-07 | Committed credential `test-signin.json` | P1 | High | High | SEC-P1-002, SUPPLY-P1-001 | Security | Immediate |
| 8 | R-08 | E2E/security gates non-blocking → regressions ship | P1 | High | Med | CI-P1-003, TEST-P1-001 | QA/CI | 7 days |
| 9 | R-09 | Prod auto-deploy without enforced review | P1 | Med | High | CI-P1-001, CI-P2-007 | Release | 7 days |
| 10 | R-10 | Webhook signature optional; retries non-durable | P1 | Med | Med | SEC-P1-008, FEAT-P1-002 | Integrations | 30 days |
| 11 | R-11 | `/metrics` readable by any user; tenant labels | P1 | High | Med | API-P1-001, OBS-P2-002 | API | 7 days |
| 12 | R-12 | No alerting wired | P1 | High | Med | OBS-P1-001 | Ops | 30 days |
| 13 | R-13 | Single-node topology / no HA / Redis SPOF | P2 | Med | High | ARCH-P2-003 | Infra | 30–90 days |
| 14 | R-14 | Coverage/diff-coverage weak; no RLS tests | P2 | High | Med | TEST-P2-002/003 | QA | 30 days |
| 15 | R-15 | Migration rollback never executed; duplicate migration | P2 | Med | Med | DATA-P2-003/004, TEST-P2-004 | DB | 30 days |
| 16 | R-16 | Actions tag-pinned; SBOM not for prod | P2 | Med | Med | SUPPLY-P2-002/004 | CI | 30 days |
| 17 | R-17 | GDPR deletion partial/coupled | P2 | Med | Med | DATA-P2-005 | Privacy | 30 days |
| 18 | R-18 | Generated artifacts/archives/encoding debris | P2/P3 | High | Low | INV-P2-001, HYG-P2-001, SUPPLY-P3-005 | Maintainer | 30 days |
| 19 | R-19 | Naive sanitizer blocks legitimate content | P2 | Med | Low | FEAT-P2-004 | API | 30 days |
| 20 | R-20 | Contract drift (errors, OpenAPI, status field) | P2/P3 | Med | Low | API-P2-002/003/004, API-P3-005 | API | 90 days |
| 21 | R-21 | Admin error logs in-memory only | P2 | Med | Low | OBS-P2-003 | Ops | 30 days |
| 22 | R-22 | CSRF length-mismatch 500 | P2 | Low | Low | SEC-P2-009 | API | 90 days |
| 23 | R-23 | Socket typing/leave to arbitrary rooms | P2 | Low | Low | SEC-P2-010 | Real-time | 30 days |

## Accepted / monitor

- None recommended at present.

## Notes

- R-01/R-02 are the same automated mechanism (deploy-time SQL) manifesting as security and data risks.
- Severity totals: P0 1, P1 24, P2 31, P3 7 (63 findings).

## Finding index

| ID | Severity | Title |
|---|---|---|
| SEC-P0-001 | P0 | Production deploy creates `users_select USING (true)`, exposing all users' PII to any authenticated user |
| API-P1-001 | P1 | `/metrics` is readable by any authenticated user |
| ARCH-P1-001 | P1 | Webhook service uses the anonymous Supabase client, so RLS denies all operations |
| ARCH-P1-002 | P1 | Socket.io authorization and presence use the anonymous client; membership checks fail/bypass |
| BLD-P1-001 | P1 | Web build fails prerendering /install (navigator is not defined) |
| CI-P1-001 | P1 | Production auto-deploys on push to `main` without a required review gate in-repo |
| CI-P1-002 | P1 | Deploy workflow mutates production schema and data from CI |
| CI-P1-003 | P1 | Security scans are non-blocking |
| CI-P1-004 | P1 | Deploy prunes all Docker volumes (data loss) |
| DATA-P1-001 | P1 | Deploy workflows seed production with test users and a hardcoded password |
| DATA-P1-002 | P1 | Deploy runs `docker system prune -af --volumes`, destroying the Redis named volume |
| EXEC-P1-001 | P1 | Release gate must be conditional on P0/P1 remediation |
| FEAT-P1-001 | P1 | `/v1/auth/magic-link` does not send a magic link |
| FEAT-P1-002 | P1 | Webhook retries are in-process `setTimeout`, not durable |
| FINAL-P1-001 | P1 | Systemic Supabase client/role mismatch |
| FINAL-P1-002 | P1 | Deploy pipeline mutates schema/policies/data outside migrations |
| OBS-P1-001 | P1 | No alerting is wired despite metrics and a TODO |
| SEC-P1-002 | P1 | Tracked credential file `test-signin.json` |
| SEC-P1-003 | P1 | Admin `/v1/admin/users` returns all platform users (including email) to any workspace admin |
| SEC-P1-004 | P1 | Admin `/v1/admin/audit-logs` leaks other tenants' logs when `workspaceId` omitted |
| SEC-P1-005 | P1 | Admin compliance exports are not tenant-scoped on list/download |
| SEC-P1-006 | P1 | Bulk import endpoints operate globally with only "admin of anything" authorization |
| SEC-P1-007 | P1 | SSH is open to the internet by default |
| SEC-P1-008 | P1 | Webhook secrets are optional and signature can be omitted |
| SUPPLY-P1-001 | P1 | Credential committed to the repository |
| TEST-P1-001 | P1 | E2E tests skip without `test-signin.json` and are non-blocking |
| API-P2-002 | P2 | Inconsistent error response shapes in parts of the API |
| API-P2-003 | P2 | User input interpolated into PostgREST filters (`.or(...)`) |
| API-P2-004 | P2 | `PATCH /v1/auth/status` accepts unvalidated `customStatus` |
| ARCH-P2-003 | P2 | Single-node, no-high-availability topology |
| ARCH-P2-004 | P2 | Worker `/metrics` and health endpoints are unauthenticated |
| CI-P2-005 | P2 | Migration validation and order checks are non-blocking |
| CI-P2-006 | P2 | `build-push` pushes images on pull requests |
| CI-P2-007 | P2 | Branch-protection check cannot fail the build and uses an outdated API shape |
| DATA-P2-003 | P2 | Duplicate `add_user_groups` migrations |
| DATA-P2-004 | P2 | Rollback scripts are only proven to exist, never executed |
| DATA-P2-005 | P2 | `gdpr_delete_user` is a hard multi-table delete with partial coverage and coupled auth deletion |
| EXEC-P2-002 | P2 | Documentation materially overstates readiness |
| FEAT-P2-003 | P2 | Webhook idempotency key is regenerated per attempt |
| FEAT-P2-004 | P2 | Naive input sanitizer blocks legitimate content |
| FINAL-P2-003 | P2 | Release confidence limited by advisory gates |
| HYG-P2-001 | P2 | Generated outputs and audit artifacts committed |
| HYG-P2-002 | P2 | One-off remediation scripts and duplicated logic/schema remain |
| INV-P2-001 | P2 | Committed audit/generated artifacts bloat the repository |
| INV-P2-002 | P2 | Credential file `test-signin.json` is tracked |
| INV-P2-003 | P2 | Documentation self-contradicts repository state |
| OBS-P2-002 | P2 | `/metrics` authorization is weak and label cardinality is risky |
| OBS-P2-003 | P2 | Error tracking is optional and admin log buffer is in-memory only |
| OBS-P2-004 | P2 | No distributed tracing / correlation to a collector |
| SEC-P2-009 | P2 | `timingSafeEqual` can throw on length mismatch (unhandled 500) in CSRF middleware |
| SEC-P2-010 | P2 | Socket typing/leave events can be sent to arbitrary channel rooms |
| SUPPLY-P2-002 | P2 | GitHub Actions are not pinned to commit SHAs |
| SUPPLY-P2-003 | P2 | Dependency vulnerability scanning is advisory-only |
| SUPPLY-P2-004 | P2 | SBOM is generated only for develop and not for production artifacts |
| TEST-P2-002 | P2 | Low coverage thresholds and non-blocking diff coverage |
| TEST-P2-003 | P2 | No real-database/RLS integration test tier |
| TEST-P2-004 | P2 | Migration rollback is validated by file existence only |
| API-P3-005 | P3 | OpenAPI spec coverage/consistency needs verification |
| ARCH-P3-005 | P3 | Duplicated `requireAdmin` implementations |
| HYG-P3-003 | P3 | Unresolved TODO in operational metrics |
| HYG-P3-004 | P3 | Encoding artifacts and inconsistent comments |
| INV-P3-001 | P3 | Character-encoding (mojibake) artifacts in docs and config |
| INV-P3-002 | P3 | Overlapping and inconsistent environment example files |
| SUPPLY-P3-005 | P3 | Large binary archives committed to the repo |
