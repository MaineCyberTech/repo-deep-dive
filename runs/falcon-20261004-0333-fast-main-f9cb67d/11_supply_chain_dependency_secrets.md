# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `falcon-20261004-0333-fast-main-f9cb67d`
- Target: `falcon` @ `f9cb67d` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

Read-only review of the supply-chain surface at `f9cb67d`: `.github/dependabot.yml`, `.github/workflows/validate.yml` (SBOM/provenance steps), `pins/supply-chain-waivers.json`, `pins/images.lock`, and `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md`.

- `validate.yml:103-113` runs `sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json`, `sbom_hashes.sh verify`, and the publication-chain/digest gates every run.
- `pins/supply-chain-waivers.json` carries a blanket `mct/compose` digest waiver (`ref: "*"`) and twelve `vuln_scan_pending` images, all `review_by 2026-12-31`.
- `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` states the artifacts are SHA-256 integrity bindings; none is cryptographically signed (SLSA ~0-1).

No secrets were printed.

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-001 | P2 | Dependabot covers only GitHub Actions; Python CI deps and container images are unmanaged |
| SC-P2-002 | P2 | Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1) |
| SC-P3-001 | P3 | Vendored mct/compose images are unpinned under a blanket waiver |
| SC-P3-002 | P3 | Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers |
| SC-P3-003 | P3 | Image/SBOM-component license allow/deny gate is not enforced |
