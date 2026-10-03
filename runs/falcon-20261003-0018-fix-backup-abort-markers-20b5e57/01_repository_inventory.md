# Comprehensive Repository Inventory

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: INV
- Output path: docs/audits/{name}/{run}/01_repository_inventory.md
- Scope limitations: static/read-only repository review; no lab host, no Docker, no network. The lab's raw evidence tree is partly off-repo, so live-dependent items are `unverified`.

## Scope

Reviewed the full tree at `20b5e57`: root configs, bootstrap stages, automation/validation, CI, compose/config, pins/sbom, ledgers, docs, and the committed `review-package/` tree. Starting point was the run's `inventory.json` (6,994 files / 1,008,972 lines). Did not execute lab scripts; did not modify the repository.

## Evidence Reviewed

- `inventory.json` (run folder) — totals, extensions, dir sizes, workflows, secret-adjacent files.
- `README.md`, `REPOSITORY.md`, `docs/CURRENT_STATE.md`.
- `ledgers/` (gate_ledger.csv, risk_register.md, exception_register.md, evidence_index.csv, gate/phase9 ledgers).
- `pins/images.lock`, `sbom/`, `closeout/`, `review-package/`.
- Prior run records under `docs/audits/repo-deep-dive/`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `inventory.json` totals | Generated | Establish size/shape | 6,994 files, 1,008,972 lines |
| `review-package/` dir listing | Tree | Detect duplication | 3,272 files vs source tree |
| `sbom/` listing + `vuln-summary.csv` | Generated | Provenance/freshness | 39 committed JSON, scan dated 2026-09-22 |
| `closeout/FINAL_RESPONSE.json`, `PACKAGE_DIGEST.txt` | Generated | Delivery binding | see HYG report |

## Executive Summary

The repository is a documentation- and evidence-heavy monitoring-lab build, not a typical application monorepo. Roughly four fifths of the tree is generated or derived content: `.out` captures (2,092), `.json` (2,218), and a committed `review-package/` copy (3,272 files) that replicates the source tree. This is a deliberate "evidence-first" design, but it means most committed bytes are stale-able artifacts with no in-repo regeneration/drift gate. Source-of-truth code is small and well-organized (`bootstrap/`, `automation/validation/`, `config/`, `compose/`, `ci/`). The inventory itself is sound; the risks are artifact staleness and the size of the committed duplicate.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Bootstrap stages | `bootstrap/*.sh` | Host/stack provisioning | Functional | Medium | Source, reviewed |
| Validation tooling | `automation/validation/*` | Health, drills, scans | Functional | Medium | ~90 scripts |
| Offline tests | `automation/validation/tests/*` | Regression suites | Functional | Low | 32 suites; auto-discovered by `ci/validate.py` |
| CI | `.github/workflows/*`, `ci/*` | Static gate | Functional | Medium | see CI report |
| Compose | `compose/central`, `compose/probe`, `compose/mct` | Runtime topology | Functional | High | see ARCH/SEC |
| Pins/SBOM | `pins/`, `sbom/` | Supply chain | Partial | High | see SUPPLY |
| Committed evidence | `evidence/` (2,227 files) | Raw captures | Generated | Medium | large, partly host-absolute |
| Review package | `review-package/` (3,272 files) | Delivery artifact | Stale copy | High | see HYG-P1-001 |
| Ledgers | `ledgers/` | Records of truth | Maintained | Low | append-only |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Root configs | 4 | `.gitattributes`, `.gitleaks.toml`, `README` | none material | — |
| Package/workspace files | 3 | `ci/requirements-ci.txt` hash-pinned | no top-level workspace manifest | document CI deps |
| Applications | 3 | bootstrap/automation are the "app" | no single entrypoint | keep `run-all-deploy.sh` canonical |
| API services | 3 | edge/enroll APIs | contracts partly out of repo | see API report |
| Workers | 3 | systemd units in `config/systemd` | graceful-stop gaps | see ARCH |
| Shared packages | 2 | `bootstrap/lib.sh`, `automation/validation/lib` | vendored `mct` duplication | subtree policy |
| Database/migrations | 3 | OpenSearch ISM/index scripts | retention gaps | see DATA |
| GitHub metadata | 3 | workflows, CODEOWNERS, dependabot | branch protection unenforced | see CI |
| Tests | 3 | 32 offline suites | no e2e gate for backup | see TEST |
| Docs | 4 | extensive, current-state page | some stale cross-links | see HYG |
| Assets/public files | 3 | configs, dashboards | — | — |
| Generated artifacts | 2 | 2,092 `.out`, 39 SBOM, review-package | no regen/drift check | add regen binding |

## Findings

### Finding ID: INV-P2-001 - Repository is majority generated/derived content with no in-repo regeneration or drift check

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `inventory.json` — 6,994 files; `.out` 2,092, `.json` 2,218, `.md` 1,605; `review-package/` 3,272 files; `evidence/` 2,227 files
  - `automation/validation/build_review_package.sh` — regeneration exists but is not gated
- What is happening: Most committed bytes are captures/derived artifacts. Regeneration scripts exist but nothing verifies the committed copies match a rebuild at HEAD.
- Why it matters: Stale or hand-edited generated artifacts can silently contradict their sources of truth (the doctrine says the ledger wins).
- User / business impact: Audit/delivery consumers can be misled by stale machine artifacts.
- Security / privacy / reliability impact: Not directly exploitable; undermines trust and reproducibility.
- Recommended fix: Add a CI check that regenerates a deterministic subset (manifests/digests/closeout) and fails on drift, or mark generated trees as build outputs and stop committing them.
- Suggested validation: Extend `ci/validate.py` with a `generated-drift` check; run in CI.
- Owner suggestion: release owner
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: INV-P3-001 - Legacy host-absolute evidence paths require manual rewrite to resolve in a clone

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `inventory.json` — secret-adjacent `evidence/raw/**/*.meta.json`
  - `ledgers/evidence_index.csv` — rows referencing `/home/user/...` / `/srv/falcon/...`
- What is happening: Evidence metadata records absolute lab paths that do not exist in a fresh checkout.
- Why it matters: Off-host review cannot resolve captures without manual path rewriting.
- User / business impact: Slows independent review.
- Security / privacy / reliability impact: Low; provenance clarity only.
- Recommended fix: Record repo-relative paths in metadata, or add a resolver script.
- Suggested validation: `automation/validation/check_evidence_index.py` (already present) extended to warn on non-repo-relative paths.
- Owner suggestion: release owner
- Effort estimate: S
- Dependencies: None
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale generated artifact mistaken for current | P2 | Medium | Medium | inventory.json | drift gate (INV-P2-001) |
| Review cannot resolve evidence off-host | P3 | High | Low | evidence meta | relative paths |

## Recommendations

### Immediate / Release Blocking
None from this report.

### This Week
- Add the generated-artifact drift gate.

### This Month
- Convert evidence metadata to repo-relative paths.

### Later / Platform Evolution
- Define retention for committed evidence and review-package.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Document which trees are generated | Stops hand-edits | `REPOSITORY.md` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Generated-artifact drift gate | P2 | release owner | M | CI |
| Relative evidence paths | P3 | release owner | S | — |

## Suggested Tests

- CI drift check for `closeout/`, `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`.

## Suggested Documentation Updates

- `REPOSITORY.md` — classify each top-level tree as source vs generated.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which evidence files are safely deletable? | Repo size | retention policy |

## Appendix

Mermaid (source vs generated):

```mermaid
graph LR
  SRC[bootstrap/ automation/ ci/ config/ compose/] --> GEN[review-package/ evidence/ sbom/ closeout/]
  GEN --> DEL[delivery archive]
```
