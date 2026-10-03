# Patch Plan — buddy

- Audit: repo-deep-dive (Full Hardening, profile base)
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy` — `master` @ `99abf29`
- Generated: 2026-10-03T04:18Z

Every finding lands in exactly one patch set. PS-01 (P0-only immediate set) — there are no P0s here, so PS-01 is the first release-blocking set and has no dependencies. Sets spanning 3+ files get their own set.

## Patch-set mapping

| Set | Title | Findings | Files | Depends on | Effort | Verification |
|---|---|---|---|---|---|---|
| PS-01 | CI + governance | CI-P1-001, CI-P1-002, CI-P2-001, TEST-P3-001, EXEC-P2-001 | `.github/workflows/ci.yml`, `.github/dependabot.yml`, `.github/CODEOWNERS`, `vitest.config.ts`, `package.json` | — | S | CI runs lint/typecheck/test/build; failing PR is blocked; `test:coverage` script exists |
| PS-02 | Licensing & provenance | SUPPLY-P1-001, SUPPLY-P2-003 | `LICENSE`, `NOTICE`, `docs/README.md` | — | S | GitHub license detection; pack provenance documented |
| PS-03 | State & identity correctness | ARCH-P1-002, ARCH-P2-002, SEC-P3-001 | `components/device/MainDevice.tsx`, `components/device/AdventureScreen.tsx`, `app/page.tsx`, `lib/buddy/store.ts`, `components/hatch/HatchFlow.tsx` | — | M | component test: adventure updates device; reload test preserves guestId |
| PS-04 | Save integrity | DATA-P1-001, DATA-P1-002, DATA-P2-001, SEC-P2-001 | `lib/storage/indexeddb.ts`, new `lib/storage/schema.ts`, `lib/storage/autosave.ts` | — | M | migration fixtures + fuzz/malformed-import tests pass |
| PS-05 | Hygiene / dead code | ARCH-P2-003, HYG-P2-001, HYG-P2-002, HYG-P3-001 | `lib/storage/autosave.ts`, `lib/generation/rng.ts`, `lib/generation/hash.ts`, `data/items.ts`, `components/device/MainDevice.tsx` | PS-03 | S | `knip`/no-unused clean; determinism tests pass; label fixed |
| PS-06 | Feature wiring | FEAT-P1-001, FEAT-P1-002, FEAT-P2-001 | `lib/actions/care.ts`, `lib/locations/adventure.ts`, `components/device/MainDevice.tsx`, `components/device/InventoryScreen.tsx`, `data/achievements.ts` | PS-04 | M | integration tests: achievement once; lifecycle transition; item use |
| PS-07 | Operations, privacy, offline | OBS-P2-001, OBS-P2-002, OBS-P3-001, API-P2-001*(partial), API-P2-002, SEC-P2-002, ARCH-P2-001 | `app/error.tsx`, `next.config.js`, `public/sw.js`, `app/globals.css`, `app/layout.tsx`, public fonts | PS-03 | M | error-boundary test; header assertions; offline font load; cache name changes on build |
| PS-08 | Supply chain & inventory fidelity | SUPPLY-P2-001, SUPPLY-P2-002, API-P2-001, INV-P2-002 | `package.json`, `package-lock.json`, `.github/dependabot.yml`, run `inventory.json` | PS-01 | M | `npm audit` clean/triaged; SBOM artifact; inventory matches tree |
| PS-09 | Documentation reconciliation | INV-P2-001, INV-P3-001, FINAL-P2-001, FINAL-P2-002, EXEC-P2-001 | `README.md`, `CHANGELOG.md`, `docs/README.md`, phase reports, `risk_register.md` | — | S | link check; claims match code; register has owner/status |

Note: ARCH-P1-001 (server authority) and the RLS/tenant implications are **future platform work**, not part of this release patch plan; they are captured on the roadmap (60–90 day) and must be re-audited when account/cloud features are added. There is no P0 patch set because the run found zero P0 findings.

## Immediate patch set (release blocking) — PS-01

Purpose: make the project's own quality gate real and bind releases to commits.

```text
.github/workflows/ci.yml
  on: [push, pull_request]
  jobs:
    ci:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version: 20, cache: npm }
        - run: npm ci
        - run: npm run lint
        - run: npm run typecheck
        - run: npm run test
        - run: npm run build
```

Also: `.github/dependabot.yml`, `.github/CODEOWNERS`, branch protection requiring the `ci` check.

## Validation commands (per set)

| Set | Command |
|---|---|
| PS-01 | `npm ci && npm run lint && npm run typecheck && npm run test && npm run build` |
| PS-02 | `test -f LICENSE && echo ok` ; GitHub license badge |
| PS-03 | `npm run test -- MainDevice AdventureScreen` |
| PS-04 | `npm run test -- storage` (new tests) |
| PS-06 | `npm run test -- achievements lifecycle items` |
| PS-07 | `npm run build && npm run test -- error` ; header curl |
| PS-08 | `npm audit --production` ; SBOM generation |
| PS-09 | docs link checker |

## Definition of done

- All findings in PS-01..PS-04 closed or owner-accepted with artifacts.
- CI green and required; LICENSE present; save/state/feature tests passing.
- `risk_register.md` rows updated with status/owner; `INDEX.md` and `audit_manifest.json` refreshed.
