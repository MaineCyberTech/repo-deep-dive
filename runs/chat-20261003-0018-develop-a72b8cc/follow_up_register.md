# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| SEC-P0-001 | P0 | Production deploy creates `users_select USING (true)`, exposing all users' PII to any authenticated user |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P1-001 | P1 | `/metrics` is readable by any authenticated user |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P1-001 | P1 | Webhook service uses the anonymous Supabase client, so RLS denies all operations |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P1-002 | P1 | Socket.io authorization and presence use the anonymous client; membership checks fail/bypass |  |  | verified-fixed | re-audit 2026-10-04: closed |
| BLD-P1-001 | P1 | Web build fails prerendering /install (navigator is not defined) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-001 | P1 | Production auto-deploys on push to `main` without a required review gate in-repo |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-002 | P1 | Deploy workflow mutates production schema and data from CI |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-003 | P1 | Security scans are non-blocking |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-004 | P1 | Deploy prunes all Docker volumes (data loss) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P1-001 | P1 | Deploy workflows seed production with test users and a hardcoded password |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P1-002 | P1 | Deploy runs `docker system prune -af --volumes`, destroying the Redis named volume |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P1-001 | P1 | Release gate must be conditional on P0/P1 remediation |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P1-001 | P1 | `/v1/auth/magic-link` does not send a magic link |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P1-002 | P1 | Webhook retries are in-process `setTimeout`, not durable |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P1-001 | P1 | Systemic Supabase client/role mismatch |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P1-002 | P1 | Deploy pipeline mutates schema/policies/data outside migrations |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P1-001 | P1 | No alerting is wired despite metrics and a TODO |  |  | verified-fixed | re-audit 2026-10-04: closed by chat#95 @ 6924305 (Prometheus+Alertmanager wired to ntfy) |
| SEC-P1-002 | P1 | Tracked credential file `test-signin.json` |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-003 | P1 | Admin `/v1/admin/users` returns all platform users (including email) to any workspace admin |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-004 | P1 | Admin `/v1/admin/audit-logs` leaks other tenants' logs when `workspaceId` omitted |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-005 | P1 | Admin compliance exports are not tenant-scoped on list/download |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-006 | P1 | Bulk import endpoints operate globally with only "admin of anything" authorization |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-007 | P1 | SSH is open to the internet by default |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-008 | P1 | Webhook secrets are optional and signature can be omitted |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P1-001 | P1 | Credential committed to the repository |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P1-001 | P1 | E2E tests skip without `test-signin.json` and are non-blocking |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-002 | P2 | Inconsistent error response shapes in parts of the API |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-003 | P2 | User input interpolated into PostgREST filters (`.or(...)`) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-004 | P2 | `PATCH /v1/auth/status` accepts unvalidated `customStatus` |  |  | open |  |
| ARCH-P2-003 | P2 | Single-node, no-high-availability topology |  |  | partially-fixed | remediation PS-U02 open 5dbe6652c1039f3d0b0bb518fef45ae2eca64c0d https://github.com/MaineCyberTech/chat/pull/73 |
| ARCH-P2-004 | P2 | Worker `/metrics` and health endpoints are unauthenticated |  |  | partially-fixed | remediation PS-U02 open 5dbe6652c1039f3d0b0bb518fef45ae2eca64c0d https://github.com/MaineCyberTech/chat/pull/73 |
| CI-P2-005 | P2 | Migration validation and order checks are non-blocking |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-006 | P2 | `build-push` pushes images on pull requests |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-007 | P2 | Branch-protection check cannot fail the build and uses an outdated API shape |  |  | partially-fixed | remediation PS-U03 open 8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3 https://github.com/MaineCyberTech/chat/pull/68 |
| DATA-P2-003 | P2 | Duplicate `add_user_groups` migrations |  |  | open |  |
| DATA-P2-004 | P2 | Rollback scripts are only proven to exist, never executed |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-005 | P2 | `gdpr_delete_user` is a hard multi-table delete with partial coverage and coupled auth deletion |  |  | partially-fixed | remediation PS-U04 open 937b43983fd3efc836f19af8407e4f06e8fcfbc2 https://github.com/MaineCyberTech/chat/pull/74 |
| EXEC-P2-002 | P2 | Documentation materially overstates readiness |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P2-003 | P2 | Webhook idempotency key is regenerated per attempt |  |  | partially-fixed | remediation PS-U06 open 92ef54074256aec75e3858f3339a28c21a980d4e https://github.com/MaineCyberTech/chat/pull/69 |
| FEAT-P2-004 | P2 | Naive input sanitizer blocks legitimate content |  |  | open |  |
| FINAL-P2-003 | P2 | Release confidence limited by advisory gates |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P2-001 | P2 | Generated outputs and audit artifacts committed |  |  | open |  |
| HYG-P2-002 | P2 | One-off remediation scripts and duplicated logic/schema remain |  |  | partially-fixed | remediation PS-U08 open cc41daee2b2e7d8bc4b27beafafe43ad59708a7b https://github.com/MaineCyberTech/chat/pull/75 |
| INV-P2-001 | P2 | Committed audit/generated artifacts bloat the repository |  |  | open |  |
| INV-P2-002 | P2 | Credential file `test-signin.json` is tracked |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-003 | P2 | Documentation self-contradicts repository state |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P2-002 | P2 | `/metrics` authorization is weak and label cardinality is risky |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P2-003 | P2 | Error tracking is optional and admin log buffer is in-memory only |  |  | partially-fixed | remediation PATCH-12 open d458b82e1a6ba11dd87b91b07d60aa7c53396f28 https://github.com/MaineCyberTech/chat/pull/66 |
| OBS-P2-004 | P2 | No distributed tracing / correlation to a collector |  |  | still-open | re-audit 2026-10-04: still-open |
| SEC-P2-009 | P2 | `timingSafeEqual` can throw on length mismatch (unhandled 500) in CSRF middleware |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-010 | P2 | Socket typing/leave events can be sent to arbitrary channel rooms |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-002 | P2 | GitHub Actions are not pinned to commit SHAs |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-003 | P2 | Dependency vulnerability scanning is advisory-only |  |  | partially-fixed | remediation PS-U12 open a202fad83cd2fceb244dc6e815d76da7d8cb9978 https://github.com/MaineCyberTech/chat/pull/78 |
| SUPPLY-P2-004 | P2 | SBOM is generated only for develop and not for production artifacts |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | Low coverage thresholds and non-blocking diff coverage |  |  | partially-fixed | remediation PS-U13 open fe04ab3a01cd04ff3dcc8c9a4cce6153c0340f9b https://github.com/MaineCyberTech/chat/pull/79 |
| TEST-P2-003 | P2 | No real-database/RLS integration test tier |  |  | open |  |
| TEST-P2-004 | P2 | Migration rollback is validated by file existence only |  |  | open |  |
| API-P3-005 | P3 | OpenAPI spec coverage/consistency needs verification |  |  | partially-fixed | remediation PS-U01 open 43ad5e62db6ce224c696cf4c24c7887333ae41c5 https://github.com/MaineCyberTech/chat/pull/72 |
| ARCH-P3-005 | P3 | Duplicated `requireAdmin` implementations |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P3-003 | P3 | Unresolved TODO in operational metrics |  |  | verified-fixed | re-audit 2026-10-04: closed by chat#95 @ 6924305 (TODO removed) |
| HYG-P3-004 | P3 | Encoding artifacts and inconsistent comments |  |  | partially-fixed | remediation PS-U08 open cc41daee2b2e7d8bc4b27beafafe43ad59708a7b https://github.com/MaineCyberTech/chat/pull/75 |
| INV-P3-001 | P3 | Character-encoding (mojibake) artifacts in docs and config |  |  | open |  |
| INV-P3-002 | P3 | Overlapping and inconsistent environment example files |  |  | partially-fixed | remediation PS-U09 open 3a46f2f8c3ab723d3f07402e1559bca9094e21a1 https://github.com/MaineCyberTech/chat/pull/76 |
| SUPPLY-P3-005 | P3 | Large binary archives committed to the repo |  |  | open |  |
