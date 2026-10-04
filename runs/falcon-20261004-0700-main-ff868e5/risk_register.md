# Follow-up register

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| SEC-P2-001 | P2 | gitleaks curl-auth-user allowlist is unanchored and suppresses every curl line | @owner | SEC | verified-fixed | merged #34 @ bc58e7e |
| SEC-P2-002 | P2 | Retired DFIR-IRIS API key literal still committed in vendored scripts; rotation PENDING | @owner | SEC | verified-fixed | merged #37 @ a146ae0 |
| SEC-P2-003 | P2 | All 20 inherited credentials are PENDING rotation; vendored scripts source credential files wholesale | @owner | SEC | verified-fixed | merged #38 @ 01c176a |
| DEP-P2-001 | P2 | Dependabot covers only GitHub Actions; Python dependencies and container images are unmanaged | @owner | DEP | open | Add pip/uv and docker ecosystems to .github/dependabot.yml, or add renovate.json with digest pinning, preserving the exi |
| SUPPLY-P2-001 | P2 | Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1) | @owner | SUPPLY | open | Implement D1: owner-held ed25519/GPG signature over sbom/SBOM_MANIFEST.sha256 with the public key published and the mani |
| CI-P2-001 | P2 | Branch protection and required checks are plan-gated, so validate is advisory | @owner | CI | open | Owner decision: upgrade to GitHub Pro/Team and apply the ready payload (BRANCH_PROTECTION.md:16-51), or record a per-mer |
| PORT-P3-001 | P3 | 90 tracked shell scripts lack the executable bit | @owner | PORT | open | git update-index --chmod=+x on intended entrypoints and add a CI check asserting exec bits on shebang-bearing scripts un |
| PORT-P3-002 | P3 | CRLF committed in four markdown files despite text eol=lf | @owner | PORT | open | git add --renormalize . for the affected .md files only; leave -text .out evidence captures untouched. |
| GIT-P3-001 | P3 | No LICENSE file | @owner | GIT | open | Add a LICENSE or a proprietary review-only notice consistent with the owner decision; dependency licensing is separately |
| SUPPLY-P3-001 | P3 | Vendored mct/compose images are unpinned under a blanket waiver | @owner | SUPPLY | open | Scope the waiver to specific refs, add an explicit deploy-blocking guard for mct/compose, and remove or justify the dock |
| SUPPLY-P3-002 | P3 | Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers | @owner | SUPPLY | open | Run automation/validation/vuln-summary.sh in the next patch window, refresh waivers to real dispositions, keep the DD-15 |
| SUPPLY-P3-003 | P3 | Image/SBOM-component license allow/deny gate is not enforced | @owner | SUPPLY | open | Add pins/licenses.allow plus a check over sbom/*.cdx.json license fields (allow MIT/BSD/Apache/ISC; deny GPL/AGPL/LGPL/S |
| CI-P3-001 | P3 | dependabot-merge merges without pinning the checked commit and holds broad write scope | @owner | CI | open | Add --match-head-commit to gh pr merge and scope permissions to the minimum; extend the ci_governance_guard_test.sh guar |
| CONF-P3-001 | P3 | SBOM coverage doc contradicts the live validate workflow on --require-vuln | @owner | CONF | open | Append a dated correction section (append-only) stating --require-vuln --vuln-waivers is live and naming the waiver file |
