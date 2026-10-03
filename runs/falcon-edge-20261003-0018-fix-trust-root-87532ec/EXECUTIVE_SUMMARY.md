# Executive Summary

- Repository: MaineCyberTech/falcon-edge — `C:\temp\falcon-edge`
- Branch / commit: fix/trust-root / 87532ec
- Audit run: 20261003-0018-fix-trust-root-87532ec (repo-deep-dive Full Hardening, base profile)
- Verdict: **GO WITH CONDITIONS** (lab); production readiness not claimed

## What this is

A lab implementation of a Raspberry Pi edge sensor program: a stdlib-only Python
control plane (mTLS, SQLite, Ed25519-signed desired state/updates/recovery) managing
`falcon-agent` devices with a bounded loss-accounting queue, signed-directive
verification, and a root-side signed-update verify/swap/rollback path. Delivery is a
credential-bearing Raspberry Pi image built in CI and published as a release.

## Findings at a glance

| Severity | Count |
|---|---:|
| P0 | 0 |
| P1 | 3 |
| P2 | 27 |
| P3 | 12 |
| Total | 42 |

## Strengths

- Pinned operator trust root; CN never grants operator; ingestion attributed to the
  certificate identity (`src/falcon_control/service.py`, `pki.py`).
- Root-side update verification with TOCTOU-closed hashing, safe extraction, and
  power-loss recovery (`image/overlay/.../falcon-update-verify.py`).
- Bounded, checksummed queue with honest loss accounting and DLQ.
- Strong CI: SHA-pinned actions, gitleaks/zizmor/actionlint/shellcheck/ruff,
  `ci/validate.sh`, contract/model drift checks, license gate, boot smoke.
- 21 alert rules with runbook links and monitoring-of-the-monitoring.

## Biggest risks

1. **P1 — revocation reset on re-enrollment** (`h_enroll` sets CONFIGURING for a
   REVOKED/RETIRED sensor). SEC-P1-001.
2. **No alert delivery** — rules are visible only in Prometheus/Grafana; no pager.
   OBS-P2-001.
3. **CI/supply-chain integrity** — unpinned CI deps, unverified tool downloads, no
   git-history secret scan. SC-P2-001/002/003.
4. **Data growth** — unbounded idempotency/events tables, no migrations/FKs.
   DATA-P2-001/002/003.
5. **Drift** — stale test counts/cadence, unguarded generated artifacts, working-tree
   deploy. HYG-P2-001/002, TEST-P2-001, ARCH-P2-001.

## Release gate

GO WITH CONDITIONS for lab operation; see `RELEASE_GATE.md` §Conditions (C1–C4).
Production readiness remains insufficient-evidence pending owner gates P10-G02/G04/G06.

## Next actions

1. Fix C1 (enrollment revocation guard) + regression test — immediate.
2. Fix C2/C3 (CI merge binding + tool/dep pinning + history scan) — this week.
3. Correct documentation drift; add idempotency retention — this week.
4. Fix C4 (alert delivery) and data migrations/retention — this month.

## Files

- Domain reports: `01`, `02`, `03`, `06`, `07`, `08`, `09`, `10`, `11`, `14`, `21`, `22`, `23`.
- Finals: `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`, `risk_register.md`, `roadmap.md`, `patch_plan.md`.
