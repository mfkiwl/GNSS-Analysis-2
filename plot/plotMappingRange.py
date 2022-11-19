from plotConfig import *
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as sgeom
from cartopy.geodesic import Geodesic
import cartopy.crs as ccrs
from sub_ionospheric_point import convert_coords
import datetime 
from build import paths
import json

def get_coords_from_sites(station, dat):

     coords = dat[station]["position"]
     obs_x, obs_y, obs_z = tuple(coords)
     
     lon, lat, alt = convert_coords(obs_x, obs_y, obs_z, 
                                    to_radians = False)
     
     return lon, lat
 
    
def square_area(ax, 
                   lat_min = -12, 
                   lat_max = -2, 
                   lon_max = -32, 
                   lon_min = -42, lw = 4):
    
    
    """Plotting square area by coords limits"""
    
    ax.plot([lon_min, lon_max, lon_max, lon_min, lon_min], 
            [lat_min, lat_min, lat_max, lat_max, lat_min],
             color='black', 
             linewidth = lw, 
             marker='.',
             transform=ccrs.PlateCarree(), 
             )
    return 



def plotStations(ax, 
                 date = datetime.date(2014, 1, 1), 
                 color = "green", 
                 markersize = 15, 
                 marker = "o",   
                 lat_min = -12, 
                 lat_max = -2, 
                 lon_max = -32, 
                 lon_min = -42):
    
   
    doy = date.strftime("%j")
    year = date.year
    
    path_json = paths(year, int(doy)).fn_json

    dat = json.load(open(path_json))
    

    stations = list(dat.keys())

    for station in stations:
            
        lon, lat = get_coords_from_sites(station, dat)
        
        
        if ((lat_min < lat < lat_max) and
            (lon_min < lon < lon_max)):
                        
            ax.plot(lon, lat, 
                    marker = marker, 
                    markersize = markersize, 
                    color = color)
            
            ax.text(lon + 0.15, lat, 
                    station.upper(), 
                    transform = ccrs.PlateCarree(), 
                    color = "k", 
                    fontsize = 30)

def circle_range(ax, longitude, latitude, 
                 radius = 500, color = "gray"):
             
    gd = Geodesic()

    cp = gd.circle(lon = longitude, 
                   lat = latitude, 
                   radius = radius * 1000.)
    
    geoms = [sgeom.Polygon(cp)]

    ax.add_geometries(geoms, crs=ccrs.PlateCarree(), 
                      edgecolor = 'black', color = color,
                      alpha = 0.2, label = 'radius')

def circle_with_legend(ax, angle, height, name, color,
                       marker = "s", infos = None, 
                       markersize = 30):
     
     radius = height * np.sin(np.radians(angle)) 
          
     if radius < 1:
         radius = 500
    
     if infos == None:
         infos = {"Cariri": [-36.55, -7.38], 
                  "Fortaleza": [-38.45, -3.9]}
     
     lon, lat = tuple(infos[name])

     circle_range(ax, lon, lat, radius = radius, 
                  color = color)
         
     ax.plot(lon, lat, marker = marker, label =  name, 
             color = color, markersize = markersize,
             transform = ccrs.PlateCarree())
     
     ax.legend(loc = "lower right")
 
    
def plot_range_stations(ax, 
                        angles = [180, 33], 
                        colors = ["red", "blue"], 
                        names = ["Cariri", "Fortaleza"], 
                        markers = ["s", "^"], 
                        markersize = 30):
    for num in range(2):
        
        angle = angles[num]
        name = names[num]
        color = colors[num]
        marker = markers[num]
       
        circle_with_legend(ax, angle, 250, 
                           name, color, marker, 
                           markersize = markersize)
        
        
def save(infile = "img/methods/InstrumentionLocations.png"):     
  
    plt.savefig(infile, dpi = 500, bbox_inches = "tight")
    
def main():   
    p = mapping(width = 15, heigth = 15, ncols = 1)
    
    fig, ax = p.subplots_with_map()
    
    
    p.mapping_attrs(ax, step_lat = 1, step_lon = 1,
                         lat_min = -12, lat_max = -2, 
                         lon_max = -32, lon_min = -42)
    
    
    plot_range_stations(ax)
    
        
    plotStations(ax)
    ax.legend(["Cariri \n (imageador)", 
               "Fortaleza \n (digissonda)", 
               "Receptores GNSS"], ncol = 3)
    plt.show()
    
