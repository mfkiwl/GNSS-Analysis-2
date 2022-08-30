from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import get_cdb_value, create_prns
import pandas as pd
from utils import get_paths
import time



def process_data(year:int, 
                 station:str,
                 obs: list,
                 prn: str):
    
    """
    Concat the relative TEC for each piercing point 
    and compute other variables
    """

    path_tec, path_orbit, path_dcb = get_paths(year, station)
 
    sat_bias = get_cdb_value(path_dcb, prn)

    tecData = relative_tec_data(path_tec, prn = prn)
    
    tecData["cTEC"] = tecData["rTEC"] - sat_bias
      
    ippData = piercing_points_data(path_orbit, obs, prn = prn)
    
    
    df = tecData.join(ippData).interpolate()
    
    df["vTEC"] = df["proj"] * df["cTEC"]
    
    df['prn'] = prn
    #df.set_index('prn', append = True, inplace = True)
    
    
    return df



def run_for_all_prns(year, station, obs, doy, save = True):

    result = []
    
    for prn in create_prns():
        try: 
            result.append(process_data(year, station, obs, prn))
        except:
            continue
            print(f"The {prn} doesnt work!")
    
    df = pd.concat(result)
    
    if save:
        filename = f"{station}{doy}"
        df.to_csv(f"Database/all_process/{year}/{filename}.txt", 
                                  sep = " ", index = True)
    return df

def main():
    start_time = time.time()
    
    
    # Arapiraca
    #obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067
    
    # Belo Horizonte
    obs_x, obs_y, obs_z = 4320741.822, -4161560.476, -2161984.249
    
    obs = list((obs_x, obs_y, obs_z))
    
    year = 2015
    station = "mgbh"
    doy = 131
    
    run_for_all_prns(year, station, obs, doy, save = True)
    
    
    print("--- %s seconds ---" % (time.time() - start_time))