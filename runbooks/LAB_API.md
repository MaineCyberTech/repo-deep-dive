# Lab job API

The lab job API lets a GitHub-hosted workflow (or a local agent) dispatch shell commands
to a Proxmox lab guest without inbound network access. It is the server side of
`tools/lab_runner.py`; `tools/lab-vpn/lab-audit-run.sh` uses it when the lab is reachable
and falls back to local execution otherwise.

## Topology

- **Server**: `tools/lab_api_server.py` (stdlib only), systemd unit `lab-api.service`,
  port `8722`, on the **testnuc** `ci-runner` guest — `http://192.168.222.201:8722`.
- Workspace root: `/var/lib/lab-repos`.
- Auth: `Authorization: Bearer <LAB_API_TOKEN>` (`/health` is unauthenticated).

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness (`{"status":"ok"}`) |
| GET | `/repos` | list git workspaces (repo, head, branch, dirty) |
| POST | `/sync` | clone/fetch a repo workspace (`{repo,org,ref,token}`) |
| POST | `/run` | run a shell command in a workspace (`{repo,cwd,command,timeout}`) |

## Deploy / refresh

On the Proxmox host (as root):

```bash
bash tools/lab-vpn/deploy-lab-api.sh 201        # pushes + installs into guest 201
```

Then wire the consuming repo:

```bash
gh variable set LAB_API_URL   -R MaineCyberTech/repo-deep-dive -b "http://192.168.222.201:8722"
gh secret   set LAB_API_TOKEN -R MaineCyberTech/repo-deep-dive -b "<TOKEN printed by the installer>"
```

The overlay preflight (`health`) checks `LAB2_API=http://192.168.222.201:8722/health` as part
of the "lab #2 reachable" group.

## Use

```bash
LAB_API_URL=http://192.168.222.201:8722 LAB_API_TOKEN=<t> \
  bash tools/lab-vpn/lab-audit-run.sh --repo chat --command "corepack pnpm test"
```

`lab_runner.py` fails closed: if `/health` is not `ok`, it refuses to dispatch (use
`--no-preflight` only deliberately).
