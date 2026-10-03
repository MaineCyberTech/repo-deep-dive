# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: CI
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/10_github_actions_cicd_governance.md
- Scope limitations: no GitHub API access; branch-protection state is `Unknown`.

## Scope

Both CI artifacts: `.github/workflows/deep-dive-deterministic.yml` (wired) and `ci/audit.yml` (example). Governance: branch protection, required checks, CODEOWNERS, Dependabot, permissions, triggers, concurrency, caching, artifacts.

## Evidence Reviewed

- `.github/workflows/deep-dive-deterministic.yml` (full)
- `ci/audit.yml` (full)
- `git ls-files` governance sweep; `.github` tree listing
- `runs/INDEX.md`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github` tree listing | command | wired workflows | only deterministic workflow |
| `ci/audit.yml` path | scan | wiring | committed under `ci/`, not `.github/workflows/` |
| `ci/audit.yml` `PACK_DIR` | config | layout correctness | `docs/audits/repo-deep-dive` vs root `tools/` |

## Executive Summary

The documented CI (lint → validate → score → P0 gate) is not wired: `ci/audit.yml` sits outside `.github/workflows/`, so it never runs, and its `PACK_DIR` assumes a vendored layout that does not match this repo's root. The one wired workflow is an org-wide scheduled scan that installs tools unsafely, has no concurrency/timeout/environment protection, and swallows failures. There is no CODEOWNERS, Dependabot, or in-repo branch-protection evidence.

## Inventory

| Workflow | Path | Trigger | Purpose | State |
|---|---|---|---|---|
| Deterministic | `.github/workflows/deep-dive-deterministic.yml` | `workflow_dispatch`, weekly cron | scan org repos | wired |
| Audit example | `ci/audit.yml` | `workflow_dispatch`, PR on `docs/audits/**` | lint/validate/score/P0 | **unwired** |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| `.github/workflows` | 2 | one workflow | no PR gate | add pack CI |
| PR validation | 1 | `ci/audit.yml` unwired | never runs | wire it |
| Lint/test/build | 2 | lint exists, not run in CI | no enforcement | add job |
| Deploy workflows | N/A | none | — | — |
| Migration workflows | N/A | none | — | — |
| Docker build/push | N/A | none | — | — |
| Releases | 1 | no release workflow | no tagging | add |
| Badge/report | 2 | step summary only | no dashboard CI | document |
| Secrets | 2 | PAT in URL | leak risk | fix (SEC-P1-002) |
| permissions blocks | 3 | `contents: read` | least-privilege ok | keep |
| OIDC | 0 | none | PAT used | consider OIDC |
| Environment protection | 0 | none | no approvals | add for prod |

## Findings

### Finding ID: CI-P1-001 - The audit CI example is not under `.github/workflows/` and never runs

- Severity: P1
- Confidence: High
- Area: CI
- Evidence:
  - `ci/audit.yml` — a full GitHub Actions workflow committed at `ci/audit.yml`
  - `.github/workflows/` contains only `deep-dive-deterministic.yml`
  - `README.md` §ci describes `ci/audit.yml` as "GitHub Actions example"
- What is happening: The workflow that lints the pack, validates runs, scores, and enforces the P0 gate is not in a location GitHub executes.
- Why it matters: The pack's central release-quality gate is documented but not exercised ("configured ≠ exercised").
- User / business impact: Regressions can't be blocked automatically.
- Security / privacy / reliability impact: No automated P0 gate.
- Recommended fix: Move/copy it to `.github/workflows/audit.yml` (or document it as a template and wire a real workflow).
- Suggested validation: Workflow appears in the Actions tab; a P0 fixture run fails.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: CI-P1-002 - ci/audit.yml assumes a vendored PACK_DIR that does not match this repo

- Severity: P1
- Confidence: High
- Area: CI
- Evidence:
  - `ci/audit.yml` lines 29-31 — `PACK_DIR: docs/audits/repo-deep-dive`
  - lines 44, 48, 52 — steps run `./tools/lint_pack.sh` / `python3 tools/run_toolchain.py` with `working-directory: ${{ env.PACK_DIR }}`
  - repo root — `tools/` lives at the repository root, and there is no `docs/audits/repo-deep-dive/tools`
- What is happening: The workflow expects the pack itself to be vendored under `docs/audits/repo-deep-dive`; in this repository the pack is the root.
- Why it matters: Even if wired, every step fails with "No such file or directory".
- User / business impact: CI would appear broken; operators may disable it.
- Security / privacy / reliability impact: Gate never green.
- Recommended fix: Set `PACK_DIR: .` for in-repo use, or parameterize; document the vendored variant separately.
- Suggested validation: Run the workflow against this repo; lint/validate steps succeed.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: CI-P1-001
- Status: open

### Finding ID: CI-P2-003 - The wired workflow installs mutable "latest" tools and fails silently

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` lines 51-56 — downloads actionlint from `main` branch and gitleaks from `releases/latest`; `|| true` on failure
  - line 57 — version print has `|| true`
  - line 88 — deterministic checks run with `|| true`
- What is happening: Tool versions are non-deterministic and failures are masked, so a missing tool produces a green run.
- Why it matters: Scheduled results are not reproducible and can silently stop checking.
- User / business impact: False confidence in org scan.
- Security / privacy / reliability impact: A disabled scanner goes unnoticed.
- Recommended fix: Pin versions+sha256; remove `|| true` on install; fail if a required scanner is absent.
- Suggested validation: Remove network access to the download host; job fails rather than skips.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: SEC-P1-001
- Status: open

### Finding ID: CI-P2-004 - Org-wide PAT workflow lacks concurrency, timeouts, and environment protection

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` — no `concurrency:`, no `timeout-minutes:`, `permissions: contents: read`
  - line 39 — uses a stored PAT (`ORG_READ_TOKEN`) rather than OIDC
  - schedule line 25 — weekly cron over all org repos
- What is happening: A broad-scope scheduled job has no cancellation, no bounded runtime, and no approval/environment gate.
- Why it matters: Overlapping runs can race on artifacts; a hung clone can consume the default 6h; token scope is long-lived.
- User / business impact: Resource waste; no review point for an org-wide operation.
- Security / privacy / reliability impact: Long-lived token + unbounded job.
- Recommended fix: Add `concurrency`, `timeout-minutes`, and consider a protected environment and GitHub App/OIDC token.
- Suggested validation: Workflow YAML contains the keys; concurrent dispatch cancels.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: CI-P2-005 - No branch protection, required-check, or CODEOWNERS evidence

- Severity: P2
- Confidence: Medium
- Area: CI
- Evidence:
  - `git ls-files` — no `.github/CODEOWNERS`
  - no committed branch-protection config or documentation of required checks
  - `ci/audit.yml` is unwired, so there is no check to require
  - GitHub branch-protection state: `Unknown` (no API access)
- What is happening: Nothing in the repo establishes review requirements or required status checks.
- Why it matters: Force-push/admin-merge bypass and unreviewed changes are possible; the shared rules ask whether checks can be bypassed and whether bypasses are audited.
- User / business impact: Governance gap.
- Security / privacy / reliability impact: Changes to the gate can ship unreviewed.
- Recommended fix: Add `CODEOWNERS`, require the pack CI + `check_run.sh` jobs on `main`, require PRs, and document bypass policy.
- Suggested validation: `gh api` shows required checks; a direct push to `main` is rejected.
- Owner suggestion: repo admin
- Effort estimate: S
- Dependencies: TEST-P1-001
- Status: open

### Finding ID: CI-P2-006 - pull_request runs pass an empty run_dir to the P0 gate

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `ci/audit.yml` lines 15-20 — `run_dir` is a `workflow_dispatch` input only
  - lines 48, 52, 56-57 — use `${{ inputs.run_dir || 'docs/audits/repo-deep-dive/latest' }}`
  - lines 21-23 — also triggered on `pull_request`
- What is happening: On PR events, `inputs.run_dir` is empty and everything targets a fixed `latest` path; the P0 gate then reads a possibly absent `findings.json`.
- Why it matters: The gate either checks the wrong folder or errors on a missing file.
- User / business impact: Confusing/misleading CI on PRs.
- Security / privacy / reliability impact: Gate not tied to the changed run.
- Recommended fix: Derive the changed run folder from the PR diff, or split PR vs manual jobs.
- Suggested validation: A PR touching a specific run validates that run.
- Owner suggestion: CI owner
- Effort estimate: M
- Dependencies: CI-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No enforced QA gate | P1 | High | Medium | CI-P1-001/002 | wire + fix path |
| Silent tool failure | P2 | High | Medium | CI-P2-003 | pin + fail closed |
| Unreviewed changes | P2 | Medium | Medium | CI-P2-005 | CODEOWNERS + checks |

## Recommendations

### Immediate / Release Blocking
- Wire the audit workflow at a correct path and fix `PACK_DIR`.

### This Week
- Pin CI tools; add concurrency/timeout.
- Add CODEOWNERS and required checks.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `PACK_DIR: .` + move workflow | CI runs | `.github/workflows/audit.yml` | Actions run green |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| OIDC/App token for org scan | P2 | CI owner | M | CI-P2-004 |

## Suggested Tests

- Push a P0 fixture run; P0 gate fails.
- Concurrency: dispatch twice; second cancels first.

## Suggested Documentation Updates

- README "CI" section: in-repo vs vendored layout; required checks.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are required checks set in GitHub settings? | actual enforcement | branch protection API — `Unknown` |

## Appendix

No deploy, migration, or container workflows exist in this pack.
