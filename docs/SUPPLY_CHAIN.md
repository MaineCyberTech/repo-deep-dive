# Supply chain, license, and SBOM policy

This page records how the **repo-deep-dive** pack itself handles provenance,
licensing, and its own dependencies. It applies the pack's own prompt 35
(`prompts/35_sbom_license_policy.md`) to the pack.

## Dependency inventory

| Component | Where | Pin | Notes |
|---|---|---|---|
| Python tools | `tools/*.py` | standard library only | no third-party Python packages |
| Shell tools | `tools/*.sh` | bash | coreutils/bash only |
| GitHub Actions | `.github/workflows/*.yml`, `ci/audit.yml` | full commit SHA + `# vX.Y.Z` | re-pinned after the PR #33/#35 regression (**SUPPLY-P1-001**) |
| Downloaded scanners | `.github/workflows/deep-dive-deterministic.yml` | versioned releases | checksum-verify downloads (SUPPLY-P1-001) |

Because the pack ships no `package.json`, lockfile, container image, or published
binary, there is **no build artifact to attach an SBOM to**. That is a
deliberate N/A, not an omission:

- **SBOM (pack):** N/A — the pack is source (Markdown + Python stdlib + bash).
  If a package dependency is ever added, an SPDX/CycloneDX SBOM step and an
  allow-list (`LicenseRef-Proprietary` fails the build) must be added to CI in
  the same change.
- **SBOM (targets):** required output of prompt 35 for every audited repository;
  see `examples/*.json` for the expected artifact name
  (`sbom_license_policy_recommendation.md`).

## License status

- The repository currently ships **no chosen license**; `LICENSE` records the
  pending **all-rights-reserved** status so the pack is not mistaken for one
  that grants reuse rights.
- Choosing the final license (open-source, proprietary/internal-only, or
  otherwise) is a product/legal decision and is tracked as an **open question**
  under finding **SUPPLY-P3-004** (audit run `20261003-0018-main-7bac320`).
- Third-party components (GitHub Actions, `actionlint`, `gitleaks`, GitHub CLI)
  retain their own upstream licenses; none are vendored into this repository.
- Sibling MaineCyberTech repositories are not consistent (`mainecybertech` ISC,
  `chat` MIT, `snowride` proprietary), which is exactly why the pack does not
  guess a license here.

## CI pinning (SUPPLY-P1-001 — regressed then re-fixed)

Workflow `uses:` references and downloaded scanner binaries are pinned by
commit SHA and version+sha256 under finding **SUPPLY-P1-001** (patch set PS-003),
with **SUPPLY-P2-002** adding `.github/dependabot.yml` for `github-actions`.
Those edits live in `.github/` and are intentionally not duplicated here.

**Regression (2026-10-04).** The PS-003 pinning was reverted piecemeal after it
landed: PR #33 (`ci-gate-23`) restored the four `.github/workflows/audit.yml`
refs to mutable tags (`actions/checkout@v4`, `actions/setup-python@v5`), PR #35
re-added `actions/checkout@v4` unpinned in `.github/workflows/pack-digest.yml`,
and `ci/audit.yml` (which the original finding `SUPPLY-P1-001` explicitly cited at
lines ~43/56/77) had never been pinned. The post-merge re-audit
(`20261004-0700-main-49f46a8`, `SUPPLY-P2-001`) flagged the regression.

**Fix.** Every external `uses:` in `.github/workflows/*.yml` and `ci/audit.yml`
is re-pinned to a full 40-hex commit SHA with a trailing `# vX.Y.Z` comment:
`actions/checkout` v4.4.0, `actions/setup-python` v5.6.0, and
`actions/upload-artifact` v4.6.2. Dependabot keeps the pins current.

## Portability: org / repository identifiers (SEC-P3-005)

The scheduled workflow currently defaults `org` to `MaineCyberTech` and
`exclude` to `soc,infra,AWS-WWW,www,www-dev`
(`.github/workflows/deep-dive-deterministic.yml`). Those defaults leak internal
structure and make the pack non-portable. Until they move to repository
variables or a config file, **override them explicitly** when running the
workflow (`workflow_dispatch` inputs):

- `org` — target GitHub organization (default `MaineCyberTech`)
- `repos` — comma-separated repo names (blank = all org repos)
- `exclude` — comma-separated repos to skip
- `runner` — runner label (`ubuntu-latest` or a self-hosted label)
- `deep` — run hadolint/trivy checks

Removing the hardcoded literals is tracked under finding **SEC-P3-005**. This
page documents the override contract; the literal move to repository variables
or a config file is deferred because the same workflow file is being edited for
pinning under patch set PS-003, and the edits must not conflict.
