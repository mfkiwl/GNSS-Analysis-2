from sub_ionospheric_point import piercing_points_data
from differentialCodeBias import get_cdb_value
import pandas as pd
import time
import json
import os
from build import paths, prns, folder
from sub_ionospheric_point import convert_coords
from rot_roti import roti
import sys       
import os
os.path.dirname(sys.executable)
from pathlib import Path       




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
    for prn in prns:
        dat_all_prns.append(compute_roti(year, doy, station, 
                     prn))
    
    df = pd.concat(dat_all_prns)
    
    df["station"] = station
    
    return df

year = 2014
doy = 1

station = "alar"

infile = "database/process/2014/001/"
_, _, files = next(os.walk(infile))


print(files)

