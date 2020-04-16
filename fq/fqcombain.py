#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-03-11 17:07:44
# @Last Modified by:   MingJia
# @Last Modified time: 2020-03-11 17:40:27
import glob
import os
import subprocess

import click


#### Some Functions ####


def get_sample_names(file_in):
    """
    """
    res = set()
    with open(file_in, 'r') as IN:
        for line in IN:
            if line.strip():
                res.add(line.strip())
    return res


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-s', '--samples',
              required=True,
              type=click.Path(),
              help="The file contain the mark for samples to combain")
@click.option('-r', '--rawdata',
              required=True,
              type=click.Path(),
              help="The rawdata dirs,sep by ','")
@click.option('-o', '--out',
              required=True,
              type=click.Path(),
              help="The out put dir")
@click.option('--suffix',
              required=True,
              default='fq.gz',
              show_default=True,
              help="The suffix for fq files")
def cli(samples, rawdata, out, suffix):
    """
    Combain rawdatas from different batch

    The fq1 name must be *_1.*\n
    The fq2 name must be *_2.*
    """
    dir_oris = rawdata.strip().split(',')
    sample_names = get_sample_names(samples)
    out = os.path.abspath(out)

    for sample in sample_names:
        click.echo(click.style(f'Deal with {sample}', fg='green'))
        fq1s = []
        fq2s = []
        statue_code = 0
        for i in dir_oris:
            fq_files = glob.glob(f'{i}/*.{suffix}')
            for fq_file in fq_files:
                if sample in fq_file and f'_1.{suffix}' in fq_file:
                    fq1s.append(os.path.realpath(fq_file))
                    statue_code += 1
                elif sample in fq_file and f'_2.{suffix}' in fq_file:
                    fq2s.append(os.path.realpath(fq_file))
                    statue_code += 1
        if statue_code == 0:
            click.echo(click.style(f'{sample} not exists', fg='red'))
        elif statue_code % 2 == 1:
            click.echo(
                click.style(f'{sample} got the wrong fq numer', fg='red'))
        elif statue_code == 2:
            cmd = f"""
ln -sf {fq1s[0]} {out}/{sample}_1.fq.gz
ln -sf {fq2s[0]} {out}/{sample}_2.fq.gz
"""
            click.echo(click.style(f'{cmd}', fg='green'))
            subprocess.run(cmd, shell=True)
        else:
            seq1 = ' '.join(fq1s)
            seq2 = ' '.join(fq2s)
            cmd = f"""
cat {seq1} > {out}/{sample}_1.fq.gz
cat {seq2} > {out}/{sample}_2.fq.gz
"""
            click.echo(click.style(f'{cmd}', fg='green'))
            subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    cli()
