# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

<!-- One paragraph: which patch set and what it fixes. -->

- Audit run: `<run>`
- Patch set: `PS-00N` — <title>
- Repo / base: `<repo>` @ `<base sha>`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `AREA-P1-001` | P1 | open -> fixed | |

## Changes

| File | What changed |
|---|---|

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| | | | `remediation/PS-00N/verify.log` |

- Secret scan (gitleaks): <pass/fail, evidence>
- Scope check (files within patch set): <pass/fail>

## Evidence bundle

- `remediation/PS-00N/diff.patch` — SHA-256 `<sha>`
- `remediation/PS-00N/manifest.json`
- `remediation/PS-00N/verify.log`

## Risk and rollback

- Risk: <low/medium/high + why>
- Rollback: `git revert <sha>` / feature flag / config revert

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

<!-- from patch_plan.md -->
