# Billing, Payments, and Reconciliation Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: BILL
- Status: N/A — self-hosted, license-free lab; no billing or payment subsystem
- Scope limitations: read-only; no payment provider, plan or invoice system exists to exercise

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Payment provider SDKs | `grep -rIln -i -E 'stripe\|paddle\|braintree\|paypal\|checkout\|payment' <code dirs>` | 0 real hits; matches were false positives (`actions/checkout` in CI docs, `persist-credentials`) |
| Subscription/plan/entitlement models | `ls falcon-edge-build/api/schemas` | Sensor lifecycle schemas only (Enrollment, Heartbeat, UpdateManifest, …); no plan, seat, usage or entitlement object |
| Billing pages/APIs | 0 HTML/CSS/JS/TS files; `grep -nE '^  /' api/openapi/falcon-edge-v1.yaml` | No billing route or UI |
| Ownership/licensing | `README.md` §"License / ownership" | "Owner: Maine Cyber Tech" — no paid product license referenced |
| License-free services | `live_snapshot.txt` systemd descriptions | `falcon-nfacctd.service` "nfacctd NetFlow/IPFIX collection (license-free)"; `falcon-pmacct.service` "… (license-free)" |
| Dependency licensing policy | `mct/docs/DEPENDENCIES.md` | License column per artifact; "No proprietary binaries committed without license review" (line 61) |
| Billing-like field | `mct/config/examples/client-profile.example.yml` | `billing_label` — a report/scorecard label for future clients, not payment logic |

## Evidence Reviewed

- `/home/user/falcon-build/README.md` — license/ownership section
- `/home/user/falcon-build/mct/docs/WHITELABEL.md` + `mct/config/examples/client-profile.example.yml` — `billing_label`/invoice wording in client templates only
- `/home/user/falcon-build/mct/docs/DEPENDENCIES.md` — license inventory and the no-proprietary-binaries rule
- `/home/user/falcon-build/docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/live_snapshot.txt` — license-free service descriptions
- `/home/user/falcon-edge-build/api/schemas/` — no commercial state models

## Not Applicable / Future Readiness

**Why N/A.** The lab is self-hosted and license-free: no billing pages, no subscription/plan models, no entitlement checks, no payment provider integration, no invoices, no reconciliation jobs, no seat counts, no usage billing, no payment data to protect. The `billing_label` field and "invoices" wording in the MCT white-label templates are branding/reporting labels for a future service business; they contain no payment logic. Domain score: **0 (not assessable)**.

**What is adjacent.** Cost control for the lab is infrastructure efficiency (disk, retention, resource sizing) — prompt 15 — and third-party service dependencies (e.g. offsite snapshot storage) belong to prompts 11/12. The MCT first-client go/no-go is a commercial planning document, but the audit scope contains no automated billing surface.

**Future readiness trigger.** If MCT begins invoicing clients with automated plans/entitlements, this prompt becomes applicable and needs: a plan/entitlement model gated server-side, a payment provider integration with idempotent, reconciled webhooks, invoice/status records, dunning/failed-payment handling, refund/cancel/trial states, audit logs, and explicit handling rules for payment-sensitive data (PCI scope). Today none of that exists.

**Findings:** none — no applicable first-party surface.
