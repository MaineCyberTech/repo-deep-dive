# G2 — CI / security / ops verify pass — buddy @ `9e3b015`

- Repository: `MaineCyberTech/buddy` (public)
- Target: `master` @ `9e3b015446b21e5b1130fce58899c0627f339a3c` (2026-10-15)
- Verified: 2026-11-08, read-only (no commits or pushes)
- Prior run: `buddy-20261005-full-master-adcf767` (28 findings in scope)
- Method: checkout of `origin/master`, unauthenticated GitHub API checks (rulesets, environments, workflow runs/annotations), `npm audit`/`npm ls` with Node 20.19.5, and a pinned gitleaks 8.30.1 scan.

## Counts

| Dimension | Values |
|---|---|
| Prior in-scope findings | 28 (P1 3 / P2 8 / P3 17) |
| New findings | 5 (P1 1 / P2 3 / P3 1) |
| Total | 33 (P1 4 / P2 11 / P3 18) |

| Status | Count |
|---|---|
| verified-fixed | 2 |
| partially-fixed | 0 |
| open | 30 |
| regressed | 1 |
| owner-accepted | 0 |

| Area | Count |
|---|---|
| BP 2, CI 5, SC 6, DOC 4, SEC 2, RES 2, HYGIENE 2 | 23 |
| SBOM 1, INFRA 1, DR 1, IR 1, OBS 1, TEST 1, PRIV 1, CHAIN 1, EVOL 1, DET 1 | 10 |

## Status changes vs the prior audit

| Finding | Prior | Now | Why |
|---|---|---|---|
| `CI-P1-001` | partially-fixed | **regressed** | Master was green at `1db7d77` (run 37269996571) after the postcss override; `9e3b015` is red again (run 38688963905) because new production advisories fail `npm audit`. |
| `SC-P2-001` | partially-fixed | **verified-fixed** | `overrides.postcss ^8.5.28` merged; `npm ls postcss` resolves the Next copy to 8.5.28 and the advisory is gone. |
| `SC-P3-001` | open | **verified-fixed** | Reviewed `.gitleaks.toml` baseline is in-repo and used by CI/pre-commit. |
| `CI-P2-001` | open | open (worse) | dependency-review no longer skips quietly on PRs; it now hard-fails because Dependency graph is still disabled. |
| `SC-P2-002`, `SC-P2-003`, `SBOM-P3-001`, `DET-P3-001` | open | open | No repository change at `9e3b015` addressed them: Dependabot security updates/Dependency graph remain off, prompt-pack provenance is still unconfirmed, no license policy/committed SBOM exists, and the deterministic host still lacks gitleaks. |
| other 20 | open | open | No code/config change at `9e3b015` addressed them. |

## Re-verified findings (prior 28)

| ID | Sev | Title | Status | Key evidence |
|---|---|---|---|---|
| BP-P1-001 | P1 | master is unprotected | open | `/rulesets` is empty; PR #42 merged with 0 reviews while its head CI failed. |
| BP-P1-002 | P1 | `release` environment missing | open | `release.yml:30` requires it; API lists only `dev`/`development`. |
| CI-P1-001 | P1 | CI failing on master | **regressed** | Run 38688963905 security job fails at `ci.yml:75-76`; local audit: 1 critical + 2 high. |
| CI-P2-001 | P2 | dependency-review skipped/disabled | open | Annotation: “Dependency review is not supported … ensure Dependency graph is enabled.” |
| DOC-P2-001 | P2 | README says Next.js 14 | open | `README.md:27` vs `package.json:24` / lock `next@15.5.27`. |
| DOC-P2-002 | P2 | README known-gaps/testing drift | open | `README.md:19-21,105-108` contradict `care.ts:133-145`, `adventure.ts:168-176`, existing component/storage tests. |
| DR-P2-001 | P2 | no backup/restore drill | open | `release-process.md:51-67` and `release-readiness.md:40-45` have no drill; no drill artifact. |
| SC-P2-001 | P2 | postcss advisory | **verified-fixed** | `package.json:50-52`, `package-lock.json:7115-7117`; `npm ls postcss` → 8.5.28 everywhere. |
| SC-P2-002 | P2 | secret scanning/Dependabot security updates | open | Dependabot version updates pre-date the target and run; Dependency graph still off; secret scanning/push protection not evidenced. |
| SC-P2-003 | P2 | prompt-pack authorship/licensing | open | `LICENSE:1-5`/`NOTICE:20-28` pre-date the target; `docs/README.md:28-32` still says authorship/license unconfirmed. |
| SEC-P2-001 | P2 | CSP allows `unsafe-inline` | open | `next.config.js:30-31`; no nonce/hash and no dated risk acceptance. |
| CHAIN-P3-001 | P3 | client-only exploit-chain surface | open | No server/route handlers; `README.md:7-9`. |
| CI-P3-001 | P3 | `next lint` deprecated | open | `package.json:12`; CI still invokes it at `ci.yml:35-36`. |
| DET-P3-001 | P3 | gitleaks not installed | open | CI has had the pinned scanner since before `adcf767`; the deterministic host still has no gitleaks on PATH. |
| DOC-P3-001 | P3 | README gate omits build | open | `README.md:60-63` vs `ci.yml:41-48`. |
| EVOL-P3-001 | P3 | no feature-flag/plugin seam | open | Fixed screen union `lib/buddy/screens.ts:1`; no flag config. |
| HYGIENE-P3-001 | P3 | prompt pack dominates tree | open | 87/232 tracked files (~388K); no archive/submodule boundary. |
| HYGIENE-P3-002 | P3 | no `.editorconfig` | open | File absent; only line-ending policy in `.gitattributes:1-4`. |
| INFRA-P3-001 | P3 | documented controls drift from live config | open | `release-process.md:69-111` vs empty rulesets / missing `release` environment. |
| IR-P3-001 | P3 | no IR runbook/tabletop | open | `docs/README.md:12-17` has none; `release-process.md:63-67` is release rollback only. |
| OBS-P3-001 | P3 | no production error sink | open | `app/error.tsx:21-43` emits console + `buddy:error`, but no reporter is attached. |
| PRIV-P3-001 | P3 | no privacy/data-management surface | open | Only an internal privacy comment `app/error.tsx:24-28`; export/import never called by UI. |
| RES-P3-001 | P3 | unbounded SW runtime cache | open | `public/sw.js:56-75` caches every 200/basic GET with no bound/quota handling. |
| RES-P3-002 | P3 | no automated backup | open | `exportSave` exists `lib/storage/indexeddb.ts:82-87`; no UI/periodic call. |
| SBOM-P3-001 | P3 | no license policy/committed SBOM | open | `release.yml:69-70,94-101` generate/upload SBOM (pre-existing); `ci.yml:88-93` license check is a notice placeholder and no SBOM is committed. |
| SC-P3-001 | P3 | gitleaks default ruleset/no allowlist | **verified-fixed** | `.gitleaks.toml:1-61`; used by pre-commit and CI; clean scan. |
| SEC-P3-001 | P3 | guest id Math.random fallback | open | `components/hatch/HatchFlow.tsx:17-22` still falls back in non-secure contexts. |
| TEST-P3-001 | P3 | coverage excludes app/components; no E2E | open | `vitest.config.ts:17-19`; no Playwright config despite `package.json:47`. |

## New findings (5)

| ID | Sev | Title | Status | Evidence | Remediation |
|---|---|---|---|---|---|
| SC-P1-001 | P1 | Next.js 15.5.27 critical RCE + high DoS advisory | open | `package-lock.json:6574-6575` pins 15.5.27; GHSA-2464-fhr4-w9xw (CVSS 9.5, fixed 15.5.28) + GHSA-p3m5-59mp-jv5r; `npm audit` critical. | Bump next to >=15.5.28 and regenerate the lockfile; re-run audit/CI. |
| CI-P2-002 | P2 | Release workflow has no security gate | open | `release.yml:33-58` runs only install/lint/typecheck/test/build; `:91-102` packages/publishes; no audit/gitleaks/license step. | Run the security gate in the release build job or require green CI for the tagged SHA. |
| CI-P2-003 | P2 | Failed audit suppresses secret scan/license policy | open | `ci.yml:75-93`; run 38688963905 job 116270206623: Audit failed, Secret scan and License policy skipped. | Split jobs or add `if: always()` so secret scanning always runs. |
| SC-P2-004 | P2 | source-map-js 1.2.1 + zod 3.25.76 high advisories | open | Lock `:8097-8098` (GHSA-68fv-2mgg-jv7q, fixed 1.2.2) and `:9379-9380` (GHSA-mrhx-c7xc-m3w5, fixed 4.6.6); `npm audit` high. | Override/update source-map-js >=1.2.2 and zod >=4.6.6; re-run audit. |
| DOC-P3-002 | P3 | docs/README audit/licensing status stale | open | `docs/README.md:52,57-65,95-98` still cites 99abf29/no-CI/no-LICENSE; `LICENSE:1-5`, `ci.yml`, and feature wiring are current. | Update the matrix and licensing section, or archive the historical page. |

## Regression check: secret baseline and Next/postcss pin

- **`security/org-secret-baseline` (`9b2e9c0`) — no regression.** `.gitleaks.toml` uses `useDefault = true` with narrow, commented allowlists; pre-commit invokes it explicitly; CI auto-discovers it. A pinned gitleaks 8.30.1 run against the checkout reported “no leaks found” (39 commits).
- **Next/postcss pin — fixed, but superseded by new advisories.** `overrides.postcss ^8.5.28` works (`next -> postcss@8.5.28 deduped`), closing `SC-P2-001`/RA-001. However, the lockfile still pins `next@15.5.27`, `source-map-js@1.2.1`, and `zod@3.25.76`; the resulting `npm audit` failure is the current master CI regression (`CI-P1-001`).

## Top new findings

1. **SC-P1-001 — critical Next.js RCE advisory.** Practical exposure is reduced (`sharp@0.35.5` meets the advisory workaround and the app does not use `next/image`), but the production dependency is flagged critical and the release/CI gate is already red.
2. **CI-P2-003 — secret scanning is effectively off.** Since `npm audit` fails first, the gitleaks step has not run on master since `9e3b015`; the new baseline is present but not executing in the failing workflow.
3. **CI-P2-002 — releases can bypass the security gate.** The tag workflow builds and publishes without audit/secret/license checks.
4. **SC-P2-004 — two additional high advisories** remain in the production tree independent of postcss.
