# 10 GitHub Actions, CI/CD & Governance

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

CI/CD workflows, permissions, action pinning, branch/merge governance, and deployment authority. Read-only; GitHub repository settings are not visible from the clone.

## Evidence Reviewed

- `.github/workflows/ci-foundation.yml`
- `.github/dependabot.yml`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`
- `CONTRIBUTING.md`, `AGENTS.md`, `README.md`
- `scripts/verify-all.sh`, `scripts/bundle-secret-gate.mjs`

## Verification Performed

- Read the single workflow end-to-end: triggers (`push`, `pull_request`), `permissions: contents: read`, three jobs (`foundation`, `migrations`, `e2e`).
- Confirmed no deployment/publish step and no repository secrets referenced.
- Checked action references: `actions/checkout@v4`, `actions/setup-node@v4` (tags, not SHAs).
- Searched the tree for branch-protection/required-check documentation — none found.

## Executive Summary

The CI workflow is intentionally minimal and least-privilege (`contents: read`, no secrets, no deploy authority), which matches the single-host manual deploy model and is a good posture. Governance gaps are process-level: there is no in-repo evidence that `main` is protected with required status checks, no deployment environment/gate, and no dependency-audit or repository secret scan in the pipeline. Actions are pinned by mutable tags rather than commit SHAs, which is a supply-chain weakness for a security-conscious repo.

## Inventory

| Job | Steps | Permissions | Secrets |
|---|---|---|---|
| foundation | npm ci, typecheck, lint, format, test, integration, build, compose config, secret gate | `contents: read` | none |
| migrations | fresh Postgres 17, apply all migrations | `contents: read` | none |
| e2e | chromium Playwright | `contents: read` | none |
| deploy | none (manual on host) | — | — |

## Findings

### Finding ID: CI-P1-001 - No evidence of branch protection or required status checks on `main`

- Severity: P1
- Confidence: Medium
- Area: CI
- Evidence:
  - `.github/workflows/ci-foundation.yml` triggers on `push` and `pull_request` with no path/branch filters
  - `.github/CODEOWNERS` sets `* @MaineCyberTech`
  - No `branch_protection_recommendation.md` or equivalent artifact found in the tree
- What is happening: Nothing in the repository demonstrates that `main` rejects un-reviewed or red-CI merges; branch protection is a server-side setting not captured here.
- Why it matters: All the CI gates are advisory if merges are not blocked on them.
- User / business impact: A defective change can reach the certified host.
- Security / privacy / reliability impact: Governance/assurance.
- Recommended fix: Enforce branch protection (require PR review + the `foundation`/`migrations` checks), capture a screenshot/export as evidence, and keep CODEOWNERS current.
- Suggested validation: Attempt to merge with a failing check — it is blocked.
- Owner suggestion: Owner
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: CI-P2-001 - No dependency-vulnerability audit or repository secret scan in CI

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/ci-foundation.yml` — no `npm audit`, OSV, or secret-scan step
  - `package.json` `audit` script exists but is not invoked by CI or `verify-all.sh`
  - `scripts/bundle-secret-gate.mjs` scans only built bundles
- What is happening: Vulnerabilities/secret leaks are checked only by the daily host assurance lane (`scripts/assurance/assurance.sh`), not per-PR.
- Why it matters: A vulnerable dependency or committed secret can merge before the next daily lane.
- User / business impact: Delayed detection.
- Security / privacy / reliability impact: Supply-chain/secret exposure window.
- Recommended fix: Add `npm audit --omit=dev` (non-blocking advisory + blocking on high/critical policy) and a pinned secret scanner to CI.
- Suggested validation: CI surfaces a known-vulnerable fixture.
- Owner suggestion: CI/security engineer
- Effort estimate: S
- Dependencies: SEC-P2-002
- Status: open

### Finding ID: CI-P2-002 - GitHub Actions are pinned by mutable tags, not commit SHAs

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/ci-foundation.yml` lines 20, 23 — `actions/checkout@v4`, `actions/setup-node@v4`
- What is happening: Third-party actions resolve to a moving tag.
- Why it matters: A compromised/retagged action runs with the workflow's (read-only) token; the repo elsewhere pins container images by digest, so this is inconsistent.
- User / business impact: CI integrity risk.
- Security / privacy / reliability impact: Supply-chain.
- Recommended fix: Pin actions to full commit SHAs (Dependabot can maintain them).
- Suggested validation: Workflow contains 40-char SHAs.
- Owner suggestion: CI engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: CI-P3-001 - CI produces no durable artifacts bound to the commit

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/ci-foundation.yml` — no `actions/upload-artifact`
  - Run folder has no CI log/test artifact for 59e12b9
- What is happening: Test/build results are not retained or bound to the SHA.
- Why it matters: Release confidence cannot be independently sampled after the fact.
- User / business impact: Slower audits and incident forensics.
- Security / privacy / reliability impact: Assurance.
- Recommended fix: Upload coverage/test results (and later SBOM) as workflow artifacts.
- Suggested validation: Artifact downloadable for a given SHA.
- Owner suggestion: CI engineer
- Effort estimate: S
- Dependencies: TEST-P2-001
- Status: open

## Risks

- R-CI-1: Gates advisory without branch protection (P1).
- R-CI-2: Per-PR supply-chain/secret checks absent (P2).
- R-CI-3: Mutable action pins (P2).

## Recommendations

1. Protect `main` with required checks and capture evidence.
2. Add audit + secret scan to CI.
3. SHA-pin actions; upload artifacts.

## Quick Wins

- SHA-pin the two actions (S). Protect `main` (S).

## Hardening Backlog

- Deployment environment with manual approval + OIDC (only if/when deploy moves to CI).

## Suggested Tests

- Branch-protection drill; CI pipeline self-test.

## Suggested Documentation Updates

- `CONTRIBUTING.md`: state required checks.

## Open Questions

- Are required checks configured in the GitHub org/repo settings? (`Unknown` — not visible from clone.)

## Appendix

- `.github/dependabot.yml` covers npm + github-actions weekly.
