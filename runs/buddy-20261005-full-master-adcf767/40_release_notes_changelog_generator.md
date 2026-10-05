# 40_release_notes_changelog_generator — Prompt 40 - Release Notes and Changelog Generator

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `40_release_notes_changelog_generator.md` (area REL, prompt)

## Verification Performed

release.yml generates a per-release `CHANGELOG-RELEASE.md` bound to the tag/commit; the repo also keeps a Keep-a-Changelog `CHANGELOG.md`. No finding: the generator exists and the manual changelog is present. Release notes are produced at publish time, not committed, which is consistent with the tag-driven process.

## Findings

_No findings in this domain._
