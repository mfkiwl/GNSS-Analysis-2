from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import get_cdb_value, create_prns
import pandas as pd
from utils import get_paths, doy_str_format
import time



def process_data(year:int, 
                 doy: int,
                 station:str,
                 obs: list,
                 prn: str):
    
    """
    Concat the relative TEC for each piercing point 
    and compute other variables
    """

    path_tec, path_orbit, path_dcb = get_paths(year, doy, station)
     
    sat_bias = get_cdb_value(path_dcb, prn)

    tecData = relative_tec_data(path_tec, prn = prn)
      
    ippData = piercing_points_data(path_orbit, obs, prn = prn)
    
    df = tecData.join(ippData).interpolate(method = 
                                           'nearest').ffill().bfill()
    
    df["vtec"] = df["proj"] * df["stec"]
    
    df['prn'] = prn
    
    df["bias"] = sat_bias
    
    
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
        filename = f"{station}{doy_str_format(doy)}"
        df.to_csv(f"Database/all_process/{year}/{filename}.txt", 
                                  sep = " ", index = True)
    return df

def main():
    start_time = time.time()
    
    
    # Arapiraca
    #obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067
    
    # Belo Horizonte
    #obs_x, obs_y, obs_z = 4320741.822, -4161560.476, -2161984.249
    
    # Fortaleza
    
    obs_x, obs_y, obs_z = 4983062.7560, -3959862.9020,  -410039.5900
    
    obs = list((obs_x, obs_y, obs_z))

    
    year = 2014
    station = "ceft"
    doy = 1
    prn = "G01"
    
   
    df = process_data(year, 
                     doy,
                     station,
                     obs,
                     prn)
    
    print(df)
    
    #run_for_all_prns(year, station, obs, doy, save = True)
    
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
main()