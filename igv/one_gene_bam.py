#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-04-27 11:41:45
# @Last Modified by:   MingJia
# @Last Modified time: 2020-04-27 11:41:45
import logging
import os
import subprocess

import click
from jinja2 import Template

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

#### Some Functions ####
template = Template("""
new
genome {{ info.gene }}
load  {{ info.bam }}
snapshotDirectory {{ info.dir_out }}
sort position
collapse
snapshot {{ info.prefix }}.svg
snapshot {{ info.prefix }}.png
exit
""")
########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('--gene',
              required=True,
              type=click.Path(),
              help="The gene fasta file")
@click.option('--bam',
              required=True,
              type=click.Path(),
              help="The gene's bam for(sorted)")
@click.option('--prefix',
              required=True,
              type=click.Path(),
              help="The prefix for the out put pic")
@click.option('--snapshot',
              default='snpashot',
              show_default=True,
              help=u"The snapshot out put dir")
@click.option('--batch',
              default='./batch.txt',
              show_default=True,
              help=u"The out put batch script file")
@click.option('--run/--no-run',
              default=False,
              show_default=True,
              help=u"Whether direct run the batch")
@click.option('--xvfb',
              default='/usr/bin/xvfb-run',
              show_default=True,
              help=u"The xvfb-run path")
@click.option('--java',
              default='/Bio/User/renchaobo/software/IGV/IGV_2.7.0/jdk-11',
              show_default=True,
              help=u"The JAVA_HOME path")
@click.option('--igv_dir',
              default='/Bio/User/renchaobo/software/IGV/IGV_2.7.0',
              show_default=True,
              help=u"The igv install dir")
@click.option('--mem',
              default='4g',
              show_default=True,
              help=u"The mem use for java")
def cli(gene, bam, prefix, snapshot, batch, run, xvfb, java, igv_dir, mem):
    """
    Use the gene bam file to plot the read distribution
    """
    if not os.path.exists(snapshot):
        os.makedirs(snapshot)

    info = dict()
    info['gene'] = gene
    info['bam'] = bam
    info['dir_out'] = snapshot
    info['prefix'] = prefix

    with open(batch, 'w') as OUT:
        print(template.render(info=info), file=OUT)

    if run:
        cmd = f"""JAVA_HOME={java}
PATH=$JAVA_HOME/bin:$PATH
{xvfb} -a --server-num=1 {java}/bin/java -Xmx{mem} --module-path={igv_dir}/lib @{igv_dir}/igv.args --module=org.igv/org.broad.igv.ui.Main -b {batch}
"""
        logging.info(f"Start run command ...\n{cmd}")
        subprocess.run(cmd, shell=True)
        logging.info("Finish")


if __name__ == "__main__":
    cli()
