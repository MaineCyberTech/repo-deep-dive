# Lab architecture — Proxmox today, physical host tomorrow

Design for the audit/CI lab, written to be **portable to a bare-metal host**. Pairs with
`docs/LAB_VPN.md` (access) and `docs/ARCHITECTURE.md` (the pack platform).

## Today (as-built)

| Piece | Detail |
|---|---|
| Host | **Proxmox VE** node `testnuc` `192.168.222.222` (lab #2). The legacy node (`172.23.128.50`) is retired. |
| Guests | `ci-runner` `192.168.222.201` (container, root; lab job API `:8722`, node/pnpm/docker/gitleaks/rg/python) · `edge-builder` `192.168.222.202` (container, Ubuntu 24.04, `lab-python`/`lab-sudo`) · `lab-runner-2` `192.168.222.203` (container, docker). |
| Access | Dedicated audit overlay `wgaudit0` (UDP 51900) via `mct-portal-dev`; lab #2 = testnuc (`192.168.222.0/24`); scoped non-root `labvpn` identity; GitHub-routed onboarding (`lab-audit-gh.sh`). Separate falcon telemetry `wg0`. |
| Runners | GitHub Actions runners registered at the **org** in the `lab` runner group (public repos allowed, selected = repo-deep-dive + private repos); label `lab` (`ci-runner`, `edge-builder`, `lab-runner-2`), all online. |
| Secrets | `.env`, `lab-tokens.json` (lab job API), GitHub repo secrets. |
| Monitoring | falcon `wg0` + node-exporter (external). |

## Weaknesses

1. **Single host, no HA**, and the workstation route couples access to one PC.
2. **Manual guest config** — no IaC/templates/cloud-init; rebuilds aren't reproducible.
3. **Runners share lab guests**, are persistent (not ephemeral), and run as root in a container → PR-code risk.
4. **Secrets in files** (`.env`, `lab-tokens.json`) — no broker, no short-lived creds, no rotation automation.
5. **No backup/DR** for the lab host/guests; no snapshot policy or restore drill.
6. **Flat network** — no VLAN segmentation; firewall rules ad hoc.
7. **No lab-level observability/alerting** (host/guests/job API).
8. **No provisioning standard** — drift and snowflake guests.

## Target architecture (same shape on VM or bare metal)

1. **Hardware/host** — Proxmox VE; ZFS mirror (or HW RAID) + ECC; UPS; IPMI/BMC; optional 10GbE. On bare metal, PVE *is* the physical host (no hypervisor nesting).
2. **Network** — management + lab data VLANs; dedicated `vmbr` for the lab; the WireGuard overlay for remote; `dnsmasq` for `*.lab` names.
3. **Compute** — declarative guests: cloud-init templates + Ansible roles (or Terraform `bpg/proxmox`); role templates (runner, worker, edge). Prefer **ephemeral** runners via Actions Runner Controller (ARC) or `--ephemeral`.
4. **Runners** — org runner group + `lab` label; ephemeral; a **separate runner host** from lab workloads.
5. **Storage/backup** — Proxmox Backup Server (PBS) + scheduled snapshots + offsite (R2/S3); periodic restore drills.
6. **Identity/secrets** — broker: GitHub **OIDC → short-lived lab job tokens**; rotation register; retire long-lived `.env`/`lab-tokens.json`.
7. **Observability** — Prometheus + node-exporter for host/guests/job API; ntfy alerts; lab health surfaced in the preflight.
8. **IaC** — one repo (`infra/lab`) builds host + guests + runners; PVE API tokens; one-command rebuild.

## Physical-host migration plan

- **Phase 0 (now):** node runs as a VM; stabilize IaC, backups, and secrets first.
- **Phase 1:** pick hardware (ECC RAM, NVMe + ZFS mirror, BMC); install **Proxmox VE on bare metal**; restore VMs from PBS/`vzdump`; replace the workstation route with a real switch/VLAN.
- **Phase 2:** second node + PBS host; quorum/replication; PBS offsite.
- **Phase 3:** site readiness — UPS/PDU, cooling, uplink, IPMI network, physical security (office rack or colocation).
- **Phase 4:** retire the VM; the lab *is* the physical host; document BMC/break-glass access.

## Next steps (tracked in the roadmap)

- [~] `infra/lab/` IaC (Ansible/Terraform) for host + guests + templates —
  scaffolded (draft PR); see `infra/lab/README.md` and `docs/LAB_IAC.md`.
- [~] Ephemeral org runners (ARC) on a dedicated runner host —
  designed in `infra/lab/runners/`; not yet applied.
- [ ] PBS + offsite backups + a restore drill.
- [ ] Secret broker (OIDC) + enforced rotation register.
- [ ] Lab observability + alerts.
- [ ] Physical-host BOM + migration runbook.
