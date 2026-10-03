# Lens — Integration (falcon ↔ edge pair, shared host)

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab) · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0 · Lens: integration · Area code: INTG
- Repos: central `/home/user/falcon-build` @ `8282d3f` (delivered package `3ac6cd4`); edge `/home/user/falcon-edge-build` @ run-start `45dfed0` → `f1c5def` (manifest commit `155f2446`); delivery `/home/user/falcon-edge-delivery`
- Generated: 2026-09-30 (audit session) · Auditor: read-only lens subagent · Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/lens_integration.md`
- Scope limits: no root/docker/wg/nft; effective firewall, ntfy delivery and edge-device state come from run reports and are `unverified` here; no repo, ledger, gate, or live system was mutated.

## Scope

Reviewed the two programs as one system: pairing pin, release manifest/sidecar, WireGuard tunnel, control-plane API and ingest spool, fleet-metrics textfile, alert-rule/dashboard deployment, operator and renewal timers, shared delivery directory, offsite coverage, version skew, the additive rule, boundary failures and paired upgrade/rollback. Sources: this run's reports 02, 08, 12, 13, 14, 30, 32, 41, 42, 43, 44 plus the prior INTG run. Deep domain quality is cross-referenced, not re-filed.

## Evidence Reviewed

- Falcon: `docs/edge/EDGE_RELEASE_PIN.md`; `config/wireguard/wg0.conf.tpl`; `bootstrap/95-wireguard.sh`; `docs/runbooks/VPN.md`; `config/prometheus/prometheus.yml`; `compose/central/docker-compose.yml`; `bootstrap/90-alerting.sh`; `ci/validate.py`; `config/grafana/dashboards/edge-fleet-overview.json`; `docs/phase9/CLEAN_HOST_REBUILD_RUNBOOK.md`.
- Edge: `deploy/edge-control-plane.{lab.json,service}`; `api/openapi/falcon-edge-v1.yaml`; `config/prometheus/edge-alerts.yaml`; `automation/validation/deploy_edge_alert_rules.sh`; `automation/observability/fleet_metrics.py`; `automation/validation/{backup_edge_secrets,renew_operator_cert,onboard_lab_side}.{py,sh}`; `src/falcon_control/{service,store}.py`; `src/falcon_agent/{runner,queue}.py`; `profiles/sensor/vector/edge.toml`; `docs/phase8/CLOSEOUT.md`.
- Delivery/live/prior: `/home/user/falcon-edge-delivery/*`; `/srv/falcon/textfile/*.prom`; host-only `/etc/systemd/system/falcon-edge-*`; `live_snapshot.txt`; prior `20260930-0320-…/lens_integration.md` + `findings.json`.

## Verification Performed

| Check | Method | Result |
|---|---|---|
| Pin vs manifest | `sha256sum` + field compare | pin `dffcbbb7…` / `35f0793c` / lab6 SBOM vs disk `3fa4a49c…` / `155f2446` / lab8 — mismatch reproduced; pin copy `eb1191bc…` identical in tree and `review-package/` |
| Manifest sidecar | `sha256sum -c` | fails: sidecar `18681751…` vs actual `3fa4a49c…` |
| Tunnel interface | read tpl + script + runbook | `ListenPort=5182`; template has no edge peer; `95-wireguard.sh:43-65` merges runtime peers by public key |
| CP bind + unit | read JSON + unit | `0.0.0.0:9443`; `WorkingDirectory=/home/user/falcon-edge-build`; runs as `user` |
| Alert path | read compose/prometheus/`90-alerting.sh` + drill scripts | 31 Grafana-managed rules; no standalone Alertmanager; `prometheus.yml` has no `rule_files` |
| Edge rules deploy | read `deploy_edge_alert_rules.sh:1-69` | dry-run default; `--apply` edits falcon repo/compose, recreates Prometheus, verifies only `/api/v1/rules` |
| Telemetry contract | read exporter + live file | atomic replace; HELP/TYPE-once requirement in code; live `falcon_edge_*` (9 sensors); no mtime/scrape-error rule |
| Host-only timers | `systemctl list-timers`, unit files | 3 edge units active (metrics 5 min, operator-cert daily, secrets-backup daily); no repo unit source |
| Control path | grep handlers | `consume_directive` has no callers (`store.py:323`); `purge_expired` deletes all rows when called (`queue.py:126-138`, latent) |
| Shared paths | `ls -l` | delivery dir mixed user/root; `edge-fleet-overview.json` root-owned in falcon tree (committed `cf7f5c4`); root-owned secrets backup absent from manifest |
| Joint gate | grep `EDGE_RELEASE_PIN` across `ci/`, `automation/` | 0 hits; `ci/validate.py` checks only parsers/compose pins/gates/evidence/secret scan |

## Executive Summary

The pair works as a live lab system (tunnel up, sensor ACTIVE, metrics flowing, signed manifest with matching artifact hashes, rollback-noted edge deployment), but it is held together by manual bookkeeping and convention. Every recorded identity of the pairing disagrees (pin `35f0793c`/lab6, manifest `155f2446`/lab8, sidecar 33-artifact generation, live card lab5, edge HEAD `f1c5def`), and neither repository's validation touches the other side. This lens adds five joint-system findings beyond the domain ones: the prepared edge alert-rule deployment targets a plane the central alert path cannot deliver; there is no pair-level release gate, upgrade order, or atomic rollback; the edge→central metric contract can fail totally and silently; there is no joint recovery/rebind procedure; and central→edge operator control depends on unmonitored timers with non-authoritative command state. Findings: 2 × P1, 3 × P2. The release-blocking P0s are filed by XREPO/INV/EVID and cross-referenced, not duplicated.

## Inventory — Interface Inventory

| Interface | Where defined | Owner | Contract | Failure mode |
|---|---|---|---|---|
| Pairing pin | falcon `docs/edge/EDGE_RELEASE_PIN.md` (shipped in package) | falcon | manifest sha256 + commit + SBOM + image + interface text | stale/wrong on all identity fields (observed); nothing consumes or verifies it (XREPO-P0-001/P1-004) |
| Release manifest + sidecar | edge `build_release_manifest.py` → delivery dir | edge | ed25519-signed artifact list; fixed dated filename | in-place rewrite breaks sidecar/pin; root-owned file skipped by builder (XREPO-P1-001, FLEET-P1-001) |
| Delivery + offsite surface | `/home/user/falcon-edge-delivery`; falcon `80-offsite-backup.sh` | shared, unowned / falcon backup | none written down | mixed user/root artifacts, SSH keys, unencrypted backups; edge PKI/DB excluded from offsite (DR-P1-005, XREPO-P1-003) |
| WireGuard tunnel `wg0` | falcon `config/wireguard/wg0.conf.tpl` + live; edge `onboard_lab_side.sh` | falcon host config; edge script writes it with root | `10.99.0.0/24`, peer `10.99.0.30`, UDP 5182 | template lacks the edge peer (runtime merge only); docs omit `.30`; re-image key change needs manual re-onboard |
| Edge CP mTLS API | edge `falcon-edge-v1.yaml`, `service.py:ROUTES` | edge | mTLS + RBAC; 16/19 ops documented; replay window 300 s | reachable from every wg0 peer; contract drift (API-P1-001, API-P2-001, ARCH-P2-001) |
| Sensor→CP ingest spool | edge `service.py:584-599` → `/home/user/falcon-edge-secrets/ingest` | edge | NDJSON, ≤128 MiB, rotate overwrites `.1` | older batches silently lost; spool not backed up offsite (DQ-P2-007) |
| Fleet-metrics textfile | edge `fleet_metrics.py` via host-only timer → `/srv/falcon/textfile/falcon_edge_metrics.prom` | edge writes / falcon consumes | Prom textfile, atomic replace, HELP/TYPE once, fixed path | one format regression makes the collector reject the whole family; no freshness rule (INTG-P2-001) |
| Central alert pipeline | falcon `90-alerting.sh` → relay `:9099` → ntfy pair | falcon | Grafana-managed rules, 31 live, dual ntfy | relay at-most-once; zero edge rules (RES-P0-002, OBS-P1-004) |
| Edge alert rules + deploy script | edge `edge-alerts.yaml`, `deploy_edge_alert_rules.sh` | edge proposed / owner undecided | Prometheus rule file; script edits falcon compose | non-additive, recreates Prometheus, and still cannot notify (INTG-P1-001) |
| Edge dashboard | falcon `config/grafana/dashboards/edge-fleet-overview.json` | falcon (adopted `cf7f5c4`); root-owned file | Grafana JSON | written across the boundary pre-adoption; central cannot regenerate it with normal tooling |
| Operator cert / CLI access | edge `pki.py` + `renew_operator_cert.py` via host-only timer | edge | X.509 operator cert, renew ≤15 days, expires 2026-10-29 | renewal failure unmonitored → central loses quarantine/revoke/update control (INTG-P2-003) |
| Directives & signed updates | edge `service.py`, `store.py`; agent `runner.py` | edge (central operator drives) | ed25519 update manifests, sha256 + compile checks, in-process revert | `consume_directive` never called; counters include expired (INTG-P2-003); swap not power-loss safe (FLEET-P1-002) |
| Sensor identity / PKI | edge agent identity dir + CP DB; `pki.py` | edge | CN-scoped certs, 30-day rotation, renewal drills live | no CRL — revoked certs work until expiry; CSR subject unconstrained (FLEET-P2-005, API-P1-001) |
| Wazuh proxies 15140/15141 | falcon `automation/wazuh/lab-manager-proxy.sh` + sockets | falcon | TCP proxy to `127.0.0.1:1516/1517` for client devices | pin mis-describes them as edge enrollment; port docs stale (prior INTG-P3-001, INFRA-P2-001) |
| Shared host / ports / clock | host `falcon` (one KVM guest) | shared, no joint owner | NTP/UTC, single wg0, textfile dir, 9443 | single SPOF: host loss/OOM takes monitoring and edge trust path together (ARCH-P1-001, DR-P1-005) |

**Version skew matrix (recorded states).** Pin: manifest `dffcbbb7…`, commit `35f0793c`, lab6 SBOM + lab5 image. Manifest on disk: `3fa4a49c…`, commit `155f2446`, lab8 SBOM, 42 artifacts. Sidecar: `18681751…` (33-artifact `0b83acc` generation, 04:44Z). Live sensor: image `2026.09.29-lab5`, agent `0.1.1-lab` + in-place modules under `/opt/falcon-edge/src`. Edge HEAD: `f1c5def` (run start `45dfed0`). Falcon delivery: package `3ac6cd4`, publication `8282d3f`, pin copy `eb1191bc…`.

**Skew scenarios and concrete outcomes.**

| Scenario | Concrete outcome |
|---|---|
| Edge newer than pin (current) | Approval/review records describe a non-current release; reviewers verify a nonexistent digest; edge HEAD `f1c5def` is ahead of the manifest commit; no check detects any of it. |
| Edge release regenerated under the fixed name | Sidecar and reviewer acceptance bind superseded bytes; a manifest swap is undetectable; pin rebound without a rebuild makes verification fail everywhere. |
| Live card older than released images (lab5 vs lab7/lab8) | "What is running" cannot be rebuilt or attested from any shipped SBOM; replacement needs rebind. |
| Central package rollback | Edge side unchanged; packaged pin/dashboard revert while the edge keeps writing; root-owned files complicate rebuild. |
| Metric rename/label change (edge) or textfile path change (central) | Central series disappear silently or the exporter write fails; only timer journal records it; no alert. |
| Sensor clock skew >300 s / operator cert expiry | Heartbeats/renewals rejected (skew indistinguishable from outage); central loses quarantine/revoke/update control. |

**Boundary failure modes.**

| Event | Effect | Detection today |
|---|---|---|
| Edge sensor/agent stopped | Queue fills, heartbeats stop, commands undeliverable | WG per-peer rule only after 24 h; never-handshaked peers invisible (OBS-P1-005) |
| Edge CP / exporter stopped | Fleet metrics freeze; renewals/directives stop | None central (rules undeployed; mtime unalerted) |
| Tunnel down | Sensor cannot reach CP (only `10.99.0.1` configured); buffer blocks then queue | 24 h WG rule / dashboard |
| Central offline | Sensor buffers 2 GiB then queue; alert path dead; directives queued; duplicates on recovery (no dedupe) | Dead-man ≤26 h; R-27 residual accepted |
| DNS failure / host loss | Alt-ntfy fails (Sep 28 proof); all infrastructure down together | Journal only; external watcher ≤26 h; edge PKI local-only |

**Additive rule in practice.** Mostly respected edge→central for the metric file, but the edge-written dashboard entered the falcon tree before adoption (`cf7f5c4`), and the prepared rules deployment is explicitly non-additive — its own header says it edits the falcon compose file and recreates Prometheus. Secrets/backups live outside the falcon tree but inside the shared delivery surface. Central→edge signed updates are verified, but central path changes can silently break the edge exporter. Nothing enforces the rule mechanically.

**Paired upgrade/rollback.** No document defines the order of operations. Agent bundle updates are signature+digest+compile checked but the swap is not power-loss safe (no boot recovery, FLEET-P1-002); OS images have no A/B on Pi 3B (P7-G05 BLOCKED); central approval binding is defective (EVID-P0-001); pin rollback is undefined with no previous-manifest retention. A paired rollback cannot be performed atomically; the sides are released, verified, and reverted independently.

## Findings

Note: these are joint-system findings; component-level defects are referenced by ID and not re-filed.

### Finding ID: INTG-P1-001 - The prepared edge alert-rule deployment targets a plane the central alert path cannot deliver

- Severity: P1 · Confidence: High (both sides read; delivery semantics inferred from compose/relay configuration) · Area: INTG (alert-path integration)
- Evidence: `falcon-edge-build/automation/validation/deploy_edge_alert_rules.sh:1-7,21-31,61-66` (adds `rule_files`, mounts compose, recreates Prometheus, verifies only `/api/v1/rules`); `falcon-edge-build/config/prometheus/edge-alerts.yaml` (10 Prometheus-format rules); `falcon-build/config/prometheus/prometheus.yml` (no `rule_files`); `compose/central/docker-compose.yml` (no Alertmanager service); `bootstrap/90-alerting.sh:57-129,202-323` + drill scripts (Grafana-managed rules; `grafana.falcon.lab/api/alertmanager/grafana/...`). Symbol: Grafana rule provisioning vs Prometheus `rule_files`.
- What is happening: the only prepared remediation for "no alert covers the edge path" loads rules into Prometheus, but delivery in this stack is Grafana-unified-alerting → relay → ntfy; Prometheus would evaluate with no Alertmanager to route.
- Why it matters: the documented fix is both non-additive (edits the other repo, restarts its Prometheus) and ineffective (no notification); an operator could "complete" D-007 and still have zero edge alerting.
- User / business impact: silent edge outages continue while the team believes alerting was deployed; unplanned Prometheus downtime during the change.
- Security / privacy / reliability impact: no detection for fleet loss, capture drops or cert expiry; boundary erosion between the programs.
- Recommended fix: add the 10 scoped rules as Grafana-managed rules via the catalogue flow (or add Alertmanager and route it); keep it additive; validate end-to-end by stopping the exporter and asserting delivery on both ntfy instances, not by `/api/v1/rules`; re-check expression semantics against exporter metrics first.
- Suggested validation: simulated ACTIVE-sensor silence and exporter stop deliver FIRING + RESOLVED to lab and independent ntfy; nothing fires for retired/revoked residue.
- Owner suggestion: edge maintainer + falcon maintainer · Effort: M · Dependencies: D-007 owner decision, change window
- Status: open (cross-refs XREPO-P1-002, OBS-P1-004, prior INTG-P1-001)

### Finding ID: INTG-P1-002 - The pair has no joint release gate, upgrade order, or atomic rollback; both sides' gates pass over a broken pairing

- Severity: P1 · Confidence: High · Area: INTG (release integration)
- Evidence: `falcon-build/ci/validate.py:161-167` (only local checks; `grep EDGE_RELEASE_PIN` over `ci/`, `automation/` = 0 hits); edge `ci/validate.sh` validates only the edge tree, and the P10-G05 PASS binds a manifest generation (`18681751…`) that no longer matches the file on disk; observed disagreement across all six references (version matrix) with central 101 PASS / 1 N/A and edge 77 PASS / 8 BLOCKED / 3 IE; `docs/edge/EDGE_RELEASE_PIN.md` says only "Update it (new commit + digest)"; `profiles/pi/AB_STRATEGY.md`/P7-G05 BLOCKED; central `FINAL_RESPONSE.json` "image-version rollback not rehearsed".
- What is happening: each program gates itself; the only pairing mechanism is a hand-edited pin, and no gate or procedure fails when the pair is inconsistent.
- Why it matters: the observed P0 drift was producible precisely because both gates pass; a rollback on one side can silently invalidate the other side's verified state.
- User / business impact: approvals and reviewer verifications bind to wrong artifacts; incident rollback is improvised.
- Security / privacy / reliability impact: no supply-chain gate between the two released artifact sets.
- Recommended fix: add `automation/validation/verify_edge_pin.sh` wired into `ci/validate.py` (fail closed on digest/commit/SBOM/artifact mismatch) plus a paired-release checklist (freeze edge release → build manifest+sidecar atomically → freeze central package → rebind pin → deploy → record versions both sides) and per-side rollback (retain previous manifest digest; rebind, never hand-edit).
- Suggested validation: mutated pin fails CI; a dry-run paired release leaves pin == manifest == deployed digest == edge commit.
- Owner suggestion: release engineer (central) + edge maintainer · Effort: M · Dependencies: XREPO-P0-001
- Status: open (cross-refs XREPO-P0-001/P1-004/P2-003, FLEET-P1-001/P2-003, EVID-P0-001)

### Finding ID: INTG-P2-001 - Edge→central telemetry contract is implicit and unvalidated; one producer regression silently deletes the whole edge metric family

- Severity: P2 · Confidence: High · Area: INTG (telemetry contract)
- Evidence: `fleet_metrics.py:41-52` (comment: repeating HELP/TYPE per sensor made the node-exporter textfile collector reject the whole file during live deployment 2026-09-30; atomic tmp+replace write); host-only `falcon-edge-metrics.service` writes `/srv/falcon/textfile/falcon_edge_metrics.prom`; `compose/central/docker-compose.yml:291-294` mounts it read-only for the textfile collector; report 14: `node_textfile_mtime_seconds` / `node_textfile_scrape_error` exist live but no rule uses them; report 08: no `falcon_edge_*` rules in the live catalogue.
- What is happening: the contract (path, permissions, HELP-once, metric/label names, cadence) exists only in producer code; the consumer fails closed and silently, and nothing alerts on the missing family.
- Why it matters: an edge exporter change or a central mount/path change removes all fleet telemetry, and the failure looks like "no data" on a dashboard nobody may be watching.
- User / business impact: fleet blindness until a human notices; dashboards blank without explanation.
- Security / privacy / reliability impact: loss of the only fleet-wide monitoring signal for the edge estate.
- Recommended fix: add central staleness and `node_textfile_scrape_error` rules; add a producer self-check plus a metric-name/label snapshot test in edge CI; document and version the contract; add a canary series to separate "empty" from "broken".
- Suggested validation: rename a metric in a scratch exporter → central staleness alert fires; restore → resolved.
- Owner suggestion: edge maintainer + falcon maintainer · Effort: S/M · Dependencies: none
- Status: open (cross-refs OBS-P1-003, RES-P1-002, XREPO-004)

### Finding ID: INTG-P2-002 - No joint recovery/rebind procedure; the central clean-host path does not reconstruct the edge side of the pair

- Severity: P2 · Confidence: High · Area: INTG (joint DR)
- Evidence: `docs/phase9/CLEAN_HOST_REBUILD_RUNBOOK.md` has no "edge" occurrence (grep); central restore/clean-host drills are central-only (P9-G06/G09, reports 13/32); host-only `falcon-edge-{metrics,secrets-backup,operator-cert}` units have no repo unit file (INFRA-P2-003); edge PKI/DB backups are local-only (DR-P1-005); pin has no rebind-recovery steps; `onboard_lab_side.sh` is the only written sequence and depends on the host secrets dir and the repo tree.
- What is happening: after a host rebuild the monitoring stack can return from the runbook, but the edge control plane, trust anchor, exporter unit, operator cert and tunnel peer must be rebuilt from memory or host-only artifacts.
- Why it matters: recovery time for the fleet path is unbounded, and trust-anchor loss forces fleet-wide re-enrollment.
- User / business impact: hours-to-days added to recovery; every enrolled sensor must be re-onboarded if the CA is lost.
- Security / privacy / reliability impact: single-host custody of the fleet trust anchor; recovery depends on undocumented steps.
- Recommended fix: write `docs/edge/PAIR_RECOVERY_AND_REBIND.md` (peer → CP install → operator cert → exporter unit → verify heartbeat/metrics), commit the three unit files with an install step, add the edge PKI/DB archive to offsite, and rehearse on a scratch host.
- Suggested validation: clean-host rehearsal restores both sides, re-enrolls a scratch sensor, and shows fresh `falcon_edge_*` with no manual file copying.
- Owner suggestion: both maintainers · Effort: M · Dependencies: secret custody, INFRA-P2-003
- Status: open (cross-refs INFRA-P2-003, DR-P1-005, ARCH-P2-002, RES-P2-001)

### Finding ID: INTG-P2-003 - Central→edge operator control is unmonitored and its command state is not authoritative

- Severity: P2 · Confidence: High · Area: INTG (control path)
- Evidence: host-only `falcon-edge-operator-cert.service/timer` runs `renew_operator_cert.py` daily (threshold 15 days, no alerting, no repo unit); operator cert expires 2026-10-29 (report 43); `store.py:323` `consume_directive` has no callers (grep) and live metrics show pending directives on RETIRED sensors (`falcon_edge_sensor_pending_directives … 2`) with expired directives counted (report 08); `queue.py:126-138` `purge_expired` deletes `enqueued_at < iso_now()` — latent delete-all (RES-P2-002).
- What is happening: the credential that lets central quarantine/revoke/release/update sensors is renewed by an unmonitored host-only timer running edge code from a mutable tree, and the directive counters central sees do not prove delivery or consumption.
- Why it matters: central can silently lose fleet control (cert expiry) and cannot distinguish delivered, pending and expired commands.
- User / business impact: a compromised/lost sensor may remain reachable while dashboards show "pending"; operators cannot confirm a quarantine or revoke took effect.
- Security / privacy / reliability impact: degraded command-and-control assurance for the fleet.
- Recommended fix: add an operator-cert expiry/renewal-failure alert, wire or remove `consume_directive` and exclude expired directives from the pending count, fix the purge cutoff, and commit the timer units to the edge repo.
- Suggested validation: forced cert expiry fires an alert before lockout; executing a directive moves the pending count to 0; mixed-age `purge_expired` unit test.
- Owner suggestion: edge maintainer · Effort: S/M · Dependencies: INFRA-P2-003
- Status: open (cross-refs FLEET-P2-005, RES-P2-002, DATA-P2-004, API-P1-001)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Edge alerting "deployed" but mute | High | Medium | Silent fleet outages; Prometheus restart | INTG-P1-001 | Grafana rules/Alertmanager; E2E delivery test |
| Pair released with inconsistent identity | High | Certain today | Approvals/verification invalid | INTG-P1-002 | Pin verifier + paired checklist |
| Whole edge metric family vanishes silently | Medium | Medium | Fleet blindness | INTG-P2-001 | Staleness/scrape-error rules + contract test |
| Host loss without joint recovery | Medium | Low | Fleet re-enrollment, days of work | INTG-P2-002 | Joint runbook + offsite PKI + rehearsal |
| Operator lockout / false command state | Medium | Medium | No quarantine/revoke/update; wrong decisions | INTG-P2-003 | Cert alert; consume directives |

## Recommendations

**Immediate / release-blocking:** (1) Do not run `deploy_edge_alert_rules.sh --apply`; translate the 10 rules to the Grafana-managed path or stand up Alertmanager first (INTG-P1-001). (2) Add the pin verifier and paired-release checklist so no release ships with a stale pairing (INTG-P1-002).
**This week:** Add textfile staleness/scrape-error rules (INTG-P2-001); alert on operator-cert expiry and fix directive tracking (INTG-P2-003); commit the three host-only edge units (INFRA-P2-003).
**This month:** Write and rehearse the joint recovery/rebind runbook with encrypted offsite edge PKI/DB (INTG-P2-002); record and test the metric contract (INTG-P2-001); define per-side rollback and retain previous manifest digests (INTG-P1-002).
**Later:** contract versioning and automated skew detection across pin, manifest, edge HEAD and live sensor.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Pin verifier in `ci/validate.py` | Fails closed on the observed drift | `automation/validation/verify_edge_pin.sh`, `ci/validate.py` | mutated pin fails |
| Textfile staleness rule | Whole-family loss becomes visible | `bootstrap/90-alerting.sh` | stop timer → fire |
| Operator-cert alert | Prevents silent control lockout | `90-alerting.sh`, `export_monitor_metrics.sh` | forced threshold fires |

## Hardening Backlog

| Item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Grafana-native edge rules + E2E delivery proof | P1 | edge + falcon | M | D-007 |
| Paired release gate + rollback order | P1 | release engineer | M | pin verifier |
| Joint recovery/rebind runbook + offsite PKI | P1 | both | M | secret doctrine |
| Metric/API contract versioning + skew detector | P2 | both | M | CI hooks |
| Command-state authority (directive wiring, purge fix) | P2 | edge | S | none |

## Suggested Tests

- Integration: manifest sidecar `sha256sum -c` and pin verifier both fail closed on mutation.
- E2E: paired release drill — freeze edge release, rebuild manifest+sidecar, rebuild central package, rebind pin, verify every reference matches.
- Failure: stop `falcon-edge-metrics.timer` → central staleness alert; stop the edge CP → out-of-band silence alert (after INTG-P1-001).
- Failure: expire/rotate the operator cert in a scratch secrets dir → alert before lockout; directive execution decrements pending.
- DR: scratch-host rehearsal restores both sides from offsite+pinned artifacts without manual file copying.
- Security: revoked/expired sensor cert rejected at TLS, not only at route checks (FLEET-P2-005).

## Suggested Documentation Updates

- New `docs/edge/INTERFACES.md`: interface, owner, contract, failure mode, rollback (pin, manifest, tunnel, CP, metrics, alert rules).
- New `docs/edge/PAIR_RECOVERY_AND_REBIND.md`; link from `CLEAN_HOST_REBUILD_RUNBOOK.md` and `VPN.md`.
- `EDGE_RELEASE_PIN.md`: correct 15140/15141 ownership, replace the template-persistence claim, add rebind/rollback.
- Both contradiction ledgers: entries for pin/manifest/sidecar/live/HEAD skew; correct the edge-alert deploy plan to the Grafana path.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which artifact is the accepted edge release — `18681751…`, `3fa4a49c…`, or the live card? | Rebind target | Owner statement |
| Should edge rules become Grafana rules, or is Alertmanager being added? | Fix for INTG-P1-001 | Owner/decision-log entry |
| Do owner-custody copies of the edge CA and `backup_enc.key` exist off-host? | Joint recovery feasibility | Owner attestation |

## Prior-Run Finding Status (INTG lens, run 20260930-0320)

| Prior ID | Status now | Evidence |
|---|---|---|
| INTG-P0-001 pin↔delivery digest mismatch | still-open | pin `dffcbbb7…`, sidecar `18681751…`, actual `3fa4a49c…` (XREPO-P0-001) |
| INTG-P0-002 edge peer persistence/template drift | partially-fixed | `95-wireguard.sh:43-65` peer merge + regression check; `.30` live; template still lacks the peer |
| INTG-P1-001 no alert covers edge path | still-open | `edge-alerts.yaml` absent from falcon; no `rule_files`; D-007 deferred (INTG-P1-001) |
| INTG-P1-002 live code is edge working tree | still-open | `edge-control-plane.service:13-15`; exporter also runs from the tree (ARCH-P1-002) |
| INTG-P1-003 edge PKI/DB backup local-only | still-open | backups → delivery dir; falcon offsite excludes it (DR-P1-005) |
| INTG-P1-004 version skew across moving references | still-open | six references disagree (version matrix) |
| INTG-P2-001 boundary breach dashboard/ownership | partially-fixed | dashboard committed `cf7f5c4`; root-owned; rules script still writes into falcon repo |
| INTG-P2-002 WG peer admin inverted; runbook omits `.30` | partially-fixed | decision log records `.30`; `VPN.md`/port matrix still stale (INFRA-P2-001) |
| INTG-P2-003 secrets backup inside release surface | still-open | SSH keys, credentials, unencrypted backups in delivery dir (XREPO-P1-003) |
| INTG-P2-004 falcon-side record/alert drift | partially-fixed | catalogue part verified-fixed (31=31 incl. `falcon-wg-peer-stale`); port/pin text still stale |
| INTG-P2-005 shared-host resource risk unowned | still-open | root 82–83%, swap 4.8–5.5 GiB (ARCH-P1-001, RES-P1-005) |
| INTG-P3-001 pin misidentifies 15140/15141 | still-open | pin interface text unchanged |
| INTG-P3-002 `falcon-` prefix on edge units | not re-assessed | no change evidence |
| INTG-P3-003 cosmetic drift | not re-assessed | not re-checked |
| INTG-P3-004 control plane binds 0.0.0.0 | still-open | `edge-control-plane.lab.json:2`; ARCH-P2-001 |

## Cross-Reference Table (INTG ↔ domain)

| INTG ID | Related domain IDs | Relationship |
|---|---|---|
| INTG-P1-001 | XREPO-P1-002, OBS-P1-004, prior INTG-P1-001 | The prepared fix for the uncovered edge path cannot deliver |
| INTG-P1-002 | XREPO-P0-001, XREPO-P1-004, XREPO-P2-003, FLEET-P1-001, FLEET-P2-003, EVID-P0-001 | Joint gate/order/rollback absent; component defects referenced |
| INTG-P2-001 | OBS-P1-003, RES-P1-002, XREPO-004 | Unvalidated producer/consumer contract; silent family loss |
| INTG-P2-002 | INFRA-P2-003, DR-P1-005, ARCH-P2-002, RES-P2-001 | No joint recovery; edge side missing from central rebuild |
| INTG-P2-003 | FLEET-P2-005, RES-P2-002, DATA-P2-004, API-P1-001 | Control-path credential and command-state integrity |

## Appendix

- Read-only methods: `sha256sum`, `grep`, `ls -l`, `systemctl list-timers`, file reads; no services restarted, no files written outside this report.
- Evidence limits: effective nft rules, ntfy delivery and Grafana live rule state are `unverified` here (covered by reports 12/14); the live sensor was inspected by report 43, not re-probed.
- Counts: INTG-P1 ×2, INTG-P2 ×3. No new P0 (pairing P0s are XREPO-P0-001; claim-chain P0s are EVID-P0-001/002). Secrets are referenced by path/type only.
