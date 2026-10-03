# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U03` (unassigned CI findings). After checking `origin/main`
(`430da82`), three of the five findings are already `verified-fixed` at the base commit
(`CI-P1-001`, `CI-P2-001`, `CI-P3-001`) and one is `owner-accepted` (`CI-P1-002`,
plan-gated branch protection). The only open item, `CI-P2-002` (auto-merge holds
`contents: write` with no environment protection), is an **owner/plan setting**: on a
private GitHub Free repository, required reviewers and wait timers for environments are
not available, exactly like the plan-gated branch protection the repo already documents.

This PR therefore makes the one safe, reproducible repo-local contribution: an **offline
regression guard** (`automation/validation/tests/ci_governance_guard_test.sh`, run by
`ci/validate.py`'s shell-test suite) that pins the compensating controls so they cannot
silently regress, and it records the environment-protection residual as an owner open
question instead of guessing a setting that cannot be applied. No workflow file is
changed, so no live behaviour changes.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U03` — Unassigned CI findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u03-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `375c4fb13d5ff24b2fa1df2d48565e9ec11f2124`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P2-002` | P2 | open -> partially-fixed (draft PR) | The auto-merge compensating controls are now guarded by an offline test: author restricted to `app/dependabot`, the owner `dependabot-approved` label required, and `gh pr checks` green before `gh pr merge`; a mutation test proves the guard fails when the label gate is removed. The finding's **protected-environment** recommendation needs an owner/plan decision (see open questions) and remains open. |
| `CI-P1-001` | P1 | verified-fixed (base) -> guarded | Already fixed at `430da82` (every `curl` fails fast + SHA-256 verified). New guard asserts no un-`--fail` `curl` and that downloads are hash-verified. No status change. |
| `CI-P2-001` | P2 | verified-fixed (base) -> guarded | Already fixed at `430da82` (`check_evidence_index` wired into `CHECKS`). New guard asserts the function, the `evidence-index` check id, and the referenced script. No status change. |
| `CI-P3-001` | P3 | verified-fixed (base) -> guarded | Already fixed at `430da82` (local + CI shellcheck both `--severity=warning --format=gcc`). New guard asserts the parity. No status change. |
| `CI-P1-002` | P1 | owner-accepted (no change) | Branch protection / required checks are plan-gated on private GitHub Free; the owner decision is recorded in `docs/security/BRANCH_PROTECTION.md`. Repo-local work cannot change it. |

Statuses map to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI.

## Changes

| File | What changed |
|---|---|
| `automation/validation/tests/ci_governance_guard_test.sh` | New offline, read-only regression guard for all five PS-U03 findings. Runs automatically in `ci/validate.py` (`shell-tests`). |

Scope: a single new test file under `automation/validation/tests/`. No workflow,
`ci/validate.py`, dependency or runtime config was modified. No secrets.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against the branch synced with
`scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U03/verify.log` (commit under test `375c4fb`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 31 shell suites incl. `ci_governance_guard_test.sh`; shellcheck over 173 scripts; secret scan pass |
| `actionlint -color .github/workflows/{validate,dependabot-merge,external-smoke}.yml` | lab `ci-runner` | 0 | `verify.log` — all workflows lint clean (no workflow changed; run for completeness) |
| `shellcheck --severity=warning --format=gcc automation/validation/tests/ci_governance_guard_test.sh` | lab `ci-runner` | 0 | `verify.log` — no findings |
| mutation test: `sed -i s/dependabot-approved/XXremovedXX/ dependabot-merge.yml` then run the guard | lab `ci-runner` | 1 (mutant) / 0 (restored) | `verify.log` — `MUTANT_EXIT=1` (`FAIL: CI-P2-002 ... does not match /dependabot-approved/`), `RESTORED_EXIT=0` |
| `git diff 430da82 HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `no leaks found` (~3,937 bytes scanned) |

- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — one new test file.
- Notes: `lab-sync.ps1` wipes `/srv/work/falcon`; because the extracted repo has
  `core.fileMode=false`, tracked `*.sh` were `chmod +x`'d before the gate. Four
  `docs/phase8/reviews/*.md` files remain reported as modified from the repository's
  pre-existing mixed-EOL blobs (HYG-P2-002); they are unrelated to this patch and not
  part of the diff.

## Evidence bundle

- `remediation/PS-U03/diff.patch` — SHA-256 `8458E94A2E3A748C352745074A809035AA8287B7A3F23C98DB7FA60104A676AF`
- `remediation/PS-U03/verify.log`
- `remediation/PS-U03/manifest.json`
- `remediation/PS-U03/pr_body.md`

## Risk and rollback

- Risk: **low**. The change is a new offline test that only reads repository files; it
  runs in `ci/validate.py` and cannot affect the workflows, deployment or runtime. The
  guarded files are unchanged in this PR.
- Rollback: `git revert 375c4fb13d5ff24b2fa1df2d48565e9ec11f2124`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ test)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] The guard is an acceptable substitute for a live workflow test
- [ ] Rollback is practical

## Open questions / deferred

1. **`CI-P2-002` protected environment (owner/plan).** The finding asks for a protected
   environment around the Dependabot merge job. On private repositories, required
   reviewers and wait timers are only available on higher plans (GitHub Free/Pro/Team
   restrict them to public repos), so this cannot be applied to `MaineCyberTech/falcon`
   on the current plan — the same constraint already accepted for branch protection
   (`docs/security/BRANCH_PROTECTION.md`). The repo-local compensating controls
   (Dependabot-only author, `dependabot-approved` label, green checks) are now guarded on
   top of the existing workflow. Owner action: decide whether to keep the label gate as
   the accepted control, or move to a plan that allows environment protection and then
   add required reviewers to the merge environment.
2. **`CI-P1-002` branch protection (owner-accepted).** No change; remains plan-gated and
   documented.
