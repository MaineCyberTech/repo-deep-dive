# Platform architecture — `repo-deep-dive`

How the pack, the lab, and the CI fit together, what is strong, what is ad hoc, and the target
shape. Complements `docs/DEEP_DIVE_ROADMAP.md` (improvements) and `docs/LAB_ARCHITECTURE.md` (lab).

## Layers

```
Lenses → Engine → Evidence → Orchestration → Remediation → Fabric → Governance
```

| Layer | What it is | Current | Gap |
|---|---|---|---|
| **Lenses** | Domain prompts + focused security/supply-chain/CI | `prompts/**` (46 domains), focused lenses | No lens registry; adding a lens is code, not config |
| **Engine** | Deterministic + LLM analysis | `deterministic_checks.py`, `aggregate_findings.py`, LLM deep-dives | No first-class full-domain driver (`tools/full_domain.py`); no `--fast/--full` budget |
| **Evidence** | Runs, findings, registers, digest | `check_run.sh`, `findings.json`, registers, `PACK_DIGEST.txt`, `runs/INDEX.md` | Digest CRLF fragility; no `generated_at_commit` staleness binding; stale-clone findings (chat pilot) |
| **Orchestration** | Runs the whole pass | runbook + `publish_audit.py` | No control plane/state (`tools/pass.py`), no resume/dedup, no org pass manifest |
| **Remediation** | Plan → draft PRs → merge → reconcile | `remediation_plan.py`, `REMEDIATION_RUNNER.md`, `remediation_status.py` | No work queue/ownership/dedup; conflict handling is manual |
| **Fabric** | Lab overlay, runners, secrets | `wgaudit0` + scoped `labvpn` + GitHub-routed access; **org runners label `lab` (online)** | No reusable lab workflow; no ephemeral runners; secrets still file-based; no broker |
| **Governance** | Approvals, policy, scorecard | `repo_approvals.py` (verify) + `POST_AUDIT_PIPELINE.md` | Controls not declared/applied as code (`apply_approvals.py`); no scorecard/FP registry |

## Recent additions

- **Runner fabric:** `ci-runner` + `edge-builder` re-registered at the **org** level with a `lab`
  label (both online); enables free self-hosted CI for the private repos, which are out of
  GitHub-hosted minutes.
- **Agent setup:** `runbooks/AGENT_SETUP.md` + `tools/repo_approvals.py` (confirm/record approvals).
- **Post-audit pipeline:** `runbooks/POST_AUDIT_PIPELINE.md` + `tools/publish_audit.py`.
- **Scoped rules:** `AGENTS.md` rules grouped by applicability.

## Target additions (priority order)

1. **Control plane** — `tools/pass.py`: org pass state machine (`sweep → deep-dive → publish →
   remediate → merge → reconcile`) with `docs/audits/_org/<pass>/manifest.json`, resume + dedup.
2. **Reusable lab CI** — `.github/workflows/reusable-lab-ci.yml` (org) + a repo template; `runs-on:
   [self-hosted, linux, x64, lab]` for **trusted events only**; PRs stay on hosted (or same-repo on
   the lab when minutes are exhausted). Ephemeral runners (ARC) for isolation.
3. **Approvals as code** — `approvals.yml` + `tools/apply_approvals.py` (idempotent apply) + drift
   check; `repo_approvals.py` verifies.
4. **Credential broker** — GitHub OIDC → short-lived lab job tokens; retire `.env`/`lab-tokens.json`
   handling; rotation register enforced in CI.
5. **Evidence integrity** — LF-normalized digest; `generated_at_commit` staleness binding; verify
   the run base is an ancestor of HEAD before publish.
6. **Coverage/quality** — lens registry, coverage matrix, FP registry, org scorecard (open/closed,
   TTL, gate pass rate, FP rate, cost).
7. **Full-domain driver** — `tools/full_domain.py` (per-domain subagents → pack-schema findings →
   aggregate), one pilot done for `chat`.

## Fabric: runner policy

- **Trusted events** (push to protected branches, `schedule`, `workflow_dispatch`) → lab runners
  (`[self-hosted, linux, x64, lab]`).
- **`pull_request`** (esp. forks) → GitHub-hosted by default. For the out-of-minutes private repos,
  allow **same-repo PRs** on the lab, forks blocked/pending approval, and least-privilege
  `permissions:` with no org secrets on PR jobs.
- Prefer **ephemeral** runners so untrusted runs can't persist on the lab host.
