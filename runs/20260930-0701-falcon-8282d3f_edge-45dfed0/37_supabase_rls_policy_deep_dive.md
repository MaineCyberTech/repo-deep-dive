# Supabase RLS Policy Deep-Dive Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: RLS
- Status: N/A — Supabase is not used; the equivalent access control work is OpenSearch security, audited by 06/24
- Scope limitations: read-only; no database was queried

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Supabase usage | `grep -rIln -i 'supabase' <first-party dirs>` | `0` files. Corpus-wide matches exist only in the generated Suricata ET ruleset (`config/suricata/rules/suricata.rules`, `.supabase.co` detection signatures) and a captured alert — not usage |
| SQL schema / migrations | `find <both repos> -path '*/.git' -prune -o \( -name '*.sql' -o -type d -name 'migrations' \) -print \| wc -l` | `0` — no first-party SQL, migrations or policy files |
| Data services in the stack | `grep -nE '^  [a-z0-9_-]+:\|image:' compose/central/docker-compose.yml` | OpenSearch 2.19.6 (local S3 build) and Redis 8.8.2; no Supabase/Postgres service |
| Upstream app database | `compose/mct/iris-web/docker-compose.yml` | `iriswebapp_db` (Postgres) exists for the upstream DFIR-IRIS app; its schema/roles ship with that project, not this repo |
| Generated types / client SDKs | `grep -rIln -i -E '@supabase/supabase-js\|supabase-js' <code dirs> \| wc -l` | `0` files |
| Equivalent access controls | `automation/validation/phase4_data_checks.sh` (P4-G11); `automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml` | OpenSearch security roles enforce a single-site read boundary (403 outside `falcon-*`, 200 inside); dashboard multi-tenancy disabled (line 6) |

## Evidence Reviewed

- `/home/user/falcon-build/config/suricata/rules/suricata.rules` — only "supabase" matches are vendor detection signatures for `.supabase.co` (generated, gitignored)
- `/home/user/falcon-build/compose/central/docker-compose.yml` — data stores are OpenSearch and Redis
- `/home/user/falcon-build/automation/validation/phase4_data_checks.sh` — role-based read-boundary test (P4-G11)
- `/home/user/falcon-build/automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml` — OpenSearch security settings; multi-tenancy off
- `/home/user/falcon-build/compose/mct/iris-web/docker-compose.yml` — upstream IRIS stack's own Postgres database

## Not Applicable / Future Readiness

**Why N/A.** There is no Supabase project, no Supabase migrations, no generated TS types, no `supabase-js` client and no SQL/RLS policy file anywhere in the first-party trees. The platform's persistence is OpenSearch (events/indices) plus Redis; authorization is enforced by OpenSearch security roles and OS/container controls, which prompts 06/24 audit. The Postgres instance in the MCT stack belongs to upstream DFIR-IRIS and carries vendor schema/policies, not first-party RLS. Domain score: **0 (not assessable)**.

**Equivalent-control note.** The nearest equivalent to RLS today is index-pattern-based role scoping in OpenSearch Security (P4-G11: reader 403 outside `falcon-*`, 200 inside, cannot enumerate), with multi-tenancy explicitly disabled. That is a single-role boundary, not per-row policy enforcement; it should not be mistaken for RLS coverage.

**Future readiness trigger.** If a first-party relational database or Supabase project is introduced (e.g. MCT client/tenant data), this prompt becomes applicable: enable RLS on every table, `WITH CHECK` on writes, safe `security definer` search_path, service-role handling, storage policies, generated types, and RLS regression tests in CI. None of these exist today.

**Findings:** none — no applicable first-party surface.
