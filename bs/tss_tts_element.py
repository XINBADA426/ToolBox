#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-11-28 15:20:33
# @Last Modified by:   MingJia
# @Last Modified time: 2020-11-28 15:20:33
import logging

import click

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

#### Some Functions ####

########################
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option("--overlap",
              required=True,
              type=click.Path(),
              help="The overlap file")
@click.option("--size",
              default=50,
              show_default=True,
              type=int,
              help="The default bin size")
@click.option("--number",
              default="40,20,20,40",
              show_default=True,
              help="The tss_up tss_down tts_up tts_down bin number")
@click.option("-p", "--prefix",
              default="./res",
              required=True,
              help="The out put prefix")
def cli(overlap, size, number, prefix):
    """
    Get the tss and tts up down element
    """
    number = [int(i) for i in number]
    tss_up = [set() for i in range(number[0])]
    tss_up_dis = size * number[0]
    tss_down = [set() for i in range(number[1])]
    tss_down_dis = size * number[1]
    tts_up = [set() for i in range(number[2])]
    tts_up_dis = size * number[2]
    tts_down = [set() for i in range(number[3])]
    tts_down_dis = size * number[3]
    logging.info(f"Parse the overlap file {overlap}...")
    with open(overlap, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            strand = arr[5]

            feature_a_start = int(arr[1])
            feature_b_start = int(arr[7])
            feature_a_end = int(arr[2])
            feature_b_end = int(arr[8])

            if strand == "+":
                if feature_b_start < feature_a_start:
                    dis = feature_a_start + 1 - feature_b_start
                    if dis < tss_up_dis:
                        index = number[0] - dis // size - 1
                        tss_up[index].add(arr[9])
                if feature_b_start >= feature_a_start:
                    dis = feature_b_start + 1 - feature_a_start
                    if dis < tss_down_dis:
                        index = dis // size
                        tss_down[index].add(arr[9])
                if feature_b_start < feature_a_end:
                    dis = feature_a_end - feature_a_start
                    if dis < tts_up_dis:
                        index = dis // size
                        tts_up[index].add(arr[9])
                if feature_b_start > feature_a_end:
                    dis = (feature_b_start + 1) - (feature_a_end - 1)
                    if dis < tts_down_dis:
                        index = dis // size
                        tts_down[index].add(arr[9])
            elif strand == "-":
                if feature_b_end > feature_a_end:
                    dis = feature_b_end - feature_a_end + 1
                    if dis < tss_up_dis:
                        index = number[0] - dis // size - 1
                        tss_up[index].add(arr[9])
                if feature_b_end < feature_a_end:
                    dis = feature_a_end - feature_b_end + 1
                    if dis < tss_down_dis:
                        index = dis // size
                        tss_down[index].add(arr[9])
                if feature_b_end > feature_a_start:
                    dis = feature_b_end - feature_a_start
                    if dis < tts_up_dis:
                        index = number[2] - dis // size - 1
                        tts_up[index].add(arr[9])
                if feature_b_end < feature_a_start:
                    dis = (feature_a_start + 1) - (feature_b_end - 1)
                    if dis < tts_down_dis:
                        index = number[3] - dis // size - 1
                        tts_down[index].add(arr[9])


if __name__ == "__main__":
    cli()
