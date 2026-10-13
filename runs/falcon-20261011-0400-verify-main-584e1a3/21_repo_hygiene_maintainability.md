# 21_repo_hygiene_maintainability — Prompt 21 - Repository Hygiene, Maintainability, and Code Health Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `21_repo_hygiene_maintainability.md` (area HYGIENE, prompt)

## Verification Performed

# Repository Hygiene, Maintainability, and Code Health Audit — falcon @ 08e20d1

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` @ `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d` (branch `main`), read-only worktree `/tmp/opencode/falcon-audit-08e20d1`
- Generated at: 2026-10-09 · Auditor: subagent, read-only
- Area code: HYGIENE
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/21_repo_hygiene_maintainability.md`
- Scope limitations: static inventories from `git ls-files`/`find`; sampled analysis of scripts/configs; no runtime mutation; live host inspected read-only where claims needed verification.

## Scope

Reviewed: folder/file naming, duplicate/dead content, generated/build artifacts and their regeneration, imports/typing/error-handling/logging patterns (sampled), TODO/FIXME, config sprawl, competing patterns, package scripts, dependency boundaries, test utilities, docs drift, and changelog/ADRs. Not reviewed in depth: vulnerability content (domain 11/35), runtime behavior (12/13), vendored `mct/` service semantics (12/19).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Tracked tree: 3,865 files (`evidence` 2,269; `mct` 858; `docs` 344; `automation` 205; `config` 69; `sbom` 39) | inventory | layout/size | `git ls-files` |
| `review-package/` absence + `.gitignore:26` | generated artifact | prior HYGIENE-P1-001 | verified-fixed |
| `sbom/` (25 cdx + 12 vuln, 29 MB) | generated artifact | prior HYGIENE-P2-001 | still open (finding) |
| `docs/RELEASE_GATE.md`, `README.md`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` | status docs | docs drift | release-gate stale (finding) |
| `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `closeout/FINAL_RESPONSE.json` | binding artifacts | staleness/binding | bound to 69b3c80; declared-commit checks pass |
| `mct/VENDORING.md`, `pins/supply-chain-waivers.json` | vendored tree policy | unpinned images residual | 29/37 unpinned, waiver to 2026-12-31 |
| `ledgers/{evidence_index,test_execution,decision_log}.md|csv` | derived records | staleness | 1,128 / 1,128 / 250 lines |
| Scripts: 321 `*.sh`, 121 `*.py` | code health | error handling/typing | sampled |

## Verification Performed

| Check | Command / read | Result |
|---|---|---|
| review-package untracked | `git ls-files | grep -c '^review-package/'` / `git check-ignore` | 0 tracked files; `.gitignore:26` matches — HYGIENE-P1-001 **verified-fixed** |
| Publication chain at declared commit | `bash automation/validation/verify_publication_chain.sh` | `publication_chain_failures=0`; signed archives intact |
| Digest/manifest consistency | `sha256sum PACKAGE_MANIFEST.sha256` vs digest field | matches (`5f591655...`); 3,783 entries; 3 known package-generated exclusions |
| Fast gate | `python3 ci/validate.py --fast` | `validation_failures=0` |
| SBOM size/count | `du -sh sbom`; `find sbom -name '*.json' -printf '%s\n' | sort -rn` | 29 MB; max 3,064,465 B; 37 files |
| Unpinned vendored images | `grep image: mct/compose/*.yml` | 37 refs, 29 unpinned, 12 floating (`latest`/`stable`) |
| TODO/FIXME | `git ls-files '*.sh' '*.py' | xargs grep -c` | 0 occurrences in code |
| Duplicates | sha256 of every tracked file | 38 duplicate groups — mostly evidence captures, register mirrors and vendored pairs (no misleading dead source found in the sample) |
| Shell error handling | per-file `set -e` scan | 230/321 scripts have no `set -e` (by design in capture/test tools); 153 are >50 lines |
| Live drift spot-checks | `nft list`, `docker ps`, worktree status | live host at a divergent worktree; firewall fix not applied (cross-ref CHAIN) |

## Executive Summary

Mechanical hygiene is strong: naming is consistent, there is no TODO/FIXME debt in code, the pre-commit gate passes its fast subset, the review-package duplication (prior HYGIENE-P1-001) is genuinely closed by untracking the generated tree and documenting it in `REPOSITORY.md`/`AGENTS.md`, and the publication chain still verifies at its declared commit. The material issues are generated-artifact weight and status-page staleness: the committed SBOM/vuln JSON is now 29 MB (max 3.0 MB per file) with no regeneration/freshness gate beyond hash verification, and the canonical release-gate page still presents the 2026-10-03 audit opinion while the newest full run reports a P0 and GO WITH CONDITIONS. The LICENSE residual persists (no root LICENSE/NOTICE). The unpinned vendored images and review-package binding staleness were verified and remain tracked under their owning findings (DET-P3-002/CTR-P3-001/ARCH-P2-002, INFRA-P2-001).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| review-package | `review-package/` | delivery artifact | untracked, gitignored | Low | HYGIENE-P1-001 fixed |
| SBOM/vuln JSON | `sbom/`, `sbom/vuln/` | image provenance/scans | committed, 29 MB | Medium | HYGIENE-P2-001 |
| Binding artifacts | `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256` | delivery binding | bound to 69b3c80 | Low | declared-commit checks pass |
| Release-gate page | `docs/RELEASE_GATE.md` | canonical reconciliation | stale run reference | Medium | new P2 |
| LICENSE | — | licensing | absent | Low | new P3 / DET-P3-001 |
| Vendored tree | `mct/` (858 files) | imported snapshot | banner + policy; owner decision pending | Medium | EVOL-P2-004/ARCH-P2-002 |
| Ledgers | `ledgers/*` | records | append-only; large (decision log 221 KB) | Low | by design |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Folder/file naming | 4 | root layout, numeric bootstrap prefixes, no spaces | — | keep |
| Duplicate/dead/unused code | 4 | 38 duplicate groups, mostly evidence captures/register mirrors/vendored pairs | vendored pairs by design | keep banners |
| Generated/build artifacts | 3 | review-package fixed; SBOM 29 MB; evidence 14 MB | no regeneration/freshness gate for SBOM | HYGIENE-P2-001 |
| Imports and circular deps | 4 | stdlib Python; no cycles observed in sampled modules | no import lint | optional |
| Large files/components | 3 | max source ~712 lines; SBOM 3.0 MB; evidence outs 2 MB | large generated JSON in git | HYGIENE-P2-001 |
| Type safety/any usage | 3 | ruff `E9,F,B` only; no mypy/pyright | no type gate | optional checker |
| Error handling | 3 | 230/321 scripts without `set -e`; capture/test tools by design; shellcheck warning gate | explicit-check house style | document pattern |
| TODO/FIXME | 5 | 0 occurrences in code | — | keep |
| Logging consistency | 4 | echo + evidence metadata; no logging module | two styles (script/test) | optional |
| Config sprawl | 3 | `config/` 15 subdirs; 3 first-party compose projects + 8 staged vendored compose files | discovery cost | index/config map |
| Competing patterns | 3 | `mct/` banner + VENDORING policy (owner decision pending); upstream vs falcon docs | staged services archive-only | record owner decision |
| Package scripts | 3 | documented shell/python entry points; no pyproject/make | no standard task runner | optional |

## Detailed Review

### Item: review-package untracking (prior HYGIENE-P1-001)

- Evidence: `.gitignore:26`; `REPOSITORY.md:33,47,51-59`; `AGENTS.md:44`; `README.md:116-120`.
- Verification: no tracked `review-package/**` files; the directory is absent from the worktree; `verify_publication_chain.sh` skips the working-tree manifest check with an explicit note and validates the declared commit instead. Status: **verified-fixed** (artifact committed at a2dded8 / PR #43).
- Residual: `PACKAGE_DIGEST.txt`/`PACKAGE_MANIFEST.sha256`/`FINAL_RESPONSE.json` remain bound to commit 69b3c80 (11 commits behind HEAD) by design; no HEAD drift gate exists (INFRA-P2-001, open). This is a binding-scope residual, not a regression of HYGIENE-P1-001.

### Item: generated SBOM/vulnerability JSON

- Evidence: `sbom/` 25 cdx + `sbom/vuln/` 12 scans = 29 MB; largest 3,064,465 B; CI verifies hashes (`validate.yml:103-106`) and coverage, but nothing forces regeneration.
- Risk: repo clone/build weight, review noise, stale scans mistaken for current.
- Recommendation: release-artifact storage or compression; freshness gate.

### Item: status/audit documentation currency

- Evidence: `docs/RELEASE_GATE.md:48-56` (20261003 run as "current"), README.md:138 (2026-10-02), `AUDIT_RUN_LIFECYCLE.md:39-42` (2026-09-30 as "current run") vs the committed 20261005 full run.
- Risk: operators and agents miss the newest P0/conditions; the release-gate page's purpose (no lab/production confusion) is undermined by staleness.
- Recommendation: refresh the pointers; add a doc-drift test (see findings).

### Item: vendored MCT tree and unpinned images

- Evidence: `mct/VENDORING.md` (policy proposed 2026-10-01; owner decision pending); 37 image refs in `mct/compose`, 29 unpinned, 12 floating; `pins/supply-chain-waivers.json` blanket `mct/compose` waiver review_by 2026-12-31; `ci/validate.py` pin check globs `compose/**` only.
- Verification: `python3 ci/validate.py --fast` reports `PASS compose image pinning` because the vendored tree is out of scope — the documented blind spot is still present.
- Assessment: tracked as DET-P3-002 / CTR-P3-001 / ARCH-P2-002; not refiled. The banner and VENDORING policy make the state honest; the owner decision remains the dependency.

### Item: code health sample

- Evidence: 321 shell scripts / 121 Python modules; no TODO/FIXME; `capture.sh` intentionally records exit codes (no errexit); long runners (`bootstrap/80-offsite-backup.sh`) use `set -euo pipefail` + traps; CI runs actionlint/shellcheck/ruff/zizmor/gitleaks.
- Assessment: healthy for an ops repo; type checking and a task runner remain maturity gaps.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| HYGIENE-001 | Folder/file naming | `git ls-files` | Convention documented | — | — | Keep |
| HYGIENE-002 | Duplicate/dead code | hash scan; `mct/` banner | Banners + policy | Owner decision pending | P3 | Record decision |
| HYGIENE-003 | Generated/build artifacts | sbom/, digest, manifests | Hash/coverage gates | No freshness gate; 29 MB | P2 | HYGIENE-P2-001 |
| HYGIENE-004 | Imports/circular deps | sampled modules | stdlib, no cycles | No import lint | P3 | Optional |
| HYGIENE-005 | Large files | sbom 3.0 MB; scripts ≤712 lines | — | Generated JSON in git | P2 | HYGIENE-P2-001 |
| HYGIENE-006 | Type safety | ruff E9/F/B only | Lint | No type gate | P3 | Optional |
| HYGIENE-007 | Error handling | 230/321 no errexit | shellcheck + explicit checks | By-design pattern | P3 | Document |
| HYGIENE-008 | TODO/FIXME | 0 in code | Discipline | — | — | Keep |
| HYGIENE-009 | Logging | echo/capture metadata | Evidence model | Two styles | P3 | Optional |
| HYGIENE-010 | Config sprawl | config/ 15 subdirs | Documented layout | Discovery cost | P3 | Config map |
| HYGIENE-011 | Competing patterns | mct vs falcon docs | Banner + policy | Pending decision | P3 | Record decision |
| HYGIENE-012 | Package scripts | shell/python entry points | Documented flows | No task runner | P3 | Optional |

## Findings

### Finding: HYGIENE-P2-001 — Large generated SBOM/vulnerability JSON remains committed (see JSON)

### Finding: HYGIENE-P2 (new) — Canonical release-gate page carries a superseded audit opinion (see JSON)

### Finding: HYGIENE-P3 (new) — No root LICENSE/NOTICE file (see JSON; cross-ref DET-P3-001)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale scans mistaken for current | P2 | Medium | Medium | sbom/ no freshness gate | HYGIENE-P2-001 |
| Operator misses newest P0/conditions | P2 | Medium | Medium | RELEASE_GATE stale | new P2 |
| Licensing ambiguity | P3 | Low | Low | no LICENSE | new P3 |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Refresh the release-gate/README pointers to the newest run (new P2).

### This Month
- SBOM/vuln JSON to release artifacts or compress + freshness gate (HYGIENE-P2-001).
- Add LICENSE/NOTICE (new P3).

### Later / Platform Evolution
- Record the `mct/` keep/extract/delete owner decision and wire the vendoring policy into CI.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Refresh release-gate pointers | Operators see the current P0 | `docs/RELEASE_GATE.md`, `README.md` | newest run referenced |
| Add LICENSE/NOTICE | Removes licensing ambiguity | root `LICENSE` | file present |
| Compress SBOM JSON | Cuts repo weight | `sbom/` | `du -sh` drops |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| SBOM artifact storage + freshness gate | P2 | maintainer | M | release pipeline |
| Doc-drift check for run references | P3 | maintainer | S | none |
| Type gate (mypy/pyright) for automation | P3 | maintainer | M | none |

## Suggested Tests

- CI: fail if the newest committed run is newer than the run referenced by `docs/RELEASE_GATE.md`.
- CI: SBOM freshness — refuse to ship scans older than N days without a waiver.
- Negative test: planted secret under `docs/audits/` still fails the scanner (existing test).

## Suggested Documentation Updates

- `docs/RELEASE_GATE.md` — refresh the current audit opinion.
- `README.md` — refresh the current-state line.
- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` — derive the current run.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Keep/extract/delete the `mct/` subtree? | Determines urgency of pin enforcement | Owner decision |
| SBOM retention policy? | Repo weight vs reviewability | Owner decision |

## Prior-Run Comparison

- `HYGIENE-P1-001` (stale committed review-package): **verified-fixed** at a2dded8 (PR #43) — reproduced here (0 tracked files, `.gitignore:26`, docs updated).
- `HYGIENE-P2-001` (large generated SBOM/vuln JSON): prior "partially-fixed" → still open at this commit, and larger (29 MB, 3.0 MB max).
- 2026-09-30 residuals: audit-folder/validate conflict (HYGIENE-P2-001 of that run) fixed via lifecycle + scanner skip; stale pack/closeout artifacts (HYGIENE-P2-002/003) were partially addressed; the release-gate staleness filed here is a current instance of that class.
- New this run: release-gate staleness (P2), LICENSE absence (P3, cross-ref DET-P3-001).

## Limitations

- Duplicate/dead-code analysis is hash/sample based; vendored upstream semantics were not compared file-by-file.
- No full `ci/validate.py` run (needs lab/offsite context); `--fast` subset + targeted checks were used.
- Live host checks were read-only and used only to verify claims about generated/runtime artifacts.

## Appendix — tracked tree by top-level directory

| Dir | Files | Dir | Files |
|---|---:|---|---:|
| evidence | 2,269 | config | 69 |
| mct | 858 | sbom | 39 |
| docs | 344 | bootstrap | 30 |
| automation | 205 | ledgers | 11 |

## Findings

| ID | Severity | Title |
|---|---|---|
| HYGIENE-P2-001 | P2 | Large generated SBOM/vulnerability JSON remains committed (37 files, 29 MB, up to 3.0 MB each) |
| HYGIENE-P2-002 | P2 | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced |
| HYGIENE-P3-001 | P3 | No root LICENSE/NOTICE file; README ownership section grants no terms |
