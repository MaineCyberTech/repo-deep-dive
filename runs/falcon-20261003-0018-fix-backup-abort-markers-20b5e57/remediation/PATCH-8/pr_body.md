# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Tightens the exposed attack surface for the three P1 exposure findings: the OpenCanary
deception stack no longer publishes its decoy ports on all interfaces, the blanket WireGuard
tunnel accept is replaced by explicit per-port allows, and the inbound-mode runtime state is
made authoritative and audited per toggle.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PATCH-8` - Exposure edges (`SEC-P1-001/002/003`)
- Repo / base: `falcon` @ `main` (`430da82`)
- Branch: `remediation/patch-08-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `7bb6187a212c61d626fadd7e681a13929d287306`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-001` | P1 | open -> partially-fixed (open draft PR) | Six decoy ports bound to the management interface (`OPENCANARY_BIND_ADDR`, default `192.168.222.228`) instead of `0.0.0.0` |
| `SEC-P1-002` | P1 | open -> partially-fixed (open draft PR) | Blanket `iifname "wg0" accept` replaced by explicit per-port tunnel allows; exact set to be re-verified against live tunnel listeners before deploy |
| `SEC-P1-003` | P1 | partially-fixed -> partially-fixed (open draft PR) | Runtime state file authoritative; every toggle appended to a runtime ledger; `status` fails closed on unknown/drift; matrix reconciled |

## Changes

| File | What changed |
|---|---|
| `config/nftables/falcon.nft` | Removed the blanket `iifname "wg0" accept`; added explicit wg0 allows (`tcp 9443`, `tcp 15140/15141`, `tcp 514/1514/1515`, `udp 514/2055`) from the documented tunnel trust set. |
| `compose/mct/docker-compose.opencanary.yml` | Decoy ports now bind `${OPENCANARY_BIND_ADDR:-192.168.222.228}:<port>:<port>` instead of all interfaces. |
| `bootstrap/32-inbound-mode.sh` | `record_toggle` writes the authoritative state file and appends every toggle to `/srv/falcon/compose-state/inbound-mode-ledger.md`; `status` reconciles the recorded mode against the live `nft` input policy and exits non-zero on unknown/drift. |
| `docs/architecture/PORT_PROTOCOL_MATRIX.md` | Reconciles the inbound-mode note (closed; runtime state authoritative), the N-22 OpenCanary row (management-interface bind), and the N-24 addendum (narrowing applied). |
| `automation/validation/tests/exposure_edges_test.sh` | New offline regression guards for the three fixes. |

## Verification Performed

All commands ran on WSL `Ubuntu-24.04` in a clean LF `git worktree` at commit
`7bb6187a212c61d626fadd7e681a13929d287306` (the Windows checkout carries CRLF, so a fresh
worktree applies the repository's `eol=lf` attributes).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `nft -c -f config/nftables/falcon.nft` | WSL, clean worktree (`nft` 1.x) | 0 | `remediation/PATCH-8/verify.log` |
| `bash automation/validation/tests/exposure_edges_test.sh` | WSL, clean worktree | 0 (PASS) | `remediation/PATCH-8/verify.log` |
| `bash -n bootstrap/32-inbound-mode.sh` | WSL, clean worktree | 0 | `remediation/PATCH-8/verify.log` |
| `bash -n automation/validation/tests/exposure_edges_test.sh` | WSL, clean worktree | 0 | `remediation/PATCH-8/verify.log` |
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | WSL, clean worktree | 0 (`validation_failures=0`, 31/31 suites) | `remediation/PATCH-8/verify.log` |
| `gitleaks detect --no-git --source . --redact --config .gitleaks.toml` | WSL, gitleaks v8.30.1 (pinned sha256 verified) | 0 (no leaks found) | `remediation/PATCH-8/verify.log` |

Live validation (`ss -ltn` decoy fencing, nft negative tests from a non-allowlisted source,
`32-inbound-mode.sh status` against the live host) was **not run**: the remediation host has
no live falcon host/firewall. These are recorded as `not run` and remain for the lab.

- Secret scan (gitleaks): pass (exit 0, "no leaks found"); `ci/validate.py` secret scan also passes.
- Scope check (files within patch set): pass - the four patch-set files plus one regression
  test under `automation/validation/tests/`.

## Evidence bundle

- `remediation/PATCH-8/diff.patch` - SHA-256 `e83a0652c371b4063b313aef53acb05485f2070247d604ff27453f9931c06c27`
- `remediation/PATCH-8/verify.log`
- `remediation/PATCH-8/manifest.json`

## Risk and rollback

- Risk: medium. The WireGuard narrowing is the security-relevant change; if the port set is
  incomplete a site peer could lose a path after deploy. The change is config-only in this PR
  (not applied to a live host here) and the set is the documented tunnel trust set; verify it
  against the live tunnel listeners before applying. The OpenCanary bind and the state/status
  changes are low risk.
- Rollback: `git revert 7bb6187a212c61d626fadd7e681a13929d287306`; or restore the previous
  `config/nftables/falcon.nft` / `/etc/nftables.conf` via `bootstrap/30-firewall.sh`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

`nft` negative tests from a non-allowlisted source; `ss -ltn` shows the decoys fenced to the
management interface; `32-inbound-mode.sh status` captured to evidence. Config + regression
test are added here; the **live** negative tests and the live tunnel-listener verification
remain for the lab (no live host on the remediation runner).
