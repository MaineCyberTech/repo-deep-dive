# Executive Summary — Snowride

- Run: `20261003-0018-main-59e12b9`
- Repo: C:\temp\snowride @ `main` / `59e12b9`
- Profile: base (Full Hardening)
- Date: 2026-10-03

## What was audited

A mature server-authoritative browser snowboarding game: Next.js 15 web client, a Node/Socket.IO realtime service, shared TypeScript contracts/game-core packages, and a Supabase/Postgres data plane with 56 migrations and 16 manual SQL negative suites. Audit was read-only and static (no `node_modules`, no production access).

## Headline result

| Severity | Count |
|---|---|
| P0 (critical) | 0 |
| P1 (high) | 6 |
| P2 (medium) | 25 |
| P3 (low) | 15 |
| **Total** | **46** |

**Release gate: GO WITH CONDITIONS.**

## Strengths

- **AuthN/AuthZ**: server-side JWKS verification with issuer/audience/expiry; admin-vs-ops split; admin-only PII surfaces; per-socket/per-user rate limits; zod validation on every socket event and submission (`apps/realtime/src/auth.ts`, `server.ts`).
- **Data plane**: default-deny RLS with explicit deny policies; `SECURITY DEFINER` RPCs with fixed `search_path`; own-row scoping (`supabase/migrations/0002`, `0017`, …).
- **Containers/CI**: non-root, read-only rootfs, dropped capabilities, digest-pinned images; least-privilege CI (`contents: read`, no deploy authority); built-bundle secret gate.
- **Server authority**: scoring, eligibility, rating, XP and purchases are computed server-side.

## Top risks (why the gate is conditional)

1. **Release identity is self-asserted and stale** — `LAUNCH_OWNER_SIGNATURE` is free text; the checked-in attestation binds to commit `e5fea775` and migration `0055`, while HEAD is `59e12b9` and the schema head is `0056`. (SEC-P1-001, DATA-P1-001, FINAL-P1-001)
2. **No SBOM bound to the release**, and vulnerability/license checks run only on a daily host lane, not per-PR. (SUPPLY-P1-001, SUPPLY-P2-001)
3. **Alerting/scheduling is host-only**, not version-controlled or reproducible. (OBS-P1-001)
4. **Branch protection / required checks unproven**, so CLI gates may be advisory. (CI-P1-001)
5. **RLS negative suites are manual**, so tenant-isolation regressions are not caught by CI. (DATA-P2-001, TEST-P2-003)

## Conditions to reach GO

1. Re-attest at `59e12b9` / migration `0056` with cryptographic signature verification and a head-equality CI check.
2. Add branch protection (required `foundation` + `migrations` checks), SHA-pin actions, and a per-PR dependency audit + repository secret scan.
3. Generate and bind an SBOM; move license/OSV checks into CI.
4. Commit and self-test the alerting schedule; define RPO/RTO and SLOs.
5. Run the SQL negative suites in the existing CI migrations job.

## Scope note

No P0 and no exploitable P1 runtime defect was reproduced. The P1 set is release/supply-chain governance. All findings are static-evidence backed; dynamic test execution was not possible in this environment and is marked `Unknown` where relevant.

## Detailed inputs

Domain reports `01`, `02`, `03`, `06`, `07`, `08`, `09`, `10`, `11`, `14`, `21`; consolidation in `22`; decision in `RELEASE_GATE.md`; work lists in `risk_register.md`, `roadmap.md`, `patch_plan.md`.
