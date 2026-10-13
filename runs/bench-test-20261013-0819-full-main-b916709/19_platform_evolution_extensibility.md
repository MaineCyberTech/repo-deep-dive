# 19_platform_evolution_extensibility — Prompt 19 - Platform Evolution and Extensibility Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `19_platform_evolution_extensibility.md` (area EVOL, prompt)

## Verification Performed

# 19_platform_evolution_extensibility - 19_platform_evolution_extensibility.md

Domain subagent `19_platform_evolution_extensibility` (area EVOL), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - Adding a benchmark module/phase requires editing 6+ hardcoded lists; there is no registry or module template** (confidence: High)
  - `bench/benchreport.py:36 - GROUPS is the canonical group list (["gpu","cpu",... "gfx"]).`
  - `bench/agent.py:55 - DEFAULT_GROUPS duplicates that list verbatim.`
  - `bench/gui.py:94 - GROUPS (label pairs); bench/gui.py:101 - _ALL_G hardcodes the same 12 names a third time.`
  - `bench/tui.py:109 - GROUPS is yet another copy.`
  - `server/web/app.js:4 - const GROUPS; server/web/app.js:5 - const ALL_GROUPS (byte-identical duplicate of GROUPS).`
  - `bench/run_win.py:27 - PHASE_GROUP maps battery phase index -> group; bench/run_win.py:33-35 registers --skip-<g>; bench/run_win.py:490-509 appends each -SkipX explicitly so a new group must be wired by hand.`
  - `bench/Run-LinuxBench.sh:79-90 - per-group --skip-* parsing (a separate copy of the group vocabulary).`
  - `tests/test_presets.py:10 - the audit test hardcodes the group list a seventh time.`
  - `docs/DATA.md:90-97 documents conventions for adding a telemetry *field* but there is no document or template for adding a *phase/module*.`
  - Impact: Module/phase extensibility is load-bearing but purely convention-based: a new benchmark must be added to 6+ independent literals across Python, PowerShell, Bash and JavaScript, and every miss is a silent no-op or drift. The only parity guard (tests/test_presets.py) hardcodes its own copy of the list and parses app.js with regexes, so it cannot catch a genuinely new group or a new platform skip flag. Raising the platform's capability surface is therefore error-prone and expensive, which directly limits evolution.
  - Recommendation: Make benchreport.GROUPS (or a small JSON registry: name/label/platform/runner-flag) the single source of truth and have supported_groups(), agent.DEFAULT_GROUPS, gui._ALL_G, tui.GROUPS, run_win skip flags, app.js and Run-LinuxBench.sh derive from it. Add a bench/PHASE_TEMPLATE.md plus a unit test that fails when a group is present in the registry but not selectable end-to-end (registry -> runner flag -> server capabilities -> dashboard toggle).
- **P2 - No CI workflow runs the test suite, so platform changes are merged unverified** (confidence: High)
  - `.github/workflows/build-app.yml:38-64 - checkout, pip install pyinstaller, then build bundles; no tests/run_all.py step.`
  - `.github/workflows/build-iso.yml:56-118 - requirements check + ISO build + release attach; no test step.`
  - `.github/workflows/release.yml:36-107 - computes the next version, writes VERSION, tags; no test step.`
  - `AGENTS.md:164-174 - declares `python tests/run_all.py` and py_compile 'required before every commit'.`
  - `tests/run_all.py + tests/test_presets.py, tests/test_control_plane.py, tests/test_update.py exist and cover presets, the API and the update path.`
  - Impact: The repo has a meaningful stdlib suite but nothing enforces it in CI. All three workflows are triggered by pushes to main (release.yml and build-app.yml), so a refactor or new module can be merged (and can even trigger an ISO/app release) with a red or never-run suite. Extensibility work is exactly the kind that regresses shared invariants (preset parity, telemetry columns, API shape), and there is no automated gate to catch it.
  - Recommendation: Add .github/workflows/test.yml running on push+PR: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py` and `bash -n bench/Run-LinuxBench.sh live/Build-LiveUSB.sh live/airootfs/usr/local/bin/bench-*` on both ubuntu-latest and windows-latest; make it a required status check and have build-iso/build-app `needs:` it.
- **P2 - Schema 'migration' is unversioned, additive-only column checks run on every startup** (confidence: High)
  - `server/benchd.py:159-176 - _migrate() only runs `ALTER TABLE ... ADD COLUMN` guarded by `PRAGMA table_info` membership tests; there is no schema version.`
  - `server/benchd.py:95-143 - all tables are created with `CREATE TABLE IF NOT EXISTS`; there is no migrations table and no `PRAGMA user_version` anywhere in the file.`
  - `server/benchd.py:156 - _migrate() is invoked unconditionally in Store.__init__, i.e. re-evaluated on every server start.`
  - Impact: The storage layer can only ever gain nullable columns. There is no ordered, recorded, or reversible path for a rename, a type change, a backfill or a drop, and no marker of which schema version a given benchd.sqlite is at. A future evolution of the run/telemetry model (e.g. splitting system/preset out, or adding indexes) has no safe mechanism, and a partially-applied change leaves no trace to detect or resume from. Non-additive edits would silently corrupt existing deployments' queries.
  - Recommendation: Introduce `PRAGMA user_version` (or a schema_migrations table) with an ordered list of idempotent migration callables, run each once inside a transaction, and assert the expected version at startup. Add tests/test_migrations.py that builds a v(N) DB, migrates to v(N+1), and asserts data is preserved. Document the policy (append-only columns, rename = new column + backfill).
- **P2 - Authorization is a hardcoded two-tier boolean checked per handler; no role/permission model to extend** (confidence: High)
  - `server/benchd.py:572-580 - _is_operator() reduces auth to `token is None or bearer/query == token`.`
  - `server/benchd.py:582-591 - _runner_ok(); :593-605 - _caller()/_may_act_as(); :607-615 - _may_write_run(). The only principals are 'operator' and 'this runner'.`
  - `server/benchd.py:1008,1026 - operator-only checks are inlined at each call site (`if not self._is_operator(q): return self._err(403, ...)`).`
  - `docs/CONTROL_PLANE.md:275 - roadmap explicitly lists 'Operator logins (per-user accounts) instead of the shared join token'.`
  - `A grep for role/permission/rbac across *.py returns no matches.`
  - Impact: Permission extensibility is absent: there is a single shared operator token with full privileges (including the remote `exec`/`shell` and `iso_write` commands). Any future need for a read-only/auditor role, per-user attribution, or scoping a subset of commands requires editing every handler because there is no central authorization decision point or role table. This blocks the roadmap item and makes least-privilege operation impossible.
  - Recommendation: Add a central `authorize(principal, action, resource)` policy (backed by a roles/permissions table once accounts exist) and route every check through it. Keep the shared token as the bootstrap admin role. Add tests asserting each command kind and each UI route requires an explicit capability so a new endpoint cannot default to open.
- **P2 - Telemetry/summary metric catalogue is duplicated across Python and JavaScript with no single source of truth** (confidence: Medium)
  - `server/benchd.py:78-90 - METRICS is a hand-written (key, label) list used by /state and /metrics.`
  - `bench/benchreport.py:190-203 - DASH_FIELDS is a second hand-written (key, label, decimals) list.`
  - `server/web/app.js:29-44 - SERIES hand-writes name+colour per key; server/web/app.js:45-56 - CHART_PRESETS; server/web/app.js:60-64 - STAT_ORDER is yet another ordered key list.`
  - `tests/test_reporting.py:393-397 - the only parity check is DASH_FIELDS-vs-sampler-columns; there is no test tying app.js SERIES/METRICS to the same set.`
  - `bench/benchreport.py:54-107 - CSV_ALIASES is a fourth list mapping raw column names to canonical keys.`
  - Impact: Adding one metric (a routine evolution step — docs/DATA.md:90-97 describes it) means editing at least four independent literals in two languages. A key that exists in the server catalogue but not in app.js is silently rendered with a default label/colour (app.js:772 `SERIES[k] || [k, ...]`), and the METRICS list used for trends/compare can drift from what the runner actually emits, producing empty charts with no error.
  - Recommendation: Define the metric catalogue once (e.g. a JSON/registry consumed by benchreport, benchd and the web build) and generate METRICS, DASH_FIELDS and SERIES/STAT_ORDER from it. Extend the existing parity test to assert every METRICS/DASH_FIELDS/SERIES key belongs to the same catalogue and every sampler column is covered.
- **P3 - Command kinds are a hardcoded tuple; clients cannot advertise command capability and silently fail unknown kinds** (confidence: High)
  - `server/benchd.py:1223-1225 - the set of valid command kinds is an inline tuple literal in _issue_command.`
  - `bench/agent.py:243-283 - a hand-written if/elif chain dispatches each kind (agent implements all).`
  - `bench/gui.py:630-655 and bench/tui.py:280-304 - each dashboard re-implements its own if/elif chain and acks anything it does not implement as failed ('unsupported: %s').`
  - `bench/agent.py:67-70 - probe_capabilities() advertises os/groups/platform/toolkit/live but no command support, so the server cannot know which kinds a runner will accept.`
  - `docs/CONTROL_PLANE.md:139-142 - documents that the GUI/TUI and the agent implement different subsets.`
  - Impact: Extending the control surface (e.g. a new maintenance action) requires coordinated edits in the server and in three separate clients, with no compile-time or test-time signal if one is missed; the operator only discovers the gap when a runner acks 'failed'. There is no way to add or version a command without touching every executor.
  - Recommendation: Move command kinds into one registry (kind -> payload schema) shared by the server, and advertise supported kinds in registration capabilities so the UI can disable unsupported actions. Add a test that every kind in the registry is handled by at least the agent and that capabilities cover it.
- **P3 - Vendored LibreHardwareMonitor binaries are git-ignored, so the app bundle is not reproducible from a clone despite docs claiming otherwise** (confidence: High)
  - `.gitignore:23 - `tools/` is ignored wholesale (no exception for tools/lhm).`
  - ``git check-ignore -v tools/lhm/LibreHardwareMonitorLib.dll` -> `.gitignore:23:tools/`; `git ls-files tools` -> 0 tracked files.`
  - `packaging/build_app.py:163-164 - sets have_lhm only if tools/lhm/LibreHardwareMonitorLib.dll already exists; build_app.py:178-179 adds the tools/ dir to the bundle only when have_lhm is true (no error/warning otherwise).`
  - `.github/workflows/build-app.yml:38-64 - CI checks out, installs PyInstaller and builds; there is no step that fetches or restores tools/lhm.`
  - `AGENTS.md:146-147 - states 'The DLL is vendored under tools/lhm and shipped in the app bundle' (only true for a local checkout that happens to have the untracked files).`
  - `bench/Sample-Sensors.ps1:36-52 - a runtime curl download is the fallback when the DLL is absent.`
  - Impact: A fresh clone or a CI run produces bundles without the sensor library, and the build reports success silently. On AMD/Intel Windows (no nvidia-smi) the dashboard/agent then depends on a runtime GitHub download to populate GPU temp/power/clocks and CPU sensors, so an offline or rate-limited target loses those columns. The documented 'vendored' guarantee is not enforced by the repository.
  - Recommendation: Un-ignore tools/lhm (e.g. `!tools/lhm/**` with the DLLs pinned and checksummed) or add an explicit, version-pinned fetch+verify step to build-app.yml and build_app.py. Make build_app.py fail or warn loudly when have_lhm is false, and correct AGENTS.md/docs to match whichever policy is chosen.
- **P3 - No package structure; shared code is a 2.5k-line flat module imported via sys.path insertion** (confidence: Medium)
  - `bench/benchreport.py is 2533 lines / ~117 KB and mixes group vocabulary (line 36), conf resolution (load_conf, line 131), hardware helpers, DASH_FIELDS (line 190), CSV_ALIASES (line 54), the reporting client and summary builders (build_summary, line 2267).`
  - `bench/agent.py:42 - `sys.path.insert(0, BENCH)` then top-level `import benchreport`; there are no packages.`
  - `No `__init__.py` exists anywhere under bench/, server/ or packaging/ (recursive search returns nothing).`
  - `docs/DATA.md:90-97 and AGENTS.md:122-162 document behaviour that spans this one module, which is the de-facto shared library for the GUI, TUI, agent, server and packaging.`
  - Impact: Package extraction is not currently possible: every consumer imports one monolithic module by name, boundaries between config, client, summary and telemetry logic are unenforced, and a change to one concern re-imports/re-runs the whole module. This makes it harder to add or reuse a module and to adopt an offline/validator boundary.
  - Recommendation: Introduce a `bench` package (`bench/__init__.py`, e.g. bench/config.py, bench/telemetry.py, bench/summary.py, bench/client.py) and re-export the current names so existing importers keep working; add a lint that forbids new sys.path hacks. This is a prerequisite for the module-registry work above.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| EVOL-P2-001 | P2 | Adding a benchmark module/phase requires editing 6+ hardcoded lists; there is no registry or module template |
| EVOL-P2-002 | P2 | No CI workflow runs the test suite, so platform changes are merged unverified |
| EVOL-P2-003 | P2 | Schema 'migration' is unversioned, additive-only column checks run on every startup |
| EVOL-P2-004 | P2 | Authorization is a hardcoded two-tier boolean checked per handler; no role/permission model to extend |
| EVOL-P2-005 | P2 | Telemetry/summary metric catalogue is duplicated across Python and JavaScript with no single source of truth |
| EVOL-P3-001 | P3 | Command kinds are a hardcoded tuple; clients cannot advertise command capability and silently fail unknown kinds |
| EVOL-P3-002 | P3 | Vendored LibreHardwareMonitor binaries are git-ignored, so the app bundle is not reproducible from a clone despite docs claiming otherwise |
| EVOL-P3-003 | P3 | No package structure; shared code is a 2.5k-line flat module imported via sys.path insertion |
