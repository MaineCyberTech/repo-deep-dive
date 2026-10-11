# 33_incident_tabletop_exercise — Prompt 33 - Incident Tabletop Exercise

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `33_incident_tabletop_exercise.md` (area IR, prompt)

## Verification Performed

# Incident Tabletop Exercise

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c9` (branch `main`; `origin/main` = `584e1a3` + publication commits)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-11T05:00Z
- Auditor: subagent (IR)
- Area code: IR
- Scope limitations: no facilitated exercise was conducted by this audit (by design). The evaluation is a documentation/readiness audit plus reconciliation against live incident evidence from Oct 6-11. No on-call roster exists; external notification systems are reviewed only via their lab-side wiring.

## Scope

Reviewed incident doctrine, the tabletop scenario catalogue and facilitation kit, exercise records, escalation contacts, the breach notification procedure, rollback/CI-CD playbooks, backups, audit logs and observability as incident-response inputs at `f5cb7c9`, and reconciled them with the incidents that actually occurred in the window: the Oct 7-9 OpenSearch RED episode, the Oct 8-9 aggregator OOM loop, the Oct 9 capacity recovery, the Oct 10 offsite backup failure, the Oct 11 kernel-upgrade reboot with the Wazuh socket outage and the root-LV guard failure loop. Not reviewed: actual on-call behaviour (no roster), production-scale incident response (lab only).

## Evidence Reviewed

- `docs/phase7/runbooks/INCIDENT_RESPONSE.md` (severity :54-65, first 15 minutes :66-83, playbooks :84-221, communications :222-231, recovery verification :232-250, rollback/abort :251-265, post-incident review :266-290)
- `docs/phase9/exercises/TABLETOP_PACKAGE.md`, `EXERCISE_RECORD_TEMPLATE.md`, `DRY_RUN_WALKTHROUGH.md`, `scenarios/` (10 files incl. SCENARIO_05 total monitoring/alerting loss and SCENARIO_06 alert-delivery loss), `records/README.md`, `records/TABLETOP_KIT.md`
- `docs/security/ESCALATION_CONTACTS_TEMPLATE.md`, `BREACH_NOTIFICATION_PROCEDURE.md`, `CI_CD_INCIDENT_PLAYBOOK.md`
- `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` (postmortem format)
- `ledgers/decision_log.md` (last entry 2026-10-10T02:55Z), `ledgers/risk_register.md`
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md:178-183` (maintenance windows), `docs/runbooks/VPN.md:193`, `docs/runbooks/RUNTIME_AND_SCHEDULE.md:186`
- Live: `journalctl -u falcon-alert-relay.service` (Oct 9-11 incidents), `journalctl -b 0` (boot ordering), `journalctl -u falcon-disk-guard.service`, `last -x`, `/var/log/apt/history.log`, `systemctl list-timers`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `TABLETOP_PACKAGE.md:3` "no facilitated exercise has been run"; `records/README.md:3-6` "no exercise has been run and no record exists here yet"; `TABLETOP_KIT.md:3-8` | repo | Prior IR-P2-001 | Still open: status unchanged |
| `ESCALATION_CONTACTS_TEMPLATE.md` (field template; all roles OWNER-INPUT; no values collected) | repo | Prior IR-P2-002 | Still open |
| `decision_log.md` last entry 2026-10-10T02:55Z; Oct 9 rows cover the capacity/backup/OOM incidents | repo | Prior IR-P2-003 | Partially-fixed: Oct 10-11 events unrecorded |
| `decision_log.md` 2026-10-01T21:32Z claims the boot-order fix "verified CLOSED"; `journalctl -b 0` 02:27:44Z shows the same ordering cycle and the sockets were dead until 03:13:02Z | repo/live | Extended check: previous fixes stuck | Fails: recurrence |
| `journalctl -b 0` / apt history: kernel 6.8.0-142 -> 6.8.0-146, clean reboot 02:24-02:27Z; no decision-log entry; no post-reboot check run | live/repo | Maintenance-window doctrine | Gap |
| Scenario catalogue (10 scenarios incl. 5 and 6), exercise record template, comms templates, breach procedure | repo | Required special checks | Present on paper |
| Incident playbooks (probe/central compromise, secret disclosure, tampering, data exposure, supply chain) + severity/first-15-min/postmortem sections | repo | Doctrine completeness | Present |
| Live incidents Oct 9-11: OpenSearch red (Oct 7-9), OOM (Oct 8-9), offsite failure (Oct 10), reboot/socket/root-disk (Oct 11) | live | Reconciliation | Recorded only in raw evidence/decision log for Oct 9 |

## Executive Summary

Incident doctrine is strong on paper: a full response runbook with severity classes, a first-15-minutes procedure, five scenario playbooks, communications, recovery verification, rollback/abort criteria and an append-only post-incident review; a 10-scenario tabletop catalogue including the required Scenario 5 (total loss of the monitoring/alerting path) and Scenario 6 (alert-delivery loss); an exercise record template; a breach-notification procedure (with legal inputs marked OWNER/LEGAL-INPUT, not exercised); and a CI/CD incident playbook.

The readiness gaps are the same as the prior run plus new evidence: no facilitated exercise has ever been run (the records directory is still empty), escalation contacts remain placeholders, and the recurring incidents of the last week have no post-incident review - the Oct 10 offsite failure, the Oct 11 kernel reboot with the 46-minute Wazuh socket outage, and the ongoing root-LV guard failure loop are not recorded anywhere except raw evidence and live journals. The extended check "verify previous fixes stuck" fails for one important class: the 2026-10-01 decision-log entry claimed the Wazuh proxy boot-order fix was verified CLOSED, but the Oct 11 boot shows the identical systemd ordering cycle and the listeners were again started by hand. The kernel-upgrade reboot also violated the maintenance-window doctrine (no decision-log entry, no post-reboot verification).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Incident runbook | `docs/phase7/runbooks/INCIDENT_RESPONSE.md` | Severity, first 15 min, playbooks, comms, recovery, postmortem | Complete | Low | Strong doctrine |
| Tabletop catalogue | `docs/phase9/exercises/scenarios/` (10) | Exercise scenarios | Complete incl. Scenario 5/6 | Medium | Paper only |
| Exercise records | `docs/phase9/exercises/records/` | Signed session records | Empty | High | IR-P2-001 open |
| Facilitation kit | `records/TABLETOP_KIT.md` | Scenario 5 kit | Kit only | Medium | No session |
| Escalation contacts | `docs/security/ESCALATION_CONTACTS_TEMPLATE.md` | Contact tree | All OWNER-INPUT | High | IR-P2-002 open |
| Breach procedure | `docs/security/BREACH_NOTIFICATION_PROCEDURE.md` | Breach notification | Written; OWNER/LEGAL inputs; not exercised | Medium | |
| CI/CD playbook | `docs/security/CI_CD_INCIDENT_PLAYBOOK.md` | Pipeline incidents | Present | Low | |
| Postmortem format | `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` | Example record | Present | Low | Not reused for Oct 10-11 |
| Decision log | `ledgers/decision_log.md` | Append-only decisions/incidents | Last entry Oct 10 02:55Z | Medium | Oct 10-11 events missing |
| Maintenance windows | `docs/runbooks/CAPACITY_AND_TELEMETRY.md:178-183` | Planned-work procedure | Documented | Medium | Not followed for the reboot |
| Boot-order claim | `docs/runbooks/VPN.md:193` | Reboot recovery | Claims fixed 2026-09-30 | Medium | Contradicted live |
| Audit logs | journald + container logs; Grafana annotations | Incident forensics | Present | Low | 10-day boot journal |
| Backups | see DR report | Recovery input | Local healthy; offsite stale | High | DR-P1-002 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Incident docs | 4 | `INCIDENT_RESPONSE.md` complete | Recurring reviews not run | IR-P2-003 |
| Monitoring/alerting | 4 | 86 rules; delivery 200; canary/watcher | Noise; stuck-run gap | OBS findings |
| Rollback | 4 | `index_rename_rollback_drill.sh`; rollback sections | Not scheduled | Schedule |
| Security docs | 4 | Playbooks + breach procedure | OWNER/LEGAL inputs missing | Fill in custody |
| Deployment docs | 3 | Deploy/rollback docs | Reboot maintenance procedure not followed | IR-P2-005 |
| Operator docs | 3 | `OPERATOR_START_HERE.md`, runbooks | Boot checks manual | RES-P3-002 |
| Data breach process | 3 | Procedure written | Not exercised; inputs missing | Exercise |
| Backups | 3 | Local healthy; offsite stale | Offsite DR copy | DR-P1-002 |
| Audit logs | 4 | journald/containers/annotations | No centralized actor trail | ADMIN-P2-003 (prior) |
| Observability | 4 | Metrics/rules/freshness | Noise/reset issues | OBS findings |
| CI/CD failures | 4 | `CI_CD_INCIDENT_PLAYBOOK.md` | Not exercised | Exercise |
| Admin abuse | 2 | No centralized admin audit trail | Prior ADMIN-P2-003 | Keep tracked |

## Detailed Review

### Item: Exercise readiness (scenario catalogue, records, roles)

- Evidence: `TABLETOP_PACKAGE.md` (coverage matrix, roles, ground rules, record template), `records/README.md`, `TABLETOP_KIT.md`, `DRY_RUN_WALKTHROUGH.md`.
- What it does: defines 10 scenarios, roles, safety rails, a record template, and the Scenario 5 facilitation kit.
- Current controls: package + kit + templates; the 2026-10-01 paper walkthrough.
- Missing controls: a real facilitated session with an independent reviewer; measured out-of-band notification latency.
- Risks: the documented response path is untested; Scenario 5 exposure is paper-only.
- Recommended improvement: schedule the session (owner + responder + reviewer), start with Scenario 5, measure out-of-band latency, sign and index the record, repeat quarterly.
- Suggested tests: the session itself; a read-only smoke capture per the checklist.
- Suggested docs: `records/EX-<date>-*.md`.

### Item: Escalation and communication

- Evidence: `ESCALATION_CONTACTS_TEMPLATE.md` (13 OWNER-INPUT roles; values never collected), `BREACH_NOTIFICATION_PROCEDURE.md` (OWNER/LEGAL inputs), `TABLETOP_PACKAGE.md` §7 checklist.
- Missing controls: filled contact table (owner custody), one verified out-of-band channel, a communication-template fill-in.
- Risks: a second responder cannot follow the documented escalation path.
- Recommended improvement: complete the contacts in custody, verify one out-of-band channel end to end, record the verification.

### Item: Post-incident review and recurrence

- Evidence: `decision_log.md` (Oct 9 rows; last entry Oct 10 02:55Z), live journals (Oct 10 offsite failure; Oct 11 reboot/socket/root-disk).
- Current controls: an append-only decision log and a postmortem format.
- Missing controls: reviews for the Oct 10-11 events; a recurring pattern analysis (backup fragility, disk pressure, socket boot race).
- Risks: the same failures recur without a durable lesson record (already observed: socket race 3-4 times; disk pressure twice).
- Recommended improvement: run and record a post-incident review for the Oct 10-11 episode; add a monthly recurrence review of the alert/incident history.

### Item: Previous-fix verification (extended check)

- Evidence: `decision_log.md` 2026-10-01T21:32Z ("boot-order fix ... verified CLOSED"), `journalctl -b 0` 02:27:44Z (identical cycle), socket history.
- Finding: the verification method (units byte-identical, sockets active after a manual start) did not test the actual boot path; the fix does not hold.
- Recommended improvement: any "verified" claim for boot/recovery behavior must cite an artifact from an actual boot or an equivalent ordering test.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| IR-001 | Incident docs | `INCIDENT_RESPONSE.md` | Complete runbook | Recurring reviews | P2 | IR-P2-003 |
| IR-002 | Monitoring/alerting | 86 rules; relay 200 | Good | Noise; stuck-run | P2 | OBS findings |
| IR-003 | Rollback | rollback sections + drill | Documented + drilled | Not scheduled | P3 | Schedule |
| IR-004 | Security docs | playbooks; breach procedure | Present | Inputs missing | P2 | Fill in custody |
| IR-005 | Deployment docs | deploy docs | Present | Reboot procedure not followed | P3 | IR-P2-005 |
| IR-006 | Operator docs | operator runbooks | Present | Manual boot checks | P3 | RES-P3-002 |
| IR-007 | Data breach process | `BREACH_NOTIFICATION_PROCEDURE.md` | Written | Not exercised | P2 | Exercise |
| IR-008 | Backups | DR report | Local healthy | Offsite stale | P1 | DR-P1-002 |
| IR-009 | Audit logs | journald/containers | Present | No actor trail | P2 | ADMIN-P2-003 |
| IR-010 | Observability | metrics/rules | Good | Reset/noise | P2 | OBS findings |
| IR-011 | CI/CD failures | playbook | Present | Not exercised | P3 | Exercise |
| IR-012 | Admin abuse | no centralized trail | Partial | Prior ADMIN-P2-003 | P2 | Keep tracked |

## Findings

### IR-P2-001 - No facilitated tabletop exercise has been run; Scenario 5 (total monitoring/alerting loss) remains unexercised

- Severity: P2
- Confidence: High (repository status lines + empty records directory)
- Area: IR
- Evidence:
  - `docs/phase9/exercises/TABLETOP_PACKAGE.md:3`: "package delivered 2026-10-01; no facilitated exercise has been run against it"
  - `docs/phase9/exercises/records/README.md:3-6`: "no exercise has been run and no record exists here yet"
  - `docs/phase9/exercises/records/TABLETOP_KIT.md:3-8`: kit only; `IR-P0-001` remains OPEN
  - 10 scenarios exist incl. `SCENARIO_05_TOTAL_LOSS_MONITORING_ALERTING.md` and `SCENARIO_06_ALERT_DELIVERY_LOSS.md`
  - `runs/falcon-20261009-2117-full-08e20d1/follow_up_register.md:54` (IR-P2-001 open)
- What is happening: the scenario catalogue, roles, templates and the Scenario 5 kit all exist, but no session has been recorded; the required total-loss-of-monitoring scenario is paper-only and the out-of-band notification latency is unmeasured.
- Why it matters: the documented response path is unproven; a real monitoring-path loss would be handled ad hoc.
- Recommended fix: schedule and record a facilitated session (owner + responder + independent reviewer), starting with Scenario 5; measure out-of-band latency; sign and index the record; repeat quarterly.
- Suggested validation: a signed record in `records/`; the checklist items checked.
- Owner suggestion: owner
- Effort estimate: S (session) / recurring
- Status: still-open

### IR-P2-002 - Escalation contacts remain placeholders; the incident escalation path is unverified

- Severity: P2
- Confidence: High (template status + field content)
- Area: IR
- Evidence:
  - `docs/security/ESCALATION_CONTACTS_TEMPLATE.md`: field template (written 2026-10-01); every role is OWNER-INPUT across name/contact/out-of-band/hours/backup/verification; no values in the repository
  - `docs/phase9/exercises/TABLETOP_PACKAGE.md` §7 (pre-session checklist items 1-2 require the completed table and a verified out-of-band channel)
  - `docs/security/BREACH_NOTIFICATION_PROCEDURE.md` (OWNER-INPUT contacts section)
- What is happening: the contact tree has never been filled in owner custody and no out-of-band channel has been verified end to end.
- Why it matters: a second responder cannot execute the documented escalation path; the recent incidents were handled through the owner's own channels.
- Recommended fix: fill the contact table in owner custody (keep values out of the repository), verify at least one out-of-band channel end to end, and record the verification.
- Suggested validation: a recorded channel test (e.g. DO ntfy / phone) with timestamps.
- Owner suggestion: owner
- Effort estimate: S
- Status: still-open

### IR-P2-003 - Recurring incidents still lack post-incident review; the Oct 10-11 events (offsite state damage, kernel reboot/socket outage, root-LV guard loop) have no record

- Severity: P2
- Confidence: High (decision log + live journals)
- Area: IR
- Evidence:
  - `ledgers/decision_log.md` last entry 2026-10-10T02:55Z; the Oct 8-9 incidents do have root-cause rows (2026-10-09T20:15Z, 22:45Z)
  - Live events with no record: the 2026-10-10 offsite failure and upload-state truncation (`offsite.log`; state 0 bytes), the 2026-10-11 kernel-upgrade reboot with the Wazuh socket outage (`journalctl -b 0`) and the root-LV guard failure loop (`journalctl -u falcon-disk-guard.service`)
  - `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` shows the expected postmortem format (not reused)
  - `runs/falcon-20261011-0400-verify-main-584e1a3/follow_up_register.md:56` (IR-P2-003 partially-fixed: root-cause records exist for Oct 8-9; a recurring practice remains owner-side)
- What is happening: one-off root-cause rows exist for the Oct 8-9 episode, but the Oct 10-11 events have no timeline/root-cause/follow-up record, and no recurring review cadence exists.
- Why it matters: the same failure classes recur (socket boot race, disk pressure, backup fragility) without a durable lesson record.
- Recommended fix: run and record a post-incident review for the Oct 10-11 episode; add a monthly recurrence review of the incident/alert history.
- Suggested validation: an append-only review entry citing the journals and evidence captures.
- Owner suggestion: owner/platform
- Effort estimate: S
- Status: partially-fixed

### IR-P2-004 - Previous-fix verification failed for the Wazuh proxy boot ordering: the 2026-10-01 "verified CLOSED" claim is contradicted by the 2026-10-11 boot

- Severity: P2
- Confidence: High (decision-log claim + live boot journal + socket history)
- Area: IR
- Evidence:
  - `ledgers/decision_log.md` 2026-10-01T21:32Z: "the 2026-10-01 boot-order fix is verified CLOSED (the installed units are byte-identical to the repo, WantedBy=multi-user.target, the sockets enabled+active with 10.99.0.1:15140/15141 listening and peers handshaking)"
  - `journalctl -b 0` 2026-10-11T02:27:44Z: `sockets.target: Found ordering cycle on falcon-wazuh-{enroll,agent}-proxy.socket/start ... dependency on wg-quick@wg0.service/start ... Job ... deleted`; listeners only at 03:13:02Z (manual start; sudo journal)
  - `journalctl -u falcon-wazuh-agent-proxy.socket`: the same pattern at the 2026-10-01 01:47Z boot (listener up 03:21:32Z)
  - `docs/runbooks/VPN.md:193` still claims "fixed 2026-09-30"
  - `docs/phase9/exercises/TABLETOP_PACKAGE.md` extended-check intent ("verify previous fixes stuck")
- What is happening: the closure claim was based on the units being installed and the sockets active after a manual start, not on the actual boot path; the ordering cycle still deletes the socket jobs at every boot.
- Why it matters: it is the clearest example in the current estate of a "verified" claim that does not hold, and the pattern (symptom closure without boot-path proof) is exactly what an incident-review practice must catch.
- Recommended fix: correct the record (append-only) and `VPN.md`; require boot-path evidence (a real boot or an equivalent ordering test) for any boot/recovery "verified" claim; re-verify after the unit fix (RES-P2-002).
- Suggested validation: a post-fix boot (or ordering test) showing the listeners bind without manual action, recorded as evidence.
- Owner suggestion: platform
- Effort estimate: S
- Status: open

### IR-P2-005 - The 2026-10-11 kernel-upgrade reboot was not recorded as a maintenance window and had no post-reboot verification

- Severity: P3
- Confidence: High (apt history + journals + doctrine)
- Area: IR
- Evidence:
  - `/var/log/apt/history.log`: linux-image 6.8.0-142 -> 6.8.0-146; clean reboot 2026-10-11 02:24-02:27Z (`last -x`, `journalctl --list-boots`)
  - `docs/runbooks/CAPACITY_AND_TELEMETRY.md:178-183`: planned work should be muted/annotated and the window documented in `ledgers/decision_log.md`; no entry exists
  - No `post_reboot_verify.sh`/`boot_check_readonly.sh`/`boot_order_check.sh` run after 02:27Z
  - Degradations after the reboot: socket outage 02:27-03:13, Wazuh agent disconnected 02:44-03:15, Suricata uptime-reset alert 02:39-03:29, `Disk space low` 03:24
- What is happening: a planned kernel reboot was executed without the documented maintenance procedure and without a recorded verification.
- Why it matters: post-reboot degradations were only found via alerts; the doctrine exists but was not followed.
- Recommended fix: record planned reboots as maintenance windows (decision log), run/record the read-only boot checks, and note the expected reboot alert artifacts.
- Suggested validation: the next reboot has a decision-log entry and a recorded boot check.
- Owner suggestion: operator
- Effort estimate: S
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Response path untested (Scenario 5) | P2 | Medium | Slow/incorrect response | package status | IR-P2-001 |
| Escalation impossible for a second responder | P2 | Medium | Delayed response | template placeholders | IR-P2-002 |
| Failure classes recur without lessons | P2 | High (observed) | Repeat outages | socket race; disk pressure | IR-P2-003/004 |
| Boot path regressions ship as "verified" | P2 | Medium | Silent outages | boot-order claim | IR-P2-004 |
| Maintenance windows unrecorded | P3 | Medium | Surprise degradations | apt history/journals | IR-P2-005 |
| Offsite DR copy stale | P1 | High | Recovery window | DR report | DR-P1-002 |

## Recommendations

### Immediate / Release Blocking

- Fix the boot-ordering defect and re-verify with boot-path evidence; correct the record and `VPN.md` (IR-P2-004, RES-P2-002).
- Confirm the offsite copy is recovering (DR-P1-002).

### This Week

- Fill the escalation contacts in custody and verify one out-of-band channel (IR-P2-002).
- Record a post-incident review for the Oct 10-11 episode (IR-P2-003).
- Record the reboot as a maintenance window and run the boot checks (IR-P2-005).

### This Month

- Run the facilitated tabletop session, starting with Scenario 5; measure out-of-band latency (IR-P2-001).
- Exercise the breach procedure and the CI/CD playbook.

### Later / Platform Evolution

- Quarterly exercise cadence and a monthly recurrence review.
- Centralized admin/audit trail (prior ADMIN-P2-003).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Append-only correction of the boot-order claim | Restores trust in records | `ledgers/decision_log.md`, `docs/runbooks/VPN.md:193` | record cites the boot journal |
| Decision-log entry for the Oct 11 reboot | Follows the documented procedure | `ledgers/decision_log.md` | entry present |
| Complete the escalation table in custody | Enables a second responder | owner custody copy | channel test recorded |
| Schedule the tabletop (calendar + record template) | Closes the readiness gap | `docs/phase9/exercises/` | signed record |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Facilitated tabletop + quarterly cadence | P2 | owner | S | owner/reviewer time |
| Escalation contacts + out-of-band verification | P2 | owner | S | owner custody |
| Post-incident review practice (monthly recurrence review) | P2 | owner/platform | S | none |
| Boot-path evidence rule for "verified" claims | P2 | platform | S | none |
| Maintenance-window procedure enforcement | P3 | operator | S | none |

## Suggested Tests

- Manual: the facilitated tabletop (Scenario 5 first), with a recorded out-of-band latency measurement.
- Manual: a breach-procedure walkthrough with the legal inputs filled (or explicitly marked pending).
- Regression: a reboot or ordering test after the socket fix; a maintenance-window checklist dry run.
- CI: no new automated test required for IR; the boot-order fix is covered under RES.

## Suggested Documentation Updates

- `docs/phase9/exercises/records/`: add the first signed record after the session.
- `docs/security/ESCALATION_CONTACTS_TEMPLATE.md`: note the custody completion date (values stay out of repo).
- `docs/runbooks/VPN.md:193`: correct the boot-order claim.
- `ledgers/decision_log.md`: Oct 11 maintenance window + post-incident review entries.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: reference the reboot checklist from the maintenance section.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| When can the owner + reviewer hold the Scenario 5 session? | Closes IR-P2-001 | calendar/session record |
| Which out-of-band channel will be the primary? | Escalation reliability | owner decision + test |
| Was the Oct 10 offsite failure deliberately followed by the marker clear? | Record integrity | operator note |
| Does any other claimed "verified CLOSED" fix rely on a post-hoc symptom check rather than the failure path? | Systemic verification quality | audit of closure claims |

## Appendix

### Incident readiness inventory (live-relevant)

- Alerting: 86 Grafana rules; relay to lab ntfy + independent instance (both HTTP 200); weekly canary; DO dead-man watcher; relay-path-failure and freshness rules.
- Escalation: template only (owner custody pending).
- Runbooks: incident response, restore, disk pressure, VPN, notification/deadman, R2 cold tier, Wazuh indexer backup.
- Evidence: journald (10-day boot), container logs, Grafana annotations, raw evidence captures under `evidence/raw/`.
- Recovery inputs: local snapshots (healthy), offsite copy (stale, DR-P1-002), config archives (encrypted), key custody (attested).

### Scenario catalog (10)

1 probe compromise; 2 central compromise; 3 secret disclosure; 4 telemetry tampering; 5 data exposure; 6 supply chain; plus the phase9 scenario set including Scenario 5 total loss of monitoring/alerting and Scenario 6 alert-delivery loss. Severity classes, containment, communications and postmortem steps are defined in `INCIDENT_RESPONSE.md`.

### Communication templates

- Tabletop record template (`EXERCISE_RECORD_TEMPLATE.md`), incident comms section (`INCIDENT_RESPONSE.md` §6), breach notification drafts (`BREACH_NOTIFICATION_PROCEDURE.md` §templates) - all present; values for the breach path remain OWNER/LEGAL-INPUT.

## Findings

| ID | Severity | Title |
|---|---|---|
| IR-P2-001 | P2 | No facilitated tabletop exercise has been run; Scenario 5 (total monitoring/alerting loss) remains unexercised |
| IR-P2-002 | P2 | Escalation contacts remain placeholders; the incident escalation path is unverified |
| IR-P2-003 | P2 | Recurring incidents still lack post-incident review; the Oct 10-11 events (offsite state damage, kernel reboot/socket outage, root-LV guard loop) have no record |
| IR-P2-004 | P2 | Previous-fix verification failed for the Wazuh proxy boot ordering: the 2026-10-01 'verified CLOSED' claim is contradicted by the 2026-10-11 boot |
| IR-P2-005 | P3 | The 2026-10-11 kernel-upgrade reboot was not recorded as a maintenance window and had no post-reboot verification |
