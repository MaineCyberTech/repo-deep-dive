# Buddy verify register — master@9e3b015

| ID | Sev | Status | Title |
|---|---|---|---|
| ARCH-P1-001 | P1 | owner-accepted | Client is fully authoritative: no server trust boundary exists |
| BP-P1-001 | P1 | open | master is unprotected: no required PR, review, or status checks |
| BP-P1-002 | P1 | open | The `release` environment required by release.yml does not exist |
| CI-P1-001 | P1 | regressed | CI is failing on master at the audited commit |
| SC-P1-001 | P1 | open | Next.js 15.5.27 carries a critical RCE advisory and a high DoS advisory |
| ARCH-P2-001 | P2 | open | Inventory item actions mutate the store but are never persisted |
| CI-P2-001 | P2 | open | dependency-review job is skipped because the dependency graph / Dependabot is disabled |
| CI-P2-002 | P2 | open | Release workflow packages and publishes without the security gate |
| CI-P2-003 | P2 | open | Security job skips secret scan and license policy whenever npm audit fails |
| DATA-P2-001 | P2 | open | Inventory item actions are not written to the save |
| DOC-P2-001 | P2 | open | README states the stack is Next.js 14 but the repo is Next.js 15.5.27 |
| DOC-P2-002 | P2 | open | README 'Known gaps' and testing sections contradict the current code/tests |
| DR-P2-001 | P2 | open | No backup/restore drill and no committed evidence of one |
| FILE-P2-001 | P2 | open | Save export uses btoa and can throw on non-Latin-1 content |
| FILE-P2-002 | P2 | open | Save export/import has no user-facing entry point |
| MOB-P2-001 | P2 | open | No service-worker update prompt; activation deletes the old cache under a running page |
| SC-P2-001 | P2 | verified-fixed | High-severity postcss advisory remains in the production dependency tree (accepted) |
| SC-P2-002 | P2 | open | Repository secret-scanning and Dependabot security updates are disabled |
| SC-P2-003 | P2 | open | Vendored prompt pack authorship and licensing are unconfirmed |
| SC-P2-004 | P2 | open | Additional high advisories in production dependencies: source-map-js 1.2.1 and zod 3.25.76 |
| SEC-P2-001 | P2 | open | CSP allows 'unsafe-inline' scripts and styles |
| USE-P2-001 | P2 | open | Inventory actions are lost on reload (persistence gap visible to the player) |
| USE-P2-002 | P2 | open | Equipping a hat writes an item id into identity.hat, so hats do not render and can outlive the item |
| UX-P2-001 | P2 | open | Pinch-zoom is disabled (viewport maximumScale=1, userScalable=false) |
| ARCH-P3-001 | P3 | open | AdventureScreen mutates a state object in place instead of returning a new one |
| CHAIN-P3-001 | P3 | open | Exploit-chain surface is limited to save import; residual risk is client respawn |
| CI-P3-001 | P3 | open | `next lint` is deprecated and will be removed in Next.js 16 |
| DATA-P3-001 | P3 | open | applyAdventureResult mutates item objects shared with the input inventory |
| DET-P3-001 | P3 | open | [SEC] gitleaks not installed (secret scan skipped) |
| DOC-P3-001 | P3 | open | README quality-gate command omits the build step used by CI |
| DOC-P3-002 | P3 | open | docs/README audit reconciliation and licensing status are stale |
| EVOL-P3-001 | P3 | open | No feature-flag or plugin boundary for content/feature evolution |
| HYGIENE-P3-001 | P3 | open | Vendored prompt pack dominates the repository tree |
| HYGIENE-P3-002 | P3 | open | No .editorconfig; line/format policy is split across tools |
| INFRA-P3-001 | P3 | open | Documented release/CI controls drift from the live repository configuration |
| IR-P3-001 | P3 | open | No incident-response runbook or tabletop exercise recorded |
| MOB-P3-001 | P3 | open | Manifest relies on SVG icons flagged maskable; no PNG/apple-touch fallback |
| MOB-P3-002 | P3 | open | Service worker caches all runtime responses without a storage budget |
| OBS-P3-001 | P3 | open | Client errors are only logged locally; no production error sink is wired |
| PERF-P3-001 | P3 | open | Install-prompt detection polls on a 1s interval |
| PRIV-P3-001 | P3 | open | No in-app privacy notice or data-management surface |
| RES-P3-001 | P3 | open | Service worker caches every successful same-origin GET with no bound or eviction policy |
| RES-P3-002 | P3 | open | No automated backup of the browser-local save |
| SBOM-P3-001 | P3 | open | No license policy and no committed SBOM artifact |
| SC-P3-001 | P3 | verified-fixed | gitleaks runs with the default ruleset; no reviewed allowlist file in-repo |
| SEC-P3-001 | P3 | open | Guest id falls back to Math.random in non-secure contexts |
| TEST-P3-001 | P3 | open | Coverage scope excludes components/ and app/; no E2E or accessibility automation |
| USE-P3-001 | P3 | open | Selling an item has no confirmation step |
| USE-P3-002 | P3 | open | Adventure results leave mood stale |
| UX-P3-001 | P3 | open | Install prompt and offline banner can overlay content |
| UX-P3-002 | P3 | open | Inventory action buttons are undersized for touch |
