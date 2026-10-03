# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all testing remediation for the unassigned `TEST` findings from the
2026-10-03 audit run. It makes **coverage measured and enforced in CI**
(thresholds + commit-bound artifact), **exercises the mobile/a11y journeys in
Firefox and WebKit as well as Chromium**, fixes the broken **`test:unit`**
entry point, and raises the local gate with **`format:check`**. No application
behaviour changes.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U13` — Unassigned TEST findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `TEST-P2-001` | P2 | open -> **partially-fixed** | `vitest.config.ts` now declares the v8 coverage provider and a ratchet floor pinned to the measured baseline at this commit (lines 44.46%, statements 44%, functions 46.75%, branches 39.9% -> thresholds 43/43/45/38). The foundation CI job runs `npm run test:coverage` and uploads `coverage/` as a commit-bound `coverage-<sha>` artifact. The thresholds are a floor, not a target; they should be raised as coverage grows. |
| `TEST-P2-002` | P2 | open -> **partially-fixed** | `playwright.config.ts` adds `firefox` and `webkit` projects for the mobile-layout and accessibility journeys (`menu.mobile.spec.ts`, `shopPanel.a11y.spec.ts`); the sprite/WebGL spec stays Chromium-only. CI installs all three engines. Verified with `npx playwright test --list` (19 tests across the three projects); the browser journeys themselves are not runnable on the lab host (no browser install in this pass), so actual engine execution is deferred to CI. |
| `TEST-P2-003` | P2 | open -> **partially-fixed (dependency / cross-reference)** | This is the testing view of `DATA-P2-001` (the audit's own risk register says so). The fix — running `supabase/tests/*.sql` in the `migrations` CI job — is delivered by **PS-U04 (draft PR #14, commit `dcdceca`)**, which required a faithful Supabase auth stub and a forward migration (`0057`). It is deliberately **not duplicated here**: a second, conflicting edit of the same `ci-foundation.yml` / `ci-migrations-dryrun.sh` and a copy of `scripts/ci-db-tests.sh` would be outside this set's scope. See open question 1. |
| `TEST-P3-001` | P3 | open -> **partially-fixed** | `test:unit` no longer points at the non-existent `packages/*/src/apps`; it builds the packages/realtime and runs the real workspace paths (`vitest run packages apps/realtime --exclude '**/server.integration.test.ts'`). |
| `TEST-P3-002` | P3 | open -> **partially-fixed** | `scripts/verify-all.sh` now runs `format:check` (previously CI-only) and prints the documented local-vs-CI delta (e2e, compose validation, coverage and DB suites remain CI-only because they need browsers/docker/postgres). `AGENTS.md` and `README.md` updated to match. |

Status is `partially-fixed` while the PR is an unmerged draft; `tools/remediation_status.py`
marks `verified-fixed` only when the commit is merged.

## Changes

| File | What changed |
|---|---|
| `package.json` | `test:unit` fixed to real paths; new `test:coverage` script; `@vitest/coverage-v8` devDependency (required for `--coverage`). |
| `package-lock.json` | Lockfile entries for `@vitest/coverage-v8` and its transitive deps only. |
| `vitest.config.ts` | `coverage.provider: "v8"`, explicit excludes, and ratchet `thresholds` pinned to the measured baseline. |
| `playwright.config.ts` | `firefox` + `webkit` projects scoped to the mobile/a11y specs. |
| `.github/workflows/ci-foundation.yml` | Foundation job runs `npm run test:coverage` and uploads `coverage-<sha>`; e2e job installs chromium/firefox/webkit. |
| `scripts/verify-all.sh` | Adds `format:check`; documents the remaining local-vs-CI delta. |
| `AGENTS.md`, `README.md` | Gate descriptions and the bounded browser-support claim updated to match. |
| `apps/web/e2e/shopPanel.a11y.spec.ts` | Header comment made engine-neutral (the journey now runs in three engines). |

Coordination: `P1-3`, `PS-U03` and `PS-U04` also edit
`.github/workflows/ci-foundation.yml`. This PR adds a coverage step in the
`foundation` job and a browser-install change in the `e2e` job; those hunks are
disjoint from the SBOM/secret-scan/migration hunks, so the conflict surface is
small.

## Verification Performed

Run in a clean LF bundle clone on the ci-runner lab
(`/srv/work/snowride-ps-u13`, `core.autocrlf false`, HEAD `a7fb4a6`), Node
v20.20.2 / npm 10.8.2 / gitleaks 8.30.1 / actionlint 1.7.12. Raw output with
exit codes is in `remediation/PS-U13/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/ci-foundation.yml` | ci-runner | 0 | no findings |
| `bash -n scripts/verify-all.sh` | ci-runner | 0 | shell syntax OK |
| `npm ci` | ci-runner | 0 | 640 packages installed (646 audited; +12 vs base for the coverage provider) |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm run test:coverage` | ci-runner | 0 | thresholds enforced; 131 files / 873 tests passed; total lines 44.46% / statements 44% / functions 46.75% / branches 39.9% |
| `npm test` (profile gate) | ci-runner | 0 | 131 test files, 873 tests passed |
| `npx playwright test --list` | ci-runner | 0 | 19 tests: 7 chromium, 6 firefox, 6 webkit across 3 files |
| `git status --short` after the gates | ci-runner | 0 | clean |
| `gitleaks detect --no-git --redact` on each changed file (x9) | ci-runner | 0 | 9/9 changed files clean |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing `generic-api-key` fixtures under `evidence/**`; **none** in this diff |

- Secret scan (gitleaks): **pass** for this diff — all nine changed files clean;
  the 19 full-tree hits are the audited fixtures also recorded by
  PS-U03/U04/U10/U11.
- Scope check (files within patch set): **pass** — `PS-U13` declared no file
  list; the diff is limited to test configuration, the CI test steps, the local
  gate and the matching docs, plus the coverage-provider lockfile entries the
  coverage fix requires.
- `TEST-P2-003` is **not** run here; its evidence lives in PS-U04's PR #14
  (16 SQL suites pass on a fresh database against `postgres:17`).

## Evidence bundle

- `remediation/PS-U13/diff.patch` — SHA-256 `19d1b26b7421f8a0abb33838410a5c54e7ed5a89b5181a5468fb683dec212a97`
- `remediation/PS-U13/verify.log` — SHA-256 `d8b91d48eb9bdf50a4e81e2b549a410563f8626592d2f1f34304c47703e98660`
- `remediation/PS-U13/gitleaks.log`
- `remediation/PS-U13/manifest.json`

## Risk and rollback

- Risk: **low**. No application behaviour change. The coverage thresholds are a
  floor at the measured level, so `npm run test:coverage` is green at this
  commit; if a future engine yields slightly different coverage, the floor has a
  ~1-point margin. Adding `@vitest/coverage-v8` is the only dependency change
  and is required to run coverage at all.
- Rollback: `git revert a7fb4a6270774ad588f68184fa4a21cd5d61565c`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Coverage thresholds are a sane ratchet floor (raise over time)
- [ ] Rollback is practical

## Definition of done (for this set)

- Coverage runs in the foundation job, enforces a threshold, and produces a
  commit-bound artifact (`TEST-P2-001`).
- The mobile/a11y journeys are wired for Firefox and WebKit, not Chromium only
  (`TEST-P2-002`).
- `npm run test:unit` executes real tests (`TEST-P3-001`).
- The local gate runs `format:check` and documents the residual CI delta
  (`TEST-P3-002`).

## Open questions

1. **`TEST-P2-003` / coordination with PS-U04.** The SQL negative-suite gate is
   implemented in PS-U04 (draft PR #14) together with the DATA-P2-002 migration
   manifest and the `0057` forward migration it exposed. Merge order: whichever
   of PS-U04 / PS-U13 lands second should re-check that the `migrations` job
   still runs the suites after the `foundation` job changes here. Should
   remediation instead have folded TEST-P2-003 into PS-U04 and dropped it from
   this set?
2. **Coverage thresholds under the CI runtime (Node 24).** Measurement was made
   on the lab's Node 20; CI uses Node 24. The 1-point margin should cover v8
   variance, but the first green CI run should confirm; raise the numbers once
   stable. Should coverage also be wired into `scripts/verify-all.sh`, or is a
   local coverage run too slow to be the default gate?
3. **Firefox/WebKit on the certified host.** The bounded claim in `README.md`
   now says the mobile/a11y journeys run in three engines. That is true in CI;
   the local docs still tell contributors to install only `chromium` for the
   default `test:e2e`. Update the developer quick-start if local three-engine
   runs are expected.
