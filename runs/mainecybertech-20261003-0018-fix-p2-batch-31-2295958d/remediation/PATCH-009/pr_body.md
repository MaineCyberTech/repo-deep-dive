# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d`
- Patch set: `PATCH-009` — (P2) API-key authentication or removal
- Repo / base: `mainecybertech` @ `11746adc` (`fix/p2-batch-31`)

Closes **FEAT-P2-001**. Before this change the API could mint and list `mct_…` API keys but no
request path ever verified them: `requireAuth` only accepted HS256 JWTs or Supabase sessions, so
every `Authorization: Bearer mct_*` request was rejected 401 and the advertised
machine-credential feature was dead. This PR adds fail-closed API-key verification.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P2-001` | P2 | open -> fixed | `mct_*` keys now authenticate; revoked/expired/wrong-hash keys 401 |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/middleware/api-key.ts` (new) | `authenticateApiKey()`: indexed `key_prefix` lookup -> constant-time SHA-256 compare (`crypto.timingSafeEqual`) -> `is_active`/`expires_at` checks -> records `last_used_at` (best effort) -> returns key org/creator/permissions. Helpers `isApiKeyToken`, `apiKeyPrefix`, `hashApiKey`, `timingSafeEqualHex`. |
| `apps/api/src/middleware/auth.ts` | `requireAuth` resolves `mct_*` tokens before the JWT/Supabase paths, attaches `req.authUser` + `req.apiKey`, pins `req.orgScope`/`req.orgId` and injects the key's `organization_id` into the query so the existing `requireOrgAccess`/`requirePermission` chain still scopes the request. Caller-supplied org ids are overwritten. |
| `apps/api/src/__tests__/api-key-auth.test.ts` (new) | Valid key authenticates and is org-pinned; revoked / expired / unknown-prefix / mismatched-hash keys 401; no session-cookie fallback for `mct_` tokens. |

Design note: the key acts with the **creating user's** org permissions (the existing permission
model), pinned to the key's own organization. A key cannot be repointed at another org by passing
`?organization_id=`.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` (setup) | ci-runner (LXC 200, `172.23.128.51`) | 0 | not captured (setup) |
| `corepack pnpm --filter api typecheck && corepack pnpm --filter api test` | ci-runner (LXC 200, `172.23.128.51`) | 0 | `remediation/PATCH-009/verify.log` — 123 suites / 1413 tests passed |
| `gitleaks detect --no-git --redact` on each changed file (gitleaks 8.30.1) | ci-runner (LXC 200, `172.23.128.51`) | 0 | `remediation/PATCH-009/verify.log` — no leaks found |

- Scope check (files within patch set + tests): **pass** — `middleware/api-key.ts`,
  `middleware/auth.ts`, and the new `__tests__/api-key-auth.test.ts` only.
- ESLint on all three files (`apps/api/eslint.config.js`, `--max-warnings=0`): pass (exit 0).
- Honesty note: the route tests mock the Supabase admin client. There is no live Supabase
  provisioned by the lab `pnpm --filter api test` command, so end-to-end "real key over HTTP"
  verification was **not run**; the auth/revoked/expired branches are covered by unit tests.

## Evidence bundle

- `remediation/PATCH-009/diff.patch` — SHA-256 `93a38b1c4d55266aa741ff64e988c9516acd87fa30802b1cbafe27331399b60e`
- `remediation/PATCH-009/manifest.json`
- `remediation/PATCH-009/verify.log`

## Risk and rollback

- Risk: low-to-moderate. Adds a new authentication path; it is gated behind the `mct_` prefix, so
  existing JWT/cookie auth is unchanged. Key resolution is fail-closed (lookup, constant-time hash
  compare, active/expiry). No schema, config, or dependency change.
- Rollback: `git revert c7e2bd02d222df802b05879693118a8d8b2a4543`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions (for the reviewer)

1. `api_keys.permissions` (jsonb, defaults to `[]`) is still not enforced per-key. Because the
   create route does not let callers set it, enforcing `[]` literally would make every key inert,
   so this PR inherits the creating user's org permissions. If per-key permission narrowing is
   intended, that is a follow-up product decision (new scope + UI), not a guess made here.
2. If the creating user loses their approved membership in the key's org, `requireOrgAccess`
   will now reject the key. That is fail-closed; confirm it matches the intended lifecycle.

## Definition of done (for this set)

From `patch_plan.md` PATCH-009: implement `mct_` bearer verification (prefix lookup -> constant-time
SHA-256 compare -> active/expiry -> attach org + permissions, update `last_used_at`), or hide the
UI. Validation: key authenticates; revoked/expired 401. This PR implements the former.
