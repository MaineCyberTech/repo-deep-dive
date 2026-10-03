# API Contracts, Realtime, and Integrations Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: API
- Output path: docs/audits/{name}/{run}/08_api_contracts_realtime_integrations.md
- Scope limitations: the paired edge contract lives in a separate private repo; cross-repo verification cannot run here.

## Scope

Reviewed first-party integration contracts: edge→central ingest (Vector), client VPN enrollment service, alert relay → ntfy, OpenSearch snapshot API, and the cross-repo pairing pin. Realtime is limited to dashboard polling; no websocket surface.

## Evidence Reviewed

- `config/vector/aggregator.yaml`, `config/vector/edge.yaml`.
- `automation/vpn/issue-enroll-token.sh`, `config/traefik/dynamic.yml` (`vpn-enroll`).
- `docs/edge/EDGE_RELEASE_PIN.md`, `automation/validation/verify_edge_pin.py`.
- `bootstrap/85-backup-job.sh` (`os_api`), `automation/validation/alert_canary.sh`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/vector/*.yaml` | Config | Ingest auth | basic auth, shared secret |
| `issue-enroll-token.sh` | Source | Token model | no expiry field found |
| `EDGE_RELEASE_PIN.md` | Doc | Pairing contract | digests pinned, verifier exists |
| `grep -i expir issue-enroll-token.sh` | Search | Token lifetime | no TTL |

## Executive Summary

The live ingest contract is a shared-secret basic-auth HTTP path with validation and a DLQ — functional but not identity-bearing. The client enrollment API issues tokens with no expiry. The cross-repo pairing pin is now machine-checked by `verify_edge_pin.py` (a strength), but resolution depends on the edge delivery directory which is not present in this checkout, so the pairing contract is `unverified` here.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Ingest API | `config/vector/aggregator.yaml` | edge→central | Functional | Medium | shared secret |
| Enrollment API | `issue-enroll-token.sh` | client VPN | Functional | Medium | no expiry |
| Alert relay | `automation/validation/alert_canary.sh` | ntfy delivery | Functional | Medium | relay metrics gap |
| Snapshot API | `85-backup-job.sh os_api` | OpenSearch backup | Functional | Medium | unused-var lint |
| Edge pin | `docs/edge/EDGE_RELEASE_PIN.md` | pairing | Partial | High | unverifiable here |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Contract definitions | 3 | vector configs, pin | shared-secret auth | API-P2-002 |
| Versioning | 3 | edge pin/doc | drift check | API-P1-001 |
| Realtime | 2 | polling only | n/a | — |
| Webhooks/retries | 2 | relay retries | bounded | OBS |
| Idempotency | 2 | none for ingest | could duplicate | API-P2-002 |
| Error handling | 3 | DLQ, validation | — | — |

## Findings

### Finding ID: API-P1-001 - Cross-repo pairing contract cannot be verified in this environment

- Severity: P1
- Confidence: High
- Area: API
- Evidence:
  - `docs/edge/EDGE_RELEASE_PIN.md` — resolves digests against a delivery directory
  - `automation/validation/verify_edge_pin.py` — verifier; requires the edge delivery tree
  - `docs/CURRENT_STATE.md` C3/C8 — pairing contract previously failed to verify at run time
- What is happening: The pin and its verifier exist, but the edge delivery artifacts are not in this repository, so a clone cannot confirm the contract.
- Why it matters: A frozen interface is only as good as its verification; unverifiable pairings mask drift.
- User / business impact: Cross-repo releases can diverge silently.
- Security / privacy / reliability impact: Integrity of the joint release.
- Recommended fix: Vendor a signed digest manifest (not the artifacts) into this repo, or run the verifier in CI against a pinned artifact URL; record the result as evidence.
- Suggested validation: `python3 automation/validation/verify_edge_pin.py` returns 0 from a fresh clone.
- Owner suggestion: release owner
- Effort estimate: M
- Dependencies: edge session
- Status: open

### Finding ID: API-P2-001 - Enrollment API tokens have no expiry field

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `automation/vpn/issue-enroll-token.sh` — issues tokens; no TTL/expiry key found (`grep -i "expir|ttl"` shows none)
  - `config/traefik/dynamic.yml` lines 121-126 — `enroll.mainecybertech.us` public route
- What is happening: Issued enrollment tokens do not carry an expiry.
- Why it matters: A leaked token remains valid indefinitely.
- User / business impact: Unauthorized device enrollment.
- Security / privacy / reliability impact: Persistent credential.
- Recommended fix: Add an issue/expiry timestamp and reject expired tokens; rotate the shared token after onboarding pauses.
- Suggested validation: Unit test: expired token rejected; token older than window denied.
- Owner suggestion: release owner
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: API-P2-002 - Ingest contract relies on a shared secret header, not request signing or idempotency keys

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `config/vector/aggregator.yaml` line 25 `auth:` — basic-auth/shared secret
  - `config/vector/edge.yaml` line 245 `auth:`
- What is happening: Sender identity is a shared secret; there is no per-message signing or idempotency key.
- Why it matters: Forged telemetry can be injected by any holder of the secret; retries can duplicate events.
- User / business impact: Telemetry integrity/dedup.
- Security / privacy / reliability impact: Spoofing and duplicate ingestion.
- Recommended fix: mTLS per sensor, or HMAC request signing plus an idempotency key deduped at ingest.
- Suggested validation: Replay test — duplicate idempotency key stored once.
- Owner suggestion: release owner
- Effort estimate: M
- Dependencies: edge PKI
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unverifiable pairing | P1 | Medium | High | edge pin | API-P1-001 |
| Non-expiring enrollment token | P2 | Medium | Medium | issue-enroll-token.sh | API-P2-001 |
| Forged/duplicate telemetry | P2 | Low | Medium | vector auth | API-P2-002 |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Add enrollment token expiry (API-P2-001).

### This Month
- Vendor a signed edge digest manifest (API-P1-001).

### Later / Platform Evolution
- mTLS/signing + idempotency (API-P2-002).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Token expiry field | Limits leak window | issue-enroll-token.sh | unit test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Signed edge manifest | P1 | release owner | M | edge session |
| Ingest signing | P2 | release owner | M | PKI |

## Suggested Tests

- Expired enrollment token rejected.
- Idempotency dedup test.
- Mutation test for the edge pin (exists: `test_edge_pin_mutation.py`).

## Suggested Documentation Updates

- Document the ingest auth contract and its threat model.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Where is the edge delivery dir in CI? | Verifier applicability | CI env |

## Appendix
Not applicable.
