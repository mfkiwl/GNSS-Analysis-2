from iono_piercing_point import piercing_points_data
import pandas as pd
import time
import os
from build import paths, prns
from tec_rate import roti
import sys       
os.path.dirname(sys.executable)
from tqdm import tqdm



def load_slant_tec(path: str,
                   prn: str, 
                   station: str) -> pd.DataFrame:
    
    """Read processed STEC data"""
    
    tec_path = path.fn_process(station)
    
    try:
        tec = pd.read_csv(tec_path, 
                      delimiter = ",", 
                      index_col = "time")
    except:
        
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


def compute_roti(path: str, 
                 prn: str,
                 station: str, 
                 elevation: float = 30.0) -> pd.DataFrame:
    
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

def run_for_all_prns(path: str, 
                     station: str):

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


def run_for_all_stations(path: str, 
                         save: bool = True) -> pd.DataFrame:
    
    
    _, _, files = next(os.walk(path.process))
    
    all_stations = []
        
    for filename in files:
        station = filename[:4]
        
        all_stations.append(run_for_all_prns(path, station))
    
     
    df = pd.concat(all_stations)
    
    if save:
        df.to_csv(path.fn_roti, sep = ",", index = True)

    return df


def compute_for_prns(year: int = 2014,  
                     doy: int = 1, 
                     station: str =  "ceft"):
    


    path = paths(year, doy)
    out = []
    for prn in prns().gps_and_glonass:
        try:
            out.append(join_data(path,
                      prn,
                      station))
        except:
            continue
    
    df = pd.concat(out)
    
    df.to_csv(f"database/examples/{station}.txt", 
              sep = ",", 
              index = True)
    
    return df

def run_for_all_days(year: str, 
                     root: str, 
                     start: int = 1, 
                     end: int = 365):
    
    
    for doy in range(start, end + 1):
        
        try:
            print("starting...", doy)
            path = paths(year, doy, root = root)
            
            run_for_all_stations(path)
            
        except Exception:
            continue
        
        
def main():
         
    start_time = time.time()
    compute_for_prns(year = 2014,  
                 doy = 1, 
                 station = "ceft")
    print("--- %s hours ---" % ((time.time() - start_time) / 3600))


