# Audit Run Index

## Metadata

- Name: `repo-deep-dive` · Profile: `falcon-lab` v1.0.0 (pack v1.2.1)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Run type: **full-domain** (first full run; prior findings status-triaged)
- Started: 2026-09-30T07:01Z · Completed: 2026-09-30
- Repos: falcon-build @ `8282d3f` (clean at start; parallel-session activity during the run) · falcon-edge-build @ `45dfed0` (dirty at start — in-flight CI; advanced to `f1c5def` mid-run, agents verified at current HEAD where possible)
- Live host: read-only snapshot `live_snapshot.txt` (2026-09-30T07:01:55Z)
- Prior run: `20260930-0320-falcon-794ba31_edge-2b5bc8b` — triage: **1 verified-fixed · 31 partially-fixed · 53 still-open · 2 regressed** (ND-P2-001, REV-P3-007) · 3 not re-assessed

## Findings

**P0 ×13 · P1 ×80 · P2 ×131 · P3 ×40 = 264** across 36 areas (256 domain/lens + 8 synthesis).

Top P0s:

1. `EVID-P0-001` / `REV-P0-001` / `INV-P0-002` — approval binds a superseded package (`c312ab7`/1,168 vs delivered `3ac6cd4`/2,067); APPROVED not reproducible.
2. `API-P0-001` — live Wazuh/VirusTotal credentials committed in `wazuh_cluster/etc/ossec.conf` and shipped in the 2026-09-30 delivery archive; scanner blind.
3. `LIVE-P0-001` / `RES-P0-002` — alert path is relay-blind; total host loss detectable only ~26 h later; stale monitors read healthy.
4. `LIVE-P0-002` / `RES-P0-001` — backup green-washing: offsite failures invisible (realized 2026-09-30), recovery evidence uncommitted.
5. `XREPO-P0-001` / `INV-P0-001` — pin/sidecar/manifest digest chain broken.
6. `EVID-P0-002` — reviewer disposition is a transcription; JPB recorded as installer (independence unresolved).

Full set: `findings.json`, `risk_register.md`, `follow_up_register.md` (256 rows).

## Gate

**GO WITH CONDITIONS** — lab operation continues; the production-readiness claim is NO-GO until conditions C1–C3 close. Full text and reconciliation: `RELEASE_GATE.md`.

## Reports

All reports complete (68 files in this folder): 45 prompt reports (27 RUN + 8 ADAPTED + 10 N/A short), 5 lens reports, synthesis (`22`, `23`, `40` + finals), companion artifacts (`access_control_matrix.md`, `backup_restore_drill_plan.md`, `incident_tabletop_scenarios.md`, `branch_protection_recommendation.md`, `sbom_license_policy_recommendation.md`, `secret_rotation_runbook.md`). Full list: `audit_manifest.json`.

## Key Outputs

- Executive summary: `EXECUTIVE_SUMMARY.md` · Gate: `RELEASE_GATE.md`
- Registers: `risk_register.md` · `follow_up_register.md` · Roadmap: `roadmap.md` · Patch plan: `patch_plan.md`
- Machine-readable findings: `findings.json` · Manifest: `audit_manifest.json`
- Verification log: `verification_log.md` (2026-09-30 pass: 29 verified-fixed, 19 partially-fixed)
- Decision-log entry (proposed): `decision_log_entry_proposed.md`
- Live snapshot: `live_snapshot.txt`
- Edge mirror: `/home/user/falcon-edge-build/docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/`

## Next Actions

1. Apply `patch_plan.md` **set 1** (release blockers) first; then owner decisions D1–D8 (`follow_up_register.md`).
2. Decision-log entry applied 2026-09-30 (falcon commits `c11fa94..724302e`); ledger entries recorded (decision log, risk register R-31..R-35, redactions).
3. Run a verification-only pass after fixes; re-run synthesis (`22`/`23`/`40`).
4. Scanner interaction fixed (`c11fa94`): `docs/audits/` is exempt from the `long_hex` secret rule; `ci/validate.py` passes with the run in-tree.
