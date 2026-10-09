# 24_access_control_matrix_audit — Prompt 24 - Access Control Matrix Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `24_access_control_matrix_audit.md` (area ACM, prompt)

## Verification Performed

# Access Control Matrix Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65`
- Generated at: 2026-10-09T21:45:00Z
- Auditor: subagent (domain 24)
- Area code: ACM
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/24_access_control_matrix_audit.md`
- Scope limitations: single-operator lab (no org/role model in the app sense); Cloudflare Access policy details were not read via API; app-internal role definitions (Grafana org roles, IRIS roles) are not represented in the repo and were only sampled live where possible.

## Scope

Reviewed: roles, permissions, membership, per-surface permissions, admin consoles, public/authenticated/internal routes, server actions, API endpoints, background jobs, DB helpers, middleware, client-side hiding, server enforcement, audit logs, authz tests. This repo is infrastructure/security tooling (no application code with end users), so the "matrix" is: host/services → route/port → auth mechanism → credential custody → enforcement point.

Not reviewed: vendor application internals beyond declared config; the edge-sensor repository; Cloudflare account configuration via API.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/PORT_PROTOCOL_MATRIX.md` | doc | route/port → auth/firewall matrix (N-01..N-28) | most complete route matrix; live-bind reconciliation appended |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md` | doc | human access surfaces + credential custody + §6 Access verification | no single consolidated matrix artifact |
| `docs/architecture/IDENTITY_AND_SECRETS.md` | doc | human/service identities, OpenSearch roles, lifecycle | Phase-0 baseline + 2026-10-02 annotations |
| `docs/architecture/TRUST_BOUNDARIES.md` | doc | TB-1..TB-9 identities/auth per boundary | authoritative control narrative |
| `config/traefik/dynamic.yml`, `config/ntfy/server.yml` | config | per-route auth/middleware | `falcon-basic-auth` only on `/ntop`; ntfy native auth |
| `compose/central/docker-compose.yml`, `bootstrap/60-central-deploy.sh` | deployment | service identities and OpenSearch roles | least-privilege roles; demo users removed |
| `automation/vpn/enroll-service.py`, `issue-enroll-token.sh` | code | machine credential issuance/expiry/revocation | per-device support exists; live uses shared token |
| `bootstrap/31-docker-user-firewall.sh`, `config/nftables/falcon.nft` | firewall | forwarded-port allowlist + host input policy | mgmt/admin subnets + bridges |
| `.github/workflows/*`, `.github/CODEOWNERS` | CI governance | repo roles/approvals | label-gated Dependabot; branch protection plan-gated (other domain) |
| Live checks (read-only) | live state | actual enforcement | `iptables -S DOCKER-USER`, `nft list chain`, `ss`, Grafana API users, `ntfy user list`, token-file structure |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `iptables -S DOCKER-USER` (live) | reproduction | forwarded-port authz | matches the repo allowlist + final DROP (management/admin RETURN) |
| `nft list chain inet falcon_filter input` (live) | reproduction | host input authz | **does not match repo**: blanket `iifname "wg0" accept` live (SEC finding) |
| Grafana `/api/users` (read-only) | verification | human roles | exactly one user `admin` (isAdmin=true); no external auth |
| `ntfy user list` (read-only) | verification | topic ACLs | anonymous denied; monadmin admin; relay write-only; owner rw; watcher ro |
| Enrollment token file (structure only) | verification | key lifecycle | one bare shared token; no per-device bindings or expiry |
| `curl` public hosts from owner IP (v4) | verification | Access bypass behavior | falcon → Access challenge; iris/soc → origin redirects |
| `docker ps` (live) | verification | running services vs declared | matches compose; Wazuh stack tag-only (other domain) |
| `find` for an access-control matrix artifact | self-consistency | consolidated matrix existence | no `access_control_matrix.md`; matrix is distributed across 4 docs |

## Executive Summary

There is no single consolidated access-control matrix artifact; instead the repo maintains four complementary documents (PORT_PROTOCOL_MATRIX, ACCESS_AND_ACCOUNTS, IDENTITY_AND_SECRETS, TRUST_BOUNDARIES) that together cover most of the surface. The matrix that exists is accurate for the host/network layer (verified live for the DOCKER-USER chain) but incomplete for: console application roles (Grafana org roles, OSD roles, IRIS roles), the Cloudflare Access layer (documented from a one-time verification, and now partially inconsistent with live behavior), and machine credential lifecycles (enrollment tokens).

Strengths: every network route has a documented exposure class and negative test; OpenSearch roles are least-privilege and applied by code; secret custody is per-class root-only; the ntopng basic-auth file was decoupled from the ntfy file; repo governance has CODEOWNERS + label-gated Dependabot.

Key gaps: (1) no consolidated role/route matrix artifact; (2) the live client-VPN enrollment credential is still a single shared token with no expiry despite per-device support; (3) the documented Cloudflare Access policy state no longer matches live behavior for the falcon host (live shows an Access challenge from the documented bypass IP while iris/soc pass through).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Roles (host) | `user`, `root` via sudo | operator/break-glass | single interactive account | Medium | IDENTITY §1; OD-04 custody pending |
| Roles (OpenSearch) | `admin`, `falcon_writer`, `falcon_reader`, `falcon_backup` | data access | least-privilege, code-applied | Low | `bootstrap/60-central-deploy.sh:131-155` |
| Roles (consoles) | Grafana admin; OSD/OpenSearch internal users; ntfy ACLs; IRIS roles | UI access | single admin each | Medium | not in repo except ntfy ACLs via provisioning |
| Membership | n/a (no org/tenant model) | — | N/A | — | see MT report |
| API keys/tokens | enrollment token(s), relay path token, service passwords | machine auth | mixed | Medium | shared enrollment token live |
| Admin console | Grafana/OSD/ntop/ntfy/Wazuh/IRIS/UniFi | operations | per-service auth | Medium | see ADMIN report |
| Public routes | 7 hostnames (dynamic.yml) | edge exposure | Access (3) / app auth | High | SEC-P2-001 |
| Internal routes | PORT_PROTOCOL_MATRIX N-01..N-28 | network authz | documented + firewalled | Low | one live drift (wg0) |
| Middleware | `sec-headers`, `public-rate-limit`, `falcon-basic-auth`, `ntfy-auth` | request controls | ntfy-auth unused | Low | dead config |
| Audit logs | auditd, OpenSearch REST, Wazuh audit, decision log | accountability | partial | Medium | see ADMIN report |
| Authz tests | phase7_security_checks, port_matrix_check, enrollment suite | verification | present | Low | no Access-posture test that works from the lab |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Roles | 3 | IDENTITY §1-3 | no per-operator roles; OD-04 pending | owner decision |
| Permissions | 4 | 60-central-deploy roles; ntfy ACLs | console roles not codified | document console roles |
| Org/tenant/workspace membership | N/A | single-tenant | — | see MT |
| Project/ticket/doc/billing/API key/webhook permission | 3 | enrollment/relay tokens; ACLs | shared enrollment token | per-device tokens |
| Admin console | 3 | ACCESS §1; live users | single admin; origin auth gap | see ADMIN |
| Public/authenticated/internal routes | 3 | PORT_PROTOCOL_MATRIX; dynamic.yml | live wg0 drift; Access doc drift | apply fix; re-verify Access |
| Server actions | N/A | no server-action framework | — | — |
| API endpoints | 3 | OpenSearch/Wazuh APIs; enroll API | no central API authz matrix | keep PORT matrix current |
| Background jobs | 3 | systemd timers (root) | run as root by design | least privilege where feasible |
| DB helpers | 3 | OpenSearch client roles | — | — |
| Middleware | 3 | dynamic.yml | ntfy-auth dead; XFF keying | fix rate-limit key |
| Client-side hiding | N/A | no SPA | — | — |

## Detailed Review

### Item: Route/port access matrix

- Evidence: `docs/architecture/PORT_PROTOCOL_MATRIX.md` N-01..N-28; live `iptables -S DOCKER-USER` and `nft list chain`.
- What it does: maps each port to source, purpose, auth, firewall owner, exposure class, negative test.
- Current controls: default-deny host input; DOCKER-USER allowlist for forwarded ports; wg0 per-port set in the repo.
- Missing controls: the live host still enforces the old blanket wg0 rule (SEC finding); no single role column for console users.
- Recommended improvement: keep the matrix as the source of truth; add a generated live-vs-doc diff to CI/health checks.

### Item: Human access surfaces and credentials

- Evidence: `ACCESS_AND_ACCOUNTS.md` §1-§5; live Grafana user list; ntfy user list; `/srv/falcon/secrets` modes.
- What it does: lists each surface, auth type, and credential custody.
- Current controls: root-only secret files; dedicated htpasswd files; per-class env files; rotation runbooks.
- Missing controls: no SSO/per-person identity; password policy/lifecycle undefined (documented gap); console roles not codified.
- Recommended improvement: add a role/permission table (console → account → role → scope) and an owner decision on SSO.

### Item: Machine credentials and key lifecycle

- Evidence: `automation/vpn/issue-enroll-token.sh`; `enroll-service.py:60-113`; live token file (1 bare line); `docs/security/ENROLLMENT_CLOSURE.md:15,78-100`; `docs/phase9/OWNER_ACTIONS.md` C6.
- What it does: supports `name:token[:expiry]` per-device bindings; a bare shared token is accepted only for names without a binding; expired bindings fail closed.
- Current controls: hmac compare, expiry support, per-device override, revocation by removing/replacing the line.
- Missing controls: the live credential is a single shared token with no expiry, baked into endpoint scripts; revocation requires rotating for all devices.
- Recommended improvement: issue per-device tokens for every active device, rotate the shared token, and add a lifecycle check to `enrollment_closure_check.sh`.

### Item: Cloudflare Access layer (documented state vs live)

- Evidence: `ACCESS_AND_ACCOUNTS.md:114-137` (apps for falcon/iris/soc; `bypass-owner-public-ip` for the owner's public address); live probes from egress 142.105.190.25: falcon → 302 `cloudflareaccess.com`, iris → 302 origin `/dashboard`, soc → 302 origin `/app/login`.
- What it does: edge identity gate for the public hostnames.
- Current controls: Access apps + allow-owner-domain + owner-IP bypass (as documented).
- Missing controls: no in-repo mechanism verifies Access posture from a non-lab vantage anymore (see ADMIN finding); the documented falcon bypass is not observable live.
- Recommended improvement: re-verify and record the Access app/policy state; correct §6; restore an external posture check when billing allows.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ACM-001 | Roles | IDENTITY §1-3 | single operator; least-priv service roles | no per-operator roles | P3 | owner decision |
| ACM-002 | Permissions | 60-central-deploy; ntfy ACLs | code-applied | console roles not codified | P3 | document |
| ACM-003 | Membership | N/A | single-tenant | — | — | — |
| ACM-004 | API key/webhook permission | enroll/relay code | token path, fail-closed | shared enroll token | P2 | per-device tokens |
| ACM-005 | Admin console | ACCESS §1; live | per-service logins | origin auth gap | P2 | see ADMIN |
| ACM-006 | Public/authenticated/internal routes | PORT matrix; dynamic.yml | firewall + Access + app auth | live wg0 drift | P1 | apply firewall fix |
| ACM-007 | Server actions | N/A | — | — | — | — |
| ACM-008 | API endpoints | OpenSearch/Wazuh | role-scoped | no consolidated API matrix | P3 | extend PORT matrix |
| ACM-009 | Background jobs | systemd timers | root-run | least privilege | P3 | review |
| ACM-010 | DB helpers | OpenSearch roles | least-priv | — | — | — |
| ACM-011 | Middleware | dynamic.yml | sec-headers/rate-limit | ntfy-auth dead; XFF key | P2 | fix key; remove dead config |
| ACM-012 | Client-side hiding | N/A | — | — | — | — |

## Findings

### ACM-P3-001 - No consolidated access-control matrix; authorization remains per-service and distributed across four documents

- Severity: P3
- Confidence: High
- Area: ACM
- Evidence:
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md` (route/port matrix), `docs/runbooks/ACCESS_AND_ACCOUNTS.md` (human surfaces), `docs/architecture/IDENTITY_AND_SECRETS.md` (identities/roles), `docs/architecture/TRUST_BOUNDARIES.md` (boundary controls)
  - `find . -iname '*access*matrix*'` → no consolidated artifact
  - Console application roles (Grafana org roles, OSD roles, IRIS roles) are not defined in the repo
- What is happening: The access-control knowledge exists but is spread across four documents with different scopes; there is no single route→auth→role→custody matrix an operator can review each patch window.
- Why it matters: Drift between docs and live state (as seen with the wg0 rule and the Access policy) is harder to detect; reviewers must read four documents to reconstruct access.
- User / business impact: Slower audits; higher chance of stale authorization documentation.
- Security / privacy / reliability impact: Medium-low; documentation/verification gap.
- Recommended fix: Publish `docs/security/access_control_matrix.md` generated from the four sources (route, exposure class, auth mechanism, enforcement point, account/role, custody, verification command), and reference it from ACCESS_AND_ACCOUNTS.
- Suggested validation: a check that every PORT_PROTOCOL_MATRIX row and every Traefik router appears in the matrix.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none
- Status: open (prior run ACM-P3-001)
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: (new) ACM-P2-002 - Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused

- Severity: P2
- Confidence: High (live token file structure + code)
- Area: ACM
- Evidence:
  - Live `/srv/falcon/secrets/vpn_enroll.token`: one line, bare token (no `name:token[:expiry]` bindings) — structure checked 2026-10-09T21:33Z, value not read
  - `automation/vpn/enroll-service.py:60-113` (shared-token fallback; per-device binding support; expiry enforcement)
  - `automation/vpn/issue-enroll-token.sh` (per-device issuance, 24h default TTL, replaces the binding on re-run)
  - `docs/security/ENROLLMENT_CLOSURE.md:15,78-100` (shared token baked into endpoint scripts; rotate after onboarding)
  - `docs/phase9/OWNER_ACTIONS.md` C6 (owner action; "shared token unrotated")
- What is happening: The hardened per-device token flow exists and is tested, but the live credential remains one shared secret accepted for any device name without a binding and with no expiry; the shared secret is distributed inside endpoint installer scripts.
- Why it matters: Any endpoint (or anyone who obtains a script) can enroll arbitrary new peers, gaining persistent WireGuard access; revocation means rotating the secret for every device.
- User / business impact: Fleet-wide credential compromise blast radius; onboarding/offboarding is not per-device.
- Security / privacy / reliability impact: Medium; machine-credential lifecycle gap.
- Recommended fix: Issue per-device tokens for every active device (`issue-enroll-token.sh <name>`), rotate the shared token, remove the bare line once all devices are bound, and extend `enrollment_closure_check.sh` to flag bare shared tokens in the live file.
- Suggested validation: enroll with a bound device using the shared token → 403; enroll with an expired token → 403; live file contains no bare token.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: device onboarding window (owner)
- Status: open (new; documented owner action C6)
- Endpoint / data path: `POST https://enroll.mainecybertech.us/enroll` → Traefik → enroll-service → wg0.conf
- Attack path: leaked shared token → arbitrary peer enrollment → WireGuard network access

### Finding ID: (new) ACM-P3-002 - Documented Cloudflare Access policy state does not match live behavior for the falcon host

- Severity: P3
- Confidence: High (live probe from the documented bypass IP)
- Area: ACM
- Evidence:
  - `docs/runbooks/ACCESS_AND_ACCOUNTS.md:124-134` (Access apps for falcon/iris/soc "Each carries an allow-owner-domain policy plus a bypass-owner-public-ip policy for the owner's public address"; external probe description)
  - `ledgers/decision_log.md` 2026-09-21T19:05Z (bypass added for 142.105.190.25/32 on the falcon app)
  - Live 2026-10-09T21:24Z from egress 142.105.190.25: `https://falcon.mainecybertech.us/` → 302 to `mainecybertech.cloudflareaccess.com` (challenge); `iris`/`soc` → origin redirects (bypass honored)
- What is happening: The matrix documentation says the falcon app carries an owner-IP bypass; live behavior shows the challenge from that exact IP, while iris/soc bypass as documented. Either the policy changed without a ledger entry or the doc is stale.
- Why it matters: Operators rely on the documented bypass for access; auditors/reviewers rely on it to reason about exposure. An unrecorded policy difference undermines the Access model documentation.
- User / business impact: Operator access expectations may be wrong (owner lockout vs expected bypass).
- Security / privacy / reliability impact: Low (more enforcement, not less), but documentation accuracy.
- Recommended fix: Re-verify the three Access apps via the Cloudflare API, record the current policies, and update ACCESS_AND_ACCOUNTS §6 + decision log; note the result in the external-smoke rationale.
- Suggested validation: repeat the read-only probe from the owner IP for all three hosts and diff against §6.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: Cloudflare API token (`cf_api` scope)
- Status: open (new)
- Endpoint / data path: internet → Cloudflare Access → tunnel → Traefik
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Shared enrollment token without expiry | Medium | Medium | Medium | live token file | per-device tokens + rotation |
| Access policy doc drift | Low | Medium | Medium | live vs docs | re-verify + record |
| Matrix fragmentation | Low | High | Low | 4 docs, no artifact | consolidated matrix |

## Recommendations

### Immediate / Release Blocking

- None in this domain (the live wg0 firewall regression is tracked under SEC).

### This Week

- Issue per-device enrollment tokens and rotate the shared token (owner action C6).
- Re-verify and record the Cloudflare Access app/policy state; update ACCESS §6.

### This Month

- Publish the consolidated `access_control_matrix.md` and wire it into the docs index.

### Later / Platform Evolution

- IdP/SSO with per-operator identities (R-15); per-service admin accounts.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Consolidated matrix artifact | single review surface | `docs/security/access_control_matrix.md` | cross-check vs PORT matrix |
| `issue-enroll-token.sh` for active devices | per-device revocation | `/srv/falcon/secrets/vpn_enroll.token` | live file structure check |
| Correct ACCESS §6 | doc accuracy | `docs/runbooks/ACCESS_AND_ACCOUNTS.md` | probe diff |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Per-device enrollment only | P2 | @owner | S | device list |
| Access policy verification automation | P2 | @owner | M | external vantage |
| Console role inventory | P3 | @owner | S | app configs |

## Suggested Tests

- Unit: token-file parser tests for bare/shared/bound/expired lines (exists; extend for "no bare token" assertion).
- Integration: enroll with shared token for a bound name → 403; expired token → 403.
- Regression: matrix-completeness check (every Traefik router + PORT matrix row present).
- Manual: read-only Cloudflare API read of Access apps after any policy change; record in the decision log.

## Suggested Documentation Updates

- Create `docs/security/access_control_matrix.md`.
- Update `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §6 (current Access policy state).
- Update `docs/security/ENROLLMENT_CLOSURE.md` with the live token state and retirement steps.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why does falcon challenge the documented bypass IP? | doc/live consistency | Cloudflare API read |
| Which devices still rely on the shared token? | retirement plan | owner device inventory |
| Are Grafana/OSD/IRIS roles documented anywhere? | matrix completeness | app configs/exports |

## Prior-Run Comparison

| Prior finding (falcon-20261005-full-main-e267ce1) | Status now | Notes |
|---|---|---|
| ACM-P3-001 no consolidated access-control matrix | still-open | docs improved (PORT matrix live-bind reconciliation, ACCESS §6) but no single artifact; console roles still not codified |
| (none) | new | shared enrollment token lifecycle (ACM-P2-002) |
| (none) | new | Access policy doc vs live mismatch (ACM-P3-002) |

## Limitations

- Cloudflare Access policy state not read via API; conclusions rest on live HTTP behavior + docs.
- Console-internal role models (Grafana org roles, IRIS role matrix) are not represented in the repo; sampled only where read-only APIs allowed (Grafana: single admin).
- The matrix in this report is derived from repo docs + live checks; it does not replace the proposed generated artifact.

## Appendix

- Key lifecycle commands: `automation/vpn/issue-enroll-token.sh <name>`; revocation = remove/replace the binding line; service re-reads the file per request (`enroll-service.py:60-92`).
- Live access checks (read-only): `iptables -S DOCKER-USER`; `nft list chain inet falcon_filter input`; Grafana `/api/users`; `docker exec falcon-central-ntfy-1 ntfy user list`.

## Findings

| ID | Severity | Title |
|---|---|---|
| ACM-P3-001 | P3 | No consolidated access-control matrix; authorization remains per-service and distributed across four documents |
| ACM-P2-001 | P2 | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused |
| ACM-P3-002 | P3 | Documented Cloudflare Access policy state does not match live behavior for the falcon host |
