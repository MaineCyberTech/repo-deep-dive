# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U06` (unassigned FEAT finding `FEAT-P2-001`, "vendored MCT services are
present in Compose while the subtree policy calls the tree archive-only"). The finding's
recommended fix is either to freeze the vendored tree read-only with a CI guard or to formally
adopt those services into the pin/SBOM scope. The repository actually contains **two distinct
things** that the finding's title conflates:

- `compose/mct/` — **first-party, adopted** consolidated services (DFIR-IRIS, OpenCanary). These
  are already digest-pinned and are already inside the pin/SBOM scope `ci/validate.py` enforces
  for `compose/**` (`pins/images.lock` carries `ghcr.io/dfir-iris/*`, `thinkst/opencanary`,
  `rabbitmq`).
- `mct/compose/` — the **vendored** imported snapshot, which `mct/VENDORING.md` P3 already
  declares archive-only (not a deployment source). Bringing *that* tree into pin scope is the
  owner-pending decision E-2b.

This PR closes the unambiguous, repo-local half of the finding: it states the live-vs-staged
classification in one authoritative place, marks the two `compose/mct/` deployment entrypoints
as first-party/adopted, and adds a cheap static CI guard that (a) asserts the classification is
present and (b) fails if a first-party deployment entrypoint starts referencing the archive-only
`mct/compose/` tree. It deliberately does **not** change the subtree's fate or its pin
enforcement approach; those remain the owner's decision and are recorded as an open question.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U06` — Unassigned FEAT findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u06-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `f19acdbbb7670673446fa86df51f0e3374cd3057`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P2-001` | P2 | open -> partially-fixed (draft PR) | `compose/mct/` is now explicitly classified first-party/adopted (in pin/SBOM scope) and the vendored `mct/compose/` tree explicitly archive-only, in one authoritative table (`docs/runbooks/MCT_CONSOLIDATION.md`), mirrored as a header on both `compose/mct/` deployment entrypoints. A static guard (`remediation_guards_test.sh`) asserts the classification and fails if a first-party compose/bootstrap artifact references `mct/compose/`. The remaining half — pin enforcement approach for the vendored tree and its keep-vs-extract fate — is the owner's decision (`docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-2a/E-2b) and stays open. |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and the finding's evidence requirements are
met.

## Changes

| File | What changed |
|---|---|
| `compose/mct/docker-compose.opencanary.yml` | Header classifies the file as FIRST-PARTY (adopted, in pin/SBOM scope) and points at the live-vs-staged authority; no service, image, port or volume changed. |
| `compose/mct/iris-web/docker-compose.yml` | Same FIRST-PARTY classification header; no service, image, port or volume changed. |
| `docs/runbooks/MCT_CONSOLIDATION.md` | New "Live vs staged classification (FEAT-P2-001)" section: single authoritative table (live first-party vs staged archive-only vs on-VM), the pin/SBOM scope statement, and the pointer to the owner decision E-2a/E-2b. |
| `automation/validation/tests/remediation_guards_test.sh` | Three new static assertions for FEAT-P2-001: `compose/mct` entrypoints carry `FIRST-PARTY`; the classification section exists; no first-party compose/bootstrap artifact deploys from `mct/compose/` (negative control verified locally). |

Scope: two comment-only compose headers, one docs section, and one existing offline test. No
service definition, dependency, lockfile, workflow, schema, ledger or machine artifact changed.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced with
`scripts/lab-sync.ps1 -Repo falcon` and invoked over SSH (the lab job API is also available).
Raw log: `remediation/PS-U06/verify.log` (commit under test `f19acdb`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 30/30 shell suites incl. `remediation_guards_test.sh`; shellcheck over 172 scripts; compose pin + digest cross-check; secret scan; edge-pin skip |
| `bash automation/validation/tests/remediation_guards_test.sh` | lab `ci-runner` | 0 | `verify.log` — `PASS remediation_guards` |
| `git diff origin/main..HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `no leaks found` (~5,023 bytes scanned) |

- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — only the four files above.

## Evidence bundle

- `remediation/PS-U06/diff.patch` — SHA-256 `0213130f472a17689c35f41ab151399646be77c97b3590a25f5576ba8966de58`
- `remediation/PS-U06/verify.log`
- `remediation/PS-U06/manifest.json`
- `remediation/PS-U06/pr_body.md`

## Risk and rollback

- Risk: **low**. The compose changes are comments only; the docs change is additive; the test
  change is a static guard with a verified negative control. No runtime behaviour, service
  definition, image reference, dependency or gate scope changed.
- Rollback: `git revert f19acdbbb7670673446fa86df51f0e3374cd3057`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ test/doc)
- [ ] `compose/mct/` first-party classification matches how the lab actually deploys IRIS/OpenCanary
- [ ] `mct/compose/` archive-only boundary is the intended policy (owner decision E-2b not preempted)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Rollback is practical

## Open questions / deferred

1. **MCT subtree fate (owner decision E-2a).** Keep as archive-only, extract needed pieces, or
   plan deletion — `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-2a is unchecked. This PR does
   not preempt it.
2. **Archive-only / pin enforcement for the vendored tree (owner decision E-2b, owner of
   `ci/validate.py`).** The finding's stronger option — bring `mct/compose/**` into the pin
   check (with an exceptions file) or fail closed on any deployment reference — is a
   coordinator/owner call. This PR adds a narrower first-party guard only; the vendored tree
   itself (29/37 unpinned refs, 11 floating) is untouched.
3. **FEAT-P2-001's title/evidence conflates `compose/mct/` with `mct/compose/`.** Recommend the
   next audit run state the two paths separately so the finding does not read as if the live,
   pinned, first-party IRIS/OpenCanary stack were the problem.
