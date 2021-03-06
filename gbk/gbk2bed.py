#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-03-25 16:07:43
# @Last Modified by:   MingJia
# @Last Modified time: 2020-03-25 16:26:02
import gzip
import logging

import click
from Bio import SeqIO

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input genebank file")
@click.option('-f', '--feature',
              required=True,
              help="The feature you want to extract")
@click.option('--name_tag',
              required=True,
              help="The name tag you want to as the feature name")
@click.option('-o', '--output',
              default='result.bed',
              show_default=True,
              type=click.Path(),
              help="The out put bed file")
def cli(input, feature, name_tag, output):
    """
    Extract your target feature from genbank file and convert them
    to bed format

    """
    with open(output, 'w') as OUT:
        logging.info(f'Start to parse genbank file: {input}')
        handle = gzip.open(input, 'rt') if input.endswith('gz') else open(input, 'r')
        for chromosome in SeqIO.parse(handle, "genbank"):
            for record in chromosome.features:
                if record.type == feature:
                    start = record.location.start.position
                    end = record.location.end.position
                    if name_tag in record.qualifiers:
                        name = record.qualifiers[name_tag][0]
                    else:
                        name = '*'
                    strand = '-' if record.strand < 0 else '+'
                    print(*[chromosome.name, start, end, name,
                            0, strand], sep='\t', file=OUT)


if __name__ == "__main__":
    cli()
