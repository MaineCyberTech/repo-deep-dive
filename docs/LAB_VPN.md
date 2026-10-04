# Lab audit VPN (WireGuard)

A dedicated WireGuard overlay that lets agents and developers reach the **Proxmox lab**
(`172.23.128.0/20`) from anywhere, through a public endpoint on the DigitalOcean droplet
`mct-portal-dev` (`138.197.105.82`). It is **separate** from the falcon telemetry VPN
(`wg0`, `10.99.0.0/24`, UDP 5182) and never edits it.

```
agent/dev ──(wg)──► mct-portal-dev  wgaudit0 10.250.0.1:51900 ──(wg)──► Proxmox lab peer 10.250.0.9
                                                                           └─ routes 172.23.128.0/20
                                                                              proxmox.lab .50 · ci-runner.lab .51 · edge-builder.lab .52
```

| Item | Value |
|---|---|
| Endpoint | `138.197.105.82:51900/udp` (`mct-portal-dev`) |
| Interface | `wgaudit0` (endpoint **and** lab host) |
| Overlay subnet | `10.250.0.0/24` (endpoint `.1`, lab `.9`, agents `.10+`) |
| Lab subnet routed | `172.23.128.0/20` |
| Friendly names | `lab-endpoint` `.1`, `proxmox.lab` `.50`, `ci-runner.lab` `.51`, `edge-builder.lab` `.52` |
| Peer registry | `/etc/wireguard/wgaudit0/peers.tsv` (name, ip, pubkey, added) |
| Key dir (endpoint) | `/etc/wireguard/wgaudit0/` + `/etc/wireguard/wgaudit0/clients/<name>.conf` |
| Key dir (lab) | `/etc/wireguard/wgaudit0/` |
| Scoped admin identity | SSH user `labvpn` (forced command; non-root) |
| Falcon VPN (do NOT touch) | `wg0` `10.99.0.0/24`, UDP 5182, hub `142.105.190.25` |

## Toolkit (`tools/lab-vpn/`)

| Script | Where | Purpose |
|---|---|---|
| `lab-audit-endpoint.sh` | public droplet | `inventory` / `ensure [labPub]` / `status` |
| `lab-audit-lab.sh` | Proxmox lab host | `inventory` / `ensure <serverPub> [endpointHost]` / `status` |
| `lab-audit-add-agent.sh` | endpoint (root) | add/refresh a peer: `<name> [public-key] [ip]`; maintains the registry; emits a client config |
| `lab-audit-list-agents.sh` | endpoint (root) | list peers + handshake age |
| `lab-audit-revoke-agent.sh` | endpoint (root) | remove a peer, its registry row and client key material |
| `lab-audit-verify.sh` | endpoint / lab / client | health check (handshake age + lab pings + lab API) → `RESULT: PASS|FAIL` |
| `lab-audit-scoped-deploy.sh` | endpoint (root) | install/refresh the scoped `labvpn` identity (user, forced command, sudoers, restart drop-in) |
| `labvpn-run.sh` | endpoint | the forced-command wrapper (installed to `/usr/local/bin/labvpn-run`) |
| `lab-audit-connect.sh` | agent/dev workstation | install a client config, add friendly names, verify the lab |

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

# 5) install/refresh the scoped non-root identity + self-heal drop-in
scp lab-audit-scoped-deploy.sh labvpn-run.sh lab-audit-add-agent.sh lab-audit-list-agents.sh \
    lab-audit-revoke-agent.sh lab-audit-verify.sh root@138.197.105.82:/root/
ssh root@138.197.105.82 'bash /root/lab-audit-scoped-deploy.sh'
# -> prints LABVPN_PRIVATE_KEY_FILE=/root/labvpn_ed25519 ; store it as secret LAB_ENDPOINT_SSH_KEY
```

Deployment is verified: `wg show wgaudit0` handshake both ways, `ping 172.23.128.51`, and
`curl http://172.23.128.51:8722/health`.

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
#  checks: ping lab-endpoint/proxmox.lab/ci-runner.lab/edge-builder.lab, curl http://ci-runner.lab:8722/health
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
- `wg-quick@wgaudit0` is `enabled` on both ends and has a systemd `Restart=always` drop-in, so the
  interface is recreated on boot and restarted if the process dies.

Note: GitHub disables scheduled workflows after 60 days of repo inactivity; re-enable or run it
manually if that happens.

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
