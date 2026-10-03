# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PATCH-002` — fail closed when PII field encryption is not configured in
production, covering `SEC-P1-001` (P1). Previously `FIELD_ENCRYPTION_KEY` was optional in the
env schema, and `lib/field-encryption.ts` returned a reversible `` `plain:<value>` `` transform
whenever the key was missing or not 32 bytes. A production deployment with a missing/mis-sized
key would therefore silently store profile PII in cleartext, tagged in a way that looks safe at
rest.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d` (findings at `fix/p2-batch-31 @ 2295958d`)
- Patch set: `PATCH-002` — Fail closed on PII encryption in production
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)

> Base note: the audit branch was force-updated after the audit; per runner instructions this PR
> is based on the current `origin/fix/p2-batch-31` (`11746adc`). The two patch-set source files
> are unchanged from the audited commit apart from an unrelated M365 comment in `env.ts`, so the
> finding still reproduces on this base.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-001` | P1 | open -> fixed (pending review) | Production now refuses to boot without a valid 32-byte `FIELD_ENCRYPTION_KEY`, and `encryptField` throws instead of writing `plain:` in production. |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/config/env.ts` | New `assertProductionSecrets()` (called from `getEnv()`): when `NODE_ENV=production`, a missing or malformed `FIELD_ENCRYPTION_KEY` (must decode to 32 bytes, 64-char hex or base64) throws at boot. |
| `apps/api/src/lib/field-encryption.ts` | `encryptField` throws in production when the key is absent/wrong length instead of returning `` `plain:` ``. Legacy `` `plain:` `` values are still read, but now emit a `pii_legacy_plaintext` warn counter and are never silently rewritten. |
| `apps/api/src/__tests__/env.test.ts` | New unit tests for the production boot assertion (missing key, wrong length, valid hex, valid base64, non-prod unchanged). |
| `apps/api/src/__tests__/field-encryption.test.ts` | Tests that `encryptField` throws in production (absent and wrong-length key), still encrypts with a valid key, keeps the dev/test fallback, and reads legacy `` `plain:` `` values. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | Proxmox ci-runner | 0 | `remediation/PATCH-002/verify.log` |
| `corepack pnpm --filter api typecheck` | Proxmox ci-runner (tsc --noEmit) | 0 | `remediation/PATCH-002/verify.log` |
| `corepack pnpm --filter api test` | Proxmox ci-runner (jest 29) | 0 | `remediation/PATCH-002/verify.log` — 123 suites passed, 1416 tests passed |
| `gitleaks detect --no-git --redact` (changed files) | `zricethezav/gitleaks:latest` (docker) | 0 | `remediation/PATCH-002/verify.log` — `no leaks found` |

- Secret scan (gitleaks): **pass** — no leaks found on the four changed files.
- Scope check: **pass** — only the two patch-set files plus their tests were touched.
- Fail-then-pass on production refusal is covered by the new unit tests (they fail without the
  `encryptField`/`assertProductionSecrets` change).

## Evidence bundle

- `remediation/PATCH-002/diff.patch` — SHA-256 `82ada4b7ec964d1e27fb640ce1cd9314a59e061cc20774fe8723e10202bbb66f`
- `remediation/PATCH-002/manifest.json`
- `remediation/PATCH-002/verify.log`

## Risk and rollback

- Risk: **low, but operationally visible.** The change is fail-closed. If `FIELD_ENCRYPTION_KEY`
  is not present (valid) in the production secret store, the API will now refuse to start rather
  than degrade. That is the intended fix, but it must be coordinated with secret provisioning
  before deploy.
- Rollback: `git revert 42c76bf` (or drop the branch).

## Open questions / follow-ups (out of scope)

- Is `FIELD_ENCRYPTION_KEY` currently set in the production environment? If not, it must be
  provisioned before this ships or startup will fail by design.
- Existing rows previously written with the `` `plain:` `` prefix are not migrated here. They now
  log a `pii_legacy_plaintext` counter; a backfill/re-encrypt migration is a separate follow-up.

## Review checklist

- [x] Diff touches only the patch-set files (+ tests)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran in the lab; results pasted, not asserted
- [x] No secrets added; gitleaks clean
- [x] Tests added/updated for the fix
- [x] Rollback is practical
