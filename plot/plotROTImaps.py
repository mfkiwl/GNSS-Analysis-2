import os
import pandas as pd
import numpy as np
from build import paths
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import cartopy.feature as cf
import cartopy.crs as ccrs
import datetime
from utils import doy_str_format
from terminator import *
from __init__ import *
from tecmap import MapMaker
from scipy import interpolate
from tecmap import *



def maps_and_times(infile, 
                   morning = 7, 
                   evening = 21, 
                   delta = 10, 
                   lat_min = -30.0, 
                   lat_max = 10.0, 
                   lon_min = -70.0, 
                   lon_max = -10.0):
    
    df = pd.read_csv(infile, delim_whitespace = True)
    
    df.index = pd.to_datetime(df.index)
    dt = df.index[0].date()
    
    year, month, day = dt.year, dt.month, dt.day
    
    times = []
    roti_maps = []
    
    for hour in range(0, 24):
        for minute in range(0, 60, delta):
            if (hour > evening) or (hour < morning):
                
                times.append(datetime.datetime(year, month, day, 
                                               hour, minute, 0))
               
                
                roti_maps.append(make_maps(df, hour, minute, delta = delta, 
                                           lat_min = lat_min, lat_max = lat_max, 
                                           lon_min = lon_min, lon_max = lon_max))
            
    return times, roti_maps
        
      
        

def setting_states_map(ax, step_lat = 10, step_lon = 10,
                       lat_min = -30.0, lat_max = 10.0, 
                       lon_min = -70.0, lon_max = -10.0):    
    
    
    ax.set_global()

    ax.gridlines(color = 'grey', linestyle = '--', 
             crs=ccrs.PlateCarree())

    states_provinces = cf.NaturalEarthFeature(
                    category='cultural',
                    name='admin_1_states_provinces_lines',
                    scale='50m',
                    facecolor='none')


    ax.add_feature(states_provinces, edgecolor='black')
    ax.add_feature(cf.COASTLINE, edgecolor='black', lw = 2) 
    ax.add_feature(cf.BORDERS, linestyle='-', edgecolor='black')

    ax.set(ylabel = 'Latitude (°)', xlabel = 'Longitude (°)')
    

    ax.set_extent([lon_min, lon_max, lat_min, lat_max], 
                  crs=ccrs.PlateCarree())

    ax.set_xticks(np.arange(lon_min, lon_max + step_lat, step_lon), 
                              crs=ccrs.PlateCarree()) 

    ax.set_yticks(np.arange(lat_min, lat_max + step_lat, step_lat), 
                  crs=ccrs.PlateCarree())
    



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
    
    #print(len(yy), len(xx))
    img = ax.contourf(xx, yy, tecmap, levels = levels, cmap = "jet")
    #lon, lat = np.meshgrid(xx, yy)
    #levels = 50
    #img = ax.contourf(lon, lat, tecmap, levels = levels, cmap = "jet")

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

year = 2014
doy = 1
infile = f"Database/roti/{year}/{doy_str_format(doy)}.txt"
times, roti_maps = maps_and_times(infile, morning = 7, evening = 20, delta = 5) 

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

