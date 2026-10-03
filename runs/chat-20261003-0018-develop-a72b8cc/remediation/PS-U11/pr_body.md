# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the three unassigned security findings in the catch-all set `PS-U11` (SEC-P1-008,
SEC-P2-009, SEC-P2-010) with minimal, targeted changes:

- **SEC-P1-008** — Webhook endpoints could be created/updated without a signing secret, so
  deliveries could be sent unsigned. Creation now requires a secret of at least 16 characters
  (enforced in the Zod body schema and in `WebhookService.validateSecret`), and the stored
  secret is always encrypted. Updates may omit the secret (the existing one is retained) but
  cannot set one shorter than 16 characters.
- **SEC-P2-009** — `crypto.timingSafeEqual` throws `RangeError` when buffers differ in length.
  Both CSRF comparison sites now compare lengths first via a `safeEqual` helper, so a crafted
  mismatched-length `x-csrf-token` returns `403 CSRF_INVALID` instead of an unhandled 500.
- **SEC-P2-010** — `channel:leave` and `typing:start`/`typing:stop` broadcast to
  `channel:<id>` without checking that the sender had joined that room. A joined-room guard
  (`isChannelRoomMember(socket.rooms, id)`) now suppresses any broadcast to a channel the
  socket never joined. Membership itself is still enforced by `channel:join` (workspace +
  private-channel checks) before `socket.join(...)`.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U11` — Unassigned SEC findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-008` | P1 | open -> partially-fixed | Secret now required (>=16 chars) on create/update; unsigned configs rejected. Existing rows created before this change are unaffected and remain a follow-up (migration/rotation). |
| `SEC-P2-009` | P2 | open -> partially-fixed | Length checked before `timingSafeEqual`; regression tests assert 403 (not throw) for mismatched lengths. |
| `SEC-P2-010` | P2 | open -> partially-fixed | Joined-room guard on leave/typing broadcasts; unit test covers the room-membership predicate. |

Status advances to `verified-fixed` on merge.

## Changes

| File | What changed |
|---|---|
| `apps/api/src/modules/webhooks/service.ts` | `validateSecret` rejects empty/short secrets with a clear message; `create` requires `secret: string` and always encrypts it. |
| `apps/api/src/modules/webhooks/routes.ts` | `createWebhookSchema.secret` is now required with `min(16)`; `updateWebhookSchema.secret` uses `min(16)` when present. |
| `apps/api/src/middleware/csrf.ts` | New `safeEqual()` length-first constant-time compare used by `csrfProtection` and `doubleSubmitCookieCsrf`. |
| `apps/api/src/lib/socket.ts` | New exported `isChannelRoomMember()`; joined-room guard added to `channel:leave`, `typing:start`, `typing:stop`. |
| `apps/api/src/middleware/__tests__/csrf.test.ts` | Mock `timingSafeEqual` now throws on length mismatch (faithful to Node); two regression tests assert 403 instead of a throw. |
| `apps/api/src/modules/webhooks/__tests__/webhook.service.test.ts` | Create test supplies a valid secret; new tests reject missing and too-short secrets. |
| `apps/api/src/lib/__tests__/socket.test.ts` | New unit tests for `isChannelRoomMember`. |

Scope: 4 in-scope product files + 3 test files. No dependency, config, or unrelated changes.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter api test` | lab `ci-runner` (172.23.128.51) | 0 | `remediation/PS-U11/verify.log` — 63 files, **492 tests passed**; includes `csrf.test.ts` (22), `webhook.service.test.ts` (14), `socket.test.ts` (3) |
| `corepack pnpm --filter @chat/api test` | lab `ci-runner` | 0 | `verify.log` — 63 files, 492 tests passed (same suites isolated) |
| `git diff --cached --unified=0 \| gitleaks stdin --redact --no-banner` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` — `no leaks found` (7,887 bytes scanned) |
| `corepack pnpm --filter @chat/api lint` | lab `ci-runner` | 0 | `verify.log` — `eslint .` clean |
| `corepack pnpm --filter @chat/api typecheck` | lab `ci-runner` | 2 | Pre-existing: all 15 errors are `TS2307` "cannot find module `@chat/db`/`@chat/config/*`" in files **not touched** by this diff (workspace packages are not built before per-package `tsc`). A `git stash -u` baseline produced the identical error set; the one error this change introduced (`TS2352` in the webhook test) was fixed and is absent. |

- Secret scan (gitleaks): **pass** — no leaks on the changed paths / staged diff.
- Scope check (files within patch set): **pass** — only the webhook service/routes, CSRF
  middleware, socket lib, plus the three test files.

### Note on `--filter api`

The required command uses `--filter api`, which matches no workspace package, so pnpm scopes
all 8 projects (`Scope: all 8 workspace projects`). The `@chat/api` suites do run in that pass
(confirmed by name in the log), and the targeted `--filter @chat/api test` run isolates them.

## Evidence bundle

- `remediation/PS-U11/diff.patch` — SHA-256 `090ADA3EAC398495FF520D20C7B9C4AFF3304F2718C85F62574AE7D26466B424`
- `remediation/PS-U11/manifest.json`
- `remediation/PS-U11/verify.log`

## Risk and rollback

- Risk: **low**. SEC-P1-008 is a tightening of input validation; clients that already send a
  secret are unaffected. SEC-P2-009 only changes an error path from 500 to 403. SEC-P2-010
  only suppresses broadcasts for sockets that were never in the room (legitimate clients always
  join first). No schema, data, dependency, or config changes.
- Rollback: `git revert 52588c328c4a8521ff155ce0882733c9e7ceb95f`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- `corepack pnpm install --frozen-lockfile && corepack pnpm --filter api test` passes.
- Creating a webhook without a valid secret is rejected; a length-mismatched CSRF token yields
  403; typing/leave to a non-joined channel produces no broadcast.

## Follow-ups (not in this patch set)

- A migration/backfill (or hard DB constraint) to force existing `webhook_endpoints.secret`
  rows and drop the `default ''` column default — SEC-P1-008's pre-existing rows.
- SEC-P2-010's recommended per-event membership re-validation via a user-scoped Supabase
  client (the joined-room guard covers the reported cross-room broadcast; a full re-check is a
  larger change).
