# SBOM / licence policy recommendation — snowride @ `38b34a9`

Companion artifact for `35_sbom_license_policy.md`.

## Current state

- CycloneDX SBOM is generated in CI with the lockfile-pinned
  `@cyclonedx/cyclonedx-npm` (`--no-install`) and uploaded as the commit-bound
  artifact `sbom-<sha>` with 90-day retention.
- The production licence allow-list is a blocking merge gate
  (`scripts/license-assurance.mjs`, `.github/workflows/supply-chain.yml`).
- Registry signature verification (`npm audit signatures`) is advisory due to
  `EMISSINGSIGNATUREKEY` for `@playwright/test@1.63.0`.

## Recommendations

1. **Durable binding.** Publish the SBOM to a durable release location and bind
   its hash into the launch-attestation identity, so an inventory survives the
   90-day CI window (`SBOM-P3-001`).
2. **Promote provenance.** Time-box the signature-advisory posture and promote
   `npm audit signatures` to blocking once the upstream attestation issue
   clears (`SC-P3-001`).
3. **Doc currency.** Reconcile `docs/SUPPLY_CHAIN.md` with the blocking posture
   already shipped (`SC-P2-001`).
