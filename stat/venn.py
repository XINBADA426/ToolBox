#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: MingJia
# @Date:   2020-08-04 22:29:57
# @Last Modified by:   MingJia
# @Last Modified time: 2020-08-05 11:30:00
import matplotlib as mpl

mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import chain
import pandas as pd
import logging
import click
import sys
import os

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


class Venn(object):
    """
    An class for Venn plot
    """
    default_colors = [
        # r, g, b, a
        [92, 192, 98, 0.5],
        [90, 155, 212, 0.5],
        [246, 236, 86, 0.6],
        [241, 90, 96, 0.4],
        [255, 117, 0, 0.3],
        [82, 82, 190, 0.2],
    ]

    def __init__(self, color=None):
        super(Venn, self).__init__()
        if color:
            self.colors = color
        else:
            self.colors = [
                [i[0] / 255.0, i[1] / 255.0, i[2] / 255.0, i[3]]
                for i in Venn.default_colors
            ]

    def parse(self, info):
        """
        Parse the DataFrame info to venn dict
        """
        self.samples = info.columns
        self.sample_num = len(self.samples)
        data = [set(info[sample].dropna()) for sample in self.samples]
        set_all = set(chain(*data))

        self.venn = {}
        for n in range(1, 2 ** self.sample_num):
            key = bin(n).split('0b')[-1].zfill(self.sample_num)
            value = set_all
            sets_for_intersection = [data[i]
                                     for i in range(self.sample_num) if
                                     key[i] == '1']
            sets_for_difference = [data[i]
                                   for i in range(self.sample_num) if
                                   key[i] == '0']
            for s in sets_for_intersection:
                value = value & s
            for s in sets_for_difference:
                value = value - s
            self.venn[key] = value

        self.label = {i: len(j) for i, j in self.venn.items()}

    def plot(self):
        """
        Draw the venn plot
        """
        if self.sample_num == 2:
            self.sample2()
        elif self.sample_num == 3:
            self.sample3()
        elif self.sample_num == 4:
            self.sample4()
        elif self.sample_num == 5:
            self.sample5()
        elif self.sample_num == 6:
            self.sample6()

    def get_result(self, dir_out):
        """
        Out put the plot and infos
        """
        logging.info(f"Out put the result to dir {dir_out}")
        prefix = os.path.join(dir_out, 'Venn')
        plt.savefig(prefix + '.svg', bbox_inches='tight')
        plt.savefig(prefix + '.png', bbox_inches='tight')

        file_venn = f"{prefix}.tsv"
        with open(file_venn, 'w') as OUT:
            for key, value in self.venn.items():
                name = '&'.join(
                    [self.samples[i] for i in range(self.sample_num) if
                     key[i] == '1'])
                elements = ';'.join(value) if len(value) > 0 else 'nan'
                print(*[name, elements], sep='\t', file=OUT)

    def sample2(self):
        """
        Two sample venn
        """
        logging.info("2 Sample Venn Plot...")
        colors = [self.colors[i] for i in range(self.sample_num)]
        figsize = (10, 7)
        dpi = 96
        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        fontsize = 14

        self.axis.set_axis_off()
        self.axis.set_ylim(bottom=0.0, top=0.7)
        self.axis.set_xlim(left=0.0, right=1.0)

        # body
        self.draw_ellipse(0.375, 0.3, 0.5, 0.5, 0.0, colors[0])
        self.draw_ellipse(0.625, 0.3, 0.5, 0.5, 0.0, colors[1])
        self.draw_text(0.74, 0.30, self.label.get('01', ''), fontsize=fontsize)
        self.draw_text(0.26, 0.30, self.label.get('10', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.30, self.label.get('11', ''), fontsize=fontsize)

        # legend
        self.draw_text(0.20, 0.56,
                       self.samples[0],
                       colors[0],
                       fontsize=fontsize,
                       ha="right", va="bottom")
        self.draw_text(0.80, 0.56,
                       self.samples[1],
                       colors[1],
                       fontsize=fontsize,
                       ha="left", va="bottom")
        legend = self.axis.legend(self.samples,
                                  loc='center left',
                                  bbox_to_anchor=(1.0, 0.5),
                                  fancybox=True)
        legend.get_frame().set_alpha(0.5)

    def sample3(self):
        """
        Three sample venn
        """
        logging.info("3 Sample Venn Plot...")

        colors = [self.colors[i] for i in range(self.sample_num)]
        figsize = (9, 9)
        dpi = 96
        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        fontsize = 14

        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        self.axis.set_axis_off()
        self.axis.set_ylim(bottom=0.0, top=1.0)
        self.axis.set_xlim(left=0.0, right=1.0)

        # body
        self.draw_ellipse(0.333, 0.633, 0.5, 0.5, 0.0, colors[0])
        self.draw_ellipse(0.666, 0.633, 0.5, 0.5, 0.0, colors[1])
        self.draw_ellipse(0.500, 0.310, 0.5, 0.5, 0.0, colors[2])
        self.draw_text(0.50, 0.27, self.label.get(
            '001', ''), fontsize=fontsize)
        self.draw_text(0.73, 0.65, self.label.get(
            '010', ''), fontsize=fontsize)
        self.draw_text(0.61, 0.46, self.label.get(
            '011', ''), fontsize=fontsize)
        self.draw_text(0.27, 0.65, self.label.get(
            '100', ''), fontsize=fontsize)
        self.draw_text(0.39, 0.46, self.label.get(
            '101', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.65, self.label.get(
            '110', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.51, self.label.get(
            '111', ''), fontsize=fontsize)

        # legend
        self.draw_text(0.15, 0.87,
                       self.samples[0],
                       colors[0],
                       fontsize=fontsize,
                       ha="right", va="bottom")
        self.draw_text(0.85, 0.87,
                       self.samples[1],
                       colors[1],
                       fontsize=fontsize,
                       ha="left",
                       va="bottom")
        self.draw_text(0.50, 0.02,
                       self.samples[2],
                       colors[2],
                       fontsize=fontsize,
                       va="top")
        legend = self.axis.legend(self.samples,
                                  loc='center left',
                                  bbox_to_anchor=(1.0, 0.5),
                                  fancybox=True)
        legend.get_frame().set_alpha(0.5)

    def sample4(self):
        """
        Four sample venn
        """
        logging.info("4 Sample Venn Plot...")
        colors = [self.colors[i] for i in range(self.sample_num)]
        figsize = (12, 12)
        dpi = 96
        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        fontsize = 14

        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        self.axis.set_axis_off()
        self.axis.set_ylim(bottom=0.0, top=1.0)
        self.axis.set_xlim(left=0.0, right=1.0)

        # body
        self.draw_ellipse(0.350, 0.400, 0.72, 0.45, 140.0, colors[0])
        self.draw_ellipse(0.450, 0.500, 0.72, 0.45, 140.0, colors[1])
        self.draw_ellipse(0.544, 0.500, 0.72, 0.45, 40.0, colors[2])
        self.draw_ellipse(0.644, 0.400, 0.72, 0.45, 40.0, colors[3])
        self.draw_text(0.85, 0.42, self.label.get(
            '0001', ''), fontsize=fontsize)
        self.draw_text(0.68, 0.72, self.label.get(
            '0010', ''), fontsize=fontsize)
        self.draw_text(0.77, 0.59, self.label.get(
            '0011', ''), fontsize=fontsize)
        self.draw_text(0.32, 0.72, self.label.get(
            '0100', ''), fontsize=fontsize)
        self.draw_text(0.71, 0.30, self.label.get(
            '0101', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.66, self.label.get(
            '0110', ''), fontsize=fontsize)
        self.draw_text(0.65, 0.50, self.label.get(
            '0111', ''), fontsize=fontsize)
        self.draw_text(0.14, 0.42, self.label.get(
            '1000', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.17, self.label.get(
            '1001', ''), fontsize=fontsize)
        self.draw_text(0.29, 0.30, self.label.get(
            '1010', ''), fontsize=fontsize)
        self.draw_text(0.39, 0.24, self.label.get(
            '1011', ''), fontsize=fontsize)
        self.draw_text(0.23, 0.59, self.label.get(
            '1100', ''), fontsize=fontsize)
        self.draw_text(0.61, 0.24, self.label.get(
            '1101', ''), fontsize=fontsize)
        self.draw_text(0.35, 0.50, self.label.get(
            '1110', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.38, self.label.get(
            '1111', ''), fontsize=fontsize)

        # legend
        self.draw_text(0.13, 0.18,
                       self.samples[0],
                       colors[0],
                       fontsize=fontsize,
                       ha="right")
        self.draw_text(0.18, 0.83,
                       self.samples[1],
                       colors[1],
                       fontsize=fontsize,
                       ha="right",
                       va="bottom")
        self.draw_text(0.82, 0.83,
                       self.samples[2],
                       colors[2],
                       fontsize=fontsize,
                       ha="left",
                       va="bottom")
        self.draw_text(0.87, 0.18,
                       self.samples[3],
                       colors[3],
                       fontsize=fontsize,
                       ha="left",
                       va="top")
        legend = self.axis.legend(self.samples, loc='center left',
                                  bbox_to_anchor=(1.0, 0.5), fancybox=True)
        legend.get_frame().set_alpha(0.5)

    def sample5(self):
        """
        Five sample venn
        """
        logging.info("5 Sample Venn Plot...")
        colors = [self.colors[i] for i in range(self.sample_num)]
        figsize = (13, 13)
        dpi = 96
        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        fontsize = 14

        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        self.axis.set_axis_off()
        self.axis.set_ylim(bottom=0.0, top=1.0)
        self.axis.set_xlim(left=0.0, right=1.0)

        # body
        self.draw_ellipse(0.428, 0.449, 0.87, 0.50, 155.0, colors[0])
        self.draw_ellipse(0.469, 0.543, 0.87, 0.50, 82.0, colors[1])
        self.draw_ellipse(0.558, 0.523, 0.87, 0.50, 10.0, colors[2])
        self.draw_ellipse(0.578, 0.432, 0.87, 0.50, 118.0, colors[3])
        self.draw_ellipse(0.489, 0.383, 0.87, 0.50, 46.0, colors[4])
        self.draw_text(0.27, 0.11, self.label.get(
            '00001', ''), fontsize=fontsize)
        self.draw_text(0.72, 0.11, self.label.get(
            '00010', ''), fontsize=fontsize)
        self.draw_text(0.55, 0.13, self.label.get(
            '00011', ''), fontsize=fontsize)
        self.draw_text(0.91, 0.58, self.label.get(
            '00100', ''), fontsize=fontsize)
        self.draw_text(0.78, 0.64, self.label.get(
            '00101', ''), fontsize=fontsize)
        self.draw_text(0.84, 0.41, self.label.get(
            '00110', ''), fontsize=fontsize)
        self.draw_text(0.76, 0.55, self.label.get(
            '00111', ''), fontsize=fontsize)
        self.draw_text(0.51, 0.90, self.label.get(
            '01000', ''), fontsize=fontsize)
        self.draw_text(0.39, 0.15, self.label.get(
            '01001', ''), fontsize=fontsize)
        self.draw_text(0.42, 0.78, self.label.get(
            '01010', ''), fontsize=fontsize)
        self.draw_text(0.50, 0.15, self.label.get(
            '01011', ''), fontsize=fontsize)
        self.draw_text(0.67, 0.76, self.label.get(
            '01100', ''), fontsize=fontsize)
        self.draw_text(0.70, 0.71, self.label.get(
            '01101', ''), fontsize=fontsize)
        self.draw_text(0.51, 0.74, self.label.get(
            '01110', ''), fontsize=fontsize)
        self.draw_text(0.64, 0.67, self.label.get(
            '01111', ''), fontsize=fontsize)
        self.draw_text(0.10, 0.61, self.label.get(
            '10000', ''), fontsize=fontsize)
        self.draw_text(0.20, 0.31, self.label.get(
            '10001', ''), fontsize=fontsize)
        self.draw_text(0.76, 0.25, self.label.get(
            '10010', ''), fontsize=fontsize)
        self.draw_text(0.65, 0.23, self.label.get(
            '10011', ''), fontsize=fontsize)
        self.draw_text(0.18, 0.50, self.label.get(
            '10100', ''), fontsize=fontsize)
        self.draw_text(0.21, 0.37, self.label.get(
            '10101', ''), fontsize=fontsize)
        self.draw_text(0.81, 0.37, self.label.get(
            '10110', ''), fontsize=fontsize)
        self.draw_text(0.74, 0.40, self.label.get(
            '10111', ''), fontsize=fontsize)
        self.draw_text(0.27, 0.70, self.label.get(
            '11000', ''), fontsize=fontsize)
        self.draw_text(0.34, 0.25, self.label.get(
            '11001', ''), fontsize=fontsize)
        self.draw_text(0.33, 0.72, self.label.get(
            '11010', ''), fontsize=fontsize)
        self.draw_text(0.51, 0.22, self.label.get(
            '11011', ''), fontsize=fontsize)
        self.draw_text(0.25, 0.58, self.label.get(
            '11100', ''), fontsize=fontsize)
        self.draw_text(0.28, 0.39, self.label.get(
            '11101', ''), fontsize=fontsize)
        self.draw_text(0.36, 0.66, self.label.get(
            '11110', ''), fontsize=fontsize)
        self.draw_text(0.51, 0.47, self.label.get(
            '11111', ''), fontsize=fontsize)

        # legend
        self.draw_text(0.02, 0.72,
                       self.samples[0],
                       colors[0],
                       fontsize=fontsize,
                       ha="right")
        self.draw_text(0.72, 0.94,
                       self.samples[1],
                       colors[1],
                       fontsize=fontsize,
                       va="bottom")
        self.draw_text(0.97, 0.74,
                       self.samples[2],
                       colors[2],
                       fontsize=fontsize,
                       ha="left")
        self.draw_text(0.88, 0.05,
                       self.samples[3],
                       colors[3],
                       fontsize=fontsize,
                       ha="left")
        self.draw_text(0.12, 0.05,
                       self.samples[4],
                       colors[4],
                       fontsize=fontsize,
                       ha="right")
        legend = self.axis.legend(
            self.samples, loc='center left', bbox_to_anchor=(1.0, 0.5),
            fancybox=True)
        legend.get_frame().set_alpha(0.5)

    def sample6(self):
        """
        Six sample venn
        """
        logging.info("6 Sample Venn Plot...")
        colors = [self.colors[i] for i in range(self.sample_num)]
        figsize = (20, 20)
        dpi = 96
        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        fontsize = 14

        self.figure, self.axis = plt.subplots(figsize=figsize, dpi=dpi)
        self.axis.set_axis_off()
        self.axis.set_ylim(bottom=0.0, top=1.0)
        self.axis.set_xlim(left=0.0, right=1.0)

        # body
        # See https://web.archive.org/web/20040819232503/http://www.hpl.hp.com/techreports/2000/HPL-2000-73.pdf
        self.draw_triangle(0.637, 0.921, 0.649, 0.274, 0.188, 0.667, colors[0])
        self.draw_triangle(0.981, 0.769, 0.335, 0.191, 0.393, 0.671, colors[1])
        self.draw_triangle(0.941, 0.397, 0.292, 0.475, 0.456, 0.747, colors[2])
        self.draw_triangle(0.662, 0.119, 0.316, 0.548, 0.662, 0.700, colors[3])
        self.draw_triangle(0.309, 0.081, 0.374, 0.718, 0.681, 0.488, colors[4])
        self.draw_triangle(0.016, 0.626, 0.726, 0.687, 0.522, 0.327, colors[5])
        self.draw_text(0.212, 0.562, self.label.get('000001', ''),
                       fontsize=fontsize)
        self.draw_text(0.430, 0.249, self.label.get('000010', ''),
                       fontsize=fontsize)
        self.draw_text(0.356, 0.444, self.label.get('000011', ''),
                       fontsize=fontsize)
        self.draw_text(0.609, 0.255, self.label.get('000100', ''),
                       fontsize=fontsize)
        self.draw_text(0.323, 0.546, self.label.get('000101', ''),
                       fontsize=fontsize)
        self.draw_text(0.513, 0.316, self.label.get('000110', ''),
                       fontsize=fontsize)
        self.draw_text(0.523, 0.348, self.label.get('000111', ''),
                       fontsize=fontsize)
        self.draw_text(0.747, 0.458, self.label.get('001000', ''),
                       fontsize=fontsize)
        self.draw_text(0.325, 0.492, self.label.get('001001', ''),
                       fontsize=fontsize)
        self.draw_text(0.670, 0.481, self.label.get('001010', ''),
                       fontsize=fontsize)
        self.draw_text(0.359, 0.478, self.label.get('001011', ''),
                       fontsize=fontsize)
        self.draw_text(0.653, 0.444, self.label.get('001100', ''),
                       fontsize=fontsize)
        self.draw_text(0.344, 0.526, self.label.get('001101', ''),
                       fontsize=fontsize)
        self.draw_text(0.653, 0.466, self.label.get('001110', ''),
                       fontsize=fontsize)
        self.draw_text(0.363, 0.503, self.label.get('001111', ''),
                       fontsize=fontsize)
        self.draw_text(0.750, 0.616, self.label.get('010000', ''),
                       fontsize=fontsize)
        self.draw_text(0.682, 0.654, self.label.get('010001', ''),
                       fontsize=fontsize)
        self.draw_text(0.402, 0.310, self.label.get('010010', ''),
                       fontsize=fontsize)
        self.draw_text(0.392, 0.421, self.label.get('010011', ''),
                       fontsize=fontsize)
        self.draw_text(0.653, 0.691, self.label.get('010100', ''),
                       fontsize=fontsize)
        self.draw_text(0.651, 0.644, self.label.get('010101', ''),
                       fontsize=fontsize)
        self.draw_text(0.490, 0.340, self.label.get('010110', ''),
                       fontsize=fontsize)
        self.draw_text(0.468, 0.399, self.label.get('010111', ''),
                       fontsize=fontsize)
        self.draw_text(0.692, 0.545, self.label.get('011000', ''),
                       fontsize=fontsize)
        self.draw_text(0.666, 0.592, self.label.get('011001', ''),
                       fontsize=fontsize)
        self.draw_text(0.665, 0.496, self.label.get('011010', ''),
                       fontsize=fontsize)
        self.draw_text(0.374, 0.470, self.label.get('011011', ''),
                       fontsize=fontsize)
        self.draw_text(0.653, 0.537, self.label.get('011100', ''),
                       fontsize=fontsize)
        self.draw_text(0.652, 0.579, self.label.get('011101', ''),
                       fontsize=fontsize)
        self.draw_text(0.653, 0.488, self.label.get('011110', ''),
                       fontsize=fontsize)
        self.draw_text(0.389, 0.486, self.label.get('011111', ''),
                       fontsize=fontsize)
        self.draw_text(0.553, 0.806, self.label.get('100000', ''),
                       fontsize=fontsize)
        self.draw_text(0.313, 0.604, self.label.get('100001', ''),
                       fontsize=fontsize)
        self.draw_text(0.388, 0.694, self.label.get('100010', ''),
                       fontsize=fontsize)
        self.draw_text(0.375, 0.633, self.label.get('100011', ''),
                       fontsize=fontsize)
        self.draw_text(0.605, 0.359, self.label.get('100100', ''),
                       fontsize=fontsize)
        self.draw_text(0.334, 0.555, self.label.get('100101', ''),
                       fontsize=fontsize)
        self.draw_text(0.582, 0.397, self.label.get('100110', ''),
                       fontsize=fontsize)
        self.draw_text(0.542, 0.372, self.label.get('100111', ''),
                       fontsize=fontsize)
        self.draw_text(0.468, 0.708, self.label.get('101000', ''),
                       fontsize=fontsize)
        self.draw_text(0.355, 0.572, self.label.get('101001', ''),
                       fontsize=fontsize)
        self.draw_text(0.420, 0.679, self.label.get('101010', ''),
                       fontsize=fontsize)
        self.draw_text(0.375, 0.597, self.label.get('101011', ''),
                       fontsize=fontsize)
        self.draw_text(0.641, 0.436, self.label.get('101100', ''),
                       fontsize=fontsize)
        self.draw_text(0.348, 0.538, self.label.get('101101', ''),
                       fontsize=fontsize)
        self.draw_text(0.635, 0.453, self.label.get('101110', ''),
                       fontsize=fontsize)
        self.draw_text(0.370, 0.548, self.label.get('101111', ''),
                       fontsize=fontsize)
        self.draw_text(0.594, 0.689, self.label.get('110000', ''),
                       fontsize=fontsize)
        self.draw_text(0.579, 0.670, self.label.get('110001', ''),
                       fontsize=fontsize)
        self.draw_text(0.398, 0.670, self.label.get('110010', ''),
                       fontsize=fontsize)
        self.draw_text(0.395, 0.653, self.label.get('110011', ''),
                       fontsize=fontsize)
        self.draw_text(0.633, 0.682, self.label.get('110100', ''),
                       fontsize=fontsize)
        self.draw_text(0.616, 0.656, self.label.get('110101', ''),
                       fontsize=fontsize)
        self.draw_text(0.587, 0.427, self.label.get('110110', ''),
                       fontsize=fontsize)
        self.draw_text(0.526, 0.415, self.label.get('110111', ''),
                       fontsize=fontsize)
        self.draw_text(0.495, 0.677, self.label.get('111000', ''),
                       fontsize=fontsize)
        self.draw_text(0.505, 0.648, self.label.get('111001', ''),
                       fontsize=fontsize)
        self.draw_text(0.428, 0.663, self.label.get('111010', ''),
                       fontsize=fontsize)
        self.draw_text(0.430, 0.631, self.label.get('111011', ''),
                       fontsize=fontsize)
        self.draw_text(0.639, 0.524, self.label.get('111100', ''),
                       fontsize=fontsize)
        self.draw_text(0.591, 0.604, self.label.get('111101', ''),
                       fontsize=fontsize)
        self.draw_text(0.622, 0.477, self.label.get('111110', ''),
                       fontsize=fontsize)
        self.draw_text(0.501, 0.523, self.label.get('111111', ''),
                       fontsize=fontsize)

        # legend
        self.draw_text(0.674, 0.824, self.samples[0], colors[0],
                       fontsize=fontsize)
        self.draw_text(0.747, 0.751, self.samples[1], colors[1],
                       fontsize=fontsize)
        self.draw_text(0.739, 0.396, self.samples[2], colors[2],
                       fontsize=fontsize)
        self.draw_text(0.700, 0.247, self.samples[3], colors[3],
                       fontsize=fontsize)
        self.draw_text(0.291, 0.255, self.samples[4], colors[4],
                       fontsize=fontsize)
        self.draw_text(0.203, 0.484, self.samples[5], colors[5],
                       fontsize=fontsize)
        legend = self.axix.legend(self.samples, loc='center left',
                                  bbox_to_anchor=(1.0, 0.5), fancybox=True)
        legend.get_frame().set_alpha(0.5)

    def draw_ellipse(self, x, y, w, h, a, fillcolor):
        e = patches.Ellipse(
            xy=(x, y),
            width=w,
            height=h,
            angle=a,
            color=fillcolor)
        self.axis.add_patch(e)

    def draw_triangle(self, x1, y1, x2, y2, x3, y3, fillcolor):
        xy = [
            (x1, y1),
            (x2, y2),
            (x3, y3),
        ]
        polygon = patches.Polygon(
            xy=xy,
            closed=True,
            color=fillcolor)
        self.axis.add_patch(polygon)

    def draw_text(self, x, y, text, color=[0, 0, 0, 1], fontsize=14,
                  ha="center", va="center"):
        self.axis.text(
            x, y, text,
            horizontalalignment=ha,
            verticalalignment=va,
            fontsize=fontsize,
            color="black")


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option('-o', '--out',
              default="./",
              show_default=True,
              type=click.Path(),
              help="The output dir")
@click.option('--weight/--no-weight',
              default=False,
              show_default=True,
              help="The output prefix")
def cli(input, out, weight):
    """
    A tool for Venn Plot.
    Only support 2 to 6 samples

    TODO
    - weight or unweight
    """
    logging.info(f'Parse the input {input}')
    df = pd.read_csv(input, sep='\t', header=0)
    samples = df.columns
    if len(samples) < 2:
        logging.error(f"Need 2 samples at least")
        sys.exit(1)
    elif len(samples) > 6:
        logging.error(f"Sample number should not more than 6")
        sys.exit(1)
    else:
        info = Venn()
        info.parse(df)
        info.plot()
        info.get_result(out)


if __name__ == "__main__":
    cli()
