# Privacy, Compliance, and Data Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab v1.0.0 (pack v1.2.1)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` · Repos: `/home/user/falcon-build` @ `8282d3f` (clean) · `/home/user/falcon-edge-build` @ `45dfed0` (dirty — in-flight CI)
- Generated at: 2026-09-30 (UTC) · Auditor: repo-deep-dive subagent (prompt 18) · Area code: PRIV
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/18_privacy_compliance_data_governance.md` · Scope limitations: read-only account; live view = `live_snapshot.txt`; prior-run ES/IRIS/Wazuh query depth reused where re-query was not possible. Per `profiles/falcon-lab.md` §4 this prompt is **ADAPTED** to **monitoring-data governance**: redaction, retention, personal data in logs, published-artifact hygiene. No formal compliance is claimed; SOC2/ISO27001/NIST/OWASP/GDPR/CCPA are readiness lenses only.

## Scope

Reviewed: personal/identifying data in monitoring streams (Suricata, flows, syslog, Wazuh, edge telemetry), auth/audit records, retention/deletion, redaction (ingest, evidence, delivery), secrets hygiene around published artifacts, backups, access controls, classification docs, vendor touchpoints, export/deletion. Not reviewed: upstream internals; live ES content this run; processor-side controls; legal sufficiency. Consent/cookie flows are N/A (no first-party surface; prompt 39).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md`; edge `docs/phase0/DATA_FLOW_AND_CLASSIFICATION.md`; `config/vector/{aggregator,edge}.yaml`; `automation/evidence/capture.sh` (both repos) | policy/config/code | Classes, retention, deletion; ingest redaction; GeoIP; DLQ; evidence redaction | Flow row stale; edge retentions proposed; `set -a; . .env` still present |
| `ledgers/redactions.md` (20 rows); `docs/security/SCANNER_ALLOWLIST_CHANGES.md`; `secret_scan.py`; edge `.gitleaks.toml`; `phase4_data_checks.sh:33-56`; `bootstrap/60-central-deploy.sh:204-215` | records/code/config | Redaction/scanner governance; ISM retention; audit REST | Original hashes kept; only `falcon-eve-*` has ISM |
| `bootstrap/{85-backup-job,80-offsite-backup}.sh`; `backup_edge_secrets.py`; `/home/user/falcon-edge-delivery/*`; `falcon-edge-release-manifest-20260930.json` | code/artifacts | Backup encryption; published-artifact hygiene | Offsite encrypted; edge secret files + hashes in delivery |
| `docs/runbooks/{ACCESS_AND_ACCOUNTS,OPERATOR_START_HERE,CAPACITY_AND_TELEMETRY}.md`; `docs/phase9/OWNER_INPUTS_REQUIRED.md`; `PACKAGE_DIGEST.txt`; `PRODUCTION_VERDICT.md`; `review-package/MANIFEST.sha256`; prior run `20260930-0320-…` | docs/artifacts/records | Real-device telemetry; pending authority; binding coherence; prior findings | OD-14 **REQUESTED**; prior IDs checked below |

## Verification Performed

| Check | Type | Why relevant | Notes |
|---|---|---|---|
| REV-P3-010 delivery/secret hygiene; REV-P3-011 capture env export | reproduce | Verify at current commits | **both still-open**: delivery dir holds `*-ssh-key`, `*-credentials.txt`, `falcon-edge-secrets-backup-*.tar.gz` (0600; signed 42-artifact manifest lists names + SHA-256; `backup_edge_secrets.py` writes plain `tar.gz`); `capture.sh:69-71` (both repos) does `set -a; . "$ENV_FILE"; set +a`, unsetting only `sudo` |
| LIVE-P2-005 secrets hygiene; LIVE-P2-002 retention | inspect | Verify at current commits | **both still-open**: `/home/user/.env` 0600 but still holds sudo password + Cloudflare/DO Spaces/GitHub/UniFi/WiFi keys (names only); only `falcon-eve-*` ISM (14d) while audit REST is enabled with no `security-auditlog-*` retention |
| ND-P1-001 digest derivation; REV-P1-003 verdict contradiction; `secret_scan.py` over repo trees and `review-package/`; edge `falcon-logs/`; edge MAC hashing | inspect/read/reproduce | Verify fixes; hygiene claims | Digest now derived and matches ledgers but README/AGENTS stale; verdict says `NOT_SUPPORTED` alongside 101 PASS/APPROVED; tree clean except 5 allowlisted-path hits in `sbom/vuln/*.json`; package `NO_FINDINGS`; logs have no private-key blocks; `collectors.py:167-168` HMAC-SHA256 site salt |

## Executive Summary

Strong governance exists at the artifact core: classification docs with a prohibited list, ingest credential redaction, an evidence wrapper with a maintained redaction ledger (original hashes kept), a content-addressed secret scanner, review packages that exclude secrets and scan clean, encrypted offsite backups, 0600 secret files, and MAC pseudonymization on edge inventory. The central risks are that **the governance narrative lags the live system** and **credential hygiene at the edges is weaker than artifact hygiene at the centre**: live real-device telemetry contradicts the "synthetic-only" claim while privacy authority (OD-14) remains REQUESTED; both capture wrappers export the whole credential file into captured commands; the edge delivery directory concentrates private keys and unencrypted secrets backups (enumerated by hash in the signed manifest); retention covers one index class; and the digest/verdict bind different artifact sets. Fixes: capture env leak, real-data authorization, then delivery-surface and retention gaps.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Data classification (central/edge) | `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md`; edge `docs/phase0/…` | Classes, retention, deletion | Partial/stale; edge proposed | Medium | Live syslog/Wazuh/GeoIP under-mapped |
| Ingest/evidence redaction; secret scanning | `config/vector/{aggregator,edge}.yaml`; `capture.sh`; `ledgers/redactions.md`; `secret_scan.py`; `.gitleaks.toml` | Strip identifiers/credentials; prevent commits | Implemented | Medium | Credential-focused only; env export issue |
| Retention | `phase4_data_checks.sh:33-56`; Prometheus 30d; ntfy 48h | Deletion windows | One index class only | High | Audit/DLQ/IRIS/Wazuh uncovered |
| Backups/published artifacts | `85-backup-job.sh`; `80-offsite-backup.sh`; `backup_edge_secrets.py`; `review-package/`; edge manifest | Snapshots; reviewer/operator delivery | Offsite encrypted; edge backup plain; binding drift | Medium | Key-concentration risk |
| Auth/audit records; access/policies | OS audit REST; Wazuh alerts; ledgers; `ACCESS_AND_ACCOUNTS.md`; mTLS roles; threat model | Traceability; authn/authz; governance | Enabled; per-service; no SSO; scattered | Medium | No unified retention; no notice/processor list |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Personal/sensitive data | 2 | Live UniFi/Wazuh data; partial classification | Authorization pending; stale classes | Record OD-14 or stop real-data ingest |
| Auth records / audit logs / admin actions | 3 | OS users; mTLS; ntfy auth; OS audit REST; ledgers; adoption | No SSO/lifecycle; no retention/access policy; host-only steps | Document accounts; ISM + owner; extend captures |
| Billing/payment refs | 0 | N/A self-hosted | — | None |
| Uploaded docs / user content | 2 | Packages/evidence; delivery dir; device logs; Wazuh data | No upload DLP; keys in dir; minimization undefined | Vault split; classify identifiers |
| Export/deletion | 3 | ISM delete test; restore | Only eve class | Per-class deletion tests |
| Retention | 2 | 14d eve; 30d Prom; 48h ntfy | Audit/DLQ/IRIS/Wazuh gaps | Consolidate retention matrix |
| Consent/cookie + policies/terms | 0/2 | N/A (prompt 39); threat model; owner acceptance | No notice/subprocessor list | Publish notice; revisit on portal |
| Access controls | 3 | 0600 secrets; least-privilege roles | `.env` monolith; shared enroll token | Split per-service secrets |

## Detailed Review

### Item: Monitoring data classes and personal-data content

- Evidence: classification docs; `config/vector/aggregator.yaml:30-36,71-80` (GeoIP); live UniFi/Wazuh data documented in `OPERATOR_START_HERE.md`, `CAPACITY_AND_TELEMETRY.md`.
- What it does: indexes device syslog (device names/MACs/possibly usernames), Wazuh alerts, flow 5-tuples, Suricata metadata; edge heartbeats/inventory (MAC hashed) and wireless metadata (hashed).
- Current controls / missing / risks: payload/credential prohibitions; per-site HMAC; ingest redaction; 14-day ISM on `falcon-eve-*`. Missing: legal basis for real-device data; identifier columns; per-class deletion. Record OD-14 authorization or quarantine real feeds; update both tables; add a known MAC/device canary deletion test.

### Item: Redaction and published-artifact hygiene

- Evidence: `capture.sh` (both); `ledgers/redactions.md`; `secret_scan.py`; `build_review_package.sh` (excludes `secrets/`, SBOMs); edge manifest.
- What it does: redacts credential-like patterns from captures/device logs; excludes secrets from review packages; scanned clean; edge identifiers hashed; 20 recorded redactions with original hashes.
- Missing / recommended: env export in captures; delivery-dir key material; manifest hashes for secret files; no public verification key. Fix wrapper env handling; vault delivery secrets; encrypt edge backups; ship the public key; add env-dump and delivery-dir CI tests.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| PRIV-001 | Personal/sensitive data | Classification docs; live feeds | Classes + prohibited list | Authorization pending; stale classes | P1 | PRIV-P1-001 |
| PRIV-002 | Auth records | OS users; mTLS; ntfy | Per-service auth | Lifecycle/SSO | P2 | Document + rotate |
| PRIV-003 | Audit logs | OS audit REST; ledgers | Enabled | No retention | P2 | ISM + owner |
| PRIV-004 | Admin/billing refs | Ledgers; adoption; N/A self-hosted | Append-only | Host-only steps | P3 | Extend captures |
| PRIV-006 | Uploaded docs | Package; delivery dir | Central excludes secrets | Edge dir keys | P2 | Vault split |
| PRIV-007 | User content | Device syslog/Wazuh | Credential redaction | No minimization policy | P3 | Classify identifiers |
| PRIV-008 | Export/deletion | ISM test; restore | Delete for eve | Other stores undefined | P2 | Per-store deletion |
| PRIV-009 | Retention | ISM/Prom/ntfy configs | Three caps defined | Audit/DLQ/IRIS gaps | P2 | Retention matrix |
| PRIV-010/011 | Consent/cookie; policies/terms | Prompt 39 N/A; threat model; acceptance | None/Internal | Notice/processor list | P3 | Publish notice; revisit on portal |
| PRIV-012 | Access controls | 0600 files; roles | Least privilege | `.env` monolith | P2 | Split secrets |

## Findings

### Finding ID: PRIV-P1-001 - "Synthetic traffic" privacy claim is contradicted by live real owner-device telemetry, with privacy authority still pending

- Severity: P1
- Confidence: High
- Area: PRIV
- Evidence: `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:4` ("synthetic; no real user traffic") and `:24-25` (OD-14 pending; no production data may be ingested); same file update 2026-09-21(2) (UniFi fleet syslog live); `OPERATOR_START_HERE.md`/`CAPACITY_AND_TELEMETRY.md` (Wazuh fleet; named agents); `OWNER_INPUTS_REQUIRED.md` (privacy authority **REQUESTED**); `docs/phase7/CLOSEOUT.md` P7-G07 ("Only synthetic traffic captured")
- What is happening: governance records claim synthetic-only and defer authority while the pipeline ingests real device/endpoint data.
- Why it matters: personal data is processed without recorded authorization, retention, or data-subject handling.
- User / business impact: privacy/legal exposure if the environment is promoted as-is.
- Security / privacy / reliability impact: compliance and trust risk.
- Recommended fix: record monitoring authorization per site/device or quarantine real feeds with deletion; update both classification docs.
- Suggested validation: map each live feed to a recorded authorization and retention entry.
- Owner suggestion: owner / data authority · Effort estimate: M · Dependencies: owner decisions
- Status: still-open (P0-G06 INSUFFICIENT_EVIDENCE; P7-G07 lab-scoped).

### Finding ID: PRIV-P1-002 - Evidence-capture wrappers export the whole credential file into captured command environments (REV-P3-011)

- Severity: P1
- Confidence: High
- Area: PRIV
- Evidence: `/home/user/falcon-build/automation/evidence/capture.sh:69-75`; `/home/user/falcon-edge-build/automation/evidence/capture.sh:64-75` (`set -a; . "$ENV_FILE"; set +a`; only `unset sudo`); `/home/user/.env` (0600; sudo + Cloudflare/DO Spaces/GitHub/UniFi/WiFi/prox_key/ntfy credential classes — names only); redaction covers OSSEC/WG/ntfy/password patterns only
- What is happening: every `--sudo` capture runs its command with the full credential set exported.
- Why it matters: an `env`/crash dump or tool printing its environment writes credentials to `evidence/raw` unmasked.
- User / business impact: secret exposure and rotation churn.
- Security / privacy / reliability impact: credentials persist in long-lived, distributed artifacts.
- Recommended fix: read only the `sudo` value via subshell and feed stdin without exporting other variables.
- Suggested validation: `capture.sh --sudo -- env` fixture shows no credential value in both repos.
- Owner suggestion: falcon/edge maintainers · Effort estimate: S · Dependencies: none
- Status: still-open (verified at both current commits).

### Finding ID: PRIV-P2-001 - Edge delivery directory mixes private keys, credentials and unencrypted secrets backups with publishable artifacts; the signed manifest enumerates them by hash (REV-P3-010)

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence: `/home/user/falcon-edge-delivery/` (`…-lab8-ssh-key`, `…-lab8-credentials.txt`, `falcon-edge-secrets-backup-20260930T011054Z.tar.gz`, 0600, beside images/SBOMs); `falcon-edge-release-manifest-20260930.json` (42 artifacts incl. secrets backups/keys/credentials with SHA-256, ed25519-signed); `backup_edge_secrets.py` (plain `tar.gz` of CA key, signing seed, operator keys, sensor certs, control-plane DB)
- What is happening: the release/distribution directory doubles as the secret backup location, and the manifest publishes hashes and names.
- Why it matters: offline hash confirmation; unit copy of key material; plaintext backups expand the blast radius.
- User / business impact: device/CA compromise if the directory is shared.
- Security / privacy / reliability impact: key-custody hygiene.
- Recommended fix: dedicated vault outside the delivery surface; encrypt backups; scope the manifest to release artifacts.
- Suggested validation: delivery-dir CI policy; restore from the encrypted archive.
- Owner suggestion: edge maintainer · Effort estimate: M · Dependencies: key-custody decision
- Status: still-open (newer files 0600; location/manifest inclusion persist).

### Finding ID: PRIV-P2-002 - Retention defined for one index class only; audit logs and DLQ lack deletion policies (LIVE-P2-002)

- Severity: P2
- Confidence: Medium (repo evidence; prior live queries)
- Area: PRIV
- Evidence: `automation/validation/phase4_data_checks.sh:33-56` (ISM deletes `falcon-eve-*` after 14d only); `bootstrap/60-central-deploy.sh:204-215` (REST audit enabled, no retention); `config/vector/aggregator.yaml:106-111` (DLQ files, no expiry); prior run LIVE-P2-002 (`security-auditlog-*`, `top_queries-*`, ISM history, test indices unmanaged)
- What is happening: audit records (username/source IP) and pipeline rejects accumulate without a documented deletion policy.
- Why it matters: personal data outlives the declared window; storage growth.
- User / business impact: compliance/review exposure.
- Security / privacy / reliability impact: data minimization failure.
- Recommended fix: ISM templates for audit/DLQ/test indices; clean leftovers; one retention matrix.
- Suggested validation: accelerated retention test per policy (pattern exists).
- Owner suggestion: falcon maintainer · Effort estimate: M · Dependencies: none
- Status: still-open.

### Finding ID: PRIV-P2-003 - Published governance artifacts bind different artifact sets (digest vs production verdict); verdict keeps a contradictory readiness line

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence: `PACKAGE_DIGEST.txt` (`3ac6cd4`; 2,067 entries; manifest `0e5912…`; APPROVED); `PRODUCTION_VERDICT.md` (`c312ab7`; 1,168 entries; manifest `4476fc…`; "NOT_SUPPORTED until the mandatory gates pass"); `review-package/MANIFEST.sha256` (2,067; matches digest); prior ND-P1-001 (partially fixed), REV-P1-003 (still-open)
- What is happening: the authoritative digest and the signed verdict describe different packages; the readiness line contradicts APPROVED/all-PASS.
- Why it matters: reviewers cannot map the verdict to the data-handling configuration it approved.
- User / business impact: assurance integrity weakened.
- Security / privacy / reliability impact: unreviewed config can carry the approved label.
- Recommended fix: append-only verdict addendum binding the current package (or re-freeze the reviewed one); correct readiness text.
- Suggested validation: CI assertion that the verdict binding equals the current package manifest hash.
- Owner suggestion: release owner / reviewer · Effort estimate: S · Dependencies: reviewer
- Status: still-open (cross-ref FEAT-P1-002).

### Finding ID: PRIV-P3-001 - Governance documentation gaps: identifier inventory and processor/notice artifacts

- Severity: P3
- Confidence: High
- Area: PRIV
- Evidence: `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` (no MAC/username/geo columns for syslog/flows); `config/vector/aggregator.yaml:30-36,71-80` (GeoIP city/ASN enrichment); edge doc (MAC hashing for inventory only); `ACCESS_AND_ACCOUNTS.md` (Cloudflare, UniFi, level.io surfaces); `mct/client-onboarding/client-intake-form.md:49`; `bootstrap/{80-offsite-backup,95-cloudflared,97-cloudflare-api-config}.sh`; no privacy/DPA/subprocessor document found
- What is happening: live classes carry more identifiers than the tables state, and processors/notice artifacts are not consolidated.
- Why it matters: minimization/retention decisions depend on the identifier inventory; readiness lenses (GDPR Art. 28/30) need a processor list.
- User / business impact: over-retention risk and a production-promotion gap.
- Security / privacy / reliability impact: unassessed processor risk; misdirected privacy reviews.
- Recommended fix: extend both tables with identifier columns; create `docs/security/DATA_PROCESSORS.md` and a monitored-site notice template.
- Suggested validation: field census per index template; reviewer walkthrough of each processor.
- Owner suggestion: falcon maintainer / owner · Effort estimate: S · Dependencies: owner input
- Status: open.

### Finding ID: PRIV-P3-002 - Signed edge release manifest cannot be verified from the delivery set alone (no public key published) and signs hashes of secret files

- Severity: P3
- Confidence: High
- Area: PRIV
- Evidence: `falcon-edge-release-manifest-20260930.json` (`signature: ed25519`, `keyId 5ea52faf9cf6ee97`); delivery listing has no public key/certificate; prior review verified using the repo-side seed path (`closeout/REVIEW-2026-09-30.md` §3); prior REV-P3-009 class
- What is happening: an external recipient cannot verify the manifest without repo/key access; the manifest also anchors secret-file hashes.
- Why it matters: provenance verification is core to published-artifact integrity.
- User / business impact: recipients must trust transport, not cryptography.
- Security / privacy / reliability impact: weaker supply-chain assurance.
- Recommended fix: publish the ed25519 public key/keyId with the release; scope the manifest to release artifacts.
- Suggested validation: verify the delivered manifest on a clean host using only delivered files.
- Owner suggestion: edge maintainer · Effort estimate: S · Dependencies: none
- Status: still-open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Real-device data without recorded authorization | P1 | High | Privacy/legal exposure | PRIV-P1-001 | Record OD-14 or stop ingest |
| Credentials leak via captured env | P1 | Medium | Secret exposure | PRIV-P1-002 | Subshell-only sudo read |
| Delivery-dir key concentration | P2 | Medium | Key compromise | PRIV-P2-001 | Vault split + encryption |
| Audit/DLQ data outlives retention | P2 | High | Compliance/storage | PRIV-P2-002 | ISM per class |
| Verdict/package binding divergence; no processor inventory/notice | P2/P3 | Actual/Medium | Assurance integrity; readiness gap | PRIV-P2-003, PRIV-P3-001 | Addendum + CI binding; publish inventory/notice |

## Recommendations

**Immediate / release blocking:** (1) fix the capture env leak (PRIV-P1-002); (2) record real-data authorization or stop ingest (PRIV-P1-001).
**This week:** (3) move edge secrets out of the delivery directory + encrypt backups; (4) ISM retention for audit/DLQ/test indices; (5) verdict addendum + binding check.
**This month / later:** (6) extend classification tables; (7) processor inventory + notice; (8) ship the manifest public key; (9) per-store deletion matrix; (10) per-service secret files replacing `.env`.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Subshell sudo read | Closes env leak | `automation/evidence/capture.sh` (both) | `env` capture test |
| Encrypt edge secrets backup; publish manifest public key | Protects CA/keys; external verifiability | `backup_edge_secrets.py`; release tooling | Restore test; clean-host verify |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Capture wrapper env fix | P1 | falcon/edge maintainers | S | none |
| Real-data authorization record | P1 | owner/data authority | M | owner |
| Delivery vault split + backup encryption | P2 | edge maintainer | M | key decision |
| Retention matrix + ISM policies; verdict binding addendum | P2 | falcon maintainer / release owner | M/S | none / reviewer |
| Classification update; processor inventory/notice | P3 | falcon maintainer / owner | S | owner input |
| Public key publication | P3 | edge maintainer | S | none |

## Suggested Tests

- Security/privacy: `capture.sh --sudo -- env` fixture asserting no credential value reaches the artifact (both repos); deletion test per index class (reuse `retention_execution_test.sh`) incl. `security-auditlog-*` and DLQ.
- Governance/delivery: CI assertion that the digest equals `review-package/MANIFEST.sha256` and matches the verdict binding; CI content policy for `/home/user/falcon-edge-delivery` (no private keys, no plaintext secret archives).
- Regression/manual: `secret_scan.py` over `review-package/` + gitleaks on edge; walk every ingested feed to a recorded authorization/retention entry.

## Suggested Documentation Updates

- `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md`; edge phase-0 file — live classes, identifiers, GeoIP, retention/deletion.
- New `docs/security/DATA_PROCESSORS.md` + monitored-site notice template.
- `ACCESS_AND_ACCOUNTS.md` — delivery-directory secret rule; `.env` split plan; `SCANNER_ALLOWLIST_CHANGES.md` — keep new allowlist entries content-addressed.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What is the recorded legal basis for UniFi/Wazuh real-device data? | PRIV-P1-001 | OD-14 decision or feed restriction |
| Are the 09-30 package changes intended to carry the 09-29 verdict; where should edge secrets live; which retention applies to IRIS/host-side Wazuh? | PRIV-P2-003/001/002 | Owner/reviewer statement; key-custody decision; host configs |

## Appendix

- Prior-run verification: REV-P3-010/011 still-open · LIVE-P2-005/002 still-open · ND-P1-001 partially-fixed · REV-P1-003 still-open. Redaction ledger: 20 recorded redactions with original SHA-256s (OSSEC/WireGuard keys, ntfy topic/password, MCT imported credentials).
- Secret scan this run: repo tree clean except 5 allowlisted-path hits in `sbom/vuln/*.json`; `review-package/` = `NO_FINDINGS`; edge `falcon-logs/` = no private-key blocks. Secret values were not printed anywhere in this report; only paths and credential types are named.
