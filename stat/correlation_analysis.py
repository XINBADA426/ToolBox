#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-06-02 11:44:03
# @Last Modified by:   MingJia
# @Last Modified time: 2020-06-02 15:04:41
import itertools
import logging

import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def parse_file(file_name):
    """
    Parse the table
    """
    header = None
    res = {}
    logging.info(f"Parse {file_name}...")
    with open(file_name, 'r') as IN:
        header = next(IN).strip().split('\t')[1:]
        for line in IN:
            row = line.strip().split('\t')
            name = row[0]
            res[name] = [float(i) for i in row[1:]]
    return res, header


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-t1', '--table1',
              required=True,
              type=click.Path(),
              help="The first table")
@click.option('-l1', '--label1',
              required=True,
              help="The first label")
@click.option('-t2', '--table2',
              required=True,
              type=click.Path(),
              help="The second table")
@click.option('-l2', '--label2',
              required=True,
              help="The second label")
@click.option('-o', '--out',
              default="result.txt",
              show_default=True,
              type=click.Path(),
              help="The out put result")
@click.option('--method',
              type=click.Choice(['pearson', 'spearman']),
              default="pearson",
              show_default=True,
              help="The correlation type")
def cli(table1, label1, table2, label2, out, method):
    """
    Correlation analysis for two table
    """
    table1_exp, table1_header = parse_file(table1)
    table2_exp, table2_header = parse_file(table2)

    if method == "pearson":
        from scipy.stats import pearsonr
        func_cor = pearsonr
    elif method == "spearman":
        from scipy.stats import spearmanr
        func_cor = spearmanr
    else:
        logging.error("WRONG METHOD")

    logging.info(f"{method} correlation analysis...")
    with open(out, 'w') as OUT:
        print(*[label1, *[f'{i}({label1})' for i in table1_header]],
              sep='\t', end='\t', file=OUT)
        print(*[label2, *[f'{i}({label2})' for i in table1_header]],
              sep='\t', end='\t', file=OUT)
        print(*['r', 'p'], sep='\t', file=OUT)

        for id1, id2 in itertools.product(table1_exp.keys(), table2_exp.keys()):
            print(*([id1] + table1_exp[id1]), sep='\t', end='\t', file=OUT)
            print(*([id2] + table2_exp[id2]), sep='\t', end='\t', file=OUT)
            print(*func_cor(table1_exp[id1],
                            table2_exp[id2]), sep='\t', file=OUT)


if __name__ == "__main__":
    cli()
