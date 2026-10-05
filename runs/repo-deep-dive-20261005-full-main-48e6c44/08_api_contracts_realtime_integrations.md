# 08_api_contracts_realtime_integrations — Prompt 08 - API Contracts, Realtime, and Integrations Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `08_api_contracts_realtime_integrations.md` (area API, prompt)

## Verification Performed

The only HTTP API is the lab job API (`tools/lab_api_server.py`) with its client (`tools/lab_runner.py`). Endpoints: GET /health, GET /repos, POST /sync, POST /run.

## Findings

| ID | Severity | Title |
|---|---|---|
| API-P2-001 | P2 | Lab API has no rate limiting or request-body error signalling |
| API-P3-001 | P3 | Lab API contract is documented in prose only (no schema) |
