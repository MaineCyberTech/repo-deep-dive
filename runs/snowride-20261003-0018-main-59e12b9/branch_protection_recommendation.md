# Branch Protection Recommendation — Snowride

## Finding

CI-P1-001: no evidence in the repository that `main` is protected or that `ci-foundation` is a required check. The workflow triggers on `push` and `pull_request` but nothing enforces it.

## Recommended settings for `main`

- Require a pull request before merging (≥1 approval; CODEOWNERS review for `supabase/migrations`, `infra/`, `evidence/`, `.github/`).
- Require status checks to pass: `foundation`, `migrations`, `e2e` (jobs in `ci-foundation.yml`).
- Require branches to be up to date before merging.
- Require conversation resolution.
- Restrict force pushes and deletions.
- Optionally require signed commits/tags for release tags.

## Evidence to capture

- Branch-protection settings export (JSON via GitHub API, or screenshot) stored under `evidence/`.
- A test PR demonstrating a failing required check blocks merge.

## Notes

- `.github/CODEOWNERS` currently maps `*` to `@MaineCyberTech`; the file itself notes it should move to a team handle if the repo moves under an org.
- Only the two workflow actions need SHA pinning (CI-P2-002) for the checks to be trustworthy.
