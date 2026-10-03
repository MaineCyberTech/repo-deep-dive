# Remediation PATCH-5 — Complete supply-chain + vuln gate

**Findings:** SUPPLY-P1-001, SUPPLY-P1-002
**Repo:** MaineCyberTech/falcon · **Base:** `main` · **Branch:** `remediation/patch-05-20261003-0018-fix-backup-abort-markers-20b5e57` · **Commit:** `5c6c537`

## Summary
- **SUPPLY-P1-001** — the compose digest gate only globbed `compose/**`, so `mct/compose/**` and `automation/wazuh/**` were ungated. `automation/validation/check_compose_digests.py` now scans every declared root (repeatable `--compose-dir`); `ci/validate.py` passes `compose/`, `mct/compose/` and `automation/wazuh/`. A declared root that is missing is a usage error (`exit 2`), so coverage cannot silently shrink.
- **SUPPLY-P1-002** — `sbom_coverage_check.sh` was invoked without `--require-vuln`, so a pinned image without a vulnerability scan passed CI. The gate now runs with `--require-vuln` (workflow + `ci/validate.py`). A missing/malformed/expired waiver file fails closed.
- Known, owner-visible exceptions are recorded in `pins/supply-chain-waivers.json` (root + ref glob, reason, owner, `review_by`) instead of being skipped.

## Verification performed (ci-runner, LF snapshot of the commit)
| Command | Exit | Result |
|---|---|---|
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | 0 | `validation_failures=0`; 30 shell suites pass |
| `bash automation/validation/tests/compose_digest_check_test.sh` | 0 | 25/25 checks passed (multi-root scope + waivers) |
| `bash automation/validation/tests/sbom_coverage_and_hashes_test.sh` | 0 | 25/25 checks passed (vuln gate + hashes) |

Raw output: `remediation/PATCH-5/verify.log`. Diff: `remediation/PATCH-5/diff.patch`.

## Risk / rollback
Low: validation/CI gates only. `git revert 5c6c537`.

## Review checklist
- [ ] Waiver entries in `pins/supply-chain-waivers.json` are acceptable and time-boxed.
- [ ] New compose roots match the deploy topology.
- [ ] `--require-vuln` enforcement is intended to be blocking.

*Draft only — a human reviewer merges. No auto-merge, no self-approval. No secrets committed.*
