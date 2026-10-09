# 37_supabase_rls_policy_deep_dive — Prompt 37 - Supabase RLS Policy Deep-Dive Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `37_supabase_rls_policy_deep_dive.md` (area RLS, prompt)

## Verification Performed

# Supabase RLS Policy Deep-Dive Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-08e20d1`
- Branch: main (worktree detached at the audited commit)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:50:50Z
- Auditor: subagent (read-only)
- Area code: RLS
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/37_supabase_rls_policy_deep_dive.md
- Scope limitations: static + read-only live; no Supabase/Postgres RLS surface exists in this repository.

## Scope

Checked the repository for Supabase/Postgres RLS-relevant surfaces: SQL files, migrations, `CREATE POLICY`/RLS statements, Supabase clients, storage buckets/policies, security-definer functions/triggers, generated DB types, and app queries. Because none exist, the prompt's fallback applies: produce an equivalent-control readiness report for the datastore actually in use (OpenSearch security plugin) and the vendored Postgres application.

## Evidence Reviewed

- `git ls-files '*.sql'` -> empty (no SQL files anywhere in the repository).
- Repository-wide grep (source trees, excluding `evidence/` and `docs/audits/`): no `supabase`, `row-level security`, `row level security`, `CREATE POLICY`, or `ENABLE ROW LEVEL` matches.
- `bootstrap/60-central-deploy.sh:131-202` (OpenSearch least-privilege roles/users).
- `docs/architecture/PORT_PROTOCOL_MATRIX.md:23` (OpenSearch 9200 container-only, service credentials).
- `mct/compose/docker-compose.dfir-iris.yml`, `compose/mct/iris-web/docker-compose.base.yml` (vendored DFIR-IRIS with Postgres; third-party app, not authored here).
- Live (read-only): `_plugins/_security/api/roles` on `falcon-central-opensearch-1`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git ls-files '*.sql'` | static | RLS requires SQL schema | empty output |
| Source grep for Supabase/RLS keywords | static | Detect any RLS surface | zero matches outside evidence/audits |
| Live `_plugins/_security/api/roles` | live read-only | Equivalent access-control controls | `falcon_writer` (create_index/write/read on `falcon-*`), `falcon_reader`, `falcon_backup`; `fls: []`, `masked_fields: []` (no document/field-level security) |
| `bootstrap/60-central-deploy.sh:131-202` | static | Declared roles/users | writer/reader/backup identities, least privilege, admin break-glass |
| Prior-run reconciliation | review | Same N/A determination | prior run (e267ce1) emitted `findings: []` with the same N/A conclusion |

### Prior-run reconciliation (run falcon-20261005-full-main-e267ce1)

- Prior domain 37 emitted `findings: []` and "Not applicable: repository does not use Supabase/Postgres RLS." Re-verified at `08e20d1`; conclusion unchanged.

## Executive Summary

Not applicable. Falcon is an infrastructure/telemetry repository with no Supabase project, no SQL schema, no migrations, and no RLS policies. The datastore is OpenSearch with the security plugin; its equivalent controls are per-service least-privilege identities and TLS, which are declared in `bootstrap/60-central-deploy.sh` and live-verified. The only Postgres in scope is the vendored DFIR-IRIS case-management app, which is third-party software outside this repository's authored surface. No findings.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| SQL schema/migrations | none | - | absent | N/A | `git ls-files '*.sql'` empty |
| Supabase config/clients | none | - | absent | N/A | grep zero matches |
| OpenSearch roles | `bootstrap/60-central-deploy.sh:131-202` | datastore access | writer/reader/backup least privilege | Low | live-verified |
| Document/field-level security | `_plugins/_security` | row-level equivalent | not configured | N/A (single tenant) | `fls: []`, `masked_fields: []` |
| Storage buckets/policies | R2/Spaces via rclone | backups | root-owned configs | Low | no bucket policy DSL in repo |
| Vendored IRIS Postgres | `mct/compose/docker-compose.dfir-iris.yml` | case mgmt | third-party | N/A | outside authored surface |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Supabase migrations | 0 | absent | N/A | - |
| SQL schema | 0 | absent | N/A | - |
| RLS enablement | 0 | absent | N/A | - |
| Policies | 0 | absent | N/A | - |
| Grants/roles (equivalent) | 3 | OpenSearch roles | no DLS/FLS | keep single-tenant scope documented |
| Storage bucket policies | 1 | rclone configs only | no declarative policy | owner-side |
| Functions/triggers | 0 | absent | N/A | - |
| Security definer | 0 | absent | N/A | - |
| Generated types | 0 | absent | N/A | - |
| App queries | N/A | infra repo | - | - |
| Tenant/user matching | N/A | `site_id` fields only | - | - |
| Admin bypass | 2 | break-glass admin | documented | rotation already tracked |

## Detailed Review

### Item: Equivalent control — OpenSearch security plugin

- Evidence: `bootstrap/60-central-deploy.sh:131-202`; live `_plugins/_security/api/roles`.
- What it does: `falcon_writer` can `create_index`/`write`/`read` on `falcon-*`; `falcon_reader` (dashboard, healthcheck) read-only; `falcon_backup` snapshot-only; admin is break-glass; demo users deleted.
- Missing controls: no document-level or field-level security, no per-tenant policy — acceptable for a single-tenant lab, but a future multi-tenant deployment would need the OpenSearch DLS/FLS equivalent of RLS.
- Recommended improvement: record the "single tenant; no DLS/FLS by design" decision in the security docs so a future multi-tenant evolution starts from an explicit statement.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| RLS-001 | Supabase migrations | absent | n/a | n/a | - | - |
| RLS-002 | SQL schema | absent | n/a | n/a | - | - |
| RLS-003 | RLS enablement | absent | n/a | n/a | - | - |
| RLS-004 | Policies | absent | n/a | n/a | - | - |
| RLS-005 | Grants/roles | `60-central-deploy.sh:131-202` | least-privilege roles | no DLS/FLS | N/A | document scope |
| RLS-006 | Storage bucket policies | rclone configs | owner-side | no declarative policy | P3 (owner-side) | R2 lifecycle (SEARCH-P2-004) |
| RLS-007 | Functions/triggers | absent | n/a | n/a | - | - |
| RLS-008 | Security definer | absent | n/a | n/a | - | - |
| RLS-009 | Generated types | absent | n/a | n/a | - | - |
| RLS-010 | App queries | infra repo | n/a | n/a | - | - |
| RLS-011 | Tenant/user matching | `site_id` fields | validation only | not storage-enforced | N/A | single tenant |
| RLS-012 | Admin bypass | break-glass admin | documented, rotated | - | - | - |

## Findings

_No findings: the domain is not applicable; no fabricated equivalent gap was found in the authored surface._

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| None in this domain (N/A) | - | - | - | - | - |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- None.

### This Month
- Record the single-tenant/no-DLS decision in `docs/security/`.

### Later / Platform Evolution
- If multi-tenancy is ever introduced, design the OpenSearch DLS/FLS equivalent before ingesting multi-tenant data.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| One-line scope statement | Prevents future false "RLS missing" findings | `docs/security/` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Multi-tenant access-control design note | P3 | security owner | S | future requirement |

## Suggested Tests

- A repo guard test asserting no `*.sql`/Supabase surface appears without an accompanying RLS review (documentation-only).

## Suggested Documentation Updates

- `docs/security/`: note that the datastore is OpenSearch with role-based least privilege and no DLS/FLS (single tenant).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Any plan for multi-tenant ingestion? | Would require an RLS-equivalent design | owner roadmap |

## Appendix

- Grep evidence: `grep -rliE 'supabase|row.level.security|create policy|enable row level' --include='*.sql' --include='*.md' --include='*.sh' --include='*.py' --include='*.yml' --include='*.yaml' .` -> no source-tree matches.

## Findings

_No findings in this domain._
