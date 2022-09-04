import os
import time
from utils import doy_str_format, get_paths, date_from_doy
import datetime
import pandas as pd
import numpy as np

def range_date(year, doy, freq = "10min"):
    
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 45)

    date = date_from_doy(year, doy)

    start = datetime.datetime.combine(date, stime)
    end = datetime.datetime.combine(date, etime)
    return pd.date_range(start = start, end = end, freq = freq)

def read_all_processed(year, doy):
    
    infile = f"Database/all_process/{year}/{doy_str_format(doy)}/"

    _, _, files = next(os.walk(infile))
    
    out = []

    for filename in files:

        df = pd.read_csv(infile + filename, 
                         delim_whitespace = True, 
                         index_col = "time")

        df.index = pd.to_datetime(df.index)

        df["lon"] = df["lon"] - 360

        out.append(df)
        
    return pd.concat(out)


def getting_values(ts, 
                   start_lat, end_lat, 
                   start_lon, end_lon, 
                   step = 1):
    
    
    lats = np.arange(start_lat, end_lat + step, step)
    lons = np.arange(start_lon, end_lon + step, step)
    
    xsize = len(lons)
    ysize = len(lats)
    
    arr = np.zeros((xsize, ysize))
    
    for x in range(xsize):
        for y in range(ysize):

            data = ts.loc[((ts.lon > lons[x]) & 
                           (ts.lon < lons[x] + step)) &
                           ((ts.lat > lats[y]) & 
                        (ts.lat < lats[y] + step)), 
                        "stec"]
            
            arr[x, y] = data.mean()
            
    return lons, lats, arr

def interpolate(arr, start_lat, end_lat,
                start_lon, end_lon, step = 0.2):
    
    x = np.arange(start_lat, end_lat + step, step)
    y = np.arange(start_lon, end_lon + step, step)
    #mask invalid values

    array = arr.copy()
    array = np.ma.masked_invalid(array)
    xx, yy = np.meshgrid(x, y)
    x1 = xx[~array.mask]
    y1 = yy[~array.mask]

    newarr = array[~array.mask]

    return interpolate.griddata((x1, y1), newarr.ravel(),
                                (xx, yy),
                                 method='linear')



def main():
    year = 2014
    doy = 1
    
            
    adf = read_all_processed(year, doy)
    
    
    times = range_date(year, doy)