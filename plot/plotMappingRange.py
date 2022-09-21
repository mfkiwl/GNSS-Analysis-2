from plot.plotConfig import *
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as sgeom
from cartopy.geodesic import Geodesic

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

def circle_with_legend(ax, angle, height, name, color, marker = "s"):
     
     radius = height * np.sin(np.radians(angle)) 
          
     if radius < 1:
         radius = 500
     
     lon, lat = tuple(infos[name])

     circle_range(ax, lon, lat, radius = radius, 
                  color = color)
         
     ax.plot(lon, lat, marker = marker, label =  name, 
             color = color, markersize = 15,
             transform = ccrs.PlateCarree())
 
     #ax.text(lon, lat + (radius / 100), 
       #      f"h = {height} km (raio de {round(radius)} km)", 
       #      transform = ccrs.PlateCarree())
     

    
    
def salve():     
  
    plt.savefig("range.png", dpi = 500, bbox_inches = "tight")
    
    plt.show()
    
    
    
    
p = plotting()

fig, ax = p.subplots_with_map(xsize = 15, ysize = 15, ncols = 1)

p.setting_states_map(ax, step_lat = 1, step_lon = 1,
                     lat_min = -12, lat_max = -2, 
                     lon_max = -32, lon_min = -42)

infos = {"Cariri": [-36.55, -7.38], 
         "Fortaleza": [-38.45, -3.9]}

angles =  [180, 33]
colors = ["red", "blue"]
names = ["Cariri", "Fortaleza"]
markers = ["s", "^"]

for num in range(2):
    
    angle = angles[num]
    name = names[num]
    color = colors[num]
    marker = markers[num]
    circle_with_legend(ax, angle, 250, name, color, marker)
    
    
ax.legend(["Cariri \n (imageador)", 
           "Fortaleza \n (digissonda)"], ncol = 2)
