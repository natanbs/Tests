#!/bin/python3
"""
This script creates an ansible env with a master container with ansible installed and customized amount of nodes.

Usage: ./proj_ansible.py one two    # where one and two would be the names of the nodes. Can create any amount of nodes and names them as you wish
"""
import os
import sys

# Stop all existsing containers
del_containers = os.popen("docker ps -a | grep -v CONTAINER | cut -d ' ' -f 1").read()
if del_containers != '':
    os.system("docker ps -a | grep -v CONTAINER |  cut -d' ' -f1 | xargs sudo docker stop")
    os.system('docker ps -a')

# Delete all containers and images except img_master and img_node
    os.system("docker ps -a | grep -v CONTAINER | cut -d' ' -f1 | xargs docker rm; for i in `docker images | grep -Ev 'img|sickp' | awk '{print $3}' | grep -v IMA > /dev/null`; do docker rmi $i; done")

# Create Dockerfile
with open('Dockerfile', 'w') as dfile:
    l01 = "FROM sickp/centos-sshd:latest"
    l02 = ""
    #l03 = "RUN yum -y update"
    l04 = "RUN yum -y install vim iputils"
    l05 = "RUN yum clean all"
    l06 = "ENV PATH=${PATH}:/usr/lib64"
    l07 = ""
    l08 = "RUN echo 'root:1234' | chpasswd"
    #l09 = "CMD echo '1234' | passwd --stdin root"
    dfile.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(l01, l02, l04, l05, l06, l07, l08))
    dfile.close()
    print('-- Dockerfile created')

Containers = len(sys.argv) # Count num of containers
Nodes = str(sys.argv[1:]).strip('[]').replace(',', '').replace("'", "") #
print()
print('Create master and nodes:')
print('Nodes: ', Nodes)
for node in range(Containers):
    # Master container
    if node == 0:
        print()
        print('master container')

        # Check if img_master image exists and run it as master if it does.
        if os.popen('docker images | grep img_master > /dev/null && echo Yes').read().replace('\n', '') != 'Yes':
            # Build img_node with ssh image
            print()
            print('-- Build img_node image')
            os.system('docker build -t img_node/ssh:centos .')
            print('-- Running master from img_node image')
            os.system('docker run -dP --name=master img_node/ssh:centos 2>logs/master_err.log 1>logs/master_out.log &')
            os.system('sleep 2')

        else:
            print()
            print('-- Running master from img_master image')
            print('docker run -dP --name=master img_master/ssh:centos 2>logs/master_err.log 1>logs/master_out.log &')
            os.system('docker run -dP --name=master img_master/ssh:centos 2>logs/master_err.log 1>logs/master_out.log &')

        print()
        os.system('docker images; docker ps -a')

        # Install Python and pip on master
        print()
        print('-- Install Python, pip and Ansible on the master container')
        os.system('docker exec -it master yum -y install epel-release python3 python3-pip sshpass')
        os.system('docker exec -it master pip3 install --upgrade pip')
        os.system('docker exec -it master pip3 install ansible')

        # Create img_master image from the master if it is missing
        print()
        print('-- Creating img_master from master container')
        os.system('docker commit master img_master/ssh:centos')


    # Nodes containers
    else:
        print()
        print('-- Node name: ', sys.argv[node])  # Nodes containers

        # Check if img_node image exists and run it if it does
        if os.popen('docker images | grep img_node > /dev/null && echo Yes').read().replace('\n', '') != 'Yes':
            # Build img_node image if it does not exists (due to the loop)
            print()
            print('-- img_node image does not exist')
            print('-- Build img_node image')
            os.system('docker build -t img_node/ssh:centos .')

        # Run the img_node containers
        print()
        print('AAA')
        print('-- Running node ' + sys.argv[node] + ' from img_node image')
        os.system('docker run -dP --name=' + sys.argv[node] + ' img_node/ssh:centos 2>logs/' + sys.argv[node] + '_err.log 1>logs/' + sys.argv[node] + '_out.log &')

# Get the master IP
os.system('sleep 2')
os.system('echo master; docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" master')

# Get the nodes IP
os.system('''for n in ''' + str(Nodes) + '''; do echo $n; docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" $n; done''')

# Create Ansible hosts file and copy to the master image
print()
print('-- Creating and copying Ansible hosts file to container')
os.system('cat /dev/null > hosts')
os.system('''for n in ''' + str(Nodes) + '''; do echo -n "$n ansible_host=" >> hosts; docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" $n >> hosts; done''')
os.system('docker cp hosts master:/root')
os.system('docker cp ansible.cfg master:/root')
os.system('docker cp ansible_ping.yml master:/root')

# Create keys on nodes
os.system('''docker exec -it master bash -c "mkdir -p /root/.ssh; chmod 0700 /root/.ssh; ls -la /root/.ssh"''')
os.system('''docker exec -it master bash -c "rm -f /root/.ssh/id_rsa; ssh-keygen -t rsa -qN '' -f /root/.ssh/id_rsa"''')
os.system('''docker exec -it master bash -c "echo 'StrictHostKeyChecking no' >> ~/.ssh/config; chmod 600 /root/.ssh/config"''')
os.system('''docker exec -it master bash -c "for i in $(cat hosts | cut -d= -f2); do sshpass -p '1234' ssh-copy-id -i ~/.ssh/id_rsa.pub $i; done"''')

# Show the created images and the running containers
os.system('docker images; docker ps -a')
