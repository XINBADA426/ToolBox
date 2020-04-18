#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-03-23 12:28:38
# @Last Modified by:   Ming
# @Last Modified time: 2020-03-23 13:18:36
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
@click.option('-f', '--fastq',
              required=True,
              type=click.Path(),
              help="The fastq input")
@click.option('-o', '--out',
              required=True,
              type=click.Path(),
              help="The out put fastq gz file")
def cli(fastq, out):
    """
    Rename the input fastq.gz file's id

    As the id in fq1 and fq2 file download from sra sometime,
    This script is to rename the fq's id to numbers so both
    id's are same
    """
    number = 1
    with gzip.open(out, 'wt') as OUT:
        logging.info(f'Start to parse {fastq}')
        for record in SeqIO.parse(gzip.open(fastq, 'rt'), 'fastq'):
            record.id = str(number)
            SeqIO.write(record, OUT, 'fastq')
            number += 1
    logging.info('Finish rename the fq id')


if __name__ == "__main__":
    cli()
