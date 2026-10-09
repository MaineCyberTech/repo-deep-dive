# 33_incident_tabletop_exercise — Prompt 33 - Incident Tabletop Exercise

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `33_incident_tabletop_exercise.md` (area IR, prompt)

## Verification Performed

# Incident Tabletop Exercise

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` @ `08e20d1` (branch `main`)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-09T21:55Z
- Auditor: subagent (IR)
- Area code: IR
- Scope limitation: no facilitated exercise was conducted by this audit (by design); the evaluation is a documentation/readiness audit plus reconciliation against live incident evidence from Oct 6–9.

## Scope

Reviewed incident doctrine, the tabletop scenario catalogue and facilitation kit, exercise records, escalation contacts, breach notification procedure, rollback/CI-CD playbooks, backups, audit logs and observability as incident-response inputs at `08e20d1`, and reconciled them with live evidence of the incidents that actually occurred during the window (backup failures Oct 3/8/9, OpenSearch RED episode Oct 7–9, Vector OOM restart loop Oct 8–9). Not reviewed: actual on-call behaviour (no on-call roster exists), external notification systems beyond their lab-side wiring, and production-scale incident response (lab scale only).

## Evidence Reviewed

- `docs/phase7/TABLETOP_SCENARIO.md`, `docs/phase7/CLOSEOUT.md`, `docs/phase7/runbooks/INCIDENT_RESPONSE.md` (severity §3, first 15 min §4, playbooks §5, communications §6, recovery §7, post-incident review §9)
- `docs/phase9/exercises/TABLETOP_PACKAGE.md`, `records/README.md`, `records/TABLETOP_KIT.md`, `EXERCISE_RECORD_TEMPLATE.md`, `DRY_RUN_WALKTHROUGH.md`, 10 scenario files incl. `SCENARIO_05_TOTAL_LOSS_MONITORING_ALERTING.md` and `SCENARIO_06_ALERT_DELIVERY_LOSS.md`
- `docs/security/CI_CD_INCIDENT_PLAYBOOK.md`, `docs/security/BREACH_NOTIFICATION_PROCEDURE.md`, `docs/security/ESCALATION_CONTACTS_TEMPLATE.md`
- `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` (postmortem format)
- Live: `journalctl -u falcon-alert-relay.service` (Oct 6–9), `journalctl -u falcon-backup.service`, `ledgers/decision_log.md` rows, Grafana active alerts

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `TABLETOP_PACKAGE.md:3` / `records/README.md:3-6` | Repo | Exercise status | "no facilitated exercise has been run"; records index "(none yet)" |
| Scenario catalogue (10 files) | Repo | Required ≥8 + monitoring-loss | Present incl. Scenario 5 and 6 |
| `ESCALATION_CONTACTS_TEMPLATE.md:58-64` | Repo | Escalation path | 13 roles all OWNER-INPUT; IR-P2-005 open |
| `INCIDENT_RESPONSE.md` headings | Repo | Roles/severity/containment/comms/postmortem | All sections present |
| Relay journal Oct 6–9 | Live | Detection/delivery | 334 FIRING notifications delivered on both paths; backup/red-cluster episodes alerted |
| `journalctl -u falcon-backup.service` + decision log | Live | Recurring incidents | 3 backup failures; no postmortem record |
| `CI_CD_INCIDENT_PLAYBOOK.md §8` | Repo | CI/CD failure path | 6 scenarios; mutating steps untested |

## Executive Summary

The incident-response documentation layer is unusually complete: a master runbook with severity classes, first-15-minutes actions, six scenario playbooks, communications and append-only post-incident review; a breach-notification procedure with templates; a CI/CD incident playbook with six scenarios; and a 10-scenario tabletop catalogue that includes the two hardest cases — total loss of the monitoring/alerting path (Scenario 5) and alert-delivery loss (Scenario 6) — plus roles, ground rules, a record template, a facilitation kit and scoring. Live evidence shows the detection and delivery machinery actually works: during the Oct 7–9 incidents, "OpenSearch cluster red", "Backup stale", "Offsite backup stale" and the feed-silence rules fired and were delivered to both relay paths with HTTP 200.

The readiness gap is execution and ownership, not documentation. No facilitated exercise has ever been recorded (`records/` is empty; IR-P0-001/IR-P1-001/IR-P1-002 remain open in the repository's own records); the required Scenario 5 has only a paper walkthrough; and the escalation contact table is still a placeholder, so the documented path cannot be followed by a second responder. At the same time, the Oct 8–9 backup failure class recurred three times in a week without a post-incident review, and the OpenSearch RED episode ran ~45 hours — the very situations the tabletop programme is meant to rehearse.

## Findings Summary

| # | Severity | Title | Status |
|---|---|---|---|
| 1 | P2 | No facilitated tabletop exercise recorded; Scenario 5 (total monitoring loss) unexercised | open |
| 2 | P2 | Escalation contacts remain placeholders (IR-P2-005 open) | open |
| 3 | P2 | Recurring incidents lack post-incident review; backup-failure class has no root-cause record | open |

## Detailed Findings

### 1. No facilitated tabletop exercise recorded; Scenario 5 unexercised (P2)

The package is explicit about its own status: "no facilitated exercise has been run against it" (`TABLETOP_PACKAGE.md:3`), the records directory says "no exercise has been run and no record exists here yet" (`records/README.md:3-6`), and the records index is "(none yet — IR-P0-001 OPEN)". The 2026-09-23 session was a compressed three-scenario walkthrough; the 2026-10-01 Scenario 5 exposure was a paper walkthrough by the implementer, which the package itself says "is a paper walkthrough, not an exercise". The extended check — a scenario for total loss of the monitoring/alerting path — is therefore satisfied on paper but never rehearsed with participants, and the out-of-band notification latency target (≤60–90 min) is unmeasured.

**Fix:** schedule and record the facilitated session (owner + responder + independent reviewer), starting with Scenario 5; measure the out-of-band latency with a real low-priority message; sign and index the record; then repeat quarterly per the cadence. **Validation:** a signed record under `docs/phase9/exercises/records/` referencing real captures, plus the owner's append-only decision-log row.

### 2. Escalation contacts remain placeholders (P2)

`docs/security/ESCALATION_CONTACTS_TEMPLATE.md` is a field template: all 13 required roles (incident commander, secondary responder, reviewer, legal, regulator, insurer, law enforcement, customer, ISP, Cloudflare, DigitalOcean, registrar, key custodian) are OWNER-INPUT across name/contact/out-of-band/hours/backup/verification, and §5 states the values "were never collected" and "the incident runbook's escalation path is a placeholder and IR-P2-005 stays open". The current incidents were handled through the owner's personal channels, which works only while the owner is available and is not verifiable by a second responder. **Fix:** fill the table in owner custody, verify at least one out-of-band channel end to end, and record the verification log; keep sensitive values out of the repository as required.

### 3. Recurring incidents lack post-incident review; backup-failure class has no root-cause record (P2)

Live evidence shows three backup failures in seven days (Oct 3, 8, 9), a ~45-hour OpenSearch RED episode (Oct 7 19:20Z → Oct 9 16:41Z) and 23 Vector OOM kills on Oct 8–9. The in-repo record is a capacity decision-log row (2026-10-09T20:15Z) plus raw evidence files; there is no incident record with timeline, root cause, impact and follow-ups for the backup failure class, although `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` shows the expected format. The extended check "verify previous fixes stuck" is mixed: the Oct 3 Wazuh per-feed rule did stick (live), while host-memory-pressure noise (38 firings in 4 days) and backup fragility recur. **Fix:** run a post-incident review for the Oct 7–9 episode (backup + capacity), record it append-only, and add the recurring backup-failure pattern to the quarterly review.

## Strengths (verified)

- Required catalogue breadth: 10 scenarios including total monitoring/alerting loss and alert-delivery loss; roles, safety rails, scoring and record templates are all present.
- Incident doctrine covers severity, first 15 minutes, containment, communications, recovery verification, rollback criteria and append-only postmortem (`INCIDENT_RESPONSE.md` §3–§9).
- Breach notification procedure with decision authority, clock, channels, procedure and templates exists (`BREACH_NOTIFICATION_PROCEDURE.md`), owner inputs flagged.
- CI/CD incident playbook covers compromised tooling/credentials, broken release, bad bake, failed publication and CI unavailability, and honestly records untested steps.
- Detection and delivery worked in the real Oct 7–9 incidents: cluster-red, backup-stale and feed-silence alerts fired and were delivered on both relay paths (HTTP 200).

## Prior-Run Comparison

The prior run (`falcon-20261005-full-main-e267ce1`) recorded no IR findings, noting only that tabletop and playbook documents exist. This run confirms the documents exist and adds the live-verified gap: the programme has never been exercised, the contacts are placeholders, and the recurring incident classes from Oct 7–9 lack post-incident review. The repository's own records (IR-P0-001/IR-P1-001/IR-P1-002/IR-P2-005) agree these items remain open.

## Scorecard

| Category | Score | Evidence | Gap |
|---|---:|---|---|
| Incident docs | 4 | Master runbook + playbooks + postmortem format | No incident record for Oct 8–9 |
| Monitoring/alerting | 4 | Rules live and delivered; canary 3 paths | 6 rules not provisioned (see OBS) |
| Rollback | 3 | Rollback rehearsals + joint procedures | Not re-run recently; live-tree drift |
| Security docs | 4 | Breach, rotation, break-glass, CI secret gate | Contacts/owner inputs pending |
| Deployment docs | 4 | Production change plan, clean-host rebuild, joint release | Lab-scale only |
| Operator docs | 4 | Runbooks + OPERATOR_START_HERE | — |
| Data breach process | 3 | Procedure + templates present | Owner/legal inputs placeholders |
| Backups | 3 | Verified offsite; rehearsal 2026-10-01 | Oct 8–9 failure class unreviewed |
| Audit logs | 3 | OpenSearch audit indices, auditd | Retention gaps owned elsewhere |
| Observability | 4 | 77 live rules, dashboards, DO watcher | Source-drop blindness (OBS) |
| CI/CD failures | 4 | Playbook with 6 scenarios | Mutating steps untested; validate not run on GitHub |
| Admin abuse | 3 | Access logs + console rules | Public-router origin auth open (SEC) |

## Limitations

- No exercise was facilitated during this audit; findings are about readiness artifacts and live incident evidence only.
- Incident-response behaviour is inferred from alert logs and decision-log rows, not from a recorded timeline with human participants.
- The Oct 8–9 backup root cause remains probable (RED cluster from data-LV pressure), not proven, because the API response was not captured.

## Findings

| ID | Severity | Title |
|---|---|---|
| IR-P2-001 | P2 | No facilitated tabletop exercise has been run; Scenario 5 (total monitoring/alerting loss) remains unexercised |
| IR-P2-002 | P2 | Escalation contacts remain placeholders; incident escalation path unverified (IR-P2-005 open) |
| IR-P2-003 | P2 | Recurring incidents lack post-incident review; Oct 8-9 backup failure has no root-cause record |
