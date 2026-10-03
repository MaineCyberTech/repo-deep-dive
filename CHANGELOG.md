# Changelog

## 2026-10-02 — Base edition v1.4.1 (verification feedback + vocabulary gate)

- **Gates**: `check_run.sh` also fails on finding statuses outside the shared vocabulary (all archived registers verified conforming first).
- **Verification feedback**: both runners' verification modes now mirror new statuses into `follow_up_register.md`, so `collect_findings.py` picks them up instead of stranding them in `verification_log.md`.
- **Orchestration**: prompt `00` points at `tools/new_run.py`; new `templates/subagent_brief_template.md` keeps Wave 1–2 fan-out briefs uniform (referenced by the falcon-lab runner).
- **Versions**: base pack `1.4.0 → 1.4.1` (falcon-lab profile unchanged at `1.1.0`).

## 2026-10-02 — Base edition v1.4.0 (robustness: scaffold, chain, gates, digest)

- **Tools**: `new_run.py` (Wave 0 scaffold: valid run folder with INDEX skeleton + seed manifest; refuses non-empty dirs) and `run_toolchain.py` (one-command Wave 4/verify chain: check → collect → score → dashboard → diff → CSV; read-only by default, `--write` to emit; pure-Python except the optional `check_run.sh` step, which degrades to a warning without bash).
- **Gates**: `check_run.sh` gains a duplicate-finding-ID gate (IDs are load-bearing for registers, CSVs, and diffs; both archived runs verified clean before enabling).
- **Digest**: environment-local files are untracked (`opencode.json`, `.DS_Store`, `Thumbs.db`, `*~`) in `pack_digest.sh` and `lint_pack.sh` together, so local pins no longer dirty the digest.
- **Inventory**: wider stack/CI detection (jenkins, gitlab-ci, azure-pipelines, helm, serverless, dotnet, iOS, android, terraform globs) plus a `ci` systems field.
- **CI/docs**: `ci/audit.yml` simplified onto `run_toolchain.py`; quickstart scaffolds via `new_run.py`; reference card documents the chain.
- **Tests**: `self_test.sh` covers the read-only toolchain chain and a TMP scaffold.
- **Versions**: base pack `1.3.1 → 1.4.0` (falcon-lab profile unchanged at `1.1.0`).

## 2026-10-02 — Base edition v1.3.1 (old-pack wording sweep)

- **Finding format** (shared rules + `finding_template.md`): two optional lines — `Endpoint / data path` (method + route, request → service → storage) and `Attack path` (CHAIN composition or `none identified`). Backward-compatible: tools parse only ID/severity/title.
- **Prompt 22**: patch-set grouping rules (every finding in exactly one set; P0-only immediate set; 3+ files → own set; resolve contradictions into one plan) + patch-set mapping table in required outputs. `patch_plan_template.md` upgraded to per-set tables (`PS-00N` → findings → files → dependencies → effort → verification command).
- **Net-new checks from the retired packs' v2 deltas**: optimistic-locking/version preconditions (`07`), raw-body webhook signatures (`27`), beyond-IP rate-limit keys (`06`), bulk per-item results (`04`); recipes added to `docs/AUTOMATION_GUIDE.md`.
- **Operator docs**: remediation execution discipline (branch per patch set, verification-or-rollback, milestone grouping) in `runbooks/OPERATOR_TROUBLESHOOTING.md`.
- **Versions**: base pack `1.3.0 → 1.3.1` (falcon-lab profile unchanged at `1.1.0`).

## 2026-10-02 — Base edition v1.3.0 (single-pack consolidation)

- **Goal**: `repo-deep-dive` becomes the one pack for all repos. Portable value from the two retired MCT-scoped packs (hardening prompt pack, portal alignment engine) is absorbed here in repo-agnostic form; the retired packs stay read-only archives and receive no further updates.
- **Prompt**: `45_exploit_chain_attack_path_audit.md` (area `CHAIN`) — end-to-end attack paths composed from domain findings, with prerequisites, blast radius, and detection per chain. Registered in both runners, both manifest examples, and the falcon-lab profile (matrix 28 RUN · 8 ADAPTED · 10 N/A; `ADV` lens targets gain `45`).
- **Tools**: `repo_inventory.py` (Wave 0 inventory of any repo layout — stacks, routes, migrations, workflows, containers; filenames only for secret-adjacent files), `risk_score.py` (advisory 0–100 score `100 − (P0×40 + P1×10 + P2×3)` + `GO / GO WITH CONDITIONS / NO-GO` suggestion; never overrides `RELEASE_GATE.md`), `render_dashboard.py` (`dashboard.md` + `dashboard.html` + `pr_comment.md` from findings).
- **Schemas / CI**: `schemas/findings.schema.json` (envelope for `findings.json`); `ci/audit.yml` (GitHub example: lint → validate → score → P0 gate → artifacts).
- **Docs**: `docs/AUTOMATION_GUIDE.md` (portable grep/glob/read recipes + retired-check mapping table); `runbooks/OPERATOR_TROUBLESHOOTING.md`; quickstarts point at both; `wiring/SUGGESTED_TOOLING.md` gains a pack-internal toolchain section; `REFERENCE_CARD.md` documents the advisory score.
- **Portability fixes**: `diff_runs.py` output is ASCII-only (was crashing on Windows cp1252 consoles); `lint_pack.sh` digest check normalizes path separators (was false-stale on Windows); new tools are stdlib-only, forward-slash paths, ASCII stdout.
- **Tests**: `self_test.sh` now also covers `risk_score.py`, `render_dashboard.py`, findings-schema conformance, and a read-only `repo_inventory.py` self-scan.
- **Versions**: base pack `1.2.1 → 1.3.0`; falcon-lab profile `1.0.0 → 1.1.0`.

## 2026-09-30 — Base edition v1.2.1 (self-test and consistency closers)

- **Tools**: `self_test.sh` (end-to-end toolchain exercise: lint + run validation + findings collection/diff/CSV + read-only live snapshot); `collect_findings.py` warns on duplicate finding IDs; `lint_pack.sh` gains runs ↔ `runs/INDEX.md` consistency and `Verification Performed` structure checks.
- **Docs**: `lenses/README.md` (lens concept and application); `templates/edge_mirror_pointer_template.md`; both runners reference the run tools; CONTRIBUTING completion checklist updated.
- **Run index**: archived run `INDEX.md` lists `findings.json`.
- **Versions**: base pack `1.2.0 → 1.2.1`.
- **Mirror**: synced to `/home/user/Prompts/repo-deep-dive/`.

## 2026-09-30 — Base edition v1.2.0 (tooling, templates, reference, adversarial lens)

- **Tools**: `lint_pack.sh` (pack self-consistency: versions, JSON, area codes, prompt structure/counts, references, run validation, digest freshness); `collect_findings.py` (normalize run findings → `findings.json`, optional manifest count sync); `diff_runs.py` (run-to-run delta: new/missing/severity/title/status changes); `findings_to_csv.py` (tracker export); `live_snapshot.sh` (falcon-lab read-only live-state capture).
- **Templates**: claim sample, verification log, decision-log entry, owner decisions, follow-up register, lens report.
- **Lens**: `lenses/security_adversary.md` (`ADV`) — adversarial overlay; wired into the falcon-lab profile matrix, manifests, and runner.
- **Prompt**: `44_data_quality_pipeline_fidelity_audit.md` (`DQ`) — data quality and pipeline fidelity domain; registered in the profile (matrix, counts), manifests, and runner.
- **Scales**: confidence, effort, and remediation-window definitions added to the shared rules; `REFERENCE_CARD.md` one-pager; `VERSION` file.
- **Docs**: `CONTRIBUTING.md` (extension recipe), `runs/INDEX.md` (archive index), `wiring/SUGGESTED_TOOLING.md`, README run-flow diagram.
- **Run artifact**: generated `runs/20260930-0320-.../findings.json` (machine-readable findings).
- **Versions**: base pack `1.1.0 → 1.2.0`; falcon-lab prompt count `44 → 45`.
- **Mirror**: synced to `/home/user/Prompts/repo-deep-dive/`.

## 2026-09-30 — Base edition v1.1.0 (verification discipline extension)

- **Shared rules**: added a **Verification discipline** section (claim sampling and reproduction, self-consistency of status artifacts, literal walks, review-claim artifacts, artifact binding, aggregates, configured-vs-exercised), a **Finding status vocabulary** (`open` / `partially-fixed` / `verified-fixed` / `still-open` / `regressed` / `owner-accepted`), destructive-tooling inventory and operator-authorized read-only live verification in the safety rules, and a **Verification Performed** required report section.
- **Prompts**: added **Extended verification checks (base edition v1.1.0)** blocks to 34 prompts (`00`–`40` where motivated, plus `41`–`43`), each mapped to failure classes from the 2026-09-30 audit run; added **Verification Performed** to all 44 prompt report structures.
- **Master runner**: added verification execution rules, a **Verification mode** workflow, and a reconciliation subsection in the final response.
- **Templates**: `audit_report_template.md` and `audit_report_template.falcon.md` gained a `Verification Performed` section.
- **Quickstart**: base quickstart gained a verification-mode section.
- **Wiring**: `REPO_WIRING.md` documents the status vocabulary and post-remediation verification.
- **Versions**: base pack `1.0.0 → 1.1.0` (both manifest examples + the falcon-lab profile manifest's `basePackVersion`).
- **Mirror**: synced to `/home/user/Prompts/repo-deep-dive/` (trees kept identical).

## 2026-09-30 — Consolidated edition (this tree)

- **Merged** the original pack v1.0.0 (41 prompts, shared rules, master runner, 6 templates, manifest example, quickstart) and the falcon-lab layer v1.0.0 (profile + machine-readable manifest, 4 lenses, prompts `41`–`43`, falcon master runner, falcon quickstart, falcon report template, falcon manifest example).
- **Added** `runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/`: first archived run — the six 2026-09-30 audits converted into four lens reports (90 findings, `AREA-Px-NNN` IDs) with `INDEX`, `EXECUTIVE_SUMMARY`, `RELEASE_GATE`, `risk_register`, `roadmap`, `patch_plan`, `follow_up_register`, `audit_manifest.json`, and byte-identical `source_reports/` with sha256 provenance.
- **Added** `wiring/REPO_WIRING.md`: layout options (central vs vendored), run conventions, decision-log integration, register integration, CI drift checks, parallel-session coordination, archiving/versioning.
- **Added** `tools/check_run.sh` (validates a run folder: required finals, manifest JSON, falcon-lab extras, finding-ID consistency across register tables) and `tools/pack_digest.sh` (regenerates `PACK_DIGEST.txt`).
- **Modified (additive notes only)**:
  - `runbooks/OPERATOR_QUICKSTART.md` — appended a "Falcon lab" pointer to the falcon-lab quickstart/profile/runner.
  - `prompts/MASTER_RUNNER_FULL_HARDENING.md` — appended a "Falcon lab variant" pointer.
- No other original files were changed (verify with `tools/pack_digest.sh` against a prior digest if needed).

## Falcon-lab layer history (merged into this edition)

### 2026-09-30 — falcon-lab layer v1.0.0

- `profiles/falcon-lab.md` + `profiles/falcon-lab.manifest.json`: scope, doctrine read-first list, 6 boundary rules, 44-prompt applicability matrix (26 RUN / 8 ADAPTED / 10 N/A), lens matrix, waves, output wiring, cadence, reconciliation rule.
- `lenses/new_developer.md`, `lenses/independent_reviewer.md`, `lenses/integration.md`, `lenses/live_operations.md` with area codes `ND`, `REV`, `INTG`, `LIVE`.
- `prompts/41_evidence_doctrine_gate_integrity_audit.md` (`EVID`), `prompts/42_cross_repo_integration_pairing_audit.md` (`XREPO`), `prompts/43_edge_fleet_hardware_audit.md` (`FLEET`).
- `prompts/MASTER_RUNNER_FALCON_LAB.md` (waves: recon → domain fan-out → lenses → synthesis → doctrine wiring; verification mode).
- `runbooks/OPERATOR_QUICKSTART_FALCON_LAB.md`, `templates/audit_report_template.falcon.md`, `examples/audit_manifest.falcon-lab.example.json`.

### Base edition v1.0.0

- Original 41-prompt Full Hardening pack (unmodified except the two additive pointers above).
