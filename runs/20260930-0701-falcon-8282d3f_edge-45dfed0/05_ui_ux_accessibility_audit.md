# UI/UX, Design System, and Accessibility Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: UX
- Status: N/A — UIs are upstream (Wazuh dashboard / OpenSearch Dashboards, Grafana, ntfy, ntopng, DFIR-IRIS); future readiness only
- Scope limitations: read-only repository review; no rendered UI, contrast, keyboard or screen-reader checks were possible

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| First-party UI/design assets | `find <both repos> -type f \( -name '*.html' -o -name '*.css' -o -name '*.scss' -o -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.vue' -o -name '*.svelte' \) \| wc -l` | `0` |
| Design system / a11y tooling | `grep -rIln -i -E 'tailwind\|storybook\|design token\|aria-\|wcag' <code dirs> \| wc -l` | `0` files |
| UI renderers (upstream) | `grep -n 'image:' compose/central/docker-compose.yml` | `opensearchproject/opensearch-dashboards:2.19.6` (line 92), `grafana/grafana:13.2.2` (175), `binwiederhier/ntfy:v2.28.0` (224), `ntop/ntopng` (247) |
| First-party UI content | `ls config/grafana/dashboards/`; `config/dashboards/saved-searches.json` | 3 Grafana dashboard JSONs + 1 OSD saved-searches file; content is rendered by upstream UIs |
| Upstream session/auth settings | `grep -n 'multitenancy\|securitytenant' automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml` | upstream config: `securitytenant` header whitelisted (line 5), `multitenancy.enabled: false` (line 6) |
| Console exposure path | `evidence/raw/REVIEW-FIX/20260928T011607Z_soc-console-exposure.out` | Wazuh dashboard reached through Cloudflare Access (`soc.mainecybertech.us`); rendering surface is entirely upstream |

## Evidence Reviewed

- `/home/user/falcon-build/compose/central/docker-compose.yml` — pinned upstream UI images (no first-party frontend)
- `/home/user/falcon-build/config/grafana/dashboards/{feeds-overview,central-overview,edge-fleet-overview}.json` — first-party dashboard content
- `/home/user/falcon-build/config/dashboards/saved-searches.json` — first-party OSD saved-search content
- `/home/user/falcon-build/automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml` — upstream Wazuh dashboard configuration
- `/home/user/falcon-build/docs/runbooks/ACCESS_AND_ACCOUNTS.md` — all human UI surfaces are vendor products

## Not Applicable / Future Readiness

**Why N/A.** There is no first-party UI in either repository: no components, no design tokens, no CSS/theme layer, no layouts/nav, no forms/dialogs/toasts/tables, no focus/keyboard/ARIA/semantic-HTML code, no breakpoints/dark mode, no Storybook or visual/a11y tests. The user-visible surfaces are the upstream Wazuh dashboard / OpenSearch Dashboards, Grafana, ntfy, ntopng and (for the MCT stack) DFIR-IRIS. Their accessibility, design system and responsive behavior are vendor-owned and out of scope for a repo audit. Domain score: **0 (not assessable)**.

**What the repo does own.** Dashboard/saved-search definitions and Grafana provisioning (`GF_USERS_ALLOW_SIGN_UP: "false"`, analytics flags off) are configuration content. Any first-party responsibility today is limited to whether panels render legibly on the operator's screens, which is operational verification under the `LIVE` lens.

**Future readiness trigger.** If a first-party operator console or MCT client portal is built, run this prompt with: a documented design-token set, component inventory, WCAG 2.2 AA target, keyboard/screen-reader checks, responsive breakpoints, dark mode, and automated visual + axe-core regression tests in CI. Until such a UI exists, there is no design system to score.

**Findings:** none — no applicable first-party surface.
