# 02_architecture_runtime_topology — Prompt 02 - Architecture and Runtime Topology Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `02_architecture_runtime_topology.md` (area ARCH, prompt)

## Verification Performed

## Metadata

- Domain: `02_architecture_runtime_topology` (area ARCH)
- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`); live host checks read-only on the same host, 2026-10-09 21:29-21:50 UTC
- Emitted: 2026-10-09T21:52:25Z by the repo-deep-dive full-pass subagent
- Scope limitation: live inspection was read-only; no restarts, reconfigurations or deployments.

## Scope

Reviewed: the single-host topology (Proxmox VM `falcon`, Ubuntu 24.04) and its containers, the central/probe data path, auth/session surfaces, tenant boundaries (single owner; zone isolation), request lifecycle, background jobs/timers, notifications, external integrations, deployment topology, environment parity and runtime validation. Evidence: repository topology docs + compose/config, plus live read-only checks (docker, systemd, journal, nft, wireguard, textfile metrics, Grafana API).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md:23-36` | doc | documented topology and data path | SPAN -> Suricata/pmacct -> Vector edge -> aggregator -> OpenSearch; Prometheus/Grafana side-channel |
| `docs/architecture/{TARGET_ARCHITECTURE,DATA_FLOW_AND_CLASSIFICATION,PORT_PROTOCOL_MATRIX,TRUST_BOUNDARIES,IDENTITY_AND_SECRETS,STORAGE_CAPACITY_MODEL}.md` | docs | topology, ports, trust, data classes | live-bind reconciliation 2026-10-01 |
| `compose/central/docker-compose.yml`, `compose/probe/docker-compose.yml`, `compose/mct/*` | source | deployment sources | digest-pinned; declared hardening |
| `config/vector/aggregator.yaml`, `config/vector/edge.yaml` | source | transport/auth/buffering | edge disk buffer 2 GiB; basic-auth ingest |
| `config/traefik/*`, `config/prometheus/*`, `config/nftables/*`, `config/wireguard/*` | source | ingress, scrape, firewall, VPN | |
| `bootstrap/30-firewall.sh`, `31-docker-user-firewall.sh`, `32-inbound-mode.sh`, `60-central-deploy.sh`, `70-probe-deploy.sh`, `90-alerting.sh` | source | enforcement + provisioning | alert rules provisioned by API |
| `docs/threat-model/THREAT_MODEL.md` | doc | trust boundaries | |
| live `docker ps/inspect/stats`, `systemctl`, `journalctl -k`, `nft list`, `wg show`, textfile metrics, Grafana API | live | as-built state | timestamped below |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docker ps` (27 containers) | live | as-built topology | central, probe, Wazuh multi-node, IRIS, OpenCanary |
| `docker inspect` (central services) | live | declared-vs-running hardening | all declare `no-new-privileges`; cap_drop ALL on vector/prometheus/grafana/ntfy |
| `falcon_container_drift` metric | live | continuous drift check | all kinds `0`; `falcon_container_undeclared 1` (forwarder installed by script, not compose) |
| `journalctl -k` | live | OOM analysis | 18 vector cgroup OOM kills on 2026-10-09; 5 on 2026-10-08; RSS ~505-518 MB vs 512 MiB limit |
| `docker inspect falcon-central-vector-aggregator-1` | live | restart count | `RestartCount=23`, `Memory=536870912` |
| `docker stats --no-stream` | live | current memory | aggregator 510.8 MiB / 512 MiB (99.77%) |
| `curl 127.0.0.1:9598/metrics` | live | vector internals | edge_ingest received 903,021 vs sent 474,013 (backlog) at capture |
| textfile metrics (`/srv/falcon/textfile/*.prom`) | live | feature state | services all `1`; e2e recovered; backup stamps |
| Grafana API `/api/v1/provisioning/alert-rules` | live | live rule set | 77 rules; all updated 2026-10-03T03:49-03:50Z |
| `wg show` | live | VPN topology | wg0 port 5182; 8 peers, handshakes seconds old |
| `nft list ruleset` | live | enforcement | `FORWARD` policy drop; DOCKER-USER chain present |
| `git -C /home/user/falcon-build ...` | live | source/tree state | see ARCH-P1-002 |
| `falcon_port_matrix_undocumented` | live | port matrix drift | 0 |
| OpenSearch exporter metrics | live | storage state | status 1 (yellow), 118,241,931 docs, 58.9 GB |

## Executive Summary

The documented topology matches the running system structurally: 27 containers, a single Traefik entry point, internal Docker networks, WireGuard on 5182, default-deny host firewall, and a continuous running-vs-declared container drift check at zero. The serious live findings are (1) the central Vector aggregator is in a cgroup OOM restart loop (23 restarts; 18 kills in the last 24 h; ~100% of its 512 MiB limit) with no container-level memory/restart alert, and (2) the live host's source tree has diverged from the audited commit: it forked from origin/main at `54d67fd`, carries two unpushed local commits plus uncommitted alert-rule changes, is missing the merged remediation commits #46-#48 (including the OBS-P0-001 per-file textfile freshness rules), and its live Grafana has 77 rules versus the repo's 79/83. Single-host concentration remains owner-accepted. The prior hardening-parity finding is now verified fixed; the ingest shared-secret and MCT/Wazuh pin-scope findings remain partially fixed.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Central stack | `compose/central/docker-compose.yml` | traefik, opensearch(+dashboards), vector-aggregator, prometheus, grafana, redis, ntfy, ntopng, node-exporter | running, drift 0 | medium | 10 services |
| Probe stack | `compose/probe/docker-compose.yml` | suricata (SPAN), vector-edge (2 GiB disk buffer) | running | medium | suricata restarted 4 h ago |
| MCT live | `compose/mct/` | IRIS, OpenCanary | running | medium | first-party, pinned |
| Wazuh multi-node | `automation/wazuh/multi-node/` | 3 indexers, manager, worker, dashboard, cloudflared, nginx | running | medium | cloudflared/nginx floating tags |
| Data path | SPAN ens19 -> suricata/pmacct -> vector-edge -> aggregator:6000 -> OpenSearch | telemetry | running, OOM loop on aggregator | high | see ARCH-P1-003 |
| Metrics path | node-exporter textfile + direct scrapes (prometheus/node/traefik/vector/grafana) | platform health | running | medium | OpenSearch not scrapable (documented) |
| Alerting path | Grafana 77 rules -> relay -> ntfy (+ independent ntfy, dead-man) | alerting | running, 6 repo rules not provisioned | medium | see FEAT-P2-002 |
| Ingress | Traefik 80/443 + Cloudflare tunnel routes | access | running | medium | public routes: grafana/dash/ntop/ntfy/iris/soc/enroll |
| VPN | wg0 5182 (8 peers) + enroll service | telemetry/enrollment | running | low | |
| Backups | falcon-backup.timer 03:30, offsite, R2 cold copy, Wazuh snapshots | recovery | daily job failed Oct 8/9, manually recovered 16:49 today | medium | see report note |
| Source tree | `/home/user/falcon-build` | ops source | diverged (`6e4fccd` + dirty) | high | see ARCH-P1-002 |

## Findings

### ARCH-P1-001 - Single-host concentration: host loss is total pipeline loss (owner-accepted)

- Severity: P1
- Confidence: High
- Area: ARCH
- Evidence:
  - `README.md:5-6` — one Ubuntu 24.04 KVM host (`falcon`)
  - `compose/central/docker-compose.yml` — single central stack; no warm standby
  - prior register: `runs/falcon-20261005-full-main-e267ce1/follow_up_register.md` — ARCH-P1-001 `owner-accepted` (documented RTO/RPO acceptance)
- What is happening: all capture, storage, metrics, alerting and delivery run on one host; there is no warm standby.
- Why it matters: host loss is total monitoring loss (the edge buffers ~2 GiB, then blocks).
- User / business impact: monitoring outage until the host is rebuilt.
- Security / privacy / reliability impact: high availability risk, accepted by the owner.
- Recommended fix: warm standby or a tested RTO/RPO acceptance (already recorded).
- Suggested validation: restore rehearsal results + owner sign-off artifact.
- Owner suggestion: owner.
- Effort estimate: L.
- Dependencies: hardware.
- Status: owner-accepted.

### ARCH-P2-001 - Declared container hardening lags the running containers (verified fixed)

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `compose/central/docker-compose.yml` — `security_opt: ["no-new-privileges:true"]` on traefik, opensearch, dashboards, vector, prometheus, grafana, redis, ntfy, node-exporter; `cap_drop: [ALL]` on vector/prometheus/grafana/ntfy
  - live `docker inspect` — same controls present on the running containers
  - `falcon_container_drift{kind="security"} 0` (continuous check, `automation/validation/container_drift_check.sh:44`)
- What is happening: declared and running hardening are now at parity and continuously gated; the prior gap is closed.
- Why it matters: container hardening cannot silently lag again.
- Recommended fix: none; keep the drift check in the gate. Residual opportunity: no service uses `read_only` root filesystems (not a declared/live gap).
- Status: verified-fixed.

### ARCH-P2-002 - Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope (partially fixed)

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `pins/images.lock` — 24 entries now include `wazuh/wazuh-manager|indexer|dashboard:4.14.7`, `cloudflare/cloudflared:latest`, `nginx:stable`, `python:3.12-alpine` with recorded digests
  - `sbom/*wazuh*.cdx.json` present (SBOM coverage)
  - `pins/supply-chain-waivers.json` — blanket waiver `root: mct/compose, ref: *` (review_by 2026-12-31)
  - `mct/VENDORING.md:38` — 29/37 unpinned refs in `mct/compose/`
  - live `docker ps` — `cloudflare/cloudflared:latest`, `nginx:stable`, `wazuh/*:4.14.7` run tag-only refs
- What is happening: Wazuh is now in the lock/SBOM; the vendored MCT compose tree remains tag-only under a blanket waiver and floating tags still run live.
- Why it matters: revived staged services or a moved `latest` bypass the pin policy.
- Recommended fix: scope the waiver per ref (as the Wazuh waivers already do), or make `mct/compose` non-deployable (FEAT-P2-001); replace `latest`/`stable` live refs with digest refs at the next deploy.
- Suggested validation: `check_compose_digests.py` over `mct/compose` with no blanket waiver.
- Status: partially-fixed.

### ARCH-P2-003 - Live ingest authentication is a shared secret header, not mTLS (partially fixed)

- Severity: P2
- Confidence: High
- Area: ARCH
- Evidence:
  - `config/vector/edge.yaml:245-246` — sink to `vector-aggregator:6000` uses `auth: strategy: basic` with a shared user/password
  - `config/vector/aggregator.yaml:25-28` — `edge_ingest` HTTP source uses the same basic auth
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` (N-08) — ingest auth described as a shared secret
- What is happening: edge->central ingest is authenticated by a shared secret over the (internal) network; no per-device certificate identity or request signing/idempotency.
- Why it matters: any holder of the shared secret can inject telemetry; a replay is not distinguishable.
- Recommended fix: certificate/mTLS identity for ingest (the edge program already has certificate-attributed ingest), or request signing + idempotency keys.
- Status: partially-fixed.

### ARCH-P1-002 - Live host source tree has diverged from the audited commit and is dirty; merged remediation is not deployed

- Severity: P1
- Confidence: High (reproduced from the live tree and the live Grafana API)
- Area: ARCH
- Evidence:
  - `git -C /home/user/falcon-build rev-parse HEAD main origin/main` -> `6e4fccd` / `6e4fccd` / `08e20d1`; `git merge-base 08e20d1 6e4fccd` -> `54d67fd`; `git log 54d67fd..6e4fccd` -> 2 local commits (`4a64c76`, `6e4fccd`)
  - `git merge-base --is-ancestor 483f878|f7522d0|27ed413 6e4fccd` -> NOT ancestor: live tree is missing the merged remediation commits #46 (OBS-P0-001), #47 (API-P1-001), #48 (FINAL-P1-001) plus #43/#44/#45
  - `git -C /home/user/falcon-build status --porcelain` -> `M config/prometheus/edge-alerts.yaml` (119 added lines of sensor-health rules) + review-package artifacts; 12 Oct-9 evidence captures are committed only in the local `6e4fccd`
  - `falcon_runtime_source_info{commit="6e4fccd",dirty="1"} 1` and `falcon_runtime_source_dirty 1` (live textfile metrics)
  - `grep -c falcon-textfile-collector /home/user/falcon-build/bootstrap/90-alerting.sh` -> 0 (audited tree: 3); `ls /home/user/falcon-build/automation/validation/restore_assertion.sh` -> absent
  - live Grafana API: 77 rules, none of `falcon-textfile-collector-{absent,stale,stale-daily}`; all 77 last updated 2026-10-03T03:49:54-03:50:04Z
  - `docs/CURRENT_STATE.md:103` — "live host now runs current main"
- What is happening: the program's live source tree forked from origin/main at `54d67fd` (2026-10-04), accumulated two unpushed local commits, and is dirty; it lacks the merged remediation set, while its uncommitted alert-rule changes run live. The runtime scripts/metrics identify the live tree as `6e4fccd`+dirty, not the audited `08e20d1`.
- Why it matters: findings marked verified-fixed in the follow-up register (OBS-P0-001 via PR #46, FINAL-P1-001 via PR #48) are not present in the live tree; live alerting differs from both the repo and the catalogue; the documented "runs current main" claim is false.
- User / business impact: operators believe remediations are live when they are not; alert coverage is weaker than documented.
- Security / privacy / reliability impact: unreviewed live configuration changes; monitoring-death detection gap (the P0-class freshness rules are absent live).
- Recommended fix: converge the live tree on origin/main (fetch/merge, reconcile the local ops commit through a PR), commit or revert the dirty `edge-alerts.yaml` change, re-provision Grafana rules from the converged tree, and add a live-source drift alert (the `falcon_runtime_source_dirty` metric exists but has no rule).
- Suggested validation: `git -C /home/user/falcon-build status --porcelain` clean at origin/main; live rule set equals the script's UID set; a rule on `falcon_runtime_source_dirty` / commit age.
- Owner suggestion: ops owner.
- Effort estimate: M.
- Dependencies: PR for the local ops commit (#49).
- Status: open.

### ARCH-P1-003 - Central Vector aggregator is in a cgroup OOM restart loop; no container memory/restart alert covers it

- Severity: P1
- Confidence: High
- Area: ARCH
- Evidence:
  - `journalctl -k` — 18 x `Memory cgroup out of memory: Killed process ... (vector)` on 2026-10-09 (first 02:29:19Z; 5 on 2026-10-08; 0 on 2026-10-07); RSS ~505-518 MB per kill
  - `docker inspect falcon-central-vector-aggregator-1` — `RestartCount=23`, `Memory=536870912`, started 21:19:13Z
  - `docker stats --no-stream` — aggregator `510.8MiB / 512MiB` (99.77%)
  - `compose/central/docker-compose.yml:149-152` — `memory: 512M` limit; `config/vector/aggregator.yaml` has no source-side queue bound (sink buffer default 500 events)
  - vector internals at capture — `edge_ingest` received 903,021 vs sent 474,013 events (large in-flight backlog, consistent with edge disk-buffer replay after restarts)
  - `falcon_pipeline_e2e` — failures 19:56Z / 20:41Z (last failure epoch 1791578410 = 20:40:10Z); recovered 21:25Z
  - `bootstrap/90-alerting.sh:402` — the only restart-loop rule is Suricata-specific; `:371` `falcon-container-unhealthy` does not catch a container that restarts and becomes healthy again; no rule uses `falcon_container_mem_bytes` for a near-limit condition
- What is happening: the central ingest container repeatedly grows to its 512 MiB cgroup limit and is OOM-killed (~every 10-25 minutes in the hour before capture), restarting and replaying the probe buffer, which appears to feed the loop. Alerting sees downstream e2e failures but not the root cause.
- Why it matters: the central ingest path (syslog TCP 514 and edge_ingest) is interrupted continuously; in-memory sink buffers (500 events) are lost on each kill; the loop masks itself as transient e2e failures.
- User / business impact: telemetry gaps and alert noise; operator time on a recurring failure.
- Security / privacy / reliability impact: reliability of the monitoring pipeline itself.
- Recommended fix: right-size the limit or bound the source-side queue (e.g., disk buffer on the aggregator ingest, explicit `buffer.max_events`/`max_size` and concurrency limits), investigate the post-restart replay burst, and add an alert on container memory near limit + policy-restart count for central services.
- Suggested validation: 24 h without OOM kills; a synthetic replay test that does not exceed the limit; alert rule fires on a memory-pressure fixture.
- Owner suggestion: ops owner.
- Effort estimate: M.
- Dependencies: none.
- Status: open.

### ARCH-P3-001 - Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth

- Severity: P3
- Confidence: High
- Area: ARCH
- Evidence:
  - `docs/architecture/PORT_PROTOCOL_MATRIX.md:27` (N-08) — authentication column: "shared secret header"
  - `config/vector/aggregator.yaml:25-28` — `auth: strategy: basic`
  - `config/vector/edge.yaml:245-246` — `auth: strategy: basic`
- What is happening: the authoritative port/auth matrix names a mechanism that is not implemented.
- Why it matters: operators/reviewers reason about the wrong control; both mechanisms are shared-secret based but differ in implementation and rotation.
- Recommended fix: correct the N-08 row (and any negative-test wording) to "HTTP basic auth (shared credential)".
- Suggested validation: doc review against config.
- Owner suggestion: maintainer.
- Effort estimate: S.
- Dependencies: none.
- Status: open.

## Prior-Run Comparison

| Prior finding | Status now | Evidence |
|---|---|---|
| ARCH-P1-001 | owner-accepted (unchanged) | single host; register status |
| ARCH-P2-001 | verified-fixed | compose/live parity + `falcon_container_drift{security}=0` |
| ARCH-P2-002 | partially-fixed | Wazuh in lock/SBOM; MCT blanket waiver + floating tags live |
| ARCH-P2-003 | partially-fixed | basic-auth ingest unchanged |

New this run: ARCH-P1-002 (live source divergence / undeployed remediation), ARCH-P1-003 (aggregator OOM loop), ARCH-P3-001 (matrix auth description).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Aggregator OOM loop | P1 | Certain (ongoing) | High | 23 restarts; 18 kills/24h | bound queues + alert |
| Live tree diverged / remediation not deployed | P1 | Certain | High | git state; live rules | converge + drift alert |
| Single host | P1 | Low | Critical | one host | owner-accepted |
| Floating tags live | P2 | Medium | Medium | `latest`/`stable` running | digest refs |
| Shared-secret ingest | P2 | Medium | Medium | basic auth configs | mTLS/signing |

## Recommendations

### Immediate / Release Blocking
- Break the aggregator OOM loop or bound its queues; add the container memory/restart alert (ARCH-P1-003).

### This Week
- Converge the live tree on origin/main and re-provision the alert rules (ARCH-P1-002); reconcile the dirty `edge-alerts.yaml`.
- Scope the MCT waiver per ref (ARCH-P2-002).

### This Month
- Move ingest to certificate identity or signing (ARCH-P2-003); replace floating live tags.

### Later / Platform Evolution
- Warm standby / tested RTO-RPO for the owner-accepted single-host risk.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Alert on `falcon_runtime_source_dirty` | catches undeployed/uncommitted live changes | `bootstrap/90-alerting.sh` | rule fires on a fixture |
| Alert on container memory > 90% of limit | catches the OOM loop before the kill | `bootstrap/90-alerting.sh` + exporter | rule fires |
| Correct N-08 wording | removes doc drift | `PORT_PROTOCOL_MATRIX.md` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Aggregator buffer/limit redesign | P1 | ops | M | load evidence |
| Live-source convergence + drift gate | P1 | ops | M | PR #49 |
| mTLS ingest | P2 | ops/edge | L | edge program |
| Container memory/restart alerting for all central services | P2 | ops | S | exporter |

## Suggested Tests

- Load/replay test: edge buffer replay against the aggregator with bounded memory; assert no OOM.
- Integration: live-rule set equals `bootstrap/90-alerting.sh` UIDs (provisioning drift check).
- CI: port matrix auth column matches vector configs.
- Manual: `git -C /home/user/falcon-build status --porcelain` empty on the deploy tree after convergence.

## Suggested Documentation Updates

- `PORT_PROTOCOL_MATRIX.md` N-08 auth wording.
- `docs/CURRENT_STATE.md` — correct the "live host runs current main" statement until convergence.
- Runbook for the aggregator memory/backlog loop (symptoms, bounds, replay behavior).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Root cause of the memory growth (source backlog vs leak)? | determines fix (bounds vs upgrade) | vector metrics over time; heap profile |
| Is the live fork intentional (ops branch) or drift? | determines convergence path | owner statement; PR #49 state |
| Was alert provisioning expected to run at every merge? | determines the drift gate design | ops statement |

## Limitations

- Live checks are point-in-time (2026-10-09 21:29-21:50 UTC) and read-only; no load tests or restarts were performed.
- One container (`falcon-wazuh-forwarder`) is created by `automation/wazuh/forwarder-install.sh` and appears as `falcon_container_undeclared 1`; not treated as a finding.
- The daily `falcon-backup.service` failed on 2026-10-08 and 2026-10-09 (OpenSearch snapshot step) and was recovered manually on 2026-10-09 16:49Z (`.last_backup_epoch`; offsite 19:01Z); resilience/backup domains own that finding.

## Findings

| ID | Severity | Title |
|---|---|---|
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS |
| ARCH-P1-002 | P1 | Live host source tree has diverged from the audited commit and is dirty; merged remediation is not deployed |
| ARCH-P1-003 | P1 | Central Vector aggregator is in a cgroup OOM restart loop; no container memory/restart alert covers it |
| ARCH-P3-001 | P3 | Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth |
