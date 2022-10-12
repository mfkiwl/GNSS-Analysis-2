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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import shapely.geometry as sgeom
from cartopy.geodesic import Geodesic

plt.rcParams.update({'font.size': 12, 
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
    
class mapping(object):
    
    """Plotting a map with cartopy"""
    
    def __init__(self, nrows = 1, 
                        ncols = 1, 
                        heigth = 15, 
                        width = 8, 
                        ):
        
        self.heigth = heigth
        self.width = width
        self.ncols = ncols
        self.nrows = nrows
    
    
    def subplots_with_map(self, step_lat = 10, 
                                step_lon = 10,
                                lat_min = -40.0, 
                                lat_max = 10.0, 
                                lon_min = -80.0, 
                                lon_max = -30.0):
        
        fig, axs = plt.subplots(figsize = (self.heigth, self.width), 
                               ncols = self.ncols, 
                               nrows = self.nrows, 
                               subplot_kw = {'projection': ccrs.PlateCarree()})
        
    
        return fig, axs
    
    @staticmethod
    def mapping_attrs(ax, step_lat = 10, 
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
        """Plotting geomagnetic equator"""
        
        eq = pd.read_csv(infile, 
                         delim_whitespace = True)
        
        eq = pd.pivot_table(eq, columns = "lon", index = "lat", values = "B")
        
        cs = ax.contour(eq.columns, eq.index, eq.values, 1, 
                   linewidths = 3, colors = "red", 
                    transform = ccrs.PlateCarree())
        
        cs.cmap.set_over('red')
        
        
    @staticmethod
    def terminator(ax, date, angle = 18):
        """Plotting terminator line from datetime"""
        a_lon_term, a_lat_term = tr.terminator(date, 18)
    
        x = np.array(a_lon_term) 
        y = np.array(a_lat_term)
        f = interpolate.interp1d(x, y, 
                                 fill_value = "extrapolate")
        
        delta = 1
        lonmin = -180
        lonmax = 180
        
        xnew = np.arange(lonmin, 
                         lonmax + 0.5 * delta, delta,
                         dtype=np.float32)
        ynew = f(xnew)
        #ax.plot(xnew, ynew,  "--", color = "k", lw = 3)
        ax.plot(x, y,  "--", color = "k", lw = 3)
        
def text_painels(axs, x = 0.8, y = 0.8, fontsize = 14):
    """Plot text for enumerate painels by letter"""
    chars = list(map(chr, range(97, 123)))
    
    for num, ax in enumerate(axs.flat):
        char = chars[num]
        ax.text(x, y, f"({char})", 
                transform = ax.transAxes, 
                fontsize = fontsize)

    
    
def colorbar_setting(img, ax, ticks):
    
    """Color bar settings"""
    axins = inset_axes(
                ax,
                width="3%",  # width: 5% of parent_bbox width
                height="100%",  # height: 50%
                loc="lower left",
                bbox_to_anchor=(1.05, 0., 1, 1),
                bbox_transform=ax.transAxes,
                borderpad=0,
            )
    
    cb = plt.colorbar(img, cax = axins, ticks = ticks)
    
    cb.set_label(r'ROTI (TECU/min)')


 
def save(infile = "img/methods/InstrumentionLocations.png"):     
    """Save figure"""
    plt.savefig(infile, dpi = 500, bbox_inches = "tight")
    
def main():   
    p = mapping()
    
    #fig, ax = p.subplots_with_map()
    
    fig, ax = p.subplots_with_map(width = 15, heigth = 15, ncols = 1)
    
    p.setting_states_map(ax, step_lat = 1, step_lon = 1,
                         lat_min = -12, lat_max = -2, 
                         lon_max = -32, lon_min = -42)
    
    infos = {"Cariri": [-36.55, -7.38], 
             "Fortaleza": [-38.45, -3.9]}
    







            