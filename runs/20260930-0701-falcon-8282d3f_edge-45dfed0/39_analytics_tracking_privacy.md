# Analytics, Tracking, and Privacy Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: AN
- Status: N/A — no analytics or tracking of any kind; monitoring-data privacy is covered by prompt 18
- Scope limitations: read-only; no network capture of browser traffic was performed

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Analytics/tracking scripts | `grep -rIln -i -E 'gtag\|google-analytics\|plausible\|matomo\|posthog\|mixpanel\|hotjar\|cookie consent\|consent banner' <code dirs>` | 0 real hits; false positives only — `%syslogtag%` contains "gtag" in `config/rsyslog/49-falcon-tls.conf`, "plausible" in a test comment (`tests/phase8/test_observability.py:83`) |
| Web assets (pixels, replay, cookies) | `find <both repos> -type f \( -name '*.html' -o -name '*.js' … \) \| wc -l` | `0` — no pages, scripts, pixels, cookie banner or session-replay code |
| Grafana telemetry to vendor | `grep -n 'GF_ANALYTICS' compose/central/docker-compose.yml` | `GF_ANALYTICS_REPORTING_ENABLED: "false"` (line 184), `GF_ANALYTICS_CHECK_FOR_UPDATES: "false"` (line 185) |
| Error telemetry SDKs | `grep -rIln -i -E 'sentry\|datadog\|bugsnag\|rollbar' <code dirs>` | 0 first-party hits (Sentry strings appear only inside the generated Suricata ruleset as detection content) |
| Operational telemetry (not analytics) | `grep -nE '^  [a-z0-9_-]+:' compose/central/docker-compose.yml` | prometheus, vector-aggregator, grafana, opensearch-dashboards, node-exporter — host/service monitoring for the lab itself |
| Notification channel | `config/ntfy/server.yml`; `automation/alerting/ntfy_relay.py` | Alert notifications only (topic stored as a secret); no behavioral event capture |

## Evidence Reviewed

- `/home/user/falcon-build/compose/central/docker-compose.yml` — Grafana analytics/update telemetry explicitly disabled (lines 184–185)
- `/home/user/falcon-build/config/ntfy/server.yml` — notification channel configuration, no tracking
- `/home/user/falcon-edge-build/tests/phase8/test_observability.py` — the only "analytics" greps are unrelated words in comments
- `/home/user/falcon-build/docs/runbooks/CAPACITY_AND_TELEMETRY.md` — telemetry is operational capacity metric export, not product analytics
- `/home/user/falcon-build/docs/runbooks/ACCESS_AND_ACCOUNTS.md` — human access surfaces; no analytics accounts/vendors

## Not Applicable / Future Readiness

**Why N/A.** There is no product surface to instrument: no first-party web app, no marketing site, no cookies, no consent banner, no analytics/tracking scripts, no session replay and no page-view or user-event capture. Vendor analytics are explicitly disabled where a vendor (Grafana) would have them on by default. All telemetry in the stack is operational monitoring of the lab itself — Prometheus scrape targets, Vector pipeline metrics, OpenSearch indices — which is in scope for prompts 14 (observability) and 18 (privacy/data governance), not product analytics. Domain score: **0 (not assessable)**.

**Adjacent privacy matters.** (1) Alert notifications travel through ntfy; the topic name is treated as a secret (`/srv/falcon/secrets/ntfy_topic`), and payloads are operational alert text. (2) Monitoring data (syslog, flows, TLS metadata) can contain personal data — retention, redaction and governance belong to prompt 18. (3) The MCT client layer includes `scan_authorized` / `deception_authorized` gates, which are authorization controls rather than analytics.

**Future readiness trigger.** If a first-party website, operator console or MCT client portal is published, this prompt becomes applicable: cookie/consent policy, event taxonomy with PII minimization, opt-out/do-not-track handling, vendor inventory, retention, and tests proving that third-party scripts honor consent. Until then no analytics or tracking exists.

**Findings:** none — no applicable first-party surface.
