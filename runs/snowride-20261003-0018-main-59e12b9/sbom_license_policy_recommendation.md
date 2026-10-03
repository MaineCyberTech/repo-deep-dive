# SBOM & License Policy Recommendation — Snowride

## Current state

- Lockfile committed (`package-lock.json`, lockfileVersion 3).
- CycloneDX tooling (`@cyclonedx/cyclonedx-npm`) is a devDependency but no SBOM artifact exists for HEAD (SUPPLY-P1-001).
- License assurance runs via `scripts/license-assurance.mjs` only in the daily host lane (`scripts/assurance/assurance.sh`), not CI (SUPPLY-P2-001).
- Repo is proprietary (`LICENSE`); third-party notices in `evidence/THIRD_PARTY_NOTICES.md`.

## Recommendation

1. **Generate SBOM per release**: `npx @cyclonedx/cyclonedx-npm --output-format json --output-file sbom.cdx.json` (and optionally SPDX); commit/attach to the release and to CI artifacts.
2. **Enforce license policy in CI**: run `license-assurance.mjs` on PRs touching `package-lock.json`; fail on disallowed licenses (copyleft/unknown) per an explicit allowlist.
3. **Vulnerability policy**: `npm audit --omit=dev` + OSV scan on PRs; block on high/critical with a documented exception register entry for accepted risk.
4. **Provenance**: require npm registry signatures where feasible; document the `allowScripts` entries and why each is needed.
5. **Bind to commit**: every artifact records `git rev-parse HEAD`; a redeploy without a fresh artifact fails the release gate.

## Acceptance criteria

- `sbom.cdx.json` exists for each release and validates against the CycloneDX schema.
- A planted disallowed dependency/secret fails CI on a test branch.
