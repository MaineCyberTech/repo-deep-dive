# Security, Authorization, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: SEC
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/06_security_authz_tenancy_audit.md
- Scope limitations: Client-only app with no server, no auth, no tenancy. Static analysis only; no dynamic testing. No secrets printed.

## Scope

Reviewed authentication/authorization surfaces, session/identity handling, input handling (nickname, save import), external requests, security headers, and dependency surface. Because there is no backend, tenant isolation/RLS/IDOR/SSRF are **not applicable** at this commit and are recorded as future readiness. Not reviewed: hosting/CDN config (none in repo).

## Evidence Reviewed

- `components/hatch/HatchFlow.tsx` (nickname input, guest id)
- `lib/storage/indexeddb.ts` (export/import), `lib/buddy/store.ts`
- `next.config.js`, `app/layout.tsx`
- `package.json` / `package-lock.json`
- `lib/actions/care.ts` (Math.random in messages)
- grep for secret patterns across the repo

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| secret-pattern grep | command | secret exposure | only string matches in prose; no live secrets |
| `lib/storage/indexeddb.ts` lines 86–99 | code | untrusted input | `atob`+`JSON.parse`, minimal validation |
| `next.config.js` | config | headers | no `headers()` configured |
| `app/layout.tsx` lines 37–38 | code | external origins | Google Fonts preconnect |
| `package-lock.json` | lockfile | dependency risk | lockfileVersion 3 present |
| `inventory.json` `secret_adjacent_files` | data | secrets | empty |

## Executive Summary

`buddy` is a guest-only, offline, single-player web game with **no server, no accounts, no cookies/tokens, no API keys, and no secrets in the repository** (a pattern scan found only prose matches). For that scope, the security surface is small and there are **no P0/P1 security vulnerabilities**. The main hardening gaps are: save import accepts essentially arbitrary JSON (`importSave` only checks `version` and `guestId`), no HTTP security headers/CSP are set, and the guest identity uses `Math.random` and is predictable. All three are low-to-moderate given there is no server-side authority or other user's data at risk. When account mode/Supabase is introduced, the "no server authority" gap (ARCH-P1-001) becomes a P1 security issue per the repo's own spec.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Auth provider | (none) | authn | Absent | N/A (guest-only) | account phase planned |
| Session/token/cookie | (none) | sessions | Absent | N/A | no server |
| JWT validation | (none) | — | N/A | N/A | — |
| CSRF/CORS | (none) | request forgery | N/A | N/A | no server |
| Rate limits | (none) | abuse | Absent | N/A | no server |
| Security headers | `next.config.js` | browser hardening | Absent | P2 | no CSP/HSTS/etc. |
| Input validation | `HatchFlow.tsx`, `indexeddb.ts` | untrusted input | Partial | P2 | import unvalidated |
| Save import | `indexeddb.ts::importSave` | data ingress | Weak | P2 | arbitrary JSON |
| Secrets | repo-wide | secrets | None found | Low | grep clean |
| Dependency risk | `package-lock.json` | supply chain | Untracked | P2 | see SUPPLY |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Auth provider | 0 | none | guest-only | document |
| Session tokens/cookies | 0 | none | N/A | N/A |
| JWT validation | 0 | none | N/A | N/A |
| CSRF/CORS | 0 | none | N/A | N/A |
| Rate limits | 0 | none | N/A | N/A |
| Security headers | 1 | `next.config.js` | no headers | add CSP/headers |
| Input/output validation | 2 | nickname slice; no schema | import weak | use zod |
| File handling | 1 | import base64 | no size/type checks | validate |
| API permissions | 0 | none | N/A | N/A |
| Admin permissions | 0 | none | N/A | N/A |
| Tenant/org isolation | 0 | none | N/A | future |
| RLS policies | 0 | none | N/A | future (supabase plan) |

## Detailed Review

### Item: Save import
- Evidence: `lib/storage/indexeddb.ts` — `exportSave` = `btoa(JSON.stringify(save))`; `importSave` = `atob` → `JSON.parse`, then only `if (!save.version || !save.guestId) throw`.
- Risks: A crafted save can set arbitrary `buddy` (stats, level, bond, health, progression) and `inventory` (coins/items), then is written to IndexedDB. In this local-only game that is a self-cheat, not cross-user impact.

### Item: Security headers
- Evidence: `next.config.js` has no `async headers()`; `app/layout.tsx` includes no CSP meta.
- Risks: No defense-in-depth for any future injected content; low for a static app.

### Item: External origins
- Evidence: `app/layout.tsx` preconnects `fonts.googleapis.com`/`fonts.gstatic.com`; `globals.css` `@import` Google Fonts.
- Risks: third-party request on first load, privacy/GDPR consideration (see API-P2-002).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEC-001 | Importing saves | `indexeddb.ts` | version/guestId only | no schema | P2 | zod validate |
| SEC-002 | Security headers | `next.config.js` | none | no CSP | P2 | add headers |
| SEC-003 | Guest identity | `HatchFlow.tsx` | `Math.random` | predictable | P3 | crypto UUID |
| SEC-004 | Authn/authz/tenancy | repo tree | none | N/A guest-only | Informational | server phase |

## Findings

### Finding ID: SEC-P2-001 - Save import performs no schema validation (arbitrary state injection)

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `lib/storage/indexeddb.ts` lines 86–99 — `importSave` decodes base64, `JSON.parse`, checks only `!save.version || !save.guestId`
  - `package.json` — `zod` is a dependency but has no import anywhere (grep `from 'zod'` = 0)
- What is happening: Any base64 JSON with a `version` and `guestId` is accepted and persisted, including out-of-range stats, huge inventories, or malformed `progression` that later code assumes exists.
- Why it matters: Save import is the one untrusted ingress; without validation it is both a cheat vector and a crash/corruption vector.
- User / business impact: Corrupt imports can break the game; trivial save editing undermines any economy.
- Security / privacy / reliability impact: Integrity/robustness; no cross-user data exposure (local-only).
- Recommended fix: Define a zod schema for `GameSave`/`BuddyState`/`InventoryState`, validate in `importSave` and `loadGame`, clamp ranges, and reject unknown/malformed fields.
- Suggested validation: Unit tests rejecting malformed/hostile saves and accepting a valid round-trip.
- Owner suggestion: frontend
- Effort estimate: M
- Dependencies: DATA-P1-002
- Status: open

### Finding ID: SEC-P2-002 - No HTTP security headers or Content-Security-Policy configured

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `next.config.js` — only `reactStrictMode`, `output`, `images`; no `headers()`
  - `app/layout.tsx` — no CSP meta
- What is happening: The app ships without CSP, `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`/frame-ancestors, or HSTS.
- Why it matters: Defense-in-depth is absent; any future third-party script or markup injection has fewer barriers, and the app can be framed.
- User / business impact: Minor for a static game; becomes relevant as the app grows.
- Security / privacy / reliability impact: Hardening gap.
- Recommended fix: Add `headers()` in `next.config.js` (or host config) with a restrictive CSP allowing self + Google Fonts, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, frame-ancestors 'none'.
- Suggested validation: Fetch response headers in a build/preview and assert presence; CSP report-only trial.
- Owner suggestion: platform
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SEC-P3-001 - Guest identity uses non-cryptographic randomness and is predictable

- Severity: P3
- Confidence: High
- Area: SEC
- Evidence:
  - `components/hatch/HatchFlow.tsx` line 17 — `'guest-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)`
  - `lib/storage/autosave.ts` line 12 — same pattern
- What is happening: `guestId` combines a timestamp with ~4 base36 chars of `Math.random`.
- Why it matters: `guestId` is not a security boundary today (no server), but if it ever keys cloud rows or migration, a predictable id is unsafe.
- User / business impact: Future account-migration risk.
- Security / privacy / reliability impact: Low today.
- Recommended fix: Use `crypto.randomUUID()` and persist the id in its own IndexedDB key.
- Suggested validation: Test id format and persistence across reload.
- Owner suggestion: frontend
- Effort estimate: S
- Dependencies: ARCH-P2-002
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Hostile/corrupt save import | P2 | Medium | Medium | SEC-P2-001 | zod validation |
| Missing security headers | P2 | High | Low | SEC-P2-002 | add headers |
| Predictable guest id | P3 | Low | Low | SEC-P3-001 | crypto UUID |

## Recommendations

### Immediate / Release Blocking
- None at this commit (guest-only, no server data).

### This Week
- Add zod validation for load/import.
- Add security headers.

### This Month
- Harden guest id and persist it.

### Later / Platform Evolution
- Implement server authority + RLS before accounts (ARCH-P1-001).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| zod-validate saves | integrity | `lib/storage/indexeddb.ts`, new `lib/storage/schema.ts` | unit tests |
| Add headers | hardening | `next.config.js` | header assertions |
| crypto.randomUUID | future-proof id | `HatchFlow.tsx`, `autosave.ts` | unit test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Save schema validation | P2 | frontend | M | DATA |
| Security headers/CSP | P2 | platform | S | none |
| Guest id hardening | P3 | frontend | S | none |

## Suggested Tests

- Unit: `importSave` rejects missing fields, wrong types, out-of-range stats.
- Header test via Next config preview.
- Fuzz malformed base64/JSON.

## Suggested Documentation Updates

- `SECURITY.md` stating guest-only trust model and no-secrets policy.
- Note the CSP and font-origin allowlist.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Will accounts/Supabase ship? | turns ARCH-P1-001 into a security gate | roadmap |
| Self-host fonts? | removes third-party origin/privacy | design |

## Appendix

- Secret scan result: no live secrets. Matches were prose only (`data/personalities.ts` flavour text, prompt-pack checklists).
- Tenancy/RLS/IDOR/SSRF/mass-assignment: **not applicable** — no server, no multi-tenant data at this commit.
