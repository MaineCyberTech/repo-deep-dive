# Focused security / supply-chain / CI deep-dive - repo-deep-dive

## Findings

| ID | Severity | Title | Report |
|---|---|---|---|
| CI-P1-001 | P1 | P1 secret gate in the org scan is inert: it matches 'SEC-' IDs but deterministic findings are namespaced 'DET-' | lens_focused_security_supply_chain_ci.md |
| SEC-P2-001 | P2 | PAT embedded in git clone URL in three workflows (contradicts the hardened extraheader pattern) | lens_focused_security_supply_chain_ci.md |
| CI-P2-001 | P2 | verify-remediation executes arbitrary commands from a PR-controllable plan on the self-hosted lab runner | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P2-001 | P2 | 15 GitHub Action refs are tag-pinned (@v4/@v5), not commit-SHA pinned | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P2-002 | P2 | Two large third-party binaries are committed into an archived run with no checksum record | lens_focused_security_supply_chain_ci.md |
| SEC-P2-002 | P2 | publish_audit.py publishes findings/reports to the pack and a target-repo PR without a secret scan | lens_focused_security_supply_chain_ci.md |
| CI-P3-001 | P3 | The changed-run gate enforces only P0 and only on pull_request; pushes to main skip it | lens_focused_security_supply_chain_ci.md |
| PORT-P3-001 | P3 | 35 tracked shell scripts carry mode 100644 (no exec bit) | lens_focused_security_supply_chain_ci.md |
| CI-P3-002 | P3 | actionlint reports shellcheck SC2015/SC2018 notes in four workflows | lens_focused_security_supply_chain_ci.md |
| CONF-P3-001 | P3 | gitleaks generic-api-key hits in shipped runs/ artifacts are false positives; allowlist does not cover them | lens_focused_security_supply_chain_ci.md |
| CONF-P3-002 | P3 | secrets: inherit passes every repo/org secret into the reusable lab-preflight workflow | lens_focused_security_supply_chain_ci.md |
| CI-P3-003 | P3 | lab-tests.yml interpolates a dispatch input directly into a shell command on the lab runner | lens_focused_security_supply_chain_ci.md |

---

# Focused security / supply-chain / CI deep-dive — repo-deep-dive (the audit pack itself)

Read-only audit of `MaineCyberTech/repo-deep-dive` at `c4121cb30c2419430442fea6829230a1f067da1a`
(2026-10-04), cloned to `C:\temp\rdd-audit`. No files in the pack were modified.

This report is a focused pass over areas `SEC`, `SUPPLY`, `CI`, `PORT` and `CONF`,
driven by prompts `00_SHARED_AUDIT_RULES.md`, `06`, `10`, `11`, `36`, `38` (plus `41`
for gate integrity). Because this *is* the tooling repo, special attention is paid to
anything that weakens the pack's own audit gate.

## Audit Metadata

- Audit name: `repo-deep-dive`
- Repository: `MaineCyberTech/repo-deep-dive`
- Commit SHA: `c4121cb30c2419430442fea6829230a1f067da1a`
- Generated at: 2026-10-04
- Area codes used: `SEC`, `SUPPLY`, `CI`, `PORT`, `CONF`
- Auditor: LLM subagent (read-only); deterministic inputs from
  `deterministic-findings.json` / `lens_deterministic.md`

## Scope

Reviewed the pack's own workflows, tooling, secret-scan config, dependency config and
archived run artifacts. **Not** reviewed: the target repositories the pack audits, the
live lab/Proxmox overlay, GitHub server-side branch-protection settings (not in the
repo — `CONTRIBUTING.md:67-71` states these are admin-side), or live secret values.

## Deterministic findings — validation

| DET | Title | Verdict | Evidence / reproduction | Notes |
|---|---|---|---|---|
| DET-P2-001 | actionlint workflow problems | **Real** | Quoted SC2015/SC2018 scripts exist at `lab-overlay-health.yml:36`, `lab-preflight.yml:55`, `lab-agent-offboard.yml:43`, `remediation.yml:101` | Info-level shellcheck; real but severity arguably P3 |
| DET-P3-002 | 2 large tracked files (>5 MB) | **Real** | `git ls-tree` shows `100644 ... 6074530 .../PS-003/tools/actionlint` and `100644 ... 21958840 .../PS-003/tools/gitleaks` | Escalated to SUPPLY P2: unverified vendored binaries |
| DET-P2-003 | 35 tracked `.sh` without exec bit | **Real** | `git ls-files -s` matched exactly 35 `100644 ... *.sh` under `runs/*/remediation/**` | All archived artifacts; `tools/*.sh` are 100755 |
| DET-P2-004 | gitleaks generic-api-key (17 hits) | **False positive** | Sampled 10: a documented placeholder `token=abcdef1234567890` (`.../PS-003/pr_body.md:54`) and SHA-256 manifest digests (`.../PS-U04/diff.patch:73`); plus prose about `long_hex` (`.../21_repo_hygiene_maintainability.md:106`) | Underlying config gap tracked as CONF-001; remaining 7 hits `unverified` |
| DET-P2-005 | 15 Action refs not SHA-pinned | **Real** | Grep of `uses:` lines: `audit.yml:30,33,48,53`, `pack-tests.yml:27,30,44`, `lab-preflight.yml:47`, `lab-agent-onboard.yml:115`, `remediation.yml:57,114`, `verify-remediation.yml:55,110`, `remediation-board.yml:19,30` | `deep-dive-deterministic.yml:60,191` shows the intended SHA-pin standard |

**Real: 4 / False-positive: 1.** `core.filemode=false` on this Windows clone does not
affect the index-mode evidence (`git ls-files -s`), which is authoritative.

## Findings

### Finding ID: repo-deep-dive-CI-001 — P1 secret gate is inert (DET namespace mismatch)

- Severity: **P1** · Confidence: **High** · Area: CI
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml:173` — `if f.get("severity") == "P1" and fid.startswith("SEC-"):`
  - `tools/deterministic_checks.py:361-365` — `area = "DET"` … `fid = "%s-%s-%03d" % (area, f["severity"], counters[area])`; the SEC subcode is only placed in the *title* (`"[%s] %s" % (f["subcode"], ...)`).
- What is happening: every machine finding is emitted with a `DET-Px-NNN` ID; the fail-closed step matches IDs beginning `SEC-`, which can never occur.
- Why it matters: high-risk gitleaks rules (aws/private-key/github/slack/stripe/…) and tracked `.env`/key files are emitted as `DET-P1-*` (`deterministic_checks.py:124,153`) and **pass**. The org-wide weekly secret gate never fires.
- Impact: a real secret in any scanned org repo does not fail the sweep.
- Recommended fix: gate on the subcode (`title.startswith("[SEC]")`) or emit a structured `subcode`/`area` field; add a test feeding a synthetic P1 SEC doc and asserting non-zero exit.
- Attack path: leaked credential in a scanned repo → deterministic scan records DET-P1 → inert check → no alert/fail.

### Finding ID: repo-deep-dive-SEC-001 — PAT embedded in the clone URL

- Severity: **P2** · Confidence: **High** · Area: SEC
- Evidence: `remediation.yml:61`, `verify-remediation.yml:61`, `lab-tests.yml:49` — `git clone -q "https://x-access-token:${GH_TOKEN}@github.com/...`; token from `secrets.ORG_READ_TOKEN || github.token` (`remediation.yml:53`). Contrast `deep-dive-deterministic.yml:139-146`, which uses `http.extraheader` and explicitly states the PAT is *“never placed in the clone URL, so it cannot leak.”*
- What is happening: the pack regresses the control it already implemented elsewhere.
- Impact: PAT can leak via git/shell error output, process listings, or credential helpers.
- Recommended fix: use the extraheader pattern in all three workflows; prefer a short-lived App token over a long-lived org PAT.

### Finding ID: repo-deep-dive-CI-002 — PR-controllable commands executed on the self-hosted lab runner

- Severity: **P2** · Confidence: **High** · Area: CI
- Evidence: `verify-remediation.yml:42` (`runs-on: [self-hosted, linux, x64, ci-runner]`), `:83` (`PLAN="runs/$RUN/remediation_plan.json"`), `:101` (`subprocess.run(["bash", "-lc", cmd], ...)` where `cmd` is from the plan's `verification` array).
- What is happening: a plan in `runs/**` (PR-editable) supplies arbitrary shell that a maintainer dispatch executes on a persistent runner holding `ORG_READ_TOKEN` and `LAB_ENDPOINT_SSH_KEY`.
- Recommended fix: restrict `run`/`ref` to trusted refs, verify the plan digest, execute in an ephemeral/isolated runner without org secrets, and require a protected environment approval.

### Finding ID: repo-deep-dive-SUPPLY-001 — 15 tag-pinned Actions (DET-P2-005)

- Severity: **P2** · Confidence: **High** · Area: SUPPLY
- Evidence: the 15 refs listed in the deterministic table above; intended standard at `deep-dive-deterministic.yml:60,191`.
- Impact: mutable tags are retargetable; these jobs carry org read PAT and lab SSH key.
- Recommended fix: pin to full SHAs with `# vX.Y.Z` comments (Dependabot `.github/dependabot.yml` already updates them weekly); enforce via the existing deterministic check as a required check.

### Finding ID: repo-deep-dive-SUPPLY-002 — committed vendored binaries (DET-P3-002)

- Severity: **P2** · Confidence: **High** · Area: SUPPLY
- Evidence: `runs/repo-deep-dive-20261003-0018-main-7bac320/remediation/PS-003/tools/actionlint` (6,074,530 B) and `.../tools/gitleaks` (21,958,840 B); directory has **no** checksum file, while `deep-dive-deterministic.yml:62-72` establishes sha256-verified download as policy.
- Impact: clone bloat plus a stockpile of unverified executables that invite use.
- Recommended fix: delete the binaries, keep the verify.sh that downloads by version+SHA, or add SHA256SUMS and verify before use; use Git LFS if provenance retention is required.

### Finding ID: repo-deep-dive-SEC-002 — publish_audit.py publishes without a secret scan

- Severity: **P2** · Confidence: **Medium** · Area: SEC
- Evidence: `tools/publish_audit.py:282-284` writes files into `runs/`; `:219-229` `PUT /contents/...` into the target repo; `:270,118` embeds the raw report verbatim; no `gitleaks`/`scan`/`redact` reference anywhere in the file; `.gitleaks.toml:13-17` allowlists only gitleaks logs.
- Impact: a secret pasted into an audit write-up is committed to two repos with no redaction pass, violating the shared rules' "do not print secret values."
- Recommended fix: run `gitleaks --redact` over the assembled file set and fail closed before writing/PR-ing; record the scan in the manifest.

### Finding ID: repo-deep-dive-CI-003 — run gate enforces only P0 and only on PR

- Severity: **P3** · Confidence: **High** · Area: CI
- Evidence: `audit.yml:45` (`if: github.event_name == 'pull_request'`), `:85-87` (reads `counts.bySeverity.P0`); `CONTRIBUTING.md:65,73-75`.
- Impact: P1 runs pass the gate; a direct/force push to `main` is not run-gated. Combined with CI-001, P1 has no automated enforcement.
- Recommended fix: run the gate on push too; allow P1 enforcement; keep the documented bypass with an auditable exception entry.

### Finding ID: repo-deep-dive-PORT-001 — 35 scripts lack the exec bit (DET-P2-003)

- Severity: **P3** · Confidence: **High** · Area: PORT
- Evidence: 35 `100644 ... *.sh` in `git ls-files -s` under `runs/*/remediation/**`; `.gitattributes:5-6` covers line endings only.
- Impact: low (verify-remediation uses `bash -lc`), but archived runbooks use `./script.sh`.
- Recommended fix: `git update-index --chmod=+x` for the affected files; the existing deterministic check already detects regressions.

### Finding ID: repo-deep-dive-CI-004 — actionlint shellcheck notes (DET-P2-001)

- Severity: **P3** · Confidence: **High** · Area: CI
- Evidence: `lab-overlay-health.yml:36`, `lab-preflight.yml:55`, `lab-agent-offboard.yml:43` (`A && B || C`, SC2015); `remediation.yml:101` (`tr 'A-Z' 'a-z'`, SC2018).
- Impact: real correctness smells at info level; noisy for the pack's own scan.
- Recommended fix: use explicit `if` guards and `tr '[:upper:]' '[:lower:]'`.

### Finding ID: repo-deep-dive-CONF-001 — gitleaks false positives in shipped runs (DET-P2-004)

- Severity: **P3** · Confidence: **High** · Area: CONF
- Evidence: `.../PS-003/pr_body.md:54` (placeholder `token=abcdef1234567890`, with `gitleaks generic-api-key false positive` at `:56`); `.../PS-U04/diff.patch:73` (SHA-256 manifest digests); `21_repo_hygiene_maintainability.md:106` (prose about `long_hex`). `.gitleaks.toml:13-17` does not allowlist these paths. `tools/deterministic_checks.py:153` marks `generic-api-key` as P2.
- Impact: recurring noise that masks real hits and never reaches the intended P1 gate.
- Recommended fix: confirm the remaining 7 hits; allowlist the known-safe run artifacts, preferably rule-narrowed rather than path-blanket, so real keys in diffs still fire. **No secret values are reproduced here.**

### Finding ID: repo-deep-dive-CONF-002 — `secrets: inherit` over-shares

- Severity: **P3** · Confidence: **High** · Area: CONF
- Evidence: `remediation.yml:41`, `verify-remediation.yml:38`, `lab-tests.yml:33`; `lab-preflight.yml:19-22` only needs `LAB_ENDPOINT_SSH_KEY`.
- Recommended fix: pass the single secret explicitly instead of `inherit`.

### Finding ID: repo-deep-dive-CI-005 — dispatch input interpolated into the lab shell

- Severity: **P3** · Confidence: **Medium** · Area: CI
- Evidence: `lab-tests.yml:62` `bash -o pipefail -c "${{ inputs.command }}"`; `:37-39` self-hosted runner with `GH_TOKEN` in env.
- Impact: script-injection primitive for dispatchers; unsafe to expose via `workflow_call`.
- Recommended fix: route the input through `env:` and reference `"$CMD"`.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Org secret sweep never fails on real secrets | P1 | High (control absent) | Credential exposure persists | CI-001 | Fix the ID match; add a test |
| PAT exposure via clone URL | P2 | Medium | Org read-token compromise | SEC-001 | extraheader pattern |
| PR content → RCE on persistent runner | P2 | Medium | Runner/secret compromise | CI-002 | ephemeral runner, trusted refs |
| Action supply-chain compromise | P2 | Low–Med | Job credential theft | SUPPLY-001 | SHA pins |

## Recommendations

### Immediate / Release Blocking
1. Fix the inert P1 secret gate (CI-001) and add a regression test.
2. Remove the PAT-from-URL pattern (SEC-001).

### This Week
3. Sandbox or restrict verify-remediation execution (CI-002); stop over-sharing secrets (CONF-002).
4. SHA-pin the 15 Action refs (SUPPLY-001); remove/checksum the vendored binaries (SUPPLY-002).

### This Month
5. Add a secret scan to publish_audit.py (SEC-002).
6. Extend the run gate to push + optional P1 (CI-003); clean exec bits (PORT-001); fix lint (CI-004); tighten gitleaks allowlist (CONF-001).

## Verification Performed

| Evidence | Type | Why relevant | Result |
|---|---|---|---|
| `git ls-files -s` / `git ls-tree` | reproduced | exec bit + large files | 35 noexec, two >5 MB confirmed |
| grep of `uses:` refs | reproduced | supply-chain pins | 15 unpinned confirmed |
| dst `deterministic-findings.json` IDs | reproduced | dead-gate hypothesis | all IDs `DET-P*`; `startswith("SEC-")` cannot match |
| slam-dunk source read | reproduced | workflow/token/permission claims | quotes captured at cited lines |

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| The 7 unsampled generic-api-key hits | confirm false-positive vs real | full gitleaks JSON (values redacted) |
| Actual ORG_READ_TOKEN scopes | bounds the SEC-001 blast radius | GitHub token settings (admin-side) |
| Branch protection / required checks on `main` | CI-003 enforceability | repo admin settings |

## Appendix — counts

- Findings: 12 — **P1 ×1, P2 ×5, P3 ×6**
- Areas: CI ×5, SEC ×2, SUPPLY ×2, PORT ×1, CONF ×2
- Deterministic validation: **4 real, 1 false-positive**
- Top findings: `repo-deep-dive-CI-001` (inert secret gate), `repo-deep-dive-SEC-001` (PAT in URL), `repo-deep-dive-CI-002` (self-hosted execution), `repo-deep-dive-SUPPLY-001` (unpinned Actions).
