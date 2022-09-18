from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from differentialCodeBias import get_cdb_value
import pandas as pd
import time
import json
import os
from build import paths, prns

def process_data(year: int, 
                 doy: int,
                 station: str,
                 prn: str, 
                 use_dcb: bool = False) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    for one single PRN
    """
    path = paths(year, doy)

    tec_path = f"001/{station}"

    tec = pd.read_csv(tec_path, delimiter = ";", index_col = "time")

    tec.index = pd.to_datetime(tec.index)
    tec = tec.loc[:, [prn]].dropna()

    dat = json.load(open(path.fn_json))

    positions = dat[station.replace(".txt", "")]["position"]
        
    ipp = piercing_points_data(year, doy, positions, prn = prn)
        
    df = tec.join(ipp).interpolate(method ='nearest').ffill().bfill()

    df.rename(columns = {prn : "stec"})

    df['prn'] = prn
        
    df.columns.names = [station]

    
    if use_dcb:
        path_dcb = path.fn_dcb()
             
        df["bias"] = get_cdb_value(path_dcb, prn)

    
    return df




def run_for_all_stations(year: int, doy: int):
    
    """Processed the data for all stations"""   
    path = paths(year, doy)
    
    path_created = create_directory(path.all_process)
    
    json_path = open(path.fn_json)

    dat = json.load(json_path)
    
    _, _, files = next(os.walk(path.process))
        
    for filename in files:
    
        station = filename[:4]
            
        positions = dat[station]["position"]
   
        #df = run_for_all_prns(year, doy, station, positions, save = True)
        
        print(f"The station: {station} finishied")
    
year = 2014
doy = 1



_, _, files = next(os.walk("001/"))

out = []
for station in files:
    for prn in prns().gps_and_glonass:
        try:
            out.append(process_data(year, doy, station, prn))
        except:
            continue
        
pd.concat(out).to_csv("test.txt", index = True, sep = " ")
print(len(out))