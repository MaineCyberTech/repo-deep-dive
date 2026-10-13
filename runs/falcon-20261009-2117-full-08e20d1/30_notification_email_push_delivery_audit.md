# 30_notification_email_push_delivery_audit — Prompt 30 - Notification, Email, and Push Delivery Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `30_notification_email_push_delivery_audit.md` (area NOTIF, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon
- Branch: main (origin/main)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:42:16Z
- Auditor: repo-deep-dive full-domain subagent (read-only, no mutation)
- Area code: NOTIF
- Live vantage: this audit ran on the live lab host. The live tree `/home/user/falcon-build` is at `6e4fccd` (local `main`, 2026-10-09 ops commit); the NOTIF-relevant files are byte-identical between `6e4fccd` and `08e20d1` (e.g. `automation/alerting/ntfy_relay.py` sha256 `01ec4e75be8b...` matches both), so the live observations bind to the audited commit for this domain. `08e20d1` is `origin/main`; local `main` is a rebased ops lineage with no diff in any file in this domain's scope.

## Scope

Reviewed: the Grafana -> relay -> ntfy delivery path (`automation/alerting/ntfy_relay.py`, `config/systemd/falcon-alert-relay.service`, `bootstrap/90-alerting.sh` contact point/rules/notification policy), self-hosted ntfy configuration and ACLs (`config/ntfy/server.yml`, `automation/alerting/provision_ntfy.sh`), the dead-man heartbeat and independent watcher (`automation/validation/heartbeat.sh`, `automation/alerting/do_watcher/`, `falcon-heartbeat.timer`), public access to the ntfy topic (`config/traefik/dynamic.yml`, `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh`, live cloudflared config), delivery verification (`automation/validation/alert_canary.sh`, live textfile metrics, `post_reboot_verify.sh`), noise/dedupe, preference/opt-out, and tests (`automation/validation/tests/ntfy_relay_auth_test.py`, `heartbeat_independence_test.sh`, `alert_canary_test.sh`, `deadman_contract_test.sh`).

Not reviewed: owner-side DO host internals (watcher state file `/var/lib/falcon-watcher/state`, crontab, DO ntfy source/config) - the DO instance is owner-gated and not in the repo; email delivery (Wazuh `ossec.conf` has email intentionally disabled and there is no first-party email sender); web-push/VAPID (the ntfy mobile app uses its own push service; no first-party push subscription code exists). No test send was performed: publishing is state-mutating (owner-visible) and this audit is read-only; delivery was verified from the relay's own metrics, journals, and the cached topics instead.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `automation/alerting/ntfy_relay.py` | code | fail-closed token auth, per-source rate limit, per-path metrics, 502+spool on total failure, dual-path publish | live process runs the same bytes (sha256 match) |
| `config/systemd/falcon-alert-relay.service` | unit | relay runs on 10 docker bridge gateways, ALT_URL set | live unit matches repo file |
| `bootstrap/90-alerting.sh` | provisioning | contact point `falcon-ntfy`, notification policy (group_by alertname, group_wait 10s, group_interval 1m, repeat_interval 4h), 60+ rules | rules live-provisioned |
| `config/ntfy/server.yml` | config | deny-all native auth, 48h cache, rate limits, base-url | live container config identical |
| `automation/alerting/provision_ntfy.sh` | provisioning | idempotent users/ACLs (monadmin, falcon-relay wo, owner rw, watcher ro) | live users match; extra test-topic ACLs found |
| `automation/validation/heartbeat.sh` + `config/systemd/falcon-heartbeat.timer` | dead-man | hourly heartbeat to both instances, independent of the relay | live publishes 200/200 hourly |
| `automation/alerting/do_watcher/watch.sh` | dead-man | independent watcher reads the lab public topic; 2h threshold | read path currently 404 |
| `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh`, `config/traefik/dynamic.yml` | public access | declared tunnel ingress / Traefik routers / hostname | hostname mismatch (finding) |
| `automation/validation/alert_canary.sh`, `post_reboot_verify.sh` | verification | weekly canary all paths; post-reboot owner-read check | canary passes on loopback; post-reboot check would fail |
| live: cloudflared config + journal, `docker exec ntfy user list/access`, `/srv/falcon/textfile/falcon_relay.prom`, `falcon_alert_canary.prom`, relay journal, DO topic 48h JSON | live | current delivery, ACLs, public reachability, noise | read-only; secrets never printed |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Relay health on bridge gateways | `curl http://172.30.1.1:9099/` and `172.30.2.1:9099/` | 200 / 200 |
| Relay rejects an unauthenticated POST | `curl -X POST http://172.30.1.1:9099/grafana/wrong-token -d '{}'` | 404 (fail-closed) |
| Relay delivery accounting | `/srv/falcon/textfile/falcon_relay.prom` | lab 468 ok/0 fail, alt 467 ok/1 fail, last success 2026-10-09T21:12Z |
| ntfy anonymous read | `curl https://<origin>/falcon-alerts/json?poll=1` (via Traefik SNI) | 403 (deny-all enforced) |
| ntfy health (origin) | `curl --resolve falcon-ntfy...:443:127.0.0.1 .../v1/health` | 200 |
| Public lab ntfy hostname (documented) | `curl https://falcon-ntfy.mainecybertech.us/v1/health` and the topic read with valid `watcher` credentials | 404 (Cloudflare/tunnel) |
| Public lab ntfy hostname (tunnel-declared) | `curl https://ntfy.falcon.mainecybertech.us` | TLS handshake failure (edge certificate) |
| Live tunnel ingress | `cat /etc/cloudflared/config.yml`; `journalctl -u cloudflared` remote config v12 | `ntfy.falcon.mainecybertech.us` only; `falcon-ntfy` absent |
| ntfy users/ACLs | `docker exec falcon-central-ntfy-1 ntfy user list` / `ntfy access` | 4 production users/ACLs as designed + stale test-topic ACLs |
| Heartbeat end-to-end | `journalctl -u falcon-heartbeat` + DO topic 48h | `heartbeat_publish=200`, `heartbeat_publish_independent=200`, hourly messages present on both instances |
| Canary | `/srv/falcon/textfile/falcon_alert_canary.prom` | all three paths up (last success 2026-10-05T06:00Z) - loopback, so it cannot see the public break |
| Noise quantification | DO topic 48h JSON (409 messages) | 361 FIRING/RESOLVED transitions; per-title repeat gaps below the 4h repeat_interval |
| Dead-man alerts on the alt topic | DO topic 48h filter `dead|heartbeat` | no dead-man messages in cache (heartbeats only); watcher state owner-side, not verifiable from the lab |

## Executive Summary

The notification pipeline itself is well built and currently delivering: the relay is fail-closed, rate-limited, dual-path with per-path metrics, the ntfy server enforces deny-all native auth with least-privilege ACLs, the heartbeat publishes hourly to both failure domains, and the weekly canary proves the loopback/relay/alt paths. Two real gaps remain. First (P1): the *public* lab ntfy hostname is broken end-to-end - the repo docs/consumers use `falcon-ntfy.mainecybertech.us` (404 at Cloudflare) while the deploy scripts and live tunnel declare `ntfy.falcon.mainecybertech.us` (TLS handshake failure at the edge, no Traefik router); the origin is healthy, but no public hostname serves it, so owner devices on the documented URL get nothing and the independent dead-man watcher's heartbeat read cannot work. The canary cannot see this because it publishes to the loopback URL. Second (P2): owner-facing noise is high (~8 messages/hour baseline; 361 FIRING/RESOLVED transitions in 48h; several rules re-fire within 6-31 minutes against a 4h repeat interval) with no relay-side dedupe/suppression. The prior NOTIF-P2-001 (public router origin auth) is reassessed: ntfy-native deny-all is the working control, the route is currently unreachable, and the unwired `ntfy-auth` middleware is a P3 config-hygiene item.

## Findings

### NOTIF-P1-001 - Public lab ntfy endpoint is dead: tunnel ingress and repo docs disagree on the hostname

- Severity: P1, Confidence: High (live-verified both hostnames and the origin), Effort: S-M
- What is happening: the documented public hostname `falcon-ntfy.mainecybertech.us` returns Cloudflare 404; the tunnel-declared `ntfy.falcon.mainecybertech.us` fails the edge TLS handshake and has no Traefik router. The origin (Traefik+ntfy) answers correctly for the documented SNI.
- Why it matters: the owner-facing public read path and the independent watcher's heartbeat read are broken while monitoring reports healthy (loopback canary).
- Recommended fix: pick one canonical hostname and wire it end-to-end (bootstrap 96/97 + tunnel ingress/DNS + cert), then verify owner read and watcher read and add a public read check to the canary.
- Owner suggestion: @owner. Status: open. Validation: public `GET /v1/health` 200 and authenticated topic read 200 from an external vantage; watcher log shows `ok: heartbeat age`.

### NOTIF-P2-001 (prior) - ntfy-auth middleware is still dead config; ntfy-native deny-all is the actual control

- Severity: P3 (reassessed from P2), Confidence: High, Status: partially-fixed
- What is happening: the `ntfy-auth` basicAuth middleware is defined with a real, mounted htpasswd file but referenced by no router; ntfy itself enforces deny-all (anonymous read 403) and the public route is currently 404.
- Why it matters: defense-in-depth is absent at the Traefik layer and the dead definition misleads access reviews; the anonymous-access risk the prior finding described is not present today.
- Recommended fix: wire `ntfy-auth` on the public ntfy router (if the route is restored) or delete the dead middleware; keep the ntfy-native auth as the primary control.
- Owner suggestion: @owner. Validation: router list shows the middleware; anonymous 401/403 at Traefik before ntfy.

### NOTIF-P2-002 (new) - Notification noise remains high with sub-repeat-interval flapping

- Severity: P2, Confidence: High (48h live topic export), Effort: M
- What is happening: 409 messages/48h on the owner topic; 361 FIRING/RESOLVED transitions; several rules repeat within 6-31 min while Grafana's repeat_interval is 4h; the relay has no dedupe/suppression.
- Why it matters: alert fatigue for a single-operator MSP; genuine transitions are harder to spot in the flood.
- Recommended fix: raise `for` on the flapping feed/probe rules, add mute timings for maintenance, or add a relay-side same-title suppression window; record the 7-day noise measurement (the 2026-10-07 re-measure named in the decision log is not in the repo).
- Owner suggestion: @owner. Validation: 7-day per-title counts and min-gap report; target < 25% of current transitions.

### NOTIF-P3-001 (new) - Stale ntfy test-topic ACLs remain in the live user DB

- Severity: P3, Confidence: High, Effort: S
- What is happening: `ntfy user list`/`ntfy access` show ~11 leftover test topics granted to `falcon-relay` (`falconstorm*`, `probe*`, `cap*`, `relayprobe*`, `manualburst*` - the last denied) from the NOTIF-P3-001 storm/probe tests; `provision_ntfy.sh` manages only the four production users/ACLs and does not prune them.
- Why it matters: access reviews and rebuilds inherit test residue; a rebuild from `provision_ntfy.sh` would not reproduce the live ACL set exactly.
- Recommended fix: `ntfy access falcon-relay <topic> deny` for the stale topics, and add a prune/review note to the runbook.
- Owner suggestion: @owner. Validation: `ntfy user list` shows only the four production entries plus `*`.

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

- Prior `NOTIF-P2-001` (public ntfy routers lack origin authentication; `ntfy-auth` not wired; status still-open): reassessed against live evidence - ntfy-native deny-all is live and enforced (anonymous 403), the public route is currently 404, and the middleware remains dead config. Carried forward with the same ID at P3 (partially-fixed) rather than re-asserting P2.
- Prior run had no other NOTIF findings. New findings this run: the broken public hostname (P1, live-verified), noise quantification (P2), stale test-topic ACLs (P3).
- The prior run's report body for this domain was empty (machine-only); this run adds the live verification record above.

## Limitations

- Owner-side DO watcher state (its `alerted`/`ok` file and installed script revision) cannot be read from the lab; the impact analysis of the broken heartbeat read is therefore "cannot work as designed; current alert state unknown".
- No test notification was published (read-only audit); delivery was verified from relay metrics/journals and cached topics.
- The DO ntfy instance source/config is owner-gated and not in the repo (NOTIF-P1-001 residual in the runbook); its health was verified via `https://ntfy.mainecybertech.us/v1/health` (200) only.
- Mobile push transit (Firebase/APNs) remains an owner confirmation item (documented residual), not repo-verifiable.

## Findings

| ID | Severity | Title |
|---|---|---|
| NOTIF-P1-001 | P1 | Public lab ntfy endpoint is dead: tunnel ingress and repo docs disagree on the hostname; watcher heartbeat read and owner public subscriptions cannot work |
| NOTIF-P2-001 | P3 | ntfy-auth middleware is still dead config; ntfy-native deny-all is the actual control |
| NOTIF-P2-002 | P2 | Notification noise remains high: 409 messages/48h, 361 FIRING/RESOLVED transitions, and sub-repeat-interval flapping on several rules |
| NOTIF-P3-001 | P3 | Stale ntfy test-topic ACLs remain in the live user DB from the storm/probe tests |
