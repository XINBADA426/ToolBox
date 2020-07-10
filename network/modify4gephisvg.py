#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2019-03-29 15:23:04
# @Last Modified by:   Ming
# @Last Modified time: 2019-03-29 21:13:08
import argparse
import logging

from bs4 import BeautifulSoup
from bs4 import Tag

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


# 妈蛋，忘了装饰器怎么用了
def parse_node(file_name):
    res = {}
    with open(file_name, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            name = 'id_{}'.format(arr[0].replace(' ', '_'))
            res[name] = arr[1]
    return res


def parse_edge(file_name):
    res = {}
    with open(file_name, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            name1 = 'id_{}'.format(arr[0].replace(' ', '_'))
            name2 = 'id_{}'.format(arr[1].replace(' ', '_'))
            res[tuple(sorted([name1, name2]))] = arr[2]
    return res


def node_color(soup, file_node_color):
    """
    """
    info_node_color = parse_node(file_node_color)
    for node in soup.find('g', attrs={'id': 'nodes'}).children:
        if isinstance(node, Tag):
            if node['class'] in info_node_color:
                node['fill'] = info_node_color[node['class']]


def node_shape(soup, file_node_shape):
    """
    遍历nodes节点，将指定的节点从圆形替换为特定图形
    """

    def circle_polygon(x, y, r, n):
        """
        only support 3,4now
        """
        x = float(x)
        y = float(y)
        r = float(r)
        n = int(n)

        res = None
        if n == 3:
            p1 = ','.join(map(str, [x, y + r]))
            p2 = ','.join(map(str, [x + 0.87 * r, y - r / 2]))
            p3 = ','.join(map(str, [x - 0.87 * r, y - r / 2]))
            res = ' '.join([p1, p2, p3])
        elif n == 4:
            p1 = ','.join(map(str, [x - 0.71 * r, y + 0.71 * r]))
            p2 = ','.join(map(str, [x + 0.71 * r, y + 0.71 * r]))
            p3 = ','.join(map(str, [x + 0.71 * r, y - 0.71 * r]))
            p4 = ','.join(map(str, [x - 0.71 * r, y - 0.71 * r]))
            res = ' '.join([p1, p2, p3, p4])
        else:
            pass

        return res

    info_node_shape = parse_node(file_node_shape)
    for node in soup.find('g', attrs={'id': 'nodes'}).children:
        if isinstance(node, Tag):
            if node['class'] in info_node_shape:
                # change the info
                node.name = 'polygon'
                node['points'] = circle_polygon(node['cx'], node['cy'], node[
                    'r'], info_node_shape[node['class']])
                del node['cx']
                del node['cy']
                del node['r']


def edge_color(soup, file_edge_color):
    """
    """
    info_edge_color = parse_edge(file_edge_color)
    for edge in soup.find('g', attrs={'id': 'edges'}).children:
        if isinstance(edge, Tag):
            if tuple(sorted(edge['class'])) in info_edge_color:
                edge['stroke'] = info_edge_color[tuple(sorted(edge['class']))]


def edge_width(soup, file_edge_width):
    """
    """
    info_edge_width = parse_edge(file_edge_width)
    info_edge_scale = {}
    mean = sum(map(float, info_edge_width.values())) / len(info_edge_width)
    for key, value in info_edge_width.iteritems():
        # info_edge_scale[key] = max(float(value) / mean * SCALE, 1.5)
        info_edge_scale[key] = max((float(value) - mean) / mean * SCALE, 1)
    for edge in soup.find('g', attrs={'id': 'edges'}).children:
        if isinstance(edge, Tag):
            if tuple(sorted(
                    edge['class'].strip().split(' '))) in info_edge_width:
                edge['stroke-width'] = float(edge['stroke-width']) * \
                                       float(info_edge_scale[
                                                 tuple(sorted(edge[
                                                     'class'].strip().split(
                                                     ' ')))])


def main(args):
    """
    """
    logging.info(f"Parse the input {args.file_in}...")
    soup = BeautifulSoup(open(args.file_in), 'xml')

    if args.file_node_color:
        logging.info(f"Change the node color...")
        node_color(soup, args.file_node_color)
    if args.file_node_shape:
        logging.info(f"Change the node shape...")
        node_shape(soup, args.file_node_shape)
    if args.file_edge_color:
        logging.info(f"Change the edge color...")
        edge_color(soup, args.file_edge_color)
    if args.file_edge_width:
        logging.info(f"Change the edge width...")
        edge_width(soup, args.file_edge_width)

    logging.info(f"Output the result to file {args.file_out}")
    with open(args.file_out, 'w') as OUT:
        print(soup.prettify(), file=OUT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u"Modify the Gephi svg.")
    parser.add_argument("-i", "--file_in", required=True,
                        help=u"The Gephi svg result you  want to modify.")
    parser.add_argument("-ns", "--file_node_shape",
                        help=u"The file contain the nodes to change shape.")
    parser.add_argument("-nc", "--file_node_color",
                        help=u"The file contain the nodes to change color.")
    parser.add_argument("-ec", "--file_edge_color",
                        help=u"The file contain the edges to change color.")
    parser.add_argument("-ew", "--file_edge_width",
                        help=u"The file contain the edges to change width.")
    parser.add_argument("-s", "--edge_width_scale", type=float,
                        default=100, help=u"The edge width scale.")
    parser.add_argument("-o", "--file_out",
                        default='result.svg', help=u"The out put file name.")
    args = parser.parse_args()
    SCALE = args.edge_width_scale
    main(args)
