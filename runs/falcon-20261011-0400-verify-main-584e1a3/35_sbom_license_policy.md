# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

# SBOM and License Policy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (private)
- Branch: `main`
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:45Z
- Auditor: subagent (read-only)
- Area code: SBOM
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/35_sbom_license_policy.md
- Scope limitations: repository + read-only GitHub API. No scan was regenerated (trivy DB download would be a live operation); committed SBOM/vulnerability artifacts were verified against their manifest. The `falcon-edge` release SBOM/signing is out of scope (separate repo).

## Scope

Reviewed: `sbom/` (25 CycloneDX SBOMs, 12 per-image vulnerability JSONs, `vuln-summary.csv`, `SBOM_MANIFEST.sha256`), `pins/images.lock` (24 images), `automation/validation/{sbom_coverage_check.sh,sbom_hashes.sh,vuln-summary.sh,sbom-and-vuln.sh,install-trivy.sh}`, `ci/license_check.py` + `docs/security/LICENSE_GATE.md`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md`, `docs/phase7/IMAGE_SCAN_DISPOSITION.md`, `pins/supply-chain-waivers.json`, the CI steps in `.github/workflows/validate.yml`, `compose/central/opensearch-s3.Dockerfile`, `automation/validation/build_review_package.sh` + `PACKAGE_MANIFEST.sha256`, and GitHub API state for dependency review/alerts. Not reviewed: the actual vulnerability databases, edge release artifacts, and license texts of every component (the SBOM license fields were counted, not adjudicated).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sbom/*.cdx.json` (25) + `sbom/vuln/*.json` (12) + `vuln-summary.csv` | generated artifacts | SBOM/vuln set | 38 artifacts under `SBOM_MANIFEST.sha256` |
| `sbom/SBOM_MANIFEST.sha256` | manifest | set integrity | unsigned; relative paths |
| `pins/images.lock` | lock | pinned images | 24 entries |
| `automation/validation/sbom_coverage_check.sh` | gate | coverage + vuln + waivers | exit 1/2 fail-closed |
| `automation/validation/sbom_hashes.sh` | gate | manifest create/verify | fails on unlisted artifacts |
| `pins/supply-chain-waivers.json` | waiver | 12 vuln-scan pending | review_by 2026-12-31 |
| `ci/license_check.py`, `docs/security/LICENSE_GATE.md` | license gate | Python-only denylist | images ungated |
| `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` | doc | declared policy + owner decisions D1-D6 | partially stale |
| `docs/phase7/IMAGE_SCAN_DISPOSITION.md` | doc | DD-15 threshold dispositions | refresh 2026-09-22 |
| `validate.yml:103-106` | CI | enforced steps | `--require-vuln --vuln-waivers` + hashes |
| `build_review_package.sh`, `PACKAGE_MANIFEST.sha256` | delivery | what ships | SBOMs excluded |
| GitHub API: `code-scanning/alerts`, `dependency-graph/*`, `dependabot/alerts` | live state | dependency review | 403/404 (GHAS + disabled) |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| Coverage 24/24 digest-bound | `bash automation/validation/sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json` | supported: PASS; pinned=24 covered=24 missing=0 mismatched=0 legacy=1 vuln_scans=12 vuln_pending=12 vuln_missing=0 |
| SBOM set matches its manifest | `bash automation/validation/sbom_hashes.sh verify` | supported: PASS (38 artifacts, manifest unsigned) |
| CI enforces the vuln gate | `.github/workflows/validate.yml:103-106` | supported: `--require-vuln` with waivers; local equivalent PASS |
| Vuln data is stale | `CreatedAt` fields in `sbom/vuln/*.json` | supported: 2026-09-22 (12 scans); 12 images waived |
| License gate scope | `ci/license_check.py`, LICENSE_GATE.md:18-21 | supported: installed Python distributions only; image licenses ungated |
| No signing/attestation | grep workflows/scripts for attest/cosign/gpg; `sbom_hashes.sh:13-18` | supported: none; manifest explicitly unsigned |
| Delivery excludes SBOMs | `build_review_package.sh:39,50-51,71`; `PACKAGE_MANIFEST.sha256` | supported: 0 `*.cdx.json`, 0 `sbom/` paths; `./vuln-summary.csv` at root |
| Prior SBOM-P2-001 still open | doc decisions + code | supported: unsigned; image/SBOM license gate not enforced |

## Executive Summary

The SBOM program is stronger than the prior audit recorded: 24/24 pinned images have digest-bound CycloneDX SBOMs; the committed set (38 artifacts) is hash-verified in CI and fails closed on unlisted additions; the vulnerability gate (`--require-vuln`) is now enforced in CI with an owner-visible, expiring waiver list; the local gate passes at HEAD; and the license gate for installed Python tooling runs in CI. The one locally built image (`falcon-opensearch-s3`) uses a digest-pinned base matching the lock.

Two gaps remain. First, provenance is integrity-only: `SBOM_MANIFEST.sha256` and the publication chain are SHA-256 checks with no signature or attestation (owner decision D1 still pending), and the image/SBOM license allow-deny gate over component license fields is still not implemented (the SBOM license data exists at 38-98% coverage; only Python distributions are gated). Second, the delivered review package excludes the entire SBOM set — all `*.cdx.json` and per-image vulnerability JSONs — shipping only `vuln-summary.csv`; a pack-only reviewer cannot see the SBOMs (owner decision D2 still pending). The 12 unscanned images are explicitly waived to 2026-12-31, and the vulnerability data itself is from 2026-09-22.

Recommended next actions: make the D1 signing decision and bind the manifest hash into the package digest; implement the image/SBOM license gate with `pins/licenses.allow`; decide D2 (ship SBOMs or record a dated exclusion); refresh the 12 waived scans before the waiver expires; append the current state to the (stale) SBOM doc.

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
| SBOM/provenance doc | `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` | policy + decisions | stale (says vuln gate off) | Low | needs append-only update |
| Disposition | `docs/phase7/IMAGE_SCAN_DISPOSITION.md` | DD-15 | refresh 2026-09-22 | Medium | refresh at patch window |
| Delivery | `build_review_package.sh` | review package | excludes SBOMs | Low-Medium | D2 pending |
| Provenance | `PACKAGE_DIGEST.txt` | digest chain | SHA-256 only | Medium | D1 pending |

## Findings

### Finding ID: SBOM-P2-001 (prior, still-open) - Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced

- Severity: P2
- Confidence: High
- Area: SBOM
- Evidence:
  - `automation/validation/sbom_hashes.sh:13-18` - "The manifest is NOT signed: falcon has no published signing key, so this proves integrity of the set, not authorship"
  - `.github/workflows/validate.yml:103-106` - coverage + hash verification only; no signing/attestation step anywhere (grep for attest/cosign/gpg finds none in `.github/`, `automation/`, `ci/`)
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:102-105` (no signature, no published key), `:156-158` (D1 signing authority "OWNER DECISION REQUIRED"), `:88-92` (image/SBOM license allow-deny gate is "the remaining SBOM-P1-001 follow-up")
  - `ci/license_check.py` covers installed Python distributions only (`docs/security/LICENSE_GATE.md:18-21`); no `pins/licenses.allow` exists
  - Partial progress since the prior run: the vulnerability gate is now enforced (`validate.yml:105` uses `--require-vuln --vuln-waivers pins/supply-chain-waivers.json`), and the SBOM set is hash-verified in CI
- What is happening: the SBOM/release chain proves integrity (hashes) but not authorship (no signature/attestation), and the license policy for image components (the data exists in the SBOMs at 38-98% field coverage) is documented but not gated.
- Why it matters: a reviewer cannot distinguish an owner-produced SBOM set from a tampered one that was re-hashed; and license obligations for shipped images are managed by manual dispositions only.
- User / business impact: weaker release provenance (SLSA ~0-1) and unenforced license policy for images.
- Security / privacy / reliability impact: supply-chain tamper-evidence gap.
- Recommended fix: decide D1 - sign `sbom/SBOM_MANIFEST.sha256` with an owner-held ed25519/GPG key and publish the public key, or use GitHub artifact attestations; bind the manifest hash into `PACKAGE_DIGEST.txt`. Implement the image/SBOM license allow-deny gate over the collected component license fields with a time-boxed exception process and `pins/licenses.allow`.
- Suggested validation: `openssl`/`cosign` verify of the manifest with only delivered files; a fixture with a denylisted component license fails the gate; an unsigned or mismatched manifest fails.
- Owner suggestion: owner (signing authority) + security maintainer (license gate).
- Effort estimate: M
- Dependencies: D1 owner decision; license-policy exception process.
- Status: still-open (prior SBOM-P2-001; partial progress on the vuln gate)

### Finding ID: SBOM-P3-001 (new, ID provisional) - Delivered review package excludes the SBOM set entirely; only the summary CSV ships

- Severity: P3
- Confidence: High
- Area: SBOM
- Evidence:
  - `automation/validation/build_review_package.sh:39` copies only `sbom/vuln-summary.csv` (to the package root), `:50-51` deletes every `*.cdx.json`, `:71` prints the exclusion ("sbom/*.cdx.json (large generated SBOMs)")
  - `PACKAGE_MANIFEST.sha256` (3,783 entries; sha256 `5f591655...` equals `PACKAGE_DIGEST.txt` `review_package_manifest_sha256`) contains 0 `*.cdx.json` entries and 0 `sbom/` paths; the summary appears as `./vuln-summary.csv` (entry 3783)
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:159` - D2 (ship SBOMs in the review package vs dated exclusion) is "OWNER/POLICY DECISION REQUIRED"
- What is happening: the repository has a complete digest-bound SBOM set, but the delivered review package ships none of it (not even the per-image vulnerability JSONs), so a pack-only reviewer cannot verify SBOM completeness or component licenses from the delivery.
- Why it matters: the prompt's "SBOM completeness over shipped artifacts" is empty by construction; the delivered provenance story omits the SBOM evidence.
- User / business impact: reviewers/distributors cannot inspect what is in the images.
- Security / privacy / reliability impact: reduced transparency; not a direct vulnerability.
- Recommended fix: decide D2 - include `sbom/*.cdx.json`, `sbom/vuln/*.json` and the (signed) `SBOM_MANIFEST.sha256` in the review package and re-bind `PACKAGE_DIGEST.txt`; or record a dated exclusion decision in the doc and keep the set repo-only.
- Suggested validation: rebuild the package and assert the SBOM files and manifest are present and hash-match; or assert the dated exclusion note exists.
- Owner suggestion: owner/policy.
- Effort estimate: S
- Dependencies: D1 (signing) if the shipped manifest is to be signed.
- Status: open (owner decision pending)

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

| Prior item | Prior status | Current verification | Disposition |
|---|---|---|---|
| SBOM-P2-001 unsigned artifacts + license gate not enforced | open | Still unsigned (no signing/attestation anywhere); image license gate still absent (`ci/license_check.py` Python-only; no `pins/licenses.allow`). Partial progress: `--require-vuln` now enforced in CI with expiring waivers | re-filed as SBOM-P2-001 (still-open) |
| SBOM-P2-002 coverage | fixed earlier | 24/24 digest-bound; local PASS | holds |
| SBOM-P2-003 vulnerability refresh | deferred/waived | 12 scans dated 2026-09-22; 12 images waived to 2026-12-31 with fail-closed expiry | tracked; not re-filed |
| SBOM-P2-004 provenance manifest | implemented (unsigned) | `SBOM_MANIFEST.sha256` verified in CI; unsigned | folded into SBOM-P2-001 |
| SBOM-P3-001 metadata quality (repo.cdx.json scope, ntopng naming) | documented residual | `sbom/repo.cdx.json` still a 0-component host-path FS SBOM; ntopng legacy name accepted as LEGACY by the coverage check | tracked; not re-filed |
| Dependency review / code scanning | n/a | GHAS plan-gated (403); Dependabot alerts disabled (SC report) | noted |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unsigned SBOM/release set | Medium | Low-Medium | tampered set passes hash check if re-hashed | sbom_hashes.sh:13-18 | D1 signing/attestation |
| License policy unenforced for images | Medium | Medium | license obligation missed | LICENSE_GATE.md:18-21 | build the allow/deny gate |
| Stale vulnerability data | Medium | Medium | known-vulnerable image deployed | vuln CreatedAt 2026-09-22 | refresh before 2026-12-31 |
| SBOMs absent from delivery | Low-Medium | High | reviewer blindness | PACKAGE_MANIFEST.sha256 | decide D2 |
| Waiver expiry breaks CI | Low | Low | CI red without plan | waiver review_by | calendar/decision |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Refresh the 12 waived vulnerability scans (or schedule the refresh) so `--require-vuln` is a real gate for all 24 images.
- Append the current enforcement state to `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` (it still says `--require-vuln` is off).

### This Month
- D1: choose signing vs attestations; bind the manifest hash into `PACKAGE_DIGEST.txt`.
- Implement the image/SBOM license allow-deny gate + `pins/licenses.allow` + exception process.
- D2: ship SBOMs in the review package or record the dated exclusion.

### Later / Platform Evolution
- Automate the SBOM/vuln refresh as a scheduled job on a runner with docker+network; publish SBOMs as release assets.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Update the SBOM doc (`--require-vuln` is on) | docs match enforcement | SBOM_COVERAGE_AND_PROVENANCE.md | doc review |
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
- License gate fixture: a component with a denylisted license must fail; an allowlisted one must pass; an exception must require an unexpired register row.
- Post-signing-addition test: add an artifact after signing and assert verification fails (the current unlisted-artifact check is the model).

## Suggested Documentation Updates

- `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md`: append-only update for the 2026-10-09 state (`--require-vuln` enforced with waivers; signing/license decisions still open).
- `docs/phase7/IMAGE_SCAN_DISPOSITION.md`: refresh the dispositions at the next scan.
- `docs/security/LICENSE_GATE.md`: add the image/SBOM gate once built.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| D1: which signing authority (owner key vs GitHub attestations)? | closes the provenance gap | owner decision-log entry |
| D2: are SBOMs in scope for the delivered package? | reviewer completeness | owner/policy decision |
| Who refreshes the trivy scans and when? | waiver expiry 2026-12-31 | scheduled job or patch-window plan |

## Limitations

- Scans were not regenerated (would require a live trivy DB download); staleness is measured from the committed artifacts.
- License fields in SBOMs were counted, not adjudicated; component license coverage varies 38-98% per the project's own table.
- The edge-side release SBOM/signing is out of scope.

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P2-001 | P2 | Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced |
| SBOM-P3-001 | P3 | Delivered review package excludes the SBOM set entirely; only the summary CSV ships |
