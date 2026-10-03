# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: API
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/08_api_contracts_realtime_integrations.md
- Scope limitations: No API layer exists. Static review only.

## Scope

Looked for server API routes, route handlers, server actions, RPC/GraphQL, realtime channels, webhooks, and third-party integrations. Relevant integrations: PWA manifest/service worker and Google Fonts. Not reviewed: host/CDN/edge config (none in repo).

## Evidence Reviewed

- repo tree (`app/` has only `page.tsx`, `layout.tsx`, `globals.css` — no `app/api/`, no `route.ts`)
- `app/layout.tsx` lines 37–38 (font preconnect), `app/globals.css` line 5 (`@import` Google Fonts)
- `public/manifest.json`, `public/sw.js`, `lib/offline/sw.ts`
- `docs/prompts/.../specs/api-contracts.md`, `specs/database-schema.md` (plans, not implemented)
- `inventory.json` — `routes: []`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| directory listing `app/` | static | route presence | only page/layout/css |
| grep `route\.ts\|NextResponse\|app/api` | command | API presence | 0 |
| `layout.tsx`/`globals.css` | code | external calls | Google Fonts only |
| `specs/api-contracts.md` | docs | intended contracts | no code |
| `public/sw.js` | code | integration | caches same-origin GET |

## Executive Summary

There is **no API layer at all**: no route handlers, no server actions, no RPC, no webhooks, and no realtime. The app communicates with exactly one external service class — Google Fonts — at runtime. The prompt pack documents intended API contracts and a Supabase schema, but none of it is implemented. For a guest-only local-first game this is acceptable, and the absence is best recorded as **future readiness** rather than a defect. The two actionable integration concerns are (1) the uncached, privacy-relevant Google Fonts dependency and (2) the absence of any contract/versioning discipline to govern the future save-sync API.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| API routes | (none) | server API | Absent | N/A future | no `app/api` |
| Server actions | (none) | mutations | Absent | N/A | client-only |
| Realtime | (none) | live sync | Absent | N/A future | — |
| Webhooks | (none) | inbound events | Absent | N/A | — |
| PWA integration | `public/manifest.json`, `public/sw.js` | install/offline | Implemented | Low | — |
| Fonts | `app/layout.tsx`, `app/globals.css` | typography | External | Medium | uncached, privacy |
| Supabase | docs plan only | cloud | Absent | N/A future | `specs/*` |
| Vercel/Cloudflare | docs plan only | hosting | Absent | N/A future | integration guides |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| REST/RPC endpoints | 0 | none | N/A | add when cloud |
| API contracts/versioning | 0 | specs only | no implementation | define before cloud |
| Error/response envelope | 0 | none | N/A | define with API |
| Server actions | 0 | none | N/A | — |
| Webhooks | 0 | none | N/A | — |
| Realtime | 0 | none | N/A | — |
| External integrations | 2 | Google Fonts | uncached/privacy | self-host fonts |
| Auth integration | 0 | none | N/A future | Supabase plan |
| Rate limiting | 0 | none | N/A | add with API |

## Detailed Review

### Item: Google Fonts runtime dependency
- Evidence: `app/globals.css` line 5 `@import url('https://fonts.googleapis.com/...')`; `app/layout.tsx` lines 37–38 preconnect.
- Nature: first-load third-party request from Google; `public/sw.js` only caches `type === 'basic'` responses, so CORS font responses are not cached → offline renders fallback fonts.
- Risks: privacy (external IP disclosure), offline inconsistency, extra DNS/TLS.

### Item: Future API contracts
- Evidence: `docs/prompts/.../specs/api-contracts.md` and `specs/database-schema.md` exist; no code.
- Risk: when implemented, ad-hoc shapes without validation/versioning could cause drift.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| API-001 | API contract layer | repo tree | none | N/A now | P2 (future) | define schema/versioning first |
| API-002 | External font dependency | `globals.css`, `layout.tsx` | preconnect | uncached/privacy | P2 | self-host fonts |

## Findings

### Finding ID: API-P2-001 - No API contract or versioning discipline exists to govern the planned save-sync API

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - repo tree — no `app/api/`, no `route.ts`, no server actions
  - `docs/prompts/.../specs/api-contracts.md` — intended contracts, no code
  - `docs/prompts/.../specs/database-schema.md` — intended schema, no code
- What is happening: API and DB contracts are documented only as prompts; there is no implemented interface, schema, or versioning.
- Why it matters: When cloud save/adventure validation is built (ARCH-P1-001), the absence of a contract-first approach invites drift between client types and server shapes.
- User / business impact: Future integration cost/risk; not a current defect.
- Security / privacy / reliability impact: Future correctness/security; none today.
- Recommended fix: Before building the API, define versioned request/response schemas (zod/OpenAPI) shared between client and server, and a compatibility policy.
- Suggested validation: Contract tests against the defined schema once implemented.
- Owner suggestion: backend
- Effort estimate: M
- Dependencies: ARCH-P1-001
- Status: open

### Finding ID: API-P2-002 - Google Fonts is an uncached runtime dependency with privacy implications

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `app/globals.css` line 5 — `@import url('https://fonts.googleapis.com/css2?...')`
  - `app/layout.tsx` lines 37–38 — preconnect to `fonts.googleapis.com` / `fonts.gstatic.com`
  - `public/sw.js` line 43 — only `response.type === 'basic'` (same-origin) responses are cached; cross-origin font responses are `cors`
- What is happening: Typography loads from Google on first paint and is not available offline/cached, so an installed offline PWA sees fallback fonts and leaks a third-party request.
- Why it matters: The app is offline-first; the visual design degrades offline, and EU/GDPR guidance treats Google Fonts CDN calls as a personal-data transfer.
- User / business impact: Inconsistent offline UI; privacy/compliance exposure.
- Security / privacy / reliability impact: Privacy + offline reliability.
- Recommended fix: Self-host the two fonts (or use `next/font` local) and remove the external `@import`/preconnect; precache with the SW.
- Suggested validation: Offline load renders the intended font; network tab shows no third-party request.
- Owner suggestion: frontend
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Contract drift at cloud time | P2 | Medium | Medium | API-P2-001 | schema-first |
| Offline font fallback/privacy | P2 | High | Low | API-P2-002 | self-host fonts |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Self-host fonts.

### This Month
- Draft versioned API contract before any server work.

### Later / Platform Evolution
- Implement Supabase save-sync with RLS per the plan.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Self-host fonts | offline + privacy | `globals.css`, `layout.tsx`, `public/` | offline load |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Self-host fonts | P2 | frontend | S | none |
| API contract definition | P2 | backend | M | product decision |

## Suggested Tests

- Offline load snapshot verifying font applied.
- Contract tests (once API exists).

## Suggested Documentation Updates

- `docs/integrations.md` listing external dependencies and their offline behavior.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is Supabase still planned? | drives API work | roadmap |
| Which host (Vercel/Cloudflare)? | headers/deploy | decision |

## Appendix

- REST/RPC/webhooks/realtime: **not applicable at this commit** — no server. Recorded as future readiness with evidence: no `app/api/`, no `route.ts`, `inventory.json` `routes: []`.
