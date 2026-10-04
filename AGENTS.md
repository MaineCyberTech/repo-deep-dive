# AGENTS.md — rules for AI agents in `repo-deep-dive`

This repository is an **audit + remediation framework**, not an application. Agents (OpenCode
subagents or others) use it to audit repos and to open remediation PRs.

## Rules (scoped — apply only when the condition holds)

### While auditing
1. **Evidence or `Unknown`.** Cite file/symbol/route/workflow/migration/lines; never invent.
2. **Read-only on app code.** Write only under the run folder.
3. **Reproduce headline claims** (verdicts, PASS, "verified/fixed") or mark `not reproducible`.
4. **No secrets.** Reference path + type and redact the value.

### While remediating
5. **Minimal scope.** Only the patch set's files (plus the tests/docs the fix requires).
6. **Draft PRs; no auto-merge or self-approval** unless the operator explicitly authorizes the merge.
7. **Fail closed.** Record `not run` + why; `verified-fixed` only with a commit/artifact at the
   current commit.

### When using the lab
8. **Preflight only for lab-dependent work.** `tools/lab-vpn/lab-audit-preflight.sh` must print
   `RESULT: PASS`; if the lab genuinely can't be used, run the work locally and record `MODE=local`.
   Audits that don't touch the lab are exempt. (Setup + local fallback: `runbooks/AGENT_SETUP.md`.)

### After an audit
9. **Standard pipeline** (`runbooks/POST_AUDIT_PIPELINE.md`): publish the audit first
   (`tools/publish_audit.py`), then draft remediation PRs, then merge only on authorization — audit
   PR first — then reconcile.

### On setup
10. **Confirm repo approvals.** When setting up the pack + lab, run `tools/repo_approvals.py` and
    record the result (`runbooks/AGENT_SETUP.md`); record controls you cannot set (branch
    protection, environment reviewers, tag rules) as `NEEDS-HUMAN` — never fake them.

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
| Agent setup (pack + lab + approvals) | `runbooks/AGENT_SETUP.md` + `tools/repo_approvals.py` |
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
