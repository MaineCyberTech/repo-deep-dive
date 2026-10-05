# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P1-001 | P1 | No license allow/deny policy in dependency review or any CI gate |
| SBOM-P1-002 | P1 | SBOM carries no license data and no dependency graph, limiting triage and license review |
| SBOM-P2-001 | P2 | SBOM is artifact-only: not release-bound, not commit-bound, not attested |
| SBOM-P2-002 | P2 | No container/image SBOM; base-image OS packages untracked |
| SBOM-P2-003 | P2 | `docs/CI.md` documents the SBOM workflow as "Blocking" but it gates nothing |
| SBOM-P3-001 | P3 | Root license is ISC with no documented rationale |
| SBOM-P3-002 | P3 | SBOM format/count not validated before upload; no regression guard |
