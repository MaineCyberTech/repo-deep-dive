output "ci_runner_id" {
  description = "VMID of the ci-runner container."
  value       = proxmox_virtual_environment_container.ci_runner.vm_id
}

output "ci_runner_ipv4" {
  description = "Configured IPv4 address of ci-runner."
  value       = var.ci_runner_ipv4
}

output "edge_builder_id" {
  description = "VMID of the edge-builder VM."
  value       = proxmox_virtual_environment_vm.edge_builder.vm_id
}

output "edge_builder_ipv4" {
  description = "Configured IPv4 address of edge-builder."
  value       = var.edge_builder_ipv4
}
