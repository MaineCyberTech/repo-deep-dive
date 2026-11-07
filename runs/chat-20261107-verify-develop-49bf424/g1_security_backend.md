# G1 — Security & Backend Verification

- Repo: `MaineCyberTech/chat`
- Commit: `develop@49bf4243ae02a9cd5c6ca090417d12c3696429ea` (2026-11-07)
- Previous run: `chat-20261004-full-develop-a62e44a`
- Mode: read-only source verification; no live DB, bucket, Supabase, or lab access. Findings that depend on deployed state are marked as such.
- Output: `g1_security_backend.json`, this file.

## Counts

| Set | P1 | P2 | P3 | Total |
|---|---:|---:|---:|---:|
| Re-verified IDs | 0 | 11 | 8 | 19 |
| New findings | 1 | 5 | 2 | 8 |
| **All** | **1** | **16** | **10** | **27** |

Re-verified status breakdown:

| Status | Count |
|---|---:|
| verified-fixed | 2 |
| partially-fixed | 8 |
| open | 8 |
| owner-accepted | 1 |
| regressed | 0 |

## Re-verified findings

| ID | Sev | Status | Evidence (current code) | Residual / remediation |
|---|---|---|---|---|
| SEC-P2-001 | P2 | verified-fixed | `infra/docker/docker-compose.prod.yml:58-60,132-134`; `infra/docker/.env.prod.example:29-33`; `.env.example`; `apps/api/src/modules/webhooks/service.ts:21-27` | Key now delivered to api+worker. Stale `docs/environments/env-vars.md:88-94` still says it is not; update docs. |
| SEC-P2-002 | P2 | partially-fixed | `packages/config/webhook-utils.ts:92`; `apps/api/src/modules/webhooks/service.ts:253`; `apps/worker/src/processors/webhook-delivery.ts:104`; residual `webhook-utils.ts:31-57` | Redirects no longer followed. Still no IP pinning: `0.0.0.0`, `100.64/10`, `fd00::/8`, IPv4-mapped IPv6 pass; `resolve4` only; validation and fetch are separate DNS lookups (service `:228`/`:246`). |
| WH-P2-002 | P2 | partially-fixed | Same code path as SEC-P2-002 (`webhook-utils.ts:92`, service `:253`, worker `:104`) | Same residual: DNS rebinding/IPv6 SSRF. Implement IP-pinned dispatch and A+AAAA checks. |
| CHAIN-P2-001 | P2 | partially-fixed | Key delivery `docker-compose.prod.yml:58-60,132-134`; redirect guard `webhook-utils.ts:92`; residual `webhook-utils.ts:31-57`, service `:246` | Encryption-key half fixed and redirect hop closed. Chain survives only as an SSRF bypass (SEC-P2-002); fix that to close. |
| CHAIN-P3-001 | P3 | open | `apps/api/src/modules/messages/routes.ts:486-500`; `apps/api/src/validators/upload.ts:55-66`; `apps/web/components/chat/chat-view.tsx:527-535`; `supabase/config.toml:122-132` | Public URL + metadata-only type check. Use private bucket, magic-byte sniff, signed downloads. |
| FILE-P2-001 | P2 | open | `messages/routes.ts:474-501` (`getPublicUrl` at `:500`; signed URL `:489-491`); `validators/upload.ts:55-67` (optional `fileSize` at `:66`, never used); bucket undefined (`config.toml:122-132`) | No byte sniff; declared type/size not enforced; bucket visibility unverified. Sniff bytes, enforce size, return signed URLs, track bucket policy. |
| FILE-P3-001 | P3 | open | No quota code; `apps/api/src/validators/upload.ts:3,66` (optional client 10MB); `supabase/config.toml:125` (global 50MiB) | Add per-user/workspace storage accounting + quota before issuing upload URLs. Note: current cleanup is not a quota and is destructive (FILE-P1-001). |
| DATA-P2-001 | P2 | owner-accepted | `supabase/migrations/README.md:8-25`; `supabase/migrations/migrations.list:44,48`; permissive policies `20260705000003_add_user_groups.sql:12-21` | Documented as intentional/immutable applied history. Do not squash; address policy ambiguity via new migration (DATA-P2-003). |
| DATA-P2-002 | P2 | partially-fixed | `supabase/migrations/20260725000001_make_gdpr_delete_atomic.sql:48-104` (atomic, auth rows at `:100-104`); no `storage` deletion; `apps/api/src/modules/auth/routes.ts:338-354` | DB-row coverage is now broad and atomic. Residual: hard delete only, no storage-object cleanup, no retention/legal-hold matrix. |
| PRIV-P2-001 | P2 | partially-fixed | Same as DATA-P2-002: `20260725000001_make_gdpr_delete_atomic.sql:48-104`, comment `:25-44` | Erasure does not remove avatars/uploads; no documented retention matrix. Extend erasure + test storage objects. |
| PRIV-P3-001 | P3 | verified-fixed | `apps/worker/src/scheduler.ts:31-48,127-159`; `apps/worker/src/main.ts:96`; `apps/worker/src/processors/data-retention.ts:31-60,236-284` | Prior run was a false negative: retention scheduler existed at a62e44a and still runs. Add a run metric if proof-of-execution is needed. |
| MT-P3-001 | P3 | open | `apps/api/src/modules/admin/routes.ts:59-68` (users `:61`, messages `:67` unscoped) | Scope counts to admin workspace ids or gate global counts as platform-admin-only. |
| ACM-P2-001 | P2 | partially-fixed | Matrix exists: `packages/db/src/permissions.ts:3-82`; middleware `apps/api/src/middleware/require-permission.ts:13-36`; but unused by routes; registry `apps/api/src/route-registry.ts:46-114` annotates only health/auth/workspaces (`:51,:57-70,:76-89`) | Matrix is not wired to routes and there are no per-role negative tests. Apply requirePermission, annotate all registry entries, generate matrix, add tests. |
| ACM-P3-001 | P3 | open | `apps/api/src/modules/admin/routes.ts:61,67` | Same as MT-P3-001: users/messages counts are global. |
| ADMIN-P3-001 | P3 | partially-fixed | `apps/api/src/modules/admin/error-buffer.ts:16-27,34-60`; `apps/api/src/server.ts:22`; no `ERROR_LOG_FILE`/volume in `infra/docker/docker-compose.prod.yml` | Optional durable NDJSON exists, but production does not enable it, so `/admin/logs` is still restart-volatile. |
| AI-P2-001 | P2 | open | `apps/api/src/modules/ai/routes.ts:5-20` | Still a local string-rewrite stub; no rate limit, input cap, tenancy/data-governance or cost contract. Define before adding a provider. |
| SEARCH-P3-001 | P3 | open | `supabase/migrations/20260625000005_create_search.sql:18-46`; `20260627000003_enhanced_search.sql:18-46`; `apps/api/src/modules/messages/routes.ts:39-76`; no docs statement | Search is in-DB and tenant-scoped, but no documented data-flow/retention statement for queries/index. |
| NOTIF-P2-001 | P2 | partially-fixed | Durable worker exists: `apps/worker/src/processors/notification.ts:17-25,275-300`; API path still direct: `apps/api/src/modules/notifications/service.ts:78-112`; prod compose passes no VAPID/SMTP | Worker queue is not used by the API, so no durable multi-channel delivery in production; no delivery log. Wire the API to the queue and configure channels. |
| NOTIF-P3-001 | P3 | open | 404/410 pruning: `push-subscription-service.ts:161-164`; worker `notification.ts:106-108`; no push metric in `apps/api/src/lib/metrics.ts` | Pruning exists but no metrics/alerts for stale endpoints or delivery failures. |

## New findings

| ID | Sev | Title | Evidence | Remediation |
|---|---|---|---|---|
| FILE-P1-001 | P1 | Scheduled `expired_uploads` cleanup deletes every `chat-uploads` object older than 7 days, including attachments and avatars | `apps/worker/src/scheduler.ts:45,141-147,177-185`; `apps/worker/src/processors/cleanup.ts:162-179`; uploads `messages/routes.ts:487-500`; avatars `auth/routes.ts:120-121`; content embed `chat-view.tsx:527-535` | Delete only confirmed orphans (reference-aware), not by age; disable schedule until fixed; add retention test. |
| WH-P2-003 | P2 | Any workspace member can manage webhooks and receive all message content (incl. private channels) | API membership-only: `webhooks/routes.ts:55-70,167-182`; matrix grants webhook perms only to admin/owner: `packages/db/src/permissions.ts:23-64`; RLS says admin-only: `20260625000012_create_webhooks.sql:34-52`; service-role bypass: `webhooks/service.ts:93-97,183-199`; payload content `messages/service.ts:103-114` | Require admin/owner on webhook mutations; align API with RLS; add member-role negative test. |
| ADMIN-P2-002 | P2 | Compliance export authorizes target workspace by membership, not admin role | `admin/routes.ts:23` (admin anywhere), `:39-48` (membership only), `:514-526` (export); correct pattern at `:487-495` | Check `workspaceIds.includes(workspaceId)` or require admin/owner in target workspace; test admin-elsewhere/member-target. |
| DATA-P2-003 | P2 | `user_groups` INSERT/UPDATE RLS omits workspace membership, allowing cross-tenant groups | `20260705000003_add_user_groups.sql:12-21`; OR-ed with `20260704000007_add_user_groups.sql:33-34`; API check bypassable via PostgREST `user-groups/routes.ts:50-61` | Forward migration adding workspace membership check to INSERT/UPDATE policies; RLS test. |
| PRIV-P2-002 | P2 | Account deletion unusable: API requires password, UI sends none, magic-link users have no password | `auth/routes.ts:317-336`; UI `settings/page.tsx:86-90`; magic link `auth/service.ts:76-85` | Re-auth via recent session/OTP or accept password from UI + set-password for magic-link users; E2E deletion test. |
| SEC-P2-003 | P2 | Push endpoints stored unvalidated and fetched server-side (stored SSRF) | `push-subscription-service.ts:64-80,141-157`; RLS allows own insert `20260625000009_create_push_subscriptions.sql:20-22`; worker fetch `notification.ts:95-104` | Validate HTTPS/public endpoint, block private IPs, no redirects, pin IP, or restrict to known push domains; enforce on write. |
| FILE-P3-002 | P3 | Avatar upload accepts any `image/*` (incl. SVG) and uses client subtype in the storage path | `validators/upload.ts:69-74`; `auth/routes.ts:120-121,136-138`; web `avatar-upload.tsx:56-60` | Explicit image allowlist (no SVG), fixed extension map, private bucket + signed URL. |
| SEC-P3-001 | P3 | Org gitleaks ruleset is local/opt-in only; CI relies on generic Trivy secret scanning | `.pre-commit-config.yaml:12-20`; `.husky/pre-commit:1-38` (no secret scan); no gitleaks in `.github/workflows`; Trivy fs scan at `validate.yml:255-265` (generic secrets); no install docs | Add blocking gitleaks/allowlist-verifier job to CI, document `pre-commit install`; keep Trivy as backstop. |

## Recent security commits (`1a06708..49bf424`)

- `1a06708` (demo JWT replacement / CI fallback removal): verified good. No `supabase-demo` tokens remain outside `.gitleaks.toml`/fixtures, and `validate.yml:473` no longer falls back to a demo anon key. This is fail-closed.
- `214e5c8` (org gitleaks baseline + pre-commit): the commit message and stat only add `.pre-commit-config.yaml`, `scripts/check-no-dotenv.sh`, and `.gitattributes`; `.gitleaks.toml` already existed from `53139a6`. The hook is opt-in and CI does not run this ruleset; CI does run Trivy's generic secret scanner (`validate.yml:255-265`), so the gap is narrower than "no secret scanning" → SEC-P3-001. Not a regression.
- `7ad52a7` (redirect guard): verified at both API and worker; no regression found. DNS/IP pinning remains (SEC-P2-002/WH-P2-002).
- `96ade3b` (WEBHOOK_ENCRYPTION_KEY): verified delivered to api and worker; no regression.

## Regressions

None of the previously `verified-fixed` IDs in scope regressed. `SEC-P2-001` and the redirect half of `SEC-P2-002`/`WH-P2-002` are genuinely fixed. The new findings are pre-existing gaps exposed by this pass, not regressions from the recent commits.

## Top new findings

1. **FILE-P1-001 (P1)** — the worker's `expired_uploads` job deletes *all* `chat-uploads` objects older than 7 days on a 6-hour schedule, including avatars and attachments still referenced by messages. This is active data loss in normal operation.
2. **WH-P2-003 (P2)** — the API lets any workspace member create webhooks (service-role path bypasses the admin-only RLS), so a regular member can receive every message payload in the workspace, including channels they cannot read.
3. **ADMIN-P2-002 (P2)** — `/v1/admin/export/compliance` checks only membership of the target workspace; an admin of tenant A who is a plain member of tenant B can export B's full data.
4. **DATA-P2-003 (P2)** — user-group RLS allows creating/moving a group in any workspace via direct PostgREST because INSERT/UPDATE check only `created_by`.
5. **PRIV-P2-002 (P2)** — account deletion cannot succeed from the UI (password required by API, never sent) and is impossible for magic-link-only users; right-to-erasure is blocked.
6. **SEC-P2-003 (P2)** — push subscription endpoints are stored unvalidated and fetched server-side, a stored SSRF when VAPID is configured.

## Verification limits

- Source-only: no local Supabase/RLS execution, no live storage bucket inspection, no deployed compose rendering. RLS behavior was assessed from migration SQL; bucket visibility remains unknown and is noted as such.
- No dynamic exploit was attempted. All claims are reproducible from the cited files at `49bf424`.
