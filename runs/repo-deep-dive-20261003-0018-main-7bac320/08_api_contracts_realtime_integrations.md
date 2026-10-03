# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: API
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/08_api_contracts_realtime_integrations.md
- Scope limitations: no HTTP/realtime API; "contracts" are CLI tool interfaces, finding-ID vocabulary, and JSON artifacts.

## Scope

Tool CLI contracts and the shared finding-ID/area namespace. GitHub Actions is the only external integration. No webhooks, realtime channels, or third-party API calls exist.

## Evidence Reviewed

- `tools/run_toolchain.py`, `tools/deterministic_checks.py`, `tools/lib_findings.py`
- `prompts/06_...` (area SEC), `prompts/10_...` (area CI), `prompts/21_...` (area HYGIENE)
- `tools/check_run.sh` duplicate-ID gate (lines 97-113)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `deterministic_checks.py` add() calls | code | area codes used | PORT, SEC, CI, DEP, GIT, DOC |
| prompt area lines | doc | declared area codes | SEC, CI already owned |
| `check_run.sh` dupe gate | code | collision consequence | run fails on duplicate IDs |

## Executive Summary

There is no network API to audit. The meaningful contract issues are in the machine-findings pipeline: the deterministic lens reuses area codes (`SEC`, `CI`) already owned by domain prompts, which can trip the duplicate-ID gate; and deterministic findings are emitted to a separate `out/` tree that never feeds `collect_findings.py`/`risk_score.py`. Both are integration gaps that limit the new capability.

## Inventory

| Contract | Definition | Producer | Consumer | State |
|---|---|---|---|---|
| Finding ID | `AREA-Px-NNN` | prompts/lenses | lib, check_run, CSV | stable |
| Deterministic lens | `lens_deterministic.md` | `deterministic_checks.py` | aggregate only | not wired |
| Tool CLI flags | argparse | each tool | `run_toolchain.py` | consistent |
| GitHub Actions | workflow | maintainer | GitHub | present |

## Findings

### Finding ID: API-P2-001 - Deterministic lens reuses domain area codes, risking duplicate finding IDs

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `tools/deterministic_checks.py` — `add("SEC", ...)` (lines 114, 144), `add("CI", ...)` (lines 159, 167), plus PORT/DEP/GIT/DOC
  - `prompts/06_security_authz_tenancy_audit.md` — area `SEC`
  - `prompts/10_github_actions_cicd_governance.md` — area `CI`
  - `tools/check_run.sh` lines 97-113 — duplicate IDs cause `FAIL`; `tools/lib_findings.py` scans `lens_*.md` and `NN_*.md`
- What is happening: If `lens_deterministic.md` is placed in a run folder alongside the SEC/CI domain reports, independent counters can both emit e.g. `SEC-P1-001`/`CI-P2-001`.
- Why it matters: The duplicate-ID gate exists precisely because IDs are load-bearing for registers, CSVs, and diffs.
- User / business impact: A run can fail validation or silently merge unrelated findings.
- Security / privacy / reliability impact: Register/diff integrity.
- Recommended fix: Namespace deterministic area codes (e.g. `DET-SEC`, `DET-CI`) or emit a distinct area (`DET`) with a subcode.
- Suggested validation: Generate a run containing both the deterministic lens and prompt 06/10 output; `check_run.sh` duplicates gate stays green.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: API-P2-002 - Deterministic findings never reach the run findings flow

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `tools/deterministic_checks.py` line 282 — default `outdir = <repo>/deterministic-out`
  - `tools/aggregate_findings.py` — reads `*/*/deterministic-findings.json`, separate from runs
  - `tools/lib_findings.py` `run_reports` — only scans a run folder's `*.md`
  - `.github/workflows/deep-dive-deterministic.yml` line 98 — writes `out/ORG_SUMMARY.md`, not a run folder
- What is happening: Machine findings live in an org rollup and are never normalized into `findings.json`, scored, or diffed per run.
- Why it matters: The claimed "real findings before the prompt audit" do not participate in scoring/gates/tracking.
- User / business impact: Two disconnected finding stores; counts diverge.
- Security / privacy / reliability impact: Findings can be missed by risk scoring.
- Recommended fix: Provide an import path (`deterministic_checks.py --run-folder <dir>` writing `lens_deterministic.md` plus merge into `findings.json`) or document the separate store explicitly.
- Suggested validation: After import, `collect_findings.py` counts deterministic findings.
- Owner suggestion: pack maintainer
- Effort estimate: M
- Dependencies: API-P2-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Duplicate IDs break gate | P2 | Medium | Medium | API-P2-001 | namespace areas |
| Two finding stores diverge | P2 | High | Medium | API-P2-002 | import path |

## Recommendations

### This Week
- Namespace deterministic area codes.

### This Month
- Wire deterministic findings into the run flow.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `DET-` prefix on deterministic areas | no ID collision | `deterministic_checks.py` | dupe gate |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Deterministic→run import | P2 | maintainer | M | API-P2-001 |

## Suggested Tests

- Run containing deterministic + domain reports passes `check_run.sh`.

## Suggested Documentation Updates

- Document deterministic areas and the separate store.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Should deterministic findings be gate-relevant? | affects scoring | maintainer intent |

## Appendix

Realtime/webhooks: not applicable — no such surface exists.
