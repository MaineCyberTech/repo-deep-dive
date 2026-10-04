# `infra/lab` — declarative lab infrastructure

Rebuild the audit/CI lab (Proxmox VE host + guests + org runners) from code, so
the same definitions work on the current VM and, later, on a bare-metal host.
Companions: `docs/LAB_ARCHITECTURE.md` (design), `docs/LAB_VPN.md` (access),
`docs/LAB_IAC.md` (pointer + gaps), `runbooks/CI_ON_LAB.md` (runner policy).

> **Scaffold + design.** These files are written to be correct and idempotent,
> but they have **not been applied to the live lab**. Treat the first run as a
> dry run (`--check --diff` / `terraform plan`) with console access available.

## Topology (as-built)

| Host | Kind | Address | Role |
|---|---|---|---|
| `proxmox` | Proxmox VE node | `172.23.128.50` | Hypervisor |
| `ci-runner` | LXC container | `172.23.128.51` | Node/pnpm/docker/gitleaks/rg/python + Actions runner |
| `edge-builder` | VM (Ubuntu) | `172.23.128.52` | arm/build toolchain + Actions runner |

Overlay access and identity live in `docs/LAB_VPN.md` (WireGuard `wgaudit0`,
scoped `labvpn`). Runner policy — trusted events only — is in
`runbooks/CI_ON_LAB.md` and `docs/ARCHITECTURE.md`.

## Layout

```
infra/lab/
├── README.md                    # this file
├── ansible/                     # configure the host + guests (in-guest state)
│   ├── ansible.cfg
│   ├── inventory.example.ini    # copy -> inventory.ini (no secrets)
│   ├── requirements.yml         # ansible.posix, community.general
│   ├── site.yml                 # one playbook, four plays
│   ├── group_vars/all.yml
│   └── roles/
│       ├── base/                # users, ssh, packages, timezone
│       ├── proxmox_host/        # PVE preflight, bridges, ZFS notes
│       ├── guest_runner/        # node/pnpm/docker/gitleaks/rg/python + runner
│       └── guest_edge/          # arm/build toolchain
├── terraform/                   # create the guests (bpg/proxmox + cloud-init)
│   ├── versions.tf providers.tf variables.tf main.tf outputs.tf
│   ├── terraform.tfvars.example
│   └── cloud-init/*.yaml.tftpl
└── runners/                     # ephemeral org runners (ARC or --ephemeral)
    ├── README.md
    ├── bootstrap-runner.sh
    └── arc-values.yaml
```

## Build order

1. **Access.** Get onto the overlay per `docs/LAB_VPN.md`; confirm the lab
   preflight (`tools/lab-vpn/lab-audit-preflight.sh`) prints `RESULT: PASS`.
2. **Templates.** On the PVE host, have an LXC template (for `ci-runner`) and a
   cloud-init VM template (for `edge-builder`). Record their VMIDs.
3. **Guests (Terraform).**
   ```bash
   cd infra/lab/terraform
   cp terraform.tfvars.example terraform.tfvars   # fill in; never commit
   terraform init
   terraform fmt -check
   terraform validate
   terraform plan      # review
   terraform apply
   ```
4. **Guests (Ansible).** Configure them (and optionally the host):
   ```bash
   cd infra/lab/ansible
   ansible-galaxy collection install -r requirements.yml
   cp inventory.example.ini inventory.ini          # edit hosts/ips
   ansible-playbook -i inventory.ini site.yml --check --diff
   ansible-playbook -i inventory.ini site.yml
   ```
5. **Runners.** Register a persistent runner via `guest_runner`
   (`RUNNER_TOKEN=... runner_register=true`), or move to ephemeral runners under
   `infra/lab/runners/`.
6. **Verify.** `docs/LAB_VPN.md` health check + a dispatched workflow on the lab
   (`runbooks/CI_ON_LAB.md` §"Verifying a switch").

## Parameters (what to change per site)

| Where | Variable | Meaning |
|---|---|---|
| `ansible/inventory.ini` | hosts/`ansible_host` | lab addresses |
| `ansible/group_vars/all.yml` | `base_admin_user`, `base_timezone` | baseline admin |
| `ansible/roles/proxmox_host/defaults` | `proxmox_bridge_*`, `proxmox_manage_network` | host network |
| `ansible/roles/guest_runner/defaults` | `runner_labels`, `runner_scope`, `runner_version`, `node_major` | runner toolchain |
| `ansible/roles/guest_edge/defaults` | `edge_packages` | build toolchain |
| `terraform/variables.tf` | `proxmox_endpoint`, `datastore_id`, `bridge`, IPs, VMIDs, sizes | guest provisioning |

## Secrets (never committed)

- **Ansible:** admin SSH keys via `LAB_ADMIN_SSH_KEY` / `LAB_ADMIN_SSH_KEY_FILE`;
  runner registration token via `RUNNER_TOKEN`. `site.yml` reads them with
  `lookup('env', ...)` and marks the token `no_log`.
- **Terraform:** Proxmox API token via `PROXMOX_VE_API_TOKEN` or
  `proxmox_api_token` (sensitive). `terraform.tfvars`, `*.tfstate`,
  `*.tfstate.*`, `.terraform/`, and SSH keys must be gitignored (see
  `.gitignore`).
- **Runners:** ARC uses a GitHub App private key secret created out of band;
  `bootstrap-runner.sh` takes a short-lived token from the environment only.

## Bare-metal migration

Follows Phase 1 of `docs/LAB_ARCHITECTURE.md`. The same code applies because the
guests are described independently of whether the host is nested or physical.

1. Pick hardware (ECC RAM, NVMe + ZFS mirror/RAID, BMC/IPMI, UPS).
2. Install **Proxmox VE on the bare metal** (standard ISO install). This replaces
   the workstation route and the nested VM.
3. Join the audit overlay (`tools/lab-vpn/lab-audit-lab.sh ensure ...`) so
   remote access is restored before anything else.
4. Re-apply this repo: create the `vmbr0` lab bridge
   (`proxmox_manage_network: true`) and restore/import the guests, either
   - **restore** from PBS/`vzdump` backups, or
   - **rebuild** with `terraform apply` + `ansible-playbook site.yml`.
5. Re-register runners (or bring up ARC on a separate runner host).
6. Run the restore drill and record it (PBS follow-up below).
7. Decommission the old Proxmox VM; keep BMC/break-glass access documented.

## Scaffold vs verified

| Item | State |
|---|---|
| Ansible YAML (`site.yml`, roles, group_vars) | **Validated**: parses as YAML |
| Ansible playbooks | **Not run**: `ansible-playbook` not installed here; run `--syntax-check` where available |
| Terraform HCL | **Not validated**: `terraform` not installed here; run `fmt -check` + `validate` before use |
| cloud-init templates | Parse as YAML; `${...}` interpolation is rendered by Terraform |
| `bootstrap-runner.sh` | Executable (100755), `bash -n` clean; **not run** |
| `arc-values.yaml` | Parses as YAML; ARC/k3s **not installed** |
| Live lab changes | **None** — nothing here was applied |

## Top follow-ups

Not in this scaffold (tracked in `docs/LAB_IAC.md`): PBS/offsite backup + restore
drill; VLAN segmentation on the host bridge; lab observability/alerts; and a
secret broker (GitHub OIDC → short-lived lab tokens).
