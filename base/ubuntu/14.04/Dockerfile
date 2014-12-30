FROM ubuntu:14.04
MAINTAINER Brett Viren <bv@bnl.gov>
RUN apt-get update
RUN apt-get -y install wget gettext file git subversion
RUN apt-get -y install python-virtualenv
RUN apt-get -y install make g++ m4 patch automake flex bison libtool
RUN apt-get -y install libncurses5-dev zlib1g-dev libbz2-dev \
                   libx11-dev libxmu-dev libxpm-dev libxft-dev \
                   libgl1-mesa-dev libglu1-mesa-dev \
                   tcl8.5-dev \
                   libexpat1-dev libreadline-dev libkrb5-dev
RUN apt-get -y install doxygen-latex 
RUN useradd -c "LBNE Software Build" -d /home/lbne -m -s /bin/bash lbne
