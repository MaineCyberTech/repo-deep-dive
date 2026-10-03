# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U09` (unassigned INV findings) for the audit run
`20261003-0018-fix-backup-abort-markers-20b5e57`. After checking `origin/main`
(`430da82`), the two open inventory findings are addressed with the smallest
repo-local, verifiable changes; the structural residuals are recorded as owner
decisions rather than guessed.

- `INV-P2-001` — most committed bytes are generated/derived and nothing bound the
  committed copies to a manifest. Added `automation/validation/check_generated_drift.py`,
  a deterministic read-only check that recomputes `evidence/MANIFEST.sha256` over the
  committed capture tree and fails on drift/missing files, wired into `ci/validate.py`
  as check `generated-drift`. `REPOSITORY.md` now classifies each top-level tree as
  source vs generated with its regenerator and binding (the audit's documented quick win).
- `INV-P3-001` — host-absolute / legacy evidence paths needed manual prefix rewriting in
  a clone. Added `automation/validation/resolve_evidence_path.py` (maps a recorded path
  to `evidence/raw/...` or `review-package/evidence/...` and verifies it exists), and
  `check_evidence_index.py` now reports the count of host-absolute metas it resolves.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U09` — Unassigned INV findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u09-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `e31523a59c945126e1b3e1e6ea9e630559292812`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `INV-P2-001` | P2 | open -> partially-fixed (draft PR) | No check bound committed generated content to its manifest. `ci/validate.py` now runs the `generated-drift` check over the 2,268-entry `evidence/MANIFEST.sha256`; a tampered or stale capture fails the gate (negative control below). `REPOSITORY.md` classifies source vs generated trees. Residual: the committed `review-package/` content-drift gate needs the package rebuild + digest rebind (`HYG-P0-001`/`PATCH-6`) — an owner/release decision, because the committed `review-package/MANIFEST.sha256` is already stale against HEAD (4 mismatches, 1 absent entry). |
| `INV-P3-001` | P3 | open -> partially-fixed (draft PR) | A resolver turns the manual prefix rewrite into one command and can verify presence in a clone. Residual (not guessed): the metadata and the 264 legacy `evidence_index.csv` rows still record host/absolute paths; evidence is append-only and is not rewritten in place, so the resolver is the portability path. |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and its evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `automation/validation/check_generated_drift.py` (new) | Deterministic, read-only drift check over declared generated-tree manifests (default `evidence/MANIFEST.sha256`); recomputes SHA-256 per entry and fails on drift, missing file, or unparseable manifest. |
| `automation/validation/tests/generated_drift_check_test.sh` (new) | Fixture suite: consistent tree passes; tampered/missing file fails; malformed manifest fails closed. |
| `ci/validate.py` | Adds check 13 `generated-drift` (delegates to the script above). |
| `automation/validation/resolve_evidence_path.py` (new) | Resolves a recorded `falcon-build` / `monitoring-build` / `../monitoring-build` / already-relative path to `evidence/raw/...` (or `--package` review-package copy) and verifies presence with `--root`. |
| `automation/validation/tests/resolve_evidence_path_test.sh` (new) | Fixture suite for all path forms, `--package`, `--root` presence, and fail-closed junk. |
| `automation/validation/check_evidence_index.py` | Reports the count of host-absolute `raw_artifact` metas it normalises and resolves (informational). |
| `REPOSITORY.md` | New "Source vs generated trees" section (class, regenerator, binding) and the resolver usage note in Evidence rules. |

Scope: 7 files (3 modified, 4 new + 2 test suites). No evidence, ledger, package,
digest, workflow or runtime artifact was modified; no generated file was edited in place.

## Verification Performed

All commands ran on the lab `ci-runner` (`ci-runner`) against an LF worktree synced at the
branch commit with `scripts/lab-sync.ps1 -Repo falcon`. Raw log:
`remediation/PS-U09/verify.log` (commit `e31523a`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; `PASS generated drift (committed evidence tree matches MANIFEST.sha256)`; 32/32 shell suites incl. both new fixture suites; shellcheck 174 scripts; secret scan; edge-pin skipped |
| `python3 automation/validation/check_generated_drift.py --root .` | lab `ci-runner` | 0 | `PASS generated_drift (2268 entries match their committed manifests)` |
| `python3 automation/validation/resolve_evidence_path.py /home/user/falcon-build/evidence/raw/... --root .` | lab `ci-runner` | 0 | resolves to `evidence/raw/ARCH-P2-001/...out` |
| `python3 automation/validation/resolve_evidence_path.py ../monitoring-build/evidence/raw/... --root .` | lab `ci-runner` | 0 | resolves to `evidence/raw/P0-G02/...out` |
| Negative control: append to a committed evidence capture, then `check_generated_drift.py --root .` | lab `ci-runner` | 1 (expected) | `FAIL generated_drift ... drift evidence/raw/ARCH-P2-001/... (declared=bcde762b3ede actual=d4a26f46c0c4)`; restored and re-checked PASS |
| Negative control: `resolve_evidence_path.py /etc/passwd` | lab `ci-runner` | 1 (expected) | `UNRESOLVED: /etc/passwd (no 'evidence/raw/' component)` |
| `git diff origin/main..HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `no leaks found` (24,353 bytes scanned) |

- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — only the 7 files above.
- Note: the lab worktree carried 4 pre-existing CRLF-only differences in
  `docs/phase8/reviews/INDEPENDENT_REVIEW_2026-09-23*.md` (finding `HYG-P2-002`, tracked
  separately); they are not in this diff. Tracked `*.sh` files were `chmod +x` before the
  gate because the lab-sync extraction has `core.fileMode=false` (recorded in `verify.log`).

## Evidence bundle

- `remediation/PS-U09/diff.patch` — SHA-256 `7c68909638d69dc6b7caa7abee2005d3823f92565825eab5509e2926f33f45d8`
- `remediation/PS-U09/verify.log`
- `remediation/PS-U09/manifest.json`
- `remediation/PS-U09/pr_body.md`

## Risk and rollback

- Risk: **low**. Three modified lines are informational; the gate adds one read-only
  check that delegates to a script with a self-test, and the resolver is a new opt-in tool.
  The only way `ci/validate.py` changes colour is on real `evidence/` drift.
- Rollback: `git revert e31523a59c945126e1b3e1e6ea9e630559292812`.

## Review checklist

- [ ] Diff touches only the patch-set files (no evidence/package/digest edits)
- [ ] Both findings are addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Scoping the `generated-drift` gate to `evidence/` (not the stale `review-package/`) is acceptable
- [ ] Rollback is practical

## Open questions / deferred

1. **`INV-P2-001` residual — refresh/rebind `review-package/` (or stop committing it).**
   The committed `review-package/MANIFEST.sha256` is stale against a clean checkout
   (4 mismatches in `docs/phase8/reviews/INDEPENDENT_REVIEW_2026-09-23*.md`, and
   `mct/config/examples/secrets.example.env` listed but absent), so a strict package
   content-drift gate cannot be green until the package is rebuilt and the digest rebound:
   `HYG-P0-001`/`HYG-P1-001`/`PATCH-6`. Owner action: release/owner.
2. **`INV-P3-001` residual — rewrite metadata to repo-relative paths?** Evidence is
   append-only and 1,127 metas record the capture-host path, so this patch adds a resolver
   rather than editing evidence in place. If the owner wants the recorded paths changed,
   that is a separate, append-only correction decision. Owner action: release/owner.
