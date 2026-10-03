# Repo Wiring — repo-deep-dive for the falcon lab

How this pack works with `/home/user/falcon-build` (central) and `/home/user/falcon-edge-build` (edge), and how to vendor it.

## 1. Layout options

### Option A — Central pack (default)

The pack lives at `/home/user/repo-deep-dive/`. Runs are written into the repos:

- **Canonical run folder:** `<falcon>/docs/audits/repo-deep-dive/{run}/` — all reports, lens reports, finals, `audit_manifest.json`.
- **Edge mirror:** `<edge>/docs/audits/repo-deep-dive/{run}/` — the edge-scoped reports and finals plus a pointer to the canonical folder.
- **Pack archive:** copy the completed run into `<pack>/runs/{run}/` for portability (the pack stays self-contained).

### Option B — Vendored pack

Copy this tree into `<falcon>/docs/audits/repo-deep-dive/` (single source of truth for the lab). The edge repo receives run mirrors only. Record `PACK_DIGEST.txt` in the run manifest when vendoring or when running a released pack.

Do **not** vendor or copy into a repo while another session has uncommitted changes in it (see §6).

## 2. Run conventions

- **Naming:** `YYYYMMDD-HHMM-falcon-<sha7>_edge-<sha7>`; fallback `YYYYMMDD-HHMM-manual`.
- **Runner:** `prompts/MASTER_RUNNER_FALCON_LAB.md`. **Boundaries:** `profiles/falcon-lab.md` §3 (audit-only, read-only live host, no secrets, append-only records, independence, parallel sessions).
- **Validate before calling a run complete:** `tools/check_run.sh <run-folder>` must print `PASS` (required finals present, manifest valid, falcon-lab extras present, finding IDs consistent between `risk_register.md` and `follow_up_register.md`).
- **After remediation:** run the verification mode (falcon runner) and use the shared status vocabulary (`verified-fixed`, `partially-fixed`, `still-open`, `regressed`); only artifact-backed verification closes a finding.
- **Run tooling:** `tools/collect_findings.py <run>` normalizes findings (`--write`, `--update-manifest`); `tools/diff_runs.py <old> <new>` produces the delta report; `tools/findings_to_csv.py <run>` exports for trackers; `tools/live_snapshot.sh` captures read-only host state; `tools/self_test.sh` exercises the whole toolchain end-to-end.

## 3. Decision-log integration (operator-applied)

The audit never edits ledgers. Wave 4 *proposes* an entry; the operator applies it through the normal flow. Suggested entry shape:

```markdown
## YYYY-MM-DD — repo-deep-dive audit run <run>
- Scope: <repos> @ <shas>; lenses: ND/REV/INTG/LIVE; findings: P0 x / P1 x / P2 x / P3 x
- Run folder(s): <canonical + mirror paths>
- Gate opinion: GO WITH CONDITIONS (conditions: ...)
- Reconciliation: <delta vs existing verdicts, if any — never revoke/grant>
- Follow-up: <follow_up_register path>; verification pass planned: <date>
```

## 4. Register integration

Findings feed the repos' risk registers through the normal flow: the operator adds/updates rows referencing `AREA-Px-NNN` and the run folder. The run's `risk_register.md` is the audit's aggregated view — it does not replace the repo register, and `follow_up_register.md` is the remediation tracker (post-audit notes do not close findings; only a verification pass does).

## 5. CI drift checks (recommended; implement in the repos' `ci/`)

The recurring failure classes found by the 2026-09-30 audits map to cheap, read-only checks:

| # | Check | Failure class it prevents |
|---|---|---|
| 1 | Status artifacts (digest, `AGENTS.md`, `README.md`, `FINAL_RESPONSE.json`) derive their state from the ledgers — never hardcoded | ND-P1-001/002, REV-P1-001/006 |
| 2 | Pin ↔ delivery: the pinned digest must resolve to a present artifact; manifest filenames are versioned | INTG-P0-001 |
| 3 | Current-state block in docs matches ledgers (generated) | ND-P1-002 |
| 4 | Run completeness: `tools/check_run.sh` on any committed run folder | Broken/incomplete audit records |
| 5 | Run manifest records `packVersion` / `profileVersion` (+ pack digest when vendored) | Untraceable audits |
| 6 | WG peer preservation regression (`automation/validation/wg_peer_preservation_check.sh` in falcon) | INTG-P0-002 |
| 7 | Evidence-index paths are package-relative and resolvable in the package | ND-P2-011 |
| 8 | Alert catalogue matches live rules | LIVE-P1-004, INTG-P2-004 |

Implement per repo doctrine (checks are read-only; record results as evidence).

## 6. Parallel-session coordination

- Record both repos' branch/HEAD/dirty state at run start **and** before writing reports; note movement in `audit_manifest.json`.
- If a tree moves mid-run, do not chase it — record it (see the archived run's edge note: `cfaf09d` → `ced99b3` → `2b5bc8b`).
- Repo wiring (copying runs in, vendoring the pack, decision-log entries) happens only on a settled tree.

## 7. Archiving and versioning

- Completed runs are archived under `runs/` in addition to the repo copies; `runs/` is excluded from nothing — it is part of the pack.
- After any pack change: update `CHANGELOG.md`, regenerate `PACK_DIGEST.txt` (`tools/pack_digest.sh`), and record the version/digest where the pack is used.
- The archived run's `audit_manifest.json` records `packVersion` and `profileVersion` of the edition that produced it.

## 8. First-run checklist (falcon lab)

1. `tools/check_run.sh` the latest run — `PASS`.
2. Confirm the decision-log entry is applied (or scheduled) and the follow-up register is handed to the owners.
3. Schedule the verification-only pass for fixed findings; then the first full domain run.
4. When the tree settles: copy the run to the canonical + mirror folders and (optionally) vendor this pack.
