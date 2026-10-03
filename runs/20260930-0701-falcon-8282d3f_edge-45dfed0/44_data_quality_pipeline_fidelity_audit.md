# Data Quality and Pipeline Fidelity Audit

## Audit Metadata

- Audit name: repo-deep-dive (Falcon Lab profile)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: `/home/user/falcon-build` (central data plane); edge-side stores read where they feed central metrics
- Branch/commit: main; `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (working tree only audit artifacts)
- Generated at: 2026-09-30T16:40Z (live metrics read 15:13Z)
- Auditor: audit subagent (read-only, prompt 44) · Area code: DQ
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/44_data_quality_pipeline_fidelity_audit.md`
- Scope limitations: no writes into the pipeline (canary marked `not exercised`); OpenSearch queried only via existing textfile metrics and read-only file access (audit account cannot reach the container/credentials); mct program not audited except where it shares the central stack.

## Scope

Reviewed: feed→store→consumer data flow, schemas/mappings per index generation, required fields/identity keys, freshness and gap detection, canary/synthetic assertions, DLQ/retry/poison handling, dedup/idempotency, clock/timezone handling, retention/rollover boundaries, data-quality metrics/definitions/owners, and consumer query correctness (silent-empty risk). Cross-referenced, not duplicated: DATA-P1-001/002/003, DATA-P2-004/005/006, SEARCH-P2-001/002, OBS-P1-003, ND-P2-014/015, and the prior-run LIVE findings.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/vector/aggregator.yaml` | pipeline config | Central ingest, validation, route, DLQ, index naming | DLQ input is **only** `route_valid.invalid`; index `falcon-eve-%Y.%m.%d` |
| `config/vector/edge.yaml` | pipeline config | Probe-side sources/transforms to aggregator | Identity literals `site-lab`/`probe-01`; syslog timestamp overwritten with `now()` |
| `automation/validation/phase4_data_checks.sh` | validation | Template, guardrails, retention, duplicates/replay, canary drills | Template/ISM created here only; P4-G05 replay delta documented |
| `automation/validation/phase9_data_quality.sh`, `docs/phase9/DATA_QUALITY_SCORECARD.md` | DQ metrics | Per-feed counts, identity completeness, DLQ, distinct ids, field growth | Scorecard dated 2026-09-23; cites missing `evidence/phase9/`; gaps list |
| `automation/validation/export_monitor_metrics.sh`, `/srv/falcon/textfile/falcon_metrics.prom` | metrics/consumers | Live per-feed counts, DLQ, freshness, alert inputs | Uses `severity.keyword`, `transport.keyword`, `event_type`, `alert.signature.keyword` |
| `bootstrap/90-alerting.sh` | alert rules | Freshness/gap thresholds and targets | Per-feed silence rules; no rule for the Suricata `alert` feed |
| `docs/phase9/CERTIFICATE_AND_TIME_CONTROLS.md`, `docs/phase9/OPERATING_ENVELOPE.md` | time controls | NTP/UTC baseline; skew metric status | Skew metric/alert explicitly production-pending |
| `automation/validation/retention_execution_test.sh`, `index_rename_migration.sh`, `bootstrap/80-offsite-backup.sh` | retention | Boundary behaviour, deletion proof, keep counts | ISM delete at 14d; snapshot keep 7; disk guard keep 3 |
| `automation/validation/probe_pipeline_test.sh`, `phase4_data_checks.sh` (canary sections) | canary | E2E synthetic path and canary alert | E2E needs root and stops the aggregator; canary is manual |
| Edge `src/falcon_control/service.py` (`h_ingest_vector`, `_append_ingest`) | store | Spool append/rotation and idempotency statement | "at-least-once and dedupe is the consumer's concern"; 128 MiB cap |

## Verification Performed

| Check | Command / read | Result | Notes |
|---|---|---|---|
| Live freshness | `/srv/falcon/textfile/falcon_metrics.prom` (15:13Z) | `falcon_eve_last_event_age_seconds 2`; 514=1700, netflow=3716, flows=13489, TLS=0, 15140=8175 (5m) | Feeds flowing; TLS quiet (rule window 6h) |
| DLQ state | same + `ls -la /srv/falcon/vector/dlq` | `falcon_pipeline_dlq_lines 0`; files 0-byte dated 2026-09-22 | Healthy reading even though sink write failures are not counted |
| Mapping/template | `phase4_data_checks.sh:33-108` read | Template pins `timestamp/event_type/site_id/sensor_id/src_ip/dest_ip/alert.*`; ISM 14d | `severity`/`transport` not pinned; template applied only when script runs |
| Aggregation-vs-mapping test | Static analysis of `export_monitor_metrics.sh:65,69` vs template | `severity.keyword`/`transport.keyword` depend on dynamic mapping; old `event_type` text indices break `.keyword` terms | Live mapping not queryable by audit account — confidence Medium |
| Duplicate/replay behaviour | `phase4_data_checks.sh:111-126` | Explicit `_id` canary is idempotent; pipeline replay increments docs (delta ≥ 1) and is "documented" | Main path has no dedup key |
| Canary E2E | `probe_pipeline_test.sh` read | Requires root/docker and stops the aggregator; no timer; latest evidence 2026-09-21/24 | Marked `not exercised` (read-only audit) |
| Retention boundary | `retention_execution_test.sh`, ISM policy | Disposable index rolled over and deleted; production `falcon-eve-*` 14d delete | No deletion metric/alert; test itself read-only for audit |
| Edge spool boundary | `service.py` (`INGEST_FILE_CAP_BYTES = 128*1024*1024`), live ingest dir | `vector-20260930.ndjson` 48 MB + `.1` 134 MB; rotation overwrites `.1` silently | Older batches unrecoverable, no metric |
| Prior-run carry-over | current-run reports 07/14/31 | DATA-P2-006, SEARCH-P2-002, OBS-P1-003, DATA-P1-003, DATA-P2-004 all still open | No regression found in this pass |

## Executive Summary

The pipeline is real and mostly healthy: feeds flow (514/netflow/flows/15140 counts in the thousands per 5 minutes), the newest-indexed-event age is 2 s, the DLQ is empty, retention has an execution proof, and freshness is measured **on the data path** (OpenSearch counts/age) rather than process liveness. The core weaknesses are fidelity guarantees: the DLQ counts only pre-sink validation errors while OpenSearch write/bulk/mapping failures are invisible (a replay of the 2026-09-22 rejection drill would show `DLQ=0` with 84 sink errors); the main ingest path is explicitly at-least-once with no dedup or idempotency key, and the scorecard's "distinct ids" metric cannot measure duplication; no canary/E2E assertion is scheduled; event time is replaced by ingest time with a hardcoded timezone label and no skew metric; identity fields are literals rather than validated unit identity; whole-index ISM deletion and the 128 MiB spool rotation are silent boundaries; and DQ metrics lack owners/schedule despite an invented-looking definitions set. Priority: DLQ coverage for sink errors, a scheduled canary with assertions, dedup/duplication metrics, a skew metric, and boundary observability. Prior-run status (20260930-0320): LIVE-P2-003 mapping drift **still-open** (current-run DATA-P2-006/SEARCH-P2-002); LIVE-P2-002 index hygiene **still-open** (SEARCH-P3-005); LIVE-P1-002 monitoring-of-the-monitoring **still-open** (OBS-P1-003); ND-P2-014 purge bug **still-open** (DATA-P1-003); ND-P2-015 pending directives **still-open** (DATA-P2-004); prior LIVE-P0-001/002 backup silent failure **still-open** (DR-P1-001/002). No regressions found.

## Inventory (feed → store → consumer)

| Stage | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Probe edge | `config/vector/edge.yaml` | Collect EVE/pmacct/netflow/syslog; buffer; forward | Live; retries 10×/300s | Medium | Identity literals; disk buffer 2 GiB |
| Aggregator | `config/vector/aggregator.yaml` | Validate identity; enrich GeoIP; route; write | Live | High | DLQ = validation only |
| Store | `falcon-eve-%Y.%m.%d` OpenSearch indices | Event store | ~59 M docs; cluster yellow | Medium | Daily index; no rollover alias |
| Retention | `falcon-eve-policy` ISM (14d delete) | Bounded retention | Attached (script-applied) | Medium | Deletion silent; cold copies persist |
| Edge store | `control-plane.db` + `ingest/vector-*.ndjson` | Edge metadata + capture spool | Live; spool rotates at 128 MiB | Medium | 2-file window, silent loss |
| Consumers | `export_monitor_metrics.sh` → Grafana rules; OpenSearch Dashboards saved searches | Alerting + triage | Live | Medium | Keyword-field coupling; no canary |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Schema and mapping consistency | 2 | Template in `phase4_data_checks.sh`; drift documented in 07/31 | Template not deployed; `severity`/`transport` unpinned; old-index text fields | Deploy template+ISM via bootstrap; drift check |
| Required fields and identity keys | 2 | Validator checks site/sensor; scorecard 100% | Values are literals; timestamp/event_type unchecked | Validate against registry; check 4 fields |
| Freshness and gap detection | 3 | Data-path counts/age; per-feed silence rules | Alert feed no rule; no rate/partial-gap/parse-error view | Add alert-feed rule; rate deltas |
| Canary and synthetic assertions | 1 | Manual canary + ntfy drill; E2E test exists | Not scheduled, not exercised, canary index is manual | Scheduled canary with assertions |
| Dead-letter and retry handling | 1 | Validation DLQ + alert; sink retries | Write/bulk/mapping failures not dead-lettered | Sink-error DLQ/metric |
| Deduplication and idempotency | 1 | Canary `_id` idempotent; replay documented | No dedup key; duplicates accepted; metric misleading | Idempotency key + dup ratio |
| Clock and timezone consistency | 2 | NTP/UTC baseline; ingest time authoritative | Event time lost; hardcoded tz; no skew metric | Skew metric; preserve parsed event time |
| Retention and rollover boundaries | 2 | ISM execution proof; keep 7/3 | Silent deletion; spool overwrite; cold copies | Delete/rotate metrics + alerts |
| Data-quality scorecards | 2 | Scorecard exists with definitions | No owners, no schedule, stale evidence path | Assign owners; schedule script |
| Consumer query correctness | 2 | Dashboards/searches match queries | Dynamic-mapping dependency; empty-result checks absent | Query regression tests per path |

## Detailed Review (condensed)

- **Ingest/validation**: `normalize` flags events with missing/invalid `site_id`/`sensor_id`; the route sends them to a file DLQ and everything else to OpenSearch. There is no check for `timestamp`, `event_type`, host, or per-feed required fields, and no post-sink confirmation.
- **Dedup**: `phase4_data_checks.sh` proves idempotency only for an explicit `_id` (`PUT falcon-canary/_doc/canary-001` twice → 1 doc); the replay step writes twice through the real pipeline and expects duplicates. Edge `h_ingest_vector` states dedupe is the consumer's concern.
- **Freshness**: global age uses the newest event across all `falcon-eve-*`; per-feed rules cover 514, 15140, TLS (6 h), NetFlow and flows (all data-path counts). No rule covers the Suricata `alert` feed, and rate collapse/partial gaps are not detected.
- **DLQ**: file sink under `/var/lib/vector/dlq/`, line-count metric and a `> 0` Grafana rule; the archive holds only 0-byte files dated 2026-09-22; the 2026-09-22 write-rejection drill produced sink errors and a missing event, not DLQ lines.
- **Retention**: archived design is age-based delete without rollover aliases (P4-G03 accepted); the 14d delete removes whole indices with no metric; snapshot/cold copies (keep 7/3) and manual R2 mounts retain data (SEARCH-P2-001); the edge spool keeps ~2 files and overwrites silently.
- **Cross-references (not duplicated)**: DATA-P1-001/002/003, DATA-P2-004/005/006, SEARCH-P2-001/002, OBS-P1-003, ND-P2-014/015.

## Schema and Mapping Drift

| Field | Old type | New type | Consumer impact | Evidence |
|---|---|---|---|---|
| `event_type` | text (≤2026-09-22 indices) | keyword (since 09-23) | `.keyword` terms/aggregations silently 0 on old indices; template terms work on new | LIVE-P2-003; current-run DATA-P2-006/SEARCH-P2-002 |
| `host` | text with keyword subfield | text-only on 09-29/09-30 | `.keyword` filters/aggregations on host silently empty for newest indices | LIVE-P2-003; current-run 31 appendix |
| `severity` | not in template; dynamic | dynamic (text+keyword if strings first) | `severity.keyword` term query in the error-count metric can silently return 0 or conflict | `export_monitor_metrics.sh:65`; template `phase4_data_checks.sh:73-82` |
| `transport` | not in template; dynamic | dynamic | `transport.keyword` TLS exclusion in the 514 count can silently mis-count if mapped non-string | `export_monitor_metrics.sh:68-69` |
| `alert.signature` | text+keyword (template) | text+keyword (template) | Top-signature aggregation safe where template applied; dynamic otherwise | `phase4_data_checks.sh:81` |
| `timestamp` | date (documented) | date | Fine for freshness; event time overwritten at ingest (see DQ-P2-005) | `aggregator.yaml:63`; `edge.yaml` transforms |
| Fixture residue | n/a | `falcon-canary`, `falcon-test`, `falcon-eve-fixture-test`, `other-site-index` | Pollute index patterns and counts | LIVE-P2-002; SEARCH-P3-005 |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DQ-001 | Schema/mapping consistency | phase4 template; 07/31 | Template + guardrails exist | Script-applied only; dynamic fields | P2 | Deploy via bootstrap; drift test |
| DQ-002 | Required fields/identity | normalize; scorecard | site/sensor presence | Literals; only 2 fields checked | P2 | Registry validation; more fields |
| DQ-003 | Freshness/gap detection | metrics + 90-alerting | Data-path counts/age; 5 feed rules | Alert feed uncovered; no rate gaps | P2 | Add rule; rate anomaly |
| DQ-004 | Canary assertions | canary drills; probe test | Manual canary + alert drill | Not scheduled/exercised | P2 | Scheduled canary |
| DQ-005 | DLQ/retry/poison | aggregator; 09-22 drill | Validation DLQ + retry | Sink/bulk/mapping failures invisible | P1 | Sink-error DLQ/metric |
| DQ-006 | Dedup/idempotency | P4-G05; h_ingest_vector | Explicit-id idempotent; replay documented | No dedup key; dup unmeasured | P2 | Idempotency key + dup ratio |
| DQ-007 | Clock/timezone | CERT_AND_TIME; transforms | NTP/UTC; ingest-time authority | Event time lost; skewed tz; no metric | P2 | Preserve event time; skew metric |
| DQ-008 | Retention boundaries | ISM test; backups; spool | 14d ISM; keep 7/3 | Silent deletions/overwrites | P2 | Boundary metrics/alerts |
| DQ-009 | DQ scorecards | scorecard | Definitions + baseline | No owners/schedule; stale path | P3 | Owners; schedule; re-measure |
| DQ-010 | Consumer queries | metrics/dashboards | Working today | Empty-result risk from drift | P2 | Query regression tests |

## Findings

### Finding ID: DQ-P1-001 - DLQ counts only pre-sink validation errors; write failures are invisible

- Severity: P1 · Confidence: High · Area: DQ / DLQ
- Evidence: `config/vector/aggregator.yaml:82-111` (dlq sink input is `route_valid.invalid` only); `export_monitor_metrics.sh:38` (line count of `/srv/falcon/vector/dlq/*.jsonl`); `bootstrap/90-alerting.sh:210-212` (`falcon_pipeline_dlq_lines > 0`); decision log 2026-09-22 (write-rejection drill: 84 sink errors, marked event absent, settings restored); live 15:13Z DLQ 0 with 0-byte archive files.
- What is happening: mapping conflicts, read-only blocks, bulk item failures and OpenSearch sink errors never reach the DLQ or any metric; the alert condition reads healthy while events are lost.
- Why it matters: a whole class of data loss is unobservable and unreplayable.
- User/business impact: missing telemetry during incidents; alerting gaps.
- Security/privacy/reliability impact: silent evidence loss in the monitoring plane.
- Recommended fix: capture sink/bulk failures (Vector internal errors → DLQ file or a `falcon_pipeline_sink_errors_total` metric), alert on per-feed rejects, and record partial-bulk outcomes.
- Suggested validation: replay the write-rejection drill and assert the failure is counted, dead-lettered, and alerted (not DLQ 0).
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: DQ-P2-002 - No deduplication or idempotency on the main ingest path

- Severity: P2 · Confidence: High · Area: DQ / dedup
- Evidence: `phase4_data_checks.sh:111-126` ("identical `_id` is idempotent" applies to explicit-id canary; replay delta ≥ 1 "duplicates expected and documented"); edge `service.py:550-556` ("at-least-once and dedupe is the consumer's concern"); `aggregator.yaml:90-97` bulk index without `_id`/fingerprint; scorecard metric "Distinct document ids" (`phase9_data_quality.sh:15`).
- What is happening: replayed/duplicated events get distinct `_id`s and are indexed as separate documents; no duplicate/replay ratio is computed; the distinct-id metric would not change on duplication.
- Why it matters: alert counts, top-talker sums and forensic timelines can double-count; no measurement of the problem.
- User/business impact: inaccurate dashboards and reports; slow root-cause work.
- Security/privacy/reliability impact: replay of security events distorts incident decisions.
- Recommended fix: derive a deterministic id/fingerprint (sensor+event id/time+hash) or add a dedup transform with a bounded key store; add a duplicate-ratio metric per feed.
- Suggested validation: replay a known batch twice; assert one document/one alert and a non-zero dup-ratio counter.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: DQ-P2-003 - No scheduled canary or end-to-end assertion

- Severity: P2 · Confidence: High · Area: DQ / canary
- Evidence: `phase4_data_checks.sh:112-140` (manual `falcon-canary` fixture and ntfy delivery); `probe_pipeline_test.sh` (root, stops the aggregator; "for read-only checks use central_health.sh"); no canary timer in `config/systemd/` or `bootstrap/`; freshest canary/adversarial evidence `REVIEW-FIX/20260924T220153Z_suricata-noise-gone-and-canary-test.out`; gate P4-G07 PASS dated 2026-09-21.
- What is happening: pipeline correctness depends on manual drills; there is no continuous write→store→query assertion, and the audit could not exercise the E2E path (marked `not exercised`).
- Why it matters: silent transform drops, misrouting or index-name changes can persist for hours without a canary failure.
- User/business impact: consumers notice gaps before monitoring does.
- Security/privacy/reliability impact: detection quality unverified between drills.
- Recommended fix: deploy a canary writer/checker (distinct index excluded from retention/alerts) with assertions on count, fields, and latency; keep it out of production indices.
- Suggested validation: canary fires and clears on a simulated transform drop; alert on missing canary within N minutes.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: DQ-P1-001 optional · Status: open

### Finding ID: DQ-P2-004 - Freshness detection is zero-rate silence only; partial gaps and the alert feed are uncovered

- Severity: P2 · Confidence: High · Area: DQ / freshness
- Evidence: `bootstrap/90-alerting.sh:206-247,289-291` (global age `>900s`; per-feed `< bool 1` for flows, netflow, TLS 6h, 15140, 514); live 15:13Z metrics (514=1700, netflow=3716, flows=13489, TLS=0); no rule for `event_type:alert`; scorecard gaps list ("per-feed parse-error counts, timestamp-skew distribution, duplicate/replay ratios") unimplemented; metric staleness unalerted (OBS-P1-003).
- What is happening: a feed that keeps emitting but at 1% of normal volume, drops a batch, or fails parsing passes every rule; freshness for the age metric is a max across all feeds, so one healthy feed masks others.
- Why it matters: partial data loss and degradation are exactly the failures consumers notice late.
- User/business impact: incomplete monitoring coverage during outages.
- Security/privacy/reliability impact: alert feed (Suricata alerts) can be silent without paging.
- Recommended fix: add an alert-feed rule; add rate-deviation bands per feed (baseline vs current window); add parse-error counters per transform; alert on metric staleness.
- Suggested validation: synthetic rate drop and parse-error injection produce distinct alerts.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: OBS-P1-003 · Status: open

### Finding ID: DQ-P2-005 - Event time is discarded in favour of ingest time with a hardcoded timezone label

- Severity: P2 · Confidence: High · Area: DQ / clock
- Evidence: `aggregator.yaml:51-69` and `edge.yaml` syslog transforms set `.timestamp = now()`, keep `.device_timestamp_local` and a literal `.device_timezone = "America/New_York"`; `parse_syslog` results are not converted; `CERTIFICATE_AND_TIME_CONTROLS.md` lists "clock-skew alerting threshold and per-feed skew metric" as production-pending; Pi local timezone Europe/London (live), central UTC.
- What is happening: all searches/orderings use ingest time; device local time is a string with an assumed fixed offset; DST changes silently shift the meaning of the stored value; no skew measurement exists.
- Why it matters: forensic timelines and "when did this happen" queries are wrong or ambiguous; skew invisible.
- User/business impact: incident reconstruction error.
- Security/privacy/reliability impact: event ordering affected.
- Recommended fix: parse and convert device timestamps to UTC (IANA tz per feed), keep `event_time`/`ingested_at` distinct, and add per-feed skew percentiles with an alert threshold.
- Suggested validation: DST-boundary unit fixture; skew metric appears for a clock-shifted sender.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: DQ-P2-006 - Required-field completeness checks two identity fields whose values are pipeline literals

- Severity: P2 · Confidence: High · Area: DQ / identity
- Evidence: `aggregator.yaml:44-49` (only `site_id`/`sensor_id` validated); `edge.yaml` sets `.site_id = "site-lab"`, `.sensor_id = "probe-01"|"syslog"|"gateway-netflow"|"syslog-15140"`; `phase9_data_quality.sh:10` checks `_exists_:site_id AND _exists_:sensor_id`; scorecard reports 100% identity completeness; edge `profiles/sensor/vector/edge.toml` hardcodes the enrolled sensor id (cross-ref ND-P2-018).
- What is happening: completeness is guaranteed by construction, so the metric cannot detect misattribution, a wrong site, a cloned image, or a missing timestamp/event_type.
- Why it matters: "identity complete" data can still be attributed to the wrong site/unit; consumers cannot trust the keys.
- User/business impact: per-site reporting incorrect and undetectable.
- Security/privacy/reliability impact: multi-site isolation evidence rests on constants.
- Recommended fix: validate identity against the sensor/registry (or per-device credentials), require `timestamp`/`event_type` in the normalize route, and count rejects per missing field.
- Suggested validation: send valid-identity/absent-timestamp events and assert rejection/counting; registry-mismatch test.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: DQ-P2-005 · Status: open

### Finding ID: DQ-P2-007 - Retention boundaries delete silently (indices and the edge spool) with no observability

- Severity: P2 · Confidence: High · Area: DQ / retention
- Evidence: ISM `falcon-eve-policy` 14d delete (`phase4_data_checks.sh:33-56`; execution test `retention_execution_test.sh`); no metric/alert tracks index deletion; `service.py:594-599` rotates the edge spool at `INGEST_FILE_CAP_BYTES=128 MiB` via `os.replace(path, path+".1")`, overwriting the prior file (live: 134 MB `.1`); cold/snapshot copies persist (SEARCH-P2-001); fixture indices remain in the pattern (SEARCH-P3-005).
- What is happening: data disappears at boundaries without a marker, count, or alert; the spool keeps only ~2 files, and older batches are silently dropped.
- Why it matters: "no silent data loss at boundaries" is unmet; consumers cannot tell deletion from outage.
- User/business impact: unexpected gaps in history; storage surprises.
- Security/privacy/reliability impact: deletion-of-record evidence missing for compliance.
- Recommended fix: emit delete/rotate counters (indices expired, bytes/batches dropped), alert on unexpected drops, and align the spool cap/retention with the 7-day queue intent; document the deletion window.
- Suggested validation: forced rotation/expiry produces metrics and alerts; boundary test asserts no data older than policy remains (and that consumers know).
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: DATA-P1-001 · Status: open

### Finding ID: DQ-P2-008 - Consumer queries depend on dynamically mapped fields the template does not pin

- Severity: P2 · Confidence: Medium · Area: DQ / consumer queries
- Evidence: `export_monitor_metrics.sh:65` (`terms severity.keyword`), `:68-69` (`transport.keyword`), `:131` (`alert.signature.keyword`); template `phase4_data_checks.sh:73-82` pins `timestamp`, `event_type`, `site_id`, `sensor_id`, `src_ip`, `dest_ip`, and `alert.signature` but **not** `severity`/`transport`; prior live drift: `event_type` text before 09-23, `host` text-only on 09-29/30 (LIVE-P2-003), and the current-run 07/31 reports confirm it.
- What is happening: whether the alerting counts work depends on the first document's value type in each index generation; a non-string or pre-template index makes the term query silently return zero (no error), turning "error syslog count" into an apparently healthy 0.
- Why it matters: silent-empty aggregations are exactly the consumer failure the audit is asked to detect.
- User/business impact: false "no errors"/"no TLS feed" states.
- Security/privacy/reliability impact: alerting blind spots.
- Recommended fix: pin every queried field in the deployed template (strings as keyword, numeric levels as long), deploy it before writers start, and add a query regression test per consumer against the live mapping.
- Suggested validation: run each metric query against a fresh index and an old-index fixture; fail if results are empty where data exists.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: DQ-001/DATA-P1-001 · Status: open

### Finding ID: DQ-P3-009 - DQ scorecard has definitions but no owners, schedule, or reachable evidence

- Severity: P3 · Confidence: High · Area: DQ / scorecards
- Evidence: `docs/phase9/DATA_QUALITY_SCORECARD.md` (dated 2026-09-23; cites `evidence/phase9/…` which does not exist — ND-P3-001); `phase9_data_quality.sh` is not referenced by any timer/service (`config/systemd/` has no DQ job); scorecard lists gaps (parse errors, skew, duplicate ratios, field growth, per-feed DLQ attribution) with no owner column.
- What is happening: the metric set is defined and once measured, but nothing schedules it, no one owns thresholds, and the evidence path is broken.
- Why it matters: DQ regressions depend on manual review; the scorecard cannot be trusted at face value.
- User/business impact: governance gap; stale numbers drive decisions.
- Security/privacy/reliability impact: low.
- Recommended fix: add owners and thresholds per metric, schedule the script (or fold its metrics into `export_monitor_metrics.sh`), fix the evidence path, and record a re-measurement date.
- Suggested validation: CI/docs test that the evidence path resolves and a timer exists; dashboard shows the scheduled metric.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: DATA-P1-001 · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent sink/write data loss unnoticed | High | Medium | Missing telemetry | DQ-P1-001 | Sink-error DLQ/metric |
| Duplicate events distort counts/forensics | Medium | Medium-High | Wrong decisions | DQ-P2-002 | Dedup key + ratio |
| Partial feed gaps unseen | Medium | Medium | Coverage loss | DQ-P2-004 | Rate/parse metrics |
| Misattributed data passes completeness | Medium | Medium | Wrong per-site data | DQ-P2-006 | Registry validation |
| Boundary deletions silent | Medium | Medium | Historic gaps | DQ-P2-007 | Delete/rotate metrics |
| Silent-empty consumer queries | Medium | Medium | False healthy state | DQ-P2-008 | Pinned mappings + tests |

## Recommendations

### Immediate / Release Blocking
1. Add sink/bulk failure capture to the DLQ or a first-class metric, and alert on it (DQ-P1-001).
2. Pin all queried fields (`severity`, `transport`, `event_type`, `host`) in the deployed template before further writers (DQ-P2-008, DQ-001).

### This Week
3. Deploy a scheduled canary with counts/field assertions and an alert (DQ-P2-003).
4. Keep raw event time in UTC alongside `ingested_at`; add per-feed skew metric (DQ-P2-005).
5. Add delete/rotation counters for ISM and the edge spool (DQ-P2-007).

### This Month
6. Dedup key or fingerprint + duplicate-ratio metric per feed (DQ-P2-002).
7. Extend normalize to require timestamp/event_type and validate identity against the registry (DQ-P2-006).
8. Add rate-deviation and parse-error metrics per feed, including the alert feed (DQ-P2-004).
9. Assign DQ metric owners, schedule the script, fix the evidence path (DQ-P3-009).

### Later / Platform Evolution
10. Continuous DQ scorecard in Grafana with thresholds and trend history; cold-copy deletion policy (cross-ref SEARCH-P2-001).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Pin `severity`/`transport` in the template | Removes silent-empty risk | `phase4_data_checks.sh:62-84` | template diff + query test |
| Alert-feed silence rule | Covers the uncovered feed | `bootstrap/90-alerting.sh` | firing proof |
| Fix scorecard evidence path | Restores trust | `DATA_QUALITY_SCORECARD.md` | docs test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Sink-error DLQ + metric | P1 | falcon maintainer | M | none |
| Query regression tests per consumer | P2 | falcon maintainer | M | template deploy |
| Scheduled canary + alert | P2 | falcon maintainer | M | DQ-P1-001 opt |
| Dedup/idempotency key + ratio | P2 | falcon maintainer | M | none |
| Event-time preservation + skew metric | P2 | falcon maintainer | M | none |
| Registry validation of identity | P2 | falcon + edge maintainers | M | XREPO |
| Retention boundary observability | P2 | falcon maintainer | M | DATA-P1-001 |

## Suggested Tests

- Unit: normalize rejects missing timestamp/event_type; timezone conversion at DST boundary; spool rotation counter.
- Integration: write-rejection replay asserts DLQ/metric/alert; replay batch asserts dedup ratio; forced ISM expiry emits counter.
- E2E/CI: canary write→query asserts counts/fields and alert on silence; template-vs-query field test; scorecard evidence-path test.
- Regression/manual: run `phase9_data_quality.sh` against current indices and compare to the scorecard; verify per-feed DLQ attribution.

## Suggested Documentation Updates

- `docs/phase9/DATA_QUALITY_SCORECARD.md` — owners, thresholds, schedule, corrected evidence path, re-measured values.
- `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` — explicit event-time vs ingest-time semantics and dedup status.
- Runbook `docs/phase7/runbooks/SENSOR_SILENCE.md` — add partial-gap/rate and canary failure procedures; note DLQ scope (aggregator.yaml comments).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What is the accepted duplicate rate on the main feeds? | Drives dedup design and alert accuracy | Replay/dup measurement |
| Which device feeds must carry true event time? | Determines conversion scope | Owner input |
| Is `falcon-canary`/fixture residue intentionally retained? | Affects index patterns/retention | Owner decision (SEARCH-P3-005) |
| Who owns each DQ metric threshold? | Closure of DQ-P3-009 | Operator assignment |

## Appendix

- Live values (15:13Z): eve age 2 s; DLQ 0; cluster yellow (1, expected); 514=1700, TLS=0, 15140=8175, netflow=3716, flows=13489 per 5 min; docs 58,971,969.
- Edge path (15:12–15:13Z): `ingest_vector` audit rows every ~5–7 s (17–58 events/batch) into `vector-20260930.ndjson`; capture stats age 14 s, 0 drops/errors; `edge_ids_events_window_total{alert}=1`.
- No secret values were printed; references are path/type only.
