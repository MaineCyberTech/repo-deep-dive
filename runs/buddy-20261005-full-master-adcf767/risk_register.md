# Follow-up register

Run: `buddy-20261005-full-master-adcf767` · Target: `buddy` @ `adcf767` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| ARCH-P1-001 | P1 | Client is fully authoritative: no server trust boundary exists | @owner | ARCH | owner-accepted | owner-accepted: deferred while guest-only; dated acceptance in docs/README.md. Residual: no server trust boundary until an account/cloud mode adds one. |
| BP-P1-001 | P1 | master is unprotected: no required PR, review, or status checks | @owner | BP | open | owner-gated: enable a master ruleset (required PR + CI status check + CODEOWNERS review; block force-push/deletion). Proposal in docs/release-process.md. No infra changed. Residual: master remains directly pushable/unprotected. |
| BP-P1-002 | P1 | The `release` environment required by release.yml does not exist | @owner | BP | open | owner-gated: create the `release` environment with required reviewers restricted to v* tags. Proposal in docs/release-process.md. No infra changed. Residual: release.yml has no approval gate. |
| CI-P1-001 | P1 | CI is failing on master at the audited commit | @owner | CI | partially-fixed | Draft PR MaineCyberTech/buddy#35 (remediation/buddy-CI-P1-001) adds a root npm overrides.postcss ^8.5.28 so the copy under next is patched; CI security gate green. Verified-fixed only on merge. |
| ARCH-P2-001 | P2 | Inventory item actions mutate the store but are never persisted | @owner | DATA | open |  |
| CI-P2-001 | P2 | dependency-review job is skipped because the dependency graph / Dependabot is disabled | @owner | CI | open |  |
| DATA-P2-001 | P2 | Inventory item actions are not written to the save | @owner | DATA | open |  |
| DOC-P2-001 | P2 | README states the stack is Next.js 14 but the repo is Next.js 15.5.27 | @owner | DOC | open |  |
| DOC-P2-002 | P2 | README 'Known gaps' and testing sections contradict the current code/tests | @owner | DOC | open |  |
| DR-P2-001 | P2 | No backup/restore drill and no committed evidence of one | @owner | DR | open |  |
| FILE-P2-001 | P2 | Save export uses btoa and can throw on non-Latin-1 content | @owner | FILE | open |  |
| SC-P2-001 | P2 | High-severity postcss advisory remains in the production dependency tree (accepted) | @owner | SC | partially-fixed | Same root cause as CI-P1-001; overrides.postcss ^8.5.28 validated in buddy#35 and RA-001 closed. Verified-fixed only on merge. |
| SC-P2-002 | P2 | Repository secret-scanning and Dependabot security updates are disabled | @owner | SC | open |  |
| SC-P2-003 | P2 | Vendored prompt pack authorship and licensing are unconfirmed | @owner | SC | open |  |
| SEC-P2-001 | P2 | CSP allows 'unsafe-inline' scripts and styles | @owner | SEC | open |  |
| USE-P2-001 | P2 | Inventory actions are lost on reload (persistence gap visible to the player) | @owner | USE | open |  |
| UX-P2-001 | P2 | Pinch-zoom is disabled (viewport maximumScale=1, userScalable=false) | @owner | UX | open |  |
| ARCH-P3-001 | P3 | AdventureScreen mutates a state object in place instead of returning a new one | @owner | ARCH | open |  |
| CHAIN-P3-001 | P3 | Exploit-chain surface is limited to save import; residual risk is client respawn | @owner | CHAIN | open |  |
| CI-P3-001 | P3 | `next lint` is deprecated and will be removed in Next.js 16 | @owner | CI | open |  |
| DATA-P3-001 | P3 | applyAdventureResult mutates item objects shared with the input inventory | @owner | DATA | open |  |
| DET-P3-001 | P3 | [SEC] gitleaks not installed (secret scan skipped) | @owner | DET | open |  |
| DOC-P3-001 | P3 | README quality-gate command omits the build step used by CI | @owner | DOC | open |  |
| EVOL-P3-001 | P3 | No feature-flag or plugin boundary for content/feature evolution | @owner | EVOL | open |  |
| HYGIENE-P3-001 | P3 | Vendored prompt pack dominates the repository tree | @owner | HYGIENE | open |  |
| HYGIENE-P3-002 | P3 | No .editorconfig; line/format policy is split across tools | @owner | HYGIENE | open |  |
| INFRA-P3-001 | P3 | Documented release/CI controls drift from the live repository configuration | @owner | INFRA | open |  |
| IR-P3-001 | P3 | No incident-response runbook or tabletop exercise recorded | @owner | IR | open |  |
| MOB-P3-001 | P3 | Manifest relies on SVG icons flagged maskable; no PNG/apple-touch fallback | @owner | MOB | open |  |
| MOB-P3-002 | P3 | Service worker caches all runtime responses without a storage budget | @owner | MOB | open |  |
| OBS-P3-001 | P3 | Client errors are only logged locally; no production error sink is wired | @owner | OBS | open |  |
| PERF-P3-001 | P3 | Install-prompt detection polls on a 1s interval | @owner | PERF | open |  |
| PRIV-P3-001 | P3 | No in-app privacy notice or data-management surface | @owner | PRIV | open |  |
| RES-P3-001 | P3 | Service worker caches every successful same-origin GET with no bound or eviction policy | @owner | RES | open |  |
| RES-P3-002 | P3 | No automated backup of the browser-local save | @owner | RES | open |  |
| SBOM-P3-001 | P3 | No license policy and no committed SBOM artifact | @owner | SBOM | open |  |
| SC-P3-001 | P3 | gitleaks runs with the default ruleset; no reviewed allowlist file in-repo | @owner | SC | open |  |
| SEC-P3-001 | P3 | Guest id falls back to Math.random in non-secure contexts | @owner | SEC | open |  |
| TEST-P3-001 | P3 | Coverage scope excludes components/ and app/; no E2E or accessibility automation | @owner | TEST | open |  |
| USE-P3-001 | P3 | Selling an item has no confirmation step | @owner | USE | open |  |
| UX-P3-001 | P3 | Install prompt and offline banner can overlay content | @owner | UX | open |  |
