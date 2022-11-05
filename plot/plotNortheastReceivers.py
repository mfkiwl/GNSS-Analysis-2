# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 20:23:57 2022

@author: Luiz
"""

from mapping import *

start_lat = -40
end_lat = 10
end_lon = -30
start_lon = -80
fig, ax = plotMapping(start_lat = start_lat, 
                end_lat = end_lat, 
                start_lon = start_lon, 
                end_lon = end_lon,
                step_lat = 5, 
                step_lon = 5)

num = 30
elevation = 0

sel_time = times[num]

df = adf.loc[(adf.index > sel_time) & 
             (adf.index < sel_time + delta) & 
             (adf.el > elevation), :]

ts = df.copy()

lons, lats, arr = getting_values(ts, 
               start_lat, end_lat, 
               start_lon, end_lon, 
               step = 1)

ax.contourf(lons, lats, arr, 50, cmap = "jet")

ax.set(title = str(sel_time))
plt.show()