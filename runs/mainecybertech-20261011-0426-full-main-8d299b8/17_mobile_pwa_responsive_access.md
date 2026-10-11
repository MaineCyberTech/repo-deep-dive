# 17_mobile_pwa_responsive_access — Prompt 17 - Mobile, PWA, and Responsive Access Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `17_mobile_pwa_responsive_access.md` (area MOB, prompt)

## Verification Performed

# Mobile, PWA, and Responsive Access Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: mainecybertech-20261011-0426-full-main-8d299b8
- Repository: MaineCyberTech/mainecybertech (read-only copy at `/tmp/opencode/mct-audit-target`)
- Branch: main
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent (MOB), static read-only analysis
- Area code: MOB
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/17_mobile_pwa_responsive_access.md`
- Scope limitations: no browser was launched, no device emulation, no build, no `pnpm install`; everything below is source/config/test evidence at `8d299b8d`. Rendering-dependent conclusions (clipping, zoom, overlap) are marked with confidence. Previous-run register re-checked for Area `MOB` (one row) plus the service-worker aspect of `NOTIF-P2-001`.

## Scope

Reviewed: viewport/meta handling, responsive layout utilities, mobile navigation (marketing/portal/admin/store), touch targets, mobile forms, dialogs/tables, auth/dashboard/admin mobile headers, PWA manifest, service worker, offline fallback, install prompt, push, icons, cache strategy, update flow, background sync, mobile E2E and touch accessibility.

Not reviewed: native app wrappers (none exist), iOS/Android store packaging (none), real-device rendering, network-throttled offline behaviour, and the notification delivery backend (owned by `NOTIF`, see `30_notification_email_push_delivery_audit`).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/web/app/layout.tsx:19-28` | Config | Root metadata: icons, manifest, themeColor | No `viewport` export |
| `apps/web/app/manifest.ts:1-20` | PWA | The generated manifest (SVG-only icon) | Added by 62de9c1b |
| `apps/web/public/manifest.json`, `apps/web/public/manifest.webmanifest` | PWA | Duplicate static manifests | Content identical (trailing newline only) |
| `apps/web/public/sw.js:1-53` | PWA | Service worker source | Never registered |
| `apps/web/public/favicon.svg`, `favicon.ico` | Icons | App icons | `.ico` contains SVG bytes |
| `apps/web/next.config.mjs:23-33` | Config | Same-origin `/api/v1/*` rewrite into the SW scope | Cache-risk vector |
| `apps/web/middleware.ts:152-154` | Config | Matcher does not exclude `/sw.js` or the manifest | Non-blocking |
| `apps/web/components/layout/SidebarShell.tsx:70-151` | UI | Portal/admin mobile drawer + toggle | Focus trap, Escape, aria |
| `apps/web/components/store/StoreLayoutShell.tsx:27-99` | UI | Store mobile drawer | Focus trap, Escape, aria |
| `apps/web/components/marketing/MarketingHeader.tsx:74-146` | UI | Public mobile nav (hamburger) | 28×16px button |
| `packages/ui/src/styles.css:1-201` | CSS | Shared utilities, `cyber-container`, `cyber-main`, breakpoints | 1 media query (reduced motion) |
| `apps/web/tailwind.config.ts` | Config | Tailwind content globs; default breakpoints | No custom breakpoints |
| `apps/web/playwright.config.ts:28-40` | Test | Only a Desktop Chrome project | No mobile project |
| `apps/web/e2e/a11y.spec.ts:1-108` | Test | 25-route axe gate, WCAG 2.2 AA tags | Desktop viewport only |
| `.github/workflows/e2e.yml`, `a11y-breadth.yml` | CI | E2E/a11y jobs install chromium only | No mobile device run |
| `packages/ui/src/components/Dialog.tsx:94-149` | UI | Shared dialog | No max-height/scroll |
| `apps/web/components/portal/SupportCenterClient.tsx:216-224` | UI | Ticket modal without max-height | Clipping risk |
| `apps/web/app/(admin)/admin/store/products/ProductForm.tsx:76-97` | UI | Counter-example: `max-h-[90vh] overflow-y-auto` | Good pattern |
| `apps/web/components/store/QuoteBuilderClient.tsx:290-355` | Forms | Public quote funnel, `text-sm` inputs | iOS zoom |
| `apps/web/components/store/IntakeFormRenderer.tsx:157-158` | Forms | Intake widget inputs, `text-sm` | iOS zoom |
| `docs/GAP_ANALYSIS.md:45,67` | Docs | Mobile gap and PWA priority statements | Partly stale |
| `docs/WEB_UI_CONVENTIONS.md:85-93` | Docs | A11y gate scope | 25 routes, desktop |

## Verification Performed

All commands read-only against `/tmp/opencode/mct-audit-target` at `8d299b8d`.

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse HEAD` | Command | Bind the audit | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` |
| `grep -rn "navigator\.serviceWorker\|serviceWorker\.register\|workbox" apps packages scripts infra .github` + `grep -rn "sw\.js" apps packages` | Command | Is the SW registered? | **No matches** in `apps/**`/`packages/**`; only committed audit docs mention it |
| `git log --all --oneline -S "navigator.serviceWorker" -- apps/web` | Command | History check | **Empty** — no registration ever existed |
| `git log --oneline -1 -- apps/web/public/sw.js` | Command | Provenance | Added in `f02ec685` (2026-07-30), never wired |
| `git cat-file -e 6286137:apps/web/public/sw.js` | Command | Prior-audit claim check | SW **existed** at 6286137/9c0b88c — the NOTIF audit's "no sw.js" evidence was wrong |
| `diff apps/web/public/manifest.json apps/web/public/manifest.webmanifest` | Command | Duplication | Differ only by a trailing newline |
| `file apps/web/public/favicon.ico apps/web/public/favicon.svg` | Command | Icon formats | Both report "SVG Scalable Vector Graphics image" |
| `git diff --stat 9c0b88c 8d299b8d -- apps/web/app/manifest.ts apps/web/public/ apps/web/app/layout.tsx` | Command | Re-verify MOB-P3-001 | **Empty** — unchanged since the previous run |
| Python scan of 382 `<input>/<select>/<textarea>` tags | Command | Font-size/zoom risk | 174 `cyber-input`, 129 `text-sm`, 28 `text-xs`, 51 unspecified |
| `grep -rn "<table" apps/web` (24 matches) + wrapper spot-checks | Command | Table overflow | All 24 are inside `overflow-x-auto`, or `hidden md:block` with mobile cards |
| `grep -roh "sm:\|md:\|lg:\|xl:" apps/web` | Command | Responsive coverage | 683 breakpoint utilities (sm 364, md 150, lg 128, xl 41) |
| `grep -rn "beforeinstallprompt\|pushManager\|vapid\|showNotification" apps packages` | Command | Install prompt / push | No matches |
| Next.js v15.5.27 `resolve-metadata.ts` (fetched source) | External | themeColor handling | `case 'themeColor'` adds a warning only; the value is **not** emitted |
| MDN "Making PWAs installable" | External | Installability criteria | Chromium requires 192px **and** 512px manifest icons; SW not required |

## Executive Summary

The web app is **mobile-shaped but not mobile-verified**. Responsive implementation is broad and deliberate: 683 Tailwind breakpoint utilities, three mobile drawers (portal/admin/store) with focus traps and Escape handling, mobile card fallbacks for data tables, a mobile-only sticky CTA, a skip link, and live-region announcements. All 24 `<table>`s sit inside horizontal-scroll wrappers or are replaced by cards below `md`.

The PWA story is the weak half. The manifest declares a single SVG icon and does not meet Chromium's installability criteria (192px + 512px icons required), no `apple-touch-icon` exists, and `apps/web/public/favicon.ico` contains SVG bytes. A service worker file exists but is **never registered** anywhere in the repo, so offline support, install prompt, and update flow are all inert; if it were registered as written, its fetch handler would cache every same-origin GET 200 — including authenticated `/api/v1/*` responses proxied through the web app — in persistent Cache Storage with no allowlist, no `Cache-Control` respect, and no logout purge.

Two mobile UX defects are systemic: ~41% of form controls render below 16px and will trigger iOS Safari focus zoom, and several modal dialogs have no max-height or vertical scroll, so long forms can be unreachable on a phone. No mobile-viewport E2E or a11y coverage exists (Desktop Chrome only), which is why none of this is caught by CI.

Next actions: (1) decide the PWA scope — either delete `sw.js` + duplicate manifests or implement a safe SW (static allowlist, API bypass, offline page, update flow); (2) add a 16px mobile input floor; (3) adopt one scroll-safe modal shell; (4) add a mobile Playwright project + viewport a11y scan.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Viewport meta | `apps/web/app/layout.tsx` (no `viewport` export) | Mobile scaling | Framework default applies | Low | `themeColor` is in `metadata` and ignored |
| Theme colour | `apps/web/app/layout.tsx:27`, `manifest.ts:11` | Brand chrome | Ignored in metadata; manifest only | Low | Verified against Next.js 15.5.27 source |
| Responsive utilities | `packages/ui/src/styles.css:22-160`, app components | Layout scaling | Broad (683 breakpoints) | Low | `cyber-container`, `cyber-main`, grids |
| Marketing nav | `apps/web/components/marketing/MarketingHeader.tsx` | Public mobile nav | Implemented | Medium | 28×16px hamburger; no focus trap |
| Portal/admin nav | `SidebarShell.tsx` + `Portal/AdminSidebarContent` | Drawer + desktop sidebar | Implemented | Low | Focus trap, Escape, popstate close |
| Store nav | `StoreLayoutShell.tsx` | Drawer | Implemented | Low | Focus trap via `use-focus-trap` |
| Tables | 24 `<table>`s | Data display | All wrapped or card-fallback | Low | `cyber-table-responsive` class unused |
| Dialogs | `Dialog.tsx`, `ConfirmDialog.tsx`, ad-hoc modals | Modal flows | Mixed | Medium | Several lack max-height/scroll |
| Forms | 382 controls | Data entry | Mixed | Medium | 157 with <16px font |
| Manifest | `app/manifest.ts` + 2 public copies | PWA install | SVG-only, triplicated | Medium | Fails Chromium criteria |
| Icons | `public/favicon.*` | Brand/install icons | SVG only; `.ico` mislabelled | Medium | No PNG/maskable/apple icons |
| Service worker | `public/sw.js` | Offline/caching | **Never registered** | Medium | Dead code; unsafe if enabled as-is |
| Offline fallback | `sw.js:47-50` | Offline UX | Plain-text 503 | Low | No offline page |
| Install prompt | (absent) | Home-screen install | Absent | Low | No `beforeinstallprompt` handler |
| Push | (absent) | OS notifications | Absent | Low | Owned by `NOTIF-P2-001` |
| Background sync | (absent) | Deferred actions | Absent | Low | No `sync.register` |
| Update flow | (absent) | SW updates | Absent | Low | No registration, no update UI |
| Mobile E2E | `playwright.config.ts` | Regression safety | Desktop Chrome only | Medium | No mobile project |
| Mobile a11y | `e2e/a11y.spec.ts` | Touch/target checks | Desktop viewport | Medium | No viewport override |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Viewport | 3 | No override; Next default `width=device-width, initial-scale=1`; `global-error.tsx:26` explicit | No explicit `viewport` export; themeColor ignored | `export const viewport = { themeColor: "#059669" }` |
| Responsive layouts | 4 | 683 breakpoint utilities; drawers; mobile cards; sticky CTA | No automated mobile proof | Add mobile Playwright project |
| Mobile nav | 4 | 3 drawers with focus traps (`SidebarShell`, `StoreLayoutShell`, `MarketingHeader`) | Small close/hamburger targets; marketing menu lacks trap | Enlarge hit areas; reuse `useFocusTrap` |
| Touch targets | 2 | 9 controls measured 20–36px (see finding) | No 44px policy; no mobile target-size test | Add min 44px hit areas + test |
| Mobile forms | 2 | 129 `text-sm` + 28 `text-xs` controls of 382 | iOS focus zoom on public funnels | 16px mobile input floor |
| Mobile dialogs/tables | 3 | All tables scroll or card-ify; `ProductForm` scroll-safe | `SupportCenterClient`, doc-center create, `PromoForm`, `CategoryForm` clip | One scroll-safe modal shell |
| Auth/dashboard/admin mobile | 3 | Responsive login/MFA; wrapping headers; drawer nav | Notification dropdown clips ≤375px; admin header density | Mobile-position the dropdown; test 320–375px |
| PWA manifest | 2 | `manifest.ts` valid JSON, name/short_name/display/start_url | SVG-only icon; 3 sources; fails installability | One source + 192/512/maskable icons |
| Service worker | 1 | `sw.js` present | Never registered; unsafe cache strategy | Delete or fix + register |
| Offline fallback | 1 | `sw.js:47-50` plain-text 503 | No offline page; no registration | Offline HTML route + precache |
| Install prompt | 0 | No `beforeinstallprompt` handler anywhere | Cannot install | Add install affordance after manifest fix |
| Push notifications | 0 | No VAPID/pushManager/`showNotification` | No OS-level alerts | Owned by `NOTIF-P2-001` |

## Detailed Review

### Item: Viewport and theme colour

- Evidence: `apps/web/app/layout.tsx:19-28`; `apps/web/app/global-error.tsx:24-27`.
- What it does: relies on the Next.js default viewport meta; declares `themeColor` inside `metadata`.
- How it appears to work: Next.js 15.5.27 emits the default `width=device-width, initial-scale=1`; `metadata.themeColor` hits the "Unsupported metadata" switch case and is dropped with a build warning (source-verified).
- Current controls: framework default; explicit viewport only in the standalone error document.
- Missing controls: explicit `viewport` export; theme-color meta; `viewportFit: "cover"`/safe-area handling.
- Risks: browser chrome colour mismatch; build warning noise.
- Recommended improvement: `export const viewport: Viewport = { themeColor: "#059669" };` in `layout.tsx`.
- Suggested tests: snapshot the rendered `<head>` for `meta[name=theme-color]` and `meta[name=viewport]`.
- Suggested docs: `docs/WEB_UI_CONVENTIONS.md` "Mobile & viewport".

### Item: Responsive layouts and navigation

- Evidence: `packages/ui/src/styles.css:22-160`; `SidebarShell.tsx:70-151`; `StoreLayoutShell.tsx:27-99`; `MarketingHeader.tsx:74-146`; `cyber-container`/`cyber-main`.
- What it does: fluid containers, `sm/md/lg` grids, `lg` sidebar ↔ drawer switch, sticky mobile CTA, scrollable subnavs (`AdminSubnav.tsx:35-36`, `PortalSubnav.tsx:34-35`).
- How it appears to work: Tailwind default breakpoints; drawer uses `lg:hidden` + fixed aside.
- Current controls: focus trap, `aria-modal`, Escape, focus restore, popstate close.
- Missing controls: marketing menu has no focus trap; no `aria-controls` on the hamburger.
- Risks: low; drawer patterns are solid.
- Recommended improvement: reuse `useFocusTrap` in `MarketingHeader`; add `aria-controls`.
- Suggested tests: Playwright mobile project: open/close each drawer, assert focus containment and Escape.
- Suggested docs: extend `docs/WEB_UI_CONVENTIONS.md` with the drawer contract.

### Item: PWA manifest and icons

- Evidence: `apps/web/app/manifest.ts:12-18`; `apps/web/public/manifest.json`; `apps/web/public/manifest.webmanifest`; `apps/web/app/layout.tsx:23-26`; `apps/web/public/favicon.ico`.
- What it does: one metadata-route manifest plus two static copies; a single `sizes:"any"` SVG icon.
- How it appears to work: `/manifest.webmanifest` is claimed by both the metadata route and a public file; `layout.tsx` links it explicitly.
- Current controls: valid JSON, `name/short_name/start_url/display/theme_color/background_color`.
- Missing controls: 192/512 PNG, maskable, apple-touch-icon, single source, `purpose`.
- Risks: not installable in Chromium (icon criteria); iOS home-screen icon missing; source drift.
- Recommended improvement: keep `app/manifest.ts`, add PNG + maskable icons, delete both public manifests, add `apple-touch-icon`.
- Suggested tests: assert the built manifest parses and contains 192/512 entries; Lighthouse installability audit in CI.
- Suggested docs: `docs/PWA.md` describing the manifest/icon contract.

### Item: Service worker, offline and cache

- Evidence: `apps/web/public/sw.js:1-53`; `apps/web/next.config.mjs:23-31`; registration grep; `git log -S`.
- What it does: precaches 8 routes, network-first fetch with runtime caching of every 200 GET, plain-text offline fallback, `skipWaiting`/`clients.claim`.
- How it appears to work: nothing calls `navigator.serviceWorker.register`, so none of it runs.
- Current controls: versioned cache name `mct-cache-v1`; old-cache deletion on activate.
- Missing controls: registration, allowlist, API bypass, `Cache-Control` respect, logout purge, offline page, update UX, quota handling.
- Risks: latent privacy exposure if registered as-is (authenticated API/HTML cached persistently); no offline capability today.
- Recommended improvement: either delete `sw.js` (and record the product decision) or rewrite with a static-asset allowlist, `/api/` bypass, `no-store` respect, an offline HTML fallback, and `Cache-Control: no-cache` for `/sw.js`.
- Suggested tests: unit-test the fetch router with mocked caches; E2E offline reload of `/portal/dashboard`; assert API responses are never cached.
- Suggested docs: `docs/PWA.md` + an explicit product decision record.

### Item: Mobile forms

- Evidence: `QuoteBuilderClient.tsx:303,319,335,351`; `IntakeFormRenderer.tsx:157-158`; `packages/ui/src/styles.css:60-66` (`cyber-input` has no font-size).
- What it does: public quote/intake forms use `text-sm` inputs; shared `cyber-input` inherits 16px.
- How it appears to work: iOS Safari zooms the viewport when a focused control's font-size is < 16px.
- Current controls: `inputMode="numeric"`, `autoComplete="one-time-code"`, labels, inline errors.
- Missing controls: 16px mobile floor; `autocapitalize`/`spellcheck` on email fields.
- Risks: layout jumps and lost context during the quote funnel.
- Recommended improvement: `.cyber-input { @apply text-base sm:text-sm }` and a `text-base sm:text-sm` pattern for ad-hoc inputs.
- Suggested tests: Playwright mobile emulation asserting `font-size >= 16px` on all visible controls.
- Suggested docs: form conventions in `docs/WEB_UI_CONVENTIONS.md`.

### Item: Dialogs and tables

- Evidence: `Dialog.tsx:104-119`; `SupportCenterClient.tsx:216-224`; `AdminDocumentsCenterClient.tsx:1769-1779`; `PromoForm.tsx:59-69`; `CategoryForm.tsx:51-61`; contrast `ProductForm.tsx:85`, `AdminProjectsClient.tsx:304-312`.
- What it does: centered modals with `p-4` and `max-w-*`; some have `max-h`/scroll, some do not.
- How it appears to work: without a max-height, tall content overflows the viewport; with body scroll locked or `overflow-hidden`, it is unreachable.
- Current controls: focus traps, Escape, aria-modal, focus restore.
- Missing controls: `max-h-[90vh] overflow-y-auto`, `items-start` on mobile, sticky footer actions.
- Risks: long forms unusable on phones (create-document, support ticket, promo/category).
- Recommended improvement: extract the `ProductForm` pattern into the shared `Dialog` and adopt it everywhere.
- Suggested tests: Playwright mobile test opening each long modal and scrolling to the submit button.
- Suggested docs: modal checklist in `docs/WEB_UI_CONVENTIONS.md`.

### Item: Mobile E2E and touch accessibility

- Evidence: `playwright.config.ts:28-40`; `e2e/a11y.spec.ts:84-104`; `.github/workflows/e2e.yml`.
- What it does: one Desktop Chrome project; axe gate on 25 routes with `wcag22aa` tags; CI installs chromium only.
- How it appears to work: mobile geometry is never exercised; desktop spacing masks target-size issues.
- Current controls: broad a11y gate; focus traps; skip link (`layout.tsx:36-41`); live regions (`RouteAnnouncer.tsx:28`, `ToastProvider.tsx:117-123`).
- Missing controls: mobile device projects, viewport overrides, overflow assertions, touch-target checks.
- Risks: responsive regressions ship unseen.
- Recommended improvement: add `Pixel 7`/`iPhone 13` Playwright projects; run the a11y spec at 360×800; assert `document.documentElement.scrollWidth <= viewport`.
- Suggested tests: overflow smoke test across 10 representative routes at 320/375/414px.
- Suggested docs: `docs/testing.md` mobile section.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| MOB-001 | Viewport | `layout.tsx` (no viewport export) | Next default | themeColor dropped | P3 | Add `viewport` export |
| MOB-002 | Responsive layouts | 683 breakpoint utilities | Tailwind responsive classes | No mobile proof | P2 | Mobile E2E project |
| MOB-003 | Mobile nav | 3 drawers + focus traps | Drawer/aria/Escape | Marketing menu trap; small targets | P3 | Reuse `useFocusTrap`; 44px targets |
| MOB-004 | Touch targets | 9 controls 20–36px | None | Below 44px guidance | P3 | Min 44px hit areas |
| MOB-005 | Mobile forms | 157/382 controls <16px | 16px on `cyber-input` | iOS zoom | P2 | 16px mobile floor |
| MOB-006 | Mobile dialogs/tables | 24 tables wrapped; 4 modals not | Mixed | Clipping modals | P2 | Scroll-safe modal shell |
| MOB-007 | Auth/dashboard/admin mobile | `(portal)/layout.tsx`, `(admin)/layout.tsx` | Responsive headers | Dropdown clips; density | P3 | Mobile dropdown positioning |
| MOB-008 | PWA manifest | `manifest.ts` + 2 copies | Valid JSON | SVG-only; triplicated | P3 | One source; 192/512 icons |
| MOB-009 | Service worker | `public/sw.js` | None (unregistered) | Inert; unsafe strategy | P2 | Delete or fix+register |
| MOB-010 | Offline fallback | `sw.js:47-50` | Plain-text 503 | No offline page | P2 | Offline route + precache |
| MOB-011 | Install prompt | (absent) | None | No `beforeinstallprompt` | P3 | Add after manifest fix |
| MOB-012 | Push notifications | (absent) | None | No OS alerts | — | Owned by NOTIF-P2-001 |

## Findings

Provisional IDs are shown; the aggregator assigns the final `AREA-Px-NNN` values.

### Finding ID: MOB-P3-001 (provisional) - PWA manifest ships only an SVG icon and is duplicated across three sources

- Severity: P3
- Confidence: High
- Area: MOB
- Evidence:
  - `apps/web/app/manifest.ts:12-18` — single icon `/favicon.svg`, `sizes:"any"`, `type:"image/svg+xml"`
  - `apps/web/public/manifest.json` / `apps/web/public/manifest.webmanifest` — duplicate manifests (diff = trailing newline)
  - `apps/web/app/layout.tsx:26` — `manifest: "/manifest.webmanifest"` while `app/manifest.ts` already generates that URL
  - `apps/web/public` — no PNG, maskable, or apple-touch icon (`git ls-files` + `file(1)`)
  - `git diff --stat 9c0b88c 8d299b8d -- apps/web/app/manifest.ts apps/web/public/ apps/web/app/layout.tsx` — empty (unchanged)
- What is happening: the manifest exists but has no 192/512 icon and is declared from three places.
- Why it matters: Chromium installability requires a 192px and a 512px icon; the current manifest does not qualify, and the redundant sources can drift.
- User / business impact: no home-screen install in Chrome/Edge/Android; iOS gets no proper icon.
- Security / privacy / reliability impact: none direct.
- Recommended fix: keep `app/manifest.ts`, add 192/512 + maskable PNGs and an apple-touch-icon, delete the two public manifests.
- Suggested validation: parse the built manifest in a unit test; run Lighthouse installability.
- Owner suggestion: `@web`
- Effort estimate: S
- Dependencies: brand PNG assets.
- Status: still-open
- Note: re-verified at 8d299b8d — unchanged since 9c0b88c; previous status `open` → `still-open`.

### Finding ID: MOB-P2-001 (provisional) - Service worker `apps/web/public/sw.js` is never registered, so PWA/offline support is inert

- Severity: P2
- Confidence: High
- Area: MOB
- Evidence:
  - `apps/web/public/sw.js:1-53` — full SW implementation (precache, fetch, activate)
  - repo-wide grep for `navigator.serviceWorker` / `serviceWorker.register` / `workbox` in `apps/**` and `packages/**` — no matches
  - `git log --all --oneline -S "navigator.serviceWorker" -- apps/web` — empty (never existed)
  - `git log --oneline -1 -- apps/web/public/sw.js` — added in `f02ec685` (2026-07-30)
- What is happening: the file ships to `/sw.js` but nothing registers it.
- Why it matters: no offline capability, no install/update flow; the dead file misleads future maintainers and auditors into believing PWA support exists.
- User / business impact: field users on flaky mobile networks get no offline resilience.
- Security / privacy / reliability impact: none while unregistered (see MOB-P2-002 for the latent risk).
- Recommended fix: either delete `sw.js` and record the product decision, or implement registration with the safe cache design below.
- Suggested validation: `curl -s /sw.js` + `navigator.serviceWorker.getRegistrations()` in an E2E test.
- Owner suggestion: `@web` with a product decision
- Effort estimate: S (delete) / M (implement)
- Dependencies: MOB-P2-002.
- Status: open
- Note: new finding at 8d299b8d. Corrects the prior NOTIF audit's evidence ("no service worker in apps/web"): the file has existed since f02ec685 and was present at 6286137/9c0b88c — it is simply unregistered.

### Finding ID: MOB-P2-002 (provisional) - sw.js cache strategy would persist authenticated API responses and all GET 200s if registered as-is

- Severity: P2
- Confidence: High (code); Medium (impact — SW is inert today)
- Area: MOB
- Evidence:
  - `apps/web/public/sw.js:33-53` — every same-origin GET is fetched and, on status 200, written to `mct-cache-v1` with no allowlist and no `Cache-Control`/`no-store` check
  - `apps/web/next.config.mjs:23-31` — `/api/v1/:path*` is proxied same-origin, so API GETs are in scope
  - `apps/web/public/sw.js:47-50` — offline fallback is `new Response("Offline", {status:503})`, not an HTML page
  - no logout cache purge (grep: no `caches.delete` outside `activate`)
- What is happening: the Cache API ignores `private`/`no-store`, so tenant/user JSON and rendered portal HTML would persist indefinitely in Cache Storage and be served by the network-first fallback.
- Why it matters: on a shared or lost device, cached authenticated data outlives logout; stale content can be served after deploy.
- User / business impact: privacy exposure and stale-data confusion — only if the SW is ever registered.
- Security / privacy / reliability impact: tenant data cached client-side; no purge path.
- Recommended fix: rewrite the fetch handler to allowlist static assets, bypass `/api/` and non-GET, respect `no-store`, precache an offline HTML route, purge user-scoped caches on logout, and serve `/sw.js` with `Cache-Control: no-cache`.
- Suggested validation: unit tests over the fetch router with mocked `caches`/`fetch`; E2E asserting no `/api/v1/*` entries in Cache Storage.
- Owner suggestion: `@web` + security reviewer
- Effort estimate: M
- Dependencies: MOB-P2-001 decision.
- Status: open
- Note: new finding at 8d299b8d; the domain prompt's "service worker cache risks" special check.

### Finding ID: MOB-P2-003 (provisional) - No mobile-viewport E2E or accessibility coverage (Desktop Chrome only)

- Severity: P2
- Confidence: High
- Area: MOB
- Evidence:
  - `apps/web/playwright.config.ts:28-40` — projects are `setup` + `chromium` (`devices["Desktop Chrome"]`) only
  - `apps/web/e2e/a11y.spec.ts:84-104` — axe scan without `setViewportSize`/device emulation
  - `.github/workflows/e2e.yml` — installs `chromium` only
  - `docs/WEB_UI_CONVENTIONS.md:87-93` — gate is 25 routes, no viewport note
- What is happening: mobile layout, target-size, overflow and dialog behaviour are never exercised in CI.
- Why it matters: the defects in MOB-P2-004/005 and MOB-P3-002/003 can regress unseen.
- User / business impact: mobile UX regressions reach production.
- Security / privacy / reliability impact: none direct.
- Recommended fix: add Pixel 7 / iPhone 13 Playwright projects, run a subset of the a11y spec at 360×800, and add an overflow assertion (`scrollWidth <= innerWidth`) on key routes.
- Suggested validation: the new projects fail on a deliberately overflowing fixture.
- Owner suggestion: `@web` / QA
- Effort estimate: M
- Dependencies: none.
- Status: open
- Note: new finding at 8d299b8d.

### Finding ID: MOB-P2-004 (provisional) - ~41% of form controls render below 16px and trigger iOS Safari focus zoom

- Severity: P2
- Confidence: High (counts); High (iOS behaviour)
- Area: MOB
- Evidence:
  - Python scan of 382 `<input>/<select>/<textarea>` elements: 129 `text-sm` (14px), 28 `text-xs` (12px), 174 `cyber-input`, 51 unspecified
  - `apps/web/components/store/QuoteBuilderClient.tsx:303,319,335,351` — `text-sm` quote-funnel inputs
  - `apps/web/components/store/IntakeFormRenderer.tsx:157-158` — `text-sm` intake inputs
  - `packages/ui/src/styles.css:60-66` — `.cyber-input` sets no font-size (inherits 16px)
- What is happening: public lead-capture forms use 12–14px control text.
- Why it matters: iOS Safari zooms the viewport on focus of any control < 16px, disorienting users mid-form.
- User / business impact: abandoned quote/intake submissions on the primary public conversion path.
- Security / privacy / reliability impact: none.
- Recommended fix: 16px mobile floor (`.cyber-input { @apply text-base sm:text-sm; }` and the same pattern for ad-hoc inputs).
- Suggested validation: Playwright mobile test asserting computed font-size ≥ 16px on visible controls.
- Owner suggestion: `@web`
- Effort estimate: S
- Dependencies: none.
- Status: open
- Note: new finding at 8d299b8d.

### Finding ID: MOB-P2-005 (provisional) - Several modal dialogs have no max-height or vertical scroll and clip on small screens

- Severity: P2
- Confidence: Medium (geometry not rendered; content height inferred)
- Area: MOB
- Evidence:
  - `packages/ui/src/components/Dialog.tsx:104-119` — centered panel with `overflow-hidden`, no `max-h`/`overflow-y`
  - `apps/web/components/portal/SupportCenterClient.tsx:216-224` — create-ticket modal, no max-height
  - `apps/web/components/admin/AdminDocumentsCenterClient.tsx:1769-1779` — create-document modal (`max-w-3xl`), no max-height
  - `apps/web/app/(admin)/admin/store/promotions/PromoForm.tsx:59-69` and `apps/web/app/(admin)/admin/store/categories/CategoryForm.tsx:51-61` — centered modals, no scroll
  - counter-examples: `apps/web/app/(admin)/admin/store/products/ProductForm.tsx:85` (`max-h-[90vh] overflow-y-auto`), `apps/web/app/(admin)/admin/projects/AdminProjectsClient.tsx:304-312` (container `overflow-y-auto`, `items-start` on mobile)
- What is happening: modal patterns are inconsistent; some cannot scroll vertically.
- Why it matters: on a phone, long forms can extend past the viewport with body scroll locked, making the submit button unreachable.
- User / business impact: mobile users cannot complete document creation, support tickets, promotions or categories.
- Security / privacy / reliability impact: none.
- Recommended fix: adopt the `ProductForm` pattern in the shared `Dialog` (max-h + overflow-y-auto + mobile `items-start` + sticky actions) and migrate the ad-hoc modals.
- Suggested validation: Playwright mobile test opening each long modal, scrolling to the submit button.
- Owner suggestion: `@web`
- Effort estimate: M
- Dependencies: none.
- Status: open
- Note: new finding at 8d299b8d.

### Finding ID: MOB-P3-002 (provisional) - Icon-only controls have touch targets well below the 44x44 recommendation

- Severity: P3
- Confidence: High (class math); Medium (real-world tap accuracy)
- Area: MOB
- Evidence:
  - `apps/web/components/marketing/MarketingHeader.tsx:92-106` — hamburger: three `h-0.5 w-7` bars ≈ 28×16px, no padding
  - `apps/web/components/layout/SidebarShell.tsx:116-130` — drawer close: `p-1` + `h-5` icon ≈ 28×28px
  - `apps/web/components/store/StoreLayoutShell.tsx:67-80` — drawer close ≈ 28×28px
  - `packages/ui/src/components/Dialog.tsx:121-128` — close ≈ 28×28px
  - `apps/web/components/ui/ToastProvider.tsx:60-67`, `apps/web/components/store/StickyMobileCta.tsx:55-64` — dismiss `p-1` + `h-4` ≈ 24×24px
  - `apps/web/components/portal/ProjectCalendarView.tsx:106-117` — month arrows `p-1` ≈ 24×24px
  - `apps/web/app/(admin)/admin/store/products/ProductForm.tsx:91-97` — close button with no padding ≈ 20×20px
  - `apps/web/components/NotificationBell.tsx:226-231` — "Mark all read" `text-xs` ≈ 16px tall
- What is happening: several icon-only controls rely on their glyph size for hit area.
- Why it matters: WCAG 2.5.8's 24px minimum is met by some but not all, and all are below the 44px iOS/48px Android guidance; mis-taps are likely one-handed.
- User / business impact: harder navigation/close actions on phones.
- Security / privacy / reliability impact: none.
- Recommended fix: give icon buttons `min-h-11 min-w-11` (or a padded hit area) and keep the glyph size; add the marketing hamburger padding.
- Suggested validation: mobile Playwright test asserting each icon button's bounding box ≥ 44px.
- Owner suggestion: `@web`
- Effort estimate: S
- Dependencies: MOB-P2-003 for regression cover.
- Status: open
- Note: new finding at 8d299b8d.

### Finding ID: MOB-P3-003 (provisional) - Notification dropdown is a fixed 320px panel anchored right-0 and clips on narrow phones

- Severity: P3
- Confidence: Medium (geometry inferred from component widths)
- Area: MOB
- Evidence:
  - `apps/web/components/NotificationBell.tsx:221-222` — `absolute right-0 ... w-80` (320px)
  - `apps/web/app/(portal)/layout.tsx:193-205` — the bell sits left of `PortalHeaderActions` (Admin Portal / Sign Out), so its right edge is inset from the viewport
  - `apps/web/app/(admin)/admin/layout.tsx:156-163` — same order in the admin header
- What is happening: the dropdown's right edge aligns to the bell, not the viewport; 320px extends left past the screen edge on ≤375px devices.
- Why it matters: part of the notification list can be off-screen and unreachable.
- User / business impact: missed notifications on small phones.
- Security / privacy / reliability impact: none.
- Recommended fix: on small screens position the panel with `fixed inset-x-2 top-16 w-auto`, or `w-[min(20rem,calc(100vw-2rem))]`.
- Suggested validation: mobile Playwright test asserting the panel's bounding box is within the viewport at 320/375px.
- Owner suggestion: `@web`
- Effort estimate: S
- Dependencies: none.
- Status: open
- Note: new finding at 8d299b8d.

### Finding ID: MOB-P3-004 (provisional) - `themeColor` is declared in the deprecated metadata export, so the theme-color meta tag is not emitted

- Severity: P3
- Confidence: High (verified against Next.js 15.5.27 source)
- Area: MOB
- Evidence:
  - `apps/web/app/layout.tsx:27` — `themeColor: "#059669"` inside `metadata`
  - Next.js v15.5.27 `packages/next/src/lib/metadata/resolve-metadata.ts` — the `themeColor` case only pushes an "Unsupported metadata ... move it to viewport export" warning and does not set the resolved value
  - no `viewport` export anywhere in `apps/web/app` (grep)
  - `apps/web/app/manifest.ts:11` — `theme_color` exists for the manifest only
- What is happening: the brand colour never reaches `<meta name="theme-color">`.
- Why it matters: browser/OS chrome colour on mobile does not match the brand; build log carries a warning.
- User / business impact: minor visual/brand inconsistency.
- Security / privacy / reliability impact: none.
- Recommended fix: add `export const viewport: Viewport = { themeColor: "#059669" };` to `apps/web/app/layout.tsx` and drop `themeColor` from `metadata`.
- Suggested validation: render test asserting `meta[name=theme-color]`.
- Owner suggestion: `@web`
- Effort estimate: S
- Dependencies: none.
- Status: open
- Note: new finding at 8d299b8d.

### Finding ID: MOB-P3-005 (provisional) - `favicon.ico` contains SVG bytes and no apple-touch-icon is declared

- Severity: P3
- Confidence: High
- Area: MOB
- Evidence:
  - `file apps/web/public/favicon.ico` → "SVG Scalable Vector Graphics image" (435 bytes, byte-identical to `favicon.svg` per `diff`)
  - `apps/web/app/layout.tsx:23-25` — only `icon: "/favicon.svg"` is declared; no `apple`
  - `git ls-files apps/web/public` — no PNG assets
- What is happening: a file named `.ico` is served with an icon MIME type but SVG content; iOS has no touch icon.
- Why it matters: clients that require a real ICO or PNG may not render the icon; iOS "Add to Home Screen" has no proper icon.
- User / business impact: poor home-screen/tab branding on iOS and legacy clients.
- Security / privacy / reliability impact: none.
- Recommended fix: ship a real multi-size `.ico` (or drop the `.ico`), and add a 180×180 `apple-touch-icon` PNG.
- Suggested validation: `file`/magic-byte check in CI for icon assets; Lighthouse icon audit.
- Owner suggestion: `@web`
- Effort estimate: S
- Dependencies: brand assets.
- Status: open
- Note: new finding at 8d299b8d.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| PWA install/offline claims unsupported by registration | P2 | High (already true) | Field users get no offline resilience | `sw.js` + no registration | Decide scope; delete or fix+register |
| Authenticated data cached if SW enabled as-is | P2 | Low (inert today) | Tenant data persists after logout | `sw.js:33-53`, `next.config.mjs:23-31` | Allowlist + API bypass + purge |
| Mobile layout regressions ship unseen | P2 | Medium | Repeated UX defects | Desktop-only Playwright | Mobile projects + overflow assertions |
| iOS zoom breaks public lead forms | P2 | High | Lost conversions | 157 controls <16px | 16px mobile floor |
| Modals unusable on phones | P2 | Medium | Blocked admin/portal tasks | 4 modal patterns without scroll | Shared scroll-safe shell |
| Small touch targets | P3 | Medium | Mis-taps | 9 controls 20–36px | 44px hit areas |
| Notification panel clipping | P3 | Medium | Missed notifications | `w-80` + `right-0` | Viewport-anchored panel |

## Recommendations

### Immediate / Release Blocking

None — no P0/P1 in this domain.

### This Week

1. Add `export const viewport = { themeColor: "#059669" }` (MOB-P3-004) — one line, removes the build warning.
2. Enlarge icon-button hit areas to ≥44px (MOB-P3-002).
3. Set a 16px mobile input floor in `cyber-input` and the quote/intake forms (MOB-P2-004).

### This Month

4. Decide PWA scope: delete `sw.js` + duplicate manifests, or implement MOB-P2-001/002 (registration, allowlist cache, offline page, update flow, no-cache for `/sw.js`).
5. Fix the manifest and icons (MOB-P3-001, MOB-P3-005): one source, 192/512 + maskable + apple-touch.
6. Adopt a scroll-safe modal shell and migrate `SupportCenterClient`, document-center create, `PromoForm`, `CategoryForm` (MOB-P2-005).
7. Add mobile Playwright projects and a 360×800 a11y/overflow pass (MOB-P2-003).
8. Position the notification dropdown for small screens (MOB-P3-003).

### Later / Platform Evolution

9. Offline HTML fallback route and background-sync decision.
10. Install prompt UX (`beforeinstallprompt`) once installability passes.
11. Web Push (owned by NOTIF-P2-001) with permission UX and subscription hygiene.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `viewport` export with themeColor | Removes warning; correct chrome colour | `apps/web/app/layout.tsx` | Render test for `meta[name=theme-color]` |
| 16px mobile input floor | Stops iOS zoom on funnels | `packages/ui/src/styles.css`, store forms | Playwright font-size assertion |
| Padding on hamburger/close buttons | Tap accuracy | `MarketingHeader.tsx`, `SidebarShell.tsx`, `StoreLayoutShell.tsx`, `Dialog.tsx` | Bounding-box assertion |
| `max-h-[90vh] overflow-y-auto` on 4 modals | Unblocks phone form completion | `SupportCenterClient.tsx`, `AdminDocumentsCenterClient.tsx`, `PromoForm.tsx`, `CategoryForm.tsx` | Mobile modal scroll test |
| Delete `public/manifest.json`/`.webmanifest` | Removes drift/ambiguity | `apps/web/public/` | Manifest route test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Safe service worker (allowlist cache, API bypass, purge on logout, offline page, update UX) | P2 | `@web` + security | M | Product decision |
| Mobile Playwright projects + overflow/target-size assertions | P2 | `@web`/QA | M | None |
| 192/512/maskable/apple icons + single manifest source | P3 | `@web` | S | Brand assets |
| Scroll-safe shared modal shell | P2 | `@web` | M | None |
| Touch-target policy (44px) applied app-wide | P3 | `@web` | S | MOB-P2-003 |
| `viewportFit: "cover"` + safe-area insets for notched devices | P3 | `@web` | S | None |
| Install prompt UX + `beforeinstallprompt` capture | P3 | `@web` | S | Installability fix |
| Web Push channel | P2 | platform + notifications | L | NOTIF-P2-001 |

## Suggested Tests

- Unit: parse the generated manifest and assert 192/512 icons; assert the SW fetch router never caches `/api/` or non-GET.
- Integration: rendered-head test for `meta[name=viewport]`, `meta[name=theme-color]`, and a single `link[rel=manifest]`.
- E2E (new mobile project): open/close each drawer with focus containment; open each long modal and scroll to submit; assert `scrollWidth <= innerWidth` on `/`, `/store`, `/store/quote`, `/login`, `/portal/dashboard`, `/admin` at 320/375/414px; assert icon-button bounding boxes ≥44px; assert input font-size ≥16px.
- A11y: run the existing axe spec at 360×800 in the breadth workflow; keep `wcag22aa` tags.
- Offline (once SW exists): go offline and reload a cached page, assert the offline page renders and no API JSON is served.
- CI: add the mobile project to `e2e.yml`; add an icon-format guard (`file`/magic bytes) for `public/*.ico`/PNG assets.

## Suggested Documentation Updates

- Create `docs/PWA.md`: product decision (offline/install/push in or out of scope), manifest/icon contract, SW cache rules, update flow.
- Update `docs/WEB_UI_CONVENTIONS.md`: mobile section (drawer contract, 44px touch targets, 16px input floor, scroll-safe modal rules, mobile E2E requirement).
- Update `docs/testing.md`: mobile Playwright projects and the overflow/target-size assertions.
- Correct `docs/GAP_ANALYSIS.md:45` (subnav pills): code now scrolls horizontally (`AdminSubnav.tsx:35`, `PortalSubnav.tsx:34`) — mark mitigated rather than Open.
- Correct `docs/GAP_ANALYSIS.md:67` and `docs/MEGA_AUDIT_2026-06-18.md:973`: a manifest and `sw.js` do exist (unregistered); the remaining gap is registration/offline scope, not "not started".

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is offline/PWA support a product goal? | Determines delete-vs-implement for `sw.js` | Product decision record |
| Which manifest is actually served at `/manifest.webmanifest` (metadata route vs public file)? | Determines whether `public/manifest.webmanifest` is dead code | Build + `curl -I` in a deployed environment |
| Does the deployed `/sw.js` get cached? | Update-flow correctness if registered | `curl -I https://app.../sw.js` Cache-Control |
| Are the 4 unscrolled modals tall enough to clip on 360×640? | Confirms MOB-P2-005 impact | Device/browser rendering |
| Do portal/admin headers overflow at 320px with a super-admin switcher? | Confirms header density risk | Mobile rendering with a super-admin session |
| Does iOS "Add to Home Screen" fall back to a screenshot? | Confirms icon impact | Device test |

## Appendix

- SW lifecycle as shipped: `install` precaches 8 routes (`sw.js:2-19`), `activate` deletes other caches (`sw.js:22-31`), `fetch` is network-first with cache fallback (`sw.js:33-53`). Nothing registers it.
- The `cyber-table-responsive` utility (`packages/ui/src/styles.css:118-133`) is unused by app code (0 matches); tables use inline `overflow-x-auto` wrappers instead.
- `cyber-subnav-scroll` (`styles.css:159-161`) is also unused; subnavs use `overflow-x-auto` + `min-w-max`.
- 683 responsive utilities: `sm:` 364, `md:` 150, `lg:` 128, `xl:` 41 (grep count over `apps/web` + `packages/ui/src`).
- `PortalSidebarLayout.tsx:19` passes `mobile` unconditionally to `PortalSidebarContent`, so the desktop flyout branch (`PortalSidebarContent.tsx:150-177`) is effectively dead code — a cleanup item, not a mobile defect.
- No `env(safe-area-inset-*)` usage anywhere; `min-h-screen` (100vh) is used in 30 places (`grep -rn "min-h-screen" apps/web packages/ui`).

## Findings

| ID | Severity | Title |
|---|---|---|
| MOB-P3-001 | P3 | PWA manifest ships only an SVG icon and is duplicated across three sources |
| MOB-P2-001 | P2 | Service worker apps/web/public/sw.js is never registered, so PWA/offline support is inert |
| MOB-P2-002 | P2 | sw.js cache strategy would persist authenticated API responses and all GET 200s if registered as-is |
| MOB-P2-003 | P2 | No mobile-viewport E2E or accessibility coverage (Desktop Chrome only) |
| MOB-P2-004 | P2 | About 41% of form controls render below 16px and trigger iOS Safari focus zoom |
| MOB-P2-005 | P2 | Several modal dialogs have no max-height or vertical scroll and clip on small screens |
| MOB-P3-002 | P3 | Icon-only controls have touch targets well below the 44x44 recommendation |
| MOB-P3-003 | P3 | Notification dropdown is a fixed 320px panel anchored right-0 and clips on narrow phones |
| MOB-P3-004 | P3 | themeColor is declared in the deprecated metadata export, so the theme-color meta tag is not emitted |
| MOB-P3-005 | P3 | favicon.ico contains SVG bytes and no apple-touch-icon is declared |
