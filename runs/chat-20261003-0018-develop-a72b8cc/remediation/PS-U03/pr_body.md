<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the unassigned CI governance findings for run `20261003-0018`: make the `main`
branch-rules check blocking and correct, and stop publishing container images from pull
requests. Both are workflow-only, minimal changes.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U03` — Unassigned CI findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (`develop`)
- Branch: `remediation/ps-u03-20261003-0018-develop-a72b8cc`
- Commit: `8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P2-007` | P2 | open -> partially-fixed | Branch-protection check is now blocking, uses the aggregated branch-rules API, and requires PR review + status checks + no force pushes on `main`. |
| `CI-P1-001` | P1 | open -> partially-fixed | The same branch-rules gate is the in-repo enforcement piece of this finding. The other recommended controls (required `production` environment reviewers; required PR review on `main`) are repository settings, not workflow code — see Open questions. |
| `CI-P2-006` | P2 | open -> partially-fixed | `build-push` no longer publishes to GHCR on pull requests; PRs build only (and load locally for the image scan). |

Statuses map to `partially-fixed` because the PR is a draft; they become `verified-fixed`
after a green CI run / merge at which the gates take effect.

### Overlap with PATCH-07 (#63) — no duplication

`PATCH-07` (#63) made the *quality/security* gates blocking (`CI-P1-003`, `TEST-P1-001`,
`FINAL-P2-003`) by removing `continue-on-error`/`|| true` from the audit, Trivy and E2E
steps. It explicitly left the **branch-protection** job's `continue-on-error: true` in
place (recorded as out of PATCH-07 scope, and still present at base line 250). Therefore:

- `CI-P2-007` is **not** covered by #63 — this PR is its only fix.
- `CI-P1-001`'s "make the branch-protection check blocking" recommendation is **not**
  covered by #63 either; this PR implements it. The fix is shared with `CI-P2-007`, so it
  is implemented once and mapped to both findings rather than duplicated.

Both PRs touch `.github/workflows/build-push.yml` and `.github/workflows/validate.yml`, but
in disjoint hunks (PATCH-07: audit/Trivy/E2E steps; this PR: the build `push`/`load` inputs
and the `branch-protection` job). They should merge cleanly; note the file-level overlap for
merge ordering.

## Changes

| File | What changed |
|---|---|
| `.github/workflows/validate.yml` | `branch-protection` job: removed `continue-on-error: true` (was advisory); replaced the deprecated `repos.getBranchProtection` call (404s when protection is a ruleset, and wrongly treats the optional `restrictions` field as required) with the aggregated `GET /repos/{owner}/{repo}/rules/branches/{branch}` endpoint; the gate now requires the `pull_request`, `required_status_checks`, and `non_fast_forward` rule types on `main`; the odd `github.repository_owner == github.actor` condition is replaced with a clear PR-or-push-to-`main` condition. |
| `.github/workflows/build-push.yml` | The three `docker/build-push-action` steps now use `push: ${{ github.event_name != 'pull_request' }}` and `load: ${{ github.event_name == 'pull_request' }}` (was `push: true`). Pull requests build without publishing; loading the built image locally keeps the existing Trivy image scans pointed at the PR build instead of a stale `:dev` tag. |

Scope: the two CI workflow files cited by the findings. No application code, dependency
bumps, other workflow edits, or repository-setting changes.

## Verification Performed

Runner: `ci-runner` (LXC 200), clean workspace `/srv/work/chat-ps-u03` at commit `8e5ab8a`.
Full raw log: `remediation/PS-U03/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/validate.yml` | ci-runner (actionlint 1.7.12) | 1 | 12 diagnostics, **identical to base** (pre-existing shellcheck info/style only) — `verify.log` §2/§7 |
| `actionlint .github/workflows/build-push.yml` | ci-runner | 1 | 1 diagnostic, **identical to base** (pre-existing shellcheck) — `verify.log` §2/§7 |
| `yq -e '.jobs \| keys'` both workflows | ci-runner (yq 4.54.1) | 0 | both parse; job keys unchanged — `verify.log` §3 |
| branch-protection job `continue-on-error` assertion | ci-runner | 0 | `continue-on-error: null` — `verify.log` §4 |
| branch-rules API assertion | ci-runner | 0 | `rules/branches` used in code; `getBranchProtection` only in the explanatory comment — `verify.log` §4 |
| build-push publish assertion | ci-runner | 0 | 0 bare `push: true`; 3 conditional `push`; 3 `load` — `verify.log` §4 |
| **executable gate logic test** (extracts the exact `github-script` body and runs it under node with mocked `github`/`context`/`core`) | ci-runner (node 20.20.2) | 0 | **negative case** (missing `pull_request`/`required_status_checks`) calls `setFailed`; **positive case** passes — `verify.log` §5 |
| `git diff base..HEAD \| gitleaks stdin --exit-code 1` | ci-runner (gitleaks 8.30.1) | 0 | no secrets added by the diff — `verify.log` §6b |
| `gitleaks` changed-file scan (no allowlist) | ci-runner | 1 / 0 | `build-push.yml` clean; `validate.yml` reports the **pre-existing** hardcoded Supabase anon JWT fixture (base line 396 -> branch line 411, unchanged) — `verify.log` §6a/§7 |
| `gitleaks` full worktree (JSON) | ci-runner | 1 | 5 **pre-existing** findings (`validate.yml:jwt`, `keyboard-shortcuts.tsx:generic-api-key`, `infra/docker/.env.dev.example:jwt` x3); **none introduced by this diff** — `verify.log` §6c |

- **No new actionlint diagnostics**: base `validate.yml` 12 = branch 12; base `build-push.yml`
  1 = branch 1. The non-zero exit is the pre-existing shellcheck backlog, not this change.
- **Gate logic is exercised, not asserted**: the negative case proves a misconfigured `main`
  fails the new blocking check; the positive case proves a correctly-configured `main` passes.
- **Secret gate**: clean on the diff. The only changed-file hit is pre-existing and unchanged.

## Evidence bundle

- `remediation/PS-U03/diff.patch` — SHA-256 `7B658AB9352C2D92A0983416B38F462292066128B075B1EB3E426B397392CD79`
- `remediation/PS-U03/manifest.json`
- `remediation/PS-U03/verify.log`

## Risk and rollback

- Risk: **medium**. Making the branch-rules check blocking means CI will fail if `main` is
  not protected with required PR reviews, required status checks, and force-push blocking.
  That is the intended fail-closed behaviour (a missing governance control should fail, not
  pass silently), but the first run may be red until a maintainer configures/confirms the
  rules on `main`. The build-push change removes PR publish permissions only; it does not
  change what is built or scanned.
- Rollback: `git revert 8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3` (workflow-only change).

## Review checklist

- [ ] Diff touches only `.github/workflows/validate.yml` and `.github/workflows/build-push.yml`
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] A maintainer confirms `main` carries (or will carry) required PR review + status checks
      before this blocking gate is merged, so the first run is green
- [ ] Overlap with #63 (PATCH-07) reviewed for merge order; hunks are disjoint
- [ ] Rollback is practical

## Definition of done (for this set)

- The `main` branch-rules check is blocking and evaluates rulesets/classic protection correctly.
- Pull requests no longer publish images to GHCR.
- Repository settings (production environment reviewers; required PR review on `main`) are
  configured by a maintainer (outside workflow code).

## Open questions

1. **CI-P1-001 administrative controls are repository settings, not code.** GitHub
   environment protection reviewers for `production` and required PR reviews on `main`
   cannot be expressed in a workflow file. The in-repo portion (blocking branch-rules gate)
   is fixed here; a maintainer must confirm/configure the settings. The audit itself listed
   "Are GitHub `production` environment protection rules configured?" as Unknown.
2. **Merge order with #63.** Both PRs edit `validate.yml` and `build-push.yml`; the hunks are
   disjoint, but whichever merges second should rebase. #63 also changes the build-push Trivy
   steps that consume the images built here.
3. No behavioural change is made to the production deploy trigger
   (`deploy-production.yml` `on: push: branches: [main]`); removing or reworking it is a
   release-process/product decision and is intentionally left to the owner rather than
   guessed at here.
