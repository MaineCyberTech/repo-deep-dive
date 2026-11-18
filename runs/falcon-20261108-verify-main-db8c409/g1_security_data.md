# G1 — Security / identity / data verification

Repo: `MaineCyberTech/falcon` @ `main` = `db8c40970083a98e50dbae8038971ec2ac6bc252` (2026-11-08).
Mode: read-only tree verification (no host/live access in this pass). Previous run: `falcon-20261014-verify-main-edbf441`.

## Counts

| Status | Count |
|---|---:|
| verified-fixed | 14 |
| partially-fixed | 15 |
| open | 13 |
| regressed | 1 |
| owner-accepted | 1 |
| **Total** | **44** |

| Severity | Count |
|---|---:|
| P0 | 0 |
| P1 | 4 |
| P2 | 24 |
| P3 | 16 |

## Regressions

- **CHAIN-P2-001 (P2)** — The only automated Access-posture check no longer verifies Access (external-smoke accepts any 302 from the lab vantage). Previous status: `verified-fixed`.
  - Evidence: The prior fix relied on the independent DO watcher asserting Cloudflare Access: automation/alerting/do_watcher/watch.sh:63-75 still requires a 302 to cloudflareaccess.com. docs/runbooks/SSO.md:3-8 says the Access apps were removed on 2026-11-05 and Kestrel is live; docs/CURRENT_STATE.md:24-27 still says Access remains the edge gate. .github/workflows/external-smoke.yml:40-60 remains reachability-only. No check now asserts the Kestrel forward-auth path, so the previous verified-fixed control is void.

## Top new findings

- **ACM-P2-004 (P1, open)** — Endpoint-script sync embeds the entire enrollment token file (all per-device tokens) into every device script
  - Evidence: automation/vpn/sync-levelio-scripts.sh:11 reads the whole /srv/falcon/secrets/vpn_enroll.token into ENROLL_TOKEN and :18-19 substitutes it into every installer/updater script. issue-enroll-token.sh:44,48 writes per-device lines <name>:<token>:<expiry> plus a <name>.enroll-token file. Once any per-device binding exists, every endpoint script receives all bindings (and the multi-line value can break or corrupt the sed substitution), defeating the per-device lifecycle and leaking credentials to every device. This also turns the ACM-P2-001 shared-token issue into a whole-fleet token distribution problem.
  - Remediation: Generate each script from that device's <name>.enroll-token only (or inject the token at runtime); refuse to sync when the token file has more than the one intended line; add a two-binding test proving only the target token is embedded.
- **ADMIN-P2-004 (P2, open)** — Kestrel cutover left Cloudflare Access in the independent posture check, deploy provisioning and current-state docs
  - Evidence: automation/alerting/do_watcher/watch.sh:63-75 still requires a 302 to cloudflareaccess.com; bootstrap/97-cloudflare-api-config.sh:122-155 still creates/updates Access apps and an owner-IP bypass, and bootstrap/run-all-deploy.sh:45 runs it; docs/CURRENT_STATE.md:24-27 says Access remains the edge gate and docs/runbooks/ACCESS_AND_ACCOUNTS.md:124-134,181-192 still describes Access/Authelia while docs/runbooks/SSO.md:3-8 says the Access apps were removed on 2026-11-05.
  - Remediation: Retire/replace the Access provisioning with a Kestrel-aware path (or make it fail closed and require an explicit rollback flag), update the watcher to assert the Kestrel login redirect/401, and refresh the current-state/access docs.
- **ADMIN-P2-005 (P2, open)** — Console API still requires a Cloudflare Access JWT and grants admin to owner-IP/LAN, not the Kestrel identity used by Traefik
  - Evidence: console/auth.py:1-13,116-132 verifies Cf-Access-Jwt-Assertion and otherwise grants admin for CF-Connecting-IP == owner or a direct private peer; config/traefik/dynamic.yml:137-157 now puts only kestrel-auth in front of the console (no Access JWT), and docs/runbooks/SSO.md:12 says the console is Kestrel gate-only. After the documented Access-app deletion, non-owner Kestrel users get 401 from the API, while bootstrap/98-console.sh:121-126 still tries to populate the Access AUD from the deleted app.
  - Remediation: Consume the Kestrel identity headers (signed by Traefik/adapter), remove the Access-JWT and owner-IP/LAN bypass for the public path, and add a test that a non-owner Kestrel user gets viewer access.
- **ADMIN-P2-006 (P2, open)** — Console action endpoints have no CSRF/Origin enforcement and trust an owner-IP/LAN admin identity
  - Evidence: console/api/server.py:722-756 accepts POST /console/api/v1/actions/{ack,unack,downtime-add}, parses the body and calls the root broker without checking Origin/Referer or a CSRF token; console/auth.py:126-131 treats the owner IP or a direct LAN peer as admin; console/web/app.js:258-262 sends the state-changing request. A cross-site POST from an owner browser (or a LAN client) can ack/unack/downtime checks and suppress alerts when the session cookie is sent.
  - Remediation: Require a per-session CSRF token and an Origin/Referer allowlist, enforce Content-Type: application/json, and use SameSite cookies; do not grant admin solely by source IP.
- **ADMIN-P2-007 (P2, open)** — Trusted-header SSO trusts entire Docker subnets: any frontend/backend container can self-assert Grafana/OpenSearch admin
  - Evidence: compose/central/docker-compose.yml:233 whitelists 172.30.2.0/24 for Grafana's auth proxy; config/central/opensearch-security/config.yml:77-79 and automation/wazuh/multi-node/config/wazuh_indexer/opensearch-security/config.yml:77-79 trust 172.30.1/2/4 as internal proxies. A compromised container on those shared networks (vector aggregator, ntop, etc.) can call Grafana/OSD/Wazuh with X-Falcon-User/X-Proxy-User: <admin> and X-Proxy-Roles: admin directly, bypassing Kestrel.
  - Remediation: Scope each whitelist to the Traefik container IP/network, strip client-supplied identity headers at the app ingress, and use mTLS/JWT between Traefik and the apps; separate the data-plane networks.
- **SEC-P2-005 (P2, open)** — SSO header adapter authenticates unsigned X-Authentik-*/Remote-* headers on 0.0.0.0:8090
  - Evidence: console/sso_gateway.py:166-186 accepts X-Authentik-Username/Remote-User and ...-Groups with no shared secret, mints an admin role when the group contains admins (:173), and returns the IRIS token at :184-185. The service binds 0.0.0.0:8090 (bootstrap/98-console.sh:239-240) and nftables allows 8090 from all Docker and management sources (config/nftables/falcon.nft:50); docs/runbooks/SSO.md:152-164 even documents the direct fake-header curl.
  - Remediation: Bind the adapter to Traefik's Docker gateway/loopback, require a Traefik-injected shared secret or mTLS, remove the Remote-* fallback, and add a negative test that a direct fake-header request is 401.
- **SEC-P2-006 (P2, open)** — Client VPN peer-class firewall rule is a hardcoded three-address set; dynamically enrolled clients .23-.99 reach the control plane and Wazuh proxies
  - Evidence: config/nftables/falcon.nft:33 drops only 10.99.0.20/.21/.22 on tcp 9443/15140/15141; automation/vpn/enroll-service.py:46,230-240 allocates any free address in 10.99.0.20-99, and docs/runbooks/VPN.md:16 documents that pool. A new client peer at .23+ is not dropped; syslog/NetFlow also remain open to all wg0 peers at falcon.nft:36-37.
  - Remediation: Replace the three addresses with the full client pool/subnet (or an nft set maintained by enrollment), keep site/sensor peers in a separate range, and add a negative test from a .23 peer.

## Full register

| ID | Sev | Status | Prev | Title |
|---|---|---|---|---|
| DATA-P1-001 | P1 | owner-accepted | owner-accepted | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts class not ISM-managed) |
| PRIV-P1-001 | P1 | verified-fixed | verified-fixed | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| WH-P1-001 | P1 | partially-fixed | partially-fixed | OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified) |
| ACM-P2-001 | P2 | partially-fixed | partially-fixed | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused |
| ACM-P2-003 | P2 | verified-fixed | verified-fixed | Deployed enrollment service does not enforce per-device token expiry; issuance tool and deployed enforcement disagree (no deployed-artifact binding) |
| ADMIN-P2-001 | P2 | verified-fixed | open | Admin/observability consoles are exposed through public routers without origin authentication |
| ADMIN-P2-002 | P2 | partially-fixed | partially-fixed | The Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement anymore |
| ADMIN-P2-003 | P2 | partially-fixed | partially-fixed | No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions |
| API-P2-001 | P2 | partially-fixed | partially-fixed | Ingest contract relies on a shared secret header, not request signing or idempotency keys |
| CHAIN-P2-001 | P2 | regressed | verified-fixed | The only automated Access-posture check no longer verifies Access (external-smoke accepts any 302 from the lab vantage) |
| DATA-P2-002 | P2 | verified-fixed | verified-fixed | Root LV is below the disk guard's 20 GiB threshold: the guard fails every 15 minutes and cannot reclaim back above it (69 GiB snapshot repo on root) |
| DATA-P2-003 | P2 | partially-fixed | partially-fixed | Edge control-plane spool keeps purging ~134 MiB per 10-14 h; nothing consumes it and the purge alert cannot fire at that rate |
| NOTIF-P2-002 | P2 | partially-fixed | open | Notification noise remains high; the accurate disk-guard root alert now dominates and sub-repeat-interval flapping persists |
| PRIV-P2-001 | P2 | verified-fixed | verified-fixed | The vendored MCT client/vendor layer still has no privacy-classification boundary in this repository |
| PRIV-P2-003 | P2 | open | open | The published production verdict still binds a superseded package and carries a contradictory readiness line |
| SEARCH-P2-001 | P2 | partially-fixed | partially-fixed | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale |
| SEARCH-P2-002 | P2 | verified-fixed | verified-fixed | OpenSearch snapshot repository still on the root LV; root free is below the guard threshold and the guard now fails every 15 minutes |
| SEC-P2-001 | P2 | verified-fixed | open | Public-facing routers have no origin authentication; ntfy-auth is dead config |
| SEC-P2-002 | P2 | partially-fixed | open | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints |
| SEC-P2-004 | P2 | verified-fixed | verified-fixed | Deployed enrollment service is a stale build: per-device token expiry is not enforced and the documented issuance flow is rejected |
| ACM-P3-001 | P3 | open | open | No consolidated access-control matrix; authorization remains per-service and distributed across four documents |
| ACM-P3-002 | P3 | open | open | Documented Cloudflare Access policy state does not match live behavior: the falcon app has no owner-IP bypass (and two dead apps remain) |
| AI-P3-001 | P3 | partially-fixed | partially-fixed | Agent/audit-run pointers are stale: the lifecycle runbook still calls the closed 2026-09-30 run 'the current run' and AGENTS.md/README point at it as the full-domain reference |
| AI-P3-002 | P3 | partially-fixed | partially-fixed | No AI-provenance policy and no per-tool agent instruction coverage |
| API-P3-002 | P3 | verified-fixed | verified-fixed | Public-access deploy script still names the retired dash.falcon/ntfy.falcon hostnames in its operator guidance |
| CHAIN-P3-001 | P3 | verified-fixed | open | Anonymous origin -> admin console exposure, plus latent docker.sock mounts in the vendored Shuffle compose |
| CHAIN-P3-002 | P3 | open | open | No automated live-vs-repo drift check for the exposure edges; the applied wg0 narrowing can regress silently |
| DATA-P3-004 | P3 | verified-fixed | verified-fixed | Nightly backup leaves an unencrypted config archive beside the encrypted one and never removes it |
| DATA-P3-005 | P3 | partially-fixed | partially-fixed | Retention documentation drift: snapshot cadence/keep count disagree and the Wazuh indexer backup job is not in the matrix |
| NOTIF-P2-001 | P3 | verified-fixed | open | ntfy-auth Traefik middleware is still dead config; ntfy-native deny-all remains the only access control |
| NOTIF-P3-003 | P3 | partially-fixed | partially-fixed | Retired public lab-ntfy hostname still referenced in ledgers and the 97 deploy fallback text |
| PRIV-P3-001 | P3 | open | open | Owner/legal privacy inputs and the 'synthetic-only' wording remain outstanding |
| SEARCH-P3-001 | P3 | verified-fixed | verified-fixed | Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return |
| SEC-P3-004 | P3 | open | open | wg0 tunnel has no peer-class separation; every peer (including client endpoints) can reach the edge control plane and Wazuh proxies |
| SEC-P3-005 | P3 | verified-fixed | verified-fixed | Console session cookies are not marked Secure (central OSD explicit cookie.secure: false; Grafana/Wazuh default) |
| WH-P3-001 | P3 | partially-fixed | open | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired |
| ARCH-P2-003 | P2 | partially-fixed | open | Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing |
| ACM-P2-004 | P1 | open | new | Endpoint-script sync embeds the entire enrollment token file (all per-device tokens) into every device script |
| SEC-P2-005 | P2 | open | new | SSO header adapter authenticates unsigned X-Authentik-*/Remote-* headers on 0.0.0.0:8090 |
| SEC-P2-006 | P2 | open | new | Client VPN peer-class firewall rule is a hardcoded three-address set; dynamically enrolled clients .23-.99 reach the control plane and Wazuh proxies |
| ADMIN-P2-004 | P2 | open | new | Kestrel cutover left Cloudflare Access in the independent posture check, deploy provisioning and current-state docs |
| ADMIN-P2-005 | P2 | open | new | Console API still requires a Cloudflare Access JWT and grants admin to owner-IP/LAN, not the Kestrel identity used by Traefik |
| ADMIN-P2-006 | P2 | open | new | Console action endpoints have no CSRF/Origin enforcement and trust an owner-IP/LAN admin identity |
| ADMIN-P2-007 | P2 | open | new | Trusted-header SSO trusts entire Docker subnets: any frontend/backend container can self-assert Grafana/OpenSearch admin |

## Notes

- 37 prior findings were re-checked (the 36 G1-area rows plus the explicitly requested ARCH-P2-003) and 7 new issues were added: 44 total.
- `verified-fixed` entries are re-checked against the current tree (code/config at `db8c409`); live-only claims from the previous run are marked in the evidence text where this read-only pass could not re-measure them.
- New IDs continue the area numbering: ACM-P2-004, SEC-P2-005/006, ADMIN-P2-004/005/006/007.
- No P0 found. One new P1 (ACM-P2-004): the endpoint-script sync would distribute all per-device enrollment tokens to every device once per-device bindings are used.
- The biggest status changes are positive on the public-edge controls (ADMIN-P2-001, SEC-P2-001, CHAIN-P3-001 now verified-fixed behind Kestrel), but the Kestrel cutover left the Access-based posture/deploy/docs paths stale (CHAIN-P2-001 regressed; ADMIN-P2-004 new).

