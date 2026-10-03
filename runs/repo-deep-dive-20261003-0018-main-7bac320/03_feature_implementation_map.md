# Feature Implementation Map

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: FEAT
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/03_feature_implementation_map.md
- Scope limitations: capability map, not product features (the pack has no end-user UI).

## Scope

Map each pack capability to its implementation, docs, tests, and status: run scaffolding, run validation, findings normalization, advisory scoring, dashboards, diffs/CSV, inventory, deterministic checks, org rollup, profiles/lenses, templates, and CI.

## Evidence Reviewed

- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `REFERENCE_CARD.md`
- `tools/` (all), `.github/workflows/deep-dive-deterministic.yml`, `ci/audit.yml`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `CHANGELOG.md` top entry v1.4.1 | doc | change control baseline | no mention of deterministic/rollup/workflow |
| `git log 7bac320..6cada03` | command | new capabilities | 2 commits, no changelog edit in diff |
| `README.md` tools row | doc | documented inventory | lists 12 tools; tree has 11 py + 5 sh |

## Executive Summary

Most core capabilities are implemented and documented. The newest capabilities (deterministic checks, org rollup, org-wide workflow) shipped without changelog, version bump, or README/reference-card updates, violating the pack's own change control. The README tool list is also stale. Completeness is high but traceability is not.

## Inventory

| Capability | Implementation | Docs | Tests | Status |
|---|---|---|---|---|
| Run scaffold | `tools/new_run.py` | README, CONTRIBUTING | `self_test.sh` | implemented; base seed bug (DATA-P1-002) |
| Run validation | `tools/check_run.sh` | REFERENCE_CARD | `self_test.sh` | implemented; bash-only |
| Findings normalize | `tools/collect_findings.py`, `tools/lib_findings.py` | AUTOMATION_GUIDE | `self_test.sh` | implemented; schema drift (DATA-P1-001) |
| Advisory score | `tools/risk_score.py` | REFERENCE_CARD | `self_test.sh` | implemented |
| Dashboard | `tools/render_dashboard.py` | REFERENCE_CARD | `self_test.sh` | implemented |
| Diff / CSV | `tools/diff_runs.py`, `tools/findings_to_csv.py` | AUTOMATION_GUIDE | `self_test.sh` | implemented |
| Inventory | `tools/repo_inventory.py` | AUTOMATION_GUIDE | `self_test.sh` | implemented |
| Deterministic checks | `tools/deterministic_checks.py` | **none** | **none** | implemented, undocumented |
| Org rollup | `tools/aggregate_findings.py` | **none** | **none** | implemented, undocumented |
| Org workflow | `.github/workflows/deep-dive-deterministic.yml` | **none** | **none** | implemented, undocumented |
| Profiles/lenses | `profiles/`, `lenses/` | README | lint | implemented |
| Templates | `templates/` | CONTRIBUTING | lint | implemented |
| CI example | `ci/audit.yml` | README | **none** | unwired (CI-P1-001) |

## Findings

### Finding ID: FEAT-P2-001 - New tools and the org workflow shipped without changelog, version bump, or docs

- Severity: P2
- Confidence: High
- Area: FEAT
- Evidence:
  - `tools/deterministic_checks.py`, `tools/aggregate_findings.py`, `.github/workflows/deep-dive-deterministic.yml` — added in `18e75cb`/`6cada03`
  - `CHANGELOG.md` top entry is v1.4.1; `git diff --stat 7bac320 6cada03` shows no `CHANGELOG.md`/`VERSION` change
  - `README.md`, `REFERENCE_CARD.md`, `CONTRIBUTING.md` — no mention of the new tools/workflow
- What is happening: Commits `18e75cb` and `6cada03` added user-facing capabilities but did not update the changelog, version, README, or reference card.
- Why it matters: `CONTRIBUTING.md` mandates "One change, one changelog entry" and "Version everything".
- User / business impact: Consumers cannot discover the deterministic checks or know which version contains them.
- Security / privacy / reliability impact: The new org-wide PAT workflow is invisible to readers.
- Recommended fix: Add a CHANGELOG entry, bump `VERSION` (and manifest version fields), and list the new tools/workflow in README/REFERENCE_CARD.
- Suggested validation: `tools/lint_pack.sh` passes and CHANGELOG contains the new capability names.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: FEAT-P3-002 - README tool inventory is stale

- Severity: P3
- Confidence: High
- Area: FEAT
- Evidence:
  - `README.md` §Layout lists 12 tools (ends at `run_toolchain.py`)
  - Tree: 11 `.py` + 5 `.sh`; `aggregate_findings.py`, `deterministic_checks.py`, `lib_findings.py`, `self_test.sh` are not listed
- What is happening: The layout table under-describes the tool suite.
- Why it matters: New contributors and agents trust the README as the map.
- User / business impact: Discovery friction only.
- Security / privacy / reliability impact: None direct.
- Recommended fix: Refresh the `tools/` row with the full list.
- Suggested validation: `lint_pack.sh` remains green; manual diff of `ls tools`.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: FEAT-P2-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Undiscoverable capabilities | P2 | High | Medium | FEAT-P2-001 | changelog + docs |

## Recommendations

### This Week
- Backfill changelog/version/docs for the deterministic work.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Update README tools row | accurate map | `README.md` | `ls tools` comparison |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Docs-drift lint (README lists all tools) | P3 | maintainer | S | none |

## Suggested Tests

- Lint: every `tools/*` basename appears in README.

## Suggested Documentation Updates

- `README.md`, `CHANGELOG.md`, `REFERENCE_CARD.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is deterministic checks a base-edition or opt-in capability? | placement in docs/manifests | maintainer intent |

## Appendix

Not applicable.
