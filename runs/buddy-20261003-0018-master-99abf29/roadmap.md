# Roadmap — buddy

- Audit: repo-deep-dive (Full Hardening, profile base)
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy` — `master` @ `99abf29`
- Generated: 2026-10-03T04:18Z

Themes: (1) governance, (2) save/state integrity, (3) feature wiring, (4) operations/privacy, (5) supply chain, (6) future server authority.

## 7-day plan (release conditions)

| Day | Action | Findings | Patch set |
|---|---|---|---|
| 1 | Add `.github/workflows/ci.yml` (npm ci, lint, typecheck, test, build) | CI-P1-001, TEST-P3-001 | PS-01 |
| 2 | Enable branch protection + CODEOWNERS + Dependabot | CI-P1-002, CI-P2-001 | PS-01 |
| 3 | Add `LICENSE` + `NOTICE`; classify prompt pack | SUPPLY-P1-001, SUPPLY-P2-003 | PS-02 |
| 4 | Fix save version constant + zod validation; add migration | DATA-P1-001/002, DATA-P2-001 | PS-04 |
| 5 | Restore guestId on load; crypto UUID; add reload test | ARCH-P2-002, SEC-P3-001 | PS-03 |
| 6 | Make store the single source of truth for the device | ARCH-P1-002 | PS-03 |
| 7 | Add `app/error.tsx` + error boundary; reconcile phase reports | OBS-P2-002, FINAL-P2-001 | PS-07/09 |

## 30-day plan

| Week | Action | Findings | Patch set |
|---|---|---|---|
| 1 | (above) | — | PS-01..04 |
| 2 | Wire achievements + evolution/skills; persist unlocked rewards | FEAT-P1-001/002 | PS-06 |
| 2 | Remove/consolidate dead code + duplicate `hashString`; fix typo | HYG-P2-001/002, HYG-P3-001, ARCH-P2-003 | PS-05 |
| 3 | Security headers/CSP; self-host fonts; SW cache versioning | SEC-P2-002, API-P2-002, ARCH-P2-001 | PS-07 |
| 3 | Build marker + error reporting | OBS-P2-001, OBS-P3-001 | PS-07 |
| 4 | Dependency upgrades (Next/ESLint), `engines`, SBOM + audit in CI | SUPPLY-P2-001/002, INV-P2-002 | PS-08 |
| 4 | README/CHANGELOG/data-model/testing docs | INV-P2-001, INV-P3-001 | PS-09 |

## 60-day plan

- Implement item economy: use/sell/equip, skill-book effects, shop sink (FEAT-P2-001).
- Add Playwright smoke E2E (hatch → care → adventure → reload) and component coverage thresholds.
- Add accessibility (axe) tests; consider PNG PWA icons.
- Adopt `knip`/`ts-prune` to prevent dead-code regressions.

## 90-day plan (platform evolution)

- Define versioned API contracts (API-P2-001) and choose a host (Vercel/Cloudflare).
- If accounts/cloud are committed: implement server authority for saves/adventures and Supabase RLS (ARCH-P1-001), then re-audit.
- Establish release automation: tag-driven workflow with SBOM + build id + changelog (FINAL-P1-001).

## Definition of done for the next gate (GO)

1. CI green and required on `master`; release artifacts bound to commit.
2. LICENSE present.
3. Save version consistent; saves validated; migrations tested.
4. Device state sync fixed; guestId stable.
5. Achievements/evolution wired or explicitly deferred in UI and docs.
6. Risk register reviewed with owner sign-off and accepted/deferred rows recorded.
