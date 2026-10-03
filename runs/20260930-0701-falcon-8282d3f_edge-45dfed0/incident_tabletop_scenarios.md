# Incident Tabletop Scenarios — Falcon Lab (companion artefact)

Companion to `33_incident_tabletop_exercise.md` (run `20260930-0701-falcon-8282d3f_edge-45dfed0`).
Facilitation kit for the owner-led lab; aligns with `docs/phase7/runbooks/INCIDENT_RESPONSE.md`
and `docs/phase7/TABLETOP_SCENARIO.md`. Scenario 5 (total loss of the monitoring path) is the
required extended check and has never been exercised.

## 1. Roles

| Role | Filled by (lab) | Responsibility |
|---|---|---|
| Facilitator | owner or agent | reads injects, keeps time, blocks out-of-scope work |
| Incident lead / commander | owner | declares severity, decisions, communications, closure |
| Technical responder | build agent / operator | runbooks, evidence capture, containment, recovery |
| Scribe | any second person, else lead | UTC timeline, decisions, evidence IDs, gaps |
| Communications | owner | notifications to contacts; post-incident summary |

Out-of-band requirement: at least one communication channel that does not depend on the lab
(phone/SMS/email from the DO server or the owner's phone) must be named **before** the session.

## 2. Severity model (lab)

| Sev | Definition (lab) | Examples |
|---|---|---|
| SEV-1 | Confirmed compromise/exposure, or the central store / monitoring path unavailable | host root compromise; OpenSearch down >15 min; both notification domains silent |
| SEV-2 | Strong suspicion or contained compromise of one zone | edge sensor suspected lost; DLQ identity spoofing; one ntfy domain down |
| SEV-3 | Single-service degradation, no adversary evidence | one healthcheck failing; disk guard fires below threshold; feed silence |
| SEV-4 | Hygiene/finding, no active impact | config drift; stale doc; unpinned image |

Rules: declare in `ledgers/decision_log.md` before acting; preserve evidence before changes;
never rebuild before the evidence list is captured; never use the lab ntfy topic as the record.

## 3. Scenario catalogue (10)

Each scenario: **Injects → Expected actions → Success criteria → Detection gap to note.**

### Scenario 1 — Sensor silence during a security event (SEV-2/3)
- Injects: `falcon-sensor-silence` fires at 02:10 (no indexed events 15 min); EVE last flush 02:04,
  Suricata `drop=0`; gateway NetFlow still flows; device syslog shows an external port-scan.
- Expected: confirm scope (EVE vs all ingestion); check `falcon-probe-vector-edge-1`,
  pmacctd/Suricata, disk, buffer; preserve before restarting; decide failover vs accepted gap;
  record the gap window; root-cause (flap, disk, DLQ).
- Success: alert acknowledged <2 min, scope <10 min, evidence preserved, gap recorded, owners set.
- Gap: adversarial-cause path never exercised (runbook status); no disk-buffer alert for the
  syslog/NetFlow senders (R-27 residual).

### Scenario 2 — Credential exposure on the central host (SEV-1)
- Injects: repo scan finds a service password in a captured log; the credential is valid for an
  internal service behind Traefik; Cloudflare Access logs show two unfamiliar IPs with access.
- Expected: identify scope and every stored copy (logs, indices, backups, git history); rotate in
  parallel with evidence collection; confirm old value fails; review Access policy; check
  auditd/OpenSearch for lateral movement (C-28/R-17 pattern).
- Success: rotation <30 min from confirmation, old credential invalid, logs reviewed, incident
  record with evidence, notification decision made.
- Gap: full rotation drills for some classes are untested (`CERTIFICATE_AND_SECRET_ROTATION.md`
  status); OSSEC keys accepted as-is (EX-21).

### Scenario 3 — Disk pressure with write failures (SEV-3)
- Injects: disk warning >86% and climbing to 99% in 10 min; aggregator bulk write failures, DLQ
  grows; backups due in 30 min.
- Expected: identify growth source; choose rotate/delete/throttle; preserve recent evidence;
  validate OpenSearch health and feed continuity; run/defer backup with recorded RPO impact.
- Success: writes restored <20 min, loss bounded and recorded, RPO stated.
- Gap: disk-guard reclaim has never fired live (13 RES-P2-001); ISM delete never reached;
  watermarks not enforced on the single node.

### Scenario 4 — WireGuard tunnel loss (SEV-2)
- Injects: `falcon-vpn-tunnel-stale`/`falcon-wg-peer-stale` fires; the DO site stops delivering syslog
  over TLS; handshake age grows past the threshold; a key rotation was performed last week.
- Expected: preserve `wg show`, conf, and backup files; compare live conf vs persisted conf;
  check endpoint port (5182) and key persistence (R-30 class); restore with `wg syncconf`; verify
  bidirectional ping and an encrypted telemetry marker.
- Success: tunnel restored, alerts cleared on both ntfy paths, provenance recorded.
- Gap: never-handshaked peers are invisible (13 RES-P1-002); per-peer rule is 24 h.

### Scenario 5 — Total loss of the monitoring/alerting path (SEV-1) — required
- Injects: the lab host loses power at 10:59 (all dashboards, Grafana, OpenSearch, ntfy, relay
  gone); the DO watcher is healthy; no notification arrives; at 12:30 the owner asks "is the lab
  up?"; the edge sensor is still roaming with queued data.
- Expected: operate blind — use the DO watcher/`falcon_site_watcher_last_run_timestamp_seconds`
  and DO ntfy as the only truth; declare the incident from out of band; wait for/enable auto-start
  (`onboot=1`), then run `post_reboot_verify.sh`; verify feeds, alerting, VPN, firewall; measure
  the gap start/end; record the notification latency and fix the detector (relay-path canary,
  tighter heartbeat).
- Success: total-loss detected by the documented external path within the documented threshold;
  recovery verified 50/50; gap and latency recorded; at least one detector improvement actioned.
- Gap (evidence, not hypothetical): 2026-09-28 outage produced **no** external notification; the
  watcher threshold is 26 h and the heartbeat is daily; a relay-only failure is invisible.
  See 13 RES-P0-002/RES-P1-001 and 33 IR-P1-001.

### Scenario 6 — Alert-delivery path loss while the lab looks healthy (SEV-1)
- Injects: `falcon-alert-relay` dies; Grafana keeps evaluating and firing; the heartbeat keeps
  posting nightly; the DO watcher stays quiet; the dashboard's active-alert counter shows 3 firing.
- Expected: discover via a scheduled canary that must arrive on the DO instance; confirm relay
  probe metric; restart/replace the relay; replay the missed alerts; verify both domains; record
  the blind window.
- Success: canary absence detected on the next cycle; missed deliveries replayed; the gap recorded.
- Gap: no canary exists; `falcon-service-down` for the relay routes through the relay itself.

### Scenario 7 — Backup/offsite failure discovered before host loss (SEV-2)
- Injects: the offsite upload silently fails at 03:34; only the local snapshot succeeds; the
  backup-stale rule stays green; three days later the owner asks for the restore window.
- Expected: check offsite inventory/freshness; validate a sample read-back; re-run with the fix;
  confirm new-services archives; rehearse a scratch restore; add/verify the offsite detector.
- Success: offsite fresh and proven; detector exists and fires on a forced failure; RPO/window
  stated.
- Gap: no offsite alert (13 RES-P0-001); new-services verification unproven (RES-P1-006).

### Scenario 8 — Edge sensor lost or re-imaged (SEV-2)
- Injects: the sensor stops heartbeating; last heartbeat age grows; queued data ages; the device
  may have been lost/stolen; the lab has no edge alert rule deployed.
- Expected: confirm via dashboard + control-plane DB; decide quarantine/revoke; revoke peer and
  cert; review the spool; re-image/re-enrol with a fresh token; rotate the WG key; verify no
  telemetry from the old identity.
- Success: revocation and re-enrolment evidenced; loss window bounded; runbook updated.
- Gap: edge alert rules undeployed; device outage/backlog drills pending (33 IR-P2-006).

### Scenario 9 — Data breach / exposure (SEV-1, production framing)
- Injects: a backup archive containing secrets is found in a release/handoff directory; the
  signed manifest lists it; an external researcher emails a screenshot of the archive name.
- Expected: contain (move/limit access, stop new releases); preserve evidence (hashes, accesses);
  identify affected credentials and rotate; assess reportability; notify owner/data authority per
  the (to-be-written) breach procedure; publish nothing externally without owner approval.
- Success: exposure contained and rotations done; notification decision recorded; evidence bundle
  hashed; prevention actions assigned.
- Gap: no breach annex/timeline; secrets backups have appeared in the delivery surface before
  (prior INTG-P2-003).

### Scenario 10 — CI/CD credential exposure (SEV-1/2)
- Injects: the image-bake workflow logs show a masked-but-recoverable secret; a badge/artifact is
  public for a moment; the claim token may still be valid; the release asset includes credentials.
- Expected: rotate CI secrets and the claim token; revoke/delete affected artifacts/releases;
  audit run logs and artifact downloads; re-bake; confirm edge claim rejects the old token; record
  R-012 decision (approval gate vs accepted controls).
- Success: old credentials invalid, exposure audited, release re-cut, owner decision recorded.
- Gap: no CI incident playbook; environment approval unavailable on the current plan (R-012).

## 4. Communication templates

### 4.1 Incident declaration (ntfy + ledger entry + out-of-band if SEV-1)
```text
[SEV-<n>] <short title> — declared <UTC> by <lead>
What: <one line>. Impact: <feeds/store/alerting/edge>. Scope: <known | unknown>.
Actions: <containment started>. Next update: <UTC +30 min>. Evidence: <capture id>.
```

### 4.2 Status update (every 30 min for SEV-1, 60 min for SEV-2)
```text
[SEV-<n> UPDATE <UTC>] <title>
Status: <investigating | contained | recovering | monitoring>.
Findings: <facts only>. Gaps: <window start-end or unknown>. Next: <action + owner + time>.
```

### 4.3 Resolution / closure
```text
[SEV-<n> RESOLVED <UTC>] <title>
Detection: <how>. Duration: <start-end>. Data impact: <none | bounded window>.
Verified: <commands/captures>. Follow-ups: <IDs>. Postmortem due: <date+5d>.
```

### 4.4 Out-of-band page when the lab is down
```text
FALCON LAB DOWN suspected. Last known good: <UTC>. Watcher last run: <UTC>.
Owner action: verify power/VM onboot; do not assume monitoring. Reply to acknowledge.
```

## 5. Postmortem template (append-only; no history rewrite)

1. **Header**: incident ID, severity, detection time, resolution time, duration, detect method.
2. **Impact**: services, data window, alerting gap, tenant/privacy scope (lab: synthetic).
3. **Timeline (UTC)**: every action with actor, command, result, evidence ID.
4. **Root cause**: technical + contributing factors (use 5-whys once).
5. **What went well / what failed**: especially detector behaviour and docs accuracy.
6. **Actions**: owner, due date, verification command; each becomes a ledger row/risk entry.
7. **Evidence index**: captures, hashes, redactions.
8. **Sign-off**: lead; append to `ledgers/decision_log.md`; never edit prior entries.

## 6. Exercise cadence and scoring

- Cadence: quarterly full session (≥2 scenarios, 60–90 min) + one injected walk-through per month
  (15 min, any scenario); always run Scenario 5 at least once per quarter.
- Facilitator notes: run against captured evidence when a live failure is unethical; time-box
  injects; force at least one out-of-band notification per session.
- Scoring sheet (per scenario): alert recognised/acknowledged · runbook located and usable ·
  evidence preserved before change · containment/rollback executed · communication and gap
  recorded · follow-ups with owners. Score each pass/partial/fail; a fail becomes a finding.

## 7. Pre-session checklist (owner)

- [ ] Escalation contacts table completed (out-of-band channels listed, not in the repo if sensitive).
- [ ] DO watcher config captured and pasted into the runbook (threshold, cadence, blind spots).
- [ ] ntfy subscriptions verified on both domains; do-not-disturb off during the session.
- [ ] Evidence wrapper works: `automation/evidence/capture.sh --sudo --gate <GATE> --name <step> -- <cmd>`.
- [ ] Decide which scenarios are tabletop vs live (no destructive steps without owner sanction).
- [ ] Record the session in `docs/phase7/CLOSEOUT.md` (append-only) and `ledgers/decision_log.md`.

## 8. Known detection gaps referenced by these scenarios

| Gap | Status | Tracker |
|---|---|---|
| Offsite backup failure silent | partially-fixed | 13 RES-P0-001 |
| Relay-only alert-path failure invisible | open | 13 RES-P0-002 |
| Total-loss detection ≤26 h; no real-time notice | still-open | 13 RES-P1-001 / 33 IR-P1-001 |
| Never-handshaked WG peers invisible | still-open | 13 RES-P1-002 |
| Monitor freshness (exporter/probe/guard/watcher) unalerted | still-open | 13 RES-P1-003 |
| Edge path has no deployed alert rule | still-open | 13 RES-P1-004 |
| Edge PKI/DB backup local-only | still-open | 13 RES-P1-005 |
| New-services backup verification unproven | unverified | 13 RES-P1-006 |
| Root LV growth unguarded | still-open | 13 RES-P1-007 |
| Disk-guard reclaim never exercised | open | 13 RES-P2-001 |
| Reboot/boot-order recurrence | partially-fixed | 33 IR-P2-002 |
| Data-breach procedure missing | open | 33 IR-P2-001 |
| Escalation contacts/templates missing | open | 33 IR-P2-005 |
