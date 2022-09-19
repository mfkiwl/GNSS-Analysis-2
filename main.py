from load import load_receiver, save_attrs
from relative_tec_calculator import relative_tec_data
from build import paths, prns, folder
import time
import os
from tqdm import tqdm
import pandas as pd


def run_for_all_prns(path, filename, save = True):
    
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

    if save:
        station = filename[:4]
        path_to_save = path.fn_process(station)
        all_prns.to_csv(path_to_save, sep = ";", index = True)
        
    return prns_list, data.attrs


def run_for_all_files(path):
    
    _, _, files = next(os.walk(path.rinex))
    
    out_prns = []
    out_dict = {}
    create_folder = folder(path.process)
        
    for filename in files[:1]:
        
        if filename.endswith(f".{path.ext_rinex}"):
            try:
                prns, attr_dat = run_for_all_prns(path, filename)
                out_dict.update(attr_dat)
                out_prns.append(pd.DataFrame({filename[:4]: prns}))
            except:
                print(f"Station {filename} not work")
                continue

    return out_dict, pd.concat(out_prns, axis = 1)


def run_for_all_days(year, root, start = 1, 
                     end = 365, save_prn = True):
    
    prn_in_year = []
    
    for doy in range(start, end + 1):
    
        path = paths(year, doy)
        
        json_dat, prn_dat = run_for_all_files(path)
        
        prn_dat["doy"] =  doy
    
        prn_in_year.append(prn_dat)
        
        save_attrs(path.fn_json, json_dat)
         
    if save_prn:
        prns_dat = pd.concat(prn_in_year)
        prn_dat.to_csv(f"prns_in_{year}", sep = " ")
        

start_time = time.time()
 
year = 2014
root = "C:\\Users\\Public\\"

run_for_all_days(year, root, start = 1, end = 365, save_prn = True)

        


print("--- %s hours ---" % ((time.time() - start_time) / 3600))


