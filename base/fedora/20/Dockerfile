FROM fedora:20
MAINTAINER Brett Viren <bv@bnl.gov>
ENV ftp_proxy http://192.168.1.165:3128/
ENV FTP_PROXY http://192.168.1.165:3128/
ENV http_proxy http://192.168.1.165:3128/
ENV HTTP_PROXY http://192.168.1.165:3128/
ENV https_proxy http://192.168.1.165:3128/
ENV HTTPS_PROXY http://192.168.1.165:3128/
RUN yum -y install wget gettext bzip2 file git subversion
RUN yum -y install python-virtualenv 
RUN yum -y install make gcc-c++ m4 patch automake flex bison libtool
RUN yum -y install ncurses-devel zlib-devel bzip2-devel \
                   libX11-devel libXmu-devel libXpm-devel libXft-devel \
                   mesa-libGL-devel mesa-libGLU-devel \
                   tcl-devel \
                   expat-devel readline-devel krb5-devel
RUN yum -y install doxygen-latex 
RUN useradd -c "LBNE Software Build" -d /home/lbne -m -s /bin/bash lbne
