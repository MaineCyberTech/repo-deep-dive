# Security Adversary Lens — Trust Ladder, Escalation Chains, Blast Radius

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab, full-domain) · Lens: Security Adversary (area `ADV`) · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repositories: `falcon-build` @ `8282d3f` (central); `falcon-edge-build` @ `45dfed0`, moved `→ f1c5def` mid-run (CI-only delta per prompt-36/43); delivery `/home/user/falcon-edge-delivery`. Read-only audit.
- Generated at: 2026-09-30T15:45Z · Auditor: repo-deep-dive wave-2 subagent (this lens) · Successor to run `20260930-0320` (REV/INTG/LIVE/ND lens).
- Method: trust-ladder enumeration; chain analysis over domain reports 06/08/24/30/36/38/41/42/43 + `access_control_matrix.md`; four isolated sandbox reproductions under `/tmp/opencode/adv-sandbox` (temp dirs, loopback, no repo/live-system mutation).
- Scope limitations: no root/docker/wg/nft on the live host; live firewall/container state taken from reports and repo; no exploitation of live systems; edge repo assessed at `45dfed0`; secrets redacted (names/paths/lengths only).

## Scope

Reviewed: the full trust ladder (anonymous → enrollment-token holder → sensor/agent → client-VPN peer → operator → host user → root), step-up paths, privileged consumers of lower-trust input (agent-written files → root apply; sensor-written NDJSON → root-run exporter; webhook → publisher; CSR subject → role), leaked-token/leaked-key blast radius, chains across repos, and whether any of it would be detected. Explicitly cross-referenced, not re-filed: SEC-P1-001/002, SEC-P2-003/004/005, SECRET-P1-001/002/003, ACM-P1-001/002, CTR-P1-001/002, XREPO-P1-002, NOTIF-P2-001. Not reviewed: upstream Wazuh/Traefik internals, physical access attacks beyond reported bake evidence, Cloudflare account state.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `falcon-edge-build/src/falcon_control/service.py`, `pki.py`, `store.py`, `tokens.py` | code | Identity resolution, CSR signing, lifecycle, audit | `_resolve_identity` :196-203; enroll :333; renewal :378-416; ingest :550-599; audit `store.py:129` |
| `falcon-edge-build/src/falcon_agent/{runner,client,identity,directives}.py` | code | Agent trust, update staging, signing pin | Manifest verify+offer :444-473; stage :475-521; auto-apply gate :600 |
| `falcon-edge-build/image/overlay/usr/local/sbin/falcon-apply-update.sh`; `deploy/falcon-update-apply.*`; `tests/phase7/test_update_apply.py` | code/test | Privileged apply path | Root script; name-only archive filter :76-80; no negative tests :114-135 |
| `falcon-build/config/nftables/falcon.nft`; `bootstrap/31-docker-user-firewall.sh` | config | Network trust boundaries | `iifname wg0 accept` :24; 1516/1517 any-source :62-68 |
| `falcon-build/automation/vpn/enroll-service.py` | code | Client-VPN admission | Shared token :104-111; peer replace :136-150; 0.0.0.0 bind :171-175 |
| `falcon-build/automation/alerting/ntfy_relay.py` | code | Alert path integrity | Path token + fail-open :197-200; no access log :226-227 |
| `falcon-build/automation/observability/fleet_metrics.py` | code | Consumer of sensor ingest data | `collect_ingest` :126-200 trusts payload `sensor_id` |
| Reports 06/24/36/38/41/42/43 + `access_control_matrix.md`; prior `findings.json` | reports | Domain IDs for cross-reference | Statuses re-used; prior-run findings re-verified in R6 |
| Live read-only: delivery dir listing; `tar -tzf` of one secrets backup (names only); secret perms | host | Blast-radius evidence | Archive contains `ca/ca.key.pem`, `operator.key.pem`, `signing.seed`, `control-plane.db` |

## Verification Performed

| Ref | Check / reproduction | Result | Notes |
|---|---|---|---|
| R1 | Enrollment-token → operator escalation, full mTLS flow on loopback with temp PKI (script `repro1_operator_escalation.py`) | **Reproduced**: token→`CN=operator` CSR signed (201); cert mapped as sensor; renewal replaces fingerprint (200); unmapped cert gets `GET /sensors` 200 and `POST /bootstrap-tokens` 201 | Audit rows look like a normal enroll + renew + token creation; no CN/subject recorded |
| R2 | Forged `apply-request.json` + unsigned bundle, real apply script with `AGENT_STATE`/`SRC_DIR`/`SYSTEMCTL` overrides (sandbox, non-root) | **Reproduced**: attacker-computed digest accepted, payload installed, `result=applied` | In production the script runs as root; no signature consulted at the root boundary |
| R3 | Crafted tar with symlink member `falcon_agent → <absolute dir>` plus `falcon_agent/pwned.txt` | **Reproduced**: name filter passes; extraction writes through the symlink; script installs the symlink and reports `applied` | Write-through (= arbitrary file write as root in production); `tests/phase7` has no symlink/device case |
| R4 | Sensor cert posts NDJSON with `sensor_id` of a *different* sensor; run `collect_ingest` on the spool | **Reproduced**: `edge_capture_*` and `edge_ids_events_window_total` exported under the victim `sensor_id` | One enrolled sensor can mask drops/silence or fake liveness for another |
| R5 | Read-only verification: delivery archive members/perms; secret-store modes | `falcon-edge-secrets-backup-20260930T011054Z.tar.gz` (0600 user) contains `signing.seed`, `ca/ca.key.pem`, `operator.key.pem`, `server.key.pem`, `control-plane.db`; delivery dir 775 | Real secrets never printed; names/lengths only |
| R6 | Prior-run re-check on the current code paths | REV-P1-004/005, REV-P2-007, REV-P3-010/011, INTG-P1-003 **still-open**; audited logic unchanged `2b5bc8b → 45dfed0` (prompt 06/24/38 diffs) | No regression found |

## Executive Summary

The security domains found the individual defects; this lens assembled and (where safe) reproduced the **chains**. Three results matter: (1) a single device enrollment token becomes **fleet-wide operator** authority in three API calls — enroll a `CN=operator` CSR, renew once so the certificate fingerprint is unmapped, then use that certificate as operator (R1) — and operator can mass-publish signed update manifests, whose execution on devices ends in the same root apply script that accepts unsigned, agent-written input (R2/R3); (2) the CI/governance failures are a security chain too: the delivered, repo-committed Wazuh credential literals (API-P0-001) plus the unencrypted edge PKI backup and baked device/host credentials mean one artifact or one lost device can expose CA, operator and update-signing material — no revocation or seed-rotation path exists, so the fleet would keep trusting it indefinitely; (3) nothing in the ladder is detectable: the escalation's only trace is local audit rows indistinguishable from normal operations, edge alert rules are undeployed, and one sensor can even spoof another sensor's health metrics (R4). Controls that held under sandbox attempts: single-use/expiring tokens, path-vs-cert mismatch quarantine, agent-side manifest signature/expiry checks, bundle digest/compile rejection for honest mistakes. Net: the domain “P1 identity” finding is not a paperwork issue; it is a live ladder from one credential to root across the fleet, and the fix ordering should be identity substance, key custody, then detection.

## Inventory

| Item | Path / symbol | Adversarial role | Risk | Notes |
|---|---|---|---|---|
| Enroll route | `service.py:291-376`, `pki.py:30-59` | Lower-trust input → certificate | **High** | Signs CSR subject verbatim |
| Renewal route | `service.py:378-416` | Fingerprint unmapping primitive | **High** | Enables R1 |
| Root apply | `falcon-apply-update.sh`; `deploy/falcon-update-apply.path` | Agent input → root | **High** | R2/R3 |
| Edge secrets backup | `backup_edge_secrets.py:43-52`; delivery dir | Fleet trust material | **High** | CA+operator+seed, plain |
| Host input firewall | `falcon.nft:24` | Tunnel peer → host plane | Medium | Blanket wg0 accept |
| VPN enrollment | `enroll-service.py:104-150` | Shared token → peer slot | Medium | Replace by name |
| Ingest spool | `service.py:550-599` → `fleet_metrics.py:126-200` | Sensor input → metrics | Medium | Self-attested identity |

## Trust Ladder

| Position | Can reach | Step-up paths found | Controls that held |
|---|---|---|---|
| Anonymous (internet/LAN) | Wazuh authd 1516/1517 (password, unthrottled), SSH password auth from mgmt/admin subnets (fail2ban), WG UDP 5182 handshake, Traefik ≥ Access (out-of-repo) | Brute force/DoS authd; password spray sshd | nft default-deny for non-allowed ports; CP 403 without cert; fail2ban 5→1 h |
| Enrollment-token holder | `POST /enrollments` (public route) | **R1: `CN=operator` CSR + one renewal ⇒ operator**; operator persists by minting more tokens | Token single-use, hashed at rest, 60 s–7 d TTL; profile match; device-UUID rules |
| Sensor / agent (mTLS) | Own sensor routes; `POST /ingest/vector` (no path/lifecycle check); renewals (RETIRED allowed) | **Write `apply-request.json` ⇒ root (R2)**; Vector/sibling collector holds device key 0640; ingest spoofing (R4) | Fingerprint→sensor; path mismatch ⇒ 403 + quarantine + audit; REVOKED denied on most routes |
| Client-VPN peer (shared token) | **All host input from `wg0`** incl. sshd 22, CP 9443, enroll 8791; peer slots by name | Shared token ⇒ enroll/replace any peer (peer shadowing); then host-plane access; sensor peers reach the same surface | mTLS still gates CP data; name regex; key length check |
| Operator (cert `CN=operator`) | Tokens, sensor list/detail, update manifests (any URL + digest, signed by CP), directives, quarantine/revoke | Mass-stage signed updates → device root (auto-apply enabled in P7-G01 drill config; shipped image config does not set it); no operator revocation ⇒ 30-day expiry is the only bound | Per-route role check; signed+expiring manifests verified agent-side against pinned key |
| Host `user` account | `.env` (sudo + cloud/API keys), root-run repo scripts (CTR-P1-001), delivery dir (CA/operator/seed), edge secrets dir 700 user | `sudo` password in `.env`; user-writable root ExecStart scripts ⇒ root; delivery backup ⇒ fleet trust (ADV-P1-002) | File mode 0600; units run as root; not a boundary for this account |
| Root / host | Everything on host; edge CP secrets; signing seed; sensor fleet via signed updates | Sign updates accepted by all pinned agents; mint CA certs | None beyond crypto (not a boundary to defend) |
| Stolen sensor image/device | Wi-Fi PSK; device account password = host credential source per bake evidence; sensor key/cert | Password reuse ⇒ host account; sensor identity ⇒ fleet APIs; then delivery ⇒ fleet trust root | No post-flash rotation evidence (SECRET-P1-001) |

## Findings

### Finding ID: ADV-P1-001 - A single-use device token becomes fleet-wide operator authority (reproduced)

- Severity: P1
- Confidence: High (reproduced end-to-end in a temp sandbox at this commit)
- Area: ADV (identity escalation / trust ladder)
- Evidence:
  - `falcon-edge-build/src/falcon_control/service.py:196-203` (`peer_fp` → sensor else `peer_cn == "operator"` → operator); `:333` and `:399` sign the submitted `csrPem`; `:400-403` renewal replaces the stored fingerprint; `pki.py:30-59` (verbatim, same CA, no extensions/EKU); `tokens.py:28-54` (single-use token is the only gate on `/enrollments`).
  - Reproduction R1: token 201 → `CN=operator` enroll 201 (mapped as sensor) → renewal 200 (cert A unmapped) → cert A: `GET /sensors` 200, `POST /bootstrap-tokens` 201.
  - Chain tail: `runner.py:444-473,475-521,600-601` (operator-issued manifest → download → digest/size → apply request); `falcon-apply-update.sh:37-45,66-80` (root trusts that request — see as well SEC-P1-002/CTR-P1-002); `image/overlay/etc/falcon-agent/agent.json` has no `update_auto_apply`; drill evidence `evidence/raw/P7-G01/20260930T041130Z_update-apply-rollback-drill-3.out:14` shows it enabled in the update drill.
- What is happening: the operator role is derived from a name the enrolling party chooses, and the one mechanism that should tether a certificate to a device (fingerprint mapping) is undone by the renewal route. Legitimate device flows only renew with sensor CSRs, but the service never enforces that.
- Why it matters: a claim token that ships in the delivery dir/CI/image is a fleet-admin credential, not a device credential; the operator role can issue update manifests and directives fleet-wide and can mint more tokens, so the escalation is repeatable and self-sustaining.
- User / business impact: one leaked token or one unauthorized enrollment converts into fleet control, update authority and eventual root on devices.
- Security / privacy / reliability impact: root-of-authority bypass; the ladder’s second rung skips directly to the fifth.
- Recommended fix: server-pin CSR subjects/policies per route (ignore or reject non-`sensor` subjects; separate operator CA/EKU); make renewal preserve/rotate only sensor identities under the same policy; add forbidden-access tests (ACM-P3-001).
- Suggested validation: rerun R1 against the fix — enroll `CN=operator` must 403 or map to sensor; operator flow via the separate path still works.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: PKI/gate records · Status: still-open (carried from REV-P1-004 / ACM-P1-001 / SEC-P1-001; new end-to-end reproduction)

### Finding ID: ADV-P1-002 - One readable directory (or one lost device) exposes CA, operator and update-signing authority

- Severity: P1
- Confidence: High for the artifacts and custody facts (R5, live listings); the “seed → fleet root” tail is code-verified, not executed
- Area: ADV (key custody / blast radius)
- Evidence:
  - Delivery: `falcon-edge-secrets-backup-20260930T011054Z.tar.gz` (0600, owner `user` in a 775 dir) contains `signing.seed`, `ca/ca.key.pem`, `operator.key.pem`, `server.key.pem`, `control-plane.db`; `backup_edge_secrets.py:25-26,43-52` writes it there unencrypted; no offsite (INTG-P1-003).
  - Fleet trust tail: `directives.py:50-61` verifies manifests against the key pinned at enrollment; `runner.py:475-521` stages them; `falcon-apply-update.sh:76-96` installs them as root; `pki.py:73-80` + `_resolve_identity` mean the CA key can mint `CN=operator` certs directly.
  - Input chain: `bake_lab_test_image.sh` bakes the host credential as the device password and the Wi-Fi PSK (SECRET-P1-001; evidence source `.env sudo (host credential)`); `falcon-edge-delivery` holding images/credentials is the same account/dir group as the backup.
  - No invalidation: no CRL/OCSP (`pki.py`); `renew_operator_cert.py` auto-renews the on-disk operator key; `signing.seed` has no rotation procedure (SECRET-P2-004).
- What is happening: fleet root-of-trust (CA key), fleet admin key (operator), and fleet update-signing key (seed) are three files in one unencrypted archive reachable by the same account that the device/image password protects. A copy is sufficient; no live access needed.
- Why it matters: the update path trusts the seed, so a seed-holder can sign malicious updates accepted by every currently-pinned agent; the CA-holder can mint new identities; the operator key is immediate admin. Nothing can invalidate these credentials except physical reflash/re-enroll, which is not documented as a rotation flow.
- User / business impact: one lost microSD, one image copy, or one read of the delivery directory equals fleet-wide compromise and loss of update integrity.
- Security / privacy / reliability impact: root-of-trust disclosure; update supply-chain compromise; no revocation lever.
- Recommended fix: age/gpg-encrypt backups to an owner key and move them out of the delivery surface; exclude secret-bearing files (and their hashes) from the release manifest; remove the `sudo` fallback in the bake; rotate Wi-Fi/host credentials on devices; add CA/seed rotation + agent re-pin procedure and rehearse it.
- Suggested validation: archive unreadable without key; manifest has no secret entries; seed-rotation drill where an old-seed manifest is rejected by a re-pinned test agent.
- Owner suggestion: edge maintainer + owner · Effort: M · Dependencies: key-custody decision · Status: still-open (combines SECRET-P1-001/003, ACM-P2-003, REV-P3-010, INTG-P2-003; chain framing new)

### Finding ID: ADV-P2-001 - Every tunnel peer reaches the host management plane; VPN membership is cheap

- Severity: P2
- Confidence: High (config + code); live nft state unreadable in this role
- Area: ADV (network trust boundary)
- Evidence:
  - `falcon-build/config/nftables/falcon.nft:24` accepts all `iifname "wg0"` traffic *before* the SSH source restrictions `:26-28` and before the enroll/relay rules `:29-32` — first-match accept, so client and sensor peers are exempt from them.
  - `automation/vpn/enroll-service.py:104-111` (one shared token, no throttle), `:136-150` (a token holder replaces a peer by name/key), `:171-175` (0.0.0.0 bind); `docs/runbooks/VPN.md:69-71` client peers are `10.99.0.20/32+` on the same `wg0`.
  - `access_control_matrix.md` rows: CP 9443 reachable from every wg0 peer (ACM-P3-002/INTG-P3-004), enroll 8791 “Traefik front”.
- What is happening: the tunnel is treated as one trusted zone. A weakened client device (or anyone with the shared token) can reach sshd with password auth (EX-01), flood the CP (thread-per-connection), and hit the enrollment service; a sensor peer gets the same surface.
- Why it matters: client devices are the weakest devices in the estate (personal laptops) and are admitted by a shared secret; the ladder’s fourth rung reaches the host plane, not just the fleet API.
- User / business impact: one compromised laptop or leaked token has a direct path into the host management plane.
- Security / privacy / reliability impact: expanded attack surface, DoS, potential credential brute force.
- Recommended fix: replace the blanket wg0 accept with per-port, per-source rules (sensor peers → 9443; client peers → 15140/15141 only; never blanket SSH); separate client VPN from the fleet tunnel or enforce per-peer AllowedIPs/roles; per-client one-time tokens + lock.
- Suggested validation: port scan and SSH attempt from a client peer namespace must fail; sensor flows unaffected.
- Owner suggestion: edge + central maintainers · Effort: S–M · Dependencies: wg peer policy · Status: open (new framing; cross-ref ACM-P2-002, ACM-P3-002, SEC-P2-005)

### Finding ID: ADV-P2-002 - Sensor telemetry is self-attested: one sensor can spoof another sensor's health (reproduced)

- Severity: P2
- Confidence: High (reproduced)
- Area: ADV (monitoring integrity)
- Evidence:
  - `falcon-edge-build/src/falcon_control/service.py:550-581` accepts arbitrary JSON items, checks only count/shape, no lifecycle gate, no comparison of payload identity to the client certificate; spool `:583-599`.
  - `falcon-build/automation/observability/fleet_metrics.py:126-200` reads `sensor_id` and `event_type` from the NDJSON lines and emits `edge_capture_kernel_packets_total`, `edge_capture_kernel_drops_total`, `edge_capture_drop_ratio`, `edge_ids_events_window_total` for that id; run as root by `falcon-edge-metrics.timer`.
  - R4: an enrolled sensor’s cert produced metrics labelled with a different (non-existent) sensor id.
  - Edge alert rules that would consume this (`EdgeSensorSilence`, `QueueLoss`, `QueueBacklog`) are not deployed centrally (XREPO-P1-002).
- What is happening: the ingest endpoint has no object scoping (unlike every other sensor route) and the downstream consumer trusts the payload’s own identity; a REVOKED sensor keeps writing (ACM-P1-002), and any live sensor can write on behalf of another.
- Why it matters: the only cross-fleet detection channel for the attacks above reads attacker-shaped data. An intruder can hide dropped-capture/Suricata silence on a victim sensor or fake activity to defeat silence rules.
- User / business impact: operators cannot trust fleet health signals when a device is compromised.
- Security / privacy / reliability impact: integrity of the monitoring-of-the-monitoring path; false negatives in incident detection.
- Recommended fix: server-assign the sensor id from the certificate for ingest; schema-validate items; add a lifecycle gate; keep at-least-once semantics but record provenance; alert on ingest from unknown/revoked ids.
- Suggested validation: forged `sensor_id` must be ignored or stored under the cert id; metrics labels must match the authenticated sensor.
- Owner suggestion: edge maintainer · Effort: S–M · Dependencies: spool consumers · Status: open (new; cross-ref ACM-P1-002, XREPO-P1-002)

### Finding ID: ADV-P2-003 - The ladder is quiet: the only trace is local audit rows that look normal

- Severity: P2
- Confidence: Medium-High (code + audit rows reproduced; no alerting path found in repo)
- Area: ADV (detection/response)
- Evidence:
  - Audit entries (`store.py:129-133`) for enrollment/renewal record the sensor id and a fingerprint prefix (`service.py:363-364,404-405`); R1’s rows are `sensor.enrolled`, `certificate.renewed`, `bootstrap_token.created` — no CSR subject, no anomaly signal.
  - Edge audit is local SQLite only; no metric/export consumes it; edge alert rules (`edge-alerts.yaml`) are absent from the central stack (XREPO-P1-002) and the fleet metrics exporter is host-only (ND-P2-016).
  - Wazuh authd 1516/1517 is any-source (`31-docker-user-firewall.sh:62-68`) with no throttle/abuse alert recorded (SEC-P2-005); the relay does not log accepted POSTs (`ntfy_relay.py:226-227`) and fails open without a token (`:197-200`).
  - Revocation is state-only (ACM-P1-002): `destroyKeys` inert, REVOKED ingest allowed, no CRL.
- What is happening: the escalation, the forged apply, the metric spoof and authd brute force all land in files/logs that nothing watches and that look like routine activity.
- Why it matters: dwell time is unbounded; response (“revoke the sensor”) under-delivers because revocation does not stop ingest, does not revoke operator/CA/seed, and is not alarmed.
- User / business impact: an incident would likely be discovered by humans late, after fleet impact.
- Security / privacy / reliability impact: detection and response gaps for every chain above.
- Recommended fix: record CSR subjects/policies and actor fingerprints in audit; alert on non-sensor enrollment subjects, operator-cert issuance, update-manifest issuance and apply outcomes; deploy edge alert rules; fail-closed + log relay POSTs; add authd abuse alerts; make revocation effective and alarm on it.
- Suggested validation: repeat R1 against a staging copy with alerting on; alerts must fire and name the actor.
- Owner suggestion: edge maintainer + central owner · Effort: M · Dependencies: XREPO-P1-002, ACM-P1-002 · Status: open (new)

### Finding ID: ADV-P3-001 - No revocation or rotation path for operator identity, CA, or update-signing key

- Severity: P3
- Confidence: Medium (code/process evidence; rotation would be a design exercise)
- Area: ADV (response capability)
- Evidence: `falcon-edge-build/src/falcon_control/pki.py` has no CRL/OCSP/revoke; `service.py:141-142,378-403` only sensor renewal; `automation/validation/renew_operator_cert.py` renews the on-disk operator key locally; `service.py:125-130` signing seed is non-expiring and pinned by agents at enrollment; SECRET-P2-004 (no seed procedure); FLEET-P2-005.
- What is happening: the operator key/cert, CA key and update-signing key have no invalidation path; a forged operator cert (ADV-P1-001) simply ages out in 30 days but can be re-minted indefinitely while the attacker holds the token/mechanics, and a stolen seed is accepted for as long as agents keep their pin.
- Why it matters: incident response for the top of the ladder is undefined; the eventual fix for a seed/CA leak requires re-enrolling the fleet, which is not rehearsed or documented.
- Recommended fix: short-lived operator credentials from a separate path; revocation list/EKU checks; documented + drilled CA/seed rotation with agent re-pin and rollback.
- Suggested validation: revoked identity rejected at the route layer; old-seed manifest rejected after re-pin.
- Owner suggestion: edge maintainer · Effort: M–L · Dependencies: PKI redesign · Status: open (new; cross-ref SECRET-P2-004, FLEET-P2-005)

## Cross-Reference: ADV ↔ Domain

| ADV | Related domain IDs | Relationship |
|---|---|---|
| ADV-P1-001 | ACM-P1-001, SEC-P1-001, REV-P1-004; tail CTR-P1-002/SEC-P1-002/REV-P1-005; tests ACM-P3-001; detection XREPO-P1-002 | Domain found the forgeable CN; this lens reproduced the unmap+reuse mechanism and the fleet-root tail |
| ADV-P1-002 | SECRET-P1-001, SECRET-P1-003, ACM-P2-003, REV-P3-010, INTG-P2-003, INTG-P1-003; SECRET-P2-004 | Domain found the artifacts; this lens states the chain and the missing revocation lever |
| ADV-P2-001 | ACM-P2-002, ACM-P3-002 (INTG-P3-004), SEC-P2-005 | Domain found CP reachability; this lens adds the blanket host-plane accept incl. sshd/enroll |
| ADV-P2-002 | ACM-P1-002, XREPO-P1-002; FLEET/XREPO alert gap | Domain found the ingest lifecycle gap; this lens shows downstream identity spoofing defeats detection |
| ADV-P2-003 | SEC-P2-003, SEC-P2-005, NOTIF-P2-001, XREPO-P1-002, ND-P2-016 | Domain has the pieces; this lens consolidates “would it be noticed?” |
| ADV-P3-001 | SECRET-P2-004, FLEET-P2-005, ACM-P1-002 | Rotation/revocation gap for top-of-ladder identities |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Token → operator → fleet root | P1 | Medium | Critical | ADV-P1-001 (R1) | Subject pinning; separate operator PKI |
| CA/operator/seed exposed in one archive | P1 | Low–Med | Critical | ADV-P1-002 (R5) | Encrypt/relocate; rotate; re-pin flow |
| Tunnel peer reaches host plane | P2 | Medium | High | ADV-P2-001 | Per-port wg0 ACLs; per-client tokens |
| Monitoring spoofed via ingest | P2 | Medium | High | ADV-P2-002 (R4) | Cert-bound ingest identity |
| Chains produce no alert | P2 | High | High | ADV-P2-003 | Audit enrichment + edge alerts |

## Recommendations

### Immediate / Release Blocking
1. ADV-P1-001: pin CSR subjects/policies server-side; add the R1 sequence as a regression test before any new token is minted.
2. ADV-P1-002: get CA/operator/seed out of the delivery surface and off plaintext storage; treat the current material as disclosed and plan rotation/re-pin.

### This Week
3. ADV-P2-001: split the wg0 accept into per-port rules; stop exempting tunnel peers from SSH restrictions.
4. ADV-P2-002: bind ingest identity to the client certificate; gate lifecycle.
5. ADV-P2-003: log/alert the five events that would have caught R1–R3; deploy the existing edge rules.

### This Month
6. ADV-P3-001: design and drill operator/CA/seed rotation + re-pin with rollback.
7. Close the negative-test gaps below in CI so the reproduced attacks cannot return.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `filter="data"` + member-type checks to the apply script | Kills R3 write-through | `falcon-apply-update.sh` | R3 case must be `rejected` |
| Reject non-sensor CSR subjects on enroll/renew | Kills R1 | `service.py`, `pki.py` | R1 must 403 |
| Cert-bound `sensor_id` in ingest | Kills R4 | `service.py`, `fleet_metrics.py` | Forged id ignored |
| Encrypt the secrets backup before it lands in delivery | Removes plaintext CA/seed | `backup_edge_secrets.py` | `tar -tzf` unreadable without key |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Separate operator issuance (CA/EKU) + revocation | P1 | edge maintainer | M | PKI redesign |
| Key-custody redesign (encrypt, relocate, offsite) | P1 | edge + owner | M | key decision |
| Per-port wg0 ACL + client/fleet separation | P2 | central + edge | M | wg peer policy |
| Ingest provenance + lifecycle gate | P2 | edge maintainer | S–M | schema |
| Detection events/metrics for edge ladder actions | P2 | edge maintainer | M | XREPO alert deployment |
| CA/seed rotation + agent re-pin drill | P2 | edge maintainer | L | maintenance window |

## Suggested Tests

- Negative (locks in this lens): `CN=operator` enrollment/renewal rejected or mapped to sensor (R1); forged apply-request and symlink/device tar members rejected (R2/R3); forged ingest `sensor_id` ignored (R4); revoked sensor ingest 403.
- Positive-regression: legitimate sensor enrollment, renewal, operator-token flow, signed update apply/rollback still pass (existing `tests/phase2`, `tests/phase7`).
- Detection and audit: staging repeat of R1–R3 must produce alerts; relay POST without valid token must be logged and rejected; audit rows must include CSR subject/full fingerprint; `collect_ingest` must label metrics from the cert id, not the payload.

## Suggested Documentation Updates

- Edge `docs/security/TRUST_MODEL.md`: the ladder, who may enroll what subject, revocation semantics, seed/CA rotation and re-pin.
- `docs/runbooks/VPN.md` + `falcon.nft` comments: tunnel is not a single trusted zone; per-port policy; WAZUH_INTEGRATION/risk register: authd exposure + credential literals as an attack chain (with API-P0-001).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `update_auto_apply` enabled on the live sensor’s `agent.json`? | Determines whether operator staging executes automatically | Read-only dump of `/etc/falcon-agent/agent.json` on the device |
| Has any delivered image/archive left the host since the bake? | Decides immediate rotation of Wi-Fi/host credentials | Delivery/transfer records; owner statement |
| Is any `CN=operator` cert currently mapped or unmapped in the live DB? | Scope of a potential existing escalation | Read-only census of `sensors.cert_fingerprint` vs CSR subjects (issuance log) |

## Appendix

- Sandboxes: `/tmp/opencode/adv-sandbox/` — `repro1_operator_escalation.py` (R1), `repro2_update_apply.sh` (R2/R3), `repro4_ingest_spoof.py` (R4). No repo file, ledger, gate, live system or device was modified; only loopback HTTP in temp dirs and read-only file listings were used. R2/R3 ran the real apply script as an unprivileged sandbox user with `AGENT_STATE`/`SRC_DIR`/`SYSTEMCTL` overrides; its production user is root, which only widens the impact of the same logic.
- Redaction and binding: no secret values printed (archive members, permissions, lengths only); the Wazuh key literals in `ossec.conf` were counted/length-checked, not displayed (API-P0-001/EVID-P1-004). Line references are at `falcon-build @ 8282d3f` / `falcon-edge-build @ 45dfed0` as recorded in the wave-1 reports; the edge repo advanced to `f1c5def` (CI-only) during the run and the audited logic was unchanged.
