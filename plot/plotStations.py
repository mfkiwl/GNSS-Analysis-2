

from sub_ionospheric_point import convert_coords
import matplotlib.pyplot as plt
from mapping import plotMapping
import json

path_json = 'Database/json/stations.json'


f = open(path_json)
dat = json.load(f)

stations = list(dat.keys())

start_lat = -35
end_lat = 5
start_lon = -75
end_lon = -30

fig, ax = plotMapping(start_lat = start_lat, 
                     start_lon = start_lon, 
                     end_lat = end_lat,
                     end_lon = end_lon)

for station in stations:
    positions = dat[station]["position"] 
    obs_x, obs_y, obs_z = tuple(positions)

    coords = convert_coords(obs_x, obs_y, obs_z, to_radians = False)
    lon, lat, alt = coords
    
    ax.plot(lon, lat, "s", markersize = 7, color = "red")
    
    
ax.legend(["RBMC"])

plt.show()