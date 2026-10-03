# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Adds the missing per-PR supply-chain checks to `ci-foundation` and pins the two
third-party actions to immutable commit SHAs. This is the catch-all CI patch set
from the 2026-10-03 snowride audit.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U03` — Unassigned CI findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P2-001` | P2 | open -> partially-fixed | Production-dependency audit (advisory) + pinned repository-tree gitleaks scan added to CI. Blocking audit enforcement is a follow-up (one pre-existing high advisory). |
| `CI-P2-002` | P2 | open -> fixed | `actions/checkout` and `actions/setup-node` pinned to `v4.4.0` commit SHAs in all three jobs. |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/ci-foundation.yml` | Pinned `actions/checkout@11d5960a…` and `actions/setup-node@49933ea5…` (v4.4.0) in `foundation`, `migrations`, `e2e`; added a repository secret scan and a production dependency audit to the `foundation` job. |
| `scripts/repo-secret-scan.sh` | New: repository-tree gitleaks scan. Uses a gitleaks already on `PATH`, else downloads pinned `v8.30.1` and verifies its SHA-256 before executing. Findings are `--redact`ed. |
| `.gitleaks.toml` | New: inherits the default gitleaks rules and allowlists only the audited secret-shaped fixtures (append-only `evidence/**` exports and the bundle gate's own test data) so the tree scan is clean. |

## Verification Performed

Run in a clean LF bundle clone on the ci-runner lab (`/srv/work/snowride-ps-u03`) at commit `cfd5d00`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/ci-foundation.yml` | ci-runner | 0 | `remediation/PS-U03/verify.log` |
| `bash scripts/repo-secret-scan.sh` | ci-runner | 0 | no leaks found, ~78 MB scanned (`verify.log`) |
| `npm ci` | ci-runner | 0 | 628 packages installed (`verify.log`) |
| `npm audit --omit=dev --audit-level=high` | ci-runner | 1 | 1 high advisory (`@grpc/grpc-js`); advisory in CI, recorded in `verify.log` |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed |
| `gitleaks detect --no-git --redact --source <changed files>` (x3) | ci-runner | 0 | no leaks in any changed file (`remediation/PS-U03/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source . --config .gitleaks.toml` | ci-runner | 0 | full-tree gate clean (`gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` (allowlist moved aside) | ci-runner | 1 | 19 pre-existing fixture hits (audited; none in this diff) |

- Secret scan (gitleaks): **pass** — changed files clean; full-tree scan clean with `.gitleaks.toml`.
- Scope check (files within patch set): **pass** — `PS-U03` declared no file list; the diff is limited to the CI workflow plus the scan script and its gitleaks config.

### Action SHAs verified independently

- `actions/checkout@v4.4.0` -> `11d5960a326750d5838078e36cf38b85af677262`
- `actions/setup-node@v4.4.0` -> `49933ea5288caeca8642d1e84afbd3f7d6820020`
- gitleaks `v8.30.1` linux_x64 tarball SHA-256 -> `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`

## Evidence bundle

- `remediation/PS-U03/diff.patch` — SHA-256 `3949ea3de0d68f680438b779e2bfbe3b362dd6dc50bd38c5ecccc9a0fa14a213`
- `remediation/PS-U03/verify.log` — SHA-256 `4594f636bde41db5f3c9fa5626c660b0ac240473f1c87172d606a511d3650398`
- `remediation/PS-U03/gitleaks.log` — SHA-256 `097e88de43f35a1f0ed082074c0a1df7a6a4fa0ae3bd69985e0f9efe3fc8a92c`
- `remediation/PS-U03/manifest.json`

## Risk and rollback

- Risk: low. CI-only change; no runtime code, no dependency or lockfile change, least-privilege (`contents: read`) preserved.
- The dependency audit is advisory (`continue-on-error: true`) so the one known high advisory does not block unrelated PRs.
- Rollback: `git revert cfd5d00adc9f3c01db21640c891edf7256a12f5a`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **Blocking audit policy.** `npm audit --omit=dev` currently reports one high advisory
   in the transitive runtime dependency `@grpc/grpc-js` (GHSA-m9gg-hp2v-232j /
   GHSA-f596-whhp-79r4; `npm audit fix` available). Should the audit step be made
   blocking now (which requires bumping that dependency, out of scope for this
   CI-only set), or stay advisory until the dependency is updated?
2. **Overlap with `SEC-P2-002` / `PS-U11`.** This PR adds a CI tree scan; the
   sibling SEC finding also asks for a pre-commit hook and history scanning.
   Decide whether to consolidate both into one gitleaks configuration.

## Definition of done (for this set)

- `foundation`, `migrations`, `e2e` continue to run; the two new `foundation` steps
  execute on every push/PR.
- Actions resolve to immutable SHAs (no mutable tags).
- A clean tree passes the committed gitleaks config; the audited fixtures are the
  only allowlisted paths.
