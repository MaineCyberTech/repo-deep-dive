# Prompt 43 - Edge Fleet, Image, and Hardware Audit

@include `00_SHARED_AUDIT_RULES.md`

## Mission

Audit the edge sensor program as a fleet: image build and reproducibility, deployment/update/rollback, hardware compatibility, per-unit identity and lifecycle, field diagnostics, and decommissioning.

This prompt is part of the **Repo Deep-Dive Full Hardening Edition — Falcon Lab profile**. It should produce a repository-specific markdown report with evidence-backed findings, practical fixes, tests, documentation updates, and implementation-ready backlog items.

## Output path

Save the final report to:

`docs/audits/{name}/{run}/43_edge_fleet_hardware_audit.md`

## Area code

Use finding IDs beginning with `FLEET`.

Examples:

- `FLEET-P0-001`
- `FLEET-P1-001`
- `FLEET-P2-001`
- `FLEET-P3-001`

## Primary audit questions

1. What repository evidence proves the current behavior for image build (reproducible, pinned inputs, signed artifacts)?
2. What repository evidence proves the current behavior for release artifacts (manifest, SBOM, checksums, versions)?
3. What repository evidence proves the current behavior for install, enrollment, and rebind procedures?
4. What repository evidence proves the current behavior for update and rollback (atomicity, power-loss safety, version pinning)?
5. What repository evidence proves the current behavior for the hardware compatibility matrix (supported adapters, kernels, drivers) versus actual hardware reality?
6. What repository evidence proves the current behavior for per-unit identity (sensor IDs, certificates, keys) and lifecycle (provision, rotate, revoke)?
7. What repository evidence proves the current behavior for fleet inventory and state tracking (which units exist, at what version, in what state)?
8. What repository evidence proves the current behavior for failure modes (storage wear, thermal, power loss, connectivity loss, clock issues)?
9. What repository evidence proves the current behavior for field diagnostics and support bundles?
10. What repository evidence proves the current behavior for decommissioning and replacement?

## Scope to analyze

- Image build scripts, recipes, and pinned inputs (`image/`)
- Deployment and update tooling (`deploy/`, `bin/`)
- Profiles and device configuration (`profiles/`, `config/`)
- Agent and updater source (`src/`, `api/`)
- Hardware documentation and compatibility claims (`docs/`)
- Tests and CI for image/deploy paths (`tests/`, `ci/`)
- Release and evidence artifacts (`evidence/`, release records)
- The live sensor unit and its state (read-only)
- Falcon-side edge-facing records (pin, enrollment records)

## Required special checks

- Verify the documented hardware compatibility matrix against actual attached hardware and driver/kernel evidence; report every claim not supported by evidence.
- Check image build reproducibility: are inputs pinned (base image, packages, toolchain), and can the build be repeated from the repo alone?
- Check update atomicity: what happens if power fails mid-update? Is there an A/B or staged path, and is rollback proven?
- Check secrets on the unit: where do keys/certificates live, what protects them, and what happens on compromise?
- Check the agent's privilege model and update path for escalation potential; cross-reference security findings rather than duplicating them.
- Check fleet-state reality: how many units exist, which are live, and how that is tracked in-repo.
- Check the pin to the central side; cross-reference XREPO findings rather than duplicating them.

## Extended verification checks (base edition v1.1.0)

- Mark every hardware and fleet-state claim as evidenced or unsupported; verify against the live fleet where authorized, otherwise mark `unverified`.
- For every update and rollback path, state the power-loss outcome explicitly.

## Required outputs and companion artifacts

- Hardware compatibility matrix (claimed vs evidenced)
- Image build reproducibility assessment
- Update/rollback safety assessment
- Per-unit identity and lifecycle review
- Fleet inventory (as evidenced)
- Field diagnostics assessment

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

- [ ] Reviewed Image build and reproducibility
- [ ] Reviewed Release artifacts (manifest, SBOM, checksums)
- [ ] Reviewed Install, enrollment, and rebind procedures
- [ ] Reviewed Update and rollback safety
- [ ] Reviewed Hardware compatibility matrix vs reality
- [ ] Reviewed Per-unit identity and lifecycle
- [ ] Reviewed Fleet inventory and state tracking
- [ ] Reviewed Failure modes (storage, thermal, power, connectivity, clock)
- [ ] Reviewed Field diagnostics and support bundles
- [ ] Reviewed Decommissioning and replacement
- [ ] Reviewed Agent privilege and update escalation (cross-referenced)

## Required report structure

```markdown
# Edge Fleet, Image, and Hardware Audit

## Audit Metadata

- Audit name:
- Run:
- Repository:
- Branch:
- Commit SHA:
- Generated at:
- Auditor:
- Area code: FLEET
- Output path: docs/audits/{name}/{run}/43_edge_fleet_hardware_audit.md
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
| Image build and reproducibility | 0-5 | Evidence | Gap | Recommended action |
| Release artifacts (manifest, SBOM, checksums) | 0-5 | Evidence | Gap | Recommended action |
| Install, enrollment, and rebind | 0-5 | Evidence | Gap | Recommended action |
| Update and rollback safety | 0-5 | Evidence | Gap | Recommended action |
| Hardware compatibility matrix | 0-5 | Evidence | Gap | Recommended action |
| Per-unit identity and lifecycle | 0-5 | Evidence | Gap | Recommended action |
| Fleet inventory and state tracking | 0-5 | Evidence | Gap | Recommended action |
| Failure modes (storage, thermal, power, connectivity, clock) | 0-5 | Evidence | Gap | Recommended action |
| Field diagnostics and support bundles | 0-5 | Evidence | Gap | Recommended action |
| Decommissioning and replacement | 0-5 | Evidence | Gap | Recommended action |

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

## Hardware Compatibility Matrix

| Component | Claimed support | Evidence | Actual state | Gap | Notes |
|---|---|---|---|---|---|

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FLEET-001 | Image build and reproducibility | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-002 | Release artifacts | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-003 | Install, enrollment, and rebind | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-004 | Update and rollback safety | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-005 | Hardware compatibility matrix | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-006 | Per-unit identity and lifecycle | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-007 | Fleet inventory and state tracking | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-008 | Failure modes | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-009 | Field diagnostics and support bundles | Evidence | Current control | Gap | Severity | Recommendation |
| FLEET-010 | Decommissioning and replacement | Evidence | Current control | Gap | Severity | Recommendation |

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

The final report should be detailed enough that an implementation agent can open the report and start creating safe, scoped remediation PRs without needing another discovery pass. Every hardware claim must be marked evidenced or unsupported, and every update/rollback path must have a stated power-loss outcome.
