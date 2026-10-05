# 08_api_contracts_realtime_integrations — Prompt 08 - API Contracts, Realtime, and Integrations Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `08_api_contracts_realtime_integrations.md` (area API, prompt)

## Verification Performed

HTTP/socket contract reviewed against docs/API.md: run submission, creator courses, and admin routes are authenticated; health/readiness are intentionally public. Residual: several read-only operational endpoints are public and unversioned, and /config exposes rollout-mode booleans to unauthenticated callers.

## Findings

| ID | Severity | Title |
|---|---|---|
| API-P3-001 | P3 | Public operational endpoints are unauthenticated and unversioned |
| API-P3-002 | P3 | /config exposes rollout-mode values to unauthenticated clients |
