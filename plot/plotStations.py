from sub_ionospheric_point import convert_coords
import json
from plot.plotConfig import *

def get_coords_from_sites(dat, station):
   
    
    positions = dat[station]["position"] 
    obs_x, obs_y, obs_z = tuple(positions)

    coords = convert_coords(obs_x, obs_y, obs_z, to_radians = False)
    lon, lat, alt = coords
    
    return lon, lat

def plotStations(ax,year = 2014, 
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
            
            
