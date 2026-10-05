# 29_billing_payments_reconciliation_audit — Prompt 29 - Billing, Payments, and Reconciliation Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `29_billing_payments_reconciliation_audit.md` (area BILL, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| BILL-P1-001 | P1 | Module entitlements are derived but not enforced server-side |
| BILL-P1-002 | P1 | `payments` table is never populated; payment history is silently empty |
| BILL-P1-003 | P1 | Missing Stripe webhook events leave refunds, void, and payment lifecycle unrecorded |
| BILL-P2-001 | P2 | No refund and incomplete trial/cancel state handling |
| BILL-P2-002 | P2 | `POST /billing/sync` does not paginate Stripe results |
| BILL-P2-003 | P2 | Reconciliation job has no drift detection, alerting, or tests |
| BILL-P2-004 | P2 | Failed payments produce no notification or dunning visibility |
| BILL-P2-005 | P2 | Subscription/invoice schema lacks trial, interval, and void-lifecycle fields |
| BILL-P3-001 | P3 | Webhook raw body typed as `string` but consumed as `Buffer` |
| BILL-P3-002 | P3 | Billing email stored in plaintext and raw Stripe payment-method id rendered to users |
