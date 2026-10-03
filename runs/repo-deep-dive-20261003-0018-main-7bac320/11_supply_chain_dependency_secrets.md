# Supply Chain, Dependencies, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: SUPPLY
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/11_supply_chain_dependency_secrets.md
- Scope limitations: no package manager; dependency surface is GitHub Actions + downloaded CLI tools.

## Scope

Third-party dependencies (GitHub Actions, downloaded actionlint/gitleaks), lockfiles, SBOM, license, and secret material. Python tools are stdlib-only, so no language lockfile exists.

## Evidence Reviewed

- `.github/workflows/deep-dive-deterministic.yml`
- `ci/audit.yml`
- `git ls-files` secret/license sweep
- `PACK_DIGEST.txt` (integrity manifest)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git ls-files` grep | command | secrets/license | no `.env`/keys; no `LICENSE` |
| action refs in workflows | code | pinning | `@v4`/`@v5` mutable tags |
| no Dependabot config | scan | update automation | absent |
| no SBOM artifact | scan | provenance | absent |

## Executive Summary

The pack has no language dependencies, which is a strength, but it consumes mutable CI inputs: GitHub Actions pinned by major tag and two binaries downloaded from "latest"/`main` without checksums. There is no Dependabot, SBOM, or license policy enforcement, and no LICENSE file. No secret values are committed.

## Inventory

| Dependency | Where | Pin | Risk |
|---|---|---|---|
| `actions/checkout` | both workflows | `@v4` | mutable |
| `actions/setup-python` | `ci/audit.yml` | `@v5` | mutable |
| `actions/upload-artifact` | both | `@v4` | mutable |
| actionlint download | deterministic workflow | `main` branch | high |
| gitleaks download | deterministic workflow | `releases/latest` | high |
| Python libs | tools | stdlib only | none |
| License | root | **absent** | policy |
| SBOM | — | **absent** | provenance |

## Findings

### Finding ID: SUPPLY-P1-001 - GitHub Actions and downloaded tools are unpinned (mutable tags/branches)

- Severity: P1
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` lines 43, 103 — `actions/checkout@v4`, `actions/upload-artifact@v4`
  - same file lines 51-56 — actionlint from `main`, gitleaks from `releases/latest`
  - `ci/audit.yml` lines 37, 39, 60 — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`
- What is happening: CI dependencies are referenced by mutable tags/branches rather than immutable commit SHAs or versioned+checksummed artifacts.
- Why it matters: A tag/branch can be moved to inject code; this is the classic GitHub Actions supply-chain attack. The pack's own prompt 35 demands pinning.
- User / business impact: Org-wide CI compromise.
- Security / privacy / reliability impact: Reproducibility and integrity loss.
- Recommended fix: Pin actions by full commit SHA; pin actionlint/gitleaks by version+sha256 (ties to SEC-P1-001).
- Suggested validation: Every `uses:` has a 40-hex SHA; download URLs are versioned and checksum-verified.
- Owner suggestion: CI owner
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: SUPPLY-P2-002 - No dependency-update automation

- Severity: P2
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `git ls-files` — no `.github/dependabot.yml`, no `renovate.json`
  - `docs/AUTOMATION_GUIDE.md` line 61 — describes Dependabot absence as a P2
- What is happening: Action pins (once added) and any future dependencies won't receive automated updates.
- Why it matters: Stale actions/binaries accumulate known vulnerabilities.
- User / business impact: Manual upkeep burden.
- Security / privacy / reliability impact: Delayed patching.
- Recommended fix: Add `.github/dependabot.yml` covering `github-actions`.
- Suggested validation: Dependabot opens PRs.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: SUPPLY-P1-001
- Status: open

### Finding ID: SUPPLY-P2-003 - No SBOM or license policy is enforced despite prompt 35

- Severity: P2
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `prompts/35_sbom_license_policy.md` — requires an SBOM/license recommendation
  - no SBOM artifact or generation step in either workflow
  - `git ls-files` — no license file
- What is happening: The pack prescribes SBOM/license gates for target repos but applies none to itself.
- Why it matters: Inconsistent with its own quality bar; consumers cannot verify component provenance.
- User / business impact: License/compliance ambiguity for adopters.
- Security / privacy / reliability impact: Low-medium.
- Recommended fix: Add a LICENSE, a documented license for Actions/tools, and an SBOM step (e.g. `anchore/sbom-action`) or a documented N/A rationale.
- Suggested validation: Release artifact includes an SBOM; license policy documented.
- Owner suggestion: pack maintainer
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: SUPPLY-P3-004 - No LICENSE file

- Severity: P3
- Confidence: High
- Area: SUPPLY
- Evidence:
  - repo root listing — no `LICENSE`; `GIT ls-files` confirms
  - `tools/deterministic_checks.py` `check_hygiene` — emits `GIT-P3` "No LICENSE file"
- What is happening: The pack ships without a license.
- Why it matters: Reuse rights are undefined; the pack's own deterministic check flags this.
- User / business impact: Adoption friction.
- Security / privacy / reliability impact: None.
- Recommended fix: Add an explicit LICENSE.
- Suggested validation: License file present and referenced in README.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| CI supply-chain compromise | P1 | Medium | High | SUPPLY-P1-001 | SHA/checksum pins |
| Stale vulnerable actions | P2 | Medium | Medium | SUPPLY-P2-002 | Dependabot |
| License ambiguity | P2 | Medium | Low | SUPPLY-P2-003/004 | add LICENSE/policy |

## Recommendations

### Immediate / Release Blocking
- Pin CI dependencies by SHA/checksum.

### This Week
- Add Dependabot and a LICENSE.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| SHA-pin `uses:` | immutability | workflows | uses refs are SHAs |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| SBOM generation | P2 | maintainer | M | none |

## Suggested Tests

- Lint: every `uses:` ends with `@<40-hex>`.
- Download checksum mismatch fails job.

## Suggested Documentation Updates

- README "Supply chain" note; `docs/AUTOMATION_GUIDE.md` pin guidance.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the pack intended to be public? | license choice | maintainer intent |

## Appendix

Secret sweep: `git ls-files` shows no `.env`, `*.pem`, `id_rsa`, or key material; the only secret-like artifact is CI token usage (SEC-P1-002).
