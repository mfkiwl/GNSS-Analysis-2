# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 09:50:22 2022

@author: Luiz
"""
from main import example
import cartopy.feature as cf
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from load import *

def plotMapping(start_lat = -40, 
                end_lat = 15, 
                start_lon = -80, 
                end_lon = -20,
                step_lat = 5, 
                step_lon = 5):
    
    """Plotting a map with cartopy"""
    
    
    fig = plt.figure(figsize = (15, 12))
    ax = plt.axes(projection = ccrs.PlateCarree())
    
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
    
    
    ax.set_extent([start_lon, end_lon, start_lat, end_lat], 
              crs=ccrs.PlateCarree())
    
    ax.set_xticks(np.arange(start_lon, end_lon + step_lat, step_lon), 
                  crs=ccrs.PlateCarree()) 
    
    ax.set_yticks(np.arange(start_lat, end_lat + step_lat, step_lat), 
                  crs=ccrs.PlateCarree())

    return ax


obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067

obs = list((obs_x, obs_y, obs_z))
prn = "G01"
path_tec = "Database/alar0011.14o.txt"
path_orbit = "Database/jpl17733.sp3/igr17733.sp3"
    
    
df = pd.read_csv(path_tec, 
                 delim_whitespace = True, 
                 index_col = ["sv", "time"])

prns = observables(df).prns

ax =  plotMapping()


for prn in prns:
    
    if "G" in prn:

        df = concat_data(path_tec, path_orbit, 
                         obs, prn, 
                         time_for_interpol = None)

        ax.scatter(df.lon, df.lat, c = df.RTEC, 
                   s = 20, cmap = "jet")


