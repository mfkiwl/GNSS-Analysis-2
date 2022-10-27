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



def load_slant_tec(path,
                   prn, 
                   station) -> pd.DataFrame:
    
    """Read processed STEC data"""
    
    tec_path = path.fn_process(station)
    
    tec = pd.read_csv(tec_path, 
                      delimiter = ";", 
                      index_col = "time")

    tec.index = pd.to_datetime(tec.index)
    
    return tec.loc[:, [prn]].dropna()

def join_data(path: str,
              prn: str,
              station: str) -> pd.DataFrame:
    
    """
    Concat the relative TEC for each piercing point 
    for one single PRN
    """
    
    tec = load_slant_tec(path, prn, station)
        
    ipp = piercing_points_data(path, station, prn)
        
    df = tec.join(ipp).interpolate().ffill().bfill()

    df.rename(columns = {prn : "stec"}, inplace = True)

    df['prn'] = prn
        
    df.columns.names = [station]
    
    return df



def get_prns(path, station)-> pd.DataFrame:

    path_prns = path.prns
    
    df = pd.read_csv(path_prns)
    
    return df.loc[:, station].values


def compute_roti(path, 
                 prn,
                 station, 
                 elevation = 30) -> pd.DataFrame:
    
    tec = join_data(path, prn, station)
    
    
    df1 = tec.loc[tec.el > elevation, :]
    
    stec = df1.stec.values
    time = df1.index
    
    dtime, droti = roti(stec, time)
    
    new_dat = df1.loc[df1.index.isin(dtime), 
                            ["lat", "lon", "el"]]
    
    new_dat["roti"] = droti
    
    new_dat["prn"] = prn
    
    return new_dat

def run_for_all_prns(path, station):

    prns = get_prns(path, station)
    
    dat_all_prns = []
    
    for prn in tqdm(prns, desc = station):
        try:
            dat_all_prns.append(compute_roti(path, prn, station))           
        except Exception:
            continue
    
    df = pd.concat(dat_all_prns)
    
    df["station"] = station
    
    return df


def run_for_all_stations(path, save = True):
    
    
    _, _, files = next(os.walk(path.process))
    
    all_stations = []
        
    for filename in files:
        station = filename[:4]
        
        all_stations.append(run_for_all_prns(path, station))
    
     
    df = pd.concat(all_stations)
    
    if save:
        df.to_csv(path.fn_roti, sep = ";", index = True)

    return df


def run_for_all_days(year:str, 
                     root:str, 
                     start:int = 1, 
                     end:int = 365):
    
    
    for doy in range(start, end + 1):
        
        try:
            print("starting...", doy)
            path = paths(year, doy, root = root)
            
            run_for_all_stations(path)
            
        except Exception:
            continue
         
start_time = time.time()

year = 2014
root = "D:\\"
doy = 1
#run_for_all_days(year, root)
path = paths(year, doy, root = root)
#run_for_all_stations(path, year, doy)
print(path.fn_orbit(const = "igl"))

print("--- %s hours ---" % ((time.time() - start_time) / 3600))


