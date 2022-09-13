from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import get_cdb_value
import pandas as pd
from utils import doy_str_format, create_prns
import time
import json
import os
from build import build_paths

def process_data(year:int, 
                 doy: int,
                 station: str,
                 obs: list,
                 prn: str) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    and compute other variables
    """
    path = build_paths(year, doy)
    
    path_tec = path.fn_process(station)
    path_orbit = path.fn_orbit()
    path_dcb = path.fn_dcb()
     
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
    
    path_to_save = build_paths(year, doy).fn_all_process(station)
    
    for prn in create_prns():
        try: 
            result.append(process_data(year, doy, station, positions, prn))
        except:
            continue
            print(f"The {prn} doesnt work!")
    
    df = pd.concat(result)
    
    if save:
        df.to_csv(path_to_save, sep = " ", index = True)
        
    return df

def main():
    start_time = time.time()
    
    
    year = 2022
    doy = 1
    ext = str(year)[-2:]
    
    path = build_paths(year, doy)
    
    json_path = open(f'Database/json/stations{ext}.json')

    dat = json.load(json_path)
    
    _, _, files = next(os.walk(path.process))
    
    files = files[:1]
    
    for num, filename in enumerate(files):
    
        station = filename[:4]
            
        positions = dat[station]["position"]
   
        df = run_for_all_prns(year, doy, station, positions, save = True)
        
        #df = process_data(year, doy, station, positions, "G01")
        print(df)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
main()

