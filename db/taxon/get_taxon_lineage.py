#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: xinbada
# @Date:   2019-08-06 16:25:56
# @Last Modified by:   MingJia
# @Last Modified time: 2020-06-05 11:46:19
import logging
import os

import click

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


#### Some Functions ####


class Tree(object):
    """docstring for Tree"""

    def __init__(self, file_name, file_node):
        super(Tree, self).__init__()
        self.tree = {}
        self.parse_name(file_name)
        self.parse_node(file_node)
        self.prefix = {'root': 'r__',
                       'kingdom': 'k__',
                       'phylum': 'p__',
                       'class': 'c__',
                       'order': 'o__',
                       'family': 'f__',
                       'genus': 'g__',
                       'species': 's__'}
        self.last_clade = {'kingdom': 'root',
                           'phylum': 'kingdom',
                           'class': 'phylum',
                           'order': 'class',
                           'family': 'order',
                           'genus': 'family',
                           'species': 'genus'}
        logging.info('Build the lineage tree...')
        self.number = 0
        for key in self.names.keys():
            self.number += 1
            self.add_node(key)

    def parse_name(self, file_name):
        """
        Parse the file names.dmp
        """
        logging.info("Parse the names.dmp...")
        self.names = {}
        with open(file_name, 'r') as IN:
            for line in IN:
                arr = [i.strip() for i in line.split('|')]
                if arr[3] == "scientific name":
                    self.names[arr[0]] = arr[1].replace(
                        ' ', '_').replace('#', '')

    def parse_node(self, file_node):
        """
        Parse the file nodes.dmp

        由于项目需要，将细菌，古菌，病毒，类病毒的rank都设为kindgom，直接指向root
        将除真菌之外的真核生物也设为kindgom，直接指向root
        """
        logging.info("Parse the nodes.dmp...")
        self.parents = {}
        self.ranks = {}
        with open(file_node, 'r') as IN:
            for line in IN:
                arr = [i.strip() for i in line.split('|')]
                # Bacteria | Archaea | Viruses | Viroids | Eukaryota
                if arr[0] == '2' or arr[0] == '2157' or arr[0] == '10239' or \
                        arr[
                            0] == '12884' or arr[0] == '2759':
                    arr[2] = 'kingdom'
                if arr[2] == 'kingdom':
                    arr[1] = '1'
                self.parents[arr[0]] = arr[1]
                self.ranks[arr[0]] = arr[2]

    def add_node(self, taxon_id):
        taxon_name = self.names[taxon_id]
        parent_taxon_id = self.parents[taxon_id]
        taxon_rank = self.ranks[taxon_id]

        if taxon_id == '1':
            self.tree['1'] = {'clade': 'root', 'taxon': 'r__root'}

        if parent_taxon_id not in self.tree:
            self.add_node(parent_taxon_id)

        if taxon_rank in self.prefix:
            parent_taxon = self.tree[parent_taxon_id]['taxon']
            prefix = self.prefix[taxon_rank]

            if self.prefix[self.last_clade[taxon_rank]] not in parent_taxon:
                parent_taxon = self.get_full_taxon(
                    parent_taxon, taxon_rank)

            self.tree[taxon_id] = {'clade': f'{taxon_rank}',
                                   'taxon': f'{parent_taxon}|{prefix}{taxon_name}'}
        else:
            self.tree[taxon_id] = self.tree[parent_taxon_id]

    def get_full_taxon(self, parent_taxon, taxon_rank):
        if parent_taxon == 'r__root':
            for key, value in self.prefix.items():
                if key == 'root':
                    pass
                elif key == taxon_rank:
                    return parent_taxon
                else:
                    parent_taxon = f'{parent_taxon};{value}{key}_noname'
        else:
            basename = parent_taxon.strip().split(';')[-1].split('__')[1]
            for key, value in self.prefix.items():
                if key == taxon_rank:
                    return parent_taxon
                if value not in parent_taxon:
                    parent_taxon = f'{parent_taxon};{value}{basename}_noname'

    def to_pickle(self, output):
        """
        Out put the tree info to a pickle file
        """
        import pickle
        logging.info(f"Pickle the info to {output}...")
        with open(output, 'wb') as OUT:
            pickle.dump(self.tree, OUT)

    def to_sqlite(self, output):
        """
        Out put the tree info to a sqlite3 database
        """
        import sqlite3
        logging.info(f"Out put the info to database {output}...")
        if os.path.exists(output):
            logging.warning(f"{output} exists, remove it")
            os.remove(output)
        db = sqlite3.connect(output)
        c = db.cursor()
        cmd = "CREATE TABLE lineage (ID INT NOT NULL, CLADE text NOT NULL, LINEAGE text NOT NULL )"
        c.execute(cmd)
        for key, value in self.tree.items():
            key = int(key)
            cmd = "INSERT INTO lineage (ID, CLADE, LINEAGE) VALUES (?, ?, ?)"
            c.execute(cmd, (key, value['clade'], value['taxon']))
        db.commit()
        db.close()

    def to_txt(self, output):
        """
        Out put the tree info to a sqlite3 database
        """
        logging.info(f"Out put the info to txt file {output}...")
        with open(output, 'w') as OUT:
            print(*["ID", "CLADE", "LINEAGE"], sep='\t', file=OUT)
            for key, value in self.tree.items():
                print(*[key, value['clade'], value['taxon']], sep='\t',
                      file=OUT)


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--name',
              required=True,
              type=click.Path(),
              help="The names.dmp file")
@click.option('--node',
              required=True,
              type=click.Path(),
              help="The nodes.dmp file")
@click.option("-f", "--form",
              default='sqlite',
              show_default=True,
              type=click.Choice(['sqlite', 'pickle', 'txt']),
              help="The out put type for the taxon lineage info")
@click.option('--prefix',
              default='taxonid2lineage',
              show_default=True,
              help="The out put prefix")
def cli(name, node, form, prefix):
    """
    Use the names.dmp and nodes.dmp file to generate the taxonid
    lineage info

    由于项目需要，将细菌，古菌，病毒，类病毒的rank都设为kindgom，直接
    指向root将除真菌之外的真核生物也设为kindgom，直接指向root，如果某
    一ID对应的层级并非门纲目科属种中的一个，则其层级为其最近的父节点所
    对应的门纲目科属种
    """
    lineage_info = Tree(name, node)

    if form == "sqlite":
        lineage_info.to_sqlite(f"{prefix}.db")
    elif form == "pickle":
        lineage_info.to_pickle(f"{prefix}.pkl")
    elif form == "txt":
        lineage_info.to_txt(f"{prefix}.txt")


if __name__ == '__main__':
    cli()
