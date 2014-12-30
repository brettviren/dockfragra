#!/usr/bin/env python

import os
import ConfigParser
from collections import OrderedDict
import click
from dockermap.map.base import DockerClientWrapper
from dockermap.build.dockerfile import DockerFile
from dockermap.shortcuts import adduser


mydir = os.path.dirname(os.path.realpath(__file__))

def parse_config_section(filename, section):
    from ConfigParser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.read(filename)
    items = cfg.items(section)
    return OrderedDict(items)

def debian_install(*pkgs):
    line = ' '.join(pkgs)
    return 'apt-get install -y ' + line
def redhat_install(*pkgs):
    line = ' '.join(pkgs)
    return 'yum install -y ' + line


def do_build(imagename, url, maintainer, **kwds):
    platform = kwds['from']
    platname,platver = platform.split(':')
    packages = kwds['packages'].split()
    suites = kwds['suites'].split()
    release = kwds['release']

    if platname in ['debian','ubuntu']:
        install_cmd = debian_install
    if platname in ['fedora','scientific','centos']:
        install_cmd = redhat_install

    client = DockerClientWrapper(url)

    with DockerFile(platform, maintainer) as df:
        # Base system
        df.run(install_cmd(*packages))

        # Add and setup LBNE user
        df.run('useradd -c "LBNE Software Build" -d /home/lbne -m -s /bin/bash lbne')
        df.prefix('USER','lbne')
        df.prefix('WORKDIR','/home/lbne')
        # fixme: need to find dot.profile better!
        df.prefix('ENV','HOME /home/lbne') # doesn't get set???
        df.run('rm -f /home/lbne/.bash*')

        # note, we assume this will source venv/bin/activate for us!
        df.add_file(os.path.join(mydir, 'dot.profile'), '/home/lbne/.bash_profile')

        # setup lbne-build
        df.run('virtualenv venv')
        df.run("bash -l -c 'pip install lbne-build==%s'" % release)
        df.run("cp venv/share/worch/wscripts/lbne/wscript .")

        # todo: add lbne release
        # todo: may need to "bash -c" all commands
        for suite in suites:
            df.run("bash -l -c 'waf --prefix=install --orch-config=lbne/suite-%s.cfg configure build'" % suite)
            df.run("touch built-suite-%s" % suite) # just a marker

        client.build_from_file(df, imagename)

    return

@click.command()
@click.option('-c','--config', default='lbne-docker.cfg',
              help='Set the lbne-docker.cfg file')
@click.option('-u','--url', default='unix://var/run/docker.sock',
              help='Set the URL to the docker daemon')
@click.option('-m','--maintainer', default='Brett Viren <bv@bnl.gov>',
              help='Set identifier of the maintainer')
@click.argument('build')
def doit(config, url, maintainer, build):
    cfg = parse_config_section(config, build)
    do_build(build, url, maintainer, **cfg)


if '__main__' == __name__:
    doit()
