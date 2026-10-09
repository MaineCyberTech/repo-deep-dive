# 17_mobile_pwa_responsive_access — Prompt 17 - Mobile, PWA, and Responsive Access Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `17_mobile_pwa_responsive_access.md` (area MOB, prompt)

## Verification Performed

# Mobile, PWA, and Responsive Access Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` (single-host monitoring lab)
- Branch: `main` / Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: `2026-10-09T22:05:00Z`
- Auditor: subagent (area MOB), read-only
- Area code: MOB
- Output path (repo convention): `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/17_mobile_pwa_responsive_access.md`
- Scope limitations: no mobile client, PWA manifest, service worker, install flow, push integration, or responsive first-party layout exists in this repository; the audit is **Not Applicable** by scope (see Evidence).

## Scope

The prompt targets a mobile/PWA client: viewport, responsive layouts, mobile nav, touch targets, mobile forms/dialogs/tables, auth/dashboard/admin mobile, PWA manifest, service worker, offline fallback, install prompt, push notifications, icons, cache strategy, update flow, background sync, mobile E2E, and touch accessibility. This repository is an infrastructure/ops artifact; operator access is CLI plus browser dashboards (Grafana, OpenSearch Dashboards) rendered by third-party software. There is no first-party HTML, manifest, service worker, or push integration to audit. Mobile access to third-party dashboards depends on those vendors' responsive implementations, which are outside this repository's authorship.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Negative search: `manifest.json`, `manifest.webmanifest`, `sw.js`, `service-worker.js`, `*.tsx/jsx/vue/svelte`, `index.html` | Command | Proves no PWA/mobile client exists | No matches (including `mct/` at depth 3) |
| Search for `viewport|service worker|PWA|install prompt` in source trees | Command | Confirms no PWA code or configuration | Matches only in audit docs and third-party SBOM metadata |
| `README.md:22-44`, `docs/runbooks/OPERATOR_START_HERE.md:1-30` | Doc | Operator access model | Desktop browser dashboards + CLI; no mobile app |
| `config/dashboards/*.json` | Config | Provisioned dashboard content | Rendered by third-party UIs; no first-party responsive layer |
| Prior run `falcon-20261005-full-main-e267ce1/17_mobile_pwa_responsive_access.md` | Prior report | Baseline | N/A, no findings |
| Prior in-repo audits (`docs/audits/repo-deep-dive/*/17_*`) | Prior reports | Historical treatment | Same N/A scope decision |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| File-type and keyword inventory (above) | Command | Confirms absence of PWA/mobile artifacts | Zero first-party matches |
| Compose/service inventory | Live | Operator endpoints are Grafana/OSD/ntfy/Traefik | All third-party, desktop-oriented |
| Notification path review | Source | Push is via ntfy (HTTP), not a web-push PWA integration | `automation/alerting/ntfy_relay.py`, ntfy containers |
| Prior-run reconciliation | Doc | Consistency | Prior run: N/A, no findings — unchanged at this commit |

## Executive Summary

Not Applicable. There is no mobile or PWA client in this repository: no manifest, service worker, install flow, background sync, or first-party responsive layout. Operators use desktop browser dashboards (Grafana/OpenSearch Dashboards) and the ntfy mobile app for notifications — both third-party clients outside this repository's scope. No finding is raised.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| PWA manifest | — | — | Absent | N/A | No first-party web app |
| Service worker / offline cache | — | — | Absent | N/A | No first-party web app |
| Mobile nav / touch UI | — | — | Absent | N/A | Third-party renderers |
| Push notifications | ntfy containers (`falcon-central-ntfy-1`, DO instance) | Operator alerts | Present (HTTP pub/sub) | Low | ntfy mobile app is third-party |
| Mobile E2E tests | — | — | Absent | N/A | No first-party UI |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Viewport | 0 (N/A) | No first-party HTML | N/A | None |
| Responsive layouts | 0 (N/A) | Third-party renderers | N/A | None |
| Mobile nav | 0 (N/A) | No first-party UI | N/A | None |
| Touch targets | 0 (N/A) | No first-party UI | N/A | None |
| Mobile forms | 0 (N/A) | No first-party UI | N/A | None |
| Mobile dialogs/tables | 0 (N/A) | Third-party renderers | N/A | None |
| Auth/dashboard/admin mobile | 0 (N/A) | Grafana/OSD third-party | N/A | None |
| PWA manifest | 0 (N/A) | Absent | N/A | None |
| Service worker | 0 (N/A) | Absent | N/A | None |
| Offline fallback | 0 (N/A) | Absent | N/A | None |
| Install prompt | 0 (N/A) | Absent | N/A | None |
| Push notifications | 0 (N/A) | ntfy third-party client | N/A | None |

## Findings

_No findings in this domain (Not Applicable by scope)._

## Prior-Run Comparison

- Prior run `falcon-20261005-full-main-e267ce1`: N/A, no findings. Current run: same conclusion, re-verified at `08e20d1`. Nothing to reconcile.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| N/A | — | — | — | — | — |

## Recommendations

None for this domain. If a first-party mobile/PWA console is ever added, re-scope this domain and add manifest/service-worker/offline/push checks plus mobile E2E (viewport, touch targets, horizontal overflow).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Do operators use the ntfy mobile app for paging today? | Determines whether notification UX should be reviewed somewhere | Owner confirmation |
| Any plan for a mobile triage client? | Would make this domain assessable | Owner roadmap |

## Appendix

Negative searches run at `08e20d1`:

```bash
find . -type f \( -name 'manifest.json' -o -name 'manifest.webmanifest' -o -name 'sw.js' \
  -o -name 'service-worker.js' -o -name 'index.html' \) -print     # none
grep -rliE 'viewport|service ?worker|pwa|install prompt' --include='*.md' --include='*.yml' . \
  | grep -v 'docs/audits' | grep -v 'sbom/'                        # none in source trees
```

## Findings

_No findings in this domain._
