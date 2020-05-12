#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-05-12 09:50:46
# @Last Modified by:   MingJia
# @Last Modified time: 2020-05-12 10:14:26
import logging

import click
import pandas as pd

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def parse_group(file_name):
    """
    """
    res = {}
    with open(file_name, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            res.setdefault(arr[1], [])
            res[arr[1]].append(arr[0])
    return res


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-t', '--table',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option('-g', '--group',
              required=True,
              type=click.Path(),
              help="The group info file")
@click.option('-o', '--out',
              default="res.txt",
              show_default=True,
              help="The out put file")
def cli(table, group, out):
    """
    Calculate the mean value of group that list in
    the group file

    The group file has no header, sample name as
    first column and group name as second column.
    Samples that not in the group file will be
    discard
    """
    logging.info(f'Parse the file {table}...')
    df = pd.read_csv(table, sep='\t', index_col=0)
    logging.info(f'Parse the group info file {group}...')
    group_info = parse_group(group)

    logging.info('Calculate the mean...')
    for key, value in group_info.items():
        df[key] = df[value].mean(axis=1)

    df[group_info.keys()].to_csv(out, sep='\t')


if __name__ == "__main__":
    cli()
