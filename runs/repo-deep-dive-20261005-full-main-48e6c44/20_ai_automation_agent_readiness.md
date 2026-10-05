# 20_ai_automation_agent_readiness — Prompt 20 - AI Automation and Agent Readiness Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `20_ai_automation_agent_readiness.md` (area AI, prompt)

## Verification Performed

Reviewed the full_domain driver's subagent contract and the agent-facing rules.

## Findings

| ID | Severity | Title |
|---|---|---|
| AI-P2-001 | P2 | emit accepts findings with no evidence or citation requirement |
| AI-P3-001 | P3 | run --agent-cmd executes a shell template with unvalidated substitutions |
