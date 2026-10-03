# Lens — Live Operations

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab
- Run: `20260930-0320-falcon-794ba31_edge-2b5bc8b`
- Prompt: lens `live_operations` (`lenses/live_operations.md`, area `LIVE`)
- Repo: falcon-build @ `794ba31` (live stack observed read-only)
- Generated: 2026-09-30 (converted from source audit)
- Area code: `LIVE`
- Source report: `source_reports/06-live-operations.md`
- Scope limitations: no root/docker/wg; live checks via systemd, listeners, filesystem, HTTP, read-only metrics/DB; container-internal state partly inferred

## Doctrine and Safety Compliance

- Audit-only observed: yes — read-only operator journey; no restarts or mutations
- Secret values redacted: yes
- Artifacts written only under the run folder: yes
- Repo HEAD re-checked before writing: yes

## Executive Summary

The core pipeline is **healthy and fast**: feeds at normal rates, ingestion lag sub-second to ~1.6 s, DLQ empty, Suricata 0 kernel drops, all service probes answering, snapshots succeeding locally. Two **real backup regressions were caught live** (offsite sync failed; new-services backup failing/unverified) — both **silent**, with no alert. Disk is the dominant near-term risk (data LV losing ~10 GB/day; the 5 GiB guard is the first signal; root LV at 82% is unguarded). Alerting works and delivery is reliable and dual-path, but 56% of real alerts are one flapping rule (TLS feed silence), and the 2026-09-28 power outage produced **no real-time external notification** (dead-man runs inside the monitored stack). Runbooks drift from reality, and the monitoring-of-the-monitoring has concrete gaps (exporter/probe freshness, swap, peers that never handshake, daily Suricata restarts).

Findings: 4 × P0, 7 × P1, 5 × P2 (16 total).

## Scope

- Host, containers/services, OpenSearch cluster/indices/retention, feeds/pipeline/data quality, alerting path, dashboards
- Runbook-vs-reality for operator tasks (read-only); failure modes; alert experience (sampled); monitoring-of-the-monitoring gaps
- Not reviewed: root-only logs (`/srv/falcon/backups/new-services.log`), container-internal state, offsite contents beyond sampled reads

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| Live host (systemd, disk, swap, wg, containers via metrics) | observation | Operator reality |
| OpenSearch/ISM state, index stats, snapshot history | observation | Retention and backup readiness |
| Feed rates + latency samples (72 h hourly checks) | observation | Pipeline health |
| Grafana rules, relay/ntfy history (153 alerts since Sep 22) | observation | Alert experience |
| Runbooks (`SENSOR_SILENCE`, `DISK_PRESSURE`, `RESTORE`, `VPN`, `OPERATOR_START_HERE`) | docs | Runbook vs reality |
| Backup scripts + timers (`80-offsite`, `85-backup-job`, `backup_new_services`, disk guard) | code | Backup readiness |

---

## Findings

### Finding ID: LIVE-P0-001 - Offsite backup failed silently; cold tier one day stale; no alert

- Severity: P0 (source: 06 §7 P0-1) · Confidence: High
- Area: LIVE · Scope: backup
- Evidence: offsite Spaces sync failed 2026-09-30 03:34Z instantly ("offsite sync unavailable"); last complete upload 2026-09-29 07:06Z; most likely cause: malformed `/home/user/.env` line `wifi_ssid=The Internet` (unquoted space → `set -euo pipefail` exit 127; reproduced); `falcon-backup-stale` tracks only the local freshness timestamp, which today's success refreshed. Source: 06 §5.3.
- What is happening: the offsite protection silently stopped; nothing alerted.
- Why it matters: offsite is the last line of defense against host loss.
- Impact: data-protection window silently degraded; a host loss during the window loses the delta.
- Recommended fix: quote `.env` values; re-run offsite and confirm the inventory upload; add offsite success/freshness metric + alert (and for new-services).
- Suggested validation: offsite inventory present and fresh; alert fires when the job fails.
- Owner suggestion: falcon maintainer/operator · Effort: S · Dependencies: none
- Status: open at audit time (fixed post-audit; verification pending — see `follow_up_register.md`)

### Finding ID: LIVE-P0-002 - New-services backup failing and unverified; archival state unproven

- Severity: P0 (source: 06 §7 P0-2) · Confidence: High
- Area: LIVE · Scope: backup
- Evidence: 00:46 manual run produced a 380 KB/217-entry archive but its critical-item check printed `[MISSING]` for all four items; 03:34 automated run logged failure; check greps absolute paths against `tar -tzf` while the script uses `--absolute-names`; root-only log needed to confirm. Source: 06 §5.3.
- What is happening: either a critical path is genuinely absent or the verification is wrong — either way the newest archival state is unproven.
- Why it matters: WireGuard keys / Wazuh registry / IRIS / enrollment state are the recovery set.
- Impact: recovery from host loss may lack critical services; false confidence from a green-looking archive.
- Recommended fix: read the root log; confirm archive contents; fix the verification (or the missing path); add success/freshness alert.
- Suggested validation: archive contains all critical items; verification passes deterministically.
- Owner suggestion: falcon maintainer · Effort: S/M · Dependencies: root access
- Status: open at audit time (script fix landed post-audit; verification pending)

### Finding ID: LIVE-P0-003 - Data-LV growth unmanaged (~10 GB/day); first signal only at the 5 GiB guard

- Severity: P0 (source: 06 §7 P0-3) · Confidence: High
- Area: LIVE · Scope: capacity
- Evidence: `/srv/falcon` 58.3→47.8 GB free in 24 h (~10 GB/day) = ~4.4 GB/day indices + ~6 GB/day rotated EVE (one parked `eve.json` 6.2 GB); disk guard acts only below 5 GiB and has **never reclaimed** (`reclaims_total 0`); no warning in the 15→5 GiB band; root LV not guarded. Source: 06 §5.1.
- What is happening: growth outpaces reclamation; the guard threshold is the only signal and sits 4–5 days away.
- Why it matters: full data LV wedges writers (OpenSearch, Prometheus, edge spool) and risks index loss.
- Impact: monitoring outage; potential data loss; sawtooth operation once the guard trips.
- Recommended fix: automate EVE housekeeping (compress/delete rotated files >12–24 h after consumption); consider retention 14→10–12 d or automated R2 cold-offload before ISM delete; add a <15 GiB warning alert.
- Suggested validation: free space stable over 7 days; warning fires before the guard.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: retention policy decision
- Status: open at audit time (rotation/prune fixes landed post-audit; monitoring pending)

### Finding ID: LIVE-P0-004 - TLS-silence alert flaps ~once an hour; 56% of all alerts are noise

- Severity: P0 (source: 06 §7 P0-4) · Confidence: High
- Area: LIVE · Scope: alerting
- Evidence: 85 of 153 real alerts since Sep 22 are the "Syslog-TLS feed silence" rule; the feed carries ~1.3 Wazuh forwards/hour (32 events/24 h); rule fires on short windows. Source: 06 §3.5, §6.
- What is happening: a legitimate low-traffic feed triggers a high-frequency alert.
- Why it matters: operator fatigue masks real alerts; the alert channel is part of the monitoring system.
- Impact: missed real events; eroded trust in alerting.
- Recommended fix: raise the window to 6–12 h or re-anchor the rule on the Wazuh forwarder/manager liveness; rename to reflect what it watches.
- Suggested validation: alert count drops to expected; a real Wazuh-path outage still alerts.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open at audit time (tuned post-audit; verification pending)

### Finding ID: LIVE-P1-001 - Root LV at 82% and unguarded; Docker growth unowned

- Severity: P1 (source: 06 §7 P1-5) · Confidence: High
- Area: LIVE · Scope: capacity
- Evidence: root LV 133/171 GB (82.2%); +75 GB jump Sep 27–28 (Wazuh/IRIS/R2 volumes); growth now ~0.2–0.3 GB/day but a prior one-night 75 GB jump; only an 85% warning rule above it; disk guard covers `/` but no per-directory signal. Source: 06 §3.1, §5.1.
- What is happening: root growth is neither bounded nor attributed; the last jump shows it can move fast.
- Why it matters: root exhaustion breaks the platform (logs, Docker, textfile metrics).
- Impact: platform-level outage risk; recovery requires manual cleanup.
- Recommended fix: `docker system df` cleanup, consider moving Wazuh volumes off `/`, add per-directory/root growth signal.
- Suggested validation: root usage trend flat or bounded; alert before 90%.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none
- Status: open at audit time

### Finding ID: LIVE-P1-002 - Monitoring-of-the-monitoring gaps (exporter/probe freshness, swap, guard metric, alert-eval health)

- Severity: P1 (source: 06 §7 P1-6) · Confidence: High
- Area: LIVE · Scope: observability
- Evidence: no `falcon_metrics_last_run` metric; service-probe results can freeze at `1` if the timer dies; no swap alert (59% used); no alert on `falcon_disk_guard_free_bytes`; Grafana alert-evaluation health not checked; `node_textfile_scrape_error` unalerted. Source: 06 §5.5.
- What is happening: the monitors can stop without being noticed; last-known values look healthy.
- Why it matters: silent monitor death = silent blindness.
- Impact: undetected monitoring loss; false confidence.
- Recommended fix: freshness metrics + staleness alerts for exporter and probe timers; swap alert; guard-metric alert; alert-eval dead-man (checked externally).
- Suggested validation: kill each timer; alert fires.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none
- Status: open at audit time

### Finding ID: LIVE-P1-003 - Peers that never handshake are invisible; a lost device would not alert

- Severity: P1 (source: 06 §7 P1-7) · Confidence: High
- Area: LIVE · Scope: VPN
- Evidence: per-peer stale rule only covers peers that handshaked at least once; `10.99.0.20` ("samsung") is configured and never handshaked, invisible; 2/6 peers never handshaked. Source: 06 §3.1, §5.4.
- What is happening: the metric model omits never-connected peers.
- Why it matters: a peer that never connects (or a device lost before first handshake) cannot alert.
- Impact: silent connectivity gaps; fleet blind spots.
- Recommended fix: export a metric for every configured peer (`-1`/large age when never handshaked); retire or document `10.99.0.20`.
- Suggested validation: never-handshaked peer produces an alert condition (or explicit "expected idle" state).
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open at audit time

### Finding ID: LIVE-P1-004 - Alert hygiene: benign UniFi messages, Zen Link-Down flood, catalogue drift

- Severity: P1 (source: 06 §7 P1-8) · Confidence: High
- Area: LIVE · Scope: alerting
- Evidence: "Device syslog errors" fires on benign UniFi broker/AP messages; Zen Link-Down flood ~600/h; `ALERT_CATALOGUE.yaml` lists 29 rules while 30 are live (missing `falcon-wg-peer-stale`). Source: 06 §3.5, §6; 05 §INT-M4.
- What is happening: known-benign families are not excluded; a flood source has no rate alert; catalogue is stale.
- Why it matters: noise + untracked rules degrade the alert path's credibility.
- Impact: operator fatigue; alert inventory not auditable.
- Recommended fix: exclude the benign families (or per-host dedupe); per-host rate alert for Zen; update catalogue to live state.
- Suggested validation: noise counts drop; catalogue matches live rules.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open at audit time

### Finding ID: LIVE-P1-005 - Backup structure: duplicate daily snapshots, undocumented recoverability window, rehearsal scope

- Severity: P1 (source: 06 §7 P1-9) · Confidence: High
- Area: LIVE · Scope: backup
- Evidence: two snapshots/day (`85-backup-job.sh` + `80-offsite-backup.sh`, ~3 min apart); snapshot coverage ~7 days → a deleted index is restorable ~a week after deletion (window undocumented); clean-host rehearsal covers OpenSearch but not R2/Wazuh/IRIS/edge; local repo keeps 10 snapshots. Source: 06 §3.3, §5.3.
- What is happening: duplicated storage/upload; undocumented recovery windows; rehearsal narrower than the production claim.
- Why it matters: restore expectations are not documented or fully proven.
- Impact: surprise data loss after the ~7-day window; restore-time uncertainty for off-repo services.
- Recommended fix: offsite reuses the job's snapshot; document RPO/RTO + post-deletion window; extend the rehearsal.
- Suggested validation: one snapshot/day; documented windows match rehearsal results.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none
- Status: open at audit time

### Finding ID: LIVE-P1-006 - Runbook drift and missing non-root health view

- Severity: P1 (source: 06 §7 P1-10) · Confidence: High
- Area: LIVE · Scope: runbooks
- Evidence: `SENSOR_SILENCE.md` says "no VPN / no physical SPAN"; `DISK_PRESSURE.md`/`RESTORE.md` list stale capacities/snapshots and miss the guard/offsite flow; `VPN.md` peer table omits the edge peer; a non-root operator cannot run most documented commands (docker root-only; `/srv/falcon/secrets` root-only; `wg show` denied). Source: 06 §4, §5.
- What is happening: incident-time instructions are wrong or unexecutable for the available role.
- Why it matters: the operator journey fails exactly when it matters.
- Impact: slower/wrong incident response; escalation to root for basic checks.
- Recommended fix: update the four runbooks; add a non-root read-only health view; note `localhost:9200` is the Wazuh indexer.
- Suggested validation: follow each runbook read-only as non-root; every step works or states its role requirement.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none
- Status: open at audit time

### Finding ID: LIVE-P1-007 - Power outage produced no real-time external notification; dead-man runs inside the stack

- Severity: P1 (source: 06 §7 + §5.4) · Confidence: High
- Area: LIVE · Scope: resilience/alerting
- Evidence: 2026-09-28 host died 10:58Z; alerts resumed only 15:32Z after recovery; the daily heartbeat runs inside the monitored stack; the independent DO watcher (`/var/log/falcon-watcher.log` mtime exported) is not in the repo and undocumented; detection latency hours-to-a-day. Source: 06 §3.5, §5.2, §5.4.
- What is happening: total-host failure has no external real-time alarm.
- Why it matters: a production monitoring system must announce its own death.
- Impact: outage detection by humans only; the Sep 28 outage is the proof.
- Recommended fix: document the DO watcher (threshold/cadence) and tighten it; add an external dead-man check on the alert-eval cycle; record in the repo.
- Suggested validation: stop the lab; external notification within the documented threshold.
- Owner suggestion: falcon maintainer/owner · Effort: M · Dependencies: external watcher access
- Status: open at audit time

### P2 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| LIVE-P2-001 | P2 | "Network throughput" panel broken (containerized node-exporter only sees its own netns); host NIC counters unmonitored | 06 §3.6, §7 P2-11 | Host-netns exporter or drop/repair panel |
| LIVE-P2-002 | P2 | Index hygiene: leftover test indices (`falcon-test`, `falcon-canary`, fixture/retention tests, `other-site-index`); no retention on `security-auditlog-*`, `top_queries-*`, ISM history | 06 §3.3, §7 P2-12 | Cleanup + ISM policies |
| LIVE-P2-003 | P2 | Mapping drift: `event_type` keyword since 09.23 (older indices text) → `.keyword` aggregations silently empty; `host` text-only on 09.29/09.30 | 06 §3.3, §7 P2-13 | Document/repair mappings; add `host.keyword` |
| LIVE-P2-004 | P2 | Daily Suricata in-container restart (EVE rotation) invisible (`RestartCount` 0, uptime resets) | 06 §3.4, §7 P2-14 | Reload without restart or uptime-decrease alert |
| LIVE-P2-005 | P2 | Secrets hygiene: `/home/user/.env` holds sudo password + third-party keys in cleartext; credentials printed to terminals recently | 06 §7 P2-15 (see REV-P3-010/011) | Permissions/ownership review; split per-service files; rotate exposed credentials |

## Cross-References

| This report ID | Related lens | Related ID | Relationship |
|---|---|---|---|
| LIVE-P0-001/002 | INTG-P1-003 | offsite coverage | Same backup gap, edge view |
| LIVE-P0-003, LIVE-P1-001 | INTG-P2-005 | shared host resources | Joint resource risk |
| LIVE-P0-004, LIVE-P1-004 | INTG-P1-001, INTG-P2-004 | alert coverage/drift | Edge + catalogue |
| LIVE-P1-006 | ND-P1-003 | runbook safety | Dangerous/stale runbooks |
| LIVE-P1-007 | INTG-P1-001 | detection latency | External visibility |

**Domain routing for the next full run:** `14` (observability), `32` (backup/restore drill), `13` (resilience), `15` (capacity/cost), `30` (notification delivery), `06` (secrets hygiene), `16` (runbooks).

## Open Questions (from source)

1. Where is the DO watcher configured, and what threshold does it use? (06)
2. Are the four critical new-services paths genuinely absent or is the check wrong? (root log)
3. Is retention (14 d) intended to shrink, or should R2 cold-offload be automated? (06 §7 P0-3)
4. Who owns the root LV cleanup (Docker/Wazuh volumes)? (06 §7 P1-5)

## Appendix

- Full narrative, sampled values, and evidence snapshots: `source_reports/06-live-operations.md`
- Finding counts: LIVE-P0 ×4, LIVE-P1 ×7, LIVE-P2 ×5
