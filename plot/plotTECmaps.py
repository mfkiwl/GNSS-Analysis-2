import os
import pandas as pd
import numpy as np
from plotConfig import *
import datetime
from scipy import interpolate
from gnss_utils import tec_fname
from mpl_toolkits.axes_grid1.inset_locator import inset_axes



    
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

def plotTECmap(ax, tecInfile, tecFilename, step = 10):
    
    p = plotting()


    load_data_and_contourf(ax, tecInfile + tecFilename)

    date = tec_fname(tecFilename)
    ax.set(title = date)

    step = 10
    p.setting_states_map(ax, step_lat = step, step_lon = step,
                         lat_min = -40.0, lat_max = 10.0, 
                         lon_min = -80.0, lon_max = -30.0)

    p.equator(ax)
    p.terminator(ax, date)


    infos = {"Cariri": [-36.55, -7.38], 
             "Fortaleza": [-38.45, -3.9]}

    angles =  [180, 33]
    colors = ["red", "black"]
    names = list(infos.keys())
    markers = ["s", "^"]

    for num in range(2):
        
        angle = angles[num]
        name = names[num]
        color = colors[num]
        marker = markers[num]
        circle_with_legend(ax, angle, 250, name, color, infos, marker)
        
        

    ax.plot([-42, -32, -32, -42, -42], [-12, -12, -2, -2, -12],
             color='black', linewidth = 3, marker='.',
             transform=ccrs.PlateCarree(), #remove this line to get straight lines
             )
    
def main():

    fig, ax = p.subplots_with_map(width = 10, heigth = 10, ncols = 1)
    
    tecInfile = "C:\\TEC_2014\\TEC_2014_01\\"
    
    
    _, _, tec_files = next(os.walk(tecInfile))
    
    tecFilename = tec_files[0]
    
    plotTECmap(ax, tecInfile, tecFilename)
    
    


