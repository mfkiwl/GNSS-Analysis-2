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

def make_maps(ds, hour, minute):
    """Separe the data in specifics time range for construct the TEC MAP"""
    

    dt = ds.index[0].date()

    year, month, day = dt.year, dt.month, dt.day

    start = datetime.datetime(year, month, day, hour, minute, 0)
    end = datetime.datetime(year, month, day, hour, minute + 9, 59)

    res = ds.loc[(ds.index >= start) & (ds.index <= end)]

    lat_list = res.lat.values
    lon_list = res.lon.values
    roti_list = res.roti.values
    prn_list = res.prn.values

    tec_matrix, rms_tec = MapMaker.generate_matrix_tec(lat_list, 
                                                       lon_list, 
                                                       roti_list, 
                                                       prn_list, -1)
    
    return MapMaker.full_binning(tec_matrix, -1)

def maps_and_times(infile, 
                   morning = 7, 
                   evening = 21, 
                   roti_maximum = 5):
    
    df = pd.read_csv(infile, delim_whitespace = True)
    
    df.index = pd.to_datetime(df.index)
    dt = df.index[0].date()
    
    year, month, day = dt.year, dt.month, dt.day
    
    times = []
    roti_maps = []
    for hour in range(0, 24):
        for minute in range(0, 60, 10):
            if (hour > evening) or (hour < morning):
                
                times.append(datetime.datetime(year, month, day, 
                                               hour, minute, 0))
                dat = df.loc[df.roti <= roti_maximum, :]
                
                roti_maps.append(make_maps(dat, hour, minute))
            
    return times, roti_maps
        
      
        

def setting_states_map(ax, LAT_MIN = -60.0, LAT_MAX = 40.0, 
                       LON_MIN = -120.0, LON_MAX = -20.0):    
    
    
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
    
    step_lat = 10
    step_lon = 10

    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], 
                  crs=ccrs.PlateCarree())

    ax.set_xticks(np.arange(LON_MIN, LON_MAX + step_lat, step_lon), 
                              crs=ccrs.PlateCarree()) 

    ax.set_yticks(np.arange(LAT_MIN, LAT_MAX + step_lat, step_lat), 
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

    yy = np.linspace(-60.0, 40.0, 200)
    xx = np.linspace(-120.0, -20.0, 200)


    lon, lat = np.meshgrid(xx, yy)

    img = ax.contourf(lon, lat, tecmap, 
                      levels = levels, cmap = "jet")

    cbar_ax = fig.add_axes([0.95, 0.12, 0.03, 0.75]) #xposition, yposition, espessura, altura

    cb = plt.colorbar(img, cax=cbar_ax, 
                      ticks= [0, 1, 2, 3, 4, 5])

    cb.set_label(r'ROTI (TECU/min)')

    setting_states_map(ax, LAT_MIN = -40, LAT_MAX = 10, LON_MIN=-80)

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
        do = int(doy_str_format(i)) #+ 144
        plt.savefig(f'img/maps/{do}.png', 
                    dpi = 80, bbox_inches="tight")
    else:
        plt.show()

year = 2014
doy = 1
infile = f"Database/roti/{year}/{doy_str_format(doy)}.txt"
times, roti_maps = maps_and_times(infile, morning = 7, evening = 21) 

for i in range(len(times)):
    plotROTImaps(i, save = True)
