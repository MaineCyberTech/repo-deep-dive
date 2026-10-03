# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: SEC
- Output path: docs/audits/{name}/{run}/06_security_authz_tenancy_audit.md
- Scope limitations: no live host; inbound-mode, Access policy and nft state are `unverified` from the repo alone. No secret values are printed.

## Scope

Reviewed the externally reachable surface (Traefik routers, Cloudflare Access, ntfy, OpenCanary, WireGuard), host firewall config, API auth (enroll/ingest), secret handling adjacency, and the secret scanner. This is a single-tenant lab; tenancy/RLS is not applicable.

## Evidence Reviewed

- `config/traefik/dynamic.yml`, `config/nftables/falcon.nft`, `bootstrap/32-inbound-mode.sh`, `bootstrap/31-docker-user-firewall.sh`.
- `compose/mct/docker-compose.opencanary.yml`.
- `bootstrap/97-cloudflare-api-config.sh`, `automation/validation/secret_scan.py`, `.gitleaks.toml`.
- `ledgers/exception_register.md`, `ledgers/redactions.md`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/traefik/dynamic.yml` | Config | Public router auth | only `falcon-ntop` has basic auth |
| `git grep ntfy-auth` | Search | Dead config | defined L26, unused |
| `config/nftables/falcon.nft` L24 | Config | wg0 scope | blanket accept |
| `compose/mct/...opencanary.yml` L27-33 | Config | Exposed canary ports | 6 published on 0.0.0.0 |
| `ledgers/exception_register.md` EX-13 | Ledger | Inbound state | register says CLOSED; matrix says open |
| `bootstrap/97-cloudflare-api-config.sh` L42-45 | Source | Token in argv | `curl -H "Authorization: Bearer ..."` |

## Executive Summary

The security posture is mature for a lab: default-deny host firewall, Cloudflare Access in front of public hosts, basic auth on ntopng, pinned images and an independent secret scanner. The main residual gaps are structural: public routes rely solely on Cloudflare Access (no origin auth), WireGuard peers are trusted host-wide, the OpenCanary honeypot publishes six decoy ports on all interfaces, and a Cloudflare API token is passed on the `curl` command line where it is visible in the process list. These were previously reported and remain open at this commit.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Traefik routers | `config/traefik/dynamic.yml` | ingress/auth | Functional | High | origin auth gap |
| Host firewall | `config/nftables/falcon.nft` | default-deny | Functional | Medium | forward/output accept |
| Inbound toggle | `bootstrap/32-inbound-mode.sh` | open/closed | Functional | High | state contradiction |
| Cloudflare API | `bootstrap/97-cloudflare-api-config.sh` | DNS/tunnel as code | Functional | Medium | token in argv |
| OpenCanary | `compose/mct/...opencanary.yml` | deception | Functional | High | 6 public ports |
| Secret scanner | `automation/validation/secret_scan.py` | leak detection | Functional | Low | strong |
| Redactions | `ledgers/redactions.md` | hash registry | Maintained | Low | no values |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 3 | Cloudflare Access | no origin auth | SEC-P2-001 |
| Session tokens/cookies | 2 | basic auth only | no session model | n/a lab |
| JWT validation | 1 | none first-party | n/a | — |
| CSRF/CORS | 2 | Traefik defaults | undocumented | document |
| Rate limits | 3 | `public-rate-limit` | XFF-keyed | SEC-P2-003 |
| Security headers | 4 | `sec-headers` | — | — |
| Input/output validation | 3 | Vector validation | shared secret | API |
| File handling | 3 | root-owned secrets | env_file | SECRET |
| API permissions | 3 | enroll token | no expiry | API |
| Admin permissions | 3 | SSH allowlist | password auth EX-01 | owner-accepted |
| Tenant isolation | N/A | single-tenant lab | — | — |
| RLS policies | N/A | no DB RLS | — | — |

## Findings

### Finding ID: SEC-P1-001 - OpenCanary publishes six decoy services on all interfaces

- Severity: P1
- Confidence: High
- Area: SEC
- Evidence:
  - `compose/mct/docker-compose.opencanary.yml` lines 27-33 — ports `21,23,3306,1433,9100,8008` published without a host bind
  - `compose/mct/docker-compose.opencanary.yml` lines 37-39 — joins `multi-node_default` external network
- What is happening: Six ports bind `0.0.0.0`; access control depends on the host firewall allowlist.
- Why it matters: Honeypot services deliberately accept connections; any firewall/allowed-source gap exposes them broadly. Port 9100 collides conceptually with node-exporter.
- User / business impact: Increased attack surface on the lab host.
- Security / privacy / reliability impact: A mis-set inbound mode turns decoys into reachable services.
- Recommended fix: Bind to the management interface/loopback only, or add an explicit nftables allowlist per port; document the decoy exposure as intentional and fenced.
- Suggested validation: `ss -ltn` on host; negative test from a non-allowlisted source.
- Owner suggestion: ops+owner
- Effort estimate: S
- Dependencies: inbound mode
- Status: open

### Finding ID: SEC-P1-002 - Blanket `iifname "wg0" accept` grants every WireGuard peer host-wide access

- Severity: P1
- Confidence: High
- Area: SEC
- Evidence:
  - `config/nftables/falcon.nft` line 24 — `iifname "wg0" accept comment "authenticated WireGuard tunnel traffic"`
- What is happening: Any authenticated VPN peer can reach every host service; the only further barrier is per-service auth.
- Why it matters: A compromised client peer becomes a broad foothold (CHAIN-P1-001).
- User / business impact: Lateral movement from a VPN endpoint.
- Security / privacy / reliability impact: Network-level trust too broad.
- Recommended fix: Replace the blanket accept with per-destination/per-port rules; isolate client peers from the probe/control network.
- Suggested validation: nft ruleset review + peer-to-service scan from a test peer.
- Owner suggestion: ops+owner
- Effort estimate: M
- Dependencies: peer inventory
- Status: open

### Finding ID: SEC-P1-003 - Owner-directed open-inbound override state is contradictory across records

- Severity: P1
- Confidence: Medium
- Area: SEC
- Evidence:
  - `ledgers/exception_register.md` line 22 / line 51 — EX-13 `CLOSED 2026-09-22`
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md` line 7 — describes the open window and revert
  - `bootstrap/32-inbound-mode.sh` lines 14, 37-40 — runtime state file `/srv/falcon/compose-state/inbound-mode`
- What is happening: Ledgers, architecture docs and the runtime state file can disagree about whether inbound is open.
- Why it matters: An auditor/operator cannot determine actual exposure from records; the last real state is only on the host.
- User / business impact: Mis-scoped risk decisions.
- Security / privacy / reliability impact: Unknown exposure window.
- Recommended fix: Make the runtime state file authoritative and reflect it into a ledger row at each toggle; reconcile docs.
- Suggested validation: `bootstrap/32-inbound-mode.sh status` captured to evidence at each change.
- Owner suggestion: ops+owner
- Effort estimate: S
- Dependencies: None
- Status: partially-fixed

### Finding ID: SEC-P2-001 - Public-facing routers have no origin authentication; `ntfy-auth` is dead config

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `config/traefik/dynamic.yml` lines 89-134 — `falcon-grafana`, `falcon-dash`, `iris-public`, `soc-wazuh`, `vpn-enroll`, `ntfy-public` use only `sec-headers`/`public-rate-limit`
  - `config/traefik/dynamic.yml` lines 26-28 — `ntfy-auth` defined; `grep ntfy-auth` shows no router references it
- What is happening: Cloudflare Access is the single gate for public hosts; origin has no independent auth.
- Why it matters: If Access policy, tunnel config or a DNS bypass is wrong, the origin is directly reachable.
- User / business impact: Exposure of dashboards/case data.
- Security / privacy / reliability impact: Single control at the edge.
- Recommended fix: Add origin auth (mTLS or basic/OIDC) to public routers, or record a testable owner acceptance with an automated Access-posture check (external-smoke already asserts 302 to cloudflareaccess.com).
- Suggested validation: Direct-to-origin request without Access returns 401/403.
- Owner suggestion: ops+owner
- Effort estimate: M
- Dependencies: Access policy export
- Status: open

### Finding ID: SEC-P2-002 - Cloudflare API token is passed on the `curl` command line

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `bootstrap/97-cloudflare-api-config.sh` lines 42-45 — `curl ... -H "Authorization: Bearer ${cf_api:-${cf_key}}"`
- What is happening: The bearer token appears in the process argv, readable by other local users/processes and in any capture of process listings.
- Why it matters: Token disclosure on a multi-process host.
- User / business impact: Account-level Cloudflare control if leaked.
- Security / privacy / reliability impact: Credential exposure.
- Recommended fix: Pass the token via a config file (`curl --config`) or `-H @file`, or via `env` stdin, never argv.
- Suggested validation: `ps` during the script shows no token; scanner/allowlist unchanged.
- Owner suggestion: ops+owner
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SEC-P3-001 - Default-deny `forward`/`output` policies are inert at the managed-table level

- Severity: P3
- Confidence: High
- Area: SEC
- Evidence:
  - `config/nftables/falcon.nft` lines 47-55 — `forward` and `output` chains are `policy accept`, documented as "Docker owns forward policy"
- What is happening: The managed table does not enforce egress or forwarding; Docker/iptables-nft tables do.
- Why it matters: Readers may believe the managed table is default-deny for all hooks.
- User / business impact: Low; documentation clarity.
- Security / privacy / reliability impact: Acceptable for the design but must be understood.
- Recommended fix: Add explicit comments/assertions, or a CI check that the DOCKER-USER chain is non-empty and allowlisted.
- Suggested validation: `iptables -S DOCKER-USER` at deploy.
- Owner suggestion: ops+owner
- Effort estimate: S
- Dependencies: None
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| VPN peer reaches control plane | P1 | Medium | High | falcon.nft L24 | SEC-P1-002 |
| Decoy ports exposed | P1 | Low | High | opencanary | SEC-P1-001 |
| Unknown inbound state | P1 | Medium | High | ledgers/docs | SEC-P1-003 |
| Origin reachable if Access fails | P2 | Low | High | dynamic.yml | SEC-P2-001 |
| Token in argv | P2 | Medium | Medium | cf script | SEC-P2-002 |

## Recommendations

### Immediate / Release Blocking
- Reconcile inbound state and capture it (SEC-P1-003).

### This Week
- Narrow wg0 accept (SEC-P1-002).
- Fence OpenCanary ports (SEC-P1-001).

### This Month
- Origin auth or testable acceptance (SEC-P2-001).
- Move Cloudflare token off argv (SEC-P2-002).

### Later / Platform Evolution
- DOCKER-USER assertions in CI (SEC-P3-001).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Update PORT_PROTOCOL_MATRIX to closed | Removes contradiction | docs/architecture | review |
| `curl --config` for CF token | Removes argv exposure | bootstrap/97 | ps check |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Origin auth on public routers | P2 | ops | M | Access export |
| Per-port wg0 rules | P1 | ops | M | peer map |

## Suggested Tests

- Direct-origin request without Access is rejected.
- nft negative test from non-allowlisted sources.
- `ss -ltn` decoy-port exposure check.

## Suggested Documentation Updates

- `docs/architecture/PORT_PROTOCOL_MATRIX.md` — align with EX-13 CLOSED and runtime state.
- Threat model — record the origin-auth acceptance or control.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What is the current `/srv/falcon/compose-state/inbound-mode`? | Real exposure | host read |
| Is OpenCanary actually running? | Scope | `docker ps` |

## Appendix
Not applicable.
