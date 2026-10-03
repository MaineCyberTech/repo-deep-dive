# 01 Repository Inventory

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride
- Branch/commit: main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent (Full Hardening, profile=base)
- Input: `inventory.json` (generated 2026-10-03T04:18:39Z)

## Scope

Inventory of what exists in the repository at commit 59e12b9: languages, workspaces, entry points, migrations, workflows, containers, tests, and large artifacts. Read-only; no repo modification.

## Evidence Reviewed

- `inventory.json` — totals (1496 files / 496,436 lines), extensions, stacks, migrations, entry points.
- `package.json` — npm workspaces (`apps/*`, `packages/*`), scripts.
- `git ls-files` (1500 tracked files), `.gitignore`, `Get-ChildItem` sizes.
- Directory listing of `apps`, `packages`, `supabase`, `scripts`, `docs`, `evidence`, `infra`, `.github`.

## Verification Performed

- `git log -1 --format=%H %s` → `59e12b9b... chore(evidence): round-6 biome decor entry + live captures`; branch `main`; clean tree.
- `git ls-files | Measure-Object` → 1500 tracked files.
- Largest-file scan over tracked worktree (~94.6 MB total, `.git` excluded).
- Confirmed no `middleware.*` under `apps/web`; only one workflow (`.github/workflows/ci-foundation.yml`).

## Executive Summary

The repository is a mature TypeScript monorepo (npm workspaces) for a server-authoritative browser snowboarding game: Next.js 15 web client, a Node/Socket.IO realtime service, shared contracts/game-core packages, and a Supabase (Postgres) data plane with 56 ordered migrations and 16 manual SQL negative suites. Documentation, runbooks and an extensive append-only `evidence/` tree (849 of 1496 files) dominate the tree by count. The main inventory risk is not missing code but weight and duplication: three full-source `repomix` exports and a 6.9 MB PDF are tracked, and 94 generated `.log` files are committed in conflict with the `*.log` `.gitignore` rule. These are maintainability/secret-hygiene concerns rather than functional defects.

## Inventory

| Area | Count / detail |
|---|---|
| Files / lines | 1496 / 496,436 (tracked 1500) |
| Workspaces | `apps/web`, `apps/realtime`, `packages/contracts`, `packages/game-core`, `packages/config` |
| Entry points | `apps/realtime/src/index.ts`, `server.ts`, `packages/contracts/src/index.ts`, `packages/game-core/src/index.ts` |
| Migrations | `supabase/migrations/0001`–`0056` (0032 intentionally absent) |
| SQL negative suites | `supabase/tests/0001`–`0016` (16 files, manual) |
| TS/TSX source | 238 `.ts` + 51 `.tsx` |
| Workflows | 1 (`ci-foundation.yml`) |
| Containers | `apps/web/Dockerfile`, `apps/realtime/Dockerfile` |
| Test files | 138 |
| Evidence tree | 849 files |
| Largest artifacts | 6.88 MB PDF; `repomix-output.*.xml` (2.1–4.1 MB each, 3 copies) |

## Findings

### Finding ID: INV-P2-001 - Duplicate full-source repomix exports committed to the repository

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `evidence/production-acceptance/repomix-split/repomix-output.*.xml`
  - `evidence/production-acceptance/repomix-r71/repomix-output.*.xml`
  - `evidence/production-acceptance/repomix-r71-repair/repomix-output.*.xml`
  - Largest-file scan: 3 near-identical copies (`repomix-output.6.xml` = 4.07/4.07/4.06 MB)
- What is happening: Three full-repository source snapshots are checked in as split XML bundles.
- Why it matters: They duplicate source content, bloat clones, and can drift from HEAD while appearing authoritative.
- User / business impact: Slower CI checkout/clone and a misleading "current state" artifact.
- Security / privacy / reliability impact: Snapshots may retain old source/env-adjacent text indefinitely.
- Recommended fix: Remove duplicates from the working tree, keep at most one archive gated by a documented policy, and exclude via `.repomixignore`/`.gitignore`.
- Suggested validation: `git ls-files | grep repomix` returns ≤1 intended bundle; clone size drops.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: INV-P2-002 - Evidence tree dominates the repository by file count and size

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `inventory.json` — `largest_dirs`: evidence 849 files vs apps 270
  - Tracked worktree ≈ 94.6 MB
- What is happening: Over half of all files are append-only evidence artifacts.
- Why it matters: Discovery cost and clone/build friction rise with every review round; append-only doctrine discourages pruning.
- User / business impact: New contributors and agents struggle to find the current state.
- Security / privacy / reliability impact: Larger surface of historical logs to scan for accidental secrets.
- Recommended fix: Adopt an explicit archive policy (e.g. `docs/archive/`), a current-state index, and size budgets; never rewrite history.
- Suggested validation: Documented archive pointer exists; active tree bounded by budget.
- Owner suggestion: Repo maintainer
- Effort estimate: M
- Dependencies: INV-P2-001
- Status: open

### Finding ID: INV-P3-001 - Tracked `.log` files contradict the `*.log` gitignore rule

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `.gitignore` contains `*.log`
  - `git ls-files` returns 94 tracked `.log` files under `evidence/`
- What is happening: Generated logs were committed before/despite the ignore rule.
- Why it matters: Ignore rules no longer describe the tree; reviewers cannot trust `git status` clean-tree claims.
- User / business impact: Minor; mostly confusion and review noise.
- Security / privacy / reliability impact: Logs occasionally carry sensitive operational text.
- Recommended fix: Move needed transcripts to tracked `.txt` (the pattern already used after an earlier manifest fix) or exempt intentionally under `evidence/`.
- Suggested validation: `git ls-files '*.log'` count is zero or matches a documented allowlist.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: INV-P3-002 - One-off review artifacts at repository root

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - Root files: `ext_review.md`, `reviewer.md`, `agent_final_response.json`, `GATE_LEDGER.csv`, `REVIEW_PLAN_20260911.md`, `snowride_production_grade_major_phase_roadmap_*.pdf`
- What is happening: Historical review/roadmap artifacts live beside build config.
- Why it matters: The README calls `docs/product/*` the constitution, yet root files imply competing sources of truth.
- User / business impact: Onboarding ambiguity.
- Security / privacy / reliability impact: None identified.
- Recommended fix: Move historical review artifacts under `evidence/` or `docs/archive/` and leave a short pointer.
- Suggested validation: Root contains only build/config/docs entry files.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: INV-P2-002
- Status: open

## Risks

- R-INV-1: Duplicated snapshots could be mistaken for the canonical current state (P2).
- R-INV-2: Historical logs/snapshots are a persistent secret-leak scanning surface (P2).

## Recommendations

1. Define and enforce an evidence/archive size + duplication policy (INV-P2-001/002).
2. Reconcile `.gitignore` with tracked artifacts (INV-P3-001).
3. Establish a single current-state pointer (`docs/product/CURRENT_STATE_SCHEMA.md` exists — link it from root).

## Quick Wins

- Delete two of the three repomix copies (S).
- Re-home root review artifacts (S).

## Hardening Backlog

- Automated "tree budget" + duplicate-artifact check in CI.

## Suggested Tests

- CI check: fail if any tracked file >2 MB outside an allowlist; fail on duplicate large blobs.

## Suggested Documentation Updates

- `README.md`: add an evidence/archive policy section and current-state pointer.

## Open Questions

- Are the `repomix-*` bundles referenced by any published publication manifest? (`Unknown` — requires owner confirmation.)

## Appendix

- `inventory.json` totals and stack list (`github-actions`, `node`, `npm`, `supabase`).
