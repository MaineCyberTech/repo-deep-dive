# AGENTS.md — rules for AI agents in `repo-deep-dive`

This repository is an **audit + remediation framework**, not an application. Agents (OpenCode
subagents or others) use it to audit repos and to open remediation PRs.

## Golden rules

1. **Evidence or `Unknown`.** Every finding cites repository evidence (file, symbol/route/workflow/
   migration, lines). Never invent functionality, risks, or controls.
2. **No secrets.** Never print or commit secret values; reference path + type and redact.
3. **Audit-only during an audit.** Do not modify application code; write only under the run folder.
4. **Reproduce before asserting.** For headline claims (verdicts, PASS/APPROVED, "verified/fixed"),
   reproduce from the repo or mark `not reproducible`.
5. **A finding is `verified-fixed` only with an artifact at the current commit** — assertions and
   intentions do not close findings.

## Remediation rules (see `prompts/REMEDIATION_RUNNER.md`)

6. **Draft PRs only.** Never auto-merge and never self-approve; a human/reviewer merges.
7. **Minimal scope.** Touch only the patch set's files (plus the tests/docs the fix requires).
8. **Fail closed.** Run the patch set's verification in the lab (`ci-runner` / `edge-builder`) and
   `gitleaks` the diff; if a gate cannot run, record it as `not run` and why — never fabricate.
9. **Reconcile, don't rewrite.** Update finding statuses via `tools/remediation_status.py`; never
   edit the original finding reports.
10. **Lab preflight first (fail closed).** On a fresh agent/server, prefer the GitHub route so no
    lab key/token is handled locally: `bash tools/lab-vpn/lab-audit-gh.sh onboard <name>` to set the
    connection up and `bash tools/lab-vpn/lab-audit-gh.sh run --repo <r> --command "<cmd>"` to use
    the lab (falls back to local). Then, before any audit or remediation work — and before
    dispatching work to the lab — run `bash tools/lab-vpn/lab-audit-preflight.sh`
    (`--mode lab` when dispatching to the lab/CI; `--remote-key <labvpn key>` to classify the lab
    remotely; `--conf <client.conf>` only as a local fallback). It MUST print `RESULT: PASS`.
    If it does not: **STOP**. Specifically, when it reports `lab_up_local_down` fix **local access**
    (`LABVPN_KEY=<labvpn key> bash tools/lab-vpn/lab-audit-bootstrap.sh` sets the connection up
    automatically); when it reports `lab_down`/`unknown` (the lab genuinely can't be used), do
    **not** dispatch to the lab — run the work **locally** instead via
    `bash tools/lab-vpn/lab-audit-run.sh --repo <repo> --command "<cmd>"`, which uses the lab when
    reachable and falls back to local execution. Record which mode was used. The same gate runs in
    CI (`Lab preflight`) and as a `needs:` gate on the remediation/lab workflows, and
    `tools/lab_runner.py` refuses to dispatch unless the lab API is healthy.

11. **Publish after every audit (standard pipeline).** After an audit, follow
    `runbooks/POST_AUDIT_PIPELINE.md`: publish the **full audit first** with
    `tools/publish_audit.py` (writes a `check_run.sh`-valid `runs/<repo>-<run>/`, updates
    `runs/INDEX.md`, and opens a **draft** audit PR in the repo), then run remediation agents for
    a plan + draft remediation PRs, then merge **only on explicit authorization** — audit PR first,
    then remediation PRs — and either finish the queue or stop for delegation.

## Working on the pack itself

- **Keep the digest current.** After ANY file change, run `tools/pack_digest.sh`, then
  `tools/lint_pack.sh` (must print `RESULT: PASS`).
- **Line endings & exec bits.** Text files are LF; `*.sh` are executable (`100755`). Windows checkouts
  can silently drop both — verify with `git ls-files --eol` / `git ls-files -s`.
- **Prompts must pass the structure gate.** A counted domain prompt (`NN_*.md`) needs the
  `Required report structure` headings. Non-domain runbooks (e.g. `REMEDIATION_RUNNER.md`,
  `MASTER_RUNNER_*.md`) are not counted — keep them out of the numeric sequence.
- **Prompt counts are load-bearing** — `examples/audit_manifest*.example.json` and
  `profiles/*.manifest.json` carry `promptCount`; update them if you add/remove a domain prompt.
- **Versioning.** `VERSION` is compared against `README.md` and the JSON `version` fields by
  `lint_pack.sh`; bump all of them together (or none). Add a `CHANGELOG.md` entry.
- **Runs are flat.** Every folder under `runs/` must be a valid run (`tools/check_run.sh` → PASS);
  add it to `runs/INDEX.md`.

## Lab access (agents & developers)

The Proxmox lab (`172.23.128.0/20`) is reachable over a **dedicated** WireGuard overlay
(`wgaudit0`, UDP `51900`) through the public endpoint `mct-portal-dev` (`138.197.105.82`).
This is **separate** from the falcon telemetry VPN (`wg0`) — never reuse or edit `wg0`.

- Full guide: [`docs/LAB_VPN.md`](docs/LAB_VPN.md) · toolkit: `tools/lab-vpn/`.
- **To connect (self-service):** generate your own keypair and dispatch the GitHub
  **"Lab agent onboarding (WireGuard)"** workflow with your name + public key, then
  `bash tools/lab-vpn/lab-audit-connect.sh lab-audit-<you>.conf` (Linux/macOS/WSL), or import it in
  the WireGuard app (Windows/macOS). Access is issued via a **scoped non-root** identity, not root.
- **To verify:** `ping lab-endpoint`/`proxmox.lab`/`ci-runner.lab`/`edge-builder.lab` (hostnames the
  connect script adds), and `curl http://ci-runner.lab:8722/health`.
- **To revoke:** dispatch **"Lab agent offboarding (WireGuard)"** with the name (removes the peer and
  its key material). Do this promptly when someone leaves.
- **Health / inventory:** `lab-audit-verify.sh` (handshake + lab pings + API), `lab-audit-list-agents.sh`,
  `lab-audit-endpoint.sh inventory`, `lab-audit-lab.sh inventory`.

## Map

| Need | Location |
|---|---|
| Lab WireGuard access | `docs/LAB_VPN.md` + `tools/lab-vpn/` |
| Post-audit pipeline | `runbooks/POST_AUDIT_PIPELINE.md` + `tools/publish_audit.py` |
| Audit runner (generic) | `prompts/MASTER_RUNNER_FULL_HARDENING.md` |
| Audit runner (falcon lab) | `prompts/MASTER_RUNNER_FALCON_LAB.md` + `profiles/falcon-lab.md` |
| Remediation runner | `prompts/REMEDIATION_RUNNER.md` + `profiles/remediation.md` |
| LLM-free checks | `tools/deterministic_checks.py` (+ `aggregate_findings.py`) |
| Machine chain | `tools/run_toolchain.py` (`check → collect → score → dashboard → diff → CSV`) |
| Scaffold a run | `tools/new_run.py` |
| Inventory | `tools/repo_inventory.py` |
| Lab test dispatch (HTTP) | `tools/lab_runner.py` (ci-runner / edge-builder job API) |
| Validate a run | `tools/check_run.sh <run>` |
| Validate the pack | `tools/lint_pack.sh` / `tools/self_test.sh` |

## Verification before committing

```bash
bash tools/pack_digest.sh                        # regenerate PACK_DIGEST.txt
bash tools/lint_pack.sh                          # RESULT: PASS expected
bash tools/self_test.sh                          # toolchain self-test (optional)
bash tools/lab-vpn/lab-audit-preflight.sh        # RESULT: PASS expected before work
```

Never commit with a failing `lint_pack.sh`. Never fabricate a test result in a PR body or finding.
