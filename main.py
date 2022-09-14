from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import get_cdb_value
import pandas as pd
from utils import create_prns, create_directory
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
    for one single PRN
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



def run_for_all_prns(year: int, 
                     doy: int, 
                     station: str, 
                     positions: list, 
                     save: bool = True) -> pd.DataFrame:
    
    """Run for all prns and concatenate them"""

    result = []
    
    path_to_save = build_paths(year, doy).fn_all_process(station)
    
    for prn in create_prns():
        try: 
            result.append(process_data(year, doy, station, positions, prn))
        except:
            print(f"The {prn} doesnt work!")
            continue
            
    
    df = pd.concat(result)
    
    if save:
        df.to_csv(path_to_save, sep = " ", index = True)
        
    return df

def run_for_all_stations(year: int, doy: int):
    
    """Processed the data for all stations"""   
    path = build_paths(year, doy)
    
    path_created = create_directory(path.all_process)
    
    json_path = open(path.fn_json)

    dat = json.load(json_path)
    
    _, _, files = next(os.walk(path.process))
        
    for filename in files:
    
        station = filename[:4]
            
        positions = dat[station]["position"]
   
        df = run_for_all_prns(year, doy, station, positions, save = True)
        
        print(f"The station: {station} finishied")
    
    
    
def main():
    
   start_time = time.time()
    
   year = 2022
   
   for doy in range(2, 5):
       run_for_all_stations(year, doy)
   
   print("--- %s seconds ---" % (time.time() - start_time))
main()

