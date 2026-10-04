# Release Gate — Audit Opinion for run `20260930-0701-falcon-8282d3f_edge-45dfed0`

## Decision

**GO WITH CONDITIONS**

This is the **audit opinion** on the state of the falcon lab (central `falcon-build` @ `8282d3f`, edge `falcon-edge-build` @ `45dfed0`/`f1c5def`, shared live host) as of the 2026-09-30 full-domain run. It is not a program verdict: it does not revoke, replace, or grant one (see *Reconciliation*).

Scope note, stated plainly: this GO applies to **continued lab operation** under the conditions below. The **production-readiness claim is NO-GO until conditions C1–C3 close** — the delivered bytes are not the reviewed bytes, the credential exposure is confirmed, and the pairing contract does not verify. The audit also notes the pack's special check ("NO-GO if unresolved P0"): read literally against every P0 regardless of scope it would stop a working lab over stale signatures and missing detectors; read against the production claim, as the program's own doctrine requires, it is satisfied by treating the 11 P0s as hard, time-boxed conditions. Triggers that would convert this opinion to NO-GO are listed below.

## Why

- **The lab operates and the core pipeline works.** Feeds flow (~2 s lag, 0 drops), alerts deliver on two independent ntfy instances, the daily backup ran, the offsite re-run succeeded (1,723 files, 07:43Z), the edge sensor is enrolled and reporting, and restores/clean-host rebuilds were proven on 2026-09-23. Nothing found requires stopping operations today.
- **But the release claim is not reproducible.** The APPROVED verdict binds `c312ab7` / 1,168-entry package / `fc8b9007…` archive; the delivered package is `3ac6cd4` / 2,067 entries; the reviewed archive itself contains a digest saying `INSUFFICIENT_EVIDENCE`; `FINAL_RESPONSE.json` hardcodes the opposite of `PACKAGE_DIGEST.txt`; and the reviewer disposition is a transcription whose digest hashes the transcription file, with the named reviewer recorded as the installer.
- **The pairing and edge release chain do not verify.** Pin `dffcbbb7…` and sidecar `18681751…` match neither the manifest (`3fa4a49c…`) nor each other; the signed manifest is rewritten in place under a fixed dated name; no central script checks the pin; the stale pin ships inside the package.
- **Credential exposure is confirmed and still shipping.** XML-tag credentials (cluster key, API keys) are in the repo, the review package, and the 2026-09-30 delivery archive while `secret_scan.py` reports `NO_FINDINGS`; the edge CA/operator/signing-seed backup is unencrypted in the shared delivery directory.
- **The system cannot reliably announce its own death or backup failure.** The dead-man bypasses the relay all alerts traverse; total-host loss waits up to ~26 h; stale metrics read healthy; offsite and new-services outcomes have no metric or rule; the edge fleet has zero deployed alerts.
- **Two reproduced security chains remain open:** enrollment token → operator → fleet update authority, and an unsigned/agent-writable root update path with symlink write-through. Neither would be alerted today.

These are serious but bounded, cited, and fixable inside the existing processes — hence GO **with conditions**, not NO-GO.

### Decision basis at a glance

| Question | Answer | Evidence |
|---|---|---|
| Does the lab operate? | Yes | Live probes; pipeline metrics; dual-path deliveries |
| Is the delivered release the reviewed release? | No | Verdict `c312ab7` vs delivery `3ac6cd4` |
| Do the machine verdicts agree? | No | Digest `APPROVED` vs `FINAL_RESPONSE.json` `IE` |
| Is the reviewer independent? | Not evidenced | Transcription; JPB recorded as installer |
| Does the edge release verify? | No | Sidecar/pin/manifest all disagree |
| Are secrets contained? | No | Committed XML-tag credentials; unencrypted edge backups |
| Can the system announce its own failure? | Not reliably | Relay-blind dead-man; offsite unalerted |
| Is recovery proven? | Partly | Restores 09-23; offsite detector absent; new-services unverified |

### What may continue, and what must pause

May continue under this gate: lab monitoring, alerting, backups, and the edge sensor as-is; scoped remediation work under the existing review doctrine; evidence capture per `AGENTS.md`.

Must pause until the named conditions close: any production-readiness claim, cutover, or external reliance on the APPROVED verdict (C1); publishing artifacts that carry the exposed credential material (C2); any "verified" claim for the edge release or pin (C3); running `deploy_edge_alert_rules.sh --apply` as written — use the Grafana path (C6); unsanctioned guard reclaim/fill drills (C7).

## Conditions

| # | Condition | Finding IDs | Done when |
|---|---|---|---|
| **C1** | Re-review/rebind the production approval to the delivered commit, with a reviewer-produced artifact and one derived verdict | EVID-P0-001, EVID-P0-002, INV-P0-002, REV-P0-001; REV-P1-001/002, EVID-P1-001/002/003, FEAT-P1-002 | A reviewer-produced disposition (author ≠ implementer, true role recorded) is digested and bound; `PACKAGE_DIGEST.txt` = `FINAL_RESPONSE.json` = verdict text = shipped archive by a CI equality test; gate flips are not in approval commits; phase-9 aggregate includes N/A (sums to 14); contradiction-ledger entries recorded |
| **C2** | Rotate, remove, and re-scan the exposed credential material; rebuild the package and delivery | API-P0-001; EVID-P1-004, SC-P1-001, SECRET-P1-002/003, XREPO-P1-003, ADV-P1-002 | Keys rotated and recorded; values removed from repo/package/delivery and redactions logged with SHA-256; scanner catches XML-tag and 64-hex credential contexts (fixture test); edge secrets backup encrypted and off the release surface, or owner-accepted with expiry; package and delivery rebuilt |
| **C3** | Freeze the edge release and make the pairing contract verify | INV-P0-001, XREPO-P0-001; FLEET-P1-001, XREPO-P1-001/004, INTG-P1-002 | Manifest names are versioned/immutable; sidecar regenerated atomically and `sha256sum -c` passes; `EDGE_RELEASE_PIN.md` digest/commit/SBOM/image resolve to delivery artifacts; `verify_edge_pin.sh` wired into `ci/validate.py` and a mutated-pin test fails closed |
| **C4** | Make alert-path death visible end-to-end | LIVE-P0-001, RES-P0-002; OBS-P1-001/003, NOTIF-P1-001/002, RES-P1-001/002, IR-P1-001 | A canary alert must arrive on the independent instance each cycle; relay-failure and watcher-age rules live; freshness rules cover every timer/exporter/textfile, guard free space, swap, and scrape errors; the total-loss threshold is owner-set (≤60–90 min target) and a real stop test meets it; a blind-ops page exists |
| **C5** | Make backup truth visible and recovered evidence binding | LIVE-P0-002, RES-P0-001; DR-P1-001/002/003/004/005, OBS-P1-002, DATA-P1-002 | Offsite and new-services last-success gauges with 36 h rules; forced failure fires one alert per path; retention deletes only files absent from the retained union; a missing IRIS dump fails the run; the 07:43Z recovery capture is committed and the package verifies with it; custody attestation + decrypt drill for `backup_enc.key`; edge PKI/DB offsite or owner-accepted |
| **C6** | Close the edge trust ladder and fleet safety gaps | ADV-P1-001/002; SEC-P1-001/002, CTR-P1-001/002, ACM-P1-001/002, FLEET-P1-002, API-P1-001, INTG-P1-001, XREPO-P1-002, OBS-P1-004, LIVE-P1-003 | R1–R4 reproductions fail (non-sensor CSR subjects rejected/mapped; forged and symlink/device bundles rejected; forged ingest id ignored); operator issuance separated with revocation; update swap crash-safe with boot recovery; scoped edge rules deployed via the Grafana path (or Alertmanager) with an end-to-end delivery test and no RETIRED/REVOKED residue firing |
| **C7** | Control capacity before exhaustion | PERF-P1-001/002, LIVE-P1-001, RES-P1-005, ARCH-P1-001 | Root reclaim plan executed + ≥90% critical page; data warning band (15–20 GiB) with projection; sanctioned guard reclaim drill frees space and alerts; 7-day free space stable |
| **C8** | Verification-only pass and reconciliation | All closed findings; ND-P1-001, EVID-P1-003, DOC-P1-001/002/003, REV-P2-002 | Every condition's finding is marked `verified-fixed` with a current-commit artifact; `docs/CURRENT_STATE.md` published in both repos; scanner allowlist/decision recorded so `ci/validate.py` passes with the run folder; gate/risk/contradiction/decision registers refreshed |

**Priority:** C2 and C3 are same-day; C1, C4, C5 this week; C6, C7 this month; C8 closes the gate. C1–C3 additionally govern the production claim (NO-GO until closed).

### Condition sequencing and dependencies

1. **C2 first** — the exposure is live and still shipping; rotation, redaction, and scanner fixes are prerequisites for rebuilding a clean package.
2. **C3 second** — it is low-effort and unblocks any future verification of the edge side.
3. **C1 next** — it depends on owner/reviewer availability, not engineering; start the request now.
4. **C4/C5 in parallel** — detector code plus owner decisions (threshold, custody).

## Post-remediation status (2026-09-30 verification pass)

| Condition | Status | Notes |
|---|---|---|
| C1 | OPEN (human, reviewer artifact pending) | JPB confirmed as final reviewer (owner 2026-10-01); the package rebuilt + rebound (package `305d777`, publication `df934e5`, archive SHA-256 `e4ca5696...`, chain 0 failures); awaiting JPB's disposition (`docs/phase9/review/C1_REVIEW_BINDER.md`) + the owner adoption |
| C2 | DONE | VT + cluster keys rotated, Shuffle key retired, repo/package scrubbed (live-verified); rebuild/rebind at C1 |
| C3 | DONE | Frozen release `f2acd9c`; pin verifies; mutation test fails closed |
| C4 | DONE | Relay/watcher/offsite blindness closed; three-path canary live (all 2xx); DO-side watcher threshold remains |
| C5 | DONE | Backup gauges/rules + verification fix; the offsite pruner union engaged live 2026-10-01; the decrypt drill + restore rehearsal executed 2026-10-01/02; the owner's custody attestation recorded 2026-10-02 (escrow in SharePoint; `docs/security/CUSTODY_ATTESTATION.md`) |
| C6 | DONE | R1–R4 fail closed (tests + live); gates P2-G02/P2-G03 re-verified |
| C7 | PARTIAL | Reclaim + drill + projections live; volume migration + 7-day observation remain |
| C8 | THIS PASS | `verification_log.md`; `docs/CURRENT_STATE.md` in both repos; registers reconciled |

Gate opinion unchanged: **GO WITH CONDITIONS**; the production-readiness claim remains NO-GO until C1–C3 close. Details and residuals: `verification_log.md`.
5. **C6/C7 next** — design changes plus a maintenance window.
6. **C8 last** — verification only; the tree freezes when it starts.

## Reconciliation With Existing Program Verdicts

The program's own flow is the only authority for its verdicts; this audit neither revokes nor grants them.

- **Central:** the program's published verdict is **APPROVED** (2026-09-29) with a reviewer disposition and owner adoption; it stands per the program's flow. **Deltas the audit found:**
  1. **Superseded approval binding** — verdict/review/adoption bind `c312ab7` (1,168/918-entry manifests, archive `fc8b9007…`), while the delivered package is `3ac6cd4` (2,067/933) and the reviewed archive's inner digest says `INSUFFICIENT_EVIDENCE`; the 2026-09-30 archive has no review record.
  2. **Transcription independence** — the "reviewer disposition digest" is the SHA-256 of the in-repo transcription; JPB is recorded elsewhere as the installer; gate flips and approval publication share one `build-agent` commit.
  3. **Hardcoded `FINAL_RESPONSE.json`** — `generate_final_response.py` hardcodes `INSUFFICIENT_EVIDENCE`/`NOT_SUPPORTED` at commit `12aa2fd`, contradicting `PACKAGE_DIGEST.txt` `APPROVED` at HEAD.
  4. **Committed credentials** — XML-tag credentials ship in the repo, review package, and delivery archive; the scanner is blind to them and no redaction entry exists.
  **Recommended reconciliation:** rebuild an immutable package from the reviewed commit and deliver exactly that, or re-review/rebind over the delivered commit; produce a reviewer-produced artifact (or record an explicit owner acceptance of the attestation basis); derive digest and closeout JSON from one source and fail closed; rotate/redact/rebuild the credential-affected artifacts; log all four deltas in the contradiction ledger. Resolve through the program's normal review/adoption flow.
- **Edge:** the program's review remains **CONDITIONAL_PASS for lab review gates with production readiness not supported** (gate ledger 77 PASS / 8 BLOCKED / 3 IE; `production_readiness` NOT_SUPPORTED). The audit concurs and adds C3/C6/C7. The edge review package/acceptance records that bind manifest generation `18681751…` are themselves superseded by the 06:25Z regeneration (`3fa4a49c…`) — a delta to reconcile by accepting releases by digest.
- Where audit conditions and program records differ, the difference is stated here with evidence pointers in the source reports; the resolution path is the program's review/adoption workflow, not this document.

## What this gate is not

- Not a revocation or grant of any program gate, verdict, review, adoption, or release. The APPROVED verdict stands as published; the audit states deltas and recommended reconciliation only.
- Not a substitute for the independent human review or owner adoption the program requires.
- Not a certification of production readiness: the delivered package is not the reviewed package, and C1–C3 govern that claim.
- Not a full re-audit of every P2/P3: remediation of non-release-blocking findings is delegated to the reports and backlog.
- Not based on live root access: container internals, effective firewall state, root logs/archives, offsite listings, and GitHub server settings are `unverified` and do not carry this opinion.

## Path to GO

1. Close C2 and C3 (same day), C1/C4/C5 (this week), C6/C7 (this month), in that order; each condition's evidence is captured per doctrine.
2. Run the verification-only pass (C8) at the settled tree; mark findings `verified-fixed` only with current-commit artifacts.
3. Refresh this gate at the next synthesis against the settled commits; it becomes **GO** when C1–C8 all verify and no condition regresses.

## Path to NO-GO (triggers to revisit)

- Any condition regresses, or a new silent-data-loss path is found.
- Confirmed exploitation of the committed credentials, the enrollment→operator chain, or the root update path (ADV-P1-001/002, SEC-P1-001/002, CTR-P1-002).
- Root or data volume exhaustion occurs before C7 lands.
- The approval binding (C1) is still unreconciled beyond the next review cycle while external parties rely on the APPROVED claim.
- A production cutover is attempted before C1–C3 close.

**Verification basis:** the run's reproductions and claim samples are recorded in `23_executive_summary_release_gate.md` §Verification Performed, `41_evidence_doctrine_gate_integrity_audit.md`, `42_cross_repo_integration_pairing_audit.md`, and the five lens reports; all checks were read-only, secret values were not printed, and no repo, ledger, gate, delivery, or live system was modified by this audit.
