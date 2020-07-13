#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-07-11 10:32:16
# @Last Modified by:   Ming
# @Last Modified time: 2020-07-12 13:41:07
import gzip
import logging
import os
import subprocess

import click

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def parse_diamod_report(file_diamond_tab, file_acc2taxon, file_names_dmp,
                        file_out):
    """
    Parse the diamond report
    """
    logging.info(f"Parse the {file_acc2taxon}...")
    info_acc2taxon = {}
    with gzip.open(file_acc2taxon, 'rt') as IN:
        next(IN)
        for line in IN:
            arr = line.strip().split('\t')
            info_acc2taxon[arr[1]] = arr[2]

    logging.info(f"Parse the {file_names_dmp}...")
    info_taxonid2name = {}
    with open(file_names_dmp, 'r') as IN:
        for line in IN:
            arr = [i.strip() for i in line.split('|')]
            if arr[3] == "scientific name":
                info_taxonid2name[arr[0]] = arr[1]

    logging.info(f"Parse the {file_diamond_tab}...")
    res = {}
    pool = set()
    with open(file_diamond_tab, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            if arr[0] not in pool:
                if arr[1] in info_acc2taxon and info_acc2taxon[
                    arr[1]] in info_taxonid2name:
                    spe = info_taxonid2name[info_acc2taxon[arr[1]]]
                    res.setdefault(spe, 0)
                    res[spe] += 1
                    pool.add(arr[0])

    logging.info(f"Out put the result to {file_out}")
    with open(file_out, 'w') as OUT:
        print(*["Species", "Count"], sep='\t', file=OUT)
        for key, value in sorted(res.items(), key=lambda x: x[1], reverse=True):
            print(*[key, value], sep='\t', file=OUT)


def parse_kraken2_report(file_name, file_out):
    """
    Parse the kraken2 report
    """
    logging.info(f"Parse the {file_name}...")
    res = {}
    with open(file_name, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            if arr[3].strip() == "S":
                res[arr[5].strip()] = int(arr[1].strip())
    logging.info(f"Out put the result to {file_out}")
    with open(file_out, 'w') as OUT:
        print(*["Species", "Count"], sep='\t', file=OUT)
        for key, value in sorted(res.items(), key=lambda x: x[1], reverse=True):
            print(*[key, value], sep='\t', file=OUT)


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Species stat for fasta
    """
    pass


@click.command()
@click.option('-f', '--fasta',
              required=True,
              type=click.Path(),
              help="The input fasta file")
@click.option('--db',
              default="/Bio/Database/Database/diamondDB/nr/2018-06-08/9class/all",
              show_default=True,
              help="The database path to use")
@click.option('--diamond',
              default="/Bio/Linux-src-files/NGS/Align/diamond/with_intelcompiler/diamond-0.9.24/diamond",
              show_default=True,
              type=click.Path(),
              help="The diamond path")
@click.option('--program',
              default="blastx",
              show_default=True,
              type=click.Choice(["blastx", "blastp"]),
              help="The blast program to use")
@click.option('--param',
              default="-e 1e-5 --salltitles --sensitive --outfmt 6 -p 4",
              show_default=True,
              help="The diamond param")
@click.option('--acc2taxon',
              default="/Bio/Database/Database/diamondDB/nr/2018-06-08/prot.accession2taxid.gz",
              show_default=True,
              type=click.Path(),
              help="The accession2taxid file")
@click.option('--names',
              default="/Bio/Database/Database/diamondDB/nr/2018-06-08/taxdump/names.dmp",
              show_default=True,
              type=click.Path(),
              help="The names.dmp file")
@click.option('--out',
              default="./",
              show_default=True,
              help="The out put dir")
@click.option('--prefix',
              default="result",
              show_default=True,
              help="The out put prefix")
def diamond(fasta, db, diamond, program, param, acc2taxon, names, out, prefix):
    """
    Use diamod to get the species info of the fasta seq

    Be attention please!!!
    It must use the big mem node in parse diamond tab
    """
    fasta = os.path.abspath(fasta)
    dir_out = os.path.abspath(out)
    if not os.path.exists(dir_out):
        logging.info(f"{dir_out} not exists, make it")
        os.makedirs(dir_out)
    logging.info(f"Query the {fasta} through diamond")
    cmd = f"{diamond} {program} {param} -d {db} -q {fasta} -o {dir_out}/{prefix}.tab"
    logging.info(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"{e}")

    parse_diamod_report(f"{dir_out}/{prefix}.tab", acc2taxon,
                        names, f"{dir_out}/{prefix}.spe.txt")


@click.command()
@click.option('-f', '--fasta',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option('--db',
              default="/home/renchaobo/db/Kraken2/micro",
              show_default=True,
              help="The database path to use")
@click.option('--kraken2',
              default="/public/Database/kraken/kraken2/kraken2",
              show_default=True,
              help="The kraken2 program path")
@click.option('--param',
              default="--threads 8",
              show_default=True,
              help="The diamond param")
@click.option('--out',
              default="./",
              show_default=True,
              help="The out put dir")
@click.option('--prefix',
              default="result",
              show_default=True,
              help="The out put prefix")
def kraken2(fasta, db, kraken2, param, out, prefix):
    """
    Use kraken2 to get the species info of the fasta seq
    """
    fasta = os.path.abspath(fasta)
    dir_out = os.path.abspath(out)
    if not os.path.exists(dir_out):
        logging.info(f"{dir_out} not exists, make it")
        os.makedirs(dir_out)
    logging.info(f"Query the {fasta} through kraken2")
    cmd = f"{kraken2} {param} -db {db} --output {dir_out}/{prefix}.kraken2 --report {dir_out}/{prefix}.report {fasta}"
    logging.info(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"{e}")

    parse_kraken2_report(f"{dir_out}/{prefix}.report",
                         f"{dir_out}/{prefix}.spe.txt")


cli.add_command(diamond)
cli.add_command(kraken2)

if __name__ == "__main__":
    cli()
