lvms_operator_install
=========

This Ansible role facilitates the installation of Advanced Cluster Management (LVMS) operators in an OpenShift environment.

Requirements
------------
* Access to an OpenShift cluster
* Properly configured kubeconfig file for cluster access
* Existing CatalogSource.


Role Variables
--------------

* `lvms_operator_install_kubeconfig_file`: (string) The file path of kubeconfig file for cluster. Default: undefined, If not provided, and no other connection options are provided, the Kubernetes client will attempt to load the default configuration file from ~/.kube/config. Can also be specified via `K8S_AUTH_KUBECONFIG` environment variable.
* `lvms_operator_install_namespace`: (string) The name of project LVMS is installed into. Default: `open-cluster-management`
* `lvms_operator_install_channel`: (string) LVMS Catalog Channel to install from. Default: Same as the default specified in Package Manifest.


Example Playbook
----------------

* Install LVMS on a cluster

```yaml
    - hosts: localhost
      roles:
         - { role: lvms_operator_install, lvms_operator_install_kubeconfig_file: "/tmp/kubeconfig" }
```
