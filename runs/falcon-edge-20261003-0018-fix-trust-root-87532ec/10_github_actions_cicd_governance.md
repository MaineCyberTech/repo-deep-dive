# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: CI
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/10_github_actions_cicd_governance.md
- Scope limitations: no GitHub API access; governance status read from repo docs and workflows (branch protection is documented as plan-blocked).

## Scope

Reviewed the five workflows (`.github/workflows/*`), Dependabot config, CODEOWNERS, PR template, branch-protection docs, and release/publish flow.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github/workflows/validate.yml` | Workflow | Main gate | tests matrix + lints + review pkg |
| `.github/workflows/bake-image.yml` | Workflow | Credential-bearing build | `bake` environment |
| `.github/workflows/publish-release.yml` | Workflow | Release | manual, `contents: write` |
| `.github/workflows/boot-smoke.yml` | Workflow | Boot test | manual |
| `.github/workflows/dependabot-merge.yml` | Workflow | Auto-merge | scheduled sweep |
| `.github/dependabot.yml`, `CODEOWNERS` | Config | Supply chain/ownership | SHA-pinned actions |
| `docs/security/BRANCH_PROTECTION.md`, `docs/GITHUB_CI.md` | Docs | Governance | plan-blocked |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Workflow read | Static | permissions/pins/triggers | least privilege; SHA pins |
| Publish flow read | Static | artifact promotion | draft default |
| Dependabot merge read | Static | bypass logic | no head-commit match |
| Docs cadence compare | Static | drift | "every 20 minutes" vs daily cron |

## Executive Summary

CI is well designed for a private lab repo: every action SHA-pinned with Dependabot bumps, `persist-credentials: false`, least-privilege `permissions`, `concurrency`, gitleaks/zizmor/actionlint/shellcheck/ruff, `ci/validate.sh`, review-package build+verify, plus a manual credential-bearing bake and QEMU boot smoke. The governance gap is structural and owner-accepted: on GitHub Free/private, branch protection and required checks cannot be enforced, so a failing push to `main` is only *visible*, not blocked. Secondary issues: `dependabot-merge.yml` merges on green without matching the checked commit to the merged head, and the docs state a 20-minute sweep while the cron is daily.

## Inventory

| Workflow | Trigger | Purpose | Controls | Risk |
|---|---|---|---|---|
| `validate` | push(main)/PR/schedule | gate | pins, perms, scans | Low |
| `bake-image` | dispatch | image build | `bake` env, 0600 staging | Med (secrets) |
| `publish-release` | dispatch | release | draft/prerelease default | Low |
| `boot-smoke` | dispatch | QEMU boot | artifact download | Low |
| `dependabot-merge` | schedule/dispatch | auto-merge | author filter | Med |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Workflows | 5 | SHA-pinned, perms | — | — |
| PR validation | 4 | validate on PR | advisory | branch protection |
| Lint/typecheck/test/build | 4 | ruff/shellcheck/actionlint | no typecheck | add mypy? |
| Deploy workflows | 3 | no deploy workflow | by design lab | document |
| Migration workflows | 1 | none | no migrations | DATA |
| Docker build/push | N/A | none | — | — |
| Releases | 4 | publish workflow | manual | — |
| Secrets/perms blocks | 5 | least privilege | — | — |
| OIDC | N/A | not used | — | — |
| Environment protection | 2 | `bake` env exists | reviewers plan-blocked | upgrade |
| Manual approval | 2 | none | plan-blocked | upgrade |
| Concurrency/caching | 4 | concurrency present | no cache | minor |
| Branch protection | 1 | plan-blocked | not enforced | CI-P2-001 |
| CODEOWNERS | 3 | present | not enforced | plan |
| Dependabot | 4 | weekly, SHA pins | merge race | CI-P2-002 |
| SBOM/container scans | 4 | SBOM in bake | no image scan | future |

## Detailed Review

### Item: Required checks / branch protection

- Evidence: `docs/security/BRANCH_PROTECTION.md` (403 plan-gated), `docs/GITHUB_CI.md` §Plan limitations, `ledgers/risk_register.md` R-012/D-011.
- Status: owner-accepted compensating controls (advisory validate, CODEOWNERS, discipline).
- Risk: CI-P2-001.

### Item: Dependabot auto-merge

- Evidence: `dependabot-merge.yml` — `gh pr checks "$pr" >/dev/null && gh pr merge "$pr" --squash`.
- Gap: no `--match-head-commit`; checks are evaluated then the merge proceeds, so a force-push/new commit between the check and merge could be merged unchecked (low likelihood on a bot-authored PR, but the pattern is the issue).
- Risk: CI-P2-002.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CI-001 | Workflows | `.github` | SHA pin | — | — | — |
| CI-002 | PR validation | validate | advisory only | no required checks | P2 | plan upgrade |
| CI-003 | Lint/test | validate | comprehensive | no typecheck | P3 | optional |
| CI-004 | Deploy | none | N/A lab | — | — | — |
| CI-005 | Migrations | none | N/A | — | P2 | DATA |
| CI-006 | Releases | publish | manual draft | — | — | — |
| CI-007 | Secrets | workflows | env-passed | secrets in bake | P2 | owner-accepted |
| CI-008 | Permissions | workflows | least privilege | — | — | — |
| CI-009 | Environment approval | `bake` | not available | plan | P2 | upgrade |
| CI-010 | Branch protection | doc | not enforced | plan | P2 | CI-P2-001 |

## Findings

### Finding ID: CI-P2-001 - Branch protection and required checks cannot be enforced; pushes to main are only advisory-gated

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `docs/security/BRANCH_PROTECTION.md` — every protection/ruleset API call returns `403 Upgrade to GitHub Pro`
  - `docs/GITHUB_CI.md` §Plan limitations — environment reviewers and required checks unavailable
  - `ledgers/risk_register.md` — R-012, owner decision D-011 (stay Free)
- What is happening: `main` has no enforced required status checks; a red push is visible but not blocked. Owner explicitly accepted this with compensating controls.
- Why it matters: the primary merge safety control is procedural, not technical.
- User / business impact: a bad change can reach `main` without green CI.
- Security / privacy / reliability impact: release-integrity risk (partially mitigated by no-force-push doctrine, pins, and reviews).
- Recommended fix: upgrade to GitHub Team/Pro to enable the already-prepared protection payload and `bake` environment reviewers; otherwise re-affirm the accepted risk with a dated review.
- Suggested validation: after upgrade, `GET /branches/main/protection` shows the three required contexts.
- Owner suggestion: owner
- Effort estimate: S (plan) / L (migration)
- Dependencies: billing plan
- Status: owner-accepted

### Finding ID: CI-P2-002 - Dependabot auto-merge does not bind the merge to the exact checked commit

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/dependabot-merge.yml` — `gh pr checks "$pr" && gh pr merge "$pr" --squash --delete-branch`
  - no `--match-head-commit` / SHA comparison
  - `permissions: contents: write, pull-requests: write`
- What is happening: the workflow checks status for the PR head, then unconditionally merges; a commit pushed between those calls is not re-checked.
- Why it matters: the merge path can violate the "only merge on green" guarantee it exists to provide.
- User / business impact: a malicious/compromised Dependabot branch (or a race) could merge unchecked.
- Security / privacy / reliability impact: supply-chain merge integrity.
- Recommended fix: capture the head SHA from `gh pr checks`/`gh pr view`, assert it equals the current head, then `gh pr merge --match-head-commit <sha>`.
- Suggested validation: test the workflow against a PR whose head changes; assert it refuses.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: CI-P3-001 - CI documentation states a 20-minute Dependabot sweep; the workflow runs daily

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - `docs/GITHUB_CI.md` §4 — "A scheduled sweep (every 20 minutes, plus manual dispatch)"
  - `.github/workflows/dependabot-merge.yml` — `cron: "23 5 * * *"` (daily 05:23 UTC)
- What is happening: the documented cadence does not match the actual schedule.
- Why it matters: self-consistency; operators expecting prompt merges wait a day.
- User / business impact: minor expectation mismatch.
- Security / privacy / reliability impact: low.
- Recommended fix: correct the docs (or the cron) so they agree.
- Suggested validation: doc review / actionlint.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No enforced branch protection | P2 | Medium | Bad change on main | BRANCH_PROTECTION.md | plan upgrade |
| Merge/dependabot race | P2 | Low | Unchecked merge | dependabot-merge.yml | match head |
| Doc cadence drift | P3 | High | Confusion | GITHUB_CI.md | fix docs |

## Recommendations

### Immediate / Release Blocking
Add `--match-head-commit` to the Dependabot merge.

### This Week
Re-affirm the branch-protection risk acceptance with a date; fix docs.

### This Month
Evaluate GitHub Team plan for required checks + bake reviewers.

### Later / Platform Evolution
Add migration CI and image vulnerability scanning.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `--match-head-commit` | closes race | `dependabot-merge.yml` | workflow test |
| Fix cadence doc | consistency | `docs/GITHUB_CI.md` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Plan upgrade for protection | P2 | owner | S | billing |
| Image scan | P3 | build-agent | M | tooling |

## Suggested Tests

- Workflow: simulate head change mid-check.
- Governance: assert required contexts after plan upgrade.

## Suggested Documentation Updates

- `docs/GITHUB_CI.md`: align the Dependabot cadence; record the date of the risk acceptance.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Will the owner reconsider the plan? | CI-P2-001 fix | owner decision |
| Is a deploy workflow planned for production? | CI-004 scope | roadmap |

## Appendix

All four published actions are SHA-pinned: `actions/checkout@3d3c42e...`, `actions/setup-python@5fda3b9...`, `actions/upload-artifact@043fb46...`. Every workflow sets `persist-credentials: false` on checkout. `validate` runs on `push(main)`, PR, weekly cron, and dispatch.
