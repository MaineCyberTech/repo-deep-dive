# Falcon live monitoring lab — operations audit (2026-09-30)

Auditor role: operator/user of the running system. Scope: the live stack on host `falcon`
(VM 106 on the owner's Proxmox), not the repository. All checks were read-only: no service or
container changes, no restarts, no config edits, no writes to OpenSearch, no snapshot/restore
operations. The only remote interaction beyond reads was a read-only download of two offsite
backup objects to prove they are retrievable. Credential values were read where required and
never printed.

Audit window: 2026-09-30 03:20–03:55 UTC (lab uptime 1 d 12 h; host boot 2026-09-28 15:30 UTC).

---

## 1. Executive summary

- **The core pipeline is healthy and fast.** Feeds are flowing at normal rates, ingestion lag is
  sub-second to ~1.6 s, the dead-letter queue is empty (0 lines), Suricata has 0 kernel drops,
  and all user-facing service probes answer. OpenSearch is yellow as designed for a single node
  (33 unassigned replica shards), heap at 28 %, no rejections, no pending tasks.
- **Two real backup regressions were caught live today (2026-09-30 03:30–03:34 UTC):**
  the offsite Spaces sync failed, and the daily new-services backup reported failure. Both are
  *silent* — there is no alert or metric for either. The offsite cold tier is now one day stale
  (last success 2026-09-29 07:06 UTC). The offsite data itself is readable (verified by
  read-only download of the Sep 28/29 encrypted config backups).
- **Disk is the dominant near-term risk.** The data LV (`/srv/falcon`, 122 GB) is losing
  ~10 GB/day (58.3 GB free → 47.8 GB in 24 h) driven by ~4.4 GB/day of indices plus ~6 GB/day of
  rotated EVE files; the disk guard's 5 GiB threshold will be exercised in roughly 4–5 days.
  The root LV is at 82.2 % used (133/171 GB) with only a 85 % warning rule above it.
- **Alerting works but is dominated by noise.** Of 153 real alerts since Sep 22, **85 (56 %) are
  the "Syslog-TLS feed silence" alert flapping** roughly once an hour (the feed carries only
  ~1.3 Wazuh alert forwards/hour; 32 events/24 h). "Device syslog errors" also fires on benign
  UniFi broker/AP messages. Delivery itself is reliable and dual-path (lab ntfy + independent
  DO ntfy): all sampled relays returned 200 on both paths.
- **The 2026-09-28 4.5-hour power outage produced no real-time external notification** — the
  host died at 10:58 UTC and alerts only resumed at 15:32 UTC after recovery. The dead-man
  heartbeat is daily and runs *inside* the monitored stack; the independent DO watcher that
  observes it is not in the repository and is undocumented.
- **Runbooks drift from reality**: `SENSOR_SILENCE.md` still says "there is no VPN / no physical
  SPAN"; `DISK_PRESSURE.md` and `RESTORE.md` list stale capacities, snapshot names, and gaps that
  have since been fixed (and miss the disk guard and offsite flow). A new operator without root
  cannot run most of the documented commands (`docker` is root-only; `/srv/falcon/secrets` is
  root-only; even `wg show` is denied).
- **Monitoring-of-the-monitoring has gaps**: no freshness metric/alert for the metrics exporter
  timer itself, no swap alert, no alert on data-LV free space, no alert for offsite/new-services
  backup success, and peers that never handshaked are invisible to the WireGuard stale rule.

---

## 2. Method and access limitations

| Available | Not available (as non-root user) |
|---|---|
| Host `/proc`, `journalctl` (adm group), systemd unit states/timers | `docker` CLI (socket is root:docker; `sudo` needs a password) |
| Prometheus API (container IP 172.30.1.6:9090) | Grafana API (admin secret is root-only) — alert *state* reconstructed from webhook deliveries |
| OpenSearch API (container IP 172.30.3.2:9200) with least-privilege `falcon-healthcheck`; read-only GETs as `admin` | Wazuh API/manager credentials |
| node-exporter textfile metrics under `/srv/falcon/textfile` | Container logs (`docker logs`), `/srv/falcon/secrets`, `/srv/falcon/backups` logs |
| ntfy `cache.db` (read-only SQLite), relay webhook delivery log via journald | Offsite logs (`offsite.log`, `new-services.log`) |

Consequences: container *healthchecks* were inferred from the `falcon_unhealthy_containers`
textfile metric and process/netns introspection rather than `docker inspect`; Grafana alert
states were rebuilt by re-evaluating the provisioned expressions against Prometheus and from the
delivered notifications.

Note: `127.0.0.1:9200` on the host is the **Wazuh indexer**, not the falcon OpenSearch cluster.
The falcon cluster is only reachable inside the Docker networks (or via `docker exec` as root).
Runbooks correctly use `docker exec`, but a casual operator probing `localhost:9200` gets a 401
from a different cluster — worth a doc note.

---

## 3. Health and quality findings

### 3.1 Host

- Ubuntu 24.04, kernel 6.8.0-142, 6 vCPU, load ~1.9. RAM 15.2 GiB total (VM configured 24 GiB,
  ballooned down; PVE balloon floor 12 GiB), 9.5 GiB used, **swap 4.6–4.9 GiB / 8 GiB (≈59 %)**.
  Biggest swap consumers: 3× Wazuh indexer JVMs (~0.5 GB each), Suricata (~0.5 GB), OpenSearch
  JVM (~0.3 GB), IRIS celery workers (~0.15 GB each), `wazuh-modulesd`.
- Root LV: 171 GB, 133 GB used (**82.2 %**). The +75 GB step on Sep 27–28 corresponds to the
  Wazuh multi-node migration/IRIS/R2 work landing in Docker volumes on `/`. Growth is now
  ~0.2–0.3 GB/day but the warning threshold (85 %) is only ~5 GB away.
- Data LV: `/srv/falcon` 122 GB, **46 GB free (62 %)**, falling ~10 GB/day (see §3.3, §5.1).
- SPAN NIC `ens19`: UP, PROMISC, RX 164.6 M packets, 462 drops (0.0003 %), 0 errors.
- `wg0`: UP, 6 configured peers, 4 handshaking <2 min (`10.99.0.10/22/21/30`), 2 never
  (`10.99.0.2` lab netns test, `10.99.0.20` "samsung" client).
- Boot history confirms the recorded incidents: 5 boots in 45 min on Sep 27 21:44–22:28
  (PVE host OOM-killed the VM) and a 4.5 h outage Sep 28 10:59→15:30 (power). The journal was
  "corrupted or uncleanly shut down, renaming and replacing" on the Sep 28 boot — logs from
  before the outage are partially lost.

### 3.2 Containers and services

27 local containers (central 10, probe 2, Wazuh 8, IRIS 5, opencanary 1, wazuh-forwarder 1),
all present with fresh metrics: `falcon_unhealthy_containers 0`, `falcon_suricata_restarts_total 0`.
Service probes (2-minute timer): grafana, dash, ntfy, traefik, ntop, relay, iris, do-host,
do-ntfy-public all `1`; one transient `dash=0` at 03:33 (a 20 s timeout through Traefik), and
`do-host`/`do-ntfy-public` zeroed once at 05:49 Sep 29 (VPN-side blip). Grafana 13.2.2
(`/api/health` ok), OSD 2.19.6 healthy, Prometheus 3.14.0, 3/3 targets up (node-exporter,
prometheus, traefik — nothing else is scraped). Traefik shows no 5xx; only 1×403/2×404 per hour
(scanner noise). ntopng captures host `eth0`, CPU ~12 %.

### 3.3 OpenSearch cluster, indices, retention, gaps

- Cluster `falcon-central`: **yellow** (normal single node), 1 node, 52 primary shards,
  33 unassigned replicas (61 % active), no pending tasks, heap 28 %, no write/search rejections,
  data volume available per OpenSearch 36.5 GB. Repository `falcon-backup` `_verify` → OK.
- `falcon-*` totals: **55.27 M docs / 26.49 GB** store. Daily indices and docs:
  09.21 1.11 M · 09.22 2.95 M · 09.23 4.39 M · 09.24 5.12 M · 09.25 8.09 M · 09.26 8.19 M ·
  09.27 8.77 M · 09.28 6.75 M (outage) · 09.29 7.56 M · 09.30 1.26 M at 03:40.
- Retention: ISM `falcon-eve-policy` = **delete `falcon-eve-*` after 14 d**; 12 managed indices;
  the oldest (09.21) is deleted around **Oct 5**. There is **no automation to cold-copy indices
  to R2 before deletion** — only 09.21 was manually snapshotted to R2 and mounted as
  `falcon-eve-2026.09.21-searchable` (`remote_snapshot`, 1.11 M docs, not ISM-managed, 0 replicas).
  Everything else older than 14 d survives only as full snapshots in the fs repo / offsite Spaces
  (restore required, not searchable). Snapshot coverage is ~7 days, so a deleted index is
  restorable for about a week after deletion — this window is not documented anywhere.
- Snapshots: daily 03:30 job; today `snap-20260930-033005` SUCCESS (15 indices, 15/15 shards).
  The local repo keeps 10 snapshots (guard prunes to 3 only when disk <5 GiB; offsite keeps 7
  inventories). **Two snapshots are created per day** because both `85-backup-job.sh` and
  `80-offsite-backup.sh` create one (~3 min apart) — duplicated snapshot storage and upload.
- Clutter/leftovers: `falcon-test` (1 doc), `falcon-canary` (1), `falcon-eve-fixture-test` (1),
  `falcon-retention-test-20260922055012` (1 + alias), `other-site-index` (admin-only artefact),
  plus 11 `security-auditlog-*` and daily `top_queries-*` / `.opendistro-ism-managed-index-history-*`
  indices with **no retention policy**.
- Mapping drift: `event_type` is `keyword` on falcon-eve indices since 09.23 but text+keyword on
  the 09.21/09.22 (mon-eve) indices — `event_type.keyword` aggregations silently return nothing
  for new data. `host` is text-only on 09.29/09.30 (aggregations/sorts on it fail).

### 3.4 Feeds, pipeline, data quality

- Last 24 h counts: `flow_record` 3.07 M · `syslog` 1.84 M · Suricata `flow` 1.00 M ·
  `netflow_record` 0.98 M · Suricata `tls` 0.29 M · `dns` 0.26 M · `alert` 0.17 M ·
  `http` 0.08 M · `stats` 2 878 · `wazuh` 32.
- Rates (exporter): syslog 514 8 213/h · 15140 62 931/h · netflow 45 193/h · SPAN flows
  145 766/h · TLS 1/h · Suricata alerts 9 155/h (793/5 min) · kernel drops 0.
- Latency (sampled): aggregator lag 0.03–1.6 s; edge→aggregator sub-second for every feed.
- Hourly checks over 72 h show **no gaps** outside the Sep 28 outage; per-day feed volumes drop
  only in the outage window. DQS: **0 docs missing `site_id`/`sensor_id`** across all main feeds
  in 24 h; no DLQ lines (last DLQ files are zero-byte from Sep 22); probe buffer oscillates
  0.15 MB–132 MB (currently ~30 MB) against a 2 GiB cap — the doc statement "near zero in normal
  operation" is not accurate, though the safety margin is large.
- Suricata: uptime 84 113 s ≈ 23.4 h, i.e. **the engine restarts daily at the 04:19 EVE
  rotation**, while Docker `RestartCount = 0` — the "Suricata restart loop" rule cannot see these
  daily in-container restarts. `stats` events keep the freshness metric alive during such gaps.
- Wazuh integration: 147 / 306 / 28 / 7 events per day Sep 27–30, mostly levels 3–7; last
  level ≥10 event was Sep 28 (12, auth-failure class) — before the new high-severity rule was
  deployed (2026-09-30 00:55), so the rule has not fired live yet. Wazuh alert traffic arrives
  as `transport=tls` documents, i.e. the TLS syslog feed is now effectively the Wazuh forwarder.

### 3.5 Alerting path

- 30 Grafana-managed rules (folder `monitoring-lab`) are provisioned from
  `bootstrap/90-alerting.sh`; the catalogue `docs/phase9/ALERT_CATALOGUE.yaml` lists 29
  (misses `falcon-wg-peer-stale`). No Prometheus rules (Prometheus has 0; evaluation is Grafana's).
- Contact point: webhook → host relay `:9099` → ntfy. The relay dual-publishes to the self-hosted
  lab ntfy (`127.0.0.1:2586`) and the independent public path (`ntfy.mainecybertech.us`) — both
  observed returning 200 throughout today's TLS-silence flaps. Relay is a systemd unit with
  `Restart=on-failure` (restarted 00:54 and 02:51 today, config-change related).
- ntfy server: health 200, `auth-default-access: deny-all`, cache 48 h (cache currently holds 96
  messages).
- Heartbeat: `falcon-heartbeat.timer` publishes a daily "falcon lab alive" to the local topic
  (00:00:20 today, 200). It is explicitly a prototype that runs *inside* the monitored stack;
  the independent DO-side watcher (`/var/log/falcon-watcher.log` mtime is exported) is not in the
  repo. Detection latency for a total host failure is therefore measured in hours-to-a-day, and
  the Sep 28 outage was not announced in real time.
- Webhook delivery history (Sep 22 → Sep 30) captures 153 real alerts + synthetic drill alerts;
  no failed primary or alt publish was found.

### 3.6 Dashboards

- Grafana: 34 panels (Central Overview), 31 (Feeds Overview), 7 (Edge Fleet) — I re-ran every
  panel expression against Prometheus: **all but one return data**. The broken one is "Network
  throughput" (Central Overview): it queries `node_network_*{device=~"ens18|ens19|wg0"}`, but the
  containerized node-exporter only exposes its own netns (`eth0`, `lo`). Host NIC throughput is
  effectively unmonitored.
- OSD: index pattern + 9 saved searches + 2 dashboards (falcon-triage, host drill-down) exist in
  the `falcon-dashboard` private tenant; an unauthenticated/probing client sees nothing
  (tenant selection needed in the UI).

---

## 4. Runbook vs reality (operator tasks followed read-only)

**Task 1 — OPERATOR_START_HERE "Quick health checks".**
`central_health.sh all`, `probe_pipeline_test.sh`, `span_mirror_check.sh` all require root and the
`docker` socket; as the `user` account they are unusable (`docker` → permission denied; `sudo`
prompts for a password — the password happens to sit in `/home/user/.env`, which is itself a
finding). The 8 `falcon-*` timers were verified live and match the documented cadence
(metrics 1 min, probe 2 min, edge metrics 5 min, disk guard 15 min, backup 03:30, heartbeat
00:00). Verdict: docs are directionally right but assume a root shell that a new operator does
not automatically have. Also note `central_health.sh` *writes* test docs (`falcon-test`), so it is
not a read-only check despite living in `automation/validation/`.

**Task 2 — SENSOR_SILENCE.md checklist.**
I executed read-only equivalents of §3–§5: newest event age 2 s, index counts advancing,
buffer <1 % of cap, DLQ 0, Suricata healthy/uptime advancing, EVE path (Suricata) advancing,
clock synced. All good. But the runbook's "Known substitutions" are **stale and misleading**:
it says "there is no VPN (OD-05)", "there is no physical SPAN (OD-07) — the source is the
synthetic veth". Live reality: a real WireGuard hub with 6 peers and a real UniFi mirror feeding
`ens19`. Sections that instruct the operator to use `span-src` netns/`veth-span-b` and to record
"licensed flow source unavailable" would send a new operator down the wrong path. The runbook
also relies on root-only commands and a canary POST (a write). Undocumented: the daily Suricata
restart at EVE rotation, and the fact that the TLS feed carries Wazuh alert forwards.

**Task 3 — DISK_PRESSURE.md.**
Stale: the capacity table says `/` 73 G / `/srv/falcon` 59 G with 14 G unallocated; today it is
171 G / 122 G with everything allocated. It says "No Prometheus or Grafana alert rules are
provisioned; continuous disk alerting is an open P7-G08 gap" and elsewhere that continuous rules
*are* deployed (self-contradictory); the deployed thresholds are 85/92 %, not 80/90 %. It does
not mention the disk guard, the EVE file rotation (~6 GB/day), the Wazuh migration growth on `/`,
or the searchable-snapshot cache. Verdict: an operator following it would look for the wrong
things; the actual first-line control (guard at 5 GiB on `/srv/falcon`) is undocumented there.

**Task 4 — RESTORE.md readiness (no restore performed).**
Live state is better than the doc: daily scheduled snapshots exist (today SUCCESS, 15 indices),
`falcon-backup` repository `_verify` passes, an offsite Spaces copy exists (Sep 28/29 config
archives downloaded read-only and readable), the R2 searchable tier is mounted, and a dedicated
`falcon-backup` identity now exists. The runbook's asset table (Sep 21 filenames/sizes), the
"no scheduled backup" and "no offsite copy" gap list, and the manual procedures are outdated.
Real readiness gaps found: (a) **today's offsite sync failed**; (b) the **new-services backup
reported failure**; (c) the last clean-host rehearsal (Sep 23, 4.79 M docs restored, 10/10
containers) predates R2, Wazuh multi-node, IRIS and the edge sensor; (d) snapshot retention
(3 local/7 offsite) vs 14-day index retention leaves a ~1-week recoverability window that is
undocumented.

**Task 5 — VPN.md.**
Runbook commands (`wg show`, editing `wg0.conf`) are root-only; as the operator user they fail
("Operation not permitted"), and there is no documented non-root read path (the metrics exist —
`falcon_wg_peer_handshake_age_seconds`). The "Current production state" table is from Sep 24 and
lists only the DO peer; live has 6 peers (DO, 3 client endpoints, edge sensor, test peer).
The independent dead-man watcher is referenced only as a log file path in
`SITE_HOST_ONBOARDING.md`; its script, cadence and alert threshold are undocumented.

**Task 6 — WAZUH_INTEGRATION.md (spot check).**
The forwarder container is running, Wazuh alerts are landing (event_type=wazuh / transport=tls)
with sub-second puck-to-index latency. The TLS-silence rule makes this otherwise-good feed look
broken every hour (see §5.4). The decision log already flags the remaining owner action to
re-point desktop agents; nothing in the live system contradicted the documented wiring.

---

## 5. Failure modes

### 5.1 Single-host and resource risks

- Everything (ingest, storage, alerting, identity, VPN, SOC consoles) runs on one VM. The
  Proxmox host overcommit already killed this VM three times in one hour on Sep 27
  (OOM; hard resets, no shutdown). Mitigations are in place (VM balloon floor 12 GiB,
  `oom_score_adj=-500`, post-start hookscript, PVE swap file) but they depend on host settings
  the lab cannot verify from inside; the guest is currently ballooned to ~15 GiB and using 4.9 GiB
  of swap, so an adverse host-side event has little headroom.
- Data LV growth ~10 GB/day: OpenSearch indices ~4.4 GB/day + rotated Suricata EVE ~6 GB/day
  (one parked `eve.json.20260929T041939Z` was 6.2 GB; the live file was ~1 GB after <1 day).
  The disk guard only acts below 5 GiB free and has **never reclaimed** (`reclaims_total 0`);
  at today's rate it will first trigger in ~4–5 days, then enter a sawtooth. Nothing warns in the
  15→5 GiB band, and the root LV (82 %) is not guarded at all.
- Single-node OpenSearch with 14-day retention and manual-only R2 offload — data older than
  14 days is deleted; only 09.21 has a searchable cold copy.

### 5.2 Power-outage recovery

- Recovery worked (post-outage verification recorded 50 pass/0 fail; this audit's live checks
  agree). Residual issues: journal corruption lost pre-outage logs; `onboot=1` is now set but
  was not at the time; the Wazuh VPN proxy sockets race `wg0` at boot (fixed in the installed
  units; the workstream installer is still WIP per the decision log); and no alert fires while
  the host is down (see §5.4/§6).

### 5.3 Backup and restore readiness

- Local: snapshots daily SUCCESS (today 15/15 shards), repository `_verify` OK, encrypted config
  archive written 03:34 today.
- Offsite: **failed today at 03:34**, instantly ("offsite sync unavailable"); last complete
  upload 2026-09-29 07:06. The most likely cause is malformed `/home/user/.env` — line
  `wifi_ssid=The Internet` is an unquoted value with a space, and sourcing the file under
  `set -euo pipefail` exits 127 (verified). `80-offsite-backup.sh` sources `.env` without
  guarding; the failure needs root log confirmation but this is the only step that fails in the
  first second. Spaces itself is reachable (TCP/TLS OK) and read access with the .env keys works
  (Sep 28/29 encrypted config backups downloaded).
- New-services backup (WireGuard keys, Wazuh registry, IRIS, enrollment): the 00:46 manual run
  produced a 380 KB/217-entry archive but its own critical-item check printed `[MISSING]` for all
  four items, and the 03:34 automated run logged failure. The check greps absolute paths against
  `tar -tzf` output; the current script uses `--absolute-names`, so either one critical path is
  genuinely absent on disk or the verification is still wrong. This cannot be confirmed without
  the root-only log (`/srv/falcon/backups/new-services.log`).
- **Neither failure raised an alert** — `falcon-backup-stale` tracks only the local freshness
  timestamp, which today's 03:34 success refreshed.
- The R2 searchable tier works but covers one index and has no automation, no cache/eviction
  policy beyond the 8 GB search cache, and no failure alerting.

### 5.4 VPN and site dependencies

- DO site (10.99.0.10) and three client peers handshake continuously; site metrics and the
  DO notifier containers are up. The one-time 05:49 zero for `do-host`/`do-ntfy-public` shows the
  probes can flap with the tunnel.
- A configured peer that never handshakes (`10.99.0.20`) is invisible to the `wg-peer-stale`
  rule because the per-peer metric only exists for peers that connected at least once — a lost
  device would not alert.
- The independent DO watcher is the only external watchdog; its threshold/cadence is not in the
  repo, and the daily heartbeat bounds detection latency to ~a day for total-host failure.

### 5.5 Monitoring-of-the-monitoring gaps

| Gap | Evidence |
|---|---|
| Metrics exporter (1-min timer) has no heartbeat metric/alert; if it wedges, Prometheus keeps the last values and feed rules stop seeing reality | No `falcon_metrics_last_run` metric exists; `falcon-target-down` only covers node/prometheus/traefik scrapes |
| Service-probe results can freeze at `1` if the probe timer dies | `falcon_service_up` has no freshness companion |
| No alert on `/srv/falcon` free space band (15→5 GiB) or on root LV consumption by directory | Disk rules use `mountpoint="/"` only; guard alerts only below 5 GiB |
| No swap alert (59 % used now; OOM history) | No rule on `node_memory_SwapFree` |
| Offsite/new-services backup failures silent | Today's failures generated no notification |
| Grafana alert-evaluation health not checked | Probes only test HTTP liveness of Grafana |
| Peers that never handshake invisible | Only 4/6 peers emit metrics |
| Daily Suricata in-container restart invisible | `RestartCount` stays 0 while uptime resets |

---

## 6. Alert experience (sampled)

Source: relay webhook delivery log (journald, Sep 22→30), ntfy `cache.db` (last ~12 h) and live
re-evaluation of the provisioned expressions. Grafana's own state UI/API was not reachable
without the root-only admin secret.

- **Volume**: 153 real notifications in 8 days (plus ~850 synthetic storm/drill messages).
  Per day: 8, 7, 12, 9, 1, 16, 49, 42, 9.
- **Noise**: `Syslog-TLS feed silence` = 45 FIRING / 40 RESOLVED (**56 % of all real alerts**),
  flapping every ~30–45 min because the feed only carries ~1.3 Wazuh forwards/hour (32 events/24 h).
  It is technically true and practically useless; it buries real signal and would train an
  operator to ignore ntfy.
- **Observed true positives**: feed-silence alerts (SPAN/NetFlow/15140/514) and service/site-down
  exactly during the Sep 28 outage; capture-fidelity during the Sep 24/27 capture incidents;
  disk-low twice on Sep 28 (before cleanup); sensor-silence during the Sep 23 drill.
- **False/soft positives**: `Device syslog errors` fires on benign UniFi noise — an internal
  broker message (`unifi-mq-broker drop message due to rate limit`, every ~2 min) and an AP
  client-capability warning (`ieee80211_recv_asreq ... 7 RX MCS Rates supported`); 503 such
  messages in 24 h, and 4 FIRING/RESOLVED pairs since Sep 22.
- **Potential false negatives**:
  - Host "Zen" emits ~600 Link-Down syslog events/hour (≈50 per 5 min) continuously; the
    link-flap rule needs >300/5 min, so a chronic fault (likely one flapping port) never alerts.
  - The daily Suricata restart/uptime reset, swap pressure, exporter freshness, backup-path
    failures, and never-connected WG peers (above) have no alert.
  - During the 4.5 h outage no notification was emitted in real time; recovery immediately
    produced 4 feed-silence alerts plus service/site-down (15:32), which is after-the-fact.
- **Accuracy cross-checks against live data**: feed counters during alert windows match
  OpenSearch counts; the TLS-silence windows match the 0 events in 30 min; the "Disk space low"
  firings correspond to the then-rising root FS; the new `Wazuh high-severity` rule is correctly
  armed but untriggered (last level≥10 event predates its deployment).
- **Delivery**: primary and alt publishes returned 200 for every sampled notification; the
  heartbeat is delivered daily; resolve messages are enabled; repeat interval 4 h.

---

## 7. Prioritized recommendations

**P0 — today (operational correctness / data safety)**

1. **Fix the offsite backup**: quote the malformed `.env` value(s), re-run
   `bootstrap/80-offsite-backup.sh` (or tonight's timer), and confirm the inventory upload.
   Add a success/freshness metric + alert for offsite (e.g.,
   `falcon_backup_offsite_last_success_timestamp_seconds`) and for the new-services archive.
2. **Resolve the new-services backup failure**: read
   `/srv/falcon/backups/new-services.log` as root, confirm whether WireGuard keys / Wazuh
   `client.keys` / IRIS are inside the archive, and fix the verification (or the missing path).
   Until then the newest archival state is unproven.
3. **Data-LV growth**: automate EVE housekeeping (compress or delete rotated `eve.json.*` after
   the pipeline has consumed them, e.g. >12–24 h) and/or shorten ISM retention (14→10–12 d) or
   automate the R2 cold-offload step each day before ISM deletes an index. Add a warning alert
   at, say, <15 GiB free on `/srv/falcon` so the 5 GiB guard is not the first signal.
4. **Stop the TLS-silence flap**: raise the rule to a 6–12 h window or replace it with a check on
   the Wazuh forwarder/manager liveness; rename it to reflect that it is the Wazuh alert path.

**P1 — this week (monitoring integrity)**

5. **Root LV**: identify and clean Docker growth (`docker system df`, dangling layers), consider
   moving Wazuh volumes off `/`, and add a per-directory/root growth signal; 82 % → 92 % at
   current pace is ~3 weeks but the last jump was 75 GB in one night.
6. **Monitoring-of-monitoring**: add `falcon_metrics_last_run_timestamp` (exporter) and
   `falcon_service_probe_last_run_timestamp`; alert on staleness; add a swap-usage alert and an
   alert on `falcon_disk_guard_free_bytes`; add an external "Grafana alert evaluation alive"
   dead-man (e.g., a counter exported per evaluation cycle, checked by the DO watcher).
7. **Peer visibility**: export a metric for every configured peer (`-1`/large age when never
   handshaked) so idle/lost peers alert; retire or document `10.99.0.20`.
8. **Alert hygiene**: exclude the two known benign UniFi message families (or add per-host dedupe)
   from "Device syslog errors"; investigate the Zen Link-Down flood (~600/h) and add a
   per-host rate alert; update `ALERT_CATALOGUE.yaml` to the 30 live rules (missing
   `falcon-wg-peer-stale`).
9. **Backups**: stop creating two snapshots per day (have the offsite script reuse the job's
   snapshot); document the ~7-day post-deletion recoverability window and RPO/RTO; extend the
   clean-host rehearsal to include R2/Wazuh/IRIS/edge before calling restore "proven".
10. **Runbooks**: update `DISK_PRESSURE.md` (capacities, guard, thresholds, EVE growth),
    `RESTORE.md` (current assets/procedures), `SENSOR_SILENCE.md` (VPN/SPAN are real now; no
    netns), and the `VPN.md` peer table; add a non-root "read-only health view" section and a
    note that `localhost:9200` is the Wazuh indexer.

**P2 — cleanup and polish**

11. Fix or remove the "Network throughput" panel (node-exporter is not in the host netns; use a
    host-netns exporter or drop the panel). Note host NIC counters are otherwise unmonitored.
12. Clean up leftover test indices (`falcon-test`, `falcon-canary`, `falcon-eve-fixture-test`,
    `falcon-retention-test-*`, `other-site-index`) and add ISM/`cleanup` for
    `security-auditlog-*`, `top_queries-*`, `.opendistro-ism-managed-index-history-*`.
13. Mapping hygiene: document/repair the `event_type` text-vs-keyword drift on 09.21/09.22 and
    add a `host` keyword sub-field.
14. Treat the daily Suricata restart explicitly (either reload without restart or add an
    uptime-decrease alert).
15. Rotate any credentials that were printed to operator terminals in the last week (the lab
    keeps `/home/user/.env` with the sudo password and third-party keys in cleartext — consider
    file permissions/ownership review and a split into per-service files).

---

## 8. Evidence snapshots (observed values)

- `falcon_*` textfile at 03:42 UTC: eve age 2 s; DLQ 0; buffer 30 MB; OS yellow/33 unassigned;
  514=8 213/1 h; 15140=62 931/1 h; netflow=45 193/1 h; flows=145 766/1 h; TLS=1/1 h;
  Suricata alerts 9 155/1 h; drops 0; restarts 0; unhealthy 0; backup age <1 h (03:34);
  WG handshake 43 s; disk-guard free 47.8 GB; service probes 9/9 up.
- OpenSearch: cluster yellow, 55 270 756 falcon-* docs, 26.49 GB; repository `_verify` OK;
  `snap-20260930-033005` SUCCESS 15/15; `falcon-r2` 1 snapshot (`snap-cold-2026.09.21`).
- Prometheus: 3/3 targets up; root 82.15 %, data LV 62.6 % used; mem available 41.7 %;
  swap 57.6 % used; load1 1.93.
- Relay log (Sep 22–30): 153 real alerts, 85 TLS-silence; all relay publishes HTTP 200
  (primary + alt). ntfy cache holds the current flap + heartbeat messages.
- Host: no OOM since Sep 28 boot; journal corruption on the Sep 28 unclean boot;
  `ens19` PROMISC, 164.6 M RX, 0 errors.

*(All timestamps UTC. No secrets are included; credential values were read but never printed.)*
