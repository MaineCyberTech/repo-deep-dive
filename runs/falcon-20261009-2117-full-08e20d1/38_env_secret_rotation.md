# 38_env_secret_rotation — Prompt 38 - Environment and Secret Rotation Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `38_env_secret_rotation.md` (area SECRET, prompt)

## Verification Performed

# Environment and Secret Rotation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon @ 08e20d1 (branch main), live lab host `falcon`
- Generated at: 2026-10-09T21:44:07Z
- Auditor: subagent (repo-deep-dive full, area SECRET)
- Area code: SECRET
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/38_env_secret_rotation.md
- Scope limitations: read-only. No secret values were printed; only names, paths, modes, mtimes and counts are recorded. Rotation execution is owner-gated and was not performed.

## Scope

Reviewed: .env.example, docs/security/* (inventory, rotation register/procedure, break-glass, CI secret gate, scanner allowlists), the runtime validators (check_owner_env.py, rotation_status.py, check_rotation_register.py, secret_scan.py), the CI gitleaks gates and pins, the compose/secret-consumption paths (env_file + /srv/falcon/secrets), the inherited Wazuh/MCT credential stores (metadata only), and the live permissions of /srv/falcon/secrets and /home/user/.env.

Not reviewed: third-party consoles (DO, Cloudflare, UniFi, MISP, Shuffle UI) and any value material.

Companion artifacts (in-repo, satisfying the prompt's required outputs):
- Rotation runbook: docs/security/INHERITED_CREDENTIAL_ROTATION.md + docs/security/CREDENTIAL_ROTATION_REGISTER.md + mct/runbooks/credential-rotation-checklist.md
- Env inventory: docs/security/OWNER_ENV_INVENTORY.md + .env.example + docs/architecture/IDENTITY_AND_SECRETS.md
- Secret classification: docs/architecture/IDENTITY_AND_SECRETS.md sections 2-3
- Emergency revocation: INHERITED_CREDENTIAL_ROTATION.md (per-item negative tests) + docs/security/BREAK_GLASS_CUSTODY.md

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| .env.example | env example | documented owner key set (7) | names only, no values |
| /home/user/.env | live env | actual owner key set | 9 keys, mode 0600; names only |
| docs/security/OWNER_ENV_INVENTORY.md | docs | inventory + validator contract | claims 7 keys/PASS (stale) |
| automation/validation/check_owner_env.py | validator | duplicate/unknown/malformed detection | live run FAILs (2 unknown) |
| docs/security/CREDENTIAL_ROTATION_REGISTER.md | register | 20 inherited classes, evidence rules | 20/20 PENDING as of 2026-10-04 |
| mct/runbooks/credential-rotation-checklist.md | checklist | vendored status table | all rows PENDING |
| automation/validation/rotation_status.py | validator | tracker counts + --live store metadata | ran 2026-10-09 |
| automation/validation/secret_scan.py + .gitleaks.toml | scanner | tree/history secret detection | tree scan PASS at 08e20d1 |
| .github/workflows/validate.yml | CI | gitleaks pinned + history scan | checksum-pinned download |
| docs/security/BREAK_GLASS_CUSTODY.md | docs | emergency access procedure | OD-04 PENDING |
| /srv/falcon/secrets (live) | live store | permissions of the split stores | 0600 root; two 0640 htpasswd; ca.pem 0644 |
| /opt/wazuh-docker/multi-node/ops/creds.env (live) | inherited store | rotation target | 0600 user, mtime 2026-08-31 |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Owner env validator | `python3 automation/validation/check_owner_env.py` (read-only) | 9 keys, expected 7, mode 0600, 0 duplicates, 2 unknown (do_api, unifi_cert_sha256) -> FAIL |
| Rotation tracker | `python3 automation/validation/rotation_status.py` | 20 items / 0 rotated / 20 pending |
| Live store metadata | `python3 automation/validation/rotation_status.py --live` | present ops/creds.env (0600, 2026-08-31), .env (2026-08-22), wazuh-local.env (2026-08-07), iris-shuffle.env (2026-08-27); absent /opt/mct-security-stack/.env and .../iris-web/.env |
| Tree secret scan | `python3 ci/validate.py` (secret-scan check) | PASS (NO_FINDINGS) |
| CI secret gates | validate.yml + run 37985725668 | gitleaks tree + history checks pass in CI (0 findings) |
| Live secret permissions | `sudo ls -la /srv/falcon/secrets` | dir 0700 root; values 0600; ntfy_htpasswd/ntop_htpasswd 0640; opensearch-ca.pem 0644 (public) |
| Owner capture file | `ls -la /home/user/.config/falcon/capture.env` | exists, 0600 (SEC-P2-002 single-key path done) |
| Client-exposed vars | repo grep for VITE_/NEXT_PUBLIC_/PUBLIC_ | none (no browser app); no `secrets.` use in workflows |

## Executive Summary

Strengths: the secret architecture is deliberate and documented — split per-class stores under /srv/falcon/secrets (root 0600), no secret literals in compose, single-key capture wrapper (capture.env 0600), a layered scanner (entropy scanner + gitleaks tree/history, both fail-closed), a validated rotation register that refuses ROTATED without capture evidence, and a written break-glass procedure. The tree scan and the CI gitleaks history scan are green at 08e20d1.

Risks: the inherited credential estate remains 20/20 PENDING with stores untouched since August 2026, and vendored MCT scripts still source whole credential files into their process environment. The live owner credential file has drifted from its documented inventory (2 unknown keys) and the validator that detects this is not wired into any gate. Break-glass custody is procedural only (OD-04 pending). Register/live-store paths for IRIS/MCT rows are stale after consolidation, so the --live verification cannot cover them.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Owner env example | .env.example | documented key set | 7 keys | low | matches inventory |
| Owner env live | /home/user/.env | owner credentials | 9 keys, 0600 | medium | 2 undocumented keys |
| Owner validator | check_owner_env.py | inventory drift detection | works; not gated | medium | proposed wiring only |
| Rotation register | CREDENTIAL_ROTATION_REGISTER.md | 20 classes + evidence rules | 20/20 PENDING | high | unchanged since 2026-10-04 |
| Rotation tracker | rotation_status.py | counts + live metadata | works | low | read-only |
| Vendored sourcing | mct/**/*.sh | whole-file credential sourcing | 23 scripts (14 set -a) | medium | doc says 28/22 |
| Tree scanner | secret_scan.py | entropy + patterns | green at 08e20d1 | low | hash-only allowlist |
| gitleaks gates | validate.yml | tree + history scan | pinned, green | low | local binary absent (DET-P3-002) |
| Break-glass | BREAK_GLASS_CUSTODY.md | emergency access | procedure only | medium | OD-04 PENDING |
| Live split stores | /srv/falcon/secrets | first-party secrets | 0600 root | low | htpasswd 0640 by design |
| Inherited stores | /opt/wazuh-docker/multi-node/* | Wazuh/MCT creds | 0600 user, Aug mtimes | high | pending rotation |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| .env.example | 4 | .env.example:1-18 | live file drifted | reconcile then keep in lockstep |
| Env docs | 4 | OWNER_ENV_INVENTORY.md, IDENTITY_AND_SECRETS.md | claims stale vs live | refresh |
| Runtime validators | 4 | check_owner_env.py, rotation_status.py, check_rotation_register.py | owner-env not gated | wire into ci/validate.py |
| CI/deploy/local secrets | 4 | /srv/falcon/secrets 0600, no literals, capture.env | whole-file env injection (env_file) | per-key secrets long term |
| API/JWT/DB/webhook/oauth/email/push/Sentry/payment/cloud/GitHub keys | 4 | split stores + fingerprints; no payment/email/push classes present | inherited estate unrotated | execute rotation |
| Naming consistency | 4 | canonical NTfy_TOPIC in ntfy.env; inventory rules | do_api vs do_pf ambiguity | document/rename |
| Client-exposed vars | 5 | none (no browser app); Grafana anonymous off | none | keep |
| Rotation/revocation docs | 4 | INHERITED_CREDENTIAL_ROTATION.md + register | execution pending; paths stale | execute + fix paths |
| Break-glass | 2 | BREAK_GLASS_CUSTODY.md | OD-04 pending; no rehearsal | owner closure |

## Detailed Review

### Item: Owner env inventory and validator

- Evidence: .env.example:1-18; docs/security/OWNER_ENV_INVENTORY.md:8-27,47,49-74; live validator run 2026-10-09.
- What it does: validator fails on duplicate/unknown/malformed keys, warns on missing/mode; never prints values.
- Current controls: run by hand; offline fixture suite runs in the gate.
- Missing controls: no live check in ci/validate.py (explicitly proposed, not applied).
- Risks: undocumented credentials accumulate (2 today) with no CI signal.

### Item: Inherited rotation estate

- Evidence: CREDENTIAL_ROTATION_REGISTER.md:12-13,20-39; rotation_status.py (20/20); live store mtimes.
- What it does: execution order, negative tests, capture-id evidence rule.
- Missing controls: execution itself; the tracker gate (--fail-if-pending) is not wired into any scheduled check.
- Risks: any inherited key exposure remains valid indefinitely.

### Item: Vendored wholesale sourcing

- Evidence: INHERITED_CREDENTIAL_ROTATION.md:72-78; independent scan (23 scripts under mct/**, 14 with set -a).
- Missing controls: migration to the single-key reader is deferred as a vendored change.

### Item: Break-glass

- Evidence: BREAK_GLASS_CUSTODY.md:5-8,26-54.
- Current state: root via sudo, controlled by file mode; no custodian/sealed value/rehearsal.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SECRET-001 | .env.example | .env.example | 7 documented keys | live drift | P2 | reconcile + gate |
| SECRET-002 | Env docs | OWNER_ENV_INVENTORY.md | inventory | stale PASS claim | P3 | refresh |
| SECRET-003 | Runtime validators | check_owner_env.py | fail-closed | not wired | P2 | wire into gate |
| SECRET-004 | CI/deploy/local secrets | /srv/falcon/secrets | 0600, no literals | env_file whole-file injection | P2 | per-key secrets |
| SECRET-005 | API/DB/cloud keys | split stores | per-class files | rotation pending | P2 | execute rotation |
| SECRET-006 | Naming consistency | inventory rules | canonical names | do_api/do_pf ambiguity | P3 | document |
| SECRET-007 | Client-exposed vars | repo grep | none exposed | none | - | keep |
| SECRET-008 | Rotation/revocation docs | register + procedure | complete procedure | unexecuted; stale paths | P2/P3 | execute + fix |
| SECRET-009 | Break-glass | BREAK_GLASS_CUSTODY.md | procedure written | OD-04 pending | P3 | owner closure |

## Findings

### SECRET-P2-001 - Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale

- Severity: P2
- Confidence: High
- Area: SECRET
- Evidence: docs/security/CREDENTIAL_ROTATION_REGISTER.md:12-13,20-39; rotation_status.py output 2026-10-09; mct/runbooks/credential-rotation-checklist.md:9-49; docs/security/INHERITED_CREDENTIAL_ROTATION.md:72-78.
- What is happening: unchanged since the prior run. The register and vendored checklist are 20/20 PENDING; --live shows the inherited stores with August 2026 mtimes (ops/creds.env 2026-08-31, wazuh-local.env 2026-08-07); 23 scripts under mct/** still source creds.env/wazuh-local.env/.env wholesale (14 with set -a; docs count 28/22 across a wider set).
- Why it matters: inherited credentials with unknown exposure history remain valid across Wazuh, IRIS, MISP, Shuffle, DO Spaces, PVE and Security Onion; wholesale sourcing also puts those values into script process environments.
- User / business impact: breach blast radius; evidence rules require capture-id per rotation so progress is auditable.
- Security / privacy / reliability impact: high if any inherited key leaked in the 2026-09-30 exposure set.
- Recommended fix: execute the documented rotation order (owner-console steps first), record name-only captures per row, then migrate vendored scripts to automation/validation/lib/env_key.sh.
- Suggested validation: `python3 automation/validation/rotation_status.py --fail-if-pending` in a scheduled owner check; negative test per row (old value rejected).
- Owner suggestion: owner (console steps) + platform (automation).
- Effort estimate: L (owner-gated)
- Dependencies: console access; MCT vendoring policy.
- Status: still-open (prior SECRET-P2-001)
- Attack path: leaked inherited credential -> console/API access without new exploitation.

### SECRET-P2-002 - Live owner credential file has undocumented keys and the validator is not wired into any gate

- Severity: P2
- Confidence: High
- Area: SECRET
- Evidence: `python3 automation/validation/check_owner_env.py` (2026-10-09: 9 keys, expected 7, mode 0600, 0 duplicates, 2 unknown -> FAIL); .env.example:1-18; docs/security/OWNER_ENV_INVENTORY.md:20-27,47; ci/validate.py:593-615; docs/security/CI_SECRET_GATE.md:173-175.
- What is happening: the live file carries do_api (line 8) and unifi_cert_sha256 (line 9), neither documented; the inventory page still claims 7 keys/PASS; the validator is documented as a proposed ci/validate.py check but no owner-env check exists in the gate.
- Why it matters: do_api is plausibly a second DigitalOcean token alongside do_pf — an untracked credential class with no owner, rotation or revocation row; unifi_cert_sha256 is likely a fingerprint but is undocumented.
- User / business impact: credential inventory drift; owner cannot rely on the page as truth.
- Security / privacy / reliability impact: an unmanaged secret can outlive its purpose or leak unnoticed.
- Recommended fix: reconcile the inventory (document or remove each key; consolidate the DO tokens), refresh OWNER_ENV_INVENTORY.md, and wire check_owner_env.py into ci/validate.py as the documented snippet.
- Suggested validation: run the validator in the gate (skipped when the file is absent) and re-run it after each rotation (--strict).
- Owner suggestion: owner + coordinator (validate.py ownership).
- Effort estimate: S
- Dependencies: none.
- Status: open
- Attack path: none identified (hygiene/traceability).

### SECRET-P3-001 - Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation

- Severity: P3
- Confidence: High
- Area: SECRET
- Evidence: rotation_status.py --live 2026-10-09 (absent /opt/mct-security-stack/.env, absent /opt/mct-security-stack/data/dfir-iris/iris-web/.env; present /srv/falcon/secrets/iris-web.env and mct.env); live IRIS container label config_files=/opt/iris-web/docker-compose.yml; CREDENTIAL_ROTATION_REGISTER.md:30-39; credential-rotation-checklist.md:40-49.
- What is happening: rows 11-20 name pre-consolidation VM paths that no longer exist on this host, so their --live verification cannot be produced and the register's evidence requirements point at the wrong stores.
- Why it matters: rotation evidence for IRIS/MISP/Shuffle rows cannot be captured where the register says.
- Recommended fix: update register/checklist paths to the consolidated stores (or mark migrated rows and record the new store), then re-run --live.
- Suggested validation: rotation_status.py --live reports no absent store for rows that exist on this host.
- Owner suggestion: owner.
- Effort estimate: S
- Status: open

### SECRET-P3-002 - Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal

- Severity: P3
- Confidence: High
- Area: SECRET
- Evidence: docs/security/BREAK_GLASS_CUSTODY.md:5-8,26-54; docs/architecture/IDENTITY_AND_SECRETS.md:4-7; live capture.env 0600 exists.
- What is happening: today the only emergency path is root via sudo with the sudo value in /home/user/.env or capture.env, controlled by file mode alone; the custody procedure (custodians, sealed value, two-person rule, post-use rotation, annual review) and tabletop checklist are written but unchecked.
- Why it matters: single-account emergency access with no custody/rehearsal is a recovery and auditability gap; IDENTITY_AND_SECRETS requires documented custody.
- Recommended fix: owner names custodians, seals the credential, runs the tabletop, and logs the decision row to close OD-04.
- Suggested validation: tabletop capture via automation/evidence/capture.sh --name break-glass-tabletop.
- Owner suggestion: owner.
- Effort estimate: S (owner time)
- Status: open

## Prior-Run Comparison

- SECRET-P2-001 (inherited rotation + wholesale sourcing): still-open, unchanged; kept with the prior ID. Live metadata confirms zero rotations since the prior run.
- No other prior SECRET findings in the pack lineage. The repo's own SECRET-P2-006 (owner-env inventory) has regressed at the data level: the live file now fails its own validator (SECRET-P2-002 here); SECRET-P3-008 (break-glass) remains open as SECRET-P3-002 here.
- SEC-P2-002 (single-key capture) verified done: /home/user/.config/falcon/capture.env exists 0600 and ci/validate.py credential-sourcing check passes.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Inherited credential still valid | High | Medium | High | 20/20 pending; Aug mtimes | execute rotation |
| Undocumented owner key | Medium | Medium | Medium | validator FAIL | reconcile + gate |
| Emergency access unrehearsed | Medium | Low | High | OD-04 pending | tabletop + sealing |
| Rotation evidence paths stale | Low | High | Medium | --live absent stores | fix register |

## Recommendations

### Immediate / Release Blocking
- None demonstrated as an active leak; the exposure-set keys (VT/cluster/Shuffle) were rotated in the 2026-09-30 wave per the register history.

### This Week
- Reconcile /home/user/.env and wire check_owner_env.py into ci/validate.py.
- Fix the register paths for the consolidated stores.

### This Month
- Execute the rotation order with name-only captures; migrate vendored scripts to env_key.sh.
- Owner closure of OD-04 (break-glass custody).

### Later / Platform Evolution
- Move env_file whole-file injection to per-key Docker secrets; add a scheduled --fail-if-pending owner check.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Remove/rename do_api | removes an untracked credential class | /home/user/.env, .env.example, OWNER_ENV_INVENTORY.md | check_owner_env.py |
| Wire the owner-env check | drift becomes a gate failure | ci/validate.py | full gate |
| Fix register paths | --live verification works | CREDENTIAL_ROTATION_REGISTER.md, checklist | rotation_status.py --live |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rotation execution | P2 | owner | L | console access |
| Owner-env gate wiring | P2 | coordinator | S | none |
| Vendored env_key migration | P2 | platform | M | MCT vendoring policy |
| Break-glass closure | P3 | owner | S | none |

## Suggested Tests

- Add the owner-env validator as a ci/validate.py check (skip when absent) plus a negative fixture already present in owner_env_validator_test.sh.
- Add a gate check that the register's store paths exist on the host when --live runs (fail closed on absent rows).
- Extend rotation_status_test.sh with the consolidated-path fixtures.

## Suggested Documentation Updates

- docs/security/OWNER_ENV_INVENTORY.md: refresh to 9 keys and record do_api/unifi_cert_sha256 dispositions.
- docs/security/CREDENTIAL_ROTATION_REGISTER.md + mct/runbooks/credential-rotation-checklist.md: consolidated store paths.
- docs/security/BREAK_GLASS_CUSTODY.md: record the tabletop result when run.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What is do_api used for vs do_pf? | determines the credential class/owner | owner confirmation |
| Is unifi_cert_sha256 a secret or a fingerprint? | determines whether it belongs in .env | owner confirmation |
| When will the owner execute the rotation order? | the top residual in this domain | owner schedule |
| Should --fail-if-pending become a scheduled gate? | prevents silent non-rotation | owner decision |

## Limitations

- No values were read or printed; store observations are metadata only (mode/mtime/size).
- Rotation execution and console-side verification are owner-only and were not performed.
- History-scan entropy findings (36 classified: R-32/EX-21) were not re-run; the CI gitleaks history check is the current authority and is green.

## Appendix

Rotation tracker snapshot (2026-10-09, names only):

```
rotation_items=20 rotated=0 pending=20
rotation_live_stores:
  present /opt/wazuh-docker/multi-node/ops/creds.env mode=0600 mtime=2026-08-31T07:32:52Z
  present /opt/wazuh-docker/multi-node/.env mode=0600 mtime=2026-08-22T03:34:53Z
  present /opt/wazuh-docker/multi-node/wazuh-local.env mode=0600 mtime=2026-08-07T05:15:01Z
  present /opt/wazuh-docker/multi-node/ops/iris-shuffle.env mode=0600 mtime=2026-08-27T17:47:33Z
  absent /opt/mct-security-stack/.env
  absent /opt/mct-security-stack/data/dfir-iris/iris-web/.env
```

## Findings

| ID | Severity | Title |
|---|---|---|
| SECRET-P2-001 | P2 | Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale |
| SECRET-P2-002 | P2 | Live owner credential file has undocumented keys and the validator is not wired into any gate |
| SECRET-P3-001 | P3 | Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation |
| SECRET-P3-002 | P3 | Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal |
