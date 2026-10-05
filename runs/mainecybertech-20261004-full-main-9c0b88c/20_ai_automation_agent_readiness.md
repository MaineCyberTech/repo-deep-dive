# 20_ai_automation_agent_readiness — Prompt 20 - AI Automation and Agent Readiness Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `20_ai_automation_agent_readiness.md` (area AI, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| AI-P1-001 | P1 | Vendored audit prompt packs are stale and the run manifest references a prompt the pack does not contain |
| AI-P1-002 | P1 | `AGENTS.md` names a stale repository path and three developer docs state a stale accessibility gate size that no guard covers |
| AI-P2-001 | P2 | No machine-enforced agent guardrails: allowed paths, human-approval actions, and small-batch PR limits exist only as prose |
| AI-P2-002 | P2 | Prompt packs embed generated outputs alongside instructions without a machine-detectable "not instructions" marker |
| AI-P2-003 | P2 | `.continue/` agent configuration defines models only and does not surface project rules or boundaries |
| AI-P3-001 | P3 | Embedded repo maps and historical pack outputs still reference the pre-rename repository path |
| AI-P3-002 | P3 | `AGENTS.md` retains a large self-contradicting "snapshot" history that an agent must disambiguate |
| AI-P3-003 | P3 | Secrets guidance is spread across instructions without a linked canonical runbook |
