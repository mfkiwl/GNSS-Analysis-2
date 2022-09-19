from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from differentialCodeBias import get_cdb_value
import pandas as pd
import time
import json
import os
from build import paths, prns



def load_slant_tec(year, doy, station, prn):
    
    tec_path = f"001/{station}.txt"
    
    tec = pd.read_csv(tec_path, delimiter = ";", index_col = "time")

    tec.index = pd.to_datetime(tec.index)
    
    return tec.loc[:, [prn]].dropna()

def join_data(year: int, 
              doy: int,
              station: str,
              prn: str) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    for one single PRN
    """
    tec = load_slant_tec(year, doy, station, prn)
        
    ipp = piercing_points_data(year, doy, station, prn = prn)
        
    df = tec.join(ipp).interpolate(method ='nearest').ffill().bfill()

    df.rename(columns = {prn : "stec"}, inplace = True)

    df['prn'] = prn
        
    df.columns.names = [station]
    
    return df

def process_for_all_stations():
    year = 2014
    doy = 1
    
    _, _, files = next(os.walk("001/"))
    
    
    for filename in files:
        
        station = filename[:4]
        out_station = []
        for prn in prns().gps_and_glonass:
            try:
                out_station.append(join_data(year, doy, station, prn))
            except:
                continue
        
        dat = pd.concat(out_station)
        print(f"The station: {station} finished")
        dat.to_csv(f"Database/all_process/2014/001_test/{filename}",
                   index = True, sep = " ")
