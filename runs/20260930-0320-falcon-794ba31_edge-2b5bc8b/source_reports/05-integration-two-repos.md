# 05 — Integration audit: `falcon-build` ↔ `falcon-edge-build` (two-repo interface)

- **Date/window:** 2026-09-30, ~03:05–03:35 UTC (all observations are from that window; the live
  edge host was mid-hard-reset-endurance at the time — see §2.5).
- **Scope:** the pairing pin, the actual coupling between the two programs and the shared host, the
  edge program's additive-only obligation, joint failure modes, and the runbook/ownership boundary.
- **Method (read-only):** files/git inspected in both repos; live host state read via `systemctl`,
  `wg`, `nft`, `ss`, Docker (read-only), Prometheus/Grafana DB queries (`mode=ro`), journal reads,
  and SSH to the sensor. Privileged reads used the documented owner-authorised `sudo` stdin
  mechanism (`/home/user/.env` key `sudo`); **no credential value was printed, logged, or
  included below**. No repository writes, no commits, no service/container changes, no mutating
  scripts were run by this audit.

## 1. Executive summary

1. **The pairing pin is stale and partly inaccurate.** The pin
   (`/home/user/falcon-build/docs/edge/EDGE_RELEASE_PIN.md`, falcon commit `0aa7e7c`, 01:12:14Z)
   records edge manifest SHA-256 `dffcbbb7…` / commit `35f0793c…` / lab6 SBOM. The edge delivery
   manifest was regenerated **7 minutes later** (`9c1021e9…`, commit `14e7c70d…`, lab7 SBOM) and
   **the old manifest file was overwritten in place under the same filename** — the digest the pin
   names no longer exists anywhere on disk. The edge HEAD has since moved to `2b5bc8b` (32 commits
   past the pin's release commit).
2. **One pin claim is factually wrong in both directions:** the pin says the sensor's WireGuard
   peer is "persisted in `config/wireguard/wg0.conf.tpl` and the live `wg0.conf` — falcon commit
   `36ca988`". In reality: (a) the **repo template was never updated** (no falcon commit ever added
   the edge peer to it); (b) `36ca988` changed only evidence/ledgers, not config; and (c) the live
   `/etc/wireguard/wg0.conf` was last written by the **edge program's own onboarding script** on
   2026-09-29 20:02:38Z (six in-place rewrites, backups kept), not by falcon at 00:59.
   Consequence: a re-run of `bootstrap/95-wireguard.sh` (which renders the template over the live
   file) **silently drops the edge tunnel** — exactly the R-30 failure class the lab warns about.
3. **The live sensor facts in the pin are otherwise correct:** tunnel `10.99.0.30` is up (endpoint
   `10.11.12.158:51820`, key matches the lab5 baked key), sensor `fes_b9f5c03d58713121659f1796` is
   `ACTIVE` with ~30 s heartbeats, the Pi runs image `2026.09.29-lab5`, and the edge control plane
   runs on the lab host at `10.99.0.1:9443` (mTLS, healthz OK).
4. **Additive rule: mostly respected, with one boundary deviation.** The exporter (own timer + own
   `.prom` file) and the alert-rules *non*-deployment are doctrinally clean; the **Grafana dashboard
   was written by the edge program into falcon's repository working tree** (`config/grafana/
   dashboards/edge-fleet-overview.json`) at 01:11:51Z — 23 seconds before the pin commit claimed
   "the edge program never writes into this repository". Falcon later adopted the file into git
   (`cf7f5c4`, 02:49), so the edge rollback note ("remove the file") is now stale.
5. **Joint monitoring holes:** edge heartbeat/certificate/queue conditions have **no deployed alert
   rule** (the edge rule file exists but is deliberately undeployed; falcon has no edge rule in its
   live 30-rule set); falcon does not probe the edge control plane (`9443`) or the exporter file's
   freshness; the only live cross-check is the per-peer WireGuard stale rule (24 h threshold) plus
   the Grafana dashboard for humans.
6. **Version/reproducibility gaps:** the live control plane and exporter execute **code directly
   from the edge repo working tree** (no pinned copy/version); the `falcon-edge-*` systemd units
   exist **only on the host** (in neither repo); the release manifest is unversioned in name and
   already 21 commits behind the edge HEAD; both repos are ahead of their `origin/main` refs (6 and
   23 commits), so the "private remote" state is not the released state.
7. **Backup/offsite split:** edge CA, signing seed and control-plane DB are backed up **only
   locally** (daily, keep 7, inside the delivery dir), and the falcon offsite job does not cover
   them. Host loss = edge fleet PKI loss. The signed release manifest also digests a **secrets
   backup archive** that sits in the same delivery directory.

## 2. Method and environment snapshot

### 2.1 Repos and refs at observation time

| Repo | HEAD | `origin/main` | Notes |
|---|---|---|---|
| `/home/user/falcon-build` | `794ba317…` (publication) | `79dabe21…` | 6 commits ahead of origin ref; pin file unchanged since `0aa7e7c` |
| `/home/user/falcon-edge-build` | `2b5bc8b` (phase7 update-drill pre-flight, 03:29:43Z) | `0348fa1f…` | 23 commits ahead of origin ref; HEAD **moved during the audit** (`cfaf09d` → `ced99b3` → `2b5bc8b`) |

### 2.2 Live lab host facts used

- `wg0` 10.99.0.1/24, UDP 5182; peers `.2` netns test, `.10` do-server, `.20` samsung, `.21/.22`
  desktops, `.30` edge-sensor (endpoint `10.11.12.158:51820`, latest handshake ≤2 min in-window).
- `edge-control-plane.service`: active since 00:51:05Z, TLS 1.3, cert CN `falcon.lab` (issued by
  "Falcon Edge Lab CA"), healthz `{"status":"ok","version":"0.1.0"}`; 21.5 MB RSS / 256 MB cap.
- `falcon-edge-metrics.timer` every 5 min → `/srv/falcon/textfile/falcon_edge_metrics.prom`
  (8.9 KB, 61 `falcon_edge_*` series, mtime ≤5 min); node-exporter textfile collector
  `node_textfile_scrape_error = 0`; Prometheus `up{job="node"} = 1`; dashboard resource
  `falcon-edge-fleet` present (edge evidence verified via the Grafana API; file content hash
  matches the falcon repo copy).
- Sensor PI (SSH, read-only): host `falcon-sensor-01`, image `2026.09.29-lab5`
  (`baseImageSha256 49fafba6…`), agent + bootstrap + kismet units active, update path unit
  waiting, **no Wazuh agent** (`wazuh-agent` inactive/absent), `/` 12 % used.
- Lab host resources: root LV **82 %** used (31 GiB free), `/srv/falcon` 61 %, RAM 9.6/17 GiB, swap
  4.7 GiB used.

### 2.3 Secrets handling

- Edge control-plane secrets: `/home/user/falcon-edge-secrets` (`0700`, user-owned) — CA, server,
  operator and 9 sensor certs, signing seed, SQLite DB, NDJSON ingest spool.
- PEM expiry read out (no key material): CA 2036, server cert 2027-06-29, operator cert
  2026-10-29 (daily renewal timer), live sensor cert 2026-10-30 (30-day lab lifetime).
- Lab VPN secrets `/srv/falcon/secrets/wireguard` (`0700`, root) — same WG peer key material the
  edge onboarding writes into the live config path (public keys only mirrored in evidence).

### 2.4 Documents reviewed

Falcon: `AGENTS.md`, `REPOSITORY.md`, `docs/edge/EDGE_RELEASE_PIN.md`, `docs/runbooks/VPN.md`,
`docs/runbooks/OPERATOR_START_HERE.md`, `docs/phase9/ALERT_CATALOGUE.yaml`,
`bootstrap/95-wireguard.sh`, `bootstrap/90-alerting.sh`, `bootstrap/85-backup-job.sh`,
`bootstrap/80-offsite-backup.sh`, `automation/validation/backup_new_services.sh`,
`automation/validation/export_monitor_metrics.sh`, `automation/validation/service_probe.sh`.
Edge: `AGENTS.md`, `REPOSITORY.md`, `ledgers/{decision_log,gate_ledger,contradiction_ledger}.md`,
`docs/phase0/OWNER_DECISIONS.json`, `docs/phase8/CLOSEOUT.md`, `closeout/OWNER_ACTIONS.md`,
`automation/validation/{onboard_lab_side.sh,deploy_edge_alert_rules.sh,backup_edge_secrets.py,
build_release_manifest.py}`, `deploy/edge-control-plane.service`, P8/P10 evidence captures.

### 2.5 Active mutating activity during the audit (observed, not performed by me)

`p9_hard_reset_endurance.sh 10` (edge repo, PID 720153, started 02:38:47Z, still running) was
force-rebooting the live Pi throughout the window (confirmed in the Pi's journal:
`sudo … reboot -f` at 04:27 sensor-clock; uptime 0 min). Tunnel/agent recovered after each reboot,
but all live sensor figures above are snapshots taken mid-drill.

## 3. Pin check results

### 3.1 Claims vs reality

| # | Pin claim | Observed reality | Verdict |
|---|---|---|---|
| 3.1 | Edge repo `https://github.com/MaineCyberTech/falcon-edge` (private) | `origin` matches exactly; but local is 23 commits ahead of `origin/main` (`0348fa1f…`); no network fetch attempted | **URL OK; publication state unverified/stale** |
| 3.2 | Manifest `falcon-edge-release-manifest-20260930.json` SHA-256 `dffcbbb7…` | Current file SHA-256 `9c1021e9…`. `dffcbbb7…` is recorded only in edge evidence; the file was **overwritten in place** at 01:19:54Z (same name, new content) | **FAIL (stale/overwritten)** |
| 3.3 | Release commit `35f0793c…` | Exists (2026-09-30 00:20:52Z, "ledger: fix D-007 evidence reference"); current manifest names `14e7c70d…`; HEAD is `2b5bc8b` (32 commits later) | **FAIL (stale)** |
| 3.4 | SBOM `falcon-edge-sensor-2026.09.29-lab6-sbom.cdx.json` SHA-256 `36db1125…` | File exists and hash matches, but it is no longer the manifest's SBOM (current: lab7 `e137ad48…`) | **Stale (was valid for the 00:23 manifest)** |
| 3.5 | Signature ed25519, keyId `5ea52faf9cf6ee97` | Derived public key from `/home/user/falcon-edge-secrets/signing.seed`; keyId matches; current manifest signature **VALID**; all 31 listed artifact hashes verify | **OK** |
| 3.6 | Sensor image artifact `…lab5-arm64.img.xz` | File exists (`8fad7710…`); live card runs lab5 (verified `/etc/falcon-edge-image.json`) and its baked WG key matches the live peer. But the current release artifact set is **lab7** ("use lab7 for any future reflash", OWNER_ACTIONS) | **Misleading (running ≠ released artifact)** |
| 3.7 | Live state: tunnel 10.99.0.30, sensor `fes_b9f5c03d58713121659f1796`, LAN 10.11.12.158, lab5 image | All verified live (handshake fresh; DB `ACTIVE`; heartbeat age ~30 s; peer key = lab5 baked key) | **OK** |
| 3.8 | Edge control plane runs on lab host (`deploy/edge-control-plane.lab.json`) | Verified: `edge-control-plane.service` active, unit byte-identical to the edge repo copy, 9443 mTLS | **OK** |
| 3.9 | WG peer "persisted in `config/wireguard/wg0.conf.tpl` and the live `wg0.conf` — falcon commit `36ca988`" | Template contains **no** edge peer (only `.2` netns peer); `36ca988` touches evidence/ledgers only; live conf last written **by the edge onboarding script** 2026-09-29 20:02:38Z (mtime + `.bak-edge-*` chain + edge evidence) | **FAIL (three ways)** |
| 3.10 | Lab → edge "enrollment/manager services (10.99.0.1:15140/15141)" | Those are **falcon's Wazuh client proxies** (TCP 15140 agent, 15141 enrollment; 15140 UDP is the Sebago-Fiber syslog path). The sensor has **no Wazuh agent** and the edge repo has no 15140/15141 references; sensor enrollment is the edge control plane's own 9443 mTLS + bootstrap token | **FAIL (misidentified coupling)** |
| 3.11 | "The edge program never writes into this repository" | At 01:11:51Z — 23 s before the pin commit — the edge program installed `config/grafana/dashboards/edge-fleet-overview.json` **into the falcon working tree** (root-owned, untracked until falcon's `cf7f5c4` at 02:49). Edge evidence itself says "new file in their provisioned dir" | **FAIL (factually wrong at pin time)** |
| 3.12 | "the falcon side … is the delivery that contains this file" | Verified: `falcon-review-delivery-2026-09-30.tar.gz` contains `review-package/docs/edge/EDGE_RELEASE_PIN.md` and the edge dashboard; pin copy identical to `docs/` copy | **OK** |
| 3.13 | Pairing is two-sided ("Update it whenever the edge release or the interface changes") | Edge repo has **no mention** of the pin or of its falcon pairing (only a phase-0 "related program" row); no CI check on either side detects drift | **Process gap** |

### 3.2 Manifest integrity spot-check (current file)

- 31/31 listed artifacts hash-verify on disk; signature valid; the file names lab7 artifacts and
  the lab7 SBOM.
- Two files in the delivery dir are **not** in the manifest: `falcon-agent-0.1.1-lab.tar.gz`
  (built 01:50, after the 01:19 rebuild — the open F11 item in the edge contradiction ledger) and
  `falcon-edge-secrets-backup-20260930T011356Z.tar.gz` (root-owned; manifest builder skips
  unreadable files and prints "skipped (unreadable)" — the manifest therefore silently omits a
  secret-bearing archive while listing an earlier one).
- The manifest (a signed, release-facing document) digests a **secrets backup archive** that lives
  in the same handoff directory.

## 4. Coupling map (actual, including undocumented)

### 4.1 Services, ports, units

| Component | Code/source owner | Live artifact / path | Port / schedule | Mutual dependency |
|---|---|---|---|---|
| Edge control plane | edge repo `src/falcon_control`, `deploy/edge-control-plane.service` | unit in `/etc/systemd/system`, runs as `user` from `/home/user/falcon-edge-build` working tree; secrets in `/home/user/falcon-edge-secrets` | TCP **9443** on 0.0.0.0 (LAN blocked by nft default-deny; `iifname wg0 accept`) | Sensor → lab over wg0; falcon host provides WG + firewall only |
| Edge fleet exporter | edge repo `automation/observability/fleet_metrics.py` | `falcon-edge-metrics.{service,timer}` — **unit exists only on host**; writes `/srv/falcon/textfile/falcon_edge_metrics.prom` | every 5 min | falcon node-exporter textfile collector → Prometheus → Grafana |
| Edge maintenance timers | edge repo `automation/validation/{renew_operator_cert,backup_edge_secrets}.py` | `falcon-edge-operator-cert.*`, `falcon-edge-secrets-backup.*` — **units exist only on host**; backups into `/home/user/falcon-edge-delivery` | daily 01:13Z | Local-only backup; not covered by falcon offsite |
| Grafana edge dashboard | **created by edge, owned now by falcon** | `config/grafana/dashboards/edge-fleet-overview.json` (tracked `cf7f5c4`, same bytes as live) | provisioned by Grafana file provider | Queries `falcon_edge_*`; no edge-repo source file |
| WireGuard `wg0` | falcon (repo template + live conf) | `/etc/wireguard/wg0.conf` last written by edge onboarding; falcon template lacks the peer | UDP 5182 | Edge tunnel is the only sensor data path |
| Wazuh VPN proxies | falcon | `falcon-wazuh-agent-proxy.socket` / `falcon-wazuh-enroll-proxy.socket`, 10.99.0.1:15140/15141 | TCP | **Not used by the edge sensor** (pin says otherwise) |
| VPN enrollment service | falcon | `falcon-vpn-enroll.service` :8791 | TCP | Client-endpoint onboarding; edge sensor not in it (`clients/`+`peers/` dirs empty) |
| Alerts | falcon | Grafana rules: 30 live, incl. `falcon-wg-peer-stale` (`falcon_wg_peer_handshake_age_seconds > 86400`, 30 m) and `falcon-vpn-tunnel-stale` (global, 600 s) | live | Edge-specific rules (`falcon-edge` group) **not deployed** |

### 4.2 Data paths

- **Edge → lab (metrics):** LB5 sensor heartbeat/metrics → control plane DB → `fleet_metrics.py`
  (direct SQLite read) → `falcon_edge_metrics.prom` → node-exporter → Prometheus (15 s scrape) →
  Grafana dashboard + (potentially) falcon alert rules/relay.
- **Edge → lab (metadata/EVE):** sensor Vector → `POST /api/v1/ingest/vector` → NDJSON spool under
  `/home/user/falcon-edge-secrets/ingest` (128 MB/file cap, no retention policy; 44 MB in 2 days).
  This data **does not** enter the falcon OpenSearch pipeline.
- **Edge → lab (control):** sensor agent → 9443 mTLS heartbeat/desired-state/update-manifest/renewal.
- **Lab → edge:** WireGuard transport + firewall + DNS (`falcon.lab`); WG peer managed by the edge
  onboarding script; the edge's own CA/PKI is fully separate from falcon's PKI.

### 4.3 Undocumented / conflicting couplings found

- **U-1** The pin does not mention the Grafana dashboard at all, although it went live 23 s before
  the pin.
- **U-2** `falcon-edge-*` units are host-only; neither repo contains the unit files (rollback notes
  describe deletion, not reconstruction).
- **U-3** Live services execute code from the edge repo working tree (`ExecStart` paths); a
  `git checkout`/branch switch on this host changes production behaviour with no deploy step.
- **U-4** Repo template vs live WG config drift (pin claims persistence; template has no peer;
  `bootstrap/95-wireguard.sh` overwrites the live file).
- **U-5** Edge onboarding modifies the lab-owned `/etc/wireguard/wg0.conf` in place (6 rewrites on
  2026-09-29, backups `wg0.conf.bak-edge-*`, rollback note in the script header).
- **U-6** Falcon's decision log describes that persistence with inverted facts ("was NOT in wg0.conf
  … persisted … falcon commit 36ca988"); the falcon evidence capture at 00:59:13Z contains only a
  `wg show dump` line — no config evidence at all.
- **U-7** Port 15140 is both falcon's UDP syslog feed and TCP Wazuh proxy; the pin conflates these
  with the edge sensor.
- **U-8** Edge `ca.key`, signing seed and DB live under a user-owned directory, while edge
  `OWNER_DECISIONS.json` ED-06 (still `PROPOSED_PENDING`) proposed "owner-custodied root-only
  secrets under `/srv/falcon/secrets`".
- **U-9** Edge secrets backups are stored in the release/delivery directory and one of them is
  referenced by the signed release manifest.
- **U-10** Falcon's live 30-rule set includes `falcon-wg-peer-stale`, which is **absent from**
  `docs/phase9/ALERT_CATALOGUE.yaml` (29 catalogued). The rule is the only automated detection that
  covers the edge sensor path today.

## 5. Additive-rule assessment (edge AGENTS rule 6 / edge REPOSITORY change classes)

| Change | Additive? | Rollback note? | Verdict |
|---|---|---|---|
| Exporter (`falcon-edge-metrics` timer + own `.prom`) | Yes — own unit, own file, falcon configs untouched (`node_textfile_scrape_error=0`; falcon `falcon_metrics.prom`/`falcon_services.prom` unchanged) | Yes — D-007 explicit rollback | **Compliant** |
| Alert rules (`edge-alerts.yaml`) | Not deployed — the deploy script itself says it is **NOT additive** (edits compose + `prometheus.yml`, recreates Prometheus) and is dry-run by default, owner decision pending; live Prometheus has no `rule_files` and no `.bak-edge-rules` exists | Script prints rollback | **Compliant by restraint** |
| Grafana dashboard | New file, but written **inside falcon's working tree** (`config/grafana/dashboards/`), root-owned and untracked until falcon adopted it; installed by the edge program 23 s before the pin claimed it never writes there | Rollback note in the capture ("remove the file"; Grafana keeps it because `disableDeletion=true`) — but now stale, the file is falcon-tracked | **Deviation** (additive in effect, boundary breach in form) |
| WG peer in `/etc/wireguard/wg0.conf` | In-place rewrite of a falcon-owned artifact; backups kept per run; peer block is additive by semantics | Yes — script header rollback + per-run backup files | **Deviation from "never rewrite in place" unless owner approval is on record; approval context exists (owner-supplied Pi, owner-authorised sudo), but the falcon record got the facts wrong** |
| Edge control plane + maintenance timers | New units, separate secrets dir, no monitoring-stack config touched | D-005 (install) / rollback described in audit evidence | **Compliant** |

Record-keeping inconsistencies on the edge side: D-007 says "Rules/dashboard deployment deferred"
while the dashboard was deployed later (the phase-8 closeout amends this append-only, but D-007's
text itself was not superseded); `OWNER_ACTIONS.md` calls the alert-rules/dashboard recipe
"additive", contradicting `deploy_edge_alert_rules.sh` and the phase-8 closeout, which correctly
call rule deployment non-additive.

## 6. Findings by severity

### Critical

- **INT-C1 — Pin ↔ delivery digest mismatch; unversioned overwritten manifest.**
  Evidence: pin `dffcbbb7…`/`35f0793c`/lab6 SBOM vs delivery `9c1021e9…`/`14e7c70`/lab7 SBOM;
  edge evidence `20260930T011949Z_lab7-manifest-rebuilt.out`; manifest mtime 01:19:55Z vs pin
  commit 01:12:14Z. Any consumer trusting the pin verifies the wrong artifact; the pinned manifest
  no longer exists.
- **INT-C2 — Edge peer persistence claim is wrong; template-vs-live drift means a bootstrap re-run
  drops the tunnel.** Evidence: `git log --all -- config/wireguard/wg0.conf.tpl` shows no edge peer
  ever; `git show 36ca988` (6 files, all evidence/ledgers); live conf mtime 2026-09-29 20:02:38Z;
  `.bak-edge-*` chain shows keys e5ZSUt6S→HHw+CTw0→vjDMRryN→9+1VICCn→**sXdIz** (lab5); edge
  onboarding evidence `20260929T200238Z_onboard-lab-side-lab5.out` ("current peer written; peers
  now: 6"); `bootstrap/95-wireguard.sh` renders the template over the live file.

### High

- **INT-H1 — No alert covers the edge path.** Live Grafana has 30 rules, none `falcon-edge`; the
  per-peer WG rule fires only after 24 h with no handshake; the edge's own silence/queue/cert rules
  are prepared but undeployed; falcon's service probe checks Grafana/dash/ntfy/traefik/ntop/relay/
  do/iris — not 9443 and not exporter freshness. A sensor that stops heartbeating or an exporter
  that stops writing is visible only on the dashboard.
- **INT-H2 — Live code is the edge working tree.** `edge-control-plane.service` ExecStart
  `-m falcon_control --config /home/user/falcon-edge-build/deploy/…`; exporter ExecStart runs
  `automation/observability/fleet_metrics.py` from the same tree; both run as enabled services while
  the repo HEAD moved 23 commits and a reviewer is actively changing docs/evidence in place.
- **INT-H3 — Edge PKI/DB backup is local-only and outside falcon's offsite job.** Edge daily backup
  → `/home/user/falcon-edge-delivery` (keep 7, host-local); falcon offsite uploads OpenSearch
  snapshots (`falcon-*` indices) and the encrypted falcon-repo config archive only
  (`bootstrap/80-offsite-backup.sh`). Host loss = edge CA/signing seed/sensor certificates lost;
  every enrolled sensor's trust anchor disappears.
- **INT-H4 — Version skew across four moving references.** Pin commit `35f0793` (32 commits behind
  edge HEAD), manifest commit `14e7c70` (21 behind), live image lab5 vs recommended lab7, control
  plane 0.1.0 vs agent bundle 0.1.1-lab (built 01:50, not in manifest, F11 open), units host-only.
  Both repos are also ahead of their origin refs (6 / 23 commits), so "release" ≠ remote.

### Medium

- **INT-M1 — Boundary breach on the dashboard (see §5)** and now-ambiguous ownership: edge created
  it in falcon's tree; falcon adopted it; the edge rollback instruction would delete a
  falcon-tracked file.
- **INT-M2 — WG peer administration is inverted.** The edge onboarding script writes into the lab's
  config (with backups/rollback); falcon's runbook doesn't list the `.30` peer, and the falcon
  decision log misdescribes the event. A lab-side key/IP rotation that doesn't coordinate with the
  edge procedure (or vice-versa) silently breaks the sensor path.
- **INT-M3 — Secrets backup inside the release surface.** `falcon-edge-secrets-backup-20260930T011054Z.tar.gz`
  is digest-listed in the signed release manifest and both backups sit in the release delivery dir;
  the newer root-owned backup is silently skipped by the manifest builder.
- **INT-M4 — Falcon-side record/alert drift.** `falcon-wg-peer-stale` exists live and in
  `bootstrap/90-alerting.sh` but is missing from `docs/phase9/ALERT_CATALOGUE.yaml` (29 vs 30);
  the pin's WG-persistence claim is repeated in the delivery; `docs/runbooks/VPN.md` doesn't list
  the edge peer.
- **INT-M5 — Shared-host resource risk unowned.** Root LV 82 % (31 GiB free) and 4.7 GiB swap in
  use; the edge ingest spool has a 128 MB/file cap but no retention; the edge's own
  endurance/soak tooling runs on the same host/Pi and can overlap maintenance windows (observed).

### Low

- **INT-L1 — Pin misidentifies the 15140/15141 coupling** (Wazuh client proxies; sensor has no
  Wazuh agent). Any future reader may build the wrong dependency model.
- **INT-L2 — `falcon-` prefix on edge-provided units** invites ownership confusion (units are not
  in the falcon repo).
- **INT-L3 — Cosmetic drift:** five stacked "falcon-edge lab sensor (updated …)" comment blocks in
  `wg0.conf`; a 0-byte stale `control.db` in the edge secrets dir; duplicate token mint leaving 7
  unredeemed 7-day bootstrap tokens in the DB (two minted 2026-09-29 17:06–21:04, one at
  2026-09-30 01:13:51 — expected per D-005 but worth hygiene review).
- **INT-L4 — Control plane binds 0.0.0.0:9443.** nft default-deny plus `iifname wg0 accept` keeps
  it off the LAN, but every VPN peer (including client endpoints) can reach it; mTLS is the only
  gate.

## 7. Failure modes of the joint system

| # | Trigger | What breaks | Detection today |
|---|---|---|---|
| F1 | `bootstrap/95-wireguard.sh` re-run / host rebuild from repo | Edge peer disappears from `/etc/wireguard/wg0.conf`; tunnel down; sensor offline until onboarding re-runs | WG handshake metrics stay "last seen"; per-peer alert after **24 h**; otherwise dashboard only |
| F2 | Edge repo `git checkout` / branch switch / uncommitted edit | Live control plane and exporter behaviour changes without deploy review (worktree execution) | None automated |
| F3 | Edge control plane stops (crash, port conflict, cert expiry mishandled) | Sensor queues metadata, heartbeats stop, renewals stop; falcon still shows last metric values | No falcon alert; edge alerts undeployed; dashboard shows stale heartbeat age |
| F4 | Prometheus/node-exporter config change on falcon side (textfile dir, scrape) | All `falcon_edge_*` series vanish silently | No rule; `node_textfile_scrape_error` is not alerted either |
| F5 | Lab host loss | Edge CA + signing seed + DB + backups on the same host; offsite doesn't cover them; fleet-wide re-enrollment/trust reset needed | n/a (backup gap) |
| F6 | Root LV exhaustion (82 % now) | Both programs' writers (OpenSearch/Prometheus + edge spool) can wedge; node-exporter textfile writes fail | falcon disk rules exist; edge has no host-disk-specific alert of its own |
| F7 | Sensor re-image (new WG key baked) | New key must be rewritten into the lab's wg0.conf by the edge onboarding script; if it isn't, tunnel down | Handshake alert (24 h) / dashboard |
| F8 | Manifest/pin drift (already happened) | Reviewers verify the wrong digests; `P10-G05` evidence cites an 18→31 artifact transition that no longer matches any file | None — no cross-repo drift check |
| F9 | Prometheus rules deployment attempt outside the doctrine | Edits falcon compose + `prometheus.yml`, recreates Prometheus — non-additive, can interrupt the monitored stack | Script is dry-run by default; plan documented; owner decision pending |
| F10 | Edge cert/secret rotation | Sensor/operator certs rotate correctly (verified), but trust bundle/CA custody is user-owned and unoffshored; losing the CA key is unrecoverable | Renewal timer runs daily; no CA-backup alert |

## 8. Runbook and ownership coverage

- **Falcon side:** the joint system has no runbook. `OPERATOR_START_HERE.md` names the sensor peer
  `10.99.0.30` but there is no procedure for edge fleet monitoring, dashboard ownership, exporter
  staleness, control-plane health, or the edge backup/offsite split. `VPN.md` doesn't list the
  edge peer.
- **Edge side:** good per-sensor runbooks (`docs/runbooks/`, 15 files) but no joint-host runbook
  (e.g., "lab control plane down", "falcon node-exporter lost", "lab host reboot", "delivery-dir
  cleanup", "pin/manifest re-pairing"). Several runbooks are explicitly "device drill pending".
- **Ownership:** the only written boundary is edge AGENTS rule 6 + the pin. In practice ownership
  of the dashboard moved from edge to falcon without a falcon-side "we own this" record, and WG
  peer administration sits with the edge program although the lab owns the interface.

## 9. Recommendations (concrete)

**Pin/interface doc (falcon)**
1. Re-pin to the edge artifact batch after the edge program freezes a release: record the manifest
   digest **and** the release commit; attach a copy of the signed manifest (or a URI) to the falcon
   package so the pin is checkable offline.
2. Correct the interface section: (a) WG peer persisted only in the live `wg0.conf` (template
   update tracked separately or make bootstrap preserve peers); (b) 15140/15141 are Wazuh client
   proxies, not the sensor interface — the sensor interface is WG transport + its own 9443 mTLS
   enrollment; (c) add the dashboard and the metric-name contract (`falcon_edge_*`) to the
   interface; (d) note live image (lab5) vs release artifact (lab7) explicitly.
3. Add a CI/closeout check that fails when the pin's digest/commit cannot be matched against a
   supplied manifest copy or a mutually agreed pointer file.

**Ownership boundaries**
4. Move the unit files for `falcon-edge-metrics`, `falcon-edge-operator-cert`,
   `falcon-edge-secrets-backup` into the edge repo `deploy/` (the units are currently host-only);
   either rename them out of the `falcon-` namespace or document them as edge-owned in the pin.
5. Declare the dashboard falcon-owned (it is already tracked in falcon) and record the edge metric
   contract in the pin; delete the stale edge rollback note or re-point it to falcon's removal
   procedure.
6. Make WG peer addition a falcon-owned step (`automation/vpn/add_peer.sh` or a joint procedure)
   or require the edge onboarding to be run under a falcon-documented joint runbook, with the
   template/config persistence landing in the falcon repo.

**Monitoring of the joint paths**
7. Deploy a minimum edge alert set behind the owner decision: `EdgeSensorSilence` (≥15 min,
   ACTIVE-state filter), queue backlog/drops, certificate <7 d — or fold equivalents into falcon's
   catalogue so there is one source of truth. Today only a 24 h WG rule exists.
8. Add falcon-side checks/alerts for: edge control plane `9443/api/v1/healthz` (service probe),
   `falcon_edge_control_plane_scrape_timestamp` / exporter-file staleness (e.g. >15 min), and
   `node_textfile_scrape_error > 0`; add `falcon-wg-peer-stale` to `ALERT_CATALOGUE.yaml`.
9. List the edge sensor peer in `docs/runbooks/VPN.md` with its key-rotation flow.

**Backups / secrets / release hygiene**
10. Extend the offsite path to the edge secrets backup (or explicitly accept the local-only risk in
    writing, in both programs' ledgers); move secrets backups out of `/home/user/falcon-edge-delivery`
    and exclude them from the release manifest.
11. Version release manifests (`…-YYYYMMDD-<shortsha>.json` or manifest `releaseId`), generate them
    from a git tag, push before pinning, and never overwrite a published manifest name in place.
12. Keep the live code path immutable: copy/pin the edge release tree (or install a versioned
    release directory) instead of executing `/home/user/falcon-edge-build` directly; add a unit
    `ConditionPathExists`/version check if a pin is introduced.

**Doc corrections (append-only)**
13. Falcon: correct the 2026-09-30T01:00Z decision-log entry and the pin's WG/completion claims with
    a new entry that states the true provenance (edge onboarding wrote the live conf on 09-29;
    `36ca988` has no config change; template still lacks the peer).
14. Edge: amend D-007/OWNER_ACTIONS texts that still say the dashboard/rules are deferred or
    "additive"; note the dashboard was adopted by falcon in `cf7f5c4` and that its rollback note is
    void.

## 10. Evidence index (selected)

- Pin: `/home/user/falcon-build/docs/edge/EDGE_RELEASE_PIN.md` (`eb1191bc…`), commit `0aa7e7c`;
  package copy embedded in `/home/user/falcon-review-delivery-2026-09-30.tar.gz`.
- Manifests: `/home/user/falcon-edge-delivery/falcon-edge-release-manifest-20260930.json`
  (`9c1021e9…`) + `.sha256`; edge evidence `P10-G05/20260930T002328Z_release-manifest-clean-rebuild.out`,
  `…011929Z_lab7-sbom-and-manifest.out`, `…011949Z_lab7-manifest-rebuilt.out`.
- WG provenance: `/etc/wireguard/wg0.conf` (+ 6 `.bak-edge-*` files), edge evidence
  `EDGE-ONBOARD/20260929T2…_onboard-lab-side-{v2,lab3,lab4,lab5}.out`, falcon commit `36ca988`,
  falcon evidence `REVIEW-FIX/20260930T005913Z_edge-sensor-peer-persisted.{out,meta.json}`.
- Dashboard/units/exporter: edge evidence `P8-G01/20260930T001859Z_exporter-deployed-textfile.out`,
  `…011151Z_grafana-dashboard-deployed.out`, `…011318Z_grafana-dashboard-verified5.out`; falcon
  commits `0e78670`, `cf7f5c4`; live unit files under `/etc/systemd/system/`.
- Alerts/rules: live Grafana `alert_rule` (30 rows), falcon `bootstrap/90-alerting.sh`,
  `docs/phase9/ALERT_CATALOGUE.yaml`; edge `config/prometheus/edge-alerts.yaml`,
  `automation/validation/deploy_edge_alert_rules.sh`.
- Live facts: `wg show wg0`, `systemctl status edge-control-plane`,
  `/srv/falcon/textfile/falcon_edge_metrics.prom`, Prometheus queries (`up`, `node_textfile_scrape_error`,
  `falcon_edge_sensors_total`), Pi SSH probes (`/etc/falcon-edge-image.json`, unit states).

---

*Audit performed read-only; no secrets are reproduced. Live figures were captured while the edge
program's own 10× hard-reset endurance test was running, which is noted where relevant.*
