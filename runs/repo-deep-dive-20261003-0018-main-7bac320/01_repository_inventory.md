# Comprehensive Repository Inventory

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: recorded 7bac320; **worktree HEAD = 6cada03** (2 commits ahead)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: INV
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/01_repository_inventory.md
- Scope limitations: read-only scan of the pack tree; `.git` excluded from counts; no live systems.

## Scope

Reviewed the whole pack: root configs, `prompts/` (49), `tools/` (13 Python + 5 shell), `templates/` (15), `lenses/` (6), `profiles/` (2), `examples/`, `schemas/`, `ci/`, `.github/workflows/`, `docs/`, `runbooks/`, `wiring/`, and `runs/` (2 archived runs). This is a documentation + stdlib-tooling repository, not a runtime service.

## Evidence Reviewed

- `inventory.json` (run input, generated from 7bac320)
- `README.md`, `CHANGELOG.md`, `VERSION`, `REFERENCE_CARD.md`, `CONTRIBUTING.md`, `opencode.json`
- `PACK_DIGEST.txt` (196 files), `git log 7bac320..6cada03`, `git ls-files`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse --short HEAD` | command | bind run to commit | returned `6cada03`, not `7bac320` |
| `git log --oneline 7bac320..6cada03` | command | show delta | 2 commits: `18e75cb`, `6cada03` |
| `git diff --stat 7bac320 6cada03` | command | file delta | adds `.github/workflows/deep-dive-deterministic.yml`, `tools/aggregate_findings.py`, `tools/deterministic_checks.py` |
| `git ls-tree` .py count | command | compare inventory | 9 at 7bac320, 11 at HEAD |
| `inventory.json` `workflows`/`ci` | artifact | cross-check | both empty; workflow exists at HEAD |

## Executive Summary

The pack is internally coherent at a high level but its run is mis-bound to the recorded commit, and its own machine inventory is stale. The worktree is 2 commits ahead of the run's recorded SHA and has gained a GitHub Actions workflow and two Python tools that the inventory does not see. Strengths: no committed secrets, no third-party Python deps, generated digest present. Main risks: binding/self-consistency drift (INV-P1-001), stale inventory CI picture (INV-P2-002), and an undocumented committed environment pin (INV-P3-003).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Prompts | `prompts/*.md` (49) | audit program | present | low | 42 base + 4 falcon + 2 runners + shared |
| Tools | `tools/*.py` (11 at HEAD) | machine chain | present | medium | inventory records 9 |
| Shell tools | `tools/*.sh` (5) | gates/digest/self-test | present | medium | bash-dependent |
| Actual CI | `.github/workflows/deep-dive-deterministic.yml` | org-wide deterministic scan | present | medium | not in inventory |
| CI example | `ci/audit.yml` | lint/validate/score/P0 example | present, **unwired** | medium | not under `.github/workflows` |
| Schema | `schemas/findings.schema.json` | findings.json contract | present | high | type drift (see DATA/API) |
| Archived runs | `runs/*/` (2) | evidence archives | present | low | includes `live_snapshot.txt` |
| Env pin | `opencode.json` | local model pin | tracked | low | excluded from digest |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Root configs | 3 | `VERSION`, `CHANGELOG.md`, `opencode.json` | no `.gitignore`/`.gitattributes`/`LICENSE` | add standards files |
| Package/workspace | 4 | stdlib-only Python | no lockfile (intentional) | document N/A |
| Applications | 1 | no runtime app | N/A | state N/A |
| API services | 1 | no HTTP API | N/A | state N/A |
| Workers | 2 | CI jobs | unwired example | wire CI |
| Shared packages | 3 | `tools/lib_findings.py` | no unit tests | add tests |
| Database/migrations | 1 | `schemas/` only | schema drift | align schema |
| GitHub metadata | 3 | one workflow | no CODEOWNERS/branch protection | add governance |
| Tests | 2 | `tools/self_test.sh` | not run in CI | wire + add unit tests |
| Docs | 4 | README/CONTRIBUTING/guides | stale tool list | refresh docs |
| Assets/public | 1 | none | N/A | state N/A |
| Generated artifacts | 3 | `PACK_DIGEST.txt` present | digest incomplete vs tracked tree | reconcile |

## Findings

### Finding ID: INV-P1-001 - Run is bound to 7bac320 but the worktree is at 6cada03

- Severity: P1
- Confidence: High
- Area: INV
- Evidence:
  - `inventory.json` — `git.sha = 7bac320`, `totals.files = 195`, `by_ext[".py"] = 9`
  - `git rev-parse --short HEAD` → `6cada03`; `git log --oneline 7bac320..6cada03` → `18e75cb`, `6cada03`
  - `git diff --stat 7bac320 6cada03` — adds `.github/workflows/deep-dive-deterministic.yml`, `tools/deterministic_checks.py`, `tools/aggregate_findings.py`
- What is happening: The run id, `INDEX.md`, and `inventory.json` all claim commit `7bac320`, but the repository being audited is at `6cada03`, two commits ahead.
- Why it matters: The shared rules require generated artifacts to record the commit they were generated from and to match the artifact set they ship with. Here the inventory and the run identity do not describe the code on disk.
- User / business impact: Findings and gate decisions may not correspond to the code a reader checks out; remediation can target the wrong revision.
- Security / privacy / reliability impact: Reduced audit integrity; stale inventory hides the new org-wide CI workflow.
- Recommended fix: Re-run `tools/repo_inventory.py` at the audited commit, write the actual SHA into `INDEX.md`/manifest, and either audit `6cada03` explicitly or check out `7bac320`.
- Suggested validation: `python3 tools/repo_inventory.py . -o inventory.json` then assert `inventory.json.git.sha == git rev-parse --short HEAD`.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: INV-P2-002 - inventory.json reports no CI/workflows while a workflow exists at HEAD

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `inventory.json` — `"workflows": []`, `"ci": []`, `"stacks": []`
  - `.github/workflows/deep-dive-deterministic.yml` — present at HEAD
- What is happening: The run's Wave 0 inventory says the repo has no CI workflows or CI system, because it was generated before the workflow was added.
- Why it matters: Wave 1 CI/supply-chain prompts are seeded from inventory; an empty CI section suppresses review of the one workflow that exists.
- User / business impact: Reviewers under-audit the CI surface.
- Security / privacy / reliability impact: The org-wide PAT workflow (SEC-P1-002) is easy to miss.
- Recommended fix: Regenerate the inventory at HEAD; add a staleness assertion comparing inventory SHA to HEAD.
- Suggested validation: `python3 tools/repo_inventory.py . -o /tmp/i.json && python3 -c "import json;d=json.load(open('/tmp/i.json'));assert d['workflows']"`
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: INV-P1-001
- Status: open

### Finding ID: INV-P3-003 - A tracked, environment-local pin is excluded from the integrity digest

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `opencode.json` — `{"model": "ollama/qwen3:8b"}`, tracked (`git ls-files`)
  - `tools/pack_digest.sh` — skip list includes `opencode.json`
  - `PACK_DIGEST.txt` — does not contain `opencode.json`
- What is happening: `opencode.json` is committed to the repo but deliberately omitted from the digest/lint, so the digest is not a complete manifest of the tracked tree.
- Why it matters: A committed file that the integrity check ignores can drift unobserved; it also pins a machine-specific model.
- User / business impact: Minor; digest consumers may assume completeness.
- Security / privacy / reliability impact: Low — config sprawl.
- Recommended fix: Either untrack `opencode.json`/add it to `.gitignore`, or include it in the digest and document why.
- Suggested validation: `git check-ignore opencode.json` or confirm it appears in `PACK_DIGEST.txt`.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Audit bound to wrong commit | P1 | High | High | INV-P1-001 | re-bind run to HEAD |
| Under-audited CI surface | P2 | Medium | Medium | INV-P2-002 | regenerate inventory |

## Recommendations

### Immediate / Release Blocking
- Re-bind the run to the actual commit and regenerate inventory.

### This Week
- Add a HEAD-vs-inventory staleness assertion.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Regenerate `inventory.json` | correct Wave 0 input | `inventory.json` | SHA assert |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Inventory SHA binding check | P1 | maintainer | S | none |

## Suggested Tests

- Assert `inventory.json.git.sha == $(git rev-parse --short HEAD)` in `self_test.sh`.

## Suggested Documentation Updates

- `README.md` "How a run flows": state that the run records the exact audited SHA.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was the audit intended for 6cada03 or 7bac320? | determines correct evidence set | operator confirmation |

## Appendix

Not applicable beyond the tables above.
