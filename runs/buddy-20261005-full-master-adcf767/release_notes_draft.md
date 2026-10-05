# Release Notes Draft — buddy `0.1.0` RC (audit delta)

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- This is an audit-generated draft, not a published release note.

## Quality gate evidence (bind to commit)

Lab `ci-runner` executed against `adcf767` in `/var/lib/lab-repos/buddy`:

- `npm ci` — exit 0
- `npm run typecheck` (`tsc --noEmit`) — exit 0
- `npm run test` (`vitest run`, Next.js 15.5.27) — 185/185 passed across 19 files
- `npm run lint` (`next lint`) — exit 0 (deprecation notice only)
- `npm run build` — exit 0 (First Load JS 143 kB)

GitHub Actions: the `install / lint / typecheck / test / build` job is green, but the
`audit / secret scan / license policy` job fails on master (nested postcss). See `CI-P1-001`.

## Gate

**GO WITH CONDITIONS** — 0 P0, 4 P1. The P1s are governance/trust items
(`ARCH-P1-001`, `BP-P1-001`, `BP-P1-002`, `CI-P1-001`), not runtime defects.
