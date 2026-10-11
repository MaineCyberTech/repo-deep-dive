# 30_notification_email_push_delivery_audit — Prompt 30 - Notification, Email, and Push Delivery Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `30_notification_email_push_delivery_audit.md` (area NOTIF, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon
- Branch: main (origin/main)
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:45:00Z
- Auditor: repo-deep-dive full-domain subagent (read-only; live lab host vantage)
- Area code: NOTIF
- Live vantage: this audit ran on the live lab host. Live tree `/home/user/falcon-build` == `f5cb7c9` (clean, 0 dirty files). The live Traefik config is the repo file (bind mount `/home/user/falcon-build/config/traefik/dynamic.yml -> /etc/traefik/dynamic.yml`), the live ntfy `server.yml` is byte-identical to the repo file, and the DO watcher script hash matches the repo script - so the live observations bind to the audited commit for this domain.

## Scope

Reviewed: the Grafana -> relay -> ntfy delivery path (`automation/alerting/ntfy_relay.py`, `config/systemd/falcon-alert-relay.service`, `bootstrap/90-alerting.sh` contact point/policy), self-hosted lab ntfy configuration and ACLs (`config/ntfy/server.yml`, `automation/alerting/provision_ntfy.sh`), the dead-man heartbeat and independent watcher (`automation/validation/heartbeat.sh`, `automation/alerting/do_watcher/`), the public-access architecture after the 2026-10-09/11 change (only `ntfy.mainecybertech.us` public; lab ntfy internal-only; tunnel remote config v13 = falcon/iris/enroll), delivery verification (`automation/validation/alert_canary.sh`, live textfile metrics, `post_reboot_verify.sh`), noise/dedupe, preferences/opt-out, sensitive content, sender config, retries/failure handling, rate limiting, and the offline tests.

Not reviewed: the owner's phone-side subscriptions and the DO instance's internals beyond the watcher (owner-gated; verified via its health/topic read and the watcher log), and mobile-push transit (Firebase/APNs) which remains an owner confirmation item.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `automation/alerting/ntfy_relay.py` | code | fail-closed token auth (hmac compare), per-source rate limit (120/60s), dual-path publish, bounded replay spool, per-path metrics, 502 on total failure | live process runs the repo bytes |
| `config/systemd/falcon-alert-relay.service` | unit | relay env: `MON_RELAY_ALT_URL=https://ntfy.mainecybertech.us/falcon-alerts` | live unit matches |
| `bootstrap/90-alerting.sh:87-147` | provisioning | contact point `falcon-ntfy` -> relay; policy group_by alertname, group_wait 10s, group_interval 1m, repeat_interval 4h | live Grafana matches (86 rules live) |
| `config/ntfy/server.yml` | config | lab ntfy: base-url `https://ntfy.falcon.lab`, deny-all default, 48h cache, visitor limits with internal exemption | live container file identical |
| `automation/alerting/provision_ntfy.sh:89-127` | provisioning | 4 production users/ACLs (monadmin admin; falcon-relay wo; owner rw; watcher ro) | live users match; test-topic entries now explicit denies |
| `automation/validation/heartbeat.sh:15-34` | dead-man | publishes hourly to lab topic AND the independent instance; per-path HTTP codes | live: `heartbeat_publish=200` / `heartbeat_publish_independent=200` hourly |
| `automation/alerting/do_watcher/watch.sh:17-54` + `install.sh:16` | dead-man | watcher now reads the independent topic LOCALLY (`http://127.0.0.1:8080/falcon-alerts`, user `falcon-relay2`); 2h threshold; cron */5 | deployed script sha256 == repo script; log `ok: heartbeat age …`; state `ok` |
| `config/traefik/dynamic.yml:26-28,77-86,87-124` | public access | lab ntfy internal-only (`Host(ntfy.falcon.lab)`); former public lab-ntfy routers removed; `ntfy-auth` middleware still defined but unreferenced | live Traefik mounts this file read-only |
| `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh` | public access | tunnel ingress hosts falcon/iris/enroll | live remote config v13 (03:51:14Z) matches |
| `automation/validation/alert_canary.sh:28-29,74-122` | verification | weekly canary proves lab + independent + relay paths; last_success only when all three 2xx | last run 2026-10-05; all three up |
| `automation/validation/tests/{ntfy_relay_auth_test.py,heartbeat_independence_test.sh,deadman_contract_test.sh,alert_canary_test.sh}` | tests | offline delivery/auth/dead-man regression suites | wired via `ci/validate.py` test step |
| live: ntfy user list/access; cloudflared journal + Cloudflare API; DO watcher (ssh read-only); Grafana API; textfile metrics; 48h topic export | live | current delivery, ACLs, public reachability, noise | read-only; secrets never printed |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Lab ntfy internal-only | `docker port falcon-central-ntfy-1`; `curl http://127.0.0.1:2586/v1/health`; SNI `ntfy.falcon.lab` | `80/tcp -> 127.0.0.1:2586`; health 200; SNI health 200 |
| Anonymous read denied | `curl http://127.0.0.1:2586/falcon-alerts/json?poll=1` | 403 (deny-all enforced) |
| ACLs | `docker exec falcon-central-ntfy-1 ntfy user list/access` | 4 production users as designed + anonymous deny-all; former test-topic grants now explicit `no access` denies |
| Tunnel ingress (effective) | cloudflared journal + Cloudflare API `cfd_tunnel/a2d74235…/configurations` | remote config **version 13** (created 2026-10-11T03:51:14Z, source cloudflare): `falcon`, `iris`, `enroll`, catch-all. **No lab-ntfy hostname.** |
| DNS | Cloudflare API zone `mainecybertech.us` (22 records) | no `falcon-ntfy` / `ntfy.falcon` records; `ntfy.mainecybertech.us` -> DO tunnel `4ab18c9c…`; `falcon-ntfy` resolves only via the zone wildcard and returns 521 (no origin route) |
| Public independent instance | `curl https://ntfy.mainecybertech.us/v1/health`; owner-credential topic read | 200; 48h topic export read OK (335 messages) |
| DO watcher | `ssh root@138.197.105.82` (read-only): sha256, log, state, cron, health | script sha256 `5138c56e…` == repo; log `ok: heartbeat age 601s…1801s`; state `ok`; cron `*/5`; local ntfy health 200 |
| DO watcher metrics | `http://10.99.0.10:9100/metrics` | `falcon_site_watcher_last_run_timestamp_seconds{site="do-server"}` = 2026-10-11T04:35:02Z; `falcon_site_container_up{name="falcon-alerts2"}` = 1 |
| Heartbeat | `journalctl -u falcon-heartbeat --since "24 hours ago"` | hourly `heartbeat_publish=200` and `heartbeat_publish_independent=200` |
| Relay delivery | `journalctl -u falcon-alert-relay`; `/srv/falcon/textfile/falcon_relay.prom` | 168 publishes/24h; lab 8 ok / alt 8 ok since reboot; 0 failures; no unauthorized attempts logged |
| Service probe | `/srv/falcon/textfile/falcon_services.prom` | `ntfy`=1, `relay`=1, `dash`=1, `do-ntfy-public`=1 |
| Canary | `/srv/falcon/textfile/falcon_alert_canary.prom` | lab=1, independent=1, relay=1; last full success 2026-10-05T06:00Z (weekly; next 2026-10-12) |
| Grafana contact point / policy | Grafana provisioning API (live) | `falcon-ntfy` webhook -> relay (token redacted); repeat_interval 4h; 86 rules live |
| Noise quantification | independent topic 48h export (read-only) | 335 messages: 206 FIRING + 81 RESOLVED + 48 heartbeats; top offender "disk guard: root still below threshold" 47 msgs; 91/169 same-title FIRING gaps < 4h |
| Sensitive content | regex scan of all 335 message titles/bodies for secret-like patterns | 0 matches; max message 910 bytes; mobile push sees titles only (documented) |
| Email | `/opt/wazuh-docker/multi-node/config/wazuh_cluster/wazuh_manager.conf:7` | `<email_notification>no</email_notification>`; no first-party email sender exists |
| Push/VAPID | repo grep | no VAPID/web-push/FCM/APNs code; delivery delegated to the ntfy app (documented) |

## Executive Summary

The notification path is in the best state this audit series has seen. The 2026-10-09/11 architecture change is live and verified end to end: the lab ntfy is internal-only (loopback publish), the only public ntfy is the independent `https://ntfy.mainecybertech.us`, the effective tunnel ingress (remote config v13) is exactly `falcon/iris/enroll`, the dead-man watcher reads the independent topic locally on the DO (`ok: heartbeat age …`, script == repo), heartbeats publish 200/200 hourly to both failure domains, the relay is fail-closed and dual-path with zero failures, and the weekly canary proves lab + independent + relay. The prior P1 (dead public lab-ntfy endpoint) and the stale test-topic ACL grants are verified-fixed. Three issues remain: (P2) notification noise is still high - 335 messages/48h with 206 FIRING/81 RESOLVED and 91 of 169 same-title FIRING gaps below Grafana's 4h repeat interval; the top driver is now the *accurate* disk-guard root alert (47 messages, tied to the SEARCH-P2-002 root-LV condition), so fixing the root capacity issue also removes the largest noise source; (P3) the `ntfy-auth` Traefik middleware is still dead config (no router references it) while ntfy-native deny-all is the actual control; (P3) retired public lab-ntfy hostnames still appear in the exception/risk ledgers and in the 97 deploy script's fallback instructions, which could misdirect a manual tunnel repair.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Relay | `automation/alerting/ntfy_relay.py` | Grafana webhook -> ntfy | running; fail-closed; dual-path; 0 failures | low | per-source 120/60s rate limit; bounded spool |
| Lab ntfy | `config/ntfy/server.yml` + container | primary internal topic | internal-only (127.0.0.1:2586); deny-all; 48h cache | low | base-url `https://ntfy.falcon.lab` |
| Independent ntfy | DO host, `ntfy.mainecybertech.us` | public owner topic + watcher source | 200; owner read verified | low | falcon-alerts2 container up |
| Heartbeat | `automation/validation/heartbeat.sh` + timer | dead-man liveness | hourly 200/200 | low | independent path also 200 |
| Watcher | `automation/alerting/do_watcher/watch.sh` | independent dead-man | local read; `ok`; 5-min cron | low | deployed == repo |
| Grafana policy | `bootstrap/90-alerting.sh:133-141` | grouping/repeat | group_by alertname; repeat 4h | medium | no relay-side dedupe |
| ACLs | `provision_ntfy.sh` + live user DB | least-privilege access | 4 users + deny-all; test grants revoked to deny | low | explicit deny entries remain (cosmetic) |
| Canary | `automation/validation/alert_canary.sh` | weekly end-to-end proof | all 3 paths up | low | loopback lab path is correct now that lab ntfy is internal |
| Tests | `automation/validation/tests/*notif*` | offline regression | present, CI-run | low | auth/deadman/canary suites |
| Email | Wazuh manager config | email notifications | disabled by design | n/a | no first-party email |
| Mobile push | ntfy app | owner phone delivery | delegated; transit unconfirmed | low | owner confirmation item |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Notification models | 4 | relay + ntfy users/ACLs + heartbeat/watcher | no per-user preference store (single operator) | none for now |
| Email templates | N/A | email disabled by design | none | none |
| Push subscriptions | 3 | delegated to ntfy app; no first-party push | mobile-push transit unconfirmed | owner confirmation |
| VAPID/config | N/A | no web-push code | none | none |
| Reminder jobs | 4 | hourly heartbeat timer; weekly canary timer | none | none |
| Preferences | 3 | `NOTIFICATION_AND_DEADMAN.md` section 5; ntfy pause/ACL | no server-side preference store | document as accepted |
| Tenant scoping | N/A | single-tenant lab | none | none |
| Unsubscribe/opt-out | 3 | ACL deny/pause documented | none | none |
| Retries | 4 | relay retries 2x + alt path + 502->Grafana retry; backup/disk-guard retries | none | none |
| Failure handling | 4 | dual-path + spool + metrics + canary | no relay-side dedupe | add suppression window |
| Duplicate prevention | 2 | Grafana grouping only | sub-repeat flapping | NOTIF-P2-002 |
| Rate limiting | 4 | relay per-source limit; ntfy visitor limits; Traefik public limit | none | none |

## Findings

### NOTIF-P2-001 (prior, reassessed P3) - ntfy-auth Traefik middleware is still dead config

- Severity: P3, Confidence: High (repo + live mount), Status: still-open (register: partially-fixed)
- What is happening: `config/traefik/dynamic.yml:26-28` defines `ntfy-auth` (basicAuth against `/etc/traefik/secrets/ntfy_htpasswd`), but no router references it: the routers at `:51-132` use only `sec-headers`, `redirect-https`, `dash-root-redirect`, `public-rate-limit`, `falcon-basic-auth`. The lab ntfy is now internal-only (`:77-82`, `Host(ntfy.falcon.lab)`), and the only public ntfy is the DO instance. ntfy-native deny-all remains the actual control (anonymous read 403 verified live).
- Why it matters: dead security config misleads access reviews and could be re-wired by mistake; it also hides the fact that the internal router has no Traefik-layer auth (ntfy auth is the only gate).
- Recommended fix: delete the `ntfy-auth` middleware (and the mounted htpasswd if unused), or wire it on the internal `ntfy` router as defense-in-depth.
- Evidence: `config/traefik/dynamic.yml:26-28`; live Traefik mounts the repo file read-only (`docker inspect falcon-central-traefik-1`); anonymous read 403 on the lab topic; `docs/audits` prior runs.

### NOTIF-P2-002 (prior) - Notification noise remains high; the accurate disk-guard root alert now dominates

- Severity: P2, Confidence: High (48h live topic export), Status: still-open
- What is happening: the independent topic cache holds 335 messages over 48h: 206 FIRING, 81 RESOLVED, 48 heartbeats. 91 of 169 same-title FIRING gaps are below Grafana's 4h `repeat_interval`. The single largest source is `FIRING: Falcon disk guard: root still below threshold` - 47 messages in three segments (2026-10-10 10:00-13:00, 16:15-23:45, and 2026-10-11 03:45-ongoing) because the root LV free space hovers at/below the guard's 20 GiB threshold and the guard exits 1 after alerting (see SEARCH-P2-002). The relay publishes every webhook synchronously with no dedupe key or suppression window; the only grouping is Grafana `group_by [alertname]` / `group_interval 1m` / `repeat_interval 4h` (`bootstrap/90-alerting.sh:133-141`).
- Why it matters: alert fatigue for a single-operator MSP; the 47-message root alert is correct but repeated every 15 minutes, so it masks genuine transitions.
- Recommended fix: (1) fix the root capacity condition (SEARCH-P2-002) so the dominant alert stops; (2) raise `for`/thresholds on the remaining flapping feed/probe rules or add mute timings for known transient conditions; (3) optionally add a relay-side same-title suppression window for repeats inside the 4h interval; (4) record the 7-day noise measurement the decision log still calls for.
- Evidence: 48h topic export (335/206/81/48; disk-guard title 47; min gaps 361-893s); `bootstrap/90-alerting.sh:133-141`; `automation/alerting/ntfy_relay.py` (publish path, no dedupe); `disk_guard.sh:152-155`.

### NOTIF-P3-003 (new) - Retired public lab-ntfy hostname still referenced in ledgers and the 97 deploy fallback

- Severity: P3, Confidence: High (repo read), Status: open
- What is happening: the architecture moved to "lab ntfy internal-only; the only public ntfy is `ntfy.mainecybertech.us`", but stale text remains: `ledgers/exception_register.md:29` (EX-20) still states the lab ntfy "is published at falcon-ntfy.mainecybertech.us through the Cloudflare tunnel WITHOUT Cloudflare Access"; `ledgers/risk_register.md:31` (R-24 updated) still locates the self-hosted ntfy at `falcon-ntfy.mainecybertech.us`; and `bootstrap/97-cloudflare-api-config.sh:61` (the token-lacks-access fallback instructions) still tells the operator to configure `dash.falcon.mainecybertech.us` and `ntfy.falcon.mainecybertech.us` tunnel hostnames - if followed, it would re-add the retired ntfy host and drop `iris`/`enroll` (the actual v13 ingress is falcon/iris/enroll).
- Why it matters: ledgers are the review artifacts of record (EX-20 now misstates the control set), and the 97 fallback is executable guidance that contradicts the script's own `HOSTS` array - a manual tunnel repair would regress the ingress.
- Recommended fix: update EX-20/R-24 to the internal-only architecture (or close them), and rewrite the 97 fallback host list to falcon/iris/enroll.
- Evidence: `ledgers/exception_register.md:29`; `ledgers/risk_register.md:31`; `bootstrap/97-cloudflare-api-config.sh:61`; `config/traefik/dynamic.yml:83-86`; live tunnel v13.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1 + falcon-20261011-0400-verify-main-584e1a3)

- **NOTIF-P1-001 (prior P1): verified-fixed.** All legs re-verified 2026-10-11: lab ntfy internal-only (`127.0.0.1:2586`, SNI `ntfy.falcon.lab` 200); no public lab-ntfy Traefik router; no `falcon-ntfy`/`ntfy.falcon` DNS records (wildcard explains resolution; 521 = no origin); effective remote tunnel config **v13** = falcon/iris/enroll (the v12 leftover from the 0400 verification is gone); DO watcher reads locally with the current repo script and reports `ok: heartbeat age …`; owner public read verified; `do-ntfy-public` service probe = 1. Note: the register's "routers/DNS removed" is accurate; a dead Cloudflare Access app for the retired host remains (inert; noted, not a finding).
- **NOTIF-P3-001 (prior P3): verified-fixed.** The stale storm/probe test-topic grants for `falcon-relay` are revoked - live `ntfy access` shows explicit `no access` for all former test topics and write-only retained on `falcon-alerts`; the owner read and relay write are intact. Residual (cosmetic): the explicit deny entries remain in the user DB and `provision_ntfy.sh` still does not prune them.
- **NOTIF-P2-001 (prior P2 -> P3): carried forward still-open** (dead middleware still unreferenced).
- **NOTIF-P2-002 (prior P2): carried forward still-open**, with the disk-guard root alert now the dominant source (was 409 messages/361 transitions on 2026-10-09; now 335/287 with a different top offender).
- New: NOTIF-P3-003 (stale retired-hostname references).

## Limitations

- Owner phone subscriptions and mobile-push transit (Firebase/APNs) cannot be verified from the lab; the runbook records it as an owner confirmation item.
- The DO ntfy instance internals (user DB, service config) are owner-gated; verified only via public health/topic read, the watcher log/state, and the site-exporter metrics.
- No test notification was published by this audit (read-only); delivery was verified from relay metrics/journals, the canary, the heartbeat, and cached topics. (The disk-guard/backup scripts do publish during normal operation; those messages are visible in the 48h export.)
- The 48h topic window is a cache, not an archive; longer-term noise trends rely on the missing 7-day measurement.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the mobile-push transit (titles only) acceptable to the owner? | content-sensitivity confirmation | owner statement |
| Should the lab ntfy `ntfy-auth` middleware be deleted or wired? | dead-config hygiene vs defense-in-depth | owner/implementation decision |

## Suggested Tests

- Keep `ntfy_relay_auth_test.py`, `heartbeat_independence_test.sh`, `deadman_contract_test.sh`, `alert_canary_test.sh` green in CI; add a test asserting no router references a missing middleware and that every middleware is referenced (dead-config lint for `dynamic.yml`).
- Add a monthly noise measurement job (per-title counts, min-gap report) exported as metrics so the 7-day re-measure is recorded automatically.

## Suggested Documentation Updates

- `ledgers/exception_register.md` EX-20, `ledgers/risk_register.md` R-24: update to the internal-only lab ntfy + public DO instance architecture.
- `bootstrap/97-cloudflare-api-config.sh:61`: fix the fallback host list (falcon/iris/enroll).
- `docs/runbooks/NOTIFICATION_AND_DEADMAN.md`: already updated for the new architecture; add the disk-guard root alert as the top noise source and its dependency on SEARCH-P2-002.

## Findings

| ID | Severity | Title |
|---|---|---|
| NOTIF-P2-001 | P3 | ntfy-auth Traefik middleware is still dead config; ntfy-native deny-all remains the only access control |
| NOTIF-P2-002 | P2 | Notification noise remains high; the accurate disk-guard root alert now dominates and sub-repeat-interval flapping persists |
| NOTIF-P3-003 | P3 | Retired public lab-ntfy hostname still referenced in ledgers and the 97 deploy fallback text |
