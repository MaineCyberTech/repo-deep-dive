# Observability, Monitoring, and Incident Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: OBS
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/14_observability_monitoring_incident_readiness.md
- Scope limitations: Client-only app; no servers to instrument. Static review.

## Scope

Reviewed client error handling, logging, crash reporting, release markers, and user-impact signals. Server metrics/tracing/health checks are **not applicable** (no server), recorded as future readiness. Not reviewed: hosting-provider monitoring (none configured).

## Evidence Reviewed

- `lib/storage/indexeddb.ts`, `lib/storage/autosave.ts`, `lib/offline/sw.ts` (logging)
- `components/device/MainDevice.tsx`, `components/device/AdventureScreen.tsx` (error handling)
- `app/page.tsx` (boot), `app/layout.tsx` (no error boundary)
- grep `console.` / `Sentry` / `error-boundary` / `metrics`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| grep `console.(log\|warn\|error)` | command | logging surface | 9 matches, all console |
| grep `Sentry\|datadog\|opentelemetry` | command | error tracking | 0 |
| grep `ErrorBoundary\|componentDidCatch` | command | crash handling | 0 |
| `app/page.tsx` | code | boot failure | no error UI |
| `next.config.js` | config | release markers | none |

## Executive Summary

Observability is effectively absent beyond `console.*`. There is **no error tracking** (Sentry/Rollbar), **no metrics/tracing**, **no React error boundary**, **no structured logging**, and **no release/version marker** exposed at runtime (only a hardcoded "BUDDY v0.1" string). For a client-only offline game this is common, but it means the team cannot see crashes, save failures, or offline/deploy incidents in production, and cannot correlate a bug report to a build. Given the P1 save-state bugs identified elsewhere, the lack of any signal when a save fails (beyond a transient "save failed" badge) is a real operational blind spot. Server-side golden signals, health checks, and audit logs are **not applicable** at this commit.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Error tracking | (none) | crash reports | Absent | P2 | no Sentry |
| Structured logs | `console.*` ×9 | diagnostics | None | P2 | unstructured |
| Error boundary | (none) | UI crash containment | Absent | P2 | — |
| Metrics/tracing | (none) | perf | Absent | P3 | no server |
| Release markers | "BUDDY v0.1" | version | Hardcoded | P2 | no build id |
| Health/readiness | (none) | uptime | N/A | N/A | static |
| Audit/security logs | (none) | events | N/A | N/A | no server |
| User-impact signals | `save failed` badge | save status | Minimal | P2 | not reported |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Structured logs | 1 | console only | no format/levels | add logger |
| Request IDs/correlation | 0 | none | N/A client | add build/session id |
| Error tracking | 0 | none | no visibility | add Sentry |
| Metrics | 0 | none | N/A | optional |
| Tracing | 0 | none | N/A | — |
| Health/readiness | 0 | N/A | N/A | — |
| Client errors | 1 | console.error + badge | no reporting | error boundary + report |
| Job metrics | 0 | none | N/A | — |
| DB/queue/webhook metrics | 0 | none | N/A | — |
| Uptime checks | 0 | N/A | N/A | — |
| Alerts/dashboards | 0 | none | none | optional |
| Incident runbooks | 0 | none | none | add for releases |

## Detailed Review

### Item: Save failure visibility
- Evidence: `MainDevice.tsx` lines 70–73 show `save failed` for 3s; `AdventureScreen.tsx` line 55 only `console.error`; `indexeddb.ts` throws `new Error('Save failed')`.
- Risk: Silent data-loss scenarios have no durable record and no user recovery path.

### Item: Crash containment
- Evidence: no error boundary in `app/layout.tsx`; a render error in `MainDevice` blanks the app.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| OBS-001 | Error tracking | grep | none | no telemetry | P2 | add Sentry |
| OBS-002 | Crash containment | `layout.tsx` | none | no boundary | P2 | add boundary |
| OBS-003 | Release/build marker | hardcoded string | manual | no build id | P2 | inject build id |
| OBS-004 | Server golden signals | no server | N/A | N/A future | N/A | add with API |

## Findings

### Finding ID: OBS-P2-001 - No error tracking, metrics, or structured logging; only console output

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - grep `console.(log|warn|error)` → 9 matches (`lib/storage/indexeddb.ts` ×4, `lib/offline/sw.ts` ×2, `autosave.ts`, `HatchFlow.tsx`, `AdventureScreen.tsx`)
  - grep `Sentry|datadog|opentelemetry` → 0
- What is happening: Errors and warnings go to the browser console; nothing is aggregated or reported.
- Why it matters: Production crashes and save failures are invisible; bugs are reproduced only by user report.
- User / business impact: Longer time-to-detect/resolve; silent data-loss risk.
- Security / privacy / reliability impact: Reliability/operability.
- Recommended fix: Add a minimal error-reporting integration (e.g., Sentry client) with build id/session id, plus a small structured logger that also captures save failures; keep it opt-in/privacy-aware.
- Suggested validation: Force a save error in a test and assert an event is captured (mocked reporter).
- Owner suggestion: frontend/platform
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: OBS-P2-002 - No React error boundary, so a render error can blank the whole app

- Severity: P2
- Confidence: High
- Area: OBS
- Evidence:
  - `app/layout.tsx` / `app/page.tsx` — no `ErrorBoundary`/`componentDidCatch`/`error.tsx`
  - grep `ErrorBoundary|componentDidCatch` → 0
- What is happening: An exception during render (e.g., malformed save `progression` per DATA-P1-002) crashes to a blank screen with no recovery UI.
- Why it matters: The exact corrupt-save failure mode identified elsewhere produces an unrecoverable screen.
- User / business impact: Users lose access and cannot self-recover.
- Security / privacy / reliability impact: Reliability/UX.
- Recommended fix: Add Next.js `app/error.tsx` and a class error boundary around the device, offering "reset save" and "reload" actions, and report the error.
- Suggested validation: Render with an invalid buddy state and assert the fallback UI plus recovery path.
- Owner suggestion: frontend
- Effort estimate: S
- Dependencies: DATA-P1-002
- Status: open

### Finding ID: OBS-P3-001 - No release/build marker exposed at runtime

- Severity: P3
- Confidence: High
- Area: OBS
- Evidence:
  - `components/device/MainDevice.tsx` line 91 — hardcoded `<h1>BUDDY v0.1</h1>`
  - no build id injection in `next.config.js`
- What is happening: Runtime version is a hardcoded string unrelated to the commit/tag.
- Why it matters: Bug reports and stale-cache issues (ARCH-P2-001) cannot be tied to a build.
- User / business impact: Slower triage.
- Security / privacy / reliability impact: Operability.
- Recommended fix: Inject commit SHA/build time (e.g., `NEXT_PUBLIC_BUILD_ID`) and display it subtly; log it at startup.
- Suggested validation: Build with a known SHA and assert it appears/logs.
- Owner suggestion: platform
- Effort estimate: S
- Dependencies: CI-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Invisible production errors | P2 | High | Medium | OBS-P2-001 | error tracking |
| Blank-screen crash | P2 | Medium | High | OBS-P2-002 | error boundary |
| Unknown deployed build | P3 | Medium | Low | OBS-P3-001 | build marker |

## Recommendations

### Immediate / Release Blocking
- None (client-only).

### This Week
- Add `app/error.tsx` and a device error boundary.
- Add a build id.

### This Month
- Add privacy-aware error reporting and a save-failure signal.

### Later / Platform Evolution
- Add server golden signals when an API exists.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `app/error.tsx` | crash recovery | `app/error.tsx` | invalid-state test |
| Build id injection | triage | `next.config.js`, UI | build test |
| Logger wrapper | consistent logs | `lib/log.ts` | unit test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Error boundary | P2 | frontend | S | none |
| Error reporting | P2 | platform | M | privacy review |
| Build marker | P3 | platform | S | CI |

## Suggested Tests

- Error-boundary fallback renders on thrown error.
- Save-failure path reports once and shows recovery.
- Build-id unit test.

## Suggested Documentation Updates

- `docs/observability.md`; incident note in `README.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is privacy-respecting telemetry acceptable? | enables OBS fix | product/legal |
| Which host? | error sink options | decision |

## Appendix

- Server golden signals, health checks, queue/webhook metrics, uptime: **not applicable** — no server at this commit.
