# Post-merge verification re-audit — ARCH / FEAT / CTR / INFRA / RES findings

- Repo: `/home/user/falcon-build` @ `edbf441` (HEAD = `edbf441d03cfba1f2a2e923a94021e1cbab0c338`, main, clean), 2026-10-14 ~00:30–00:50Z. Read-only: nothing written to the tree.
- Original run: `falcon-20261011-0416-full-f5cb7c9` (audit commit `f5cb7c9`), 126 findings; 17 in scope.
- Previous verification: `falcon-20261012-verify-main-3623d2e` (2026-10-12); this run re-checks at `edbf441` after `f82f82f`, `f23ecff`, `96d722a`/`55a84df`/`73f2d8e`, `e15c731`, `1b14231`, `d61b493`, `ce76ef0`, `11623a1` and the publication/records chain.
- Method: repo inspection at `edbf441` (`git show`/grep), deterministic pass (`/tmp/opencode/reaudit-20261014/det/`), and live read-only checks (docker ps/inspect/stats, systemctl/journalctl, Prometheus HTTP queries, Grafana SQLite read-only, OpenSearch snapshot read API, textfile metrics, rclone/offsite logs). No mutations; no secrets reproduced.

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| ARCH-P1-001 | P1 | owner-accepted | owner-accepted | No warm standby (no standby commit); acceptance `docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md:21` (OD-09/OD-10) + 20261005 register row still open |
| ARCH-P2-002 | P2 | open | open | Live stacks tag@digest + lock (24 entries); live drift 1→0; residual `mct/compose` 37 refs / **29 unpinned** (deterministic DET-P3-003=29) under blanket `mct/compose ref:*` waivers |
| ARCH-P2-003 | P2 | open | open | `config/vector/aggregator.yaml:26` / `config/vector/edge.yaml:246` still `strategy: basic` (shared credential) |
| ARCH-P3-001 | P3 | verified-fixed | verified-fixed | `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` N-08 = "HTTP basic auth (shared credential; ARCH-P2-003)" |
| ARCH-P3-002 | P3 | verified-fixed | verified-fixed | `bootstrap/90-alerting.sh:705-710` rules; both UIDs live in Grafana DB; mem rule fired 2026-10-11 |
| CTR-P2-001 | P2 | open | open | Live nnp 26/27, healthchecks 19/27, `cap_drop` null on adopted; repo: only opencanary hardened, IRIS/Wazuh + `forwarder-install.sh:27-31` bare; vuln scans still pending (12 images) |
| CTR-P3-001 | P3 | open | open | shuffle docker.sock mounts still commented (`mct/compose/docker-compose.shuffle.yml:48-51,90-93`); live sock/privileged = 0; 29 unpinned refs + blanket waiver |
| CTR-P3-002 | P3 | open | open | `compose/central/opensearch-s3.Dockerfile:1-4` unchanged; plugin sha only in `bootstrap/60-central-deploy.sh:52-54` comment; mismatch WARN-only (`:60-64`) |
| FEAT-P2-001 | P2 | open | open | `automation/validation/container_drift_check.sh:150` still lists `mct/compose` in DECLARED_ROOTS; `mct/VENDORING.md:67` P4 still proposed/unimplemented |
| FEAT-P3-001 | P3 | verified-fixed | verified-fixed | 94 `write_rule` = 94 catalogue ids = 94 live (Grafana DB `alert_rule` rows=94); `README.md:32` / `docs/CURRENT_STATE.md:112` = 94 |
| INFRA-P2-005 | P2 | verified-fixed | verified-fixed | Guard `ok` every 15 min (00:30:03Z `root_free=47,475,284 KB` ≈ 45.3 GiB vs 20 GiB); 0 BELOW THRESHOLD since Oct 12; keep-2 (`85-backup-job.sh:68-76`) |
| INFRA-P2-006 | P2 | verified-fixed | verified-fixed | Oct 13 run complete 05:45:39Z (encrypted crypt default); full verification PASS (opensearch 1,593 + wazuh-indexer 8,245 objects, 0 mismatched); stamp 2026-10-13T05:45:39Z; DLQ 0 |
| RES-P1-002 | P1 | verified-fixed | verified-fixed | Guard ok; exactly 2 SUCCESS snapshots (snap-20261012/13-033000); tarball gone from `/var/tmp` (23.3 GB on data LV); watch: root free 51→45.3 GiB since Oct 12 |
| RES-P2-001 | P2 | open | open | 48 h Prometheus: mem-available avg 32.79% (min 17.77 / max 47.2), now 28.97%; swap avg 51.76%, now 52.76% (max 63.15%); 0 OOM since Oct 9; envelope still stale (`PERFORMANCE_ENVELOPE.md:10-11`) |
| RES-P2-002 | P1 | verified-fixed | verified-fixed | `FreeBind=yes` on both sockets (`config/systemd/falcon-wazuh-{agent,enroll}-proxy.socket:12`); live active since 2026-10-11 05:04:53, listeners 15140/15141; `VPN.md:193` now documents the fix |
| RES-P3-001 | P3 | open | open | No OOM/host-mem/boot-order/root-LV injections; `3623d2e..edbf441` tests diff = 3 files (watchdog/DLQ/env-validator) |
| RES-P3-002 | P3 | open | open | 59/0 run recorded (`ledgers/decision_log.md:268`); still no boot-time unit/timer in `config/systemd/`; `post_reboot_verify.sh` manual (`OPERATOR_START_HERE.md:102`); no reboot since Oct 11 |

Verdict counts: **verified-fixed 7, open 9, owner-accepted 1, partially-fixed 0, regressed 0**.

---

## Per-finding detail

### ARCH-P1-001 — Single-host concentration — owner-accepted (unchanged)

- No infra change: all capture/storage/metrics/alerting/delivery still run on the one host; no warm-standby commit exists (`git log --all --grep=standby` empty).
- Acceptance artifacts still in place: `docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md:21` (OD-09/OD-10: RPO 24 h, RTO config ≤1 h / data ≤4 h, 2026-09-22) and the 2026-10-05 run register (`docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/follow_up_register.md:7`, ARCH-P1-001 still `open @owner`).
- Verdict rationale: carried owner-accepted design risk; unchanged at `edbf441`.

### ARCH-P2-002 — Vendored MCT tree unpinned under blanket waiver — open (residual unchanged; live drift regression resolved)

- Fixed half intact: live containers run tag@digest and are lock-covered — `pins/images.lock` has 24 images incl. the adopted IRIS/OpenCanary/Wazuh/cloudflared/nginx/rabbitmq set. `automation/validation/live_image_pin_check.sh` at capture: `containers=27 drift=0`, `falcon_live_image_drift 0` (metric in `/srv/falcon/textfile/falcon_services.prom`, fresh 00:32Z).
- The 2026-10-12 drift=1 regression (forwarder recreated as a bare digest reference) is **resolved**: `falcon-wazuh-forwarder` now has `Config.Image = python:3.12-alpine@sha256:4c47124a…` (recreated with the locked reference, recorded in `ledgers/decision_log.md:276`).
- Residual unchanged: `mct/compose` = 37 image refs, 8 pinned / **29 unpinned** (`grep` count at edbf441; the re-audit deterministic pass DET-P3-003 counts exactly 29 unpinned images, all in `mct/compose`). Coverage is via blanket waivers `pins/supply-chain-waivers.json` → `compose_digest: {root: mct/compose, ref: "*", review_by 2026-12-31}` **and** the new `compose_pin` section (`root: mct/compose, ref: "*"`); the pin gate now covers the vendored trees (`ci/validate.py:113-140`, EVOL-P1-002) but per-ref scoping/P4 remain unimplemented.
- Verdict: open — the finding as written (tag-only vendored tree under a blanket pin waiver) is still true; the live-stack half remains fixed.

### ARCH-P2-003 — Ingest auth is HTTP basic auth — open (unchanged)

- `config/vector/aggregator.yaml:26` and `config/vector/edge.yaml:246` still `strategy: basic` with the shared `falcon-vector-edge` / `${VECTOR_INGEST_PW}` credential; no per-device certificate identity, no signing/idempotency. (WH-P1-001 added end-to-end acknowledgements at `aggregator.yaml:31+`, which is a loss-protection change, not an auth change.)

### ARCH-P3-001 — Port matrix wording — verified-fixed (unchanged)

- `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` N-08 still reads `HTTP basic auth (shared credential; ARCH-P2-003)`; the negative test wording matches.

### ARCH-P3-002 — Container-level memory/restart alerting — verified-fixed (unchanged, now firing-proven)

- Repo: `bootstrap/90-alerting.sh:705-707` `falcon-container-mem-high` (`falcon_container_mem_bytes > bool 5368709120`, 30m) and `:709-710` `falcon-container-restarts` (`delta(falcon_container_restarts[1h]) > bool 1`, 15m).
- Live: Grafana DB (`/srv/falcon/grafana/grafana.db`, read-only) `alert_rule` contains both UIDs; `alert_instance` has 0 rows (nothing currently firing). The memory rule demonstrably works: the relay delivered `FIRING: Container memory high` on 2026-10-11 (`journalctl -u falcon-alert-relay`).

### CTR-P2-001 — Adopted stacks without baseline hardening/healthchecks — open (residual unchanged; live > repo)

- Live profile 2026-10-14 (27 containers): `no-new-privileges` on 26/27 — only `falcon-central-ntopng-1` is null (documented capture-privilege exception); 0 privileged; 0 docker.sock mounts; healthchecks on **19/27** — the 8 without are `falcon-wazuh-forwarder`, `iriswebapp_app`, `iriswebapp_worker`, `iriswebapp_rabbitmq`, `mct-security-stack-opencanary-1`, `multi-node-nginx-1`, `multi-node-wazuh.worker-1`, `wazuh-cloudflared`; `cap_drop` is null on every adopted container. Live memory caps: indexers 2 GiB, master/worker 1 GiB, dashboard 768m, IRIS app 1 GiB, db/rabbitmq/worker 512m, nginx/opencanary 256m; forwarder + cloudflared uncapped.
- Repo at `edbf441`: only `compose/mct/docker-compose.opencanary.yml:32-33` carries `security_opt` + mem caps (no healthcheck); `compose/mct/iris-web/{docker-compose.base.yml,docker-compose.yml}` (204 lines total) and `automation/wazuh/multi-node/docker-compose.yml` (235 lines) declare **no** `security_opt`/`healthcheck`/`cap_drop`; `automation/wazuh/forwarder-install.sh:27-31` still runs with no `--security-opt`/`--user`/`--health-cmd`. The IRIS/Wazuh hardening overlays remain live-only (`/opt/iris-web/docker-compose.hardening.yml`, `/opt/wazuh-docker/multi-node/docker-compose.hardening.yml`; no `docker-compose.hardening.yml` in the tree).
- Supply-chain residual: vulnerability scans still pending for 12 images (`pins/supply-chain-waivers.json` `vuln_scan_pending`, review_by 2026-12-31); `sbom/vuln/` (12 files) has no scan for IRIS/OpenCanary/Wazuh/cloudflared/rabbitmq/nginx/python.
- Verdict rationale: unchanged from 2026-10-12; the live exposure is largely closed, but a clean-host rebuild from the repo would lose the hardening, and healthcheck/cap_drop/vuln-scan coverage is incomplete. (The previous run's N-4 record-overstatement is corrected at `ledgers/decision_log.md:276`: "26/27 … nnp … and 19/27 have healthchecks".)

### CTR-P3-001 — Vendored Shuffle docker.sock / pins — open (partially fixed; unchanged)

- Socket mounts remain removed/commented in `mct/compose/docker-compose.shuffle.yml:48-51` and `:90-93` (CTR-P3-001/CHAIN-P3-001 note, re-add only with a scoped socket proxy).
- Live: docker.sock mounts = 0, privileged = 0 across all 27 containers.
- Residual: same 29 unpinned refs under the blanket `mct/compose ref:*` waiver (also ARCH-P2-002/FEAT-P2-001); no per-ref exception recorded.

### CTR-P3-002 — OpenSearch repository-s3 plugin install — open (unchanged)

- `compose/central/opensearch-s3.Dockerfile:1-4`: digest-pinned base, `USER root`, `opensearch-plugin install --batch repository-s3` (version implied, no checksum), back to `USER 1000`.
- `bootstrap/60-central-deploy.sh:52-54` still records only the artifact URL + sha256 (`060a1bef…`, 14,269,609 bytes) as a comment; the build does not verify it; a rebuild/digest mismatch remains WARN-only (`:60-64`).

### FEAT-P2-001 — Vendored MCT services vs archive-only policy — open (unchanged)

- `automation/validation/container_drift_check.sh:150` still lists `"mct/compose"` in `DECLARED_ROOTS` (comments at `:19`, `:579`), so a container started from the archive tree would be classified as declared.
- `mct/VENDORING.md:67` P4 remains "Proposed (coordinator-owned, not implemented here)"; the tree still has 29 unpinned refs; no `mct/compose` containers run live (latent).

### FEAT-P3-001 — Alert-rule count claims vs catalogue — verified-fixed (unchanged, count advanced to 94)

- `bootstrap/90-alerting.sh` has 94 `write_rule` calls (95 grep hits minus the function definition at `:186`); `docs/phase9/ALERT_CATALOGUE.yaml` has 94 ids; `README.md:32` and `docs/CURRENT_STATE.md:112` say 94.
- Live: Grafana DB `alert_rule` rows = **94** (read-only query) — the 2026-10-13 WZ-VOLUME addition (`falcon-wazuh-alert-volume-drop`) is present and the catalogue was regenerated from live (`73f2d8e`). Counts moved together 93 → 94; no drift.

### INFRA-P2-005 — Disk guard failing on root LV — verified-fixed (no regression)

- Live guard (unit ExecStart = repo script): every 15 min run since at least Oct 12 logs `ok: above thresholds, nothing to do`; latest 00:30:03Z `free=66,574,404 KB threshold=25,165,824 KB root_free=47,475,284 KB root_threshold=20,971,520 KB`; `falcon_disk_guard_root_free_bytes 48,614,678,528` (45.3 GiB) vs 20 GiB; 0 `BELOW THRESHOLD` lines since Oct 12 (last reclaim 2026-10-11 04:30, `reclaims_total 51`).
- Reclaim/retention policy unchanged (`automation/validation/disk_guard.sh`: data 24 GiB, root 20 GiB; snapshots keep newest 2; config archives keep newest 3); retention keep-2 unchanged in `bootstrap/85-backup-job.sh:68-76`.
- df `/` = 46 GiB avail (73% used). No disk alert active (`alert_instance` empty).

### INFRA-P2-006 — Nightly offsite backup catch-up — verified-fixed (no regression)

- The Oct 13 nightly (started 03:30) completed the offsite leg at 05:45:39Z: `offsite sync OK`, full verification `spaces-crypt:/monitoring/opensearch: total=1593 mismatched=0` + `spaces-crypt:/monitoring/wazuh-indexer: total=8245 mismatched=0`, `offsite_verify_all: PASS`, `offsite backup workflow complete` (`/srv/falcon/backups/offsite.log`).
- Metrics: `falcon_backup_offsite_last_success_timestamp_seconds 1791870339` = 2026-10-13T05:45:39Z; `falcon_backup_offsite_dlq 0`; `last_uploaded_files 696` (delta, not a full re-upload); duration ~7,571 s.
- The encrypted crypt remote is now the default: `OFFSITE_CRYPT=1` in `bootstrap/85-backup-job.sh:100` and `config/systemd/falcon-backup.service` (DR-P2-002), matching the log's `spaces-crypt:` paths. Next run scheduled 03:30Z (RPO bounded by the nightly cadence).

### RES-P1-002 — Root LV below threshold / guard failing — verified-fixed (no regression; thin-capacity watch)

- Same evidence as INFRA-P2-005: guard ok, root free 45.3 GiB vs the 20 GiB threshold, 0 BELOW THRESHOLD since Oct 12.
- Local snapshot repository holds exactly **2 SUCCESS snapshots** (`snap-20261012-033000`, `snap-20261013-033003`) matching keep-2; the stale `/var/tmp/wz-migration/wazuh-stack.tar` is gone (23.3 GB archived at `/srv/falcon/archive/wz-migration/` on the data LV).
- Watch item (residual, not a regression): root free has declined ~51.2 GiB (Oct 13 00:41) → 45.3 GiB (Oct 14 00:41) with the snapshot repo at 62 GiB (was 59 GiB on Oct 12) and `/var/lib/docker` + `/var/lib/containerd` at 22 GiB each on root. At the recent ~2–5 GiB/day net burn the 20 GiB threshold is roughly 1–2 weeks out if nothing changes; the guard's own reclaim cannot free root once keep-2 is satisfied. No action taken this run (read-only).

### RES-P2-001 — Host memory/swap pressure — open (unchanged; fluctuates around the same level)

- 48 h Prometheus (`falcon_host_memory_available_percent`): min 17.77%, max 47.2%, avg 32.79%; current metric 28.97% (`falcon_metrics.prom`, fresh 00:36Z; `free -m`: 4,055/14,230 MiB available). `falcon_host_swap_used_percent`: min 19.45%, max 63.15%, avg 51.76%; current 52.76% (~4.3 GiB of 8 GiB).
- 0 kernel OOM/kill lines since 2026-10-09; no alert rule currently firing; the Grafana relay shows no "Host memory pressure" delivery since Oct 9 (the only memory deliveries were the new "Container memory high" rule on Oct 11). However journald logged "Under memory pressure, flushing caches" 12×/142×/18× on Oct 11/12/13 — pressure events continue.
- Residual unchanged: the measured envelope is stale (`docs/phase5/PERFORMANCE_ENVELOPE.md:10-11` still "4 vCPU, 11.7 GiB RAM … 74 GiB root + 59 GiB data", last changed 2026-10-01); central/probe/opencanary have compose memory limits, but the adopted IRIS/Wazuh trees still carry no repo-side requests/limits (live caps only).

### RES-P2-002 — Wazuh VPN proxy socket boot race — verified-fixed (no regression; boot-proof still pending)

- Repo: `config/systemd/falcon-wazuh-agent-proxy.socket:12` and `falcon-wazuh-enroll-proxy.socket:12` set `FreeBind=yes`; the `After=wg-quick@wg0` ordering stays removed (comment `:2-8`); `boot_order_check.sh` still checks the `multi-user.target` links and is wired into `post_reboot_verify.sh`.
- Live: both sockets `enabled`/`active (listening)` since 2026-10-11 05:04:53; listeners on `10.99.0.1:15141` and `10.99.0.1:15140` (systemd/socket-proxyd).
- The previous run's doc gap (N-3) is closed: `docs/runbooks/VPN.md:193` now documents the FreeBind fix and that the 2026-09-30 ordering fix did not survive the reboot.
- Caveat (non-blocking): no reboot since the fix (boot ID 0 from 2026-10-11 02:27:44, uptime 2d22h) — the next reboot is the final proof.

### RES-P3-001 — Failure-injection coverage — open (unchanged)

- Still no aggregator-OOM, host-memory, boot-order/socket or root-LV injection test: `automation/validation/tests/` (54 files) has no such drill; grep for OOM/boot_order in the tests dir is empty.
- Test diff `3623d2e..edbf441` = 3 files / +193 lines: `ci_run_watchdog_test.sh`, `dlq_replay_test.sh`, `owner_env_validator_test.sh` — none of the four occurred failure classes.

### RES-P3-002 — Post-reboot verification — open (partially addressed; unchanged)

- Progress (from 2026-10-11): a post-reboot verification was run and recorded — 59 passed / 0 failed (`ledgers/decision_log.md:268`), and `post_reboot_verify.sh` now includes the socket boot-order check.
- Still missing: no boot-time automation — `config/systemd/` contains no post-reboot/boot-check unit or timer (the only new timer, `falcon-ci-watchdog.timer`, is CI-scoped); `post_reboot_verify.sh` remains a documented manual root step (`docs/runbooks/OPERATOR_START_HERE.md:102`). No reboot has occurred since 2026-10-11 (uptime 2d22h), so the 59/0 record is still the most recent run.

---

## New findings

No new findings this run. Status of the four carried new findings from the 2026-10-12 verification:

- **N-1 (live drift 0→1) — closed.** `live_image_pin_check.sh`: 27 containers, `drift=0`; the forwarder now runs `python:3.12-alpine@sha256:4c47124a…` (recreated with the locked tag@digest reference, `ledgers/decision_log.md:276`).
- **N-2 (live Wazuh compose hardcoded indexer password) — closed.** `/opt/wazuh-docker/multi-node/docker-compose.yml` now interpolates `${INDEXER_PASSWORD}` (1 interpolated / 0 literal) and is mode `0640`; the `.env` is `0600`.
- **N-3 (VPN runbook stale) — closed.** `docs/runbooks/VPN.md:193` documents the FreeBind fix and the failed 2026-09-30 ordering attempt.
- **N-4 (decision-log healthcheck overstatement) — closed.** `ledgers/decision_log.md:276` corrects the record to "26/27 … no-new-privileges … and 19/27 have healthchecks".

Watch item (residual of RES-P1-002/INFRA-P2-005, not a new finding): root-LV free is declining again (~2–5 GiB/day since Oct 12; 45.3 GiB now) with the snapshot repo (62 GiB) still on the root LV; if the trend holds, the 20 GiB guard threshold is roughly 1–2 weeks out and the guard's reclaim order cannot free root at keep-2. Suggested follow-up (unchanged from the original finding): move/limit the snapshot repository or add a bounded reclaim (containerd prune) to the guard.
