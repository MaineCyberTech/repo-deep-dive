# Post-merge verification re-audit — PERF / OBS / NOTIF findings

- Repo (read-only): `/home/user/falcon-build` @ `edbf441` (clean; live exporter confirms `falcon_runtime_source_info{commit="edbf441",dirty="0"}`), branch `main`.
- Date: 2026-10-14 (live checks 00:30–00:55 UTC).
- Original audit: `falcon-20261011-0416-full-f5cb7c9` (126 findings); previous verification @ `3623d2e` (2026-10-12).
- Scope: the 16 PERF / OBS / NOTIF findings in `scope-95.json`.
- Method: read-only. Repo inspection at `edbf441` (`git show`, grep, set-compares); live reads via the lab sudo pattern — `journalctl`, `systemctl`, `docker inspect`, `/srv/falcon/textfile/*.prom`, Grafana provisioning/alert APIs + Prometheus datasource proxy (GET only), `df`/`du`/`find`. No secrets printed, no state changed.
- Substantive commits since `3623d2e` checked: `f82f82f` (projection window 6h→24h + WH-P1-001), `96d722a`/`55a84df`/`73f2d8e` (WZ-VOLUME + catalogue 94), `e15c731` (Wazuh indexer source), `d61b493` (alert triage + silences), `ce76ef0` (live-tree reconcile), `11623a1` (edge pin).

**Result: 8 verified-fixed, 2 partially-fixed, 6 open, 0 regressed. No new defects.**

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| PERF-P1-002 | P1 | verified-fixed | **verified-fixed** | root free 48.3 GB (45.0 GiB) at 00:50Z; guard `ok` continuously (last BELOW 2026-10-11T04:30Z; 195 ok runs since 10-12); keep-2 live (2 `snap-*.dat`); `reclaims_total 51` |
| NOTIF-P2-002 | P2 | open | **open** | noise low (8 publishes 10-13; 1 on 10-14 by 00:53Z — the real site-disk firing); dominant source gone; relay still rate-limit only (`ntfy_relay.py:351-378`), no dedupe/same-title window; repeat 4h; 7-day re-measure still not run |
| OBS-P2-001 | P2 | verified-fixed | **verified-fixed** | live Grafana 94 = catalogue 94 = script 94 (set-compare empty both ways); all 94 live expressions match the script; README/CURRENT_STATE "94"; residual NF-6 unchanged |
| OBS-P2-002 | P2 | partially-fixed | **partially-fixed** | WZ-VOLUME rule live (expr 0; median guard unarmed until ~10-17) + indexer source (763/5m); 3 triage silences active; repeat 4h / Suricata not reboot-aware / 7-day accounting still open |
| OBS-P2-003 | P2 | verified-fixed | **verified-fixed** | `edge_ingest` exclusion intact (`export_monitor_metrics.sh:85-90`, `:555-557`); live all-errors 0 / edge-ingest 0; no firing since 10-11T04:21Z |
| OBS-P2-004 | P2 | verified-fixed | **verified-fixed** | `falcon_backup_service_state 0`; failed(5m)+stuck(8h) rules live; 10-13 run 03:30:03→05:45:47 success; residual: no RuntimeMaxSec, no generic unit rule |
| PERF-P2-001 | P2 | open | **open** | mem avail 28.97 % / swap 52.76 %; caps live for the named stacks; 2 uncapped containers; bars <20 %/15m & >75 %/30m unchanged; envelope/capacity-model docs still stale |
| PERF-P2-002 | P2 | verified-fixed | **verified-fixed** | guard 24 GiB (`disk_guard.sh:22` + live journal); warn rule 30 GiB live; no watermark commits in range; NF-1 doc numbers now fixed |
| PERF-P2-006 | P2 | verified-fixed | **verified-fixed** | `/var/tmp/wz-migration` absent; archive `wazuh-stack.tar` 23,273,175,040 B + README present |
| PERF-P2-007 | P2 | verified-fixed | **verified-fixed** | live projection rules use `[24h]` (repo `90-alerting.sh:561-566`; f82f82f apply evidence); root projection +21.2 GB (clear); data projection firing 22:39Z (real signal); root-free-low <20 GiB live |
| NOTIF-P2-001 | P3 | open | **open** | `ntfy-auth` absent repo + live Traefik; residual unchanged: `ntfy_htpasswd` still mounted/generated, 2 runbooks still describe it |
| NOTIF-P3-003 | P3 | partially-fixed | **partially-fixed** | 97 fallback + PORT_PROTOCOL_MATRIX correct; EX-20/R-24 still name the retired host as historical rows |
| PERF-P3-001 | P3 | open | **open** | no commits to PERFORMANCE_ENVELOPE.md / STORAGE_CAPACITY_MODEL.md in range; cost register 4× `owner: invoice`; no perf budgets |
| PERF-P3-002 | P3 | open | **open** | 120 s cadence live; exporter still has no self-runtime metric; whole-cluster queries unchanged |
| PERF-P3-008 | P3 | verified-fixed | **verified-fixed** | `validate.yml:43-55` cache steps intact; CI run 38485693681 (head `edbf441`) success with pip + falcon-ci-tools cache hits |
| PERF-P3-009 | P3 | open | **open** | counter 2,817,148,556 (21 purges/33 rotations) ⇒ ≈215 MB/day; no spool consumer (live or repo); 256 MiB/6h rule cannot fire at ~134 MB/rotation |

---

## Per-finding detail

### PERF-P1-002 — Root LV below the guard's 20 GiB threshold — **verified-fixed**
- Root free at 00:50Z: `df -B1 /` = 48,331,386,880 B free (45.0 GiB, 73 %); data LV 68.4 GB free.
- Guard journal: `ok: above thresholds, nothing to do` continuously — last `BELOW THRESHOLD`/`still below` line remains **2026-10-11T04:30Z**; 195 `ok` runs since 2026-10-12T00:00Z, latest 2026-10-14T00:30:03Z (`falcon-disk-guard.service` exit 0).
- Reclaim/retention path unchanged at `edbf441`: `automation/validation/disk_guard.sh:25` `KEEP_SNAPSHOTS=2`, `bootstrap/85-backup-job.sh:69-75` keep newest 2. Live repo has exactly 2 snapshot metas (`snap-*.dat`) in the 62 GB `/var/lib/falcon-snapshots/opensearch`; `falcon_disk_guard_reclaims_total 51` (no new reclaim needed).
- The audit's failure mode (sub-threshold root + 15-min paging) has not recurred since 2026-10-11T04:45Z. Transient note: root dipped ~3.6 GB in the last 2 h because a concurrent session wrote a 3.1 GB pi-image under `/tmp/opencode/pi-image` (not repo work; still 25 GiB above the threshold).

### NOTIF-P2-002 — Notification noise / no suppression — **open**
- Noise is low, the dominant source is gone, but the structural gap is unchanged:
  - Relay journal (main path): Oct 11 = 43 publishes, Oct 12 = 27, **Oct 13 = 8** (pipeline e2e 03:42/03:51; live-tree 20:02→23:23; pair-state drift 23:23→23:38; data projection 22:39), **Oct 14 = 1 through 00:53Z** (`Site host disk high` FIRING 00:51:28Z, both paths — see O-2).
  - `Falcon disk guard: root still below threshold`: last FIRING 2026-10-11T04:30Z (none since).
  - Sub-4h same-title repeats in the retained journal: 8 total, all on 10-11/10-12 (last `Container unhealthy` burst 10-12T19:04–19:25Z during the stack recreate); none on 10-13/10-14.
- Unchanged: `automation/alerting/ntfy_relay.py` publishes every webhook synchronously; the only control is the per-source sliding-window rate limit (`:57-59`, `:351-378`, 120 POSTs/60 s); no dedupe key / same-title suppression window (handler `:398-433`); live policy still `group_by [alertname]`, `group_interval 1m`, `repeat_interval 4h`; `disk_guard.sh:64-81` `alert()` still has no rate limit; the documented 7-day noise accounting has still not been re-run.

### OBS-P2-001 — Catalogue/README/CURRENT_STATE vs live Grafana — **verified-fixed**
- Live Grafana (`/api/v1/provisioning/alert-rules`) = **94 rules**; `docs/phase9/ALERT_CATALOGUE.yaml` = 94 ids; `bootstrap/90-alerting.sh` = 94 `write_rule` calls (95th match is the function definition). Set-compare live↔catalogue↔script is empty in **both directions** for all three pairs.
- Stronger than before: all 94 live expressions match the script expressions exactly (whitespace-normalized compare, 0 mismatches) — the 6h→24h projection change and the WZ-VOLUME rule are both live and in the catalogue (`73f2d8e` regenerated; catalogue `review_date: 2026-10-13`).
- `README.md:32` = "94 alert rules"; `docs/CURRENT_STATE.md:112` = "94 rules live".
- Residual (NF-6) unchanged: `alert_rule_lint_test.sh` is still script-only (count/dup/balance) and `readme_ledger_drift_test.sh:64-77` still compares README **counts** to the catalogue — no automated id/expression check (the "cannot drift" docstring stays unenforced).

### OBS-P2-002 — Alert noise; disk-guard storm; reboot artifacts — **partially-fixed**
- Noise fixed/quiet: 8 publishes on 10-13; 10-14 has 1 so far (the genuine `Site host disk high` firing, 00:51:28Z — O-2); no sub-4h flapping since 10-12T19:25Z; the disk-guard root storm is gone (see PERF-P1-002).
- New detection + triage landed: WZ-VOLUME rule `falcon-wazuh-alert-volume-drop` live (for 1 h; expression = the bool-product form, current value 0; its 7-day median is 0 until ~10-17 so it is intentionally unarmed — recorded in `ALERT_TRIAGE_2026-10-13.md`); the indexer source fix is live (`falcon_wazuh_alerts_5m 763`, high-severity 0); `d61b493` triage added 3 commented silences (2 retired WireGuard peers + the Wazuh feed) expiring 2026-10-20T22:30Z — all three verified active in the live Alertmanager.
- Still open (unchanged at `edbf441`): notification policy `repeat_interval 4h` (live), `falcon-suricata-restart-loop` is still uptime-reset based (`90-alerting.sh:436-438`) so a planned reboot would still produce the 10-11-style artifact (no reboot since 10-11T02:27Z to re-test), and the documented 7-day noise accounting has not been re-run.

### OBS-P2-003 — Pipeline counters rule fires on benign rejections — **verified-fixed**
- `automation/validation/export_monitor_metrics.sh:85-90` still excludes `edge_ingest` `http_server` errors from the data-loss sum and exports them separately (`:555-557`).
- Live textfile: `falcon_pipeline_all_errors_total 0`, `falcon_pipeline_edge_ingest_errors_total 0`, `falcon_pipeline_all_discarded_events_total 0`.
- Live rule expression unchanged (`(increase(all_discarded[15m]) > bool 0) + (increase(all_errors[15m]) > bool 0)`); relay journal shows no `Pipeline discarded/error events` firing since the 2026-10-11T04:10–04:21Z incident (the only pipeline-family event since is the unrelated `Pipeline end-to-end assertion failed`, 10-13T03:42→03:51Z).

### OBS-P2-004 — Stuck backup / failed unit detection — **verified-fixed**
- Live `falcon_backup_service_state 0`; rules `falcon-backup-unit-failed` (state==2, 5m) and `falcon-backup-stuck-activating` (state==1, 8h) are live with expressions matching the script (`90-alerting.sh:695-703`).
- 2026-10-13 run: activating 03:30:03Z → `Finished` 05:45:47Z (snapshot SUCCESS 03:39:24Z, ~2 h 15 m, well under 8 h); `systemctl --failed` shows only unrelated `fwupd*` units.
- Residual unchanged: `config/systemd/falcon-backup.service` still has only `TimeoutStopSec=900` (no `RuntimeMaxSec`/watchdog), and there is still no generic failed-systemd-unit rule (backup-specific only).

### PERF-P2-001 — Host memory/swap pressure, uncapped stacks, stale docs — **open**
- Live: `falcon_host_memory_available_percent 28.97`, `falcon_host_swap_used_percent 52.76` (3.9–4.2 GiB of 8 GiB); pressure persists as at audit.
- Caps live (docker inspect `HostConfig.Memory`): wazuh indexers 3×2 GiB, master/worker 2×1 GiB, dashboard 768 MiB, IRIS app 1 GiB / db+worker+rabbitmq 512 MiB / nginx 256 MiB, OpenCanary 256 MiB. Still uncapped: `falcon-wazuh-forwarder`, `wazuh-cloudflared`.
- Alert bars unchanged and still below observed values: `falcon-host-memory-low < 20 %/15m` and `falcon-swap-high > 75 %/30m` (both live).
- Docs still stale: `docs/phase5/PERFORMANCE_ENVELOPE.md:10-11` (4 vCPU / 11.7 GiB / 74+59 GiB, 2026-09-21) and `docs/architecture/STORAGE_CAPACITY_MODEL.md:7-8` (Phase-0 74/60 GiB) — zero commits in `3623d2e..edbf441`; the repo's vendored `automation/wazuh/multi-node/` compose still has no `mem_limit` (caps live only in `/opt` overlays — NF-4 residual).

### PERF-P2-002 — Data-LV thresholds vs OpenSearch watermarks — **verified-fixed**
- Guard default 24 GiB (`automation/validation/disk_guard.sh:22`; live journal `threshold=25165824KB`), warning rule 30 GiB live (`falcon-data-lv-low` = `falcon_disk_guard_free_bytes < bool 32212254720`, matches repo `90-alerting.sh:557-559`).
- No commits in `3623d2e..edbf441` touch OpenSearch watermark settings (grep over `config/opensearch` + `bootstrap`); the 2026-10-12 verification of default 85/90/95 % still holds, so the ordering (warn 30 → guard 24 → high ~22.1 → flood ~11 GiB free) is correct.
- The NF-1 residual from the previous pass is now fixed: `docs/runbooks/CAPACITY_AND_TELEMETRY.md:21,39-44,50,340-344` now says 24 GiB guard / 20 GiB root / 30 GiB warn / keep-2 / both LVs.

### PERF-P2-006 — 21.7 GiB stale migration bundle — **verified-fixed**
- `/var/tmp/wz-migration` does not exist; `/srv/falcon/archive/wz-migration/` holds `wazuh-stack.tar` (23,273,175,040 B = 21.7 GiB, mtime 2026-10-11) + `README.md` (review by 2027-01-31). Root freed accordingly (see PERF-P1-002).

### PERF-P2-007 — Root-disk projection blind; no guard-threshold alert — **verified-fixed**
- **Projection window fix verified live**: `falcon-disk-projection` = `predict_linear(node_filesystem_avail_bytes{mountpoint="/",fstype!~"tmpfs|overlay"}[24h], 7 * 86400) < bool 0` and `falcon-data-projection` = `predict_linear(falcon_disk_guard_free_bytes[24h], 7 * 86400) < bool 0` — both match `bootstrap/90-alerting.sh:561-566` at `edbf441` (commit `f82f82f`); the apply evidence (`20261013T005408Z_perf-p2-007-projection-window-24h`) shows the live re-provision.
- Current values via the datasource proxy: root projection **+21.2 GB** (not firing — the 6 h sawtooth false positive class is gone); data projection **−13 to −16 GB** (firing; see below).
- `falcon-disk-root-free-low` (`falcon_disk_guard_root_free_bytes < bool 20971520`, for 15m) live; guard self-alert path (`disk_guard.sh:149-161`) intact. Residual: there is still no dedicated Grafana rule on "guard reclaim failed" (the guard alerts directly through the relay); unchanged since 3623d2e.
- **Known capacity signal** (task focus): `Data volume projected full within 7 days` FIRING at 2026-10-13T22:39:10Z (relay published 22:39:22Z, both paths), still Alerting at 00:55Z. Data LV: 221 GiB / 148 GiB used / 64 GB free (70 %); free fell 75.2→64.1 GB across 10-13 and the 24 h regression is negative — a genuine trend, not a sawtooth artifact (the 24 h window is exactly the fix). This is the expected capacity signal, not a false positive; the guard threshold (24 GiB) is far below current free.

### NOTIF-P2-001 — ntfy-auth dead middleware — **open**
- `config/traefik/dynamic.yml:26-28`: `ntfy-auth` still deleted (comment records NOTIF-P2-001/SEC-P2-001); live Traefik's mounted file contains the same comment and no middleware; no router references it; lab ntfy remains internal-only with native deny-all.
- Residual unchanged (why this stays open): `ntfy_htpasswd` is still mounted into Traefik (live `docker inspect` mount; `compose/central/docker-compose.yml:35`) and generated (`bootstrap/50-secrets.sh:87-97`); runbooks still describe the removed middleware (`docs/phase7/runbooks/CERTIFICATE_AND_SECRET_ROTATION.md:47`, `docs/runbooks/ACCESS_AND_ACCOUNTS.md:48,105`). No change since 3623d2e.

### NOTIF-P3-003 — Retired lab-ntfy hostname references — **partially-fixed**
- `bootstrap/97-cloudflare-api-config.sh:58-62`: fallback lists falcon/iris/enroll + the retired-host note (fixed, unchanged at `edbf441`); `docs/architecture/PORT_PROTOCOL_MATRIX.md:38` N-21 row describes `ntfy.mainecybertech.us` + internal lab ntfy + retired hostnames.
- Remaining references are the historical ledger rows: `ledgers/exception_register.md:29` (EX-20, OPEN) and `ledgers/risk_register.md:31` (R-24 updated) still name `falcon-ntfy.mainecybertech.us`. Unchanged since 3623d2e; the finding itself accepted these as historical records.

### PERF-P3-001 — Stale envelope / capacity model / cost register — **open**
- `git log 3623d2e..edbf441 -- docs/phase5/PERFORMANCE_ENVELOPE.md docs/architecture/STORAGE_CAPACITY_MODEL.md` = empty. `PERFORMANCE_ENVELOPE.md:10-11` still the 2026-09-21 measurement (4 vCPU / 11.7 GiB / 74+59 GiB); `STORAGE_CAPACITY_MODEL.md:7-8,14-21` still the Phase-0 plan.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md:64-82`: the cost register still has every unit-cost/budget cell as `owner: invoice` (4 cells); no ingest-lag / snapshot-duration / exporter-runtime / root-free budgets exist.

### PERF-P3-002 — Whole-cluster monitoring queries / no runtime budget — **open**
- Cadence 120 s live: `falcon-metrics.timer` last 00:36:05 → next 00:38:05 (121 s delta); `config/systemd/falcon-metrics.timer:6` `OnUnitActiveSec=120`.
- The exporter still publishes no self-runtime metric — `falcon_metrics.prom` has only `falcon_runtime_source_*` (repo-commit state) and `falcon_metrics_last_run_timestamp_seconds`; the whole-index `max(timestamp)` per-feed aggregation and the other cluster queries still run every 120 s (the WZ-VOLUME fix added two indexer `_count` queries per run). No runtime budget/alert exists.

### PERF-P3-008 — CI dependency/tool caching — **verified-fixed**
- `.github/workflows/validate.yml:43-55`: `setup-python` with `cache: pip` + `cache-dependency-path`, and pinned `actions/cache@0057852b…` for `~/.cache/falcon-ci-tools`; each tool step checks the cache before downloading.
- Live proof at the audited head: CI run **38485693681** (`head_sha edbf441`, conclusion success) — "Cache restored from key: setup-python-…" and "Cache restored from key: falcon-ci-tools-actionlint-1.7.12-shellcheck-0.10.0-ruff-0.16.9-gitleaks-8.30.1" (23 MB).

### PERF-P3-009 — Edge spool purge counter meaning / no consumer — **open**
- `falcon_edge_spool_purged_bytes_total 2,817,148,556` (21 purges / 33 rotations) vs 2,548,743,849 / 19 / 30 on 2026-10-12 ⇒ +268,404,707 B in ~30 h ≈ **215 MB/day**, still advancing.
- No live consumer: no running container mounts `/home/user/falcon-edge-secrets/ingest` (checked every container's Mounts); no repo config in `falcon-build` reads the spool path, and no consumer found in the `falcon-edge-build` tree either.
- The provisioned rule `falcon-edge-spool-purge-burst` (256 MiB/6h, `90-alerting.sh:630-632`) cannot fire at ~134 MB per routine rotation. The data-loss interpretation still needs edge-side confirmation.

---

## New findings

**No new defects were found.** Two observations (not defects), for awareness only:

| # | Sev | Observation | Evidence |
|---|---|---|---|
| O-1 | — (known signal) | Data-LV capacity: `Data volume projected full within 7 days` is Alerting (fired 2026-10-13T22:39:10Z, still active). This is the known capacity signal the task flagged — rule expression verified as the 24 h `predict_linear` form, current value −13 to −16 GB, data LV 70 % used / 64 GB free. No action needed beyond the owner's existing capacity watch. | live Grafana rules + Prometheus proxy; relay journal 22:39:22Z |
| O-2 | P3 (watch) | The independent-site host (DO, `site=do-server`) root filesystem is back at **86.1 %** and rising — `Site host disk high` **fired 2026-10-14T00:51:10Z** (published 00:51:28Z, both paths); it fired 10-12 00:47→03:12 and 18:12→18:20, was cleaned to 67.5 %, and has climbed steadily since (48 h: 67.5→86.1). The independent ntfy + dead-man watcher live there; the existing rule covers it, but the growth is real. Cross-ref the site-host findings outside this scope. | `falcon_site_filesystem_used_percent` 86.1; relay journal 10-12 + 10-14T00:51Z |

*No regressions were found in PERF/OBS/NOTIF at `edbf441`*: every remediation from the 2026-10-11/12 batches is still present and functioning (guard margin, threshold band, root-free rule, projection window, exporter exclusion, backup-state rules, CI caching, middleware removal), and the new 2026-10-13 batch (WZ-VOLUME rule + indexer source, catalogue 94, triage silences, live-tree reconcile) is live and consistent with the repo. The still-open items are the audit's own residual clauses, not new breakage. Evidence caveat: the relay journal only retains entries from 2026-10-11T00:08Z onward, so noise comparisons use that window.
