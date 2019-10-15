This script creates an ansible env with a master container with ansible installed and customized amount of nodes.

Usage: ./proj_ansible.py one two    # where one and two would be the names of the nodes. Can create any amount of nodes and names them as you wish

A master container is running from an img_master/ssh built from the sickp/centos-sshd:latest public repository if the image already exists.
Else an img_node/ssh:centos is created and will be the skelaton of all the containers. A master container is created from it.
Python and Ansible are installed on the master container.
Custom nodes are created from the img_node/ssh:centos image
SSH keys are set to acess all nodes from the master
- Ansible Playbook creates nginx services on all nodes (not ready)
- Triggered by Travis-CI (not ready)
