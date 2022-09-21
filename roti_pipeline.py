from ROTI import rot_and_roti
import os
import pandas as pd
from build import prns
import datetime
from load import load_all_process
from utils import doy_str_format

def compute_roti(df, prn, delta = "2.5min"):
    
    prn_el = df.loc[(df.prn == prn), :]
    
    dtec = prn_el["stec"] - prn_el["stec"].rolling(delta).mean()
    time = prn_el.index

    rot, rot_tstamps, roti, roti_time = rot_and_roti(dtec, time)

    roti_df = pd.DataFrame({"roti": roti, "prn": prn}, 
                           index = roti_time)

    coords = prn_el.loc[prn_el.index.isin(roti_time), ["lat", "lon", "el"]]
    
    return pd.concat([roti_df, coords], axis = 1)



def set_between(df, morning = 7, evening = 21):
    dt = df.index[0].date()

    year, month, day = dt.year, dt.month, dt.day
    
    start = datetime.datetime(year, month, day, evening, 0)
    
    end = datetime.datetime(year, month, day, morning, 0)
    
    return df.loc[(df.index > start) | (df.index < end), :]


def compute_roti_for_all_stations(year, 
                                  doy, 
                                  delta = '2.5min', 
                                  elevation = 30, 
                                  morning = 7, 
                                  evening = 21, 
                                  time_between = True):
    
    #infile = build_paths(year, doy).all_process
    
    infile = "Database/all_process/2014/001_test/"

    _, _, files = next(os.walk(infile))
    
    
    
    for filename in files:
        

        df = load_all_process(infile, filename)
    
        result = []
        
        for prn in prns().gps_and_glonass:
            try:

                result.append(compute_roti(df, prn, delta = delta))
            except:
                continue
            
        ds = pd.concat(result)
        
        ds.to_csv(f"Database/roti/{year}/001/{filename}", 
                  sep = " ", index = True)
        
        print(f"Station {filename[:4]} processed correctly")

    return 




def main():
    year = 2014
    doy = 1
    
    ds = compute_roti_for_all_stations(year, doy)    
    
    
main()


    
    