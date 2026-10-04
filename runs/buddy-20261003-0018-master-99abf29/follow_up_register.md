# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| ARCH-P1-001 | P1 | Entire game is client-authoritative with no server trust boundary |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P1-002 | P1 | Adventure results update the store but not the device component's local state |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-001 | P1 | No CI workflows, so lint/typecheck/test/build never run automatically |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-002 | P1 | No repository-enforced review/required checks (branch protection unverified) |  |  | still-open | re-audit 2026-10-04: still-open |
| DATA-P1-001 | P1 | loadGame silently downgrades every save to version 1, contradicting writers |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P1-002 | P1 | No runtime schema validation for loaded or imported saves (zod unused) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P1-001 | P1 | Unresolved P1 findings preclude an unconditional GO |  |  | still-open | re-audit 2026-10-04: still-open |
| FEAT-P1-001 | P1 | Achievement system is implemented but never invoked during gameplay |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P1-002 | P1 | Lifecycle evolution and skill progression are not wired into the game loop |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P1-001 | P1 | No release/versioning process binds artifacts to a commit |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P1-001 | P1 | No LICENSE file; distribution/derivative rights are undefined |  |  | still-open | re-audit 2026-10-04: still-open |
| API-P2-001 | P2 | No API contract or versioning discipline exists to govern the planned save-sync API |  |  | still-open | re-audit 2026-10-04: still-open |
| API-P2-002 | P2 | Google Fonts is an uncached runtime dependency with privacy implications |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-001 | P2 | Service worker uses a static cache name and no cache versioning |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-002 | P2 | Guest identity is weakly generated and not restored after reload |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-003 | P2 | Autosave module is dead code; persistence happens only on discrete actions |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-001 | P2 | No dependency or security scanning in the pipeline |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-001 | P2 | No real save migration strategy despite a version field |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P2-001 | P2 | Validation evidence is manual and unbound to the audited commit |  |  | partially-fixed | CI gate + Dependabot + CODEOWNERS + coverage thresholds; draft PR #3 awaiting human review |
| FEAT-P2-001 | P2 | Item catalogue and economy are non-functional (no use, sell, or equip) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P2-001 | P2 | Phase completion reports claim "None" P0/P1 while this audit finds unresolved P1s |  |  | partially-fixed |  |
| FINAL-P2-002 | P2 | No accepted/deferred-risk record or owner sign-off |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P2-001 | P2 | Multiple exported functions and constants are defined but never used in production |  |  | partially-fixed | hygiene + deterministic generation; draft PR #10; lab lint/typecheck/test green (110 tests), gitleaks clean |
| HYG-P2-002 | P2 | `hashString` is implemented twice with divergent callers |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-001 | P2 | No root README or operator documentation |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-002 | P2 | Provided inventory.json contradicts the actual application |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P2-001 | P2 | No error tracking, metrics, or structured logging; only console output |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P2-002 | P2 | No React error boundary, so a render error can blank the whole app |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-001 | P2 | Save import performs no schema validation (arbitrary state injection) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-002 | P2 | No HTTP security headers or Content-Security-Policy configured |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-001 | P2 | Dependencies are pinned but unmanaged and include aged/EOL lines |  |  | partially-fixed | PS-08 supply-chain + inventory hardening; draft PR #12; lab lint/typecheck/test 109 green, CycloneDX SBOM 17 components, gitleaks clean; npm audit non-clean (3 prod advisories) triaged to Dependabot/Next upgrade; API-P2-001 deferred (no server); INV-P2-002 run inventory.json corrected. |
| SUPPLY-P2-002 | P2 | No SBOM, license policy, or dependency-vulnerability scanning |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-003 | P2 | Vendored prompt-pack content has unclear provenance and third-party references |  |  | still-open | re-audit 2026-10-04: still-open |
| TEST-P2-001 | P2 | No component/UI tests despite React Testing Library being installed |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | Persistence layer (IndexedDB, save migration, import/export) is untested |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P3-001 | P3 | Content label typo and no enforced formatting/lint gate |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P3-001 | P3 | Committed prompt-pack docs dominate the repository with no index |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P3-001 | P3 | No release/build marker exposed at runtime |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P3-001 | P3 | Guest identity uses non-cryptographic randomness and is predictable |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-001 | P3 | No coverage configuration or thresholds, and test setup is empty |  |  | verified-fixed | re-audit 2026-10-04: closed |
