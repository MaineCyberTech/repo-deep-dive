# Two guests, declaratively: ci-runner (LXC) + edge-builder (VM with cloud-init).
# Mirrors docs/LAB_ARCHITECTURE.md. This is a scaffold: review before applying
# to a live host. It does not create the Proxmox templates it clones from.

locals {
  runner_packages_json = jsonencode([
    "curl", "git", "jq", "ripgrep", "python3", "python3-pip", "python3-venv",
  ])
  edge_packages_json = jsonencode([
    "build-essential", "cmake", "git", "curl", "jq", "python3", "python3-pip",
    "python3-venv", "qemu-user-static", "binfmt-support", "docker.io",
  ])
}

# --- cloud-init user-data (snippets) ------------------------------------------
resource "proxmox_virtual_environment_file" "edge_user_data" {
  content_type = "snippets"
  datastore_id = var.snippet_datastore_id
  node_name    = var.proxmox_node

  source_raw {
    file_name = "edge-builder-user-data.yaml"
    data = templatefile("${path.module}/cloud-init/edge.yaml.tftpl", {
      hostname              = var.edge_builder_hostname
      username              = var.guest_username
      ssh_authorized_keys   = jsonencode(var.ssh_public_keys)
      packages              = local.edge_packages_json
    })
  }
}

resource "proxmox_virtual_environment_file" "runner_user_data" {
  content_type = "snippets"
  datastore_id = var.snippet_datastore_id
  node_name    = var.proxmox_node

  source_raw {
    file_name = "ci-runner-user-data.yaml"
    data = templatefile("${path.module}/cloud-init/runner.yaml.tftpl", {
      hostname            = var.ci_runner_hostname
      username            = var.guest_username
      ssh_authorized_keys = jsonencode(var.ssh_public_keys)
      packages            = local.runner_packages_json
    })
  }
}

# --- ci-runner (LXC container) -------------------------------------------------
resource "proxmox_virtual_environment_container" "ci_runner" {
  node_name    = var.proxmox_node
  vm_id        = var.ci_runner_vm_id
  tags         = ["lab", "runner"]
  unprivileged = var.ci_runner_unprivileged
  start_on_boot = true

  clone {
    vm_id = var.ct_template_vm_id
  }

  cpu {
    cores = var.ci_runner_cores
  }

  memory {
    dedicated = var.ci_runner_memory
  }

  disk {
    datastore_id = var.datastore_id
    size         = var.ci_runner_disk
  }

  network_interface {
    name   = "eth0"
    bridge = var.bridge
  }

  initialization {
    hostname = var.ci_runner_hostname

    ip_config {
      ipv4 {
        address = var.ci_runner_ipv4
        gateway = var.gateway
      }
    }

    user_account {
      keys = var.ssh_public_keys
    }

    dns {
      domain  = var.dns_domain
      servers = var.dns_servers
    }
  }

  features {
    nesting = true
    keyctl  = true
  }
}

# --- edge-builder (VM, cloud-init) --------------------------------------------
resource "proxmox_virtual_environment_vm" "edge_builder" {
  name      = var.edge_builder_hostname
  node_name = var.proxmox_node
  vm_id     = var.edge_builder_vm_id
  tags      = ["lab", "edge"]

  clone {
    vm_id = var.vm_template_vm_id
    full  = true
  }

  agent {
    enabled = true
  }

  cpu {
    cores = var.edge_builder_cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = var.edge_builder_memory
  }

  disk {
    datastore_id = var.datastore_id
    interface    = "scsi0"
    size         = var.edge_builder_disk
    file_format  = "raw"
  }

  network_device {
    bridge = var.bridge
    model  = "virtio"
  }

  initialization {
    datastore_id = var.datastore_id

    ip_config {
      ipv4 {
        address = var.edge_builder_ipv4
        gateway = var.gateway
      }
    }

    dns {
      domain  = var.dns_domain
      servers = var.dns_servers
    }

    user_data_file_id = proxmox_virtual_environment_file.edge_user_data.id
  }

  started = true
}
