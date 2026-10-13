# 29_billing_payments_reconciliation_audit — Prompt 29 - Billing, Payments, and Reconciliation Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `29_billing_payments_reconciliation_audit.md` (area BILL, prompt)

## Verification Performed

# Billing, Payments, and Reconciliation Audit

## Audit Metadata

- Audit name: repo-deep-dive (bench-dive domain subagent)
- Run: 20261013-bench-test-domain29
- Repository: `C:\temp\bench-test`
- Branch: `main`
- Commit SHA audited: `72c18734aea2e5b3381254b74205d0b2944bafab` (VERSION `1.11.4`)
  - Note: the domain brief cites `b9167095b08c2f45a814e88e09d88decbd0ea885` (VERSION `1.11.3`),
    which is an ancestor of HEAD. All evidence below was captured at the live checkout/HEAD.
- Generated at: 2026-10-13
- Auditor: domain subagent — `29_billing_payments_reconciliation_audit`
- Area code: BILL
- Output path (pack convention): `docs/audits/{name}/{run}/29_billing_payments_reconciliation_audit.md`
  (this run writes to the bench-dive driver output path, not into the read-only target)
- Scope limitations: Target is read-only. No network calls, no state mutation. Review is a static
  read + `git grep` sweep at the audited commit.

## Scope

Reviewed the entire `C:\temp\bench-test` working tree (tracked content) for any evidence of a
billing, payment, subscription, entitlement, webhook, invoice, reconciliation, seat-count, or
usage-billing system. This includes the Python control plane (`server/benchd.py`), the
`bench/` toolkit modules, `server/web/` front end, `live/`, `packaging/`, `.github/workflows/`,
`tests/`, and `docs/`.

**Finding: the domain is NOT APPLICABLE to this repository.** `bench-test` is a self-hosted
workstation benchmark / stress / fleet toolkit. There is no commerce surface of any kind: no
billing pages, no plan or subscription model, no entitlement checks, no billing API, no payment
provider integration, no webhooks, no invoices or status records, no reconciliation jobs, no
failed-payment handling, no refund/cancel/trial states, no seat counts, and no usage metering that
is billed. Because no such functionality exists, there is nothing to score above the "absent"
baseline and **no findings are raised**.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md:1-51` | Docs | Declares product purpose | "workstation benchmark, stress & fleet control plane"; 12 test groups (sys/gpu/cpu/ram/disk/combined/fullsoak/net/nvenc/llm/fan/gfx). No pricing/plan/billing section. |
| `LICENSE:1-16` | Legal | Distribution/licensing model | Proprietary "AS IS" license; no per-seat / per-subscription / license-key billing scheme. |
| `server/benchd.py` | Source | Control plane | Stdlib HTTP + SSE + SQLite server for runs/inventory; auth is a shared bearer token, not accounts/plans. |
| `server/benchd.conf.example` | Config | Server config keys | No Stripe/provider keys, no plan/price/entitlement config. |
| `bench/benchreport.py:346-546` | Source | Runner identity | `runner_id` / `api_key` are fleet identity + bearer auth for runners, not billing seats. |
| `tests/harness.py:26,56-91` | Tests | Auth test fixture | Uses `TOKEN = "test-token"`; confirms bearer-token model, no billing tests. |
| `.github/workflows/*.yml` | CI | Workflows | `release.yml`, `build-app.yml`, `build-iso.yml` — build/release only; no payment/billing jobs. |
| `docs/` | Docs | Product docs | `CONTROL_PLANE.md`, `DATA.md`, `FUTURE_WORK.md`, `METHODOLOGY.md`, `PHASE_TIMINGS.md` — no billing docs. |
| prior audit `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/` | Artifacts | Prior review | Only lexical hit for the sweep was the word "reconcile" (relicense README/LICENSE), unrelated to billing. |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse HEAD` → `72c18734aea2e5b3381254b74205d0b2944bafab` | Command | Bind evidence to commit | Actual HEAD; brief cited `b9167095` (ancestor, VERSION 1.11.3). |
| `git log -1` / `git branch --show-current` / `Get-Content VERSION` | Command | Commit + branch + version | `main`, VERSION `1.11.4`. |
| `git grep -iIl -e stripe -e billing -e subscription -e entitlement -e payment -e webhook -e invoice -e reconcil -e paywall -e "checkout session" -e "seat count" -e "usage billing" HEAD` | Command (case-insensitive, all tracked files) | Prove absence | Returned only the 5 prior-audit files; all matches are the word "reconcile" in a governance/README context. Zero commerce terms. |
| `git grep -inE "<same terms>" HEAD -- docs/audits` | Command | Disambiguate matches | Every hit is "reconcile README/LICENSE" — no billing meaning. |
| ripgrep over tree: `\b(stripe\|paypal\|paddle\|braintree\|adyen\|billing\|invoice\|subscription\|entitlement\|price_id\|customer_id\|payment\|webhook\|refund\|...)\b` | Command | Corroborate absence | **No matches found.** |
| ripgrep over tree: `\b(pricing\|plan\|tier\|trial\|quota\|metered\|credit card\|revenue\|monetiz\|commercial\|purchase\|charge\|paywall\|upgrade to pro\|pro plan)\b` | Command | Corroborate absence | Only incidental matches: `patch_plan.md`, `roadmap.md` reference, and a Linux `Disk quota exceeded` string in an example log — none billing-related. |
| `git cat-file -t b9167095...` / `git merge-base --is-ancestor` | Command | Confirm brief-vs-HEAD | `b9167095` is a commit and an ancestor of HEAD; brief is one release stale. |
| Read of `README.md`, `LICENSE`, `docs/` listing, `server/` listing, `bench/benchreport.py` identity paths, `tests/harness.py` | Read | Understand product + auth model | Confirms non-commerce product with shared-token auth. |

Reproduction status of headline claim ("billing domain is not applicable"): **supported** —
the case-insensitive, whole-tree `git grep` for the full commerce vocabulary returns no
commerce code, config, tests, or docs; the only lexical hits are the benign word "reconcile".

## Executive Summary

`bench-test` is an internal/proprietary, self-hosted workstation benchmarking and fleet-control
toolkit (Windows PowerShell + Python + Bash, stdlib control plane, live-USB build, packaged app).
It is not a SaaS product with customers, plans, or payments. There is **no billing domain to
audit**: no billing pages, no subscription/plan model, no entitlement gating, no billing APIs, no
payment-provider integration, no webhook delivery, no invoices/status records, no reconciliation
jobs, no failed-payment handling, no refund/cancel/trial states, no seat counts, and no usage
billing. The only "account"-like concept is a fleet runner identity (`runner_id` + bearer
`api_key`/`token`) used to authenticate benchmark runners to the control plane — an
infrastructure-auth concern, not a commercial-entitlement one.

**Strengths (as verified):** the repo has no payment data to leak, no third-party payment
credentials in config, and no billing logic that could drift from provider state — the entire
class of billing risk is absent by construction.

**Risks:** none in this domain. The residual note is purely a governance/prior-audit artifact
(reconcile the public repo visibility against the proprietary `LICENSE`), which belongs to the
GOV domain, not BILL — it is recorded here only because it is the sole lexical hit of the sweep.

**Recommended next actions:** none for BILL. If monetization is ever planned (e.g., selling
licenses or a hosted tier), re-run this prompt against the implementation at that time; until
then no BILL backlog items, tests, or docs are warranted.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Billing pages | — | Sell/plan/manage UI | Absent | None | No such UI in `server/web/` (dashboard shows runs/trends/inventory only). |
| Subscription/plan models | — | Plan/tier state | Absent | None | No plan/tier schema in `server/benchd.py` SQLite. |
| Entitlement checks | — | Gate features by plan | Absent | None | No feature gating; access is a shared bearer token. |
| Billing APIs | — | Checkout/invoice APIs | Absent | None | `server/benchd.py` exposes run/inventory/control APIs only. |
| Payment provider integration | — | Stripe/Paddle/etc. | Absent | None | No provider SDK, keys, or calls anywhere. |
| Webhooks | — | Provider event ingestion | Absent | None | No inbound webhook route; server is SSE/poll based. |
| Invoices/status records | — | Billing records | Absent | None | No invoice/subscription tables. |
| Reconciliation jobs | — | Ledger vs provider | Absent | None | No scheduled billing jobs. (Word "reconcile" appears only re: README/LICENSE.) |
| Failed payments | — | Dunning/retry | Absent | None | N/A. |
| Refund/cancel/trial states | — | Lifecycle states | Absent | None | N/A. |
| Seat counts | — | Per-seat licensing | Absent | None | `runner_id` is fleet identity, not a licensed seat. |
| Usage billing | — | Metered billing | Absent | None | Telemetry (`*.telemetry.csv`, run metrics) is not metered for billing. |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Billing pages | 0 | No billing UI in `server/web/app.js`; README lists benchmark dashboards only | Entirely absent | None (out of product scope) |
| Subscription/plan models | 0 | No plan/tier schema in `server/benchd.py` | Entirely absent | None |
| Entitlement checks | 0 | Auth is a shared bearer token (`tests/harness.py:26`); no feature gating | Entirely absent | None |
| Billing APIs | 0 | `server/benchd.py` API surface is runs/runners/schedules only | Entirely absent | None |
| Payment provider integration | 0 | Whole-tree grep finds no provider terms | Entirely absent | None |
| Webhooks | 0 | No webhook route/verification code | Entirely absent | None |
| Invoices/status records | 0 | No invoice tables/records | Entirely absent | None |
| Reconciliation jobs | 0 | No billing jobs; "reconcile" only in prior-audit wording | Entirely absent | None |
| Failed payments | 0 | No payment flow | Entirely absent | None |
| Refund/cancel/trial states | 0 | No lifecycle states | Entirely absent | None |
| Seat counts | 0 | `runner_id`/`api_key` are infra identity, not seats | Entirely absent | None |
| Usage billing | 0 | Telemetry is not metered for billing | Entirely absent | None |

Scores are `0` = "absent or not assessable" per the shared scoring rules, explained by the
whole-tree absence evidence above. A score of 0 here reflects *out-of-scope absence*, not a defect.

## Detailed Review

### Item: Product purpose and commerce surface (composite)

- Evidence: `README.md:1-51`; `LICENSE:1-16`; directory listings of `server/`, `docs/`.
- What it does: Benchmarks and stress-tests workstations and optionally aggregates runs via a
  self-hosted control plane.
- How it appears to work: Runners execute test groups, emit JSON/Markdown reports and telemetry,
  and optionally report to `benchd` (HTTP + SSE + SQLite) authenticated by a token.
- Dependencies: Python stdlib; PyTorch/numpy for compute phases. No payment SDKs.
- Current controls: Shared-secret bearer token for the control plane; no accounts/plans.
- Missing controls: None required — no billing surface exists.
- Risks: None in domain.
- Recommended improvement: None.
- Suggested tests: None for BILL.
- Suggested docs: None for BILL.

### Item: Runner identity (`runner_id`, `api_key`) vs. seats

- Evidence: `bench/benchreport.py:346,355,449-455,512-524,538-546`; `bench/agent.py:115-117`;
  `tests/harness.py:26,56-91`.
- What it does: Registers each benchmark runner with the control plane and authenticates it.
- How it appears to work: A random `runner_id` (uuid in `bench-agent.json`) plus an `api_key`
  issued by the server; the key becomes the bearer token.
- Dependencies: `server/benchd.py` runner registry.
- Interpretation: This is **infrastructure identity/authentication**, not per-seat licensing or
  entitlement. No plan, quota, or charge attaches to a runner.
- Risks: None in this domain (auth-model review is the AUTH/control-plane domain's remit).
- Recommended improvement / tests / docs: none for BILL.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| BILL-001 | Billing pages | No billing UI in `server/web/` | N/A | Out of scope | — | None |
| BILL-002 | Subscription/plan models | No plan schema in `server/benchd.py` | N/A | Out of scope | — | None |
| BILL-003 | Entitlement checks | Shared bearer token (`tests/harness.py:26`) | Token auth only | Out of scope | — | None |
| BILL-004 | Billing APIs | `server/benchd.py` API surface | N/A | Out of scope | — | None |
| BILL-005 | Payment provider integration | Whole-tree grep: none | N/A | Out of scope | — | None |
| BILL-006 | Webhooks | No webhook routes | N/A | Out of scope | — | None |
| BILL-007 | Invoices/status records | No invoice tables | N/A | Out of scope | — | None |
| BILL-008 | Reconciliation jobs | No billing jobs | N/A | Out of scope | — | None |
| BILL-009 | Failed payments | No payment flow | N/A | Out of scope | — | None |
| BILL-010 | Refund/cancel/trial states | No lifecycle states | N/A | Out of scope | — | None |
| BILL-011 | Seat counts | `runner_id` = infra identity | N/A | Out of scope | — | None |
| BILL-012 | Usage billing | Telemetry not metered for billing | N/A | Out of scope | — | None |

## Findings

None. `{"findings": []}` is the accurate result: the domain is not applicable to this repository,
and no evidence contradicts that.

(Finding format, status vocabulary, and severity model from `00_SHARED_AUDIT_RULES.md` apply but
are unused because there is nothing to report.)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| *(none in BILL)* | — | — | — | Whole-tree absence, see Verification Performed | N/A |

Note: the only related item in the prior audit corpus is a **GOV** finding
(`GOV-P3-001`, public repo vs. proprietary `LICENSE`) — outside this domain and not counted here.

## Recommendations

### Immediate / Release Blocking

None for BILL.

### This Week

None for BILL.

### This Month

None for BILL.

### Later / Platform Evolution

- **If and only if** monetization is introduced (hosted tier, paid licenses, per-seat billing),
  design it with: server-side entitlement gating, idempotent + reconciled webhook handling, an
  invoice/status source of truth, and reconciliation tests — then re-run this prompt. No such work
  exists today.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| *(none)* | No billing surface exists | — | — |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| *(none for BILL)* | — | — | — | — |

## Suggested Tests

None for BILL. (The domain has no code to test; the appropriate control is the whole-tree absence
sweep already performed, which is reproducible via the `git grep` commands in Verification
Performed.)

## Suggested Documentation Updates

None for BILL. The product docs (`README.md`, `docs/*`) already describe a non-commerce product;
adding a "Billing: not applicable" note is optional and low value. If a commercial tier is ever
built, add `docs/BILLING.md` describing plans, entitlement gating, webhook idempotency, and
reconciliation at that time.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there any private/out-of-tree commercial wrapper (billing service, license server) around `bench-test`? | Would move BILL from N/A to in-scope | A separate repository or deployment config; none found in this tree |
| Does the proprietary `LICENSE` imply per-seat/per-org licensing enforced anywhere? | Could imply a license-key/seat mechanism | No license-key or seat enforcement code found; `api_key` is infra auth only |
| Brief cited commit `b9167095` (VERSION 1.11.3) but HEAD is `72c18734` (VERSION 1.11.4) | Evidence should bind to the intended commit | Re-run at the intended SHA if it differs materially; both contain no billing code |

## Appendix

### Absence sweep (raw)

- `git grep -iIl -e stripe -e billing -e subscription -e entitlement -e payment -e webhook -e invoice -e reconcil -e paywall -e "checkout session" -e "seat count" -e "usage billing" HEAD`
  → only 5 files, all prior-audit docs, all matches = the word **"reconcile"** (README/LICENSE
  relicense text). No commerce terms.
- `git grep -inE "<same>" HEAD -- docs/audits` → confirms every hit is "reconcile README/LICENSE".
- ripgrep `\b(stripe|paypal|paddle|braintree|adyen|billing|invoice|subscription|entitlement|price_id|customer_id|payment|webhook|refund|...)\b` over the tree → `No matches found`.
- ripgrep `\b(pricing|plan|tier|trial|quota|metered|credit card|revenue|monetiz|commercial|purchase|charge|paywall|...)\b`
  → incidental only: `patch_plan.md`/`roadmap.md` filenames, and a Linux `Disk quota exceeded`
  telemetry string in `examples/omarchy-20261009/...` (OS error text, not billing).

### Product composition (context)

Test groups per `README.md:38-51`: `sys`, `gpu`, `cpu`, `ram`, `disk`, `combined`, `fullsoak`,
`net`, `nvenc`, `llm`, `fan`, `gfx`. Control plane (`benchd`) exposes runs, runners, schedules,
trends, compare, console, and inventory over HTTP+SSE backed by SQLite. None of these are billed.

### Verification bind

- `git rev-parse HEAD` = `72c18734aea2e5b3381254b74205d0b2944bafab`
- `git branch --show-current` = `main`
- `VERSION` = `1.11.4`
- `git merge-base --is-ancestor b9167095... HEAD` = true (brief commit is an ancestor)

## Findings

_No findings in this domain._
