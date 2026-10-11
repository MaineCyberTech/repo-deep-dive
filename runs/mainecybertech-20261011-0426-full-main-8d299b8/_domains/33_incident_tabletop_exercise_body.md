# Incident Tabletop Exercise

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: MaineCyberTech portal monorepo (`/tmp/opencode/mct-audit-target`, read-only)
- Branch: `main`
- Commit SHA: `8d299b8d` (`8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`, 2026-10-11)
- Generated at: 2026-10-11 (run clock)
- Auditor: repo-deep-dive subagent (prompt 33, area IR)
- Output path: `docs/audits/{name}/{run}/33_incident_tabletop_exercise.md` (this run stores outputs under the run folder)
- Companion artifact: the committed catalog at `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/incident_tabletop_scenarios.md` is stale; a refreshed 12-scenario catalog is included in this body and should be promoted to `docs/INCIDENT_TABLETOP_SCENARIOS.md`
- Scope limitations:
  - Audit-only. No live system, droplet, GitHub environment, Sentry org, ntfy topic, or Supabase project was contacted; GitHub Actions run history and secret values are not repo-visible.
  - `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` being unset is taken from this run's operator context; it is **not** repo-verifiable and is marked as such.
  - This is a documented-procedure exercise; no tabletop was actually facilitated.

## Scope

Reviewed at `8d299b8d`:

- Incident docs: `docs/INCIDENT_RESPONSE.md`, `docs/PLATFORM_FAILURE_RUNBOOKS.md`, the stale companion `incident_tabletop_scenarios.md`, `docs/runbooks/security-incident-response.md` (tenant product runbook — distinguished).
- Monitoring/alerting: `infra/digitalocean/prometheus.rules.yml`, `prometheus.rules.test.yml`, `prometheus.yml`, `alertmanager.tmpl.yml`, `docker-compose.yml`, `apps/api/src/lib/metrics.ts`, `apps/worker/src/metrics.ts`, `apps/api/src/routes/health.ts`, `docs/MONITORING_AND_ALERTING.md`.
- Rollback: `docs/ROLLBACK_PROCEDURES.md`, `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` §Rollback, `deploy-do.yml` rollback input, `docs/RTO_RPO.md`.
- Security docs: `SECURITY.md`, `docs/SECRETS_ROTATION.md`, `docs/JWT_ROTATION.md`, `docs/DATA_BREACH_RESPONSE.md`.
- Deployment docs: handbook, `docs/RELEASING.md`, `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `docs/ENVIRONMENT_VARIABLES.md`, `.github/workflows/deploy-do.yml`.
- Operator docs: `docs/TROUBLESHOOTING.md`, `docs/FINAL_OPERATOR_MAP.md`, 61 module runbooks under `docs/runbooks/`, `docs/SLO.md`.
- Data breach process: `docs/DATA_BREACH_RESPONSE.md` (459 lines).
- Backups: `db-backup.yml`, `db-restore-test.yml`, `storage-backup.yml`, `scripts/backup-database.sh`, `.github/restore-test-baseline.env`.
- Audit logs / admin abuse: `apps/api/src/services/audit.ts`, `apps/api/src/services/impersonation.ts`, `apps/api/src/routes/audit.ts`, rules in `prometheus.rules.yml` (`MCTImpersonationBurst`).
- Observability: metrics wiring, Sentry, pino logging, `docs/SLO.md`, dashboards-as-code.
- CI/CD failures: `deploy-do.yml` (health gate, auto-revert, watchdog guard), `supabase-migrations.yml`.
- Tenant isolation: RLS metrics/rules/tests (`rls-boundary-metrics.test.ts`, `get-scoped-client.test.ts`, `store-tenant-isolation.test.ts`).
- Webhook/payment/notification failures: `webhook-dispatcher.ts` (api/worker), `webhook-retry.ts`, `stripe-reconcile.ts`, dead-letter counters.

Not reviewed: live incident history, customer contracts, the 61 product-module runbooks except where they define platform recovery.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/INCIDENT_RESPONSE.md` | Doc | Platform IR plan (roles/severity/containment/comms/postmortem) | Accurate except §8 stale alerting text (:124-128) |
| `docs/DATA_BREACH_RESPONSE.md` | Doc | Breach detection → notification → register | 459 lines; stale alerting paragraph (:143-146) |
| `docs/PLATFORM_FAILURE_RUNBOOKS.md` | Doc | Operator runbooks + drill table | Drill table all `_pending_` (:112-118) |
| `infra/digitalocean/alertmanager.tmpl.yml` | Config | Routing incl. Watchdog receiver | Watchdog route :86-100; receiver :144-152 |
| `infra/digitalocean/prometheus.rules.yml` | Config | 7 alert rules | Availability, impersonation, RLS ×2, Watchdog |
| `infra/digitalocean/prometheus.rules.test.yml` | Test | promtool unit tests (fire/no-fire) | Not run in CI |
| `infra/digitalocean/prometheus.yml` | Config | Scrapes api (METRICS_TOKEN) + worker; forwards to Alertmanager | :11-17, :20-39 |
| `infra/digitalocean/docker-compose.yml` | Config | alertmanager service + noop defaults | :239-307 |
| `.github/workflows/deploy-do.yml` | CI | Watchdog fail-closed guard; worker health fatal | :739-747, :905-922 |
| `.github/workflows/supabase-migrations.yml` | CI | Dry-run artifact + post-push drift check | :67-83, :90-125 |
| `.github/workflows/db-restore-test.yml` | CI | Deep restore assertions | :135-224 |
| `.github/workflows/secret-rotation-reminder.yml` | CI | Quarterly rotation reminder | Committed (7dfb8650) |
| `apps/api/src/lib/metrics.ts` | Code | Metric definitions + record helpers | All previously unwired metrics now recorded |
| `apps/api/src/services/audit.ts` | Code | Audit write with retry | Final failure only logs (:61-63) |
| `apps/worker/src/tasks/stripe-reconcile.ts` | Code | Reconciliation task | Returns counts; no metric |
| `docs/RELEASE_GATE.md` | Doc | Pre-go-live blockers | 'No production environment yet' (:8); alert delivery exit criterion (:34) |

## Verification Performed

Commands run (read-only, all from `/tmp/opencode/mct-audit-target`):

```text
git log -1 --format='%H %ci %s'                          # 8d299b8dc271... "Merge PR #168 ..."
git rev-list --count 9c0b88c..8d299b8d                    # 113 commits since previous run
git merge-base --is-ancestor 6de167d3 9c0b88c             # RLS observability predates the previous run
grep -n "WATCHDOG\|watchdog" .github/workflows/deploy-do.yml
grep -rn "watchdog" infra/ docs/ --include=*.md --include=*.yml
grep -n "MCTTenantScopeRegression\|MCTImpersonationBurst\|MCTRlsEnforcedShareCollapsed" infra/digitalocean/prometheus.rules.yml
git show 9c0b88c:infra/digitalocean/prometheus.rules.yml | grep -n "MCTTenantScopeRegression"   # already present at 9c0b88c
grep -rn "recordRlsBypass\|recordImpersonationEvent\|recordWebhookDeadLetter\|recordSearchQuery..." apps --include=*.ts
grep -rn "promtool\|prometheus.rules.test" .github/workflows/*.yml    # no hits
grep -rn "ALERTMANAGER\|NTFY" docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md docs/ENVIRONMENT_VARIABLES.md  # no hits
grep -rn "secret_rotation_runbook\|backup_restore_drill_plan\|incident_tabletop_scenarios" docs/INCIDENT_RESPONSE.md docs/DATA_BREACH_RESPONSE.md
find . -name "POSTMORTEM.md" -o -name "INCIDENT_COMMS.md"    # none; docs/templates/ does not exist
```

Outcome summary: the incident plan and breach plan are committed and substantive; the alerting path is fully wired from rules → Alertmanager → ntfy for critical/default; the dead-man's switch receiver is still not provisioned and has never been exercised; every previous IR row was re-verified individually (below); no tabletop or drill artifact exists.

## Executive Summary

MCT's incident readiness is materially better than at the 20261004 run. The platform now has a real IR plan with roles, a three-level severity model, containment phases, a communication table and a postmortem requirement (`docs/INCIDENT_RESPONSE.md`), plus a 459-line breach plan with detection sources, containment playbooks, an assessment map, a notification decision record and a breach register schema (`docs/DATA_BREACH_RESPONSE.md`). Operator runbooks cover the top failure modes (`docs/PLATFORM_FAILURE_RUNBOOKS.md`), rollback docs now agree with the workflow, the worker health check is fatal, the restore drill asserts structure, freshness and RLS, and the previously unwired metrics plus the RLS/impersonation alerts are live with promtool unit tests.

The remaining risk is concentrated in **operationalization**, not documentation:

1. **The dead-man's switch is not provisioned.** Routing and the fail-closed prod guard exist, but with `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` unset the Watchdog pings a loopback no-op — a total loss of the droplet is still silent, and prod deploys are blocked by the same guard until it is set. Nothing about the path has been exercised.
2. **Nobody is on the rota.** The plan says it is not operational until names and escalation contacts are recorded; they are not.
3. **No exercise has been run and the only scenario catalog is stale.** The committed catalog (20261002) still says the IR plan is absent and Alertmanager is not deployed; its monitoring-loss scenario no longer matches the system.
4. **The plans were not refreshed after the alerting fix.** Both the IR plan and the breach plan still tell operators "Alertmanager is not deployed" and point at template files that only exist inside an old audit run folder.
5. **Two detection gaps remain:** audit-trail gaps are still log-only, and webhook dead-letters / reconciliation drift have counters but no alert rules. Alert-rule unit tests are not run in CI.

Recommended next actions: provision the watchdog heartbeat and record the documented stop-Alertmanager exercise; fill the rota; promote a refreshed scenario catalog into `docs/` and run Scenario 11 (monitoring-path loss) as the first recorded tabletop; refresh the two plans' alerting sections and template links; add the audit-gap and dead-letter rules.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Platform IR plan | `docs/INCIDENT_RESPONSE.md` | Roles/severity/containment/comms/postmortem | Present, substantive | Medium | Stale §8 alerting text; rota unfilled |
| Breach plan | `docs/DATA_BREACH_RESPONSE.md` | Detection→notification→register | Present, substantive | Medium | Stale alerting paragraph |
| Operator runbooks | `docs/PLATFORM_FAILURE_RUNBOOKS.md` | Top failure-mode recovery | Present | Medium | All drills `_pending_` |
| Scenario catalog | `docs/audits/.../20261002-0344.../incident_tabletop_scenarios.md` | 12 scenarios + templates | Stale (bound to 62861370) | High | Not under `docs/`; referenced by bare name |
| Alertmanager | `infra/digitalocean/alertmanager.tmpl.yml` + compose | Delivery + watchdog | Deployed path; watchdog receiver unset | High | Fail-closed prod guard |
| Alert rules | `infra/digitalocean/prometheus.rules.yml` | 7 rules | Present | Medium | No audit-gap / dead-letter rules |
| Rule unit tests | `infra/digitalocean/prometheus.rules.test.yml` | promtool fire/no-fire | Present, manual only | Medium | Not in CI |
| Metrics | `apps/api/src/lib/metrics.ts`, worker | Diagnosis + alert inputs | Wired | Low | Doc table stale |
| Health endpoint | `apps/api/src/routes/health.ts` | Liveness/readiness | Public minimal; `/health/detail` gated | Low | Doc §2 stale |
| Docker rollback | `deploy-do.yml` + `ROLLBACK_PROCEDURES.md` | SHA rollback | Consistent | Low | Precondition: images exist |
| Migration recovery | `ROLLBACK_PROCEDURES.md` §3; `supabase-migrations.yml` | Reverse/PITR/drift | Drift fail-closed; reverse manual | High | No PITR drill |
| Restore drill | `db-restore-test.yml` | Backup verification | Deep assertions | Low | PITR RPO unproven |
| Secret rotation | `SECRETS_ROTATION.md` + reminder workflow | Rotation policy | Reminder committed; log unexercised | Medium | Single log row |
| Status surface | (none for MCT) | External comms | Absent | Medium | Runbook points at product feature |
| Audit-gap alert | `apps/api/src/services/audit.ts` | Gap detection | Log-only | Medium | No metric/rule |
| Dead-letter/reconcile alerts | counters + `stripe-reconcile.ts` | Webhook/billing failure | Counters emitted; no rules | Medium | Reconcile has no metric |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Incident docs | 4 | `INCIDENT_RESPONSE.md` roles/severity/phases/comms/postmortem | Rota unfilled; stale alerting text; broken template links | Fill rota; refresh §8; move templates to `docs/templates/` |
| Monitoring/alerting | 3 | Alertmanager + ntfy wired; 7 rules; promtool tests | Watchdog receiver unset; rule tests not in CI; no audit-gap/dead-letter rules | Provision + exercise watchdog; wire promtool CI; add rules |
| Rollback | 4 | Auto-revert; SHA rollback docs consistent; drift check | DB reverse/PITR manual and undrilled | Record one PITR/reverse drill |
| Security docs | 4 | `SECURITY.md`, rotation, JWT, RLS, breach plan | Rotation unexercised; alerting secrets undocumented | Rotation drill; secrets matrix update |
| Deployment docs | 4 | Handbook, `RELEASING.md`, `CI.md`, secrets matrix | Matrix missing alerting secrets | Add `ALERTMANAGER_*`/`NTFY_ALERTS_*` rows |
| Operator docs | 4 | `PLATFORM_FAILURE_RUNBOOKS.md`, `TROUBLESHOOTING.md`, 61 runbooks | Drills pending; status-page pointer wrong | Exercise runbooks; fix status reference |
| Data breach process | 4 | 459-line plan + register + templates | Never exercised; stale detection gap text | Run breach tabletop; refresh §3 |
| Backups | 4 | Deep restore assertions; shared bucket contract | PITR RPO unproven | Record dated PITR exercise |
| Audit logs | 3 | Retry + PII redaction; impersonation alert | Gap remains silent; no tamper-evidence check | Emit audit-gap metric + rule |
| Observability | 4 | Metrics wired; SLO doc; dashboards-as-code | Doc table stale; dead-letter/reconcile unalerted | Doc refresh; add rules |
| CI/CD failures | 4 | Health gates, auto-revert, migration gates | Alert-rule tests not in CI | Add promtool CI job |
| Admin abuse | 4 | Impersonation metric + burst alert + tests | Audit-gap half silent | Audit-gap alert |

## Detailed Review

### Item: Platform IR plan and postmortem process

- Evidence: `docs/INCIDENT_RESPONSE.md:14-38` (severity + roles), `:40-87` (declare/contain/eradicate/postmortem), `:89-99` (comms), `:101-107` (evidence handling), `:120-128` (rota + known gaps).
- What it does: gives a single platform plan with named roles, a 3-level severity model, containment rules ("revoke first"), a 5-business-day postmortem requirement and a "no doc/config change = not closed" rule.
- Missing controls: no names in the rota; §8 alerting text contradicts the deployed stack; template references unresolved.
- Risks: during a real incident the IC role is unassigned and the plan's alerting assumptions are wrong.

### Item: Breach response

- Evidence: `docs/DATA_BREACH_RESPONSE.md:61-153` (definitions + breach types incl. RLS regression, service-role key, phishing_targets), `:127-153` (detection sources), `:169-234` (containment playbooks), `:275-346` (notification decision + template), `:369-403` (register).
- What it does: decision-oriented breach process with explicit counsel gates and a processor/controller framing.
- Missing controls: never exercised; §3/§11 repeat the stale Alertmanager claim; register lives outside the repo (by design).
- Risks: delayed breach detection (RLS/audit signals partly unalerted); stale detection guidance.

### Item: Monitoring, alerting and the dead-man's switch

- Evidence: `alertmanager.tmpl.yml:63-100` (routes), `:144-152` (watchdog receiver), `docker-compose.yml:239-307`, `prometheus.yml:11-17`, `deploy-do.yml:739-747` (fail-closed), `MONITORING_AND_ALERTING.md:271-352` (§9 model + test), `RELEASE_GATE.md:34`.
- What it does: Prometheus → Alertmanager → ntfy (critical/default) with a separate always-firing Watchdog heartbeat to an external receiver.
- Missing controls: receiver URL unset (per run context); no exercise artifact; `MCTServiceDown`/warning delivery assurance is tracked in the NOTIF domain; rule unit tests not in CI.
- Risks: total monitoring loss remains undetected until the URL is provisioned and tested; prod deploy is blocked by the guard meanwhile.

### Item: Rollback and migration recovery

- Evidence: `ROLLBACK_PROCEDURES.md:1-27` (§1 automated), `:75-115` (§3 manual options), `FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:157-176`; `supabase-migrations.yml:67-125`.
- What it does: consistent SHA rollback docs; fail-closed drift check; dry-run artifact.
- Missing controls: no automated reverse migration; no PITR drill; `ROLLBACK_PROCEDURES.md:214-226` state-restore still a comment block.
- Risks: bad migration recovery time unproven; Terraform state corruption untested.

### Item: Backups

- Evidence: `db-restore-test.yml:135-224`, `.github/restore-test-baseline.env`, `db-backup.yml:30-35`, `scripts/backup-database.sh:8-24`, `RTO_RPO.md:41-45`.
- What it does: daily encrypted dump; weekly restore with structural/freshness/RLS floors.
- Missing controls: PITR 5-minute RPO unproven; encryption/offsite activation is an operator action (`RTO_RPO.md:37-40`).
- Risks: a real incident may discover the 5-minute RPO claim is aspirational.

### Item: Audit logs and admin abuse

- Evidence: `audit.ts:47-66`, `impersonation.ts:46`, `metrics.ts:125-130`, `prometheus.rules.yml:48-56`.
- What it does: retried audit writes with PII redaction; impersonation events metered and alerted on bursts.
- Missing controls: audit-gap has no metric/rule; no tamper-evidence assertion.
- Risks: an evidence trail for a breach can silently have holes.

### Item: Webhook / payment / notification failures

- Evidence: `metrics.ts:136-145`, `worker/src/metrics.ts:66-76`, `webhook-dispatcher.ts:124` (api) and `:128` (worker), `stripe-reconcile.ts:96-150`, `SLO.md:15`.
- What it does: retries with backoff; dead-letter counters; reconciliation task returns counts.
- Missing controls: no alert rule on dead-letter growth; no reconciliation metric.
- Risks: silent customer-facing delivery and billing drift.

## Scenario / Control Matrix

Refreshed catalog for `8d299b8d` (12 scenarios; the stale committed catalog lives at `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/incident_tabletop_scenarios.md`). Each scenario is rated on whether the repo would enable detection → triage → recovery within `docs/RTO_RPO.md` targets.

| ID | Scenario | Detection (0-5) | Triage | Recovery | Overall | Weakest link / change since 20261002 |
|---|---|---:|---:|---:|---:|---|
| IR-001 | Total database loss / restore | 4 | 3 | 3 | 3.3 | Deep restore assertions added; PITR still undrilled |
| IR-002 | Secret/key compromise | 2 | 3 | 3 | 2.7 | No compromise-detection alert; rotation undrilled |
| IR-003 | Bad migration | 3 | 3 | 2 | 2.7 | Drift check now fail-closed; reverse still manual |
| IR-004 | Failed deploy / rollback | 4 | 4 | 4 | 4.0 | Worker health now fatal |
| IR-005 | Supabase outage | 3 | 3 | 3 | 3.0 | ntfy delivery wired; status surface still absent |
| IR-006 | Dependency / supply-chain compromise | 4 | 3 | 3 | 3.3 | Unchanged |
| IR-007 | CI/CD compromise | 2 | 3 | 3 | 2.7 | Unchanged; no out-of-band CI alert |
| IR-008 | RLS regression / tenant exposure | 4 | 3 | 3 | 3.3 | RLS metrics + alert rules + tests now present |
| IR-009 | Webhook / payment / notification failure | 3 | 3 | 4 | 3.3 | Counters emitted; still unalerted |
| IR-010 | Admin abuse / insider action | 3 | 3 | 3 | 3.0 | Impersonation burst alert added; audit gap silent |
| IR-011 | **Total loss of the monitoring/alerting path** | 2 | 2 | 3 | 2.3 | Routing + fail-closed guard exist; watchdog receiver unset and unexercised → still undetected |
| IR-012 | Recurring incident / fix durability | 3 | 3 | 2 | 2.7 | No postmortem registry; fixes not always re-bound to docs (this run found stale plans) |

Communication templates: the stale catalog's §5 (declaration, status-update, resolution, postmortem) is still usable but must be moved under `docs/` and re-dated; the breach plan already carries a notification-content template (`DATA_BREACH_RESPONSE.md:316-346`). No `docs/templates/POSTMORTEM.md` or `INCIDENT_COMMS.md` exists.

## Findings

Finding IDs are assigned by the aggregator; this run's JSON carries the same titles. Summary:

| Severity | Title | Status |
|---|---|---|
| P0 | No platform-level incident response plan, roles, or postmortem process | verified-fixed |
| P0 | No data breach response / notification process | verified-fixed |
| P0 | Total loss of the monitoring/alerting path has no independent dead-man's-switch receiver | partially-fixed |
| P1 | Rollback documentation contradicts itself on SHA-targeted rollback | verified-fixed |
| P1 | Bad-migration recovery is manual-only with no automated reverse or staging proof | partially-fixed |
| P1 | Worker health failure during deploy is non-fatal | verified-fixed |
| P1 | Backups are not verified deeply enough to prove the documented RPO/RTO | verified-fixed |
| P1 | Backup bucket configuration is inconsistent between the script, the backup workflow, and the restore test | verified-fixed |
| P1 | No runtime detection or alerting for tenant-isolation (RLS) regressions | verified-fixed |
| P2 | Several Prometheus metrics are declared but not wired, limiting incident diagnosis | verified-fixed |
| P2 | No alerting on audit-trail gaps or privileged (impersonation/admin) abuse | partially-fixed |
| P2 | No alerting when webhook dead-letters accumulate or payment reconciliation drifts | still-open |
| P2 | Secrets rotation is documented but has no exercised evidence | partially-fixed |
| P2 | No platform status/communication surface for MCT's own outages | still-open |
| P2 | Migration dry-run result is discarded in CI | verified-fixed |
| P3 | Terraform state restore guidance lacks a tested procedure | still-open |
| P3 | Monitoring doc and health endpoint disagree on check semantics; Redis severity undocumented in alerts | still-open |
| P2 | Platform IR and breach plans are stale on the deployed alerting path and reference template files that do not exist in docs/ | open (new) |
| P2 | On-call rota and escalation contacts are unassigned, so the incident plan is not operational | open (new) |
| P2 | No tabletop exercise has been run and the scenario catalog is stale | open (new) |
| P2 | Prometheus alert-rule unit tests are not wired into CI | open (new) |
| P3 | Monitoring doc still reports wired metrics as 'defined, not wired' and omits the alert rules added for impersonation and RLS | open (new) |
| P3 | Alerting secrets are not documented in the secrets matrix or environment-variable reference | open (new) |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Total monitoring loss stays silent (watchdog receiver unset) | P0 | Medium | High | `docker-compose.yml:256-258`; run context | IR-P0-003: provision + exercise |
| Prod deploy blocked by the fail-closed watchdog guard | P1 | High (while unset) | Medium | `deploy-do.yml:739-747` | Set the secret before the next prod deploy |
| Incident response stalls because nobody is on the rota | P1 | High | Medium-High | `INCIDENT_RESPONSE.md:120-123` | Fill rota/escalation |
| Operators act on stale alerting assumptions in the plans | P2 | Medium | Medium | `INCIDENT_RESPONSE.md:124-128`; `DATA_BREACH_RESPONSE.md:143-146` | Refresh plans |
| Tabletop never run → scenario catalog rots | P2 | High | Medium | Drill table `_pending_`; stale catalog | Run + record Scenario 11 |
| Dead-rule regression returns (tests not in CI) | P2 | Medium | Medium | `prometheus.rules.test.yml` unreferenced | Add promtool CI job |
| Silent audit-trail gaps during a breach | P2 | Low-Med | Medium-High | `audit.ts:61-63` | Add metric + rule |
| Silent webhook/billing failure | P2 | Medium | Medium | counters without rules | Add dead-letter/reconcile rules |

## Recommendations

### Immediate / Release Blocking

1. **IR-P0-003** — Provision the external watchdog heartbeat secret for prod and record the documented exercise (stop `alertmanager`, confirm the external service pages within its grace period). Until then no prod deploy completes and total monitoring loss is undetectable.
2. Fill the rota/escalation block in `docs/INCIDENT_RESPONSE.md` §8 and the breach-plan contacts; the plans declare themselves non-operational without it.

### This Week

3. Refresh the alerting sections and template links in `docs/INCIDENT_RESPONSE.md` and `docs/DATA_BREACH_RESPONSE.md`; move the postmortem/comms/rotation/drill templates into `docs/templates/` and index both plans in `docs/INDEX.md`.
4. Promote the refreshed 12-scenario catalog into `docs/INCIDENT_TABLETOP_SCENARIOS.md` and run Scenario IR-011 (monitoring-path loss) as the first recorded exercise.

### This Month

5. Add the audit-gap metric + rule and the dead-letter/reconciliation rules (IR-P2-002/IR-P2-003 residuals).
6. Add a CI job running `promtool check rules` + `test rules` on `infra/digitalocean/prometheus.rules*.yml`.
7. Add the alerting/notification secrets to the secrets matrix and env reference.
8. Perform one rotation drill and one PITR/reverse-migration drill; record both with artifacts.

### Later / Platform Evolution

9. Stand up an MCT-owned status surface (or an internal instance of the product) and wire the runbook to it (IR-P2-005).
10. Operationalize Terraform state restore with exact commands and a scratch-backend drill (IR-P3-001).
11. Institutionalize quarterly tabletops with after-action reports stored in-repo.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Set `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` + run the stop-alertmanager test | Makes the only off-box detector real | GitHub prod env secret; `MONITORING_AND_ALERTING.md` §9 | External service reports missed heartbeat; artifact recorded |
| Fill the rota table | Makes the plan operational | `docs/INCIDENT_RESPONSE.md` §8 | Names present; escalation test |
| Fix template references | Operators can open the referenced templates | `docs/INCIDENT_RESPONSE.md`, `docs/DATA_BREACH_RESPONSE.md` | All referenced paths resolve |
| Wire promtool tests into CI | Prevents dead-rule regressions | `.github/workflows/*`, `prometheus.rules.test.yml` | CI fails on a mutated rule |
| Update the §4 metric table | Doc matches emitted metrics | `docs/MONITORING_AND_ALERTING.md` | Table matches `metrics.ts` |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Watchdog receiver provisioning + exercise (IR-P0-003) | P0 | Platform | S | External heartbeat account |
| Rota/escalation assignment | P1 | Platform lead | S | — |
| Refresh IR + breach plans; template move | P2 | Security/platform | S-M | — |
| Refreshed tabletop catalog + first exercise | P2 | Platform lead | M | Rota |
| Audit-gap metric + rule (IR-P2-002 residual) | P2 | Security/platform | M | — |
| Dead-letter + reconcile rules (IR-P2-003) | P2 | Backend | S-M | — |
| promtool CI job | P2 | Platform/infra | S | — |
| Alerting secrets docs | P3 | Platform/infra | S | — |
| Monitoring doc refresh (metrics + rules header) | P3 | Docs maintainer | S | — |
| Status surface (IR-P2-005) | P2 | Platform lead | M | — |
| Terraform state restore drill (IR-P3-001) | P3 | Platform | S | DO Spaces scratch |

## Suggested Tests

- **CI**: promtool `check rules` + `test rules` on every change under `infra/digitalocean/prometheus*.yml`.
- **CI**: assert every secret name required by `deploy-do.yml` env forwarding appears in the secrets matrix (docs-consistency check).
- **Integration**: force an audit-insert failure and assert the new audit-gap metric increments and its rule fires.
- **Integration**: force repeated webhook failures; assert dead-letter counter increase triggers the new rule.
- **Manual (tabletop)**: run all 12 scenarios with only repo docs available; record detection time, time-to-triage and time-to-recovery vs `RTO_RPO.md`; start with IR-011.
- **Manual (watchdog)**: `docker compose stop alertmanager`; assert the external service pages within its grace period; store the artifact.
- **Manual (rotation)**: complete one dev rotation and update `SECRETS_ROTATION.md` Rotation Log.

## Suggested Documentation Updates

- `docs/INCIDENT_RESPONSE.md` — refresh §8 (Alertmanager deployed; watchdog pending), fix template links, fill rota.
- `docs/DATA_BREACH_RESPONSE.md` — refresh §3/§11 detection gap text; link templates.
- `docs/INCIDENT_TABLETOP_SCENARIOS.md` — new, refreshed from this body.
- `docs/templates/POSTMORTEM.md`, `docs/templates/INCIDENT_COMMS.md` — create from the catalog §5.
- `docs/MONITORING_AND_ALERTING.md` — §2/§3 health semantics, §4 metric statuses, §7 alert table, §9 watchdog exercise record.
- `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `docs/ENVIRONMENT_VARIABLES.md` — alerting/notification secrets.
- `docs/PLATFORM_FAILURE_RUNBOOKS.md` — replace the product status-page pointer with the real channel once it exists; record drills.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` set in any environment, and what service backs it? | Determines whether IR-P0-003 is real | GitHub environment secret inventory (names only) |
| Has any critical alert actually reached ntfy? | Delivery assurance (NOTIF-domain finding) | ntfy topic history / run artifact |
| Will the `prod` environment/rota ever be staffed for a small team? | Determines whether the plan is operational | Rota decision |
| Is the audit-log insert failure observable anywhere today? | Gap detection | Sentry/log alert or metric |
| Has a Supabase PITR restore ever been performed? | Proves the 5-minute RPO claim | Supabase dashboard history |
| Has any tabletop/drill been run outside the repo? | The domain's central question | After-action artifact |

## Appendix

### A. Previous-run IR rows re-verified at 8d299b8d

| Previous ID | Status now | Note |
|---|---|---|
| IR-P0-001 | verified-fixed | Plan committed; unchanged |
| IR-P0-002 | verified-fixed | Breach plan committed; unchanged |
| IR-P0-003 | partially-fixed | Mechanism + guard present; receiver unset and unexercised (corrects the 9c0b88c verified-fixed claim) |
| IR-P1-001 | verified-fixed | Handbook matches workflow/docs |
| IR-P1-002 | partially-fixed | Drift check fail-closed; reverse/PITR still manual |
| IR-P1-003 | verified-fixed | Worker health fatal |
| IR-P1-004 | verified-fixed | Deep restore assertions |
| IR-P1-005 | verified-fixed | Shared bucket contract |
| IR-P1-006 | verified-fixed | Rules existed at 9c0b88c too (previous note looked in the wrong file) |
| IR-P2-001 | verified-fixed | All metrics wired |
| IR-P2-002 | partially-fixed | Impersonation alerted; audit gap silent |
| IR-P2-003 | still-open | Counters emitted; no rules; no reconcile metric |
| IR-P2-004 | partially-fixed | Reminder workflow committed; log unexercised |
| IR-P2-005 | still-open | No platform status surface |
| IR-P2-006 | verified-fixed | Dry-run artifact + drift gate |
| IR-P3-001 | still-open | No executable state-restore procedure |
| IR-P3-002 | still-open | Doc/health divergence widened by the /health split |

Out-of-area rows touching this domain but owned elsewhere: `INFRA-P2-003` (alert rules delivery path) and `OBS-P2-001` (rules not routed) were reconciled as verified-fixed; re-verified here that routing exists (`prometheus.yml:11-17`, `alertmanager.tmpl.yml:63-100`). The critical-receiver delivery-assurance residual is tracked in the NOTIF domain.

### B. Scenario catalog provenance

The refreshed matrix above is grounded in this commit's code and docs. The stale catalog was bound to `develop@62861370`; its readiness inventory still lists the IR plan as Absent and Alertmanager as not deployed, and its Scenario 11 says the Watchdog has no receiver — all superseded. It remains the only source of the communication/postmortem templates, which is why finding "No tabletop exercise has been run and the scenario catalog is stale" recommends promoting a refreshed copy into `docs/`.

### C. Secrets handling

No secret values were read or printed. Only secret *names* and code paths are referenced. Redactions: `ALERTMANAGER_WEBHOOK_PASS`, `ALERTMANAGER_*_WEBHOOK_URL`, `NTFY_ALERTS_PASS` values are not shown.
