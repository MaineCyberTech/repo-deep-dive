# Data, Schema, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: DATA
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/07_data_schema_migration_runtime_validation.md
- Scope limitations: no database or migrations; the data contracts are `findings.json`, `audit_manifest.json`, and `inventory.json`.

## Scope

JSON data contracts produced/consumed by the tools: `schemas/findings.schema.json`, `collect_findings.py` output, `new_run.py` seed manifest, and `check_run.sh` required keys. No SQL migrations exist.

## Evidence Reviewed

- `schemas/findings.schema.json`
- `tools/collect_findings.py` lines 49-59
- `tools/new_run.py` lines 63-73; `examples/audit_manifest.example.json`
- `tools/check_run.sh` lines 25-45
- `runs/20260930-0701-.../findings.json`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Archived `findings.json` head | artifact | schema conformance | `sourceReports` is an array |
| `schema.required.sourceReports.type` | contract | type check | integer |
| base example manifest keys | contract | scaffold vs gate | lacks `profile`,`scope`,`findings` |
| `check_run.sh` required list | code | gate contract | requires those keys |

## Executive Summary

Two contract defects exist. First, `collect_findings.py` writes `sourceReports` as a filename array while the schema requires an integer (confirmed in the archived run), so every real run violates its own schema and no test catches it. Second, the base example manifest lacks the `profile`/`scope`/`findings` keys that `check_run.sh` requires, so a `new_run.py --profile base` scaffold is rejected by the pack's own gate. Both are deterministic and fixable in one patch.

## Inventory

| Contract | Producer | Consumer | State |
|---|---|---|---|
| `findings.schema.json` | maintainer | `self_test.sh`, reviewers | drifted |
| `findings.json` | `collect_findings.py` | score/dashboard/CSV/schema | violates schema |
| `audit_manifest.json` | `new_run.py` seed | `check_run.sh` | base seed fails |
| `inventory.json` | `repo_inventory.py` | prompts 01/02 | stale (INV) |

## Findings

### Finding ID: DATA-P1-001 - findings.json violates its own schema (`sourceReports` array vs integer)

- Severity: P1
- Confidence: High
- Area: DATA
- Evidence:
  - `tools/collect_findings.py` line 53 — `"sourceReports": [p.name for p in reports]`
  - `schemas/findings.schema.json` line 11 — `"sourceReports": { "type": "integer", "minimum": 0 }`
  - `runs/20260930-0701-falcon-8282d3f_edge-45dfed0/findings.json` — `"sourceReports": [ "00_audit_orchestrator.md", ... ]`
  - `tools/self_test.sh` lines 75-83 — asserts only required keys and ID pattern, not types
- What is happening: The emitted artifact and the published schema disagree; the schema validator in the self-test does not check types.
- Why it matters: Any downstream JSON-Schema consumer fails, and the pack's "schema conformance" test gives false assurance.
- User / business impact: Integrators cannot rely on the contract; CI schema validation would fail.
- Security / privacy / reliability impact: Silent contract drift across all runs.
- Recommended fix: Change `collect_findings.py` to emit an integer count (e.g. `len(reports)`), or change the schema to `array of string`; update the archived run and `deterministic_checks.py` (`sourceReports: 1`) consistently.
- Suggested validation: `python3 -m jsonschema -i findings.json schemas/findings.schema.json` passes for a regenerated run.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: DATA-P1-002 - Base-profile scaffold produces a manifest the pack's own gate rejects

- Severity: P1
- Confidence: High
- Area: DATA
- Evidence:
  - `examples/audit_manifest.example.json` keys: `executionOrder, outputRoot, pack, promptCount, recommendedName, version` (no `profile`, `scope`, `findings`)
  - `tools/new_run.py` lines 63-73 — copies that example verbatim (plus `run`/`scaffolded_*`)
  - run manifest `20261003-0018-main-7bac320/audit_manifest.json` keys confirm the same gap
  - `tools/check_run.sh` line 32 — required keys `["pack","profile","run","scope","findings"]`
- What is happening: `new_run.py --profile base` seeds a manifest missing three required keys, so `check_run.sh` immediately fails and the run must be hand-patched (as this run was).
- Why it matters: The advertised Wave 0 scaffold does not produce a valid, checkable run on the base profile.
- User / business impact: Every base run starts red; operators may ignore the gate or patch ad hoc.
- Security / privacy / reliability impact: Gate credibility erosion; machine-readable counts absent until fixed.
- Recommended fix: Add `profile: "base"`, a `scope` object, and a zeroed `findings{total,bySeverity,byArea}` to the base example manifest; keep the falcon example's `total`.
- Suggested validation: `tools/new_run.py --run t --root $TMP && tools/check_run.sh $TMP/.../t` prints PASS on the skeleton.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: DATA-P3-003 - Deterministic findings use line 1 for every row and an en-dash separator

- Severity: P3
- Confidence: High
- Area: DATA
- Evidence:
  - `tools/deterministic_checks.py` line 233 — every finding gets `"line": 1`
  - `tools/deterministic_checks.py` line 256 — `"### Finding ID: %s – %s"` uses U+2013 en-dash
  - brief/shared format uses ` - ` (ASCII space-hyphen-space)
- What is happening: The deterministic lens emits unlocated findings and a separator variant.
- Why it matters: `line: 1` misleads reviewers; a stricter parser keyed on ` - ` may miss these findings.
- User / business impact: Minor traceability loss.
- Security / privacy / reliability impact: None direct.
- Recommended fix: Compute real line numbers for markdown output and use ASCII ` - `.
- Suggested validation: Parse `lens_deterministic.md` with the shared finding regex.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Schema divergence | P1 | High | Medium | DATA-P1-001 | align producer/schema |
| Scaffold fails own gate | P1 | High | Medium | DATA-P1-002 | fix seed manifest |

## Recommendations

### Immediate / Release Blocking
- Align `collect_findings.py` `sourceReports` with the schema.
- Fix the base example manifest.

### This Week
- Add type-level schema validation to `self_test.sh`.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Seed manifest keys | valid base scaffold | `examples/audit_manifest.example.json`, `new_run.py` | `check_run.sh` PASS |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Full JSON-Schema validation in CI | P2 | maintainer | S | DATA-P1-001 |

## Suggested Tests

- Round-trip: scaffold → `collect --write` → validate against schema.

## Suggested Documentation Updates

- `schemas/findings.schema.json` description; `CONTRIBUTING.md` contract note.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was `sourceReports` intended as a count or list? | determines fix direction | maintainer intent |

## Appendix

No SQL migrations or app database exist in this repository.
