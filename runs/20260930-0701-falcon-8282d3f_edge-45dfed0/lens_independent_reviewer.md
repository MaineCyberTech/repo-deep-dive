# Lens — Independent Reviewer

## Audit Metadata

- Audit name: `repo-deep-dive` · Profile: `falcon-lab` · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Lens: `independent_reviewer` (area `REV`); adversarial claim-vs-evidence overlay; domain findings cross-referenced, not re-filed
- Repos: falcon-build `main@8282d3f` (dirty: one in-flight REVIEW-FIX capture + untracked audit dir) · falcon-edge-build `main@f1c5def` (clean; run anchored `45dfed0`)
- Generated 2026-09-30T15:40Z · read-only; commands in `/tmp/opencode`; no repo/ledger/gate/delivery mutation; no secret values printed
- Scope limits: GitHub server-side settings not queryable (no API creds); live host, root-owned delivery files, DO watcher, offsite listings `unverified`

## Scope

Reviewed (targets 32, 33, 34, 35, 41 + prior run `20260930-0320-falcon-794ba31_edge-2b5bc8b`): the verdict/review/adoption chain (digests, dates, author/reviewer roles), digest/manifest chains, gate-flip history, review-claim reproduction, and whether prior-run REV findings are fixed at the current commits. Not reviewed: full domain quality (other reports).

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json`, `PRODUCTION_VERDICT.md`, `REVIEW_REPORT_2026-09-29.md`, `OWNER_ADOPTION.md`, `docs/phase8/REVIEW_RECORD.md`, `OWNER_ACCEPTANCE.md` | records | Claim chain under review |
| `review-package/MANIFEST.sha256` (2,067), `evidence/MANIFEST.sha256` (933), `PACKAGE_MANIFEST.sha256`, `verify_publication_chain.sh`, `publish_digests.sh`, `generate_final_response.py` | artifacts/code | Digest derivation and honesty |
| `ledgers/{gate_ledger.csv,phase9_gate_ledger.csv,decision_log.md,test_execution.csv}` | ledgers | Status truth |
| `/home/user/falcon-review-delivery-2026-09-29{-reviewed,-closure}.tar.gz`, `…-2026-09-30.tar.gz` | delivery | Binding vs shipped bytes |
| Edge `closeout/`, `ledgers/gate_ledger.csv`, `tests/phase10/`, `REVIEW-2026-09-30.md`, `src/falcon_control/{service,pki}.py`, `image/overlay/.../falcon-apply-update.sh`, delivery sidecars/SBOM; reports 32/33/34/35/41 + prior findings | artifacts/audits | Prior-fix verification and claim sampling |

## Verification Performed

Read-only: `git rev-parse/merge-base/log/show`; `sha256sum`/`sha256sum -c` on three manifests; reviewed-archive extraction under `/tmp/opencode/reviewed`; `verify_publication_chain.sh`; `python3 ci/validate.py`; gate-aggregate recount; decision-log monotonicity script; `python3 -m unittest tests.phase10.test_release_artifacts.FinalResponseTests`; `sha256sum -c *.sha256` in the edge delivery; targeted greps on verdict and edge code.

### Claim sample

| # | Claim | Artifact | Reproduction result | Verdict |
|---|---|---|---|---|
| 1 | `gate_aggregate=101 PASS / 0 BLOCKED / 0 IE / 1 NOT_APPLICABLE` | `PACKAGE_DIGEST.txt` → `gate_ledger.csv` | Recount 101 PASS + 1 N/A (102 rows) | supported |
| 2 | `review_package_entries=2067`, sha `0e591249…` | `review-package/MANIFEST.sha256` | `sha256sum -c` exit 0, **2,067/2,067 OK**; hash matches | supported |
| 3 | Evidence manifest (933 entries) verifies | `evidence/MANIFEST.sha256` | exit 1: **932/933**; 1 FAILED (`REVIEW-FIX/…offsite-backup-env-fix.out`); committed blob 0 B; manifests bind `e3b0c442…` (empty) | partially supported |
| 4 | `PACKAGE_MANIFEST.sha256` verifies the repo tree | root manifest | **2,060/2,067 OK**; 4 mismatch + 3 absent; byte-identical duplicate of the package manifest (`cmp`) | unsupported |
| 5 | `verify_publication_chain.sh` → 0 failures | publication script | exit 0; `publication_chain_failures=0`; signed archives intact | supported |
| 6 | The APPROVED verdict covers the delivered package | digest (`3ac6cd4`, 2,067/933) vs verdict (`c312ab7`, 1,168/918); reviewed archive's inner `PACKAGE_DIGEST.txt` | Two generations; 2026-09-30 archive `b8c3fa20…` has no review record; reviewed archive itself carries `program_verdict=INSUFFICIENT_EVIDENCE` | unsupported |
| 7 | "Reviewer disposition digest" `bca83492…` is reviewer-produced | `REVIEW_REPORT_2026-09-29.md` | `sha256` of that file = `bca83492…`; file line 3 "Transcribed… sign-off relayed by the owner" | unsupported |
| 8 | `P9-G11` = "Independent human reviewer disposition published" PASS | `phase9_gate_ledger.csv` | Evidence is the transcription; `REVIEW_RECORD.md` "NOT an independent human reviewer"; decision log names **installer JPB** | unsupported |
| 9 | `human_review=completed and approved 2026-09-22` | `PACKAGE_DIGEST.txt` | `REVIEW_RECORD.md` contradicts human review; `OWNER_ACCEPTANCE.md` (OD-19): owner-attested, name withheld | unsupported |
| 10 | `P9-G10` PASS (archive/manifests independently reproduce) | review report §Integrity | 1,168 (sha `4476fc93…`) + 918 (`adacd9a1…`) reproduce **at `c312ab7`**, not the delivery; chain verifier from archive exit 6 | partially supported |
| 11 | Reviewer commands "runnable from the delivered archive" | review report commands | package cmd OK; `( cd evidence && sha256sum -c MANIFEST.sha256 )` fails as written (no top-level `evidence/`; corrected path 918/918) | not reproducible as written |
| 12 | `phase9_gate_aggregate=13 PASS / 0 BLOCKED / 0 IE / 0 NOT_RUN` | digest vs phase-9 ledger | Ledger is 13 PASS + **1 NOT_APPLICABLE**; `publish_digests.sh:34` prints only PASS/BLOCKED/IE/NOT_RUN | unsupported |
| 13 | `ci/validate.sh` must pass before committing (AGENTS rule) | `python3 ci/validate.py` | 4 PASS; **FAIL secret scan: 3 `long_hex` findings in this run's own `01`/`02`/`43` reports** (32 saw 2) | unsupported at audit time |
| 14 | Edge release manifest + sidecar verify | delivery `*.sha256` | manifest sidecar **FAIL**; lab8 SBOM sidecar FAIL (`/home/runner/…`); all artifact digests OK | unsupported |
| 15 | Prior REV-P1-004/005 (enrollment→operator; update-apply root trust) fixed | edge code | No diff `2b5bc8b..HEAD` for the apply script; `service.py:196-203` maps `CN=operator`→operator; `:333,:399` sign submitted CSRs; SEC/CTR still-open | unsupported (no fix) |
| 16 | `P7-G09` tabletop PASS | `gate_ledger.csv:90` vs `docs/phase7/CLOSEOUT.md:16` | Ledger PASS; closeout row still `INSUFFICIENT_EVIDENCE` while row 77 closes it; compressed/async session | partially supported |
| 17 | Neither `main` protected / falcon state Unknown | report 34 + edge `docs/GITHUB_CI.md` §Plan limitations | Edge documents 2026-09-30 API-attempt failures; falcon has no protection text (grep); server state needs API creds | not reproducible from repo alone |

Outcomes: **supported 3** (#1,2,5) · **partially supported 3** (#3,10,16) · **unsupported 9** (#4,6,7,8,9,12,13,14,15) · **not reproducible 2** (#11,17).

## Executive Summary

The mechanics of the central evidence estate are largely honest: manifests recompute, the publication-chain verifier passes at its declared commit, gate aggregates recount, the reviewed archive's 1,168/918 manifests verify, and the offsite fix was really executed (exit 0, hash matching). The **claims that fail** sit at the approval boundary, exactly where this lens looks:

1. **The approval covers a package nobody shipped.** Verdict/review/adoption bind `c312ab7` + 1,168/918 + archive `fc8b9007…` (Sep 29); the delivered set is `3ac6cd4` + 2,067/933 + `090d48b3…`/`b8c3fa20…` (Sep 30), and the reviewed archive itself contains a digest saying `INSUFFICIENT_EVIDENCE`.
2. **Independence is self-referential.** The "reviewer disposition digest" is the SHA-256 of the in-repo transcription that `build-agent` wrote in the same commit (`6f3c2e4`) that flipped the gates; JPB is recorded elsewhere as the SPAN installer; `P9-G11` says "Independent human reviewer".
3. **Machine artifacts disagree at HEAD** (digest=APPROVED vs `FINAL_RESPONSE.json`=INSUFFICIENT_EVIDENCE, hardcoded), the phase-9 aggregate omits N/A, and the audit run's own reports break the repo's mandated secret scan (3 `long_hex` hits).
4. **Prior-run edge security P1s are untouched** at `f1c5def` (no fix commits; SEC/CTR re-filed them); the phase-10 consistency defect is genuinely fixed (tests green, counts match).
Findings: 1 × P0, 2 × P1, 3 × P2, 0 × P3 (6 total). Domain findings are not re-filed except where the REV lens adjudicates a claim (approval and independence chains).

## Inventory (claim-chain artifacts, state)

| Item | Path | State | Risk |
|---|---|---|---|
| Controlled verdict | `docs/phase9/review/PRODUCTION_VERDICT.md` | APPROVED; body says NOT_SUPPORTED/pending SPAN | High |
| Review report | `docs/phase9/review/REVIEW_REPORT_2026-09-29.md` | "Transcribed… sign-off relayed" | High |
| Digest | `PACKAGE_DIGEST.txt` | binds `3ac6cd4`; APPROVED derived from counts | High |
| Closeout JSON | `closeout/FINAL_RESPONSE.json` | verdict IE, commit `12aa2fd`, hardcoded | High |

## Findings

### Finding ID: REV-P0-001 - The release approval binds a superseded package; the reviewed archive itself carries a denying digest

- Severity: P0 · Confidence: High · Area: REV (delivery/approval binding)
- Evidence:
  - `PRODUCTION_VERDICT.md` lines 8–20: `c312ab7`, manifest `4476fc93…` (1,168), evidence `adacd9a1…` (918), archive `fc8b9007…` — all re-verified in the extracted reviewed archive; `PACKAGE_DIGEST.txt` binds `3ac6cd4…`/2,067/`2a7f4f7b…`
  - `tar xOf …-2026-09-29-reviewed.tar.gz ./PACKAGE_DIGEST.txt` → `program_verdict=INSUFFICIENT_EVIDENCE`; `/home/user/falcon-review-delivery-2026-09-29.tar.gz` = `090d48b3…` (not the bound `fc8b9007…`); `…-2026-09-30.tar.gz` = `b8c3fa20…` (no review record)
- What is happening: the review/adoption/verdict were produced against a Sep-29 package; the program kept rebuilding (Wazuh config round, relay fixes) and shipped a different generation no reviewer covered; the sign-off archive holds a machine artifact that denies the verdict.
- Why it matters: "APPROVED" cannot be reproduced against any delivered artifact; every rebuild silently voids the approval.
- User / business impact: external consumers receive an approval for bytes they do not have.
- Security / privacy / reliability impact: governance control failure; release gate unearned.
- Recommended fix: re-review and rebind over the exact delivered commit/archive (or rebuild an immutable package at `c312ab7` and deliver exactly that); make re-review mandatory on rebuild; never ship a reviewed package whose digest denies it.
- Suggested validation: CI equality verdict digests ↔ `PACKAGE_DIGEST.txt` ↔ shipped archive; extraction test asserting the inner digest matches the verdict.
- Owner suggestion: owner + release engineer · Effort: M · Dependencies: EVID-P0-001
- Status: still-open (prior REV-P1-001/002)

### Finding ID: REV-P1-001 - The independence claim is self-referential; `P9-G11` wording requires a human reviewer

- Severity: P1 · Confidence: High · Area: REV (review-claim artifacts / JPB)
- Evidence:
  - `sha256(REVIEW_REPORT_2026-09-29.md)` = `bca83492…` — the exact "reviewer disposition digest" recorded in the ledger/adoption; the file says "Transcribed… sign-off relayed by the owner"; `decision_log.md:91,109` "installer JPB" while `:139` asserts independence
  - `git show 6f3c2e4` — one `build-agent` commit flips the gates and publishes the "signed" records; `phase9_gate_ledger.csv` P9-G11 criterion "Independent human reviewer disposition published"; `REVIEW_RECORD.md` "NOT an independent human reviewer"
- What is happening: the disposition digest hashes the transcription, not a reviewer artifact; the only named human is also recorded as the installer.
- Why it matters: the core production assurance claim rests on self-attestation relayed through the implementer.
- User / business impact: verdict credibility; no accountable basis for the production approval.
- Security / privacy / reliability impact: release-blocking assurance failure under the program's own doctrine.
- Recommended fix: reviewer-produced signed disposition with provenance and true role; disambiguate JPB or replace the reviewer; if only an agent review exists, reword gate/verdict and owner-accept explicitly.
- Suggested validation: provenance test (author ≠ implementer; digest binds an external artifact).
- Owner suggestion: owner · Effort: M · Dependencies: human inputs (OD-19)
- Status: still-open (same root cause as EVID-P0-002; filed for the P9-G11 wording and digest-of-transcription proof)

### Finding ID: REV-P1-002 - Machine-readable verdict artifacts disagree at HEAD and are not derived from one source

- Severity: P1 · Confidence: High · Area: REV (gate/digest honesty)
- Evidence:
  - `PACKAGE_DIGEST.txt` `program_verdict=APPROVED`/`production_readiness=APPROVED` (generated 2026-09-30T06:57Z) vs `closeout/FINAL_RESPONSE.json` `verdict=INSUFFICIENT_EVIDENCE`/`production_readiness=NOT_SUPPORTED`; `generate_final_response.py:65-66` hardcodes both
  - `publish_digests.sh:30-32` derives APPROVED from gate counts + verdict-file existence, never the verdict text; `PRODUCTION_VERDICT.md` still says "NOT_SUPPORTED until the mandatory gates pass"; `publish_digests.sh:34` omits NOT_APPLICABLE
- What is happening: two shipped machine artifacts assert opposite verdicts; the digest can approve a document whose body denies readiness; the phase-9 aggregate does not sum to 14 rows.
- Why it matters: automation/reviewers cannot determine the governing verdict; no contradiction-ledger entry exists.
- User / business impact: wrong decisions for consumers of the closeout JSON.
- Security / privacy / reliability impact: hidden statuses (N/A); governance drift.
- Recommended fix: single source of truth feeding both generators; fail closed on non-APPROVED verdict content; include N/A; add a CI equality test and contradiction entries.
- Suggested validation: generate both artifacts, assert equality; aggregate sums to 14.
- Owner suggestion: release engineer · Effort: S · Dependencies: EVID-P0-001/EVID-P1-002
- Status: partially-fixed (digest de-hardcoded 2026-09-30T04:35Z; response and N/A omission remain)

### Finding ID: REV-P2-001 - Reviewer reproduction commands are not reproducible as written from the delivered archive

- Severity: P2 · Confidence: High · Area: REV (review-claim reproduction)
- Evidence: from `/tmp/opencode/reviewed`: package manifest 1,168/1,168 OK; `( cd evidence && sha256sum -c MANIFEST.sha256 )` fails (archive has `review-package/evidence/`; corrected path verifies 918/918); `verify_publication_chain.sh` from `review-package/` exit 6 (reads `PACKAGE_DIGEST.txt` at a base it cannot see; needs a git repo); the record cites `/home/user/falcon-review-delivery-2026-09-29.tar.gz` = `fc8b9007…`, but that path holds `090d48b3…`
- What is happening: the review's "all matched; runnable from the delivered archive" claim is true only after path corrections; the chain verifier cannot run from an archive at all.
- Why it matters: an independent verifier following the record fails before reaching the substance; the cited location no longer holds the signed bytes.
- User / business impact: review evidence cannot be re-executed as documented.
- Security / privacy / reliability impact: tamper detection harder than the record implies.
- Recommended fix: print commands exactly as run from archive root; ship a standalone non-git verifier; never rewrite date-named paths or cite a mutable path for signed bytes.
- Suggested validation: run every listed command from a fresh extraction with no edits; expect 0 failures.
- Owner suggestion: release engineer + reviewer · Effort: S · Dependencies: build/verify scripts
- Status: partially-fixed (prior REV-P2-002; digests verify with corrected paths)

### Finding ID: REV-P2-002 - The audit run's own reports break the repository's mandated validation gate

- Severity: P2 · Confidence: High · Area: REV (audit hygiene/self-consistency)
- Evidence: `python3 ci/validate.py` → 4 PASS, then `FAIL secret scan findings` with 3 `long_hex` hits in this run's `01_repository_inventory.md:6`, `02_architecture_runtime_topology.md:6`, `43_edge_fleet_hardware_audit.md:8`; report 32 recorded the same failure with 2 hits; `AGENTS.md` rule 5 requires `ci/validate.sh` to pass before committing; `audit_manifest.json` declares `wiring.gateMutation: none` while the run adds untracked `docs/audits/**` that makes validation fail
- What is happening: full 40-hex SHAs in audit reports trip the scanner, so the falcon tree cannot pass its own gate while the audit exists; no allowlist/decision entry exists.
- Why it matters: a future commit either ships failing validation or must exclude/edit reports; both contradict the evidence-first doctrine; "no mutation" is true only at file-content level.
- User / business impact: noisy secret-scan signal; reviewer distrust of the gate.
- Security / privacy / reliability impact: a real future finding can hide in accepted noise.
- Recommended fix: allowlist `docs/audits/**` (hashes are intentional, non-secret) or omit full SHAs; record the decision; add a scanner self-test with audit output present.
- Suggested validation: `python3 ci/validate.py` exits 0 with the audit folder present; synthetic secret fixture still fails.
- Owner suggestion: maintainer + audit pack owner · Effort: S · Dependencies: `secret_scan.py`, `ci/validate.py`
- Status: open

### Finding ID: REV-P2-003 - Prior-run edge P1 security fixes are absent at the current commit; the phase-10 fix is real

- Severity: P2 · Confidence: High · Area: REV (prior-fix verification)
- Evidence: `git diff --stat 2b5bc8b..f1c5def` empty for `image/overlay/.../falcon-apply-update.sh` and `deploy/falcon-update-apply.*`; `service.py:201-203` still returns `Identity("operator")` on `peer_cn == "operator"`; `:333,:399` still sign `data["csrPem"]` verbatim; SEC-P1-001/002 and CTR-P1-002 re-file these still-open; the phase-10 consistency test is green at `f1c5def` (prior REV-P1-006 fixed)
- What is happening: the two most serious edge P1s have no fix commit and no time-bounded owner acceptance; the data-integrity defect was fixed without regression.
- Why it matters: enrollment-token holder → operator; root code execution via the agent-writable update request.
- User / business impact: fleet control and device root remain exposed (details in SEC/CTR findings).
- Security / privacy / reliability impact: unchanged from the prior run.
- Recommended fix: follow the SEC/CTR redesigns (server-pinned subjects, root-side signed-manifest verification, symlink-safe extraction) or record owner acceptance with expiry.
- Suggested validation: negative tests (CN=operator rejected; forged/symlink bundle rejected) plus a green update drill.
- Owner suggestion: edge maintainer + owner · Effort: M · Dependencies: PKI/update-flow change
- Status: still-open (prior REV-P1-004/005)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Approval does not cover shipped bytes | High | Certain | Release gate unearned | REV-P0-001 | Re-review/rebind |
| Independence claim self-referential | High | High | Assurance failure | REV-P1-001 | Reviewer artifact |
| Opposing verdict artifacts at HEAD | Medium | High | Wrong decisions | REV-P1-002 | Single derived status |
| Review record fails reproduction as written | Medium | High | Review not repeatable | REV-P2-001 | Fix commands/standalone verifier |
| Edge P1 security untouched | High | High | Fleet compromise path | REV-P2-003 | SEC/CTR fixes |

## Recommendations

### Immediate / Release Blocking
1. Re-review + rebind (or rebuild an immutable package from `c312ab7` and deliver it) — REV-P0-001.
2. Replace the transcription with a reviewer-produced artifact; resolve the JPB role conflict — REV-P1-001.
3. Fix verdict-artifact divergence and the N/A aggregate; add the equality test — REV-P1-002.

### This Week
4. Correct the review report's commands; ship a standalone verifier — REV-P2-001.
5. Allowlist `docs/audits/**` in the scanner; record the decision — REV-P2-002.
6. Re-generate the edge manifest/sidecar atomically; publish the ed25519 key (SBOM-P2-001/004; prior REV-P3-009).

### This Month
7. Fix or owner-accept-with-expiry the edge P1s (SEC-P1-001/002, CTR-P1-002) — REV-P2-003 — and add CI checks for verdict↔digest↔archive equality plus a scanner self-test with audit reports present.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Include N/A in the phase-9 aggregate | Aggregate sums | `publish_digests.sh` | recompute 14 rows |
| Delete/derive the "28 alert rules" line | Stale claim | `PRODUCTION_VERDICT.md` | diff vs catalogue (31) |
| Cite the `-reviewed` archive name | Reproducibility | review/verdict/adoption | `sha256sum` at cited path |
| Add contradiction entries for verdict artifacts | Reconciliation | `contradiction_ledger.md` | review |

## Hardening Backlog

| Item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Re-review/rebind workflow + rebuild policy | P0 | owner + release | M | reviewer availability |
| Reviewer provenance + gate wording | P1 | owner | M | human input |
| Single derived status generator | P1 | maintainer | S | verdict parser |
| Scanner allowlist for audit reports + CI self-test | P2 | maintainer | S | none |

## Suggested Tests

- CI: digest ↔ `FINAL_RESPONSE.json` ↔ verdict-text equality; phase-9 aggregate sums to 14; `ci/validate.py` passes with `docs/audits/**` present.
- E2E: extract the shipped archive and run every command in the review record verbatim; expect 0 path corrections.
- Provenance/regression: the disposition digest binds a non-`build-agent` artifact; after any rebuild the review record's commit/digest equals the shipped one.

## Suggested Documentation Updates

- `docs/phase9/review/`: provenance fields (author, transcription path, independence evidence); correct commands and archive path.
- `AGENTS.md`/`REPOSITORY.md`: canonical-immutable archive vs "latest pointer"; audit-output scanner policy; contradiction-ledger entries for the verdict/digest divergence and N/A omission.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does a JPB-produced disposition artifact exist off-repo? | Independence validity | external file/signature |
| Was the 2026-09-30 delivery (`b8c3fa20…`) reviewed by anyone? | Gate scope | reviewer record for that archive |
| Which artifact is authoritative for external parties? | Consumer clarity | operator decision |

## Appendix

### Prior-run REV finding status (current commits)

| Prior ID | Status now | Evidence |
|---|---|---|
| REV-P1-001 (digest contradicts verdict) | partially-fixed | digest now derived (decision log 04:35Z); `FINAL_RESPONSE` still hardcoded; divergence verified |
| REV-P1-002 (independence self-closed) | still-open (worse) | disposition digest = transcription hash; JPB installer entries |
| REV-P1-003 (verdict self-contradiction) | partially-fixed | body still "NOT_SUPPORTED"; 28 rules vs 31 |
| REV-P1-004 (enrollment→operator) | still-open | code unchanged at `f1c5def` (SEC-P1-001) |
| REV-P1-005 (update-apply root trust) | still-open | no diff `2b5bc8b..HEAD` (CTR-P1-002) |
| REV-P1-006 (edge response + phase-10) | partially-fixed | tests green; commit `d6147ef` lags HEAD; sidecar FAIL (SBOM-P2-001) |
| REV-P2-001 (archive path drift) | partially-fixed | `-reviewed` preserves `fc8b9007…`; citations still point at `090d48b3…` |
| REV-P2-002 (reproduction commands) | partially-fixed | package cmd OK; evidence path/chain verifier fail as written |
| REV-P2-005 (P4-G02 owner flash) | partially-supported | lab-side captures only (report 41 sample) |
| REV-P3-009 (no ed25519 public key) | still-open | no pubkey in delivery (SBOM-P2-004) |

### Cross-reference: REV-ID ↔ domain ID

| REV-ID | Related domain ID(s) | Relationship |
|---|---|---|
| REV-P0-001 | EVID-P0-001, INV-P0-002, INTG-P0-001; prior REV-P1-001/002 | Same binding defect; REV adds reviewed-archive denial + delivery-coverage adjudication |
| REV-P1-001 | EVID-P0-002, prior REV-P1-002 | Same root cause; REV adds digest-of-transcription proof and P9-G11 wording |
| REV-P1-002 | EVID-P1-002, EVID-P1-003, EVID-P2-001, ND-P1-001, ND-P2-002 | Machine-artifact divergence/N-A; REV adjudicates claim honesty |
| REV-P2-001 | EVID-P3-001, SBOM-P2-001; prior REV-P2-002 | Reproduction commands + archive path |
| REV-P2-002 | report 32 note; CI area (10) | Unique to this lens: audit output breaks `ci/validate.py` |
| REV-P2-003 | SEC-P1-001/002, CTR-P1-002; prior REV-P1-004/005 | Prior-fix reality check; domain findings own remediation |

### Reproduction notes

Reviewed archive extracted at `/tmp/opencode/reviewed`; logs at `/tmp/opencode/{rp_verify,ev_verify2,root_verify,rev_pkg,rev_ev2,rev_chain,chain}.txt`. No repository, ledger, gate, evidence or delivery file was modified by this lens; the only file written is this report.
