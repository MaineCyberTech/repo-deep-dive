# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the one repo-local, unambiguous finding in catch-all patch set `PS-U01` — the
enrollment API tokens with no expiry — with a minimal, backward-compatible change, and
records the two remaining API findings as deferred with their audit-stated dependencies
(the edge session / edge PKI). No finding is claimed fixed without evidence.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U01` — Unassigned API findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u01-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `c04c0068c182b7d61521978f154f5ac33ae42c2a`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `API-P2-001` | P2 | open -> partially-fixed (verified at this commit, draft PR) | Per-device enrollment tokens now carry a Unix expiry timestamp and the service rejects an expired (or malformed-expiry) token with `403`; a legacy binding without the third field stays valid. `issue-enroll-token.sh` writes `<name>:<token>:<expiry-epoch>` with `FALCON_ENROLL_TOKEN_TTL_SECONDS` (default 86400 s); the offline enrollment suite gained 4 checks (expired / malformed / future / legacy), **18/18 pass**. |
| `API-P1-001` | P1 | open -> still-open (deferred) | The finding's recommended fix is to vendor a **signed** edge digest manifest into this repo or fetch it from a pinned artifact URL. The edge delivery artifacts live in the private `falcon-edge` repo; neither the signed manifest nor a release URL is available repo-locally, and `automation/validation/verify_edge_pin.py` already runs in `ci/validate.py` (fails closed on a malformed pin, skips when the delivery is absent). Closing it here would require fabricating signature/digest evidence. Deferred to the edge session per the finding's own `Dependencies: edge session`. |
| `API-P2-002` | P2 | open -> still-open (deferred) | The finding asks for mTLS per sensor or HMAC request signing plus an idempotency key; its stated dependency is `edge PKI` and effort `M`. Vector's HTTP ingest does not sign requests and a content-only dedupe would drop legitimate repeats without addressing spoofing, so the honest repo-local delta is a contract-threat-model note, not a fix. Deferred to the edge PKI / ingest-signing work. |

Statuses map to `partially-fixed` while the PR is a draft; they become `verified-fixed` only
after a human merges with green CI.

## Changes

| File | What changed |
|---|---|
| `automation/vpn/enroll-service.py` | `load_tokens()` parses an optional per-device expiry (`<name>:<token>:<expiry-epoch>`; malformed -> already expired, fail closed); `authorize()` returns `(label, expired)`; `do_POST` logs and returns `403 "expired token"` for an expired binding. |
| `automation/vpn/issue-enroll-token.sh` | Writes the expiry epoch into the binding (`FALCON_ENROLL_TOKEN_TTL_SECONDS`, default 86400 s; non-numeric TTL fails usage); log line reports the expiry. |
| `automation/vpn/test_enroll_service.sh` | Token file fixtures for future/expired/malformed/legacy bindings, 4 new assertions, rate ceiling raised to keep the existing burst assertion meaningful. |
| `docs/security/ENROLL_API.md` | Documents the expiry field, the `403` expired response and the new residual (shared token still non-expiring). |

Scope: only the enrollment token model and its offline test/doc. No other API contract,
dependency or runtime config was touched.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U01/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 30/30 shell suites (incl. shellcheck over 172 scripts, secret scan, edge-pin skip) |
| `bash automation/vpn/test_enroll_service.sh` | lab `ci-runner` | 0 | `verify.log` — `enroll_test_pass=18 fail=0` (expired/malformed refused; future/legacy enroll) |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `no leaks found` (~13,002 bytes scanned) |

- Note: the lab job API runs with `HOME` unset, so the first `ci/validate.py` invocation failed
  only inside the unrelated offline `audit_run_lifecycle_test.sh` fixture (`HOME: unbound
  variable`). The same gate with a normal `HOME=/root` passes (recorded above). No repository
  change was made for this.
- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — only the four patch-set files above.

## Evidence bundle

- `remediation/PS-U01/diff.patch` — SHA-256 `C1B1A1961777E05BF4AE9C809D4C6539D8774F2C766F4910039BEB740733AB55`
- `remediation/PS-U01/verify.log`
- `remediation/PS-U01/manifest.json`
- `remediation/PS-U01/pr_body.md`

## Risk and rollback

- Risk: **low**. The token file gains an optional third field; the parser stays compatible with
  existing `<name>:<token>` and bare shared lines, and malformed expiry fails closed. The
  default 24 h lifetime only needs to cover delivery because endpoints enroll immediately after
  issuance. No live service is redeployed by this PR; deployment remains owner-run.
- Operational note: on deploy, restart `falcon-vpn-enroll.service` so the new parser is loaded;
  previously issued per-device bindings remain valid.
- Rollback: `git revert c04c0068c182b7d61521978f154f5ac33ae42c2a`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ test/doc)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Token-file format change is backward compatible (legacy bindings still valid)
- [ ] Rollback is practical

## Open questions / deferred

1. **API-P1-001 (cross-repo pairing).** Needs either the signed edge digest manifest vendored
   into this repo or a pinned artifact URL for CI. Owner action: edge session. Until then the
   verifier correctly reports "edge pin artifacts not present; skipped".
2. **API-P2-002 (ingest signing/idempotency).** Needs edge PKI (mTLS or HMAC request signing)
   and a dedupe at ingest. Recommend a follow-up design note + an idempotency key in the edge
   HTTP sink once the PKI work lands.
3. **Shared enrollment token has no expiry.** Only per-device bindings expire. Rotate/replace
   the bootstrap-generated shared token after onboarding pauses (`docs/security/ENROLLMENT_CLOSURE.md`,
   owner decision).
