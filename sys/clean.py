#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-09-20 07:38:27
# @Last Modified by:   MingJia
# @Last Modified time: 2020-09-20 07:38:27
import logging
import os
import sqlite3

import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def parse_project_table(file_name):
    """
    Parse the table file generate by get_my_plan.py
    """
    res = []
    with open(file_name, 'r') as IN:
        next(IN)
        for line in IN:
            # p_id, a_id,
            arr = line.strip().split('\t')
            project_id = arr[0].strip().split('/')[0]
            analysis_info = arr[1].split('/')
            analysis_id = analysis_info[0]
            if '例' in analysis_info[1]:
                analysis_type = analysis_info[2] if len(analysis_info) > 2 else "NA"
                product_line = analysis_info[3] if len(analysis_info) > 3 else "NA"
            else:
                analysis_type = analysis_info[1] if len(analysis_info) > 1 else "NA"
                product_line = analysis_info[2] if len(analysis_info) > 2 else "NA"
            time_finish = arr[12] if arr[12] else "NA"
            time_clean = 'NA'
            size_before_clean = "NA"
            size_after_clean = "NA"
            server_address = arr[20] if arr[20] else "NA"
            ftp_address = "NA" if len(arr) < 22 else arr[21]
            clean = 0
            deep_clean = 0

            info = [project_id,
                    analysis_id,
                    analysis_type,
                    product_line,
                    time_finish,
                    time_clean,
                    size_before_clean,
                    size_after_clean,
                    server_address,
                    ftp_address,
                    clean,
                    deep_clean]
            res.append(info)
    return res


def db_update(info, cursor):
    """
    Update the project info database
    """
    pass


########################

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Tools to clean projects
    """
    pass


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input file genenate by get_my_plan.py")
@click.option('-o', '--out',
              default="/home/renchaobo/db/clean/project.db",
              show_default=True,
              type=click.Path(),
              help="The out put sqlite3 database that contain project info")
def init(input, out):
    """
    Init a sqlite3 db that contain the projcet info
    """
    logging.info(f"Read the info from file {input}...")
    project_info = parse_project_table(input)
    if os.path.exists(out):
        logging.error(f"Database {out} exist")
        exit(1)
    logging.info(f"Connect the database {out}...")
    connect = sqlite3.connect(out)
    cursor = connect.cursor()
    logging.info("Create table info")
    sql = '''CREATE TABLE info(
            project_id VARCHAR(20),
            analysis_id VARCHAR(40) PRIMARY KEY,
            analysis_type VARCHAR(20) ,
            product_line VARCHAR(20),
            time_finish DATE ,
            time_clean DATE,
            size_before_clean TEXT,
            size_after_clean TEXT,
            server_address TEXT,
            ftp_address TEXT,
            clean INTEGER,
            deep_clean INTEGER)'''
    cursor.execute(sql)
    logging.info("Insert data to table info...")
    cursor.executemany('INSERT INTO info VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', project_info)
    connect.commit()

    cursor.close()
    connect.close()


cli.add_command(init)

if __name__ == "__main__":
    cli()
