# Usability and Workflow Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: USE
- Status: N/A — no end-user application; operator usability is covered by prompt 16 and the `LIVE` lens
- Scope limitations: read-only repository and live-snapshot review; no UI, workflow or form was executed

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| First-party web assets (screens/forms/nav) | `find <both repos> -type f \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.vue' -o -name '*.svelte' \) \| wc -l` | `0` — no first-party UI source in either repository |
| Login/signup/reset | `grep -rIn -i -E 'sign[-_ ]?up\|forgot password\|password reset' <code dirs>` | 1 config hit: `GF_USERS_ALLOW_SIGN_UP: "false"` (`compose/central/docker-compose.yml:181`); no first-party auth flow |
| Screen inventory | `grep -nE '^  [a-z0-9_-]+:\|image:' compose/central/docker-compose.yml` | traefik, opensearch, opensearch-dashboards, vector-aggregator, prometheus, grafana, redis, ntfy, ntopng, node-exporter — all upstream UIs |
| Operator documentation | `ls docs/runbooks/` | 8 runbooks incl. `OPERATOR_START_HERE.md`, `ACCESS_AND_ACCOUNTS.md` |
| First-party interactive surface | `grep -nE 'add_parser' falcon-edge-build/src/falcon_cli/__main__.py` | 15 `falcon deploy edge …` CLI commands; no GUI |
| Live surface | `live_snapshot.txt` local HTTP probes | upstream-only probes (e.g. `127.0.0.1:2586/v1/health -> 200`); no first-party app endpoint |

## Evidence Reviewed

- `/home/user/falcon-build/docs/runbooks/OPERATOR_START_HERE.md` — triage flow; "three screens" are Grafana, OpenSearch Dashboards, ntopng (all upstream)
- `/home/user/falcon-build/docs/runbooks/ACCESS_AND_ACCOUNTS.md` — human access-surface table (Grafana, OSD, ntopng, ntfy, UniFi)
- `/home/user/falcon-build/compose/central/docker-compose.yml` — service inventory; no first-party end-user app
- `/home/user/falcon-edge-build/src/falcon_cli/__main__.py` — the only first-party interactive interface
- `20260930-0701-falcon-8282d3f_edge-45dfed0/live_snapshot.txt` — live sockets/probes

## Not Applicable / Future Readiness

**Why N/A.** The audited system is an infrastructure monitoring lab, not an end-user product. Both repositories contain configuration, automation, doctrine and documentation (zero HTML/CSS/JS/TS source; check above). Every user-visible screen is a third-party UI — Grafana 13.2.2, OpenSearch Dashboards 2.19.6, ntfy 2.28.0, ntopng — consumed with first-party dashboard/saved-search content. There is no onboarding, navigation, forms, search UX, bulk workflow, session-expiry or offline behavior in first-party code. Domain score: **0 (not assessable)** per the shared scoring rules.

**Operator usability is audited elsewhere.** The human workflow surface is runbooks + upstream dashboards + the `falcon` CLI. Prompt 16 covers documentation/operator readiness; the `LIVE` lens covers operator use of the live stack. Usability findings about the Grafana/OSD screens belong there, not in this report.

**Future readiness trigger.** This domain becomes applicable if a first-party operator console, status page or customer portal is built (e.g. an MCT client-facing UI). Prerequisites for a future USE run: source under version control, named personas, documented workflows, and reachable error/empty/session states for literal walkthroughs.

**Findings:** none — no applicable first-party surface.
