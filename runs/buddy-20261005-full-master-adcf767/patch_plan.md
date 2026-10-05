# Patch plan

## ARCH-P1-001 — Client is fully authoritative: no server trust boundary exists

Keep deferred while guest-only. Before any cloud/account mode, add a server-side validation boundary and re-audit. Re-confirm the dated acceptance in docs/README.md.

## BP-P1-001 — master is unprotected: no required PR, review, or status checks

Enable a master ruleset: require a PR, require the CI status check, require CODEOWNERS review, block force-push and deletion. Verify by attempting a direct push.

## BP-P1-002 — The `release` environment required by release.yml does not exist

Create the `release` environment with required reviewers and restrict it to v* tags, then verify a non-maintainer tag push waits for approval.

## CI-P1-001 — CI is failing on master at the audited commit

Upgrade to a Next.js line that bundles postcss >= 8.5.19 (or a validated override), or mark the audit step as an explicit, non-blocking risk-acceptance with a linked register entry so the workflow result is meaningful.

## ARCH-P2-001 — Inventory item actions mutate the store but are never persisted

Persist after applyItemAction (call saveGame with version 2, guestId, buddy, inventory, createdAt/updatedAt), exactly as the other two screens do.

## CI-P2-001 — dependency-review job is skipped because the dependency graph / Dependabot is disabled

Enable Dependency graph + Dependabot alerts/security updates in repository settings; verify the dependency-review job then reports a real conclusion.

## DATA-P2-001 — Inventory item actions are not written to the save

Call saveGame after a successful applyItemAction, using the same pattern as MainDevice and AdventureScreen.

## DOC-P2-001 — README states the stack is Next.js 14 but the repo is Next.js 15.5.27

Update the README stack table to the actual pinned major.

## DOC-P2-002 — README 'Known gaps' and testing sections contradict the current code/tests

Reconcile the README with the current code: mark achievements/evolution/skills wired, and update the testing section to list existing suites.

## DR-P2-001 — No backup/restore drill and no committed evidence of one

Add a restore drill to the release checklist: export a representative save, clear storage, import, and assert equality; record the artifact per release.

## FILE-P2-001 — Save export uses btoa and can throw on non-Latin-1 content

Encode with TextEncoder + base64 (or encodeURIComponent/unescape) and decode symmetrically in importSave; add a test with a Unicode nickname.

## SC-P2-001 — High-severity postcss advisory remains in the production dependency tree (accepted)

Upgrade Next.js to a line bundling postcss >= 8.5.19, or validate a root override; otherwise keep RA-001 current and re-check monthly and at expiry.

## SC-P2-002 — Repository secret-scanning and Dependabot security updates are disabled

Enable Dependency graph, Dependabot alerts + security updates, and secret scanning with push protection in repository settings.

## SC-P2-003 — Vendored prompt pack authorship and licensing are unconfirmed

Confirm author/holder and license, or remove the pack from the distribution; record the decision with an owner and date.

## SEC-P2-001 — CSP allows 'unsafe-inline' scripts and styles

Move to a nonce/hash-based script-src when Next.js supports it, or record the exception with an owner and revisit on the Next.js major upgrade.

## USE-P2-001 — Inventory actions are lost on reload (persistence gap visible to the player)

Persist on every successful item action; optionally show the autosave status like MainDevice.

## UX-P2-001 — Pinch-zoom is disabled (viewport maximumScale=1, userScalable=false)

Remove maximumScale/userScalable (or set userScalable true and allow zoom to at least 5x).

## ARCH-P3-001 — AdventureScreen mutates a state object in place instead of returning a new one

Return the incremented progression from applyAdventureResult (or spread into a new buddy) rather than assigning to the returned object.

## CHAIN-P3-001 — Exploit-chain surface is limited to save import; residual risk is client respawn

No action required while guest-only. Re-run this lens after any server/account introduction.

## CI-P3-001 — `next lint` is deprecated and will be removed in Next.js 16

Migrate to `eslint` CLI (or the codemod) before upgrading Next.js.

## DATA-P3-001 — applyAdventureResult mutates item objects shared with the input inventory

Map to new item objects before incrementing quantity.

## DET-P3-001 — [SEC] gitleaks not installed (secret scan skipped)

Install gitleaks in CI to enable the secret scan.

## DOC-P3-001 — README quality-gate command omits the build step used by CI

Document the gate CI actually enforces (lint, typecheck, test, coverage, build).

## EVOL-P3-001 — No feature-flag or plugin boundary for content/feature evolution

For future content velocity, add a typed content-loading seam and a minimal feature-flag config; not required for the current RC.

## HYGIENE-P3-001 — Vendored prompt pack dominates the repository tree

Decide: keep under a submodule/archive with confirmed license, or move out of the product repo.

## HYGIENE-P3-002 — No .editorconfig; line/format policy is split across tools

Add `.editorconfig` and, optionally, a pre-commit format check.

## INFRA-P3-001 — Documented release/CI controls drift from the live repository configuration

Add an automated settings check (gh api) to CI or a runbook step, and reconcile the docs with actual settings.

## IR-P3-001 — No incident-response runbook or tabletop exercise recorded

Add a short IR runbook (token compromise, bad release rollback, dependency emergency) and run one tabletop; store the record under docs/.

## MOB-P3-001 — Manifest relies on SVG icons flagged maskable; no PNG/apple-touch fallback

Add PNG 192/512 and a maskable PNG (with safe zone), plus apple-touch-icon and manifest id.

## MOB-P3-002 — Service worker caches all runtime responses without a storage budget

Bound the cache and handle QuotaExceededError on cache.put.

## OBS-P3-001 — Client errors are only logged locally; no production error sink is wired

Attach a privacy-respecting reporter to `buddy:error` (no save contents), or explicitly accept 'no production telemetry' in the risk register.

## PERF-P3-001 — Install-prompt detection polls on a 1s interval

Replace polling with the `beforeinstallprompt` event (already listened for in lib/offline/sw.ts) and store the captured event in the store.

## PRIV-P3-001 — No in-app privacy notice or data-management surface

Add a small settings/about surface with export, delete, and a short privacy notice.

## RES-P3-001 — Service worker caches every successful same-origin GET with no bound or eviction policy

Restrict runtime caching to immutable hashed assets, bound the cache, and use stale-while-revalidate for navigations.

## RES-P3-002 — No automated backup of the browser-local save

Provide a periodic export/backup affordance (or File System Access download) and document recovery steps.

## SBOM-P3-001 — No license policy and no committed SBOM artifact

Define an allow/deny license policy and enforce it in CI; optionally commit the per-release SBOM (or link the artifact) and resolve the LICENSE decision (SUPPLY-P1-001).

## SC-P3-001 — gitleaks runs with the default ruleset; no reviewed allowlist file in-repo

Add a reviewed `.gitleaks.toml` allowlist (or a documented false-positive registry) and use it both in CI and in deterministic runs.

## SEC-P3-001 — Guest id falls back to Math.random in non-secure contexts

Keep as documented. Ensure fallback is never used as an auth/ownership token if a server is added later.

## TEST-P3-001 — Coverage scope excludes components/ and app/; no E2E or accessibility automation

Add component/app files to the coverage scope (or a second threshold), and either add E2E + axe checks or remove the unused Playwright dependency.

## USE-P3-001 — Selling an item has no confirmation step

Add a confirm step for sell, or an undo window.

## UX-P3-001 — Install prompt and offline banner can overlay content

Reserve space or make the indicators dismissible, and test on a 320px viewport.

