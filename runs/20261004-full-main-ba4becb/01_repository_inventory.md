# 01_repository_inventory — Prompt 01 - Comprehensive Repository Inventory

- Run: `20261004-full-main-ba4becb`
- Target: `falcon-edge` @ `ba4becb` (branch `main`)
- Domain: `01_repository_inventory.md` (area INV, prompt)

## Verification Performed

- Read-only analysis of `MaineCyberTech/falcon-edge` at `ba4becb` (git `ba4becb6ecd8fdc0c4e0363a67d7a62f60985788`, branch `main`).
- Deterministic lens (LLM-free) run on the lab (`ci-runner`, HTTP job API) and locally: LICENSE absent; no non-executable tracked `*.sh`; no CRLF tracked text; no tracked secret-like filenames; `.gitattributes` present.
- Wave-0 inventory via `tools/repo_inventory.py` (1,410 files; 5 workflows; 3 routes; 17 schema tables; 56 test files).
- Target repository is not applicable to this domain; the finding records the evidence and the future-readiness trigger.
- No secrets printed; all evidence is file:line references.

## Findings

| ID | Severity | Title |
|---|---|---|
| INV-P2-001 | P2 | Committed raw evidence is large and only now budget-guarded |
| INV-P2-002 | P2 | Pack inventory tooling now emits routes/schema/entrypoints |
| INV-P3-001 | P3 | Generated models/schemas/dashboard JSON committed and can drift |
