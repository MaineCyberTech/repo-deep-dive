# 12_infra_deployment_environment_drift — Prompt 12 - Infrastructure, Deployment, and Environment Drift Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `12_infra_deployment_environment_drift.md` (area INFRA, prompt)

## Verification Performed

# Infrastructure, Deployment, and Environment Drift Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon @ f5cb7c9 (branch main); live lab host `falcon` (/home/user/falcon-build deployment tree)
- Generated at: 2026-10-11T04:40:00Z
- Auditor: subagent (repo-deep-dive full, area INFRA)
- Area code: INFRA
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/12_infra_deployment_environment_drift.md
- Scope limitations: read-only; no deploys, restarts, or config changes. Live checks: systemctl status/cat/list-timers, nft list, sha256 compares, docker ps/inspect, df/du, journal reads. The offsite backup was running during the audit and was not interfered with.

## Scope

Reviewed at f5cb7c9: bootstrap stages (host baseline, storage, firewall, docker, secrets, deploys, timers), config/ (nftables, docker daemon, systemd units, traefik, prometheus, vector templates), compose declarations vs running containers, environment examples and live secret-store layout, deploy/rollback scripts, backup hooks and the disk guard, and the live host state (units, timers, firewall, daemon, mounts, disk).

Not reviewed: Cloudflare/PVE/UDM consoles, the edge repository internals, VM 101/103 internals beyond what the host exposes, and anything outside the lab host.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| bootstrap/*.sh, run-all*.sh | deploy scripts | ordered deploy, rollback notes | 30 stages |
| config/nftables/falcon.nft + live /etc/nftables.conf | firewall | declared vs applied | byte-identical (sha256 f6b18722...) |
| live `nft list table inet falcon_filter` | live firewall | wg0 narrowing | per-port wg0 set applied; no blanket accept |
| config/docker/daemon.json + live daemon | runtime | logging/live-restore | identical |
| config/systemd/* vs /etc/systemd/system | units | unit drift | all present, no diffs |
| compose/central/docker-compose.yml | compose | snapshot mount/declared services | matches live (opensearch snapshot mount now /var/lib/falcon-snapshots) |
| /home/user/falcon-build git state | deployment tree | commit binding | clean, HEAD == f5cb7c9 == remote main |
| automation/validation/disk_guard.sh + journal | ops control | disk thresholds/reclaim | root threshold 20 GiB; currently failing |
| bootstrap/85-backup-job.sh + journal/metrics | backup hook | nightly backup | Oct 11 local success; offsite in progress |
| /etc/cloudflared/config.yml + public curls | tunnel | ingress | falcon/dash local file; remote-managed v13 has falcon/iris/enroll |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git -C /home/user/falcon-build rev-parse HEAD` | live | tree binding | f5cb7c9; `status --short` clean |
| GitHub API `branches/main` + actions runs | live | remote binding | remote main = f5cb7c9; validate on f5cb7c9 = success |
| sha256 /etc/nftables.conf vs repo | live | firewall drift | identical; nftables enabled+active |
| `systemctl list-units --state=failed` | live | host health | falcon-disk-guard.service FAILED (4 consecutive runs) |
| `df -k /` + `du -sh /var/lib/falcon-snapshots/opensearch` | live | disk headroom | root 88%, ~19.6 GiB free; snapshot repo 69G |
| `curl -sI` enroll/iris/soc | live | public surface | enroll /health 200; iris/soc 302 |
| systemd unit diff loop | live | unit drift | no DIFF / no MISSING |
| backup journal + offsite.log + metrics | live | backup state | local SUCCESS 03:37; offsite upload in progress |

## Executive Summary

The deployment-drift findings from the prior full run are resolved at this commit: the live tree /home/user/falcon-build is clean at f5cb7c9, which is also the GitHub remote main, and the validate workflow on that commit is green. The wg0 firewall narrowing is applied and byte-identical to the repository file, the Wazuh VPN proxy sockets are enabled and listening with a critical alert rule, the tunnel ingress (falcon/iris/enroll) answers publicly with enroll restored, the live Prometheus rules are committed, all systemd units match the repo, and the backup hook has produced local snapshots and freshness updates on Oct 10 and Oct 11 with keep-3 retention working.

One new live operational issue was found: the disk guard is failing every 15 minutes since 2026-10-11T03:45Z because the root LV free space (about 19.6 GiB) is below its 20 GiB threshold after the nightly snapshot added ~5 GiB to the relocated 69 GB snapshot repository on the root LV. The guard cannot reclaim enough (retention is already at keep-3) and alerts each run, so a monitoring unit is now permanently failed until capacity action is taken. The nightly backup's offsite leg is still uploading at capture (the one-time full re-upload caused by the PR #51 real-path fix): the last fully successful offsite run per metrics is 2026-10-09T19:01Z, so offsite RPO is ~33 h and the Oct 11 run is not yet verifiable as successful.

Recommended next actions: act on the root-LV capacity (extend the LV, lower snapshot retention/size, or move the snapshot repo), and confirm the Oct 11 offsite run completes and re-baselines the offsite RPO. No other deployment drift was found.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Deployment tree | /home/user/falcon-build | live source | clean @ f5cb7c9 == remote main | Low | 0 behind/0 ahead of remote |
| Firewall | config/nftables/falcon.nft | host firewall | applied, identical | Low | wg0 per-port set live |
| Wazuh proxies | falcon-wazuh-{agent,enroll}-proxy.socket | VPN-only tunnels | enabled, active, 2 listeners | Low | metric + critical rule live |
| Tunnel ingress | cloudflared (remote-managed v13) | public hostnames | falcon/iris/enroll answer | Low | local file lists falcon/dash only |
| Disk guard | automation/validation/disk_guard.sh | headroom control | FAILING since 03:45Z | Medium | root below 20 GiB threshold |
| Backup hook | bootstrap/85-backup-job.sh | nightly snapshot | local OK; offsite uploading | Medium | offsite RPO ~33 h at capture |
| Snapshot repo | /var/lib/falcon-snapshots/opensearch | OpenSearch snapshots | 69G on root LV | Medium | keep-3 retention active |
| Daemon config | config/docker/daemon.json | runtime | identical live | Low | live-restore on |
| Units/timers | config/systemd/* | scheduling | all match live | Low | 20+ falcon timers active |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 3 | single Dockerfile digest-pinned | plugin pin (CTR) | see CTR report |
| Compose | 4 | declared == live (drift check OK) | - | - |
| Terraform/OpenTofu | N/A | not used | - | - |
| Cloud/hosting config | 3 | tunnel v13 + API scripts | no remote-vs-repo drift check | add drift check |
| Deploy scripts | 4 | bootstrap stages; gate passes | - | - |
| Reverse proxy | 4 | Traefik + tunnel verified | - | - |
| Environment examples | 3 | .env.example 7 keys | 2 live extras (SECRET) | see SECRET report |
| Runtime validators | 4 | container drift + image pin + boot checks | - | - |
| Secret references | 3 | root-only stores | register path staleness (SECRET) | see SECRET report |
| Build args | N/A | none | - | - |
| Container users | 3 | 11/27 explicit | adopted stacks | see CTR report |
| Health/readiness/liveness | 3 | 13/27 healthchecked | adopted stacks | see CTR report |

## Detailed Review

### Item: Deployment tree binding
- Evidence: `git -C /home/user/falcon-build rev-parse HEAD` -> f5cb7c9; `status --short` empty; GitHub API branches/main -> f5cb7c9; validate run on f5cb7c9 success (2026-10-11T04:04Z).
- What it does: the tree systemd ExecStart paths and container ro-mounts resolve to.
- Current controls: clean checkout bound to remote main; CI green on the head.
- Missing controls: a read-only checkout-vs-origin drift check is still absent (container drift exists; tree drift does not).
- Recommended improvement: add a scheduled `git fetch --dry-run`/rev comparison metric.
- Suggested tests: unit test for the drift check.
- Suggested docs: docs/runbooks/RUNTIME_AND_SCHEDULE.md.

### Item: Disk guard / root LV capacity
- Evidence: journalctl falcon-disk-guard: 03:45/04:00/04:15/04:30Z "BELOW THRESHOLD: reclaiming" -> "still below threshold after reclaim - alert sent" -> exit 1; `df -k /` root_free 20,513,444 KB (19.6 GiB) vs threshold 20,971,520 KB; `du -sh /var/lib/falcon-snapshots/opensearch` = 69G; disk_guard.sh:22-24,100-160.
- What it does: reclaims EVE/snapshots/config archives and alerts when below thresholds.
- Current controls: keep-3 snapshot retention (pruned snap-20261007 at 03:37:40); alerts on failure.
- Missing controls: headroom above the 20 GiB threshold after the nightly snapshot; guard cannot reclaim snapshot data it still needs.
- Risks: root LV at 88%; if it fills, Docker volumes/images (all on root) and systemd state are affected.
- Recommended improvement: extend the root LV or move/shrink the snapshot repository; alternatively lower retention or raise the threshold with an explicit owner decision.
- Suggested tests: run disk_pressure_drill.sh; add a test asserting the guard's alert path.
- Suggested docs: docs/runbooks/CAPACITY_AND_TELEMETRY.md.

### Item: Nightly backup and offsite leg
- Evidence: falcon-backup.service activating since 03:30Z; 85-backup-job.sh log: snapshot SUCCESS 03:37:39, retention pruned 03:37:40, config archive + freshness 03:37:41, offsite attempt 03:37:42; offsite.log: "1981 file(s) total, 0 unchanged, 1981 to upload"; metrics: backup_last_success = 2026-10-11T03:37:41Z, offsite_last_success = 2026-10-09T19:01:37Z; Oct 10 offsite verification failed (wrong path, fixed by PR #51).
- What it does: nightly snapshot + encrypted config + offsite upload.
- Current controls: retry + immediate alert (PR #49); real-path fix (PR #51); reuse-only script (never creates snapshots).
- Missing controls: none material; the first run under the path fix re-uploads the full snapshot set.
- Risks: if the long catch-up fails, offsite RPO grows beyond 33 h.
- Recommended improvement: let the run complete and confirm offsite_last_success advances; consider a destination-side listing check.
- Suggested tests: offsite_backup_reuse_test.sh / offsite_upload_delta_test.sh (pass in the gate).
- Suggested docs: docs/runbooks/R2_COLD_TIER.md / WAZUH_INDEXER_BACKUP.md.

### Item: Firewall / tunnel / proxies (verification)
- Evidence: nft live == repo; wg0 per-port set; 2 proxy listeners on 10.99.0.1:15140/15141 with metric `falcon_wazuh_proxy_listeners_up 2`; public enroll/health 200; iris/soc 302; remote tunnel v13.
- Current controls: default-deny, per-port wg0 set, sockets enabled at boot, alert rule live.
- Missing controls: no automated remote-vs-repo tunnel config drift check (documented residual).
- Recommended improvement: add the drift check when the tunnel API allows read-only comparison.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INFRA-001 | Dockerfiles | opensearch-s3.Dockerfile | digest-pinned | plugin pin | P3 | see CTR |
| INFRA-002 | Compose | drift check OK | declared==live | - | - | - |
| INFRA-003 | Terraform/OpenTofu | not used | - | - | - | - |
| INFRA-004 | Cloud/hosting config | tunnel v13 + scripts | applied | remote-vs-repo check | P3 | add check |
| INFRA-005 | Deploy scripts | bootstrap stages | gate passes | - | - | - |
| INFRA-006 | Reverse proxy | Traefik + tunnel | verified live | - | - | - |
| INFRA-007 | Environment examples | .env.example | 7 keys | 2 live extras | P2 | see SECRET |
| INFRA-008 | Runtime validators | container/image/boot checks | active timers | - | - | - |
| INFRA-009 | Secret references | root-only stores | 0600 | register paths | P3 | see SECRET |
| INFRA-010 | Build args | none | - | - | - | - |
| INFRA-011 | Container users | 11/27 explicit | partial | adopted stacks | P2 | see CTR |
| INFRA-012 | Health/readiness | 13/27 | central/probe | adopted stacks | P2 | see CTR |
| INFRA-013 | Disk headroom | disk_guard journal | alerting works | root below threshold | P2 | capacity action |
| INFRA-014 | Backup/offsite | journal + metrics | local OK | offsite catch-up in progress | P2 | confirm completion |

## Findings

### INFRA-P2-005 - Disk guard failing: root LV below its 20 GiB threshold after the nightly snapshot; reclaims exhausted

- Severity: P2
- Confidence: High
- Area: INFRA
- Evidence:
  - Command: `journalctl -u falcon-disk-guard.service --since 2026-10-11` -> 03:45/04:00/04:15/04:30Z "BELOW THRESHOLD: reclaiming"; "still below threshold after reclaim - alert sent"; `Main process exited, code=exited, status=1/FAILURE`
  - Command: `df -k /` (2026-10-11T04:31Z) -> 178,999,788 KB total / 150,396,400 used / 20,513,444 free (88% used; ~19.6 GiB free) vs root threshold 20,971,520 KB
  - `automation/validation/disk_guard.sh:22-24` (ROOT_THRESHOLD_KB 20 GiB; "+~4.3 GiB/night"), `:100-160` (reclaim order: EVE, snapshots keep-3, config archives keep-3; alert+exit 1 when still below)
  - Command: `du -sh /var/lib/falcon-snapshots/opensearch` -> 69G on the root LV; retention pruned snap-20261007 at 03:37:40
  - `systemctl list-units --state=failed` -> falcon-disk-guard.service failed (fwupd units are unrelated OS-level)
- What is happening: the Oct 11 nightly snapshot (~5 GiB) pushed root free space below the guard's 20 GiB threshold; the guard's safe reclaims cannot free enough because snapshot retention is already at keep-3.
- Why it matters: the guard is a safety control and is now failing every 15 minutes; the root LV also carries Docker's images/volumes, so continued growth threatens the whole platform.
- User / business impact: persistent critical alerts (noise) and a real headroom risk on the host that runs everything.
- Security / privacy / reliability impact: a full root LV can stop Docker and with it the entire pipeline; no data loss expected while alerting works.
- Recommended fix: take a capacity action on the root LV (extend the LV, move the snapshot repository to the data LV/offsite-only, or reduce retention), or raise/retune the threshold with an owner decision; then verify the guard returns to "ok: above thresholds".
- Suggested validation: `automation/validation/disk_pressure_drill.sh`; assert the guard exits 0 and the metric `falcon_disk_guard_reclaims_total` stops incrementing hourly.
- Owner suggestion: owner/platform (capacity decision)
- Effort estimate: S-M
- Dependencies: owner decision on capacity (RAM/disk budget is already open as PERF-P2-001)
- Status: open
- Endpoint / data path: host root LV -> Docker volumes/images + snapshot repo
- Attack path: none identified (availability risk)

### INFRA-P2-006 - Nightly offsite backup in a multi-hour catch-up; offsite RPO ~33 h at capture and not yet verifiable

- Severity: P2
- Confidence: High
- Area: INFRA
- Evidence:
  - Command: `systemctl is-active falcon-backup.service` -> activating since 2026-10-11T03:30:03Z (still running at 04:31Z)
  - `bootstrap/85-backup-job.sh` journal: snapshot SUCCESS 03:37:39; retention pruned snap-20261007; freshness updated; offsite attempt 03:37:42
  - `/srv/falcon/backups/offsite.log`: 2026-10-11T03:37:44Z "opensearch upload delta: 1981 file(s) total, 0 unchanged, 1981 to upload"; 2026-10-10 run failed verification ("could not download index-78"; "hash mismatch for index.latest") before the PR #51 real-path fix
  - Metrics `/srv/falcon/textfile/falcon_metrics.prom`: `falcon_backup_offsite_last_success_timestamp_seconds 1791572497` (=2026-10-09T19:01:37Z)
- What is happening: the first nightly offsite run after the PR #51 path fix treats the whole snapshot repository as new (0 unchanged) and is re-uploading 1981 files; the previous nightly's offsite leg failed verification.
- Why it matters: offsite recovery point age is ~33 h and growing until this run completes; the run's outcome is unverified at capture.
- User / business impact: DR posture below the intended daily offsite RPO during the catch-up.
- Security / privacy / reliability impact: if the catch-up fails, offsite RPO keeps growing; local snapshots remain valid.
- Recommended fix: confirm the run completes and `falcon_backup_offsite_last_success_timestamp_seconds` advances; if it fails, investigate the upload/verify path (the fix is one commit old); consider a destination-listing check to avoid future full re-uploads.
- Suggested validation: `automation/validation/tests/offsite_backup_reuse_test.sh` and `offsite_upload_delta_test.sh` (pass in the gate); live metric check after completion.
- Owner suggestion: platform/DR
- Effort estimate: S
- Dependencies: none
- Status: open (in-progress condition; verify before closing)
- Endpoint / data path: /var/lib/falcon-snapshots/opensearch -> R2/Spaces bucket falcon-mct

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Root LV fills | P2 | Medium | High | 19.6 GiB free; 88% used; guard failing | capacity action |
| Offsite RPO grows | P2 | Medium | High | offsite last success Oct 9; catch-up running | confirm completion |
| Tunnel remote-vs-repo drift | P3 | Low | Medium | local file != remote v13 | add drift check |

## Recommendations

### Immediate / Release Blocking
- None (no outage state at capture).

### This Week
- Act on root-LV capacity and confirm the disk guard returns to green (INFRA-P2-005).
- Confirm the Oct 11 offsite run completes and the metric advances (INFRA-P2-006).

### This Month
- Add a checkout-vs-origin tree drift check and a remote-vs-repo tunnel drift check.
- Refresh the capacity envelope after the snapshot relocation (owner-gated).

### Later / Platform Evolution
- Evaluate moving the snapshot repository off the root LV entirely (data LV or offsite-only with a local cache).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Confirm offsite completion and record the metric | closes the DR uncertainty | none (observation) | metric check |
| Lower snapshot retention or raise threshold explicitly | stops 15-min alert loop | automation/validation/disk_guard.sh | guard journal |
| Record the capacity decision in the decision log | keeps owner decisions traceable | ledgers/decision_log.md | row present |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Root-LV capacity action | P2 | owner/platform | S-M | owner budget |
| Tree-vs-origin drift check | P3 | platform | S | - |
| Tunnel remote-vs-repo drift check | P3 | platform | M | CF API access |

## Suggested Tests

- Unit: guard threshold/alert path (disk_pressure_drill.sh exists).
- Integration: backup hook end-to-end incl. offsite reuse (suites pass).
- CI: the full local gate (21 checks + 50 suites) passes at f5cb7c9.
- Manual: after capacity action, confirm guard exits 0 for 24 h.

## Suggested Documentation Updates

- docs/runbooks/CAPACITY_AND_TELEMETRY.md (root-LV snapshot budget).
- docs/runbooks/RUNTIME_AND_SCHEDULE.md (tree drift check).
- docs/runbooks/WAZUH_INTEGRATION.md / VPN.md (tunnel v13 note already added by PR #54).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which capacity action will the owner choose? | decides guard threshold/retention changes | owner decision |
| How long will the 1981-file offsite catch-up take? | offsite RPO window | completion log |
| Is the local cloudflared config file expected to diverge from remote v13? | drift-check design | owner confirmation |

## Appendix

- Prior-run reconciliation: INFRA-P1-001 (wg0 narrowing) verified-fixed; INFRA-P2-001 (tree drift) verified-fixed (live tree clean @ f5cb7c9 == remote main; validate on the head is green); INFRA-P2-002 (uncommitted edge-alerts) verified-fixed (committed by PR #50; tree clean); INFRA-P2-003 (backup hook) verified-fixed for the hook/freshness (Oct 10/11 local successes, retention working) with the offsite residual filed as INFRA-P2-006; INFRA-P1-002 (proxy sockets) verified-fixed; INFRA-P1-003 (enroll) verified-fixed; INFRA-P2-004 (tunnel ingress drift) verified-fixed with the no-drift-check residual.
- Live capture timestamp: 2026-10-11T04:31Z.
- The 2 commits the live local main had above the last-fetched origin/main (3c11752, f5cb7c9) are on remote main (verified via API); the local ref was simply stale.

## Findings

| ID | Severity | Title |
|---|---|---|
| INFRA-P2-005 | P2 | Disk guard failing: root LV below its 20 GiB threshold after the nightly snapshot; reclaims exhausted |
| INFRA-P2-006 | P2 | Nightly offsite backup in a multi-hour catch-up; offsite RPO ~33 h at capture and not yet verifiable |
