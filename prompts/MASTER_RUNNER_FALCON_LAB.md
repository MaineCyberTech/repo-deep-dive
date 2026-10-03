# Master Runner — Falcon Lab Edition

You are running the Repo Deep-Dive Full Hardening audit against the falcon monitoring lab (central + edge + shared live host).

## Variables

Set:

- `{name}` = `repo-deep-dive`
- `{run}` = `YYYYMMDD-HHMM-falcon-<sha7>_edge-<sha7>` when both repo SHAs are available; otherwise `YYYYMMDD-HHMM-manual`
- `{central}` = `/home/user/falcon-build`
- `{edge}` = `/home/user/falcon-edge-build`
- Canonical run folder: `{central}/docs/audits/{name}/{run}/`
- Edge mirror: `{edge}/docs/audits/{name}/{run}/`
- Profile: `profiles/falcon-lab.md` (machine-readable: `profiles/falcon-lab.manifest.json`)
- Lenses: `lenses/`

## Preconditions

1. Read `profiles/falcon-lab.md` in full before starting. It defines scope, doctrine, boundaries, the applicability matrix, lens targets, and the reconciliation rule.
2. Record repo state for both repos: branch, HEAD SHA, dirty state. Note any parallel session activity.
3. Record a read-only live-host snapshot: service state, versions, disk, tunnels, containers.
4. Confirm the boundaries: read-only against the live host; no ledger/gate mutation; no secret values in any output.

## Execution rules

Inherit all base execution rules (`MASTER_RUNNER_FULL_HARDENING.md`) plus:

- Write only under the two run folders. The canonical folder holds everything; the edge mirror holds the edge-scoped reports plus a pointer to the canonical folder.
- Live-host inspection is read-only. No restarts, reconfigurations, deployments, or failovers. Destructive or disruptive checks require explicit owner sanction and must be recorded in the report.
- Never print secret values; reference path + type only.
- Do not edit ledgers, gates, pins, or program verdicts. Wave 4 *proposes* the decision-log entry; the operator applies it.
- The audit is not the independent review and not the owner adoption. It never grants or revokes a program verdict.
- Findings use the shared format with the per-prompt area codes (`ORCH` … `FLEET`) and lens codes (`ND`, `REV`, `INTG`, `LIVE`).
- Re-check repo HEADs before writing reports; if they moved, note it in the manifest.

## Wave plan

### Wave 0 — Recon (sequential, shared)

Run `00`, `01`, `02` plus the doctrine read from the profile.

Outputs:

- Both run folders created
- `INDEX.md` skeleton
- `audit_manifest.json` (use `examples/audit_manifest.falcon-lab.example.json` as the schema)
- Repo + host snapshot (take a repo inventory first: `tools/repo_inventory.py <repo>`; see `docs/AUTOMATION_GUIDE.md`)
- Prompt status list (run / adapted / na) for the whole run

### Wave 1 — Domain fan-out (parallel subagents, read-only)

Launch subagents per prompt group, in dependency order. Every subagent brief must include: the prompt file path, the profile boundaries, the repo(s) in scope, the evidence discipline, the output path, the area code, the finding format, and any assigned lens overlay. Use `templates/subagent_brief_template.md` so briefs stay uniform.

| Group | Prompts |
|---|---|
| Product surface | 03 |
| Security | 06 → 24 |
| Data | 07 |
| Interfaces | 08 → 30 → 31 |
| Supply chain and CI | 10 → 34, 11 → 35 → 36 → 38 |
| Infra and quality | 12, 09 |
| Resilience | 13 → 32 → 33 |
| Observability and performance | 14, 15 |
| Data governance | 18 |
| People and platform | 16, 19, 20, 21 |
| Falcon-lab domains | 41, 42, 43, 44, 45 |
| N/A (short evidenced reports) | 04, 05, 17, 25, 26, 27, 28, 29, 37, 39 |

### Wave 2 — Lenses (parallel)

Apply each lens per the matrix in the profile (`ND`, `REV`, `INTG`, `LIVE`, `ADV`). Each lens reads the wave-1 reports plus primary evidence and writes `lens_<id>.md` in the canonical run folder.

### Wave 3 — Synthesis

Run `22` (risk register + roadmap), `23` (executive summary + release gate), `40` (release notes/changelog).

The release gate is an audit opinion and must reconcile with existing program verdicts per profile §9 — state the delta and the recommended reconciliation; never grant or revoke a verdict.

### Wave 4 — Doctrine wiring

- Draft the proposed decision-log entry text (the operator applies it).
- Populate `follow_up_register.md`: finding ID → owner suggestion → status → target.
- Normalize findings (`tools/collect_findings.py <run> --write --update-manifest`), score the run (`tools/risk_score.py <run> --write`), render the dashboard (`tools/render_dashboard.py <run> --write`), and, when this run supersedes an earlier one, record the delta with `tools/diff_runs.py <old> <new>`.
- Define the verification plan for findings that are fixed before the next run.
- Do not mutate gates, ledgers, pins, or verdicts.

## Required final files

Base set (all in the canonical run folder):

- `INDEX.md`, `risk_register.md`, `roadmap.md`, `patch_plan.md`
- `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`
- `access_control_matrix.md`, `backup_restore_drill_plan.md`, `incident_tabletop_scenarios.md`
- `branch_protection_recommendation.md`, `sbom_license_policy_recommendation.md`, `secret_rotation_runbook.md`
- `release_notes_draft.md`, `changelog_draft.md`

Falcon-lab additions:

- `audit_manifest.json`
- `lens_new_developer.md`, `lens_independent_reviewer.md`, `lens_integration.md`, `lens_live_operations.md`
- `follow_up_register.md`
- `verification_log.md` (verification mode only)
- Edge mirror folder with the edge-scoped reports and a pointer to the canonical folder

## Verification mode

When re-checking findings that were fixed since the last run:

1. Re-run only the owning prompts (and affected lenses) for the fixed findings.
2. For each finding, capture evidence at the current SHA and mark: `verified-fixed` / `partially-fixed` / `still-open` / `regressed`.
3. Append verification notes; do not rewrite the original findings.
4. Mirror the new statuses into `follow_up_register.md` so `tools/collect_findings.py` picks them up.
5. Write `verification_log.md`.
6. Refresh `22`, `23`, `40`.

## Final response required from the audit agent

```markdown
# Audit Run Complete

## Files Created

## Top 10 Risks

## Release Gate Decision

Use one:

- GO
- GO WITH CONDITIONS
- NO-GO

## Reconciliation With Existing Program Verdicts

State the delta, if any, and the recommended reconciliation. Do not revoke or grant verdicts.

## Recommended Immediate Patch Set

## Recommended 7-Day Plan

## Recommended 30-Day Plan

## Validation Commands

## Open Questions
```
