# 08 API Contracts, Realtime & Integrations

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

HTTP endpoints, Socket.IO events, schema validation, versioning, idempotency and external integrations at the API boundary. Read-only.

## Evidence Reviewed

- `docs/API.md`
- `apps/realtime/src/server.ts` (routing at ~803–1211, socket binding at ~4846–4928)
- `packages/contracts/src/schemas.ts` (`EVENT_SCHEMAS`), `constants.ts`
- `infra/nginx/nginx.conf.template` (proxy surface)
- `SECURITY.md`, `README.md`

## Verification Performed

- Cross-checked the `docs/API.md` route table against the `handleHttp` route list (all documented routes present in code; `/health`, `/readyz`, `/client-error` present in code).
- Cross-checked socket event names in `docs/API.md` against `bindSocketHandler` registrations (match incl. `admin:catalog-check`).
- Confirmed per-route body caps in `server.ts` (e.g. 128 KB at 1647, 4 KB at 2023, 256 KB at 3440).
- Confirmed Socket.IO `maxHttpBufferSize: 64 KB` and CORS allowlist.

## Executive Summary

The realtime API is well-structured: zod-validated inputs, per-route body caps, a 64 KB socket buffer ceiling, explicit socket event schemas, and documented idempotency for `/runs` and admin mutations. The principal integration concern is that the HTTP/event contract is hand-maintained in `docs/API.md` with no automated drift test, so the documented contract can silently diverge from code. Several unauthenticated public endpoints expose operational views and are unversioned. No breaking integration defect was reproduced.

## Inventory

| Surface | Count | Validation |
|---|---|---|
| HTTP endpoints | ~40 | zod per body; body caps |
| Socket client→server events | 13 (`EVENT_SCHEMAS`) | zod per event |
| Socket server→client events | documented in API.md | n/a |
| Idempotency | `/runs` (submissionKey), admin claims, purchases | RPC keys |
| Versioning | payload `v` fields; score/course versions | present |

## Findings

### Finding ID: API-P2-001 - API contract is hand-maintained with no automated drift test

- Severity: P2
- Confidence: High
- Area: API
- Evidence:
  - `docs/API.md` line 3–6 — "Regenerate this file by hand when those change"
  - `apps/realtime/src/server.ts` route list is code-defined; no test asserts docs/API.md parity
- What is happening: The documented contract can drift from `server.ts`/`EVENT_SCHEMAS` without any failing check.
- Why it matters: Clients and integrators rely on a document that may be stale.
- User / business impact: Integration breakage and wasted support effort.
- Security / privacy / reliability impact: A stale doc can understate the exposed surface.
- Recommended fix: Generate the route/event tables from code (or add a test that parses registered routes and compares to a committed snapshot).
- Suggested validation: A route added without a doc update fails CI.
- Owner suggestion: Realtime engineer
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: API-P3-001 - Public operational endpoints are unauthenticated and unversioned

- Severity: P3
- Confidence: High
- Area: API
- Evidence:
  - `server.ts` — `/config` (853), `/equipment` (869), `/content/discover` (884), `/challenges` (897), `/launch-readiness` (903), `/perf-budget` (947), `/economy/simulation` (1016)
  - No auth gate on those routes; response shapes carry no version envelope
- What is happening: Internal runtime modes, economy simulation and perf budget are world-readable.
- Why it matters: Informational exposure and an unstable contract for consumers.
- User / business impact: Low.
- Security / privacy / reliability impact: Minor information disclosure; no PII observed.
- Recommended fix: Confirm each public route is intentional; add a `v` field or `/v1` prefix for stability; consider gating operational ones behind ops auth.
- Suggested validation: Route allowlist review + response schema test.
- Owner suggestion: Realtime engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: API-P3-002 - No explicit CORS response headers for cross-origin HTTP dev/deploy

- Severity: P3
- Confidence: Medium
- Area: API
- Evidence:
  - `server.ts` — HTTP responses set `x-trace-id` (811) but no `Access-Control-*` headers
  - `apps/web/package.json` uses `NEXT_PUBLIC_SOCKET_URL` which may be direct in dev
- What is happening: Browser HTTP calls to the realtime origin work only same-origin (via nginx).
- Why it matters: A misconfigured `NEXT_PUBLIC_SOCKET_URL` yields opaque CORS failures that are hard to diagnose.
- User / business impact: Local/dev friction.
- Security / privacy / reliability impact: None (token auth).
- Recommended fix: Document the same-origin requirement and/or emit allowlisted CORS headers on the browser-facing endpoints.
- Suggested validation: Dev-mode cross-origin fetch succeeds or fails with a clear header.
- Owner suggestion: Web engineer
- Effort estimate: S
- Dependencies: SEC-P2-001
- Status: open

## Risks

- R-API-1: Contract drift between docs and code (P2).
- R-API-2: Public operational surface (P3).

## Recommendations

1. Add contract drift testing.
2. Review public route exposure and add version envelopes.

## Quick Wins

- Snapshot the route table in a test (M). Confirm public route intent (S).

## Hardening Backlog

- OpenAPI-style generated reference for HTTP + socket.

## Suggested Tests

- Route/event parity test; public-route allowlist test.

## Suggested Documentation Updates

- `docs/API.md` versioning/exposure note.

## Open Questions

- Are `/config`, `/economy/simulation` consumed by external partners? (`Unknown`.)

## Appendix

- Nginx routes every documented path explicitly (no catch-all proxy to realtime).
