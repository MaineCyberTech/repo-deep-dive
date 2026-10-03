<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Adds the missing **database change / deploy governance** policy the audit found
undocumented. CI has been a second, unversioned migration channel: the deploy
workflows posted raw SQL to the Supabase Management API, including an RLS policy
that widened `public.users` to `USING (true)` and seed users with a shared
password (audit findings `FINAL-P1-002`, `CI-P1-002`, `SEC-P0-001`). This PR
records the target state — migrations are the only schema/RLS channel, seed data
uses the protected seed workflow, and deploys perform no DDL/DML — and the exact
reviewer check that enforces it.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U07` — Unassigned FINAL findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (`develop`)
- Branch: `remediation/ps-u07-20261003-0018-develop-a72b8cc`
- Commit: `f4bcb403785130f14d73e644996266226af25add`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FINAL-P1-002` | P1 | open -> partially-fixed | The database change / deploy governance policy is now committed and cross-linked, with the reviewer check that keeps deploy workflows free of DDL/DML. The **workflow change itself is owned by `PATCH-01` (draft PR #56, `SEC-P0-001` / `CI-P1-002` / `DATA-P1-001`)** and is not duplicated here. The finding becomes `verified-fixed` only once the deploy workflows contain no `database/query` DDL/DML at a merged commit. |

### Overlap with PATCH-01 (#56) — no duplication

`PATCH-01` (#56) removes the two "Seed … via Management SQL/API" steps (RLS DDL,
password/identity seeding, data seed) from `deploy-production.yml` and
`deploy-development.yml` (273 deletion-only lines). `FINAL-P1-002` is the FINAL
synthesis finding that names that same root cause and recommends "use migrations
+ protected seed workflow". This PR supplies the governance documentation and the
sanctioned-channel record; it deliberately does **not** re-edit the deploy
workflows, so the two changes do not conflict.

## Changes

| File | What changed |
|---|---|
| `docs/operations/database-change-governance.md` | New. States the policy (migrations are the only schema channel; seed data via `seed-database.yml`; deploy workflows perform no DDL/DML; RLS may only be relaxed by a reviewed migration), the exact `rg` reviewer check, and the current status (removal tracked by PATCH-01 / #56). |
| `docs/operations/deployment-policy.md` | New "Database Changes" section pointing to the governance page. |
| `docs/README.md` | Added a quick link to the governance page. |

Scope: three documentation files. No application code, workflow, dependency, or
lockfile change.

## Verification Performed

Runner: `ci-runner` (LXC 200), workspace `/srv/work/chat`. The lab sync drops
`.git` objects, so the run is bound to the commit via `ps-u07-commit.txt`, the
documented blob SHA-256 values, and a transferred diff (`git diff base..HEAD`).
Full raw log: `remediation/PS-U07/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `sha256sum` of the 3 docs | ci-runner | 0 | hashes match the committed blobs (`bc3c95d7…`, `d7fa0d79…`, `c33942f3…`) — `verify.log` |
| relative-link existence check for changed docs | ci-runner | 0 | `linkcheck_broken=0` — `verify.log` |
| `corepack pnpm install --frozen-lockfile` | ci-runner (pnpm 9.15.4) | 0 | "Lockfile is up to date"; 883 packages, done in 2.5s — `verify.log` |
| `corepack pnpm exec prettier --check` (3 docs) | ci-runner | 0 | "All matched files use Prettier code style!" — `verify.log` |
| `gitleaks detect --no-git --redact --source <changed file>` ×3 | ci-runner (gitleaks 8.30.1) | 0 | no leaks in any changed doc — `verify.log` |
| `gitleaks detect --no-git --redact --source ps-u07-diff.patch` (the committed diff) | ci-runner | 0 | "no leaks found" (8.55 KB scanned) — `verify.log` |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 5 **pre-existing** findings (`.github/workflows/validate.yml:jwt`, `apps/web/components/shared/keyboard-shortcuts.tsx:generic-api-key`, `infra/docker/.env.dev.example:jwt` ×3); **none** in this diff — `verify.log` |

- **Docs checks pass**; the change is documentation only, so the product test
  suite is not applicable.
- **Secret gate**: clean on every changed file and on the committed diff. The
  full-tree hits are the same audited, pre-existing fixtures recorded by the
  sibling remediation runs.

## Evidence bundle

- `remediation/PS-U07/diff.patch` — SHA-256 `e7b6d1c0e488454857120a3af5dec29fe6c52f184b2a32206bff825b6b544f5a`
- `remediation/PS-U07/verify.log` — SHA-256 `2458e42c083c3f23c670d6e1969817abb5caba329e21b258d4c04422e820d424`
- `remediation/PS-U07/manifest.json`
- `remediation/PS-U07/pr_body.md`

## Risk and rollback

- Risk: **very low**. Documentation only; no runtime code, CI workflow,
  dependency or lockfile change. The policy page changes no runtime gate.
- Rollback: `git revert f4bcb403785130f14d73e644996266226af25add`.

## Review checklist

- [ ] Diff touches only the three documentation files
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] `FINAL-P1-002` closure is understood to depend on PATCH-01 (#56) merging
- [ ] Rollback is practical

## Definition of done (for this set)

- Database change / deploy governance is documented in-repo and discoverable
  from the deployment policy and docs index.
- No deploy-time DDL/DML is stated as a reviewable policy with an exact check.
- `FINAL-P1-002` moves to `verified-fixed` once the deploy workflows are free of
  DDL/DML at a merged commit (PATCH-01 / #56 or equivalent).

## Open questions

1. **Final closure is workflow-gated, not docs-gated.** `FINAL-P1-002`'s own
   recommendation is to *remove* the deploy-time DDL/DML. That is `PATCH-01`
   (draft PR #56), still open at this base. This catch-all PR documents and
   cross-links the policy but cannot itself satisfy the finding's validation
   (`deploy pipeline has no database/query writes`); it must move to
   `verified-fixed` only after #56 (or an equivalent) merges.
2. **`AGENTS.md` still documents the deploy-time Management-SQL seeding** as the
   working approach (Seed Workflow section). Correcting that long-form status
   doc is a follow-up for the owner once #56 lands; it is intentionally out of
   this minimal patch set to avoid a large docs rewrite.
3. **Repository-settings controls remain out of scope.** Production environment
   reviewers and required PR review on `main` (recommended by `CI-P1-001`) are
   repository configuration, not code or docs.
