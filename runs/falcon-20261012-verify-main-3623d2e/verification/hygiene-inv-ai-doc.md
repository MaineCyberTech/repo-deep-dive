# Post-merge verification — HYGIENE / INV / AI / DOC (15 findings)

- Run re-checked: `falcon-20261011-0416-full-f5cb7c9` (audit target `f5cb7c9`)
- Current state: `/home/user/falcon-build` @ `3623d2e7608db28c427d63a36dedf7a969de8572` (49 commits after the audit commit)
- Method: read-only repo checks + read-only live checks (Grafana API, sudo). No writes to the repo; no secrets printed.
- Date: 2026-10-12
- Overall: 7 closed, 8 still-open (all partially addressed; none regressed). One live working-tree mutation observed (see New findings).

## Summary table

| ID | Sev | Audit status | Verdict now | Evidence (short) |
|---|---|---|---|---|
| AI-P3-001 | P3 | open | **still-open** (partial) | AGENTS.md:86, README.md:11, AUDIT_RUN_LIFECYCLE.md:39-40 now name `falcon-20261011-0416-full-f5cb7c9`; CURRENT_STATE.md:1 (title 2026-10-10), :91 records table and C4 row still lag; no run-pointer drift test |
| AI-P3-002 | P3 | open | **still-open** (partial) | Provenance rule added (AGENTS.md:89-93); still no CLAUDE.md/.cursor/copilot pointer files (find → none); PR template has no authorship field (.github/pull_request_template.md, 32 lines) |
| DOC-P2-001 | P3 | open | **closed** (doc residuals) | `verify_delivery.sh:41-52` wires `pack_fidelity.py` fail-closed; BOM handling `pack_fidelity.py:53-58`; residual: notes file still carries no verdict, RELEASE_PACK_VERIFICATION.md:81 still says "open" |
| DOC-P2-002 | P2 | partially-fixed | **still-open** (partial) | catalogue = source = live = 93 (sets identical); README.md:32=93; CURRENT_STATE.md:112,132=93; EVOLUTION_GUIDE §7 refreshed. Residual: CURRENT_STATE.md:56 still "85-rule"; ALERT_FIRING_PROOFS.md:21 still "75 of the 77"; no source↔catalogue static check |
| DOC-P3-001 | P3 | open | **closed** | README.md:29 "Suricata 8.0.7", :31 "OpenSearch 2.19.6" match pins/images.lock:55 / :13 |
| HYGIENE-P2-001 | P2 | still-open | **still-open** | sbom/ 42 files / 29.6 MB (29,565,401 B), largest 3,064,465 B; hash binding only, no freshness gate |
| HYGIENE-P2-002 | P2 | open | **still-open** (partial) | RELEASE_GATE.md:15-17 now reference `falcon-20261011-0416…` (P0 x0); :51 still headed "Current audit opinion (run 20261003-0018…)"; README.md:138 still "Current state (2026-10-02…)"; no drift test |
| HYGIENE-P2-003 | P2 | verified-fixed | **closed** | Doctrine updated: .gitignore:24-29, AGENTS.md:44, REPOSITORY.md:33,54, build_review_package.sh:9-12; publication equality PASS |
| HYGIENE-P3-001 | P3 | open | **closed** | LICENSE (509 B) + NOTICE (662 B) tracked (added 5e8b262); git ls-files shows both |
| INV-P2-001 | P2 | open | **still-open** | Only `evidence/MANIFEST.sha256` bound by default (`check_generated_drift.py:37`); docs/audits/ structural lifecycle only; mct/ has no import manifest (REPOSITORY.md:44) |
| INV-P3-001 | P3 | open | **still-open** | `check_evidence_index.py:118-120` still skips legacy rows; PASS output: 1136 metas / 872 host-absolute resolved / 264 legacy skipped; resolver documented (REPOSITORY.md:63-74) but not applied centrally |
| INV-P3-002 | P3 | open | **closed** | PACK_NOT_INCLUDED.txt has no "unexpected; investigate" entries; both files verified present in the current pack (verify_pack parse: 191 B / 724 B); PACK_VERIFICATION_NOTES.txt:260 |
| INV-P3-003 | P3 | open | **still-open** | ci/validate.py:489-497 "A stale digest therefore fails here…" and check_digest_binding.py:10-12 "a stale package or digest fails closed" unchanged; freshness is enforced by check_publication_equality.py |
| INV-P3-004 | P3 | verified-fixed | **closed** | PACKAGE_MANIFEST.sha256 == review-package/MANIFEST.sha256 (sha256 7e2526ae…); copy wired at publish_digests.sh:18; equality PASS |
| INV-P3-005 | P3 | verified-fixed | **closed** | Same doctrine fix as HYGIENE-P2-003 (docs/ignore rules + build script); residual: EVOLUTION_GUIDE.md:89 step 7 does not mention the declared-manifest exception |

## Per-finding detail

### AI-P3-001 — Agent/audit-run pointers stale — **still-open (partially addressed)**

Fixed parts:
- `AGENTS.md:86` — "the newest full-domain runs live in the repo-deep-dive pack under `runs/` (current: `falcon-20261011-0416-full-f5cb7c9`)".
- `README.md:8-14` — "Current state (2026-10-11) … current: `falcon-20261011-0416-full-f5cb7c9`, GO WITH CONDITIONS, P0 x0".
- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:39-40` — rule 6 now: "The newest runs are live. The current falcon baseline is `falcon-20261011-0416-full-f5cb7c9` … the archived `20260930-0701…` copy remains read-only".

Remains:
- `docs/CURRENT_STATE.md:1` is still titled "Falcon current state (2026-10-10)"; the records table `:91` still names only the 2026-09-30 run; there is no mention of `falcon-20261011-0416` anywhere in the file (`grep -c "20261011" docs/CURRENT_STATE.md` → 0; `20261009` → 1).
- No doc-drift test asserts that the referenced run resolves / that the newest full run is referenced (grep of `automation/` and `ci/` finds no such check).
- The 2026-10-05 in-repo run remains unreferenced in README/RELEASE_GATE/CURRENT_STATE (superseded by the newer pack runs, but the original finding's "unreferenced run" half was only fixed by pointing at a newer run).

### AI-P3-002 — No AI-provenance policy / per-tool agent coverage — **still-open (partially addressed)**

Fixed: provenance policy added at `AGENTS.md:89-93` ("agent-authored changes commit under the `build-agent` identity and record the tool/session in the commit body when non-trivial; agent-opened PRs carry the `AI-assisted` label…").

Remains:
- `find . \( -iname "CLAUDE.md" -o -iname "*copilot*" -o -iname ".cursor*" -o -iname "*windsurf*" \)` → no files; AGENTS.md is still the only agent-instruction file.
- `.github/pull_request_template.md` (32 lines) still has no authorship/provenance field.

### DOC-P2-001 — Pack-fidelity not wired into the delivery build — **closed**

- `automation/validation/verify_delivery.sh:41-52` now runs, before archiving:
  `python3 automation/validation/pack_fidelity.py /home/user/falcon-repomix.md review-package/MANIFEST.sha256` and increments `fail` on mismatch (fail-closed); prints `pack_fidelity_verdict=PASS|FAIL`.
- The BOM-only classification landed in `automation/validation/pack_fidelity.py:53-58` (`strip_bom`), with the 3 archived 2026-10-02 evidence patches recorded in `PACK_VERIFICATION_NOTES.txt` ("leading BOM dropped by the pack renderer").
- The current pack (`/home/user/falcon-repomix.md`, 46,763,888 B, 2026-10-11 18:33) verifies: `PACK_NOT_INCLUDED.txt` has only the 3 package-generated entries.
- Residual (not blocking): `PACK_VERIFICATION_NOTES.txt` still carries no verdict/counts header (was "optional" in the audit's fix); `docs/security/RELEASE_PACK_VERIFICATION.md:81` still states the wiring recommendation "is still open" and `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` still calls pack checks "still local-only"/partial — stale after the fix.

### DOC-P2-002 — Status artifacts lag the live state — **still-open (partially fixed)**

Fixed:
- Catalogue/source/live now agree exactly: `docs/phase9/ALERT_CATALOGUE.yaml` = 93 entries; `bootstrap/90-alerting.sh` = 93 unique `write_rule` UIDs (`alert_rule_lint_test.sh` → `derived_rule_count=93; unique_uids=93`); live Grafana API (read-only, 2026-10-12) = 93 rules / 93 unique UIDs; set difference catalogue↔live, source↔catalogue, source↔live all empty.
- `README.md:32` = "93 alert rules"; `docs/CURRENT_STATE.md:112,132` = 93 rules (2026-10-11).
- `docs/architecture/EVOLUTION_GUIDE.md` §7 state block refreshed ("Current state (view; source of truth is the ledgers, 2026-10-11)" with the 2026-10-11 run and C7 closed).

Remains:
- `docs/CURRENT_STATE.md:56` (C4 row) still says "**85-rule catalogue live** (2026-10-10)".
- `docs/phase9/ALERT_FIRING_PROOFS.md:21` (section "Current coverage (authoritative)") still says "As of 2026-10-03, **75 of the 77 live rules have a firing proof**"; the consolidated section (:457) says 75 of 76. Only the historical 2026-10-03 section got a parenthetical annotation "(the live set is 93 rules as of 2026-10-11; newer rules are proven per the release process)".
- Source→catalogue static drift is still unchecked: `automation/validation/tests/alert_rule_lint_test.sh` parses `90-alerting.sh` but does not compare its UID set to the catalogue; `readme_ledger_drift_test.sh` compares README to the catalogue only.

### DOC-P3-001 — Imprecise version shorthand — **closed**

- `README.md:29` now "Suricata 8.0.7" (pins/images.lock:55 `jasonish/suricata:8.0.7`); `README.md:31` "OpenSearch 2.19.6" (pins/images.lock:13 `opensearchproject/opensearch:2.19.6`).

### HYGIENE-P2-001 — Large generated SBOM/vulnerability JSON committed — **still-open**

- `find sbom -type f | wc -l` → 42 (37 JSON), `du -sb sbom/` → 29,565,401 B (29.6 MB); largest `sbom/opensearchproject_opensearch-dashboards_2.19.6.cdx.json` 3,064,465 B.
- Only integrity is bound: `sbom/SBOM_MANIFEST.sha256` + `sbom_hashes.sh verify` (hash match / no unlisted files) and the new ed25519 signature (SBOM-P2-001); no freshness/expiry gate exists (`ci/validate.py:512-519` says publishing as CI/release assets is the recorded owner decision). Same size as at the audit.

### HYGIENE-P2-002 — Release-gate page carries a superseded opinion — **still-open (partially addressed)**

- Fix: `docs/RELEASE_GATE.md:15-17` now lists the newest full-domain runs and states "(current: `falcon-20261011-0416-full-f5cb7c9`, GO WITH CONDITIONS, P0 x0; the stale-opinion pointer was HYGIENE-P2-002)" — the newest run's P0 (x0) is referenced.
- Remains: `docs/RELEASE_GATE.md:51` is still headed "## Current audit opinion (run `20261003-0018-fix-backup-abort-markers-20b5e57`, commit `20b5e57`)" with the old NO-GO/46-finding roll-up; `README.md:138` still says "Current state (2026-10-02, audit reconciliation)"; the in-repo 20261005 run remains unreferenced; no CI drift test (newest referenced run newer than the page's → fail) exists.

### HYGIENE-P2-003 — Force-tracked MANIFEST vs doctrine — **closed**

- Doctrine now documents the exception everywhere the finding cited:
  - `.gitignore:24-29` — "EXCEPTION: the publication flow intentionally force-adds review-package/MANIFEST.sha256 in the declared commit as the publication anchor … that single file is expected to be tracked (HYGIENE-P2-003 / INV-P3-005, 2026-10-11)".
  - `AGENTS.md:44` — "generated artifact; gitignored, do NOT commit (HYG-P1-001) EXCEPT the force-added review-package/MANIFEST.sha256 publication anchor (declared commit)".
  - `REPOSITORY.md:33` and `:54` — same exception stated.
  - `automation/validation/build_review_package.sh:9-12` — same exception in the header.
- `python3 automation/validation/check_publication_equality.py --root .` → PASS (17 ok checks, including "declared-commit review-package manifest hash matches digest" and "commits after the declared commit touch only publication/test files" — no skip note, because the tracked manifest is present).
- Minor residual: the absent-manifest skip path (`check_publication_equality.py:187-191`, "post-publication ancestry restriction skipped") is still fail-open and has no regression test; `docs/architecture/EVOLUTION_GUIDE.md:89` step 7 does not mention the exception (see New findings N-3).

### HYGIENE-P3-001 — No root LICENSE/NOTICE — **closed**

- `LICENSE` (509 B, "Proprietary - all rights reserved. Copyright (c) 2026 Maine Cyber Tech…") and `NOTICE` (662 B) exist and are tracked (`git ls-files`); added in commit `5e8b262` ("LICENSE/NOTICE added (proprietary, all rights reserved) - DET-P3-001 closed", decision log 2026-10-11T18:12Z).
- Minor: `README.md:125-128` ("License / ownership") still does not link LICENSE/NOTICE; terms now live in the root files.

### INV-P2-001 — Majority generated content; audit records and mct/ unbound — **still-open**

- Bound today: `evidence/` via `evidence/MANIFEST.sha256` (`check_generated_drift.py:37` DEFAULT_MANIFESTS = only evidence), `sbom/` via SBOM_MANIFEST, the declared review-package manifest via the digest chain.
- Still unbound: `docs/audits/` run folders (only the structural `audit_run_lifecycle.sh check`; no content manifest), the vendored `mct/` subtree (no import manifest — `REPOSITORY.md:44` lists `mct/` as authored Source; `mct/VENDORING.md` remains a policy, not a binding).
- The published `PACKAGE_MANIFEST.sha256` residual from this finding (INV-P3-004) is fixed.

### INV-P3-001 — Legacy host-absolute evidence paths — **still-open**

- `python3 automation/validation/check_evidence_index.py` → `PASS evidence_index (1136 metas, 1136 rows, 872 host-absolute resolved, 264 legacy skipped)`.
- `check_evidence_index.py:118-120` still short-circuits legacy rows (`if LEGACY_MARKER in norm_artifact: skipped += 1; continue`) rather than resolving them; the resolver (`automation/validation/resolve_evidence_path.py`) and its docs (`REPOSITORY.md:63-74`) exist but every consumer must know to run it. New metas still record host-absolute paths (872 now vs 870 at the audit).

### INV-P3-002 — Pack fidelity artifact ships unresolved entries — **closed**

- `PACK_NOT_INCLUDED.txt` at HEAD contains only the 3 package-generated entries (`OWNER_ACCEPTANCE.md`, `REVIEWER_CHECKLIST.md`, `vuln-summary.csv`); the two "not-in-pack (unexpected; investigate)" lines were removed in `5e8b262`.
- Verified against the current pack with the repo's own parser (`verify_pack.parse_pack`): `evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out` present (191 B) and `mct/config/examples/secrets.example.env` present (724 B); the gitleaks file is listed in `PACK_VERIFICATION_NOTES.txt:260` as a whitespace-normalisation entry. Both files exist in the tree (196 B / 724 B).
- Minor residual: no root-cause disposition sentence was recorded for the earlier omission; the regenerated classification now simply reflects inclusion.

### INV-P3-003 — "A stale digest fails" wording — **still-open**

- The residual from the audit is unchanged: `ci/validate.py:489-497` still says "A stale digest therefore fails here instead of being mistaken for current"; `automation/validation/check_digest_binding.py:10-12` still says "a stale package or digest fails closed".
- In fact the check only compares declared manifest hashes to shipped files and resolves the declared commit; freshness (non-publication commits after the declared commit) is enforced by `check_publication_equality.py` (ancestry block; skip path at :186-191). Neither file was touched between `f5cb7c9` and HEAD (`git log f5cb7c9..HEAD -- check_digest_binding.py` → no changes to the wording; ci/validate.py changes were the SBOM-signature/owner-env additions).

### INV-P3-004 — Published PACKAGE_MANIFEST.sha256 stale — **closed**

- `sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` → both `7e2526aeb85bf6dd614bac3d25b26aa43338d2532e2053b6904e5d9bd2b2686b`.
- Copy wired into the publication flow: `automation/validation/publish_digests.sh:18` `cp review-package/MANIFEST.sha256 PACKAGE_MANIFEST.sha256` (commit 0b24a70), and `verify_delivery.sh:38` does the same at delivery build.
- `check_publication_equality.py` PASS confirms the digest ↔ shipped manifest ↔ declared-commit chain. Residual: no standalone equality assertion `PACKAGE_MANIFEST == review-package/MANIFEST` in a gate (the copy step makes them equal by construction).

### INV-P3-005 — HYG-P1-001 doctrine contradiction — **closed**

- Same fix as HYGIENE-P2-003: `.gitignore:26-28`, `AGENTS.md:44`, `REPOSITORY.md:33`/`:54`, `build_review_package.sh:9-12` now state the tracked `review-package/MANIFEST.sha256` is the declared-commit anchor.
- `git ls-files -s review-package/` → `100644 … review-package/MANIFEST.sha256`; `git check-ignore --no-index -v review-package/MANIFEST.sha256` shows it is still matched by the `review-package/` rule but is force-tracked by design (documented).
- Minor residual: `docs/architecture/EVOLUTION_GUIDE.md:89` (step 7) still says "generated artifact, gitignored — do not commit, HYG-P1-001" without the exception (see New findings N-3).

## New findings

### N-1 (P2) — Live working-tree mutation makes the mandated gate fail in place

- At verification start the tree was clean (`git status --short` empty, ~19:56Z). At **19:59:39Z** `config/grafana/dashboards/edge-fleet-overview.json` was rewritten in place (7 → 23 panels; pretty-printed; new edge sensor-health panels). It is uncommitted (`git status --short` → ` M config/grafana/dashboards/edge-fleet-overview.json`, still dirty at 20:14Z).
- Consequence: `python3 ci/validate.py` at the current working tree → `validation_failures=1`:
  `automation/validation/tests/readme_ledger_drift_test.sh: FAIL: README: panel count (expected '89', got '73')`.
- At the committed state the gate is green for this check: `git archive HEAD` extracted to /tmp and the same test run → `readme_ledger_drift_test_checks=28 readme_ledger_drift_test_failures=0` (HEAD panels = 73 = README).
- Interpretation: a concurrent live/cross-repo process (or another session) writes the adopted edge dashboard into the tracked tree; while in flight, the repo's working tree is not self-consistent and `ci/validate.py` is red. This is not a committed regression of the assigned findings, but it is an operational hazard (the "repo is clean at the audited commit" invariant can be silently broken between publications). Recommend: treat the in-flight write as a normal change (commit + rebind) or gate the live exporter to write only outside the tracked tree / through the documented adoption flow.

### N-2 (P3) — DOC-P2-001 fix left two docs describing the wiring as open

- `docs/security/RELEASE_PACK_VERIFICATION.md:81` still: "Recommendation 3 above (wire `pack_fidelity.py` into `verify_delivery.sh`) is still open" — contradicted by `verify_delivery.sh:41-52`.
- `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` still: "`pack_fidelity.py` … still local-only | **partial**" (accurate for CI, stale for the delivery build).

### N-3 (P3, minor) — Residual doctrine/skip-path edges from HYGIENE-P2-003 / INV-P3-005

- `docs/architecture/EVOLUTION_GUIDE.md:89` (step 7) still says the review package is "gitignored — do not commit, HYG-P1-001" without the declared-manifest exception that AGENTS/REPOSITORY/.gitignore now carry.
- `automation/validation/check_publication_equality.py:187-191` keeps a fail-open skip ("post-publication ancestry restriction skipped") for the case where `review-package/MANIFEST.sha256` is absent; the tracked manifest makes this path unreachable in practice, but no test pins it closed (the suite `publication_equality_test.sh` has no absent-manifest case).

## Verification commands (selected)

```bash
git -C /home/user/falcon-build rev-parse HEAD            # 3623d2e… (49 commits after f5cb7c9)
git ls-files | grep -iE '(^|/)(LICENSE|NOTICE)'          # LICENSE, NOTICE
du -sb sbom/ ; find sbom -type f | wc -l                 # 29,565,401 B; 42
python3 automation/validation/check_generated_drift.py --manifest review-package/MANIFEST.sha256   # drift vs package extras/closeout only (expected)
python3 automation/validation/check_publication_equality.py --root .   # PASS
python3 automation/validation/check_digest_binding.py --root .         # PASS
python3 automation/validation/check_evidence_index.py                  # PASS … 872 host-absolute resolved, 264 legacy skipped
bash automation/validation/tests/alert_rule_lint_test.sh               # PASS … derived_rule_count=93
# live Grafana (read-only, sudo): GET /api/v1/provisioning/alert-rules → 93 rules / 93 unique UIDs; set-identical to catalogue and source
python3 ci/validate.py                                                 # validation_failures=1 — caused by the uncommitted dashboard (N-1); passes at HEAD
```

Note: no secrets were printed; the live Grafana check read `/srv/falcon/secrets/grafana_admin.pw` via sudo and only emitted counts.
