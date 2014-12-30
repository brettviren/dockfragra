FROM ubuntu-14.04
MAINTAINER Brett Viren <bv@bnl.gov>
USER lbne
ENV ftp_proxy http://192.168.1.165:3128/ \
 FTP_PROXY http://192.168.1.165:3128/ \
 http_proxy http://192.168.1.165:3128/ \
 HTTP_PROXY http://192.168.1.165:3128/ \
 https_proxy http://192.168.1.165:3128/ \
 HTTPS_PROXY http://192.168.1.165:3128/
WORKDIR /home/lbne
RUN virtualenv venv
RUN /bin/bash -c "source venv/bin/activate && pip install lbne-build"
RUN cp venv/share/worch/wscripts/lbne/wscript .
RUN touch install-0-worch.flag
RUN /bin/bash -c "source venv/bin/activate && waf --prefix=install --orch-config=lbne/suite-buildtools.cfg configure build"
RUN touch install-1-buildtools.flag
RUN /bin/bash -c "source venv/bin/activate && waf --prefix=install --orch-config=lbne/suite-compiler.cfg configure build"
RUN touch install-2-compiler.flag
RUN /bin/bash -c "source venv/bin/activate && waf --prefix=install --orch-config=lbne/suite-larsoft.cfg configure build"
RUN touch install-3-larsoft.flag
