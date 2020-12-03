#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-11-30 22:36:30
# @Last Modified by:   Ming
# @Last Modified time: 2020-11-30 22:36:30
import logging
import os
import sys

import click

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
DIRNAME = os.path.dirname(os.path.abspath(__file__))
# sys.path.append("/Bio/User/renchaobo/PyLibs/EasyPipe/v3.x.x/v3.0.0")
sys.path.append("/Bio/User/renchaobo/2")
from EasyPipe import __version__
from EasyPipe import Pipe
from EasyPipe.jobs import Job
from EasyPipe.jobs import ComplexJob
from EasyPipe.utils import parse_config


#### Some Functions ####
def split(pipe):
    job = Job(name="split")
    job.set_workdir(f"{pipe.project_dir}/{job.name}")
    template = "{seqkit} split2 -p {num} -O {out} {fasta}"
    cmd = template.format(seqkit=pipe.softwares["seqkit"],
                          num=pipe.infos["cut"],
                          out=job.workdir,
                          fasta=pipe.infos["fasta"])
    job.add_command(cmd)
    pipe.add(job)


def align(pipe):
    job = ComplexJob(name="blast")
    job.set_workdir(f"{pipe.project_dir}/{job.name}")

    align = Job(name="align")
    align.set_workdir(f"{pipe.project_dir}/{job.name}/{align.name}")
    align.set_run_type("multi_run")
    align.set_jobprefix("blast")
    align.set_maxjob(min(12, pipe.infos["cut"]))
    fa = os.path.basename(pipe.infos["fasta"])
    dir_split = pipe.children["split"].workdir
    prefix, suffix = os.path.splitext(fa)
    tags = ["part_%s" % str(i + 1).rjust(3, '0') for i in
            range(pipe.infos["cut"])]
    fas = [os.path.join(dir_split, f"{prefix}.{i}{suffix}") for i in tags]

    if pipe.infos["db"] == "nr":
        db = pipe.dbs["nr"]
        software = pipe.softwares["diamond"]
        if pipe.infos["seqtype"] == "prot":
            template = "{software} blastp -p 6 -f 100 -d {db} -q {seq} -e 1e-5 -k 20 -o {out};{software} view -p 6 --daa {out} -f 6 -o {tsv}"
            for i in range(len(fas)):
                seq = fas[i]
                out = os.path.join(align.workdir,
                                   f"{prefix}.{tags[i]}{suffix}.daa")
                tsv = os.path.join(align.workdir,
                                   f"{prefix}.{tags[i]}{suffix}.tsv")
                align.add_command(
                    template.format(software=software,
                                    db=db,
                                    seq=seq,
                                    out=out,
                                    tsv=tsv))
        elif pipe.infos["seqtype"] == "nucl":
            template = "{software} blastx -p 6 -f 100 -d {db} -q {seq} -e 1e-5 -k 20 -o {out};{software} view -p 6 --daa {out} -f 6 -o {tsv}"
            for i in range(len(fas)):
                seq = fas[i]
                out = os.path.join(align.workdir,
                                   f"{prefix}.{tags[i]}{suffix}.daa")
                tsv = os.path.join(align.workdir,
                                   f"{prefix}.{tags[i]}{suffix}.tsv")
                align.add_command(
                    template.format(software=software,
                                    db=db,
                                    seq=seq,
                                    out=out,
                                    tsv=tsv))
    elif pipe.infos["db"] == "nt":
        db = pipe.dbs["nt"]
        if pipe.infos["seqtype"] == "prot":
            pass
            # software = pipe.softwares[""]
            # template = f"{software} -p 6 -db {db} -query {seq} -num_alignments 20 -evalue 1e-5 -outfmt 6 -out {out}"
            # for i in range(len(fas)):
            #     seq = fas[i]
            #     out = os.path.join(align.workdir,
            #                        f"{prefix}.{tags[i]}{suffix}.tsv")
            #     align.add_command(
            #         template.format(software=software,
            #                         db=db,
            #                         seq=seq,
            #                         out=out))
        elif pipe.infos["seqtype"] == "nucl":
            software = pipe.softwares["blastn"]
            template = "{software} -p 6 -db {db} -query {seq} -num_alignments 20 -evalue 1e-5 -outfmt 6 -out {out}"
            for i in range(len(fas)):
                seq = fas[i]
                out = os.path.join(align.workdir,
                                   f"{prefix}.{tags[i]}{suffix}.tsv")
                align.add_command(
                    template.format(software=software,
                                    db=db,
                                    seq=seq,
                                    out=out))
    job.add(align)

    taxon = Job(name="taxon")
    taxon.set_workdir(f"{pipe.project_dir}/{job.name}/{taxon.name}")
    taxon.set_run_type("multi_run")
    taxon.set_maxjob(min(12, pipe.infos["cut"]))
    taxon.set_jobprefix("taxon")
    blast_tsvs = [os.path.join(align.workdir, f"{prefix}.{i}{suffix}.tsv")
                  for i in tags]
    acc2taxon_tsvs = [os.path.join(taxon.workdir, f"{prefix}.{i}.acc2taxon")
                      for i in tags]
    template = "{py} {script} -t {input} -c 1 --db {db} -o {out}"
    script = os.path.join(pipe.bin, "accession2taxid.py")
    db = pipe.dbs['nt_acc2taxonid'] if pipe.infos["db"] == "nt" else pipe.dbs[
        "nr_acc2taxonid"]
    for i in range(len(blast_tsvs)):
        cmd = template.format(py=pipe.softwares["py3"],
                              script=script,
                              input=blast_tsvs[i],
                              db=db,
                              out=acc2taxon_tsvs[i])
        taxon.add_command(cmd)
    job.add(taxon)

    merge = Job(name="merge")


    pipe.add(job)


# def lineage(pipe):
#     job = ComplexJob(name="taxon")
#     job.set_workdir(f"{pipe.project_dir}/{job.name}")
#     job.set_prefix("acc2taxon")
#     template = "{py} {script} {}"


########################

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0")
@click.option('--fasta',
              required=True,
              type=click.Path(),
              help="The seq file")
@click.option('--cut',
              default=5,
              show_default=True,
              type=int,
              help="The cut num for the seq")
@click.option('--seqtype',
              type=click.Choice(["nucl", "prot"]),
              required=True,
              help="The input seq type")
@click.option('--database',
              default="nr",
              show_default=True,
              type=click.Choice(["nr", "nt"]),
              help="Use nr or nt database")
@click.option('--config',
              default=os.path.join(DIRNAME, "blast2lineage.ini"),
              show_default=True,
              help="The config file to use")
@click.option('--out',
              default="./",
              show_default=True,
              type=click.Path(),
              help="The out put dir")
def cli(fasta, cut, seqtype, database, config, out):
    """
    Use nr/nt to get the gene lineage info

    If you choose nr db, it will use diamond as aligner,
    if nt, it will use blast
    """
    logging.info(f"EasyPipe version: {__version__}")

    fasta = os.path.abspath(fasta)
    out = os.path.abspath(out)
    project = Pipe(project_name="Blast2lineage",
                   project_dir=out)

    cfg = parse_config(os.path.abspath(config))
    for software in cfg.options("software"):
        project.add_software(software, cfg.get("software", software))
    for db in cfg.options("db"):
        project.add_db(db, cfg.get("db", db))
    project.set_bin(os.path.join(DIRNAME, "bin"))
    project.add_info("seqtype", seqtype)
    project.add_info("db", database)
    project.add_info("cut", cut)
    project.add_info("fasta", fasta)

    logging.debug(project)
    split(project)
    align(project)
    project.finish()


if __name__ == "__main__":
    cli()
