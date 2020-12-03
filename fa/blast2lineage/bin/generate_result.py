#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-12-03 14:47:27
# @Last Modified by:   MingJia
# @Last Modified time: 2020-12-03 14:47:27
import logging

import click

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The acc2taxon result file")
@click.option('--lineage',
              required=True,
              type=click.Path(),
              help="The taxon to lineage info")
@click.option("-o", '--output',
              default="./result.tsv",
              show_default=True,
              type=click.Path(),
              help="The out put file")
def cli(input, lineage, output):
    """
    Get the final table
    """
    logging.info(f"Parse the lineage info {lineage}")
    info = {}
    with open(lineage, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            info[arr[0]] = arr[1]
    logging.info(f"Parse the file {input}")
    with open(input, 'r') as IN, open(output, 'w') as OUT:
        h = ["ID", "Kingdom", "Phylum", "Class", "Order", "Family", "Genus",
             "Species"]
        print(*h, sep='\t', file=OUT)
        for line in IN:
            arr = line.strip().split('\t')
            name = arr[0]
            t = info[arr[2]].split(';')
            res = [name, *t]
            print(*res, sep='\t', file=OUT)


if __name__ == "__main__":
    cli()
