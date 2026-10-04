# Ephemeral org runners

Design for replacing the current **persistent, root-in-container** runners
(`ci-runner`, `edge-builder`) with runners that exist only for the life of a job.
Context: `docs/ARCHITECTURE.md` ("Fabric: runner policy") and
`runbooks/CI_ON_LAB.md`.

## Why ephemeral

| | Persistent (today) | Ephemeral (target) |
|---|---|---|
| Lifetime | Long-lived process, registered once | Registered per job, deregistered after |
| Blast radius | A bad job can leave state, credentials, or backdoors behind; the next job inherits it | Fresh sandbox per job; nothing persists |
| Untrusted PRs | Unsafe on the lab | Still policy-gated, but failure is contained |
| Scaling | Manual, fixed 2 runners | Scale to 0 → N with ARC |
| Tokens | Long-lived runner registration / job API token | Short-lived registration or JIT config |

Ephemeral does **not** remove the need for the trusted-events policy: an
ephemeral runner still executes job steps on lab hardware, so forks/PRs stay off
it unless the run is explicitly approved.

## Option A — ARC on k3s (recommended)

Actions Runner Controller (ARC) runs runner pods on Kubernetes/nomad-style
orchestration and creates a runner per job (`minRunners: 0`).

1. Provision a **dedicated runner node** (small VM or bare-metal host) — not the
   lab workload host.
2. Install k3s and ARC:
   ```bash
   curl -sfL https://get.k3s.io | sh -
   helm install arc --namespace arc --create-namespace \
     oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller
   ```
3. Create the GitHub App secret out of band and install the scale set:
   ```bash
   kubectl -n arc create secret generic lab-runners-github-app \
     --from-literal=github_app_id=... \
     --from-file=github_app_private_key=app.pem \
     --from-literal=github_app_installation_id=...
   helm install lab-runners --namespace arc -f arc-values.yaml \
     oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
   ```
4. Workflows target `runs-on: lab-ephemeral` (the `runnerScaleSetName`).

`arc-values.yaml` here is the scaffold: scale-to-zero, capped at 4, dind for
build jobs, pinned to a `lab-runners` node pool.

## Option B — single ephemeral runner (`--ephemeral`)

For one-off jobs, demos, or a host without Kubernetes, `bootstrap-runner.sh`
registers one runner with `config.sh --ephemeral` and runs it. It exits (and
deregisters) after a single job.

```bash
sudo RUNNER_TOKEN=<registration-token> \
     RUNNER_SCOPE=org RUNNER_ORG=MaineCyberTech \
     RUNNER_LABELS=self-hosted,linux,x64,lab,ephemeral \
     infra/lab/runners/bootstrap-runner.sh
```

Caveats:
- Registration tokens expire (~1h), so a naive systemd service can't re-register
  forever. Generate a fresh token per boot, or pass a **JIT config**
  (`run.sh --jitconfig <base64>`) obtained from the API at start-up.
- Do not write the token to a unit file or `.env`; pass it in the environment
  (systemd `Environment=` is visible to root — prefer a credential file with
  `LoadCredential=` or a broker).

## Tradeoffs vs the current persistent runners

- **Isolation:** the biggest win — untrusted or buggy jobs can't persist on the
  lab. Directly addresses weakness #3 in `docs/LAB_ARCHITECTURE.md`.
- **Cold start:** a fresh runner/container adds seconds to each job. ARC keeps a
  warm image; dind adds a bit more.
- **Capability gap:** the edge bake jobs need passwordless sudo, loop mounts, and
  QEMU. Those are hard to give a pod safely, so they may stay on a dedicated
  **trusted** persistent edge host (with the runner itself still ephemeral) —
  see `guest_edge`.
- **Secrets:** ephemeral runners should get short-lived, per-job credentials from
  a broker (GitHub OIDC), not long-lived org secrets. That is the secret-broker
  follow-up in `docs/LAB_IAC.md`.

## What is scaffold vs verified

- Scaffold (not run here): k3s + ARC install, `arc-values.yaml`, the App secret,
  and `bootstrap-runner.sh`.
- Verified: files are LF, `arc-values.yaml` is valid YAML, `bootstrap-runner.sh`
  is executable and passes `bash -n`.
