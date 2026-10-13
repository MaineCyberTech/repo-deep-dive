# 09_testing_quality_release_confidence — Prompt 09 - Testing, Quality, and Release Confidence Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `09_testing_quality_release_confidence.md` (area TEST, prompt)

## Verification Performed

# 09_testing_quality_release_confidence - 09_testing_quality_release_confidence.md

Domain subagent `09_testing_quality_release_confidence` (area TEST), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - No CI job runs the test suite or any compile/lint gate** (confidence: High)
  - `.github/workflows/ contains only build-app.yml, build-iso.yml and release.yml (git ls-files .github); none of them invoke the tests`
  - `grep of C:\temp\bench-test\.github for run_all|tests/|pytest|py_compile|shellcheck|PSScriptAnalyzer -> No matches found`
  - `AGENTS.md:164-174 - 'Testing - required before every commit' documents `python tests/run_all.py` and 'Never commit with a failing suite'`
  - `AGENTS.md:284 - the 'Do not' list says 'Push to main with a red tests/run_all.py ...' but nothing enforces it`
  - `README.md:308-315 and docs/CONTROL_PLANE.md:256-266 document the suite as the validation command`
  - Impact: The documented release gate is aspirational: a red or crashing suite does not block a merge to main, a tag, an app-bundle build or an ISO build. A regression can ship as a release.
  - Recommendation: Add .github/workflows/ci.yml on push/PR running on ubuntu-latest + windows-latest: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py packaging/*.py`, and `bash -n` over bench/*.sh + live/*.sh. Make it a required status check on main and add `needs: ci` to release.yml, build-iso.yml and build-app.yml.
- **P2 - Releases, tags and public ISO/app artifacts are published with no test or smoke verification of the artifact** (confidence: High)
  - `.github/workflows/release.yml:22-23 auto-runs on every push to main; :54-63 chooses the bump from commit subjects only; :96-107 tags and pushes the release`
  - `.github/workflows/build-iso.yml:38-42 auto-builds on any push touching bench/** or live/**; :114-131 attaches the bootable ISO to a public GitHub release - there is no test or verify step in the job`
  - `.github/workflows/build-app.yml:12-17 auto-runs on pushes to bench/** or packaging/**; :104-117 publishes the Windows/Linux bundles - no smoke test that a bundle launches`
  - `No workflow contains a step that executes the built artifact (grep of .github for run_all/pytest/py_compile/self-test -> no matches)`
  - Impact: A commit that never passed tests can be auto-tagged as a release and can produce a publicly downloadable live ISO / app bundle that was never launched or verified.
  - Recommendation: Gate tag/build jobs on the CI test job (`needs: ci`) and add a post-build smoke step (e.g. run `bench/agent.py --self-test` against the built bundle, and boot/verify the ISO image's SHA256SUMS + a headless start) before the release asset is attached.
- **P2 - Documented test command fails on Windows: suite needs third-party windows-curses but is described as stdlib-only** (confidence: High)
  - `tests/harness.py:4-5 - 'Stdlib only, so it runs on Windows, Linux and the live USB alike'`
  - `tests/test_presets.py:41 loads bench/tui.py at suite import time; bench/tui.py:15 is `import curses``
  - `Observed: `python tests/run_all.py` with system CPython 3.12.10 (no windows-curses) -> 'RESULT: FAIL (1)  - test_presets: crashed (No module named _curses)'`
  - `Observed: same command under .venv (windows-curses 2.4.2) -> 'RESULT: PASS'`
  - `AGENTS.md:167 documents `python tests/run_all.py   # RESULT: PASS expected (stdlib only)``
  - Impact: A contributor or a Windows CI runner following the documented command sees a hard failure; the advertised 'stdlib only / runs anywhere' invariant is false for the suite on Windows.
  - Recommendation: Either guard the tui/curses import in tests/test_presets.py (skip cleanly when curses is unavailable) or document that the suite must run under the bootstrapped .venv (which installs windows-curses); correct the 'stdlib only' wording in harness.py/AGENTS.md.
- **P2 - The 23 PowerShell battery scripts and the web dashboard are only validated by substring assertions, never executed or linted** (confidence: High)
  - `git ls-files shows 23 *.ps1 under bench/ (Run-WorkstationBench.ps1, Invoke-*.ps1, Sample-Sensors.ps1, Get-*.ps1, Set-*.ps1, Install-*.ps1) - no test or CI step runs or parses them`
  - `tests/test_reporting.py:487-493 asserts Invoke-NetBench.ps1 contains the strings 'http_code'/'download_error'/'@($DownMB, 50, 25, 10)' - substring only`
  - `tests/test_soak.py:70-75 asserts Run-WorkstationBench.ps1 contains 'Invoke-FurMarkBench.ps1'/'$SoakUntilStable' - substring only`
  - `tests/test_packaging.py:80-92 asserts Sample-Sensors.ps1 exists and run_win.py/tui.py contain strings`
  - `tests/test_dashboards.py:99-132 (_web) reads server/web/app.js + style.css and asserts substrings; there is no JS runtime or browser test`
  - `No PSScriptAnalyzer / shellcheck / node / eslint step exists in .github (grep -> no matches)`
  - Impact: The primary Windows deliverable (the battery) and the web UI can break syntactically/semantically while the suite still passes, because the checks only assert that particular text is present.
  - Recommendation: Add a PowerShell parse/lint gate (PSScriptAnalyzer, or `pwsh -NoProfile -Command '[void][scriptblock]::Create((Get-Content -Raw <file>))'` at minimum) and a JS syntax/lint step (node --check on app.js) to CI; add at least one execution smoke of the PowerShell battery entry point on a windows runner.
- **P3 - The suite silently skips whole test groups, so lost coverage does not fail the run** (confidence: High)
  - `tests/test_dashboards.py:23-32 - _gui prints 'SKIP gui rows' and returns without recording a failure when tkinter/display is unavailable`
  - `tests/test_dashboards.py:50-55 - _tui prints 'SKIP tui rows' and returns when tui/curses cannot be imported`
  - `tests/test_soak.py:78-82 - prints 'SKIP plateau logic' and returns if bench/gpu_bench.py fails to import (e.g. torch missing)`
  - Impact: On a headless or partially-provisioned runner the GUI, TUI and soak-decision coverage disappears silently while run_all.py still prints RESULT: PASS, overstating confidence.
  - Recommendation: Track skips explicitly and print a machine-readable skip total; fail (or at least exit non-zero under a BENCH_TEST_STRICT flag) when an expected group cannot run, so a provisioning gap is visible.
- **P3 - Wall-clock/sleep based assertions make the suite flake-prone** (confidence: Medium)
  - `tests/test_reporting.py:52-66 - ReporterPump with interval=0.3 then time.sleep(0.9) to assert 3 telemetry rows were flushed and a command was received`
  - `tests/test_reporting.py:213-218 - runs run_win.sampler for 2.5s then asserts rows exist; tests/test_reporting.py:229-243 repeats the pattern for the AMD branch`
  - `tests/test_reporting.py:257-259 - runs bench/telemetry_log.py for a 2s duration with capture_output and a 90s timeout`
  - `tests/test_update.py:22-27,96-114 spawn git/subprocess and local servers whose completion is assumed`
  - Impact: On a slow or loaded host these fixed sleeps can produce spurious failures, and there is no CI job to establish the flake rate.
  - Recommendation: Replace fixed sleeps with poll-until-timeout helpers that wait on the observed condition, and record a measured flake budget once the CI test job exists.
- **P3 - No coverage measurement and no statement of what 'RESULT: PASS' does not cover** (confidence: High)
  - `git ls-files has no pyproject.toml, setup.cfg, pytest.ini, .coveragerc or any coverage/lint config; the suite is plain stdlib prints`
  - `AGENTS.md:172-174 lists what run_all.py covers but there is no e2e/real-run path in the suite`
  - `bench/agent.py:375-416 implements a `--self-test` smoke path; bench/gui.py:221 has a self_test flag - neither is invoked by tests or CI`
  - Impact: A green suite does not exercise a real benchmark run, the PowerShell battery, app.js, or the built bundles/ISO, yet reviewers may treat 'RESULT: PASS' as release evidence.
  - Recommendation: Add coverage.py with a threshold, wire the existing --self-test path into CI as an e2e smoke, and document a short 'what PASS excludes' note in README.md and AGENTS.md next to the Testing section.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| TEST-P1-001 | P1 | No CI job runs the test suite or any compile/lint gate |
| TEST-P2-001 | P2 | Releases, tags and public ISO/app artifacts are published with no test or smoke verification of the artifact |
| TEST-P2-002 | P2 | Documented test command fails on Windows: suite needs third-party windows-curses but is described as stdlib-only |
| TEST-P2-003 | P2 | The 23 PowerShell battery scripts and the web dashboard are only validated by substring assertions, never executed or linted |
| TEST-P3-001 | P3 | The suite silently skips whole test groups, so lost coverage does not fail the run |
| TEST-P3-002 | P3 | Wall-clock/sleep based assertions make the suite flake-prone |
| TEST-P3-003 | P3 | No coverage measurement and no statement of what 'RESULT: PASS' does not cover |
