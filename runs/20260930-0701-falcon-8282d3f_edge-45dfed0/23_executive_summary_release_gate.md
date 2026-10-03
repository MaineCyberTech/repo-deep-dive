# Executive Summary and Release Gate

## Audit Metadata

- Audit name: `repo-deep-dive` (profile `falcon-lab` v1.0.0, pack v1.2.1)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (first full-domain run; 45 source reports incl. 5 lenses)
- Repositories: central `/home/user/falcon-build`; edge `/home/user/falcon-edge-build`; delivery `/home/user/falcon-edge-delivery`
- Branch: `main` (both)
- Commit SHA: central `8282d3fd866d` (delivered package `3ac6cd4`); edge run-start `45dfed050fba` (moved to `f1c5def` mid-run; manifest commit `155f2446`)
- Generated at: 2026-09-30 (findings.json 15:50Z; synthesis at the recorded commits)
- Auditor: read-only synthesis subagent (prompt 23); no repo, ledger, gate, delivery, or live-system mutation
- Area code: EXEC
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/23_executive_summary_release_gate.md`
- Scope limitations: no root/docker/nft/wg; live truth from `live_snapshot.txt` (07:01:55Z) plus a 15:29–15:35Z lens refresh; GitHub server settings not queryable; root-only logs/archives and offsite listings `unverified`; secrets by path/type only

## Scope

Reviewed: all domain reports (01–44, incl. 10 N/A), the five lenses, `findings.json` (256 findings), the machine artifacts they contradict (`PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json`, `PACKAGE_MANIFEST.sha256`, gate ledgers, review/adoption records, edge manifest/sidecar, `docs/edge/EDGE_RELEASE_PIN.md`), and the prior-run `RELEASE_GATE.md` (run `20260930-0320-...-edge-2b5bc8b`). Not reviewed: commits after the recorded SHAs; container internals, effective firewall/VPN state, offsite listings, root-owned files; upstream product internals; re-derivation of every domain finding.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `findings.json` + 45 source reports | findings | Aggregate: P0×13, P1×80, P2×131, P3×40 (264) | Generated 2026-09-30T15:50Z |
| `ledgers/{gate,phase9_gate}.csv`, `docs/phase9/review/*` | ledgers/records | Approval chain | 101 PASS+1 N/A; phase-9 13 PASS+1 N/A |
| `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json`, `PACKAGE_MANIFEST.sha256` | generated | Verdict vs delivered bytes | Digest APPROVED vs response IE; hardcoded |
| `review-package/MANIFEST.sha256`, `evidence/MANIFEST.sha256` | checksums | Integrity mechanics | 2,067/2,067 OK; 932/933 |
| Delivery archives + edge manifest/sidecar + pin; `automation/wazuh/.../ossec.conf`; prior-run records; live snapshot | release/config/records/live | Pairing, credentials, continuity, live truth | Sidecar FAIL; scanner blind to XML-tag literals; 0 prior P0s verified-fixed; root 83%/data 62% |

## Verification Performed

| # | Claim | Artifact / source | Reproduction result | Outcome |
|---:|---|---|---|---|
| 1 | `gate_aggregate=101 PASS / 1 N/A` | `ledgers/gate_ledger.csv` | Recount 101 PASS + 1 N/A across 102 rows | supported |
| 2 | Review package 2,067 entries, `0e591249…` | `review-package/MANIFEST.sha256` | `sha256sum -c` exit 0, 2,067/2,067 | supported |
| 3 | Evidence manifest verifies | `evidence/MANIFEST.sha256` | 932/933; one committed 0-byte `REVIEW-FIX` artifact | partially supported |
| 4 | Publication chain 0 failures | `verify_publication_chain.sh` | Exit 0, `publication_chain_failures=0` | supported |
| 5 | Verdict covers the delivered package | verdict vs digest vs archive | Verdict binds `c312ab7`/1,168/918; delivered `3ac6cd4`/2,067/933; reviewed archive's inner digest says `INSUFFICIENT_EVIDENCE` | unsupported |
| 6 | `FINAL_RESPONSE.json` matches the digest | both at HEAD | Opposite verdicts (`IE/NOT_SUPPORTED` vs `APPROVED`); generator hardcodes both | unsupported |
| 7 | Reviewer disposition is independent | `REVIEW_REPORT_2026-09-29.md`, ledgers | Disposition digest = SHA-256 of the transcription; JPB recorded as installer; one `build-agent` commit flips gates and publishes records | unsupported |
| 8 | Edge manifest + sidecar verify | delivery `*.sha256` | Sidecar FAIL (`18681751…` vs actual `3fa4a49c…`); pin `dffcbbb7…` matches neither; signature VALID over current bytes | unsupported |
| 9 | No secrets in the delivered package | `secret_scan.py`; `ossec.conf`; delivery tar | Scanner `NO_FINDINGS`; XML-tag credentials in repo, review package, and 2026-09-30 archive; no redaction entry | unsupported |
| 10 | Token cannot become operator; root update trusts verified input | ADV sandbox R1–R3 | Token→`CN=operator` cert→operator 200/201; forged apply-request accepted; symlink tar write-through installed | unsupported |
| 11 | Literal walks + live host health | README step 1; chain script; read-only probes 07:01–15:35Z | Falcon step 1 exits 1 (`FAIL secret scan findings`); chain 0 failures; edge `ci/validate.sh` ALL PASS (no tests invoked); feeds flowing (~2 s lag, 0 drops), 79/79 primary deliveries 200 over 7 d, backup 03:34Z, offsite re-run 07:43Z; root 83%, data 62%, swap ~58% | partially supported / supported |

Mechanics reproduce; every claim at the approval, pairing, and secret boundaries fails at least one reproduction. No fabricated execution was found (edge captures hash-verify; failures stay in ledgers).

## Executive Summary

The lab is real, operates, and its core pipeline works: feeds flow (sub-second–2 s lag, 0 drops), alerts deliver on two independent ntfy instances, the daily backup and a manual offsite re-run succeeded on 2026-09-30, the edge sensor is enrolled and reporting, and the evidence estate is sincere — manifests recompute, the publication chain verifies at its declared commit, failures stay in the ledgers, and no fabricated output was found. Hence **GO WITH CONDITIONS** for continued lab operation, not NO-GO; the production claim is NO-GO until C1–C3 close (`RELEASE_GATE.md`). Four boundaries are serious:

1. **The approval does not cover the delivered bytes.** Verdict/review/adoption bind `c312ab7` (1,168-entry package); the delivery is `3ac6cd4` (2,067); the reviewed archive itself carries a digest denying the verdict; `FINAL_RESPONSE.json` hardcodes the opposite verdict; the "reviewer disposition" is a transcription whose digest hashes the transcription file, with the named reviewer recorded as the installer.
2. **The edge release chain and pairing contract do not verify.** Sidecar and pin name digests matching neither the manifest nor each other; the signed manifest is rewritten in place under a fixed name; nothing checks the pin; the stale pin ships in the package. Both gates pass over the drift.
3. **Credentials cross the publication boundary.** XML-tag credentials ship in repo, review package, and delivery while the scanner reports clean; edge CA/operator/signing-seed material is unencrypted in the shared delivery directory; device credentials are baked into images.
4. **Monitoring and backups cannot announce their own failure.** The dead-man bypasses the relay every real alert uses; total-host loss waits up to ~26 h (28 Sep outage: no external notice); stale metrics read healthy; offsite/new-services outcomes are unalerted while the local snapshot reads green. Two reproduced chains compound this: a single-use enrollment token becomes fleet-wide operator authority in three API calls, and the root update path accepts agent-writable, unsigned input incl. symlink tar members. Neither is alerted (zero deployed edge rules).

**Strengths to protect:** evidence discipline/append-only records; the review/adoption/verdict separation (right design, missing artifacts); working dual-path alerting with mapped runbooks; the edge test estate (163 checks) and a validly signed manifest whose artifact hashes verify; hardened containers and default-deny networking; honest edge gates (77 PASS / 8 BLOCKED / 3 IE).

**Improved since prior run:** offsite `.env` bug fixed and offsite re-ran (1,723 files, 07:43Z); WG peer preservation + regression check; TLS-silence noise tuned to 6 h; digest derivation de-hardcoded; edge phase-10 consistency fixed; new-services check fails on a missing item; real CI added to both repos. **Not closed:** of the prior six P0s, five partially fixed, one still open — none `verified-fixed`; the open P0 set grew 6→11 as the full sweep covered boundaries the lens run did not.

**Next:** rotate/redact/rebuild and fix the scanner (C2); re-review/rebind with a reviewer artifact and one derived verdict (C1); freeze/rebind the edge release with a CI pin verifier (C3); make alert-path death and offsite failure visible (C4/C5); edge trust and capacity (C6/C7); verification pass (C8). Owner decisions: reviewer identity/JPB, D-007 edge alerts, key custody, retention/reclaim, total-loss threshold.

## Inventory

| Item | Path / symbol | State | Risk | Notes |
|---|---|---|---|---|
| Central package | `PACKAGE_DIGEST.txt`, `review-package/` | Fresh; 2,067/2,067 verify | High | Binding to verdict broken |
| Approval records / closeout verdict | `docs/phase9/review/*`, `closeout/FINAL_RESPONSE.json` | APPROVED (superseded binding); response `IE/NOT_SUPPORTED`, hardcoded | High | EVID-P0-001/002, REV-P0-001 |
| Edge release | manifest + `.sha256` + pin | Signed; sidecar+pin stale; manifest rewritten | High | INV-P0-001, XREPO-P0-001 |
| Alert/backup paths | `heartbeat.sh`, `90-alerting.sh`, `85/80-backup*.sh` | Working; relay-blind; offsite unalerted | High | LIVE-P0-001/002, RES-P0-001/002 |
| Secrets | `ossec.conf`, delivery dir, `.env`, images | Literals committed; concentration; baked reuse | High | API-P0-001, SECRET-P1-00x |
| Edge trust/live host | `service.py`, `pki.py`, apply script; `falcon` host | Token→operator; unsigned root apply; 83% root, swap ~58% | High | ADV-P1-001/002, PERF-P1-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Current state | 3 | Validators pass; pipeline live; edge tests 163 | APPROVED unreproducible at HEAD | Close C1/C3 |
| Strengths | 4 | Manifests, chain verifier, retained failures, dual alerts | Strengths not binding release integrity | Preserve; formalize verification |
| Biggest risks | 2 | 11 P0s incl. credentials, dead-man, backup truth | No active exploit/outage found | Close C2/C4/C5 |
| Release blockers | 1 | Approval, pin/sidecar, credentials | Release claim unearned for delivered bytes | C1–C3, then re-review |
| Business/security/ops/UX impact | 2 | Real disclosure + silent-loss paths; single owner | Owner decisions pending | Owner decisions; blind-ops page |
| Investment recommendation | 3 | Substance sound; fixes scoped and cited | No production claim until conditions close | Continue investment |
| Next actions | 3 | Concrete fixes per finding | Sequencing depends on owner inputs | Execute C1–C8 |
| Risk counts/themes | 4 | 264 findings machine-readable | New ADV themes unalerted | Track to closure |

### Per-audit verdicts (condensed)

| Area(s) | Verdict |
|---|---|
| INV/ARCH/FEAT (01–03) | Structurally complete; release binding broken; single-host SPOF; live code from dirty trees; status claims contradict ledgers |
| SEC/ACM (06, 24) | Above-average lab posture; forgeable operator subject, root-trust update, state-only revocation |
| DATA/SEARCH (07, 31) | Store healthy; governance not deployed; Wazuh unbacked; deletion misses cold copies |
| API (08) | Contract-first and tested; boundary gaps; P0 committed credentials |
| TEST/CI/BP (09, 10, 34) | Edge suite strong; falcon lacks a unit loop; no branch protection (plan limits) |
| SC/SBOM (11, 35) | Dependencies pinned; scanner blind spots; no license gate |
| INFRA/CTR/SECRET (12, 36, 38) | Deployable stronger than docs; estate outgrew certification; credential concentration/reuse |
| RES/OBS/NOTIF/DR/IR (13, 14, 30, 32, 33) | Working delivery; cannot detect its own death; backups partly proven; no monitoring-loss scenario |
| PERF/PRIV/EVOL/AI/HYGIENE (15, 18–21) | Capacity-constrained; synthetic claim contradicted; instruction layer stale |
| EVID/XREPO/FLEET/DQ (41–44) | Mechanics strong; approval boundary fails; pairing broken; update not power-loss safe; DLQ blind to sink errors |

## Detailed Review

### Theme: Release binding and approval chain

- Evidence: `PRODUCTION_VERDICT.md` lines 8–20; `PACKAGE_DIGEST.txt`; `FINAL_RESPONSE.json`; `generate_final_response.py:65-66`; `REVIEW_REPORT_2026-09-29.md` line 3; `decision_log.md` JPB rows; `git show 6f3c2e4`.
- Missing: verdict↔delivery equality, reviewer provenance, separation of gate flips from approvals, derived (non-hardcoded) fields. Risks: an approval consumers cannot reproduce; unreviewed rebuilds self-approve by inheritance.
- Fix/tests/docs: condition C1; CI equality test; provenance fields; contradiction-ledger entries.

### Theme: Operational detection and recovery truth

- Evidence: `heartbeat.sh` direct-to-ntfy; relay is the single hop; 26 h watcher; no rule consumes watcher age, textfile mtime, guard free space, swap, or scrape errors; offsite metric absent; recovery capture 0-byte at HEAD; silent IRIS skip; retention deletes by stale inventories.
- Missing: end-to-end canary, staleness rules, offsite/new-services metrics, retained-union retention, exercised reclaim. Risks: undetected alert-path death; stale cold tier shown green; unrecoverable key/IRIS state.
- Fix/tests/docs: conditions C4/C5; blind-ops and alert-path-recovery runbooks.

### Theme: Edge trust ladder, secrets, and capacity

- Evidence: R1–R4 reproductions (ADV lens); `service.py:196-203,333,399`; `pki.py`; `falcon-apply-update.sh:76-96`; secrets archive contents (names only); baked device credentials; zero `falcon_edge_*` rules; `FLEET-P1-002`; guard text 5 vs 10 GiB; `reclaims_total 0`.
- Risks: token/lost device → fleet control; power-cut update bricks the agent; spoofed telemetry defeats detection; root/data exhaustion before reclaim lands.
- Fix/tests/docs: conditions C6/C7; CI negative tests R1–R4; edge trust-model doc; sanctioned reclaim drill.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EXEC-001 | Current state | Reports 01–44; live snapshot | Validators, ledgers, probes | Release binding broken | P0 | C1/C3 |
| EXEC-002 | Strengths | Manifests/chain/edge tests | Real evidence discipline | Not binding to approval | P2 | Preserve; formalize |
| EXEC-003 | Biggest risks | 11 P0 findings | Existing automation | Detection/governance gaps | P0 | C2/C4/C5 |
| EXEC-004 | Release blockers | Approval, pin, credentials | Gate ledger | APPROVED unreproducible | P0 | C1–C3 |
| EXEC-005 | Business/security/ops impact | Secret exposure; dead-man; backup | Lab-scope controls | Owner decisions pending | P1 | Owner decisions; blind-ops |
| EXEC-006 | Investment recommendation | Scoped, cited fixes | None | Sequencing | P2 | Fund conditions only |
| EXEC-007 | Next actions | Recommendations in reports | Prior gate C1–C10 | Low closure rate | P1 | Condition-led execution |
| EXEC-008 | Risk counts/themes | `findings.json` (256) | Machine-readable | New ADV themes unalerted | P2 | Track to closure |

## Findings

### Finding ID: EXEC-P1-001 - No prior-run P0 is verified-fixed and the open P0 set grew from 6 to 11

- Severity: P1
- Confidence: High
- Area: EXEC (run-to-run closure)
- Evidence:
  - Prior `RELEASE_GATE.md` (run `20260930-0320`) conditions C1–C10 and its P0 list
  - Current status tables: prior INTG-P0-001 still open (now INV-P0-001/XREPO-P0-001); INTG-P0-002 partially fixed; LIVE-P0-001…004 all `partially-fixed`; `findings.json` now P0×13 vs prior P0×6
- What is happening: several causes were fixed (offsite `.env`, WG persistence, noise tune), but detectors, bindings, and evidence remain open; no prior P0 reached `verified-fixed`.
- Why it matters: a condition-driven gate cannot graduate while closure is not evidence-bound.
- User / business impact: repeated cycles with the same release blockers; false confidence from partially fixed causes.
- Security / privacy / reliability impact: silent alert/backup loss paths and an unearned approval persist.
- Recommended fix: verification-only pass per fixed finding; close only with current-commit artifacts.
- Suggested validation: verification log where every closed condition cites a post-fix capture.
- Owner suggestion: owner + maintainers
- Effort estimate: M
- Dependencies: C8; owner decisions (EXEC-P1-002)
- Status: open

### Finding ID: EXEC-P1-002 - Several closure-critical decisions are owner-only and still pending

- Severity: P1
- Confidence: High
- Area: EXEC (governance dependency)
- Evidence:
  - Reviewer identity/JPB provenance (report 41, REV lens); D-007 edge alert rules (XREPO/INTG/OBS); secret/backup-key custody (`DR-P1-004`); retention vs cold-offload and reclaim (`LIVE`/`PERF`); total-loss threshold (RES/OBS); branch-protection plan limits (report 34, R-012)
- What is happening: fixes for C1, C4, C5, and C6 depend on decisions only the owner can make; they remain open questions.
- Why it matters: the gate's critical path is owner time, not code.
- User / business impact: release conditions cannot be scheduled honestly until decisions are recorded.
- Security / privacy / reliability impact: custody and detection targets remain undefined.
- Recommended fix: record the six decisions in `decision_log.md` with owners; attach each to a condition.
- Suggested validation: each condition's "done when" names a decision-log row.
- Owner suggestion: owner
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Shipped credentials abused | P0 | Medium | Account/resource compromise | API-P0-001 | C2 rotate/redact/rebuild |
| Approval relied on for unreviewed bytes | P0 | Certain | Governance/release failure | EVID-P0-001, REV-P0-001 | C1 rebind/re-review |
| Alert-path death unnoticed | P0 | Low–Med | Missed security/ops events | LIVE-P0-001, RES-P0-002 | C4 canary + freshness |
| Silent cold-tier staleness | P0 | Medium | Data-protection loss | LIVE-P0-002, RES-P0-001 | C5 metrics + retention fix |
| Pin/sidecar mispairing recurs | P0 | High | Wrong release verified | INV-P0-001, XREPO-P0-001 | C3 immutable rebind + verifier |
| Token→operator / root update chain exploited | P1 | Medium | Fleet compromise | ADV-P1-001/002 | C6 tests + redesign |
| Root/data exhaustion | P1 | Medium | Platform outage | PERF-P1-001/002 | C7 reclaim + drill |

## Recommendations

### Immediate / Release Blocking
1. Rotate exposed Wazuh credentials; redact with SHA-256 entries; rebuild package + delivery; make the scanner XML/64-hex aware (C2).
2. Re-review/rebind the approval to the delivered commit, or deliver an immutable package rebuilt from the reviewed commit (C1); separate gate flips from approvals.
3. Freeze the edge release; regenerate the sidecar atomically; rebind the pin; add the pin verifier to CI (C3).

### This Week
4. Offsite/new-services gauges + 36 h rules; commit the recovery capture; retained-union retention; fail on a missing IRIS dump (C5).
5. Relay canary on the independent instance + watcher/textfile/timer/swap/scrape-error rules; stop-test the threshold (C4).
6. Deploy edge rules through the Grafana path (not `deploy_edge_alert_rules.sh --apply` as written) (C6).

### This Month
7. Edge trust ladder: server-pinned CSR subjects, separate operator issuance/revocation, signed/symlink-safe root apply, crash-safe update, cert-bound ingest (C6).
8. Root reclaim plan + ≥90% page; data warning band; sanctioned guard drill (C7); verification pass and current-state docs (C8). Later: one binding subsystem for both programs — content-addressed releases, acceptance by digest, derived status, skew detection, paired rollback.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Include N/A in the phase-9 aggregate | Aggregate sums to 14 rows | `publish_digests.sh` | Recount |
| Regenerate the sidecar atomically | Sidecar verifies | delivery dir | `sha256sum -c` |
| Scanner allowlist for audit revision IDs | First documented command goes green | `secret_scan.py` | `ci/validate.py` with run folder |
| Watcher-age + offsite rules | Dead monitors and stale cold tier become visible | `90-alerting.sh`, `export_monitor_metrics.sh` | Stop timer/probe → fires |
| Fix guard alert text (5 vs 10 GiB) | Operator acts on the real threshold | `disk_guard.sh` | Text diff |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Release-binding subsystem (verdict↔package↔archive) | P0 | release engineer + owner | M | reviewer availability |
| Versioned immutable edge releases + pin verifier | P0 | edge release engineer | M | freeze decision |
| XML-aware secret scanning + rotation | P0 | security owner | S | key rotation |
| Alert-path canary + freshness rules | P0 | falcon maintainer + owner | M | DO access |
| Edge trust-ladder redesign + negative tests | P1 | edge maintainer | M | PKI redesign |
| Capacity reclaim + guard drill | P1 | falcon maintainer | M | maintenance window |
| Joint recovery/rebind runbook + offsite PKI | P1 | both maintainers | M | key custody |

## Suggested Tests

- Unit: verdict fields derive from one source (no literals); phase-9 aggregate includes N/A and sums to rows.
- Integration/CI: `verify_edge_pin.sh` fails closed on a mutated pin; verdict digests = digest file = shipped archive; scanner fixtures for XML-tag 64-hex and planted secrets.
- E2E: extract the delivered archive and run every review-record command verbatim (zero path corrections); paired-release drill where pin = manifest = deployed digest = edge commit.
- Failure drills: stop the relay → independent canary ≤ threshold; break the Spaces probe → offsite alert; stop each timer → one staleness alert; power-cut the edge update in QEMU → boot recovers.
- Security/regression + manual: R1–R4 reproductions fail after the fix; revoked-sensor ingest rejected and alarmed; non-root read-only walk of every incident runbook; blind-ops walkthrough with dashboards blocked.

## Suggested Documentation Updates

- New: `docs/CURRENT_STATE.md` (both repos), `docs/edge/INTERFACES.md`, `docs/edge/PAIR_RECOVERY_AND_REBIND.md`, runbooks `ALERT_PATH_RECOVERY`, `BLIND_OPERATIONS`, `NOTIFICATION_AND_DEADMAN`.
- Update: README/AGENTS current state and safe-vs-mutating sections; `REPOSITORY.md` manifest/pin semantics; `VPN.md` + port matrix (5182, peer `.30`); edge trust model/revocation semantics; contradiction ledgers for every delta in this report.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does a JPB-produced disposition artifact exist off-repo? | Independence validity | External file/signature |
| Was the delivered 2026-09-30 archive reviewed by anyone? | Gate scope for shipped bytes | Reviewer record for `3ac6cd4` |
| Which artifact is authoritative for external parties, and have the exposed keys been rotated? | Consumer clarity; rotation urgency | Owner decision record; rotation log |

## Appendix

- Counts: P0×13, P1×80, P2×131, P3×40 (264 across 36 areas; includes 8 synthesis findings). The 13 P0s: API-P0-001; EVID-P0-001/002; FINAL-P0-001/002; INV-P0-001/002; LIVE-P0-001/002; RES-P0-001/002; REV-P0-001; XREPO-P0-001.
- Audit-wiring hazard (cross-ref REV-P2-002/ND-P2-001, filed by the REV lens): full 40-hex SHAs in this run's reports make `python3 ci/validate.py` exit 1 (`FAIL secret scan findings`) while the folder is present; allowlist `docs/audits/**` benign revision IDs or omit full SHAs before wiring.
- Reconciliation deltas vs machine artifacts: digest `APPROVED` vs `FINAL_RESPONSE.json` `IE`; verdict binds `c312ab7` vs delivery `3ac6cd4`; pin `dffcbbb7…`/sidecar `18681751…` vs manifest `3fa4a49c…`; scanner `NO_FINDINGS` vs literal XML-tag credentials; gate aggregate omits one N/A row.
- Method/redaction: read-only; reproductions in `/tmp/opencode` sandboxes; no secret values printed (paths/types/lengths only); no repo/ledger/gate/delivery/live mutation. The run folder itself is written into the audited tree — see EXEC-P2-001.
