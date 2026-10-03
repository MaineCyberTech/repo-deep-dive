# Cross-Repo Integration and Pairing Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab, full-hardening) · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: central `/home/user/falcon-build`; edge `/home/user/falcon-edge-build`; delivery `/home/user/falcon-edge-delivery`
- Commit SHA: central recorded `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (delivered package `3ac6cd46…`); edge recorded `45dfed0`, moved `→ f1c5defe6b66887ae49bc44c2cd79b37ad249663` mid-run; edge manifest generated at `155f2446…`. Claims bind to recorded states.
- Generated at: 2026-09-30T15:20Z · Auditor: audit subagent (prompt 42), read-only · Area code: XREPO
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/42_cross_repo_integration_pairing_audit.md`
- Scope limitations: live host read-only; no restarts/reconfigurations; edge device untouched; digests recomputed at the recorded delivery state; secrets by path/type only.

## Scope

Reviewed: central pin and its delivery copies; edge release manifest/signature/sidecar and generator; edge release/closeout/review records; shared-host interfaces (WireGuard, control plane 9443, metrics textfile, ingest, Wazuh proxies, delivery dirs); cross-repo docs (README/AGENTS/runbooks/port matrix); upgrade/rollback evidence; boundary failure modes. Not reviewed: edge hardware certification (43), data quality (44), live service deep-state (LIVE lens).

## Evidence Reviewed

- `falcon-build/docs/edge/EDGE_RELEASE_PIN.md` (sha256 `eb1191bc…`; identical copy in `review-package/`).
- `/home/user/falcon-edge-delivery/falcon-edge-release-manifest-20260930.json` (actual sha256 `3fa4a49c…`, 42 artifacts, commit `155f2446…`, generated 2026-09-30T06:25:23Z) + sidecar (`18681751…`).
- Edge `automation/validation/build_release_manifest.py`; capture `E-P10-G05-313` (33-artifact manifest `18681751…`, commit `0b83acc`); `closeout/REVIEW-2026-09-30.md`; `closeout/FINAL_RESPONSE.json`; edge ledgers.
- Falcon `docs/runbooks/VPN.md`, `docs/architecture/PORT_PROTOCOL_MATRIX.md`, `config/grafana/dashboards/edge-fleet-overview.json`, `config/prometheus/`, `ledgers/decision_log.md` (2026-09-30T01:00Z, 04:25Z).
- Edge `deploy/edge-control-plane.lab.json`, `deploy/edge-control-plane.service`, `config/prometheus/edge-alerts.yaml`, `automation/validation/{deploy_edge_alert_rules.sh,backup_edge_secrets.py,onboard_lab_side.sh}`; edge D-007, edge R-003.
- `/home/user/falcon-review-delivery-2026-09-30.tar.gz` (contains `review-package/`).

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sha256sum falcon-edge-release-manifest-20260930.json` | checksum | pin verification | `3fa4a49c…`; pin `dffcbbb7…`, sidecar `18681751…` |
| `sha256sum -c …json.sha256` | checksum | release integrity | FAILED (mismatch; sidecar stores an absolute path) |
| Manifest artifact verification | checksum | delivery contents | **42/42 artifacts hash+size match** on disk |
| Edge `sha256sum -c evidence/MANIFEST.sha256` | checksum | edge evidence | 642/642 OK at current HEAD |
| Edge review-package sidecar | checksum | edge delivery | `63732ccd…` matches `...-20260930044418-0b83acc.tar.gz` |
| Falcon package `sha256sum -c` | checksum | host package | 2067/2067 OK (report 41) |
| Pin vs manifest field compare | diff | pairing contract | pin commit `35f0793c` vs manifest `155f2446`; SBOM lab6 vs lab8; image lab5 vs lab5–lab8 present |
| Interface cross-check (VPN/WG/ports) | grep | shared host | `VPN.md` omits peer `10.99.0.30`; port matrix says `51820`, runbook `5182`; pin calls 15140/15141 edge enrollment |
| Edge alert rules presence in falcon | ls/grep | boundary failure | `config/prometheus/edge-alerts.yaml` absent; dashboard adopted (`cf7f5c4`) |
| `deploy_edge_alert_rules.sh` target scan | read | additive rule | writes `/home/user/falcon-build/config/prometheus/…` and edits the falcon compose mount |
| Edge service unit | read | runtime binding | `WorkingDirectory=/home/user/falcon-edge-build`; `python3 -m falcon_control` — live code is the repo tree |
| Edge backup script scope | read | offsite coverage | writes unencrypted tarballs to the delivery dir; falcon offsite job does not include it |

## Executive Summary

The pair works as a lab system: the sensor is enrolled, the tunnel and metrics path are live, the 42 artifact hashes and the edge evidence manifest verify, and edge D-007 documents an additive deployment with a rollback note. The pairing contract is broken: the pin's digest, commit, SBOM and image fields describe older generations than the manifest on disk; the signed manifest is rewritten in place under a fixed dated name, so the sidecar and the reviewer's release acceptance (`18681751…`, 33 artifacts) no longer match (`3fa4a49c…`, 42 artifacts); nothing verifies the pin, and the stale pin ships inside the central package. On the shared host, the dashboard was adopted but the edge alert rules were never deployed, so edge-path failures remain invisible to central alerting, and several cross-repo documents disagree with the live interface. Recommended: freeze release artifacts under versioned immutable names, rebind the pin with an automated contract check, and complete the alert path with a rollback note.

## Inventory

| Item | Path / symbol | Purpose | State | Risk |
|---|---|---|---|---|
| Pairing pin | `docs/edge/EDGE_RELEASE_PIN.md` | pair central↔edge | stale (digest/commit/SBOM/image) | High |
| Edge manifest | delivery `…20260930.json` | signed release record | 42 artifacts, hashes verify | High |
| Manifest sidecar | `…json.sha256` | integrity check | stale (`18681751…`) | High |
| Edge review | `closeout/REVIEW-2026-09-30.md` | independent review | substantive; FINAL PASS for lab scope | Low |
| Edge gate ledger | `ledgers/gate_ledger.csv` | 88 gates | 77 PASS / 8 BLOCKED / 3 IE | Medium |
| WG tunnel | `wg0` 10.99.0.0/24, UDP 5182 | data/control path | live; peer `.30` persisted | Medium |
| Edge control plane | `deploy/edge-control-plane.lab.json` | mTLS API | 0.0.0.0:9443, runs from repo tree | Medium |
| Fleet metrics | `/srv/falcon/textfile/falcon_edge_metrics.prom` | additive telemetry | live, 61 series | Medium |
| Edge alert rules | edge `config/prometheus/edge-alerts.yaml` | alerting | not deployed to falcon | High |
| Secrets backup | `falcon-edge-delivery/falcon-edge-secrets-backup-*.tar.gz` | recovery | local-only, unencrypted | High |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Pairing contract | 1 | pin fields defined | fails verification | rebind + automate |
| Edge release process / central consumption | 2 | signed manifest + review | mutable artifact; 33↔42 generations | versioned releases |
| Shared-host interfaces | 3 | WG/metrics/proxies live | alert gap; doc drift | complete + document |
| Protocol/API compatibility | 3 | additive metrics-only | no version field (not needed yet) | record contract |
| Version skew handling | 1 | manual pin rule only | no detection/enforcement | add check |
| Additive rule and isolation | 3 | D-007 rollback; R-003 | deploy script writes into falcon repo | operator-mediated deploy |
| Cross-repo documentation consistency | 2 | both repos document | port/peer/declaration drift | reconcile |
| Cross-repo evidence / delivery artifacts | 2 | manifests/checksums exist | mutable manifest; secrets | versioned signing |
| Boundary failure modes | 2 | spool, heartbeat, dead-man | no central edge alert | deploy alerts |
| Rebind/upgrade and rollback | 2 | update path verified | A/B boot + image rollback untested | test + document |

## Detailed Review

### Item: Pairing contract and release immutability

- Evidence: pin `eb1191bc…`; manifest `3fa4a49c…`; sidecar `18681751…`; `build_release_manifest.py` (writes one file, no sidecar, no history); `verify_publication_chain.sh` covers only the central chain; `E-P10-G05-313` shows the 33-artifact review-time generation.
- Behavior: manual pin updates; one dated filename reused for every regeneration. Missing: pin verifier, content-addressed names, sidecar regeneration, acceptance by digest. Risks: wrong pairing delivered (observed); manifest swap undetectable. Fixes: versioned immutable manifests, CI pin check.

### Item: Shared-host interfaces and additive rule

- Evidence: edge D-007 (timer, textfile, rollback note), edge R-003, falcon dashboard commit `cf7f5c4`, absent alert rules, `deploy_edge_alert_rules.sh` targeting the falcon tree, `edge-control-plane.service` running from the working tree.
- Behavior: edge writes metrics into the falcon textfile dir; falcon hosts WG, ingest, proxies and the control plane. Missing: metric freshness alert; rules deployment; a documented write contract. Risks: silent edge outage; boundary erosion. Fixes: deploy rules via the operator flow; add staleness alert; install the control plane outside the repo.

## Interface Inventory

| Interface | Where defined | Owner | Contract | Failure mode | Notes |
|---|---|---|---|---|---|
| Pairing pin | falcon `docs/edge/EDGE_RELEASE_PIN.md` | falcon | manifest sha + commit + SBOM + image | stale pin (observed) | shipped in package |
| Release manifest | edge `build_release_manifest.py` → delivery | edge | ed25519-signed artifact list + commit | in-place rewrite breaks sidecar/pin (observed) | 42 artifacts |
| WG tunnel `wg0` | falcon `config/wireguard/wg0.conf.tpl` + live | falcon | 10.99.0.0/24, peer `.30`, UDP 5182 | peer loss on bootstrap (fixed: syncconf + preservation check); docs omit `.30` | persisted 2026-09-30 |
| Control-plane API | edge `deploy/edge-control-plane.lab.json` | edge | mTLS HTTPS 9443, 0.0.0.0 | reachable from any wg0 peer; firewall-only gate | runs from repo tree |
| Fleet metrics textfile | edge D-007 → `/srv/falcon/textfile/` | edge writes / falcon consumes | Prom textfile, 61 series | timer stop → stale metrics, no alert | rollback documented |
| Edge dashboard | falcon `config/grafana/dashboards/edge-fleet-overview.json` | falcon | Grafana JSON | silent panel breakage | adopted `cf7f5c4` |
| Edge alert rules | edge `config/prometheus/edge-alerts.yaml` | edge (proposed) | Prometheus rules | not deployed → no central edge alert | deploy script writes into falcon repo |
| Wazuh agent proxies | falcon `automation/wazuh/lab-manager-proxy.sh` | falcon | `10.99.0.1:15140/15141` → `1516/1517` | sockets bind before wg0 (fixed with unit deps) | pin calls them edge enrollment — wrong |
| Sensor ingest | falcon Vector `10.99.0.1:6000` | falcon | Vector protocol | central outage → edge spool until full | R-27 residual |
| Delivery exchange | `/home/user/falcon-edge-delivery` | shared | artifacts + secrets backups | secret spill; local-only backups | outside falcon offsite |

## Skew Scenario Analysis

| Scenario | Concrete outcome |
|---|---|
| Edge newer than pin (current: manifest lab8/`155f2446` vs pin lab5–6/`35f0793c`) | **Silent mispairing**: central approval/pin describes releases that are not current; no check detects it. |
| Edge older than pin (pin updated, sensor not upgraded) | Sensor keeps lab5; integration is additive metrics-only, so no functional break, but the pin overstates capability and there is no min-version gate. |
| Protocol/API drift | Falcon consumes no edge API, only metrics; drift is silent but bounded to stale/renamed metric names (no schema/version field). |
| Config drift | Docs say 51820 / omit peer `.30`; live is 5182 with `.30`; operator actions can target the wrong port/peer (R-30 class). |
| Clock skew | Edge cert/time controls and central NTP exist; central has no edge-time alert; skew can cause false cert/heartbeat results. |
| Certificate expiry | Edge exports `falcon_edge_sensor_certificate_days_remaining`; without deployed rules the expiry is not alerted centrally. |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| XREPO-001 | Pairing contract | pin + manifest | manual rule | pin fails verification | P0 | rebind + CI check |
| XREPO-002 | Edge release/central consumption | manifest builder | signature + review | mutable artifact; generations differ | P1 | versioned immutable releases |
| XREPO-003 | Shared-host interfaces | WG/metrics/proxies | documented + rollback | alerts missing; docs drift | P1 | deploy alerts; reconcile docs |
| XREPO-004 | Protocol/API compatibility | additive metrics-only | none needed yet | no version field | P3 | record contract version |
| XREPO-005 | Version skew handling | pin vs live lab5/lab8 | manual | no detection | P1 | pin verifier |
| XREPO-006 | Additive rule and isolation | D-007, R-003 | additive + rollback | script writes into falcon repo | P2 | operator-mediated deploy |
| XREPO-007 | Cross-repo documentation | runbooks/pin/README | docs exist | contradictions | P2 | reconcile + log |
| XREPO-008 | Cross-repo evidence/delivery | manifests | digests present | secrets; unversioned manifest | P1 | versioned signed releases |
| XREPO-009 | Boundary failure modes | spool/heartbeat | edge-side controls | no central edge alert | P1 | deploy rules |
| XREPO-010 | Rebind/upgrade/rollback | P7-G01/G06; pin rule | update verified | A/B boot + image rollback untested | P2 | test + document |

## Findings

### Finding ID: XREPO-P0-001 - The pairing pin does not verify against the edge release manifest

- Severity: P0 · Confidence: High · Area: XREPO (cross-ref INV-P0-001)
- Evidence: pin line 12 `dffcbbb7…`, line 13 commit `35f0793c…`, line 15 SBOM lab6 `36db1125…`, line 17 image lab5; actual manifest `3fa4a49ca83a2c06dd1b22f24d2594bfae2f449b977ab4e3218f0287f65edba7`, commit `155f2446…`, SBOM lab8 `c5020d6b…`; sidecar `18681751…` matches neither.
- What is happening: every identity field in the pin is stale and none is reproducible from the delivery directory.
- Why it matters: the central program claims a pairing that does not exist; reviewers inherit the wrong binding.
- Business impact: wrong release referenced in approvals/communications. Reliability impact: supply-chain pairing failure (release-blocking).
- Recommended fix: regenerate the pin from the current manifest and add an automated verifier; never hand-copy digests.
- Suggested validation: `verify_edge_pin.sh` reproducing digest/commit/SBOM/artifact names.
- Owner suggestion: release engineer (central) with edge owner · Effort: S · Dependencies: INV-P0-001 · Status: still-open

### Finding ID: XREPO-P1-001 - The signed release manifest is rewritten in place; sidecar and reviewer acceptance bind superseded contents

- Severity: P1 · Confidence: High · Area: XREPO
- Evidence: `E-P10-G05-313` (2026-09-30T04:43:59Z): "release manifest … (33 artifacts, commit `0b83acc`), sha256 `18681751…`, signature VALID"; edge review final section cites `18681751…` as "unchanged"; current file: 42 artifacts, commit `155f2446`, generated 06:25:23Z, sha256 `3fa4a49c…`; sidecar unchanged.
- What is happening: a dated filename is reused across regenerations; signature validity covers only the latest bytes while earlier acceptance records reference a manifest no longer on disk.
- Why it matters: signed release acceptance is not reproducible; a manifest swap leaves pinned records unchanged.
- Recommended fix: content-addressed/versioned manifest names, keep every generation, accept by digest, regenerate the sidecar atomically.
- Suggested validation: immutability test — old digests still exist and verify. · Owner: edge release engineer · Effort: S · Status: open

### Finding ID: XREPO-P1-002 - No central alerting for the edge path; the rules deployment crosses the repo boundary

- Severity: P1 · Confidence: High · Area: XREPO (cross-ref prior INTG-P1-001)
- Evidence: `config/prometheus/edge-alerts.yaml` absent in falcon; `compose/central/docker-compose.yml` mounts no edge rules; edge `config/prometheus/edge-alerts.yaml` defines EdgeSensorSilence/QueueBacklog/QueueLoss/CertificateExpiry; edge D-007 "Rules/dashboard deployment deferred"; falcon adopted only the dashboard (`cf7f5c4`); `deploy_edge_alert_rules.sh` writes into `/home/user/falcon-build/…`.
- What is happening: edge metrics reach central Prometheus but no rules evaluate them; the prepared deploy path writes into the other program's repository.
- Why it matters: a silent edge sensor or stopped exporter has no central alert; boundary ownership is ambiguous.
- Recommended fix: deploy rules through the operator flow with rollback; use a separate rule file with an explicit write contract.
- Suggested validation: stop the edge exporter timer; assert `EdgeSensorSilence` fires. · Owner: operator + edge owner · Effort: S · Dependencies: compose change window · Status: open

### Finding ID: XREPO-P1-003 - Secret material in the shared delivery directory and delivery archives

- Severity: P1 · Confidence: High · Area: XREPO (cross-ref API-P0-001, prior REV-P3-010)
- Evidence: falcon `review-package/automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf` (sha256 `7a6eb61c…`) carries literal cluster/API key values and is present in `/home/user/falcon-review-delivery-2026-09-30.tar.gz`; edge delivery dir holds `falcon-edge-sensor-*-ssh-key`, `*-credentials.txt` and mode-0600 but unencrypted secrets backups; `backup_edge_secrets.py` writes them into the delivery dir; the falcon offsite job does not cover that dir.
- What is happening: credentials live in the same shared home directory as both programs' delivery surfaces; one central archive also carries credential literals.
- Why it matters: a host or shared-dir compromise exposes control-plane and sensor credentials; the edge PKI/DB has no offsite copy.
- Recommended fix: remove/rotate literals (API-P0-001); encrypt edge backups and include them in the offsite job.
- Suggested validation: secret scan over all delivery archives; restore test from the encrypted backup. · Owner: security owner · Effort: M · Status: still-open

### Finding ID: XREPO-P1-004 - No automated pin verification or skew detection

- Severity: P1 · Confidence: High · Area: XREPO
- Evidence: no script references `EDGE_RELEASE_PIN` (`grep` across `automation/`, `ci/`); the pin's own rule is manual; the stale pin ships in `review-package/docs/edge/EDGE_RELEASE_PIN.md` (sha256 `eb1191bc…`).
- What is happening: pairing is maintained entirely by manual copying.
- Why it matters: the observed P0 drift will recur; consumers cannot distinguish current from stale pins.
- Recommended fix: `automation/validation/verify_edge_pin.sh` in `ci/validate.sh`, comparing pin vs delivery manifest, failing closed.
- Suggested validation: template test with a mutated pin. · Owner: maintainer · Effort: S · Dependencies: XREPO-P0-001 · Status: open

### Finding ID: XREPO-P2-001 - Cross-repo documents contradict the live shared interface

- Severity: P2 · Confidence: High · Area: XREPO (cross-ref prior INTG-P2-002/INTG-P3-001/ND-P2-004)
- Evidence: `docs/architecture/PORT_PROTOCOL_MATRIX.md` still `mon:51820` while `docs/runbooks/VPN.md` says 5182; `VPN.md` documents only `.10` and omits the persisted edge peer `10.99.0.30` (decision log 2026-09-30T01:00Z); the pin calls `10.99.0.1:15140/15141` edge enrollment while code shows Wazuh agent proxies to `1516/1517`; edge README says lab8 current while AGENTS/live say lab5 and the pin says lab5/lab6.
- What is happening: four documents describe different states of the same interface.
- Why it matters: operators/agents follow wrong ports/peers during incidents.
- Recommended fix: reconcile port matrix/VPN runbook/pin text with live state; log entries in both contradiction ledgers.
- Suggested validation: doc-to-live diff for ports/peers. · Owner: operator · Effort: S · Status: open

### Finding ID: XREPO-P2-002 - Edge P4-G02 owner-flash claim has no owner-attributable artifact

- Severity: P2 · Confidence: High · Area: XREPO (cross-ref prior REV-P2-005)
- Evidence: edge gate P4-G02 PASS cites `E-P4-G02-030/031` (`preflight-and-media-guards*.out`, lab-side; shows `control_plane … Connection refused`) and `E-EDGE-ONBOARD-062..070` (falcon-side bakes); no owner flash/first-boot capture is indexed while the gate note asserts the owner flashed the card on Windows.
- What is happening: a claim about an external actor's action rests on the implementer's note.
- Why it matters: actor claims need an artifact from that actor (shared rules).
- Recommended fix: add an owner statement/capture to the refs, or mark the note "owner-reported, unverified".
- Suggested validation: gate refs resolve to an owner-provided artifact. · Owner: owner · Effort: S · Status: still-open

### Finding ID: XREPO-P2-003 - Upgrade/rollback skew is only partially covered across the pair

- Severity: P2 · Confidence: High · Area: XREPO
- Evidence: edge P7-G01 update apply/rollback verified; P4-G06 rollback drill lab-simulated; P7-G05 A/B boot BLOCKED (Pi 3B has no tryboot); falcon `FINAL_RESPONSE.json` `rollback_status`: "image-version rollback not rehearsed"; the pin defines no rollback procedure.
- What is happening: software update/rollback works in the lab path; boot-slot rollback and central pin rollback are unexercised.
- Why it matters: a bad edge release or pin has no tested recovery.
- Recommended fix: document/test pin rollback (retain previous manifest digest); complete a boot-slot rollback rehearsal when hardware allows.
- Suggested validation: rollback drill with a deliberately broken bundle. · Owner: edge owner + operator · Effort: M · Status: open

### Finding ID: XREPO-P2-004 - The live edge control plane runs from the repository working tree

- Severity: P2 · Confidence: High · Area: XREPO (cross-ref prior INTG-P1-002)
- Evidence: `deploy/edge-control-plane.service`: `WorkingDirectory=/home/user/falcon-edge-build`, `ExecStart=python3 -m falcon_control --config …/deploy/edge-control-plane.lab.json`; edge AGENTS notes parallel-session activity in the tree.
- What is happening: the running service is the mutable tree, not a released artifact.
- Why it matters: uncommitted or parallel-session edits alter live behavior without release controls.
- Recommended fix: install from a versioned wheel/tarball or pinned checkout outside the repo, with a controlled restart path.
- Suggested validation: assert the resolved module path is not the repo tree. · Owner: edge maintainer · Effort: M · Status: still-open

### Finding ID: XREPO-P3-001 - Edge control plane binds 0.0.0.0:9443 with a firewall-only gate

- Severity: P3 · Confidence: High · Area: XREPO (cross-ref prior INTG-P3-004)
- Evidence: `deploy/edge-control-plane.lab.json` `"bind": "0.0.0.0", "port": 9443` with the comment relying on the host default-deny firewall; every WireGuard peer can reach it and mTLS is the only application gate.
- Recommended fix: bind the wg0 address or add an explicit nftables accept from `10.99.0.0/24`; document the assumption in the pin interface section.
- Suggested validation: port scan from a peer namespace. · Owner: edge maintainer · Effort: S · Status: still-open

## Prior-Run Finding Status (INTG lens, run 20260930-0320)

| Prior ID | Status now | Evidence |
|---|---|---|
| INTG-P0-001 pin↔delivery digest mismatch | still-open | pin `dffcbbb7…`, sidecar `18681751…`, actual `3fa4a49c…` |
| INTG-P0-002 edge peer persistence/template drift | partially-fixed | `95-wireguard.sh` preserves runtime peers + `wg_peer_preservation_check.sh`; `.30` live; `VPN.md` still omits it |
| INTG-P1-001 no alert covers edge path | still-open | `edge-alerts.yaml` absent from falcon; D-007 defers rules |
| INTG-P1-002 live code is edge working tree | still-open | `edge-control-plane.service` runs from the repo |
| INTG-P1-003 edge PKI/DB backup local-only | still-open | backups go to the delivery dir; falcon offsite excludes it |
| INTG-P1-004 version skew across moving references | still-open | five references: pin commit, manifest commit, README lab8, live lab5, AGENTS lab5 |
| INTG-P2-001 boundary breach dashboard/ownership | partially-fixed | dashboard adopted `cf7f5c4`; rules script still writes into falcon repo |
| INTG-P2-002 WG peer admin inverted; runbook omits `.30` | partially-fixed | decision log records `.30`; runbook/port matrix stale |
| INTG-P2-003 secrets backup inside release surface | still-open | key files + unencrypted backups in delivery dir |
| INTG-P2-004 falcon-side record/alert drift | still-open | port matrix `51820`; pin repeats stale claims |
| INTG-P2-005 shared-host resource risk unowned | not re-assessed | LIVE lens scope |
| INTG-P3-001 pin misidentifies 15140/15141 | still-open | pin interface text unchanged |
| INTG-P3-002 `falcon-` prefix on edge units | not re-assessed | no change evidence |
| INTG-P3-003 cosmetic drift | unknown | not re-checked |
| INTG-P3-004 control plane binds 0.0.0.0 | still-open | XREPO-P3-001 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Wrong pin governs the pair | High | Certain | release/approval invalid | XREPO-P0-001 | rebind + verifier |
| Manifest swap undetected | High | Medium | supply chain | XREPO-P1-001 | versioned signed releases |
| Edge outage invisible centrally | High | Medium | monitoring gap | XREPO-P1-002 | deploy alerts |
| Credential exposure in deliveries | High | Certain | compromise | XREPO-P1-003 / API-P0-001 | rotate/encrypt |

## Recommendations

**Immediate / Release Blocking:** (1) Rebind the pin to the actual manifest and add the verifier (XREPO-P0-001/P1-004). (2) Freeze releases under versioned names; stop rewriting the dated manifest (XREPO-P1-001). (3) Remove/rotate credentials crossing the delivery boundary (XREPO-P1-003/API-P0-001).

**This Week:** (1) Deploy edge alert rules with an owner-approved rollback-documented change; add staleness (XREPO-P1-002). (2) Reconcile VPN/port/pin/README docs; log contradiction entries (XREPO-P2-001). (3) Encrypt/relocate edge secrets backups into the offsite job (XREPO-P1-003).

**This Month:** (1) Package the control plane for install outside the repo (XREPO-P2-004). (2) Add a pairing/rebind/rollback section to the operator runbook (XREPO-P2-003). (3) Record the additive write contract for edge→falcon artifacts (XREPO-006).

**Later / Platform Evolution:** protocol/version negotiation with a min-version policy; automated skew detection across pin, live sensor and manifest.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Regenerate pin digest/commit/SBOM from manifest | removes P0 drift | `docs/edge/EDGE_RELEASE_PIN.md` | `verify_edge_pin.sh` |
| Regenerate sidecar atomically, drop absolute path | integrity check works | delivery dir | `sha256sum -c` |
| Add `.30` peer and 5182 to VPN/port docs | operator accuracy | `docs/runbooks/VPN.md`, port matrix | grep/read |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Versioned immutable edge releases + acceptance by digest | P0 | edge release engineer | M | none |
| Pin verifier + skew detector in CI | P1 | central maintainer | S | pin rebind |
| Edge alert deployment + staleness | P1 | operator | S | compose window |
| Secrets backup encryption/offsite | P1 | security | M | key management |
| Installed (non-repo) control plane | P2 | edge maintainer | M | packaging |

## Suggested Tests

- Integration: pin-vs-manifest verifier (digest, commit, SBOM, names) fails closed on mutation.
- E2E: pairing drill — publish a release, update the pin, verify the central package embeds the correct pin.
- Failure: stop `falcon-edge-metrics.timer`; assert central alert; stop edge CP; assert lifecycle event.
- Security: secret scan over delivery archives; confirm no literal credentials.
- Manual/regression: re-run skew scenarios after doc fixes; verify signed manifest + sidecar from a clean host.

## Suggested Documentation Updates

- `docs/edge/EDGE_RELEASE_PIN.md`: correct interface text (15140/15141 ownership) and rebind procedure.
- `docs/edge/INTERFACES.md` (new): interface, owner, contract, failure mode, rollback.
- `docs/runbooks/VPN.md` + `docs/architecture/PORT_PROTOCOL_MATRIX.md`: port 5182 and edge peer.
- Edge README/AGENTS: live-image statement template; both contradiction ledgers: entries for these mismatches.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which manifest generation is the accepted edge release? | rebind target | owner statement |
| Was the 06:25 manifest regeneration an approved change? | provenance | decision-log entry |
| Were the pinned SSH keys/credentials rotated after delivery? | rotation scope | owner statement |
| Who owns edge rules deployment on the falcon side? | accountability | operator decision |

## Appendix

Recorded-state facts: edge recorded `45dfed0` (06:40Z), current `f1c5def` (09:29Z); manifest commit `155f2446` generated 06:25Z; falcon delivered `3ac6cd4`, publication `8282d3f`. Commands: `sha256sum`, `sha256sum -c`, `git show/archive` (read-only), a JSON artifact verification script, grep/ls. No repo, ledger, gate or live system was mutated; only this report and report 41 were written.
