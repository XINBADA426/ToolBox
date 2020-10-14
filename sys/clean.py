#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-09-20 07:38:27
# @Last Modified by:   MingJia
# @Last Modified time: 2020-09-20 07:38:27
import logging
import os
import sqlite3
import subprocess
from datetime import date, timedelta

import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def mild_clean_command(dir_path):
    """
    Generate mild clean command

    :param dir_path: The dir you want to clean
    :return:
    """
    command = f"""
find {dir_path} -type d \
-name *.qsub \
-name *_map \
-delete
find {dir_path} -type f \
-iname *clean.sh \
-exec bash {{}}
"""
    return command


def deep_clean_command(dir_path):
    """

    :return:
    """
    command = f"""
find {dir_path} -type d \
-name *.qsub \
-name *_map \
-delete
find {dir_path} -type f \
! -iname "*.py" \
! -iname "*.sh" \
! -iname "*.r" \
! -iname "*.pl" \
! -iname "*.conf" \
! -iname "*.yml" \
! -iname "*.yaml" \
! -iname "*.ini" \
! -iname "*.nf" \
! -iname "*.config" \
! -iname "*.tar.bz2" \
! -iname "*.tar.gz" \
! -iname "*.tbz2" \
-delete
"""
    return command


class Analysis(object):
    """A Class for deal with analysis
    """

    def __init__(self, info, connect, cursor, force=False):
        """
        Init the Analysis Class

        :param info: Info fetch from database
        """
        super(Analysis, self).__init__()
        self.project_id = info[0]
        self.analysis_id = info[1]
        self.analysis_type = info[2]
        self.product_line = info[3]
        self.time_finish = info[4]
        self.time_clean = info[5]
        self.size_before_clean = info[6]
        self.size_after_clean = info[7]
        self.server_address = info[8]
        self.ftp_address = info[9]
        self.clean = int(info[10])
        self.deep_clean = int(info[11])
        self.connect = connect
        self.cursor = cursor
        self.force = force
        if self.server_address == "NA":
            raise Exception(f"Server address for {self.analysis_id} is None")

    def get_dir_size(self):
        """
        Get the analysis dir size
        """
        try:
            res = subprocess.check_output(
                ["du", "-sh", self.server_address]).decode().split('\t')[0]
        except:
            logging.error(
                f"Check dir size err {self.analysis_id}: {self.server_address}")
        return res

    def mild(self):
        """
        Mild clean for the analysis
        """
        if self.time_finish == "NA":
            raise Exception(f"{self.analysis_id} not finish")
        if self.size_before_clean == "NA":
            self.size_before_clean = self.get_dir_size()

        if self.force or self.clean == 0:
            if self.analysis_type == "补充分析" or self.analysis_type == "个性化分析":
                command = deep_clean_command(self.server_address)
            else:
                # 先偷懒处理
                if "有参RNA-seq" in self.product_line:
                    command = mild_clean_command(self.server_address)
                elif "宏基因组" in self.product_line:
                    command = mild_clean_command(self.server_address)
                elif "10X" in self.product_line:
                    command = mild_clean_command(self.server_address)
            subprocess.run(command, shell=True)

            self.time_clean = date.today()
            self.size_after_clean = self.get_dir_size()
            self.clean = 1
            self.update()

    def deep(self):
        """
        Deep clean for the analysis
        """
        if self.time_finish == "NA":
            raise Exception(f"{self.analysis_id} not finish")
        if self.size_before_clean == "NA":
            self.size_before_clean = self.get_dir_size()
        if self.force or self.deep_clean == 0:
            command = deep_clean_command(self.server_address)
            subprocess.run(command, shell=True)
            self.time_clean = date.today()
            self.size_after_clean = self.get_dir_size()
            self.clean = 1
            self.deep_clean = 1
            self.update()

    def update(self):
        """
        """
        sql = f"""UPDATE info
SET time_finish = \"{self.time_finish}\",
    time_clean = \"{self.time_clean}\",
    size_before_clean = \"{self.size_before_clean}\",
    size_after_clean = \"{self.size_after_clean}\",
    clean = \"{self.clean}\",
    deep_clean = \"{self.deep_clean}\"
WHERE analysis_id = \"{self.analysis_id}\"
"""
        self.cursor.execute(sql)
        self.connect.commit()


def parse_list_file(file_name):
    """
    Parse the one column file
    """
    res = set()
    with open(file_name, 'r') as IN:
        for line in IN:
            res.add(line.strip())
    return res


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
                analysis_type = analysis_info[2] if len(
                    analysis_info) > 2 else "NA"
                product_line = analysis_info[3] if len(
                    analysis_info) > 3 else "NA"
            else:
                analysis_type = analysis_info[1] if len(
                    analysis_info) > 1 else "NA"
                product_line = analysis_info[2] if len(
                    analysis_info) > 2 else "NA"
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


def screen_by_time(start, end, cursor):
    """
    Screen the data in the project db by start and end time
    """
    sql = f'''SELECT * FROM info
            WHERE time_finish >= \"{start}\"
            AND 
            time_finish <= \"{end}\"'''
    cursor.execute(sql)
    infos = cursor.fetchall()
    if len(infos) > 0:
        res = {i[1]: i for i in infos}
    else:
        res = {}
    return res


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
    cursor.executemany('INSERT INTO info VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                       project_info)

    cursor.close()
    connect.commit()
    connect.close()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--start',
              default=date.today() - timedelta(180),
              show_default=True,
              help="The start time you want to clean")
@click.option('--end',
              default=date.today() - timedelta(90),
              show_default=True,
              help="The end time you want to clean")
@click.option('--include',
              type=click.Path(),
              help="The file contain the analysis names will be clean")
@click.option('--exclude',
              type=click.Path(),
              help="The file contain the analysis names should be exclude")
@click.option('--db',
              default="/home/renchaobo/db/clean/project.db",
              show_default=True,
              type=click.Path(),
              help="The project database")
@click.option('--force/--no-force',
              default=False,
              show_default=True,
              help="Whether force clean")
@click.option("--log",
              required=True,
              type=click.Path(),
              help="The mild clean log")
def mild(start, end, include, exclude, db, force, log):
    """
    Mild clean

    如果提供分析名称文件，则只清理start-end之间，并包含在分析名称文件内的项目
    """
    logging.info(f"Connect the database {db}...")
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    analysis_infos = screen_by_time(start, end, cursor)
    if include:
        logging.info(f"Parse the include file {include}...")
        include_names = parse_list_file(include)
        analysis_infos = {i: analysis_infos[i] for i in analysis_infos.keys() if
                          i in include_names}
    if exclude:
        logging.info(f"Parse the include file {exclude}...")
        exclude_names = parse_list_file(exclude)
        analysis_infos = {i: analysis_infos[i] for i in analysis_infos.keys() if
                          i not in exclude_names}

    res = []
    for analysis_id, info in analysis_infos.items():
        obj = Analysis(info, connect, cursor, force=force)
        obj.mild()
        res.append(obj)

    cursor.close()
    connect.close()

    header = ["project_id", "analysis_id", "analysis_type", "product_line",
              "time_finish", "time_clean", "size_before_clean",
              "size_after_clean", "server_address", "ftp_address", "clean",
              "deep_clean"]
    logging.info(f"Out put the clean log...")
    with open(log, 'w') as OUT:
        print(*header, sep='\t', file=OUT)
        for i in res:
            tmp = [i.project_id, i.analysis_id,
                   i.analysis_type, i.product_line,
                   i.time_finish, i.time_clean,
                   i.size_before_clean, i.size_after_clean,
                   i.server_address, i.ftp_address,
                   i.clean, i.deep_clean]
            print(*tmp, sep='\t', file=OUT)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--start',
              default=date.today() - timedelta(180),
              show_default=True,
              help="The start time you want to clean")
@click.option('--end',
              default=date.today() - timedelta(90),
              show_default=True,
              help="The end time you want to clean")
@click.option('--include',
              type=click.Path(),
              help="The file contain the analysis names will be clean")
@click.option('--exclude',
              type=click.Path(),
              help="The file contain the analysis names should be exclude")
@click.option('--db',
              default="/home/renchaobo/db/clean/project.db",
              show_default=True,
              type=click.Path(),
              help="The project database")
@click.option('--force/--no-force',
              default=False,
              show_default=True,
              help="Whether force clean")
@click.option("--log",
              required=True,
              type=click.Path(),
              help="The deep clean log")
def deep(start, end, include, exclude, db, force, log):
    """
    Deep clean

    如果提供分析名称文件，则只清理start-end之间，并包含在分析名称文件内的项目
    """
    logging.info(f"Connect the database {db}...")
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    analysis_infos = screen_by_time(start, end, cursor)
    if include:
        logging.info(f"Parse the include file {include}...")
        include_names = parse_list_file(include)
        analysis_infos = {i: analysis_infos[i] for i in analysis_infos.keys() if
                          i in include_names}
    if exclude:
        logging.info(f"Parse the include file {exclude}...")
        exclude_names = parse_list_file(exclude)
        analysis_infos = {i: analysis_infos[i] for i in analysis_infos.keys() if
                          i not in exclude_names}

    res = []
    for analysis_id, info in analysis_infos.items():
        obj = Analysis(info, connect, cursor, force=force)
        obj.deep()
        res.append(obj)

    cursor.close()
    connect.close()

    header = ["project_id", "analysis_id", "analysis_type", "product_line",
              "time_finish", "time_clean", "size_before_clean",
              "size_after_clean", "server_address", "ftp_address", "clean",
              "deep_clean"]
    logging.info(f"Out put the clean log...")
    with open(log, 'w') as OUT:
        print(*header, sep='\t', file=OUT)
        for i in res:
            tmp = [i.project_id, i.analysis_id,
                   i.analysis_type, i.product_line,
                   i.time_finish, i.time_clean,
                   i.size_before_clean, i.size_after_clean,
                   i.server_address, i.ftp_address,
                   i.clean, i.deep_clean]
            print(*tmp, sep='\t', file=OUT)


cli.add_command(init)
cli.add_command(mild)
cli.add_command(deep)

if __name__ == "__main__":
    cli()
