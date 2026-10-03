# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: DATA
- Output path: docs/audits/{name}/{run}/07_data_schema_migration_runtime_validation.md
- Scope limitations: no live cluster; retention state is `unverified`.

## Scope

Reviewed OpenSearch index lifecycle (ISM), index templates, migration scripts, the backup archive contents, and the Wazuh/IRIS data stores. No DB migrations framework (no SQL/ORM) — entities are OpenSearch indices and Docker volumes.

## Evidence Reviewed

- `bootstrap/61-search-policies.sh`, `automation/validation/index_rename_migration.sh`, `automation/validation/ism_retention_metrics.sh`.
- `config/opensearch/`, `config/vector/`.
- `bootstrap/85-backup-job.sh` line 39 (archive contents).
- `docs/CURRENT_STATE.md` (C7 capacity).

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `bootstrap/85-backup-job.sh` L39 | Source | Archive scope | includes docs/ledgers |
| `automation/validation/index_rename_migration.sh` | Source | Loss history | R-23 documented |
| `config/opensearch` ISM | Config | Retention | falcon-eve covered |

## Executive Summary

Falcon's event data (`falcon-eve-*`) is well-controlled with ISM retention and a documented (painful) rename-migration history. The gap is the imported data domains: Wazuh indices and DFIR-IRIS case data have no lifecycle/retention, so they grow unbounded on the shared data LV and have no deletion window. Index template/`event_time` ownership is split between the Vector transform and the OpenSearch template with no consistency check.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Event indices | `falcon-eve-*` | normalized events | Retained (ISM) | Low | 14-day delete + cold copy |
| Wazuh indices | `wazuh-*` | agent/SOC data | No retention | High | unbounded |
| IRIS data | IRIS DB/volume | case management | No retention/backup | High | — |
| Templates | `config/opensearch` + Vector | mapping | Split ownership | Medium | — |
| Migration | `index_rename_migration.sh` | rename | Verified destination before delete | Medium | prior loss documented |
| Config archive | `85-backup-job.sh` | backup | tars docs/ledgers | Low | — |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Data model | 3 | indices | Wazuh/IRIS unmanaged | DATA-P1-001 |
| Migrations | 3 | rename script w/ guard | no automated runner | document |
| Retention | 2 | ISM for eve only | gaps | DATA-P1-001 |
| Runtime validation | 3 | checks present | live only | — |
| Backup binding | 3 | gauges/rules | evidence binding | BACKUP |

## Findings

### Finding ID: DATA-P1-001 - Wazuh and IRIS data have no retention (unbounded index growth)

- Severity: P1
- Confidence: High
- Area: DATA
- Evidence:
  - `bootstrap/61-search-policies.sh` — ISM templates cover `falcon-eve-*`
  - `docs/CURRENT_STATE.md` C7 — "unbounded Wazuh data on the shared data LV"
  - `compose/mct/iris-web/` — IRIS data volume with no lifecycle
- What is happening: Only the Falcon event indices have a delete/retention policy; Wazuh and IRIS grow without bound.
- Why it matters: Capacity exhaustion and a privacy retention gap.
- User / business impact: Disk pressure can take down central storage; data kept indefinitely.
- Security / privacy / reliability impact: Retention/erasure obligations unmet; disk-fill outage.
- Recommended fix: Add ISM for `wazuh-*` (align to the documented retention decision) and a lifecycle/retention policy for IRIS case data; alarm on index growth.
- Suggested validation: `ism_retention_metrics.sh` extended to Wazuh/IRIS; projected growth rule.
- Owner suggestion: data owner
- Effort estimate: M
- Dependencies: owner retention decision
- Status: open

### Finding ID: DATA-P2-001 - Index template and `event_time` ownership are split with no consistency check

- Severity: P2
- Confidence: Medium
- Area: DATA
- Evidence:
  - `config/vector/*` — transform sets `event_time`
  - `config/opensearch/*` — index template field types
  - No test asserts the two agree at HEAD
- What is happening: Two components own the same field semantics independently.
- Why it matters: Mapping drift can reject events (mapping explosion was previously observed, R-25).
- User / business impact: Silent event drops.
- Security / privacy / reliability impact: Data quality.
- Recommended fix: Generate the template from a single schema source, or add a CI check that validates the Vector-derived document against the template.
- Suggested validation: `mapping_drift_check.py` in CI (present) — extend to assert `event_time` type.
- Owner suggestion: data owner
- Effort estimate: M
- Dependencies: schema source
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Data LV exhaustion | P1 | High | High | CURRENT_STATE C7 | DATA-P1-001 |
| Retention/privacy gap | P1 | High | Medium | no lifecycle | DATA-P1-001 |
| Mapping drift drop | P2 | Medium | Medium | split ownership | DATA-P2-001 |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
- Set Wazuh/IRIS retention (DATA-P1-001).

### This Month
- Single-source schema (DATA-P2-001).

### Later / Platform Evolution
- Automated migration runner with pre-delete verification.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Growth alarm on wazuh indices | Early warning | ism_retention_metrics.sh | rule fires |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Wazuh/IRIS lifecycle | P1 | data owner | M | owner decision |

## Suggested Tests

- ISM coverage test asserting every index pattern has a policy.
- Document-vs-template validation.

## Suggested Documentation Updates

- Record the retention matrix (indices, window, deletion path).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Owner retention decision for Wazuh/IRIS? | Config target | decision log |

## Appendix
Not applicable.
