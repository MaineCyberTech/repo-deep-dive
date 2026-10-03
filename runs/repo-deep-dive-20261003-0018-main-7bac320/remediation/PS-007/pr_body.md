# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

- Audit run: `20261003-0018-main-7bac320`
- Patch set: `PS-007` — Deterministic findings integration
- Repo / base: `MaineCyberTech/repo-deep-dive` @ `b3d0382` (main)

Namespaces deterministic finding IDs so they can no longer collide with the
domain reports' areas, wires the deterministic lens into the run findings flow
via a `--run-folder` import path plus a `deterministic-findings.json` merge, and
fixes the lens's line numbers and heading separator.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `API-P2-001` | P2 | open -> fixed | Deterministic IDs now use the distinct `DET` area; the check family is kept as a `[SUBCODE]` title prefix. |
| `API-P2-002` | P2 | open -> fixed | `deterministic_checks.py --run-folder <dir>` writes `lens_deterministic.md` and merges into `findings.json`; `collect_findings.py` also merges `deterministic-findings.json` directly. |
| `DATA-P3-003` | P3 | open -> fixed | Real heading line numbers are emitted; the heading uses the shared ASCII ` - ` separator. |

## Changes

| File | What changed |
|---|---|
| `tools/deterministic_checks.py` | Emit the namespaced `DET` area (check family in the title). `render_markdown` records each finding's real heading line and uses ASCII ` - `. New `--run-folder` import path that writes the lens/JSON into a run and calls `collect_findings.py --write`. Summary table reordered (`ID | Title | Severity`) so the lens is not double-counted by the shared table parser. |
| `tools/collect_findings.py` | New `merge_deterministic()` ingests `deterministic-findings.json` from the run folder, de-duplicating by ID so a markdown lens and the machine JSON can coexist. |
| `PACK_DIGEST.txt` | Regenerated after the tool changes. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash tools/pack_digest.sh` | WSL Ubuntu-24.04 | 0 | `remediation/PS-007/verify.log` |
| `bash tools/lint_pack.sh` | WSL Ubuntu-24.04 | 0 | `remediation/PS-007/verify.log` (RESULT: PASS) |
| `bash tools/self_test.sh` | WSL Ubuntu-24.04 | 0 | `remediation/PS-007/verify.log` (RESULT: PASS) |
| `python3 tools/deterministic_checks.py <fixture> -o <out> --run fixture` | WSL Ubuntu-24.04 | 0 | `remediation/PS-007/verify.log` — 8 findings, `areas: {'DET': 8}`, real line numbers 20/24/28/... ASCII ` - ` |
| `python3 tools/deterministic_checks.py <fixture> --run-folder <run>` + `collect_findings.py` | WSL Ubuntu-24.04 | 0 | `remediation/PS-007/verify.log` — `findings.json` total 9, `byArea {'DET': 8, 'SEC': 1}` |
| `check_run.sh` duplicate gate + `lib_findings.collect_with_dupes` | WSL Ubuntu-24.04 | 0 | `remediation/PS-007/verify.log` — `finding IDs unique (9 unique IDs)`, `dupes []` |

- Secret scan (gitleaks): **NOT RUN** — the `gitleaks` binary is not installed on the verification host (recorded honestly). Supplementary diff-scope regex scan for secret-like patterns: no matches. The repo's CI workflow includes a gitleaks gate.
- Scope check (files within patch set): **pass** — only `tools/deterministic_checks.py`, `tools/collect_findings.py`, and the regenerated `PACK_DIGEST.txt` are changed. The `collect_findings.py` edit is in a region distinct from open PS-002 (#1), which only rewrites the `sourceReports` line.

## Evidence bundle

- `remediation/PS-007/diff.patch` — SHA-256 `44b128184ccd103f4dd6ea6c3756993720d6e9713ef3986aa8b111b59a236666`
- `remediation/PS-007/manifest.json`
- `remediation/PS-007/verify.log`

## Risk and rollback

- Risk: **low** — the deterministic lens is opt-in. The only behaviour change to existing paths is the area rename (`SEC`/`CI`/... -> `DET`) for deterministic output, and a larger `findings.json` when `--run-folder`/machine JSON is used.
- Rollback: `git revert c661a6c`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ regenerated digest)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean (gitleaks not available locally — CI gate applies)
- [ ] Tests added/updated for the fix where applicable (functional fixture run recorded)
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md` / roadmap: namespace deterministic area codes (dupe gate
green), provide an import path so deterministic findings are counted by
`collect_findings.py`, and fix the line number/separator. All three are covered
by the recorded verification.
