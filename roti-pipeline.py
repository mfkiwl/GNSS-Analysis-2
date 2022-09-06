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

def processed(infile, filename, rounded = False):
    
    
    df = pd.read_csv(infile + filename, 
                         delim_whitespace = True, 
                         index_col = "time")

    df.index = pd.to_datetime(df.index)
    
    df["lon"] = df["lon"] - 360
    
    if rounded:
        
        decimals = 0
        df["lon"] = df["lon"].apply(lambda x: round(x, decimals))
        df["lat"] = df["lat"].apply(lambda x: round(x, decimals))

    return df


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


def roti_by_prn(station_df):

    getting_roti = []

    for prn in create_prns():
        prn_df = station_df.loc[station_df.prn == prn, :]

        stec = prn_df.stec.values
        time = prn_df.index

        try:
            rot, rot_time, roti, roti_time = rot_and_roti(stec, time)
            droti = prn_df.loc[prn_df.index.isin(roti_time), ["lat", "lon"]]

            droti["roti"] = roti
            droti["prn"] = prn
            getting_roti.append(droti)

        except:
            print(f"{prn} doesn't have enough data")
            continue

    return pd.concat(getting_roti)

def roti_by_station(outside, elevation = 30):
    
    station_roti = []

    for num in range(len(outside)):

        station_df = outside[num]

        station_df = station_df.loc[(station_df.el > elevation), :]

        station_roti.append(roti_by_prn(station_df))
        
    return pd.concat(station_roti)

def avg_piercing_points(df_roti, 
                        coords,
                        step = 1, 
                        decimals = None):
    
    start_lon, end_lon, start_lat, end_lat = coords
                         
    lats = np.arange(start_lat, end_lat + step, step)
    lons = np.arange(start_lon, end_lon + step, step)

    ts = df_roti.copy()

    result = []
    for x in range(len(lons)):
        for y in range(len(lats)):

            dat = ts.loc[((ts.lon > lons[x]) & 
                         (ts.lon < lons[x] + step)) &
                         ((ts.lat > lats[y]) & 
                         (ts.lat < lats[y] + step)), 
                         ["lat", "lon", "roti"]]
            result.append(dat.mean().values)
            
    df = pd.DataFrame(result, columns = ["lat", "lon", "roti"]).dropna()
    
    if decimals is not None:
        
        df["lon"] = df["lon"].apply(lambda x: round(x, decimals))
        df["lat"] = df["lat"].apply(lambda x: round(x, decimals))
    
    return df




def main():
    year = 2014
    doy = 1
    
    
    infile = f"Database/all_process/{year}/{doy_str_format(doy)}/"
    
    
    _, _, files = next(os.walk(infile))
       
    
    result_list = [processed(infile, files[num]) for num in range(len(files))]

    df_roti = roti_by_station(result_list , elevation = 30)
    
    num = 3

    times = range_date(year, doy, freq = "10min")
    
    start_lat = -35
    end_lat = 5
    start_lon = -75
    end_lon = -30
    
    ipp_roti = avg_piercing_points(df_roti.loc[(df_roti.index > times[num]) & 
                                (df_roti.index < times[num + 1]), :], 
                                tuple((start_lon, end_lon, start_lat, end_lat)),
                                step = 0.5, 
                                decimals = None)

