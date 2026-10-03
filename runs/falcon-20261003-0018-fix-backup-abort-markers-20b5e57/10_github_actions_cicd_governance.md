# GitHub Actions and CI/CD Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: CI
- Output path: docs/audits/{name}/{run}/10_github_actions_cicd_governance.md
- Scope limitations: no GitHub API/settings access; branch-protection state is `unverified` and documented as plan-blocked.

## Scope

Reviewed the three workflows (`validate`, `external-smoke`, `dependabot-merge`), `ci/validate.py`, the governance docs, CODEOWNERS, and dependabot config.

## Evidence Reviewed

- `.github/workflows/validate.yml`, `external-smoke.yml`, `dependabot-merge.yml`.
- `ci/validate.py`, `ci/requirements-ci.txt`, `ci/preflight.sh`.
- `docs/security/BRANCH_PROTECTION.md`, `CI_GOVERNANCE_RECONCILIATION.md`, `CI_TOOL_PINS.md`.
- `.github/CODEOWNERS`, `.github/dependabot.yml`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `validate.yml` L43-72 | Config | curl fail-fast | all downloads use `--fail` |
| `ci/validate.py` CHECKS | Source | Gate breadth | 13 checks incl. evidence-index, shell-tests |
| `validate.yml` L101-106 | Config | drift gate | verify_publication_chain + digest test |
| `dependabot-merge.yml` | Config | auto-merge | contents:write, label-gated |

## Executive Summary

CI governance has improved materially since the prior run: every tool download now fails fast (`--fail`), `ci/validate.py` implements the evidence-index check it documents, the shellcheck invocation matches CI, and the publication-chain/digest gate runs on every push/PR. Branch protection remains plan-blocked (GitHub Free private) with the owner-label gate as the compensating control, and the auto-merge workflow still holds `contents: write` without environment protection.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| validate | `.github/workflows/validate.yml` | static gate | Functional | Low | 13 checks |
| external-smoke | `external-smoke.yml` | public surface | Functional | Low | daily |
| dependabot-merge | `dependabot-merge.yml` | auto-merge | Functional | Medium | label-gated |
| gauntlet | `ci/validate.py` | repo checks | Functional | Low | evidence-index now real |
| branch protection | `docs/security/BRANCH_PROTECTION.md` | governance | Plan-blocked | Medium | compensating control |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Workflow correctness | 4 | actionlint, zizmor | — | — |
| Least privilege | 3 | `contents: read` on validate | auto-merge write | CI-P2-002 |
| Pinning | 5 | actions pinned by SHA; tools by hash | — | — |
| Branch protection | 2 | plan-blocked | required checks | CI-P1-002 |
| Secrets in CI | 4 | no secrets needed | — | — |
| Drift detection | 4 | weekly schedule + chain gate | — | — |

## Findings

### Finding ID: CI-P1-001 - CI tool downloads did not fail fast

- Severity: P1
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/validate.yml` lines 43-72 — every `curl` download now passes `--fail --show-error --retry 3` and verifies a SHA-256
  - prior status: `CI-P1-001 partially-fixed` in the 2026-10-02 run register
- What is happening: The fix is present at this commit; a failed download now aborts instead of piping garbage into the tool.
- Why it matters: Previously a transient 4xx/5xx could install an empty/bad binary.
- User / business impact: None at this commit; recorded for traceability.
- Security / privacy / reliability impact: Supply-chain integrity improved.
- Recommended fix: None.
- Suggested validation: CI run green; mutation test unnecessary.
- Owner suggestion: CI/coordinator
- Effort estimate: S
- Dependencies: None
- Status: verified-fixed

### Finding ID: CI-P1-002 - Branch protection and required checks are not enforced server-side

- Severity: P1
- Confidence: Medium
- Area: CI
- Evidence:
  - `.github/CODEOWNERS` header — "Branch protection that would enforce Code Owner review is plan-blocked (GitHub Free private repo)"
  - `docs/security/BRANCH_PROTECTION.md` — plan-blocked rationale and compensating controls
  - `dependabot-merge.yml` — label-gated alternative
- What is happening: The repository cannot enforce required review/checks at the GitHub settings layer.
- Why it matters: A direct push to `main` bypasses the gate.
- User / business impact: Governance relies on process.
- Security / privacy / reliability impact: Weaker merge control.
- Recommended fix: Enable branch protection/required checks when the plan allows; until then keep the label gate and document exceptions in the decision log.
- Suggested validation: `gh api` branch-protection read returns required checks.
- Owner suggestion: owner
- Effort estimate: S
- Dependencies: GitHub plan
- Status: owner-accepted

### Finding ID: CI-P2-001 - `ci/validate.py` did not implement the evidence-index verification its docstring promises

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `ci/validate.py` line 183 `check_evidence_index()` calls `automation/validation/check_evidence_index.py`
  - `ci/validate.py` CHECKS includes `"evidence-index"`
  - `automation/validation/check_evidence_index.py` present; test `evidence_index_check_test.sh` present
- What is happening: The check is now wired and tested.
- Why it matters: Prior doc/code mismatch is closed.
- User / business impact: None at this commit.
- Security / privacy / reliability impact: Evidence/provenance integrity improved.
- Recommended fix: None.
- Suggested validation: `python ci/validate.py --only evidence-index`.
- Owner suggestion: CI/coordinator
- Effort estimate: S
- Dependencies: None
- Status: verified-fixed

### Finding ID: CI-P2-002 - Auto-merge workflow holds `contents: write` with no environment protection

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/dependabot-merge.yml` lines 17-19 — `permissions: contents: write, pull-requests: write`
  - lines 46-48 — `gh pr merge --squash --delete-branch`
- What is happening: A scheduled workflow can merge and delete branches with write scope; no environment/protected-branch gate bounds it.
- Why it matters: If the workflow or token were subverted, it could land changes.
- User / business impact: Governance risk.
- Security / privacy / reliability impact: CI supply-chain escalation.
- Recommended fix: Use a protected environment, restrict to `dependabot[bot]`-authored PRs (already) and required checks, and pin the token scope.
- Suggested validation: Workflow run with a non-approved PR is skipped.
- Owner suggestion: owner
- Effort estimate: S
- Dependencies: plan
- Status: open

### Finding ID: CI-P3-001 - Local and CI shellcheck semantics diverged

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - `ci/validate.py` line 264 — `shellcheck --severity=warning --format=gcc`
  - `.github/workflows/validate.yml` lines 56-57 — same `--severity=warning --format=gcc`
- What is happening: Both invocations now agree on severity and format.
- Why it matters: Local runs predict CI.
- User / business impact: None at this commit.
- Security / privacy / reliability impact: Dev experience.
- Recommended fix: None.
- Suggested validation: local run matches CI.
- Owner suggestion: CI/coordinator
- Effort estimate: S
- Dependencies: None
- Status: verified-fixed

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Direct push bypasses gate | P1 | Medium | High | plan-blocked | CI-P1-002 |
| Auto-merge scope | P2 | Low | High | dependabot-merge | CI-P2-002 |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
- Add environment protection to the auto-merge workflow (CI-P2-002).

### This Month
- Enable required checks when the plan allows.

### Later / Platform Evolution
- Policy-as-code for branch protection.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Document the current gate authority | Clarity | CI_GOVERNANCE_RECONCILIATION.md | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Environment-gated auto-merge | P2 | owner | S | plan |

## Suggested Tests

- Assert the auto-merge workflow skips unlabeled PRs (static).

## Suggested Documentation Updates

- Keep `CI_TOOL_PINS.md` current with new tool digests.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `validate` currently green on `main`/branch? | Gate rot | CI log |

## Appendix
Not applicable.
