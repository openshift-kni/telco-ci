# LLC Role

This Ansible role creates a PerformanceProfile for Low Latency Communications (LLC) workloads on OpenShift clusters.

## Description

The role creates a PerformanceProfile with specific configurations optimized for low latency workloads including:
- CPU isolation and reservation
- Huge pages configuration
- Real-time kernel settings
- Network optimizations
- NUMA topology settings

## Variables

The following variables can be customized in your playbook or inventory:

- `llc_performance_profile_name`: Name of the performance profile (default: "performance")
- `llc_performance_profile_namespace`: Namespace where the profile will be created (default: "openshift-cluster-node-tuning-operator")
- `pp_kubeconfig`: Path to kubeconfig file (optional)

## Usage

Include this role in your playbook:

```yaml
- hosts: localhost
  roles:
    - llc
```

Or with custom variables:

```yaml
- hosts: localhost
  vars:
    llc_performance_profile_name: "my-llc-profile"
  roles:
    - llc
```

## Requirements

- kubernetes.core collection
- Access to OpenShift cluster with cluster-admin privileges
- Node Feature Discovery and Performance Addon Operator installed