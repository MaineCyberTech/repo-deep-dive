# Branch Protection and Required Checks Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repository: `falcon-build` @ `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (`main`; dirty — parallel-session capture) and `falcon-edge-build` @ `f1c5defe6b66887ae49bc44c2cd79b37ad249663` (`main`, clean); only `main` exists in either repo.
- Generated at: 2026-09-30 (audit session)
- Auditor: repo-deep-dive subagent (prompt 34)
- Area code: BP
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/34_branch_protection_required_checks.md`
- Scope limitations: GitHub server-side protection settings cannot be read without API credentials, which this audit did not use; edge documents its own failed API attempts (`docs/GITHUB_CI.md`), falcon documents nothing. No rule was changed (audit-only). Companion: `branch_protection_recommendation.md`.

## Scope

Reviewed: default-branch state, workflow-to-check mapping, PR templates, CODEOWNERS, Dependabot, release/deploy/migration/security workflows, branch/release/hotfix documentation, environment approvals, manual dispatch, workflow risks, and bypass paths for both repos. Not reviewed: server-side ruleset/environment/secret settings beyond in-repo documentation; no GitHub API call was made.

## Evidence Reviewed

- falcon-build: `.github/workflows/validate.yml`, `.github/dependabot.yml`, `AGENTS.md` (rules 4-5), `REPOSITORY.md:12,14,17`, `README.md` CI section; `git branch -a`.
- falcon-edge-build: `.github/workflows/{validate,bake-image,boot-smoke,publish-release,dependabot-merge}.yml`, `.github/dependabot.yml`, `AGENTS.md` (rules 4-7), `REPOSITORY.md:12,17`, `docs/GITHUB_CI.md` (incl. §Plan limitations and releases), `ledgers/risk_register.md` R-012, `ledgers/decision_log.md` D-009, `closeout/OWNER_ACTIONS.md` §9, `closeout/REVIEW-2026-09-30.md`; `git branch -a`.
- Prior run: `/home/user/repo-deep-dive/runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/` — no prior `BP` findings (lens-only run).

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git branch -a` both repos | Reproduced | Branch topology | Only `main` + `origin/main`; no develop/release/hotfix branches |
| `find .github -type f` both repos | Reproduced | Ownership/template presence | No `CODEOWNERS`, no `pull_request_template.md`; only workflows + `dependabot.yml` |
| Every workflow's `on`/`permissions`/`environment`/job names | Reproduced | Required-check mapping | Edge jobs: `tests (3.12)`, `tests (3.13)`, `validate`, `bake`, `boot`, `publish`, `merge`; falcon: `validate` |
| `docs/GITHUB_CI.md` plan-limits table + R-012 | Captured doc | Protection status (edge) | Documents failed API attempts for rulesets/classic protection/env reviewers; marked `documented, not reproducible` (no API access) |
| grep for protection/plan text in falcon docs | Reproduced | Protection status (falcon) | No mention of branch protection, rulesets, or plan limits anywhere |
| Bypass scan: force-push doctrine, `[skip ci]`, workflow-edit path, bot merge | Static walk | Bypass analysis | No enforcement exists to audit; bot merge is the only automated merge path |

## Executive Summary

Neither repository currently enforces branch protection or required checks on `main`. For `falcon-edge-build` this is documented and dated: `docs/GITHUB_CI.md` §Plan limitations records API attempts on 2026-09-30 that returned "Upgrade to GitHub Pro or make this repository public…" for rulesets and classic protection, and "Please ensure the billing plan supports the required reviewers protection rule." for environment reviewers. The repo is private and must stay private (credential-bearing releases), so the plan is the blocker; owner decision R-012 is open. What exists instead: every push runs the full `validate` workflow (failing pushes are visible), Dependabot PRs merge only on green checks (bot sweep), and "no force-push to main" is program doctrine (`AGENTS.md` rule 4, `REPOSITORY.md:12`). `falcon-build` added a static `validate` workflow on 2026-09-30 but documents nothing about protection or plan limits; its status is `Unknown` from the repo.

Because checks are advisory, they are bypassable by design: a direct push to `main` lands regardless of CI; a workflow file can be edited and pushed by any write-capable actor and will run on the next event (on the edge repo, secrets-bearing workflows exist); commit messages can request `[skip ci]`; and there is no bypass audit trail because there are no rulesets. The credential-bearing bake path has an `environment: bake` deployment record but no approver, and `publish-release.yml` has no environment at all, so a release can be dispatched without an owner approval step. There is no CODEOWNERS file, no PR template, and no required review; the daily `dependabot-merge` bot merges Dependabot PRs without human review (deliberate, documented, and a direct consequence of the same plan limit). Recommended next actions: owner resolves R-012 with a GitHub Pro/Team upgrade, applies the companion ruleset (required checks `validate / tests (3.12)`, `validate / tests (3.13)`, `validate / validate` on edge; `validate / validate` on falcon), adds required reviewers to the `bake` environment and a `release` environment, adds CODEOWNERS + PR template, protects release tags, and documents the branch/release/hotfix + break-glass process.

## Prior-Run Finding Status

No `BP` findings existed in the prior run (lens-only run; areas ND/REV/INTG/LIVE). CI-side prior findings are covered in `10_github_actions_cicd_governance.md`.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Default branch | `main` (both) | Integration branch | Only branch; no develop/release/hotfix | P2 | Branch rules for those flows undefined |
| falcon CI checks | `.github/workflows/validate.yml` (`validate`) | Static gates | Present, unproven (see CI report) | P2 | would be the required check if enforced |
| edge CI checks | `.github/workflows/validate.yml` (`tests 3.12`, `tests 3.13`, `validate`) | Tests + static gates + package verify | Live, green in captures | — | natural required-check set |
| PR template | `.github/pull_request_template.md` | Change checklist | Absent (both) | P3 | no evidence/rollback prompts |
| CODEOWNERS | `.github/CODEOWNERS` | Review routing | Absent (both) | P2 | no file-level ownership |
| Dependabot + merge bot | `.github/dependabot.yml` (both); `dependabot-merge.yml` (edge) | Weekly action bumps; bot merge on green | Live (daily cron, `contents: write`) | P2 | no human review; author-restricted |
| Environment | `environment: bake` (edge `bake-image.yml`) | Deployment record | No reviewers (plan) | P2 | R-012 |
| Release | `.github/workflows/publish-release.yml` | Tag/release creation | Dispatch-only, draft default; no environment | P2 | tag not protected |
| Manual dispatch | all edge workflows + falcon validate | Operator trigger | Present; inputs env-passed | P3 | no approval layer |
| Process docs | `AGENTS.md`, `docs/GITHUB_CI.md` (edge) | Rules + CI doc | Doctrine exists; no branch/hotfix/break-glass doc | P2 | edge documents plan limits; falcon none |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Workflows/jobs | 4 | Edge: 5 workflows, pinned, least privilege; falcon: 1 unproven | Checks advisory | Enable ruleset required checks |
| PR templates | 0 | absent in both | No checklist/review prompts | Add template |
| CODEOWNERS | 0 | absent in both | No ownership routing | Add CODEOWNERS + require review |
| Dependabot | 3 | weekly configs; edge merge-on-green live | Bot bypasses human review | Plan upgrade → require review + auto-merge |
| Release/deploy/migration/security workflows | 3 | `publish-release`, `bake-image`, `validate`; deploy scripted | No approval on credential paths | `bake`/`release` environments with reviewers |
| Branch/release/hotfix docs | 1 | `AGENTS.md` doctrine only | No process doc, no break-glass | Add PROCESS/CONTRIBUTING + break-glass |
| Environment approvals | 1 | `environment: bake` | reviewers plan-blocked; publish no env | Upgrade plan; add reviewers |
| Manual dispatch | 3 | dispatch inputs via `env:` | No approval; any write actor | Gate via environments/ruleset perms |
| Workflow risks | 2 | zizmor clean (edge claim); no protection | Unprotected workflow edits; `[skip ci]` | Ruleset + CODEOWNERS on `.github/**` |

## Detailed Review

### Item: Workflow-to-check mapping (what a required check would execute)

- Edge `validate`: `tests (3.12)` = 163-test suite + coverage summary; `tests (3.13)` = 163-test suite; `validate` = actionlint, shellcheck (warning-blocking), ruff, gitleaks, zizmor, upstream drift, `ci/validate.sh` (ledger/evidence/contract/decisions/secret scan), review-package build+verify+upload. Falcon `validate`: actionlint, shellcheck, ruff, gitleaks, zizmor, `ci/validate.py` (parse/pins/ledger/evidence/secret scan); no tests.
- Gap: none are currently *required*; with a ruleset they become the PR merge gate and block direct pushes to `main`.

### Item: Bypass paths and audit trail

- Direct push to `main` (no protection); force-push prevented only by doctrine (`AGENTS.md` rule 4, `REPOSITORY.md:12`); `[skip ci]` can skip push/PR runs; any write actor can edit a workflow and have it run on the next event (secrets exist on edge — `bake-image.yml`); `dependabot-merge.yml` merges without review; no ruleset bypass list exists to audit.
- Fix: active ruleset, no bypass actors except documented owner break-glass, plus audit-log captures on bypass use.

### Item: Environment approvals, manual dispatch, release flow

- `bake-image.yml` sets `environment: bake` (record only; reviewers plan-blocked — `docs/GITHUB_CI.md`, R-012); `publish-release.yml`/`boot-smoke.yml` have no environment; dispatch inputs are passed via `env:`; releases create tags (`sensor-<date>-r<N>` / `lab-*`) with draft defaults. No `CONTRIBUTING`/process doc; break-glass undefined.
- Fix: required reviewers on `bake`, new `release` environment, tag protection, and the process/break-glass doc (BP-P2-001, BP-P3-001/002, companion §Break-glass).

## Scenario / Control Matrix

| ID | Scenario / control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| BP-001 | Workflows/jobs | workflow files | Advisory checks only | No required checks | P1 | Ruleset + required checks |
| BP-002 | PR templates | absence | None | No checklist | P3 | Add PR template |
| BP-003 | CODEOWNERS | absence | None | No ownership/review routing | P2 | Add + require Code Owners |
| BP-004 | Dependabot | configs + merge bot | Weekly bumps; bot merges green PRs | No human review | P2 | Require review post-upgrade |
| BP-005 | Release/deploy/migration/security workflows | `publish-release`, `bake-image`, `validate` | Manual, draft default | No approval on bake/release | P2 | Environments with reviewers |
| BP-006 | Branch/release/hotfix docs | `AGENTS.md` | Doctrine only | Process + break-glass undefined | P3 | Add process doc |
| BP-007 | Environment approvals | `environment: bake` | Record only | Reviewers plan-blocked | P2 | Upgrade + add reviewers |
| BP-008 | Manual dispatch | dispatch triggers | Inputs via `env:` | No approval layer | P3 | Gate via environments |
| BP-009 | Workflow risks | no protection; zizmor | Doctrine + scans | Workflow edits/`[skip ci]`/bot bypass un-audited | P1→P2 | Ruleset + CODEOWNERS + audit-log capture |

## Findings

### Finding ID: BP-P1-001 - Neither `main` is protected; required checks are advisory and bypassable

- Severity: P1 · Confidence: Medium (edge documented; falcon Unknown) · Area: BP
- Evidence: `falcon-edge-build/docs/GITHUB_CI.md` §Plan limitations (API attempts for rulesets, classic protection, env reviewers, auto-merge returned plan-upgrade errors, 2026-09-30); `ledgers/risk_register.md` R-012 (open); no protection/ruleset config or doc in either repo; `git branch -a` shows only `main`; `AGENTS.md` rule 4 / `REPOSITORY.md:12` (no force-push, doctrine only); `.github/workflows/validate.yml` (both).
- What is happening: Checks run on push/PR but nothing blocks a direct or failing push; the documented process ("no force-push", "validate before commit") is not executable as a GitHub rule.
- Why it matters: with write access—including the agent token—a workflow file can be edited and pushed to `main`; on the edge repo that path can reach the seven repository secrets (`bake-image.yml`) or create a release. There is no bypass audit trail.
- User / business impact: release integrity and credential safety depend on operator discipline alone; the program's own independent-review doctrine (AGENTS rule 7) has no enforcement point.
- Security / privacy / reliability impact: P1 CI/CD governance risk; mitigated (not removed) by private access, SHA pins, zizmor/gitleaks, and manual bakes.
- Recommended fix: upgrade to GitHub Pro/Team (owner decision R-012) and apply `branch_protection_recommendation.md`; enforce for admins; keep a documented, owner-only break-glass.
- Suggested validation: a failing PR cannot merge; a direct push to `main` is rejected; a bypass by the owner records an audit-log entry captured as evidence.
- Owner suggestion: owner · Effort estimate: S · Dependencies: GitHub plan upgrade (R-012) · Status: open

### Finding ID: BP-P2-001 - Credential-bearing bake and release paths have no approval gate

- Severity: P2 · Confidence: Medium · Area: BP
- Evidence: `.github/workflows/bake-image.yml` (`environment: bake`, 7 secrets, no reviewers), `.github/workflows/publish-release.yml` (dispatch-only, no `environment`), `docs/GITHUB_CI.md` §Plan limitations, `closeout/OWNER_ACTIONS.md` §9, R-012.
- What is happening: The `bake` environment exists only as a deployment record; required reviewers are plan-blocked; release publishing has no environment at all, so a release can be created by any write+dispatch actor (draft/prerelease by default).
- Why it matters: the image/release contains live credentials; "implementer cannot approve" (edge `AGENTS.md` rule 7) has no enforced approval to attach to.
- User / business impact: unapproved credential use/publication; no separation of duties.
- Security / privacy / reliability impact: elevated blast radius if a token or workflow is abused.
- Recommended fix: on plan upgrade, add required reviewers to `bake` and a new `release` environment (deployment branches = `main`); capture approval records; keep draft-by-default.
- Suggested validation: a dispatch stays "Waiting" until a reviewer approves; a rejected approval aborts the run; records are captured in evidence.
- Owner suggestion: owner · Effort estimate: S · Dependencies: BP-P1-001 (plan) · Status: open

### Finding ID: BP-P2-002 - No CODEOWNERS/PR template/required review; Dependabot bot merges bypass human review

- Severity: P2 · Confidence: High · Area: BP
- Evidence: absence of `.github/CODEOWNERS` and `.github/pull_request_template.md` (`find .github -type f` — only workflows + `dependabot.yml`); `.github/workflows/dependabot-merge.yml` (author `app/dependabot`, `gh pr checks` then `--squash --delete-branch`, `contents: write`); `.github/dependabot.yml` (weekly); `AGENTS.md` rule 7 (doctrine).
- What is happening: No file-level ownership or review requirement; a scheduled bot merges Dependabot PRs when checks are green, with no human disposition.
- Why it matters: action-pin bumps and future dependency updates land unreviewed; workflow-file changes have no ownership gate.
- User / business impact: review trail is missing for automated merges; onboarding lacks a change checklist.
- Security / privacy / reliability impact: a malicious/broken bump could land as long as checks are green; no reviewer for `.github/**`.
- Recommended fix: add CODEOWNERS (owner on `.github/**`, `ci/`, `bootstrap/`, `deploy/`, `secrets/` schemas, `pins/`), a PR template (evidence, rollback, validation), and—after plan upgrade—require Code Owner review + GitHub auto-merge; retire or keep the bot with the same review requirement.
- Suggested validation: PRs touching `.github/**` request owner review; bot merges blocked until review is satisfied; template appears on new PRs.
- Owner suggestion: build-agent + owner · Effort estimate: S · Dependencies: BP-P1-001 for enforcement · Status: open

### Finding ID: BP-P2-003 - falcon-build protection/plan state is undocumented and unverifiable from the repo

- Severity: P2 · Confidence: High (absence reproduced) · Area: BP
- Evidence: no mention of branch protection, rulesets, or plan limits in falcon `AGENTS.md`, `REPOSITORY.md`, `README.md`, or `docs/` (grep); contrast edge `docs/GITHUB_CI.md` §Plan limitations; falcon CI added `6f33a06` has no run evidence (CI-P2-002).
- What is happening: An operator or auditor cannot tell whether falcon `main` is protected, what plan the repo is on, or which checks are intended as required; per shared rules the state is `Unknown` from repo evidence.
- Why it matters: process-vs-actual reconciliation is impossible without a server-side check; the audit cannot mark protection "configured" or "absent".
- User / business impact: governance blind spot on the central monitoring program.
- Security / privacy / reliability impact: undocumented risk ownership around the central repo.
- Recommended fix: record the repo/plan/protection state in `REPOSITORY.md` (or a CI doc) and capture `gh api` output for rules/checks/plan as evidence at each change; mirror the edge documentation pattern.
- Suggested validation: doc matches a fresh API capture; staleness detectable in review.
- Owner suggestion: build-agent + owner · Effort estimate: S · Dependencies: none · Status: open

### Finding ID: BP-P3-001 - Branch/release/hotfix process and break-glass are undefined in both repos

- Severity: P3 · Confidence: High · Area: BP
- Evidence: no `CONTRIBUTING`/process doc; `git branch -a` (only `main`); `AGENTS.md` (change flow, hard rules) and `docs/GITHUB_CI.md` (CI/release naming) cover fragments only; falcon publication flow documented in `AGENTS.md` but no branch/hotfix rules.
- What is happening: Rules for develop/release/hotfix branches, review expectations, and an emergency bypass are not written down; prompt 34 requires main/develop/release/hotfix rules and a defined break-glass.
- Why it matters: incident-time improvisation; new agents cannot tell how to ship a hotfix legitimately.
- User / business impact: slower, riskier emergency changes; ambiguous review expectations.
- Security / privacy / reliability impact: bypass decisions would be unrecorded.
- Recommended fix: add a short process doc (or AGENTS section): main-only integration; releases via tags + `publish-release`; hotfix via expedited PR to `main` with post-hoc review; break-glass = owner-only, ≤24 h, decision-log entry + post-hoc review + captured audit-log entry.
- Suggested validation: a tabletop hotfix walkthrough follows the doc; break-glass record exists for a real drill.
- Owner suggestion: owner + build-agent · Effort estimate: S · Dependencies: BP-P1-001 for enforcement · Status: open

### Finding ID: BP-P3-002 - Release tags are unprotected; `publish-release` can create tags without approval

- Severity: P3 · Confidence: Medium (plan-limited) · Area: BP
- Evidence: `.github/workflows/publish-release.yml` (`gh release create "$TAG"` with dispatch inputs, drafts by default); `docs/GITHUB_CI.md` release naming (`sensor-<date>-r<N>`, historical `lab-*`); plan limits block tag rules.
- What is happening: Any write+dispatch actor can create a release tag and assets; there is no tag immutability or creation restriction.
- Why it matters: tag spoofing or accidental publication; releases are credential-bearing and are the durable delivery point.
- User / business impact: a wrong/duplicate release can be published (draft default limits exposure).
- Security / privacy / reliability impact: release integrity depends on operator care.
- Recommended fix: on plan upgrade, add a tag ruleset for `sensor-*`/`lab-*` (restrict creation/updates/deletes to owner) and require the `release` environment from BP-P2-001.
- Suggested validation: a non-owner tag push is rejected; release creation requires approval; tags immutable after publish.
- Owner suggestion: owner · Effort estimate: S · Dependencies: BP-P1-001 · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unprotected `main`; workflow edits can reach secrets/releases | P1 | Medium | High | BP-P1-001, R-012 | Plan upgrade + ruleset + env reviewers |
| Unapproved credential-bearing bake/release | P2 | Medium | High | BP-P2-001 | `bake`/`release` environments with reviewers |
| Unreviewed automated merges / no ownership | P2 | Medium | Medium | BP-P2-002 | CODEOWNERS + required review |
| Protection state undocumented (falcon) | P2 | High | Medium | BP-P2-003 | Document + capture API evidence |
| Hotfix/break-glass improvised; tag/release spoofing or error | P3 | Low–Medium | Medium | BP-P3-001/002 | Process doc; tag ruleset + approval |

## Recommendations

### Immediate / Release Blocking

- Resolve R-012: owner upgrades to GitHub Pro/Team; apply the companion `branch_protection_recommendation.md` to both repos before the next credential-bearing bake/release.

### This Week

- Add CODEOWNERS + PR template (BP-P2-002) and document falcon protection state (BP-P2-003).
- Define branch/release/hotfix + break-glass process (BP-P3-001).

### This Month

- Enable required checks + required reviews; add `bake` reviewers and the `release` environment (BP-P1-001, BP-P2-001).
- Protect release tags; retire or constrain `dependabot-merge` under the review requirement (BP-P3-002, BP-P2-002).

### Later / Platform Evolution

- Keep ruleset-as-code snapshots (API captures) in `evidence/`; revisit OIDC if a cloud target appears; periodic protection audit in the full run.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add CODEOWNERS for `.github/**`, `ci/`, `deploy/`, `pins/` | Ownership routing without a plan upgrade | `.github/CODEOWNERS` (new, both) | review requests appear on PRs |
| Add PR template with evidence/rollback checklist | Consistent change discipline | `.github/pull_request_template.md` (new, both) | template shows on new PRs |
| Document falcon protection/plan state | Removes `Unknown` | `REPOSITORY.md` or new CI doc | doc matches API capture |
| Write the break-glass paragraph | Makes bypass auditable | `AGENTS.md`/process doc | tabletop walkthrough |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Plan upgrade + ruleset (required checks/reviews/linear history) | P1 | owner | S | R-012 decision |
| `bake` + `release` environment reviewers | P2 | owner | S | plan upgrade |
| CODEOWNERS/PR template + required Code Owner review | P2 | build-agent | S | plan upgrade for enforcement |
| Required checks for edge (`tests 3.12/3.13`, `validate`) and falcon (`validate`) | P1 | owner | S | ruleset |
| Tag protection + release approval | P3 | owner | S | plan upgrade |
| Branch/release/hotfix + break-glass doc | P3 | owner + build-agent | S | none |

## Suggested Tests

- **CI/unit:** a scripted check that ruleset/repo settings match `branch_protection_recommendation.md` (API read → compare), run in the weekly validate schedule.
- **Integration/E2E:** push a deliberately failing commit/PR and confirm it cannot merge; confirm a red PR cannot be admin-merged.
- **Security:** attempt a `[skip ci]` push to `main` in a sandbox; confirm workflow-file changes require Code Owner review; confirm `dependabot-merge` skips PRs lacking review after the upgrade.
- **Regression/manual:** after each plan or settings change, re-capture `gh api` output and diff against the previous snapshot; owner-run drill of the break-glass path (time-boxed, recorded, post-hoc reviewed).

## Suggested Documentation Updates

- New `branch_protection_recommendation.md` (this run) — apply and keep linked from both repos.
- `REPOSITORY.md` (both): branch rules, required checks, protection status/plan, break-glass.
- `AGENTS.md` (both): pointer to the process doc; explicit "protection may be absent; do not rely on CI to block".
- `docs/GITHUB_CI.md` (edge): update the plan-limits section to link this audit and note current status.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Owner decision on R-012 (upgrade vs accept) | Determines all remediation paths | Owner statement; decision-log entry |
| Is falcon on GitHub Free like edge? | Whether rulesets are available | `gh api` capture / owner |
| Who holds write access (users/tokens)? | Bypass exposure | Org member/role list (owner) |

## Appendix

### Required-check mapping (recommended)

| Repo | Workflow / job check name | What it executes | Recommend required |
|---|---|---|---|
| falcon | `validate / validate` | actionlint, shellcheck, ruff, gitleaks, zizmor, `ci/validate.py` | yes (once exercised) |
| edge | `validate / tests (3.12)` | 163 tests + coverage summary | yes |
| edge | `validate / tests (3.13)` | 163 tests | yes |
| edge | `validate / validate` | linters, drift check, `ci/validate.sh`, review-package verify | yes |

### Edge cases (bake / boot / publish / merge)

- These are manual/triggered, not PR checks: `bake-image / bake` (credential build; env-gated), `boot-smoke / boot` (QEMU; run before release), `publish-release / publish` (release; env-gated), `dependabot-merge / merge` (scheduled; no bypass actor).

### Break-glass (recommended definition)

- Who: repository owner only (no bots, no agent tokens). When: production-impacting incident where the normal PR/check flow cannot be used. How: owner bypasses the ruleset; decision-log entry same day; post-hoc review within 48 h.
- Evidence: GitHub audit-log entry captured into `evidence/raw/`; bypass list limited to the owner; `dependabot-merge` must never be a bypass actor; quarterly review of bypass use.
