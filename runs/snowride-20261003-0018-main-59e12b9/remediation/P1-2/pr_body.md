# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the repository-side part of **CI-P1-001**: nothing in the repo proved
that `main` rejects un-reviewed or red-CI merges, so the `ci-foundation` gates
were advisory. This adds branch protection **as code** for `main`, an audit
tool, and a test that runs inside the `foundation` check, so the declared
required checks cannot silently drift from the workflow. Applying the setting
to GitHub is an operator action (it cannot be done from a PR); the runbook and
evidence commands are included.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `P1-2` — branch protection
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P1-001` | P1 | open -> partially-fixed | Policy declared + enforced for consistency in `foundation`; live GitHub protection still to be applied by an operator (token here had no `administration:read`). |

## Changes

| File | What changed |
|---|---|
| `.github/branch-protection.json` | New: desired protection for `main` — 1 review + CODEOWNERS, required checks `foundation`/`migrations`/`e2e`, strict, conversation resolution, no force-push/delete. |
| `scripts/verify-branch-protection.mjs` | New: validates the policy against the workflow's job names; `--print-expected` emits the GitHub API payload; live mode audits/exports the setting. |
| `tests/branch-protection.test.ts` | New: 6 tests; runs in `npm test`, which the `foundation` check runs, so drift fails CI. |
| `docs/runbooks/BRANCH_PROTECTION.md` | New: how to apply, capture evidence, and run the red-CI drill. |
| `CONTRIBUTING.md` | States the required review/checks for `main`. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci` | ci-runner (clean worktree `/srv/work/snowride-p1-2`, node v20.20.2) | 0 | `remediation/P1-2/verify.log` |
| `npm run lint` | ci-runner | 0 | `verify.log` (1 pre-existing warning in `Home.tsx`) |
| `npm test` | ci-runner | 0 | `verify.log` — 132 files, 879 tests passed; includes `tests/branch-protection.test.ts` (6) |
| `npx prettier --check <changed>` | ci-runner | 0 | `verify.log` |
| `node scripts/verify-branch-protection.mjs --self-test` | ci-runner | 0 | `verify.log` |
| `actionlint .github/workflows/ci-foundation.yml` | ci-runner | 0 | `verify.log` |
| `gitleaks detect --no-git --redact --source <P1-2 diff>` | ci-runner | 0 | `verify.log` — no leaks found |
| live branch-protection audit (`GITHUB_TOKEN` scoped) | — | not run | API returned 403 (token lacks `administration:read`); operator step in the runbook |

- Secret scan (gitleaks): pass (no leaks in the patch).
- Scope check: pass — only the policy, its tool/test, the runbook and CONTRIBUTING changed.

## Evidence bundle

- `remediation/P1-2/diff.patch` — SHA-256 `2b9ea4665cf00945775fd3f713754ba8409e0c89612cda5131324e0721a3c29e`
- `remediation/P1-2/manifest.json`
- `remediation/P1-2/verify.log` — SHA-256 `4bd5abd95d452fffdb170b60a399b272ac824587f5f7e3bf454029315e60323f`

## Risk and rollback

- Risk: low — governance/config + tests only; no runtime code, no dependency
  change. The CI consistency test is the only new gate.
- Rollback: `git revert 54c6070` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Operator follow-up (required to reach `verified-fixed`)

1. Apply the declared policy to `main` (Settings -> Branches, or
   `gh api -X PUT ... --input <(node scripts/verify-branch-protection.mjs --print-expected)`).
2. Capture evidence: `GITHUB_TOKEN=... GITHUB_REPOSITORY=MaineCyberTech/snowride node scripts/verify-branch-protection.mjs`.
3. Run the red-CI drill from `docs/runbooks/BRANCH_PROTECTION.md`.
