# Access Control Matrix (companion artifact)

- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repos: `falcon-build` @ `8282d3f` · `falcon-edge-build` @ `45dfed0` (dirty — in-flight CI work)
- Generated: 2026-09-30T07:35Z · Auditor: repo-deep-dive wave-1 subagent (06/24)
- Source reports: `06_security_authz_tenancy_audit.md`, `24_access_control_matrix_audit.md`
- Status vocabulary: implemented / partial / gap; severities per shared rules.

## 1. Identity and role inventory

| Identity | Where defined | How established | Scope | Enforcement point | Notes |
|---|---|---|---|---|---|
| `public` | `falcon-edge-build/src/falcon_control/service.py:138` | none (no client cert) | `GET /healthz` only | route table | Only unauthenticated edge route |
| `bootstrap` | `service.py:140,208-212` | `Authorization: Bearer fbt_…` single-use token | `POST /enrollments` | token hash/expiry/redemption checks `:291-331` | Token plaintext never stored (`tokens.py:20-25`) |
| `sensor` | `service.py:196-200` | client cert fingerprint mapped to a sensor row | sensor routes under its own id | fingerprint lookup + path match + lifecycle checks | Mismatch → 403 + quarantine + audit (`:225-234`) |
| `operator` | `service.py:201-202` | any CA-signed cert with `CN=operator` | token/list/detail/update/directive/quarantine/release/revoke routes | `_authorize:216-217` | **Gap: subject string is enrollable** (ACM-P1-001) |
| `user` (host) | `/etc/passwd`; sudo group; `id` | OS account, password SSH | shell, sudo, Docker access | OS auth; sshd (password auth EX-01), fail2ban | Owner/operator account; `.env` readable |
| `root` (host) | OS | sudo / systemd | host + container admin | sudo password | All privileged units run as root |
| systemd services | `falcon-build/config/systemd/*`, live units | root or `user` ExecStart | backups, metrics, relay, enroll, edge CP | unit hardening (NoNewPrivileges, Protect*) | Edge secrets backup + update-apply run as root |
| OpenSearch users | `falcon-build/bootstrap/60-central-deploy.sh:119-190` | internal users file + securityadmin | data RBAC | OpenSearch security plugin | `admin`, `falcon-vector-writer` (writer), `falcon-dashboard` (reader+kibana), `falcon-healthcheck` (reader), `falcon-backup` |
| Grafana admin | container env/db (`grafana.env`) | Grafana login (anonymous/signup disabled) | metrics dashboards | Grafana auth | Credential file `/srv/falcon/secrets/grafana_admin.pw` |
| ntopng users | `/srv/falcon/secrets/ntop_htpasswd` | Traefik basic auth | `/ntop` | Traefik `falcon-basic-auth` | Dedicated file since 2026-09-23 |
| ntfy users | `/srv/falcon/ntfy/user.db` + relay files | ntfy login; `auth-default-access: deny-all` | alert topics | ntfy auth | Relay users in `/srv/falcon/secrets/ntfy_relay_*` |
| Wazuh manager/agents | upstream agents | agent key (TLS) + enrollment password | 1516/1517 API paths | Wazuh authd | `0.0.0.0` + any-source firewall allow (SEC-P2-006) |
| UniFi admin | controller UI; `/home/user/.env` `unifi_admin` | UniFi login (super-admin) | network fabric | UniFi OS | Out-of-band; documented in `ACCESS_AND_ACCOUNTS.md` |
| Client-VPN peers | `falcon-build/automation/vpn/enroll-service.py` | shared token + pubkey (or server keygen) | wg0 `10.99.0.20-99/32` | token HMAC `:104-111` | No per-client identity/throttle (ACM-P2-002) |

## 2. Edge control-plane route access matrix (19/19 routes classified)

Source: `falcon-edge-build/src/falcon_control/service.py:137-158`; columns: required identity, object scoping, lifecycle gate.

| # | Method & path | Required | Object scope | Lifecycle gate | Audit |
|---|---|---|---|---|---|
| 1 | GET `/healthz` | public | — | — | no |
| 2 | POST `/bootstrap-tokens` | operator | bound `sensorId` must exist | — | `bootstrap_token.created` |
| 3 | POST `/enrollments` | bootstrap | token profile/sensor binding; device-UUID rules | token expiry/redeemed | `sensor.enrolled` |
| 4 | POST `/sensors/{id}/renewals` | sensor | path == cert id; device UUID check | REVOKED only (RETIRED allowed — gap) | `certificate.renewed` |
| 5 | GET `/sensors` | operator | — | — | no |
| 6 | GET `/sensors/{id}` | operator | — | — | no |
| 7 | POST `/sensors/{id}/heartbeats` | sensor | path == cert id | REVOKED denied; quarantine may heartbeat | accepted/duplicate |
| 8 | PUT `/sensors/{id}/inventory` | sensor | path == cert id | REVOKED denied | — |
| 9 | GET `/sensors/{id}/desired-state` | sensor | path == cert id | `_config_blocked` (Q/S/R) | — |
| 10 | POST `/sensors/{id}/state-reports` | sensor | path == cert id | REVOKED denied | — |
| 11 | POST `/sensors/{id}/events` | sensor | path == cert id | REVOKED denied | — |
| 12 | POST `/ingest/vector` | sensor | cert only (no path id) | **none — gap (ACM-P1-002)** | `ingest_vector` |
| 13 | GET `/sensors/{id}/update-manifest` | sensor | path == cert id | `_config_blocked` | — |
| 14 | GET `/sensors/{id}/recovery-directive` | sensor | path == cert id | REVOKED denied only (quarantine allowed by design) | — |
| 15 | POST `/sensors/{id}/update-manifests` | operator | — | — | — |
| 16 | POST `/sensors/{id}/recovery-directives` | operator | — | — | — |
| 17 | POST `/sensors/{id}/quarantine` | operator | — | — | `sensor.quarantined` |
| 18 | POST `/sensors/{id}/release` | operator | — | — | `sensor.released` |
| 19 | POST `/sensors/{id}/revoke` | operator | — | — | `sensor.revoked` (`destroyKeys` inert) |

Route-matching behavior: 405 with `Allow` for wrong method; 404 problem body for unknown paths; all problem bodies use RFC-9457-style JSON. Idempotency keys (16–128 chars) required on heartbeat/inventory/state-reports/events; not on ingest.

## 3. Central host and service access matrix

| Surface | Listener | Network restriction | AuthN/AuthZ | Evidence |
|---|---|---|---|---|
| SSH | `0.0.0.0:22` | mgmt `192.168.222.0/24`, admin `192.168.111.0/24`, IPv6 link-local (nftables) | password auth (EX-01/OD-20); maxauthtries 4; root prohibit-password; fail2ban 5→1h | `falcon.nft:26-28`, `10-host-baseline.sh:24-32`, live `/etc/fail2ban/jail.local` |
| Traefik HTTPS | `:443` | mgmt/admin subnets; public via Cloudflare tunnel | per-app login; ntopng basic auth; sec-headers | `dynamic.yml` |
| OpenSearch | `127.0.0.1:9200` | loopback (Docker) | internal users/roles | compose override:15 |
| OpenSearch Dashboards | `127.0.0.1:443:5601` (loopback→container) | loopback | OSD login + `falcon-dashboard` | compose override:20-21 |
| Wazuh API | `127.0.0.1:55000` | loopback | API creds (owner) | override:4 |
| Wazuh syslog/agent/enroll | `0.0.0.0:1514/1515/1516/1517/1518` | DOCKER-USER: 1516/1517 **any source**; syslog ports restricted | agent key; authd password | `31-docker-user-firewall.sh:62-68` |
| ntfy | `127.0.0.1:2586` + Traefik | loopback + Traefik route | deny-all + users | `server.yml:7-8` |
| Alert relay | docker bridge `*:9099` | `br-*`/docker0 only | POST token path `/grafana/<token>`; GET health public | `ntfy_relay.py:197-224` |
| VPN enroll | `0.0.0.0:8791` (Traefik front) | bridges/LAN per nftables | shared token | `enroll-service.py:104-111` |
| Edge control plane | `0.0.0.0:9443` | `iifname wg0 accept` (all tunnel peers) | mTLS + route roles | `falcon.nft:24`, `edge-control-plane.lab.json` |
| OpenCanary | `0.0.0.0:21/23/3306/1433/8008/9100` | DOCKER-USER allowlist | honeypot (intentional bait) | `MCT_CONSOLIDATION.md:27` |
| WireGuard | `0.0.0.0:5182/udp` | public (protocol) | peer keys | `falcon.nft:23`; R-30 lesson |

## 4. Credential, key, and certificate lifecycle

| Material | Issued by / stored at | Format & mode | Expiry | Revocation | Pruning | Evidence / finding |
|---|---|---|---|---|---|---|
| Bootstrap token | operator CLI → `control-plane.db.bootstrap_tokens` | `fbt_`+32B; SHA-256 at rest; plaintext only in response | 60 s – 7 d (`tokens.py:30-33`) | redemption/expiry; row retained | **none** — 3 expired unredeemed live (ACM-P2-001) | `tokens.py`; DB census |
| Sensor cert | control plane signs device CSR | Ed25519, 30 d (`CERT_DAYS_LAB=30`) | auto-renew rotation (6 h cooldown); live cert exp 2026-10-30 | state-based only; no CRL/OCSP | fingerprint replaced on rotation | `service.py:333,399`; DB census |
| Sensor private key | device (`identity.py`) | PKCS#8 PEM, 0640 | n/a | n/a (destroy on reimage per policy) | n/a | `identity.py:44,66`; SEC-P2-005 |
| Operator cert/key | `pki.issue_operator_cert` → `/home/user/falcon-edge-secrets/operator.*` | Ed25519, 30 d (exp 2026-10-29) | renewed by `renew_operator_cert.py` (<15 d) | none | replacement on renewal | live openssl; ACM-P1-001 |
| Server cert | `issue_server_cert` (only if absent) | 365 d; SANs `falcon.lab`, localhost, 127.0.0.1, 10.99.0.1 (live) | regeneration manual | n/a | n/a | SEC-P2-001 |
| Lab CA | `pki.init_ca`; `/home/user/falcon-edge-secrets/ca/` | Ed25519, 3650 d, key 0600 | 2036 | n/a (root of trust) | n/a | SEC-P2-004 backup exposure |
| Directive/desired-state signing seed | generated at first CP start | 32 B, 0600 | non-expiring | rotate = new key (agents pin keyId) | n/a | `service.py:125-130` |
| VPN enrollment token | `enroll-service-install.sh` (`openssl rand -hex 24`) | 24 B hex, 0600 | none | manual replace + service restart not required (read per request) | n/a | ACM-P2-002 |
| WireGuard peer keys | `wg genkey` (site) / endpoint / server-side generation | keys in `/srv/falcon/secrets/wireguard`; conf 0600 | none | remove block + `syncconf` | manual | SEC-P3-001 |
| OpenSearch users | bootstrap `internal_users.yml` | hashed; declared set | none | delete via API | bootstrap replaces set | R-28 lesson |
| Relay token | `/srv/falcon/secrets/ntfy_relay.token` | path token; Basic auth to ntfy | none | rotate file + Grafana contact point | n/a | `ntfy_relay.py:10,197-200` |
| Owner `.env` | owner-provided | cleartext, 0600, owner `user` | none | manual | n/a | SEC-P2-002 |
| Edge secrets backups | `backup_edge_secrets.py` → `/home/user/falcon-edge-delivery` | tar.gz **unencrypted**, 0600; keep 7 | n/a | n/a | rotation by `--keep` | SEC-P2-004 / ACM-P2-003 |

## 5. Sensitive action matrix

| Action | Who can perform | Enforcement | Audit | Gap |
|---|---|---|---|---|
| Issue bootstrap token | operator | `POST /bootstrap-tokens` role check | yes | role forgeable (ACM-P1-001) |
| Enroll sensor | bootstrap-token holder | token hash/expiry/profile/binding | yes | → operator escalation (ACM-P1-001) |
| Rotate sensor cert | sensor cert holder | path match + device UUID | yes | RETIRED allowed (ACM-P1-002) |
| Issue update manifest | operator | role check | — | role forgeable |
| Publish recovery directive | operator | role check | — | role forgeable |
| Quarantine/release/revoke | operator | role check | yes | `destroyKeys` inert (ACM-P1-002) |
| Push telemetry batch | sensor cert holder | role check only | yes | REVOKED allowed (ACM-P1-002) |
| Enroll client VPN peer | shared token holder | HMAC token | log lines only | shared, peer replace (ACM-P2-002) |
| Back up edge secrets | root timer | file modes | systemd | unencrypted artifacts (ACM-P2-003) |
| Apply agent update (root) | agent-written request file | none root-side | result.json | SEC-P1-002 (prompt 06) |
| Rotate central credentials | owner via runbook | capture + rotation drill | evidence captures | host-only steps |
| Cloudflare Access policy change | owner (external) | external only | none in repo | ACM-P2-004 |

## 6. Network and middleware enforcement

| Layer | Control | Evidence | Gaps |
|---|---|---|---|
| Host input | nftables default-deny + allowlists | `config/nftables/falcon.nft` | live state not readable by audit account |
| Docker DNAT | DOCKER-USER managed allowlist / mode-aware | `bootstrap/31-docker-user-firewall.sh`; contradiction C-29/C-30 fixed | 1516/1517 any-source was deliberate (SEC-P2-006) |
| Traefik | routers, sec-headers, basic auth (ntopng) | `config/traefik/dynamic.yml` | no rate-limit middleware (ACM-P2-004) |
| Backend isolation | internal Docker networks; loopback publishes | `compose/central/docker-compose.yml:6-13` | Wazuh override publishes several `0.0.0.0` ports |
| VPN | peer keys; tunnel accepted wholesale | `falcon.nft:23-24` | every peer reaches 9443 (ACM-P3-002) |
| Edge CP TLS | CERT_OPTIONAL, TLS ≥1.2, CA verify | `pki.py:83-95` | no hostname check on the client side (SEC-P2-001) |

## 7. Background jobs and DB helpers

| Unit/helper | Runs as | Touches | Authorization-relevant risk |
|---|---|---|---|
| `falcon-update-apply.path/.service` (edge) | root | `/opt/falcon-edge/src/falcon_agent`, agent state | trusts agent-written request (SEC-P1-002) |
| `falcon-edge-secrets-backup.timer` (edge) | root | secrets → delivery | unencrypted archive (ACM-P2-003) |
| `falcon-edge-operator-cert.timer` (edge) | root | operator key/cert | renewal without revocation; shared owner account |
| `falcon-edge-metrics.timer` | root (verified) | `/srv/falcon/textfile` metrics | writes root-owned metrics file consumed by Prometheus |
| `falcon-backup.timer` / `falcon-disk-guard.timer` | root | snapshots/configs/disk | credentials from `.env` + root files |
| `falcon-docker-user-firewall.service` | root | iptables DOCKER-USER | last result success; mode state root-only |
| `store.py` helpers | in-process (CP) | sensors/tokens/audit | parameterized SQL; no prune helpers |
| `retire_stale_sensors.py` / `_drop_token.py` | manual | sensors / token rows | manual lifecycle; no schedule |

## 8. Client-side hiding, server enforcement, audit, tests

- **Client-side hiding:** none — no first-party UI; the CLI is a thin client and all routes re-check identity server-side (`_authorize`), verified by an unauthenticated live probe returning 403.
- **Server enforcement gaps:** `POST /ingest/vector` lifecycle (ACM-P1-002); operator role substance (ACM-P1-001); update-apply trust (SEC-P1-002).
- **Audit logs:** edge `audit_log` table (4,664 rows; 4664 grows per request; entries for enroll/renew/revoke/quarantine/release/ingest/mismatch); OpenSearch `security-auditlog-*`; host `auditd`; Traefik access log `/srv/falcon/traefik-logs`; systemd journals.
- **Authz tests present:** role boundaries (`tests/phase2/test_service_integration.py:340-354`), sensor-id mismatch quarantine (`:296-315`, `tests/phase6/test_ingest_endpoint.py:108-115`), token single-use/expiry (`:189-237`), quarantine/revoke (`:317-338`).
- **Authz tests missing:** CSR-subject escalation, REVOKED ingest, RETIRED renewal, `destroyKeys`, operator-CA separation, enrollment throttle (ACM-P3-001).

## 9. Gap summary (mapped to findings)

| Gap | Finding | Severity |
|---|---|---|
| Operator role from enrollable CN | ACM-P1-001 / SEC-P1-001 (REV-P1-004) | P1 |
| Revoked ingest / inert destroyKeys / retired renewal | ACM-P1-002 / SEC-P2-003 | P1/P2 |
| No token/directive pruning | ACM-P2-001 | P2 |
| Shared VPN enrollment token, peer replace, no throttle | ACM-P2-002 / SEC-P3-001 | P2/P3 |
| Unencrypted secrets backup + manifest omission | ACM-P2-003 / SEC-P2-004 | P2 |
| Public routes: no rate limits, Access out-of-repo | ACM-P2-004 / SEC-P2-006 | P2 |
| Missing forbidden-access tests | ACM-P3-001 | P3 |
| CP reachable by every VPN peer | ACM-P3-002 (INTG-P3-004) | P3 |
| Update-apply root trust | SEC-P1-002 (REV-P1-005) | P1 |
| No client hostname verification | SEC-P2-001 (REV-P2-007) | P2 |
| Vector holds sensor key | SEC-P2-005 | P2 |
| Cleartext `.env` sourced into captures | SEC-P2-002 (LIVE-P2-005) | P2 |
