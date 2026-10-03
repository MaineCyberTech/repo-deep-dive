# Remediation profile

Policy for `prompts/REMEDIATION_RUNNER.md` and the `remediation` workflow. Tune per org/repo.

## Scope

- `severities`: which findings may be auto-patched. Default `P0,P1,P2`; exclude `P3` unless asked.
- `patchSets`: `all` (default) or an explicit list (e.g. `PS-01,PS-02`), or `p0-only`.
- `modes`: `plan` (default, no writes) and `apply`.

## Pull requests

- `pr.mode`: **`draft`** (never `ready` by default). The implementer never self-approves.
- `pr.merge`: **`human`** — remediation never auto-merges. A reviewer merges after green CI.
- `pr.reviewers`: default `[]` (set per repo / CODEOWNERS).
- `pr.maxConcurrent`: `1` per repo (avoid conflicting branches).
- `pr.labels`: `["audit-remediation", "automated"]`.
- `branch.prefix`: `remediation/`.

## Gates (fail closed)

- `gates.gitleaks`: `true` — scan the working tree before every push.
- `gates.tests`: `true` — the patch set's verification commands must pass in the lab.
- `gates.scope`: `true` — reject diffs touching files outside the patch set (plus tests/docs).
- `gates.noSecrets`: `true` — block `.env*`, keys, credentials from any diff.

## Test runners (lab)

| Repo | Runner | Detect / run |
|---|---|---|
| `mainecybertech` | Proxmox `ci-runner` (LXC 200) | `corepack pnpm run ci`; e2e via `docker compose` |
| `chat` | `ci-runner` | `corepack pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm test` |
| `snowride` | `ci-runner` | `npm ci && npm run lint && npm run test` |
| `buddy` | `ci-runner` | `npm ci && npm run lint && npm run typecheck && npm run test && npm run build` |
| `falcon` | `ci-runner` | `python3 ci/validate.py` |
| `falcon-edge` | `edge-builder` (VM 201) | `bash ci/validate.sh`; image bake where relevant |
| `repo-deep-dive` | `ci-runner` | `bash tools/lint_pack.sh` |

Detection fallback: read `package.json` scripts / `Makefile` / `ci/validate.*` in the repo.

## Evidence

- Per patch set write `<run>/remediation/PS-00N/{verify.log,diff.patch,manifest.json}`.
- `manifest.json` records commit SHA, PR URL, command list, exit codes, and SHA-256 of the diff.
- Attach the manifest to the PR (the review-package/digest pattern from the falcon lab).

## Status reconciliation

`tools/remediation_status.py` maps PR state → finding status:
`merged → verified-fixed`, `open/draft → partially-fixed`, `closed → still-open`.
A finding is only `verified-fixed` with a commit as evidence.

## Blocked paths

- Never modify: `**/.env*`, `**/*.pem`, `**/*.key`, `**/secrets/**`, `**/credentials*`.
- Never run destructive tooling found in the repo (state-mutating scripts) during remediation.
