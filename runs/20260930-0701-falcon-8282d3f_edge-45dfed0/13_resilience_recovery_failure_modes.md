# Resilience, Recovery, and Failure Modes Audit

## Audit Metadata

- Audit name: `repo-deep-dive` · Profile: `falcon-lab` · Area: RES
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repos: falcon-build `main@8282d3f` · falcon-edge-build `main@f1c5def` (run label names edge `45dfed0`; HEAD moved 6 commits — all edge claims checked at `f1c5def`)
- Generated: 2026-09-30T14:20Z (live checks 14:15–14:20Z) · Auditor: read-only wave-1 subagent (prompt 13)
- Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/13_resilience_recovery_failure_modes.md`
- Scope limits: no root/sudo (root-only logs/archives = `unverified`); no Grafana/Prometheus API; no restarts/drills; falcon tree has an in-flight uncommitted offsite-backup capture

## Scope

Reviewed read-only: power loss, disk full, tunnel loss, feed loss, service loss; detectors and detector placement; external dead-man; backups/offsite; recovery procedures written vs exercised; edge offline queue/control-plane; graceful shutdown; prior LIVE-P0-001/002/003, LIVE-P1-001…007 and INTG F1–F10. Not reviewed: container-internal state, DO watcher implementation (not in either repo), root-only files, live alert-evaluation state, destructive drills.

## Evidence Reviewed

- Scripts/units: `bootstrap/{80-offsite-backup,85-backup-job,90-alerting,95-wireguard,96-disk-guard}.sh`, `automation/validation/{disk_guard,heartbeat,export_monitor_metrics,service_probe,backup_new_services,post_reboot_verify,central_recovery_test,wg_peer_preservation_check}.sh`, `config/systemd/falcon-*`, `config/wireguard/wg0.conf.tpl`, `compose/{central,probe}/docker-compose.yml`.
- Docs: `docs/phase7/runbooks/*` (INCIDENT_RESPONSE, SENSOR_SILENCE, DISK_PRESSURE, RESTORE, UPGRADE_ROLLBACK), `docs/phase9/NOTIFICATION_SEPARATION_RUNBOOK.md`, `CLEAN_HOST_REBUILD_RUNBOOK.md`, `docs/edge/EDGE_RELEASE_PIN.md`.
- Ledgers: `decision_log.md`, `risk_register.md`, `phase9_gate_ledger.csv`, `test_execution.csv`, `exception_register.md`.
- Edge: `src/falcon_agent/queue.py`, `src/falcon_control/store.py`, `automation/observability/fleet_metrics.py`, `automation/validation/deploy_edge_alert_rules.sh`, `docs/phase8/CLOSEOUT.md`.
- Live: `live_snapshot.txt` (07:01Z) + fresh checks 14:15–14:20Z (`df`, `free`, `systemctl list-timers 'falcon*'`, `/srv/falcon/textfile/*.prom`, `/etc/systemd/system/docker.service.d/10-require-falcon-mount.conf`, host-only units).
- Prior run: `/home/user/repo-deep-dive/runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Prior findings at current commits | verification | fixed/still-open | Appendix A; nothing closed on assertion |
| `85-backup-job.sh:35-46` vs `90-alerting.sh:222-224` | code | offsite detector | freshness written before offsite; only local-snapshot rule — supported |
| Working-tree `evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out` | observation | offsite fix | ran 03:55→07:43Z, 1723 files, hash-verified; HEAD copy 0-byte (uncommitted) |
| `heartbeat.sh:2-11` + `NOTIFICATION_SEPARATION_RUNBOOK.md:43-49` | code+doc | dead-man scope | heartbeat→lab ntfy directly, bypasses relay 9099; DO threshold 26 h |
| Live textfiles (`wg_peer_handshake_age_seconds`, `disk_guard_reclaims_total 0`, `site_watcher_last_run…`) | observation | detector coverage | 6 peers configured/4 exported; guard never reclaimed; watcher unalerted |
| `tar --absolute-names` list+grep in `/tmp/opencode` | reproduction | backup verification | script's absolute-path grep matches on GNU tar 1.35; earlier all-`[MISSING]` not reproducible; live logs root-only |
| `test_execution.csv` drill rows | ledger | exercise dates | restore 09-23; silence drill 09-23; power 09-28; central down/up 09-21; no disk/storm drill runs |
| Live `df`/`free` 14:20Z | observation | capacity | root 83% (29 GB free), data 62% (45 GB free), swap 4.8/8 GiB |

## Executive Summary

Better than the prior run, but the lab still cannot reliably detect the loss of its own alerting or backup paths. Two real fixes landed today: the `.env` quoting bug that broke every `set -e` backup/offsite run, and WireGuard peer preservation across bootstrap reruns (R-30 class, dry-run PASS). Offsite completed successfully at 07:43Z and the data LV stabilised (~45–47 GB free) with EVE/stats rotation live. Residual risk is detector placement: no offsite signal; the dead-man tests the lab-ntfy publish path, not the relay every real alert uses; total-host loss has ~26 h worst-case latency (the 2026-09-28 outage produced no external notice); textfile metrics can freeze unalerted; the edge path has no deployed rule. Recovery is mostly written; the strongest paths are proven (P9-G06 restore, P9-G09 clean-host, 09-28 post-reboot 50/50), but guard reclaiming has never fired and the new-services check is unproven. Findings: 2 × P0, 6 × P1, 3 × P2, 1 × P3.

## Failure Mode Inventory

| Failure mode | Detector today | Detector in failed domain? | External dead-man? | Status |
|---|---|---|---|---|
| Total host/power loss | DO watcher stale-heartbeat >26 h | No (watcher on DO) | Yes, slow, relay-blind | RES-P1-001/P0-002 |
| Data-LV full | guard self-alert <10 GiB; no metric rule | Yes | No | RES-P1-005 |
| Root-LV full | Grafana >85% / >92% | Yes | No | RES-P1-005 |
| WG tunnel loss (seen peer) | `falcon-vpn-tunnel-stale` 10 m; per-peer 24 h | Yes | No | RES-P1-006 |
| WG peer never handshakes | none (metric omits) | n/a | No | RES-P1-006 |
| Feed loss | 6 silence rules (bool fixed) | Yes | No | prior LIVE-P0-004 partially-fixed |
| Service/relay loss | service probe; alert routes via relay | Yes | Blind | RES-P0-002 |
| Grafana alert-eval loss | none (stall found manually 09-24) | Yes | No | RES-P1-002 |
| Offsite backup failure | none (local rule only) | Yes | No | RES-P0-001 |
| New-services backup incomplete | script exits 1; correctness unproven | Yes | No | RES-P1-004 |
| Edge sensor/control-plane loss | only 24 h WG rule; edge rules undeployed | Partly | No | RES-P1-003 |
| Edge queue/directive accounting | edge metrics exist; purge bug latent | Edge+lab | No | RES-P2-002 |
| Edge PKI/host loss | local-only daily backup | n/a | No | RES-P1-003 |
| Reboot/boot-order faults | post_reboot_verify (root) | host | No | RES-P2-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Action |
|---|---:|---|---|---|
| Timeouts | 3 | curl timeouts in probes/guard/relay | no job/ingest timeouts | per-job timeout+metric |
| Retries/backoff | 2 | relay retry ×2 then drop | no persistent retry spool | bounded backoff spool |
| Idempotency | 3 | edge keys; `ingest/vector` none (D-006) | replay semantics undocumented | document dedupe |
| Circuit breakers | 1 | none found | dependency cascades | breaker in exporter/relay |
| Queue DLQ | 3 | vector DLQ live; edge queue+DLQ | purge bug; no edge DLQ alert | RES-P2-002 |
| Webhook recovery | 2 | relay + resolve enabled | no replay path | cold-path replay test |
| Worker recovery | 3 | `restart: unless-stopped`; timers | restart visibility gaps | counters per worker |
| Graceful shutdown | 2 | buffers; compose stop | no ordered shutdown doc/test | document + test |
| DB/Redis/API/email/file/realtime | 3 | OpenSearch/target rules | Redis/ntfy cascade untested | dependency drill |
| Offline client | 3 | edge 2 GiB buffer; 90 s drill OK | no lab-side edge alarm | RES-P1-003 |
| Transactions | 2 | snapshot/restore atomicity proven | no transactional ingest | document replay |
| Partial writes | 2 | snapshot-before-delete practice | ISM delete never exercised | fault injection |

## Detailed Review

- **Total loss/power**: docker depends on `/srv/falcon` via a **host-only** drop-in (`10-require-falcon-mount.conf`); 09-28 real outage → 50/50 post-reboot; no real-time notice (RES-P1-001/002).
- **Disk full**: guard 10 GiB self-alert (`disk_guard.sh:12,24-42`); root only >85/92% (`90-alerting.sh:249-255`); guard `reclaims_total 0`; no swap/early-warning (RES-P1-005).
- **Tunnel**: rerun preservation (`95-wireguard.sh:42-66`) + syncconf; per-peer 24 h rule; never-handshaked peers invisible (RES-P1-006).
- **Feed**: six silence rules, V-5 `bool` fix, TLS window 6 h (09-30); no post-change volume proof; adversary-silence untested.
- **Service/alert path**: probe of 9 services; relay is the single delivery hop; heartbeat bypasses it (RES-P0-002).
- **Backups**: daily local snapshot + offsite Spaces + encrypted config; restore 7 s/720 k docs (P9-G06) and clean-host 4.79 M docs (P9-G09) on 09-23; no offsite detector; duplicate snapshots (RES-P0-001, RES-P1-004).
- **Edge recovery**: bounded queue/DLQ + renewal drills; alerts undeployed; PKI local-only; purge bug latent (RES-P1-003, RES-P2-002).
- **Runbooks**: incident-critical docs stale (no-VPN/no-SPAN/no-offsite), dead-man described as owner-gated while P9-G07 PASS (RES-P2-003).

## Scenario / Control Matrix

| ID | Scenario/control | Evidence | Control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| RES-001 | Timeouts | scripts | bounded HTTP | no job timeouts | P2 | add per-job timeout |
| RES-002 | Retries/backoff | relay | ×2 bounded | drops on failure | P2 | spool+backoff |
| RES-003 | Idempotency | D-006 | partial | undocumented replay | P3 | document |
| RES-004 | Circuit breakers | none | none | cascades | P2 | breaker |
| RES-005 | Queue DLQ | vector/edge | live | purge bug, no edge alert | P2 | RES-P2-002 |
| RES-006 | Webhook recovery | relay | delivered | no replay | P2 | replay test |
| RES-007 | Worker recovery | compose/timers | good | visibility gaps | P2 | restart counters |
| RES-008 | Graceful shutdown | buffers | partial | no ordered stop | P2 | document+test |
| RES-009 | DB/Redis/API/email/file/realtime | OpenSearch rules | partial | cascades untested | P2 | dependency drill |
| RES-010 | Offline client | edge queue | strong | no lab alarm | P1 | RES-P1-003 |
| RES-011 | Transactions | restores | proven restore | no transactional ingest | P3 | document |
| RES-012 | Partial writes | ISM design | snapshot-first | delete untested | P2 | fault injection |

## Findings

### Finding ID: RES-P0-001 - Offsite backup failures remain invisible to alerting

- Severity: P0 · Confidence: High · Area: RES (backup)
- Evidence: `bootstrap/85-backup-job.sh:35-46` (freshness written after local snapshot; offsite failure only logged); `bootstrap/90-alerting.sh:222-224` (`falcon-backup-stale` reads `falcon_backup_last_success_timestamp_seconds`, local only); `bootstrap/80-offsite-backup.sh`; working-tree capture `evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out` (HEAD 0-byte).
- What is happening: the `.env` bug was fixed and offsite succeeded 2026-09-30, but no signal exists if it fails again.
- Why it matters: offsite is the last line of defence against host loss.
- Impact: silent data-protection loss; overstated recoverability.
- Fix / validation: emit offsite + new-services last-success metrics and add an offsite-stale rule; force a failure and confirm one alert per ntfy path.
- Owner/effort/deps: falcon maintainer · S · none.
- Status: partially-fixed (prior LIVE-P0-001; cause fixed, detector open).

### Finding ID: RES-P0-002 - A relay-only alert-path failure is invisible to the dead-man

- Severity: P0 · Confidence: High · Area: RES (alerting)
- Evidence: `automation/validation/heartbeat.sh:6-11` (posts to lab ntfy `127.0.0.1:2586`, not relay `:9099`); `falcon-alert-relay.service` is the only route to both ntfy targets; `service_probe.sh:31-39` + `90-alerting.sh:309-311` would alert through the failed relay; watcher watches heartbeat age only (`NOTIFICATION_SEPARATION_RUNBOOK.md:43-49`).
- What is happening: relay dies → all alerts stop in both domains while heartbeats stay fresh.
- Why it matters: the monitoring system can lose its voice undetected.
- Impact: undetected alerting outage; security alerts never delivered.
- Fix / validation: canary alert that must arrive on the independent instance each cycle + relay/freshness rule; stop the relay 15 min and observe the canary.
- Owner/effort/deps: falcon maintainer/owner · M · DO watcher access.
- Status: open (new).

### Finding ID: RES-P1-001 - Total-host loss has up to ~26 h detection; the 09-28 outage produced no notification

- Severity: P1 · Confidence: High · Area: RES (dead-man)
- Evidence: daily `falcon-heartbeat.timer` + 26 h watcher threshold (`NOTIFICATION_SEPARATION_RUNBOOK.md:43-49`); `decision_log.md:98` (10-min outage below threshold — "correct"); `:136` (2026-09-28 host down 10:59Z, alerts only after 15:30Z recovery).
- What is happening: the watcher exists and was expiry-tested (P9-G07), but it is slow and its 30-min unreachable clause lacks evidence.
- Why it matters: a monitoring system must announce its own death.
- Impact: hours of blind operation per host loss — already proven.
- Fix / validation: hourly heartbeat + ≤60–90 min threshold; capture the watcher config in-repo; stop the heartbeat and measure alert latency.
- Owner/effort/deps: owner+falcon maintainer · M · DO access.
- Status: still-open (prior LIVE-P1-007).

### Finding ID: RES-P1-002 - Monitor freshness is not monitored; stale textfile metrics read as healthy

- Severity: P1 · Confidence: High · Area: RES (observability)
- Evidence: no `falcon_metrics_last_run` in `export_monitor_metrics.sh`; no rule on `falcon_site_watcher_last_run_timestamp_seconds`, `falcon_disk_guard_*`, or `node_textfile_scrape_error` in `90-alerting.sh`; alert-eval stall discovered manually (`test_execution.csv` T-REVIEW-FIX-426, 2026-09-24); live swap 4.8/8 GiB with no swap rule.
- What is happening: if a metrics/probe/guard/watcher timer stops, values freeze and silence rules keep evaluating OK (`noDataState: OK`).
- Why it matters: silent monitor death equals silent blindness.
- Impact: false confidence during incidents.
- Fix / validation: last-run/mtime metrics + staleness rules for every timer/guard/watcher; scrape-error and swap rules; kill each timer and expect one alert.
- Owner/effort/deps: falcon maintainer · M · none.
- Status: still-open (prior LIVE-P1-002).

### Finding ID: RES-P1-003 - Edge path: no deployed alert and local-only PKI/DB backup

- Severity: P1 · Confidence: High · Area: RES (edge)
- Evidence: edge `docs/phase8/CLOSEOUT.md` ("alert rules + dashboard remain prepared but not deployed"); `deploy_edge_alert_rules.sh` dry-run; live falcon 31 rules include none for `falcon_edge_*`; only `falcon-wg-peer-stale` (24 h, `90-alerting.sh:297-299`); `80-offsite-backup.sh:115-137` and `backup_new_services.sh:18-36` exclude `/home/user/falcon-edge-secrets` (CA, signing seed, DB).
- What is happening: sensor silence/queue/cert have prepared rules but no live alert; host loss destroys the fleet trust anchor.
- Why it matters: the edge is a production path with a 24 h worst-case detector and no offsite key custody.
- Impact: fleet outage/data loss may go unannounced; unrecoverable PKI.
- Fix / validation: fold scoped edge rules into the catalogue (owner decision) or deploy `edge-alerts.yaml`; extend offsite with the encrypted edge archive; drill edge loss + restore.
- Owner/effort/deps: owner+edge maintainer · M · Prometheus change approval, ED-06.
- Status: still-open (prior INTG-P1-001/P1-003, F3/F4/F5/F10).

### Finding ID: RES-P1-004 - Backup quality: new-services verification unproven, duplicate snapshots, undocumented window

- Severity: P1 · Confidence: Medium · Area: RES (backup)
- Evidence: `backup_new_services.sh:43-52` (check + `exit 1` added `d0f4aaf`); `decision_log.md:144` lists "the new-services backup verification" as queued; offsite uploads 3 archives (07:37Z) but `/srv/falcon/backups/new-services.log` root-only; `85-backup-job.sh:18-25` + `80-offsite-backup.sh:59-69` create two snapshots/day; `:139-150` keep 7 inventories with no documented post-deletion window in `RESTORE.md`.
- What is happening: archives exist and are offsite, but no current-commit evidence proves the critical-item check passes; scratch reproduction shows the absolute-name grep works.
- Why it matters: the unrecoverable state (WG keys, Wazuh registry, IRIS, enrolment) must be proven present.
- Impact: recovery may miss critical items with a green-looking job.
- Fix / validation: commit one passing captured run (redacted); reuse one snapshot for offsite; document RPO/RTO + window; validate against a scratch restore.
- Owner/effort/deps: falcon maintainer · S/M · root capture.
- Status: partially-fixed / unverified (prior LIVE-P0-002, LIVE-P1-005).

### Finding ID: RES-P1-005 - Capacity: root LV unguarded; data-LV early warning missing; guard reclaim never exercised

- Severity: P1 · Confidence: High · Area: RES (capacity)
- Evidence: live `df` 14:20Z (root 135/171 GB, 83%, 29 GB free; data 62%, 45 GB free; 82% at 07:01Z); `90-alerting.sh:249-255` root-only rules; `disk_guard.sh:12` 10 GiB + live `reclaims_total 0`; no rule on `falcon_disk_guard_free_bytes`; prior 75 GB one-night root jump (LIVE-P1-001).
- What is happening: first data signal is the guard at 10 GiB; root grows unattributed; the deletion path has never fired live.
- Why it matters: root exhaustion breaks Docker/metrics; data-LV exhaustion wedges writers.
- Impact: platform outage; index loss; manual recovery.
- Fix / validation: 20 GiB warning + projection alert, swap alert, root growth attribution/cleanup; sanctioned guard reclaim drill with metrics.
- Owner/effort/deps: falcon maintainer · M · owner-sanctioned drill.
- Status: partially-fixed (prior LIVE-P0-003/LIVE-P1-001).

### Finding ID: RES-P1-006 - Peers that never handshake are invisible (6 configured, 4 exported)

- Severity: P1 · Confidence: High · Area: RES (VPN)
- Evidence: `export_monitor_metrics.sh:146-161` ("only peers that connected at least once"); live `falcon_wg_peers_total 6` vs 4 per-peer series (`.10/.21/.22/.30`); `.20` (samsung) absent since the prior run.
- What is happening: a lost/re-imaged device that never connected cannot alert.
- Why it matters: fleet blind spot for client endpoints.
- Impact: silent connectivity gaps; lost devices look healthy by absence.
- Fix / validation: export every configured peer with a sentinel age; retire/document `.20`; add a never-connected peer and expect an alert.
- Owner/effort/deps: falcon maintainer · S · none.
- Status: still-open (prior LIVE-P1-003).

### Finding ID: RES-P2-001 - Reboot/boot-order failures recurred; resilience controls are host-only

- Severity: P2 · Confidence: High · Area: RES (recovery)
- Evidence: `decision_log.md:79` (09-22 cloudflared stale paths), `:108` (09-24 veth-span-b 712-restart Suricata loop invisible for hours), `:136` (09-28 Wazuh proxy sockets failed again at boot); host-only `/etc/systemd/system/docker.service.d/10-require-falcon-mount.conf` has no repo writer; `falcon-edge-*` units host-only; `CLEAN_HOST_REBUILD_RUNBOOK.md` omits the mount guard.
- What is happening: each reboot exposed a different latent issue; host fixes are only partly encoded.
- Why it matters: clean rebuilds and future reboots can reintroduce failures.
- Impact: hours of degraded monitoring per boot event.
- Fix / validation: encode units/drop-ins in repo; add ordered-dependency boot check; clean-host rebuild passes without manual steps.
- Owner/effort/deps: falcon maintainer · M · clean-host rehearsal.
- Status: partially-fixed.

### Finding ID: RES-P2-002 - Edge queue: latent delete-all purge and directives that never decrement

- Severity: P2 · Confidence: High · Area: RES (worker recovery)
- Evidence: `src/falcon_agent/queue.py:126-140` (selects by age cutoff, then `DELETE … enqueued_at < iso_now()` — deletes all when called); sole caller is `tests/phase3/test_queue.py:80` (all-expired rows only); `consume_directive` (`store.py:323`) has no callers; `fleet_metrics.py:61-62` counts all unconsumed; live ACTIVE sensor shows 7 pending.
- What is happening: a future purge caller would wipe the offline queue and under-report drops; recovery directives never appear consumed.
- Why it matters: edge buffering and recovery actions are resilience controls.
- Impact: silent sensor data loss; stale operator state.
- Fix / validation: use the expiry cutoff in DELETE; wire consumption; mixed-age unit test; live pending returns to 0.
- Owner/effort/deps: edge maintainer · S · none.
- Status: still-open (prior ND-P2-014/015, REV-P3-008).

### Finding ID: RES-P2-003 - Incident-critical runbooks are stale

- Severity: P2 · Confidence: High · Area: RES (runbooks)
- Evidence: `SENSOR_SILENCE.md:26-33` ("no VPN … no physical SPAN"), `DISK_PRESSURE.md:181` ("no offsite copy; local only"), `RESTORE.md` §7 superseded notes, `CERTIFICATE_AND_SECRET_ROTATION.md:349-355`; SENSOR_SILENCE also calls dead-man placement owner-gated while `phase9_gate_ledger.csv:8` is PASS.
- What is happening: responders following these runbooks get the wrong system model.
- Why it matters: runbook trust is the core of incident response.
- Impact: slower/wrong response and containment.
- Fix / validation: update the four runbooks to current state with an append-only status block; walk each read-only.
- Owner/effort/deps: falcon maintainer · M · none.
- Status: still-open (prior LIVE-P1-006).

### Finding ID: RES-P3-001 - Minor correctness drift (guard threshold text; peer-check counts)

- Severity: P3 · Confidence: High · Area: RES (docs/tests)
- Evidence: `bootstrap/96-disk-guard.sh:4` says "5 GiB" vs `disk_guard.sh:12` 10 GiB; `wg_peer_preservation_check.sh` compares block counts only, and the 2026-09-30 capture passes live=6/rendered=7 without key comparison.
- What is happening: small doc drift + a regression check that could miss one-peer-drop/one-stale-peer swaps.
- Why it matters: low, but both guard the recovery path.
- Impact: negligible today; possible masked regression.
- Fix / validation: fix text; compare public-key sets (live ⊆ rendered); mutate a conf to prove failure.
- Owner/effort/deps: falcon maintainer · S · none.
- Status: open.

## Critical Path Resilience Matrix

| Path | Failure | Detector | Latency | Recovery | Last exercise |
|---|---|---|---|---|---|
| Power → boot | total loss | DO watcher | ≤26 h | onboot=1, mount guard, units | 09-28 post-reboot 50/50 |
| Disk → writes | full | guard/<85% rules | min–hours | guard reclaim, ISM | reclaim never; drill 09-21 |
| Edge → WG → CP | loss | 24 h WG rule only | ≤24 h | queue + peer preservation | 90 s edge drill; hard-reset soak |
| Feeds → store | loss | 6 silence rules + DLQ | 15 m–6 h | buffer drain; runbooks | silence drill 09-23 |
| Grafana → relay → ntfy | relay loss | probe (routes via relay) | blind | dual path if relay alive | dual-delivery 09-23 |
| Backup → Spaces | offsite fail | none | until host loss | re-run; local snapshot | offsite success 09-30 (uncommitted) |
| Backup → restore | host loss | n/a | n/a | clean-host + offsite | P9-G09 09-23 (central only) |

## Recovery Readiness

| Procedure | Written | Exercised | Gap |
|---|---|---|---|
| Restore/clean-cluster | RESTORE + CLEAN_HOST_REBUILD | P9-G06 7 s/720 k docs; P9-G09 52 s/4.79 M docs (09-23) | central-only; edge/probe not reconstructed |
| Upgrade/rollback | UPGRADE_ROLLBACK | rehearsal 09-21 (P6-G07); edge drills 09-30 | no real component upgrade |
| Disk pressure | DISK_PRESSURE | synthetic drill 09-21; guard installed 09-27 | guard never reclaimed; doc stale |
| Sensor silence | SENSOR_SILENCE | live drill 09-23 (fired/delivered/cleared) | adversary-silence untested; doc stale |
| Power loss | post_reboot_verify | real 09-28, 50/50 | auto-start not yet re-exercised |
| Tunnel loss | VPN | R-30 recovery 09-24; rerun-preservation 09-30 | never-handshaked peers |
| Edge recovery | edge runbooks | renewal/update drills 09-30 | outage/backlog drills device-gated |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent offsite failure | High | Medium | High | RES-P0-001 | offsite metric+alert |
| Relay outage blind spot | High | Low-Med | High | RES-P0-002 | relay canary |
| Total-loss latency 26 h | High | Medium | High | RES-P1-001 | tighter heartbeat/watcher |
| Edge path unalerted | High | Medium | Medium | RES-P1-003 | deploy scoped rules |
| Root LV to 92% | Medium | Medium | High | RES-P1-005 | cleanup + growth alert |
| Reboot failure recurrence | Medium | Medium | High | RES-P2-001 | encode + boot regression |

## Recommendations

### Immediate / Release Blocking
- Add offsite/new-services freshness metrics + alert; commit the pending capture (RES-P0-001).
- Add an end-to-end relay canary verified on the independent instance (RES-P0-002).

### This Week
- Capture a passing `backup_new_services.sh` run at HEAD (RES-P1-004).
- Export all configured WG peers (RES-P1-006); `docker system df` + root attribution (RES-P1-005).

### This Month
- Freshness/swap/data-LV rules; guard reclaim drill; edge rule-set decision; offsite edge secrets; boot-order encoding; runbook refresh (RES-P1-002/003/005, RES-P2-001/003).

### Later / Platform Evolution
- Chaos suite below; edge rule ownership; retention/multi-node evolution per the capacity model.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Offsite metric + rule | closes P0 detector | `80-offsite-backup.sh`, `export_monitor_metrics.sh`, `90-alerting.sh` | forced failure alerts |
| Relay canary every 6 h | proves voice end-to-end | `90-alerting.sh`, DO watcher | DO delivery observed |
| Peer sentinel metric | lost-device visibility | `export_monitor_metrics.sh` | never-connected peer alerts |
| Timer `last_run` rules | stops silent monitor death | `export_monitor_metrics.sh`, `90-alerting.sh` | stop timer → alert |
| Fix purge cutoff | removes latent queue wipe | `src/falcon_agent/queue.py` | mixed-age unit test |
| 5→10 GiB text; key-set check | correctness | `96-disk-guard.sh`, `wg_peer_preservation_check.sh` | grep/mutation |

## Hardening Backlog

| Item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Chaos suite in lab cadence | P1 | falcon maintainer | L | owner windows |
| Watchdog config in repo + threshold review | P1 | owner+falcon | M | DO access |
| Edge rules + edge offsite secrets | P1 | owner | M | approval, ED-06 |
| Boot-order regression + host-only encoding | P2 | falcon maintainer | M | clean-host |
| Single-snapshot backup redesign | P2 | falcon maintainer | M | none |

## Chaos Test Plan

| # | Test | Safety | Expected signal | Capture |
|---|---|---|---|---|
| C1 | Stop relay 15 min | sanctioned | DO canary arrives | relay journal + DO receipt |
| C2 | Stop heartbeat timer 90 min | sanctioned | DO dead-man ≤ threshold | watcher log + DO ntfy |
| C3 | Offsite with bad endpoint (scratch) | non-destructive | offsite alert both paths | job log + relay |
| C4 | Fill data LV to 20 GiB free | sanctioned | early-warning alert; guard <10 only | metrics + guard |
| C5 | `docker kill` OpenSearch 10 min | sanctioned | cluster-red + feed rules; drain | metrics/DLQ |
| C6 | Halt VM 106 20 min | owner window | watcher latency; auto-start | host journal + verify |
| C7 | Edge agent stop 20 min | owner window | edge silence (after fix) | edge capture |
| C8 | `wg-quick down/up` | sanctioned | rules fire/clear; peers preserved | wg dump + alerts |
| C9 | Existing alert storm test | sanctioned | no drops | storm measurement |
| C10 | ISM delete in scratch | sanctioned | watermark/space behavior | counts |

## Suggested Tests

- Unit: `purge_expired` mixed-age; peer key-set preservation; offsite metric emission.
- Integration: relay-stopped canary; offsite failure alert; guard reclaim on synthetic LV; boot-order regression.
- E2E: host halt + watcher latency (C6); clean-host rebuild including the mount guard.
- CI: validate every shipped + host-only unit has a repo source; lint for `iso_now()` misuse.
- Security: verify the pending capture/archives carry no secrets.
- Manual: read-only runbook walk; confirm alerts land on both ntfy domains.

## Suggested Documentation Updates

- `docs/phase7/runbooks/{SENSOR_SILENCE,DISK_PRESSURE,RESTORE}.md`: current topology/offsite/guard/dead-man.
- `docs/phase9/NOTIFICATION_SEPARATION_RUNBOOK.md`: real watcher threshold + blind spot; relay canary.
- `docs/runbooks/OPERATOR_START_HERE.md`: total-loss first-15-minutes / blind-ops checklist.
- New: `docs/runbooks/{ALERT_PATH_RECOVERY,BOOT_ORDER}.md`.
- `ledgers/risk_register.md`: reconcile R-05/R-06 and R-29 (see 33 report).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Watcher cadence/threshold and the unreachable clause? | Blind-window sizing | watcher config on DO |
| Is heartbeat delivered via relay or direct? | RES-P0-002 scope | relay journal |
| VM 106 auto-start exercised since onboot=1? | Power-recovery claim | PVE journal |
| New-services `[ok]` at HEAD? | RES-P1-004 | root-only capture |
| Who owns root-LV Docker growth? | RES-P1-005 | owner decision |

## Appendix A — Prior-run status at current commits

| Prior ID | Status | Evidence |
|---|---|---|
| LIVE-P0-001 offsite silent | partially-fixed | succeeded 09-30 (uncommitted); no alert → RES-P0-001 |
| LIVE-P0-002 new-services unproven | partially-fixed/unverified | `d0f4aaf`; root log unreadable → RES-P1-004 |
| LIVE-P0-003 disk growth | partially-fixed | rotation live; guard 10 GiB; reclaims 0 → RES-P1-005 |
| LIVE-P0-004 TLS flap | partially-fixed | 6 h window; post-change volume unverified |
| LIVE-P1-001 root LV | still-open | 83% at 14:20Z → RES-P1-005 |
| LIVE-P1-002 monitor gaps | still-open | RES-P1-002 |
| LIVE-P1-003 never-handshake peers | still-open | 6/4 → RES-P1-006 |
| LIVE-P1-004 alert hygiene | partially-fixed | catalogue 31 = live; link-flap rule; labels |
| LIVE-P1-005 backup structure | still-open | duplicate snapshots → RES-P1-004 |
| LIVE-P1-006 runbook drift | still-open | RES-P2-003 |
| LIVE-P1-007 total-loss notice | still-open | 26 h; 09-28 proof → RES-P1-001 |
| INTG F1 WG rerun drops peers | fixed | `95-wireguard.sh:42-66`; capture 09-30T042108Z |
| INTG F2 worktree execution | still-open | edge ExecStart from repo tree |
| INTG F3/F4 edge CP/exporter loss | still-open | no falcon edge rules → RES-P1-003 |
| INTG F5/F10 edge PKI/host loss | still-open | local-only backup → RES-P1-003 |
| INTG F6 root LV | still-open | RES-P1-005 |
| INTG F7 sensor re-image | partially-fixed | peer preservation + onboarding; 24 h alert |
| INTG F8 pin/manifest drift | still-open | `EDGE_RELEASE_PIN.md:12,25,31` stale digest/commit/false template claim |
| INTG F9 non-additive rules deploy | still-open | dry-run only; owner decision pending |

**Overall resilience score: 3/5** — functional and improving, but detectors for the alerting/backup paths themselves are incomplete and several recovery paths remain unproven or stale.
