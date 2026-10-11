# 14_observability_monitoring_incident_readiness — Prompt 14 - Observability, Monitoring, and Incident Readiness Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `14_observability_monitoring_incident_readiness.md` (area OBS, prompt)

## Verification Performed

# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: `repo-deep-dive` (full hardening rerun)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (monorepo: api / worker / web, Supabase, single DigitalOcean droplet)
- Branch: `main` @ `8d299b8d` (merge of PR #168)
- Generated at: 2026-10-11
- Auditor: subagent, domain 14 (area code **OBS**)
- Scope limitations: repository-only review. No production/lab access, no secret values, no live Prometheus/Alertmanager/ntfy calls. "Delivered/configured" is distinguished from "exercised"; operator-side secret presence is marked unverifiable.

## Scope

Reviewed: structured logs, request-id correlation, error tracking (Sentry), metrics (API + worker), tracing, health/readiness, client/API/worker errors, job metrics, DB/queue/webhook/notification metrics, uptime checks, alert rules, Alertmanager routing + ntfy delivery, dashboards/SLOs, incident runbooks, audit/security-log signals, release markers, user-impact and data-quality signals.

Not reviewed: tenant-facing uptime-monitor product internals beyond confirming it is not platform self-monitoring; Sentry account configuration (alert rules are UI-side); DigitalOcean monitoring config (not in repo).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/lib/metrics.ts` (263 lines) | Source | API metric registry (30 named metrics) | prom-client, `portal_` prefix |
| `apps/worker/src/metrics.ts` (119 lines) | Source | Worker job/queue/webhook metrics | 9 named metrics |
| `apps/api/src/middleware/request-id.ts` | Source | Request IDs + HTTP metrics labels | `route: req.path` (cardinality) |
| `apps/api/src/routes/health.ts` | Source | Public `/health`, gated `/health/detail` | Fail-closed token gate |
| `apps/api/src/app.ts:145-171` | Source | Middleware order + `/metrics` gate | 404 without token |
| `apps/api/src/lib/logger.ts`, `apps/worker/src/logger.ts` | Source | pino JSON + redaction | Redacts PII/secret paths |
| `apps/api/src/lib/sentry.ts`, worker `main.ts`, web `sentry.*.config.ts` | Source | Error tracking init | Web DSN variable mismatch |
| `apps/worker/src/health-server.ts`, `task-registry.ts` | Source | Worker health + job metrics | Queue degraded ⇒ still 200 |
| `infra/digitalocean/prometheus.yml` | Config | Scrape configs + bearer scrape | `metrics-token` credentials file |
| `infra/digitalocean/prometheus.rules.yml` | Config | 6 alert rules | 4/30 metric names referenced |
| `infra/digitalocean/prometheus.rules.test.yml` | Test | promtool rule unit tests (manual) | Not run in CI |
| `infra/digitalocean/alertmanager.tmpl.yml` | Config | Routing to ntfy + watchdog | awk-rendered template |
| `infra/digitalocean/docker-compose.yml:206-344` | Config | Prometheus/Alertmanager/Caddy | No published monitoring ports |
| `infra/digitalocean/dashboards/mct-overview.json` | Artifact | Grafana dashboard (7 panels) | Not provisioned anywhere |
| `.github/workflows/deploy-do.yml` | CI/CD | Secret delivery, fail-closed guard, health gate | No monitoring-stack gate |
| `.github/workflows/db-backup.yml`, `db-restore-test.yml`, `storage-backup.yml` | CI/CD | Backup alerting | ntfy notifiers, `environment: dev` |
| `docs/MONITORING_AND_ALERTING.md`, `docs/SLO.md`, `docs/RELEASE_GATE.md`, `docs/INCIDENT_RESPONSE.md`, `docs/PLATFORM_FAILURE_RUNBOOKS.md`, `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` | Docs | Operator-facing claims | Several stale statements |
| Previous run register/risk register (`mainecybertech-20261004-full-main-9c0b88c`) | Register | Verification duty | OBS + IR rows re-checked |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline 9c0b88c..8d299b8d` | Command | Delta since previous audit | 4 observability commits: ntfy routing (#154), scrape auth (#155, #166, #167) |
| Metric-name vs rule comparison (python, regex over `metrics.ts` + `rules.yml`) | Command | "Which declared metrics lack alert rules" | 4 of 30 referenced; 26 have no rule |
| `git show 9c0b88c:infra/.../prometheus.rules.yml` | Command | Verify IR-P1-006 at prior commit | Rules already present — register note was wrong |
| `grep -rn "promtool\|amtool" .github/ scripts/` | Command | CI validation of alerting config | No matches — manual only |
| `grep -rn "NEXT_PUBLIC_SENTRY_DSN"` | Command | Web Sentry wiring | Read by web configs; never set by build/deploy |
| `grep -rn "NTFY" .github/workflows/*.yml` | Command | Backup alert delivery | 3 workflows post to ntfy with Slack fallback |
| `grep -rn "environment: dev" .github/workflows/db-*.yml` | Command | Deployed-branch restore verification | Backup/restore target dev only |
| `grep -rn "req.route\|normalizeRoute" apps/api/src` | Command | Metric label normalization | None — raw `req.path` used |
| `git merge-base --is-ancestor 6de167d3 9c0b88c` | Command | Correct IR-P1-006 status | Ancestor — rule existed at 9c0b88c |
| File reads of all evidence listed above | Read | Primary evidence | Line numbers cited in findings |

Not reproducible in this audit: Sentry project alert rules (UI-side), DigitalOcean monitoring (not in repo), live ntfy delivery, actual secret values.

## Executive Summary

The observability stack is materially better than the previous audit left it. Since `9c0b88c` the team added ntfy delivery with basic auth to Alertmanager (#154), authenticated the Prometheus→API scrape with a deploy-written `metrics-token` file (#155/#166/#167), and wired the remaining declared metrics (#147). The alert path is now: rules → Alertmanager → org ntfy topic, plus an off-box watchdog dead-man's switch with a production fail-closed deploy guard (IR-P0-003). The committed SLO doc and Grafana-importable dashboard exist, and the RLS/tenant-isolation telemetry is real, wired, and unit-tested (IR-P1-006 is actually fixed — the previous register wrongly recorded it open).

The main weaknesses are in breadth and proof rather than the core path: only 6 alert rules exist for 30 declared metrics, so latency, circuit-breaker state, auth-failure spikes, notification/webhook delivery failures, worker job failures and queue depth are measurable but unalerted. Web error tracking is silently disabled in production (`NEXT_PUBLIC_SENTRY_DSN` is never provided while the deploy passes `SENTRY_DSN`). HTTP metric labels use the raw request path, creating unbounded Prometheus series cardinality against a 256MB memory limit. Alerting configs are not validated in CI, and the deploy health gate ignores Prometheus/Alertmanager, so a broken rules file or an empty `METRICS_TOKEN` ships green. Finally, the alert path has never been exercised end-to-end (no synthetic alert/heartbeat evidence; the release gate still lists it as an exit condition), and the incident docs contradict the deployed topology while referencing two files that do not exist.

Priority actions: (1) exercise the alert path and record evidence; (2) add the missing golden-signal rules and wire `promtool` tests into CI; (3) fix the web Sentry DSN and the `route` label cardinality; (4) add a non-empty `METRICS_TOKEN` deploy guard and gate the deploy on monitoring health.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| API metrics | `apps/api/src/lib/metrics.ts` | 21 named metrics + defaults | Implemented, token-gated `/metrics` | Medium | 26/30 metrics unalerted |
| Worker metrics | `apps/worker/src/metrics.ts` | 9 job/queue/webhook metrics | Implemented | Medium | No alert rules |
| Request ID | `middleware/request-id.ts` | `X-Request-ID`, child logger | Implemented | Low | Not propagated to worker jobs |
| Logging | api/worker/web pino | Structured JSON + redaction | Implemented | Medium | No shipping; logs lost on deploy `down` |
| Error tracking | Sentry api/worker/web | Exception capture | API/worker wired; web disabled | High | `NEXT_PUBLIC_SENTRY_DSN` never set |
| Tracing | Sentry perf only | Distributed tracing | Absent | Low | No OTel, no cross-service trace |
| Health/readiness | `/health`, `/health/detail`, worker `/health` | Liveness/dependency probes | Implemented | Low | Queue degraded still 200; docs stale |
| Scrape auth | `prometheus.yml:19-32` + `metrics-token` | Bearer scrape | Implemented | Medium | No empty-token guard |
| Alert rules | `prometheus.rules.yml` | 6 rules | Implemented | High | Latency/job/queue/delivery rules missing |
| Alert routing | `alertmanager.tmpl.yml` | ntfy critical/default + watchdog | Implemented | Medium | Never exercised; awk renderer fragile |
| Dead-man's switch | watchdog receiver + deploy guard | Off-box liveness | Implemented | Low | Not exercised |
| Dashboards | `dashboards/mct-overview.json` | Grafana artifact | Committed, not provisioned | Medium | No Grafana service |
| SLOs | `docs/SLO.md` | 5 SLOs + error budget | Committed | Medium | 2 objectives have no alert rule |
| Runbooks | `PLATFORM_FAILURE_RUNBOOKS.md`, `INCIDENT_RESPONSE.md` | Incident response | Present | Medium | Drill table pending; broken refs |
| Audit/security signals | impersonation metric + rule | Privileged-access alerting | Partial | Medium | No audit-gap detection |
| Uptime checks | none in repo | External platform checks | Absent | High | Watchdog covers alert path only |
| Release markers | `SENTRY_RELEASE`/`GIT_SHA` | Deploy correlation | Web only | Low | API/worker unversioned |
| Data-quality signals | none | Data integrity monitoring | Absent | Low | No metrics/checks found |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Structured logs | 3 | pino JSON, redaction, 10m×3 rotation (`compose:19-23`) | No shipping; deploy `down` deletes previous logs; no Caddy access logs | Ship off-box or snapshot before deploy |
| Request IDs/correlation | 3 | `request-id.ts:16-18`; `X-Request-ID` response header | No propagation into task payloads/worker logs | Pass requestId into `enqueueTask` payloads |
| Error tracking | 2 | api/worker Sentry init; web configs read a never-set var | Web (client/server/edge) silent; release markers absent; Sentry alert rules unverified | Provide `NEXT_PUBLIC_SENTRY_DSN`; deliver release marker |
| Metrics | 3 | 30 metrics; token-gated; db/latency/job counters wired | Raw-path label cardinality; 26 metrics unalerted | Normalize route label; add rules |
| Tracing | 1 | Sentry `tracesSampleRate` only | No distributed tracing/context propagation | Optional: OTel later |
| Health/readiness | 3 | `/health` + gated `/detail`; worker `/health`; compose healthchecks | Queue degraded never fails health; docs mismatch; no web health route | Align docs; expose queue state to alerts |
| Client/API/worker errors | 2 | API error middleware + Sentry; worker task capture | Client errors uncaptured (web Sentry off); no RUM | Fix web DSN; add Web Vitals later |
| Job metrics | 3 | `worker_task_executions_total`, duration, queue depth | Zero alert rules; `queue="unavailable"` synthetic series | Add failure/queue alerts |
| DB/queue/webhook/notification metrics | 3 | db duration, dead letters, delivery counters (api+worker) | No rules; reconciliation has no metric | Add rules; export reconcile counts |
| Uptime checks | 1 | Watchdog (alert-path liveness) | No external HTTP check for public endpoints | Add external uptime probe + alert |
| Alerts | 3 | 6 rules; ntfy routing; watchdog; fail-closed prod guard | Not CI-validated; not exercised; golden signals missing | CI validation + synthetic delivery |
| Dashboards | 2 | Dashboard JSON + SLO.md | No Grafana; Prometheus UI internal-only; SLO panels partly unalerted | Provision Grafana or document tunnel |

## Detailed Review

### Item: Alert rules and routing (golden signals)
- Evidence: `prometheus.rules.yml:8-142`; `alertmanager.tmpl.yml:63-152`; `prometheus.yml:14-17`.
- What it does: 6 rules (service down, 5xx rate, Watchdog, impersonation burst, tenant-scope regression, RLS enforced-share collapse) route by severity/alertname to ntfy (basic auth) and the off-box watchdog.
- Missing controls: latency/SLO-burn, circuit-breaker open, auth-failure spike, notification/webhook failure + dead letters, worker failure/queue depth, disk/memory, edge reachability.
- Risks: silent worker/queue/delivery failures; false confidence from the SLO doc.
- Recommended improvement: add the rules above; run `promtool test rules` in CI.
- Suggested tests: promtool unit cases per rule (fire + no-fire); a CI job; a synthetic end-to-end alert.
- Suggested docs: update `docs/SLO.md` alert column to match reality.

### Item: Prometheus scrape + METRICS_TOKEN
- Evidence: `prometheus.yml:19-32`; `deploy-do.yml:718-727`; `app.ts:154-164`; `health.ts:16-26`.
- What it does: bearer scrape from a 0600 credentials file chowned to the container user; API 404s unauthenticated `/metrics`.
- Missing controls: non-empty guard; post-deploy scrape assertion; limiter headroom.
- Risks: empty token ⇒ 404 scrape ⇒ false `MCTServiceDown` + no metrics (the exact class of incident PR #155 fixed).
- Recommended improvement: fail prod deploy on empty `METRICS_TOKEN`; assert `up{job="mct-api"}==1` post-deploy.

### Item: Logging and correlation
- Evidence: `apps/api/src/lib/logger.ts:6-54`; `apps/worker/src/logger.ts:4-45`; `request-id.ts:15-53`; `compose:19-23`.
- What it does: structured pino logs with requestId, PII redaction, bounded rotation.
- Missing controls: off-box shipping; log survival across `compose down`; worker correlation to the originating request; Caddy access logs.
- Risks: incident forensics window is small and destroyed by the next deploy.

### Item: Health/readiness
- Evidence: `health.ts:91-161`; `health-server.ts:8-57`.
- What it does: API checks DB + Stripe + JSM (30s cache), Redis reported but non-degrading; worker reports queue state.
- Missing controls: queue-disconnected still 200; docs describe an older response shape; no alert on health degradation (only `up`).

### Item: Dashboards/SLOs/runbooks
- Evidence: `mct-overview.json:1-108`; `SLO.md:10-40`; `PLATFORM_FAILURE_RUNBOOKS.md:19-118`; `INCIDENT_RESPONSE.md:126-136`.
- What it does: 5 SLOs with PromQL/error budget; 7-panel dashboard; 5 platform runbooks.
- Missing controls: Grafana; exercised drills; doc accuracy (Alertmanager status, worker metrics, wiring status, broken file references).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| OBS-001 | Structured logs | pino api/worker/web | JSON + redaction + rotation | No shipping; lost on deploy down | P2 | Ship/snapshot logs |
| OBS-002 | Request IDs/correlation | `request-id.ts:15-53` | UUID + `X-Request-ID` | Not propagated to jobs | P3 | Carry id into task payloads |
| OBS-003 | Error tracking | Sentry api/worker/web | API/worker capture | Web DSN never set; release tags absent | P2 | Provide `NEXT_PUBLIC_SENTRY_DSN` |
| OBS-004 | Metrics | `metrics.ts` (30 metrics) | Token-gated, wired | Raw-path cardinality; 25 unalerted | P2 | Normalize labels; add rules |
| OBS-005 | Tracing | Sentry perf sampling | 20% traces when DSN set | No distributed tracing | P3 | Defer; document |
| OBS-006 | Health/readiness | `/health`, `/detail`, worker `/health` | Probes + gated detail | Queue degraded ⇒ 200; docs stale | P3 | Align doc/code; alert queue |
| OBS-007 | Client/API/worker errors | error middleware; task Sentry | Server-side capture | Client-side off (web DSN) | P2 | Fix web DSN |
| OBS-008 | Job metrics | `worker metrics.ts:9-29` | Executions/duration/depth | No rules; fake `unavailable` series | P2 | Add job/queue alerts |
| OBS-009 | DB/queue/webhook/notification metrics | api+worker metrics | Counters/histograms | No rules; reconcile metric missing | P2 | Add rules + reconcile metric |
| OBS-010 | Uptime checks | rules only cover internal `up` | Watchdog for alert path | No external HTTP check | P2 | Add external probe |
| OBS-011 | Alerts | 6 rules + Alertmanager + ntfy | Routed, dead-man's switch | Not CI-validated; not exercised | P2 | CI validate; synthetic delivery |
| OBS-012 | Dashboards | dashboard JSON + SLO.md | Committed artifacts | No Grafana; UI internal | P2 | Provision or document access |

## Findings

Verification of previous register rows (same titles as the previous run):

| Title (previous register) | Sev | Status at 8d299b8d | Evidence / note |
|---|---|---|---|
| Prometheus alert rules are not routed anywhere | P2 | verified-fixed | `prometheus.yml:14-17`, `compose:244-307`, `alertmanager.tmpl.yml:63-152`, `deploy-do.yml:739-747`. Residual: synthetic delivery unproven (RELEASE_GATE.md:34,64). |
| No committed dashboards or SLO/error-budget definitions | P2 | verified-fixed | `dashboards/mct-overview.json:1-108`, `SLO.md:10-40`. Residual: no Grafana; 2 SLOs unalerted. |
| Backup/restore is scheduled but not verified on the deployed branch | P2 | partially-fixed | `db-backup.yml:14`, `db-restore-test.yml:14` (dev env), ntfy notifiers (`db-backup.yml:48-63`). Prod restore still unevidenced. |
| Incident runbooks/tabletop evidence is partial | P3 | partially-fixed | `PLATFORM_FAILURE_RUNBOOKS.md:19-118`; drill table `:110-118` all pending; `INCIDENT_RESPONSE.md:133-136` references missing files. |
| Total loss of the monitoring/alerting path has no independent dead-man's-switch receiver | P0 | verified-fixed | `alertmanager.tmpl.yml:86-100,144-152`; `deploy-do.yml:728-747`. Not exercised end-to-end. |
| No runtime detection or alerting for tenant-isolation (RLS) regressions | P1 | verified-fixed | `metrics.ts:163-196`; `supabase.ts:217,224`; `prometheus.rules.yml:94-142`; `prometheus.rules.test.yml:20-94`. **Correction**: previous register said still-open; rules existed at 9c0b88c. |
| Several Prometheus metrics are declared but not wired, limiting incident diagnosis | P2 | verified-fixed | Call sites verified (organizations/projects/tickets/documents/search/idempotency/admin/users/supabase). Docs stale. |
| No alerting on audit-trail gaps or privileged (impersonation/admin) abuse | P2 | partially-fixed | `MCTImpersonationBurst` rule (`prometheus.rules.yml:48-56`); audit-gap detection still absent. |
| No alerting when webhook dead-letters accumulate or payment reconciliation drifts | P2 | still-open | Dead-letter counters exist; no rules; `stripe-reconcile.ts:91-142` has no metric. |
| Monitoring doc and health endpoint disagree on check semantics; Redis severity undocumented in alerts | P3 | still-open | `MONITORING_AND_ALERTING.md:62,68-79,107` vs `health.ts:118-123,131-161`. |
| `/metrics` is fully public when `METRICS_TOKEN` is unset | P3 | verified-fixed | `health.ts:16-26` fail-closed; `app.ts:161`; Caddy 404 (`Caddyfile:22-23`). |
| `/health` publicly discloses provider configuration and Redis errors | P2 | verified-fixed | `health.ts:128-161`; 30s provider cache `:32-33,45-89`. |
| Availability detection lives inside the failed domain; no external dead-man's switch or alert delivery | P2 | verified-fixed | Same control set as IR-P0-003 + ntfy delivery (`db-backup.yml:59-62`). Not exercised. |

New findings (full field detail in the domain JSON):

| Title | Sev | Confidence | Effort | Status |
|---|---|---|---|---|
| Most golden-signal and SLO metrics have no alert rules (latency, circuit breaker, auth failures, notification/webhook failures, worker jobs, queue depth) | P2 | high | M | open |
| HTTP metric labels use the raw request path, creating unbounded Prometheus series cardinality | P2 | high | S | open |
| Web error tracking is silently disabled in production (`NEXT_PUBLIC_SENTRY_DSN` vs `SENTRY_DSN`) | P2 | high | S | open |
| Alerting configuration is not validated in CI and the deploy health gate ignores Prometheus/Alertmanager | P2 | high | S | open |
| Empty `METRICS_TOKEN` has no deploy guard and is documented as optional; breaks the scrape and fires a false service-down alert | P2 | high | S | open |
| Alert delivery and the dead-man's switch are configured but never exercised end-to-end; no monitoring-of-monitoring rules | P2 | high | S | open |
| Container logs are not persisted off-box and are destroyed by the deploy's `compose down` | P2 | high | M | open |
| No repository evidence of external uptime checks; an edge/proxy failure is undetected in-stack | P2 | high | S | open |
| API/worker Sentry release markers are not delivered (no `SENTRY_RELEASE`/`GIT_SHA`) | P3 | high | S | open |
| Alertmanager secret provisioning gaps: matrix omits `ALERTMANAGER_*`; awk renderer breaks on `&`/backslash | P3 | medium | S | open |
| Metrics rate limiter leaves almost no headroom for the 15s scrape (max 5/min vs 4/min) | P3 | high | S | open |
| SLO and monitoring docs drift from implemented metrics and alert rules | P3 | high | S | open |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent worker/job/queue failure | High | Medium | Stalled notifications/webhooks, data drift | `worker metrics.ts:9-29`; no rules | Add job/queue alerts |
| Prometheus TSDB cardinality blow-up | High | Medium | Monitoring OOM/outage | `request-id.ts:43,47`; `compose:224,232` | Normalize route label |
| Alerting path misconfigured/never exercised | High | Medium | No pages during a real incident | `RELEASE_GATE.md:34,64` | Synthetic alert + drill |
| Broken alert config ships green | High | Low-Med | Monitoring dead post-deploy | `deploy-do.yml:835-858`; no promtool CI | CI validate + gate health |
| Empty METRICS_TOKEN | Medium | Medium | False page + blind metrics | `deploy-do.yml:722-727` | Fail-closed deploy guard |
| Web errors invisible | Medium | High | Client failures unseen | `sentry.server.config.ts:3`; build args | Provide `NEXT_PUBLIC_SENTRY_DSN` |
| Incident evidence lost at deploy | Medium | Medium | Slower triage | `deploy-do.yml:809`; `compose:19-23` | Ship/snapshot logs |
| Edge outage undetected | High | Low-Med | Users down, alerts green | `rules.yml:8-16`; no external probe | External uptime check |

## Recommendations

### Immediate / Release Blocking
- Dispatch a synthetic alert through Prometheus → Alertmanager → ntfy and record the delivery; run one missed-heartbeat drill against the watchdog (`RELEASE_GATE.md:34,64`).
- Provide `NEXT_PUBLIC_SENTRY_DSN` to the web build/runtime or web error tracking stays dead in prod.

### This Week
- Add the missing golden-signal rules (worker failures/queue depth, circuit breaker, auth failures, notification/webhook failure + dead letters, latency burn) with promtool tests.
- Add a CI job (`promtool check rules`, `promtool test rules`, `amtool check-config`) and extend the deploy gate to Prometheus/Alertmanager health and `up{job=~"mct-api|mct-worker"}==1`.
- Fail the prod deploy when `METRICS_TOKEN` is empty; update the secrets matrix to "required for monitoring".

### This Month
- Normalize the HTTP metric `route` label to the Express route template and add a regression test.
- Add an external uptime check for the API `/health` and app login page, routed to ntfy; document it.
- Record a restore test on a production-derived snapshot with row assertions; update `RELEASE_GATE.md`.
- Ship logs off-box (or snapshot before `compose down`); enable Caddy access logs.

### Later / Platform Evolution
- Provision Grafana (or document the SSH-tunnel workflow) and wire the SLO dashboard.
- Add tracing/context propagation if the topology grows beyond one droplet.
- Add audit-trail gap detection and stripe-reconcile drift metrics.
- Refresh `INCIDENT_RESPONSE.md`/`MONITORING_AND_ALERTING.md`/`SLO.md`; create the referenced tabletop/drill docs.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `NEXT_PUBLIC_SENTRY_DSN` build arg | Restores web error tracking | `build-push.yml`, `docker-compose.yml` | Web Sentry event appears in staging |
| Fail-closed `METRICS_TOKEN` guard | Prevents false pages + blind metrics | `deploy-do.yml` | Deploy fails on empty value |
| Promtool CI job | Catches dead/broken rules pre-merge | `.github/workflows/validate.yml` | CI runs rules tests |
| Deploy gate on prometheus/alertmanager health | Green deploy = working monitoring | `deploy-do.yml:835-858` | Broken config fails the deploy |
| Watchdog "fires once per day" comment fix | Removes a misleading claim | `prometheus.rules.yml:3-4` | Review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Golden-signal alert rules + promtool tests | P2 | SRE | M | CI job |
| Route-label normalization | P2 | API platform | S | — |
| Web Sentry DSN delivery | P2 | Web platform | S | Repo secret/variable |
| CI + deploy-gate monitoring validation | P2 | Infra | S | — |
| Synthetic alert + heartbeat drill evidence | P2 | Ops | S | ntfy topic access |
| External uptime check | P2 | Ops | S | DO/uptime service |
| Log shipping/retention | P2 | Ops | M | Budget for log store |
| Audit-gap + reconcile metrics/rules | P3 | API/security, billing | M | — |
| Release markers for API/worker | P3 | Platform | S | — |
| Secrets matrix for ALERTMANAGER_*/NTFY_* | P3 | Infra/docs | S | — |

## Suggested Tests

- Unit: route-label normalization (ids never appear as labels); metric wiring assertions for new counters (pattern already used in `search.test.ts`).
- Rule tests: promtool fire/no-fire cases for every new rule, run in CI (extend `prometheus.rules.test.yml`).
- Config tests: `amtool check-config` on the rendered Alertmanager config; a deploy-step assertion that the rendered file contains no surviving placeholders.
- CI: a validate job that fails on missing rules tests, empty `METRICS_TOKEN` in prod, or unvalidated templates.
- Integration: post-deploy script asserting `up{job=~"mct-api|mct-worker"}==1` and Alertmanager `/-/healthy`.
- Manual: synthetic alert → ntfy delivery evidence; stop-alertmanager heartbeat drill; one tabletop exercise recorded in `PLATFORM_FAILURE_RUNBOOKS.md`.
- Regression: a test that web Sentry init receives a DSN when `SENTRY_DSN` is configured (env wiring).

## Suggested Documentation Updates

- `docs/MONITORING_AND_ALERTING.md`: §2/§3 health semantics + healthcheck commands; §4 metric table ("wired" status); §7 alert table (add Prometheus rules); §9 exercise evidence.
- `docs/SLO.md`: worker/queue metrics now exported; align the Alert column with real rules; note dashboard access path.
- `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`: add `ALERTMANAGER_*`/`NTFY_ALERTS_*`; change `METRICS_TOKEN` to required-for-monitoring.
- `docs/INCIDENT_RESPONSE.md`: §8 update IR-P0-003 status; fix references to `incident_tabletop_scenarios.md` / `backup_restore_drill_plan.md` (create or correct).
- `docs/RELEASE_GATE.md`: record the synthetic-alert and restore-drill artifacts when executed.
- `infra/digitalocean/prometheus.rules.yml`: fix the stale "fires once per day" comment.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` actually set in prod, and where does it point? | The dead-man's switch is only real when set | Operator confirmation; `gh api` environment secrets (names only) |
| Are the Sentry project alert rules from §5 actually configured? | Documented alerting may not exist | Sentry UI screenshot/export |
| Is DO monitoring configured for CPU/disk as §7 claims? | Capacity/disk outage detection | DO dashboard capture |
| Which IP scrapes `/metrics` and does the 5/min limiter ever trip? | Scrape reliability | Prometheus logs/`up` history |
| Does any alerting secret contain `&` or `\`? | awk rendering could break the container | Secret value review by operator (not exported) |
| When was the last green `db-restore-test`, and against which DB? | Release gate condition | Actions run URL |

## Appendix

- Metric vs rule coverage (8d299b8d): `portal_http_requests_total`, `portal_impersonation_events_total`, `portal_rls_bypass_total`, `portal_rls_enforced_total` are referenced by rules; the remaining 26 named metrics (incl. all 9 worker metrics) have no rule.
- Alert path (as configured): Prometheus 15s eval (`prometheus.yml:5`) → `alertmanager:9093` → routes (`alertmanager.tmpl.yml:63-100`) → ntfy critical/default (basic auth) + watchdog heartbeat every 5m (`:99`).
- Deploy sequence relevant to observability: prepare step writes `.env` + `metrics-token` (`deploy-do.yml:666-727`), prod watchdog guard (`:739-747`), copy of monitoring configs (`:797-805`), `compose down`/`up` (`:809-824`), health gate api/web/worker only (`:835-858`), public health loops (`:869-960`).
- Previous-run delta since `9c0b88c`: PRs #154 (ntfy basic auth), #155/#166/#167 (scrape auth + file ownership), #157 (backup ntfy), #147 (metric wiring), #168 (promotion).

## Findings

| ID | Severity | Title |
|---|---|---|
| OBS-P2-001 | P2 | Prometheus alert rules are not routed anywhere |
| OBS-P2-002 | P2 | No committed dashboards or SLO/error-budget definitions |
| OBS-P2-003 | P2 | Backup/restore is scheduled but not verified on the deployed branch |
| OBS-P3-001 | P3 | Incident runbooks/tabletop evidence is partial |
| OBS-P0-001 | P0 | Total loss of the monitoring/alerting path has no independent dead-man's-switch receiver |
| OBS-P1-001 | P1 | No runtime detection or alerting for tenant-isolation (RLS) regressions |
| OBS-P2-004 | P2 | Several Prometheus metrics are declared but not wired, limiting incident diagnosis |
| OBS-P2-005 | P2 | No alerting on audit-trail gaps or privileged (impersonation/admin) abuse |
| OBS-P2-006 | P2 | No alerting when webhook dead-letters accumulate or payment reconciliation drifts |
| OBS-P3-002 | P3 | Monitoring doc and health endpoint disagree on check semantics; Redis severity undocumented in alerts |
| OBS-P3-003 | P3 | `/metrics` is fully public when `METRICS_TOKEN` is unset |
| OBS-P2-007 | P2 | `/health` publicly discloses provider configuration and Redis errors |
| OBS-P2-008 | P2 | Availability detection lives inside the failed domain; no external dead-man's switch or alert delivery |
| OBS-P2-009 | P2 | Most golden-signal and SLO metrics have no alert rules (latency, circuit breaker, auth failures, notification/webhook failures, worker jobs, queue depth) |
| OBS-P2-010 | P2 | HTTP metric labels use the raw request path, creating unbounded Prometheus series cardinality |
| OBS-P2-011 | P2 | Web error tracking is silently disabled in production (code reads NEXT_PUBLIC_SENTRY_DSN; deploy provides SENTRY_DSN) |
| OBS-P2-012 | P2 | Alerting configuration is not validated in CI and the deploy health gate ignores Prometheus/Alertmanager |
| OBS-P2-013 | P2 | Empty METRICS_TOKEN has no deploy guard and is documented as optional; it breaks the API scrape and fires a false service-down alert |
| OBS-P2-014 | P2 | Alert delivery and the dead-man's switch are configured but never exercised end-to-end; no monitoring-of-monitoring rules |
| OBS-P2-015 | P2 | Container logs are not persisted off-box and are destroyed by the deploy's `compose down` |
| OBS-P3-004 | P3 | API/worker Sentry release markers are not delivered (no SENTRY_RELEASE/GIT_SHA) |
| OBS-P3-005 | P3 | Alertmanager secret provisioning gaps: matrix omits ALERTMANAGER_*; awk renderer breaks on '&' or backslash in values |
| OBS-P3-006 | P3 | Metrics rate limiter leaves almost no headroom for the 15s scrape (max 5/min vs 4/min) |
| OBS-P2-016 | P2 | No repository evidence of external uptime checks for platform endpoints; an edge/proxy failure is undetected in-stack |
| OBS-P3-007 | P3 | SLO and monitoring docs drift from implemented metrics and alert rules |
