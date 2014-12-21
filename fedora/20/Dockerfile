FROM fedora:20
MAINTAINER Brett Viren <bv@bnl.gov>
RUN yum -y install python-virtualenv \
                   make git gcc-c++ m4 subversion patch automake flex \
                   ncurses-devel zlib-devel libtool bzip2-devel \
                   libX11-devel libXmu-devel libXpm-devel libXft-devel \
                   mesa-libGL-devel mesa-libGLU-devel \
                   doxygen-latex tcl-devel \
                   libtool libbz2-dev libreadline-dev automake \
                   expat-devl readline-devel krb5-devel
RUN useradd -c "LBNE Software Build" -d /home/lbne -m -s /bin/bash lbne
USER lbne
WORKDIR /home/lbne
RUN virtualenv lbne-0.5.0 
RUN source lbne-0.5.0/bin/activate && pip install lbne-build==0.5.0 
RUN cp lbne-0.5.0/share/worch/wscripts/lbne/wscript .
RUN source lbne-0.5.0/bin/activate && waf --prefix=install --orch-config=lbne/suite-buildtools.cfg configure build
RUN source lbne-0.5.0/bin/activate && waf --prefix=install --orch-config=lbne/suite-compiler.cfg configure build
