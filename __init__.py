# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 13:55:16 2022

@author: Luiz
"""

from load import *
from constants import *
from cycle_slips import *
from dcb_calculator import *
from sub_ionospheric_point import *
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 14, 
                     'axes.linewidth' : 0.5,
                     'grid.linewidth' : 0.5,
                     'lines.linewidth' : 1.,
                     'legend.frameon' : False,
                     'savefig.bbox' : 'tight',
                     'savefig.pad_inches' : 0.05,
                     'mathtext.fontset': 'dejavuserif', 
                     'font.family': 'serif', 
                     'ytick.direction': 'in',
                     'ytick.minor.visible' : True,
                     'ytick.right' : True,
                     'ytick.major.size' : 3,
                     'ytick.major.width' : 0.5,
                     'ytick.minor.size' : 1.5,
                     'ytick.minor.width' : 0.5,
                     'xtick.direction' : 'in',
                     'xtick.major.size' : 3,
                     'xtick.major.width': 0.5,
                     'xtick.minor.size' : 1.5,
                     'xtick.minor.width' : 0.5,
                     'xtick.minor.visible' : True,
                     'xtick.top' : True,
                     'axes.prop_cycle' : plt.cycler('color', ['#0C5DA5', '#00B945', '#FF9500', 
                                                              '#FF2C00', '#845B97', '#474747', '#9e9e9e'])
                         })   