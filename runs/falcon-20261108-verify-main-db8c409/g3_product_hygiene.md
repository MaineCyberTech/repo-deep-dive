# G3 — Product / Docs / Evolution / Hygiene — verification pass

**Repository:** `MaineCyberTech/falcon`  
**Target:** `main@db8c40970083a98e50dbae8038971ec2ac6bc252` (2026-11-05T23:42:19-05:00)  
**Previous run:** `falcon-20261014-verify-main-edbf441`  
**Generated:** 2026-11-08T06:45:00Z  
**Lens:** G3 — product/docs/evolution/hygiene  
**Mode:** read-only verification; no commits, pushes or runtime changes.

## Method and limits

Read-only verification at db8c409 (shallow clone + GitHub API for commit/tag/CI state); file:line evidence in the falcon tree; pack checks in /root/repo-deep-dive at 4f42d9b; no secret values read or printed.

A shallow clone at `db8c409` was used for the tree evidence. GitHub API reads (tags, compare, check-runs, commit history) supplied commit distance and CI state. The audit pack at `/root/repo-deep-dive` (`4f42d9b`) supplied `tools/full_domain.py`, `tools/check_run.sh` and the committed run folders. Live-only state (Grafana rule count, container list, Wazuh indices) is not re-measured in this pass; where a claim depends on live state it is marked as such and the repository-side evidence is given. No credential values were read or printed.

**Summary:** No new P0/P1 findings. 8 new findings: 6 P2 and 2 P3. Two P3 items carry regression status: FEAT-P3-001 is newly regressed; INV-P3-002 remains regressed and worsened. Of the 36 re-verified findings: 18 verified-fixed, 9 partially-fixed, 5 open, 2 regressed, 2 owner-accepted.

## Counts

| Group | Total | verified-fixed | partially-fixed | open | regressed | owner-accepted |
|---|---:|---:|---:|---:|---:|---:|
| ARCH | 5 | 3 | 0 | 0 | 0 | 2 |
| EVOL | 4 | 3 | 1 | 0 | 0 | 0 |
| FEAT | 2 | 1 | 0 | 0 | 1 | 0 |
| DOC | 6 | 2 | 1 | 3 | 0 | 0 |
| HYGIENE | 4 | 2 | 2 | 0 | 0 | 0 |
| INV | 8 | 3 | 0 | 4 | 1 | 0 |
| ORCH | 5 | 1 | 2 | 2 | 0 | 0 |
| REL | 6 | 2 | 2 | 2 | 0 | 0 |
| TEST | 4 | 1 | 1 | 2 | 0 | 0 |
| **G3 total** | **44** | **18** | **9** | **13** | **2** | **2** |

Re-verified: **36** findings from the 2026-10-14 pass. New: **8** (0 P1, 6 P2, 2 P3). Severity mix of all 44: **3 P1 / 20 P2 / 21 P3**.

| Severity | Re-verified | New |
|---|---:|---:|
| P1 | 3 | 0 |
| P2 | 14 | 6 |
| P3 | 19 | 2 |

## Regressions

`FEAT-P3-001` is a new regression this pass. `INV-P3-002` was already regressed at edbf441 and worsened (1–2 entries to 51). Neither is a P1/P2 security regression.

| ID | Sev | What regressed |
|---|---|---|
| `INV-P3-002` | P3 | **Still regressed / worse:** the pack-fidelity artifact now lists **51** unresolved `unexpected; investigate` entries (all SBOM/vuln files) instead of 1–2, and the gate still reports PASS. |
| `FEAT-P3-001` | P3 | The alert-rule count drifted by one again: 95 `write_rule` calls vs 94 catalogue/README/CURRENT_STATE entries, after `falcon-edge-spool-unretained` was added on 2026-10-14. |

## Changes vs the 2026-10-14 pass

| ID | edbf441 | db8c409 | Why |
|---|---|---|---|
| `ARCH-P2-002` | open | owner-accepted | 2026-10-15 owner decision accepts the 29 unpinned mct/compose refs under the expiring waiver and makes the tree archive-only; P4 manifest/drift gate added. |
| `ARCH-P2-003` | open | verified-fixed | Ingest is now mutual TLS + basic second factor with live handshake evidence. |
| `FEAT-P2-001` | open | verified-fixed | `container_drift_check.sh` no longer declares mct/compose; vendor manifest/drift gate exist. |
| `FEAT-P3-001` | verified-fixed | regressed | One-rule count drift recurred (95 source vs 94 catalogue/README). |
| `HYGIENE-P2-001` | open | partially-fixed | 60-day SBOM freshness gate added; size grew to 58.4 MB and nothing moved/compressed it. |
| `INV-P3-003` | open | verified-fixed | Digest-binding docstring corrected; freshness/ancestry explicitly delegated. |
| `ORCH-P2-001` | open | partially-fixed | A newer 2026-10-23 P0-free run is published, but the 2026-10-05 record still contradicts the gate and has no reconciliation note. |
| `REL-P3-001` | open | partially-fixed | `gen_changelog.py` exists; CHANGELOG stops at 2026.10.14. |
| `REL-P3-003` | open | partially-fixed | Packaged-closeout assertion added, but it allows 8 commits behind HEAD and the current package still embeds a previous-cycle closeout. |
| `TEST-P3-001` | open | partially-fixed | CI now verifies 7 in-repo captures (was 0); 1,295 remain external skips. |

## New findings

### P2

1. **`REL-P2-003` — main is unbound and red after the Kestrel SSO merges.** `PACKAGE_DIGEST.txt` declares `f79d786e`; seven commits have landed since, including the Kestrel SSO changes. The repository `validate` run on the `db8c409` push failed (`42164078378`) on `publication equality`: *commits after the declared commit touch source files*. The PR-only topic allowance lets PR CI pass while main stays red until a rebind; no rebind followed. The delivered package predates the SSO cutover.
2. **`INV-P2-002` — SBOM/vuln set is absent from the review pack while the package manifest lists it, and fidelity still says PASS.** `make-repomix.sh` excludes `sbom/*.cdx.json` and `sbom/vuln/**`; `pack_fidelity.py` writes 51 `unexpected; investigate` rows but returns 0 because it only fails on content mismatches. `PACK_NOT_INCLUDED.txt` has been stale since 2026-10-15.
3. **`INV-P2-003` — the review package omits the Falcon Console source and the root legal/version files.** `build_review_package.sh` copies a fixed directory list that omits `console/` (19 tracked files, including auth, SSO gateway, API, actions broker and tests) and copies only three root files (not LICENSE, NOTICE, VERSION, CHANGELOG.md or TESTING.md). `PACKAGE_MANIFEST.sha256` has zero `./console/`, `./LICENSE` or `./NOTICE` entries, so the formal delivered package cannot be used to review/rebuild the current root UI/API and does not carry the GPLv2 license text or NOTICE.
4. **`ORCH-P2-003` — the newest committed audit run fails the audit pack's own checker.** The 2026-10-23 run's `audit_manifest.json` lacks `pack`/`profile`/`findings`, and its statuses (`remediated-2026-11-02`, `closed 2026-11-03`, `owner-gated`, …) are outside the shared vocabulary. `tools/check_run.sh` returns FAIL (2 checks); the consumer lifecycle check passes, so the two validators disagree.
5. **`DOC-P2-003` — operator entry docs still route to Grafana at the public root and describe the old access model.** README labels the root as Grafana and says basic auth; `OPERATOR_START_HERE.md:10` starts operators at “Grafana — Command Center” on the root URL. Since 2026-10-21 the Console is at `/` and Grafana at `/grafana`; since 2026-11-05 Kestrel/Authelia + `falcon-sso` is the auth path.
6. **`TEST-P2-002` — the mTLS ingest migration left three plaintext HTTP validation paths.** `phase4_data_checks.sh`, `probe_pipeline_test.sh` and `phase7_security_checks.sh` still POST `http://vector-aggregator:6000/`; the listener now requires a client certificate, so the replay and DLQ checks cannot exercise the deployed ingress.

### P3

7. **`DOC-P3-002` — check-engine docs contradict the deployed waves.** `CHECK_ENGINE.md:18-22` says the SNMP wave is “staged but not built” while its own status table (`:405-409`) marks SNMP, P6b, P6c, P5c and P7a DONE; `CURRENT_STATE.md:67-68` still shows the 2026-10-14 15-pack state while the 2026-10-15 record says 35 packs.
8. **`DOC-P3-003` — policy/guide status text says proposed/unimplemented where controls are implemented.** `mct/VENDORING.md` still says “policy proposed / owner decision pending” and “P4 unimplemented” while :66-77 records the owner decision and implementation; `EVOLUTION_GUIDE.md` still calls the merge-safe apply a runtime follow-up; the console runbook says “no buttons that change anything” while documenting ack/unack.

## Finding index

| ID | Sev | Area | Status | Title |
|---|---|---|---|---|
| `ARCH-P1-001` | P1 | ARCH | owner-accepted | Single-host concentration: host loss is total pipeline loss |
| `EVOL-P1-001` | P1 | EVOL | partially-fixed | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| `EVOL-P1-002` | P1 | EVOL | verified-fixed | MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose |
| `ARCH-P2-002` | P2 | ARCH | owner-accepted | Vendored MCT tree remains tag-only under a blanket pin waiver; live stacks are tag@digest and lock-covered |
| `ARCH-P2-003` | P2 | ARCH | verified-fixed | Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing |
| `EVOL-P2-001` | P2 | EVOL | verified-fixed | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) |
| `FEAT-P2-001` | P2 | FEAT | verified-fixed | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |
| `DOC-P2-002` | P2 | DOC | partially-fixed | Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 94 vs 95 provisioned, firing proofs at 75/77, evolution-guide block at 2026-10-11 |
| `HYGIENE-P2-001` | P2 | HYGIENE | partially-fixed | Large generated SBOM/vulnerability JSON remains committed (56 files, 58.4 MB, up to 3.0 MB each) |
| `HYGIENE-P2-002` | P2 | HYGIENE | partially-fixed | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced |
| `HYGIENE-P2-003` | P2 | HYGIENE | verified-fixed | The publication flow force-tracks review-package/MANIFEST.sha256 while .gitignore, AGENTS.md, REPOSITORY.md and build_review_package.sh say the review package must not be committed; the file is load-bearing for the declared-commit gates |
| `INV-P2-001` | P2 | INV | open | Repository is majority generated/derived content; largest trees bound, audit records and mct/ remain unbound |
| `ORCH-P2-001` | P2 | ORCH | partially-fixed | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence |
| `ORCH-P2-002` | P2 | ORCH | partially-fixed | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable |
| `REL-P2-001` | P2 | REL | open | Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now clean at main HEAD |
| `REL-P2-002` | P2 | REL | verified-fixed | Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files and no gate compares them |
| `TEST-P2-001` | P2 | TEST | verified-fixed | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass |
| `ARCH-P3-001` | P3 | ARCH | verified-fixed | Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth |
| `ARCH-P3-002` | P3 | ARCH | verified-fixed | Container-level memory and policy-restart alerting for central services is still absent |
| `EVOL-P3-002` | P3 | EVOL | verified-fixed | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance |
| `FEAT-P3-001` | P3 | FEAT | regressed | Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-listener addition |
| `DOC-P2-001` | P3 | DOC | verified-fixed | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict |
| `DOC-P3-001` | P3 | DOC | verified-fixed | Imprecise version shorthand in the README vs the pinned versions |
| `HYGIENE-P3-001` | P3 | HYGIENE | verified-fixed | No root LICENSE/NOTICE file; README ownership section grants no terms |
| `INV-P3-001` | P3 | INV | open | Legacy host-absolute evidence paths require the resolver to resolve in a clone |
| `INV-P3-002` | P3 | INV | regressed | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries |
| `INV-P3-003` | P3 | INV | verified-fixed | 'A stale digest fails' is enforced by publication equality, not by the digest-binding check whose docstring claims it |
| `INV-P3-004` | P3 | INV | verified-fixed | Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-package manifest; no check binds it |
| `INV-P3-005` | P3 | INV | verified-fixed | HYG-P1-001 doctrine ('review-package is generated, gitignored, must not be committed') contradicts the tracked review-package/MANIFEST.sha256 |
| `ORCH-P3-001` | P3 | ORCH | verified-fixed | Run id does not start with the timestamp required by the consumer repo's lifecycle check |
| `ORCH-P3-002` | P3 | ORCH | open | Domain report and findings array disagree on a finding status inside the same 20261009 run artifact |
| `REL-P3-001` | P3 | REL | partially-fixed | No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented |
| `REL-P3-002` | P3 | REL | verified-fixed | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place |
| `REL-P3-003` | P3 | REL | partially-fixed | The delivered package embeds a closeout bound to the previous publication cycle while the digest declares the manifest commit; the equality gate reads the working tree only |
| `TEST-P3-001` | P3 | TEST | partially-fixed | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths |
| `TEST-P3-002` | P3 | TEST | open | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead |
| `DOC-P2-003` **NEW** | P2 | DOC | open | Operator entry docs still route to Grafana at the public root and describe basic auth after the Console/Kestrel cutover |
| `INV-P2-002` **NEW** | P2 | INV | open | The review pack omits the entire SBOM/vuln set but the package manifest lists it; pack fidelity still reports PASS with 51 unexplained entries |
| `INV-P2-003` **NEW** | P2 | INV | open | Review package omits the Falcon Console source and the root LICENSE/NOTICE/VERSION/CHANGELOG files |
| `ORCH-P2-003` **NEW** | P2 | ORCH | open | The newest committed audit run fails the audit pack's own run checker (manifest keys and status vocabulary) |
| `REL-P2-003` **NEW** | P2 | REL | open | Main is unbound and red after the Kestrel SSO merges: publication equality fails at db8c409 and the package still declares f79d786e |
| `TEST-P2-002` **NEW** | P2 | TEST | open | The mTLS ingest migration left three plaintext HTTP validation paths that can no longer exercise replay/DLQ ingress |
| `DOC-P3-002` **NEW** | P3 | DOC | open | Check-engine runbook status block contradicts its own phase table and the deployed 2026-10-15 waves |
| `DOC-P3-003` **NEW** | P3 | DOC | open | Policy/guide status text still says proposed/not implemented where the repository records implemented controls |

## Detailed findings

### ARCH

#### `ARCH-P1-001` (P1, owner-accepted)

**Single-host concentration: host loss is total pipeline loss**

Previous status: `owner-accepted`. 

All capture, storage, metrics, alerting and delivery still run on one Ubuntu 24.04 KVM host with no warm standby; host loss remains total monitoring loss (the edge buffers ~2 GiB, then blocks). No standby or tested RTO/RPO artifact was added in the 399 commits since edbf441.

Evidence:
- docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md:21 accepts OD-09/OD-10 (14-day retention, RPO 24 h, RTO <=1 h config / <=4 h data)
- docs/CURRENT_STATE.md:1-3 and README.md:6 still describe a single Ubuntu 24.04 KVM host; no warm-standby service/tree exists
- docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/RELEASE_GATE.md:22 lists single-host concentration as an inherited owner-gated risk

**Remediation:** Warm standby or a tested RTO/RPO acceptance artifact; the existing acceptance remains owner-gated.

**Verification note:** Carried unchanged. Owner-accepted (OD-09/OD-10); no standby commit between edbf441 and db8c409.

#### `ARCH-P2-002` (P2, owner-accepted)

**Vendored MCT tree remains tag-only under a blanket pin waiver; live stacks are tag@digest and lock-covered**

Previous status: `open`. 

First-party compose is fully digest-pinned (19/19 refs) and pins/images.lock has 25 entries, but the vendored mct/compose tree still carries 37 refs: 8 pinned / 29 unpinned / 12 floating. The blanket waivers remain root=mct/compose ref=* with review_by 2026-12-31. The 2026-10-15 owner decision explicitly accepts the 29 unpinned refs (pinning impossible for licensed/unavailable images) and makes the tree archive-only, backed by mct/compose/VENDOR_MANIFEST.sha256 and the vendor-drift gate; container_drift_check.sh no longer declares mct/compose.

Evidence:
- mct/compose/*.yml: 37 image refs, 8 digest-pinned, 29 unpinned, 12 floating (recounted at db8c409)
- pins/supply-chain-waivers.json:3-11 and :14-22: compose_digest + compose_pin waivers root=mct/compose ref=* review_by 2026-12-31
- mct/VENDORING.md:62-77 records the owner decision, archive-only boundary and P4 implementation
- ledgers/decision_log.md:316 (2026-10-15T00:11Z) records the archive-only decision and the accepted expiring waiver
- ci/validate.py:198 pin gate covers compose, mct/compose and automation/wazuh; :773-790 vendor-drift check
- automation/validation/container_drift_check.sh:150-152 no longer declares mct/compose

**Remediation:** Keep the archive-only boundary and expiry enforced; at the next import record the upstream commit and either digest-pin each staged ref or scope the waiver per ref. Remove the stale 'policy proposed / P4 unimplemented' status text (DOC-P3-003).

**Verification note:** Reclassified from open to owner-accepted: the residual unpinned refs are now an explicit, expiring owner waiver plus an archive-only control. The blanket ref:* waiver still means a revived mct/compose service would pass the pin gate without per-ref review; that residual is latent until 2026-12-31.

#### `ARCH-P2-003` (P2, verified-fixed)

**Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing**

Previous status: `open`. 

The edge->aggregator hop now uses mutual TLS plus HTTP basic as a second factor. The aggregator's edge_ingest source enables TLS with ca_file and verify_certificate: true; the probe sink presents CN=vector-edge-probe client material over https://vector-aggregator:6000. Certificates are generated by automation/validation/gen_ingest_certs.sh and mounted read-only into both containers. Evidence captures a handshake failure without a client certificate and success with one.

Evidence:
- config/vector/aggregator.yaml:17-35 (tls.enabled, crt/key/ca files, verify_certificate: true) and :36-39 (basic auth second factor)
- config/vector/edge.yaml:239-252 (https URI, client cert/key + CA, verify_certificate)
- compose/central/docker-compose.yml:153-159 and compose/probe/docker-compose.yml:61-67 mount the ingest material
- automation/validation/gen_ingest_certs.sh:1-58 generates the dedicated CA, server and client certificates
- evidence/raw/REVIEW-FIX/20261014T232947Z_ingest-mtls.out: handshake failure without a client certificate, success with it
- docs/architecture/PORT_PROTOCOL_MATRIX.md:27 (N-08) now documents mTLS + basic auth

**Remediation:** None for the auth mechanism. Update the live validation clients that still POST plain HTTP (TEST-P2-002).

**Verification note:** Fixed after edbf441 by the 2026-10-14 ingest-mTLS change; live evidence confirms rejection without a client certificate.

#### `ARCH-P3-001` (P3, verified-fixed)

**Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth**

Previous status: `verified-fixed`. 

The N-08 row now names mutual TLS + HTTP basic (second factor) and references ARCH-P2-003/API-P2-001; the separate 'shared secret header' wording is gone.

Evidence:
- docs/architecture/PORT_PROTOCOL_MATRIX.md:27

**Remediation:** None.

**Verification note:** Still correct after the mTLS change.

#### `ARCH-P3-002` (P3, verified-fixed)

**Container-level memory and policy-restart alerting for central services is still absent**

Previous status: `verified-fixed`. 

Container memory and restart rules remain provisioned in bootstrap/90-alerting.sh (falcon-container-mem-high, falcon-container-restarts), with container drift/unhealthy/stale rules alongside them.

Evidence:
- bootstrap/90-alerting.sh:711-718 (falcon-container-mem-high, falcon-container-restarts)
- bootstrap/90-alerting.sh:407-421 (container unhealthy/drift/stale rules)

**Remediation:** None.

**Verification note:** Rules and metrics unchanged; prior live proof at 2026-10-11 still applies.

### EVOL

#### `EVOL-P1-001` (P1, partially-fixed)

**Cross-repo shared tooling has drifted and still has no pin/hash enforcement**

Previous status: `partially-fixed`. 

The falcon half is enforced: automation/shared-tooling.lock lists 6 shared files, automation/validation/shared_tooling_check.sh verifies them, and ci/validate.py runs it (CI PASS). The cross-repo half is still missing: the edge repository (MaineCyberTech/falcon-edge, main 42e849a, 2026-11-03) has no automation/shared-tooling.lock and no shared_tooling_check.sh (GitHub contents API: 404 for both). Its capture.sh (sha256 1284e0ec..., lock expects 13a3bfe8...) now reads only the sudo key, but still records RC=${PIPESTATUS[0]} on the sudo path (line 93) and its redaction filter (line 52) still omits the falcon- ntfy topic. Its secret scanner remains a separate implementation. SHARED_TOOLING_POLICY.md:1-4 still says 'nothing implemented cross-repo'.

Evidence:
- automation/shared-tooling.lock:1-30 (6 files + sha256)
- automation/validation/shared_tooling_check.sh:1-30
- ci/validate.py:689-701 and :818 (shared-tooling check wired; CI log 2026-11-06: 'PASS shared tooling')
- GitHub contents API, MaineCyberTech/falcon-edge@42e849a: automation/shared-tooling.lock -> 404; automation/validation/shared_tooling_check.sh -> 404
- edge automation/evidence/capture.sh sha256 1284e0ec... vs locked 13a3bfe81a73...; line 93 RC=${PIPESTATUS[0]}; line 52 redaction lacks falcon- topics
- docs/architecture/SHARED_TOOLING_POLICY.md:1-4 still 'proposed ... nothing implemented cross-repo'

**Remediation:** Land the same lock + check in falcon-edge, adopt falcon's capture wrapper fixes (PIPESTATUS[1], falcon- topic redaction), and unify or cross-check the scanner pattern sets; refresh the policy status.

**Verification note:** Falcon side persists; edge side still absent at 2026-11-03. The edge wrapper has partially converged (single-key read) but the two named defects remain.

#### `EVOL-P1-002` (P1, verified-fixed)

**MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose**

Previous status: `verified-fixed`. 

Enforcement is in place: the pin gate covers compose, mct/compose and automation/wazuh with expiring waivers, ci/validate.py has a vendor-drift check over mct/compose/VENDOR_MANIFEST.sha256, and the owner decisions (E-2a/E-2b) are recorded. The upstream commit is still unrecorded, which is deferred to the next import by policy.

Evidence:
- ci/validate.py:198 (pin-gate roots include mct/compose), :773-790 (vendor-drift check), :816 (dispatcher)
- mct/compose/VENDOR_MANIFEST.sha256 (6 compose files, sha256 each)
- mct/VENDORING.md:71-77 (P4 decided and implemented 2026-10-15)
- ledgers/decision_log.md:316 (owner-approved archive-only + P4)
- CI log 2026-11-06: PASS vendor drift; PASS compose image pinning (waivers active)

**Remediation:** Record the upstream commit at the next import. Fix the stale status header/§5/§7 text (DOC-P3-003).

**Verification note:** Enforcement leg remains fixed; residual is documentation/status text and the future import pin.

#### `EVOL-P2-001` (P2, verified-fixed)

**The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending)**

Previous status: `verified-fixed`. 

The merge-safe carry-over is still implemented: before the securityadmin apply, bootstrap/60 reads the live internal-user set, appends undeclared users (with hashes/roles) to the temporary internal_users.yml, and only then applies it. The residual is test coverage (no undeclared-user fixture) and stale guide text.

Evidence:
- bootstrap/60-central-deploy.sh:209-241 (carry-over of undeclared internal users before the apply)
- bootstrap/60-central-deploy.sh:241-243 (securityadmin apply)
- docs/architecture/EVOLUTION_GUIDE.md:317-326 still says the merge-safe follow-up is 'not done here'

**Remediation:** Add an undeclared-user regression fixture and refresh EVOLUTION_GUIDE §8 (DOC-P3-003).

**Verification note:** Implementation persists; no regression. Residual docs/test only.

#### `EVOL-P3-002` (P3, verified-fixed)

**No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance**

Previous status: `verified-fixed`. 

The additive-deploy substitute remains documented in EVOLUTION_GUIDE §9 and the owner acceptance is recorded in the decision log.

Evidence:
- ledgers/decision_log.md:271 records 'EVOL-P3-002 additive-deploy substitute accepted'
- docs/architecture/EVOLUTION_GUIDE.md:346-362 (§9 additive deploy + staged rollout + idempotent rollback)

**Remediation:** None; optionally mark the backlog row as accepted.

**Verification note:** Acceptance persists; backlog table still omits the marker (minor).

### FEAT

#### `FEAT-P2-001` (P2, verified-fixed)

**Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only**

Previous status: `open`. 

The archive-only policy is now enforced at the two places the finding named: container_drift_check.sh no longer declares mct/compose as a deployable root, and a committed vendor manifest + vendor-drift gate makes silent edits visible. The policy and the prior run state that no mct/compose container is live (this pass did not re-measure the live container set); the tree remains staged.

Evidence:
- automation/validation/container_drift_check.sh:150-152 (DECLARED_ROOTS excludes mct/compose; comment cites FEAT-P2-001)
- mct/VENDORING.md:62-77 (archive-only boundary; P4 manifest/drift gate)
- ci/validate.py:773-790 (vendor-drift fails on an edited mct/compose file)
- ledgers/decision_log.md:316 (archive-only decision)

**Remediation:** None for the latent path; keep the archive-only declaration if a staged service is ever revived.

**Verification note:** Both named controls are now in place; previously open only because DECLARED_ROOTS still listed mct/compose.

#### `FEAT-P3-001` (P3, regressed)

**Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-listener addition**

Previous status: `verified-fixed`. 

The same one-rule class has recurred. bootstrap/90-alerting.sh now has 95 write_rule UIDs (including falcon-edge-spool-unretained at line 636, added 2026-10-14), while docs/phase9/ALERT_CATALOGUE.yaml has 94 ids and README.md:33 / docs/CURRENT_STATE.md:169 still say 94. The catalogue was last regenerated 2026-10-13 (commit 73f2d8ea) before the new rule; README's drift test compares README to the catalogue only, so the source->catalogue gap passes.

Evidence:
- bootstrap/90-alerting.sh:636 (falcon-edge-spool-unretained; 95 write_rule total)
- docs/phase9/ALERT_CATALOGUE.yaml:2-5, 94 ids; last catalogue commit 73f2d8ea 2026-10-13
- README.md:33 '94 alert rules'; docs/CURRENT_STATE.md:169 '94 rules live'
- automation/validation/tests/readme_ledger_drift_test.sh:62-84 compares README only to ALERT_CATALOGUE.yaml
- automation/validation/tests/alert_rule_lint_test.sh:1-12 parses the source only; no catalogue comparison

**Remediation:** Regenerate the catalogue from the source/live set, update README/CURRENT_STATE, and add a source<->catalogue id-set check to alert_rule_lint_test.sh so it fails closed.

**Verification note:** Regression of the previously closed one-rule drift: 95 source vs 94 catalogue/README; the exact static-check gap the prior finding asked for is still absent.

### DOC

#### `DOC-P2-002` (P2, partially-fixed)

**Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 94 vs 95 provisioned, firing proofs at 75/77, evolution-guide block at 2026-10-11**

Previous status: `partially-fixed`. 

The catalogue was regenerated at 94 on 2026-10-13, but bootstrap/90-alerting.sh now has 95 write_rule UIDs (falcon-edge-spool-unretained added 2026-10-14). ALERT_CATALOGUE.yaml has 94 ids, README.md:33 and CURRENT_STATE.md:169 say 94, while the source has 95. ALERT_FIRING_PROOFS.md:21 still says 75 of 77 (and line 475/482 says the live set is 93). EVOLUTION_GUIDE.md §7 is still a 2026-10-11 snapshot. The README drift test compares README to the catalogue only, so the source gap is invisible.

Evidence:
- bootstrap/90-alerting.sh:636 (falcon-edge-spool-unretained; 95 write_rule calls)
- docs/phase9/ALERT_CATALOGUE.yaml:1-5 (94 ids; header claims it is generated from live and cannot drift)
- README.md:33 (94); docs/CURRENT_STATE.md:169 (94)
- docs/phase9/ALERT_FIRING_PROOFS.md:21 (75 of 77), :475, :482 (live set stated as 93)
- docs/architecture/EVOLUTION_GUIDE.md:274-284 ('Current state ... 2026-10-11')
- automation/validation/tests/readme_ledger_drift_test.sh:62-84 (README<->catalogue only)

**Remediation:** Regenerate catalogue + firing proofs from the 95-rule set; refresh README/CURRENT_STATE/EVOLUTION_GUIDE; add a source<->catalogue equality check.

**Verification note:** Still partial: the drift-test mechanism exists but compares the wrong pair; the count regression is also FEAT-P3-001.

#### `DOC-P2-003` (P2, open) — **NEW**

**Operator entry docs still route to Grafana at the public root and describe basic auth after the Console/Kestrel cutover**

The Console cutover on 2026-10-21 moved the Falcon Console to https://falcon.mainecybertech.us/ and Grafana to /grafana; Kestrel/Authelia replaced the old access model on 2026-11-05. README and the operator start page were not updated: README.md:35 still says 'Access | Traefik ... basic auth for ntopng', README.md:96-97 still labels the public root as Grafana, and OPERATOR_START_HERE.md:10 tells operators to start at 'Grafana - Command Center' on the root URL. The access runbook and console runbook have the correct model, so the documents now contradict each other.

Evidence:
- README.md:35 (access row says basic auth for ntopng; omits Kestrel/Authelia and falcon-sso)
- README.md:96-97 ('falcon.mainecybertech.us (Grafana, /dash, /ntop)')
- docs/runbooks/OPERATOR_START_HERE.md:10 (Grafana Command Center at https://falcon.mainecybertech.us/) vs :37-42 (Kestrel/Authelia forward-auth)
- docs/runbooks/CONSOLE_PHASE0.md:3-5 (Console live at /, Grafana at /grafana since 2026-10-21)
- docs/design/FALCON_CONSOLE.md:1081 (D1 executed: console at /, Grafana at /grafana)
- docs/runbooks/ACCESS_AND_ACCOUNTS.md:11-13 (Kestrel/Authelia + falcon-sso for Grafana/OSD/ntop)

**Remediation:** Update README's product map/access row/hostnames and the operator start page to the Console-at-root + Kestrel model; add a link to CONSOLE_PHASE0/SSO.

**Verification note:** New P2. The 2026-10-23 audit closed its own DOC-P2-001 ('refresh CURRENT_STATE and operator auth runbooks') on 2026-11-03, but these entry docs remain wrong.

#### `DOC-P2-001` (P3, verified-fixed)

**Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict**

Previous status: `verified-fixed`. 

verify_delivery.sh still runs pack_fidelity.py fail-closed on content mismatches; PACK_VERIFICATION_NOTES.txt now opens with a verdict line, and the verification doc records the wiring as implemented.

Evidence:
- automation/validation/verify_delivery.sh:42-50 (pack_fidelity called; nonzero increments delivery failures)
- PACK_VERIFICATION_NOTES.txt:1-3 (verdict header)
- docs/security/RELEASE_PACK_VERIFICATION.md:81-84 ('implemented ... notes file now carries a verdict header')

**Remediation:** None for the wiring; the missing-entry class is tracked as INV-P2-002.

**Verification note:** Wiring persists. Caveat: pack_fidelity returns 0 when entries are merely absent from the pack, so 'unexpected' omissions do not fail the archive (new INV-P2-002).

#### `DOC-P3-001` (P3, verified-fixed)

**Imprecise version shorthand in the README vs the pinned versions**

Previous status: `verified-fixed`. 

README still states exact pinned versions: Suricata 8.0.7 and OpenSearch 2.19.6.

Evidence:
- README.md:30 (Suricata 8.0.7); README.md:32 (OpenSearch 2.19.6)
- pins/images.lock (jasonish/suricata:8.0.7, opensearchproject/opensearch:2.19.6)

**Remediation:** None.

**Verification note:** Unchanged and still exact.

#### `DOC-P3-002` (P3, open) — **NEW**

**Check-engine runbook status block contradicts its own phase table and the deployed 2026-10-15 waves**

CHECK_ENGINE.md:18-22 says only P1/P2/P3/P4a/P5a/P5b/P6a are implemented and that the SNMP wave is 'staged but not built', while the same file's status table at :405-409 records SNMP, P6b, P6c, P5c and P7a as DONE (2026-10-14/15). The file list at :64-80 omits the new pack files (03-snmp, 07-time, 08-node, 09-topology, 10-ups) and actions. CURRENT_STATE.md:67-68 still says 220 checks / 46 assets / 15 pack rules (2026-10-14), while the 2026-10-15 deploy record says 35 packs upserted and config/checks now has 12 pack YAMLs.

Evidence:
- docs/runbooks/CHECK_ENGINE.md:18-22 (SNMP staged/not built) vs :405-409 (SNMP/P6b/P6c/P5c/P7a DONE)
- docs/runbooks/CHECK_ENGINE.md:64-80 (file table omits 03-snmp/07-time/08-node/09-topology/10-ups and actions)
- docs/CURRENT_STATE.md:67-68 (220 checks, 46 assets, 15 pack rules; 2026-10-14)
- ledgers/decision_log.md:325 (2026-10-15: 35 packs upserted; topology probe; availability delivery)
- config/checks/: 12 YAML pack files including 03-snmp.yaml, 07-time.yaml, 08-node.yaml, 09-topology.yaml, 10-ups.yaml

**Remediation:** Refresh the status block and file table to the P7a state, and update CURRENT_STATE's check-engine counts/waves from the ledgers.

**Verification note:** New P3. Documentation truth for the newest product surface; no runtime defect observed.

#### `DOC-P3-003` (P3, open) — **NEW**

**Policy/guide status text still says proposed/not implemented where the repository records implemented controls**

mct/VENDORING.md:3 still says 'policy proposed 2026-10-01; owner decision pending', :96 is headed 'Manual checks while P4 is unimplemented', and :127 says 'policy proposed; pin enforcement ... not yet implemented', while :66-77 records the 2026-10-15 owner decision and P4 implementation. EVOLUTION_GUIDE.md:293-294 still calls MCT pin enforcement proposed and the merge-safe apply a 'runtime follow-up', while :317-324 says the follow-up is not done, although bootstrap/60 implements it. The console runbook also says 'There are no buttons that change anything' (:39) while :33-34 documents ack/unack through the actions broker.

Evidence:
- mct/VENDORING.md:3 vs :66-77 (owner decision + P4 implemented), :96, :127
- docs/architecture/EVOLUTION_GUIDE.md:293-294, :317-326 vs bootstrap/60-central-deploy.sh:209-241
- docs/runbooks/CONSOLE_PHASE0.md:33-34 (ack/unack) vs :39 ('no buttons that change anything')

**Remediation:** Update the status headers/backlog rows to the implemented state and qualify the console read-only statement (read-only data, explicit role-gated ack/unack actions).

**Verification note:** New P3. Same class as DOC-P2-002 but on policy/guide pages rather than status pages.

### HYGIENE

#### `HYGIENE-P2-001` (P2, partially-fixed)

**Large generated SBOM/vulnerability JSON remains committed (56 files, 58.4 MB, up to 3.0 MB each)**

Previous status: `open`. 

The committed SBOM/vuln set has grown from 42 files / 29.6 MB to 56 files / 58,397,686 bytes (56 MB), including 26 vulnerability JSONs (~39 MB); the largest file is still opensearchproject_opensearch-dashboards_2.19.6.cdx.json at 3,064,465 B. A 60-day sbom-freshness gate now exists (last manifest change 22 days old in the 2026-11-06 CI run), but nothing moves or compresses the payload, and the review package now ships the SBOM set (owner decision D2, 2026-10-15).

Evidence:
- sbom/: 56 tracked files, 58,397,686 bytes; sbom/vuln: 26 files, ~39 MB; largest 3,064,465 B
- ci/validate.py:666-686 (sbom-freshness, SBOM_MAX_AGE_DAYS=60); CI 2026-11-06: 'PASS sbom freshness (manifest 22d <= 60d)'
- docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:158-160 (freshness gate implemented 2026-10-15)
- automation/validation/build_review_package.sh:51-53 (SBOM set ships in the review package, D2 option (a))

**Remediation:** Move the SBOM/vuln payload to release-artifact storage or compress it, or record a dated owner acceptance of the committed size; keep the freshness gate.

**Verification note:** Freshness leg fixed; the size leg worsened by ~28.8 MB since edbf441. The payload is now also delivered in the review package.

#### `HYGIENE-P2-002` (P2, partially-fixed)

**Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced**

Previous status: `partially-fixed`. 

docs/RELEASE_GATE.md:15-17 still names the 2026-10-11 full run and the 2026-10-14 post-merge verification as 'current'; :51 still heads the current audit opinion with the 2026-10-03 run (20b5e57) and its P0 x1/P1 x7 roll-up. The newer in-repo 2026-10-23 deep-dive (P0 x0, GO WITH CONDITIONS, NO-GO clean rebuild) is referenced only in docs/CURRENT_STATE.md:36, not on the gate page or README. README.md:8-12 still says 'Current state (2026-10-14)'.

Evidence:
- docs/RELEASE_GATE.md:15-17 (newest runs pointer stops at 2026-10-11/2026-10-14)
- docs/RELEASE_GATE.md:51-58 ('Current audit opinion (run 20261003-0018..., commit 20b5e57)')
- docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/RELEASE_GATE.md:1-13 (P0 0; GO WITH CONDITIONS; NO-GO clean rebuild)
- docs/CURRENT_STATE.md:36 (only reference to the 20261023 audit); README.md:8-12 (2026-10-14)

**Remediation:** Point the current-opinion section at the 2026-10-23 run (with its remediation update) and refresh README's current-state block; add a doc-drift test that compares the gate's 'current' pointer to the newest run folder.

**Verification note:** Still partial: a newer audit is now published but the canonical gate page was not refreshed.

#### `HYGIENE-P2-003` (P2, verified-fixed)

**The publication flow force-tracks review-package/MANIFEST.sha256 while .gitignore, AGENTS.md, REPOSITORY.md and build_review_package.sh say the review package must not be committed; the file is load-bearing for the declared-commit gates**

Previous status: `verified-fixed`. 

The doctrine now documents the single force-added manifest as the declared-commit anchor, and the tracked file remains the publication anchor. The residual fail-open is unchanged: check_publication_equality.py skips the ancestry restriction when review-package/ is absent.

Evidence:
- .gitignore:24-29; AGENTS.md:61-62; REPOSITORY.md:33,54; automation/validation/build_review_package.sh:9-14
- git ls-files review-package/ -> review-package/MANIFEST.sha256
- automation/validation/check_publication_equality.py:213-214 (skip when the manifest is absent)

**Remediation:** Add a test that the declared-commit binding cannot be skipped silently (residual).

**Verification note:** Doctrine fix persists; absent-manifest skip remains fail-open and untested.

#### `HYGIENE-P3-001` (P3, verified-fixed)

**No root LICENSE/NOTICE file; README ownership section grants no terms**

Previous status: `verified-fixed`. 

LICENSE (GPLv2) and NOTICE are tracked, and the README ownership section now links both.

Evidence:
- LICENSE (15,174 B) and NOTICE (995 B) tracked at db8c409
- README.md:127-131 (License / ownership links LICENSE and NOTICE)

**Remediation:** None.

**Verification note:** Links added since the prior run; no residual.

### INV

#### `INV-P2-001` (P2, open)

**Repository is majority generated/derived content; largest trees bound, audit records and mct/ remain unbound**

Previous status: `open`. 

At db8c409 the tree is 4,433 files / 88 MB; evidence/ is 2,619 files / 16 MB and sbom/ is 56 files / 56 MB, i.e. ~60% of files and ~82% of bytes are generated. evidence/MANIFEST.sha256 and sbom/SBOM_MANIFEST.sha256 bind those two trees, but check_generated_drift.py's DEFAULT_MANIFESTS is still only evidence/MANIFEST.sha256; docs/audits/ has only a structural lifecycle check; mct/ has a manifest only for mct/compose (not the other ~800 files); PACKAGE_MANIFEST is a copy bound by the publication chain.

Evidence:
- git ls-files: 4,433 files; du -sh . (excluding .git): 88 MB
- evidence/: 2,619 files / 16 MB; sbom/: 56 files / 56 MB
- automation/validation/check_generated_drift.py:37 (DEFAULT_MANIFESTS = ('evidence/MANIFEST.sha256',))
- docs/audits/: 218 files / 2.9 MB; lifecycle check only (automation/validation/audit_run_lifecycle.sh)
- mct/: 858 files / 4.1 MB; mct/compose/VENDOR_MANIFEST.sha256 covers only the 6/7 compose files

**Remediation:** Bind the committed run folders and the whole mct/ import (or a declared subset) to manifests; consider moving sbom/ to release storage (HYGIENE-P2-001).

**Verification note:** No change to the generated-majority ratio; the binding gap for docs/audits and most of mct/ persists.

#### `INV-P2-002` (P2, open) — **NEW**

**The review pack omits the entire SBOM/vuln set but the package manifest lists it; pack fidelity still reports PASS with 51 unexplained entries**

The review package now ships sbom/ (owner decision D2, 2026-10-15), so review-package/MANIFEST.sha256 contains 56 sbom files. make-repomix.sh still excludes sbom/*.cdx.json and sbom/vuln/** from the repomix pack. pack_fidelity.py therefore writes 51 'not-in-pack (unexpected; investigate)' rows, but returns 0 because it only fails on content mismatches, and verify_delivery.sh treats that as pack_fidelity_verdict=PASS. A pack-only reviewer cannot see the SBOM/vuln set the manifest claims, and the unresolved rows are not surfaced as a failure.

Evidence:
- automation/validation/make-repomix.sh:19-22 (ignore includes sbom/*.cdx.json and sbom/vuln/**)
- automation/validation/pack_fidelity.py:95-110 (writes 'unexpected; investigate'), :112-117 (returns 0 unless content mismatch)
- PACK_NOT_INCLUDED.txt:5-55 (51 sbom entries 'not-in-pack (unexpected; investigate)')
- automation/validation/verify_delivery.sh:42-50 (PASS from pack_fidelity return code; no not-in-pack assertion)
- automation/validation/build_review_package.sh:51-53 (sbom set ships in the package since 2026-10-15)
- PACK_NOT_INCLUDED.txt last changed 2026-10-15 (commit a0ac9003), so the artifact is stale across the later publication cycles

**Remediation:** Add the sbom ignore patterns to KNOWN_PACK_EXCLUSIONS (or include sbom in the pack), fail on any 'unexpected' not-in-pack entry, and regenerate PACK_NOT_INCLUDED.txt in verify_delivery.sh. If the pack intentionally cannot carry 56 MB of SBOM, record that as a dated disposition and keep the package manifest authoritative.

**Verification note:** New P2. Distinct from INV-P3-002 (the artifact regression): this is the systemic mismatch + fail-open gate introduced when SBOMs started shipping in the package.

#### `INV-P2-003` (P2, open) — **NEW**

**Review package omits the Falcon Console source and the root LICENSE/NOTICE/VERSION/CHANGELOG files**

build_review_package.sh copies only docs ledgers closeout compose config bootstrap automation ci pins mct sbom plus evidence and three root files (REPOSITORY.md, README.md, AGENTS.md). Two omissions follow. (1) The Falcon Console (console/, 19 tracked files including auth.py, sso_gateway.py, api/server.py, actions_broker.py and tests) is now the product's root UI/API but is never copied; PACKAGE_MANIFEST.sha256 has zero './console/' entries (the only console matches are ./automation/console/resolve_sources.sh and ./config/console/roles.yaml). (2) The root LICENSE, NOTICE, VERSION, CHANGELOG.md and TESTING.md files are also absent from the manifest. A reviewer receiving the declared package cannot inspect or rebuild the console and does not receive the GPLv2 license text or the third-party NOTICE that the repository now advertises.

Evidence:
- automation/validation/build_review_package.sh:34-39 (copy list: docs ledgers closeout compose config bootstrap automation ci pins mct sbom; root files only REPOSITORY.md/README.md/AGENTS.md)
- git ls-files console -> 19 files, including console/auth.py, console/sso_gateway.py, console/api/server.py, console/actions_broker.py and console/tests/
- PACKAGE_MANIFEST.sha256: 0 entries matching ' ./console/'; only ./automation/console/resolve_sources.sh and ./config/console/roles.yaml
- PACKAGE_MANIFEST.sha256: 0 entries for ./LICENSE, ./NOTICE, ./VERSION, ./CHANGELOG.md, ./TESTING.md, although README.md:127-131 advertises LICENSE/NOTICE
- docs/runbooks/CONSOLE_PHASE0.md:3-5 (Console is live at the public root since 2026-10-21)

**Remediation:** Add console/ and the root LICENSE/NOTICE/VERSION/CHANGELOG/TESTING files to the package copy list, rebuild the review package/manifest/digest, and add a gate that every tracked first-party top-level source file/directory is represented in the package manifest (allowlist the generated/delivery dirs explicitly).

**Verification note:** New P2. This is a package-completeness gap, not a repomix-pack omission: the pack includes console/, the formal review package does not; the missing LICENSE/NOTICE also undermines the HYGIENE-P3-001 closure for the delivered artifact.

#### `INV-P3-001` (P3, open)

**Legacy host-absolute evidence paths require the resolver to resolve in a clone**

Previous status: `open`. 

check_evidence_index.py still skips 264 legacy '../monitoring-build/...' rows instead of resolving them; at db8c409 it reports 1,302 metas/rows, 1,031 host-absolute resolved, 264 legacy skipped. New captures now reference in-repo artifacts (7 verified), but the legacy class is unchanged.

Evidence:
- automation/validation/check_evidence_index.py:112-130, :162-164 (legacy rows counted and skipped)
- local run: PASS evidence_index (1302 metas, 1302 rows, 1031 host-absolute resolved, 264 legacy skipped)
- REPOSITORY.md:63-74 documents the resolver, but it is not applied centrally

**Remediation:** Resolve legacy rows centrally (resolve-then-check) or rewrite the index paths in an append-only migration.

**Verification note:** 264 skipped is unchanged since edbf441.

#### `INV-P3-002` (P3, regressed)

**Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries**

Previous status: `regressed`. 

The class has grown from two entries to 51. PACK_NOT_INCLUDED.txt:4 keeps the known ANSI-capture entry, and :5-55 list 51 sbom/*.cdx.json and sbom/vuln/*.json files as 'not-in-pack (unexpected; investigate)'. The files exist in the tree and in the review-package manifest; make-repomix.sh explicitly excludes them, but pack_fidelity.py does not know that, and it returns 0 as long as content mismatches are zero, so the delivery verdict still says PASS.

Evidence:
- PACK_NOT_INCLUDED.txt:4 (known ANSI capture), :5-55 (51 sbom entries 'unexpected; investigate')
- automation/validation/make-repomix.sh:19-22 (ignore='review-package/**,sbom/*.cdx.json,sbom/vuln/**,...')
- automation/validation/pack_fidelity.py:95-110 (writes 'unexpected; investigate') and :117 (returns 0 unless content mismatches)
- automation/validation/verify_delivery.sh:42-50 (PASS is based on that return code)
- PACK_NOT_INCLUDED.txt last changed 2026-10-15 (commit a0ac9003); 51 unresolved entries persist at db8c409

**Remediation:** Teach pack_fidelity.py the sbom exclusion as a known disposition (or include sbom in the pack), fail on unexpected not-in-pack entries, and regenerate PACK_NOT_INCLUDED.txt each delivery.

**Verification note:** Regression: 2 -> 51 unresolved entries; the fidelity verdict is fail-open for absent entries. New systemic finding is INV-P2-002.

#### `INV-P3-003` (P3, verified-fixed)

**'A stale digest fails' is enforced by publication equality, not by the digest-binding check whose docstring claims it**

Previous status: `open`. 

The wording is corrected: check_digest_binding.py now says it binds the shipped manifests and explicitly delegates freshness/ancestry to check_publication_equality.py; ci/validate.py's digest-binding docstring says the same.

Evidence:
- automation/validation/check_digest_binding.py:8-14
- ci/validate.py:555-565 (freshness/ancestry delegated to check_publication_equality.py)

**Remediation:** None.

**Verification note:** Docstring/claim corrected since edbf441.

#### `INV-P3-004` (P3, verified-fixed)

**Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-package manifest; no check binds it**

Previous status: `verified-fixed`. 

PACKAGE_MANIFEST.sha256 and review-package/MANIFEST.sha256 are byte-identical at db8c409 (both sha256 fd9ee76a..., 4,394 entries), and publish_digests.sh still copies the shipped manifest into the published copy on every bind.

Evidence:
- sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256 -> fd9ee76a... for both; wc -l -> 4,394 each
- automation/validation/publish_digests.sh:15-20 (copy-on-bind)
- automation/validation/check_publication_equality.py: manifest/hash equality checks pass

**Remediation:** None; consider a standalone equality assertion for the published copy (residual).

**Verification note:** Equality persists; the only equality-gate failure is the ancestry rule after the Kestrel commits (REL-P2-003).

#### `INV-P3-005` (P3, verified-fixed)

**HYG-P1-001 doctrine ('review-package is generated, gitignored, must not be committed') contradicts the tracked review-package/MANIFEST.sha256**

Previous status: `verified-fixed`. 

The declared-manifest exception is now documented in EVOLUTION_GUIDE step 7 as well as .gitignore/AGENTS.md/REPOSITORY.md/build_review_package.sh.

Evidence:
- docs/architecture/EVOLUTION_GUIDE.md:93 (declared-manifest exception in step 7)
- .gitignore:24-29; AGENTS.md:61-62; REPOSITORY.md:33,54; automation/validation/build_review_package.sh:9-14

**Remediation:** None.

**Verification note:** Doctrine now consistent; no residual on this item.

### ORCH

#### `ORCH-P2-001` (P2, partially-fixed)

**Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence**

Previous status: `open`. 

The 2026-10-05 record is still internally wrong: RELEASE_GATE.md says 'GO WITH CONDITIONS' with P0 x1/P1 x7 while the shared rule makes any P0 NO-GO; findings.json keeps all 34 findings open and the profile is 'focused-security-supply-chain-ci' with no per-domain reports; no dated reconciliation note exists. A newer 2026-10-23 deep-dive gate (P0 x0) is now published in docs/audits/, so the repository no longer ends at the P0-bearing record, but the newest full-domain in-repo record is still this 2026-10-05 run.

Evidence:
- docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md:3-5 ('GO WITH CONDITIONS', P0 x1, P1 x7)
- docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/findings.json (34 findings, all status open; counts P0 1/P1 7)
- docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/audit_manifest.json: profile focused-security-supply-chain-ci, no per-domain reports
- no reconciliation/superseded note in the folder (grep empty)
- docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/RELEASE_GATE.md (newer P0 x0 focused run)
- ci/validate.py has no docs/audits publish gate for P0-bearing run verdicts

**Remediation:** Append a dated reconciliation note to the 2026-10-05 folder (never rewrite it) and add a publish-time check that a P0-bearing run cannot emit GO/GO WITH CONDITIONS while unresolved.

**Verification note:** Partially fixed: a newer focused run is published, but the wrong 2026-10-05 record and the missing publish gate remain.

#### `ORCH-P2-002` (P2, partially-fixed)

**full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable**

Previous status: `partially-fixed`. 

The pack driver now accepts --profile and records the label, but the manifest still emits 'lenses': [d['area'] for d in domains] (43 area codes) and no lens ids/targets/status/waves. tools/check_run.sh only requires the five falcon-lab extra reports when profile == 'falcon-lab'; the newest falcon manifests are still profile=base, promptCount=42, lenses=43.

Evidence:
- tools/full_domain.py:200-225 (manifest_for; 'lenses': [d['area'] for d in domains] at :224)
- tools/full_domain.py:718-721 (--profile option, default base)
- tools/check_run.sh:41-52 (falcon-lab extras gated on profile)
- /root/repo-deep-dive/runs/falcon-20261011-0416-full-f5cb7c9, falcon-20261012-verify-main-3623d2e, falcon-20261014-verify-main-edbf441 audit_manifest.json: profile base, promptCount 42, lenses 43

**Remediation:** Emit the falcon-lab manifest shape (lens ids/targets/status, waves, prompt status) and validate it; or record an explicit, documented scope reduction in every run.

**Verification note:** Profile label added; the manifest shape and validation remain base-only.

#### `ORCH-P2-003` (P2, open) — **NEW**

**The newest committed audit run fails the audit pack's own run checker (manifest keys and status vocabulary)**

docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/ is the newest durable audit record, but its audit_manifest.json has no pack/profile/findings keys (only run/generated/repository/.../counts), and its findings/register statuses use free text ('remediated-2026-11-02', 'closed 2026-11-03', 'partially-remediated-2026-11-03', 'owner-gated') outside the shared vocabulary. tools/check_run.sh reports 'missing keys: pack,profile,findings' and 'unknown finding status values', so the run cannot be machine-diffed or CSV-exported like the others.

Evidence:
- docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/audit_manifest.json:1-40 (no pack/profile/findings keys; scope is an array)
- docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/follow_up_register.md:5-17 (closed/remediated/owner-gated text)
- docs/audits/repo-deep-dive/20261023-1725-repo-deepdive-main-cdc1910/findings.json (statuses remediated-2026-11-02, partially-remediated-2026-11-03)
- tools/check_run.sh (pack validator) -> 'missing keys: pack,profile,findings', 'unknown finding status values ...', RESULT: FAIL (2 checks)
- automation/validation/audit_run_lifecycle.sh:120-141 passes the same folder (structure/id only), so the two validators disagree

**Remediation:** Re-publish the 20261023 record in the shared manifest/status shape (pack/profile/findings, allowed status vocabulary), or extend the pack checker with an explicit focused-run schema; add the pack check to the publish flow.

**Verification note:** New P2. The consumer lifecycle check passes, but the producer's check_run.sh fails, so downstream diff/register tooling cannot consume the newest run faithfully.

#### `ORCH-P3-001` (P3, verified-fixed)

**Run id does not start with the timestamp required by the consumer repo's lifecycle check**

Previous status: `verified-fixed`. 

The consumer lifecycle regex still accepts an optional repo prefix before the timestamp, and the current run id passes.

Evidence:
- automation/validation/audit_run_lifecycle.sh:120-124 (optional repo prefix; ^([a-z0-9][a-z0-9-]*-)?[0-9]{8}-[0-9]{4}-)
- local run: check_failures=0 for all 7 committed run folders

**Remediation:** None.

**Verification note:** Unchanged and still passing.

#### `ORCH-P3-002` (P3, open)

**Domain report and findings array disagree on a finding status inside the same 20261009 run artifact**

Previous status: `open`. 

The 2026-10-09 domain report still says 'ARCH-P2-001 ... (verified fixed)' with 'Status: verified-fixed', while the same file's findings array and both follow-up registers record ARCH-P2-001 as open. No dated reconciliation note exists and tools/check_run.sh still has no report-vs-array cross-check.

Evidence:
- /root/repo-deep-dive/runs/falcon-20261009-2117-full-08e20d1/_domains/02_architecture_runtime_topology.json: report says verified-fixed; findings array status open
- /root/repo-deep-dive/runs/falcon-20261009-2117-full-08e20d1/findings.json: ARCH-P2-001 status open
- tools/check_run.sh: no report-vs-findings-array status cross-check

**Remediation:** Append a dated reconciliation note and add the report-vs-array cross-check to check_run.sh.

**Verification note:** Unchanged since edbf441.

### REL

#### `REL-P2-001` (P2, open)

**Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now clean at main HEAD**

Previous status: `open`. 

VERSION remains 2026.10.11 and the only tag is v2026.10.11 (dff362c0ec), now 489 commits behind db8c409. No deploy manifest or deployed-commit record exists (grep docs/ledgers -> none). Deployment identity is still a mutable branch HEAD; the publication digest binds the package at f79d786e, not the deployment.

Evidence:
- VERSION: 2026.10.11
- GitHub tags API: only v2026.10.11 (tag dff362c0ec); compare dff362c..db8c409 ahead_by=489
- docs/security/BRANCH_PROTECTION.md:59 says 'releases are tags on main'; no new tag
- no deploy manifest / deployed-commit record in docs/, ledgers/, REPOSITORY.md, README.md (grep)
- PACKAGE_DIGEST.txt:2-4 declares package commit f79d786e (2026-11-03), not a deployment identity

**Remediation:** Record the deployed commit per deploy (deploy manifest or decision-log entry) and tag releases at the delivered commit; bump VERSION.

**Verification note:** Still open; tag lag grew from 90 to 489 commits since edbf441.

#### `REL-P2-002` (P2, verified-fixed)

**Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files and no gate compares them**

Previous status: `verified-fixed`. 

The published and shipped manifests are still byte-identical (fd9ee76a..., 4,394 entries), and publish_digests.sh copies the shipped manifest on every bind.

Evidence:
- sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256: both fd9ee76a...
- automation/validation/publish_digests.sh:15-20
- automation/validation/check_publication_equality.py: review_package_manifest_sha256/entries checks pass

**Remediation:** None; optionally add a standalone equality assertion.

**Verification note:** Equality persists; the manifest itself is not the cause of the current publication-equality failure (REL-P2-003).

#### `REL-P2-003` (P2, open) — **NEW**

**Main is unbound and red after the Kestrel SSO merges: publication equality fails at db8c409 and the package still declares f79d786e**

PACKAGE_DIGEST.txt declares repository/closeout/delivered commit f79d786e (2026-11-03). Seven commits have landed since, including security/SSO changes (6c923cd8, 93a31cc6, merge ba4bf8b4/db8c409). The repository validate workflow on the db8c409 push failed (run 42164078378, 2026-11-06): 'FAIL publication equality ... commits after the declared commit touch only publication/test files (93a31cc6:config/traefik/dynamic.yml; 93a31cc6:console/sso_gateway.py; ... 6c923cd8:bootstrap/98-console.sh; ...)'. The topic-branch allowance only applies to pull_request events, so PR CI can be green while main stays red until a rebind; no rebind followed the merges. The delivered package therefore predates the Kestrel SSO cutover.

Evidence:
- PACKAGE_DIGEST.txt:2-4 (repository_commit=CLOSEOUT_SOURCE_COMMIT=DELIVERED_PACKAGE_COMMIT=f79d786e...)
- git rev-list --count f79d786e..db8c409 -> 7 commits, including 6c923cd8 and 93a31cc6 (Kestrel SSO) and the merge commits
- .github/workflows/validate.yml:126-129 (FALCON_PUBLICATION_ALLOW_TOPIC only when event_name == pull_request)
- GitHub Actions run 42164078378 (push, db8c409, 2026-11-06): check 'validate' failure; log line 'FAIL publication equality ... commits after the declared commit touch ...'
- check_publication_equality.py at db8c409: FAIL (commits after declared commit touch source files)

**Remediation:** Rebind the publication chain at the post-Kestrel commit (build package, regenerate closeout, publish digest) before/at merge of source waves, and add a post-merge/main check that fails fast when the declared commit is behind source commits; consider requiring the rebind as part of the merge.

**Verification note:** New P2. The gate is honestly strict and detects the drift; the defect is the process leaving main unbound and red after a security-relevant merge.

#### `REL-P3-001` (P3, partially-fixed)

**No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented**

Previous status: `open`. 

A generator now exists (automation/validation/gen_changelog.py) and CHANGELOG.md documents through 2026.10.14, but the 2026-10-15..11-05 window (including the 2026-10-23 audit, P1 remediation, P2 docs and the Kestrel SSO cutover) is undocumented, and generation is not wired into CI.

Evidence:
- automation/validation/gen_changelog.py exists (--since helper)
- CHANGELOG.md:7 last window '## 2026.10.14'; no 2026.10.15+ entries
- grep automation/ ci/ .github/ for gen_changelog: no CI wiring

**Remediation:** Generate and publish the 2026-10-15..11-05 window and wire gen_changelog.py into the release flow.

**Verification note:** Generator leg fixed; coverage still stale.

#### `REL-P3-002` (P3, verified-fixed)

**Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place**

Previous status: `verified-fixed`. 

VERSION and an annotated tag exist; the remaining staleness (no bump/tag since 2026.10.11) is tracked under REL-P2-001.

Evidence:
- VERSION: 2026.10.11; tag v2026.10.11 exists
- docs/security/BRANCH_PROTECTION.md:59 matches the tag policy

**Remediation:** None beyond REL-P2-001.

**Verification note:** Mechanism fixed; tag freshness is a REL-P2-001 residual.

#### `REL-P3-003` (P3, partially-fixed)

**The delivered package embeds a closeout bound to the previous publication cycle while the digest declares the manifest commit; the equality gate reads the working tree only**

Previous status: `open`. 

The two-regen flow and a packaged-closeout assertion now exist, but the assertion still permits a package closeout up to 8 commits behind HEAD and compares against HEAD, not the digest's declared commit. The current package manifest (declared f79d786e) hashes closeout/FINAL_RESPONSE.json = 75e3ef6..., which names 7c447ac (the prior records commit), not f79d786e; the working-tree closeout names f79d786e. The delivered package therefore still embeds a previous-cycle closeout.

Evidence:
- PACKAGE_DIGEST.txt:2-4 (declared commit f79d786e)
- review-package/MANIFEST.sha256:314 (closeout/FINAL_RESPONSE.json = 75e3ef6...); the file at f79d786e names commit 7c447ac
- closeout/FINAL_RESPONSE.json at HEAD names f79d786e (sha256 fbfc5bac...)
- automation/validation/verify_delivery.sh:55-70 (assertion allows distance <= 8 and compares to HEAD, not the declared commit)
- CHANGELOG.md:12-14 claims REL-P3-003 fixed by the two-regen flow

**Remediation:** Regenerate the closeout before building the package (or rebuild the manifest after) and assert packaged-closeout commit == declared commit; tighten the distance from 8 to 0.

**Verification note:** Partially fixed: assertion added, but the shipped package still lags the declared commit and the gate permits it.

### TEST

#### `TEST-P2-001` (P2, verified-fixed)

**external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass**

Previous status: `verified-fixed`. 

The workflow now states explicitly that it runs on the lab runner and asserts reachability only; Access enforcement is asserted from the non-owner vantage by the independent site-host watcher. The watcher exists and performs the cloudflareaccess.com redirect check.

Evidence:
- .github/workflows/external-smoke.yml:3-12, :27-31 (vantage note; lab runner; DO watcher owns enforcement)
- automation/alerting/do_watcher/watch.sh:58-67 (non-owner vantage; Cloudflare Access redirect assertion)

**Remediation:** None.

**Verification note:** Fix persists; no regression from the added 401/403/200 acceptance.

#### `TEST-P2-002` (P2, open) — **NEW**

**The mTLS ingest migration left three plaintext HTTP validation paths that can no longer exercise replay/DLQ ingress**

The aggregator's edge_ingest source now requires mutual TLS (verify_certificate: true), and the probe sink presents a client certificate. Three live validation scripts still POST plain http://vector-aggregator:6000/ without certs: phase4_data_checks.sh (the replay test, expects events to be ingested), probe_pipeline_test.sh (the dead-letter test, expects the DLQ to grow), and phase7_security_checks.sh (old-credential rejection). Against the TLS listener the plaintext requests fail at the handshake, so the replay and DLQ checks either fail or pass for the wrong reason; the security regression suite no longer tests the deployed ingress.

Evidence:
- config/vector/aggregator.yaml:17-35 (tls.enabled, verify_certificate: true)
- config/vector/edge.yaml:239-252 (https + client cert)
- automation/validation/phase4_data_checks.sh:111 (curl http://vector-aggregator:6000/ for the replay test)
- automation/validation/probe_pipeline_test.sh:48 (curl http://vector-aggregator:6000/ for the dead-letter test)
- automation/validation/phase7_security_checks.sh:85 (old-credential POST over http://)
- evidence/raw/REVIEW-FIX/20261014T232947Z_ingest-mtls.out: handshake failure without a client certificate

**Remediation:** Update the three scripts to use https with the ingest CA/client cert from /srv/falcon/secrets/vector-ingest (or run the request from the probe container), and add an offline fixture asserting the plaintext path is rejected.

**Verification note:** New P2. The mTLS migration itself is sound (ARCH-P2-003 verified-fixed); its negative/positive tests were not migrated.

#### `TEST-P3-001` (P3, partially-fixed)

**CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths**

Previous status: `open`. 

The CI check now verifies 7 in-repo captures (up from 0), but 1,295 of 1,302 metas still point at lab-absolute paths and are skipped under FALCON_EVIDENCE_OPTIONAL=1. The check states the skip explicitly; there is still no split check that verifies the committed manifest in CI.

Evidence:
- CI run 42164078378 (db8c409): 'PASS evidence integrity (7 captures, 1295 external skipped in CI)'
- ci/validate.py:246-267 (skip outside-repo artifacts when OPTIONAL_EVIDENCE=1)
- .github/workflows/validate.yml:133 (FALCON_EVIDENCE_OPTIONAL=1)

**Remediation:** Split the check: CI verifies the committed evidence/MANIFEST.sha256 hashes; the lab verifies meta raw artifacts. Or state the residual explicitly in the check output/doc.

**Verification note:** Improved from 0 to 7 in-repo captures; the precision/claim gap remains for 1,295 rows.

#### `TEST-P3-002` (P3, open)

**The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead**

Previous status: `open`. 

The reader still loads only the first 15 lines (ci/validate.py:493); the line-26 marker in validate_gate_test.sh is fixture content, not the suite's own marker. A genuinely root/docker-requiring suite whose marker is later would run instead of skipping.

Evidence:
- ci/validate.py:493 (readlines()[:15]) and :497 (marker regex)
- automation/validation/tests/validate_gate_test.sh:26 (marker inside the skip fixture)
- CI 2026-11-06: validate_gate_test PASS; container_ensure_live_test correctly SKIPped (marker in first 15 lines)

**Remediation:** Scan the header comment block (or the whole file) for the marker.

**Verification note:** Unchanged; harmless in the current suite, general late-marker risk remains.

## Coverage and residuals

- All 36 actionable G3 findings from the 2026-10-14 pass were re-checked; no G3 finding was dropped as out-of-scope.
- The newest full-domain audit in the repository remains the 2026-10-05 record (ORCH-P2-001); the 2026-10-23 run is a focused deep-dive, so the check engine (2026-10-13), Console (2026-10-21) and Kestrel SSO (2026-11-05) are not covered by a full-domain pass. That is a coverage observation, not scored as a separate finding.
- Live-only claims (Grafana rule count, container drift, Wazuh index state) are not re-measured here; the repository-side source/catalogue and gate evidence is used. G1/G2 own live security/CI verification.
- The pack checks were run read-only from `/root/repo-deep-dive` at `4f42d9b`; the falcon clone is at `db8c409` and was not modified.

