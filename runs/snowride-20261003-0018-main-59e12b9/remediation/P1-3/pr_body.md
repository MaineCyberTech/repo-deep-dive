# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **P1-3 (SBOM in CI)** closes two audit findings: the repository shipped a
CycloneDX tool but never invoked it, and CI produced no durable artifact bound to a
commit. This change generates a CycloneDX SBOM in the `foundation` job right after
`npm ci` and uploads it as a workflow artifact whose name is the full commit SHA, so
component inventory and vulnerability response can be sampled after the fact. It also
pins every action used by this workflow to a full commit SHA (supply-chain hardening;
the mutable-pin finding `CI-P2-002` remains separately tracked under P2-3).

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `P1-3` — SBOM in CI
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SUPPLY-P1-001` | P1 | open -> partially-fixed | SBOM generation + commit-bound upload added to `foundation`. Reaches `verified-fixed` only once the uploaded artifact is observable for a merged commit/run. |
| `CI-P3-001` | P3 | open -> partially-fixed | The SBOM is uploaded as `sbom-${{ github.sha }}` (retained 90 days), a durable artifact bound to the commit. Coverage upload is deferred to TEST-P2-001 (no coverage is produced yet). |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/ci-foundation.yml` | New `generate CycloneDX SBOM` step (`npx --no-install @cyclonedx/cyclonedx-npm --output-file sbom.json`, uses the lockfile-pinned devDependency). New `upload SBOM evidence (bound to commit)` step (`actions/upload-artifact`, artifact name includes `github.sha`, `retention-days: 90`, `if-no-files-found: error`). All `actions/checkout@v4` / `actions/setup-node@v4` references pinned to full commit SHAs (v4.4.0); the new upload action pinned to `actions/upload-artifact` v4.6.2. |

No runtime code, dependencies, or other files changed.

## Verification Performed

Run on the lab `ci-runner` (`172.23.128.51`) in a **clean LF git worktree** cloned
from a git bundle at the exact commit `d61c968` (dirty count 0), node `v20.20.2`,
npm `10.8.2`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci` | ci-runner, clean worktree | 0 | `remediation/P1-3/verify.log` |
| `npx --no-install @cyclonedx/cyclonedx-npm --output-file sbom.json` | ci-runner | 0 | `verify.log` |
| `node -e` validate SBOM (`bomFormat==="CycloneDX"`, specVersion, components) | ci-runner | 0 | `verify.log` — `SBOM OK bomFormat=CycloneDX specVersion=1.6 components=573` |
| `npm run lint` | ci-runner | 0 | `verify.log` — 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` | ci-runner | 0 | `verify.log` — 131 files, 873 tests passed |
| `actionlint .github/workflows/ci-foundation.yml` | ci-runner | 0 | `verify.log` |
| `gitleaks detect --no-git --redact --source <P1-3 diff.patch>` | ci-runner | 0 | `remediation/P1-3/gitleaks.log` — no leaks found |

- Secret scan (gitleaks): **pass** — no leaks in the patch (`gitleaks.log`).
- Scope check (files within patch set): **pass** — only `.github/workflows/ci-foundation.yml` changed.
- Workflow is syntactically valid (`actionlint`, exit 0). The GitHub-hosted run itself is not executed here; the first real run happens post-merge.

### Environment note (not caused by this change)

`lab-sync` tars the Windows working tree, which carries CRLF line endings. In that
copy `tests/ledger-format.test.ts` fails to transform (`SyntaxError`) because vitest
chokes on the CRLF `.ts`. The failure is purely environmental: the git blob for that
file contains LF (0 CR lines) and the clean LF worktree passes it (5/5 tests; full
suite 873/873). Verification was therefore run in a clean LF worktree at the commit,
which matches a normal CI checkout. README-only evidence of the delta is in the run
folder if a reviewer wants to reproduce it.

## Evidence bundle

- `remediation/P1-3/diff.patch` — SHA-256 `8170c7f28e5aeeb313a6c39abab66d5b724880b107e5d8411f7a0665049e6b10`
- `remediation/P1-3/manifest.json`
- `remediation/P1-3/verify.log` — SHA-256 `3f68fcff00c91adf467e28c8998db6057a6c3b7e2daefc46122fd15996bab102`

## Risk and rollback

- Risk: **low** — CI workflow only; no runtime code or dependency change. The SBOM
  step uses the already-lockfile-pinned `@cyclonedx/cyclonedx-npm` devDependency with
  `--no-install`, so it does not fetch an unpinned tool. Added CI cost is small.

- Rollback: `git revert d61c968` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

<!-- from patch_plan.md: npx @cyclonedx/cyclonedx-npm --output-file sbom.json; upload as artifact; retain per release -->

- [ ] `foundation` job produces `sbom.json` and uploads `sbom-<sha>`.
- [ ] Artifact is downloadable for the commit.

## Operator follow-up (required to reach `verified-fixed`)

1. Merge this PR (human review; this runner never merges or self-approves).
2. Confirm a `foundation` run on `main` uploaded the `sbom-<full-sha>` artifact and
   that it downloads and validates as CycloneDX.
3. Optionally reconcile the register to `verified-fixed` with that run as evidence.
