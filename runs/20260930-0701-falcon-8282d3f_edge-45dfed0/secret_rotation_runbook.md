# Secret Rotation Runbook (Recommended)

Audit artifact produced by prompt 38 of run `20260930-0701-falcon-8282d3f_edge-45dfed0`.
This is a **recommended** procedure assembled from repository evidence and the live state; it is
**not** execution evidence, and no credential was rotated during the audit. Executed items already
on record are marked `EXERCISED`; everything else is `PROPOSED`. Owners should adopt it via the
normal decision-log flow (`ledgers/decision_log.md` is proposed, never edited by the audit).

## Audit Metadata

- Audit name: repo-deep-dive · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repos: `falcon-build` @ `8282d3f` · `falcon-edge-build` @ `f1c5def`
- Scope: central host service secrets, `.env`-class stores, edge PKI/signing material, sensor
  image/device credentials, delivery backups, legacy Wazuh/MCT stores
- Redaction rule: never print or paste values. Track fingerprints/dates/artifacts only.

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| `falcon-build/docs/phase7/runbooks/CERTIFICATE_AND_SECRET_ROTATION.md` | runbook | Central classes, dependents, DN warning, §11 status |
| `falcon-build/bootstrap/50-secrets.sh` | generator | Generation, permissions, idempotent `central.env` |
| `falcon-build/bootstrap/{60,70,80,90,95}-*.sh` | consumers | How secrets reach services (incl. whole-file export) |
| `falcon-build/evidence/raw/P7-G01/20260921T020201Z_phase7-security-checks.out:44-48` | evidence | Executed rotation example (vector ingest; old = 401) |
| `falcon-build/docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md:20,27` | governance | OD-17/OD-18 accepted (cadence/on-call) |
| `falcon-edge-build/docs/runbooks/certificate-renewal-revocation.md` + gate `P8-G04` | runbook/ledger | Executed sensor cert renewal/revocation |
| `falcon-edge-build/automation/validation/backup_edge_secrets.py` + delivery archives | code/artifact | Backup contents, perms, retention, gap |
| `falcon-edge-build/automation/validation/build_release_manifest.py` | code | Secret-bearing files in release surface |
| `falcon-edge-build/automation/validation/bake_lab_test_image.sh:52-54,109-118` | code | Baked Wi-Fi PSK / host-credential device password |
| `mct/runbooks/{credential-rotation-checklist,phase10-credential-rotation}.md` | runbook | Legacy store priority order; all PENDING |
| `docs/phase0/OWNER_DECISIONS.json` (OD-04/17/18) | governance | Pending/contradiction status |

## Verification Performed

| Check | Result | Note |
|---|---|---|
| Read runbooks/evidence above | supported | Extracted only steps already present in repo |
| Store permission census (`stat`) | reproduced | `.env` 0600 user; `/opt/…` 0600 user; delivery 0600 user/root; `/srv/falcon/secrets` 0700 root (unreadable) |
| Backup archive member listing | reproduced | CA key, signing seed, server/operator keys, DB (names only) |
| Rotation evidence inventory | supported | 1 central service credential + edge cert auto-renewal executed; rest untested/PENDING |
| Value comparison (ntfy keys) | reproduced | duplicates differ; no values printed |
| Live rotations | not performed | Audit is read-only and non-destructive |

## 1. Inventory and rotation map

| # | Secret class | Store (owner, mode) | Consumers | Rotation method (evidence-backed where noted) | Status |
|---|---|---|---|---|---|
| 1 | Host sudo password | `/home/user/.env` key `sudo` (user 0600) | capture wrapper, offsite backup, image bake | `passwd`; update `.env`; re-check `sudo -v` | PROPOSED |
| 2 | Third-party API keys | `/home/user/.env` (`prox_key`, `cf_*`, `do_*`, `s3_*`, `gh_api`, `unifi_admin`, `wifi_*`) | offsite backup, cloudflared, firewall/network tooling | Console-side regeneration; update `.env`; verify each consumer | PROPOSED |
| 3 | ntfy topic/user | `/home/user/.env` (`NTFY_TOPIC`, `ntfy_user_pass`) + `/srv/falcon/secrets/ntfy_topic` (root) | alert relay, provisioners | Canonicalize to one key first; self-hosted ntfy topic rotate + re-deliver | PARTIAL (2026-09-22/23 rotations recorded) |
| 4 | OpenSearch service users | `/srv/falcon/secrets/{opensearch_admin,pw…,central.env}` (root 0700/0600) | opensearch, dashboards, vector aggregator/edge, backup | Edit value + re-run `60-central-deploy.sh` / `70-probe-deploy.sh`; negative test | PROPOSED |
| 5 | Vector ingest/writer | same as #4 | pipeline | same; **precedent**: P7-G04 vector-ingest rotation with 401 | EXERCISED (2026-09-21) |
| 6 | Grafana admin | `/srv/falcon/secrets/grafana_admin.pw` + `grafana.env` | grafana | `grafana cli admin reset-admin-password`, reconcile via deploy script | PARTIAL (Phase 2) |
| 7 | Traefik basic-auth files | `/srv/falcon/secrets/{ntfy,ntop}_htpasswd` (root 0640) | traefik | Regenerate APR1, write in place (inode cache), restart Traefik | PARTIAL (ntop/ntfy split + rotation 2026-09-23) |
| 8 | Redis password | `/srv/falcon/secrets/redis_pw` + Docker secret | redis, ntopng | Replace file, recreate container, negative test | PROPOSED |
| 9 | Lab CA + server/OS certs | `/srv/falcon/secrets/tls/` (root 0700) | traefik, opensearch, dashboards, vector | Runbook §4.2 (manual re-issue); OS admin DN order warning is load-bearing | PROPOSED (mostly untested) |
| 10 | Edge CA + server/operator certs | `/home/user/falcon-edge-secrets/{ca,operator.*,server.*}` (0700 user) | edge control plane, operator CLI | Re-issue per edge runbooks; operator cert timer exists | PARTIAL (sensor auto-renew EXERCISED 2026-09-30) |
| 11 | Edge signing seed | `/home/user/falcon-edge-secrets/signing.seed` (0600 user) | signs update/release manifests | **No procedure exists** — add re-sign + fleet re-trust + rollback; see §5 | PROPOSED |
| 12 | Sensor claim/bootstrap tokens | control-plane DB (SHA-256 hashes), device claim file (0600, shredded) | enrollment | Single-use, 7-day expiry; re-mint per device; no rotation needed if unredeemed | EXERCISED (enrollment flow) |
| 13 | Sensor image/device credentials | `/home/user/falcon-edge-delivery/*-credentials.txt`, `*-ssh-key`, baked Wi-Fi/account | lab devices | Generate per-device random password + per-device Wi-Fi credential; change after flash | PROPOSED (currently host sudo + shared PSK) |
| 14 | Edge secret backups | delivery `falcon-edge-secrets-backup-*.tar.gz` | restore | Encrypt + relocate to root custody + offsite; exclude from release manifest | PROPOSED (unencrypted today) |
| 15 | Legacy Wazuh/MCT stores | `/opt/wazuh-docker/multi-node/{.env,ops/creds.env,…}` (0600 user), `wazuh-local.env` (root) | Wazuh, IRIS integration, DO Spaces backups | MCT priority order: DO Spaces → Wazuh admin → Cloudflare → indexer/dashboard → IRIS/MISP/Shuffle | PROPOSED (all PENDING) |

## 2. Cadence, triggers, and owners

- Cadence is owner-gated (OD-18 accepted 2026-09-22: monthly patch window; ad-hoc critical). Use
  that window for rotation; keep a dated entry per credential in the runbook/register.
- Rotate immediately (break-glass) when: an artifact is redacted into evidence; a credential is
  pasted into chat/terminal/scan output; a device/image is lost; a delivery copy leaves the host;
  an operator leaves/roles change.
- Suggested review cadence: quarterly for the `.env` third-party keys, annual for PKI and the
  signing seed, per-device for image credentials.
- Rule: validate the new credential **before** revoking the old one; keep the overlap as short as
  the consumer allows.

## 3. Standard procedure (per credential)

1. Record: credential ID, owner, consumer list, current fingerprint/date, reason.
2. Archive the outgoing material into a root-only 0700 directory outside Git (e.g.
   `/srv/falcon/secrets/rotation-archive/<UTC>/`); never copy values into evidence.
3. Issue/generate the new value (`openssl rand` for lab-generated; console/UI for third-party).
4. Update the store (`central.env`/`.env`/secret file) — **write files in place** where Traefik
   caches them.
5. Apply: re-run the deploy script or restart the consumer; capture the command via the evidence
   wrapper (`automation/evidence/capture.sh`) with fingerprints only.
6. Negative test: prove the old value fails (401/403) and the pipeline/service stays healthy.
7. Record status (date, artifact, affected consumers) and destroy the overlap copy.
8. If anything was exposed (image, evidence, chat), treat the old value as disclosed and complete
   the consumer audit.

## 4. Class-specific notes

### 4.1 Central service secrets and PKI

- Follow `CERTIFICATE_AND_SECRET_ROTATION.md` §3 (dependents) and §4 (commands); do not improvise
  the OpenSearch admin DN (`CN=kirk,OU=client,O=client,L=test,C=de`) — wrong order silently drops
  admin rights.
- Vector 0.58 does not interpolate env vars in rendered configs: re-run both deploy scripts after
  ingest/writer rotations, then verify ingestion on 514/15140/TLS paths.
- Update runbook §11 after the first successful rotation of each class; resolve the internal
  contradiction it currently carries (vector rotation listed as both executed and untested).

### 4.2 Owner `.env` and root-run tooling

- Before rotating anything, split the file by purpose and remove the duplicate `ntfy_topic` keys;
  make root scripts pass only the variable they need instead of `set -a; . /home/user/.env`.
- Rotating `sudo` implies re-baking lab images or changing device passwords; sequence carefully.
- The offsite backup job consumes R2/S3 keys: rotate one side at a time and re-run a small
  upload/read-back before pruning.

### 4.3 Edge PKI, signing seed, and backups

- Sensor cert renewal/revocation is automated and exercised (`P8-G04`): use
  `falcon deploy edge` commands from `certificate-renewal-revocation.md`.
- Add a signing-seed procedure: generate a new seed, re-sign the release/update manifests, roll
  out trust (devices verify against the new public key), verify one device update, then retire the
  old seed. Until this exists, treat seed compromise as a full-fleet event.
- Backups: encrypt before writing (owner public key), write to root-only custody, keep ≤7, and
  upload offsite; ensure the release manifest excludes secret-bearing files rather than hashing
  them (current gap).
- Confirm whether any delivery archive ever left the host; if yes, rotate the CA/seed.

### 4.4 Device/image credentials

- Stop using the host `sudo` value and the shared Wi-Fi PSK: generate a random per-image password
  and either a per-device PSK on a dedicated IoT SSID or a WPA-Enterprise identity.
- After flashing, change the device account password (`passwd`) and record the date; keep the SSH
  key per-device and destroy the private key when the device is retired
  (`retirement-key-destruction.md`).

### 4.5 Legacy Wazuh/MCT stores

- Execute `mct/runbooks/credential-rotation-checklist.md` in its priority order; migrate stores to
  root-owned files during the same pass; update the tracker with dates and artifacts (status-only,
  never values).

## 5. Emergency revocation plan (break-glass)

| Scenario | Immediate action (read-only audit recommendation) | Evidence to capture |
|---|---|---|
| `.env`/account compromise | Rotate `sudo` + all third-party keys starting with Proxmox/Cloudflare (infra control), then R2/S3/GitHub; invalidate sessions/SSH keys | Rotation entries + negative tests |
| Edge CA or signing seed disclosure | Pause updates; revoke/re-mint CA and sensor certs; re-sign manifests with a new seed; re-enroll devices as needed | `falcon deploy edge` audit log, update drill |
| Delivery archive loss | Assume CA key + signing seed + DB disclosed; full edge PKI rotation | Incident record + rotation evidence |
| Legacy stack credential leak | Rotate the affected class per MCT order; isolate tunnel if Cloudflare token involved | Tracker rows + service health |
| Break-glass needed | Use root via owner console; log the action in the decision log; after recovery, rotate anything used | Decision-log entry |

Note: OD-04 (break-glass custody) is still PENDING; `.env` currently makes the sudo password the
de facto break-glass credential. Close OD-04 before any production transition.

## 6. Validation checklist (per rotation)

- [ ] Old credential rejected with an explicit status (401/403) captured.
- [ ] Consumer list verified healthy after the change (service probes, pipeline counters).
- [ ] Store permissions unchanged (0600/0640) and file written in place where cached.
- [ ] No value in evidence: metadata shows fingerprint/date only; redaction statement accurate.
- [ ] Rotation register updated; overlap copy destroyed.
- [ ] `ci/validate.py` / `ci/validate.sh` still pass (central scan currently trips on audit docs — see SECRET-P3-010).

## 7. Suggested automation and tests

- A `rotation-status` checker that fails if a class has no entry within its cadence.
- Env validator: reject duplicate/unknown keys and stale names (would have caught `ntfy_topic`×2).
- Signing-seed drill script with device-apply assertion and rollback.
- Encrypted-backup round-trip test (encrypt → remote copy → restore on scratch).
- CI job that greps root-run scripts for whole-file `.env` sourcing.

## 8. Open items surfaced by the audit

1. `SECRET-P1-001` device/image credential reuse (host sudo + Wi-Fi PSK).
2. `SECRET-P1-002` split `/home/user/.env`; selective export from root scripts.
3. `SECRET-P1-003` encrypt/relocate edge backups; remove secrets from the release manifest; offsite.
4. `SECRET-P2-004` exercise untested central classes; add signing-seed rotation.
5. `SECRET-P2-006` deduplicate keys and publish the owner-env inventory.
6. `SECRET-P2-007` execute the legacy MCT tracker.
7. `SECRET-P3-008/009` close OD-04; reconcile OD-17/18 records.
