# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-05T05:45:00Z | PS-01 | draft | partially-fixed | 343f56977d9f1db3eb9374a112ae8f57a02cfe7b https://github.com/MaineCyberTech/buddy/pull/35 | Draft PR #35 (remediation/buddy-CI-P1-001): root npm `overrides.postcss` pin to `^8.5.28` replaces the Next.js-vendored `postcss@8.4.31`; `npm audit --audit-level=high --omit=dev` = 0 vulnerabilities and the full local gate is green. Verified-fixed only once merged to `master`. |
| 2026-10-05T05:45:00Z | PS-02 | open | open | - | OWNER-GATED (`BP-P1-001`, `BP-P1-002`): branch protection and the `release` environment are repository settings. Proposal and residual recorded in `OWNER_GATED_PROPOSALS.md`; **no infra changed**. |
| 2026-10-05T05:45:00Z | PS-03 | owner-accepted | owner-accepted | - | `ARCH-P1-001` remains a dated, owned acceptance while the app is guest-only; no server trust boundary is in scope until an account/cloud mode. |
