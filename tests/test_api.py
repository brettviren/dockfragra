#!/usr/bin/env python

from io import BytesIO
from docker import Client
dockerfile = '''
# Shared Volume
FROM busybox:buildroot-2014.02
MAINTAINER first last, first.last@yourdomain.com
CMD ["/bin/sh"]
'''
f = BytesIO(dockerfile.encode('utf-8'))
cli = Client(base_url='unix://var/run/docker.sock')
#gen = cli.build( fileobj=f, rm=True, tag='yourname/volume' )
gen = cli.build( fileobj=f, rm=True, tag='mytag' )
for line in gen:
    print line

