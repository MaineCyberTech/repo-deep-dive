# Security Policy

This repository is the **repo-deep-dive** audit/remediation pack: prompts,
lenses, profiles, templates, docs, and small Python/bash tooling. It ships no
runtime service and no package dependencies, but vulnerabilities in the tooling
or in committed content (for example a leaked secret in an archived run) are in
scope.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately**, using GitHub private
vulnerability reporting for this repository:

1. Go to the repository's **Security** tab → **Report a vulnerability**
   (<https://github.com/MaineCyberTech/repo-deep-dive/security/advisories/new>).
2. Include: affected path/version, impact, reproduction steps, and any suggested
   fix. Redact secret values; reference path and secret type only.

Do **not** open a public issue for a suspected vulnerability, and do not include
live credentials or personal data in a report.

## What not to do

- Do not run destructive or state-mutating tooling found in the repo
  (`prompts/00_SHARED_AUDIT_RULES.md`).
- Do not commit secrets. Every remediation diff is expected to pass a
  `gitleaks` scan before push.

## Response

Reports are triaged by the pack maintainers on a best-effort basis. Findings are
tracked in the audit run's `follow_up_register.md` with one of the standard
statuses (`open`, `partially-fixed`, `verified-fixed`, `still-open`,
`regressed`, `owner-accepted`). A finding is only `verified-fixed` with an
artifact captured at the fixing commit.

## Supported versions

The pack is developed on `main`. Only the current `main` (and the latest tagged
`VERSION`) is supported; older archived runs are historical records and are not
patched in place.

## Related

- `docs/SUPPLY_CHAIN.md` — license and SBOM policy.
- `runs/README.md` — sensitivity of archived run content.
- `.github/CODEOWNERS` — review ownership (tracked separately; see finding
  SEC-P3-004).
