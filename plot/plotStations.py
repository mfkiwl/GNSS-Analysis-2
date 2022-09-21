

from sub_ionospheric_point import convert_coords
import json



def plotStations(ax, year, color = "green", markersize = 5, marker = "o"):
    
    
    path_json = 'Database/json/2014/001.json'


    dat = json.load(open(path_json))

    stations = list(dat.keys())

    for station in stations:
        positions = dat[station]["position"] 
        obs_x, obs_y, obs_z = tuple(positions)
    
        coords = convert_coords(obs_x, obs_y, obs_z, to_radians = False)
        lon, lat, alt = coords
        
        ax.plot(lon, lat, marker = marker, markersize = markersize, color = color)
    