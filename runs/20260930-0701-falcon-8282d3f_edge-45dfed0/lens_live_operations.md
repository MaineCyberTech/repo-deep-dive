# Lens — Live Operations

## Audit Metadata

- Audit name: `repo-deep-dive` · Profile: `falcon-lab` · Lens: `live_operations` (area `LIVE`)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (full-domain)
- Repos: falcon-build `main@8282d3f` (clean at run start) · falcon-edge-build `main@45dfed0` (dirty, in-flight CI work)
- Live host: read-only; run snapshot `live_snapshot.txt` 2026-09-30T07:01:55Z; lens refresh 2026-09-30T15:29–15:35Z
- Generated: 2026-09-30T15:45Z · Auditor: read-only subagent; no restarts, no synthetic alerts, no mutations
- Scope limitations: no root/docker/wg; Grafana admin API, container internals and root-only logs/archives unread; the DO watcher source is not in either repo. Items not directly observed are marked `unverified`.

## Scope

Operator-experience overlay on the running lab: the 3am journey, alert signal quality, degraded-mode behavior, runbook executability as non-root, silent failures (relay-only dead-man gap, offsite unalerted, disk trajectory), and monitoring-of-the-monitoring. Domain findings are cross-referenced, not duplicated. Sources: this run's reports 06/13/14/15/30/32/33/43 plus a fresh read-only host refresh.

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| Run reports `13` (RES), `14` (OBS), `15` (PERF), `30` (NOTIF), `32` (DR), `33` (IR), `43` (FLEET), `06` (SEC) | audit | Operator-relevant facts at this commit |
| `live_snapshot.txt` 07:01:55Z + fresh checks 15:29–15:35Z (timers, `df`, `free`, textfile metrics, relay journal, HTTP probes) | live read-only | What is true on the host now |
| Alert/backup code (`90-alerting.sh`, validation and backup scripts) plus operator docs (`OPERATOR_START_HERE.md`, `docs/phase7/runbooks/*`, `VPN.md`, `ALERT_CATALOGUE.yaml`, edge `edge-alerts.yaml`) | code+docs | Detection/backup mechanics and the operator's actual instructions |
| Prior run `…/20260930-0320-falcon-794ba31_edge-2b5bc8b/` (lens + findings.json) | records | Status of prior LIVE findings |

## Verification Performed

| Evidence | Type | Why relevant | Result / notes |
|---|---|---|---|
| Operator-surface refresh 15:29–15:33Z | live read-only | current truth | Root 83.0% (30.6 GB free), data 62.0% (48.0 GB free); swap 58.2% used; all 8 falcon timers scheduled, last runs ≤12 h. Oneshot services read `inactive` between runs (expected, not a failure). |
| Textfile metrics + `service_probe` | live read-only | dashboard/probe truth | Probe 9/9 services up 15:32Z (incl. relay, both ntfy, do-host); watcher last-run 15:30:01Z; backup epoch 03:34:01Z; guard free 47.95 GB, `reclaims_total 0`. |
| Relay journal 7 d + today; ntfy probes | live read-only | delivery | 155 primary / 149 alt `[200]` in 7 d; last delivery 08:38:22Z (`Disk space low` RESOLVED); ntfy 200/200; relay restarted 04:26:21Z (single delivery hop). |
| `heartbeat.sh` literal read | code | dead-man scope | Publishes to `127.0.0.1:2586` (lab ntfy) directly; it never traverses the relay `:9099` that carries every real alert (cf. 13 RES-P0-002). |
| Config reads (`90-alerting.sh`, `disk_guard.sh`) | code | monitoring-of-the-monitoring + disk journey | No rule consumes textfile mtime, watcher age, swap, `falcon_disk_guard_free_bytes`, or `node_textfile_scrape_error`; `noDataState: OK` (:169); TLS `for: 6h` (:235); root rules 85/92% (:249-255); guard threshold 10 GiB (:14) but text says 5 GiB (:3,:94,:98). |
| Runbook read-only walk as non-root | docs | executability | Root/docker/secrets references: SENSOR_SILENCE 27, DISK_PRESSURE 31, RESTORE 31, VPN 10; e.g. `docker exec … $(sudo cat /srv/falcon/secrets/…)` (SENSOR_SILENCE.md:46,49); stale claims SENSOR_SILENCE:27-28, DISK_PRESSURE:181; no ALERT_PATH_RECOVERY / BLIND_OPERATIONS / notification-loss runbook exists. |
| Prior-run LIVE statuses via 13 Appendix A + 14 prior table | verification | closure discipline | No prior LIVE finding is `verified-fixed`; details in Appendix A. |

## Executive Summary

On a normal day the operator gets readable FIRING/RESOLVED messages on two ntfy instances, deep links, and a mapped runbook; dashboards and the service probe are mostly truthful. The 3am journey fails at the edges: the monitoring stack cannot announce its own death (a relay-only failure is invisible; total-host loss waits up to 26 h; stale monitor data reads as healthy), the backup screen is green-washed by the local snapshot while the offsite tier is unalerted and its recovery evidence uncommitted, disk pressure ends in an untested reclaim whose runbook is stale and root-only, and the person paged cannot execute the incident runbooks without root. Findings: 2 × P0, 3 × P1, 4 × P2.

## Inventory (operator view)

| Surface | What it shows | Truthful today? | Gap |
|---|---|---|---|
| Phone (ntfy ×2) + DO watcher | FIRING/RESOLVED, priority, deep link; off-host liveness | Yes when relay works | Single relay hop; 26 h dead-man; no delivery-loss alert or spool |
| Grafana Central/Feeds | resources, feeds, disk, VPN, backups | Mostly | Throughput panel broken; no eval-health; backup panel shows local snapshot only |
| `service_probe` + textfile metrics | 9 services answering; guard/watcher/backup/peers/edge values | Yes (liveness) | Proves nothing about alert delivery; freshness not alerted |
| Runbooks | detect → contain → recover | Partly | Root/docker-only; stale system model; no blind-ops |

## Degraded-Mode Matrix

| Failure class | Detection | Alert? | Runbook? | Recovery time | Silent gap |
|---|---|---|---|---|---|
| Total host / power loss | DO watcher stale heartbeat (15 min cadence) | Yes, via independent ntfy, up to 26 h late | `NOTIFICATION_SEPARATION_RUNBOOK.md` (watcher out of repo) | onboot=1 + post-reboot verify; 09-28 proved 50/50 | Host produces no signal; 09-28 outage human-detected after ~4.5 h |
| Alert path down: relay-only failure or Grafana eval stall | None: heartbeat bypasses relay; probe tests liveness only; eval stall found manually 09-24 | No | None (`ALERT_PATH_RECOVERY.md` absent) | Manual restart; unbounded to discovery | All alerts to both instances stop silently; dashboards render old data |
| Backup pipeline: offsite and/or new-services incomplete / IRIS dump skip | None for offsite (local metric only); script `exit 1` for new-services (root log only) | No | RESTORE/PATCH stale, no offsite procedure | Manual re-run (~4 h full copy); window undocumented | Cold tier stale indefinitely while local stays green; archive can look successful |
| Data-LV full | Disk guard self-alert <10 GiB only | Only at guard threshold | `DISK_PRESSURE.md` (stale, root-only) | Guard reclaim never exercised; ISM first delete ≈Oct 5 | 15→10 GiB band has no signal; reclaim capacity unverified |
| Capacity exhaustion: root LV / memory / OOM | Grafana >85%/>92%; available <10% rule | Yes/partial (fired 08:03→08:38Z today) | None specific; no OOM runbook | Manual Docker/volume cleanup (root); host hookscript never exercised | Growth unattributed; swap 58% unalerted; host-side memory outside monitoring |
| Feed down/stale (SPAN, NetFlow, syslog, TLS) | Six silence rules (bool-fixed) | Yes | `SENSOR_SILENCE.md` (stale "no VPN/no SPAN") | Buffers drain; silence drill 09-23 | TLS/Wazuh path now pages up to 6 h late; ~⅓ of rules unproven |
| WG tunnel / peer loss | Tunnel stale 10 min; per-peer 24 h | Only for peers that ever handshaked | `VPN.md` (root-only) | Rerun-preservation + syncconf (R-30 fix) | `10.99.0.2`, `10.99.0.20` configured but never exported (2/6) |
| Edge sensor loss / failed update | Only 24 h WG rule for sensor silence | No: zero `falcon_edge_*` rules deployed | Edge runbooks; no joint lab↔edge runbook | Queue + re-image; update swap not crash-safe | Sensor can go dark for hours-days; power cut mid-update leaves agent absent |
| Certificate near expiry | Daily check + expiring rule (drilled 09-23) | Yes | `CERTIFICATE_AND_SECRET_ROTATION.md` | Renewal timers live | Fleet revocation is a DB state; no CRL |

## Findings

### Finding ID: LIVE-P0-001 - The monitoring stack cannot announce its own death: delivery is relay-blind, total loss waits up to 26 h, and stale monitors read healthy

- Severity: P0
- Confidence: High
- Area: LIVE (alert path / dead-man / monitor freshness)
- Evidence:
  - `automation/validation/heartbeat.sh` publishes directly to lab ntfy `127.0.0.1:2586`, bypassing the relay `:9099` that carries every real alert; `NOTIFICATION_SEPARATION_RUNBOOK.md:43-49` documents a 26 h watcher whose source/config is out of repo; `bootstrap/90-alerting.sh` has no rule using `falcon_site_watcher_last_run_timestamp_seconds` (metric fresh 15:30:01Z); relay restarted 04:26:21Z (single hop); Sep 28 — last publish 10:58:26Z, host back 15:30:53Z, no external notice; no "if you stop receiving alerts" or blind-ops procedure exists.
  - Freshness data exists (textfiles 15:29–15:32Z) but no rule in `90-alerting.sh` consumes mtime, watcher age, swap, `falcon_disk_guard_free_bytes`, or `node_textfile_scrape_error`; `noDataState: OK` (:169); exporter has no self last-run; relay publish failures are journal-only (30 NOTIF-P1-002); an alert-eval stall was found manually on 09-24 (13 RES-P1-002).
- What is happening: the only external dead-man checks that the heartbeat publisher ran, not that alerts can be delivered; separately, if a timer/exporter/Grafana evaluation dies, last-known values keep looking healthy and silence rules keep passing.
- Why it matters: the system cannot announce its own death; a security alert during a relay outage is never delivered, and silent monitor death equals silent blindness.
- User / business impact: MTTD hours-to-a-day for total loss (already realized); undetected monitoring loss the rest of the time.
- Security / privacy / reliability impact: alerting reliability and observability assurance.
- Recommended fix: end-to-end relay canary that must arrive on the independent instance each cycle; watcher-age staleness rule; shorten the threshold with the owner; freshness/staleness rules for every timer/exporter plus swap, guard-free-space, scrape-error and relay-failure rules; external eval-plane dead-man; blind-ops checklist.
- Suggested validation: stop relay 15 min → independent canary; stop heartbeat → external alert within the documented threshold; stop each timer → one statement alert; stop Grafana → external path fires.
- Owner suggestion: falcon maintainer + owner · Effort estimate: M · Dependencies: DO access, owner threshold decision
- Status: open (prior LIVE-P1-002/LIVE-P1-007; 13 RES-P0-002/RES-P1-002, 14 OBS-P1-001/P1-003, 30 NOTIF-P1-001/P1-002, 33 IR-P1-001)

### Finding ID: LIVE-P0-002 - The backup the operator sees green can hide a stale offsite tier and uncommitted recovery evidence

- Severity: P0
- Confidence: High
- Area: LIVE (backup / recovery)
- Evidence:
  - `automation/validation/export_monitor_metrics.sh:80-84` exports only the local snapshot epoch; `bootstrap/85-backup-job.sh:35-46` writes freshness before offsite and logs offsite failures only; `bootstrap/90-alerting.sh:222-224` (`falcon-backup-stale`, local only); live backup epoch 03:34:01Z with no offsite metric; the 09-30 silent offsite failure needed a manual 03:55→07:43Z re-run.
  - `evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out` is 0 bytes in HEAD while `.meta.json` is untracked; `backup_new_services.sh:38-45` silently skips the IRIS dump; last real capture 4× `[MISSING]`; root log unread (`unverified`).
- What is happening: the operator's backup gauge proves the local snapshot only; the cold tier can be stale or unverified with no screen or alert, and the proof of the 09-30 recovery is outside the published package.
- Why it matters: offsite is the last defence against host loss; the failure that already happened once is still invisible and its evidence unbound.
- User / business impact: host loss during a silent offsite outage loses the delta; reviewers cannot see recovery proof.
- Security / privacy / reliability impact: unrecoverable cold-tier loss; overstated recoverability.
- Recommended fix: offsite + new-services last-success gauges with 36 h staleness rules; commit/rebind the recovery capture; retained-union remote retention; fail on a missing IRIS dump; record key-custody attestation.
- Suggested validation: break the Spaces probe → one alert per path; package verification passes with the 1708-byte artifact; scratch restore after retention.
- Owner suggestion: falcon maintainer (+ owner for custody) · Effort estimate: S–M · Dependencies: publication flow, offsite access
- Status: partially-fixed (prior LIVE-P0-001/002; 13 RES-P0-001, 32 DR-P1-001/002/004, 14 OBS-P1-002)

### Finding ID: LIVE-P1-001 - Disk pressure leaves the operator a late signal, a mislabelled alert and an untested action

- Severity: P1
- Confidence: High
- Area: LIVE (capacity / operator journey)
- Evidence:
  - Live 15:32Z: root 144.4/183.3 GB (83%, 30.6 GB free); data 76.8/130.7 GB (62%, 48.0 GB free); swap 58.2%; `Disk space low` fired 08:03→08:38Z on both paths and self-resolved; `disk_guard.sh:14` threshold 10 GiB but header/alert text says 5 GiB (`:3,:94,:98`); `falcon_disk_guard_reclaims_total 0`; no warning band between healthy and guard action; ISM first EVE delete expected ≈Oct 5 (`unverified`); `DISK_PRESSURE.md:181` says "no offsite copy; local only".
- What is happening: root has a warning with no reclaim path and no attribution; data's first signal is an acting guard that has never run, with a message that misstates its own threshold.
- Why it matters: at measured slopes the root warning recurs in 1–3 days and failure 8–13 days (15 PERF); a guard that cannot free enough wedges OpenSearch/probe writers.
- User / business impact: platform outage and manual root cleanup; data at risk on the data LV.
- Security / privacy / reliability impact: availability and retention safety.
- Recommended fix: reclaim plan (Docker prune, move Wazuh/IRIS volumes) + ≥90% critical page; <15–20 GiB data warning with projection; sanctioned guard reclaim drill; fix 5→10 GiB text; refresh the capacity runbook.
- Suggested validation: controlled fill pages before 90%; guard drill frees space and pages; 7-day free-space stable.
- Owner suggestion: falcon maintainer · Effort estimate: M · Dependencies: maintenance window, retention decision
- Status: partially-fixed (prior LIVE-P0-003/LIVE-P1-001; 15 PERF-P1-001/002, 13 RES-P1-005, 12 INFRA-P3-002)

### Finding ID: LIVE-P1-002 - The paged operator cannot execute the incident runbooks as written, and they describe a lab that no longer exists

- Severity: P1
- Confidence: High
- Area: LIVE (runbooks / operator readiness)
- Evidence:
  - Read-only walk 15:35Z (non-root): root/docker/secrets references — SENSOR_SILENCE 27, DISK_PRESSURE 31, RESTORE 31, VPN 10; e.g. `docker exec -e PW="$(sudo cat /srv/falcon/secrets/opensearch_admin.pw)" …` (SENSOR_SILENCE.md:46,49), `docker system df` (DISK_PRESSURE.md:56); `OPERATOR_START_HERE.md` quick checks are labelled "(lab host, root)" and `central_health.sh` shells into containers; no non-root health view exists.
  - Stale model: SENSOR_SILENCE.md:27-28 ("no VPN … no physical SPAN"), DISK_PRESSURE.md:181 ("no offsite"); no BLIND_OPERATIONS/ALERT_PATH_RECOVERY runbook; escalation matrix is a placeholder (TABLETOP_SCENARIO.md:67-74).
- What is happening: the first-15-minutes path assumes root and a topology that no longer exists; when screens are gone there is no blind-ops procedure.
- Why it matters: incident response starts with escalation to root or guesswork exactly when speed matters.
- User / business impact: slower, wrong response; prolonged outages.
- Security / privacy / reliability impact: containment quality depends on stale documents.
- Recommended fix: role-annotated runbooks plus a non-root read-only health view; blind-ops checklist; fill escalation contacts; append-only reconciliation of stale claims.
- Suggested validation: walk every runbook read-only as non-root — each step works or states its role; CI lint for stale phrases.
- Owner suggestion: falcon maintainer + owner (contacts) · Effort estimate: M · Dependencies: none
- Status: still-open (prior LIVE-P1-006; 13 RES-P2-003, 12 INFRA-P1-001, 16 DOC-P2-001, 33 IR-P1-001/002)

### Finding ID: LIVE-P1-003 - The edge fleet is visible but not alertable; a lost sensor or failed update pages nobody

- Severity: P1
- Confidence: High
- Area: LIVE (edge fleet operations)
- Evidence:
  - Live `falcon_edge_metrics.prom` 15:29Z: 9 sensors (1 ACTIVE, 5 RETIRED, 3 REVOKED); zero rules consume `falcon_edge_*`; `deploy_edge_alert_rules.sh` is dry-run, D-007 pending; the prepared `EdgeSensorRevoked` rule would fire immediately on residue; FLEET-P1-002 explicit outcome: power loss between rename and move during an update leaves `falcon_agent` absent with no boot restore; `queue.py:126-140` purge bug; edge PKI/DB backup is host-local.
- What is happening: the production sensor path produces metrics and dashboards but no alarms; sensor/queue/PKI failures wait on a human noticing a dashboard.
- Why it matters: the monitored edge is the fleet's eyes; silence there is also a monitoring blind spot.
- User / business impact: hours-days of unrecognized sensor loss; field intervention; fleet trust reset on host loss.
- Security / privacy / reliability impact: edge security posture and recoverability.
- Recommended fix: deploy scoped rules excluding RETIRED/REVOKED residue; crash-safe update swap + boot recovery; fix the queue cutoff; offsite edge secrets archive; joint edge incident runbook.
- Suggested validation: simulated ACTIVE-sensor silence fires and no residue fires; kill apply in QEMU → boot recovers; restore edge PKI on scratch.
- Owner suggestion: edge maintainer + owner · Effort estimate: M · Dependencies: D-007, P7-G05 decision
- Status: still-open (prior INTG-P1-001/LIVE-P1-003; 14 OBS-P1-004, 13 RES-P1-003, 43 FLEET-P1-002, 07 DATA-P1-003)

### P2 findings (index)

| ID | Sev | Finding (operator view) | Evidence | Status |
|---|---|---|---|---|
| LIVE-P2-001 | P2 | Only ~⅔ of rules have firing proof; one raw drill artifact says the disk rules never fired while the summary claims they did — the operator cannot know which alarms to trust | 14 OBS-P2-003; `P5-G08/…disk-pressure-drill.out` vs `PERFORMANCE_ENVELOPE.md`; 09 TEST-P2-005 | open |
| LIVE-P2-002 | P2 | Reboots keep producing new 3am failures; fixes are installed but not re-exercised (OOM hookscript never fired, auto-start not re-tested); R-29 postmortem still open; escalation contacts a placeholder | 33 IR-P2-002/005; `decision_log.md:79,108,136`; `risk_register.md:38` | partially-fixed |
| LIVE-P2-003 | P2 | The dominant noise source is curbed but the trade-off is undocumented: a genuinely dead Wazuh/TLS path now pages up to 6 h late; benign UniFi families unfiltered; 7-day re-measure pending | 14 OBS-P2-001; 30 NOTIF-P2-002; `90-alerting.sh:235` `for: 6h` | partially-fixed |
| LIVE-P2-004 | P2 | Operator screens can silently lie: throughput panel broken (container netns), mapping drift empties `.keyword` aggregations, `OPERATOR_START_HERE` says restarts read 0 while daily rotation resets uptime invisibly | 14 OBS-012/OBS-P2-002; 15 PERF-P2-004; 14 prior LIVE-P2-001 | still-open |

## Cross-References (LIVE ↔ domain)

| This report ID | Related domain ID(s) | Relationship |
|---|---|---|
| LIVE-P0-001 | RES-P0-002 · RES-P1-002 · OBS-P1-001 · OBS-P1-003 · NOTIF-P1-001/002 · IR-P1-001 | Operator view: the monitoring stack's own death |
| LIVE-P0-002 | RES-P0-001 · DR-P1-001/002/004 · OBS-P1-002 · DATA-P1-002 | Operator view: backup truth and evidence binding |
| LIVE-P1-001 | PERF-P1-001/002 · RES-P1-005 · INFRA-P3-002 | Capacity journey from signal to action |
| LIVE-P1-002 | RES-P2-003 · INFRA-P1-001 · DOC-P2-001 · IR-P1-001/002/003 | Runbook executability and stale system model |
| LIVE-P1-003 | OBS-P1-004 · RES-P1-003 · FLEET-P1-002 · DATA-P1-003 | Edge-fleet visibility and silent sensor loss |
| LIVE-P2-001/002/003/004 | OBS-P2-001/003 · IR-P2-002/003/005 · PERF-P2-004 · OBS-012 · OBS-P2-002 · RES-P2-001 | Detection trust, recurrence, signal quality, lying screens |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Alert-path death is invisible | P0 | Low–Medium | Missed security/ops pages | LIVE-P0-001 | Relay canary + watcher alert + freshness rules |
| Silent offsite staleness | P0 | Medium | Data-protection loss | LIVE-P0-002 | Offsite gauges + rules |
| Root/data LV exhaustion | P1 | Medium | Platform outage | LIVE-P1-001 | Reclaim + warning band |
| Wrong/slow incident response | P1 | Medium | Prolonged outage | LIVE-P1-002 | Non-root runbooks + blind-ops |
| Sensor loss unnoticed | P1 | Medium | Fleet blindness | LIVE-P1-003 | Edge rules + crash-safe update |

## Recommendations

### Immediate / Release Blocking
- Relay end-to-end canary verified on the independent instance; watcher-age and freshness rules (LIVE-P0-001).
- Offsite + new-services freshness gauges with 36 h rules; commit/rebind the recovery evidence (LIVE-P0-002).

### This Week
- Non-root read-only health view; blind-ops first-15-min page; fill escalation contacts (LIVE-P1-002).
- Root reclaim plan + ≥90% page; <15–20 GiB data warning; fix guard text (LIVE-P1-001).

### This Month
- Deploy scoped edge rules (D-007); crash-safe update apply; queue purge fix; offsite edge PKI (LIVE-P1-003).
- Firing-proof drills per unproven rule; 7-day noise re-measure; repair the throughput panel and mapping contract (LIVE-P2-001/003/004).
- Controlled VM restart to exercise auto-start + OOM hookscript; close R-29 (LIVE-P2-002).

### Later / Platform Evolution
- Quarterly chaos/tabletop cadence incl. monitoring-loss scenario; quarterly total-loss walkthrough; external evaluation-plane mutual check.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Watcher-age/mtime staleness rules + offsite epoch metric | Dead monitors and a stale cold tier become visible | `90-alerting.sh`, `export_monitor_metrics.sh`, `80-offsite-backup.sh` | stop timer / break probe → fires |
| Non-root health section | 3am journey works without root | `OPERATOR_START_HERE.md` | read-only walk |

## Hardening Backlog

| Item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Alert-path canary, freshness rules, runbook rewrite + blind-ops page; guard text fix | P1 | falcon maintainer + owner | M | DO access |
| Edge rules deployment + crash-safe apply | P1 | edge maintainer | M | D-007/P7-G05 |
| Firing-proof drill program | P2 | owner + maintainer | M | quiet windows |

## Suggested Tests

- Integration: stop relay 15 min → independent canary; stop heartbeat → dead-man alert ≤ documented threshold; break Spaces probe → offsite alert; stop metrics/probe timers → staleness alerts fire.
- E2E: controlled fill to 90% root and <20 GiB data → warning before action; sanctioned guard reclaim drill.
- Manual: full read-only runbook walk as the non-root audit account; blind-ops walkthrough with dashboards blocked.

## Suggested Documentation Updates

- New `docs/runbooks/{ALERT_PATH_RECOVERY,BLIND_OPERATIONS,NOTIFICATION_AND_DEADMAN}.md`.
- `OPERATOR_START_HERE.md`: non-root health section; correct buffer/rotation claims; "if you stop receiving alerts" checklist.
- `SENSOR_SILENCE.md` / `DISK_PRESSURE.md` / `RESTORE.md` / `VPN.md` / `TABLETOP_SCENARIO.md`: append-only reconciliation, current topology/roles, completed escalation matrix, monitoring-loss scenario.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Owner-accepted total-loss detection target, and does Grafana notify on `execErrState: Error`? | Sets the watcher threshold; blind-failure path | Owner decision record; config or sanctioned test |
| Who owns the remaining operational decisions: root-LV reclaim, offsite evidence binding, and an out-of-band channel if home power/internet is lost? | Sustaining the fixes and escalation reality | Owner/maintainer decision |

## Appendix A — Prior-run LIVE findings status at this commit

| Prior ID | Status at this commit | Current report ref |
|---|---|---|
| LIVE-P0-001/002 offsite + new-services | partially-fixed (cause fixed; detectors open; evidence uncommitted; new-services unverified) | RES-P0-001 / RES-P1-004 · DR-P1-001/002 · LIVE-P0-002 |
| LIVE-P0-003 data-LV growth | partially-fixed (rotation + 10 GiB guard; no warning band) | PERF-P1-002 / RES-P1-005 / LIVE-P1-001 |
| LIVE-P0-004 TLS flap | partially-fixed (6 h window since 04:12Z; 7-day re-measure pending) | OBS-P2-001 / NOTIF-P2-002 / LIVE-P2-003 |
| LIVE-P1-001 root LV | still-open (83.0% at 15:32Z) | PERF-P1-001 / LIVE-P1-001 |
| LIVE-P1-002 monitor gaps | partially-fixed (metrics exist; rules absent) | OBS-P1-003 / RES-P1-002 / LIVE-P0-001 |
| LIVE-P1-003 never-handshake peers | still-open (6 configured / 4 exported) | OBS-P1-005 / RES-P1-006 |
| LIVE-P1-004 alert hygiene | partially-fixed (catalogue 31=31; benign filters absent) | OBS-P2-001 / LIVE-P2-003 |
| LIVE-P1-005/006/007 backup structure / runbooks / total-loss notice | still-open | DR-P1-003 · RES-P2-003 · RES-P1-001 / OBS-P1-001 / NOTIF-P1-001 · LIVE-P0-001/P1-002 |
| LIVE-P2-001…005 panel, index hygiene, mapping drift, Suricata restart, secrets | still-open (P2-002 index hygiene not re-verified this wave; needs 07/31/44) | OBS-012 · DATA-P2-005/P3-007 · PERF-P2-004 · OBS-P2-002 · SEC-P2-002 |

## Appendix B — Method and redaction

- All live checks were read-only (systemd status/timers, `df`, `free`, textfile metrics, journal counts, HTTP GET). No service was restarted, no synthetic alert fired, no file on a live system was modified.
- Secret-like values were not printed; `.env`, `/srv/falcon/secrets` and archive references are path/type only. Not directly observed: watcher implementation/threshold internals, Grafana evaluation health, root-only backup logs, phone-side receipts (`unverified`).

**Overall live-operations score: 3/5** — a working, mostly truthful operator experience with readable alerts and mapped runbooks, held back by silent death of the alert/backup paths themselves, an untested disk action, root-only stale runbooks, and unalerted monitor freshness.
