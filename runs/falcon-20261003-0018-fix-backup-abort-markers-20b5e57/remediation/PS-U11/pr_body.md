# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U11` (unassigned SEC findings). Checked against `origin/main`
(`430da82`); all three findings were still open at that commit. This PR applies the two
fixes that are unambiguous and repo-local, and records an **open question** for the third
(origin auth for public routers), which is an owner/ops product decision rather than a
guess.

- `SEC-P2-002` (P2, open) - **fixed here**: the Cloudflare API bearer token was passed to
  `curl` as an `-H` argument, so it was visible in `ps` / `/proc/<pid>/cmdline`. It is now
  delivered through `curl --config -` (stdin). A new offline regression test extracts and
  exercises the shipped `api()` against a stub `curl` to prove the token never appears on
  the command line.
- `SEC-P3-001` (P3, open) - **addressed here**: the `forward`/`output` chains are
  `policy accept` and the file let a reader assume the managed table was default-deny for
  those hooks. The chains now state explicitly that forwarding default-deny lives in the
  separate `DOCKER-USER` allowlist (`bootstrap/31-docker-user-firewall.sh`) and point at the
  existing deploy assertion in `automation/validation/post_reboot_verify.sh` (which requires
  the `falcon-lab` `DROP` rule).
- `SEC-P2-001` (P2, open) - **open question, no code change**: adding independent origin
  auth (mTLS / basic / OIDC) to the Cloudflare-fronted public routers, or recording a
  testable owner acceptance, changes the auth UX and has a dependency on the Access policy
  export. Left to the owner; see "Open questions".

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U11` - Unassigned SEC findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u11-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `1127bf6015f6026c7f930032fe969dbebe320b52`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-002` | P2 | open -> partially-fixed (draft PR) | Bearer token moved off `curl` argv onto stdin via `curl --config -`; new `cloudflare_token_argv_test.sh` fails closed if the header returns to argv. |
| `SEC-P3-001` | P3 | open -> partially-fixed (draft PR) | Explicit chain comments: managed table does not enforce forward/egress default-deny; `DOCKER-USER` does, asserted by `post_reboot_verify.sh`. Comment-only change to the nftables file. |
| `SEC-P2-001` | P2 | open (unchanged) | Needs an owner decision (origin auth on public routers vs recorded acceptance). Recorded as an open question; no guessed auth change. |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and its evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `bootstrap/97-cloudflare-api-config.sh` | `api()` now passes the `Authorization` header through `curl --config -` (stdin) instead of an `-H` argv element. 6 added / 6 removed lines. |
| `automation/validation/tests/cloudflare_token_argv_test.sh` | New offline regression guard (79 lines): static checks plus a runtime harness that extracts the shipped `api()` and runs it against a stub `curl`, asserting the token is absent from argv and present on stdin. Runs in the `ci/validate.py` shell-test gate. |
| `config/nftables/falcon.nft` | Clarifying comments on the `forward`/`output` chains (SEC-P3-001); no rule or policy change. |

Scope: two SEC source files plus one test file. No workflow, dependency, schema, ledger,
lockfile, or machine-artifact changes.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U11/verify.log` (commit `1127bf6`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` - `validation_failures=0`; 31/31 shell suites incl. `cloudflare_token_argv_test.sh`; shell syntax 601 scripts; shellcheck 173 scripts; secret scan; edge-pin skipped |
| `bash automation/validation/tests/cloudflare_token_argv_test.sh` | lab `ci-runner` | 0 | `verify.log` - `PASS cloudflare_token_argv (token never on curl argv; delivered via --config -)` |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` - `no leaks found` (~5.87 KB scanned) |

- Secret scan (gitleaks): **pass** - no leaks on the diff.
- Scope check: **pass** - only the three files above.
- Note: the lab worktree shows four pre-existing modified `docs/phase8/reviews/*.md` files
  (finding `HYG-P2-002`, mixed-EOL blobs); they are not in this diff.

## Evidence bundle

- `remediation/PS-U11/diff.patch` - SHA-256 `f65d864d5c969be82016b658d82522cdf741a5ea448b63a58ba1821af9aa92a6`
- `remediation/PS-U11/verify.log`
- `remediation/PS-U11/manifest.json`
- `remediation/PS-U11/pr_body.md`

## Risk and rollback

- Risk: **low**. The token transport change is internal to `bootstrap/97-cloudflare-api-config.sh`
  and only alters how `curl` receives the header (same header value, same requests). The
  nftables change is comments only. The added test is offline and stubbed.
- Rollback: `git revert 1127bf6015f6026c7f930032fe969dbebe320b52`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ the regression test)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason (`SEC-P2-001`)
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] The bearer token cannot be observed in `ps`/argv after this change
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Rollback is practical

## Open questions / deferred

1. **`SEC-P2-001` - origin auth for the public routers (owner decision).** The finding is
   the single edge control: `falcon-grafana`, `falcon-dash`, `iris-public`, `soc-wazuh`,
   `vpn-enroll`, and `ntfy-public` rely on Cloudflare Access at the origin with no
   independent auth (`config/traefik/dynamic.yml`). `ntfy-auth` is defined but referenced by
   no router. Two documented paths exist: (a) add origin auth (mTLS/basic/OIDC) to those
   routers, or (b) record a testable owner acceptance plus an automated Access-posture check
   (`external-smoke` already asserts the 302 to `cloudflareaccess.com`). Both change the
   auth UX / add a second factor (dependency: Access policy export) and are an ops+owner
   decision. Not guessed; left open.
2. **`SEC-P2-002` runtime proof on a multi-user host.** The fix is verified by the argv/stdin
   harness at this commit. A live `ps` capture during a real Cloudflare API call is not
   reproduced here (needs the scoped token and a provisioned run); the offline proof is the
   fail-closed guard in the gate.

## Not run

| Command | Reason |
|---|---|
| Live `ps` capture during a real Cloudflare API call | needs the account-scoped token and a provisioned deploy run; the offline argv/stdin proof is committed instead, not fabricated. |
| Direct-to-origin request without Access returning 401/403 (`SEC-P2-001` validation) | requires a network probe of the live public hosts and the owner's auth decision; not run. |
