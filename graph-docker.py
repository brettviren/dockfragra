#!/usr/bin/env python

import os
import ConfigParser
from collections import OrderedDict
import click
import networkx as nx
from dockermap.map.base import DockerClientWrapper
from dockermap.build.dockerfile import DockerFile
from dockermap.shortcuts import adduser

mydir = os.path.dirname(os.path.realpath(__file__))

def parse_config_section(filename, section):
    from ConfigParser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.read(filename)
    lst = list()
    for k,v in cfg.items(section):
        if k == 'packages':
            v = ' '.join(v.split()) # normalize space/newline delimiters to spaces
        lst.append((k,v))
    lst.append(('image', section))
    return OrderedDict(lst)

# A workflow is a graph with nodes representing a file system image
# and edge representing the Docker actions needed to transform between
# them.

def find_docker_fragment(path):
    fullpath = os.path.join(mydir, path)
    if not os.path.exists(fullpath):
        raise RuntimeError('No such file: %s' % fullpath)
    return open(fullpath).read()

def fill_dockerfile_obj(df, string):
    for line in string.split('\n'):
        line = line.strip()
        if not line: continue
        try:
            cmd,rest = line.split(' ',1)
        except ValueError,e:
            print string
            print 'Offending line: "%s"' % line
            raise
        df.prefix(cmd, rest.strip())

def make_dockerfile_obj(from_image, fragment, **cfg):
    df = DockerFile(from_image, maintainer = cfg['maintainer'])
    fragment = find_docker_fragment(fragment)
    fragment = fragment.format(**cfg)
    fill_dockerfile_obj(df, fragment)
    return df

import re
def split_list(string):
    return [s for s in re.split('[,\s]', string) if s]

def workflow_graph(**cfg):

    def image_name(derived=None):
        ret = cfg['image']
        if not derived:
            return ret
        return ret + '_' + derived

    graph = nx.DiGraph(**cfg)
    step = 0

    # main nodes
    last_image = cfg['platform']
    for name in split_list(cfg['workflow']):
        next_image = image_name(name)
        df = make_dockerfile_obj(last_image, 'fragments/worch.df', suite=name, **cfg)
        graph.add_edge(last_image, next_image, type='main', dockerfile = df)
        last_image = next_image

    # test nodes
    validate = cfg.get('validate','')
    for name in split_list(cfg['validate']):
        iname  = image_name(name)
        tname = iname + '-tested'
        fname = 'fragments/validate_%s.df' % name
        df = make_dockerfile_obj(iname, fname, **cfg)
        graph.add_edge(iname, tname, type='validation', dockerfile = df)

    return graph

def os_package_install(platform):
    platname,platver = platform.split(':')
    if platname in ['debian','ubuntu']:
        return 'apt-get update && apt-get install -y '
    if platname in ['fedora','scientific','centos']:
        return 'yum install -y '


def get_nodes(graph, value='main', key='type'):
    found = set()
    for n,d in graph.nodes(data=True):
        if d.get(key) == value:
            found.add(n)
    return found

def get_edges(graph, value='main', key='type'):
    found = set()
    for t,h,d in graph.edges(data=True):
        if d.get(key) == value:
            found.add((t,h,d))
    return found

def subgraph_by_edge_attr(graph, value='main', key='type'):
    sg = nx.DiGraph()
    for t,h,d in graph.edges(data=True):
        if d.get(key) == value:
            sg.add_edge(t,h,**d)
    return sg
    

def sequence(graph):
    ret = list()

    main_graph = subgraph_by_edge_attr(graph, 'main')
    test_graph = subgraph_by_edge_attr(graph, 'validation')

    transitions = list()

    for node in nx.topological_sort(main_graph):
        test_edges = test_graph.edges(node, data=True)
        if test_edges:
            transitions += test_edges
        main_edges = main_graph.edges(node, data=True)
        if main_edges:
            transitions += main_edges
    return transitions

@click.command()
@click.option('-c','--config', default='graph-docker.cfg',
              help='Set the configuration file')
@click.argument('build')
@click.option('-m','--maintainer', default='Brett Viren <bv@bnl.gov>',
              help='Set identifier of the maintainer')
@click.option('--docker-url', default='unix://var/run/docker.sock',
              help='Set the URL to the docker daemon')
@click.option('--install-user', default='lbne',
              help='Set a user name for the account that will install the software in the container')
@click.option('--ups-products-dir', default=None,
              help='Set to a directory in the Docker container into which the build results will be installed as UPS products')
def doit(config, build, **kwds):
    cfg = parse_config_section(config, build)
    cfg.update(**kwds)
    cfg['os_package_install'] = os_package_install(cfg['platform'])
    cfg['host_dir'] = mydir     # fixme - this breaks once we do setup.py installs!
    graph = workflow_graph(**cfg)

    for edge in sequence(graph):
        print "%s --> %s" % edge[:2]

if '__main__' == __name__:
    doit()
