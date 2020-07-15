#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-07-15 9:59:14
# @Last Modified by:   MingJia
# @Last Modified time: 2020-07-15 9:59:14
import logging

import click
import pandas as pd
from skbio import diversity

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Diversity analysis
    """
    pass


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option("-m", "--metric",
              required=True,
              type=click.Choice(diversity.get_alpha_diversity_metrics(),
                                case_sensitive=False),
              metavar=f'[ace | chao1 | ...]',
              multiple=True,
              help=f"""Alpha-diversity metric(s) to use, you can choose from
                       {diversity.get_alpha_diversity_metrics()}""")
@click.option('-o', '--out',
              default="./result.txt",
              show_default=True,
              type=click.Path(),
              help="The out put result")
def alpha(input, metric, out):
    """
    Alpah diversity analysis
    """
    df = pd.read_csv(input, index_col=0, sep='\t')
    samples = df.columns
    res = {}
    for i in metric:
        logging.info(f"{i} analysis ...")
        res[i] = list(diversity.alpha_diversity(i, df.T))
    res_df = pd.DataFrame(res, index=samples)
    logging.info(f"Save result to {out}")
    res_df.to_csv(out, sep='\t', index_label="Sample")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option("-m", "--metric",
              required=True,
              type=click.Choice(diversity.get_beta_diversity_metrics(),
                                case_sensitive=False),
              multiple=True,
              help=f"""Beta-diversity metric(s) to use""")
@click.option('-o', '--out',
              default="./result.txt",
              show_default=True,
              type=click.Path(),
              help="The out put result")
def beta(input, metric, out):
    """
    Beta diversity analysis
    """
    pass


cli.add_command(alpha)
cli.add_command(beta)

if __name__ == "__main__":
    cli()
