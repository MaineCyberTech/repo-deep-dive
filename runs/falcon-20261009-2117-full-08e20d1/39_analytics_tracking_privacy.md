# 39_analytics_tracking_privacy — Prompt 39 - Analytics, Tracking, and Privacy Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `39_analytics_tracking_privacy.md` (area AN, prompt)

## Verification Performed

# Analytics, Tracking, and Privacy Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d` (short `08e20d1`)
- Branch: `main` (target pinned at 08e20d1; the clone's `main` ref now points at `6e4fccd` and `ops/20261009-snapshot-repo-relocate-clean` at `c13a416` — both used only as post-audit context, never as the audited tree)
- Generated at: 2026-10-09T21:50:40Z · Auditor: repo-deep-dive subagent (prompt 39) · Area code: AN
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/39_analytics_tracking_privacy.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo password read from the owner file in a subshell, never printed); no state mutated; no formal compliance claimed — SOC2/ISO27001/NIST/CIS/OWASP/GDPR/CCPA/HIPAA/PCI/CMMC are used as readiness lenses only. Edge-repository surfaces (sensor images, edge delivery directory, edge SQLite store) are outside this repository and are referenced through owner-action C13. This is an evidenced N/A report: the repository has no analytics/tracking surface. It is written as a future-readiness statement per the prompt.


## Scope

Reviewed at `08e20d1`: analytics scripts, tracking pixels, events, product analytics, error telemetry, session replay, cookie banner, consent, opt-in/out, user/tenant identifiers, sensitive payloads, page views, admin tracking, marketing lead tracking, policies, retention, vendor list, do-not-track, tests/docs. The falcon repository is a self-hosted network-monitoring stack (Suricata/Vector/OpenSearch/Prometheus/Grafana/Wazuh/ntfy) with no first-party web product; the only browser surfaces are authenticated operator tools (Grafana, OpenSearch Dashboards, ntopng, ntfy).

Not reviewed: the tool vendors' own internal telemetry implementations beyond the configuration evidence below; the edge repository.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Repo-wide grep for analytics/tracking vendors (`google-analytics`, `gtag`, `matomo`, `plausible`, `posthog`, `hotjar`, `fullstory`, `clarity.ms`, `session replay`, `sentry`, `datadog`, `newrelic`, `segment`, `mixpanel`, `amplitude`, `facebook pixel`, `tracking pixel`, `cookie banner`, `do-not-track`) | inspect | Any first-party or injected tracker | **No hits** (excluding `mct/`, `docs/audits/`, `sbom/`) |
| `compose/central/docker-compose.yml:203-204` | config | Grafana analytics | `GF_ANALYTICS_REPORTING_ENABLED: "false"`, `GF_ANALYTICS_CHECK_FOR_UPDATES: "false"` |
| Live `docker exec falcon-central-grafana-1 env` | live read-only | Runtime state | Same two values `false`; sign-up/anonymous disabled |
| Live `curl _nodes/plugins` on `falcon-central-opensearch-1` | live read-only | OpenSearch telemetry plugin | No `telemetry` plugin present (`grep` no match) |
| Live `opensearch_dashboards.yml` (container) | live read-only | OSD search-usage telemetry | `data.search.usageTelemetry.enabled` only appears commented (`:181-183`); vendor documentation states search telemetry is off by default |
| `docs/privacy/DATA_GOVERNANCE.md:16,44` | doc | Vendor list / egress | ntfy push service sees titles only; "no third-party analytics; the only outbound paths are the documented processors" |
| `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:10-20` | doc | Data classes | No page-view/analytics class exists |
| `README.md:91-93` | doc | Public surfaces | Grafana/`/dash`/`/ntop` + ntfy — all authenticated tool UIs, no marketing site |
| `find . -name '*.html' -o -name '*.js'` (first-party) | inspect | First-party web content | Only audit-run dashboards; no application HTML/JS |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Vendor-name grep (see above) | reproduce | Third-party scripts/pixels | Zero matches in first-party trees |
| Grafana live env read | live read-only | Product analytics off | Confirmed `false` at runtime |
| OpenSearch plugin list | live read-only | Usage telemetry | No telemetry plugin installed |
| OSD config + vendor doc | inspect/reference | Search-usage telemetry | Default off; shipped file leaves the setting commented |
| Public-surface check (`curl` 302 to login) | live read-only | No anonymous content that could carry a tracker | `https://falcon.mainecybertech.us/` and `/dash` → 302 |
| `Set-Cookie`/`document.cookie` grep in first-party code | inspect | Cookie setting | No first-party code sets cookies |
| Existing privacy docs | inspect | Consent/notice | Consent flows N/A (no first-party collection surface) |

## Executive Summary

There is **no analytics, tracking, advertising, session-replay, or product-telemetry surface in this repository**, and the operator tools that could phone home are configured off: Grafana analytics/update checks are disabled in Compose and at runtime, the OpenSearch distribution in use has no telemetry plugin, and OpenSearch Dashboards' search-usage telemetry is off by default. The only outbound data paths are the documented processors (DigitalOcean ntfy/dead-man, Cloudflare, GitHub, Spaces backup, ntfy push service) recorded in `docs/privacy/DATA_GOVERNANCE.md`. Error telemetry is internal only (Prometheus/Grafana/ntfy and the security feeds), and identifiers in the security telemetry are pseudonymous site/sensor labels. This domain is therefore **N/A at this commit**; the report records the future-readiness requirements should a first-party portal or marketing surface ever be added (consent gate before any script, event-payload minimization, vendor inventory, retention, and a test that fails on un-consented third-party calls). No findings are raised because no analytics exists and no policy gap is actionable today.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Analytics scripts | — | — | **Absent** | None | Zero vendor matches |
| Tracking pixels | — | — | **Absent** | None | No first-party web content |
| Product analytics | — | — | **Absent** | None | Grafana analytics disabled |
| Error telemetry | Prometheus/Grafana/ntfy; Wazuh/Suricata feeds | Platform/security health | Internal only | Low | No external error SaaS |
| Session replay | — | — | **Absent** | None | — |
| Cookie banner | — | — | **N/A** | None | No first-party collection; tool session cookies only |
| Consent / opt-in-out | — | — | **N/A** | None | Revisit on portal |
| User/tenant IDs | `site_id`, `sensor_id` in EVE events | Telemetry labeling | Pseudonymous labels | Low | Owner-device identifiers governed by PRIV |
| Sensitive payloads | `DATA_FLOW_AND_CLASSIFICATION.md:24` | Payload prohibition | Full packet payloads prohibited (OD-13) | Low | Credential redaction at ingest |
| Page views / admin tracking | OpenSearch audit log (`security-auditlog-*`, 30 d) | Admin action traceability | Enabled | Low | Governance, not analytics |
| Marketing lead tracking | `mct/client-onboarding/*` | Sales kit files | Templates only; no tracker | Low | PRIV boundary tracked separately |
| Vendor list | `DATA_GOVERNANCE.md:10-19` | Processors | Documented (no analytics vendors) | Low | — |
| Do-not-track | — | — | N/A | None | No client-side collection |
| Tests/docs | `ci/validate.py` | Secret scan etc. | PASS | Low | Add an analytics guard if a web surface is added |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Analytics scripts | 5 (N/A) | Vendor grep zero | — | None |
| Tracking pixels | 5 (N/A) | No first-party web content | — | None |
| Events | 4 | Internal security events; no product events | No product-event policy (N/A) | None |
| Product analytics | 5 (N/A) | Grafana analytics off (live) | — | Keep |
| Error telemetry | 4 | Internal Prometheus/ntfy | No external error telemetry (by design) | Keep |
| Session replay | 5 (N/A) | Absent | — | None |
| Cookie banner | N/A | No first-party collection | — | Revisit on portal |
| Consent | N/A | No collection | — | Revisit on portal |
| Opt-in/out | N/A | No collection | — | Revisit on portal |
| User/tenant IDs | 4 | site/sensor labels; PRIV governs device IDs | — | Keep pseudonymous |
| Sensitive payloads | 4 | Payload prohibition + redaction | — | Keep |
| Page views | N/A | No web product | — | Revisit on portal |

## Detailed Review

### Item: Third-party scripts and pixels

- Evidence: repo-wide vendor grep (zero hits); no first-party `.html`/`.js`; public surfaces are authenticated tool UIs (`README.md:91-93`).
- Assessment: nothing to consent to; no tracker can be injected by repository code. The only browser surfaces are Grafana/Dashboards/ntopng/ntfy, whose own vendor telemetry is disabled/absent as verified.

### Item: Tool telemetry (Grafana / OpenSearch / Dashboards)

- Evidence: `compose/central/docker-compose.yml:203-204`; live Grafana env (`false`); live OpenSearch plugins (no telemetry plugin); OSD config comments (`:181-183`) + vendor documentation (search telemetry off by default).
- Assessment: outbound tool telemetry is off by configuration; no analytics egress.

### Item: Identifiers and sensitive payloads in telemetry

- Evidence: `docs/privacy/DATA_GOVERNANCE.md:23-32`; `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:24` (payload prohibition).
- Assessment: identifiers are pseudonymous site/sensor labels; owner-device telemetry is governed under PRIV (owner/legal inputs outstanding). No product analytics identifiers exist.

### Item: Future readiness (if a portal/marketing surface is added)

- Required before any analytics: consent gate before script load; vendor inventory + DPA; event-payload minimization (no PII in event names/properties); retention for analytics data; do-not-track/GPC handling; a CI guard/test that fails on un-approved third-party calls; a policy document (proposed `docs/privacy/ANALYTICS_POLICY.md`).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| AN-001 | Analytics scripts | Vendor grep zero | Absent | — | — | None |
| AN-002 | Tracking pixels | No first-party web content | Absent | — | — | None |
| AN-003 | Events | Internal security events only | Documented classes | — | — | None |
| AN-004 | Product analytics | Grafana `GF_ANALYTICS_*` false (live) | Disabled | — | — | Keep |
| AN-005 | Error telemetry | Prometheus/ntfy internal | Internal only | — | — | Keep |
| AN-006 | Session replay | Absent | — | — | — | None |
| AN-007 | Cookie banner | No first-party collection | N/A | — | — | Revisit on portal |
| AN-008 | Consent | N/A | N/A | — | — | Revisit on portal |
| AN-009 | Opt-in/out | N/A | N/A | — | — | Revisit on portal |
| AN-010 | User/tenant IDs | site/sensor labels | Pseudonymous | — | — | Keep |
| AN-011 | Sensitive payloads | Payload prohibition; redaction | Enforced | — | — | Keep |
| AN-012 | Page views | No web product | N/A | — | — | Revisit on portal |

## Findings

_No findings._ No analytics, tracking, or consent-triggering surface exists at this commit; the tool telemetry that could egress is disabled or absent, verified in configuration and at runtime.

## Prior-Run Comparison

- Prior full run `falcon-20261005-full-main-e267ce1`: same-domain report "No third-party analytics/tracking is present. No finding." (0 findings).
- 20260930 run: no AN findings either. This run re-verified the conclusion at `08e20d1` and added live checks (Grafana env, OpenSearch plugin list, OSD config, public 302s).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Future portal adds un-consented analytics | P3 (future) | Low | Privacy | No policy exists | Adopt the future-readiness checklist before launch |

## Recommendations

### Immediate / Release Blocking

None.

### This Week / This Month

None.

### Later / Platform Evolution

1. If a first-party portal or marketing surface is added: write `docs/privacy/ANALYTICS_POLICY.md`, require a consent gate, minimize event payloads, inventory vendors, and add a CI guard.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Record this N/A verdict in the governance doc | Prevents re-discovery each audit | `docs/privacy/DATA_GOVERNANCE.md` (one line) | Doc states "no analytics" |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Analytics/consent policy (only if a portal is planned) | P3 | maintainer | S | Product decision |

## Suggested Tests

- CI grep guard: fail on known tracker domains/scripts appearing in first-party trees (cheap, prevents accidental injection).
- If a portal is added: an E2E test asserting no third-party request before consent.

## Suggested Documentation Updates

- `docs/privacy/DATA_GOVERNANCE.md` — one line stating analytics N/A + the future checklist pointer.
- If a portal is added: `docs/privacy/ANALYTICS_POLICY.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is a client portal or marketing site planned? | Would activate consent/tracking requirements | Owner roadmap |

## Limitations / Appendix

- Vendor documentation was used to confirm the OpenSearch Dashboards search-telemetry default (off); the shipped config leaves the setting commented, and no search-usage index exists on the cluster (read-only `_cat/indices` check showed none).
- The grep excluded `mct/` (vendored, archive-only; no trackers found there either in the broader scan), `docs/audits/` (historical reports) and `sbom/` (generated data).

## Findings

_No findings in this domain._
