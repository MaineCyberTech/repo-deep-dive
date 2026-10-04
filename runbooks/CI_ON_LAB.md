# Running CI on the self-hosted lab runners

The org's GitHub-hosted Actions minutes are exhausted, so hosted jobs on the private repos fail to
start ("no runner, no steps"). Org-level self-hosted runners are registered and online:

| Runner | Labels |
|---|---|
| `ci-runner` | `self-hosted`, `Linux`, `X64`, `lab`, `ci-runner` |
| `edge-builder` | `self-hosted`, `Linux`, `X64`, `lab`, `edge-builder` |

The common target label is **`lab`**, so `runs-on: [self-hosted, linux, x64, lab]` is usable
org-wide. Self-hosted jobs do not consume hosted minutes.

## Policy: trusted events only

Only **trusted events** may run on the lab:

- `push` to protected branches
- `schedule`
- `workflow_dispatch`

`pull_request` is **untrusted** and must stay on a GitHub-hosted runner (`ubuntu-latest`), because a
self-hosted runner executes job steps directly on lab infrastructure.

Rules:

1. A job whose `on:` has **no** `pull_request` trigger -> run it on
   `[self-hosted, linux, x64, lab]`.
2. A workflow that has **both** `push` and `pull_request` -> leave it on `ubuntu-latest` (do not
   split the workflow), unless a job is `schedule`/`workflow_dispatch`-only.

## Applied switches (2026-10-04)

| Repo | Workflow | Trigger | runs-on | Notes |
|---|---|---|---|---|
| `falcon` | `dependabot-merge.yml` | `schedule`, `workflow_dispatch` | lab | |
| `falcon` | `external-smoke.yml` | `schedule`, `workflow_dispatch` | **stayed hosted** | vantage-dependent, see below |
| `falcon` | `validate.yml` | `push`, `pull_request`, ... | stayed hosted | has a PR trigger |
| `falcon-edge` | `bake-image.yml` | `workflow_dispatch` | lab | heavy; needs passwordless sudo + loop mounts |
| `falcon-edge` | `boot-smoke.yml` | `workflow_dispatch` | lab | needs QEMU + a successful bake artifact |
| `falcon-edge` | `dependabot-merge.yml` | `schedule`, `workflow_dispatch` | lab | |
| `falcon-edge` | `publish-release.yml` | `workflow_dispatch` | lab | |
| `falcon-edge` | `validate.yml` | `push`, `pull_request`, ... | stayed hosted | has a PR trigger |
| `snowride` | `ci-foundation.yml` | `push`, `pull_request` | stays hosted | no trusted-only job |
| `snowride` | `supply-chain.yml` | `pull_request`, `push` | stays hosted | no trusted-only job |

## Vantage caveat (`falcon` external-smoke)

`external-smoke` asserts the **public** Cloudflare Access posture (302 -> `cloudflareaccess.com`)
*from GitHub's network*. Dispatched on the lab it runs from **inside** the network and observes
internal responses (`iris` -> 404, `soc` -> 302 `/app/login?`), so it fails on vantage, not on
toolchain. It must stay on a hosted runner. Never move a network-position-dependent gate to the lab
without re-checking what it measures.

## Verifying a switch

Dispatch a switched workflow on the branch (so the branch's YAML is used, not `main`'s):

```bash
gh workflow run <workflow>.yml -R MaineCyberTech/<repo> --ref ci/lab-runners
gh run watch <run-id> -R MaineCyberTech/<repo> --exit-status
gh api repos/MaineCyberTech/<repo>/actions/runs/<run-id>/jobs \
  --jq '.jobs[] | {name, conclusion, runner_name, labels}'
```

Confirm `runner_name` is `ci-runner`/`edge-builder` and `labels` includes `self-hosted` and `lab`.

## Reverting a switch

If a lab run fails because lab infrastructure is missing a toolchain or capability, revert that
workflow to `ubuntu-latest` rather than leaving broken CI, and record the gap. Switch again once the
runner is provisioned.
