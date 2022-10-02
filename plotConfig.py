import matplotlib.pyplot as plt
import matplotlib.dates as dates
import cartopy.feature as cf
import cartopy.crs as ccrs
import numpy as np
import json
import pandas as pd
from scipy import interpolate
import terminator as tr
from sub_ionospheric_point import convert_coords
import json

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
                     'axes.prop_cycle' : plt.cycler('color', 
                                                    ['#0C5DA5', '#00B945', '#FF9500', 
                                                     '#FF2C00', '#845B97', '#474747', 
                                                     '#9e9e9e'])
                         })   
    
class plotting(object):
    
    """Plotting a map with cartopy"""
    
    @staticmethod
    def subplots_with_map(nrows = 1, ncols = 2, heigth = 15, width = 8):
        
        fig, ax = plt.subplots(figsize = (heigth, width), 
                               ncols = ncols, 
                               nrows = nrows, 
                               subplot_kw={'projection': ccrs.PlateCarree()})
        
        
        return fig, ax
    
    @staticmethod
    def setting_states_map(ax, 
                           step_lat = 10, 
                           step_lon = 10,
                           lat_min = -40.0, 
                            lat_max = 10.0, 
                            lon_min = -80.0, 
                            lon_max = -30.0):    
        
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

        ax.set_xticks(np.arange(lon_min, lon_max + step_lon, step_lon), 
                                  crs=ccrs.PlateCarree()) 

        ax.set_yticks(np.arange(lat_min, lat_max + step_lat, step_lat), 
                      crs=ccrs.PlateCarree())
    
    @staticmethod
    def equator(ax, infile = "G://My Drive//Python//data-analysis//GNSS//database//geo//Inclination2021.txt"):
        eq = pd.read_csv(infile, 
                         delim_whitespace = True)
        
        eq = pd.pivot_table(eq, columns = "lon", index = "lat", values = "B")
        
        cs = ax.contour(eq.columns, eq.index, eq.values, 1, 
                   linewidths = 3, colors = "red", 
                    transform = ccrs.PlateCarree())
        
        cs.cmap.set_over('red')
        
        
    @staticmethod
    def terminator(ax, date, angle = 18):
        
        a_lon_term, a_lat_term = tr.terminator(date, 18)
    
        x = np.array(a_lon_term) 
        y = np.array(a_lat_term)
        f = interpolate.interp1d(x, y, fill_value="extrapolate")
        
        xnew = np.arange(-180, 180, 1)
        ynew = f(xnew)
        ax.plot(xnew, ynew,  "--", color = "k", lw = 3)
    
    




def plotStations(ax, year = 2014, 
             doy = 1, 
             color = "green", 
             markersize = 15, 
             marker = "o",   
             lat_min = -12, lat_max = -2, lon_max = -32, lon_min = -42):
    
    
    path_json = f'Database/json/{year}/001.json'

    dat = json.load(open(path_json))

    stations = list(dat.keys())

    for station in stations:
        
        
        lon, lat = get_coords_from_sites(station)
        
        if (lat_min < lat < lat_max) and (lon_min < lon < lon_max):
            
            ax.plot(lon, lat, marker = marker, markersize = markersize, color = color)
            
            ax.text(lon + 0.09, lat, station.upper(), 
                    transform = ccrs.PlateCarree(), color = "k")
            