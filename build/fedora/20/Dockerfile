FROM fedora-20
MAINTAINER Brett Viren <bv@bnl.gov>
USER lbne
WORKDIR /home/lbne
RUN virtualenv venv
RUN source venv/bin/activate && pip install lbne-build
RUN cp venv/share/worch/wscripts/lbne/wscript .
RUN touch install-0-worch.flag
RUN source venv/bin/activate && waf --prefix=install --orch-config=lbne/suite-buildtools.cfg configure build
RUN touch install-1-buildtools.flag
RUN source venv/bin/activate && waf --prefix=install --orch-config=lbne/suite-compiler.cfg configure build
RUN touch install-2-compiler.flag
RUN source venv/bin/activate && waf --prefix=install --orch-config=lbne/suite-larsoft.cfg configure build
RUN touch install-3-larsoft.flag
