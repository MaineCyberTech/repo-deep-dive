# Evidence, Doctrine, and Gate Integrity Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab, full-hardening) · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: central `/home/user/falcon-build`; edge `/home/user/falcon-edge-build`; delivery `/home/user/falcon-edge-delivery`
- Commit SHA: central recorded `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (delivered package `3ac6cd46…`); edge recorded `45dfed0`, moved `→ f1c5defe…` mid-run. Claims are bound to recorded states.
- Generated at: 2026-09-30T15:20Z · Auditor: audit subagent (prompt 41), read-only · Area code: EVID
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/41_evidence_doctrine_gate_integrity_audit.md`
- Scope limitations: live host read-only; no archival/verify-delivery scripts that write; secrets by path/type only; the parallel-session evidence edit was observed, not reproduced.

## Scope

Reviewed: doctrine docs (AGENTS.md, REPOSITORY.md, README.md) both repos; all central ledgers; program + phase-9 gate ledgers; evidence indexes/manifests; `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `PACK_*` files; review/adoption/verdict records; publication scripts; delivery archives; edge ledgers/closeout. Not reviewed: source correctness, live service state, edge hardware, data quality (other prompts).

## Evidence Reviewed

- `AGENTS.md`, `REPOSITORY.md`, `README.md` (central) and edge equivalents; `ledgers/` (gate, phase-9, decision, evidence index, risk, contradiction, exception, redactions, progress, test) both repos.
- `PACKAGE_DIGEST.txt`; `review-package/MANIFEST.sha256`; `evidence/MANIFEST.sha256`; `PACKAGE_MANIFEST.sha256`; `PACK_VERIFICATION_NOTES.txt`; `PACK_NOT_INCLUDED.txt`.
- `docs/phase9/review/{PRODUCTION_VERDICT.md,OWNER_ADOPTION.md,REVIEW_REPORT_2026-09-29.md}`; `docs/phase8/REVIEW_RECORD.md`; `docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md`.
- `automation/validation/{publish_digests.sh,verify_publication_chain.sh,build_review_package.sh,secret_scan.py}`; `closeout/generate_final_response.py`.
- Edge `closeout/FINAL_RESPONSE.json` + `closeout/REVIEW-2026-09-30.md`; archives `/home/user/falcon-review-delivery-2026-09-29*.tar.gz`, `-2026-09-30.tar.gz`; edge release manifest + sidecar.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sha256sum -c review-package/MANIFEST.sha256` | checksum | package integrity | exit 0, **2067/2067 OK** |
| `sha256sum -c evidence/MANIFEST.sha256` | checksum | evidence integrity | exit 1: 932/933; `evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out` changed in worktree (M) |
| `sha256sum -c PACKAGE_MANIFEST.sha256` | checksum | root pack manifest | 2060/2067; 4 mismatch + 3 package-only files absent |
| `verify_publication_chain.sh` | script | publication chain | 0 failures; signed archives `fc8b9007…`/`ef6e9a10…` intact |
| Manifest recomputation at `c312ab7` vs `3ac6cd4` | git | verdict binding | verdict binds 1,168-entry `4476fc93…` + 918-entry `adacd9a1…`; delivered 2,067-entry `0e591249…` + 933-entry `2a7f4f7b…` |
| Package-vs-source `git archive 3ac6cd4` compare | diff | delivery binding | 2060/2067 identical; 7 differences (2 stale closeout JSONs, package README, 4 package-generated) |
| Gate aggregate recompute | csv | gate integrity | main 101 PASS/0/0/1; phase 9 13 PASS/1 N/A; edge 77 PASS/8 BLOCKED/3 IE |
| Test-ledger scan | csv | PASS discipline | 0 PASS rows with non-zero exit (central 461, edge 313) |
| Decision-log monotonicity | script | append-only | 136 rows, 4 out-of-order transitions |
| Evidence-index resolution | script | reviewer usability | 461/461 resolve in worktree (264 via stale `../monitoring-build/`); 264 don't resolve in package as written, package copies exist and hash-match 264/264 |
| Secret scan of `ossec.conf` | script | redaction | repo scanner: `NO_FINDINGS` despite literal key material (API-P0-001) |

## Executive Summary

The evidence estate is strong in mechanics: manifests are internally consistent, the publication-chain verifier passes at the declared commit, signed archives are byte-preserved, failures are retained in test ledgers, and the edge review is substantive. Integrity failures concentrate at the **approval boundary**: verdict, review and adoption bind `c312ab7` and its 1,168/918-entry package, while the delivery is `3ac6cd4` with 2,067/933; gates were flipped in the same commit that published the "signed" records; the reviewer disposition is a transcription and the named reviewer is recorded elsewhere as the installer; the shipped package contains a closeout JSON older than its own commit; doctrine docs and the progress ledger still describe the pre-closure state; and secrets ship in delivered artifacts. Treat the binding and independence issues as release-blocking.

## Inventory

| Item | Path / symbol | Purpose | State | Risk |
|---|---|---|---|---|
| Program gate ledger | `ledgers/gate_ledger.csv` | 102 gates | 101 PASS / 1 N/A | Low |
| Phase-9 gate ledger | `ledgers/phase9_gate_ledger.csv` | 14 gates | 13 PASS / 1 N/A | Medium |
| Verdict / review / adoption | `docs/phase9/review/` | approval chain | binds `c312ab7`; transcription | High |
| Package manifests | `review-package/`, `evidence/` MANIFEST | integrity | 2067/2067, 932/933 | Medium |
| Pack manifest | `PACKAGE_MANIFEST.sha256` | pack integrity | duplicate; fails tree check | Medium |
| Closeout JSON | `closeout/FINAL_RESPONSE.json` | machine verdict | verdict IE, commit `12aa2fd` | High |
| Progress ledger | `ledgers/progress_ledger.md` | phase summary | mtime 2026-09-21 | Medium |
| Contradiction ledger | `ledgers/contradiction_ledger.md` | contradictions | last substantive 2026-09-23 | Medium |
| Redactions | `ledgers/redactions.md` | redaction record | no wazuh key entries | High |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Doctrine documents and binding rules | 2 | strict rules defined | AGENTS/README state stale | refresh |
| Ledger structure and append-only discipline | 3 | stable schemas, failures kept | ordering violations; in-place edit | add checks |
| Claim-to-evidence-to-ledger chain | 2 | refs resolve | self-referential/transcribed approvals | external artifacts |
| Digest/checksum verification | 3 | package/chain verify | root manifest, pin fail | fix packaging + pin check |
| Gate definitions and pass criteria | 3 | charter PASS rule | no per-gate criteria | criteria column |
| Independent review records | 1 | report exists | transcription; installer conflict | reviewer artifact |
| Owner adoption records | 2 | record exists | implementer-prepared | person-level artifact |
| Contradiction handling | 2 | 31 entries | no closure-era entries | log closures |
| Exception handling | 2 | 23 accepted rows | EX-04/07/08/09/10 unresolved | reconcile |
| Delivery/publication integrity | 2 | chain verifier passes | verdict misbound; stale in-package closeout | rebind/rebuild |
| Redaction consistency | 1 | redaction process exists | secrets present; scanner blind | fix/rotate |

## Detailed Review

### Item: Claim chain, independence and redaction boundary

- Evidence: `PRODUCTION_VERDICT.md` lines 8–20; `PACKAGE_DIGEST.txt`; `git show 6f3c2e4`; review report line 3 ("Transcribed…"); `decision_log.md` (installer JPB); `automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf` (sha256 `7a6eb61c…`, identical in `review-package/` and the 2026-09-30 archive); `secret_scan.py`.
- Behavior: APPROVED with digests copied at closure; all gates closed in `6f3c2e4`; the implementer commits the transcription and adoption; the scanner cannot see `<key>`/`<api_key>` XML values and no redaction entry exists.
- Missing controls: verdict↔delivery equality check; reviewer/approver-produced artifacts and role conflict checks; tag-aware secret scanning. Fixes: machine-check the binding; separate gate-flip commits from approvals; fix scanner, redact, rotate. Cross-ref INV-P0-002 and API-P0-001.

## Claim-to-Evidence Sample Table

| Claim | Artifact | Reproduction result | Verdict | Notes |
|---|---|---|---|---|
| `gate_aggregate=101 PASS/0/0/1` | `ledgers/gate_ledger.csv` | recomputed exactly | supported | — |
| `review_package_entries=2067` / `0e591249…` | `review-package/MANIFEST.sha256` | 2067/2067 OK; hash matches | supported | — |
| `program_verdict=APPROVED` | `PACKAGE_DIGEST.txt` → verdict doc | verdict binds `c312ab7`/1,168; digest `3ac6cd4`/2,067; verdict prose says NOT_SUPPORTED | unsupported | INV-P0-002 |
| `P8-G10 PASS` | phase ledger + verdict | flipped with verdict text in `6f3c2e4` | partially supported | same-commit justification |
| `P9-G10 PASS` (manifests reproduce) | review report | verified 1,168+918 at `c312ab7`, not delivered | partially supported | superseded package |
| `P9-G11 PASS` (independent reviewer) | review report | transcription; JPB recorded as installer | unsupported | JPB question |
| `human_review=completed 2026-09-22` | review record | record: "separate AI agent… NOT an independent human reviewer" | unsupported | mislabel |
| `phase9_gate_aggregate=13 PASS/…/0 NOT_RUN` | `PACKAGE_DIGEST.txt` | ledger has 1 NOT_APPLICABLE omitted | partially supported | aggregate incomplete |
| `P9-G06 PASS` (production-scale restore) | `evidence/raw/P9-G06/20260923T061644Z…` | one index 720,474 docs, 7 s, scratch name | partially supported | lab-scale |
| Edge `P10-G05 PASS` (manifest/SBOM) | edge manifest | 42/42 artifact hashes re-verified | supported | signature verified by edge review |
| Edge `P4-G02 PASS` (owner flash + first boot) | `E-P4-G02-030/031`, `E-EDGE-ONBOARD-06x` | lab-side captures; no owner artifact | partially supported | REV-P2-005 |

## Gate Integrity Table

| Gate | Criteria | Evidence | Recorded | Supported? | Notes |
|---|---|---|---|---|---|
| P8-G10 | controlled verdict published | `PRODUCTION_VERDICT.md` | PASS | Partial | superseded binding |
| P9-G02 | hosts hardened, independently inventoried | review report | PASS | Partial | inventory of `c312ab7`; transcription |
| P9-G06 | production-scale restore RPO/RTO | restore capture | PASS | Partial | single index |
| P9-G10 | archive/manifests reproduce | review report | PASS | Partial | old package |
| P9-G11 | independent human reviewer | review report | PASS | No | transcription; installer |
| P9-G12 | owner adoption + authorization | adoption record | PASS | Partial | identity only "MCT Board" |
| P9-G13 | cutover/rollback observed | EX-23 | N/A | Yes | no-change promotion |
| P9-G14 | verdict published, P8-G10 reconciled | verdict | PASS | Partial | binding defect |
| Edge P10-G03/P10-G08 | review remediation/closure | edge review | PASS | Yes | conditions tracked |
| Edge P4-G02 | owner flash + first boot | lab captures | PASS | Partial | no owner artifact |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EVID-001 | Doctrine documents and binding | AGENTS/README vs ledger | doctrine exists | stale gate/verdict text | P1 | refresh |
| EVID-002 | Append-only discipline | decision log; evidence edit | conventions | ordering; in-place edit | P3 | ordering check; new captures |
| EVID-003 | Claim→evidence→ledger chain | closure gates | evidence refs resolve | self-justifying flips | P0 | external artifacts |
| EVID-004 | Digest/checksum verification | manifests, pin | chain verifier | root manifest; pin | P2 | canonical manifest |
| EVID-005 | Gate definitions and criteria | phase-9 charter | PASS rule | no per-gate criteria | P3 | criteria column |
| EVID-006 | Independent review records | review report | digest-bound file | provenance absent | P0 | reviewer artifact |
| EVID-007 | Owner adoption records | adoption file | digest-bound | person-level identity | P2 | signed artifact |
| EVID-008 | Contradiction handling | contradiction ledger | register | no closure entries | P2 | log closures |
| EVID-009 | Exception handling | exception register | acceptance flow | unresolved exceptions | P2 | reconcile |
| EVID-010 | Delivery/publication integrity | package vs source | chain verifier | stale in-package closeout | P1 | rebuild/rebind |

## Findings

### Finding ID: EVID-P0-001 - Approval chain binds a superseded package; signatures published with the gate flips

- Severity: P0 · Confidence: High · Area: EVID (cross-ref INV-P0-002)
- Evidence: `PRODUCTION_VERDICT.md` binds `c312ab7` + package `4476fc93…` (1,168) + evidence `adacd9a1…` (918); `PACKAGE_DIGEST.txt` binds `3ac6cd4` + `0e591249…` (2,067) + `2a7f4f7b…` (933); `git show 6f3c2e4` flips P8-G10/P9 gates to PASS and publishes the "signed" review/adoption/verdict text (prior commits are drafts "pending signatures").
- What is happening: the release approval is bound to a package generation that is not the delivery; gate flips and justifications share one commit.
- Why it matters: the APPROVED verdict cannot be reproduced against the shipped artifact set.
- User / business impact: release gate unearned for the delivered package.
- Security / privacy / reliability impact: governance control failure.
- Recommended fix: re-review/rebind over the exact delivered commit (or rebuild an immutable package from `c312ab7`); never combine gate flips with approval publication.
- Suggested validation: CI equality check between verdict digests and `PACKAGE_DIGEST.txt`.
- Owner suggestion: owner + release engineer · Effort: M · Dependencies: INV-P0-002 · Status: still-open

### Finding ID: EVID-P0-002 - Reviewer disposition is a transcription and the named reviewer is recorded as the system installer

- Severity: P0 · Confidence: High · Area: EVID (JPB question; cross-ref REV-P1-002)
- Evidence: `REVIEW_REPORT_2026-09-29.md` line 3 ("Transcribed…; sign-off relayed by the owner"); `ledgers/decision_log.md` 2026-09-23T06:35Z and 2026-09-24T18:49Z name "installer JPB" while line 139 asserts independence "did not implement the system"; all commits by `build-agent`.
- What is happening: the charter's independent-review requirement is evidenced by an implementer transcription of a verbal disposition; the reviewer is elsewhere recorded as installer.
- Why it matters: the charter cannot be satisfied by transcription; the independence basis is contradicted by the repo.
- Business impact: production approval lacks a verifiable independent basis.
- Reliability impact: release-blocking assurance failure.
- Recommended fix: obtain a reviewer-produced signed disposition declaring the true role; if JPB installed the SPAN, use a different reviewer; record any transcript path.
- Suggested validation: review-record provenance test (author ≠ implementer; external artifact reference).
- Owner suggestion: owner · Effort: M · Dependencies: none · Status: still-open

### Finding ID: EVID-P1-001 - The delivered package ships closeout records that do not match the delivery commit

- Severity: P1 · Confidence: High · Area: EVID
- Evidence: `git archive 3ac6cd4` compare: `review-package/closeout/FINAL_RESPONSE.json` generated at `b8542bf5…` vs source tree at the same commit `12aa2fdb…`; same for the superseding file; `PACKAGE_MANIFEST.sha256` records `7b7cd8c4…` while the tree file hashes `b9b779f1…`; 2060/2067 files otherwise identical.
- What is happening: `build_review_package.sh` copies the worktree; closeout JSON was regenerated after the copy, leaving the shipped copy stale.
- Why it matters: "delivery matches what was verified" is violated for the machine-readable verdict.
- Business impact: contradictory final responses depending on artifact.
- Recommended fix: atomic build after all generation, or exclude closeout from the package and publish it separately with its own digest.
- Suggested validation: package-vs-tree diff gate in the release script.
- Owner suggestion: release engineer · Effort: S · Dependencies: `build_review_package.sh` · Status: open

### Finding ID: EVID-P1-002 - FINAL_RESPONSE.json contradicts PACKAGE_DIGEST.txt at HEAD; verdict fields hardcoded

- Severity: P1 · Confidence: High · Area: EVID (cross-ref INV-P0-002; prior REV-P1-006/ND-P2-002)
- Evidence: `closeout/FINAL_RESPONSE.json` at HEAD: `commit=12aa2fd`, `verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`; `PACKAGE_DIGEST.txt`: `program_verdict=APPROVED`, `production_readiness=APPROVED`; `generate_final_response.py` hardcodes verdict/readiness; `publish_digests.sh` derives APPROVED from file existence + empty IE/BLOCKED counts.
- What is happening: two shipped machine-readable artifacts assert opposite verdicts; neither reads a single source of truth.
- Why it matters: consumers and automation cannot determine the governing verdict.
- Recommended fix: derive both from the controlled verdict text; fail closed on any non-APPROVED content.
- Suggested validation: consistency test asserting digest and final response agree at HEAD.
- Owner suggestion: release engineer · Effort: S · Dependencies: EVID-P0-001 · Status: still-open

### Finding ID: EVID-P1-003 - Doctrine docs and progress ledger describe the pre-closure state

- Severity: P1 · Confidence: High · Area: EVID
- Evidence: `AGENTS.md` lines 72–73 list open gates P8-G10, P9-G02/P9-G10, P9-G11/G12/G14 (all closed in the ledgers); `README.md` line 8: "Current state (2026-09-24) … 100 PASS / 0 BLOCKED / 1 INSUFFICIENT_EVIDENCE"; `ledgers/progress_ledger.md` (mtime 2026-09-21) totals 62 PASS / 10 BLOCKED / 30 IE; no contradiction entry.
- What is happening: the documents agents read first point at already-closed gates and a stale aggregate.
- Why it matters: agents act on wrong state; doctrine binding undermined.
- Recommended fix: refresh AGENTS.md/README; append a progress-ledger closure section or mark superseded; log reconciliation.
- Suggested validation: CI check that AGENTS open-gate list equals the ledger.
- Owner suggestion: maintainer · Effort: S · Dependencies: none · Status: open

### Finding ID: EVID-P1-004 - Secret literals ship in repo/package/delivery; scanner blind to XML-tag credentials; no redaction entry

- Severity: P1 · Confidence: High · Area: EVID (cross-ref API-P0-001; prior REV-P3-010)
- Evidence: `automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf` sha256 `7a6eb61c…` carries literal 32-char cluster key and `<api_key>` values (64/36-char); identical bytes in `review-package/` and `/home/user/falcon-review-delivery-2026-09-30.tar.gz`; `mct/config/wazuh_cluster/wazuh_manager.conf.canonical` also has a literal `<api_key>`; `secret_scan.py` matches only assignment forms → `NO_FINDINGS`; `redactions.md` has no entry.
- What is happening: credentials cross repo/package/delivery boundaries undetected and unrecorded.
- Why it matters: exposure persists in the instrument of record; rotation status unknown.
- Impact: credential compromise (values reported by path/type only).
- Recommended fix: remove values and load at deploy time; tag-aware scanner patterns; append redactions entry; rotate cluster/API keys.
- Suggested validation: scanner negatives for XML tags; grep shows values gone.
- Owner suggestion: security owner · Effort: S–M · Dependencies: API-P0-001 · Status: still-open

### Finding ID: EVID-P2-001 - Phase-9 aggregate omits the NOT_APPLICABLE gate

- Severity: P2 · Confidence: High · Area: EVID (prior REV-P3-003, unfixed)
- Evidence: `PACKAGE_DIGEST.txt` `phase9_gate_aggregate=13 PASS / 0 BLOCKED / 0 INSUFFICIENT_EVIDENCE / 0 NOT_RUN`; ledger contains P9-G13 = NOT_APPLICABLE (14 rows); `publish_digests.sh` prints only PASS/BLOCKED/IE/NOT_RUN.
- What is happening: the aggregate does not sum to the gate count.
- Why it matters: hidden statuses violate the aggregates rule (N/A must be stated).
- Recommended fix: include NOT_APPLICABLE. · Validation: aggregate sums to ledger rows. · Owner: release engineer · Effort: S · Dependencies: `publish_digests.sh` · Status: open

### Finding ID: EVID-P2-002 - `PACKAGE_MANIFEST.sha256` cannot verify the tree it appears to describe

- Severity: P2 · Confidence: High · Area: EVID
- Evidence: `cmp` shows it is byte-identical to `review-package/MANIFEST.sha256` (both `0e591249…`); run from repo root: 2060/2067 OK; mismatches `closeout/FINAL_RESPONSE*.json`, `README.md`, one evidence file; missing `OWNER_ACCEPTANCE.md`/`REVIEWER_CHECKLIST.md`/`vuln-summary.csv` (documented in `PACK_NOT_INCLUDED.txt`).
- What is happening: a package manifest is duplicated at repo root under a name that invites tree verification.
- Why it matters: verifiers get false failures or wrongly trust the duplicate.
- Recommended fix: keep the manifest only inside the package, or generate a true root pack manifest with documented exclusions.
- Validation: instructions verify successfully as written. · Owner: release engineer · Effort: S · Status: open

### Finding ID: EVID-P2-003 - Exception and contradiction registers are not reconciled with closure

- Severity: P2 · Confidence: High · Area: EVID (prior ND-P2-008/ND-P3-005, partial)
- Evidence: `OWNER_ADOPTION.md` accepts EX-01/02/03/11/12/13/14/15/16/18/20/21/22/23 while `exception_register.md` still shows PENDING_ACCEPTANCE for EX-04/07/08/09/10 (EX-19 row replaced); `PRODUCTION_VERDICT.md` cites "EX-07/EX-14 etc. as listed in the register" though no EX-07 acceptance row exists; contradiction ledger's last substantive entry is 2026-09-23 (C-12 updated) with C-04/05/06/08/11/22 still OPEN although later evidence supersedes them and no entry exists for the verdict/package, FINAL_RESPONSE or pin contradictions.
- What is happening: both registers stopped being maintained at closure.
- Why it matters: exception ownership/expiry is a gate condition and the contradiction ledger is the required reconciliation channel.
- Recommended fix: append current-status rows for unresolved exceptions and closure-era contradiction entries; cite exact exception IDs in the verdict.
- Suggested validation: register-vs-verdict diff; findings mapped to contradiction IDs.
- Owner suggestion: owner · Effort: S · Dependencies: none · Status: open

### Finding ID: EVID-P3-001 - Housekeeping: decision-log ordering and the cited archive path

- Severity: P3 · Confidence: High · Area: EVID (prior REV-P2-001, partial)
- Evidence: 136 decision-log rows with 4 out-of-order transitions (2026-09-20T22:45Z→22:43Z; 2026-09-21T06:25Z→06:16Z; 2026-09-22T07:30Z→07:20Z; 2026-09-30T04:35Z→04:25Z); verdict/review cite `/home/user/falcon-review-delivery-2026-09-29.tar.gz` = `fc8b9007…`, but that path holds `090d48b3…`; signed bytes preserved at `...-2026-09-29-reviewed.tar.gz` (`fc8b9007…`, verifier-confirmed).
- Recommended fix: add an ordering note/`logged_utc` column; update the cited archive path or restore signed bytes. · Validation: monotonicity check; path+digest check as written. · Owner: maintainer · Effort: S · Status: partially-fixed

## Prior-Run Finding Status (REV lens, run 20260930-0320)

| Prior ID | Status now | Evidence |
|---|---|---|
| REV-P1-001 publication artifacts contradict APPROVED | still-open | verdict binds `c312ab7`; in-package FINAL_RESPONSE (`b8542bf`) vs tree (`12aa2fd`) vs digest (`3ac6cd4`) |
| REV-P1-002 independence unverifiable/self-closed | still-open (worse) | transcription-only report; JPB recorded as installer |
| REV-P1-003 verdict contradicts itself/ledgers | partially-fixed | verdict APPROVED; line 31 still "NOT_SUPPORTED"; limitations cite pending SPAN while P5-G02/P9-G04 PASS |
| REV-P2-001 reviewed archive not at cited path | partially-fixed | signed copy preserved; canonical path `090d48b3…`; docs unchanged |
| REV-P2-002 reproduction claims not reproducible | partially-fixed | chain verifier passes; absolute meta/sidecar paths remain |
| REV-P2-003 gate-claim evidence gaps | partially-fixed | P9-G04/P5-G02 real-mirror evidence; P9-G06 single-index; P9-G02 via transcription |
| REV-P3-001 uncatalogued raw evidence | still-open | 11 `.out` files not indexed by basename |
| REV-P3-002 stale supporting docs | still-open | progress ledger mtime 2026-09-21; README/AGENTS stale |
| REV-P3-003 manifest path base; phase-9 N/A; PASS exits | mixed | PASS-nonzero fixed (0); N/A omission open; absolute paths open |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Approval invalid for delivered package | High | Certain | Release gate unearned | EVID-P0-001 | rebind/re-review |
| Reviewer independence contradicted | High | High | Assurance failure | EVID-P0-002 | new reviewer/artifact |
| Credential exposure in deliveries | High | Certain | Compromise | EVID-P1-004 / API-P0-001 | rotate/remove/rescan |
| Contradictory verdict artifacts | Medium | High | Wrong decisions | EVID-P1-002/003 | single source of truth |

## Recommendations

**Immediate / Release Blocking:** (1) Re-review/rebind over the exact delivered package; separate gate flips from approval commits (EVID-P0-001). (2) Replace the transcription with a reviewer-produced artifact; resolve the JPB installer conflict (EVID-P0-002). (3) Remove/rotate the exposed Wazuh credentials; redact and fix the scanner (EVID-P1-004).

**This Week:** (1) Regenerate `FINAL_RESPONSE.json` from the verdict source; make digest and response agree (EVID-P1-002). (2) Refresh AGENTS.md/README/progress ledger; log reconciliation entries (EVID-P1-003, EVID-P2-003). (3) Rebuild the package atomically (EVID-P1-001); fix the phase-9 aggregate and root manifest naming (EVID-P2-001/002).

**This Month:** (1) Add CI checks: verdict↔digest, package↔tree diff, decision-log ordering, scanner XML negatives. (2) Reconcile the exception register; add per-gate criteria (EVID-P2-003, EVID-005). (3) Update the verdict to cite the signed `-reviewed` archive (EVID-P3-001).

**Later / Platform Evolution:** signed review/release provenance manifest; a single derived status document for all publication artifacts.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Include N/A in phase-9 aggregate | aggregate sums | `publish_digests.sh` | recompute 14 rows |
| Add closure contradiction entries | reconciliation | `ledgers/contradiction_ledger.md` | review |
| Refresh AGENTS.md open-gate line | stops misdirected work | `AGENTS.md` | diff vs ledger |
| Ordering note in decision log | append-only clarity | `ledgers/decision_log.md` | monotonicity script |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Verdict rebind tooling + immutable packages | P0 | release engineer | M | rebuild vs re-review decision |
| Reviewer provenance workflow | P0 | owner | M | reviewer availability |
| XML-aware secret scan + rotation | P1 | security | S | none |
| Package/tree atomic consistency check | P1 | release engineer | S | build script |
| Ledger reconciliation cadence | P2 | maintainer | S | none |

## Suggested Tests

- Unit: aggregate includes N/A and sums to row count; verdict parser fails closed.
- Integration: package build then tree-diff assertion (0 unexpected differences).
- E2E: fresh verifier reproduces every digest bound by `PACKAGE_DIGEST.txt` for the delivered commit.
- CI: decision-log monotonicity; approval docs cannot change in a gate-flip commit; scanner negatives for `<api_key>`, `<key>`, `<password>`.
- Manual/regression: owner verification of reviewer identity and adoption; re-run the 10-row claim sample after remediation.

## Suggested Documentation Updates

- `AGENTS.md`/`README.md`: current gate/verdict state; rebind procedure.
- `REPOSITORY.md`: which manifest verifies which tree; publication artifact names.
- `docs/phase9/review/` template: provenance fields (author, transcript path, independence evidence).
- `ledgers/exception_register.md` and `contradiction_ledger.md`: closure-era entries.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does a JPB-authored disposition artifact exist off-repo? | review validity | external file/signature |
| Was the delivered 2026-09-30 archive reviewed by anyone? | gate scope | reviewer record for `3ac6cd4` |
| Are the exposed Wazuh keys live? | rotation urgency | rotation log (read-only) |
| Which artifact is authoritative for external parties? | consumer clarity | operator decision |

## Appendix

Read-only commands: `git rev-parse HEAD` (falcon `8282d3f…`, edge `45dfed0`→`f1c5def…`); `sha256sum -c` on both manifests and the root manifest; `verify_publication_chain.sh` → 0 failures; `git archive 3ac6cd4` compared under `/tmp/opencode/state3ac6`. This audit wrote only this report and `42_cross_repo_integration_pairing_audit.md`; no ledger, gate, evidence or delivery file was modified.
