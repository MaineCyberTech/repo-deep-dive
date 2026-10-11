# 38_env_secret_rotation — Prompt 38 - Environment and Secret Rotation Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `38_env_secret_rotation.md` (area SECRET, prompt)

## Verification Performed

# Environment and Secret Rotation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon @ f5cb7c9 (branch main), live lab host `falcon`
- Generated at: 2026-10-11T04:40:00Z
- Auditor: subagent (repo-deep-dive full, area SECRET)
- Area code: SECRET
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/38_env_secret_rotation.md
- Scope limitations: read-only. No secret values were printed; only names, paths, modes, mtimes and counts are recorded. Rotation execution is owner-gated and was not performed. Third-party consoles (DO, Cloudflare, UniFi, MISP, Shuffle UI) were not accessed.

## Scope

Reviewed at f5cb7c9: `.env.example`, docs/security/* (owner-env inventory, rotation register/procedure, break-glass custody, CI secret gate, scanner allowlists), the runtime validators (`check_owner_env.py`, `rotation_status.py`, `check_rotation_register.py`, `secret_scan.py`), the CI secret gates (gitleaks static + history), the compose secret-consumption paths (env_file + /srv/falcon/secrets), the inherited Wazuh/MCT credential stores (metadata only), the vendored wholesale-sourcing residual, and live file permissions for `/home/user/.env`, `/home/user/.config/falcon/capture.env` and `/srv/falcon/secrets`.

Not reviewed: any credential value material, and any rotation execution (owner-gated).

Companion artifacts (in-repo, satisfying the prompt's required outputs):
- Rotation runbook: docs/security/INHERITED_CREDENTIAL_ROTATION.md + docs/security/CREDENTIAL_ROTATION_REGISTER.md + mct/runbooks/credential-rotation-checklist.md
- Env inventory: docs/security/OWNER_ENV_INVENTORY.md + .env.example + docs/architecture/IDENTITY_AND_SECRETS.md
- Secret classification: docs/architecture/IDENTITY_AND_SECRETS.md sections 2-3
- Emergency revocation: INHERITED_CREDENTIAL_ROTATION.md (per-item negative tests) + docs/security/BREAK_GLASS_CUSTODY.md

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| .env.example | env example | documented owner key set (7) | names only, no values |
| /home/user/.env | live env | actual owner key set | metadata only (9 keys, mode 0600) |
| automation/validation/check_owner_env.py | validator | owner-file inventory check | names only; fails on unknown/duplicate/malformed |
| automation/validation/rotation_status.py | validator | rotation checklist + live store stats | report-only; --live stats modes/mtimes only |
| docs/security/CREDENTIAL_ROTATION_REGISTER.md | register | 20 inherited classes | status as of 2026-10-04: 20/20 PENDING |
| mct/runbooks/credential-rotation-checklist.md | checklist | vendored status table + key-file index | rows 13-20 point at pre-consolidation paths |
| docs/security/OWNER_ENV_INVENTORY.md | docs | expected key set + CI wiring plan | claims 7 keys/PASS (2026-10-01); wiring still "proposed" |
| docs/security/BREAK_GLASS_CUSTODY.md | docs | emergency access procedure | OD-04 PENDING; rehearsal unchecked |
| docs/phase0/OWNER_DECISIONS.json | decisions | OD-04 status | status: PENDING |
| ci/validate.py | gate | CHECKS dict (21 checks) | no owner-env check registered |
| .github/workflows/validate.yml | CI | gitleaks static + history scans | pinned gitleaks v8.30.1; passes |
| /srv/falcon/secrets/ | live store | consolidated per-class files | dir 0700 root; files 0600 (CA cert 0644) |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 automation/validation/check_owner_env.py` | live validator | owner-file drift | 9 keys / expected 7 / 2 unknown -> FAIL (exit 1) |
| `sudo python3 automation/validation/rotation_status.py --live` | live validator | rotation + stores | 20 items / 0 rotated / 20 pending; wazuh stores mtimes Aug 2026 |
| live store listing | live | consolidated stores exist | /srv/falcon/secrets/mct.env + iris-web.env present (0600) |
| `ls -la /home/user/.config/falcon/capture.env` | live | break-glass single-key path | 0600, 15 bytes |
| ci/validate.py CHECKS inspection | repo | validator wiring | no owner-env entry (21 checks) |
| wholesale-sourcing scan | repo | vendored residual | 28 files source creds.env/wazuh-local.env/.env |

## Executive Summary

The secret hygiene around the deployed platform is strong: secrets live in root-only stores under /srv/falcon/secrets (0700 dir, 0600 files), compose consumes them via env_file and docker secrets, no secrets are committed (gitleaks static + history gates pass), and the delivery pack contains no secret files. The structural gaps from the prior run are unchanged at f5cb7c9 and remain the dominant risk: the inherited credential estate is still 20/20 pending rotation, the live owner file has two undocumented keys and the validator that detects this is not wired into any gate, the rotation register/checklist still point at pre-consolidation stores for rows 11-20, and break-glass custody is procedural only (OD-04 PENDING) with no custodian, sealed credential, or rehearsal.

Two documentation artifacts now contradict live state and should be corrected with the remediation: docs/security/OWNER_ENV_INVENTORY.md:47 still states "7 keys ... PASS" while the live file fails with 9 keys/2 unknown, and CI_SECRET_GATE.md:239 records the same 7-key claim. The consolidated stores (/srv/falcon/secrets/mct.env, iris-web.env) exist and are the correct targets for the register rows that still name /opt/mct-security-stack paths.

Recommended next actions: wire `check_owner_env.py` into `ci/validate.py` and reconcile the inventory; update the register/checklist to the consolidated stores; execute the documented rotation order with name-only capture evidence per row; and complete OD-04 (custodian + sealed credential + rehearsal).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Owner env example | .env.example | documented 7-key set | current, matches inventory doc | Low | missing the 2 live extras |
| Owner env (live) | /home/user/.env | owner credentials | 9 keys, mode 0600, 2 unknown | Medium | do_api, unifi_cert_sha256 |
| Capture env | /home/user/.config/falcon/capture.env | sudo single-key path | 0600, 1 key | Low | SEC-P2-002 path done |
| Owner validator | automation/validation/check_owner_env.py | drift detector | works; not wired | Medium | fails on live file |
| Rotation register | docs/security/CREDENTIAL_ROTATION_REGISTER.md | 20 classes | 20/20 PENDING (2026-10-04) | High (owner-gated) | rows 11-20 stores stale |
| Rotation checklist | mct/runbooks/credential-rotation-checklist.md | vendored table | 20/20 PENDING | High | key-file index stale |
| Live Wazuh stores | /opt/wazuh-docker/multi-node/* | inherited creds | present, 0600, Aug 2026 mtimes | High | untouched since import |
| Consolidated stores | /srv/falcon/secrets/{mct,iris-web}.env | MCT/IRIS creds | present, 0600, Sep 28 mtimes | Medium | register does not point here |
| Break-glass | docs/security/BREAK_GLASS_CUSTODY.md | emergency access | procedure written; OD-04 PENDING | Medium | no rehearsal |
| CI secret gate | validate.yml + gitleaks | leak prevention | active, pinned | Low | passes |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| .env.example | 4 | 7 keys documented; validator test uses it | missing the 2 live extras | reconcile after decision |
| Env docs | 3 | OWNER_ENV_INVENTORY + IDENTITY_AND_SECRETS | stale 7-key/PASS claim | update with the fix |
| Runtime validators | 3 | check_owner_env.py, rotation_status.py work | owner-env not wired into ci/validate.py | register in CHECKS |
| CI/deploy/local secrets | 4 | root-only stores; env_file; gitleaks gates | none material | - |
| API/JWT/DB/... keys | 2 | register covers 20 classes | 20/20 pending; stores untouched | execute rotation |
| Naming consistency | 4 | consistent per-class files | 2 undocumented owner keys | reconcile |
| Client-exposed vars | 5 | no client bundle; server-side repo | - | - |
| Rotation/revocation docs | 3 | register + procedure + negative tests | register stores stale; no rotation evidence | update + execute |
| Break-glass | 1 | procedure only; OD-04 PENDING | no custodian/sealed value/rehearsal | complete OD-04 |

## Detailed Review

### Item: Owner credential file and validator
- Evidence: check_owner_env.py output (2026-10-11): keys=9 expected=7 mode=0600 duplicates=0 unknown=2 (do_api line 8, unifi_cert_sha256 line 9) -> FAIL; .env.example (7 keys); OWNER_ENV_INVENTORY.md:47,49-74; ci/validate.py:593-615.
- What it does: documents and validates the owner key set.
- Current controls: file mode 0600; validator exists and is tested (owner_env_validator_test.sh passes in the gate).
- Missing controls: gate wiring; inventory reconciliation.
- Risks: undocumented credentials (plausibly a second DigitalOcean token) without lifecycle; drift invisible except by hand.
- Recommended improvement: decide on the 2 keys (document or remove), update .env.example/inventory, register the check in ci/validate.py.
- Suggested tests: existing suite; add a fixture mirroring the live 9-key file to prove FAIL output.
- Suggested docs: OWNER_ENV_INVENTORY.md current-state line.

### Item: Inherited rotation estate
- Evidence: rotation_status.py --live: 20/0/20; stores /opt/wazuh-docker/multi-node/*.env present with Aug 2026 mtimes; register 20/20 PENDING; 28 vendored scripts wholesale-source.
- What it does: tracks the MCT/Wazuh inherited credential classes.
- Current controls: register + checklist + capture-id evidence rule (check_rotation_register.py fails closed on ROTATED without capture).
- Missing controls: executed rotations; vendored script migration to env_key.sh.
- Risks: long-lived inherited credentials in readable stores; wholesale-sourcing exposes them to every process environment.
- Recommended improvement: execute the documented rotation order; migrate vendored scripts in a sanctioned vendored-patch wave.
- Suggested tests: rotation_register_test.sh; add a live pre/post negative-test capture per row.
- Suggested docs: register rows after each rotation.

### Item: Register path staleness
- Evidence: checklist rows 13/16/18/19/20 and the key-file index name /opt/mct-security-stack/...; rotation_status.py --live reports those paths absent while /srv/falcon/secrets/mct.env and iris-web.env are present (0600).
- What it does: maps classes to stores.
- Missing controls: consolidated paths in the register/checklist.
- Risks: --live verification cannot be produced for rows 11-20 on this host; rotation evidence could target the wrong store.
- Recommended improvement: update rows 11-20 and the key-file index to the consolidated stores (or mark migrated explicitly).
- Suggested tests: a doc/live path consistency test.
- Suggested docs: CREDENTIAL_ROTATION_REGISTER.md, credential-rotation-checklist.md.

### Item: Break-glass custody
- Evidence: BREAK_GLASS_CUSTODY.md:5-8 (OD-04 PENDING; only path is sudo value in /home/user/.env or capture.env, mode-controlled); docs/phase0/OWNER_DECISIONS.json OD-04 PENDING; no rehearsal row in ledgers/decision_log.md.
- Missing controls: custodian naming, sealed credential, two-person rule, post-use rotation, annual review, rehearsal.
- Risks: emergency access depends on a single file mode; no custody record.
- Recommended improvement: complete OD-04 and run the documented tabletop checklist.
- Suggested tests: rehearsal capture `break-glass-tabletop`; a check that the decision log has a rehearsal row.
- Suggested docs: BREAK_GLASS_CUSTODY.md.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SECRET-001 | .env.example | .env.example | 7 keys documented | 2 live extras undocumented | P2 | reconcile |
| SECRET-002 | Env docs | OWNER_ENV_INVENTORY.md:47 | inventory + validator | stale PASS claim | P2 | update |
| SECRET-003 | Runtime validators | check_owner_env.py; ci/validate.py:593-615 | validator exists | not wired into any gate | P2 | register check |
| SECRET-004 | CI/deploy/local secrets | validate.yml; /srv/falcon/secrets | gitleaks + root-only stores | none material | - | - |
| SECRET-005 | API/JWT/DB/... keys | register + live stores | tracked, evidence rule | 20/20 pending | P2 | execute rotation |
| SECRET-006 | Naming consistency | store listing | per-class files | 2 unknown owner keys | P2 | reconcile |
| SECRET-007 | Client-exposed vars | repo is server-side | none | - | - | - |
| SECRET-008 | Rotation/revocation docs | register; checklist | documented + negative tests | stale paths; no execution evidence | P3 | update + execute |
| SECRET-009 | Break-glass | BREAK_GLASS_CUSTODY.md; OD-04 | procedure written | no custody/rehearsal | P3 | complete OD-04 |

## Findings

### SECRET-P2-001 - Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale

- Severity: P2
- Confidence: High
- Area: SECRET
- Evidence:
  - `docs/security/CREDENTIAL_ROTATION_REGISTER.md:12-13` (20/20 PENDING; capture-id rule)
  - `mct/runbooks/credential-rotation-checklist.md:9-49` (all rows PENDING)
  - Command: `sudo python3 automation/validation/rotation_status.py --live` (2026-10-11: 20 items / 0 rotated / 20 pending; /opt/wazuh-docker/multi-node/*.env mtimes 2026-08-07..2026-08-31)
  - Independent scan: 28 files under mct/scripts + mct/deploy-scripts source creds.env/wazuh-local.env/.env wholesale (19 with set -a)
- What is happening: the inherited MCT/Wazuh credential estate has not been rotated since import; vendored automation still loads whole credential files into process environments.
- Why it matters: long-lived credentials in shared stores widen the window for credential theft and complicate revocation.
- User / business impact: inherited-credential compromise would require a large, unplanned rotation event under pressure.
- Security / privacy / reliability impact: no rotation evidence; wholesale sourcing leaks credentials into child processes/environments.
- Recommended fix: execute the documented rotation order with name-only capture evidence per row; then migrate the vendored scripts to `automation/validation/lib/env_key.sh` in an owner-approved vendored patch wave.
- Suggested validation: `check_rotation_register.py` (fails closed on ROTATED without capture); per-row negative test (old value must fail).
- Owner suggestion: owner (OWNER-console rows) + platform (OWNER-host rows)
- Effort estimate: L
- Dependencies: owner console access; MCT vendoring policy (EVOL-P1-002)
- Status: still-open

### SECRET-P2-002 - Live owner credential file has undocumented keys and the validator is not wired into any gate

- Severity: P2
- Confidence: High
- Area: SECRET
- Evidence:
  - Command: `python3 automation/validation/check_owner_env.py` (2026-10-11: keys=9 expected=7 unknown=2 -> FAIL; unknown: do_api line 8, unifi_cert_sha256 line 9; mode 0600)
  - `.env.example:1-18` (7 documented keys)
  - `docs/security/OWNER_ENV_INVENTORY.md:47` ("7 keys ... PASS", 2026-10-01) and `:49-74` (CI wiring "proposed")
  - `ci/validate.py:593-615` (CHECKS dict; no owner-env entry)
  - `docs/security/CI_SECRET_GATE.md:239` (evidence row records the 7-key claim)
- What is happening: the live owner file contains two keys that exist nowhere in the repository documentation, and the validator that detects this runs only by hand.
- Why it matters: undocumented credentials (do_api plausibly a second DigitalOcean token) have no owner, purpose, or rotation path, and the drift is invisible to every gate.
- User / business impact: unknown-credential exposure would be discovered only in an incident.
- Security / privacy / reliability impact: shadow credential class; no revocation procedure.
- Recommended fix: reconcile the inventory (document or remove the two keys), update .env.example/OWNER_ENV_INVENTORY.md, and register `check_owner_env` in `ci/validate.py` CHECKS.
- Suggested validation: the existing `owner_env_validator_test.sh`; a fixture reproducing the live 9-key file; gate run showing the check.
- Owner suggestion: owner (key decision) + CI coordinator (wiring)
- Effort estimate: S
- Dependencies: owner decision on do_api/unifi_cert_sha256
- Status: still-open

### SECRET-P3-001 - Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation

- Severity: P3
- Confidence: High
- Area: SECRET
- Evidence:
  - `mct/runbooks/credential-rotation-checklist.md:40-55` (rows 13/16/18/19/20 and key-file index name /opt/mct-security-stack/... and /opt/mct-security-stack/data/dfir-iris/iris-web/.env)
  - Command: `sudo python3 automation/validation/rotation_status.py --live` (those paths absent; `/srv/falcon/secrets/mct.env` and `/srv/falcon/secrets/iris-web.env` present, 0600)
  - `docs/security/CREDENTIAL_ROTATION_REGISTER.md:30-39` (rows 13/18/19 name the pre-consolidation stores)
- What is happening: the rotation register/checklist still point at pre-consolidation VM stores; the consolidated per-class stores under /srv/falcon/secrets are not named.
- Why it matters: rotation evidence for rows 11-20 cannot be produced against the documented paths on this host.
- User / business impact: rotation work could target or verify the wrong store.
- Security / privacy / reliability impact: verification gap on 10 of 20 rows.
- Recommended fix: update rows 11-20 and the key-file index to the consolidated stores or mark migrated rows explicitly.
- Suggested validation: a doc-vs-live path check in rotation_status_test.sh.
- Owner suggestion: security
- Effort estimate: S
- Dependencies: none
- Status: still-open

### SECRET-P3-002 - Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal

- Severity: P3
- Confidence: High
- Area: SECRET
- Evidence:
  - `docs/security/BREAK_GLASS_CUSTODY.md:5-8,26-54` (OD-04 PENDING; only path is sudo value in /home/user/.env or capture.env; custody/rehearsal steps unchecked)
  - `docs/phase0/OWNER_DECISIONS.json` OD-04 status: PENDING
  - Command: `ls -la /home/user/.config/falcon/capture.env` (0600, 15 bytes)
  - `ledgers/decision_log.md` has no break-glass rehearsal row
- What is happening: emergency access relies on a single file-mode-protected credential; no custodian, sealed copy, or exercised procedure exists.
- Why it matters: a lost or unavailable credential during an incident has no documented recovery path.
- User / business impact: extended outage risk during a host-loss/incident scenario.
- Security / privacy / reliability impact: no two-person rule; no post-use rotation evidence.
- Recommended fix: owner names custodians, seals the credential, runs the documented tabletop checklist, and logs the decision row.
- Suggested validation: `automation/evidence/capture.sh --gate REVIEW-FIX --name break-glass-tabletop -- <rehearsal command>`.
- Owner suggestion: owner
- Effort estimate: M
- Dependencies: OD-04 owner decision
- Status: still-open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Inherited credentials never rotated | P2 | Medium | High | register 20/20 pending; stores Aug 2026 | execute rotation |
| Shadow owner credentials | P2 | Medium | Medium | check_owner_env FAIL (2 unknown) | reconcile + wire gate |
| Rotation evidence impossible for 10 rows | P3 | High | Medium | stale register paths | update register |
| Break-glass unavailable in an incident | P3 | Low | High | OD-04 pending | complete custody + rehearsal |

## Recommendations

### Immediate / Release Blocking
- None (no committed or client-exposed secret found).

### This Week
- Reconcile the owner-env inventory and wire `check_owner_env` into `ci/validate.py` (SECRET-P2-002).
- Update register/checklist stores for rows 11-20 (SECRET-P3-001).

### This Month
- Execute the rotation order with per-row captures and negative tests (SECRET-P2-001).
- Complete OD-04 break-glass custody (SECRET-P3-002).

### Later / Platform Evolution
- Migrate the 28 wholesale-sourcing vendored scripts to env_key.sh in a sanctioned patch wave.
- Add a live store inventory test (paths/modes) to CI where a host is available.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Register owner-env check in ci/validate.py | drift becomes visible in every gate | ci/validate.py | local gate run |
| Update OWNER_ENV_INVENTORY.md current-state line | removes contradiction with live | docs/security/OWNER_ENV_INVENTORY.md | doc review |
| Fix register rows 13-20 to /srv/falcon/secrets | makes --live verification possible | register + checklist | rotation_status.py --live |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rotate the 20 inherited classes | P2 | owner/platform | L | console access |
| Wire owner-env validator | P2 | CI coordinator | S | owner key decision |
| Vendored script migration to env_key.sh | P3 | platform | M | EVOL-P1-002 |
| Break-glass custody + rehearsal | P3 | owner | M | OD-04 |

## Suggested Tests

- Unit: owner_env_validator fixtures incl. the live 9-key case.
- Integration: rotation_status --live run as a scheduled host check with path assertions.
- CI: owner-env check wired into the gate (skips when the file is absent).
- Security: gitleaks static + history already enforced; keep the pinned versions.
- Manual: post-rotation negative tests per register row.

## Suggested Documentation Updates

- docs/security/OWNER_ENV_INVENTORY.md (current state + CI wiring status).
- docs/security/CI_SECRET_GATE.md (replace the 7-key claim).
- docs/security/CREDENTIAL_ROTATION_REGISTER.md and mct/runbooks/credential-rotation-checklist.md (consolidated stores).
- docs/security/BREAK_GLASS_CUSTODY.md (custody rows once OD-04 completes).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What are do_api and unifi_cert_sha256? | decides document-vs-remove and rotation class | owner statement |
| Which rows are OWNER-console vs automatable on this host? | rotation sequencing | owner assignment |
| Is /opt/mct-security-stack still the MISP/Greenbone store on the VM? | row 13/18 verification | VM inspection |

## Appendix

- Validator outputs captured 2026-10-11: check_owner_env.py (9/7/2 FAIL); rotation_status.py --live (20/0/20; stores listed above).
- /srv/falcon/secrets listing (names/modes only): dir 0700 root; per-class files 0600; opensearch-ca.pem 0644; htpasswd files 0640.
- No secret material was found in review-package/ or the pack manifest; config archives are encrypted (.enc).

## Findings

| ID | Severity | Title |
|---|---|---|
| SECRET-P2-001 | P2 | Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale |
| SECRET-P2-002 | P2 | Live owner credential file has undocumented keys and the validator is not wired into any gate |
| SECRET-P3-001 | P3 | Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation |
| SECRET-P3-002 | P3 | Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal |
