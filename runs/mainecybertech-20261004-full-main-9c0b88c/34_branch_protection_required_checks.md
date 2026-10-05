# 34_branch_protection_required_checks — Prompt 34 - Branch Protection and Required Checks Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `34_branch_protection_required_checks.md` (area BP, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| BP-P1-001 | P1 | `main` requires a context (`Dependency Review`) that no job emits |
| BP-P1-002 | P1 | `enforce_admins:false` lets administrators bypass all required checks and reviews |
| BP-P1-003 | P1 | Production deploy path uses the unguarded `prod` environment, not `prod-approval` |
| BP-P2-001 | P2 | `require_code_owner_reviews:false` makes the committed CODEOWNERS advisory only |
| BP-P2-002 | P2 | No break-glass / bypass process for branch protection, and no bypass audit trail |
| BP-P2-003 | P2 | No drift detection between committed branch-protection JSON and live GitHub settings |
| BP-P2-004 | P2 | Path-filtered required checks can leave `main`/`develop` protected by checks that never run |
| BP-P3-001 | P3 | Hotfix and emergency-deploy documentation is a stub and partially stale |
| BP-P3-002 | P3 | Dependabot has no security-update separation or triage SLA, and PR template has no enforced link to required checks |
