## 2026-09-30 — repo-deep-dive full audit run 20260930-0701-falcon-8282d3f_edge-45dfed0

- Scope: falcon-build @ `8282d3f` (clean at start) · falcon-edge-build @ `45dfed0` (dirty at start; advanced to `f1c5def` mid-run) · shared live host (read-only snapshot 07:01:55Z)
- Lenses: ND · REV · INTG · LIVE · ADV; findings: **P0 ×13 / P1 ×80 / P2 ×131 / P3 ×40** (264 total; prior-run 90/90 triaged: 1 verified-fixed · 31 partially-fixed · 53 still-open · 2 regressed)
- Run folder(s): `falcon-build/docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/`; edge mirror at `falcon-edge-build/docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/`
- Gate opinion: **GO WITH CONDITIONS** — lab operation continues; the production-readiness claim is NO-GO until C1–C3 close (approval re-review/rebind + reviewer artifact; credential rotation + scanner fix + package rebuild; edge release rebind/sidecar + pin verifier), then C4–C5 (dead-man/alert path; backup truth)
- Reconciliation: the program's APPROVED verdict stands per its own flow. Deltas found: superseded approval binding (`c312ab7`/1,168 vs delivered `3ac6cd4`/2,067), transcription-based independence (JPB), hardcoded `FINAL_RESPONSE` verdict, committed credentials in `ossec.conf` + 2026-09-30 archive. Recommended reconciliation: re-review/rebind through the program's review/adoption flow; never revoke/grant here.
- Follow-up: `follow_up_register.md` (256 rows; owners: falcon 125 · edge 53 · both 44 · falcon/ops 21 · owner 13); owner decisions D1–D8; verification pass planned after patch set 1
- Note: this run's files under `docs/audits/` currently fail falcon `ci/validate.py` (secret-scan `long_hex` false positive — finding `CI-P2-001`); allowlist or scanner fix required before the next publication.

<!--
This entry is PROPOSED by the audit (wave 4) and applied by the operator through the
normal flow. The audit never edits ledgers directly. Delete this comment when applying.
-->
