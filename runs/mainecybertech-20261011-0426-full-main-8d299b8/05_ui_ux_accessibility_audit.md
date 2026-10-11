# 05_ui_ux_accessibility_audit — Prompt 05 - UI/UX, Design System, and Accessibility Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `05_ui_ux_accessibility_audit.md` (area UX, prompt)

## Verification Performed

# UI/UX, Design System, and Accessibility Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (monorepo: `apps/web` Next.js App Router, `apps/api`, `apps/worker`, `packages/ui`, `packages/sdk`, `packages/config`)
- Branch: `main`
- Commit SHA: `8d299b8d` (`8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`)
- Generated at: 2026-10-11
- Auditor: domain subagent (read-only static review)
- Area code: UX
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/05_ui_ux_accessibility_audit.md`
- Scope limitations: **static JSX/CSS review only** — no browser, no axe run, no screenshots, no `pnpm install`/`build` (host is a 1 vCPU droplet). Contrast values were computed from the token hex values. No live accessibility-tree inspection. Findings that depend on runtime behavior (click bubbling, axe rule firing) are marked with their confidence.

## Scope

Reviewed at `8d299b8d`:

- `packages/ui` in full: tokens (`src/tokens/*`), `styles.css`, ThemeProvider/useTheme, and all 7 components (Button, Input/Textarea, Badge, Avatar, Dialog, Skeleton\*, SidebarGroup/Item) plus their 7 stories.
- `apps/web`: root/public/portal/admin layouts, `tailwind.config.ts`, `app/globals.css`, `components/**` (layout, marketing, store, portal, admin, ui), the shared shells/guards (`AdminPageShell`, `AdminListPage`, `ModuleDetailPage`, `RecordDetail`, `ConfirmDialog`, `SubmitButton`, `RouteGuard`, `EmptyState`, `DataErrorNote`, `Breadcrumbs`, `ToastProvider`, `RouteAnnouncer`), the a11y E2E spec, Storybook config and the Chromatic workflow.
- Process evidence: `docs/WEB_UI_CONVENTIONS.md`, `docs/ui-kit.md`, `docs/CI.md`, `docs/testing.md`, `AGENTS.md`, `.github/branch-protection/main.json`.
- Previous run artifacts for the verification duty: `runs/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md` (UX-P3-001).

Not reviewed: `apps/api` UI-adjacent behavior, email templates, PDF generation, native app surfaces (none), and any runtime rendering (no server/browser available).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `packages/ui/src/tokens/{colors,semantic-colors,focus,typography,spacing,borders,shadows,motion}.ts` | Source | Design-token definitions | Complete, typed, exported |
| `apps/web/tailwind.config.ts:1-43` | Config | Token → Tailwind wiring | Imports colors/spacing/typography/borders/shadows/motion; **not** semantic-colors/focus |
| `packages/ui/src/styles.css` | Source | Global utilities, focus-visible, reduced motion, dark/light vars | 183 lines; global `*:focus-visible` outline |
| `packages/ui/src/components/*.tsx` + `*.stories.tsx` | Source | Shared component library | 7 components, 7 stories |
| `apps/web/app/layout.tsx`, `(public)/layout.tsx`, `(portal)/layout.tsx`, `(admin)/admin/layout.tsx` | Source | Landmarks, skip link, providers | `#main-content` present in both shells |
| `apps/web/components/**` (≈300 files) | Source | Component consistency, ARIA, forms, tables, dialogs | Scanned by attribute-aware scripts |
| `apps/web/e2e/a11y.spec.ts` | Test | WCAG gate (25 routes) + breadth triage (68) | axe-core critical/serious filter |
| `.storybook/{main.ts,preview.tsx}`, `.github/workflows/chromatic.yml` | Config/CI | Storybook + visual regression | a11y addon configured; job `continue-on-error` |
| `apps/web/__tests__/**` (≈250 files) | Test | Role-based query usage | 460 `*ByRole` queries, no jest-axe |
| `docs/WEB_UI_CONVENTIONS.md`, `docs/ui-kit.md` | Docs | The declared standard | 93 + ~200 lines |
| `docs/CI.md:13,21,115-119`, `docs/testing.md:66-68` | Docs | A11y/CI process claims | Used for verification |
| `.github/branch-protection/main.json` | Config | Required checks | E2E required; breadth scan not |
| Previous register `…9c0b88c/follow_up_register.md:342` (UX-P3-001) | Prior finding | Verification duty | Re-checked |

## Verification Performed

All commands were read-only against `/tmp/opencode/mct-audit-target` at `8d299b8d`.

| Command / check | Result |
|---|---|
| `git rev-parse HEAD` | `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` — matches run target |
| Attribute-aware Python scan of all `<input>/<select>/<textarea>` (brace/quote-aware tag parser; excludes labels, `id=`, `aria-label`, hidden) | **1** unlabeled control (`ScorecardsEvaluateClient.tsx:35`) |
| Icon-only button scan (button content with no text/literal, ignoring `aria-label`/`title`) | **0** nameless icon-only buttons |
| `<Link>` containing `<button>` / `<button>` containing `<Link>` scan | **1** hit: `AdminTicketCenterClient.tsx:191` (checkbox + status button inside the card Link) |
| `aria-hidden="true"` element containing focusable content scan | **0** |
| `role="dialog"` count vs `aria-modal` count vs `useFocusTrap` usage | 14 / 14 / 10 files + SidebarShell's own trap → all dialogs covered |
| `aria-labelledby` targets existence check (11 references) | All target ids exist |
| Error-render live-region scan (`error` state rendered in JSX without `role=alert/status/aria-live`) | 44 files without; 31 `role="alert"` + 15 `role="status"` repo-wide; 10 files use toasts |
| Page-title scan (`page.tsx` without `metadata`/`generateMetadata`) | **89 of 319** (79 dynamic, 10 static) |
| Heading scan (`<h1>`-to-`<h3>` skips) | 1 page (`ImportExportClient.tsx`) |
| Table scan (`<table` vs `scope=` vs `cyber-table-responsive` wrappers) | 22 files; all wrapped in a scroll container; `aria-sort`/`<caption>` absent but no sortable headers |
| `grep -rn "href=\"#\""`, `role="button"`, positive `tabIndex`, `dangerouslySetInnerHTML` (sanitized elsewhere) | 0 / 0 / 0 / 3 known (QR, JSON-LD, sanitized comment HTML) |
| `grep -rn "useTheme|data-theme|prefers-color-scheme"` in `apps/web` | **0** consumers; 0 `dark:` variants; theme pinned dark |
| `grep -rn "prefers-reduced-motion"` | CSS global (`styles.css:174-183`) + `ParticleBackground.tsx:59` (JS canvas respects it) |
| Contrast computation from token hex values (12 combos incl. remapped slate) | All ≥ 4.5:1 (lowest 5.04:1, primary button text on emerald-600); slate-400/500/600 were deliberately remapped in `tailwind.config.ts:19-24` |
| `grep -rn "@mct/ui"` usage counts | Button 6 files, Input/Dialog/Badge 1, Skeleton 25, others 0 |
| `grep -rho "cyber-[a-z-]*"` usage counts | `cyber-button-secondary` 152, `cyber-button` 79, `cyber-button-sm` 2, `cyber-button-danger` 1 (234) |
| Hex-color scan | 66 of 510 tsx files hardcode a hex; `#0A1118` ×80 |
| `cat packages/ui/package.json` | No `scripts` key; no test files under `packages/ui` |
| `grep -rn "continue-on-error" .github/workflows` | Only `chromatic.yml:28` (+ explicit `false` in `terraform-do.yml`); `a11y-breadth.yml` has none, contradicting `docs/CI.md:117` |
| A11y page-count parse of `a11y.spec.ts` | BASE 25 + FULL 43 = 68 routes; 319 `page.tsx` files exist |
| `cat .github/branch-protection/main.json` | Contexts: Test, Lint, TypeCheck, E2E, Dependency Review — breadth scan not required |
| UX-P3-001 re-verification (below) | **still-open** |

### Verification duty — previous run

- **UX-P3-001 — “Full accessibility breadth scan (68 routes) is triage-only and not a required check”** (previous status `open`, verified at `9c0b88c`): **still-open** at `8d299b8d`.
  - `.github/workflows/a11y-breadth.yml:1-22` — still `workflow_dispatch` + weekly `schedule` only, calling `e2e.yml` with `a11y_full: true`.
  - `apps/web/e2e/a11y.spec.ts:83-86` — default E2E still runs only the 25 `BASE_PAGES`; the 43 `FULL_PAGES` require `A11Y_FULL=1`.
  - `.github/branch-protection/main.json:5-11` — required checks are unchanged; no breadth/a11y context.
  - New residual found during re-verification: `docs/CI.md:117` claims the breadth job is `continue-on-error: true`; the workflow sets no such key (folded into the finding note).
- Other rows whose subject matter touches this domain are owned elsewhere and were **not** re-emitted: `TEST-P2-001` (a11y gate width docs — spot-checked: `docs/testing.md:66`, `docs/WEB_UI_CONVENTIONS.md:87`, `AGENTS.md:285`, `docs/CI.md:13` all still say 25/68, consistent with code), `TEST-P3-001` and `CI-P2-006` (Chromatic/visual regression — cross-referenced only).

## Executive Summary

The UI layer is in better shape than a 500-component app usually is. Accessibility is treated as a first-class concern: a skip link and `#main-content` landmark on every shell, a global `:focus-visible` outline that cannot be defeated by utility `outline-none` classes, a global `prefers-reduced-motion` block plus JS respect in the particle canvas, a deliberately contrast-tuned slate palette (all sampled combos ≥ 4.5:1), 14/14 dialogs with `aria-modal` + focus trap + Escape + focus restore, a route announcer for client navigation, a well-built toast system with polite/assertive regions, labelled form controls almost everywhere (1 miss in 510 files), 0 nameless icon-only buttons, 0 nested-link/button patterns except one, and a 25-route axe gate wired into the required E2E check.

The gaps are concentrated in **verification breadth and component consistency**, not in fundamentals:

1. **Interactive states are outside the gate.** The axe scan only loads pages; dialogs, drawers, filter chips and bulk-selection bars are never scanned. The one nested-interactive defect found by static review (`AdminTicketCenterClient`) is exactly the kind the gate cannot see — and it also breaks mouse multi-select.
2. **Feedback is silent for AT.** ~44 components render async action errors as plain red text with no live region, contradicting the project's own convention (`docs/WEB_UI_CONVENTIONS.md:51-52`).
3. **Modal responsiveness is inconsistent.** Some dialogs handle small viewports; five do not, including a 10-field promotion form and the shared `@mct/ui` Dialog.
4. **The design system is bypassed.** `@mct/ui` interactive primitives are used in 7 files; the app hand-rolls 234 raw button classes and four identical Chip copies. Tokens are also bypassed (66 files hardcode hex colors).
5. **89 pages have no specific title** (WCAG 2.4.2, Level A), and the breadth scan that would catch new route-level regressions is still triage-only (previous UX-P3-001).

No P0/P1 was found in this domain: nothing blocks a release, but items 1–3 should be fixed before the next broad rollout of the admin surfaces.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Design tokens | `packages/ui/src/tokens/*` | Colors, semantic colors, focus, typography, spacing, borders, shadows, motion | Implemented, typed, exported | Low | `semantic-colors` and `focus` exported but unused anywhere |
| Tailwind theme | `apps/web/tailwind.config.ts` | Consumes tokens | Wired (6 of 8 token groups) | Low | Remaps slate 400/500/600 for contrast |
| Global CSS | `packages/ui/src/styles.css` | `cyber-*` utilities, focus-visible, reduced motion, theme vars | Implemented | Low | `cyber-page-bg` hardcodes `#0A1118` |
| Theme | `use-theme.tsx`, `ThemeProvider`, `app/layout.tsx:43` | Dark/light/system | Dark-only in practice; light/system code dead | Low | Documented dark-only |
| Button | `packages/ui/src/components/Button.tsx` | Primary button | Implemented | Low | Used in 6 files; `focus:` not `focus-visible:`; white ring-offset on dark |
| Input/Textarea | `packages/ui/src/components/Input.tsx` | Label + error + helper wiring | Implemented well | Low | Used in 1 file |
| Dialog | `packages/ui/src/components/Dialog.tsx` | Modal with trap/labels | Implemented | Medium | No max-height/scroll |
| Badge/Avatar/Skeleton/SidebarGroup | `packages/ui/src/components/*` | Misc primitives | Implemented | Low | Avatar/SidebarGroup/Item unused in app |
| ToastProvider | `apps/web/components/ui/ToastProvider.tsx` | Live-region toasts | Strong | Low | Errors persist; polite/assertive split |
| RouteAnnouncer | `apps/web/components/RouteAnnouncer.tsx` | SPA navigation announcement | Strong | Low | Falls back to document.title |
| SidebarShell | `apps/web/components/layout/SidebarShell.tsx` | Admin/portal shell + mobile drawer | Strong | Low | Focus trap, Escape, restore, `aria-expanded` |
| StoreLayoutShell | `apps/web/components/store/StoreLayoutShell.tsx` | Store shell + drawer | Good | Low | No `aria-expanded` on toggle |
| ConfirmDialog / useFocusTrap | `components/admin/ConfirmDialog.tsx`, `lib/use-focus-trap.ts` | Standard confirm + trap | Strong | Low | Static `confirm-dialog-body` id |
| StatusPill | `components/admin/StatusPill.tsx` | Central status badge | Strong | Low | 60+ status→tone map |
| Chip (×4 copies) | `AdminTicketCenterClient`, `AdminUsersClient`, `AdminProjectsClient`, `AdminOrganizationsClient` | Filter chips | Duplicated | Medium | Glyph-only ×, small target |
| EmptyState / DataErrorNote | `components/EmptyState.tsx`, `components/admin/DataErrorNote.tsx` | Empty + load-failure states | Strong | Low | Convention documented |
| a11y gate | `apps/web/e2e/a11y.spec.ts` | axe WCAG 2.0/2.1/2.2 A+AA | 25 routes required, 43 triage | Medium | Static page loads only |
| Storybook | `.storybook/*`, `packages/ui/src/**/*.stories.tsx` | Component docs + a11y addon | 7 stories, build broken | Medium | No app-component stories |
| Visual tests | — | Screenshot regression | Absent | Medium | Chromatic `continue-on-error` |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Design tokens | 4 | 8 token modules, typed, wired into Tailwind (`tailwind.config.ts:2-40`) | `semanticColors`/`focus` unused; 66 files hardcode hex | Enforce tokens with a guard; delete or adopt unused token groups |
| CSS/Tailwind/theme | 3 | `styles.css` utilities, global focus-visible + reduced motion | Dead light theme; arbitrary rgba cards duplicate utilities | Remove dead theme code; standardize card backgrounds |
| Reusable components | 2 | 7 primitives, only 7 app files import interactive ones; 234 raw button classes; Chip ×4 | Library bypassed; no standard enforced | Adopt or document; move Chip/ConfirmDialog into the library |
| Layouts/nav | 4 | Skip link + `#main-content`, nav labels, `aria-current`, subnavs, mobile drawers with traps | `aria-haspopup` mismatch; bell/drawer missing `aria-expanded` | Fix the two ARIA attributes |
| Forms/dialogs/toasts/tables/cards | 4 | 1 unlabeled control, 14/14 dialogs trapped, toasts strong, tables scoped + scroll-wrapped | 5 modals clip on small screens; ~44 errors unannounced | Modal max-height sweep; InlineError primitive |
| Icons/color/typography/spacing | 4 | Contrast-tuned palette (all sampled ≥4.5:1), lucide icons, remapped slate | `text-[10px]`/`text-[11px]` micro-type; hex drift | Tokenize colors; consider a 12px type floor |
| Focus states | 5 | Global `*:focus-visible` outline survives utility overrides; dialogs manage focus | Button uses `focus:` ring + white offset | Optional polish to `focus-visible:` |
| Keyboard nav | 4 | Traps + Escape + focus restore in dialogs/drawers/menus; subnav links; no positive tabindex | Bell panel has no Escape; custom status dropdown is Tab-only | Add Escape to the bell; consider listbox semantics |
| ARIA | 4 | 14/14 dialogs labelled, `aria-current`, live regions for toasts, labels on filters | `aria-haspopup` mismatch; missing `aria-expanded`; unannounced errors | Fix the three patterns above |
| Semantic HTML | 4 | `<nav>/<main>/<ol>` breadcrumbs, headings on nearly all pages, no clickable divs except backdrops | 1 nested-interactive card; 1 heading skip | Fix the ticket card; promote h3→h2 |
| Responsive breakpoints | 4 | 355 `sm:` / 144 `md:` / 123 `lg:` usages; tables in scroll wrappers; timeline/calendar scroll | Modals without max-height; no automated viewport tests | Modal fix + a 375×667 Playwright check |
| Dark mode | 3 | Dark-only by design and documented; consistent dark palette | Light/system code is dead weight; Storybook toolbar is decorative | Delete or implement; keep docs in sync |

Overall domain score: **3.6 / 5** — functional and partially hardened, with a strong accessibility baseline but weak verification breadth and design-system discipline.

## Detailed Review

### Item: Design tokens and theme

- Evidence: `packages/ui/src/tokens/*.ts`, `apps/web/tailwind.config.ts:2-40`, `packages/ui/src/styles.css:5-13,153-165`, `docs/WEB_UI_CONVENTIONS.md:83`.
- What it does: tokens define the cyber palette, spacing, type, radii, shadows and motion; Tailwind consumes six token groups; `styles.css` exposes `cyber-*` utilities and CSS variables.
- How it appears to work: components use Tailwind utilities generated from tokens (plus remapped slate shades for contrast); arbitrary values are used freely where tokens exist.
- Missing controls: no guard against new hardcoded colors; `semanticColors` and `focus` tokens are exported but referenced nowhere; the light-theme block and ThemeProvider branches are unreachable.
- Risks: drift, mass-edit cost, misleading Storybook theme toolbar.
- Recommended improvement: adopt `text-cyber-base`/`glass-card` in touched files, delete dead theme paths (or implement a toggle), add a hex-color guard.
- Suggested tests: a regex/ESLint check for `#[0-9a-f]{6}` in `apps/web/{app,components}`; a Storybook story that asserts `data-theme` handling if a toggle is added.
- Suggested docs: update `docs/WEB_UI_CONVENTIONS.md` (“Consistency”) with the token-vs-hex rule.

### Item: Shared primitives (`@mct/ui`)

- Evidence: `packages/ui/src/index.ts:14-21`; usage counts (Button 6 files, Input/Dialog/Badge 1, others 0); 234 raw `cyber-button*` usages; Chip ×4; `packages/ui/package.json` has no scripts.
- What it does: provides Button/Input/Badge/Avatar/Dialog/Skeleton/Sidebar primitives with loading, error, focus and ARIA handling.
- How it appears to work: only auth pages and `DocumentShareClient` import interactive primitives; the rest of the app uses `cyber-*` classes and local copies.
- Missing controls: no lint rule, no ownership doc beyond `docs/ui-kit.md`, no tests for the library.
- Risks: a11y fixes applied per call site; duplicated behavior drift (e.g. StoreLayoutShell vs SidebarShell `aria-expanded`).
- Recommended improvement: single standard; move Chip/ConfirmDialog/StatusPill into `@mct/ui`; add scripts + jest-axe.
- Suggested tests: RTL + jest-axe tests for each primitive; Storybook test-runner.
- Suggested docs: `docs/ui-kit.md` “which one to use” decision table; deprecation note for raw `cyber-button*`.

### Item: Modals and drawers

- Evidence: 14 `role="dialog"` with `aria-modal`; `useFocusTrap` in 10 files + SidebarShell trap; good scroll patterns in `ProductForm.tsx:85`, `AdminProjectsClient.tsx:305`, `AdminTicketCenterClient.tsx:718`; missing in `PromoForm.tsx:60-71`, `CategoryForm.tsx:52-63`, `SupportCenterClient.tsx:216-225`, `AdminDocumentsCenterClient.tsx:1769-1780`, `ConfirmDialog.tsx:37-47`, `Dialog.tsx:114-119`.
- What it does: consistent dialog semantics; inconsistent viewport handling.
- Risks: clipped forms/unreachable submit on small screens.
- Recommended improvement: fix the shared Dialog + the four app modals; add a viewport test.
- Suggested tests: Playwright at 375×667 opening each modal and asserting the primary button is visible/clickable.

### Item: Forms and feedback

- Evidence: 1 unlabeled input in 510 files; ContactForm exemplary (`ContactForm.tsx:117-289`); Input component wires `aria-invalid`/`aria-describedby`; 44 files render errors without live regions; signup lacks `autocomplete`.
- Recommended improvement: InlineError primitive; autocomplete on auth forms.
- Suggested tests: RTL test asserting `role="alert"` appears after a failed submit; a lint/scan test for unlabeled controls.

### Item: Tables, lists and navigation

- Evidence: 22 files with tables, all in scroll wrappers, `scope` used 102×; no `aria-sort` (sorting is via selects); `AdminPagination` has `nav[aria-label]` + `aria-current`; breadcrumbs are `nav > ol`.
- Recommended improvement: none required; consider `<caption class="sr-only">` for data tables and `aria-sort` if sortable headers are introduced.

### Item: Motion, icons and color

- Evidence: global reduced-motion block (`styles.css:174-183`); `ParticleBackground.tsx:59` checks `prefers-reduced-motion`; lucide icons with `aria-hidden` on decorative SVGs; contrast computed for 12 combos, all pass.
- Recommended improvement: replace `text-[10px]`/`text-[11px]` micro-type where it carries meaning; keep contrast discipline.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| UX-001 | Design tokens | `tokens/*.ts`, `tailwind.config.ts:2-40` | Complete token set, wired | 2 token groups unused; 66 files hardcode hex | P3 | Enforce tokens; delete/adopt unused groups |
| UX-002 | CSS/Tailwind/theme | `styles.css`, `layout.tsx:43` | Utilities + focus + reduced motion | Dead light theme; arbitrary rgba cards | P3 | Remove dead theme; use utilities |
| UX-003 | Reusable components | `packages/ui/src/index.ts:14-21` | 7 primitives | 234 raw buttons; Chip ×4; library untested | P2 | Single standard + tests |
| UX-004 | Layouts/nav | shells, subnavs, `aria-current` | Strong | `aria-haspopup` mismatch; bell/drawer `aria-expanded` | P3 | Fix attributes |
| UX-005 | Forms/dialogs/toasts/tables/cards | 14 dialogs, toasts, tables | Mostly strong | 5 modals clip; 44 unannounced errors | P2 | Modal sweep; InlineError |
| UX-006 | Icons/color/typography/spacing | palette, lucide, type scale | Contrast-tuned; icons hidden from AT | micro-type 10–11px | P3 | Tokenize; type floor |
| UX-007 | Focus states | `styles.css:168-171`, traps | Global focus-visible; trap/restore | Button `focus:` ring + white offset | P3 | Optional polish |
| UX-008 | Keyboard nav | traps, menus, subnavs | Escape/Tab/arrow support | Bell no Escape; custom dropdown Tab-only | P3 | Add Escape; consider listbox |
| UX-009 | ARIA | 14/14 dialogs labelled, live regions | Strong | `aria-haspopup`, missing `aria-expanded`, unannounced errors | P2 | Fix patterns |
| UX-010 | Semantic HTML | nav/main/ol, 0 clickable divs | Strong | Nested checkbox/button in Link; h1→h3 skip | P2 | Fix ticket card; h2 |
| UX-011 | Responsive breakpoints | 355 sm / 144 md / 123 lg; scroll wrappers | Good | Modal overflow; no viewport tests | P2 | Modal fix + viewport test |
| UX-012 | Dark mode | dark-only, documented | Consistent dark | Dead light/system code | P3 | Delete or implement |
| UX-013 | Skeletons/errors/empty states | 26 `loading.tsx`, 4 `error.tsx`, `EmptyState`, `DataErrorNote` | Standards exist | Skeleton coverage 26/319; load-failure rule documented but not audited here | P3 | Extend loading coverage to high-traffic routes |
| UX-014 | Storybook | `.storybook/*`, 7 stories | Configured with a11y addon | No app stories; build broken; library untested | P3 | Add stories/tests; unblock build |
| UX-015 | Visual/A11y tests | `a11y.spec.ts`, Chromatic | 25-route required axe gate | Breadth triage-only; no interaction scans; no visual tests | P3 | Ratchet + interaction scans |

## Findings

Summary table (details follow):

| Severity | Title | Status |
|---|---|---|
| P2 | Ticket-card bulk selection nests a checkbox and a status button inside a Link, so ticking a ticket also navigates | open |
| P2 | Inline async action errors are not announced by assistive tech in ~44 components, contradicting the documented convention | open |
| P2 | Several dialogs have no max-height or internal scroll, so tall forms are clipped on small viewports | open |
| P2 | 89 of 319 pages have no page-specific title (79 dynamic detail pages + 10 static) | open |
| P2 | @mct/ui primitives are largely bypassed: 6 files import Button, 1 uses Input/Dialog/Badge, 234 raw button classes, four Chip copies | open |
| P3 | Four Chip copies render a glyph-only '×' remove button with a sub-24px target size | open |
| P3 | Theme is documented dark-only but ships dead light/system code paths | open |
| P3 | Sidebar group toggles declare aria-haspopup='true' for a link list | open |
| P3 | Notification bell and store drawer toggles omit aria-expanded | open |
| P3 | Color-token drift: 66 files hardcode hex colors, 45 arbitrary rgba card backgrounds | open |
| P3 | Heading order skips a level on the store import/export page | open |
| P3 | ScorecardsEvaluateClient renders the only unlabeled input and an unannounced error | open |
| P3 | Signup form inputs lack autocomplete attributes | open |
| P3 | Storybook covers only the 7 @mct/ui primitives; packages/ui has no tests/lint scripts | open |
| P3 | Full accessibility breadth scan (68 routes) is triage-only and not a required check | still-open (re-verified) |
| P3 | The a11y gate scans only initial page loads; interactive states are untested | open |

### Finding UX-P2-001 — Ticket-card bulk selection nests a checkbox and a status button inside a Link

- Severity: P2 · Confidence: high · Area: UX
- Evidence: `apps/web/components/admin/AdminTicketCenterClient.tsx:191-192` (whole card is a `<Link>`); `:197-204` (checkbox inside it, `handleCheckboxChange` at `:184-187` stops only `change`); `:218-221` (status button inside it calls `preventDefault`+`stopPropagation` via `:172-177`); `:551-574` (header select-all sits in a plain label outside any Link).
- What is happening: the per-row checkbox is nested inside an anchor; the click that selects the row also bubbles to the Link, so selection navigates to the detail page. The sibling status button is explicitly guarded, showing the wrapper is known to be interactive.
- Why it matters: invalid interactive nesting (axe `nested-interactive`, serious, medium confidence it fires) and a broken bulk-select workflow.
- Recommended fix: move controls out of the Link (title-only link / stretched-link pattern) or intercept the click; add a regression test.
- Owner suggestion: web UI engineer (admin tickets) · Effort: S · Target: this month · Status: open.

### Finding UX-P2-002 — Inline async errors are unannounced in ~44 components

- Severity: P2 · Confidence: high · Area: UX
- Evidence: `docs/WEB_UI_CONVENTIONS.md:51-52`; examples `DmarcAnalyzeForm.tsx:93`, `CreateRoleForm.tsx:107`, `RecordDetail.tsx:166`, `UploadForm.tsx:62-72`, `PortalTriageClient.tsx:98`; scan counts (44 files without a live region; 31 `role="alert"`, 15 `role="status"`, 10 toast users).
- What is happening: failures of server actions / API calls render as red text with no live region, so AT users get no status message (WCAG 4.1.3).
- Recommended fix: `InlineError` primitive (or `pushToast`) and sweep the call sites.
- Owner suggestion: web UI engineer · Effort: M · Target: this month · Status: open.

### Finding UX-P2-003 — Dialogs without max-height/scroll clip on small viewports

- Severity: P2 · Confidence: high · Area: UX
- Evidence: `PromoForm.tsx:60-71`, `CategoryForm.tsx:52-63`, `SupportCenterClient.tsx:216-225`, `AdminDocumentsCenterClient.tsx:1769-1780`, `ConfirmDialog.tsx:37-47`, `Dialog.tsx:114-119`; good patterns at `ProductForm.tsx:85`, `AdminProjectsClient.tsx:305`, `AdminTicketCenterClient.tsx:718`.
- What is happening: `fixed inset-0 flex items-center justify-center` with no panel max-height and no overlay scroll; content taller than the viewport is unreachable.
- Recommended fix: `max-h-[90vh] overflow-y-auto` on panels (or overlay scroll); fix the shared Dialog.
- Owner suggestion: web UI engineer · Effort: S · Target: this month · Status: open.

### Finding UX-P2-004 — 89 pages lack a specific title

- Severity: P2 · Confidence: high · Area: UX
- Evidence: static scan (89/319; 79 dynamic, 10 static); `app/layout.tsx:19-20` fallback title; `app/(public)/layout.tsx:15-18` template; `RouteAnnouncer.tsx:20-23` fallback to `document.title`.
- What is happening: detail pages and auth pages inherit generic titles (WCAG 2.4.2).
- Recommended fix: `generateMetadata` per detail route; explicit titles for the five auth pages; add a route-title test.
- Owner suggestion: web UI engineer · Effort: M · Target: this month · Status: open.

### Finding UX-P2-005 — `@mct/ui` primitives are largely bypassed

- Severity: P2 · Confidence: high · Area: UX
- Evidence: usage counts (above); 234 raw `cyber-button*`; Chip ×4; duplicated drawer shells; `packages/ui/package.json` has no scripts.
- What is happening: the design system exists but the app mostly hand-rolls it.
- Recommended fix: single standard; migrate local primitives into `@mct/ui`; add tests and a lint guard.
- Owner suggestion: design-system owner · Effort: L · Target: next quarter · Status: open.

### Finding UX-P3-006 — Chip remove buttons: glyph-only name, sub-24px target

- Severity: P3 · Confidence: high · Area: UX
- Evidence: the four Chip copies (lines above); button class `ml-0.5 text-emerald-400 ...` with `&times;`.
- Recommended fix: one Chip component, `aria-label`, min 24×24 target.
- Owner: web UI engineer · Effort: S · Target: this month · Status: open.

### Finding UX-P3-007 — Dead light/system theme paths

- Severity: P3 · Confidence: high · Area: UX
- Evidence: `docs/WEB_UI_CONVENTIONS.md:83`; `styles.css:154-165`; `use-theme.tsx:37-47`; `layout.tsx:43`; 0 `useTheme`/`dark:` usages; `.storybook/preview.tsx:35-46` toolbar not wired.
- Recommended fix: delete the dead paths (or implement a real toggle); sync docs.
- Owner: design-system owner · Effort: S · Target: this quarter · Status: open.

### Finding UX-P3-008 — `aria-haspopup="true"` on sidebar disclosures

- Severity: P3 · Confidence: high · Area: UX
- Evidence: `AdminSidebarContent.tsx:104`, `PortalSidebarContent.tsx:104`, popup at `:123-178`.
- Recommended fix: drop `aria-haspopup` or implement menu semantics.
- Owner: web UI engineer · Effort: S · Target: this quarter · Status: open.

### Finding UX-P3-009 — Missing `aria-expanded` on bell and store drawer toggles

- Severity: P3 · Confidence: high · Area: UX
- Evidence: `NotificationBell.tsx:196-199,221-222,147-154`; `StoreLayoutShell.tsx:31-36`; contrast `SidebarShell.tsx:79-80`.
- Recommended fix: add `aria-expanded` (+ Escape/focus return for the bell).
- Owner: web UI engineer · Effort: S · Target: this quarter · Status: open.

### Finding UX-P3-010 — Color-token drift

- Severity: P3 · Confidence: high · Area: UX
- Evidence: 66 files with hex; `#0A1118` ×80; 45 arbitrary rgba card backgrounds; tokens available (`colors.ts:1-13`, `tailwind.config.ts:14-18`).
- Recommended fix: tokenize touched files; add a hex guard.
- Owner: design-system owner · Effort: M · Target: next quarter · Status: open.

### Finding UX-P3-011 — Heading-order skip on import/export

- Severity: P3 · Confidence: high · Area: UX
- Evidence: `AdminPageShell.tsx:27` (h1) + `ImportExportClient.tsx:168,193,220,239,259` (h3, no h2).
- Recommended fix: promote to h2.
- Owner: web UI engineer · Effort: S · Target: this quarter · Status: open.

### Finding UX-P3-012 — Unlabeled input and unannounced error in ScorecardsEvaluateClient

- Severity: P3 · Confidence: high · Area: UX
- Evidence: `ScorecardsEvaluateClient.tsx:35-40,49`; only such control found in the app.
- Recommended fix: label + `role="alert"`.
- Owner: web UI engineer (edu-automation) · Effort: S · Target: this quarter · Status: open.

### Finding UX-P3-013 — Signup inputs lack autocomplete

- Severity: P3 · Confidence: high · Area: UX
- Evidence: `signup/page.tsx:55,72,90` vs `login/page.tsx:148,168,310`.
- Recommended fix: `autoComplete="name" | "email" | "new-password"`.
- Owner: web UI engineer (auth) · Effort: S · Target: this quarter · Status: open.

### Finding UX-P3-014 — Storybook coverage and untested UI package

- Severity: P3 · Confidence: high · Area: UX
- Evidence: 7 stories under `packages/ui/src/components`; no `apps/web` stories though `.storybook/main.ts:6` globs them; `packages/ui/package.json` has no scripts; a11y addon configured (`main.ts:13`, `preview.tsx:20-24`) but Chromatic is `continue-on-error` (`chromatic.yml:22-28`, `docs/CI.md:114-116`).
- Recommended fix: stories for app primitives, jest-axe/test-runner, package scripts, unblock Chromatic (cross-ref CI-P2-006/TEST-P3-001).
- Owner: design-system owner / QA · Effort: M · Target: next quarter · Status: open.

### Finding UX-P3-015 — Breadth scan triage-only (previous UX-P3-001)

- Severity: P3 · Confidence: high · Area: UX · Status: **still-open**
- Evidence: `a11y-breadth.yml:1-22`; `a11y.spec.ts:5-32,37-81,83-86`; `.github/branch-protection/main.json:5-11`; `docs/CI.md:21,117`; 319 routes vs 68 scanned.
- Note: re-verified at `8d299b8d` — unchanged from `9c0b88c`; residual doc mismatch at `docs/CI.md:117`.
- Recommended fix: ratchet FULL_PAGES into BASE_PAGES in batches; fix or deliberately add `continue-on-error`.
- Owner: @web / platform CI owner · Effort: M · Target: next quarter.

### Finding UX-P3-016 — Gate scans only initial page loads

- Severity: P3 · Confidence: medium · Area: UX
- Evidence: `a11y.spec.ts:89-111` (goto + bounded `networkidle` + axe, no interactions); comment `:92-96`; client-fetch example `NotificationsPageClient.tsx:50-60`; no dialog/drawer/chip/bulk-bar scans.
- Recommended fix: interaction scan set and/or jest-axe unit tests.
- Owner: QA / web UI engineer · Effort: M · Target: next quarter · Status: open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| A11y regression ships on breadth-only routes or in interactive states | Medium | Medium | WCAG conformance and user trust | `a11y-breadth.yml`, `a11y.spec.ts:89-111` | Ratchet gate + interaction scans |
| Screen-reader users miss action failures | Medium | High | Users retry blindly or abandon | 44 unannounced error sites | InlineError primitive |
| Mobile users blocked by clipped modals | Medium | Medium | Cannot complete create/edit flows | `PromoForm.tsx:60-71` etc. | Modal max-height sweep |
| Bulk-select unusable / nested-interactive defect spreads as a pattern | Medium | Medium | Admin workflow + AT confusion | `AdminTicketCenterClient.tsx:191-205` | Fix card structure |
| Design-system drift makes a11y fixes incomplete | Low | High | Fixes applied N times; misses | 234 raw buttons; Chip ×4 | Single standard + guards |
| Generic page titles harm orientation | Low | High | WCAG 2.4.2 (A) failure | 89 pages | generateMetadata |
| Dead theme code misleads contributors | Low | Medium | Wasted work, inconsistent UI | `styles.css:154-165` | Delete or implement |

## Recommendations

### Immediate / Release Blocking

None. No P0/P1 was identified in this domain.

### This Week

1. Fix the ticket-card interactive nesting (UX-P2-001) — small change, breaks a real workflow.
2. Modal max-height sweep (UX-P2-003) — five containers, one shared component.
3. Chip component consolidation with labelled, ≥24px remove buttons (UX-P3-006).

### This Month

4. InlineError/live-region sweep for the ~44 error sites (UX-P2-002).
5. `generateMetadata` for detail routes + titles for auth pages (UX-P2-004).
6. `aria-expanded`/`aria-haspopup`/Escape fixes (UX-P3-008, UX-P3-009).
7. Signup autocomplete + the scorecards input label (UX-P3-012, UX-P3-013).

### Later / Platform Evolution

8. Design-system adoption decision and migration (UX-P2-005, UX-P3-010).
9. A11y gate ratchet + interaction scans (UX-P3-015, UX-P3-016).
10. Storybook coverage and library tests; unblock Chromatic (UX-P3-014).
11. Delete or implement light/system theme (UX-P3-007).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `role="alert"` to the five highest-traffic error renders | Immediate AT feedback | `DmarcAnalyzeForm.tsx`, `CreateRoleForm.tsx`, `RecordDetail.tsx`, `UploadForm.tsx`, `PortalTriageClient.tsx` | RTL test asserting alert appears |
| `max-h-[90vh] overflow-y-auto` on 4 app modals + shared Dialog | Unblocks mobile forms | `PromoForm`, `CategoryForm`, `SupportCenterClient`, `AdminDocumentsCenterClient`, `Dialog.tsx` | Playwright 375×667 visibility check |
| Add `aria-expanded` to bell + store toggle | One-line ARIA correctness | `NotificationBell.tsx`, `StoreLayoutShell.tsx` | axe/manual keyboard check |
| Remove `aria-haspopup` from sidebar toggles | Removes misleading announcement | `AdminSidebarContent.tsx`, `PortalSidebarContent.tsx` | Manual SR check |
| h3→h2 on import/export | Heading outline fix | `ImportExportClient.tsx` | axe heading-order |
| Signup autocomplete | WCAG 1.3.5 | `signup/page.tsx` | axe/manual |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Move Chip/ConfirmDialog/StatusPill into `@mct/ui` | P2 | design-system owner | M | standard decision |
| Add test/lint/typecheck scripts + jest-axe to `packages/ui` | P2 | design-system owner | M | — |
| Ratchet FULL_PAGES → BASE_PAGES in batches | P2 | @web / CI | M | clean pages list |
| Interaction a11y scan set (dialogs/drawers/filters) | P2 | QA | M | Playwright helpers |
| Route-title guard test | P3 | web UI | S | — |
| Hex-color lint guard | P3 | design-system owner | S | — |
| Tokenize card backgrounds (`glass-card`) | P3 | web UI | M | — |
| Theme cleanup (delete or implement) | P3 | design-system owner | S | product decision |
| Skeleton coverage for remaining high-traffic routes | P3 | web UI | M | — |

## Suggested Tests

- **Unit (RTL + jest-axe)**: Button, Input, Dialog, Chip, StatusPill, ToastProvider, ConfirmDialog — assert roles/labels/live regions; snapshot-free.
- **Interaction E2E**: open each dialog/drawer/menu and run axe in the open state; apply a filter chip and scan; bulk-select a ticket row and assert no navigation (UX-P2-001 regression).
- **Viewport E2E**: 375×667 and 768×1024 runs opening every modal and asserting the primary action is in the viewport.
- **Route metadata test**: enumerate `app/**/page.tsx` and assert a non-default title (extend `scripts/check-docs-counts.mjs` style parsing).
- **Static guards**: unlabeled-control scan and hex-color scan as CI steps (both are simple regex/AST walks).
- **Visual**: fix the Storybook build, then make Chromatic blocking with the 7+ primitives.

## Suggested Documentation Updates

- `docs/WEB_UI_CONVENTIONS.md`: add “Modals must set `max-height` + internal scroll”; add “new error renders must use `InlineError`/toast”; record the component-vs-utility standard decision.
- `docs/ui-kit.md`: add Chip/InlineError/ConfirmDialog once promoted; add a “do not hand-roll” note.
- `docs/CI.md:117`: correct the `continue-on-error` claim for the breadth job (or add the key deliberately).
- `docs/testing.md`: document the interaction/viewport a11y test plan when added.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was the populated `/admin/tickets` DOM ever scanned green (the nested checkbox)? | Determines whether the gate has a blind spot or axe tolerates the pattern | A local axe run against the seeded page |
| Is `continue-on-error` intended for the breadth workflow? | Docs and code disagree | Owner decision |
| Is the raw `cyber-*` utility approach the intended standard (and `@mct/ui` legacy), or vice versa? | Determines the direction of the design-system backlog | Owner/design decision |
| Are the 10px/11px micro-type styles accepted for the brand? | Readability vs brand choice | Design decision |
| Should the light theme exist? | Dead code vs roadmap | Product decision |

## Appendix

### A. Contrast samples (computed from token hex, WCAG relative luminance)

| Pair | Ratio | AA normal text |
|---|---:|---|
| slate-400 (#c7d3e0, remapped) on #0A1118 | 12.49 | Pass |
| slate-500 (#94a3b8, remapped) on #0A1118 | 7.40 | Pass |
| slate-600 (#7a8ba0, remapped) on #0A1118 | 5.45 | Pass |
| emerald-400 on #0A1118 | 9.87 | Pass |
| amber-300 on #0A1118 | 13.16 | Pass |
| red-400 on #0A1118 | 6.86 | Pass |
| #0A1118 on emerald-600 (#059669) | 5.04 | Pass |
| slate-500 on slate-900 (#0f172a) | 6.96 | Pass |

### B. Coverage math

- Routes: 319 `page.tsx` files; axe gate: 25 required + 43 triage = 68 (~21%).
- Dialogs: 14 `role="dialog"` / 14 `aria-modal` / 10 files with `useFocusTrap` + SidebarShell custom trap → 100% covered by a trap.
- Forms: 1 unlabeled control of the scanned population; 0 nameless icon-only buttons; 0 positive tabindex.
- Live regions: 31 `role="alert"` + 15 `role="status"` + 2 toast viewports; 44 error-render sites without.
- Component reuse: 7 `@mct/ui` interactive primitives, 7 consuming files; 234 raw button utility usages; 4 Chip copies.

### C. Method

Static review only: brace/quote-aware tag scanners over `apps/web/{app,components}` (510 tsx files), grep inventories, line-level citation, contrast math from tokens. No repository files were modified; the target worktree was read-only.

## Findings

| ID | Severity | Title |
|---|---|---|
| UX-P2-001 | P2 | Ticket-card bulk selection nests a checkbox and a status button inside a Link, so ticking a ticket also navigates |
| UX-P2-002 | P2 | Inline async action errors are not announced by assistive tech in ~44 components, contradicting the documented convention |
| UX-P2-003 | P2 | Several dialogs have no max-height or internal scroll, so tall forms are clipped on small viewports |
| UX-P2-004 | P2 | 89 of 319 pages have no page-specific title (79 dynamic detail pages + 10 static), so browser and AT titles are generic |
| UX-P2-005 | P2 | @mct/ui primitives are largely bypassed: 6 files import Button, 1 uses Input/Dialog/Badge, while the app hand-rolls 234 raw cyber-button* usages and four Chip copies |
| UX-P3-001 | P3 | Four Chip copies render a glyph-only '×' remove button with a sub-24px target size |
| UX-P3-002 | P3 | Theme is documented dark-only but ships dead light/system code paths (CSS variables, ThemeProvider, Storybook toolbar) |
| UX-P3-003 | P3 | Sidebar group toggles declare aria-haspopup='true' for a popup that is a link list, not a menu |
| UX-P3-004 | P3 | Notification bell and store drawer toggles omit aria-expanded |
| UX-P3-005 | P3 | Color-token drift: 66 files hardcode hex colors (80x #0A1118) and 45 arbitrary rgba card backgrounds instead of the design tokens |
| UX-P3-006 | P3 | Heading order skips a level on the store import/export page |
| UX-P3-007 | P3 | ScorecardsEvaluateClient renders the only programmatically unlabeled input in the app and an unannounced error |
| UX-P3-008 | P3 | Signup form inputs lack autocomplete attributes |
| UX-P3-009 | P3 | Storybook covers only the 7 @mct/ui primitives; packages/ui has no test/lint scripts and the a11y addon runs nowhere |
| UX-P3-010 | P3 | Full accessibility breadth scan (68 routes) is triage-only and not a required check |
| UX-P3-011 | P3 | The a11y gate scans only initial page loads; interactive states (dialogs, drawers, filters, bulk bars) and client-fetched content are untested |
