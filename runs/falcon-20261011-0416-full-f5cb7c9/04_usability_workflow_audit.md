# 04_usability_workflow_audit — Prompt 04 - Usability and Workflow Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `04_usability_workflow_audit.md` (area USE, prompt)

## Verification Performed

# Usability and Workflow Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` (single-host monitoring lab)
- Branch: `main` / Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: `2026-10-11T04:45:00Z`
- Auditor: subagent (area USE), read-only
- Area code: USE
- Output path (repo convention): `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/04_usability_workflow_audit.md`
- Scope limitations: this repository contains no end-user application; the audit is **Not Applicable** by scope (see Evidence). Operator-facing workflows are covered by the operator-readiness (16), observability (14) and alerting domains.

## Scope

The prompt targets user-facing workflows (onboarding, login/signup/reset, navigation, dashboards, forms, search/filter/sort, bulk workflows, admin/support workflows, notifications, preferences, error recovery, empty/loading states, destructive actions, session expiry, offline/poor network, help paths). This repository is an infrastructure/operations artifact for a network-monitoring lab: it ships host bootstrap scripts, Compose stacks, configuration, runbooks, ledgers, evidence and CI validation - not a product UI. No end-user or admin web application is authored here. The closest operator-facing surfaces are third-party UIs (Grafana, OpenSearch Dashboards, ntopng, ntfy) provisioned from JSON, plus CLI/runbook procedures.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Repository tree (`README.md`, `REPOSITORY.md`, `compose/`, `bootstrap/`, `automation/`, `docs/`, `ledgers/`, `ci/`) | Source | Confirms no application source tree | No `package.json`, `src/`, templates or app routes |
| `find . -path ./.git -prune -o -type f \( -name 'package.json' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.css' -o -name 'index.html' \) -print` | Command | Negative search for a UI codebase | No matches anywhere, including the vendored `mct/` tree |
| `find ./mct -type f \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.tsx' \)` | Command | Checks the vendored subtree for UI code | No matches; `mct/reporting/templates/` is Markdown report templates only |
| `README.md` (stack/access sections), `docs/runbooks/OPERATOR_START_HERE.md` | Doc | Describes the operator surface | Grafana/OSD/ntopng are third-party; no first-party UI |
| `config/dashboards/dashboards.json`, `index-patterns.json`, `saved-searches.json` | Config | Provisioned dashboard content | Rendered by third-party UIs; no repo-authored UX layer |
| Live container inventory (27 running containers) | Live | Shows the user-facing surfaces are third-party services | Grafana, OpenSearch Dashboards, ntopng, ntfy, Traefik |
| Prior run `falcon-20261009-2117-full-08e20d1/_domains/04_usability_workflow_audit.json` | Prior report | Baseline | N/A, no findings |
| `falcon-20261011-0400-verify-main-584e1a3/follow_up_register.md` | Prior register | Reconciliation | No USE entries; nothing to reconcile |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| File-type inventory (above) at `f5cb7c9` | Command | Proves the absence of a first-party UI | Zero matches |
| Vendored `mct/` subtree scan | Command | Rules out a hidden UI in vendored code | Zero matches; Markdown templates only |
| Live service inventory | Live | Confirms operator surfaces are third-party | 27 containers, none first-party UI |
| Runbook inventory (`docs/runbooks/`, 18 files) | Doc | Operator procedures exist and are documented | Covered by prompt 16 |
| Prior-run reconciliation | Doc | Consistency | Prior full run N/A; newest verification run has no USE rows |

## Executive Summary

Not Applicable. There is no end-user application in this repository, so the persona/workflow checks (onboarding, auth flows, forms, bulk operations, notification preferences, session expiry, offline behaviour) have no first-party surface to audit. No finding is raised. Operator usability is instead covered by the documentation/operator-readiness domain (prompt 16) and the observability/alerting domains; third-party UI usability (Grafana/OSD/ntopng) is outside this repository's authorship.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Operator entry point | `docs/runbooks/OPERATOR_START_HERE.md` | "Something looks wrong" path | Present | Low | Ops surface, not end-user |
| Dashboards | `config/dashboards/*.json` | Provision Grafana/OSD content | Present | Low | Third-party renderers |
| CLI/automation | `automation/validation/*.sh`, `bootstrap/*.sh` | Operator and CI tooling | Present | Low | Covered by other domains |
| End-user app | - | - | Absent | N/A | No app code |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Onboarding | 0 (N/A) | No app | N/A | None |
| Login/signup/reset | 0 (N/A) | No app | N/A | None |
| Navigation | 0 (N/A) | No app | N/A | None |
| Dashboards | 0 (N/A) | Third-party provisioned JSON | N/A | None |
| Forms | 0 (N/A) | No app | N/A | None |
| Search/filter/sort | 0 (N/A) | OSD/Grafana third-party | N/A | None |
| Bulk workflows | 0 (N/A) | No app | N/A | None |
| Admin/support workflows | 0 (N/A) | Ops runbooks (other domain) | N/A | None |
| Notifications | 0 (N/A) | ntfy third-party | N/A | None |
| Preferences | 0 (N/A) | No app | N/A | None |
| Error recovery | 0 (N/A) | No app | N/A | None |
| Empty/loading states | 0 (N/A) | No app | N/A | None |

## Findings

_No findings in this domain (Not Applicable by scope)._

## Prior-Run Comparison

- Prior full run `falcon-20261009-2117-full-08e20d1`: N/A, no findings. Current run: same conclusion, re-verified at `f5cb7c9`. Nothing to reconcile.
- Newest statuses (`falcon-20261011-0400-verify-main-584e1a3/follow_up_register.md`): no USE-domain entries.
- Prior in-repo audit `docs/audits/repo-deep-dive/20261002-0522-main-67dec27/` (domain 04): same N/A scope decision.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| N/A | - | - | - | - | - |

## Recommendations

None for this domain. Operator workflow friction, if any, belongs to the documentation/operator-readiness and observability domains.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there owner intent to add a first-party UI (beyond Grafana/OSD)? | Would make this domain assessable in future runs | Owner roadmap |
| Should operator runbook walkthroughs be scored under this domain? | Avoids duplicate coverage with prompt 16 | Orchestrator scope decision |

## Appendix

Negative searches run at `f5cb7c9` (2026-10-11):

```bash
find . -path ./.git -prune -o -type f \( -name 'package.json' -o -name '*.tsx' -o -name '*.jsx' \
  -o -name '*.vue' -o -name '*.svelte' -o -name '*.css' -o -name 'index.html' \) -print   # no matches
find ./mct -type f \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.tsx' \)   # no matches
find . -path ./.git -prune -o -type f -name '*.html' -print
# -> only docs/audits/repo-deep-dive/<prior-run>/dashboard.html (2 generated audit dashboards, not app UI)
```

## Findings

_No findings in this domain._
