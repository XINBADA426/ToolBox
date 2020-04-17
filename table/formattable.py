#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-04-17 14:15:17
# @Last Modified by:   MingJia
# @Last Modified time: 2020-04-17 14:15:17
import logging
import re

import click
from prettytable import PrettyTable

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.argument('input',
                type=click.File('r'))
@click.option('-s', '--sep',
              default='\t',
              # show_default=True,
              help="The separator of input content [default: \\t]")
def cli(input, sep):
    """
    Print the input table in a pretty format

    It's juest uesd for show small piece of content,
    the max row number is 1000

    """
    res = PrettyTable()
    i = 0
    while True and i <= 1000:
        line = input.readline()
        if line:
            arr = re.split(sep, line.strip())
            if i == 0:
                res.field_names = arr
            else:
                res.add_row(arr)
        i += 1
    res.align = 'l'
    print(res)


if __name__ == "__main__":
    cli()
