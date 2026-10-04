# Lab Infrastructure-as-Code

The declarative build for the audit/CI lab now lives in **`infra/lab/`**:

- `infra/lab/README.md` — build order, parameters, bare-metal migration, and the
  scaffold-vs-verified table.
- `infra/lab/ansible/` — roles to configure the Proxmox host and both guests
  (`base`, `proxmox_host`, `guest_runner`, `guest_edge`).
- `infra/lab/terraform/` — `bpg/proxmox` config to create `ci-runner` (LXC) and
  `edge-builder` (VM, cloud-init).
- `infra/lab/runners/` — ephemeral org runners: ARC (k3s) and a `--ephemeral`
  bootstrap script, with the tradeoff vs today's persistent runners.

Start there. This page is a **pointer plus the explicitly deferred work**, so the
roadmap in `docs/LAB_ARCHITECTURE.md` and `docs/ARCHITECTURE.md` can link here.

## Scope of this scaffold

Declarative, parameterized, LF, no secrets. It provides the host/guest/runner
plumbing only. It is **not applied** to the live lab, and it deliberately leaves
out the items below.

## What remains (deferred, in priority order)

1. **PBS / backup + restore drill.** No Proxmox Backup Server, snapshot policy,
   offsite copy, or tested restore yet. Add scheduled `vzdump`/PBS jobs, offsite
   (R2/S3), and perform + record a restore drill against the bare-metal host.
   *(Weakness #5.)*
2. **VLAN segmentation.** The host bridge in `proxmox_host` can be made
   VLAN-aware, but management/data VLANs and firewall rules are not declared
   here; the network is still flat. Define VLANs, per-guest tags, and default-deny
   host firewall rules. *(Weakness #6.)*
3. **Secret broker / OIDC.** Ansible still passes an admin key and a runner
   registration token via the environment; Terraform still uses a long-lived PVE
   API token. Replace with GitHub **OIDC → short-lived lab job tokens**, retire
   `.env`/`lab-tokens.json`, and enforce a rotation register in CI.
   *(Weaknesses #2 and #4.)*
4. **Observability.** No lab-level Prometheus/node-exporter, ntfy alerting, or
   lab-health signal in the preflight from this code (falcon `wg0` +
   node-exporter are external). Add exporters for host/guests and the job API.
   *(Weakness #7.)*
5. **Second node / quorum.** Single host, no HA; out of scope until PBS exists.
   *(Weakness #1.)*

## Non-goals

- It does **not** create the LXC/VM templates it clones from.
- It does **not** change runner policy; trusted-events-only still applies
  (`runbooks/CI_ON_LAB.md`).
