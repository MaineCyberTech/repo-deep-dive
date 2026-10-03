# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-015** hardens the control-plane HTTP transport for the findings from run
`20261003-0018-fix-trust-root-87532ec` (audit reports `06_security_authz_tenancy_audit.md` and
`02_architecture_runtime_topology.md`).

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-015`
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)
- Findings: `SEC-P2-001`, `ARCH-P3-001`

Both findings were re-verified against current `origin/main` and **still reproduce**: the transport
is a bare `ThreadingHTTPServer` (unbounded thread per accepted connection), writes no security
headers, has no request timeout, and has no per-peer request limit. The base check in
`verify.log` shows `SECURITY_HEADERS`, `PeerRateLimiter`, `BoundedThreadingHTTPServer` and
`REQUEST_TIMEOUT_SECONDS` are all absent from `origin/main:src/falcon_control/http_server.py`.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-001` | P2 | open -> fixed (draft PR) | Security response headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store`) on every response; a per-peer fixed-window request limiter keyed by client-certificate fingerprint (falling back to source address) returning `429 RATE_LIMITED`; and a 30 s request-socket timeout for slow/stalled clients. |
| `ARCH-P3-001` | P3 | open -> fixed (draft PR) | `BoundedThreadingHTTPServer` caps simultaneous request handlers (`FALCON_HTTP_MAX_CONNECTIONS`, default 64). A connection beyond the cap is shed with `503 SERVER_BUSY` instead of spawning an unbounded thread. |

## Changes

| File | What changed |
|---|---|
| `src/falcon_control/http_server.py` | New `PeerRateLimiter` (fixed window, fingerprint-or-IP key, bounded peer map); `SECURITY_HEADERS` applied centrally in a new `_write_response()`; `EdgeRequestHandler.timeout = 30` for slow-client protection; rate-limit gate returns a retryable `429` problem before reading the body; new `BoundedThreadingHTTPServer` with a `threading.BoundedSemaphore` cap and a `503` shed path; `EdgeControlServer.create()` gains optional `max_workers` / `rate_limit` / `rate_window` (env-tunable via `FALCON_HTTP_MAX_CONNECTIONS`, `FALCON_HTTP_RATE_LIMIT`, `FALCON_HTTP_RATE_WINDOW`). |
| `tests/phase2/test_service_integration.py` | Five Phase-2 tests: security headers present; server is connection-bounded and carries a limiter; an over-capacity connection is shed with `503` (unit, fake socket); the limiter bounds per peer independently; and over real mTLS the third request in a 2-request budget receives a retryable `429 RATE_LIMITED` with the hardened headers. |

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1). The committed branch was synced with the lab job API (`/sync`,
a real git clone at `1cb9ec0`, so `ci/validate.sh` exercises its `git ls-files` parse loop); raw
output and exit codes are in `remediation/PS-015/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2/test_service_integration.py -k "security_headers or connection_bounded or over_capacity or rate_limit"` | edge-builder VM (pytest 7.4.4) | 0 (5 passed) | `remediation/PS-015/verify.log` |
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM (pytest 7.4.4) | 0 (134 passed) | `remediation/PS-015/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-015/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-015/verify.log` |

- Secret scan: **pass** — "no leaks found" (6.66 MB scanned).
- Scope check: **pass** — the patch-set file (`src/falcon_control/http_server.py`) plus the Phase-2
  regression tests that assert the fixed behaviour. No API/schema/dependency changes.

**Not run (recorded as `not run`, not asserted):**

- A live slow-loris client holding a socket open: the 30 s socket timeout is configured on the
  handler but was not exercised against a deliberately stalled TLS client.
- A real high-concurrency load test proving memory is bounded: the cap is asserted by shedding a
  connection once the semaphore is exhausted (unit test), not by a load generator.

## Evidence bundle

- `remediation/PS-015/diff.patch` — SHA-256 `e108f5e20174982b7777ff56d46c0be0e50c7edfcefa78dae0d5a18c6297de94`
- `remediation/PS-015/manifest.json`
- `remediation/PS-015/verify.log`

## Risk and rollback

- Risk: **low-medium**. New behaviour: a client exceeding the default budget (1000 requests /
  10 s per peer) receives `429`; more than 64 in-flight handlers receive `503`; an idle
  connection is dropped after 30 s. Defaults are deliberately generous for the lab (the limiter
  is a bound, not a tight quota) and are env-tunable. The stray `503` path writes a raw HTTP
  response, so it is intentionally not a service-handled RFC 9457 response.
- Rollback: `git revert 1cb9ec0` restores the unbounded `ThreadingHTTPServer`, removes the
  headers/timeout/limiter, and drops the Phase-2 assertions.

## Review checklist

- [ ] Diff touches only the patch-set file (+ tests)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- **Rate-limit budget and placement.** The default `1000/10s` per peer is chosen to bound DoS
  without tripping normal lab/test traffic. If this is deployed beyond the lab, the owner should
  decide the production budget (and consider fronting the service with a reverse proxy, the
  finding's stated alternative). Both are one-line config/env changes here.
- **Shed vs. queue on saturation.** Over-capacity connections are refused with `503` rather than
  queued; this is fail-fast and protects memory, but a reverse proxy may be preferable for
  graceful back-pressure. Flagged for the reviewer.
- **Timeout value.** 30 s bounds a stalled client; if any legitimate client holds a long-lived
  keep-alive connection, lower/raise `FALCON_HTTP_RATE_WINDOW`/handler timeout as needed.

## Definition of done (for this set)

From `patch_plan.md`: "N-connection bound; security-header assertion". The focused Phase-2 run
proves the connection bound (503 shed once slots are exhausted) and the security-header assertion,
and the full `tests/phase2 tests/phase3` suite plus `ci/validate.sh` and gitleaks pass at commit
`1cb9ec0`.
