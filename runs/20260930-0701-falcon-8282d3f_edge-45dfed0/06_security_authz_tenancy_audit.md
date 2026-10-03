# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (full-domain)
- Repositories: `falcon-build` @ `8282d3f` (main, clean) · `falcon-edge-build` @ `45dfed0` (main, dirty — in-flight CI work)
- Generated at: 2026-09-30T07:40Z · Auditor: repo-deep-dive wave-1 subagent (prompts 06 + 24) · Area code: SEC
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/06_security_authz_tenancy_audit.md`
- Scope limitations: read-only account (no root/docker/wg/nft); live firewall/iptables/Docker/WireGuard state not directly readable; private-repo CI not independently verifiable; no destructive tests; edge repo dirty (uncommitted files assessed as working tree)

## Scope

Reviewed: edge control-plane authn/authz (mTLS, roles, enrollment/renewal, tokens, revocation), agent/collector trust boundaries, central host exposure (nftables + DOCKER-USER), Traefik/ntfy/Grafana/OpenSearch/Wazuh access paths, WireGuard and client-VPN enrollment, secret handling and delivery artifacts, CI secret scanning in both repos, and the four lead-listed prior findings at current commits. Not reviewed: upstream product internals; out-of-repo Cloudflare config; kernel/container escape; the physical Pi filesystem; tenancy (single owner/site — prompt 25 N/A).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `falcon-edge-build/src/falcon_control/service.py` | code | Identity, routing, enroll/renew/revoke/ingest | `_resolve_identity` :196-203; issue_cert :333,:399; ingest :550-581 |
| `falcon-edge-build/src/falcon_control/{pki,http_server}.py` | code | CA issuance, TLS, peer CN/fingerprint | One CA; CERT_OPTIONAL; CSR signed verbatim :30-59 |
| `falcon-edge-build/src/falcon_common/x509tools.py`, `src/falcon_agent/{client,identity}.py`; `deploy/falcon-update-apply.*`, `image/overlay/usr/local/sbin/falcon-apply-update.sh` | code | Client TLS; device key modes; root update path | `check_hostname=False` :112; key 0640 :44,:66; request/digest/`extractall` apply script |
| `falcon-build/bootstrap/31-docker-user-firewall.sh`, `config/nftables/falcon.nft` | config | Docker-published port policy | 1516/1517 any-source :62-68 |
| `falcon-build/automation/vpn/enroll-service.py`; `automation/evidence/capture.sh`; `/home/user/.env` (path/type only) | code/host | Enrollment; secret handling | Shared token/keygen; `set -a; . .env` :69-72 |
| Both `.gitleaks.toml`, both CI workflows, `ci/secret_scan.py` | CI | Secret-scan claims | gitleaks `--no-git`; allowlists; CLI behavior |
| `live_snapshot.txt` (07:01:55Z) + read-only probes; prior-run `findings.json` | live/records | Exposure + prior verification | 9443/8791/2586/9099 probes; cert SANs; fail2ban |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse/status` both repos; `git diff --stat 2b5bc8b 45dfed0` on finding paths | repo state/diff | Binding; remediation check | central clean; edge 4 modified + 2 untracked CI files; audited logic unchanged → still-open |
| `FALCON_EVIDENCE_OPTIONAL=1 python3 -B ci/validate.py` | validation | Central gate claim | `validation_failures=0` (461 captures; secret scan PASS) |
| `python3 -B ci/secret_scan.py` (edge) | validation | Edge gate claim | PASS 891 files, no findings |
| `systemctl cat/show`; `/etc/fail2ban/jail.local`; read-only DB query (`mode=ro&immutable=1`) | live config/data | Runtime binding; lifecycle state | Units match repo; fail2ban 5→1h; 1 ACTIVE / 5 RETIRED / 3 REVOKED; 22 tokens (13 unredeemed, 3 expired); 15/15 directives expired; 4664 audit rows |

## Prior-Run Findings Verification

Prior run `20260930-0320-falcon-794ba31_edge-2b5bc8b`; status at 8282d3f/45dfed0:

| Prior ID | Status | Evidence |
|---|---|---|
| REV-P1-004 (enrollment→operator) | **still-open** | `service.py:196-203` CN→operator; `pki.py:30-59` signs CSRs; :333/:399; no diff in audited paths |
| REV-P1-005 (update-apply root trust) | **still-open** | Apply script byte-identical 2b5bc8b→45dfed0; request path :37-43; self-digest :67-71; `extractall` :80 |
| REV-P2-007 (no hostname verify; one CA) | **still-open** | `x509tools.py:112` unconditional `check_hostname=False`; no `server_hostname`; same CA for all certs |
| LIVE-P2-005 (cleartext `.env`) | **still-open** | `.env` present 0600 with sudo+third-party keys; source wholesale (`capture.sh:69-72` et al.) |

No regression introduced; all four are restated below as current-commit findings.

## Executive Summary

Posture is above average for a single-owner lab: default-deny nftables; DOCKER-USER guard for published ports; pinned images/actions; root-only secret dirs; hardened units; single-use expiring tokens; mTLS on the edge path; secret-scan gates in both repos (central `validate.py` passes at HEAD; edge working-tree scan clean). The material risks: (1) operator authority is a forgeable certificate subject mintable at enrollment (SEC-P1-001); (2) the root update path trusts agent-writable input (SEC-P1-002); (3) revocation is state-only and inconsistently enforced (SEC-P2-003); (4) fleet key material sits in unencrypted backups and in a parser-facing collector (SEC-P2-004); (5) standing public enrollment surfaces and an out-of-repo Access policy carry the public exposure (SEC-P2-005). Recommended: fix identity substance and revocation first, then key custody and exposure. Prior-run status: four lead-listed findings still-open, none fixed or regressed.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| CP identity resolver | `service.py:196` `_resolve_identity` | Cert → role | Implemented | **High** | CN string → operator |
| Root update apply | `falcon-apply-update.sh` | Apply bundle as root | Implemented | **High** | Trusts agent-written request |
| Agent TLS client | `client.py`, `x509tools.py` | mTLS to CP | Implemented | Medium | No hostname check |
| Sensor identity files | `identity.py` | Key/cert/CA/signing pin | Implemented | Medium | Key 0640 for Vector |
| Revocation | `service.py` revoke/`_config_blocked` | Quarantine/revoke | Partial | Medium | Ingest exempt; `destroyKeys` inert |
| Secrets backup | `backup_edge_secrets.py` | Daily archive | Implemented (plain) | Medium | Unencrypted; manifest omission |
| Host firewall / Docker guard | `falcon.nft`, `31-docker-user-firewall.sh` | Network access control | Implemented | Medium | 1516/1517 any-source; live state unreadable |
| Owner credentials | `/home/user/.env` (type only) | Sudo + third-party keys | Implemented | **High** | Cleartext; sourced into captures |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 2 | mTLS + bearer enroll | Role from CN | Separate operator path |
| Session tokens/cookies | 3 | `tokens.py` | No prune/throttle | Prune job; enroll throttle |
| JWT validation | N/A | No JWT (Ed25519 signed JSON) | — | — |
| CSRF/CORS | N/A | No browser session API | — | — |
| Rate limits | 2 | ntfy limits; SSH 30/min + fail2ban | CP/enroll/Wazuh unthrottled | Per-source throttles |
| Security headers | 3 | Traefik `sec-headers` | Traefik routes only | CSP review |
| Input/output validation | 3 | Schema validators; body/ingest caps | CSR subject; tar filter | Subject pinning; `filter="data"` |
| File handling | 2 | Bundle digest/compile/rollback | Symlink traversal; self-digest | SEC-P1-002 fix |
| API permissions | 2 | Route roles; sensor-id match | Ingest bypasses lifecycle | SEC-P2-003 fix |
| Admin permissions | 3 | Operator routes; audit | Role forgeable | SEC-P1-001 fix |
| Tenant/org/workspace isolation | N/A | Single owner/site (prompt 25 N/A) | — | — |
| RLS policies | N/A | OpenSearch roles only (`60-central-deploy.sh:119-190`) | — | Keep role review |

## Detailed Review

### Item: Edge control-plane identity, authorization, and lifecycle

- Evidence: `service.py:137-235` (routes/authz), `:196-203` (identity), `:550-581` (ingest); `pki.py:30-80`; tests `tests/phase2/test_service_integration.py:340-354`.
- What it does / controls: CERT_OPTIONAL TLS; fingerprint→sensor else CN→operator; per-route roles; path sensor must match cert or quarantine+audit; all state changes audited (4,664 rows); token hygiene, body caps, TLS ≥1.2.
- Missing controls: subject pinning, separate operator chain, uniform lifecycle checks, rate limiting.
- Risks/improvements: SEC-P1-001; SEC-P2-003; forbidden-access tests; trust-model doc.

### Item: Agent trust, privileged apply, and key custody

- Evidence: `x509tools.py:93-113`, `client.py:33-76`, `runner.py:444-519`, apply script/unit, `identity.py`, backup/manifest helpers, delivery listing.
- What it does / controls: agent key (0640), token enroll, pinned signing key, signature-verified directives/manifests, root apply with digest/compile/rollback; root timer backs up secrets; hardened units.
- Missing controls: hostname verification, root-side update anchor, safe tar filter, backup encryption, collector key separation.
- Risks/improvements: SEC-P1-002; SEC-P2-001/004; SAN+hostname check; encrypted backups; Vector separate cert.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity |
|---|---|---|---|---|---|
| SEC-001 | Auth provider | `service.py:196` | mTLS + token enroll | Role from CN | P1 |
| SEC-005 | Rate limits | ntfy; fail2ban | Partial | CP/enroll/Wazuh unthrottled | P2 |
| SEC-007 | Input/output validation | schema validators | Caps + schemas | CSR subject | P1 |
| SEC-008 | File handling | apply script | Digest/compile/rollback | Traversal; self-digest | P1 |
| SEC-009 | API permissions | `service.py:137-235` | Route roles + path match | Ingest lifecycle | P2 |
| SEC-010 | Admin permissions | CLI + operator cert | Audit | Forgeable | P1 |

Notes: SEC-003/004 (JWT, CSRF/CORS) and SEC-011/012 (tenancy, RLS) are N/A — no JWT/browser-session surface, single owner/site, and OpenSearch role policies are the only DB-level layer.

## Findings

### Finding ID: SEC-P1-001 - Enrollment signs attacker-supplied CSR subjects; operator role resolves from the CN string (REV-P1-004 still-open)

- Severity: P1
- Confidence: High
- Area: SEC (edge identity)
- Evidence:
  - `falcon-edge-build/src/falcon_control/service.py:196-203` (CN=operator → operator), `:333,:399` (enroll/renew sign `data["csrPem"]`); `pki.py:30-59,73-80` (verbatim signing; same CA); no CSR-subject test in `tests/phase2/test_service_integration.py:340-354`.
- What is happening: a token holder submits `CN=operator`; the service signs it; after fingerprint unmapping it authenticates as operator.
- Why it matters: privilege escalation from device holder to fleet operator via a forgeable identifier, not an unforgeable credential. Business impact: leaked pre-baked claim token (image/CI) becomes fleet control.
- Security / privacy / reliability impact: root-of-authority bypass; token/update/directive issuance, quarantine/revoke, fleet reads.
- Recommended fix: server-pinned subjects (ignore CSR subject); separate operator issuance path (CA or EKU/policy); negative tests; reopen affected gate evidence.
- Suggested validation: `CN=operator` CSR rejected/mapped to sensor; operator flow still works via the separate path.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: PKI change → gate records
- Status: still-open (carried from REV-P1-004; unchanged 2b5bc8b→45dfed0)

### Finding ID: SEC-P1-002 - Root update-apply trusts an agent-writable request file (REV-P1-005 still-open)

- Severity: P1
- Confidence: High
- Area: SEC (privileged input)
- Evidence:
  - `falcon-edge-build/deploy/falcon-update-apply.path:7` (watches agent-written `apply-request.json`; written by `runner.py:494-516`); `falcon-apply-update.sh:37-45` (`path`/`sha256` from request), `:67-71` (digest vs same request), `:77-80` (name check; default-filter `extractall`), `:90-96` (root swap).
- What is happening: the root transaction's inputs are controlled by the unprivileged agent; signed-manifest verification happens agent-side only; archive handling remains symlink-traversable.
- Why it matters: any agent compromise yields root code execution on the sensor; fleet-wide if an update is broadly deployed. Business impact: full device compromise.
- Security / privacy / reliability impact: root RCE; update-integrity bypass.
- Recommended fix: root-owned digest/manifest; constrain `path`; `extractall(filter="data")` + member-type checks; forged-request/symlink negative tests.
- Suggested validation: forged request and symlink bundle rejected; legitimate drill still applies/rolls back.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: update-flow redesign; risk entry
- Status: still-open (carried from REV-P1-005; script identical)

### Finding ID: SEC-P2-001 - Agent never verifies the control-plane hostname; one CA issues all identities (REV-P2-007 still-open)

- Severity: P2
- Confidence: High
- Area: SEC (transport trust)
- Evidence:
  - `falcon-edge-build/src/falcon_common/x509tools.py:112` (`check_hostname=False` unconditionally); `src/falcon_agent/client.py:33-56` (no `server_hostname`); `pki.py:10` (single CA); live certs: server SANs incl. `10.99.0.1`, operator+server same issuer.
- What is happening: the chain is verified but not the server identity; any CA-issued cert (e.g. a sensor cert) is accepted as the control plane.
- Why it matters: an on-path attacker with any CA cert can impersonate the CP (signature checks on payloads limit but do not remove the impact). Business impact: fleet telemetry/directive trust weakens to one CA.
- Security / privacy / reliability impact: MITM; false state/update offers.
- Recommended fix: enable hostname checks and SANs (live cert already covers the tunnel IP; add it to `deploy/edge-control-plane.lab.json` `server_hostnames`); separate role CAs/EKUs; document trust model.
- Suggested validation: wrong-CN/SAN server cert rejected; tunnel-IP connection still works.
- Owner suggestion: edge maintainer · Effort: S–M · Dependencies: SAN config
- Status: still-open (carried from REV-P2-007)

### Finding ID: SEC-P2-002 - Owner credential file stays cleartext and is sourced into capture environments (LIVE-P2-005 + REV-P3-011 still-open)

- Severity: P2
- Confidence: High
- Area: SEC (secret handling)
- Evidence:
  - `/home/user/.env` mode 0600 owner `user`; keys (type only, values redacted): `sudo`, `gh_api`, DO/S3/R2, Cloudflare, ntfy, UniFi, WiFi. `automation/evidence/capture.sh:69-72` `set -a; .` exports all of it into every `--sudo` capture env; redaction `:40-47` misses cloud keys; same pattern in `alert_storm_test.sh:12`, `restore_rehearsal.sh:10`, `ntfy_sh_alert_test.sh:11`, `spaces_probe.sh:7`, `host_oom_check.sh:15`, `97-cloudflare-api-config.sh:21`.
- What is happening: one file mixes sudo and third-party credentials and is loaded wholesale wherever sudo is needed.
- Why it matters: single-file compromise grants sudo + cloud/API/ZT tokens; captures can leak unredacted values. Business impact: lab root + third-party accounts.
- Security / privacy / reliability impact: credential blast radius; evidence-publication risk.
- Recommended fix: split per-consumer files; pass only `sudo` to capture; extend redaction; rotate exposed keys; document in rotation runbook.
- Suggested validation: `capture.sh --sudo env` shows no third-party keys; evidence grep clean.
- Owner suggestion: owner + build agent · Effort: M · Dependencies: rotation plan
- Status: still-open (carried from LIVE-P2-005/REV-P3-011)

### Finding ID: SEC-P2-003 - Revocation is state-only: revoked certs can still ingest, `destroyKeys` is inert, RETIRED sensors can renew

- Severity: P2
- Confidence: High
- Area: SEC (lifecycle authorization)
- Evidence:
  - `falcon-edge-build/src/falcon_control/service.py:550-581` (`h_ingest_vector` has no lifecycle check; unlike :439/:498/:536/:606); `:196-203` (REVOKED fingerprints still resolve); `:759-770` (`destroyKeys` audited, not implemented); `:388-390` (renewal rejects REVOKED only); `retire_stale_sensors.py` sets RETIRED; live DB: 3 REVOKED, 5 RETIRED rows.
- What is happening: lifecycle enforcement is duplicated per handler and drifted; no CRL/OCSP exists.
- Why it matters: stolen/revoked sensors keep injecting data; retirement does not stop renewal. Business impact: telemetry integrity and audit inconsistency.
- Security / privacy / reliability impact: residual trust after revoke; documented capability not delivered.
- Recommended fix: single fail-closed lifecycle gate (incl. ingest); RETIRED non-renewable; implement or remove `destroyKeys`; regression tests.
- Suggested validation: REVOKED → 403 on every sensor route; RETIRED renewal 403; destroy semantics verified.
- Owner suggestion: edge maintainer · Effort: S–M · Dependencies: API/doc wording
- Status: open (new; revocation/lifecycle gap)

### Finding ID: SEC-P2-004 - Fleet key material is unencrypted in the delivery surface, incompletely manifest-covered, and exposed to the collector boundary

- Severity: P2
- Confidence: High
- Area: SEC (key custody)
- Evidence:
  - `backup_edge_secrets.py:43-52` — plain `tar.gz` (CA key, `signing.seed`, operator/server keys, control-plane DB) into `/home/user/falcon-edge-delivery`; listing shows root-owned archive too. `build_release_manifest.py:48-61` skips unreadable files → manifest (42 entries, commit 155f244) omits the root-owned `.tar.gz` (recorded in `closeout/REVIEW-2026-09-30.md:219`).
  - `src/falcon_agent/identity.py:44,66,79` — device key/cert 0640 "group-read for sibling collectors (Vector)"; `profiles/sensor/vector/edge.toml:53-54` reads `device.key.pem`; `docs/phase0/TRUST_BOUNDARIES.md` row 2 claims least-privilege collectors.
- What is happening: one directory copy yields CA+signing+operator authority; the signed manifest is not complete for the newest backup; the parser-facing collector holds the sensor mTLS key.
- Why it matters: fleet identity forgery and operator impersonation from artifact exposure; a Vector compromise yields a sensor identity.
- Security / privacy / reliability impact: root-of-trust exposure; second key holder outside the hardened agent.
- Recommended fix: encrypt backups (owner key) or move them out of the delivery tree; manifest fail-closed; relay telemetry via the agent or issue Vector a separate restricted cert; document residual if kept.
- Suggested validation: archive unreadable without key; manifest covers 100% or fails; key removed from Vector's reach with delivery unaffected.
- Owner suggestion: edge maintainer + owner · Effort: S–M · Dependencies: encryption decision
- Status: still-open (REV-P3-010/INTG-P2-003; Vector variant new)

### Finding ID: SEC-P2-005 - Public enrollment surfaces: Wazuh 1516/1517 open to any source; client-VPN enrollment is token-shared and unthrottled

- Severity: P2
- Confidence: Medium (repo + listeners; live firewall unreadable)
- Area: SEC (public exposure/enrollment)
- Evidence:
  - `falcon-build/bootstrap/31-docker-user-firewall.sh:62-68` — any-source RETURN for original dport 1516/1517; `WAZUH_INTEGRATION.md:87-100` — public `142.105.190.25:1516/1517`, password-protected authd, no throttle recorded; live `0.0.0.0:1516/1517`; retirement path in `VPN.md:94`; `automation/vpn/enroll-service.py:104-111` (one shared token, no rate limit), `:136-150` (peer by name replaced; unlocked read-modify-write), `:116-126,:163-165` (server-generated private key), `dynamic.yml:111-117` (no auth middleware); public dashboards rely on out-of-repo Cloudflare Access (`MCT_CONSOLIDATION.md:70-79`; R-15 open; `ACCESS_AND_ACCOUNTS.md:55-67`).
- What is happening: standing internet-reachable enrollment endpoints are protected by password/shared token only; the repo cannot prove the public-policy controls.
- Why it matters: brute force/DoS on authd; token loss = tunnel membership and peer shadowing; policy drift could expose dashboards. Business impact: availability and network membership integrity.
- Security / privacy / reliability impact: exposed auth endpoints without throttling; external control unverifiable.
- Recommended fix: remove the public Wazuh forwards after VPN migration + add authd abuse alerting; per-client one-time VPN tokens, name binding, lock, throttles, deprecate keygen; add Traefik rate-limit middleware and record Access policy in-repo.
- Suggested validation: external 1516/1517 blocked; concurrent/duplicate enrollments rejected; burst throttled; anonymous request → Access redirect.
- Owner suggestion: owner + build agent · Effort: M · Dependencies: VPN onboarding; Cloudflare account
- Status: open (new; exposure carried from INTG-P3-004)

### Finding ID: SEC-P3-001 - CI secret-gate integrity: scanner invocation/allowlists, un-evidenced gitleaks run, and secret interpolation

- Severity: P3
- Confidence: High
- Area: SEC (CI secret scanning)
- Evidence:
  - `falcon-build/automation/validation/secret_scan.py` treats unknown args as paths (`--help` → exit 0 "NO_FINDINGS", reproduced); `.gitleaks.toml:18-22,39-41` allowlists curl-shaped lines and the whole `review-package/` copy; both CI workflows run `gitleaks --no-git`. `falcon-edge-build` gitleaks gate added at `824f701` (06:34Z); last captured CI evidence `evidence/raw/REVIEW-FIX/20260930T061913Z_github-actions-runs.out` predates it (latest success `155f2446`); `docs/GITHUB_CI.md:150-169` claims "live and green"; private repo (API 404) → not independently verifiable; working tree dirty. `bake-image.yml:92-95` interpolates `${{ secrets.* }}` into a `run:` script while `docs/GITHUB_CI.md:117-119` claims env-only handling (inputs only).
- What is happening: scanning exists and works for the common cases, but specific invocation/allowlist/CI-evidence choices can hide classes of findings or present unevidenced green.
- Why it matters: false green on secrets/history/curl-shaped lines; gate claims outrun captured evidence. Business impact: low today; review integrity.
- Security / privacy / reliability impact: secret-scan assurance is narrower than it appears.
- Recommended fix: fail on unknown CLI args; narrow allowlists; scan the review package with awareness; capture post-push gitleaks/validate evidence and index it; pass secrets via `env:`; update the doc claim.
- Suggested validation: `--bogus` exits non-zero; synthetic history secret caught; indexed run evidence shows gitleaks green at the pushed commit.
- Owner suggestion: platform + edge maintainers · Effort: S · Dependencies: push of in-flight CI work
- Status: open (new; evidence/robustness)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Operator role forgery | P1 | Medium | Fleet control | SEC-P1-001 | Separate issuance; pin subjects |
| Root RCE via update request | P1 | Low–Med | Device/fleet | SEC-P1-002 | Root-side verification; safe extract |
| Revocation ineffective | P2 | Medium | Telemetry integrity | SEC-P2-003 | Central lifecycle gate; CRL/destroy |
| Key material exposure | P2 | Low | CA/signing/operator forgery | SEC-P2-004 | Encrypt; fail-closed manifest; separate cert |

## Recommendations

### Immediate / Release Blocking
1. SEC-P1-001: pin CSR subjects; remove CN-based operator resolution before minting new tokens.
2. SEC-P1-002: root-side verification + `filter="data"` in the apply path.

### This Week
3. SEC-P2-003: lifecycle gate on ingest; RETIRED renewal denied; `destroyKeys` decision; forbidden-access tests.
4. SEC-P2-001: enable hostname verification + SAN config.
5. SEC-P2-002: split `.env`; stop wholesale sourcing in captures; rotate exposed keys.

### This Month
6. SEC-P2-004: encrypt/relocate backups; manifest fail-closed; separate Vector cert or relay via agent.
7. SEC-P2-005: VPN-migrate Wazuh roaming; per-client enrollment tokens; rate limits + Access policy record.

### Later / Platform Evolution
8. IdP/Cloudflare Access with per-person identity for public UIs (R-15); per-source CP throttling.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Hostname check + SAN config | Removes MITM class | `x509tools.py`, `client.py`, CP config | Wrong-SAN cert rejected |
| Ingest lifecycle check | Blocks revoked injection | `service.py` | Revoked → 403 |
| `argparse` in secret scanner | No false green | `secret_scan.py` | `--bogus` exits 2 |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Operator identity redesign (CA/EKU) | P1 | edge maintainer | M | gate records |
| Revocation design (CRL/deny list/destroy) | P1 | edge maintainer | M | PKI |
| Encrypted backups + key custody | P2 | owner | S–M | decision |
| Per-client VPN tokens + lock/limits | P2 | build agent | M | endpoint scripts |

## Suggested Tests

- Security/negative: `CN=operator` CSR rejected; revoked sensor ingest → 403; RETIRED renewal → 403; forged/symlink update bundles rejected; wrong-SAN server cert rejected; concurrent enrollments get distinct IPs.
- CI: `secret_scan.py --bogus` non-zero; synthetic secret fixture fails gitleaks; pinned actions resolve; update drill still applies/rolls back.
- Manual (owner): external 1516/1517 probe blocked after VPN migration; manifest verifies with all files readable.

## Suggested Documentation Updates

- Edge `docs/security/`: trust model (CA roles, SAN/hostname policy, Vector key decision, revocation semantics).
- `docs/GITHUB_CI.md`: scope the env-only claim; bind gitleaks/validate evidence; note `--no-git`.
- `docs/runbooks/ACCESS_AND_ACCOUNTS.md`: `.env` split status; enrollment exposure notes; `WAZUH_INTEGRATION.md`/`VPN.md` + both risk registers: removal trigger for public forwards; proposed entries for SEC-P1-001/002 and key-custody exposure.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is live DOCKER-USER in closed mode with the repo allowlist? | Actual exposure | Root capture of `iptables -S DOCKER-USER` + mode file |
| Are any `CN=operator` CSRs already issued live? | Escalation may exist | CSR/cert inventory + enrollment audit review |

## Appendix

- Read-only DB query used `file:...?mode=ro&immutable=1` (no writes/locks); probes: healthz 200, `/sensors` 403, enroll health public, relay GET public/POST token-gated; role/route/key matrices in `access_control_matrix.md`; no secret values printed.
