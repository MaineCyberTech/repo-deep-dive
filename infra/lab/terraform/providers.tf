# Proxmox VE provider (bpg/proxmox). Credentials come from variables /
# environment (PROXMOX_VE_API_TOKEN) — never committed.
#
# Create a dedicated API token with least privilege, e.g.:
#   pveum user token add terraform@pve lab --privsep 1
#   # grant:  PVEVMAdmin on /vms, PVEDatastoreAdmin on /storage, PVESysAdmin? no
# Prefer a role scoped to /vms + the datastores used here.
provider "proxmox" {
  endpoint  = var.proxmox_endpoint
  api_token = var.proxmox_api_token
  insecure  = var.proxmox_insecure

  ssh {
    agent    = var.proxmox_ssh_agent
    username = var.proxmox_ssh_username
  }
}
