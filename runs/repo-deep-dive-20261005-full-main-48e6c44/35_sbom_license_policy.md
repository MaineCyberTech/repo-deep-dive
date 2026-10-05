# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `repo-deep-dive-20261005-full-main-48e6c44`
- Target: `repo-deep-dive` @ `48e6c44` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

The pack ships no runtime dependencies (stdlib-only Python), but it also publishes no SBOM or provenance for its own releases; it audits others' SBOMs.

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P3-001 | P3 | No SBOM/provenance artifact or release manifest is published for the pack itself |
