#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-11-09 11:20:33
# @Last Modified by:   MingJia
# @Last Modified time: 2020-11-09 14:17:13
import matplotlib as mpl

mpl.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='white')
from scipy.ndimage import gaussian_filter1d

import logging
import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def smooth(data):
    res = gaussian_filter1d(data, 3)
    return res


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input plot data")
@click.option("-pos", '--positions',
              default="10,30,50",
              show_default=True,
              help="The positions for x names, html code split by ,")
@click.option('-n', '--names',
              default="upstream,genebody,downstream",
              show_default=True,
              help="The xnames, html code split by ,")
@click.option('-w', '--window',
              default="20",
              show_default=True,
              type=int,
              help="The window size for a region")
@click.option('--xlab',
              required=False,
              help="The xlab name for the plot")
@click.option('--ylab',
              required=False,
              help="The ylab name for the plot.")
@click.option('-t', '--title',
              required=False,
              help="The title for the plot.")
@click.option('-c', '--colors',
              required=False,
              help="The colors used for plot, html code split by ,")
@click.option('--size',
              required=False,
              default="6,6",
              show_default=True,
              help="The figsize of pic")
@click.option("-p", "--prefix",
              default="./res",
              show_default=True,
              help="The out put prefix")
def cli(input, positions, names, window, xlab, ylab, title, colors, size,
        prefix):
    """
    Script for plot meth level
    """
    logging.info(f"Parse the plot data {input}...")
    df = pd.read_csv(input, sep="\t")
    logging.info(f"smooth the input...")
    smooth_df = df.apply(smooth)
    col_names = df.columns

    if colors:
        colors = colors.strip().split(',')
        color_palette = {}
        for i in range(len(col_names)):
            color_palette[col_names[i]] = colors[i % len(colors)]
    else:
        color_palette = None

    logging.info("Plot...")
    figure, ax = plt.subplots(
        figsize=([float(i) for i in size.strip().split(',')]), dpi=300)

    sns.lineplot(data=smooth_df,
                 palette=color_palette,
                 linestyle='-',
                 lw=1.5,
                 markers=False,
                 sort=False,
                 ax=ax)

    for i in ax.lines:
        i.set_linestyle("-")

    for i in range(window, df.shape[0], window):
        ax.axvline(x=i, color='black', linestyle='--', linewidth=0.5)

    plt.xticks([float(i) for i in positions.strip().split(',')],
               names.strip().split(','),
               fontsize=10)

    if xlab:
        ax.set_xlabel(xlab, fontsize=15)
    if ylab:
        ax.set_ylabel(ylab, fontsize=15)
    if title:
        ax.set_title(title, fontsize=22)

    plt.legend(bbox_to_anchor=(1.05, 0.5), loc=6, borderaxespad=0.)

    ax.spines['right'].set_color("none")
    ax.spines['top'].set_color("none")

    plt.savefig(prefix + '.svg', bbox_inches='tight')
    plt.savefig(prefix + '.png', dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    cli()
