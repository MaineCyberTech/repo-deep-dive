# Repository Hygiene and Maintainability Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: HYG
- Output path: docs/audits/{name}/{run}/21_repo_hygiene_maintainability.md
- Scope limitations: no bash host, so `verify_publication_chain.sh` could not be executed; its result is inferred from artifacts.

## Scope

Reviewed delivery/publication artifacts (`PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `closeout/FINAL_RESPONSE.json`), the committed `review-package/` tree, large generated files, and the secret-scanner path handling.

## Evidence Reviewed

- `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `closeout/FINAL_RESPONSE.json`.
- `review-package/` (3,272 files; matches `review_package_entries=3272`).
- `automation/validation/verify_publication_chain.sh`, `check_digest_binding.py`.
- `automation/validation/secret_scan.py` (path normalization).
- `sbom/` (39 JSON, up to ~122 KB each).

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `PACKAGE_DIGEST.txt` | Generated | Delivery binding | commit `b595354f...` |
| `closeout/FINAL_RESPONSE.json` | Generated | Verdict binding | commit `605fc100...` |
| `git rev-parse HEAD` | Git | Current commit | `20b5e57` |
| `review-package` file count | Tree | Manifest agreement | 3272 = declared |
| `secret_scan.py` L269 | Source | Path portability | normalizes `\` → `/` |

## Executive Summary

The release-integrity defect that drove the prior NO-GO is still present at this commit: the delivery digest and closeout name commits (`b595354f`, `605fc100`) that are not the audited HEAD (`20b5e57`), so the delivered bytes are not provably bound to the tree under review. The manifest entry count (3,272) matches the committed `review-package/`, so the package copy is internally consistent — but a committed copy of the whole tree remains a stale-able duplicate. The scanner path-portability fix landed and is verified. Large generated SBOM/vulnerability JSON remain committed.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Package digest | `PACKAGE_DIGEST.txt` | delivery binding | Mismatched | High | `b595354f` |
| Closeout | `closeout/FINAL_RESPONSE.json` | verdict | Mismatched | High | `605fc100` |
| Review package | `review-package/` | delivery copy | Present | Medium | 3272 files |
| Chain verifier | `verify_publication_chain.sh` | drift check | Present | Medium | not run here |
| SBOM JSON | `sbom/*.cdx.json` | provenance | Committed | Low | ~3 MB total |
| Scanner | `secret_scan.py` | secrets | Fixed | Low | normalized paths |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Delivery binding | 1 | digest vs HEAD | not bound | HYG-P0-001 |
| Chain verification | 2 | verifier present | result unknown/failing | HYG-P0-002 |
| Generated tree hygiene | 2 | review-package | stale duplicate | HYG-P1-001 |
| Secret scanning | 4 | secret_scan.py | — | — |
| Repo size/maintainability | 3 | 39 SBOM | large files | HYG-P2-001 |
| Docs | 4 | extensive | minor | — |

## Findings

### Finding ID: HYG-P0-001 - Publication digest and closeout declare commits that do not match the audited tree

- Severity: P0
- Confidence: High
- Area: HYG
- Evidence:
  - `PACKAGE_DIGEST.txt` — `repository_commit=b595354f6fb3252300087e8e040b77a64f37311d`, `DELIVERED_PACKAGE_COMMIT=b595354f...`
  - `closeout/FINAL_RESPONSE.json` — `"commit": "605fc100a23ef49af09f2935736193889fd3bd64"`
  - `git rev-parse HEAD` → `20b5e57`
  - `PACKAGE_DIGEST.txt` — `review_package_entries=3272` (matches the committed tree)
- What is happening: The two machine artifacts name different commits, neither of which is the audited HEAD. The package manifest is internally consistent but not bound to this commit.
- Why it matters: A production-readiness claim requires the delivered bytes to be provably the reviewed bytes.
- User / business impact: The approval cannot be substantiated against this tree.
- Security / privacy / reliability impact: Release-integrity failure.
- Recommended fix: Rebuild the review package at a frozen commit; regenerate `FINAL_RESPONSE.json` and `PACKAGE_DIGEST.txt` from the same commit; publish in the documented order; add a CI equality test binding digest↔closeout↔package manifest↔HEAD.
- Suggested validation: `verify_publication_chain.sh` returns 0 from a full clone; CI digest-binding test passes.
- Owner suggestion: owner
- Effort estimate: M
- Dependencies: release review flow
- Status: partially-fixed

### Finding ID: HYG-P0-002 - The mandated publication-chain verifier could not be reproduced and the chain is not bound to HEAD

- Severity: P0
- Confidence: Medium
- Area: HYG
- Evidence:
  - `automation/validation/verify_publication_chain.sh` — exists and is wired into `.github/workflows/validate.yml` (lines 101-106)
  - `PACKAGE_DIGEST.txt` vs `closeout/FINAL_RESPONSE.json` — commit mismatch (see HYG-P0-001)
  - Environment: no usable `bash` on this audit host, so the verifier could not be executed
- What is happening: The verifier is present but its result is unknown here; the static commit mismatch means at least the binding check cannot pass against HEAD.
- Why it matters: The docs/summary promise a passing chain; the artifacts contradict.
- User / business impact: False assurance.
- Security / privacy / reliability impact: Release integrity.
- Recommended fix: Same rebuild/rebind as HYG-P0-001; record the verifier output as evidence at the delivering commit.
- Suggested validation: Run `bash automation/validation/verify_publication_chain.sh` and capture exit 0.
- Owner suggestion: owner
- Effort estimate: M
- Dependencies: HYG-P0-001
- Status: open

### Finding ID: HYG-P1-001 - Committed `review-package/` is a stale snapshot duplicate of the source tree

- Severity: P1
- Confidence: High
- Area: HYG
- Evidence:
  - `review-package/` — 3,272 files duplicating `bootstrap/`, `automation/`, `docs/`, `ledgers/`, etc.
  - `automation/validation/build_review_package.sh` — regeneration script; no drift check binds the copy to HEAD
  - Prior 2026-10-02 run `HYG-P1-001` (open)
- What is happening: A full copy of the tree is committed and served as the delivery artifact.
- Why it matters: It can silently diverge from source; reviewers may read the stale copy.
- User / business impact: Wasted space; review against wrong bytes.
- Security / privacy / reliability impact: Provenance risk.
- Recommended fix: Build the package as a CI artifact (not committed) or add a drift check that regenerates and diffs.
- Suggested validation: `ci/validate.py` fails when `review-package/` differs from a fresh build.
- Owner suggestion: owner
- Effort estimate: M
- Dependencies: build script
- Status: open

### Finding ID: HYG-P1-002 - Secret-scanner path allowlist was not separator-portable

- Severity: P1
- Confidence: High
- Area: HYG
- Evidence:
  - `automation/validation/secret_scan.py` lines 266-269 — normalizes `p.replace("\\", "/")` before `ALLOW_PATH.search`
- What is happening: The fix is present; Windows paths now match the `/`-based allowlist patterns.
- Why it matters: Prior false failures on Windows checkouts are resolved.
- User / business impact: None at this commit.
- Security / privacy / reliability impact: Dev/CI parity.
- Recommended fix: None.
- Suggested validation: `automation/validation/tests/secret_scan_test.sh` on Windows.
- Owner suggestion: owner
- Effort estimate: S
- Dependencies: None
- Status: verified-fixed

### Finding ID: HYG-P2-001 - Large generated SBOM/vulnerability JSON committed (39 files, up to ~122 KB each)

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `sbom/` — 39 committed JSON (e.g. `binwiederhier_ntfy_v2.28.0.cdx.json` 121,887 bytes)
  - `sbom/vuln/` — per-image vulnerability JSON
- What is happening: Generated security artifacts are committed rather than published as CI artifacts.
- Why it matters: Repo bloat and staleness; they can be mistaken for current.
- User / business impact: Maintainability.
- Security / privacy / reliability impact: Low.
- Recommended fix: Publish SBOM/vuln JSON as CI artifacts/release assets; keep only hashes/manifest in-repo.
- Suggested validation: CI uploads artifacts and verifies hashes.
- Owner suggestion: owner
- Effort estimate: S
- Dependencies: CI artifacts
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unbound delivered bytes | P0 | High | High | digest vs HEAD | HYG-P0-001 |
| Stale review copy | P1 | Medium | Medium | review-package | HYG-P1-001 |
| Large generated files | P2 | High | Low | sbom | HYG-P2-001 |

## Recommendations

### Immediate / Release Blocking
- Rebuild/rebind the delivery chain (HYG-P0-001/002).

### This Week
- Add a package drift check (HYG-P1-001).

### This Month
- Move SBOM output to CI artifacts (HYG-P2-001).

### Later / Platform Evolution
- Generated-artifact policy (INV-P2-001).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Bind digest to HEAD in CI | Prevents recurrence | ci/validate.py | test fails on drift |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rebuild/rebind | P0 | owner | M | review flow |
| Package drift check | P1 | owner | M | build script |

## Suggested Tests

- Digest↔closeout↔package↔HEAD equality test (already drafted as `digest_binding_check_test.sh`).

## Suggested Documentation Updates

- Align `PACKAGE_DIGEST.txt` provenance with the actual HEAD.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which commit is the true delivered tree? | Approval binding | release review artifact |

## Appendix
Not applicable.
