#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-04-22 11:36:45
# @Last Modified by:   MingJia
# @Last Modified time: 2020-04-22 11:36:45
import gzip
import logging

import click
from Bio import SeqIO

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input genebank file")
@click.option('-f', '--feature',
              default="CDS",
              show_default=True,
              help="The feature to extract seq")
@click.option('-n', '--name',
              default="protein_id",
              show_default=True,
              help="The name tag for seq")
@click.option('-s', '--seq',
              default="translation",
              show_default=True,
              help="The seq tag for seq")
@click.option('-o', '--output',
              default='result.fa',
              show_default=True,
              type=click.Path(),
              help="The out put fasta file")
def cli(input, feature, name, seq, output):
    """
    Extract seq from genbank file
    """
    with open(output, 'w') as OUT:
        logging.info(f'Start to parse genbank file: {input}')
        handle = gzip.open(input, 'rt') if input.endswith('gz') else open(input,
                                                                          'r')
        for chromosome in SeqIO.parse(handle, "genbank"):
            for record in chromosome.features:
                if record.type == feature:
                    try:
                        target_name = record.qualifiers[name][0]
                        target_seq = record.qualifiers[seq][0]
                        print(f'>{target_name}\n{target_seq}', file=OUT)
                    except KeyError as e:
                        logging.warning(f'No {e} in Location {record.location}')


if __name__ == "__main__":
    cli()
