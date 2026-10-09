# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (private)
- Branch: `main`
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:40Z
- Auditor: subagent (read-only)
- Area code: CI
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/10_github_actions_cicd_governance.md
- Scope limitations: repository inspection + read-only GitHub API reads (token from `/home/user/.env`, never printed). No workflow was dispatched or executed; no file in the target repo or on the host was modified. Host-level runner state was inferred from captured workflow logs and a throwaway probe run from 2026-10-04 (the probe workflow itself is no longer on any branch).

## Scope

Reviewed: `.github/workflows/{validate,external-smoke,dependabot-merge}.yml`, `.github/{CODEOWNERS,dependabot.yml,pull_request_template.md,actionlint.yaml}`, `ci/*` (validate.py, license_check.py, requirements-ci.txt, preflight.sh), `automation/validation/*` gate scripts invoked by CI, `docs/security/{BRANCH_PROTECTION,CI_GOVERNANCE_RECONCILIATION,CI_CD_INCIDENT_PLAYBOOK,CI_TOOL_PINS,CI_SECRET_GATE,SBOM_COVERAGE_AND_PROVENANCE}.md`, and live GitHub server state (workflow runs 2026-09-30..2026-10-09, workflow registry, permissions settings, environments, labels, branches, PRs). Not reviewed: the `falcon-edge` repository's workflows (out of scope; referenced only), org-level runner-group configuration (needs org admin), GitHub billing state (inferred from job outcomes).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github/workflows/validate.yml` | workflow | main PR/push/schedule gate | 140 lines; SHA-pinned actions; hash-pinned tools; SBOM/publication steps |
| `.github/workflows/dependabot-merge.yml` | workflow | auto-merge of Dependabot PRs | `contents: write` + `pull-requests: write`; label gate; self-hosted |
| `.github/workflows/external-smoke.yml` | workflow | public-surface/Access smoke | moved to lab runner (70292a0) and weakened (08e20d1) |
| `ci/validate.py`, `ci/requirements-ci.txt`, `ci/license_check.py` | gate code | what the single CI job actually executes | 21 checks, 50 shell suites |
| `docs/security/BRANCH_PROTECTION.md`, `CI_GOVERNANCE_RECONCILIATION.md`, `CI_CD_INCIDENT_PLAYBOOK.md`, `CI_TOOL_PINS.md` | docs | declared governance vs actual | playbook §8 and SBOM doc are stale |
| GitHub API: `actions/workflows`, `actions/permissions`, `actions/permissions/workflow`, runs/jobs/check-runs, `codeowners/errors` | live state | server-side truth | read-only GETs on 2026-10-09 |
| Workflow runs 37985725668, 37985746101, 37986933263, 37986216737, 37985520606, 37966546614, 37662354033, 37820256218, 37189467074 | run logs | reproduction/verification | logs and job metadata fetched read-only |
| Commits `70292a0b`, `08e20d1a` | git | today's CI changes | external-smoke runner + assertion change |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| `validate` runs and passes at HEAD | GitHub run 37985725668 (push, 08e20d1) | supported: completed success; all steps green |
| `validate` is a real fail-closed gate | PR #49 runs 37986933263 / 37986216737 | supported: step 12 failed with `validation_failures=1` (6 unindexed evidence artifacts) |
| Hosted runners are billing-blocked | jobs 37662354033, 37820256218, 37966546614 on `ubuntu-latest` | supported: 0 steps, empty runner name, 2 s duration (job never started) |
| external-smoke now passes on an owner-IP Access bypass | run 37985746101 job 114007177637 log | supported: `OK https://iris... -> 302 (owner-IP Access bypass; origin reachable)`; summary still claims `cloudflareaccess.com` |
| Same-repo PR code runs on a sudo-capable runner | probe run 37189467074 job 111398447974 (`edge-builder`) | supported at 2026-10-04: `SUDO_OK`, `/usr/bin/docker`; `ci-runner` job 111398448046 showed `SUDO_NO` |
| Prior CI-P2-001 still open | `dependabot-merge.yml:17-19,48` | supported: write scopes, no environment, no `--match-head-commit` |
| Branch protection still plan-gated | API GET protection + rulesets | supported: both 403 "Upgrade to GitHub Pro..." on 2026-10-09 |
| Local gate subset green | `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only ...` | supported: `validation_failures=0` |
| Three extra workflows registered | API `actions/workflows` (7 total) vs `git for-each-ref` | supported: `lab-probe`, `lab-pwsh-probe`, `testnuc-runner-verify` have no file on any live ref |

## Executive Summary

The committed workflow set is small and deliberately hardened: 3 workflows, SHA-pinned actions, hash-pinned CI tooling (`ci/requirements-ci.txt`), gitleaks tree + full-history scans, zizmor, actionlint, and a single `validate` job that runs 21 checks and 50 offline shell suites. The gate demonstrably works (PR #49 is currently red on a real evidence-index finding). This is a strong baseline for a single-owner private repo.

The dominant risks are now runner-related, not YAML-related. Every same-repo `pull_request` (including Dependabot PRs, which modify workflow files by design) executes on the self-hosted `edge-builder` runner, whose service account has passwordless sudo (probe evidence 2026-10-04) and docker — so pre-review PR code has root-equivalent reach on a lab host. The repository's Actions defaults are permissive (`default_workflow_permissions: write`, PR approvals allowed, `allowed_actions: all`, `sha_pinning_required: false`). The `external-smoke` monitoring gate was neutered today (it now passes on an owner-IP Access bypass and still claims to assert Cloudflare Access), and GitHub-hosted runner jobs silently never started for three days because hosted runners are billing-blocked; fork PRs and scheduled runs therefore get no signal and there is no failure notification. Three throwaway probe workflows remain registered/active although no workflow file exists on any live branch.

Immediate actions: move PR jobs to the non-sudo runner (or remove sudo), set read-only default token permissions, fix or rescope external-smoke, and add failure notification for scheduled workflows.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| validate | `.github/workflows/validate.yml` | push/PR/dispatch/weekly static gate | functional, green at HEAD | Medium (runner) | 21 checks + 50 suites; `contents: read` |
| dependabot-merge | `.github/workflows/dependabot-merge.yml` | daily Dependabot sweep | configured, unexercised | Medium | `contents: write`; label gate; no `--match-head-commit` |
| external-smoke | `.github/workflows/external-smoke.yml` | public surface/Access smoke | degraded | Medium | passes on bypass; comments/summary stale |
| CI deps | `ci/requirements-ci.txt` | pyyaml + zizmor | hash-pinned | Low | `--require-hashes` |
| Tool downloads | validate.yml steps | actionlint/shellcheck/ruff/gitleaks | SHA-256 verified | Low | `--fail`, retry 3 |
| Secret scans | validate.yml:69-85 | tree + history gitleaks | fail-closed | Low | `fetch-depth: 0` |
| SBOM gate | validate.yml:103-106 | coverage + hashes + vuln waivers | enforced | Low | `--require-vuln --vuln-waivers` |
| Publication gate | validate.yml:108-113 | chain + digest/verdict consistency | enforced | Low | fails closed |
| Workflow registry | GitHub API | 7 workflows listed | drift | Low | 3 probe workflows have no file |
| Actions settings | GitHub API | default token write; all actions; no SHA requirement | permissive | Medium | latent footgun |
| Environments | GitHub API | 0 environments | absent | Low | no environment protection anywhere |

## Findings

### Finding ID: CI-P1-002 (new, ID provisional) - Same-repo PR workflows execute on a passwordless-sudo self-hosted runner

- Severity: P1
- Confidence: Medium-High (routing reproduced live; sudo state captured 2026-10-04 and not re-probed)
- Area: CI
- Evidence:
  - `.github/workflows/validate.yml:26-28` (`runs-on` sends same-repo PRs and all push/schedule/dispatch runs to `["self-hosted","linux","x64","lab-python"]`)
  - GitHub run 37986933263 (PR #49 `pull_request`): job started on runner `edge-builder`
  - Probe run 37189467074 job 111398447974 (`edge-builder`): log lines `Runner name: 'edge-builder'`, `SUDO_OK`, `/usr/bin/docker`; job 111398448046 (`ci-runner`) showed `SUDO_NO`
  - `.github/workflows/dependabot-merge.yml:27` (also self-hosted); `.github/workflows/external-smoke.yml:26` (moved to lab runner in commit `70292a0b`)
  - `docs/security/CI_CD_INCIDENT_PLAYBOOK.md:34` (the same lab runner group serves the credential-bearing edge bake path)
- What is happening: GitHub evaluates `pull_request` workflows from the PR's merge commit, so a same-repo PR that edits `.github/workflows/**` executes the edited workflow on the lab runner before any human review. Dependabot's weekly `github-actions` updates are exactly such PRs (they change pinned action SHAs in `validate.yml`). The `edge-builder` runner service account has passwordless sudo and docker on that host.
- Why it matters: a compromised upstream action, a malicious PR branch from a collaborator/agent, or a tampered Dependabot PR turns into arbitrary code execution with root-equivalent privilege on a lab host that builds credential-bearing edge images. `contents: read` does not contain this: sudo and docker do.
- User / business impact: potential host compromise in the lab that produces the monitoring/edge artifacts; blast radius extends beyond this repository.
- Security / privacy / reliability impact: CI/CD supply-chain foothold; secrets present on the runner host (or reachable through docker/sudo) are at risk.
- Recommended fix: run PR jobs on the non-sudo `ci-runner` (add a `lab-python-nosudo` label there) or an ephemeral runner; remove passwordless sudo from the runner service account; restrict the org runner group to selected workflows; keep fork PRs off the lab; add a regression check that asserts `sudo -n true` fails on PR runners.
- Suggested validation: a test PR that tries `sudo -n true` must fail; `gh api .../actions/runs/<id>/jobs` shows `ci-runner` for `pull_request`; re-run the probe after any runner change.
- Owner suggestion: platform/CI owner (owner-gated: org runner group + runner host config).
- Effort estimate: M
- Dependencies: org runner-group access; runner host admin.
- Status: open

### Finding ID: CI-P2-001 (prior, still-open) - Auto-merge workflow holds `contents: write` with no environment protection

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/dependabot-merge.yml:17-19` (`permissions: contents: write, pull-requests: write`)
  - `.github/workflows/dependabot-merge.yml:27` (self-hosted `lab` runner), `:46-48` (checks green -> `gh pr merge --squash --delete-branch`, no `--match-head-commit`)
  - `docs/security/BRANCH_PROTECTION.md:95` (label gate is the human disposition; environment reviewers plan-blocked)
  - API: environments `total_count: 0` (no environment protection exists)
- What is happening: the daily sweep runs with a write-capable `GITHUB_TOKEN` on a self-hosted runner and merges without pinning the verified head commit. A push between `gh pr checks` and `gh pr merge` would merge unverified code; the token's write scope is broader than the task needs.
- Why it matters: the compensating control (owner label + green checks) can be defeated by a TOCTOU push; the workflow concentrates write scope on a runner that also executes PR code (see CI-P1-002).
- User / business impact: unreviewed or unverified code can land on `main`.
- Security / privacy / reliability impact: integrity of `main` depends on a non-atomic check-then-merge sequence.
- Recommended fix: add `--match-head-commit "$(gh pr view ... --json headRefOid)"`; reduce to `contents: write` + `pull-requests: read` (verify the minimum `gh` needs); add an environment with required reviewers when the plan allows, or convert the merge to an owner-run `workflow_dispatch`.
- Suggested validation: a fixture/regression test asserting the merge command includes `--match-head-commit` and that the declared permissions contain no unused write scope.
- Owner suggestion: CI owner.
- Effort estimate: S
- Dependencies: none (plan-gated piece optional).
- Status: still-open (prior CI-P2-001; recommendation not implemented)

### Finding ID: CI-P2-002 (new, ID provisional) - external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass

- Severity: P2
- Confidence: High (run log captured at HEAD)
- Area: CI
- Evidence:
  - `.github/workflows/external-smoke.yml:3-6` ("from GitHub's network ... gated by Cloudflare Access (302 -> cloudflareaccess.com)")
  - `.github/workflows/external-smoke.yml:23-26` (comment says "Must run from GitHub's network ... so it stays on hosted"; actual `runs-on: [self-hosted, lab]`, commit `70292a0b`)
  - `.github/workflows/external-smoke.yml:37-42` (any 302 is now `OK`, including `owner-IP Access bypass`, commit `08e20d1a`)
  - `.github/workflows/external-smoke.yml:64-67` (summary still says "must be 302 to cloudflareaccess.com (Access still enforcing)")
  - Run 37985746101 job 114007177637 log: `OK https://iris.mainecybertech.us/ -> 302 (owner-IP Access bypass; origin reachable)` and the same for `soc`; job conclusion `success`
  - Commit `08e20d1a` message claims "Access posture is verified externally" - no in-repo artifact of that external verification found (grep of `docs/`, `evidence/`)
- What is happening: the gate runs from the lab vantage (where the owner IP bypasses Access) and accepts any 302, so it can no longer distinguish "Access enforcing" from "Access bypassed for this source". The artifact still asserts the stronger claim.
- Why it matters: an accidental removal/misconfiguration of Cloudflare Access on `iris`/`soc` would no longer be detected; the job summary misstates what was verified (self-inconsistent artifact).
- User / business impact: loss of the only automated Access-posture check for the public hostnames.
- Security / privacy / reliability impact: reduced detection for a public exposure regression.
- Recommended fix: either restore an external vantage (an external monitor or the DigitalOcean forwarder with an alert; hosted runners are billing-blocked) or rescope the workflow to "origin reachability" and record/link where Access posture is verified externally; update the header comment and summary text to match the check; add the Access assertion as a required external check when possible.
- Suggested validation: a canary that removes/bypasses Access for a test hostname must fail the check; the summary text must match the assertion logic.
- Owner suggestion: CI owner + Cloudflare/Access owner.
- Effort estimate: S-M
- Dependencies: external vantage (DO host or monitor) for the strong assertion.
- Status: open (regression introduced 2026-10-09)

### Finding ID: CI-P2-003 (new, ID provisional) - Repository Actions settings default to permissive

- Severity: P2
- Confidence: High (live API)
- Area: CI
- Evidence:
  - API `GET /repos/MaineCyberTech/falcon/actions/permissions` -> `{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}`
  - API `GET /repos/MaineCyberTech/falcon/actions/permissions/workflow` -> `{"default_workflow_permissions":"write","can_approve_pull_request_reviews":true}`
  - Current workflows all declare permissions (`validate.yml:17-18`, `external-smoke.yml:14-15`, `dependabot-merge.yml:17-19`), so the default is latent, not currently exercised
- What is happening: a new workflow without a `permissions:` block gets a read-write token by default; Actions can create/approve PRs; any marketplace action is allowed; server-side SHA-pin enforcement is off (the repo pins manually).
- Why it matters: one forgotten `permissions:` block silently grants write scope on a self-hosted runner; Actions approving its own PRs undermines the review boundary the owner relies on.
- User / business impact: latent privilege escalation surface for future workflow changes.
- Security / privacy / reliability impact: default-deny should replace default-allow for tokens and actions.
- Recommended fix: set default workflow permissions to `read`; disable "Allow GitHub Actions to create and approve pull requests"; consider `allowed_actions: selected` and `sha_pinning_required: true`.
- Suggested validation: `gh api .../actions/permissions/workflow` returns `read`/`false`; a workflow with no permissions block shows a read-only token in its run log.
- Owner suggestion: repo admin (owner).
- Effort estimate: S
- Dependencies: none.
- Status: open

### Finding ID: CI-P3-001 (new, ID provisional) - Hosted-runner dependency is dead and scheduled-workflow failures are silent

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - Scheduled `external-smoke` jobs 37662354033 (2026-10-07), 37820256218 (2026-10-08), 37966546614 (2026-10-09): `labels: [ubuntu-latest]`, `runner_name: ""`, `steps: []`, ~2 s duration - the job never started
  - `.github/workflows/validate.yml:26-28` (fork PRs still fall back to `ubuntu-latest`, so fork PRs get no validation)
  - `.github/workflows/external-smoke.yml:26` comment ("GitHub-hosted is billing-blocked")
  - No failure-notification wiring in any workflow (grep: no `ntfy`/notify step); `automation/alerting/ntfy_relay.py` only relays Grafana webhooks; `docs/security/CI_CD_INCIDENT_PLAYBOOK.md:239-249` detection is manual
- What is happening: workflows that assumed GitHub-hosted runners silently fail to start, and nothing alerts on a failed scheduled run. The gate was effectively dead for 3 days until an operator noticed.
- Why it matters: silent gate death is indistinguishable from a green system; fork PRs never get validated at all.
- User / business impact: false confidence in monitoring/validation coverage.
- Security / privacy / reliability impact: monitoring blind spot.
- Recommended fix: remove or replace the hosted fallback (document the fork-PR policy explicitly); add a failure notification path (e.g., a small workflow step posting to the existing ntfy relay, or a Prometheus textfile metric from a scheduled self-check + alert).
- Suggested validation: force a failing scheduled run and confirm a notification arrives; confirm a fork PR either validates or is documented as out of scope.
- Owner suggestion: CI owner.
- Effort estimate: S
- Dependencies: ntfy relay credentials (already provisioned).
- Status: open

### Finding ID: CI-P3-002 (new, ID provisional) - Three probe workflows remain registered/active with no file on any branch

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - API `actions/workflows`: 7 entries, including `lab-probe` (`id 374465077`, path `.github/workflows/lab-probe.yml`, state `active`), `lab-pwsh-probe` (`374566273`), `testnuc-runner-verify` (`374995041`, path `.github/workflows/testnuc-verify.yml`)
  - `git for-each-ref` over all live refs: only `validate.yml`, `external-smoke.yml`, `dependabot-merge.yml` exist
  - Runs: 37189693050/37189467074/37189140946 (`probe/lab-toolchain`), 37200695034 (`probe/pwsh-lab`), 37252867449/37252237591 (`ci-verify-testnuc`); branches now deleted
  - Fetched probe files by SHA: throwaway diagnostics; `testnuc-verify.yml` uses unpinned `actions/setup-python@v5` and ran on `tn-*` self-hosted labels
- What is happening: diagnostic workflows pushed to short-lived branches were registered in the repo's Actions list and remain `active` after their branches were deleted. The repo tree and docs describe 3 workflows.
- Why it matters: the Actions inventory no longer matches the repository; stale registrations can confuse incident response and (if the file reappears on a branch) trigger on push. The probes also demonstrate that any writer can execute arbitrary code on lab runners via a branch push.
- User / business impact: governance/inventory drift; small operational confusion.
- Security / privacy / reliability impact: low by itself; reinforces CI-P1-002.
- Recommended fix: clean up the stale registrations (recreate+delete the workflow files via a temporary branch, or ask GitHub support); keep diagnostic probes out of the persistent repo; add an inventory assertion comparing the API workflow list to the tree.
- Suggested validation: `gh api .../actions/workflows` returns exactly the three canonical workflows.
- Owner suggestion: CI owner.
- Effort estimate: S
- Dependencies: none.
- Status: open

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

| Prior finding | Prior status | Current verification | Disposition |
|---|---|---|---|
| CI-P1-001 Branch protection/required checks not enforced server-side | owner-accepted | API protection + rulesets both 403 "Upgrade to GitHub Pro" on 2026-10-09; owner decision to stay on Free unchanged (`BRANCH_PROTECTION.md:75-80`) | still owner-accepted; not re-filed |
| CI-P2-001 Auto-merge `contents: write`, no environment protection | still-open | `dependabot-merge.yml:17-19,48` unchanged (no `--match-head-commit`, no environment) | re-filed as CI-P2-001 |
| CI-P2-002 residual "no captured falcon validate run" / CI unexercised | open (from 2026-10-02 reconciliation) | validate ran green on push at HEAD (37985725668) and red on PR #49 (37985733263) | closed by observation |
| CI-P3-002 residual "tool downloads unverified / unpinned Python" | partial | all downloads SHA-256 verified; `ci/requirements-ci.txt` hash-pinned (validate.yml:40-41) | fixed at this commit |
| CI-P3-001 docs-vs-records drift | partial | playbook §8 still says "only gitleaks is SHA-256-pinned" and "no captured validate run"; SBOM doc still says `--require-vuln` is off | still open (documentation) |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| PR code executes with sudo on lab runner | High | Low-Medium | Host compromise | validate.yml:28; probe SUDO_OK; run 37986933263 | move to non-sudo runner; drop sudo |
| Auto-merge TOCTOU / broad write token | Medium | Low | Unverified code on main | dependabot-merge.yml:46-48 | `--match-head-commit`; minimal scopes |
| Access-posture regression undetected | Medium | Medium | Public exposure regression | external-smoke.yml:37-42; run 37985746101 | restore external vantage; fix summary |
| Silent gate death (hosted block) | Medium | High | False confidence | jobs with 0 steps | failure notification; remove hosted dependency |
| Permissive Actions defaults | Medium | Low | Future workflow privilege | API settings | read-only default; disable PR approvals |
| Stale workflow registrations | Low | Medium | Inventory drift | API 7 vs tree 3 | clean up; inventory check |

## Recommendations

### Immediate / Release Blocking
- CI-P1-002: move `pull_request` jobs to the non-sudo runner (or remove the sudo grant) before accepting further PR-based workflow changes.

### This Week
- CI-P2-001: add `--match-head-commit`; scope permissions to the minimum.
- CI-P2-002: fix or rescope external-smoke; correct the comments/summary; record where Access posture is actually verified.
- CI-P2-003: set read-only default token permissions; disable Actions PR approval.

### This Month
- CI-P3-001: failure notification for scheduled workflows; document the fork-PR policy.
- CI-P3-002: clean up stale workflow registrations; add an inventory assertion.

### Later / Platform Evolution
- Consider org runner groups restricted to selected workflows; ephemeral runners; `allowed_actions: selected` + `sha_pinning_required: true`.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `--match-head-commit` in the merge step | removes the TOCTOU window | dependabot-merge.yml | grep/regression test |
| Read-only default workflow permissions | default-deny for future workflows | repo settings (API/UI) | API returns `read` |
| Fix external-smoke summary text | artifact stops contradicting the check | external-smoke.yml:64-67 | run log matches assertion |
| Add ntfy failure step | scheduled failures become visible | workflows + relay | forced-failure notification |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Non-sudo/ephemeral PR runners | P1 | platform | M | org runner group |
| Signed commits / required checks after plan upgrade | P2 | owner | S | GitHub Pro (owner decision) |
| Workflow inventory API-vs-tree check | P3 | CI owner | S | none |

## Suggested Tests

- CI regression: assert `dependabot-merge.yml` contains `--match-head-commit` and no unused write scope (`automation/validation/tests/ci_governance_guard_test.sh` already guards other CI-P2-002 properties).
- Runner isolation test: a PR job asserts `sudo -n true` fails on the PR runner label.
- external-smoke canary: a known bypass URL must fail the strong assertion.
- Scheduled-workflow watchdog: force one failed run and assert a notification/metric.

## Suggested Documentation Updates

- `docs/security/CI_CD_INCIDENT_PLAYBOOK.md` §1 and §8: external-smoke now runs from the lab vantage; tool pins are applied; a validate run has been captured; add the runner-sudo residual.
- `docs/security/CI_GOVERNANCE_RECONCILIATION.md`: append the 2026-10-09 state (runners, permissions defaults, probe registrations).
- `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md`: `--require-vuln` is now enforced with waivers (append-only update).
- `README.md` CI section: runner topology (lab runners, billing-blocked hosted).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which runner group(s) can access this repo's runners, and do other repos (falcon-edge bake) share them? | blast radius of CI-P1-002 | org runner-group settings (org admin) |
| Was sudo removed from `edge-builder` after 2026-10-04? | severity of CI-P1-002 today | re-probe or runner host config |
| Where is the "external" Access-posture verification the 08e20d1 commit claims? | CI-P2-002 remediation | monitor config / evidence capture |

## Limitations

- Read-only audit: no workflow was dispatched; runner state is inferred from captured logs (probe dated 2026-10-04).
- Org-level settings (runner groups, billing, org plan) were not accessible.
- Logs are untrusted data; only their factual content was used as evidence.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P1-001 | P1 | Same-repo PR workflows execute on a passwordless-sudo self-hosted runner |
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection |
| CI-P2-002 | P2 | external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass |
| CI-P2-003 | P2 | Repository Actions settings default to permissive (write token, PR approvals, any action, no SHA-pin requirement) |
| CI-P3-001 | P3 | Hosted-runner dependency is dead and scheduled-workflow failures are silent |
| CI-P3-002 | P3 | Three probe workflows remain registered/active with no file on any branch |
