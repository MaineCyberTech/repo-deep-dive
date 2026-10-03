# Notification, Email, and Push Delivery Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab profile, prompt 30 ADAPTED)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: `/home/user/falcon-build` (central) + `/home/user/falcon-edge-build` (edge); branch `main`
- Commit SHA: central `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c`; edge `45dfed050fba9c25d7f8f8b5c64526887379ce84` (dirty, in-flight CI work)
- Generated at: 2026-09-30T07:28Z · Auditor: audit subagent (read-only; no test sends, no mutations) · Area code: NOTIF
- Output path: docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/30_notification_email_push_delivery_audit.md
- Scope limitations: no synthetic alert fired (would notify the owner); delivery verified from config + read-only journal; secrets files root-only and unread; DO host aside from journal/exported metrics not inspected.

## Scope

Reviewed: Grafana alert rules and notification policy (`bootstrap/90-alerting.sh`, catalogue), the `falcon-alert-relay` webhook receiver and dual ntfy publish path, the lab and independent ntfy instances, dead-man heartbeat + DO watcher, noise/flapping and dedupe, contact-point auth, delivery evidence, and refresh/alert tests. Email is disabled by design; mobile push is delegated to the ntfy app (no VAPID/web-push code exists). Not reviewed: the DO host itself, the owner's phone-side subscriptions, and ntfy internals beyond repo config.

## Evidence Reviewed

- `falcon-build/automation/alerting/ntfy_relay.py`; `config/systemd/falcon-alert-relay.service`; `bootstrap/90-alerting.sh` (contact point 40-105, policy 115-129, rules 202-323)
- `falcon-build/docs/phase9/ALERT_CATALOGUE.yaml` (31 live-generated rules); `automation/validation/build_alert_catalogue.py`
- `falcon-build/config/ntfy/server.yml`; `automation/validation/{heartbeat.sh,service_probe.sh,storm_measurement.sh,alert_storm_test.sh,ntfy_sh_alert_test.sh,device_alert_test.sh,phase9_notification_tests.sh}`
- `falcon-build/config/systemd/falcon-heartbeat.{service,timer}`; `docs/phase9/{PROGRESS_2026-09-23.md,NOTIFICATION_SEPARATION_RUNBOOK.md}`; `automation/vpn/site-monitoring.sh`; `export_monitor_metrics.sh:355-388`
- `falcon-build/automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf:7-11` (email off); `ledgers/decision_log.md` (73, 93, 96); `ledgers/phase9_gate_ledger.csv` (P9-G07)
- Run dir `live_snapshot.txt`; read-only `journalctl -u falcon-alert-relay --since "-7 days"` (counts only)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Relay journal 2026-09-23→30 | live read-only | delivery accounting | 148 primary `[200]`, 147 alt `[200]`; 12 failure lines (setup + outage) |
| Per-rule journal count | live read-only | noise quantification | TLS-silence 88/148 (59.5%); Device syslog errors 8; long tail ≤6 |
| Sep 28 outage window | live read-only | dead-man/real outage | FIRING 10:58:26 primary; alt failed 10:58:37 (DNS); last log 10:59:06; reboot 15:30:53 |
| Rule-window change | commit + catalogue | LIVE-P0-004 status | `d83f421` 04:12:24Z sets TLS `for: 6h`; 0 fires in ~3.2 h since |
| Relay code path | source | delivery guarantees | 200 returned before publish; 2 immediate attempts; no spool |
| Contact point/policy | source | routing | webhook URL with path token; group_wait 10 s; repeat 4 h |
| Wazuh email settings | source | email N/A | `<email_notification>no</email_notification>` |
| ACL/alert tests | source only | not executed | state-mutating tests skipped per audit rules |

## Executive Summary

The alert path exists, runs daily, and is better than most labs: 31 rules as code, resolved notifications, a readable-message relay, a second ntfy instance on an independent host, a dead-man watcher, and storm/ACL proofs. The dominant risks are deliverability and path honesty: the relay acknowledges Grafana before publishing and keeps nothing when ntfy is unavailable; total-host failure still has no real-time external signal (the Sep 28 outage was detected by humans after reboot); and the webhook receiver is protected only by a static path token with a fail-open branch, reachable from every Docker bridge gateway. The largest noise source (TLS-silence, 59% of deliveries) was tuned to 6 h today; early evidence is clean but only ~3 h old. Recommended: fail-closed + bounded spool/backoff + failure metric on the relay; re-measure noise after a week; repo-ize the watcher/ntfy provisioning; refresh the stale ntfy.sh-era tests.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Alert rules | `bootstrap/90-alerting.sh`; live Grafana | detection | 31 rules; catalogue 31/31 | Low | regenerated at HEAD; includes `falcon-wg-peer-stale` |
| Routing policy | `90-alerting.sh:115-123` | grouping | group_by alertname; 4 h repeat | Low | no per-severity routes |
| Contact point | `90-alerting.sh:66-105` | delivery | webhook → relay `/<path-token>` | Medium | single point; no fallback |
| Relay | `ntfy_relay.py` | render + publish | running; all bridge gateways | High | at-most-once; fail-open if token empty |
| Lab ntfy | `config/ntfy/server.yml`; 127.0.0.1:2586 | subscriber delivery | healthy (live 200) | Medium | deny-all; cache 48 h; internal rate-exempt |
| Independent ntfy | `https://ntfy.mainecybertech.us` (DO) | second failure domain | live; 147 alt deliveries/7 d | Medium | config/creds out of repo; same topic/user |
| Dead-man heartbeat | `heartbeat.sh`; daily timer | liveness publish | inside monitored stack | High | absence-based only |
| DO watcher | `PROGRESS_2026-09-23.md`; `SITE_HOST_ONBOARDING.md:150` | off-host liveness | 15-min cadence, 26 h threshold; source not in repo | Medium | last-run metric exists, unalerted |
| Email | Wazuh `ossec.conf:7-11` | — | disabled, placeholder SMTP | n/a | intentional; no templates |
| Mobile push | ntfy app (out of repo) | phone delivery | two subscriptions | Low | no VAPID/web-push code |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Notification models | 3 | rules-as-code + catalogue | single channel; no templates | keep; per-rule owner |
| Email templates | 0 | email off | intentionally absent | mark N/A in docs |
| Push subscriptions | 3 | two ntfy instances | setup not reproducible | repo-ize provisioning |
| VAPID/config | n/a | no web-push code | none | none |
| Reminder jobs | 2 | daily heartbeat + 15-min watcher | 26 h detection latency | shorten/verify |
| Preferences | 1 | single owner account | no per-user prefs | document |
| Tenant scoping | n/a | single tenant | none | none |
| Unsubscribe/opt-out | 1 | client-side only | undocumented | document revocation |
| Retries | 2 | relay x2 immediate | no backoff/spool | bounded retry |
| Failure handling | 2 | journal only; alt best-effort | no metric/alert | export + alert |
| Duplicate prevention | 2 | Grafana grouping; 4 h repeat | no relay dedupe | idempotency key |
| Rate limiting | 3 | `server.yml:13-15` | relay unbounded | token bucket |

## Detailed Review

### Item: Grafana rules → relay → ntfy
- Evidence: `90-alerting.sh:57-105`; `ntfy_relay.py:194-249`; live journal.
- Works: fixed JSON payload rendered into title/priority/tags/click; priority urgent for critical; resolved messages enabled; publishes to lab + independent instance.
- Controls: ntfy deny-all + TLS; click deep-link; grouping.
- Gaps: no ACK/retry persistence, no failure metric, no HMAC/replay, no rate limit, fail-open when `TOKEN` is empty (`ntfy_relay.py:197-200`; startup WARN only).
- Fix: fail-closed token, constant-time compare, HMAC + timestamp, bounded spool with backoff, `falcon_relay_publish_failures_total` + alert, per-rule noise budget. Tests: auth branches; ntfy-down retry; replayed body rejected.

### Item: Dead-man heartbeat and independent watcher
- Evidence: `heartbeat.sh`; daily timer; unit description "production must run outside the monitored stack"; `PROGRESS_2026-09-23.md:14` (DO watcher, 26 h threshold, expiry test 07:22:58Z); P9-G07 PASS (residual EX-22).
- Works: off-host watcher alerts the independent instance on a stale heartbeat.
- Gaps: 26 h detection latency; publisher co-hosted (no mutual check); watcher script/config/threshold not in repo; `falcon_site_watcher_last_run_timestamp_seconds` exported but unalerted.
- Fix: shorten threshold (owner decision); alert on watcher staleness; repo-ize watcher; consider publisher on the independent host. Tests: documented expiry drill; watcher-stale alert.

### Item: Noise, flapping, duplicates
- Evidence: live journal; `90-alerting.sh:115-123`; catalogue TLS `for: 6h`.
- Works: one notification per group; repeat 4 h while firing; resolved notices.
- Observed (7 days): TLS-silence 46 F + 42 R = 88/148 (59.5%); Device syslog errors 8; remainder ≤6 each (incl. 4 manual `post-reboot-check` posts).
- Gaps: no per-rule noise budget/review gate; known-benign filters absent (prior LIVE-P1-004); no relay dedupe; 6 h window delays a real Wazuh/TLS-path outage.
- Fix: re-measure after 7 days; add expected-rate notes; per-host link-flap and benign-message filters; record the 6 h trade-off.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| NOTIF-001 | Notification models | rules-as-code; catalogue | 31 rules | single route | P3 | keep |
| NOTIF-002 | Email templates | `ossec.conf:7-11` | disabled | no fallback channel | P3 | document N/A |
| NOTIF-003 | Push subscriptions | ntfy app; progress doc | dual instance | setup out of repo | P2 | repo-ize |
| NOTIF-004 | VAPID/config | no web-push code | n/a | n/a | n/a | none |
| NOTIF-005 | Reminder jobs | heartbeat/watcher | dead-man | 26 h latency | P1 | shorten; mutual check |
| NOTIF-006 | Preferences | single owner account | none needed | undocumented | P3 | document |
| NOTIF-007 | Tenant scoping | single tenant | n/a | none | n/a | none |
| NOTIF-008 | Unsubscribe/opt-out | ntfy ACLs | account revoke | undocumented | P3 | document |
| NOTIF-009 | Retries | `ntfy_relay.py:105-132` | 2 immediate attempts | no backoff/spool | P1 | bounded retry + spool |
| NOTIF-010 | Failure handling | journal only | alt best-effort | no metric/alert | P1 | export + alert |
| NOTIF-011 | Duplicate prevention | group_by; 4 h repeat | grouping | relay no dedupe | P2 | idempotency key |
| NOTIF-012 | Rate limiting | `server.yml:13-15` | ntfy visitor limits | relay unbounded | P2 | token bucket |

## Findings

### Finding ID: NOTIF-P1-001 - Total-host failure still has no real-time external notification; dead-man detection is up to 26 h
- Severity: P1 · Confidence: High · Area: NOTIF (dead-man/heartbeat)
- Evidence: live journal 2026-09-28 — `published [200] FIRING: User-facing service down` and `Site host unreachable` at 10:58:26Z, `published_alt failed: [Errno -3] Temporary failure in name resolution` at 10:58:37Z, last host journal 10:59:06Z, reboot 15:30:53Z. `falcon-heartbeat.service` runs a daily publisher inside the stack; `PROGRESS_2026-09-23.md:14` documents the DO watcher (15-min cadence, 26 h threshold, expiry test); `SITE_HOST_ONBOARDING.md:150` names only its log path; no watcher installer exists in either repo; `export_monitor_metrics.sh:377-378` exports its last-run but no rule in `90-alerting.sh`/the catalogue uses it.
- What is happening: a power/network loss kills in-flight external publish, and the only detector is the off-host watcher at a 26 h threshold.
- Why it matters: the monitoring system cannot announce its own death promptly.
- User/business impact: outages run until a human notices (Sep 28 ~4.5 h undetected); MTTD hours-to-a-day · Security/privacy/reliability impact: reliability/incident readiness of the alert path itself.
- Recommended fix: shorten the watcher threshold (owner decision), alert on the watcher last-run metric, store watcher + ntfy provisioning in the repo, and consider a mutual check with a publisher on the independent host.
- Suggested validation: documented expiry drill; stop the lab heartbeat → external alert within the documented threshold.
- Owner suggestion: falcon maintainer/owner · Effort: M · Dependencies: DO access · Status: still-open (prior LIVE-P1-007; partially fixed)

### Finding ID: NOTIF-P1-002 - Relay acknowledges Grafana before delivery and keeps nothing on failure
- Severity: P1 · Confidence: High (mechanism) / Medium (realized loss) · Area: NOTIF (retries/failure)
- Evidence: `ntfy_relay.py:216-219` starts `publish` in a daemon thread and immediately returns HTTP 200; `publish` (105-132) makes two immediate attempts, no sleep/persistence/queue; errors only print to stderr; `publish_alt` (94-103) best-effort. Live: 148 primary vs 147 alt `[200]` over 7 days; alt failures during the Sep 28 outage after Grafana was acknowledged; `service_probe.sh:30` covers relay liveness only, not publish failures.
- What is happening: any ntfy downtime/restart/network blip during an alert window silently drops the notification while the alert source believes delivery succeeded.
- Why it matters: the alert channel is part of the monitoring system; silent loss defeats it.
- User/business impact: missed pages; no reconstructable delivery history outside journald · Security/privacy/reliability impact: alerting reliability.
- Recommended fix: persist pending messages, retry with capped backoff, export `falcon_relay_publish_failures_total` + alert, and return non-200 to Grafana when nothing was delivered (so Alertmanager retries).
- Suggested validation: stop ntfy, fire a test alert, confirm retry + metric; restart ntfy, confirm eventual delivery.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: NOTIF-P2-001 - Webhook auth is a static path token with a fail-open branch, bound to every Docker bridge gateway
- Severity: P2 · Confidence: High (code) / Medium (exploitability) · Area: NOTIF (auth/replay)
- Evidence: `ntfy_relay.py:197-200` (`if not TOKEN: return True`, else exact path compare), `42` (token read once at import), `48-65,236-249` (auto-detected bridge addresses; live on `172.17.0.1:9099` and `172.30.0.1-8.1:9099` per `live_snapshot.txt`); `90-alerting.sh:59-61` embeds the token in the contact-point URL; no timestamp/HMAC/replay check; no rate limit.
- What is happening: a bearer token in the URL path is the only gate; a missing/empty secret fails open; any container on a shared bridge can post.
- Why it matters: a compromised container can spoof or flood operator notifications; a missing secret silently disables auth.
- User/business impact: trust in alerts; potential alert suppression/social engineering · Security/privacy/reliability impact: spoofable notification channel; token exposure in URL logs/DB.
- Recommended fix: fail closed, constant-time compare, HMAC + timestamp of the raw body, reject stale/replayed requests, per-source rate limit, bind only the frontend gateway.
- Suggested validation: unit tests for empty/wrong token and replay; unauthorized bridge container gets a 403/refused.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: NOTIF-P2-002 - Noise concentrated in one rule (59% of deliveries); tuning is only ~3 h old
- Severity: P2 · Confidence: High (counts) / Medium (post-tune effect) · Area: NOTIF (noise/flapping)
- Evidence: relay journal 2026-09-23→30 — `Syslog-TLS feed silence` 46 F + 42 R = 88/148 (59.5%); next is `Device syslog errors` 8; long tail ≤6. TLS rule widened to `for: 6h` in `d83f421` at 04:12:24Z; `ALERT_CATALOGUE.yaml:239-246` (live-generated) records it; zero deliveries since 04:12:28Z (~3.2 h).
- What is happening: the TLS feed carries sparse Wazuh forwards, so a short window flapped hourly; 6 h trades noise for slower detection of a genuinely dead Wazuh/TLS path.
- Why it matters: 59% of notifications were one dim signal; fatigue suppresses attention on real alerts.
- User/business impact: operator fatigue, previously 56% noise (prior LIVE-P0-004) · Security/privacy/reliability impact: a real outage is detected up to 6 h late.
- Recommended fix: require per-rule expected-rate/noise budget in `build_alert_catalogue.py`; re-measure after 7 days; add benign-family suppression and per-host link-flap; record the 6 h trade-off.
- Suggested validation: 7-day per-rule counts fall within budget; a real feed outage still pages within the documented window.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: 7-day data · Status: partially-fixed (prior LIVE-P0-004)

### Finding ID: NOTIF-P2-003 - Notification configuration is not reproducible; the watcher guarding it can fail invisibly
- Severity: P2 · Confidence: High · Area: NOTIF (sender config/worker queues)
- Evidence: ntfy users/ACLs/topic and alt-instance setup were done out of band (decision log 2026-09-22T07:12Z; `bootstrap/50-secrets.sh:88-94` creates only HTTP basic files; `90-alerting.sh` creates the relay token/topic but no ntfy users); the DO watcher exists only in `PROGRESS_2026-09-23.md`/`SITE_HOST_ONBOARDING.md:150`; `site-monitoring.sh` installs only the metric writer; the watcher last-run metric is unused by any rule.
- What is happening: a host rebuild cannot restore the alert path from the repo; watcher death is silent.
- Why it matters: recovery time for the notification path is unbounded; monitoring-of-the-monitoring gap.
- User / business impact: alerting may be absent after recovery without anyone knowing.
- Recommended fix: idempotent provisioning script (ntfy users/ACL/topic, relay creds, alt instance, watcher install) with rollback notes; add the watcher-stale alert.
- Suggested validation: rebuild rehearsal from repo scripts only; kill the watcher → alert fires.
- Owner suggestion: falcon maintainer/owner · Effort: M · Dependencies: DO access · Status: open

### Finding ID: NOTIF-P3-001 - Refresh/storm tests still poll the retired external ntfy.sh path
- Severity: P3 · Confidence: High · Area: NOTIF (tests/docs)
- Evidence: `alert_storm_test.sh:27`, `device_alert_test.sh:15`, `ntfy_sh_alert_test.sh:12` read `https://ntfy.sh/${NTFY_TOPIC}`; production has been self-hosted since 2026-09-22 (decision log 73; R-24 closed "external ntfy.sh is no longer used"); `storm_measurement.sh` is the updated variant.
- Why it matters: tests can pass/fail against a channel nobody uses, giving false confidence.
- Recommended fix: point the tests at the live relay/self-hosted ntfy or mark them superseded.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none · Status: open

### Finding ID: NOTIF-P3-002 - Preferences/opt-out and notification content handling are undocumented
- Severity: P3 · Confidence: Medium · Area: NOTIF (preferences/privacy)
- Evidence: a single `owner` account is shared across both instances for one phone (`PROGRESS_2026-09-23.md`); the relay publishes summaries, selected labels and up to 300 chars of values (`ntfy_relay.py:155-172`), with a JSON fallback up to 800 chars; no preference store or unsubscribe procedure is documented; ntfy cache 48 h (`server.yml:6`).
- Why it matters: alert content includes hostnames/IPs and rule details; recipients have no documented pause/scope/opt-out path.
- Recommended fix: document per-topic subscriptions, mute windows and account revocation; state what content can appear and keep secrets out of annotations; confirm the mobile push transit path with the owner.
- Owner suggestion: falcon maintainer/owner · Effort: S · Dependencies: none · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent alert loss on transient ntfy failure | P1 | Medium | Missed pages | relay code; journal counts | spool + backoff + failure metric |
| Total-host outage detected up to 26 h late | P1 | Medium | Long MTTD | Sep 28 timeline; watcher threshold | shorten; mutual check; watcher alert |
| Spoofed/flooded notifications from bridges | P2 | Low-Medium | Trust loss | path token; bridge binds | HMAC, fail-closed, rate limit |
| Noise from one dim rule | P2 | Was high | Fatigue | 88/148 deliveries | keep 6 h; re-measure; filters |
| Path not rebuildable from repo | P2 | Medium | Recovery delay | out-of-band setup | provisioning scripts |

## Recommendations

### Immediate / Release Blocking
- Fix the relay fail-open branch and add a delivery-failure metric/alert; publish failures must not be visible only in journald.

### This Week
- Decide and record the dead-man threshold; add the watcher-stale alert; re-measure TLS noise after a full week; rotate notification credentials if they entered a delivered artifact (see API-P0-001).

### This Month
- Bounded spool/retry + replay protection; repo-ize ntfy/watcher provisioning; update stale ntfy.sh tests; add per-rule noise budgets.

### Later / Platform Evolution
- Per-user preferences/opt-out, severity-based routing, and a documented alternate/email fallback if the owner wants one (currently intentionally absent).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fail closed on missing relay token | removes silent open gate | `automation/alerting/ntfy_relay.py` | unit test |
| Alert on watcher last-run > 1 h | watcher death becomes visible | `bootstrap/90-alerting.sh` | rule in catalogue |
| Update tests to self-hosted ntfy | tests match production | `automation/validation/*alert*test*.sh` | test run |
| Catalogue note for 6 h TLS window | audit trail for the trade-off | `build_alert_catalogue.py` | regenerated catalogue |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Relay spool + backoff + failure metric | P1 | falcon maintainer | M | none |
| Dead-man threshold + watcher alert + mutual check | P1 | owner + maintainer | M | DO access |
| HMAC/replay/rate-limit on webhook | P2 | falcon maintainer | M | none |
| Reprovisionable ntfy/watcher install | P2 | falcon maintainer | M | DO access |
| Per-rule noise budget | P2 | falcon maintainer | S | 7-day data |

## Suggested Tests

- Unit: relay auth branches (token present/absent/wrong; unknown path); render priority/tags/click; HMAC + replay rejection.
- Integration: ntfy stopped → spool/retry/failure metric; watcher expiry drill; dual-path delivery from a relay test message (owner-approved, off-hours).
- E2E: one rule per severity class fired and resolved on both instances; count duplicates (expect one per group per repeat window).
- CI: catalogue regenerated from live rules equals deployed rules; every rule declares runbook + review date.
- Manual: verify the phone shows FIRING and RESOLVED from each instance; verify an unauthorized POST is rejected.

## Suggested Documentation Updates

- New `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`: channels, thresholds, failover drill, token rotation, watcher install/rollback.
- `docs/phase9/NOTIFICATION_SEPARATION_RUNBOOK.md`: correct the 2026-09-23 "Current state" and add the 6 h TLS-window rationale.
- `docs/runbooks/OPERATOR_START_HERE.md`: "if you stop receiving alerts" checklist.
- `build_alert_catalogue.py`: delivery budget/expected-rate; map `falcon-wg-peer-stale` to `docs/runbooks/VPN.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the mobile push path transit an upstream push service? | sensitive content egress | ntfy client/server config or owner confirmation |
| What is the owner-accepted detection target for total-host loss? | sets watcher threshold | owner decision record |
| Are `Device syslog errors` notifications still single benign messages? | remaining noise budget | 7-day post-September counts |
| Should every alert page, or only critical? | priority model | owner preference |

## Appendix

Live delivery accounting (read-only journal, 7 days; primary 148 / alt 147): `Syslog-TLS feed silence` 46 F + 42 R; `Device syslog errors` 4 F + 4 R; `Syslog 514 feed silence` 3 F + 3 R; `Capture fidelity degraded` 3 F + 2 R; `SPAN flow feed silence`, `Remote syslog feed silence (15140)`, `NetFlow feed silence`, `Disk space low` 2 F + 2 R each; `User-facing service down` and `Site host unreachable` 2 F + 1 R; `post-reboot-check` 4 F (manual `post_reboot_verify.sh` hook); `VPN tunnel stale`, `TLS certificate expiring (drill)`, `Sensor silence`, `Probe buffer filling` 1 F + 1 R; `Probe buffer near cap` and `Container unhealthy` 1 R. Prior-run verification: LIVE-P0-004 partially-fixed (above); LIVE-P1-004 partially-fixed (catalogue 31=31 fixed; benign filters absent); LIVE-P1-007 still-open (independent path + watcher live; real-time gap/out-of-repo watcher remain); INTG-P1-001 still-open (edge rules prepared in `config/prometheus/edge-alerts.yaml`, deploy gated by D-007, `prometheus.yml` has no `rule_files`); INTG-P2-004 verified-fixed (catalogue matches 31 live rules incl. `falcon-wg-peer-stale`).
