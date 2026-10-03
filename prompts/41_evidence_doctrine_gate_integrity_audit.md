# Prompt 41 - Evidence, Doctrine, and Gate Integrity Audit

@include `00_SHARED_AUDIT_RULES.md`

## Mission

Audit whether the program's evidence-first doctrine holds end-to-end: every claimed status is backed by verifiable evidence, ledgers are append-only and internally consistent, gates were earned rather than asserted, reviews are independent, and deliveries match what was verified.

This prompt is part of the **Repo Deep-Dive Full Hardening Edition — Falcon Lab profile**. It should produce a repository-specific markdown report with evidence-backed findings, practical fixes, tests, documentation updates, and implementation-ready backlog items.

## Output path

Save the final report to:

`docs/audits/{name}/{run}/41_evidence_doctrine_gate_integrity_audit.md`

## Area code

Use finding IDs beginning with `EVID`.

Examples:

- `EVID-P0-001`
- `EVID-P1-001`
- `EVID-P2-001`
- `EVID-P3-001`

## Primary audit questions

1. What repository evidence proves the current behavior for the doctrine documents (AGENTS.md, REPOSITORY.md) and how they bind contributors?
2. What repository evidence proves the current behavior for ledger structure, append-only discipline, and update rules (decision log, gate ledger, evidence index, risk register, contradiction ledger, exception register, redactions, progress ledger, test execution)?
3. What repository evidence proves the current behavior for the chain from claim to evidence to ledger entry (verdicts, PASS statuses, digests, checksums)?
4. What repository evidence proves the current behavior for digest/checksum derivation and verification (PACKAGE_DIGEST.txt, PACKAGE_MANIFEST.sha256, publication/verification chain)?
5. What repository evidence proves the current behavior for gate definitions and pass criteria, and whether every gate status has evidence?
6. What repository evidence proves the current behavior for independent review records and reviewer independence (who produced vs reviewed vs approved)?
7. What repository evidence proves the current behavior for owner adoption records and approval artifacts (who approved, when, over what scope)?
8. What repository evidence proves the current behavior for contradiction handling (open/closed items, resolutions, staleness)?
9. What repository evidence proves the current behavior for exception handling (justifications, expiry, owner approval)?
10. What repository evidence proves the current behavior for delivery/publication integrity (what is published, pinning, rebinding, reproducibility of the package)?

## Scope to analyze

- Doctrine documents (AGENTS.md, REPOSITORY.md, README.md) in both repos
- Ledgers: decision log, gate ledger(s), evidence index, risk register, contradiction ledger, exception register, redactions, progress ledger, test execution
- Evidence directories and evidence references
- Package digest and manifest artifacts
- Pins and release pin records
- Review, adoption, and verdict records
- Closeout and review-package artifacts
- Publication/verification scripts and their outputs
- Edge program equivalents (its own doctrine, ledgers, gates, releases)

## Required special checks

- Sample at least ten claimed PASS/APPROVED/verified statuses across both repos and trace each to its evidence; report every unearned or unsupported status.
- Recompute digests/checksums where possible and report any drift between artifact and record.
- Check append-only discipline: look for rewritten history, silent edits, timestamp ordering violations, or status changes without a corresponding log entry.
- Check independence: reviewer is not the author; reviewer had access to the artifacts; approver is recorded; conflicts are declared.
- Check reconciliation between documents: no doc may contradict a ledger without an entry in the contradiction ledger.
- Check that audits/verification runs themselves do not mutate gates or ledgers (including this run).
- Check redaction consistency: no secret values in artifacts, while keeping records reviewable.

## Extended verification checks (base edition v1.1.0)

- For every ledger status change, verify a corresponding evidence artifact at the recorded commit; flag status changes made in the same commit that added their own justification.
- Sample at least ten claimed statuses per program and record `supported` / `partially supported` / `unsupported` / `not reproducible`.

## Required outputs and companion artifacts

- Evidence integrity matrix (claim, artifact, reproduction result)
- Claim-to-evidence sample table
- Digest/checksum verification report
- Gate integrity report (gate, criteria, evidence, status)
- Contradiction and exception register review
- Independence assessment (reviewer/author/approver separation)

## Step-by-step execution instructions

1. Read the repository tree and identify all files relevant to this domain.
2. Review source files, configuration files, tests, docs, and generated artifacts separately.
3. Create an evidence inventory before writing findings.
4. For each item in scope, determine whether it is implemented, partially implemented, absent, stale, duplicated, unsafe, undocumented, or unknown.
5. Identify strengths before risks so the report is balanced and useful.
6. Create findings only when there is concrete evidence.
7. Assign severity using the shared P0/P1/P2/P3 model.
8. Suggest exact file-level remediation where possible.
9. Suggest tests that would prove the remediation works.
10. Suggest documentation updates needed to keep operators and future AI agents aligned.
11. End with open questions and evidence gaps.

## Evidence collection checklist

- [ ] Reviewed Doctrine documents and their binding rules
- [ ] Reviewed Ledger structure and append-only discipline
- [ ] Reviewed Claim to evidence to ledger chain
- [ ] Reviewed Digest/checksum derivation and verification
- [ ] Reviewed Gate definitions and pass criteria
- [ ] Reviewed Independent review records
- [ ] Reviewed Owner adoption records
- [ ] Reviewed Contradiction handling
- [ ] Reviewed Exception handling
- [ ] Reviewed Delivery/publication integrity
- [ ] Reviewed Edge program equivalents
- [ ] Reviewed Redaction consistency
- [ ] Reviewed Audit non-mutation of gates and ledgers

## Required report structure

```markdown
# Evidence, Doctrine, and Gate Integrity Audit

## Audit Metadata

- Audit name:
- Run:
- Repository:
- Branch:
- Commit SHA:
- Generated at:
- Auditor:
- Area code: EVID
- Output path: docs/audits/{name}/{run}/41_evidence_doctrine_gate_integrity_audit.md
- Scope limitations:

## Scope

Describe exactly what was reviewed and what was not reviewed.

## Evidence Reviewed

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|

## Executive Summary

Summarize the current state in plain English. Include strengths, major risks, and recommended next actions.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Doctrine documents and binding rules | 0-5 | Evidence | Gap | Recommended action |
| Ledger structure and append-only discipline | 0-5 | Evidence | Gap | Recommended action |
| Claim to evidence to ledger chain | 0-5 | Evidence | Gap | Recommended action |
| Digest/checksum verification | 0-5 | Evidence | Gap | Recommended action |
| Gate definitions and pass criteria | 0-5 | Evidence | Gap | Recommended action |
| Independent review records | 0-5 | Evidence | Gap | Recommended action |
| Owner adoption records | 0-5 | Evidence | Gap | Recommended action |
| Contradiction handling | 0-5 | Evidence | Gap | Recommended action |
| Exception handling | 0-5 | Evidence | Gap | Recommended action |
| Delivery/publication integrity | 0-5 | Evidence | Gap | Recommended action |
| Redaction consistency | 0-5 | Evidence | Gap | Recommended action |

## Detailed Review

For every major item in scope, include:

### Item: Name

- Evidence:
- What it does:
- How it appears to work:
- Dependencies:
- Current controls:
- Missing controls:
- Risks:
- Recommended improvement:
- Suggested tests:
- Suggested docs:

## Claim-to-Evidence Sample Table

| Claim | Artifact | Reproduction result | Verdict | Notes |
|---|---|---|---|---|

## Gate Integrity Table

| Gate | Criteria | Evidence | Recorded status | Supported? | Notes |
|---|---|---|---|---|---|

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EVID-001 | Doctrine documents and binding rules | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-002 | Ledger structure and append-only discipline | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-003 | Claim to evidence to ledger chain | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-004 | Digest/checksum verification | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-005 | Gate definitions and pass criteria | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-006 | Independent review records | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-007 | Owner adoption records | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-008 | Contradiction handling | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-009 | Exception handling | Evidence | Current control | Gap | Severity | Recommendation |
| EVID-010 | Delivery/publication integrity | Evidence | Current control | Gap | Severity | Recommendation |

## Findings

Use the shared finding format exactly.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|

## Recommendations

Group recommendations into:

### Immediate / Release Blocking

### This Week

### This Month

### Later / Platform Evolution

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|

## Suggested Tests

Include unit, integration, E2E, CI, security, regression, and manual validation ideas as applicable.

## Suggested Documentation Updates

List exact docs to create or update.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|

## Appendix

Include raw inventories, diagrams, Mermaid diagrams, command outputs, or additional notes as needed.
```

## Quality bar

The final report should be detailed enough that an implementation agent can open the report and start creating safe, scoped remediation PRs without needing another discovery pass. Every sampled claim must have a stated verdict, and every unearned status must be listed explicitly.
