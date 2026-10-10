# 26_admin_console_abuse_case_audit — Prompt 26 - Admin Console Abuse Case Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `26_admin_console_abuse_case_audit.md` (area ADMIN, prompt)

## Verification Performed

# Admin Console Abuse Case Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65`
- Generated at: 2026-10-09T21:45:00Z
- Auditor: subagent (domain 26)
- Area code: ADMIN
- Output path: `docs/audits/falcon-20261009-2117-full-08e20d1/26_admin_console_abuse_case_audit.md`
- Scope limitations: the "admin console" surface is the set of operator UIs (Grafana, OpenSearch Dashboards, ntopng, ntfy, Wazuh dashboard, DFIR-IRIS, UniFi) plus host/root tooling. Vendor app internals were not audited beyond declared configuration and read-only live checks; Cloudflare Access policy details were not read via API.

## Scope

Reviewed: admin pages/APIs, user/org/role management, billing panels (N/A), document/ticket admin (IRIS), webhook/API key admin, bulk ops, approval flows, impersonation, settings, exports, destructive actions, confirmations, permissions, rate limits, undo/recovery, tests.

Not reviewed: vendor UI code paths (Grafana/OSD/IRIS internals), the edge-sensor repo, Cloudflare dashboard configuration via API.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/traefik/dynamic.yml` | runtime config | public/private console routers + auth | `/ntop` basic auth; others app login only |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §1, §5, §6 | doc | admin surfaces, known gaps, Access verification | single admin per service; origin auth gap recorded |
| `ledgers/risk_register.md` R-15 | ledger | accepted public-exposure risk | OPEN (prepared, fail-closed) |
| `ledgers/decision_log.md` 2026-09-21T19:05Z, 2026-09-28T01:10/01:20Z | ledger | owner-IP bypass rationale + NAT caveat | "anyone sharing the same NAT IP bypasses" |
| `.github/workflows/external-smoke.yml` | CI | Access-posture gate | HEAD accepts owner-IP bypass; comment/runner contradiction |
| `.github/workflows/dependabot-merge.yml`, `.github/CODEOWNERS` | CI | repo approval flow | label-gated merges (plan-gated branch protection, other domain) |
| `config/docker/daemon.json` | runtime | container log driver | `json-file` (20 MB × 5), not shipped |
| `bootstrap/60-host-auditd.sh` | host baseline | auditd watches | identity/sudoers/ssh/firewall/secrets metadata |
| `bootstrap/60-central-deploy.sh:216-230` | deployment | OpenSearch REST audit | `plugins.security.audit.config.enable_rest: true` |
| `automation/wazuh/multi-node/config/wazuh_indexer/*.yml:48` | deployment | Wazuh security audit | `internal_opensearch` |
| `config/traefik/traefik.yml:30-32` | config | access log | JSON; no authenticated-user field |
| `bootstrap/32-inbound-mode.sh`, `automation/validation/retire_migrated_docker_volumes.sh` | ops tooling | destructive/toggle actions | ledgered toggle; dry-run default |
| Live checks (read-only) | live state | actual exposure + accounts | HTTP probes, Grafana users, ntfy ACLs, agent localfiles, access-log fields |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Live origin probes via loopback (2026-10-09T21:23Z) | reproduction | origin auth on consoles | Grafana `/`→302 login; `/dash/`→302 login; `/ntop`→401 basic auth; no origin auth |
| Live public probes from owner IP 142.105.190.25 | reproduction | Access posture | falcon → Access challenge; iris/soc → origin redirects (bypass); enroll → 404 (token path); ntfy → 404 |
| Grafana `/api/users` (read-only) | verification | admin accounts | one `admin`, no external auth |
| `ntfy user list` (read-only) | verification | admin/ACL model | monadmin admin; relay write-only; owner rw; watcher ro; anonymous denied |
| Host Wazuh agent localfiles (read-only) | verification | audit coverage | journald/audit.log/dpkg + commands; no container-log source |
| Traefik access-log sample (read-only) | verification | actor attribution | ClientAddr/host/path/status only; no user identity |
| `external-smoke` diff `27ed413..08e20d1` | reproduction | gate weakening | accepts any 302 incl. origin reachability |
| `docker ps` (live) | drift check | admin service estate | 27 containers; matches declared central/probe/mct sets |

## Executive Summary

The operator consoles are the crown jewels of this stack, and their exposure model is: Cloudflare Access at the edge for falcon/iris/soc, per-service application logins at the origin, basic auth for ntopng, native auth for ntfy, and a default-deny host firewall that only admits web traffic from the management/admin subnets and the loopback tunnel. This is a coherent single-operator design, documented and mostly verified.

Three issues stand out:

1. **The consoles have no origin authentication** (prior ADMIN-P2-001): any edge-policy mistake, or any actor behind the bypassed owner NAT, reaches Grafana/OSD/IRIS/Wazuh login pages directly; `/ntop` is the only route with origin auth.
2. **The automated Access-posture gate was weakened at this commit** (`08e20d1`): `external-smoke` now runs on the lab (self-hosted) and treats *any* 302 as OK, including "owner-IP Access bypass; origin reachable". Its own comment still says it must run from GitHub's network, and its job summary still claims "iris/soc: must be 302 to cloudflareaccess.com (Access still enforcing)". The claimed "Access posture is verified externally" has no artifact in the repo. This makes an Access regression invisible to CI.
3. **Admin actions are not centrally audited at the actor level** for Grafana/ntfy/IRIS (container `json-file` logs are not shipped; Traefik access logs carry no user identity). Host file/identity changes (auditd) and OpenSearch REST activity (security audit) are covered; Wazuh has its own audit. Role/delete/export actions in the non-OpenSearch consoles have no durable audit trail beyond rotated local logs.

Strengths: no self-privilege escalation path (single admin per console, no user-management UI exposed), no bulk destructive console operations, no impersonation feature, destructive host tooling is root-gated and largely dry-run/ledgered, and OpenSearch/Wazuh auth events are audited.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Grafana admin | `grafana.falcon.lab` / public root | metrics/alerts | local admin (single) | Medium | anonymous+signup off |
| OpenSearch Dashboards | `/dash` | events search | OSD login (OpenSearch internal users) | Medium | falcon-dashboard service + admin |
| ntopng | `/ntop` | flow UI | Traefik basic auth (`ntop_htpasswd`) | Low | dedicated file since U-10 |
| ntfy | `falcon-ntfy.mainecybertech.us` | notifications | native auth, deny-all | Low | ACLs verified live |
| Wazuh dashboard | `soc.mainecybertech.us` | SOC console | OSD/OpenSearch login | Medium | Access + app login |
| DFIR-IRIS | `iris.mainecybertech.us` | case management | IRIS login | Medium | Access + app login |
| UniFi | LAN only | network admin | super-admin login | Medium | `/home/user/.env` (user-side) |
| Host root/sudo | SSH/console | break-glass | sudo value in 0600 file | Medium | OD-04 custody PENDING |
| Repo approvals | `.github/CODEOWNERS`, dependabot label gate | change control | advisory (plan-gated) | Medium | other domain (BP/CI) |
| Destructive ops | bootstrap stages, retire/restore scripts | host lifecycle | root + ledger/dry-run | Low | `32-inbound-mode.sh` toggles exposure with ledger |
| Bulk ops / impersonation | n/a | — | absent | — | — |
| Exports | Grafana/OSD/IRIS export features | data egress | app-level | Low | not audited centrally |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Admin pages/APIs | 3 | dynamic.yml; live probes | origin auth gap | SEC-P2-001/ADMIN-P2-001 fix |
| User/org/role management | 2 | ACCESS §1; single admin/service | no separation; OD-04 pending | per-service accounts; custody |
| Billing panels | N/A | none | — | — |
| Document/ticket admin | 2 | IRIS deployed | audit trail gap | ship IRIS logs |
| Webhook/API key admin | 3 | relay/enroll code | shared enroll token | ACM finding |
| Bulk ops | N/A | none found | — | — |
| Approval flows | 2 | CODEOWNERS + label gate | plan-gated enforcement | other domain |
| Impersonation | N/A | none found | — | — |
| Settings | 3 | compose envs; provisioning | console settings not codified | document |
| Exports | 2 | app features | no export audit | enable/log where possible |
| Destructive actions | 3 | root gating; dry-run; ledger | none material | keep |
| Confirmations | 3 | scripts require root; dry-run defaults | — | — |

## Detailed Review

### Item: Console exposure and origin authentication

- Evidence: `dynamic.yml:71-134`; live probes; `ACCESS_AND_ACCOUNTS.md` §5-§6; `risk_register.md` R-15.
- What it does: publishes Grafana/OSD/ntop/IRIS/Wazuh consoles via Cloudflare Tunnel + Access.
- Current controls: Access (falcon/iris/soc), app logins, ntopng basic auth, host firewall allowlist, rate limits.
- Missing controls: origin auth on Grafana/OSD/IRIS/Wazuh; Access JWT validation.
- Risks: edge-only enforcement; owner-IP bypass is a shared-NAT bypass by design.
- Recommended improvement: origin auth or Access-JWT validation; document acceptance otherwise.

### Item: Access-posture verification (`external-smoke`)

- Evidence: `.github/workflows/external-smoke.yml:20-25` (comment says "Must run from GitHub's network ... On the lab the vantage is internal and the result is wrong, so it stays on hosted" while `runs-on` is `[self-hosted, lab]`), `:34-46` (any 302 passes; non-Access 302 labeled "owner-IP Access bypass; origin reachable"), `:59-66` (summary still claims "must be 302 to cloudflareaccess.com"); commits `70292a0` + `08e20d1`; live iris/soc origin redirects from the lab vantage.
- What it does: daily public-surface availability + Access-posture check.
- Current controls: reachability check still works; Access-posture assertion is gone.
- Missing controls: a vantage that can distinguish Access-enforced from origin-reachable; no service-token/API check.
- Risks: an Access app removal/misconfiguration for iris/soc would not be detected; the workflow would stay green.
- Recommended improvement: restore an external vantage (or a Cloudflare API/service-token check with a scoped token) and fail on non-`cloudflareaccess.com` redirects; if the lab vantage must be used, split the workflow: availability (lab) vs posture (external/API).

### Item: Admin action auditability

- Evidence: `config/docker/daemon.json` (`json-file` 20 MB × 5); live host Wazuh agent localfiles (journald/audit.log/dpkg + 3 commands; no container logs); `bootstrap/60-host-auditd.sh` (host file watches); `bootstrap/60-central-deploy.sh:216-230` (OpenSearch REST audit); `traefik.yml:30-32` + live access-log sample (no user field); live Grafana single admin; `ntfy user list`.
- What it does: records host identity/config changes and OpenSearch/Wazuh auth events.
- Current controls: auditd, OpenSearch security audit, Wazuh audit, decision log, rotated container logs.
- Missing controls: actor-level audit for Grafana/ntfy/IRIS console actions (logins, role/settings changes, deletes, exports) shipped to a durable/central store.
- Risks: an abusive admin action on those consoles leaves only rotated local logs; no alerting on admin-action anomalies.
- Recommended improvement: ship container logs to the Wazuh/OpenSearch pipeline (Wazuh docker-listener or a Vector source), enable Grafana/OSD audit features where available, and add rules for admin role/settings/delete events.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ADMIN-001 | Admin pages/APIs | dynamic.yml; live | Access + app logins | no origin auth | P2 | ADMIN-P2-001 fix |
| ADMIN-002 | User/org/role management | ACCESS §1 | single admin | no separation | P3 | per-service accounts |
| ADMIN-003 | Billing panels | n/a | — | — | — | — |
| ADMIN-004 | Document/ticket admin | IRIS | app auth | audit gap | P3 | ship logs |
| ADMIN-005 | Webhook/API key admin | relay/enroll | token-gated | shared enroll token | P2 | ACM finding |
| ADMIN-006 | Bulk ops | none found | — | — | — | — |
| ADMIN-007 | Approval flows | CODEOWNERS/label gate | advisory | plan-gated | P3 | other domain |
| ADMIN-008 | Impersonation | none found | — | — | — | — |
| ADMIN-009 | Settings | compose/env | code-managed | console settings not codified | P3 | document |
| ADMIN-010 | Exports | app features | app-level | no export audit | P3 | enable audit |
| ADMIN-011 | Destructive actions | bootstrap scripts | root + dry-run + ledger | — | — | — |
| ADMIN-012 | Confirmations | scripts | root gating | — | — | — |
| ADMIN-013 | Access-posture gate | external-smoke | weakened at HEAD | posture unverified | P2 | restore external check |
| ADMIN-014 | Admin action audit | logs/auditd | partial | no console actor audit | P2 | ship container logs |

## Findings

### ADMIN-P2-001 - Admin/observability consoles are exposed through public routers without origin authentication

- Severity: P2
- Confidence: High (config + live probes reproduced)
- Area: ADMIN
- Evidence:
  - `config/traefik/dynamic.yml:71-134` (grafana, dash, iris-public, soc-wazuh routers carry only `sec-headers`/`public-rate-limit`; only `falcon-ntop` has `falcon-basic-auth`)
  - Live origin probes 2026-10-09T21:23Z: `/`→302 Grafana login, `/dash/`→302 OSD login, `/ntop`→401, iris→302 `/dashboard`, soc→302 `/app/login`
  - `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §5-§6 (app logins behind Cloudflare; owner-IP bypass recorded)
  - `ledgers/risk_register.md` R-15 (public UI exposure OPEN, owner-gated); `ledgers/decision_log.md` 2026-09-21T19:05Z (bypass NAT caveat)
- What is happening: The consoles are reachable through the Cloudflare tunnel with only application logins at the origin; the sole network gate is Cloudflare Access at the edge plus the host firewall. The owner-IP bypass is active for iris/soc (verified live), so anything behind the owner NAT reaches those consoles without an Access challenge.
- Why it matters: An Access policy error/removal or a shared-NAT actor reduces protection to the application login; there is no origin-side control to fail closed.
- User / business impact: Admin console exposure beyond the intended Access gate.
- Security / privacy / reliability impact: Edge-only enforcement of the SOC/monitoring consoles.
- Recommended fix: Put an origin auth layer (or Access-JWT validation) in front of the console routers; alternatively record the residual acceptance explicitly against R-15 with the new live evidence.
- Suggested validation: staging Access-app removal test asserting origin denial; repeat live probes for all five hostnames and attach to the risk acceptance.
- Owner suggestion: @owner
- Effort estimate: M
- Dependencies: Cloudflare config for Access/JWT or service tokens
- Status: still-open (prior run ADMIN-P2-001; same root cause as SEC-P2-001)
- Endpoint / data path: public hostname → cloudflared → Traefik → console container
- Attack path: Access bypass/misconfig → app login brute force → console admin abuse

### Finding ID: (new) ADMIN-P2-002 - The Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement anymore

- Severity: P2
- Confidence: High (workflow diff + live behavior)
- Area: ADMIN
- Evidence:
  - `.github/workflows/external-smoke.yml:20-25` — comment: "Must run from GitHub's network: this gate asserts the public Cloudflare Access posture ... On the lab the vantage is internal and the result is wrong, so it stays on hosted"; `runs-on: [self-hosted, lab]`
  - `.github/workflows/external-smoke.yml:34-46` — any 302 passes; non-`cloudflareaccess.com` locations are reported "OK ... owner-IP Access bypass; origin reachable"
  - `.github/workflows/external-smoke.yml:59-66` — job summary still says "iris/soc: must be 302 to cloudflareaccess.com (Access still enforcing)"
  - Commits `70292a0` ("run on the self-hosted lab runners") and `08e20d1` ("accept the owner-IP Access bypass ... Access posture is verified externally"); no external verification artifact exists in the repo (grep)
  - Live 2026-10-09T21:24Z from the lab: iris → 302 origin `/dashboard`; soc → 302 origin `/app/login` (i.e., the now-accepted condition)
  - `docs/security/CI_GOVERNANCE_RECONCILIATION.md:40` still describes the workflow as "public-surface availability + Cloudflare Access posture"
- What is happening: The only automated check that asserted the Access gate on iris/soc was relaxed at HEAD to accept origin reachability from the lab vantage. The workflow self-description and the governance doc still claim posture verification, and the commit message's "verified externally" has no in-repo artifact.
- Why it matters: If the iris/soc Access apps are removed or misconfigured, CI remains green; the compensating control for the exposed consoles (Access) is no longer machine-verified.
- User / business impact: Silent loss of the edge control that gates the SOC consoles.
- Security / privacy / reliability impact: Verification gap on the primary control for admin-console exposure.
- Recommended fix: Restore a trustworthy posture check: run the posture assertion from an external vantage, or use a scoped Cloudflare API/service-token check; fail on non-Access redirects. If the lab vantage is kept for availability only, rename/split the workflow and remove the posture claim.
- Suggested validation: mutate a staging Access policy (remove app) and assert the check fails; or simulate a non-Access 302 and assert failure.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: external runner or scoped Cloudflare API token
- Status: open (new at `08e20d1`)
- Endpoint / data path: CI → https://iris.mainecybertech.us/, https://soc.mainecybertech.us/
- Attack path: none directly; this removes detection of an Access regression

### Finding ID: (new) ADMIN-P2-003 - No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions

- Severity: P2
- Confidence: High (log config + live agent config)
- Area: ADMIN
- Evidence:
  - `config/docker/daemon.json` — container logs use `json-file` with 20 MB × 5 rotation (local only)
  - Live host Wazuh agent localfiles (2026-10-09T21:33Z): `df`, `netstat`, `last`, `journald`, `/var/log/audit/audit.log`, `active-responses.log`, `dpkg.log` — no Docker container-log source
  - `bootstrap/60-host-auditd.sh` — watches identity/sudoers/ssh/firewall/secret metadata only
  - `bootstrap/60-central-deploy.sh:216-230` — OpenSearch REST audit enabled (covers OpenSearch/OSD backend calls and Wazuh indexer audit covers the Wazuh side)
  - `config/traefik/traefik.yml:30-32` + live access-log sample — JSON access log has ClientAddr/host/path/status, no authenticated user
  - Live Grafana: single `admin` account; live ntfy ACLs (monadmin admin)
- What is happening: Admin activity in Grafana, ntfy and IRIS is recorded only in rotated container-local logs; there is no durable, centrally searchable audit of who did what (logins, settings/role changes, deletes, exports) for those consoles. OpenSearch and Wazuh auth events are audited.
- Why it matters: The prompt's abuse cases (self-escalation, role/delete/export actions) cannot be reconstructed for the non-OpenSearch consoles; a compromised or careless admin leaves little durable evidence.
- User / business impact: Weaker incident reconstruction and accountability for the consoles that control monitoring/alerting and case data.
- Security / privacy / reliability impact: Audit/observability gap.
- Recommended fix: Ship container logs into the Wazuh/OpenSearch pipeline (Wazuh docker-listener, or a Vector source reading the json-file logs), enable app audit features where available (Grafana audit is Enterprise-only; OSD security audit already applies), and add detection rules for admin role/settings/delete/export events.
- Suggested validation: perform a read-only admin action (e.g., Grafana API GET with admin creds is not an action; use a lab Grafana user settings change in a maintenance window) and verify an event lands in OpenSearch.
- Owner suggestion: @owner
- Effort estimate: M
- Dependencies: log-shipping decision + Wazuh/Vector config
- Status: open (new)
- Endpoint / data path: console container stdout → json-file → (not shipped) → no central audit
- Attack path: admin console abuse leaves only local rotated logs

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Console exposure beyond Access | Medium | Medium | High | dynamic.yml; live probes | origin auth / accept R-15 |
| Access-posture regression undetected | Medium | Medium | High | external-smoke diff | restore external/API check |
| Admin actions not centrally audited | Medium | Medium | Medium | log config; agent localfiles | ship container logs |
| Shared admin identities | Low | Medium | Medium | ACCESS §1 | per-service accounts; OD-04 |

## Recommendations

### Immediate / Release Blocking

- None (the live firewall regression is tracked under SEC).

### This Week

- Fix or explicitly re-scope the Access-posture gate (`external-smoke`) and update the governance doc.
- Record the console-exposure residual (R-15) against the new live evidence, or fund the origin-auth fix.

### This Month

- Ship Grafana/ntfy/IRIS container logs to the central pipeline and add admin-action detection rules.
- Move to per-service admin accounts and close OD-04 custody.

### Later / Platform Evolution

- IdP/SSO in front of all consoles; per-operator identities; automated Access posture verification from an external vantage.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Split availability vs posture in `external-smoke` | stops false assurance | `.github/workflows/external-smoke.yml` | simulated non-Access 302 fails |
| Update the job summary text | removes self-contradiction | same | review |
| Add a Vector/Wazuh docker-log source | durable console audit | `config/vector/*`, Wazuh agent config | log lands in OpenSearch |
| Record R-15 acceptance with evidence | closes ambiguity | `ledgers/risk_register.md` | owner sign-off |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Origin auth / Access JWT for consoles | P2 | @owner | M | Cloudflare |
| External Access-posture check | P2 | @owner | S-M | external vantage/token |
| Console log shipping + rules | P2 | @owner | M | pipeline |
| Per-service admin accounts | P3 | @owner | S | owner decision |

## Suggested Tests

- CI: posture check must fail on a 302 that does not target `cloudflareaccess.com` (unit-test the shell function with fixture headers).
- Integration: Access-app removal test in a staging zone; assert origin denial.
- Audit: trigger a console admin action in a maintenance window and assert it is searchable centrally.
- Manual: quarterly review of console accounts and ACLs (Grafana users, ntfy ACLs, OSD internal users, IRIS users).

## Suggested Documentation Updates

- `.github/workflows/external-smoke.yml` comment/summary (align with actual behavior).
- `docs/security/CI_GOVERNANCE_RECONCILIATION.md:40` (describe the availability-vs-posture split).
- `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §5-§6 (residual acceptance; current Access state).
- `ledgers/risk_register.md` R-15 (re-affirm/refresh acceptance with live evidence).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What is the actual current Access policy set for falcon/iris/soc? | exposure reasoning | Cloudflare API read |
| Where will the external posture check run now that hosted runners are billing-blocked? | detection restoration | CI/platform decision |
| Is Grafana audit (Enterprise) an option? | console audit | licensing decision |

## Prior-Run Comparison

| Prior finding (falcon-20261005-full-main-e267ce1) | Status now | Notes |
|---|---|---|
| ADMIN-P2-001 consoles exposed without origin auth | still-open | config unchanged; re-verified live (iris/soc reachable via owner-IP bypass) |
| (none) | new | `external-smoke` posture gate weakened at `08e20d1` |
| (none) | new | no centralized console admin-action audit |

## Limitations

- Vendor UI internals not audited; console settings are only partly represented in the repo.
- Cloudflare Access state inferred from live HTTP behavior (no API read authorized).
- Audit-coverage conclusion is based on the live host agent configuration and repo log settings; a future log-shipping change would supersede it.

## Appendix

- Live probes (read-only, 2026-10-09T21:23-21:24Z): origin via loopback `--resolve`; public via IPv4 from egress 142.105.190.25; results recorded in the Verification table.
- Accounts: Grafana `/api/users` → `admin` only; `ntfy user list` → monadmin/falcon-relay/owner/watcher + anonymous denied.
- Audit sources: auditd watches (`bootstrap/60-host-auditd.sh`), OpenSearch REST audit (`bootstrap/60-central-deploy.sh:216-230`), Wazuh indexer audit (`plugins.security.audit.type: internal_opensearch`).

## Findings

| ID | Severity | Title |
|---|---|---|
| ADMIN-P2-001 | P2 | Admin/observability consoles are exposed through public routers without origin authentication |
| ADMIN-P2-002 | P2 | Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement anymore |
| ADMIN-P2-003 | P2 | No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions |
