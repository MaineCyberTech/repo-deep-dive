<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the three unassigned repository-hygiene findings in catch-all patch set `PS-U08`
(`HYG-P2-002`, `HYG-P3-003`, `HYG-P3-004`) with minimal, non-functional changes: remove
one-off audit scripts, make the two inline alerting TODOs point at a tracked finding, and
normalise README text encoding / drop a tooling scratch file.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U08` — Unassigned HYG findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (`develop`)
- Branch: `remediation/ps-u08-20261003-0018-develop-a72b8cc`
- Commit: `cc41daee2b2e7d8bc4b27beafafe43ad59708a7b`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `HYG-P2-002` | P2 | open -> partially-fixed | Removed the one-off audit remediation/reporting scripts that mutated transient `tmp_prompt_outputs/` JSON or read `docs/audits/latest_run.json`; none were referenced by any workflow or `package.json` script. The duplicated `requireAdmin` implementations and the duplicate `add_user_groups` migration in the same finding are **not** touched here — they are the same work as `ARCH-P3-005` + `DATA-P2-003` in `PATCH-15` (not yet merged), so consolidating them in this catch-all would conflict. |
| `HYG-P3-003` | P3 | open -> partially-fixed | The two inline `TODO: Configure alerting channels` comments (`metrics.ts`, `server.ts`) now read `TODO(OBS-P1-001): ...`, referencing the tracked audit finding that owns this gap. No behaviour change. |
| `HYG-P3-004` | P3 | open -> partially-fixed | Fixed the em-dash mojibake in `README.md` (1x `—`, 1x `Ã—`) and the arrow mojibake (4x `→`), and deleted `opencode_opacity_replacements.txt` (tooling scratch file). `.env.example` already uses valid UTF-8 em dashes at this commit — the finding's `.env.example` claim is **not reproducible** and no change was made there. |

Statuses map to `partially-fixed` while the PR is a draft; they become `verified-fixed` only
after a human merges with green CI.

## Changes

| File | What changed |
|---|---|
| `scripts/fix_p0.py` | **Deleted** — one-off: stripped P0 findings from `tmp_prompt_outputs/*.json`. |
| `scripts/fix_p0_round2.py` | **Deleted** — one-off repeat of the above. |
| `scripts/fix_p1s.py` | **Deleted** — one-off: removed hard-coded "fixed" P1 patterns from prompt outputs. |
| `scripts/remove_p0.py` | **Deleted** — one-off: removed P0s from two named prompt-output JSONs. |
| `scripts/update_fixed_p1.py` | **Deleted** — one-off: removed ~45 hard-coded "fixed" patterns from prompt outputs. |
| `scripts/remaining_todos.py` | **Deleted** — one-off: printed interim audit backlog notes. |
| `scripts/list_p1.py` | **Deleted** — one-off reporter reading `docs/audits/latest_run.json`; superseded by the documented `scripts/list_current_p1.py`. |
| `scripts/list_p2p3.py` | **Deleted** — one-off reporter; superseded by documented maintenance scripts. |
| `scripts/show_remaining.py` | **Deleted** — one-off reporter; superseded by the documented `scripts/list_remaining_findings.py`. |
| `opencode_opacity_replacements.txt` | **Deleted** — root tooling scratch file (61-line replacement log). |
| `apps/api/src/lib/metrics.ts` | `TODO:` -> `TODO(OBS-P1-001):` (comment only). |
| `apps/api/src/server.ts` | `TODO:` -> `TODO(OBS-P1-001):` (comment only). |
| `README.md` | Normalised mojibake: `—`, `→`, `Ã—` -> proper UTF-8 `—` / `→`. |

Scope: only the artifacts and lines cited by the three HYG findings. Kept the scripts that
`scripts/README.md` documents as maintenance (`list_current_p1.py`, `list_remaining_findings.py`,
`check_imports.py`, `consolidate_audit.py`, `update_scores.py`, `generate_prompt_outputs.py`,
`check_medium_items.py`). No dependency, config, or runtime-code changes.

## Verification Performed

Runner: lab `ci-runner` (172.23.128.51) via `scripts/lab-sync.ps1 -Repo chat` +
`scripts/lab-run.ps1 -Repo chat`. Raw log: `remediation/PS-U08/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter @chat/api test` | lab `ci-runner` | 0 | `verify.log` — **62 test files passed, 485 tests passed** (vitest 3.2.6) |
| `git diff origin/develop \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` — `no leaks found` (~20,162 bytes scanned) |

- Secret scan (gitleaks): **pass** — no leaks in the diff.
- Scope check (files within patch set): **pass** — only the nine one-off scripts, the scratch
  file, the two TODO comment lines, and `README.md`.
- No test/lint command was required for the comment-only and Markdown/script-deletion changes;
  the full API test suite was still run as the broad regression gate.

## Evidence bundle

- `remediation/PS-U08/diff.patch` — SHA-256 `189C4EB9048A250A824BD08DBFED6689800363B597C3F03D1BF1C4A99D2A5CDB`
- `remediation/PS-U08/manifest.json`
- `remediation/PS-U08/verify.log`

## Risk and rollback

- Risk: **very low**.
  - The deleted scripts were one-off audit helpers that operated on transient, local outputs
    (`tmp_prompt_outputs/*.json`, `docs/audits/latest_run.json`); nothing imports or executes them.
  - The `TODO(OBS-P1-001)` change is comment-only.
  - The `README.md` change only corrects display characters.
- Rollback: `git revert cc41daee2b2e7d8bc4b27beafafe43ad59708a7b`.

## Review checklist

- [ ] Diff touches only the patch-set artifacts/lines (+ no unrelated refactors)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Deleted scripts are genuinely unreferenced (grep of workflows/package.json/docs)
- [ ] Rollback is practical

## Definition of done (for this set)

- No workflow or `package.json` script references the deleted one-off scripts.
- Alerting TODOs resolve to a tracked id (`OBS-P1-001`).
- `README.md` contains valid UTF-8 (`—`, `→`) and no mojibake markers.

## Open questions / deferred

1. **Duplicate consolidation (`HYG-P2-002`) is deferred to `PATCH-15`.** The duplicate
   `requireAdmin` (`apps/api/src/middleware/require-admin.ts` vs `apps/api/src/modules/admin/routes.ts`)
   and the duplicate `add_user_groups` migration are `ARCH-P3-005` + `DATA-P2-003`; doing them
   here would duplicate/conflict with that set. A reviewer may prefer to leave `HYG-P2-002`
   `partially-fixed` until `PATCH-15` lands.
2. **`.env.example` encoding claim not reproducible.** At `a72b8cc` the file is valid UTF-8
   (`E2 80 94` em dashes); the finding's `�?"` sequence is not present. No change made.
3. **No automated encoding guard.** A repo-level CI check that fails on mojibake / invalid
   UTF-8 would prevent recurrence and is a sensible follow-up (not added here to keep scope minimal).
4. `HYG-P3-004` is declared to depend on `INV-P3-001` (`PATCH-14`, not merged). The
   README/scratch-file part is independent; `PATCH-14`'s archive/generated-artifact removal is
   untouched, so the branches should not conflict.
