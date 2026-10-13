# 18_privacy_compliance_data_governance — Prompt 18 - Privacy, Compliance, and Data Governance Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `18_privacy_compliance_data_governance.md` (area PRIV, prompt)

## Verification Performed

# Privacy, Compliance, and Data Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d` (short `08e20d1`)
- Branch: `main` (target pinned at 08e20d1; the clone's `main` ref now points at `6e4fccd` and `ops/20261009-snapshot-repo-relocate-clean` at `c13a416` — both used only as post-audit context, never as the audited tree)
- Generated at: 2026-10-09T21:50:40Z · Auditor: repo-deep-dive subagent (prompt 18) · Area code: PRIV
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/18_privacy_compliance_data_governance.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo password read from the owner file in a subshell, never printed); no state mutated; no formal compliance claimed — SOC2/ISO27001/NIST/CIS/OWASP/GDPR/CCPA/HIPAA/PCI/CMMC are used as readiness lenses only. Edge-repository surfaces (sensor images, edge delivery directory, edge SQLite store) are outside this repository and are referenced through owner-action C13. Owner/legal inputs remain outstanding by design (A6/C3) and are reported, not invented.


## Scope

Reviewed at commit `08e20d1`: personal/sensitive data in the monitoring streams (Suricata EVE, flows, syslog, Wazuh, edge telemetry), auth/audit records, admin actions, billing/payment references (none), uploaded docs/evidence, user content (case data, owner-device telemetry), export/deletion, retention, consent/cookie flows (N/A), policies/terms, access controls, encryption assumptions, backups, incident response, vendor data inventory and data-processing integrations.

Not reviewed: upstream internals; live data-subject requests; processor-side controls (DigitalOcean/Cloudflare/GitHub); legal sufficiency of the owner/legal inputs; edge-repository surfaces (edge delivery directory, sensor images) — tracked via `docs/phase9/OWNER_ACTIONS.md` C13.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/privacy/DATA_GOVERNANCE.md` | doc | Controller/processor map, data classes, flows, open owner/legal inputs | Written 2026-10-02; legal row empty (`:19`, `:47-54`) |
| `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` | doc | Classification, prohibited payloads, live-state reconciliation | Phase-0 baseline kept; `:4` still says synthetic-only; `:49-71` records the live deltas |
| `docs/runbooks/RETENTION_MATRIX.md` | doc | Per-class retention and mechanisms | Wazuh `:23` and IRIS `:43` are explicit GAPs |
| `config/opensearch/falcon-*-ism-policy.json` | config | Actual deletion policies | eve 14 d, topqueries 14 d, auditlog 30 d, ISM history 30 d, test 1 d |
| `bootstrap/60-central-deploy.sh:216-233` | code | Audit REST enablement | Live `opensearch.yml:47` `plugins.security.audit.config.enable_rest: true` |
| `automation/evidence/capture.sh:1-13,82-98` | code | Evidence-capture credential handling | sudo value read in a subshell only; PRIV-P1-002 fix present |
| `ledgers/redactions.md` | ledger | Redaction record (20+ rows, original hashes kept) | Last row 2026-10-03 |
| `docs/security/{BREACH_NOTIFICATION_PROCEDURE,CUSTODY_ATTESTATION,CREDENTIAL_ROTATION_REGISTER}.md` | docs | Incident, custody, rotation readiness | Breach procedure written but not exercised; rotation 20/20 PENDING (`:12`) |
| `PACKAGE_DIGEST.txt`, `docs/phase9/review/PRODUCTION_VERDICT.md`, `docs/CURRENT_STATE.md:53`, `docs/phase9/OWNER_ACTIONS.md:32` | artifacts | Governance-artifact binding | Verdict binds a superseded package; C1 OPEN |
| `docs/phase9/OWNER_ACTIONS.md:35,74`, `docs/phase9/OWNER_INPUTS_REQUIRED.md` | records | Owner/legal inputs | A6 (privacy authority), C3 (legal/processor inputs) |
| `mct/VENDORING.md`, `mct/client-onboarding/*` | docs | Vendored third-party layer | Archive-only policy; client files are templates/placeholders |

## Verification Performed

| Check | Type | Observed result |
|---|---|---|
| `python3 ci/validate.py` (documented Track-A step) | reproduce | `validation_failures=0` — incl. `secret scan PASS`, `digest binding PASS`, `credential sourcing PASS` (no script sources `/home/user/.env`) |
| `bash automation/validation/verify_publication_chain.sh` | reproduce | `publication_chain_failures=0` |
| `automation/evidence/capture.sh` re-read | inspect | The wrapper reads only `sudo` in a subshell and feeds it over stdin (`:82-98`); PRIV-P1-002 verified fixed at this commit |
| Live: `docker exec falcon-central-opensearch-1 grep audit.config.enable_rest opensearch.yml` | live read-only | `plugins.security.audit.config.enable_rest: true` (line 47) |
| Live: `curl _plugins/_security/api/internalusers` as `falcon-healthcheck` | live read-only | HTTP 403 (`no permissions for [cluster:admin/opendistro/ism/policy/search]` on the ISM API) — least-privilege reader role is real |
| Live: `docker exec falcon-central-grafana-1 env` | live read-only | `GF_ANALYTICS_*` disabled (see AN report) |
| Retention policies in-tree | inspect | Only `falcon-*` classes have ISM; Wazuh indexer and IRIS have none (`RETENTION_MATRIX.md:23,43`) |
| Redaction claims vs artifacts | inspect | `ledgers/redactions.md` rows carry original SHA-256; tree scan clean at this commit |

## Executive Summary

The governance core is strong and materially improved since the 2026-09-30 audit: a controller/processor map and data-class inventory exist (`docs/privacy/DATA_GOVERNANCE.md`), the retention matrix is per-class and names its gaps, audit logging is live with a 30-day ISM policy, the evidence-capture wrapper no longer exports the credential file (verified fixed), the secret scan is clean at this commit, and backups are encrypted with an owner custody attestation and a rehearsed restore. The open risks are the known owner/legal residuals, not new defects: (1) the Wazuh indexer estate and IRIS case data still have **no retention or deletion window** (owner-gated; tracked as DATA-P1-001/SEARCH-P2-001); (2) the owner/legal inputs (entity, DPA status, jurisdiction notice, device scope) remain outstanding and the classification doc still carries the contradicted "synthetic-only" line; (3) the published production verdict still binds a superseded package and keeps a `NOT_SUPPORTED` readiness line while `PACKAGE_DIGEST.txt` says APPROVED (C1 OPEN); (4) the vendored MCT client/vendor layer has no privacy-classification boundary recorded in this repo. Recommended next actions: close the retention decision (owner), record the D7 authority wording in both classification docs, complete C1 rebind, and record the MCT privacy boundary.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Data classes / identifiers | `docs/privacy/DATA_GOVERNANCE.md:23-32` | Class inventory | Implemented | Low | Owner-device class documented as PRIV-P1-001 follow-up |
| Retention matrix | `docs/runbooks/RETENTION_MATRIX.md` | Per-class windows | Implemented; 2 GAPs | High | Wazuh/IRIS gaps owner-gated |
| Audit logs | `security-auditlog-*`, ISM `falcon-auditlog-policy` (30 d) | Admin/auth traceability | Live + retained | Low | REST audit enabled live |
| Auth records | OpenSearch internal users, mTLS roles, ntfy users | Authentication | Per-service, least privilege | Medium | `.env` monolith residual owner-accepted (SECRET-P2-002) |
| Evidence redaction | `automation/evidence/capture.sh`, `ledgers/redactions.md` | Prevent credential capture | Implemented; fixed | Low | Original hashes kept |
| Backups/encryption | `bootstrap/85/86/92`, `docs/security/CUSTODY_ATTESTATION.md` | DR + key custody | Encrypted; attestation recorded | Low | Restore rehearsal 2026-10-01/02 |
| Breach procedure | `docs/security/BREACH_NOTIFICATION_PROCEDURE.md` | Incident notification | Written; **not exercised** | Medium | Every clock value OWNER-INPUT |
| Processors | `docs/privacy/DATA_GOVERNANCE.md:10-19` | Vendor inventory | Partial | Medium | MCT/vendor stack not mapped |
| MCT client layer | `mct/client-onboarding/*`, `mct/VENDORING.md` | Vendored third-party program | Archive-only; templates | Medium | No privacy boundary recorded |
| Export/deletion | ISM policies; `docs/phase7/runbooks/RESTORE.md` | Deletion + recovery | Per-class for central; GAPs | High | No DSAR path (lab scope) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Personal/sensitive data | 3 | `DATA_GOVERNANCE.md`, `RETENTION_MATRIX.md` | Owner-device scope/authority wording; classification doc says synthetic-only | Record D7 wording in both docs |
| Auth records | 3 | OS internal users; live 403 least-privilege check | Lifecycle/rotation 20/20 pending (SECRET-P2-001) | Execute rotation (owner) |
| Audit logs | 4 | Live REST audit + 30 d ISM | Retention for admin-only indices verified in repo only | Keep; add deletion evidence per class |
| Admin actions | 3 | REST audit; decision log; evidence captures | Some owner steps host-only | Extend captures |
| Billing/payment refs | N/A | Self-hosted lab; no billing code found | — | None |
| Uploaded docs | 3 | Evidence tree + redaction ledger; package excludes secrets | IRIS attachments unclassified | Add to retention/classification |
| User content | 2 | IRIS case data live; owner-device telemetry | No retention/backup decision for case data | Owner decision C1/E-3 |
| Export/deletion | 3 | ISM delete policies; restore drill | Wazuh/IRIS have no deletion window | Implement retention |
| Retention | 2 | `RETENTION_MATRIX.md` | 2 explicit GAPs | Owner decision |
| Consent/cookie flows | N/A | No first-party web surface (AN report) | — | Revisit if a portal is added |
| Policies/terms | 2 | Breach procedure; threat model | Entity/DPA/notice owner-legal inputs | C3 owner input |
| Access controls | 3 | 0600 secrets; least-privilege live check | `.env` holds several credential classes (owner-accepted) | Split per class (SECRET-P2-002) |

## Detailed Review

### Item: Data classes and classification

- Evidence: `docs/privacy/DATA_GOVERNANCE.md:23-32`; `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:10-29,49-71`.
- What it does / how it works: classifies EVE/flow/syslog/Wazuh/edge/case/identity/secret data; the classification doc is the Phase-0 baseline with dated update sections that record the live state (flows land in `falcon-eve-*`, audit in `security-auditlog-*`, template `dynamic:false` with 75 pinned properties).
- Missing controls: the "synthetic; no real user traffic" line at `:4` contradicts the live owner-device data documented in `DATA_GOVERNANCE.md:29` and `RETENTION_MATRIX.md:50-51`; the device/site scope is still an open input.
- Risks: a reviewer can misread the collection basis. Recommended: apply the D7 wording (owner-authorized, metadata-only) in both docs.

### Item: Retention and deletion

- Evidence: `docs/runbooks/RETENTION_MATRIX.md:11-43`; `config/opensearch/falcon-eve-ism-policy.json` (14 d delete), `falcon-auditlog-ism-policy.json` (30 d), `falcon-ism-history-ism-policy.json` (30 d), `falcon-topqueries-ism-policy.json` (14 d), `falcon-test-cleanup-ism-policy.json` (1 d); `docs/phase7/runbooks/RESTORE.md:350`.
- Current controls: central index classes are bounded and machine-generated from the ISM policy files; DLQ is bounded (30 d / 64 MiB, `disk_guard.sh`); Prometheus 30 d; ntfy 48 h.
- Missing controls: Wazuh indexer estate has **no ISM policy** (`:23`) and IRIS case data/downloads have **no retention** (`:43`), so there is no deletion guarantee for potentially sensitive case/security data. Owner decision tracked as DATA-P1-001/SEARCH-P2-001 (owner-accepted / still-open) and owner-action C1.
- Risks: unbounded growth plus an unbounded privacy window. Recommended: decide retention (suggested Wazuh alerts 90 d / statistics 30 d; IRIS lifecycle TBD) and implement.

### Item: Auth/audit records and admin actions

- Evidence: live `opensearch.yml:47` audit REST enabled; `falcon-auditlog-policy` 30 d; `docs/runbooks/ACCESS_AND_ACCOUNTS.md`; live 403 least-privilege check.
- Current controls: per-service identities with least privilege (verified 403 on the security/ISM APIs for the healthcheck reader), append-only ledgers for admin actions, evidence captures.
- Missing: no SSO/human lifecycle (lab scope); credential rotation 20/20 pending (tracked SECRET-P2-001).

### Item: Redaction and evidence hygiene

- Evidence: `automation/evidence/capture.sh` (subshell sudo read; redaction filters for OSSEC/WG/ntfy/password forms); `ledgers/redactions.md`; `ci/validate.py` secret scan PASS.
- Current controls: fixed since 2026-10-01; no script sources the owner credential file (gate PASS); redactions keep original hashes.
- Residual: 20/20 inherited credentials still pending rotation (other domain).

### Item: Backups, encryption, custody

- Evidence: `bootstrap/80-offsite-backup.sh`, `85-backup-job.sh`, `86-wazuh-indexer-backup.sh`, `92-cold-copy.sh`; `docs/security/CUSTODY_ATTESTATION.md`; restore rehearsal 2026-10-01/02 (1.47 M docs in 21 s).
- Current controls: encrypted offsite (Spaces), encrypted edge-secrets set, owner custody attestation, rehearsed decrypt/restore. Residual: IRIS dump coverage fail-loud fix pending (owner E-3).

### Item: Processors, policies, consent

- Evidence: `docs/privacy/DATA_GOVERNANCE.md:10-19` (DigitalOcean, Cloudflare, GitHub, self-hosted ntfy + push service, UniFi, Microsoft 365), `:47-54`; `docs/security/BREACH_NOTIFICATION_PROCEDURE.md`.
- Missing: entity/DPA/notice values (OWNER/LEGAL-INPUT); the MCT vendor/integration stack (IRIS live; MISP/Velociraptor/Greenbone/Security Onion staged or VM-side) is not in the processor table; consent/cookie flows are N/A (no first-party web surface — see AN report).

### Item: Export/deletion

- Evidence: ISM delete policies; `docs/runbooks/R2_COLD_TIER.md`; `automation/validation/retention_execution_test.sh`.
- Current controls: per-class delete for central classes, cold-tier copy before ISM deletion, deletion execution test exists. Missing: Wazuh/IRIS deletion window; no data-subject export path (not applicable to the lab; would be an owner/legal input for production).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| PRIV-001 | Personal/sensitive data | `DATA_GOVERNANCE.md:23-32` | Classes + prohibitions | Owner-device scope/authority wording | P2 | Record D7 wording (PRIV-P3-001) |
| PRIV-002 | Auth records | `ACCESS_AND_ACCOUNTS.md`; live 403 | Least privilege | Rotation pending | P2 | Execute rotation (SECRET-P2-001) |
| PRIV-003 | Audit logs | Live REST audit; ISM 30 d | Enabled + retained | — | P3 | Keep; add per-class deletion evidence |
| PRIV-004 | Admin actions | Ledgers; captures | Append-only records | Host-only steps | P3 | Extend captures |
| PRIV-005 | Billing/payment refs | No billing code in repo | N/A | — | — | None |
| PRIV-006 | Uploaded docs | Evidence tree; redactions | Secret exclusion + redaction | IRIS attachments unclassified | P2 | Add to classification/retention |
| PRIV-007 | User content | IRIS live; owner devices | Case-data row exists | No lifecycle | P1 | Retention decision (PRIV-P1-001) |
| PRIV-008 | Export/deletion | ISM; restore | Per-class delete | Wazuh/IRIS gap | P1 | Implement retention |
| PRIV-009 | Retention | `RETENTION_MATRIX.md` | Matrix authoritative | 2 GAPs | P1 | Owner decision |
| PRIV-010 | Consent/cookie | AN report | N/A (no first-party surface) | — | — | Revisit on portal |
| PRIV-011 | Policies/terms | Breach procedure | Procedure exists | Entity/DPA/notice | P2 | C3 owner input |
| PRIV-012 | Access controls | 0600 secrets; live check | Least privilege | `.env` monolith (accepted) | P2 | Split per class |

## Findings

### PRIV-P1-001 - Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated)

- Severity: P1
- Confidence: High
- Area: PRIV
- Evidence:
  - `docs/runbooks/RETENTION_MATRIX.md:23` ("Wazuh alerts/archives/inventory/statistics ... **none configured (GAP)** ... indices grow unbounded (audit PRIV-P2-002 residual)")
  - `docs/runbooks/RETENTION_MATRIX.md:43` ("IRIS case DB / downloads | **no retention (GAP)** | manual; owner decision for case-data lifecycle")
  - `docs/phase7/runbooks/RESTORE.md:350` ("IRIS case DB | no | local volume only | unbounded | **OPEN**")
  - `docs/phase9/OWNER_ACTIONS.md:72` (C1: decide Wazuh-estate + IRIS retention; "no default for IRIS")
  - Prior-run register `runs/falcon-20261005-full-main-e267ce1/follow_up_register.md` rows DATA-P1-001 / SEARCH-P2-001 (owner-accepted / still-open; 2026-10-09 capacity note: snapshot repo relocated, data LV 87%→60%; retention decision itself remains owner-gated)
- What is happening: security data (Wazuh indexer estate) and case data (IRIS) are retained indefinitely; no ISM/lifecycle policy exists for either store, so there is no bounded deletion guarantee.
- Why it matters: unbounded retention of security/case data is both a storage-growth problem and a privacy/data-minimization failure; the 2026-10-09 capacity incident (data-LV watermarks) is a direct symptom on the Wazuh side.
- User / business impact: storage pressure and privacy exposure if the environment is promoted as-is.
- Security / privacy / reliability impact: data minimization failure; reactive capacity management.
- Recommended fix: owner decides and records the windows (suggested: Wazuh alerts 90 d / statistics 30 d via an ISM policy on the indexer cluster; IRIS lifecycle TBD), then implement and document in `RETENTION_MATRIX.md`; add an accelerated deletion test per class.
- Suggested validation: ISM policy present on the Wazuh indexer; documented IRIS window; index counts stabilize; deletion evidence captured.
- Owner suggestion: owner (data/privacy) + ops · Effort: L · Dependencies: owner decision (C1)
- Status: still-open (owner-gated)
- Endpoint / data path: Wazuh manager → indexer `wazuh-*` (no lifecycle); IRIS app → case DB volumes (no lifecycle)
- Attack path: none identified

### PRIV-P2-001 - The vendored MCT client/vendor layer has no privacy-classification boundary in this repository

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `docs/privacy/DATA_GOVERNANCE.md:10-19` (processors listed: DigitalOcean, Cloudflare, GitHub, ntfy, UniFi, Microsoft 365 — the MCT integration/vendor stack is absent)
  - `docs/privacy/DATA_GOVERNANCE.md:30` (only "Case data | IRIS cases, notes, uploaded artefacts")
  - `mct/client-onboarding/*` (client intake/authorization templates and phase records; first-client files are placeholders — "NO CLIENT", "TEMPLATE")
  - `mct/VENDORING.md:3-7,50-78` (archive-only policy; subtree not classified for privacy)
  - Prior finding: 20261002 run PRIV-P2-001 (same issue)
- What is happening: the repository vendors an 856-file MCT subtree that includes client-onboarding records and integrations (IRIS live; MISP/Velociraptor/Greenbone/Security Onion staged or VM-side), but the governance page does not state the privacy boundary for that content or its vendors.
- Why it matters: a reviewer cannot determine from this repo which third-party/personal data the vendored layer may hold or which processors are in scope; onboarding a real client would immediately create unclassified processing.
- User / business impact: blocks a clean production/privacy review of the client program.
- Security / privacy / reliability impact: unassessed processor risk; misdirected retention/minimization decisions.
- Recommended fix: record the privacy boundary in `docs/privacy/DATA_GOVERNANCE.md` (vendored archive-only; MCT program owns client-data classification) and in `docs/runbooks/MCT_CONSOLIDATION.md`; extend the processor table if any MCT integration is revived.
- Suggested validation: governance doc names the MCT boundary; reviewer walkthrough of each live integration.
- Owner suggestion: falcon maintainer + MCT owner · Effort: M · Dependencies: owner decision (E-2/E-3)
- Status: partially-fixed (governance page exists; MCT boundary still unrecorded)
- Attack path: none identified

### PRIV-P2-003 - The published production verdict still binds a superseded package and carries a contradictory readiness line

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `docs/phase9/review/PRODUCTION_VERDICT.md:8-14` (Repository commit `c312ab7`; package manifest `4476fc93…`; **1,168 entries**)
  - `docs/phase9/review/PRODUCTION_VERDICT.md:31` ("Production readiness: `NOT_SUPPORTED` until the mandatory gates pass")
  - `PACKAGE_DIGEST.txt:2,6-7,12` (`repository_commit=69b3c80…`; manifest `5f591655…`; **3,783 entries**; `production_readiness=APPROVED …`)
  - `docs/CURRENT_STATE.md:53` (C1 "OPEN (reviewer artifact pending)")
  - `docs/phase9/OWNER_ACTIONS.md:32` (A3: "Published verdict keeps binding a superseded package with a contradictory `NOT_SUPPORTED` line; consumers misinformed")
  - Prior finding: 20260930 run PRIV-P2-003 / DOC-P2-004 (same issue)
- What is happening: the signed verdict describes a different (older) artifact set than the current digest, and its readiness line contradicts the digest's APPROVED and the current-state page's APPROVED. The C1 re-review/rebind is still open.
- Why it matters: reviewers and consumers cannot map the approval to the delivered data-handling configuration; the artifact pair is not self-consistent.
- User / business impact: assurance integrity weakened; a strict reviewer cannot reproduce the binding.
- Security / privacy / reliability impact: unreviewed configuration can carry the approved label.
- Recommended fix: at C1, regenerate the verdict from the ledgers per the template (identity block from `PACKAGE_DIGEST.txt`; readiness wording corrected) and publish the reviewer disposition + owner adoption; keep the old record as history.
- Suggested validation: CI consistency test binding verdict ↔ digest ↔ manifest ↔ HEAD (the digest/verdict consistency test exists; extend it to the verdict binding fields).
- Owner suggestion: reviewer + owner (C1/A3) · Effort: S · Dependencies: reviewer disposition
- Status: still-open (owner-gated)
- Attack path: none identified

### PRIV-P3-001 - Owner/legal privacy inputs and notice/processor artifacts remain outstanding; the "synthetic-only" wording persists

- Severity: P3
- Confidence: High
- Area: PRIV
- Evidence:
  - `docs/privacy/DATA_GOVERNANCE.md:19,49-54` (owner/legal row empty; DPA status, jurisdiction statements and the owner-device scope are open inputs)
  - `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:4` ("Lab traffic is synthetic; no real user traffic is captured") vs `docs/runbooks/RETENTION_MATRIX.md:50-51` ("PRIV-P1-001 corrected the earlier 'synthetic-only' claim") and `docs/privacy/DATA_GOVERNANCE.md:29` (owner-device telemetry live)
  - `docs/phase9/OWNER_ACTIONS.md:35` (A6) and `:74` (C3: no default — OWNER/LEGAL-INPUT)
  - `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/owner_decisions.md` D7 (APPROVED 2026-09-30; "wording updates routed")
  - Prior finding: 20260930 run PRIV-P3-001 (same class)
- What is happening: the owner granted monitoring authority for the owner's own devices/sites (metadata-only) on 2026-09-30, but the written scope, the classification-doc wording update, and the entity/DPA/notice inputs are still outstanding.
- Why it matters: readiness lenses (GDPR Art. 28/30; CCPA notices) need a processor/notice record; the docs currently contradict each other on the collection basis.
- Recommended fix: apply the D7 wording in both classification docs, record the device/site scope in `DATA_GOVERNANCE.md`, and complete C3 with the owner/legal inputs (or explicitly accept the lab-scope limitation).
- Suggested validation: both docs carry the same scope statement; processor list complete.
- Owner suggestion: owner/legal · Effort: S–M · Dependencies: owner/legal input
- Status: open (owner-gated)

## Prior-Run Comparison

- Prior full run `falcon-20261005-full-main-e267ce1` (target `e267ce1`) emitted **no PRIV findings**; its same-domain report noted: "Data governance is documented (docs/privacy/DATA_GOVERNANCE.md, architecture/DATA_FLOW_AND_CLASSIFICATION.md); the retention enforcement gap is tracked under DATA-P1-001/SEARCH. No independent finding." This run keeps that reconciliation but re-emits the retention gap in the PRIV domain (as the 20261002 run did with PRIV-P1-001) because it is squarely in the PRIV scope.
- Lineage checks at `08e20d1`:
  - `PRIV-P1-002` (capture wrapper exported the credential file) — **verified-fixed**: `automation/evidence/capture.sh:1-13,82-98` reads only `sudo` in a subshell; `ci/validate.py` credential-sourcing check PASS.
  - `PRIV-P2-002` (audit/DLQ retention missing) — **verified-fixed for central classes**: `security-auditlog-*` 30 d, `top_queries-*` 14 d, ISM history 30 d, test 1 d, DLQ bounded (30 d / 64 MiB). The remaining Wazuh/IRIS gap is re-emitted as PRIV-P1-001.
  - `PRIV-P2-003` (digest vs verdict binding) — **still-open** (re-emitted).
  - `PRIV-P1-001` (real-device telemetry authority) — **partially-fixed**: D7 approved 2026-09-30; residual re-emitted as PRIV-P3-001.
  - `PRIV-P3-001` (identifier inventory / processor artifacts) — **partially-fixed**: `DATA_GOVERNANCE.md` exists; residual re-emitted as PRIV-P3-001 and PRIV-P2-001.
  - Edge-side items (20260930 PRIV-P2-001 delivery-dir key concentration; PRIV-P3-002 manifest public key) — **out of this repo**; tracked in `docs/phase9/OWNER_ACTIONS.md` C13 (edge owner actions).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Wazuh/IRIS data retained indefinitely | P1 | High | Privacy + capacity | `RETENTION_MATRIX.md:23,43` | Owner retention decision + ISM |
| Verdict binds a superseded package | P2 | Medium | Assurance integrity | `PRODUCTION_VERDICT.md:8-14,31` | C1 rebind |
| MCT vendor/client layer unclassified | P2 | Medium | Privacy review blocked | `DATA_GOVERNANCE.md:10-19` | Record boundary |
| Owner/legal inputs outstanding | P2 | Medium | Production promotion blocked | `OWNER_ACTIONS.md:35,74` | C3/A6 |
| Inherited credentials unrotated | P2 | Medium | Exposure window | `CREDENTIAL_ROTATION_REGISTER.md:13` | Rotation (SECRET-P2-001) |

## Recommendations

### Immediate / Release Blocking

1. Owner retention decision for Wazuh + IRIS (C1) — PRIV-P1-001.

### This Week

2. C1 verdict rebind and readiness-line correction — PRIV-P2-003.
3. Record the D7 authority wording in both classification docs — PRIV-P3-001.

### This Month

4. Record the MCT privacy boundary (PRIV-P2-001).
5. Complete C3 owner/legal inputs (entity, DPA status, notice).
6. Execute the inherited-credential rotation (SECRET-P2-001).

### Later / Platform Evolution

7. If a client portal/marketing surface is ever added, apply the AN future-readiness checklist (consent + minimization + vendor inventory).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the synthetic-only wording | Removes a direct doc contradiction | `DATA_FLOW_AND_CLASSIFICATION.md:4`; `DATA_GOVERNANCE.md:29` | Grep for "synthetic"; scope statement consistent |
| Add the MCT boundary paragraph | Makes the privacy boundary reviewable | `DATA_GOVERNANCE.md`; `mct/VENDORING.md` | Reviewer walkthrough |
| Correct the verdict readiness line at rebind | Removes a contradictory status | `PRODUCTION_VERDICT.md` (regenerated) | Digest/verdict consistency test |

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
- Governance: CI assertion that `PRODUCTION_VERDICT.md` identity fields equal `PACKAGE_DIGEST.txt` (extend `tests/digest_verdict_consistency_test.sh`).
- Evidence: capture-wrapper fixture proving `--sudo -- env` exposes no credential value (exists; keep).
- Manual: reviewer walkthrough of each processor entry.

## Suggested Documentation Updates

- `docs/privacy/DATA_GOVERNANCE.md` — apply D7 scope; add the MCT boundary and any revived integrations.
- `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` — replace the synthetic-only line with the D7 basis while keeping the historical table.
- `docs/runbooks/RETENTION_MATRIX.md` — update when the Wazuh/IRIS decision lands.
- `docs/security/BREACH_NOTIFICATION_PROCEDURE.md` — exercise and fill owner/legal clocks when production is considered.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What retention/RPO does the owner choose for Wazuh and IRIS? | Closes the deletion window | Owner decision (C1) |
| Which personal devices/sites are in scope? | Bounds the processing | D7 execution note |
| Will the MCT program onboard a real client? | Determines vendor classification urgency | E-2/E-3 decision |
| Is a production DSAR/export path required? | Production readiness | Owner/legal input |

## Limitations / Appendix

- Live observations at 2026-10-09T21:19-21:40Z (read-only): root LV 83% used (the OpenSearch snapshot repo now lives on the root LV after the 2026-10-09 relocation), data LV 55%; `falcon-backup.service` in failed state in the snapshot while the backup/offsite stamps advanced (backup 16:49:51Z, offsite 19:01:37Z); repeated vector OOM kills in the journal — these are operational conditions for the OBS/RES domains, recorded here for completeness only.
- The ISM policy list could not be read live with the least-privilege healthcheck identity (HTTP 403), which is itself evidence that the role separation works; retention evidence is repo-side plus prior-run live evidence.
- No data-subject request, processor-side control or legal sufficiency was exercised; those remain `unverified`.

## Findings

| ID | Severity | Title |
|---|---|---|
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| PRIV-P2-001 | P2 | Vendored MCT client/vendor layer has no privacy-classification boundary in this repository |
| PRIV-P2-003 | P2 | Published production verdict still binds a superseded package and carries a contradictory readiness line |
| PRIV-P3-001 | P3 | Owner/legal privacy inputs and notice/processor artifacts outstanding; the 'synthetic-only' wording persists |
