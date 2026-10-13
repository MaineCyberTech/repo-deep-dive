# 27_webhook_delivery_replay_idempotency_audit — Prompt 27 - Webhook Delivery, Replay, and Idempotency Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `27_webhook_delivery_replay_idempotency_audit.md` (area WH, prompt)

## Verification Performed

# Webhook Delivery, Replay, and Idempotency Audit — NOT APPLICABLE

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261013-bench-main-72c1873
- Repository: `C:\temp\bench-test`
- Branch: `main`
- Commit SHA: `72c18734aea2e5b3381254b74205d0b2944bafab` (observed HEAD at audit time)
  - Note: the domain brief stated `b9167095b08c2f45a814e88e09d88decbd0ea885`; that commit is the
    parent release tag `VERSION 1.11.3` in this history (`git log`: `72c18734` →
    `a3dc49b8` → `b9167095`). The audited tree is two commits ahead of the brief's SHA. The
    working tree also contained uncommitted edits (see Verification Performed); `server/benchd.py`
    itself was **not** modified.
- Generated at: 2026-10-13
- Auditor: domain subagent (27_webhook_delivery_replay_idempotency_audit)
- Area code: WH
- Output path (pack convention): `docs/audits/{name}/{run}/27_webhook_delivery_replay_idempotency_audit.md`
- Scope limitations: read-only; no network/lab access required or used; static review only.

## Scope

This domain covers **inbound/outbound webhooks**: HTTP callbacks delivered to or from third-party
endpoints, with signature (HMAC) verification, timestamp tolerance, replay nonces, idempotency
keys, retry/backoff, dead-letter queues, tenant scoping, and delivery observability.

Reviewed: the entire repository tree, with emphasis on the only server (`server/benchd.py`), the
reporting/upload clients (`bench/benchreport.py`, `bench/upload.py`, `server/import_results.py`),
the web dashboard (`server/web/`), docs (`docs/CONTROL_PLANE.md`, `docs/DATA.md`, `AGENTS.md`,
`README.md`), tests (`tests/`), and the three GitHub workflows (`.github/workflows/`).

**Not reviewed:** the Windows/Linux benchmark engines (`bench/*.ps1`, `bench/*.py` outside the
reporting client) except where they issue outbound HTTP; prebuilt artifacts under `dist/` and
`results/` beyond a keyword scan.

## Evidence Reviewed

- `server/benchd.py` — the control plane (REST + SSE + SQLite). The only HTTP surface that accepts
  structured POST bodies and the only code that issues outbound HTTP.
- `bench/benchreport.py:487-514` — the shared runner→server client (`_req`, bearer token,
  `POST /api/v1/register`, …).
- `bench/upload.py`, `server/import_results.py` — GitHub/control-plane upload clients.
- `docs/CONTROL_PLANE.md:99-137, 202-213` — API reference and security model.
- `.github/workflows/build-app.yml`, `release.yml`, `build-iso.yml` — CI triggers.
- `tests/test_control_plane.py` — control-plane test suite.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `grep -r "webhook\|Webhook\|WEBHOOK"` over repo | command | locate any webhook code/config | **0 matches.** No webhook subsystem exists. |
| `grep -r "hmac\|HMAC\|X-Signature\|X-Hub\|signature"` | command | signature verification | Only `Get-EnvInfo.ps1:41` (Defender AV signature age) and audit-doc prose about *binary* supply chain. No webhook signing. |
| `grep -r "nonce\|replay\|Replay"` | command | replay protection | Only `bench/cpu_bench.py:124` (AES-GCM test nonce) and GPU `nvidia-smi` "Replays" counters in `results/**`. No request-replay protection. |
| `grep -r "idempot\|retry\|backoff\|dead.?letter\|dlq\|callback"` | command | retry/idempotency/DLQ | Only UI retry copy (`server/web/index.html:25`), curl `--retry` for a download (`bench/Sample-Sensors.ps1:43`), Tk callback plumbing, and registration retry loops. No idempotency/DLQ subsystem. |
| `git -C C:\temp\bench-test rev-parse HEAD` | command | bind evidence to a commit | `72c18734…`; tree dirty (`git status` shows `server/web/app.js`, several `bench/*` modified). |
| `.github/workflows/*` scan (`on:`, `repository_dispatch`) | read | inbound webhook triggers | Only `workflow_dispatch` (manual). No `repository_dispatch`/webhook trigger. |
| `docs/CONTROL_PLANE.md:99-137` | read | inbound endpoint inventory | Enumerates every API route; all are internal runner/UI routes, none are callbacks to/from third parties. |

## Executive Summary

**This domain is not applicable to `bench-test`.** The repository is a workstation
benchmark/stress toolkit plus a stdlib control plane (`server/benchd.py`); it has **no webhook
system** — no inbound webhook receiver, no outbound webhook dispatcher, no event-subscription or
signed-callback mechanism, and no third-party webhook integration.

Everything that could resemble this domain is ordinary first-party RPC:

- **Inbound "endpoints"** are the control-plane REST API (`server/benchd.py:626-1161`), consumed
  only by the toolkit's own runners/dashboards, authenticated with a shared operator token
  (`BENCHD_TOKEN`) or a per-runner API key (`server/benchd.py:562-616`, `docs/CONTROL_PLANE.md:202-213`).
- **Outbound delivery** is limited to GitHub REST calls (`server/benchd.py:307-321, 359-379`;
  `bench/upload.py`) and publishing run data to the control plane (`bench/benchreport.py:487-514`).
  None of these are webhooks; none are replayed or retried by a delivery queue.

Because no webhook surface exists, the required special checks (raw-body signature verification,
timestamp tolerance, replay nonce, idempotency keys, webhook retry/backoff, DLQ, webhook tenant
scoping) have **no target to evaluate**. Per the brief, an accurate "not applicable" result is
returned: **0 findings**.

The closest genuine analogs — noted for the implementation agent's awareness, but *out of domain
scope and not filed as webhook findings* — are the control plane's command-delivery path and its
idempotency of run creation; these are covered by other domains (auth/API, reliability).
Strengths observed: per-runner API keys are minted with `secrets.token_urlsafe` and compared with
`secrets.compare_digest`; body size is capped (`MAX_BODY`, `server/benchd.py:55, 545-559`); the
static-file handler uses `os.path.commonpath` to prevent traversal (`server/benchd.py:1254-1273`).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Inbound webhook receiver | — | receive third-party signed callbacks | **Absent** | N/A | No route, no signature handling. |
| Outbound webhook dispatcher | — | deliver events to external URLs | **Absent** | N/A | No subscription registry or delivery queue. |
| Event models | `events` table, `server/benchd.py:123-125, 1109-1116` | run log/event lines | Present, but is a DB log row, not a webhook event envelope | N/A | No event type/versioning/signature. |
| Signature verification | — | HMAC over raw body | **Absent** | N/A | Auth is bearer token / API key only. |
| Timestamp tolerance / replay nonce | — | reject stale/replayed requests | **Absent** | N/A | No nonce/timestamp logic anywhere. |
| Idempotency keys | — | dedupe retried deliveries | **Absent** | N/A | Not applicable to internal RPC. |
| Retry backoff | `bench/benchreport.py` (client retry loop) | re-send reporting to server | Present client-side | Low | Not a webhook retry queue. |
| Dead-letter queue | `reap_stale_commands`, `server/benchd.py:1376-1385` | mark un-acked commands failed | Analog only | Low | DB status flip, not a DLQ with redrive. |
| Secrets | `BENCHD_TOKEN`, per-runner `api_key`, `server/benchd.py:562-616, 1163-1218` | control-plane auth | Present | N/A | Bearer/key, not webhook signing secret. |
| Delivery logs | `log_message`, `server/benchd.py:515-525` | HTTP access logging | Present | Low | Redacts `?token=`; not a webhook delivery log. |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Inbound endpoints (webhook) | 0 | No webhook route; `server/benchd.py:626-1161` is internal RPC | N/A | None — domain not present |
| Outbound delivery (webhook) | 0 | Outbound limited to GitHub/control-plane (`server/benchd.py:307-379`) | N/A | None |
| Event models (webhook) | 0 | `events` is a plain log table (`server/benchd.py:123-125`) | N/A | None |
| Signature verification | 0 | No HMAC/`X-Signature` anywhere (grep) | N/A | None |
| Timestamp tolerance | 0 | No timestamp validation (grep) | N/A | None |
| Replay nonce | 0 | No nonce logic (grep) | N/A | None |
| Idempotency keys | 0 | No dedupe key handling | N/A | None |
| Retry backoff | 0 (webhook) | No webhook retry queue | N/A | None |
| Dead-letter queues | 0 (webhook) | `reap_stale_commands` is an analog only | N/A | None |
| Secrets | 0 (webhook) | Auth uses bearer/API keys, not signing secrets | N/A | None |
| Tenant scoping | 0 (webhook) | Single-operator model | N/A | None |
| Payload schema/size | 0 (webhook) | `MAX_BODY` cap, no webhook schema | N/A | None |

Scores are `0` = "absent / not assessable" per the shared scoring model, because the domain itself
does not exist — not because a required control is missing from an existing webhook system.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| WH-001 | Inbound endpoints | `server/benchd.py:626-1161` | bearer token / API key, not webhooks | N/A | — | None |
| WH-002 | Outbound delivery | `server/benchd.py:307-379`; `bench/upload.py` | GitHub REST + control-plane POST | N/A | — | None |
| WH-003 | Event models | `server/benchd.py:123-125, 1109-1116` | DB log rows | N/A | — | None |
| WH-004 | Signature verification | grep: none | absent | N/A | — | None |
| WH-005 | Timestamp tolerance | grep: none | absent | N/A | — | None |
| WH-006 | Replay nonce | grep: none | absent | N/A | — | None |
| WH-007 | Idempotency keys | grep: none | absent | N/A | — | None |
| WH-008 | Retry backoff | `bench/benchreport.py` | client-side reporting retry | N/A | — | None |
| WH-009 | Dead-letter queues | `server/benchd.py:1376-1385` | failed-command status flip (analog) | N/A | — | None |
| WH-010 | Secrets | `server/benchd.py:562-616, 1163-1218` | bearer/API keys | N/A | — | None |
| WH-011 | Tenant scoping | `docs/CONTROL_PLANE.md:202-213` | single operator token | N/A | — | None |
| WH-012 | Payload schema/size | `server/benchd.py:55, 545-559` | `MAX_BODY` = 24 MiB | N/A | — | None |

## Findings

None. The webhook domain is not present in this repository; filing webhook findings would require
inventing functionality that does not exist. `{"findings": []}`.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Webhook-specific risks (forgery, replay, duplicate delivery, silent DLQ loss) cannot apply | Low | n/a | n/a | No webhook surface (grep/read evidence above) | None required; revisit if a webhook/integration feature is added |

## Recommendations

### Immediate / Release Blocking

None for this domain.

### This Week

None for this domain.

### This Month

- If/when any external integration or callback is introduced, design it up front with a signed
  payload (HMAC over the raw body), a timestamp + tolerance window, a replay nonce/idempotency key,
  bounded retry with backoff, and an admin-visible DLQ. There is no existing system to retrofit.

### Later / Platform Evolution

- The control plane's roadmap (`docs/CONTROL_PLANE.md:273-278`) lists Prometheus/`/metrics` and
  alerting. If outbound alert notifications (e.g. a Slack/HTTP alert sink) are added later, apply
  the webhook checklist then; treat this domain as "not applicable until then".

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| (none) | Domain absent | — | — |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Re-run domain 27 if a webhook/integration feature lands | P3 | platform | S | A webhook feature existing |

## Suggested Tests

Not applicable — there is no webhook behavior to test. (Candidate consumer tests exist for the
control-plane API in `tests/test_control_plane.py`, but they exercise internal RPC, not webhooks.)

## Suggested Documentation Updates

- Optionally add a one-line "not applicable" note in a future integration design doc stating that
  the toolkit has no webhook surface today. No existing doc claims a webhook feature, so nothing is
  currently misleading.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Will a future roadmap item add outbound alert/webhook delivery? | Determines whether domain 27 becomes applicable | `docs/CONTROL_PLANE.md:273-278` mentions alerting but no webhook; confirm with maintainers |
| Does the domain brief's commit SHA drift matter? | Evidence binding | Brief says `b9167095`; HEAD is `72c18734` (two commits ahead) |

## Appendix

- Commands run and observed results (all read-only):
  - `grep -r "webhook|Webhook|WEBHOOK"` → no matches.
  - `grep -r "hmac|HMAC|signature|Signature|sign_"` → 13 matches, all non-webhook (Defender AV
    signature, supply-chain prose).
  - `grep -r "nonce|replay|Replay"` → AES-GCM test nonce (`bench/cpu_bench.py:124`), GPU replay
    counters in `results/**`, `nvidia-smi` logs.
  - `grep -r "idempot|retry|backoff|dlq|DLQ|callback"` → UI retry copy, curl `--retry`, Tk
    callbacks, registration retry loops.
  - `.github/workflows` → `workflow_dispatch` only; no `repository_dispatch`/webhook triggers.
- Closest analogs (out of scope, no finding filed): internal command delivery is at-most-once —
  `GET /api/v1/runners/<id>/commands` flips `queued`→`sent` on read (`server/benchd.py:773-786`),
  and un-acked commands are later marked `failed` by `reap_stale_commands` (`server/benchd.py:1376-1385`).

## Findings

_No findings in this domain._
