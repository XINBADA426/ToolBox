#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-11-06 22:55:02
# @Last Modified by:   Ming
# @Last Modified time: 2020-11-07 00:01:59
import logging

import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def index_judge(arr_overlap, bin_number):
    """
    """
    feature_a_length = int(arr_overlap[2]) - int(arr_overlap[1])
    strand = arr_overlap[5]
    window_size = feature_a_length / bin_number

    feature_a_start = int(arr_overlap[1])
    feature_b_start = int(arr_overlap[7])
    feature_a_end = int(arr_overlap[2])
    feature_b_end = int(arr_overlap[8])

    if strand == "+":
        index = (feature_b_start - feature_a_start) / window_size
    else:
        index = (feature_a_end - feature_b_end) / window_size

    index = min(round(index), bin_number - 1)
    return index


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option("--overlap",
              required=True,
              type=click.Path(),
              help="The overlap file")
@click.option("--number",
              default=40,
              show_default=True,
              type=int,
              help="The bin number for the feature")
@click.option("-o", "--out",
              required=True,
              type=click.Path(),
              help="The out put file name ")
def cli(overlap, number, out):
    """
    Get the bin info for feature

    overlap 为6列 bed 文件的 intersect wo 结果，
    对每个 col4 的 feature，将其分为 number 个 bin，
    获取每个 bin 内包含的 col10 的 feature
    详见 example.overlap
    """
    res = [set() for i in range(number)]
    logging.info(f"Parse the overlap file {overlap}...")
    with open(overlap, 'r') as IN:
        for line in IN:
            arr = line.strip().split("\t")
            if int(arr[1]) > int(arr[7]) or int(arr[2]) < int(arr[8]):
                pass
            else:
                index = index_judge(arr, number)
                res[index].add(arr[9])

    logging.info(f"Out put the result to file {out}...")
    with open(out, 'w') as OUT:
        for i in range(number):
            print(*[i, ';'.join(res[i])], sep="\t", file=OUT)


if __name__ == "__main__":
    cli()
