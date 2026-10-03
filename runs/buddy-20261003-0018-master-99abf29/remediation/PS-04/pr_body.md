# Remediation PR — PS-04 Save integrity

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Makes buddy's local save layer trustworthy. Previously `loadGame` silently rewrote every
save to `version: 1` while three writers persisted `version: 2` and autosave persisted `1`;
nothing validated save shape at runtime. This PR makes `SAVE_VERSION = 2` the single source of
truth, adds a versioned migration registry, and validates all loaded/imported saves with zod.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-04` — Save integrity
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P1-001` | P1 | open -> fixed | Removed the `version = 1` downgrade; `SAVE_VERSION` used by autosave. |
| `DATA-P1-002` | P1 | open -> fixed | zod validation of loaded saves; malformed data fails closed. |
| `DATA-P2-001` | P2 | open -> fixed | Versioned migration registry (`v1 -> v2`) applied on load/import. |
| `SEC-P2-001` | P2 | open -> fixed | Import decodes, validates (incl. size cap) before persisting. |

## Changes

| File | What changed |
|---|---|
| `lib/storage/schema.ts` (new) | `SAVE_VERSION = 2`, zod schemas for `GameSave`/`BuddyState`/`InventoryState`/`ProgressionState`, numeric clamping, and a versioned migration registry exposed via `validateSave()`. |
| `lib/storage/indexeddb.ts` | `loadGame` migrates + validates instead of force-setting `version = 1`; `importSave` validates the decoded payload and enforces a size cap; `getSaveMetadata` now reports the real version. |
| `lib/storage/autosave.ts` | Writes `SAVE_VERSION` instead of the stale literal `1`. |
| `lib/storage/schema.test.ts` (new) | Migration fixtures (v1/v2), malformed/unknown-mood rejection, clamping, oversized-inventory rejection, and valid import round-trip. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`) | 0 | `remediation/PS-04/verify.log` — 6 files / 121 tests passed |
| `npm run test -- storage` | local (node v24.19.0) | 0 | `remediation/PS-04/verify.log` — 12 tests passed |
| `npm run test` | local (node v24.19.0) | 0 | `remediation/PS-04/verify.log` — 121 tests passed |
| `npm run lint` | local (node v24.19.0) | 0 | `remediation/PS-04/verify.log` — no warnings/errors |
| `npm run typecheck` | local (node v24.19.0) | 2 | PRE-EXISTING baseline error in `lib/progression/lifecycle.test.ts` (TS2802); reproduced on base with changes stashed. Not caused by PS-04. |
| `gitleaks detect --no-git --redact --source .` | lab: `ci-runner` | 0 | no leaks found (`remediation/PS-04/verify.log`) |

- Secret scan (gitleaks): pass, exit 0, no leaks found.
- Scope check (files within patch set): pass — only `lib/storage/{indexeddb,autosave}.ts`,
  new `lib/storage/schema.ts`, plus the required new test file.

## Evidence bundle

- `remediation/PS-04/diff.patch` — SHA-256 `2373a6c092a83084f3a7dbe5a7f6c3e002e3ac47d7c4ee3e0d7683559a4e091f`
- `remediation/PS-04/manifest.json`
- `remediation/PS-04/verify.log`

## Risk and rollback

- Risk: **medium-low**. Save validation now fails closed: an invalid/corrupt save loads as
  `null` and the app routes the player to hatch instead of crashing. Numeric drift is clamped
  rather than rejected. Migration covers the only known prior version (v1).
- Rollback: `git revert ec824fc`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

Migration fixtures + fuzz/malformed-import tests pass (`npm run test -- storage`).
