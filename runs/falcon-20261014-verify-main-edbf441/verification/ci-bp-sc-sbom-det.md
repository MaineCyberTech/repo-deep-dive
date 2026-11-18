# Post-merge verification re-audit — CI / BP / SC / SBOM / DET findings

- **Repo**: `MaineCyberTech/falcon` (private), current `main` = **edbf441** (`publication: bind (closeout + digest at the declared commit c045e78)`), working tree `/home/user/falcon-build` (read-only, clean).
- **Date**: 2026-10-14. **Original run**: `falcon-20261011-0416-full-f5cb7c9` (audit commit f5cb7c9). **Previous verification**: 2026-10-12 @ `3623d2e`.
- **Method**: read-only. Repo/file inspection at edbf441 (`git cat-file`/`git grep`); live GitHub REST reads with the `gh_api` token from `/home/user/.env` (never printed); live lab checks (`systemctl`, `/srv/falcon/textfile`); read-only SSH to the DO watcher host (`chat-ci` key); machine re-run of `tools/deterministic_checks.py /home/user/falcon-build` at edbf441; job-log reads for the affected workflow runs.
- **Verdicts**: **8 verified-fixed, 4 partially-fixed, 6 open, 0 owner-accepted, 0 regressed.** Two follow-ups under New findings (the `gh`-on-runner residual from the previous NEW-1, and a pack-metadata drift); DET-P2-001 (CRLF) is verified in the supplementary section (not in this scope).
- **Commits since 3623d2e referenced**: `ee4be3f` (2026-10-12, external-smoke/SBOM wording), `f23ecff`+`d6fb8d3`+`e02ae57` (2026-10-13, CI-P3-001/002), `b90498d`+`52a5ccc` (owner defaults: license gate, rotation round 2), `e62348a` (pack notes), `ce76ef0`, `11623a1`, `edbf441`.

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| BP-P2-001 | P2 | verified-fixed | **verified-fixed** | `.github/CODEOWNERS:7-14` = `@HenryTru0518`; live `codeowners/errors` = `{"errors":[]}` |
| CI-P2-001 | P2 | open | **partially-fixed** | head pin `dependabot-merge.yml:54`; `contents: write`/`pull-requests: write` (:18-19) + 0 environments; sweep still `gh: command not found` on edge-builder (run 38399605845) |
| CI-P2-002 | P2 | open | **verified-fixed** | stale text fixed (`external-smoke.yml:29-31,73`, ee4be3f); DO watcher live 2026-10-14T00:35Z `posture ok` |
| CI-P2-003 | P2 | open | **partially-fixed** | live workflow defaults `read`/`false`; `allowed_actions:"all"`, `sha_pinning_required:false` remain |
| SBOM-P2-001 | P2 | open | **partially-fixed** | signature `Good "falcon-sbom"`; license gate now `pins/licenses.allow` + `ci/validate.py:638-667,731`; no sbom hash in `PACKAGE_DIGEST.txt` (D1 open) |
| SC-P2-002 | P2 | open | **partially-fixed** | 2 ROTATED + 7 DONE + 11 PENDING; 20 vendored `set -a` scripts; docs still say 28 |
| BP-P3-001 | P3 | open | **open** | label exists; 0 Dependabot PRs ever; sweep no-ops (`gh` missing on edge-builder); no exercise record |
| CI-P3-001 | P3 | open | **verified-fixed** | `validate.yml:31-32` fork-PR skip; watchdog timer active (last run 00:30Z); live `falcon_ci_*` ok; test PASS (16) |
| CI-P3-002 | P3 | open | **verified-fixed** | live API 5 workflows (3 stale registrations gone); retire captures tracked |
| CI-P3-003 | P3 | verified-fixed | **verified-fixed** | playbook §8 closure (lines 273-279); validate green at edbf441 |
| CI-P3-004 | P3 | open | **open** | `README.md:120` still "delivered as a CI/release artifact"; 0 artifacts / 0 releases |
| DET machine findings | — | — | — | carried in `lens_deterministic.md` + the register (4 rows: new P2 CRLF blob; gitleaks/hadolint host-env; 29 unpinned) — not repeated here |
| SBOM-P3-001 | P3 | open | **open** | `build_review_package.sh:41,53,73`; manifest 0 sbom/cdx entries; D2 still OWNER/POLICY DECISION REQUIRED |
| SBOM-P3-002 | P3 | open | **open** | doc:82 "`--require-vuln` stays off" vs `validate.yml:130` enforcing it; no correction |
| SC-P3-001 | P3 | verified-fixed | **verified-fixed** | manifest sha == digest `80a089be…`, 3910 entries; `publish_digests.sh:18`; equality check wired |
| SC-P3-002 | P3 | verified-fixed | **verified-fixed** | live `/automated-security-fixes` = enabled:true; open Dependabot alerts 0 |

---

## Per-finding detail

### BP-P2-001 — CODEOWNERS invalid — **verified-fixed**
- `.github/CODEOWNERS:7` `* @HenryTru0518`; `:10-14` sensitive trees (`/.github/`, `/ci/`, `/bootstrap/`, `/pins/`, `/secrets/`) all `@HenryTru0518`; header comment records the BP-P2-001 fix.
- Live: `GET /repos/MaineCyberTech/falcon/codeowners/errors` -> `{"errors":[]}`. Unchanged from 3623d2e.

### CI-P2-001 — auto-merge write scope / no env / no head pin — **partially-fixed**
- Head-commit pin still present: `dependabot-merge.yml:51-54` reads `headRefOid` and merges with `--match-head-commit "$head_sha"`.
- Residual unchanged: `:18-19` `contents: write` + `pull-requests: write`; live `GET /environments` -> `{"total_count":0}` (plan-blocked, comment `:20-23`); the label is the compensating gate.
- **New live evidence**: the gh-based merge path is still non-functional on the runner that executed the latest sweep — run `38399605845` job `115303529830` (edge-builder, 2026-10-13T12:45Z) log: `/home/runner/actions-runner/_work/_temp/….sh: line 1: gh: command not found` then `no open dependabot PRs`, exit 0. So the pin/label control cannot act when the job lands on that runner.

### CI-P2-002 — external-smoke Access posture — **verified-fixed**
- The two stale-text residuals from 2026-10-12 are fixed by `ee4be3f`: `external-smoke.yml:29-31` runs-on comment now "Runs on the lab runner (GitHub-hosted is billing-blocked): availability/reachability only…", and the job summary `:73` now "iris/soc: reachable (the lab vantage cannot assert Access; the DO watcher does)".
- Latest run `38446409098` (2026-10-13T18:24Z) log confirms the honest wording: `OK https://iris… -> 302 (owner-IP bypass: origin reachable; Access enforcement NOT asserted from this vantage)`.
- External assertion live-verified (read-only SSH, 2026-10-14T00:35Z): host `mct-portal-dev` posture file = `ok`, log tail `posture ok: https://falcon/iris/soc.mainecybertech.us/ -> 302 (Cloudflare Access)`, `enroll -> 404`; deployed `/opt/falcon-watcher/watch.sh` sha256 `239d3a4c…` == repo blob `automation/alerting/do_watcher/watch.sh`; cron `*/5`.
- Owner decision log 2026-10-12T22:10Z records the DO watcher (5-min, non-owner vantage) as the accepted Access-enforcement check. Remaining "required external check" is plan-gated and covered by the owner-accepted BP-P1-001 compensating controls.

### CI-P2-003 — permissive repository Actions defaults — **partially-fixed**
- Live `GET /actions/permissions/workflow` -> `{"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}` (fixed 2026-10-11).
- Live `GET /actions/permissions` -> `{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}` — unchanged; no decision-log/acceptance record found for these two (grep of `ledgers/decision_log.md` for allowed_actions/sha_pinning empty). All workflows pin manually and zizmor runs.

### SBOM-P2-001 — unsigned artifacts / license gate — **partially-fixed**
- Signing re-verified at edbf441: `ssh-keygen -Y verify -f sbom/SBOM_SIGNING.allowed_signers -I falcon-sbom-signing -n falcon-sbom -s sbom/SBOM_MANIFEST.sha256.sig < sbom/SBOM_MANIFEST.sha256` -> `Good "falcon-sbom" signature for falcon-sbom-signing with ED25519 key SHA256:mTlQOWjhVymwkHWbdXw+fD9/e8dyupOiDFD3d3koQvQ`.
- **Newly fixed since 3623d2e**: the image/SBOM license gate exists — `pins/licenses.allow` (491 lines; ~486 accepted licenses) + `ci/validate.py:638-667` `check_sbom_licenses` (new licenses fail), wired at `:731`; owner default recorded 2026-10-12T22:10Z. `automation/validation/sbom_hashes.sh` stale "NOT signed" wording fixed by `ee4be3f` (`:13-18,69,85` now "signed ed25519").
- Remaining: `PACKAGE_DIGEST.txt` has no `sbom_manifest_sha256` field (grep shows only review_package/evidence hashes); D1 is still `OWNER DECISION REQUIRED` (`docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:158`). Minor: `automation/validation/verify_publication_chain.sh:112` still labels the 2026-09-29 archives "signed" while only verifying SHA-256 bytes (`:118-129`).

### SC-P2-002 — rotation pending + wholesale credential sourcing — **partially-fixed**
- (a) Progress since 3623d2e: register rows now **2 ROTATED** (rows 1-2) + **7 DONE** with the VM101-decommission capture (rows 10,13,14,15,16,18,20) + **11 PENDING** owner-console (rows 3-9,11,12,17,19) — `docs/security/CREDENTIAL_ROTATION_REGISTER.md:20-39`. Header `:13` still says "Status as of 2026-10-04: **20/20 PENDING**".
- (b) Unchanged: `git grep -l "set -a" edbf441 -- 'mct/scripts/*'` = **20** files combining `set -a` with wholesale credential sourcing (e.g. `mct/scripts/full-stack-healthcheck.sh:16`, `p33-core-alert.sh:16`); `docs/security/INHERITED_CREDENTIAL_ROTATION.md:20,72` still claims **28** scripts.

### BP-P3-001 — Dependabot auto-merge never exercised — **open**
- Label `dependabot-approved` exists (live `/labels`), but `GET /pulls?state=all` = 55 closed / 0 open, **all authored by JulianB-MCT** (0 by `app/dependabot`); no exercise record; `docs/security/BRANCH_PROTECTION.md:84-86` still asserts "The Dependabot label gate is live".
- Latest sweep `38399605845` (2026-10-13, edge-builder) logged `gh: command not found` -> "no open dependabot PRs" (success), so the gate still cannot merge or refuse anything (see New findings).

### CI-P3-001 — dead hosted fallback + silent failures — **verified-fixed**
- (a) Fallback removed: `validate.yml:31` `if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository`; `:32` `runs-on: [self-hosted, linux, x64, lab-python]`; no `ubuntu-latest` anywhere in `.github/workflows/` (grep); fork-PR policy documented (`validate.yml:26-30`, `CI_CD_INCIDENT_PLAYBOOK.md:282-285`).
- (b) Watchdog live: `systemctl status falcon-ci-watchdog.timer` -> `enabled; active (waiting)` since 2026-10-13 05:44Z, last run 2026-10-14T00:30Z, next 00:45Z; `/srv/falcon/textfile/falcon_ci.prom` -> `falcon_ci_queued_runs 0`, `falcon_ci_queued_oldest_seconds -1`, `falcon_ci_scheduled_failures_24h 0`, `falcon_ci_watchdog_ok 1`, last-run timestamp fresh; state file `ok`.
- Units + script + test tracked by `f23ecff` (`config/systemd/falcon-ci-watchdog.{service,timer}`, `automation/validation/ci_run_watchdog.sh`, `automation/validation/tests/ci_run_watchdog_test.sh`); test re-run -> `PASS (16 checks)`; playbook §5.6 + detection table updated (`CI_CD_INCIDENT_PLAYBOOK.md:224-229,249-252,282-288`).

### CI-P3-002 — stale probe workflow registrations — **verified-fixed**
- Live `GET /actions/workflows` -> `total_count: 5`: `dependabot-merge`, `external-smoke`, `validate` + the two dynamic Dependabot workflows. `lab-probe` (374465077), `lab-pwsh-probe` (374566273), `testnuc-runner-verify` (374995041) are gone.
- Retire path captured at edbf441: recreate `d6fb8d3` -> delete `e02ae57` -> verify (capture `20261013T054341Z_ci-p3-002-retire-stale-workflows.out` shows only the 5 entries and "in-tree=no" for all three).

### CI-P3-003 — playbook §8 stale — **verified-fixed**
- `docs/security/CI_CD_INCIDENT_PLAYBOOK.md:273-279` still carries the 2026-10-11 closure text (all CI tools SHA-256-verified, `CI_TOOL_PINS.md`, captured green runs; "closed (CI-P3-003, 2026-10-11)").
- Cross-check: latest `validate` run at edbf441 `38485693681` (2026-10-13T23:40Z) = success.

### CI-P3-004 — review package not built by CI — **open**
- `README.md:118-120` still: "…it is gitignored and no longer committed (HYG-P1-001), so it is delivered as a CI/release artifact." No `.github` reference to `build_review_package.sh`, `upload-artifact`, `id-token` or attestations (grep empty); live `GET /actions/artifacts` `total_count: 0`, `GET /releases` 0.
- `REPOSITORY.md:52-53` remains corrected ("built on demand; CI does not currently build it - CI-P3-004").

### LICENSE (previously DET-P3-001; no longer emitted by the 2026-10-14 machine pass) — **verified-fixed**
- `git ls-tree edbf441 -- LICENSE NOTICE` -> both tracked (blobs `70e2313b…`, `f7d8ad21…`). My deterministic re-run at edbf441 (2026-10-14) emits no `[GIT] No LICENSE` finding.

### DET-P3-002 — gitleaks not installed — **open** (environmental)
- Host: `which gitleaks` rc=1; the 2026-10-14 deterministic re-run still emits `DET-P3-002 [SEC] gitleaks not installed (secret scan skipped)`.
- CI side verified: `validate.yml:93-110` downloads pinned gitleaks 8.30.1 (SHA-256 `551f6fc8…`), runs the tree scan, the fail-closed history scan and the curl-allowlist regression; latest validate run green. The residual is the host-side tool absence, not a repo control gap.

### DET-P3-003 — 29 images without digest pin — **open**
- Tracked tree unchanged: **29** unpinned `image:` refs, all under `mct/compose/*` (`docker-compose.greenbone.yml` 20, `docker-compose.dfir-iris.yml` 2, `docker-compose.misp.yml` 3, otel/phase2/shuffle/velociraptor 1 each); the 2026-10-14 re-run title still says 29.
- Owner-visible blanket waiver `pins/supply-chain-waivers.json` (`compose_digest` root `mct/compose`, ref `*`, `review_by` 2026-12-31) — knowingly waived, still open per the deterministic baseline.

### SBOM-P3-001 — review package excludes the SBOM set — **open**
- `automation/validation/build_review_package.sh:41` copies only `sbom/vuln-summary.csv`; `:53` deletes `*.cdx.json`; `:73` prints the exclusion. `PACKAGE_MANIFEST.sha256` (3910 entries) has **0** `cdx.json`/`sbom/` entries; on-disk `review-package/` has no `sbom/` dir.
- D2 still `OWNER/POLICY DECISION REQUIRED` (`SBOM_COVERAGE_AND_PROVENANCE.md:159`).

### SBOM-P3-002 — doc contradicts the enforced vuln gate — **open**
- Doc `:82-83` still: "The step enforces coverage only: `--require-vuln` stays off until the vulnerability refresh in §5 lands…"; `:143` and the §7 proposed row repeat the old framing. Actual CI: `validate.yml:130` runs `sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json`.
- No append-only correction exists (the only doc change since 3623d2e is the signing wording in `ee4be3f`). Note: §5 residual item 2 ("SBOM license allow/deny gate + `pins/licenses.allow`") is now also stale — that gate exists (see SBOM-P2-001).

### SC-P3-001 — published PACKAGE_MANIFEST stale — **verified-fixed**
- Live equality: `sha256sum PACKAGE_MANIFEST.sha256` = `sha256sum review-package/MANIFEST.sha256` = `80a089bec48ebd8e3fdeba62d87835a11dcb4a60e6526e3cb1a845d44a5c4886` = `PACKAGE_DIGEST.txt:review_package_manifest_sha256`; 3910 entries = `review_package_entries`.
- Refresh wired: `automation/validation/publish_digests.sh:18` copies `review-package/MANIFEST.sha256` -> `PACKAGE_MANIFEST.sha256`; equality check `ci/validate.py:499,726` (`check_publication_equality`). Minor new drift: `PACK_NOT_INCLUDED.txt` regained one "unexpected; investigate" entry (see New findings).

### SC-P3-002 — Dependabot security updates — **verified-fixed**
- Live `GET /automated-security-fixes` -> `{"enabled":true,"paused":false}`; `GET /dependabot/alerts?state=open` -> 0; `.github/dependabot.yml` pip ecosystem present.

---

## Supplementary checks (not in this scope)

### DET-P2-001 — [PORT] CRLF committed for 1 file — **still present at edbf441**
- `git -C /home/user/falcon-build cat-file blob edbf441:evidence/raw/REVIEW-FIX/20261013T053408Z_ci-p3-002-stale-workflow-cleanup.out | grep -c $'\r'` -> **12** (file is 50 lines, 2159 bytes, ASCII with mixed CRLF/LF endings).
- `git ls-files --eol <file>` -> `i/mixed w/mixed attr/-text`; the CRs sit on the captured `curl` 404 JSON lines 11-14/16-19/21-24 (`"message": "Not Found",\r`). My 2026-10-14 re-run of `tools/deterministic_checks.py` reproduces `DET-P2-001 [PORT] CRLF committed for 1 file(s) (index has CRLF)`.
- **What it would take to fix**: `.gitattributes` marks `*.out -text` (bytes never rewritten), so `git add --renormalize .` will **not** convert this file — an explicit byte rewrite is required (`tr -d '\r' < f > f.tmp && mv`), followed by: update `evidence/MANIFEST.sha256:2280` (sha256 `b8683a74…` -> new) and the capture meta `raw_artifact_sha256`/`raw_artifact_bytes` (`…053408Z_ci-p3-002-stale-workflow-cleanup.meta.json`), add a `ledgers/redactions.md` row recording the in-place evidence edit (old/new sha256, as done for the credential-hygiene redaction), and re-run `ci/validate.py` evidence-integrity + `verify_publication_chain.sh`. Cheaper alternative: record a dated disposition (mixed endings are harmless in a byte-hashed evidence file) and make the capture wrapper emit LF-clean output, optionally exempting `-text` evidence paths in the PORT check.

### hadolint (DET-P3-004 in the 2026-10-14 --deep run) — environmental
- `which hadolint` rc=1; no hadolint step in any workflow. Same class as gitleaks: the deep-mode Dockerfile lint is skipped locally and not run in CI either; not a repo regression, but worth a note if the deep lens is used for gating.

## New findings

### NEW-1 (P2, CI/BP) — `gh` is still missing on the runner that executes the Dependabot sweep; the control silently no-ops
- The previous run's NEW-1 ("gh missing on the self-hosted runners") was claimed fixed in `ee4be3f` ("gh on the runner", decision log 2026-10-12T20:35Z). The evidence capture for that fix ran on the **falcon host** (`meta.json`: `working_directory /home/user/falcon-build`, `gh=gh version 2.102.0`; `/usr/bin/gh` is present here), not on a runner LXC.
- Live counter-evidence: the latest sweep run `38399605845` job `115303529830` (runner **edge-builder**, 2026-10-13T12:45Z) log: `/home/runner/actions-runner/_work/_temp/cbfb0901-….sh: line 1: gh: command not found` -> `no open dependabot PRs`, run reported **success**. The label gate (BP-P3-001) and the pinned merge (CI-P2-001) still cannot act when the job lands there; `BRANCH_PROTECTION.md:84-86` still asserts the gate is live.
- Suggested fix: install `gh` on every runner in the `lab` group (ci-runner, edge-builder, lab-runner-2) or fail closed (`command -v gh || exit 1`) and/or replace the gh calls with REST `curl` calls; then exercise the skip/merge path once a Dependabot PR exists.

### NEW-2 (P3, delivery metadata) — pack-fidelity "unexpected; investigate" entry re-appeared
- `PACK_NOT_INCLUDED.txt:4` (added by `e62348a`, 2026-10-13 publication for f82f82f): `evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out	not-in-pack (unexpected; investigate)` — the file **is** tracked at edbf441 (blob `27042236…`), so the pack renderer dropped a repo file from the delivery pack. Was 0 such entries at 3623d2e. Needs a disposition (pack exclusion rule or re-pack) before the next delivery.

## Notes / limitations
- All GitHub reads were read-only (`Authorization: Bearer` from `/home/user/.env`, never printed). No repo files were modified; the scratch deterministic run wrote only under `/tmp/opencode/reaudit-20261014/.scratch/`.
- Live checks: `systemctl` timer/service state, `/srv/falcon/textfile/falcon_ci.prom`, and one read-only SSH session to `mct-portal-dev` (hostname/cat/stat/sha256sum/tail only).
- No P0/P1 regressions found in this scope; the two status flips since 3623d2e are CI-P2-002 (open -> verified-fixed via `ee4be3f` + the live DO watcher) and the DET/CI items already closed.
