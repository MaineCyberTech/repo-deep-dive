# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (audited tree: `/tmp/opencode/falcon-audit-f5cb7c9`; live deployment tree `/home/user/falcon-build` is clean and at the same commit)
- Generated at: 2026-10-11T04:35:00Z
- Auditor: subagent (domain 06)
- Area code: SEC
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/06_security_authz_tenancy_audit.md`
- Scope limitations: vendor container internals were reviewed only through their declared/live configuration; no load or brute-force testing was performed against live logins; Cloudflare state was read read-only via the zone API (Access apps, DNS, tunnel configurations) — no writes. The lab preflight script (`tools/lab-vpn/lab-audit-preflight.sh --mode lab --no-pack`) returned `RESULT: FAIL` from this vantage (no scoped endpoint key/local overlay) because this agent runs ON the live lab host itself; all live checks below are local read-only host inspections.

## Scope

Reviewed: auth provider, session tokens/cookies, JWT validation, CSRF/CORS, rate limits, security headers, input/output validation, file handling, API permissions, admin permissions, tenant isolation, RLS, public/internal routes, webhooks, API keys, secrets, reset/invite/account lifecycle, audit/security logging, dependency risk (reference), IDOR, SSRF, mass assignment, sensitive logs.

Not reviewed: the edge-sensor repository, vendor application internals beyond declared configuration, and any non-lab production system. The wire-level behavior of Cloudflare Access beyond what the zone API reports was not exercised (no Access app mutation test).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/traefik/dynamic.yml` | runtime config | routers, middlewares, origin auth, rate limits | `ntfy-auth` (26-28) defined/unused; `falcon-basic-auth` only on `falcon-ntop` (94-100); public ntfy router removed (83-86) |
| `config/traefik/traefik.yml` | runtime config | entrypoints, access log | API dashboard disabled (17-18); JSON access log without field config |
| `config/nftables/falcon.nft` | host firewall | wg0 trust set after SEC-P1-001 fix | per-port wg0 allows (30-33); SSH source-scoped (35-37) |
| `automation/vpn/enroll-service.py` | service code | public enrollment authn/authz, token parsing, rate limit | repo version supports `<name>:<token>:<expiry>` and 403 on expired (60-113) |
| `automation/vpn/issue-enroll-token.sh` | tooling | per-device token issuance with TTL | writes `<name>:<token>:<expiry>` (44), TTL default 86400 (26) |
| `automation/vpn/enroll-service-install.sh` | deployment | how the live service is installed | copies repo file to `/opt/falcon/vpn-enroll/` (15,21); manual step, not wired into bootstrap |
| `automation/vpn/test_enroll_service.sh` | test | expiry/authorization coverage | expiry tests (122-127) run the repo file, not the deployed copy |
| `docs/security/ENROLL_API.md`, `docs/security/ENROLLMENT_CLOSURE.md` | docs | enrollment contract + lifecycle | contract documents expiry (30-43); closure doc documents the 2026-10-01 deploy |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md` | doc | surfaces, custody, Access §6 | §6 Access apps/policies; stale for the falcon app (see ACM report) |
| `compose/central/docker-compose.yml` | deployment | Grafana/OSD/ntfy hardening, secrets mounts | Grafana signup/anonymous off (202-203); ntfy (244-259) |
| `automation/alerting/ntfy_relay.py` | service code | webhook auth, rate limit, spool, fail-closed | constant-time path token, per-source limit, no token logging |
| `bootstrap/60-central-deploy.sh` | deployment | OpenSearch identities + REST audit | least-privilege roles (131-155); `enable_rest: true` (216-227) |
| `automation/wazuh/multi-node/config/wazuh_indexer/*.yml` | deployment | Wazuh audit | `plugins.security.audit.type: internal_opensearch` (48) |
| `.github/workflows/external-smoke.yml` | CI | public-surface posture gate | any 302 accepted (33-46); lab runner (26) |
| Live host (read-only) | live state | actual enforcement | `nft`, `ss`, `docker`, `wg`, HTTP probes, Grafana API, ntfy user list, token-file structure, OpenSearch security API, Cloudflare zone API |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sha256sum /etc/nftables.conf` vs repo `config/nftables/falcon.nft` | reproduction | SEC-P1-001 close-out | byte-identical: `f6b18722…`; live `nft list chain inet falcon_filter input` shows the per-port wg0 set, no blanket accept |
| `docker exec falcon-central-traefik-1 cat /etc/traefik/{dynamic,traefik}.yml` vs repo | reproduction | config binding | byte-identical (`b9c50f46…`, `3c791165…`) |
| `curl --resolve <host>:443:127.0.0.1` origin probes | reproduction | origin authentication | `/`→302 `/login`; `/dash/`→302 `/dash/app/login`; `/ntop`→401 basic auth; iris→302 `/dashboard`; soc→302 `/app/login` |
| Public probes from host egress 142.105.190.25 (Cloudflare trace-verified) | reproduction | edge posture | falcon→302 `cloudflareaccess.com`; iris→302 origin; soc→302 origin; enroll `/`→404 |
| Cloudflare zone API (read-only): `/access/apps`, `/access/apps/{id}/policies`, `/dns_records`, `/cfd_tunnel/{id}/configurations` | verification | Access/edge ground truth | falcon app has **no** bypass policy (2× allow-domain); soc/iris carry `bypass-owner-public-ip` 142.105.190.25/32; tunnel v13 ingress = falcon/iris/enroll |
| `sha256sum` of live `/opt/falcon/vpn-enroll/enroll-service.py` vs repo and vs git history | reproduction | deployment binding | live = commit `70739c3` (2026-10-02), repo = `c04c006` (2026-10-03, +40/−13); mtime of live copy 2026-10-02 00:42:19Z |
| `curl /health` + bad-token POST on 127.0.0.1:8791 | verification | live service behavior | `/health` → `falcon-vpn-enroll/1.1`; invalid token → HTTP 403 `invalid token` (non-mutating probe) |
| `awk` structure check of `/srv/falcon/secrets/vpn_enroll.token` (values never read) | verification | token lifecycle | 1 line, fields=1 (bare shared token), 0600 root |
| Grafana `/api/users`, `/api/serviceaccounts/search`, `/api/auth/keys` | verification | admin identities | exactly one `admin`; 0 service accounts; 0 API keys |
| OpenSearch security API (via `docker exec`, admin creds from secret store) | verification | API permissions | 5 internal users (`admin`, `falcon-dashboard`, `falcon-vector-writer`, `falcon-healthcheck`, `falcon-backup`); `falcon_writer` create/write/read `falcon-*`; `falcon_reader` read `falcon-*`; demo users removed |
| Live container configs: central OSD, Wazuh dashboard, Wazuh indexer, ntfy `server.yml` | reproduction | session/cookie/audit config | OSD `cookie.secure: false` (line 233); Wazuh dashboard TTL 900000 ms (14-16); ntfy/OSD/indexer files match repo |
| `ntfy user list` | verification | notification authz | anonymous denied; monadmin admin; relay write-only `falcon-alerts`; owner rw; watcher ro |
| Live response headers (`/`, `/ntop`) | verification | security headers | HSTS 31536000 includeSubDomains, nosniff, frame DENY, referrer-policy, XSS; no CSP |
| GitHub Actions API + latest external-smoke log | verification | posture-gate claim | run 38067043888 (2026-10-10) green on `lab-runner-2`; log `OK … (owner-IP Access bypass; origin reachable)` for iris/soc |
| Wazuh agent `ossec.conf` localfiles; Traefik access-log field sample | verification | audit/log hygiene | no container-log source; access log has `ClientUsername` but only `"-"` (no authenticated user) |
| `wg show wg0` + `/etc/wireguard/wg0.conf` comments | verification | peer classes on the tunnel | 8 peers; 3 `client peer:` devices (samsung, desktop-mi54lft, desktop-h3addu8) alongside site/sensor peers |

## Executive Summary

The falcon security model is unchanged in shape: default-deny host firewall, Cloudflare Tunnel + Access at the edge for the public hostnames, per-service logins at the origin, native ntfy auth, token-gated VPN enrollment, and least-privilege OpenSearch identities. Two previously open findings persist, one prior P1 is now verified fixed live, and this run adds three findings — the most important being that the **deployed public enrollment service is a stale build** that does not implement the repository's per-device token expiry.

1. **SEC-P2-001 (still open)** — public routers have no origin authentication; `ntfy-auth` remains dead config. Live origin probes reproduce 302 login pages for Grafana/OSD/IRIS/Wazuh and 401 for `/ntop`; no `Cf-Access-Jwt-Assertion` handling exists anywhere in the tree. The lab ntfy public router was removed (internal-only), so the dead-config surface is smaller but the middleware is still defined and unused.
2. **SEC-P2-002 (still open)** — the only origin rate limit keys on the client-influenced `X-Forwarded-For` header; the enrollment service's own 60/60 s limiter collapses to one fleet-wide bucket behind Traefik (`172.17.0.1`). Grafana's built-in brute-force protection is enabled by default, but OSD/Wazuh/IRIS have no per-account lockout and no login-path-specific limit exists.
3. **SEC-P2-004 (new)** — `/opt/falcon/vpn-enroll/enroll-service.py` is the 2026-10-02 build (`70739c3`), not the repo build (`c04c006`, which added per-device token expiry). The live service does not enforce expiry, and the documented issuance flow (`issue-enroll-token.sh` writes `<name>:<token>:<expiry>`) is rejected by the live parser — the ACM-P2-001 remediation path cannot be executed as written. The `/health` version string was not bumped (`falcon-vpn-enroll/1.1` on both builds), so the drift is invisible to health checks.
4. **SEC-P3-004 (new)** — the narrowed wg0 set still admits every tunnel peer (including the 3 client-VPN endpoint devices) to the edge control plane on 9443 (mTLS only), the Wazuh tunnel proxies 15140/15141 and the syslog ports; the N-24 addendum's claim that the residual "is resolved at the config level" overstates the result.
5. **SEC-P3-005 (new)** — console session cookies are not marked `Secure`: the live central OSD config sets `opensearch_security.cookie.secure: false`, and Grafana/Wazuh-dashboard carry no override (default false). The central OSD configuration is not represented in the repository at all.

Verified fixed: **SEC-P1-001** (WireGuard blanket accept) — `/etc/nftables.conf` is byte-identical to `config/nftables/falcon.nft`, the live input chain carries only the per-port wg0 set, and peers are handshaking (6 of 8 recent). See Prior-Run Comparison.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Auth provider | Cloudflare Access (edge) + per-service logins | user auth | Access apps for falcon/iris/soc (+2 dead apps); no IdP | Medium | API-verified; falcon app now enforces for the owner IP |
| Sessions/cookies | app defaults; Wazuh OSD 15 min; Access 24 h | session management | no central policy; cookies not Secure | Medium | SEC-P3-005 |
| JWT validation | none at origin | Access assertion | absent | Medium | `Cf-Access-Jwt-Assertion` never referenced |
| CSRF/CORS | app defaults; Traefik headers | request integrity | not configured in repo | Unknown | vendor defaults |
| Rate limits | `public-rate-limit` (XFF), enroll 60/60 s, relay 120/60 s, ntfy visitor limits | abuse control | header-keyed; fleet-wide enroll bucket | Medium | SEC-P2-002 |
| Security headers | `sec-headers` on every router | browser hardening | HSTS/nosniff/frame/referrer/XSS live | Low | no CSP/permissions-policy |
| Input validation | enroll service, relay, vector schema | boundary validation | implemented (regex, base64 32-byte key, JSON) | Low | negative tests exist offline |
| File handling | wg0.conf locked RMW; 0600 | file writes | implemented | Low | `fcntl.flock` (repo) |
| API permissions | OpenSearch roles; Wazuh API; enrollment tokens | API authz | least-privilege, live-verified | Low | 5 users, no demo users |
| Admin permissions | single admin per console | admin authz | no separation; OD-04 pending | Medium | see ADMIN report |
| Tenant isolation | none | tenancy | N/A single-tenant | N/A | see MT report |
| RLS | none (OpenSearch roles instead) | row security | N/A | N/A | no SQL app datastore |
| Public routes | 6 live hostnames | edge exposure | Access (falcon/iris/soc) / app auth | High | SEC-P2-001 |
| Webhooks | Grafana→relay→ntfy | alert delivery | path token, fail-closed, rate-limited | Low | replay residual documented |
| API keys | enrollment token; relay token; service pw files | machine auth | mixed | Medium | live token bare shared |
| Secrets | `/srv/falcon/secrets/**` 0700/0600 root | secret custody | strong | Low | no repo values; htpasswd 0640 |
| Account lifecycle | rotate/revoke runbooks | lifecycle | partial | Medium | no password policy (documented gap) |
| Audit logging | auditd + OpenSearch REST + Wazuh + Traefik | audit | partial | Medium | no console-actor audit (ADMIN report) |
| Sensitive logs | relay/enroll redaction | log hygiene | good | Low | tokens never logged |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 3 | Access apps (API-verified); per-service logins | no IdP; owner bypass on iris/soc | owner decision R-15 |
| Session tokens/cookies | 2 | Wazuh OSD 15 min; Access 24 h | cookies not Secure; no central policy | SEC-P3-005 |
| JWT validation | 1 | none at origin | origin cannot verify Access | validate `Cf-Access-Jwt-Assertion` or add origin auth |
| CSRF/CORS | 2 | app defaults | not configured/verifiable from repo | document per-app posture |
| Rate limits | 2 | XFF-keyed Traefik limit; enroll/relay/ntfy limits | spoofable key; no login-path limit; fleet-wide enroll bucket | SEC-P2-002 |
| Security headers | 3 | live headers verified | no CSP | add CSP where compatible |
| Input/output validation | 3 | enroll/relay validation; offline suite | deployed enroll build differs | SEC-P2-004 |
| File handling | 3 | locked wg0.conf RMW; 0600 | — | — |
| API permissions | 4 | OpenSearch least-privilege live-verified | writer role broader than Phase-0 doc (annotated) | keep; reconcile doc |
| Admin permissions | 2 | single admin/service; break-glass custody PENDING | no separation; shared super-admin | OD-04; per-service accounts |
| Tenant/org/workspace isolation | N/A | single-tenant (grep + docs) | n/a | see MT report |
| RLS policies | N/A | no RLS datastore | n/a | — |

## Detailed Review

### Item: Public/internal routes and origin authentication

- Evidence: `config/traefik/dynamic.yml` routers 51-132; live origin probes 2026-10-11T04:26Z; Cloudflare Access apps (API read).
- What it does: routes the public hostnames (falcon, iris, soc, enroll) to Grafana, OSD, ntopng, IRIS, the Wazuh dashboard and the enrollment service.
- How it appears to work: Cloudflare Access decides at the edge for falcon/iris/soc; the origin always accepts and relies on the application login (or the enrollment token). `falcon-basic-auth` protects only `/ntop`.
- Current controls: Access (falcon/iris/soc; session 24 h), app logins, host firewall (origin web only from mgmt/admin subnets + tunnel loopback), `public-rate-limit`.
- Missing controls: origin-side auth or Access-JWT validation; the unused `ntfy-auth` middleware (26-28).
- Risks: edge-only enforcement; an Access misconfiguration or bypass (the owner-NAT bypass is active for iris/soc, API-verified) reduces protection to the application login.
- Recommended improvement: validate `Cf-Access-Jwt-Assertion` at Traefik (forward-auth) or add origin auth; delete or wire `ntfy-auth`.
- Suggested tests: staging Access-app removal test asserting origin denial; assert the origin returns 401/403 for requests without an Access JWT.
- Suggested docs: record the accepted residual against R-15 with the current Access policy set.

### Item: WireGuard tunnel authorization boundary (SEC-P1-001 close-out + residual)

- Evidence: `config/nftables/falcon.nft:30-33`; live `/etc/nftables.conf` (sha `f6b18722…`); live `nft list chain`; `wg show wg0`; `wg0.conf` peer comments.
- What it does: governs what WireGuard peers may reach on the host.
- Current controls: per-port set — tcp 9443, tcp 15140/15141, tcp 514/1514/1515, udp 514/2055; SSH is source-scoped; the blanket rule is gone.
- Missing controls: no peer-class separation — the 3 enrolled client-VPN endpoints share wg0 and the same allowlist; the CP's only gate is mTLS.
- Risks: a compromised endpoint can reach the CP API surface and the Wazuh tunnel proxies (authenticated), not the consoles/SSH.
- Recommended improvement: give client endpoints a separate address range (e.g. 10.98.0.0/24) or interface and exclude it from the 9443 rule; correct the N-24 addendum wording.
- Suggested tests: negative probe from a client peer to 9443/15140 (expect DROP after separation) — read-only today shows ACCEPT path exists.
- Suggested docs: `PORT_PROTOCOL_MATRIX.md` N-24 addendum (residual statement).

### Item: Rate limiting and auth abuse controls

- Evidence: `dynamic.yml:36-41`; `enroll-service.py:116-121`; service mapping `vpn-enroll → http://172.17.0.1:8791` (149-152); `ENROLL_API.md` (rate-limit section); live Grafana default (`disable_brute_force_login_protection` commented false).
- What it does: caps public request rates and application bursts.
- Current controls: Traefik 50/s + 100 burst per raw `X-Forwarded-For` value; enroll 60/60 s per socket source (one bucket behind Traefik); relay 120/60 s; ntfy visitor limits with internal exemptions; Grafana built-in brute-force protection (enabled by default).
- Missing controls: trusted client-IP extraction; login-path-specific limit; per-account lockouts on OSD/Wazuh/IRIS.
- Risks: rotating the XFF prefix changes the bucket; credential stuffing on OSD/Wazuh/IRIS is bounded only by the header-keyed limit.
- Recommended improvement: key on `CF-Connecting-IP` (Cloudflare-controlled) or a cloudflared-injected header; add a stricter limit on login paths; document Grafana's built-in protection.
- Suggested tests: 200 requests with unique XFF prefixes and assert 429s still occur.

### Item: Enrollment credential lifecycle and deployed service (new)

- Evidence: live `/opt/falcon/vpn-enroll/enroll-service.py` sha `ed7d02ab…` = commit `70739c3`; repo sha `cdd4c671…` = `c04c006`; `issue-enroll-token.sh:44`; `test_enroll_service.sh:122-127`; `ENROLL_API.md:36-43`; `ENROLLMENT_CLOSURE.md:27-37`; token file structure (1 bare line).
- What it does: gates client-VPN enrollment by token; the repo version additionally supports per-device expiry.
- Current controls: constant-time token compare, per-device binding override, name regex, 32-byte key check, locked wg0.conf write, rate limit, 403 on invalid token (live-verified).
- Missing controls (live): expiry parsing/enforcement; any check that the deployed copy matches the repo; the version string does not distinguish builds.
- Risks: a claimed control (24 h per-device expiry, fail-closed) is not deployed; the documented remediation for the shared token fails closed and would be discovered only at issuance time.
- Recommended improvement: re-run `automation/vpn/enroll-service-install.sh` after pulls (or wire it into bootstrap/60), bump the version string, add a deployed-vs-repo hash assertion to a validation script.
- Suggested tests: run `automation/vpn/test_enroll_service.sh` against the deployed file (it would fail today); add a health-check field carrying the source commit.
- Suggested docs: `ENROLLMENT_CLOSURE.md` deploy note (which build is live), `ENROLL_API.md` residual wording.

### Item: Sessions, cookies, and security headers

- Evidence: live central OSD `opensearch_dashboards.yml:229-233` (`cookie.secure: false`, multitenancy enabled); Wazuh dashboard `opensearch_dashboards.yml:6,14-16` (multitenancy false; cookie/session TTL 900000 ms); Grafana container env (no `GF_SECURITY_COOKIE_SECURE`; `disable_brute_force_login_protection` default); live response headers.
- Current controls: Access session 24 h; Wazuh 15-min TTL; Grafana signup/anonymous off; HSTS etc. on all routers.
- Missing controls: Secure cookie attribute on the consoles; central OSD config not in the repo; CSP absent.
- Risks: defense-in-depth loss if an HTTP path to the origin exists (HTTP entrypoint redirects, but the cookie policy is not enforced).
- Recommended improvement: set `opensearch_security.cookie.secure: true` for central OSD and the Wazuh dashboard; set `GF_SECURITY_COOKIE_SECURE=true`; codify central OSD config in the repo.
- Suggested tests: assert `Set-Cookie` carries `Secure` on each console login in a lab test.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEC-001 | Auth provider | Access apps (API) | Access + app logins | no IdP; bypass on iris/soc | P2 | owner decision R-15 |
| SEC-002 | Sessions/cookies | OSD/Grafana configs | TTLs on Wazuh; Access 24 h | cookies not Secure; no central policy | P3 | SEC-P3-005 |
| SEC-003 | JWT validation | no refs | none | origin cannot verify Access | P2 | forward-auth/JWT |
| SEC-004 | CSRF/CORS | app defaults | vendor built-ins | unverifiable from repo | P3 | document |
| SEC-005 | Rate limits | dynamic.yml:36-41 | XFF-keyed + app limits | spoofable key; no login limit | P2 | SEC-P2-002 |
| SEC-006 | Security headers | live headers | HSTS etc. | no CSP | P3 | add CSP |
| SEC-007 | Input validation | enroll/relay | strict validation | deployed build differs | P2 | SEC-P2-004 |
| SEC-008 | File handling | enroll lock | safe RMW | — | — | — |
| SEC-009 | API permissions | live security API | least-privilege | — | — | — |
| SEC-010 | Admin permissions | ACCESS §1 | single admin/service | no separation | P2 | OD-04 + per-op accounts |
| SEC-011 | Tenant isolation | see MT | N/A | — | — | — |
| SEC-012 | RLS | N/A | OpenSearch roles | — | — | — |
| SEC-013 | Public routes origin auth | dynamic.yml; live | Access edge only | no origin auth | P2 | SEC-P2-001 fix |
| SEC-014 | WG tunnel authz | nft sha match (live) | per-port set live | peer-class residual | P3 | SEC-P3-004 |
| SEC-015 | Enrollment token lifecycle | live token file; live service | shared token; no expiry live | issuance/expiry drift | P2 | SEC-P2-004 / ACM-P2-001 |
| SEC-016 | Access policy doc vs live | API read | Access apps verified | doc stale (falcon bypass) | P3 | ACM report |

## Findings

### SEC-P2-001 - Public-facing routers have no origin authentication; `ntfy-auth` is dead config

- Severity: P2
- Confidence: High (config + live origin probes reproduced at the current commit)
- Area: SEC
- Evidence:
  - `config/traefik/dynamic.yml` (routers 87-132; `ntfy-auth` 26-28; `falcon-basic-auth` only on `falcon-ntop` 94-100; ntfy public router removed 83-86)
  - Live origin probes 2026-10-11T04:26Z via loopback: `/`→302 `/login`, `/dash/`→302 `/dash/app/login`, `/ntop`→401 (`WWW-Authenticate: Basic realm="traefik"`), iris→302 `/dashboard`, soc→302 `/app/login`
  - `grep -rn 'Cf-Access-Jwt-Assertion'` → no matches anywhere in the tree
  - Cloudflare zone API: Access apps for falcon (`a8bb98c6…`), soc (`adfd5945…`), iris (`88aec22b…`), session 24 h; the origin cannot tell an Access-authenticated request from a bypassed one
  - `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §5-§6; `ledgers/risk_register.md` R-15 (OPEN)
- What is happening: Every public hostname reaches the origin without origin-side authentication except `/ntop`; Grafana/OSD/IRIS/Wazuh rely on their own login pages and the edge Access app. `ntfy-auth` is defined but referenced by no router.
- Why it matters: A Cloudflare Access mistake/removal, or an actor behind the owner-NAT bypass (active for iris/soc), reduces protection to the application login. The origin fails open relative to the edge.
- User / business impact: Reduced defense-in-depth for the SOC/monitoring consoles.
- Security / privacy / reliability impact: Edge-only enforcement of admin surfaces.
- Recommended fix: Validate the Access JWT at Traefik (forward-auth/plugin) or add an origin auth layer for the console routers; wire or delete `ntfy-auth`; otherwise record the accepted residual against R-15 with the current Access policy set.
- Suggested validation: staging Access-app removal test asserting origin denial; assert a request without `Cf-Access-Jwt-Assertion` is rejected.
- Owner suggestion: @owner
- Effort estimate: M
- Dependencies: Cloudflare config for Access/JWT or service tokens
- Status: still-open (prior ID SEC-P2-001; ntfy public route removed since the prior run, core issue unchanged)
- Endpoint / data path: `https://falcon.mainecybertech.us/` → cloudflared → Traefik `falcon-grafana` → grafana:3000
- Attack path: public host → Access bypass/misconfig → origin app login (brute force) → console

### SEC-P2-002 - Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints

- Severity: P2
- Confidence: Medium (config semantics reproduced; bypass not load-tested)
- Area: SEC
- Evidence:
  - `config/traefik/dynamic.yml:36-41` (`sourceCriterion.requestHeaderName: X-Forwarded-For`)
  - `config/traefik/dynamic.yml:149-152` (`vpn-enroll` service → `http://172.17.0.1:8791`), so all web enrollments share one socket source and one 60/60 s bucket (`automation/vpn/enroll-service.py:116-121`)
  - `docs/security/ENROLL_API.md` documents the XFF keying and the fleet-wide enrollment bucket
  - Live Grafana config: `disable_brute_force_login_protection` left at the default (protection enabled); OSD/Wazuh/IRIS have no per-account lockout and no login-path-specific Traefik limit
- What is happening: The only origin rate limit for the public/auth surfaces is keyed on a client-influenced header; rotating the prefix changes the bucket. Enrollment's own limit is a fleet-wide circuit breaker behind Traefik.
- Why it matters: Per-IP rotation via header manipulation defeats the intended credential-stuffing/flood bound on the console logins.
- User / business impact: Weaker brute-force resistance on internet-reachable logins.
- Security / privacy / reliability impact: Abuse-control gap, medium.
- Recommended fix: Key the limit on `CF-Connecting-IP` (overwritten by Cloudflare) or a cloudflared-injected header; add a stricter limit on login paths; document Grafana's built-in protection and add controls for OSD/Wazuh/IRIS where possible.
- Suggested validation: send 200 requests with unique XFF prefixes and assert 429s still occur; per-account lockout test on OSD.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none (Traefik config change + restart)
- Status: still-open (prior ID SEC-P2-002)
- Endpoint / data path: internet → Cloudflare → cloudflared → Traefik rateLimit middleware → service
- Attack path: credential stuffing with XFF rotation against `/login` paths

### SEC-P2-004 - Deployed enrollment service is a stale build: per-device token expiry is not enforced and the documented issuance flow is rejected

- Severity: P2
- Confidence: High (live file hash vs git history + code diff + live health/behavior probes)
- Area: SEC
- Evidence:
  - Live `/opt/falcon/vpn-enroll/enroll-service.py` sha256 `ed7d02abe98aa33f765ff65bc1b9e56f715d567de2d250c168f76dd97717045e` = commit `70739c3` (2026-10-02 00:42:30Z); installed mtime 2026-10-02 00:42:19Z
  - Repo `automation/vpn/enroll-service.py` sha256 `cdd4c671d537fe661ac74428bd8ed42e030a43c610ae6afcd2f7115e33f9fb3c` = commit `c04c006` (2026-10-03, +40/−13 lines: expiry support + contract)
  - `automation/vpn/issue-enroll-token.sh:44` writes `printf '%s:%s:%s\n' "$NAME" "$token" "$expiry"`; the live parser does `name, _, token = line.partition(":")`, so the live service compares the submitted token against `"<token>:<expiry>"` and returns 403 `invalid token` — the per-device path fails closed
  - `automation/vpn/enroll-service-install.sh:15,21` (copies to `/opt/falcon/vpn-enroll/`) is a manual step, not wired into `bootstrap/60-central-deploy.sh`; no validation script hashes the deployed copy
  - Live `/health` reports `falcon-vpn-enroll/1.1`; the repo file also reports `1.1` (version string unchanged across the behavior change)
  - `automation/vpn/test_enroll_service.sh:122-127` exercises expiry against the repo file only; against the deployed file, `future-expiry`/legacy expectations would not hold
- What is happening: The public token-gated enrollment endpoint runs an older build than the repository. Expiry enforcement (API-P2-001) is absent live, and issuing a per-device token with the documented script produces a token the live service rejects. The drift is invisible to `/health` and to any existing check.
- Why it matters: A declared security control is not deployed (delivery vs configuration), and the documented remediation path for the shared token (ACM-P2-001) cannot be executed as written.
- User / business impact: Onboarding a device with a per-device token fails (403); the operator must fall back to the shared token or manually reinstall the service.
- Security / privacy / reliability impact: Machine-credential lifecycle control not enforced at the deployed boundary.
- Recommended fix: Re-run `automation/vpn/enroll-service-install.sh` from the deployed tree, then add a deployed-vs-repo hash assertion to a validation script (e.g. `port_matrix_check.sh` or `central_health.sh`) and bump the version string when behavior changes.
- Suggested validation: run `automation/vpn/test_enroll_service.sh` against `/opt/falcon/vpn-enroll/enroll-service.py`; issue a test token with an expiry and confirm 200 within TTL and 403 after (lab only).
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none (manual reinstall + a check)
- Status: open (new)
- Endpoint / data path: `POST https://enroll.mainecybertech.us/enroll` → tunnel → Traefik `vpn-enroll` → 172.17.0.1:8791 → live (stale) service
- Attack path: none identified (fail-closed); the impact is a control/verification gap

### SEC-P3-004 - wg0 tunnel has no peer-class separation; every peer (including client endpoints) can reach the edge control plane and Wazuh proxies

- Severity: P3
- Confidence: High (live ruleset + wg0.conf peer inventory + nft sha match)
- Area: SEC
- Evidence:
  - `config/nftables/falcon.nft:30-33` (per-port wg0 set: tcp 9443, tcp 15140/15141, tcp 514/1514/1515, udp 514/2055) — live-identical (`f6b18722…`)
  - Live `/etc/wireguard/wg0.conf`: 8 peers including 3 `client peer:` endpoint devices (samsung, desktop-mi54lft, desktop-h3addu8) alongside site/sensor peers; `wg show wg0` shows all on 10.99.0.0/24
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md:89-126` N-24 addendum states the residual "is resolved at the config level by the per-port rules"
- What is happening: The blanket accept is fixed, but the per-port set applies to every peer on wg0 regardless of peer class; a client-VPN endpoint can reach the CP (mTLS is the only gate), the Wazuh tunnel proxies and the syslog ports.
- Why it matters: The residual defense-in-depth gap is smaller than before but not eliminated; the doc overstates the resolution.
- User / business impact: Low today (mTLS + token gates), but a compromised endpoint has more reach than its role requires.
- Security / privacy / reliability impact: Network-layer lateral reachability from lower-trust endpoints.
- Recommended fix: Put client endpoints on a separate address range/interface and scope the 9443 rule to the sensor range; update the N-24 addendum to state the remaining reachability honestly.
- Suggested validation: negative probe from a client peer to 9443/15140 after separation (expect DROP).
- Owner suggestion: @owner
- Effort estimate: M
- Dependencies: WG address plan change (device re-enrollment)
- Status: open (new; residual after the verified SEC-P1-001 fix)
- Endpoint / data path: wg0 peer → host input chain → 9443 / 15140/15141 / 514/1514/1515
- Attack path: compromised client endpoint → CP API (mTLS-gated) / Wazuh proxies

### SEC-P3-005 - Console session cookies are not marked Secure (central OSD explicit `cookie.secure: false`; Grafana/Wazuh default)

- Severity: P3
- Confidence: High for central OSD (live config read); Medium for Grafana/Wazuh (documented defaults, no override present)
- Area: SEC
- Evidence:
  - Live `falcon-central-opensearch-dashboards-1:/usr/share/opensearch-dashboards/config/opensearch_dashboards.yml:233` → `opensearch_security.cookie.secure: false` (active line); multitenancy enabled (229)
  - `automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml:14-16` sets cookie/session TTL but no `cookie.secure` (default false)
  - Grafana container env has no `GF_SECURITY_COOKIE_SECURE`; `grafana.ini` leaves `cookie_secure` at its default (false)
  - The central OSD configuration is not represented in the repository (no repo file for the central dashboards config)
- What is happening: Console session cookies are issued without the Secure attribute.
- Why it matters: Defense-in-depth loss if any HTTP path to the origin is reachable; the attribute is a standard hardening baseline.
- User / business impact: Low (public access is HTTPS-only through Cloudflare; the HTTP entrypoint redirects).
- Security / privacy / reliability impact: Session-hygiene gap.
- Recommended fix: set `opensearch_security.cookie.secure: true` (central OSD and Wazuh dashboard) and `GF_SECURITY_COOKIE_SECURE=true`; codify the central OSD config in the repo.
- Suggested validation: lab test asserting `Set-Cookie` contains `Secure` on each console login.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none
- Status: open (new)
- Endpoint / data path: browser → Traefik → console session cookie
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Edge-only auth for public consoles | Medium | Medium | High | dynamic.yml; live probes | origin auth / Access JWT validation |
| Rate-limit bypass via XFF rotation | Medium | Medium | Medium | dynamic.yml:36-41 | CF-Connecting-IP keying |
| Stale deployed enrollment service (no expiry enforcement) | Medium | High | Medium | live vs repo hash | reinstall + deployed-hash check |
| Shared enrollment token without expiry | Medium | Medium | Medium | live token file | per-device tokens + rotate |
| Client peers reach CP/Wazuh proxies | Low | Low | Medium | nft + wg0.conf | peer-class separation |
| Console cookies not Secure | Low | Low | Low | live OSD config | set Secure cookies |

## Recommendations

### Immediate / Release Blocking

- None (the prior live P1, SEC-P1-001, is verified fixed).

### This Week

- Reinstall the enrollment service from the deployed tree and add a deployed-vs-repo hash assertion (SEC-P2-004).
- Fix the rate-limit key to a Cloudflare-controlled header; add a login-path limit (SEC-P2-002).
- Decide and record: origin auth / Access-JWT validation for console routers, or accept R-15 explicitly with current evidence (SEC-P2-001).

### This Month

- Retire the shared enrollment token in favour of per-device tokens with expiry (owner action C6), now that the live service is updated.
- Set Secure cookies and codify the central OSD config (SEC-P3-005); add CSP where compatible.
- Correct the N-24 residual wording; plan peer-class separation for client endpoints (SEC-P3-004).

### Later / Platform Evolution

- IdP/SSO in front of all consoles (per-operator identities); production-grade break-glass custody (OD-04).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Re-run `enroll-service-install.sh` | deploys the expiry control | `automation/vpn/enroll-service-install.sh` | live sha == repo; `/health` version bump |
| Change rate-limit key to `CF-Connecting-IP` | removes header-rotation bypass | `config/traefik/dynamic.yml` | curl loop with rotated XFF |
| Delete or wire `ntfy-auth` | removes misleading dead config | `config/traefik/dynamic.yml` | grep references; router behavior |
| `opensearch_security.cookie.secure: true` | session hardening | central OSD config | login `Set-Cookie` check |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Origin auth / Access JWT validation | P2 | @owner | M | Cloudflare config |
| Per-device enrollment tokens only | P2 | @owner | S | device onboarding |
| Deployed-artifact hash checks for host-run services | P2 | @owner | S | validation scripts |
| WG peer-class separation | P3 | @owner | M | device re-enrollment |
| CSP/session policy documentation | P3 | @owner | S | — |

## Suggested Tests

- Security: run `automation/vpn/test_enroll_service.sh` against the deployed file (must pass after reinstall).
- Security: negative probe from a client WireGuard peer to 9443/15140 (expect DROP after peer-class separation).
- Security: XFF-rotation rate-limit test against each public hostname.
- Regression: assert `/etc/nftables.conf` and the deployed Traefik/ntfy/OSD/Wazuh configs hash-match the repo in a validation script.
- Integration: enrollment with an expired per-device token (expect 403) and with a future-expiry token (expect 200) against the live service.
- Manual: Access-app removal test in a staging zone to prove origin denial.

## Suggested Documentation Updates

- `docs/security/ENROLLMENT_CLOSURE.md`: record which build is deployed and how to redeploy it.
- `docs/security/ENROLL_API.md`: reconcile the "per-device tokens have no expiry field yet" residual with the expiry section.
- `docs/architecture/PORT_PROTOCOL_MATRIX.md`: correct the N-24 residual statement (peer classes).
- `docs/runbooks/ACCESS_AND_ACCOUNTS.md`: session/cookie posture per console.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why was the falcon Access bypass removed without a ledger entry? | docs/edge-model accuracy | owner/Cloudflare audit log |
| Are central OSD sessions intentionally left at plugin defaults? | session policy | owner decision |
| When will the shared enrollment token be rotated? | credential lifecycle | owner action C6 closure evidence |

## Prior-Run Comparison

| Prior finding (falcon-20261009-2117-full-08e20d1) | Status now | Notes |
|---|---|---|
| SEC-P1-001 (wg0 blanket accept live) | **verified-fixed** | live per-port wg0 set; `/etc/nftables.conf` sha `f6b18722…` == repo; peers handshaking (verified 2026-10-11) |
| SEC-P2-001 public routers no origin auth; ntfy-auth dead | still-open | config unchanged except the ntfy public router removal; re-verified live + Access apps read via API |
| SEC-P2-002 XFF rate-limit keying / no per-account limits | still-open | config unchanged; Grafana's built-in brute-force protection noted (enabled by default) |
| (none) | new SEC-P2-004 | deployed enrollment service stale (no expiry enforcement; issuance flow rejected) |
| (none) | new SEC-P3-004 | wg0 peer-class residual after the fix |
| (none) | new SEC-P3-005 | console cookies not Secure |

## Limitations

- No load/brute-force testing was performed; the XFF bypass remains Medium confidence (config semantics).
- Grafana cookie flags were inferred from defaults + absence of overrides (the effective flag was not exercised with a login).
- Vendor application internals (OSD/Wazuh/IRIS) were reviewed only through their configuration.
- The Cloudflare API was used read-only; no Access policy mutation test was performed.

## Appendix

- Live probe commands (read-only): `curl -skI --resolve falcon.mainecybertech.us:443:127.0.0.1 https://falcon.mainecybertech.us/`; `curl -4 -s -o /dev/null -w '%{http_code} %{redirect_url}' https://falcon.mainecybertech.us/`; `nft list chain inet falcon_filter input`; `sha256sum /etc/nftables.conf`; `docker exec falcon-central-traefik-1 cat /etc/traefik/dynamic.yml | sha256sum`; `docker exec falcon-central-opensearch-1 curl -sk -u admin:$PW https://localhost:9200/_plugins/_security/api/internalusers`; `curl -s http://127.0.0.1:8791/health`; `curl -X POST http://127.0.0.1:8791/enroll -d '{"token":"deadbeef",...}'` (non-mutating); Cloudflare zone API GETs.
- Egress IP at check time: 142.105.190.25 (Cloudflare trace), the documented owner bypass IP.
- Live enrollment sha256: `ed7d02ab…` (70739c3); repo sha256: `cdd4c671…` (c04c006).

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; ntfy-auth is dead config |
| SEC-P2-002 | P2 | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints |
| SEC-P2-004 | P2 | Deployed enrollment service is a stale build: per-device token expiry is not enforced and the documented issuance flow is rejected |
| SEC-P3-004 | P3 | wg0 tunnel has no peer-class separation; every peer (including client endpoints) can reach the edge control plane and Wazuh proxies |
| SEC-P3-005 | P3 | Console session cookies are not marked Secure (central OSD explicit cookie.secure: false; Grafana/Wazuh default) |
