# Lab audit VPN (WireGuard)

A dedicated WireGuard overlay that lets agents and developers reach the **Proxmox lab**
(`172.23.128.0/20`) from anywhere, through a public endpoint on the DigitalOcean droplet
`mct-portal-dev` (`138.197.105.82`). It is **separate** from the falcon telemetry VPN
(`wg0`, `10.99.0.0/24`, UDP 5182) and never edits it.

```
agent/dev ──(wg)──► mct-portal-dev  wgaudit0 10.250.0.1:51900 ──(wg)──► Proxmox lab peer 10.250.0.9
                                                                          └─ routes 172.23.128.0/20 (ci-runner .51, edge-builder .52)
```

| Item | Value |
|---|---|
| Endpoint | `138.197.105.82:51900/udp` (`mct-portal-dev`) |
| Interface | `wgaudit0` (endpoint **and** lab host) |
| Overlay subnet | `10.250.0.0/24` (endpoint `.1`, lab `.9`, agents `.10+`) |
| Lab subnet routed | `172.23.128.0/20` |
| Key dir (endpoint) | `/etc/wireguard/wgaudit0/` + `/etc/wireguard/wgaudit0/clients/<name>.conf` |
| Key dir (lab) | `/etc/wireguard/wgaudit0/` |
| Falcon VPN (do NOT touch) | `wg0` `10.99.0.0/24`, UDP 5182, hub `142.105.190.25` |

## Toolkit (`tools/lab-vpn/`)

| Script | Where | Purpose |
|---|---|---|
| `lab-audit-endpoint.sh` | public droplet | `inventory` (read-only) / `ensure [labPub]` / `status` |
| `lab-audit-lab.sh` | Proxmox lab host | `inventory` / `ensure <serverPub> [endpointHost]` / `status` |
| `lab-audit-add-agent.sh` | public droplet | add an agent/dev peer and emit a client config |
| `lab-audit-connect.sh` | agent/dev workstation | install the client config and verify the lab |

All scripts are **idempotent**, **back up before writing**, run **pre-checks** (interface /
UDP port / subnet collisions), refuse to touch `wg0`, and print an inventory.

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

# 4) open the DigitalOcean cloud firewall for the overlay UDP port (use the
#    mainecybertech workflow, which has DO_API_TOKEN): dispatches
#    `.github/workflows/wireguard-endpoint.yml` with action=firewall-allow udp_port=51900
```

## Onboarding a new agent / developer

On the endpoint:
```bash
ssh root@138.197.105.82 'bash /root/lab-audit-add-agent.sh <name> 138.197.105.82'
# -> /etc/wireguard/wgaudit/clients/<name>.conf  (deliver securely)
```
On the agent/dev workstation (Linux/macOS/WSL):
```bash
bash tools/lab-vpn/lab-audit-connect.sh <name>.conf
# checks: ping 10.250.0.1, ping 172.23.128.51/.52, curl http://172.23.128.51:8722/health
```
Windows: import `<name>.conf` in the WireGuard app, then verify the same pings.

## Inventory / status (read-only)

```bash
bash lab-audit-endpoint.sh inventory      # endpoint: interfaces, conf, listeners, ufw, routes
bash lab-audit-lab.sh inventory           # lab: interfaces, conf, bridge, route to endpoint
bash lab-audit-endpoint.sh status         # wg show wgaudit0 (handshakes)
```

## Design rules (learned the hard way — see `wireguard/RECOVERY.md`)

- **Never overwrite an existing `*.conf` you did not create.** Back up first; use a new
  interface name and a new UDP port for a new purpose. The 2026-10-04 incident clobbered the
  droplet's falcon `wg0` telemetry client config.
- The endpoint advertises the lab subnet; the lab peer **masquerades** `10.250.0.0/24` onto
  `vmbr0` so lab guests can reply.
- Firewall must be opened in **two** places: `ufw` on the host **and** the DigitalOcean cloud
  firewall (via `DO_API_TOKEN`).
- Client configs are secrets (private keys) — deliver out of band, `0600`, never commit.

## Troubleshooting

- **No handshake, `0 B received`** → the DO cloud firewall is blocking the UDP port (open it
  with the workflow), or the lab host can't reach the endpoint (check `ip route get`).
- **Tunnel up but lab unreachable** → lab peer missing the NAT/forward rules, or the lab
  firewall dropping `wgaudit0`; re-run `lab-audit-lab.sh ensure`.
- **Endpoint unreachable at all** → confirm `systemctl status wg-quick@wgaudit0` and
  `ss -lunp | grep 51900` on the endpoint.
