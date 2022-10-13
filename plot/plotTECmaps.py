import os
import pandas as pd
import numpy as np
from plotConfig import *
import datetime
from scipy import interpolate
from gnss_utils import tec_fname
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import plot.plotMappingRange as r 

    
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
    
    cb = plt.colorbar(img, cax = axins) 
    
    cb.set_label(r'TEC ($10^{16} / m^2$)')

def plotTECmap(ax, p, tecInfile, tecFilename, step = 5):
    

    load_data_and_contourf(ax, tecInfile + tecFilename)

    date = tec_fname(tecFilename)
    
    ax.set(title = date)

    p.mapping_attrs(ax, step_lat = step, step_lon = step,
                         lat_min = -40.0, lat_max = 10.0, 
                         lon_min = -80.0, lon_max = -30.0)

    p.equator(ax)
    p.terminator(ax, date)
    r.plot_range_stations(ax)
    r.plot_square_area(ax)
    


   
def main():
    
    p = mapping(width = 10, heigth = 10, ncols = 1)

    fig, ax = p.subplots_with_map()
    
    tecInfile = "C:\\TEC_2014\\TEC_2014_01\\"
    
    
    _, _, tec_files = next(os.walk(tecInfile))
    
    date = datetime.datetime(2014, 1, 1, 0, 0)
    tecFilename = [f for f in tec_files if tec_fname(f) ==
                   date][0]
    
    plotTECmap(ax, p, tecInfile, tecFilename, step = 20)
    

main()