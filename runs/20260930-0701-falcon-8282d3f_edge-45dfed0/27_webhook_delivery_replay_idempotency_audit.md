# Webhook Delivery, Replay, and Idempotency Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: WH
- Status: N/A — no first-party webhook product surface; alert delivery is covered by prompt 30
- Scope limitations: read-only; no webhook was sent or replayed

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Inbound/outbound webhook APIs | `grep -nE '^  /' falcon-edge-build/api/openapi/falcon-edge-v1.yaml` | 16 sensor-lifecycle paths; no webhook subscription/callback/management endpoints |
| Webhook-shaped code | `grep -rIn -i 'webhook' <code dirs>` | Only the internal alert relay: `automation/alerting/ntfy_relay.py` + `config/systemd/falcon-alert-relay.service`; Grafana contact point type `webhook`; evidence captures |
| Relay auth/transport | `sed -n '1,50p' automation/alerting/ntfy_relay.py` | Receives Grafana's fixed webhook JSON on Docker bridge addresses (port 9099); path token from `/srv/falcon/secrets/ntfy_relay.token`; renders and publishes to ntfy (primary + alternate target) |
| Relay exercise evidence | `evidence/raw/P9-G02/20260928T153847Z_post-outage-verification-20260928.out` | `PASS alert relay accepts webhooks (200)`, `PASS self-hosted ntfy health` |
| MCT pipeline webhooks | `automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf:341` | Comment: "Zeek Class A (SSH/SMB/RDP) -> Shuffle webhook -> IRIS" — separate MCT stack, not the falcon-lab control plane |
| Signature/replay/idempotency code | `grep -rIln -i -E 'hmac\|nonce\|idempotency' <code dirs>` | No first-party webhook signature, nonce, retry-backoff or DLQ implementation |

## Evidence Reviewed

- `/home/user/falcon-build/automation/alerting/ntfy_relay.py` — the only webhook receiver in the repo (alert transport)
- `/home/user/falcon-build/config/systemd/falcon-alert-relay.service` — relay unit, alternate ntfy target, hardening flags
- `/home/user/falcon-build/evidence/raw/P9-G02/20260928T153847Z_post-outage-verification-20260928.out` — live relay acceptance check
- `/home/user/falcon-edge-build/api/openapi/falcon-edge-v1.yaml` — control-plane contract without webhook endpoints
- `/home/user/falcon-build/automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf` — MCT Shuffle→IRIS webhook reference (separate stack)

## Not Applicable / Future Readiness

**Why N/A.** The audited system exposes no webhook product features: no subscriptions, no signed events, no retries, no DLQ, no admin management, no tenant scoping — the edge control plane's API is sensor lifecycle only. The single webhook-shaped flow is the Grafana alert contact point POSTing to the local `falcon-alert-relay`, which is part of the alert-notification channel and is deliberately audited under prompt 30 (notification delivery). Domain score: **0 (not assessable)**.

**Boundary note for prompt 30 (not a WH finding here).** The relay authenticates with a static path token and has no HMAC signature, timestamp tolerance, nonce cache or idempotency key; Grafana retries or duplicate POSTs would simply re-publish a notification. As fire-and-forget alerting this is tolerable, but 30/ADV should record the relay's replay and duplicate-notification behavior explicitly. A second path publishes to an alternate ntfy target (`MON_RELAY_ALT_URL`) for failure-domain independence.

**Future readiness trigger.** This prompt becomes applicable if webhooks become a product feature — e.g. customer-facing event notifications, or the MCT Shuffle→IRIS integration moving into the audited scope. Minimum controls then: HMAC signatures with timestamp tolerance, replay/nonce protection or idempotency keys, retry with backoff, a dead-letter queue, delivery logs visible to operators, secret rotation and size/schema limits.

**Findings:** none — no applicable first-party surface.
