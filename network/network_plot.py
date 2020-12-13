#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-12-12 22:27:50
# @Last Modified by:   Ming
# @Last Modified time: 2020-12-12 22:27:50
import logging

import click
import igraph
import numpy as np
import pandas as pd

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

LAYOUT = ["auto", "circle", "drl", "fruchterman_reingold",
          "grid_fruchterman_reingold", "kamada_kawai", "lgl",
          "random", "reingold_tilford", "reingold_tilford_circular"]


def get_layout(graph, layout):
    """
    Get the layout obj

    :param graph: The igraph obj
    :param layout: The layout to apply
    :return:
    """
    if layout == "auto":
        res = graph.layout_auto()
    elif layout == "circle":
        res = graph.layout_circle()
    elif layout == "drl":
        res = graph.layout_drl()
    elif layout == "fruchterman_reingold":
        res = graph.layout_fruchterman_reingold()
    elif layout == "grid_fruchterman_reingold":
        res = graph.layout_grid_fruchterman_reingold()
    elif layout == "kamada_kawai":
        res = graph.layout_kamada_kawai()
    elif layout == "lgl":
        res = graph.layout_lgl()
    elif layout == "random":
        res = graph.layout_random()
    elif layout == "random_3d":
        res = graph.layout_random_3d()
    elif layout == "reingold_tilford":
        res = graph.layout_reingold_tilford()
    elif layout == "reingold_tilford_circular":
        res = graph.layout_reingold_tilford_circular()

    return res


########################

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-n', '--node',
              required=True,
              type=click.Path(),
              help="The node file")
@click.option('-e', '--edge',
              required=True,
              type=click.Path(),
              help="The edge file")
@click.option('-l', '--layout',
              metavar="[auto | circle | drl | ...]",
              default="auto",
              type=click.Choice(LAYOUT),
              help=f"The layout to apply, you can choose from {LAYOUT}")
@click.option("--label",
              default="Id",
              show_default=True,
              help="The label column name in node file")
@click.option('-nc', '--nodecolor',
              default="red",
              show_default=True,
              help="The node color")
@click.option('-ns', '--nodeshape',
              default="circle",
              show_default=True,
              help="The node shape")
@click.option('-ec', '--edgecolor',
              default="grey",
              show_default=True,
              help="The edge color")
@click.option('-ew', '--edgewidth',
              default=0.1,
              show_default=True,
              type=float,
              help="The edge width")
@click.option('-p', '--prefix',
              default="./result",
              show_default=True,
              help="The prefix of result")
def cli(node, edge, layout, label, nodecolor, nodeshape, edgecolor, edgewidth,
        prefix):
    """
    Use igraph to plot network

    The node file first col must be Id\n
    The edge file first second col must be Source Target

    if file node have column named color, it will be regard as node color
    if file node have column named shape, it will be regard as node shape
    if file edge have column named color, it will be regard as edge color
    """
    g = igraph.Graph()
    df_node = pd.read_csv(node, sep='\t')
    df_edge = pd.read_csv(edge, sep='\t')
    logging.info("Add nodes")
    g.add_vertices(df_node["Id"])
    logging.info("Add edges")
    g.add_edges(zip(df_edge["Source"], df_edge["Target"]))
    logging.info(f"Node number {g.vcount()}")
    logging.info(f"Edge number {g.ecount()}")

    visual_style = {}
    logging.info(f"Apply layout {layout}")
    visual_style["layout"] = get_layout(g, layout)
    if "shape" in df_node.columns:
        visual_style["vertex_shape"] = df_node["shape"]
    else:
        visual_style["vertex_shape"] = nodeshape
    if "color" in df_node.columns:
        visual_style["vertex_color"] = df_node["color"]
    else:
        visual_style["vertex_color"] = nodecolor
    visual_style["vertex_frame_width"] = 0
    if label:
        visual_style["vertex_label"] = df_node[label]
    pagerank = np.array(g.pagerank())
    visual_style["vertex_label_size"] = 20 * (pagerank - min(pagerank)) / (
            max(pagerank) - min(pagerank)) + 1
    visual_style["vertex_size"] = 100 * (pagerank - min(pagerank)) / (
            max(pagerank) - min(pagerank)) + 1

    if "color" in df_edge.columns:
        visual_style["edge_color"] = df_edge["color"]
    else:
        visual_style["edge_color"] = edgecolor
    visual_style["edge_curved"] = 0.5
    visual_style["edge_width"] = edgewidth

    logging.info(f"Out put the graph")
    file_pdf = f"{prefix}.pdf"
    igraph.plot(g, file_pdf,
                bbox=(3000, 3000),
                margin=50,
                **visual_style)


if __name__ == "__main__":
    cli()
