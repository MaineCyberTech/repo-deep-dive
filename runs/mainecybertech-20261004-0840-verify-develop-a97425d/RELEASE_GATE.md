# Release Gate — post-merge verification

**Repo:** `MaineCyberTech/mainecybertech` · **Commit:** `a97425db` (develop) ·
**Date:** 2026-10-04

## Gate: develop — GO WITH CONDITIONS

| Criterion | State |
|---|---|
| Zero open/regressed P0 at the merged commit | PASS — `DATA-P0-001` verified-fixed |
| Zero open/regressed P1 at the merged commit | FAIL (operator) — `CI-P1-001` prod environment provisioning remains |
| Every merged patch set reconciled | PASS — 16/16 reconciled; 13 sets fully merged, 3 sets partially (owner/operator residuals) |
| Deploy pipeline green | PASS — `deploy-do` run 37188587849 success; droplet healthy at `a97425db` |
| Machine re-audit regressions | PASS — no new P0/P1 |
| CI at the merge commit | PASS except pre-existing CodeQL alert (issue #31) |

## Gate: prod — NO-GO (unchanged, operator)

The `prod` environment still lacks the application secrets (`SUPABASE_*`,
`JWT_SECRET`, `FIELD_ENCRYPTION_KEY`, `TURNSTILE_SECRET_KEY`, …) and the
migrations for the current schema; the prod deploy path is fail-closed and will
not start until those are provisioned. This is `CI-P1-001`.

## Residual P1 register

| ID | State | Required action |
|---|---|---|
| `CI-P1-001` | still-open | Provision `prod` secrets + reviewers; then run a prod deploy drill |
| `FINAL-P1-001` | verified-fixed | Release-gate docs at the commit (`docs/RELEASE_GATE.md`) |

## Notes

- Gate verdicts are valid only at `a97425db`; later commits require their own
  verification pass.
- The dev Turnstile secret is Cloudflare's documented always-pass **test** pair;
  replace with the real widget pair before a public production launch.
