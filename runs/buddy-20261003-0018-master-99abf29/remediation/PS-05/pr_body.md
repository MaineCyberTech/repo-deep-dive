# Remediation PR — PS-05 Hygiene / dead code

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Removes dead/duplicated code and fixes a content label, per the hygiene and architecture findings
of the audit run. The dead `autosave` module (which carried a duplicate `Math.random()` guest-id
generator and had no callers) is deleted, and `lib/generation/rng.ts` now uses the single canonical
`hashString` from `lib/generation/hash.ts` so pet generation/RNG seeding cannot drift. A
cross-module determinism regression test locks that in.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-05` — Hygiene / dead code
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Branch: `remediation/ps-05-20261003-0018-master-99abf29`
- Commit: `742c3d335ce14826eb6147952899f43e922c7f21`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P2-003` | P2 | open -> fixed | Dead `autosave` module removed; persistence stays action-driven in `MainDevice`. |
| `HYG-P2-001` | P2 | open -> partially-fixed | Removed `autosave` module, unused `getStageProgress` import (MainDevice), unused `DECOR_ITEMS` constant (items). Other listed symbols (achievements/lifecycle/indexeddb/hats) are out of this set's scope and remain open (PS-04/PS-06 territory). |
| `HYG-P2-002` | P2 | open -> fixed | Duplicate private `hashString` in `rng.ts` deleted; `createRNG` imports the canonical `hash.ts` implementation. Determinism tests added. |
| `HYG-P3-001` | P3 | open -> partially-fixed | Label typo fixed (` celebration Cake` -> `Celebration Cake`). Enforced format/lint in CI depends on `CI-P1-001` (PS-01) and is not in this set. |

## Changes

| File | What changed |
|---|---|
| `lib/storage/autosave.ts` (deleted) | Unused `startAutosave`/`stopAutosave` module; also removed its duplicate `Math.random()` guest-id path. |
| `lib/generation/rng.ts` | Imports `hashString` from `@/lib/generation/hash`; the private near-identical copy is deleted (HYG-P2-002). |
| `lib/generation/hash.ts` | Unchanged: confirmed as the single canonical hashing module. |
| `lib/generation/generation.test.ts` | New test proving `createRNG(str)` derives its seed through the shared `hashString` (cross-module determinism). |
| `components/device/MainDevice.tsx` | Removed unused `getStageProgress` import (only `getStageName` is used). |
| `data/items.ts` | Removed unused `DECOR_ITEMS` export; fixed the `Celebration Cake` label typo. |
| `lib/progression/lifecycle.test.ts` | Test-only pre-existing TS2802 unblock (identical to PS-01/PS-03) so the typecheck gate can pass; not a runtime change. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---:|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `742c3d3`) | 0 | `remediation/PS-05/verify.log` — lint clean, typecheck clean, 5 files / 110 tests passed |
| `git archive HEAD \| tar -x -C /tmp/glscan-ps05 && gitleaks detect --no-git --redact --source /tmp/glscan-ps05 -v` | lab: `ci-runner` | 0 | `remediation/PS-05/verify.log` — scanned ~252 KB, no leaks found |
| `npm run lint` | local (Windows, node v24.19.0) | 0 | no ESLint warnings/errors |
| `npm run typecheck` | local (Windows, node v24.19.0) | 0 | clean |
| `npm run test` | local (Windows, node v24.19.0) | 0 | 5 files / 110 tests passed |

- Secret scan (gitleaks): pass, exit 0, no leaks found.
- Scope check (files within patch set + tests): pass. Runtime files are exactly the PS-05 set; the
  only extra is `lib/progression/lifecycle.test.ts`, a test-only pre-existing TS2802 unblock also
  carried by PS-01/PS-03 (reproduced as a baseline failure on `master`).

## Evidence bundle

- `remediation/PS-05/diff.patch` — SHA-256 `0627124e308d398266f4b09f6e66d811af423647176bb9887f7a1d61f432d018`
- `remediation/PS-05/manifest.json`
- `remediation/PS-05/verify.log`

## Risk and rollback

- Risk: **low**. Deletions are of unreferenced code; the `hashString` dedup is byte-identical in
  behavior and covered by new and existing determinism tests.
- Rollback: `git revert 742c3d335ce14826eb6147952899f43e922c7f21` (or close the PR without merging).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

`knip`/no-unused clean; determinism tests pass; label fixed.
