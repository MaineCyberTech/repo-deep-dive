# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the two unassigned FEAT findings from the `snowride` audit by making the
production feature-flag state and the readiness view honest and drift-checked.
Production already runs scoring/hazard/gear features live, but the repo's
documented default (and the readiness endpoint) did not say so: this PR makes
compose the single documented source of production flag values, adds a CI drift
check, and derives `/launch-readiness` `deployed` from the modules compiled into
the artifact instead of a hardcoded `true`.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U06` — Unassigned FEAT findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P2-001` | P2 | open -> partially-fixed | `docs/runbooks/KILL_SWITCHES.md` now documents the production overrides with `infra/compose/docker-compose.yml` as the single source of truth, `.env.example` warns that its values are code/dev defaults, and `tests/feature-flag-drift.test.ts` fails CI if the runbook table and compose diverge. |
| `FEAT-P3-001` | P3 | open -> partially-fixed | `/launch-readiness` no longer hardcodes `deployed: true`: `apps/realtime/src/server.ts` derives each flag from `DEPLOYED_FEATURE_MODULES`, built from the versioned feature modules compiled into the artifact, via `isDeployedFeature()` in `productSurface.ts`; a unit test asserts a missing/zero-version module reports `deployed: false`. |

Both are draft-PR `partially-fixed` per policy (`tools/remediation_status.py` maps `open`/draft to `partially-fixed`); they become `verified-fixed` on human merge.

## Changes

| File | What changed |
|---|---|
| `docs/runbooks/KILL_SWITCHES.md` | New "Production overrides (source of truth: `infra/compose/docker-compose.yml`)" section: the code defaults vs the five values production forces (`TRICK_SCORING_MODE=enforce`, `AVALANCHE_MODE=live`, `MOVING_HAZARD_MODE=live`, `GEAR_MODE=live`, `METRICS_SNAPSHOT_INTERVAL_MS=300000`), plus a pointer to the drift test. |
| `.env.example` | Header comment states these are CODE/dev-test defaults and lists the production overrides, warning that copying the file to a prod host would turn features OFF. |
| `apps/realtime/src/productSurface.ts` | Added pure `isDeployedFeature(moduleVersions, name)` helper: `deployed` is true only when the module version is present, finite and > 0. |
| `apps/realtime/src/server.ts` | Added `DEPLOYED_FEATURE_MODULES` derived from `TRICKS_VERSION` / `AVALANCHE_VERSION` / `AUTHORITATIVE_SIM_VERSION` / `MOVING_HAZARD_VERSION`; `/launch-readiness` now computes `deployed` from it instead of literals. |
| `apps/realtime/src/__tests__/launchReadinessDeploy.test.ts` | New: asserts absent / zero-version modules report `deployed: false` and the derivation propagates through `launchReadinessView`. |
| `tests/feature-flag-drift.test.ts` | New: parses the compose overrides and the runbook table and fails CI if they diverge. |

No behavior change when all modules are present (all four version constants are `> 0`, so the four flags still report `deployed: true`); the fix removes the ability of the endpoint to over-claim silently.

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab (`/srv/work/snowride-ps-u06`, `core.autocrlf` unset) at commit `97211d6`. `npm ci && npm run lint && npm test` plus gitleaks.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci` | ci-runner | 0 | 628 packages installed (`remediation/PS-U06/verify.log`) |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` (`verify.log`) |
| `npm test` | ci-runner | 0 | 133 test files, 877 tests passed (baseline 131/873 + the 2 new files) (`verify.log`) |
| `git status --short` after gates | ci-runner | 0 | clean (generated files not committed) |
| `gitleaks detect --no-git --redact --source <6 changed files>` | ci-runner | 0 | no leaks in any changed file (`remediation/PS-U06/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing audited fixture hits under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff (`gitleaks.log`) |

- Secret scan (gitleaks): **pass** — every changed file clean; the 19 full-tree hits are the same audited, pre-existing fixtures recorded by the sibling PS-U03/PS-U04/PS-U05 runs.
- Scope check (files within patch set): **pass** — `PS-U06` declared no file list; the two findings name the config/compose/server surface, and the diff is limited to those plus the docs and the two tests the fix requires.

## Evidence bundle

- `remediation/PS-U06/diff.patch` — SHA-256 `43739473390000aae6c4d8f10ac8382dd9ad5c8d480ef063ff6ad776ff5f7f98`
- `remediation/PS-U06/verify.log` — SHA-256 `d1cf51db236c3b065b41ca186f30dd9a88c18094c9194c6ba8ae3e2a0280b8ab`
- `remediation/PS-U06/gitleaks.log` — SHA-256 `3e4e14a687b4f3aaeecdc4904fc220ffd8ce09704d9e97424b6ee6391f516946`
- `remediation/PS-U06/manifest.json`

## Risk and rollback

- Risk: **low**. Docs + tests plus one small, behavior-preserving runtime change. `DEPLOYED_FEATURE_MODULES` reads only existing module version constants; the readiness response keeps `deployed: true` for all four flags in this build. No dependency, lockfile, migration or CI-workflow change.
- Rollback: `git revert 97211d66cc3ccde3cfb4df0539808d0d6d833d66`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **`deployed` is still `true` in a single-bundle build.** All four modules are compiled into the one realtime artifact, so the derivation does not change today's values; it removes the silent over-claim and responds if a module is ever built out (version absent/0). If the project later splits features into separately built images, `DEPLOYED_FEATURE_MODULES` is the single place to bind that reality.
2. **`config.ts`/`.env.example` remain the code defaults.** FEAT-P2-001's alternative ("make config.ts the source") was deliberately not taken: compose is the deploy-time authority for the running service. The docs now state this explicitly rather than duplicating the values into code.
