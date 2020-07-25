#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-07-24 11:07:29
# @Last Modified by:   Ming
# @Last Modified time: 2020-07-25 16:01:37
import logging
import sys

import click
import igraph
import pandas as pd

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

FEATURES = ['average_path_length',
            'diameter',
            'average_degree',
            'graph_density',
            'clustering_coefficient',
            'modularity']


def deal_graph(graph, feature):
    """
    Graph feature analysis
    """
    res = {}
    res['nodes'] = graph.vcount()
    res['edges'] = graph.ecount()
    for i in feature:
        if i == "average_path_length":
            res['average_path_length'] = graph.average_path_length()
        elif i == "diameter":
            res["diameter"] = graph.diameter()
        elif i == "average_degree":
            res['average_degree'] = igraph.mean(graph.degree())
        elif i == "graph_density":
            res["graph_density"] = graph.density()
        elif i == "clustering_coefficient":
            res[
                "clustering_coefficient"] = graph.transitivity_avglocal_undirected()
        elif i == "modularity":
            cluster = graph.community_multilevel()
            res["modularity"] = cluster.modularity
    return res


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Network analysis with igraph
    """
    pass


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--node',
              required=True,
              type=click.Path(),
              help="The node file(header needed)")
@click.option('--edge',
              required=True,
              type=click.Path(),
              help="The edge file(header needed)")
@click.option('--feature',
              metavar=f'[average_path_length | diameter | ...]',
              type=click.Choice(FEATURES),
              multiple=True,
              help=f"""The network feature you want to analysis,
                        you can choose from {FEATURES}""")
@click.option("-o", "--out",
              default='result.tsv',
              show_default=True,
              type=click.Path(),
              help="The output file")
def analysis(node, edge, feature, out):
    """
    Network analysis with target network

    node: The first col must the nodes
    edge: The first and second must the source and target
    """
    logging.info(f"Parse the node file {node}...")
    df_node = pd.read_csv(node, sep='\t', header=0)
    logging.info(f"Parse the edge file {edge}...")
    df_edge = pd.read_csv(edge, sep='\t', header=0)

    g = igraph.Graph()
    g.add_vertices(df_node.iloc[:, 0])
    g.add_edges(df_edge.iloc[:, 0:2].values)

    logging.info(f"Analysis the network for feature {feature}...")
    res = deal_graph(g, feature)
    logging.info(f"Out put the result to {out}")
    with open(out, 'w') as OUT:
        print(*res.keys(), sep='\t', file=OUT)
        print(*res.values(), sep='\t', file=OUT)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-n", '--node',
              required=True,
              type=int,
              help="The init node number for analysis")
@click.option("-p", '--probability',
              type=float,
              help="The probability of edges")
@click.option("-e", '--edge',
              type=int,
              help="The number of edges")
@click.option('--method',
              default="ER",
              show_default=True,
              type=click.Choice(['ER']),
              help="The method used for init network, only support Erdős-Rényi now")
@click.option('--feature',
              metavar=f'[average_path_length | diameter | ...]',
              type=click.Choice(FEATURES),
              multiple=True,
              help=f"""The network feature you want to analysis,
                        you can choose from {FEATURES}""")
@click.option('--iteration',
              default=1,
              show_default=True,
              type=int,
              help="The iteration for generate the graph")
@click.option("-o", "--out",
              default='result.tsv',
              show_default=True,
              type=click.Path(),
              help="The output file")
def random(node, probability, edge, method, feature, iteration, out):
    """
    Random network analysis
    """
    res = []
    logging.info(f"Analysis the network for feature {feature}...")
    if method == "ER":
        logging.info(f"Method: Erdős-Rényi")
        logging.info(f"Iteration: {iteration}")
        logging.info(f"Node number: {node}")
        if probability and edge:
            logging.error(
                f"probability and edge are conflict, select only one")
            sys.exit(1)
        elif probability:
            logging.info(f"Probability: {method}")
            for i in range(iteration):
                g = igraph.Graph.Erdos_Renyi(n=node, p=probability)
                res.append(deal_graph(g, feature))
        elif edge:
            logging.info(f"Edge number: {edge}")
            for i in range(iteration):
                g = igraph.Graph.Erdos_Renyi(n=node, m=edge)
                res.append(deal_graph(g, feature))
        else:
            logging.error(f"Must offer param probability or edge")
            sys.exit(1)
    else:
        logging.error(f'Not support {method} now')
        sys.exit(1)
    df = pd.DataFrame(res)
    df_mean = df.mean(axis=0).to_frame().T
    logging.info(f"Out put the result to {out}")
    df_mean.to_csv(out, sep='\t', index=False)


cli.add_command(analysis)
cli.add_command(random)

if __name__ == "__main__":
    cli()
