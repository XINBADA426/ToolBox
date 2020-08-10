#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-08-06 13:26:32
# @Last Modified by:   MingJia
# @Last Modified time: 2020-08-06 13:26:32
import logging

import click
import pandas as pd

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Interconversion  between LongTable and  WideTable
    """
    pass


@click.command()
@click.option('-t', '--table',
              type=click.Path(),
              required=True,
              help='The input table')
@click.option('--index',
              required=True,
              help='The index column name')
@click.option('--column',
              required=True,
              help='The column name used to generate new column names')
@click.option('--value',
              required=True,
              help='The column name used to generate new table values')
@click.option('-o', '--out',
              default="wide.tsv",
              show_default=True,
              help='The out put file name')
def l2w(table, index, column, value, out):
    """
    Long form table to wide form table
    """
    logging.info(f"Parse the input table {table}...")
    df = pd.read_csv(table, sep='\t')
    logging.info('Formating...')
    res = df.pivot(index=index,
                   columns=column,
                   values=value)
    logging.info(f"Output to {out}...")
    res.to_csv(out, sep='\t', index=True)


@click.command()
@click.option('-t', '--table',
              type=click.Path(),
              required=True,
              help='The input table')
@click.option('--ids',
              required=True,
              help='The column name(s) as ID, sep by ,')
@click.option('--values',
              help='The column name(s) you want to format, sep by ,')
@click.option('--var_name',
              default="variable",
              show_default=True,
              help='The column name of variable after format')
@click.option('--val_name',
              default="value",
              show_default=True,
              help='The column name of value after format')
@click.option('-o', '--out',
              default="long.tsv",
              show_default=True,
              help='The out put file name')
def w2l(table, ids, values, var_name, val_name, out):
    """
    Wide form table to Long form table
    """
    logging.info(f"Parse the input table {table}...")
    df = pd.read_csv(table, sep='\t')
    id_columns = ids.strip().split(',')
    val_columns = values.strip().split(',') if values else None
    logging.info('Formating...')
    if val_columns:
        res = df.melt(id_vars=id_columns,
                      value_vars=val_columns,
                      var_name=var_name,
                      value_name=val_name)
    else:
        res = df.melt(id_vars=id_columns,
                      var_name=var_name,
                      value_name=val_name)
    logging.info(f"Output to {out}...")
    res.to_csv(out, sep='\t', index=False)


cli.add_command(w2l)
cli.add_command(l2w)

if __name__ == "__main__":
    cli()
