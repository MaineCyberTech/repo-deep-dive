# Chat verify summary — develop@49bf424 (2026-11-07)

Re-verification of the Oct 4 audit's actionable findings plus new issues in the touched areas.

## Counts

| Status | Count |
|---|---:|
| verified-fixed | 7 |
| partially-fixed | 12 |
| open | 56 |
| regressed | 0 |
| owner-accepted | 1 |
| **total** | **76** |

## P1

- **FILE-P1-001** (open) — Scheduled `expired_uploads` cleanup hard-deletes every chat-uploads object older than 7 days, including avatars and message attachments
- **EXEC-P1-001** (open) — Release gate must remain conditional pending P1/P2 remediation
- **FINAL-P1-001** (open) — Release gate must remain conditional pending P2 remediation
- **INFRA-P1-001** (open) — Development and production share one Terraform state key and resource address

## New findings

