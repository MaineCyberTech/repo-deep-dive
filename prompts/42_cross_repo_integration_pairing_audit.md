# Prompt 42 - Cross-Repo Integration and Pairing Audit

@include `00_SHARED_AUDIT_RULES.md`

## Mission

Audit the central ↔ edge pair as one integrated system: the pin/pairing contract, shared-host coupling, protocol compatibility, version skew, the additive rule, and every failure mode at the boundary.

This prompt is part of the **Repo Deep-Dive Full Hardening Edition — Falcon Lab profile**. It should produce a repository-specific markdown report with evidence-backed findings, practical fixes, tests, documentation updates, and implementation-ready backlog items.

## Output path

Save the final report to:

`docs/audits/{name}/{run}/42_cross_repo_integration_pairing_audit.md`

## Area code

Use finding IDs beginning with `XREPO`.

Examples:

- `XREPO-P0-001`
- `XREPO-P1-001`
- `XREPO-P2-001`
- `XREPO-P3-001`

## Primary audit questions

1. What repository evidence proves the current behavior for the pairing contract (pin file, release manifest, versions, digests)?
2. What repository evidence proves the current behavior for the edge release process and how the central side consumes a release (pin, rebind, digest verification)?
3. What repository evidence proves the current behavior for shared-host interfaces (ports, sockets, users, directories, containers, networks, tunnels)?
4. What repository evidence proves the current behavior for protocol/API compatibility (edge control plane, enrollment, telemetry ingestion, notification delivery)?
5. What repository evidence proves the current behavior for version skew handling (edge newer or older than the pinned release)?
6. What repository evidence proves the current behavior for the additive rule and isolation requirements (edge changes cannot weaken central; central changes cannot silently break edge)?
7. What repository evidence proves the current behavior for cross-repo documentation consistency (claims in one repo versus the other)?
8. What repository evidence proves the current behavior for cross-repo evidence and delivery artifacts (manifests, SBOM, checksums)?
9. What repository evidence proves the current behavior for boundary failure modes (edge offline, central offline, clock skew, certificate expiry)?
10. What repository evidence proves the current behavior for the rebind/upgrade procedure and rollback?

## Scope to analyze

- Pins and release pin records (central side)
- Edge release manifests, gates, and release records (edge side)
- `docs/edge/` and any cross-repo reference documents
- Shared-host service definitions, ports, users, directories, containers, networks
- Edge control plane, enrollment, and telemetry paths
- WireGuard peers/tunnels shared between the programs
- Notification delivery paths shared across programs
- Delivery directories and release artifacts
- Cross-repo claims in READMEs, runbooks, and doctrine documents

## Required special checks

- Enumerate every cross-repo interface and record where its contract is defined and who owns it.
- Verify the pin matches the actual edge release (digest, versions, claimed capabilities); report any mismatch as a finding.
- Walk the skew scenarios: edge older than pin, edge newer than pin, protocol drift, config drift — describe concrete failure or silent degradation.
- Check the additive rule with evidence: which changes on either side could weaken the other?
- Check for contradictory claims between the two repos (ports, paths, procedures, versions) and whether a contradiction-ledger entry exists.
- Check the edge repo's publication state (remote, pushed commits, tags) against what the pin and docs claim.

## Extended verification checks (base edition v1.1.0)

- Verify each pin claim independently in both repositories; a claim true on one side may be false on the other.
- For every interface, require a named owner and a concrete failure mode; skew scenarios must state the actual outcome (breaks, degrades, or is silent).

## Required outputs and companion artifacts

- Interface inventory table (interface, definition, owner, contract, failure mode)
- Pin/release verification report
- Skew scenario analysis
- Cross-repo consistency report
- Upgrade/rollback procedure assessment

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

- [ ] Reviewed Pairing contract (pin, manifest, versions, digests)
- [ ] Reviewed Edge release process and central consumption
- [ ] Reviewed Shared-host interfaces
- [ ] Reviewed Protocol/API compatibility
- [ ] Reviewed Version skew handling
- [ ] Reviewed Additive rule and isolation requirements
- [ ] Reviewed Cross-repo documentation consistency
- [ ] Reviewed Cross-repo evidence and delivery artifacts
- [ ] Reviewed Boundary failure modes
- [ ] Reviewed Rebind/upgrade and rollback procedure
- [ ] Reviewed Edge repo publication state

## Required report structure

```markdown
# Cross-Repo Integration and Pairing Audit

## Audit Metadata

- Audit name:
- Run:
- Repository:
- Branch:
- Commit SHA:
- Generated at:
- Auditor:
- Area code: XREPO
- Output path: docs/audits/{name}/{run}/42_cross_repo_integration_pairing_audit.md
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
| Pairing contract | 0-5 | Evidence | Gap | Recommended action |
| Edge release process and central consumption | 0-5 | Evidence | Gap | Recommended action |
| Shared-host interfaces | 0-5 | Evidence | Gap | Recommended action |
| Protocol/API compatibility | 0-5 | Evidence | Gap | Recommended action |
| Version skew handling | 0-5 | Evidence | Gap | Recommended action |
| Additive rule and isolation requirements | 0-5 | Evidence | Gap | Recommended action |
| Cross-repo documentation consistency | 0-5 | Evidence | Gap | Recommended action |
| Cross-repo evidence and delivery artifacts | 0-5 | Evidence | Gap | Recommended action |
| Boundary failure modes | 0-5 | Evidence | Gap | Recommended action |
| Rebind/upgrade and rollback procedure | 0-5 | Evidence | Gap | Recommended action |

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

## Interface Inventory

| Interface | Where defined | Owner | Contract | Failure mode | Notes |
|---|---|---|---|---|---|

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| XREPO-001 | Pairing contract | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-002 | Edge release process and central consumption | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-003 | Shared-host interfaces | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-004 | Protocol/API compatibility | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-005 | Version skew handling | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-006 | Additive rule and isolation requirements | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-007 | Cross-repo documentation consistency | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-008 | Cross-repo evidence and delivery artifacts | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-009 | Boundary failure modes | Evidence | Current control | Gap | Severity | Recommendation |
| XREPO-010 | Rebind/upgrade and rollback procedure | Evidence | Current control | Gap | Severity | Recommendation |

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

The final report should be detailed enough that an implementation agent can open the report and start creating safe, scoped remediation PRs without needing another discovery pass. Every interface must have an owner and a failure mode, and every skew scenario must state the concrete outcome.
