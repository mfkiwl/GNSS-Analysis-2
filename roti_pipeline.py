from build import build_paths
from ROTI import rot_and_roti
from tecmap import *
import os
import pandas as pd
from utils import create_prns
import datetime


    
def compute_roti_for_all_stations(year, doy, delta = '2.5min'):
    
    infile = build_paths(year, doy).all_process

    _, _, files = next(os.walk(infile))
    
    result = []
    
    for filename in files:

        df = pd.read_csv(os.path.join(infile, filename), 
                         delim_whitespace = True, 
                         index_col = "time")

        df.index = pd.to_datetime(df.index)
        

        df["lon"] = df["lon"] - 360

        for prn in create_prns():
            try:
                prn_el = df.loc[(df.prn == prn) & (df.el > 30), :]

                dtec = prn_el["stec"] - prn_el["stec"].rolling(delta).mean()
                time = prn_el.index
                
                rot, rot_tstamps, roti, roti_time = rot_and_roti(dtec, time)
                
                roti_df = pd.DataFrame({"roti": roti, "prn": prn}, 
                                       index = roti_time)
               
                coords = prn_el.loc[prn_el.index.isin(roti_time), 
                                    ["lat", "lon"]]
                
                result.append(pd.concat([roti_df, coords], axis = 1))
            except:
                print(f"PRN: {prn} doesn`t works.")
                continue

    return pd.concat(result)


def make_maps(year, doy, hour, minute):
    """Separe the data in specifics time range for construct the TEC MAP"""
    ds = compute_roti_for_all_stations(year, doy)

    dt = ds.index[0].date()

    year, month, day = dt.year, dt.month, dt.day

    start = datetime.datetime(year, month, day, hour, minute , 0)
    end = datetime.datetime(year, month, day, hour, minute + 9, 59)

    res = ds.loc[(ds.index >= start) & (ds.index <= end)]

    lat_list = res.lat.values
    lon_list = res.lon.values
    roti_list = res.roti.values
    prn_list = res.prn.values

    tec_matrix, rms_tec = MapMaker.generate_matrix_tec(lat_list, lon_list, roti_list, 
                                                        prn_list, -1)
    
    return MapMaker.full_binning(tec_matrix, -1)

def main():
    year = 2022
    doy = 1
    
    hour = 0
    minute = 0

    tecmap = make_maps(year, doy, hour, minute)
    
    print(tecmap)
    
main()