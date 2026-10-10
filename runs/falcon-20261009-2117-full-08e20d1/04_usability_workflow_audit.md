# 04_usability_workflow_audit — Prompt 04 - Usability and Workflow Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `04_usability_workflow_audit.md` (area USE, prompt)

## Verification Performed

# Usability and Workflow Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` (single-host monitoring lab)
- Branch: `main` / Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: `2026-10-09T22:05:00Z`
- Auditor: subagent (area USE), read-only
- Area code: USE
- Output path (repo convention): `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/04_usability_workflow_audit.md`
- Scope limitations: this repository contains no end-user application; the audit is **Not Applicable** by scope (see Evidence).

## Scope

The prompt targets user-facing workflows (onboarding, login/signup/reset, navigation, dashboards, forms, search, bulk workflows, notifications, preferences, error recovery, empty states, destructive actions, session expiry, offline). This repository is an infrastructure/operations artifact for a network-monitoring lab: it ships host bootstrap scripts, Compose stacks, configuration, runbooks, ledgers, evidence and CI validation — not a product UI. No end-user or admin web application is authored here. The closest operator-facing surfaces are third-party UIs (Grafana, OpenSearch Dashboards, ntopng, ntfy) provisioned from JSON, and CLI/runbook procedures. Those operator workflows are documented and exercised by automation, but they are not the user-workflow surface this prompt audits.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Repository tree (`README.md`, `REPOSITORY.md`, `compose/`, `bootstrap/`, `automation/`, `docs/`, `ledgers/`, `ci/`) | Source | Confirms no application source tree | No `package.json`, `src/`, templates, or app routes |
| `find . -type f \( -name 'package.json' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.css' -o -name 'index.html' \)` | Command | Negative search for a UI codebase | No matches (including the vendored `mct/` tree at depth 3) |
| `README.md:22-44` | Doc | Describes the stack and operator access | Grafana/OSD/ntopng are third-party; no first-party UI |
| `docs/runbooks/OPERATOR_START_HERE.md:1-30` | Doc | Operator workflow surface | "three screens" (Grafana, OSD) + runbooks; deep links in alerts |
| `config/dashboards/dashboards.json`, `index-patterns.json`, `saved-searches.json` | Config | Provisioned dashboard content | Grafana/OSD render third-party UIs; no repo-authored UX layer |
| Prior run `falcon-20261005-full-main-e267ce1/04_usability_workflow_audit.md` | Prior report | Baseline | N/A, no findings |
| Prior in-repo audit `docs/audits/repo-deep-dive/20261002-0522-main-67dec27/` (domain 04) | Prior report | Historical treatment | Same N/A scope decision |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| File-type inventory for web frameworks/UI files | Command | Proves the absence of a first-party UI | Zero matches; no build tooling for a frontend |
| Compose service inventory (26 running containers) | Live | Shows the user-facing surfaces are third-party services | Grafana, OSD, ntopng, ntfy, Traefik |
| `docs/runbooks/*` listing | Doc | Confirms operator procedures are documented | 18 runbooks; operator workflows are ops procedures |
| Prior-run reconciliation | Doc | Consistency | Prior run: N/A, no findings — unchanged at this commit |

## Executive Summary

Not Applicable. There is no end-user application in this repository, so the persona/workflow checks (onboarding, auth flows, forms, bulk operations, notifications preferences, session expiry, offline behaviour) have no first-party surface to audit. No finding is raised. Operator usability is instead covered by the runbook/operator-readiness domain (prompt 16) and the alerting/observability domains; third-party UI usability (Grafana/OSD) is outside this repository's authorship.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Operator entry point | `docs/runbooks/OPERATOR_START_HERE.md` | "Something looks wrong" path | Present | Low | Ops surface, not end-user |
| Dashboards | `config/dashboards/*.json` | Provision Grafana/OSD content | Present | Low | Third-party renderers |
| CLI/automation | `automation/validation/*.sh`, `bootstrap/*.sh` | Operator and CI tooling | Present | Low | Covered by other domains |
| End-user app | — | — | Absent | N/A | No app code |

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

- Prior run `falcon-20261005-full-main-e267ce1`: N/A, no findings. Current run: same conclusion, re-verified against the current tree (`08e20d1`). No regressions or changes to reconcile.
- Related prior items in other domains (DATA-P1-001/SEARCH-P2-001 retention, ARCH-P1-001 single-host) remain tracked in their own domains; they are not usability findings.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| N/A | — | — | — | — | — |

## Recommendations

None for this domain. Operator workflow friction, if any, is in scope for the documentation/operator-readiness and observability domains.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there any owner intent to add a first-party UI (beyond Grafana/OSD)? | Would make this domain assessable in future runs | Owner roadmap |
| Should operator runbook walkthroughs be scored under this domain? | Avoids duplicate coverage with prompt 16 | Orchestrator scope decision |

## Appendix

Negative searches run at `08e20d1`:

```bash
find . -path ./mct -prune -o -type f \( -name 'package.json' -o -name '*.tsx' \
  -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.css' \
  -o -name 'index.html' \) -print          # no matches
find ./mct -maxdepth 3 -type f \( -name 'package.json' -o -name '*.tsx' -o -name '*.css' \)  # no matches
```

## Findings

_No findings in this domain._
