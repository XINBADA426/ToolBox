#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-11-26 21:46:15
# @Last Modified by:   Ming
# @Last Modified time: 2020-11-26 21:46:15
import logging
import os
from subprocess import run

import click

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


#### Some Functions ####
def blast(query_file, subject_file, blast_type, dir_out):
    """
    Blast between two fasta file.
    """
    db = os.path.join(dir_out, os.path.basename(subject_file))
    if not os.path.exists(db):
        mkdb = f'{DIAMOND} makedb --in {subject_file} --db {db}'
        run(mkdb, shell=True)
    base_query = os.path.basename(query_file)
    base_subject = os.path.basename(subject_file)
    file_out = os.path.join(dir_out, f'{base_query}_{base_subject}.out')
    command = f'{DIAMOND} {blast_type} -p 4 -q {query_file} -d {db} -e 1e-5 -f 6 -o {file_out}'
    run(command, shell=True)
    return file_out


def parse_blast(file_in):
    res = {}
    with open(file_in, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            if arr[0] not in res:
                res[arr[0]] = arr[1]
    return res


########################

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-q', '--query',
              required=True,
              help='The query fasta file input.')
@click.option('-s', '--subject',
              required=True,
              help='The subject fasta file input.')
@click.option('-o', '--dir_out',
              default='./blast',
              show_default=True,
              help='The out put dir.[default ./blast]')
@click.option('-t', '--blast_type',
              type=click.Choice(["blastp"]),
              default='blastp',
              show_default=True,
              help='The progroam used for blast')
def bothwayblast(query, subject, dir_out, blast_type):
    """
    A tool for both way blast.

    This tool will use the query sequence to blast the subject sequence and
    the subject sequence to blast the query sequence, if one sequence A in
    the query's best match is the sequence B in the subject and the sequence
    B in the subject's best match is the sequence A in the query, Then we
    will regard them as the same sequence.

    TODO:
    - add nucl support
    """
    if not os.path.exists(dir_out):
        logging.info(f"{dir_out} not exist, make it...")
        os.mkdir(dir_out)

    logging.info('Query query to Subject...')
    file_query_subject = blast(query, subject, blast_type, dir_out)

    logging.info('Query subject blast query')
    flie_subject_query = blast(subject, query, blast_type, dir_out)

    logging.info("Parse the blast result")
    query_subject = parse_blast(file_query_subject)
    subject_query = parse_blast(flie_subject_query)
    res = {}
    for query, subject in query_subject.items():
        if subject in subject_query and subject_query[subject] == query:
            res[query] = subject
    file_out = os.path.join(dir_out, 'result.txt')
    with open(file_out, 'w') as OUT:
        for key, value in res.items():
            print(*[key, value], sep='\t', file=OUT)


if __name__ == '__main__':
    DIAMOND = '/Bio/Linux-src-files/NGS/Align/diamond/diamond-0.9.22/diamond'
    bothwayblast()
