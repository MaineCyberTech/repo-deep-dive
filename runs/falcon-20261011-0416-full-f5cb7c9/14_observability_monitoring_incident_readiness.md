# 14_observability_monitoring_incident_readiness — Prompt 14 - Observability, Monitoring, and Incident Readiness Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `14_observability_monitoring_incident_readiness.md` (area OBS, prompt)

## Verification Performed

# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c9` (branch `main`; `origin/main` = `584e1a3` + publication commits)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-11T04:55Z
- Auditor: subagent (OBS)
- Area code: OBS
- Scope limitations: read-only; Grafana/Prometheus APIs queried with GETs only; no alert was injected. Alert history is sampled (relay journal; annotation caps); the boot journal of the 10-day boot was queried with bounded ranges.

## Scope

Reviewed structured logs, request/correlation IDs, error tracking, metrics, tracing, health/readiness, client/API/worker errors, job metrics, DB/queue/webhook/notification metrics, uptime checks, alerts, dashboards, incident runbooks, audit/security logs, release markers, user-impact and data-quality signals at `f5cb7c9`. Verified live: the Grafana rule set (count and selected rule states), Prometheus targets/alerts, the aggregator's internal metrics endpoint, the textfile collector output, the alert relay journal and delivery paths, the dead-man/canary path, and rule provisioning vs code/catalogue.

## Evidence Reviewed

- `bootstrap/90-alerting.sh` (86 `write_rule` calls; freshness/scrape/relay/drop rules; new proxy-listener rule :252-254)
- `automation/validation/export_monitor_metrics.sh` (textfile exporter; sink/all-component metrics :60-92; backup gauges :225-241, :585-592)
- `automation/validation/alert_rule_lint_test.sh`, `automation/validation/build_alert_catalogue.py`, `docs/phase9/ALERT_CATALOGUE.yaml`, `docs/phase9/ALERT_FIRING_PROOFS.md`
- `automation/validation/disk_guard.sh` (self-alerting), `alert_canary.sh`, `heartbeat.sh`, `service_probe.sh`, `pipeline_e2e_check.sh`
- `config/systemd/falcon-metrics.timer`, `falcon-service-probe.timer`, `falcon-alert-canary.timer`, `falcon-heartbeat.timer`, `falcon-alert-relay.service`, `falcon-backup.service`
- `automation/alerting/ntfy_relay.py`, `automation/alerting/do_watcher/watch.sh`
- `docs/runbooks/MONITORING_SCRAPE_AND_FRESHNESS.md`, `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`, `README.md:30`, `docs/CURRENT_STATE.md`
- Live: Grafana `/api/v1/provisioning/alert-rules` (86), `/api/alertmanager/grafana/api/v2/alerts`, Prometheus `/api/v1/alerts`, `/api/v1/query[_range]`, aggregator `/metrics` on 127.0.0.1:9598, `/srv/falcon/textfile/falcon_metrics.prom`, `journalctl -u falcon-alert-relay.service`, `journalctl -u falcon-disk-guard.service`, container state

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Grafana `GET /api/v1/provisioning/alert-rules` -> 86 rules | live | Prior OBS-P0-001 (rules not provisioned) | Supported: 86 live = 86 `write_rule` calls; the new proxy rule present |
| `falcon_runtime_source_dirty 0`; `falcon_runtime_source_behind_remote 0`; live tree HEAD `f5cb7c9`, `git status` clean | live | Prior OBS-P0-001 root cause (tree 22 behind) | Supported: tree at the audited commit |
| Exporter code exports `falcon_pipeline_all_discarded_events_total`, `_all_errors_total`, `falcon_pipeline_aggregator_drop_logs_15m`; live textfile contains them; both rules live | live/repo | Prior OBS-P1-001 | Supported |
| `comm` catalogue (85 entries) vs live rule titles: `falcon-wazuh-proxy-listeners` absent from the catalogue; README/CURRENT_STATE say 85 | repo/live | Prior OBS-P2-001 | Regressed: 85 vs 86 |
| Relay journal Oct 9/10/11: 152/69/11 FIRING; top Oct 10-11: disk guard 48, Disk space low 7, DLQ 6, ISM burst 5, Wazuh feed stale 4, root projection 3, counters 2 | live | Prior OBS-P2-002 | Still open; quantified |
| `falcon_pipeline_all_errors_total` 0 -> 2 -> 4 (04:05-04:12) -> 0; raw `/metrics` has no `vector_component_errors_total`/`discarded_events_total` series now; `resets(...[1h])=1`; `increase(...[15m])=2.03` at 04:20 with the counter at 0 | live | New counters-rule behavior | Supported: benign source errors + series disappearance |
| Aggregator log 04:03-04:04Z: `ERROR source edge_ingest ... Rejection([MethodNotAllowed, MethodNotAllowed])` | live | Counters-rule trigger source | Supported: HTTP method rejections, no loss |
| `falcon-backup.service` activating since 03:30:03Z (>1 h); no `TimeoutStartSec`/`RuntimeMaxSec`; no `OnFailure=` in `config/systemd/`; no `node_systemd_unit_state` rule | live/repo | New stuck-run/unit-failure detection gap | Supported |
| `sha256` live `/etc/prometheus/edge-alerts.yaml` == repo `config/prometheus/edge-alerts.yaml` (`7608f39a...`); `diff` rc=0 | live | Prior OBS-P3-001 | Verified-fixed |
| Freshness/scrape/relay/guard rules live (`falcon-textfile-collector-stale[-daily]`, `falcon-monitoring-scrape-absent`, `falcon-relay-path-failures`, `falcon-disk-guard-stale`, canary) | live/repo | Monitoring-of-the-monitoring | Supported: present |

## Executive Summary

The prior OBS deployment gap is closed: the live Grafana rule set now has 86 rules matching `bootstrap/90-alerting.sh` one-for-one (including the previously missing freshness/scrape/relay rules and the new `falcon-wazuh-proxy-listeners`), the runtime tree is at the audited commit (`f5cb7c9`, clean, 0 behind), the drop-visibility metrics are exported and alerted, and the live edge-alerts file matches the committed config byte-for-byte. Monitoring-of-the-monitoring exists: textfile freshness rules (fast and daily sets), scrape-absence rules, relay-path-failure rules, a disk-guard staleness rule, a weekly canary, and the DO-side dead-man watcher.

Current gaps are quality and coverage, not existence. (1) The alert catalogue/README/CURRENT_STATE now lag live by one rule (85 vs 86) even though the catalogue header and generator claim it "cannot drift"; the lint is static and the drift test compares README to the catalogue, so the drift is invisible. (2) Alert noise remains high: 69 FIRING notifications on Oct 10 and 11 by 04:30 on Oct 11, dominated by the disk-guard alert repeated every 15 minutes (48 in 28 h) with no repeat suppression, plus reboot artifacts (the Suricata uptime-reset rule fired ~50 minutes on a planned reboot with 0 real restarts). (3) The new pipeline counters rule fired on benign `edge_ingest` HTTP method rejections and the underlying Vector counters vanish when idle, producing a Prometheus counter reset that distorted `increase()` during the firing window. (4) There is no alert for a stuck/hung backup run or for a failed systemd unit; the backup service ran >1 h with no signal, and detection depends on 36 h freshness rules.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Rule provisioning | `bootstrap/90-alerting.sh` (86), live Grafana (86) | Source of truth for alerts | In sync | Low | New proxy rule included |
| Catalogue | `docs/phase9/ALERT_CATALOGUE.yaml` (85) | As-code catalogue | Lags live by 1 | Medium | Claims it cannot drift |
| Rule lint | `automation/validation/alert_rule_lint_test.sh` | Static lint (count, dup UIDs/expressions, delimiters) | PASS (86 derived) | Low | No catalogue comparison |
| Drift test | `automation/validation/tests/readme_ledger_drift_test.sh` | README vs catalogue counts | PASS (85/85) | Medium | Blind to live |
| Textfile exporter | `automation/validation/export_monitor_metrics.sh` + `falcon-metrics.timer` | Metrics every minute | Running (04:38Z) | Low | Includes drop/error sums |
| Aggregator metrics | `config/vector/aggregator.yaml:33-34,142` -> 127.0.0.1:9598 | Component metrics | Running | Medium | Lazy series disappear when idle |
| Relay | `automation/alerting/ntfy_relay.py` + `falcon-alert-relay.service` | Webhook -> ntfy (two paths) | Running; publishes 200 | Low | Noise source |
| Disk guard | `automation/validation/disk_guard.sh` | Reclaim + self-alert | Failing every 15 min; alerts | Medium | No repeat suppression |
| Backup job | `config/systemd/falcon-backup.{service,timer}` | Nightly backup | Stuck activating >1 h; no alert | High | OBS-P2-004 |
| Canary / heartbeat | `alert_canary.sh` (weekly), `heartbeat.sh` (hourly) + DO watcher | Alert-path death detection | Running | Low | Canary weekly |
| Dashboards | `config/grafana/dashboards/*.json` | Ops views | Present | Low | Not re-verified this run |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Structured logs | 4 | Container/journald logs; relay logs | No correlation IDs at the host level | Accept for infra scope |
| Request IDs/correlation | 3 | Vector request ids in sink logs; relay publishes alert names | No end-to-end correlation | Document |
| Error tracking | 3 | Vector component errors, exporter, rules | Lazy series; benign errors counted | OBS-P2-003 |
| Metrics | 4 | Textfile exporter + Vector internal metrics + rules | Reset behavior | OBS-P2-003 |
| Tracing | 1 | None (not applicable to the infra stack) | n/a | Accept |
| Health/readiness | 4 | Healthchecks, service probe, pipeline E2E | Post-reboot checks manual | RES-P3-002 |
| Client/API/worker errors | 3 | Ingest rejections logged; sink rules | Source rejections alert as loss | OBS-P2-003 |
| Job metrics | 4 | Backup/cold-copy/Wazuh/guard stamps + rules | No stuck-run signal | OBS-P2-004 |
| DB/queue/webhook/notification metrics | 4 | OpenSearch/sink/buffer/relay metrics + rules | Sink DLQ absent (known) | Keep WH-P1-001 |
| Uptime checks | 4 | Service probe + pipeline E2E + site watcher | n/a | Keep |
| Alerts | 3 | 86 rules; delivery 200 both paths | Noise; catalogue drift | OBS-P2-001/002 |
| Dashboards | 3 | 3 dashboards/73 panels | Not re-verified | Refresh after changes |

## Detailed Review

### Item: Rule provisioning and drift

- Evidence: live 86 vs script 86 vs catalogue 85; `README.md:30`; `docs/CURRENT_STATE.md:56,112`; catalogue header line 2; `build_alert_catalogue.py:1-9`; `alert_rule_lint_test.sh` (static); `readme_ledger_drift_test.sh`.
- What it does: `90-alerting.sh` provisions rules; the catalogue is regenerated from live Grafana; README counts are checked against the catalogue.
- How it appears to work: provisioning is idempotent and in sync; the catalogue was rebuilt on 2026-10-10 (85 rules) before PR #53 added `falcon-wazuh-proxy-listeners` (live 86), so the catalogue/README/CURRENT_STATE are stale by one rule.
- Missing controls: a catalogue-vs-live (or catalogue-vs-script) comparison in CI; the lint does not compare sets.
- Risks: operators and future agents trust stale counts; a missing rule would not be caught by the drift test.
- Recommended improvement: regenerate the catalogue after #53 (or run the generator in CI with live access), and add a script-vs-catalogue rule-ID comparison.
- Suggested tests: extend `alert_rule_lint_test.sh` to diff script rule IDs against `ALERT_CATALOGUE.yaml`.
- Suggested docs: update the README/CURRENT_STATE counts and the catalogue.

### Item: Alert signal quality (noise)

- Evidence: relay journal Oct 9/10/11 = 152/69/11 FIRING; top Oct 10-11 offenders; the disk guard posts directly to the relay every 15 min; Suricata reboot artifact.
- What it does: every Grafana/Prometheus notification is relayed to ntfy on two paths.
- Current controls: per-rule `for`, repeat intervals, some tuning (syslog/TLS).
- Missing controls: repeat suppression for the self-alerting disk guard; reboot-aware handling for uptime-reset rules; a noise budget review after incidents.
- Risks: alert fatigue; real signals buried.
- Recommended improvement: rate-limit the disk-guard alert (e.g. hourly), suppress/annotate planned-reboot artifacts, and re-run the documented 7-day noise accounting.
- Suggested tests: a noise accounting script over the relay journal with per-rule counts.
- Suggested docs: a noise review section in `MONITORING_SCRAPE_AND_FRESHNESS.md`.

### Item: Pipeline drop/error counters

- Evidence: exporter :60-92; live metric behavior; aggregator log; rule `falcon-pipeline-discarded-events`.
- What it does: exports all-component discard/error sums plus a log-derived drop counter.
- How it appears to work: the sums are lazily registered by Vector and disappear when idle; the exporter then writes 0, so Prometheus sees a counter reset.
- Risks: false/sustained increases after resets; benign HTTP rejections count as "discarded/error events".
- Recommended improvement: exclude source-level HTTP 4xx/method rejections from the loss signal (or use a sink-focused signal) and document the reset behavior; prefer a gauge/counter that does not vanish.
- Suggested tests: a bounded probe (GET/OPTIONS) asserting the rule does not fire on method rejections; a reset test asserting no spurious increase.
- Suggested docs: `MONITORING_SCRAPE_AND_FRESHNESS.md` counters semantics.

### Item: Job/unit failure detection

- Evidence: backup service activating >1 h; no start timeout; no `OnFailure=`; no systemd unit-state rule; disk-guard unit failed repeatedly.
- What it does: job failures surface via freshness rules (36 h), dead-letter markers, or the job's own relay alert.
- Missing controls: a stuck-run alert; a generic unit-failure alert.
- Risks: a hung backup is invisible for 36 h; silent job failures.
- Recommended improvement: bound the run and alert on a stuck run; consider a small set of `node_systemd_unit_state`-style checks for critical units (via the textfile exporter).
- Suggested tests: SIGSTOP a job and assert an alert within the bound.
- Suggested docs: job monitoring in `RUNTIME_AND_SCHEDULE.md`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| OBS-001 | Structured logs | journald/container logs | Structured where available | No correlation IDs | P3 | Accept/document |
| OBS-002 | Request IDs/correlation | Vector request ids; relay logs | Partial | End-to-end absent | P3 | Document |
| OBS-003 | Error tracking | Vector component errors | Rules | Lazy series/reset | P2 | OBS-P2-003 |
| OBS-004 | Metrics | Exporter + internal metrics | Broad | Reset behavior | P2 | OBS-P2-003 |
| OBS-005 | Tracing | none | n/a | n/a | n/a | Accept |
| OBS-006 | Health/readiness | Healthchecks + probes | Good | Boot checks manual | P3 | RES-P3-002 |
| OBS-007 | Client/API/worker errors | Ingest rejections | Logged + counted | Counted as loss | P2 | OBS-P2-003 |
| OBS-008 | Job metrics | Stamps + rules | Good | No stuck-run signal | P2 | OBS-P2-004 |
| OBS-009 | DB/queue/webhook/notification metrics | Sink/buffer/relay metrics | Good | Sink DLQ absent | P2 | Keep WH-P1-001 |
| OBS-010 | Uptime checks | Probe + E2E + watcher | Good | n/a | P3 | Keep |
| OBS-011 | Alerts | 86 rules; delivery 200 | Good | Noise; catalogue drift | P2 | OBS-P2-001/002 |
| OBS-012 | Dashboards | 3 dashboards/73 panels | Present | Not re-verified | P3 | Refresh |

## Findings

### OBS-P2-001 - ALERT_CATALOGUE.yaml, README and CURRENT_STATE lag live Grafana by one rule while claiming the catalogue cannot drift

- Severity: P2
- Confidence: High (live API count, repo counts, set difference)
- Area: OBS
- Evidence:
  - Live Grafana `GET /api/v1/provisioning/alert-rules` -> 86 rules
  - `docs/phase9/ALERT_CATALOGUE.yaml` -> 85 entries; `falcon-wazuh-proxy-listeners` absent
  - `bootstrap/90-alerting.sh` -> 86 `write_rule` calls (new rule at :252-254)
  - `README.md:30` ("85 alert rules"); `docs/CURRENT_STATE.md:56,112` ("85 rules live", page dated 2026-10-10)
  - `docs/phase9/ALERT_CATALOGUE.yaml:2` ("Generated from the live Grafana rules") and `automation/validation/build_alert_catalogue.py:1-9` ("so it cannot drift from what is deployed")
  - `automation/validation/alert_rule_lint_test.sh` is a static lint (derived count 86) with no catalogue comparison; `readme_ledger_drift_test.sh` compares README (85) to the catalogue (85), so the live drift is invisible
- What is happening: PR #53 added `falcon-wazuh-proxy-listeners` on 2026-10-10 after the catalogue was regenerated; the catalogue and both doc counts still say 85, and no check compares them to the live rule set.
- Why it matters: the "cannot drift" claim is false; operators and future agents use the catalogue as the as-code source; a missing rule would not be caught by the current drift test.
- Recommended fix: regenerate the catalogue from live Grafana (86) and update README/CURRENT_STATE; extend `alert_rule_lint_test.sh` (or the drift test) to compare the script's rule IDs against the catalogue so the next rule addition cannot drift.
- Suggested validation: the extended lint fails on an injected rule-ID mismatch; `readme_ledger_drift_test.sh` passes with 86/86.
- Owner suggestion: platform
- Effort estimate: S
- Status: regressed (prior OBS-P2-001 was verified-fixed at 85/85/85 before PR #53)

### OBS-P2-002 - Alert noise remains high and is now dominated by the disk-guard alert repeated every 15 minutes; planned reboots produce artifact alerts

- Severity: P2
- Confidence: High (relay journal counts over Oct 9-11)
- Area: OBS
- Evidence:
  - Relay journal FIRING per day: Oct 9 = 152, Oct 10 = 69, Oct 11 (00:00-04:30) = 11 (+8 RESOLVED)
  - Top offenders Oct 10-11: `Falcon disk guard: root still below threshold` 48, `Disk space low` 7, `Offsite backup retries exhausted (dead-letter)` 6, `ISM deletion burst` 5, `Wazuh alert feed stale` 4, `Root disk projected full within 7 days` 3, `Pipeline discarded/error events (counters)` 2, `Live source tree not reviewable` 2
  - `automation/validation/disk_guard.sh:64-81` posts directly to the relay on every failing run (15 min) with no rate limit
  - `Suricata restart loop` FIRING 02:39:28Z -> RESOLVED 03:29:33Z after the planned reboot while `falcon_suricata_restarts_total` = 0 (uptime-reset artifact of the rule)
  - `docs/runbooks/CAPACITY_AND_TELEMETRY.md:178-183` (planned work should be muted/annotated and documented)
- What is happening: a legitimate but persistent condition (root free below the guard threshold) repeats an urgent alert every 15 minutes, and the uptime-reset Suricata rule fires for ~50 minutes on every reboot even with zero restarts.
- Why it matters: alert fatigue buries real signals; the repeated urgent notifications add no new information after the first.
- Recommended fix: rate-limit the disk-guard alert (e.g. hourly or state-change-only); exclude planned reboots from the Suricata uptime-reset rule or annotate them; re-run the documented 7-day noise accounting and record the result.
- Suggested validation: after tuning, a 7-day count shows the disk-guard rule at <=1/day for a persistent condition and no Suricata firing across a sanctioned reboot.
- Owner suggestion: platform
- Effort estimate: S
- Status: still-open (prior OBS-P2-002)

### OBS-P2-003 - Pipeline counters rule fires on benign edge_ingest HTTP method rejections and the lazily-registered Vector counters vanish, producing a counter reset inside the firing window

- Severity: P2
- Confidence: High (rule definition, live metric series, aggregator log, Prometheus reset/increase values)
- Area: OBS
- Evidence:
  - Rule `falcon-pipeline-discarded-events` (title "Pipeline discarded/error events (counters)", `bootstrap/90-alerting.sh:246-248`): `(increase(falcon_pipeline_all_discarded_events_total[15m]) > bool 0) + (increase(falcon_pipeline_all_errors_total[15m]) > bool 0)`
  - Relay: FIRING 04:10:25Z -> RESOLVED 04:21:25Z (both paths)
  - `falcon_pipeline_all_errors_total` 0 -> 2 (04:05Z) -> 4 (04:06-04:12Z) -> 0 (from 04:13Z); `falcon_pipeline_all_discarded_events_total` stayed 0 throughout
  - Aggregator log 04:03:42-04:04:54Z: `ERROR source{component_id=edge_ingest component_type=http_server} ... Rejection([MethodNotAllowed, MethodNotAllowed])` (GET/OPTIONS on the ingest listener)
  - Raw `http://127.0.0.1:9598/metrics` now contains no `vector_component_errors_total` or `vector_component_discarded_events_total` series (the counters are lazily registered and disappear when idle); the exporter then writes 0 (`export_monitor_metrics.sh:84-85,505-509`)
  - Prometheus: `resets(falcon_pipeline_all_errors_total[1h])` = 1; `increase(...[15m])` = 2.03 at 04:20Z while the counter was 0 (the reset kept the alert firing ~8 minutes past the errors)
- What is happening: the "discarded/error" signal conflates benign source-level HTTP rejections (probes/scanners hitting the ingest listener with GET/OPTIONS) with data loss; the underlying series then vanish, so the exported counter resets to 0 and `increase()` reports the pre-reset value as an increase.
- Why it matters: noise on a loss-detection rule and a counter semantic that can distort both firing and resolution timing; the rule no longer cleanly answers "did we lose events".
- Recommended fix: exclude source-level HTTP 4xx/method rejections from the loss signal (e.g. only sink errors/discards plus the log-derived non-retriable drop counter), or add a dedicated rejection counter that is not part of the loss rule; document the reset behavior; optionally export a stable gauge of the last-window loss.
- Suggested validation: a bounded GET/OPTIONS probe asserting the loss rule does not fire; a reset test asserting `increase()` stays 0 after the series disappears.
- Owner suggestion: platform
- Effort estimate: S
- Status: open

### OBS-P2-004 - No alert for a stuck backup run or for failed systemd units; detection depends on 36 h staleness rules

- Severity: P2
- Confidence: High (live service state, unit definitions, rule inventory)
- Area: OBS
- Evidence:
  - `systemctl status falcon-backup.service`: `activating (start)` since 2026-10-11T03:30:03Z (>1 h 10 m at 04:40Z); the offsite upload is re-copying 68.3 GiB
  - `config/systemd/falcon-backup.service` has `TimeoutStopSec=900` but no `TimeoutStartSec`/`RuntimeMaxSec`
  - `grep -rn 'OnFailure' config/systemd/` -> no matches; `grep node_systemd bootstrap/90-alerting.sh` -> no unit-state rule
  - The only backstops for this run are the 36 h `Backup stale`/`Offsite backup stale` rules (`bootstrap/90-alerting.sh:476-478`) and the dead-letter marker (which is cleared on success only)
  - `automation/validation/disk_guard.sh:147-159` exits 1 on every failing run (unit failed) while alerting itself; there is no generic unit-failure alert
- What is happening: a run that neither succeeds nor fails is invisible for up to 36 hours; failed units are only noticed if the job self-alerts or a staleness rule fires.
- Why it matters: a hung backup delays detection of a growing RPO; silent unit failures can go unnoticed for other jobs.
- Recommended fix: add `RuntimeMaxSec` (or an equivalent watchdog) to the backup unit and a stuck-run alert (e.g. the exporter publishing a "run in progress > N minutes" signal); consider a textfile-based check of critical unit states.
- Suggested validation: SIGSTOP the offsite uploader in a bounded drill and assert an alert within the bound; fail a test unit and assert the unit-state check fires.
- Owner suggestion: platform
- Effort estimate: S-M
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Catalogue/doc counts drift from live rules | P2 | High (already) | Wrong as-code source; missed rule | 85 vs 86 | OBS-P2-001 |
| Alert fatigue from repeated urgent notifications | P2 | High | Missed real alerts | 48 disk-guard firings/28 h | OBS-P2-002 |
| Loss rule fires on benign rejections / reset distortion | P2 | Medium | Trust in loss signal | counters behavior | OBS-P2-003 |
| Hung job invisible for 36 h | P2 | Medium | RPO growth | activating >1 h | OBS-P2-004 |
| Monitoring-path death | P3 | Low | Blindness | freshness/scrape/canary rules present | Keep drills |

## Recommendations

### Immediate / Release Blocking

- Regenerate the catalogue and update the README/CURRENT_STATE counts (OBS-P2-001).
- Rate-limit the disk-guard alert (OBS-P2-002).

### This Week

- Filter the loss rule to real loss signals and document counter resets (OBS-P2-003).
- Add a runtime bound + stuck-run alert (OBS-P2-004).
- Re-run the 7-day noise accounting and record it.

### This Month

- Extend the lint/drift test to compare rule IDs across script/catalogue/live.
- Refresh the dashboards after the rule changes.

### Later / Platform Evolution

- Consider an external uptime check for the lab's public entrypoints (already partially covered by the DO watcher).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Regenerate the catalogue + counts | Restores the as-code truth | `docs/phase9/ALERT_CATALOGUE.yaml`, `README.md`, `CURRENT_STATE.md` | counts 86/86 |
| Hourly rate-limit for the disk-guard alert | Cuts 90% of current noise | `automation/validation/disk_guard.sh` | relay count |
| Exclude method rejections from the loss rule | Removes benign firings | `bootstrap/90-alerting.sh`, exporter | probe test |
| `RuntimeMaxSec` on the backup unit | Bounds stuck runs | `config/systemd/falcon-backup.service` | timeout test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rule-ID comparison across script/catalogue/live | P2 | platform | S | live access in CI |
| Stuck-run/unit-state monitoring | P2 | platform | M | exporter change |
| Noise budget review cadence | P2 | platform | S | none |
| Reboot-aware alert suppression | P3 | platform | S | maintenance procedure |

## Suggested Tests

- Unit: extended `alert_rule_lint_test.sh` (catalogue comparison); rule-expression tests for the filtered loss signal.
- Integration: bounded probe test for method rejections; a series-disappearance test asserting no spurious `increase()`.
- E2E: a stuck-run drill; a sanctioned reboot asserting no Suricata artifact firing and the socket rule behaves.
- CI: keep the static lint; add a check that README/CURRENT_STATE counts match the catalogue and the script.
- Manual: 7-day noise accounting from the relay journal.

## Suggested Documentation Updates

- `docs/phase9/ALERT_CATALOGUE.yaml`: regenerate (86) and correct the header claim.
- `README.md:30`, `docs/CURRENT_STATE.md:56,112`: counts and the 2026-10-11 state.
- `docs/runbooks/MONITORING_SCRAPE_AND_FRESHNESS.md`: counter reset semantics; noise review.
- `docs/runbooks/RUNTIME_AND_SCHEDULE.md`: stuck-run monitoring.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which client sent GET/OPTIONS to the ingest listener at 04:03Z? | Probe vs scanner; exposure check | Ingest access logs / network capture |
| Should the loss rule include source errors at all? | Signal quality | Owner/platform decision |
| Is a weekly canary sufficient for alert-path death? | Detection latency | Canary schedule review |

## Appendix

### Golden signals

| Signal | Metric/rule | Coverage |
|---|---|---|
| Latency | Vector component latency; service probe | Partial |
| Traffic | syslog/netflow/flow counters; sink received/sent | Good |
| Errors | sink errors/discards; source rejections; log-derived drops | Good (see OBS-P2-003) |
| Saturation | buffer events/bytes; disk guard; host memory | Good |

### Monitoring-of-the-monitoring

- Textfile freshness (fast set 2 h, daily set 48 h), scrape-absence, relay-path failures, disk-guard staleness, canary (weekly, three paths), DO dead-man watcher reading the independent ntfy locally, heartbeat hourly.
- Live rule set: 86; both delivery paths returned HTTP 200 for every relayed notification in the sampled window.

## Findings

| ID | Severity | Title |
|---|---|---|
| OBS-P2-001 | P2 | ALERT_CATALOGUE.yaml, README and CURRENT_STATE lag live Grafana by one rule while claiming the catalogue cannot drift |
| OBS-P2-002 | P2 | Alert noise remains high and is now dominated by the disk-guard alert repeated every 15 minutes; planned reboots produce artifact alerts |
| OBS-P2-003 | P2 | Pipeline counters rule fires on benign edge_ingest HTTP method rejections and the lazily-registered Vector counters vanish, producing a counter reset inside the firing window |
| OBS-P2-004 | P2 | No alert for a stuck backup run or for failed systemd units; detection depends on 36 h staleness rules |
