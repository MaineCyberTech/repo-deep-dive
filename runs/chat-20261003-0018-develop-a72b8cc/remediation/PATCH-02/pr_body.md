# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Removes the tracked E2E credential file `test-signin.json` from version control and from
the working tree, ignores local credential variants while keeping the
`test-signin.example.json` template tracked, and documents the required rotation in
`SECURITY.md`. The file contained a plaintext E2E credential that was committed to the
repository and was not covered by `.gitignore`.

> **ACTION REQUIRED (out-of-band): the committed credential MUST be rotated.**
> This PR removes the file from the tracked tree but **cannot** rotate a leaked secret.
> A repository owner must invalidate/rotate the password through the identity provider
> (Supabase Auth) and, if deemed necessary, purge it from git history with
> `git filter-repo`. Treat the credential as compromised. The secret value is **never
> printed** in this PR or its evidence bundle.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-02` — Rotate/remove committed credential
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-002` | P1 | open -> partially-fixed | File untracked + deleted from the working tree and ignored. Rotation is a required human follow-up. |
| `SUPPLY-P1-001` | P1 | open -> partially-fixed | Credential removed from VCS; gitleaks diff gate clean. History purge/CI secret sourcing is a follow-up. |
| `INV-P2-002` | P2 | open -> partially-fixed | `test-signin.json` no longer tracked; `.gitignore` now covers local credential variants; template stays tracked. |

Statuses are `partially-fixed` until the out-of-band rotation is confirmed (a file removal
cannot itself close a "leaked credential" finding).

## Changes

| File | What changed |
|---|---|
| `test-signin.json` | Removed from version control (`git rm --cached`) and deleted from the working tree. Secret value not reproduced anywhere. |
| `.gitignore` | Added `test-signin*.json` and `!test-signin.example.json`, so local credential files are ignored while the committed template stays tracked. |
| `SECURITY.md` | Added a "Test credential files" note documenting local handling and the required remove/rotate/history-purge response if a credential is ever committed. |

Diff is 12 insertions, 1 deletion (the deleted line is the credential, intentionally
omitted from `diff.patch`).

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `git ls-files \| grep -c test-signin.json` | local + ci-runner | 0 (count = 0) | `remediation/PATCH-02/verify.log` |
| `Test-Path test-signin.json` after removal | local | n/a (False) | `remediation/PATCH-02/verify.log` |
| `git check-ignore -v test-signin.json` | ci-runner | 0 (ignored) | `remediation/PATCH-02/verify.log` |
| `git check-ignore -v test-signin.example.json` | ci-runner | 1 (not ignored — expected) | `remediation/PATCH-02/verify.log` |
| `gitleaks protect --staged --redact --exit-code 1` | ci-runner | 0 (no leaks) | `remediation/PATCH-02/verify.log` |
| `gitleaks detect --no-git --redact` (clean tracked tree) | ci-runner | findings set identical to base; 0 test-signin | `remediation/PATCH-02/verify.log` |
| `git diff --cached --name-status` (scope) | local | 0 | `D test-signin.json`, `M .gitignore`, `M SECURITY.md` |

- Secret scan (gitleaks): **diff gate pass** (`gitleaks protect --staged`: "no leaks found").
  The full working-tree `--no-git` scan is **not literally zero**: it reports pre-existing,
  unrelated findings (47 under generated `apps/web/.next/**` build caches; 5 in the clean
  tracked tree — JWTs in `.env.dev.example`/`validate.yml` and one keyboard-shortcut false
  positive). All of these exist identically at base `develop`; **none is `test-signin*`**.
  This is recorded honestly rather than asserted clean. A dedicated follow-up (rotate +
  history purge + CI secret sourcing) is required to fully close the findings.
- Scope check (files within patch set): **pass** — only `test-signin.json`, `.gitignore`
  (patch set) plus a `SECURITY.md` documentation note.
- Tests: not applicable to a file removal; no test files changed. The E2E suite already
  skips when `test-signin.json` is absent and reads `test-signin.example.json` as the
  template.

## Evidence bundle

- `remediation/PATCH-02/diff.patch` — SHA-256 `D7063AFC4D928C5333D86822572C01AB1440A2A94B16404497A6ABDC52F54054`
  (credential content intentionally omitted)
- `remediation/PATCH-02/manifest.json`
- `remediation/PATCH-02/verify.log`

## Risk and rollback

- Risk: low. Removes a committed credential and adds ignore rules; no runtime code changes.
  Requires no build. The deleted file was only a local E2E convenience; the template remains.
- Rollback: `git revert 3fc2091f6cea856e90d492220b926bbf0da73801` (note: reverting would
  re-introduce the exposed credential — do not revert without rotating first).

## Review checklist

- [ ] Diff touches only the patch-set files (+ docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks diff gate clean
- [ ] Rotation is tracked as an owner action (this PR cannot rotate)
- [ ] Rollback is practical

## Definition of done (for this set)

- `git ls-files | rg test-signin.json` empty — **done**.
- `gitleaks` diff gate passes — **done** (full-tree residual findings are pre-existing).
- Credential rotated out-of-band — **NOT DONE (required, owner action)**.
- History purge if required (`git filter-repo`) — **follow-up decision by owner**.
