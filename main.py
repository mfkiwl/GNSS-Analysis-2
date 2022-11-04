from load import load_receiver, save_attrs
from relative_tec_calculator import relative_tec_data
from build import paths, prns, folder
import time
import os
from tqdm import tqdm
import pandas as pd


def run_for_all_prns(path:str, 
                     filename: str, 
                     save:bool = True):
    
    
    """Read RINEX file with, get compute relative TEC"""
    
    infile = os.path.join(path.rinex, filename)
    
    data = load_receiver(infile)
    
    out_prns = []
    
    try:
        prns_list = data.prns
    except:
        prns_list = prns().gps_and_glonass

    for prn in tqdm(prns_list, desc = filename):
        try:
            out_prns.append(relative_tec_data(data.df, prn = prn))
        except:
            continue

    all_prns = pd.concat(out_prns, axis = 1)
    
    
    station = filename[:4]
    
    prn_data = pd.DataFrame({station: prns_list})
    if save:
        
        path_to_save = path.fn_process(station)
        all_prns.to_csv(path_to_save, sep = ";", index = True)
        
    return prn_data, data.attrs


def run_for_all_files(path):
    
    """Enter with the root path and run for all files in directory"""
    
    _, _, files = next(os.walk(path.rinex))
    
    out_prns = []
    out_dict = {}
    create_folder = folder(path.process)
        
    for filename in files:
        
        if filename.endswith(f".{path.ext_rinex}"):
            try:
                prn_data, attr_dat = run_for_all_prns(path, filename)
                out_dict.update(attr_dat) #json file
                out_prns.append(prn_data) #prns data
            except:
                continue
    all_prns = pd.concat(out_prns, axis = 1)
    all_prns.to_csv(path.prns, sep = ",")
    save_attrs(path.fn_json, out_dict)
    return out_dict, all_prns


def run_for_all_days(year:str, 
                     root:str, 
                     start:int = 1, 
                     end:int = 365, 
                     save_prn:bool = True):
    
    prn_in_year = []
    
    for doy in range(start, end + 1):
        
        try:
            path = paths(year, doy, root = root)
            
            json_dat, all_prns = run_for_all_files(path)
            
        except:
            continue
         
        
        

start_time = time.time()
year = 2014
doy = 1
root = "D:\\"
path = paths(year, doy, root = root)


print("--- %s hours ---" % ((time.time() - start_time) / 3600))


