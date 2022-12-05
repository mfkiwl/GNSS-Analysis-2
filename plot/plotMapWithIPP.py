import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
from plot.plotMappingRange import square_area
import plotConfig as p




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




def plotMappingIPP(df, hour, minute):
   
    
    map = p.mapping(width = 20, 
                heigth = 20,
                ncols = 1 )
    
    
    fig, ax = map.subplots_with_map()
    
    map.mapping_attrs(ax, 
                    step_lat = 10, step_lon = 10,
                    lat_min = -35, lat_max = 5, 
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
    p.colorbar_setting(img, ax, ticks)
    
    square_area(ax, lw = 6)

    map.equator(ax)
    
    date = df.index[0].strftime("%d/%m/%Y") 
    time = datetime.time(hour, minute).strftime("%H:%M")
    
    ax.set(title = f"{date} {time} (UT)")
    plt.show()
    
    return fig



def choose_a_time(infile:str, 
                  hour:int = 21, 
                  minute:int = 0, 
                  save:bool = False)-> plt.figure:
   
    """
    
    """
    
    df = interval(load_roti(infile), 
                   hour = hour, 
                   minute = minute)
    
    
    fig = plotMappingIPP(df, hour, minute)
    
    if save:
        fig.savefig(f"{hour}{minute}.png", dpi = 100)
        
    return fig
        
def main():  
    
    
    for day, hour in zip([1, 2, 2, 2], 
                         [21, 1, 3, 7]):
        
        infile = f"database/roti/2014/00{day}.txt"
        choose_a_time(infile, hour = hour, minute = 0, save = True)
    
main()