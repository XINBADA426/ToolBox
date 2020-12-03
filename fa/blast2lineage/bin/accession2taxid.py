#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-09-16 10:31:54
# @Last Modified by:   MingJia
# @Last Modified time: 2020-09-16 10:31:54
import logging
import sqlite3

import click

########################

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


########################

def query_accession(accession, cursor):
    """
    Query the accession info

    :param accession: The nucl or prot accession(no version info)
    :param db: The accession2taxid.db cursor
    :return: The taxon id
    """
    cursor.execute(
        f"SELECT taxid FROM accession2taxid WHERE accession==\"{accession}\"")
    try:
        res = cursor.fetchone()[0]
    except TypeError:
        # logging.warning(f"{accession} could not be found in database")
        res = None
    return res


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-t', '--table',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option('-c', '--column',
              required=True,
              type=int,
              help="The accession id column number(0 base)")
@click.option('--db',
              required=True,
              default="/home/renchaobo/db/accession2taxid/prot/20170309/accession2taxid.db",
              show_default=True,
              type=click.Path(),
              help="The accession to taxonid database")
@click.option('--header/--no-header',
              default=False,
              show_default=True,
              help="Whether the input file has a header")
@click.option('-o', '--out',
              default="res.tsv",
              type=click.Path(),
              help="The out put file name")
def cli(table, column, db, header, out):
    """Get the taxonid from the accession id.
    The taxon id would add to the end of each line.

    \b
    The accession id should not has version info.
    APZ74649    ---- Right
    APZ74649.1  ---- Wrong
    """
    logging.info(f"Connect the database {db}...")
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    logging.info(f"Searching the input file {table}...")
    pool = set()
    with open(table, 'r') as IN, open(out, 'w') as OUT:
        if header:
            print(*[*next(IN).strip().split('\t'), "TaxonID"], sep='\t',
                  file=OUT)
        for line in IN:
            arr = line.strip().split('\t')
            query = arr[0]
            if query not in pool:
                accession = arr[column].strip().split('.')[0]
                taxonid = query_accession(accession, cursor)
                if taxonid:
                    print(*[query, arr[column], taxonid], sep='\t', file=OUT)
                    pool.add(query)
    logging.info(f"Finish. the output file is {out}")


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

if __name__ == "__main__":
    cli()
