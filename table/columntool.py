#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2019-12-24 09:47:58
# @Last Modified by:   Ming
# @Last Modified time: 2020-01-11 09:55:22
import logging

import click

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


#### Some Functions ####
def parse_table(file_name):
    """
    Parse the map file(two columns)
    """
    res = {}
    with open(file_name, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            res[arr[0]] = arr[1]
    return res


def parse_list(file_name):
    """
    Parse the list file(one column)
    """
    res = []
    with open(file_name, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            res.append(arr[0])
    return res


########################

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Tools for deal with table by columns

    """
    pass


@click.command()
@click.option('-t', '--table',
              type=click.Path(),
              required=True,
              help='The input table')
@click.option('-m', '--map_file',
              type=click.Path(),
              required=True,
              help="The list contain the source and target name, sep by '\\t'")
@click.option('--keep/--no-keep',
              default=True,
              show_default=True,
              help='Whether keep the column not list in the map file')
@click.option('-o', '--out',
              required=True,
              help='The out put file name')
def rename(table, map_file, keep, out):
    """
    Rename the table column that offered in the map file,
    the order of column will be the original order in the
    table.
    """
    logging.info(f"Parse the map file {map_file}")
    map_info = parse_table(map_file)
    logging.info(f"Deal with the file {table}")
    with open(table, 'r') as IN, open(out, 'w') as OUT:
        header = next(IN).strip().split('\t')
        if keep:
            new_header = []
            for i in header:
                if i in map_info:
                    new_header.append(map_info[i])
                else:
                    new_header.append(i)
            print(*new_header, sep='\t', file=OUT)
            for line in IN:
                print(line.strip(), file=OUT)
        else:
            new_header = []
            order_list = []
            for i in range(len(header)):
                if header[i] in map_info:
                    new_header.append(map_info[header[i]])
                    order_list.append(i)
            print(*new_header, sep='\t', file=OUT)
            for line in IN:
                arr = line.strip().split('\t')
                new_arr = [arr[i] for i in order_list]
                print(*new_arr, sep='\t', file=OUT)


@click.command()
@click.option('-t', '--table',
              type=click.Path(),
              required=True,
              help='The input table')
@click.option('-l', '--list_file',
              type=click.Path(),
              required=True,
              help="The column order file, first column are the column name")
@click.option('-o', '--out',
              required=True,
              help='The out put file name')
def reorder(table, list_file, out):
    """
    Order the input table column by offered list file,
    columns not list in the list file will be abandoned
    """
    order_info = parse_list(list_file)
    column_order = []
    with open(table, 'r') as IN, open(out, 'w') as OUT:
        header = next(IN).strip().split('\t')
        for i in order_info:
            column_order.append(header.index(i))
        new_header = [header[index] for index in column_order]
        print(*new_header, sep='\t', file=OUT)
        for line in IN:
            arr = line.strip().split('\t')
            new_arr = [arr[index] for index in column_order]
            print(*new_arr, sep='\t', file=OUT)


cli.add_command(rename)
cli.add_command(reorder)

if __name__ == "__main__":
    cli()
