#!/usr/bin/python3
"""
This script creates a customized amount of containers.

Usage: ./create_containers.py one two    # where one and two would be the names of the nodes. Can create any amount of nodes and names them as you wish
"""
import os
import sys

if len(sys.argv) < 2:
    print()
    print('Please type the containers names')
    print()
    exit(0)

print()
print('Deleting all existsing containers')
# Stop all existsing containers
del_containers = os.popen("docker ps -a | grep -v CONTAINER | cut -d ' ' -f 1").read()
if del_containers != '':
    print()
    os.system("docker ps -a | grep -v CONTAINER |  cut -d' ' -f1 | xargs sudo docker stop > /dev/null")
#    os.system('docker ps -a')

# Delete all containers and images except img_master and img_node
    os.system("docker ps -a | grep -v CONTAINER | cut -d' ' -f1 | xargs docker rm > /dev/null; for i in `docker images | grep -Ev 'img|sickp' | awk '{print $3}' | grep -v IMA > /dev/null`; do docker rmi $i; done")

NumContainers = len(sys.argv) # Count num of containers
Containers = str(sys.argv[1:]).strip('[]').replace(',', '').replace("'", "")
print()
print('Creating Containers: ', Containers)
for node in range(NumContainers)[1:]:
    print()
    print('-- Containers name: ', sys.argv[node])  # Nodes containers
    os.system('docker run -dP --name=' + sys.argv[node] + ' eg_sshd ')

# Get the Containers IP
print()
os.system('''for n in ''' + str(Containers) + '''; do echo $n; docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" $n; done''')

# Create Ansible hosts file
print()
print('-- Creating Ansible hosts file to container')
os.system('cat /dev/null > hosts')
os.system('''for n in ''' + str(Containers) + '''; do echo -n "$n ansible_host=" >> hosts; docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" $n >> hosts; done''')

# Create keys on Containers
os.system("""for i in $(cat hosts | cut -d= -f2); do cat ~/.ssh/id_rsa.pub | sshpass -p 1234 ssh -o "StrictHostKeyChecking no" root@${i} "cat >> .ssh/authorized_keys && echo Key copied to ${i}"; done""")

# Show the created images and the running containers
os.system('echo; docker images; echo; docker ps -a; echo')
