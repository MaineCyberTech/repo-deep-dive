# SBOM and License Policy Recommendation (companion artifact)

- Audit run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Parent report: `35_sbom_license_policy.md` (findings SBOM-P1-001 … SBOM-P3-002)
- Applies to: `falcon-build`, `falcon-edge-build`, the edge image pipeline, and the edge/central delivery sets.
- Owner constraint: **license-free stack** (no paid/commercial licenses) — per `docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md` and the phase-8 license-free amendment.

## Evidence Reviewed

- `falcon-edge-build/docs/security/DEPENDENCY_POLICY.md` (principles §1/§3/§7; CI enforcement "future" list)
- `falcon-edge-delivery/falcon-edge-sensor-2026.09.30-lab8-sbom.cdx.json` (0/636 license fields), `…lab7-sbom.cdx.json`, lab6 SBOM
- `falcon-build/sbom/*.cdx.json` + `vuln-summary.csv` + `pins/images.lock` (no license fields)
- `falcon-build/docs/phase8/review-package-extras/OWNER_ACCEPTANCE.md` (license-free row, DD-15), `docs/phase8/CLOSEOUT.md` (license-free amendment), `ledgers/exception_register.md` (EX-11/EX-12)
- `falcon-edge-build/.github/workflows/{validate,bake-image}.yml`, `falcon-build/.github/workflows/validate.yml`, both `.github/dependabot.yml`

## Verification Performed

| Evidence | Type | Result |
|---|---|---|
| Lab8 SBOM license-field count | execution (json parse) | 0 of 636 components carry license data |
| Central SBOM license-field counts | execution (json parse) | Partial (0/49 node-exporter, 0/441 prometheus, 18/378 traefik); `repo.cdx.json` 0 components |
| Workflow grep for license/SBOM/vuln gates | inspection | None present; edge policy lists them as future enforcement |
| License decision records | inspection | Owner acceptance + exception prose only; no allow/deny list or register entries mapped to components |

## 1. Objective

Give the program a machine-enforceable license-free policy so that a future image, dependency, or base-image change cannot silently introduce a paid, proprietary, or unlicensed component, and so that any accepted deviation is recorded and expires.

Current state (evidence in the parent report): no license fields in the edge SBOM (0/636 components), partial/absent license data in central SBOMs, no license gate in either CI, "license check" listed only as future enforcement in `docs/security/DEPENDENCY_POLICY.md`.

## 2. Policy: allow / review / deny

### Allow (no review needed)

| License family | Notes |
|---|---|
| MIT, ISC, BSD-2-Clause, BSD-3-Clause, 0BSD | Permissive |
| Apache-2.0 | Includes patent grant; used by OpenSearch and much of the stack |
| MPL-2.0 | File-level copyleft; used by Vector and RabbitMQ |
| LGPL-2.1/3.0 (dynamic linking) | e.g. system libraries, IRIS components — accept for self-hosted service use |
| GPL-2.0/3.0, AGPL-3.0 (self-hosted, no redistribution of the combined product) | e.g. Suricata, ntfy, ntopng Community, Redis 8.x; internal use is compliant. Flag for review if the program ever redistributes a combined work |
| CC-BY-4.0 / public-domain data | e.g. DB-IP Lite (attribution required); GeoLite data must not be used |
| Proprietary-but-free-of-charge firmware blobs distributed with Raspberry Pi OS | Accept for the lab; record in the baseline as "vendor firmware, no fee, redistribution limited" |

### Review required (time-boxed owner decision)

- CC-BY-SA, CDDL, EPL-2.0 — reciprocal terms; usually acceptable self-hosted.
- Any license with a field-of-use, non-commercial, or revenue threshold clause.
- Any component whose license cannot be determined from the SBOM (`NOASSERTION`, empty).

### Deny

- Paid licenses / license keys: **ntopng Enterprise**, **nProbe**, **MaxMind GeoIP2** (commercial), Elastic-licensed components, Grafana Enterprise plugins, any "contact sales" component.
- SSPL/BSL-style licenses **if** the program later redistributes the stack (Redis pre-8, MongoDB) — current Redis 8.x is AGPLv3 and allowed.
- "All rights reserved" without an OSS license and without an accepted exception.

Note: current stack checks — OpenSearch/Dashboards (Apache-2.0), Traefik (MIT), Prometheus/node-exporter (Apache-2.0), Grafana (AGPL-3.0; self-hosted allowed, redistribution triggers obligations), redis 8.8.2 (AGPLv3), Vector (MPL-2.0), Suricata (GPL-2.0), ntfy (GPL-2.0), cadvisor (Apache-2.0), IRIS (LGPL/MIT mix), RabbitMQ (MPL-2.0), OpenCanary (BSD), ntopng Community (GPL-3.0), DB-IP Lite (CC BY 4.0). All fit "license-free" for self-hosted internal use.

## 3. SBOM requirements (so the policy has data)

1. Generate one CycloneDX 1.5+ SBOM per shipped artifact at release time:
   - Central: every image in `pins/images.lock` **and** the review-package tree (`sbom/repo.cdx.json` currently has 0 components).
   - Edge: the sensor image rootfs **and** the update bundle (`falcon-agent-0.1.1-lab.tar.gz`), not just dpkg metadata.
2. Every SBOM must include: `metadata.tools` (name+version), image/file hashes, `licenses` per component (SPDX expression or `LicenseRef-*`), and the image digest it describes.
3. Include SBOMs in the delivery/review set (central `build_review_package.sh` currently deletes `*.cdx.json`) or record the exclusion as an explicit policy decision with a compensating scan.
4. Keep the existing hash binding (edge manifest `sbom.sha256` and `metadata.component.hashes` match the shipped image — verified).
5. Suggested tooling: syft (`-o cyclonedx-json`) for files+licenses, trivy `--scanners license,vuln` for the gap scan; keep trivy pinned + checksum-verified as `install-trivy.sh` already does.

## 4. CI gates (both repos)

| Gate | Trigger | Behavior |
|---|---|---|
| SBOM coverage | release/publication | fail if any shipped artifact lacks an SBOM or hashes disagree |
| License policy | PR + release | parse SBOMs, compare component licenses to the allow/deny list; fail on deny or unknown without a register entry |
| Exception check | PR + release | fail if a register entry is expired, unowned, or missing its component |
| Vulnerability threshold (DD-15) | schedule + release | fail internet-facing images on any HIGH/CRITICAL; internal images per owner threshold, with unfixed findings reviewed each patch window |
| Base image drift | weekly (edge already has `check_upstream_drift.sh`) | extend to also verify the pinned Pi OS checksum and flag registry digest changes for locked images |
| Tool integrity | every CI run | verify checksums of downloaded CI tools (actionlint, shellcheck, ruff, gitleaks) — see SC-P2-004 |
| Release binding | publication | fail if any `.sha256` sidecar is stale, if the repomix pack predates the package commit, or if artifacts changed after signing |

Implementation notes:
- Central: add a `license_policy.py` + `pins/licenses.allow` and call it from `ci/validate.py`; keep the manual scan scripts as the data producer.
- Edge: implement the "future enforcement" items already listed in `docs/security/DEPENDENCY_POLICY.md:35-36`; add the same gate to `ci/validate.sh` and the `validate` workflow.

## 5. Docker and GitHub Actions dependencies

- Docker images: digest-pin everywhere (already true) and add a `license` field + `license_source` to each `pins/images.lock` entry, generated by the license scan.
- Dockerfile builds (`compose/central/opensearch-s3.Dockerfile`): record the base digest and the plugin name/version; a plugin that is not in the allow list blocks the build.
- GitHub Actions: keep 40-hex SHA pins + Dependabot (already true); record the action's license only if it is ever run on untrusted input or vendored; checksum-verify every tool download (SC-P2-004).
- Base OS: record the Raspberry Pi OS image license profile (mostly Debian OSS + vendor firmware blobs) once in the baseline exception list.

## 6. Exception process

Create a `license_exceptions` table (extend `ledgers/exception_register.md`):

| Field | Meaning |
|---|---|
| component | name + version + purl (or image digest) |
| license | SPDX or `LicenseRef-*` |
| reason | why it is required |
| compensating controls | isolation, no redistribution, attribution page, etc. |
| owner / date | who accepted |
| expiry | review at each patch window (max 12 months) |
| evidence | SBOM path + scan artifact |

Map the existing acceptances into it: EX-11 (ntopng community/digest-pin), EX-12 (DB-IP Lite replaces MaxMind), the license-free amendment, and DD-15 (vulnerability threshold).

## 7. Baseline actions (start here)

1. Record the current stack licenses once (18 images + edge image + Pi OS base) as `pins/licenses.baseline.md`; confirm all are allow/review, not deny.
2. Add license collection to `sbom-and-vuln.sh`/`vuln-summary.sh` (add `--scanners license`) and to edge `build_sbom.py` (or replace with syft).
3. Add the license-policy gate to `ci/validate.py` / `ci/validate.sh` with the allow list from §2.
4. Fix the release-binding gaps first (stale manifest sidecar; non-portable SBOM checksum) so the gate can trust digests.
5. Publish the ed25519 public key so an external reviewer can verify the SBOM-to-artifact binding independently.

## 8. Acceptance criteria

- A PR that adds `ntopng Enterprise` (or any deny-list component) fails CI with a clear message.
- Every shipped artifact has an SBOM with license data and a matching hash.
- A verifier with only the delivered files can verify the signature, every digest, and the license disposition of every component.
- The license-free owner requirement is demonstrably enforced, not merely documented.
