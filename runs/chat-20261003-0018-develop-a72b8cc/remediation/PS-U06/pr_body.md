# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the unassigned feature finding `FEAT-P1-001` in the catch-all set `PS-U06`. The
patch set also lists `FEAT-P2-003`, which is already implemented by `PATCH-09` (draft
PR #64); it is **not duplicated here**.

- **FEAT-P1-001** — `POST /v1/auth/magic-link` validated the email and then returned
  `{ success: true }` without ever asking Supabase to send anything, so callers believed a
  mail had gone out. `AuthService.sendMagicLink` now calls the server-side Supabase
  `auth.signInWithOtp({ shouldCreateUser: false, emailRedirectTo: <FRONTEND_URL>/auth/callback })`.
  Delivery and unknown-account errors are logged but never surfaced, so the endpoint keeps a
  neutral response and cannot be used to enumerate accounts.
- **FEAT-P2-003** (webhook idempotency key regenerated per attempt) — **covered elsewhere**:
  PR #64 adds a stable per-delivery key carried on the durable BullMQ retry job. Re-implementing
  it here would duplicate that change. Recorded for traceability only; it stays `partially-fixed`
  until #64 merges.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U06` — Unassigned FEAT findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P1-001` | P1 | open -> partially-fixed | Magic link is now sent server-side via Supabase `signInWithOtp`; the route still returns a neutral success. |
| `FEAT-P2-003` | P2 | open -> deferred | Already implemented by `PATCH-09` (draft PR #64). Not duplicated in this PR; closes when #64 merges. |

Status advances to `verified-fixed` on merge (FEAT-P1-001) / when #64 merges (FEAT-P2-003).

## Changes

| File | What changed |
|---|---|
| `apps/api/src/modules/auth/service.ts` | New `AuthService.sendMagicLink(email)` using `getSupabase().auth.signInWithOtp` with `shouldCreateUser: false` and the `FRONTEND_URL` callback; failures are logged via `logger.warn`, not thrown. Imports `getSupabase`, `loadEnv`, `logger`. |
| `apps/api/src/modules/auth/routes.ts` | `POST /magic-link` awaits `authService.sendMagicLink(parsed.data.email)` before the unchanged neutral JSON response. |
| `apps/api/src/modules/auth/__tests__/auth.service.test.ts` | Mock anon client gains `auth.signInWithOtp`; new assertions that the email + callback redirect are passed, and a new case asserting a delivery failure still returns a neutral success. |

Scope: 2 in-scope product files + 1 test file. No dependency, config, schema, or unrelated changes.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter @chat/api test` | lab `ci-runner` (172.23.128.51) | 0 | `remediation/PS-U06/verify.log` — `Lockfile is up to date`; **62 files / 486 tests passed**, including `auth.service.test.ts` (11 tests) |
| `git add <changed paths> && git diff --cached --unified=0 \| gitleaks stdin --redact --no-banner` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `scanned ~3340 bytes (3.34 KB)`; `no leaks found` |
| `corepack pnpm exec vitest run apps/api/src/modules/auth/__tests__/auth.service.test.ts` | local clone | 0 | `verify.log` — 1 file / 11 tests passed |
| `corepack pnpm --filter @chat/api lint` | local clone | 0 | `verify.log` — `eslint .` clean |
| `corepack pnpm --filter @chat/api typecheck` | local clone (workspace deps built) | 0 | `verify.log` — `tsc --noEmit` clean |

- Secret scan (gitleaks): **pass** — no leaks on the staged diff.
- Scope check (files within patch set): **pass** — auth service/routes + their test only.

## Evidence bundle

- `remediation/PS-U06/diff.patch` — SHA-256 `590C5DA323C605AD4D597CA72939636119BF9E4A3BE31619D34A16483A6F401D`
- `remediation/PS-U06/manifest.json`
- `remediation/PS-U06/verify.log`

## Risk and rollback

- Risk: **low**. The endpoint was previously a no-op; it now performs the documented action.
  The web client calls Supabase directly (`auth-context.tsx`), so its flow is unchanged. The
  new call only runs when someone calls the API route, is already rate-limited by
  `magicLinkLimiter`, and its errors are swallowed into a neutral response.
- Rollback: `git revert 92ef54074256aec75e3858f3339a28c21a980d4e` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- `POST /v1/auth/magic-link` asks Supabase to send a magic link and still returns a neutral response.
- Unknown-account / delivery errors do not leak account existence.
- API test suite, targeted test, lint, typecheck, and gitleaks are green.

## Notes / open questions

- `shouldCreateUser: false` preserves the endpoint's "sent if account exists" semantics; sign-up
  stays on the password/OAuth flows. If the product wants magic-link self-signup, flip this flag.
- `FEAT-P2-003` is intentionally deferred to `PATCH-09` / PR #64 to avoid duplicating the same fix.
