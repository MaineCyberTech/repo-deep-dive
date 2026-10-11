# 01_repository_inventory — Prompt 01 - Comprehensive Repository Inventory

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `01_repository_inventory.md` (area INV, prompt)

## Verification Performed

# Comprehensive Repository Inventory

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `https://github.com/MaineCyberTech/mainecybertech`
- Branch: `main` (worktree at `/tmp/opencode/mct-audit-target`, detached HEAD, clean)
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (`8d299b8d`)
- Generated at: 2026-10-11 (read-only pass)
- Auditor: domain subagent (area `INV`)
- Area code: INV
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/01_repository_inventory.md`
- Scope limitations: no `node`/`pnpm` runtime available on the audit host, so no generator or test suite could be executed; all verification is static (git, grep, file hashing, JSON parsing). No network/GitHub API access, so live branch-protection/environment state is not re-verified. The target worktree is read-only; nothing was modified.

## Scope

Reviewed at `8d299b8d` (repo state: `git status --porcelain` → 0 files, branch `main` via worktree of `/root/mainecybertech`): root configs; pnpm/turbo workspace files; the three applications (`apps/api`, `apps/web`, `apps/worker`); shared packages (`packages/config`, `packages/sdk`, `packages/ui`); database artifacts (`supabase/migrations`, `seeds`, `policies`, `functions`, `snippets`, `config.toml*`); GitHub metadata (`.github/workflows`, actions, CODEOWNERS, branch-protection JSON, dependabot, templates); tests (jest/playwright); docs (`docs/**`, `AGENTS.md`, `review.md`, `README*.md`, `CHANGELOG.md`); assets (`apps/web/public`); generated artifacts (committed and untracked); Docker/deploy/infra (`docker-compose.yml`, `infra/**`); environment examples. Not reviewed in depth: application business logic, RLS policy content, CI workflow internals, Terraform resource details — those belong to other domains; this report only inventories them.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `pnpm-lock.yaml` (493 KB) | root/workspace | Monorepo shape and task graph | 3 apps + 3 packages; `apps/*`, `packages/*` |
| `apps/api` (327 files), `apps/web` (1012), `apps/worker` (53) | applications | Runtime surface | Dockerfiles + `.env.example` per app |
| `packages/config` (5), `packages/sdk` (69), `packages/ui` (30) | shared packages | Reuse boundary | SDK holds generated `database.types.ts` |
| `supabase/migrations` (134 `.sql`), `supabase/seeds` (9), `config.toml` | database | Schema/seed chain | latest `5302436_restore_platform_admin_rls_gates.sql` |
| `.github/**` (34 files, 20 workflows) | GitHub metadata | CI/CD + governance | composite actions, branch-protection JSON, CODEOWNERS |
| `apps/web/e2e` (90 specs), jest configs, coverage thresholds | tests | Release confidence | counts guarded in docs |
| `docs/**` (364 files), `AGENTS.md` (1003 lines), `review.md` (generated mirror) | docs | Operator/agent readiness | docs counts + links guards |
| `apps/web/public` (6 files) | assets | PWA surface | `sw.js`, two manifests, `version.json` |
| `prompts/**` (632 files, 12 MB) + `prompts/manifest.json` | generated corpus | Supply-chain pinning | verified clean |
| `docs/audits/**` (75 files, 2.9 MB) | generated outputs | Audit ledger | previous run dir amended in place |
| `docker-compose.yml`, `infra/**` (25 files) | deploy/infra | Local + prod runtime | DO compose + Terraform + Caddy |
| `*.env.example` (4 files), `.gitleaks.toml`, `security/*.json` | env/security | Sensitive inventory | placeholders only |

## Verification Performed

Exact commands run (read-only) and observed results at `8d299b8d`:

| Command | Observed result |
|---|---|
| `git log --oneline -1`, `git status --porcelain` | `8d299b8d …`, 0 dirty files; worktree clean |
| `git ls-files \| wc -l` | 2823 tracked files; top dirs: apps 1392, prompts 632, docs 364, supabase 152 |
| `git ls-files -- licenses.json sbom.cdx.json sbom.spdx.json` | empty → untracked gate would pass |
| `git ls-files -ci --exclude-standard` | empty → no tracked-but-ignored files |
| `git ls-files -s \| awk '$1=="100644" && $4~/\.sh$/'` | empty → validate.yml exec-bit gate would pass |
| Python re-implementation of `verify-prompts.js` hashing (UTF-8 + CRLF→LF) over all 630 manifest entries | 0 missing, 0 added, 0 hash mismatches → `prompts/manifest.json` is current |
| `python3` compare of `AGENTS.md` vs `review.md` body (banner stripped) | byte-identical → mirror in sync |
| `diff "supabase/snippets/Untitled query 314.sql" supabase/seeds/00_local_auth_users.corrected.v2.sql` | no differences (byte-identical) |
| `git log --format=… -1 -- docs/openapi.yaml` and `-- apps/api/src/openapi/spec.ts` | both last changed in `1c1bd4ad` (2026-10-04) → aligned, but no CI sync gate exists |
| `git diff e4db0a0c 8d299b8d -- docs/audits/…/findings.json` | `generated` 2026-10-10→2026-10-11; DR-P2-001/INFRA-P2-006 `open`→`verified-fixed` |
| `python3` parse of the run's `audit_manifest.json` | still `scope.commit 9c0b88c`, `scaffolded_at 2026-10-05` |
| `grep -rn "serviceWorker\|sw\.js" apps/web` (excl. node_modules) | no registration found |
| `grep -rn "version.json" .github scripts` | no guard found |
| `python3` link check for `docs/INDEX.md` (164 links), `README.md` (12 links) | 0 missing targets (matches intent of `check-docs-links.mjs`) |
| Counts vs `AGENTS.md` rows (migrations 134, workflows 20, scripts 81, prompts 632, components 102, e2e specs 90, seeds 9, worker tasks 12, sdk modules 60) | all match → docs-counts guard would pass |
| `git merge-base --is-ancestor` for fix commits `3e7a39bb`, `0a2e5331`, `2d4e6788`, `fd27150f` | all ancestors of HEAD |
| `du -sh` per dir | apps 18M, prompts 12M, docs 8.1M, supabase 1.9M; 4 tracked files > 1 MB (2× products.json app copies, 2× prompts-pack copies) |

Not reproducible on this host (recorded as Unknown, not as pass): `pnpm test` / coverage totals (no node runtime); `generate-db-types.js --check`; `openapi-audit.js`; `check-docs-counts.mjs` / `check-docs-links.mjs` / `verify-rls.mjs` execution; `pnpm build`; anything requiring GitHub or the droplet.

## Executive Summary

The repository is a well-organized Turborepo monorepo (3 apps, 3 packages, 134 migrations, 632-file pinned prompt corpus, 20 workflows, 364 docs) with an unusually strong set of self-checking guards for a project of this size: prompt provenance pinning, docs count/link checks, DB-type freshness, RLS predicate linting, branch-protection parity, untracked-generated-artifact checks, and coverage thresholds. Repo state at audit time is clean (`main 8d299b8d`, no dirty files).

The previous INV findings all hold up: the bootstrap-SQL header, the prompt-corpus pinning, and the canonical repo slug are present and effective at this commit. However, the original "generated artifacts drift without a gate" finding is only partially closed — the gate covers `licenses.json`/`sbom*.json`, while `apps/web/public/version.json` is demonstrably stale and unguarded and `docs/openapi.yaml` has no regenerate-and-diff check. Two additional inventory-level issues surfaced this pass: the committed previous-run audit artifacts (`docs/audits/…/9c0b88c/`) are amended in place (statuses flipped, `generated` timestamp moved to 2026-10-11) while the run manifest still binds commit `9c0b88c`, and a handful of questionable committed artifacts remain (a Studio scratch snippet duplicating a dev seed, an unregistered service worker, vestigial Vercel configs).

Recommended next actions, in order: (1) extend the artifact-drift gate to `version.json` and `openapi.yaml`; (2) decide the audit-ledger policy (freeze runs vs. per-finding `verified_at_commit`); (3) delete or re-home the scratch snippet and the unregistered service worker. None of these are release-blocking.

## Inventory

### Inventory summary table

| Item | Path / symbol | Purpose | Current state | Risk | Notes / likely owner |
|---|---|---|---|---|---|
| Root manifest | `package.json` | Scripts, dev deps, pnpm overrides | Active; name `mct-portal`, `packageManager pnpm@10.34.3` | Low | platform |
| Workspace | `pnpm-workspace.yaml` | `apps/*`, `packages/*` | Active | Low | platform |
| Task graph | `turbo.json` | build/dev/lint/test/typecheck | Active | Low | platform |
| Lockfile | `pnpm-lock.yaml` (493 KB) | Dependency pinning | Committed | Low | platform |
| Vercel configs | `vercel.json`, `apps/web/vercel.json` | Vercel deploy config | Vestigial (last touched 2026-06-09) | Low | infra — see INV–P3-004 |
| Version identity | `VERSION` = `0.1.0`; 0 git tags | Release identity | No tags; REL-P1-001 open | Medium | release owner (other domain) |
| API app | `apps/api` (327 files) | Express API, 62 route files (75 incl. subdirs) | Active; OpenAPI spec + guards | Low | backend |
| Web app | `apps/web` (1012 files) | Next.js App Router, 319 pages, 102 components | Active | Low | frontend |
| Worker app | `apps/worker` (53 files) | Queue consumer, 12 task files / 28 handlers | Active | Low | backend |
| SDK | `packages/sdk` (69 files, 60 modules) | Typed client + generated DB types | Active; `--check` guard in CI | Low | backend |
| UI kit | `packages/ui` (30 files, 7 components + stories) | Shared components/tokens | Active; no unit tests | Low | frontend |
| Config package | `packages/config` | Shared ESLint/TS/date helpers | Active, minimal | Low | platform |
| Migrations | `supabase/migrations` (134 `.sql`) | Schema chain | Active; guarded | Low | backend/DB |
| Seeds | `supabase/seeds` (9 `.sql`) | Local/E2E data | Dev-only; `config.toml` lists 00–08 | Medium (test creds) | backend/DB |
| Snippet | `supabase/snippets/Untitled query 314.sql` | Studio scratch | Duplicate of seed 00 | Low | backend/DB — see INV–P3-006 |
| CI | `.github/workflows` (20) + 4 composite actions | Test/lint/typecheck/E2E/deploy/backup/SBOM | Active; PR + deploy gates | Low | CI owner |
| Governance | `CODEOWNERS`, `branch-protection/*.json`, `dependabot.yml` | Review + checks | Committed; parity guard | Low | repo admin (live apply pending) |
| Tests | 362 web + 134 api + 14 worker + 3 sdk files; 90 E2E specs | Quality gates | Active; coverage thresholds | Low | all teams |
| Docs | `docs/**` (364 files), `AGENTS.md`/`review.md` | Operator/dev/agent docs | Active; counts+links guards | Low | docs/leads |
| Prompt corpus | `prompts/**` (632 files, 12 MB) | Vendored prompt packs | Pinned; manifest verifies | Low | maintainer |
| Audit ledger | `docs/audits/**` (75 files, 2.9 MB) | Audit run outputs | Amended in place | Medium | audit tooling — see INV–P3-005 |
| Assets | `apps/web/public` (6 files) | favicon, manifests, `sw.js`, `version.json` | `sw.js` unregistered; `version.json` stale | Low | frontend — INV–P3-003/007 |
| Local stack | `docker-compose.yml` (api/web/worker/e2e) | Local dev | Active | Low | platform |
| Prod stack | `infra/digitalocean/docker-compose.yml` + Caddy + Prometheus/Alertmanager | Production runtime | Active | Low | infra |
| IaC | `infra/terraform/digitalocean` (15 files) | Droplet/DNS/firewall | Active; lockfile committed | Low | infra |

### Sensitive inventory table

| File / area | Sensitivity | Handling notes |
|---|---|---|
| `supabase/seeds/00,01,05,06,07*.sql` | Local test users with bcrypt password hashes; shared test password "1" | Header marks LOCAL / DEV ONLY; values not printed here |
| `supabase/snippets/Untitled query 314.sql` | Byte-identical copy of seed 00 (same hashes) | See INV–P3-006 |
| `.gitleaks.toml` | Allowlists (module id, manifest checksums, e2e throwaway JWT default) | Scoped per rule; negative fixture verifies it |
| `scripts/ci/fixtures/gitleaks-negative.env.fixture` | Deliberately fake key halves | Guard file, explicitly "DO NOT fix" |
| `apps/api/.env.example`, `apps/web/.env.example`, `apps/worker/.env.example`, `infra/digitalocean/.env.example` | Placeholders only | `<your-…>` / empty values |
| `.github/restore-test-baseline.env` | Restore-test thresholds (not secrets) | Definition of "verified backup" |
| `security/dependency-audit-policy.json`, `security/license-policy.json` | Policies, allowlists | No secret material |
| `.github/workflows/*.yml` | Secrets referenced by name only | No values committed |
| `docs/audits/**` | Findings that discuss security issues | No secrets printed; quote config paths only |

No live-looking credentials were found by targeted pattern grep (`AKIA…`, `sk_live_…`, `ghp_…`, JWT literal); the only hits were the scan pattern itself and a test string in `apps/api/src/__tests__/api-key-auth.test.ts:68`.

### Generated / stale artifact table

| Artifact | Generator | Regeneration command | Tracked | Guard | State at 8d299b8d |
|---|---|---|---|---|---|
| `licenses.json` | `scripts/collect-licenses.mjs` | CI job | No (ignored) | Untracked gate | OK |
| `sbom.cdx.json` / `sbom.spdx.json` | `scripts/generate-sbom.mjs` | CI job | No (ignored) | Untracked gate | OK |
| `prompts/manifest.json` | `scripts/verify-prompts.js generate` | same | Yes | `verify` in validate.yml | Current (0 mismatches) |
| `review.md` | `scripts/sync-review-md.mjs` | same | Yes | `--check` in CI | Current (body == AGENTS.md) |
| `packages/sdk/src/database.types.ts` | `scripts/generate-db-types.js` | same | Yes | `--check` in CI | Not re-run here (no node); last changed `e89f466c` |
| `docs/openapi.yaml` | `apps/api/src/openapi/generate.ts` | `pnpm --filter=api generate:openapi` | Yes | none (only route coverage/validation) | Aligned at `1c1bd4ad`; no drift gate |
| `apps/web/public/version.json` | `apps/web/scripts/generate-version.js` | `pnpm --filter=web generate:version` | Yes | none | STALE (`sha unknown`, 2026-08-05) |
| `docs/audits/**` | audit packs / aggregator | re-run or reconcile | Yes | none | Previous run amended 2026-10-11; binding mismatch |
| `repomix-*.xml`, `session-*.diff` | repomix configs | local runs | No (ignored) | — | OK |
| `docs/storybook-static` | `storybook build` | local | No (ignored) | — | OK |

### Unknowns table

| Unknown | Why it matters | Evidence needed |
|---|---|---|
| Actual current test totals / pass state | Docs claim "3,490 tests, all passing" (2026-09-27) | Run `pnpm test:coverage` in CI or locally with node |
| `generate-db-types.js --check` result at HEAD | Generated DB types could be stale | Run the check (CI-wired) |
| Whether `docs/openapi.yaml` byte-matches `buildSpec()` | YAML snapshot could drift silently | Run `generate:openapi` + `git diff --exit-code` |
| Live branch-protection/environment settings | Committed JSON is not proof of applied settings | GitHub admin/API read |
| Whether a Vercel project still auto-deploys | Vestigial configs could be live | Vercel dashboard |
| Whether the E2E suite is green on main | E2E is a prod-deploy gate | CI run history |
| Actual `pnpm-lock.yaml` consistency with `package.json` | Drift would break frozen installs | `pnpm install --frozen-lockfile` in CI |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Root configs | 4 | `package.json` pinned packageManager/engines; editorconfig/prettier; 20 workflows | Vestigial `vercel.json`; no tags (REL) | Remove/mark Vercel configs |
| Package/workspace files | 4 | `pnpm-workspace.yaml`, `turbo.json`, lockfile | packages lint via prettier only | Optional: shared lint for packages |
| Applications | 4 | 3 apps with Dockerfiles, tests, env examples | none material | — |
| API services | 4 | 62 route files, OpenAPI spec + coverage audit, service layer | openapi.yaml snapshot unguarded | Add regen+diff gate |
| Workers | 4 | 12 task files, 28 handlers, 104 tests | none material | — |
| Shared packages | 3 | SDK 60 modules + CI-checked generated types; UI 7 components + stories | `packages/ui` has no unit tests | Add component tests |
| Database/migrations | 4 | 134 migrations, naming guide, RLS guards, drift check | no down-migrations (documented) | Keep documented rollback path |
| GitHub metadata | 4 | CODEOWNERS, branch-protection JSON + parity guard, dependabot, templates | live application is manual | Apply protection JSON via admin |
| Tests | 4 | 362+134+14+3 unit files, 90 E2E specs, coverage thresholds | counts not machine-verified against runs | Publish test-count artifact in CI |
| Docs | 4 | 364 docs, INDEX, ADRs, runbooks, counts/links guards | dated audits mixed with runbooks (DOC-P3-001) | Archive/staleness markers |
| Assets/public files | 3 | favicon + manifests + sw.js + version.json | unregistered SW; stale version.json; duplicate manifests (MOB-P3-001) | See INV–P3-003/007 |
| Generated artifacts | 3 | license/SBOM untracked+gated; manifest/review/types gated | version.json, openapi.yaml, audit ledger | Extend drift gate; fix ledger binding |

## Detailed Review

### Item: Root configs and workspace

- Evidence: `package.json:5-7` (pnpm 10.34.3, node >=20), `:55-95` (overrides, packageExtensions), `pnpm-workspace.yaml`, `turbo.json`, `.editorconfig`, `.prettierrc.json`, `.husky/pre-commit` (secret scan + lint-staged), `.npmrc`.
- What it does: defines the monorepo, task graph, formatting/lint entry points and pre-commit hooks.
- How it appears to work: `turbo run` drives per-app tasks; lint-staged runs per-app ESLint configs with `--max-warnings=0`.
- Dependencies: all apps/packages; husky requires local install.
- Current controls: pinned package manager, engines, frozen-lockfile CI, secret scan pre-commit.
- Missing controls: no CI check that `pnpm-lock.yaml` matches manifests beyond install; `vercel.json` vestigial.
- Risks: low; see INV–P3-004.
- Recommended improvement: delete/mark the Vercel configs; consider a lockfile-drift check.
- Suggested tests: CI `pnpm install --frozen-lockfile` is already the check.
- Suggested docs: note the removal in `docs/INDEX.md` if files are deleted.

### Item: Applications (api/web/worker)

- Evidence: `apps/api/src/{app.ts,main.ts,routes,services,middleware}`, `apps/web/app/**` (319 pages), `apps/web/e2e` (90 specs), `apps/worker/src/{tasks,services,lib}`; Dockerfiles with digest-pinned node:20-alpine; per-app `.env.example`.
- What it does: Express API (port 4000), Next.js web (3000), worker consumer (3001).
- How it appears to work: API mounts 62 route files (+ `routes/final`, `routes/store`); web uses App Router with server components/actions; worker registers 28 handlers.
- Dependencies: `@mct/sdk`, `@mct/ui`, `@mct/config`, Supabase, Redis/SQS.
- Current controls: Dockerfiles drop npm/corepack and run non-root; healthchecks; tests + coverage thresholds.
- Missing controls: none material for inventory purposes.
- Risks: low.
- Recommended improvement: none required by this domain.
- Suggested tests: existing suites.
- Suggested docs: existing app docs are indexed.

### Item: Shared packages

- Evidence: `packages/sdk/src/*.ts` (60 modules, `database.types.ts` generated), `packages/ui/src` (7 components + stories + tokens), `packages/config/src/date.ts`.
- What it does: typed API client, shared UI kit, shared configs.
- Current controls: `generate-db-types.js --check` in CI; Storybook stories for UI.
- Missing controls: no unit tests in `packages/ui`; SDK has 3 test files.
- Risks: low-medium (UI regressions caught only by web tests/E2E).
- Recommended improvement: add focused component tests or axe assertions for the UI kit.
- Suggested tests: render tests for Button/Input/Dialog/SidebarGroup.
- Suggested docs: `docs/ui-kit.md` already covers usage.

### Item: Database/migrations/seeds

- Evidence: `supabase/migrations` (134 files; latest `5302436_restore_platform_admin_rls_gates.sql`), `supabase/seeds/00-08`, `supabase/config.toml:3-15`, `supabase/config.toml.production.example`, `supabase/policies/.gitkeep`, `supabase/functions/.gitkeep`, `scripts/verify-rls.mjs`, `scripts/check-rls-predicate.mjs`, `tools/migration_chain_check.sh`.
- What it does: schema evolution + local/E2E data; demo data is opt-in via `app.seed_demo` (e.g. `5302123_demo_expanded_test_data.sql:28`).
- Current controls: RLS/migration hygiene guards in CI; drift check in `supabase-migrations.yml`; seeds only run locally.
- Missing controls: none inventory-level.
- Risks: dev credentials in seeds (expected, labeled); duplicate snippet (INV–P3-006).
- Recommended improvement: delete the duplicate snippet; keep seeds as the only copy.
- Suggested tests: existing RLS/migration guards.
- Suggested docs: `docs/SUPABASE_MIGRATION_WORKFLOW.md` exists.

### Item: GitHub metadata

- Evidence: `.github/workflows` (20), `.github/actions/{setup-pnpm,unit-tests,dependency-audit,secret-scan}`, `CODEOWNERS`, `branch-protection/{main,develop}.json`, `dependabot.yml`, PR/issue templates, `actionlint.yaml`.
- What it does: PR gates (test/lint/typecheck/E2E/dependency review), deploy pipeline, backups, SBOM, secret scans, Terraform.
- Current controls: branch-protection parity script; composite actions shared between PR and deploy gates; `enforce_admins: true` in committed JSON.
- Missing controls: live application is a repo-admin action (tracked by CI-P1-001/003, other domain).
- Risks: low within this domain.
- Recommended improvement: keep parity guard; apply JSON via admin.
- Suggested tests: `scripts/check-required-checks.mjs` (CI-wired).
- Suggested docs: `.github/branch-protection/README.md`.

### Item: Tests

- Evidence: 362 web test files, 134 api, 14 worker, 3 sdk; 90 Playwright specs (`apps/web/e2e/**`); jest configs with ratcheted thresholds (`apps/web/jest.config.mjs`, `apps/api/jest.config.mjs`); `docs/testing.md`.
- Current controls: coverage thresholds, E2E gate, a11y gate (25 routes default / 68 with `A11Y_FULL`).
- Missing controls: docs test-count claim is not machine-verified against a test run.
- Risks: low.
- Recommended improvement: emit a test-count artifact in CI and check the docs against it.
- Suggested tests: existing.
- Suggested docs: `docs/testing.md`.

### Item: Docs and agent references

- Evidence: `docs/**` (364 files), `docs/INDEX.md` (164 links, 0 missing), `AGENTS.md` (1003 lines) + `review.md` mirror, `CHANGELOG.md` (recently updated), `docs/audits/README.md`.
- Current controls: `check-docs-counts.mjs`, `check-docs-links.mjs`, `sync-review-md.mjs --check` in CI.
- Missing controls: dated audit reports mixed with current runbooks (DOC-P3-001); `docs/audits/README.md` run table does not list repo-deep-dive runs.
- Risks: low-medium (doc drift).
- Recommended improvement: staleness/archive markers; list all runs.
- Suggested tests: existing guards + a freshness check for audit dirs.
- Suggested docs: update `docs/audits/README.md`.

### Item: Assets and generated artifacts

- Evidence: `apps/web/public/{favicon.ico,favicon.svg,manifest.json,manifest.webmanifest,sw.js,version.json}`; `apps/web/app/layout.tsx:26` (references `/manifest.webmanifest`); `apps/web/public/sw.js` (no registration); `apps/web/public/version.json` (stale); `docs/openapi.yaml`; `prompts/manifest.json`; `packages/sdk/src/database.types.ts`.
- Current controls: untracked gate for licenses/SBOM; provenance/type/mirror checks.
- Missing controls: version.json and openapi.yaml are unguarded; audit ledger binding.
- Risks: see INV–P2-001/INV–P3-003/INV–P3-005.
- Recommended improvement: extend drift gate; freeze or rebind audit outputs.
- Suggested tests: `generate:openapi && git diff --exit-code`; version.json check; audit-manifest binding check.
- Suggested docs: `docs/SBOM_PROCESS.md` pattern can be reused.

### Item: Docker/deploy/infra and env examples

- Evidence: root `docker-compose.yml` (api/web/worker/e2e), `infra/digitalocean/docker-compose.yml` (redis/api/worker/web/prometheus/alertmanager/caddy), `infra/digitalocean/Caddyfile*`, `infra/terraform/digitalocean/*.tf` + committed `.terraform.lock.hcl`, `.env.example` files.
- Current controls: digest-pinned base images (Dockerfiles), trivy scans, terraform CI, env examples with placeholders.
- Missing controls: none inventory-level.
- Risks: low.
- Recommended improvement: none required by this domain.
- Suggested tests: existing infra CI.
- Suggested docs: `infra/digitalocean/README.md`, `infra/terraform/README.md`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INV-001 | Root configs | `package.json`, `turbo.json` | pinned pnpm/engines, overrides | Vercel configs vestigial | P3 | Remove/mark `vercel.json` files |
| INV-002 | Package/workspace files | `pnpm-workspace.yaml`, lockfile | frozen-lockfile CI | none material | — | — |
| INV-003 | Applications | 3 apps, Dockerfiles, tests | per-app gates | none material | — | — |
| INV-004 | API services | `apps/api/src/openapi/*`, `scripts/openapi-audit.js` | spec validation + route coverage | committed YAML has no sync gate | P3 | Add regen+diff CI step |
| INV-005 | Workers | `apps/worker/src/tasks` (28 handlers) | tests + env schema | none material | — | — |
| INV-006 | Shared packages | `packages/sdk`, `packages/ui` | DB-type check; stories | no UI unit tests | P3 | Add UI component tests |
| INV-007 | Database/migrations | 134 migrations, RLS guards | CI hygiene checks | none material | — | — |
| INV-008 | GitHub metadata | branch-protection JSON + parity script | committed checks resolve | live apply manual | P2 (other domain) | Apply via admin |
| INV-009 | Tests | jest/playwright suites | coverage thresholds, E2E gate | test-count claims unverified | P3 | CI test-count artifact |
| INV-010 | Docs | `docs/**`, guards | counts/links/mirror checks | audit docs staleness | P3 (DOC) | Archive markers |
| INV-011 | Assets/public files | `apps/web/public/*` | metadata references manifest | unregistered `sw.js`; stale `version.json` | P3 | INV–P3-003/007 |
| INV-012 | Generated artifacts | gitignore + CI gates | license/SBOM untracked gate | version.json/openapi/audit ledger | P2 | INV–P2-001/INV–P3-005 |

## Findings

### Finding ID: INV–P2-001 - Committed generated artifacts drift without a gate

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `.gitignore:59-63` — `licenses.json`, `sbom.cdx.json`, `sbom.spdx.json` untracked
  - `.github/actions/dependency-audit/action.yml:30-41` — untracked gate (fix `3e7a39bb`)
  - `apps/web/public/version.json:1-6` — stale committed build artifact
  - `docs/openapi.yaml:1-4` + `.github/actions/unit-tests/action.yml:27,33` — no sync gate
  - `docs/audits/…/9c0b88c/findings.json` — regenerated 2026-10-11 while manifest binds `9c0b88c`
- What is happening: The original fix untracked and gated the license/SBOM aggregates, but other committed generated artifacts remain ungated and one is demonstrably stale.
- Why it matters: Generated files can silently diverge from their sources; consumers then trust stale output.
- User / business impact: Low direct; medium for tooling/consumers of the OpenAPI snapshot and build badge.
- Security / privacy / reliability impact: Low; mostly provenance.
- Recommended fix: Add `generate:openapi` + `git diff --exit-code` and a version.json check to CI; keep the untracked gate.
- Suggested validation: Introduce a deliberate drift and confirm CI fails; revert.
- Owner suggestion: repo maintainer / platform CI owner
- Effort estimate: S
- Dependencies: none
- Status: partially-fixed
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P2-002 - Duplicate schema bootstrap SQL can be mistaken for the source of truth

- Severity: P2
- Confidence: High
- Area: INV
- Evidence: `docs/portal_platform_formal_handoff_bundle/supabase_consolidated_fresh_bootstrap_20260529.sql:16-21`; migration `5302026_…corrected.v3.sql`; fix `0a2e5331`
- What is happening: The historical bootstrap copy is clearly marked do-not-edit and points at the migration chain.
- Why it matters: Prevents schema edits landing in a dead file.
- User / business impact: None; guardrail retained.
- Security / privacy / reliability impact: Positive.
- Recommended fix: none.
- Suggested validation: keep header; re-check on docs restructure.
- Owner suggestion: backend/DB lead
- Effort estimate: —
- Dependencies: —
- Status: verified-fixed
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-001 - Large committed prompt/audit corpus inflates the application repository

- Severity: P3
- Confidence: High
- Area: INV
- Evidence: fix `fd27150f` (787→630, 157 files removed); manifest verifies (Python replication: 0 mismatches); `validate.yml:94-107` gate; `prompts/PROVENANCE.md`
- What is happening: The corpus is now pinned, documented and gated; it still occupies ~12 MB.
- Why it matters: Tampering is blocked; repo weight remains.
- User / business impact: Low.
- Security / privacy / reliability impact: Positive (supply-chain pinning).
- Recommended fix: optional size budget + fix stale "787 files" comment.
- Suggested validation: `verify-prompts.js verify` in CI (already).
- Owner suggestion: repo maintainer (audit tooling)
- Effort estimate: S
- Dependencies: none
- Status: verified-fixed
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-002 - Stale, machine-specific repo path in the agent reference

- Severity: P3
- Confidence: High
- Area: INV
- Evidence: `AGENTS.md:3`; fix `2d4e6788`; `review.md` in sync; CI `--check`
- What is happening: Canonical slug is present and mirrored.
- Why it matters: Agents resolve the correct repository.
- User / business impact: Low.
- Security / privacy / reliability impact: Low.
- Recommended fix: none.
- Suggested validation: `sync-review-md.mjs --check`.
- Owner suggestion: repo maintainer (AI readiness)
- Effort estimate: —
- Dependencies: —
- Status: verified-fixed
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-003 - Committed build artifact apps/web/public/version.json is stale and unguarded

- Severity: P3
- Confidence: High
- Area: INV
- Evidence: `apps/web/public/version.json:1-6`; `apps/web/scripts/generate-version.js:9-23`; `apps/web/package.json:8`; `apps/web/lib/version.ts:4,10`; no CI guard
- What is happening: A build-time file is committed with placeholder values and never checked.
- Why it matters: Dev/UI build badge shows "unknown"; policy inconsistency.
- User / business impact: Cosmetic.
- Security / privacy / reliability impact: Low.
- Recommended fix: untrack + generate in predev/prebuild, or add a drift check.
- Suggested validation: build without env vars and confirm the badge is generated fresh.
- Owner suggestion: @web
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-004 - Vestigial Vercel deploy configs remain after the DigitalOcean migration

- Severity: P3
- Confidence: Medium
- Area: INV
- Evidence: `vercel.json`, `apps/web/vercel.json` (last touched `2b3f02de`, 2026-06-09); `README.md:73,110-121,293`; no code/CI references
- What is happening: Deploy configs for an unused platform remain.
- Why it matters: Deploy-path ambiguity; possible unintended auto-deploy.
- User / business impact: Low.
- Security / privacy / reliability impact: Low.
- Recommended fix: delete or annotate; confirm no Vercel project link.
- Suggested validation: Vercel dashboard check (not available to this audit).
- Owner suggestion: platform/infrastructure
- Effort estimate: S
- Dependencies: owner confirmation
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-005 - Previous-run audit artifacts are amended in place without rebinding to the commit they now reflect

- Severity: P3
- Confidence: High
- Area: INV
- Evidence: `git diff e4db0a0c 8d299b8d -- …/findings.json`; `audit_manifest.json` still binds `9c0b88c`; `findings.json` notes empty; `docs/audits/README.md` "Never overwrite a previous run"
- What is happening: The committed ledger for the 9c0b88c run is a living document; the manifest no longer describes its content.
- Why it matters: Machine consumers can read statuses without provenance; audit record is not reproducible.
- User / business impact: Low-medium (audit governance).
- Security / privacy / reliability impact: Low.
- Recommended fix: freeze + new run dir, or add per-finding `verified_at_commit`/`reconciled_at` and update the manifest; carry notes into findings.json.
- Suggested validation: `tools/check_run.sh`-style check that manifest commit == findings binding.
- Owner suggestion: repo maintainer (audit tooling)
- Effort estimate: M
- Dependencies: audit tooling decision
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-006 - Committed Supabase Studio scratch snippet duplicates a dev seed

- Severity: P3
- Confidence: High
- Area: INV
- Evidence: `supabase/snippets/Untitled query 314.sql` (byte-identical to `supabase/seeds/00_local_auth_users.corrected.v2.sql`); initial commit `4a87279f`; `supabase/config.toml:5-15` seed list
- What is happening: A Studio scratch file was committed and duplicates a seed that is actually used.
- Why it matters: Two copies can drift; scratch filename invites edits.
- User / business impact: Low.
- Security / privacy / reliability impact: Low (dev-only credentials duplicated).
- Recommended fix: delete the snippet (or re-home it under seeds with a real name).
- Suggested validation: `diff` against the seed returns no output; seed reset flow unaffected.
- Owner suggestion: backend/DB lead
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

### Finding ID: INV–P3-007 - Service worker asset apps/web/public/sw.js is not registered anywhere

- Severity: P3
- Confidence: High
- Area: INV
- Evidence: `apps/web/public/sw.js:1-12`; no registration found by grep; `apps/web/app/layout.tsx:26` references only the manifest
- What is happening: A committed service worker is dead code.
- Why it matters: If later registered, its hardcoded cache list/version will serve stale pages; PWA coverage looks better than it is.
- User / business impact: None today.
- Security / privacy / reliability impact: Low.
- Recommended fix: register deliberately with a versioned cache, or delete.
- Suggested validation: grep for registration; Lighthouse/PWA check.
- Owner suggestion: @web
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: n/a
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale generated artifacts consumed as current (openapi.yaml, version.json) | P2 | Medium | Medium | INV–P2-001/INV–P3-003 | Regenerate + diff gate |
| Audit ledger statuses not bound to a commit | P3 | Medium | Medium | INV–P3-005 | Freeze runs or per-finding binding |
| Two dev-seed copies drift / scratch file edited | P3 | Medium | Low | INV–P3-006 | Delete duplicate |
| Unregistered SW registered later with stale cache | P3 | Low | Medium | INV–P3-007 | Register properly or delete |
| Vestigial Vercel config triggers unintended deploy | P3 | Low | Medium | INV–P3-004 | Delete/confirm |

## Recommendations

### Immediate / Release Blocking

- None identified by this domain. (No P0/P1 inventory findings.)

### This Week

- Add the `generate:openapi` + `git diff --exit-code docs/openapi.yaml` CI step and a `version.json` drift check (INV–P2-001, INV–P3-003).
- Decide the audit-ledger policy and record it in `docs/audits/README.md` (INV–P3-005).

### This Month

- Delete `supabase/snippets/Untitled query 314.sql` (INV–P3-006).
- Register or delete `apps/web/public/sw.js` (INV–P3-007).
- Remove or annotate the Vercel configs after confirming project state (INV–P3-004).

### Later / Platform Evolution

- Add a `prompts/` size/file-count budget and refresh the stale workflow comment (INV–P3-001 residual).
- Add UI-kit unit tests and a machine-checked test-count artifact (scorecard gaps).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Delete the scratch snippet | Removes a duplicate seed copy | `supabase/snippets/Untitled query 314.sql` | `diff` against seed 00 is empty; reset still works |
| Untrack `version.json` and generate in predev/prebuild | Removes a stale committed artifact | `apps/web/public/version.json`, `apps/web/package.json` | badge shows fresh sha in dev |
| Delete/mark Vercel configs | Removes deploy ambiguity | `vercel.json`, `apps/web/vercel.json` | grep shows no Vercel references |
| Delete or register `sw.js` | Removes dead asset | `apps/web/public/sw.js`, layout/registration | grep + Lighthouse |
| Fix "787 files" comment in validate.yml | Keeps the guard comment truthful | `.github/workflows/validate.yml:105` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| OpenAPI snapshot drift gate | P2 | CI owner | S | none |
| version.json generation/guard | P3 | @web | S | none |
| Audit-ledger binding (`verified_at_commit`) | P3 | audit tooling | M | policy decision |
| UI-kit component tests | P3 | frontend | M | none |
| Test-count artifact checked against docs | P3 | CI owner | M | CI test job |
| Prompt corpus size budget | P3 | maintainer | S | none |

## Suggested Tests

- CI: `pnpm --filter=api generate:openapi && git diff --exit-code docs/openapi.yaml`.
- CI: regenerate `version.json` with fixed env values and fail on drift (or assert untracked).
- CI: assert `prompts/manifest.json` fileCount equals tracked prompts minus manifest/PROVENANCE (already implied by verify).
- CI: audit-manifest binding check — `audit_manifest.json.scope.commit` must match the commit recorded in `findings.json` metadata.
- Unit: `packages/ui` render tests for Button/Input/Dialog/SidebarGroup.
- Manual: Lighthouse PWA audit if the service worker is registered.
- Manual: confirm `docs/audits/README.md` run table lists every committed run.

## Suggested Documentation Updates

- `docs/audits/README.md`: add repo-deep-dive runs to the Runs table; state the reconcile-vs-freeze policy for run dirs.
- `apps/web/README` or `README.dev.md`: document where `version.json` comes from.
- `infra/digitalocean/README.md` or `README.md`: note that Vercel configs are removed (if removed).
- `.github/workflows/validate.yml:105`: update the "787 files" comment to 632.
- `scripts/README.md`: already documents one-off scripts; no change needed.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is a Vercel project still linked to this repo? | Determines whether INV–P3-004 is cosmetic or live | Vercel dashboard / owner statement |
| Should audit run dirs be frozen or living? | Drives INV–P3-005 remediation shape | Owner/process decision |
| Are the 3,490-test / 397-suite docs claims still accurate? | Docs accuracy | CI test run at HEAD |
| Is `database.types.ts` current at HEAD? | SDK correctness | `generate-db-types.js --check` |
| Is the E2E gate green on main? | Prod deploy readiness | CI run history |

## Appendix

### Repository state for the run manifest

- Worktree: `/tmp/opencode/mct-audit-target` (gitdir pointer to `/root/mainecybertech/.git/worktrees/mct-audit-target`)
- Branch: `main` (detached HEAD), HEAD `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`, date 2026-10-11 00:13:46 -0400
- Dirty state: `git status --porcelain` → 0 lines
- Parallel activity: none observed during this pass (read-only)

### File-count inventory (tracked, `git ls-files`)

| Area | Count |
|---|---:|
| apps/api | 327 |
| apps/web | 1012 |
| apps/worker | 53 |
| packages (sdk 69, ui 30, config 5) | 104 |
| supabase | 152 (134 migrations) |
| docs | 364 |
| prompts | 632 |
| scripts | 81 |
| .github | 34 (20 workflows) |
| infra | 25 |
| total | 2823 |

### Size profile

`apps` 18M · `prompts` 12M · `docs` 8.1M (audits 2.9M) · `supabase` 1.9M · `scripts` 1.8M · `packages` 924K. Largest tracked files: `apps/api/src/data/products.json` (3.5 MB), `apps/web/lib/catalog/data/products.json` (2.5 MB), two 2 MB copies of the same catalog inside `prompts/mct-full-webstore-product-catalog-pack/`. The app-copy divergence is tracked by HYG-P2-002 (other domain); the prompts copies are byte-identical to each other.

### Cross-domain references (not duplicated here)

- HYG-P2-002 — duplicate product catalogs have diverged (HYGIENE domain).
- MOB-P3-001 — PWA manifest duplicated across three sources (MOBILE domain).
- DOC-P3-001 — dated audit reports mixed with current runbooks (DOCS domain).
- REL-P1-001 — no version identity / tags (RELEASE domain).
- CI-P1-001/CI-P1-003 — prod environment/approval provisioning (CI domain).
- DET-P3-001/002 — deterministic lens (gitleaks install, image digest pins).

## Findings

| ID | Severity | Title |
|---|---|---|
| INV-P2-001 | P2 | Committed generated artifacts drift without a gate |
| INV-P2-002 | P2 | Duplicate schema bootstrap SQL can be mistaken for the source of truth |
| INV-P3-001 | P3 | Large committed prompt/audit corpus inflates the application repository |
| INV-P3-002 | P3 | Stale, machine-specific repo path in the agent reference |
| INV-P3-003 | P3 | Committed build artifact apps/web/public/version.json is stale and unguarded |
| INV-P3-004 | P3 | Vestigial Vercel deploy configs remain after the DigitalOcean migration |
| INV-P3-005 | P3 | Previous-run audit artifacts are amended in place without rebinding to the commit they now reflect |
| INV-P3-006 | P3 | Committed Supabase Studio scratch snippet duplicates a dev seed |
| INV-P3-007 | P3 | Service worker asset apps/web/public/sw.js is not registered anywhere |
