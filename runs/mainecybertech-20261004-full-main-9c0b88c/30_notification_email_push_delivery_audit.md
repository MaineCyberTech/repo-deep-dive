# 30_notification_email_push_delivery_audit — Prompt 30 - Notification, Email, and Push Delivery Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `30_notification_email_push_delivery_audit.md` (area NOTIF, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| NOTIF-P1-001 | P1 | Notification preferences are stored and displayed but never enforced on any send path |
| NOTIF-P1-002 | P1 | API-originated notifications bypass the dedup unique index |
| NOTIF-P1-003 | P1 | No delivery observability: email/notification failures are silent and unalerted |
| NOTIF-P2-001 | P2 | Web Push channel is entirely absent (no subscriptions, no VAPID, no service worker) |
| NOTIF-P2-002 | P2 | SMTP remains optional; email silently degrades to no-op in production |
| NOTIF-P2-003 | P2 | Worker lacks an `unhandledRejection` handler (independently verified) |
| NOTIF-P2-004 | P2 | Scheduled reminder inserts and email sends are not atomic; retries can double-send |
| NOTIF-P2-005 | P2 | Sensitive ticket content is stored and emailed verbatim with no sensitivity filter |
| NOTIF-P2-006 | P2 | API inline email fallback has no retry and ignores the send result |
| NOTIF-P3-001 | P3 | No email template system; repetitive inline HTML diverges between senders |
| NOTIF-P3-002 | P3 | `sms` channel is a dead preference option; UI copy misstates enforcement |
| NOTIF-P3-003 | P3 | SSE polling fallback interval is not cleared on unmount |
