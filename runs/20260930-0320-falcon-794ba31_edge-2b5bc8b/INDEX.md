# Audit Run Index

## Metadata

- Name: `repo-deep-dive`
- Profile: `falcon-lab` v1.0.0 (Repo Deep-Dive Full Hardening pack, base v1.0.0)
- Run: `20260930-0320-falcon-794ba31_edge-2b5bc8b`
- Run type: **lens-focused** (conversion of the six 2026-09-30 audits; domain prompts not executed in this run)
- Audit window: 2026-09-30 ~03:20–03:45 UTC
- Repos: falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b` (edge HEAD moved during the audit: `cfaf09d` → `ced99b3` → `2b5bc8b`)
- Live host: shared lab host, read-only snapshot taken during the audit window
- Converted: 2026-09-30 (post-audit), by the audit session
- Scope limitations: audit account had no root/docker/wg access; live checks limited to systemd state, listeners, filesystem, HTTP endpoints, and read-only DB/metrics where available

## Conversion notes

- The six source reports were **lens** audits, not domain audits. They are converted 1:1 into the four falcon-lab lens reports; findings keep their source severity and get stable IDs.
- Severity mapping: source `High` → `P1`; `Medium` → `P2`; `Low`/`Info` → `P3`; report 05 `Critical` → `P0`; report 06 source priorities `P0/P1/P2` → `P0/P1/P2`. Where a source severity was mixed (`LOW/MEDIUM`), the higher value is used and noted.
- P0/P1 findings are converted in the full shared finding format; P2/P3 findings are indexed compactly (title, evidence pointer, fix) — the full narrative remains in `source_reports/` (hashes below).
- Post-audit remediation known at conversion time is recorded in `follow_up_register.md` only; it does not alter the audit-time record.

## Reports

| Order | Report | Path | Status |
|---:|---|---|---|
| 1 | New-developer lens (falcon + edge) | `lens_new_developer.md` | complete |
| 2 | Independent-reviewer lens (falcon + edge) | `lens_independent_reviewer.md` | complete |
| 3 | Integration lens | `lens_integration.md` | complete |
| 4 | Live-operations lens | `lens_live_operations.md` | complete |

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md`
- Release gate (audit opinion): `RELEASE_GATE.md`
- Risk register: `risk_register.md`
- Roadmap: `roadmap.md`
- Patch plan: `patch_plan.md`
- Follow-up register: `follow_up_register.md`
- Run manifest: `audit_manifest.json`
- Machine-readable findings: `findings.json`
- Source reports (original six audits): `source_reports/`

## Findings Summary

| Severity | Count |
|---|---:|
| P0 | 6 |
| P1 | 22 |
| P2 | 35 |
| P3 | 27 |
| **Total** | **90** |

By area: `ND` 34 · `REV` 25 · `INTG` 15 · `LIVE` 16.

## Top Risks

1. `INTG-P0-001` — pin ↔ delivery digest mismatch; the pinned manifest no longer exists (edge release integrity).
2. `INTG-P0-002` — edge WG peer persistence claim wrong; a bootstrap re-run silently drops the sensor tunnel.
3. `LIVE-P0-001` — offsite backup failed silently; cold tier one day stale; no alert.
4. `LIVE-P0-002` — new-services backup failing/unverified; archival state unproven.
5. `LIVE-P0-003` — data LV losing ~10 GB/day; first signal only at the 5 GiB guard.
6. `REV-P1-001` — published machine artifacts contradict the APPROVED verdict (hard-coded generators).
7. `REV-P1-002` — independence/adoption is attestation-based, not artifact-based.
8. `REV-P1-004` — edge enrollment can escalate to operator access.
9. `REV-P1-005` — edge update-apply trusts an agent-writable request (root code execution).
10. `INTG-P1-001` — no alert covers the edge path.

## Source Report Hashes (sha256)

| Source | sha256 |
|---|---|
| `01-falcon-build-new-developer.md` | `795db75285caa6e2e336ab09d5f7567e13e272b78bd5d5805b7aaba2df0e02ea` |
| `02-falcon-build-reviewer.md` | `47c7436143e70b437cead696ae14aaae7757ca9076c1de315dda1faab86dbd31` |
| `03-falcon-edge-new-developer.md` | `7299d2241f504cb155da4e7bd86b63d5f5b3aaff94d591b97083c4deb842996f` |
| `04-falcon-edge-reviewer.md` | `fb7b32359508950a0c4fdd7ea63993b15e9e37932bddfa5e0986fe5300255bee` |
| `05-integration-two-repos.md` | `9fffd846de174ef3e60dfb8621cb2753ea7246cd1622bcde8712c6f1aa533ad9` |
| `06-live-operations.md` | `7945ef297b8b641490e26894d3cd8d5f4a07fa8adc66f6342e8dbcc9464b7512` |

## Next Actions

1. Apply the patch plan P0 set (see `patch_plan.md`); record in the decision log.
2. Reconcile the delivery artifacts and the independence/adoption chain (`REV-P1-001..003`) — either remediate or record explicit owner acceptance.
3. Re-bind the edge pin and re-verify the release (`INTG-P0-001`) after the edge session pushes and stabilizes.
4. Run a **verification-only pass** (falcon-lab master runner, verification mode) over fixed findings once the tree settles; refresh risk register, gate, and changelog.
5. Schedule the first full domain run (all applicable prompts) when the P0/P1 set is closed.
