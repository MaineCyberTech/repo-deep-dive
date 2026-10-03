# Remediation PR — PS-01 CI + governance

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Makes buddy's quality gate real. Previously there was no `.github/` at all: `lint`,
`typecheck`, `test`, and `build` existed as scripts but never ran automatically, dependencies
were not tracked for updates, and no code ownership routed review. This PR adds a blocking CI
workflow, Dependabot, and CODEOWNERS, and establishes coverage thresholds so test scope cannot
silently shrink. It also fixes a pre-existing `tsc` error in a test file so the new `typecheck`
gate can run green.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-01` — CI + governance
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `2d9cb592d95c025cddf60d42010ea6ebf1dda98a`
- Branch: `remediation/ps-01-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P1-001` | P1 | open -> fixed | `.github/workflows/ci.yml` runs `npm ci`, `lint`, `typecheck`, `test`, `test:coverage`, `build` on push/PR to `master`. |
| `CI-P1-002` | P1 | open -> partially-fixed | `CODEOWNERS` added so review is routed. Branch protection / required status checks are GitHub server-side settings and must be enabled by a maintainer (see Open questions). |
| `CI-P2-001` | P2 | open -> partially-fixed | Dependabot tracks `npm` and `github-actions` updates. A blocking `npm audit`/CodeQL step is deferred (tracked with PS-08); `npm audit` currently reports pre-existing advisories. |
| `TEST-P3-001` | P3 | open -> fixed | v8 coverage config with baseline thresholds, `test:coverage` script, `coverage/` ignored, and CI enforces the thresholds. |
| `EXEC-P2-001` | P2 | open -> partially-fixed | CI runs are now bound to commits, producing machine-checkable evidence at the merge commit; fully realized once the workflow runs on GitHub. |

`TEST-P3-001` required unblocking `npm run typecheck`, which failed on the base commit at
`lib/progression/lifecycle.test.ts:52` (`TS2802`). The spread of a `Set` cannot be downlevel
iterated at the project's default target; this PR makes the minimal test-side fix
(`Array.from(new Set(...))`) rather than changing the project-wide `tsconfig` target.

## Changes

| File | What changed |
|---|---|
| `.github/workflows/ci.yml` (new) | Blocking `ci` job: checkout, Node 20 + npm cache, `npm ci`, `npm run lint`, `npm run typecheck`, `npm run test`, `npm run test:coverage`, `npm run build`. Least-privilege `contents: read`; concurrency cancellation on superseded runs. |
| `.github/dependabot.yml` (new) | Weekly updates for the `npm` and `github-actions` ecosystems. |
| `.github/CODEOWNERS` (new) | Default owner `@JulianB-MCT` for all paths (routing only; enforcement needs branch protection). |
| `vitest.config.ts` | Adds v8 coverage over `lib/**` and `data/**` with baseline thresholds (lines/statements 80, branches 75, functions 65 — measured baseline is higher). |
| `package.json` | Adds `test:coverage` script and `@vitest/coverage-v8` devDependency. |
| `package-lock.json` | Lockfile entries for `@vitest/coverage-v8` and its transitive dependencies. |
| `.gitignore` | Ignores the `coverage/` output directory produced by the coverage run. |
| `lib/progression/lifecycle.test.ts` | Makes the pre-existing `TS2802` error go away so `npm run typecheck` can gate (`[...new Set(x)]` -> `Array.from(new Set(x))`). |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `git rev-parse HEAD && npm ci && npm run lint && npm run typecheck && npm run test && npm run test:coverage && npm run build` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`) | 0 | `remediation/PS-01/verify.log` — 109 tests passed; coverage 83.7% lines; build compiled; exit 0 |
| `gitleaks detect --no-git --redact --source /tmp/glscan` (tracked content at the commit) | lab: `ci-runner` | 0 | `remediation/PS-01/verify.log` — no leaks found |
| `npm run lint` | local (node v24.19.0) | 0 | No ESLint warnings or errors |
| `npm run typecheck` | local (node v24.19.0) | 0 | clean (`TS2802` gone) |
| `npm run test` | local (node v24.19.0) | 0 | 5 files / 109 tests passed |
| `npm run test:coverage` | local (node v24.19.0) | 0 | thresholds met |
| `npm run build` | local (node v24.19.0) | 0 | Compiled successfully; 4/4 static pages |

- Secret scan (gitleaks): pass on tracked repository content, exit 0, no leaks found. A whole-tree
  scan including `node_modules` reported 6 findings, all inside installed dependencies — not
  repository content and not introduced here.
- Scope check (files within patch set): pass — `.github/{workflows/ci.yml,dependabot.yml,CODEOWNERS}`,
  `vitest.config.ts`, `package.json`, plus the necessary supporting files `package-lock.json`
  (lockfile for the added dev dependency), `.gitignore` (ignore `coverage/`), and
  `lib/progression/lifecycle.test.ts` (the `TEST-P3-001` typecheck unblock called out in the patch
  instruction).

## Evidence bundle

- `remediation/PS-01/diff.patch` — SHA-256 `9d016aeec491a6746b5fa3cba79ea105289f624805d2d181a0963b67e994b565`
- `remediation/PS-01/manifest.json`
- `remediation/PS-01/verify.log`

## Risk and rollback

- Risk: **low**. CI, Dependabot, and CODEOWNERS are additive and do not change runtime code. The
  only source change is a test-only `Array.from(...)` fix and the coverage thresholds; thresholds
  are set below the measured baseline, so the existing suite passes while future shrinkage fails.
  The CI workflow is only *required* once branch protection is enabled (see Open questions).
- Rollback: `git revert 2d9cb59`.

## Open questions / reviewer actions

1. **Enable branch protection on `master`** — require a pull request, >= 1 approving review, and
   the `ci` status check; disallow force-push. This cannot be expressed as a repository file and is
   required to make the `ci` check truly blocking (`CI-P1-002`).
2. **Owner handle** — `CODEOWNERS` uses `@JulianB-MCT`, the repository's only contributor. Confirm
   or replace with the intended GitHub user/team.
3. **Audit scanning** — should `npm audit --production` and/or CodeQL become blocking CI steps?
   Deferred here because `npm audit` currently reports pre-existing advisories (20) that need
   triage; tracked with `CI-P2-001` / PS-08.

## Review checklist

- [ ] Diff touches only the patch-set files (+ necessary supporting files listed above)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean on tracked content
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

CI runs lint/typecheck/test/build on push and PR; coverage thresholds enforce test scope;
Dependabot and CODEOWNERS are present; branch protection is enabled by the maintainer.
