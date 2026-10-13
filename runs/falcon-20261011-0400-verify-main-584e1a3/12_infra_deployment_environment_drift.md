# 12_infra_deployment_environment_drift — Prompt 12 - Infrastructure, Deployment, and Environment Drift Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `12_infra_deployment_environment_drift.md` (area INFRA, prompt)

## Verification Performed

# Infrastructure, Deployment, and Environment Drift Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon @ 08e20d1 (branch main); live lab host `falcon` (/home/user/falcon-build deployment tree)
- Generated at: 2026-10-09T21:44:07Z
- Auditor: subagent (repo-deep-dive full, area INFRA)
- Area code: INFRA
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/12_infra_deployment_environment_drift.md
- Scope limitations: read-only; no deploys, restarts, or config changes. Live checks: systemctl status/cat, nft/iptables lists, docker ps/inspect/info, file hashes, journal reads.

## Scope

Reviewed: bootstrap stages (host baseline, storage, firewall, docker, secrets, deploys, timers), config/ (nftables, docker, systemd, traefik, prometheus, vector templates), compose declarations vs the running containers, environment examples and the live secret-store layout, deploy/rollback scripts, backup hooks, and the live host state (units, timers, firewall, daemon, mounts).

Not reviewed: Cloudflare/PVE/UDM consoles, the edge repository internals, and anything outside the lab host.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| bootstrap/*.sh, run-all*.sh | deploy scripts | ordered deploy, rollback notes | 30 files; stage list documented |
| config/nftables/falcon.nft | firewall | declared default-deny + wg0 set | narrowed SEC-P1-002 set |
| /etc/nftables.conf + live nft | live firewall | applied state | blanket wg0 accept still live |
| bootstrap/31-docker-user-firewall.sh + live iptables | firewall | Docker DNAT allowlist | live matches declared |
| config/systemd/* | units/timers | scheduled jobs | all installed; contents identical |
| config/docker/daemon.json + live daemon | runtime | logging/live-restore | identical |
| compose/central, compose/probe + live inspect | containers | declared vs running | 0 drift; live mounts use the live tree |
| /home/user/falcon-build (git) | deployment tree | source binding | 6e4fccd, behind 22 / ahead 2 vs origin/main 08e20d1 |
| CI runs 278-280 | CI | gate status of both lineages | main green; ops branch fails evidence-index |
| /srv/falcon/rendered/vector-*.yaml | rendered config | secret-rendered runtime config | matches templates (masked) |
| falcon-backup service/journal | backup hook | daily recovery path | failed Oct 8 + Oct 9 |
| docs/architecture/PORT_PROTOCOL_MATRIX.md | docs | ports/paths/users matrix | matches live except wg0 addendum |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Live deployment tree vs origin/main | `git -C /home/user/falcon-build rev-parse HEAD; branch -vv` | 6e4fccd; main [origin/main: ahead 2, behind 22]; origin/main=08e20d1 |
| Lineage CI status | GitHub API runs | validate main @08e20d1 success (1.4 min); ops branch c13a4160 runs 279/280 FAIL (evidence index) |
| Firewall file binding | `sha256sum /etc/nftables.conf config/nftables/falcon.nft` | 8a7f5b94... vs f6b18722... (differ); live file has blanket wg0 rule |
| Live firewall table | `sudo nft list table inet falcon_filter` | policy drop; blanket `iifname wg0 accept`; no per-port wg0 rules |
| DOCKER-USER | `sudo iptables -S DOCKER-USER` | matches bootstrap/31 (mgmt/admin RETURN, RFC1918 5140/5141, 15140, final DROP) |
| Docker daemon | `sudo cat /etc/docker/daemon.json; docker info` | identical; live-restore=true; json-file 20m x5 |
| systemd units | diff config/systemd/* vs /etc/systemd/system/* | all installed; contents identical (one blank-line difference) |
| Rendered vector configs | diff templates vs /srv/falcon/rendered (secret values masked) | no structural difference |
| Backup hook | `systemctl status falcon-backup; journalctl` | failed 2026-10-08 and 2026-10-09; last success 10-07 |
| Live mounts | `docker inspect` prometheus/opensearch/vector | mount the live tree (/home/user/falcon-build) and live snapshot path |
| Env examples | .env.example vs live .env | see SECRET report (drift found there) |

## Executive Summary

Strengths: the deploy surface is unusually well-bound for a lab — every installed systemd unit matches the repo, the Docker daemon config matches exactly, the DOCKER-USER allowlist matches the script, rendered Vector configs match their templates, the port matrix reconciles with live listeners, and the scheduled container-drift check reports zero drift. Terraform/OpenTofu is not used (N/A), and rollback paths are documented per script.

Risks: three live-vs-declared drifts matter. (1) The declared wg0 firewall narrowing (SEC-P1-002) is not applied: /etc/nftables.conf and the live kernel table still contain the blanket `iifname wg0 accept`, so all 8 VPN peers retain blanket access to host services despite the matrix claiming the fix is applied. (2) The deployment tree is not the audited commit: it is 22 commits behind origin/main (missing OBS-P0-001, API-P1-001, FINAL-P1-001, HYG-P1-001) and 2 local commits ahead; its own CI fails on the evidence-index check, and the snapshot-path change exists only there. (3) Live Prometheus alert rules exist only as uncommitted working-tree edits (+112/-7). The daily backup hook has also failed for two consecutive runs (freshness not updated since 10-07).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Deploy tree | /home/user/falcon-build | source for units/scripts/mounts | 6e4fccd (behind 22/ahead 2) | high | not the audited commit |
| Firewall declared | config/nftables/falcon.nft | default-deny + wg0 set | narrowed set | - | merged SEC-P1-002 |
| Firewall applied | /etc/nftables.conf | live rules | blanket wg0 accept | high | stale vs declared |
| DOCKER-USER | live iptables | DNAT allowlist | matches declared | low | good |
| Daemon | /etc/docker/daemon.json | logging/live-restore | matches | low | good |
| systemd units | /etc/systemd/system/falcon-* | timers/jobs | match repo | low | good |
| Rendered configs | /srv/falcon/rendered | vector configs | match templates | low | good |
| Prometheus rules | live edge-alerts.yaml | alerting | uncommitted +112/-7 | medium | only copy |
| Backup hook | falcon-backup.service | daily snapshot/offsite | failed Oct 8-9 | high | freshness stale |
| Snapshot path | /var/lib/falcon-snapshots (live) vs /srv/falcon/backups (08e20d1) | OpenSearch repo | differs by lineage | medium | regression risk on deploy |
| Terraform/OpenTofu | - | - | not used | - | N/A |
| Rollback | bootstrap/rollback-firewall.sh, compose comments | recovery | present | low | no blue/green (single host) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 4 | see CTR report | plugin pin | CTR-P3-002 |
| Compose | 4 | declared=live (0 drift) | adopted stacks (CTR) | CTR-P2-001 |
| Terraform/OpenTofu | N/A | none in tree | none | n/a |
| Cloud/hosting config | 4 | bootstrap/95-97, cloudflared unit | live tree behind | merge live commits |
| Deploy scripts | 3 | bootstrap ordered, idempotent, rollback notes | live tree not at main; firewall not re-applied | INFRA-P1-001/P2-001 |
| Reverse proxy | 4 | traefik config mounted ro; matrix reconciled | none | keep |
| Environment examples | 3 | .env.example 7 keys | live 9 keys (SECRET) | reconcile |
| Runtime validators | 4 | post_reboot_verify, container_drift, port_matrix | validators miss wg0 file drift | add file-binding assertion |
| Secret references | 4 | /srv/falcon/secrets, no literals | env_file whole-file (SECRET) | per-key secrets |
| Build args | N/A | none | none | n/a |
| Container users | 3 | explicit on central/probe | adopted stacks (CTR) | CTR-P2-001 |
| Health/readiness/liveness | 3 | central/probe all; 13/27 live | adopted stacks | CTR-P2-001 |

## Detailed Review

### Item: Live firewall vs declared wg0 trust set

- Evidence: config/nftables/falcon.nft:24-33; live nft output; /etc/nftables.conf:24; PORT_PROTOCOL_MATRIX.md N-24 addendum; post_reboot_verify.sh:25-35.
- What it does: declared set allows only 9443, 15140/15141, 514/1514/1515, 514/2055 over wg0.
- Live: blanket accept; 8 peers.
- Missing controls: no assertion that /etc/nftables.conf equals the repo file; post_reboot_verify only checks policy drop.

### Item: Deployment tree binding

- Evidence: git state; CI runs; systemd ExecStart; container mounts.
- What it does: systemd units and ro mounts execute config/scripts from /home/user/falcon-build.
- Live: 6e4fccd lineage; missing verified-fixed remediations; CI failing on that lineage.
- Missing controls: no checkout-vs-origin drift check (container drift exists; tree drift does not).

### Item: Live alert rules

- Evidence: git status/diff; docker inspect mount; grep at 08e20d1.
- Live: uncommitted +112/-7 in config/prometheus/edge-alerts.yaml.

### Item: Backup hook

- Evidence: systemctl/journal; /srv/falcon/compose-state listing.
- Live: failed Oct 8 + 9; last success Oct 7; marker not present now.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INFRA-001 | Dockerfiles | CTR report | digest-pinned | plugin pin | P3 | CTR-P3-002 |
| INFRA-002 | Compose | live drift check | 0 drift | adopted hardening | P2 | CTR-P2-001 |
| INFRA-003 | Terraform/OpenTofu | none | n/a | n/a | - | n/a |
| INFRA-004 | Cloud/hosting config | bootstrap/95-97 | as code | live tree behind | P2 | merge |
| INFRA-005 | Deploy scripts | bootstrap | ordered/idempotent | firewall not applied; tree not main | P1/P2 | re-run 30; land commits |
| INFRA-006 | Reverse proxy | config/traefik | mounted ro | none | - | keep |
| INFRA-007 | Environment examples | .env.example | 7 keys | live drift | P2 | SECRET-P2-002 |
| INFRA-008 | Runtime validators | post_reboot_verify | policy+chain checks | no wg0/file binding | P1 | add assertion |
| INFRA-009 | Secret references | /srv/falcon/secrets | 0600 files | env_file | P2 | SECRET |
| INFRA-010 | Build args | none | n/a | n/a | - | n/a |
| INFRA-011 | Container users | live | central/probe explicit | adopted stacks | P2 | CTR-P2-001 |
| INFRA-012 | Health/readiness/liveness | live | 13/27 | adopted stacks | P2 | CTR-P2-001 |

## Findings

### INFRA-P1-001 - Declared wg0 firewall narrowing (SEC-P1-002) is not applied; every VPN peer still has blanket access

- Severity: P1
- Confidence: High
- Area: INFRA
- Evidence: live `nft list table inet falcon_filter` 2026-10-09 (blanket `iifname "wg0" accept`); `grep wg0 /etc/nftables.conf` -> line 24; /etc/nftables.conf sha256 8a7f5b941a26963f4b1041a7f65391aefa474b8ae6a304fc3d218072b3b78cdf vs config/nftables/falcon.nft sha256 f6b187220587da2a84538b8d44f0a4fdddcc0ebc268c01b1f4ee18f27b182c9e (same hash at 6e4fccd and 08e20d1); `sudo wg show wg0` (8 peers, current handshakes); PORT_PROTOCOL_MATRIX.md:104-126 (N-24 addendum claims the narrowing is applied); post_reboot_verify.sh:25-35 (only asserts policy drop + DOCKER-USER DROP).
- What is happening: the repo (and the live tree) declare per-port wg0 allows, but the host was never re-applied since commit 7bb6187; nftables.service is enabled+active so the stale file persists across reboots. Every WireGuard peer (sensor + client endpoints) can reach all host listeners reachable over wg0, including SSH 22 (password auth, lab exception EX-01), the 9443 control plane, and the 1516/1517/1518 Wazuh paths.
- Why it matters: the documented trust-set fix is not in effect; a compromised or malicious enrolled peer has a broad host foothold instead of the intended four services.
- User / business impact: lab-only today, but it invalidates the SEC-P1-002 closure claim and the N-24 addendum's "verified" language.
- Security / privacy / reliability impact: lateral movement from any tunnel peer; SSH brute-force path.
- Recommended fix: re-run `sudo bootstrap/30-firewall.sh` (installs config/nftables/falcon.nft and reloads; rollback per script), then verify the per-port rules; add a live assertion comparing the applied wg0 rules to the declared set.
- Suggested validation: `nft list chain inet falcon_filter input | grep wg0` shows only the four per-port rules; negative test from a peer to a non-allowed port is refused.
- Owner suggestion: owner/platform (root action).
- Effort estimate: S
- Dependencies: maintenance window (firewall reload); rollback script available.
- Status: open (repo SEC-P1-002 declared fixed at config level, not applied live)
- Attack path: compromised VPN endpoint -> wg0 blanket accept -> host SSH/control-plane/enrollment services.

### INFRA-P2-001 - Live deployment tree is not the audited commit: 22 behind origin/main, 2 ahead, and its own CI fails

- Severity: P2
- Confidence: High
- Area: INFRA
- Evidence: `git -C /home/user/falcon-build rev-parse HEAD` -> 6e4fccd; `branch -vv` -> main [origin/main: ahead 2, behind 22]; origin/main = 08e20d1; `git diff 6e4fccd..08e20d1 --stat` (bootstrap/90-alerting.sh +20 OBS-P0-001 rules, automation/validation/restore_assertion.sh +115, ci/validate.py +54 with check_restore_assertion absent at 6e4fccd); config/systemd/falcon-container-drift.service:14 ExecStart=/home/user/falcon-build/...; `docker inspect falcon-central-prometheus-1` mounts the live tree; CI run 37986933263 (ops c13a4160) FAIL evidence index cross-check (6 meta files without index rows); compose/central/docker-compose.yml:78 snapshot mount differs between the trees.
- What is happening: the host executes scripts, unit files and config mounts from a checkout that is not the audited commit and carries a divergent local lineage. It lacks verified-fixed remediations (OBS-P0-001 textfile freshness rules: 0 vs 3 occurrences in bootstrap/90-alerting.sh; FINAL-P1-001 restore assertion: 0 vs 2 occurrences in ci/validate.py) and fails the repository's own evidence-index gate.
- Why it matters: the audit target cannot attest to the deployed bytes; a deploy from the audited commit would also revert the snapshot-repo relocation (mount path changes back to /srv/falcon/backups/opensearch on the data LV).
- User / business impact: monitoring/recovery fixes claimed in the follow-up register are not in effect on the host.
- Security / privacy / reliability impact: observability and release-gate coverage gaps; configuration regression risk on next deploy.
- Recommended fix: land the live commits (PR #49 lineage), update the host tree to origin/main, and add a read-only checkout-vs-origin drift check (mirroring the container drift check) to the timer set.
- Suggested validation: `git -C /home/user/falcon-build status --porcelain` empty and HEAD == origin/main; CI green on main; the new drift metric reports 0.
- Owner suggestion: owner/platform.
- Effort estimate: S-M
- Dependencies: PR #49 merge; index rows for the 6 evidence files.
- Status: open
- Attack path: none identified (configuration/recovery correctness).

### INFRA-P2-002 - Live Prometheus alert rules exist only as uncommitted working-tree changes

- Severity: P2
- Confidence: High
- Area: INFRA
- Evidence: `git -C /home/user/falcon-build status --short` -> ' M config/prometheus/edge-alerts.yaml'; `git diff --stat` -> 112 insertions(+), 7 deletions(-); `docker inspect falcon-central-prometheus-1` mounts /home/user/falcon-build/config/prometheus/edge-alerts.yaml:ro; `grep -c falcon_edge_inventory_collector_last_run_timestamp` -> 0 at 08e20d1, 3 live; untracked compose/central/docker-compose.yml.bak-edge-rules and config/prometheus/prometheus.yml.bak-edge-rules.
- What is happening: the live alert set (OBS-P2-002 gating plus new edge sensor/capture/A-B slot alerts dated 2026-10-09) is not committed anywhere; the single host's working tree is the only copy.
- Why it matters: host loss or a fresh deploy from main silently drops the rules; the audit at 08e20d1 cannot reproduce live alert semantics.
- Recommended fix: commit the changes (or capture them as a patch artifact) and rebind the live mount to a commit; remove the .bak leftovers.
- Suggested validation: `git status` clean; a re-render/redeploy reproduces the live rule file byte-for-byte.
- Owner suggestion: owner/platform.
- Effort estimate: S
- Dependencies: none.
- Status: open
- Attack path: none identified (alerting integrity).

### INFRA-P2-003 - Daily backup hook has failed for two consecutive runs and has not updated snapshot freshness

- Severity: P2
- Confidence: High
- Area: INFRA
- Evidence: `systemctl status falcon-backup.service` failed since 2026-10-09 03:30:16Z ('snapshot failed (state=); not updating freshness'; 'incomplete run (rc=1); wrote marker'); `journalctl -u falcon-backup` shows Oct 5-7 success, Oct 8 and Oct 9 snapshot failures; `ls /srv/falcon/compose-state/` currently shows only inbound-mode (the falcon-backup.aborted marker is not present); falcon-backup.timer next run 2026-10-10 03:30Z.
- What is happening: the daily snapshot step failed twice around the data-LV watermark incident; the capacity relocation that addresses it exists only in the live lineage (INFRA-P2-001). Recovery point age is now >48h.
- Why it matters: the backup path is part of the release gate; a stale snapshot weakens the recovery claim verified by FINAL-P1-001.
- Recommended fix: confirm the relocated snapshot repository, run the backup job, verify a fresh snapshot + offsite sync, and ensure the aborted marker surfaces on the next run; merge the relocation.
- Suggested validation: falcon-backup.service succeeds and snapshot freshness metric updates; restore assertion still passes.
- Owner suggestion: owner/platform.
- Effort estimate: S-M
- Dependencies: INFRA-P2-001 merge; OpenSearch health.
- Status: open
- Attack path: none identified (recovery capability).

## Prior-Run Comparison

- INFRA-P2-001 (generated/derived trees not bound to HEAD by an automated drift gate): verified-fixed at 08e20d1. Evidence: review-package is untracked by design (REPOSITORY.md:35-59, HYG-P1-001), evidence tree bound by check_generated_drift (INV-P2-001), SBOM set bound by sbom_hashes (HYG-P2-001), closeout/digest bound by check_publication_equality + check_digest_binding; the full gate passes. No current finding carried forward.
- The new INFRA findings are live-environment drifts (firewall, deployment tree, uncommitted rules, backup hook) that the prior run did not capture.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| VPN peer blanket host access | High | Medium | High | live nft wg0 | INFRA-P1-001 |
| Deployed bytes != audited commit | Medium | High | Medium | git state + CI fail | INFRA-P2-001 |
| Alert rules lost on redeploy/host loss | Medium | Medium | Medium | uncommitted diff | INFRA-P2-002 |
| Stale recovery point | Medium | Medium | High | backup failed | INFRA-P2-003 |
| Firewall regression at reboot | Medium | High | High | stale /etc/nftables.conf persists | INFRA-P1-001 |

## Recommendations

### Immediate / Release Blocking
- Re-apply the declared firewall ruleset (bootstrap/30-firewall.sh) and verify the per-port wg0 set.

### This Week
- Land the live commits and update the deployment tree to origin/main; add the checkout drift check.
- Commit the live alert-rule changes; verify a fresh backup snapshot.

### This Month
- Add the firewall file-binding assertion to post_reboot_verify or the drift timer.
- Remove the .bak leftovers; refresh the port matrix N-24 evidence with a live re-capture.

### Later / Platform Evolution
- A small "environment binding" gate (checkout commit, unit hashes, firewall hash, rendered configs) exported as metrics would close this class.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Re-run bootstrap/30-firewall.sh | closes the blanket wg0 accept | config/nftables/falcon.nft -> /etc/nftables.conf | nft list wg0 rules |
| Commit edge-alerts.yaml | ends single-copy config | live tree | git status |
| Run falcon-backup manually | restores freshness | bootstrap/85-backup-job.sh | service success + metric |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Firewall apply + assertion | P1 | owner | S | window |
| Tree rebind to main + drift check | P2 | platform | S-M | PR #49 |
| Commit live alert rules | P2 | owner | S | none |
| Backup recovery run | P2 | owner | S | capacity fix |

## Suggested Tests

- Add a test that renders/composes the firewall file and compares it byte-for-byte with /etc/nftables.conf (root-marked, live).
- Extend container_drift_check with a checkout-drift metric (HEAD vs origin/main, dirty count).
- Add a test asserting the live Prometheus rule file hash equals a committed hash.

## Suggested Documentation Updates

- docs/architecture/PORT_PROTOCOL_MATRIX.md: re-verify and re-capture the N-24 addendum after the apply.
- docs/runbooks/RUNTIME_AND_SCHEDULE.md: record the deployment-tree binding expectation.
- REPOSITORY.md: document the live-tree vs repo-main policy and the drift check.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| When will bootstrap/30-firewall.sh be re-run? | the top live security drift | owner schedule |
| Is the live tree intentionally ahead of main? | determines merge vs rebase strategy | owner decision |
| Will PR #49 merge with the evidence-index rows fixed? | restores CI green on the live lineage | PR update + run |

## Limitations

- One-shot live captures; no reboot/reload was performed to test persistence behavior beyond reading nftables.service state.
- CI conclusions come from the GitHub API (read-only); fork-PR jobs are billing-blocked and were not exercised.
- The edge repository and consoles are out of scope.

## Appendix

Live firewall (2026-10-09):

```
chain input {
  type filter hook input priority filter; policy drop;
  ...
  iifname "wg0" accept comment "authenticated WireGuard tunnel traffic (probe telemetry)"
  ...
  counter packets 231140 bytes 7931728 drop comment "denied inbound (default deny)"
}
```

Declared (config/nftables/falcon.nft:24-33): per-port wg0 allows for 9443, 15140/15141, 514/1514/1515, 514/2055.

## Findings

| ID | Severity | Title |
|---|---|---|
| INFRA-P1-001 | P1 | Declared wg0 firewall narrowing (SEC-P1-002) is not applied; every VPN peer still has blanket access |
| INFRA-P2-001 | P2 | Live deployment tree is not the audited commit: 22 behind origin/main, 2 ahead, and its own CI fails |
| INFRA-P2-002 | P2 | Live Prometheus alert rules exist only as uncommitted working-tree changes |
| INFRA-P2-003 | P2 | Daily backup hook has failed for two consecutive runs and has not updated snapshot freshness |
