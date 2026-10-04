# Roadmap

- SEC-P2-001 (P2) - gitleaks curl-auth-user allowlist is unanchored and suppresses every curl line
- SEC-P2-002 (P2) - Retired DFIR-IRIS API key literal still committed in vendored scripts; rotation PENDING
- SEC-P2-003 (P2) - All 20 inherited credentials are PENDING rotation; vendored scripts source credential files wholesale
- DEP-P2-001 (P2) - Dependabot covers only GitHub Actions; Python dependencies and container images are unmanaged
- SUPPLY-P2-001 (P2) - Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1)
- CI-P2-001 (P2) - Branch protection and required checks are plan-gated, so validate is advisory
- PORT-P3-001 (P3) - 90 tracked shell scripts lack the executable bit
- PORT-P3-002 (P3) - CRLF committed in four markdown files despite text eol=lf
- GIT-P3-001 (P3) - No LICENSE file
- SUPPLY-P3-001 (P3) - Vendored mct/compose images are unpinned under a blanket waiver
- SUPPLY-P3-002 (P3) - Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers
- SUPPLY-P3-003 (P3) - Image/SBOM-component license allow/deny gate is not enforced
- CI-P3-001 (P3) - dependabot-merge merges without pinning the checked commit and holds broad write scope
- CONF-P3-001 (P3) - SBOM coverage doc contradicts the live validate workflow on --require-vuln
