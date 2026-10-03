# Repository Hygiene, Maintainability, and Code Health Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: HYG
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/21_repo_hygiene_maintainability.md
- Scope limitations: static review; no long-term churn/ownership analytics.

## Scope

Reviewed naming/structure, dead/duplicated code, committed generated artifacts, logging consistency, config sprawl, documentation drift, and root-level project metadata.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Full `git ls-files` tree | Manifest | Structure/dead files | 1,288 files |
| `src/**` (23 files, 4,303 LOC) | Source | Complexity | cohesive |
| `docs/GITHUB_CI.md` vs workflows | Docs | Drift | cadence, counts |
| `docs/CURRENT_STATE.md` | Docs | Stale counts | 197 vs 253 |
| `automation/validation/inventory_metrics.py` | Source | Hardcoded endpoints | host drift |
| `closeout/FINAL_RESPONSE.json`, `docs/audits/**` | Generated | Committed derived | staleness |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Doc-vs-code compare | Static | Drift | multiple mismatches |
| Dead-code grep | Static | `purge_expired` | unwired (DATA-P3-001) |
| Endpoint inventory | Static | Hardcoded IPs | `10.11.12.211` vs `10.99.0.31` |
| Root metadata check | Static | LICENSE absent | — |

## Executive Summary

The codebase is small, cohesive, and readable; `ruff` (E9,F,B) runs in CI and the directory layout matches its documentation. The main maintainability burdens are documentation drift (test counts, Dependabot cadence, sensor endpoints), a large committed evidence tree (INV-P2-001), committed generated artifacts that can go stale, and the absence of root-level project metadata (LICENSE/CONTRIBUTING/pyproject). No duplicated source modules or large-file hotspots were found.

## Inventory

| Item | Path | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Structure | `src/`, `api/`, `image/`, `automation/` | Layout | Clear | Low | matches README |
| Source size | `src/**` | 4,303 LOC | Small | Low | cohesive |
| Doc drift | `docs/GITHUB_CI.md`, `CURRENT_STATE.md` | Claims | Stale | Med | HYG-P2-001 |
| Hardcoded endpoints | `inventory_metrics.py` | Sensor list | Drifted | Low | HYG-P3-001 |
| Generated artifacts | `closeout/`, `docs/audits/` | Derived | Committed | Med | HYG-P2-002 |
| Root metadata | root | LICENSE etc. | Absent | Low | HYG-P3-002 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Folder/file naming | 4 | consistent | — | — |
| Duplicate/dead code | 4 | none major | `purge_expired` | DATA-P3-001 |
| Generated/build artifacts | 2 | evidence/closeout committed | staleness | INV/HYG |
| Imports/circular deps | 4 | clean | — | — |
| Large files/components | 4 | manageable | — | — |
| Type safety | 3 | hints, no mypy | no gate | optional |
| Error handling | 4 | consistent | — | — |
| TODO/FIXME | 4 | none significant | — | — |
| Logging consistency | 3 | mixed print/stderr | — | minor |
| Config sprawl | 3 | several JSONs | duplication | minor |
| Test utilities | 4 | shared | — | — |
| Docs drift | 2 | multiple | stale counts | HYG-P2-001 |
| Changelog/ADRs | 4 | decision log | — | — |

## Detailed Review

### Item: Documentation drift

- Evidence: `docs/GITHUB_CI.md` (163 tests; Dependabot every 20 min), `docs/CURRENT_STATE.md` (197 tests), actual suite 253 and cron daily.
- Gap: summary docs are hand-maintained and lag code.
- Risk: HYG-P2-001 (consolidates TEST-P2-001 and CI-P3-001).

### Item: Hardcoded sensor endpoints

- Evidence: `inventory_metrics.py` — SENSORS includes `("zero", "10.11.12.211", ...)` while `AGENTS.md`/`CURRENT_STATE.md` give the Zero W tunnel `10.99.0.31`.
- Gap: endpoint list is edited by hand and has drifted.
- Risk: HYG-P3-001.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| HYG-001 | Naming | tree | consistent | — | — | — |
| HYG-002 | Dead code | grep | minor | `purge_expired` | P3 | wire/remove |
| HYG-003 | Generated artifacts | evidence/closeout | hash/guard some | others stale | P2 | guard/drop |
| HYG-004 | Imports | src | clean | — | — | — |
| HYG-005 | Large files | src | small | — | — | — |
| HYG-006 | Type safety | hints only | partial | no mypy | P3 | optional |
| HYG-007 | Error handling | consistent | good | — | — | — |
| HYG-008 | TODO/FIXME | grep | clean | — | — | — |
| HYG-009 | Logging | print/stderr | mixed | — | P3 | minor |
| HYG-010 | Config sprawl | JSONs | several | hardcoded | P3 | config mgmt |
| HYG-011 | Docs drift | docs | multiple | stale | P2 | HYG-P2-001 |
| HYG-012 | Changelog/ADRs | decision log | present | — | — | — |

## Findings

### Finding ID: HYG-P2-001 - Summary documentation drifts from the code (test counts, Dependabot cadence)

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `docs/GITHUB_CI.md` — "163 tests"; "sweep (every 20 minutes)"
  - `docs/CURRENT_STATE.md` — "197 tests OK"
  - `.github/workflows/validate.yml` / `dependabot-merge.yml` — suite is 253 tests; cron `23 5 * * *`
  - `docs/security/BRANCH_PROTECTION.md` — "163 tests"
- What is happening: authoritative-looking docs disagree with the code they describe.
- Why it matters: the repo's doctrine is evidence-first and machine-readable; stale prose undermines that.
- User / business impact: reviewers/operators are misled.
- Security / privacy / reliability impact: low.
- Recommended fix: derive counts from CI artifacts, link them, and add a docs-drift check where feasible.
- Suggested validation: manual review against the current workflow/test run.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: HYG-P2-002 - Committed derived artifacts (audit mirrors, closeout response, evidence) can go stale

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `closeout/FINAL_RESPONSE.json` (generated by `closeout/generate_final_response.py`)
  - `docs/audits/repo-deep-dive/20261002-0630-edge-f6f1610/**` (frozen mirror)
  - `evidence/` (900 files)
  - `config/grafana/edge-fleet-dashboard.json`
- What is happening: several derived artifacts are committed without a regeneration/`--check` guard (only the generated models/schemas are guarded).
- Why it matters: readers may treat stale derived output as current.
- User / business impact: wrong decisions from stale data.
- Security / privacy / reliability impact: low.
- Recommended fix: add regeneration checks for `FINAL_RESPONSE.json`/dashboard, or mark audit mirrors as immutable snapshots with a clear "frozen at <sha>" header.
- Suggested validation: mutate the source of a derived artifact and confirm a check fails.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: HYG-P3-001 - Hardcoded, drifted sensor endpoint/key list in the inventory metrics collector

- Severity: P3
- Confidence: High
- Area: HYG
- Evidence:
  - `automation/validation/inventory_metrics.py` — `SENSORS` hardcodes `10.11.12.158`, `10.99.0.32`, `10.11.12.211` and delivery key filenames
  - `AGENTS.md` / `docs/CURRENT_STATE.md` — Zero W tunnel is `10.99.0.31`, LAN `10.11.12.211` is the Zero's LAN address
- What is happening: endpoint/key values are duplicated in code and docs and have drifted.
- Why it matters: the collector reads the wrong/old address after a reflash and silently reports down.
- Security / privacy / reliability impact: monitoring inaccuracy.
- Recommended fix: load sensors from a single config file (or the control-plane registry) instead of literals.
- Suggested validation: unit test that the collector reads its config and tolerates unknown sensors.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Doc drift | P2 | High | Misinformation | docs vs code | derive/link |
| Stale derived artifacts | P2 | Medium | Wrong decisions | closeout/mirrors | guards |
| Hardcoded endpoints | P3 | Medium | Monitoring miss | inventory_metrics | config file |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Correct the stale doc counts/cadence.

### This Month
Add regeneration guards for derived artifacts; externalize sensor config.

### Later / Platform Evolution
Add `pyproject.toml` + optional mypy gate; split evidence storage.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix test count/cadence | accuracy | `docs/GITHUB_CI.md` | review |
| Mark mirrors frozen | clarity | `docs/audits/**` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Derived-artifact guards | P2 | build-agent | S | none |
| Sensor config externalization | P3 | build-agent | S | none |
| Packaging metadata | P3 | build-agent | S | none |

## Suggested Tests

- Docs-drift check for generated counts (where derivable).
- Collector config test.

## Suggested Documentation Updates

- Add a dated "generated artifacts" section to `docs/README.md`.
- Add root `LICENSE`/proprietary notice and `CONTRIBUTING.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which docs are authoritative vs historical? | drift policy | owner decision |
| Is a Windows dev workflow intended? | platform guards | owner decision |

## Appendix

No duplicated source modules were found; `src/` is 4,303 LOC across 23 files. `ruff --select E9,F,B` passes in CI; `shellcheck --severity=warning` runs on shell. Root lacks `LICENSE`, `CONTRIBUTING.md`, and `pyproject.toml`.
