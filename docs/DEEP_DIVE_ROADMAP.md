# Deep-dive roadmap — robustness, streamlining, coverage

Findings and proposals from running the full post-audit pipeline end-to-end (2026-10-04:
org deterministic sweep → 4 focused deep-dives → 16 remediation PRs → merge → reconcile).
Prioritized; each item is actionable.

## Robustness (fix what repeatedly bit us)

1. **CRLF/digest fragility.** `PACK_DIGEST.txt` broke the moment a generated file (or an appended
   `runs/INDEX.md` row) was written with CRLF — three times in one session. Fix:
   - hash **LF-normalized** content in `tools/pack_digest.sh` and `tools/lint_pack.sh`; and
   - make `tools/normalize-and-digest.sh` treat `w/mixed` (not just `w/crlf`); and
   - add a `pre-commit`/`publish` normalization step so generators can't inject CRLF.
2. **Run-generator compatibility.** The pack's `lib_findings` only reads findings from `lens_*.md` /
   `NN_*.md` tables; `publish_audit.py` had to emit a specific table or the self-test failed.
   Codify a single **run schema** (`schemas/run.schema.json`) + a `tools/new_run.py`-backed validator
   that runs BEFORE writing, so any producer (agent or tool) emits `check_run.sh`-valid runs.
3. **Publish idempotency.** Opening the canonical PR created near-duplicate audit PRs on re-run.
   `publish_audit.py` should locate the open PR by `head` (and update it) instead of opening a new one.
4. **Self-hosted runner health.** `ci-runner`'s GitHub runner was offline while the lab was up. Add a
   runner-health probe to the preflight (`gh api .../actions/runners`) and a
   `gh api -X POST .../runners/<id>/...`/lab-side service restart runbook; surface it in `health`.
5. **Merge-in conflicts are inevitable.** Two merges conflicted (buddy `release.yml`, falcon changelog).
   Add `tools/merge_queue.py`: detect `CONFLICTING`, attempt a deterministic LLM-assisted resolution
   (union of both sides) into a branch, and only merge if the repo's checks stay green.
6. **Gate bypass on direct push.** Branch protection only gates PRs; direct pushes to `main` bypass the
   lab preflight. Either require PRs for the pack, or run `Lab preflight` on a push too (or as a
   pre-push hook) so audit/remediation commits can't skip it.

## Streamlining (fewer manual steps)

7. **One command for the whole pipeline.** `tools/post_audit.py run --org <o> --repos <r>`:
   deterministic sweep → focused deep-dive dispatch → publish → remediation plan → draft PRs →
   merge → reconcile, with per-stage resumes. Today this is ~8 manual phases.
8. **Feed the deterministic artifact into the deep-dive automatically.** Agents were handed the
   artifact path by hand; a `tools/audit_inputs.py` should fetch the latest `deep-dive-deterministic`
   artifact per repo and drop `deterministic-findings.json`/`lens_deterministic.md` where the deep-dive
   expects them.
9. **Run staleness binding.** A run is bound to the HEAD at audit start; if the repo moves before
   publish/merge, flag `stale` and re-scope. Add a `generated_at_commit` check in `publish_audit.py`.
10. **Org pass manifest.** One `docs/audits/_org/<pass>/manifest.json` recording which repos, which
    lenses, artifact URLs, and PRs — the whole pass reproducible from a single file.
11. **Single remediation bridge.** `findings.json` (focused or full) → `remediation_plan.json` directly,
    so remediation doesn't only work from a hand-written `patch_plan.md`.

## Comprehensive (cover more than security/supply-chain/CI)

12. **Coverage matrix per repo.** Track which lenses ran and which are missing; the focused pass today
    omits data/RLS, resilience, observability, docs-operator, a11y. Add a `--lenses` selector and a
    `coverage.md` per run.
13. **First-class full-domain pass.** `tools/full_domain.py` drives the 46-prompt master runner with
    per-domain subagents that emit pack-schema findings, then aggregates — the "full-domain pass"
    becomes a supported mode, not a manual prompt run. **Done** (2026-10-04): driver +
    `emit`/`aggregate` pipeline; first `--fast` pilot for falcon at `f9cb67d`
    (`runs/falcon-20261004-fast-main-f9cb67d`).
14. **Cross-repo / org lens.** The deterministic rollup exists; add an **LLM org lens** that reads all
    per-repo findings and surfaces systemic patterns (shared credential estates, copy-pasted CI,
    shared base images) as org-level findings.
15. **False-positive registry.** Persist each scanner hit's adjudication (`real|false-positive|partial`)
    in a repo-level `.audit-fp-registry.json`; future runs pre-classify, cutting triage noise
    (this session: most falcon/snowride gitleaks hits were FPs).

## Effective (make results trustworthy and useful)

16. **Verification-bound statuses.** Reconcile already records the merge commit; also record the
    verification command/CI run URL and its result, so `verified-fixed` always carries a reproducible
    artifact (the repo's own `AGENTS.md` rule 5).
17. **Owner-gated findings as first-class.** Formalize `owner-accepted` with an expiry + owner, and a
    dashboard (`OWNER_DECISIONS.md` exists — wire it into the org scorecard).
18. **Org scorecard.** Per pass: open/closed by severity, time-to-remediate, gate pass rate, FP rate,
    coverage — publish with the board so progress is visible.
19. **Prompt hardening for the lenses.** Have deep-dive agents emit pack-schema IDs (`AREA-Px-NNN`)
    directly and include a `## Verification Performed` section, so publish/reconcile stop needing a
    normalization/remap step.
20. **Cost/latency control.** Deep-dives and full-domain passes are token-heavy; add a `--fast` mode
    (deterministic + security/supply-chain/CI only) vs `--full`, and cache per-repo inventories.
    **Partially done** (2026-10-04): `tools/full_domain.py` has `--fast`/`--full`; per-repo
    inventory caching remains.

## Immediate next actions (this cycle)
- Extend the focused pass to `falcon-edge`, `mainecybertech`, `repo-deep-dive`; publish + remediate + merge.
- Run one **full-domain pilot** (one repo) via `tools/full_domain.py` before scaling.
- Fix items 1, 2, 3 (robustness) and 16 (verification binding) — highest leverage, lowest risk.
