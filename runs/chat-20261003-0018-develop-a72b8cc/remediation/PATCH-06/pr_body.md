# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Secure the droplet SSH ingress for SEC-P1-007. The `ssh_allowed_ips` Terraform variable
defaulted to `0.0.0.0/0`, so SSH (port 22) allowed the whole internet. Commit `a72b8cc`
removed `TF_VAR_ssh_allowed_ips` from the dev infra workflow's Apply step, leaving both
provision workflows dependent on that wide default. This PR makes the variable **required**,
rejects `0.0.0.0/0` / `::/0` via validation, and supplies `TF_VAR_ssh_allowed_ips` from the
`SSH_ALLOWED_IPS` secret in every Terraform invocation of both provision workflows.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-06` — Secure SSH (SEC-P1-007)
- Repo / base: `chat` @ `a72b8cc` (`origin/develop`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-007` | P1 | open -> fixed | `ssh_allowed_ips` no longer has a `0.0.0.0/0` default; it is required and validated to reject world-open CIDRs, and is passed from `secrets.SSH_ALLOWED_IPS` in all Terraform steps |

## Changes

| File | What changed |
|---|---|
| `infra/terraform/variables.tf` | Removed `default = "0.0.0.0/0"`; `ssh_allowed_ips` is now required, with a validation block that rejects `0.0.0.0/0`, `::/0`, and empty entries. `main.tf` already consumes it for the port-22 `source_addresses`. |
| `.github/workflows/deploy-production.yml` | Added `TF_VAR_ssh_allowed_ips: ${{ secrets.SSH_ALLOWED_IPS }}` to the Terraform Import step (the Apply step already had it at line 137). |
| `.github/workflows/infra-development.yml` | Restored `TF_VAR_ssh_allowed_ips: ${{ secrets.SSH_ALLOWED_IPS }}` to the Terraform Apply step (removed by `a72b8cc`) and added it to the Import step, so the now-required variable is supplied. |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `grep -E 'default.*0\.0\.0\.0/0' infra/terraform/variables.tf` | ci-runner (Proxmox, lab API) | 1 | `remediation/PATCH-06/verify.log` — no match (PASS) |
| `grep -E 'default.*::/0' infra/terraform/variables.tf` | ci-runner (Proxmox, lab API) | 1 | `remediation/PATCH-06/verify.log` — no match (PASS) |
| `command -v terraform` / `tofu` | ci-runner (Proxmox, lab API) | n/a | **NOT RUN** — terraform/tofu not installed on ci-runner |
| `actionlint .github/workflows/deploy-production.yml .github/workflows/infra-development.yml` | ci-runner (Proxmox, lab API) | 1 | 18 diagnostics on base `a72b8cc` = 18 on branch; normalized diff empty — **no new actionlint diagnostics**; pre-existing shellcheck + `run_started_at` warnings |
| `gitleaks dir /tmp/p06scan --redact --exit-code 1` | ci-runner (Proxmox, lab API, gitleaks 8.30.1) | 0 | `no leaks found` (three changed files) |
| `<git diff> \| gitleaks stdin --redact` | ci-runner (Proxmox, lab API) | 0 | `no leaks found` |
| `gitleaks detect --no-git --redact --exit-code 1` | ci-runner (Proxmox, lab API) | 1 | 5 pre-existing findings, all outside this patch (`keyboard-shortcuts.tsx`, `validate.yml`, `infra/docker/.env.dev.example`) |

- Secret scan (gitleaks 8.30.1): **pass for the diff** — changed files and the diff itself are clean. The repo-wide run is red only on pre-existing unrelated files (see above), which belong to other owners/sets.
- Scope check: **pass with a documented companion change** — the diff is `variables.tf` + `deploy-production.yml` (the two files named by the patch set) plus a one-line-per-step wiring in `infra-development.yml`. That third file is required: making the variable required would otherwise fail the dev provision workflow, which invokes the same Terraform module.

## Evidence bundle

- `remediation/PATCH-06/diff.patch` — SHA-256 `4DD2DC90DB335038468FAA8B1575F5FD49FD4A62DD692097F142CC872D4A9347`
- `remediation/PATCH-06/manifest.json`
- `remediation/PATCH-06/verify.log`

## Risk and rollback

- Risk: **low-medium**. Behaviour change: Terraform now fails closed if `ssh_allowed_ips` is absent or set to `0.0.0.0/0`/`::/0`. Operators must have `SSH_ALLOWED_IPS` set as a repository/environment secret with the real operator CIDRs; otherwise provisioning stops (intentional). This is a firewall-only change — no application code, data, or containers are touched.
- Rollback: `git revert 7481c5f4e9186c28eb17bd080e232a302c121d40` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ the required workflow wiring)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Rollback is practical
- [ ] `SSH_ALLOWED_IPS` is populated with the real operator CIDRs before the next provision run (see open questions)

## Definition of done (for this set)

- `ssh_allowed_ips` has no world-open default and cannot be `0.0.0.0/0`/`::/0`.
- Every Terraform invocation in the provision workflows receives `TF_VAR_ssh_allowed_ips`.
- Port 22 `source_addresses` is driven only by the trusted CIDR variable.
  (`terraform plan` could not be run — terraform is not installed on the lab; recorded as not run.)

## Notes / open questions

- **Companion file beyond the patch-set list.** `remediation_plan.json` names `deploy-production.yml` and `variables.tf`, but the confirmed regression is in `infra-development.yml`: `a72b8cc` deleted `TF_VAR_ssh_allowed_ips` from its Apply step. Because `variables.tf` is now required, that workflow must supply it or fail; the PR includes the minimal wiring and flags it here. If reviewers prefer strict file scope, split the `infra-development.yml` line into a follow-up before making the variable required.
- **`terraform fmt -check` / `terraform validate` not run**: no `terraform`/`tofu` binary on `ci-runner`. Validation is written to standard `validation` syntax; HCL was reviewed manually. Recommend running `terraform fmt -check` + `terraform validate` in a lab with Terraform installed as a follow-up gate.
- **Secret value not inspected**: this patch assumes `SSH_ALLOWED_IPS` holds real trusted CIDRs. If it is currently `0.0.0.0/0`, the new validation will intentionally block the deploy until it is corrected.
- `deploy-development.yml` (app deploy, not the infra provision workflow) does not call Terraform and is unaffected.
