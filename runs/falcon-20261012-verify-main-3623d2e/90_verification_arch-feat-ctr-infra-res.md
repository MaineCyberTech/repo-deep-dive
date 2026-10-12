# Post-merge verification — ARCH / FEAT / CTR / INFRA / RES (17 findings)

- Repo: `/home/user/falcon-build` @ `3623d2e` (clean working tree), 2026-10-12 ~20:00–20:20Z.
- Original run: `falcon-20261011-0416-full-f5cb7c9` (audit commit `f5cb7c9`), 126 findings; 17 in scope.
- Method: repo inspection at `3623d2e` + live read-only checks (docker inspect, systemctl/journalctl, OpenSearch/Grafana read APIs, textfile metrics, rclone/offsite logs). No mutations; secrets never reproduced.
- Note: live hardening overlays for IRIS/Wazuh exist only on the host (`/opt/...`), not in the repo; live drift/secret items are reported under "New findings".

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| ARCH-P1-001 | P1 | owner-accepted | still-open (owner-accepted, unchanged) | no warm standby; acceptance `docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md:21` (OD-09/OD-10); 20261005 run register |
| ARCH-P2-002 | P2 | open | still-open (partially fixed) | live stacks tag@digest + `pins/images.lock` (24 entries incl. adopted); residual `mct/compose` 37 refs / 29 unpinned under blanket waiver `root:mct/compose ref:*`; **live drift metric now 1** (new finding) |
| ARCH-P2-003 | P2 | open | still-open | `config/vector/aggregator.yaml:25-28`, `config/vector/edge.yaml:245-248` still HTTP basic auth |
| ARCH-P3-001 | P3 | open | **closed** | `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` N-08 = "HTTP basic auth (shared credential; ARCH-P2-003)" |
| ARCH-P3-002 | P3 | open | **closed** | `bootstrap/90-alerting.sh:688-695` container-mem + container-restart rules; live 93-rule set; metrics exported (`export_monitor_metrics.sh:717,727`) |
| CTR-P2-001 | P2 | still-open | still-open (partially fixed, live > repo) | live nnp 26/27 (ntopng documented); healthchecks 19/27; `cap_drop` none on adopted; IRIS/Wazuh hardening overlays live-only; `forwarder-install.sh:27-31` no flags |
| CTR-P3-001 | P3 | still-open | still-open (partially fixed) | docker.sock mounts removed (`e094473`); 29 unpinned refs + blanket waiver remain |
| CTR-P3-002 | P3 | still-open | still-open | `compose/central/opensearch-s3.Dockerfile:1-4` unchanged; plugin sha only in a comment (`bootstrap/60-central-deploy.sh:53`); mismatch WARN-only (`:60-64`) |
| FEAT-P2-001 | P2 | open | still-open | `automation/validation/container_drift_check.sh:150` DECLARED_ROOTS includes `mct/compose`; `mct/VENDORING.md:67` P4 proposed/unimplemented |
| FEAT-P3-001 | P3 | verified-fixed | **closed** | 93 `write_rule` = 93 catalogue = 93 live (UID sets identical); README.md:32 / CURRENT_STATE.md:112 = 93 |
| INFRA-P2-005 | P2 | verified-fixed | **closed** | guard `ok` every 15 min (root_free 53.8 GiB vs 20 GiB); keep-2 (`85-backup-job.sh:68-76`); bundle archived to data LV |
| INFRA-P2-006 | P2 | open | **closed** | Oct 12 offsite complete 04:22:35Z, full verification PASS (1,584+9,547 objects, 0 mismatched); stamp 18:46:35Z; DLQ 0 |
| RES-P1-002 | P1 | verified-fixed | **closed** | as INFRA-P2-005; exactly 2 SUCCESS snapshots live |
| RES-P2-001 | P2 | open | still-open (improved) | 34.85% mem available (was 32.56%), swap 46.70% (was 52.88%), 0 OOM since Oct 9; envelope stale (`PERFORMANCE_ENVELOPE.md:10-11`) |
| RES-P2-002 | P1 | verified-fixed | **closed** | `config/systemd/falcon-wazuh-{agent,enroll}-proxy.socket:12` `FreeBind=yes`, wg ordering removed (`3b0b976`); live units match, active, listeners 10.99.0.1:15140/15141 |
| RES-P3-001 | P3 | open | still-open | no new OOM/host-mem/boot-order/root-LV injections; `f5cb7c9..3623d2e` test diff = 3 files / 7 lines |
| RES-P3-002 | P3 | open | still-open (partially) | run recorded 59/0 (`ledgers/decision_log.md:268`); no boot-time unit/timer (`config/systemd/` has none) |

---

## Per-finding detail

### ARCH-P1-001 — Single-host concentration (owner-accepted) — still-open (accepted)
- No infra change: all capture/storage/metrics/alerting/delivery still on the one host; no warm standby added at `3623d2e`.
- Acceptance artifacts present: `docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md:21` (OD-09/OD-10, RPO 24 h / RTO config ≤1 h, data ≤4 h, 2026-09-22) and the 2026-10-05 run register (`docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/follow_up_register.md:7`).
- Verdict rationale: design acceptance stands; the fix path (warm standby or a tested RTO/RPO artifact) is still not implemented — this is a carried accepted risk, not a merge blocker.

### ARCH-P2-002 — Vendored MCT tree tag-only under blanket waiver — still-open (partially fixed)
- Fixed half confirmed: live stacks are tag@digest and lock-covered — `pins/images.lock` has 24 entries including `wazuh/wazuh-manager|indexer|dashboard:4.14.7`, `ghcr.io/dfir-iris/*`, `thinkst/opencanary`, `cloudflare/cloudflared:latest`, `falcon-opensearch-s3:2.19.6`; `automation/validation/tests/vendored_compose_pin_test.sh` 4/4 PASS; `compose_digest_check_test.sh` 25/25 PASS.
- Residual confirmed: `mct/compose/` has 37 image refs, 8 pinned / 29 unpinned (floating tags like `stable`, `latest`); blanket waiver `pins/supply-chain-waivers.json` → `compose_digest: [{root: mct/compose, ref: "*", review_by 2026-12-31}]`.
- **Live drift regressed to 1** (was 0 at the audit) — see New finding N-1.

### ARCH-P2-003 — Ingest auth is HTTP basic auth — still-open
- `config/vector/aggregator.yaml:25-28` and `config/vector/edge.yaml:245-248` still `strategy: basic` with the shared `falcon-vector-edge` / `${VECTOR_INGEST_PW}` credential; no per-device certificate identity, no signing/idempotency.
- (The port-matrix description of this mechanism is now correct — ARCH-P3-001.)

### ARCH-P3-001 — Port matrix wording — closed
- `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` N-08 now reads: `HTTP basic auth (shared credential; ARCH-P2-003)` (was "shared secret header"). The negative-test wording matches ("ingest without credentials rejected; host port closed").

### ARCH-P3-002 — Container-level memory/restart alerting — closed
- `bootstrap/90-alerting.sh:688-691` `falcon-container-mem-high` (`falcon_container_mem_bytes > bool 5368709120`, 30m, warning; tuned 2026-10-11 in `1328d70`) and `:692-695` `falcon-container-restarts` (`delta(falcon_container_restarts[1h]) > bool 1`, 15m).
- Both live: the Grafana provisioning API returns 93 rules whose UIDs equal the script's 93 `write_rule` UIDs (set diff empty).
- Metrics exported for all 27 running containers (`automation/validation/export_monitor_metrics.sh:717,727`; live `falcon_container_mem_bytes` present for 27 names).
- Minor deviation: the memory rule uses an absolute 5 GiB threshold, not a ratio vs each declared limit (the suggested form); acceptable as an early-warning signal, but per-service ratio alerting remains a possible refinement.

### CTR-P2-001 — Adopted stacks hardening/healthchecks — still-open (partially fixed)
- Live now (hardening round 2026-10-12, recorded `ledgers/decision_log.md:275`):
  - `no-new-privileges` on 26/27 running containers; the single exception is `falcon-central-ntopng-1` (documented in `compose/central/docker-compose.yml:280`, capture privileges).
  - 0 privileged, 0 docker.sock mounts (checked across all 27).
  - Healthchecks live on 19/27. **Without a healthcheck (8):** `multi-node-nginx-1`, `multi-node-wazuh.worker-1`, `iriswebapp_app`, `iriswebapp_worker`, `iriswebapp_rabbitmq`, `mct-security-stack-opencanary-1`, `falcon-wazuh-forwarder`, `wazuh-cloudflared` (the live overlays define no healthcheck for these; the decision-log "27/27 where applicable" overstates the coverage).
  - Memory caps applied live via `docker update` (e.g. indexers 2 GiB, master/worker 1 GiB, dashboard 768m, IRIS app 1 GiB); `falcon-wazuh-forwarder` and `wazuh-cloudflared` are uncapped.
  - `cap_drop` is still null on all adopted containers; no read-only rootfs.
- Repo side at `3623d2e`:
  - Committed: `compose/mct/docker-compose.opencanary.yml:31-35` (security_opt + mem caps, `b377f14`).
  - NOT committed: the IRIS/Wazuh hardening overlays exist only at `/opt/iris-web/docker-compose.hardening.yml` and `/opt/wazuh-docker/multi-node/docker-compose.hardening.yml` (live compose chains include them); `git ls-tree 3623d2e` has no `docker-compose.hardening.yml` and `compose/mct/iris-web/*` + `automation/wazuh/multi-node/*.yml` still declare no `security_opt`/`healthcheck`/`cap_drop`.
  - `automation/wazuh/forwarder-install.sh:27-31` still runs the forwarder with no `--security-opt`, `--user` or `--health-cmd`.
- Verdict rationale: the live exposure is largely closed, but the repo does not carry the hardening for the adopted trees (a clean-host rebuild from the repo would lose it) and healthcheck/cap_drop coverage is incomplete.

### CTR-P3-001 — Vendored Shuffle docker.sock / pins — still-open (partially fixed)
- Socket mounts removed in `e094473` (2026-10-11): both `mct/compose/docker-compose.shuffle.yml` mounts are now commented with a CTR-P3-001/CHAIN-P3-001 note (re-add only with a scoped socket proxy); live docker.sock count = 0.
- Residual: the same tree still carries 29 unpinned image refs under the blanket `mct/compose ref:*` waiver (also ARCH-P2-002/FEAT-P2-001), and no per-ref exception was recorded.

### CTR-P3-002 — OpenSearch repository-s3 plugin install — still-open
- `compose/central/opensearch-s3.Dockerfile:1-4` unchanged: digest-pinned base, `USER root`, `opensearch-plugin install --batch repository-s3` (version implied, no checksum), back to `USER 1000`.
- `bootstrap/60-central-deploy.sh:53` records the artifact URL + sha256 (`060a1bef…`, 14,269,609 bytes) but the build does not verify it (grep: the hash appears only in that comment); a rebuild/digest mismatch is still WARN-only (`:60-64`).

### FEAT-P2-001 — Vendored MCT services vs archive-only policy — still-open
- `automation/validation/container_drift_check.sh:150` still lists `"mct/compose"` in `DECLARED_ROOTS` (and comments at `:19`, `:579`), so a container started from the archive tree would be classified as declared.
- `mct/VENDORING.md:67` P4 (import manifest + vendor-drift check) remains "Proposed … not implemented"; no import manifest exists (`:36` "no upstream commit and no import manifest").
- The static archive-only guard (`remediation_guards_test.sh`) passes; no `mct/compose` containers run live (latent).

### FEAT-P3-001 — Alert-rule count claims — closed
- `bootstrap/90-alerting.sh` has 93 `write_rule` calls; `docs/phase9/ALERT_CATALOGUE.yaml` has 93 ids; `README.md:32` and `docs/CURRENT_STATE.md:112,132` say 93.
- Live: Grafana provisioning API (`/api/v1/provisioning/alert-rules`) returns 93 rules; UID set diff script↔live↔catalogue is empty. (Counts advanced 91 → 93 with the container rules in `e094473`; all artifacts moved together.)

### INFRA-P2-005 — Disk guard failing on root LV — closed
- Live guard (unit ExecStart = repo script): last runs every 15 min all log `ok: above thresholds, nothing to do`; latest `root_free=53847952 KB` (51.3 GiB) vs `ROOT_THRESHOLD_KB` 20 GiB; `df /` = 52 GiB avail (69% used).
- Reclaim history: 8 `BELOW THRESHOLD` events on 2026-10-11 (pre-fix), none since.
- Remediation in main: retention keep-2 (`bootstrap/85-backup-job.sh:68-76`, `b9a8bd7`), snapshot repo 69→59 GiB, 22 GiB bundle archived to `/srv/falcon/archive/wz-migration/wazuh-stack.tar` on the **data LV** (`/srv/falcon`, separate mount, 71 GiB avail). Guard threshold unchanged (20 GiB) — acceptable now that the margin is ~31 GiB.

### INFRA-P2-006 — Offsite backup catch-up — closed
- The Oct-11 catch-up was killed mid-run (`rc=130` at 14:40:30Z, abort marker), but the Oct-12 03:30 run completed the offsite leg: `offsite sync OK` 04:22:35Z, `backup job complete` 04:22:44Z, with the full verification `spaces…: total=1584 mismatched=0` + `total=9547 mismatched=0` (`/srv/falcon/backups/offsite.log`).
- Stamp advanced: `falcon_backup_offsite_last_success_timestamp_seconds 1791830795` = **2026-10-12T18:46:35Z** (the encrypted-remote migration completion run, `offsite-crypt-migration.log`); RPO ≈ 75 min at capture; `falcon_backup_offsite_dlq 0`; `falcon_backup_offsite_last_uploaded_files 540` (delta, not a full re-upload).

### RES-P1-002 — Root LV below threshold / guard failing — closed
- Same evidence as INFRA-P2-005; additionally the local snapshot repository now holds exactly **2 SUCCESS snapshots** (`snap-20261011-033003`, `snap-20261012-033000`) matching the keep-2 policy; guard exit 0; no firing disk alerts (Grafana alertmanager list empty at capture).
- The finding's "underlying capacity remains thin" note: root free is ~52 GiB today with the snapshot repo at 59 GiB; the nightly ~4-5 GiB churn is within the 20 GiB threshold margin.

### RES-P2-001 — Host memory/swap pressure — still-open (improved)
- Live: MemAvailable 5,440,804 kB / 15,340 MiB ≈ **34.6%** (metric `falcon_host_memory_available_percent` 34.85% at the last metrics run), swap used 3,824/8,191 MiB = **46.70%** (`falcon_host_swap_used_percent`); 0 OOM/kill lines in the kernel log since 2026-10-09.
- Adopted stacks now have live memory caps and central services have compose `mem_limit`; the hardening overlays are live-only (repo gap shared with CTR-P2-001).
- Still-open: the measured capacity envelope is stale — `docs/phase5/PERFORMANCE_ENVELOPE.md:10-11` still states "4 vCPU, 11.7 GiB RAM … 74 GiB root + 59 GiB data" vs today's 15.2 GiB RAM / 171 GiB root / 221 GiB data; no refreshed memory budget; per-service requests/limits not documented repo-side.

### RES-P2-002 — Wazuh VPN proxy socket boot race — closed
- Repo: `config/systemd/falcon-wazuh-enroll-proxy.socket:12` and `falcon-wazuh-agent-proxy.socket:12` set `FreeBind=yes`; the `After=wg-quick@wg0` ordering is removed (comment at `:2-8`; commit `3b0b976`).
- Live: installed units are byte-identical to the repo copies; both sockets `active`; listeners up on `10.99.0.1:15141` and `10.99.0.1:15140` (systemd + socket-proxyd); `boot_order_check.sh` includes socket checks (enabled/active/multi-user.target/no sockets.target) and is wired into `post_reboot_verify.sh`.
- Caveats (non-blocking): the fix is not yet boot-proven — last boot 2026-10-11T02:27:39Z predates the fix; the next reboot is the final proof (freebind capability was proven live). `docs/runbooks/VPN.md:193` still attributes the fix to 2026-09-30 and does not mention FreeBind (see N-3).

### RES-P3-001 — Failure-injection coverage — still-open
- No new drills for the four occurred failure classes: the repo's drills remain `disk_pressure_drill.sh`, `index_rename_rollback_drill.sh`, `sensor_silence_drill.sh` (+ alert/VPN/sink drills from earlier waves); no aggregator-OOM, host-memory, boot-order/socket or root-LV injection test.
- `git diff --stat f5cb7c9 3623d2e -- automation/validation/tests/` = 3 files, 7 insertions (env-validator/rotation/freshness tweaks — no new drills).

### RES-P3-002 — Post-reboot verification — still-open (partially)
- Progress: a post-reboot verification was run and recorded after the Oct-11 reboot (`ledgers/decision_log.md:268` — 59 passed / 0 failed), and `post_reboot_verify.sh` now includes the socket boot-order check.
- Still missing: no boot-time automation — `config/systemd/` contains no post-reboot/boot-check unit and no timer; the script remains a documented manual root step (`docs/runbooks/OPERATOR_START_HERE.md:102`), so a reboot can again go unverified unless an operator runs it.

---

## New findings

### N-1 (live regression, P3) — `falcon_live_image_drift` regressed 0 → 1 (forwarder reference form)
- The audit note for ARCH-P2-002 recorded live drift 0; now `falcon_live_image_drift 1` in `/srv/falcon/textfile/falcon_services.prom` (fresh 20:04Z) and `automation/validation/live_image_pin_check.sh` prints:
  `DRIFT falcon-wazuh-forwarder sha256:4c47124a… [not in pins/images.lock]` (27 containers, drift=1; all others OK).
- Cause: the forwarder was recreated 2026-10-12T19:28:58Z (hardening round) with `Config.Image = sha256:4c47124a…` — a bare digest reference — so the read-only check cannot resolve it to the lock entry even though the digest **is** the locked `python:3.12-alpine` digest (`pins/images.lock`). The image bytes are correct; the reference form is what trips the check.
- Impact: the drift metric is wrong-positive and, more importantly, **no alert rule consumes `falcon_live_image_drift`** (metric-only residual documented in TB-8 / decision log 2026-10-01), so this is silent.
- Fix: recreate the forwarder via `automation/wazuh/forwarder-install.sh` (uses `python:3.12-alpine@sha256:4c47124a…`, the proper reference), or teach the checker to resolve bare-digest refs via the image ID; consider adding a rule on the metric.

### N-2 (live secret hygiene, P2) — live Wazuh compose hardcodes the current indexer password (world-readable)
- `/opt/wazuh-docker/multi-node/docker-compose.yml:66` contains the **current** Wazuh indexer password as a literal (verified by hash equality with the live `/opt/…/.env` and the running worker's env — values not reproduced). File mode `0644 user:user` on a `755` directory, so any local user/process can read the credential.
- The committed repo file is clean (`${INDEXER_PASSWORD}` at both lines, unchanged since `1c79d02`); commit `4c423d8` ("security: redact the hardcoded indexer passwords in the committed compose…") is **empty** — `git diff-tree -r 4c423d8` shows no tree change, so the claimed redaction never landed anywhere.
- Functional state today is consistent (running master/worker use the `.env` value; the incident "stale worker value broke alert shipping" is not recurring), but the live file exposes the credential and a future edit/recreate from it can reintroduce the stale-value failure.
- Fix: replace line 66 with `${INDEXER_PASSWORD}` (and ensure the `.env` interpolation is used by the compose chain), keep the file `0600` or the value only in the root-only `.env`, and re-verify the running worker after the next recreate.

### N-3 (doc, P3) — VPN runbook does not document the actual RES-P2-002 fix
- `docs/runbooks/VPN.md:193` still says the sockets are "enabled in multi-user.target (NOT sockets.target …; fixed 2026-09-30)" and does not mention `FreeBind=yes` / the 2026-10-11 ordering removal, which is what actually fixed the boot race. Update the row so operators don't rely on the superseded mechanism.

### N-4 (doc/ops note, P3) — decision-log healthcheck coverage claim overstates the live state
- `ledgers/decision_log.md:275` says the adopted stacks carry nnp + healthchecks "27/27 where applicable"; live healthchecks are on 19/27 (8 adopted containers have none — see CTR-P2-001). Suggest correcting the record and either adding the missing healthchecks or stating the explicit "no healthcheck" exception list (ntopng-style).
