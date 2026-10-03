# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the remaining advisory-only dependency-vulnerability gate called out by
`SUPPLY-P2-003` (catch-all set `PS-U12`). The developer pre-commit hook previously ran
`pnpm audit --prod --audit-level=high` and, on any failure, printed a warning and continued
("Findings never block"). It now **fails the commit** on any HIGH/CRITICAL advisory that is not
in the shared, time-boxed exception list, with an explicit `HUSKY_AUDIT=off` local override.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U12` — Unassigned SUPPLY findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)
- Branch: `remediation/ps-u12-20261003-0018-develop-a72b8cc`
- Commit: `a202fad83cd2fceb244dc6e815d76da7d8cb9978`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SUPPLY-P2-003` | P2 | open -> partially-fixed | The pre-commit vulnerability check is now blocking (was warning-only). It uses the same time-boxed allowlist as the CI gate and fails closed on new/unlisted HIGH/CRITICAL advisories, on an expired list, and when no list is present. |

Status advances to `verified-fixed` on merge (a draft PR can only be `partially-fixed`).

## Changes

| File | What changed |
|---|---|
| `.husky/pre-commit` | The `pnpm audit` step no longer swallows the result. It captures `pnpm audit --prod --json`, runs the gate, and exits non-zero on an un-allowlisted HIGH/CRITICAL advisory. `HUSKY_AUDIT=off` bypasses locally; CI remains authoritative. |
| `.husky/audit-gate.mjs` | New. Reads the audit JSON and `.pnpm-audit-exceptions.json`; blocks HIGH/CRITICAL advisories not in the list, blocks once the list expires, and fails closed (exit 1) when an advisory is present but no allowlist exists. Exit 2 on usage/parse errors (also fail-closed at the wrapper). |

Scope: the pre-commit hook plus the small gate module it requires. No application code,
dependency, workflow, or config changes.

### Overlap with sibling PATCH-07 (PR #63) — disjoint hunks

`SUPPLY-P2-003`'s evidence spans the CI gates and the local hook. The CI half
(`.github/workflows/validate.yml` pnpm-audit step + Trivy `exit-code`, and the new
`.pnpm-audit-exceptions.json` / `.trivyignore`) is already implemented by **PATCH-07 (#63)**,
which is a separate draft. `PS-U12` therefore touches **only** the developer-side hook and
**consumes the same `.pnpm-audit-exceptions.json`** so there is a single allowlist. The two
diffs do not overlap.

Merge-order note: the hook is enforcing only once `.pnpm-audit-exceptions.json` exists (it fails
closed when absent). Merge **#63 first**, or bring that file over, so the 30 pre-existing
advisories stay allowlisted while new ones block. `HUSKY_AUDIT=off` is available in the interim.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | lab `ci-runner` (172.23.128.51) | 0 | install ok, 883 pkgs — `remediation/PS-U12/verify.log` §0 |
| `corepack pnpm audit --prod --json` | lab `ci-runner` | 1 | advisories total=52, high=28, critical=2 (non-zero is expected) — §1 |
| `node .husky/audit-gate.mjs <real audit> .pnpm-audit-exceptions.json` | lab `ci-runner` | 0 | 0 un-allowlisted HIGH/CRITICAL; all 30 allowlisted — §2 |
| **negative**: injected new HIGH advisory | lab `ci-runner` | 1 | `GHSA-injected-new01` blocked — §3 |
| **negative**: expired exception list | lab `ci-runner` | 1 | expiry enforced — §4 |
| **negative**: missing exception list | lab `ci-runner` | 1 | fails closed — §5 |
| `sh -n` + `shellcheck -S warning` (LF blob) | lab `ci-runner` | 0 | hook parses clean — §6 |
| end-to-end hook audit block (fake `pnpm`; real vs injected) | lab `ci-runner` | 1 / 0 | blocks injected, passes real — §7 |
| `git diff --cached \| gitleaks stdin --redact` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `no leaks found` (3,995 bytes) — §8 |
| full worktree `gitleaks --no-git` | lab `ci-runner` | 1 | 5 **pre-existing** findings, none in the diff — §8 |

- Secret scan (gitleaks): **pass on the diff**. The 5 worktree findings are pre-existing
  (`validate.yml` jwt fixture, `keyboard-shortcuts.tsx` generic-api-key, `infra/docker/.env.dev.example`
  jwt x3), identical to the base set documented under PATCH-07/PS-U03.
- Scope check: **pass** — two `.husky` files only.
- Line endings: the repo stores `.husky/pre-commit` as LF (base blob CR count 0); the local
  worktree is CRLF only because `core.autocrlf=true`. The committed blob is LF and the
  syntax/shellcheck runs use the LF content.

## Evidence bundle

- `remediation/PS-U12/diff.patch` — SHA-256 `D7D12CDFD7A12A8F0E59C9270976EB858121ABFB0219C63B9A93735B05B5A628`
- `remediation/PS-U12/manifest.json`
- `remediation/PS-U12/verify.log`

## Risk and rollback

- Risk: **low**. A pre-commit hook is developer-side only and cannot affect production or CI
  runtime. Its only behavior change is to block commits on un-allowlisted HIGH/CRITICAL
  advisories (previously a warning). `HUSKY_AUDIT=off` provides an explicit override, and CI
  enforces the same policy regardless. The enforcement becomes effective once the shared
  allowlist from #63 is present.
- Rollback: `git revert a202fad83cd2fceb244dc6e815d76da7d8cb9978` (two `.husky` files).

## Review checklist

- [ ] Diff touches only the patch-set files (`+` the small gate module it requires)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Merge order vs PATCH-07 (#63) is acceptable (shared `.pnpm-audit-exceptions.json`)
- [ ] `HUSKY_AUDIT=off` override is acceptable as a local escape hatch
- [ ] Rollback is practical

## Open questions

1. Enforcement depends on the shared `.pnpm-audit-exceptions.json` introduced by PATCH-07 (#63).
   If #63 is not merged, the hook fails closed on the 30 pre-existing advisories; merge #63 first
   or the reviewer should decide otherwise.
2. The finding also recommends enabling Dependabot **security** updates. That is a repository
   setting (not a file), so it is out of scope for this code patch and left as a follow-up; the
   existing `.github/dependabot.yml` covers version updates only.
