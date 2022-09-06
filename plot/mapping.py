# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 09:50:22 2022

@author: Luiz
"""
import cartopy.feature as cf
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np


def plotMapping(start_lat = -40, 
                end_lat = 15, 
                start_lon = -80, 
                end_lon = -20,
                step_lat = 5, 
                step_lon = 5, 
                xsize = 12, 
                ysize = 10):
    
    """Plotting a map with cartopy"""
    
    
    fig = plt.figure(figsize = (xsize, ysize))
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

    return fig, ax




