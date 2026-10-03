# Admin Console Abuse Case Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: ADMIN
- Status: N/A — no first-party admin console; privileged UIs are covered by prompts 06/24 and runbook hardening by 16
- Scope limitations: read-only; no admin session was exercised

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| First-party admin pages/APIs | 0 HTML/CSS/JS/TS files; `grep -nE '^  /' falcon-edge-build/api/openapi/falcon-edge-v1.yaml` | 16 sensor-lifecycle paths only (`/healthz`, `/bootstrap-tokens`, `/enrollments`, `/sensors…`); no `/admin`, `/users`, `/roles`, `/settings`, `/billing`, `/exports` |
| Admin UIs in the stack | `grep -nE '^  [a-z0-9_-]+:\|image:' compose/central/docker-compose.yml` | Grafana, OpenSearch Dashboards, ntfy, ntopng — all upstream vendor consoles |
| Privileged access surfaces | `docs/runbooks/ACCESS_AND_ACCOUNTS.md` | Table of human surfaces: Grafana admin, OSD security users, ntopng basic auth, ntfy admin, UniFi **super-admin**; credentials/rotation documented |
| Console exposure control | `evidence/raw/REVIEW-FIX/20260928T011607Z_soc-console-exposure.out` | Wazuh dashboard behind Cloudflare Access (owner-domain allow + owner-IP bypass); external requests redirect to Access login |
| First-party privileged operations | `grep -nE 'add_parser\|destructive' falcon-edge-build/src/falcon_cli/__main__.py` | `quarantine`, `release`, `revoke`, `retire`, `publish-update`; docstring: "Destructive commands require an affirmative --confirm flag" |
| Upstream MCT admin UI | `compose/mct/iris-web/docker-compose.yml` | DFIR-IRIS app/nginx services (its admin configures evidence types per `mct/integrations/velociraptor/evidence-to-iris-workflow.md`) |

## Evidence Reviewed

- `/home/user/falcon-build/docs/runbooks/ACCESS_AND_ACCOUNTS.md` — every privileged surface is upstream; known gaps recorded
- `/home/user/falcon-build/evidence/raw/REVIEW-FIX/20260928T011607Z_soc-console-exposure.out` — Cloudflare Access gating of the SOC console
- `/home/user/falcon-build/compose/central/docker-compose.yml` — no first-party admin container
- `/home/user/falcon-edge-build/src/falcon_cli/__main__.py` — privileged CLI with `--confirm` on destructive commands
- `/home/user/falcon-build/compose/mct/iris-web/docker-compose.yml` — upstream DFIR-IRIS admin surface

## Not Applicable / Future Readiness

**Why N/A.** There is no first-party admin console, admin API, user/role management, billing panel, document/ticket admin, bulk operation UI, approval flow, impersonation or settings surface in either repository — the only first-party control plane API is the sensor lifecycle API, which is operator mTLS-protected and has no user/org/role objects. Every console an admin uses today (Grafana org/admin, OpenSearch Security, Wazuh dashboard, ntfy, ntopng, UniFi, IRIS) is an upstream product whose misuse cases are vendor concerns; the repo's role is to gate and account for them, which prompts 06 (security/authz) and 24 (access control matrix) audit. Domain score: **0 (not assessable)**.

**First-party privileged tooling.** The `falcon` CLI's destructive commands (`revoke`, `retire`, `quarantine`, `publish-update`) are the closest first-party analogue to admin abuse cases; `--confirm` is required and the operations are documented. Their authorization, key handling and auditability belong to 06/24 and the edge program's own gates (43), not to this prompt.

**Future readiness trigger.** If a first-party admin console or an MCT client admin portal ships, this prompt becomes applicable and needs: server-side role checks, least-privilege/service accounts, approval flows for destructive/bulk actions with previews, self-escalation tests, undo/recovery, rate limits, and audit logs for role/delete/export actions.

**Findings:** none — no applicable first-party surface.
