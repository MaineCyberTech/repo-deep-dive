# 18_privacy_compliance_data_governance — Prompt 18 - Privacy, Compliance, and Data Governance Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `18_privacy_compliance_data_governance.md` (area PRIV, prompt)

## Verification Performed

# Privacy, Compliance, and Data Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (short `f5cb7c9`)
- Branch: `main` · Generated at: 2026-10-11T04:33Z · Auditor: repo-deep-dive subagent (prompt 18) · Area code: PRIV
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/18_privacy_compliance_data_governance.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo value read from the owner file in a subshell, never printed); no state mutated; no formal compliance claimed — SOC2/ISO27001/NIST/CIS/OWASP/GDPR/CCPA/HIPAA/PCI/CMMC are used as readiness lenses only. The live Wazuh-indexer ISM API was not re-verified in this pass (no non-mutating credential path from the host; the dashboard user lacks ISM permission — 403 observed); Wazuh-estate evidence is repo-side plus prior-run live evidence. Owner/legal inputs remain outstanding by design (A6/C3) and are reported, not invented.

## Scope

Reviewed at `f5cb7c9`: personal/sensitive data in the monitoring streams (Suricata EVE, flows, syslog, Wazuh, edge telemetry), auth/audit records, admin actions, billing/payment references (none found), uploaded docs/evidence, user content (IRIS case data, owner-device telemetry), export/deletion, retention, consent/cookie flows (N/A), policies/terms, access controls, encryption assumptions, backups, incident response, vendor data inventory and data-processing integrations.

Not reviewed: upstream internals; live data-subject requests; processor-side controls (DigitalOcean/Cloudflare/GitHub); legal sufficiency of the owner/legal inputs; edge-repository surfaces (tracked via `docs/phase9/OWNER_ACTIONS.md` C13).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/privacy/DATA_GOVERNANCE.md` | doc | Controller/processor map, data classes, flows, open owner/legal inputs | Written 2026-10-02; owner/legal row empty (`:19`, `:47-54`); MCT stack absent from processors (`:10-19`) |
| `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` | doc | Classification, prohibited payloads, live-state reconciliation | `:4` still says "Lab traffic is synthetic; no real user traffic is captured" (contradicted by `DATA_GOVERNANCE.md:29`, `RETENTION_MATRIX.md:50-51`) |
| `docs/runbooks/RETENTION_MATRIX.md` | doc | Per-class retention and mechanisms | Wazuh `:23` and IRIS `:43` remain explicit GAPs |
| `config/opensearch/falcon-*-ism-policy.json` | config | Actual deletion policies (central cluster) | eve 14 d, topqueries 14 d, auditlog 30 d, ISM history 30 d, test 1 d |
| Live central OpenSearch `_plugins/_ism/policies` (admin, in-container, read-only) | live | Confirm deletion policies exist live | 7 policies: falcon-{eve,auditlog,topqueries,ism-history,test-cleanup}-policy + one-off exec + legacy mon-eve-policy |
| Live `opensearch.yml:47` audit config | live | Admin/auth traceability | `plugins.security.audit.config.enable_rest: true` |
| Live `falcon-healthcheck` identity | live | Least-privilege verification | `_plugins/_security/api/internalusers` → HTTP 403; `_cluster/health` → HTTP 200 |
| `docs/phase9/review/PRODUCTION_VERDICT.md`, `PACKAGE_DIGEST.txt`, `docs/CURRENT_STATE.md`, `docs/phase9/OWNER_ACTIONS.md` | artifacts | Governance-artifact binding | Verdict binds `c312ab7` / manifest `4476fc93…` / 1,168 entries / `NOT_SUPPORTED`; digest binds `3c11752` / `749dae85…` / 3,830 entries / `APPROVED`; C1 OPEN |
| `docs/security/CREDENTIAL_ROTATION_REGISTER.md`, `BREACH_NOTIFICATION_PROCEDURE.md` | docs | Auth lifecycle and incident readiness | Rotation 20/20 PENDING; breach procedure not exercised, every clock OWNER-INPUT |
| `mct/VENDORING.md`, `mct/client-onboarding/*` | docs | Vendored third-party layer | Archive-only policy; client files are templates/placeholders |
| `automation/evidence/capture.sh`, `ledgers/redactions.md` | code/ledger | Evidence redaction | Capture wrapper reads only `sudo`; redaction ledger current through 2026-10-04 |

## Verification Performed

| Check | Type | Observed result |
|---|---|---|
| `python3 ci/validate.py` (Track A gate) | reproduce | `validation_failures=0` — includes secret scan PASS and credential-sourcing PASS |
| `bash automation/validation/verify_publication_chain.sh` | reproduce | `publication_chain_failures=0`; digests bind the declared commit `3c11752` |
| Live central ISM policy list (read-only, in-container admin) | live | 7 policies; no Wazuh/IRIS class present on the central cluster (those estates are separate stores) |
| Live OpenSearch REST audit setting | live | `audit.config.enable_rest: true` (`opensearch.yml:47`) |
| Live least-privilege check (`falcon-healthcheck`) | live | 403 on the security API; 200 on cluster health — role separation is real |
| Retention matrix vs repo ISM files | inspect | Central classes bounded; Wazuh indexer estate and IRIS case data have no policy in-tree |
| Verdict vs digest binding fields | inspect | Still mismatched (see PRIV-P2-003) |
| Wazuh-indexer live ISM | live (attempted) | Not verified — dashboard user lacks `cluster:admin/opendistro/ism/policy/search` (403); no non-mutating admin path used |

## Executive Summary

The governance core remains strong: a controller/processor map and class inventory exist, the central retention classes are machine-generated ISM policies (live-verified, 7 policies), audit logging is enabled live with a 30-day policy, evidence redaction is enforced by the hardened capture wrapper and a clean secret scan, and backups are encrypted with a recorded custody attestation. All four prior-run PRIV findings persist at `f5cb7c9` and are the known owner/legal and artifact-binding residuals, not new defects: (1) the Wazuh indexer estate and IRIS case data still have **no retention or deletion window** (owner-gated; owner-accepted); (2) the vendored MCT client/vendor layer still has **no recorded privacy-classification boundary**; (3) the published production verdict still **binds a superseded package** (`c312ab7`/1,168 entries) and keeps a contradictory `NOT_SUPPORTED` readiness line while `PACKAGE_DIGEST.txt` at `f5cb7c9` binds `3c11752`/3,830 entries/`APPROVED` (C1 OPEN; the A3 `FINAL_RESPONSE.json` residual is now fixed — digest and closeout agree); (4) owner/legal inputs and the D7 wording update remain outstanding and the classification doc still carries the contradicted "synthetic-only" line. Recommended next actions: close the C1 rebind, decide the Wazuh/IRIS retention (C1 owner action), record the MCT boundary, and apply the D7 wording to both classification docs.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Data classes / identifiers | `docs/privacy/DATA_GOVERNANCE.md:23-32` | Class inventory | Implemented | Low | Owner-device class documented |
| Retention matrix | `docs/runbooks/RETENTION_MATRIX.md` | Per-class windows | Implemented; 2 GAPs | High | Wazuh/IRIS owner-gated |
| Audit logs | `security-auditlog-*`, ISM 30 d | Admin/auth traceability | Live + retained | Low | REST audit enabled live |
| Auth records | OpenSearch internal users, mTLS roles, ntfy users | Authentication | Per-service, least privilege | Medium | Rotation 20/20 pending (SECRET-P2-001) |
| Evidence redaction | `automation/evidence/capture.sh`, `ledgers/redactions.md` | Prevent credential capture | Implemented | Low | Secret scan clean |
| Backups/encryption | `bootstrap/85/86/92`, `CUSTODY_ATTESTATION.md` | DR + key custody | Encrypted; attestation recorded | Low | Restore rehearsal 2026-10-01/02 |
| Breach procedure | `docs/security/BREACH_NOTIFICATION_PROCEDURE.md` | Incident notification | Written; not exercised | Medium | Every clock OWNER-INPUT |
| Processors | `docs/privacy/DATA_GOVERNANCE.md:10-19` | Vendor inventory | Partial | Medium | MCT/vendor stack not mapped |
| Export/deletion | ISM policies; `docs/phase7/runbooks/RESTORE.md` | Deletion + recovery | Per-class for central; GAPs | High | IRIS case DB OPEN (`RESTORE.md:350`) |

## Findings

### PRIV-P1-001 — Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated)

- Severity: P1 · Confidence: High · Status: owner-accepted (unchanged)
- Evidence: `docs/runbooks/RETENTION_MATRIX.md:23` (Wazuh alerts/archives/inventory/statistics: "none configured (GAP)"), `:43` (IRIS case DB / downloads: "no retention (GAP)"); `docs/phase7/runbooks/RESTORE.md:350` (IRIS case DB unbounded, OPEN); `docs/phase9/OWNER_ACTIONS.md:72` (C1: decide Wazuh-estate + IRIS retention; "no default for IRIS"); live central ISM list confirms no policy covers those estates (they live on separate stores).
- What is happening: security data (Wazuh indexer estate) and case data (IRIS) are retained indefinitely; no ISM/lifecycle policy exists for either store, so there is no bounded deletion guarantee.
- Why it matters: unbounded retention of security/case data is a data-minimization failure and a capacity risk; the 2026-10-09 capacity work relieved pressure but did not create a deletion window.
- Recommended fix: owner decides and records the windows (suggested Wazuh alerts 90 d / statistics 30 d via an ISM policy; IRIS lifecycle TBD), implement, document in `RETENTION_MATRIX.md`, add an accelerated deletion test per class.
- Status: owner-accepted (register 2026-10-11: owner-accepted, unchanged).

### PRIV-P2-001 — The vendored MCT client/vendor layer still has no privacy-classification boundary in this repository

- Severity: P2 · Confidence: High · Status: open
- Evidence: `docs/privacy/DATA_GOVERNANCE.md:10-19` (processors: DigitalOcean, Cloudflare, GitHub, ntfy, UniFi, M365 — MCT stack absent), `:30` (only "Case data | IRIS cases, notes, uploaded artefacts"); `mct/client-onboarding/*` (templates/placeholders, no client); `mct/VENDORING.md:3-7,50-78` (archive-only policy; no privacy classification).
- What is happening: the vendored MCT subtree includes client-onboarding records and integrations (IRIS live; MISP/Velociraptor/Greenbone/Security Onion staged or VM-side) but the governance page does not state the privacy boundary for that content or its vendors.
- Why it matters: a reviewer cannot determine from this repo which third-party/personal data the vendored layer may hold; onboarding a real client would immediately create unclassified processing.
- Recommended fix: record the boundary (vendored archive-only; MCT program owns client-data classification) in `DATA_GOVERNANCE.md` and `MCT_CONSOLIDATION.md`; extend the processor table when an integration is revived.
- Status: open (same issue as the prior full run).

### PRIV-P2-003 — The published production verdict still binds a superseded package and carries a contradictory readiness line

- Severity: P2 · Confidence: High · Status: open (C1)
- Evidence: `docs/phase9/review/PRODUCTION_VERDICT.md:8-14` (commit `c312ab7`; manifest `4476fc93…`; 1,168 entries), `:31` ("Production readiness: `NOT_SUPPORTED` until the mandatory gates pass"), and the 2026-10-01 state note (28 alert rules superseded; now 86 live); `PACKAGE_DIGEST.txt` at `f5cb7c9` (repository_commit `3c11752`; manifest `749dae85…`; 3,830 entries; `production_readiness=APPROVED`); `docs/CURRENT_STATE.md:53` (C1 OPEN — reviewer artifact pending; `C1_REVIEW_REPORT.md` is still an unsigned template); `docs/phase9/OWNER_ACTIONS.md:32` (A3).
- What is happening: the signed verdict describes a different (older) artifact set than the current digest and its readiness line contradicts the digest's APPROVED and the current-state page's APPROVED. The C1 re-review/rebind is still open.
- Why it matters: reviewers and consumers cannot map the approval to the delivered data-handling configuration; the artifact pair is not self-consistent.
- Recommended fix: at C1, regenerate the verdict from the ledgers per the template (identity block from `PACKAGE_DIGEST.txt`; corrected readiness wording) and publish the reviewer disposition + owner adoption; extend `tests/digest_verdict_consistency_test.sh` (today it checks digest ↔ `FINAL_RESPONSE.json` only) to the verdict binding fields.
- Status: open (the A3 `FINAL_RESPONSE.json` stale-binding residual is fixed at this commit — closeout and digest agree on `3c11752`; the verdict rebind itself remains).

### PRIV-P3-001 — Owner/legal privacy inputs and the "synthetic-only" wording remain outstanding

- Severity: P3 · Confidence: High · Status: open
- Evidence: `docs/privacy/DATA_GOVERNANCE.md:19,49-54` (owner/legal row empty; DPA status, jurisdiction statements and the owner-device scope open); `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:4` ("Lab traffic is synthetic; no real user traffic is captured") vs `docs/runbooks/RETENTION_MATRIX.md:50-51` and `DATA_GOVERNANCE.md:29` (owner-device telemetry live); `docs/phase9/OWNER_ACTIONS.md:35` (A6) and `:74` (C3: no default — OWNER/LEGAL-INPUT); D7 approved 2026-09-30.
- What is happening: the owner granted monitoring authority for the owner's own devices/sites (metadata-only) on 2026-09-30, but the written scope, the classification-doc wording update, and the entity/DPA/notice inputs are still outstanding.
- Recommended fix: apply the D7 wording in both classification docs, record the device/site scope, and complete C3 with owner/legal inputs (or explicitly accept the lab-scope limitation).
- Status: open (owner-gated).

## Prior-Run Comparison

- Prior full run `falcon-20261009-2117-full-08e20d1` (target `08e20d1`) emitted four PRIV findings: PRIV-P1-001 (retention), PRIV-P2-001 (MCT boundary), PRIV-P2-003 (verdict binding), PRIV-P3-001 (owner/legal + wording). All four are re-emitted unchanged at `f5cb7c9`; the 2026-10-11 verification register dispositions (owner-accepted / open / open / open) are confirmed.
- Previously fixed PRIV findings were re-checked and show no regression: PRIV-P1-002 (capture wrapper no longer exports the credential file — `capture.sh` single-key read; `ci/validate.py` credential-sourcing PASS) and PRIV-P2-002 (central audit/DLQ retention — live ISM policies present).
- Post-08e20d1 changes reviewed (PRs #49–#54): capacity close-out, wg0 narrowing, alerting 77→86, ntfy internal-only, backup retry, tunnel ingress set falcon/iris/enroll, Wazuh proxy listener alert. None closes a PRIV finding. The A3 `FINAL_RESPONSE.json` stale-binding residual is fixed (closeout/FINAL_RESPONSE.json now carries `3c11752` and agrees with the digest).
- No new PRIV issues were identified at this commit.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Wazuh/IRIS data retained indefinitely | P1 | High | Privacy + capacity | `RETENTION_MATRIX.md:23,43` | Owner retention decision + ISM |
| Verdict binds a superseded package | P2 | Medium | Assurance integrity | `PRODUCTION_VERDICT.md:8-14,31`; `PACKAGE_DIGEST.txt` | C1 rebind |
| MCT vendor/client layer unclassified | P2 | Medium | Privacy review blocked | `DATA_GOVERNANCE.md:10-19` | Record boundary |
| Owner/legal inputs outstanding | P2 | Medium | Production promotion blocked | `OWNER_ACTIONS.md:35,74` | C3/A6 |
| Inherited credentials unrotated | P2 | Medium | Exposure window | `CREDENTIAL_ROTATION_REGISTER.md` (20/20 PENDING) | Rotation (SECRET-P2-001) |

## Recommendations

### Immediate / Release Blocking
1. Owner retention decision for Wazuh + IRIS (C1) — PRIV-P1-001.

### This Week
2. C1 verdict rebind and readiness-line correction — PRIV-P2-003.
3. Record the D7 authority wording in both classification docs — PRIV-P3-001.

### This Month
4. Record the MCT privacy boundary — PRIV-P2-001.
5. Complete C3 owner/legal inputs; execute the inherited-credential rotation (SECRET-P2-001).

### Later / Platform Evolution
6. If a client portal/marketing surface is added, apply the AN future-readiness checklist (consent + minimization + vendor inventory).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the synthetic-only wording | Removes a direct doc contradiction | `DATA_FLOW_AND_CLASSIFICATION.md:4`; `DATA_GOVERNANCE.md:29` | Grep for "synthetic"; scope statement consistent |
| Add the MCT boundary paragraph | Makes the privacy boundary reviewable | `DATA_GOVERNANCE.md`; `mct/VENDORING.md` | Reviewer walkthrough |
| Correct the verdict readiness line at rebind | Removes a contradictory status | `PRODUCTION_VERDICT.md` (regenerated) | Extend digest/verdict consistency test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Wazuh/IRIS retention + ISM | P1 | owner + ops | L | Owner decision C1 |
| Verdict rebind | P2 | reviewer + owner | S | Reviewer disposition |
| MCT privacy boundary | P2 | maintainer | M | E-2/E-3 |
| Legal/processor inputs | P2 | owner/legal | S | C3 |
| IRIS attachments classification | P2 | owner + ops | M | E-3 |

## Suggested Tests

- Retention: accelerated ISM deletion test per class (pattern exists: `automation/validation/retention_execution_test.sh`); Wazuh-indexer ISM dry-run; IRIS lifecycle test.
- Privacy: fixture asserting the classification docs state the same collection basis (no "synthetic-only" while real feeds are documented).
- Governance: extend `tests/digest_verdict_consistency_test.sh` to `PRODUCTION_VERDICT.md` identity fields vs `PACKAGE_DIGEST.txt` (today it covers digest ↔ closeout only).
- Evidence: capture-wrapper fixture proving `--sudo -- env` exposes no credential value (exists; keep).

## Suggested Documentation Updates

- `docs/privacy/DATA_GOVERNANCE.md` — apply D7 scope; add the MCT boundary.
- `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` — replace the synthetic-only line with the D7 basis.
- `docs/runbooks/RETENTION_MATRIX.md` — update when the Wazuh/IRIS decision lands.
- `docs/security/BREACH_NOTIFICATION_PROCEDURE.md` — exercise and fill owner/legal clocks before production is considered.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What retention does the owner choose for Wazuh and IRIS? | Closes the deletion window | Owner decision (C1) |
| Which personal devices/sites are in scope? | Bounds the processing | D7 execution note |
| Will the MCT program onboard a real client? | Determines vendor classification urgency | E-2/E-3 decision |
| Is a production DSAR/export path required? | Production readiness | Owner/legal input |

## Limitations / Appendix

- Live observations at 2026-10-11T04:20–04:35Z (read-only): central ISM has 7 policies (falcon-* classes + one-off exec + legacy mon-eve-policy); OpenSearch REST audit enabled; `falcon-healthcheck` least-privilege verified (403 security API / 200 health). The Wazuh-indexer ISM list could not be read without elevated credentials (dashboard user 403); the Wazuh/IRIS retention gap is evidenced repo-side (`RETENTION_MATRIX.md`, `RESTORE.md`) and from prior-run live work, and is marked owner-gated.
- No data-subject request, processor-side control or legal sufficiency was exercised; those remain `unverified`.
- Cross-refs (other domains, not re-filed here): IRIS is publicly routed at `iris.mainecybertech.us` behind Cloudflare Access with an owner-IP bypass (documented in `MCT_CONSOLIDATION.md:73-89`; ADMIN/CHAIN domains track the origin-auth posture); credential rotation 20/20 pending (SECRET-P2-001); breach procedure unexercised (IR-P2-001).

## Findings

| ID | Severity | Title |
|---|---|---|
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| PRIV-P2-001 | P2 | The vendored MCT client/vendor layer still has no privacy-classification boundary in this repository |
| PRIV-P2-003 | P2 | The published production verdict still binds a superseded package and carries a contradictory readiness line |
| PRIV-P3-001 | P3 | Owner/legal privacy inputs and the 'synthetic-only' wording remain outstanding |
