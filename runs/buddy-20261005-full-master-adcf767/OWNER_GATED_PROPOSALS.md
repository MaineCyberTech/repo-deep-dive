# Owner-gated findings — proposals and residuals

Run: `buddy-20261005-full-master-adcf767` · Target: `buddy` @ `adcf767` (branch `master`)

This run has **no P0** and four P1 findings. One P1 (`CI-P1-001`) is code-fixable and is
implemented in draft PR [MaineCyberTech/buddy#35](https://github.com/MaineCyberTech/buddy/pull/35);
the other three are **owner-gated** (repository settings / product decision). No infrastructure
was changed for the owner-gated part.

## CI-P1-001 — CI is failing on master at the audited commit

- **Code-fixable half (done — draft PR [#35](https://github.com/MaineCyberTech/buddy/pull/35),
  commit `343f569`)** — not owner-gated. The `security` job failed because `next@15.5.27`
  vendors `postcss@8.4.31` (affected by `postcss <=8.5.22`, GHSA-qx2v-qp2m-jg93 and the
  `sourceMappingURL` file-read advisories). The fix is the finding's "validated override"
  option: a root `overrides.postcss` pin to `^8.5.28`. `npm audit --audit-level=high --omit=dev`
  → `found 0 vulnerabilities`; full local gate green. `RA-001` is closed.
- **Residual until merge**: `master` CI stays red until #35 merges. On a `master` push the
  `dependency-review` job does not run (`if: pull_request`), so the only remaining master-red
  cause is the security job, which #35 fixes.

## BP-P1-001 — `master` is unprotected: no required PR, review, or status checks

- **Evidence (live API)**: `gh api repos/MaineCyberTech/buddy/branches/master/protection`
  → `404 Branch not protected`; `gh api repos/MaineCyberTech/buddy/rulesets` → `[]`.
- **Owner-gated half (proposal — no infra changed)**: create a `master` ruleset (or classic
  branch protection) that requires a pull request before merging, requires the `CI` status
  check, requires review from `.github/CODEOWNERS`, and blocks force-push and deletion. The
  concrete settings are already documented in `docs/release-process.md` §Protected `master`
  branch and in the pack's `branch_protection_recommendation.md`.
- **Residual**: `master` remains directly pushable and unprotected; any push can bypass
  review and the CI gate. The plan-gated limit (rulesets may require a paid plan) is the
  reason this is not applied from code.

## BP-P1-002 — the `release` environment required by `release.yml` does not exist

- **Evidence (live API)**: `gh api repos/MaineCyberTech/buddy/environments` → only `dev` and
  `development`; `release.yml` sets `environment: release` on the `build` job.
- **Owner-gated half (proposal — no infra changed)**: create the `release` environment, add
  the release owner(s) under **Required reviewers**, and restrict **Deployment branches and
  tags** to tags matching `v*`. Steps are documented in `docs/release-process.md` §Release
  environment.
- **Residual**: a `v*` tag push currently starts the release `build`/`publish` with no
  approval gate; a stolen write token is not stopped by an environment reviewer.

## ARCH-P1-001 — client is fully authoritative: no server trust boundary exists

- **Owner-accepted**: deferred while the app is guest-only and local-first; the dated,
  owned acceptance is already recorded in `docs/README.md` (accepted/deferred risks table).
- **Residual**: there is no server-side validation boundary. It must be added before any
  account/cloud mode, at which point this lens must be re-run.

## Other owner-gated classes in scope (no P1 remaining)

The remaining P2/P3 owner-gated items (repository security settings `CI-P2-001`/`SC-P2-002`,
license decision `SC-P2-003`, etc.) are recorded in the follow-up register and are **not**
part of this P1 reconciliation; none was changed.
