# Analytics, Tracking, and Privacy Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (mct-portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11
- Auditor: domain subagent (area AN, prompt 39)
- Area code: AN
- Output path: `docs/audits/repo-deep-dive/{run}/39_analytics_tracking_privacy.md` (this run: `_domains/39_analytics_tracking_privacy_body.md`)
- Scope limitations: read-only static analysis. No running stack, no Supabase project, no browser session. Production environment exercise (Vercel env, droplet `.env`) was not observable from the repository; wherever that matters it is marked `unverified`.

## Scope

Reviewed (all at `8d299b8d`):

- Analytics scripts and third-party embeds: `apps/web/app/(public)/layout.tsx` (GA4 + Tawk.to), CSP nonce plumbing in `apps/web/middleware.ts`.
- First-party event tracking: `apps/web/lib/catalog/analytics.ts`, `packages/sdk/src/analytics.ts`, `apps/api/src/routes/analytics.ts`, `supabase/migrations/5302106_store_analytics.sql`, `supabase/migrations/5302434_anon_privilege_least_privilege.sql`.
- Visitor tracking / lead tracking: `apps/api/src/routes/public.ts`, `apps/web/components/marketing/ContactForm.tsx`, `apps/web/components/store/IntakeFormRenderer.tsx`, `apps/api/src/lib/bot-detection.ts`, `docs/VISITOR_ALERTS.md`.
- Consent and opt-in/out: contact/intake consent checkboxes, `apps/api/src/middleware/csrf.ts` (tracking path), privacy policy page.
- Retention: `apps/worker/src/tasks/retention.ts`, `apps/worker/src/tasks/public-interaction-retention.ts`, `apps/worker/src/main.ts`, `apps/worker/src/schedule-config.ts`.
- Error telemetry: `apps/api/src/lib/sentry.ts`, `apps/web/instrumentation-client.ts`, `apps/web/sentry.server.config.ts`, `apps/web/sentry.edge.config.ts`, `apps/api/src/lib/logger.ts`.
- Governance/docs: `docs/modules/analytics.md`, `apps/web/lib/catalog/data/analytics-events.json`, `docs/MARKETING_SITE_INTEGRATION.md`, `docs/ENVIRONMENT_VARIABLES.md`, privacy page.
- Tests: `apps/api/src/__tests__/analytics.test.ts`, `apps/api/src/__tests__/csrf.test.ts`, `apps/web/__tests__/lib/catalog/analytics.test.ts`, `apps/web/__tests__/app/(admin)/admin/store/analytics/page.test.tsx`.

Not reviewed / explicitly out of scope for this domain: tenant-scoping of admin analytics reads and the undefined `get_analytics_summary` RPC (already re-verified by domains 06/25 this run — see cross-references), search-query analytics (domain 31), general data-retention ownership (domain 07), RLS internals (domain 37).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/web/app/(public)/layout.tsx:11,49,58-78` | Source | GA4 and Tawk.to loading, consent gating | Both embeds unconditional on env presence |
| `apps/web/middleware.ts:58-96` | Source | CSP nonce for third-party scripts | `script-src 'self' 'nonce-...' 'strict-dynamic'`; scripts receive `x-nonce` |
| `apps/api/src/routes/analytics.ts:13-91` | Source | Public track + admin list/summary endpoints | Stores IP/UA; no consent; calls undefined RPC |
| `apps/web/lib/catalog/analytics.ts:15-32` | Source | Browser tracking helper | No CSRF header; zero call sites |
| `packages/sdk/src/analytics.ts:31-47`, `packages/sdk/src/client.ts:149-185` | Source | SDK tracking + CSRF handling | SDK sends CSRF when host provides it |
| `apps/api/src/middleware/csrf.ts:40-89` | Source | CSRF gate on tracking POST | `/api/v1/analytics/track` not exempt |
| `supabase/migrations/5302106_store_analytics.sql:1-25` | Migration | Analytics table + RLS | ip_address/user_agent; anon INSERT policy; no org id |
| `supabase/migrations/5302434_anon_privilege_least_privilege.sql:73` | Migration | Anon write allow-list | Grant INSERT on store_analytics_events to anon |
| `apps/api/src/routes/public.ts:47-259` | Source | Visitor init + lead submit data flows | ip-api.com over HTTP; Teams/JSM forwarding with IP/UA |
| `apps/web/components/marketing/ContactForm.tsx:43-51,313-333` | Source | Pre-consent tracking + consent UI | init fires on mount; consent gates submit only |
| `apps/web/components/store/IntakeFormRenderer.tsx:43-46,244-264` | Source | Store intake tracking + consent | Same pattern |
| `apps/worker/src/tasks/retention.ts:129-135` | Source | Retention coverage | audit_logs + notifications only |
| `apps/worker/src/tasks/public-interaction-retention.ts:5-24` | Source | 90-day visitor retention | Pattern store analytics lacks |
| `apps/api/src/lib/sentry.ts`, `apps/web/instrumentation-client.ts`, `apps/web/sentry.server.config.ts` | Source | Error telemetry config | Minimal init; no scrub callback; no replay |
| `docs/modules/analytics.md:9,13,28` | Doc | Analytics contract | Claims "no PII" and live tracking |
| `apps/web/lib/catalog/data/analytics-events.json:3-53` | Data | Event registry + privacy rules | 20 event names; rules say hash/omit IP/UA |
| `apps/web/app/(public)/privacy/page.tsx:19-110` | Doc | Policy: collection, vendors, retention, rights | No cookie/opt-out section; no first-party stores |
| `docs/MARKETING_SITE_INTEGRATION.md:20-21`, `docs/ENVIRONMENT_VARIABLES.md:15-16` | Doc | Vendor IDs and env wiring | GA/Tawk IDs recorded as in use |
| `.github/workflows/deploy-do.yml:330-341`, `infra/digitalocean/docker-compose.yml:186-194` | Config | Web build/deploy env | GA/Tawk IDs not delivered |

## Verification Performed

All commands read-only, run against `/tmp/opencode/mct-audit-target` @ `8d299b8d`.

| Command | Observed result |
|---|---|
| `git log --oneline -3` | HEAD is `8d299b8d Merge PR #168: promote develop to main` (clean worktree) |
| `grep -rn "gtag\|googletagmanager" apps/web --include="*.ts" --include="*.tsx"` | Only `apps/web/app/(public)/layout.tsx:61,66`; no `gtag('consent', ...)` anywhere |
| `grep -rni "cookie-banner\|cookie consent\|cookieConsent\|doNotTrack\|do-not-track\|dnt" apps/web apps/api packages` | Zero hits — no banner, no DNT handling |
| `grep -rn "consent" apps/web --include="*.ts" --include="*.tsx"` | Only the contact/intake checkboxes and testimonial seed flags; no analytics consent |
| `grep -rn "store_analytics" apps/api/src apps/worker apps/web/app` | Writer only at `apps/api/src/routes/analytics.ts:32`; no worker retention reference |
| `grep -rn "get_analytics_summary" supabase apps` | Only the caller `apps/api/src/routes/analytics.ts:84` — still no migration definition (owned by domain 06; not duplicated) |
| `git log --oneline 9c0b88c..8d299b8d -- "apps/web/app/(public)/layout.tsx" "apps/api/src/routes/analytics.ts" "apps/web/lib/catalog/analytics.ts" "apps/web/app/(public)/privacy/page.tsx"` | Empty — no analytics/consent files changed since the previous run |
| `git log --oneline 9c0b88c..8d299b8d --all --grep="consent" -i` | Empty — no consent work landed in the delta |
| `grep -rn "\btrack\b" apps/web/app apps/web/components apps/web/lib` | No call site of `track()` outside its own module |
| `grep -rn "api/v1/analytics" apps/web packages/sdk` | Helper fetch + SDK methods only; no page calls the API |
| `grep -rn "replayIntegration\|Replay" apps/web apps/api/src` | No session replay; matches are idempotency/webhook "replay" wording only |
| `grep -rni "hotjar\|mixpanel\|posthog\|fullstory\|clarity\|matomo\|plausible\|fbq(\|amplitude" apps packages` | Zero hits — no other third-party analytics/pixels |
| `git ls-files \| grep -i "analytics\|privacy\|consent\|cookie"` | `docs/modules/analytics.md`, the registry, the route/helper; no consent/governance doc |
| `sed -n '330,341p' .github/workflows/deploy-do.yml` | Web build args: API URL, version, SHA, build time, test-accounts, Turnstile — no GA/Tawk IDs |
| `grep -n "GA_ID\|TAWKTO" infra/ .github/workflows/` | Zero hits — IDs not delivered by the deploy pipeline |

Headline-claim checks (shared-rules sampling duty):

- "Public events are tracked anonymously (no PII)" (`docs/modules/analytics.md:9`) — **unsupported**: the route stores IP/UA (`analytics.ts:43-44`).
- "POST /analytics/track — anonymous event tracking from the storefront" is a working feature (`docs/modules/analytics.md:13`) — **partially supported**: endpoint + tests exist, but no caller and the browser helper cannot pass CSRF → not reproducible end-to-end.
- "GA + Tawk.to fire on every marketing page visit" (`docs/MARKETING_SITE_INTEGRATION.md:269`) — **code path supported, production exercise unverified** (IDs are not delivered by the deploy pipeline).
- "The 90-day retention task bounds table growth" for `public_interactions` (`docs/VISITOR_ALERTS.md`) — **supported** (`public-interaction-retention.ts:5-24`, scheduled in `main.ts:71-76`); note there is no equivalent for `store_analytics_events`.

## Executive Summary

Strengths: the public marketing layout is the only place third-party analytics load (admin/portal layouts load none); the scripts are env-gated, CSP-nonce'd, and Tawk.to is `crossOrigin="anonymous"`; there is no session replay, no tracking pixel, and no analytics SDK beyond GA4 + Tawk.to; the event registry documents 20 events and privacy rules; `public_interactions` has a 90-day purge and bot filtering; the contact and intake forms gate submission on a consent checkbox; the API logger redacts PII fields.

Risks: (1) GA4 and Tawk.to load with no consent or opt-out, and there is no consent-mode signalling; (2) the public analytics endpoint stores visitor IP/user-agent and arbitrary metadata in plaintext, contradicting the module doc and the registry's own privacy rules; (3) storefront event capture is dead — no call sites and a CSRF gate the helper cannot pass; (4) first-party analytics rows have no retention; (5) contact-page visitor tracking sends the visitor IP to ip-api.com over plaintext HTTP before consent; (6) consent is never recorded and the privacy policy omits first-party tracking stores and opt-out.

Recommended next actions (ordered): fix the no-PII contract or the code; add consent mode + a cookie/opt-out; wire or remove storefront capture; add analytics retention; move the geo lookup to HTTPS and behind consent; persist consent and extend the policy.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| GA4 embed | `apps/web/app/(public)/layout.tsx:58-69` | Marketing page analytics | Implemented, unconditional on env | Consent gap | No consent mode |
| Tawk.to embed | `apps/web/app/(public)/layout.tsx:71-78` | Live chat | Implemented, unconditional on env | Consent gap | Third-party cookies |
| Public track API | `apps/api/src/routes/analytics.ts:27-61` | Storefront event capture | Implemented; no caller; CSRF-blocked for browsers | PII + dead feature | Stores IP/UA |
| Admin list API | `apps/api/src/routes/analytics.ts:64-78` | Recent 500 events | Implemented, `select("*")` | PII exposure | Scoping covered by domain 06 |
| Summary API | `apps/api/src/routes/analytics.ts:81-91` | Aggregates via RPC | Broken (RPC undefined) | Functional | Domain 06 re-verified |
| Browser helper | `apps/web/lib/catalog/analytics.ts` | track() + in-memory log | Dead code | Coverage | No CSRF header, no callers |
| SDK analytics | `packages/sdk/src/analytics.ts:31-47` | track/list/summary client | Implemented | — | Sends CSRF when supplied |
| Event registry | `apps/web/lib/catalog/data/analytics-events.json` | Event names/shape/privacy rules | Present | Doc vs code drift | Rules contradict the API |
| Analytics table | `supabase/migrations/5302106_store_analytics.sql` | Event storage | No org id, no retention; anon INSERT | PII, integrity | IP/UA columns |
| Anon grant | `supabase/migrations/5302434...sql:73` | Public insert allow-list | Present | Integrity | Bypasses API validation |
| Visitor init | `apps/api/src/routes/public.ts:47-125` | Visitor session + alerts | Implemented | Pre-consent, HTTP geo | 90-day retention |
| Lead submit | `apps/api/src/routes/public.ts:127-259` | Lead + Teams/JSM forwarding | Implemented | PII to vendors | Consent not stored |
| Consent UI | `ContactForm.tsx:313-333`, `IntakeFormRenderer.tsx:244-264` | Submit gate | Implemented | No record | Client-side only |
| Error telemetry | `apps/api/src/lib/sentry.ts`, web sentry configs | Error capture | Implemented, minimal | Scrubbing/disclosure | No replay |
| Retention | `apps/worker/src/tasks/retention.ts`, `public-interaction-retention.ts` | Purges | audit_logs + notifications + public_interactions | Analytics uncovered | — |
| Admin UI | `apps/web/app/(admin)/admin/store/analytics/page.tsx` | Registry display | Static registry only | Misleading | No API data |
| Module doc | `docs/modules/analytics.md` | Contract | Stale vs code | Documentation | "No PII" claim false |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Analytics scripts | 2 | `layout.tsx:58-69` | No consent gate/mode | Add consent mode + banner |
| Tracking pixels | 5 | grep: none | — | Keep absent |
| Events | 2 | `analytics.ts:13-61`; registry | No caller; PII; CSRF-blocked | Wire or remove; fix payload |
| Product analytics | 1 | registry + dead helper | No data ever captured | E2E + wiring |
| Error telemetry | 3 | sentry configs | No scrub/disclosure | beforeSend + policy |
| Session replay | 5 | grep: none | — | Keep absent |
| Cookie banner | 0 | grep: none | Absent | Add banner/opt-out |
| Consent | 1 | form checkboxes only | Not recorded; no analytics consent | Persist + consent mode |
| Opt-in/out | 0 | privacy page | No opt-out | Add opt-out |
| User/tenant IDs | 2 | `store_analytics_events` has no org id; anonymous_id | No tenant/purpose model | Decide model, document |
| Sensitive payloads | 1 | `analytics.ts:22,43-44` | IP/UA + unbounded metadata | Hash/omit; schema |
| Page views | 1 | GA only, ungated | First-party page views absent | Decide first-party vs GA |
| Retention | 2 | `retention.ts`, `public-interaction-retention.ts` | Analytics store uncovered | Add retention task |

## Detailed Review

### Item: GA4 embed and consent mode

- Evidence: `apps/web/app/(public)/layout.tsx:58-69`; `apps/web/middleware.ts:58-96` (nonce).
- What it does: loads `gtag.js` after interactive and runs `gtag('config', ID)` for every public page when `NEXT_PUBLIC_GA_ID` is set.
- Missing controls: no `gtag('consent', 'default', ...)`, no opt-out, no banner.
- Risks: consent exposure in the EU/EEA/UK and California opt-out expectations; the privacy policy describes GA as active.
- Recommended improvement: consent-mode default-denied + banner; document opt-out.
- Suggested tests: unit test asserting the consent script precedes config when a consent flag is false; E2E asserting no GA request before accept.
- Suggested docs: privacy policy cookie section; `docs/modules/analytics.md`.

### Item: Tawk.to embed

- Evidence: `layout.tsx:71-78`.
- Same class as GA: loads on every public page whenever the ID is configured, with no consent gate.

### Item: Public track endpoint and payload

- Evidence: `apps/api/src/routes/analytics.ts:13-61`; `docs/modules/analytics.md:9,28`; `analytics-events.json:37-43`.
- What it does: validates `event` plus optional ids/metadata and inserts a row with `ip_address` and `user_agent` from the request.
- Missing controls: consent, PII minimisation, typed metadata, tenant/purpose model.
- Risks: PII retention without basis; documentation contradicts code.

### Item: Storefront capture wiring (CSRF)

- Evidence: `apps/web/lib/catalog/analytics.ts:15-32`; `apps/api/src/middleware/csrf.ts:81-89`; `apps/api/src/app.ts:150`.
- What it does: helper posts without CSRF header; no component calls it.
- Risks: product analytics is not captured; docs and dashboard cards overstate coverage.

### Item: Visitor alerts (`/public/init`)

- Evidence: `apps/api/src/routes/public.ts:47-125`; `ContactForm.tsx:43-51`; `docs/VISITOR_ALERTS.md`.
- What it does: stores IP/UA/platform/referrer, looks up geo via `http://ip-api.com`, optionally alerts Teams.
- Missing controls: consent, HTTPS for the third-party lookup.
- Mitigations already present: bot filter, 30-min alert dedupe, 90-day retention.

### Item: Consent recording

- Evidence: `apps/web/app/(public)/contact/actions.ts:21-25`; `apps/api/src/routes/public.ts:13-24`.
- What it does: blocks submit without the checkbox, then drops the flag; API has no consent field.

### Item: Retention

- Evidence: `apps/worker/src/tasks/retention.ts:129-135`; `public-interaction-retention.ts:5-24`.
- What it does: purges audit_logs + notifications daily and public_interactions at 90 days; store analytics has no purge.

### Item: Error telemetry

- Evidence: `apps/api/src/lib/sentry.ts:8-13`; web sentry configs; `apps/api/src/lib/logger.ts:5-39`.
- What it does: sends errors/traces to Sentry when a DSN is set; no explicit PII scrubbing in the Sentry path; logger redaction is separate.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| AN-001 | Analytics scripts | `layout.tsx:58-78` | env-gated + nonce | No consent | P2 | Consent mode + banner |
| AN-002 | Tracking pixels | grep none | Absent | — | — | Keep absent |
| AN-003 | Events | `analytics.ts:13-61` | Zod + admin gate | PII; dead caller | P2 | Fix payload; wire/remove |
| AN-004 | Product analytics | registry, helper | Registry only | No capture | P2 | E2E + wiring |
| AN-005 | Error telemetry | sentry configs | DSN-gated | No scrub/disclosure | P3 | beforeSend + policy |
| AN-006 | Session replay | grep none | Absent | — | — | Keep absent |
| AN-007 | Cookie banner | grep none | Absent | No banner | P2 | Add banner/opt-out |
| AN-008 | Consent | form checkboxes | Submit gate | Not recorded; analytics not covered | P2 | Persist + consent mode |
| AN-009 | Opt-in/out | privacy page | Rights text only | No control | P2 | Add opt-out |
| AN-010 | User/tenant IDs | `5302106`; `anonymous_id` | anonymous_id only | No org/purpose model | P3 | Decide + document |
| AN-011 | Sensitive payloads | `analytics.ts:22,43-44` | none | IP/UA + free metadata | P2 | Hash/omit + schema |
| AN-012 | Page views | GA only | GA (ungated) | No first-party page views | P3 | Decide model |

## Findings

IDs are assigned by the aggregator; titles below match the JSON.

1. **Analytics has no consent-mode signalling and no documented event/retention governance** (P3, still-open — verification of prior `AN-P3-001`). Re-verified at `8d299b8d`: unchanged.
2. **Google Analytics and Tawk.to load on public pages with no cookie-consent or opt-out gate** (P2, still-open — verification of prior `PRIV-P2-001`, cross-listed from area PRIV). Re-verified at `8d299b8d`: unchanged.
3. **Analytics API stores visitor IP and user-agent in plaintext despite the documented no-PII contract** (P2, open). New.
4. **Storefront analytics capture is dead: the browser helper is never called and cannot pass the CSRF gate** (P2, open). New.
5. **First-party analytics events have no retention or purge path** (P2, open). New.
6. **Anonymous direct inserts to store_analytics_events bypass API validation, rate limits, and retention** (P3, open). New.
7. **Visitor-alert tracking collects IP/geo before consent and sends the visitor IP to ip-api.com over plaintext HTTP** (P2, open). New.
8. **Consent is not recorded and the privacy policy omits first-party tracking stores and opt-out mechanics** (P3, open). New.
9. **Error telemetry has no explicit PII scrubbing, retention, or vendor disclosure** (P3, open). New.

Cross-references (not duplicated): the undefined `get_analytics_summary` RPC and the tenant-scoping of admin analytics reads were re-verified by domain 06 (`06_security_authz_tenancy_audit.json`); the platform-wide store/analytics admin surface by domain 25; search-query analytics by domain 31; generic retention ownership by domain 07.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Consentless GA/Tawk.to on marketing pages | P2 | High (when IDs configured) | Regulatory complaint/loss of trust | `layout.tsx:58-78` | Consent mode + banner |
| Visitor IP/UA stored + arbitrary metadata | P2 | High (endpoint live) | Privacy exposure, doc contradiction | `analytics.ts:22,43-44` | Hash/omit, schema |
| Pre-consent IP transfer over HTTP to ip-api.com | P2 | High (contact page) | Interception + third-party disclosure | `public.ts:64`; `ContactForm.tsx:43-51` | HTTPS + consent gate |
| Analytics rows retained indefinitely | P2 | Medium | Storage-limitation breach | `retention.ts:129-135` | Retention task |
| Product analytics claimed but not captured | P2 | High | Bad business decisions | helper + CSRF | Wire/remove |
| Analytics poisoning via anon insert | P3 | Medium | Data integrity | `5302434:73` | Revoke grant |
| Consent not recorded | P3 | High | No accountability | `contact/actions.ts:25` | Persist consent |

## Recommendations

### Immediate / Release Blocking

- None. No P0/P1 was identified in this domain at `8d299b8d`.

### This Week

- Remove or hash `ip_address`/`user_agent` from the analytics insert and align `docs/modules/analytics.md` (finding 3).
- Switch the ip-api.com lookup to HTTPS or remove it; document the pre-consent tracking (finding 7).

### This Month

- Add consent-mode default-denied + a cookie banner/opt-out (findings 1, 2, 8).
- Wire `track()` (with CSRF) into storefront views or delete the dead surface and its docs (finding 4).
- Add `store_analytics_events` retention mirroring `public-interaction-retention` (finding 5).
- Persist consent (flag/timestamp/policy version) and extend the privacy policy (finding 8).

### Later / Platform Evolution

- Typed per-event metadata schema; DB-level constraints; revoke the anon INSERT grant (findings 3, 6).
- Sentry `beforeSend` scrubbing + vendor/retention disclosure (finding 9).
- Decide the tenant/purpose model for analytics (platform-wide vs per-org) with domain 06/25 follow-up.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Drop IP/UA columns from the insert | Removes plaintext visitor PII | `apps/api/src/routes/analytics.ts` | Unit test on insert payload |
| Add `gtag('consent', 'default', {denied})` before config | Signals consent-mode contract | `apps/web/app/(public)/layout.tsx` | E2E: no GA request pre-accept |
| Change geo URL to `https://ip-api.com` | Removes cleartext third-party transfer | `apps/api/src/routes/public.ts:64` | Grep + unit test |
| Add a retention task for the analytics table | Bounds retention | `apps/worker/src/tasks/*`, `main.ts` | Task unit test |
| Persist the consent flag | Accountability record | `public.ts` schema + `contact/actions.ts` | API test asserting stored consent |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Consent-mode + banner + opt-out | P2 | @web | M | Policy wording |
| Analytics payload minimisation + schema | P2 | API platform | S–M | Product decision on fields |
| Storefront capture wiring or removal | P2 | @web + API | M | CSRF decision |
| Analytics retention task | P2 | platform/backend | S | None |
| Anon insert grant removal | P3 | DB lead | S | Confirm API-only writes |
| Consent persistence + policy update | P3 | @web + privacy | M | Policy review |
| Sentry scrubbing/disclosure | P3 | platform/backend | S–M | None |

## Suggested Tests

- Unit: `analytics.track` insert never contains `ip_address`/`user_agent` (mock Supabase, assert payload).
- Unit: `track()` helper attaches `X-CSRF-Token` and the API accepts it (mount `csrfProtection` in the route test).
- Integration: `POST /api/v1/analytics/track` without a CSRF token returns 403 (documents current behavior) — or 200 if the path is deliberately exempted.
- Integration: `public.ts` geo lookup uses an HTTPS URL and is skipped when consent is absent (if gated).
- Worker: retention task purges `store_analytics_events` older than the cutoff and reports counts; cutoff boundary test.
- E2E: no GA/Tawk.to network request before consent accept; after accept, the requests fire.
- E2E: storefront page view lands a row visible via `GET /api/v1/analytics` (once wired).
- CI: a docs-contract check that `docs/modules/analytics.md` claims match the insert payload (or at least a review checklist).

## Suggested Documentation Updates

- `docs/modules/analytics.md` — replace the "no PII" claim; document payload, retention, consent behavior, and whether capture is live.
- `apps/web/app/(public)/privacy/page.tsx` — add a cookie/analytics section, opt-out instructions, first-party tracking stores (`store_analytics_events`, `public_interactions`) and their retention; add Sentry to the vendor list.
- New `docs/ANALYTICS_GOVERNANCE.md` (or extend a data-governance doc) — event catalog, purpose, retention, vendor list, consent state.
- `docs/VISITOR_ALERTS.md` — document the pre-consent tracking and the geo transport.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are `NEXT_PUBLIC_GA_ID` / `NEXT_PUBLIC_TAWKTO_ID` actually set on the deployed site (Vercel or droplet)? | Determines whether findings 1/2 are live or latent | Operator/Vercel env inspection (not in repo) |
| Is the storefront meant to capture first-party events, or is GA the only product analytics? | Decides whether finding 4 is a bug or dead code to delete | Product decision |
| Should analytics be platform-wide or per-tenant? | Resolves the scoping overlap with domains 06/25 | Product/architecture decision |
| Was ip-api.com ever evaluated as a data processor (DPA, data residency)? | Privacy compliance for the visitor IP transfer | Vendor records (not in repo) |
| Is the anon INSERT grant on `store_analytics_events` still needed given the API route exists? | Least-privilege decision for finding 6 | Confirm no direct-Supabase writer |

## Appendix

Raw command outputs are summarized in "Verification Performed". Key file excerpts (verbatim, read-only):

- `apps/web/app/(public)/layout.tsx:58-78` — the unconditional GA/Tawk.to blocks.
- `apps/api/src/routes/analytics.ts:27-61` — public track insert with `ip_address`/`user_agent`.
- `apps/api/src/routes/public.ts:64` — `http://ip-api.com/json/${cleanIp}`.
- `apps/worker/src/tasks/retention.ts:129-135` — purge list.
- `apps/web/lib/catalog/data/analytics-events.json:37-43` — privacy rules ("Hash or omit IP/user-agent if not needed").

No secrets were printed; all references are path:line only.
