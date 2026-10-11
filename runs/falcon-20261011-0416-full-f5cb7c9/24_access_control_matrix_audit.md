# 24_access_control_matrix_audit — Prompt 24 - Access Control Matrix Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `24_access_control_matrix_audit.md` (area ACM, prompt)

## Verification Performed

# Access Control Matrix Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:35:00Z
- Auditor: subagent (domain 24)
- Area code: ACM
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/24_access_control_matrix_audit.md`
- Scope limitations: this repository is infrastructure/security tooling, not an application with end users, so the "matrix" is host/services → route/port → auth mechanism → credential custody → enforcement point. Console application roles (Grafana org roles, central OSD roles, IRIS roles) are not defined in the repository; Cloudflare state was read read-only via the zone API.

## Scope

Reviewed: roles, permissions, membership (N/A), per-surface permissions, admin consoles, public/authenticated/internal routes, server actions (N/A), API endpoints, background jobs, DB helpers, middleware, client-side hiding (N/A), server enforcement, audit logs, authz tests.

Not reviewed: vendor UI code paths; the edge-sensor repository; Cloudflare account-level configuration beyond the zone's Access/DNS/tunnel read.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/PORT_PROTOCOL_MATRIX.md` | doc | route/port → auth/firewall matrix (N-01..N-28 + addendum) | complete route matrix; live-bind reconciliation |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md` | doc | human surfaces, custody, Access §6 | §6 stale for the falcon app (finding) |
| `docs/architecture/IDENTITY_AND_SECRETS.md` | doc | human/service identities, OpenSearch roles | one interactive account; role table + 2026-10-02 update |
| `docs/architecture/TRUST_BOUNDARIES.md` | doc | TB-1..TB-9 boundary controls | authoritative control narrative |
| `config/traefik/dynamic.yml`, `config/ntfy/server.yml` | config | per-route auth/middleware | `falcon-basic-auth` only on `/ntop`; ntfy deny-all |
| `compose/central/docker-compose.yml`, `bootstrap/60-central-deploy.sh` | deployment | service identities + OpenSearch roles | least-privilege roles (131-155); demo users deleted (152-155) |
| `automation/vpn/enroll-service.py`, `issue-enroll-token.sh`, `enroll-service-install.sh` | code/tooling | machine credential issuance/expiry/revocation/deployment | repo supports expiry; live copy is older (finding) |
| `.github/workflows/*`, `.github/CODEOWNERS` | CI governance | repo roles/approvals | label-gated Dependabot; CODEOWNERS invalid (other domain) |
| `docs/security/ENROLLMENT_CLOSURE.md`, `docs/security/ENROLL_API.md` | docs | enrollment lifecycle + contract | closure doc predates the expiry feature |
| Live checks (read-only) | live state | actual enforcement | nft/iptables, Grafana API, ntfy ACLs, OpenSearch security API, token-file structure, live enroll `/health` + hash, Cloudflare Access/DNS/tunnel API |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sha256sum /etc/nftables.conf` vs repo + live `nft list chain` | reproduction | host input authz | byte-identical (`f6b18722…`); per-port wg0 set; live drift from the prior run resolved |
| `iptables -S DOCKER-USER` (live) | reproduction | forwarded-port authz | allowlist + final DROP unchanged from prior run |
| Grafana `/api/users`, service accounts, auth keys | verification | human/service roles | exactly one `admin` (isAdmin); 0 service accounts; 0 API keys |
| OpenSearch security API (5 users; `falcon_writer`/`falcon_reader`/`falcon_backup` role bodies) | verification | API permission model | least-privilege index patterns (`falcon-*`); no demo users |
| `ntfy user list` | verification | topic ACLs | monadmin admin; relay write-only; owner rw; watcher ro; anonymous denied; ~11 stale deny rows retained |
| Token-file structure (fields counted; values never read) | verification | key lifecycle | 1 line, fields=1 → bare shared token, no expiry |
| Live `/opt/falcon/vpn-enroll/enroll-service.py` sha256 vs repo/git history | reproduction | deployed enforcement vs repo | live = `70739c3` (2026-10-02); repo = `c04c006` (2026-10-03, expiry support) |
| Cloudflare zone API: Access apps + policies | verification | edge authorization ground truth | falcon app: 2× `allow-mainecybertech.us`, **no bypass**; soc/iris: bypass 142.105.190.25/32 + allow-domain; 2 dead apps remain |
| Cloudflare zone API: DNS + tunnel configurations | verification | route inventory | tunnel v13 ingress = falcon/iris/enroll; `dash.falcon` DNS/Access app remain but are not served |
| Public probes from owner egress 142.105.190.25 | reproduction | documented bypass behavior | falcon → Access challenge (no bypass); iris/soc → origin redirects (bypass) |
| `find . -iname '*access*matrix*'` | self-consistency | consolidated matrix existence | none in this repository (an edge-repo matrix exists only under `docs/audits/`) |

## Executive Summary

The access-control knowledge remains distributed across four documents and is accurate for the network layer (verified live: the DOCKER-USER allowlist and the narrowed wg0 set both match the repo). Two things changed materially since the prior run: the wg0 firewall fix is now applied live (the prior ACM-006 drift is closed), and the enrollment-service deployment is now a *new* authorization-lifecycle gap — the repo implements per-device token expiry, but the deployed public service is an older build that neither enforces expiry nor accepts the documented `<name>:<token>:<expiry>` lines. The shared enrollment token also remains live and bare.

Current gaps:
1. **ACM-P2-001 (still open)** — the live enrollment credential is one shared token with no expiry; per-device lifecycle exists in the repo but is unused, and the closure check does not flag bare tokens.
2. **ACM-P2-003 (new)** — the deployed enrollment service (`70739c3`) does not implement the expiry/contract behavior the repo declares (`c04c006`); the documented issuance tool is rejected by the live parser, and no deployed-vs-repo check exists. Same root cause as SEC-P2-004.
3. **ACM-P3-001 (still open)** — no consolidated access-control matrix artifact; console roles are not codified.
4. **ACM-P3-002 (still open, now API-confirmed)** — the documented Cloudflare Access state is stale: the falcon app has **no** owner-IP bypass policy (live behavior confirms the challenge), while iris/soc do; the decision log records the bypass as added but never records its removal. Two dead Access apps (`falcon-dash`, `falcon-ntfy`) and the `dash.falcon` DNS record remain.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Roles (host) | `user` (sudo/adm), `root` | operator/break-glass | single interactive account | Medium | IDENTITY §1; OD-04 pending |
| Roles (OpenSearch) | `admin`, `falcon_writer`, `falcon_reader`, `falcon_backup` | data access | least-privilege, live-verified | Low | `bootstrap/60-central-deploy.sh:131-155` |
| Roles (consoles) | Grafana admin; OSD internal users; ntfy ACLs; IRIS roles | UI access | single admin each | Medium | not in repo except ntfy provisioning |
| Membership | n/a (no org/tenant model) | — | N/A | — | see MT report |
| API keys/tokens | enrollment token, relay path token, service passwords | machine auth | mixed | Medium | shared enrollment token live |
| Admin console | Grafana/OSD/ntop/ntfy/Wazuh/IRIS/UniFi | operations | per-service auth | Medium | see ADMIN report |
| Public routes | falcon/iris/soc/enroll (+2 dead) | edge exposure | Access (3) / token (1) | High | SEC-P2-001 |
| Internal routes | PORT_PROTOCOL_MATRIX N-01..N-28 | network authz | documented + firewalled | Low | live wg0 now matches |
| Middleware | `sec-headers`, `public-rate-limit`, `falcon-basic-auth`, `ntfy-auth` | request controls | ntfy-auth unused | Low | dead config |
| Audit logs | auditd, OpenSearch REST (live), Wazuh audit, decision log | accountability | partial | Medium | see ADMIN report |
| Authz tests | phase7_security_checks, port_matrix_check, enrollment suite | verification | present | Medium | no deployed-artifact hash check; no Access-posture test that works from the lab |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Roles | 3 | IDENTITY §1-3; live users | no per-operator roles; OD-04 pending | owner decision |
| Permissions | 4 | live OpenSearch roles; ntfy ACLs | console roles not codified | document console roles |
| Org/tenant/workspace membership | N/A | single-tenant | — | see MT |
| API key/webhook permission | 2 | enroll/relay code | shared token; deployed service stale | ACM-P2-001/002 |
| Admin console | 3 | ACCESS §1; live users | origin auth gap | see ADMIN |
| Public/authenticated/internal routes | 3 | PORT matrix; dynamic.yml; live nft | Access doc drift; dead apps | ACM-P3-002 |
| Server actions | N/A | no server-action framework | — | — |
| API endpoints | 3 | OpenSearch/Wazuh APIs; enroll API | no central API authz matrix | keep PORT matrix current |
| Background jobs | 3 | systemd timers (root) | run as root by design | least privilege where feasible |
| DB helpers | 3 | OpenSearch client roles | — | — |
| Middleware | 3 | dynamic.yml | ntfy-auth dead; XFF keying | fix rate-limit key |
| Client-side hiding | N/A | no SPA | — | — |

## Detailed Review

### Item: Route/port access matrix

- Evidence: `docs/architecture/PORT_PROTOCOL_MATRIX.md` N-01..N-28 + live-bind reconciliation + N-24 addendum; live `iptables -S DOCKER-USER`; live `nft list chain inet falcon_filter input`; `/etc/nftables.conf` sha match.
- What it does: maps each port to source, purpose, auth, firewall owner, exposure class, negative test.
- Current controls: default-deny host input; DOCKER-USER allowlist for forwarded ports; per-port wg0 set applied live.
- Missing controls: no single role column for console users; no automated live-vs-doc diff; N-24 residual wording overstates the peer-class resolution.
- Recommended improvement: keep the matrix as source of truth; add a live-vs-doc diff to a health check; correct the N-24 residual.

### Item: Human access surfaces and credentials

- Evidence: `ACCESS_AND_ACCOUNTS.md` §1-§5; live Grafana users; ntfy ACLs; `/srv/falcon/secrets` modes (dir 0700; files 0600; htpasswd 0640).
- What it does: lists each surface, auth type, credential custody.
- Current controls: root-only secret files; dedicated htpasswd files; per-class env files; rotation runbooks.
- Missing controls: no SSO/per-person identity; password policy undefined; console roles not codified.
- Recommended improvement: add a role/permission table (console → account → role → scope) and an owner decision on SSO.

### Item: Machine credentials and key lifecycle

- Evidence: `issue-enroll-token.sh`; `enroll-service.py:60-113` (repo); live token file structure; live `/opt` service hash; `ENROLLMENT_CLOSURE.md:15,78-100`.
- What it does: supports `name:token[:expiry]` bindings; bare shared token accepted only for names without a binding.
- Current controls (repo): HMAC compare, expiry support with fail-closed malformed handling, per-device override, revocation by replacing the line.
- Current controls (live): HMAC compare, per-device override (no expiry field); token file read per request.
- Missing controls: per-device tokens are unused; the live service is a stale build; no pruning of expired bindings; no check that the deployed copy matches the repo.
- Recommended improvement: reinstall the service; issue per-device tokens; rotate the shared token; extend `enrollment_closure_check.sh` to flag bare tokens and the deployed hash.
- Suggested validation: enroll with a bound device using the shared token → 403; expired token → 403; live file contains no bare token.

### Item: Cloudflare Access layer (documented state vs live, now API-verified)

- Evidence: `ACCESS_AND_ACCOUNTS.md:114-141`; `decision_log.md:47,139,140`; Cloudflare zone API (`/access/apps`, policies); public probes from 142.105.190.25.
- What it does: edge identity gate for the public hostnames.
- Current controls (API): falcon app — 2× `allow-mainecybertech.us` (email domain), no bypass; soc/iris apps — `bypass-owner-public-ip` 142.105.190.25/32 + `allow-owner-domain`; all session 24 h. Dead apps: `falcon-dash`, `falcon-ntfy` (allow-domain only, no served route).
- Missing controls: no in-repo mechanism verifies Access posture from a non-lab vantage (see ADMIN-P2-002); the doc/decision log do not reflect the falcon bypass removal.
- Recommended improvement: update §6 + decision log; delete the dead apps and the `dash.falcon` DNS record; restore an external posture check.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| ACM-001 | Roles | IDENTITY §1-3 | single operator; least-priv service roles | no per-operator roles | P3 | owner decision |
| ACM-002 | Permissions | live OpenSearch roles; ntfy ACLs | code-applied | console roles not codified | P3 | document |
| ACM-003 | Membership | N/A | single-tenant | — | — | — |
| ACM-004 | API key/webhook permission | enroll/relay code | token path, fail-closed | shared enroll token; stale live service | P2 | ACM-P2-001/002 |
| ACM-005 | Admin console | ACCESS §1; live | per-service logins | origin auth gap | P2 | see ADMIN |
| ACM-006 | Public/authenticated/internal routes | PORT matrix; dynamic.yml; live nft | firewall + Access + app auth | Access doc drift | P3 | ACM-P3-002 |
| ACM-007 | Server actions | N/A | — | — | — | — |
| ACM-008 | API endpoints | OpenSearch/Wazuh | role-scoped | no consolidated API matrix | P3 | extend PORT matrix |
| ACM-009 | Background jobs | systemd timers | root-run | least privilege | P3 | review |
| ACM-010 | DB helpers | OpenSearch roles | least-priv | — | — | — |
| ACM-011 | Middleware | dynamic.yml | sec-headers/rate-limit | ntfy-auth dead; XFF key | P2 | fix key; remove dead config |
| ACM-012 | Client-side hiding | N/A | — | — | — | — |
| ACM-013 | Deployed artifact binding | live `/opt` hash | none | deployed service stale | P2 | ACM-P2-003 |
| ACM-014 | Access estate hygiene | zone API | apps + policies | dead apps; doc stale | P3 | ACM-P3-002 |

## Findings

### ACM-P2-001 - Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused

- Severity: P2
- Confidence: High (live token file structure + code)
- Area: ACM
- Evidence:
  - Live `/srv/falcon/secrets/vpn_enroll.token`: 1 line, fields=1 (bare token; no `name:token[:expiry]` bindings), 0600 root, mtime 2026-09-28 — structure checked 2026-10-11, value never read
  - `automation/vpn/enroll-service.py:60-113` (repo: shared-token fallback; per-device binding; expiry enforcement)
  - `automation/vpn/issue-enroll-token.sh` (per-device issuance, 24 h default TTL)
  - `automation/validation/enrollment_closure_check.sh` (does not flag bare/shared tokens or expired bindings)
  - `docs/security/ENROLLMENT_CLOSURE.md:15,78-100` (shared token baked into endpoint scripts; rotate after onboarding)
  - `docs/phase9/OWNER_ACTIONS.md` C6 (owner action; shared token unrotated)
- What is happening: The hardened per-device flow exists and is tested, but the live credential remains one shared secret accepted for any device name without a binding and with no expiry; it is distributed inside endpoint installer scripts. Additionally the deployed service cannot enforce expiry (ACM-P2-003).
- Why it matters: Any endpoint (or anyone who obtains a script) can enroll arbitrary new peers, gaining persistent WireGuard access; revocation means rotating the secret for every device.
- User / business impact: Fleet-wide credential compromise blast radius; onboarding/offboarding is not per-device.
- Security / privacy / reliability impact: Medium; machine-credential lifecycle gap.
- Recommended fix: reinstall the current service (ACM-P2-003), issue per-device tokens for every active device, rotate the shared token, remove the bare line once all devices are bound, and extend `enrollment_closure_check.sh` to flag bare tokens.
- Suggested validation: enroll with a bound device using the shared token → 403; enroll with an expired token → 403; live file contains no bare token.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: device onboarding window (owner); deployed-service refresh (ACM-P2-003)
- Status: still-open (prior ID ACM-P2-001)
- Endpoint / data path: `POST https://enroll.mainecybertech.us/enroll` → Traefik → enroll-service → wg0.conf
- Attack path: leaked shared token → arbitrary peer enrollment → WireGuard network access

### ACM-P2-003 - Deployed enrollment service does not enforce per-device token expiry; issuance tool and deployed enforcement disagree (no deployed-artifact binding)

- Severity: P2
- Confidence: High (live file hash vs git history; code diff; live behavior probe)
- Area: ACM
- Evidence:
  - Live `/opt/falcon/vpn-enroll/enroll-service.py` sha256 `ed7d02ab…` = commit `70739c3` (2026-10-02); repo sha256 `cdd4c671…` = `c04c006` (2026-10-03, +40/−13 lines adding expiry + contract)
  - `automation/vpn/issue-enroll-token.sh:44` writes `<name>:<token>:<expiry>`; the deployed parser (`name, _, token = line.partition(":")`) treats the remainder as the token, so an expiry-bearing binding is rejected (403) — issuance and enforcement disagree
  - `automation/vpn/enroll-service-install.sh:15,21` is manual and not wired into bootstrap; no validation script hashes the deployed copy; `/health` reports the same version (`falcon-vpn-enroll/1.1`) on both builds
  - `automation/validation/enrollment_closure_check.sh` has no expiry/pruning/deployed-hash check
- What is happening: The key lifecycle declared in the repository (per-device expiry, fail-closed malformed expiry, contract doc) is not the lifecycle enforced by the deployed public service; the deployment has no binding to the repo.
- Why it matters: The ACM-P2-001 remediation cannot be executed as written, and a security control claimed by the repo is absent at the boundary.
- User / business impact: Per-device issuance fails until the service is refreshed.
- Security / privacy / reliability impact: Lifecycle control not enforced; no pruning of expired bindings exists even in the repo.
- Recommended fix: reinstall from the deployed tree, add a deployed-hash assertion, bump the service version on behavior changes, and add an expired-binding prune step to the lifecycle tooling.
- Suggested validation: `automation/vpn/test_enroll_service.sh` run against the deployed file; live issuance of a short-TTL token then a 403 after expiry (lab).
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none
- Status: open (new; same root cause as SEC-P2-004, filed here for the key-lifecycle check)
- Endpoint / data path: `POST https://enroll.mainecybertech.us/enroll` → live service (stale build)
- Attack path: none identified (fail-closed); control/verification gap

### ACM-P3-001 - No consolidated access-control matrix; authorization remains per-service and distributed across four documents

- Severity: P3
- Confidence: High
- Area: ACM
- Evidence:
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md`, `docs/runbooks/ACCESS_AND_ACCOUNTS.md`, `docs/architecture/IDENTITY_AND_SECRETS.md`, `docs/architecture/TRUST_BOUNDARIES.md`
  - `find . -iname '*access*matrix*'` → no consolidated artifact in this repository
  - Console application roles (Grafana org roles, central OSD roles, IRIS roles) are not defined in the repo; ntfy ACLs exist only as live state
- What is happening: The access-control knowledge exists but is spread across four documents with different scopes; there is no single route→auth→role→custody matrix.
- Why it matters: Doc/live drift (Access policy, deployed service) is harder to detect; reviewers must read four documents.
- User / business impact: Slower audits; higher chance of stale authorization documentation.
- Security / privacy / reliability impact: Medium-low; documentation/verification gap.
- Recommended fix: publish `docs/security/access_control_matrix.md` generated from the four sources (route, exposure class, auth mechanism, enforcement point, account/role, custody, verification command) and reference it from ACCESS_AND_ACCOUNTS.
- Suggested validation: a check that every PORT_PROTOCOL_MATRIX row and every Traefik router appears in the matrix.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior ID ACM-P3-001)
- Endpoint / data path: n/a
- Attack path: none identified

### ACM-P3-002 - Documented Cloudflare Access policy state does not match live behavior: the falcon app has no owner-IP bypass (and two dead apps remain)

- Severity: P3
- Confidence: High (Cloudflare zone API read + live probes from the documented bypass IP)
- Area: ACM
- Evidence:
  - `docs/runbooks/ACCESS_AND_ACCOUNTS.md:124-134` ("Each carries an `allow-owner-domain` policy plus a `bypass-owner-public-ip` policy for the owner's public address"; "the owner IP is on the Access bypass policy by design")
  - `ledgers/decision_log.md:47` (bypass added 2026-09-21 for 142.105.190.25/32 on the falcon app); `:139,:140` (iris/soc bypass added 2026-09-28) — no entry records a removal
  - Zone API: falcon app `a8bb98c6…` policies = two identical `allow-mainecybertech.us` (no bypass); soc `adfd5945…` and iris `88aec22b…` = `bypass-owner-public-ip` 142.105.190.25/32 + `allow-owner-domain`
  - Live from egress 142.105.190.25 (trace-verified) 2026-10-11T04:24Z: falcon → 302 `mainecybertech.cloudflareaccess.com` (challenge); iris → 302 origin `/dashboard`; soc → 302 origin `/app/login`
  - Dead estate: Access apps `falcon-dash.falcon.mainecybertech.us` and `falcon-ntfy.falcon.mainecybertech.us` still exist; `dash.falcon.mainecybertech.us` still has a proxied CNAME but is not in tunnel v13 ingress (404)
- What is happening: The falcon app lost (or never had applied at review time) the documented owner-IP bypass; the doc and decision log still claim it. Two dead Access apps and one dead DNS record remain.
- Why it matters: Operators rely on the documented bypass; auditors rely on the doc to reason about exposure; the external-smoke rationale assumes the lab vantage sees the bypass.
- User / business impact: Owner access expectations may be wrong; minor estate hygiene.
- Security / privacy / reliability impact: Low (more enforcement, not less) — documentation accuracy.
- Recommended fix: update ACCESS §6 and the decision log with the API-verified policy set; delete the dead Access apps and the `dash.falcon` DNS record; de-duplicate the falcon app's allow policies.
- Suggested validation: repeat the read-only API read and the probe from the owner IP; diff against §6.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: Cloudflare API token (available, read-only)
- Status: still-open (prior ID ACM-P3-002; evidence upgraded from inference to API read)
- Endpoint / data path: internet → Cloudflare Access → tunnel → Traefik
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Shared enrollment token without expiry | Medium | Medium | Medium | live token file | per-device tokens + rotation |
| Deployed enrollment service stale (no expiry enforcement) | Medium | High | Medium | live vs repo hash | reinstall + hash check |
| Access policy doc drift / dead apps | Low | Medium | Medium | zone API | update doc; delete dead apps |
| Matrix fragmentation | Low | High | Low | 4 docs, no artifact | consolidated matrix |

## Recommendations

### Immediate / Release Blocking

- None in this domain (the live wg0 drift is closed).

### This Week

- Reinstall the enrollment service and add a deployed-artifact hash check (ACM-P2-003).
- Issue per-device enrollment tokens and rotate the shared token (ACM-P2-001 / owner action C6).
- Update ACCESS §6 + decision log with the API-verified Access policies; delete the dead apps/DNS (ACM-P3-002).

### This Month

- Publish the consolidated `access_control_matrix.md` and wire it into the docs index (ACM-P3-001).
- Add expired-binding pruning and a bare-token assertion to the enrollment lifecycle tooling.

### Later / Platform Evolution

- IdP/SSO with per-operator identities (R-15); per-service admin accounts.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `enroll-service-install.sh` re-run + hash check | closes the deployed drift | `automation/vpn/enroll-service-install.sh` | live sha == repo |
| `issue-enroll-token.sh` for active devices | per-device revocation | `/srv/falcon/secrets/vpn_enroll.token` | live file structure check |
| Correct ACCESS §6 + delete dead apps | doc/estate accuracy | `docs/runbooks/ACCESS_AND_ACCOUNTS.md`; Cloudflare | API read diff |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Per-device enrollment only | P2 | @owner | S | device list + service refresh |
| Deployed-artifact hash checks | P2 | @owner | S | validation scripts |
| Access policy verification automation | P2 | @owner | M | external vantage |
| Console role inventory | P3 | @owner | S | app configs |

## Suggested Tests

- Unit: token-file parser tests for bare/bound/expired lines (exists; extend for "no bare token" and deployed-hash assertions).
- Integration: enroll with shared token for a bound name → 403; expired token → 403; future-expiry token → 200.
- Regression: matrix-completeness check (every Traefik router + PORT matrix row present); deployed-vs-repo hash check for host-run services.
- Manual: read-only Cloudflare API read of Access apps/policies after any policy change; record in the decision log.

## Suggested Documentation Updates

- Create `docs/security/access_control_matrix.md`.
- Update `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §6 (current Access policy set; dead apps removed).
- Update `docs/security/ENROLLMENT_CLOSURE.md` with the deployed build and redeploy step.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| When/why was the falcon Access bypass removed? | doc/live consistency | owner + Cloudflare audit log |
| Which devices still rely on the shared token? | retirement plan | owner device inventory |
| Should central OSD/console roles be codified? | matrix completeness | app configs/exports |

## Prior-Run Comparison

| Prior finding (falcon-20261009-2117-full-08e20d1) | Status now | Notes |
|---|---|---|
| ACM-P2-001 shared enrollment token, per-device unused | still-open | live token file still bare; re-verified 2026-10-11 |
| ACM-P3-001 no consolidated access-control matrix | still-open | no new artifact; console roles still not codified |
| ACM-P3-002 Access doc vs live mismatch | still-open | now API-confirmed: falcon app has no bypass; dead apps/DNS remain |
| (none) | new ACM-P2-003 | deployed enrollment service stale (expiry not enforced; issuance tool rejected) |
| live wg0 drift (cross-listed as ACM-006 in the prior report) | verified-fixed | live nft == repo (`f6b18722…`) |

## Limitations

- Console-internal role models (Grafana org roles, IRIS role matrix, Wazuh indexer internal users) are not represented in the repo; the Wazuh indexer user set was not enumerated (separate admin credentials).
- Cloudflare reads were zone-scoped and read-only; account-level policies (if any) were not enumerated.
- The proposed consolidated matrix in this report is derived from repo docs + live checks; it does not replace the generated artifact.

## Appendix

- Key lifecycle commands: `automation/vpn/issue-enroll-token.sh <name>`; revocation = replace/remove the binding line; the service re-reads the file per request.
- Live access checks (read-only): `iptables -S DOCKER-USER`; `nft list chain inet falcon_filter input`; Grafana `/api/users`; `docker exec falcon-central-ntfy-1 ntfy user list`; OpenSearch `_plugins/_security/api/internalusers`; Cloudflare `/access/apps`, `/dns_records`, `/cfd_tunnel/{id}/configurations`.
- Deployed artifact check: `sha256sum /opt/falcon/vpn-enroll/enroll-service.py` vs `git show <commit>:automation/vpn/enroll-service.py`.

## Findings

| ID | Severity | Title |
|---|---|---|
| ACM-P2-001 | P2 | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused |
| ACM-P2-003 | P2 | Deployed enrollment service does not enforce per-device token expiry; issuance tool and deployed enforcement disagree (no deployed-artifact binding) |
| ACM-P3-001 | P3 | No consolidated access-control matrix; authorization remains per-service and distributed across four documents |
| ACM-P3-002 | P3 | Documented Cloudflare Access policy state does not match live behavior: the falcon app has no owner-IP bypass (and two dead apps remain) |
