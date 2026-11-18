# Delta re-audit summary — main@3fa9f636 (2026-11-07)

Scope: changes since the Nov 3 full audit + re-verification of the unresolved items. Not a full 43-domain sweep.

## Counts

| Status | Count |
|---|---:|
| verified-fixed | 22 |
| partially-fixed | 6 |
| open | 19 |
| still-open | 3 |
| regressed | 0 |
| **total** | **50** |

## Open / partial P0–P1

- **SEC-P1-012** (P1, open) — NEW: client roles can still read internal comments on tickets and project tasks (is_internal is not enforced on the API or the RLS policy)
- **BP-P1-004** (P1, still-open) — PR #279 merged into main with required checks pending and zero reviews - live protection does not match the committed payloads (or an unrecorded bypass)
- **CI-P1-001** (P1, still-open) — Production application deploys have no working manual-approval gate
- **CI-P1-003** (P1, still-open) — Production deploy path cannot run; prod environment lacks secrets and protection rules
- **DR-P0-001** (P0, open) — No successful backup has ever run: all four backup/restore workflows still have zero green runs, including the new Garage-primary path
- **DR-P1-004** (P1, partially-fixed) — Encryption is now enforced, but the offsite/second-destination copy is optional, skipped in the documented dev config, and never verified
- **IR-P0-003** (P0, partially-fixed) — The off-box dead-man's switch is configured and fail-closed, but the external heartbeat URL is still unset and never drilled
- **DR-P1-008** (P1, open) — Restore-test workflows hard-code ubuntu-latest and cannot reach the private Garage endpoint the backup workflows now use

## New findings

- **SEC-P1-012** (P1, open) — client roles can still read internal comments on tickets and project tasks (is_internal is not enforced on the API or the RLS policy)
- **SEC-P3-016** (P3, open) — GET /ai/triage returns every triage draft in the org (raw descriptions and first-response drafts) to client roles holding ai:view
- **SEC-P3-017** (P3, open) — SSO callback forwards the caller's entire cookie jar (including mct_session and csrf_token) to the API when only the PKCE verifier is needed
- **SEC-P3-018** (P3, open) — the SSO PKCE start route and the verifier-missing/negative callback paths have no regression tests
- **CI-P1-005** (P1, verified-fixed) — required E2E check is red at the promotion head (Start Supabase fails)
- **SBOM-P1-006** (P1, verified-fixed) — PSF-2.0 is allowed by the full-tree gate but not the PR dependency-review gate or docs
- **CTR-P2-007** (P2, partially-fixed) — global .trivyignore suppresses fixable HIGH CVEs in the new node-exporter image
- **INFRA-P3-011** (P3, verified-fixed) — promtool CI gate pins Prometheus v3.5.1 while production runs v3.15.1

## Prior status changes vs Nov 3

- `SEC-P3-014`: verified-fixed -> partially-fixed (API-key exemption kept).
- `CTR-P2-007`, `CTR-P3-006`, `INFRA-P2-003`: verified-fixed -> partially-fixed (node-exporter exceptions/stale docs).
- `TEST-P2-010`: open -> verified-fixed (required checks green before the Nov 7 promotion).
- `DR-P1-004`, `IR-P0-003`: verified-fixed -> partially-fixed (offsite copy unproven; watchdog URL unset).

## Operator blockers

- `DR-P0-001`: `SUPABASE_DB_URL` missing/stale, Garage access key unknown, no non-empty restore drill.
- `BP-P1-004`, `CI-P1-001`, `CI-P1-003`: branch protection and prod environment/reviewers.
- `IR-P2-011`: alert-path exercise still not green.

## Remediation (2026-11-07)

- **SEC-P1-012** -> verified-fixed (#384)
- **SEC-P3-016** -> verified-fixed (#384)
- **SEC-P3-017** -> verified-fixed (#384)
- **SEC-P3-018** -> verified-fixed (#384)
- **DR-P1-008** -> verified-fixed (#383)
- **DR-P2-010** -> verified-fixed (#383)
- **DR-P2-011** -> verified-fixed (#383)
- **CI-P3-016** -> verified-fixed (#383)
- **EVOL-P2-003** -> verified-fixed (#383)
- **SBOM-P3-012** -> verified-fixed (#383)
- **OBS-P3-009** -> verified-fixed (#383)
- **CI-P2-012** -> verified-fixed (ai-reviewer#2 + #385)
- **CI-P2-013** -> verified-fixed (ai-reviewer#2 + #385)

## Backup verification (2026-11-07)

Storage-backup is green end-to-end (runs 42356362156, 42415467689; encrypted
archive in Garage). `DR-P0-001` is now partially-fixed; the DB backup still
needs `SUPABASE_DB_URL`.

## Final remediation (2026-11-07)

- `CI-P3-017`, `CI-P3-018` -> verified-fixed (ai-reviewer#3 + #390)
- `DR-P3-010` -> verified-fixed (#389)

## Alert path (2026-11-07)

`IR-P2-011` -> verified-fixed: the exercise passed end-to-end after #394 removed the no-op Slack receiver (webhook total 1->2, failed 0); evidence recorded in #399.

