# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Rebinds the delivered publication artifacts to one reviewed commit and adds the missing CI
equality test so the digest, the closeout and the shipped manifests cannot drift apart again.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PATCH-6` - Release rebind + CI equality test (`FINAL-P0-001`, `HYG-P0-001`, `HYG-P0-002`)
- Repo / base: `falcon` @ `main` (`430da82`)
- Branch: `remediation/PATCH-6-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commits:
  - `8e4c20ccc49b23f8ffe497c2eaaaea25fc68fccf` - add the publication-equality CI gate + regression test
  - `c8c86d14fd016959125a0dc0835b68a06b1f1a79` - rebind `PACKAGE_DIGEST.txt` and `closeout/FINAL_RESPONSE*.json` to `8e4c20c`

At `main` the digest named `ddb9eb9`, the closeout named `c665ad13`, and neither was the tree
being reviewed; the only binding checker was deliberately left out of CI. Both artifacts now
name the same reviewed commit (`8e4c20c`) and the same review-package manifest hash.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FINAL-P0-001` | P0 | open -> partially-fixed (open draft PR) | Production-readiness claim bound to a single reviewed commit; CI equality gate added |
| `HYG-P0-001` | P0 | open -> partially-fixed (open draft PR) | Digest and closeout now name the same commit and the manifest hash matches the tree |
| `HYG-P0-002` | P0 | addressed (not mapped to PATCH-6 in `remediation_plan.json`) | `verify_publication_chain.sh` reproduced and returns 0; the new gate makes the binding enforceable in CI |

> Note: `remediation_plan.json` maps `PATCH-6` to `FINAL-P0-001` + `HYG-P0-001`; `HYG-P0-002`
> is listed under `unassignedFindings`, so the reconciliation tool only moves the two mapped
> findings. `HYG-P0-002` is nevertheless fixed by this set (verifier reproduced, exit 0).

## Changes

| File | What changed |
|---|---|
| `automation/validation/check_publication_equality.py` | New fail-closed checker: digest repo/src/del must agree, closeout commit must equal them, manifests must match both the shipped files and the tree at the declared commit, the declared commit must be HEAD or an ancestor reached only through publication/test commits. |
| `ci/validate.py` | New `publication-equality` check wired into the standard gate (docstring item 13). |
| `automation/validation/tests/publication_equality_test.sh` | Offline regression: a bound tree passes; a digest/closeout commit mismatch, a mutated manifest hash, and a closeout commit mismatch each fail. |
| `PACKAGE_DIGEST.txt` | `repository_commit`/`CLOSEOUT_SOURCE_COMMIT`/`DELIVERED_PACKAGE_COMMIT` = `8e4c20c`; regenerated timestamp. Manifest hashes unchanged (they match the tree at `8e4c20c`). |
| `closeout/FINAL_RESPONSE.json` | `commit` + `publication_chain` = `8e4c20c`; review-package manifest hash aligned to the shipped manifest. |
| `closeout/FINAL_RESPONSE_SUPERSEDING_2026-09-23.json` | Same commit rebind for consistency. |

`PACKAGE_MANIFEST.sha256` is unchanged: it is a byte-copy of `review-package/MANIFEST.sha256`
(hash `4167f360...`), which this set does not rebuild (rebuilt package content is `HYG-P1-001`,
out of this patch set).

A file cannot name its own commit; the repository's documented `PUBLICATION_RELATIONSHIP`
therefore lets the publication commit (which adds only publication artifacts) sit one commit
after the declared commit. The checker encodes exactly that allowance and rejects any other
drift. `verify_publication_chain.sh` confirms the publishing commit changes only publication
artifacts.

## Verification Performed

All commands ran on WSL `Ubuntu-24.04` in a clean LF git worktree (`/root/falcon-p6`) at
commit `c8c86d14fd016959125a0dc0835b68a06b1f1a79` (the Windows checkout carries CRLF line
endings that break `bash -n`/the bash suites).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 automation/validation/check_publication_equality.py --root .` | WSL, clean worktree | 0 (PASS) | `remediation/PATCH-6/verify.log` |
| `bash automation/validation/tests/publication_equality_test.sh` | WSL, clean worktree | 0 (PASS) | `remediation/PATCH-6/verify.log` |
| `bash automation/validation/tests/digest_binding_check_test.sh` | WSL, clean worktree | 0 (PASS) | `remediation/PATCH-6/verify.log` |
| `bash automation/validation/tests/digest_verdict_consistency_test.sh` | WSL, clean worktree | 0 (PASS) | `remediation/PATCH-6/verify.log` |
| `FALCON_SIGNED_GUARD_OPTIONAL=1 bash automation/validation/verify_publication_chain.sh` | WSL, clean worktree | 0 (`publication_chain_failures=0`) | `remediation/PATCH-6/verify.log` |
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | WSL, clean worktree | 0 (`validation_failures=0`; new gate PASS) | `remediation/PATCH-6/verify.log` |
| `gitleaks detect --no-git --source . --redact --config .gitleaks.toml` | WSL, gitleaks v8.30.1 (pinned sha256 verified) | 0 (no leaks found) | `remediation/PATCH-6/verify.log` |

The signed delivery archives are not present on this remediation host, so those checks report
`SKIP` under `FALCON_SIGNED_GUARD_OPTIONAL=1`; in CI they are skipped via `GITHUB_ACTIONS=true`
as designed.

- Secret scan (gitleaks): pass (exit 0, "no leaks found"); `ci/validate.py` secret scan also passes.
- Scope check (files within patch set): pass - `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`
  (unchanged), `closeout/FINAL_RESPONSE*.json`, `ci/validate.py`, plus the new checker/test under
  `automation/validation/`.

## Evidence bundle

- `remediation/PATCH-6/diff.patch` - SHA-256 `75e45b7cf9721867415b21f053be2cb40e49409a553d9deb85a56b777e439566`
- `remediation/PATCH-6/verify.log`
- `remediation/PATCH-6/manifest.json`

## Risk and rollback

- Risk: low-medium. It changes machine-readable delivery metadata only (digest/closeout) and
  adds a CI gate; no runtime behavior. The CI gate is fail-closed, so a later non-publication
  commit will fail it until the digest is rebound - that is the intended drift control.
- Rollback: `git revert c8c86d14fd016959125a0dc0835b68a06b1f1a79 8e4c20ccc49b23f8ffe497c2eaaaea25fc68fccf`
  (reverts the rebind and removes the gate/test).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

`bash automation/validation/verify_publication_chain.sh` returns 0 in a full clone (verified),
the new CI test passes and fails on a mutated digest (verified offline), and
`repository_commit == CLOSEOUT_SOURCE_COMMIT == DELIVERED_PACKAGE_COMMIT` across the digest and
the closeout (verified). The declared commit is the pre-publication tree, per the documented
`PUBLICATION_RELATIONSHIP`.
