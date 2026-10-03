# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U05` (unassigned EXEC finding `EXEC-P1-001`, "lab GO can be misread as a
production approval"). The finding's recommended fix is to keep the reconciliation statement
prominent in the gate and keep lab/production language separated in every machine artifact. The
repo already separates the two in the machine artifacts (`PACKAGE_DIGEST.txt` carries distinct
`lab_implementation` and `production_readiness` keys; `closeout/FINAL_RESPONSE.json` carries
`environment_class=LAB` and `production_readiness`), but there was no **canonical repo-level gate
page** tying the program verdict and the audit opinion together — `docs/CURRENT_STATE.md` pointed
readers at a bare `RELEASE_GATE.md` that did not exist at the repo root.

This PR adds that page, `docs/RELEASE_GATE.md`, and links it from the README doc map. The page
states the non-negotiable rule (a lab pass is not a production pass), the conditional gate
(NO-GO for any production-readiness claim; GO WITH CONDITIONS for continued lab operation), the
reconciliation between the program's APPROVED verdict (2026-09-29) and the audit opinion, and the
run's blocking/lab conditions mapped to finding IDs. It is documentation only and deliberately
asserts no new readiness: it points at the authoritative ledgers and `docs/CURRENT_STATE.md`.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U05` — Unassigned EXEC findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u05-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `4529dbdb966a639a79d46d85c3d32de9ae865925`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `EXEC-P1-001` | P1 | open -> partially-fixed (draft PR) | A canonical `docs/RELEASE_GATE.md` now makes the conditional gate and the lab/production separation prominent and in-repo, and is linked from `README.md`. The page transcribes the audit run's own gate verdict and conditions; it claims no fix of the underlying P0/P1 and no change to the program verdict. The finding's other half — the reviewer-produced C1 disposition and the verdict rebind (`docs/phase9/OWNER_ACTIONS.md` A1/A3) — is owner/reviewer work and remains open (see below). |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and the finding's evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `docs/RELEASE_GATE.md` | **New.** Canonical reconciliation page: the "a lab pass is not a production pass" rule; the machine-artifact split (lab vs production keys); the program-verdict vs audit-opinion reconciliation; the run's verdict and conditions C0–C6 with finding IDs; and a pointer to the authoritative ledgers / `docs/CURRENT_STATE.md`. |
| `README.md` | One row added to the "Where to start reading" doc map linking `docs/RELEASE_GATE.md`. |

Scope: one new doc plus a one-line README link. No code, workflow, dependency, schema, ledger or
machine artifact was changed.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against the branch synced with
`scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U05/verify.log` (commit under test `4529dbd`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 30/30 shell suites incl. `readme_ledger_drift_test.sh` (which resolves the new README link), shellcheck over 172 scripts, secret scan, edge-pin skip |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` — `no leaks found` (~6,219 bytes scanned) |
| `test -f docs/RELEASE_GATE.md && grep -q ... && grep -q "docs/RELEASE_GATE.md" README.md` | lab `ci-runner` | 0 | `verify.log` — `DOCS_CHECK_OK` (new page exists, carries the lab/production rule, the conditional verdict, and the `EXEC-P1-001` reference; README links it) |

- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — one new docs file plus a one-line README addition.
- Note: `lab-sync.ps1` extracts the Windows working tree; the extracted clone has
  `core.fileMode=false`, so the 592 tracked mode-100755 files were `chmod +x`'d before the gate.
  Without that step the offline suites that execute tracked scripts exit 126; the same gate passes
  once the exec bits are restored. Four `docs/phase8/reviews/*.md` files remain reported as
  modified from the repository's pre-existing mixed-EOL blobs (HYG-P2-002); they are unrelated to
  this patch and not part of the diff.

## Evidence bundle

- `remediation/PS-U05/diff.patch` — SHA-256 `AF14BA33AA88929A792999E29BBC632BB5B6CAE838F866D9C5D63B1D5CF534EA`
- `remediation/PS-U05/verify.log`
- `remediation/PS-U05/manifest.json`
- `remediation/PS-U05/pr_body.md`

## Risk and rollback

- Risk: **low**. Documentation only. The page is an advisory reconciliation that explicitly does
  not override the program verdict and does not change the ledgers, machine artifacts or CI. It
  cannot change runtime behaviour.
- Rollback: `git revert 4529dbdb966a639a79d46d85c3d32de9ae865925`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] The gate page does not overstate readiness or override the program verdict
- [ ] Rollback is practical

## Open questions / deferred

1. **`EXEC-P1-001` reviewer/owner half.** The finding is also tracked in
   `docs/phase9/OWNER_ACTIONS.md` (A1: the C1 reviewer-produced disposition; A3: the verdict
   rebind + release authorization) and is bound to the release-integrity condition C0
   (`FINAL-P0-001` / `HYG-P0-001` / `HYG-P0-002`). Those require a named reviewer's artifact and the
   owner's adoption; a repo-local docs PR cannot produce them. This PR closes the documentation
   half and leaves the reviewer/owner half open.
2. **Present-state authority.** The conditions in `docs/RELEASE_GATE.md` are recorded at the
   audited commit `20b5e57`. Later commits and remediation waves may have advanced them; the page
   defers to `docs/CURRENT_STATE.md` and the ledgers, which stay the source of truth.
