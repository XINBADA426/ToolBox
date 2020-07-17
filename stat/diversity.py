#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-07-15 9:59:14
# @Last Modified by:   MingJia
# @Last Modified time: 2020-07-15 9:59:14

# TODO
# - support for unweighted_unifrac
# - support for weighted_unifrac

import logging
import sys

import click
import pandas as pd
from skbio import diversity

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

metric_alpha = diversity.get_alpha_diversity_metrics()
metric_beta = ["braycurtis", "canberra", "chebyshev", "cityblock",
               "correlation", "cosine", "dice", "euclidean", "hamming",
               "jaccard", "jensenshannon", "kulsinski", "mahalanobis",
               "matching", "minkowski", "rogerstanimoto", "russellrao",
               "seuclidean", "sokalmichener", "sokalsneath", "sqeuclidean",
               "yule", "unweighted_unifrac", "weighted_unifrac"]

########################

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(
    context_settings=CONTEXT_SETTINGS)
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
                       {metric_alpha}""")
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
              metavar=f'[ braycurtis | jaccard | ...]',
              type=click.Choice(metric_beta,
                                case_sensitive=False),
              multiple=True,
              help=f"""Beta-diversity metric(s) to use, you can choose from
                        {metric_beta}""")
@click.option('-p', '--prefix',
              default="./result",
              show_default=True,
              help="The out put prefix")
def beta(input, metric, prefix):
    """
    Beta diversity analysis
    """
    df = pd.read_csv(input, index_col=0, sep='\t')
    samples = df.columns
    for i in metric:
        logging.info(f"{i} analysis ...")
        if i == "unweighted_unifrac" or i == "weighted_unifrac":
            logging.error(f"Don't support {i} now, Stop here")
            sys.exit(1)
        else:
            res = diversity.beta_diversity(i, df.T)
        df_out = pd.DataFrame(res.data, index=samples, columns=samples)
        file_out = f"{prefix}.{i}.tsv"
        logging.info(f"Save {i} result to {file_out}")
        df_out.to_csv(file_out, sep='\t')


cli.add_command(alpha)
cli.add_command(beta)

if __name__ == "__main__":
    cli()
