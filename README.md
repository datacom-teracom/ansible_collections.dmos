# Datacom DmOS Collection - datacom.dmos

The Ansible [Datacom] DmOS collection includes a variety of Ansible content to help automate the
management of [Datacom] DmOS equipment.

[Datacom]: http://datacom.com.br

## Available features
- dmos_commands
- dmos_l2_interface
- dmos_l3 interface
- dmos_linkagg
- dmos_lldp
- dmos_log
- dmos_sntp
- dmos_twamp
- dmos_vlan
- dmos_user

# Usage guideline

## Install Collection

### Install collection from ansible-galaxy

```bash
ansible-galaxy collection install datacom.dmos
```

### Install collection from source code

```bash
git clone https://github.com/datacom-teracom/ansible_collections.dmos.git
cd ansible_collections.dmos
ansible-galaxy collection build
ansible-galaxy collection install datacom-dmos-*.tar.gz
```

### Verify installation and show module documentation

```bash
ansible-doc datacom.dmos.dmos_vlan
```

## example

Basic example need two files:
- hosts
- vlan.yml

### Invetory example
hosts
```yml
all:vars]
ansible_connection=ansible.netcommon.network_cli

[dmos]
DM4170 ansible_host=172.22.126.157

[dmos:vars]
ansible_user=admin
ansible_ssh_pass=admin
ansible_network_os=datacom.dmos.dmos
```

### playbook example
vlan.yml
```yml
---

- hosts: dmos
  gather_facts: no
  collections:
    - datacom.dmos
  tasks:
      - name: Configure vlan_ids
        dmos_vlan:
          config:
            - vlan_id: 2019
              interface:
                - name: gigabit-ethernet-1/1/1
                  tagged: true
              name: null
            - vlan_id: 2020
              name: dmos_vlan
              interface:
                - name: gigabit-ethernet-1/1/2
                  tagged: false
            - vlan_id: 2021
      - name: Remove vlan_ids
        dmos_vlan:
          config: []
          state: deleted
```

### Running example
```bash
ansible-playbook vlan.yml
```

