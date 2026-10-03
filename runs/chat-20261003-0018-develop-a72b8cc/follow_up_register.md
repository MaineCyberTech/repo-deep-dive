# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| SEC-P0-001 | P0 | Production deploy creates `users_select USING (true)`, exposing all users' PII to any authenticated user |  |  | partially-fixed | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| API-P1-001 | P1 | `/metrics` is readable by any authenticated user |  |  | partially-fixed | remediation PATCH-08 open 9feae529cc04e0f53e87abb1539b7307dbf62dbf https://github.com/MaineCyberTech/chat/pull/65 |
| ARCH-P1-001 | P1 | Webhook service uses the anonymous Supabase client, so RLS denies all operations |  |  | partially-fixed | Draft PR #59 commit 9bd4f88: webhooks+push use service-role client, socket builds per-user client from JWT; FEAT-P1-002 durable BullMQ retries deferred to PATCH-09 |
| ARCH-P1-002 | P1 | Socket.io authorization and presence use the anonymous client; membership checks fail/bypass |  |  | partially-fixed | Draft PR #59 commit 9bd4f88: webhooks+push use service-role client, socket builds per-user client from JWT; FEAT-P1-002 durable BullMQ retries deferred to PATCH-09 |
| BLD-P1-001 | P1 | Web build fails prerendering /install (navigator is not defined) |  |  | partially-fixed |  |
| CI-P1-001 | P1 | Production auto-deploys on push to `main` without a required review gate in-repo |  |  | partially-fixed | remediation PS-U03 open 8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3 https://github.com/MaineCyberTech/chat/pull/68 |
| CI-P1-002 | P1 | Deploy workflow mutates production schema and data from CI |  |  | partially-fixed | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| CI-P1-003 | P1 | Security scans are non-blocking |  |  | partially-fixed | remediation PATCH-07 open 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2 https://github.com/MaineCyberTech/chat/pull/63 |
| CI-P1-004 | P1 | Deploy prunes all Docker volumes (data loss) |  |  | partially-fixed | Draft PR #61 commit 6733291c: removed --volumes from docker system prune in both deploy workflows (prod :287/:527, dev :219); named volumes preserved. |
| DATA-P1-001 | P1 | Deploy workflows seed production with test users and a hardcoded password |  |  | partially-fixed | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| DATA-P1-002 | P1 | Deploy runs `docker system prune -af --volumes`, destroying the Redis named volume |  |  | partially-fixed | Draft PR #61 commit 6733291c: removed --volumes from docker system prune in both deploy workflows (prod :287/:527, dev :219); named volumes preserved. |
| EXEC-P1-001 | P1 | Release gate must be conditional on P0/P1 remediation |  |  | partially-fixed | remediation PS-U05 open 82f8eaa2c8525febd24f6fbaa7c0ef93de28de82 https://github.com/MaineCyberTech/chat/pull/71 |
| FEAT-P1-001 | P1 | `/v1/auth/magic-link` does not send a magic link |  |  | partially-fixed | remediation PS-U06 open 92ef54074256aec75e3858f3339a28c21a980d4e https://github.com/MaineCyberTech/chat/pull/69 |
| FEAT-P1-002 | P1 | Webhook retries are in-process `setTimeout`, not durable |  |  | partially-fixed | remediation PATCH-09 open 7e1f260a804dfb7896a970c342274d45c2defa24 https://github.com/MaineCyberTech/chat/pull/64 |
| FINAL-P1-001 | P1 | Systemic Supabase client/role mismatch |  |  | partially-fixed | Draft PR #59 commit 9bd4f88: webhooks+push use service-role client, socket builds per-user client from JWT; FEAT-P1-002 durable BullMQ retries deferred to PATCH-09 |
| FINAL-P1-002 | P1 | Deploy pipeline mutates schema/policies/data outside migrations |  |  | partially-fixed | remediation PS-U07 open f4bcb403785130f14d73e644996266226af25add https://github.com/MaineCyberTech/chat/pull/70 |
| OBS-P1-001 | P1 | No alerting is wired despite metrics and a TODO |  |  | partially-fixed | remediation PATCH-12 open d458b82e1a6ba11dd87b91b07d60aa7c53396f28 https://github.com/MaineCyberTech/chat/pull/66 |
| SEC-P1-002 | P1 | Tracked credential file `test-signin.json` |  |  | partially-fixed | removed+ignored credential; rotation required out-of-band |
| SEC-P1-003 | P1 | Admin `/v1/admin/users` returns all platform users (including email) to any workspace admin |  |  | partially-fixed | draft PR #58 commit c41aa79; SEC-P1-004/005/006 fixed too but not mapped in remediation_plan.json |
| SEC-P1-004 | P1 | Admin `/v1/admin/audit-logs` leaks other tenants' logs when `workspaceId` omitted |  |  | partially-fixed |  |
| SEC-P1-005 | P1 | Admin compliance exports are not tenant-scoped on list/download |  |  | partially-fixed |  |
| SEC-P1-006 | P1 | Bulk import endpoints operate globally with only "admin of anything" authorization |  |  | partially-fixed |  |
| SEC-P1-007 | P1 | SSH is open to the internet by default |  |  | partially-fixed |  |
| SEC-P1-008 | P1 | Webhook secrets are optional and signature can be omitted |  |  | partially-fixed | remediation PS-U11 open 52588c328c4a8521ff155ce0882733c9e7ceb95f https://github.com/MaineCyberTech/chat/pull/67 |
| SUPPLY-P1-001 | P1 | Credential committed to the repository |  |  | partially-fixed | removed+ignored credential; rotation required out-of-band |
| TEST-P1-001 | P1 | E2E tests skip without `test-signin.json` and are non-blocking |  |  | partially-fixed | remediation PATCH-07 open 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2 https://github.com/MaineCyberTech/chat/pull/63 |
| API-P2-002 | P2 | Inconsistent error response shapes in parts of the API |  |  | open |  |
| API-P2-003 | P2 | User input interpolated into PostgREST filters (`.or(...)`) |  |  | partially-fixed | remediation PS-U01 open 43ad5e62db6ce224c696cf4c24c7887333ae41c5 https://github.com/MaineCyberTech/chat/pull/72 |
| API-P2-004 | P2 | `PATCH /v1/auth/status` accepts unvalidated `customStatus` |  |  | open |  |
| ARCH-P2-003 | P2 | Single-node, no-high-availability topology |  |  | partially-fixed | remediation PS-U02 open 5dbe6652c1039f3d0b0bb518fef45ae2eca64c0d https://github.com/MaineCyberTech/chat/pull/73 |
| ARCH-P2-004 | P2 | Worker `/metrics` and health endpoints are unauthenticated |  |  | partially-fixed | remediation PS-U02 open 5dbe6652c1039f3d0b0bb518fef45ae2eca64c0d https://github.com/MaineCyberTech/chat/pull/73 |
| CI-P2-005 | P2 | Migration validation and order checks are non-blocking |  |  | open |  |
| CI-P2-006 | P2 | `build-push` pushes images on pull requests |  |  | partially-fixed | remediation PS-U03 open 8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3 https://github.com/MaineCyberTech/chat/pull/68 |
| CI-P2-007 | P2 | Branch-protection check cannot fail the build and uses an outdated API shape |  |  | partially-fixed | remediation PS-U03 open 8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3 https://github.com/MaineCyberTech/chat/pull/68 |
| DATA-P2-003 | P2 | Duplicate `add_user_groups` migrations |  |  | open |  |
| DATA-P2-004 | P2 | Rollback scripts are only proven to exist, never executed |  |  | open |  |
| DATA-P2-005 | P2 | `gdpr_delete_user` is a hard multi-table delete with partial coverage and coupled auth deletion |  |  | partially-fixed | remediation PS-U04 open 937b43983fd3efc836f19af8407e4f06e8fcfbc2 https://github.com/MaineCyberTech/chat/pull/74 |
| EXEC-P2-002 | P2 | Documentation materially overstates readiness |  |  | partially-fixed | remediation PS-U05 open 82f8eaa2c8525febd24f6fbaa7c0ef93de28de82 https://github.com/MaineCyberTech/chat/pull/71 |
| FEAT-P2-003 | P2 | Webhook idempotency key is regenerated per attempt |  |  | partially-fixed | remediation PS-U06 open 92ef54074256aec75e3858f3339a28c21a980d4e https://github.com/MaineCyberTech/chat/pull/69 |
| FEAT-P2-004 | P2 | Naive input sanitizer blocks legitimate content |  |  | open |  |
| FINAL-P2-003 | P2 | Release confidence limited by advisory gates |  |  | partially-fixed | remediation PATCH-07 open 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2 https://github.com/MaineCyberTech/chat/pull/63 |
| HYG-P2-001 | P2 | Generated outputs and audit artifacts committed |  |  | open |  |
| HYG-P2-002 | P2 | One-off remediation scripts and duplicated logic/schema remain |  |  | partially-fixed | remediation PS-U08 open cc41daee2b2e7d8bc4b27beafafe43ad59708a7b https://github.com/MaineCyberTech/chat/pull/75 |
| INV-P2-001 | P2 | Committed audit/generated artifacts bloat the repository |  |  | open |  |
| INV-P2-002 | P2 | Credential file `test-signin.json` is tracked |  |  | partially-fixed | removed+ignored credential; rotation required out-of-band |
| INV-P2-003 | P2 | Documentation self-contradicts repository state |  |  | partially-fixed | remediation PS-U09 open 3a46f2f8c3ab723d3f07402e1559bca9094e21a1 https://github.com/MaineCyberTech/chat/pull/76 |
| OBS-P2-002 | P2 | `/metrics` authorization is weak and label cardinality is risky |  |  | partially-fixed | remediation PATCH-08 open 9feae529cc04e0f53e87abb1539b7307dbf62dbf https://github.com/MaineCyberTech/chat/pull/65 |
| OBS-P2-003 | P2 | Error tracking is optional and admin log buffer is in-memory only |  |  | partially-fixed | remediation PATCH-12 open d458b82e1a6ba11dd87b91b07d60aa7c53396f28 https://github.com/MaineCyberTech/chat/pull/66 |
| OBS-P2-004 | P2 | No distributed tracing / correlation to a collector |  |  | partially-fixed | remediation PS-U10 open fdadf5941c86b0b27182c8289e4812300455e7ce https://github.com/MaineCyberTech/chat/pull/77 |
| SEC-P2-009 | P2 | `timingSafeEqual` can throw on length mismatch (unhandled 500) in CSRF middleware |  |  | partially-fixed | remediation PS-U11 open 52588c328c4a8521ff155ce0882733c9e7ceb95f https://github.com/MaineCyberTech/chat/pull/67 |
| SEC-P2-010 | P2 | Socket typing/leave events can be sent to arbitrary channel rooms |  |  | partially-fixed | remediation PS-U11 open 52588c328c4a8521ff155ce0882733c9e7ceb95f https://github.com/MaineCyberTech/chat/pull/67 |
| SUPPLY-P2-002 | P2 | GitHub Actions are not pinned to commit SHAs |  |  | open |  |
| SUPPLY-P2-003 | P2 | Dependency vulnerability scanning is advisory-only |  |  | partially-fixed | remediation PS-U12 open a202fad83cd2fceb244dc6e815d76da7d8cb9978 https://github.com/MaineCyberTech/chat/pull/78 |
| SUPPLY-P2-004 | P2 | SBOM is generated only for develop and not for production artifacts |  |  | open |  |
| TEST-P2-002 | P2 | Low coverage thresholds and non-blocking diff coverage |  |  | partially-fixed | remediation PS-U13 open fe04ab3a01cd04ff3dcc8c9a4cce6153c0340f9b https://github.com/MaineCyberTech/chat/pull/79 |
| TEST-P2-003 | P2 | No real-database/RLS integration test tier |  |  | open |  |
| TEST-P2-004 | P2 | Migration rollback is validated by file existence only |  |  | open |  |
| API-P3-005 | P3 | OpenAPI spec coverage/consistency needs verification |  |  | partially-fixed | remediation PS-U01 open 43ad5e62db6ce224c696cf4c24c7887333ae41c5 https://github.com/MaineCyberTech/chat/pull/72 |
| ARCH-P3-005 | P3 | Duplicated `requireAdmin` implementations |  |  | open |  |
| HYG-P3-003 | P3 | Unresolved TODO in operational metrics |  |  | partially-fixed | remediation PS-U08 open cc41daee2b2e7d8bc4b27beafafe43ad59708a7b https://github.com/MaineCyberTech/chat/pull/75 |
| HYG-P3-004 | P3 | Encoding artifacts and inconsistent comments |  |  | partially-fixed | remediation PS-U08 open cc41daee2b2e7d8bc4b27beafafe43ad59708a7b https://github.com/MaineCyberTech/chat/pull/75 |
| INV-P3-001 | P3 | Character-encoding (mojibake) artifacts in docs and config |  |  | open |  |
| INV-P3-002 | P3 | Overlapping and inconsistent environment example files |  |  | partially-fixed | remediation PS-U09 open 3a46f2f8c3ab723d3f07402e1559bca9094e21a1 https://github.com/MaineCyberTech/chat/pull/76 |
| SUPPLY-P3-005 | P3 | Large binary archives committed to the repo |  |  | open |  |
