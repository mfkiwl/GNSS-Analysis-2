import os
import pandas as pd
import numpy as np
from plot.plotConfig import *
import datetime
from scipy import interpolate
from utils import tec_fname
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def time_labels(ax, date, y = 1.0, x2 = 0.7, x1 = 0.1, fontsize = 18):

    ax.text(x1, y, date.date(), 
            rotation_mode='anchor', 
            transform=ax.transAxes, 
            fontsize = fontsize)

    ax.text(x2, y, f"{str(date.time())} UT", 
            rotation_mode='anchor', 
            transform=ax.transAxes, 
            fontsize = fontsize)
    
    
def load_data_and_contourf(ax, infile, step = 5, 
                           lat_min = -40.0, lat_max = 10.0, 
                           lon_min = -80.0, lon_max = -30.0):

    df = pd.read_csv(infile, delimiter = ';', 
                     header=None).replace(-1, np.nan)
    
    
    xmax, ymax = df.values.shape

    lat = np.arange(0, xmax)*0.5 - 60
    lon = np.arange(0, ymax)*0.5 - 90
    
    v = np.arange(0, 90 + step, step*0.5)
    img = ax.contourf(lon, lat, df.values, levels = v, cmap = 'jet')
    
    axins = inset_axes(ax,
                        width="3%",  # width: 5% of parent_bbox width
                        height="100%",  # height: 50%
                        loc="lower left",
                        bbox_to_anchor=(1.05, 0., 1, 1),
                        bbox_transform=ax.transAxes,
                        borderpad=0,
                        )
    
    cb = plt.colorbar(img, cax = axins) #position, name labels 
    
    cb.set_label(r'TEC ($10^{16} / m^2$)')

def plotTECmap(ax, tecInfile, tecFilename):
    
    p = plotting()
    
    load_data_and_contourf(ax, tecInfile + tecFilename)
    
    date = tec_fname(tecFilename)
    time_labels(ax, date, y = 1.02, x2 = 0.7)
    
     
    p.setting_states_map(ax, step_lat = 5, step_lon = 5,
                         lat_min = -40.0, lat_max = 10.0, 
                         lon_min = -80.0, lon_max = -30.0)
    
    p.equator(ax)
    p.terminator(ax, date)
    
def main():

    fig, ax = p.subplots_with_map(width = 10, heigth = 10, ncols = 1)
    
    tecInfile = "C:\\TEC_2014\\TEC_2014_01\\"
    
    
    _, _, tec_files = next(os.walk(tecInfile))
    
    tecFilename = tec_files[0]
    
    plotTECmap(ax2, tecInfile, tecFilename)


