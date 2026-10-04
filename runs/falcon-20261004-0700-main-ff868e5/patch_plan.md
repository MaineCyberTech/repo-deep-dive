# Patch plan

## SEC-P2-001 - gitleaks curl-auth-user allowlist is unanchored and suppresses every curl line

Remove the line-scoped .*curl.* allowlist; allowlist by path/rule instead, or require the credential value to be a variable/$(cat ...) reference. Add a negative fixture with a literal curl credential that must still fail.

## SEC-P2-002 - Retired DFIR-IRIS API key literal still committed in vendored scripts; rotation PENDING

Confirm revocation with IRIS, then replace the literal in both scripts with a placeholder or a SHA-256 comparison; remove the ALLOW_VALUE_SHA256 entry and record name-only rotation evidence plus a negative test.

## SEC-P2-003 - All 20 inherited credentials are PENDING rotation; vendored scripts source credential files wholesale

Execute the documented rotation order with name-only evidence and negative tests; migrate the 28 scripts to single-key reads (automation/validation/lib/env_key.sh) or restrict them to the interactive account.

## DEP-P2-001 - Dependabot covers only GitHub Actions; Python dependencies and container images are unmanaged

Add pip/uv and docker ecosystems to .github/dependabot.yml, or add renovate.json with digest pinning, preserving the existing hash-pin policy for CI deps.

## SUPPLY-P2-001 - Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1)

Implement D1: owner-held ed25519/GPG signature over sbom/SBOM_MANIFEST.sha256 with the public key published and the manifest hash bound in PACKAGE_DIGEST.txt, or use GitHub artifact attestations (actions/attest-build-provenance).

## CI-P2-001 - Branch protection and required checks are plan-gated, so validate is advisory

Owner decision: upgrade to GitHub Pro/Team and apply the ready payload (BRANCH_PROTECTION.md:16-51), or record a per-merge attestation that validate was green and treat direct pushes as break-glass with the documented record.

## PORT-P3-001 - 90 tracked shell scripts lack the executable bit

git update-index --chmod=+x on intended entrypoints and add a CI check asserting exec bits on shebang-bearing scripts under automation/**.

## PORT-P3-002 - CRLF committed in four markdown files despite text eol=lf

git add --renormalize . for the affected .md files only; leave -text .out evidence captures untouched.

## GIT-P3-001 - No LICENSE file

Add a LICENSE or a proprietary review-only notice consistent with the owner decision; dependency licensing is separately covered by ci/license_check.py.

## SUPPLY-P3-001 - Vendored mct/compose images are unpinned under a blanket waiver

Scope the waiver to specific refs, add an explicit deploy-blocking guard for mct/compose, and remove or justify the docker.sock mounts.

## SUPPLY-P3-002 - Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers

Run automation/validation/vuln-summary.sh in the next patch window, refresh waivers to real dispositions, keep the DD-15 threshold, and add a scheduled scan job.

## SUPPLY-P3-003 - Image/SBOM-component license allow/deny gate is not enforced

Add pins/licenses.allow plus a check over sbom/*.cdx.json license fields (allow MIT/BSD/Apache/ISC; deny GPL/AGPL/LGPL/SSPL unless the documented self-hosted exception applies).

## CI-P3-001 - dependabot-merge merges without pinning the checked commit and holds broad write scope

Add --match-head-commit to gh pr merge and scope permissions to the minimum; extend the ci_governance_guard_test.sh guard to pin the new flag.

## CONF-P3-001 - SBOM coverage doc contradicts the live validate workflow on --require-vuln

Append a dated correction section (append-only) stating --require-vuln --vuln-waivers is live and naming the waiver file as the compensating control.

