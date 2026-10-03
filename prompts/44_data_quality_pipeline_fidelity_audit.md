# Prompt 44 - Data Quality and Pipeline Fidelity Audit

@include `00_SHARED_AUDIT_RULES.md`

## Mission

Audit whether the data the system ingests, transforms, stores, and serves is complete, correctly typed, fresh, and accountable — and whether quality regressions are detected before consumers notice.

This prompt is part of the **Repo Deep-Dive Full Hardening Edition — Falcon Lab profile**. It should produce a repository-specific markdown report with evidence-backed findings, practical fixes, tests, documentation updates, and implementation-ready backlog items.

## Output path

Save the final report to:

`docs/audits/{name}/{run}/44_data_quality_pipeline_fidelity_audit.md`

## Area code

Use finding IDs beginning with `DQ`.

Examples:

- `DQ-P0-001`
- `DQ-P1-001`
- `DQ-P2-001`
- `DQ-P3-001`

## Primary audit questions

1. What repository evidence proves the current behavior for schema and mapping consistency across data generations (old vs new indices, tables, or files)?
2. What repository evidence proves the current behavior for required-field completeness and identity keys (site, sensor, tenant) and null/empty handling?
3. What repository evidence proves the current behavior for freshness monitoring per feed (lag, gaps, silence) and its alerting?
4. What repository evidence proves the current behavior for canary or synthetic assertions that prove the pipeline end to end?
5. What repository evidence proves the current behavior for dead-letter queues, retries, and poison-message handling?
6. What repository evidence proves the current behavior for deduplication and idempotency in ingestion?
7. What repository evidence proves the current behavior for clock and timezone consistency across sources?
8. What repository evidence proves the current behavior for retention and rollover correctness (no silent data loss at boundaries)?
9. What repository evidence proves the current behavior for data-quality metrics and scorecards, including their definitions and owners?
10. What repository evidence proves the current behavior for consumer-facing query correctness (aggregations that silently return empty)?

## Scope to analyze

- Schemas and mappings per store or index; drift between generations
- Required fields and identity keys; null handling
- Freshness and lag metrics per feed; gap detection
- Canary and synthetic test data with assertions
- Dead-letter queues, retries, poison-message handling
- Deduplication and idempotency keys
- Time sync and timezone handling
- Retention, rollover, and deletion boundaries
- Data-quality scorecards, definitions, and owners
- Consumer queries and aggregations (text vs keyword, empty results)

## Required special checks

- Test at least one aggregation or query per major consumer path against the actual mapping; flag silent empty results.
- Verify one canary end to end (write to pipeline to store to query) or mark it `not exercised`.
- Check that data-quality metrics have definitions, owners, and alert thresholds — not just dashboards.
- Compare field types and names across the oldest and newest retained data; list drift.
- Check retention boundaries: what happens to data exactly at the boundary, and whether deletion is observable or alerted.
- Check that feed silence and gap detection is anchored on the data path itself, not only on process liveness.

## Required outputs and companion artifacts

- Data inventory (feeds to stores to consumers)
- Schema and mapping drift table
- Freshness and gap analysis
- Canary assertion review
- Data-quality metric definitions review

## Step-by-step execution instructions

1. Read the repository tree and identify all files relevant to this domain.
2. Review source files, configuration files, tests, docs, and generated artifacts separately.
3. Create an evidence inventory before writing findings.
4. For each item in scope, determine whether it is implemented, partially implemented, absent, stale, duplicated, unsafe, undocumented, or unknown.
5. Identify strengths before risks so the report is balanced and useful.
6. Create findings only when there is concrete evidence.
7. Assign severity using the shared P0/P1/P2/P3 model.
8. Suggest exact file-level remediation where possible.
9. Suggest tests that would prove the remediation works.
10. Suggest documentation updates needed to keep operators and future AI agents aligned.
11. End with open questions and evidence gaps.

## Evidence collection checklist

- [ ] Reviewed Schema and mapping consistency
- [ ] Reviewed Required fields and identity keys
- [ ] Reviewed Freshness and gap detection
- [ ] Reviewed Canary and synthetic assertions
- [ ] Reviewed Dead-letter and retry handling
- [ ] Reviewed Deduplication and idempotency
- [ ] Reviewed Clock and timezone consistency
- [ ] Reviewed Retention and rollover boundaries
- [ ] Reviewed Data-quality scorecards and definitions
- [ ] Reviewed Consumer query correctness
- [ ] Reviewed Feed-silence alerting anchored on the data path

## Required report structure

```markdown
# Data Quality and Pipeline Fidelity Audit

## Audit Metadata

- Audit name:
- Run:
- Repository:
- Branch:
- Commit SHA:
- Generated at:
- Auditor:
- Area code: DQ
- Output path: docs/audits/{name}/{run}/44_data_quality_pipeline_fidelity_audit.md
- Scope limitations:

## Scope

Describe exactly what was reviewed and what was not reviewed.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|

## Verification Performed

| Check | Command / read | Result | Notes |
|---|---|---|---|

## Executive Summary

Summarize the current state in plain English. Include strengths, major risks, and recommended next actions.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Schema and mapping consistency | 0-5 | Evidence | Gap | Recommended action |
| Required fields and identity keys | 0-5 | Evidence | Gap | Recommended action |
| Freshness and gap detection | 0-5 | Evidence | Gap | Recommended action |
| Canary and synthetic assertions | 0-5 | Evidence | Gap | Recommended action |
| Dead-letter and retry handling | 0-5 | Evidence | Gap | Recommended action |
| Deduplication and idempotency | 0-5 | Evidence | Gap | Recommended action |
| Clock and timezone consistency | 0-5 | Evidence | Gap | Recommended action |
| Retention and rollover boundaries | 0-5 | Evidence | Gap | Recommended action |
| Data-quality scorecards | 0-5 | Evidence | Gap | Recommended action |
| Consumer query correctness | 0-5 | Evidence | Gap | Recommended action |

## Detailed Review

For every major item in scope, include:

### Item: Name

- Evidence:
- What it does:
- How it appears to work:
- Dependencies:
- Current controls:
- Missing controls:
- Risks:
- Recommended improvement:
- Suggested tests:
- Suggested docs:

## Schema and Mapping Drift

| Field | Old type | New type | Consumer impact | Evidence |
|---|---|---|---|---|

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DQ-001 | Schema and mapping consistency | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-002 | Required fields and identity keys | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-003 | Freshness and gap detection | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-004 | Canary and synthetic assertions | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-005 | Dead-letter and retry handling | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-006 | Deduplication and idempotency | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-007 | Clock and timezone consistency | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-008 | Retention and rollover boundaries | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-009 | Data-quality scorecards | Evidence | Current control | Gap | Severity | Recommendation |
| DQ-010 | Consumer query correctness | Evidence | Current control | Gap | Severity | Recommendation |

## Findings

Use the shared finding format exactly.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|

## Recommendations

Group recommendations into:

### Immediate / Release Blocking

### This Week

### This Month

### Later / Platform Evolution

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|

## Suggested Tests

Include unit, integration, E2E, CI, security, regression, and manual validation ideas as applicable.

## Suggested Documentation Updates

List exact docs to create or update.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|

## Appendix

Include raw inventories, diagrams, Mermaid diagrams, command outputs, or additional notes as needed.
```

## Quality bar

The final report should be detailed enough that an implementation agent can open the report and start creating safe, scoped remediation PRs without needing another discovery pass. Every data-quality metric must have a definition and an owner, and every drift item must name the consumer impact.
