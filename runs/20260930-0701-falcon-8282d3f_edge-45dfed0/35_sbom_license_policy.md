# SBOM and License Policy Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: `falcon-build` (central), `falcon-edge-build` (edge), `/home/user/falcon-edge-delivery`
- Branch: `main` (both). Commits: falcon `8282d3f`; edge `f1c5def` (run anchored at edge `45dfed0`)
- Generated at: 2026-09-30 · Auditor: DeepSeek V4.1 Flash (subagent, prompts 11 + 35) · Area code: SBOM
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/35_sbom_license_policy.md`
- Companion: `sbom_license_policy_recommendation.md`
- Scope limitations: read-only; no network/GitHub API; trivy/syft/Docker not executed (artifacts audited as files); root-owned delivery files unreadable; upstream license texts not fetched.

## Scope

Reviewed: manifests/lockfiles, Docker image inventory and SBOMs, GitHub Actions dependencies, dependency updates, license fields/policy, third-party and transitive components, SBOM generation workflows, container SBOMs, dependency review, vulnerability data, release provenance, signing/attestation, and exception records in both repos and the delivered sets. Not reviewed: upstream license texts, CVE exploitability, GitHub dependency-graph alerts, live containers.

## Evidence Reviewed

- `falcon-build/sbom/*.cdx.json` (13), `sbom/vuln/*.json` (12), `sbom/vuln-summary.csv`; `automation/validation/{sbom-and-vuln.sh,vuln-summary.sh,install-trivy.sh,build_review_package.sh,verify_delivery.sh,verify_publication_chain.sh}`; `pins/images.lock`; `compose/central/opensearch-s3.Dockerfile`; `.github/workflows/validate.yml`; `.github/dependabot.yml`; `ci/validate.py`
- `falcon-build/docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md` (OD-11/DD-15); `docs/phase8/CLOSEOUT.md` (license-free amendment); `ledgers/exception_register.md`; `/home/user/falcon-review-delivery-2026-09-30.tar.gz` (no `.cdx.json`; ships `vuln-summary.csv`)
- `falcon-edge-build/automation/validation/{build_sbom.py,build_release_manifest.py,build_review_package.sh,verify_review_package.sh}`; `.github/workflows/{bake-image,publish-release,validate}.yml`; `.github/dependabot.yml`; `docs/security/DEPENDENCY_POLICY.md`; `docs/GITHUB_CI.md`; `/home/user/falcon-edge-delivery/` (lab6–lab8 SBOMs, release manifest + sidecar, images, bundles); prior run `runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/` (REV-P3-009, ND-P2-017)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Parse lab8 SBOM | inspection | Component/license coverage | 636 components; **0 with licenses**; no `metadata.tools`; 3 synthetic components |
| lab7 vs lab8 SBOM diff | analysis | Consistency | lab8 = lab7 − 78 packages (all `kismet-*`, `apt-transport-https`, `isa-support`, …); provenance `ssh` (live card) vs `file` (image) |
| SBOM ↔ image binding | execution | Binding | lab8 `metadata.component` sha256 == manifest image entry; manifest `sbom.sha256` == file (both MATCH) |
| Parse falcon image SBOMs | analysis | License coverage | Partial (0/49 node-exporter, 0/441 prometheus, 18/378 traefik); `repo.cdx.json` = **0 components** |
| SBOM coverage vs `pins/images.lock` | analysis | Shipped coverage | 6/18 images have no SBOM file (local OpenSearch S3, 3× IRIS, rabbitmq, opencanary) |
| Delivery archive SBOM grep | execution | Delivery completeness | **0** `.cdx.json`; `vuln-summary.csv` present |
| `sha256sum -c` edge sidecars | execution | Provenance binding | Manifest sidecar **FAIL** (`18681751…` vs actual `3fa4a49c…`); lab8 SBOM sidecar FAIL (records `/home/runner/...`) |
| Edge release manifest audit | inspection | Provenance | ed25519 keyId `5ea52faf9cf6ee97`; commit `155f244` (tag `lab-2026.09.30-lab8`); all artifact digests match |
| Edge `verify_review_package.sh` | execution | Package reproducibility | PASS (876 entries, no caches/outputs, secret scan clean) |
| Workflow grep for sbom/vuln/license gates; owner acceptance + exception register | inspection | CI enforcement / policy authority | Edge: no vulnerability scanner; falcon: no CI SBOM/vuln/license gate; DD-15/OD-17 threshold; license-free amendment; EX-11/EX-12; no license exception register |

## Executive Summary

"License-free" is an owner requirement with recorded decisions (ntopng Community; DB-IP Lite instead of MaxMind; no nProbe), but it is managed only in prose: no license inventory, allow/deny list, or CI gate, and the machine-readable inventories cannot support enforcement — edge SBOMs carry zero license fields, central image SBOMs cover licenses only partially, and the repository SBOM is empty. The edge's own dependency policy lists license checks, SBOM presence, and vulnerability thresholds as future enforcement.

Provenance is asymmetric. The edge ships an ed25519-signed manifest that hash-binds every artifact, including the SBOM (all verified here), and its review package verifies deterministically (876 entries PASS). But the manifest's checksum sidecar is stale (`sha256sum -c` fails), the public key is unpublished (REV-P3-009 still-open), and the lab8 SBOM sidecar embeds a GitHub-runner path. The central delivery ships no SBOMs and no cryptographic signature. Recommended: adopt the companion license policy with a CI gate, generate release-time SBOMs for every shipped artifact, rebuild the edge manifest/sidecar as one atomic step, publish the key, and add provenance attestations.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Edge image SBOM | `falcon-edge-sensor-2026.09.30-lab8-sbom.cdx.json` | Image inventory | 636 comps; no licenses/tools metadata | Medium | Hash-bound |
| Edge SBOM builder | `automation/validation/build_sbom.py` | CDX 1.5 generator | dpkg + 3 hardcoded comps | Medium | `:73-106` |
| Edge release manifest | `falcon-edge-release-manifest-20260930.json` | Signed artifact set | ed25519, keyId `5ea52faf…` | Medium | Sidecar stale; pubkey absent |
| Edge license policy | `docs/security/DEPENDENCY_POLICY.md` | Rules + enforcement | Principles; CI enforcement "future" | High | No license gate |
| Central image SBOMs | `sbom/*.cdx.json` | Image inventories | 09-20; 12/18 images; partial licenses | High | Stale; 6 missing |
| Central repo SBOM | `sbom/repo.cdx.json` | Repo inventory | **0 components** | High | No useful scope |
| Central vuln data | `sbom/vuln-summary.csv`, `sbom/vuln/*` | HIGH/CRIT counts | 09-22; `ntopng:latest` naming | High | No refresh/gate |
| Central delivery | `/home/user/falcon-review-delivery-2026-09-30.tar.gz` | Review set | No SBOMs | Medium | Exclusion vs policy |
| Provenance (central) | `PACKAGE_DIGEST.txt` + sidecars | Binding | SHA-256 only, unsigned | Medium | Human-signed docs separate |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 4 | Stdlib-first | No CI invariant | Assert no runtime deps |
| Lockfiles | 4 | `pins/images.lock` | No license column; manual verify | Extend schema |
| Docker images | 3 | Digest pins | 6/18 unscanned; stale | SBOM-P2-002 |
| GitHub Actions | 5 | SHA pins + Dependabot + zizmor | Tool checksums (SC report) | Checksums |
| Dependency updates | 4 | Weekly actions + drift | No image cadence | Patch windows |
| License fields | 1 | Edge 0/636; repo empty | Cannot enforce license-free | SBOM-P1-001 |
| Third-party/transitive | 2 | Trivy CDX once | Stale/partial | Rebuild with licenses |
| SBOM workflows | 2 | Edge bake step; central manual | No gate centrally | SBOM-P2-002/003 |
| Container SBOM | 3 | 12 image files + edge | Coverage/staleness | Regenerate per release |
| Dependency review | 2 | No dependency-review action | No PR license/SBOM gate | Add gate |
| Vulnerability alerts | 2 | 09-22 summary (95 unfixed ntopng highs) | No refresh/gate | SBOM-P2-003 |
| Release provenance | 3 | Signed edge manifest; central digests | Sidecar stale; key absent; central unsigned | SBOM-P2-001/004 |

## Detailed Review

### Item: License policy and enforcement
- Evidence: `DEPENDENCY_POLICY.md` §1/§7 (license check, SBOM entry, vuln scan per dep; "Future enforcement … requirements pinning, image digest pinning, SBOM presence, vulnerability scan thresholds"); `OWNER_ACCEPTANCE.md` license-free row + DD-15; `CLOSEOUT.md` amendment; EX-11/EX-12; no `LICENSE*` file; no license fields in `images.lock`.
- Gap/fix: no inventory, allow/deny list, CI gate, or exception process; adopt `sbom_license_policy_recommendation.md`, baseline the stack licenses, add gate + register with expiry.

### Item: SBOM completeness over shipped artifacts
- Evidence: edge `build_sbom.py:73-106` (dpkg + hardcoded `0.1.0`; no files/hashes/relationships/licenses); lab7 via SSH vs lab8 from image; central delivery 0 CDX; `build_review_package.sh` deletes `*.cdx.json`; `repo.cdx.json` empty; 6/18 images uninventoried.
- Gap/fix: no SBOM for the update bundle or app components; generate release-time SBOMs (syft/trivy with licenses), include them, add a coverage check.

### Item: Release provenance and signing
- Evidence: `build_release_manifest.py:66-77` signs `{schemaVersion, generatedAt, commit, artifacts, sbom}` with the ed25519 seed; keyId `5ea52faf9cf6ee97`; no public key; stale sidecar; central unsigned; `publish-release.yml` SHA256SUMS only.
- Gap/fix: publish `signing.pub.pem`; atomic re-sign + sidecar; add attestations; sign the central digest.

### Item: Prior-run finding re-verification

| Prior finding | Status | Evidence |
|---|---|---|
| REV-P3-009 (no ed25519 public key in delivery) | `still-open` | No pubkey file in delivery; verification requires `/home/user/falcon-edge-secrets/signing.seed` |
| ND-P2-017 (release set not coherent) | `partially-fixed` | Bundle now in signed manifest; review pkg `0b83acc` precedes release `155f244`; sidecar stale → SBOM-P2-001 |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SBOM-001 | Manifests | Stdlib-first | Documented | No CI assertion | P3 | Assert invariant |
| SBOM-002 | Lockfiles | `pins/images.lock` | Digests | No license fields | P3 | Extend schema |
| SBOM-003 | Docker images | Compose digests | All pinned | 6 without SBOM | P2 | SBOM-P2-002 |
| SBOM-004 | GitHub Actions | SHA pins + Dependabot | Strong | Tool downloads (SC) | P3 | Checksums |
| SBOM-005 | Dependency updates | Weekly + drift | Partial | Image cadence | P3 | Patch windows |
| SBOM-006 | License fields | Edge 0/636 | Owner acceptances | No data/gate | P1 | SBOM-P1-001 |
| SBOM-007 | Third-party deps | Trivy CDX | Inventoried once | Stale/partial | P2 | Regenerate |
| SBOM-008 | SBOM workflows | Edge bake step | SBOM in CI | Central manual/excluded | P2 | SBOM-P2-002 |
| SBOM-009 | Container SBOM | 12 files | Exists | Stale; naming | P2 | Rebuild with licenses |
| SBOM-010 | Dependency review | Dependabot only | Config exists | No PR gate | P2 | Add gate |
| SBOM-011 | Vulnerability alerts | `vuln-summary.csv` | One-time trivy | No refresh/gate | P2 | SBOM-P2-003 |
| SBOM-012 | Release provenance | Edge signed manifest; central digests | Hash binding | Sidecar stale; key absent; central unsigned | P2 | SBOM-P2-001/004 |

## Findings

### Finding ID: SBOM-P1-001 - No license data or license gate exists; the license-free requirement cannot be enforced from artifacts

- Severity: P1 · Confidence: High · Area: SBOM (license policy)
- Evidence: edge lab8 SBOM 636 components, 0 with `licenses`; `build_sbom.py:73-106` emits none; central `sbom/*.cdx.json` partial/absent (0/49 node-exporter, 0/441 prometheus, 18/378 traefik); `sbom/repo.cdx.json` 0 components; `images.lock` has no license field; `DEPENDENCY_POLICY.md:28-36` lists license/SBOM checks as future; no `LICENSE*` file; decisions only in `OWNER_ACCEPTANCE.md`/`CLOSEOUT.md` prose (license-free amendment, OD-11/DD-15, EX-11/EX-12) with no license exception register entries.
- What is happening: "license-free" is directionally followed but has no machine-readable inventory, allow/deny policy, CI check, or exception process.
- Why it matters / User / business impact: a future image/dependency change (e.g. ntopng Enterprise, nProbe, MaxMind) ships silently and a reviewer cannot verify the license-free requirement from the delivered set; legal/cost risk and doctrine drift · Security / privacy / reliability impact: none direct; governance/auditability.
- Recommended fix: adopt `sbom_license_policy_recommendation.md`; collect licenses in SBOM generation (both products); add a CI license gate with an allow list and an expiry-bearing exception register; baseline the current stack.
- Suggested validation: CI fails a `LicenseRef-Proprietary` fixture; baseline matches adopted policy for all 18 images + edge image.
- Owner suggestion: falcon (policy) + edge maintainers · Effort estimate: M · Dependencies: license-capable SBOM tooling
- Status: open

### Finding ID: SBOM-P2-001 - The edge release manifest's checksum sidecar is stale; verification fails on the shipped set

- Severity: P2 · Confidence: High · Area: SBOM (release binding)
- Evidence: `falcon-edge-release-manifest-20260930.json.sha256` (04:44; records `18681751…`) vs manifest rebuilt 06:25 (actual `3fa4a49c…`); `sha256sum -c` FAIL; all manifest artifact digests match on-disk files; prior REV-P2-001 class.
- What is happening: the manifest was rebuilt during the lab8 round without atomically regenerating its checksum sidecar (sidecar predates the file it describes).
- Why it matters / User / business impact: every verifier gets FAIL and cannot distinguish stale metadata from tampering; release integrity cannot be demonstrated with the shipped instructions · Security / privacy / reliability impact: weakens the only cryptographic release chain.
- Recommended fix: regenerate manifest + sidecar (and signature) in one step, or drop the sidecar in favour of the signed manifest as root; add a delivery self-check that fails on stale sidecars; fix the lab8 SBOM checksum to a basename-only entry.
- Suggested validation: `sha256sum -c *.sha256` returns 0 across the delivery (except intentionally root-only files) and the signature verifies with the published key.
- Owner suggestion: edge maintainer · Effort estimate: S · Dependencies: signing seed access
- Status: regressed (release-binding defect recurring)

### Finding ID: SBOM-P2-002 - SBOM coverage over shipped artifacts is incomplete in both programs

- Severity: P2 · Confidence: High · Area: SBOM (completeness)
- Evidence: central delivery has 0 CDX (`tar tzf | grep -c cdx` = 0); `build_review_package.sh` deletes `*.cdx.json`; `repo.cdx.json` empty; 6/18 locked images lack SBOM; edge SBOM is a dpkg list + 3 hardcoded components with no files/hashes/relationships; `falcon-agent-0.1.1-lab.tar.gz` has no SBOM; lab7/lab8 provenance differs (`ssh` vs `file`) with 78 fewer packages.
- What is happening: SBOMs are point-in-time lab artifacts rather than release-set deliverables.
- Why it matters / User / business impact: "SBOM completeness" cannot be claimed for shipped sets and the planned license/vuln gates lack a trustworthy component list; supply-chain visibility/consumer trust · Security / privacy / reliability impact: unscoped components (no vulnerability/license mapping).
- Recommended fix: generate SBOMs at release time for all central images + repo tree and the edge image + update bundle; include and hash-bind them; add a per-artifact coverage check.
- Suggested validation: release-set test asserts one SBOM per artifact with matching hashes; NTIA minimum-fields lint.
- Owner suggestion: both maintainers · Effort estimate: M · Dependencies: tool selection
- Status: still-open (prior ND-P2-017 residual)

### Finding ID: SBOM-P2-003 - SBOM, vulnerability, and license checks are not enforced in CI; vulnerability dispositions are stale

- Severity: P2 · Confidence: High · Area: SBOM (CI enforcement)
- Evidence: edge `validate.yml` has no vuln/license/SBOM checks; `DEPENDENCY_POLICY.md:35-36` lists them as future; SBOM built only in manual `bake-image.yml`; falcon `sbom-and-vuln.sh`/`vuln-summary.sh` manual, data 09-20/22; `vuln-summary.csv` still names `ntop/ntopng:latest` while the lock is digest-pinned; IRIS/rabbitmq/opencanary/local OpenSearch never scanned; owner threshold DD-15 requires review each patch window — no refresh evidence since 09-22.
- What is happening: scanning happened once, before the latest lock changes; nothing keeps it current.
- Why it matters / User / business impact: the vulnerability statement behind the verdict ages out; new images are unscanned; license data cannot gate if never generated; unknown exposure drift on pinned-but-vulnerable images · Security / privacy / reliability impact: avoidable exposure (e.g. previously reported 95 unfixed HIGH ntopng findings).
- Recommended fix: scheduled + release-triggered CI scans (SBOM+license+vuln) for all locked images; fail on denied licenses and the owner threshold; refresh digest-named scans.
- Suggested validation: CI fails denied-license and above-threshold CVE fixtures; scheduled run refreshes `sbom/` artifacts.
- Owner suggestion: falcon + edge maintainers · Effort estimate: M · Dependencies: CI runtime for image scans
- Status: open

### Finding ID: SBOM-P2-004 - Release provenance is not independently verifiable for the edge and absent for the central delivery

- Severity: P2 · Confidence: High · Area: SBOM (provenance/signing)
- Evidence: edge manifest keyId `5ea52faf9cf6ee97`; no public key anywhere in the delivery; seed at `/home/user/falcon-edge-secrets/signing.seed` (0600) required to verify (REV-P3-009); central delivery has only `PACKAGE_DIGEST.txt` + sidecars; `verify_publication_chain.sh` protects "signed" 2026-09-29 archives with plain SHA-256 constants; `publish-release.yml` produces SHA256SUMS with no attestation; no SBOM is signed.
- What is happening: hash binding is good but cryptographic verifiability is limited to holders of the edge secret store and absent centrally.
- Why it matters / User / business impact: an external reviewer cannot verify the edge release from the delivered set and central provenance claims cannot be independently reproduced · Security / privacy / reliability impact: attestation gap (SLSA ~0-1).
- Recommended fix: publish the ed25519 public key with the manifest; add provenance attestation to bake/publish workflows; sign the central digest and SBOMs.
- Suggested validation: from delivery files alone, verify signature + all digests; `gh attestation verify` succeeds for the image.
- Owner suggestion: edge + falcon maintainers · Effort estimate: M · Dependencies: owner signing-authority decision
- Status: still-open (prior REV-P3-009)

### Finding ID: SBOM-P3-001 - SBOM metadata is inaccurate or non-portable in both programs

- Severity: P3 · Confidence: High · Area: SBOM (metadata quality)
- Evidence: `build_sbom.py:75-78` hardcodes `falcon-agent`/`falcon-control-plane` at `0.1.0` while the shipped bundle is `falcon-agent-0.1.1-lab.tar.gz`; no `metadata.tools` in the edge SBOM; lab8 SBOM sidecar records `/home/runner/work/_temp/delivery/...` so `sha256sum -c` fails off-CI; central `repo.cdx.json` empty; vuln summary mixes tag/digest naming.
- What is happening: generated metadata is not fully derived from the built artifact set, and checksum files embed CI paths.
- Why it matters / User / business impact: automated consumers and off-CI verification fail, and SBOM versions can contradict shipped bundles (tooling/audit friction) · Security / privacy / reliability impact: low.
- Recommended fix: basename-only checksum files; derive component versions/purls from build inputs; emit `metadata.tools`; give `repo.cdx.json` a real scope or mark N/A.
- Suggested validation: `sha256sum -c` passes after copying the delivery to a clean host; SBOM version equals bundle name.
- Owner suggestion: edge + falcon maintainers · Effort estimate: S · Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Non-free component enters via image update | High | Medium | License/cost/doctrine breach | SBOM-P1-001 | License gate + inventory |
| Verifier cannot validate release binding | Medium | High | Review invalidation | SBOM-P2-001/004 | Atomic re-sign + pubkey |
| Unscanned images ship with known highs | Medium | Medium | Avoidable exposure | SBOM-P2-003 | Scheduled scans + threshold |
| SBOM set incomplete for delivered artifacts | Medium | High | Audit/consumer confusion | SBOM-P2-002 | Release-time SBOMs |
| SBOM metadata misstates shipped versions | Low | Medium | Tooling failures | SBOM-P3-001 | Generate from artifact |

## Recommendations

### Immediate / Release Blocking
1. Re-generate the edge manifest + sidecar atomically and re-sign; publish the ed25519 public key (SBOM-P2-001/004, REV-P3-009).
2. Fix the lab8 SBOM checksum file to a basename-only entry after any rebuild (SBOM-P2-001/003).
### This Week
3. Adopt the companion license policy; record the baseline license inventory for all 18 images + the edge image (SBOM-P1-001).
4. Add license collection to SBOM generation (syft/trivy with license scanners) (SBOM-P1-001, P2-002).
### This Month
5. Wire a scheduled/release CI job for SBOM + license + vulnerability scans with DD-15 thresholds (SBOM-P2-003).
6. Extend the edge SBOM to files/hashes + update bundle; include SBOMs in the central delivery or record the exclusion decision (SBOM-P2-002).
7. Add provenance attestations; sign the central digest (SBOM-P2-004).
### Later / Platform Evolution
8. PR-level license gate once any package ecosystem appears; periodic license re-verification at patch windows.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Basename-only checksums | Off-CI verification works | `bake-image.yml`, delivery scripts | `sha256sum -c` after copy |
| Publish `signing.pub.pem` | Self-contained verification | delivery dir + docs | Signature verifies from release set |
| Add `--scanners license` to trivy runs | License data appears | `sbom-and-vuln.sh`, `vuln-summary.sh` | License fields present |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| License policy + CI gate | P1 | falcon | M | tooling |
| Atomic manifest/sidecar step | P1 | edge | S | seed access |
| Scheduled image scans | P2 | falcon | M | CI runtime |
| Central SBOM inclusion | P2 | falcon | S | policy |
| Attestations | P2 | both | M | owner decision |

## Suggested Tests

- CI: license gate fixture (denied license fails); SBOM coverage check; NTIA minimum-fields lint.
- Release: one-command verify (`sha256sum -c` + ed25519 verify with published key); assert no post-signing additions.
- Regression: SBOM component versions equal bundle names; sidecars reproduce on a clean host.

## Suggested Documentation Updates

- New `docs/security/LICENSE_POLICY.md` (both repos): allow/deny list, exceptions, CI wiring.
- `docs/security/DEPENDENCY_POLICY.md`: promote future enforcement items; tool-checksum rule.
- Edge release docs: verification instructions using the published key.
- `ledgers/exception_register.md`: license exceptions mapped to components (EX-11/EX-12).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Who owns production signing authority? | Publishing keys/attestations | Owner decision |
| Should the central delivery ship SBOMs? | Completeness scope | Owner/policy decision |
| Is the DD-15 per-patch-window review happening? | Threshold conformance | Dated scan artifacts per window |

## Appendix

- SBOM inventory (central): 12 image CDX + empty repo CDX; vuln JSON ×12; coverage 12/18 locked images.
- Edge SBOM deltas: lab7 (ssh/live) 714 → lab8 (file/image) 636; removed set dominated by `kismet-*`; no accompanying change record.
- Signing: manifest keyId `5ea52faf9cf6ee97`; seed `/home/user/falcon-edge-secrets/signing.seed` (0600, not read); no public key shipped.
- Recorded license decisions: license-free amendment + OD-11 (ntopng community, no nProbe/MaxMind); EX-11; EX-12 (DB-IP Lite CC BY 4.0); DD-15/OD-17 threshold; companion `sbom_license_policy_recommendation.md`.
