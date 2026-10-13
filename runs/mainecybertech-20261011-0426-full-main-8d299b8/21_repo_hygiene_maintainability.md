# 21_repo_hygiene_maintainability — Prompt 21 - Repository Hygiene, Maintainability, and Code Health Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `21_repo_hygiene_maintainability.md` (area HYGIENE, prompt)

## Verification Performed

# Repository Hygiene, Maintainability, and Code Health Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (`/tmp/opencode/mct-audit-target`, read-only)
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11
- Auditor: domain subagent 21 (HYGIENE), full-pass rerun
- Area code: HYGIENE (previous register rows used `HYG`; verification rows keep their original titles)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/21_repo_hygiene_maintainability.md`
- Scope limitations: read-only static review; `node`, `pnpm` and `rg` are not installed on the audit host, so repo guards were re-implemented in short Python/`git grep` snippets and marked as such; no build, test, install or typecheck was run.

## Scope

Reviewed at `8d299b8d`: folder/file naming, duplicate/dead/unused code, generated and build artifacts, imports and circular dependencies, large files/components, type safety/`any`, error handling, TODO/FIXME, logging consistency, config sprawl, competing patterns, package scripts, dependency boundaries, test utilities, docs drift, changelog/ADRs. Not reviewed: runtime behaviour, database state, live GitHub settings, and anything requiring a build (typecheck/lint/test execution). Cross-domain rows (DOC, ACM, RLS, INV, AI) were not duplicated; where a previous row is owned by another area it was left to that owner (see Open Questions).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git ls-files`, `git ls-files -s`, `git ls-files --eol`, `du -cb` | inventory | file set, exec bits, EOLs, corpus size | 2,823 tracked files; 19 `.sh` all 100755; 0 CRLF files |
| `prompts/manifest.json` + `scripts/verify-prompts.js` algorithm | generated artifact | pinning guard | Python replica (utf8 + CRLF-normalise SHA-256): 630/630 match, 0 mismatches |
| `apps/api/src/data/products.json` vs `apps/web/lib/catalog/data/products.json` (+2 pack copies) | data | duplicate catalogs | 245 common SKUs, 245 differ in 6 fields; 3 distinct copies |
| Import-graph scan (Python, relative + `@/` + `@mct/*`) | code | circular deps / boundaries | 756 files with local imports; 1 cycle; 0 cross-app imports |
| Orphan scan (exact symbol grep) over `apps/**`, `packages/**` | code | dead code | 3 dead lib modules, 1 dead component, 7 dead scripts, 1 dead duplicate snippet |
| `apps/web/components/admin/AdminDocumentsCenterClient.tsx` | code | large component | 2,322 lines, one component, 26 state/effect hooks |
| ESLint/TS configs (`apps/*/eslint.config.*`, `packages/config/tsconfig.base.json`) | config | type safety, unused vars | `strict: true`; `no-explicit-any` off; `no-unused-vars` warn |
| `.gitignore`, `.github/actions/dependency-audit/action.yml`, `validate.yml` | CI/config | generated artifacts + exec-bit guard | licenses/SBOM untracked and gated; exec-bit gate present |
| `scripts/README.md` vs `scripts/` listing | docs | docs drift | 14 scripts (10 active guards) undocumented; "Last updated 2026-08-01" |
| `docs/audits/README.md` + run directories | docs/artifacts | artifact layout contract | 3 repo-deep-dive runs lack `report.md`; Runs table omits them |
| `AGENTS.md` / `review.md` / `CHANGELOG.md` / `docs/adr/README.md` | docs | agent contract, changelog/ADRs | AGENTS.md 1,003 lines/120 KB; review.md generated mirror; 11 ADRs (7 table-only, disclosed) |
| Markdown link check (Python replica of `check-docs-links.mjs`, extended to all 294 non-audit md) | docs | docs drift | 0 broken links |
| Previous run `follow_up_register.md` HYG rows + `PORT-P2-001` | register | verification duty | re-verified at 8d299b8d (table below) |

## Verification Performed

| Command / check | Observed result |
|---|---|
| `git ls-files -s '*.sh' \| awk '{print $1}' \| sort \| uniq -c` | `19 100755`, 0 files at 100644 → PORT-P2-001 fixed |
| `sed -n '19,31p' .github/workflows/validate.yml` | exec-bit guard present (PORT-001), fails the deploy gate on any 100644 `.sh` |
| Python replica of `scripts/verify-prompts.js` verify | 630/630 manifest hashes match at 8d299b8d; 0 missing/added/changed |
| Python structural diff of the four `products.json` copies | API vs web: 245/245 differ (6 fields each); pack data vs pack repo_patch: byte-identical; both differ from the apps |
| `git grep -nE '\bgenerateProposal\b' \| grep -v proposal-actions.ts` | 0 hits → dead stub confirmed |
| `git grep -n 'isFeatureEnabled\|getFeatureFlags\|navClass'` (all tracked files) | 0 hits outside their defining files |
| Whole-tree orphan scan for `apps/web/components/**` | 1 unreferenced component: `CategoryVisualHeader.tsx` |
| Import-cycle DFS (Python) | 1 cycle: `apps/worker/src/metrics.ts` ↔ `apps/worker/src/task-registry.ts` |
| `git grep -c 'supabase as any' -- apps/api/src` | 63 casts; 76 `any`-ish lines in API non-test code |
| `git ls-files \| grep -E '__pycache__\|\.pyc$'` | 7 committed `.pyc` files; `.gitignore` has no entry |
| `cat apps/web/public/version.json` | tracked stale artifact: `{"sha":"unknown","date":"2026-08-05..."}`; rewritten by `apps/web/scripts/generate-version.js` at build |
| `md5sum "supabase/snippets/Untitled query 314.sql" supabase/seeds/00_local_auth_users.corrected.v2.sql` | identical (`493f2c58...`) → dead duplicate |
| `git grep -l` per script name across `.github/`, `package.json`, `apps/`, `packages/` | 7 scripts with 0 references (content-map pipeline) |
| Docs link check (294 non-audit md files) | 0 broken links |
| Machine-path grep `C:\\Users\|C:\\temp` in tracked docs | 3 files still carry machine paths (AGENTS.md/review.md fixed) |
| `git ls-files -s` on licenses/SBOM names + `sed -n '31,40p' .github/actions/dependency-audit/action.yml` | guard present, artifacts untracked → HYG-P3-002 holds |
| `git ls-files -s` mode audit + guard inspection | PORT-P2-001 verified-fixed |
| Dead-RLS-key scan (effective-policy extraction + permission catalog + role grants) | No live policy references a catalog-absent permission pair except on tables dropped by 5302055; `documents/tickets/projects:manage` were replaced by 5302129 → residual belongs to the ACM/RLS domains (already filed there) |

### Verification duty — previous register rows

| Previous row | Re-verified at 8d299b8d | Status |
|---|---|---|
| HYG-P2-001 Committed prompt/audit corpus bloats the repo and review surface | Prior-run snapshots removed (PROVENANCE.md note), manifest verifies clean; 632 files / 9.4 MB remain committed | partially-fixed |
| HYG-P2-002 Duplicate product catalogs have diverged | 245/245 SKUs differ; AGENTS.md documents it as open debt; no sync/guard added | partially-fixed |
| HYG-P3-001 Stale and machine-specific generated documentation | AGENTS.md:3/review.md:9 fixed (3e53b3da); GAP_ANALYSIS.md:149, MT-P0-001:5 and REAUDIT_REPORT_20261004.md:9-10 still carry `C:\temp` paths | partially-fixed (was verified-fixed) |
| HYG-P3-002 Generated artifacts are inconsistently tracked | licenses/SBOM untracked + guard in dependency-audit action wired to test.yml/validate.yml | verified-fixed |
| PORT-P2-001 17 tracked shell scripts lack the exec bit | 19/19 `.sh` now 100755; validate.yml:19-31 guard | verified-fixed |

## Executive Summary

The repo's *guards* are unusually good: exec bits, prompt provenance, docs links/counts, generated DB types, OpenAPI coverage, review.md mirror and SBOM/license tracking are all machine-checked in CI, and every one of those checks reproduces clean at `8d299b8d`. Docs links: 0 broken across 294 markdown files. Dependency boundaries are clean (no cross-app imports, single lockfile versions). TODO/FIXME debt is essentially zero in source (1 ops note).

The *debt* is concentrated in three places. First, duplication: the product catalog exists in four files with three different contents, and the API copy is a stale generation of the web copy. Second, orphans: three dead lib modules, one dead component, seven unreferenced one-off scripts plus their 1.2 MB content-map pipeline, and a stray duplicate seed snippet. Third, generated artifacts that escaped the otherwise-good gates: seven committed `.pyc` files and a stale `apps/web/public/version.json`. One 2,322-line component is the main complexity hotspot; one benign import cycle exists in the worker with no cycle-detection tooling.

Recommended next actions: delete the dead modules/scripts/component and the stray snippet (single cleanup PR), reconcile the catalog copies behind one canonical source, add `__pycache__`/`version.json` handling, fix the known-broken `sbom:licenses` script, and split `AdminDocumentsCenterClient.tsx`.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Prompt corpus | `prompts/` (632 files, 9.4 MB) | vendored prompt packs + generated outputs | pinned (630 files in manifest), documented in PROVENANCE.md | Low | owner decision to externalise; HYG-P2-001 |
| Audit outputs | `docs/audits/` (75 files, 2.7 MB) | published audit runs | 3 repo-deep-dive runs lack `report.md`; Runs table incomplete | Low | layout finding |
| Product catalogs | `apps/api/src/data/products.json`, `apps/web/lib/catalog/data/products.json`, 2 pack copies | store catalog content | 4 copies / 3 contents; API copy stale | Medium | HYG-P2-002 |
| Dead modules | `apps/api/src/lib/feature-flags.ts`, `apps/web/lib/catalog/proposal-actions.ts`, `apps/web/lib/subnav-styles.ts` | unused helpers/stubs | 0 references | Low | delete |
| Dead component | `apps/web/components/store/CategoryVisualHeader.tsx` | category header UI | 0 imports | Low | delete |
| Orphan scripts | `scripts/{apply-content-map,fix-*,generate-details,generate-fulfillment,generate-product-content}.js` + `scripts/content-map*/` | one-off catalog tooling | 0 references; 490/490 ids already baked in | Medium (destructive) | archive/delete |
| Generated artifacts | `apps/web/public/version.json`, `prompts/**/__pycache__/*.pyc` (7) | build output / bytecode | tracked and stale | Low | new finding |
| Duplicate snippet | `supabase/snippets/Untitled query 314.sql` | dev auth seed copy | byte-identical to `seeds/00_local_auth_users.corrected.v2.sql` | Low | delete |
| Guards (strengths) | `.github/actions/unit-tests`, `dependency-audit`, `validate.yml` | CI hygiene gates | all reproduce clean | — | see scorecard |
| Large component | `apps/web/components/admin/AdminDocumentsCenterClient.tsx` | admin documents center | 2,322 lines, 26 hooks | Medium | split |
| Agent contract | `AGENTS.md` + generated `review.md` | agent/reviewer reference | 1,003 lines / 120 KB each, half is history | Low | trim |
| Config set | 7 tsconfigs, 4 eslint, 4 jest, 2 vercel, 2 compose, 4 env examples | monorepo config | bounded and documented; two Redis clients in API | Low | minor |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Folder/file naming | 4 | kebab-case throughout apps; `tools/` holds one file while `scripts/` holds 50 | `supabase/snippets/Untitled query 314.sql`; `(2)`/`(3)` vendored names | delete stray snippet; keep vendored names as-is (pinned) |
| Duplicate/dead/unused code | 2 | 3 dead modules, 1 dead component, 7 dead scripts, 1 dead snippet, 4 catalog copies | no dead-code lint; one-off scripts undocumented | cleanup PR + orphan check |
| Generated/build artifacts | 3 | DB types/OpenAPI/review/manifest/licenses/SBOM all gated and green | `.pyc` + stale `version.json` tracked | ignore + untrack; extend gate |
| Imports and circular deps | 3 | 756-file graph, 1 cycle, 0 cross-app imports | no madge/eslint-plugin-import | break cycle; add report-only check |
| Large files/components | 3 | 1 component >2,300 lines; 4 modules 1,000–1,700 | no size lint | split AdminDocumentsCenterClient |
| Type safety/`any` usage | 3 | `strict: true`, 0 ts-ignore, sanctioned `db-types.ts` helpers | `no-explicit-any` off; 63 `supabase as any` | type `loadOwned`; warn on new `any` |
| Error handling | 4 | no empty catch blocks in source; structured logging at 805 catch sites; 15 justified disables | not exhaustively reviewed per route | keep; API domain owns response semantics |
| TODO/FIXME | 5 | 1 real TODO (`infra/digitalocean/docker-compose.yml:245`, digest re-pin note); placeholders only in tests | none | keep the TODO discipline |
| Logging consistency | 4 | pino (api/worker), server pino + client logger (web); 2 `console.log` in build/env tooling | 4 logger modules | acceptable; document web split |
| Config sprawl | 4 | bounded config set with shared base tsconfig/eslint; two `vercel.json`/compose files documented as intentional | two Redis client libs | consolidate Redis |
| Competing patterns | 3 | CJS `.js` vs ESM `.mjs` in scripts; node-redis + ioredis; two Vercel configs | no standard for new scripts | state ESM-only for new scripts |
| Package scripts | 3 | all targets exist; `sbom:licenses` known-broken; two PowerShell-only root scripts | stale script not fixed | point to `collect-licenses.mjs` |

Overall: **3.2 / 5** — well-guarded but carrying real duplication/orphan debt.

## Detailed Review

### Item: Product catalog duplication

- Evidence: four copies; 245/245 SKUs differ in 6 content fields between API and web; pack copies byte-identical to each other; no guard.
- What it does: web storefront imports `apps/web/.../products.json`; API fallback and `scripts/seed-store.ts` read `apps/api/src/data/products.json`; the pack keeps an unapplied `repo_patch/` copy.
- Risks: user-visible copy differs by surface; silent drift on every edit; destructive one-off generators target the web copy.
- Recommended improvement: canonical file + generated copies, or delete the API copy and read through the DB/seed.

### Item: Dead code inventory

- Evidence: exact-symbol greps; orphan scan; git history shows last touches 2026-07-25…07-30.
- Current controls: none (no dead-code lint; `no-unused-vars` is only a warning in app configs and lint-staged `--max-warnings=0` only covers staged files).
- Recommended improvement: delete in one PR; add `knip`/`ts-prune` as a report-only CI job.

### Item: Generated artifacts

- Evidence: `.gitignore` + dependency-audit guard for licenses/SBOM; manifest pins `.pyc`; `version.json` stale; `generate-version.js` rewrites it at build.
- Recommended improvement: untrack `.pyc` and `version.json`; extend the existing "stay untracked" guard pattern rather than inventing a new one.

### Item: CI guard suite (strength)

- Evidence: `unit-tests` action runs OpenAPI validation + coverage audit, docs counts, docs links, DB types check, `verify-rls.mjs`, `check-rls-predicate.mjs`, `sync-review-md.mjs --check`; `dependency-audit` runs license/SBOM gates; `validate.yml` adds exec-bit and required-check parity checks; prompt provenance is pinned.
- Verification: docs links 0 broken; manifest 630/630; catalog/route/openapi path parity holds; exec bits 19/19.
- Gap: no circular-dependency check, no dead-code check, no size check.

### Item: AGENTS.md / review.md

- Evidence: 1,003 lines each; history from line 339; generated mirror guarded.
- Recommended improvement: keep contract + current debt in AGENTS.md; move session logs to CHANGELOG/docs/audits.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| HYGIENE-001 | Folder/file naming | 4 spaced filenames | none | stray snippet | P3 | delete snippet |
| HYGIENE-002 | Duplicate/dead/unused code | 4 dead modules, 7 dead scripts | none | no lint | P3 | cleanup PR |
| HYGIENE-003 | Generated/build artifacts | `.pyc`, `version.json` | licenses/SBOM gate only | two classes untracked-free | P3 | extend ignore/gate |
| HYGIENE-004 | Imports and circular deps | 1 cycle | none | no tool | P3 | break + report check |
| HYGIENE-005 | Large files/components | 2,322-line component | none | no size lint | P2 | split |
| HYGIENE-006 | Type safety/any usage | 63 casts; any off | strict base + helpers | lint silent | P3 | type `loadOwned` |
| HYGIENE-007 | Error handling | no empty catches | logger + Sentry | — | — | keep |
| HYGIENE-008 | TODO/FIXME | 1 TODO | review discipline | — | — | keep |
| HYGIENE-009 | Logging consistency | 4 logger modules | per-runtime split | minor | P3 | document |
| HYGIENE-010 | Config sprawl | bounded set | shared base configs | 2 Redis libs | P3 | consolidate |
| HYGIENE-011 | Competing patterns | CJS/ESM mix | none stated | new-script drift | P3 | ESM-only rule |
| HYGIENE-012 | Package scripts | `sbom:licenses` broken | CI uses correct path | stale script | P3 | fix script |

## Findings

Findings are in the machine-readable companion (`21_repo_hygiene_maintainability.json`); titles:

- P2 — AdminDocumentsCenterClient.tsx is a 2,322-line single component
- P2 — Committed prompt/audit corpus bloats the repo and review surface *(verification: partially-fixed)*
- P2 — Duplicate product catalogs have diverged *(verification: partially-fixed)*
- P2 — 17 tracked shell scripts lack the exec bit; documented `./scripts/...` commands fail *(verification: verified-fixed)*
- P3 — Stale and machine-specific generated documentation *(verification: partially-fixed, downgraded from verified-fixed)*
- P3 — Generated artifacts are inconsistently tracked *(verification: verified-fixed)*
- P3 — Dead modules and a dead component with zero references
- P3 — Orphaned one-off catalog scripts and their 1.2 MB content-map pipeline
- P3 — Committed Python bytecode and a stale build artifact are tracked
- P3 — Stray duplicate snippet file with local dev auth seed data
- P3 — Root package script `sbom:licenses` is known-broken on the pinned pnpm
- P3 — `scripts/README.md` index is stale: 14 scripts (10 active CI guards) are undocumented
- P3 — No circular-dependency guard; one live import cycle in the worker
- P3 — Explicit `any` is lint-disabled and 63 `supabase as any` casts sit at the typed-client boundary
- P3 — AGENTS.md (120 KB) doubles as a historical changelog and is mirrored into review.md
- P3 — Audit run layout contract is not met by the committed repo-deep-dive runs
- P3 — Two Redis client libraries coexist in apps/api

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Catalog edits applied to only one copy | P2 | High | User-visible copy mismatch by surface | 245/245 divergent SKUs | canonical source + guard |
| One-off generator re-run overwrites enriched catalog | P2 | Low | Content loss in a 2.5 MB hand-edited file | `generate-details.js:263-264` unlink/rename | archive scripts |
| Dead stubs read as real features | P3 | Medium | Wasted work, false expectations | `proposal-actions.ts` returns `ok:true` | delete |
| Dead predicates/policies mislead RLS reviewers | P3 | Medium | Future widening on a dead clause | ACM/RLS domains (not duplicated) | catalog lint |
| Stale version served in non-standard deploys | P3 | Low | Support confusion | `version.json` `sha:unknown` | generate at deploy |

## Recommendations

### Immediate / Release Blocking

None. No finding in this domain blocks release; the P2s are maintainability debt, not correctness failures.

### This Week

- Delete the dead modules/component and the stray snippet (one PR, low risk).
- Fix `sbom:licenses` to call `scripts/collect-licenses.mjs`.
- Untrack `.pyc` + `version.json`; extend `.gitignore`; regenerate the prompt manifest.

### This Month

- Reconcile the catalog copies behind one canonical source (content owner + web/API).
- Split `AdminDocumentsCenterClient.tsx`; type `loadOwned` and drop the 63 `supabase as any` casts.
- Archive the one-off catalog scripts and content-map directories.

### Later / Platform Evolution

- Add report-only CI jobs for circular deps, dead code and file size, then ratchet.
- Trim AGENTS.md to a current-state contract; keep history in CHANGELOG/docs/audits.
- Align `docs/audits/README.md` with the actual run layout; regenerate the scripts index.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Delete 3 dead modules + 1 component | removes misleading stubs | `feature-flags.ts`, `proposal-actions.ts`, `subnav-styles.ts`, `CategoryVisualHeader.tsx` | `pnpm lint && pnpm typecheck` |
| Delete stray snippet | removes duplicate seed + credential copy | `supabase/snippets/Untitled query 314.sql` | `git ls-files supabase/snippets` |
| `git rm` `.pyc`, ignore `__pycache__` | removes generated binaries from the pin | 7 files + `.gitignore` | `node scripts/verify-prompts.js generate && verify` |
| Fix `sbom:licenses` | one-line, matches CI | `package.json` | `pnpm sbom:licenses && node scripts/license-gate.mjs` |
| Untrack `version.json` | removes stale artifact | `apps/web/public/version.json`, `.gitignore` | `pnpm --filter=web build` |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Canonical catalog + generated copies | P2 | content owner + web/API | M | product decision |
| Split AdminDocumentsCenterClient | P2 | web principal engineer | M | existing tests |
| Circular-dep + dead-code + size CI checks | P3 | repo maintainer | S–M | none |
| Machine-path lint for tracked markdown | P3 | repo maintainer | S | `check-docs-links.mjs` |
| AGENTS.md trim | P3 | repo maintainer | M | none |
| Redis client consolidation | P3 | API principal engineer | S | none |

## Suggested Tests

- **CI/static:** a markdown gate that fails on `C:\` / `file:///C:` in tracked docs; a catalog-identity test asserting the API and web catalogs are byte-identical or generated from one file; `madge --circular` (or `import/no-cycle`) as a report-only job; a scripts-index check (scripts/ ↔ scripts/README.md).
- **Unit:** none required for the deletions; add a `loadOwned` type-level test that would fail if the `as any` casts return.
- **Regression:** keep `verify-prompts.js verify`, `sync-review-md.mjs --check`, `check-docs-links.mjs` and the exec-bit guard green — they are the regression net for this domain.
- **Manual:** after untracking `version.json`, build web once and confirm `public/version.json` is regenerated with the current SHA.

## Suggested Documentation Updates

- `scripts/README.md` — regenerate the index; mark one-off scripts historical; add the 10 CI guards.
- `docs/audits/README.md` — align the layout contract/Runs table with the committed run artifacts (or add `report.md`).
- `AGENTS.md`/`review.md` — move ledger/history to CHANGELOG or docs/audits; keep the current contract.
- `CONTRIBUTING.md` — one line: new scripts are ESM `.mjs`; `prompts/` is historical data, not product code.
- `docs/ENVIRONMENT_VARIABLES.md` — note that `version.json` is generated at build and untracked once fixed.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which catalog copy is canonical for the storefront? | blocks the dedup fix | product/content-owner decision |
| Is the prompt corpus intended to stay in-repo long-term? | HYG-P2-001 closure | owner decision (AGENTS.md flags it) |
| Are the one-off catalog scripts still needed for a future content pass? | archive vs delete | content-owner confirmation |
| Should `prompts/` continue to pin binary artifacts (`.pyc`, `.xlsx`)? | pin semantics | maintainer decision |
| Is `version.json` intentionally committed for Vercel previews? | untrack vs keep | deployment owner (AGENTS.md:688 notes Vercel previews) |

## Appendix

- Reproduce the manifest check without node:
  `python3 - <<'EOF'` … read `prompts/manifest.json`, hash `prompts/<path>` as `sha256(raw.decode('utf-8','replace').replace('\r\n','\n'))`, compare — 0 mismatches.
- Import-graph scan: DFS over resolved relative + `@/` + `@mct/*` imports of `.ts/.tsx` (excluding `node_modules`, `dist`, `.next`, `__tests__`); cycle list: `apps/worker/src/metrics.ts ↔ apps/worker/src/task-registry.ts`.
- Catalog diff: `python3` keyed by SKU; 245/245 differ in `marketingCopy`, `customerOutcomes`, `whatIsIncluded`, `bestFor`, `internalProcedure`, `fulfillmentWorkflow`.
- Machine-path residual lines: `docs/GAP_ANALYSIS.md:149`, `docs/MT-P0-001-RLS-remediation-design.md:5`, `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md:9-10,20-26,208`.
- Cross-domain note (not duplicated): dead-RLS-key scan found the live schema free of catalog-absent permission pairs except policies on tables dropped by `supabase/migrations/5302055_cleanup_dead_tables.sql`; `documents/tickets/projects:manage` were replaced by `5302129`. The ACM/RLS domains already own that row.

## Findings

| ID | Severity | Title |
|---|---|---|
| HYGIENE-P2-001 | P2 | Committed prompt/audit corpus bloats the repo and review surface |
| HYGIENE-P2-002 | P2 | Duplicate product catalogs have diverged |
| HYGIENE-P3-001 | P3 | Stale and machine-specific generated documentation |
| HYGIENE-P3-002 | P3 | Generated artifacts are inconsistently tracked |
| HYGIENE-P2-003 | P2 | 17 tracked shell scripts lack the exec bit; documented ./scripts/... commands fail |
| HYGIENE-P2-004 | P2 | AdminDocumentsCenterClient.tsx is a 2,322-line single component |
| HYGIENE-P3-003 | P3 | Dead modules and a dead component with zero references |
| HYGIENE-P3-004 | P3 | Orphaned one-off catalog scripts and their 1.2 MB content-map pipeline |
| HYGIENE-P3-005 | P3 | Committed Python bytecode and a stale build artifact are tracked |
| HYGIENE-P3-006 | P3 | Stray duplicate snippet file with local dev auth seed data |
| HYGIENE-P3-007 | P3 | Root package script `sbom:licenses` is known-broken on the pinned pnpm |
| HYGIENE-P3-008 | P3 | scripts/README.md index is stale: 14 scripts (10 active CI guards) are undocumented |
| HYGIENE-P3-009 | P3 | No circular-dependency guard; one live import cycle in the worker |
| HYGIENE-P3-010 | P3 | Explicit `any` is lint-disabled and 63 `supabase as any` casts sit at the typed-client boundary |
| HYGIENE-P3-011 | P3 | AGENTS.md (120 KB) doubles as a historical changelog and is mirrored into review.md |
| HYGIENE-P3-012 | P3 | Audit run layout contract is not met by the committed repo-deep-dive runs |
| HYGIENE-P3-013 | P3 | Two Redis client libraries coexist in apps/api |
