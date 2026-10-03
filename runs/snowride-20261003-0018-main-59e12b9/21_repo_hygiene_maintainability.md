# 21 Repository Hygiene & Maintainability

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Lint/format coverage, duplication and weight, versioning/release lineage, documentation accuracy, and general maintainability. Read-only.

## Evidence Reviewed

- `package.json` scripts; workspace `package.json` files
- `.gitignore`, `.prettierignore`, `.repomixignore`, `.dockerignore`
- Largest-file scan; `git ls-files`
- `docs/runbooks/BACKUP_RESTORE.md` vs `scripts/assurance/assurance.sh`
- `AGENTS.md`, `CONTRIBUTING.md`, `README.md`

## Verification Performed

- Confirmed root `lint` = `npm run lint --workspaces --if-present`; only `apps/web` defines a `lint` script (`packages/contracts`, `packages/game-core`, `packages/config` do not).
- Confirmed three package versions are `0.1.0` and root is `0.1.0`.
- Compared the backup-freshness claim in `BACKUP_RESTORE.md` with the current `assurance.sh` code (`*.dump`).
- Measured tracked worktree (~94.6 MB) and largest files.

## Executive Summary

The codebase is generally well-organized and documented, with clear ownership (`AGENTS.md`), consistent runbooks, and a strict doctrine. Maintainability weaknesses are concentrated in lint coverage (only the web app is linted), artifact weight/duplication, and a few stale documentation statements that contradict current code. Versioning is nominal (`0.1.0` everywhere) with no release/tag lineage in the repo, which weakens release traceability.

## Inventory

| Item | State |
|---|---|
| Lint | web only (eslint.config.mjs in apps/web) |
| Format | prettier, repo-wide, gated in CI |
| Duplicated artifacts | 3× repomix split exports |
| Large tracked file | 6.88 MB PDF |
| Versions | 0.1.0 (all) |
| `.gitattributes` | absent |
| Doc drift | `BACKUP_RESTORE.md` freshness note stale |

## Findings

### Finding ID: HYG-P2-001 - Only `apps/web` is linted; the other workspaces have no lint script

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `package.json` line 19 — `"lint": "npm run lint --workspaces --if-present"`
  - `apps/web/package.json` has `"lint": "eslint ."`; `packages/contracts`, `packages/game-core`, `packages/config`, and `apps/realtime` have no `lint` script
  - `AGENTS.md` line 41 — "lint (web only; realtime/game-core/contracts are unlinted)"
- What is happening: `npm run lint` silently skips the realtime server and both core packages.
- Why it matters: The most security- and correctness-sensitive code (realtime, game-core) is never linted.
- User / business impact: More bugs reach review/tests.
- Security / privacy / reliability impact: Missed correctness/security patterns.
- Recommended fix: Add an ESLint config per workspace (or a root flat config) and make `lint` cover all packages.
- Suggested validation: `npm run lint` visits >1 workspace.
- Owner suggestion: Repo maintainer
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: HYG-P2-002 - Duplicated generated artifacts and a large binary inflate the repository

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - 3× `evidence/production-acceptance/repomix-*/repomix-output.*.xml` (up to 4.07 MB each)
  - `snowride_production_grade_major_phase_roadmap_20260911_050010.pdf` (6.88 MB)
  - Total tracked worktree ≈ 94.6 MB
- What is happening: Generated snapshots and a report PDF are committed in multiple copies.
- Why it matters: Clone/checkout cost and review noise; snapshots age silently.
- User / business impact: Developer friction.
- Security / privacy / reliability impact: Larger historical secret-scan surface.
- Recommended fix: Keep one archived snapshot outside the main tree (or remove); store large reports as release artifacts.
- Suggested validation: Largest tracked file < a documented budget.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: INV-P2-001
- Status: open

### Finding ID: HYG-P2-003 - Backup runbook contradicts the (fixed) assurance freshness check

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - `docs/runbooks/BACKUP_RESTORE.md` lines 16–19 — "it currently globs `*.sql` … treat that check as known-broken until fixed"
  - `scripts/assurance/assurance.sh` line 123 — now globs `*.dump`
  - `evidence/audit-20260927/REMEDIATION.md` line 120–122 documents the fix
- What is happening: The runbook still describes a bug that was fixed.
- Why it matters: Operators cannot trust the runbook for the current release.
- User / business impact: Wasted investigation; mistrust of docs.
- Security / privacy / reliability impact: Recovery-confidence erosion.
- Recommended fix: Update `BACKUP_RESTORE.md` to the current `*.dump` behavior and link the remediation evidence.
- Suggested validation: Literal walk of the runbook matches the script.
- Owner suggestion: Operator
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: HYG-P3-001 - No release/version lineage in the repository

- Severity: P3
- Confidence: High
- Area: HYG
- Evidence:
  - All `package.json` versions are `0.1.0`
  - No `CHANGELOG.md`/release tag references in the tree (a `changelog_draft.md` is a run artifact, not the repo)
- What is happening: Releases are tracked externally (evidence/ledger) but not in version metadata.
- Why it matters: Mapping a deployed artifact to a semantic version is manual.
- User / business impact: Slower support/rollback.
- Security / privacy / reliability impact: Release traceability.
- Recommended fix: Adopt version bumps per release and a committed changelog (or generate from tags).
- Suggested validation: `package.json` version matches the release.
- Owner suggestion: Release engineer
- Effort estimate: S
- Dependencies: DATA-P1-001
- Status: open

### Finding ID: HYG-P3-002 - No `.gitattributes`; binary/large content handled plainly

- Severity: P3
- Confidence: High
- Area: HYG
- Evidence:
  - No `.gitattributes` found at root
  - Tracked binaries: `.png` (75), `.pdf`, `.zip`, `.ico`
- What is happening: No text/binary normalization or diff policy.
- Why it matters: Line-ending churn and binary diffs can obscure review.
- User / business impact: Minor.
- Security / privacy / reliability impact: None identified.
- Recommended fix: Add `.gitattributes` (`* text=auto`, binary globs, linguist-generated for evidence).
- Suggested validation: `git check-attr` marks binaries.
- Owner suggestion: Repo maintainer
- Effort estimate: S
- Dependencies: None
- Status: open

## Risks

- R-HYG-1: Unlinted core services (P2).
- R-HYG-2: Stale runbook (P2).
- R-HYG-3: Repo weight/duplication (P2).

## Recommendations

1. Lint all workspaces.
2. De-duplicate artifacts and set a size budget.
3. Correct stale docs and add `.gitattributes`/versioning.

## Quick Wins

- Fix the runbook note (S). Add `.gitattributes` (S).

## Hardening Backlog

- Doc-lint/consistency check for runbooks vs scripts.

## Suggested Tests

- CI: lint coverage assertion; tree-size budget.

## Suggested Documentation Updates

- `BACKUP_RESTORE.md`, `README.md` (archive policy).

## Open Questions

- Is the roadmap PDF still the active plan or historical? (`Unknown` — `ext_review.md` supersedes it.)

## Appendix

- `.prettierignore`, `.repomixignore`, `.dockerignore` present.
