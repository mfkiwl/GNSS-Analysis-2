import os
import pandas as pd
import numpy as np
from build import paths
from plotConfig import *
import datetime
from utils import doy_str_format
from terminator import *
from __init__ import *
from tecmap import MapMaker
from scipy import interpolate
from tecmap import *


def plotROTImaps(i, save = True):
    
    
    if save:
        plt.ioff()
        
        
    fig = plt.figure(figsize = (8, 8))
    ax = plt.axes(projection = ccrs.PlateCarree())
    
    tecmap = roti_maps[i]
    date = times[i]
    
    levels = np.linspace(0, 5, 50)
    tecmap = np.where(tecmap < 0, np.nan, tecmap)
    
    
    yy = np.linspace(-60.0, 40.0, tecmap.shape[1])
    xx = np.linspace(-120.0, -20.0, tecmap.shape[0])

    yy = np.arange(-30.0, 10.0, 0.5)
    xx = np.arange(-70.0, -10.0, 0.5)
    
    img = ax.contourf(xx, yy, tecmap, levels = levels, cmap = "jet")
 

    cbar_ax = fig.add_axes([0.95, 0.12, 0.03, 0.75]) #xposition, yposition, espessura, altura

    cb = plt.colorbar(img, cax=cbar_ax)
                      #ticks= [0, 1, 2, 3, 4, 5])

    cb.set_label(r'ROTI (TECU/min)')

    setting_states_map(ax)

    ax.set(title = date)

    a_lon_term, a_lat_term = terminator(date, 18)
    
    x = np.array(a_lon_term) 
    y = np.array(a_lat_term)
    f = interpolate.interp1d(x, y, fill_value="extrapolate")
    
    xnew = np.arange(-180, 180, 1)
    ynew = f(xnew)
    ax.plot(xnew, ynew,  "--", color = "k", lw = 3)
 
    da = pd.read_csv("mag_inclination_2021.txt", 
                     delim_whitespace = True)

    da = pd.pivot_table(da, values = "B", 
                        index = "lat", columns = "lon")

    ax.contour(da.columns, da.index, da.values, 1, 
               linewidths = 2, color = 'k',
                transform = ccrs.PlateCarree())
    
    if save:
        filename = str(date).replace("-", "").replace(" ", "").replace(":", "")
        plt.savefig(f'img/maps/{filename}.png', 
                    dpi = 80, bbox_inches="tight")
    else:
        plt.show()



"""
for i, time in enumerate(times):
    
    print(i, time)
    plotROTImaps(i, save = True)
    



print(roti_maps[110].max())

"""
#pd.DataFrame(roti_maps[1]).to_excel("test_roti.x")

plotROTImaps(110, save = False)


tecmap = roti_maps[110]
xsize, ysize = tecmap.shape
print(xsize, ysize)
tecmap = np.where(tecmap < 0, np.nan, tecmap)

