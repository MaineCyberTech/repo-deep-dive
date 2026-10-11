# 21_repo_hygiene_maintainability — Prompt 21 - Repository Hygiene, Maintainability, and Code Health Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `21_repo_hygiene_maintainability.md` (area HYGIENE, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (branch `main`), read-only worktree `/tmp/opencode/falcon-audit-f5cb7c9`; live host inspected read-only
- Generated at: 2026-10-11 (UTC) - Auditor: subagent, read-only
- Area code: HYGIENE
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/21_repo_hygiene_maintainability.md`
- Scope limitations: static inventories from `git ls-files`/`find`; sampled analysis of scripts/configs; no runtime mutation; live host inspected read-only.

## Scope

Reviewed: folder/file naming, duplicate/dead content, generated/build artifacts and their regeneration, imports/typing/error-handling/logging patterns (sampled), TODO/FIXME, config sprawl, competing patterns, package scripts, dependency boundaries, test utilities, docs drift, and changelog/ADRs. Not reviewed in depth: vulnerability content (domain 11/35), runtime behavior (12/13), vendored `mct/` service semantics (12/19).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Tracked tree: 3,883 files (`evidence` 2,283; `mct` 858; `docs` 344; `automation` 206; `config` 71; `sbom` 39) | inventory | layout/size | `git ls-files` |
| `sbom/` (39 files, 37 JSON, 29.6 MB, max 3,064,465 B) | generated artifact | prior HYGIENE-P2-001 | still open (finding) |
| `review-package/MANIFEST.sha256` (tracked, 506 KB) + `.gitignore:26` | generated artifact | new contradiction | HYGIENE-P2-003 |
| `docs/RELEASE_GATE.md`, `README.md`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` | status docs | docs drift | release-gate stale (finding) |
| `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `closeout/FINAL_RESPONSE.json` | binding artifacts | staleness/binding | digest bound to 3c11752; published manifest stale (cross-ref REL-P2-002) |
| `mct/VENDORING.md`, `pins/supply-chain-waivers.json` | vendored tree policy | unpinned images residual | 29/37 unpinned, waiver to 2026-12-31 (DET-P3-003 / CTR-P3-001 / ARCH-P2-002) |
| `ledgers/{evidence_index,test_execution,decision_log}` | derived records | staleness | 1,413 evidence rows; test ledger 1,127+; decision log 266 lines (last entry 2026-10-10T02:55Z) |
| Scripts: 322 `*.sh`, 121 `*.py` | code health | error handling/typing | sampled |

## Verification Performed

| Check | Command / read | Result |
|---|---|---|
| review-package tracking | `git ls-files review-package/`; `git check-ignore --no-index -v review-package/MANIFEST.sha256` | 1 tracked file (`MANIFEST.sha256`); matched by `.gitignore:26` -> HYGIENE-P2-003 |
| review-package manifest flow | `git log -- review-package/MANIFEST.sha256`; `verify_publication_chain.sh`; `check_publication_equality.py` | force-added since abb63ab (2026-10-10); the declared-commit checks depend on it; equality PASS at f5cb7c9 |
| Publication chain | `bash automation/validation/verify_publication_chain.sh` | `publication_chain_failures=0` |
| Digest binding | `python3 automation/validation/check_digest_binding.py --root .` | PASS |
| Fast gate | `python3 ci/validate.py --fast` | `validation_failures=0` |
| SBOM size/count | `find sbom -type f | wc -l`; `du -sb sbom`; largest file | 39 files / 29.6 MB (28.2 MiB) / max 3,064,465 B |
| Unpinned vendored images | `grep image: mct/compose/*.yml` | 37 refs, 29 not digest-pinned |
| TODO/FIXME | `git ls-files '*.sh' '*.py' | xargs grep -lE 'TODO|FIXME'` | 0 files |
| Duplicates | sha256 of every tracked file | 38 duplicate groups (evidence captures, register mirrors, vendored pairs) |
| Shell error handling | per-file `set -e` scan | 229/322 scripts without errexit (capture/test tools by design) |
| Largest tracked non-generated files | `stat` + sort | ledgers/test_execution.csv 728 KB; manifests 506 KB; decision_log 229 KB |
| LICENSE/NOTICE | `git ls-files | grep -iE '(^|/)(LICENSE|NOTICE|COPYING)'` | none -> HYGIENE-P3-001 (DET-P3-001) |
| Release-gate currency | `docs/RELEASE_GATE.md:48` vs `docs/audits/` listing | 20261003 opinion; newest in-repo full run 20261005 -> HYGIENE-P2-002 |

## Executive Summary

Mechanical hygiene remains strong: naming is consistent, there are zero TODO/FIXME markers in code, the pre-commit gate passes its fast subset, the publication chain verifies at the declared commit, and the prior HYGIENE-P1-001 untracking is still documented. The material issues are generated-artifact weight and stale status/binding artifacts. The committed SBOM/vuln JSON is unchanged at 29.6 MB across 39 files with no freshness gate (HYGIENE-P2-001). The canonical release-gate page still presents the 2026-10-03 audit opinion while the newest in-repo full run (20261005) reports GO WITH CONDITIONS with a P0, and README still dates the current state to 2026-09-30 (HYGIENE-P2-002). New this run: the publication flow force-added `review-package/MANIFEST.sha256` as a tracked "declared manifest" while `.gitignore`, `AGENTS.md`, `REPOSITORY.md` and `build_review_package.sh` all say the review package must not be committed - a contradiction that is load-bearing for the publication equality gate and that already misled the 2026-10-11 verification run into reporting the manifest as absent (HYGIENE-P2-003). The LICENSE/NOTICE residual persists (HYGIENE-P3-001; owner decision recorded 2026-10-04). Unpinned vendored images (29/37) and the stale published `PACKAGE_MANIFEST.sha256` are verified and remain tracked under DET-P3-003/CTR-P3-001/ARCH-P2-002 and REL-P2-002 respectively.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| review-package manifest | `review-package/MANIFEST.sha256` | Declared package manifest | Tracked since abb63ab; gitignored pattern | Medium | HYGIENE-P2-003 |
| SBOM/vuln JSON | `sbom/`, `sbom/vuln/` | Image provenance/scans | Committed, 29.6 MB | Medium | HYGIENE-P2-001 |
| Binding artifacts | `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256` | Delivery binding | Digest current (3c11752); published manifest stale | Medium | REL-P2-002 |
| Release-gate page | `docs/RELEASE_GATE.md` | Canonical reconciliation | Stale 20261003 opinion | Medium | HYGIENE-P2-002 |
| LICENSE | - | licensing | absent | Low | HYGIENE-P3-001 |
| Vendored tree | `mct/` (858 files) | imported snapshot | banner + policy; owner decision pending | Medium | DET-P3-003/CTR-P3-001/ARCH-P2-002 |
| Ledgers | `ledgers/*` | records | append-only; large (decision log 229 KB) | Low | by design |
| Pack-fidelity notes | `PACK_VERIFICATION_NOTES.txt`, `PACK_NOT_INCLUDED.txt` | delivery notes | last touched df934e5 (2026-10-01) while the package was rebuilt 2026-10-10/11 | Low | cross-ref DOC-P2-001/INV-P3-002 (open) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Folder/file naming | 4 | root layout, numeric bootstrap prefixes, no spaces | - | keep |
| Duplicate/dead/unused code | 4 | 38 duplicate groups, mostly evidence captures/register mirrors/vendored pairs | vendored pairs by design | keep banners |
| Generated/build artifacts | 3 | SBOM 29.6 MB; tracked declared manifest; pack notes stale | no regeneration/freshness gate; tracking contradiction | HYGIENE-P2-001 / HYGIENE-P2-003 |
| Imports and circular deps | 4 | stdlib Python; no cycles observed in sampled modules | no import lint | optional |
| Large files/components | 3 | manifests 506 KB; test ledger 728 KB; SBOM 3.0 MB | large generated artifacts in git | HYGIENE-P2-001 |
| Type safety/any usage | 3 | ruff E9,F,B only; no mypy/pyright | no type gate | optional checker |
| Error handling | 3 | 229/322 scripts without errexit; capture/test tools by design | explicit-check house style | document pattern |
| TODO/FIXME | 5 | 0 occurrences in code | - | keep |
| Logging consistency | 4 | echo + evidence metadata; no logging module | two styles (script/test) | optional |
| Config sprawl | 3 | `config/` 15 subdirs; first-party + vendored compose projects | discovery cost | index/config map |
| Competing patterns | 3 | `mct/` banner + VENDORING policy (owner decision pending) | staged services archive-only | record owner decision |
| Package scripts | 3 | documented shell/python entry points; no pyproject/make | no standard task runner | optional |

## Detailed Review

### Item: tracked review-package manifest (HYGIENE-P2-003, new)

- Evidence: `git ls-files review-package/` -> `review-package/MANIFEST.sha256` (3,830 entries, 506 KB); `git check-ignore --no-index -v review-package/MANIFEST.sha256` -> `.gitignore:26:review-package/`; `git log --oneline -- review-package/MANIFEST.sha256` -> `abb63ab review-package: rebuild at 95c89f4 (declared manifest)` (new file, 3,830 insertions), then b09a50f, 3c11752; docs say not committed: `AGENTS.md:44` ("gitignored, do NOT commit (HYG-P1-001)"), `REPOSITORY.md:33,47,51`, `build_review_package.sh:9-10` ("must not be committed"), `check_publication_equality.py` docstring.
- Why it matters: the declared-commit checks in `verify_publication_chain.sh` and `check_publication_equality.py` require the manifest at the declared commit; when it is absent they print a "not committed ... skipped" note and skip the restriction (fail-open). An agent following the docs would not create the manifest commit and can break the equality gate (already observed once as CI-P2-004, rebound 2026-10-11).
- Verification: the 2026-10-11 04:00 verification run reported "review-package/ ... absent (gitignored, HYG-P1-001)" while the manifest was tracked at 584e1a3 - direct evidence the contradiction misleads readers.
- Recommended fix: document the declared-manifest exception and either add a narrow negation (`!review-package/MANIFEST.sha256`) with the flow in AGENTS.md/REPOSITORY.md, or move the declared manifest to a non-ignored path; add a test that fails when the declared-commit manifest binding is skipped.

### Item: generated SBOM/vulnerability JSON (HYGIENE-P2-001)

- Evidence: `sbom/` 39 files / 29.6 MB (37 JSON; largest `sbom/opensearchproject_opensearch-dashboards_2.19.6.cdx.json` 3,064,465 B); CI verifies hashes (`sbom_hashes.sh`, wired in `validate.yml`) but nothing forces regeneration/freshness; the 2026-10-11 04:00 verification kept the finding still-open (39 files / 29.6 MB).
- Recommendation: release-artifact storage or compression; add a freshness gate/waiver.

### Item: status and binding documentation currency (HYGIENE-P2-002)

- Evidence: `docs/RELEASE_GATE.md:48` "Current audit opinion (run 20261003-0018-fix-backup-abort-markers-20b5e57...)"; the newest in-repo full run `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md` = "GO WITH CONDITIONS, P0 x1, P1 x7" and is unreferenced; `README.md:8-11` "Current state (2026-09-30)"; `README.md:138` "Current state (2026-10-02...)"; `docs/CURRENT_STATE.md` references the 20261009 run only in its 2026-10-09/10 section.
- Recommendation: refresh the pointers; add a doc-drift test (newest committed run newer than referenced -> fail).

### Item: vendored MCT tree and unpinned images (known residual)

- Evidence: `mct/VENDORING.md`; 37 image refs in `mct/compose`, 29 not digest-pinned (deterministic lens DET-P3-003); `pins/supply-chain-waivers.json` blanket `mct/compose` waiver review_by 2026-12-31; `ci/validate.py` "compose image pinning" passes because the vendored tree is out of scope.
- Assessment: tracked as DET-P3-003 / CTR-P3-001 / ARCH-P2-002; not refiled. The owner decision remains the dependency.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| HYGIENE-001 | Folder/file naming | `git ls-files` | Convention documented | - | - | Keep |
| HYGIENE-002 | Duplicate/dead code | hash scan; `mct/` banner | Banners + policy | Owner decision pending | P3 | Record decision |
| HYGIENE-003 | Generated/build artifacts | sbom/, review-package manifest, pack notes | Hash/coverage gates | No freshness gate; tracking contradiction; stale pack notes | P2 | HYGIENE-P2-001 / HYGIENE-P2-003 |
| HYGIENE-004 | Imports/circular deps | sampled modules | stdlib, no cycles | No import lint | P3 | Optional |
| HYGIENE-005 | Large files | manifests 506 KB; SBOM 3.0 MB | - | Generated artifacts in git | P2 | HYGIENE-P2-001 |
| HYGIENE-006 | Type safety | ruff E9/F/B only | Lint | No type gate | P3 | Optional |
| HYGIENE-007 | Error handling | 229/322 no errexit | shellcheck + explicit checks | By-design pattern | P3 | Document |
| HYGIENE-008 | TODO/FIXME | 0 in code | Discipline | - | - | Keep |
| HYGIENE-009 | Logging | echo/capture metadata | Evidence model | Two styles | P3 | Optional |
| HYGIENE-010 | Config sprawl | config/ 15 subdirs | Documented layout | Discovery cost | P3 | Config map |
| HYGIENE-011 | Competing patterns | mct vs falcon docs | Banner + policy | Pending decision | P3 | Record decision |
| HYGIENE-012 | Package scripts | shell/python entry points | Documented flows | No task runner | P3 | Optional |

## Findings

### HYGIENE-P2-001 - Large generated SBOM/vulnerability JSON remains committed

- Severity: P2
- Confidence: High
- Area: HYGIENE
- Evidence:
  - `du -sb sbom` -> 29.6 MB (28.2 MiB); `find sbom -type f | wc -l` -> 39; `find sbom -name '*.json' | wc -l` -> 37
  - largest: `sbom/opensearchproject_opensearch-dashboards_2.19.6.cdx.json` 3,064,465 B
  - `automation/validation/sbom_hashes.sh` verifies hashes in `validate.yml`; no freshness/regeneration gate
- What is happening: the generated SBOM/vulnerability payloads are committed at the same size as the prior full run; nothing forces regeneration or expiry.
- Why it matters: clone/build weight, review noise, stale scans mistaken for current.
- Recommended fix: move to release-artifact storage or compress; add a freshness gate/waiver.
- Suggested validation: CI fails if scans are older than N days without a waiver; `du -sh sbom` budget.
- Owner suggestion: maintainer
- Effort estimate: M
- Status: still-open

### HYGIENE-P2-002 - Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced

- Severity: P2
- Confidence: High
- Area: HYGIENE
- Evidence:
  - `docs/RELEASE_GATE.md:48` "Current audit opinion (run `20261003-0018-fix-backup-abort-markers-20b5e57`, commit `20b5e57`)"
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md` -> "GO WITH CONDITIONS", "P0 x1, P1 x7"
  - `README.md:8-11` "Current state (2026-09-30)"; `README.md:138` "Current state (2026-10-02, audit reconciliation)"
  - `docs/CURRENT_STATE.md` references the 20261009 run only in the 2026-10-09/10 section; the canonical gate page does not
- What is happening: the canonical reconciliation page still presents the 2026-10-03 opinion while two newer full runs exist (20261005 in-repo; 20261009/20261011 outside), so a reader can miss the newest P0/conditions.
- Why it matters: the page's stated purpose (no lab/production confusion) is undermined by staleness.
- Recommended fix: refresh the current-opinion pointer; add a doc-drift test.
- Suggested validation: CI fails if the newest committed `docs/audits/repo-deep-dive/*` full run is newer than the run referenced by `docs/RELEASE_GATE.md`.
- Owner suggestion: maintainer
- Effort estimate: S
- Status: open

### HYGIENE-P2-003 - The publication flow force-tracks `review-package/MANIFEST.sha256` while four sources say the review package must not be committed; the file is load-bearing for the declared-commit gates

- Severity: P2
- Confidence: High
- Area: HYGIENE
- Evidence:
  - `git ls-files review-package/` -> `review-package/MANIFEST.sha256` (3,830 entries); `git check-ignore --no-index -v review-package/MANIFEST.sha256` -> `.gitignore:26:review-package/`
  - `git show --stat abb63ab` -> new file review-package/MANIFEST.sha256, 3,830 insertions (2026-10-10); repeated at b09a50f, 3c11752 ("review-package: rebuild at <sha> (declared manifest)")
  - `AGENTS.md:44` "generated artifact; gitignored, do NOT commit (HYG-P1-001)"; `REPOSITORY.md:33,47,51` "not committed"; `automation/validation/build_review_package.sh:9-10` "must not be committed"; `check_publication_equality.py` docstring "now a generated, gitignored artifact (HYG-P1-001)"
  - `verify_publication_chain.sh` check 3 and `check_publication_equality.py` declared-commit checks require the manifest at the declared commit; when absent they skip with a note (fail-open): "note: review-package/ not committed ... post-publication ancestry restriction skipped"
  - The 2026-10-11 04:00 verification run reported "review-package/ ... absent (gitignored, HYG-P1-001)" while the manifest was tracked at 584e1a3
- What is happening: the declared manifest was force-added (despite the ignore rule) to make the publication equality gate pass after CI-P2-004; the docs were never updated, so the tracked state and the documented state contradict each other and the binding is fail-open when the file is absent.
- Why it matters: an agent or publication session following the docs will not commit/refresh the manifest, re-breaking the equality gate or silently skipping the declared-commit binding; auditors already mis-reported the state.
- Recommended fix: document the declared-manifest exception in AGENTS.md/REPOSITORY.md (and the flow), and either add a narrow `.gitignore` negation for `review-package/MANIFEST.sha256` or relocate the declared manifest to a non-ignored path; add a test that the declared-commit manifest binding cannot be skipped silently.
- Suggested validation: CI check asserting the declared commit contains the review-package manifest when `PACKAGE_DIGEST.txt` declares `review_package_manifest_sha256`; docs lint that AGENTS/REPOSITORY wording matches the tracked state.
- Owner suggestion: maintainer
- Effort estimate: S/M
- Dependencies: publication flow owners
- Status: open

### HYGIENE-P3-001 - No root LICENSE/NOTICE file; README ownership section grants no terms

- Severity: P3
- Confidence: High
- Area: HYGIENE
- Evidence:
  - `git ls-files | grep -iE '(^|/)(LICENSE|NOTICE|COPYING)(\.|$)'` -> none
  - deterministic lens (current run) DET-P3-001 "[GIT] No LICENSE file"
  - `ledgers/decision_log.md` 2026-10-04 entry: LICENSE listed as an owner decision (private repo)
  - `ci/license_check.py` covers dependency licenses, not the repository license
- What is happening: the repository has no root license/notice; the README ownership section grants no terms.
- Why it matters: licensing ambiguity for reviewers/consumers.
- Recommended fix: add a proprietary LICENSE/NOTICE (or record the owner decision in-repo, e.g. docs/).
- Owner suggestion: owner
- Effort estimate: S
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale scans mistaken for current | P2 | Medium | Medium | sbom/ no freshness gate | HYGIENE-P2-001 |
| Operator/agent misses newest P0/conditions | P2 | Medium | Medium | RELEASE_GATE stale | HYGIENE-P2-002 |
| Publication binding breaks or is skipped | P2 | Medium | Medium | tracked manifest vs "do not commit" docs; CI-P2-004 history | HYGIENE-P2-003 |
| Licensing ambiguity | P3 | Low | Low | no LICENSE | HYGIENE-P3-001 |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Align the review-package commit instruction with the enforced flow (HYGIENE-P2-003).
- Refresh the release-gate/README pointers to the newest run (HYGIENE-P2-002).

### This Month
- SBOM/vuln JSON to release artifacts or compress + freshness gate (HYGIENE-P2-001).
- Add LICENSE/NOTICE or record the decision (HYGIENE-P3-001).

### Later / Platform Evolution
- Record the `mct/` keep/extract/delete decision and wire the vendoring policy into CI; refresh/retire the pack-fidelity notes.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Refresh release-gate pointers | Operators see the current P0 | `docs/RELEASE_GATE.md`, `README.md` | newest run referenced |
| Add LICENSE/NOTICE | Removes licensing ambiguity | root `LICENSE` | file present |
| Fix the AGENTS.md review-package instruction | Removes a gate-breaking instruction | `AGENTS.md`, `REPOSITORY.md` | wording matches tracked state |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| SBOM artifact storage + freshness gate | P2 | maintainer | M | release pipeline |
| Declared-manifest policy + test | P2 | maintainer | S/M | publication flow |
| Doc-drift check for run references | P3 | maintainer | S | none |
| Type gate (mypy/pyright) for automation | P3 | maintainer | M | none |

## Suggested Tests

- CI: fail if the newest committed run is newer than the run referenced by `docs/RELEASE_GATE.md`.
- CI: assert the declared commit contains `review-package/MANIFEST.sha256` when the digest declares it (no silent skip).
- CI: SBOM freshness - refuse to ship scans older than N days without a waiver.
- Negative test: planted secret under `docs/audits/` still fails the scanner (existing).

## Suggested Documentation Updates

- `docs/RELEASE_GATE.md` - refresh the current audit opinion.
- `README.md` - refresh the current-state line.
- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` - derive the current run.
- `AGENTS.md` / `REPOSITORY.md` - declared-manifest exception and flow.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the declared manifest intentionally tracked, or a workaround? | Determines the fix (document vs relocate) | Owner/maintainer answer; PR #49+ history |
| SBOM retention policy? | Repo weight vs reviewability | Owner decision |

## Prior-Run Comparison

- `HYGIENE-P2-001` (SBOM/vuln JSON): prior still-open -> **still-open** (39 files / 29.6 MB; unchanged).
- `HYGIENE-P2-002` (release-gate staleness): prior open -> **open**; the newest in-repo full run remains 20261005 and is still unreferenced by the gate page.
- `HYGIENE-P3-001` (LICENSE): prior open -> **open** (DET-P3-001).
- Prior `HYGIENE-P1-001` (stale committed review-package): still **verified-fixed** for the package tree, but the force-tracked `MANIFEST.sha256` is a new contradiction (HYGIENE-P2-003).
- New this run: HYGIENE-P2-003 (tracked declared manifest vs docs); unpinned vendored images verified (29/37) and left under DET-P3-003/CTR-P3-001/ARCH-P2-002.

## Limitations

- Duplicate/dead-code analysis is hash/sample based; vendored upstream semantics were not compared file-by-file.
- No full `ci/validate.py` run (needs lab/offsite context); `--fast` subset + targeted checks were used.
- Live host checks were read-only.

## Appendix - tracked tree by top-level directory

| Dir | Files | Dir | Files |
|---|---:|---|---:|
| evidence | 2,283 | config | 71 |
| mct | 858 | sbom | 39 |
| docs | 344 | bootstrap | 30 |
| automation | 206 | ledgers | 11 |

## Findings

| ID | Severity | Title |
|---|---|---|
| HYGIENE-P2-001 | P2 | Large generated SBOM/vulnerability JSON remains committed (39 files, 29.6 MB, up to 3.0 MB each) |
| HYGIENE-P2-002 | P2 | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced |
| HYGIENE-P2-003 | P2 | The publication flow force-tracks review-package/MANIFEST.sha256 while .gitignore, AGENTS.md, REPOSITORY.md and build_review_package.sh say the review package must not be committed; the file is load-bearing for the declared-commit gates |
| HYGIENE-P3-001 | P3 | No root LICENSE/NOTICE file; README ownership section grants no terms |
