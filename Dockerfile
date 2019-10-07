FROM centos

RUN dnf -y update
RUN dnf -y install python3 python3-pip vim iputils
RUN dnf -y install openssh-server
RUN dnf clean all

CMD ['/usr/sbin/init']
