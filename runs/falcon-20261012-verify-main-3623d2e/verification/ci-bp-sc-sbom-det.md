# Post-merge verification — CI / BP / SC / SBOM / DET (18 findings)

- **Repo**: `MaineCyberTech/falcon` (private), current `main` = **3623d2e** (`publication: bind (closeout + digest at the declared commit d1e5e75)`), working tree `/home/user/falcon-build`.
- **Original run**: `falcon-20261011-0416-full-f5cb7c9` (audit commit f5cb7c9).
- **Method**: read-only. Repo/file inspection at HEAD; live GitHub REST reads (read-only token); live lab checks (DO site host read-only SSH); machine re-run of `tools/deterministic_checks.py /home/user/falcon-build -o /tmp/opencode/verify-out/det --run falcon-verify`; job-log reads for the affected workflows.
- **Verdicts**: **5 closed, 13 still-open (6 of them partial), 0 regressed.** Three new findings (NEW-1 P2, NEW-2 P3 tooling, NEW-3 P3 doc drift) are listed at the end.
- Fix commits referenced: `e094473` (2026-10-11, CI pin + Actions defaults), `3b0b976` (2026-10-11, CODEOWNERS), `5e8b262` (2026-10-11, LICENSE/NOTICE + SBOM signing), `0b24a70`+`e38cc48` (2026-10-11, manifest sync), `e5cd38a`/`4c74f31` (2026-10-11, rotation rows 1–2), `0575e8b` (2026-10-12, CI caching).

## Summary table

| ID | Sev | Original status | Verdict | Evidence (short) |
|---|---|---|---|---|
| BP-P2-001 | P2 | verified-fixed | **closed** | `.github/CODEOWNERS:7-14` = `@HenryTru0518`; live `codeowners/errors` = `{"errors":0}`; owner has `admin` (API); fix `3b0b976` |
| BP-P3-001 | P3 | open | **still-open** | label `dependabot-approved` now exists, but 0 Dependabot PRs ever (55 closed/0 open, 0 authored by app/dependabot); sweeps log "no open dependabot PRs"; no exercise record; **plus NEW-1 (gh missing)** |
| CI-P2-001 | P2 | open | **still-open (partial)** | head-commit pin added (`dependabot-merge.yml:54`, `--match-head-commit`, fix `e094473`); `contents: write`/`pull-requests: write` unchanged (:18-19); `environments` API `total_count: 0`; merge path broken by NEW-1 |
| CI-P2-002 | P2 | open | **still-open (narrow)** | header rescoped (`external-smoke.yml:5-9`); DO-watcher posture check deployed+live (302→cloudflareaccess.com, `posture`=ok); **but job summary :71 still says "must be 302 to cloudflareaccess.com (Access still enforcing)"** and runs-on comment :26-28 still says "stays on hosted" |
| CI-P2-003 | P2 | open | **still-open (partial)** | live `/actions/permissions/workflow` = `read`/`false` (fixed); `allowed_actions: "all"`, `sha_pinning_required: false` remain |
| CI-P3-001 | P3 | open | **still-open** | hosted fallback still at `validate.yml:28`; no notification step in any workflow; Oct 6–8 sweeps queued ~24 h then cancelled (37460608720/37616708114/37774326519) |
| CI-P3-002 | P3 | open | **still-open** | API still lists lab-probe (374465077), lab-pwsh-probe (374566273), testnuc-runner-verify (374995041) `state=active`; contents API = `Not Found` for all 3 paths on main; no commit ever touched them |
| CI-P3-003 | P3 | open | **closed** | playbook §8 updated (`CI_CD_INCIDENT_PLAYBOOK.md:268-275`) citing `CI_TOOL_PINS.md` + captured green runs; run 38110410254 = success @ f5cb7c9 |
| CI-P3-004 | P3 | open | **still-open (partial)** | `REPOSITORY.md:53` corrected ("CI does not currently build it - CI-P3-004"); `README.md:120` still claims "delivered as a CI/release artifact"; no CI refs; 0 artifacts, 0 releases |
| DET-P3-001 | P3 | open | **closed** | `LICENSE` + `NOTICE` tracked (fix `5e8b262`); deterministic re-run no longer emits it |
| DET-P3-002 | P3 | open | **still-open** | host re-run still emits `[SEC] gitleaks not installed`; `which gitleaks` rc=1; CI now installs/runs gitleaks (`validate.yml:88-99`) |
| DET-P3-003 | P3 | open | **still-open** | tracked tree still **29** unpinned images (36 pinned); unchanged; `mct/compose` under blanket waiver (review_by 2026-12-31); re-run reported 58 (see NEW-2) |
| SBOM-P2-001 | P2 | open | **still-open (partial)** | ed25519 signing implemented + live-verified PASS; remaining: no SBOM hash in `PACKAGE_DIGEST.txt`; no image/SBOM license gate (`pins/licenses.allow` absent); stale "NOT signed" text in `sbom_hashes.sh` |
| SBOM-P3-001 | P3 | open | **still-open** | `build_review_package.sh:41,53,73` still ships only `vuln-summary.csv` and deletes `*.cdx.json`; `PACKAGE_MANIFEST.sha256` has 0 `cdx.json` entries; `review-package/` has no `sbom/`; D2 still "OWNER/POLICY DECISION REQUIRED" |
| SBOM-P3-002 | P3 | open | **still-open** | doc :82-83 still says "`--require-vuln` stays off"; `validate.yml:126` enforces `--require-vuln --vuln-waivers`; no append-only correction |
| SC-P2-002 | P2 | open | **still-open (partial)** | rows 1–2 now ROTATED with captures; 18/20 still PENDING; 20 vendored scripts still `set -a` + wholesale source; doc still says 28 |
| SC-P3-001 | P3 | verified-fixed | **closed** | `sha256(PACKAGE_MANIFEST.sha256)` = `sha256(review-package/MANIFEST.sha256)` = digest `7e2526ae…` (3842 entries); `publish_digests.sh:18` copies on every bind; equality check wired (`ci/validate.py:471,651`) |
| SC-P3-002 | P3 | verified-fixed | **closed** | live `/automated-security-fixes` = `{"enabled":true,"paused":false}`; pip ecosystem present in `.github/dependabot.yml`; `/dependabot/alerts` open = 0 |

---

## Per-finding detail

### BP-P2-001 — CODEOWNERS invalid (P2) → **closed**
- Current file uses a resolvable user, not the org handle: `.github/CODEOWNERS:7` `* @HenryTru0518`, `:10-14` sensitive trees (`/.github/`, `/ci/`, `/bootstrap/`, `/pins/`, `/secrets/`).
- Live API: `GET /repos/MaineCyberTech/falcon/codeowners/errors` → `{"errors":0,"sample":[]}` (was 6 `Unknown owner`).
- `GET /collaborators/HenryTru0518/permission` → `"role_name":"admin"`, `permissions.admin=true`.
- Fix commit `3b0b976` (2026-10-11); header comment records the BP-P2-001 closure.

### BP-P3-001 — Dependabot auto-merge control never exercised (P3) → **still-open**
- Label created: `GET /labels` now includes `dependabot-approved` (plus `AI-assisted`); this part is fixed.
- Still never exercised: `GET /pulls?state=all` → 55 closed + 0 open, **0 authored by `app/dependabot`**. Sweeps 38135559364 (2026-10-11) and 38254211113 (2026-10-12) logged "no open dependabot PRs"; no captured merge/refuse behavior; `docs/security/BRANCH_PROTECTION.md:95` still asserts the gate is live without an exercise date.
- **Blocked by NEW-1**: since 2026-10-05 the runners lack `gh`, so the sweep can never see or merge a Dependabot PR even if one appears.

### CI-P2-001 — auto-merge write scope / no env / no head pin (P2) → **still-open (partial)**
- Fixed part: `.github/workflows/dependabot-merge.yml:51-54` reads `headRefOid` and merges with `--match-head-commit "$head_sha"` (fix `e094473`; comment :50-53 cites CI-P2-001). No TOCTOU window remains in the command.
- Remaining: `:18-19` still declare `contents: write` + `pull-requests: write`; live `GET /environments` → `{"total_count":0}` (comment :20-23 documents plan-blocked environment protection; the label is the compensating human gate).
- NEW-1: the gh-based control is currently non-functional on the runners.

### CI-P2-002 — external-smoke Access posture (P2) → **still-open (narrow residual)**
- Header now honest: `external-smoke.yml:5-9` ("CANNOT assert Cloudflare Access enforcement… asserted from a non-owner vantage by the independent site host watcher").
- Replacement control live-verified: DO host `mct-portal-dev` (10.99.0.10) runs `/opt/falcon-watcher/watch.sh` with the posture section (`:56-81`); `cat /var/lib/falcon-watcher/posture` = `ok` (2026-10-12 20:05Z); log tail: `posture ok: https://falcon… -> 302 (Cloudflare Access)` + iris + soc + enroll. So an Access regression on iris/soc **is** now detected externally.
- Remaining (the artifact still misstates what was verified):
  - `external-smoke.yml:71` step summary: `"- iris/soc: must be 302 to cloudflareaccess.com (Access still enforcing)"` — echoed in the latest run 38156466921 log while the check itself printed "Access enforcement NOT asserted from this vantage".
  - `external-smoke.yml:26-28` job comment still says "Must run from GitHub's network… so it stays on hosted" although `:29` runs `[self-hosted, lab]`.
- Note: `check_gated` accepting any 302 is now by design (origin reachability only), correctly labelled in the step output (`:46`).

### CI-P2-003 — permissive repository Actions defaults (P2) → **still-open (partial)**
- Live `GET /actions/permissions/workflow` → `{"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}` (fixed 2026-10-11; decision log 2026-10-11T06:00Z).
- Live `GET /actions/permissions` → `{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}` — the "any marketplace action" and "no server-side SHA-pin" parts remain (no decision-log record found accepting them; all workflows pin manually + zizmor).

### CI-P3-001 — hosted fallback dead; silent scheduled failures (P3) → **still-open**
- (a) `validate.yml:28` still falls back to `'ubuntu-latest'` for fork PRs; hosted runners are billing-blocked (`external-smoke.yml:29` comment). Latent (private repo).
- (b) Silent queue failure class unchanged: dependabot-merge runs 37460608720 (Oct 6), 37616708114 (Oct 7), 37774326519 (Oct 8) were queued ~24 h then `cancelled` with no alert; Oct 9–12 sweeps succeeded. No watchdog.
- (c) `grep -rn 'ntfy|notify|webhook' .github/workflows/` → only the comment `external-smoke.yml:9`; no workflow posts failures anywhere. The weekly validate schedule now runs green (e.g. run 343, 2026-10-12T15:24Z success), but detection remains manual.

### CI-P3-002 — probe workflows registered with no file (P3) → **still-open**
- Live `GET /actions/workflows` (total 8) still lists `lab-probe` (374465077), `lab-pwsh-probe` (374566273), `testnuc-runner-verify` (374995041, `.github/workflows/testnuc-verify.yml`), all `state=active`.
- Tree has only `validate.yml`, `external-smoke.yml`, `dependabot-merge.yml`; `GET /contents/<path>?ref=main` = `"Not Found"` for all three; `git log --all` shows no commit touching those paths. Inventory drift persists (branch pushes can still run code on lab runners).

### CI-P3-003 — CI/CD playbook §8 stale (P3) → **closed**
- `docs/security/CI_CD_INCIDENT_PLAYBOOK.md:268-275` now: all CI tools SHA-256-verified, `CI_TOOL_PINS.md` referenced, and "Captured falcon `validate` runs exist… closed (CI-P3-003, 2026-10-11)".
- Cross-checked: `validate.yml:45-73` verifies actionlint/shellcheck/ruff/gitleaks tarballs by SHA-256; `ci/requirements-ci.txt` hash-pinned; run 38110410254 = `validate` success at `head_sha f5cb7c9` (run 311).

### CI-P3-004 — review package not built by CI (P3) → **still-open (partial)**
- `README.md:120` still: "it is delivered as a CI/release artifact" — no workflow references `build_review_package.sh`, `verify_delivery.sh`, `upload-artifact`, `id-token`, or attestations; live `GET /actions/artifacts` `total_count: 0`, `GET /releases` 0.
- `REPOSITORY.md:53` was corrected: "it is built on demand; CI does not currently build it - CI-P3-004". One of the two doc sites fixed; README claim remains unbacked.

### DET-P3-001 — no LICENSE (P3) → **closed**
- `git ls-files` → `LICENSE`, `NOTICE` (both added by `5e8b262`, 2026-10-11; decision log records "DET-P3-001 closed").
- Machine re-run (`/tmp/opencode/verify-out/det/deterministic-findings.json`) no longer contains the `[GIT] No LICENSE file` finding.

### DET-P3-002 — gitleaks not installed (P3) → **still-open**
- Host still lacks gitleaks: `which gitleaks` → rc=1; re-run emits `DET-P3-001 [SEC] gitleaks not installed (secret scan skipped)` (renumbered in the new run; original ID DET-P3-002).
- CI side is fixed: `validate.yml:88-99` downloads pinned gitleaks (SHA-256 `551f6fc8…`), runs the tree scan, plus the fail-closed history scan (`:100-102`). So the finding's "install in CI" suggestion is done, but the host-side deterministic check still skips the scan.

### DET-P3-003 — 29 images without digest pin (P3) → **still-open**
- Tracked tree unchanged: **29** unpinned `image:` refs (36 pinned) across `mct/compose/*` and `compose/*`; e.g. `mct/compose/docker-compose.greenbone.yml:5` `registry.community.greenbone.net/community/vulnerability-tests`, `mct/compose/docker-compose.misp.yml:61` `ghcr.io/misp/misp-docker/misp-modules:latest`.
- These are under the owner-visible blanket waiver `pins/supply-chain-waivers.json` (`compose_digest` root `mct/compose`, ref `*`, review_by 2026-12-31) — knowingly waived, still open per the deterministic baseline.
- See NEW-2: the re-run count (58) doubles the tracked count because the tool walks the untracked generated `review-package/` copy.

### SBOM-P2-001 — unsigned release/SBOM artifacts; no license gate (P2) → **still-open (partial)**
- **Signing fixed and verified live**: `automation/validation/sign_sbom_manifest.sh` (ed25519, root-only key `/srv/falcon/secrets/sbom_signing_ed25519`); committed `sbom/SBOM_SIGNING.pub`, `sbom/SBOM_SIGNING.allowed_signers`, `sbom/SBOM_MANIFEST.sha256.sig` (306 B); `ci/validate.py:512-551` verifies the signature (`sbom-hashes` check). I re-verified at HEAD:
  `ssh-keygen -Y verify … < sbom/SBOM_MANIFEST.sha256` → `Good "falcon-sbom" signature for falcon-sbom-signing with ED25519 key SHA256:mTlQOWjhVymwkHWbdXw+fD9/e8dyupOiDFD3d3koQvQ`.
- Remaining:
  1. `PACKAGE_DIGEST.txt` has **no** `sbom_manifest_sha256` field and `publish_digests.sh` does not reference `sbom/` — the manifest hash is not bound into the delivery digest (the fix's second half).
  2. Image/SBOM license allow-deny gate still absent: `pins/licenses.allow` does not exist; `ci/license_check.py` scans installed Python distributions only; doc still marks the follow-up open.
  3. Stale text after the fix: `automation/validation/sbom_hashes.sh:13-14,68,84` still says "The manifest is NOT signed… manifest unsigned"; `verify_publication_chain.sh:112` still calls the 2026-09-29 archives "signed" while only verifying SHA-256 (:118-127).

### SBOM-P3-001 — review package excludes the SBOM set (P3) → **still-open**
- `build_review_package.sh:41` copies only `sbom/vuln-summary.csv`; `:53` `find "$PKG" -name '*.cdx.json' -delete`; `:73` prints the exclusion.
- `PACKAGE_MANIFEST.sha256` (3842 entries) contains 0 `cdx.json` entries; on-disk `review-package/` has no `sbom/` directory; decision D2 in `SBOM_COVERAGE_AND_PROVENANCE.md:159` is still `OWNER/POLICY DECISION REQUIRED`.

### SBOM-P3-002 — doc contradicts the enforced vuln gate (P3) → **still-open**
- Doc still says the opposite of the workflow: `SBOM_COVERAGE_AND_PROVENANCE.md:82-83` "The step enforces coverage only: `--require-vuln` stays off…"; `:174` repeats the old framing.
- Actual CI gate: `validate.yml:126` runs `sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json` (waivers `review_by` 2026-12-31); `:127` runs `sbom_hashes.sh verify`.
- No append-only correction exists (the only 2026-10-11 addition to the doc is the Signing section).

### SC-P2-002 — rotation pending + wholesale credential sourcing (P2) → **still-open (partial)**
- Progress: `docs/security/CREDENTIAL_ROTATION_REGISTER.md:20-21` rows 1 (SUDO_PASSWORD) and 2 (WAZUH_ADMIN_PASSWORD) are now `ROTATED` with capture IDs (fixes `e5cd38a`, `4c74f31`); validator `check_rotation_register.py` fails closed on unsupported ROTATED rows.
- Remaining: rows 3–20 `PENDING` (18/20); register `:13` still shows the dated "Status as of 2026-10-04: 20/20 PENDING"; `mct/scripts/` still has **20** scripts combining `set -a` with sourcing a credential env file wholesale (e.g. `mct/scripts/full-stack-healthcheck.sh:16`, `p33-core-alert.sh:16`, `backup-dr-audit.sh:36,84`); `INHERITED_CREDENTIAL_ROTATION.md:20,72` still claims 28 scripts.

### SC-P3-001 — published PACKAGE_MANIFEST stale (P3) → **closed**
- Live equality: `sha256sum PACKAGE_MANIFEST.sha256` = `sha256sum review-package/MANIFEST.sha256` = `7e2526aeb85bf6dd614bac3d25b26aa43338d2532e2053b6904e5d9bd2b2686b` = `PACKAGE_DIGEST.txt:review_package_manifest_sha256`; entries 3842 = declared `review_package_entries=3842`.
- Refresh wired: `publish_digests.sh:16-19` copies `review-package/MANIFEST.sha256` → `PACKAGE_MANIFEST.sha256` on every bind (fix `0b24a70`; rebind `e38cc48`); `verify_delivery.sh:38` also refreshes.
- New equality check exists and is wired into CI: `automation/validation/check_publication_equality.py:148-152` ("digest review_package_manifest_sha256 matches shipped manifest"), registered in `ci/validate.py:471,651`.
- `PACK_VERIFICATION_NOTES.txt` / `PACK_NOT_INCLUDED.txt` refreshed: 0 `unexpected; investigate` entries (was 2); PACK_NOT_INCLUDED now lists 3 package-generated files with reasons.

### SC-P3-002 — Dependabot security updates disabled (P3) → **closed**
- Live `GET /automated-security-fixes` → `{"enabled":true,"paused":false}` (was `enabled:false`); `GET /dependabot/alerts?state=open` → 0 open; `.github/dependabot.yml` still has the pip ecosystem for `ci/requirements-ci.txt`.

---

## New findings

### NEW-1 (P2, BP/CI) — `gh` CLI missing on the self-hosted runners; the Dependabot merge sweep silently no-ops
- **What**: `.github/workflows/dependabot-merge.yml:37` uses `mapfile -t PRS < <(gh pr list …)`. On the runners `gh` is not installed; the process-substitution failure does not fail `mapfile`/the step, so the array is empty, the script prints `no open dependabot PRs`, exits 0, and the run is reported **success**. The label gate (BP-P3-001) and the head-commit pin (CI-P2-001) can therefore never act, and nothing signals it.
- **Live evidence** (job logs, read via API; same pair of lines in every run):
  - 2026-10-12T13:13:42.359Z job 114827948932 (ci-runner, run 38254211113): `line 1: gh: command not found` → `no open dependabot PRs`
  - 2026-10-11T11:26:26.830Z job 114458579876 (lab-runner-2, run 38135559364): same
  - 2026-10-10T11:12:54.111Z job 114200200490 (edge-builder, run 38047609916): same
  - 2026-10-09T18:43:36.238Z job 113810472549 (lab-runner-2, run 37926819556): same
  - 2026-10-05T12:19:39.671Z job 111758692294 (lab-runner-2, run 37308749667): same
  - 2026-10-04T11:08Z job 111422936464 (ci-runner, run 37197723327): **no error** (gh worked then) — the breakage window starts ~2026-10-05.
- **Impact**: the compensating control that replaces plan-gated required review is non-functional and invisible; `BRANCH_PROTECTION.md:95` still asserts the gate is live. Combined with BP-P3-001 (never exercised), the failure mode is now observed in production.
- **Suggested fix**: fail closed if `command -v gh` is missing; install `gh` on the lab runners (or replace with API `curl` calls); capture a skip/merge exercise once a Dependabot PR exists.

### NEW-2 (P3, audit tooling) — deterministic re-run double-counts unpinned images from the untracked `review-package/`
- `tools/deterministic_checks.py` walks the working tree without honoring `.gitignore`; the generated, gitignored `review-package/` tree exists on the lab, so the SUPPLY check counted each `mct/compose` file twice: re-run title `[SUPPLY] 58 container image(s) without a digest pin` (evidence includes `review-package/mct/compose/*`) vs the **tracked** count of **29** (unchanged from the baseline).
- No repo regression here (the 29 tracked are the same set), but the machine re-audit baseline comparison must exclude `review-package/` (or the tool should skip generated/gitignored trees) to avoid false P3s in future runs.

### NEW-3 (P3, SBOM doc/code drift) — stale "unsigned" wording after the signing fix
- `automation/validation/sbom_hashes.sh:13-14,68,84` still says the manifest is NOT signed / "manifest unsigned" although `sbom/SBOM_MANIFEST.sha256.sig` now exists and CI verifies it; `verify_publication_chain.sh:112` still labels the 2026-09-29 archives "signed" while checking only SHA-256 bytes. Cosmetic but contradicts the new control (overlaps SBOM-P2-001 residual). Fix: refresh the comments/labels to distinguish integrity vs ed25519 authorship.

## Notes / limitations
- All GitHub reads were read-only (`Authorization: Bearer` from `/home/user/.env`, never printed). No repo files were modified.
- The DO-host check was read-only SSH (`chat-ci` key): `hostname`, `grep`, `cat`, `stat`, `tail` only.
- No P0/P1 regressions found in the assigned areas. The `validate`/`external-smoke`/`dependabot-merge` workflows are otherwise green at 3623d2e (latest validate run 345 success, 2026-10-12T19:45Z).
