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
@click.option('-p', '--prefix',
              default="./result",
              show_default=True,
              help="The prefix of result")
def cli(node, edge, prefix):
    """
    Use igraph to plot network

    The node file first col must be Id\n
    The edge file first second col must be Source Target

    TODO
    1. 添加布局方式
    2. 添加颜色支持
    3. 添加多种形状支持
    """
    g = igraph.Graph()
    df_node = pd.read_csv(node, sep='\t')
    df_edge = pd.read_csv(edge, sep='\t')
    logging.info(f"Add nodes")
    g.add_vertices(df_node["Id"])
    logging.info(f"Add edges")
    g.add_edges(zip(df_edge["Source"], df_edge["Target"]))

    visual_style = {}
    # visual_style["layout"] = g.layout_auto()
    visual_style["layout"] = g.layout("fr")
    visual_style["vertex_color"] = "#779988"
    visual_style["vertex_frame_width"] = 0
    visual_style["vertex_label"] = df_node["Symbol"]
    pagerank = np.array(g.pagerank())
    visual_style["vertex_label_size"] = 20 * (pagerank - min(pagerank)) / (
            max(pagerank) - min(pagerank)) + 1
    visual_style["vertex_size"] = 50 * (pagerank - min(pagerank)) / (
            max(pagerank) - min(pagerank)) + 1

    visual_style["edge_color"] = "#99aabb"
    visual_style["edge_curved"] = 0.5
    visual_style["edge_width"] = 0.1

    logging.info(f"Out put the graph")
    file_pdf = f"{prefix}.pdf"
    igraph.plot(g, file_pdf,
                bbox=(600, 600),
                margin=10,
                **visual_style)


if __name__ == "__main__":
    cli()
