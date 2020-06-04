#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-06-03 15:15:00
# @Last Modified by:   MingJia
# @Last Modified time: 2020-06-03 16:51:41
import gzip
import logging

import click
from Bio import SeqIO

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'

########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-r', '--rawdata',
              required=True,
              type=click.Path(),
              help="The original fq to deal with")
@click.option('-f', '--filterdata',
              required=True,
              type=click.Path(),
              help="The filtered fq to deal with")
@click.option('-n', '--number',
              type=int,
              help="The number of reads you want to remove")
@click.option('-o', '--out',
              required=True,
              type=click.Path(),
              help="The out put fq")
def cli(rawdata, filterdata, number, out):
    """
    Remove fq from the original data by filtered data.

    If you assign the remove number, it will remove the
    target number of reads from original data

    The fq files must gz file
    """
    logging.info('Start...')
    with gzip.open(out, 'wt') as OUT:
        filter_records = SeqIO.parse(gzip.open(filterdata, 'rt'), 'fastq')
        filter_record_name = next(filter_records).name

        if number:
            for ori_record in SeqIO.parse(gzip.open(rawdata, 'rt'), 'fastq'):
                ori_record_name = ori_record.name
                if number > 0:
                    if ori_record_name == filter_record_name:
                        SeqIO.write(ori_record, OUT, 'fastq')
                        try:
                            filter_record_name = next(filter_records).name
                        except StopIteration:
                            logging.info(f'Finish Read {filterdata}')
                            number = 0
                    else:
                        number -= 1
                else:
                    SeqIO.write(ori_record, OUT, 'fastq')

        else:
            for ori_record in SeqIO.parse(gzip.open(rawdata, 'rt'), 'fastq'):
                ori_record_name = ori_record.name
                if ori_record_name == filter_record_name:
                    SeqIO.write(ori_record, OUT, 'fastq')
                    try:
                        filter_record_name = next(filter_records).name
                    except StopIteration:
                        logging.info(f'Finish Read {filterdata}')
                        break

    logging.info('Finish')


if __name__ == "__main__":
    cli()
