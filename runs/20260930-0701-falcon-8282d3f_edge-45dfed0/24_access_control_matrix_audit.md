# Access Control Matrix Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (full-domain)
- Repositories: `falcon-build` @ `8282d3f` (main, clean) · `falcon-edge-build` @ `45dfed0` (main, dirty — in-flight CI work)
- Generated at: 2026-09-30T07:45Z · Auditor: repo-deep-dive wave-1 subagent (prompts 06 + 24) · Area code: ACM
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/24_access_control_matrix_audit.md`
- Companion artifact: `access_control_matrix.md` (role, route, credential, sensitive-action matrices)
- Scope limitations: read-only account (no root/docker/wg); live firewall/Docker state not readable; private-repo CI not independently verifiable; no auth-bypass tests against live services; edge repo dirty

## Scope

Reviewed: roles/identities in the edge control plane and shared host; permissions and route coverage for all 19 control-plane endpoints; object scoping (single site; sensor-id mismatch); key/token/certificate lifecycle (issuance, expiry, pruning, revocation); the VPN enrollment service; DB helpers and background units; client-side vs server-side enforcement; authz test estate. Not reviewed: upstream product RBAC internals; out-of-repo Cloudflare Access; multi-tenant features (none — prompt 25 N/A); no live forbidden-access requests beyond one unauthenticated probe.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `falcon-edge-build/src/falcon_control/service.py` | code | Route→identity matrix; resolver; lifecycle; audit | `ROUTES` :137-158; `_authorize` :205-235; ingest :550-581 |
| `falcon-edge-build/src/falcon_control/{store,tokens,pki}.py` | code/DB | Roles, token records, audit, issuance | No prune; no CRL; single CA |
| `falcon-edge-build/automation/validation/{retire_stale_sensors,_drop_token,renew_operator_cert,backup_edge_secrets}.py` | code | Lifecycle helpers | Retire/revoke/renew/manual drop; plaintext backup |
| `/home/user/falcon-edge-secrets/control-plane.db` (read-only query) | live data | Role/cert/token census | 1 ACTIVE / 5 RETIRED / 3 REVOKED; tokens 22 (13 unredeemed, 3 expired); directives 15/15 expired; audit 4,664 |
| `falcon-build/bootstrap/60-central-deploy.sh:119-190` | config | OpenSearch users/roles | admin, vector-writer, dashboard, healthcheck, backup |
| `falcon-build/docs/runbooks/ACCESS_AND_ACCOUNTS.md` | docs | Human access surfaces/gaps | 5 surfaces; per-service logins; gaps §4 |
| `falcon-build/automation/vpn/enroll-service.py` | code | Peer enrollment authz | Shared token; peer replacement; no lock/throttle |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Read-only `ROUTES` extraction + handler walk | code review | Endpoint→role matrix | 19/19 routes classified in the companion artifact |
| Read-only SQLite census (`mode=ro&immutable=1`) | live data | Lifecycle state | Counts above; expired items retained; no prune evidence |
| `curl -sk https://127.0.0.1:9443/api/v1/sensors` (no cert) | live probe | Server enforcement | 403 `IDENTITY_UNKNOWN` — not UI-only |
| `openssl x509` operator/server certs | live probe | Issuance/expiry | Operator 30 d (exp 2026-10-29); server 365 d; same CA |
| `systemctl cat/show` edge CP + backups | live config | Who runs what | CP as `user` hardened; backups/apply root |
| `git diff 2b5bc8b 45dfed0`; `python3 -B ci/secret_scan.py`; `ci/validate.py` | diff/validation | Prior findings + gates | Identity/PKI unchanged → still-open; edge clean 891 files; central `validation_failures=0` |

## Prior-Run Findings Verification (access-control items)

| Prior ID | Status | Evidence at current commits |
|---|---|---|
| REV-P1-004 (enrollment→operator) | **still-open** | CN→operator `service.py:201-202`; CSRs signed verbatim `pki.py:30-59`; → ACM-P1-001 |
| REV-P1-005 (update-apply root trust) | **still-open** | Apply script unchanged; request/digest/path agent-controlled → prompt-06 SEC-P1-002, noted in matrix |
| REV-P2-007 (one CA; no hostname check) | **still-open** | Same CA (`pki.py:10`); `check_hostname=False` → ACM-P3-002 note |
| INTG-P3-004 (CP bind 0.0.0.0; any VPN peer) | **still-open** | `edge-control-plane.lab.json`; live socket; no per-source ACL → ACM-P3-002 |

## Executive Summary

The model is coherent for a single-owner lab and mostly server-side: explicit route identities, sensor-id/path matching with quarantine, append-only audit, single-use expiring tokens, least-privilege OpenSearch users, allowlisted host ports, ntfy deny-all, ntopng basic auth. Gaps are lifecycle and identity-substance: (1) operator role comes from an enrollable subject string (ACM-P1-001); (2) revocation is not enforced uniformly — REVOKED can still ingest, `destroyKeys` is inert, RETIRED can renew (ACM-P1-002); (3) expired tokens/directives are never pruned (ACM-P2-001); (4) VPN enrollment uses one shared credential with peer replacement, no throttle (ACM-P2-002); (5) CA/signing/operator material sits in unencrypted delivery backups (ACM-P2-003); (6) public routes lack in-repo rate limits and rely on out-of-repo Cloudflare Access (ACM-P2-004). Tests lack the escalation/revocation cases (ACM-P3-001). Prior REV/INTG access-control findings are still-open, none regressed.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Edge roles | `Identity` `service.py:104-111` | operator/sensor/bootstrap/public | Implemented | High | Operator role from CN |
| Route permission table | `service.py:137-158` | 19 endpoints | Implemented | Medium | Companion matrix lists all |
| Sensor path scoping | `service.py:218-234` | Path == cert identity | Implemented | Low | Mismatch quarantines + audits |
| Cert issuance | `pki.py` | Server/operator/sensor certs | Implemented | Medium | One CA; no CRL |
| Sensor lifecycle | revoke/quarantine; `retire_stale_sensors.py` | State transitions | Partial | Medium | Ingest not gated; retire ≠ revoke |
| OpenSearch users/roles | `bootstrap/60-central-deploy.sh:119-190` | Central data RBAC | Implemented | Low | 5 least-privilege users |
| Human surfaces | `ACCESS_AND_ACCOUNTS.md` | Grafana/OSD/ntop/ntfy/UniFi | Implemented | Medium | No SSO/per-person identity |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Roles | 2 | operator/sensor/bootstrap; admin/service users | Operator role from CN | Separate issuance; pin subjects |
| Permissions | 3 | Route table + role checks | Ingest bypasses lifecycle | Central gate |
| Org/tenant/workspace membership | N/A | Single owner/site (prompt 25 N/A) | — | — |
| Project/ticket/document/billing/API key/webhook permission | 2 | API keys/tokens: media/bootstrap/edge signing | No scopes/rotation; no webhooks (N/A) | Document/scope tokens |
| Admin console | N/A (no first-party console) | Operator CLI | — | — |
| Public/authenticated/internal routes | 3 | Traefik + CP routes | No limits; Access out-of-repo | Throttles; record policy |
| Server actions | N/A | No server-action framework | — | — |
| API endpoints | 3 | 19 CP routes; OpenSearch/Wazuh APIs | Ingest/lifecycle gap | Lifecycle check |
| Background jobs | 3 | Hardened units; audit | Host-only units; apply trust | Capture units; SEC-P1-002 |
| DB helpers | 3 | `store.py` parameterized; append-only audit | No prune helpers | Retention jobs |
| Middleware | 3 | nftables/DOCKER-USER/Traefik | 1516/1517 any-source; no limits | Tighten/limit |
| Client-side hiding | N/A | No first-party UI | — | — |

## Detailed Review

### Item: Edge control-plane endpoint matrix

- Evidence: `service.py:137-158`, `:205-235`; `http_server.py:18-46`; full matrix in `access_control_matrix.md` §2.
- What it does / gaps: identity from the cert (fingerprint→sensor, else CN→operator); four requirement levels; sensor paths must match or quarantine; missing throttling, ingest lifecycle, token scopes (ACM-P1-002, ACM-P3-002).
- Improvement/tests/docs: unified `authorize(row, route)`; route×identity tests; update trust docs.

### Item: Key, token, and certificate lifecycle

- Evidence: `tokens.py:20-54`, `pki.py:62-80`, `identity.py:40-80`, `renew_operator_cert.py`, live census.
- What it does / gaps: tokens hashed/single-use/TTL; sensor certs 30 d auto-renew; operator cert 30 d renewed <15 d; server cert 365 d; CA 10 y; missing pruning (ACM-P2-001), CRL/OCSP (ACM-P1-002), backup encryption (ACM-P2-003).
- Improvement/tests/docs: retention job; revocation design; lifecycle tests; custody docs.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity |
|---|---|---|---|---|---|
| ACM-001 | Roles | `service.py:104-203` | 4 identity classes | Role string forgeable | P1 |
| ACM-002 | Permissions | `service.py:205-235` | Role + path checks | Ingest exempt | P2 |
| ACM-003 | Org/tenant membership | prompt 25 N/A | Single owner/site | — | — |
| ACM-005 | Admin console | Operator CLI | Operator cert gate | Same as ACM-001 | P1 |
| ACM-006 | Public/authenticated routes | Traefik + CP | Server-side enforcement | No rate limits | P2 |
| ACM-009 | Background jobs | systemd units | Root jobs; audit | Update-apply trusts agent | P1 |

Notes: ACM-004 (API keys/tokens), ACM-007 (server actions), ACM-008 (API endpoints), ACM-010 (DB helpers), ACM-011 (middleware), ACM-012 (client-side hiding) map to the inventory/scorecard and prompt-06 findings; no server-action framework or first-party UI exists, and the CLI re-checks identity server-side.

## Findings

### Finding ID: ACM-P1-001 - Operator authority is derived from an enrollable certificate subject string (REV-P1-004 still-open)

- Severity: P1
- Confidence: High
- Area: ACM (role resolution)
- Evidence:
  - `falcon-edge-build/src/falcon_control/service.py:196-203` (CN=operator → operator), `:333,:399` (enroll/renew sign `data["csrPem"]`); `pki.py:30-59,73-80` (verbatim CSR signing; same CA); `tests/phase2/test_service_integration.py:340-354` (no CSR-subject test).
- What is happening: role comes from a name the enrolling party chooses — the extended check "role resolution relies on unforgeable attributes, not user-controlled strings" fails.
- Why it matters: enrollment-token holders become operators; membership/role lists cannot be trusted for authorization.
- User / business impact: fleet-wide administrative control from a device credential.
- Security / privacy / reliability impact: authorization bypass at the highest tier.
- Recommended fix: server-pinned subjects; separate operator issuance path (CA or EKU/policy); reject sensor CSRs with non-sensor subjects; forbidden-access tests.
- Suggested validation: `CN=operator` enrollment rejected; sensor cert gets 403 on operator routes; operator flow still works.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: PKI change; gate records
- Status: still-open (carried from REV-P1-004)

### Finding ID: ACM-P1-002 - Lifecycle state is not enforced everywhere: revoked ingest, inert `destroyKeys`, retired renewal

- Severity: P1
- Confidence: High
- Area: ACM (lifecycle authorization)
- Evidence:
  - `service.py:550-581` (`h_ingest_vector` no lifecycle check), `:196-203` (REVOKED fingerprints resolve), `:759-770` (`destroyKeys` audited only), `:388-390` (renewal rejects REVOKED only), `retire_stale_sensors.py` (RETIRED); live DB 3 REVOKED / 5 RETIRED rows.
- What is happening: lifecycle enforcement is duplicated per handler and drifted; no CRL/OCSP.
- Why it matters: incident response ("revoke the sensor") under-delivers; revoked identities keep injecting; retired ones keep renewing.
- User / business impact: telemetry integrity; audit says revoked while data continues.
- Security / privacy / reliability impact: residual access after revocation; API contract mismatch.
- Recommended fix: central fail-closed lifecycle gate (incl. ingest); RETIRED non-renewable; implement or remove `destroyKeys`; add revocation matrix tests.
- Suggested validation: REVOKED → 403 on every sensor route; RETIRED renewal 403; destroy semantics verified.
- Owner suggestion: edge maintainer · Effort: S–M · Dependencies: API/doc wording
- Status: open (new; prompt-06 SEC-P2-003)

### Finding ID: ACM-P2-001 - Expired tokens and directives are never pruned; lifecycle evidence is census-only

- Severity: P2
- Confidence: High
- Area: ACM (key/token lifecycle)
- Evidence:
  - `tokens.py:28-54` (issue/redeem; no prune); only `automation/validation/_drop_token.py` (manual bake cleanup); live DB: 22 tokens (13 unredeemed, 3 expired), 15 directives (15 expired); `store.py:297,320` filters expired rows (fail-closed but retained).
- What is happening: expired items remain indefinitely; no retention policy artifact.
- Why it matters: audit noise; unclear lifecycle maintenance answer; stale-grant exposure risk if a future query drops the filter.
- User / business impact: low today; grows with fleet size.
- Security / privacy / reliability impact: lifecycle hygiene.
- Recommended fix: scheduled prune (expired unredeemed tokens, expired directives) with audit counters and documented retention.
- Suggested validation: dry-run counts; re-run zero; one audit entry per run.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none
- Status: open (new; extends ND-P3-010/REV-P3-008)

### Finding ID: ACM-P2-002 - Client-VPN enrollment uses one shared credential, can replace peers, and is unthrottled

- Severity: P2
- Confidence: High
- Area: ACM (enrollment authorization)
- Evidence:
  - `falcon-build/automation/vpn/enroll-service.py:104-111` (single token, no throttle), `:136-150` (same-name peer replaced; unlocked read-modify-write), `:163-165` (server-generated private key returned); `config/traefik/dynamic.yml:111-117` (no auth middleware).
- What is happening: the whole client fleet trusts one bearer token; enrollment is not attributable and can displace a peer.
- Why it matters: token leakage yields uncontrolled tunnel membership and peer shadowing; no per-client revocation.
- User / business impact: network membership integrity; limited forensics.
- Security / privacy / reliability impact: shared-secret blast radius.
- Recommended fix: per-client one-time tokens; name ownership binding; lock + rate limit; structured audit; deprecate server-side keygen.
- Suggested validation: clients cannot overwrite each other; token reuse rejected; burst throttled.
- Owner suggestion: build agent · Effort: M · Dependencies: endpoint script updates
- Status: open (new; prompt-06 SEC-P2-005)

### Finding ID: ACM-P2-003 - Fleet-privilege key material sits in unencrypted delivery backups, incompletely manifest-covered

- Severity: P2
- Confidence: High
- Area: ACM (privileged key custody)
- Evidence:
  - `falcon-edge-build/automation/validation/backup_edge_secrets.py:43-52` (plain `tar.gz` incl. CA key, `signing.seed`, operator/server keys, sensor certs, control-plane DB) into `/home/user/falcon-edge-delivery`; listing shows owner+root archives; `build_release_manifest.py:48-61` skips unreadable files → 42-entry manifest (commit 155f244) omits the root-owned archive (also `closeout/REVIEW-2026-09-30.md:219`).
- What is happening: read access to one directory yields operator, CA, and signing authority; manifest verification misses the most sensitive artifact.
- Why it matters: operator impersonation and update/directive forgery if exposed.
- User / business impact: privilege boundary depends on one directory's confidentiality.
- Security / privacy / reliability impact: key custody failure.
- Recommended fix: encrypt backups, move them out of the delivery surface, manifest fail-closed on unreadable files.
- Suggested validation: archive unreadable without key; manifest covers every file or fails.
- Owner suggestion: edge maintainer + owner · Effort: S–M · Dependencies: encryption decision
- Status: still-open (REV-P3-010 + INTG-P2-003)

### Finding ID: ACM-P2-004 - Public routes rely on per-app logins and out-of-repo Cloudflare Access; no in-repo rate limits

- Severity: P2
- Confidence: Medium
- Area: ACM (public routes)
- Evidence:
  - `config/traefik/dynamic.yml:42-125` (only `falcon-ntop` carries basic auth; no rate-limit middleware defined); `ACCESS_AND_ACCOUNTS.md:55-67` (no SSO/per-person identity; Access is an owner decision, R-15 "OPEN (prepared, fail-closed)"); `MCT_CONSOLIDATION.md:70-79`/`WAZUH_INTEGRATION.md:150` (Access policies exist only in the Cloudflare account).
- What is happening: the repository cannot demonstrate fail-closed public access if external policy is missing; origin limits are absent.
- Why it matters: policy gap or a new tunnel route can expose dashboards; no defense-in-depth at the origin.
- User / business impact: dashboard/alert-channel exposure on Access drift.
- Security / privacy / reliability impact: auth depends on a system outside audited config.
- Recommended fix: Traefik rate-limit middleware; store Access policy IDs/rules in-repo with a verification script; prefer per-person IdP identities.
- Suggested validation: anonymous non-allowlisted request → Access redirect; burst trips the limit.
- Owner suggestion: owner + ops · Effort: M · Dependencies: Cloudflare account access
- Status: open (R-15; new ACM framing)

### Finding ID: ACM-P3-001 - Authz tests omit the escalation and post-revocation cases

- Severity: P3
- Confidence: High
- Area: ACM (authz test estate)
- Evidence:
  - `tests/phase2/test_service_integration.py:340-354` (sensor-on-operator, no-cert, operator-on-sensor only); `tests/phase6/test_ingest_endpoint.py:108-115` (mismatch quarantine, not revoked/quarantined ingest or retired renewal); no `destroyKeys` semantics test found.
- What is happening: the two highest-impact authz defects (ACM-P1-001/002) are outside the test matrix.
- Why it matters: regressions would not be caught; "RBAC tested" claims are narrower than they sound.
- User / business impact: latent authz bugs ship.
- Security / privacy / reliability impact: coverage gap with security consequence.
- Recommended fix: table-driven forbidden-access tests over routes × {no cert, sensor, operator, revoked, retired, CN=operator sensor}; run in CI.
- Suggested validation: each forbidden case asserts 403 + audit entry where applicable.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: ACM-P1-001/002 fixes
- Status: open (new)

### Finding ID: ACM-P3-002 - Control plane reachable from every VPN peer; mTLS is the only gate (INTG-P3-004 residue)

- Severity: P3
- Confidence: High
- Area: ACM (network ACL)
- Evidence:
  - `falcon-edge-build/deploy/edge-control-plane.lab.json` (`"bind": "0.0.0.0"`; tunnel peers expected); `falcon-build/config/nftables/falcon.nft:24` (`iifname wg0 accept`, incl. client-VPN peers); live `0.0.0.0:9443`; prior INTG-P3-004.
- What is happening: enrolled client devices share the tunnel with the fleet control plane; route roles are the only barrier; no rate limiting.
- Why it matters: broad reachable surface for 403 floods and future authz bugs; thread-per-connection server.
- User / business impact: minor today; grows with client-VPN population.
- Security / privacy / reliability impact: DoS/noise from any tunnel member.
- Recommended fix: bind to a sensor-only address/allowlist (peer AllowedIPs are already /32); per-source limits.
- Suggested validation: non-sensor peer cannot open 9443; sensor traffic unaffected.
- Owner suggestion: edge maintainer + ops · Effort: S–M · Dependencies: wg peer policy
- Status: still-open (INTG-P3-004)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Operator role forgery | P1 | Medium | Fleet control | ACM-P1-001 | Separate issuance; subject pinning |
| Revocation ineffective | P1 | Medium | Telemetry integrity | ACM-P1-002 | Central gate; CRL/destroy |
| Peer takeover via shared token | P2 | Low–Med | Tunnel membership | ACM-P2-002 | Per-client tokens; name binding |
| Privilege keys exposed via delivery dir | P2 | Low | CA/signing/operator compromise | ACM-P2-003 | Encrypt; relocate; fail-closed manifest |

## Recommendations

### Immediate / Release Blocking
1. ACM-P1-001: replace CN-based operator resolution before issuing new enrollment tokens.
2. ACM-P1-002: make revocation effective (ingest gate, RETIRED renewal denial, `destroyKeys` decision).

### This Week
3. ACM-P2-003: encrypt/relocate secrets backups; fix manifest fail-open.
4. ACM-P3-001: add the forbidden-access test matrix to CI.
5. ACM-P2-001: add token/directive pruning with audit counters.

### This Month
6. ACM-P2-002: per-client enrollment tokens, name binding, throttling.
7. ACM-P2-004: rate-limit middleware + in-repo Access policy evidence.
8. ACM-P3-002: bind the control plane to a sensor-only address/allowlist.

### Later / Platform Evolution
9. SSO/per-person identities across dashboards (R-15); token scopes/rotation API.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Forbidden-access test matrix | Locks in the two P1 fixes | `tests/phase2/`, `tests/phase6/` | CI green; fails on unfixed builds |
| Lifecycle check in `h_ingest_vector` | Closes revoked-ingest gap | `service.py` | Revoked sensor 403 |
| Prune job for expired items | Lifecycle hygiene | new helper + timer | Dry-run counts; re-run zero |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Operator identity redesign (CA/EKU) | P1 | edge maintainer | M | gate records |
| Revocation design (CRL/deny list/destroy) | P1 | edge maintainer | M | PKI |
| Per-client VPN enrollment tokens | P2 | build agent | M | endpoint scripts |

## Suggested Tests

- Unit: `_resolve_identity` with `CN=operator` unmapped fingerprint → reject/sensor; lifecycle gate per state; token prune helper.
- Integration: route × identity classes (19 routes × 6 identities); REVOKED ingest/heartbeat/desired-state/renewal; RETIRED renewal; mismatch quarantine.
- E2E/CI/manual: operator flow after PKI change; forbidden-access suite in `validate.yml`; manifest completeness; scanner arg validation; Access policy vs in-repo record; non-sensor peer blocked from 9443.

## Suggested Documentation Updates

- Documentation: update `access_control_matrix.md` on PKI/lifecycle changes; edge security boundary/trust docs (revocation, operator identity, Vector key); `ACCESS_AND_ACCOUNTS.md` (enrollment surface, `.env` split); both proposed risk-register entries.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which live identities hold `CN=operator` certs; should RETIRED sensors ever renew? | Scope of escalation; lifecycle rule | Cert inventory + issuance history; owner decision |

## Appendix

- Route/identity extraction read-only from `service.py:137-158`; only one unauthenticated live probe (403) was sent. Full matrices: `access_control_matrix.md`. Prior map: REV-P1-004→ACM-P1-001; REV-P1-005→prompt-06 SEC-P1-002; REV-P2-007/INTG-P3-004→ACM-P3-002; INTG-P2-003/REV-P3-010→ACM-P2-003. No secret values printed.
