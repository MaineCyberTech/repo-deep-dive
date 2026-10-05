# SBOM and License Policy Recommendation

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Findings: `SBOM-P3-001`, `SC-P2-003`

## Current state

- `release.yml` generates a CycloneDX SBOM per tag via `npm sbom --sbom-format cyclonedx` and
  attaches it to the GitHub Release with build-provenance attestation. This is strong.
- No SBOM is committed to the repository, so releases cannot be diffed in-tree.
- The CI "License policy" step is a placeholder `echo`
  (`.github/workflows/ci.yml`, references `buddy-SUPPLY-002`).
- `LICENSE` reports `NOASSERTION`; the project is proprietary/all-rights-reserved pending a
  decision (`docs/README.md:92-97`).
- The vendored prompt pack's authorship/licensing is unconfirmed (`SC-P2-003`).

## Recommendation

1. **License policy** — define an allow/deny list for direct + transitive licenses and enforce
   it in CI (e.g. `license-checker` / `npm sbom` + a policy script). Replace the placeholder.
2. **SBOM retention** — commit or link each release's `sbom.cdx.json` (or upload to a
   long-lived artifact store) so dependency changes are reviewable release-to-release.
3. **Provenance** — keep the existing `attest-build-provenance` step; document how consumers
   verify the attestation.
4. **Proprietary note** — until the license decision is made, ensure the NOTICE/all-rights
   reserved text is consistent, and do not distribute the vendored prompt pack.

## Exit criteria

A passing license-policy check in CI and an accessible SBOM per release.
