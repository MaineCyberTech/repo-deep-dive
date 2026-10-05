# Branch Protection and Required Checks Recommendation

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Findings: `BP-P1-001`, `BP-P1-002`, `CI-P1-001`, `CI-P2-001`

## Live state (verified via API, not docs)

| Control | Intended (docs/release-process.md) | Actual |
|---|---|---|
| `master` protected | required PR + review + status checks | **404 Branch not protected** |
| Repository rulesets | tag `v*` + master ruleset | **none** (`[]`) |
| `release` environment | required reviewers | **absent** (only `dev`, `development`) |
| CODEOWNERS review | required | file exists, not enforced |
| CI status check required | yes | **not required**; CI currently red |
| Dependency review (PR) | fail on high | job **skipped** (Dependency graph disabled) |
| Secret scanning / push protection | not stated | **disabled** |
| Dependabot security updates | weekly updates configured | **disabled** |

## Recommendation

1. **master ruleset** — require a pull request, require the `CI` status check (after
   `CI-P1-001` is green), require review from `.github/CODEOWNERS`, block force-push and
   deletion.
2. **`release` environment** — create it, add required reviewers, restrict to `v*` tags;
   verify a non-maintainer tag push waits for approval.
3. **Tag ruleset** — restrict `v*` creation, block deletion and force-push.
4. **Repository security** — enable Dependency graph, Dependabot alerts + security updates,
   and secret scanning with push protection.
5. **Verify** — from a non-maintainer account, confirm a direct push to `master` is rejected,
   a PR missing `CI` cannot merge, and a tag cannot publish without approval.

## Exit criteria

`gh api repos/MaineCyberTech/buddy/branches/master/protection` returns protection (or an
equivalent ruleset is listed), the `release` environment exists with protection rules, and a
verification attempt is recorded.
