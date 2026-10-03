# Performance, Scalability, and Cost Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab, prompt 15) · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repos: `/home/user/falcon-build` + `/home/user/falcon-edge-build`, branch `main`; central commit `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (dirty: audit run folder + offsite evidence in flight); edge `f1c5defe6b66887ae49bc44c2cd79b37ad249663`
- Generated at: 2026-09-30T15:10Z · Auditor: audit subagent (read-only; no load tests, no cleanup) · Area code: PERF
- Output path: docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/15_performance_scalability_cost.md
- Scope limitations: no root/docker, so container/snapshot sizes are inferred from metrics; no OpenSearch credentials (index stats via the falcon exporter and prior-run evidence); PVE host and Grafana not inspected; no cost figures exist in the repo.

## Scope

Reviewed host capacity (root/data LV, RAM/swap, CPU/load, containers), ingest/worker throughput against the approved budgets, storage growth and retention, backup I/O and offsite cost behaviour, index/aggregation health, CI coverage and first-party frontend scope (none). Not reviewed: PVE host resources, upstream Grafana/OSD performance, edge hardware, cloud billing state.

## Evidence Reviewed

- Live read-only: `df -B1`, `/proc/meminfo`, loadavg, `/sys/class/net/ens19/statistics`, `/srv/falcon/textfile/*.prom`, Prometheus API (`172.30.1.6:9090`) 14:17-15:10Z
- `compose/central/docker-compose.yml` (limits, Prometheus retention 158, node-exporter 283-299); `automation/wazuh/multi-node/docker-compose.yml:97,121,143` (768 m heaps)
- `automation/validation/{export_monitor_metrics,disk_guard,backup_new_services}.sh`; `bootstrap/{80-offsite-backup,85-backup-job}.sh`; `config/vector/*.yaml`; `config/suricata/suricata.yaml`
- `docs/phase5/PERFORMANCE_ENVELOPE.md`, `docs/phase5/TRAFFIC_PROFILE.md`, `ledgers/gate_ledger.csv` (P5-G03/G05), `ledgers/decision_log.md:74`; `docs/runbooks/CAPACITY_AND_TELEMETRY.md`; `evidence/raw/P9-G08`, `P5-G08`
- `.github/workflows/validate.yml`; `git remote` (github.com/MaineCyberTech/falcon)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `df -B1` + PromQL filesystem queries | live measurement | trajectory + thresholds | root 83.25 %, data 62.79 %; 24 h slopes -3.81/-2.96 GB/day |
| `predict_linear` 24 h/7 d | live query | distance to signal/failure | root 7-d free ≈4.2 GB; data ≈27.6 GB (24 h) vs ≈57.1 GB (7 d) |
| swap/memory + load queries | live query | pressure | swap 55.9 % used; MemAvailable 36.7 %; peak load 29.65 |
| index/docs/counter `deriv` | live query | throughput | 92-94 docs/s; EVE +4.0 GB/day; 0 kernel drops |
| offsite archive log | evidence | backup I/O | 03:55:39→07:43:40Z full copy, 1 723 files |

### Prior-run capacity findings re-checked at this commit

| Prior ID | Status | Evidence |
|---|---|---|
| LIVE-P0-003 data-LV growth | `partially-fixed` | rotation + guard 10 GiB (`disk_guard.sh:14`); 48.6 GB free; reclaims_total 0; no warning band |
| LIVE-P1-001 root LV | `still-open` | 83.25 %; warning fired 08:03→08:38Z; no guard/reclaim on `/`; -3.81 GB/day |
| LIVE-P1-005 snapshot dup / RPO | `still-open` | two snapshots/day; ~7-day window undocumented |
| INTG-P2-005 shared-host risk | `still-open` | root/data pressure + backup load spikes |

## Executive Summary

The lab works but is capacity-constrained: root is 3.2 GB below its warning threshold (which fired earlier today) with no reclaim path, and the data LV's only signal is a 10 GiB guard that has never run. Swap absorbs memory pressure (56 % used) and the host has OOM-killed this VM before. Throughput is healthy (92-94 docs/s vs the approved ≤120 docs/s; 0 kernel drops) but untracked at runtime. The offsite job copies the entire snapshot repository nightly (~3.7 h, load 29.65 on 6 vCPU), and the program has no cost model.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Root LV | `ubuntu--vg-ubuntu--lv` | OS, Docker, Wazuh, IRIS | 144.3/183.3 GB (83.25 %) | High | +75 GB step Sep 27-28 |
| Data LV | `ubuntu--vg-falcon--data` | OpenSearch, probe, backups | 76.1/130.7 GB (62.79 %) | High | 48.6 GB free; guard 10 GiB |
| Disk guard | `disk_guard.sh` | reclaim + alert | reclaims 0; text says 5 GiB | Medium | threshold 10 GiB |
| Snapshots/offsite | `85-backup-job.sh`, `80-offsite-backup.sh` | recovery | 2/day local; 7 remote inventories | High | ~7-day window undocumented |
| Memory/swap | host | JVM workloads | 15.08 GB total; swap 4.7/8 GiB | High | no swap alert; PVE OOM history |
| Ingest pipeline | Vector, OpenSearch | telemetry | 92-94 docs/s; DLQ 0 | Medium | 77 % of budget |
| Offsite jobs | `80-offsite-backup.sh:72` | cold tier | full copy nightly | Medium | load 29.65, no dedupe |
| CI | `validate.yml` | validation | static checks only | Low | no perf data |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Bundle size indicators | n/a | no first-party frontend | upstream only | mark N/A |
| SSR/client hot spots | n/a | no SSR app | none | mark N/A |
| Heavy dependencies | 3 | pinned images/heaps | no footprint budget | document budgets |
| Images/caching | 3 | Traefik/ntfy caches; R2 blocked | no data-tier cache | cost decision |
| Pagination | n/a | OSD Discover only | none | mark N/A |
| N+1 risks | 2 | exporter runs 10+ OS queries/min | uncached | batch queries |
| Indexes/query patterns | 2 | dynamic mapping + keyword drift | no mapping contract | explicit mappings |
| Worker throughput | 3 | 92-94 docs/s; DLQ 0 | no budget metric | ingest-rate alert |
| Queue concurrency | 3 | 2 GiB blocking buffer | central depth unalerted | add depth metric |
| Realtime scaling | 2 | single node, 4 JVM stacks, balloon | no headroom model | sizing review |
| Webhook volume | 3 | relay dual publish | no rate limit | token bucket |
| Rate limiting | 3 | ntfy limits; relay unbounded | relay limit | add limit |

## Detailed Review

- **Root:** step-driven growth (Wazuh/IRIS/R2 volumes, Sep 27-28) plus Docker/logs; the 85 % warning has no reclaim action and the disk guard covers only `/srv/falcon`.
- **Data:** the guard's reclaim path (rotated EVE >1 d, snapshots keep 3, configs keep 3) has never executed; ISM deletes EVE after 14 d (`phase4_data_checks.sh:33-52`), which should flatten growth from ~Oct 5.
- **Throughput/offsite:** 4 JVM stacks (OpenSearch 2 G + 3× Wazuh 768 m) compete for a ballooned VM; the nightly full-repository copy saturates it for ~4 h.
- **Budgets:** 0 drops at ≤20 k pps and ≤120 docs/s were owner-accepted (P5-G03/G05; decision log 2026-09-22); only the drop budget has an alert.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| PERF-001 | Bundle size | none | N/A | none | n/a | document |
| PERF-002 | SSR hot spots | none | N/A | none | n/a | document |
| PERF-003 | Heavy dependencies | images/heaps | pins + limits | no budget | P3 | footprint budget |
| PERF-004 | Images/caching | caches; R2 blocked | partial | no cold cache | P3 | cost decision |
| PERF-005 | Pagination | OSD only | upstream | none | n/a | none |
| PERF-006 | N+1 risks | exporter queries | none | repeated queries | P2 | batch queries |
| PERF-007 | Indexes/query patterns | dynamic mapping | none | silent empty aggs | P2 | explicit mappings |
| PERF-008 | Worker throughput | 92-94 docs/s | budget defined | unmonitored | P2 | ingest alert |
| PERF-009 | Queue concurrency | buffers | block backpressure | central depth | P3 | depth metric |
| PERF-010 | Realtime scaling | single VM | none | headroom unproven | P2 | sizing review |
| PERF-011 | Webhook volume | relay | grouping | rate limit | P3 | token bucket |
| PERF-012 | Rate limiting | ntfy config | visitor limits | relay unbounded | P3 | add limit |

## Findings

### Finding ID: PERF-P1-001 - Root LV is ~3 GB from its warning threshold with no reclaim path
- Severity: P1 · Confidence: High · Area: capacity / root filesystem
- Evidence: live 144 302 272 512 / 183 295 782 912 B used (83.25 %), avail 30.7 GB; 85 % headroom 3.21 GB, 92 % headroom 16.0 GB; `deriv[24h] = -3.81 GB/day`, `[7d] = -2.29 GB/day`; `Disk space low` fired 08:03→08:38Z today; `disk_guard.sh:14` guards only `/srv/falcon`; Sep 27-28 +75 GB step (prior-run evidence).
- What is happening: `/` carries Docker volumes, IRIS, Wazuh and OS logs; growth is unattributed and unguarded.
- Why it matters: at current slopes the warning recurs within ~1-3 days and unguarded growth can fill the root within ~1-2 weeks, taking the platform down.
- User / business impact: platform outage, write failures, manual recovery · Security/reliability impact: availability and data integrity.
- Recommended fix: reclaim plan (Docker prune policy, move Wazuh/IRIS volumes off `/`), per-directory growth signal, >=90 % critical page · Suggested validation: 7-day trend bounded; simulated fill pages before 90 %.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: maintenance window · Status: still-open (prior LIVE-P1-001; +1 pp)

### Finding ID: PERF-P1-002 - Data LV's only signal is an unexercised 10 GiB disk guard
- Severity: P1 · Confidence: High · Area: capacity / data filesystem
- Evidence: live 76 058 468 352 / 130 723 581 952 B used (62.79 %), avail 48.6 GB; `disk_guard.sh:14` threshold 10 GiB (raised from 5 GiB) and `falcon_disk_guard_reclaims_total 0`; slopes disagree: 24 h -2.96 GB/day vs 7 d +1.11 GB/day; ISM deletes EVE after 14 d, oldest ~Oct 5; EVE store 28.19 GB at +4.00 GB/day; guard alert text still says 5 GiB (`:94-98`).
- What is happening: no warning band exists between healthy and "guard acts"; reclaim capacity is bounded and never tested.
- Why it matters: if the guard cannot free enough, OpenSearch/probe writers wedge and data is at risk.
- User / business impact: monitoring outage, data-loss risk · Security/reliability impact: retention/capacity safety.
- Recommended fix: <15 GiB warning alert, guard drill, fix alert text, decide split-retention/cold-copy from `CAPACITY_AND_TELEMETRY.md` · Suggested validation: drill frees space + pages; 7-day free space stable.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: retention decision · Status: partially-fixed (prior LIVE-P0-003)

### Finding ID: PERF-P2-001 - Memory/swap pressure is unalerted and host-side memory is outside monitoring
- Severity: P2 · Confidence: High · Area: memory / capacity
- Evidence: live total 15.08 GB, available 5.53 GB (36.7 %); swap 8.0 GB total, 3.53 GB free (55.9 % used); slopes -0.41 GB/day (24 h) / -0.065 GB/day (7 d); container RSS sum 8.33 GB (OpenSearch 3.14 GB/4 GB; 3× Wazuh indexers 1.0-1.23 GB at 768 m heaps; Grafana 318 MB); rule only fires below 10 % available; P9-G08 meta: PVE host OOM-killed VM 106 three times on 2026-09-27.
- What is happening: the VM leans on swap and host-side protection, neither of which the lab monitors.
- Why it matters: memory pressure degrades JVM latency and can re-trigger OOM kills.
- User/business impact: latency/drops, sudden outages · Security/reliability impact: resilience.
- Recommended fix: swap >75 % for 30 m and available <20 % tiers; scraped or external PVE host check; record the 12 GiB balloon floor · Suggested validation: thresholds evaluate; host check reports.
- Owner suggestion: falcon maintainer · Effort: S/M · Dependencies: PVE access · Status: still-open (prior LIVE-P1-002)

### Finding ID: PERF-P2-002 - Offsite backup copies the whole snapshot repository nightly, spiking host load
- Severity: P2 · Confidence: High · Area: cost / backup I/O
- Evidence: `bootstrap/80-offsite-backup.sh:72` `rclone copy --no-check-dest --transfers 4`, bucket cannot list; today's manual run 03:55:39→07:43:40Z copied 1 723 files; PromQL `max_over_time(node_load1[1h])` 24.4-29.65 on 6 vCPU during offsets 7-11 h vs 2.68 at offset 5 h; remote keeps 7 inventories; two snapshots/day (~3 min apart); local repo keeps 10.
- What is happening: the full archive is re-uploaded every night ×7 remote inventories during a 4-hour window on the production host.
- Why it matters: bandwidth/storage spend, RPO risk if the host dies mid-copy, and slower alert evaluation overnight.
- User/business impact: overnight alert latency; cloud spend · Security/reliability impact: backup window.
- Recommended fix: dedupe/chunk or one snapshot/day; cap transfers/bandwidth; copy only inventory diffs; document the RPO · Suggested validation: daily upload <1 h; object count stable; error injection.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: Spaces limits · Status: still-open (prior LIVE-P1-005)

### Finding ID: PERF-P2-003 - Throughput sits at ~77 % of the approved budget with no runtime tracking
- Severity: P2 · Confidence: High · Area: worker throughput
- Evidence: `deriv(falcon_opensearch_docs_total[24h])*86400 = 7.98 M docs/day` (7 d 8.14 M) ≈ 92-94 docs/s vs the owner-accepted ≤120 docs/s (P5-G03/G05; decision log 2026-09-22); EVE +4.00 GB/day; Suricata alerts ~4.7 k/h; SPAN 228.8 M RX packets, 584 dropped; kernel drops 0; probe buffer 43.5 MB/2 GiB; no metric compares ingest to budget.
- What is happening: feeds doubled after the SPAN fix and now carry ~3/4 of the accepted ceiling with no warning as they approach it.
- Why it matters: a feed increase could breach the budget silently, risking drops/backlog.
- User/business impact: data gaps under load · Security/reliability impact: ingestion reliability.
- Recommended fix: rolling ingest-rate metric with budget ratio, >80 % warning, budget panel; keep drops visible · Suggested validation: rate drill warns before drops.
- Owner suggestion: falcon maintainer · Effort: S/M · Dependencies: budget confirmation · Status: open

### Finding ID: PERF-P2-004 - Dynamic mappings and index drift silently degrade aggregations
- Severity: P2 · Confidence: Medium (prior-run live evidence; not re-inspected) · Area: indexes/queries
- Evidence: no mapping/template exists in the repo (no mapping PUT in `bootstrap/60-central-deploy.sh:120`); prior run observed `event_type` keyword since 09.23 vs text on 09.21/09.22 and `host` text-only on 09.29/09.30; dashboards use `event_type:` terms (`bootstrap/91-dashboards.sh:57,73,89`) and the exporter uses `.keyword` fields (`severity.keyword`, `transport.keyword`).
- What is happening: inferred per-index types make some terms/aggregations silently return nothing.
- Why it matters: invisible triage/data-quality regressions in the exact tooling operators rely on.
- User/business impact: empty/wrong dashboards during incidents · Security/reliability impact: monitoring fidelity.
- Recommended fix: commit an index template with explicit hot-field mappings; add a schema-drift check; document multi-field usage · Suggested validation: new indices match template; known-data aggs non-zero.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: reindex decision · Status: still-open (prior LIVE-P2-003, unverified this run)

### Finding ID: PERF-P3-001 - No cost model, budgets or spend visibility for cloud components
- Severity: P3 · Confidence: High · Area: cost
- Evidence: no monetary cost/budget statement in README/AGENTS/runbooks/ledgers (grep); cost-bearing parts: DO droplet (independent ntfy + watcher), DO Spaces bucket `falcon-mct` (7 inventories, full nightly uploads), Cloudflare (tunnel/DNS; R2 attempt blocked), GitHub Actions (`validate.yml`, repo MaineCyberTech/falcon); storage drivers: EVE 28.2 GB at +4 GB/day, snapshots, logs.
- What is happening: real infra spend is unquantified and untied to retention decisions.
- Why it matters: budgets cannot be justified or watched; silent spend creep.
- User/business impact: budget surprises · Security/reliability impact: none directly.
- Recommended fix: cost register (fixed + per-GB assumptions), storage dashboard per component, revisit retention against cost · Suggested validation: monthly review; panel matches actuals.
- Owner suggestion: owner · Effort: S · Dependencies: billing access · Status: open

### Finding ID: PERF-P3-002 - CI captures no performance or build-time data; frontend budgets are N/A
- Severity: P3 · Confidence: High · Area: CI / build / frontend
- Evidence: `.github/workflows/validate.yml` runs static checks only (actionlint, shellcheck, ruff, gitleaks, zizmor, `ci/validate.py`), `timeout-minutes: 20`, no timing artifact/benchmark; no first-party web frontend (Grafana/OSD upstream), so bundle/SSR/image budgets do not apply; the only performance evidence is the phase-5 envelope.
- What is happening: build/test duration and regressions are invisible; performance claims live in a one-off document.
- Why it matters: unnoticed slowdowns; stale assumptions.
- User/business impact: slower feedback · Security/reliability impact: none.
- Recommended fix: record workflow duration in the summary; scheduled lightweight benchmark; state N/A frontend budgets in the envelope · Suggested validation: duration trend; >20 % regression fails.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Root LV fills | P1 | Medium | Platform outage | 83.25 %, -3.81 GB/day | reclaim + per-dir signal |
| Data guard fails to reclaim | P1 | Low-Med | Writers wedge | reclaims 0 | drill + warning band |
| Host OOM again | P2 | Low-Med | VM kill | Sep 27 OOM ×3 | host check + swap tiers |
| Backup window load harms ingest | P2 | Medium | Alert latency | load 29.65, 3.7 h copy | dedupe/bwlimit |
| Budget breach unseen | P2 | Medium | Data gaps | 77 % of budget | rate alert |

## Recommendations

### Immediate / Release Blocking
- Root reclaim plan + >=90 % critical page (PERF-P1-001); <15 GiB data warning (PERF-P1-002).

### This Week
- Swap/memory tiers and ingest-rate budget alert (PERF-P2-001/003); fix guard text; cap/dedupe offsite upload (PERF-P2-002).

### This Month
- Guard drill + retention decision; explicit index mappings/schema check (PERF-P2-004); cost register (PERF-P3-001).

### Later / Platform Evolution
- Capacity model (balloon floor, per-stack RAM/CPU), performance budgets in CI, scheduled benchmark (PERF-P3-002).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Data-LV warning <15 GiB | early signal before guard | `bootstrap/90-alerting.sh` | evaluates |
| Swap >75 % alert | pressure visible | `bootstrap/90-alerting.sh` | evaluates |
| Ingest-rate budget panel+alert | tracks 120 docs/s target | exporter, dashboards | non-zero panel |
| Guard text 5→10 GiB | accurate message | `disk_guard.sh:94-98` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Root reclaim automation | P1 | falcon maintainer | M | maintenance window |
| Offsite dedupe/chunking | P2 | falcon maintainer | M | Spaces limits |
| Explicit index template | P2 | falcon maintainer | M | reindex decision |
| PVE host memory monitoring | P2 | owner + maintainer | S/M | PVE access |

## Suggested Tests

- Integration: disk-guard drill (cross 10 GiB, verify reclaim + page); root fill drill to 90 %.
- Load: burst/replay to the 120 docs/s budget; confirm warnings fire before drops; watch eval latency.
- Regression: schema-drift check on a new index; aggregation smoke test (non-zero).
- CI: record ingest benchmark + workflow duration; fail on >20 % regression.

## Suggested Documentation Updates

- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: 10 GiB threshold, measured slopes, warning bands.
- `docs/phase5/PERFORMANCE_ENVELOPE.md`: refresh capacities (171/122 GB), current rates, N/A frontend.
- New `docs/runbooks/CAPACITY_PLAN.md`: per-resource first signal/failure distances and owner actions.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is 120 docs/s still the target after the SPAN fix? | budget validity | owner confirmation |
| What RPO is acceptable given the ~4 h copy? | threshold decisions | owner decision |
| Will ISM steady state hold the data LV flat after Oct 5? | trajectory confidence | 7-day free-space series |
| What are actual Spaces/droplet costs? | cost model | billing console |

## Appendix

| Resource | Current | First signal | Distance to first signal | Failure mode | Distance to failure |
|---|---|---|---|---|---|
| Root `/` | 83.25 %; 30.7 GB free | 85 % warning | 0.8-1.4 days | root full: writes fail | 8-13 days |
| Data `/srv/falcon` | 62.8 %; 48.6 GB free | 10 GiB guard acts | ~13 days (24 h slope; 7 d improving) | writers wedge; spool overflow | ~16 days |
| Swap | 55.9 % used | none (gap) | n/a | OOM/latency | ~9 days at 24 h slope (unreliable) |
| RAM available | 36.7 % | 10 % rule | ~4 GB | OOM kills | host OOM history |
| Probe buffer | 43.5 MB / 2 GiB | 1 GiB | far | block edge forwarding | 1.5 GiB critical |
| Ingest | 92-94 docs/s | none | 22 % below budget | drops/backlog | 120 docs/s budget |
| Suricata drops | 0 | >0 rule | none | capture loss | n/a |

Commands used: `df -B1 / /srv/falcon`; PromQL `deriv`, `predict_linear`, `max_over_time` on `node_filesystem_*`, `node_memory_*`, `falcon_opensearch_*`, `falcon_container_*`, `node_load1`; `journalctl -u falcon-alert-relay`; textfile metrics. No mutations performed.
