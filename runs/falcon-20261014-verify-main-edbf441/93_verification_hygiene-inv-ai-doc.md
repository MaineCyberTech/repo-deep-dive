# Post-merge verification re-audit — HYGIENE / INV / AI / DOC findings

- Repo: `/home/user/falcon-build` @ `edbf441` (`edbf441d03cfba1f2a2e923a94021e1cbab0c338`, main, clean, 61 commits after the previous verification `3623d2e`).
- Date: 2026-10-14. Original run: `falcon-20261011-0416-full-f5cb7c9`; previous verification: `falcon-20261012-verify-main-3623d2e` (2026-10-12); this re-audit run: `falcon-20261014-verify-main-edbf441`.
- Scope: 15 findings (DOC-P2-002, HYGIENE-P2-001/002/003, INV-P2-001, AI-P3-001/002, DOC-P2-001/P3-001, HYGIENE-P3-001, INV-P3-001..005).
- Method: read-only repo checks at edbf441 (`git show`, greps, the repo's own validators) + read-only live checks (Grafana provisioning API via `docker exec`, counts only, no secrets printed). `python3 ci/validate.py` at HEAD → `validation_failures=0` (52 shell suites). Nothing written into the repo tree.
- Result: **6 verified-fixed, 4 partially-fixed, 4 open, 1 regressed (INV-P3-002), 0 owner-accepted**.

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| DOC-P2-002 | P2 | partially-fixed | **partially-fixed** | catalogue = source = live = 94 (live Grafana API 94/94); README.md:32=94; CURRENT_STATE.md:112=94. Residual: CURRENT_STATE.md:56 still "93-rule catalogue" (2026-10-10), ALERT_FIRING_PROOFS.md:21 still "75 of the 77" (annotations say 93), no source↔catalogue static check |
| HYGIENE-P2-001 | P2 | open | **open** | sbom/ 42 files / 29,565,401 B, largest 3,064,465 B — unchanged; only hash + ed25519 signature binding (ci/validate.py:540-559), no freshness/expiry gate |
| HYGIENE-P2-002 | P2 | open | **partially-fixed** | RELEASE_GATE.md:15-17 names `falcon-20261011-0416-full-f5cb7c9` (P0 x0); :51 still "Current audit opinion (20261003-0018…)"; README.md:140 still "Current state (2026-10-02…)"; no drift test |
| HYGIENE-P2-003 | P2 | verified-fixed | **verified-fixed** | Doctrine intact (.gitignore:24-29, AGENTS.md:44, REPOSITORY.md:33/54, build_review_package.sh:9-12); publication equality PASS (declared-commit checks). Residual: absent-manifest skip `check_publication_equality.py:187-191` still fail-open + untested; EVOLUTION_GUIDE.md:89 lacks the exception |
| INV-P2-001 | P2 | open | **open** | DEFAULT_MANIFESTS still only `evidence/MANIFEST.sha256` (check_generated_drift.py:37; PASS 2342 entries); docs/audits/ structural lifecycle only; mct/ has no import manifest |
| AI-P3-001 | P3 | open | **partially-fixed** | AGENTS.md:86, README.md:11, AUDIT_RUN_LIFECYCLE.md:40 name `falcon-20261011-0416-full-f5cb7c9`; CURRENT_STATE.md:1 title 2026-10-10, :91 records table still only the 2026-09-30 run; no run-pointer drift test |
| AI-P3-002 | P3 | open | **partially-fixed** | Provenance rule intact (AGENTS.md:89-93); still no CLAUDE.md/.cursor/copilot/windsurf pointer files (find → none); PR template has no authorship field |
| DOC-P2-001 | P3 | verified-fixed | **verified-fixed** | verify_delivery.sh:41-52 wires pack_fidelity.py fail-closed (`pack_fidelity_verdict=PASS|FAIL`). Residual: PACK_VERIFICATION_NOTES.txt has no verdict header, RELEASE_PACK_VERIFICATION.md:81 still "still open" |
| DOC-P3-001 | P3 | verified-fixed | **verified-fixed** | README.md:29 "Suricata 8.0.7" = pins/images.lock:55; README.md:31 "OpenSearch 2.19.6" = pins/images.lock:13 |
| HYGIENE-P3-001 | P3 | verified-fixed | **verified-fixed** | LICENSE (509 B) + NOTICE (662 B) tracked. Minor: README.md:125-128 ownership section still does not link them |
| INV-P3-001 | P3 | open | **open** | check_evidence_index PASS: 1164 metas / 1164 rows / 900 host-absolute resolved / 264 legacy skipped; skip unchanged at check_evidence_index.py:118-120 |
| INV-P3-002 | P3 | verified-fixed | **regressed** | PACK_NOT_INCLUDED.txt:4 again lists the gitleaks .out as "not-in-pack (unexpected; investigate)"; current pack `e665c00f…` genuinely lacks it; cause reproduced: repomix binary detection of ANSI escapes |
| INV-P3-003 | P3 | open | **open** | Wording unchanged: ci/validate.py:524 "A stale digest therefore fails here…"; check_digest_binding.py:11 "a stale package or digest fails closed"; freshness is enforced by check_publication_equality.py |
| INV-P3-004 | P3 | verified-fixed | **verified-fixed** | PACKAGE_MANIFEST.sha256 == review-package/MANIFEST.sha256 (both `80a089be…`); copy wired publish_digests.sh:18 + verify_delivery.sh:38; publication equality PASS |
| INV-P3-005 | P3 | verified-fixed | **verified-fixed** | Same doctrine fix as HYGIENE-P2-003, still intact; residual: EVOLUTION_GUIDE.md:89 step 7 still lacks the declared-manifest exception |

## Per-finding detail

### DOC-P2-002 — Status artifacts lag the live state — **partially-fixed**

- Counts are now consistent end-to-end: `docs/phase9/ALERT_CATALOGUE.yaml` = 94 ids; `bootstrap/90-alerting.sh` = 94 unique `write_rule` UIDs; `alert_rule_lint_test.sh` → `PASS alert_rule_lint (derived_rule_count=94; unique_uids=94; unique_expressions=94)`; live Grafana provisioning API (read-only via `docker exec`) = 94 rules / 94 unique UIDs; set differences catalogue↔live, source↔catalogue, source↔live all empty (regenerated in 73f2d8e "alert catalogue regenerated (94 rules) + counts synced").
- README.md:32 = "94 alert rules"; `readme_ledger_drift_test.sh` → 28 checks / 0 failures; docs/CURRENT_STATE.md:112 = "94 rules live (2026-10-13)".
- Residuals (unchanged from the previous verification):
  - docs/CURRENT_STATE.md:56 (C4 row) still "**93-rule catalogue live** (2026-10-10)".
  - docs/phase9/ALERT_FIRING_PROOFS.md:19-21 ("Current coverage (authoritative)") still "As of 2026-10-03, **75 of the 77 live rules have a firing proof**"; the annotations at :475/:482 say 93 (2026-10-11/12) — one rule behind the live 94; `falcon-wazuh-alert-volume-drop` (catalogue :797, added 2026-10-13) has no proof-status statement in the file.
  - No source→catalogue static check: `alert_rule_lint_test.sh:5-12` parses `90-alerting.sh` but never compares UIDs to the catalogue; `readme_ledger_drift_test.sh:63-88` compares README only to the catalogue, so both can carry the same stale count.
  - EVOLUTION_GUIDE.md:270 §7 state block still dated 2026-10-11 (refreshed from the original 2026-10-01 block, now 3 days behind the 2026-10-13 changes; minor).

### HYGIENE-P2-001 — Large generated SBOM/vulnerability JSON committed — **open**

- Unchanged at edbf441: `find sbom -type f | wc -l` → 42 files (37 JSON), `du -sb sbom/` → 29,565,401 B (29.6 MB); largest `sbom/opensearchproject_opensearch-dashboards_2.19.6.cdx.json` 3,064,465 B — the same size as at the audit.
- Only integrity is bound: `sbom/SBOM_MANIFEST.sha256` + `sbom_hashes.sh verify` (fail on mismatch/unlisted) and the ed25519 signature check (ci/validate.py:540-559; "sbom hashes" PASS in the gate run). No regeneration/expiry/freshness gate exists; the delivery/signing scope remains an owner decision (`docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:158-159`, SBOM-P2-002/004 residuals).

### HYGIENE-P2-002 — Release-gate page carries a superseded audit opinion — **partially-fixed**

- Fixed part (as at 3623d2e): `docs/RELEASE_GATE.md:15-17` lists the newest full-domain runs in the pack and names `falcon-20261011-0416-full-f5cb7c9` (GO WITH CONDITIONS, P0 x0).
- Remains: `docs/RELEASE_GATE.md:51` still headed "## Current audit opinion (run `20261003-0018-fix-backup-abort-markers-20b5e57`, commit `20b5e57`)" with the old NO-GO roll-up; `README.md:140` still "Current state (2026-10-02, audit reconciliation)"; the newest in-repo full run `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1` remains unreferenced there; no drift test (grep of `automation/validation/tests/` and `ci/` for RELEASE_GATE → none).

### HYGIENE-P2-003 — Force-tracked MANIFEST vs doctrine — **verified-fixed**

- The declared-manifest exception is documented everywhere the finding cited: `.gitignore:24-29`, `AGENTS.md:44`, `REPOSITORY.md:33` and `:54`, `automation/validation/build_review_package.sh:9-12` ("EXCEPTION (HYGIENE-P2-003, 2026-10-11) … intentionally tracked").
- `python3 automation/validation/check_publication_equality.py --root .` → PASS, including "declared-commit review-package manifest hash matches digest", "declared-commit review-package entries match digest", "commits after the declared commit touch only publication/test files" (no skip note; the tracked manifest is present). `ci/validate.py` overall → `validation_failures=0`.
- Residual (unchanged, non-blocking): the absent-manifest skip path `check_publication_equality.py:187-191` ("post-publication ancestry restriction skipped") is still fail-open, and `publication_equality_test.sh` has no absent-manifest case; `docs/architecture/EVOLUTION_GUIDE.md:89` (step 7) still says "generated artifact, gitignored — do not commit, HYG-P1-001" without the exception.

### INV-P2-001 — Majority generated content; audit records and mct/ unbound — **open**

- Bound today: `evidence/` via `evidence/MANIFEST.sha256` (`check_generated_drift.py:37` DEFAULT_MANIFESTS = only evidence; PASS "2342 entries match their committed manifests"), `sbom/` via SBOM_MANIFEST, the declared review-package manifest via the digest chain.
- Still unbound: `docs/audits/` run folders (only the structural `audit_run_lifecycle.sh check` → `check_failures=0`; no content manifest), the vendored `mct/` subtree (no import manifest; `mct/VENDORING.md` is still "policy proposed", owner decision pending). The new vendored-compose image pin gate (ci/validate.py:120-125, `pins/supply-chain-waivers.json` roots `mct/compose`) covers image digests only, not the tree.
- The published `PACKAGE_MANIFEST.sha256` residual from this finding remains fixed (INV-P3-004).
- Minor note: `check_generated_drift.py:19-22` docstring still says the review-package manifest is "stale against HEAD (4 mismatches, 1 absent entry; mct/config/examples/secrets.example.env)"; the current comparison yields 6 findings over 3910 entries (3 package-generated files absent + package-README/closeout overlays) — the docstring counts are outdated (see N-4).

### AI-P3-001 — Agent/audit-run pointers stale — **partially-fixed**

- Fixed parts (unchanged since 3623d2e): `AGENTS.md:86`, `README.md:11`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:40`, `docs/RELEASE_GATE.md:16` all name `falcon-20261011-0416-full-f5cb7c9` as the current full-domain run — still the newest full run in the pack (`/tmp/opencode/repo-deep-dive-remote/runs/`; the 20261012/20261014 entries are verification runs).
- Remains: `docs/CURRENT_STATE.md:1` is still titled "Falcon current state (2026-10-10)"; the records table `:91` still lists only the 2026-09-30 run; `:123` mentions only the 2026-10-09 full run — the 2026-10-11 run appears nowhere in the file (`grep -c 20261011 docs/CURRENT_STATE.md` → 0). No doc-drift test asserts that the referenced/newest run resolves (grep of `automation/`/`ci/` → none).

### AI-P3-002 — No AI-provenance policy / per-tool agent coverage — **partially-fixed**

- Fixed part (unchanged since 3623d2e): provenance rule at `AGENTS.md:89-93` (agent commits under the `build-agent` identity, tool/session in the body, `AI-assisted` PR label, never attribute agent output to a human).
- Remains: `find . \( -iname "CLAUDE.md" -o -iname "*copilot*" -o -iname ".cursor*" -o -iname "*windsurf*" -o -iname "GEMINI.md" -o -iname ".aider*" \)` → no files; AGENTS.md is still the only agent-instruction file. `.github/pull_request_template.md` (32 lines) still has no authorship/provenance field.

### DOC-P2-001 — Pack-fidelity not wired into the delivery build — **verified-fixed**

- `automation/validation/verify_delivery.sh:41-52` still runs, before archiving, `python3 automation/validation/pack_fidelity.py /home/user/falcon-repomix.md review-package/MANIFEST.sha256` and increments `fail` on mismatch (fail-closed), printing `pack_fidelity_verdict=PASS|FAIL`; the BOM-only classification is at `pack_fidelity.py:53-58`; the latest publication commits (1008af0 etc.) record "fresh repomix; pack fidelity PASS".
- Residual (unchanged): `PACK_VERIFICATION_NOTES.txt` still carries no verdict/counts header (classification list only, 356 lines); `docs/security/RELEASE_PACK_VERIFICATION.md:81` still says the wiring recommendation "is still open"; `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` still calls pack checks "still local-only | partial" (see N-2).

### DOC-P3-001 — Imprecise version shorthand in the README — **verified-fixed**

- `README.md:29` "Suricata 8.0.7 on the SPAN interface" vs `pins/images.lock:55` `jasonish/suricata:8.0.7`; `README.md:31` "OpenSearch 2.19.6 single node" vs `pins/images.lock:13` `opensearchproject/opensearch:2.19.6` — exact match, unchanged since 3623d2e.

### HYGIENE-P3-001 — No root LICENSE/NOTICE — **verified-fixed**

- `git ls-files | grep -E '(^|/)(LICENSE|NOTICE)$'` → LICENSE, NOTICE; sizes 509 B / 662 B (proprietary, all rights reserved), added in 5e8b262.
- Minor residual (unchanged): `README.md:125-128` ("License / ownership") still does not link LICENSE/NOTICE.

### INV-P3-001 — Legacy host-absolute evidence paths — **open**

- `python3 automation/validation/check_evidence_index.py` → `PASS evidence_index (1164 metas, 1164 rows, 900 host-absolute resolved, 264 legacy skipped)`; the gate (`ci/validate.py`) reports "PASS evidence index cross-check". The index cross-check is consistent (1164 = 900 + 264).
- `check_evidence_index.py:118-120` still short-circuits legacy rows (`if LEGACY_MARKER in norm_artifact: skipped += 1; continue`) instead of resolving them; new metas still record host-absolute paths (900 now, up from 872 at 3623d2e). The resolver (`resolve_evidence_path.py`, test `resolve_evidence_path_test.sh`) and the mapping docs (`REPOSITORY.md:63-74`) exist but consumers must know to run it.
- Adjacent mitigation (verified working): the /tmp-/home-path provenance allowlist — `automation/validation/tests/ledger_provenance_test.sh` → `PASS ledger_provenance (rows=1164; absolute_path_rows=482; allowed_legacy_hashes=479)`; new ledger rows with absolute `/home/` or `/tmp/` paths must be explicitly allowlisted by raw-artifact hash (`automation/validation/ledger_provenance_legacy.sha256`, updated in f82f82f/f23ecff/26b839c). That pins new rows but does not resolve the 264 legacy index rows.

### INV-P3-002 — Pack fidelity artifact ships unresolved entries — **regressed**

- At HEAD, `PACK_NOT_INCLUDED.txt:4` again carries `evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out	not-in-pack (unexpected; investigate)` — the exact unresolved-entry symptom the finding was about. (The second original entry, `mct/config/examples/secrets.example.env`, is in the pack and not listed.)
- The entry is accurate for the current pack: `/home/user/falcon-repomix.md` (17.5 MB, 2026-10-13 23:38, sha256 `e665c00f…` matching `/home/user/falcon-repomix.sha256`, i.e. the latest delivery pack) — parsing it with the repo's own `verify_pack.parse_pack` leaves exactly one evidence-manifest entry absent: the gitleaks `.out`. The file's meta.json is packed; the `.out` (196 B) is not.
- Root cause reproduced (the audit asked to verify, not assume): the file contains ANSI escape sequences; repomix drops it as binary (a minimal re-pack of the file alone: with ESC → not emitted; after `sed 's/\x1b\[[0-9;]*m//g'` → emitted as `## File:`). So it is a renderer/binary-detection artifact, not a missing file — but no disposition is recorded in-repo and the classification still says "investigate".
- History: fixed at 5e8b262 (entry removed; both files present in the then-current pack, verified 2026-10-12), then regenerated at e62348a ("pack verification notes for the f82f82f delivery (fresh repomix…)") where the fresh pack again excluded the file; unchanged through the later deliveries (10ba47e, 02e25f1, 1008af0). A previously fixed finding is broken again at edbf441 → **regressed**.

### INV-P3-003 — "A stale digest fails" enforced by publication equality — **open**

- Wording unchanged: `ci/validate.py:524` still "A stale digest therefore fails here instead of being mistaken for current…"; `automation/validation/check_digest_binding.py:11` still "a stale package or digest fails closed". The check itself only compares declared manifest hashes to the shipped files and resolves the declared commit (no freshness); freshness (non-publication commits after the declared commit) is enforced by `check_publication_equality.py` (ancestry block; skip path :187-191). Neither file was touched for this wording between 3623d2e and edbf441.

### INV-P3-004 — Published PACKAGE_MANIFEST.sha256 stale — **verified-fixed**

- `sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` → both `80a089bec48ebd8e3fdeba62d87835a11dcb4a60e6526e3cb1a845d44a5c4886`; the copy is wired at `automation/validation/publish_digests.sh:18` and `verify_delivery.sh:38`; `check_publication_equality.py` → PASS and `PACKAGE_DIGEST.txt:6` declares the same hash.
- Residual (unchanged): no standalone gate assertion `PACKAGE_MANIFEST == review-package/MANIFEST` (equality holds by construction of the copy step; `readme_ledger_drift_test.sh:106` only checks the file exists).

### INV-P3-005 — HYG-P1-001 doctrine contradiction — **verified-fixed**

- Same doctrine fix as HYGIENE-P2-003, still intact: `.gitignore:24-29`, `AGENTS.md:44`, `REPOSITORY.md:33`/`:54`, `build_review_package.sh:9-12` document the force-tracked `review-package/MANIFEST.sha256` as the declared-commit anchor; `git ls-files -s review-package/` → `100644 … review-package/MANIFEST.sha256`; publication equality PASS.
- Residual (unchanged): `docs/architecture/EVOLUTION_GUIDE.md:89` (step 7) still omits the exception (see N-3).

## New findings

### N-1 (deterministic DET-P2-001; assessed low-impact policy edge) — one CRLF evidence blob is committed

- The deterministic lens reports `DET-P2-001 [PORT] CRLF committed for 1 file(s) (index has CRLF)` with evidence `evidence/raw/REVIEW-FIX/20261013T053408Z_ci-p3-002-stale-workflow-cleanup.out` (new since 3623d2e; captured 2026-10-13, added with the CI-P3-002 work).
- Verified at edbf441: the blob is mixed CRLF/LF (`git show HEAD:<path> | file -` → "ASCII text, with CRLF, LF line terminators"), 2159 B, and it is hash-bound: `evidence/MANIFEST.sha256:2280` lists it (sha256 `b8683a74…` matches the working tree), and `check_generated_drift.py` PASSes over 2342 entries.
- The CRLF policy exists: `.gitattributes` has `* text=auto eol=lf` plus per-type LF rules, and deliberately exempts raw evidence — `*.out -text` / `*.sha256 -text` / `MANIFEST.sha256 -text` ("Cryptographic and generated artifacts: bytes must never be rewritten"). The lens's generic fix ("add .gitattributes, renormalize") is therefore already satisfied and intentionally not applied to this file: renormalizing it would change the raw capture and break the committed evidence manifest hash.
- Disposition: benign as committed; the capture wrapper records raw bytes by design. Recommendation (low priority): record the `.out` byte-preservation exception in the deterministic-waiver notes, or normalize ANSI/CRLF at capture time for CI-tool outputs if the evidence semantics allow — do not renormalize the committed blob in place.

### N-2 (P3) — DOC-P2-001 fix left two docs describing the wiring as open (carry-over, still true)

- `docs/security/RELEASE_PACK_VERIFICATION.md:81` still: "Recommendation 3 above (wire `pack_fidelity.py` into `verify_delivery.sh`) is still open" — contradicted by `verify_delivery.sh:41-52`.
- `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` still: "`pack_fidelity.py` … still local-only | **partial**" — accurate for CI, stale for the delivery build. Also `PACK_VERIFICATION_NOTES.txt` still has no verdict header.

### N-3 (P3, minor) — Residual doctrine/skip-path edges from HYGIENE-P2-003 / INV-P3-005 (carry-over, still true)

- `docs/architecture/EVOLUTION_GUIDE.md:89` (step 7) still says the review package is "gitignored — do not commit, HYG-P1-001" without the declared-manifest exception that AGENTS/REPOSITORY/.gitignore now carry.
- `automation/validation/check_publication_equality.py:187-191` keeps the fail-open skip ("post-publication ancestry restriction skipped") when `review-package/MANIFEST.sha256` is absent; the tracked manifest makes it unreachable in practice, but no test pins it closed (`publication_equality_test.sh` has no absent-manifest case).

### N-4 (P4, minor) — check_generated_drift.py docstring counts are outdated

- `automation/validation/check_generated_drift.py:19-22` still says the review-package manifest is "stale against HEAD (4 mismatches, 1 absent entry; `mct/config/examples/secrets.example.env`)". At edbf441 the same command reports 6 findings over 3910 entries: 3 absent package-generated files (`OWNER_ACCEPTANCE.md`, `REVIEWER_CHECKLIST.md`, `vuln-summary.csv`) and 3 expected package-build overlays (`README.md` = the `docs/phase8/review-package-extras/README.md` overlay; `closeout/FINAL_RESPONSE*.json` regenerated at publication). The named `secrets.example.env` is no longer among them. Cosmetic, but the docstring should be re-derived rather than hand-maintained.

## Verification commands (selected)

```bash
git -C /home/user/falcon-build rev-parse HEAD                 # edbf441…; status clean
python3 ci/validate.py                                        # validation_failures=0 (52 shell suites)
python3 automation/validation/check_evidence_index.py         # PASS 1164 metas / 1164 rows / 900 host-absolute / 264 legacy
python3 automation/validation/check_generated_drift.py        # PASS 2342 entries
python3 automation/validation/check_publication_equality.py --root .   # PASS (declared-commit checks)
python3 automation/validation/check_digest_binding.py --root .         # PASS
bash automation/validation/tests/alert_rule_lint_test.sh      # PASS 94/94/94
bash automation/validation/tests/readme_ledger_drift_test.sh  # 28 checks / 0 failures
bash automation/validation/tests/ledger_provenance_test.sh    # PASS rows=1164 abs=482 allow=479
sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256       # 80a089be… both
# live Grafana (read-only, docker exec; counts only):
# GET /api/v1/provisioning/alert-rules -> live_rules 94, unique_uids 94 (set-identical to catalogue/source)
# pack (latest delivery, sidecar match e665c00f…): exactly 1 evidence-manifest entry absent =
#   evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out
#   (reproduced: repomix drops it as binary due to ANSI escapes; stripping ESC packs it)
```

No secrets were printed; the live Grafana check read `/srv/falcon/secrets/grafana_admin.pw` via sudo and emitted counts only.
