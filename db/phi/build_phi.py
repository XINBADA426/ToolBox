#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-06-04 10:16:47
# @Last Modified by:   MingJia
# @Last Modified time: 2020-06-04 10:16:47
import logging
import os
import subprocess

import click
from Bio import SeqIO

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-f', '--fasta',
              required=True,
              type=click.Path(),
              help="The input fasta file of PHI")
@click.option('-o', '--out',
              default="./",
              show_default=True,
              type=click.Path(),
              help="The out put dir")
@click.option('--diamond',
              default="/Bio/Linux-src-files/NGS/Align/diamond/with_intelcompiler/diamond-0.9.24/diamond",
              show_default=True,
              help="The diamond software to build database")
@click.option('-p', '--threads',
              default=4,
              show_default=True,
              type=int,
              help="Number of CPU threads")
def cli(fasta, out, diamond, threads):
    """
    Script to build PHI database
    """
    logging.info(f"Start to parse {fasta}...")
    out_faa = os.path.join(out, "PHI.faa")
    with open(out_faa, 'w') as OUT1:
        for record in SeqIO.parse(fasta, 'fasta'):
            arr = record.name.strip().split('#')
            print(f">{arr[0]}\n{record.seq}", file=OUT1)
    logging.info(f"Build the diamond database...")
    out_pre = os.path.join(out, "PHI")
    cmd = f"{diamond} makedb --in {out_faa} --db {out_pre} -p {threads}"
    logging.info(cmd)
    subprocess.run(cmd, shell=True)
    logging.info(f"Finish")


if __name__ == "__main__":
    cli()
