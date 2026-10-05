# Changelog draft — snowride @ `38b34a9`

Companion artifact for `40_release_notes_changelog_generator.md`. Append-only
lineage; the canonical file is `CHANGELOG.md`.

## [Unreleased]

### Security / supply chain

- Detached owner-signature verification for the launch gate (config.ts).
- Production dependency audit blocking; `@grpc/grpc-js` 1.14.5 override.
- gitleaks repo scan in CI with rule-scoped allowlists.
- Container bases digest-pinned; app images non-root, read-only.

### Operations

- Version-controlled assurance crontab and restart-safe LiveOps publish
  override.
- README validation-scope bounded claim and multi-engine e2e (chromium/
  firefox/webkit for mobile/a11y journeys).

### Audit

- Published run `20261003-0018-main-59e12b9` (46 findings) and focused run
  `20261004-0700-main-d79d0d7` (10 findings).
- This run `snowride-20261005-full-main-38b34a9` (42 findings, full-domain).

_Generated manually; an automated changelog generator is recommended
(`REL-P3-001`)._
