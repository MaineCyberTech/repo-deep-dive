# --- Proxmox endpoint ---------------------------------------------------------
variable "proxmox_endpoint" {
  description = "Proxmox VE API endpoint, e.g. https://172.23.128.50:8006/"
  type        = string
}

variable "proxmox_api_token" {
  description = "Proxmox API token in `user@realm!tokenid=uuid` form. Prefer PROXMOX_VE_API_TOKEN."
  type        = string
  sensitive   = true
  default     = null
}

variable "proxmox_insecure" {
  description = "Skip TLS verification (true for the lab's self-signed cert)."
  type        = bool
  default     = true
}

variable "proxmox_node" {
  description = "Target Proxmox node name, e.g. pve."
  type        = string
  default     = "pve"
}

variable "proxmox_ssh_agent" {
  description = "Use a local ssh-agent for provider SSH (file transfers)."
  type        = bool
  default     = true
}

variable "proxmox_ssh_username" {
  description = "SSH user the provider uses on the node (usually root)."
  type        = string
  default     = "root"
}

# --- Placement -----------------------------------------------------------------
variable "datastore_id" {
  description = "Datastore for guest disks, e.g. local-lvm / local-zfs."
  type        = string
  default     = "local-lvm"
}

variable "snippet_datastore_id" {
  description = "Datastore that supports snippets (cloud-init user-data), e.g. local."
  type        = string
  default     = "local"
}

variable "bridge" {
  description = "Proxmox bridge for guest NICs."
  type        = string
  default     = "vmbr0"
}

variable "gateway" {
  description = "Default gateway for lab guests."
  type        = string
  default     = "172.23.128.1"
}

variable "dns_domain" {
  description = "DNS search domain for lab guests."
  type        = string
  default     = "lab"
}

variable "dns_servers" {
  description = "DNS servers for lab guests."
  type        = list(string)
  default     = ["172.23.128.1"]
}

# --- Templates -----------------------------------------------------------------
variable "ct_template_vm_id" {
  description = "VMID of the LXC container template for ci-runner (e.g. an ubuntu-22.04 template)."
  type        = number
}

variable "vm_template_vm_id" {
  description = "VMID of the cloud-init VM template for edge-builder."
  type        = number
}

# --- Common auth ---------------------------------------------------------------
variable "guest_username" {
  description = "Non-root admin user created by cloud-init in each guest."
  type        = string
  default     = "labadmin"
}

variable "ssh_public_keys" {
  description = "SSH public keys injected into guests. Supply out of band; do not commit private keys."
  type        = list(string)
  default     = []
}

# --- ci-runner (LXC) -----------------------------------------------------------
variable "ci_runner_vm_id" {
  description = "VMID for the ci-runner container."
  type        = number
  default     = 201
}

variable "ci_runner_hostname" {
  description = "Hostname for the ci-runner container."
  type        = string
  default     = "ci-runner"
}

variable "ci_runner_ipv4" {
  description = "CIDR address for ci-runner, e.g. 172.23.128.51/24."
  type        = string
  default     = "172.23.128.51/24"
}

variable "ci_runner_cores" {
  description = "CPU cores for ci-runner."
  type        = number
  default     = 4
}

variable "ci_runner_memory" {
  description = "Memory (MB) for ci-runner."
  type        = number
  default     = 8192
}

variable "ci_runner_disk" {
  description = "Disk size (GB) for ci-runner."
  type        = number
  default     = 32
}

variable "ci_runner_unprivileged" {
  description = "Run ci-runner unprivileged (recommended). Current as-built runs root; see README risk note."
  type        = bool
  default     = true
}

# --- edge-builder (VM) ---------------------------------------------------------
variable "edge_builder_vm_id" {
  description = "VMID for the edge-builder VM."
  type        = number
  default     = 202
}

variable "edge_builder_hostname" {
  description = "Hostname for the edge-builder VM."
  type        = string
  default     = "edge-builder"
}

variable "edge_builder_ipv4" {
  description = "CIDR address for edge-builder, e.g. 172.23.128.52/24."
  type        = string
  default     = "172.23.128.52/24"
}

variable "edge_builder_cores" {
  description = "CPU cores for edge-builder."
  type        = number
  default     = 4
}

variable "edge_builder_memory" {
  description = "Memory (MB) for edge-builder."
  type        = number
  default     = 8192
}

variable "edge_builder_disk" {
  description = "Disk size (GB) for edge-builder."
  type        = number
  default     = 64
}
