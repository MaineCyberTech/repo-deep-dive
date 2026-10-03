# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: CI
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/10_github_actions_cicd_governance.md
- Scope limitations: No remote API access; branch-protection state is **unverified**. `.github/` is absent locally.

## Scope

Reviewed repository automation and governance: workflows, required checks, branch protection config, dependency/security scanning, release automation, and code ownership. Not reviewed: GitHub server-side settings (no network access) — marked unverified.

## Evidence Reviewed

- directory listing: no `.github/` (`Test-Path .github` = false)
- `package.json` scripts: `lint`, `typecheck`, `test`, `build`, `format:check`
- `git remote -v` → `github.com/MaineCyberTech/buddy.git`
- `git tag` → `v0.1.0-rc1`
- `inventory.json` → `"ci": []`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `Test-Path .github` | command | workflows | false |
| `git ls-files .github` | command | tracked CI | none |
| `package.json` scripts | code | available gates | lint/typecheck/test/build exist |
| `git tag` | command | releases | one tag, no generated artifacts |
| `inventory.json` `ci` | data | confirmation | `[]` |

## Executive Summary

There is **no CI/CD or repository governance**: no `.github/workflows/`, no required status checks, no dependency/security scanning, no release automation, and no CODEOWNERS. The project has all the ingredients for a fast, effective pipeline (`lint`, `typecheck`, `test`, `build` scripts; a lockfile; 109 unit tests) but nothing runs automatically, so quality depends entirely on manual discipline. Branch protection could not be verified from the repository and is recorded as **unverified** rather than assumed absent. This is a P1 governance gap for anything beyond local hobby use: there is no gate preventing a broken `build`/`test` from reaching `master`.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Workflows | `.github/workflows/` | CI | Absent | High | none |
| Required checks | GitHub settings | merge gate | Unverified | High | no local evidence |
| Branch protection | GitHub settings | governance | Unverified | Medium | check remotely |
| CODEOWNERS | (none) | review routing | Absent | Low | single maintainer likely |
| Dependabot/Renovate | (none) | updates | Absent | Medium | see SUPPLY |
| Security scanning | (none) | vuln/SBOM | Absent | Medium | no CodeQL/audit |
| Release automation | (none) | releases | Absent | Low | manual tag |
| PR/issue templates | (none) | process | Absent | Low | — |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| CI workflows | 0 | no `.github` | none | add lint/type/test/build |
| Required checks | 0 | unverified | none | enable in GitHub |
| Branch protection | 0 | unverified | none | protect `master` |
| Dependency updates | 0 | none | none | Dependabot |
| Security scanning | 0 | none | none | CodeQL + `npm audit` |
| Release automation | 1 | tag exists | no artifacts | tag-driven workflow |
| Environment/secret mgmt | 0 | no env | N/A client | — |
| Deployment automation | 0 | none | none | decide host first |

## Detailed Review

### Item: Missing CI despite ready scripts
- Evidence: `package.json` scripts and `package-lock.json`; no workflows.
- Risks: regressions merge freely; claims like "build succeeded" are unverifiable.

### Item: Governance
- Evidence: no CODEOWNERS/templates; remote exists but settings unverified.
- Risks: unknown push protection; no enforced review.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CI-001 | Automated quality gate | `package.json` vs no workflows | none | no CI | P1 | add workflow |
| CI-002 | Branch protection/required checks | no local config | unverified | unknown | P1 | verify + enable |
| CI-003 | Dependency/security scanning | none | none | none | P2 | add |
| CI-004 | Release automation | tag only | manual | no artifacts | P3 | add |

## Findings

### Finding ID: CI-P1-001 - No CI workflows, so lint/typecheck/test/build never run automatically

- Severity: P1
- Confidence: High
- Area: CI
- Evidence:
  - `Test-Path .github` → false; no `.github/workflows/`
  - `inventory.json` → `"ci": []`
  - `package.json` — `lint`, `typecheck`, `test`, `build` scripts exist but are manual
- What is happening: Nothing enforces the project's own quality gate on push/PR.
- Why it matters: Broken `build`/`test`/`typecheck` can reach `master`; the phase reports' "Build ✅" claims cannot be independently confirmed.
- User / business impact: Regression and release risk; slower, trust-based reviews.
- Security / privacy / reliability impact: Reliability and supply-chain hygiene (no audit step).
- Recommended fix: Add `.github/workflows/ci.yml` running `npm ci`, `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` on push/PR to `master`.
- Suggested validation: Open a PR introducing a type error and confirm CI fails the required check.
- Owner suggestion: maintainer/DevOps
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: CI-P1-002 - No repository-enforced review/required checks (branch protection unverified)

- Severity: P1
- Confidence: Low
- Area: CI
- Evidence:
  - No `.github/` CODEOWNERS or templates
  - Branch protection is a GitHub server-side setting; no repository artifact proves it
  - `git remote -v` → `github.com/MaineCyberTech/buddy.git`
- What is happening: It is unknown whether `master` requires reviews or passing checks; no CODEOWNERS routes review.
- Why it matters: Without protection, direct pushes and force-pushes to `master` are possible.
- User / business impact: Governance/release integrity.
- Security / privacy / reliability impact: Change-control gap.
- Recommended fix: Enable branch protection on `master` (require PR, ≥1 review, required CI status checks, no force-push, optionally signed commits); add CODEOWNERS.
- Suggested validation: Attempt an unprotected push in a sandbox; confirm rejected after enabling.
- Owner suggestion: maintainer/DevOps
- Effort estimate: S
- Dependencies: CI-P1-001
- Status: open

### Finding ID: CI-P2-001 - No dependency or security scanning in the pipeline

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - no `.github/workflows/` (no CodeQL, no `npm audit`, no SBOM)
  - `docs/prompts/.../checklists/security-checklist.md` line 3 — "No client secrets" (not automated)
- What is happening: Vulnerable dependencies and secret leaks are not detected automatically.
- Why it matters: Dependency and secret risk is discovered late or never.
- User / business impact: Increased breach/outage likelihood as dependencies age.
- Security / privacy / reliability impact: Supply-chain security.
- Recommended fix: Enable Dependabot security updates + `npm audit --production` in CI; consider CodeQL and `gitleaks`.
- Suggested validation: A known-vulnerable dependency fails the audit step.
- Owner suggestion: DevSecOps
- Effort estimate: S
- Dependencies: CI-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No quality gate | P1 | High | High | CI-P1-001 | add CI |
| Unprotected `master` | P1 | Medium | High | CI-P1-002 | branch protection |
| No dependency/secret scanning | P2 | Medium | Medium | CI-P2-001 | Dependabot/audit |

## Recommendations

### Immediate / Release Blocking
- Add CI and enable required checks before tagging a non-RC release.

### This Week
- Enable branch protection and Dependabot.

### This Month
- Add security scanning and a release workflow.

### Later / Platform Evolution
- Add deployment automation once the target host is chosen.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `ci.yml` with 4 scripts | quality gate | `.github/workflows/ci.yml` | failing PR |
| Dependabot config | updates | `.github/dependabot.yml` | PRs appear |
| CODEOWNERS | review routing | `.github/CODEOWNERS` | review request |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| CI quality gate | P1 | maintainer | S | none |
| Branch protection | P1 | maintainer | S | CI |
| Dependency/security scanning | P2 | DevSecOps | S | CI |
| Release workflow | P3 | maintainer | M | CI |

## Suggested Tests

- CI job matrix (Node LTS) running lint/typecheck/test/build.
- A deliberate-failing PR to prove the gate blocks merge.

## Suggested Documentation Updates

- `CONTRIBUTING.md` describing the PR/CI workflow and required checks.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is branch protection already enabled remotely? | P1 scope | GitHub settings/screenshot |
| Is a deploy target chosen? | deployment automation | decision |

## Appendix

- `git tag` evidence: `v0.1.0-rc1` exists locally; no workflow produces release artifacts, so tag provenance is manual/unverified.
