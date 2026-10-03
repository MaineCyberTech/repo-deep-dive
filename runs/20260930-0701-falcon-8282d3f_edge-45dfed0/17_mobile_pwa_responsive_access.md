# Mobile, PWA, and Responsive Access Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: MOB
- Status: N/A — no first-party mobile or PWA surface; the only mobile touchpoint is the upstream ntfy app
- Scope limitations: read-only repository and live-snapshot review; no device, viewport or PWA runtime was exercised

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Service worker / PWA manifest | `grep -rIln -i -E 'service.?worker\|workbox\|webmanifest' <code dirs> \| wc -l` | `0` files |
| Viewport / responsive markup | `find <both repos> -name '*.html' \| wc -l` | `0` HTML files, so no `<meta name="viewport">` or responsive layout exists to audit |
| Mobile app frameworks | `grep -rIn -i -E 'react-native\|flutter\|expo' <code dirs>` | only `react-native-*` packages inside the upstream OpenSearch Dashboards SBOM (`sbom/vuln/...`); no first-party app code |
| Install/push/offline code | `grep -rIln -i -E 'install prompt\|push subscription\|background sync' <code dirs> \| wc -l` | `0` files |
| Mobile touchpoint (upstream) | `sed -n '1,30p' config/ntfy/server.yml` | line 16: "Allow logging in from the web app and mobile app"; `enable-login: true`; ntfy mobile app is the operator's only mobile surface |
| Operator UX reference | `grep -rIn 'mobile app' config/grafana/dashboards/feeds-overview.json` | dashboard note: "mobile app subscribes to that topic" (alert notifications) |

## Evidence Reviewed

- `/home/user/falcon-build/config/ntfy/server.yml` — upstream ntfy server; mobile app login enabled
- `/home/user/falcon-build/config/grafana/dashboards/feeds-overview.json` — operator note that the mobile app subscribes to the alert topic
- `/home/user/falcon-build/docs/runbooks/ACCESS_AND_ACCOUNTS.md` — ntfy users/credential handling for that upstream app
- `/home/user/falcon-build/compose/central/docker-compose.yml` — pinned upstream ntfy image `binwiederhier/ntfy:v2.28.0` (line 224)
- `/home/user/falcon-build/docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/live_snapshot.txt` — live service/socket inventory (no mobile/API surface beyond upstream)

## Not Applicable / Future Readiness

**Why N/A.** Neither repository contains a mobile app, PWA, service worker, web manifest, responsive HTML, touch UI or push/offline logic; there is no first-party web asset at all (0 HTML/CSS/JS/TS files). The edge sensor is a headless Linux device agent and the central stack is operated from desktop browsers (Grafana, OpenSearch Dashboards, ntopng) plus the `falcon` CLI. The only mobile experience is the upstream ntfy app subscribing to alert topics — a vendor surface already pinned and access-controlled, not first-party code. Domain score: **0 (not assessable)**.

**What is nearby but out of scope.** The alert channel's mobile usability (notification readability, tap-through links to Grafana) is part of notification delivery under prompt 30 and operator readiness under 16; the MCT stack's upstream IRIS app likewise ships its own mobile behavior, if any.

**Future readiness trigger.** If a first-party mobile dashboard, PWA or installable operator console is proposed, this prompt becomes applicable and needs: viewport/responsive rules, mobile nav, touch-target and mobile-form checks, service-worker cache/update strategy, offline fallback, install prompt, push permission UX and mobile E2E tests (e.g. Playwright device profiles). None of those exist today.

**Findings:** none — no applicable first-party surface.
