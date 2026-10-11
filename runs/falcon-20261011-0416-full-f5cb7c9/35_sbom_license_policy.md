# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

# SBOM and License Policy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (private)
- Branch: `main`
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:31Z
- Auditor: subagent (read-only)
- Area code: SBOM
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/35_sbom_license_policy.md
- Scope limitations: repository + read-only GitHub API + read-only local gate reproduction. No scan was regenerated (trivy DB download would be a live operation); committed SBOM/vulnerability artifacts were verified against their manifest. The `falcon-edge` release SBOM/signing is out of scope (separate repo).

## Scope

Reviewed: `sbom/` (25 CycloneDX SBOMs, 12 per-image vulnerability JSONs, `vuln-summary.csv`, `SBOM_MANIFEST.sha256`), `pins/images.lock` (24 images), `automation/validation/{sbom_coverage_check.sh,sbom_hashes.sh,vuln-summary.sh,sbom-and-vuln.sh,install-trivy.sh}`, `ci/license_check.py` + `docs/security/LICENSE_GATE.md`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md`, `docs/phase7/IMAGE_SCAN_DISPOSITION.md`, `pins/supply-chain-waivers.json`, the CI steps in `.github/workflows/validate.yml`, the local Dockerfile, `automation/validation/build_review_package.sh` + `PACKAGE_MANIFEST.sha256`, and GitHub API state (dependency review/alerts/dependency-graph SBOM). Not reviewed: the actual vulnerability databases, edge release artifacts, and license texts of every component (SBOM license fields were counted, not adjudicated).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sbom/*.cdx.json` (25) + `sbom/vuln/*.json` (12) + `vuln-summary.csv` | generated artifacts | SBOM/vuln set | 38 artifacts under SBOM_MANIFEST.sha256 |
| `sbom/SBOM_MANIFEST.sha256` | manifest | set integrity | verified in CI; unsigned |
| `pins/images.lock` | lock | pinned images | 24 entries |
| `automation/validation/sbom_coverage_check.sh` | gate | coverage + vuln + waivers | exit 1/2 fail-closed |
| `automation/validation/sbom_hashes.sh` | gate | manifest create/verify | fails on unlisted artifacts |
| `pins/supply-chain-waivers.json` | waiver | 12 vuln-scan pending | review_by 2026-12-31 |
| `ci/license_check.py`, `docs/security/LICENSE_GATE.md` | license gate | Python-only denylist | images ungated |
| `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` | doc | declared policy + owner decisions D1-D6 | stale on --require-vuln |
| `docs/phase7/IMAGE_SCAN_DISPOSITION.md` | doc | DD-15 threshold dispositions | refresh 2026-09-22 |
| `.github/workflows/validate.yml:103-106` | CI | enforced steps | `--require-vuln --vuln-waivers` + hashes |
| `build_review_package.sh`, `PACKAGE_MANIFEST.sha256` | delivery | what ships | SBOMs excluded |
| GitHub API: `code-scanning/alerts` (403), `dependency-graph/sbom` (200), `dependabot/alerts` (0 open) | live state | dependency review | GHAS gated; dependency graph available |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| Coverage 24/24 digest-bound | `bash automation/validation/sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json` | supported: PASS; pinned=24 covered=24 missing=0 mismatched=0 legacy=1 vuln_scans=12 vuln_pending=12 vuln_missing=0 |
| SBOM set matches its manifest | `bash automation/validation/sbom_hashes.sh verify` | supported: PASS (38 artifacts verified, manifest unsigned) |
| CI enforces the vuln gate | validate.yml:103-106 + run 38110410254 step 13 | supported: `--require-vuln` with waivers; green |
| Vuln data is stale | `CreatedAt` in sbom/vuln/*.json | supported: 2026-09-22 (12 scans); 12 images waived to 2026-12-31 |
| License gate scope | ci/license_check.py; LICENSE_GATE.md:18-21 | supported: installed Python distributions only; image licenses ungated; no pins/licenses.allow |
| No signing/attestation | grep workflows/scripts for attest/cosign/gpg; `gpg --list-keys`; sbom_hashes.sh:13-18 | supported: none; manifest explicitly unsigned |
| Delivery excludes SBOMs | build_review_package.sh:39,51,71; PACKAGE_MANIFEST.sha256 | supported: 0 cdx.json, 0 sbom/ paths; ./vuln-summary.csv at line 3830 |
| Doc contradicts CI (new) | SBOM_COVERAGE_AND_PROVENANCE.md:82-83 vs validate.yml:103-106 | supported: doc says --require-vuln off; CI enforces it (SBOM-P3-002) |
| Post-signing addition protection (model) | sbom_hashes.sh verify fails on an artifact not listed | supported by design; no signing exists yet |
| Prior SBOM-P2-001 still open | doc decisions + code | supported: unsigned; image/SBOM license gate not enforced |

## Executive Summary

The SBOM program remains strong on coverage and integrity: 24/24 pinned images have digest-bound CycloneDX SBOMs; the committed set (38 artifacts) is hash-verified in CI and fails closed on unlisted additions; the vulnerability gate (`--require-vuln`) is enforced with an owner-visible, expiring waiver list; the local gate passes at f5cb7c9 (24/24 covered, 12 vuln pending, 0 missing); the license gate for installed Python tooling runs in CI; and the one locally built image uses a digest-pinned base matching the lock.

Two prior gaps persist and one documentation contradiction is new. (1) Provenance is integrity-only: `SBOM_MANIFEST.sha256` and the publication chain are SHA-256 checks with no signature or attestation (owner decision D1 pending), and the image/SBOM license allow-deny gate over component license fields is still absent (only Python distributions are gated; no `pins/licenses.allow`). (2) The delivered review package excludes the entire SBOM set - all `*.cdx.json` and per-image vulnerability JSONs - shipping only `vuln-summary.csv` (D2 pending), so a pack-only reviewer cannot see the SBOMs. (3) The SBOM enforcement doc still says `--require-vuln` is off while CI enforces it with waivers, which misstates the current gate. The 12 unscanned images are explicitly waived to 2026-12-31 and the vulnerability data is from 2026-09-22.

Recommended next actions: make the D1 signing decision and bind the manifest hash into the package digest; implement the image/SBOM license gate with `pins/licenses.allow`; decide D2 (ship SBOMs or record a dated exclusion); append the current enforcement state to the SBOM doc; refresh the 12 waived scans before the waiver expires.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Image SBOMs | `sbom/*.cdx.json` | CycloneDX per image | 24/24 digest-bound | Low | 1 legacy name (ntopng) |
| Vuln JSONs | `sbom/vuln/*.json` | per-image HIGH/CRITICAL | 12 scans, 2026-09-22 | Medium | 12 images waived |
| SBOM manifest | `sbom/SBOM_MANIFEST.sha256` | set integrity | verified in CI | Low-Medium | unsigned |
| Coverage gate | `sbom_coverage_check.sh` | coverage + vuln + waivers | enforced | Low | fail-closed |
| Hash gate | `sbom_hashes.sh` | manifest verify | enforced | Low | fails on unlisted files |
| License gate | `ci/license_check.py` | Python dists | enforced | Low | images not covered |
| License policy doc | `docs/security/LICENSE_GATE.md` | denylist/allow | current | Low | image gate is the follow-up |
| SBOM/provenance doc | `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` | policy + decisions | stale (says vuln gate off) | Low | SBOM-P3-002 |
| Disposition | `docs/phase7/IMAGE_SCAN_DISPOSITION.md` | DD-15 | refresh 2026-09-22 | Medium | refresh at patch window |
| Delivery | `build_review_package.sh` | review package | excludes SBOMs | Low-Medium | D2 pending |
| Provenance | `PACKAGE_DIGEST.txt` | digest chain | SHA-256 only | Medium | D1 pending |
| GitHub dependency graph | API `dependency-graph/sbom` | native SBOM | available (5 packages) | Low | dependency review still GHAS-gated |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 4 | requirements-ci.txt hash-pinned | single Python manifest | keep |
| Lockfiles | 4 | images.lock 24 digests | two floating tag names | owner decision |
| Docker images | 4 | 24/24 digest-bound SBOMs; Dockerfile base matches lock | 12 vuln scans pending | refresh before 2026-12-31 |
| GitHub Actions | 5 | SHA-pinned; dependency-graph SBOM lists them | none | keep |
| Dependency updates | 4 | Dependabot alerts + actions/pip ecosystems | security updates off (SC-P3-002) | enable/record |
| License fields | 2 | SBOM license data 0-98%; Python gate only | no image/SBOM gate | build `pins/licenses.allow` gate |
| Third-party/transitive deps | 3 | SBOMs cover components; license data partial | no adjudication | license gate |
| SBOM workflows | 4 | coverage + hashes + --require-vuln in CI | doc contradicts gate | doc update |
| Container SBOM | 4 | 25 cdx; 1 legacy; repo.cdx 0-component | repo.cdx scope (D4) | owner decision |
| Dependency review | 2 | GHAS 403; dependency graph available | no dependency-review enforcement | plan-gated; note |
| Vulnerability alerts | 4 | Dependabot alerts on; 0 open; waivers dated | stale scans (2026-09-22) | refresh |
| Release provenance | 2 | hash chain verified; publication chain 0 failures | unsigned; SBOMs not shipped | D1/D2 decisions |

## Detailed Review

### Item: SBOM coverage and integrity
- Evidence: sbom/ (25 cdx + 12 vuln + summary); SBOM_MANIFEST.sha256; local gates.
- What it does: every pinned image has a digest-bound SBOM; the set is hash-verified and fails closed on unlisted artifacts.
- Current controls: `sbom_coverage_check.sh --require-vuln --vuln-waivers`; `sbom_hashes.sh verify`; CI steps.
- Missing controls: signature/attestation; license gate.
- Risks: tampered set can be re-hashed; license obligations unmanaged for images.

### Item: Vulnerability refresh
- Evidence: sbom/vuln CreatedAt 2026-09-22; waivers review_by 2026-12-31; IMAGE_SCAN_DISPOSITION refresh 2026-09-22.
- Current state: 12 scans stale; 12 images never scanned (waived).
- Recommended improvement: refresh at the next patch window; schedule a durable scan job.
- Risks: known-vulnerable image deployed unnoticed.

### Item: Delivery scope
- Evidence: build_review_package.sh:39,51,71; PACKAGE_MANIFEST.sha256.
- Current state: SBOMs excluded; only vuln-summary.csv ships.
- Recommended improvement: D2 decision (ship + rebind, or dated exclusion).

### Item: License policy
- Evidence: ci/license_check.py; LICENSE_GATE.md; SBOM license counts.
- Current state: Python-only denylist enforced; image gate absent.
- Recommended improvement: implement the allow/deny gate with an exception register and `pins/licenses.allow`.

### Item: Documentation consistency
- Evidence: SBOM_COVERAGE_AND_PROVENANCE.md:82-83 vs validate.yml:103-106.
- Current state: stale (--require-vuln off claim).
- Recommended improvement: append-only update for the 2026-10-11 state.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SBOM-001 | Package manifests | requirements-ci.txt | hash pins | none | P3 | keep |
| SBOM-002 | Lockfiles | images.lock | digest pins | none | P3 | keep |
| SBOM-003 | Docker images | 24/24 SBOMs | digest-bound coverage | vuln refresh pending | P3 | refresh |
| SBOM-004 | GitHub Actions | SHA pins; dependency graph | pinned | none | P3 | keep |
| SBOM-005 | Dependency updates | Dependabot | alerts + version updates | security updates off | P3 | enable |
| SBOM-006 | License fields | license_check.py | Python denylist | no image gate | P2 | build gate |
| SBOM-007 | Third-party/transitive | SBOMs | coverage | license data partial | P3 | gate + exceptions |
| SBOM-008 | SBOM workflows | validate.yml:103-106 | enforced + waivers | doc stale | P3 | doc update |
| SBOM-009 | Container SBOM | sbom/ | 25 cdx | repo.cdx 0-component | P3 | D4 decision |
| SBOM-010 | Dependency review | API 403 | none (GHAS) | no enforcement | P3 | plan-gated |
| SBOM-011 | Vulnerability alerts | API + waivers | alerts on; 0 open | stale scans | P3 | refresh |
| SBOM-012 | Release provenance | PACKAGE_DIGEST; publication chain | hash chain 0 failures | unsigned; SBOMs excluded | P2 | D1/D2 decisions |

## Findings

### SBOM-P2-001 - Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced
- Severity: P2; Confidence: High; Area: SBOM; Status: still-open
- Evidence: sbom_hashes.sh:13-18; validate.yml:103-106; LICENSE_GATE.md:18-21; no pins/licenses.allow; D1 pending.
- Impact: weak provenance (SLSA ~0-1) and unenforced image license policy.
- Fix: D1 signing/attestation + manifest binding; image license gate with exceptions. Owner: owner + security maintainer. Effort: M.

### SBOM-P3-001 - Delivered review package excludes the SBOM set entirely; only the summary CSV ships
- Severity: P3; Confidence: High; Area: SBOM; Status: still-open
- Evidence: build_review_package.sh:39,51,71; PACKAGE_MANIFEST.sha256 (0 cdx, 0 sbom/); D2 pending.
- Impact: pack-only reviewers cannot verify SBOM completeness or licenses.
- Fix: ship SBOMs + signed manifest and rebind, or record a dated exclusion. Owner: owner/policy. Effort: S.

### SBOM-P3-002 - SBOM enforcement doc contradicts the current CI gate (says --require-vuln is off)
- Severity: P3; Confidence: High; Area: SBOM; Status: open (new)
- Evidence: SBOM_COVERAGE_AND_PROVENANCE.md:71-83 vs validate.yml:103-106; run 38110410254 step 13.
- Impact: readers conclude the vuln gate is unenforced; incident/review decisions misled.
- Fix: append-only doc update. Owner: security maintainer. Effort: S.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1 @ 08e20d1, statuses per the 2026-10-11 verification register)

| Prior item | Prior status | Current verification (f5cb7c9, 2026-10-11) | Disposition |
|---|---|---|---|
| SBOM-P2-001 unsigned + image license gate absent | still-open | still unsigned (no signing/attestation anywhere); image gate absent (no pins/licenses.allow); D1 pending | re-filed as SBOM-P2-001 |
| SBOM-P3-001 delivery excludes SBOMs | open | PACKAGE_MANIFEST.sha256 still 0 cdx/0 sbom/; build script unchanged; D2 pending | re-filed as SBOM-P3-001 |
| SBOM-P2-002 coverage | fixed earlier | 24/24 digest-bound; local PASS | holds |
| SBOM-P2-003 vulnerability refresh | deferred/waived | 12 scans dated 2026-09-22; 12 images waived to 2026-12-31 with fail-closed expiry | tracked; not re-filed |
| SBOM-P2-004 provenance manifest | implemented (unsigned) | SBOM_MANIFEST.sha256 verified in CI; unsigned | folded into SBOM-P2-001 |
| SBOM-P3-001 metadata quality (repo.cdx scope, ntopng naming) | documented residual | repo.cdx.json still 0-component naming the host path; ntopng LEGACY accepted | tracked; not re-filed |
| Doc staleness (--require-vuln off) | noted in recommendations | doc still stale; CI enforces the gate | filed as SBOM-P3-002 |
| Dependency review / code scanning | n/a | code-scanning 403 (GHAS); dependency-graph SBOM 200 | noted; plan-gated |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unsigned SBOM/release set | Medium | Low-Medium | tampered set passes hash check if re-hashed | sbom_hashes.sh:13-18 | D1 signing/attestation |
| License policy unenforced for images | Medium | Medium | license obligation missed | LICENSE_GATE.md:18-21 | build the allow/deny gate |
| Stale vulnerability data | Medium | Medium | known-vulnerable image deployed | vuln CreatedAt 2026-09-22 | refresh before 2026-12-31 |
| SBOMs absent from delivery | Low-Medium | High | reviewer blindness | PACKAGE_MANIFEST.sha256 | decide D2 |
| Doc misstates enforcement | Low | Medium | wrong review decisions | doc:82-83 | doc update |
| Waiver expiry breaks CI | Low | Low | CI red without plan | waiver review_by | calendar/decision |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- SBOM-P3-002: append the current enforcement state to SBOM_COVERAGE_AND_PROVENANCE.md.
- Refresh or schedule the 12 waived vulnerability scans so `--require-vuln` is a real gate for all 24 images.

### This Month
- D1: choose signing vs attestations; bind the manifest hash into PACKAGE_DIGEST.txt.
- Implement the image/SBOM license allow-deny gate + `pins/licenses.allow` + exception process.
- D2: ship SBOMs in the review package or record the dated exclusion.

### Later / Platform Evolution
- Automate the SBOM/vuln refresh as a scheduled job on a runner with docker+network; publish SBOMs as release assets.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Update the SBOM doc (--require-vuln is on) | docs match enforcement | SBOM_COVERAGE_AND_PROVENANCE.md | doc review |
| Decide D2 (ship or date-exclude SBOMs) | closes an open owner decision | build_review_package.sh / doc | package rebuild |
| Add license summary counts to the CI job summary | visibility for reviewers | validate.yml / sbom_coverage_check.sh | run summary |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| D1 signing/attestation | P2 | owner | M | owner key or OIDC |
| Image license gate | P2 | security maintainer | M | license policy exceptions |
| Scheduled trivy refresh | P3 | CI owner | M | docker+network runner |

## Suggested Tests

- Signature/attestation verification test over the delivered files only (fixture key).
- License gate fixture: a denylisted component license must fail; an allowlisted one must pass; an exception must require an unexpired register row.
- Post-signing-addition test: add an artifact after signing and assert verification fails (the current unlisted-artifact check is the model).
- Doc-consistency test: assert the SBOM doc's enforcement statement matches validate.yml's flags.

## Suggested Documentation Updates

- `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md`: append-only update for the 2026-10-11 state (--require-vuln enforced with waivers; signing/license decisions still open).
- `docs/phase7/IMAGE_SCAN_DISPOSITION.md`: refresh the dispositions at the next scan.
- `docs/security/LICENSE_GATE.md`: add the image/SBOM gate once built.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| D1: which signing authority (owner key vs GitHub attestations)? | closes the provenance gap | owner decision-log entry |
| D2: are SBOMs in scope for the delivered package? | reviewer completeness | owner/policy decision |
| Who refreshes the trivy scans and when? | waiver expiry 2026-12-31 | scheduled job or patch-window plan |
| Are the two 2026-09-29 archives actually signed? | the verifier labels them 'signed' but only checks bytes | signature artifact or doc correction |

## Appendix

- Local reproduction: `bash automation/validation/sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json` -> `pinned=24 covered=24 missing=0 mismatched=0 legacy=1 vuln_scans=12 vuln_pending=12 vuln_missing=0`, PASS; `bash automation/validation/sbom_hashes.sh verify` -> 38 artifacts OK (`manifest unsigned`).
- CI at f5cb7c9: run 38110410254 step 13 (SBOM coverage, vulnerability gate + provenance manifest) completed success; step 14 (publication chain) success.

## Limitations

- Scans were not regenerated (would require a live trivy DB download); staleness is measured from the committed artifacts.
- License fields in SBOMs were counted, not adjudicated; component license coverage varies 0-98% per the coverage output.
- The edge-side release SBOM/signing is out of scope.

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P2-001 | P2 | Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced |
| SBOM-P3-001 | P3 | Delivered review package excludes the SBOM set entirely; only the summary CSV ships |
| SBOM-P3-002 | P3 | SBOM enforcement doc contradicts the current CI gate (says --require-vuln is off) |
