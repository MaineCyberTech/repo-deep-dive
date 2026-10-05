# Lab audit VPN (WireGuard)

A dedicated WireGuard overlay that lets agents and developers reach **two Proxmox labs**
(lab #1 `172.23.128.0/20`, lab #2 `192.168.222.0/24`) from anywhere, through a public
endpoint on the DigitalOcean droplet `mct-portal-dev` (`138.197.105.82`). It is
**separate** from the falcon telemetry VPN (`wg0`, `10.99.0.0/24`, UDP 5182) and never edits it.

```
agent/dev ──(wg)──► mct-portal-dev  wgaudit0 10.250.0.1:51900
                                   ├──(wg)──► lab #1 peer 10.250.0.9 ── routes 172.23.128.0/20
                                   │            proxmox.lab .50 · ci-runner.lab .51 · edge-builder.lab .52
                                   └──(wg)──► lab #2 peer 10.250.0.8 ── routes 192.168.222.0/24  (host testnuc)
                                                testnuc.lab .222 · ci-runner2.lab .201
                                                edge-builder2.lab .202 · runner2.lab .203
```

Both lab subnets are advertised to clients. A client config whose `AllowedIPs` omits
`192.168.222.0/24` will handshake but be unable to route to lab #2.

| Item | Value |
|---|---|
| Endpoint | `138.197.105.82:51900/udp` (`mct-portal-dev`) |
| Interface | `wgaudit0` (endpoint **and** each lab host) |
| Overlay subnet | `10.250.0.0/24` (endpoint `.1`, lab #2 `testnuc` `.8`, lab #1 `.9`, agents `.10+`) |
| Lab subnets routed | lab #1 `172.23.128.0/20`, lab #2 `192.168.222.0/24` |
| Friendly names | `lab-endpoint` `.1`; lab #1: `proxmox.lab` `.50`, `ci-runner.lab` `.51`, `edge-builder.lab` `.52`; lab #2: `testnuc.lab` `.222`, `ci-runner2.lab` `.201`, `edge-builder2.lab` `.202`, `runner2.lab` `.203` |
| Peer registry | `/etc/wireguard/wgaudit0/peers.tsv` (name, ip, pubkey, added) |
| Key dir (endpoint) | `/etc/wireguard/wgaudit0/` + `/etc/wireguard/wgaudit0/clients/<name>.conf` |
| Key dir (lab) | `/etc/wireguard/wgaudit0/` (on each lab host, e.g. `proxmox` and `testnuc`) |
| Client AllowedIPs | `10.250.0.0/24, 172.23.128.0/20, 192.168.222.0/24` (both lab subnets) |
| Scoped admin identity | SSH user `labvpn` (forced command; non-root) |
| Falcon VPN (do NOT touch) | `wg0` `10.99.0.0/24`, UDP 5182, hub `142.105.190.25` |

## Toolkit (`tools/lab-vpn/`)

| Script | Where | Purpose |
|---|---|---|
| `lab-audit-endpoint.sh` | public droplet | `inventory` / `ensure [labPub]` / `status` |
| `lab-audit-lab.sh` | each Proxmox lab host (lab #1, lab #2) | `inventory` / `ensure <serverPub> [endpointHost]` / `status` |
| `lab-audit-add-agent.sh` | endpoint (root) | add/refresh a peer: `<name> [public-key] [ip]`; maintains the registry; emits a client config |
| `lab-audit-list-agents.sh` | endpoint (root) | list peers + handshake age |
| `lab-audit-revoke-agent.sh` | endpoint (root) | remove a peer, its registry row and client key material |
| `lab-audit-verify.sh` | endpoint / lab / client | health check (handshake age + lab pings + lab API) → `RESULT: PASS|FAIL` |
| `lab-audit-scoped-deploy.sh` | endpoint (root) | install/refresh the scoped `labvpn` identity (user, forced command, sudoers) |
| `labvpn-run.sh` | endpoint | the forced-command wrapper (installed to `/usr/local/bin/labvpn-run`) |
| `lab-audit-connect.sh` | agent/dev workstation | install a client config, add friendly names, verify the lab |
| `lab-audit-bootstrap.sh` | agent / server / workstation | one-command **connection setup**: generate a keypair, register the public key via the scoped identity, bring the tunnel up, verify |
| `lab-audit-run.sh` | agent / server | run a repo command **on the lab when reachable, else locally** (auto-sets up the tunnel first if `LABVPN_KEY` is present) |
| `lab-audit-gh.sh` | agent / server (with `gh`) | **seamless via GitHub**: `onboard` (dispatch onboarding, fetch config, connect), `run` (dispatch to the lab runner; local fallback), `status` |

All scripts are **idempotent**, **back up before writing**, run **pre-checks** (interface / UDP port /
subnet collisions), refuse to touch `wg0`, and print an inventory.

## Credentials & GitHub configuration (`MaineCyberTech/repo-deep-dive`)

| Kind | Name | Meaning |
|---|---|---|
| secret | `LAB_ENDPOINT_SSH_KEY` | private key for the **scoped** `labvpn` identity (NOT root) |
| variable | `LAB_ENDPOINT_HOST` | `138.197.105.82` |
| variable | `LAB_ENDPOINT_USER` | `labvpn` |
| variable | `LAB_OVERLAY_SERVER_PUB` | endpoint public key |
| secret | `LAB_API_TOKEN` | lab API token (ci-runner) for remote dispatch |
| variable | `LAB_API_URL` | `http://172.23.128.51:8722` |
| secret | `NTFY_TOPIC` / `NTFY_USERPASS` | ntfy alerting for the health workflow |
| variable | `NTFY_URL` | ntfy base URL (default `https://ntfy.sh`) |

The `labvpn` key can **only** run the forced commands below — add/list/revoke peers, read one client
config, and health-check. It cannot get a shell or run arbitrary commands, so the GitHub secret is far
weaker than root.

## First-time provisioning

```bash
# 1) endpoint (public droplet) - creates wgaudit0 + prints SERVER_PUB
scp lab-audit-endpoint.sh root@138.197.105.82:/root/
ssh root@138.197.105.82 'bash /root/lab-audit-endpoint.sh ensure'

# 2) lab host - joins and prints LAB_PUB (pass the endpoint's SERVER_PUB)
scp lab-audit-lab.sh root@172.23.128.50:/root/
ssh root@172.23.128.50 'bash /root/lab-audit-lab.sh ensure <SERVER_PUB> 138.197.105.82'

# 3) endpoint - add the lab peer (pass LAB_PUB) so the tunnel comes up
ssh root@138.197.105.82 'bash /root/lab-audit-endpoint.sh ensure <LAB_PUB>'

# 4) open the DigitalOcean cloud firewall for the overlay UDP port (mainecybertech
#    workflow wireguard-endpoint.yml action=firewall-allow udp_port=51900, or manually)

# 5) install/refresh the scoped non-root identity
scp lab-audit-scoped-deploy.sh labvpn-run.sh lab-audit-add-agent.sh lab-audit-list-agents.sh \
    lab-audit-revoke-agent.sh lab-audit-verify.sh root@138.197.105.82:/root/
ssh root@138.197.105.82 'bash /root/lab-audit-scoped-deploy.sh'
# -> prints LABVPN_PRIVATE_KEY_FILE=/root/labvpn_ed25519 ; store it as secret LAB_ENDPOINT_SSH_KEY
```

Deployment is verified: `wg show wgaudit0` handshake both ways, `ping 172.23.128.51`, and
`curl http://172.23.128.51:8722/health`.

## Adding a lab host / second lab (multi-lab overlay)

The endpoint can serve more than one lab peer at a time; each lab peer advertises its own subnet.
Lab #2 (`testnuc`, host `192.168.222.222`) is joined with a second `[Peer]` on the endpoint.
**Never re-run `lab-audit-endpoint.sh ensure` to add it** — that subcommand rebuilds
`wgaudit0.conf` and would drop the existing lab #1 peer (and agent peers). Append instead:

```bash
# 1) new lab host (testnuc) - install wireguard-tools, copy the script, join the overlay.
#    Use a DIFFERENT overlay address from lab #1 (lab #1 = .9, lab #2 = .8).
scp lab-audit-lab.sh root@192.168.222.222:/root/
ssh root@192.168.222.222 'LAB_IP=10.250.0.8 LAB_SUBNET=192.168.222.0/24 LAB_BRIDGE=vmbr0 \
    bash /root/lab-audit-lab.sh ensure <SERVER_PUB> 138.197.105.82'
# -> prints LAB_PUB

# 2) endpoint - back up, append the peer, then sync WITHOUT a full restart.
ssh root@138.197.105.82 'CONF=/etc/wireguard/wgaudit0.conf; \
    cp -a "$CONF" "$CONF.bak-$(date -u +%Y%m%dT%H%M%SZ)"; \
    printf "\n[Peer]\n# lab: testnuc (advertises 192.168.222.0/24)\nPublicKey = <LAB_PUB>\nAllowedIPs = 10.250.0.8/32, 192.168.222.0/24\n" >> "$CONF"; \
    wg syncconf wgaudit0 <(wg-quick strip wgaudit0); \
    ip route replace 192.168.222.0/24 dev wgaudit0'   # see note below

# 3) verify from the endpoint
ssh root@138.197.105.82 'wg show wgaudit0; ping -c2 192.168.222.201; ping -c2 192.168.222.222'
```

**`wg syncconf` does not install routes.** It applies keys and `AllowedIPs` to the running
interface but leaves the routing table alone, so add `192.168.222.0/24 dev wgaudit0` by hand after
syncing (`ip route replace ...`, idempotent). On the next `wg-quick up` wg-quick derives the same
route from `AllowedIPs` automatically, so the conf remains the source of truth across reboots.

Each lab host NATs the overlay source (`10.250.0.0/24`) onto its own bridge (`-s 10.250.0.0/24 -o
<bridge> -j MASQUERADE`) so guests reply; both labs use the same overlay subnet but advertise
disjoint lab subnets (`172.23.128.0/20` vs `192.168.222.0/24`), which is why the endpoint routes
them as separate peers.

## Onboarding a new agent / developer

**Recommended (GitHub, self-service).** Each agent generates its *own* keypair and keeps the private
key local:

```bash
wg genkey | tee agent-private.key | wg pubkey > agent-public.key
# GitHub → Actions → "Lab agent onboarding (WireGuard)" → Run workflow
#   agent_name       = <you>
#   agent_public_key = <contents of agent-public.key>     (optional)
```

If `agent_public_key` is supplied the endpoint stores only the public key; otherwise the endpoint
generates the keypair and the ready-to-use config (with the private key) comes back as a **build
artifact**. Then:

```bash
bash tools/lab-vpn/lab-audit-connect.sh lab-audit-<you>.conf
#  checks: ping lab-endpoint/proxmox.lab/ci-runner.lab/edge-builder.lab plus lab #2
#          (testnuc.lab/ci-runner2.lab/edge-builder2.lab/runner2.lab),
#          curl http://ci-runner.lab:8722/health
```

Windows: import `<name>.conf` in the WireGuard app, then use the friendly names (add them to
`C:\Windows\System32\drivers\etc\hosts` if you want names instead of IPs).

**Direct (endpoint-side, root or via the scoped identity):**

```bash
# on the endpoint
bash lab-audit-add-agent.sh <name>                 # server-generated key -> clients/<name>.conf
bash lab-audit-add-agent.sh <name> "<public-key>"  # agent-generated key (no private key stored)
```

Through the scoped identity (what the workflows use):

```bash
ssh -i labvpn_ed25519 labvpn@138.197.105.82 "add-agent <name> [<pubkey>]"
ssh -i labvpn_ed25519 labvpn@138.197.105.82 "list-agents"
ssh -i labvpn_ed25519 labvpn@138.197.105.82 "get-client <name>"
ssh -i labvpn_ed25519 labvpn@138.197.105.82 "revoke-agent <name>"
ssh -i labvpn_ed25519 labvpn@138.197.105.82 "health"
```

## Seamless access via GitHub (recommended for agents/servers)

GitHub **secrets are write-only** — an external machine cannot read `LAB_ENDPOINT_SSH_KEY`,
`LAB_API_TOKEN`, etc. back with `gh`. So the seamless pattern is to **route through GitHub
Actions**, which already holds them, and never copy keys/tokens to the machine:

```bash
# requires `gh auth login` (repo scope); nothing else
bash tools/lab-vpn/lab-audit-gh.sh setup my-server --repos chat,buddy   # connect + preflight + confirm rep approvals
bash tools/lab-vpn/lab-audit-gh.sh run --repo chat --command "corepack pnpm test"
bash tools/lab-vpn/lab-audit-gh.sh status
```
`setup` = onboard → preflight → `tools/repo_approvals.py` (confirms each repo's branch protection,
required checks, environment reviewers, required secrets and records `CONFIRMED/MISSING/NEEDS-HUMAN`;
see `runbooks/AGENT_SETUP.md`).

- `onboard` generates a keypair **locally**, sends only the public key through the
  `lab-agent-onboard` workflow, downloads the config artifact, and connects — no lab secret
  touches the machine. Offboard with the **Lab agent offboarding** workflow (or
  `lab-audit-gh.sh` dispatch of it).
- `run` dispatches `lab-tests.yml` to the lab's self-hosted runner (GitHub injects the secrets);
  if the runner/lab is unavailable it **falls back to local** execution.
- GitHub Actions themselves already read the secrets/vars directly — no change needed there.
- Read-only config that *is* retrievable via `gh variable get` (`LAB_ENDPOINT_HOST`,
  `LAB_ENDPOINT_USER`, `LAB_API_URL`) is used automatically by the helper.

## New agent / server: automatic setup + local fallback

On a fresh agent or a server running a repo, lab use is self-service and degrades gracefully:

```bash
# 1) set the connection up in one command (private key stays on this machine)
LABVPN_KEY=/path/to/labvpn_key bash tools/lab-vpn/lab-audit-bootstrap.sh [name]
#    -> generates a keypair, registers the public key, brings up wgaudit0, verifies the lab

# 2) run a command on the lab when reachable, otherwise locally
LAB_API_TOKEN=<lab token> bash tools/lab-vpn/lab-audit-run.sh \
    --repo <repo> --command "corepack pnpm test"
#    -> MODE=lab (dispatched to the lab) or MODE=local (lab unavailable: ran here)
```

- `lab-audit-bootstrap.sh` needs the scoped `labvpn` key (`LABVPN_KEY`). If it cannot register
  (endpoint down / key rejected) it exits non-zero and nothing is left half-configured.
- `lab-audit-run.sh` needs `LAB_API_TOKEN` for the lab path; without it, or if the lab is
  unreachable, it runs the command **locally** (in `--cwd`, default repo root). Which mode was used
  is printed, so it can be recorded as evidence (`lab` vs `local`).
- For CI on a server without lab runners, use `lab-tests.yml`/`verify-remediation.yml` when the lab
  is reachable; those are gated by the preflight and will not dispatch to a dead lab.

## Offboarding / revocation

Run the **"Lab agent offboarding (WireGuard)"** workflow with the agent name (or
`revoke-agent <name>` via the scoped identity). This removes the peer, its registry row, and any
generated client key material. **Revoke promptly when someone leaves** — an unremoved peer keeps full
lab access indefinitely.

## Health, watchdog & self-healing

- `lab-audit-verify.sh [--role endpoint|lab|client]` — handshake age, lab pings, lab API; exits
  non-zero on failure.
- **Lab overlay health** workflow — runs `health` on the endpoint every 15 minutes and pushes an
  **ntfy** alert on failure (and GitHub shows the failed run).
- `wg-quick@wgaudit0` is `enabled` on the endpoint and each lab host, so the interface is
  recreated on boot. `wg-quick@.service` is `Type=oneshot`, and systemd rejects `Restart=` for
  oneshot units — an earlier `Restart=always` drop-in made the unit a *bad-setting* that refused to
  start. That drop-in has been removed; the interface is kernel state kept alive by
  `RemainAfterExit=yes`, and the 15-minute overlay-health workflow is the watchdog.

Note: GitHub disables scheduled workflows after 60 days of repo inactivity; re-enable or run it
manually if that happens.

## Preflight gate (required before any work)

Lab access must be **set up and verified before work is dispatched**. This is enforced in four
places, so a broken overlay fails closed instead of queueing or half-running jobs:

1. **Agents/devs (local):** run `bash tools/lab-vpn/lab-audit-preflight.sh` (add
   `--remote-key <labvpn key>` to classify the lab remotely, and `--conf <file>` for the local
   fallback). It must print `RESULT: PASS` before you start an audit or remediation — see
   `AGENTS.md` rule 10. It:
   - checks the **lab state remotely first** (scoped `health`), independent of the local overlay;
   - only makes a **local attempt** (bring the overlay up) when the lab is confirmed down or
     unclassifiable — never when the lab is up;
   - reports one of `ready` / `ready_local_only` / `lab_up_local_down` / `lab_down` / `unknown`:
     - `lab_up_local_down` → the lab is fine; **fix local access** (onboard + `lab-audit-connect.sh`),
       do not rebuild the lab.
     - `lab_down` → **do not dispatch to the lab**; work may be attempted **locally only**.
   - Mode: `--mode local` (default) requires local reachability; `--mode lab` passes when the lab is
     up (dispatching to the lab / CI self-hosted runners), local overlay not required.
   - Also checks pack lint, and writes a stamp `tools/lab-vpn/.lab-ready.json` (gitignored).
2. **CI PR check:** the **Lab preflight** workflow (`lab-preflight.yml`) runs on PRs touching
   audit/remediation material and lints the pack + verifies the overlay/lab. Make
   `Lab preflight / lab` a **required status check** in branch protection.
3. **Workflow dispatch gate:** `remediation.yml`, `lab-tests.yml` and `verify-remediation.yml`
   declare `needs: preflight` (the reusable gate), so they will not dispatch to the lab unless the
   gate passes.
4. **API dispatch guard:** `tools/lab_runner.py` calls the lab `/health` endpoint and **refuses to
   dispatch** `run`/`sync` unless it is healthy (`--no-preflight` overrides, not recommended).

## Remote lab API (dispatching lab jobs)

Remote agents/CI can drive the lab job API through the pack's existing `tools/lab_runner.py` using
the `LAB_API_URL` / `LAB_API_TOKEN` configured above — no need to ship `lab-tokens.json`. The
`edge-builder` host uses a different token; pass it per invocation when targeting `.52`.

## Inventory / status (read-only)

```bash
bash lab-audit-endpoint.sh inventory      # endpoint: interfaces, conf, listeners, ufw, routes
bash lab-audit-lab.sh inventory           # lab: interfaces, conf, bridge, route to endpoint
bash lab-audit-endpoint.sh status         # wg show wgaudit0 (handshakes)
bash lab-audit-list-agents.sh             # peers + handshake age (endpoint)
```

## Design rules (learned the hard way — see `wireguard/RECOVERY.md`)

- **Never overwrite an existing `*.conf` you did not create.** Back up first; use a new interface name
  and a new UDP port for a new purpose. The 2026-10-04 incident clobbered the droplet's falcon `wg0`
  telemetry client config.
- The endpoint advertises the lab subnet; the lab peer **masquerades** `10.250.0.0/24` onto `vmbr0` so
  lab guests can reply.
- Firewall must be opened in **two** places: `ufw` on the host **and** the DigitalOcean cloud firewall.
- Client configs are secrets (private keys) — deliver out of band, `0600`, never commit.
- Prefer **agent-generated keys**: with a public-key add, no private key is ever stored server-side.
- **Key rotation:** re-adding the same name with a new public key **replaces** that peer's block (no
  duplicates) and reuses its address; re-run onboarding to get a fresh config.

## Troubleshooting

- **No handshake, `0 B received`** → the DO cloud firewall is blocking the UDP port, or the lab host
  can't reach the endpoint (`lab-audit-verify.sh`).
- **Tunnel up but lab unreachable** → lab peer missing NAT/forward rules, or the lab firewall dropping
  `wgaudit0`; re-run `lab-audit-lab.sh ensure`.
- **`health` fails at the API only** → the lab guests are down; bring them up (`scripts\lab-ensure-up.ps1`).
- **Endpoint unreachable at all** → confirm `systemctl status wg-quick@wgaudit0` and
  `ss -lunp | grep 51900` on the endpoint.
- **Scoped command denied** → only `list-agents`, `health`, `add-agent`, `revoke-agent`,
  `get-client` are allowed by `labvpn-run`.
