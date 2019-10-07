#!/bin/python3
"""
This script creates an ansible env with a master container and customized amount of nodes.

Usage: ./proj_ansible.py one two  # where one and two would be the names of the nodes
"""
import os
import sys

# Stop all containers
containers = os.popen("docker ps -a | grep -v CONTAINER | cut -d ' ' -f 1").read()
if containers != '':
    os.system("docker ps -a | grep -v CONTAINER |  cut -d' ' -f1 | xargs sudo docker stop")

# Delete all containers and images
    os.system("docker ps -a | grep -v CONTAINER | cut -d' ' -f1 | xargs docker rm; for i in `docker images | awk '{print $3}' | grep -v IMA`; do docker rmi $i; done")

nodes = len(sys.argv)
Nodes = sys.argv[1:]
for node in range(nodes):
    with open('Dockerfile', 'w') as dfile:
        l01 = "FROM centos"
        l02 = ""
        l03 = "RUN dnf -y update"
        l04 = "RUN dnf -y install python3 python3-pip vim iputils"
        l05 = "RUN dnf -y install openssh-clients"
        l06 = "RUN dnf -y install openssh-server"
        l07 = "RUN dnf clean all"
        l08 = "RUN pip3 install ansible"
        l09 = ""
        l10 = "CMD ['/usr/sbin/init']"
        if node == 0:
            print ('Node name: master')
            dfile.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(l01, l02, l03, l04, l05, l07, l08, l09, l10))
            dfile.close()
            # Build proj_master image
            os.system('docker build -t proj_master .')

            # Run the proj_master container
            os.system('docker run -itd --name master proj_master /bin/bash 2>logs/master_err.log 1>logs/master_out.log &')
        else:
            print ('Node name: ', sys.argv[node])
            dfile.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(l01, l02, l03, l04, l06, l07, l09, l10))
            dfile.close()
            # Build proj_node image
            os.system('docker build -t proj_node .')

            # Run the proj_node containers
            os.system('docker run -itd --name ' + sys.argv[node] + ' proj_node /bin/bash 2>logs/' + sys.argv[node] + '_err.log 1>logs/' + sys.argv[node] + '_out.log &')

# Get the containers IPs
os.system('echo master; docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" master')
os.system('''for n in ''' + str(Nodes) + '''; do echo $n; ping -qc1 `docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" $n`; done''')

# Show the created images and the running containers
os.system('docker images; docker ps -a')
