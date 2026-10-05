# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

SBOM and licence posture: CycloneDX SBOM generated per CI run with the lockfile-pinned tool and uploaded as a commit-bound 90-day artifact; an offline production licence allow-list is merge-gating (license-assurance.mjs). Residual: the SBOM lives only as a CI artifact and is not bound to the signed release identity/images.

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P3-001 | P3 | SBOM is a 90-day CI artifact, not bound to the release attestation |
