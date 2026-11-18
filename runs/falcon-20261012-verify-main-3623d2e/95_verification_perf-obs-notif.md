# PERF / OBS / NOTIF post-merge verification — falcon @ 3623d2e

- Repo (read-only): `/home/user/falcon-build` @ `3623d2e` (clean working tree; current main).
- Audit under verification: `falcon-20261011-0416-full-f5cb7c9` (audit commit `f5cb7c9`, 126 findings).
- Scope: the 16 PERF / OBS / NOTIF findings.
- Live checks: read-only (`docker inspect`/`docker logs`/`journalctl`, textfile metrics under
  `/srv/falcon/textfile`, Grafana GETs via `grafana.falcon.lab` + CA, OpenSearch
  `_cluster/settings` GET). No secrets printed; no state changed.
- Check time: 2026-10-12 ~19:45–20:25 UTC.

**Result: 10 closed, 6 still-open (all partially remediated — remains listed), 0 regressed.**

| ID | Sev | Audit status | Verdict @ 3623d2e | Key evidence |
|---|---|---|---|---|
| PERF-P1-002 | P1 | verified-fixed | **closed** | root free 51.4 GiB (`falcon_disk_guard_root_free_bytes 55140241408`); guard `ok` since 2026-10-11T04:45Z (158 consecutive ok runs); keep-2 in `automation/validation/disk_guard.sh:25` + `bootstrap/85-backup-job.sh:69-75` (commit b9a8bd7); 2 snapshots on disk; bundle relocated |
| PERF-P2-001 | P2 | open | **still-open (partial)** | Wazuh/IRIS/OpenCanary caps live (docker inspect `HostConfig.Memory` 256M–2G); swap still 47.45 % used / mem avail 37.99 %; alert bars `<20 %/15m` & `>75 %/30m` unchanged (`90-alerting.sh:378,529`); `docs/phase5/PERFORMANCE_ENVELOPE.md:10-11` + `docs/architecture/STORAGE_CAPACITY_MODEL.md:7-8` still the stale 2026-09-21/Phase-0 numbers; 2 containers uncapped; overlays live-only (NF-4) |
| PERF-P2-002 | P2 | open | **closed (residual)** | guard 24 GiB (`disk_guard.sh:22`; journal `threshold=25165824KB`), warn rule 30 GiB live (`falcon-data-lv-low < 32212254720`); live watermarks default 85/90/95 % ⇒ guard acts at 24 GiB free < high-watermark 22.1 GiB; residual: `CAPACITY_AND_TELEMETRY.md` numbers stale (NF-1) |
| PERF-P2-006 | P2 | verified-fixed | **closed** | `/var/tmp/wz-migration` absent; `/srv/falcon/archive/wz-migration/wazuh-stack.tar` 23,273,175,040 B + README (cmp-verified, review by 2027-01-31); root freed 21.7 GiB |
| PERF-P2-007 | P2 | verified-fixed | **closed** | rule live: `falcon-disk-root-free-low` = `falcon_disk_guard_root_free_bytes < bool 20971520`, for 15m (uid verified via Grafana API) |
| PERF-P3-001 | P3 | open | **still-open** | no commits to `PERFORMANCE_ENVELOPE.md`/`STORAGE_CAPACITY_MODEL.md` in `f5cb7c9..3623d2e`; cost register cells still `owner: invoice` (`CAPACITY_AND_TELEMETRY.md:67-80`); no perf budgets |
| PERF-P3-002 | P3 | open | **still-open (partial)** | cadence 120 s live+repo (`config/systemd/falcon-metrics.timer:6`; timer last/next delta 121 s) + EVE `refresh_interval 30s` (`config/opensearch/falcon-eve-template.json:2007`); exporter still publishes no self-runtime metric/budget |
| PERF-P3-008 | P3 | open | **closed** | `validate.yml:39-52,56-101` cache steps (pip + pinned tools, actions/cache pinned); CI run 38299786463 steps "cache CI tools"/"Post cache CI tools" success |
| PERF-P3-009 | P3 | open | **still-open** | counter 2,548,743,849 B (19 purges/30 rotations) ⇒ +402.6 MB / ~34 h ≈ 284 MB/day; no container mounts the spool; no repo consumer; 256 MiB rule cannot fire at routine rate |
| OBS-P2-001 | P2 | verified-fixed | **closed (residual)** | live Grafana 93 rules; `ALERT_CATALOGUE.yaml` 93 ids = live ids (set-compare empty both ways); `README.md:32` "93 alert rules"; `CURRENT_STATE.md:112` "93 rules live"; residual: no script-vs-catalogue id check (NF-6) |
| OBS-P2-002 | P2 | partially-fixed | **still-open (residual)** | disk-guard root storm over (last FIRING 2026-10-11T04:30Z, 0 since); relay noise 39 unique FIRING/~44 h (vs 206/48 h at audit), 13/24 h; repeat_interval still 4h, no tuning (decision log 2026-10-12T04:30Z "proposed"); Suricata rule not reboot-aware (fired 02:39:28Z after the 02:24–02:27 planned reboot) |
| OBS-P2-003 | P2 | verified-fixed | **closed** | `export_monitor_metrics.sh:85-90` excludes `edge_ingest` errors from the loss sum, exported separately `:534-536`; live `falcon_pipeline_edge_ingest_errors_total 0`, `falcon_pipeline_all_errors_total 0`; no firing since 2026-10-11T04:21Z |
| OBS-P2-004 | P2 | verified-fixed | **closed (residual)** | `falcon_backup_service_state 0` live; rules `falcon-backup-unit-failed` (5m) + `falcon-backup-stuck-activating` (8h) live; 2026-10-12 run 03:30–04:22 success; residual: no `RuntimeMaxSec`, no generic unit-failure rule |
| NOTIF-P2-001 | P3 | still-open | **closed (residual)** | middleware deleted (`config/traefik/dynamic.yml:26-28` comment; live Traefik file has no `ntfy-auth`; no router references); residual: unused `ntfy_htpasswd` mount + 2 runbooks stale (NF-5) |
| NOTIF-P2-002 | P2 | still-open | **still-open (residual)** | dominant source gone (0 disk-guard root FIRINGs in ~39 h); noise low (13 unique/24 h); relay still has no dedupe/same-title window (`ntfy_relay.py` rate limit only); repeat 4h; 7-day re-measure not re-run |
| NOTIF-P3-003 | P3 | partially-fixed | **closed** | `bootstrap/97-cloudflare-api-config.sh:58-62` fallback now falcon/iris/enroll + retired note; `PORT_PROTOCOL_MATRIX.md:37-38` N-21 rows updated; EX-20/R-24 rows remain as historical records |

---

## Per-finding detail

### PERF-P1-002 — Root LV below the guard's 20 GiB threshold (P1) → **closed**
- Live root: `df -h /` = 112G used / 171G / **52G avail** (69 %); textfile
  `falcon_disk_guard_root_free_bytes 55140241408` (51.35 GiB).
- Guard journal: last `BELOW THRESHOLD` / `still below ... alert sent` at **2026-10-11T04:30:00/01Z**;
  `ok: above thresholds` continuously from **04:45:00Z** to 2026-10-12T19:45:03Z (158 ok runs,
  `systemctl status falcon-disk-guard.service` exit 0; `falcon_disk_guard_reclaims_total 51`).
- Reclaim path: snapshot retention 3→2 (`automation/validation/disk_guard.sh:25` KEEP_SNAPSHOTS=2,
  `bootstrap/85-backup-job.sh:69-75` keep newest 2; commit b9a8bd7); snapshot repo now 59 GB with
  2 snapshots (`.dat` files: Oct 11 03:37, Oct 12 03:36); 21.7 GiB bundle relocated (see PERF-P2-006).
- The audit's "no effective reclaim path" concern is resolved at the current state (keep-2 sawtooth
  plus the freed 21.7 GiB; root has not re-crossed the threshold since 04:45Z Oct 11).

### PERF-P2-001 — Host memory/swap pressure, uncapped stacks, stale envelope (P2) → **still-open (partial)**
Fixed:
- Memory caps are live for the named stacks (docker inspect `HostConfig.Memory`): wazuh indexers
  3×2 GiB, master/worker 2×1 GiB, dashboard 768 MiB, nginx 256 MiB; IRIS app 1 GiB, db/worker/rabbitmq
  512 MiB, nginx 256 MiB; OpenCanary 256 MiB; central stack already capped (OpenSearch 4 GiB, etc.).
  Declared in the live overlays `/opt/wazuh-docker/multi-node/docker-compose.hardening.yml` and
  `/opt/iris-web/docker-compose.hardening.yml` (applied via `docker update`), repo side:
  `compose/mct/docker-compose.opencanary.yml:31-34`.
Remains:
- Pressure persists: `falcon_host_memory_available_percent 37.99`, `falcon_host_swap_used_percent
  47.45` (3.8/8.0 GiB swap); no kernel OOM since boot (only a sudo command line matched "OOM").
- Alert bars unchanged and still below the observed values: `bootstrap/90-alerting.sh:378`
  (`<20 %`, 15m) and `:529` (`>75 %`, 30m).
- Docs stale: `docs/phase5/PERFORMANCE_ENVELOPE.md:10-11` still records the 2026-09-21 envelope
  (4 vCPU / 11.7 GiB / 74+59 GiB); `docs/architecture/STORAGE_CAPACITY_MODEL.md:1,7-8` still the
  Phase-0 plan; no memory budget exists in the tree; no commits to either file in `f5cb7c9..3623d2e`.
- Two containers remain uncapped (`wazuh-cloudflared` 25.6 MB, `falcon-wazuh-forwarder` 10.9 MB RSS).
- The cap overlays exist only in the live `/opt` trees, not in the repo's vendored
  `automation/wazuh/multi-node` (see New finding NF-4).

### PERF-P2-002 — Data-LV thresholds vs OpenSearch watermarks (P2) → **closed (residual)**
- Guard default now 24 GiB (`automation/validation/disk_guard.sh:22`; live journal line
  `threshold=25165824KB` from 2026-10-11T06:00Z), warning rule now 30 GiB
  (`falcon-data-lv-low` = `falcon_disk_guard_free_bytes < bool 32212254720`, live + catalogue).
- Live watermarks are the defaults with single-node enable: low 85 %, high 90 %, flood 95 %
  (OpenSearch `_cluster/settings?include_defaults=true`, 2026-10-12); on the 221 GiB data LV that is
  33.2 / 22.1 / 11.0 GiB free. Ordering is now correct: warning 30 GiB → guard reclaim 24 GiB →
  high watermark 22.1 GiB → flood 11 GiB.
- Residual: the threshold constants are still literals with no CI check tying them to the engine
  watermarks (finding clause), and the runbook numbers were left stale by the change (NF-1).

### PERF-P2-006 — Stale 21.7 GiB migration bundle on root (P2) → **closed**
- `/var/tmp/wz-migration` no longer exists. `/srv/falcon/archive/wz-migration/` holds
  `wazuh-stack.tar` (23,273,175,040 B = 21.7 GiB) and `README.md` (relocated 2026-10-11,
  cmp-verified before source removal, review by 2027-01-31). Root freed per `df`/guard metric.
- Repo record: `docs/runbooks/CAPACITY_AND_TELEMETRY.md:44-46` and decision log (362b342).
- Residual doc drift: `automation/wazuh/migration/README.md:17-19` still points at the old path (NF-3).

### PERF-P2-007 — No alert on the guard's root threshold (P2) → **closed**
- Live rule `falcon-disk-root-free-low` ("Root volume free space low"):
  `falcon_disk_guard_root_free_bytes < bool 20971520` (20 GiB), for 15m, warning — verified via the
  Grafana provisioning API (uid, expression) and `bootstrap/90-alerting.sh:666-668`.
- Warning band now consistent: `Disk space low` >85 % root (~25.7 GiB free) + the new 20 GiB rule +
  the guard's own alert. The projection rule remains as-is (it is trend-based, not threshold-based).

### PERF-P3-001 — Stale performance envelope / capacity model / cost register (P3) → **still-open**
- `docs/phase5/PERFORMANCE_ENVELOPE.md:10-11` still the 2026-09-21 measurement (4 vCPU / 11.7 GiB /
  74+59 GiB); `docs/architecture/STORAGE_CAPACITY_MODEL.md:1,7-8` still "Phase 0" (74 GiB root,
  60 GiB proposed data); zero commits to either in `f5cb7c9..3623d2e`.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md:67-80`: cost register exists but every unit-cost/budget
  cell is `owner: invoice`; no ingest-lag / snapshot-duration / exporter-runtime / root-free budgets.

### PERF-P3-002 — Whole-cluster exporter queries (P3) → **still-open (partial)**
- Remediated: metrics cadence 60→120 s (`config/systemd/falcon-metrics.timer:6`,
  `OnUnitActiveSec=120`; live timer last→next = 121 s; decision log 2026-10-12T04:30Z explicitly
  cites PERF-P3-002) and EVE `refresh_interval` 30 s
  (`config/opensearch/falcon-eve-template.json:2007` + all existing indices).
- Remains: the exporter still runs the whole-index `max(timestamp)` per-feed aggregation and the
  other cluster queries every 120 s, and it still publishes no self-runtime metric
  (`export_monitor_metrics.sh` has only `falcon_metrics_last_run_timestamp_seconds`), so no runtime
  budget/alert exists. The audit's second clause is unaddressed.

### PERF-P3-008 — No CI dependency/tool caching (P3) → **closed**
- `.github/workflows/validate.yml`: `setup-python` with `cache: pip` +
  `cache-dependency-path` (:39-41), `actions/cache` pinned `0057852b…` for
  `~/.cache/falcon-ci-tools` (:46-52), and each tool step checks the cache before downloading
  (:56-101). Commit 0575e8b.
- Live proof: validate run `38299786463` (head 3623d2e) — steps "cache CI tools" and
  "Post cache CI tools" both `success`.

### PERF-P3-009 — Edge spool purge counter meaning / no consumer (P3) → **still-open**
- Counter: `falcon_edge_spool_purged_bytes_total 2548743849`, 19 purges / 30 rotations
  (state `v1 30 19 0 2548743849 …`) vs 2,146,154,182 / 16 / 26 at audit ⇒ +402,589,667 B in
  ~34 h ≈ **284 MB/day**, still advancing.
- No live consumer: no running container mounts `/home/user/falcon-edge-secrets/ingest` (docker
  inspect over all containers); no open handles on the spool files (`fuser`); no repo config reads it.
- Rule `falcon-edge-spool-purge-burst` is 256 MiB/6h (`90-alerting.sh:613-615`); a single routine
  rotation is ~134 MiB, so it cannot fire at the observed rate. The audit's ask — edge-side
  confirmation of the data-loss semantics or a consumer — has not happened; the interpretation
  remains "unknown".

### OBS-P2-001 — Catalogue/README/CURRENT_STATE lag live rules (P2) → **closed (residual)**
- Live Grafana: **93 rules**. `docs/phase9/ALERT_CATALOGUE.yaml`: 93 ids; set-comparison against
  live uids is empty in both directions (scripted check). `README.md:32` "93 alert rules";
  `docs/CURRENT_STATE.md:112,132` "93 rules live".
- Residual: `alert_rule_lint_test.sh` parses only `bootstrap/90-alerting.sh` (derived count,
  duplicates, expression balance); `readme_ledger_drift_test.sh:64-77` compares README counts to
  catalogue counts. Nothing compares script rule **ids/expressions** to the catalogue, so a
  same-count substitution would drift silently (NF-6). The catalogue's "cannot drift" docstring
  holds only at regeneration time.

### OBS-P2-002 — Alert noise; disk-guard storm; reboot artifacts (P2) → **still-open (residual)**
- The dominant source is gone: last `Falcon disk guard: root still below threshold` FIRING
  2026-10-11T04:30Z; none since (guard passes; see PERF-P1-002). Relay journal (available since
  2026-10-11T00:08Z after the journal vacuum): 39 unique FIRING events / 78 path deliveries in
  ~44 h; last 24 h = 13 unique. Top current sources: Container unhealthy 4, Wazuh high-severity 3,
  Offsite backup stale 3, Data-volume projection 3, Container memory high 3 (the memory-high
  firings were all before the 14:36Z retune).
- Tuning landed: container mem 2→5 GiB, spool 64→256 MiB, wazuh feed 6→24 h, backup stuck 4→8 h
  (1328d70; live expressions verified). No firing of the re-tuned rules since.
- Remains: repeat-interval/grouping tuning still "proposed" (decision log 2026-10-12T04:30Z);
  live policy unchanged `group_by [alertname]`, `group_interval 1m`, `repeat_interval 4h`;
  the disk-guard `alert()` has no rate limit (`disk_guard.sh:64-81`); the Suricata rule is not
  reboot-aware — `falcon-suricata-restart-loop` fired 2026-10-11T02:39:28Z → resolved 03:29:33Z
  after the planned 02:24–02:27 kernel reboot (`90-alerting.sh:420-422`, unchanged); the documented
  7-day noise accounting was not re-run.

### OBS-P2-003 — Pipeline counters rule fires on benign rejections (P2) → **closed**
- `automation/validation/export_monitor_metrics.sh:85-90`: `edge_ingest` http_server component
  errors are excluded from the data-loss sum and exported separately as
  `falcon_pipeline_edge_ingest_errors_total` (`:534-536`); commit 3b0b976.
- Live textfile: `falcon_pipeline_all_errors_total 0`, `falcon_pipeline_edge_ingest_errors_total 0`.
- The rule expression is unchanged but now fed the clean signal; relay shows no
  `Pipeline discarded/error events` firing since the 2026-10-11T04:10–04:21Z incident.
- The lazy-counter reset behavior remains but is documented in the exporter comments (the finding's
  "document the reset behavior" ask).

### OBS-P2-004 — Stuck backup / failed unit detection (P2) → **closed (residual)**
- New metric live: `falcon_backup_service_state 0` (0 idle/done, 1 activating, 2 failed;
  `export_monitor_metrics.sh:98-106,531-533`); rules live:
  `falcon-backup-unit-failed` (state==2, 5m) and `falcon-backup-stuck-activating` (state==1, 8h,
  retuned from 4h by 1328d70). The new failed-rule proved itself: FIRING 2026-10-11T14:46:20Z →
  RESOLVED 14:49:20Z.
- 2026-10-12 nightly run: activating 03:30:03Z → success 04:22:44Z (~52 min, within normal);
  no stuck firing. `systemctl --failed` shows no falcon units.
- Remains: `config/systemd/falcon-backup.service` still has only `TimeoutStopSec=900` (no
  `RuntimeMaxSec`/watchdog), and there is still no generic failed-systemd-unit alert (only the
  backup-specific rule); the audit's "consider a textfile-based check of critical unit states" was
  not implemented.

### NOTIF-P2-001 — ntfy-auth dead middleware (P3) → **closed (residual)**
- `config/traefik/dynamic.yml:26-28`: `ntfy-auth` middleware deleted (comment records
  NOTIF-P2-001/SEC-P2-001); the live Traefik container's mounted file contains the same comment and
  no middleware; no router references `ntfy-auth` anywhere in the tree (grep). Commit e094473.
- Residual: the now-unused `ntfy_htpasswd` is still mounted into Traefik
  (`compose/central/docker-compose.yml:35`) and generated (`bootstrap/50-secrets.sh:87-97`); two
  runbooks still describe the removed middleware (NF-5).

### NOTIF-P2-002 — Notification noise / no suppression (P2) → **still-open (residual)**
- Noise is no longer high and the disk-guard root alert no longer dominates: relay journal
  39 unique FIRING / ~44 h (last 24 h: 13 unique); `Falcon disk guard: root still below threshold`
  last fired 2026-10-11T04:30Z (8 path-deliveries total in the retained journal, all that morning).
  Compare with the audit: 206 FIRING messages in 48 h.
- Remains: the structural items are untouched — the relay still publishes every webhook
  synchronously with no dedupe key or same-title suppression window (`automation/alerting/ntfy_relay.py`
  has only the per-source rate limit at `:355-371`), Grafana repeat_interval is still 4 h
  (`90-alerting.sh:141`), and sub-repeat flapping still occurs on transitions (e.g.
  `Container unhealthy` 4 FIRINGs within 24 min on 2026-10-12T19:04–19:28Z during the stack
  recreate). The finding's "record the 7-day noise measurement" was not redone after the fix.

### NOTIF-P3-003 — Retired lab-ntfy hostname references (P3) → **closed**
- `bootstrap/97-cloudflare-api-config.sh:58-62`: fallback guidance now lists falcon/iris/enroll and
  states "dash.falcon and ntfy.falcon are retired (API-P3-002 / NOTIF-P3-003, 2026-10-11)".
- `docs/architecture/PORT_PROTOCOL_MATRIX.md:37-38`: the N-21 current-path rows now describe the
  public ntfy as `ntfy.mainecybertech.us` (DO) with the lab ntfy internal-only and the retired
  hostnames noted — the previously queued row update landed (362b342).
- `ledgers/exception_register.md:29` (EX-20) and `ledgers/risk_register.md:31` (R-24 updated) still
  contain the retired hostname, but these are historical record rows (the finding itself accepted
  them as such); no live path uses the retired name.

---

## New findings

| # | Sev | Finding | Evidence |
|---|---|---|---|
| NF-1 | P3 | `docs/runbooks/CAPACITY_AND_TELEMETRY.md` was not updated by the 24/30 GiB threshold change (commit e094473 landed after the 362b342 docs pass): it still says the guard triggers below **10 GiB** on `/srv/falcon` (:39-40), calls it a **15 GiB warning band** (:21) and `falcon-data-lv-low` warns below **15 GiB** (:50), says "the disk guard watches `/srv/falcon` only" (:260) and "10 GiB / 20 GiB" (:273-274), and "keeps the newest 3" in the remediation section (:275-277). Live/repo are 24 GiB guard / 30 GiB rule / both LVs / keep-2. | `CAPACITY_AND_TELEMETRY.md:21,39-40,50,260,273-277` vs `disk_guard.sh:22-25`, `90-alerting.sh:540-542`, live journal `threshold=25165824KB` |
| NF-2 | P3 | The 120 s metrics cadence is not reflected in docs/units: `config/systemd/falcon-metrics.timer:1` description still "every minute"; `docs/runbooks/RUNTIME_AND_SCHEDULE.md:12` table cadence "1 min", `:81`/`:97` mention the 1-minute cadence, `:178` "Keep the 1-minute metrics cadence". | `config/systemd/falcon-metrics.timer:1-6`; `RUNTIME_AND_SCHEDULE.md:12,81,97,178`; live timer delta 121 s |
| NF-3 | P3 | `automation/wazuh/migration/README.md:17-19` still documents the bundle as living at `/var/tmp/wz-migration/wazuh-stack.tar` (and PVE copies) although it was relocated 2026-10-11 to `/srv/falcon/archive/wz-migration/` (review by 2027-01-31). | `automation/wazuh/migration/README.md:17-19` vs `/srv/falcon/archive/wz-migration/README.md` (live) |
| NF-4 | P3 | The Wazuh/IRIS memory-cap + hardening overlays exist only in the live `/opt` trees (`docker-compose.hardening.yml`, applied via `docker update`); the repo's vendored `automation/wazuh/multi-node/` compose has no `mem_limit`, so a repo-driven recreate would lose the caps added for PERF-P2-001. Two containers also remain uncapped (`wazuh-cloudflared`, `falcon-wazuh-forwarder`). Cross-ref CTR-P2-001 / ARCH-P2-002. | `grep mem_limit automation/wazuh/` = none; live `/opt/wazuh-docker/multi-node/docker-compose.hardening.yml`, `/opt/iris-web/docker-compose.hardening.yml`; `docker inspect` HostConfig.Memory=0 for the two containers |
| NF-5 | P3 | The removed `ntfy-auth` middleware is still described/rotated by runbooks and its users file is still mounted/generated: `docs/phase7/runbooks/CERTIFICATE_AND_SECRET_ROTATION.md:47` ("middleware `ntfy-auth`"), `docs/runbooks/ACCESS_AND_ACCOUNTS.md:48,105` ("currently unused"), `compose/central/docker-compose.yml:35` (ro mount), `bootstrap/50-secrets.sh:87-97` (generation). | paths as listed; live Traefik dynamic.yml has no such middleware |
| NF-6 | P3 | No automated check compares the provisioned rule set to `docs/phase9/ALERT_CATALOGUE.yaml` at id level: `alert_rule_lint_test.sh` is script-only (derived count, dup uids, expression balance) and `readme_ledger_drift_test.sh` compares README **counts** to the catalogue. A same-count rule substitution in `bootstrap/90-alerting.sh` would leave the catalogue stale and pass both tests (the catalogue header's "cannot drift" claim stays unenforced). | `automation/validation/tests/alert_rule_lint_test.sh:1-24,60-75`; `automation/validation/tests/readme_ledger_drift_test.sh:64-77` |
| NF-7 | P3 (observation) | `export_monitor_metrics.sh` `site_get()` emits `printf: write error: Broken pipe` when the DO site's metrics payload is large (awk exits at first match). Cosmetic only (script is `set -u`, no pipefail) but it litters the backup journal (6 lines in the 2026-10-12 run). | `automation/validation/export_monitor_metrics.sh:439`; `journalctl -u falcon-backup.service` 2026-10-12T04:22:43Z |

*No regressions were found in PERF/OBS/NOTIF:* the remediations that landed since the audit
(root-LV margin, threshold raise, rule additions, exporter exclusion, cadence change, CI caching,
middleware removal) are all present and functioning at `3623d2e`; the still-open items are the
audit's own residual clauses, not new breakage. One caveat on evidence windows: the lab journal
was vacuumed on 2026-10-12T04:30Z, so relay-noise comparisons are limited to entries after
2026-10-11T00:08Z.

### Method / commands (read-only)
- Repo: `git log/diff f5cb7c9..3623d2e`, file inspection (paths above), CI run inspection via the
  GitHub API.
- Live: `df -h`, `vgs`, `systemctl status/list-timers --failed`, `journalctl -u falcon-disk-guard|
  falcon-alert-relay|falcon-backup|falcon-metrics`, `docker inspect/ps/logs`, `fuser`,
  `/srv/falcon/textfile/*.prom`, Grafana provisioning/alert APIs (`--cacert` + `--resolve`),
  OpenSearch `_cluster/settings` GET.
