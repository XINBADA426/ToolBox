#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2018-03-15 11:19:15
# @Last Modified by:   Ming
# @Last Modified time: 2018-03-15 12:53:57
import logging

import click
from Bio import Seq
from Bio import SeqIO

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def pick_longest(seq_list):
    """
    """
    res = seq_list[0]
    for i in seq_list[1:]:
        if len(i) > len(res):
            res = i

    return res


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-f', '--fasta',
              required=True,
              help="The input cds fasta file")
@click.option('--table',
              default=1,
              show_default=True,
              type=int,
              help="The codon table to use")
@click.option('-o', '--output',
              default='result.faa',
              show_default=True,
              type=click.Path(),
              help="The out put protein file")
def cli(fasta, table, output):
    """
    Get the longest ORF of the fasta sequence
    """
    with open(output, 'w') as OUT:
        logging.info('Program Start...')
        for sequence in SeqIO.parse(fasta, "fasta"):
            ORFs = [Seq.translate(sequence.seq[i:], table=table,
                                  stop_symbol='*', to_stop=False, cds=False) for i in range(3)]
            ORFs_cut = []
            for i in ORFs:
                ORFs_cut.extend(i.split('*'))
            if len(ORFs_cut) > 0:
                res = pick_longest(ORFs_cut)
                print(">" + sequence.id, file=OUT)
                print(res, file=OUT)
            else:
                logging.warning(f'No CDS find for {sequence.id}')


if __name__ == "__main__":
    cli()
