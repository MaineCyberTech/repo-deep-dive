# Observability, Monitoring, and Incident Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: OBS
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/14_observability_monitoring_incident_readiness.md
- Scope limitations: no running service; observability applies to the toolchain and scheduled CI.

## Scope

The pack's ability to detect and triage failures: tool output/exit codes, CI visibility, run-to-run change detection, and archived-run dashboards. No metrics, dashboards, or alerts run in production (there is no production service).

## Evidence Reviewed

- `tools/run_toolchain.py`, `tools/risk_score.py`, `tools/render_dashboard.py`, `tools/diff_runs.py`
- `.github/workflows/deep-dive-deterministic.yml`
- `runs/*/` (presence of dashboards)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| tool stdout review | code | signal quality | human-readable only |
| workflow `|| true` review | code | failure visibility | failures masked |
| `runs/*` listing | command | dashboards committed | no `dashboard.md` present |

## Executive Summary

For a CLI/doc pack, observability means clear failure signals and drift detection. The tools exit non-zero on failure and can render dashboards, which is good, but the scheduled org scan masks failures with `|| true`, provides no regression alert, and there is no freshness/health signal for the pipeline itself. Generated dashboards are not committed with runs, so trends aren't visible in-repo.

## Inventory

| Signal | Source | Present | Gating |
|---|---|---|---|
| Tool exit codes | Python tools | yes | partial |
| Human summaries | tool stdout | yes | n/a |
| Advisory score | `risk_score.py` | yes | advisory |
| Dashboards | `render_dashboard.py` | tool only | not committed |
| Run diffs | `diff_runs.py` | tool only | not run in CI |
| CI failure visibility | workflow | masked | `|| true` |

## Findings

### Finding ID: OBS-P2-001 - No structured output or freshness signal for the audit pipeline

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - `tools/*.py` — print human-readable lines; no JSON logs or documented exit-code taxonomy
  - `tools/run_toolchain.py` — prints `TOOLCHAIN: PASS`
  - no monitoring-of-the-monitoring (last-run timestamp, tool-version freshness)
- What is happening: Failures and runs are not machine-observable beyond stdout and exit codes.
- Why it matters: The shared verification rules require freshness metrics and an external check that the pipeline itself is alive; neither exists.
- User / business impact: Silent staleness of scheduled scans.
- Security / privacy / reliability impact: A broken pipeline looks idle, not failed.
- Recommended fix: Add a `--json` output and a run manifest timestamp/freshness check; surface last-success time.
- Suggested validation: Parse JSON output; a stale run raises a signal.
- Owner suggestion: maintainer
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: OBS-P2-002 - Scheduled checks mask failures and never alert on regression

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` lines 51, 56, 87-88, 98 — `|| true` on install/scan/aggregate
  - no threshold/diff step; `tools/diff_runs.py` is never called by CI
- What is happening: The weekly job stays green even when tools fail or findings regress.
- Why it matters: Detection without alerting is not monitoring.
- User / business impact: Regressions accumulate unseen.
- Security / privacy / reliability impact: No incident signal.
- Recommended fix: Fail on scanner errors; run `diff_runs.py` against the previous run and alert on new P0/P1.
- Suggested validation: Introduce a new P0 fixture; workflow flags it.
- Owner suggestion: CI owner
- Effort estimate: M
- Dependencies: CI-P2-003
- Status: open

### Finding ID: OBS-P3-003 - Dashboards and diffs are generated but not bound to archived runs

- Severity: P3
- Confidence: High
- Area: OBS
- Evidence:
  - `tools/render_dashboard.py` writes `dashboard.md`/`dashboard.html`/`pr_comment.md` with `--write`
  - `runs/20260930-0320-.../` and `runs/20260930-0701-.../` contain no `dashboard.md`
  - `tools/diff_runs.py` output is not committed for either run
- What is happening: Trend artifacts are optional and absent from the archive.
- Why it matters: Reviewers can't see run-over-run movement in the repo.
- User / business impact: Manual comparison burden.
- Security / privacy / reliability impact: None direct.
- Recommended fix: Commit dashboards/deltas with completed runs (or document they are ephemeral).
- Suggested validation: Archived run contains `dashboard.md`.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent pipeline failure | P2 | High | Medium | OBS-P2-002 | fail closed + alert |
| No freshness signal | P2 | Medium | Medium | OBS-P2-001 | last-run metric |

## Recommendations

### This Week
- Remove `|| true`; alert on new P0/P1.

### This Month
- Add `--json` output and freshness metadata.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Call `diff_runs.py` in CI | regression alert | workflow | new finding flagged |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Structured tool logs | P2 | maintainer | M | none |

## Suggested Tests

- Simulate scanner failure; job fails.

## Suggested Documentation Updates

- Document exit codes and expected stdout.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Who consumes the org rollup? | alert routing | maintainer intent |

## Appendix

Not applicable — no production monitoring stack.
