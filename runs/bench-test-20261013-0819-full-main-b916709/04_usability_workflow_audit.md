# 04_usability_workflow_audit — Prompt 04 - Usability and Workflow Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `04_usability_workflow_audit.md` (area USE, prompt)

## Verification Performed

# 04_usability_workflow_audit - 04_usability_workflow_audit.md

Domain subagent `04_usability_workflow_audit` (area USE), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - Control-plane commands report success on enqueue and never surface the runner's ack, so a rejected start/stop/exec looks successful** (confidence: High)
  - `server/web/app.js:1352 - `toast(kind + " sent")` fires after the POST /runners/<id>/commands call returns {'status':'queued'}; nothing waits for the command result`
  - `server/web/app.js:1343-1345 - the start path toasts `"run queued: " + payload.label` and refreshes; the button is never put into a pending/failed state`
  - `server/web/app.js:187 - `es.addEventListener("command", () => queueRefresh());` is the only handling of the server's `command` SSE event; the event's `status`/`result` payload is discarded`
  - `server/benchd.py:1019-1023 - the server DOES publish the ack (`UPDATE commands SET status=?, result=?` then bus.publish({event:'command', data:{status, result}})`, so the failure data is available to the UI`
  - `server/web/app.js:370,403 - `const disabled = r.online ? "" : "disabled"` leaves Start enabled while the runner is busy, so pressing Start on a running box queues a command the runner rejects`
  - `bench/gui.py:630-633 - a `start` command while `self.running` acks `failed` with `{'error': 'already running'}`; bench/tui.py:281-283 does the same`
  - `server/web/app.js:1810-1823 - the remote-terminal submit toasts `"sent to runner: " + cmd` on enqueue only; the exec result (rc) is never shown in the UI`
  - Impact: An operator who clicks Start on a busy runner, Stop on the wrong card, Update, or an exec command sees a success toast even when the runner rejects or fails the command. The only feedback channel is the runner's own live console, which is not on screen for the Live tab; failed control actions are effectively silent and easy to mistake for a done action.
  - Recommendation: Render command lifecycle in the UI: subscribe to the `command` SSE event and toast/log on status `failed` (including `result.error`), show a per-runner pending/queued indicator on the Start/Stop/Update buttons, and disable Start while the runner reports `busy`. Optionally add a small per-runner 'last command: <kind> <status>' line sourced from the same event.
- **P2 - Web Start-run form has no input validation; blank/zero/negative durations and sizes are sent silently** (confidence: High)
  - `server/web/app.js:1270-1288 - 13 duration/tuning inputs are bare `<input type="number">` with no `min`, `max`, `required` or `step`; e.g. `<input id="mGpu" type="number" value="600">``
  - `server/web/app.js:1324-1340 - the payload coerces with `+$("#mGpu").value` etc. with no validation before `api(.../commands, "POST", ...)`; a cleared field becomes 0 and a non-numeric value becomes NaN (serialised to `null` by JSON.stringify)`
  - `bench/benchreport.py:915-930 - `extra_runner_args()` forwards each value straight through as a runner flag (`args += [flag, str(v)]`), so e.g. `gpu_size: 0` is passed on unchanged`
  - `bench/gui.py:350-357 - the Tk dashboard's equivalents are `ttk.Spinbox(from_=5, to=7200)`, i.e. the GUI clamps what the web form does not`
  - Impact: A mistyped or cleared field starts a run whose phases measure nothing (0-second soak, 0-size matrix, 0 passes) or that fails immediately, and the run is still recorded in history as a real result. Because these numbers are the point of the tool (reproducible comparison), bad input silently produces misleading results with no error message.
  - Recommendation: Add `min`/`max`/`step` to the numeric inputs, validate the whole form in the `#mGo` handler (reject blank/NaN/out-of-range with an inline error next to the field, and block the submit), and mirror the GUI's sane ranges. Optionally have `extra_runner_args`/the runners reject non-positive values.
- **P2 - GUI 'Clean up environment' deletes the cached runner interpreter with no confirmation and no in-run guard** (confidence: High)
  - `bench/gui.py:378-380 - the 'Clean up environment' button is created once and never disabled, including during a run`
  - `bench/gui.py:831-847 - `clean_env()` calls `bootstrap.clean(log=self._log)` immediately; it has no `if self.running` check and no confirmation dialog`
  - `bench/bootstrap.py:316-331 - `clean()` `shutil.rmtree`s the cached `env` and `python` directories (the interpreter + numpy/psutil/cryptography that the frozen bundle launches batteries with)`
  - `bench/gui.py:693-699 - by contrast, the remote `update`/`iso_*` path refuses with 'a run is in progress - update once it finishes', showing the intended guard pattern is absent here`
  - Impact: One unconfirmed click during an in-flight soak removes the interpreter the battery was launched from (packaged apps run via `bootstrap.python_path`), aborting or corrupting the run and discarding the environment the operator provisioned; the button gives no hint that it is destructive.
  - Recommendation: Gate `clean_env()` with `if self.running: return self._set_status('a run is in progress', WARN)`, and add a confirm dialog naming what will be deleted (cache path, size) before calling `bootstrap.clean()`.
- **P2 - Remote terminal / ad-hoc exec is only offered while a run is live, so idle runners cannot be diagnosed from the dashboard** (confidence: High)
  - `server/web/app.js:622-624 - in `focusShell()` the exec form is emitted only inside `${live ? ... : ''}`: `${live ? `<form class="term" data-exec=...>` : ''}``
  - `server/web/app.js:550-556 - `runnerRun()` returns the runner's *last* run when it has no live run, and `focusShell(r, live)` is called with `live=false` for it`
  - `server/web/app.js:1765-1790 - the focus view is the only path that renders a terminal; the runner card (`runnerCard`, app.js:392-416) has no command box`
  - `README.md:189-190 and docs/CONTROL_PLANE.md:140-142 advertise a 'remote terminal' and `exec`/`shell` as general runner capabilities`
  - `server/benchd.py:1223-1225 - the server accepts `exec`/`shell` for any runner id regardless of run state`
  - Impact: An operator or support person cannot run a one-off diagnostic (e.g. `nvidia-smi`, `dmesg | tail`) on a machine that is idle or that has never completed a run, even though the API supports it; the advertised 'remote terminal' is effectively only a run console.
  - Recommendation: Expose a terminal independent of run state - either always render the exec form in the focus view (routing output to the runner's stream rather than a run), or add a 'run command…' action to the runner card that opens a modal and streams the result.
- **P3 - Deleting a schedule is immediate with no confirmation, unlike every other destructive control** (confidence: High)
  - `server/web/app.js:1663 - the schedules table renders `<button class="danger" data-sched-del=...>delete</button>``
  - `server/web/app.js:1779 - the global click handler dispatches `if (t.dataset.schedDel) return deleteSchedule(t.dataset.schedDel);` with no confirm`
  - `server/web/app.js:1702-1705 - `deleteSchedule()` calls `api('/schedules/'+id, 'DELETE')` directly`
  - `server/web/app.js:1358 (forget runner), 1368 (reboot/shutdown), 1434/1439 (ISO write) all confirm first, showing the established pattern`
  - Impact: A single click on a `danger`-styled button permanently removes a recurring run schedule (the server deletes the row, benchd.py:662), with no undo and no confirm prompt - inconsistent with the care taken around the other destructive actions.
  - Recommendation: Wrap the delete in a `confirm()` naming the runner and cadence (as `forgetRunner`/`powerRunner` do), or require the same explicit checkbox used for ISO writes.
- **P3 - No completion notification for long runs; the only signal is the browser tab title** (confidence: High)
  - `server/web/app.js:314 - the sole completion hint is `document.title = STATE.active.length ? `(${STATE.active.length}) bench-test` : 'bench-test control plane'``
  - `server/web/app.js:143-149 - `toast()` auto-hides after 4000 ms and is only fired by user actions, never by a run finishing`
  - `server/web/app.js:182-191 - the SSE handlers refresh state on run/phase/command events but never notify on a run transition to done/failed/stopped`
  - `server/web/app.js:26-27, README.md:210-220 - presets include 1800 s GPU/fullsoak soaks, i.e. completion is tens of minutes after the click`
  - Impact: Operators running the long soak presets must keep the page (or at least the tab) in view to notice a run finished, failed, or hit a NOT-clean verdict; a missed completion delays the next run and the hardware decision the benchmark was run for.
  - Recommendation: On a run transitioning out of `running`, raise a persistent toast and (with permission) a Web Notification with host, status and headline metric; keep a small 'unseen results' badge until the operator opens the run.
- **P3 - Compare gives no empty state, and with a single finished run it compares the run with itself and presents the 0% deltas as a comparison** (confidence: High)
  - `server/web/app.js:978-987 - `renderCompareOptions()` builds both selects from `finished.slice(0,60)` and only sets distinct defaults `if (finished.length > 1)`; with one finished run both selects point at the same run`
  - `server/web/app.js:988-990 - `runCompare()` starts with `if (!A || !B) return;`, so with zero finished runs the 'compare' button silently does nothing`
  - `server/web/app.js:996-1010 - the result table is always rendered with A/B/Δ and a 'vs <timestamp>' style header (via showDetail's pattern), with no guard that A !== B`
  - `server/web/index.html:97-105 - the Compare pane has placeholder-less `<select id="cmpA">`/`<select id="cmpB">` and no explanatory empty state`
  - Impact: A new operator clicks 'compare' and either gets nothing at all or a table of 0.0% deltas that looks like a real cross-run/cross-host comparison but is the same run on both sides - a false comparison that can be mistaken for 'no regression'.
  - Recommendation: Disable the compare button and show 'compare needs two finished runs' when fewer than two exist, and reject A === B with a clear message (or auto-pick a different B).
- **P3 - README release/version strings are stale and mutually inconsistent with VERSION** (confidence: High)
  - `README.md:12 - '**Release `v1.1.0`**'`
  - `README.md:15 - 'release line plus an automatic build: `1.11.3+<n>.<commit>`'`
  - `README.md:17 - "name it too (`ISO <gpu> v1.11.3 #<run>`)",`
  - `VERSION - contains `1.11.5`, which is what the GUI/TUI/control plane actually report (benchreport.bench_version; asserted by tests/test_version.py:26-45)`
  - `tests/test_version.py:23-135 - the version tests cover VERSION/semver/surfaces but never the README text, so nothing catches the drift`
  - Impact: A newcomer cannot tell which release the checkout is: the README headline says v1.1.0, the same paragraph says 1.11.3, and the running app says 1.11.5. This undermines the 'the version lives in VERSION and is reported everywhere' promise the README opens with.
  - Recommendation: Replace the hardcoded README version numbers with the release line only (or generate that block), and add a test/lint that fails when a version literal in README.md disagrees with VERSION.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| USE-P2-001 | P2 | Control-plane commands report success on enqueue and never surface the runner's ack, so a rejected start/stop/exec looks successful |
| USE-P2-002 | P2 | Web Start-run form has no input validation; blank/zero/negative durations and sizes are sent silently |
| USE-P2-003 | P2 | GUI 'Clean up environment' deletes the cached runner interpreter with no confirmation and no in-run guard |
| USE-P2-004 | P2 | Remote terminal / ad-hoc exec is only offered while a run is live, so idle runners cannot be diagnosed from the dashboard |
| USE-P3-001 | P3 | Deleting a schedule is immediate with no confirmation, unlike every other destructive control |
| USE-P3-002 | P3 | No completion notification for long runs; the only signal is the browser tab title |
| USE-P3-003 | P3 | Compare gives no empty state, and with a single finished run it compares the run with itself and presents the 0% deltas as a comparison |
| USE-P3-004 | P3 | README release/version strings are stale and mutually inconsistent with VERSION |
