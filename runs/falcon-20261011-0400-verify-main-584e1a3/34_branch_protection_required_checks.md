# 34_branch_protection_required_checks — Prompt 34 - Branch Protection and Required Checks Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `34_branch_protection_required_checks.md` (area BP, prompt)

## Verification Performed

# Branch Protection and Required Checks Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (private, org-owned)
- Branch: `main`
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:42Z
- Auditor: subagent (read-only)
- Area code: BP
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/34_branch_protection_required_checks.md
- Scope limitations: repository + read-only GitHub API. Branch protection/rulesets cannot be applied on the current plan; the API returns 403 (verified). No settings were changed.

## Scope

Reviewed: all three workflows and their check names, `.github/CODEOWNERS`, `.github/pull_request_template.md`, `.github/dependabot.yml`, `docs/security/BRANCH_PROTECTION.md` (target payload, enforcement matrix, break-glass), `docs/security/BREAK_GLASS_CUSTODY.md`, and live server state: protection/rulesets, environments, labels, PRs, branches, check-runs, codeowners/errors. Not reviewed: org-level rulesets/settings (none apply to a private Free repo), `falcon-edge` workflows (separate repo), and the actual apply of the ready payload (plan-gated).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| GitHub API `branches/main/protection`, `rulesets` | live state | server-side enforcement truth | both 403 on 2026-10-09 |
| GitHub API `environments` | live state | environment approvals | total_count 0 |
| GitHub API `codeowners/errors` | live state | CODEOWNERS validity | 6 errors, all `Unknown owner` |
| GitHub API `labels`, `pulls`, `branches`, `commits/{sha}/check-runs` | live state | dependabot label gate, PR inventory, check names | no `dependabot-approved`; 0 dependabot PRs of 49 |
| `.github/CODEOWNERS`, `.github/dependabot.yml`, `.github/pull_request_template.md` | repo | ownership/update controls | 14 lines / 7 lines / 32 lines |
| `.github/workflows/*.yml` | repo | required-check candidates | validate (job `validate`), external-smoke, dependabot-merge |
| `docs/security/BRANCH_PROTECTION.md` | repo | declared process + enforcement matrix | lines 1-183 |
| `docs/security/BREAK_GLASS_CUSTODY.md` | repo | break-glass custody | OD-04 PENDING |
| Runs 37926819556 (dependabot-merge sweep), 37985725668 (validate@HEAD) | live runs | exercise evidence | sweep: "no open dependabot PRs" |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| Branch protection is still plan-gated | GET protection, GET rulesets (2026-10-09) | supported: both 403 "Upgrade to GitHub Pro or make this repository public" |
| Owner decision is "stay on Free" | `docs/security/BRANCH_PROTECTION.md:75-80` | supported (documented decision, no change found) |
| Required-check candidate is `validate` | check-runs API for 08e20d1 | observed names: `validate` and `smoke` (both success); docs use `validate / validate` (see Open Questions) |
| CODEOWNERS resolves | `codeowners/errors` API | unsupported: 6 `Unknown owner` errors (lines 7,10-14) |
| Dependabot label gate works | labels API + PR inventory + sweep log | configured, never exercised: label absent, 0 dependabot PRs ever |
| Environment approvals exist | environments API | unsupported: 0 environments |
| Break-glass process documented | BRANCH_PROTECTION.md:133-172; BREAK_GLASS_CUSTODY.md | supported; custody designation (OD-04) still pending |
| Prior BP-P1-001 unchanged | API + doc | supported: still plan-gated, owner-accepted |

## Executive Summary

The branch/release/hotfix process is documented unusually well for a single-owner repo: target protection payload, precise enforcement matrix, hotfix walkthrough, break-glass template and custody procedure. Server-side enforcement remains impossible on the private GitHub Free plan (protection and rulesets both return 403), and the owner has explicitly accepted that (BP-P1-001 owner-accepted; CI-P1-001 same root cause). This audit verified the accepted status rather than re-filing it.

Two compensating-control gaps are current and fixable: (1) the `.github/CODEOWNERS` file — the documented advisory review control — is entirely invalid: GitHub reports `Unknown owner` on all six entries because they use the bare org handle `@MaineCyberTech` (the org has no teams). (2) The Dependabot auto-merge label gate (the human disposition that replaces plan-blocked required review) has never been exercised: the `dependabot-approved` label does not exist and no Dependabot PR has ever been opened, so the "green checks + label" path has no evidence of ever gating a merge.

Recommended next actions: fix CODEOWNERS to a resolvable user/team and re-check via the API; create the label and exercise the merge path once with a captured result; when the plan changes, apply the ready payload after confirming the exact required-check context.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Branch protection | `main` | required checks/reviews | absent (plan-gated) | accepted | 403 on GET/PUT |
| Rulesets | repo | modern protection | absent (plan-gated) | accepted | 403 |
| CODEOWNERS | `.github/CODEOWNERS` | advisory ownership | invalid | Medium | 6 `Unknown owner` errors |
| PR template | `.github/pull_request_template.md` | review checklist | present | Low | evidence/validation/rollback sections |
| Dependabot config | `.github/dependabot.yml` | actions updates | present, actions-only | Low | weekly, limit 5 |
| Auto-merge sweep | `.github/workflows/dependabot-merge.yml` | label-gated merges | configured, unexercised | Low-Medium | write scopes (CI-P2-001) |
| Environments | repo settings | required reviewers | none | accepted | 0 environments |
| Manual dispatch | all 3 workflows | operator triggers | present | Low | owner-only repo |
| Break-glass | `docs/security/{BRANCH_PROTECTION,BREAK_GLASS_CUSTODY}.md` | emergency access | documented; custody pending | Low-Medium | OD-04 PENDING |
| Stale registrations | Actions API | workflow inventory | 3 probe workflows | Low | see CI report |

## Findings

### Finding ID: BP-P2-001 (new, ID provisional) - CODEOWNERS is invalid: every entry uses an unresolvable org handle

- Severity: P2
- Confidence: High (GitHub `codeowners/errors` API)
- Area: BP
- Evidence:
  - `.github/CODEOWNERS:7,10-14` (`* @MaineCyberTech`, `/.github/ @MaineCyberTech`, `/ci/`, `/bootstrap/`, `/pins/`, `/secrets/`)
  - `GET /repos/MaineCyberTech/falcon/codeowners/errors` -> 6 errors, all `"kind": "Unknown owner"` with the suggestion "make sure @MaineCyberTech exists and has write access"
  - `GET /orgs/MaineCyberTech/teams` -> `[]` (no team exists that could be addressed as `@MaineCyberTech/<team>`)
  - `docs/security/BRANCH_PROTECTION.md:34-35` claims CODEOWNERS "make[s] the ownership/review expectation explicit" as a compensating control; `:93` records that owner review is advisory
- What is happening: CODEOWNERS entries must be a user or `org/team`; the bare org handle does not resolve, so GitHub ignores all six lines. The file's own comment anticipated this ("If GitHub cannot resolve the org handle, replace @MaineCyberTech with the owner user account") but the replacement was never made.
- Why it matters: with branch protection and required review plan-gated, CODEOWNERS is one of the few remaining review signals — and it currently assigns no owners at all, including for sensitive trees (`/.github/`, `/ci/`, `/bootstrap/`, `/pins/`).
- User / business impact: the documented compensating control does not function; sensitive-path ownership is not signaled in PRs.
- Security / privacy / reliability impact: reduced review pressure on exactly the files that define the CI/secret surface.
- Recommended fix: replace `@MaineCyberTech` with the owner user account (`@JulianB-MCT`, who has admin/write) or create an org team with write access and use `@MaineCyberTech/<team>`; then confirm `codeowners/errors` returns zero errors and update `BRANCH_PROTECTION.md` compensating-controls text.
- Suggested validation: `gh api repos/MaineCyberTech/falcon/codeowners/errors` returns `{"errors":[]}`; a test PR touching `/ci/` shows the owner as a requested reviewer.
- Owner suggestion: repo owner.
- Effort estimate: S
- Dependencies: none.
- Status: open

### Finding ID: BP-P3-001 (new, ID provisional) - Dependabot auto-merge compensating control has never been exercised

- Severity: P3
- Confidence: High
- Area: BP
- Evidence:
  - `.github/workflows/dependabot-merge.yml:41-45` (merge only when the PR carries the owner-applied `dependabot-approved` label)
  - `GET /repos/MaineCyberTech/falcon/labels` -> bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix (no `dependabot-approved`)
  - `GET /pulls?state=all` (49 PRs) -> zero authored by `app/dependabot`
  - Sweep run 37926819556 job log: `no open dependabot PRs`; the Dependabot dynamic update workflow has 4 runs (last 2026-10-07, success)
  - `docs/security/BRANCH_PROTECTION.md:84-88` claims the label gate is "live"
- What is happening: the label-gated sweep is configured and runs daily, but the label does not exist and no Dependabot PR has ever been created, so the gate has never merged (or refused to merge) anything. Per the shared rules, configured is not exercised.
- Why it matters: the label gate is the compensating control for plan-blocked required review on the bot path; its failure mode (e.g., a broken `gh pr checks` or label typo) is untested.
- User / business impact: the human-disposition step that replaces required review has no evidence it works.
- Security / privacy / reliability impact: low; an untested control can silently no-op.
- Recommended fix: create the `dependabot-approved` label; exercise the path once (stage a Dependabot-style PR or re-run the sweep against a controlled PR) and capture the result; record the exercise date in the enforcement matrix.
- Suggested validation: a captured run showing the skip-without-label and merge-with-label behaviors.
- Owner suggestion: repo owner.
- Effort estimate: S
- Dependencies: an open Dependabot PR (or a staged equivalent).
- Status: open (not exercised)

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

| Prior finding | Prior status | Current verification | Disposition |
|---|---|---|---|
| BP-P1-001 Branch protection/required checks plan-gated and unenforceable | owner-accepted | GET protection + rulesets 403 on 2026-10-09; owner decision "stay on Free" (`BRANCH_PROTECTION.md:75-80`); compensating controls documented | still owner-accepted; not re-filed |
| CI-P1-001 same root cause | owner-accepted | same 403 evidence | still owner-accepted; not re-filed |
| BP-P2-002 residual (Dependabot label gate) | documented in the enforcement matrix | label gate configured but unexercised; CODEOWNERS broken | see BP-P2-001/BP-P3-001; the matrix remains the accurate statement of what is not enforced |

No prior BP finding is regressed. The enforcement matrix (`BRANCH_PROTECTION.md:90-97`) remains accurate: required checks/reviews/force-push/linear-history/tag protection are not server-enforced; the Dependabot label path is the only bot-specific control; bypass audit is manual.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No server-side review/check enforcement | Medium | Medium | failing/direct push can land | 403; matrix :90-97 | accepted; compensating controls (fix CODEOWNERS) |
| CODEOWNERS ineffective | Medium | High | sensitive paths unreviewed | codeowners/errors | fix owner handle |
| Untested auto-merge control | Low | Medium | silent no-op | labels/PRs API | exercise once; capture |
| Break-glass custody undecided (OD-04) | Medium | Low | no two-person rule in an emergency | BREAK_GLASS_CUSTODY.md:6-10 | owner decision (cross-ref SECRET) |

## Recommendations

### Immediate / Release Blocking
- None: no server-side control can be enabled on the current plan (owner-accepted).

### This Week
- BP-P2-001: fix CODEOWNERS to a resolvable owner and verify with `codeowners/errors`.
- BP-P3-001: create the `dependabot-approved` label and exercise the sweep once.

### This Month
- Append the exercise results and the CODEOWNERS fix to the enforcement matrix; confirm the required-check context when applying the ready payload after any plan change.

### Later / Platform Evolution
- If the plan changes: apply the ready payload, add tag protection/release approval, and add environment required reviewers for the merge path; consider a `main` ruleset with bypass audit.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix CODEOWNERS owner | restores the advisory review signal | `.github/CODEOWNERS` | codeowners/errors empty |
| Create the Dependabot label | makes the gate actionable | repo settings | label exists; sweep exercised |
| Append 2026-10-09 verification to the matrix | keeps records current | `docs/security/BRANCH_PROTECTION.md` | doc matches API state |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Required checks + linear history + force-push block | P1 | owner | S | GitHub Pro (owner decision) |
| Tag/release protection | P2 | owner | S | plan |
| Break-glass custody designation (OD-04) | P2 | owner | S | owner-only |

## Suggested Tests

- A fixture/regression test that fails when CODEOWNERS contains an unresolvable owner (the API check can be captured periodically).
- A staged auto-merge exercise with both label states, captured as evidence.
- On plan upgrade: a canary PR that must be blocked by the required check and one that must be blocked by force-push.

## Suggested Documentation Updates

- `docs/security/BRANCH_PROTECTION.md`: append the 2026-10-09 verification (403s, CODEOWNERS invalid, label unexercised) and the required-check-context question.
- `README.md`/`AGENTS.md` if the CODEOWNERS owner handle changes.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Exact required-check context for the ready payload: check-runs API reports the job name `validate`, while `BRANCH_PROTECTION.md:20,45` uses `validate / validate` | an incorrect context would leave merges waiting on a check that never reports | GitHub UI picker after plan upgrade, or a test apply |
| Will the owner designate break-glass custodians (OD-04)? | emergency access currently rests on a shared sudo value + file mode | decision-log entry |
| Do org runner groups restrict this repo's runners to specific workflows? | blast radius (cross-ref CI-P1-002) | org settings (org admin) |

## Limitations

- The ready-to-apply payload cannot be exercised on the current plan; all enforcement statements are from the 403 responses and the repo's own matrix.
- Org-level settings (rulesets inheritance, runner groups, plan) were not accessible.
- Check-run naming semantics were observed via the check-runs API only; the UI picker was not available (plan-gated).

## Findings

| ID | Severity | Title |
|---|---|---|
| BP-P2-001 | P2 | CODEOWNERS is invalid: every entry uses an unresolvable org handle |
| BP-P3-001 | P3 | Dependabot auto-merge compensating control has never been exercised |
