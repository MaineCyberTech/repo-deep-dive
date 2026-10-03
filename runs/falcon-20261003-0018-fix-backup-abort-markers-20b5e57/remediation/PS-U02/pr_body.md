# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U02` (unassigned ARCH findings). After checking `origin/main`, one
sub-issue is repo-local and unambiguous enough to fix minimally: the vendored Wazuh stack's
`flow-relay` helper ran on a **tag-only** `python:3-alpine` reference that was outside the
central pin/SBOM scope (finding `ARCH-P2-002`). It now uses the same digest-pinned
`python:3.12-alpine` image already recorded in `pins/images.lock` and bound by an SBOM, with
an offline regression guard. The remaining three findings — and the residual vendor images
under `ARCH-P2-002` — need an owner/design decision or an out-of-repo dependency, so they are
**deferred with reasons**, not guessed. No finding is claimed fixed without evidence.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U02` — Unassigned ARCH findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u02-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `41cd5a1e65e22f7ef1e957605bb0f0df2755328d`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P2-002` | P2 | open -> partially-fixed (verified at this commit, draft PR) | The vendored `flow-relay` helper is aligned to the locked, SBOM-bound `python:3.12-alpine@sha256:4c47124a…` instead of tag-only `python:3-alpine`. New offline guard `automation/validation/tests/vendored_compose_pin_test.sh` passes **4/4** and is auto-run by `ci/validate.py`. Residual vendor images (`elastiflow/flow-collector`, `wazuh/wazuh-certs-generator`) stay deferred to `SUPPLY-P1-001` / `PATCH-5` (PR #17, open); see below. |
| `ARCH-P1-001` | P1 | open -> still-open (deferred) | Single-host concentration (host loss = total pipeline loss) needs an owner/ops decision on a warm standby and an independent external dead-man with a short window. `docs/CURRENT_STATE.md` §C4 records the external dead-man as an owner/ops item; `docs/architecture/TRUST_BOUNDARIES.md` TB-3 already states the mTLS/VPN production delta. No repo-local change can close it without inventing a recovery SLA. |
| `ARCH-P2-001` | P2 | open -> still-open (deferred, mechanism present) | "Declared container hardening lags the running containers" is a live-deploy observation. The repo already ships the mitigation: `automation/validation/container_drift_check.sh` + `falcon-container-drift.timer`, wired in `bootstrap/90-alerting.sh`, plus the 2026-10-03 full ordered deploy (`docs/CURRENT_STATE.md`). Confirming the live fleet is an ops action, not a static edit. |
| `ARCH-P2-003` | P2 | open -> still-open (deferred) | Central ingest still authenticates with a shared secret header (`config/vector/aggregator.yaml` `auth.strategy: basic`; `config/vector/edge.yaml`). Moving to mTLS or request signing needs the edge PKI (out-of-repo dependency; same dependency as `API-P2-002`, deferred in PS-U01). |

Statuses map to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI.

## Changes

| File | What changed |
|---|---|
| `automation/wazuh/multi-node/docker-compose.override.yml` | `flow-relay` image `python:3-alpine@sha256:a1321512…` -> `python:3.12-alpine@sha256:4c47124a…` (the digest recorded in `pins/images.lock` and bound by `sbom/python_3.12-alpine.cdx.json`), with a short comment tying it to `ARCH-P2-002`. |
| `automation/validation/tests/vendored_compose_pin_test.sh` | New offline guard: asserts the lock records the digest, the helper uses it, no tag-only `python:3-alpine@` remains under `automation/wazuh`, and the SBOM binds the digest. |

Scope: only the vendored Wazuh helper image pin and its offline test. No other image,
service, dependency or runtime config was touched. `flow-relay` was retired with VM 101
(`automation/wazuh/multi-node/docker-compose.lab.yml`), so this is a pin/scope fix with no
live redeploy.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U02/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 31/31 shell suites (incl. the new `vendored_compose_pin_test.sh`, shellcheck over 173 scripts, secret scan, edge-pin skip) |
| `bash automation/validation/tests/vendored_compose_pin_test.sh` | lab `ci-runner` | 0 | `verify.log` — `vendored_compose_pin_test: 4/4 checks passed` |
| `python3 automation/validation/check_compose_digests.py --compose-dir automation/wazuh` | lab `ci-runner` | 1 (expected; residual) | `verify.log` — `compose_digest_findings=2` (elastiflow, certs-generator only; the former python finding is gone) |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `no leaks found` (~3,244 bytes scanned) |

- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — only the two files above.
- Note: the lab job API runs with `HOME` unset, so the gate is invoked with `HOME=/root`
  (recorded); no repository change was made for it.

## Evidence bundle

- `remediation/PS-U02/diff.patch` — SHA-256 `94FA6C632FD170381B69BC25E1F1BC42FEC9B1E1568B1E819342FF53295625AA`
- `remediation/PS-U02/verify.log`
- `remediation/PS-U02/manifest.json`
- `remediation/PS-U02/pr_body.md`

## Risk and rollback

- Risk: **low**. `flow-relay` is not started by the current lab deployment
  (`docker-compose.lab.yml`: "elastiflow/flow-relay are not started (retired with VM 101)").
  Even if started, `config/flow_relay/relay.py` is stdlib-only and runs unchanged on Python
  3.12; the image is already used by the Wazuh alert forwarder.
- Rollback: `git revert 41cd5a1e65e22f7ef1e957605bb0f0df2755328d`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ test/doc)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Alignment to `python:3.12-alpine` is acceptable for `flow-relay`
- [ ] Rollback is practical

## Open questions / deferred

1. **`ARCH-P2-002` residual (vendored images in pin/SBOM scope).** `elastiflow/flow-collector:7.26.2`
   and `wazuh/wazuh-certs-generator:0.0.4` still lack lock/SBOM artifacts. The stated dependency
   is `SUPPLY-P1-001`, implemented by `PATCH-5` (PR #17, open) via `pins/supply-chain-waivers.json`,
   which explicitly assigns the tracking to `ARCH-P2-002`. Recording them in the lock requires
   digest-verified SBOM/vulnerability artifacts, so it should land after `PATCH-5` merges rather
   than be fabricated here. Owner action: supply-chain.
2. **`ARCH-P1-001` (single-host concentration).** Needs an owner/ops decision on a warm standby,
   a restore SLA/RTO, and an independent external dead-man with a short window. Recommend a
   tabletop + restore rehearsal into a fresh host (as the finding states).
3. **`ARCH-P2-001` (declared vs running hardening).** Confirm on the live host that the running
   containers match the declared controls (the drift timer and metric already exist); capture the
   drift-check artifact at the maintenance window. Owner action: container/ops.
4. **`ARCH-P2-003` (ingest mTLS/signing).** Dependency is the edge PKI; same deferral as
   `API-P2-002` in PS-U01. Owner action: owner/ops + edge PKI.
