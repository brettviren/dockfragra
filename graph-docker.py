#!/usr/bin/env python

import os
import re
import sys
import ConfigParser
from collections import OrderedDict
import click
import networkx as nx
from dockermap.map.base import DockerClientWrapper
from dockermap.build.dockerfile import DockerFile
from dockermap.build.context import DockerContext
from dockermap.shortcuts import adduser

mydir = os.path.dirname(os.path.realpath(__file__))

def parse_config_section(filename, section):
    'Return a dictionary of config info relevant to the given section'
    from ConfigParser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.read(filename)
    lst = list()
    for k,v in cfg.items(section):
        if k == 'packages':
            v = ' '.join(v.split()) # normalize space/newline delimiters to spaces
        lst.append((k,v))
    lst.append(('image', section))
    lst.append(('host_dir', mydir)) # fixme: pick a better policy for this, see also fragments/user.df
    return OrderedDict(lst)

# fixme: mydir won't make sense once this package moves to a real setup.py install
def find_docker_fragment(path):
    'Return the contents of a fragment'
    for maybe in [path, os.path.join(mydir, path)]:
        if not os.path.exists(maybe):
            continue
        return open(maybe).read()
    raise RuntimeError('No such file: %s' % path)

def make_dockerfile_obj(from_image, fragment, **cfg):
    'Make and return a DockerFile object made from the given fragment file.'
    print 'DockerFile from fragment: "%s"' % fragment
    content = find_docker_fragment(fragment)
    df = DockerFile(from_image, maintainer = cfg['maintainer'],
                    initial = content.format(**cfg))
    return df

def split_list(string):
    return [s for s in re.split('[,\s]', string) if s]

def workflow_graph(**cfg):
    '''Return a graph corresponding to the given configuration.

    A node of this graph is the name of a Docker image.

    An edge of this graph holds a 'dockerfile' and a 'type' attribute.

    The 'dockerfile' attribute hods a DockerFile object which can
    transition from the image represented by the tail of the edge to
    the one represented by the head.

    The 'type' attribute holds "main" or "validation" to indicate if
    the transition is part of the main-line build or if it is a
    validation spur.
    '''

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
        df = make_dockerfile_obj(last_image, 'fragments/%s.df'%name, **cfg)
        graph.add_edge(last_image, next_image, type='main', dockerfile = df)
        last_image = next_image

    # test nodes
    validate = cfg.get('validate','')
    for name in split_list(validate):
        iname  = image_name(name)
        tname = iname + '-tested'
        fname = 'fragments/validate_%s.df' % name
        df = make_dockerfile_obj(iname, fname, **cfg)
        graph.add_edge(iname, tname, type='validation', dockerfile = df)

    return graph

def os_package_install(platform):
    'Return the command needed to install OS-packages on the given platform'
    platname,platver = platform.split(':')
    if platname in ['debian','ubuntu']:
        return 'apt-get update && apt-get install -y '
    if platname in ['fedora','scientific','centos']:
        return 'yum install -y '


def get_nodes(graph, value='main', key='type'):
    'Return all nodes that have the given key/value as an attribute'
    found = set()
    for n,d in graph.nodes(data=True):
        if d.get(key) == value:
            found.add(n)
    return found

def get_edges(graph, value='main', key='type'):
    'Return all edges with the given key/value as an attribute'
    found = set()
    for t,h,d in graph.edges(data=True):
        if d.get(key) == value:
            found.add((t,h,d))
    return found

def subgraph_by_edge_attr(graph, value='main', key='type'):
    'Return a subgraph made from matching edges'
    sg = nx.DiGraph()
    for t,h,d in graph.edges(data=True):
        if d.get(key) == value:
            sg.add_edge(t,h,**d)
    return sg
    

def sequence_graph(graph):
    '''Return an list of ordered edges

    The ordering is such that validation steps are run just after the
    state they are validating is produced.
    '''
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

def print_sequence(sequence):
    for edge in sequence:
        print "%s --> %s (%s)" % (edge[0], edge[1], edge[2]['type'])

def context_add_files(ctx, df):
    """Add any  files to the context which are added to the dockerfile.  

    Why doesn't docker-map handle this???"""
    for line in str(df).split('\n'):
        line = line.strip()
        if not line: continue
        prefix,rest = re.split('[\s]', line, 1)
        if prefix.lower() in ['add']:
            src,dst = re.split('[\s]', rest, 1) # fixme: this will puke if the first file has spaces
            ctx.add(src)

def run_sequence(client, sequence):
    for edge in sequence:
        print "%s --> %s (%s)" % (edge[0], edge[1], edge[2]['type'])
        df = edge[2]['dockerfile']
        print str(df)

        with DockerContext(df) as context:
            context_add_files(context, df)
            context.finalize()
            image = client.build_from_context(context, edge[1])

        if not image:
            raise RuntimeError('Failed to build "%s" -> "%s"' % edge[:2])

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
@click.option('--noop', default=False, is_flag=True,
              help='Just print what would happen.')
@click.option('--ups-products-dir', default=None,
              help='Set to a directory in the Docker container into which the build results will be installed as UPS products')
def doit(config, build, **kwds):
    cfg = parse_config_section(config, build)
    cfg.update(**kwds)
    cfg['os_package_install'] = os_package_install(cfg['platform'])
    cfg['host_dir'] = mydir     # fixme - this breaks once we do setup.py installs!

    graph = workflow_graph(**cfg)
    sequence = sequence_graph(graph)

    if kwds.get('noop'):
        print_sequence(sequence)
        return
        
    client = DockerClientWrapper(kwds['docker_url'])
    run_sequence(client, sequence_graph(graph))
        


if '__main__' == __name__:
    doit()
