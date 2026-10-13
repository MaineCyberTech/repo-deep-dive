# 16_documentation_devex_operator_readiness — Prompt 16 - Documentation, Developer Experience, and Operator Readiness Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `16_documentation_devex_operator_readiness.md` (area DOC, prompt)

## Verification Performed

# 16_documentation_devex_operator_readiness - 16_documentation_devex_operator_readiness.md

Domain subagent `16_documentation_devex_operator_readiness` (area DOC), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - Documented test command (`python tests/run_all.py`) fails on Windows: needs `windows-curses`, which the docs never say** (confidence: High)
  - `README.md:310-312 - the `## Tests` section instructs `python tests/run_all.py` with `# RESULT: PASS` and no platform caveat`
  - `AGENTS.md:164-174 - the required-before-commit check lists `python tests/run_all.py   # RESULT: PASS expected (stdlib only)``
  - `bench/tui.py:15 - `import curses` at module import time; tests/test_presets.py:41 loads tui.py unconditionally via _load()`
  - `.github/workflows/build-app.yml:53-54 - CI installs `windows-curses` with the comment 'CPython on Windows has no _curses; the TUI bundle needs this wheel'`
  - `Observed: `python tests/run_all.py` (system CPython 3.12.10, no _curses) -> `RESULT: FAIL (1)  - test_presets: crashed (No module named '_curses')`; `.venv/Scripts/python.exe tests/run_all.py` -> `RESULT: PASS``
  - Impact: Windows 10/11 is a first-class target (README.md:19, AGENTS.md:64) and is the platform the repo's own CI builds bundles on. A fresh Windows checkout that runs the documented command (system python, not the .venv) gets a FAIL, and an AI agent following AGENTS.md's 'required before every commit' step will be blocked or report a false failure. The dependency is only mentioned for bundle building (README.md:165-166), not for running the suite.
  - Recommendation: In README.md (Tests) and AGENTS.md (Testing), either use the venv interpreter (`.venv\Scripts\python.exe tests/run_all.py`) or explicitly add `pip install windows-curses` for Windows; make tests/test_presets.py import tui.py with a guard/soft-skip when curses is unavailable; add a CI workflow that runs `tests/run_all.py` on windows-latest and ubuntu-latest so the claim is enforced rather than asserted.
- **P2 - README release/version is stale and self-contradictory (v1.1.0 vs VERSION 1.11.5 vs the 1.11.3 written directly below it)** (confidence: High)
  - `README.md:12 - '**Release `v1.1.0`** - the version lives in `VERSION` and is reported everywhere it matters'`
  - `README.md:15 - 'release line plus an automatic build: `1.11.3+<n>.<commit>`'`
  - `README.md:17 - 'name it too (`ISO <gpu> v1.11.3 #<run>`)'`
  - `VERSION = `1.11.5`; `git describe --tags --long` = `v1.11.5-0-g60ab90eb` (HEAD 60ab90eb); AGENTS.md:192-207 documents `version_info()` as 'the single authoritative descriptor'`
  - Impact: The version is the repo's single authoritative 'current state' identifier. The README headline is ten minor releases behind the actual tag and directly contradicts the number in the next paragraph, so neither operators nor agents can tell which release the document describes. Release assets name v1.11.5 (build-iso.yml:119 / build-app.yml:107) while the README says v1.1.0 or v1.11.3.
  - Recommendation: Make the README state the current release from the tag/VERSION (or generate it), and reconcile the inline 1.11.3 examples; keep all three consistent in one place. Add a docs test (or reuse tests/test_version.py) that asserts the README's release string matches VERSION.
- **P2 - docs/PHASE_TIMINGS.md reports the same preset on the same machine as both ~11.5 min and ~14.1 min, contradicting itself** (confidence: High)
  - `docs/PHASE_TIMINGS.md:13 - '| `bench-live` (live USB) - i7-3770, 16 GiB, GTX 1080 | Arch live | **~14.1 min** (845 s) | `disk` skipped ...'`
  - `docs/PHASE_TIMINGS.md:83 - '| **Stabilized full soak (15 min)** | **~11.5 min** (live stick) - ~26 min (old desktop, slow disk) |'`
  - `docs/PHASE_TIMINGS.md:118 - 'its stabilized run measured **843 s before the trim and 853 s after**'`
  - Impact: The doc explicitly exists 'to estimate how long a run/preset takes', yet the two headline totals for the identical preset+host differ by ~2.6 min (691/843/845/853 s all appear). Anyone sizing a test window cannot trust the estimates, and the extended-check requirement for one authoritative current-state source is not met within the file.
  - Recommendation: Pick the current measured value for the live stick and use it in both places (line 13 and the line-83 row); note the pre/post-trim numbers are historical only if they must remain. Add the measurement date/commit next to the totals.
- **P2 - LICENSE declares the repo PROPRIETARY AND CONFIDENTIAL while README instructs the public to clone and download its public releases** (confidence: High)
  - `LICENSE:3 - 'PROPRIETARY AND CONFIDENTIAL.'`
  - `LICENSE:9-12 - 'No part of the Software may be copied, reproduced, modified, translated, distributed, sublicensed, published, transmitted, or used ... without the express prior written permission'`
  - `README.md:71 - public `git clone https://github.com/MaineCyberTech/bench-test.git``
  - `README.md:135-137 - 'Download from **Releases -> newest "App bundles" build**' (public URL)`
  - `README.md:357-363 - Security section: 'The repo and its ISO releases are public'`
  - `README.md:365-367 - License section: 'Proprietary - see LICENSE'; also logged as GOV-P3-001, docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/follow_up_register.md:11 (still 'open')`
  - Impact: Contributors, operators and downstream users cannot determine whether they may clone, build, redistribute or run the toolkit; the LICENSE forbids exactly the cloning/distribution the README relies on. This is an onboarding and legal-risk blocker for anyone outside the author.
  - Recommendation: Decide the licensing model and make README and LICENSE agree: either make the repo private and point README to an internal-use license, or ship a real OSS license and drop the 'CONFIDENTIAL' text. Reconcile the README 'Security'/'License' wording either way.
- **P3 - README 'Presets' table lists 11 presets but the GUI/TUI/web ship 13 - it omits 'Stabilized full soak (15 min)' and 'Graphics only (FurMark/Valley)'** (confidence: High)
  - `README.md:206-220 - the Presets table has 11 rows and claims 'Identical across GUI/TUI/web; each sets every group and duration'`
  - `bench/gui.py:130+ - PRESETS includes 'Stabilized full soak (15 min)' and 'Graphics only (FurMark/Valley)'`
  - `server/web/app.js - PRESETS carries the same 13 entries`
  - `tests/test_presets.py:12-28 - CANON defines 13 presets, including both omitted ones`
  - `README.md:114 - the prose describes 'Stabilized full soak (15 min)' although it is absent from the table`
  - Impact: Two shipped, first-class presets (one of them the headline '15 min' soak that the prose explains) are undiscoverable from the README's canonical list, so users pick the slower default and miss the tool's main bounded preset.
  - Recommendation: Add the two missing rows to the Presets table to match gui.py/tui.py/app.js/test_presets.py, and note the source of truth for the list.
- **P3 - AGENTS.md points to `update_ct.py`, which does not exist in the repository** (confidence: High)
  - `AGENTS.md:205 - '... deployed as a copy, so `VERSION` ships with it - see `update_ct.py`'`
  - `server/ contains only benchd.py, import_results.py, bench-agent.service, benchd.service, benchd.conf.example, web/ (no update_ct.py); `git ls-files` and a repo-wide search for 'update_ct' match only AGENTS.md:205`
  - Impact: The reference is in the versioning/deploy note that tells readers how a copy-deployed server stays honest about its release; the missing script makes that guidance unactionable for a developer or agent trying to follow it.
  - Recommendation: Either add the deploy/update script under server/ (referenced by docs/CONTROL_PLANE.md's Deployment section) or correct the reference to the actual mechanism, and add the `.deployed-commit`/`.bench-version` stamp step it describes.
- **P3 - No CONTRIBUTING/SECURITY/CHANGELOG or PR/issue templates, and no operator troubleshooting/rollback/incident runbook** (confidence: High)
  - `Repo root has only README.md, AGENTS.md, LICENSE (no CONTRIBUTING.md, SECURITY.md, CHANGELOG.md)`
  - `.github/ contains only workflows/ (no PULL_REQUEST_TEMPLATE, ISSUE_TEMPLATE, CODEOWNERS)`
  - `Docs are METHODOLOGY, CONTROL_PLANE, PHASE_TIMINGS, FUTURE_WORK, DATA (docs/ listing); a case-insensitive search for rollback|incident|runbook|troubleshoot|on-call|postmortem across tracked *.md returns nothing outside .venv`
  - `docs/CONTROL_PLANE.md:168-254 covers deployment + operating notes but no control-plane rollback and no incident response`
  - Impact: Contribution/coding standards exist only inside AGENTS.md (framed 'for AI agents and humans'), with no PR/release process doc, no security-reporting path, no release history, and no recovery/troubleshooting runbook for operators of the always-on control plane. The 'operator manuals' and 'troubleshooting' items on the prompt's scope are effectively absent.
  - Recommendation: Add CONTRIBUTING.md (contribution flow + coding standards distilled from AGENTS.md), SECURITY.md (private reporting), CHANGELOG.md (or point to release notes), .github/ PR + issue templates, and docs/RUNBOOK.md covering control-plane deploy/rollback, live-USB recovery, and incident triage.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| DOC-P2-001 | P2 | Documented test command (`python tests/run_all.py`) fails on Windows: needs `windows-curses`, which the docs never say |
| DOC-P2-002 | P2 | README release/version is stale and self-contradictory (v1.1.0 vs VERSION 1.11.5 vs the 1.11.3 written directly below it) |
| DOC-P2-003 | P2 | docs/PHASE_TIMINGS.md reports the same preset on the same machine as both ~11.5 min and ~14.1 min, contradicting itself |
| DOC-P2-004 | P2 | LICENSE declares the repo PROPRIETARY AND CONFIDENTIAL while README instructs the public to clone and download its public releases |
| DOC-P3-001 | P3 | README 'Presets' table lists 11 presets but the GUI/TUI/web ship 13 - it omits 'Stabilized full soak (15 min)' and 'Graphics only (FurMark/Valley)' |
| DOC-P3-002 | P3 | AGENTS.md points to `update_ct.py`, which does not exist in the repository |
| DOC-P3-003 | P3 | No CONTRIBUTING/SECURITY/CHANGELOG or PR/issue templates, and no operator troubleshooting/rollback/incident runbook |
