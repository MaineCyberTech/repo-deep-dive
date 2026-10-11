# 13_resilience_recovery_failure_modes — Prompt 13 - Resilience, Recovery, and Failure Modes Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `13_resilience_recovery_failure_modes.md` (area RES, prompt)

## Verification Performed

# Resilience, Recovery, and Failure Modes Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c9` (branch `main`; `origin/main` = `584e1a3` + publication commits `3c11752`/`f5cb7c9`)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-11T04:45Z
- Auditor: subagent (RES)
- Area code: RES
- Scope limitations: read-only; no restarts, failure injection, or restores were performed. Live state was sampled while the nightly backup's offsite upload was still running (falcon-backup.service activating > 1 h). Journal windows are sampled; the boot journal of the 10-day boot is large and was queried with bounded ranges.

## Scope

Reviewed failure behavior at `f5cb7c9`: timeout/retry/backoff, idempotency, circuit breakers, queue/DLQ, webhook recovery, worker recovery, graceful shutdown, dependency failure (DB/Redis/API/email/file/realtime are mostly container/service equivalents in this infra repository), offline client (edge), transactions/partial writes, duplicate events, backups/restore, rollback, incident runbooks, and failure-injection tests. Verified live read-only: kernel OOM records, container memory/restart state, host memory/swap, root/data LV free space and the disk-guard journal, systemd boot ordering for the Wazuh VPN proxy sockets, the backup job's live run, the alert relay journal, and the systemd timers. Not reviewed: application-layer code (this repository is infrastructure-only), Kubernetes-style circuit breakers (not present by design), and any mutating recovery action.

## Evidence Reviewed

- `compose/central/docker-compose.yml` (restart policies, memory limits, healthchecks; aggregator limit at :154)
- `config/vector/aggregator.yaml`, `config/vector/edge.yaml` (buffers, retries, DLQ, internal metrics)
- `bootstrap/85-backup-job.sh` (3-attempt snapshot retry :51-65, retention keep-3 :68-76, abort markers)
- `bootstrap/80-offsite-backup.sh` (bounded retry/backoff :71-95, dead-letter marker :97-106, upload-state delta :254-409, abort traps)
- `automation/validation/disk_guard.sh` (root-LV threshold :24, safe reclaim order :120-140, alert+exit-1 :147-159)
- `automation/validation/lib/abort.sh`, `restore_assertion.sh`, `restore_rehearsal.sh`, `write_rejection_test.sh`, `disk_pressure_drill.sh`, `sensor_silence_drill.sh`, `index_rename_rollback_drill.sh`, `lab_stress_test.sh`
- `config/systemd/falcon-backup.{service,timer}`, `falcon-disk-guard.{service,timer}`, `falcon-wazuh-{agent,enroll}-proxy.socket`
- `docs/phase9/TEST_PROCEDURES.md`, `docs/phase7/runbooks/RESTORE.md`, `docs/runbooks/CAPACITY_AND_TELEMETRY.md`, `docs/runbooks/VPN.md`, `docs/runbooks/RUNTIME_AND_SCHEDULE.md`
- Live: `journalctl -k` (OOM), `journalctl -u falcon-disk-guard.service`, `journalctl -u falcon-backup.service`, `journalctl -b 0` (boot ordering), `journalctl -u falcon-wazuh-agent-proxy.socket`, `systemctl show`, `docker inspect`, `docker stats`, Prometheus queries, `df -k`, `du`, `free -m`, `uptime`, `ps`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docker inspect falcon-central-vector-aggregator-1` -> `Mem=1073741824 RestartCount=0 OOMKilled=false`, StartedAt 2026-10-11T02:28:00Z | live | Prior RES-P1-001 (aggregator OOM crash-loop) closure | Supported: 1 GiB limit live, 0 restarts, no OOM |
| `journalctl -k --since 2026-10-09 20:00 \| grep -c 'Killed process'` -> 0 | live | OOM recurrence check | Supported: no kernel OOM kills since the fix |
| `falcon_host_memory_available_percent` = 32.56; `falcon_host_swap_used_percent` = 52.88; `free -m` 15,536 MiB total | live | Prior RES-P2-001 host headroom | Partially supported: RAM grew to ~15.2 GiB and available is ~33%, but swap remains ~4.0 GiB used |
| `journalctl -u falcon-disk-guard.service` 04:15/04:30 runs: `BELOW THRESHOLD: reclaiming` -> `still below threshold after reclaim - alert sent` -> exit 1; `df -k /` root_free 19.56 GiB | live | New root-LV capacity failure | Supported: guard in failing loop, root below its 20 GiB threshold |
| `journalctl -b 0` 02:27:44Z: `sockets.target: Found ordering cycle on falcon-wazuh-{enroll,agent}-proxy.socket/start ... dependency on wg-quick@wg0.service/start ... Job ... deleted`; socket `Listening` only at 03:13:02Z | live | Boot resilience / prior "fixed" claim | Supported: boot race still present; listeners down 45 min |
| `ps`/`systemctl` 04:39Z: `falcon-backup.service` activating since 03:30:03Z; rclone 1 h 01 m copying 1,981 files / 68.3 GiB | live | Stuck/long-running backup run | Supported: no start timeout; service stuck in activating |
| Relay journal Oct 10-11: 48x `Falcon disk guard: root still below threshold`; `Disk space low` active since 03:24:10Z | live | Alerting of the new condition | Supported: condition is alerted every 15 min |
| `automation/validation/tests/` inventory (no aggregator-memory/OOM test); drills list | repo | Prior RES-P3-001 chaos coverage | Supported: still absent |
| `docs/runbooks/RUNTIME_AND_SCHEDULE.md:186`, `VPN.md:193` (boot-order "fixed 2026-09-30") | repo | Documentation vs live behavior | Contradicted by the live ordering cycle |

## Executive Summary

The two prior headline RES issues are genuinely closed: the central Vector aggregator no longer OOMs (1 GiB limit, 0 restarts, 0 kernel kills since 2026-10-09) and host memory headroom improved (15.2 GiB RAM, ~33% available, swap still ~4 GiB used). The retry/backoff and abort-marker machinery added on 2026-10-09 is present and exercised (3-attempt snapshot retry; the Oct 10-11 nightly runs completed their local snapshot + freshness + retention steps).

However, the live host is currently in a **root-LV capacity failure**: the relocated OpenSearch snapshot repository (69 GiB) sits on the root LV, the nightly snapshot added 5.56 GiB today, root free is 19.56 GiB against the guard's 20 GiB threshold, and the disk guard is reclaiming-and-failing every 15 minutes (unit in failed state, alert repeated 48 times in 28 h). The guard's reclaim list cannot free root space; 21.7 GiB of stale `/var/tmp/wz-migration/wazuh-stack.tar` and ~22 GiB of containerd data are reclaimable but unmanaged. If root fills, the nightly snapshot fails (the repository is on root) and RPO grows. Live update: the condition self-cleared at 04:45Z after a concurrent session pruned the oldest snapshot at 04:40Z (root 19.55 -> ~30 GiB free; guard 'ok') and began relocating the 21.7 GiB migration tarball off root at 04:45Z; the emergency prune cut the local chain to 2 snapshots, below the keep-3 policy, and the underlying churn (~4.3-5.5 GiB/night) is unchanged.

Second, the Wazuh VPN proxy socket boot race is **not fixed**: at the 2026-10-11T02:27:44Z boot systemd still found the ordering cycle and deleted both socket start jobs; the listeners were dead for 45 minutes until a session started them by hand, which also disconnected the remote Wazuh agent for ~30 minutes. The same pattern occurred at the 2026-10-01 boot. The new `falcon-wazuh-proxy-listeners` alert (PR #53) now detects it, but the root cause persists and the runbook still claims the 2026-09-30 fix works. A post-reboot verification was not run or recorded after the Oct 11 kernel-upgrade reboot.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Aggregator memory limit | `compose/central/docker-compose.yml:154` | Bound Vector memory | 1 GiB live, 0 restarts | Low | OOM loop closed |
| Snapshot retry | `bootstrap/85-backup-job.sh:51-65` | 3 attempts, 60 s apart + immediate alert | Present; live runs Oct 10/11 succeeded locally | Low | Exercised by nightly runs |
| Offsite retry/backoff + DLQ | `bootstrap/80-offsite-backup.sh:71-106` | 3 attempts, exponential backoff, dead-letter marker | Present; marker written Oct 10, cleared manually Oct 11 02:39 | Medium | Marker not bound to a success |
| Upload-state delta | `80-offsite-backup.sh:254-409` | Upload only new/changed repo files | State truncated to empty by the Oct 10 run; Oct 11 re-uploads 68.3 GiB | High | Symlink bug (fixed by #51) already damaged state |
| Abort markers | `automation/validation/lib/abort.sh`, `85/80/disk_guard` | Durable marker on interrupted runs | Present; `falcon-backup.aborted` present from Oct 10 | Low | Cleared on clean completion |
| Root-LV guard | `automation/validation/disk_guard.sh:24,147-159` | Reclaim + alert below 20 GiB | Failing every 15 min; alert delivered | High | Cannot free root in current layout |
| Wazuh proxy sockets | `config/systemd/falcon-wazuh-{agent,enroll}-proxy.socket` | Agent/enroll path over VPN | Boot ordering cycle deletes jobs; manual start needed | High | Detected by new rule |
| Backup timer/service | `config/systemd/falcon-backup.{timer,service}` | Daily 03:30Z backup | Timer `Trigger: n/a` while service runs >1 h; no `TimeoutStartSec`/`RuntimeMaxSec` | Medium | A hung run is invisible until staleness |
| Graceful shutdown | `falcon-backup.service: TimeoutStopSec=900`, abort traps | SIGTERM -> markers | Present | Low | Not re-exercised this window |
| Vector sink DLQ | `config/vector/aggregator.yaml` (route_valid.invalid) | Invalid-event DLQ only | Sink failures are counted/alerted, not dead-lettered | Medium | Known WH-P1-001 residual |
| Chaos tests | `automation/validation/tests/`, drills | Failure injection | No aggregator-memory/OOM, boot-order, or root-LV test | Medium | RES-P3-001 open |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Timeouts | 3 | Vector sink retries/timeouts; systemd `TimeoutStopSec=900`; no backup start/run timeout | No `TimeoutStartSec`/`RuntimeMaxSec`; offsite upload unbounded | Add a bounded runtime + stuck-run alert |
| Retries/backoff | 4 | `80-offsite-backup.sh:79-95` (3x, x3 backoff); `85-backup-job.sh:51-65` | Offsite retry re-uploads the full 68 GiB on state loss | Persist/repair upload state; cap retry payload |
| Idempotency | 3 | Snapshot reuse (80 never creates snapshots); upload-state delta; abort markers | Upload-state delta is fragile (symlink bug truncated it) | Add a state-integrity check before upload |
| Circuit breakers | 2 | Vector sink health/retries; no explicit breakers | No per-dependency breaker in host scripts | Not critical at this scale; document |
| Queue DLQ | 3 | Probe disk buffer (block), Vector DLQ, log-derived drop counter | Sink batches not dead-lettered/replayed | Keep WH-P1-001 tracked |
| Webhook recovery | 3 | ntfy relay with two paths; alert canary weekly; relay-path-failure rule | Lab ntfy internal-only; canary weekly | Increase canary frequency |
| Worker recovery | 3 | `restart: unless-stopped`; healthchecks; boot-order fix incomplete | Wazuh socket boot race; no post-reboot verification run | Fix socket cycle; automate boot check |
| Graceful shutdown | 3 | SIGTERM traps + markers; `TimeoutStopSec=900` | No verification after the Oct 11 reboot | Run/record `post_reboot_verify.sh` |
| DB/Redis/API/email/file/realtime failure | 3 | OpenSearch sink retry/alert; disk guard; buffer-at-cap behavior documented | Root LV exhaustion path unmitigated | Capacity plan (see RES-P1-002) |
| Offline client | 3 | Probe disk buffer 2 GiB (block) + edge spool metrics | Edge buffer cap 2 GiB; no offline-replay test | Add a buffer-cap chaos test |
| Transactions | 3 | OpenSearch snapshot atomicity; keep-3 retention | Local snapshot pruning is synchronous with the job | Acceptable |
| Partial writes | 3 | Snapshot `state=SUCCESS` check; upload-state only updated after success | A 68 GiB partial upload leaves the state empty | State recovery procedure |

## Detailed Review

### Item: Root-LV capacity and the disk guard

- Evidence: `automation/validation/disk_guard.sh:24` (20 GiB root threshold), live guard journal 04:15/04:30Z, `df -k /` 19.56 GiB free / 89% used, `du` 69 GiB `/var/lib/falcon-snapshots`, `find -newermt 03:00` 238 files / 5.56 GiB, 21.7 GiB `/var/tmp/wz-migration/wazuh-stack.tar`.
- What it does: the guard reclaims EVE rotations, keeps 3 snapshots, keeps 3 config archives, then alerts and exits 1 if still below threshold.
- How it appears to work: root free crossed below 20 GiB when the Oct 11 snapshot completed; the reclaim set had nothing left to delete; the guard now fails every run.
- Dependencies: OpenSearch snapshot repo on root; nightly churn ~4.3-5.5 GiB; containerd and /var/tmp also on root.
- Current controls: guard + relay alert + `Disk space low` Grafana rule (firing since 03:24Z) + projection rule.
- Missing controls: root-side retention/reclaim for the snapshot repo; a managed cleanup for `/var/tmp/wz-migration` and containerd; a capacity plan for the relocated repo.
- Risks: root exhaustion -> snapshot failures, RPO growth, OS/containerd impact.
- Recommended improvement: reclaim the 21.7 GiB stale tarball under a documented policy, add it (and containerd prune) to the guard, and either move the snapshot repo to a dedicated volume or accept+document the retention window.
- Suggested tests: a bounded drill that fills a scratch mount below the threshold and asserts reclaim+alert; a dry-run root-capacity projection.
- Suggested docs: update `docs/runbooks/CAPACITY_AND_TELEMETRY.md` with the new root LV composition and the reclaim policy.

### Item: Wazuh VPN proxy socket boot ordering

- Evidence: `journalctl -b 0` ordering-cycle lines, socket `Listening` at 03:13:02Z, `systemctl show` (`Before=multi-user.target sockets.target`, `After=wg-quick@wg0.service`; wg-quick `After=basic.target`), socket journal history (Oct 1 03:21:32Z, Oct 11 03:13:02Z).
- What it does: binds 10.99.0.1:15140/15141 for remote Wazuh agents after wg0 exists.
- How it appears to work: the socket keeps implicit `Before=sockets.target` and `After=wg-quick@wg0.service`; wg-quick is ordered after basic.target which pulls sockets.target -> the cycle is still detected and systemd deletes the socket start job.
- Dependencies: `wg-quick@wg0.service`, systemd ordering, `WantedBy=multi-user.target`.
- Current controls: new alert rule `falcon-wazuh-proxy-listeners` (10 min), manual `systemctl start`.
- Missing controls: a working boot dependency (e.g. `DefaultDependencies=no` on the socket or a post-wg0 unit), automated boot verification.
- Risks: every reboot silently cuts the remote-agent path; telemetry and enrollment break until an operator acts.
- Recommended improvement: break the cycle in the unit itself and add the socket state to `post_reboot_verify.sh`/`boot_check_readonly.sh`.
- Suggested tests: reboot-ordering test (`systemd-analyze verify`), a bounded `systemctl restart` ordering drill.
- Suggested docs: correct `docs/runbooks/VPN.md:193` (the 2026-09-30 fix does not hold).

### Item: Host memory and swap

- Evidence: `free -m` 15,536 MiB total / 5,671 available; `falcon_host_memory_available_percent` 32.56; `falcon_host_swap_used_percent` 52.88; trend Oct 4-11.
- What it does: the host runs the whole lab; swap is the safety margin.
- Current controls: early-warning rule (<20%), critical (<10%); no firings since Oct 9.
- Missing controls: per-service memory requests/limits; a swap-usage budget.
- Risks: a workload spike still risks OOM; swap ~4 GiB used masks headroom.
- Recommended improvement: refresh the capacity envelope (see PERF-P2-001), consider `zram`/swap policy review.

### Item: Backup/offsite run robustness

- Evidence: `85-backup-job.sh:92-99` (synchronous offsite call), `80-offsite-backup.sh:254-409` (state delta), live run (activating >1 h, 68.3 GiB re-upload), `.offsite-dead-letter` manual clear at 02:39:06Z.
- What it does: snapshot -> config archive -> offsite upload -> retention -> full verification -> stamp.
- How it appears to work: a single-threaded pipeline with abort markers; a failure leaves markers and does not advance the success stamp.
- Missing controls: start/run timeout; a state-integrity check; a stuck-run alert (see OBS-P2-004).
- Risks: multi-hour stuck runs; full re-uploads; DLQ alert state can be cleared without a success.

### Item: Failure injection and drills

- Evidence: `automation/validation/tests/` (42 files), `docs/phase9/TEST_PROCEDURES.md` drill catalogue, drills (`disk_pressure_drill.sh`, `sensor_silence_drill.sh`, `index_rename_rollback_drill.sh`, `write_rejection_test.sh`, `lab_stress_test.sh`).
- Current controls: sink write-rejection, disk pressure, sensor silence, alert storms, VPN, index-rename rollback.
- Missing controls: aggregator memory/OOM, host memory exhaustion, boot-order/socket, root-LV exhaustion, edge buffer cap.
- Recommended improvement: see the chaos test plan in the Appendix.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| RES-001 | Timeouts | `falcon-backup.service` (no start timeout) | `TimeoutStopSec=900` | No run/start bound | P2 | Add `TimeoutStartSec`/`RuntimeMaxSec` |
| RES-002 | Retries/backoff | `80-offsite-backup.sh:79-95`; `85-backup-job.sh:51-65` | 3x retries, x3 backoff | Retry re-uploads 68 GiB after state loss | P2 | State integrity check |
| RES-003 | Idempotency | Snapshot reuse; upload-state delta | Snapshot never duplicated | Delta state fragile | P2 | Validate state before upload |
| RES-004 | Circuit breakers | Vector sink health/retries | Sink retries | No host-level breaker | P3 | Document |
| RES-005 | Queue DLQ | `config/vector/aggregator.yaml`; DLQ dir | DLQ for invalid events | Sink batch DLQ absent | P2 | Keep WH-P1-001 |
| RES-006 | Webhook recovery | relay two paths; canary | Relay + canary | Canary weekly | P3 | Increase frequency |
| RES-007 | Worker recovery | restart policies, healthchecks | `unless-stopped` | Socket boot race | P1 | Fix ordering cycle |
| RES-008 | Graceful shutdown | SIGTERM traps; `TimeoutStopSec` | Markers | No recorded post-reboot verify | P2 | Automate boot checks |
| RES-009 | DB/Redis/API/email/file/realtime failure | Sink retry/alert; guard | Sink alerts; buffer-at-cap | Root LV exhaustion | P1 | Capacity plan |
| RES-010 | Offline client | Probe disk buffer 2 GiB; edge spool metrics | `when_full: block` | No buffer-cap test | P3 | Chaos test |
| RES-011 | Transactions | Snapshot `state=SUCCESS`; upload state | Atomic snapshot semantics | Local prune during run | P3 | Accept/document |
| RES-012 | Partial writes | Upload-state updated only after success | Abort markers | Empty state after partial upload | P2 | Recovery procedure |

## Findings

### RES-P1-002 - Root LV below the 20 GiB disk-guard threshold; guard failing every 15 min while the snapshot repository grows ~4.3-5.5 GiB/night

- Severity: P1
- Confidence: High (captured live at the audited commit; reproduced across four guard runs and the Prometheus free-space trend)
- Area: RES
- Evidence:
  - `automation/validation/disk_guard.sh:24` (`ROOT_THRESHOLD_KB=20 GiB`), `:120-159` (reclaim order; exit 1 after alert)
  - `journalctl -u falcon-disk-guard.service` 2026-10-11 03:45/04:00/04:15/04:30Z: `BELOW THRESHOLD: reclaiming` -> `still below threshold after reclaim - alert sent` -> `status=1/FAILURE`; `systemctl status` `failed`
  - `df -k /` 04:39Z: root 19.56 GiB free (89% used); `/srv/falcon` 95.9 GiB free (55%)
  - `du -x /`: `/var/lib/falcon-snapshots` 69 GiB on the root LV; `/var/tmp/wz-migration/wazuh-stack.tar` 21.7 GiB (2026-09-27); containerd 22 GiB
  - `find /var/lib/falcon-snapshots/opensearch -newermt '2026-10-11 03:00'` -> 238 files / 5.56 GiB added by the 03:30Z snapshot
  - Prometheus `node_filesystem_avail_bytes{mountpoint="/"}`: 52.8 GiB (Oct 9 16:00) -> 27.8 (Oct 9 22:00, relocation) -> 20.1 (Oct 10 04:00) -> 19.55 (Oct 11 04:39)
  - Relay journal: 48x `Falcon disk guard: root still below threshold` on Oct 10-11; Grafana `Disk space low` active since 03:24:10Z
  - `bootstrap/85-backup-job.sh:68-76` (keep-3 already satisfied: 3 SUCCESS snapshots live)
- What is happening: the snapshot repository was relocated onto the root LV on 2026-10-09; the nightly snapshot adds ~4.3-5.5 GiB; root free is now below the guard's 20 GiB threshold and the guard's reclaim set (rotated EVE on the data LV, keep-3 snapshots, 3 newest config archives) cannot free root space, so every 15-minute run reclaims nothing, alerts, and exits 1.
- Why it matters: the OpenSearch snapshot repository lives on root; if root fills, the nightly snapshot fails and the local/offsite RPO grows. Root also carries the OS, containerd and journald.
- User / business impact: a full root LV would stop backups and can degrade the whole host (containers, logging).
- Security / privacy / reliability impact: reliability; a failed snapshot silently reduces recoverability until the staleness rules fire.
- Recommended fix: (a) reclaim the 21.7 GiB stale `/var/tmp/wz-migration/wazuh-stack.tar` under a documented owner decision and add it (plus a bounded `containerd`/docker prune) to the guard's reclaim order; (b) raise the guard threshold or move the snapshot repo to a dedicated volume sized for keep-3 plus headroom; (c) document the retention window in `CAPACITY_AND_TELEMETRY.md`.
- Suggested validation: a bounded drill on a scratch mount below threshold asserting reclaim+alert; a 7-day projection of root free after the reclaim.
- Owner suggestion: platform/owner (storage decision)
- Effort estimate: S (reclaim) / M (volume or policy change)
- Dependencies: owner decision on the stale migration tarball; capacity plan
- Status: open
- Endpoint / data path: nightly job -> OpenSearch `/_snapshot/falcon-backup/<snap>` -> `/var/lib/falcon-snapshots/opensearch` (root LV) -> offsite Spaces
- Attack path: none identified

### RES-P2-002 - Wazuh VPN proxy socket boot race is not fixed: systemd still deletes the socket jobs on boot (listeners dead 45 min after the Oct 11 reboot)

- Severity: P1
- Confidence: High (live boot journal + socket start history + unit dependency graph)
- Area: RES
- Evidence:
  - `journalctl -b 0` 2026-10-11T02:27:44Z: `sockets.target: Found ordering cycle on falcon-wazuh-enroll-proxy.socket/start`, `Found dependency on wg-quick@wg0.service/start`, `Job falcon-wazuh-enroll-proxy.socket/start deleted to break ordering cycle` (same for `-agent-`)
  - `journalctl -u falcon-wazuh-agent-proxy.socket`: `Listening` at 2026-10-01T03:21:32Z and 2026-10-11T03:13:02Z only (after manual start); closed at the 02:24Z shutdown
  - sudo journal 03:13:01Z: `systemctl enable falcon-wazuh-agent-proxy.socket falcon-wazuh-enroll-proxy.socket; systemctl start ...` (manual recovery by a verification session)
  - `systemctl show falcon-wazuh-agent-proxy.socket`: `Before=multi-user.target sockets.target ...`, `After=sysinit.target system.slice wg-quick@wg0.service`; `systemctl show wg-quick@wg0.service`: `After=... basic.target ...`
  - `config/systemd/falcon-wazuh-{agent,enroll}-proxy.socket` (`WantedBy=multi-user.target`, comment claims the 2026-09-30 fix); `docs/runbooks/VPN.md:193` ("fixed 2026-09-30")
  - Relay journal: `Wazuh critical agent disconnected` FIRING 02:44:29Z -> RESOLVED 03:15:29Z
  - Rule `falcon-wazuh-proxy-listeners` live (PR #53; `falcon_wazuh_proxy_listeners_up` = 2 now)
- What is happening: moving the sockets to `multi-user.target` did not break the ordering cycle; the socket keeps an implicit `Before=sockets.target` (DefaultDependencies) plus `After=wg-quick@wg0.service`, and wg-quick is ordered after `basic.target` (which pulls `sockets.target`), so systemd still deletes the socket start job at boot. The listeners bind only when an operator starts them by hand.
- Why it matters: every reboot silently cuts the remote Wazuh agent/enrollment path until someone notices; the Oct 11 outage lasted 45 minutes (agent disconnected ~31 min). This is the third occurrence (2026-09-27/28, 2026-09-30, 2026-10-01, 2026-10-11).
- User / business impact: remote agents (including the DO server) lose the manager path; security telemetry from those hosts stops.
- Security / privacy / reliability impact: monitoring blind spot during and after any reboot.
- Recommended fix: remove the ordering cycle at the unit level (e.g. `DefaultDependencies=no` with explicit `Before=multi-user.target` on the sockets, or start the proxy services via an `ExecStartPost`/timer after wg0); add the socket state to `automation/validation/boot_check_readonly.sh` and `post_reboot_verify.sh`; correct `VPN.md`.
- Suggested validation: `systemd-analyze verify` plus a sanctioned reboot (or a stop/start ordering test) showing the listeners bind without manual action; the new alert rule fires when the metric is 0.
- Owner suggestion: platform
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: remote agent -> 10.99.0.1:15140 (socket) -> 127.0.0.1:1516 manager
- Attack path: none identified

### RES-P2-001 - Host memory/swap pressure improved but remains: ~33% available, ~4.0 GiB swap used; capacity envelope stale

- Severity: P2
- Confidence: High (live metrics + trend)
- Area: RES
- Evidence:
  - `free -m` 2026-10-11 04:19Z: total 15,536 MiB / available 5,671 MiB; swap 3,975 MiB used of 8,191
  - `falcon_host_memory_available_percent` 32.56 (now); trend Oct 4-11 shows dips to 12.7% (Oct 8 22:00) and 15.95% (Oct 9 16:00)
  - `falcon_host_swap_used_percent` 52.88 (now); 48.76 at Oct 11 04:00 vs 55-68% on Oct 6-10
  - No `Host memory pressure (early warning)` FIRING since 2026-10-09; 0 kernel OOM kills since 2026-10-09 20:00
  - Prior RES-P2-001 evidence (Oct 9): 18.5% available, 4.5/8 GiB swap, load 24.6
- What is happening: the host RAM was increased (~12.5 -> 15.2 GiB) and the aggregator OOM was removed, so available memory is materially better; swap usage remains ~4 GiB (half the swap device) and the capacity envelope/budget refresh is still pending (PERF-P2-001).
- Why it matters: swap absorbs pressure today, but a workload spike still risks OOM and container evictions; the documented envelope is stale.
- User / business impact: potential container evictions/degradation under a load spike.
- Security / privacy / reliability impact: reliability.
- Recommended fix: refresh the capacity envelope and memory budget; add explicit per-service memory requests/limits; review swap usage after the next full week.
- Suggested validation: a bounded load test (lab_stress_test.sh) watching available/swap and the early-warning rule.
- Owner suggestion: platform/owner
- Effort estimate: M
- Dependencies: PERF-P2-001 envelope refresh
- Status: partially-fixed
- Attack path: none identified

### RES-P3-001 - Failure-injection coverage still omits the failure modes that actually occurred (aggregator OOM, host memory, boot-order/socket, root-LV exhaustion)

- Severity: P3
- Confidence: High (test/drill inventory)
- Area: RES
- Evidence:
  - `automation/validation/tests/` (42 tests) has no aggregator-memory/OOM, host-memory, boot-order or root-LV test
  - Drills: `disk_pressure_drill.sh`, `sensor_silence_drill.sh`, `index_rename_rollback_drill.sh`, `write_rejection_test.sh`, `lab_stress_test.sh`, `phase9_span_load.sh`
  - `docs/phase9/TEST_PROCEDURES.md` catalogue (82 one-row scripts; sink/disk/silence/storm/VPN drills)
  - The 2026-10-08/09 aggregator OOM and the 2026-10-11 boot/socket and root-LV failures all occurred without a matching test
- What is happening: the test suite covers sink write rejection and disk pressure but not the failure classes that have actually hit the lab.
- Why it matters: without a repeatable injection, the fixes cannot be regression-tested.
- Recommended fix: add bounded tests (see chaos plan in the Appendix): aggregator OOM under a 1 GiB cap with a synthetic burst asserting the drop metric + rules; boot-order socket test; root-LV threshold drill on a scratch mount.
- Suggested validation: each test asserts detection + recovery and records a stamp.
- Owner suggestion: platform
- Effort estimate: M
- Dependencies: none
- Status: still-open
- Attack path: none identified

### RES-P3-002 - No post-reboot verification was run or recorded after the 2026-10-11 kernel-upgrade reboot; post-reboot degradations were visible only through alerts

- Severity: P3
- Confidence: High (journal has no `post_reboot_verify`/`boot_check_readonly`/`boot_order_check` entries since 02:27; runbook requires it)
- Area: RES
- Evidence:
  - `last -x` / `journalctl --list-boots`: clean reboot 02:24-02:27Z after a kernel upgrade (6.8.0-142 -> 6.8.0-146; `/var/log/apt/history.log`)
  - `journalctl --since '2026-10-11 02:27' | grep -iE 'post_reboot_verify|boot_check_readonly|boot_order_check'` -> no matches
  - `docs/runbooks/RUNTIME_AND_SCHEDULE.md:186` (boot_order_check live 17/17 2026-10-01, run by `post_reboot_verify.sh`); `docs/runbooks/OPERATOR_START_HERE.md:102`
  - Degradations after the reboot: socket outage 02:27-03:13, `Wazuh critical agent disconnected` 02:44-03:15, `Suricata restart loop` alert 02:39-03:29 (uptime-reset artifact; `falcon_suricata_restarts_total` = 0), `Disk space low` re-fired 03:24
- What is happening: the reboot was clean and planned, but the read-only boot checks were not executed/recorded and several degradations were only found via alerts.
- Why it matters: the same reboot class has previously caused the socket outage; without a recorded check the recurrence was invisible until the next audit.
- Recommended fix: run and record `boot_check_readonly.sh`/`post_reboot_verify.sh` after every reboot (wire it to a boot-time timer or document it as a mandatory step); note the Suricata uptime-reset alert artifact for planned reboots in the maintenance-window procedure.
- Suggested validation: a recorded run after the next sanctioned reboot.
- Owner suggestion: operator
- Effort estimate: S
- Dependencies: none
- Status: open
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Root LV fills -> snapshot repo write fails | P1 | High (growing ~4.3-5.5 GiB/night; 19.56 GiB free) | RPO grows; backup failure | guard journal; df; du | RES-P1-002 |
| Wazuh agent path dead after any reboot | P1 | High (3 occurrences) | Remote telemetry loss | boot journal; socket history | RES-P2-002 |
| Offsite upload thrash after state loss | P1 | Medium | DR copy stale; long runs | offsite log; 68.3 GiB re-upload | DR-P1-002 |
| OOM under a load spike | P2 | Medium | Container eviction | swap 52.9%; mem trend | RES-P2-001 |
| Hung backup run invisible for 36 h | P2 | Medium | Late detection | service activating >1 h; no start timeout | OBS-P2-004 |

## Recommendations

### Immediate / Release Blocking

- Reclaim or owner-accept `/var/tmp/wz-migration/wazuh-stack.tar` (21.7 GiB) and add it plus containerd pruning to the disk guard (RES-P1-002).
- Fix the Wazuh proxy socket boot ordering and verify with a sanctioned reboot (RES-P2-002).

### This Week

- Persist/repair the offsite upload state and bound the backup run time (RES-P1-002, DR-P1-002, OBS-P2-004).
- Run and record the post-reboot checks (RES-P3-002).
- Refresh the capacity envelope (RES-P2-001).

### This Month

- Add the missing failure-injection tests (RES-P3-001).
- Add explicit per-service memory requests/limits.
- Document the root-LV retention/reclaim policy.

### Later / Platform Evolution

- Consider a dedicated volume for the snapshot repository sized for keep-3 + 30 days of churn.
- Add a boot-time self-verification that reports into the alerting path.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `/var/tmp/wz-migration` + `containerd` prune to the guard | Frees 20+ GiB immediately | `automation/validation/disk_guard.sh` | guard run below threshold frees and clears |
| `DefaultDependencies=no` on the proxy sockets | Breaks the ordering cycle | `config/systemd/falcon-wazuh-*-proxy.socket` | `systemd-analyze verify`; reboot test |
| Add `TimeoutStartSec`/`RuntimeMaxSec` to the backup unit | Bounds a stuck run | `config/systemd/falcon-backup.service` | unit restart after timeout |
| Add the socket check to the read-only boot check | Catches the recurrence automatically | `automation/validation/boot_check_readonly.sh` | boot check PASS with sockets up |
| Correct `VPN.md` | Stops trusting a fix that does not hold | `docs/runbooks/VPN.md:193` | doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Root-LV capacity plan (volume vs retention vs reclaim) | P1 | owner/platform | M | owner decision |
| Socket boot-order fix + automated verification | P1 | platform | S | none |
| Upload-state integrity check + bounded backup runtime | P2 | platform | M | none |
| Failure-injection suite for the observed failure classes | P3 | platform | M | none |
| Per-service memory requests/limits + envelope refresh | P2 | platform | M | PERF-P2-001 |

## Suggested Tests

- Unit: `alert_rule_lint_test.sh` for the new proxy rule; unit tests for `disk_guard.sh` reclaim order.
- Integration: a bounded disk-pressure drill on a scratch mount (reclaim + alert + exit 1); an aggregator OOM drill under a 1 GiB cap asserting `falcon_pipeline_aggregator_drop_logs_15m` and the drop rules.
- E2E: backup run with an injected offsite failure asserting the DLQ marker + alert + no success stamp; a stuck-run simulation asserting the new runtime bound.
- CI: keep `ci/validate.py` shell tests; add a static check that every socket unit's dependencies cannot form a cycle (`systemd-analyze verify` in the lab gate).
- Manual: sanctioned reboot with `boot_check_readonly.sh` recorded; offsite restore rehearsal after the state repair.

## Suggested Documentation Updates

- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: root-LV composition, reclaim policy, threshold rationale.
- `docs/runbooks/VPN.md:193`: correct the boot-order claim and the recovery step.
- `docs/runbooks/RUNTIME_AND_SCHEDULE.md`: post-reboot check as a mandatory recorded step.
- `docs/phase9/TEST_PROCEDURES.md`: add the new drills.
- `docs/phase7/runbooks/RESTORE.md`: upload-state recovery procedure.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the stale `/var/tmp/wz-migration/wazuh-stack.tar` still needed? | 21.7 GiB reclaimable | owner confirmation |
| Should the snapshot repo move to a dedicated volume? | Long-term root margin | capacity plan |
| Why did root free rise ~4.6 GiB during the 02:24-02:27 reboot (20.8 -> 25.7 GiB at 03:30)? | Understanding hidden reclaim | OpenSearch/containerd startup cleanup logs |
| Will the 68.3 GiB offsite upload finish before the 36 h offsite-stale rule fires (07:01Z)? | DR RPO | offsite log / success stamp |

## Appendix

### Failure mode inventory

| Failure mode | Detector | External dead-man's switch? | Last exercise | Evidence |
|---|---|---|---|---|
| Aggregator OOM | `falcon_pipeline_aggregator_drop_logs_15m`, restart metric | Yes (relay to independent ntfy; DO watcher) | Live 2026-10-08/09 (real); fix verified 2026-10-11 | docker inspect; journalctl -k |
| Host memory exhaustion | `Host memory pressure` rules | Yes | Real Oct 6-9 | Prometheus trend |
| Root LV exhaustion | disk guard + `Disk space low` + projection | Yes | Real, failing now | guard journal; df |
| Socket boot race | `falcon-wazuh-proxy-listeners` (new) | Yes | Real Oct 11 | journalctl -b 0 |
| Sink write rejection | sink error/discard rules + DLQ counter | Yes | Drill 2026-10-01 | decision log |
| Stuck backup run | 36 h freshness + DLQ marker only | Yes (delayed) | None | offsite log |
| Edge buffer at cap | probe buffer metric + rule | Yes | None | edge.yaml |

### Critical path resilience matrix

| Critical path | Timeout | Retry | Idempotent | DLQ | Detection | Recovery |
|---|---|---|---|---|---|---|
| Snapshot job | none | 3x/60 s | yes (named snapshot) | marker | freshness + immediate alert | re-run; keep-3 |
| Offsite upload | none | 3x backoff | delta state (fragile) | dead-letter marker | DLQ rule + 36 h stale | re-upload |
| Ingest -> aggregator -> OpenSearch | sink retry | sink retries | at-least-once (dup ratio rule) | invalid-only DLQ | drop/error rules | buffer/backlog |
| Alert delivery | relay timeouts | two paths | n/a | relay-path rule | canary + watcher | independent ntfy |
| Wazuh agent path | none | reconnect | yes | n/a | new listener rule | manual start |

### Recovery readiness

- Local snapshot restore: last rehearsal 2026-10-01 (1.47 M docs in 21 s); scheduled assertion absent (DR-P3-001).
- Offsite restore: last verified success 2026-10-09; the Oct 11 copy is still uploading.
- Config archive decrypt: key custody attested; decrypt-from-escrow not drilled (DR-P2-002).

### Chaos test plan (recommended)

1. Aggregator OOM: synthetic burst against a 1 GiB cap; assert drop metric + rule + buffer drain; bound to <=5 min.
2. Boot-order: sanctioned reboot or `systemctl stop wg-quick@wg0` + start ordering test; assert sockets bind without manual action.
3. Root-LV: scratch mount fill below threshold; assert reclaim + alert + exit 1.
4. Stuck run: SIGSTOP the offsite uploader; assert the new runtime bound and alert.
5. Offsite failure: block Spaces access; assert DLQ marker + alert + no stamp; restore.

## Findings

| ID | Severity | Title |
|---|---|---|
| RES-P1-002 | P1 | Root LV below the 20 GiB disk-guard threshold; guard failing every 15 min while the snapshot repository grows ~4.3-5.5 GiB/night |
| RES-P2-002 | P1 | Wazuh VPN proxy socket boot race is not fixed: systemd still deletes the socket jobs on boot (listeners dead 45 min after the Oct 11 reboot) |
| RES-P2-001 | P2 | Host memory/swap pressure improved but remains: ~33% available, ~4.0 GiB swap used; capacity envelope stale |
| RES-P3-001 | P3 | Failure-injection coverage still omits the failure modes that actually occurred (aggregator OOM, host memory, boot-order/socket, root-LV exhaustion) |
| RES-P3-002 | P3 | No post-reboot verification was run or recorded after the 2026-10-11 kernel-upgrade reboot; post-reboot degradations were visible only through alerts |
