# Operator Troubleshooting

Fast triage for the common failure modes of a repo-deep-dive run. The pack
never installs or runs target-repo tooling automatically; every fix below is
operator-side.

## Pre-run checklist

1. `python3 --version` works (3.10+). If the Windows Store stub answers instead,
   install Python and ensure the real `python3` is first on `PATH`.
2. `bash --version` works (Git for Windows is enough for the `tools/*.sh` scripts).
3. For readable Unicode on Windows consoles: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.
4. Read the profile (`profiles/falcon-lab.md` for the lab, otherwise the shared
   rules) before starting; record branch/HEAD/dirty state for every in-scope repo.

## `tools/lint_pack.sh` reports "digest stale"

1. Expected after any pack edit — regenerate: `tools/pack_digest.sh`, then re-run lint.
2. On Windows with native Python, an unpatched lint could report every file as
   stale (backslash vs forward-slash paths). That path artifact is fixed in this
   edition; if it recurs, compare one hash manually:
   `sha256sum <file>` vs the `PACK_DIGEST.txt` line.
3. Never hand-edit `PACK_DIGEST.txt`; always regenerate.

## `tools/check_run.sh` FAILs

| Missing | Meaning |
|---|---|
| `INDEX.md`, `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`, `risk_register.md`, `roadmap.md`, `patch_plan.md`, `audit_manifest.json` | Wave 3 synthesis incomplete — run prompts `22`, `23`, `40` |
| `lens_*.md`, `follow_up_register.md` (falcon-lab) | Wave 2 / Wave 4 incomplete |
| `manifest invalid or missing keys` | `audit_manifest.json` must parse and carry `pack`, `profile`, `run`, `scope`, `findings` |
| `finding-ID consistency` | `risk_register.md` and `follow_up_register.md` table IDs must match each other and `findings.total` |

## Findings look wrong

- **Zero findings collected:** reports must use `### Finding ID: AREA-Px-NNN - Title` headings or `| ID | Sev | …` table rows; see `tools/lib_findings.py` and `schemas/findings.schema.json`.
- **Duplicate ID warnings:** first occurrence wins; rename one side and re-run `collect_findings.py --write`.
- **Scanner-style claims without evidence:** send back to the owning prompt; the verification discipline (`00_SHARED_AUDIT_RULES.md`) requires reproduction or `Unknown`.

## Toolchain quirks

- `diff_runs.py` prints ASCII-only (`->`) so it works on Windows consoles; keep new tool output ASCII-only.
- `live_snapshot.sh` is Linux-oriented; on other hosts capture the same fields manually (service state, versions, disk, tunnels, containers) and note the method.
- `risk_score.py` is advisory: a `GO` score never overrides a `NO-GO` gate in `RELEASE_GATE.md`, and vice versa.

## Gate blocked — what next

1. Fix P0 first, then P1 release blockers; add a regression test per fixed finding.
2. Re-run only the owning prompts, then refresh `22`, `23`, `40` (synthesis refresh).
3. Verification mode: mark each finding `verified-fixed` / `partially-fixed` / `still-open` / `regressed` in `verification_log.md` with evidence at the current commit.
4. Re-validate: `check_run.sh`, `collect_findings.py --write`, `risk_score.py`, `diff_runs.py <old> <new>`.

## Remediation execution discipline (operator-side, post-audit)

The audit proposes patch sets (`PS-00N` in `patch_plan.md`); landing them is
operator work under the repo's normal change flow — never part of the audit run.

1. One branch per patch set: `fix/PS-001-short-desc`; the P0 set lands first, alone, with no dependencies.
2. Every set carries verification commands (tests, typechecks, migration checks). Run them before merge; a set with no verification is not done.
3. If verification fails, roll back the set and log the failure with the command output — never force-land a red set.
4. Group P1/P2 sets into weekly milestones; P3 sets ride the normal backlog.
5. After landing, use verification mode above — assertions and intentions never close findings.
