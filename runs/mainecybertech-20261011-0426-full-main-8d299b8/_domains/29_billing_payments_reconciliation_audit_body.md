# Billing, Payments, and Reconciliation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: MaineCyberTech/mainecybertech (target worktree `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (`8d299b8d`)
- Generated at: 2026-10-11
- Auditor: domain subagent (area `BILL`, prompt `29_billing_payments_reconciliation_audit.md`)
- Area code: BILL
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/29_billing_payments_reconciliation_audit.md`
- Scope limitations: read-only static review. No `pnpm install`/build/test run (resource discipline on the 1 vCPU host); test coverage statements are from reading test files, not executing them. No Stripe API or production access — webhook payload-shape claims are from the code and its unit-test fixtures.

## Scope

Reviewed: billing API routes, Stripe webhook handling, entitlement derivation and middleware, the `stripe-reconcile` worker task, billing schema + RLS, SDK billing surface, portal/admin billing UI, billing tests (API, worker, web component, e2e), and billing docs. Not reviewed (owned by other domains): general webhook-delivery machinery (WH), RLS policy correctness in depth (RLS/DATA), secrets rotation (SECRET), notification delivery internals (NOTIF), and the vendored prompt packs.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/routes/billing.ts` | Source | All billing APIs: summary/invoices/subscriptions/payments/customer, sync, portal session | Read in full |
| `apps/api/src/routes/webhooks.ts` | Source | Stripe event handling, idempotency, refunds, void, payment lifecycle | Read in full |
| `apps/api/src/lib/entitlements.ts`, `apps/api/src/middleware/entitlement.ts` | Source | Entitlement derivation + server-side enforcement | Read in full |
| `apps/worker/src/tasks/stripe-reconcile.ts`, `apps/worker/src/schedule-config.ts` | Source | Reconciliation job + daily schedule | Read in full |
| `apps/api/src/middleware/org-access.ts`, `apps/api/src/lib/admin-scope.ts`, `apps/api/src/lib/roles.ts` | Source | Tenant scoping used by billing reads | Read in full |
| `apps/api/src/lib/idempotency.ts`, `apps/api/src/app.ts` | Source | Webhook claim TTL + raw-body capture | Read in full |
| `supabase/migrations/5302026_...v3.sql` (billing tables/enum/RLS), `5302028_seed_permissions.sql`, `5302128_role_catalog_expansion.sql` | Migrations | Schema + permission truth | Targeted reads |
| `apps/api/src/__tests__/billing.test.ts`, `webhooks.test.ts`, `middleware-entitlement.test.ts`; `apps/worker/src/__tests__/tasks/task-handlers.test.ts`; `apps/web/__tests__/.../billing/page.test.tsx`; `apps/web/e2e/portal/billing.spec.ts` | Tests | Coverage of the fixed P1s and remaining gaps | Read, not executed |
| `apps/web/app/(portal)/portal/billing/BillingPageClient.tsx`, `apps/web/app/(admin)/admin/organizations/[orgId]/billing/AdminBillingClient.tsx`, `ClientPortalEntitlementsForm.tsx` | UI | Customer/admin billing surfaces, raw PM id, sync button | Read in full |
| `docs/BILLING.md`, `docs/modules/billing.md` | Docs | Documented behavior vs implementation | Read in full |
| `infra/digitalocean/prometheus.rules.yml`, `alertmanager.tmpl.yml` | Config | Alerting coverage for billing/reconcile | Grepped |

## Verification Performed

| Command | Observed result |
|---|---|
| `git log -1 --format='%H %s'` | `8d299b8dc271…` Merge PR #168 (promote develop to main) |
| `git merge-base --is-ancestor 9c0b88c HEAD` | 9c0b88c IS ancestor of HEAD (previous-run commit is in history) |
| `git log --oneline 9c0b88c..HEAD -- apps/api/src/routes/billing.ts apps/api/src/routes/webhooks.ts apps/worker/src/tasks/stripe-reconcile.ts apps/api/src/lib/entitlements.ts apps/api/src/middleware/entitlement.ts docs/BILLING.md` | Only `adea562c` (Jira/JSM raw-body + M365 replay hardening); billing logic unchanged since 9c0b88c |
| `grep -c 'starting_after' apps/api/src/routes/billing.ts` | 0 — no Stripe pagination |
| `grep -c 'has_more' apps/api/src/routes/billing.ts` | 0 |
| `grep -c 'charge.dispute\|credit_note\|invoice.payment_action_required' apps/api/src/routes/webhooks.ts` | 0 |
| `grep -c 'notify\|createNotification' apps/api/src/routes/webhooks.ts` | 0 — no payment-failure notification |
| `grep -c 'quantity' apps/api/src/routes/webhooks.ts apps/api/src/routes/billing.ts` | 0/0 — seat quantity ignored |
| `grep -n 'trial_end\|cancel_at_period_end\|interval'` in webhook/sync/reconcile | Only `stripe-reconcile.ts:16` (unused interface field) |
| `grep -rn 'recordWebhookDelivery' apps/api/src --include=*.ts \| grep -v __tests__` | Inbound handlers emit only `"success"`; `"failed"` used only by the outbound dispatcher |
| `grep -n 'alert:' infra/digitalocean/prometheus.rules.yml` | 7 alerts; none for task failures, webhook processing or billing drift |
| Read of `apps/api/src/__tests__/webhooks.test.ts`, `billing.test.ts`, `middleware-entitlement.test.ts`, `task-handlers.test.ts:67-74` | P1 fixes are covered by unit tests; sync pagination, reconcile logic and refund-ordering are not |

## Executive Summary

Billing is a Stripe mirror (webhooks + manual sync + daily reconcile) with a server-enforced entitlement layer. The three P1 findings from the previous run are genuinely fixed and re-verified at `8d299b8d`: entitlements are enforced with `requireEntitlement` on all six gated routers, the `payments` table is written by both the webhook and `POST /billing/sync`, and refund/void/uncollectible lifecycle events are ingested. The customer portal has a Stripe-hosted billing portal, and tenant scoping on `POST /billing/sync` was hardened.

The remaining risk is not missing features but **silent drift and false success**: webhook DB writes are never checked (a failed mirror write is still acknowledged as processed), `POST /billing/sync` does not paginate and silently skips failed Stripe calls while reporting success, and the reconcile job neither detects drift nor alerts (it even returns `ok:true` with per-customer errors). A late-retried Stripe event can also overwrite a refunded payment back to `succeeded`. Plan-state fidelity is limited (no interval/trial/cancel/seat fields), and failed payments still have no notification or dunning path. Recommended next actions: (1) fail webhook writes loudly + metric; (2) paginate sync and report partial failures; (3) add drift metrics/alerts and reconcile logic tests; (4) migrate billing reads to the hardened `admin-scope` pattern; (5) add trial/interval/seat columns and dunning UI.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Billing APIs | `apps/api/src/routes/billing.ts` | summary, invoices, subscriptions, payments, customer, sync, portal session | Implemented | Medium | Sync unpaginated; writes unchecked |
| Stripe webhook | `apps/api/src/routes/webhooks.ts:131-349` | Ingest Stripe events | Implemented | Medium | Errors swallowed; no failure metric |
| Entitlement derivation | `apps/api/src/lib/entitlements.ts` | Org → module set | Implemented | Low | All-disabled override falls back |
| Entitlement middleware | `apps/api/src/middleware/entitlement.ts` | Server-side plan gate | Implemented, tested | Low | Fail-open on lookup error (documented) |
| Reconcile worker | `apps/worker/src/tasks/stripe-reconcile.ts` | Daily suspend-on-terminal | Implemented | Medium | No drift detection/alerting/tests |
| Billing schema | `supabase/migrations/5302026_...v3.sql:510-574` | Mirror tables + RLS | Implemented | Low-Medium | No interval/trial/seat/voided_at |
| Billing SDK | `packages/sdk/src/billing.ts` | Typed client surface | Implemented | Low | Mirrors API |
| Portal billing UI | `apps/web/.../portal/billing/*` | Customer view + Manage/Sync | Implemented | Low-Medium | Raw PM id; sync 403 for most roles |
| Admin billing UI | `apps/web/.../organizations/[orgId]/billing/*` | MSP view | Implemented | Low | Same PM-id rendering |
| Entitlement admin UI | `ClientPortalEntitlementsForm.tsx` | Per-tenant module provisioning | Implemented | Low | Override cannot revoke all |
| Billing docs | `docs/BILLING.md`, `docs/modules/billing.md` | Operator/reference docs | Stale in 4 places | Low | See docs finding |
| Alerting | `infra/digitalocean/prometheus.rules.yml` | Platform alerts | No billing/task rules | Medium | Drift is unobservable |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Billing pages | 3 | Portal + admin pages; `page.test.tsx` render tests | No past-due banner; raw PM id; sync button 403 | Dunning banner; card descriptor; permission-aware button |
| Subscription/plan models | 2 | `5302026_...v3.sql:521-534` | No interval/trial/cancel/seat columns | Migration + upsert wiring |
| Entitlement checks | 4 | `entitlement.ts` + 6 wired routers + tests | Fail-open (documented); all-disabled override | Override semantics test; bypass alert |
| Billing APIs | 3 | `billing.ts`; tenant-scope tests | No pagination; unchecked writes; inner join | Paginate; check errors; left join |
| Payment provider integration | 3 | Stripe REST via `httpClients.stripe`; billing portal | No retry/backoff on sync calls | Retry + error reporting |
| Webhooks | 3 | Signature verify, atomic dedup, refunds | Unchecked writes; no failure metric; ordering | Fail loudly; monotonic statuses |
| Invoices/status records | 3 | enum + upserts + overdue derivation | overdue only derived on sync/webhook; no voided_at | Scheduled overdue refresh; timestamps |
| Reconciliation jobs | 2 | daily `stripe-reconcile`; one env-missing test | No drift detection/alerting/tests; ok:true on errors | Drift metrics + write-back + tests |
| Failed payments | 2 | `invoice.payment_failed` upsert | No notification/dunning | Billing notification + banner |
| Refund/cancel/trial states | 2 | `charge.refunded`, void/uncollectible; status only | No trial/cancel fields; refund amount/date; disputes | Schema + webhook expansion |
| Seat counts | 1 | `items.data[0].price` only | No quantity/seat column | Persist quantity |
| Usage billing | 0 | no usage/meter code (grep) | Entirely absent | N/A unless metered plans planned |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| BILL-001 | Billing pages | `BillingPageClient.tsx`, `AdminBillingClient.tsx` | Org-scoped fetch via SDK | Raw PM id; sync button for all roles | P3 | Permission-aware UI, card descriptor |
| BILL-002 | Subscription/plan models | `5302026_...v3.sql:521-534` | status + period + amount | interval/trial/cancel/seat missing | P2 | Migration + upserts |
| BILL-003 | Entitlement checks | `entitlement.ts:142-172`; 6 routers | 402 gate, admin bypass | all-disabled override; fail-open | P3 | Override semantics; alert |
| BILL-004 | Billing APIs | `billing.ts` | auth + org access; tenant-scoped sync | no pagination; unchecked writes; inner join; unscoped reads for cross-tenant roles | P2/P3 | Paginate; check errors; left join; admin-scope |
| BILL-005 | Payment provider integration | `httpClients.stripe` | Bearer key, timeout client | no retry/backoff on sync | P3 | Retry transient Stripe failures |
| BILL-006 | Webhooks | `webhooks.ts:131-349` | constructEvent verify; atomic dedup; claim release on throw | unchecked DB writes; no failure metric; ordering | P2 | Check results; failed metric; monotonic status |
| BILL-007 | Invoices/status records | enum + upserts | paid/open/void/uncollectible/overdue | overdue only refreshed on sync/webhook; no voided_at; epoch paid_at risk | P2/P3 | Scheduled refresh; guards; timestamps |
| BILL-008 | Reconciliation jobs | `stripe-reconcile.ts` | daily, terminal-only suspend, active-preference | no drift/alert/tests; ok:true on errors | P2 | Drift metrics + write-back + tests |
| BILL-009 | Failed payments | `webhooks.ts:176-213` | invoice status updated | no notification/dunning | P2 | Notify + portal banner |
| BILL-010 | Refund/cancel/trial states | `webhooks.ts:302-328` | refund + void status; trialing status | no trial/cancel fields; best-effort refunds; disputes | P2 | Schema + handlers |
| BILL-011 | Seat counts | upserts read `price` only | none | quantity ignored | P3 | Persist quantity |
| BILL-012 | Usage billing | no usage/meter code | none | absent | N/A | Confirm product need |

## Detailed Review (highlights)

### Item: Stripe webhook processing

- Evidence: `apps/api/src/routes/webhooks.ts:131-349`.
- What it does: verifies the Stripe signature with `constructEvent`, claims `stripe-<event.id>` atomically (TTL 24h), maps invoice/subscription/payment/refund/void events, writes an audit event + delivery row, releases the claim on thrown errors.
- Current controls: signature verification, atomic dedup, best-effort `resolveBillingRefs`, PII-safe delivery logging.
- Missing controls: every Supabase write result is ignored (`:190-210`, `:230-246`, `:254-261`, `:281-294`, `:323-326`); no inbound failure metric; no ordering/monotonic guard; refunds only update an existing row.
- Risks: silent mirror drift; refund state overwritten by late retries; failed writes acknowledged as processed.

### Item: `POST /billing/sync`

- Evidence: `apps/api/src/routes/billing.ts:207-376`.
- What it does: resolves and authorizes the target org, fetches invoices/subscriptions/payment_intents per customer, upserts with `onConflict` on Stripe ids, audits `billing.sync`.
- Current controls: `billing:manage` gate, `resolveAdminTenantScope` check, audit event.
- Missing controls: fixed page sizes (20/10/20) with no `starting_after`; non-`ok` responses skipped silently; no row/error counts in the response.
- Risks: false-success reconciliation; stale history for high-volume customers.

### Item: `stripe-reconcile` worker

- Evidence: `apps/worker/src/tasks/stripe-reconcile.ts:57-152`.
- What it does: daily (env-gated) per-org fetch of the active/trialing (else most recent) subscription; suspends approved memberships on terminal Stripe statuses; never touches invoices or writes Stripe state back.
- Missing controls: drift metrics, alerting, state write-back, meaningful tests; returns `ok:true` even when `errors>0` (`:146`).
- Risks: undetectable drift; entitlements keep reading stale local subscription state.

### Item: Entitlements

- Evidence: `apps/api/src/lib/entitlements.ts`, `apps/api/src/middleware/entitlement.ts`, wired in 6 routers, `middleware-entitlement.test.ts`.
- Strengths: single source of truth shared by bootstrap and middleware; 402 envelope; 30s cache; admin bypass; tested.
- Gaps: all-disabled provisioning falls back to the subscription set (`entitlements.ts:102-108` vs the admin form's "Saving overrides the subscription-derived default set"); deliberate fail-open on lookup error.

## Findings

Canonical records (severity, evidence, status, note) are in `29_billing_payments_reconciliation_audit.json`. Titles:

1. **Module entitlements are derived but not enforced server-side** — P1, `verified-fixed` (re-verified at 8d299b8d).
2. **`payments` table is never populated; payment history is silently empty** — P1, `verified-fixed`.
3. **Missing Stripe webhook events leave refunds, void, and payment lifecycle unrecorded** — P1, `verified-fixed`.
4. **No refund and incomplete trial/cancel state handling** — P2, `partially-fixed`.
5. **`POST /billing/sync` does not paginate Stripe results** — P2, `still-open`.
6. **Reconciliation job has no drift detection, alerting, or tests** — P2, `still-open`.
7. **Failed payments produce no notification or dunning visibility** — P2, `still-open`.
8. **Subscription/invoice schema lacks trial, interval, and void-lifecycle fields** — P2, `partially-fixed`.
9. **Webhook raw body typed as `string` but consumed as `Buffer`** — P3, `still-open`.
10. **Billing email stored in plaintext and raw Stripe payment-method id rendered to users** — P3, `still-open`.
11. **Stripe webhook DB writes ignore errors and still mark the event processed** — P2, `open` (new).
12. **Out-of-order or late-retried Stripe events can overwrite terminal payment states** — P2, `open` (new).
13. **Billing read endpoints fall back to all-tenant scope for cross-tenant roles without an admin-scope guard or audit** — P2, `open` (new).
14. **`invoice.paid` paid_at handling writes epoch dates (sync) or throws when status_transitions is missing (webhook)** — P3, `open` (new).
15. **Payments list uses an inner join, hiding payments not linked to an invoice** — P3, `open` (new).
16. **Entitlement override cannot revoke all modules (all-disabled falls back to the subscription set)** — P3, `open` (new).
17. **Subscription mirror ignores seat quantity and the billing summary excludes trialing plans** — P3, `open` (new).
18. **Portal 'Sync from Stripe' button is shown to client roles that lack billing:manage** — P3, `open` (new).
19. **Billing docs contradict the implementation (sync gate, webhook verification, reconcile source, payment statuses)** — P3, `open` (new).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Silent billing drift from unchecked webhook writes | P2 | Medium | Finance/entitlement state diverges from Stripe | `webhooks.ts:190-326` unchecked results | Fail loudly + failed-delivery metric + retry |
| Partial sync reported as success | P2 | Medium-High | Stale invoice/payment history | `billing.ts:256-359` | Paginate + per-object counts/errors |
| Refund overwritten by late retried event | P2 | Medium | Refund shown as collected | `webhooks.ts:281-316`; 24h claim TTL | Monotonic status/ordering guard |
| Undetected reconcile failures/drift | P2 | Medium | Suspensions missed; no alert | `stripe-reconcile.ts:141-146` | Drift metrics + alert + ok:false on errors |
| Cross-tenant billing read without audit | P2 | Low-Medium | MSP `admin` role sees all tenants unaudited | `billing.ts` GETs + `org-access.ts:146` | admin-scope + audit |
| Trial/seat/interval blind spots | P3 | High | Misleading plan amounts/labels | schema + `/mo` hardcode | Schema + UI fields |

## Recommendations

### Immediate / Release Blocking

None — no P0/P1 open at this commit. The three P1s are `verified-fixed`.

### This Week

- Make Stripe webhook writes fail loudly: check each Supabase result, emit `recordWebhookDelivery("failed", ...)`, and let the claim release so Stripe retries (finding 11).
- Guard `paid_at` in both sync and webhook paths; add tests for paid invoices without `status_transitions` (finding 14).

### This Month

- Paginate `POST /billing/sync` and report partial failures per object type (finding 5).
- Add drift detection + write-back + failure surfacing + tests to `stripe-reconcile`; alert on drift/task failure (finding 6).
- Add a monotonic status guard for payments (refunded/partially_refunded terminal) (finding 12).
- Migrate billing GETs to `resolveAdminTenantScope`/`applyOrgScope` + audit implicit cross-tenant reads (finding 13).
- Add trial/interval/cancel/seat columns and persist them; add `voided_at` (findings 4, 8, 17).
- Create a billing notification + past-due portal banner on `invoice.payment_failed` (finding 7).

### Later / Platform Evolution

- Handle `charge.dispute.*`, `credit_note.*`, `customer.subscription.trial_will_end`; store refund amount/date (finding 4).
- Left-join payments and show card descriptors; permission-aware sync button (findings 15, 18, 10).
- Adopt a usage/metered-billing design only if metered plans are planned (currently absent).
- Capture `req.rawBody` as a Buffer and drop the cast (finding 9).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Check + log webhook write errors | Converts silent drift into observable failure | `apps/api/src/routes/webhooks.ts` | Unit test with a mocked upsert error asserting a failed metric/throw |
| Guard `paid_at` branches | Removes epoch writes / 500 retry loops | `billing.ts`, `webhooks.ts` | Test paid invoice with/without `status_transitions` |
| Left join payments | Unlinked payments appear | `billing.ts:179` | API test asserting a null-invoice payment is returned |
| Hide sync button without `billing:manage` | Removes guaranteed-403 UX | `BillingPageClient.tsx` | Component test with/without permission |
| Fix the 4 stale doc lines | Operators get the right model | `docs/BILLING.md`, `docs/modules/billing.md` | Doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Webhook write failure handling + metric | P2 | billing/backend | S | None |
| Sync pagination + error reporting | P2 | billing/backend | S | None |
| Reconcile drift metrics/alerts/tests | P2 | worker/platform | M | Metrics stack (OBS) |
| Payment status monotonic guard | P2 | billing/backend | S | None |
| Billing reads admin-scope migration | P2 | API platform | S | None |
| Trial/interval/seat schema + upserts | P2 | data/platform | M | Migration sequencing |
| Dunning notification + UI | P2 | billing + notifications | S | NOTIF domain |
| Refund amount/date + disputes/credit notes | P3 | billing/backend | M | Schema |
| Raw-body Buffer typing | P3 | API platform | S | None |
| Entitlement override semantics | P3 | billing/backend | S | None |

## Suggested Tests

- Unit: webhook upsert failure → metric/throw and claim release; paid invoice without `status_transitions`; refunded payment + late `payment_intent.succeeded` stays refunded; void then late `invoice.paid` stays void.
- Integration: `POST /billing/sync` with a two-page mocked Stripe response asserts all rows upserted and `has_more` loops; one Stripe call fails → response reports the error.
- Worker: `stripe-reconcile` terminal vs `past_due`/`trialing`; errors>0 → `ok:false`; drift metric emitted; dryRun never mutates memberships.
- API/security: billing GETs with no `organization_id` as an `admin`-key holder → scoped to their orgs (or 403), and an audit/impersonation entry exists.
- E2E: portal billing as `client_user` → no Sync button (or explained 403); past-due banner renders after `invoice.payment_failed`.
- CI: keep `middleware-entitlement.test.ts` green; add an all-disabled-entitlements case.

## Suggested Documentation Updates

- `docs/BILLING.md`: webhook verification is full signature verification (not presence); reconcile queries `billing_customers` + `subscriptions`; document `STRIPE_WEBHOOK_SECRET`; payments statuses include `refunded`/`partially_refunded`; note sync page limits until pagination lands.
- `docs/modules/billing.md`: sync gate is `billing:manage` (not `requireAdmin`); add the new trial/interval/seat fields once shipped.
- `docs/SECRETS_ROTATION.md`: already covers Stripe keys — no change needed (verified present).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is metered/usage billing planned? | Entire usage-billing surface is absent | Product decision |
| Should MSP `admin` (not is_super_admin) see all-tenant billing? | Determines the intended fix for finding 13 | Owner decision; admin-scope precedent says super_admin-only |
| Do refunds/disputes need full financial records (amounts, dates)? | Determines schema scope for finding 4 | Finance requirements |
| Is the 24h webhook claim TTL acceptable vs Stripe's ~3-day retry window? | Affects ordering/duplicate handling | Stripe delivery policy + idempotency review (WH domain) |

## Appendix

- Re-verification lineage: previous run `mainecybertech-20261004-full-main-9c0b88c` (BILL rows) → this run `8d299b8d`. Since 9c0b88c, only `adea562c` touched billing-adjacent code (Jira/JSM raw-body + M365 replay); all other BILL files are byte-identical to the previous verification point, so the three P1 `verified-fixed` statuses carry forward with fresh evidence.
- Register status summary: 3 `verified-fixed` (P1), 2 `partially-fixed` (P2), 5 `still-open` (3 P2 + 2 P3), 9 new `open` (3 P2 + 6 P3).
