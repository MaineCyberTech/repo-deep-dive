# 34_branch_protection_required_checks — Prompt 34 - Branch Protection and Required Checks Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `34_branch_protection_required_checks.md` (area BP, prompt)

## Verification Performed

# Branch Protection and Required Checks Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (private, org-owned)
- Branch: `main`
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:31Z
- Auditor: subagent (read-only)
- Area code: BP
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/34_branch_protection_required_checks.md
- Scope limitations: repository + read-only GitHub API. Branch protection/rulesets cannot be applied or read on the current plan (403 verified). No settings were changed. Org-level rulesets/settings were not accessible.

## Scope

Reviewed: all three workflows and their check names, `.github/CODEOWNERS`, `.github/pull_request_template.md`, `.github/dependabot.yml`, `docs/security/{BRANCH_PROTECTION,BREAK_GLASS_CUSTODY}.md`, and live server state: branch protection/rulesets (403), environments (0), labels, PRs (54), check-runs for f5cb7c9 and PR #54, codeowners errors. Not reviewed: org-level settings, the `falcon-edge` workflows, and the actual apply of the ready payload (plan-gated).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| GitHub API `branches/main/protection`, `rulesets` | live state | server-side enforcement truth | both 403 'Upgrade to GitHub Pro...' on 2026-10-11 |
| GitHub API `environments` | live state | environment approvals | total_count 0 |
| GitHub API `codeowners/errors` | live state | CODEOWNERS validity | 6 errors, all 'Unknown owner' |
| GitHub API `labels`, `pulls`, `check-runs` | live state | label gate, PR inventory, check names | no `dependabot-approved`; 0 dependabot PRs of 54; check name 'validate' |
| `.github/CODEOWNERS`, `.github/dependabot.yml`, `.github/pull_request_template.md` | repo | ownership/update controls | CODEOWNERS invalid; 2 ecosystems (actions + pip) |
| `.github/workflows/*.yml` | repo | required-check candidates | validate (job `validate`), external-smoke (`smoke`), dependabot-merge (`merge`) |
| `docs/security/BRANCH_PROTECTION.md` | repo | declared process + enforcement matrix | target payload, matrix, break-glass, hotfix walkthrough |
| `docs/security/BREAK_GLASS_CUSTODY.md` | repo | break-glass custody | OD-04 still PENDING (custodian not named) |
| Runs 38110410254 (validate@f5cb7c9), 38109789930 (PR #54 head, red), 38047609916 (sweep) | live runs | exercise evidence | validate red at PR #54 head; sweep 'no open dependabot PRs' |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| Branch protection is still plan-gated | GET protection, GET rulesets (2026-10-11) | supported: both 403 'Upgrade to GitHub Pro or make this repository public' |
| Owner decision is 'stay on Free' | `BRANCH_PROTECTION.md:75-80` | supported (documented; no change found) |
| Required-check candidate is `validate` | check-runs API for f5cb7c9 and PR #54 head | observed name: `validate` (docs use `validate / validate` - naming question remains) |
| CODEOWNERS resolves | `codeowners/errors` API | unsupported: 6 `Unknown owner` errors (lines 7,10-14) |
| Dependabot label gate works | labels + PR inventory + sweep log | configured, never exercised: label absent, 0 Dependabot PRs ever |
| Environment approvals exist | environments API | unsupported: 0 environments |
| Bypass is possible and its audit is manual | PR #54: head check-run `validate` = failure, merged 2026-10-11T03:53Z by the owner with 0 reviews/0 comments; no decision-log row for 2026-10-11 found | supported: a red advisory check did not block the merge; the matrix's 'bypass audit trail: No; break-glass use is recorded manually' remains the accurate statement |
| Break-glass process documented | `BRANCH_PROTECTION.md:56-172`; `BREAK_GLASS_CUSTODY.md` | supported; custody designation (OD-04) still pending |
| Prior BP-P1-001 unchanged | API + doc | supported: still plan-gated, owner-accepted |

## Executive Summary

The branch/release/hotfix process remains documented unusually well for a single-owner repo: a ready-to-apply protection payload, a precise enforcement matrix that states what is and is not enforced, a hotfix walkthrough, and a break-glass record template. Server-side enforcement is still impossible on the private GitHub Free plan (protection and rulesets both 403 on 2026-10-11), and the owner has explicitly accepted that (BP-P1-001 owner-accepted; CI-P1-001 same root cause). This audit verified the accepted status rather than re-filing it, and captured a live instance of the accepted residual: PR #54 was merged 19 seconds after its `validate` check had failed (the publication-equality gate was red until the post-merge rebind at f5cb7c9), with no review record and no 2026-10-11 decision-log row.

Two compensating-control gaps remain current and fixable. (1) `.github/CODEOWNERS` is entirely invalid - all six entries use the bare org handle `@MaineCyberTech`, which GitHub reports as `Unknown owner`, so sensitive paths (`.github/`, `ci/`, `bootstrap/`, `pins/`, `secrets/`) carry no ownership signal. (2) The Dependabot auto-merge label gate - the human disposition that replaces plan-blocked required review on the bot path - has still never been exercised: the `dependabot-approved` label does not exist, no Dependabot PR has ever been opened, and the daily sweep only logs 'no open dependabot PRs'.

Recommended next actions: fix CODEOWNERS to a resolvable user/team and verify with the API; create the label and exercise the sweep once with a captured result; record disposition rows for red-check merges until required checks exist; when the plan changes, apply the ready payload after confirming the exact required-check context.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Branch protection | `main` | required checks/reviews | absent (plan-gated) | accepted | 403 on GET/PUT |
| Rulesets | repo | modern protection | absent (plan-gated) | accepted | 403 |
| CODEOWNERS | `.github/CODEOWNERS` | advisory ownership | invalid | Medium | 6 `Unknown owner` errors |
| PR template | `.github/pull_request_template.md` | review checklist | present | Low | evidence/validation/rollback/security/gate sections |
| Dependabot config | `.github/dependabot.yml` | dependency updates | actions + pip (added 2026-10-09) | Low | weekly, limit 5 each |
| Auto-merge sweep | `.github/workflows/dependabot-merge.yml` | label-gated merges | configured, unexercised | Low-Medium | write scopes (CI-P2-001) |
| Environments | repo settings | required reviewers | none | accepted | 0 environments |
| Manual dispatch | all 3 workflows | operator triggers | present | Low | owner-only repo |
| Break-glass | `docs/security/{BRANCH_PROTECTION,BREAK_GLASS_CUSTODY}.md` | emergency access | documented; custody pending | Low-Medium | OD-04 PENDING |
| Stale registrations | Actions API | workflow inventory | 3 probe workflows | Low | see CI-P3-002 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Workflows/jobs | 3 | 3 hardened workflows; validate green at f5cb7c9 | no server enforcement; same-repo PRs on lab | runner hardening; plan upgrade |
| PR templates | 4 | pull_request_template.md present with evidence/rollback sections | not enforced | keep |
| CODEOWNERS | 1 | 6 Unknown owner errors | entire file invalid | fix owner handle |
| Dependabot | 3 | 2 ecosystems; alerts enabled; sweep daily | label gate unexercised; security updates off (SC) | exercise once |
| Release/deploy/migration/security workflows | 2 | no release/deploy workflow; publication chain in validate | no release approval/tag protection | document; plan upgrade |
| Branch/release/hotfix docs | 4 | BRANCH_PROTECTION.md matrix + walkthrough + break-glass template | custody pending (OD-04) | name custodian |
| Environment approvals | 0 | environments API 0 | none | plan-gated |
| Manual dispatch | 4 | workflow_dispatch on all 3 | none | keep |
| Workflow risks | 3 | zizmor/actionlint; SHA pins | sudo runner; write token | see CI findings |

## Detailed Review

### Item: Required-check enforcement matrix
- Evidence: `BRANCH_PROTECTION.md:82-104`.
- What it does: states precisely that required checks/reviews/force-push/linear-history/tag rules are not server-enforced; the Dependabot label gate is the only bot control; bypass audit is manual.
- Current controls: doctrine (AGENTS.md no force-push), advisory validate, label gate.
- Missing controls: server enforcement (plan), environment reviewers, tag protection.
- Risks: failing/direct pushes can land (observed on PR #54).
- Recommended improvement: keep the matrix current; add a disposition row for every red-check merge.

### Item: CODEOWNERS
- Evidence: `.github/CODEOWNERS`; API errors.
- Current state: invalid; zero effective owners.
- Recommended improvement: use `@JulianB-MCT` (resolves; has admin/write) or create an org team.

### Item: Dependabot auto-merge
- Evidence: workflow + labels + PR inventory + sweep log.
- Current state: configured, never exercised.
- Recommended improvement: create the label; exercise and capture.

### Item: Break-glass
- Evidence: `BRANCH_PROTECTION.md:133-172`; `BREAK_GLASS_CUSTODY.md:5-10`.
- Current state: process documented; OD-04 custody PENDING; no custodian/sealed credential/rehearsal.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| BP-001 | Workflows/jobs | run 38110410254; matrix | advisory validate | no required check | P1 (owner-accepted) | plan upgrade |
| BP-002 | PR templates | pull_request_template.md | advisory | none | P3 | keep |
| BP-003 | CODEOWNERS | API errors 6 | none effective | invalid file | P2 | fix owner handle |
| BP-004 | Dependabot | labels/PRs/sweep | label gate configured | never exercised | P3 | exercise once |
| BP-005 | Release/deploy/security workflows | validate steps | publication chain enforced | no release approval | P2 (plan) | plan upgrade |
| BP-006 | Branch/release/hotfix docs | BRANCH_PROTECTION.md | strong docs | custody pending | P3 | name custodian |
| BP-007 | Environment approvals | environments API 0 | none | none | P2 (plan) | add when available |
| BP-008 | Manual dispatch | workflow files | present | none | P3 | keep |
| BP-009 | Workflow risks | zizmor green; PR #54 red merge | manual audit | unaudited bypasses | P3 | disposition rows |

## Findings

### BP-P2-001 - CODEOWNERS is invalid: every entry uses an unresolvable org handle
- Severity: P2; Confidence: High (codeowners/errors API); Area: BP; Status: still-open
- Evidence: `.github/CODEOWNERS:7,10-14`; 6 API errors; BRANCH_PROTECTION.md:34-35,93
- Impact: the documented compensating control does not function; sensitive-path ownership is not signaled.
- Fix: replace with `@JulianB-MCT` or an org team; verify API; update the doc text. Owner: repo owner. Effort: S.

### BP-P3-001 - Dependabot auto-merge compensating control has never been exercised
- Severity: P3; Confidence: High; Area: BP; Status: still-open
- Evidence: dependabot-merge.yml:41-45; no label; 0/54 dependabot PRs; run 38047609916 'no open dependabot PRs'
- Impact: the human-disposition step replacing required review has no evidence it works.
- Fix: create the label; exercise and capture both behaviors. Owner: repo owner. Effort: S.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1 @ 08e20d1, statuses per the 2026-10-11 verification register)

| Prior finding | Prior status | Current verification (f5cb7c9, 2026-10-11) | Disposition |
|---|---|---|---|
| BP-P1-001 Branch protection/required checks plan-gated | owner-accepted | GET protection + rulesets 403; owner decision unchanged; PR #54 shows the residual in practice | still owner-accepted; not re-filed |
| BP-P2-001 CODEOWNERS invalid | open | API still returns 6 Unknown owner errors; file unchanged | re-filed as BP-P2-001 |
| BP-P3-001 Dependabot label gate unexercised | open | no label; 0 dependabot PRs; sweep still a no-op | re-filed as BP-P3-001 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No server-side review/check enforcement | Medium | Medium | failing/direct push can land | 403; PR #54 red merge | accepted; compensating controls |
| CODEOWNERS ineffective | Medium | High | sensitive paths unreviewed | codeowners/errors | fix owner handle |
| Untested auto-merge control | Low | Medium | silent no-op | labels/PRs API | exercise once |
| Red-check merges unaudited | Low | Medium | process drift | PR #54, no 2026-10-11 row | disposition rows |
| Break-glass custody undecided (OD-04) | Medium | Low | no two-person rule in an emergency | BREAK_GLASS_CUSTODY.md:5 | owner decision |

## Recommendations

### Immediate / Release Blocking
- None: no server-side control can be enabled on the current plan (owner-accepted).

### This Week
- BP-P2-001: fix CODEOWNERS to a resolvable owner and verify with `codeowners/errors`.
- BP-P3-001: create the `dependabot-approved` label and exercise the sweep once.
- Record a disposition row for the PR #54 red-check merge (and future ones).

### This Month
- Append the exercise results and the CODEOWNERS fix to the enforcement matrix; confirm the required-check context when applying the ready payload after any plan change.

### Later / Platform Evolution
- If the plan changes: apply the ready payload, add tag protection/release approval, and add environment required reviewers for the merge path.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix CODEOWNERS owner | restores the advisory review signal | `.github/CODEOWNERS` | codeowners/errors empty |
| Create the Dependabot label | makes the gate actionable | repo settings | label exists; sweep exercised |
| Append 2026-10-11 verification to the matrix | keeps records current | BRANCH_PROTECTION.md | doc matches API state |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Required checks + linear history + force-push block | P1 | owner | S | GitHub Pro (owner decision) |
| Tag/release protection | P2 | owner | S | plan |
| Break-glass custody designation (OD-04) | P2 | owner | S | owner-only |

## Suggested Tests

- A fixture/regression test that fails when CODEOWNERS contains an unresolvable owner.
- A staged auto-merge exercise with both label states, captured as evidence.
- On plan upgrade: a canary PR that must be blocked by the required check and one that must be blocked by force-push.

## Suggested Documentation Updates

- `docs/security/BRANCH_PROTECTION.md`: append the 2026-10-11 verification (403s, CODEOWNERS invalid, label unexercised, PR #54 red-check merge) and the required-check-context question.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Exact required-check context for the ready payload: check-runs report the name `validate`, while the doc uses `validate / validate` | an incorrect context would leave merges waiting on a check that never reports | GitHub UI picker after plan upgrade, or a test apply |
| Will the owner designate break-glass custodians (OD-04)? | emergency access currently rests on a shared sudo value + file mode | decision-log entry |
| Should red-check merges require a disposition row? | bypass audit is manual | owner statement |

## Limitations

- The ready-to-apply protection payload cannot be exercised on the current plan; all enforcement statements come from the 403 responses and the repository's own matrix.
- Org-level settings (rulesets inheritance, runner groups, plan) were not accessible.
- Check-run naming semantics were observed via the check-runs API only; the UI picker was unavailable (plan-gated).

## Appendix

- PR #54: head `1cf1886cd`, check-runs = `validate` failure; merged 2026-10-11T03:53:02Z by JulianB-MCT; 0 reviews, 0 comments; merge commit `584e1a37`; publication rebind at `3c11752`/`f5cb7c9` restored the chain.
- Environments: 0; labels: default nine only; rulesets/protection: 403 plan-gated.

## Findings

| ID | Severity | Title |
|---|---|---|
| BP-P2-001 | P2 | CODEOWNERS is invalid: every entry uses an unresolvable org handle |
| BP-P3-001 | P3 | Dependabot auto-merge compensating control has never been exercised |
