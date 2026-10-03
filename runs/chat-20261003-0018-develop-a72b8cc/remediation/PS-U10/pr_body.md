# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Adds W3C Trace Context (`traceparent`) handling at the API edge so a tracing
collector has a standard correlation id across requests and structured logs.
The API continues a valid inbound trace (or starts a new one), echoes the
outgoing `traceparent` response header, and stamps `trace_id`/`span_id` onto
the request-scoped logger. This is the minimal, standards-based first step for
OBS-P2-004; wiring a full OpenTelemetry SDK/exporter and propagating spans
API -> worker -> Supabase remains a follow-up.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U10` — Unassigned OBS findings (catch-all)
- Repo / base: `chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P2-004` | P2 | open -> partially-fixed | W3C trace context + log correlation added; full OTel collector/exporter deferred (draft PR, not merged) |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/lib/trace-context.ts` | New helpers: `parseTraceparent`, `formatTraceparent`, `newTraceContext`, `resolveTraceContext` (W3C spec validation, invalid/zero/`ff` rejected) |
| `apps/api/src/middleware/request-id.ts` | Resolve trace context per request, set `traceparent` response header, add `trace_id`/`span_id` to the child logger |
| `apps/api/src/lib/__tests__/trace-context.test.ts` | 16 unit tests for parse/format/resolve |
| `apps/api/src/middleware/__tests__/request-id.test.ts` | Continue-inbound + new-trace + response-header assertions |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter @chat/api test` | lab `chat` (`172.23.128.51`) | 0 | `remediation/PS-U10/verify.log` — 63 files / 503 tests passed |
| `gitleaks protect --staged --redact` on the staged diff | lab `chat` | 0 | `remediation/PS-U10/gitleaks.log` — "no leaks found" |
| `gitleaks detect --no-git --redact --source .` (full tree) | lab `chat` | 1 | 5 pre-existing Supabase local-dev demo JWT matches in `infra/docker/.env.dev.example` (untouched by this diff); staged-diff scan is clean |

- Secret scan (gitleaks): **pass on the diff** (0 findings on staged changes). Full-tree scan flags only known Supabase local CLI demo keys in a pre-existing example file.
- Scope check (files within patch set): **pass** — 4 files, all under `apps/api` (implementation + tests); patch set declared no explicit file list (catch-all).

## Evidence bundle

- `remediation/PS-U10/diff.patch` — SHA-256 `46270B842CA22776D04DAADAD551D3AE0078E8431053366374036FFFD462F4D1`
- `remediation/PS-U10/manifest.json`
- `remediation/PS-U10/verify.log`
- `remediation/PS-U10/gitleaks.log`

## Risk and rollback

- Risk: **low** — additive middleware/helpers, no dependency or schema change; `x-request-id` behavior preserved.
- Rollback: `git revert fdadf5941c86b0b27182c8289e4812300455e7ce`

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- OBS-P2-004: trace correlation to a collector is available via W3C `traceparent`
  on API requests/responses and `trace_id`/`span_id` in logs. Full OpenTelemetry
  instrumentation and worker/Supabase span propagation are explicitly deferred
  (finding remains `partially-fixed` while this PR is open).
