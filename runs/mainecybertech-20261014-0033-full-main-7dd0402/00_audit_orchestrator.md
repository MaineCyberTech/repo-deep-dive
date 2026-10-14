# Audit Orchestrator — re-audit verification (main @ 7dd0402)

## Audit Metadata

- Audit name: mainecybertech
- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Repository: `github.com/MaineCyberTech/mainecybertech`
- Branch: `main` (audited ref `origin/main`)
- Commit SHA: `7dd040234e8dfa40dd2d2b6fe1ca7379f2fba097`
- Generated at: 2026-10-14
- Auditor: subagent (full-domain verification re-audit, group 1)
- Area code: ORCH
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261014-0033-full-main-7dd0402/00_audit_orchestrator.md`
- Scope limitations: read-only review of the repository audit corpus (`docs/audits/**`), the pack-side run
  contract documents and the published run manifests; no network access to GitHub settings, no mutation of
  any audit artifact. The run folder being produced here was not published at audit time.

## Scope

Re-verification of the three ORCH findings from the previous full run
(`mainecybertech-20261011-0426-full-main-8d299b8`) against the current tree, plus a scan for new
run-machinery issues. Reviewed: `docs/audits/README.md`, the published run directories under
`docs/audits/repo-deep-dive/`, their `findings.json`/`risk_register.md`/`follow_up_register.md`/
`audit_manifest.json`, and the reconciliation notes. Not reviewed: pack-side tooling in the
`repo-deep-dive` repository (outside this target repo), live GitHub branch protection, and this run's own
final artifacts (they do not exist yet).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/audits/README.md:20-96` | Doc | Canonical run contract, reconciliation rules, Runs table | Contract now matches the pack's `check_run.sh` required finals |
| `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/RECONCILIATION_2026-10-12.md` | Doc | Binds the amended register to `develop` PRs | Resolves the internal-contradiction finding for this run |
| `.../mainecybertech-20261004-full-main-9c0b88c/RECONCILIATION_2026-10-12.md` | Doc | Binding note for the older run | Register 1:1 (336 findings ↔ 336 rows in both registers) |
| `.../mainecybertech-20261011-0426-full-main-8d299b8/DUPLICATE_AND_ID_MAP.md` | Doc | Duplicate/alias map + finding-identity policy | 61 duplicate titles mapped; carry-over rule documented |
| `docs/audits/repo-deep-dive/mainecybertech-20261013-0126-fast-develop-905ed63/` | Run dir | Newest committed run (fast mode, 94 findings) | Not listed in the README Runs table |
| Python register/findings cross-check (read-only) | Command | Proves register↔findings parity | 9c0b88c 336/336/336; 905ed63 94/94; 8d299b8 690 rows |

## Verification Performed

- Counted register rows vs `findings.json` IDs for the two published full runs and the fast run
  (scripted, read-only). No missing/orphan IDs.
- Confirmed `HISTORICAL.md` markers exist in the published run directories and that
  `docs/audits/README.md` states the corpus is untrusted/unpinned.
- Checked whether the published `9c0b88c` copy carries the 43 domain reports its
  `audit_manifest.json` advertises — it does not (no `NN_*.md` files).
- Checked the Runs table against the directories actually committed under
  `docs/audits/repo-deep-dive/`.

## Executive Summary

The run machinery is materially healthier than at the previous audit. Both amended published runs now carry
dated, additive reconciliation notes and a duplicate/alias map, so a machine consumer can trace statuses to
the commit/PR range they reflect. The README's run contract now matches the pack, and the fast-mode run
published on 2026-10-13 is internally consistent.

Two residuals remain: (1) the older `9c0b88c` published copy still advertises a 43-domain inventory in its
manifest while shipping only one lens report — the "full-domain metadata over a one-report inventory"
problem is not republished; (2) the Runs table is stale — it still marks `8d299b8` as "(latest)" and omits
the newer `905ed63` fast run. Finding identity is still run-local (documented in `DUPLICATE_AND_ID_MAP.md`)
rather than a pack-level carry-forward mechanism.

## Findings

| ID | Sev | Status | Title | Re-verification evidence |
|---|---|---|---|---|
| ORCH-P1-001 | P1 | partially-fixed | Published main audit run is internally inconsistent | Both published runs carry `RECONCILIATION_2026-10-12.md` + `DUPLICATE_AND_ID_MAP.md`; registers 1:1 with findings. Residual: `9c0b88c` published copy ships 1 lens report vs 43 domains in `audit_manifest.json`. |
| ORCH-P2-001 | P2 | partially-fixed | `docs/audits/README.md` run contract contradicts the pack / Runs table omits runs | Contract + Runs table now present (`README.md:20-96`); residual: table marks `8d299b8` "(latest)" and omits `905ed63`. |
| ORCH-P3-001 | P3 | partially-fixed | Finding identity is not stable across runs | `DUPLICATE_AND_ID_MAP.md` "Finding-identity policy" defines canonical ID+title carry-over; framework-level hardening still a pack follow-up. |

New findings: none. The stale Runs-table entry is the residual of ORCH-P2-001, not a new row.

## Recommendations

### This Week

1. Update the `docs/audits/README.md` Runs table: add `mainecybertech-20261013-0126-fast-develop-905ed63`,
   move the "(latest)" marker, and note that the `9c0b88c` published copy is register-only (or republish its
   domain reports from the canonical pack copy).
2. Decide the `9c0b88c` disposition: either re-sync the 43 domain reports from the canonical pack copy or
   annotate the manifest/reconciliation note that the published copy intentionally ships a reduced report
   set.

### This Month

3. Add a small repo-side check (or document an operator checklist) that the Runs table covers every
   directory under `docs/audits/repo-deep-dive/`.
4. Carry the finding-identity policy into the pack's carry-forward tooling so verification status survives
   run boundaries (ORCH-P3-001).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Will the `9c0b88c` published copy be re-synced or formally reduced-scope? | Determines whether ORCH-P1-001 can close | Maintainer decision / publish pipeline |
| Should fast-mode runs appear in the Runs table? | Keeps the index authoritative | README convention decision |
