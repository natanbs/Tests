FROM sickp/centos-sshd:latest

RUN yum -y install vim iputils
RUN yum clean all
ENV PATH=${PATH}:/usr/lib64

RUN echo 'root:1234' | chpasswd
