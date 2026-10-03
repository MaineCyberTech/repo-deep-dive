# Incident Tabletop Exercise

## Audit Metadata

- Audit name: `repo-deep-dive` · Profile: `falcon-lab` · Area: IR
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repos: falcon-build `main@8282d3f` · falcon-edge-build `main@f1c5def` (run label names edge `45dfed0`; HEAD moved 6 commits)
- Generated: 2026-09-30T14:20Z · Auditor: read-only wave-1 subagent (prompt 33)
- Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/33_incident_tabletop_exercise.md`
- Companion: `incident_tabletop_scenarios.md` (10 scenarios + templates, same folder)
- Scope limits: no root (postmortem/incident captures partly root-only); no live alert/Grafana query; exercise not re-run; falcon tree has one in-flight uncommitted offsite capture

## Scope

Reviewed: incident docs, severity/roles, monitoring/alerting (falcon + edge), rollback, security/deployment/operator docs, data-breach handling, backups/restore evidence, audit logs, observability, CI/CD failure exposure, admin-abuse and tenant-isolation applicability, the exercise record (P7-G09; edge P8-G06), and durability of the 2026-09-27/28 fixes and disk trajectory. Not reviewed: facilitation quality (cannot be re-run read-only), root-only logs, DO watcher internals, non-repo legal obligations.

## Evidence Reviewed

- Incident/ops docs: `docs/phase7/runbooks/INCIDENT_RESPONSE.md`, `docs/phase7/TABLETOP_SCENARIO.md`, `docs/phase7/CLOSEOUT.md`, `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md`, `docs/phase9/NOTIFICATION_SEPARATION_RUNBOOK.md`, `docs/phase9/OWNER_INPUTS_REQUIRED.md`, `docs/runbooks/OPERATOR_START_HERE.md`, `docs/phase8/PRODUCTION_CHANGE_PLAN.md`, `docs/phase9/review/PRODUCTION_VERDICT.md`.
- Ledgers: `decision_log.md`, `risk_register.md`, `exception_register.md`, `gate_ledger.csv`, `phase9_gate_ledger.csv`, `test_execution.csv`.
- Monitoring: `bootstrap/90-alerting.sh`, `docs/phase9/ALERT_CATALOGUE.yaml`, `automation/validation/{service_probe,export_monitor_metrics,heartbeat,disk_guard}.sh`, `config/grafana/dashboards/central-overview.json`, live `/srv/falcon/textfile/*.prom`.
- Edge: `docs/runbooks/INDEX.md` + 15 runbooks, `docs/phase8/CLOSEOUT.md`, `closeout/REVIEW-2026-09-30.md`, `docs/GITHUB_CI.md`, edge `ledgers/*`.
- Prior run: `/home/user/repo-deep-dive/runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `gate_ledger.csv:90` vs `CLOSEOUT.md:16` and `:77` | ledger+doc | P7-G09 status | PASS and INSUFFICIENT_EVIDENCE coexist — contradiction (IR-P2-003) |
| `evidence/raw/P7-G09/20260923T033318Z_tabletop-session.out` + closeout session | evidence | actual exercise | A/B/C run compressed/async; several partial scores — reproduced |
| `INCIDENT_RESPONSE.md:79,266-276` | doc | untested paths | mutating commands untested; no incident declared; adversary-silence unexercised |
| `decision_log.md:98`; `NOTIFICATION_SEPARATION_RUNBOOK.md:43-49` | ledger+doc | total-loss detection | watcher 26 h; 30-min unreachable clause unevidenced (IR-P1-001) |
| `decision_log.md:126,136-137`; `test_execution.csv` T-P9-G02-353/T-P9-G08-375 | ledger+evidence | 09-27/28 fix durability | fixes installed; hookscript not yet exercised by a VM start (IR-P2-002) |
| Live `df`/`free` 14:20Z + `falcon_disk_guard_reclaims_total 0` | observation | disk trajectory | data 62% stable; root 83%; guard never reclaimed (Appendix A) |
| Edge `closeout/REVIEW-2026-09-30.md` + `docs/phase8/CLOSEOUT.md` | docs | edge readiness | independent review PASS (lab scope); edge alerts undeployed; 3 runbooks walked |
| `OWNER_INPUTS_REQUIRED.md` (OD-12/OD-18 REQUESTED) vs `phase9_gate_ledger.csv:2` (P9-G01 PASS) | docs | escalation contacts | owner-input doc stale vs PASS/verdict (IR-P1-002/IR-P2-003) |

## Executive Summary

The lab has real incident doctrine (severity model, scenario guide, append-only postmortem, 31-rule catalogue with runbook links, tested dual-notification domain) and now one executed tabletop (P7-G09, 2026-09-23, three scenarios) plus an edge runbook walk (P8-G06). Live operations produced genuine resilience evidence: the 09-28 power outage with 50/50 post-reboot verification, the 09-27 host-OOM incident with persistent host hardening, and the 09-24 19 h VPN outage (R-30) now covered by persistence controls. Gaps: no scenario for total loss of the monitoring/alerting path itself; the programme is one compressed 3-scenario session against a ≥8-scenario requirement; communication/escalation artefacts are placeholders; and incident-support documents contradict the live state (risk register says no VPN/no SPAN; runbooks describe a lab without offsite; verdict says 28 rules vs 31 live). Fix durability is mixed: power/OOM hardening persists but the OOM hookscript has not yet been exercised, and the disk guard has never reclaimed. Findings: 2 × P1, 5 × P2, 1 × P3.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Incident runbook | `docs/phase7/runbooks/INCIDENT_RESPONSE.md` | detect→contain→recover | written; mutating steps untested | Med | §6 claims P9-G07 PASS |
| Severity model | same §3 | SEV-1…4 | written | Low | no breach timeline |
| Tabletop guide | `docs/phase7/TABLETOP_SCENARIO.md` | exercise kit | 3 scenarios; escalation placeholder | High | no monitoring-loss scenario |
| Tabletop record | `docs/phase7/CLOSEOUT.md` session | P7-G09 | executed 09-23, compressed | Med | partial scores |
| Postmortem sample | `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` | incident record | open verification checklist | Med | R-29 still OPEN |
| Monitoring/alerting | `bootstrap/90-alerting.sh`, catalogue (31) | detect+deliver | live; TLS window 6 h | Med | no edge/offsite/watcher/alert-eval rules |
| Dead-man | DO watcher + daily heartbeat | total-loss alarm | live; 26 h | High | relay blind spot (13 RES-P0-002) |
| Rollback | `docs/phase8/PRODUCTION_CHANGE_PLAN.md` | cutover rollback | draft; EX-23 no-change | Med | no cutover performed |
| Backups/restore | `RESTORE.md`, P9-G06/G09 | data recovery | proven 09-23 | Low | central-only rehearsal |
| Audit logs | `security-auditlog-*`, auditd, evidence index | forensics | live | Med | retention gap on audit indices |
| Edge runbooks | edge `docs/runbooks/` (15) | sensor IR | many device drills pending | Med | no joint lab↔edge runbook |
| CI/CD | falcon `.github/workflows/validate.yml`; edge `docs/GITHUB_CI.md` | pipeline | new 09-30; credential bakes | Med | no CI playbook; R-012 open |

## Domain Scorecard

| Category | Score | Evidence | Gap | Action |
|---|---:|---|---|---|
| Incident docs | 3 | runbook+guide+sample | 3 scenarios; templates/contacts; monitoring-loss scenario | adopt companion |
| Monitoring/alerting | 4 | 31 rules; dual ntfy; V-5 fixed | edge/offsite/watcher/alert-eval rules | close 13-report gaps |
| Rollback | 3 | plan + P6-G07 rehearsal | no real upgrade/cutover | drill + capture |
| Security docs | 3 | threat model, rotation, exceptions | rotation drills thin | schedule |
| Deployment docs | 3 | bootstraps, rebuild runbook | host-only controls | encode + test |
| Operator docs | 3 | OPERATOR_START_HERE | stale runbooks; no blind-ops page | refresh |
| Data breach process | 2 | runbook §5.5; OD-14 pending | no timeline/templates | write annex |
| Backups | 3 | P9-G06/G09; offsite fixed 09-30 | offsite detector; edge PKI | see 13 |
| Audit logs | 3 | auditlog/auditd/append-only | retention + breach queries | ISM + templates |
| Observability | 3 | dashboards/metrics/probes | monitor freshness unalerted | see 13 |
| CI/CD failures | 2 | workflows + GITHUB_CI | no playbook; approval gap | document/decide |
| Admin abuse | N/A | no first-party console (profile §4/26) | covered by 06/24 | keep N/A with evidence |

## Detailed Review

- **Incident docs/exercise**: roles and scoring exist; missing monitoring-loss scenario, ≥8-scenario catalogue, comms templates, verified contacts, non-compressed session, cadence (IR-P1-001/002).
- **Monitoring/alerting/dead-man**: dual ntfy + resolve + labels; relay-path canary absent; edge and offsite rules absent; total-loss 26 h (13 RES-P0-002/001/003/004).
- **Rollback/recovery**: rollback plan draft; P9-G13 N/A; restore proven; real component upgrade and edge outage drills pending.
- **Data breach**: one paragraph; no reportable-breach definition, recipients, timelines, or bundle procedure (IR-P2-001).
- **Backups/audit logs**: daily snapshot+offsite, rehearsed restore; audit-index retention and breach-scope query playbook missing.
- **CI/CD + edge readiness**: validated/pinned pipelines and boot smoke; no CI incident playbook; edge alerts undeployed; 5 edge runbooks device-gated (IR-P2-004/005, IR-P3).

## Scenario / Control Matrix

| ID | Scenario/control | Evidence | Control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| IR-001 | Incident docs | runbook+guide+sample | severity/containment/postmortem | monitoring-loss scenario; currency | P1 | companion catalogue |
| IR-002 | Monitoring/alerting | 31 rules; P9-G07 | strong | relay blind spot; edge/offsite rules | P1 | see 13 RES-P0-002/001/003 |
| IR-003 | Rollback | plan + rehearsal | documented | real upgrade untested | P2 | drill + capture |
| IR-004 | Security docs | threat model/rotation | good | full rotation drill thin | P2 | schedule |
| IR-005 | Deployment docs | bootstraps/rebuild | good | host-only controls | P2 | encode + test |
| IR-006 | Operator docs | OPERATOR_START_HERE | good triage | stale runbooks; no blind-ops page | P2 | refresh |
| IR-007 | Data breach process | runbook §5.5 | minimal | no timeline/templates | P2 | write annex |
| IR-008 | Backups | P9-G06/G09 | proven restore | offsite detector; edge PKI | P1 | see 13 |
| IR-009 | Audit logs | auditlog/auditd/evidence | live | retention + queries | P2 | ISM + templates |
| IR-010 | Observability | metrics/dashboards | strong | freshness unalerted | P1 | see 13 RES-P1-002 |
| IR-011 | CI/CD failures | workflows | new/validated | no playbook; bake approval | P2 | document/decide |
| IR-012 | Admin abuse | N/A profile | N/A | none | N/A | covered by 06/24 |

## Findings

### Finding ID: IR-P1-001 - No tabletop scenario for total loss of the monitoring and alerting path

- Severity: P1 · Confidence: High · Area: IR (tabletop)
- Evidence: `TABLETOP_SCENARIO.md:17-65` (only sensor silence, credential exposure, disk pressure); `gate_ledger.csv:90` (three scenarios run); no blind-operations procedure in `INCIDENT_RESPONSE.md`; `NOTIFICATION_SEPARATION_RUNBOOK.md:43-49` + `decision_log.md:136` (09-28: 4.5 h outage, no external notification).
- What is happening: the programme never rehearses losing the lab's own eyes/voice, including operating while blind.
- Why it matters: this is the flagship failure mode for a monitoring system and it already occurred (power outage).
- Impact: an outage may be reported by a human hours later; no validated failover-to-DO operation.
- Fix / validation: run Scenario 5 from the companion catalogue; add a blind-ops checklist; measure notification/latency; record in ledgers.
- Owner/effort/deps: owner (incident lead) · M · DO access, owner window.
- Status: open.

### Finding ID: IR-P1-002 - Exercise coverage and artefacts fall short of the required catalogue

- Severity: P1 · Confidence: High · Area: IR (exercise quality)
- Evidence: `TABLETOP_SCENARIO.md:67-74` escalation matrix is a placeholder; `CLOSEOUT.md` session is compressed/async with partial scores ("containment steps not stated", follow-ups "not stated"); no communication/postmortem templates in-repo; prompt 33 requires ≥8 scenarios and templates.
- What is happening: one 3-scenario compressed session is the entire exercise record; escalation/comms artefacts are unfilled.
- Why it matters: responders lack a practiced, repeatable comms and escalation path.
- Impact: slower, less consistent incident response.
- Fix / validation: adopt the 10-scenario catalogue + templates; run a full 60–90 min session with complete scoring.
- Owner/effort/deps: owner+falcon maintainer · M · owner time, contacts.
- Status: open.

### Finding ID: IR-P2-001 - Data-breach notification process is a paragraph, not a procedure

- Severity: P2 · Confidence: High · Area: IR (privacy)
- Evidence: `INCIDENT_RESPONSE.md:184` ("owner and, for real personal data, the data authority"); `:270-276` (no incident declared; untested); production privacy authority OD-14 pending in `OWNER_INPUTS_REQUIRED.md`.
- What is happening: no reportable-breach definition, recipients, timelines, or templates; lab data is synthetic, so this is production readiness.
- Why it matters: a real exposure at production would need a rehearsed path.
- Impact: notification/compliance delay.
- Fix / validation: write `docs/runbooks/DATA_BREACH.md` (definition, bundle, owner/legal/regulator path, clocks); tabletop it.
- Owner/effort/deps: owner · M · OD-14.
- Status: open.

### Finding ID: IR-P2-002 - Reboot/boot-order incidents recur; 09-27/28 fixes await a real re-exercise

- Severity: P2 · Confidence: Medium-High · Area: IR (recurrence/durability)
- Evidence: `decision_log.md:79` (09-22 cloudflared stale paths), `:108` (09-24 veth-span-b 712-restart Suricata loop invisible for hours), `:136` (09-28 Wazuh proxy sockets failed again; VM 106 no auto-start), `:137` (host swap + oom_score_adj + hookscript, manually validated only); `:126` (3 OOM kills 09-27); live guest swap 4.8/8 GiB; no VM start since the hookscript install.
- What is happening: three reboots/six days found three latent faults; OOM/power mitigations are installed but the auto-start + hookscript path has not fired.
- Why it matters: the next power event re-tests them at the worst time.
- Impact: recurring degraded monitoring and OOM recurrence risk.
- Fix / validation: encode host-only controls; add ordered-dependency boot checks; exercise a controlled VM restart and capture the journal.
- Owner/effort/deps: falcon maintainer + owner · M · PVE window, clean-host rehearsal.
- Status: partially-fixed / unverified.

### Finding ID: IR-P2-003 - Incident-support artefacts contradict the live state

- Severity: P2 · Confidence: High · Area: IR (documentation)
- Evidence: `CLOSEOUT.md:16` (P7-G09 INSUFFICIENT_EVIDENCE) vs `:77` and `gate_ledger.csv:90` (PASS); `risk_register.md:9-10` (R-05 "no SPAN", R-06 "no VPN" — superseded by P9-G03/G04 PASS); `SENSOR_SILENCE.md:26-33` and `DISK_PRESSURE.md:181` stale; `PRODUCTION_VERDICT.md:40` "28 alert rules" vs 31 live; `OWNER_INPUTS_REQUIRED.md` OD-12/OD-18 REQUESTED vs P9-G01 PASS.
- What is happening: a responder reading these artefacts would believe there is no VPN/SPAN/offsite and that escalation inputs remain open.
- Why it matters: wrong mental model during an incident; self-consistency doctrine requires reconciliation.
- Impact: mis-scoped response and delayed escalation.
- Fix / validation: append-only reconciliations in each doc/register; refresh verdict via its template; grep-check stale phrases in CI.
- Owner/effort/deps: falcon maintainer · M · none.
- Status: open.

### Finding ID: IR-P2-004 - Edge incident readiness is partial and not joined to the lab

- Severity: P2 · Confidence: High · Area: IR (edge)
- Evidence: edge `docs/runbooks/INDEX.md` (sensor-silence/disk/memory/adapter/dkms/recovery-boot "device drill pending"); edge `docs/phase8/CLOSEOUT.md` (3 runbooks walked; outage/backlog device-gated; alert rules undeployed); falcon has no joint incident runbook (prior INTG §8).
- What is happening: rich sensor runbooks with limited executed drills, and the lab cannot alert on edge silence (13 RES-P1-003).
- Why it matters: the monitored edge path is a blind spot on both sides.
- Impact: sensor loss detected slowly or not at all.
- Fix / validation: schedule device-gated drills; write `docs/runbooks/EDGE_INCIDENT.md`; deploy scoped edge rules.
- Owner/effort/deps: edge maintainer + owner · M · device session, rule approval.
- Status: open.

### Finding ID: IR-P2-005 - Postmortem follow-through is incomplete (R-29) and escalation contacts are absent

- Severity: P2 · Confidence: Medium · Area: IR (process/comms)
- Evidence: `INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` "Verification (to be completed after the repair)" checkboxes unticked; `risk_register.md:38` R-29 OPEN; `INCIDENT_RESPONSE.md:6-7` ("On-call, escalation contacts, and notification targets are owner-gated (OD-18, OD-12 pending)"); no comms templates.
- What is happening: an incident record stays open long after the fix; nobody has a verified contact tree.
- Why it matters: notification/escalation is half of incident response; unclosed postmortems hide recurrence risk.
- Impact: delayed human response; process drift.
- Fix / validation: close R-29 with a captured verification; complete the escalation matrix with an out-of-band channel; add a close-out checklist to §9.
- Owner/effort/deps: owner+falcon maintainer · S · OD-12/OD-18.
- Status: open.

### Finding ID: IR-P3-001 - No CI/CD incident playbook; bake approval gap remains open

- Severity: P3 · Confidence: High · Area: IR (CI/CD)
- Evidence: falcon `.github/workflows/validate.yml` (new); edge `docs/GITHUB_CI.md`; edge `risk_register.md` R-012 (bake workflow holds owner credentials; environment required-reviewers unavailable on the current plan; owner decision open).
- What is happening: pipelines are validated and pinned, but failure handling (failed bake, leaked secret, stuck release) is undocumented.
- Why it matters: CI is now part of the supply path for credential-bearing images.
- Impact: release delays; untested credential-exposure response.
- Fix / validation: add a CI incident section (rotate secrets, revoke assets, re-bake) and tabletop "bake leaked a credential"; record the approval-gate decision.
- Owner/effort/deps: owner+edge maintainer · S · plan decision.
- Status: open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Total-loss blind window (no real-time death notice) | High | Medium | High | IR-P1-001, 13 RES-P1-001 | Scenario 5; tighter watcher |
| Responder misled by stale docs | High | Medium | Medium | IR-P2-003 | reconcile artefacts |
| Recurring boot-order faults | Medium | Medium | High | IR-P2-002 | encode + boot regression |
| No escalation/comms templates | Medium | Medium | Medium | IR-P1-002/IR-P2-005 | fill matrix; adopt templates |
| Unclosed postmortem (R-29) | Low | Medium | Low | IR-P2-005 | close with evidence |

## Recommendations

### Immediate / Release Blocking
- Run Scenario 5 (total loss of monitoring/alerting) and record it; complete the escalation matrix.

### This Week
- Adopt the companion catalogue/templates; reconcile P7-G09/CLOSEOUT and R-05/R-06; close R-29.

### This Month
- Data-breach annex + scenario; edge outage/backlog drills; CI incident section; refresh stale runbooks; exercise VM auto-start + hookscript (owner window).

### Later / Platform Evolution
- Quarterly exercise cadence (disk, tunnel, total loss, breach); full-length sessions; edge↔lab joint exercises.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Add SEV + comms templates | ready words | `INCIDENT_RESPONSE.md`, companion | inject passes |
| Fill escalation matrix | reachable humans | `TABLETOP_SCENARIO.md` | contacts verified |
| Reconcile R-05/R-06 + CLOSEOUT | remove contradictions | `risk_register.md`, `CLOSEOUT.md` | grep clean |
| Close R-29 | postmortem hygiene | `risk_register.md`, incident doc | evidence ID |
| Blind-ops checklist | first 15 min without dashboards | `OPERATOR_START_HERE.md` | read-through |

## Hardening Backlog

| Item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Total-loss scenario + blind-ops runbook | P1 | owner+falcon | M | owner time |
| Edge alert deployment + `EDGE_INCIDENT.md` | P1 | owner | M | rule approval |
| Data-breach annex | P2 | owner | M | OD-14 |
| Boot-order regression + host-only encoding | P2 | falcon maintainer | M | clean-host |
| CI incident playbook + bake approval | P3 | owner+edge | S | plan decision |

## Suggested Tests

- Unit/E2E: companion scenario injects as checks (catalogue ids, runbook links resolve).
- Integration: relay-stopped canary; watcher latency measurement; edge-silence drill once rules deploy.
- Security: breach tabletop with mock credential exposure + evidence bundle; verify redaction.
- Regression: CI lints for stale phrases ("no VPN", "no offsite", "28 alert rules"); ledger-vs-closeout status check.
- Manual: full 60–90 min tabletop; blind-operations walkthrough with dashboards blocked.

## Suggested Documentation Updates

- New: `docs/runbooks/{DATA_BREACH,BLIND_OPERATIONS,EDGE_INCIDENT,ALERT_PATH_RECOVERY}.md`.
- Update: `INCIDENT_RESPONSE.md` (templates/close-out; correct P9-G07 wording), `TABLETOP_SCENARIO.md` (catalogue + contacts), `CLOSEOUT.md`/`risk_register.md` (reconciliations), verdict rule count via template.
- Ledgers: close R-29; record the next tabletop and actions in `decision_log.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Real DO watcher cadence/threshold (26 h vs 30-min unreachable)? | Blind-window sizing | watcher config on DO |
| Which channels survive a home power/internet loss? | Escalation reality | owner confirmation |
| Production privacy authority (OD-14)? | Breach procedure | owner decision |
| Who owns the exercise cadence? | Programme durability | owner commitment |

## Appendix A — Recurring incidents and prior-fix durability (requested)

| Incident | Date | Fix applied | Durability at 2026-09-30 | Evidence |
|---|---|---|---|---|
| Relay deployment overwrote `python3.12` (R-29) | 09-23 | reinstall + deploy guard | fix in place; record OPEN, checklist incomplete | incident doc; `risk_register.md:38` |
| Host OOM killed VM 3× | 09-27 | balloon 12 000, guest swap 8 GiB; later host swap + oom_score_adj + hookscript | no recurrence; hookscript not yet exercised; guest swap 4.8/8 GiB | `decision_log.md:126,137`; live `free` |
| Power outage, VM no auto-start | 09-28 | onboot=1 + manual start; 50/50 post-reboot; proxy sockets patched; installer fixed | verification captured; auto-start not yet re-exercised | `decision_log.md:136`; T-P9-G02-353 |
| VPN down 19 h (R-30) | 09-24 | persisted key/port; syncconf; rotation test fixed | held through later reboots; peer preservation added 09-30 | `risk_register.md:39`; wg capture |
| Disk burn/EVE leak | 09-21→30 | EVE/stats rotation, guard, 10 GiB threshold | data 62% stable; guard never reclaimed; root 83% | live `df`; `reclaims_total 0` |
| Tabletop P7-G09 | 09-23 | 3 scenarios scored; runbook refinements | not repeated; coverage findings IR-P1-001/002 | `CLOSEOUT.md`; gate ledger |

## Appendix B — Companion artefact

`incident_tabletop_scenarios.md`: roles + severity definitions; 10 scenarios (1 sensor silence, 2 credential exposure, 3 disk pressure, 4 VPN/tunnel loss, **5 total loss of monitoring/alerting**, 6 relay/delivery loss, 7 backup/offsite failure, 8 edge sensor loss/re-image, 9 data breach, 10 CI credential exposure) with injects, actions, success criteria and detection gaps; communication templates; postmortem template; cadence and scoring.

**Overall incident-readiness score: 3/5** — real doctrine and exercise evidence exist, but the flagship monitoring-loss scenario is missing, artefacts are stale, and total-loss detection is slow.
