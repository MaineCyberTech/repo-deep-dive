# Infrastructure, Deployment, and Environment Drift Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab profile v1.0.0, pack v1.2.1)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: falcon-build (`/home/user/falcon-build`, central) + falcon-edge-build (`/home/user/falcon-edge-build`, edge)
- Branch: main (both) · Commit SHA: falcon `8282d3f`; edge `f1c5def` (started at `45dfed0`; +5 commits mid-run, clean)
- Generated at: 2026-09-30 (audit session) · Auditor: infra/deployment subagent, read-only, no sudo
- Area code: INFRA
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/12_infra_deployment_environment_drift.md`
- Scope limitations: no root; Docker API, nftables, `/srv/falcon/secrets`, `/srv/falcon/compose-state` and the edge Pi unreadable, so those runtime claims are marked `unverified` where noted.

## Scope

Reviewed both repos (`compose/`, Dockerfile, `bootstrap/`, `config/`, `automation/`, `pins/`, `ci/`, deploy units, runbooks, port matrix) plus the live host via `live_snapshot.txt` and fresh read-only `ss`/`systemctl`/version probes. Not reviewed: Proxmox/UniFi/DO host configs, upstream service internals, Pi runtime, secret values (redaction rule §3).

## Evidence Reviewed

- `docs/architecture/PORT_PROTOCOL_MATRIX.md:3-45`; `live_snapshot.txt:4-167`; fresh `ss -tuln`, `systemctl cat`, `hostname`, version and `/srv/falcon` probes
- `compose/central/docker-compose.yml`, `compose/central/opensearch-s3.Dockerfile`, `compose/probe/docker-compose.yml`, `compose/mct/docker-compose.opencanary.yml`
- `bootstrap/{run-all,30-32,70,80,85,95-97}*.sh`; `config/nftables/falcon.nft`, `config/systemd/*`, `config/traefik/*`, `config/suricata/suricata.yaml`, `config/wireguard/wg0.conf.tpl`
- `automation/validation/{disk_guard,backup_new_services,secret_scan_history}.sh`; `automation/vpn/{test_tunnel,test_closed_mode,add_peer}.sh`; `automation/wazuh/multi-node/README.md`
- Runbooks: `docs/runbooks/{OPERATOR_START_HERE,VPN,WAZUH_INTEGRATION}.md`; `docs/phase7/runbooks/{SENSOR_SILENCE,DISK_PRESSURE,RESTORE}.md`
- Edge: `deploy/*`, `automation/validation/{onboard_lab_side,qemu_boot_smoke}.sh`, `.github/workflows/*.yml`, docs/AGENTS/README, `ledgers/gate_ledger.csv`; prior-run `findings.json`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Live `ss` vs matrix rows | live probe | Port drift | 0.0.0.0:5182 live vs UDP/51820 in matrix; 1516/1517/1518/8791/9443/21/23/3306/1433/8008/9100 absent |
| `systemctl cat` diff vs `config/systemd/*` | live vs repo | Unit drift | 15/15 repo units byte-equivalent; 10 live falcon/edge units have no repo unit file |
| `git diff 794ba31..HEAD` on prior-finding files | history | Fixed/open | Matrix, pin and phase7 runbooks unchanged since prior run |
| Fresh probes (`hostname`, `lsb_release`, `docker --version`, `/srv/falcon`) | live | Env inventory | Host `falcon`; Ubuntu 24.04.5; kernel 6.8.0-142; Docker 29.1.3; cloudflared 2026.9.1 |
| `grep` for retired paths/ports | repo | Staleness | `veth-span-b` in bootstrap/70; VPN tests dial 51820; state path bug |

## Executive Summary

The deployable surface is stronger than the documents that describe it. Compose uses digest-pinned images, per-service users for most services, healthchecks and limits, with secrets outside the repo; all 15 falcon units installed on the host match the repository exactly; rollback and update-rehearsal paths exist. The dominant risk is drift between the live system and the operating picture: the Phase-0 port matrix still says WireGuard 51820 and host `mon` (live: 5182, `falcon`) and omits 1516/1517/1518, 8791, 9443 and the OpenCanary publishes; two incident runbooks still assert "no VPN / no physical SPAN" and "no scheduled backup / no offsite copy"; three edge maintenance timers have no repo unit file; and the VPN verification scripts are stale. Fix the runbooks first (P1), then regenerate the matrix, repair the validators, and bring host-only units and tunnel config into backup coverage.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Central compose | `compose/central/docker-compose.yml` | Traefik/OS/OSD/Vector/Prom/Grafana/Redis/ntfy/ntopng/node-exporter | Implemented | Low | Digest pins, healthchecks, users 1000/65534/472 |
| MCT compose | `compose/mct/*.yml`, `mct/compose/*.yml` | OpenCanary/IRIS/Shuffle/MISP | Implemented | Medium | Honeypot publishes 21/23/3306/1433/8008/9100 |
| Dockerfile | `compose/central/opensearch-s3.Dockerfile` | repository-s3 plugin | Implemented | Low | Digest base; root only for plugin, then `USER 1000` |
| Bootstrap | `bootstrap/*.sh` | Idempotent deploy + rollback | Partial | Medium | `run-all.sh` runs stages 10/20/30/40 only |
| Runtime state | `/srv/falcon/{rendered,compose-state,backups,textfile}` | Rendered cfg, mode, backups, metrics | Live | Medium | `compose-state` root-only; non-root cannot read mode |
| Units (host-only) | `falcon-edge-{metrics,operator-cert,secrets-backup}` | Edge maintenance | Live | Medium | Unit text not in either repo |
| Edge deploy | `deploy/edge-control-plane.{service,lab.json}` | Edge control plane on lab host | Implemented | Medium | Runs from working tree; binds 0.0.0.0:9443 |
| Out-of-repo sources | Wazuh `/opt/wazuh-docker`, IRIS `/opt/iris-web`, OpenCanary, edge CP/DO watcher | SecOps + edge | Mixed | Medium | Wazuh copy committed 2026-09-30 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 4 | `opensearch-s3.Dockerfile` | One local image; no lint | Add hadolint |
| Compose | 4 | central/probe/mct compose | Default users for some images; no render test | User pins + render check |
| Terraform/OpenTofu | N/A | none | N/A undocumented | State N/A in architecture docs |
| Cloud/hosting config | 2 | `95/96/97-cloudflare*.sh` | Token/dashboard state external; not backed up | Add to backup + scope doc |
| Deploy scripts | 3 | `bootstrap/*` | `run-all.sh` incomplete; stale stage 70 | Fix run-all and stage 70 |
| Reverse proxy | 4 | `config/traefik/*` | No config lint; htpasswd inode caveat tribal | Lint + runbook note |
| Environment examples | 2 | `mct/config/profiles/*.env.example` | No central/probe env inventory | Add env inventory doc |
| Runtime validators | 3 | health/probe/span scripts | VPN tests stale; none in CI | Repair + CI-safe subset |
| Secret references | 4 | `/srv/falcon/secrets`, `env_file:` | Master `/home/user/.env` not backed up by stack | Owner-file backup (see 38) |
| Build args | 3 | none used; CI bake env | 7 repo secrets; approval blocked by plan | Document; revisit plan |
| Container users | 3 | compose `user:` | Runtime users unverified | Root-side inspect capture |
| Health/readiness | 4 | healthchecks + service probe | No CP/timer liveness | Add probes/alerts |

## Detailed Review

- **Compose/DB:** all images tag@digest or digest-only; healthchecks + limits + `no-new-privileges`; explicit `user:` on vector/prometheus/grafana/ntfy (default users elsewhere, `unverified`); `backend` internal + deliberate OpenSearch egress for R2; Redis requirepass via file secret.
- **Deploy/cloud/migrations:** `run-all.sh` stops at stage 40, stage 70 uses the retired `veth-span-b`, stage 85 continues if the new-services backup fails; tunnel state lives in Cloudflare + `/home/user/.env` (no backup entry); index rename is a manual one-off; no feature-flag or blue/green system.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INFRA-002 | Compose | central/probe/mct | Pins, limits, healthchecks | Users/render | P2 | Pin users; render check |
| INFRA-004 | Cloud/hosting | 95/96/97 scripts | Scripted tunnel/DNS | State external; unbaked | P2 | Backup + scope doc |
| INFRA-005 | Deploy scripts | `run-all.sh` vs README | Staged scripts | Incomplete entry | P2 | Fix or relabel |
| INFRA-006 | Reverse proxy | Traefik configs | TLS + auth | No lint | P3 | Lint + inode note |
| INFRA-008 | Runtime validators | validation scripts | Host-validated | Stale VPN/probe | P2 | Repair |
| INFRA-009 | Secret refs | env_file/secrets | Out-of-repo, root-owned | `.env` not backed up | P2 | Owner backup |
| INFRA-012 | Health | compose + probe | Healthchecks | Timer liveness | P3 | Probes/alerts |

## Findings

### Finding ID: INFRA-P1-001 - Incident runbooks contradict the live architecture (no VPN, no SPAN, no backups)
- Severity: P1
- Confidence: High
- Area: INFRA / runbooks & environment drift
- Evidence: `docs/phase7/runbooks/SENSOR_SILENCE.md:27-28` ("there is **no VPN**"; "there is **no physical SPAN**"); `docs/phase7/runbooks/RESTORE.md:54-56` ("no scheduled backup exists; no offsite/immutable copy"); contradicted by `docs/runbooks/VPN.md:12,23,60`, `compose/probe/docker-compose.yml:29` (`-i ens19`), `config/systemd/falcon-backup.timer`, `bootstrap/80-offsite-backup.sh`, `live_snapshot.txt:53,70`; prior LIVE-P1-006, files unchanged since
- What is happening: incident-time "known substitutions/current state" text predates the VPN, real SPAN and scheduled/offsite backups.
- Why it matters: during sensor silence or restore the operator is told these paths do not exist and may act on a wrong model.
- User / business impact: slower, wrong incident response and recovery decisions.
- Security / privacy / reliability impact: incorrect recovery assumptions can lead to unnecessary data loss.
- Recommended fix: prepend superseded notes to both runbooks (append-only), point at current VPN/backup sections.
- Suggested validation: non-root read-only walkthrough (each step works or states its role requirement).
- Owner suggestion: falcon maintainer
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior LIVE-P1-006)

### Finding ID: INFRA-P2-001 - `PORT_PROTOCOL_MATRIX.md` is materially stale vs live listeners
- Severity: P2
- Confidence: High
- Area: INFRA / documentation vs live
- Evidence: `docs/architecture/PORT_PROTOCOL_MATRIX.md:36` N-20 UDP/51820 (live `ss`/`live_snapshot.txt:74,83` = UDP 5182); rows say host `mon:` (lines 17-19,32,36-38) while live hostname is `falcon`; missing listeners 1516/1517/1518 (`docs/runbooks/WAZUH_INTEGRATION.md:29-34`), 8791 (`config/nftables/falcon.nft:31-32`), 9443 (`deploy/edge-control-plane.lab.json:2-3`), 21/23/3306/1433/8008/9100 (`compose/mct/docker-compose.opencanary.yml:27-33`); N-18 says "open-inbound override active" although EX-13 closed (`ledgers/exception_register.md:51`)
- What is happening: the exposure baseline no longer reflects the deployment; some public ports exist only in runbooks/compose.
- Why it matters: firewall/VPN incident diagnosis and exposure reviews use this matrix as truth.
- User / business impact: responders and reviewers work from an incorrect exposure list.
- Security / privacy / reliability impact: reachable honeypot/Wazuh ports are outside the exposure inventory.
- Recommended fix: regenerate from compose + nft + a live `ss` capture; add generated-at footer and superseded notes.
- Suggested validation: CI check that every compose publish has a matrix row.
- Owner suggestion: falcon maintainer
- Effort estimate: M
- Dependencies: INFRA-P1-001 (same doc pass)
- Status: still-open (prior ND-P2-004)

### Finding ID: INFRA-P2-002 - Post-architecture-change scripts are stale: VPN tests dial 51820; bootstrap/70 still uses `veth-span-b`
- Severity: P2
- Confidence: High
- Area: INFRA / deploy scripts & runtime validators
- Evidence: `automation/vpn/test_tunnel.sh:35,51,60` use `51820` (live wg0 listens on 5182: `live_snapshot.txt:74`, `bootstrap/95-wireguard.sh:84`); `bootstrap/70-probe-deploy.sh:24,31,61` creates and validates the retired `veth-span-b`; `compose/probe/docker-compose.yml:29` and `config/suricata/suricata.yaml:6,67-69` capture on `ens19`; prior ND-P2-005/006 unchanged
- What is happening: verification scripts cannot handshake or observe the current paths as written; a rebuilt host gets false first-pass assurance.
- Why it matters: the P3-G07/P9-G03 evidence chain and rebuild checks are not reproducible from the current tree.
- User / business impact: operators trust rebuild/verification results that do not exercise the live paths.
- Security / privacy / reliability impact: silent loss of tunnel/SPAN verification coverage.
- Recommended fix: parameterize the VPN port from rendered `wg0.conf`; validate Suricata on ens19 with canary/`span_mirror_check.sh`.
- Suggested validation: add dry-run modes; assert rendered port and EVE canary events.
- Owner suggestion: ops/falcon maintainer
- Effort estimate: S
- Dependencies: none
- Status: still-open (ND-P2-005 port; ND-P2-006)

### Finding ID: INFRA-P2-003 - Three edge maintenance timers are host-only; tunnel config and units are outside backup coverage
- Severity: P2
- Confidence: High (`fleet_metrics`/`renew_operator_cert`/`backup_edge_secrets` scripts in repo; runtime settings via `systemctl cat`)
- Area: INFRA / reproducibility & backup hooks
- Evidence: live `falcon-edge-{metrics,operator-cert,secrets-backup}.{service,timer}` (`live_snapshot.txt:38-40,55-57`) have no `deploy/*` unit files and were installed by an ephemeral `/tmp/opencode/lab_maintenance_timers.sh` capture; `automation/validation/backup_new_services.sh:17-31` excludes `/etc/cloudflared/config.yml` and those units; `bootstrap/80-offsite-backup.sh` covers OpenSearch only; `bootstrap/95-cloudflared.sh:30-33` token only in `/home/user/.env`; Wazuh now covered (`automation/wazuh/multi-node/README.md`)
- What is happening: rebuild/host-loss recovery for these pieces depends on memory or the owner file.
- Why it matters: recovery time and the edge "reproducible" claim.
- User / business impact: maintenance timers/tunnel must be re-authored by hand after host loss.
- Security / privacy / reliability impact: secrets-backup and cert-renewal timers may silently stop after a rebuild.
- Recommended fix: commit the three unit files + install step; extend the new-services archive with cloudflared config/units; document token custody.
- Suggested validation: restore rehearsal reproduces units + tunnel config from archive only.
- Owner suggestion: edge + ops
- Effort estimate: M
- Dependencies: none
- Status: still-open (prior ND-P2-016; ND-P2-009/010 partial)

### Finding ID: INFRA-P3-001 - `bootstrap/run-all.sh` is not "all" while README presents it as the deploy entry
- Severity: P3
- Confidence: High
- Area: INFRA / deploy scripts
- Evidence: `bootstrap/run-all.sh:5-11` (stages 10/20/30/40 only); `README.md:36-38` ("deploy ... `sudo bootstrap/run-all.sh`")
- What is happening: secrets, stacks, alerting, VPN, cloudflared and timers must be run individually.
- Why it matters: a reader following the README gets an undeployed stack.
- User / business impact: rebuild time increases; support confusion.
- Security / privacy / reliability impact: a partial deploy can look complete without the firewall/secret stages.
- Recommended fix: extend to the full ordered list or rename to `run-core-stages.sh` and update README.
- Suggested validation: README literal walk reaches dashboards + probe health on a scratch host.
- Owner suggestion: falcon maintainer
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior ND-P1-004)

### Finding ID: INFRA-P3-002 - Disk-guard unit says 5 GiB while the script threshold is 10 GiB
- Severity: P3
- Confidence: High
- Area: INFRA / runtime validators
- Evidence: `config/systemd/falcon-disk-guard.service:2` ("below 5 GiB"); `automation/validation/disk_guard.sh:14` (`THRESHOLD_KB=$((10*1024*1024))`, "raised 2026-09-30"); live unit identical to repo
- What is happening: operator-visible text is stale after the threshold change; a 5-10 GiB window correctly does nothing.
- Why it matters: the unit text is the only operator-visible description of the guard.
- User / business impact: misjudged disk state during pressure.
- Security / privacy / reliability impact: low; reclaim/alert behavior is unchanged.
- Recommended fix: update the description; single-source the threshold; add a docs check.
- Suggested validation: docs check comparing the threshold constant and unit text.
- Owner suggestion: falcon maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Prior-Run Finding Status (verified at current commits)

| Prior ID | Status | Evidence |
|---|---|---|
| ND-P2-004 port matrix stale | still-open | Matrix unchanged; 51820 vs live 5182 → INFRA-P2-001 |
| ND-P2-005 tunnel test port; companion fix | partially-fixed | Closed-mode trap fixed (decision log); port/state capture remain → INFRA-P2-002 |
| ND-P2-006 synthetic probe path | still-open | `bootstrap/70:24,31` vs `compose/probe:29` → INFRA-P2-002 |
| LIVE-P1-006 runbook drift | still-open | SENSOR_SILENCE/RESTORE unchanged → INFRA-P1-001 |
| INTG-P3-001 pin misidentifies 15140/15141 | still-open | `docs/edge/EDGE_RELEASE_PIN.md:24-27` unchanged; INTG-P3-004 (CP binds 0.0.0.0:9443) and edge adapter-doc drift also still open |
| ND-P2-009/010 outside-repo services | partially-fixed | Wazuh committed; Cloudflare token/state + DO watcher remain → INFRA-P2-003 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Operator follows stale incident runbook | High | Medium | Wrong/delayed recovery | INFRA-P1-001 | Fix runbooks this week |
| Rebuild leaves probe silently uncaptured | Medium | Medium | Blind monitoring | INFRA-P2-002 | Fix stage 70 + rehearsal |
| Host loss → tunnel/units unrecoverable | Medium | Low | Days of manual recovery | INFRA-P2-003 | Extend backups, commit units |
| Exposure review misses a public port | Medium | Medium | Unreviewed surface | INFRA-P2-001 | Regenerate matrix + CI row check |

## Recommendations

### Immediate / This Week
- Fix the runbooks, port matrix and validators (INFRA-P1-001, P2-001, P2-002).

### This Month / Later
- Commit edge units + backup coverage (INFRA-P2-003); align run-all/README/disk-guard/edge facts/CP bind; hadolint + Traefik lint later.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| "core stages only" banner | Stops assuming full deploy | `bootstrap/run-all.sh`, `README.md` | README walk |
| Fix disk-guard description | Removes 5 GiB confusion | `config/systemd/falcon-disk-guard.service` | `systemctl cat` diff |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Regenerate port matrix from compose+nft+ss | P2 | falcon | M | none |
| VPN validator repair + dry-run | P2 | ops | S | none |

## Suggested Tests

- Regression: `test_tunnel.sh` against rendered `ListenPort`; rebuild rehearsal reaches EVE canaries via ens19.
- Restore rehearsal: archive-only recovery reproduces cloudflared config + units.

## Suggested Documentation Updates

- Regenerate `docs/architecture/PORT_PROTOCOL_MATRIX.md` with generated-at footer; append superseded notes to `SENSOR_SILENCE.md`, `RESTORE.md`, `DISK_PRESSURE.md`.
- Clarify deploy scope in `README.md` + `bootstrap/run-all.sh`; update edge hardware facts; add `SOURCE_OF_TRUTH_AND_BACKUP_MAP.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the live inbound mode `closed`? | Matrix N-18 text vs EX-13 | root read of `/srv/falcon/compose-state/inbound-mode` |
| Which container users run? | Scorecard gap | root `docker inspect` capture |

## Appendix

Live listener delta vs matrix (non-root `ss`; container-internal listeners not visible): UDP 5182 (matrix says 51820); TCP 1516/1517/1518, 8791, 9443, 21/23/3306/1433/8008/9100 undocumented; 10.99.0.1:15140/15141 VPN-only proxies. Unit drift: `config/systemd/*` vs `systemctl cat` = 15/15 identical.
