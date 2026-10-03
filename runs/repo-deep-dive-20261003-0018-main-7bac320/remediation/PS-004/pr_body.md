# Remediation PR — PS-004 (Wire the audit CI)

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Wires the pack's audit CI into `.github/workflows/` and adds a Linux pack CI so
the pack's own checks run automatically. The wired workflow lints the pack, runs
the end-to-end self-test on every PR and push to `main`, and — on pull requests —
validates each changed run folder and fails on any P0 finding. Run folders are
derived from the pull-request diff instead of a fixed `latest` path. The
reusable vendored-layout example (`ci/audit.yml`) is corrected to the in-repo
layout and is no longer mis-triggered by PR events. Review routing and the
required-check/bypass policy are documented.

- Audit run: `20261003-0018-main-7bac320`
- Patch set: `PS-004` — Wire the audit CI
- Repo / base: `repo-deep-dive` @ `b3d038250f5437490df21e1d25a1ea1297530559` (`main`)
- Branch: `remediation/ps-004-20261003-0018-main-7bac320`
- Commit: `ca641962f156f8320923e555ce1b8374f695b06a`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P1-001` | P1 | open -> fixed | The audit workflow now lives at `.github/workflows/audit.yml` and executes. |
| `CI-P1-002` | P1 | open -> fixed | `ci/audit.yml` `PACK_DIR` is `.` (in-repo layout), not a vendored path. |
| `CI-P2-005` | P2 | open -> partially-fixed | `.github/CODEOWNERS` added; required checks + bypass policy documented in `CONTRIBUTING.md`. Branch protection / required status checks are GitHub server-side settings that a repo admin must enable (see Open questions). |
| `CI-P2-006` | P2 | open -> fixed | PR events no longer feed an empty `run_dir`; the wired workflow derives changed run folders from the diff and gates each one. The example is `workflow_dispatch` only. |
| `TEST-P1-001` | P1 | open -> fixed | New `pack lint + self-test` CI job runs `tools/lint_pack.sh` + `tools/self_test.sh` on `pull_request` and `push` to `main`. |
| `TEST-P2-002` | P2 | open -> fixed | The bash suite now runs on Linux (`ubuntu-latest`) in CI on every push/PR. |

Statuses map per `profiles/remediation.md`: an open draft PR reconciles to
`partially-fixed`; `verified-fixed` requires a merge/release artifact.

## Changes

| File | What changed |
|---|---|
| `.github/workflows/audit.yml` (new) | Wired in-repo CI: `pack` job (lint + self-test) on PR/push; `run-gate` job on PRs that detects changed `runs/**` folders from the diff, runs `check_run.sh` + `run_toolchain.py`, and fails on any P0 finding. |
| `ci/audit.yml` | `PACK_DIR: .`; validated `run_dir` input; `workflow_dispatch` only so PR events cannot pass an empty `run_dir`; removed the fixed `docs/audits/repo-deep-dive/latest` fallback; documented as the reusable example. |
| `.github/CODEOWNERS` (new) | Default + per-path review routing for `.github/`, `ci/`, `tools/`, `schemas/`, `profiles/`. |
| `CONTRIBUTING.md` | New "CI and required checks" section: required checks, admin-only branch protection, and the bypass policy. |
| `PACK_DIGEST.txt` | Regenerated (`tools/pack_digest.sh`) for the new/changed files. |

## Verification Performed

All commands run in WSL Ubuntu-24.04 against the patched clone at commit
`ca641962f156f8320923e555ce1b8374f695b06a`, using the repo's real gates and the
lab's actionlint 1.7.12 / gitleaks 8.30.1. Full raw output:
`remediation/PS-004/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint -no-color .github/workflows/audit.yml` | lab actionlint 1.7.12 | 0 | `verify.log` §1 |
| `actionlint -no-color ci/audit.yml` | lab actionlint 1.7.12 | 0 | `verify.log` §2 |
| `bash tools/lint_pack.sh` | repo gate | 0 (`RESULT: PASS`) | `verify.log` §8 |
| `bash tools/self_test.sh` | repo gate | 0 (`RESULT: PASS`) | `verify.log` §9 |
| Extract workflow `run:` scripts from YAML, then `bash -n` | pyyaml + bash | 0 | `verify.log` §13 |
| Changed-run diff filter (unit check) | awk | 0 | `verify.log` §6 |
| P0 gate logic (P0 -> exit 1, clean -> exit 0) | python3 | 0 (assertion) | `verify.log` §7 |
| gitleaks changed-file scan (default rules) | lab gitleaks 8.30.1 | 0 (no leaks) | `verify.log` §10 |

- Secret scan (gitleaks): **pass** — the changed files report no leaks.
- Scope check (files within patch set + docs): **pass** — `.github/workflows/audit.yml`,
  `ci/audit.yml`, `.github/CODEOWNERS`, `CONTRIBUTING.md` (documentation), and the
  generated `PACK_DIGEST.txt`.
- `bash -n` on the YAML-extracted `run:` scripts proves the heredoc in the P0-gate
  step survives GitHub Actions' block-scalar indentation stripping.

## Evidence bundle

- `remediation/PS-004/diff.patch` — SHA-256 `f89b685c5f2caa5a7c7cca5e8e31627834f3be40e6a995308667d5e55480682e`
- `remediation/PS-004/verify.log` — SHA-256 `695dc37dbd32884ac4556a9bae12e96037ba05749ba697e9b1173b669f38da18`
- `remediation/PS-004/manifest.json`

## Risk and rollback

- Risk: **low**. CI and docs are additive; no runtime code. The `pack` job
  duplicates `lint_pack.sh` inside `self_test.sh` (intentional, matches TEST-P1-001).
- The new `run-gate` job runs `run_toolchain.py --write` on changed runs in an
  ephemeral checkout; it never commits. Its P0 gate is the same logic as the old
  example.
- Branch protection/required checks are **not** enforced by this PR (server-side);
  until an admin enables them the checks are advisory.
- Rollback: `git revert ca641962f156f8320923e555ce1b8374f695b06a`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ documentation and generated `PACK_DIGEST.txt`)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- `CI-P2-005`: branch protection, required reviews, and required status checks are
  GitHub server-side settings; the files here express intent only. An admin must
  require a pull request, review, and the `pack lint + self-test` / `changed-run gate`
  checks on `main`.
- `CODEOWNERS` uses `@JulianB-MCT` (the repository's only contributor). Confirm the
  handle if ownership changes.

## Definition of done (for this set)

`patch_plan.md` PS-004 verification: *PR runs `lint_pack.sh` + `self_test.sh`; a P0
fixture run fails the P0 gate; required checks block merge.* The first two are
demonstrated in `verify.log` (§8–§9, §7); required checks are declared in
`CONTRIBUTING.md` and `.github/CODEOWNERS` but must be enabled by an admin.

## Dependencies / disjointness

PS-002 (#1) and PS-003 (#2) are open on `main`. This PR touches none of their
files (`tools/`, `schemas/`, `examples/`, `.github/workflows/deep-dive-deterministic.yml`,
`.gitleaks.toml`, `.github/dependabot.yml`). `PACK_DIGEST.txt` is shared-generated;
regenerate with `tools/pack_digest.sh` when rebasing either PR.
