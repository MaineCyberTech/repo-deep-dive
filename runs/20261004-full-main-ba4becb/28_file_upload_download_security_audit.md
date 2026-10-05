# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `20261004-full-main-ba4becb`
- Target: `falcon-edge` @ `ba4becb` (branch `main`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

- Read-only analysis of `MaineCyberTech/falcon-edge` at `ba4becb` (git `ba4becb6ecd8fdc0c4e0363a67d7a62f60985788`, branch `main`).
- Deterministic lens (LLM-free) run on the lab (`ci-runner`, HTTP job API) and locally: LICENSE absent; no non-executable tracked `*.sh`; no CRLF tracked text; no tracked secret-like filenames; `.gitattributes` present.
- Wave-0 inventory via `tools/repo_inventory.py` (1,410 files; 5 workflows; 3 routes; 17 schema tables; 56 test files).
- Target repository is not applicable to this domain; the finding records the evidence and the future-readiness trigger.
- No secrets printed; all evidence is file:line references.

## Findings

| ID | Severity | Title |
|---|---|---|
| FILE-P2-001 | P2 | Update artifact host allowlist exists but is not configured in the shipped image |
| FILE-P3-001 | P3 | Root-side update verifier rejects symlink/traversal/setuid archive members |
