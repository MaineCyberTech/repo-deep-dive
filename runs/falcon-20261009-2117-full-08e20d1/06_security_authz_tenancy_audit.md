# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65` (audited tree: `/tmp/opencode/falcon-audit-08e20d1`)
- Generated at: 2026-10-09T21:45:00Z
- Auditor: subagent (domain 06)
- Area code: SEC
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/06_security_authz_tenancy_audit.md`
- Scope limitations: repo + read-only live host checks on the lab host the repo deploys to. Cloudflare-side Access application state was not queried (no external/API vantage authorized); it is inferred from live HTTP behavior and repo docs. App-internal session/CSRF settings for Grafana/OSD/IRIS are not fully configurable from this repo (`Unknown` where noted).

## Scope

Reviewed: auth provider, session tokens/cookies, JWT validation, CSRF/CORS, rate limits, security headers, input/output validation, file handling, API permissions, admin permissions, tenant/org/workspace isolation, RLS, public/internal routes, webhooks, API keys, secrets, reset/invite/account lifecycle, audit/security logging, dependency risk, IDOR, SSRF, mass assignment, sensitive logs.

Not reviewed: the edge-sensor repository (separate repo), the Cloudflare account configuration via API, the internals of vendor containers beyond their declared configuration, and any production system other than the lab host.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/traefik/dynamic.yml` | runtime config | all public/internal routes, middlewares, auth, rate limits, headers | `ntfy-auth` defined (26-28) but referenced by no router; `falcon-basic-auth` only on `/ntop` |
| `config/traefik/traefik.yml` | runtime config | entrypoints, access log, no dashboard API | access log JSON, no header capture |
| `config/ntfy/server.yml` | runtime config | ntfy native auth, rate limits | `auth-default-access: deny-all`, `behind-proxy: true` |
| `compose/central/docker-compose.yml` | deployment | service hardening, ports, secrets mounts | traefik 80/443; Grafana anonymous off, sign-up off |
| `compose/probe/docker-compose.yml`, `compose/mct/iris-web/*` | deployment | edge/IRIS containers | IRIS extends official base image |
| `bootstrap/31-docker-user-firewall.sh`, `config/nftables/falcon.nft`, `bootstrap/32-inbound-mode.sh` | host firewall | forwarded-port policy + live mode | live state file `closed` |
| `automation/vpn/enroll-service.py`, `enroll-service-install.sh`, `issue-enroll-token.sh` | service code | public enrollment authz, rate limit, key validation | per-device token support; live token file is a single shared token |
| `automation/alerting/ntfy_relay.py` | service code | webhook auth, rate limit, fail-closed, spool | path token, constant-time compare, 120/60s per source |
| `bootstrap/60-central-deploy.sh`, `61-search-policies.sh` | deployment | OpenSearch identities, roles, REST audit, retention | least-privilege roles; demo users removed; `enable_rest: true` |
| `automation/wazuh/multi-node/config/**` | deployment | Wazuh indexer security audit, dashboard sessions | `plugins.security.audit.type: internal_opensearch`; OSD session TTL 15 min |
| `bootstrap/10-host-auditd.sh`, `bootstrap/10-host-baseline.sh`, `bootstrap/60-host-auditd.sh` | host baseline | SSH policy, auditd watches | password auth retained (EX-01), MaxAuthTries 4 |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md`, `docs/architecture/IDENTITY_AND_SECRETS.md`, `docs/architecture/TRUST_BOUNDARIES.md`, `docs/architecture/PORT_PROTOCOL_MATRIX.md` | docs | identity model, trust boundaries, route matrix | ACCESS §6 records the Cloudflare Access apps + owner-IP bypass |
| `ledgers/decision_log.md`, `ledgers/risk_register.md` | ledgers | owner decisions, accepted risks | R-15 open; owner-IP bypass caveat recorded 2026-09-21 |
| `.gitleaks.toml`, `ci/validate.py`, `.env.example` | CI/secret controls | secret scanning, credential sourcing rules | scans tree + history; `check_credential_sourcing` |
| Live host (read-only) | live state | drift vs repo, actual exposure | `nft`, `iptables`, `ss`, `docker ps`, `systemctl`, HTTP probes, Grafana/ntfy user enumeration |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `diff /etc/nftables.conf config/nftables/falcon.nft` (live) | reproduction | verify the SEC-P1-002 wg0 fix is applied | **UNSUPPORTED live**: live file still has the blanket `iifname "wg0" accept`; repo has per-port rules |
| `nft list chain inet falcon_filter input` (live) | reproduction | effective host input policy | matches the old file, not the repo |
| `iptables -S DOCKER-USER` (live) | reproduction | forwarded-port allowlist | matches `bootstrap/31` (allowlist + final DROP) |
| `curl` origin via loopback (`--resolve ...:443:127.0.0.1`) | reproduction | origin auth behavior | `/`→302 Grafana login, `/dash/`→302 OSD login, `/ntop`→401 basic auth; no origin auth on grafana/dash |
| `curl` public hosts (IPv4, egress 142.105.190.25) | reproduction | Cloudflare Access posture | falcon → 302 `cloudflareaccess.com`; iris → 302 origin `/dashboard`; soc → 302 origin `/app/login` |
| `docker ps` (live) | drift check | running estate vs compose | matches declared central/probe/mct services; 8 WG peers live |
| `wg show wg0` (live) | reproduction | authenticated lower-trust peers | 8 peers with recent handshakes |
| Grafana API (read-only) | verification | admin accounts/sessions | exactly one user `admin`; no external auth |
| `ntfy user list` (read-only) | verification | topic ACLs | anonymous denied; relay write-only; owner rw; watcher ro |
| Enrollment token file structure (read-only) | verification | key lifecycle | one bare shared token line (no name binding, no expiry) |
| Host Wazuh agent localfiles (read-only) | verification | audit coverage | journald/audit.log/dpkg + commands; no container-log source |
| Traefik access log sample (read-only) | verification | actor attribution | fields include ClientAddr/host/path/status; no authenticated user |

## Executive Summary

The falcon stack is a single-operator lab whose security model is: default-deny host firewall, Cloudflare Tunnel + Cloudflare Access at the edge for the public hostnames, per-service application logins at the origin, native auth for ntfy, token-gated VPN enrollment, and least-privilege OpenSearch identities. Within that model the controls are unusually well documented and largely evidence-backed (trust boundaries, port matrix, identity model, decision/risk ledgers, secret custody, CI secret scanning).

Three current weaknesses matter:

1. **The origin has no authentication of its own.** Public routers terminate at application logins only; the only barrier is Cloudflare Access at the edge (with an owner-IP bypass policy). The `ntfy-auth` Traefik middleware remains dead config. Any Access misconfiguration/removal, or any actor behind the bypassed owner NAT, reaches Grafana/OSD/ntop/IRIS/Wazuh consoles directly (still behind app logins). The host firewall limits origin reachability to the mgmt/admin subnets + loopback, which is the compensating control.
2. **The SEC-P1-002 WireGuard narrowing is committed but NOT applied on the live host.** `/etc/nftables.conf` still contains the blanket `iifname "wg0" accept`, so every WireGuard peer (including lower-trust enrolled endpoints) can reach every host listener — the edge control plane on 9443, the enrollment service on 8791, Traefik 80/443, the Wazuh manager 1515, and SSH (the blanket rule precedes the SSH source rules). This is the most serious current finding.
3. **Rate limiting of the public/auth surfaces keys on the client-influenced `X-Forwarded-For` header**, and there are no per-account/per-email limits; the enrollment service's own limit collapses to a fleet-wide bucket behind Traefik. Combined with the credential-stuffing surface of five logins, this is a medium-term hardening gap.

Strengths: firewall/forward policy is default-deny and reconciled; secrets live root-only 0600 outside the repo; OpenSearch roles are least-privilege with REST audit logging; the enrollment service and alert relay are fail-closed, constant-time, rate-limited, and input-validated; SSH has MaxAuthTries 4 + fail2ban + new-connection rate limit; auditd watches identity/privilege/firewall/secret metadata changes; the repo has gitleaks + history scan + credential-sourcing checks in CI.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Auth provider | Cloudflare Access (edge) + per-service local logins | user auth | no SSO/IdP; email-domain OTP + owner-IP bypass | Medium | `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §6 |
| Sessions | app defaults; Access session 24h; Wazuh OSD 15 min | session management | no central policy | Medium | `wazuh_dashboard/opensearch_dashboards.yml` |
| JWT validation | none at origin | Access JWT not verified | absent | Medium | no `Cf-Access-Jwt-Assertion` handling anywhere |
| CSRF/CORS | app defaults; Traefik headers | request integrity | not configured in repo | Unknown | Grafana/OSD/IRIS built-ins assumed |
| Rate limits | `public-rate-limit`, ntfy visitor limits, relay/enroll app limits | abuse control | keyed on XFF / per source | Medium | `dynamic.yml:36-41` |
| Security headers | `sec-headers` on every router | browser hardening | HSTS/nosniff/frame/referrer/XSS | Low | no CSP/permissions-policy |
| Input validation | enrollment service, relay, vector schema | boundary validation | implemented | Low | 32-byte key check, name regex |
| File handling | no uploads; wg0.conf RMW under lock | file writes | implemented | Low | `enroll-service.py:224-246` |
| API permissions | OpenSearch roles; Wazuh API; enrollment tokens | API authz | least-privilege | Low | `falcon_writer`/`falcon_reader`/`falcon_backup` |
| Admin permissions | single admin per console | admin authz | no separation | Medium | documented gap §5.1 |
| Tenant isolation | none | tenancy | N/A single-tenant | N/A | see MT report |
| RLS | none (OpenSearch roles instead) | row security | N/A | N/A | no SQL app datastore exposed |
| Public routes | 7 public hostnames | edge exposure | Access (3 hosts) / app auth | High | SEC-P2-001 |
| Webhooks | Grafana→relay→ntfy | alert delivery | token path, fail-closed | Low | replay residual documented |
| API keys | enrollment tokens; relay token; service pw files | machine auth | mixed | Medium | shared enrollment token live |
| Secrets | `/srv/falcon/secrets/**` root 0600 | secret custody | strong | Low | per-class files; no repo values |
| Account lifecycle | rotate/revoke runbooks | lifecycle | partial | Medium | no password policy (gap §5.4) |
| Audit logging | auditd + OpenSearch REST + Wazuh + Traefik access | audit | partial | Medium | no console-actor audit (see ADMIN) |
| Sensitive logs | relay/enroll/capture redaction | log hygiene | good | Low | topic/token redaction in capture.sh |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 3 | Cloudflare Access apps for falcon/iris/soc; per-service logins | no SSO/per-operator identity; owner-IP bypass | owner decision R-15/C6 |
| Session tokens/cookies | 2 | Wazuh OSD cookie/session TTL 15 min; Access session 24h | Grafana/OSD-central/IRIS session settings not in repo (`Unknown`) | document + pin cookie/session settings |
| JWT validation | 1 | none at origin | origin cannot distinguish Access-authenticated vs bypassed | validate `Cf-Access-Jwt-Assertion` or add origin auth |
| CSRF/CORS | 2 | app defaults | not configured/verifiable from repo | document per-app CSRF/CORS posture |
| Rate limits | 2 | `public-rate-limit`; enroll 60/60s; relay 120/60s; ntfy visitor limits; SSH limit+fail2ban | XFF-keyed; no per-account limits; enroll fleet-wide behind Traefik | key on `CF-Connecting-IP`; add per-account lockout |
| Security headers | 3 | `sec-headers` on all routers | no CSP/permissions-policy | add CSP where compatible |
| Input/output validation | 3 | enroll/relay validation; vector schema | console apps rely on defaults | keep; add negative tests |
| File handling | 3 | locked wg0.conf RMW; chmod 600 | n/a | — |
| API permissions | 4 | OpenSearch least-privilege roles; Wazuh API user; token-gated enroll | writer role broader than doc table (noted in repo) | reconcile IDENTITY doc (already annotated) |
| Admin permissions | 2 | single admin per service; break-glass custody PENDING | no separation; UniFi super-admin shared | OD-04 custody; per-service admin accounts |
| Tenant isolation | N/A | single-tenant lab (EX-22) | n/a | see MT report |
| RLS policies | N/A | no RLS datastore | n/a | — |

## Detailed Review

### Item: Public/internal routes and origin authentication

- Evidence: `config/traefik/dynamic.yml` routers (71-134); `falcon-basic-auth` used only by `falcon-ntop` (96-102); `ntfy-auth` unused (26-28); live origin probes.
- What it does: Traefik routes public hostnames to Grafana (`falcon-grafana`), OSD (`falcon-dash`), ntopng (`falcon-ntop`, basic auth), IRIS (`iris-public`), Wazuh dashboard (`soc-wazuh`), enrollment (`vpn-enroll`), ntfy (`ntfy-public`).
- How it appears to work: Cloudflare Access (edge) decides access for falcon/iris/soc; the origin always accepts and relies on the app login (or ntfy auth / enrollment token).
- Current controls: Access at edge; app logins; host firewall restricts direct origin 80/443 to mgmt/admin subnets; `public-rate-limit`.
- Missing controls: origin-side auth or Access-JWT validation; a working per-router auth middleware for ntfy; defense-in-depth for Grafana/OSD.
- Risks: edge-only enforcement; owner-IP bypass means the owner network reaches consoles directly; misconfiguration is invisible to the origin.
- Recommended improvement: validate `Cf-Access-Jwt-Assertion` at Traefik (forward-auth/plugin) or add service tokens; wire or delete `ntfy-auth`.
- Suggested tests: request each public hostname from a non-bypass source with Access app removed in a staging zone and assert origin denies.
- Suggested docs: ACCESS_AND_ACCOUNTS §6 note that origin auth is intentionally deferred; R-15 acceptance.

### Item: WireGuard tunnel authorization boundary

- Evidence: `config/nftables/falcon.nft:24-33` (fixed) vs live `/etc/nftables.conf:24` (blanket) and live `nft list chain`.
- What it does: governs what WireGuard peers (10.99.0.0/24) may reach on the host.
- Current controls (repo): per-port set — 9443, 15140/15141, 514/1514/1515, UDP 514/2055.
- Missing controls (live): the blanket accept is still in force; no drift assertion covers the wg0 rule set.
- Risks: any enrolled endpoint (lower trust) reaches the edge control plane API, enrollment service, Traefik (all consoles via Host-header routing), Wazuh manager enrollment port, and can attempt SSH.
- Recommended improvement: apply `config/nftables/falcon.nft` (stage 30) and add a post-deploy assertion that the wg0 rule set matches the file.
- Suggested tests: `automation/validation/port_matrix_check.sh` extension: assert no blanket wg0 accept; negative probe from a peer.
- Suggested docs: runbook step to re-apply stage 30 after pull when the firewall file changes.

### Item: Rate limiting and auth abuse controls

- Evidence: `dynamic.yml:34-41`; `automation/vpn/enroll-service.py:116-121`; `automation/alerting/ntfy_relay.py:355-377`; `config/ntfy/server.yml:13-15`.
- What it does: caps public request rates and app-level bursts.
- Current controls: Traefik 50/s + 100 burst per `X-Forwarded-For` value; enroll 60/60s per socket source (fleet-wide behind Traefik); relay 120/60s per source; ntfy per-visitor with internal exemptions; SSH 30/min + fail2ban.
- Missing controls: trusted client-IP extraction; per-account/per-email lockout on Grafana/OSD/Wazuh/IRIS logins.
- Risks: IP-rotation/header-rotation defeats the per-IP bucket; credential stuffing is bounded only by a header-keyed global-ish limit.
- Recommended improvement: key the Traefik limit on `CF-Connecting-IP` (set by Cloudflare, not client-spoofable through the tunnel) or a cloudflared-injected header; enable app brute-force controls where available.
- Suggested tests: send N+1 requests with rotating XFF values and assert the bucket still trips.

### Item: Secrets and sensitive logging

- Evidence: `/srv/falcon/secrets` (live, root 0600; two htpasswd files 0640), `.gitleaks.toml`, `ci/validate.py check_credential_sourcing`, `automation/evidence/capture.sh`.
- Current controls: values outside git; per-class files; fingerprint-only evidence; secret scanning tree + history; relay/enroll logs never print tokens (pubkey prefix only).
- Missing controls: none material found in scope.
- Risks: low. Residual: inherited credential estate (SECRET-P2-001, other domain).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEC-001 | Auth provider | ACCESS §6; compose | Access + per-service logins | no IdP; owner-IP bypass | P2 | owner decision R-15 |
| SEC-002 | Sessions/cookies | Wazuh OSD yml; Access 24h | app defaults + TTLs | no central policy | P3 | document/pin |
| SEC-003 | JWT validation | no code refs | none | origin cannot verify Access | P2 | forward-auth/JWT |
| SEC-004 | CSRF/CORS | app defaults | built-ins assumed | unverifiable from repo | P3 | document |
| SEC-005 | Rate limits | dynamic.yml:36-41 | XFF-keyed + app limits | spoofable key; no per-account | P2 | CF-Connecting-IP; lockouts |
| SEC-006 | Security headers | sec-headers | HSTS etc. | no CSP | P3 | add CSP |
| SEC-007 | Input validation | enroll/relay | strict validation | — | P3 | negative tests |
| SEC-008 | File handling | enroll lock | safe RMW | — | — | — |
| SEC-009 | API permissions | 60-central-deploy | least-privilege roles | — | — | — |
| SEC-010 | Admin permissions | ACCESS §1 | single admin/service | no separation | P2 | OD-04 + per-op accounts |
| SEC-011 | Tenant isolation | see MT | N/A | — | — | — |
| SEC-012 | RLS | N/A | OpenSearch roles | — | — | — |
| SEC-013 | Public routes origin auth | dynamic.yml; live | Access edge only | no origin auth | P2 | SEC-P2-001 fix |
| SEC-014 | WG tunnel authz | nft diff (live) | blanket accept live | fix not applied | P1 | apply stage 30 |
| SEC-015 | Enrollment token lifecycle | live token file | shared token | no expiry/revocation | P2 | per-device tokens |

## Findings

### SEC-P2-001 - Public-facing routers have no origin authentication; `ntfy-auth` is dead config

- Severity: P2
- Confidence: High (config + live origin probes reproduced)
- Area: SEC
- Evidence:
  - `config/traefik/dynamic.yml` (routers 71-134; `ntfy-auth` 26-28; `falcon-basic-auth` only on 96-102)
  - `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §6 (Access apps; owner-IP bypass; app logins remain the origin control)
  - Live origin probes 2026-10-09T21:23Z via loopback: `/`→302 Grafana login, `/dash/`→302 OSD login, `/ntop`→401 (basic auth); public probes: iris→302 origin `/dashboard`, soc→302 origin `/app/login`
- What is happening: Every public hostname reaches the origin (Traefik) without any origin-side authentication except the `/ntop` basic-auth route. Grafana/OSD/IRIS/Wazuh rely solely on their own login pages, and the only network gate is Cloudflare Access at the edge plus the host firewall (origin web allowed only from mgmt/admin subnets). The `ntfy-auth` middleware is defined but referenced by no router (ntfy authenticates itself with `deny-all`).
- Why it matters: A Cloudflare Access policy mistake, removal, or bypass (the owner-IP bypass is documented and active for iris/soc) leaves the consoles exposed with only application logins. The origin cannot tell an Access-authenticated request from a bypassed one (no `Cf-Access-Jwt-Assertion` validation).
- User / business impact: Reduced defense-in-depth for the SOC/monitoring consoles; single misconfiguration away from broader exposure.
- Security / privacy / reliability impact: Edge-only enforcement of admin surfaces.
- Recommended fix: Validate the Access JWT at Traefik (forward-auth) or add an origin auth layer for the console routers; either wire `ntfy-auth` to the ntfy routers or delete it as dead config; document the accepted residual if not fixed.
- Suggested validation: staging-zone test with the Access app removed; assert origin denies (401/403) instead of serving a login page.
- Owner suggestion: @owner
- Effort estimate: M
- Dependencies: Cloudflare API access for Access app/service-token configuration
- Status: still-open (prior run SEC-P2-001)
- Endpoint / data path: `https://falcon.mainecybertech.us/` → cloudflared → Traefik `falcon-grafana` → grafana:3000
- Attack path: public host → Access bypass/misconfig → origin app login (brute force) → console

### Finding ID: (new) SEC-P1-002 remediation is committed but not applied on the live host - WireGuard blanket accept still in effect

- Severity: P1
- Confidence: High (live file + live ruleset reproduced; diff vs repo)
- Area: SEC
- Evidence:
  - `config/nftables/falcon.nft:24-33` (per-port wg0 set; commit `7bb6187`, 2026-10-03 02:24 -0400)
  - Live `/etc/nftables.conf:24`: `iifname "wg0" accept comment "authenticated WireGuard tunnel traffic (probe telemetry)"`; `nft list chain inet falcon_filter input` matches the old file (live check 2026-10-09T21:27Z)
  - `ss -tlnp`: host listeners 0.0.0.0:9443 (edge control plane), 0.0.0.0:8791 (enrollment), 0.0.0.0:80/443 (Traefik), 0.0.0.0:1515 (Wazuh manager)
  - `wg show wg0`: 8 peers with handshakes seconds-to-minutes old
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md` N-24 addendum records the intended narrow set
- What is happening: The repository fix that narrows the former blanket `iifname "wg0" accept` was never deployed to the live host. Every WireGuard peer (including enrolled endpoint devices, which are lower-trust than the host) can reach every host service bound to 0.0.0.0, and can attempt SSH because the blanket rule precedes the SSH source-address rules.
- Why it matters: This is the exact broad-foothold condition SEC-P1-002 was raised to close; the repo state makes the finding look fixed while the live host remains exposed (delivery vs configuration gap).
- User / business impact: A compromised endpoint on the VPN has a direct path to the security host's control plane, enrollment service, and web entrypoints.
- Security / privacy / reliability impact: Authorization boundary regression on the live host.
- Recommended fix: Apply `config/nftables/falcon.nft` via `bootstrap/30-firewall.sh` (or `nft -f`), verify `nft list chain inet falcon_filter input` matches the file, then extend `automation/validation/post_reboot_verify.sh`/`port_matrix_check.sh` with an assertion that no blanket wg0 accept exists.
- Suggested validation: negative probe from a WireGuard peer to 9443/8791/22 asserting DROP; compare live ruleset to the file in CI/health checks.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: maintenance window not required (nftables reload is non-disruptive); re-run of stage 30
- Status: open (live regression; repo fix present since 2026-10-03)
- Endpoint / data path: wg0 peer → host input chain → 0.0.0.0 services
- Attack path: compromised endpoint (VPN) → edge control plane 9443 / enrollment 8791 / Traefik consoles / SSH

### Finding ID: (new) Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints

- Severity: P2
- Confidence: Medium (config semantics reproduced; bypass not load-tested)
- Area: SEC
- Evidence:
  - `config/traefik/dynamic.yml:34-41` (`sourceCriterion.requestHeaderName: X-Forwarded-For`)
  - `docs/security/ENROLL_API.md:42-43` (documents the XFF keying)
  - `automation/vpn/enroll-service.py:17-19,116-121` (per-source-IP limit; behind Traefik all requests share the proxy source, i.e. a fleet-wide bucket)
  - Cloudflare appends the connecting IP to a client-provided `X-Forwarded-For`; Traefik keys the bucket on the raw header value, so a rotating prefix changes the bucket
- What is happening: The only origin rate limit for the public/auth surfaces is keyed on a header that the client influences when proxied through Cloudflare. Auth endpoints (Grafana, OSD, Wazuh dashboard, IRIS, enrollment) have no per-account/per-email lockout.
- Why it matters: Per-IP rotation via header manipulation defeats the intended credential-stuffing/flood bound; the enrollment service's own limiter collapses to one shared bucket behind Traefik.
- User / business impact: Weaker brute-force resistance on internet-reachable logins.
- Security / privacy / reliability impact: Abuse-control gap, medium.
- Recommended fix: Key the Traefik limit on `CF-Connecting-IP` (overwritten by Cloudflare) or a cloudflared-injected header; consider a second, stricter limit on the login paths; document the enrollment fleet-wide limiter and add a per-device-token-only mode when the shared token retires.
- Suggested validation: send 200 requests with unique XFF prefixes and assert 429s still occur; per-account lockout test on Grafana/OSD.
- Owner suggestion: @owner
- Effort estimate: S
- Dependencies: none (Traefik config change + restart)
- Status: open (new)
- Endpoint / data path: internet → Cloudflare → cloudflared → Traefik rateLimit middleware → service
- Attack path: credential stuffing with XFF rotation against `/login` paths

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Live wg0 blanket accept exposes host services to VPN peers | High | Medium | High | live nft vs repo | apply stage 30 + drift assertion |
| Edge-only auth for public consoles | Medium | Medium | High | dynamic.yml; live probes | origin auth / Access JWT validation |
| Rate-limit bypass via XFF rotation | Medium | Medium | Medium | dynamic.yml:36-41 | CF-Connecting-IP keying |
| Shared enrollment token without expiry | Medium | Medium | Medium | live token file | per-device tokens + rotate |
| No per-account auth lockouts | Medium | Medium | Medium | no config evidence | app-level lockouts |

## Recommendations

### Immediate / Release Blocking

- Apply the committed WireGuard narrowing on the live host and add a drift assertion (SEC-P1-002 live regression).

### This Week

- Fix the rate-limit key to a Cloudflare-controlled header; add a stricter limit on login paths.
- Decide and record: origin auth / Access-JWT validation for console routers, or accept R-15 explicitly with the new evidence.

### This Month

- Retire the shared enrollment token in favour of per-device tokens with expiry (owner action C6).
- Add CSP and a documented CSRF/CORS/session posture per console.

### Later / Platform Evolution

- IdP/SSO in front of all consoles (per-operator identities); production-grade break-glass custody (OD-04).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `nft -f config/nftables/falcon.nft` + verify | closes the live P1 | `config/nftables/falcon.nft` | ruleset diff + peer negative probe |
| Change rate-limit key to `CF-Connecting-IP` | removes header-rotation bypass | `config/traefik/dynamic.yml` | curl loop with rotated XFF |
| Delete or wire `ntfy-auth` | removes misleading dead config | `config/traefik/dynamic.yml` | grep references; router behavior |
| Add wg0 assertion to post-deploy checks | prevents recurrence | `automation/validation/*` | check fails on blanket rule |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Origin auth / Access JWT validation | P2 | @owner | M | Cloudflare config |
| Per-device enrollment tokens only | P2 | @owner | S | device onboarding |
| Per-account lockouts on consoles | P2 | @owner | M | app configs |
| CSP/session policy documentation | P3 | @owner | S | — |

## Suggested Tests

- Security: negative probe from a WireGuard peer to 9443/8791/22 (expect DROP) after the firewall fix.
- Security: XFF-rotation rate-limit test against each public hostname.
- Regression: assert `nft list chain` wg0 rules match `config/nftables/falcon.nft` in `post_reboot_verify.sh`.
- Integration: enrollment with an expired per-device token (expect 403) and with the shared token after bindings exist (expect rejection for bound names).
- Manual: Access-app removal test in a staging zone to prove origin denial.

## Suggested Documentation Updates

- `docs/runbooks/ACCESS_AND_ACCOUNTS.md`: record that origin auth is deferred (R-15) and the compensating controls; correct §6 if the falcon bypass policy changed (see ACM finding).
- `docs/security/ENROLL_API.md`: note the live shared-token state and the retirement plan.
- `docs/architecture/PORT_PROTOCOL_MATRIX.md`: add the deployment-verification note for the wg0 set.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Did the falcon Access app lose the owner-IP bypass? | docs vs live mismatch; smoke-gate rationale | Cloudflare Access app/policy read (owner API) |
| Are Grafana/OSD-central session and CSRF settings pinned anywhere? | session policy | rendered configs / DB settings |
| When will the shared enrollment token be rotated? | credential lifecycle | owner action C6 closure evidence |

## Prior-Run Comparison

| Prior finding (falcon-20261005-full-main-e267ce1) | Status now | Notes |
|---|---|---|
| SEC-P2-001 public routers no origin auth; ntfy-auth dead | still-open | config unchanged between `e267ce1` and `08e20d1`; re-verified live |
| (none) | new | live SEC-P1-002 regression (committed fix not applied) |
| (none) | new | XFF rate-limit keying / no per-account limits |

## Limitations

- Cloudflare Access app/policy state was not read via API (not authorized); conclusions about the edge layer rest on live HTTP behavior + repo docs.
- Rate-limit bypass is inferred from config semantics, not load-tested (Medium confidence).
- App-internal session/CSRF settings for Grafana/OSD-central/IRIS are not fully represented in the repo (`Unknown`).

## Appendix

- Live probe commands (read-only): `curl -sI --resolve falcon.mainecybertech.us:443:127.0.0.1 https://falcon.mainecybertech.us/`; `curl -4 -s -o /dev/null -w '%{http_code} %{redirect_url}' https://falcon.mainecybertech.us/`; `nft list chain inet falcon_filter input`; `iptables -S DOCKER-USER`; `ss -tlnp`; `wg show wg0`; `docker ps`.
- Egress IP at check time: 142.105.190.25 (Cloudflare trace), the documented owner bypass IP.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; `ntfy-auth` is dead config |
| SEC-P1-001 | P1 | SEC-P1-002 remediation committed but not applied live - WireGuard blanket accept still in effect |
| SEC-P2-002 | P2 | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints |
