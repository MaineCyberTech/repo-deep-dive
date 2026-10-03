# Contributing — extending the repo-deep-dive pack

This pack is a living artifact: prompts, lenses, profiles, templates, and tools evolve together. Follow this recipe so the tree stays consistent (the pack's own rules apply to it).

## Ground rules

- **Additive by default.** Extend before you modify; keep the base edition usable standalone.
- **Version everything.** Base edition changes bump `VERSION`; profile changes bump the profile version in `profiles/falcon-lab.manifest.json`.
- **One change, one changelog entry.** Update `CHANGELOG.md` in the same pass.
- **Regenerate and verify** (`tools/pack_digest.sh`, `tools/lint_pack.sh`) before calling it done.

## Add a domain prompt

1. Pick the next free number and a unique area code (`AREA-SEVERITY-NNN` finding IDs).
2. Create `prompts/NN_name.md` with the standard structure:
   - `@include \`00_SHARED_AUDIT_RULES.md\``
   - Mission · Output path · Area code (with examples)
   - Primary audit questions (10) · Scope to analyze
   - Required special checks · Required outputs and companion artifacts
   - Step-by-step execution instructions (11 steps) · Evidence collection checklist
   - Required report structure (include `## Verification Performed`) · Quality bar
3. Add an **Extended verification checks** block when the prompt maps to a known failure class.
4. Register the prompt: the base or falcon manifest example (`executionOrder`, `promptCount`), the falcon profile matrix if applicable, and the runner's wave table.
5. Update `README.md` layout and counts.

## Add a lens

1. Create `lenses/<name>.md` with: Purpose · Area code · When to apply (targets) · Question set · Evidence expectations · Output shape · Traps to avoid.
2. Register it: `profiles/falcon-lab.md` §5 matrix, `profiles/falcon-lab.manifest.json` `lenses[]`, the falcon manifest example, the falcon runner's wave 2 + required files, and the README lens list.
3. Lens findings use the lens area code; they must cross-reference domain IDs instead of duplicating them.

## Change the shared rules

Shared rules affect every prompt in both editions. Bump the base edition version, note the change in the changelog, and — if report sections or vocabularies change — update `REFERENCE_CARD.md` and the templates in the same pass.

## Change a template or example

Templates are the output contract. Keep them aligned with the shared rules' required sections and the finding format. Examples must parse (`tools/lint_pack.sh`).

## Versioning

| Artifact | Where | When |
|---|---|---|
| Base edition | `VERSION`, example manifests (`version` / `packVersion` / `basePackVersion`), README | Any change to prompts, shared rules, templates, or tools |
| Falcon-lab profile | `profiles/falcon-lab.manifest.json` `profileVersion` | Profile matrix, lens targets, boundaries, wiring changes |

## The completion checklist

1. Edits done; `## Verification Performed` present where required.
2. `CHANGELOG.md` entry written.
3. `./tools/pack_digest.sh` — digest regenerated.
4. `./tools/lint_pack.sh` — all checks pass.
5. `./tools/self_test.sh` — all tools pass.
6. `./tools/check_run.sh <run-folder>` for any touched run — PASS.
7. Mirror to the second tree (if maintained): `cp -a . /home/user/Prompts/repo-deep-dive/` and `diff -rq` both ways.

## Post-run pack review

After each audit run, ask: which prompts produced nothing? Where did auditors get stuck? Which checks were impossible without live access? Feed the answers back as prompt tweaks or new tools — the pack should get sharper with every run.
