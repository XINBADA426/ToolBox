#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2019-03-22 16:30:33
# @Last Modified by:   MingJia
# @Last Modified time: 2019-10-28 14:42:44
import argparse
import glob
import os


def get_relationship(file_in):
    res = {}
    with open(file_in, 'r') as IN:
        for line in IN:
            arr = line.strip().split('\t')
            res[arr[0]] = arr[1]
    return res


def deal_filename(ori_file_name, relationship, tags):
    new_name = None
    tag_list = tags.strip().split('|')
    dir_in = os.path.dirname(ori_file_name)
    for key in relationship.keys():
        if key in ori_file_name:
            if tag_list[0] in ori_file_name:
                new_name = os.path.join(
                    dir_in, '{}_1.fq.gz'.format(relationship[key]))
            elif tag_list[1] in ori_file_name:
                new_name = os.path.join(
                    dir_in, '{}_2.fq.gz'.format(relationship[key]))
    return new_name


def main(args):
    """
    """
    relationship = get_relationship(args.file_list)
    files_list = glob.glob(os.path.join(args.dir_in, '*.gz'))
    for file_name in files_list:
        new_name = deal_filename(file_name, relationship, args.tag)
        if new_name:
            print(file_name, new_name)
            os.rename(file_name, new_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u"测序的原始数据重命名，再也不用一个个改名字了😂。", )
    parser.add_argument("-i", "--dir_in", default="./",
                        help=u"The fq reads dir.")
    parser.add_argument("-l", "--file_list", default="list.txt",
                        help=u"The file list(生产编号\\t分析名称)")
    parser.add_argument("-t", "--tag", default='_R1_|_R2_',
                        help=u"The tag of read1 and read2(default _R1_|_R2_).")
    args = parser.parse_args()
    main(args)
