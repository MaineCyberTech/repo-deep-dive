# Repository Hygiene, Maintainability, and Code Health Audit

## Audit Metadata

- Audit name: `repo-deep-dive` (profile `falcon-lab` v1.0.0, pack v1.2.1)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repository: `falcon-build` @ `8282d3f`; `falcon-edge-build` @ `f1c5def` (moved `45dfed0`→`f1c5def` during the run; CI/evidence delta)
- Branch: `main` (both). falcon working tree dirty: `M evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out`, `?? docs/audits/`, `??` its `.meta.json`; edge clean
- Generated at: 2026-09-30 · Auditor: wave-1 subagent (prompt 21), read-only (no root/docker/service mutation; no secret values printed)
- Area code: HYGIENE · Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/21_repo_hygiene_maintainability.md`
- Scope limitations: inventories from `git ls-files`/`find`; static analysis limited to what CI already runs (ruff/actionlint/shellcheck); ignored dirs inspected but not cleaned.

## Scope

Reviewed: layout/naming, duplicate/dead files, generated/build artifacts and regeneration, imports/typing/error-handling/logging/config patterns (sampled), TODO/FIXME, package scripts, and this run's artifact interaction with CI. Not reviewed in depth: runtime behavior (12), vulnerability content (11/35), off-repo `mct/` services (12).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| falcon tracked tree: 4,165 files (`review-package` 2,067; `evidence` 934; `mct` 856) | inventory | layout/duplication | `git ls-files` |
| falcon generated set: `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `PACK_*`, `closeout/FINAL_RESPONSE*.json` | generated artifacts | pack/digest/response binding | digest `3ac6cd4`; manifest == package manifest `0e5912…` |
| falcon derived records: `evidence_index.csv`, `test_execution.csv`, `progress_ledger.md`, `risk_register.md`, `exception_register.md` | indexes/records | staleness | index 461 rows (264 host paths); progress "PASS 62" |
| falcon CI/run: `.github/workflows/validate.yml`, `ci/validate.py`, `.gitleaks.toml`, `docs/audits/**` | CI + run artifacts | audit-vs-CI | `ci/validate.py` exit 1 (CI-P2-001) |
| `/home/user/falcon-repomix.md` + `verify_pack.py`; gate notes P8-G01/P1-G06 | delivered pack + notes | packed-only verification | INCOMPLETE (37 mismatched/957 missing); notes claim 991/991 and clean scan |
| edge tree: 914 files + `closeout/FINAL_RESPONSE.json`, `PROGRAM_CLOSEOUT.md`, phase CLOSEOUTs; `falcon-firstboot.sh`; `image/out/`, `__pycache__`, `.ruff_cache/`; `ci/validate.sh` | inventory/generated/dead/CI | layout, staleness, cleanup | FINAL_RESPONSE `d6147ef`; "120 tests"; script unreferenced; edge CI ALL PASS |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 automation/validation/verify_pack.py /home/user/falcon-repomix.md` | execution | pack staleness | `pack_files_parsed=1118`, `manifest_entries_total=2067`, `mismatched=37`, `missing_from_pack=957`, `INCOMPLETE` |
| `python3 ci/validate.py` (falcon) | execution | CI interaction | exit 1 — 2 `long_hex` hits in `docs/audits/.../01,02` (CI-P2-001 reproduced) |
| `bash automation/validation/verify_publication_chain.sh`; `bash automation/evidence/manifest.sh check` | execution | binding/integrity | 0 failures; manifest check exit 1 (1 uncommitted mismatch) |
| `bash ci/validate.sh` (edge) | execution | hygiene baseline | ALL PASS (897 files, 321 captures) |
| `sha256sum` manifest comparison; ownership listings; sampled counts | execution/inspection | duplicates, permissions, code health | identical manifest digests (intentional copy); root-owned outputs; 0 TODO/FIXME in sampled dirs |

## Executive Summary

Mechanical hygiene is strong: small stdlib modules, validator-guarded trees, no TODO/FIXME debt in sampled paths, edge CI green, falcon manifests verify and the publication chain reports 0 failures. The problems are stale generated artifacts and duplicate/dead surfaces: the delivered repomix pack is the 2026-09-27 build and the packed-only claim in gate note P8-G01 is false at the current package; falcon `FINAL_RESPONSE.json` is stale, mis-bound, and hardcoded (generator :65-66) and sits beside a stale progress ledger/program closeout; edge `FINAL_RESPONSE.json`/`PROGRAM_CLOSEOUT.md` lag the ledger; the audit run folder makes falcon's mandated `ci/validate.py` fail (CI-P2-001, reproduced); dead/competing files remain (falcon-firstboot.sh, mct/), and one uncommitted evidence edit fails the manifest check. No P0/P1 hygiene issue was found; material risks are P2 (stale delivered artifacts, CI breakage) and P3 (cleanup).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| falcon tree | 4,165 tracked files | repo | review-package 2,067 / evidence 934 / mct 856 | Medium | mct is an import |
| falcon pack | `/home/user/falcon-repomix.md` (Sep 27) | packed-only review | stale vs 2,067-entry package | High | verify INCOMPLETE |
| falcon digest | `PACKAGE_DIGEST.txt` | status/binding | current/derived; N/A omitted | Low | :14 |
| falcon response | `closeout/FINAL_RESPONSE.json` | closeout | `12aa2fd`; verdict IE; `open_gates=[]` | Medium | generator hardcoded |
| falcon records | `evidence_index.csv`, `progress_ledger.md`, `risk_register.md` | derived/records | host paths; PASS 62; R-29 OPEN | Medium | stale |
| falcon audit run | `docs/audits/repo-deep-dive/20260930-0701-…/` | this run | 36 files, 624K, untracked | Medium | breaks validate.py |
| falcon ownership/caches | `review-package/` (root), `PACKAGE_MANIFEST.sha256` (root), `.ruff_cache/` | build state | root-owned; ignored cache | Low | friction |
| edge tree | 914 tracked files | repo | evidence 643 / docs 61 / tests 38 | Low | clean, small |
| edge responses/dead files | `closeout/FINAL_RESPONSE.json`, `PROGRAM_CLOSEOUT.md`; `falcon-firstboot.sh`; secrets `control.db` | closeout/image | `d6147ef`; "120 tests"; unreferenced script; 0-byte root stray | Medium | stale/cleanup |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Folder/file naming | 4 | root layouts; `bootstrap/` numeric prefixes | duplicate prefixes (60/95/96); edge README lists missing `bootstrap/` | annotate/fix README |
| Duplicate/dead code | 3 | `falcon-firstboot.sh`; `mct/`; duplicate md basenames | dead script + competing doc set | remove/deprecate; banner |
| Generated/build artifacts | 2 | pack; FINAL_RESPONSE ×2; progress ledger | no regeneration enforcement | wire checks |
| Imports and circular deps | 4 | edge layering `cli→control/agent→common`; tests pass | no import lint | optional |
| Large files/components | 4 | sbom/vuln JSON ~1 MB; edge <300 KB; rules 44 MB gitignored | big JSON in git | optional artifact store |
| Type safety/any usage | 3 | edge 196/272 annotated; falcon 11 typed defs; no mypy | no type gate | add checker (edge) |
| Error handling | 4 | `set -euo` sampled; 7 `except Exception` (edge) | broad excepts | narrow |
| TODO/FIXME | 5 | 0 in sampled dirs | — | keep |
| Logging consistency | 3 | edge logging module (20 sites incl. print); falcon echo | two styles | optional standard |
| Config sprawl | 3 | falcon `config/` 13 subdirs + 3 compose projects | discovery cost | index |
| Competing patterns | 2 | mct vs falcon docs; mon/falcon naming | two status worlds | banners/state page |
| Package scripts | 2 | falcon shell entry points; edge `bin/falcon`; no pyproject | no standard task entry | task runner/docs |

## Detailed Review

### Item: Generated artifact chain (pack, digest, response, manifests, indexes)
- Evidence: digest bound `3ac6cd4` (2,067 entries); `PACKAGE_MANIFEST.sha256` identical to `review-package/MANIFEST.sha256`; `/home/user/falcon-repomix.md` Sep 27; `FINAL_RESPONSE.json` hardcoded verdicts; `evidence_index.csv` 264 host paths; `progress_ledger.md:17-18`. Controls: `verify_publication_chain.sh` binds package/evidence digests; the pack and FINAL_RESPONSE are outside mandatory checks. Gap: no pack-age check, no derived verdicts; risk: reviewers receive stale material while the chain reports green.

### Item: Duplicate/dead files
- Evidence: `image/overlay/usr/local/sbin/falcon-firstboot.sh` unreferenced (only `image/overlay/etc/falcon-agent/README:3`, wrong 0600 claim vs deployed 0640); `mct/README.md:3,37` (foreign badge `github.com/MaineCyberTech/soc`, `/opt/mct-security-stack`); duplicate basenames across `mct/`/`docs/`; `FINAL_RESPONSE_SUPERSEDING_2026-09-23.json`; duplicate EX-01/EX-14/EX-19 rows (`exception_register.md:9,23,27,28,30,42`). Impact: wrong artifact edited/trusted.

### Item: Code health and layout sample
- Evidence: falcon 88 shell scripts + 761 lines validation Python; edge 272 functions/196 annotated, 7 broad excepts, 163 tests. No tracked edge file >300 KB; largest falcon files are sbom/vuln JSON. Assessment: no cycles observed, no TODO debt; type checking and a task runner are the maturity gaps.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| HYGIENE-001 | Folder/file naming | root layouts; bootstrap prefixes | convention documented | duplicate prefixes; edge README `bootstrap/` | P3 | annotate/fix |
| HYGIENE-002 | Duplicate/dead code | falcon-firstboot; mct; response copies | none | dead + competing docs | P3 | remove/deprecate |
| HYGIENE-003 | Generated/build artifacts | pack; FINAL_RESPONSE; digest | manifest checks | stale pack/responses | P2 | enforce regeneration |
| HYGIENE-004 | Imports and circular deps | edge layering; tests | CI tests | no import lint | P3 | optional |
| HYGIENE-005 | Large files/components | sbom JSON; rules gitignored | gitignore | big JSON in git | P3 | optional artifact store |
| HYGIENE-006 | Type safety | 196/272 annotated edge; no mypy | none | no type gate | P3 | add checker |
| HYGIENE-007 | Error handling | `set -euo`; 7 broad excepts | test suite | broad excepts | P3 | narrow |
| HYGIENE-008 | TODO/FIXME | 0 found | discipline | — | P3 | keep |
| HYGIENE-009 | Logging consistency | logging vs echo | per-repo | two styles | P3 | optional |
| HYGIENE-010 | Config sprawl | config/ 13 subdirs; deploy/ | documented | discovery cost | P3 | index |
| HYGIENE-011 | Competing patterns | mct/falcon docs; mon naming | none | two status worlds | P2 | banners/state page |
| HYGIENE-012 | Package scripts | no make/pyproject | documented flows | no task runner | P3 | task runner |

## Findings

### Finding ID: HYGIENE-P2-001 - The audit run folder makes falcon's mandated `ci/validate.py` fail; run-folder lifecycle is undefined

- Severity: P2 · Confidence: High · Area: HYGIENE (falcon-build)
- Evidence: `python3 ci/validate.py` reproduced — parse/pins/ledger/evidence PASS, secret scan FAIL, `validation_failures=1`; 2 `long_hex` hits at `docs/audits/…/01_repository_inventory.md:6` and `02_architecture_runtime_topology.md:6`; `secret_scan.py` long_hex rule; `AGENTS.md:18-19` ("must pass before committing"); `docs/audits/…` untracked (36 files/624K), not gitignored; edge mirror directory exists but is empty
- What is happening: required audit output is scanned as untrusted content; committing it reddens the pre-commit gate with no security defect, and no decision records whether run folders are committed or archived.
- Why it matters: AGENTS rule 5 becomes unhonorable; teams learn to bypass validation; false positives mask real findings.
- User / business impact: friction on every audit commit; CI red herrings.
- Security / privacy / reliability impact: gate erosion; scanner otherwise unchanged.
- Recommended fix: allowlist `docs/audits/**` (or benign 40-hex revision IDs) in the scanner with a planted-secret test; decide commit-vs-archive; populate/document the edge mirror.
- Suggested validation: `ci/validate.py` green with run folder present; synthetic secret under `docs/audits/` still fails; next run's folder provably committed/ignored/archived.
- Owner suggestion: falcon maintainer + audit operator · Effort estimate: S · Dependencies: CI-P2-001 (hygiene-side confirmation)
- Status: still-open (prior ND-P3-006 caveat; sibling CI-P2-001)

### Finding ID: HYGIENE-P2-002 - Stale pack and false/historical verification claims (P8-G01, P1-G06, phase9 aggregate)

- Severity: P2 · Confidence: High · Area: HYGIENE (falcon-build)
- Evidence: `/home/user/falcon-repomix.md` dated 2026-09-27; `verify_pack.py` → 1,118 parsed, 1,056 verified, **37 mismatched, 957 missing**, `INCOMPLETE` (prior run 23/933 — widened); `gate_ledger.csv:94` P8-G01 "991/991 … verify_pack.py (PASS)"; `gate_ledger.csv:17` P1-G06 "history_scan_exit=0, NO_FINDINGS" (current exit 1, 22 findings, `REVIEW_REQUIRED`); `docs/security/SCANNER_ALLOWLIST_CHANGES.md:41` records 16; `PACKAGE_DIGEST.txt:14` phase9 aggregate omits the NOT_APPLICABLE row (13 PASS/14 rows)
- What is happening: publication binds a fresh package but never regenerates/verifies the repomix pack; gate notes and the aggregate carry historical counts.
- Why it matters: the packed-only reviewer path cannot reproduce the delivered package; counts are quoted into reviews/risk decisions.
- User / business impact: external reviewer trust; wrong totals in statements.
- Security / privacy / reliability impact: verification gap and weakened evidence claims.
- Recommended fix: re-run `make-repomix.sh`; add a pack check/age gate to `verify_publication_chain.sh`; append dated corrections to P8-G01/P1-G06; include NOT_APPLICABLE in the aggregate.
- Suggested validation: `verify_pack` = PASS for the current commit; publication fails when the pack predates the package commit; aggregate parser asserts every ledger row appears in exactly one bucket.
- Owner suggestion: falcon maintainer · Effort estimate: S/M · Dependencies: none
- Status: still-open, worsened (prior ND-P2-001; ND-P2-003, ND-P3-004)

### Finding ID: HYGIENE-P2-003 - Falcon closeout/status artifacts are stale, hardcoded, and contradictory

- Severity: P2 · Confidence: High · Area: HYGIENE (falcon-build)
- Evidence: `closeout/FINAL_RESPONSE.json:7` commit `12aa2fd…` vs HEAD `8282d3f`; `verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`, `open_gates=[]`; `:60` "Git-history scan 16 findings"; `generate_final_response.py:65-66` hardcodes the verdict strings; `ledgers/progress_ledger.md:17-18` "PASS 62 … Final verdict: `INSUFFICIENT_EVIDENCE`", phase 8 "BLOCKED" (current 101 PASS/1 N/A, APPROVED); `closeout/PROGRAM_CLOSEOUT.md:19-25,44-49` totals 62/10/30 + verdict IE with last amendments 2026-09-23; `risk_register.md:38` R-29 "OPEN (repair verification pending)" while R-30 is CLOSED
- What is happening: the generator derives counts/commit but hardcodes the verdict block; append-only records were not amended after Phase 9 and remain quotable as current.
- Why it matters: automation/newcomers reading closeout-first get a pre-Phase-9 verdict opposite to the approved state.
- User / business impact: false status; review/release confusion; duplicated planning.
- Security / privacy / reliability impact: unverified claims propagate.
- Recommended fix: derive verdict/readiness from the phase-9 ledger + verdict; refresh the history-scan sentence; append a progress row (101 PASS/1 N/A + verdict pointer) and a "superseded by Phase 9 (2026-09-29)" banner; close/annotate R-29.
- Suggested validation: regenerated fields equal ledger/digest; no current-tense verdict text contradicts `PRODUCTION_VERDICT.md`; risk rows have a current status.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: none
- Status: still-open (prior ND-P2-002; REV-P3-002 items)

### Finding ID: HYGIENE-P2-004 - Edge summary artifacts lag the ledger and the current image

- Severity: P2 · Confidence: High · Area: HYGIENE (falcon-edge-build)
- Evidence: `closeout/FINAL_RESPONSE.json:7-8` commit `d6147ef…`, note "phases 5-6 in progress" (HEAD `f1c5def`; phases 0-10 implementer-side complete per `README.md:22`); `closeout/PROGRAM_CLOSEOUT.md:14` "green (120 tests)" vs 163; `docs/phase6/CLOSEOUT.md:42-43` "4 PASS / 3 BLOCKED … hardware absent" vs ledger 6 PASS/2 BLOCKED (P6-G05 PASS 2026-09-30); `gate_ledger.csv:86` P10-G05 "lab6 image digest embedded" while `README.md:31` ships lab8 and P4-G01 note says lab7
- What is happening: append-only amendments below stale headers; the generated response was not refreshed.
- Why it matters: quoted counts/image names are wrong; reflash/review planning is misled.
- User / business impact: wrong planning; review errors.
- Security / privacy / reliability impact: none direct.
- Recommended fix: regenerate the response; append correction rows for closeout/phase-6 counts; refresh the P10-G05 note by amendment.
- Suggested validation: response commit == last ledger change; counts match ledger and test run.
- Owner suggestion: edge maintainer · Effort estimate: S · Dependencies: in-flight CI round committed
- Status: still-open (prior ND-P2-013)

### Finding ID: HYGIENE-P3-001 - Uncommitted in-place evidence edit fails the evidence manifest check

- Severity: P3 · Confidence: High · Area: HYGIENE (falcon-build)
- Evidence: `git status` shows `M evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out` (+20 lines) and a new untracked `.meta.json`; `bash automation/evidence/manifest.sh check` → that file `FAILED`, exit 1; doctrine: evidence is never edited after capture (AGENTS hard rules 2/3)
- What is happening: a parallel session is mid-flow modifying an evidence file in place; at the audited working tree the manifest is inconsistent (possibly an intentional redaction/annotation in progress).
- Why it matters: if committed as-is, the manifest check fails and append-only doctrine is breached.
- User / business impact: audit-trail integrity question.
- Security / privacy / reliability impact: an in-place edit could mask a capture.
- Recommended fix: complete the flow (record original SHA-256 in `ledgers/redactions.md` if a redaction; add meta entry; regenerate `evidence/MANIFEST.sha256`) or revert; re-run `manifest.sh check`.
- Suggested validation: `manifest.sh check` exit 0 at commit time.
- Owner suggestion: owning session / falcon maintainer · Effort estimate: S · Dependencies: parallel session completion
- Status: open (working-tree observation)

### Finding ID: HYGIENE-P3-002 - Dead/duplicate files, rows, and root-owned/cache surfaces that mislead

- Severity: P3 · Confidence: High · Area: HYGIENE (both repos)
- Evidence: `falcon-edge-build/image/overlay/usr/local/sbin/falcon-firstboot.sh` unreferenced (only `image/overlay/etc/falcon-agent/README:3`, claim 0600 vs deployed 0640); `falcon-build/mct/` 856 tracked files with own README/AGENTS/ARCHITECTURE and foreign badge (`mct/README.md:3`) + `/opt/mct-security-stack` paths (`:37`); `closeout/FINAL_RESPONSE_SUPERSEDING_2026-09-23.json` vs current response; duplicate EX-01/EX-14/EX-19 rows (`exception_register.md:9,23,27,28,30,42`); edge secrets `control.db` 0-byte root-owned; falcon `review-package/` (17 top-level entries) and `PACKAGE_MANIFEST.sha256` `root:root`; `.ruff_cache/` at both repo roots, edge `image/out/0.1.0/` and `automation/validation/__pycache__/` (ignored)
- What is happening: historical/current artifacts coexist without "superseded"/"imported" markers; `sudo` builds leave root-owned outputs and caches accumulate at roots.
- Why it matters: newcomers patch/trust the wrong file; local rebuilds as `user` cannot overwrite root-owned outputs cleanly; register reconciliation cost.
- User / business impact: time loss; wrong edits; permission errors mistaken for tool failures.
- Security / privacy / reliability impact: low; privileged writes into a user-writable tree.
- Recommended fix: delete/`DEPRECATED`-header the first-boot script + fix the overlay README; add an import banner to `mct/README.md`; signpost the superseding response; add a latest-row summary to the exception register; chown build outputs (or build in temp); move caches to `$TMPDIR`; remove the stray DB file (owner).
- Suggested validation: `grep -r falcon-firstboot` shows only a deprecation header; `find . -user root` empty after rebuild; register summary has one current row per ID; repo roots cache-free after a clean run.
- Owner suggestion: both maintainers · Effort estimate: S/M · Dependencies: none
- Status: still-open (prior ND-P3-005/008/010; related INTG-P2-003, REV-P3-012)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale pack ships with a "PASS" claim | P2 | High | reviewer cannot reproduce | verify_pack INCOMPLETE; gate note 991/991 | HYGIENE-P2-002 |
| Run folder reddens mandated CI | P2 | High | gate-bypass habit | `ci/validate.py` exit 1 | HYGIENE-P2-001 |
| Hardcoded/stale closeout verdicts propagate | P2 | Medium | false status | generator:65-66; progress ledger | HYGIENE-P2-003 |
| Edge quotes stale counts/images | P2 | Medium | wrong reflash/planning | FINAL_RESPONSE; P10-G05 lab6 | HYGIENE-P2-004 |
| In-place evidence edit breaks manifest | P3 | Certain now | integrity check red | `manifest.sh check` exit 1 | HYGIENE-P3-001 |

## Recommendations

### Immediate / Release Blocking
- Fix the scanner allowlist so committed audit artifacts pass `ci/validate.py` (HYGIENE-P2-001).
- Resolve the in-flight evidence edit and re-run `manifest.sh check` (HYGIENE-P3-001).

### This Week
- Regenerate the repomix pack; add pack verification and N/A-safe aggregates (HYGIENE-P2-002).
- Make closeout responses derived on both programs and regenerate; append progress/closeout/risk corrections (HYGIENE-P2-003/004).

### This Month
- Dead/duplicate cleanup and surface hygiene: falcon-firstboot, mct banner, register summary, ownership, caches (HYGIENE-P3-002).

### Later / Platform Evolution
- Add type checking (edge first), an optional import lint, a task runner; consider artifact storage for large SBOM/vuln JSON.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Allowlist `docs/audits/**` 40-hex IDs | unblocks mandated validation | `secret_scan.py`, `.gitleaks.toml` | `ci/validate.py` green |
| Re-run `make-repomix.sh` + verify_pack | restores packed-only path | `automation/validation/` | `pack_verification=PASS` |
| Derive FINAL_RESPONSE verdict fields | ends hardcoded false status | `generate_final_response.py` | fields equal ledgers |
| Include N/A in phase9 aggregate | correct denominators | `publish_digests.sh:34` | aggregate sums to 14 |
| Delete/deprecate falcon-firstboot.sh | removes image-work trap | `image/overlay/...` | no live references |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Pack regeneration + publication gate | P2 | falcon maintainer | S/M | none |
| Derived closeout artifacts (both repos) | P2 | both maintainers | S | none |
| Scanner allowlist + run-folder lifecycle | P2 | falcon maintainer | S | CI-P2-001 |
| Surface cleanup (dead files, ownership, caches, register) | P3 | both maintainers | S/M | none |
| Type checker (edge) + task runner | P3 | edge maintainer | M | none |

## Suggested Tests

- Unit: `verify_pack.py` fixture (stale pack → publication fails; fresh pack → PASS).
- Unit: `generate_final_response.py` fixture (ledger+verdict → matching fields; hardcoded values cannot reappear).
- CI: `ci/validate.py` passes with a run folder containing 40-hex SHAs; a planted secret in the same folder still fails; `manifest.sh check` runs locally before commit.
- Integration: aggregate test enforcing every gate-ledger row appears in exactly one published bucket (incl. N/A); edge doc-count analog (CLI/tests/image).

## Suggested Documentation Updates

- falcon: `REPOSITORY.md` (artifact ownership/regeneration), `AGENTS.md` (add pack + manifest checks), `PACK_VERIFICATION_NOTES.txt` (record result), `closeout/PROGRAM_CLOSEOUT.md` (superseded banner), `mct/README.md` (import banner), `SCANNER_ALLOWLIST_CHANGES.md` (counts).
- edge: `closeout/FINAL_RESPONSE.json`/`PROGRAM_CLOSEOUT.md` regeneration notes, `docs/phase{5,6}/CLOSEOUT.md` corrections, `README.md` cleanup (`bootstrap/`, `phase10/`), AGENTS cache/build-output locations.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Should audit run folders be committed (with scanner allowlist) or archived outside the repos? | determines CI/mirror behavior | operator/maintainer decision |
| Is the repomix pack still a supported review path or superseded? | fix vs retire | owner/maintainer decision |
| Who owns the in-flight REVIEW-FIX evidence edit? | manifest integrity/append-only compliance | session/owner statement |
| Is `mct/` a frozen import or maintained code? | cleanup scope | owner decision |
| Which image is "current" (README lab8 vs ledger lab6/lab7 references)? | reflash/release coherence | edge maintainer statement |

## Appendix A — Prior-run (20260930-0320) hygiene status at current commits

- **verified-fixed:** ND-P1-001 (digest derived; residual N/A omission = HYGIENE-P2-002); ND-P3-006 (falcon `validate.yml` exists; caveat CI-P2-001 = HYGIENE-P2-001).
- **still-open / worsened:** ND-P2-001 (verify_pack 37 mismatched/957 missing) → HYGIENE-P2-002; ND-P2-002 (generator:65-66) → HYGIENE-P2-003; ND-P2-003 (exit 1, 22 findings) → HYGIENE-P2-002; ND-P2-011 (264/461 host paths) → DOC-P2-002; ND-P2-013 (FINAL_RESPONSE `d6147ef`; phase6 counts) → HYGIENE-P2-004; ND-P3-001..003 (refs/drafts) → DOC-P2-002; ND-P3-004 (digest:14; P8-G01 991/991) → HYGIENE-P2-002; ND-P3-005 (EX-01/14/19 duplicates) → HYGIENE-P3-002; ND-P3-008 (dead firstboot) → HYGIENE-P3-002; ND-P3-009 → DOC-P2-003; ND-P3-010 (0-byte `control.db`; tokens ACM-P2-001) → HYGIENE-P3-002; REV-P3-002 (progress ledger:17-18; risk_register:38) → HYGIENE-P2-003.

## Appendix B — Maintainability metrics sampled at the audited commits

- falcon-build: 4,165 tracked files (review-package 2,067; evidence 934; mct 856; automation 101; docs 77; config 40; sbom 26; bootstrap 24; ledgers 11); 88 shell scripts; no pyproject/requirements; 0 TODO/FIXME in sampled dirs; `config/suricata/rules` 44 MB gitignored.
- falcon-edge-build: 914 tracked files (evidence 643; docs 61; tests 38; automation 33; api 33; src 23); 163 tests; 272 functions/196 annotated; 7 `except Exception`; 0 TODO/FIXME; largest tracked file < 300 KB.
- Read-only executions: `verify_pack` INCOMPLETE; `manifest.sh check` exit 1; `verify_publication_chain.sh` 0 failures; edge `validate.sh` ALL PASS. Only this run folder was written by the audit.
