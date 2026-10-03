# Remediation PR — PS-02 Licensing & provenance

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Adds the licensing and provenance metadata `buddy` was missing. The repository had no `LICENSE`
and no `NOTICE`, so downstream use was legally undefined, and the large vendored prompt pack under
`docs/prompts/` had no recorded provenance or classification. This PR adds an explicit
`LICENSE` (an **all-rights-reserved / pending-decision placeholder** — it does **not** choose a
license), a `NOTICE` for ownership and vendored-content attribution, and `docs/README.md` to index
the docs tree and classify the prompt pack's provenance.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-02` — Licensing & provenance
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `594dcddb50ca2b6f7b5053e4833e1d324a444250`
- Branch: `remediation/ps-02-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SUPPLY-P1-001` | P1 | open -> partially-fixed | `LICENSE` added and `NOTICE` records ownership, so rights are no longer *undefined*. The file deliberately does **not** grant a license: the target license is a maintainer/legal decision and is recorded as an open question below. |
| `SUPPLY-P2-003` | P2 | open -> partially-fixed | `docs/README.md` classifies the vendored prompt pack (role, unconfirmed authorship/licensing, originality constraint) and `NOTICE` records the attribution requirement. Confirmation of authorship/license still needs a maintainer/legal sign-off. |

### Why the license is not chosen here

`package.json` has no `license` field, there is no root `README`, and the run's own executive
summary lists "Public OSS vs private product?" as an open maintainer decision. Sibling repos in the
org use conflicting licenses (`mainecybertech` ISC, `chat` MIT, `snowride` proprietary), so no
default can be inferred. Per the remediation guardrail ("record an open question instead of
guessing"), this PR documents the current, all-rights-reserved status and defers the actual license
choice to the maintainer/legal owner. It adds **no** guessed open-source license text.

## Changes

| File | What changed |
|---|---|
| `LICENSE` (new) | `LICENSE - PENDING`: states that no license is granted, all rights are reserved by default, and the final license is an open decision under `SUPPLY-P1-001`. Explicitly not a final license. |
| `NOTICE` (new) | Ownership (Copyright (c) 2026 Maine CyberTech), licensing status, vendored-content provenance (`SUPPLY-P2-003`), dependency-license pointer. Carries no license grant. |
| `docs/README.md` (new) | Docs index; prompt-pack provenance classification (role, authorship/licensing unconfirmed, originality constraint, no external redistribution pending confirmation); licensing status. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---:|---|
| `npm ci && npm run lint && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `594dcdd`) | 0 | `remediation/PS-02/verify.log` — lint clean; 5 files / 109 tests passed; `__VERIFY_EXIT=0` |
| `test -f LICENSE && test -f NOTICE && test -f docs/README.md && git ls-files ... && grep -l SUPPLY-P2-003 ...` | lab: `ci-runner` | 0 | `verify.log` — all three files present and tracked; provenance text found |
| `git archive HEAD \| tar -x -C /tmp/glscan-ps02 && gitleaks detect --no-git --redact --source /tmp/glscan-ps02 -v` | lab: `ci-runner` | 0 | `verify.log` — scanned ~257 KB; no leaks found |
| `npm run lint` | local (Windows, node v24.19.0) | 0 | No ESLint warnings or errors |
| `npm run test` | local (Windows, node v24.19.0) | 0 | 5 files / 109 tests passed |

- Secret scan (gitleaks): **pass** on tracked repository content at the commit, exit 0, no leaks.
- Scope check (files within patch set): **pass** — only `LICENSE`, `NOTICE`, `docs/README.md`
  (the PS-02 file set). No runtime code, dependency, or config changes.
- GitHub license detection: not asserted. Because the license is intentionally undecided, GitHub
  will not show a recognized license badge until the maintainer publishes a final `LICENSE`.

## Evidence bundle

- `remediation/PS-02/diff.patch` — SHA-256 `da7e426187d24760be89d0ee7727450f2f0a7e57901db078d658525b2fb4ac21`
- `remediation/PS-02/manifest.json`
- `remediation/PS-02/verify.log` — SHA-256 `383abcc6a7a3b9ad32f64bb5180e1d08a4aa1a2109b9d2bc779151105e84bfc6`

## Risk and rollback

- Risk: **low**. Documentation/metadata only; no runtime behavior, build, or dependency changes.
  The `LICENSE` is an explicit placeholder that grants nothing, so it cannot relax any existing
  restriction, and it is trivially replaced once the license is decided.
- Rollback: `git revert 594dcdd`.

## Open questions / reviewer actions

1. **Choose the target license (blocking the P1).** Decide *public OSS vs private product*, then
   replace the `LICENSE - PENDING` placeholder with the final license text (for example MIT or
   Apache-2.0 for open source, or a proprietary license) and add the matching `"license"` field to
   `package.json`. This is the only reason `SUPPLY-P1-001` is not fully fixed here.
2. **Confirm prompt-pack authorship and license.** Confirm whether
   `docs/prompts/buddy_virtual_pet_v2_complete_prompt_pack/` was authored in-house and under what
   terms; record the decision and update `docs/README.md` / `NOTICE` accordingly. Until then it is
   classified as all-rights-reserved / do-not-redistribute.
3. **Should the prompt pack ship in the release artifact at all?** If its provenance cannot be
   confirmed, consider removing it from the distribution (tracked separately with `INV-P3-001`).

## Review checklist

- [ ] Diff touches only the patch-set files (`LICENSE`, `NOTICE`, `docs/README.md`)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean on tracked content
- [ ] Rollback is practical
- [ ] License decision recorded by the maintainer/legal owner (open question 1)

## Definition of done (for this set)

`LICENSE` present and referenced from docs; prompt-pack provenance documented. *README reference
and GitHub license detection depend on the maintainer's license choice; the placeholder makes the
current status explicit so the repository is not silently unlicensed.*
