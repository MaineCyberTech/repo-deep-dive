# Multi-Tenant Isolation Attack Simulation — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: MT
- Status: N/A — single owner/site deployment; zone/network isolation is covered by prompts 06 and 12
- Scope limitations: read-only; no attack scenarios were executed; no multi-tenant control plane exists in the assessed scope

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Tenant-scoped IDs/models | `grep -rIn -i -E 'tenant_id\|organization_id\|workspace_id' <code dirs>` | No tenant/org/workspace data models. Hits: upstream OSD header whitelist, the P4-G11 single-site read-boundary docs, and MCT white-label profile templates |
| OpenSearch multi-tenancy | `grep -n 'multitenancy' automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml` | `opensearch_security.multitenancy.enabled: false` (line 6) |
| Read-boundary test | `automation/validation/phase4_data_checks.sh` (P4-G11) | reader: 403 on non-`falcon-*` index, 200 on `falcon-*`, 403 on `_cat/indices` — one site prefix, role-based |
| Edge API objects | `grep -nE '^  /' falcon-edge-build/api/openapi/falcon-edge-v1.yaml` | 16 paths, all sensor-scoped (`/sensors/{sensorId}/…`); no tenant/org/invitation/admin object |
| White-label layer | `find mct/config -type f`; `mct/docs/WHITELABEL.md` | Per-client profile templates exist (`client-profile.example.yml`, `tenant_prefix`); backlog: "Tenant-prefixed Wazuh groups for future clients" |
| First-client status | `mct/client-onboarding/phase9-client-go-no-go.md`; `phase16-client-scan-authorization-status.md` | CONDITIONAL GO for the first external client; signed authorization still "NOT AUTHORIZED"; internal pilot host only |

## Evidence Reviewed

- `/home/user/falcon-build/automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml` — multitenancy disabled
- `/home/user/falcon-build/automation/validation/phase4_data_checks.sh` + `/home/user/falcon-build/docs/phase4/CLOSEOUT.md` — P4-G11 tenant/site read boundary result
- `/home/user/falcon-build/mct/config/examples/client-profile.example.yml` — future per-client profile (`tenant_prefix`, `agent_group_prefix`)
- `/home/user/falcon-build/mct/docs/WHITELABEL.md` — rollout/backlog for future clients (tenant-prefixed Wazuh groups)
- `/home/user/falcon-build/mct/client-onboarding/phase9-client-go-no-go.md` — first external client is conditional, not live

## Not Applicable / Future Readiness

**Why N/A.** The falcon-lab scope is one owner, one site and one data prefix. There are no tenant IDs, memberships, invitations, org roles or tenant-scoped queries to attack; OpenSearch security multi-tenancy is explicitly disabled, and the only tested boundary is the single-site `falcon-*` index prefix via reader roles (P4-G11). Network segmentation (VLANs, WireGuard zones) is isolation of infrastructure, not tenants, and is audited by prompts 06/12. Domain score: **0 (not assessable)**.

**Boundary note (not a finding).** The repo also carries the MCT white-label/client layer. `mct/scripts/generate_p70_reports.py` asserts per-customer scoping results (customer-1 write 200; customer-2 "User not entitled") for a *separate* deployment (`/opt/mct-security-stack`, `/home/user/mct-p70`); that script is a report generator, its claims were not reproduced here, and it does not describe the falcon-lab live stack. It should be audited by the MCT program before it is cited as control evidence.

**Future readiness trigger.** When the first external MCT client onboards (currently conditional with authorization unsigned), prompt 25 becomes applicable to the MCT pipeline: tenant model and IDs, membership/entitlement checks, cross-tenant read/write tests on Wazuh groups, IRIS cases/evidence, dedup ledger, Shuffle workflows and notifications; plus regression tests that must fail closed.

**Findings:** none for the assessed falcon-lab scope.
