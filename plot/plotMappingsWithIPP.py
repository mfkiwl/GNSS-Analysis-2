from plotConfig import *
import cartopy.feature as cf
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import datetime

from plot.plotMappingRange import square_area




def load_roti(infile):
    df = pd.read_csv(infile, index_col = 0)
    df.index = pd.to_datetime(df.index)
    df["lon"] = df["lon"] - 360
    return df.loc[df.roti < 5]


def interval(df, 
             hour = 0, 
             minute = 0, 
             delta = 2):
    
    dt = df.index[0]
    
    yy, mm, dd = dt.year, dt.month, dt.day
    
    start = datetime.datetime(yy, mm, dd, hour, minute)
    end = start + datetime.timedelta(minutes = (minute + delta) - 1,
                             seconds = 59)
    
    return df.loc[(df.index >= start) & 
                  (df.index <= end)]


infile = "database/roti/2014/001.txt"

df = load_roti(infile)
hour = 21
minute = 0
df = interval(df, 
             hour = hour, 
             minute = minute)

p = mapping(width = 20, 
            heigth = 20,
            ncols = 1 )


fig, ax = p.subplots_with_map()

p.mapping_attrs(ax, 
                step_lat = 5, step_lon = 5,
                lat_min = -35, lat_max = 10, 
                lon_max = -30, lon_min = -80)

img = ax.scatter(df.lon, 
           df.lat, 
           c = df.roti, 
           s = 200, 
           cmap = "jet", 
           marker = "s", 
           vmin = 0, 
           vmax = 5)

ticks = np.arange(0, 6, 1)
colorbar_setting(img, ax, ticks)

square_area(ax, lw = 6)
p.equator(ax)

date = df.index[0].strftime("%d/%m/%Y") 


ax.set(title = f"{date}")
plt.show()

