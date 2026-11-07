# Delta re-audit — main@3fa9f636 (2026-11-07)

Scope: the changes since the Nov 3 full re-audit target (`main@6b7aa1a5`),
plus re-verification of the six unresolved findings. This is a **delta**, not
a full 43-domain sweep; untouched domains are not re-claimed.

## Lenses

1. **G1 — Security / auth / tenancy:** Kestrel SSO PKCE + callback origin,
   CSRF, client visibility, tenant scope.
2. **G2 — CI / supply chain / containers / testing:** AI reviewer and bot
   approval, Dependabot holds, majors (dotenv 18, chromatic 18, bullmq 6,
   tailwind-merge 3, jsdom 30), Alpine patch upgrades, image scans.
3. **G3 — Backups / DR / infra / observability:** offsite Garage path,
   configurable runner, backup secrets, empty-dev allowance, restore evidence,
   deploy clean checkout.

Previous run: `runs/mainecybertech-20261103-0748-full-main-6b7aa1a`.

Known operator blockers (re-verify, do not re-report as code defects):
`DR-P0-001` (DB URL / Garage key), `BP-P1-004`, `CI-P1-001/003`,
`IR-P2-011`, `TEST-P2-010`.
