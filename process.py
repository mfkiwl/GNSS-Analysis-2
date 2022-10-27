from sub_ionospheric_point import piercing_points_data
import pandas as pd
import time
import os
from build import paths, folder
from rot_roti import roti
import sys       
import os
os.path.dirname(sys.executable)
from pathlib import Path       
from tqdm import tqdm
from gnss_utils import date_from_doy



def load_slant_tec(year, 
                   doy, 
                   prn, 
                   station, 
                   root = str(Path.cwd())):
    
    """Read processed STEC data"""
    
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
              root = str(Path.cwd())) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    for one single PRN
    """
    tec = load_slant_tec(year, doy, prn, station, root)
        
    ipp = piercing_points_data(year, doy, station, prn, root)
        
    df = tec.join(ipp).interpolate().ffill().bfill()

    df.rename(columns = {prn : "stec"}, inplace = True)

    df['prn'] = prn
        
    df.columns.names = [station]
    
    return df



def get_prns(year, station, doy):

    path_prns = paths(year, doy).prns
    
    df = pd.read_csv(path_prns)
    
    return df.loc[:, station].values


def compute_roti(year, doy, station, 
                 prn, elevation = 30):
    
    
    tec = join_data(year, doy, station, prn)
    
    
    df1 = tec.loc[tec.el > elevation, :]
    
    stec = df1.stec.values
    time = df1.index
    
    dtime, droti = roti(stec, time)
    
    new_dat = df1.loc[df1.index.isin(dtime), 
                            ["lat", "lon", "el"]]
    
    new_dat["roti"] = droti
    
    new_dat["prn"] = prn
    
    return new_dat

def run_for_all_prns(year, doy, station):

    prns = get_prns(year, station, doy)
    
    
    dat_all_prns = []
    for prn in tqdm(prns, desc = station):
        try:
            dat_all_prns.append(compute_roti(year, doy, station, 
                     prn))
            
        except:
            continue
    
    df = pd.concat(dat_all_prns)
    
    df["station"] = station
    
    return df


def run_for_all_stations(path, year, doy):
    
    
    _, _, files = next(os.walk(path.process))
    
    all_stations = []
        
    for filename in files:
        station = filename[:4]
        
        all_stations.append(run_for_all_prns(year, doy, station))
    
     
    df = pd.concat(all_stations)
        
    df.to_csv(path.fn_roti, sep = ";", index = True)

    


def run_for_all_days(year:str, 
                     root:str, 
                     start:int = 1, 
                     end:int = 365, 
                     save_prn:bool = True):
    
    prn_in_year = []
    
    for doy in range(start, end + 1):
        
        try:
            path = paths(year, doy, root = "C:\\")
            
            run_for_all_stations(path, year, doy)
            
        except:
            continue
         
start_time = time.time()

year = 2014
root = "D://"
run_for_all_days(year, root)


print("--- %s hours ---" % ((time.time() - start_time) / 3600))


