# 00_audit_orchestrator — Prompt 00 - Audit Orchestrator

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `00_audit_orchestrator.md` (area ORCH, prompt)

## Verification Performed

Reviewed `tools/full_domain.py` against the master runner's wave model (`prompts/MASTER_RUNNER_FULL_HARDENING.md:34-77`) and the 00 prompt. `domains --full` parsed 42 prompt domains plus the deterministic lens.

## Findings

| ID | Severity | Title |
|---|---|---|
| ORCH-P3-001 | P3 | Full-domain driver runs the orchestrator as a flat parallel domain |
