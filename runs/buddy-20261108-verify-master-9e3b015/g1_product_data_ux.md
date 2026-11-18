# G1 — product/data/UX verification — `buddy` master@9e3b015

- **Run:** `buddy-20261108-verify-master-9e3b015`
- **Repository / target:** `MaineCyberTech/buddy` @ `9e3b015446b21e5b1130fce58899c0627f339a3c` (`master`, commit dated 2026-10-15T01:50:21-04:00)
- **Verified:** 2026-11-08
- **Scope:** ARCH, DATA, USE, FILE, UX, PERF, MOB (G1 only; G2 areas are out of scope for this file)
- **Method:** Static re-verification against the current checkout plus a full unit-test run. `npm test` at 9e3b015: 19 files / 185 tests passed. The suite has no InventoryScreen test, so the item-action persistence and equip-rendering paths are not covered. The btoa failure was reproduced separately with Node 20 (CJK/emoji throw InvalidCharacterError). No commits or pushes; product paths were not modified.

## Counts

| Severity | Prior | New | Total |
|---|---:|---:|---:|
| P1 | 1 | 0 | 1 |
| P2 | 5 | 3 | 8 |
| P3 | 7 | 2 | 9 |
| **Total** | **13** | **5** | **18** |

| Status | Count |
|---|---:|
| verified-fixed | 0 |
| partially-fixed | 0 |
| open | 17 |
| regressed | 0 |
| owner-accepted | 1 |

| Area | Count |
|---|---:|
| ARCH | 3 |
| DATA | 2 |
| USE | 4 |
| FILE | 2 |
| UX | 3 |
| PERF | 1 |
| MOB | 3 |

**Headline:** 12 prior open findings remain open, 1 prior P1 remains owner-accepted, and 5 new findings were added (3 P2, 2 P3). No regressions and no verified fixes in G1; the product code is unchanged between `adcf767` and `9e3b015` (only dependency/security/docs files changed).

## Re-verified findings (prior run)

| ID | Sev | Status | Finding | Evidence (current code) | Remediation |
|---|---|---|---|---|---|
| `ARCH-P1-001` | P1 | **owner-accepted** | Client is fully authoritative: no server trust boundary exists | docs/README.md:79 records ARCH-P1-001 as Deferred, owner maintainer, dated 2026-10-03, until an account/cloud mode exists.<br>next.config.js:62 uses static `output: 'standalone'`; app/ has no route handlers or server endpoints, so there is still no server authority to validate state. | Keep the dated acceptance while guest-only. Before any account/cloud mode, add a server-side validation/authority boundary and re-audit; re-confirm the acceptance at each release. |
| `ARCH-P2-001` | P2 | **open** | Inventory item actions mutate the store but are never persisted | components/device/InventoryScreen.tsx:23-30 `handleItemAction` calls `setBuddy` and `setInventory` but never calls `saveGame`.<br>Compare the other two mutation paths that do persist: components/device/MainDevice.tsx:61-88 and components/device/AdventureScreen.tsx:50-61. | After a successful `applyItemAction`, call `saveGame({ version: 2, guestId, buddy: outcome.buddy, createdAt: outcome.buddy.identity.generatedAt, updatedAt: Date.now(), inventory: outcome.inventory })` and surface saved/failed status like MainDevice. Prefer one shared `persistGame` helper so all mutation paths cannot drift; add a fake-indexeddb component test that reloads after use/sell/equip. |
| `DATA-P2-001` | P2 | **open** | Inventory item actions are not written to the save | components/device/InventoryScreen.tsx:23-30 updates only the Zustand store after `applyItemAction`.<br>lib/storage/indexeddb.ts:82-87 `exportSave` reads the persisted record; unsaved inventory/coins/item states are therefore omitted from any backup. | Persist the post-action buddy and inventory atomically (one `saveGame` call) and include inventory in the same save. Add a test that uses an item, reloads, and asserts the quantity/coins/hat survive. |
| `USE-P2-001` | P2 | **open** | Inventory actions are lost on reload (persistence gap visible to the player) | components/device/InventoryScreen.tsx:23-30 shows a success message but does not persist the action.<br>components/ui/OfflineIndicator.tsx:16 tells the player 'OFFLINE — Local saves only', which overstates durability for inventory actions. | Persist every successful item action before showing the success message (or show an explicit unsaved state). Add the same autosave-status affordance used by MainDevice and a reload test. |
| `FILE-P2-001` | P2 | **open** | Save export uses btoa and can throw on non-Latin-1 content | lib/storage/indexeddb.ts:82-87 `exportSave` returns `btoa(JSON.stringify(save))`; `importSave` at :94 decodes with `atob`.<br>The only tests are ASCII/Latin-1: lib/storage/indexeddb.test.ts:104-119; there is no Unicode nickname/emoji case. | Encode UTF-8 explicitly, e.g. `TextEncoder` -> base64 (chunked to avoid call-stack limits) and `TextDecoder` in `importSave`, or use the well-tested encodeURIComponent/unescape pattern. Keep the MAX_IMPORT_LENGTH guard and add a Unicode round-trip test (e.g. a nickname with CJK/emoji). |
| `UX-P2-001` | P2 | **open** | Pinch-zoom is disabled (viewport maximumScale=1, userScalable=false) | app/layout.tsx:41-48 exports `maximumScale: 1` and `userScalable: false`.<br>app/globals.css:32 also sets `touch-action: manipulation` on body, suppressing double-tap zoom. | Remove `maximumScale`/`userScalable` (or allow zoom to at least 5x) and change body touch-action to `pan-x pan-y pinch-zoom` (or remove the rule). Verify at 200%/400% zoom on a 320px viewport. |
| `ARCH-P3-001` | P3 | **open** | AdventureScreen mutates a state object in place instead of returning a new one | components/device/AdventureScreen.tsx:39-42 computes `newProgression` and then assigns `updatedBuddy.progression = newProgression`, mutating the object returned by `applyAdventureResult`.<br>The store is updated immediately afterwards, so the mutation is local today, but it violates the pure-transition contract used by the other engines. | Keep `applyAdventureResult` pure and have it return the incremented `totalAdventures` (or spread into a new buddy) instead of assigning to the returned object. Add an input-immutability assertion. |
| `DATA-P3-001` | P3 | **open** | applyAdventureResult mutates item objects shared with the input inventory | lib/locations/adventure.ts:131 creates only a shallow `newInventory = { ...inventory }`; `newItems = [...newInventory.items]` at :153 reuses the same item object references.<br>lib/locations/adventure.ts:155-157 then does `existing.quantity += item.quantity`, mutating the item object inside the caller's inventory (and any save snapshot holding that reference). | Copy each item before changing it (`const newItems = inventory.items.map(i => ({ ...i }))`) or replace the found entry with a new object; add a test that asserts the input inventory is unchanged after applying loot. |
| `MOB-P3-001` | P3 | **open** | Manifest relies on SVG icons flagged maskable; no PNG/apple-touch fallback | public/manifest.json:10-22 contains only `icon-192.svg` and `icon-512.svg`, both declared `purpose: "any maskable"`; there is no PNG or separate maskable-safe-zone asset.<br>app/layout.tsx:31-35 sets `appleWebApp` metadata but no `apple-touch-icon`, and public/ contains no PNG icon. | Add 192/512 PNG icons plus a dedicated maskable PNG with the 40% safe zone, an apple-touch-icon (180x180), and a manifest `id`. Keep `purpose` entries separate (`any` vs `maskable`) and validate with Lighthouse/installability checks on iOS and Android. |
| `MOB-P3-002` | P3 | **open** | Service worker caches all runtime responses without a storage budget | public/sw.js:67-74 caches every successful same-origin GET (`response.status === 200 && response.type === 'basic'`) with no entry/size cap or eviction.<br>public/sw.js:71-73 does not await or catch `cache.put`, so a QuotaExceededError becomes an unhandled rejection and can leave the cache partially populated. | Precache only the app shell and bound runtime caching (LRU/max entries or max bytes), and await/catch `cache.put` to handle QuotaExceededError. Add a synthetic large-response/quota test. |
| `PERF-P3-001` | P3 | **open** | Install-prompt detection polls on a 1s interval | components/ui/ServiceWorkerRegistration.tsx:28-37 runs `setInterval(..., 1000)` and checks `getInstallPrompt()` every second; the interval is cleared only if a prompt is found.<br>lib/offline/sw.ts:23-30 already captures `beforeinstallprompt`, but the captured event is not pushed to React/Zustand, forcing the polling workaround. | Replace the interval with an event-driven subscription: have `listenForInstallPrompt` notify a store/callback when the event fires, and clear the prompt on use/dismissal. Add a test that no timer remains after the prompt is captured. |
| `USE-P3-001` | P3 | **open** | Selling an item has no confirmation step | components/device/InventoryScreen.tsx:81-88 the SELL button calls `handleItemAction(entry.id, 'sell')` immediately; there is no confirm dialog, undo window, or disabled state.<br>Because item actions are not persisted (USE-P2-001), a reload can undo a mistaken sale before the next save; once a later care/adventure save persists it, there is no undo path. | Add a confirmation step or a short undo window for sell (and optionally for consuming rare items). Include the item name and coin value in the confirmation, and test cancel/undo. |
| `UX-P3-001` | P3 | **open** | Install prompt and offline banner can overlay content | components/ui/OfflineIndicator.tsx:10-17 renders a fixed top banner at `z-50`; components/ui/ServiceWorkerRegistration.tsx:53-62 renders a fixed bottom install button at `z-50`.<br>app/layout.tsx:60-68 and components/device/MainDevice.tsx:101-117 reserve no space for either overlay, so they cover the header/controls on short (e.g. 320px) viewports. | Reserve layout space (sticky in-flow banners or body padding that matches the banner height), honor safe-area insets, and make the install prompt dismissible. Test 320x568 and landscape. |

## New findings

| ID | Sev | Status | Finding | Evidence (current code) | Remediation |
|---|---|---|---|---|---|
| `USE-P2-002` | P2 | **open** | Equipping a hat writes an item id into identity.hat, so hats do not render and can outlive the item | lib/actions/care.ts:246-255 equip returns `identity: { ...buddy.identity, hat: def.id }`; the item ids are `flower_crown`, `tiny_glasses`, `adventurer_hat` (data/items.ts:17-19).<br>The renderer only recognizes HATS names such as `flower` and `crown` (data/hats.ts:1-22; components/device/LcdDisplay.tsx:57-83); none of the three equipable item ids is a key. Equipping therefore overwrites the buddy's generated hat (e.g. `crown`) and draws nothing.<br>components/device/MainDevice.tsx:216-218 prints the raw item id as `Hat: flower_crown`; lib/actions/items.test.ts:58-64 only asserts the item id, so the rendering mismatch is untested.<br>Selling the last copy (lib/actions/care.ts:234-243) leaves `identity.hat` pointing at the sold item id; no unequip/clear path exists. | Add an explicit item-to-hat-style mapping (or a separate `equippedAccessory` field) instead of overloading the generated-hat vocabulary; render that value in LcdDisplay and the profile, and clear/unequip when the last copy is sold. Add component tests asserting the rendered sprite/profile text, not just `identity.hat`. |
| `FILE-P2-002` | P2 | **open** | Save export/import has no user-facing entry point | lib/storage/indexeddb.ts:82-106 defines `exportSave`, `importSave`, and `getSaveMetadata`, but the only call sites are lib/storage/indexeddb.test.ts:104-147.<br>app/page.tsx:7,15-27 only imports `loadGame`/`hasSave`; app/error.tsx:4,59-67 only imports `deleteSave`. No component offers download/upload, so players cannot back up or restore a save.<br>This was already noted as a P2 in docs/buddy/reports/phases/audit-03-pwa-offline-report.md:30 but was not carried into the 20261005 findings; it is distinct from DR-P2-001 (drill evidence) and RES-P3-002 (automatic backup). | Add a Settings/Data surface with export (download a text/JSON file) and import (file picker + confirmation + reload), using the Unicode-safe codec from FILE-P2-001. Reject/confirm overwriting an existing save, and add an end-to-end export -> clear -> import test. |
| `MOB-P2-001` | P2 | **open** | No service-worker update prompt; activation deletes the old cache under a running page | public/sw.js:22-33 calls `self.skipWaiting()` during install, and public/sw.js:35-53 deletes every cache except the new one then calls `clients.claim()`.<br>lib/offline/sw.ts:1-19 only registers the worker; components/ui/ServiceWorkerRegistration.tsx:11-26 has no `updatefound`/`waiting`/`controllerchange` handling and no update UI.<br>A running page can therefore be claimed by a new worker whose cache no longer contains its old build assets, with no prompt to reload. docs/buddy/reports/phases/audit-03-pwa-offline-report.md:29 already flagged the missing update prompt as P2. | Keep the new worker waiting, show an 'update available' prompt, post `SKIP_WAITING` on acceptance, and reload on `controllerchange` (or reload before the activate handler deletes the old cache). Test with two build IDs and an open tab. |
| `USE-P3-002` | P3 | **open** | Adventure results leave mood stale | lib/locations/adventure.ts:133-140 changes energy/happiness/hunger and returns the new buddy without calling `recalculateMood`.<br>The care and item paths do recalculate (lib/actions/care.ts:283, :323), and components/device/MainDevice.tsx:132-142 displays `currentBuddy.mood`, so a buddy can show HAPPY after an adventure drops it into the low-needs range. | Call `newBuddy.mood = recalculateMood(newBuddy)` before returning from `applyAdventureResult` and add a test that covers a drop across the neutral/sad threshold. |
| `UX-P3-002` | P3 | **open** | Inventory action buttons are undersized for touch | components/device/InventoryScreen.tsx:66, :75, :84 use `px-2 py-0.5 text-[10px]`, producing roughly 20px-high controls; the tab controls at components/device/MainDevice.tsx:161-188 are also only ~27px high.<br>The controls are roughly 20px high with 10px label text: below the 24x24 CSS-px WCAG 2.5.8 target unless the spacing exception applies, and far below the 44px mobile guidance; the inventory is the densest action row on a touch-first screen. | Raise the inventory/tab controls to at least 24px (ideally 44px) with `min-h-11 py-2 text-xs` and adequate spacing; verify at 320px width and with a screen reader/keyboard. |

## Top new findings (detail)

### 1. `USE-P2-002` — equipping writes an item id into the generated-hat field

- lib/actions/care.ts:246-255 equip returns `identity: { ...buddy.identity, hat: def.id }`; the item ids are `flower_crown`, `tiny_glasses`, `adventurer_hat` (data/items.ts:17-19).
- The renderer only recognizes HATS names such as `flower` and `crown` (data/hats.ts:1-22; components/device/LcdDisplay.tsx:57-83); none of the three equipable item ids is a key. Equipping therefore overwrites the buddy's generated hat (e.g. `crown`) and draws nothing.
- components/device/MainDevice.tsx:216-218 prints the raw item id as `Hat: flower_crown`; lib/actions/items.test.ts:58-64 only asserts the item id, so the rendering mismatch is untested.
- Selling the last copy (lib/actions/care.ts:234-243) leaves `identity.hat` pointing at the sold item id; no unequip/clear path exists.

**Why P2:** the inventory advertises EQUIP, but every equipable item id (`flower_crown`, `tiny_glasses`, `adventurer_hat`) is outside the `HATS` vocabulary used by `LcdDisplay`. Equipping therefore removes the generated hat and draws nothing; the profile then prints the raw id. Selling the last copy does not clear it. The unit test only asserts `identity.hat` equals the item id, so the visible defect is invisible to the suite.

### 2. `FILE-P2-002` — save export/import is dead code

- lib/storage/indexeddb.ts:82-106 defines `exportSave`, `importSave`, and `getSaveMetadata`, but the only call sites are lib/storage/indexeddb.test.ts:104-147.
- app/page.tsx:7,15-27 only imports `loadGame`/`hasSave`; app/error.tsx:4,59-67 only imports `deleteSave`. No component offers download/upload, so players cannot back up or restore a save.
- This was already noted as a P2 in docs/buddy/reports/phases/audit-03-pwa-offline-report.md:30 but was not carried into the 20261005 findings; it is distinct from DR-P2-001 (drill evidence) and RES-P3-002 (automatic backup).

**Why P2:** the save is browser-local only, so without a download/upload entry point a storage clear, browser eviction, or device migration loses the entire game. The phase audit already called this out as P2 (`docs/buddy/reports/phases/audit-03-pwa-offline-report.md:30`), but it was not carried into the 20261005 consolidated findings. Fix this together with the Unicode codec (`FILE-P2-001`) and a confirmation before import overwrites an existing save.

### 3. `MOB-P2-001` — no service-worker update prompt

- public/sw.js:22-33 calls `self.skipWaiting()` during install, and public/sw.js:35-53 deletes every cache except the new one then calls `clients.claim()`.
- lib/offline/sw.ts:1-19 only registers the worker; components/ui/ServiceWorkerRegistration.tsx:11-26 has no `updatefound`/`waiting`/`controllerchange` handling and no update UI.
- A running page can therefore be claimed by a new worker whose cache no longer contains its old build assets, with no prompt to reload. docs/buddy/reports/phases/audit-03-pwa-offline-report.md:29 already flagged the missing update prompt as P2.

**Why P2:** `skipWaiting()` + `clients.claim()` plus deletion of older caches means a new deployment can take over a running page whose build assets are no longer cached. There is no update UI or `controllerchange` reload, so an offline/first-load-after-deploy user can get chunk failures or a mixed build. The phase audit also flagged this as P2 (`docs/buddy/reports/phases/audit-03-pwa-offline-report.md:29`).

### 4. `USE-P3-002` — mood is not recalculated after adventures

- lib/locations/adventure.ts:133-140 changes energy/happiness/hunger and returns the new buddy without calling `recalculateMood`.
- The care and item paths do recalculate (lib/actions/care.ts:283, :323), and components/device/MainDevice.tsx:132-142 displays `currentBuddy.mood`, so a buddy can show HAPPY after an adventure drops it into the low-needs range.

### 5. `UX-P3-002` — inventory controls are undersized

- components/device/InventoryScreen.tsx:66, :75, :84 use `px-2 py-0.5 text-[10px]`, producing roughly 20px-high controls; the tab controls at components/device/MainDevice.tsx:161-188 are also only ~27px high.
- The controls are roughly 20px high with 10px label text: below the 24x24 CSS-px WCAG 2.5.8 target unless the spacing exception applies, and far below the 44px mobile guidance; the inventory is the densest action row on a touch-first screen.

## Regressions

None. `git diff adcf767..9e3b015 -- app components lib data public next.config.js` is empty; the only product-path change is the `package.json`/`package-lock.json` postcss override from `1db7d77` (CI/security scope, no G1 behavior change). No prior G1 finding moved backwards or forward.

## Notes and verification caveats

- **Tests:** `npm test` at `9e3b015` passed 19 files / 185 tests. There is no `InventoryScreen` test, so the persistence gap and the equip-rendering mismatch are not covered.
- **FILE-P2-001 is latent:** `exportSave`/`importSave` have no production call site today; `btoa` throws for CJK/emoji and is therefore unsafe once the backup UI is wired. Characters inside the Latin-1 range survive `atob` as code units in a browser.
- **Persistence comparison:** `MainDevice.tsx:73-87` and `AdventureScreen.tsx:50-61` already implement the pattern `InventoryScreen` needs; the remediation is a small, localized change plus a test.
- **ARCH-P1-001:** the dated owner acceptance is still `2026-10-03` in `docs/README.md:79`; it was re-confirmed at this commit, not re-dated.
- **No owner-gated or external-state changes** are claimed here. Branch protection, release environments, and similar G2 items are covered by the G2 verification.

## Artifact

- Machine-readable findings: `g1_product_data_ux.json` (18 findings; every finding has `id`, `severity`, `title`, `status`, `evidence`, `remediation`).
