# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PATCH-003` — make Turnstile mandatory in production, covering `SEC-P2-002` (P2).
Previously `verifyCaptcha()` returned `true` whenever `TURNSTILE_SECRET_KEY` was unset, and
`POST /api/v1/public/submit` only required a token when the secret happened to be configured.
A deployment that forgot the secret therefore silently disabled the anti-bot control on the
public lead endpoints, which write rows and fan out to Teams/JSM (ticket spam).

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d` (findings at `fix/p2-batch-31 @ 2295958d`)
- Patch set: `PATCH-003` — Require Turnstile in production
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)

> Base note: the audit branch was force-updated after the audit; per runner instructions this PR
> is based on the current `origin/fix/p2-batch-31` (`11746adc`). The two patch-set source files
> are unchanged from the audited commit apart from an unrelated `M365` comment in `env.ts`, so the
> finding still reproduces on this base (unset secret ⇒ `verifyCaptcha` returns `true`).

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-002` | P2 | open -> fixed (pending review) | `TURNSTILE_SECRET_KEY` is now required at boot in production, and `/submit`/`verifyCaptcha` fail closed instead of skipping the check. |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/config/env.ts` | New `assertProductionTurnstile()` (called from `getEnv()`): when `NODE_ENV=production`, a missing `TURNSTILE_SECRET_KEY` throws at boot, so the public lead endpoints can never run with CAPTCHA disabled. |
| `apps/api/src/routes/public.ts` | `verifyCaptcha()` returns `false` (not `true`) when no secret is configured. `/submit` requires a verified token when the secret is set **or** when running in production, closing the omit-the-field bypass. |
| `apps/api/src/__tests__/env-turnstile.test.ts` | New unit tests for the production boot assertion (configured, missing, non-prod unchanged). Uses a distinct filename from `env.test.ts` to avoid an add/add conflict with the sibling PATCH-002 PR. |
| `apps/api/src/__tests__/public.test.ts` | Tests that `/submit` returns 400 in production without a token, fails closed with a token when no secret exists, and requires a token when Turnstile is configured. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | Proxmox ci-runner | 0 | `remediation/PATCH-003/verify.log` |
| `corepack pnpm --filter api typecheck` | Proxmox ci-runner (tsc --noEmit) | 0 | `remediation/PATCH-003/verify.log` |
| `corepack pnpm --filter api test` | Proxmox ci-runner (jest 29) | 0 | `remediation/PATCH-003/verify.log` — 123 suites passed, 1412 tests passed |
| `gitleaks detect --no-git --redact` (changed files) | `zricethezav/gitleaks:latest` (docker) | 0 | `remediation/PATCH-003/verify.log` — `no leaks found` |

- Secret scan (gitleaks): **pass** — no leaks found across the four changed files.
- Scope check: **pass** — only the two patch-set files plus their tests were touched.
- Fail-then-pass is covered by the new tests: at base, `verifyCaptcha` returned `true` with no
  secret and `/submit` accepted a token-less request in production; the new assertions fail
  without the fix and pass with it.

## Evidence bundle

- `remediation/PATCH-003/diff.patch` — SHA-256 `7e795942beb6e154167e2c49ef25794a5ea7346cc136d8d96d43649fb5d80bba`
- `remediation/PATCH-003/manifest.json`
- `remediation/PATCH-003/verify.log`

## Risk and rollback

- Risk: **low, but operationally visible.** The change is fail-closed. If `TURNSTILE_SECRET_KEY`
  is not present in the production secret store, the API will now refuse to start rather than
  degrade. That is the intended fix, but it must be coordinated with Turnstile secret provisioning
  and the client-side widget before deploy.
- Rollback: `git revert 26ea6043` (or drop the branch).

## Open questions / follow-ups (out of scope)

- Is `TURNSTILE_SECRET_KEY` currently set in the production environment? If not, it must be
  provisioned before this ships or startup will fail by design.
- The web client must send `captchaToken` on `/submit`; if the widget is not yet wired, enabling
  this in production will reject legitimate submissions. Verify the client integration first.

## Review checklist

- [x] Diff touches only the patch-set files (+ tests)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran in the lab; results pasted, not asserted
- [x] No secrets added; gitleaks clean
- [x] Tests added/updated for the fix
- [x] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md`: in `NODE_ENV==="production"` require `TURNSTILE_SECRET_KEY`; `verifyCaptcha`
returns `false` (fail closed) when called with no secret. Validation: `pnpm --filter=api test`.
