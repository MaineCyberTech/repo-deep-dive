# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U08` (unassigned HYG findings). After checking `origin/main`
(`430da82`), the repo-local, unambiguous part of the two open hygiene findings is to make
the repository's single local gate, `ci/validate.py`, enforce the integrity checks that
already exist and already run as separate CI steps but are **not** part of the gate a
developer or the lab runs:

- `automation/validation/check_digest_binding.py` (binds `PACKAGE_DIGEST.txt` to the
  shipped `review-package/` and `evidence/` manifests) -> `HYG-P1-001`.
- `automation/validation/sbom_hashes.sh verify` (hashes + unlisted-artifact check over the
  committed `sbom/` set) -> `HYG-P2-001`.

Both are delegated to (not reimplemented), so the local gate and CI share one
implementation. The residual structural work for each finding (remove the committed
`review-package/` and `sbom/` payloads, or add a fresh-build drift check) is an
owner/release decision and is recorded as an open question, not guessed. `HYG-P1-002` is
already `verified-fixed` at the base commit and is unchanged.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U08` - Unassigned HYG findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u08-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `3a200c9fe33c51c97a9e348fc5f32c846344a72b`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `HYG-P1-001` | P1 | open -> partially-fixed (draft PR) | No drift check bound the committed package into the repo gate. `ci/validate.py` now runs `check_digest_binding.py`, so a stale package or `PACKAGE_DIGEST.txt` fails the gate in addition to the existing CI step. Residual: a fresh-build drift check for the 3,720 package entries and/or removing the committed package needs the release rebind (`HYG-P0-001`/`PATCH-6`) or an owner decision. |
| `HYG-P2-001` | P2 | open -> partially-fixed (draft PR) | The committed SBOM/vulnerability JSON were not checked by the repo gate. `ci/validate.py` now runs `sbom_hashes.sh verify` (hash + unlisted-artifact check), matching the existing CI step. Residual: publishing the payloads as CI/release assets and keeping only hashes/manifests in-repo is an owner/release decision. |
| `HYG-P1-002` | P1 | verified-fixed at base (unchanged) | `automation/validation/secret_scan.py` already normalises `\` -> `/` before the allowlist match (verified at `origin/main`); no code change here. |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and its evidence requirements are met.

### Evidence recorded for `HYG-P1-001` (why the residual is an owner/rebind item)

The committed `review-package/` is already stale against its own `MANIFEST.sha256` at the
base commit: `sha256sum -c` over the package reports 4 mismatches
(`docs/phase8/reviews/INDEPENDENT_REVIEW_2026-09-23*.md`) and 1 missing file
(`mct/config/examples/secrets.example.env`), i.e. 3,715/3,720 OK. A strict
package-content gate therefore cannot be added without a package rebuild + digest rebind,
which is `HYG-P0-001`/`PATCH-6` (and itself needs an owner release decision about keeping
the package committed at all). No fabricated pass: the delegated digest gate checks the
manifest<->digest binding, which is green at this commit, and the residual is called out.

## Changes

| File | What changed |
|---|---|
| `ci/validate.py` | Adds checks 13 `digest-binding` and 14 `sbom-hashes`; both delegate to the existing validation tools (`check_digest_binding.py`, `sbom_hashes.sh verify`) so `ci/validate.py` now covers `HYG-P1-001` and `HYG-P2-001` like CI does. |
| `automation/validation/check_digest_binding.py` | Updates the module docstring: it is no longer "intentionally NOT wired into `ci/validate.py`"; the published tree is bound and the gate runs it (full-history clone required). No behaviour change. |

Scope: two files; no SBOM, package, digest, ledger, workflow or runtime artefact was
modified.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U08/verify.log` (commit `3a200c9`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` - `validation_failures=0`; 30/30 shell suites; `PASS digest binding (PACKAGE_DIGEST binds the shipped manifests)`; `PASS sbom hashes (committed SBOM/vuln set matches SBOM_MANIFEST.sha256)`; shellcheck 172 scripts; secret scan; edge-pin skipped |
| Negative control: mutate `PACKAGE_DIGEST.review_package_manifest_sha256` then `python3 automation/validation/check_digest_binding.py` | lab `ci-runner` | 1 (expected) | `verify.log` - `FAIL digest binding ... declared=deadbeef actual=4167f360...` |
| Negative control: tamper `sbom/vuln/redis_8.8.2.json` then `bash automation/validation/sbom_hashes.sh verify` | lab `ci-runner` | 1 (expected) | `verify.log` - `sha256sum: WARNING: 1 computed checksum did NOT match` / `sbom_hashes: FAIL (hash mismatch/missing/unlisted; SBOM-P2-004)` |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` - `no leaks found` (~4.5 KB scanned) |

Negative controls were run on the lab checkout and restored with `git checkout --` before
the gate run; the committed diff is unaffected.

- Secret scan (gitleaks): **pass** - no leaks on the diff.
- Scope check: **pass** - only the two files above.
- Note: the lab worktree carries pre-existing CRLF-only differences in four
  `docs/phase8/reviews/*.md` files (finding `HYG-P2-002`); they are not in this diff and
  are unrelated to the patch.

## Evidence bundle

- `remediation/PS-U08/diff.patch` - SHA-256 `3001f94749166f5157e40be7a42521ebd7d008f08902b4ef66fea966fecbf11e`
- `remediation/PS-U08/verify.log`
- `remediation/PS-U08/manifest.json`
- `remediation/PS-U08/pr_body.md`

## Risk and rollback

- Risk: **low**. Two new read-only checks are added to `ci/validate.py`; both delegate to
  existing scripts that already pass in CI. The only way the gate changes colour is on real
  digest/SBOM drift. Docstring edit is comment-only.
- Rollback: `git revert 3a200c9fe33c51c97a9e348fc5f32c846344a72b`.

## Review checklist

- [ ] Diff touches only the patch-set files (two hygiene files; no package/SBOM/digest edits)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Wiring `check_digest_binding.py` into `ci/validate.py` is acceptable (CI already runs it)
- [ ] Rollback is practical

## Open questions / deferred

1. **`HYG-P1-001` residual - remove the committed `review-package/` or add a fresh-build
   drift check.** Removing the committed 3,720-file package (build it as a CI artifact
   instead) changes the delivery model and the `PACKAGE_DIGEST.txt`/`PACKAGE_MANIFEST.sha256`
   flow; a fresh-build diff needs a deterministic rebuild. Both are owner/release decisions
   and overlap `HYG-P0-001`/`PATCH-6`. Evidence the package is already stale vs its own
   manifest is recorded above; a rebind is required before a strict content gate can pass.
   Owner action: release/owner.
2. **`HYG-P2-001` residual - publish SBOM/vulnerability JSON as CI/release assets** and keep
   only hashes/manifests in-repo. Requires an artifact pipeline + retention/signing decision
   (`docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` records the unsigned-manifest gap).
   Owner action: supply-chain/release.
