# 05_ui_ux_accessibility_audit — Prompt 05 - UI/UX, Design System, and Accessibility Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `05_ui_ux_accessibility_audit.md` (area UX, prompt)

## Verification Performed

# 05_ui_ux_accessibility_audit - 05_ui_ux_accessibility_audit.md

Domain subagent `05_ui_ux_accessibility_audit` (area UX), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - Web dashboard's primary interactions are mouse-only (runner cards, sortable headers, table rows)** (confidence: High)
  - `server/web/app.js:392 - runner panels are `<div class="runner ..." data-runner="...">`; opening the live view is bound to a click only`
  - `server/web/app.js:1734 - `document.addEventListener("click", (e) => {...})` is the single interaction entry point; app.js:1743 dispatches [data-runner],[data-detail],[data-focus], etc.`
  - `server/web/app.js:862 - sortable `<th class="sortable">` are re-rendered from the click handler (app.js:1735-1741) with no keyboard/Enter/Space path`
  - `server/web/app.js:880 - history rows `<tr data-detail="...">` and app.js:928 fleet rows are clickable only`
  - `server/web/style.css:58 `.runner{...cursor:pointer}`, style.css:110 `tbody tr{cursor:pointer}`, style.css:194 `th.sortable{cursor:pointer}``
  - `server/web - grep for `tabindex`/`role=`/`keydown` on these elements returns nothing; only two global keydown listeners exist (app.js:1716, app.js:1825) and neither covers them`
  - Impact: Keyboard-only and assistive-technology users cannot open a runner's live view, sort the history table, or open a run's detail — core tasks in the control plane.
  - Recommendation: Render the clickable panels/rows/headers as real `<button>`/`<a>` or add tabindex=0 + role=button/row and an Enter/Space keydown handler; add aria-sort to the sorted `<th>`.
- **P2 - Modal dialog has no dialog semantics, no focus trap, and no focus restore** (confidence: High)
  - `server/web/index.html:146 - `<div class="modal" id="modal"><div class="modalbox" id="modalbox"></div></div>` has no role="dialog" / aria-modal / aria-labelledby`
  - `server/web/app.js:1708-1712 - `openModal()` sets innerHTML, adds `.show`, and focuses only the first input; the rest of the page stays focusable`
  - `server/web/app.js:1714 - `closeModal()` only removes the class; focus is not returned to the element that opened it`
  - `server/web/app.js:1724 - backdrop click closes; Escape is handled at app.js:1717 but Tab is not trapped`
  - Impact: Screen-reader users are not told a dialog opened, and Tab moves focus behind the overlay (start/stop/reboot/shutdown controls); after closing, keyboard focus is lost, which is disorienting for destructive actions that are confirm-gated.
  - Recommendation: Add role="dialog" aria-modal="true" aria-labelledby to #modalbox, trap Tab within the modal while open, and restore focus to the invoking control on close.
- **P2 - No ARIA anywhere in the web dashboard; tab strip and live SSE updates are not exposed to assistive tech** (confidence: High)
  - `server/web - grep for `aria-*` / `role=` / `aria-live` across app.js, index.html, style.css returns no matches`
  - `server/web/index.html:27-34 - the six tabs are plain `<button data-tab=...>` with no role="tablist"/role="tab"/aria-selected; the panes are `<section id="tab-*" class="tabpane">``
  - `server/web/app.js:1765-1772 - tab switching only toggles the `active` class / display, so no selected-state or panel linkage is announced`
  - `server/web/app.js:280-288 - live telemetry/gauges and phase updates mutate the DOM on each SSE batch with no aria-live region to announce them`
  - Impact: Assistive-technology users get no indication of which tab is selected and no announcement of live run/telemetry changes — a core function of the live fleet view.
  - Recommendation: Add tablist/tab/tabpanel roles with aria-selected and roving tabindex, and mark the live summary/console regions aria-live="polite" (console log off or aria-live="off").
- **P2 - Canvas charts have no accessible alternative and their tooltips are pointer-only** (confidence: High)
  - `server/web/index.html:93 - `<canvas id="trendChart" height="360"></canvas>` with no role="img"/aria-label and no text fallback`
  - `server/web/app.js:1166-1187 - `attachHover()` reads values only from `mousemove` and hides on `mouseleave`; there is no keyboard/touch equivalent`
  - `server/web/app.js:1118-1119 - drawChart stores `cv._chart` and attaches hover; the plotted points are never emitted as text/table`
  - Impact: The Trends, Compare and run-detail charts are opaque to screen readers and to keyboard users; the same numbers are only reachable by hovering with a mouse.
  - Recommendation: Give each canvas role="img" with an aria-label summarising the series, and provide an accessible data table or a focusable legend listing the values (chartLegendHTML already computes the range).
- **P2 - Tk GUI suppresses the keyboard focus indicator and has no keyboard accelerators** (confidence: High)
  - `bench/gui.py:255-256 - TButton style sets `borderwidth=0, focusthickness=0`, removing the focus ring`
  - `bench/gui.py:276 - TCheckbutton style sets `focuscolor=CARD`, so a focused checkbox is visually identical to an unfocused one`
  - `bench/gui.py:331 - the only `bind()` found is `<<ComboboxSelected>>`; there are no `<Key>` accelerators or menu keyboard bindings anywhere in gui.py (grep)`
  - Impact: Keyboard users cannot see which widget has focus in the Tk dashboard, making Tab-based operation unreliable, and there are no shortcuts for start/stop/collect on the core operator surface.
  - Recommendation: Remove `focusthickness=0` and set a visible `focuscolor` (e.g. ACCENT); add keyboard accelerators for start/stop/collect.
- **P3 - No prefers-reduced-motion or prefers-color-scheme support; theme is fixed dark** (confidence: High)
  - `server/web/style.css:73-75 - `@keyframes pulse{...}` is applied to `.statusp.busy` (style.css:73) and `.rtabs .rtab.live .dot` (style.css:220) with no way to disable it`
  - `server/web/style.css:1-6 - `:root` hard-codes the dark palette (--bg:#0f1218, --text:#dce3ee, ...) with no light variant`
  - `server/web - grep for `prefers-reduced-motion` / `prefers-color-scheme` across the web assets returns no matches`
  - Impact: Users who set 'reduce motion' at the OS level still get the perpetually pulsing busy/live indicators (WCAG 2.3.3); users who rely on a light theme cannot adapt the always-dark dashboard.
  - Recommendation: Add `@media (prefers-reduced-motion: reduce)` to stop the pulse/transition animations, and honour `prefers-color-scheme` (or provide a theme toggle) for a light palette.
- **P3 - Offline runner cards dimmed with opacity .55 drops muted metadata below AA contrast** (confidence: Medium)
  - `server/web/style.css:65 - `.runner.off{opacity:.55}``
  - `server/web/style.css:2,63 - the dimmed metadata uses `--muted:#8592a6` (`.runner .rrow .rk` and `.rrv`)`
  - `computed: #8592a6 composited at 55% over the #0f1218 page background is ~#505866, a contrast ratio of ~2.6:1 (below the 4.5:1 AA minimum)`
  - Impact: The 'last run' / device metadata on offline runners (still informational — what the box last achieved) becomes hard to read for low-vision users.
  - Recommendation: Dim with a lighter overlay/opacity (or a lighter muted token) so dimmed text stays >=4.5:1, or keep offline state as a badge rather than reducing overall opacity.
- **P3 - No accessibility or visual-regression tooling or tests for any UI surface** (confidence: High)
  - `tests/test_dashboards.py:99-105 - the web 'live view' tests are source-level string matches; the docstring states 'the suite has no browser'`
  - `tests/test_dashboards.py:106-132 - assertions check for identifiers like `data-rtab=` in app.js, not rendered behaviour or a11y`
  - `repo grep (case-insensitive) for axe|pa11y|lighthouse|playwright|cypress|storybook|WCAG|a11y returns no test/config evidence in the repository`
  - Impact: There is no automated guard against keyboard/ARIA/contrast regressions in the GUI, TUI or web dashboard; the a11y gaps above can silently worsen.
  - Recommendation: Add a browser-based check (Playwright + axe-core) over the served dashboard, assert tab/focus/keyboard behaviour, and add a Lighthouse/axe CI job; include reduced-motion and a keyboard-only smoke run.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| UX-P2-001 | P2 | Web dashboard's primary interactions are mouse-only (runner cards, sortable headers, table rows) |
| UX-P2-002 | P2 | Modal dialog has no dialog semantics, no focus trap, and no focus restore |
| UX-P2-003 | P2 | No ARIA anywhere in the web dashboard; tab strip and live SSE updates are not exposed to assistive tech |
| UX-P2-004 | P2 | Canvas charts have no accessible alternative and their tooltips are pointer-only |
| UX-P2-005 | P2 | Tk GUI suppresses the keyboard focus indicator and has no keyboard accelerators |
| UX-P3-001 | P3 | No prefers-reduced-motion or prefers-color-scheme support; theme is fixed dark |
| UX-P3-002 | P3 | Offline runner cards dimmed with opacity .55 drops muted metadata below AA contrast |
| UX-P3-003 | P3 | No accessibility or visual-regression tooling or tests for any UI surface |
