# Risk Register — buddy

- Audit: repo-deep-dive (Full Hardening, profile base)
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy` — `master` @ `99abf29`
- Generated: 2026-10-03T04:18Z

Counts: **P0 0 · P1 11 · P2 24 · P3 5 · total 40**.

## P1 — High

| ID | Title | Area | Effort | Owner | Status | Patch set |
|---|---|---|---|---|---|---|
| ARCH-P1-001 | Entire game is client-authoritative with no server trust boundary | ARCH | L | backend+game | open | PS-08 (future) |
| ARCH-P1-002 | Adventure results update store but not device local state | ARCH | M | frontend | open | PS-03 |
| FEAT-P1-001 | Achievement system implemented but never invoked | FEAT | M | gameplay | open | PS-06 |
| FEAT-P1-002 | Lifecycle evolution and skills not wired into game loop | FEAT | M | gameplay | open | PS-06 |
| DATA-P1-001 | `loadGame` silently downgrades every save to version 1 | DATA | S | frontend | open | PS-04 |
| DATA-P1-002 | No runtime schema validation for loaded/imported saves | DATA | M | frontend | open | PS-04 |
| CI-P1-001 | No CI workflows; quality gate never automated | CI | S | maintainer | open | PS-01 |
| CI-P1-002 | No enforced review/required checks (branch protection unverified) | CI | S | maintainer | open | PS-01 |
| SUPPLY-P1-001 | No LICENSE; distribution rights undefined | SUPPLY | S | legal | open | PS-02 |
| FINAL-P1-001 | No release process binding artifacts to a commit | FINAL | M | maintainer | open | PS-01 |
| EXEC-P1-001 | Unresolved P1s preclude unconditional GO | EXEC | M | lead | open | — |

## P2 — Medium

| ID | Title | Area | Effort | Patch set |
|---|---|---|---|---|
| INV-P2-001 | No root README/operator docs | INV | S | PS-09 |
| INV-P2-002 | `inventory.json` contradicts the actual app | INV | S | PS-08 |
| ARCH-P2-001 | Service worker static cache name / no cache versioning | ARCH | M | PS-07 |
| ARCH-P2-002 | Guest identity weak and not restored after reload | ARCH | S | PS-03 |
| ARCH-P2-003 | Autosave module dead; persistence only on actions | ARCH | S | PS-05 |
| FEAT-P2-001 | Item catalogue/economy non-functional (no use/sell/equip) | FEAT | L | PS-06 |
| SEC-P2-001 | `importSave` performs no schema validation | SEC | M | PS-04 |
| SEC-P2-002 | No security headers/CSP | SEC | S | PS-07 |
| API-P2-001 | No API contract/versioning for planned sync | API | M | PS-08 |
| API-P2-002 | Google Fonts uncached runtime dependency + privacy | API | S | PS-07 |
| TEST-P2-001 | No component/UI tests despite RTL installed | TEST | M | PS-01/06 |
| TEST-P2-002 | Persistence layer untested | TEST | M | PS-04 |
| CI-P2-001 | No dependency/security scanning in pipeline | CI | S | PS-01 |
| SUPPLY-P2-001 | Dependencies pinned but unmanaged; aged/EOL lines | SUPPLY | M | PS-08 |
| SUPPLY-P2-002 | No SBOM/license policy/vuln scanning | SUPPLY | M | PS-08 |
| SUPPLY-P2-003 | Vendored prompt-pack provenance/IP unclear | SUPPLY | S | PS-02 |
| OBS-P2-001 | No error tracking/metrics/structured logging | OBS | M | PS-07 |
| OBS-P2-002 | No React error boundary; render error blanks app | OBS | S | PS-07 |
| HYG-P2-001 | Multiple exports defined but never used | HYG | M | PS-05 |
| HYG-P2-002 | `hashString` duplicated across two modules | HYG | S | PS-05 |
| FINAL-P2-001 | Phase reports claim "None" P0/P1 vs audit | FINAL | S | PS-09 |
| FINAL-P2-002 | No accepted/deferred-risk record or owner sign-off | FINAL | S | PS-09 |
| EXEC-P2-001 | Validation evidence manual/unbound to commit | EXEC | S | PS-01 |

## P3 — Low

| ID | Title | Area | Effort | Patch set |
|---|---|---|---|---|
| INV-P3-001 | Committed prompt-pack docs dominate repo, no index | INV | S | PS-09 |
| SEC-P3-001 | Guest identity uses non-crypto randomness | SEC | S | PS-03 |
| TEST-P3-001 | No coverage config/thresholds; empty test setup | TEST | S | PS-01 |
| OBS-P3-001 | No release/build marker at runtime | OBS | S | PS-07 |
| HYG-P3-001 | Item label typo; no enforced lint/format gate | HYG | S | PS-05 |

## Accepted / deferred risks

| ID | Decision | Owner | Date | Expiry |
|---|---|---|---|---|
| — | None recorded yet. Adopt this register; mark accepted rows here. | maintainer | — | — |

## Notes

- No P0 risks: the app is client-only with no server, accounts, or tenant data.
- ARCH-P1-001 becomes a **security P1** the moment account/cloud features ship; currently a forward-looking design risk.
- Deduplicated: identity (ARCH-P2-002 = SEC-P3-001) and save validation (SEC-P2-001 = DATA-P1-002) are linked, not double-counted in patch sets.
