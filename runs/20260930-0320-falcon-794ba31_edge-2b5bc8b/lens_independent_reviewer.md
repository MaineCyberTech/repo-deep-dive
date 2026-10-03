# Lens — Independent Reviewer

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab
- Run: `20260930-0320-falcon-794ba31_edge-2b5bc8b`
- Prompt: lens `independent_reviewer` (`lenses/independent_reviewer.md`, area `REV`)
- Repos: falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b`
- Generated: 2026-09-30 (converted from source audits)
- Area code: `REV`
- Source reports: `source_reports/02-falcon-build-reviewer.md`, `source_reports/04-falcon-edge-reviewer.md`
- Scope limitations: no root/docker/wg; reviewer signatures, live container/VPN/firewall state, offsite backup contents, and host-side protections were not independently verifiable

## Doctrine and Safety Compliance

- Audit-only observed: yes — read-only; reproductions confined to `/tmp` and clean clones
- Secret values redacted: yes
- Artifacts written only under the run folder: yes
- Repo HEAD re-checked before writing: yes — edge HEAD moved during the audit

## Executive Summary

The engineering record is unusually strong on **internal** integrity: package/evidence manifests verify (2,043 and 930 entries), `ci/validate.sh` passes, the publication chain reproduces 0 failures from a git clone, and the sampled gate evidence (26 captures on falcon; 40+ gates on edge) largely supports the recorded statuses — no fabricated output was found. The **claims that do not hold** are about *verdict-level* and *security* matters:

- falcon: the APPROVED production verdict is **not supported at the level claimed** — the delivery's own machine artifacts contradict it (hard-coded), the review/adoption chain is an owner/agent transcription (all 349 commits authored `build-agent`; the closure commit both signed and flipped gates), and the verdict document contains pre-closure contradictions. Lab implementation: substantially supported; controlled production verdict: not supported as a reproducible, consistently-bound claim.
- edge: evidence integrity holds (296/296 captures hash-verified; validators pass), the signed manifest/SBOM/lab7 image independently verify — but two **significant security design weaknesses** exist (enrollment→operator privilege escalation; update-apply root trust), the current HEAD fails its own phase-10 consistency test, and specific gate claims (P4-G02, P9-G04, P1-G06) are not supported by their cited evidence as written.

Findings: 6 × P1, 7 × P2, 12 × P3 (25 total; 9 falcon-build, 16 falcon-edge).

## Scope

- falcon: the Phase 9 claim (independent review, owner adoption, published APPROVED verdict) and the delivery chain bound to a commit
- edge: the lab review gates, release verification (manifest/SBOM/image), and code/security review
- Not reviewed: full domain quality (scheduled for a full run)

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `review-package/MANIFEST.sha256`, `evidence/MANIFEST.sha256` | manifests | Reproduced directly |
| `docs/phase9/review/` (report, adoption, verdict), `closeout/FINAL_RESPONSE.json` | records | The claim under review |
| `ledgers/*` + 26 sampled captures (falcon) / 40+ gates (edge) | records | Claim vs evidence sampling |
| Delivery archives (`…-29-reviewed`, `…-29-closure`, `…-09-30`) | artifacts | Binding drift checks |
| Edge: `src/falcon_control/*`, `src/falcon_agent/*`, `deploy/*`, `image/overlay/*`, manifest + SBOM + image verifier | code/artifacts | Security and release verification |
| Edge: `closeout/`, `ledgers/gate_ledger.csv`, `evidence/raw/*` | records | Gate claim checks |

---

## Findings — falcon-build

### Finding ID: REV-P1-001 - The delivery's own publication artifacts contradict the APPROVED verdict

- Severity: P1 (source: HIGH) · Confidence: High
- Area: REV · Repo: falcon-build
- Evidence: `PACKAGE_DIGEST.txt` (generated 2026-09-30T03:00:10Z) still `program_verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`; `closeout/FINAL_RESPONSE.json` same; `AGENTS.md` lists closed gates as open; hard-coded in `publish_digests.sh` lines 30-35 and `generate_final_response.py`; the closure archive contains the same denying response. Source: 02 §HIGH-1.
- What is happening: every rebuild reproduces machine artifacts that deny the verdict; the chain verifier does not check prose fields.
- Why it matters: any archive recipient receives a "final response" that contradicts the published verdict.
- Impact: verdict credibility; automation consuming the artifacts is misled.
- Recommended fix: generate the fields from ledgers + verdict; make the chain verifier cross-check them.
- Suggested validation: regenerate; diff against ledgers; verifier fails on mismatch.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: ND-P1-001 (same root cause)
- Status: open at audit time

### Finding ID: REV-P1-002 - Independence/adoption is unverifiable and appears self-closed

- Severity: P1 (source: HIGH) · Confidence: High
- Area: REV · Repo: falcon-build
- Evidence: review report is "transcribed from the reviewer's disposition"; no reviewer-provided artifact exists; all 349 commits authored `build-agent`, including closure commit `6f3c2e4` which both added signatures and flipped P8-G10/P9-G02/G10/G11/G12/G14 to PASS; reviewer JPB is also recorded as the SPAN installer (independence basis conflict); no raw captures for P9-G02/G10. Source: 02 §HIGH-2.
- What is happening: production-facing gates rest on owner/agent attestation; the "must not be self-closed" rule was not honoured.
- Why it matters: the production verdict's independence claim is the core of Phase 9.
- Impact: P9-G11/G12 and verdict gates unverifiable as independent evidence.
- Recommended fix: produce the reviewer's original disposition as a separate artifact with its own digest; disambiguate JPB (reviewer vs installer); record owner authorization; re-run or explicitly owner-accept the affected gates.
- Suggested validation: independent artifact with digest + disambiguation record + decision-log entries.
- Owner suggestion: owner (MCT Board) + reviewer · Effort: M · Dependencies: human inputs
- Status: open at audit time

### Finding ID: REV-P1-003 - The published verdict document contradicts itself and the ledgers

- Severity: P1 (source: HIGH) · Confidence: High
- Area: REV · Repo: falcon-build
- Evidence: `PRODUCTION_VERDICT.md` line 31 "NOT_SUPPORTED until the mandatory gates pass" and lines 46-47 "oversubscription qualification pending" coexist with APPROVED and PASS gates. Source: 02 §HIGH-3.
- What is happening: the verdict reads as a selectively filled template never sanity-checked as a whole.
- Why it matters: readers cannot reconcile the verdict with its own body.
- Impact: published-record integrity; downstream confusion.
- Recommended fix: correct the contradictory lines (append-only corrections), then re-verify the document as a whole.
- Suggested validation: read-through checklist; diff against ledgers.
- Owner suggestion: falcon maintainer + reviewer · Effort: S · Dependencies: REV-P1-002 decision
- Status: open at audit time

---

## Findings — falcon-edge-build

### Finding ID: REV-P1-004 - Sensor enrollment can be turned into full operator access (CSR subject + CN trust)

- Severity: P1 (source: HIGH) · Confidence: High
- Area: REV · Repo: falcon-edge-build
- Evidence: `src/falcon_control/service.py:196-203` (`_resolve_identity`: any CA-signed cert with `CN=operator` and unmapped fingerprint becomes operator); `pki.py:30-59` (signs submitted CSR verbatim); `service.py:333,399` (enrollment/renewal sign attacker-supplied CSRs). Reproduced in isolation (`/tmp/opencode/cn-test`): signed CSR with `CN=operator` accepted; identity resolver returned `role=operator`. Source: 04 §F-01.
- What is happening: an enrollment-token holder can obtain a CA-signed cert whose subject authenticates as operator after one renewal unmaps the fingerprint.
- Why it matters: privilege escalation from device holder to fleet operator — the control plane's root of fleet authority.
- Impact: token leak (e.g., pre-baked 7-day claim tokens) yields operator powers: issue tokens/updates/directives, quarantine/revoke sensors, read the fleet.
- Recommended fix: pin sensor certs to server-generated subjects (ignore CSR subject); authenticate operator by unforgeable means (separate CA/EKU/policy extension), never by attacker-supplied CN; reopen P2-G02/P2-G03 after the change.
- Suggested validation: negative test — CSR with `CN=operator` is rejected or mapped to sensor; operator role requires the separate issuance path.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: PKI change → gate reopen
- Status: open at audit time

### Finding ID: REV-P1-005 - The privileged update-apply path trusts an unprivileged, agent-writable request

- Severity: P1 (source: HIGH) · Confidence: High
- Area: REV · Repo: falcon-edge-build
- Evidence: `deploy/falcon-update-apply.path` triggers on agent-writable `/var/lib/falcon-agent/updates/apply-request.json`; the service runs `falcon-apply-update.sh` as root; the script reads `path`/`sha256` from that file (`:37-45`), hashes the named file, extracts with default `tarfile.extractall()` (`:76-80`), and replaces `/opt/falcon-edge/src/falcon_agent` (`:90-96`). Source: 04 §F-02.
- What is happening: the root transaction trusts attacker-controllable input; signed-manifest verification happens only agent-side.
- Why it matters: any agent compromise (the boundary updates must guard) yields root code execution.
- Impact: full device compromise via crafted tarball + forged request file; symlink-member traversal possible.
- Recommended fix: root-side verification (root-owned manifest/digest), constrain `path` to the updates dir, `extractall(filter="data")`, verify member types; add forged-request and symlink negative tests.
- Suggested validation: negative tests fail the exploit path; update drill still passes.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: update-flow redesign; risk-register entry
- Status: open at audit time

### Finding ID: REV-P1-006 - `FINAL_RESPONSE.json` is materially stale/self-contradictory, and the current HEAD fails the phase-10 consistency test

- Severity: P1 (source: HIGH) · Confidence: High
- Area: REV · Repo: falcon-edge-build
- Evidence: response at `96c3e08` still says `commit 6cad6ec…`, "phases 5-6 in progress", device NOT_EXECUTED, lists closed gates as open; counts 62 PASS vs ledger 63 → `tests/phase10/test_ledger_matches_response` FAILS in a clean archive of HEAD; prior remediation `C-106` ("F4 remediated") is overstated (commit `8fd38b1` changed only 3 fields). Source: 04 §F-03.
- What is happening: the machine-readable closeout artifact misrepresents program state and fails its own consistency test.
- Why it matters: the program's primary machine-readable status is wrong exactly where a reviewer would check.
- Impact: review-gate re-verification cannot rely on the artifact; C-101/C-106 resolution overstated.
- Recommended fix: regenerate authored fields from the ledger at current HEAD; re-run phase-10 + validate; amend C-101/C-106 (append-only).
- Suggested validation: phase-10 test passes at HEAD.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: in-flight drills
- Status: open at audit time

### falcon-build — P2 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| REV-P2-001 | P2 | Delivery binding drift; reviewed archive no longer at cited path (canonical path holds a different archive) | 02 §MED-1 | Re-bind/re-publish with unambiguous canonical names; record digests |
| REV-P2-002 | P2 | Reviewer reproduction claims not reproducible as written (evidence manifest path base; chain verifier from archive fails; post-reboot claim uncaptured) | 02 §MED-2 | Fix commands in the report; add archive-runnable verification; bind captures |
| REV-P2-003 | P2 | Evidence gaps for specific gate claims (P9-G07 failover prose-only; P9-G03 failed-first-rotation; P9-G04 interpretive figure; P4-G09 FAIL capture; P9-G08 secret modes) | 02 §MED-3 | Capture the specific scenarios or annotate claims; point notes at the supporting artifacts |

### falcon-edge-build — P2 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| REV-P2-004 | P2 | Review package incomplete (missing image pipeline) and stale (predates lab7/phase-9) | 04 §F-04 | Extend staging list to whole `image/`; rebuild from current HEAD |
| REV-P2-005 | P2 | P4-G02 "owner flash + first boot" PASS not supported by cited evidence (citations are lab-side; owner flash uncaptured) | 04 §F-05 | Cite E-EDGE-ONBOARD-138..143; record owner flash as attestation |
| REV-P2-006 | P2 | P9-G04 flipped to PASS during review without recorded owner approval; inconsistent with P9-G06 | 04 §F-06 | Record owner approval or return gate to BLOCKED/IE; note failed attempts |
| REV-P2-007 | P2 | Agent does not verify control-plane hostname; one CA issues both sides | 04 §F-07 | Enable hostname/SAN verification; EKU separation; document trust model |

### falcon-build — P3 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| REV-P3-001 | P3 | 10 uncatalogued raw evidence files (unindexed, no metadata) | 02 §LOW-1 | Index + metadata backfill |
| REV-P3-002 | P3 | Stale/contradictory supporting documents (owner inputs REQUESTED, progress doc, risk R-29, closeout totals) | 02 §LOW-2 | Append-only refreshes; "superseded" markers |
| REV-P3-003 | P3 | Minor integrity/format nits (manifest path base; phase-9 aggregate omits N/A; two PASS rows with non-zero exits) | 02 §LOW-3 | Note-level corrections |

### falcon-edge-build — P3 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| REV-P3-004 | P3 | P1-G06 PASS cites a capture ending in a failing validation | 04 §F-08 | Append current green-run reference |
| REV-P3-005 | P3 | P4-G01 lab7 "45/45" evidence truncated (`tail -3`) though claim is true | 04 §F-09 | Capture full verifier output next build |
| REV-P3-006 | P3 | P5-G04 raw negatives contain unexplained traceback (prior F9, unresolved) | 04 §F-10 | Interpretation note and/or fix helper |
| REV-P3-007 | P3 | Stale notes/citations missed by F7/F8 remediation (8 vs 10 rules; 130 vs 161 tests; lab6 vs lab7) | 04 §F-11 | Append-only note refresh |
| REV-P3-008 | P3 | `falcon_edge_sensor_pending_directives` counts expired directives forever | 04 §F-12 (dup of ND-P2-015) | Filter expiry; or ack path |
| REV-P3-009 | P3 | Release verification not self-contained (no ed25519 public key in delivery; bundle not in manifest) | 04 §F-13 | Publish `signing.pub.pem` + keyId; re-sign over complete set |
| REV-P3-010 | P3 | Delivery/secret hygiene: private keys + unencrypted secrets backups in delivery dir; hashes in signed manifest | 04 §F-14 | Risk-accept or encrypt; move out of release surface |
| REV-P3-011 | P3 | Capture wrapper exports whole credential file into captured command env (`set -a` + `.env`) | 04 §F-15 | Pass only needed variables via subshell |
| REV-P3-012 | P3 | Minor code/hygiene items (dup `client_ssl_context`, unvalidated Content-Length, `parse_iso` raise, duplicate R-008/R-009, stale EX-001) (Info) | 04 §F-16 | Batch code/hygiene cleanup |

## Cross-References

| This report ID | Related lens/domain | Related ID | Relationship |
|---|---|---|---|
| REV-P1-001 | ND-P1-001/002, ND-P2-002 | digest/response generators | Same root cause: hard-coded verdicts |
| REV-P1-002/003 | (human) | P9-G11/G12/G14 | Verdict gates |
| REV-P1-004/005 | ND-P1-003 | dangerous-by-design class | Security review vs onboarding view |
| REV-P3-008 | ND-P2-015 | same metric bug | Duplicate by design — cross-referenced |
| REV-P2-001/002 | INTG-P0-001 | delivery binding | Reviewer + integration both hit the drift |

**Domain routing for the next full run:** `41` (EVID — the verdict/independence chain), `23` (EXEC), `06`/`36` (security), `32` (DR for capture/release verification), `34`/`35` (release integrity).

## Open Questions (from sources)

1. Where is the reviewer's original disposition artifact (with its own digest)? (02 §7)
2. Are reviewer JPB and installer JPB the same person? (02 §7)
3. Where is the owner instruction authorizing the verdict/adoption? (02 §7)
4. Which archive is canonical for the reviewed delivery? (02 §7)
5. Was the reviewed tree (`c312ab7`) the intended production-bound artifact given ~20 later commits? (02 §7)
6. For edge: will the owner approve the hard-reset approximation (P9-G04) or should the gate return to BLOCKED? (04 §10)

## Appendix

- Full narratives, commands, and annexes: `source_reports/02-falcon-build-reviewer.md`, `source_reports/04-falcon-edge-reviewer.md`
- Finding counts: REV-P1 ×6, REV-P2 ×7, REV-P3 ×12
- Claim-sample outcomes (02): reproduced = manifests, hashes, chain (from clone), review-doc digests, endpoints, most gate evidence; not verifiable = signatures/instructions, live root-level state, offsite contents, canonical archive digest, P9-G07 failover.
