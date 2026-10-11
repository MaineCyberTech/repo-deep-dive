# 39_analytics_tracking_privacy — Prompt 39 - Analytics, Tracking, and Privacy Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `39_analytics_tracking_privacy.md` (area AN, prompt)

## Verification Performed

# Analytics, Tracking, and Privacy Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (short `f5cb7c9`)
- Branch: `main` · Generated at: 2026-10-11T04:33Z · Auditor: repo-deep-dive subagent (prompt 39) · Area code: AN
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/39_analytics_tracking_privacy.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo value read from the owner file in a subshell, never printed); no state mutated. This is an evidenced N/A report: the repository has no analytics/tracking surface. It is written as a future-readiness statement per the prompt.

## Scope

Reviewed at `f5cb7c9`: analytics scripts, tracking pixels, events, product analytics, error telemetry, session replay, cookie banner, consent, opt-in/out, user/tenant identifiers, sensitive payloads, page views, admin tracking, marketing lead tracking, policies, retention, vendor list, do-not-track, tests/docs. The falcon repository is a self-hosted network-monitoring stack (Suricata/Vector/OpenSearch/Prometheus/Grafana/Wazuh/ntfy) with no first-party web product; the only browser surfaces are authenticated operator tools (Grafana, OpenSearch Dashboards, ntopng, ntfy, IRIS).

Not reviewed: the tool vendors' own internal telemetry implementations beyond the configuration evidence below; the edge repository.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Repo-wide grep for analytics/tracking vendors (`google-analytics`, `gtag`, `matomo`, `plausible`, `posthog`, `hotjar`, `fullstory`, `clarity.ms`, `session replay`, `sentry`, `datadog`, `newrelic`, `segment`, `mixpanel`, `amplitude`, `facebook pixel`, `tracking pixel`, `cookie banner`, `do-not-track`, `gpc`) over `*.yml/*.yaml/*.sh/*.py/*.json/*.md` | inspect | Any first-party or injected tracker | **No hits** (excluding `mct/`, `docs/audits/`, `sbom/`, `review-package/`) |
| `compose/central/docker-compose.yml:205-206` | config | Grafana analytics | `GF_ANALYTICS_REPORTING_ENABLED: "false"`, `GF_ANALYTICS_CHECK_FOR_UPDATES: "false"` |
| Live `docker exec falcon-central-grafana-1 env` | live read-only | Runtime state | Same two values `false`; anonymous auth disabled |
| Live `docker exec falcon-central-opensearch-1 ls /usr/share/opensearch/plugins/` | live read-only | OpenSearch telemetry plugin | No `opensearch-telemetry` plugin installed (27 plugins listed) |
| Live `docker exec falcon-central-opensearch-dashboards-1 grep usageTelemetry` | live read-only | OSD search-usage telemetry | `# data.search.usageTelemetry.enabled: false` — commented (vendor default off); no search-usage index exists |
| `docs/privacy/DATA_GOVERNANCE.md:17,44` | doc | Vendor list / egress | "no cloud analytics configured" (UniFi); "no third-party analytics; the only outbound paths are the documented processors" |
| `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:10-29` | doc | Data classes | No page-view/analytics class exists |
| `README.md:91-93` | doc | Public surfaces | Grafana/`/dash`/`/ntop` + ntfy — authenticated tool UIs, no marketing site |
| First-party HTML/JS scan | inspect | First-party web content | No application HTML/JS; only generated audit-run dashboards |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Vendor-name grep (see above) | reproduce | Third-party scripts/pixels | Zero matches in first-party trees |
| Live Grafana env read | live read-only | Product analytics off | Confirmed `false` at runtime (2026-10-11) |
| Live OpenSearch plugin list | live read-only | Usage telemetry | No telemetry plugin installed |
| OSD config + vendor default | inspect/reference | Search-usage telemetry | Setting commented at line 183 of the in-container config; vendor default off; no search-usage index on the cluster |
| Public-surface check (`curl` 302s) | live read-only | No anonymous content that could carry a tracker | `https://falcon.mainecybertech.us/` → 302 to Cloudflare Access; `iris.mainecybertech.us` → 302 to IRIS login (owner-IP bypass) |
| `Set-Cookie`/first-party code scan | inspect | Cookie setting | No first-party code sets cookies |
| Existing privacy docs | inspect | Consent/notice | Consent flows N/A (no first-party collection surface) |
| `python3 ci/validate.py` | reproduce | Secret scan etc. | `validation_failures=0` |

## Executive Summary

There is **no analytics, tracking, advertising, session-replay, or product-telemetry surface in this repository**, and the operator tools that could phone home are configured off: Grafana analytics/update checks are disabled in Compose and verified `false` at runtime, the OpenSearch distribution in use has no telemetry plugin installed, and OpenSearch Dashboards' search-usage telemetry is off by default (the shipped setting is commented out). The only outbound data paths are the documented processors (DigitalOcean ntfy/dead-man, Cloudflare, GitHub, Spaces backup, ntfy push service) recorded in `docs/privacy/DATA_GOVERNANCE.md`. Error telemetry is internal only (Prometheus/Grafana/ntfy and the security feeds), and identifiers in the security telemetry are pseudonymous site/sensor labels. This domain is therefore **N/A at this commit**; the report records the future-readiness requirements should a first-party portal or marketing surface ever be added (consent gate before any script, event-payload minimization, vendor inventory, retention, and a test that fails on un-consented third-party calls). No findings are raised because no analytics exists and no policy gap is actionable today.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Analytics scripts | — | — | **Absent** | None | Zero vendor matches |
| Tracking pixels | — | — | **Absent** | None | No first-party web content |
| Product analytics | — | — | **Absent** | None | Grafana analytics disabled (live) |
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
- Assessment: nothing to consent to; no tracker can be injected by repository code. The only browser surfaces are Grafana/Dashboards/ntopng/ntfy/IRIS, whose own vendor telemetry is disabled/absent as verified.

### Item: Tool telemetry (Grafana / OpenSearch / Dashboards)

- Evidence: `compose/central/docker-compose.yml:205-206`; live Grafana env (`false`); live OpenSearch plugins (no telemetry plugin); OSD config comment (in-container line 183) + vendor default.
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

- Prior full run `falcon-20261009-2117-full-08e20d1`: same-domain report reached the same N/A verdict with 0 findings; 20261005 and 20260930 runs also emitted no AN findings.
- The 2026-10-11 verification register has no AN rows (nothing to reconcile). This run re-verified the conclusion at `f5cb7c9` with live checks (Grafana env, OpenSearch plugin list, OSD setting, public 302s) and a fresh vendor grep.
- Post-08e20d1 changes (PRs #49–#54: alerting, tunnel ingress, backup path, Wazuh proxy listener alert, exec-bit fix) add no client-side or analytics surface.

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

- Vendor documentation is the basis for the OSD search-telemetry default (off); the shipped setting is commented out and no search-usage index exists on the cluster (prior read-only `_cat/indices` check; not re-run in this pass).
- The grep excluded `mct/` (vendored, archive-only), `docs/audits/` (historical reports), `sbom/` and `review-package/` (generated data); a broader scan of `mct/` found no trackers either.
- Live checks were read-only; no browser session or network capture was performed.

## Findings

_No findings in this domain._
