from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import get_cdb_value
import pandas as pd
from utils import get_paths, doy_str_format, create_prns
import time
import json
import os


def process_data(year:int, 
                 doy: int,
                 station: str,
                 obs: list,
                 prn: str) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    and compute other variables
    """

    path_tec, path_orbit, path_dcb = get_paths(year, doy, station)
     
    sat_bias = get_cdb_value(path_dcb, prn)

    tecData = relative_tec_data(path_tec, prn = prn)
      
    ippData = piercing_points_data(path_orbit, obs, prn = prn)
    
    df = tecData.join(ippData).interpolate(method = 
                                           'nearest').ffill().bfill()
    
    df["vtec"] = df["proj"] * df["stec"]
    
    df['prn'] = prn
    
    df["bias"] = sat_bias
    
    df.columns.names = [station]
    
    return df



def run_for_all_prns(year, doy, station, positions, save = True):
    
    """Run for all prns"""

    result = []
    
    for prn in create_prns():
        try: 
            result.append(process_data(year, doy, station, positions, prn))
        except:
            continue
            print(f"The {prn} doesnt work!")
    
    df = pd.concat(result)
    
    if save:
        df.to_csv(f"Database/all_process/{year}/{doy_str_format(doy)}/{station}.txt", 
                                  sep = " ", index = True)
    return df

def main():
    start_time = time.time()
    
    
    json_path = open('Database/json/stations.json')

    dat = json.load(json_path)
    
    year = 2014
    doy = 1
    
    infile = f"Database/process/{year}/{doy_str_format(doy)}/"
    _, _, files = next(os.walk(infile))
    
    
    for filename in files:
    
        station = filename[:4]
    
        positions = dat[station]["position"]
   
        df = run_for_all_prns(year, doy, station, positions, save = True)
        print(df)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
main()