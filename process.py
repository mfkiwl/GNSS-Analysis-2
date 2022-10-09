from sub_ionospheric_point import piercing_points_data
from differentialCodeBias import get_cdb_value
import pandas as pd
import time
import json
import os
from build import paths, prns, folder
from sub_ionospheric_point import convert_coords
from ROTI import rot_and_roti
from utils import doy_str_format
from tqdm import tqdm
import sys       
import os
os.path.dirname(sys.executable)
from pathlib import Path       




def load_slant_tec(year, doy, prn, root, station):
    
    tec_path = paths(year, doy, root).fn_process(station)
    
    tec = pd.read_csv(tec_path, 
                      delimiter = ";", 
                      index_col = "time")

    tec.index = pd.to_datetime(tec.index)
    
    return tec.loc[:, [prn]].dropna()

def join_data(year: int, 
              doy: int,
              station: str,
              prn: str, 
              root) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    for one single PRN
    """
    tec = load_slant_tec(year, doy, prn, root, station)
        
    ipp = piercing_points_data(year, doy, station, prn, root)
        
    df = tec.join(ipp).interpolate().ffill().bfill()

    df.rename(columns = {prn : "stec"}, inplace = True)

    df['prn'] = prn
        
    df.columns.names = [station]
    
    return df


def _get_coords_from_sites(dat, station):
    
    """Get coords and convert them"""
        
    positions = dat[station]["position"] 
    obs_x, obs_y, obs_z = tuple(positions)

    coords = convert_coords(obs_x, obs_y, obs_z, to_radians = False)
    lon, lat, alt = coords
    
    return lon, lat



year = 2014
doy = 1
lat_min = -12
lat_max = -2
lon_max = -32
lon_min = -42
limits = [lon_min, lon_max, lat_min, lat_max]




def _filter_stations_by_limits(year, doy, root, *args):
    
    """Use Json file with coords of each station and filter the region limits"""

    path_json = paths(year, doy, root).fn_json

    dat = json.load(open(path_json))

    stations = list(dat.keys())
    
    out_stations = []

    for station in stations:
        
        lon, lat = _get_coords_from_sites(dat, station)

        if (lat_min < lat < lat_max) and (lon_min < lon < lon_max):
            out_stations.append(station)
            
    return out_stations


def compute_roti(df, prn):
    
    prn_el = df.loc[(df.prn == prn), :]
    
    dtec = prn_el.stec.values
    time = prn_el.index

    rot, rot_tstamps, roti, roti_time = rot_and_roti(dtec, time)

    roti_df = pd.DataFrame({"roti": roti, 
                            "prn": prn}, 
                            index = roti_time)

    coords = prn_el.loc[prn_el.index.isin(roti_time), 
                        ["lat", "lon", "el"]]
    
    return pd.concat([roti_df, coords], axis = 1)






def process_for_all_stations(year, doy, root, *limits):

    stations = _filter_stations_by_limits(year, doy, root, *limits)
    
    
    out_all = []
    
    for station in stations:
        
        out_station = []
        
        for prn in tqdm(prns().gps_and_glonass, desc = station):
            try:
                df_tec = join_data(year, doy, station, prn, root)
    
                df_roti = compute_roti(df_tec, prn)
                 
                out_station.append(df_roti)
            except:
                print(prn, station)
                continue
        
        df1 = pd.concat(out_station)
        df1["station"] = station
        out_all.append(df1)
        
    df2 = pd.concat(out_all)
    df2.to_csv(f"database/roti2/{year}/{doy_str_format(doy)}.txt",
               index = True, sep = ";")
    
lat_min = -12
lat_max = -2
lon_max = -32
lon_min = -42



limits = [lon_min, lon_max, lat_min, lat_max]

def run_for_all_days(year = 2014, root = "C:\\Users\\Public\\", *limits):
   
    for doy in range(1, 366, 1):
        try:
            process_for_all_stations(year, doy, root, *limits)
        except:
            print("Doesnt work", doy)
            continue


