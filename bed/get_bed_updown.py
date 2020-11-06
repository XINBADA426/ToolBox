#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-11-06 10:25:06
# @Last Modified by:   MingJia
# @Last Modified time: 2020-11-06 11:24:51
import logging
import os

import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def parse_length(file_length):
    """
    Parse the genome length info
    """

    res = {}
    with open(file_length, 'r') as IN:
        for line in IN:
            arr = line.strip().split("\t")
            res[arr[0]] = int(arr[1])
    return res


def get_pos_info(info_arr, info_length, window, pos="UP"):
    """
    Get the UP/DOWN bed info
    """
    length_chommosome = info_length[info_arr[0]]

    res = []
    res = ['NA'] * 6
    start = int(info_arr[1])
    end = int(info_arr[2])
    strand = info_arr[5]

    res[0] = info_arr[0]
    res[3:] = info_arr[3:]
    if pos == "UP":
        res[1] = max(start - window,
                     0) if strand == '+' else min(end, length_chommosome - 1)
        res[2] = max(start, 0) if strand == '+' else min(end +
                                                         window,
                                                         length_chommosome)
    elif pos == 'DOWN':
        res[1] = min(end, length_chommosome -
                     1) if strand == '+' else max(start - window, 0)
        res[2] = min(
            end + window, length_chommosome) if strand == '+' else max(start, 0)
    else:
        raise TypeError

    if res[1] < res[2]:
        return res
    else:
        return False

    return res


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('--bed',
              required=True,
              type=click.Path(),
              help="The input 6 column bed file")
@click.option('--length',
              required=True,
              type=click.Path(),
              help="The genome length file")
@click.option('--window',
              default=2000,
              show_default=True,
              type=int,
              help="The up down window size")
@click.option("-o", "--out",
              default="./",
              type=click.Path(),
              help="The out put dir")
def cli(bed, length, window, out):
    """
    Get the UP DOWN bed file from the input bed file
    """
    logging.info(f"Parse the length file {length}...")
    info_length = parse_length(length)
    logging.info(f"Parse the bed file {bed}...")
    info_up = []
    info_down = []
    with open(bed, 'r') as IN:
        for line in IN:
            arr = line.strip().split("\t")
            arr_up = get_pos_info(arr, info_length, window, pos="UP")
            arr_down = get_pos_info(arr, info_length, window, pos="DOWN")
            if arr_up:
                info_up.append(arr_up)
            if arr_down:
                info_down.append(arr_down)
    logging.info(f"Out put the result to {out}...")
    with open(os.path.join(out, f"UP{window}.bed"), 'w') as OUT:
        for i in info_up:
            print(*i, sep="\t", file=OUT)
    with open(os.path.join(out, f"DOWN{window}.bed"), 'w') as OUT:
        for i in info_down:
            print(*i, sep="\t", file=OUT)


if __name__ == "__main__":
    cli()
