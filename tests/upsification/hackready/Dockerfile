FROM lbne-0.5.2-debian-7.7-1_larsoft-tested
MAINTAINER Brett Viren <bv@bnl.gov>
USER root
RUN apt-get install -y emacs
USER lbne
RUN bash -l -c 'urman -z products init'
RUN bash -l -c 'for n in tmp/upspack/*.tar.bz2 ; do echo $n; tar -C products -xf $n; done'
USER root
RUN ln -sf /bin/bash /bin/sh
USER lbne

RUN git config --global user.name "Brett Viren"
RUN git config --global user.email "bv@bnl.gov"

RUN git clone https://github.com/brettviren/worch-ups.git
RUN bash -l -c 'cd worch-ups && python setup.py sdist'
RUN bash -l -c 'pip install worch-ups/dist/worch-ups-*.tar.gz'

RUN git clone https://github.com/LBNE/lbne-build.git
RUN cd lbne-build && git remote add github git@github.com:LBNE/lbne-build.git
RUN rm -f lbne-build/dist/lbne-build-*.tar.gz
RUN bash -l -c 'cd lbne-build && git checkout develop && python setup.py sdist'
RUN bash -l -c 'pip install lbne-build/dist/lbne-build-*.tar.gz'


RUN bash -l -c 'source products/setups && setup root v5_34_23 -q gcc48 && root --version -q -b'
# RUN bash -l -c 'source products/setups && setup genie v2_8_0 -q gcc48 && genie-config'
ENTRYPOINT /bin/bash

