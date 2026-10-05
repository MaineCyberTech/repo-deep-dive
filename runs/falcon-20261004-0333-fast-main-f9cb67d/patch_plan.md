# Patch plan

## CI-P2-001 — Branch protection and required checks are plan-gated, so `validate` is advisory

Owner decision D: upgrade to GitHub Pro/Team and apply the recorded payload, or per-merge attest that validate was green and treat direct pushes as break-glass.

## CI-P2-002 — Auto-merge workflow holds broad write scope and merges without pinning the checked commit

Add `--match-head-commit` to `gh pr merge`, scope permissions to the minimum, and add an environment/required-review gate to the auto-merge job.

## SC-P2-001 — Dependabot covers only GitHub Actions; Python CI deps and container images are unmanaged

Add pip/uv and docker ecosystems to `.github/dependabot.yml`, or add `renovate.json` with digest pinning, preserving the hash-pin policy for CI deps.

## SC-P2-002 — Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1)

Implement D1: an owner-held ed25519/GPG signature over `sbom/SBOM_MANIFEST.sha256` with the public key published and the manifest hash bound in `PACKAGE_DIGEST.txt`, or use GitHub artifact attestations.

## SEC-P2-001 — Public-facing routers rely only on Cloudflare Access; `ntfy-auth` is dead config

Add origin authentication to public routers (or record a testable owner acceptance); delete or wire `ntfy-auth`.

## SEC-P2-002 — All 20 inherited credentials remain PENDING rotation; 28 vendored scripts source credential files wholesale

Execute the documented rotation order with name-only evidence and negative tests; migrate the 28 scripts to single-key reads.

## DET-P3-001 — [DEP] trivy not installed (dependency vuln scan skipped)

Install trivy to enable the --deep dependency vulnerability scan.

## DET-P3-002 — [GIT] No LICENSE file

Add a license.

## DET-P3-003 — [SUPPLY] 58 container image(s) without a digest pin

Pin images by digest (`image@sha256:...`) for reproducible, tamper-evident deploys.

## DET-P3-004 — [SUPPLY] hadolint not installed (Dockerfile lint skipped)

Install hadolint to lint Dockerfiles in --deep mode.

## SC-P3-001 — Vendored mct/compose images are unpinned under a blanket waiver

Scope the waiver to specific refs, add an explicit deploy-blocking guard for mct/compose, and remove or justify the docker.sock mounts.

## SC-P3-002 — Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers

Run `automation/validation/vuln-summary.sh` in the next patch window, refresh waivers to real dispositions, and add a scheduled scan job.

## SC-P3-003 — Image/SBOM-component license allow/deny gate is not enforced

Add `pins/licenses.allow` plus a check over `sbom/*.cdx.json` license fields (allow MIT/BSD/Apache/ISC; deny GPL/AGPL/LGPL/SSPL unless the self-hosted exception applies).

