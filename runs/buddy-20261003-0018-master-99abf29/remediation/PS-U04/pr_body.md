# Remediation PR — PS-U04 Unassigned TEST findings (catch-all): TEST-P2-001, TEST-P2-002

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the two TEST catch-all findings by adding the missing layers the audit called out:

- **TEST-P2-001** — no component/UI tests despite `@testing-library/react` being installed.
  Adds React Testing Library tests for `StatBars`/`NeedBars`, `MainDevice`, `HatchFlow`, and
  `AdventureScreen`.
- **TEST-P2-002** — the persistence layer (IndexedDB, save migration, import/export) is untested.
  Adds `fake-indexeddb` and round-trip / version-handling / metadata / export-import tests against
  `lib/storage/indexeddb.ts`.

The audit's root concern was that the existing 109 tests are all pure functions and give false
release confidence: the known store/component divergence (ARCH-P1-002) and the save/version/import
bugs (DATA-P1-001/002, SEC-P2-001) had no regression protection. These tests exercise those paths
directly.

This set is additive (new test files + a dev dependency + two one-line enabling changes). It does
not change application/runtime logic.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-U04` — Unassigned TEST findings (catch-all)
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `e1c0555ccb451c3dd006c27ff8b581bc802002e3`
- Branch: `remediation/ps-u04-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `TEST-P2-001` | P2 | open -> partially-fixed | RTL component tests now cover the care action -> display/store loop (`MainDevice`), the hatch -> nickname flow (`HatchFlow`), the adventure energy gating + result application (`AdventureScreen`), and the stat/need ARIA bars (`StatBars`/`NeedBars`). The finding stays `partially-fixed` until the PR is merged. |
| `TEST-P2-002` | P2 | open -> partially-fixed | New `fake-indexeddb` storage tests cover save -> load round-trip (buddy/guestId/inventory), overwrite and delete, version normalization, save metadata, and export/import round-trip + malformed/`guestId`/`version` rejection without clobbering an existing save. The finding stays `partially-fixed` until the PR is merged. |

## Changes

| File | What changed |
|---|---|
| `lib/storage/indexeddb.test.ts` (new) | 15 tests for the persistence layer: empty-store behavior, save/load round-trip, last-write-wins, delete, version normalization, `getSaveMetadata`, and export/import validation (invalid base64, missing `version`, missing `guestId`, rejection does not overwrite). |
| `components/ui/StatBars.test.tsx` (new) | 5 tests: one `progressbar` per stat/need with `aria-valuenow/min/max`, width clamping, and the danger/accent colour thresholds. |
| `components/device/MainDevice.test.tsx` (new) | 4 tests: identity/level/action rendering, a care action updating both the display (`role="status"`) and the Zustand store, the STATS tab bars, and the PROFILE tab. |
| `components/hatch/HatchFlow.test.tsx` (new) | 3 tests: 16-character nickname cap, confirm committing buddy + nickname + screen transition, and blank nickname falling back to the species name. |
| `components/device/AdventureScreen.test.tsx` (new) | 3 tests: all locations disabled at zero energy, an affordable location enabled with energy, and an adventure applying its result to the store and rendering the outcome. |
| `vitest.config.ts` | Added `esbuild.jsx = 'automatic'`. The repo's `tsconfig.json` sets `"jsx": "preserve"` (Next.js); without this, Vitest cannot render `.tsx` components. Enabling change required by TEST-P2-001. |
| `package.json`, `package-lock.json` | Added `fake-indexeddb` devDependency (the tool the finding recommends for persistence tests). |
| `lib/progression/lifecycle.test.ts` | `[...new Set(x)]` -> `Array.from(new Set(x))`: unblocks `npm run typecheck` on the base commit (pre-existing `TS2802`; the identical minimal unblock is applied in PS-01/PS-03/PS-08/PS-U01/PS-U02/PS-U03). Supporting change so the required verification command runs green. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean) | 0 | `remediation/PS-U04/verify.log` — lint clean; typecheck clean; **10 files / 139 tests passed** (109 pre-existing + 30 new); `[lab-run exit code] 0` |
| `gitleaks detect --no-git --redact --exit-code 7` | lab: `ci-runner` (`/srv/work/buddy`) | 0 | `remediation/PS-U04/verify.log` — `no leaks found` |
| `npm run lint` | local (node v24.19.0) | 0 | No ESLint warnings or errors |
| `npm run typecheck` | local (node v24.19.0) | 0 | clean |
| `npm run test` | local (node v24.19.0) | 0 | 10 files / 139 tests passed |

- Secret scan (gitleaks): **pass** — exit 0, no leaks found.
- Scope check: **pass** — new tests for `TEST-P2-001`/`TEST-P2-002`, the `fake-indexeddb` dev
  dependency the fix requires, the JSX-runtime enabling line, and the pre-existing `TS2802`
  typecheck unblock. No application/runtime logic changed; this catch-all set has no declared file
  list.

## Evidence bundle

- `remediation/PS-U04/diff.patch` — SHA-256 `B4F7AE47D79353DC9C6807880D85A2AF6A7CA11E1A745BD3A1C79F2AFFA6F5B3`
- `remediation/PS-U04/manifest.json`
- `remediation/PS-U04/verify.log`

## Risk and rollback

- Risk: **low**. New test files only, plus a dev dependency and a Vitest JSX setting. No runtime
  behavior changes. The tests are deterministic (fixed inputs; `fake-indexeddb` is in-memory); the
  two timing-based flows (`HatchFlow` reveal, `AdventureScreen` result delay) use `waitFor` with a
  4s ceiling against the components' own 1.5-2s delays.
- Rollback: `git revert e1c0555`.

## Open questions / reviewer actions

1. **Coverage thresholds / E2E / CI wiring** were recommended alongside these findings but belong to
   other patch sets (`TEST-P3-001` + `CI-P1-001` in PS-01). This PR adds the tests, not the gate.
2. **`vitest.config.ts` overlaps PS-01** (which also edits the config for coverage/setup). The change
   here is a single `esbuild.jsx` block and is additive; a trivial conflict is possible at merge time.
3. **`fake-indexeddb` adds a dev dependency**; declare it acceptable for the test layer (or fold the
   version pin into the supply-chain set).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

Component tests for the named UI flows and `fake-indexeddb` persistence tests pass; lint/typecheck/
test green in the lab; gitleaks clean.
