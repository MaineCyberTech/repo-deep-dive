# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

release.yml generates a CycloneDX SBOM per tag (`npm sbom`) and attaches provenance, which is strong. There is no committed SBOM artifact and no license policy: the CI license step is a placeholder echo, and LICENSE reports NOASSERTION (proprietary, all rights reserved pending a decision).

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P3-001 | P3 | No license policy and no committed SBOM artifact |
